# Row- and Column-Level Access Control

> **Stage 2 → Python for Data Engineering → Module 2.20: Observability, Lineage, Governance, and Security**
>
> **Topic 08 — Row- and Column-Level Access Control**
>
> This module teaches fine-grained data access control from first principles through production architecture. The goal is not merely to learn SQL syntax, but to learn how to design, implement, test, audit, operate, and troubleshoot least-privilege access controls in enterprise Data Engineering platforms.

---

## 1. Learning Objectives

By completing this module, you should be able to:

- Explain data access control fundamentals.
- Distinguish authentication from authorization.
- Apply least privilege.
- Explain users, groups, roles, service identities, and machine identities.
- Design Role-Based Access Control (RBAC).
- Design Attribute-Based Access Control (ABAC).
- Combine RBAC and ABAC when appropriate.
- Understand grants, revokes, ownership, and inherited permissions.
- Control database, schema, and table access.
- Implement column-level security.
- Explain dynamic data masking.
- Implement and reason about row-level security (RLS).
- Implement PostgreSQL RLS safely.
- Distinguish `USING` from `WITH CHECK`.
- Design multi-tenant row isolation.
- Understand warehouse row-level security concepts.
- Understand lakehouse/catalog/storage/compute access boundaries.
- Use tag-based policies.
- Design PII-aware access controls.
- Separate human and service access.
- Design machine-to-machine authorization.
- Identify enforcement boundaries.
- Analyze export and bypass paths.
- Treat access policies as code.
- Write automated positive and negative security tests.
- Implement access-policy regression tests.
- Design audit logging.
- Run access reviews.
- Design approval workflows.
- Implement time-bound access.
- Design controlled break-glass access.
- Evaluate fine-grained access-control performance.
- Design a production access-control architecture.
- Investigate access-control incidents.

### Core mental model

```text
Principal
    ↓
Authentication
    ↓
Authorization
    ↓
Policy Evaluation
    ↓
Resource + Action
    ↓
Allow / Deny
    ↓
Audit
```

Fine-grained security adds another question:

```text
If access is allowed,
which rows and which columns are visible?
```

---

## 2. Why Data Access Control Matters

Enterprise Data Platforms contain information with very different sensitivity levels:

```text
Public
Internal
Confidential
PII
Financial
Restricted
Highly Sensitive
```

A single table can contain both low-risk and highly sensitive fields:

```text
customer_id
name
email
phone
salary
government_id
```

Giving everyone table-level access is therefore often too broad.

### The problem

Suppose an analyst needs:

```sql
SELECT customer_id, order_date, order_value
FROM analytics.orders;
```

but does not need:

```text
email
phone
salary
government_id
```

A production access-control design should make the least-privilege requirement enforceable rather than relying on analyst behavior.

### Security objectives

Access control should help answer:

- Who can access the data?
- What can they do?
- Which datasets can they access?
- Which rows can they see?
- Which columns can they see?
- Under what conditions?
- For how long?
- Who approved access?
- Who actually used the access?
- Can the policy be bypassed?

---

## 3. Authentication vs Authorization

These concepts must never be confused.

### Authentication

Authentication answers:

> **Who are you?**

Examples:

- username/password;
- SSO;
- certificates;
- workload identity;
- tokens;
- cloud IAM identity.

### Authorization

Authorization answers:

> **What are you allowed to do?**

Example:

```text
Alice
  ↓
Authenticated
  ↓
Analyst role
  ↓
SELECT on analytics.sales
  ↓
Only approved columns
  ↓
Only approved region rows
```

### Authentication does not imply authorization

A successfully authenticated user might still receive:

```text
403 Forbidden
```

or a database permission error.

That is expected.

### Data Engineering examples

| Principal | Authentication | Authorization |
|---|---|---|
| Data Engineer | SSO | Development + approved production access |
| Analyst | SSO | Approved analytical datasets |
| Data Scientist | SSO/workload identity | Approved feature/training data |
| Airflow | Workload identity | Specific pipeline permissions |
| Spark | Service identity | Specific read/write permissions |
| Kafka consumer | Client identity | Approved topic permissions |
| BI tool | Service/user identity | Approved datasets and columns |

---

## 4. Access Control Fundamentals

Start with six objects:

```text
Principal
Identity
Resource
Action
Permission
Policy
```

### Principal

The actor requesting access.

Examples:

```text
human user
service
application
pipeline
machine identity
```

### Identity

The representation used to authenticate the principal.

### Resource

The thing being protected:

```text
database
schema
table
column
row
object
topic
dataset
API
```

### Action

What the principal wants to do:

```text
SELECT
INSERT
UPDATE
DELETE
READ
WRITE
EXECUTE
EXPORT
```

### Permission

An allowed action on a resource.

### Policy

A rule that determines whether a request should be allowed.

### Authorization decision

```text
Principal + Action + Resource + Context
              ↓
           Policy
              ↓
        Allow / Deny
```

### Fine-grained decision

For row/column security:

```text
Principal
+
Resource
+
Action
+
Role/Attributes
+
Data Classification
+
Row Context
+
Column Classification
        ↓
Access Decision
```

---

## 5. Least Privilege

Least privilege means:

> Give an identity only the minimum access required to perform its legitimate job.

### Example

```text
Analyst
  → SELECT approved analytical columns

ETL Service
  → read source
  → write target

Data Scientist
  → approved analytical datasets

Security Administrator
  → administer security metadata
  → not unrestricted business data
```

### Excessive permissions

This is dangerous:

```text
analyst
  → SELECT *
  → INSERT
  → UPDATE
  → DELETE
  → CREATE ROLE
```

The analyst probably needs something closer to:

```text
analyst
  → SELECT approved view
```

### Privilege creep

Access often grows over time:

```text
Day 1
Analyst → sales

Month 6
Analyst → sales + finance + customer_pii

Year 2
Analyst → sales + finance + customer_pii + admin
```

This is privilege creep.

### Shared accounts

Avoid:

```text
shared_analyst_account
shared_etl_account
shared_admin_account
```

Shared identities make:

- accountability;
- access review;
- incident investigation;
- revocation

more difficult.

### Practical PostgreSQL example

```sql
CREATE ROLE analyst_role;

GRANT USAGE ON SCHEMA analytics TO analyst_role;

GRANT SELECT
ON TABLE analytics.sales_summary
TO analyst_role;
```

Do not grant broad schema/table access when a narrower view is sufficient.

---

## 6. Roles, Users, Groups, and Service Identities

Production systems usually separate identity from permission.

A simplified hierarchy:

```text
User
  ↓
Group
  ↓
Role
  ↓
Permissions
  ↓
Dataset
```

### Human user

Example:

```text
alice@example.com
```

### Group

Example:

```text
finance-analysts
```

### Role

Example:

```text
finance_readonly
```

### Service identity

Example:

```text
airflow-prod
```

### Machine identity

A workload identity representing a service rather than a human.

### Why roles matter

Instead of:

```text
Alice → SELECT sales
Bob → SELECT sales
Carol → SELECT sales
Dave → SELECT sales
```

use:

```text
analyst_role → SELECT sales
```

and assign users to the role through the organization's identity system.

### Service identity architecture

```text
Airflow
   ↓
Service Identity
   ↓
Database Role
   ↓
Permissions
```

A production pipeline should not depend on a developer's personal database credentials.

---

## 7. RBAC

Role-Based Access Control assigns permissions to roles and identities to roles.

```text
Role
  ↓
Permissions
  ↓
Resources
```

Example:

```text
analyst_role
    ↓
SELECT
    ↓
analytics.gold_sales
```

### PostgreSQL example

```sql
CREATE ROLE analyst_role;

GRANT USAGE
ON SCHEMA analytics
TO analyst_role;

GRANT SELECT
ON TABLE analytics.gold_sales
TO analyst_role;
```

Assign a user:

```sql
GRANT analyst_role TO alice;
```

### Role review

A production review asks:

```text
Which users have this role?
Which permissions does this role have?
Which resources do those permissions affect?
Is the role still necessary?
Does the role violate separation of duties?
```

### Role hierarchy awareness

Some systems support roles inheriting other roles:

```text
analyst
  ↓
senior_analyst
  ↓
analytics_manager
```

This can simplify administration but can also hide transitive permissions.

Always inspect effective permissions, not only direct grants.

### Separation of duties

Avoid roles such as:

```text
data_reader + key_admin + security_admin + production_deployer
```

unless there is a documented reason.

---

## 8. ABAC

Attribute-Based Access Control makes decisions using attributes.

Conceptually:

```text
Subject Attributes
+
Resource Attributes
+
Environment Attributes
+
Action
        ↓
Policy Decision
```

### Subject attributes

```text
department = finance
employment_status = active
clearance = restricted
region = eu
```

### Resource attributes

```text
classification = confidential
contains_pii = true
domain = finance
```

### Environment attributes

```text
network = corporate
device_trusted = true
time = business_hours
purpose = analytics
```

### Example policy

```text
ALLOW
IF
  subject.department == "finance"
  AND resource.classification == "confidential"
  AND subject.employment_status == "active"
  AND action == "read"
```

ABAC can express contextual policies that become cumbersome with pure role assignments.

---

## 9. RBAC vs ABAC

| Dimension | RBAC | ABAC |
|---|---|---|
| Decision based on | Roles | Attributes |
| Simplicity | Higher | Lower |
| Context awareness | Limited | High |
| Policy complexity | Lower | Higher |
| Governance | Easier | More complex |
| Fine-grained control | Moderate | Strong |
| Typical strength | Stable job functions | Context-sensitive rules |

### RBAC is useful when

Permissions naturally map to job functions:

```text
analyst
finance_reader
etl_writer
security_auditor
```

### ABAC is useful when

Access depends on context:

```text
department
classification
region
tenant
purpose
device
time
```

### Combining them

Production systems often use:

```text
RBAC
+
ABAC
+
Resource classification
+
Data policy
```

Example:

```text
User has analyst_role
AND
dataset classification is approved
AND
region is allowed
AND
purpose is analytics
```

---

## 10. Grants and Permissions

Common database permissions include:

- `SELECT`;
- `INSERT`;
- `UPDATE`;
- `DELETE`;
- `USAGE`;
- `EXECUTE` awareness;
- ownership;
- role membership.

### Grant

```sql
GRANT SELECT
ON TABLE analytics.sales
TO analyst_role;
```

### Revoke

```sql
REVOKE SELECT
ON TABLE analytics.sales
FROM analyst_role;
```

### Principle

Prefer explicit permissions.

Avoid relying on accidental inherited access.

### Ownership matters

A database object owner can often perform administrative actions beyond ordinary grants.

Therefore:

```text
Application runtime role
≠
Object owner
```

is often a healthier production design.

### Effective permission analysis

When investigating access, inspect:

```text
Direct grants
+
Role membership
+
Inherited roles
+
Object ownership
+
Default privileges
+
Policy filters
```

The permission visible in one SQL statement may not represent the full effective authorization state.

---

## 11. Database, Schema, and Table-Level Access

Access granularity commonly looks like:

```text
Database
   ↓
Schema
   ↓
Table
   ↓
Column
   ↓
Row
   ↓
Cell / value
```

Each layer answers a different question.

### Database-level

Can the identity connect to the database?

### Schema-level

Can the identity use objects in a schema?

```sql
GRANT USAGE
ON SCHEMA analytics
TO analyst_role;
```

### Table-level

Can the identity read/write a table?

```sql
GRANT SELECT
ON TABLE analytics.sales
TO analyst_role;
```

### Column-level

Can the identity read specific columns?

### Row-level

Which rows can the identity see or modify?

### Why table-level access is insufficient

Consider:

```text
customer_id
name
email
phone
salary
government_id
```

If an analyst only needs:

```text
customer_id
name
```

table-level `SELECT` is too broad.

---

## 12. Column-Level Security

Column-level security restricts access to individual fields.

Example:

```text
customer_id     allowed
name            allowed
email           restricted
phone           restricted
salary          restricted
government_id   restricted
```

### Common strategies

1. Column grants.
2. Secure views.
3. Dynamic masking.
4. Warehouse-native column policies.
5. Policy engines.
6. Classification/tag-driven controls.

### Secure view example

```sql
CREATE VIEW analytics.customer_safe AS
SELECT
    customer_id,
    name,
    order_value
FROM analytics.customers;
```

Grant access to the view:

```sql
GRANT SELECT
ON analytics.customer_safe
TO analyst_role;
```

Do not grant the same role direct access to the underlying sensitive table unless required.

### Important enforcement question

Where is the sensitive base table accessible?

If an analyst can bypass the view and query the base table, the view does not enforce security.

---

## 13. Dynamic Data Masking

Dynamic masking allows access while transforming sensitive values according to identity or policy.

Example:

```text
Privileged user:
john.doe@example.com

Analyst:
j***@example.com
```

### Access denied vs masked access

These are different:

```text
Access denied
→ no value is returned
```

versus:

```text
Access allowed + masking
→ transformed value is returned
```

### When masking is useful

An analyst may need to know:

```text
a customer exists
```

without needing:

```text
customer's complete email address
```

### Policy-driven masking

Conceptually:

```text
User
  ↓
Role / attributes
  ↓
Masking policy
  ↓
Original value OR masked value
```

### Risks

Masking can still leak information through:

- repeated values;
- lengths;
- patterns;
- exports;
- joins;
- frequency analysis;
- application bugs.

Masking should therefore be treated as one security control, not universal protection.

---

## 14. Row-Level Security

Row-Level Security (RLS) controls which rows an identity may access.

Example table:

```text
customer | region | revenue
---------|--------|--------
A        | US     | 100
B        | EU     | 200
C        | US     | 300
```

A US analyst sees:

```text
A
C
```

An EU analyst sees:

```text
B
```

### Common use cases

- tenant isolation;
- region restrictions;
- department-based access;
- user-specific ownership;
- data-domain restrictions.

### Conceptual policy

```text
Principal
   +
Context
   +
Row attributes
   ↓
RLS policy
   ↓
Visible rows
```

### Application filtering vs database RLS

Application-only filtering:

```python
rows = query_all_rows()
rows = [r for r in rows if r["tenant_id"] == tenant]
```

is dangerous because the application first obtained all rows.

A database-enforced RLS policy can enforce the boundary closer to the data.

---

## 15. PostgreSQL Row-Level Security

PostgreSQL provides native RLS.

### Enable RLS

```sql
ALTER TABLE sales
ENABLE ROW LEVEL SECURITY;
```

### Example policy

```sql
CREATE POLICY sales_region_policy
ON sales
FOR SELECT
USING (
    region = current_setting('app.region')
);
```

The exact session-context mechanism must be designed carefully. Do not allow an untrusted caller to arbitrarily set a security-sensitive context.

### What `USING` means

`USING` controls which existing rows are visible to an operation.

For a `SELECT`:

```text
SELECT
  ↓
USING
  ↓
Rows visible to the principal
```

### `WITH CHECK`

`WITH CHECK` controls which rows may be inserted or updated.

Conceptually:

```text
INSERT / UPDATE
       ↓
  WITH CHECK
       ↓
Does the new row satisfy policy?
```

---

## 16. `USING` vs `WITH CHECK`

This distinction is critical.

### `USING`

Controls which existing rows can be accessed.

```sql
USING (tenant_id = current_setting('app.tenant_id'))
```

### `WITH CHECK`

Controls whether a new or modified row satisfies the policy.

```sql
WITH CHECK (
    tenant_id = current_setting('app.tenant_id')
)
```

### Security gap without `WITH CHECK`

Imagine Tenant A can only **read** Tenant A rows.

If inserts are not restricted, a compromised or buggy client might attempt:

```sql
INSERT INTO orders (
    tenant_id,
    order_value
)
VALUES (
    'tenant-B',
    5000
);
```

A read-only RLS condition is not enough to guarantee write isolation.

A robust policy considers both:

```text
Visibility
+
Mutation constraints
```

### Example

```sql
CREATE POLICY tenant_isolation
ON orders
USING (
    tenant_id = current_setting('app.tenant_id')
)
WITH CHECK (
    tenant_id = current_setting('app.tenant_id')
);
```

### Production warning

RLS interacts with:

- table owners;
- roles with bypass privileges;
- superusers;
- security-definer functions;
- connection/session context;
- application connection pooling.

Always test the **effective** security boundary.

---

## 17. Multi-Tenant Data Isolation

Consider a SaaS platform:

```text
tenant_id
customer_id
email
order_value
```

Rows:

```text
tenant-A | c1 | a@example.com | 100
tenant-A | c2 | b@example.com | 200
tenant-B | c9 | z@example.com | 900
```

The goal:

```text
Tenant A → only tenant-A
Tenant B → only tenant-B
```

### Secure architecture

```text
Application Identity
        ↓
Tenant Context
        ↓
Database Role
        ↓
RLS Policy
        ↓
Tenant Rows
```

### Defense in depth

Tenant isolation should not rely on only one layer.

Use appropriate combinations of:

- application context;
- service identity;
- database RLS;
- storage permissions;
- API authorization;
- tests;
- audit logging.

### Why application-only filtering is dangerous

A bug like:

```python
tenant_id = request.args.get("tenant_id")
```

can allow a caller to request another tenant's data if the application does not validate the value.

Database-level policy can provide a second enforcement layer.

---

## 18. Warehouse Row-Level Security

Cloud warehouses commonly support concepts such as:

- policy-based row filtering;
- current user/context;
- role-based policies;
- secure views;
- masking policies;
- tenant filtering;
- region filtering.

### Generic pattern

```sql
CREATE POLICY region_policy
ON analytics.sales
FOR SELECT
USING (region = current_user_region());
```

The exact syntax is platform-specific.

### Secure views

A warehouse can expose:

```text
secure_sales_view
```

instead of:

```text
raw_sales_table
```

### Masking + RLS

A mature warehouse policy can combine:

```text
Row filtering
+
Column masking
+
Role authorization
```

For example:

```text
Analyst
→ only EU rows
→ salary masked

Finance
→ approved regions
→ salary visible
```

Do not assume all warehouses implement these features identically. Verify the specific platform's documented security model.

---

## 19. Lakehouse Access Control

Lakehouse security has multiple layers because data often lives in object storage while users query through catalogs and compute engines.

Conceptually:

```text
Object Storage
      ↑
Storage permissions
      ↑
Catalog
      ↑
Table / Column / Row policies
      ↑
Compute
      ↑
User / Service Identity
```

### Layers to consider

- object storage;
- tables;
- catalogs;
- table permissions;
- column policies;
- row filters;
- storage-layer access;
- catalog-layer access;
- compute-layer access.

### Critical bypass risk

Suppose:

```text
BI Tool
  ↓
Warehouse / Lakehouse SQL
  ↓
RLS policy
```

is secure.

But the same user can also:

```text
User
  ↓
Direct object-storage credentials
  ↓
raw/customer.parquet
```

The catalog policy is bypassed.

### Principle

> The strongest access policy is irrelevant if a user can reach the same sensitive data through an uncontrolled path.

---

## 20. Tag-Based Access Policies

Metadata can drive access policies.

Useful tags include:

```text
PII
SENSITIVE
FINANCIAL
HEALTH
CONFIDENTIAL
RESTRICTED
```

Conceptually:

```text
Dataset
   ↓
Metadata Tag
   ↓
Policy
   ↓
Access Decision
```

### Example

```text
PII = true
+
user_role = analyst
        ↓
mask email
```

Another:

```text
classification = restricted
+
clearance < restricted
        ↓
deny
```

### Why tags matter

Without classification-driven controls, every table may require custom policy configuration.

Tags allow a reusable policy:

```text
IF PII = true
AND principal.role = analyst
THEN mask sensitive columns
```

### Governance requirement

Tags themselves must be trustworthy.

If an attacker can remove:

```text
PII=true
```

and thereby obtain access, the classification system becomes a security boundary and needs its own authorization and audit controls.

---

## 21. PII-Aware Access Control

Common sensitive fields include:

```text
email
phone
government_id
salary
bank_account
```

Policies can:

- deny access;
- mask values;
- expose only approved columns;
- restrict rows;
- allow privileged access;
- log access.

### Classification-driven enforcement

The principle is:

> **Classification should drive enforcement.**

Example:

```text
Dataset classified:
PII + FINANCIAL

Analyst
  → approved non-sensitive columns
  → masked PII
  → restricted rows

Finance
  → approved financial columns
  → approved business rows

Security
  → controlled investigation access
```

### Link to data governance

Access policy should use the same authoritative classification metadata that supports:

- cataloging;
- lineage;
- PII discovery;
- retention;
- governance.

This reduces policy drift.

---

## 22. Human vs Service Access

### Human identities

Examples:

- Analyst;
- Data Engineer;
- Data Scientist;
- Administrator.

Human access typically requires:

```text
SSO
+
MFA
+
role assignment
+
approval
+
periodic review
```

### Service identities

Examples:

- Airflow;
- Spark;
- dbt;
- ingestion service;
- API;
- monitoring service.

Service identities need:

```text
workload identity
+
short-lived credentials where possible
+
least privilege
+
auditing
```

### Example

```text
Analyst
  → SELECT approved analytical view

ETL Service
  → SELECT source
  → INSERT target

Security Service
  → READ security metadata
  → AUDIT
```

Do not give all three the same role.

---

## 23. Service-to-Service Authorization

Machine-to-machine access should be explicit.

Example:

```text
Airflow
   ↓
Service Identity
   ↓
PostgreSQL role
   ↓
SELECT source
INSERT target
```

### Better than shared passwords

Avoid:

```text
all-pipelines
  ↓
shared_database_password
```

Problems include:

- difficult rotation;
- unclear ownership;
- excessive permissions;
- poor auditability;
- difficult revocation.

### Better model

```text
Pipeline A → identity-A
Pipeline B → identity-B
Pipeline C → identity-C
```

Each identity receives only required permissions.

### Short-lived credentials

Where supported, prefer short-lived workload credentials over long-lived static secrets.

---

## 24. Enforcement Boundaries

Always ask:

> **Where is the access-control policy actually enforced?**

### Example A

```text
BI Tool
   ↓
Warehouse
```

If the warehouse enforces RLS, this may be a strong boundary.

### Example B

```text
BI Tool
   ↓
Warehouse
   ↓
Direct Object Storage
```

If the same user can obtain storage credentials, the warehouse policy may not protect raw files.

### Enforcement layers

Consider:

- storage permissions;
- catalog permissions;
- compute permissions;
- database policies;
- network controls;
- API controls;
- export controls.

### Boundary mapping

For each sensitive dataset document:

```text
Who can access?
Where is policy enforced?
What credentials reach the data?
What alternate path exists?
```

---

## 25. Export and Bypass Risks

Data can leave a policy boundary through:

- CSV exports;
- notebook downloads;
- temporary tables;
- cached results;
- BI extracts;
- object storage;
- backups;
- ETL jobs;
- APIs;
- screenshots awareness.

### Example bypass

Suppose:

```text
Warehouse RLS
  ↓
Analyst sees only Tenant A
```

The analyst exports the result to:

```text
personal object storage
```

The original warehouse policy no longer governs the copied dataset.

### Another bypass

```text
Warehouse
  ↓
secure view
```

but the analyst also has:

```text
object-storage/read
```

and can read raw files.

### Production response

Access-control design must include:

```text
Primary access path
+
Alternate access paths
+
Export paths
+
Copy paths
+
Backup paths
```

### Principle

> Access control is effective only when all meaningful data paths are governed.

---

## 26. Policy-as-Code

Access-control policies should be:

- versioned;
- reviewed;
- tested;
- deployed;
- audited.

Conceptually:

```text
Git
 ↓
Policy Definition
 ↓
Pull Request
 ↓
Automated Tests
 ↓
Security Review
 ↓
Deployment
 ↓
Audit
```

### Example YAML

```yaml
dataset: customer_orders
classification: confidential

roles:
  analyst:
    columns:
      - customer_id
      - order_date
      - order_value

  finance:
    columns:
      - customer_id
      - order_date
      - order_value
      - payment_status
```

### Validation

```python
def validate_policy(policy):
    assert policy["dataset"]
    assert policy["classification"]
    assert policy["roles"]

    analyst_columns = set(policy["roles"]["analyst"]["columns"])

    assert "salary" not in analyst_columns
    assert "government_id" not in analyst_columns
```

The important architectural principle is:

```text
Policy definition
→ source controlled
→ tested
→ reviewed
→ deployed
```

---

## 27. Automated Access-Control Tests

Security tests must prove both:

```text
What should work
```

and:

```text
What must not work
```

### Positive tests

```text
Analyst can query approved columns.
Finance can query approved financial columns.
ETL can write its target.
Tenant A can query Tenant A.
```

### Negative tests

```text
Analyst cannot query salary.
Analyst cannot grant itself access.
Tenant A cannot see Tenant B.
ETL cannot administer users.
Unapproved role cannot access restricted dataset.
```

### Python example

```python
def test_analyst_columns(policy):
    columns = set(policy["roles"]["analyst"]["columns"])

    assert "customer_id" in columns
    assert "order_value" in columns
    assert "salary" not in columns
    assert "government_id" not in columns
```

### Why negative tests matter

A policy can appear correct while accidentally allowing a dangerous action.

Security testing must therefore assert denial explicitly.

---

## 28. Policy Regression Testing

Access-control regressions often result from ordinary engineering changes.

Example:

```text
Developer changes view
        ↓
Sensitive column added
        ↓
Existing policy unintentionally exposes it
```

Or:

```text
Role changed
   ↓
Inherited permission expands
   ↓
Sensitive dataset becomes visible
```

### Regression coverage

Test:

- schema changes;
- role changes;
- policy changes;
- view changes;
- catalog-tag changes;
- new columns;
- new datasets;
- new service identities.

### Example

```python
SENSITIVE = {"salary", "government_id", "bank_account"}

def test_new_columns_are_not_implicitly_exposed(schema_columns):
    newly_exposed = set(schema_columns) & SENSITIVE
    assert not newly_exposed
```

In production, connect the test to the actual policy model and deployment workflow.

---

## 29. Audit Logging

Record security-relevant access events.

Useful fields:

```text
timestamp
principal
service
dataset
table
column
action
result
source
request/context
```

Also record:

- successful access;
- denied access;
- privileged access;
- policy changes;
- role changes;
- grants;
- revokes;
- break-glass access.

### Example event

```json
{
  "timestamp": "2026-10-06T10:30:00Z",
  "principal": "alice@example.com",
  "service": "bi",
  "dataset": "customer_orders",
  "table": "orders",
  "action": "SELECT",
  "result": "DENIED",
  "reason": "restricted_column",
  "source": "dashboard-42"
}
```

### Protecting audit logs

Audit logs themselves need security controls.

Avoid allowing an ordinary analyst to:

```text
read unrestricted audit logs
+
modify audit logs
+
delete audit logs
```

A stronger model is:

```text
Application
  ↓
Audit event
  ↓
Append-oriented log
  ↓
Restricted security access
  ↓
Retention / monitoring
```

---

## 30. Access Reviews

Periodic access reviews answer:

```text
Who has access?
Why do they have it?
Do they still need it?
Is the permission excessive?
Who approved it?
When was it last reviewed?
```

### Review high-risk populations

Prioritize:

- privileged roles;
- PII access;
- financial data access;
- dormant accounts;
- orphaned access;
- service identities;
- emergency access.

### Practical workflow

```text
Generate effective-access report
        ↓
Group by owner
        ↓
Identify high-risk permissions
        ↓
Owner reviews
        ↓
Approve / revoke
        ↓
Record evidence
```

### Service identity reviews

Do not forget machine identities.

A service can remain active for years after the pipeline that created it has disappeared.

---

## 31. Approval Workflows

Access should have a clear ownership model.

Example:

```text
User requests access
        ↓
Manager / Data Owner approves
        ↓
Security / Platform validation
        ↓
Automated policy validation
        ↓
Access granted
        ↓
Access expires / reviewed
```

### Roles

#### Data owner

Determines whether business access is appropriate.

#### Manager

Confirms the user's business need.

#### Security / Platform

Ensures policy and technical controls are satisfied.

#### Automated policy validation

Checks that the requested access does not violate predefined controls.

### Audit trail

Record:

```text
requester
approver
resource
reason
scope
start time
expiration
decision
```

---

## 32. Time-Bound Access

Permanent access is often unnecessary.

Suppose:

```text
Developer needs production access
for 2 hours
```

Use:

```text
Request
  ↓
Approval
  ↓
Grant
  ↓
Expiration
  ↓
Automatic revoke
```

### Benefits

- reduces privilege creep;
- limits incident blast radius;
- makes emergency access safer;
- creates explicit audit evidence.

### Conceptual policy

```yaml
principal: engineer-42
resource: production.customer_orders
permission: read
reason: incident-investigation
expires_at: "2026-10-06T14:00:00Z"
approved_by: data-owner
```

The access-control platform should enforce expiration rather than trusting the engineer to remove access manually.

---

## 33. Break-Glass Access

Break-glass access is emergency access used when normal access workflows cannot satisfy an urgent operational need.

Example:

> A production incident requires immediate access to restricted data to determine whether customer records are corrupted.

### Required controls

- explicit approval where feasible;
- emergency justification;
- narrow scope;
- time limit;
- enhanced audit;
- automatic expiration;
- post-event review.

### Example

```text
Incident declared
      ↓
Break-glass request
      ↓
Security / incident approval
      ↓
Temporary restricted role
      ↓
Investigation
      ↓
Automatic expiration
      ↓
Post-incident review
```

### Break-glass is not normal access

If engineers routinely use break-glass permissions, the standard access model is probably inadequate.

---

## 34. Access Control for Data Products

A data product should have an explicit ownership and access model.

```text
Data Product
   ↓
Owner
   ↓
Classification
   ↓
Access Policy
   ↓
Consumers
```

### Example

```text
Customer Revenue Data Product

Owner:
  Finance Data Platform

Classification:
  Confidential

Consumers:
  Finance Analysts
  Approved ML Service

Controls:
  RLS by region
  Salary excluded
  PII masked
  All privileged access audited
```

### Why ownership matters

Without a data owner, access decisions become ambiguous:

```text
Who approves?
Who revokes?
Who reviews?
Who responds to an incident?
```

---

## 35. Performance Considerations

Fine-grained access control can affect query performance.

Potential factors include:

- row-policy evaluation;
- predicate pushdown;
- partition pruning;
- indexing;
- policy complexity;
- joins;
- dynamic masking;
- query planning;
- large policy tables;
- high-cardinality tenant filters;
- caching;
- materialized views.

### Basic trade-off

```text
More granular control
        ↓
More policy evaluation
        ↓
Potential performance cost
```

### Example: tenant filtering

Suppose:

```text
orders
partitioned by date
```

and RLS adds:

```sql
tenant_id = current_tenant()
```

If the physical layout and query engine can efficiently prune partitions or use appropriate indexes, the overhead may be manageable.

If the policy forces expensive joins against a huge policy table for every query, performance can degrade.

### Measure rather than assume

Benchmark:

```text
Query without policy
        vs
Query with policy
```

Measure:

- latency;
- scanned bytes;
- CPU;
- memory;
- query plan;
- concurrency;
- cache behavior.

### Performance design strategies

Depending on platform:

- keep policies simple;
- index policy lookup columns;
- align physical partitioning with common policy predicates;
- use efficient tenant keys;
- avoid unnecessary joins in security predicates;
- use materialized views where appropriate;
- test policy behavior at production scale;
- monitor query regressions.

Security should not be removed merely because a policy is expensive. Optimize the implementation and revisit the data model.

---

## 36. Production Access-Control Architecture

A realistic enterprise architecture:

```text
                  Identity Provider
                         |
                         v
                  User / Service
                         |
                         v
                Authorization Layer
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
        RBAC            ABAC        Tag Policies
          |              |              |
          +--------------+--------------+
                         |
                         v
                    Data Platform
              +----------+----------+
              |          |          |
              v          v          v
         PostgreSQL   Warehouse   Lakehouse
              |          |          |
             RLS    Masking/RLS  Catalog/RLS
              |          |          |
              +----------+----------+
                         |
                         v
                    Audit Logging
                         |
                         v
                    Access Reviews
```

### Supporting controls

```text
Identity Provider
    ↓
Authentication

RBAC / ABAC
    ↓
Authorization

Classification / Tags
    ↓
Fine-grained policy

Database / Warehouse / Lakehouse
    ↓
Enforcement

Audit Logging
    ↓
Evidence

Access Reviews
    ↓
Governance
```

### Production principle

No single control should be treated as the entire security architecture.

---

## 37. End-to-End Python + SQL Example

Consider a customer dataset:

```text
customer_id
tenant_id
customer_email
region
order_value
salary
```

### Step 1 — classify

```python
classification = {
    "customer_id": "internal",
    "tenant_id": "internal",
    "customer_email": "PII",
    "region": "internal",
    "order_value": "confidential",
    "salary": "restricted",
}
```

### Step 2 — define role policy

```yaml
analyst:
  columns:
    - customer_id
    - tenant_id
    - region
    - order_value

finance:
  columns:
    - customer_id
    - tenant_id
    - region
    - order_value
    - salary
```

### Step 3 — database grants

```sql
CREATE ROLE analyst_role;
CREATE ROLE finance_role;

GRANT USAGE
ON SCHEMA analytics
TO analyst_role;

GRANT SELECT
ON analytics.customer_orders
TO finance_role;
```

For analysts, expose a secure view rather than granting direct access to restricted base columns.

### Step 4 — tenant policy

```sql
ALTER TABLE analytics.customer_orders
ENABLE ROW LEVEL SECURITY;

CREATE POLICY customer_tenant_policy
ON analytics.customer_orders
FOR SELECT
USING (
    tenant_id = current_setting('app.tenant_id')
);
```

### Step 5 — test policy

```python
def assert_analyst_cannot_see_salary(columns):
    assert "salary" not in columns
```

### Step 6 — audit

```python
audit_event = {
    "principal": "analyst-42",
    "dataset": "customer_orders",
    "action": "SELECT",
    "result": "ALLOW",
}
```

The complete system becomes:

```text
Classification
      ↓
Role
      ↓
Column Policy
      ↓
Row Policy
      ↓
Masked / Allowed Output
      ↓
Audit Event
```

---

## 38. PostgreSQL Hands-On Lab

### Dataset

```sql
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE analytics.sales (
    tenant_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    customer_email TEXT,
    region TEXT NOT NULL,
    revenue NUMERIC(18, 2) NOT NULL
);
```

Insert test data:

```sql
INSERT INTO analytics.sales
    (tenant_id, customer_id, customer_email, region, revenue)
VALUES
    ('tenant-a', 'c001', 'alice@example.com', 'US', 100.00),
    ('tenant-a', 'c002', 'bob@example.com', 'US', 200.00),
    ('tenant-b', 'c003', 'carol@example.com', 'EU', 300.00);
```

### Create roles

```sql
CREATE ROLE analyst_role;
CREATE ROLE finance_role;
CREATE ROLE etl_role;
```

### Schema access

```sql
GRANT USAGE
ON SCHEMA analytics
TO analyst_role, finance_role, etl_role;
```

### Enable RLS

```sql
ALTER TABLE analytics.sales
ENABLE ROW LEVEL SECURITY;
```

### Tenant policy

```sql
CREATE POLICY tenant_sales_select
ON analytics.sales
FOR SELECT
USING (
    tenant_id = current_setting('app.tenant_id', true)
);
```

The `true` argument allows a missing setting to produce `NULL` rather than immediately raising an error. Production systems should explicitly handle missing context rather than allowing ambiguous behavior.

### Write policy

```sql
CREATE POLICY tenant_sales_write
ON analytics.sales
FOR INSERT
WITH CHECK (
    tenant_id = current_setting('app.tenant_id', true)
);
```

For updates, use both visibility and write constraints where required:

```sql
CREATE POLICY tenant_sales_update
ON analytics.sales
FOR UPDATE
USING (
    tenant_id = current_setting('app.tenant_id', true)
)
WITH CHECK (
    tenant_id = current_setting('app.tenant_id', true)
);
```

### Test context

```sql
SET app.tenant_id = 'tenant-a';

SELECT *
FROM analytics.sales;
```

Expected:

```text
tenant-a rows only
```

Then:

```sql
SET app.tenant_id = 'tenant-b';

SELECT *
FROM analytics.sales;
```

Expected:

```text
tenant-b rows only
```

### Important PostgreSQL security considerations

Test behavior for:

- table owner;
- superuser;
- `BYPASSRLS`;
- inherited roles;
- security-definer functions;
- connection pooling;
- missing tenant context.

RLS is powerful, but its security boundary depends on PostgreSQL role semantics and the surrounding application architecture.

---

## 39. Access-Control Testing Lab

Build a test matrix.

| Test | Expected |
|---|---|
| Analyst reads approved column | Allow |
| Analyst reads salary | Deny |
| Finance reads approved financial field | Allow |
| Tenant A reads Tenant A | Allow |
| Tenant A reads Tenant B | Deny |
| ETL writes approved target | Allow |
| ETL grants itself admin | Deny |
| New sensitive column appears | Deny until approved |
| Temporary access expires | Deny |
| Break-glass after expiration | Deny |

### Positive test

```python
def test_analyst_can_read_order_value(policy):
    assert "order_value" in policy["roles"]["analyst"]["columns"]
```

### Negative test

```python
def test_analyst_cannot_read_salary(policy):
    assert "salary" not in policy["roles"]["analyst"]["columns"]
```

### Tenant isolation test

```python
def test_tenant_isolation(visible_rows):
    assert all(row["tenant_id"] == "tenant-a" for row in visible_rows)
```

### Privilege escalation test

```python
def test_analyst_cannot_become_admin(effective_roles):
    assert "security_admin" not in effective_roles["analyst"]
```

### Policy regression test

```python
def test_restricted_columns_are_not_implicitly_exposed(schema):
    restricted = {"salary", "government_id", "bank_account"}

    exposed = set(schema["analyst_columns"]) & restricted

    assert exposed == set()
```

Security tests should execute in CI before production policy deployment.

---

## 40. Failure Injection and Debugging

### Failure 1 — Over-Permissioned Analyst

An analyst accidentally receives access to a sensitive table.

Workflow:

```text
Detection
  ↓
Investigation
  ↓
Revoke
  ↓
Audit
  ↓
Root Cause
  ↓
Prevention
```

Investigate:

- role membership;
- direct grants;
- inherited permissions;
- object ownership;
- recent policy changes.

### Failure 2 — RLS Misconfiguration

Tenant A can see Tenant B rows.

Workflow:

```text
Detect cross-tenant query
        ↓
Stop affected access path
        ↓
Inspect RLS policy
        ↓
Inspect tenant context
        ↓
Verify role behavior
        ↓
Correct policy
        ↓
Run regression tests
        ↓
Review audit logs
```

### Failure 3 — Missing `WITH CHECK`

A user cannot read another tenant's data but can insert a row belonging to another tenant.

This is a serious write-isolation flaw.

Fix:

```sql
WITH CHECK (
    tenant_id = current_setting('app.tenant_id')
)
```

and test insert/update paths explicitly.

### Failure 4 — Direct Object Storage Access

Warehouse policies are correct, but a user has direct storage permissions.

The warehouse is not the true enforcement boundary.

Containment:

```text
Revoke storage permission
        ↓
Inspect affected identities
        ↓
Review object access logs
        ↓
Define storage policy
        ↓
Add bypass test
```

### Failure 5 — Export Bypass

A user exports sensitive data to an uncontrolled location.

Investigate:

- export source;
- destination;
- user;
- BI tool;
- notebook;
- API;
- object storage.

Prevention can include:

- export restrictions;
- DLP controls;
- destination policies;
- monitoring;
- user education;
- approval workflows.

### Failure 6 — Expired Temporary Access

Temporary access does not revoke.

Investigate:

- expiration job;
- identity-provider synchronization;
- role assignment;
- clock/time-zone behavior;
- policy cache;
- automation failures.

### Failure 7 — Break-Glass Misuse

Emergency access becomes permanent.

Investigate:

```text
Who granted it?
Why?
When?
What was the expiration?
Why did automatic revocation fail?
What data was accessed?
```

### Universal incident workflow

```text
Failure
→ Detection
→ Investigation
→ Containment
→ Recovery
→ Verification
→ Prevention
```

---

## 41. Common Production Mistakes

### Direct table access everywhere

**Why it happens:** It is simple.

**Risk:** Excessive data exposure.

**Correct approach:** Use narrow roles, views, column policies, and RLS.

### Shared accounts

**Why it happens:** Operational convenience.

**Risk:** No individual accountability.

**Correct approach:** Individual human identities and workload identities.

### Analysts with admin roles

**Why it happens:** Troubleshooting shortcuts.

**Risk:** Privilege escalation and uncontrolled access.

**Correct approach:** Separate data access from security administration.

### Confusing authentication with authorization

**Why it happens:** Both occur during login.

**Risk:** Authenticated users receive excessive permissions.

**Correct approach:** Model authentication and authorization separately.

### Application-only filtering

**Why it happens:** Easy to implement.

**Risk:** Bugs can expose cross-tenant data.

**Correct approach:** Use database/platform enforcement where appropriate.

### No RLS for tenant isolation

**Why it happens:** Developers assume application filters are sufficient.

**Risk:** Cross-tenant leakage.

**Correct approach:** Add a defense-in-depth enforcement boundary.

### Missing `WITH CHECK`

**Why it happens:** Read policies are implemented first.

**Risk:** Unauthorized writes.

**Correct approach:** Test both visibility and mutation policies.

### Securing warehouse access but not object storage

**Why it happens:** Warehouse is considered the data access layer.

**Risk:** Raw files bypass controls.

**Correct approach:** secure every reachable data path.

### Ignoring exports

**Why it happens:** Policy focuses on query execution.

**Risk:** Data leaves the governed platform.

**Correct approach:** include exports, extracts, downloads, and copies in the threat model.

### Ignoring notebooks

**Why it happens:** Notebooks are treated as development tools.

**Risk:** Sensitive data can be copied locally.

**Correct approach:** apply identity, network, export, and logging controls.

### Static masking when dynamic masking is required

**Why it happens:** A permanently transformed dataset seems simpler.

**Risk:** Privileged users may unnecessarily lose access or sensitive values may be copied into new datasets.

**Correct approach:** choose static/dynamic masking according to the use case.

### No policy-as-code

**Why it happens:** Permissions are changed manually.

**Risk:** drift and poor reviewability.

**Correct approach:** version policies and deploy them through controlled workflows.

### No negative tests

**Why it happens:** Engineers test only successful access.

**Risk:** authorization regressions remain invisible.

**Correct approach:** test denial explicitly.

### No audit logging

**Why it happens:** Access is assumed to be safe if policy exists.

**Risk:** incidents cannot be investigated effectively.

**Correct approach:** log security-relevant decisions and administrative changes.

### No access reviews

**Why it happens:** Initial grants are treated as permanent.

**Risk:** privilege creep.

**Correct approach:** review high-risk and privileged access periodically.

### Permanent emergency access

**Why it happens:** Emergency access is easier than normal workflows.

**Risk:** break-glass becomes ordinary access.

**Correct approach:** narrow, time-bound, heavily audited emergency roles.

### Excessive service permissions

**Why it happens:** A single pipeline identity is reused everywhere.

**Risk:** large blast radius.

**Correct approach:** service-specific identities and least privilege.

### No time-bound access

**Why it happens:** Manual revocation is inconvenient.

**Risk:** temporary permissions become permanent.

**Correct approach:** automatic expiry.

### Overly complex policies

**Why it happens:** Every business rule gets encoded directly in the query.

**Risk:** poor performance and difficult security review.

**Correct approach:** simplify policy predicates, align data layout, benchmark, and use appropriate policy layers.

### Failing to test policy changes

**Why it happens:** Security changes are treated as configuration.

**Risk:** accidental exposure.

**Correct approach:** treat policy changes like production code.

---

## 42. Security Design Principles

### Least privilege

Give identities only the permissions required.

**Example:** An Airflow pipeline can write a specific target schema but cannot create security roles.

### Defense in depth

Use:

```text
Identity
+
RBAC
+
ABAC
+
RLS
+
Column Security
+
Storage Permissions
+
Audit
```

### Deny by default

If no explicit policy grants access:

```text
Deny
```

is the safer baseline.

### Explicit allow

Define approved access intentionally.

### Separation of duties

Separate:

```text
Data Owner
Security Administrator
Platform Administrator
Data Consumer
```

where appropriate.

### Policy-as-code

Policies should be:

```text
Versioned
Reviewed
Tested
Audited
Deployable
```

### Auditability

Every important access decision should be explainable.

### Traceability

You should be able to connect:

```text
Identity
→ Request
→ Policy
→ Dataset
→ Decision
→ Audit Event
```

### Temporary access

Use expiration whenever access is inherently temporary.

### Zero-trust awareness

Do not assume:

```text
internal network = trusted
```

Evaluate identity, resource, context, and authorization.

### Identity-centric security

The identity requesting access is a core security boundary.

### Data classification-driven controls

Use classification to determine appropriate protection.

### Secure defaults

New datasets should not accidentally become publicly or broadly accessible.

### Fail closed

If authorization cannot be reliably evaluated, prefer denying access rather than silently allowing it.

---

## 43. Hands-On Production Project

# Build a Fine-Grained Access-Controlled Data Platform

### Architecture

```text
Users
Services
Roles
Policies
   |
   v
PostgreSQL ---- RLS
   |
   +---- Column Controls
   |
   +---- Dynamic Masking
   |
   v
Lakehouse / Warehouse
   |
   +---- PII Tags
   +---- Policy-as-Code
   +---- Audit Logs
   +---- Access Reviews
```

### Required roles

Implement:

1. Analyst role.
2. Finance role.
3. Data Engineer role.
4. ETL service identity.

### Required controls

Implement:

1. Tenant isolation.
2. Column-level protection.
3. Dynamic masking.
4. Policy-as-code.
5. Automated negative tests.
6. Audit logging.
7. Temporary access.
8. Break-glass process.
9. Access review report.

### Suggested repository

```text
fine-grained-access-platform/
├── sql/
│   ├── schema.sql
│   ├── roles.sql
│   ├── grants.sql
│   └── rls.sql
├── policy/
│   └── access-policy.yaml
├── app/
│   └── access_context.py
├── tests/
│   ├── test_positive_access.py
│   ├── test_negative_access.py
│   ├── test_rls.py
│   └── test_policy_regression.py
├── audit/
│   └── audit-schema.sql
└── docs/
    ├── threat-model.md
    ├── enforcement-boundaries.md
    └── access-review.md
```

### Required incident exercises

Inject:

```text
1. Over-permissioned analyst
2. Cross-tenant RLS leak
3. Missing WITH CHECK
4. Direct object-storage bypass
5. Export bypass
6. Failed temporary-access revocation
7. Break-glass misuse
```

For each:

```text
Detect
Investigate
Contain
Recover
Verify
Prevent
```

---

## 44. Checkpoint Questions

### 1. What is the difference between authentication and authorization?

**Answer:** Authentication establishes identity. Authorization determines what the authenticated identity may access or perform.

### 2. What is least privilege?

**Answer:** Giving an identity only the minimum permissions required for its legitimate job.

### 3. What is RBAC?

**Answer:** A model where permissions are assigned to roles and identities receive permissions through those roles.

### 4. What is ABAC?

**Answer:** A model where policy decisions depend on subject, resource, environment, and action attributes.

### 5. Why combine RBAC and ABAC?

**Answer:** RBAC provides stable job-function permissions while ABAC can add contextual restrictions such as classification, region, tenant, or purpose.

### 6. What is column-level security?

**Answer:** Restricting access to specific columns instead of granting access to an entire table.

### 7. What is row-level security?

**Answer:** Restricting which rows an identity can access or modify.

### 8. What is the difference between `USING` and `WITH CHECK`?

**Answer:** `USING` controls which existing rows are visible/eligible for an operation. `WITH CHECK` controls whether inserted or updated rows satisfy the policy.

### 9. How does RLS support multi-tenant systems?

**Answer:** It can enforce that the tenant context of the current identity matches the `tenant_id` of rows being read or modified.

### 10. Why can warehouse security fail if object storage is directly accessible?

**Answer:** The user can bypass the warehouse enforcement boundary and read raw files directly.

### 11. What is tag-based access control?

**Answer:** Policies use metadata classifications such as `PII` or `CONFIDENTIAL` to determine access behavior.

### 12. Why are service identities different from human identities?

**Answer:** Services need stable, workload-specific permissions and lifecycle controls rather than personal permissions.

### 13. What is policy-as-code?

**Answer:** Defining access policy in version-controlled, reviewable, testable artifacts that can be deployed through controlled workflows.

### 14. Why are negative security tests important?

**Answer:** They verify that prohibited actions remain prohibited and catch authorization regressions.

### 15. What is break-glass access?

**Answer:** Controlled emergency access used when normal workflows cannot meet an urgent operational requirement.

### 16. Why should emergency access be time-bound?

**Answer:** It limits the blast radius and prevents emergency permissions from becoming permanent.

### 17. How can fine-grained policies affect query performance?

**Answer:** Policy predicates, joins, masking, and context evaluation can increase planning or execution work. Benchmark and optimize rather than assuming either zero or unacceptable overhead.

---

## 45. Interview Preparation

### Beginner

#### What is authorization?

Authorization determines what an authenticated principal is allowed to do.

#### What is RBAC?

Role-Based Access Control assigns permissions to roles and users/services to roles.

#### What is RLS?

Row-Level Security filters or controls rows according to an authorization policy.

#### What is column-level security?

A mechanism for restricting access to specific columns.

---

### Intermediate

#### RBAC vs ABAC?

RBAC is role-centered and easier to govern. ABAC evaluates attributes and can express more contextual policies. Mature systems may combine them.

#### Role vs user?

A user is an identity; a role is a reusable set of permissions.

#### RLS vs views?

Views can expose a restricted projection, while RLS can enforce row policies at the database table boundary. A secure view is not sufficient if users can bypass it.

#### Static vs dynamic masking?

Static masking permanently transforms copied data. Dynamic masking changes the returned representation based on identity or policy at access time.

#### Grants and revokes?

Grants add permissions; revokes remove them. Effective access also depends on inheritance, ownership, default privileges, and policy behavior.

#### Least privilege?

Only grant the minimum required access.

---

### Advanced

#### Explain PostgreSQL RLS.

PostgreSQL RLS attaches policies to tables. Policies can control row visibility and write eligibility through `USING` and `WITH CHECK`.

#### `USING` vs `WITH CHECK`?

`USING` constrains rows an operation can act on or see. `WITH CHECK` validates new row values for inserts and updates.

#### Multi-tenant isolation?

Use a trusted tenant context, database-enforced RLS, appropriate service identity controls, storage permissions, and automated cross-tenant negative tests.

#### Tag-based policies?

Classify datasets/columns and use reusable policies based on those classifications.

#### Policy-as-code?

Store access policies in version control, validate them in CI, require review, and deploy them through controlled workflows.

#### Access-control testing?

Test both positive and negative cases, including policy regressions and bypass paths.

---

### Senior / Production

#### Design tenant isolation for a SaaS platform.

A strong answer includes:

- workload identity;
- trusted tenant context;
- database RLS;
- `USING` and `WITH CHECK`;
- storage isolation;
- API authorization;
- negative tests;
- audit logging;
- access reviews;
- incident controls.

#### Secure a lakehouse containing PII.

Include:

- classification;
- catalog policy;
- object-storage permissions;
- compute identity;
- row/column controls;
- masking;
- audit;
- export restrictions;
- direct-storage bypass prevention.

#### Prevent warehouse-policy bypass through object storage.

Remove unnecessary direct storage permissions, use scoped workload identities, enforce storage policies, monitor object access, and test alternate data paths.

#### Design service identities for Airflow/Spark/dbt.

Give each workload identity only the permissions required for its pipelines and environments. Prefer workload identity/short-lived credentials where supported.

#### Design break-glass access.

Use an emergency role with:

```text
approval
+
reason
+
narrow scope
+
time limit
+
enhanced audit
+
automatic expiry
+
post-event review
```

#### Design time-bound access.

Model access as a resource with:

```text
principal
resource
permission
reason
start
expiration
approver
```

and enforce expiration automatically.

#### Build an access-review system.

Generate effective permissions, prioritize high-risk access, route reviews to owners, record decisions, revoke unnecessary access, and retain evidence.

#### Diagnose a cross-tenant data leak.

Immediately contain the affected access path, inspect RLS and tenant context, determine scope from audit logs, correct the policy, run regression tests, assess downstream exports, and complete incident review.

#### Balance security and performance.

Keep policies simple, align storage/indexing with common predicates, benchmark at production scale, monitor query plans, and avoid weakening authorization merely to recover performance.

---

## 46. Final Assessment

### Part A — Concepts

1. Explain authentication, authorization, and least privilege.
2. Compare RBAC and ABAC.
3. Explain role inheritance and effective permissions.
4. Explain table, column, and row-level controls.
5. Explain dynamic masking.
6. Explain PostgreSQL RLS.
7. Explain `USING` and `WITH CHECK`.
8. Explain tenant isolation.
9. Explain tag-based policies.
10. Explain service identities.
11. Explain enforcement boundaries.
12. Explain export/bypass risks.
13. Explain policy-as-code.
14. Explain access reviews and time-bound access.
15. Explain break-glass access.

### Part B — SQL

Implement:

```text
roles
grants
RLS
USING
WITH CHECK
secure view
tenant isolation
```

Demonstrate that:

```text
Tenant A cannot read Tenant B.
Tenant A cannot write Tenant B.
Analyst cannot access restricted columns.
```

### Part C — Python

Build a policy evaluator:

```python
def authorize(principal, resource, action, context):
    ...
```

It should return:

```text
ALLOW
or
DENY
```

and provide a reason that can be recorded for audit purposes.

### Part D — Security testing

Write positive and negative tests for:

- analyst;
- finance;
- ETL;
- tenant isolation;
- restricted columns;
- privilege escalation;
- temporary access;
- policy regression.

### Part E — Incident response

A tenant discovers that another tenant's records were visible.

Explain:

1. immediate containment;
2. evidence preservation;
3. RLS investigation;
4. tenant-context investigation;
5. access-log analysis;
6. downstream export analysis;
7. remediation;
8. regression tests;
9. stakeholder communication;
10. prevention.

### Assessment quality bar

A strong answer demonstrates the ability to **design and operate production access controls**, not merely define security terminology.

---

## 47. Production Challenge

> **Design a fine-grained access-control system for a multi-tenant enterprise Data Platform containing PostgreSQL, Kafka, object storage, Spark, a lakehouse, a warehouse, BI tools, Data Scientists, Analysts, Data Engineers, and automated pipelines.**

### Required design

Include:

- identity model;
- RBAC;
- ABAC;
- least privilege;
- database/schema/table grants;
- column-level security;
- dynamic masking;
- row-level security;
- tenant isolation;
- tag-based policies;
- human identities;
- service identities;
- policy-as-code;
- automated negative tests;
- audit logs;
- access reviews;
- approvals;
- time-bound access;
- break-glass access;
- enforcement boundaries;
- export controls;
- performance strategy.

### Suggested architecture

```text
                         Identity Provider
                                |
                                v
                         Users / Services
                                |
                                v
                      Authentication / SSO
                                |
                                v
                     Authorization Layer
                +---------------+---------------+
                |               |               |
               RBAC            ABAC         Tags/PII
                |               |               |
                +---------------+---------------+
                                |
                                v
                         Data Platform
              +-----------------+----------------+
              |                 |                |
              v                 v                v
         PostgreSQL          Warehouse       Lakehouse
              |                 |                |
             RLS           Masking/RLS      Catalog/RLS
              |                 |                |
              +-----------------+----------------+
                                |
                                v
                         Audit Logging
                                |
                                v
                          Access Reviews
```

### Threat model

For every control explain:

```text
Threat
↓
Control
↓
Enforcement boundary
↓
Evidence
↓
Failure mode
↓
Recovery
```

### Senior-level trade-offs

Explicitly justify:

- RBAC vs ABAC;
- database RLS vs application filtering;
- masking vs denial;
- direct storage access;
- service identity scope;
- time-bound vs permanent access;
- break-glass design;
- policy complexity vs performance;
- audit granularity;
- operational burden.

---

## 48. Glossary

| Term | Meaning |
|---|---|
| Authentication | Establishing the identity of a principal |
| Authorization | Determining what an authenticated principal may do |
| Principal | Human or machine actor requesting access |
| Identity | Representation used to authenticate a principal |
| Permission | Authorization to perform an action on a resource |
| Policy | Rules that determine authorization decisions |
| RBAC | Role-Based Access Control |
| ABAC | Attribute-Based Access Control |
| Least privilege | Minimum access required to perform a legitimate task |
| Role | Reusable collection of permissions |
| Grant | Assignment of a permission |
| Revoke | Removal of a permission |
| Column-level security | Restriction of access to individual columns |
| Row-level security | Restriction of access to individual rows |
| RLS | Row-Level Security |
| Dynamic masking | Runtime transformation of sensitive values based on policy |
| Secure view | View designed to expose only approved data |
| Tenant isolation | Preventing one tenant from accessing another tenant's data |
| Policy-as-code | Versioned and testable access-control definitions |
| Access review | Periodic evaluation of existing permissions |
| Audit log | Record of security-relevant activity |
| Time-bound access | Permission with an enforced expiration |
| Break-glass access | Controlled emergency access |
| Service identity | Identity representing a machine/workload |
| Workload identity | Identity assigned to an application or workload |
| Tag-based policy | Policy driven by resource metadata/classification |
| Enforcement boundary | Location where a security policy is actually enforced |
| Privilege escalation | Obtaining permissions beyond those intended |
| Defense in depth | Multiple complementary security controls |
| Deny by default | Access is denied unless explicitly authorized |

---

## 49. Access-Control Checklist

```text
[ ] I understand authentication vs authorization.
[ ] I understand least privilege.
[ ] I understand roles and permissions.
[ ] I understand RBAC.
[ ] I understand ABAC.
[ ] I understand RBAC vs ABAC.
[ ] I can use database/schema/table grants.
[ ] I understand column-level security.
[ ] I understand dynamic masking.
[ ] I understand row-level security.
[ ] I understand PostgreSQL RLS.
[ ] I understand USING.
[ ] I understand WITH CHECK.
[ ] I can design tenant isolation.
[ ] I understand warehouse RLS.
[ ] I understand lakehouse access control.
[ ] I understand tag-based policies.
[ ] I understand PII-aware access control.
[ ] I understand human vs service identities.
[ ] I understand machine-to-machine authorization.
[ ] I understand enforcement boundaries.
[ ] I understand export/bypass risks.
[ ] I understand policy-as-code.
[ ] I can write access-control tests.
[ ] I understand negative security testing.
[ ] I understand policy regression testing.
[ ] I understand audit logging.
[ ] I understand access reviews.
[ ] I understand approval workflows.
[ ] I understand time-bound access.
[ ] I understand break-glass access.
[ ] I understand access-control performance.
[ ] I can design a production access-control architecture.
[ ] I can investigate an access-control failure.
[ ] I can explain why every major control exists.
```

---

## 50. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Section | Code/Example? |
|---|---|---|---|
| RBAC | Yes | 7 | Yes |
| ABAC | Yes | 8 | Yes |
| Least privilege | Yes | 5 | Yes |
| Roles and grants | Yes | 6, 10 | Yes |
| Table/schema access | Yes | 11 | Yes |
| Column security | Yes | 12 | Yes |
| Dynamic masking | Yes | 13 | Yes |
| PostgreSQL RLS | Yes | 15 | Yes |
| Warehouse RLS | Yes | 18 | Yes |
| Lakehouse controls | Yes | 19 | Architecture |
| Tag-based policies | Yes | 20 | Yes |
| Human vs service roles | Yes | 22 | Yes |
| Enforcement boundaries | Yes | 24 | Architecture |
| Export gaps | Yes | 25 | Yes |
| Policy-as-code | Yes | 26 | YAML/Python |
| Automated access-policy tests | Yes | 27, 28 | pytest |
| Audit logs | Yes | 29 | JSON |
| Access reviews | Yes | 30 | Workflow |
| Approval workflows | Yes | 31 | Workflow |
| Time-bound access | Yes | 32 | YAML |
| Break-glass access | Yes | 33 | Workflow |
| Performance considerations | Yes | 35 | Benchmarking |
| Production access-control architecture | Yes | 36, 43, 47 | Yes |

### Final roadmap status

**Topic 08 — Row- and Column-Level Access Control: COMPLETE.**

The module progresses through:

```text
Basic
  ↓
Authentication / Authorization
  ↓
Least Privilege
  ↓
RBAC / ABAC
  ↓
Grants
  ↓
Column Security / Masking
  ↓
Row-Level Security
  ↓
PostgreSQL RLS
  ↓
Warehouse / Lakehouse Controls
  ↓
Tag / PII Policies
  ↓
Service Identity
  ↓
Enforcement Boundaries
  ↓
Policy-as-Code
  ↓
Automated Security Testing
  ↓
Audit / Reviews / Approvals
  ↓
Time-Bound / Break-Glass Access
  ↓
Performance
  ↓
Production Architecture
  ↓
Incident Response
  ↓
Senior Production Design
```

---

## 51. Security Accuracy Requirements

This is a security-critical learning module.

### Never

- invent security controls;
- claim a database policy protects data outside its enforcement boundary;
- claim RLS automatically secures object storage;
- assume application filtering is sufficient;
- expose real credentials;
- use insecure production configurations;
- treat masking as equivalent to access denial;
- claim authentication provides authorization;
- claim policy-as-code automatically guarantees security.

### Always

- explain the actual enforcement boundary;
- distinguish authentication from authorization;
- explain least privilege;
- explain identity lifecycle;
- test negative cases;
- protect audit logs;
- explain bypass paths;
- distinguish educational examples from production architecture;
- verify platform-specific behavior.

Whenever an example is simplified for learning:

> **Educational example — production systems require additional controls and review.**

---

## 52. Version and API Accuracy

Examples involving:

- PostgreSQL;
- SQL;
- Python;
- warehouses;
- lakehouses;
- IAM;
- policy engines

must follow documented APIs and syntax for the installed platform/version.

PostgreSQL is used for detailed RLS implementation because it provides a concrete learning environment. Warehouse and lakehouse examples are intentionally presented at the architectural level unless platform-specific behavior is required.

Do not invent APIs.

The durable knowledge is:

```text
Identity
  ↓
Policy
  ↓
Enforcement
  ↓
Decision
  ↓
Audit
```

---

## 53. Production Reasoning Framework

For every major access-control decision, ask:

```text
Who is the principal?
How was the principal authenticated?
What resource is being accessed?
What action is being requested?
What policy applies?
What data classification exists?
What role/attributes does the principal have?
Is the access least-privileged?
Where is the policy enforced?
Can the user bypass that enforcement?
Can data be exported?
Is the access logged?
Is the access periodically reviewed?
Can the access expire?
What happens during an emergency?
What happens if the policy is wrong?
How is the policy tested?
What is the performance impact?
```

### Senior Data Engineering mindset

Do not ask only:

> "Does this query work?"

Ask:

> "Who can execute it, which rows can they receive, which columns can they receive, what alternate paths exist, and how can I prove that the policy is still correct six months from now?"

---

## 54. Final Quality Bar

Before considering this module complete, verify that it is:

- beginner-friendly;
- technically accurate;
- production-oriented;
- security-conscious;
- practical;
- code-driven;
- progressively structured;
- aligned with the roadmap;
- complete;
- internally consistent.

The learner should finish this module capable of discussing fine-grained access control with:

- Data Engineers;
- Data Architects;
- Security Engineers;
- IAM Engineers;
- Platform Engineers;
- Cloud Engineers;
- Governance teams;
- Privacy teams;
- SRE/DevOps teams.

The final objective is not to memorize SQL commands.

It is to become a Data Engineer who can **design, implement, test, audit, troubleshoot, and operate least-privilege access controls across an enterprise Data Platform.**
