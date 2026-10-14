# Environment Promotion: Dev, Staging, and Prod

**Stage 2 — Python for Data Engineering**  
**Module 2.18 — Containers, Infrastructure, and CI/CD for Data**  
**Phase D — Delivering Changes**  
**Topic 06 — Environment Promotion: Dev, Staging, and Prod**

> **Module outcome:** Learn how a Data Engineering change moves safely from development to staging to production through environment isolation, immutable artifact promotion, realistic validation, approvals, controlled rollout, and recovery.

---

## 1. What You Will Learn

By the end of this module, you should be able to:

- explain why development, staging, and production environments exist;
- isolate cloud accounts/projects, catalogs, schemas, buckets, identities, and infrastructure;
- keep environment differences in configuration rather than application code;
- build an immutable artifact once and promote that exact artifact through environments;
- use image digests to identify the exact container tested and deployed;
- promote dbt packages/artifacts and DAG versions consistently;
- design dependency-aware deployment ordering;
- handle database migrations safely;
- use synthetic, sampled, or masked data in non-production;
- compare trunk-based development and release branches;
- use semantic versioning and changelogs;
- perform shadow runs and compare outputs;
- create ephemeral environments and clean them up;
- understand code rollback versus data rollback;
- use time travel, restore, and backfills as data-recovery mechanisms;
- apply expand-and-contract for breaking schema changes;
- use feature flags and progressive data rollout to reduce blast radius;
- maintain deployment/change records and auditability;
- create promotion checklists and rollback runbooks;
- perform production incident drills involving code, artifacts, migrations, data, and environment state.

The central principle is:

> **Promote artifacts, do not rebuild them.**

---

# 2. The Problem Environment Promotion Solves

A production data platform should not work like this:

```text
Developer
   ↓
Production
   ↓
Unexpected failure
   ↓
Data impact
```

A safer system separates the lifecycle:

```text
Development
    ↓
Validation
    ↓
Staging
    ↓
Approval
    ↓
Production
```

But environment promotion is more than copying source code.

The stronger model is:

```text
Code
 ↓
Immutable Artifact
 ↓
DEV
 ↓
Validation
 ↓
Same Artifact
 ↓
STAGING
 ↓
Realistic Validation
 ↓
Approval
 ↓
Same Artifact
 ↓
PRODUCTION
```

This gives the organization multiple opportunities to discover problems before the change reaches real workloads.

---

# 3. Why Separate Environments Exist

Environment separation provides:

- safe experimentation;
- realistic validation;
- production protection;
- controlled deployment;
- rollback opportunities;
- auditability.

A developer should be able to break something in development without corrupting production data.

A staging environment should expose integration and operational problems before production.

Production should have the strictest access and deployment controls because it contains real workloads and real business consequences.

---

# 4. Dev / Staging / Production Mental Model

## 4.1 Development

Purpose:

- rapid development;
- experimentation;
- debugging;
- developer feedback.

Development can intentionally be flexible.

Typical characteristics:

```text
Broad developer access
Synthetic/sample data
Frequent deployment
Lower infrastructure cost
Fast iteration
```

## 4.2 Staging

Purpose:

- production-like validation;
- integration testing;
- realistic infrastructure;
- shadow comparison;
- release verification.

Staging should answer:

> **Does this artifact behave correctly under conditions sufficiently similar to production?**

## 4.3 Production

Purpose:

- real workloads;
- real business data;
- strict access;
- controlled deployment;
- operational reliability.

Production should optimize for safety rather than experimentation.

---

# 5. Environment Comparison

| Dimension | Dev | Staging | Production |
|---|---|---|---|
| Purpose | Development | Validation | Real workloads |
| Data | Synthetic/sample/masked | Realistic | Production |
| Access | Broad developer access | Restricted | Highly restricted |
| Deployment | Automatic/frequent | Controlled | Approved |
| Risk | Lower | Medium | Highest |
| Rollback | Frequent | Practiced | Controlled |
| Infrastructure | Cost-conscious | Production-like | Production-grade |
| Change tolerance | High | Medium | Low |

The exact architecture differs by organization, but the risk gradient should be deliberate.

---

# 6. Environment Isolation

Environment isolation should cover more than application processes.

Separate, where appropriate:

- cloud accounts/projects;
- catalogs;
- schemas;
- buckets;
- credentials/identities;
- infrastructure;
- configuration.

A useful model is:

```text
DEV
 ├── dev account/project
 ├── dev catalog/schema
 ├── dev bucket
 └── dev identity

STAGING
 ├── staging account/project
 ├── staging catalog/schema
 ├── staging bucket
 └── staging identity

PROD
 ├── prod account/project
 ├── prod catalog/schema
 ├── prod bucket
 └── prod identity
```

The exact degree of isolation depends on cloud architecture and organizational requirements, but the security principle is constant:

> **A development mistake should have a limited blast radius.**

---

# 7. Why Shared Environments Are Dangerous

Consider:

```text
Developer
   ↓
Tests pipeline against shared production schema
   ↓
Writes test data
   ↓
Production dataset corrupted
```

The problem is not merely that the developer made a mistake.

The architecture allowed a low-trust activity to operate against a high-impact environment.

Isolation changes the failure mode:

```text
Developer
   ↓
Dev environment
   ↓
Test data
   ↓
Dev failure
```

The production blast radius is dramatically reduced.

---

# 8. Configuration Without Code Changes

A strong environment model follows:

```text
Same Code
+
Different Configuration
=
Different Environment
```

For example:

```text
config/
├── base
├── dev
├── staging
└── prod
```

Configuration can contain:

- bucket names;
- schemas;
- database endpoints;
- compute sizing;
- schedules;
- feature flags;
- resource limits.

The application should consume configuration rather than contain large amounts of environment-specific branching.

---

# 9. Never Hard-Code Environment Differences

A fragile pattern is:

```python
if environment == "prod":
    use_special_logic()
else:
    use_other_logic()
```

If this pattern spreads throughout a codebase, the application effectively becomes several different applications.

Problems include:

- complexity;
- testing difficulty;
- deployment risk;
- configuration drift;
- inconsistent behavior between environments.

Prefer configuration-driven behavior:

```python
config = load_config()

bucket = config.data_bucket
schema = config.analytics_schema
```

Then:

```text
DEV config
    → dev bucket/schema

STAGING config
    → staging bucket/schema

PROD config
    → prod bucket/schema
```

The code remains the same.

---

# 10. Artifact Promotion

This is the most important concept in this module.

The release flow is:

```text
Source Code
    ↓
Build
    ↓
Immutable Artifact
    ↓
DEV
    ↓
STAGING
    ↓
PROD
```

Possible artifacts include:

- Docker image;
- image digest;
- Python wheel;
- dbt package;
- DAG package/version;
- configuration bundle where appropriate.

The key principle:

> **Build once, promote the exact artifact.**

---

# 11. Why Rebuilding Per Environment Is Wrong

Bad:

```text
Build → Dev
Build → Staging
Build → Production
```

Good:

```text
Build once
   ↓
Artifact
   ↓
Dev
   ↓
Staging
   ↓
Production
```

Rebuilding introduces uncertainty:

- different dependency resolution;
- different build timestamps;
- different base images;
- different generated artifacts;
- potentially different source;
- difficult rollback;
- inability to prove that staging tested the same thing production received.

A production release should be traceable to the artifact that was actually validated.

---

# 12. Immutable Artifact Identity

An artifact needs an identity that allows operators to answer:

> **Exactly what did we deploy?**

For container images, a tag is useful:

```text
pipeline:4f2d8e...
```

But a digest is stronger:

```text
registry.example.com/pipeline@sha256:...
```

The promotion chain becomes:

```text
Git Commit
    ↓
Image
    ↓
Digest
    ↓
DEV
    ↓
STAGING
    ↓
PROD
```

Production should be able to identify the exact image that was tested.

---

# 13. Image Tags vs Image Digests

A tag such as:

```text
pipeline:release-2026-10
```

is a human-friendly reference.

A digest such as:

```text
pipeline@sha256:abcdef...
```

identifies image content immutably.

Therefore:

```text
Tag
 → convenient release label

Digest
 → exact content identity
```

A robust deployment record can store both:

```text
Release: 2026.10.05
Image tag: 4f2d8e...
Image digest: sha256:...
Git commit: 4f2d8e...
```

---

# 14. dbt Artifact Promotion

A dbt deployment should not accidentally use different project code in staging and production.

Relevant release artifacts can include:

- dbt project version;
- package version;
- manifest;
- state artifacts where appropriate;
- environment configuration.

The conceptual flow is:

```text
dbt source
   ↓
Validated release artifact
   ↓
DEV
   ↓
STAGING
   ↓
PROD
```

The environment can change its target database/schema/configuration while the logical release remains the same.

---

# 15. DAG Artifact Promotion

Airflow DAGs also need version identity.

The goal is not to re-teach DAG development.

The promotion concern is:

```text
DAG source
   ↓
Packaged/versioned artifact
   ↓
DEV
   ↓
STAGING
   ↓
PROD
```

The deployment record should identify:

- DAG version;
- artifact identifier;
- source commit;
- deployment time;
- environment.

This allows an incident responder to answer:

> Which DAG version was running when the incident began?

---

# 16. Deployment vs Promotion

These concepts are easy to confuse.

### Deployment

> Putting an artifact into an environment.

```text
Artifact → Environment
```

### Promotion

> Moving the same validated artifact to the next environment.

```text
Same Artifact → Next Environment
```

### Rebuild

> Producing a new artifact from source.

```text
Source → New Artifact
```

Memorize:

```text
Deployment:
artifact → environment

Promotion:
same artifact → next environment

Rebuild:
source → new artifact
```

---

# 17. End-to-End Deployment Workflow

A typical workflow is:

```text
Merge
  ↓
Deploy to DEV
  ↓
Run validation
  ↓
Promote SAME artifact
  ↓
STAGING
  ↓
Integration + shadow validation
  ↓
Approval
  ↓
PRODUCTION
```

The workflow builds on Topic 05.

Topic 05 answers:

> **Is the change valid enough to move forward?**

Topic 06 answers:

> **How do we safely move that validated artifact through environments?**

---

# 18. Conceptual GitHub Actions Deployment Workflow

Assume CI has already validated the artifact.

A conceptual deployment workflow can be structured as:

```yaml
name: Promote Data Platform

on:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  deploy-dev:
    runs-on: ubuntu-latest

    steps:
      - name: Deploy immutable artifact to dev
        run: |
          ./deploy.sh \
            --environment dev \
            --artifact-digest "${ARTIFACT_DIGEST}"

  validate-dev:
    needs: deploy-dev
    runs-on: ubuntu-latest

    steps:
      - name: Validate dev deployment
        run: ./validate.sh --environment dev

  deploy-staging:
    needs: validate-dev
    runs-on: ubuntu-latest

    steps:
      - name: Promote exact artifact to staging
        run: |
          ./deploy.sh \
            --environment staging \
            --artifact-digest "${ARTIFACT_DIGEST}"
```

The important property is not the shell script.

It is:

```text
ARTIFACT_DIGEST
```

being reused rather than rebuilding.

For production, use the repository's protected-environment approval mechanism.

---

# 19. Production Approvals

Production deployment should normally have stronger controls than development.

A conceptual gate:

```text
STAGING PASSES
      ↓
Production approval required
      ↓
Reviewer
      ↓
Approve
      ↓
Production deployment
```

Controls can include:

- protected environments;
- required reviewers;
- approval gates;
- separation of duties;
- auditability.

A production approval should be an explicit risk decision, not simply a button that says "continue."

---

# 20. Why Production Should Not Automatically Follow Every Merge

A merge proves that the change passed the repository's required quality gates.

It does not necessarily prove:

- the release window is appropriate;
- the migration is safe right now;
- downstream teams are ready;
- production traffic is normal;
- an incident is not already occurring;
- the operational team has approved the change.

Therefore:

```text
Merge
  ≠
Automatic production release
```

A controlled production gate provides a point where release risk can be assessed.

---

# 21. Promoting the Data Platform as a Whole

A data platform may contain:

- Docker images;
- Airflow DAGs;
- dbt jobs;
- database migrations;
- infrastructure.

These components have dependencies.

For example:

```text
Infrastructure
    ↓
Database compatibility
    ↓
Pipeline artifact
    ↓
DAGs
    ↓
dbt
    ↓
Validation
```

The exact order depends on architecture.

The important principle is:

> **Promotion must respect dependencies between platform components.**

---

# 22. Deployment Ordering

A common example is:

```text
1. Infrastructure
       ↓
2. Database compatibility changes
       ↓
3. Application/pipeline artifact
       ↓
4. DAGs
       ↓
5. dbt
       ↓
6. Validation
```

This is not a universal sequence.

For some platforms, DAG deployment may happen before a particular service deployment. For others, dbt migrations may be part of a release job.

The learner should reason from dependencies rather than memorizing a fixed order.

---

# 23. Database Migration Safety

Suppose the new pipeline expects:

```sql
SELECT new_column
FROM customers;
```

If the column does not exist yet, deployment fails.

A safer sequence may be:

```text
Add compatible schema
       ↓
Validate
       ↓
Deploy application/pipeline
       ↓
Start using new field
```

For example:

```sql
ALTER TABLE customers
ADD COLUMN new_column TEXT;
```

The important idea is that schema compatibility should exist before new code depends on it.

---

# 24. Backward-Compatible Database Changes

Prefer changes that allow old and new versions to coexist during deployment.

For example:

```text
Old application → old schema
New application → old + new schema
```

This enables rolling or staged deployments.

Dangerous pattern:

```text
Delete old column
   ↓
Deploy new code
```

If the old code is still running, it can fail.

The safer pattern is often:

```text
Expand
   ↓
Migrate
   ↓
Switch
   ↓
Contract
```

This is the expand-and-contract pattern discussed later in this module.

---

# 25. Non-Production Data

Non-production data must balance realism and privacy.

Approved approaches include:

### Synthetic data

Generated specifically for testing.

```text
Fake customer
Fake order
Fake event
```

### Sampled data

Small representative subsets.

### Masked production data

Production-like data where sensitive information has been protected.

The critical rule is:

> **Never copy raw personal data into development.**

---

# 26. Why Production Data in Development Is Dangerous

Consider:

```text
Production customer data
       ↓
Copied into dev
       ↓
Developer access
       ↓
Logs / notebooks / local files
       ↓
Privacy/security exposure
```

Potential consequences include:

- unauthorized access;
- accidental disclosure;
- sensitive values appearing in logs;
- local copies outside production controls;
- broader developer access than intended;
- regulatory or contractual consequences.

A staging environment can be realistic without being an unrestricted copy of production.

---

# 27. Data Realism vs Data Privacy

There is a real trade-off:

```text
More realistic data
        ↕
More privacy risk
```

Teams balance:

- realism;
- privacy;
- cost;
- reproducibility;
- test coverage.

For example:

```text
Dev:
synthetic data

Staging:
masked production-like data

Prod:
real production data
```

The appropriate strategy depends on the sensitivity and behavior being tested.

---

# 28. Branching Strategies

## Trunk-Based Development

Characteristics:

- short-lived branches;
- frequent integration;
- small changes.

Model:

```text
main
 ↑
small branch
 ↑
small change
```

This reduces long-lived divergence.

## Longer Release Branches

Characteristics:

- release stabilization;
- controlled release cycles;
- longer-lived release branches.

This can make sense when:

- release coordination is complex;
- multiple components require stabilization;
- regulated change processes require a release boundary.

Neither strategy is universally superior.

---

# 29. Semantic Versioning

Semantic Versioning uses:

```text
MAJOR.MINOR.PATCH
```

For example:

```text
1.4.2
```

Conceptually:

- **MAJOR** — breaking change;
- **MINOR** — backward-compatible functionality;
- **PATCH** — backward-compatible fix.

A breaking data contract or incompatible API may justify:

```text
1.x → 2.0.0
```

A small compatible bug fix may be:

```text
1.4.2 → 1.4.3
```

Versioning should be consistent with the actual artifact and release model.

---

# 30. Changelogs

A release should explain:

- what changed;
- why it changed;
- migration requirements;
- known risks;
- rollback notes.

Example:

```markdown
# Release 2.3.0

## Changes
- Added customer segmentation pipeline.
- Added new analytics output.

## Migration
- Adds `customer_segment` column.

## Risks
- Increased warehouse compute during first backfill.

## Rollback
- Redeploy image digest from 2.2.1.
- Retain new column until consumers are verified.

## Validation
- Staging integration passed.
- Shadow comparison passed.
```

A changelog is useful during both normal operations and incidents.

---

# 31. Shadow Runs

A shadow run executes the new version alongside the current version without allowing the new result to become authoritative.

```text
Production Inputs
       │
       ├──────────────→ Current Version
       │                      ↓
       │                 Current Output
       │
       └──────────────→ New Version
                              ↓
                         Shadow Output
```

Then compare the outputs.

The purpose is to discover behavior differences before switching authority.

---

# 32. What to Compare in a Shadow Run

Useful comparisons include:

- row counts;
- key-level results;
- aggregates;
- business metrics;
- null rates;
- distributions;
- expected differences.

For example:

```text
Current:
1,000,000 rows

New:
1,000,000 rows

Metric:
$4,210,500 vs $4,210,498
```

A two-dollar difference may be expected depending on the transformation.

The correct question is:

> **Is the difference expected and explainable?**

Not:

> **Are the outputs byte-for-byte identical?**

---

# 33. Expected vs Unexpected Differences

Use:

```text
Expected difference
        ↓
Document / approve

Unexpected difference
        ↓
Investigate / block
```

A shadow comparison should have defined acceptance criteria before the release begins.

For example:

```text
Row-count difference: 0%
Key mismatch: 0
Revenue difference: < 0.1%
Null-rate change: < defined threshold
```

The thresholds are domain-specific and should not be invented casually.

---

# 34. Staging Shadow Validation

A practical promotion flow:

```text
Current Version
      +
New Version
      ↓
Same Inputs
      ↓
Compare Gold Outputs
      ↓
Unexpected Difference?
    ├── Yes → Block promotion
    └── No  → Continue
```

This provides stronger evidence than unit tests alone because the comparison happens at a system/data-output level.

---

# 35. Shadow Tables and Backfills

Shadow tables can hold the output of the new implementation without replacing the authoritative dataset.

Conceptually:

```text
Input
  ├── Current pipeline → production table
  └── New pipeline     → shadow table
```

Then compare them.

Backfills can also be used to validate how a new transformation behaves over historical data before allowing it to overwrite an authoritative table.

These techniques connect to the transformation and backfill concepts established earlier in the roadmap.

---

# 36. Ephemeral Environments

An ephemeral environment is a temporary environment created for a specific change and destroyed afterward.

```text
Pull Request
     ↓
Ephemeral Environment
     ↓
Test
     ↓
Review
     ↓
PR merged/closed
     ↓
Destroy Environment
```

This is valuable because it reduces interference between changes.

---

# 37. Data Ephemeral Environments

Data Engineering can use mechanisms such as:

- warehouse zero-copy clones;
- table-format branches;
- table clones;
- temporary schemas.

These can provide isolated datasets without always performing a full physical data copy.

The exact mechanism depends on the warehouse or table technology.

---

# 38. Zero-Copy Clones

Conceptually, a zero-copy clone:

- creates an isolated logical view/copy of data;
- avoids immediately duplicating all physical data;
- allows experiments;
- reduces setup time/cost;
- protects the authoritative dataset.

The implementation is provider- and platform-specific.

The key mental model is:

```text
Production Dataset
       ↓
Logical Clone
       ↓
Isolated Test Environment
```

Do not assume all platforms implement clones identically.

---

# 39. Ephemeral Environment Lifecycle

A temporary environment should have an explicit lifecycle:

```text
Create
  ↓
Configure
  ↓
Deploy artifact
  ↓
Test
  ↓
Review
  ↓
Destroy
```

Cleanup is part of the design.

Otherwise:

```text
PR closed
   ↓
Environment remains
   ↓
Compute/storage continues
   ↓
Cost + security + clutter
```

---

# 40. Rollback Fundamentals

Rollback means:

> **Returning the system to a previously known-good state.**

But there are two distinct problems:

```text
Code rollback
vs
Data rollback
```

They are not equivalent.

---

# 41. Code Rollback

Code rollback is comparatively straightforward when artifacts are immutable.

Examples:

```text
Redeploy previous image digest
Redeploy previous DAG artifact
Restore previous dbt release artifact
```

The flow is:

```text
Bad Version
   ↓
Identify previous known-good artifact
   ↓
Redeploy
```

This is one of the strongest reasons to retain immutable artifact history.

---

# 42. Data Rollback

Data rollback is harder because the system may already have:

- written data;
- transformed data;
- propagated results downstream;
- triggered consumers;
- produced reports.

Consider:

```text
Version 42
   ↓
Bad transformation
   ↓
Wrong data written
   ↓
Code rolled back
   ↓
Wrong data still exists
```

Rolling back the code does not magically undo the data.

---

# 43. Data Rollback Scenario

Suppose a pipeline incorrectly calculates revenue.

```text
Bad pipeline
   ↓
Writes incorrect table
   ↓
Downstream dashboard reads it
   ↓
Code rollback
```

The code may now be correct while the table remains wrong.

Recovery may require:

```text
Code rollback
+
Data recovery
+
Downstream validation
```

This distinction is critical for Data Engineering.

---

# 44. Time Travel and Restore

Earlier lakehouse/table-format modules provide mechanisms such as:

- historical versions;
- time travel;
- restore;
- table recovery;
- backfills.

The conceptual recovery flow is:

```text
Detect bad state
      ↓
Identify last known-good version
      ↓
Restore/recover
      ↓
Validate restored data
      ↓
Validate downstream consumers
```

Recovery should never end at "restore completed."

The restored result must be validated.

---

# 45. Backfills as Recovery

Sometimes the correct recovery is not a direct restore.

For example:

```text
Bad partition
   ↓
Correct transformation
   ↓
Backfill affected partition
   ↓
Validate
```

Backfills are useful when the correct data can be deterministically recomputed.

The recovery strategy depends on whether:

- historical source data still exists;
- the transformation is deterministic;
- downstream systems have consumed the bad output;
- a table version can be restored safely.

---

# 46. Expand-and-Contract

Breaking schema changes should not normally be deployed as a single destructive change.

Example:

Existing:

```text
customer_name
```

New:

```text
first_name
last_name
```

Do not simply rename the field in one deployment.

Use:

```text
Phase 1 — EXPAND
Add new fields

Phase 2 — MIGRATE
Populate new fields

Phase 3 — DUAL READ/WRITE
Support old + new

Phase 4 — SWITCH
Consumers use new fields

Phase 5 — CONTRACT
Remove old field
```

This allows old and new versions to coexist during promotion.

---

# 47. Expand-and-Contract Across Environments

The same compatibility must survive:

```text
DEV
 ↓
STAGING
 ↓
PROD
```

For example:

### Phase 1

Add:

```text
first_name
last_name
```

while retaining:

```text
customer_name
```

### Phase 2

Backfill the new columns.

### Phase 3

Deploy code capable of reading both representations.

### Phase 4

Switch consumers.

### Phase 5

Remove the old representation only after all consumers have migrated.

This reduces deployment-order risk.

---

# 48. Feature Flags

Feature flags separate deployment from activation.

Example:

```text
feature.use_new_transform = false
```

The new code can be deployed without immediately enabling the new behavior.

Later:

```text
false → true
```

This reduces blast radius and makes controlled rollout possible.

For data systems, feature flags can control:

- new transformations;
- new output paths;
- new routing;
- new source selection;
- new calculation logic.

---

# 49. Progressive Data Rollout

Instead of switching the entire workload immediately:

```text
New pipeline
   ↓
Partition A
   ↓
Validate
   ↓
Partition B
   ↓
Validate
   ↓
Remaining data
```

This can also be expressed as:

```text
10%
 ↓
50%
 ↓
100%
```

The exact percentages are examples, not universal policy.

Progressive rollout is especially useful when a full replacement has a large blast radius.

---

# 50. Change Records

Every production change should identify:

- who deployed;
- what was deployed;
- when;
- which environment;
- artifact identifier;
- approval;
- relevant migration;
- validation result.

Example:

```yaml
release:
  version: "2.3.0"
  commit: "4f2d8e..."
  artifact_digest: "sha256:..."
  environment: "production"
  deployed_at: "2026-10-05T14:30:00Z"
  approved_by:
    - platform-reviewer
  migration: "2026_10_add_customer_segment"
  validation:
    staging: passed
    shadow: passed
```

This is an example structure; the actual deployment-record system may be a database, deployment platform, ticket, or release-management system.

---

# 51. Auditability

A production deployment should answer:

```text
Who?
What?
When?
Where?
Which artifact?
Which approval?
What validation?
```

Auditability matters for:

- debugging;
- governance;
- audits;
- incident response.

A useful relationship is:

```text
Git commit
   ↓
CI run
   ↓
Artifact
   ↓
Promotion
   ↓
Approval
   ↓
Deployment
   ↓
Validation
```

The chain should be reconstructable after the fact.

---

# 52. Promotion Checklist

Before production:

```text
[ ] CI passed
[ ] Artifact is immutable
[ ] Exact artifact identified
[ ] Dev validation passed
[ ] Staging validation passed
[ ] Shadow comparison passed where applicable
[ ] Migration reviewed
[ ] Infrastructure plan reviewed
[ ] Rollback plan ready
[ ] Data recovery plan ready
[ ] Production approval received
[ ] Deployment record created
```

A checklist is valuable because incident pressure makes people forget routine safety controls.

---

# 53. Rollback Runbook

A practical rollback runbook:

1. Detect the incident.
2. Stop further promotion.
3. Identify the affected artifact.
4. Determine blast radius.
5. Roll back code.
6. Assess data changes.
7. Restore or backfill data where required.
8. Validate downstream outputs.
9. Communicate status.
10. Record the incident.
11. Conduct a post-incident review.

The key distinction remains:

```text
Code recovery
+
Data recovery
=
Complete recovery
```

when both layers were affected.

---

# 54. Hands-On Exercise — Environment Configuration

Create conceptual environments:

```text
dev
staging
prod
```

Use separate configuration for:

```text
Terraform
catalogs/schemas
buckets
database endpoints
compute sizing
feature flags
```

Prove:

```text
Same application code
        +
different environment configuration
        ↓
different environment behavior
```

The learner should identify which values are configuration and which belong in code.

---

# 55. Hands-On Exercise — Promotion Workflow

Implement conceptually:

```text
Merge
 ↓
DEV deployment
 ↓
Tests
 ↓
STAGING deployment
 ↓
Integration + shadow comparison
 ↓
Manual approval
 ↓
PROD deployment
```

Use a SHA-tagged or digest-identified artifact.

### Acceptance test

Record:

```text
DEV artifact:
sha256:...

STAGING artifact:
sha256:...

PROD artifact:
sha256:...
```

They must identify the same artifact content.

If they differ, the promotion design has failed.

---

# 56. Hands-On Exercise — Deployment Order

Implement a release plan involving:

- infrastructure;
- migrations;
- pipeline artifacts;
- DAGs;
- dbt.

The learner must document:

```text
Step
Dependency
Validation
Failure action
Rollback action
```

Example:

| Step | Dependency | Validation |
|---|---|---|
| Infrastructure | None/plan | Terraform validation |
| Schema expansion | Infrastructure | Migration check |
| Pipeline artifact | Compatible schema | Smoke test |
| DAGs | Pipeline available | DAG validation |
| dbt | Required models/services | dbt validation |
| Release validation | All above | End-to-end checks |

The exact order must be adapted to the platform.

---

# 57. Hands-On Exercise — Ephemeral Environment

Create a temporary environment per pull request.

Use one or more mechanisms:

- warehouse zero-copy clone;
- table-format branch/clone;
- temporary schema.

Required lifecycle:

```text
PR opened
   ↓
Environment created
   ↓
Artifact deployed
   ↓
Tests run
   ↓
Review
   ↓
PR closed
   ↓
Environment destroyed
```

Verify that cleanup occurs even when tests fail.

---

# 58. Hands-On Exercise — Shadow Comparison

In staging:

```text
Current version
      +
New version
      ↓
Same inputs
      ↓
Compare gold outputs
```

Implement comparison logic for:

- row counts;
- keys;
- aggregates;
- important metrics.

Require unexpected differences to block promotion.

Document the acceptance thresholds before running the comparison.

---

# 59. Hands-On Exercise — Rollback Drill

Follow this sequence:

1. Deploy a deliberately bad version to staging.
2. Identify the failure.
3. Roll back the code.
4. Restore the affected table using time travel or an equivalent mechanism.
5. Validate the restored result.
6. Record the time taken.

The learner must prove recovery of both:

```text
code
+
data
```

This is a critical distinction from ordinary application deployment practice.

---

# 60. Production Failure Scenarios

## Scenario 1 — Different Image Built for Production

```text
Dev image
   ↓
Staging image
   ↓
New production build
```

### Problem

Production did not receive the artifact that staging validated.

### Prevention

Promote the exact image digest.

---

## Scenario 2 — Staging Has Unrealistic Data

### Problem

The new pipeline passes staging but behaves incorrectly on production distributions.

### Prevention

Use appropriately realistic, privacy-safe data and shadow validation where useful.

---

## Scenario 3 — Production Personal Data Copied to Dev

### Problem

Sensitive data becomes accessible outside its controlled environment.

### Prevention

Use synthetic, sampled, or properly masked data.

---

## Scenario 4 — Manual Production Deployment

### Problem

The deployment may not be reproducible or auditable.

### Prevention

Use automated deployment from an immutable artifact with controlled approval.

---

## Scenario 5 — Code Rollback Without Data Rollback

### Problem

The code is restored, but incorrect data remains.

### Prevention

Maintain explicit data-recovery procedures.

---

## Scenario 6 — Breaking Schema Migration

### Problem

Old and new application versions cannot coexist.

### Prevention

Use expand-and-contract.

---

## Scenario 7 — Shadow Output Mismatch

### Problem

The new version produces unexpected results.

### Prevention

Define comparison criteria and block promotion when material differences are unexplained.

---

## Scenario 8 — Ephemeral Environment Leaks Resources

### Problem

Temporary infrastructure survives after the PR closes.

### Prevention

Automate cleanup and monitor orphaned resources.

---

# 61. Debugging and Incident Response

Use this pattern for every promotion failure:

```text
Symptom
   ↓
Likely cause
   ↓
Investigation
   ↓
Remediation
   ↓
Prevention
```

---

## Dev Deployment Fails

Inspect:

```text
artifact identity
environment configuration
credentials
infrastructure
deployment logs
```

Do not immediately rebuild the artifact.

---

## Staging Deployment Fails

Determine whether:

- the artifact is wrong;
- staging configuration is wrong;
- staging infrastructure differs unexpectedly;
- a migration was incomplete;
- a dependency is unavailable.

---

## Production Approval Missing

Check:

- protected environment configuration;
- required reviewers;
- approval status;
- workflow/environment mapping.

---

## Wrong Artifact Deployed

Compare:

```text
Expected digest
vs
Actual digest
```

Then inspect the promotion workflow for any rebuild step.

---

## Artifact Digest Mismatch

A digest mismatch is a serious release-control signal.

Possible causes:

- wrong registry reference;
- mutable tag resolved to different content;
- artifact was rebuilt;
- deployment referenced the wrong digest.

---

## Environment Configuration Incorrect

Compare configuration sources:

```text
expected environment config
vs
actual environment config
```

Do not solve a configuration error by editing application code.

---

## Migration Fails

Determine:

- whether the migration was partially applied;
- whether old consumers still exist;
- whether the schema is in a compatible state;
- whether rollback is safe.

---

## Shadow Comparison Differs

Classify the difference:

```text
Expected
vs
Unexpected
```

Then inspect the exact records/metrics responsible.

---

## Data Rollback Required

First determine:

```text
What data changed?
When?
Which version caused it?
Which downstream systems consumed it?
```

Then select:

```text
restore
or
backfill
or
both
```

---

## Ephemeral Environment Not Destroyed

Inspect:

- lifecycle hooks;
- failure paths;
- cleanup permissions;
- resource ownership tags;
- orphan detection.

Cleanup must happen even when tests fail.

---

## Feature Flag Behaves Incorrectly

Check:

```text
flag value
environment
scope
evaluation timing
configuration source
```

Ensure that production did not inherit an unintended development value.

---

## Rollback Does Not Restore Data

This usually means code rollback was treated as complete recovery.

Return to:

```text
Code rollback
+
Data recovery
+
Downstream validation
```

---

# 62. Common Mistakes

## Mistake 1 — Rebuilding Images Per Environment

This breaks artifact identity.

**Correct:**

```text
Build once
→ promote digest
```

---

## Mistake 2 — Staging Has No Realistic Data

A system may pass tests that do not represent production behavior.

**Correct:**

Use privacy-safe realistic data where required.

---

## Mistake 3 — Copying Production Personal Data into Development

This creates unnecessary privacy and security risk.

**Correct:**

Use synthetic, sampled, or masked data.

---

## Mistake 4 — Rollback Plans Ignore Data

Code rollback does not reverse historical data writes.

**Correct:**

Maintain data recovery procedures.

---

## Mistake 5 — Manual Production Deployments

Manual steps create drift and reduce auditability.

**Correct:**

Automate deployment from an immutable artifact with controlled approval.

---

# 63. Environment Promotion Architecture

```text
                         Git Repository
                              │
                              ▼
                          Commit / PR
                              │
                              ▼
                              CI
                              │
                              ▼
                       Immutable Artifact
                              │
                              ▼
                     ┌─────────────────┐
                     │       DEV       │
                     │                 │
                     │ Deploy          │
                     │ Test            │
                     └────────┬────────┘
                              │
                         Validation
                              │
                              ▼
                     ┌─────────────────┐
                     │     STAGING     │
                     │                 │
                     │ Same Artifact   │
                     │ Integration     │
                     │ Shadow          │
                     └────────┬────────┘
                              │
                           Approval
                              │
                              ▼
                     ┌─────────────────┐
                     │      PROD       │
                     │                 │
                     │ Same Artifact   │
                     │ Controlled      │
                     │ Deployment      │
                     └─────────────────┘
```

Every transition should preserve artifact identity.

---

# 64. Production Readiness

Evidence before production should include:

```text
CI passed
Dev passed
Staging passed
Shadow comparison passed where applicable
Migrations reviewed
Infrastructure reviewed
Artifact identity known
Rollback plan ready
Data recovery plan ready
Approval recorded
```

A production deployment is a controlled decision supported by evidence.

---

# 65. Knowledge Checkpoints

## Explain

1. Why do we need dev/staging/prod?
2. Why must environments be isolated?
3. Why should artifacts not be rebuilt?
4. Why is staging necessary?
5. Why is data rollback harder than code rollback?

## Predict

Given:

```text
CI
 ↓
Dev
 ↓
Staging
 ↓
Approval
 ↓
Prod
```

Question:

> What should happen if staging shadow validation fails?

Expected reasoning:

```text
Do not promote
   ↓
Investigate
   ↓
Fix or abandon release
   ↓
Produce new artifact if code changes
   ↓
Repeat validation
```

---

## Diagnose

Scenario:

```text
Staging:
image@sha256:AAA

Production:
image@sha256:BBB
```

Question:

> What went wrong?

The production artifact differs from the validated staging artifact.

---

## Design

> Design a promotion strategy for a platform containing Airflow, dbt, Spark, Kafka, Terraform, and object storage.

A strong design should cover:

```text
artifact identity
environment isolation
configuration
deployment order
staging validation
approval
rollback
data recovery
auditability
```

---

# 66. Senior Data Engineer Interview Questions

## Fundamentals

### What is environment promotion?

Moving a validated artifact through controlled environments such as dev, staging, and production.

### Why use dev/staging/prod?

To isolate risk, validate realistically, and protect production.

### What is environment isolation?

Separating environments so that data, credentials, infrastructure, and changes have controlled blast radii.

### What is a configuration overlay?

Environment-specific configuration applied to the same application code.

---

## Intermediate

### Why promote artifacts instead of rebuilding?

Because rebuilding can produce a different dependency graph, image, or generated output. Promotion preserves what was actually tested.

### What is an immutable artifact?

An artifact whose content can be identified reliably and is not silently replaced.

### Why use image digests?

A digest identifies exact image content, making deployment traceable and reproducible.

### How do you deploy database migrations safely?

Prefer backward-compatible changes and coordinate schema compatibility with application/pipeline deployment.

### How do you handle non-production data?

Use synthetic, sampled, or properly masked data rather than raw personal production data.

### Trunk-based vs release branches?

Trunk-based development favors small frequent integrations; release branches can provide controlled stabilization boundaries. The correct choice depends on the organization and release model.

---

## Advanced

### How do you validate data changes using shadow runs?

Run the new implementation alongside the current implementation against the same inputs, compare authoritative outputs/metrics, and block promotion when unexplained differences exceed agreed criteria.

### What is an ephemeral environment?

A temporary isolated environment created for a change and destroyed after validation.

### What is a zero-copy clone?

A platform-specific mechanism for creating an isolated logical copy/clone without immediately duplicating all underlying physical data.

### Why is code rollback easier than data rollback?

Code can often be redeployed from a previous artifact; data may already have been written, consumed, propagated, or transformed downstream.

### What is expand-and-contract?

A schema evolution pattern that expands compatibility first, migrates consumers/data, switches behavior, then removes obsolete fields.

### How do feature flags support progressive rollout?

They allow code to be deployed without immediately activating new behavior and can enable controlled expansion of the affected workload.

### How do you design a data rollback strategy?

Combine immutable artifact rollback with table restore/time travel/backfill mechanisms and downstream validation.

### How do you make deployment auditable?

Record who, what, when, where, artifact identity, approval, migration, and validation results.

---

## Architecture

Design:

> A production promotion pipeline for a data platform with Python pipelines, Airflow, dbt, Spark, Kafka, Terraform, object storage, and a warehouse.

A strong architecture should contain:

```text
Git
 ↓
CI
 ↓
Immutable Artifact
 ↓
DEV
 ↓
Validation
 ↓
STAGING
 ↓
Integration / Shadow
 ↓
Approval
 ↓
PROD
 ↓
Monitoring / Validation
 ↓
Rollback / Recovery if needed
```

---

# 67. Final Capstone — Production Data Platform Promotion System

Build:

```text
                         Git
                          │
                          ▼
                         CI
                          │
                          ▼
                  Immutable Artifact
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
                DEV          Artifact Registry
                 │                 │
             Validation            │
                 │                 │
                 ▼                 │
              STAGING ◄────────────┘
                 │
          Integration Tests
                 │
          Shadow Comparison
                 │
              Approval
                 │
                 ▼
                PROD
                 │
          Monitoring/Validation
                 │
           Rollback if needed
```

The capstone must include:

- dev;
- staging;
- prod;
- environment-specific configuration;
- immutable artifact;
- deployment workflow;
- approval gate;
- migration ordering;
- ephemeral environment;
- shadow comparison;
- rollback;
- data recovery;
- audit record.

---

# 68. Capstone Acceptance Criteria

The learner must prove:

- the same artifact reaches dev, staging, and production;
- environments are isolated;
- environment configuration does not require code changes;
- production requires approval;
- migrations are ordered correctly;
- non-production data does not expose raw personal information;
- staging performs meaningful validation;
- shadow comparison can block promotion;
- ephemeral environments can be created and destroyed;
- code rollback works;
- data rollback works;
- schema changes use expand-and-contract when required;
- progressive rollout can reduce blast radius;
- every production deployment is auditable.

---

# 69. Production Incident Drills

## Drill 1 — New Image Fails in Staging

```text
Detect
→ Contain
→ Diagnose
→ Decide
→ Rollback/Recover
→ Validate
→ Record
```

Determine whether the problem is:

- artifact;
- configuration;
- dependency;
- infrastructure;
- data.

---

## Drill 2 — Different Image Digests

```text
Staging: sha256:AAA
Prod:    sha256:BBB
```

Stop the release and determine why the promotion process did not preserve artifact identity.

---

## Drill 3 — Migration Breaks Consumer

Determine:

```text
Which schema changed?
Which consumers were active?
Was the change backward-compatible?
Can the migration be reversed safely?
```

---

## Drill 4 — Shadow Outputs Differ

Determine:

```text
Expected difference?
Unexpected difference?
Threshold exceeded?
```

Block promotion until the difference is understood.

---

## Drill 5 — Bad Transformation Writes Production Data

Determine:

```text
Affected partitions/tables
Source version
Time window
Downstream consumers
Recovery method
```

---

## Drill 6 — Code Rollback Succeeds but Data Is Corrupted

Demonstrate why:

```text
code rollback ≠ data recovery
```

Then execute the data recovery procedure.

---

## Drill 7 — Ephemeral Environment Remains

Identify the orphaned resources and determine why cleanup did not run.

---

## Drill 8 — Feature Rollout Causes Abnormal Results

Disable or reduce the rollout, validate the current state, and determine whether data recovery is required.

---

# 70. Final Assessment

```text
[ ] I understand why dev/staging/prod environments exist.
[ ] I understand environment isolation.
[ ] I can separate accounts/projects.
[ ] I can separate catalogs/schemas.
[ ] I can separate buckets.
[ ] I understand environment-specific credentials.
[ ] I understand configuration overlays.
[ ] I can deploy without changing application code per environment.
[ ] I understand immutable artifacts.
[ ] I can promote the same artifact.
[ ] I understand image digests.
[ ] I can promote dbt artifacts.
[ ] I can promote DAG versions.
[ ] I understand deployment ordering.
[ ] I understand database migration ordering.
[ ] I understand synthetic data.
[ ] I understand sampled data.
[ ] I understand masked production data.
[ ] I understand why raw personal data must not be copied to dev.
[ ] I understand trunk-based development.
[ ] I understand release branches.
[ ] I understand semantic versioning.
[ ] I understand changelogs.
[ ] I understand shadow runs.
[ ] I can compare shadow outputs.
[ ] I understand ephemeral environments.
[ ] I understand zero-copy clones.
[ ] I understand temporary schemas.
[ ] I understand code rollback.
[ ] I understand data rollback.
[ ] I understand time travel/restore.
[ ] I understand backfills.
[ ] I understand expand-and-contract.
[ ] I understand feature flags.
[ ] I understand progressive rollout.
[ ] I understand change records.
[ ] I understand auditability.
[ ] I can write a promotion checklist.
[ ] I can write a rollback runbook.
[ ] I can perform a rollback drill.
[ ] I can design a production promotion architecture.
```

---

# 71. Connection to Other Modules

Keep the boundaries clear.

## Topic 05 — CI Pipelines

Topic 05 provides:

- automated validation;
- tests;
- image builds;
- image scanning;
- Terraform plans.

Topic 06 uses those results as evidence for promotion.

## Topic 04 — Terraform

Topic 04 provides:

- infrastructure as code;
- environment infrastructure;
- plans;
- safe infrastructure changes.

Topic 06 uses Terraform configurations as part of environment deployment.

## Topic 07 — Cloud Secrets Managers

Topic 07 provides:

- production secrets management;
- runtime secret delivery;
- rotation;
- credential protection.

Topic 06 only establishes that each environment must have appropriately isolated credentials.

## Module 2.15 — Lakehouse Table Formats

Provides:

- time travel;
- table clones;
- branches;
- data recovery mechanisms.

Topic 06 uses those mechanisms for promotion, testing, and recovery.

## Module 2.12

Provides:

- configuration-driven pipelines;
- backfills;
- shadow tables;
- transformation patterns.

## Module 2.7

Provides:

- database migrations;
- schema evolution.

## Module 2.11

Provides:

- contracts;
- schema compatibility.

Do not re-teach these modules.

---

# 72. Production Promotion Master Model

The complete mental model is:

```text
                    SOURCE
                      │
                      ▼
                 BUILD ONCE
                      │
                      ▼
             IMMUTABLE ARTIFACT
                      │
                      ▼
                    DEV
                      │
              Automated Validation
                      │
                      ▼
                  STAGING
                      │
        Integration + Shadow Validation
                      │
                      ▼
                 APPROVAL
                      │
                      ▼
                    PROD
                      │
             Controlled Rollout
                      │
                      ▼
             Monitor / Validate
                      │
             ┌────────┴────────┐
             │                 │
           Healthy          Failure
             │                 │
             ▼                 ▼
          Continue        Rollback/Recover
                               │
                         ┌─────┴─────┐
                         ▼           ▼
                       Code        Data
                      Rollback    Recovery
```

The core operational rule is:

> **The artifact promoted to production must be the same artifact that was validated in earlier environments.**

---

# 73. Predict → Execute → Inspect → Measure → Decide

Use this cycle throughout practical work:

```text
PREDICT
What should happen?

     ↓

EXECUTE
Run the deployment/promotion.

     ↓

INSPECT
Check artifact identity, logs,
environment state, and outputs.

     ↓

MEASURE
Check validation results and deployment time.

     ↓

DECIDE
Promote, stop, or rollback.
```

This makes promotion an engineering discipline rather than a sequence of manual clicks.

---

# 74. Final Roadmap Coverage Audit

```text
[ ] Separate environments
[ ] Safe experimentation
[ ] Realistic staging validation
[ ] Protected production
[ ] Environment isolation
[ ] Separate cloud accounts/projects
[ ] Separate catalogs/schemas
[ ] Separate buckets
[ ] Separate credentials
[ ] Configuration overlays
[ ] Promote artifacts, don't rebuild
[ ] Image digest
[ ] dbt package/artifact
[ ] DAG version
[ ] Deployment workflow
[ ] Dev automatic deployment
[ ] Staging after validation
[ ] Production approval
[ ] Protected environments
[ ] Images deployment
[ ] DAG deployment
[ ] dbt deployment
[ ] Database migrations
[ ] Infrastructure applies
[ ] Deployment ordering
[ ] Synthetic data
[ ] Sampled data
[ ] Masked production data
[ ] No raw personal data in dev
[ ] Trunk-based development
[ ] Release branches
[ ] Semantic versioning
[ ] Changelogs
[ ] Shadow runs
[ ] Shadow comparison
[ ] Shadow tables
[ ] Backfills
[ ] Ephemeral environments
[ ] Zero-copy clones
[ ] Table-format branches/clones
[ ] Temporary schemas
[ ] Ephemeral cleanup
[ ] Code rollback
[ ] Data rollback
[ ] Time travel
[ ] Restore
[ ] Backfills
[ ] Expand-and-contract
[ ] Feature flags
[ ] Progressive rollout
[ ] Change records
[ ] Auditability
[ ] Promotion checklist
[ ] Rollback runbook
[ ] Environment configuration lab
[ ] Promotion workflow lab
[ ] Deployment-order lab
[ ] Ephemeral-environment lab
[ ] Shadow-comparison lab
[ ] Rollback drill
[ ] Production incident drills
[ ] Debugging guide
[ ] Common mistakes
[ ] Knowledge checkpoints
[ ] Interview questions
[ ] Capstone
[ ] Final assessment
```

---

# 75. Module Completion Standard

You have mastered this topic when you can independently design and explain:

```text
Developer Change
      ↓
CI Validation
      ↓
Immutable Artifact
      ↓
DEV
      ↓
Environment Validation
      ↓
STAGING
      ↓
Integration + Shadow Validation
      ↓
Production Approval
      ↓
PROD
      ↓
Controlled Rollout
      ↓
Monitoring
      ↓
Rollback / Data Recovery if needed
```

You should be able to answer:

> **What exact artifact is being promoted?**

> **Was that exact artifact tested?**

> **How is each environment isolated?**

> **What configuration changes between environments?**

> **What happens if the schema migration fails?**

> **How do we validate production-like behavior without exposing raw personal data?**

> **How do we know whether a shadow difference is acceptable?**

> **How do we recover code?**

> **How do we recover data?**

> **How do we prove who approved and deployed the release?**

That is the difference between knowing how to deploy software and understanding **production-grade environment promotion for Data Engineering**.
