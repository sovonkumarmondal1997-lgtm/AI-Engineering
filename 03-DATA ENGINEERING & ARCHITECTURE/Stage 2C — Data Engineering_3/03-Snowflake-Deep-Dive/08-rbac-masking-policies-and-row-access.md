# 08 — RBAC, Masking Policies, and Row Access

> **Roadmap location:** `Stage 2C — Data Engineering_3/03-Snowflake-Deep-Dive/08-rbac-masking-policies-and-row-access.md`  
> **Lab location:** `experiments/08_rbac/`  
> **Audience:** Data engineers progressing toward production data-platform and applied-AI engineering.

This lesson follows Topic 08 of `roadmap-Snowflake-Deep-Dive.md`. It focuses on Snowflake access control, identity, data protection policies, governance, and auditability—not general-purpose cybersecurity.

> **Version and edition note:** Snowflake evolves continuously. Features such as dynamic data masking, row access policies, and tag-based masking have edition requirements documented by Snowflake (currently Enterprise Edition or higher for the policy features cited here). Network/private-connectivity options and Tri-Secret Secure have separate requirements. Confirm current edition, cloud, region, enabled behavior bundles, grants, and documentation before production rollout. SQL examples use fictional objects and test data. They are learning templates, not evidence that they were executed in an account.

## 1. Learning objectives

By the end, you should be able to:

- Explain securable objects, privileges, grants, role inheritance, and the distinction between authentication and authorization.
- Design least-privilege access for analysts, data engineers, and finance users without making `ACCOUNTADMIN` a daily role.
- Use account roles, database roles, future grants, and managed access schemas to make grants predictable.
- Implement and test dynamic masking policies for email and sensitive identifiers.
- Filter rows through a region mapping table using a row access policy.
- Classify columns with tags and apply tag-based masking where supported.
- Explain secure views/UDFs, network policies, private connectivity, encryption, and Tri-Secret Secure at the appropriate awareness level.
- Query access, login, and query history while accounting for privileges, edition, retention, and data latency.
- Build a safe lab and an auditable governance workflow.

## 2. Prerequisites and lab safety

You should already understand databases, schemas, tables, views, SQL joins, and the earlier Snowflake lessons on architecture, stages, streams/tasks, Time Travel, and cloning. Basic familiarity with Git and deployment pipelines is useful.

Use a dedicated sandbox account or an explicitly approved development database. Do **not** run the lab against production objects, production identities, or real personal data. All sample emails and identifier values are synthetic. Keep administrative and policy-owner roles separate from ordinary test-user roles.

The exact ability to create roles, grants, masking policies, row access policies, tags, and audit queries depends on the active role and account configuration. A statement failing with an authorization error is not a reason to switch reflexively to `ACCOUNTADMIN`; identify the missing privilege and request a scoped grant from the appropriate owner.

## 3. The security model: five different controls

| Control | Question it answers | Snowflake mechanism | What it does not do |
|---|---|---|---|
| Authentication | Who or what is connecting, and how was identity verified? | Password/MFA, key pair, SAML SSO, OAuth, authentication policies and integrations | It does not grant table access by itself. |
| Authorization | Which operations may the active role perform? | Roles, privileges, ownership, grants, role hierarchy | It does not automatically hide sensitive values from a role that can read them. |
| Object access | Can a role use a database/schema/table/view/warehouse? | `USAGE`, `SELECT`, `CREATE`, `OPERATE`, etc. | It is not row filtering or column masking. |
| Column masking | Which value is returned for a protected column? | Dynamic masking policy, possibly attached through a tag | It does not prevent all access to the row or to other columns. |
| Row filtering | Which records are included in a query result? | Row access policy | It does not mask sensitive values in rows that remain visible. |

A production design usually layers these controls. Grant access only to the necessary curated objects, use row policies to scope records, use masking policies to protect sensitive columns, and audit access. **Masking is not a substitute for correct object authorization:** a user who should not access a dataset should not be given broad `SELECT` simply because its columns are masked.

## 4. Beginner: securable objects, roles, privileges, and grants

### 4.1 Securable objects

A securable object is an entity Snowflake can protect with privileges: account-level objects, databases, schemas, tables, views, stages, warehouses, functions, policies, tags, and more. Objects are arranged in containers. A query commonly requires `USAGE` on the database and schema, `SELECT` on the table/view, and `USAGE` on the warehouse. Missing one required privilege can prevent the query.

A privilege is a specific permitted action. A grant assigns a privilege on an object to a role (or, in some cases, a user or other supported grantee). `OWNERSHIP` gives control over an object and is not equivalent to a read-only privilege. Treat ownership as a sensitive administrative capability.

Example access path:

```sql
-- Example names only. Run only in a sandbox with the required authority.
GRANT USAGE ON DATABASE TRAINING_DB TO ROLE ANALYST_ACCESS;
GRANT USAGE ON SCHEMA TRAINING_DB.REPORTING TO ROLE ANALYST_ACCESS;
GRANT SELECT ON TABLE TRAINING_DB.REPORTING.SALES_SUMMARY TO ROLE ANALYST_ACCESS;
GRANT USAGE ON WAREHOUSE ANALYST_WH TO ROLE ANALYST_ACCESS;
```

A `SELECT` grant on a table alone does not necessarily make the object queryable if the role lacks container or warehouse access. Conversely, `USAGE` on a database or schema does not grant `SELECT` on every object inside it.

### 4.2 Account roles and database roles

- **Account role:** exists at account level; can be activated in a session and can receive privileges on account objects.
- **Database role:** scoped to a database; useful for packaging access to that database's objects. A database role cannot be activated directly as the session's primary role. Grant it to an account role, then activate the account role.
- **Functional role:** expresses what a person/team does, such as `ANALYST`, `DATA_ENGINEER`, or `FINANCE_REPORTING`.
- **Access role:** bundles the minimum permissions to a particular data domain or schema, such as `SALES_READ` or `CUSTOMER_PII_READ`.

Separating access roles from functional roles allows permissions to be reused without giving every job family broad direct grants. Account roles can be granted to other account roles to form an inheritance hierarchy. A role granted to a higher role contributes its privileges to that higher role. Avoid cycles and review the *effective* inherited privileges, not only the grants directly attached to a role.

### 4.3 Recommended hierarchy diagram

```text
User identity (human or service principal)
  ├── ANALYST_FUNCTIONAL ───────────────┐
  │                                     ├── SALES_READ (access role)
  ├── FINANCE_FUNCTIONAL ───────────────┘
  │
  └── DATA_ENGINEER_FUNCTIONAL ─────────── PIPELINE_DEV (access role)
                                              │
                                              └── limited CREATE/USAGE in DEV schemas

Database roles (optional object bundles)
  TRAINING_DB.REPORTING_READ ──granted to──> SALES_READ

SYSADMIN ──inherits──> approved custom object-owner / platform roles
SECURITYADMIN ──governs──> users, roles, and grants within its authority
ACCOUNTADMIN (restricted break-glass/admin use; not daily work)
```

This is a conceptual design, not a required Snowflake built-in hierarchy. Your organization should align role names, role ownership, provisioning, and approvals to its own operating model.

### 4.4 System-defined roles

| Role | Purpose and practical guidance |
|---|---|
| `ACCOUNTADMIN` | Highest account-level administrative role, encompassing the responsibilities of `SYSADMIN` and `SECURITYADMIN`. Restrict membership, protect it with strong authentication, and reserve it for tasks that genuinely require it. |
| `SECURITYADMIN` | Manages users/roles and grants through its system privileges, including `MANAGE GRANTS`. That privilege does not automatically make it able to create every object or perform every data operation. |
| `SYSADMIN` | Primarily manages warehouses, databases, schemas, and data-platform objects. Custom object-owner roles should normally be granted into a hierarchy that `SYSADMIN` can manage. |
| `USERADMIN` | Focuses on user and role administration, including creating users and roles within its authority. It is not a reason to grant broad data access. |
| `PUBLIC` | Special role granted to every user. Any privileges granted to `PUBLIC` are effectively available to all users. Avoid sensitive grants to it. |

System-role behavior and available capabilities should be verified in the account's current documentation. Do not add unrelated data privileges directly to system roles as a shortcut; use custom roles and grant them appropriately.

### 4.5 Activate the intended role

```sql
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE();
USE ROLE ANALYST_FUNCTIONAL;
SELECT CURRENT_ROLE();
```

Use the narrowest role that can complete the task. Secondary roles can also affect authorization when enabled, so test in the same role configuration used by the real workload. Do not assume `CURRENT_ROLE()` alone always describes every privilege available to a session when secondary roles are enabled. Policy conditions that must respect inherited role activation may need `IS_ROLE_IN_SESSION()` rather than a simple string comparison; verify the semantics for the exact policy.

### 4.6 Users, default roles, and service identities

Users represent people or services. A user's default role and default warehouse influence initial session context; they are not a replacement for deliberate grants or role activation. Provision a human with roles that match job responsibilities. Provision a service identity with only the permissions required for its workload and a controlled credential lifecycle.

Prefer key-pair authentication or supported OAuth/workload identity patterns for automation where appropriate. Avoid shared service users, long-lived embedded secrets, and credentials stored in source code or notebooks. Where supported, use authentication policies to constrain allowed methods and MFA requirements. Confirm current feature support for the account and client.

| Method | Typical use | Important limitation / control |
|---|---|---|
| Password | Interactive sign-in where allowed | Enforce MFA and organization policy; avoid password reuse and secrets in scripts. |
| MFA | Additional proof for interactive authentication | MFA policy, enrollment, and client compatibility matter; MFA does not grant data privileges. |
| Key pair | Automation and service integrations | Protect private keys, rotate them, scope the identity, and avoid placing key material in repositories. |
| SAML SSO | Federated human login through an identity provider | Map identities/groups carefully; SSO authenticates but does not itself grant table access. |
| OAuth | Delegated or service-to-service access through configured security integrations | Scope tokens and integrations; token acquisition is distinct from Snowflake object grants. |

## 5. Intermediate: designing least-privilege access

### 5.1 Example business design

| Persona | Needs | Suggested roles | Explicitly avoid |
|---|---|---|---|
| Analyst | Read curated metrics; see masked PII; only assigned region where applicable | `ANALYST_FUNCTIONAL` + `SALES_READ` | Raw landing access, DDL, policy ownership, broad grants on all schemas |
| Data engineer | Build pipelines in development; read required raw inputs; write curated outputs | `DATA_ENGINEER_FUNCTIONAL`, `RAW_READ`, `DEV_PIPELINE_WRITE` | Routine `ACCOUNTADMIN`, unnecessary production data visibility, unmanaged grant authority |
| Finance user | Read approved finance reports and finance-specific dimensions | `FINANCE_FUNCTIONAL`, `FINANCE_REPORT_READ` | Broad customer PII, engineering write access, unrelated finance schemas |
| Policy administrator | Own/manage approved masking and row policies | Separate `POLICY_ADMIN` role | Routine analyst work with policy-management privileges |
| Audit reviewer | Read approved metadata/history views | `SECURITY_AUDIT_READ` plus narrow Snowflake database roles | Object mutation and general data access without need |

The table is a design starting point. Real grants depend on job duties, legal obligations, and data classification. Never infer that a title alone justifies access to sensitive fields.

### 5.2 Create custom roles and build a hierarchy

Run role creation with a role authorized to create roles (often `USERADMIN` or a delegated custom role with `CREATE ROLE`). Run object grants as the object owner, schema owner for managed schemas, or an authorized grant administrator as appropriate.

```sql
-- Role creation: use an authorized role, not a daily ACCOUNTADMIN session.
USE ROLE USERADMIN;
CREATE ROLE IF NOT EXISTS ANALYST_FUNCTIONAL;
CREATE ROLE IF NOT EXISTS DATA_ENGINEER_FUNCTIONAL;
CREATE ROLE IF NOT EXISTS FINANCE_FUNCTIONAL;
CREATE ROLE IF NOT EXISTS SALES_READ;
CREATE ROLE IF NOT EXISTS DEV_PIPELINE_WRITE;
CREATE ROLE IF NOT EXISTS FINANCE_REPORT_READ;
CREATE ROLE IF NOT EXISTS POLICY_ADMIN;
CREATE ROLE IF NOT EXISTS SECURITY_AUDIT_READ;

-- Build inheritance: the functional role receives the access role's grants.
GRANT ROLE SALES_READ TO ROLE ANALYST_FUNCTIONAL;
GRANT ROLE FINANCE_REPORT_READ TO ROLE FINANCE_FUNCTIONAL;
GRANT ROLE DEV_PIPELINE_WRITE TO ROLE DATA_ENGINEER_FUNCTIONAL;

-- Grant functional roles to test users only after identities have been provisioned.
-- GRANT ROLE ANALYST_FUNCTIONAL TO USER LAB_ANALYST;
-- GRANT ROLE DATA_ENGINEER_FUNCTIONAL TO USER LAB_ENGINEER;
-- GRANT ROLE FINANCE_FUNCTIONAL TO USER LAB_FINANCE;
```

For a production role tree, ensure approved custom object-owner roles are granted into the `SYSADMIN` hierarchy when that is the chosen operating model. Do not blindly grant every custom role to `SYSADMIN`; privilege inheritance should be intentional and documented.

### 5.3 Database roles

Database roles package access within one database. They are useful when the database owner wants to publish a reusable access bundle without exposing account-wide role-management concerns.

```sql
-- Requires ownership/CREATE DATABASE ROLE authority on TRAINING_DB.
CREATE DATABASE ROLE IF NOT EXISTS TRAINING_DB.REPORTING_READ;
GRANT USAGE ON SCHEMA TRAINING_DB.REPORTING
  TO DATABASE ROLE TRAINING_DB.REPORTING_READ;
GRANT SELECT ON ALL TABLES IN SCHEMA TRAINING_DB.REPORTING
  TO DATABASE ROLE TRAINING_DB.REPORTING_READ;
GRANT SELECT ON FUTURE TABLES IN SCHEMA TRAINING_DB.REPORTING
  TO DATABASE ROLE TRAINING_DB.REPORTING_READ;

-- An account role can inherit a database role.
GRANT DATABASE ROLE TRAINING_DB.REPORTING_READ TO ROLE SALES_READ;
```

Database-role grants have specific constraints, especially around shares and role hierarchies. Review Snowflake's current database-role documentation before reusing a database role in a share design. The database role is not itself selected with `USE ROLE`.

### 5.4 Existing grants, future grants, and managed access schemas

A grant on `ALL TABLES` affects objects that exist when the grant runs. A grant on `FUTURE TABLES` defines privileges for matching objects created later. Production access needs both when existing and future objects must be covered.

```sql
-- Run as the authorized schema owner / grant administrator.
GRANT USAGE ON DATABASE TRAINING_DB TO ROLE SALES_READ;
GRANT USAGE ON SCHEMA TRAINING_DB.REPORTING TO ROLE SALES_READ;
GRANT SELECT ON ALL TABLES IN SCHEMA TRAINING_DB.REPORTING TO ROLE SALES_READ;
GRANT SELECT ON FUTURE TABLES IN SCHEMA TRAINING_DB.REPORTING TO ROLE SALES_READ;
GRANT SELECT ON ALL VIEWS IN SCHEMA TRAINING_DB.REPORTING TO ROLE SALES_READ;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA TRAINING_DB.REPORTING TO ROLE SALES_READ;

-- Example revocation: review impact first, then revoke the exact grant.
REVOKE SELECT ON TABLE TRAINING_DB.REPORTING.OLD_REPORT FROM ROLE SALES_READ;
REVOKE SELECT ON FUTURE TABLES IN SCHEMA TRAINING_DB.REPORTING FROM ROLE SALES_READ;
```

Revoking a future grant prevents the future privilege assignment covered by that grant; it does not necessarily remove privileges already granted to existing objects. Review and revoke existing-object grants separately when required.

A **managed access schema** centralizes object-grant decisions: object owners cannot independently grant/revoke access to their objects; the schema owner or a role with `MANAGE GRANTS` manages grants. This reduces grant sprawl but creates an operational dependency on the designated grant authority. Use it when central governance is worth that trade-off.

```sql
-- Example only: the executing role must own the schema or be authorized to create it.
CREATE SCHEMA IF NOT EXISTS TRAINING_DB.REPORTING_MANAGED WITH MANAGED ACCESS;
```

### 5.5 Revocation and role membership review

```sql
REVOKE ROLE SALES_READ FROM ROLE ANALYST_FUNCTIONAL;
REVOKE ROLE ANALYST_FUNCTIONAL FROM USER LAB_ANALYST;
SHOW GRANTS TO ROLE ANALYST_FUNCTIONAL;
SHOW GRANTS OF ROLE SALES_READ;
SHOW GRANTS TO USER LAB_ANALYST;
```

Review the hierarchy before revoking. If a role is inherited through multiple paths, removing one grant may not remove all effective access. Confirm the actual grants and test with a representative identity after changes.

## 6. Intermediate: dynamic data masking

### 6.1 What masking does

A masking policy changes the value returned for a protected column at query time according to a policy expression. It is not the same as physically overwriting the stored data. Authorized roles may see original values while other roles receive a masked value, `NULL`, or another deliberately chosen representation.

Masking policies are an Enterprise Edition feature in current Snowflake documentation. Confirm availability and current constraints for the target account. Policy creation, policy application, and tag-based application each have privilege requirements. Use a dedicated policy administrator and avoid giving ordinary data engineers unrestricted policy-management privileges.

### 6.2 Create synthetic data

```sql
CREATE DATABASE IF NOT EXISTS TRAINING_DB;
CREATE SCHEMA IF NOT EXISTS TRAINING_DB.RBAC_LAB;

CREATE OR REPLACE TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST (
  CUSTOMER_ID NUMBER,
  REGION VARCHAR,
  EMAIL VARCHAR,
  TEST_IDENTIFIER VARCHAR
);

INSERT INTO TRAINING_DB.RBAC_LAB.CUSTOMER_TEST VALUES
  (101, 'EAST', 'maya.example@example.test', '000-11-2222'),
  (102, 'WEST', 'arun.example@example.test', '000-22-3333'),
  (103, 'EAST', 'nina.example@example.test', '000-33-4444');
```

The identifier resembles an SSN only to demonstrate masking. It is synthetic and is not a real identifier.

### 6.3 Email masking policy

Create the policy in a dedicated policy schema if that matches your governance model. The creator needs the appropriate schema privilege; applying a policy requires the applicable `APPLY MASKING POLICY`/object privileges and policy-management grants. Exact privilege setup is account-specific.

```sql
CREATE SCHEMA IF NOT EXISTS TRAINING_DB.SECURITY;

CREATE OR REPLACE MASKING POLICY TRAINING_DB.SECURITY.MASK_EMAIL
  AS (VAL VARCHAR)
  RETURNS VARCHAR ->
    CASE
      WHEN IS_ROLE_IN_SESSION('PII_CLEAR_READ') THEN VAL
      WHEN VAL IS NULL THEN NULL
      ELSE '***MASKED***'
    END;

ALTER TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST
  MODIFY COLUMN EMAIL
  SET MASKING POLICY TRAINING_DB.SECURITY.MASK_EMAIL;
```

`IS_ROLE_IN_SESSION` is used so that an authorized role in the active role hierarchy can be considered, rather than relying only on an exact `CURRENT_ROLE()` string. Test the expression under the actual primary/secondary-role configuration used by the account. If the policy should allow only a single exact role, a simpler `CURRENT_ROLE()` check may be appropriate, but understand its behavior before deploying.

### 6.4 Mask a sensitive identifier

```sql
CREATE OR REPLACE MASKING POLICY TRAINING_DB.SECURITY.MASK_TEST_IDENTIFIER
  AS (VAL VARCHAR)
  RETURNS VARCHAR ->
    CASE
      WHEN IS_ROLE_IN_SESSION('PII_CLEAR_READ') THEN VAL
      WHEN VAL IS NULL THEN NULL
      ELSE 'XXX-XX-' || RIGHT(VAL, 4)
    END;

ALTER TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST
  MODIFY COLUMN TEST_IDENTIFIER
  SET MASKING POLICY TRAINING_DB.SECURITY.MASK_TEST_IDENTIFIER;
```

Partial masking is not automatically safe. Revealing the last four characters can still enable re-identification when combined with other fields. Choose the output based on a documented threat model and data-minimization requirement. For high-risk identifiers, a fixed mask or `NULL` may be safer.

### 6.5 Grant and test the policy roles

```sql
-- Use an authorized role to create/assign the test role and grant access.
CREATE ROLE IF NOT EXISTS PII_CLEAR_READ;
CREATE ROLE IF NOT EXISTS LAB_CUSTOMER_READER;

-- Example: policy administrator grants the clear-data role only to an approved test user.
-- GRANT ROLE PII_CLEAR_READ TO USER LAB_PRIVILEGED_TEST;
-- GRANT ROLE LAB_CUSTOMER_READER TO USER LAB_MASKED_TEST;

GRANT USAGE ON DATABASE TRAINING_DB TO ROLE LAB_CUSTOMER_READER;
GRANT USAGE ON SCHEMA TRAINING_DB.RBAC_LAB TO ROLE LAB_CUSTOMER_READER;
GRANT SELECT ON TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST TO ROLE LAB_CUSTOMER_READER;
GRANT USAGE ON DATABASE TRAINING_DB TO ROLE PII_CLEAR_READ;
GRANT USAGE ON SCHEMA TRAINING_DB.RBAC_LAB TO ROLE PII_CLEAR_READ;
GRANT SELECT ON TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST TO ROLE PII_CLEAR_READ;
```

Test with two separate test users/sessions where possible. `USE ROLE` switches the active primary role, but the user's granted role set and secondary-role settings can affect the effective session context.

```sql
USE ROLE LAB_CUSTOMER_READER;
SELECT CUSTOMER_ID, EMAIL, TEST_IDENTIFIER
FROM TRAINING_DB.RBAC_LAB.CUSTOMER_TEST
ORDER BY CUSTOMER_ID;

USE ROLE PII_CLEAR_READ;
SELECT CUSTOMER_ID, EMAIL, TEST_IDENTIFIER
FROM TRAINING_DB.RBAC_LAB.CUSTOMER_TEST
ORDER BY CUSTOMER_ID;
```

Expected: the masked reader sees `***MASKED***` for email and a partially masked identifier; a user whose active role hierarchy contains `PII_CLEAR_READ` sees the original test values. The second query only works as intended if that role has been granted to the user/session and the role condition matches the configured hierarchy. Do not treat a query run by the policy owner as sufficient validation.

### 6.6 Masking limitations and information leakage

- Masking is query-time policy enforcement; it does not sanitize copies exported outside Snowflake or replace access governance on downstream systems.
- `COUNT`, grouping, joins, error behavior, and other metadata can sometimes reveal information even when values are masked. Test the whole workload, not just `SELECT *`.
- A role with access to an unprotected alternate table, view, clone, share, or export path may still reach sensitive values. Inventory all copies and paths.
- Policy expressions must return compatible types and be tested for nulls, unusual values, and performance. Policy logic that depends on another column must use a supported conditional masking signature and careful argument mapping.
- Policy attachment precedence and interactions with tag-based policies matter. A directly attached masking policy takes precedence over a tag-based masking policy for the same column in documented cases; verify current behavior when multiple governance policies are involved.

## 7. Intermediate: row access policies and mapping tables

### 7.1 How row filtering works

A row access policy evaluates a Boolean condition for rows and returns only rows for which the policy allows access. It is a query-time filter, not a physical split of the table. It can use session context or a centralized mapping table. Row access policies require Enterprise Edition or higher in current Snowflake documentation. Use mapping tables with controlled write access and protect them from unauthorized modification.

### 7.2 Create a region mapping table

This lab uses role-based mapping for clarity. In production, consider a stable user identity or an approved role hierarchy depending on the access model, and verify the behavior of `CURRENT_ROLE`, `IS_ROLE_IN_SESSION`, and secondary roles. Do not assume a role name is an identity.

```sql
CREATE TABLE TRAINING_DB.SECURITY.ROLE_REGION_ACCESS (
  ROLE_NAME VARCHAR NOT NULL,
  REGION VARCHAR NOT NULL
);

INSERT INTO TRAINING_DB.SECURITY.ROLE_REGION_ACCESS VALUES
  ('LAB_EAST_READER', 'EAST'),
  ('LAB_WEST_READER', 'WEST');

CREATE ROLE IF NOT EXISTS LAB_EAST_READER;
CREATE ROLE IF NOT EXISTS LAB_WEST_READER;

GRANT USAGE ON DATABASE TRAINING_DB TO ROLE LAB_EAST_READER;
GRANT USAGE ON SCHEMA TRAINING_DB.RBAC_LAB TO ROLE LAB_EAST_READER;
GRANT SELECT ON TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST TO ROLE LAB_EAST_READER;
GRANT USAGE ON DATABASE TRAINING_DB TO ROLE LAB_WEST_READER;
GRANT USAGE ON SCHEMA TRAINING_DB.RBAC_LAB TO ROLE LAB_WEST_READER;
GRANT SELECT ON TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST TO ROLE LAB_WEST_READER;
```

### 7.3 Create and attach the row access policy

```sql
CREATE OR REPLACE ROW ACCESS POLICY TRAINING_DB.SECURITY.REGION_FILTER
  AS (ROW_REGION VARCHAR) RETURNS BOOLEAN ->
    EXISTS (
      SELECT 1
      FROM TRAINING_DB.SECURITY.ROLE_REGION_ACCESS AS M
      WHERE M.ROLE_NAME = CURRENT_ROLE()
        AND M.REGION = ROW_REGION
    );

ALTER TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST
  ADD ROW ACCESS POLICY TRAINING_DB.SECURITY.REGION_FILTER ON (REGION);
```

The role that creates the policy needs the relevant policy-creation authority. Row access policies execute with the policy owner's rights, so the policy-owning role must have the required `SELECT` access to the mapping table at runtime. Applying the policy requires the appropriate `APPLY` privilege on the policy and privileges to alter the protected table; managing mapping-table data should be a separate, tightly controlled responsibility. Exact grant setup is account-specific because ownership and managed-access configuration differ. A typical centralized design creates the mapping table under a controlled owner, grants `SELECT` on it to the dedicated policy-owner role, grants `APPLY ON ROW ACCESS POLICY ...` to the table administrator, and keeps `INSERT`/`UPDATE`/`DELETE` with a separate mapping-data administrator.

Illustrative privilege separation (execute only with the appropriate grant authority and adapt ownership to the sandbox):

```sql
-- The mapping-data owner grants read access to the policy owner only.
GRANT SELECT ON TABLE TRAINING_DB.SECURITY.ROLE_REGION_ACCESS
  TO ROLE REGION_POLICY_OWNER;

-- A role authorized to manage policy grants assigns policy ownership/application.
-- GRANT OWNERSHIP ON ROW ACCESS POLICY TRAINING_DB.SECURITY.REGION_FILTER
--   TO ROLE REGION_POLICY_OWNER;
-- GRANT APPLY ON ROW ACCESS POLICY TRAINING_DB.SECURITY.REGION_FILTER
--   TO ROLE REGION_TABLE_ADMIN;
```

These are intentionally separated from the policy DDL: the policy's owner-rights execution model means the mapping-table read must be available to the owner role, while the table administrator should not automatically receive permission to change the mapping data.

**Expected observations:** `LAB_EAST_READER` sees rows whose region is `EAST`; `LAB_WEST_READER` sees rows whose region is `WEST`. A role absent from the mapping table sees no rows because `EXISTS` evaluates false. Test with separate user identities where possible, and ensure no broad secondary role changes the policy context.

### 7.4 Mapping-table safeguards

- Restrict `INSERT`, `UPDATE`, and `DELETE` on the mapping table to a provisioning role with an approval trail.
- Use unique constraints or controlled merge logic operationally; Snowflake standard table constraints may not enforce uniqueness as in some OLTP databases, so validate duplicates explicitly.
- Store the mapping table in the same database as the protected table when required by policy design and to align with Snowflake guidance, particularly when using session role membership functions.
- Test query performance and policy recursion risks. Avoid referencing the protected table from its own policy logic.
- Review role changes and mapping-table changes together; a correct policy can still leak data if the mapping is wrong.

## 8. Tags, data classification, and tag-based masking

### 8.1 Classification model

Tags attach metadata such as `CLASSIFICATION = 'PII'` to objects or columns. A data catalog or governance workflow can use tags to identify sensitive assets and automate policy application. Tagging by itself does not mask or deny access; the policy attached to the tag provides enforcement. Tag-based masking is an Enterprise Edition feature in current Snowflake documentation.

### 8.2 Create a tag and attach a masking policy

```sql
CREATE OR REPLACE TAG TRAINING_DB.SECURITY.DATA_CLASSIFICATION
  COMMENT = 'Fictional lab classification tag: PUBLIC, INTERNAL, PII';

CREATE OR REPLACE MASKING POLICY TRAINING_DB.SECURITY.TAG_MASK_STRING
  AS (VAL VARCHAR)
  RETURNS VARCHAR ->
    CASE
      WHEN SYSTEM$GET_TAG_ON_CURRENT_COLUMN('TRAINING_DB.SECURITY.DATA_CLASSIFICATION') = 'PII'
           AND IS_ROLE_IN_SESSION('PII_CLEAR_READ') THEN VAL
      WHEN SYSTEM$GET_TAG_ON_CURRENT_COLUMN('TRAINING_DB.SECURITY.DATA_CLASSIFICATION') = 'PII'
           AND VAL IS NOT NULL THEN '***PII MASKED***'
      ELSE VAL
    END;

ALTER TAG TRAINING_DB.SECURITY.DATA_CLASSIFICATION
  SET MASKING POLICY TRAINING_DB.SECURITY.TAG_MASK_STRING;

ALTER TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST
  MODIFY COLUMN EMAIL
  SET TAG TRAINING_DB.SECURITY.DATA_CLASSIFICATION = 'PII';

ALTER TABLE TRAINING_DB.RBAC_LAB.CUSTOMER_TEST
  MODIFY COLUMN TEST_IDENTIFIER
  SET TAG TRAINING_DB.SECURITY.DATA_CLASSIFICATION = 'PII';
```

This example demonstrates the general pattern: create tag, create compatible masking policy, attach the policy to the tag, then tag the relevant column. The policy uses a tag-inspection function, so verify the exact supported function and context for your Snowflake version before running; if your account's supported examples use a different documented tag lookup pattern, use that pattern instead. Do not treat a tag string as trustworthy if ordinary users can change it.

**Important implementation note:** tag-based masking privileges depend on where the policy is attached and the applicable grants. Applying a tag-based masking policy at a database/schema level may require account-level `APPLY MASKING POLICY` and `APPLY TAG` privileges; column-level tagging/policy operations have their own privilege and ownership requirements. Prefer narrowly delegated governance roles and confirm the current official privilege matrix.

### 8.3 Verify tags and policy references

```sql
SELECT *
FROM TABLE(TRAINING_DB.INFORMATION_SCHEMA.TAG_REFERENCES(
  'TRAINING_DB.RBAC_LAB.CUSTOMER_TEST', 'TABLE'
));

SELECT GET_DDL('MASKING_POLICY', 'TRAINING_DB.SECURITY.TAG_MASK_STRING');
SHOW TAGS IN SCHEMA TRAINING_DB.SECURITY;
SHOW MASKING POLICIES IN SCHEMA TRAINING_DB.SECURITY;
```

Metadata visibility depends on the active role. `GET_DDL` and metadata commands may not show definitions to every role, particularly for secure objects or protected policy metadata. Test the policy by querying the protected column as masked and authorized test roles.

### 8.4 Tag governance risks

- Incorrect or missing tags can leave columns unprotected if tag-based enforcement depends on classification.
- Inherited tags and propagation can affect downstream objects. Define whether classification should propagate through views, tables, and transformations; validate actual propagation behavior.
- A direct masking policy can take precedence over a tag-based policy. Avoid contradictory policies and maintain a registry of policy ownership and precedence.
- A tag can support only the documented policy attachments and type-compatible signatures. Do not assume a single generic policy automatically protects every data type.
- Make tag changes auditable. Separate classification authority from ordinary pipeline writers, or pipeline code may be able to downgrade classification.

## 9. Advanced: secure views and secure UDFs

A secure view or secure UDF is designed to restrict exposure of its definition to users who are not authorized to see it. This can reduce leakage of implementation details or sensitive logic, but it is not a universal data-loss prevention mechanism. Secure objects can have performance or optimizer trade-offs, and query outputs may still reveal information if the logic itself permits inference.

```sql
CREATE OR REPLACE SECURE VIEW TRAINING_DB.RBAC_LAB.CUSTOMER_REPORT AS
SELECT CUSTOMER_ID, REGION, EMAIL
FROM TRAINING_DB.RBAC_LAB.CUSTOMER_TEST;

GRANT SELECT ON VIEW TRAINING_DB.RBAC_LAB.CUSTOMER_REPORT
  TO ROLE LAB_CUSTOMER_READER;
```

A secure view does not automatically make its selected columns safe: masking and row access policies must still be designed and tested. Avoid publishing a secure view that exposes sensitive raw columns merely because its definition is hidden. Secure UDFs similarly protect definition visibility under documented rules, but they do not replace least-privilege access or careful output design.

## 10. Advanced awareness: network, private connectivity, and encryption

### 10.1 Network policies

Network policies restrict inbound access based on allowed/blocked network identifiers and supported network rules. They are a perimeter control, not a substitute for identity, roles, or object privileges. Incorrect allowlists can lock out users or fail to cover internal-stage traffic; stage access may require separate consideration. Roll out changes with an explicit recovery path and an allowlisted administrative connection.

### 10.2 Private connectivity

Cloud-provider private endpoints can route supported Snowflake traffic over private connectivity rather than the public internet. Availability depends on cloud, region, account edition, and feature. Private connectivity reduces certain network exposure paths but does not eliminate the need for authentication, authorization, endpoint controls, and audit.

### 10.3 Encryption and customer-managed keys

Snowflake provides encryption capabilities; some configurations allow customer-managed keys. Tri-Secret Secure combines Snowflake-managed and customer-managed key material with Snowflake's built-in authentication in a documented dual-key model. Current documentation lists Business Critical or higher for Tri-Secret Secure. It is an awareness topic here: understand key ownership, rotation, availability, and operational dependencies, and confirm the exact cloud-provider and edition prerequisites before design.

Do not claim that encryption alone enforces row/column authorization or guarantees GDPR compliance. Encryption, identity, policy enforcement, data lifecycle, and audit are complementary controls.

## 11. Advanced: access history and audit queries

### 11.1 What each history source answers

| Source | Use | Key caveats |
|---|---|---|
| `SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY` | Object/column access and data lineage signals | Current docs list Enterprise Edition or higher, approximately three-hour latency, and up to one year of history. Some query types/fields have documented coverage constraints. |
| `SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY` | Successful and failed login attempts and related details | Requires access to the relevant shared database view; expect ingestion latency and retention limits. |
| `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` | Query text/metadata, user, role, warehouse, execution state and timing | Account Usage is delayed; Information Schema query-history table functions cover a shorter time window. Handle query text as sensitive because it can contain literals. |
| `SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES` | Current/historical grant metadata available through the view | Metadata latency and privilege visibility apply; combine with direct `SHOW GRANTS` checks. |

Snowflake's shared `SNOWFLAKE` database provides database roles for scoped metadata access in supported configurations. Current docs map `ACCESS_HISTORY` and `QUERY_HISTORY` to `GOVERNANCE_VIEWER`, and `LOGIN_HISTORY` to `SECURITY_VIEWER`. Grant only the required database role to the audit role; do not default to `IMPORTED PRIVILEGES` on the entire `SNOWFLAKE` database if a narrower database role is sufficient.

```sql
-- Illustrative least-privilege access for a security/audit role.
GRANT DATABASE ROLE SNOWFLAKE.GOVERNANCE_VIEWER TO ROLE SECURITY_AUDIT_READ;
GRANT DATABASE ROLE SNOWFLAKE.SECURITY_VIEWER TO ROLE SECURITY_AUDIT_READ;

USE ROLE SECURITY_AUDIT_READ;
```

Granting database roles may require an authorized administrator and may be blocked by account-specific policy. Confirm the exact grant authority and database-role availability.

### 11.2 Investigate sensitive-column access

`ACCESS_HISTORY` exposes semi-structured arrays such as `direct_objects_accessed` and `base_objects_accessed`. The exact JSON structure can evolve, so inspect sample rows and the current column reference before building a permanent parser.

```sql
SELECT
  QUERY_ID,
  QUERY_START_TIME,
  USER_NAME,
  DIRECT_OBJECTS_ACCESSED,
  BASE_OBJECTS_ACCESSED
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE QUERY_START_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND (TO_VARCHAR(DIRECT_OBJECTS_ACCESSED) ILIKE '%CUSTOMER_TEST%'
       OR TO_VARCHAR(BASE_OBJECTS_ACCESSED) ILIKE '%CUSTOMER_TEST%')
ORDER BY QUERY_START_TIME DESC;
```

This broad search is useful for an initial investigation but can be imprecise because it stringifies structured data. For a durable report, flatten the JSON arrays using the documented schema and filter on the relevant object/column fields rather than relying on substring matching.

```sql
-- Exploratory flattening template. Validate JSON field names against current docs/sample rows.
SELECT
  H.QUERY_ID,
  H.QUERY_START_TIME,
  H.USER_NAME,
  H.ROLE_NAME,
  OBJ.VALUE:objectName::STRING AS OBJECT_NAME,
  COL.VALUE:columnName::STRING AS COLUMN_NAME
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY AS H,
LATERAL FLATTEN(INPUT => H.DIRECT_OBJECTS_ACCESSED) AS OBJ,
LATERAL FLATTEN(INPUT => OBJ.VALUE:columns) AS COL
WHERE H.QUERY_START_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND OBJ.VALUE:objectName::STRING ILIKE '%CUSTOMER_TEST%'
ORDER BY H.QUERY_START_TIME DESC;
```

Field names and array shape must be validated against the current `ACCESS_HISTORY` reference before operationalizing this query. Do not silently interpret a no-row result as proof that no one accessed the data: history can be delayed, the view may lack required coverage, the role may not see the data, or the object name/filter may be wrong.

### 11.3 Login investigation

```sql
SELECT
  EVENT_TIMESTAMP,
  USER_NAME,
  CLIENT_IP,
  REPORTED_CLIENT_TYPE,
  IS_SUCCESS,
  ERROR_CODE,
  ERROR_MESSAGE
FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY
WHERE EVENT_TIMESTAMP >= DATEADD('day', -7, CURRENT_TIMESTAMP())
ORDER BY EVENT_TIMESTAMP DESC;
```

Column availability can differ by schema/version; check the current `LOGIN_HISTORY` reference and use only columns present in your account. Keep the output restricted because IP addresses, usernames, and error details are sensitive operational data.

### 11.4 Query investigation

```sql
SELECT
  QUERY_ID,
  START_TIME,
  USER_NAME,
  ROLE_NAME,
  WAREHOUSE_NAME,
  EXECUTION_STATUS,
  QUERY_TEXT
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD('day', -1, CURRENT_TIMESTAMP())
  AND USER_NAME = 'LAB_MASKED_TEST'
ORDER BY START_TIME DESC;
```

Again, validate column names against the current view. Query text can contain literal data or business-sensitive SQL; limit who can see it and avoid exporting it casually. Account Usage views are delayed, so use a more immediate supported history interface if incident response cannot wait for the Account Usage latency.

### 11.5 Review excessive privileges

```sql
SELECT
  GRANTEE_NAME,
  GRANTED_TO,
  GRANTED_ON,
  NAME,
  PRIVILEGE,
  GRANTED_BY,
  CREATED_ON
FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
WHERE DELETED_ON IS NULL
  AND (NAME ILIKE '%ACCOUNTADMIN%'
       OR GRANTEE_NAME ILIKE '%ACCOUNTADMIN%'
       OR PRIVILEGE IN ('OWNERSHIP', 'MANAGE GRANTS', 'APPLY MASKING POLICY', 'APPLY ROW ACCESS POLICY'))
ORDER BY GRANTEE_NAME, NAME;
```

The `GRANTS_TO_ROLES` view uses `GRANTEE_NAME` and `GRANTED_TO` rather than a generic `ROLE_NAME` column. Confirm the current view definition before extending this report, because the view is not a complete inventory of every supported grant/object type. Supplement metadata queries with `SHOW GRANTS OF ROLE ACCOUNTADMIN`, `SHOW GRANTS TO USER <user_name>`, user/role provisioning records, and tests of effective access. The sample query is a triage filter, not a complete effective-access graph; a role's direct grants do not tell the entire story if it inherits other roles.

Audit checklist:

1. Enumerate users and service identities; identify stale identities and unexpected defaults.
2. Review direct role grants and inherited roles, especially administrative roles.
3. Inventory `OWNERSHIP`, `MANAGE GRANTS`, policy application privileges, and broad `SELECT` grants.
4. Compare object classification tags to actual policy references.
5. Test masked and unmasked behavior with representative identities and secondary-role settings.
6. Confirm that region mappings match business authorization records.
7. Check history latency, retention, and access permissions before concluding an incident timeline.
8. Record reviewer, date, exceptions, remediation owner, and due date.

## 12. Infrastructure as code and change governance

Use version-controlled, reviewed changes for roles, grants, policies, tags, and object definitions. The Snowflake Terraform provider can manage supported account resources and policy-related objects; `schemachange` can apply versioned SQL migrations. They solve different but complementary problems and should be used only for resource types and workflows supported by the selected versions.

A safe deployment pattern is:

1. Commit SQL/IaC changes with a ticket and data-owner approval for sensitive access.
2. Run static checks and deploy into a sandbox or non-production account.
3. Validate grants, policy syntax, object references, and positive/negative test cases.
4. Require review for changes that add privileges, unmask data, alter row mappings, or change tag classification.
5. Deploy through a controlled service identity with scoped permissions.
6. Record deployment/query IDs and validate the resulting grants and policy references.
7. Monitor audit history and roll back using a reviewed compensating change if necessary.

Do not store private keys, OAuth secrets, passwords, or token material in Terraform state, SQL files, or Git without approved secret-handling controls. IaC can make an insecure policy repeatable; review security intent as well as syntax.

## 13. Privacy, retention, and GDPR interactions

Classification and access policy are part of a broader data lifecycle. Identify why each field is collected, which roles need it, how long it is retained, where it is copied, and how deletion requests are handled. GDPR obligations depend on context, lawful basis, controller/processor roles, exceptions, and other applicable law; a Snowflake feature or configuration alone does not establish compliance.

Retention mechanisms such as Time Travel, Fail-safe, clones, exports, shares, and downstream copies can affect how deletion and restoration behave. A policy that masks a value does not delete it. A tag that labels a column `PII` does not enforce a deletion schedule unless connected to a governed workflow. Coordinate data deletion with legal/privacy teams, backups/retention policies, downstream systems, and incident-response procedures. Document exceptions and verify deletion behavior against current Snowflake documentation and contractual obligations.

## 14. Threat scenarios and production controls

| Scenario | Failure mode | Mitigation / verification |
|---|---|---|
| Analyst receives broad `SELECT` on raw data | Masking on curated table is bypassed through a raw copy | Remove unnecessary raw grants; inventory alternate tables, views, clones, shares, and stages. |
| A user gets `ACCOUNTADMIN` for convenience | Routine activity can change grants, users, and security controls | Use scoped custom roles, protected admin identities, approval workflow, and periodic membership review. |
| Future grants omitted | New tables are accessible to creators but not intended consumers, or access is inconsistent | Test creation of a new table and verify both existing and future grant paths. |
| Role condition uses only `CURRENT_ROLE()` | Inherited/secondary role behavior differs from expectation | Choose context functions deliberately; test the real session role hierarchy. |
| Mapping table is writable by analysts | Region policy is bypassed by altering mappings | Separate mapping administration; audit changes; validate mappings against an authoritative source. |
| Tag removed or downgraded | Tag-based masking no longer protects the intended column | Restrict tag mutation, audit tag references, add deployment guardrails, and run negative tests. |
| Masking policy exposes last digits | Re-identification by joining with other data | Prefer stronger masking where needed; conduct privacy review and test inference paths. |
| `ACCESS_HISTORY` returns no rows | Analyst assumes no sensitive data was read | Check edition, grants, latency, retention, query coverage, and JSON filters before drawing conclusions. |
| Service key leaks from repository | Attacker authenticates as an approved service identity | Rotate/revoke credential, review login/query history, reduce identity privileges, and use managed secrets. |
| Secure view is treated as a security boundary by itself | Raw data is exposed through another object or output inference | Apply object authorization, masking/row policies, and downstream access reviews. |

## 15. Hands-on lab — `experiments/08_rbac/`

### 15.1 Suggested folder layout

```text
experiments/08_rbac/
├── README.md
├── 00-preflight.sql
├── 01-roles-and-grants.sql
├── 02-masking-policies.sql
├── 03-row-access-policy.sql
├── 04-tags-and-tag-masking.sql
├── 05-audit-queries.sql
├── 06-verify.sql
└── 99-cleanup.sql
```

This lesson provides the file contents inline. Copy each corresponding section into the named file if building the repository tree. Do not create or overwrite files in a production repository without review.

### 15.2 Lab roles and permissions

You need a sandbox database and roles that can create the lab schema/tables, create custom roles, grant the required object privileges, create/apply masking and row access policies, and create/assign tags. Some steps require object ownership or specific policy privileges. For Account Usage history, you need access to the relevant Snowflake database role and a supported edition for `ACCESS_HISTORY`. Your account may not permit every step; ask an administrator for the narrowest required grant rather than escalating your session.

Preflight:

```sql
SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();
SHOW DATABASES LIKE 'TRAINING_DB';
SHOW ROLES LIKE 'LAB_%';
```

Record the account, role, edition if available through your normal administrative process, and lab start time. If `TRAINING_DB` already exists and is not disposable, use a uniquely named lab database instead.

### 15.3 Exercise 1 — role hierarchy and scripted grants

Use Sections 5.2–5.4 as `01-roles-and-grants.sql`. Run only the statements that your authorized sandbox role is permitted to run. Verify:

```sql
SHOW GRANTS TO ROLE ANALYST_FUNCTIONAL;
SHOW GRANTS OF ROLE SALES_READ;
SHOW GRANTS TO ROLE LAB_CUSTOMER_READER;
SHOW FUTURE GRANTS IN SCHEMA TRAINING_DB.RBAC_LAB;
```

Expected: functional roles inherit the selected access roles; future table grants are listed for the intended schema. If `SHOW FUTURE GRANTS` syntax or output differs in the account's current release, use the corresponding documented `SHOW FUTURE GRANTS` form.

Create a disposable table after future grants are configured, then check `SHOW GRANTS ON TABLE ...` to confirm whether the expected role received the intended privilege. Do not assume future grants were applied retroactively to existing objects.

### 15.4 Exercise 2 — masking email and identifier

Run Sections 6.2–6.5 using the policy-authorized role. Test using two distinct user identities if available. If you only have one user, switch roles for an initial exercise, but document that this is weaker than an identity-isolated test and verify secondary-role settings. Expected output: masked role sees masks; approved PII role sees the fictional raw values.

Negative test: query the same columns with a role that has `SELECT` but is not approved for clear data. It must not receive raw values. Positive test: approved role sees only what policy permits. If both tests show raw values, stop and investigate policy attachment, role grants, context function semantics, secondary roles, and whether you queried the expected object.

### 15.5 Exercise 3 — region row access

Run Section 7 with two test roles. Expected results: East reader returns only `EAST` rows; West reader returns only `WEST` rows. Also test an unmapped role and expect zero rows. Verify that the policy is attached to the intended table and that the mapping table contains only approved entries.

```sql
SELECT REGION, COUNT(*) AS ROWS_VISIBLE
FROM TRAINING_DB.RBAC_LAB.CUSTOMER_TEST
GROUP BY REGION
ORDER BY REGION;

SELECT *
FROM TRAINING_DB.SECURITY.ROLE_REGION_ACCESS
ORDER BY ROLE_NAME, REGION;
```

The mapping table's own access must be restricted; do not grant broad write access just to make the lab convenient.

### 15.6 Exercise 4 — tag-based classification and masking

Run Section 8 after confirming the account edition and exact current tag-based masking syntax. Apply `PII` to the email and test-identifier columns, then verify tag references and query output as both roles. Add a harmless `INTERNAL` tag to a non-sensitive lab column and verify that the policy does not accidentally mask it.

If tag-based masking is unavailable in the sandbox, record the edition/feature limitation and complete the direct masking policy exercise instead. Do not simulate success by claiming the tag-based policy was enforced.

### 15.7 Exercise 5 — investigate sensitive-column access

Grant `SNOWFLAKE.GOVERNANCE_VIEWER` to the audit role if permitted and supported, then run the Section 11 query after making several test queries against `CUSTOMER_TEST`. `ACCESS_HISTORY` may take up to roughly three hours to show records, and it requires Enterprise Edition or higher under current docs. The query may return nothing immediately. That is an expected limitation, not proof the feature failed or that no access occurred.

Use `QUERY_HISTORY` to locate the test query IDs where available, and correlate them with access history after its latency window. Record the query ID, timestamp, role, object/column evidence, and any uncertainty. Do not include actual sensitive values in the audit report.

### 15.8 Troubleshooting

| Symptom | Checks |
|---|---|
| `CREATE ROLE` denied | Confirm active role has role-creation authority; request a scoped grant. |
| `GRANT` denied in managed schema | Grant decisions may be centralized to schema owner or `MANAGE GRANTS` role. |
| Query fails despite `SELECT` grant | Check database/schema `USAGE`, warehouse `USAGE`, active role, and object name. |
| Masking policy returns raw value to unexpected role | Verify policy attachment, hierarchy, `IS_ROLE_IN_SESSION` result, secondary roles, and queried object. |
| Row policy returns zero rows for expected region | Verify exact role name and region strings in mapping table; confirm policy argument is bound to correct column. |
| Tag-based policy does not apply | Verify edition, tag assignment, policy attachment, type compatibility, privileges, and precedence from direct policies. |
| `ACCESS_HISTORY` inaccessible | Verify Enterprise Edition+, `GOVERNANCE_VIEWER` or equivalent supported access, and shared database privileges. |
| Audit query returns no records | Allow for latency; validate time window, query executed, object JSON shape, retention, and access privileges. |

### 15.9 Cleanup

Cleanup is destructive. Confirm that `TRAINING_DB` and all lab objects were created solely for this exercise. Never run broad `DROP DATABASE` against a shared or pre-existing database.

```sql
-- Review before executing. Run with an authorized owner/admin role.
-- DROP DATABASE TRAINING_DB;
```

If `TRAINING_DB` contains anything other than this lab, do **not** drop it. Instead, drop only the specifically named disposable lab objects after confirming dependencies. Remove lab users and roles only if they were created solely for this exercise and no other grants depend on them. Before removing a role, inspect `SHOW GRANTS OF ROLE ...` and `SHOW GRANTS TO ROLE ...`.

### 15.10 Safe test strategy

- Use fake values and a dedicated sandbox; no real SSNs, customer emails, or production exports.
- Keep an administrator session separate from masked/unmasked test sessions.
- Capture expected and actual results without recording sensitive values.
- Include negative tests: unapproved role, unmapped region, missing grant, and newly created table after future grants.
- Change one control at a time and preserve the previous SQL/IaC revision for rollback.
- Record whether each feature was available and tested, blocked by permissions, or not observable because of history latency.

## 16. Production governance checklist

Before launch:

- [ ] Data owners and security/privacy reviewers approved the access model.
- [ ] Roles separate functional duties from reusable access grants.
- [ ] Administrative role membership is limited, monitored, and reviewed.
- [ ] Database/schema/table/view/warehouse grants are explicitly documented.
- [ ] Existing and future grants are both addressed.
- [ ] Managed access schemas have a defined grant owner and operational process.
- [ ] Masking and row access policies have positive and negative tests.
- [ ] Role hierarchy and secondary-role behavior have been tested.
- [ ] Sensitive columns are classified; tag changes are restricted and audited.
- [ ] Mapping tables have controlled write access and reviewable change history.
- [ ] Alternate copies, clones, shares, stages, and downstream exports are included in the threat model.
- [ ] Audit queries have known privileges, latency, retention, and coverage limits.
- [ ] IaC/migrations are reviewed, versioned, and deployed through a scoped identity.
- [ ] Credential rotation, deprovisioning, and access recertification are operationalized.
- [ ] Privacy and retention requirements are documented with the appropriate legal/privacy owners.

## 17. Common mistakes

1. **Granting privileges directly to users instead of roles by default.** Role-based grants are easier to review and reuse. Direct user grants exist in Snowflake but should be deliberate exceptions.
2. **Over-using `ACCOUNTADMIN`.** This expands the blast radius and makes attribution and least-privilege review harder.
3. **Forgetting future grants.** Existing objects may work while newly created objects behave differently.
4. **Masking only in an application.** Other clients and SQL users may query the same object directly. Use Snowflake policy enforcement where appropriate.
5. **Assuming masking blocks table access.** A masked user still has access to the row and possibly to other columns; use object privileges and row policies as needed.
6. **Using `CURRENT_ROLE()` without testing role inheritance.** Secondary roles and role activation can change effective authorization. Choose the context function intentionally.
7. **Making a mapping table writable by the people being filtered.** The policy is only as trustworthy as its mapping data.
8. **Treating tags as enforcement by themselves.** A tag needs an applicable policy and correct privileges.
9. **Assuming tag-based masking is available in every edition.** Check current edition and constraints before planning rollout.
10. **Assuming history views are real-time or exhaustive.** Account Usage has latency and coverage/retention constraints.
11. **Granting `IMPORTED PRIVILEGES` broadly to expose audit history.** Prefer scoped Snowflake database roles where available and appropriate.
12. **Treating secure views/UDFs as a replacement for data authorization.** Definition protection does not prevent inference from outputs or alternate access paths.
13. **Claiming GDPR compliance because data is masked or encrypted.** Compliance requires context-specific legal, operational, and lifecycle controls.

## 18. Practice questions with answers

### Q1. What is the difference between authentication and authorization?
**Answer:** Authentication establishes identity using a configured method; authorization determines what that identity can do through roles, privileges, and policies.

### Q2. Why separate functional roles and access roles?
**Answer:** Access roles package permissions for reusable data domains; functional roles combine only the access bundles needed for a job. This reduces duplicated grants and makes review clearer.

### Q3. Does `GRANT SELECT ON FUTURE TABLES` grant access to tables that already exist?
**Answer:** No. It applies to qualifying future objects. Use appropriate `ALL` grants for existing objects and review the result.

### Q4. Why is `ACCOUNTADMIN` unsuitable for routine analyst work?
**Answer:** It carries broad administrative capability, increasing accidental-change and compromise impact. Use narrow roles for normal tasks and reserve high privilege for approved administrative work.

### Q5. Is a masked value physically changed in the table?
**Answer:** Normally no. A masking policy controls the query-time value returned for a protected column. It does not sanitize exported copies or alternate tables.

### Q6. Why might `IS_ROLE_IN_SESSION()` be preferable to `CURRENT_ROLE()` in a masking policy?
**Answer:** It can evaluate whether a role is active in the session's role hierarchy, which is useful when inherited roles matter. Confirm exact policy semantics and secondary-role behavior for the target design.

### Q7. What is the difference between masking and a row access policy?
**Answer:** Masking changes values returned for columns; a row access policy determines which rows are returned. Neither replaces object-level authorization.

### Q8. Why is a row-policy mapping table sensitive?
**Answer:** Its entries define which roles/users can see which regions or records. Unauthorized edits can expand access even if the policy SQL is correct.

### Q9. Does assigning a `PII` tag automatically mask a column?
**Answer:** No. A compatible masking policy must be attached to the tag and the tag must be correctly applied or inherited; edition, privilege, type, and precedence constraints also apply.

### Q10. Why might `ACCESS_HISTORY` show no recent query?
**Answer:** The view may be delayed, the query may not be covered by the view's documented behavior, the filter may be wrong, or the role may lack access. A no-row result alone does not prove no access occurred.

### Q11. What does a secure view protect?
**Answer:** It restricts exposure of the view definition to unauthorized users under documented rules. It does not guarantee that the output cannot leak information or that other objects do not expose the same data.

### Q12. Does encryption or masking alone guarantee GDPR compliance?
**Answer:** No. Compliance depends on the data, purpose, legal basis, retention/deletion, access, downstream copies, contracts, and applicable law. Involve privacy/legal specialists.

## 19. Topic 08 checkpoint

You are ready to continue when you can demonstrate that you can:

- [ ] Design a least-privilege role hierarchy for analysts, engineers, and finance users.
- [ ] Explain system roles and avoid routine `ACCOUNTADMIN` use.
- [ ] Distinguish authentication, object authorization, masking, and row filtering.
- [ ] Use `USE ROLE`, review inherited privileges, and explain default-role/service-identity considerations.
- [ ] Implement object grants, revocations, future grants, and a managed access schema with appropriate authority.
- [ ] Apply and test role-dependent masking on email and a synthetic sensitive identifier.
- [ ] Implement a region row access policy using a controlled mapping table and verify behavior with two roles.
- [ ] Classify columns using tags and explain tag-based masking constraints.
- [ ] Explain secure views/UDFs, network policies, private connectivity, encryption, and Tri-Secret Secure at an awareness level.
- [ ] Query `ACCESS_HISTORY`, `LOGIN_HISTORY`, and `QUERY_HISTORY` while accounting for privileges, edition, latency, and retention.
- [ ] Explain how Terraform and schemachange can support reviewed, repeatable security changes.
- [ ] Describe how data classification, retention, privacy, and deletion obligations interact.

## 20. Official documentation

Use the current Snowflake documentation for exact syntax, edition requirements, and grants. The references below support the key implementation areas covered in this lesson.

- [Overview of Access Control](https://docs.snowflake.com/en/user-guide/security-access-control-overview)
- [Access Control Best Practices](https://docs.snowflake.com/en/user-guide/security-access-control-considerations)
- [Access Control Privileges](https://docs.snowflake.com/en/user-guide/security-access-control-privileges)
- [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies)
- [Dynamic Data Masking](https://docs.snowflake.com/en/user-guide/security-column-ddm-use)
- [Advanced Column-level Security](https://docs.snowflake.com/en/user-guide/security-column-advanced)
- [Understanding Row Access Policies](https://docs.snowflake.com/en/user-guide/security-row-intro)
- [Using Row Access Policies](https://docs.snowflake.com/en/user-guide/security-row-using)
- [Tag-based Masking Policies](https://docs.snowflake.com/en/user-guide/tag-based-masking-policies)
- [Attribute-based Access Control using Tag-based Policies](https://docs.snowflake.com/en/user-guide/tag-based-policies)
- [Secure Views](https://docs.snowflake.com/en/user-guide/views-secure)
- [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies)
- [Private Connectivity for Inbound Traffic](https://docs.snowflake.com/en/user-guide/private-connectivity-inbound)
- [Tri-Secret Secure](https://docs.snowflake.com/en/user-guide/security-encryption-tss-self-serve-private)
- [Account Usage Views](https://docs.snowflake.com/en/sql-reference/account-usage)
- [ACCESS_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/access_history)
- [LOGIN_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/login_history)
- [QUERY_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/query_history)
- [GRANTS_TO_ROLES](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles)

---

**Completion standard:** be able to explain not only how to create each role or policy, but which role is allowed to administer it, how you will prove both allowed and denied cases, what audit evidence exists, and what limitations remain. Never claim a control is effective solely because its DDL succeeded.
