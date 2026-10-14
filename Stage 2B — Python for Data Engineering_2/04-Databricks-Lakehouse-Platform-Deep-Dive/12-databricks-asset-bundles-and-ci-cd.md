# 12 --- Databricks Asset Bundles and CI/CD

> **G4 --- Databricks Lakehouse Platform Deep Dive**\
> **Topic 12 --- Databricks Asset Bundles and CI/CD**\
> **Level:** Beginner → Intermediate → Advanced → Production

> **Terminology note:** Databricks documentation currently uses
> **Declarative Automation Bundles** for what was previously called
> **Databricks Asset Bundles**. This module uses "Asset Bundles" when
> referring to the roadmap terminology and "Declarative Automation
> Bundles" when discussing current product behavior.

## 1. Module Purpose

Everything built manually in a Databricks workspace eventually creates
an engineering problem:

``` text
Who changed it?
Why was it changed?
Can we reproduce it?
Can we review it?
Can we test it?
Can we promote it?
Can we roll it back?
Can we prove what version is running?
```

Asset Bundles solve part of this problem by representing a Databricks
project as source-controlled configuration, source files, artifacts, and
resource definitions that can be validated and deployed
programmatically.

The broader production system is:

``` text
Git
 +
Code
 +
Configuration
 +
Resources
 +
Testing
 +
Identity
 +
CI/CD
 +
Environment Promotion
 +
Rollback
 =
Production Delivery System
```

The learner should finish this module able to answer:

> **How do I take Databricks jobs, pipelines, Python code,
> configuration, and environment-specific settings and turn them into a
> reproducible, reviewable, testable, secure, multi-environment
> deployment system?**

------------------------------------------------------------------------

# 2. Why Topic 12 Follows Topics 09--11

The G4 progression is deliberate:

``` text
01 Architecture
 ↓
02 Compute
 ↓
03 Code Organisation
 ↓
04 Governance
 ↓
05 Ingestion
 ↓
06 Managed Ingestion
 ↓
07 Declarative Pipelines
 ↓
08 Jobs
 ↓
09 Performance
 ↓
10 Analytics
 ↓
11 Sharing
 ↓
12 Delivery / CI-CD
 ↓
13 Cost
 ↓
14 ML Handoff
```

By Topic 12 the learner has already built:

-   governed data;
-   ingestion;
-   pipelines;
-   jobs;
-   optimized workloads;
-   analytics;
-   shared data products.

Now those assets must become **deployable software**.

This is the Databricks application of the broader Data Engineering CI/CD
principles introduced earlier in the roadmap, especially Module 2.18.

------------------------------------------------------------------------

# 3. Teaching Progression

Every major concept in this module follows:

``` text
What is it?
↓
Why does it exist?
↓
How does it work?
↓
What are the components?
↓
How is it configured?
↓
How is it deployed?
↓
How is it tested?
↓
How is it secured?
↓
How can it fail?
↓
How do I troubleshoot it?
↓
How do I roll it back?
↓
What does it cost?
↓
When should I use it?
↓
When should I NOT use it?
↓
What is the production best practice?
```

The module intentionally moves from manual workspace behavior to
production delivery engineering.

------------------------------------------------------------------------

# 4. Start With the Problem: Manual Deployment

A beginner often starts here:

``` text
Developer
   ↓
Databricks UI
   ↓
Create Job
   ↓
Create Pipeline
   ↓
Configure Schedule
   ↓
Change Permissions
   ↓
Repeat for Staging
   ↓
Repeat for Production
```

This works for experimentation.

It becomes dangerous at production scale.

## 4.1 Problems With Manual Deployment

### Configuration drift

Dev and production silently become different.

### Undocumented changes

A workspace setting may exist without an equivalent Git change.

### Human error

A developer can accidentally:

-   enable a production schedule;
-   point dev to a production catalog;
-   grant excessive permissions;
-   select expensive compute;
-   deploy the wrong notebook;
-   change a production job manually.

### Poor reproducibility

Another engineer cannot reliably recreate the same environment.

### Difficult rollback

You may know that something changed but not exactly what configuration
existed before.

### Weak review

Production configuration changes may bypass pull-request review.

### Weak auditability

You may know the current state but not the intended source-controlled
state.

### Disaster-recovery risk

A workspace can contain critical configuration that is not represented
as code.

------------------------------------------------------------------------

# 5. The Desired Model

Instead:

``` text
Git Repository
      ↓
Code + Configuration
      ↓
Asset Bundle
      ↓
Validate
      ↓
Unit Tests
      ↓
Deploy Dev
      ↓
Integration Tests
      ↓
Staging
      ↓
Approval
      ↓
Production
```

The workspace becomes a **deployment target**, not the primary source of
truth.

Mental model:

> **Git is the source of truth; the workspace is a deployment target.**

------------------------------------------------------------------------

# 6. Infrastructure as Code and Configuration as Code

Before Asset Bundles, understand the broader idea.

## Infrastructure as Code

Infrastructure is described through source files rather than created
exclusively through a GUI.

Conceptually:

``` text
Desired State
     ↓
Code
     ↓
Tool
     ↓
Infrastructure
```

## Configuration as Code

Application/workload configuration is also version controlled.

For Data Engineering:

``` text
Job
 ├── tasks
 ├── schedule
 ├── compute
 ├── parameters
 └── permissions
```

can become source-controlled configuration.

## 6.1 Declarative Configuration

Declarative means:

> Describe what the desired state should be rather than manually
> performing every individual operation.

Example:

``` yaml
resources:
  jobs:
    daily_ingestion:
      name: daily_ingestion
```

The deployment system reconciles the configuration with the target
environment.

## 6.2 Reproducibility

If two environments are represented by the same code plus explicit
target configuration:

``` text
Same Application
+
Different Target Configuration
=
Controlled Environment Difference
```

## 6.3 Idempotency

A production deployment should be safe to repeat when the intended state
has not changed.

This does **not** mean every deployment is risk-free.

It means the deployment process should converge toward the declared
configuration rather than depend on an undocumented sequence of manual
clicks.

## 6.4 Drift

Drift occurs when:

``` text
Git Desired State
        ≠
Workspace Actual State
```

Example:

``` text
Git:
schedule = 02:00

Workspace:
schedule = 01:00
```

Manual edits are a common source.

------------------------------------------------------------------------

# 7. What Is a Databricks Asset Bundle?

A bundle is the deployable representation of a Databricks project.

Current Databricks documentation describes Declarative Automation
Bundles as a way to apply software-engineering practices such as source
control, code review, testing and CI/CD to Databricks data and AI
projects.

A bundle can include:

-   source files;
-   configuration;
-   resource definitions;
-   jobs;
-   pipelines;
-   artifacts;
-   environment targets;
-   workspace settings;
-   tests;
-   deployment metadata.

Mental model:

``` text
                    Asset Bundle
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
          Source      Resources    Config
           Code       Jobs/Pipes   Targets
             │           │           │
             └───────────┼───────────┘
                         ↓
                      Validate
                         ↓
                       Deploy
                         ↓
                  Databricks Target
```

The important idea is:

> **A bundle is a project-level delivery mechanism, not merely a YAML
> file.**

------------------------------------------------------------------------

# 8. Asset Bundle Project Structure

A professional project can look like:

``` text
databricks_lab/
├── databricks.yml
├── resources/
│   ├── ingestion.job.yml
│   ├── pipeline.pipeline.yml
│   └── quality.job.yml
├── src/
│   └── data_platform/
│       ├── __init__.py
│       ├── main.py
│       └── transforms.py
├── pipelines/
├── notebooks/
├── sql/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── pyproject.toml
└── README.md
```

Current Databricks examples commonly separate `databricks.yml`,
resources, source code and tests.

## Directory Responsibilities

  Directory          Responsibility
  ------------------ -----------------------------------------------
  `databricks.yml`   Root bundle configuration
  `resources/`       Resource definitions
  `src/`             Production Python source
  `tests/`           Unit/integration tests
  `notebooks/`       Notebook-oriented development or entry points
  `sql/`             SQL assets
  `pipelines/`       Pipeline-specific source/config where used
  `docs/`            Architecture/runbooks/decisions
  `pyproject.toml`   Python packaging/dependencies

The exact structure may vary by organization.

------------------------------------------------------------------------

# 9. `databricks.yml`

A bundle contains one root `databricks.yml`.

Current documentation describes it as the main configuration file. It
can include or reference additional YAML files.

A minimal conceptual example:

``` yaml
bundle:
  name: data-platform

include:
  - resources/*.yml

variables:
  catalog:
    default: dev_catalog

targets:
  dev:
    mode: development

  prod:
    mode: production
```

A production project can split resource definitions into separate files:

``` text
databricks.yml
resources/
├── ingestion.job.yml
├── pipeline.pipeline.yml
└── quality.job.yml
```

## Why Split Configuration?

Large single YAML files become difficult to review.

Splitting allows:

``` text
Root configuration
+
Resource-specific configuration
+
Target configuration
```

while still producing one deployable bundle.

------------------------------------------------------------------------

# 10. Bundle Targets

A target represents a deployment environment.

Typical targets:

``` text
dev
staging
prod
```

Mental model:

``` text
                    Same Code
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
         dev        staging        prod
          │            │            │
      low-risk      controlled   protected
      testing       validation   deployment
```

Current bundle configuration supports target-level settings and a target
can be marked as the default target.

Example:

``` yaml
targets:
  dev:
    default: true

  staging:
    workspace:
      host: https://staging-workspace.example

  prod:
    workspace:
      host: https://production-workspace.example
```

Do not copy this example blindly. Workspace hosts, variables,
permissions and resource overrides are environment-specific.

------------------------------------------------------------------------

# 11. Development, Staging, Production

## Development

Characteristics:

-   individual development;
-   small datasets;
-   inexpensive compute;
-   fast iteration;
-   developer-oriented permissions;
-   schedules generally paused;
-   development-mode behavior.

## Staging

Characteristics:

-   integration testing;
-   realistic configuration;
-   representative small/controlled datasets;
-   controlled identity;
-   production-like deployment path.

## Production

Characteristics:

-   stable configuration;
-   controlled identity;
-   protected deployment;
-   production data;
-   approved schedules;
-   monitored workloads;
-   stricter permissions.

Production progression:

``` text
Dev
 ↓
Unit Test
 ↓
Integration Test
 ↓
Staging
 ↓
Approval
 ↓
Production
```

Never use production as the first environment in which a pipeline is
tested.

------------------------------------------------------------------------

# 12. Development Mode

Current Databricks deployment modes provide optional default behaviors
for development and production targets.

A development target is conceptually:

``` yaml
targets:
  dev:
    mode: development
```

Current development-mode behavior can include:

-   resource name prefixes based on the current user for applicable
    resources;
-   `dev` tagging for jobs and pipelines;
-   pipeline development behavior;
-   development-oriented compute overrides.

Some behaviors can be customized with presets.

Important:

> Do not memorize a particular generated name. Understand the behavior
> and verify the current version.

Development mode exists to make individual development safer.

------------------------------------------------------------------------

# 13. Production Mode

A production target can be declared as:

``` yaml
targets:
  prod:
    mode: production
```

Current production-mode behavior includes stronger validation and
production-oriented deployment behavior.

Databricks documentation recommends service principals for production
deployments.

A production target should conceptually enforce:

``` text
Stable identity
+
Protected branch
+
Controlled permissions
+
Production catalog
+
Production schedule
+
Production monitoring
```

A developer's personal identity should not become the permanent
production runtime identity.

------------------------------------------------------------------------

# 14. Developer Identity vs Deployment Identity vs Runtime Identity

These are different concepts:

``` text
Developer
   ≠
CI Deployment Identity
   ≠
Production Runtime Identity
```

### Developer

Writes and reviews code.

### CI deployment identity

Authenticates the automation system that deploys the bundle.

### Runtime identity

The identity under which production jobs/pipelines execute.

Separating them improves:

-   least privilege;
-   auditability;
-   ownership;
-   credential lifecycle;
-   incident response.

------------------------------------------------------------------------

# 15. Bundle CLI Workflow

The roadmap requires these commands:

``` bash
databricks bundle validate
databricks bundle deploy
databricks bundle run
databricks bundle destroy
```

## 15.1 Validate

``` bash
databricks bundle validate
```

Purpose:

-   parse configuration;
-   validate resource definitions;
-   detect invalid configuration before deployment.

Validation is necessary but not sufficient.

``` text
Bundle validation
≠
Unit testing
≠
Integration testing
≠
Data validation
```

## 15.2 Deploy

``` bash
databricks bundle deploy -t dev
```

Purpose:

> Apply the bundle to the selected target workspace.

## 15.3 Run

``` bash
databricks bundle run -t dev ingestion_job
```

Purpose:

> Run a deployed bundle resource where the resource supports bundle
> execution.

## 15.4 Destroy

``` bash
databricks bundle destroy -t dev
```

Purpose:

> Remove bundle-managed resources from the target according to bundle
> lifecycle behavior.

Treat destroy as destructive.

Never experiment with destructive commands against production.

------------------------------------------------------------------------

# 16. Bundle Lifecycle

``` text
Create
  ↓
Develop
  ↓
Validate
  ↓
Test
  ↓
Deploy Dev
  ↓
Run Integration Tests
  ↓
Review
  ↓
Deploy Staging
  ↓
Approve
  ↓
Deploy Production
  ↓
Observe
  ↓
Rollback / Forward Fix if Required
```

Current Databricks documentation describes a lifecycle centered on
local/project development, validation, deployment and execution.

------------------------------------------------------------------------

# 17. Bundle Resources

A bundle can define supported Databricks resources as source files.

For this roadmap, focus on:

-   jobs;
-   pipelines;
-   tasks;
-   Python artifacts;
-   workload configuration.

Mental model:

``` text
Bundle
 ├── Ingestion Job
 ├── Declarative Pipeline
 └── Quality Job
```

This is the bridge between Topics 07--08 and Topic 12.

------------------------------------------------------------------------

# 18. Job as a Bundle Resource

A conceptual resource:

``` yaml
resources:
  jobs:
    ingestion_job:
      name: ingestion-job
      tasks:
        - task_key: ingest
          notebook_task:
            notebook_path: ./notebooks/ingest.py
```

Production job configuration may additionally include:

-   task dependencies;
-   parameters;
-   compute;
-   libraries;
-   notifications;
-   schedules;
-   permissions;
-   run identity.

Exact fields depend on the current Databricks resource schema.

------------------------------------------------------------------------

# 19. Pipeline as a Bundle Resource

A pipeline resource connects Topic 07 to deployment-as-code.

Conceptually:

``` yaml
resources:
  pipelines:
    bronze_silver_pipeline:
      name: bronze-silver-pipeline
      catalog: ${var.catalog}
      schema: ${var.schema}
```

The exact schema depends on the current Lakeflow Declarative Pipelines
resource model.

Do not re-teach pipeline semantics here.

The focus is:

``` text
Pipeline Definition
+
Environment Configuration
+
Version Control
+
Deployment
```

------------------------------------------------------------------------

# 20. Jobs + Pipelines + Quality Gates

A realistic data platform can be represented as:

``` text
Bundle
 │
 ├── Ingestion Job
 │
 ├── Declarative Pipeline
 │
 └── Quality Job
```

Operational sequence:

``` text
Ingestion
   ↓
Pipeline
   ↓
Quality Checks
   ↓
Promotion / Consumption
```

This makes the entire workload reviewable and reproducible.

------------------------------------------------------------------------

# 21. Python Wheels

Production Data Engineering logic should not always live inside giant
notebooks.

A Python wheel provides a packaged application artifact.

Flow:

``` text
src/
 ↓
Python Package
 ↓
Build Wheel
 ↓
Bundle Artifact
 ↓
Deploy
 ↓
Job
 ↓
Python Wheel Task
```

Benefits:

-   package boundaries;
-   testing;
-   dependency management;
-   versioning;
-   reproducibility;
-   cleaner CI;
-   reusable business logic.

------------------------------------------------------------------------

# 22. Python Project Structure

Example:

``` text
src/
└── data_platform/
    ├── __init__.py
    ├── main.py
    ├── transforms.py
    └── validation.py

tests/
└── unit/
    ├── test_transforms.py
    └── test_validation.py

pyproject.toml
```

Example pure function:

``` python
def calculate_margin(revenue: float, cost: float) -> float:
    return revenue - cost
```

Test:

``` python
def test_calculate_margin():
    assert calculate_margin(100.0, 60.0) == 40.0
```

The fast test should run without deploying a Databricks workspace.

------------------------------------------------------------------------

# 23. Python Wheel Build

Modern Python projects commonly use `pyproject.toml`.

Illustrative:

``` toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "data-platform"
version = "0.1.0"
dependencies = []
```

A build system can produce:

``` text
dist/
└── data_platform-0.1.0-py3-none-any.whl
```

Use the organization's approved packaging/build tool.

The current Databricks bundle templates also support Python wheel
artifacts.

------------------------------------------------------------------------

# 24. Wheel + Bundle Artifact

Current Databricks documentation supports a bundle artifact of type
`whl`.

Conceptual configuration:

``` yaml
artifacts:
  default:
    type: whl
    build: uv build
    path: .
```

A job can then reference the wheel:

``` yaml
resources:
  jobs:
    data_job:
      tasks:
        - task_key: run_python
          python_wheel_task:
            package_name: data_platform
            entry_point: main
          libraries:
            - whl: ./dist/*.whl
```

The exact build command and task settings must match the package and
current CLI/schema.

------------------------------------------------------------------------

# 25. Wheel Versioning

A production artifact should be traceable:

``` text
Git commit
   ↓
Package version
   ↓
Wheel
   ↓
Bundle deployment
   ↓
Job run
```

Do not rely only on:

``` text
latest.whl
```

A production investigation should answer:

> Which source revision produced the code running in this job?

------------------------------------------------------------------------

# 26. Per-Target Overrides

The same workload can require different settings.

Roadmap-required override categories:

-   catalog;
-   compute;
-   schedule;
-   permissions.

Example:

  Setting       Dev              Staging               Prod
  ------------- ---------------- --------------------- -------------------
  Catalog       `dev_catalog`    `staging_catalog`     `prod_catalog`
  Compute       Small/low-cost   Moderate              Production-sized
  Schedule      Paused           Controlled            Business schedule
  Permissions   Developer        QA/Engineering        Production group
  Identity      Developer/CI     CI/service identity   Service principal

The code remains consistent.

The environment configuration changes deliberately.

------------------------------------------------------------------------

# 27. Catalog Isolation

Never use the same production catalog simply because:

> "The code is identical."

Correct:

``` text
dev_catalog
staging_catalog
prod_catalog
```

Benefits:

-   data isolation;
-   write protection;
-   controlled testing;
-   easier incident containment;
-   clearer lineage;
-   lower accidental production risk.

Environment isolation is a security control, not merely an
organizational convention.

------------------------------------------------------------------------

# 28. Compute Overrides

Development and production can legitimately require different compute.

``` text
DEV
small / serverless / low cost

STAGING
representative test compute

PROD
production-appropriate compute
```

Choose based on:

-   workload size;
-   latency;
-   reliability;
-   concurrency;
-   cost;
-   performance requirements.

Do not hard-code arbitrary instance types merely to make a tutorial look
realistic.

------------------------------------------------------------------------

# 29. Schedule Overrides

Schedules should normally be:

``` text
Dev       → paused / manually triggered
Staging   → controlled test schedule
Prod      → business schedule
```

Why?

An accidental development schedule can cause:

-   duplicate processing;
-   unexpected writes;
-   noisy alerts;
-   compute spend;
-   test-data corruption.

A production schedule is an operational dependency and should be
reviewed like code.

------------------------------------------------------------------------

# 30. Permission Overrides

Example:

``` text
DEV
developer group

STAGING
engineering + QA

PROD
controlled production group
```

Follow least privilege.

Do not solve deployment convenience by giving CI or developers broad
administrator access.

------------------------------------------------------------------------

# 31. CI/CD Fundamentals

## Continuous Integration

Every change should be evaluated automatically.

Typical CI:

``` text
Lint
 ↓
Unit Tests
 ↓
Security Checks
 ↓
Bundle Validation
```

## Continuous Delivery / Deployment

Approved changes move through environments:

``` text
Dev
 ↓
Integration Tests
 ↓
Staging
 ↓
Approval
 ↓
Production
```

CI/CD is not:

> "Deploy every commit directly to production."

It is:

> **A controlled mechanism for producing, validating and promoting
> software.**

------------------------------------------------------------------------

# 32. Git Workflow

Recommended baseline:

``` text
main
 │
 ├── feature/a
 ├── feature/b
 └── fix/c
```

Workflow:

``` text
Feature Branch
 ↓
Commit
 ↓
Pull Request
 ↓
Review
 ↓
CI
 ↓
Merge
 ↓
Promotion
```

Production deployment should be traceable to:

``` text
Git repository
+
commit SHA
+
bundle target
+
deployment identity
```

Use protected branches and required reviews for production repositories.

------------------------------------------------------------------------

# 33. GitHub Actions

GitHub Actions is one implementation of the CI/CD control plane.

Conceptual workflow:

``` text
Pull Request
      ↓
GitHub Actions
      ├── lint
      ├── unit tests
      ├── security checks
      └── bundle validate
```

After merge:

``` text
main
 ↓
Deploy Dev
 ↓
Integration Tests
 ↓
Deploy Staging
 ↓
Approval
 ↓
Deploy Production
```

Separate:

``` text
GitHub Actions
```

from:

``` text
Databricks Asset Bundles
```

GitHub Actions orchestrates the delivery process.

The bundle defines the Databricks project/resources.

------------------------------------------------------------------------

# 34. Representative GitHub Actions Workflow

Illustrative structure:

``` yaml
name: databricks-ci

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest

      - name: Unit tests
        run: pytest

      - name: Databricks bundle validation
        run: databricks bundle validate -t dev
```

The exact Databricks authentication and CLI installation steps depend on
the current Databricks/GitHub integration guidance.

Never copy a credential pattern from an old tutorial without verifying
it.

------------------------------------------------------------------------

# 35. CI Authentication

Authentication is one of the most important production concerns.

Bad default:

``` text
GitHub Actions
      ↓
Developer personal token
      ↓
Production
```

Problems:

-   tied to an individual;
-   difficult offboarding;
-   long-lived secret risk;
-   poor separation of duties;
-   weak audit semantics.

Preferred architecture:

``` text
GitHub Actions
      ↓
OIDC token
      ↓
Cloud / Databricks trust
      ↓
Service Principal
      ↓
Databricks Deployment
```

The exact federation configuration differs by cloud and organization.

------------------------------------------------------------------------

# 36. OIDC / Workload Identity Federation

OIDC means OpenID Connect.

In CI/CD, the important idea is:

``` text
GitHub proves workload identity
        ↓
Trusted identity system verifies claims
        ↓
Short-lived access is granted
        ↓
CI deploys
```

Key concepts:

-   issuer;
-   audience;
-   claims;
-   trust relationship;
-   repository identity;
-   branch/environment conditions;
-   short-lived credentials.

Avoid hard-coding cloud-specific claims without verification.

AWS, Azure and GCP differ.

The architecture remains:

``` text
CI Workload
 ↓
Federated Identity
 ↓
Trusted Service Identity
 ↓
Least-Privilege Deployment
```

------------------------------------------------------------------------

# 37. Service Principals

A production deployment identity should be controlled by the
organization.

Responsibilities include:

-   deployment permissions;
-   ownership;
-   audit;
-   lifecycle;
-   least privilege;
-   rotation/revocation.

Example:

``` text
Developer
   |
   | PR
   v
CI
   |
   | OIDC
   v
Deployment Service Principal
   |
   v
Production Workspace
```

Runtime identity may be separate:

``` text
Deployment SP
      ≠
Runtime SP
```

That separation can reduce blast radius.

------------------------------------------------------------------------

# 38. Secrets Management

Rules:

``` text
Never hard-code secrets.
Never commit tokens.
Never print secrets.
Never store credentials in YAML.
Never use personal credentials as the permanent CI identity.
```

Use appropriate:

-   GitHub secret mechanisms where secrets are unavoidable;
-   cloud secret stores;
-   Databricks secret mechanisms where appropriate;
-   OIDC/workload identity federation to eliminate long-lived
    credentials where possible.

Security mental model:

``` text
Secret in Git
=
Potential security incident
```

------------------------------------------------------------------------

# 39. Unit Testing

Unit tests should be fast.

Test:

-   pure Python logic;
-   transformations where practical;
-   validation utilities;
-   configuration helpers;
-   parsing logic;
-   business rules.

Example:

``` python
def calculate_margin(revenue, cost):
    return revenue - cost
```

Test:

``` python
def test_margin():
    assert calculate_margin(100, 70) == 30
```

Do not require a full Databricks deployment for every unit test.

Fast tests belong early in CI.

------------------------------------------------------------------------

# 40. Integration Testing

Integration tests answer:

> Does the deployed system behave correctly against a real Databricks
> environment?

Pipeline:

``` text
Unit Tests
 ↓
Bundle Validate
 ↓
Deploy Dev
 ↓
Integration Job
 ↓
Validate Output
```

Integration tests can verify:

-   resource creation;
-   permissions;
-   task execution;
-   pipeline output;
-   table schema;
-   row counts;
-   business metrics;
-   downstream compatibility.

Use small controlled data.

------------------------------------------------------------------------

# 41. End-to-End Testing

A production data platform can also require:

``` text
Source
 ↓
Ingestion
 ↓
Pipeline
 ↓
Quality
 ↓
Gold
 ↓
Consumer
```

E2E tests are slower and more expensive.

Use them selectively.

Testing pyramid:

``` text
          E2E
         /   \
   Integration
      /       \
    Unit Tests
```

Most tests should be fast.

------------------------------------------------------------------------

# 42. Data Diffs

A deployment can succeed technically and still produce incorrect data.

Therefore:

``` text
Code Test
+
Infrastructure Test
+
Data Test
```

Example:

``` text
Before:
daily revenue = $1.20M

After:
daily revenue = $1.19M
```

The 0.8% difference may be:

-   expected because a bug was fixed;
-   expected because source data changed;
-   suspicious because a join changed;
-   unacceptable because records disappeared.

Data diffs require business context.

------------------------------------------------------------------------

# 43. Data Diff Techniques

Compare:

-   schema;
-   row counts;
-   null rates;
-   duplicate rates;
-   distinct counts;
-   aggregates;
-   business KPIs;
-   checksum/hash where appropriate.

Example:

``` sql
SELECT
    COUNT(*) AS rows,
    SUM(revenue) AS revenue,
    AVG(revenue) AS avg_revenue
FROM gold.daily_sales
WHERE business_date = '2026-10-01';
```

The comparison should be performed against a controlled baseline or
expected range.

------------------------------------------------------------------------

# 44. Data Quality Gates

Example:

``` text
Schema valid
+
Row count within expected range
+
Null rates acceptable
+
No unexpected duplicates
+
Business metrics reconcile
=
Promotion allowed
```

This is a critical Data Engineering principle:

> **CI/CD must test data, not only code.**

------------------------------------------------------------------------

# 45. Configuration Drift

Example:

``` text
Git:
schedule = 02:00

Workspace:
schedule = 01:00
```

Possible causes:

-   manual UI edit;
-   emergency change;
-   incomplete deployment;
-   multiple deployment systems;
-   Terraform/Bundle ownership overlap.

Response:

``` text
Detect
 ↓
Compare
 ↓
Identify owner
 ↓
Decide desired state
 ↓
Restore desired state
 ↓
Prevent recurrence
```

------------------------------------------------------------------------

# 46. Drift Prevention

Controls:

-   protected production workspace;
-   restricted manual editing;
-   Git review;
-   CI/CD deployment;
-   clear resource ownership;
-   Terraform/Bundle boundaries;
-   audit;
-   deployment verification.

Golden rule:

> **Do not create a second unofficial source of truth.**

------------------------------------------------------------------------

# 47. Asset Bundles vs Terraform

This is a boundary question.

## Asset Bundles

Strong fit for:

-   Databricks jobs;
-   pipelines;
-   workload/application resources;
-   source files;
-   bundle artifacts;
-   Databricks project deployment.

## Terraform

Strong fit for:

-   cloud infrastructure;
-   networking;
-   workspace infrastructure;
-   identity infrastructure;
-   Unity Catalog infrastructure where appropriate;
-   infrastructure lifecycle/state.

This is not an absolute rule.

Use the tool that owns the resource lifecycle most cleanly.

------------------------------------------------------------------------

# 48. Bundles + Terraform

A common architecture:

``` text
Terraform
   ↓
Cloud / Workspace Infrastructure
   ↓
Databricks Environment
   ↓
Asset Bundle
   ↓
Jobs / Pipelines / Workload Resources
```

Example ownership:

  Resource                   Preferred owner
  -------------------------- -------------------------
  VPC/VNet                   Terraform
  Subnets                    Terraform
  Cloud identity             Terraform/cloud IaC
  Workspace infrastructure   Terraform
  Databricks workload job    Bundle
  Pipeline workload          Bundle
  Python artifact            Bundle
  CI workflow                GitHub/GitOps
  Data product application   Bundle + supporting IaC

The actual boundary depends on organization standards and provider
support.

------------------------------------------------------------------------

# 49. Terraform and Bundle Ownership Conflict

Bad:

``` text
Terraform
   ↓
manages Job A

Bundle
   ↓
also manages Job A
```

Now:

``` text
Two Sources of Truth
```

Potential result:

``` text
Terraform applies
 ↓
Bundle changes
 ↓
Terraform detects drift
 ↓
Terraform changes it back
```

Define ownership explicitly.

------------------------------------------------------------------------

# 50. Production Promotion

Preferred:

``` text
Feature Branch
      ↓
Pull Request
      ↓
CI
      ↓
Dev
      ↓
Integration Tests
      ↓
Staging
      ↓
Approval
      ↓
Production
```

Avoid:

``` text
Dev code
 ↓
Rebuild manually
 ↓
Modify config
 ↓
Production
```

Promotion should preserve the reviewed code/configuration identity.

------------------------------------------------------------------------

# 51. Environment-Specific Configuration vs Code Forks

Good:

``` text
Same application
+
Target configuration
```

Bad:

``` text
dev.py
staging.py
prod.py

with copied business logic
```

Do not fork business logic just because environments differ.

Prefer:

``` text
Code
+
Variables
+
Targets
+
Controlled Overrides
```

------------------------------------------------------------------------

# 52. Rollback

Rollback has at least two dimensions.

## Code/configuration rollback

Return to a previous known-good deployment:

``` text
Production
 ↓
Identify version
 ↓
Select previous bundle/Git revision
 ↓
Redeploy
 ↓
Validate
```

## Data rollback

Data may require separate recovery.

``` text
Bad Code
 ↓
Bad Data
 ↓
Code Rollback
 +
Data Recovery / Reconciliation
```

Critical principle:

> **Rolling back code does not automatically roll back data.**

------------------------------------------------------------------------

# 53. Delta Time Travel and Deployment Rollback

Suppose:

``` text
Deployment v42
   ↓
Transformation bug
   ↓
Incorrect historical rows
```

You may need:

``` text
Code rollback
+
Data recovery/reconciliation
```

Potential data-recovery mechanisms can include Delta time travel where
appropriate.

But time travel is not a universal rollback button.

Consider:

-   retention;
-   downstream consumers;
-   external side effects;
-   irreversible operations;
-   CDC;
-   idempotency;
-   writes to external systems.

Always validate recovery semantics before modifying production data.

------------------------------------------------------------------------

# 54. Failed Halfway Deployment

A production deployment can fail after some resources change.

Do not assume:

``` text
Deployment failed
=
Nothing changed
```

Investigation:

``` text
Identify target
 ↓
Identify commit
 ↓
Identify deployment state
 ↓
Identify changed resources
 ↓
Determine partial state
 ↓
Validate desired state
 ↓
Recover or redeploy
```

A safe recovery may be:

``` text
Forward fix
```

rather than rollback.

Rollback is a decision, not an automatic reflex.

------------------------------------------------------------------------

# 55. Production Security Model

Production delivery should enforce:

-   protected branches;
-   pull-request review;
-   least privilege;
-   service principals;
-   OIDC where supported;
-   environment isolation;
-   Unity Catalog governance;
-   controlled production permissions;
-   auditability;
-   deployment approvals;
-   secure secret management.

CI/CD itself is a security boundary.

A compromised CI pipeline can deploy malicious code.

Therefore:

``` text
Repository Security
+
CI Security
+
Identity Security
+
Workspace Security
=
Production Security
```

------------------------------------------------------------------------

# 56. Observability

Deployment observability should allow you to answer:

> Which Git commit deployed the currently running production job?

Capture/retain where appropriate:

-   CI run ID;
-   Git commit SHA;
-   bundle target;
-   deployment identity;
-   deployment timestamp;
-   Databricks job/pipeline identifiers;
-   run IDs;
-   audit records.

Correlation:

``` text
Git SHA
 ↓
CI Run
 ↓
Bundle Deployment
 ↓
Databricks Resource
 ↓
Job Run
 ↓
Data Output
```

This is invaluable during incidents.

------------------------------------------------------------------------

# 57. Cost-Aware CI/CD

CI/CD can create significant Databricks spend if poorly designed.

Cost drivers:

-   integration test compute;
-   staging compute;
-   repeated deployments;
-   long-running test jobs;
-   oversized test data;
-   always-on clusters;
-   repeated full-refresh pipelines.

Controls:

-   small test datasets;
-   serverless where appropriate;
-   ephemeral compute;
-   auto-termination;
-   limited test frequency;
-   targeted integration tests;
-   production-like tests only when justified.

Principle:

> **Reliable CI/CD should not become an unnecessary source of Databricks
> spend.**

------------------------------------------------------------------------

# 58. CI Failure Modes

## Invalid YAML

**Symptom:** validation fails.

**Likely cause:** malformed or unsupported configuration.

**Investigation:** run local validation and inspect the referenced
configuration file.

**Fix:** correct syntax/schema.

------------------------------------------------------------------------

## Wrong Target

**Symptom:** deployment appears in the wrong workspace.

**Cause:** incorrect target/default target.

**Fix:** explicitly specify:

``` bash
databricks bundle deploy -t dev
```

and verify target workspace before deployment.

------------------------------------------------------------------------

## Wrong Catalog

**Symptom:** development writes to production.

**Cause:** incorrect variable/override.

**Fix:** isolate catalog and add a deployment test.

------------------------------------------------------------------------

## Missing Permission

**Symptom:** deployment fails with authorization error.

**Cause:** CI identity lacks required permission.

**Fix:** grant minimum required access and verify identity.

------------------------------------------------------------------------

## OIDC Failure

**Symptom:** CI authenticates locally but fails in GitHub.

**Investigate:**

-   issuer;
-   audience;
-   trust policy;
-   repository/branch conditions;
-   service identity;
-   environment configuration.

------------------------------------------------------------------------

## Personal Token in CI

**Symptom:** deployment depends on an employee credential.

**Fix:**

``` text
Personal Token
 ↓
Migration Plan
 ↓
OIDC / Federated Identity
 ↓
Service Principal
```

Rotate/revoke the old credential after validation.

------------------------------------------------------------------------

## Wheel Dependency Failure

**Symptom:** deployment succeeds but task fails at runtime.

**Cause:** missing/incompatible dependency.

**Fix:** reproduce in a controlled environment, pin compatible
dependencies and rerun integration tests.

------------------------------------------------------------------------

## Pipeline Resource Failure

**Symptom:** bundle deploys but pipeline cannot run.

**Cause:** invalid resource configuration, catalog/schema/permission
mismatch or environment issue.

**Fix:** inspect deployment and pipeline configuration separately.

------------------------------------------------------------------------

## Dev Schedule Accidentally Enabled

**Symptom:** development job runs unexpectedly.

**Cause:** schedule override omitted.

**Fix:** explicitly pause/disable development scheduling and add a test.

------------------------------------------------------------------------

## Integration Test Failure

**Symptom:** deployment works but test fails.

**Correct response:**

``` text
STOP
 ↓
Investigate
 ↓
Classify code/config/data issue
 ↓
Fix
 ↓
Rerun
```

Do not promote merely because deployment technically succeeded.

------------------------------------------------------------------------

# 59. Required Hands-On Exercise — `databricks.yml` and `.github/workflows/`

This is the central exercise for Topic 12.

## Exercise 1 --- Define Workload Resources

Represent:

-   ingestion job;
-   declarative pipeline;
-   quality job;

as bundle resources.

Use variables for:

-   catalog;
-   schema;
-   schedule;
-   compute.

------------------------------------------------------------------------

## Exercise 2 --- Dev Target

Deploy to:

``` text
dev
```

using development mode.

Verify:

-   development resource naming behavior;
-   development tags/behavior where applicable;
-   paused or controlled schedules;
-   development catalog;
-   developer-safe permissions.

------------------------------------------------------------------------

## Exercise 3 --- CI Workflow

Build:

``` text
Unit Tests
   ↓
bundle validate
   ↓
Deploy Dev
   ↓
Integration Job
   ↓
Staging
   ↓
Production Approval
   ↓
Deploy Prod
```

Use service-principal authentication through an appropriate federated
identity/OIDC model.

------------------------------------------------------------------------

## Exercise 4 --- Deliberate Failure

Break a resource definition.

Run CI.

Record:

``` text
Failure
Error
Evidence
Root Cause
Fix
Verification
Prevention
```

------------------------------------------------------------------------

## Exercise 5 --- Production Deployment

Deploy a version to production.

Record:

-   Git SHA;
-   bundle target;
-   deployment identity;
-   resources changed;
-   deployment timestamp.

------------------------------------------------------------------------

## Exercise 6 --- Rollback

Deploy a deliberately safe test revision, then return to the previous
known-good version.

Document:

``` text
Current version
Previous version
Rollback command/process
Validation
Data implications
```

------------------------------------------------------------------------

# 60. Progressive Hands-On Labs

## Lab 1 — Create a Bundle

Build:

``` text
databricks.yml
resources/
src/
tests/
```

**Goal:** understand the project model.

## Lab 2 — Validate a Bundle

Run:

``` bash
databricks bundle validate -t dev
```

**Goal:** interpret configuration errors.

## Lab 3 — Deploy Development

Deploy:

``` bash
databricks bundle deploy -t dev
```

**Goal:** understand target deployment.

## Lab 4 — Define a Job

Convert a manually configured job into a bundle resource.

## Lab 5 — Define a Pipeline

Represent a Lakeflow Declarative Pipeline as a resource.

## Lab 6 — Build a Python Wheel

Create package code and a wheel artifact.

## Lab 7 — Connect Wheel to Job

Use a Python wheel task.

## Lab 8 — Add Dev/Staging/Prod

Create environment targets.

## Lab 9 — Target Overrides

Change:

-   catalog;
-   compute;
-   schedule;
-   permissions.

## Lab 10 — Unit-Test CI

Run Python tests before bundle deployment.

## Lab 11 — Bundle Validation CI

Intentionally break configuration and verify CI fails.

## Lab 12 — Integration Testing

Deploy to dev and execute a controlled integration test.

## Lab 13 — Federated CI Identity

Design and, where the environment permits, implement OIDC/workload
federation.

## Lab 14 — Production Deployment

Promote through staging into production.

## Lab 15 — Data Diff

Compare before/after:

-   schema;
-   row count;
-   null rate;
-   business metrics.

## Lab 16 — Terraform Boundary

Design which resources Terraform owns and which the Bundle owns.

Every lab must document:

``` text
Objective
Prerequisites
Setup
Files/Configuration
Commands
Expected Behavior
Troubleshooting
Cleanup
Production Lesson
```

------------------------------------------------------------------------

# 61. Break/Fix Incidents

Each incident follows:

``` text
Symptom
 ↓
Business Impact
 ↓
Initial Hypothesis
 ↓
Evidence
 ↓
Investigation
 ↓
Root Cause
 ↓
Fix
 ↓
Verification
 ↓
Prevention
 ↓
Production Lesson
```

## Incident 1 — Bundle Validation Failure

Invalid resource configuration.

## Incident 2 — Wrong Target

Deployment accidentally targets production.

## Incident 3 — Production Catalog Used in Dev

Variable/override incorrectly maps development to production.

## Incident 4 — Service Principal Permission Failure

CI identity cannot create/update the required resource.

## Incident 5 — OIDC Authentication Failure

Federated identity trust is misconfigured.

## Incident 6 — Personal Token in CI

CI still depends on an employee token.

## Incident 7 — Python Wheel Dependency Failure

Job deploys but runtime dependencies are incompatible.

## Incident 8 — Pipeline Resource Failure

Pipeline deployment or execution fails due to target configuration.

## Incident 9 — Dev Schedule Accidentally Enabled

Development workload unexpectedly runs.

## Incident 10 — Deployment Succeeds, Integration Test Fails

Deployment is technically successful but output is incorrect.

## Incident 11 — Configuration Drift

Workspace differs from Git.

## Incident 12 — Data Diff Detects Revenue Change

Business metric changes unexpectedly after deployment.

## Incident 13 — Production Rollback Fails

Previous deployment cannot be restored cleanly.

## Incident 14 — Code Rollback, Data Still Incorrect

The application is restored but historical output remains wrong.

## Incident 15 — Terraform/Bundle Ownership Conflict

Two deployment systems continuously overwrite each other.

## Incident 16 — Wrong Production Identity

Production resource runs as a developer rather than the intended service
identity.

## Incident 17 — Integration Tests Too Expensive

CI consumes excessive compute because every test runs on large
production-sized data.

## Incident 18 — Branch/Production Mismatch

Production deployment is attempted from an unexpected branch/revision.

------------------------------------------------------------------------

# 62. Production Runbooks

## Runbook 1 --- Failed Bundle Validation

``` text
Capture error
 ↓
Identify file
 ↓
Inspect YAML/schema
 ↓
Validate locally
 ↓
Reproduce
 ↓
Fix
 ↓
Rerun
```

Checklist:

-   [ ] Correct target
-   [ ] Correct YAML
-   [ ] Correct resource key
-   [ ] Correct variable
-   [ ] Current CLI
-   [ ] Current resource schema
-   [ ] Validation passes

------------------------------------------------------------------------

## Runbook 2 --- Failed Production Deployment

1.  Identify Git SHA.
2.  Identify CI run.
3.  Identify deployment identity.
4.  Identify target.
5.  Inspect bundle output.
6.  Verify permissions.
7.  Determine partial changes.
8.  Decide forward fix vs rollback.
9.  Validate.
10. Monitor.

------------------------------------------------------------------------

## Runbook 3 --- Production Rollback

1.  Identify current version.
2.  Identify last known-good version.
3.  Determine whether code rollback is enough.
4.  Determine whether data recovery is required.
5.  Redeploy previous bundle version.
6.  Validate resources.
7.  Validate data.
8.  Monitor.
9.  Document.

------------------------------------------------------------------------

## Runbook 4 --- CI Authentication Failure

Check:

``` text
GitHub workflow
 ↓
OIDC token
 ↓
Issuer
 ↓
Audience
 ↓
Trust relationship
 ↓
Service Principal
 ↓
Databricks permissions
```

Never solve an identity problem by blindly granting administrator
access.

------------------------------------------------------------------------

## Runbook 5 --- Configuration Drift

``` text
Git
vs
Workspace
```

1.  Capture evidence.
2.  Identify manual change.
3.  Identify owner.
4.  Determine desired state.
5.  Restore desired state.
6.  Restrict unauthorized edits.
7.  Add drift detection/verification.
8.  Document.

------------------------------------------------------------------------

## Runbook 6 --- Data-Diff Failure

1.  Stop promotion.
2.  Identify affected revision.
3.  Compare schema.
4.  Compare row counts.
5.  Compare null/duplicate rates.
6.  Compare business aggregates.
7.  Identify expected vs unexpected change.
8.  Fix or approve documented expected change.
9.  Rerun validation.

------------------------------------------------------------------------

# 63. Decision Matrices

## Asset Bundles vs Terraform

  -----------------------------------------------------------------------
  Dimension               Asset Bundles           Terraform
  ----------------------- ----------------------- -----------------------
  Databricks jobs         Strong                  Possible depending on
                                                  provider/resource

  Databricks pipelines    Strong                  Possible depending on
                                                  provider/resource

  Python artifacts        Strong                  Not primary

  Cloud networking        Not primary             Strong

  Workspace               Not primary             Strong
  infrastructure                                  

  Identity infrastructure Not primary             Strong

  Workload deployment     Strong                  Secondary

  Infrastructure state    Bundle deployment state Terraform state

  Application source      Strong                  Not primary

  CI/CD                   Strong                  Strong

  Best mental model       Workload delivery       Infrastructure
                                                  lifecycle
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## Notebook vs Python Package/Wheel

  Dimension                      Notebook    Python Package/Wheel
  ------------------------------ ----------- ----------------------
  Exploration                    Excellent   Lower
  Collaboration                  Medium      High with Git
  Unit testing                   Medium      Strong
  Reuse                          Medium      Strong
  Packaging                      Weak        Strong
  Production application logic   Possible    Strong
  Versioning                     Git         Git + artifact
  CI/CD                          Possible    Strong

------------------------------------------------------------------------

## Personal Token vs Service Principal vs OIDC

  -----------------------------------------------------------------------
  Dimension         Personal Token    Service Principal OIDC/Federation
  ----------------- ----------------- ----------------- -----------------
  Human dependency  High              Low               Low

  Long-lived secret Often             Possible          Minimized

  Auditability      Weak/medium       Strong            Strong

  Rotation burden   High              Managed           Lower

  CI suitability    Poor default      Strong            Strongest pattern
                                                        where supported

  Offboarding risk  High              Low               Low
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## Manual Deployment vs CI/CD

  Dimension                  Manual      CI/CD
  -------------------------- ----------- ------------
  Speed for one experiment   High        Medium
  Reproducibility            Low         High
  Peer review                Low         High
  Auditability               Medium      High
  Rollback                   Difficult   Controlled
  Human error                Higher      Lower
  Production suitability     Low         High

------------------------------------------------------------------------

# 64. Architecture Decision Records

## ADR-001 --- Adopt Asset Bundles for Databricks Workload Deployment

**Context:** Databricks jobs and pipelines are currently configured
manually.

**Problem:** Configuration drift and poor reproducibility.

**Options:** 1. Continue manual configuration. 2. Use Asset Bundles. 3.
Use Terraform for all workload configuration.

**Decision:** Use Asset Bundles for supported Databricks
workload/project deployment.

**Why:** Source-controlled workload definitions, validation, deployment
and CI/CD alignment.

**Security:** Production deployment through controlled identity.

**Cost:** Smaller and more repeatable test environments.

**Rollback:** Redeploy a known-good bundle revision.

------------------------------------------------------------------------

## ADR-002 --- Separate Dev/Staging/Prod

**Decision:** Use explicit targets and environment isolation.

**Why:** Prevent accidental production writes and enable progressive
validation.

------------------------------------------------------------------------

## ADR-003 --- Use Python Wheels for Production Logic

**Decision:** Package reusable Python application logic into wheels.

**Why:** Testing, dependency management, reuse and reproducibility.

------------------------------------------------------------------------

## ADR-004 --- Use OIDC/Federated Identity for CI

**Decision:** Prefer short-lived federated authentication over personal
long-lived tokens.

**Why:** Better security, lifecycle and auditability.

------------------------------------------------------------------------

## ADR-005 --- Terraform + Asset Bundle Boundary

**Decision:** Terraform owns infrastructure; Asset Bundles own supported
Databricks workload resources.

**Consequence:** Ownership must be explicit.

------------------------------------------------------------------------

## ADR-006 --- Require Integration/Data-Diff Gates

**Decision:** No production promotion after deployment alone.

**Required:**

``` text
Deploy
+
Integration Tests
+
Data Validation
=
Promotion Candidate
```

Each ADR should include:

``` text
Context
Problem
Options
Decision
Why
Security
Cost
Operational Impact
Trade-offs
Consequences
Rollback
Validation
```

------------------------------------------------------------------------

# 65. Interview Preparation

## Beginner --- 15

1.  What is a Databricks Asset Bundle?
2.  What is Declarative Automation Bundles?
3.  What is `databricks.yml`?
4.  What is a target?
5.  What does `bundle validate` do?
6.  What does `bundle deploy` do?
7.  What does `bundle run` do?
8.  What does `bundle destroy` do?
9.  Why use Git?
10. Why separate dev and production?
11. What is a Python wheel?
12. What is CI?
13. What is CD?
14. What is a service principal?
15. Why is OIDC useful?

### Strong Answer Pattern

Define the concept, explain why it exists, describe where it fits in the
deployment lifecycle, then state the main production control.

------------------------------------------------------------------------

## Intermediate --- 20

1.  Why are Asset Bundles better than manual job creation?
2.  How does `databricks.yml` relate to resource files?
3.  Why use targets?
4.  What does development mode provide?
5.  What does production mode provide?
6.  Why should production use a service principal?
7.  How do Python wheels improve production delivery?
8.  How should schedules differ by environment?
9.  Why isolate catalogs?
10. What is configuration drift?
11. How does Git improve deployment auditability?
12. What should CI validate?
13. Why are integration tests separate from unit tests?
14. What are data diffs?
15. Why is data quality part of CI/CD?
16. How do Bundles and Terraform differ?
17. How can they coexist?
18. Why should personal tokens be avoided in CI?
19. What is workload identity federation?
20. Why can a successful deployment still be a failed release?

------------------------------------------------------------------------

## Advanced --- 20

1.  Design a multi-target bundle.
2.  Design a production Python wheel deployment.
3.  Design a job and pipeline as resources.
4.  Explain development mode safety.
5.  Explain production mode behavior.
6.  Design target-specific catalog isolation.
7.  Design compute overrides.
8.  Design schedule overrides.
9.  Design permission overrides.
10. Design GitHub Actions CI.
11. Design OIDC authentication.
12. Explain service-principal deployment.
13. Design integration tests.
14. Design data-diff gates.
15. Design rollback.
16. Explain code vs data rollback.
17. Design drift prevention.
18. Define the Terraform/Bundle boundary.
19. Design deployment observability.
20. Design cost controls.

------------------------------------------------------------------------

## Senior / Production --- 20

1.  A developer manually changed production configuration. What do you
    do?
2.  CI validates but production deployment fails. How do you
    investigate?
3.  Integration tests show a 7% revenue difference. Should promotion
    continue?
4.  A deployment fails halfway. What does rollback mean?
5.  Your company wants Terraform for everything. Where do Bundles add
    value?
6.  GitHub Actions uses a developer token. How do you migrate safely?
7.  Code rollback succeeds but data is incorrect. What next?
8.  Dev and prod share a catalog. Why is this unsafe?
9.  How would you design a 100-job Databricks CI/CD platform?
10. How would you prevent two deployment systems from owning the same
    resource?
11. How would you correlate a production job to its Git commit?
12. How would you control CI compute cost?
13. How would you design release approvals?
14. How would you handle an emergency production fix?
15. How would you test a breaking schema change?
16. How would you design deployment identity vs runtime identity?
17. How would you detect configuration drift?
18. How would you safely roll back a bad transformation?
19. How would you prove a release is reproducible?
20. What makes Databricks CI/CD production-grade?

------------------------------------------------------------------------

# 66. Practice Questions

## Asset Bundle Concepts — 20

1.  Explain an Asset Bundle in your own words.
2.  Explain why manual deployment creates drift.
3.  Explain `databricks.yml`.
4.  Explain bundle targets.
5.  Explain development mode.
6.  Explain production mode.
7.  Explain bundle resources.
8.  Explain artifacts.
9.  Explain validation.
10. Explain deployment.
11. Explain run.
12. Explain destroy.
13. Explain bundle lifecycle.
14. Explain source-controlled configuration.
15. Explain desired state.
16. Explain idempotency.
17. Explain environment isolation.
18. Explain deployment identity.
19. Explain runtime identity.
20. Explain rollback.

## YAML / Configuration — 15

1.  Define a bundle name.
2.  Add an `include`.
3.  Define a variable.
4.  Define dev and prod targets.
5.  Mark a target as default.
6.  Configure a workspace host.
7.  Define a job resource.
8.  Define a pipeline resource.
9.  Define an artifact.
10. Configure a Python wheel task.
11. Override a catalog.
12. Override compute.
13. Override schedule.
14. Override permissions.
15. Explain which syntax must be verified against the current schema.

## CI/CD — 20

1.  Design a PR workflow.
2.  Add linting.
3.  Add unit tests.
4.  Add bundle validation.
5.  Deploy dev.
6.  Run integration tests.
7.  Deploy staging.
8.  Add approval.
9.  Deploy production.
10. Record Git SHA.
11. Record bundle target.
12. Record deployment identity.
13. Add data-diff validation.
14. Add post-deployment verification.
15. Add failure notifications.
16. Add rollback.
17. Add branch protection.
18. Add release tagging.
19. Add cost controls.
20. Explain why automatic production deployment is not always
    appropriate.

## Security — 15

1.  Explain least privilege.
2.  Explain service principals.
3.  Explain OIDC.
4.  Explain workload identity federation.
5.  Explain why personal tokens are risky.
6.  Design secret management.
7.  Design production identity isolation.
8.  Design catalog isolation.
9.  Design permissions by environment.
10. Secure GitHub Actions.
11. Protect production branches.
12. Secure deployment approvals.
13. Audit deployments.
14. Detect suspicious deployment behavior.
15. Design credential revocation.

## Troubleshooting — 15

1.  Bundle validation fails.
2.  Deployment targets the wrong workspace.
3.  Production catalog appears in dev.
4.  Service principal lacks permission.
5.  OIDC fails.
6.  Wheel build fails.
7.  Wheel runtime dependency fails.
8.  Pipeline resource fails.
9.  Dev schedule runs.
10. Integration test fails.
11. Data diff fails.
12. Configuration drift appears.
13. Rollback fails.
14. Terraform overwrites Bundle state.
15. CI is unexpectedly expensive.

## Architecture — 15

1.  Design dev/staging/prod.
2.  Design a bundle repository.
3.  Design a job resource.
4.  Design a pipeline resource.
5.  Design wheel deployment.
6.  Design CI/CD.
7.  Design OIDC.
8.  Design service identities.
9.  Design data gates.
10. Design rollback.
11. Design Terraform boundaries.
12. Design drift prevention.
13. Design observability.
14. Design emergency change management.
15. Design a multi-team platform.

## Production Scenarios — 15

1.  Production schedule changed manually.
2.  Production deployment cannot authenticate.
3.  Deployment succeeds but revenue changes.
4.  Production data is wrong.
5.  Rollback restores code but not data.
6.  Dev writes production.
7.  Terraform and Bundle conflict.
8.  Developer leaves company but owns jobs.
9.  CI token leaks.
10. Integration tests consume too much compute.
11. Staging differs from production.
12. A release needs emergency promotion.
13. A schema change breaks consumers.
14. A previous bundle version must be restored.
15. An auditor asks which commit deployed a job.

------------------------------------------------------------------------

# 67. Senior Data Engineer Scenarios

## Scenario 1 --- Manual Production Schedule Change

> A developer manually changed the production job schedule. Git still
> contains the old schedule.

Correct reasoning:

``` text
Detect
 ↓
Preserve evidence
 ↓
Identify business impact
 ↓
Determine desired state
 ↓
Review emergency/manual change
 ↓
Restore through source-controlled deployment
 ↓
Prevent recurrence
```

Do not simply overwrite production without understanding why the change
occurred.

------------------------------------------------------------------------

## Scenario 2 --- CI Validates but Production Deploy Fails

Dev works.

Investigate:

``` text
Target
 ↓
Workspace
 ↓
Identity
 ↓
Permissions
 ↓
Production-only configuration
 ↓
Resource constraints
 ↓
Branch/mode requirements
```

------------------------------------------------------------------------

## Scenario 3 --- 7% Revenue Difference

Do not promote automatically.

Ask:

-   Is the difference expected?
-   Is source data different?
-   Did schema change?
-   Did joins change?
-   Did filtering change?
-   Is the baseline valid?

A deployment can be technically valid and analytically wrong.

------------------------------------------------------------------------

## Scenario 4 --- Halfway Deployment Failure

Determine:

``` text
What changed?
What did not change?
What is now inconsistent?
```

Then choose:

``` text
Forward fix
OR
Rollback
```

Do not assume rollback is always safer.

------------------------------------------------------------------------

## Scenario 5 --- Terraform for Everything

Ask:

-   Which resources are infrastructure?
-   Which resources are workloads?
-   Which team owns state?
-   Does Terraform support the desired lifecycle?
-   Does Bundle provide better project/workload semantics?

Choose an explicit ownership boundary.

------------------------------------------------------------------------

## Scenario 6 --- Personal Token Migration

Plan:

``` text
Inventory token usage
 ↓
Create deployment identity
 ↓
Configure federation
 ↓
Test in dev
 ↓
Test staging
 ↓
Switch production
 ↓
Revoke personal token
 ↓
Audit
```

Do not delete the old credential before proving the replacement works.

------------------------------------------------------------------------

## Scenario 7 --- Code Rollback but Data Is Wrong

Perform:

``` text
Code rollback
+
Data investigation
+
Recovery/reconciliation
+
Downstream validation
```

Code and data have different lifecycles.

------------------------------------------------------------------------

## Scenario 8 --- Shared Catalog

Explain:

> Identical code does not imply identical data authorization.

Development and production require different blast-radius boundaries.

------------------------------------------------------------------------

# 68. Common Misconceptions

### "Asset Bundles are just YAML."

Incomplete.

They combine:

``` text
Source
+
Configuration
+
Resources
+
Artifacts
+
Targets
+
Deployment
```

### "CI/CD means every commit goes to production."

False.

CI/CD means automated validation and controlled delivery.

### "Bundle validation proves the code is correct."

False.

Validation checks configuration/schema compatibility.

It does not prove business correctness.

### "Deployment success means data is correct."

False.

You need integration and data-quality validation.

### "Terraform and Asset Bundles are identical."

False.

They solve overlapping but different lifecycle problems.

### "Personal tokens are fine for CI."

Poor production default.

Prefer federated/service identities.

### "Dev and prod can share a catalog because code is identical."

Unsafe.

Data isolation is independent of code identity.

### "Rollback means Git revert."

Incomplete.

Git rollback may need to be followed by bundle redeployment and possibly
data recovery.

### "Code rollback automatically fixes data."

False.

Data may already have been modified.

### "Python wheels are unnecessary."

Not for production-grade reusable application logic.

### "Production resources can safely be edited manually."

Manual emergency changes may be necessary, but they create drift and
must be reconciled with the source of truth.

### "Unit tests are enough."

False.

Data Engineering requires integration and data validation.

### "Integration tests do not need real Databricks infrastructure."

Often false.

Some behaviors can only be validated against the actual platform.

### "Environment variables alone provide isolation."

False.

Isolation requires identity, workspace, catalog, permissions, compute
and operational controls.

------------------------------------------------------------------------

# 69. Mental Models

## Mental Model 1

**Git is the source of truth; the workspace is a deployment target.**

## Mental Model 2

**Bundle = code + configuration + resources + environment definition.**

## Mental Model 3

**Validate code before deploying; validate data before promoting.**

## Mental Model 4

**Developer identity builds; service identity deploys/runs production.**

## Mental Model 5

**Code rollback and data rollback are different operations.**

## Mental Model 6

**Terraform manages infrastructure; Bundles manage supported Databricks
workloads.**

## Mental Model 7

**The safest deployment is reproducible, reviewable, testable and
reversible.**

## Mental Model 8

**Environment differences should be configuration, not duplicated
business logic.**

## Mental Model 9

**A successful deployment is not necessarily a successful release.**

## Mental Model 10

**CI is part of the production security boundary.**

------------------------------------------------------------------------

# 70. Glossary

  ------------------------------------------------------------------------
  Term                                Definition
  ----------------------------------- ------------------------------------
  Asset Bundle                        Former Databricks name for
                                      Declarative Automation Bundles.

  Declarative Automation Bundle       Current Databricks terminology for
                                      the project deployment mechanism
                                      formerly called Asset Bundles.

  Bundle                              Deployable project representation
                                      containing
                                      source/config/resources/artifacts.

  Target                              Named deployment environment such as
                                      dev/staging/prod.

  `databricks.yml`                    Root bundle configuration file.

  Resource                            Deployable Databricks object such as
                                      a job or pipeline.

  Development mode                    Target mode with
                                      development-oriented defaults.

  Production mode                     Target mode with production-oriented
                                      safeguards/defaults.

  Deployment                          Applying bundle configuration to a
                                      target environment.

  Validation                          Checking bundle
                                      configuration/resource definitions
                                      before deployment.

  Artifact                            Build output such as a Python wheel.

  Python wheel                        Built Python package artifact.

  CI                                  Continuous Integration.

  CD                                  Continuous Delivery/Deployment.

  Git                                 Version-control system.

  Pull Request                        Reviewed proposed code/configuration
                                      change.

  GitHub Actions                      GitHub automation/CI/CD platform.

  Service principal                   Non-human service identity used for
                                      automation/runtime.

  OIDC                                OpenID Connect identity protocol
                                      used for federation.

  Workload identity federation        Trust mechanism allowing workloads
                                      to obtain short-lived access without
                                      long-lived secrets.

  Integration test                    Test against a real or
                                      representative integrated
                                      environment.

  Data diff                           Comparison of data outputs
                                      before/after a change.

  Configuration drift                 Difference between declared and
                                      actual environment state.

  Terraform                           Infrastructure-as-code tool with
                                      state-based resource management.

  Infrastructure as Code              Managing infrastructure through
                                      version-controlled definitions.

  Rollback                            Restoring a previous known-good
                                      software/configuration state.

  Promotion                           Moving a validated release through
                                      environments.

  Environment isolation               Preventing unintended interaction
                                      between dev/staging/prod.

  Deployment artifact                 Immutable or versioned output used
                                      in deployment.
  ------------------------------------------------------------------------

------------------------------------------------------------------------

# 71. Current-Documentation Safety

Databricks terminology and Bundle behavior can evolve.

Current documentation now uses:

> **Declarative Automation Bundles (formerly known as Databricks Asset
> Bundles).**

Before production implementation, verify current official documentation
for:

-   bundle configuration;
-   `databricks.yml`;
-   targets;
-   variables;
-   includes;
-   deployment modes;
-   development mode;
-   production mode;
-   presets;
-   resource definitions;
-   Python wheel artifacts;
-   CLI commands;
-   Git integration;
-   CI/CD integration;
-   service principals;
-   OIDC/workload federation;
-   supported authentication;
-   Terraform provider;
-   supported resource types;
-   deployment behavior;
-   rollback/redeployment semantics.

Also verify:

-   current GitHub Actions syntax;
-   current cloud identity federation guidance;
-   current Python packaging tooling;
-   current Databricks CLI version.

Never fabricate:

-   YAML fields;
-   CLI flags;
-   resource schemas;
-   OIDC claims;
-   authentication configuration;
-   Terraform resources;
-   GitHub Actions syntax;
-   deployment behavior;
-   rollback semantics.

If exact behavior is version/cloud dependent:

1.  explain the concept;
2.  identify the dependency;
3.  provide verified syntax only;
4.  instruct the learner to verify current official documentation before
    production.

------------------------------------------------------------------------

# 72. Connections to Previous and Next G4 Topics

## Topic 03 --- Notebooks, Git Folders, Project Structure

Topic 03 teaches professional code organization.

Topic 12 turns that organization into a deployable project.

``` text
Good Code Structure
 ↓
Bundle
 ↓
Deployment
```

## Topic 04 --- Unity Catalog

Bundle targets must point to governed catalogs and appropriate
permissions.

## Topic 07 --- Lakeflow Declarative Pipelines

Pipelines become deployable resources.

## Topic 08 --- Lakeflow Jobs

Jobs become deployable resources.

## Topic 09 --- Performance

Environment-specific compute affects:

-   performance;
-   reliability;
-   cost.

## Topic 10 --- Databricks SQL / AI-BI / Genie

Analytics assets may become part of broader deployment patterns where
supported.

## Topic 11 --- Delta Sharing / Marketplace

Data products and sharing infrastructure introduce additional
deployment/governance considerations.

## Topic 13 --- Cost Management

CI/CD must control test and deployment compute.

## Topic 14 --- MLflow / Feature Engineering

ML workloads also require reproducible deployment patterns.

------------------------------------------------------------------------

# 73. Production Capstone — Databricks Lakehouse CI/CD Platform

The learner must convert the previously built Databricks lakehouse into
a production delivery system.

Architecture:

``` text
Git Repository
      ↓
Asset Bundle
      ↓
┌──────────────────────────────┐
│ databricks.yml               │
│ targets/                     │
│ resources/                   │
│ src/                         │
│ tests/                       │
└──────────────┬───────────────┘
               ↓
              CI
       ┌───────┼────────┐
       ↓       ↓        ↓
     Lint    Tests    Validate
               ↓
          Deploy Dev
               ↓
       Integration Tests
               ↓
           Staging
               ↓
           Approval
               ↓
         Production
               ↓
        Monitoring/Audit
```

The capstone must deploy:

-   ingestion job;
-   declarative pipeline;
-   quality job;
-   Python wheel;
-   environment-specific catalogs;
-   environment-specific compute;
-   schedules;
-   permissions.

CI/CD must include:

-   unit tests;
-   bundle validation;
-   dev deployment;
-   integration tests;
-   staging;
-   production approval;
-   OIDC/service-principal authentication;
-   rollback.

The learner must demonstrate:

-   deliberate CI failure;
-   data-diff failure;
-   deployment rollback;
-   configuration-drift scenario;
-   production identity isolation.

Final documentation:

``` text
Architecture
Repository Structure
Bundle Design
Environment Strategy
Identity Strategy
CI Pipeline
CD Pipeline
Testing Strategy
Data Validation
Security Model
Rollback Strategy
Drift Strategy
Cost Strategy
Operational Runbooks
ADRs
```

------------------------------------------------------------------------

# 74. Production Quality Gate

A production release should pass:

``` text
Code Review
    ↓
Unit Tests
    ↓
Bundle Validation
    ↓
Security Checks
    ↓
Dev Deployment
    ↓
Integration Tests
    ↓
Data Quality / Data Diff
    ↓
Staging
    ↓
Approval
    ↓
Production
    ↓
Post-Deployment Verification
```

A release should not proceed merely because:

``` text
bundle deploy
```

returned success.

------------------------------------------------------------------------

# 75. Final Production Checklist

## Asset Bundles

-   [ ] I understand what a bundle is.
-   [ ] I understand current Declarative Automation Bundle terminology.
-   [ ] I understand `databricks.yml`.
-   [ ] I can define targets.
-   [ ] I can define resources.
-   [ ] I can validate a bundle.
-   [ ] I can deploy a bundle.
-   [ ] I can run a bundle resource.
-   [ ] I understand bundle destruction.

## Environments

-   [ ] I understand dev/staging/prod.
-   [ ] I can use development mode.
-   [ ] I understand production mode.
-   [ ] I can isolate catalogs.
-   [ ] I can override compute.
-   [ ] I can override schedules.
-   [ ] I can override permissions.

## Python

-   [ ] I can build a Python package.
-   [ ] I can build a wheel.
-   [ ] I can deploy the wheel.
-   [ ] I can connect it to a job.
-   [ ] I can test package logic independently.

## CI/CD

-   [ ] I understand CI.
-   [ ] I understand CD.
-   [ ] I can design Git workflows.
-   [ ] I can build CI validation.
-   [ ] I can deploy through environments.
-   [ ] I can run integration tests.
-   [ ] I can implement data-diff gates.

## Security

-   [ ] I understand service principals.
-   [ ] I understand OIDC.
-   [ ] I understand workload identity federation.
-   [ ] I avoid personal tokens in CI.
-   [ ] I understand least privilege.
-   [ ] I understand production identity isolation.
-   [ ] I can secure GitHub Actions.

## Production

-   [ ] I can detect configuration drift.
-   [ ] I can perform rollback.
-   [ ] I understand code vs data rollback.
-   [ ] I can compare data before promotion.
-   [ ] I can troubleshoot failed deployments.
-   [ ] I can decide between Bundles and Terraform.
-   [ ] I can trace production resources back to Git.

------------------------------------------------------------------------

# 76. Roadmap Coverage Audit

  ----------------------------------------------------------------------------------
  Roadmap Requirement    Covered?       Section        Hands-on?      Production
                                                                      Depth?
  ---------------------- -------------- -------------- -------------- --------------
  Bundle concept         Yes            7              Yes            Yes

  Project files          Yes            8              Yes            Yes

  Resource definitions   Yes            17--20         Yes            Yes

  Jobs                   Yes            18             Yes            Yes

  Pipelines              Yes            19             Yes            Yes

  YAML                   Yes            9              Yes            Yes

  `databricks.yml`       Yes            9              Yes            Yes

  Bundle name            Yes            9              Yes            Yes

  Targets                Yes            10--11         Yes            Yes

  Workspace settings     Yes            10             Yes            Yes

  Variables              Yes            9, 26          Yes            Yes

  `bundle validate`      Yes            15             Yes            Yes

  `bundle deploy`        Yes            15             Yes            Yes

  `bundle run`           Yes            15             Yes            Yes

  `bundle destroy`       Yes            15             Yes            Yes

  Development mode       Yes            12             Yes            Yes

  Per-user development   Yes            12             Yes            Yes
  behavior                                                            

  Paused development     Yes            12, 29         Yes            Yes
  schedules                                                           

  Production mode        Yes            13             Yes            Yes

  Service-principal      Yes            14, 37         Yes            Yes
  execution                                                           

  Guarded production     Yes            13             Yes            Yes
  settings                                                            

  Python wheels          Yes            21--25         Yes            Yes

  Bundle artifacts       Yes            24             Yes            Yes

  Jobs consuming wheels  Yes            24             Yes            Yes

  Catalog overrides      Yes            26--27         Yes            Yes

  Compute overrides      Yes            28             Yes            Yes

  Schedule overrides     Yes            29             Yes            Yes

  Permission overrides   Yes            30             Yes            Yes

  Git workflow           Yes            32             Yes            Yes

  CI/CD                  Yes            31--35         Yes            Yes

  GitHub Actions         Yes            33--34         Yes            Yes

  Service principals     Yes            37             Yes            Yes

  OIDC/workload          Yes            36             Yes            Yes
  federation                                                          

  Secrets/security       Yes            38, 55         Yes            Yes

  Unit testing           Yes            39             Yes            Yes

  Integration testing    Yes            40             Yes            Yes

  Data diffs             Yes            42--43         Yes            Yes

  Data quality gates     Yes            44             Yes            Yes

  Asset Bundles vs       Yes            47--49         Yes            Yes
  Terraform                                                           

  Configuration drift    Yes            45--46         Yes            Yes

  Production promotion   Yes            50--51         Yes            Yes

  Rollback               Yes            52--54         Yes            Yes

  Code vs data rollback  Yes            52--53         Yes            Yes

  Required               Yes            59             Yes            Yes
  `databricks.yml`                                                    
  exercise                                                            

  Required               Yes            59             Yes            Yes
  `.github/workflows/`                                                
  exercise                                                            

  16 progressive labs    Yes            60             Yes            Yes

  18 break/fix incidents Yes            61             Yes            Yes

  Production runbooks    Yes            62             Yes            Yes

  Decision matrices      Yes            63             Yes            Yes

  ADRs                   Yes            64             Yes            Yes

  Interview preparation  Yes            65             Yes            Yes

  Practice questions     Yes            66             Yes            Yes

  Senior scenarios       Yes            67             Yes            Yes

  Common misconceptions  Yes            68             Yes            Yes

  Mental models          Yes            69             Yes            Yes

  Glossary               Yes            70             Yes            Yes

  Current-doc safety     Yes            71             Yes            Yes

  Cross-topic            Yes            72             Yes            Yes
  connections                                                         

  Production capstone    Yes            73             Yes            Yes

  Production quality     Yes            74             Yes            Yes
  gate                                                                

  Final checklist        Yes            75             Yes            Yes
  ----------------------------------------------------------------------------------

**Roadmap coverage result: Complete against the supplied Topic 12
specification.**

------------------------------------------------------------------------

# 77. Final Operating Standard

Use this delivery loop:

``` text
CODE
 ↓
REVIEW
 ↓
UNIT TEST
 ↓
VALIDATE
 ↓
SECURITY CHECK
 ↓
DEPLOY DEV
 ↓
INTEGRATION TEST
 ↓
DATA DIFF / QUALITY
 ↓
STAGING
 ↓
APPROVAL
 ↓
PRODUCTION
 ↓
OBSERVE
 ↓
RECONCILE / ROLLBACK / FORWARD FIX
```

The production standard is:

> **Source-control the project, define environments explicitly, validate
> configuration, test code, test the deployed system, validate data,
> deploy through controlled identities, observe the release, and make
> rollback/recovery a designed capability rather than an emergency
> improvisation.**

The central mental model is:

``` text
Git
+
Bundle
+
Targets
+
Identity
+
Tests
+
Data Validation
+
CI/CD
+
Observability
+
Rollback
=
Production Databricks Delivery
```

------------------------------------------------------------------------

# 78. Final Validation Record

-   Exact requested filename: `12-databricks-asset-bundles-and-ci-cd.md`
-   Topic 12 authoritative requirements reviewed: Yes
-   Databricks current terminology incorporated: Yes
-   Bundle fundamentals: Complete
-   `databricks.yml`: Complete
-   Targets: Complete
-   Development mode: Complete
-   Production mode: Complete
-   CLI lifecycle: Complete
-   Jobs: Complete
-   Pipelines: Complete
-   Python wheels: Complete
-   Per-target overrides: Complete
-   Catalog isolation: Complete
-   Compute overrides: Complete
-   Schedule overrides: Complete
-   Permission overrides: Complete
-   Git workflow: Complete
-   CI/CD: Complete
-   GitHub Actions: Complete
-   Service principals: Complete
-   OIDC/workload identity federation: Complete
-   Secrets/security: Complete
-   Unit testing: Complete
-   Integration testing: Complete
-   Data diffs: Complete
-   Data quality gates: Complete
-   Bundles vs Terraform: Complete
-   Configuration drift: Complete
-   Production promotion: Complete
-   Rollback: Complete
-   Code vs data rollback: Complete
-   Hands-on labs: 16
-   Required `databricks.yml` + `.github/workflows/` exercise: Complete
-   Break/Fix incidents: 18
-   Production runbooks: 6
-   Decision matrices: 4
-   ADRs: 6
-   Interview preparation: 75 questions
-   Practice questions: 110 questions
-   Senior scenarios: 8
-   Production capstone: Complete
-   Roadmap coverage audit: Complete
-   Placeholder tokens: None
-   Other roadmap files modified: None
