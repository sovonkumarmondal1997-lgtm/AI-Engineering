# CI Pipelines for Data Projects

**Stage 2 — Python for Data Engineering**  
**Module 2.18 — Containers, Infrastructure, and CI/CD for Data**  
**Phase D — Delivering Changes**  
**Topic 05 — CI Pipelines for Data Projects**

> **Module outcome:** Build production-grade Continuous Integration (CI) for Data Engineering repositories so that Python, DAGs, SQL, data contracts, dbt, integration environments, container images, and infrastructure changes are automatically validated before merge.

---

## 1. What You Will Learn

By the end of this module, you should be able to:

- explain CI and distinguish it from CD, deployment, and release;
- build GitHub Actions workflows using triggers, jobs, steps, runners, logs, outputs, and artifacts;
- create reproducible Python CI with `uv`, Ruff, type checking, and pytest;
- validate Airflow DAG imports, structure, and policies;
- lint SQL and validate data contracts and schema compatibility;
- use Pandera for DataFrame schema validation;
- understand and implement dbt Slim CI using state-aware selection, isolated schemas, and `--defer`;
- run integration tests against the Docker Compose stack from Topic 02;
- build, scan, and SHA-tag container images;
- validate Terraform with formatting, validation, security checks, and plans;
- use OIDC federation instead of long-lived cloud credentials;
- improve CI speed with caching, parallel jobs, matrices, path filters, and selective testing;
- harden CI supply chains with SHA-pinned Actions, least-privilege permissions, dependency scanning, and secret scanning;
- protect the main branch with required checks;
- use `pre-commit` for fast local feedback;
- understand the production principle **build once, store the artifact, and deploy the exact artifact later**.

---

# 2. Why CI Exists

Imagine a repository containing:

```text
Python pipeline code
Airflow DAGs
SQL
dbt models
Spark code
Dockerfiles
Terraform
Data contracts
```

A developer changes one file.

Without CI, the team may depend on:

```text
"It works on my machine."
```

That is dangerous because a change can fail in ways the developer did not observe locally.

### Without CI

```text
Developer A
    ↓
Writes code
    ↓
"It works on my machine"
    ↓
Merge
    ↓
Production failure
```

### With CI

```text
Developer
    ↓
Commit
    ↓
Pull Request
    ↓
Automated Checks
    ↓
Failures Block Merge
    ↓
Review
    ↓
Merge
```

CI turns known failure modes into repeatable automated checks.

The central question is:

> **Is this change safe enough to merge?**

CI does **not** prove that production can never fail. It increases confidence by automatically checking the failure modes the engineering team knows how to test.

---

# 3. Why Data Engineering CI Is Different

A normal Python application might primarily need:

```text
lint
type checking
unit tests
```

A data platform has additional correctness dimensions:

```text
Python code
    +
DAG structure
    +
SQL
    +
Data contracts
    +
Schemas
    +
DataFrame validation
    +
dbt models
    +
Databases/object storage/streaming systems
    +
Container images
    +
Infrastructure
```

Therefore:

```text
Software CI
    +
Data Platform Validation
    =
Data Engineering CI
```

The goal is not to make CI complicated for its own sake. The goal is to catch the failure modes that are specific to a data system.

---

# 4. CI Mental Model

Use this mental model:

```text
Git Repository
      ↓
Git Event
      ↓
GitHub Actions Workflow
      ↓
Jobs
      ↓
Steps
      ↓
Runner
      ↓
Tools / Tests
      ↓
Artifacts / Logs
      ↓
Pass / Fail
```

For pull requests:

```text
Pull Request
      ↓
Quality Gates
      ↓
Review
      ↓
Merge
```

## 4.1 Source Control vs CI vs CD

| Concept | Main question |
|---|---|
| Source control | What changed? |
| CI | Is the change valid and safe enough to merge? |
| CD | How should an approved artifact move toward deployment? |
| Deployment | How is an artifact installed into an environment? |
| Release | When and under what controls is a version made available? |

This module focuses on CI and only introduces the delivery concepts necessary to establish good CI/CD foundations.

---

# 5. Continuous Integration Fundamentals

Continuous Integration means integrating changes frequently and validating them automatically.

The important properties are:

- frequent integration;
- automated validation;
- fast feedback;
- reproducible execution;
- deterministic dependency installation;
- failing fast where appropriate;
- explicit quality gates.

A useful model is:

```text
Small change
    ↓
Push / Pull Request
    ↓
Automated validation
    ↓
Fast feedback
    ↓
Fix immediately
    ↓
Merge
```

The smaller the change, the easier it generally is to understand and repair a failure.

---

# 6. GitHub Actions Fundamentals

GitHub Actions represents CI as YAML workflows.

A simplified structure is:

```text
.github/
└── workflows/
    └── ci.yml
```

A workflow contains:

```text
Workflow
  ├── Event / Trigger
  ├── Job
  │    ├── Step
  │    ├── Step
  │    └── Step
  └── Job
```

Important concepts:

| Term | Meaning |
|---|---|
| Workflow | YAML-defined automation |
| Event | Repository event that starts a workflow |
| Trigger | Configuration specifying when it runs |
| Job | A unit of execution |
| Step | Individual command or Action |
| Runner | Machine/environment executing a job |
| Action | Reusable automation component |
| Logs | Execution output used for inspection |
| Artifact | Persisted output from a workflow |
| Status | Success, failure, cancelled, etc. |

---

# 7. Push, Pull Request, Schedule, and Manual Triggers

## 7.1 Push

```yaml
on:
  push:
    branches:
      - main
```

This runs after changes are pushed to the selected branch.

## 7.2 Pull Request

```yaml
on:
  pull_request:
    branches:
      - main
```

This is central to merge protection.

A typical pattern is:

```text
Developer branch
      ↓
Pull Request
      ↓
CI
      ↓
Required checks
      ↓
Review
      ↓
Merge
```

## 7.3 Scheduled workflows

Scheduled workflows are useful for recurring validation that does not need to run on every pull request.

For example:

```yaml
on:
  schedule:
    - cron: "17 2 * * *"
```

Use scheduled jobs for things such as broader regression validation where appropriate.

## 7.4 Manual execution

```yaml
on:
  workflow_dispatch:
```

This allows an authorized person to start the workflow manually.

---

# 8. Your First GitHub Actions Workflow

A minimal workflow:

```yaml
name: CI

on:
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@<PINNED_COMMIT_SHA>

      - name: Run tests
        run: |
          echo "Run project tests here"
```

The important sequence is:

```text
Event
  ↓
Workflow
  ↓
Job
  ↓
Runner
  ↓
Checkout
  ↓
Commands
```

In a real production repository, pin third-party Actions to reviewed commit SHAs rather than relying on mutable version tags.

---

# 9. Workflow Organization

A data platform can eventually have:

```text
.github/
└── workflows/
    ├── ci.yml
    ├── dbt-ci.yml
    ├── integration.yml
    ├── images.yml
    └── infra.yml
```

A reasonable responsibility split is:

### `ci.yml`

Fast application and data-code checks:

- Ruff;
- formatting;
- type checking;
- pytest;
- DAG validation;
- SQL checks;
- contracts;
- Pandera.

### `dbt-ci.yml`

dbt-specific state-aware validation.

### `integration.yml`

Docker Compose-based integration tests.

### `images.yml`

Container build, scan, tagging, and publishing.

### `infra.yml`

Terraform formatting, validation, security scanning, and plan.

One giant workflow is not automatically wrong, but separating responsibilities can make ownership, debugging, permissions, and execution behavior clearer.

---

# 10. Jobs, Steps, and Dependencies

Jobs can execute independently:

```yaml
jobs:
  lint:
    ...

  typecheck:
    ...

  unit-tests:
    ...
```

This enables parallelism.

A downstream job can depend on earlier jobs:

```yaml
jobs:
  lint:
    ...

  tests:
    ...

  integration:
    needs:
      - lint
      - tests
    ...
```

The resulting graph is:

```text
lint ─────┐
          ├──> integration
tests ────┘
```

`needs:` expresses an execution dependency.

Do not add dependencies merely because jobs appear conceptually related. Add them when the later job actually depends on the earlier result or artifact.

---

# 11. Runners

A runner is the execution environment for a job.

For example:

```yaml
runs-on: ubuntu-latest
```

A hosted runner should be treated as **ephemeral**, not as a persistent server.

Do not assume:

```text
Yesterday's runner state
        ↓
Today's runner state
```

Instead design for:

```text
Clean runner
    ↓
Checkout
    ↓
Install exact dependencies
    ↓
Run checks
    ↓
Persist required artifacts/logs
    ↓
Runner discarded
```

This improves reproducibility.

---

# 12. Reading CI Logs and Debugging

A failed workflow should be debugged systematically.

```text
Job failed
    ↓
Find failed job
    ↓
Find failed step
    ↓
Read the first meaningful error
    ↓
Reproduce locally
    ↓
Fix
    ↓
Push
    ↓
CI reruns
```

Do not start by reading hundreds of lines of successful output.

Look for:

- the failed step;
- the command that returned a non-zero exit code;
- the first meaningful exception;
- dependency/version information;
- environment assumptions;
- service connection errors.

A common mistake is diagnosing the last error rather than the first causal failure.

---

# 13. Production Python CI

A production-oriented Python CI pipeline should validate at least:

```text
Checkout
   ↓
Python setup
   ↓
uv
   ↓
Locked dependencies
   ↓
Cache
   ↓
Ruff
   ↓
Format check
   ↓
Type check
   ↓
pytest
   ↓
Coverage / test results
```

Example:

```yaml
name: Python CI

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  python:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@<PINNED_COMMIT_SHA>

      - name: Set up Python
        uses: actions/setup-python@<PINNED_COMMIT_SHA>
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@<PINNED_COMMIT_SHA>
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Install locked dependencies
        run: uv sync --locked

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Type check
        run: uv run mypy src

      - name: Tests
        run: uv run pytest -q
```

> Replace placeholder Action commit SHAs with the exact reviewed commits selected by your organization. The example intentionally does not invent a SHA.

---

# 14. Why `uv` Matters in CI

CI should not silently resolve a different dependency graph every time.

A reproducible relationship is:

```text
pyproject.toml
       +
uv.lock
       +
same Python version
       +
same CI procedure
       =
more reproducible CI
```

The important principle is:

```bash
uv sync --locked
```

The lock file should be treated as part of the reproducibility boundary.

## 14.1 What Can Go Wrong

Without locked installation:

```text
Monday:
dependency A → version X

Friday:
dependency A → version Y

CI result changes
```

With a lock file, the intended dependency graph is explicit.

---

# 15. Dependency Caching with `uv`

Caching reduces repeated dependency installation.

The important pieces are:

- cache key;
- lock-file dependency;
- invalidation;
- reproducibility.

A cache must accelerate installation, not determine which versions are installed.

Good principle:

```text
Lock file
   ↓
Dependency identity
   ↓
Cache reuse
```

Not:

```text
Cache
   ↓
Whatever happens to be installed
```

If the dependency graph changes, the cache should naturally invalidate or refresh.

---

# 16. Ruff in CI

Ruff provides two distinct checks:

```bash
ruff check .
```

and:

```bash
ruff format --check .
```

They are related but not identical.

### Linting

Finds code-quality and correctness issues covered by configured rules.

### Formatting

Checks whether files conform to the configured formatting style.

A useful distinction is:

```text
Linting
  ≠
Formatting
```

CI should enforce the repository's agreed standard rather than relying only on developer discipline.

---

# 17. Type Checking

Static type checking catches a different class of defects from runtime tests.

For example:

```python
def load_count() -> int:
    return "100"
```

A runtime test may never exercise this function. A type checker can identify the incompatible return type before the code reaches runtime.

The quality gates therefore have different purposes:

```text
Ruff
  → code quality/style

Type checker
  → static type consistency

pytest
  → runtime behavior
```

Do not turn this module into a full Python typing course; the goal is to understand type checking as a CI gate.

---

# 18. Pytest in CI

Run:

```bash
pytest
```

Important concepts include:

- test discovery;
- deterministic tests;
- test isolation;
- exit codes;
- coverage;
- failure behavior.

A simplified model:

```text
pytest
   ↓
All selected tests
   ↓
Pass → exit 0
Fail → non-zero exit
```

CI interprets the exit status as a quality signal.

Coverage can be useful, but a high percentage alone does not guarantee good tests.

---

# 19. Data Engineering CI

Python checks are necessary but insufficient.

A Data Engineering repository may require:

```text
Python
DAGs
SQL
Contracts
Schemas
DataFrames
dbt
Integration systems
Images
Infrastructure
Security
```

Therefore a production pipeline should be layered.

```text
Fast software checks
        ↓
Data-system checks
        ↓
Integration checks
        ↓
Image / infrastructure checks
        ↓
Required checks
```

---

# 20. Airflow DAG Validation

A broken DAG should not reach production.

CI should test:

- DAG import;
- DAG structure;
- task dependencies;
- required policies;
- accidental cycles;
- invalid configuration;
- policy violations.

## 20.1 DAG Import Test

A simplified pattern:

```python
from pathlib import Path
import importlib.util


def import_python_file(path: Path) -> None:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot import {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def test_dags_import():
    dag_dir = Path("dags")

    for path in dag_dir.glob("*.py"):
        import_python_file(path)
```

In a real Airflow repository, use the project's established Airflow loading mechanism and test fixtures so that plugins, providers, configuration, and DAG discovery behave consistently with the intended runtime.

The core principle is:

```text
DAG change
   ↓
Import validation
   ↓
Failure
   ↓
PR blocked
```

---

# 21. DAG Structure and Policy Tests

Importing a DAG is not enough.

You may also validate properties such as:

```python
def test_required_task_exists():
    assert "load_to_warehouse" in dag.task_ids
```

Or organizational policy:

```python
def test_dag_has_owner():
    assert dag.owner
```

Or task-level expectations:

```python
def test_dag_has_no_unexpected_task_count():
    assert len(dag.task_ids) <= 50
```

The exact policies depend on the platform.

The important distinction is:

```text
Import test
    → Can the DAG load?

Structure/policy test
    → Does the DAG conform to platform rules?
```

---

# 22. SQL Linting

SQL deserves automated validation just like Python.

SQL checks can cover:

- formatting;
- syntax/quality conventions;
- naming conventions;
- dialect-specific rules;
- unsafe patterns where supported.

The specific SQL linter is a tooling choice. SQLFluff is one practical example:

```bash
sqlfluff lint sql/
```

A CI stage might be:

```yaml
- name: SQL lint
  run: uv run sqlfluff lint sql/
```

Do not confuse linting with executing every query against production-like data. Linting is a fast static check.

---

# 23. Data Contracts

A data contract defines expectations between a producer and consumer.

```text
Producer
    ↓
Data Contract
    ↓
Consumer
```

A contract can specify:

- column names;
- data types;
- required fields;
- semantic expectations;
- compatibility rules.

CI can compare the proposed change against those expectations.

For example:

```text
Existing contract:
customer_id: integer
email: string
created_at: timestamp
```

A proposed change that removes `customer_id` may be breaking.

---

# 24. Schema Compatibility

Schema changes can be classified conceptually.

### Potentially compatible

```text
Add optional column
```

### Potentially breaking

```text
Remove required column
Change type
Rename column
Make optional field required
```

Exact rules depend on the contract technology and consumer behavior.

A useful CI pattern is:

```text
Current schema
       +
Proposed schema
       ↓
Compatibility check
       ↓
Pass / Fail
```

Do not assume that every added field is harmless; downstream consumers may use strict schemas.

---

# 25. Pandera

Pandera provides schema validation for DataFrames.

A simple example:

```python
import pandas as pd
import pandera.pandas as pa


class CustomerSchema(pa.DataFrameModel):
    customer_id: int
    email: str
    age: int


def test_customer_dataframe_schema():
    df = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "email": ["a@example.com", "b@example.com"],
            "age": [31, 42],
        }
    )

    CustomerSchema.validate(df)
```

The mental model is:

```text
Test DataFrame
      ↓
Pandera Schema
      ↓
Pass / Fail
```

Pandera is useful when the pipeline's correctness depends on DataFrame shape, types, and constraints.

---

# 26. dbt Slim CI

Running an entire dbt project for every pull request can become:

- slow;
- expensive;
- unnecessary.

Suppose:

```text
model_a
   ↓
model_b
   ↓
model_c
```

A change to `model_b` may require validating `model_b` and affected descendants, rather than rebuilding unrelated parts of the graph.

The conceptual model is:

```text
Changed dbt models
       +
Affected descendants
       ↓
Relevant CI subset
```

This is commonly called **Slim CI**.

---

# 27. dbt State-Aware Selection

Slim CI relies on state.

Conceptually:

```text
Previous known-good state
        +
Current PR state
        ↓
Detect modifications
```

dbt's state-aware selection can identify modified resources and their relationships.

The exact selection syntax should be aligned with the dbt version used by the project.

A typical pattern uses a state artifact:

```bash
dbt ls \
  --select state:modified+ \
  --state path/to/previous-state
```

The `+` means the selection can include descendants.

The important idea is not the command memorization. It is:

```text
Compare states
   ↓
Identify relevant graph changes
   ↓
Validate the smallest safe subset
```

---

# 28. Isolated dbt CI Schemas

A pull request should not write test models into a shared production schema.

Instead:

```text
Production
    │
    │ existing state
    ▼
CI reference/defer
    ▲
    │
Pull Request
    │
    ▼
Isolated CI schema
```

For example:

```text
analytics_ci_pr_1842
```

The exact naming convention is a platform decision.

Isolation prevents one developer's validation from interfering with another developer's work or production data.

---

# 29. dbt `--defer`

`--defer` is closely related to state-aware CI but is **not** simply another name for "run only changed models."

The concepts are:

```text
Selection
   ↓
Which resources should be processed?

State
   ↓
What previous project state is known?

Defer
   ↓
Where should references to unbuilt resources resolve?
```

A conceptual command might be:

```bash
dbt build \
  --select state:modified+ \
  --state ./state \
  --defer \
  --target ci
```

This can allow unchanged upstream resources to be referenced from an existing state rather than rebuilt unnecessarily.

The precise behavior depends on dbt version, project configuration, target configuration, and available state artifacts.

---

# 30. dbt Slim CI Workflow

A practical architecture:

```text
Pull Request
    ↓
Detect dbt changes
    ↓
Prepare isolated schema
    ↓
Obtain trusted state artifact
    ↓
Select modified models + descendants
    ↓
Build / test
    ↓
Destroy / clean CI schema
```

The key safety property is isolation.

The key performance property is state-aware selection.

The key correctness property is that selection and defer are configured together rather than treating Slim CI as "just run changed files."

---

# 31. Integration Testing

Unit tests validate component behavior.

Integration tests validate components working together.

```text
Unit Test
    ↓
Individual component behavior

Integration Test
    ↓
Multiple components working together
```

A data platform may integrate:

- PostgreSQL;
- object storage;
- Kafka;
- Schema Registry;
- pipeline services.

The Compose environment from Topic 02 is a natural local integration environment.

Do not re-teach Docker Compose here. The purpose is to show how CI consumes that environment.

---

# 32. Compose-Based CI Integration Tests

A common flow is:

```text
CI Runner
    ↓
docker compose up
    ↓
Health / readiness
    ↓
Integration tests
    ↓
Collect logs
    ↓
docker compose down
```

A simplified workflow:

```yaml
name: Integration

on:
  pull_request:

permissions:
  contents: read

jobs:
  integration:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@<PINNED_COMMIT_SHA>

      - name: Start integration stack
        run: docker compose -f compose/compose.yaml up -d --wait

      - name: Run integration tests
        run: uv run pytest tests/integration -q

      - name: Show logs on failure
        if: failure()
        run: docker compose -f compose/compose.yaml logs --no-color

      - name: Tear down
        if: always()
        run: docker compose -f compose/compose.yaml down -v
```

`--wait` is useful when supported by the Compose version and service health checks are correctly defined.

The important principle is:

```text
Start
→ Wait for readiness
→ Test
→ Diagnose
→ Clean up
```

---

# 33. Service Containers vs Full Integration Environments

Three levels are useful:

| Level | Purpose |
|---|---|
| Unit tests | Individual function/component |
| Service containers | One or a few real dependencies |
| Full integration environment | Multiple platform services working together |

For example:

```text
Unit:
test transformation function

Service container:
test PostgreSQL repository code

Full environment:
pipeline → Kafka → processing → PostgreSQL/object storage
```

Use the smallest environment that provides meaningful confidence.

---

# 34. Image Building in CI

The CI pipeline should build the same artifact intended for later use.

```text
Git Commit
    ↓
Docker Build
    ↓
Image
    ↓
Scan
    ↓
Push / Store
```

A simplified Buildx example:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@<PINNED_COMMIT_SHA>

- name: Build image
  run: |
    docker build \
      --tag ghcr.io/example/data-pipeline:${GITHUB_SHA} \
      .
```

The exact registry and authentication mechanism depend on the platform.

---

# 35. SHA-Tagged Images

Avoid treating:

```text
my-pipeline:latest
```

as the identity of a production artifact.

A commit-specific tag provides traceability:

```text
my-pipeline:<commit-sha>
```

For example:

```text
my-pipeline:4f2d8e...
```

The relationship becomes:

```text
Git commit
    ↕
Image tag / digest
```

Benefits:

- traceability;
- auditability;
- easier rollback;
- reproducibility;
- debugging.

A tag can still be mutable, so a registry digest is the strongest immutable content identity.

---

# 36. Image Scanning

A CI image pipeline can be:

```text
Build
 ↓
Scan
 ↓
Finding?
 ├── Yes → Fix → Rebuild → Rescan
 └── No  → Push
```

Trivy is a common example:

```bash
trivy image \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  ghcr.io/example/data-pipeline:${GITHUB_SHA}
```

Image scanning can identify:

- OS package vulnerabilities;
- Python dependency vulnerabilities;
- other known vulnerable components.

Scanning is not proof of security. It is one control in a broader supply-chain security strategy.

---

# 37. Terraform in CI

Topic 04 established Terraform fundamentals. Here the question is:

> How should infrastructure changes be validated before merge?

A practical quality gate is:

```text
terraform fmt
      ↓
terraform validate
      ↓
security scan
      ↓
terraform plan
      ↓
review
```

Example:

```yaml
- name: Terraform format check
  run: terraform fmt -check -recursive

- name: Terraform init
  run: terraform init -backend=false

- name: Terraform validate
  run: terraform validate

- name: Terraform plan
  run: terraform plan -out=tfplan
```

A production repository should configure provider versions, backend behavior, credentials, and variables explicitly rather than relying on hidden runner state.

---

# 38. Terraform Plan in Pull Requests

The useful workflow is:

```text
Pull Request
    ↓
Terraform plan
    ↓
Plan summary
    ↓
Reviewer sees infrastructure changes
    ↓
Approve / reject
```

This makes destructive changes visible before they are applied.

For example, a reviewer should be able to identify a plan containing:

```text
~ update
+ create
- destroy
-/+ replacement
```

A plan that unexpectedly destroys a critical data resource should trigger investigation before merge.

Actual production application and environment promotion belong to later delivery topics.

---

# 39. OIDC Federation

One of the most important CI security principles is:

> **Cloud access should not require storing long-lived cloud access keys in CI whenever federation is available.**

### Older pattern

```text
GitHub Actions
      ↓
Long-lived cloud access key
      ↓
Stored secret
```

### Better pattern

```text
GitHub Actions
      ↓
OIDC identity token
      ↓
Cloud identity provider
      ↓
Short-lived role credentials
      ↓
Cloud API
```

OIDC means OpenID Connect.

The CI platform establishes an identity assertion, and the cloud provider validates that assertion against a configured trust policy.

---

# 40. OIDC Security

OIDC is not automatically secure simply because it is OIDC.

The trust relationship should be narrow.

Useful restrictions include:

- repository identity;
- organization identity;
- branch;
- environment;
- workflow identity;
- audience;
- subject claims;
- minimal cloud permissions.

The principle is:

```text
Only this repository
+
Only this workflow/environment
+
Only required permissions
=
safer CI cloud access
```

Short-lived credentials reduce exposure compared with static long-lived keys.

Do not turn this section into a cloud secrets-manager implementation. Topic 07 covers that domain in depth.

---

# 41. CI Performance

CI speed affects engineering throughput.

A slow pipeline creates:

```text
Slow feedback
    ↓
Developers stop waiting
    ↓
PRs stay open
    ↓
Changes accumulate
    ↓
Risk increases
```

The main optimization techniques in this roadmap are:

- dependency caching;
- parallel jobs;
- matrix builds;
- path filters;
- selective tests;
- avoiding duplicate work.

Optimization must not weaken safety.

---

# 42. Dependency Caching

Cache expensive, reproducible dependencies.

A useful cache key includes the dependency definition or lock file.

For example, `uv` can use:

```yaml
- uses: astral-sh/setup-uv@<PINNED_COMMIT_SHA>
  with:
    enable-cache: true
    cache-dependency-glob: "uv.lock"
```

The important concepts are:

```text
Cache key
   ↓
Cache hit / miss
   ↓
Dependency reuse
```

Incorrect cache design can create stale or misleading environments, so the cache must never become the source of truth for dependency versions.

---

# 43. Parallel Jobs

Independent jobs can run simultaneously.

```text
             ┌── lint
             │
Pull Request ├── typecheck
             │
             ├── unit tests
             │
             └── SQL checks
```

If integration depends on all of them:

```text
lint ─────┐
types ────┤
tests ────┼──> integration
SQL ──────┘
```

Use `needs:` only for genuine dependencies.

Parallelism reduces elapsed time but may increase concurrent compute usage.

---

# 44. Matrix Builds

A matrix prevents repetitive YAML when the same job must run across multiple configurations.

Example:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version:
          - "3.11"
          - "3.12"
          - "3.13"

    steps:
      - uses: actions/checkout@<PINNED_COMMIT_SHA>

      - uses: actions/setup-python@<PINNED_COMMIT_SHA>
        with:
          python-version: ${{ matrix.python-version }}

      - run: python --version
```

Use matrices when compatibility coverage justifies the extra CI cost.

---

# 45. Path Filters

Not every change needs every expensive validation.

A conceptual mapping:

```text
src/**       → Python CI
dbt/**       → dbt CI
spark/**     → Spark tests
infra/**     → Terraform plan
```

Path filtering can reduce unnecessary work.

However:

> **Optimization must never accidentally skip a required safety check.**

For example, a change to a shared Python library used by dbt tooling may affect more than the path appears to indicate.

When in doubt, prefer broader validation over a dangerously narrow filter.

---

# 46. Selective Test Execution

A mature pipeline can classify checks:

```text
Fast checks
    ↓
Unit tests
    ↓
Targeted integration
    ↓
Full validation when necessary
```

For example:

```text
Every PR:
lint
types
unit tests

PR when dbt changes:
dbt Slim CI

PR when infrastructure changes:
Terraform plan

Merge:
image build/push

Nightly:
full regression
```

These are examples, not universal policies. Risk, criticality, and repository architecture determine the correct frequency.

---

# 47. Supply-Chain Security

CI itself is part of the software supply chain.

```text
Repository
    ↓
Third-party Actions
    ↓
Dependencies
    ↓
Build tools
    ↓
Images
    ↓
Artifacts
    ↓
Deployment
```

A compromised component anywhere in this chain can affect the final system.

Therefore CI must protect:

- source;
- Actions;
- dependencies;
- credentials;
- build process;
- artifacts.

---

# 48. Pin Third-Party Actions by Commit SHA

A mutable reference such as:

```yaml
uses: some/action@v4
```

is convenient but does not identify one immutable commit.

A stronger pattern is:

```yaml
uses: some/action@<FULL_REVIEWED_COMMIT_SHA> # v4
```

The SHA should be selected and reviewed by the organization.

SHA pinning helps prevent unexpected movement of a referenced Action, but it does **not** eliminate all supply-chain risks. The pinned commit itself still needs to be trusted and periodically reviewed for updates and vulnerabilities.

---

# 49. Least-Privilege Workflow Permissions

Start with narrow permissions:

```yaml
permissions:
  contents: read
```

Only grant additional permissions when the workflow genuinely needs them.

Conceptually:

```text
Over-permissioned workflow
        ↓
Large blast radius

Least privilege
        ↓
Smaller blast radius
```

Permissions can be scoped at workflow or job level.

For example, a build job may only need repository read access while a publishing job needs additional registry-related permissions.

---

# 50. Dependency Scanning

Dependency scanning looks for known vulnerabilities in dependencies, including transitive dependencies.

The dependency graph may be:

```text
Your package
   ↓
Direct dependency
   ↓
Transitive dependency
   ↓
Vulnerable version
```

Lock files help make the dependency graph explicit.

Dependency scanning is different from:

```text
Linting          → code quality
Type checking    → static consistency
Unit tests       → runtime behavior
Image scanning   → image/package vulnerabilities
```

Each catches a different class of problem.

---

# 51. Secret Scanning

A common failure is accidentally committing a credential.

```text
Developer
    ↓
Secret enters file
    ↓
Git commit
    ↓
Repository
```

Use defense in depth:

```text
Developer machine
       ↓
pre-commit
       ↓
Git
       ↓
CI secret scanning
```

Gitleaks is one example of a secret-scanning tool:

```bash
gitleaks detect
```

If a real credential is exposed, scanning is not enough. The credential must be revoked/rotated according to the organization's incident process.

Do not implement cloud secret managers here; that is Topic 07.

---

# 52. Protected Branches

CI becomes meaningful as a merge gate only when the repository's branch controls enforce it.

A typical policy is:

```text
CI fails
    ↓
Merge blocked
```

and:

```text
CI passes
+
Required review
    ↓
Merge allowed
```

Protected branches can require:

- required status checks;
- pull-request review;
- up-to-date branches where appropriate;
- restrictions on direct pushes.

---

# 53. Required Checks

A mature Data Engineering repository might require:

```text
✓ lint
✓ typecheck
✓ unit-tests
✓ data-contracts
✓ dbt-ci
✓ integration-tests
✓ image-scan
✓ terraform-plan
```

The exact set depends on changed scope and repository policy.

Required checks reduce the possibility of bypassing known safety controls.

---

# 54. `pre-commit`

`pre-commit` provides fast local feedback before code reaches shared CI.

```text
Developer
    ↓
pre-commit
    ↓
Fast local feedback
    ↓
Commit
    ↓
CI
```

Possible hooks include:

- formatting;
- linting;
- secret scanning;
- YAML validation;
- Terraform formatting.

Example configuration:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: <PINNED_REVIEWED_REVISION>
    hooks:
      - id: ruff
      - id: ruff-format
```

The exact hook revisions should be pinned and reviewed by the project.

Remember:

```text
pre-commit ≠ CI
```

Local hooks provide early feedback. CI remains the authoritative shared gate.

---

# 55. Build Once, Store Artifact, Deploy Exact Artifact

A dangerous delivery pattern is:

```text
Dev
  ↓
Rebuild

Staging
  ↓
Rebuild

Production
  ↓
Rebuild
```

Each rebuild introduces another opportunity for dependency or build differences.

The stronger principle is:

```text
Source
  ↓
Build ONCE
  ↓
Artifact
  ↓
Store
  ↓
Later delivery stages
```

Possible artifacts include:

- Docker image;
- Python wheel;
- dbt package.

The relationship should be traceable:

```text
Git commit
    ↓
CI run
    ↓
Artifact
    ↓
Artifact identifier
```

This enables:

- auditability;
- debugging;
- reproducibility;
- rollback.

Topic 06 will cover environment promotion in depth. Here, the important CI foundation is that CI creates a traceable artifact rather than repeatedly rebuilding one later.

---

# 56. Complete CI Architecture

A production-oriented architecture can be visualized as:

```text
                         Git Repository
                              │
                              ▼
                         Pull Request
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        Python CI        Data Quality      Security
             │                │                │
       ┌─────┼─────┐      ┌───┼────┐      ┌───┼────┐
       │     │     │      │   │    │      │   │    │
     Ruff  Types  Pytest  DAG SQL Contract Deps Secrets
                                      │
                                      ▼
                                dbt Slim CI
                                      │
                                      ▼
                              Integration Tests
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                    Image Build              Terraform Plan
                         │                         │
                         ▼                         ▼
                    Image Scan                 IaC Scan
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                               Required Checks
                                      │
                                      ▼
                                    Review
                                      │
                                      ▼
                                    Merge
```

The goal is not that every check must execute in one serial chain. Independent branches should run in parallel when appropriate.

---

# 57. Recommended Workflow Files

```text
.github/workflows/
├── ci.yml
├── dbt-ci.yml
├── integration.yml
├── images.yml
└── infra.yml
```

## 57.1 `ci.yml`

Should cover:

- Ruff;
- format checks;
- type checking;
- pytest;
- coverage;
- DAG tests;
- contract/schema checks;
- SQL lint;
- Pandera.

Use parallel jobs where practical.

## 57.2 `dbt-ci.yml`

Should cover:

- isolated schema;
- modified models;
- descendants;
- state;
- defer;
- dbt tests.

## 57.3 `integration.yml`

Should cover:

- Compose startup;
- health/readiness;
- integration tests;
- teardown;
- logs on failure.

## 57.4 `images.yml`

Should cover:

- image build;
- image scan;
- SHA tagging;
- publishing on the appropriate event.

## 57.5 `infra.yml`

Should cover:

- Terraform fmt;
- validate;
- security scan;
- plan;
- OIDC where cloud access is required;
- plan summary/review.

---

# 58. Example `ci.yml` Architecture

A realistic structure is:

```yaml
name: CI

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<PINNED_COMMIT_SHA>
      - uses: astral-sh/setup-uv@<PINNED_COMMIT_SHA>
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"
      - run: uv sync --locked
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<PINNED_COMMIT_SHA>
      - uses: astral-sh/setup-uv@<PINNED_COMMIT_SHA>
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"
      - run: uv sync --locked
      - run: uv run mypy src

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<PINNED_COMMIT_SHA>
      - uses: astral-sh/setup-uv@<PINNED_COMMIT_SHA>
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"
      - run: uv sync --locked
      - run: uv run pytest -q

  data-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<PINNED_COMMIT_SHA>
      - uses: astral-sh/setup-uv@<PINNED_COMMIT_SHA>
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"
      - run: uv sync --locked
      - run: uv run pytest tests/dags tests/contracts tests/pandera -q
      - run: uv run sqlfluff lint sql/
```

The jobs are intentionally independent so the runner can provide feedback concurrently.

A more advanced repository may use reusable workflows or composite Actions, but that is an implementation decision rather than a requirement of this topic.

---

# 59. End-to-End Hands-On Lab

## Lab: Production Data Platform CI

Create:

```text
.github/workflows/
├── ci.yml
├── dbt-ci.yml
├── integration.yml
├── images.yml
└── infra.yml
```

The repository should contain representative:

```text
src/
dags/
sql/
contracts/
pandera/
dbt/
tests/
compose/
infra/
Dockerfile
pyproject.toml
uv.lock
```

The exact repository layout can differ, but the responsibilities must remain clear.

---

# 60. Lab Phase 1 — Python Quality Gates

Build:

```text
lint
typecheck
unit tests
coverage
```

Requirements:

```text
uv
↓
locked dependencies
↓
Ruff
↓
type checker
↓
pytest
```

### Exercise

1. Create a deliberately invalid Ruff rule violation.
2. Push it.
3. Observe the failing job.
4. Fix it.
5. Repeat with a failing test.
6. Repeat with a type error.

Use:

```text
PREDICT
→ EXECUTE
→ INSPECT
→ MEASURE
→ IMPROVE
```

---

# 61. Lab Phase 2 — DAG and Data Validation

Add:

```text
DAG import
DAG structure
SQL lint
contract checks
Pandera
```

Deliberately introduce:

- invalid DAG import;
- missing required task;
- invalid SQL;
- incompatible schema;
- invalid DataFrame column/type.

The learner should prove that each failure creates a meaningful CI signal.

---

# 62. Lab Phase 3 — dbt Slim CI

Create a CI schema such as:

```text
analytics_ci_pr_<number>
```

Configure:

```text
trusted state artifact
        ↓
modified selection
        ↓
descendants
        ↓
--defer
        ↓
dbt build/test
```

Verify that unrelated models are not rebuilt unnecessarily.

The learner must document:

1. what changed;
2. what dbt selected;
3. what was deferred;
4. what executed;
5. why the selected subset was safe.

---

# 63. Lab Phase 4 — Compose Integration

Start the Topic 02 integration environment.

```text
docker compose up
        ↓
health/readiness
        ↓
integration tests
        ↓
logs on failure
        ↓
docker compose down
```

Test at least one meaningful cross-service workflow.

Examples:

```text
pipeline → PostgreSQL
pipeline → object storage
producer → Kafka → consumer
```

Use the smallest integration flow that demonstrates real interaction.

---

# 64. Lab Phase 5 — Image Build and Scan

Build:

```text
ghcr.io/example/data-pipeline:${GITHUB_SHA}
```

Then:

```text
Build
 ↓
Scan
 ↓
Pass
 ↓
Store/publish
```

Verify that the image can be traced back to the commit that produced it.

---

# 65. Lab Phase 6 — Terraform

Configure:

```text
terraform fmt
terraform validate
security scan
terraform plan
```

Create a pull request that changes infrastructure.

The reviewer should be able to see:

```text
Plan
 ├── create
 ├── update
 └── destroy
```

Introduce a deliberately dangerous change and verify that the plan makes the impact visible.

---

# 66. Lab Phase 7 — OIDC

Create a safe cloud identity relationship.

Conceptually:

```text
GitHub Actions
      ↓
OIDC token
      ↓
Cloud identity provider
      ↓
Short-lived role
      ↓
Terraform / cloud operation
```

Verify that no long-lived cloud access key is required.

Do not hard-code credentials into the repository or workflow.

---

# 67. Deliberate Failure Labs

Do not only practice successful CI.

## Failure 1 — Ruff

Introduce a lint failure.

Expected:

```text
CI fails
→ identify lint error
→ fix
→ rerun
```

## Failure 2 — Type Checking

Introduce an incompatible type.

Expected:

```text
Type check fails
→ inspect error
→ fix annotation/implementation
→ rerun
```

## Failure 3 — Pytest

Break a test expectation.

## Failure 4 — DAG Import

Introduce a syntax/import failure.

## Failure 5 — Schema Compatibility

Remove or change a required field.

## Failure 6 — Pandera

Provide an invalid DataFrame.

## Failure 7 — dbt

Introduce a model failure or invalid dependency.

## Failure 8 — Integration Startup

Make an integration service unhealthy.

## Failure 9 — Image Vulnerability

Use a deliberately vulnerable dependency/image only in a safe lab.

## Failure 10 — Terraform

Introduce an unexpected destructive change.

## Failure 11 — Secret

Introduce a fake credential pattern into a test file.

## Failure 12 — Permissions

Make workflow permissions unnecessarily broad.

For every failure:

```text
Failure
   ↓
Locate
   ↓
Diagnose
   ↓
Reproduce
   ↓
Fix
   ↓
Re-run
   ↓
Verify
```

---

# 68. CI Performance Lab

Start with a deliberately inefficient workflow.

Measure:

```text
Total duration
Queue time
Dependency installation
Test duration
Integration duration
dbt duration
```

Then optimize with:

- caching;
- parallelism;
- matrices;
- path filters;
- test selection.

Measure again.

The learner must explain trade-offs, not merely report that the workflow became faster.

For example:

```text
Optimization:
parallel jobs

Benefit:
lower wall-clock duration

Cost:
higher concurrent compute

Risk:
more complex failure interpretation
```

---

# 69. CI Security Lab

Start with an intentionally insecure workflow containing:

- broad permissions;
- mutable Action references;
- inappropriate secret handling;
- missing scans.

Harden it.

Verification checklist:

```text
[ ] minimal permissions
[ ] pinned Actions
[ ] dependency scanning
[ ] secret scanning
[ ] image scanning
[ ] no long-lived cloud keys
[ ] protected branch
[ ] required checks
```

---

# 70. CI Debugging Playbook

## Workflow does not trigger

**Likely causes**

- incorrect event configuration;
- branch filter mismatch;
- path filter excludes the change;
- invalid workflow YAML.

**Inspect**

```text
workflow trigger
branch filters
path filters
workflow syntax
```

**Prevention**

Test trigger behavior explicitly and avoid overly narrow filters.

---

## Job fails immediately

**Likely causes**

- invalid runner configuration;
- malformed YAML;
- permission problem;
- missing tool.

**Inspect**

The first failed step and its exit code.

---

## Dependency installation fails

**Likely causes**

- lock file mismatch;
- Python version mismatch;
- network/package registry issue;
- platform-specific dependency.

**Inspect**

```text
Python version
uv version
uv.lock
pyproject.toml
package/index errors
```

---

## Cache misses

**Likely causes**

- lock file changed;
- cache key changed;
- cache scope differs;
- cache unavailable.

A cache miss should normally affect performance, not correctness.

---

## Ruff fails

Inspect:

```bash
uv run ruff check .
uv run ruff format --check .
```

Reproduce locally before changing CI.

---

## Type checker fails

Inspect the first reported type incompatibility.

Do not suppress the entire type-check stage merely to make CI green.

---

## Pytest fails

Reproduce:

```bash
uv run pytest path/to/test.py -q
```

Then run the broader suite after the targeted failure is understood.

---

## DAG import fails

Inspect:

- Python import traceback;
- missing provider;
- missing environment configuration;
- syntax;
- module path.

---

## SQL lint fails

Run the linter locally against the exact file.

---

## Contract check fails

Compare:

```text
expected contract
vs
proposed schema
```

Determine whether the change is genuinely breaking or the contract needs an intentional versioned change.

---

## dbt Slim CI fails

Inspect:

```text
state artifact
selection
target
CI schema
defer configuration
```

Do not assume every dbt failure is a selection problem.

---

## Compose service unhealthy

Inspect:

```bash
docker compose ps
docker compose logs <service>
docker inspect <container>
```

Verify readiness and health checks rather than adding arbitrary sleeps.

---

## Integration test cannot connect

Common causes:

```text
localhost used from inside a container
wrong service hostname
wrong port
service not ready
network mismatch
```

Remember:

```text
Container → service name
Host/runner → published host port
```

---

## Image build fails

Inspect:

- Dockerfile;
- build context;
- `.dockerignore`;
- dependency installation;
- architecture;
- registry/build credentials.

---

## Image scan fails

Inspect:

```text
package
version
severity
fixed version
base image
```

Prefer upgrading/removing the vulnerable dependency rather than blindly suppressing the finding.

---

## Terraform plan fails

Inspect:

- provider initialization;
- variables;
- backend;
- credentials;
- permissions;
- provider API errors.

---

## OIDC authentication fails

Inspect:

```text
issuer
audience
subject claims
repository restrictions
branch/environment restrictions
cloud trust policy
role permissions
```

OIDC failures are frequently trust-policy mismatches.

---

## Secret scanner blocks a commit

Determine:

1. Is it a real credential?
2. Is it a false positive?
3. Can the secret be removed?
4. If real, has it been revoked/rotated?

Never simply ignore a real leaked credential.

---

## Workflow permission denied

Inspect:

```yaml
permissions:
```

Then grant only the exact permission required.

---

## Third-party Action fails

Check:

- pinned revision;
- Action documentation;
- input changes;
- runner compatibility;
- permissions;
- upstream status.

---

## CI is too slow

Measure before changing it.

Then consider:

```text
cache
parallelism
path filters
test selection
smaller integration environments
matrix design
```

---

# 71. Common CI Mistakes

## Mistake 1 — CI only runs unit tests

This misses:

```text
DAG failures
SQL errors
contract breaks
dbt failures
integration failures
image vulnerabilities
Terraform mistakes
```

## Mistake 2 — CI is so slow nobody waits for it

Slow feedback increases risk.

## Mistake 3 — Long-lived cloud keys in CI

Prefer OIDC federation where supported.

## Mistake 4 — Unpinned third-party Actions

Mutable references increase supply-chain uncertainty.

## Mistake 5 — Full dbt rebuild on every PR

Use state-aware Slim CI when the project and risk profile support it.

---

# 72. Data Engineering CI vs Software CI

| Area | Standard Software CI | Data Engineering CI |
|---|---|---|
| Code | Application tests | Python + pipeline code |
| Data contracts | Sometimes | Critical |
| Schema validation | Sometimes | Critical |
| DAG validation | Usually absent | Required for DAG-based platforms |
| SQL | Sometimes | Common |
| dbt | Usually absent | Common |
| Integration | Application services | Databases/object stores/streaming |
| Images | Sometimes | Pipeline/dbt/Spark images |
| Terraform | Sometimes | Common |
| Data quality | Often external | CI-integrated where appropriate |

The important principle is:

> **Data Engineering CI extends software CI with data-system-specific correctness checks.**

---

# 73. Quality Gate Design

Classify checks by cost and feedback speed.

## Fast

```text
formatting
lint
types
unit tests
```

## Medium

```text
DAG tests
SQL
contracts
Pandera
```

## Expensive

```text
dbt integration
Compose integration
image builds
infrastructure plans
```

This classification helps determine:

- parallelism;
- trigger frequency;
- required checks;
- caching;
- selective execution.

---

# 74. Fail Fast vs Complete Feedback

There is no universal answer.

### Fail-fast strategy

```text
lint fails
    ↓
stop expensive downstream checks
```

Useful when expensive work depends on cheap validation.

### Parallel strategy

```text
lint ─────┐
types ────┤
tests ────┤
SQL ──────┘
```

Useful when independent checks can complete concurrently.

The correct design balances:

```text
developer feedback
+
compute cost
+
diagnostic value
+
dependency relationships
```

---

# 75. CI Cost Awareness

CI cost grows with:

```text
More jobs
+
More minutes
+
More compute
=
Higher CI cost
```

Optimization techniques include:

- caching;
- path filtering;
- parallelism;
- selective tests;
- right-sized integration environments.

Do not optimize by removing safety checks merely because they are expensive.

---

# 76. Test Frequency Design

Decide explicitly what runs:

- on every pull request;
- on merge;
- nightly;
- on scheduled intervals.

An example:

```text
Every PR:
lint
types
unit tests
contracts

PR when dbt changes:
dbt Slim CI

PR when infra changes:
Terraform plan

Merge:
image build/push

Nightly:
full regression
```

The correct schedule depends on system risk.

---

# 77. Knowledge Checkpoints

## Explain

1. What is CI?
2. What is a GitHub Actions workflow?
3. What is a runner?
4. What is a job?
5. Why do data pipelines need specialized CI?

## Predict

Given:

```yaml
jobs:
  lint:
    ...

  tests:
    ...

  integration:
    needs: [lint, tests]
```

Question:

> Which jobs can run concurrently, and which job waits?

## Diagnose

A workflow reports:

```text
integration failed
```

but earlier output shows:

```text
pytest: 1 failed
```

Question:

> Which failure should you investigate first and why?

## Design

> How would you design CI for a repository containing Python, dbt, Spark, Airflow, and Terraform?

A strong answer should identify separate quality gates while avoiding unnecessary duplication.

---

# 78. Production Incident Simulation

## Incident

A developer merges an Airflow DAG that imports successfully on their laptop but fails in the deployed environment because of a missing dependency.

### Questions

1. Which CI check could have detected this?
2. How would you reproduce the runtime environment?
3. Should the DAG import check run only locally?
4. What dependency/reproducibility control should accompany the test?

### Expected reasoning

```text
DAG import test
+
locked dependencies
+
reproducible CI environment
=
higher confidence before merge
```

---

# 79. Production Design Exercise

Design CI for:

```text
Python
+
Airflow
+
dbt
+
Spark
+
Kafka
+
PostgreSQL
+
Object Storage
+
Docker
+
Terraform
```

Your design should include:

```text
Fast checks
Data checks
dbt checks
Integration checks
Image checks
Infrastructure checks
Security checks
Required checks
Artifact traceability
```

Then identify which checks are:

```text
Every PR
PR when affected
Merge
Nightly
```

---

# 80. Senior Data Engineer Interview Questions

## Fundamentals

### What is CI?

CI is automated validation of changes as they are integrated into a shared codebase.

### CI vs CD?

CI validates changes. CD automates later delivery/deployment activities.

### Workflow vs job vs step?

A workflow is the automation definition; a job is an execution unit; a step is an individual action or command within a job.

### What is a runner?

The execution environment where a job runs.

### Push vs pull_request?

`push` responds to pushes; `pull_request` validates proposed changes before merge.

---

## Data Engineering

### What should Data Engineering CI validate?

At minimum:

```text
Python
DAGs
SQL
contracts
schemas
dbt
integration behavior
images
infrastructure
security
```

### How do you test Airflow DAGs?

Use import tests plus structural/policy tests.

### How do you validate data contracts?

Compare proposed producer schemas against defined compatibility rules and consumer expectations.

### Why use Pandera?

To validate DataFrame schemas and constraints programmatically.

### What is dbt Slim CI?

A state-aware strategy that validates the relevant changed dbt graph rather than unnecessarily rebuilding the entire project.

### Why use an isolated dbt schema?

To prevent PR validation from interfering with shared or production schemas.

### What does `--defer` do?

It allows references to unbuilt resources to resolve against an existing state when the project is configured appropriately; it is part of state-aware CI, not a synonym for changed-model selection.

---

## Infrastructure

### Why run Terraform plan in PRs?

To expose infrastructure changes, including potentially destructive operations, before merge.

### Why use OIDC instead of cloud keys?

OIDC can provide short-lived credentials through workload identity federation instead of storing long-lived static keys.

### What should Terraform CI validate?

Formatting, configuration validity, security controls, and the planned infrastructure changes.

---

## Security

### Why pin Actions by SHA?

To prevent a mutable tag/reference from unexpectedly changing the code executed by CI.

### Does SHA pinning eliminate supply-chain risk?

No. The pinned revision still needs to be trusted, reviewed, and updated deliberately.

### Why minimize workflow permissions?

To reduce the blast radius if a workflow or dependency is compromised.

### What is secret scanning?

Automated detection of credential-like material in source and repository changes.

### What is dependency scanning?

Detection of known vulnerabilities in direct and transitive dependencies.

### What is image scanning?

Inspection of container image components for known vulnerabilities.

---

## Performance

### How do you reduce CI time?

Use caching, parallel jobs, matrices where justified, path filtering, and selective testing.

### When should jobs run in parallel?

When they are independent and the additional compute cost is justified.

### How do path filters help?

They avoid triggering irrelevant expensive workflows.

### What is the risk of overly aggressive test selection?

A change may bypass a required safety check because its impact crosses the apparent path boundary.

---

## Architecture

### Design CI for a production Data Platform.

A strong design includes:

```text
Python quality
DAG validation
SQL validation
Contracts
dbt Slim CI
Integration
Image build/scan
Terraform plan
Security
Required checks
Artifact traceability
```

### How do you prevent broken DAGs from reaching production?

Make DAG import and policy tests required pull-request checks.

### How do you ensure the same artifact is later deployed?

Build once, assign a traceable immutable identity, store it, and promote that exact artifact later rather than rebuilding.

---

# 81. Final Capstone — Production Data Platform CI

Build:

```text
.github/workflows/
├── ci.yml
├── dbt-ci.yml
├── integration.yml
├── images.yml
└── infra.yml
```

The complete system must validate:

```text
Python
 ├── Ruff
 ├── Type checking
 └── pytest

Data
 ├── DAGs
 ├── SQL
 ├── Contracts
 ├── Schema compatibility
 └── Pandera

dbt
 ├── Slim CI
 ├── State
 ├── Selection
 └── Defer

Integration
 └── Docker Compose

Images
 ├── Build
 ├── Scan
 └── SHA tag

Infrastructure
 ├── fmt
 ├── validate
 ├── security scan
 └── plan

Security
 ├── Secret scanning
 ├── Dependency scanning
 ├── Pinned Actions
 └── Least-privilege permissions

Cloud
 └── OIDC
```

---

# 82. Capstone Acceptance Criteria

The learner must prove:

- a broken Python test blocks the PR;
- a broken DAG blocks the PR;
- an invalid contract blocks the PR;
- a dbt failure blocks the PR;
- an integration failure blocks the PR;
- an image vulnerability is detected;
- Terraform plan is visible for infrastructure changes;
- cloud access does not require long-lived cloud keys;
- third-party Actions are pinned;
- workflow permissions are minimized;
- secret scanning is enabled;
- required checks protect the main branch;
- expensive checks are optimized appropriately;
- artifacts are traceable to a commit.

---

# 83. Final Assessment

Use this checklist honestly:

```text
[ ] I understand Continuous Integration.
[ ] I understand GitHub Actions.
[ ] I can create workflows.
[ ] I understand triggers.
[ ] I understand jobs and steps.
[ ] I understand runners.
[ ] I can read CI logs.
[ ] I can build Python CI with uv.
[ ] I can run Ruff.
[ ] I can run formatting checks.
[ ] I can run type checking.
[ ] I can run pytest.
[ ] I can validate Airflow DAGs.
[ ] I can run SQL checks.
[ ] I understand data contracts.
[ ] I understand schema compatibility.
[ ] I can use Pandera validation in CI.
[ ] I understand dbt Slim CI.
[ ] I understand dbt state.
[ ] I understand dbt --defer.
[ ] I can run integration tests using Compose.
[ ] I can build images in CI.
[ ] I can scan images.
[ ] I understand SHA-tagged images.
[ ] I can run Terraform validation in CI.
[ ] I can run Terraform plan in CI.
[ ] I understand OIDC.
[ ] I can avoid long-lived cloud credentials.
[ ] I understand caching.
[ ] I can parallelize CI jobs.
[ ] I understand matrix builds.
[ ] I understand path filters.
[ ] I can optimize test selection.
[ ] I understand supply-chain security.
[ ] I can pin Actions by SHA.
[ ] I understand least-privilege permissions.
[ ] I understand dependency scanning.
[ ] I understand secret scanning.
[ ] I understand protected branches.
[ ] I understand required checks.
[ ] I can use pre-commit.
[ ] I understand build-once/store/deploy-exact-artifact.
[ ] I can design production-grade Data Engineering CI.
```

---

# 84. Roadmap Boundaries

## Topic 04 — Terraform

Topic 04 teaches:

- Terraform fundamentals;
- infrastructure as code;
- state;
- modules;
- infrastructure safety.

This topic teaches how Terraform is **validated and planned in CI**, not Terraform fundamentals again.

## Topic 06 — Environment Promotion

Topic 06 will teach:

- dev;
- staging;
- production;
- promotion;
- approvals;
- immutable artifact promotion;
- rollback.

This module only establishes the CI foundation of build-once/store/traceable-artifact behavior.

## Topic 07 — Cloud Secrets Managers

Topic 07 will teach:

- secrets managers;
- secret retrieval;
- rotation;
- secret delivery;
- leaked-secret response.

This module teaches CI's secret-safe authentication principles, especially OIDC and secret scanning, but does not become the secrets-manager module.

---

# 85. Version-Aware Implementation

CI syntax and behavior changes over time.

For production repositories:

- pin important third-party Actions;
- use a supported Python version;
- keep `uv` and project tooling current;
- use the repository's supported dbt version;
- use a supported Docker/Compose implementation;
- use a supported Terraform version;
- keep OIDC/cloud-provider configuration aligned with current provider guidance.

When behavior is version-sensitive:

1. state the version assumption;
2. use documented syntax;
3. avoid obsolete syntax;
4. test the workflow itself.

Do not assume that a workflow copied from an old blog post remains correct.

---

# 86. Predict → Execute → Inspect → Measure

Use this cycle for practical work:

```text
PREDICT
What should CI do?

      ↓

EXECUTE
Run the workflow.

      ↓

INSPECT
Read logs/results/artifacts.

      ↓

MEASURE
Check duration, failures, and coverage.

      ↓

IMPROVE
Optimize without weakening safety.
```

This turns CI learning into engineering practice rather than YAML memorization.

---

# 87. Final Mastery Model

A production Data Engineering CI system should be understood as a layered safety system:

```text
                    Pull Request
                         │
                         ▼
              ┌─────────────────────┐
              │ Fast Quality Gates  │
              │ Ruff / Types / Test │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Data-System Gates   │
              │ DAG / SQL / Schema  │
              │ Contracts / Pandera │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ dbt / Integration   │
              │ State / Compose     │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Build / Scan / IaC  │
              │ Images / Terraform  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Security & Policy   │
              │ OIDC / Secrets /    │
              │ Permissions / Gates │
              └──────────┬──────────┘
                         │
                         ▼
                     Review
                         │
                         ▼
                       Merge
```

The core engineering principle is:

> **Automate the known correctness, security, and infrastructure checks before a change becomes someone else's production incident.**

---

# 88. Final Coverage Audit

Before considering this module complete, verify:

```text
[ ] Continuous Integration fundamentals
[ ] GitHub Actions
[ ] workflows
[ ] push trigger
[ ] pull_request trigger
[ ] schedules
[ ] manual trigger
[ ] jobs
[ ] steps
[ ] runners
[ ] logs
[ ] Python CI
[ ] uv
[ ] dependency caching
[ ] Ruff lint
[ ] Ruff format check
[ ] type checking
[ ] pytest
[ ] coverage
[ ] DAG import tests
[ ] DAG structure/policy tests
[ ] SQL linting
[ ] data contracts
[ ] schema compatibility
[ ] Pandera
[ ] dbt Slim CI
[ ] modified model selection
[ ] descendants
[ ] isolated CI schema
[ ] dbt state
[ ] dbt --defer
[ ] integration testing
[ ] Docker Compose/service containers
[ ] image build
[ ] image scan
[ ] SHA image tags
[ ] Terraform fmt
[ ] Terraform validate
[ ] Terraform security scan
[ ] Terraform plan
[ ] OIDC federation
[ ] no long-lived cloud keys
[ ] caching
[ ] parallel jobs
[ ] matrix builds
[ ] path filters
[ ] test selection
[ ] supply-chain security
[ ] SHA-pinned Actions
[ ] least-privilege permissions
[ ] dependency scanning
[ ] secret scanning
[ ] protected branches
[ ] required checks
[ ] pre-commit
[ ] build once
[ ] artifact storage
[ ] exact artifact traceability
[ ] deliberate failure labs
[ ] CI performance lab
[ ] CI security lab
[ ] OIDC lab
[ ] debugging playbook
[ ] common mistakes
[ ] knowledge checkpoints
[ ] interview questions
[ ] capstone
[ ] final assessment
```

---

# 89. Module Completion Standard

You are ready to move beyond this topic when you can independently explain and implement the following production flow:

```text
Developer Change
      ↓
Pull Request
      ↓
Code Quality
      ↓
Python Tests
      ↓
Data Tests
      ↓
DAG Validation
      ↓
Contracts / Schema Checks
      ↓
dbt Slim CI
      ↓
Integration Tests
      ↓
Image Build + Scan
      ↓
Terraform Validation + Plan
      ↓
Security / Supply Chain Checks
      ↓
Required Checks
      ↓
Review
      ↓
Merge
```

You should also be able to answer:

> **Why did this check run?**

> **What failure does this check prevent?**

> **Why does this job depend on that job?**

> **Could this check safely run in parallel?**

> **What is the cost of this check?**

> **How would I reproduce its failure locally?**

> **How is the resulting artifact traced back to the source commit?**

That is the difference between knowing GitHub Actions syntax and understanding **production-grade CI for Data Engineering**.
