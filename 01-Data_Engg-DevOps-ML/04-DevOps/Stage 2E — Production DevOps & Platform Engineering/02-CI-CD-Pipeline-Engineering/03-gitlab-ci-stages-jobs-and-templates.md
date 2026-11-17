# GitLab CI: Stages, Jobs, and Templates

**Abstract:** This lesson builds a working mental model of GitLab CI/CD from a minimal Python lint-and-test pipeline through rules, DAG dependencies, artifacts and caches, reusable configuration, downstream pipelines, identity concepts, deployment serialization, platform operations, and GitHub Actions migration. It uses a small FastAPI scoring service, shared Python library, and batch ETL package as a running example. Examples are designed for a learner-owned private project and low-resource laptop; all expected outputs are illustrative, and version-/tier-sensitive details are explicitly flagged for verification.

> **Module:** M02  
> **Stage:** 2E — Production DevOps & Platform Engineering  
> **Unit:** 3  
> **Target file:** `03-gitlab-ci-stages-jobs-and-templates.md`  
> **Estimated learning time:** 8–12 hours  
> **Last reviewed:** Authoring date: 2026-10-24; no independent live-documentation review performed  
> **Assumed baseline:** GitLab CI/CD with a currently supported GitLab instance and a permitted Linux runner; exact server, Runner, executor, and plan versions must be checked  
> **Verification status:** DRAFT-AUDITED — HUMAN VERIFICATION REQUIRED. GitLab CI Lint, a real runner, and the labs were not executed for this document. Current official documentation was not live-checked. All outputs are representative, not observed results.

## Contents

- [3.0 Why this matters in production](#30-why-this-matters-in-production)
- [3.1 Learning objectives](#31-learning-objectives)
- [3.2 Concept map and vocabulary](#32-concept-map-and-vocabulary)
- [3.3 Level 1 — Beginner](#33-level-1--beginner)
- [3.4 Level 2 — Intermediate](#34-level-2--intermediate)
- [3.5 Level 3 — Advanced](#35-level-3--advanced)
- [3.6 Level 4 — Expert](#36-level-4--expert)
- [3.7 SRE lens](#37-sre-lens)
- [3.8 Security lens](#38-security-lens)
- [3.9 Production checklist](#39-production-checklist)
- [3.10 Hands-on lab set](#310-hands-on-lab-set)
  - [Lab A — Minimal GitLab CI pipeline](#lab-a--minimal-gitlab-ci-pipeline)
  - [Lab B — Rules and duplicate-pipeline diagnosis](#lab-b--rules-and-duplicate-pipeline-diagnosis)
  - [Lab C — DAG, artifacts, and cache](#lab-c--dag-artifacts-and-cache)
  - [Lab D — Reuse and child pipeline](#lab-d--reuse-and-child-pipeline)
  - [Lab E — GitHub Actions translation](#lab-e--github-actions-translation)
- [3.11 Self-check questions](#311-self-check-questions)
- [3.12 Evidence artifacts](#312-evidence-artifacts)
- [3.13 Common interview and design-review questions](#313-common-interview-and-design-review-questions)
- [Claim Register](#claim-register)
- [Ten-pass self-audit report](#ten-pass-self-audit-report)
- [3.14 Sources and verification notes](#314-sources-and-verification-notes)

## Unit 3 — GitLab CI: stages, jobs, templates

**Target file:** 03-gitlab-ci-stages-jobs-and-templates.md | **Estimated time:** 8–12 hours | **Prerequisites:** Git, shell, Python, basic YAML, pytest basics, M01 image-building outcomes

**Core tools:** GitLab CI/CD, `.gitlab-ci.yml`, Git, Python, pytest, GitLab CI Lint or equivalent validation, a permitted runner | **Awareness:** `gitlab-ci-local`, `gitlab-runner` executor choices, CI components, OIDC, GitHub Actions mapping, GitOps handoff | **Last reviewed:** Authoring date 2026-10-24; independent review not performed

### 3.0 Why this matters in production

A single commit can accidentally create both a branch pipeline and a Merge Request (MR) pipeline, consuming capacity and confusing status checks. Jobs can run in the wrong order when teams confuse stage barriers with explicit `needs` dependencies, or a downstream job can fail because an expected artifact was never transferred. A cache is an optimization, not a trustworthy release-output channel; treating it as one can make builds depend on stale or poisoned state. Untrusted contribution code must not receive privileged variables or execute in a runner context that can reach production. Finally, copy-pasted pipeline fragments and concurrent deployment jobs create configuration drift and race conditions that become harder to diagnose as the organization grows.

### 3.1 Learning objectives

| Objective | Teaching content | Lab/checklist mapping | Evidence |
|---|---|---|---|
| [L1] Explain how GitLab reads `.gitlab-ci.yml` and schedules jobs | 3.2–3.3 | Lab A | Annotated pipeline diagram |
| [L1] Build a Python lint-and-test pipeline with stages, jobs, variables, and a runner assumption | 3.3 | Lab A | YAML, source, tests, validation notes |
| [L2] Configure `workflow:rules` and job `rules` to control pipeline and job creation separately | 3.4 | Lab B; checklist | Before/after config and pipeline-count notes |
| [L2] Choose `needs`, artifacts, cache, services, environments, and matrix jobs based on their purpose | 3.4 | Lab C; checklist | DAG sketch and artifact/cache evidence |
| [L3] Compose shared configuration and explain downstream pipeline boundaries | 3.5 | Lab D | Include/extends example and design record |
| [L3] Explain protected variables, OIDC identity, cancellation, and serialization without overclaiming guarantees | 3.5, 3.8 | Checklist and self-check | Threat/control notes |
| [L4] Validate and operate a versioned pipeline library, and diagnose efficiency and failure symptoms | 3.6–3.7 | Labs B–E | Claim register checks, runbook, measurements |
| [L4] Translate a minimal GitHub Actions workflow to GitLab CI and identify non-equivalences | 3.6 | Lab E | Mapping table and translated YAML |

### 3.2 Concept map and vocabulary

```text
Commit / Merge Request / schedule / manual event
                    |
                    v
       workflow:rules — create pipeline?
                    |
                    v
      .gitlab-ci.yml configuration expansion
      (includes, hidden jobs, inheritance, references)
                    |
                    v
       job rules — include each job?
                    |
                    v
      stages (barriers) + needs (DAG edges)
                    |
                    v
       eligible runner + executor + image
                    |
                    v
         script commands and services
                    |
          +---------+---------+
          |                   |
          v                   v
  artifacts (outputs)   cache (optimization)
          |                   |
          +---------+---------+
                    v
      status, logs, evidence, environment/deploy
                    |
                    v
       downstream pipeline / operational review
```

| Term | Precise definition | Common misconception |
|---|---|---|
| Pipeline | A configured collection of jobs created for an event or action. | One commit necessarily means one pipeline. |
| Stage | A named phase used for ordering jobs. | A stage is the same thing as a job. |
| Job | A unit of CI work configured in YAML and scheduled to a runner. | A job is a single shell command. |
| Script command | A command executed by a job's shell context. | Each command is a separate GitLab job. |
| Runner | The agent/application that obtains and executes eligible jobs. | Every project automatically has a usable runner. |
| Shared runner | A runner made available across multiple projects by the GitLab instance/operator. **[VERIFY terminology/configuration]** | Shared runners are always enabled or free. |
| Project/group runner | A runner configured for a project or group scope; exact UI terminology may evolve. **[VERIFY]** | Registration scope alone makes a runner trustworthy. |
| Executor | The runner execution environment, such as shell or Docker; supported choices depend on Runner version/configuration. **[VERIFY]** | The executor is the same as the CI job image. |
| `.gitlab-ci.yml` | Default project-level CI configuration file, normally at repository root. | YAML validity alone guarantees a runnable pipeline. |
| Predefined variable | A GitLab-provided variable describing pipeline, project, commit, or job context. | Every variable exists in every pipeline type. |
| Custom variable | A value defined by project/group/instance settings or YAML. | A YAML variable is a secret store. |
| Masked variable | A variable whose matching value is redacted from eligible job logs under configured constraints. | Masking makes it safe to print secrets. |
| Hidden variable | A UI/security property intended to prevent a stored variable value from being revealed later; availability and behavior are version-sensitive. **[VERIFY]** | Hidden and masked mean the same thing. |
| Protected variable | A variable restricted to eligible protected refs according to project settings and GitLab behavior. **[VERIFY]** | Protected variables are safe for any job on a protected ref. |
| `rules` | Ordered job inclusion/behavior conditions evaluated when creating a pipeline. | Job rules alone prevent all duplicate pipelines. |
| `workflow:rules` | Rules controlling whether a pipeline is created at all. | It is just another name for job rules. |
| `needs` | A dependency declaration that can allow a job to start after specified prerequisites rather than waiting for all earlier-stage jobs. | It means “download every artifact automatically” in all cases. |
| Stage ordering | The default stage-level ordering relationship. | Every job needs a `needs` entry. |
| DAG | Directed acyclic graph of job dependencies. | A DAG has no ordering constraints. |
| Artifact | A declared file output retained by CI and potentially passed to downstream jobs. | Artifacts and cache are interchangeable. |
| Cache | Reusable data intended to reduce repeated work. | Cache contents are authoritative release outputs. |
| Service | A supporting container or service endpoint associated with a job, subject to executor/network requirements. | A service automatically works with every executor. |
| Environment | A named deployment target or lifecycle context recorded by GitLab. | Declaring an environment performs a safe deployment by itself. |
| Deployment job | A job that deploys to or records a deployment environment. | A job named `deploy` is automatically protected. |
| Hidden job | A configuration entry whose name starts with a dot, commonly used as a reusable template. | It runs like an ordinary job. |
| `extends` | Configuration inheritance from one or more parent job definitions. | It deep-merges every nested mapping exactly as expected. |
| YAML anchor/alias | YAML-level reuse of a node via `&anchor` and `*alias`. | It can reference arbitrary GitLab-expanded configuration in every context. |
| `include` | Loads configuration from another file or source supported by GitLab. | Remote includes are inherently trusted. |
| `!reference` | GitLab-specific configuration reuse syntax for referencing selected configuration sections. **[VERIFY]** | It is standard YAML. |
| CI component / `spec:inputs` | Reusable CI configuration packaging and parameterization concepts. Current syntax, version and plan constraints must be checked. **[VERIFY]** | Any component snippet from a blog is valid for every instance. |
| Child pipeline | A downstream pipeline triggered by a parent pipeline, commonly used to split configuration/workloads. | It is the same as a pipeline in another project. |
| Parent-child pipeline | A parent/child relationship typically within the same project, with defined configuration and status links. **[VERIFY details]** | It automatically inherits all parent secrets safely. |
| Multi-project pipeline | A pipeline that triggers work in a different project. | Cross-project triggering removes authorization boundaries. |
| `trigger` | A keyword used to configure downstream pipeline triggering. Exact forms/options are version-sensitive. **[VERIFY]** | It is a shell command. |
| `interruptible` | A job-level setting related to whether a running job can be interrupted in supported cancellation scenarios. **[VERIFY]** | Every interrupted job is safe to restart. |
| Auto-cancel | Pipeline cancellation behavior intended to stop redundant work under configured conditions. **[VERIFY]** | It always cancels only harmless jobs. |
| `resource_group` | A mechanism to serialize jobs sharing a named resource, commonly a deployment target. **[VERIFY]** | It replaces deployment idempotency or rollback. |
| `id_tokens` | Configuration for issuing an OIDC-compatible ID token to a job, with audience configuration in supported versions. **[VERIFY]** | Possessing a token automatically authorizes cloud access. |
| CI linting | Validation of CI configuration syntax and, where supported, configuration expansion/logic. | A successful lint proves runtime, security, or deployment correctness. |

**Core distinctions**

- `workflow:rules` decides whether to create a pipeline; job-level `rules` decide which jobs enter a pipeline.
- Stages provide broad ordering barriers. `needs` can form a more specific dependency graph; it should reflect real prerequisites.
- Artifacts transfer named outputs/evidence. Cache stores reusable work to improve efficiency and may be missing or stale.
- Protected, masked, and hidden describe different controls and are not substitutes for least privilege, safe runner isolation, or avoiding secret exposure.
- GitLab behavior varies with server version, Runner version, executor, project settings, and subscription. For every `[VERIFY]`, consult current official documentation and the target instance's configuration before adoption.

### 3.3 Level 1 — Beginner

#### How configuration becomes a running job

GitLab normally reads `.gitlab-ci.yml` from the repository root, combines it with supported included configuration, evaluates pipeline-creation and job-inclusion rules, then schedules eligible jobs to runners. A runner must be available, permitted for the project, online, and eligible for the job's tags and protected-ref requirements. A valid YAML file can still fail because an image is unavailable, no runner matches, a script exits non-zero, or a dependency cannot be retrieved.

```text
push / MR
   -> create pipeline?
   -> expand configuration and select jobs
   -> queue each eligible job
   -> runner obtains job
   -> prepare environment/image
   -> run script
   -> upload artifacts / report status
```

#### Minimal repository

```text
gitlab-python-demo/
├── .gitlab-ci.yml
├── pyproject.toml
├── src/
│   └── scorelib.py
└── tests/
    └── test_scorelib.py
```

```toml
# File: pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "gitlab-python-demo"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8,<9", "ruff>=0.6,<1"]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

```python
# File: src/scorelib.py
from __future__ import annotations


def bounded_score(raw_score: float) -> float:
    """Return a score bounded to the inclusive range [0, 1]."""
    if raw_score < 0.0:
        return 0.0
    if raw_score > 1.0:
        return 1.0
    return raw_score
```

```python
# File: tests/test_scorelib.py
from scorelib import bounded_score


def test_middle_score_is_unchanged() -> None:
    assert bounded_score(0.7) == 0.7


def test_negative_score_is_clamped() -> None:
    assert bounded_score(-0.2) == 0.0


def test_high_score_is_clamped() -> None:
    assert bounded_score(1.2) == 1.0
```

```yaml
# File: .gitlab-ci.yml
stages:
  - lint
  - test

image: python:3.12-slim

variables:
  PIP_DISABLE_PIP_VERSION_CHECK: "1"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  key: "pip-${CI_COMMIT_REF_SLUG}"
  paths:
    - .cache/pip/

lint:
  stage: lint
  script:
    - python -m pip install -e ".[dev]"
    - ruff check src tests

unit_tests:
  stage: test
  script:
    - python -m pip install -e ".[dev]"
    - pytest -q
  artifacts:
    when: always
    expire_in: 1 week
    paths:
      - .pytest_cache/
```

This example is deliberately small. **[VERIFY]** Check the current `python` image tag, runner architecture, and network/package-index access in your environment. For higher reproducibility, lock dependencies and pin the image by a reviewed immutable digest; that belongs to broader image and dependency-hardening practice. The cache here is only a speed optimization. Do not treat it as the record of which dependency versions were used.

#### GitLab-provided variables: inspect selectively

Commonly used variables include `CI_COMMIT_SHA` (commit identifier), `CI_COMMIT_REF_NAME` (ref name), `CI_COMMIT_REF_SLUG` (normalized ref form), `CI_PROJECT_PATH` (project path), and `CI_PIPELINE_SOURCE` (pipeline source). **[VERIFY: current official “Predefined CI/CD variables” reference]** Confirm each variable's availability and semantics for the pipeline type and GitLab version. Do not print the full environment; it can contain credentials.

```bash
# File: commands/inspect-safe-context.sh
#!/usr/bin/env bash
set -euo pipefail
printf 'project=%s\n' "${CI_PROJECT_PATH:-<unset>}"
printf 'source=%s\n' "${CI_PIPELINE_SOURCE:-<unset>}"
printf 'commit=%s\n' "${CI_COMMIT_SHA:-<unset>}"
printf 'ref_slug=%s\n' "${CI_COMMIT_REF_SLUG:-<unset>}"
```

Command: `bash commands/inspect-safe-context.sh`

**Example — yours will differ:**
```text
project=group/gitlab-python-demo
source=push
commit=0123456789abcdef0123456789abcdef01234567
ref_slug=feature-safe-ci
```

Interpretation: these are context identifiers, not credentials. Do not replace this allowlist with `env`, `printenv`, `set -x`, or a dump of all variables.

#### Guided local validation

Run from the repository root in a Python environment. These commands change only the local virtual environment and files; they do not publish anything.

```bash
# File: commands/local-test.sh
set -euo pipefail
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check src tests
pytest -q
```

Command: `bash commands/local-test.sh`

**Example — yours will differ:**
```text
All checks passed!
3 passed
```

Interpretation: this checks the Python project, not GitLab's server-side pipeline creation or runner behavior. Clean up with `rm -rf .venv .cache .pytest_cache`; verify using `test ! -e .venv && test ! -e .cache && test ! -e .pytest_cache && echo "cleanup verified"`.

#### Pipeline and job status

A pipeline can succeed, fail, be canceled, be blocked, or contain skipped jobs depending on rules and configuration. A job can fail during preparation, image/service setup, script execution, or artifact upload. A retry can be useful after a known transient infrastructure fault, but “retry until green” hides root causes and can conceal flakiness. Preserve a redacted failure excerpt, identify the failing phase, and test a specific hypothesis.

**Runner terminology and availability:** GitLab-hosted shared runners and runners installed/configured by a project or organization are operationally different. Whether shared runners are enabled, which executor types are available, and which plan/configuration allows a feature are instance-specific. **[VERIFY: target project's Settings → CI/CD → Runners and current GitLab runner documentation]**. If no eligible runner is available, a job can remain pending; inspect runner status, scope, tags, protected-ref eligibility, and whether it is paused before changing YAML.

#### Beginner mistake table

| Symptom | Likely cause | Fix |
|---|---|---|
| Pipeline does not appear | YAML/configuration invalid or pipeline creation rules exclude the event | Inspect pipeline creation result and validate configuration |
| Job remains pending | No eligible online runner, tag mismatch, or protected-ref mismatch | Check runner scope, tags, status, and project configuration |
| `pytest: command not found` | Dependencies were not installed in the job environment | Install the declared development dependencies before running tests |
| Test import fails | Package layout/install configuration mismatch | Use a consistent `src/` layout and install the project |
| Pipeline succeeds but output file is missing | File was not declared as an artifact or path is wrong | Declare the correct artifact path and verify it exists |
| A retry passes with no change | Transient issue or nondeterministic test | Investigate the failure class; do not treat retry as a fix |
| Secret appears in a log | Script or tool printed it, or tracing exposed it | Revoke/rotate immediately, remove unsafe logging, inspect artifacts and access |

### 3.4 Level 2 — Intermediate

#### `rules` and `workflow:rules`

`rules` are evaluated in order for a job and can decide whether the job is included and how it behaves. `workflow:rules` controls pipeline creation. This separation matters when a push to a branch with an open MR can otherwise create both a branch pipeline and an MR pipeline. Job rules alone do not necessarily prevent the second pipeline from existing.

Use current `rules` patterns for new examples. `only/except` appears in older configurations and is treated here as legacy guidance, not current best practice. **[VERIFY: migration details for the target GitLab version]**.

```yaml
# File: .gitlab-ci.yml — duplicate-pipeline defensive pattern
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS'
      when: never
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH'
    - when: never

stages: [lint, test]

lint:
  stage: lint
  script: ["python -m ruff check src tests"]
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH'

test:
  stage: test
  script: ["python -m pytest -q"]
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH'
```

This is a pattern to validate, not a guarantee for every event, trigger, schedule, fork, or GitLab version. **[VERIFY]** Test the exact desired event matrix on the target instance. The example intentionally admits MR pipelines and ordinary branch push pipelines only when no open MR suppresses the push pipeline; scheduled, tag, web, API, and downstream pipelines are not admitted by this policy unless added deliberately.

**Failure-on-purpose:** remove `workflow:rules` and configure jobs to run for both pushes and MRs. Push a branch that has an open MR. In a private test project, compare pipeline records for the same commit. The expected diagnostic is that more than one pipeline may be created for one change, depending on project settings and rule details. Do not invent a count: record what your test instance actually shows.

#### Stages versus `needs`

Without `needs`, stage ordering generally creates a barrier: jobs in a later stage wait for the earlier stage's required jobs to complete according to pipeline semantics. With `needs`, a job can declare a more precise dependency and may start once its dependencies complete, forming a DAG. A DAG should represent actual prerequisites, not simply make every job depend on every other job.

```yaml
# File: .gitlab-ci.yml — explicit DAG
stages: [lint, test, package]

lint:
  stage: lint
  script: ["python -m ruff check src tests"]

unit_tests:
  stage: test
  script: ["python -m pytest -q"]

schema_check:
  stage: test
  script: ["python scripts/check_schema.py"]

package_metadata:
  stage: package
  needs:
    - job: lint
    - job: unit_tests
    - job: schema_check
  script:
    - python -c "from pathlib import Path; Path('build-evidence.txt').write_text('checks passed\\n')"
  artifacts:
    paths: [build-evidence.txt]
    expire_in: 1 week
```

**[VERIFY]** Confirm the target version's `needs` syntax and artifact-download behavior. If a job needs an artifact, declare the dependency behavior explicitly using currently supported syntax and validate the expanded pipeline. Avoid an incorrect `needs` relationship that permits packaging before schema validation.

#### Artifacts versus cache

| Property | Artifacts | Cache |
|---|---|---|
| Primary purpose | Preserve and transfer declared outputs/evidence | Reuse data to reduce repeated work |
| Typical content | Test reports, build outputs, package files | Downloaded dependency wheels or package-manager cache |
| Correctness assumption | Explicit output expected from a successful/failed job as configured | May be absent, stale, or unsuitable for this job |
| Downstream use | Declared and retrieved according to pipeline/job configuration | Best-effort optimization; do not use as release authority |
| Retention | Controlled by artifact settings and instance policy; verify | Controlled by cache key, runner/backend setup, and policy; verify |
| Trust | Treat artifacts as potentially sensitive and validate provenance | Treat cache as potentially untrusted shared state |

A useful rule: **artifacts are the evidence/output channel; cache is an optimization channel**. Avoid placing credentials, `.env` files, private keys, or sensitive records in either. Keep paths narrow and retention intentional.

#### Data/schema validation and service containers

The running example has three logical areas: a FastAPI scoring service, a shared scoring library, and an ETL package. CI should validate code and data contracts cheaply before packaging. A schema check can use a tiny fixture, not a production dataset.

```python
# File: scripts/check_schema.py
from __future__ import annotations

import csv
from pathlib import Path

EXPECTED = {"record_id", "feature", "label"}


def main() -> int:
    path = Path("data/sample.csv")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        if columns != EXPECTED:
            raise SystemExit(
                f"schema mismatch: expected {sorted(EXPECTED)}, got {sorted(columns)}"
            )
        first_row = next(reader, None)
        if first_row is None:
            raise SystemExit("sample must contain at least one row")
    print("schema check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```csv
# File: data/sample.csv
record_id,feature,label
r1,0.25,1
r2,0.75,0
```

Command: `python scripts/check_schema.py`

**Example — yours will differ:**
```text
schema check passed
```

Interpretation: the small fixture validates a contract; it does not prove that a production-scale data lake is healthy.

A `services` job can start a database or other supporting container for integration tests. Availability depends on the runner executor, networking, service aliasing, image pull access, and resource limits. **[VERIFY]** Use a database service only if the permitted runner supports it. Keep the laptop baseline small; the following example is a shape to validate rather than an assumed universal configuration:

```yaml
# File: .gitlab-ci.yml — illustrative service job; validate executor and image
integration_test:
  stage: test
  image: python:3.12-slim
  services:
    - name: postgres:16-alpine
      alias: db
  variables:
    POSTGRES_DB: app_test
    POSTGRES_USER: app_test
    POSTGRES_PASSWORD: local-only-example
  script:
    - python -m pip install -e ".[dev]"
    - python -m pytest -q tests/integration
```

The placeholder password is not a production secret. Do not use this pattern to inject privileged credentials. A database image's initialization variables and service readiness behavior must be verified against that image's official documentation. The job also needs integration tests that use the `db` host and a readiness strategy; those tests are omitted from this optional example because the core sample does not require a database.

#### Environments, matrix jobs, and workflow creation

An environment gives a deployment a named context such as `staging`; it does not itself provision or secure the target. Detailed protected environments and approvals belong to Unit 9.

```yaml
# File: .gitlab-ci.yml — deployment concept, not a real deployment
staging_preview:
  stage: deploy
  script:
    - echo "Would deploy the validated artifact to the isolated preview target"
  environment:
    name: staging
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
```

The example is a manual, non-deploying placeholder. Do not replace the `echo` with a real deployment without an approved target, least-privilege identity, rollback plan, and Unit 9 controls.

`parallel:matrix` can repeat a job across a small set of variable combinations. Exact matrix features and constraints are **[VERSION-SENSITIVE]**; validate with CI Lint.

```yaml
# File: .gitlab-ci.yml — small matrix example
python_matrix:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.11", "3.12"]
  image: "python:${PYTHON_VERSION}-slim"
  script:
    - python --version
    - python -m pip install -e ".[dev]"
    - python -m pytest -q
```

Use a matrix when the same check should run against a small supported set of runtimes. Do not use a matrix merely to duplicate identical jobs. Pin exact image digests for supply-chain-sensitive release workflows, and measure total runner capacity before expanding the matrix. Detailed parallelism and caching are Unit 4.

#### Pattern catalogue

| Pattern | When to use | When NOT to use |
|---|---|---|
| `workflow:rules` + job `rules` | Differentiate MR, branch, tag, schedule, and manual pipeline policy | When conditions have not been tested against the event matrix |
| `needs` DAG | A job has explicit prerequisite jobs and can run before unrelated stage jobs finish | When dependencies are unclear or artifact flow is accidental |
| Artifacts for build/test output | Downstream jobs need a named file/report | For reusable dependency downloads |
| Cache for package downloads | Repeated dependency downloads are expensive | As the sole source of a release binary or evidence |
| Service container | Integration test needs an isolated database/service | When executor/network prerequisites are unknown |
| Matrix | Same job must test a small runtime/configuration set | For unrelated tasks with different requirements |
| `environment` | Record a deployment target/lifecycle | As a substitute for environment protection or authorization |
| Hidden template + `extends` | Standardize job defaults across a repo/library | When inheritance makes final config hard to understand |
| `include` | Separate configuration ownership or share reviewed rules | For unreviewed mutable remote config |

#### Anti-pattern catalogue

| Bad example | Why it hurts | Corrected version |
|---|---|---|
| Every job runs on every event without workflow policy | Duplicate or unwanted pipelines | Add an explicit event matrix with `workflow:rules` and job `rules` |
| Use cache to pass `release.tar.gz` to deploy | Cache can be missing/stale and is not authoritative | Publish the file as an artifact or approved package |
| `needs: [lint]` when packaging also requires tests | Packaging can run before a required check | Declare every true prerequisite |
| Print `env` to debug variables | Can expose credentials and tokens | Print an allowlist of non-secret context variables |
| Include a remote template without review/version control | A source change can alter pipeline trust | Pin or version where supported, review changes, lint consumer config |
| Make all jobs interruptible by default | Critical non-idempotent release work could be canceled | Define cancellation policy by job role and verify behavior |
| Run privileged runner for untrusted MR code | Code can attempt to steal runner credentials or reach internal systems | Isolate untrusted jobs and keep privileged capabilities separate |

#### Lab evidence requirement

For a rules experiment, record pipeline IDs, source types, commit SHA, MR state, and final status from the UI/API available to your account. Use a table rather than claiming an expected pipeline count. Representative evidence table:

| Scenario | Expected policy | Observed pipeline IDs/source | Pass? |
|---|---|---|---|
| Feature branch push without MR | Branch pipeline allowed | Fill with observed data | Yes/No |
| Push to branch with open MR | Duplicate push pipeline suppressed by intended rule | Fill with observed data | Yes/No |
| MR update | MR pipeline allowed | Fill with observed data | Yes/No |
| Tag/schedule/manual trigger | Explicitly excluded unless policy adds it | Fill with observed data | Yes/No |

### 3.5 Level 3 — Advanced

#### Configuration reuse: choose the smallest clear mechanism

- **Hidden jobs + `extends`:** good for inheriting common job settings such as image, tags, retry policy, or common scripts. Review merge behavior for nested mappings and arrays; do not assume arbitrary deep merge.
- **YAML anchors/aliases:** concise reuse within one YAML document. They are YAML features, not a cross-file template system.
- **`include`:** useful for splitting local configuration or consuming project, remote, or built-in template sources supported by the instance. Supported forms and trust/version behavior must be checked against current documentation.
- **`!reference`:** GitLab-specific mechanism for referencing selected configuration sections. It differs from YAML anchors and `extends`; validate supported combinations and evaluation behavior.
- **CI components and `spec:inputs`:** reusable components and typed/validated inputs are a direction for distributing pipeline configuration. **[VERIFY]** Current syntax, release status, version support, catalog behavior, and subscription constraints before use. Since current docs were not live-checked here, no purported production-valid component syntax is supplied.

```yaml
# File: .gitlab-ci.yml — local hidden template and extends
.default_python:
  image: python:3.12-slim
  before_script:
    - python --version
    - python -m pip install -e ".[dev]"

lint:
  extends: .default_python
  stage: lint
  script:
    - ruff check src tests

test:
  extends: .default_python
  stage: test
  script:
    - pytest -q
```

The example demonstrates a simple inheritance shape. **[VERIFY]** Validate the effective configuration with GitLab CI Lint and inspect the expanded result. Keep parent templates small; excessive inheritance can make the final job difficult to reason about.

```yaml
# File: .gitlab-ci.yml — YAML anchor within one file
.python_commands: &python_commands
  - python --version
  - python -m pip install -e ".[dev]"

lint:
  stage: lint
  image: python:3.12-slim
  before_script: *python_commands
  script:
    - ruff check src tests
```

This is YAML anchor reuse, not GitLab inheritance. A YAML parser may accept it while GitLab's full CI semantics still need server-side validation.

```yaml
# File: .gitlab-ci.yml — local include example
include:
  - local: "/ci/common-jobs.yml"
```

```yaml
# File: ci/common-jobs.yml
.common_python:
  image: python:3.12-slim
  before_script:
    - python --version
```

The included file must exist at that path in the repository and be valid for the target GitLab instance. Project/remote/template include forms should be selected only after reviewing source ownership, version pinning, authentication, and current supported syntax. **[VERIFY]** Do not use an untrusted remote include in a privileged pipeline.

#### Parent-child and multi-project pipelines

Use a parent-child pipeline to divide a repository's pipeline into smaller independently configured parts, such as service tests versus ETL validation. Use a multi-project pipeline when ownership or delivery boundaries cross repositories/projects. These are not interchangeable: access controls, variables, artifacts, status reporting, and failure propagation differ.

```text
Same project:
Parent pipeline
   |-- build/validate shared library
   |-- trigger child config for service
   |       |-- service tests
   |       `-- service package
   `-- trigger child config for ETL
           |-- schema checks
           `-- ETL tests

Cross-project:
Project A pipeline --trigger/permission boundary--> Project B pipeline
        status/inputs/artifact handoff must be designed explicitly
```

A small parent-child shape is shown below. **[VERIFY]** Trigger keywords, include form, downstream status behavior, and variable forwarding must be checked for the target version and policy. Do not assume the child inherits every parent variable or artifact.

```yaml
# File: .gitlab-ci.yml — illustrative parent-child configuration; CI Lint required
stages: [validate, downstream]

validate_parent:
  stage: validate
  script:
    - python -m pytest -q

run_service_child:
  stage: downstream
  trigger:
    include:
      - local: "/ci/service-child.yml"
    strategy: depend
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

```yaml
# File: ci/service-child.yml — illustrative child configuration
stages: [test]

service_tests:
  stage: test
  image: python:3.12-slim
  script:
    - python -m pip install -e ".[dev]"
    - python -m pytest -q
```

The `strategy` shown above is **[VERIFY: version-sensitive; validate current supported values and downstream status semantics]** and must not be copied into a production pipeline until checked. If the instance does not support the exact example or plan, use it as a design sketch only and validate an alternative with current official CI Lint. Dynamic child pipelines generate configuration as an artifact and then trigger it; this adds a code-generation trust boundary. Validate generated configuration and never allow untrusted data to become executable CI YAML without strict controls.

#### Protected, masked, and hidden variables

These controls solve different problems:

- **Protected** restricts availability to eligible protected refs under configured rules. It does not make the job code trustworthy.
- **Masked** attempts to redact the exact secret value in eligible logs, subject to value and logging constraints. Transformations, encoding, splitting, or other output paths can defeat simple redaction.
- **Hidden** concerns whether a stored variable value can be revealed again in the UI, where supported. It does not prevent the job from using or exfiltrating the value.

**[VERIFY]** Check the target instance's current documentation, settings, and plan for hidden-variable availability and exact protection semantics. Untrusted MR code should not run in a context that can access privileged variables. Avoid passing secrets through artifacts, caches, dotenv files, command-line arguments, test output, shell tracing, or screenshots. Detailed secret management and federation belong to M09.

#### OIDC `id_tokens`: identity is not authorization

OpenID Connect (OIDC) lets a job request a signed identity token for a relying party. In GitLab, `id_tokens` is a CI configuration concept whose syntax and supported claims must be checked against current documentation. **[VERIFY]** A token audience identifies the intended recipient; the relying party must validate issuer, signature, audience, claims, and trust policy. A token alone does not grant access: the external system must map that identity to an authorization policy. Do not paste real cloud credentials into this lesson. Provider-specific federation and secret architecture are deferred to M09.

#### Cancellation, `interruptible`, and `resource_group`

Canceling superseded pipelines can save capacity, but a cancellation policy must distinguish repeatable validation from non-idempotent release operations. `interruptible` and auto-cancel behavior are **[VERIFY]** version/configuration-sensitive. Do not assume every job will be canceled at the moment you expect, and do not mark a critical release step interruptible without an explicit recovery design.

`resource_group` can serialize jobs that mutate the same deployment target or other mutually exclusive resource. Serialization reduces overlapping writes but introduces queueing and throughput trade-offs. It does not make a deployment idempotent, atomic, or rollback-safe. Inspect queue behavior and ensure a stuck job has a runbook.

```yaml
# File: .gitlab-ci.yml — serialization concept; no real deployment
deploy_preview:
  stage: deploy
  script:
    - echo "simulate deployment to preview"
  resource_group: preview-environment
  environment:
    name: preview
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
```

**[VERIFY]** Validate the exact `resource_group` semantics and queue settings supported by your GitLab version. The command above has no external effect.

#### Advanced trade-off table

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Stages only | Easy to understand | Broad barriers may leave capacity idle | Overly slow pipeline as jobs accumulate | Small/simple workflows |
| `needs` DAG | Expresses precise dependencies and may shorten critical path | More dependency edges to maintain | Missing dependency allows unsafe early execution | Dependencies are clear and tested |
| `extends` | Shared job defaults | Inheritance can obscure effective config | Unexpected merge/override behavior | Reuse common job-level settings |
| YAML anchors | Lightweight same-file reuse | Limited scope and readability can suffer | Anchors mistaken for GitLab semantics | Small repeated YAML fragments |
| Local/project include | Ownership and structure separation | Additional files to inspect | Broken paths or hidden behavior | Team-owned reusable configuration |
| Remote include | Centralized shared policy | Network/source/version dependency | Mutable/untrusted source changes pipeline behavior | Source is reviewed and versioned/pinned where supported |
| Parent-child pipeline | Separate sub-workflows | More status/config complexity | Failures or evidence hidden from parent view | A repository has distinct service domains |
| Multi-project pipeline | Clear project boundary | Cross-project permission and handoff complexity | Excess privilege or confusing failure ownership | Independent project ownership |
| Auto-cancel | Avoids redundant work | May cancel work someone expected to finish | Release interruption | Replaced validation runs are safe to stop |
| `resource_group` | Serializes mutations | Queue time and potential bottleneck | Stuck lock/queue blocks delivery | Two jobs must not mutate the same target concurrently |

#### Performance/reliability design lab

Choose a pipeline for a repository containing `service/`, `shared/`, and `etl/`. The objective is not to maximize parallelism at any cost. Record job duration, queue time where available, repeated dependency installation, artifact transfer time, duplicate pipeline count, and the critical path. Compare a stage-only design with a small DAG, then state which prerequisites each edge represents.

Use the following decision record:

```text
# File: docs/pipeline-design-record.md
Decision: use explicit needs for package job
Context: package requires lint, unit tests, and schema validation
Alternatives: stage barriers only; needs on only unit tests
Chosen option: explicit dependencies on all three required checks
Risks: more edges to maintain; behavior must be checked after config changes
Verification: CI Lint + private test pipeline + inspect dependency graph
Rollback: revert the CI config commit
```

Do not claim a speedup before measuring. **[ILLUSTRATIVE]** A useful comparison is median and p95 pipeline duration across comparable runs, paired with runner queue time; the sample size and workload mix must be recorded.

### 3.6 Level 4 — Expert

#### Shared pipeline library operations

A shared pipeline library is a product with consumers, not just a folder of snippets. Define an owner, support channel, review policy, semantic versioning policy, compatibility guarantees, changelog, deprecation window, migration guide, and rollback procedure. Consumers should pin a reviewed version or immutable reference where the supported include mechanism permits it; mutable branch references can change behavior without a consumer code change.

A practical release process:

1. Change the library in a test project and validate all examples.
2. Run server-side CI Lint and representative consumer pipelines.
3. Review security impact, runner requirements, variables, and include sources.
4. Publish a versioned release according to the chosen repository policy.
5. Migrate one low-risk consumer, compare pipeline status and timing, then expand.
6. Keep a documented rollback to the previous known-good version.
7. Deprecate old interfaces with an owner, deadline, and migration support.

Avoid a single universal template that contains every organization's optional behavior. Small composable templates are easier to reason about, but too many includes create navigation and ownership overhead.

#### CI Lint and local simulation

Use GitLab's official CI Lint capability for server-side configuration validation when available. The UI location and API interface can change; do not guess an endpoint or request schema. **[VERIFY: current official CI Lint documentation and target instance UI/API]**. Check the fully expanded configuration when supported, including includes and inherited jobs. A successful lint does not prove that a runner is available, a service can start, a script succeeds, or secrets are safe.

`gitlab-ci-local` is an optional local helper. **[VERIFY]** Check its current installation, supported syntax, and fidelity limits before use. Local emulation is not equivalent to GitLab's server-side pipeline creation, scheduler, permissions, runner executor, or hosted integrations. A local check is useful feedback, not a replacement for a private test pipeline.

#### Efficiency analysis

Collect enough data to answer: where is the pipeline spending time, and which delay can this team control? Separate runner queue time from job runtime; inspect the critical path rather than summing every job duration. Look for duplicated pipeline creation, repeated setup, oversized service startup, excessive matrix combinations, unnecessary artifact transfer, and jobs that do not protect a meaningful invariant. Measure with pipeline/job records and a consistent time window. Cache optimization is treated in Unit 4; flaky-test management in Unit 6; artifact publishing in Unit 7; environment protection in Unit 9; runner scaling/security in Unit 10.

#### GitHub Actions ↔ GitLab CI mapping

GitHub Actions was the primary platform in Unit 2. GitLab CI is an additional platform for working fluency, not a replacement for that core curriculum.

| Concept | GitHub Actions | GitLab CI | Non-equivalence / design note |
|---|---|---|---|
| Events/triggers | `on:` events | Pipeline source plus `workflow:rules` | Event names and context differ; map desired behavior, not spelling |
| Pipeline creation | Workflow event filters and job conditions | `workflow:rules` | GitLab separates pipeline creation from job inclusion |
| Job | `jobs.<id>` | Top-level job entry | Both schedule units of work; execution semantics differ |
| Stage | No direct universal stage barrier; dependencies use `needs` | `stages` plus optional `needs` | GitLab stages are explicit phases |
| DAG dependencies | `needs` | `needs` | Syntax and artifact transfer behavior differ |
| Matrix | `strategy.matrix` | `parallel:matrix` | Supported expressions/limits differ; verify target version |
| Variables | `env`, `vars`, contexts | `variables`, predefined variables, settings | Scope, expansion, masking, and precedence differ |
| Secrets | `secrets` contexts / repository settings | CI/CD variables and external integrations | Security model and protected-ref rules are not equivalent |
| Artifacts | `upload-artifact` / `download-artifact` actions | `artifacts` keyword | Retention, sharing, and syntax differ |
| Cache | `actions/cache` or setup-action cache | `cache` keyword | Key and restore semantics differ |
| Reusable workflow | `workflow_call` | Includes/components/trigger patterns | Composition and interface model differ |
| Composite action | Composite action | No exact universal equivalent; scripts/templates/components | Package and execution boundaries differ |
| Conditions | `if:` expressions | `rules`, `workflow:rules`, `when` | Evaluation contexts and available variables differ |
| Services | Job `services` | `services` | Network aliasing and runner prerequisites differ |
| Runner selection | `runs-on` labels/groups | Runner tags and scope | Labels/tags are not directly interchangeable |
| Environment | `environment` | `environment` | Protection, approvals, deployment records and configuration differ |
| Concurrency | `concurrency` groups | `resource_group` for serialized jobs plus cancellation controls | Similar intent, different scope/queue/cancel semantics |
| Outputs | Step/job outputs and artifacts | dotenv reports, artifacts, variables, downstream handoff | Scope and persistence differ; do not assume one-to-one outputs |
| Manual gate | `workflow_dispatch`, protected environments/review rules | `when: manual`, environment controls | Approval semantics and plan requirements differ |
| Cancellation | Workflow/job cancellation and concurrency behavior | Auto-cancel and `interruptible` settings | Cancellation policy and exact behavior differ |
| Reusable scripts | Actions, shell scripts | `script`, included jobs, components | Packaging and distribution models differ |
| OIDC | `permissions: id-token` and provider trust | `id_tokens` and provider trust | Token claims/audience/trust policy must be mapped explicitly |
| Downstream workflows | Reusable workflows or workflow dispatch | Child/multi-project pipelines and `trigger` | Status and permission boundaries differ |

#### Migration method

1. Write down the required events and pipeline-creation policy.
2. Map each source job to a GitLab job and stage; preserve actual prerequisites.
3. Translate matrix combinations and verify supported syntax.
4. Identify every secret, artifact, cache, output, runner label/tag, and environment.
5. Rewrite conditions using target-platform variables rather than copying expressions verbatim.
6. Model cancellation and serialization separately; do not infer parity from similar names.
7. Validate YAML and expanded configuration with current GitLab CI Lint.
8. Run a private test pipeline with fake data and non-privileged credentials.
9. Compare pass/fail behavior and retained evidence, not only job names.
10. Document unresolved parity gaps and owner sign-off.

#### Failure scenarios

| Symptom | Hypothesis | Test | Root cause | Fix | Prevention |
|---|---|---|---|---|---|
| Two pipelines for one change | Branch and MR events both admitted | Compare source types, commit SHA, and pipeline IDs | No pipeline-level policy or incomplete rules | Add and validate `workflow:rules` | Maintain an event matrix test |
| Job unexpectedly skipped | No matching job rule or a prior dependency status affects it | Inspect expanded config, rule order, and upstream statuses | Rule condition differs from actual event context | Correct condition and document intended events | Test push, MR, tag, schedule, and manual cases |
| Downstream file missing | Artifact path/dependency is wrong or job did not upload | Check producer log, artifact browser, and consumer config | File not declared, wrong path, or retrieval semantics misunderstood | Declare exact path and explicit supported dependency behavior | Add artifact-existence assertion |
| Cache appears inconsistent | Cache is missing, stale, or keyed too broadly | Log cache key/path without printing sensitive content; rerun cleanly | Cache treated as authoritative state | Make build correct without cache; narrow key policy | Test cold-cache behavior |
| Secret available to untrusted job | Variable scope/protection assumptions are wrong | Review variable settings and run a harmless canary with fake value | Privileged variable exposed to untrusted code | Restrict scope/ref and isolate job; rotate exposed secret | Threat-model MR and fork pipelines |
| Job has no eligible runner | Tag/scope/protected-ref mismatch or runner offline | Inspect job pending reason and runner settings | No compatible runner can accept job | Correct permitted runner assignment or tags | Document runner contract per job |
| Included config invalid | Path, ref, syntax, or included content changed | Validate expanded config and inspect source revision | Missing or untrusted include | Correct path/version and review source | Pin/version and test consumer configurations |
| Child failure not visible as expected | Trigger strategy/status propagation assumptions are wrong | Inspect parent and child statuses and trigger config | Downstream strategy/config does not reflect intended failure policy | Use verified status propagation pattern | Add a parent-child failure test |
| Two deployments race | Both jobs can mutate same target | Inspect overlapping deployment timestamps and logs | No serialization or idempotency control | Use `resource_group` and safe deployment semantics | Test concurrent requests and recovery |

#### Policy/automation example

The following small Python check is a **text hygiene guardrail**, not a YAML parser or semantic policy engine. It rejects a few suspicious patterns in a file; it can produce false positives/negatives and cannot prove runner, variable, include, or rule behavior.

```python
# File: scripts/check_ci_hygiene.py
from __future__ import annotations

import sys
from pathlib import Path

FORBIDDEN_TEXT = (
    "only:",
    "except:",
    "printenv",
    "set -x",
)


def main() -> int:
    path = Path(".gitlab-ci.yml")
    text = path.read_text(encoding="utf-8")
    violations = [token for token in FORBIDDEN_TEXT if token in text]
    if violations:
        print("Review required for: " + ", ".join(violations))
        return 1
    print("basic text hygiene check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Command: `python scripts/check_ci_hygiene.py`

**Example — yours will differ:**
```text
basic text hygiene check passed
```

Interpretation: a pass means only that these exact text fragments were not found. It does not establish valid YAML or secure CI. A stronger policy should parse YAML safely, inspect the expanded configuration, and apply reviewed semantic rules. Keep exceptions documented with owner, reason, expiry, and compensating controls.

#### Organizational operations

- **Ownership:** identify the pipeline-library maintainer, security reviewer, runner owner, and application owner.
- **Review:** changes to includes, variables, triggers, runner tags, artifacts, and deployment jobs receive explicit review.
- **Exceptions:** time-bound, approved, and documented; avoid invisible permanent exceptions.
- **Runner trust:** separate untrusted validation workloads from privileged workloads.
- **Audit evidence:** preserve configuration revision, validation result, pipeline/job IDs, redacted logs, and deployment record where applicable.
- **Incident response:** know how to disable a compromised runner, revoke exposed credentials, revert a shared template, and identify consumers of a bad release.

### 3.7 SRE lens

Service reliability engineering (SRE) treats pipeline delivery as an operational service. Measure whether the pipeline system reliably creates the intended pipeline, runs the right checks, provides understandable failure evidence, and supports safe recovery.

| Signal / SLI | How to measure | Why it matters |
|---|---|---|
| Pipeline creation success | Intended events that produce a valid pipeline / intended events tested | Detects invalid configuration or rule regressions |
| Pipeline success rate | Successful completed pipelines / completed pipelines over a defined window | Indicates delivery friction; segment by source and failure class |
| p50/p95 pipeline duration | Time from pipeline start to terminal status | Shows typical and tail delivery latency |
| Runner queue time | Job queued-to-start time, if exposed by the instance | Separates capacity shortage from slow scripts |
| Job retry rate | Retried jobs / jobs over a time window | May reveal flaky tests or infrastructure instability |
| Duplicate pipeline rate | Duplicate/unwanted pipelines / intended changes in a controlled sample | Detects event/rules policy issues |
| Flaky-test rate | Tests with inconsistent outcomes under comparable conditions | Unit 6 owns detailed flake management |
| Deployment contention | Time waiting for serialized resource / deployments | Shows bottlenecks around shared targets |
| Recovery time | Time from incident detection to safe restoration | Measures runbook and rollback effectiveness |

Do not invent universal SLO targets. Define them from business impact, historical baseline, and team expectations. **[ILLUSTRATIVE]** A team might set an internal target for pipeline creation success, but the value should be chosen only after observing its own workload and defining what counts as an intended event.

**Runbook snippet**

```text
alert → triage → mitigation → follow-up

Pipeline creation failures spike
→ inspect recent CI config/include changes, event source, and CI Lint output
→ revert the last known-bad config or temporarily restrict affected event paths
→ add a regression case to the event matrix and review shared-library consumers

Runner queue time rises
→ compare queue time with execution time; inspect runner health, tags, capacity, and workload mix
→ reduce nonessential matrix work or route only to an approved compatible runner
→ record baseline, capacity assumptions, and follow-up owner

Deployment jobs overlap
→ inspect resource-group/target configuration and deployment timestamps
→ pause further manual triggers using approved controls; restore single-writer behavior
→ add a concurrency/recovery test and confirm deployment idempotency
```

Cost and capacity: account for runner compute, image pulls, dependency downloads, service startup, repeated pipeline creation, artifact storage, and log retention. Free-tier entitlements and quotas change; **[VERIFY]** check the current plan and instance-specific settings before promising that a workload fits a free allowance. Measure queue time and job duration on representative private test runs; do not assume a cache or matrix will improve performance without data.

### 3.8 Security lens

Use the OWASP document **Top 10 CI/CD Security Risks** and the SLSA specification/concepts as threat-modeling references, not as badges of compliance. A checklist alone does not establish compliance with either. Map each control to a threat, a verifiable check, and a limitation.

| Threat | Control | How to verify | Limitation |
|---|---|---|---|
| Untrusted contribution code reads privileged values | Keep secrets unavailable to untrusted jobs; separate privileged runner/workflow contexts | Inspect variable protection/scope, MR/fork policy, runner tags and access | Protected refs and UI settings vary; job code on a permitted ref can still misuse a secret |
| Secret exposure in logs or artifacts | Allowlist debug output; avoid tracing; narrow artifact paths and retention | Search redacted logs/config for risky output paths; inspect artifact browser | Masking can fail for transformed values; prevention is stronger than redaction |
| Runner compromise | Isolate untrusted workloads; minimize runner privileges and network reach | Review executor, host permissions, runner scope, network access | Container isolation is not an absolute boundary in every configuration |
| Mutable/malicious included configuration | Pin or version reviewed sources where supported; require review | Inspect include source/revision and code-owner review | Pinning does not prove the pinned source is benign |
| Dependency/supply-chain risk | Lock dependencies, review base images, validate outputs and provenance | Inspect lockfiles, image references, build records, and approved scanners | Unit 2/M12 cover deeper image and supply-chain controls |
| Cache/artifact poisoning | Separate trust domains, narrow cache keys, validate artifacts before use | Review producer/consumer trust and artifact paths | A valid artifact may still contain malicious content |
| Excessive permissions | Least-privilege job credentials and scoped variables | Review token permissions, project settings, external identity policy | UI/plan and provider behavior vary; audit periodically |
| Unsafe deployment race | Serialize shared target mutations and design idempotent deployment | Inspect resource-group configuration and test overlapping triggers | Serialization does not provide rollback or transactionality |
| Invalid or misleading configuration | CI Lint plus review and private execution | Save lint evidence and test event cases | Lint is not a security proof or runtime test |

**Protected branches/tags:** review who can modify protected refs and who can run jobs with privileged values. **[VERIFY]** Exact UI labels and permissions are instance/version/plan-sensitive.

**Masked/hidden/protected variables:** keep their semantics separate. Masking is not a license to print a secret; hidden storage does not prevent job code from exfiltrating it; protection does not make a malicious job safe.

**Runner trust boundaries:** an untrusted MR job should not share a privileged host, token, network route, or writable cache with release workloads unless a deliberate, reviewed design justifies it. Avoid granting broad Docker/socket access to untrusted jobs.

**Include/template trust:** treat external CI configuration as executable policy. Review source ownership, pin/version support, updates, and expanded output. CI Lint can detect some configuration defects but not malicious intent.

**OIDC:** validate issuer, signature, audience, claims, and the external trust policy. A valid token is an identity assertion; authorization is separately granted by the relying party. Provider-specific federation is deferred to M09.

**References:** OWASP *Top 10 CI/CD Security Risks*; SLSA specification and threat model/concepts. Current canonical URLs and specific versions were not live-verified for this lesson; see 3.14.

### 3.9 Production checklist

Use this checklist before merging a real pipeline change. Each item must be verifiable.

- [ ] Pipeline creation events are explicit and tested (`.gitlab-ci.yml` `workflow:rules`; compare push/MR/tag/schedule/manual cases).
- [ ] Job inclusion rules are explicit and ordered (`rules` in each relevant job).
- [ ] Stage order and `needs` edges reflect actual prerequisites; inspect the expanded config and DAG.
- [ ] Images are explicit and reviewed where a job uses an image; check image references and runner architecture.
- [ ] Runner assumptions are documented: scope, tags, executor, protected-ref eligibility, and permitted workload trust.
- [ ] Artifacts contain only named outputs/evidence, with explicit paths and retention; verify in job logs/UI.
- [ ] Cache is an optimization only; a cold-cache run still produces correct results.
- [ ] Variables are classified by sensitivity, scope, protection, and use; inspect current project/group settings without exporting values.
- [ ] Untrusted MR/fork code cannot access privileged secrets or runner capabilities; review the pipeline source and runner boundary.
- [ ] Included templates are owned, reviewed, and pinned/versioned where supported; inspect exact source revisions.
- [ ] `resource_group` or an equivalent single-writer control exists where concurrent mutations would be unsafe; test two controlled triggers.
- [ ] Cancellation behavior is deliberate; verify `interruptible`/auto-cancel behavior on a harmless test job before applying to release jobs.
- [ ] Configuration is validated with current GitLab CI Lint; save the validation evidence.
- [ ] Failure visibility is tested for downstream/child pipelines; inspect parent and child status on a deliberate test failure.
- [ ] Pipeline owner, runner owner, support path, and rollback procedure are documented.
- [ ] Exceptions have an approver, reason, compensating control, and expiry date.
- [ ] No logs, artifacts, caches, screenshots, or evidence bundles contain credentials or sensitive data.
- [ ] Current version, plan, UI, and executor-sensitive assumptions are checked against official docs and target instance settings.

### 3.10 Hands-on lab set

All labs are designed for a learner-owned private test project or local directory. Do not run them against production. **[VERIFY]** Free-tier availability, shared-runner enablement, CI minutes, artifact retention, and runner options depend on current plan and instance configuration. No cloud account or paid runner is required by the design, but a GitLab instance and a permitted runner are needed for live GitLab execution. If unavailable, do local Python tests and record the GitLab-specific part as not executed.

#### Lab A — Minimal GitLab CI pipeline

**ID | goal | steps | expected evidence | cleanup | stretch**

- **ID:** A
- **Goal:** Build a minimal lint/test pipeline and understand stages, jobs, runner scheduling, and logs.
- **Steps:**
  1. Create the repository layout from 3.3 in a private project.
  2. Add `.gitlab-ci.yml`, `pyproject.toml`, `src/scorelib.py`, and `tests/test_scorelib.py` exactly as shown.
  3. Run local checks first: `python3 -m venv .venv && . .venv/bin/activate && python -m pip install -e ".[dev]" && ruff check src tests && pytest -q`.
  4. Commit and push to the private project. **⚠ OUTWARD-FACING:** `git push` sends the commit to the configured remote; inspect `git remote -v` and ensure it is the intended private test repository first. Local-only alternative: stop after local checks and validate YAML separately.
  5. In the pipeline UI, inspect stages, job logs, runner assignment, status, and artifact list.
- **Representative command output — yours will differ:**
```text
All checks passed!
3 passed
```
  Interpretation: local Python checks passed in this illustrative example; this is not evidence that GitLab executed the pipeline.
- **Expected evidence:** committed YAML/source/tests; local output; pipeline ID/source/status; job logs with secrets redacted; runner name/scope if visible.
- **Cleanup:** delete `.venv`, `.cache`, and `.pytest_cache`; verify they are absent. Keep or delete the private test project according to your own policy; do not delete a shared/production project.
- **Stretch:** deliberately change one expected value in a test, rerun locally, record the failure, restore the test, and verify the working tree is clean.

#### Lab B — Rules and duplicate-pipeline diagnosis

- **ID:** B
- **Goal:** Demonstrate why job rules alone may not prevent duplicate branch/MR pipelines and apply a pipeline-level policy.
- **Steps:**
  1. Use only a private test project. Record its current default branch and runner policy.
  2. Create a feature branch and an MR in the private project.
  3. Test the original policy in a controlled commit, then compare the pipeline list for a push with an open MR.
  4. Apply the `workflow:rules` example in 3.4 and keep job-level rules explicit.
  5. Validate the configuration with the target instance's CI Lint UI/API as currently documented. **[VERIFY]** Do not guess an API endpoint or payload.
  6. Push the change and compare source type, commit SHA, pipeline IDs, and statuses.
- **Expected evidence:** event matrix table from 3.4 completed with observed IDs; before/after YAML; CI Lint result or screenshot/export.
- **Representative output — yours will differ:** a CI Lint UI reports whether the configuration is valid, and the pipeline list shows the source type and status for each pipeline. No fixed count is promised because settings and event conditions vary.
- **Interpretation:** the result is evidence about this instance and configuration, not a universal GitLab behavior guarantee.
- **Cleanup:** restore the desired defensive config; close/delete only the test MR/branch if no longer needed; verify no unintended pipeline remains queued.
- **Stretch:** add a deliberate tag or scheduled event to the event matrix, decide whether it should be admitted, and test the decision.

#### Lab C — DAG, artifacts, and cache

- **ID:** C
- **Goal:** Show a dependency edge, a declared output artifact, and a separate dependency cache.
- **Steps:**
  1. Add a producer job that creates `build-evidence.txt` and declares it as an artifact.
  2. Add a consumer job with a verified `needs` relationship to the producer and read the artifact only if the current GitLab syntax/configuration makes it available.
  3. Keep a package-manager cache for dependency downloads in a separate cache path.
  4. Run once with an empty cache, then again with cache present; do not assume either run is faster.
  5. Temporarily change the artifact path to a nonexistent path to create a safe failure. Inspect producer logs and the artifact browser; restore the correct path.
- **Representative command output — yours will differ:**
```text
build-evidence.txt
checks passed
```
  Interpretation: these are example file contents, not observed pipeline output. Record whether the consumer received the declared artifact and whether the cache was restored.
- **Expected evidence:** expanded DAG/config; producer/consumer job IDs; artifact file listing; cache key/path (no secret contents); cold-cache and warm-cache observations.
- **Cleanup:** revert the deliberate wrong path; remove local generated evidence; verify the pipeline is green after restoration.
- **Stretch:** explain why a release archive should be a declared artifact/package, not only a cache entry.

#### Lab D — Reuse and child pipeline

- **ID:** D
- **Goal:** Use a hidden job with `extends` and one supported include/reuse pattern; understand child pipeline ownership and failure visibility.
- **Steps:**
  1. Add `.default_python` and `ci/common-jobs.yml` examples from 3.5.
  2. Validate the include path and inheritance with the current GitLab CI Lint capability. Save the expanded config if the tool supports it.
  3. If supported on your instance, test the child pipeline sketch after verifying current `trigger`/status syntax. Use only `echo`/tests and no external deployment.
  4. Introduce a harmless failing assertion in the child test to observe how parent/child statuses appear; restore it after collecting evidence.
  5. If live child pipelines are blocked by plan or policy, submit a local design diagram and a CI-Lint-validated alternative; label child execution as simulated/not executed.
- **Expected evidence:** include source path, expanded config, parent/child pipeline IDs if live, and a short note explaining failure propagation as actually observed.
- **Representative output — yours will differ:** CI Lint result plus either a child pipeline status in the UI or a note that the instance does not permit the live experiment.
- **Cleanup:** restore passing tests and configuration; verify no child pipeline remains running and no temporary token/runner was created.
- **Stretch:** propose how the same split would work across two projects and list the extra permission and artifact/status handoff questions.

#### Lab E — GitHub Actions translation

- **ID:** E
- **Goal:** Re-express the minimal Unit 2 Python lint/test workflow in GitLab CI and identify constructs that do not map one-to-one.
- **Steps:**
  1. Use the mapping table in 3.6 to annotate the source workflow's triggers, jobs, runtime, dependencies, cache/artifacts, secrets, runner, and cancellation behavior.
  2. Create the GitLab YAML from 3.3, then add a deliberate `workflow:rules` policy appropriate for your private test project's push/MR behavior.
  3. Run local Python checks and validate the YAML with current GitLab CI Lint.
  4. Run in the private project if a permitted runner is available; compare check outcomes, not just job names.
  5. Document at least three non-equivalences: pipeline creation policy, reusable workflow/composite action composition, and runner/concurrency semantics.
- **Expected evidence:** full translated `.gitlab-ci.yml`; completed mapping table; CI Lint evidence; local/GitLab run notes; explicit parity gaps.
- **Representative output — yours will differ:**
```text
All checks passed!
3 passed
```
  Interpretation: this is illustrative local test output. GitLab runtime and workflow parity remain unverified until the target instance runs the pipeline.
- **Cleanup:** restore any temporary failing test/config; remove `.venv` and caches; verify no public release or deployment occurred.
- **Stretch:** add a small runtime matrix only after validating current syntax and measuring the capacity impact.

### 3.11 Self-check questions

1. **What is the difference between `workflow:rules` and job `rules`?**  
   **Answer:** `workflow:rules` controls pipeline creation; job `rules` controls inclusion/behavior of individual jobs.  
   **Why the wrong answer is tempting:** both use conditions and appear in the same file, but they operate at different scopes.

2. **When would `needs` be preferable to stage-only ordering?**  
   **Answer:** When a job has specific prerequisites and can safely start without waiting for unrelated jobs in earlier stages.  
   **Why the wrong answer is tempting:** stage names look like dependency declarations, but they can impose broader barriers than the real dependency graph.

3. **Why should a release file not be passed only through cache?**  
   **Answer:** Cache is an optimization and may be absent or stale; declared artifacts or an approved package channel are the appropriate output/evidence channel.  
   **Why the wrong answer is tempting:** cache files can appear in later jobs, which can look like a guaranteed handoff.

4. **How do `extends`, YAML anchors, and `include` differ?**  
   **Answer:** `extends` inherits GitLab job configuration, anchors reuse YAML nodes within a document, and `include` loads external or separate configuration sources.  
   **Why the wrong answer is tempting:** all reduce repetition, but their scopes and evaluation/merge semantics differ.

5. **Do protected or masked variables make untrusted MR code safe?**  
   **Answer:** No. Protection limits availability under configured rules; masking attempts log redaction. Neither makes the job code trustworthy or prevents all exfiltration.  
   **Why the wrong answer is tempting:** the labels sound like complete security guarantees.

6. **Why might one push create both a branch pipeline and an MR pipeline?**  
   **Answer:** The event/rule policy may admit both pipeline sources. A tested `workflow:rules` policy can suppress unwanted branch pipelines while retaining MR pipelines.  
   **Why the wrong answer is tempting:** one commit is assumed to imply one pipeline, but event-driven systems can create multiple runs.

7. **What should be checked before using CI components and `spec:inputs`?**  
   **Answer:** Current syntax, version support, availability/plan constraints, input schema, and server-side CI Lint behavior.  
   **Why the wrong answer is tempting:** examples from another instance may be out of date or use features not available on the target instance.

8. **Why is GitHub Actions `concurrency` not simply identical to GitLab `resource_group`?**  
   **Answer:** They have different scopes and cancellation/queue semantics; translate the intended invariant and test it rather than copying names.  
   **Why the wrong answer is tempting:** both can appear to serialize work, but the operational behavior is not guaranteed to match.

### 3.12 Evidence artifacts

Save the following in a learner-owned private workspace, with no credentials or sensitive logs:

1. `.gitlab-ci.yml` used for the final exercise.
2. Sample Python source, test files, `pyproject.toml`, and small schema fixture.
3. GitLab CI Lint result, expanded configuration export, or screenshot where available; otherwise record why it was unavailable.
4. Pipeline and job IDs, source type, statuses, and redacted relevant log excerpts.
5. Stage/DAG diagram showing each dependency and the reason for each edge.
6. Artifact/cache evidence: declared artifact path and downstream receipt; cache key/path and cold/warm observation.
7. Completed GitHub Actions-to-GitLab mapping table with at least three non-equivalences.
8. Lab notes with observed outputs clearly separated from representative outputs in this lesson.
9. Cleanup verification for local environments, temporary test files, test branches/MRs, and any runner/token resources created.
10. A short design decision record describing the pipeline policy, trade-offs, validation, rollback, and unresolved `[VERIFY]` items.

Never collect credentials, unredacted environment dumps, raw tokens, private customer data, or sensitive logs as evidence.

### 3.13 Common interview and design-review questions

1. **How do pipeline creation rules differ from job inclusion rules, and how would you prevent duplicate branch/MR pipelines?**  
   **Model answer:** I specify the allowed event matrix first, use `workflow:rules` to decide which pipeline sources are created, and use job `rules` to include the right jobs. I validate push/MR behavior in a private test project because project settings and version-sensitive details can change the result. I do not assume job-level rules alone eliminate duplicate pipeline creation.

2. **How do you decide between stages and `needs`?**  
   **Model answer:** Stages are simple phase barriers; `needs` expresses real prerequisites in a DAG and may reduce waiting. I add an edge for every correctness requirement, especially tests and schema checks required before packaging. I validate artifact transfer semantics and inspect the expanded graph; a faster but incomplete dependency graph is a correctness regression.

3. **How would you design a reusable pipeline library?**  
   **Model answer:** I assign ownership and support, version interfaces, document compatibility, publish changelogs, review security-sensitive changes, test consumers, and provide deprecation and rollback paths. I choose `extends`, anchors, includes, references, or components according to scope and complexity. I verify merge semantics and version/plan support rather than assuming every feature is universally available.

4. **How do you diagnose and prevent duplicate pipelines?**  
   **Model answer:** I compare pipeline source, commit SHA, event state, and rules; then test branch-without-MR, branch-with-MR, MR update, tag, schedule, and manual cases. I use a deliberate `workflow:rules` policy and keep job rules separate. I measure the observed result on the target instance instead of claiming a universal pipeline count.

5. **What is your migration strategy from GitHub Actions to GitLab CI?**  
   **Model answer:** I map event policy, dependencies, runtime, variables/secrets, artifacts/cache, reusable configuration, services, runner selection, environments, concurrency, outputs, and cancellation. I explicitly call out non-equivalences and test the intended behavior on a private pipeline. Similar names do not prove parity, especially for event creation, reusable workflow composition, runner labels/tags, and concurrency.

### Claim Register

Confidence describes the author's confidence in the general conceptual claim, not current-instance verification. No official documents were live-checked for this artifact; the verification column is therefore actionable rather than a claim of completed source review.

| ID | Section | Claim | Source (official document + section/title) | Confidence | Tag / verification action |
|---|---|---|---|---|---|
| C01 | 3.2–3.3 | `.gitlab-ci.yml` is the default project CI configuration file | GitLab CI/CD YAML syntax reference | High | [VERIFY] Confirm current file discovery and include behavior |
| C02 | 3.2–3.3 | Stages provide default phase ordering | GitLab CI/CD YAML syntax reference: `stages` | High | [VERIFY] Check current stage semantics |
| C03 | 3.2–3.3 | Jobs are scheduled to eligible runners | GitLab Runner documentation | High | [VERIFY] Check current runner terminology and scheduling |
| C04 | 3.3 | Predefined variables describe pipeline/project/commit context | GitLab predefined CI/CD variables reference | High | [VERIFY] Confirm each variable's availability by pipeline type |
| C05 | 3.4 | `workflow:rules` controls pipeline creation | GitLab CI/CD YAML syntax reference: `workflow` | High | [VERIFY] Test event matrix on target instance |
| C06 | 3.4 | Job `rules` controls job inclusion/behavior | GitLab CI/CD YAML syntax reference: `rules` | High | [VERIFY] Check evaluation order and current supported clauses |
| C07 | 3.4 | Legacy `only/except` should not be preferred for new examples | GitLab CI/CD YAML syntax and migration documentation | Medium | [VERIFY] Confirm current deprecation/migration guidance |
| C08 | 3.4 | Job rules alone may not prevent duplicate pipeline creation | GitLab documentation: `rules` and duplicate pipelines | High | [VERIFY] Test push/MR scenario for target project settings |
| C09 | 3.4 | `needs` can express DAG dependencies | GitLab CI/CD YAML syntax reference: `needs` | High | [VERIFY] Confirm options and behavior for target version |
| C10 | 3.4 | Artifact transfer behavior interacts with dependencies | GitLab CI/CD YAML syntax reference: `needs`, job artifacts | Medium | [VERIFY] Validate explicit artifact-download behavior |
| C11 | 3.4 | Artifacts are for outputs; cache is for reusable data | GitLab documentation: job artifacts and cache | High | [VERIFY] Confirm retention and backend details |
| C12 | 3.4 | Artifact retention/expiry depends on configuration and instance policy | GitLab job artifacts documentation | High | [VERIFY] Check target retention policy and plan |
| C13 | 3.4 | Services require compatible runner/executor/network setup | GitLab CI services documentation; GitLab Runner executor docs | High | [VERIFY] Test selected executor and service readiness |
| C14 | 3.4 | `parallel:matrix` supports repeated jobs across variable combinations | GitLab CI/CD YAML syntax reference: `parallel:matrix` | High | [VERIFY] Check supported syntax/limits |
| C15 | 3.4 | Environments record deployment target context but do not alone secure it | GitLab environments/deployments documentation | High | [VERIFY] Check environment behavior and Unit 9 controls |
| C16 | 3.5 | Hidden jobs and `extends` enable reusable job configuration | GitLab CI/CD YAML syntax reference: `extends` | High | [VERIFY] Inspect merge behavior and expanded config |
| C17 | 3.5 | YAML anchors/aliases are YAML-level reuse within a document | YAML specification; GitLab YAML syntax reference | High | [VERIFY] Validate anchor use in target config |
| C18 | 3.5 | `include` supports multiple configuration source forms | GitLab CI/CD YAML syntax reference: `include` | Medium | [VERIFY] Confirm currently supported forms and access rules |
| C19 | 3.5 | `!reference` is GitLab-specific configuration reuse | GitLab CI/CD YAML syntax reference: `!reference` | Medium | [VERIFY] Check combinations and evaluation order |
| C20 | 3.5 | CI components and `spec:inputs` are version-sensitive reusable config features | GitLab CI/CD components and input specification docs | Medium | [VERIFY] Confirm release/version/plan status and syntax |
| C21 | 3.5 | Parent-child and multi-project pipelines have distinct boundaries | GitLab downstream pipelines documentation | High | [VERIFY] Check trigger forms and status propagation |
| C22 | 3.5 | Dynamic child pipelines add generated configuration as an execution boundary | GitLab downstream/dynamic child pipeline documentation | High | [VERIFY] Validate generated configuration and trigger pattern |
| C23 | 3.5, 3.8 | Protected variables have ref/configuration restrictions | GitLab CI/CD variables documentation | Medium | [VERIFY] Check exact target protected-ref semantics |
| C24 | 3.5, 3.8 | Masking is not a complete guarantee against secret exposure | GitLab CI/CD variables documentation; OWASP CI/CD risks | High | [VERIFY] Review logging/output paths and masking constraints |
| C25 | 3.5, 3.8 | Hidden-variable behavior and availability are version-sensitive | GitLab CI/CD variables documentation | Medium | [VERIFY] Confirm current feature availability/UI behavior |
| C26 | 3.5, 3.8 | `id_tokens` can provide OIDC-compatible job identity tokens | GitLab CI/CD YAML syntax reference: `id_tokens`; OIDC docs | Medium | [VERIFY] Confirm syntax, claims, audience, and issuer |
| C27 | 3.5 | A token does not itself grant authorization at the relying party | OpenID Connect Core; provider trust documentation | High | [VERIFY] Review provider-side trust policy in M09 |
| C28 | 3.5 | `interruptible` and auto-cancel behavior depend on configuration | GitLab CI/CD YAML syntax reference and pipeline cancellation docs | Medium | [VERIFY] Test behavior with harmless jobs on target version |
| C29 | 3.5 | `resource_group` can serialize jobs sharing a resource | GitLab CI/CD YAML syntax reference: `resource_group` | High | [VERIFY] Check queue behavior and current options |
| C30 | 3.6 | CI Lint validates CI configuration but does not prove runtime correctness | GitLab CI Lint documentation | High | [VERIFY] Check current UI/API and expanded-config support |
| C31 | 3.6 | Local CI emulation does not equal server-side pipeline execution | `gitlab-ci-local` project documentation; GitLab CI Lint docs | Medium | [VERIFY] Inspect current supported features and limitations |
| C32 | 3.6 | GitHub Actions `on`, jobs, `needs`, matrix, artifacts, and cache have platform-specific semantics | GitHub Actions workflow syntax; artifact/cache action docs | High | [VERIFY] Compare current workflow syntax and action versions |
| C33 | 3.6 | GitHub Actions concurrency is not automatically equivalent to GitLab resource groups | GitHub Actions workflow syntax: concurrency; GitLab resource groups | High | [VERIFY] Test required serialization/cancellation invariants |
| C34 | 3.7 | Queue time and job runtime should be measured separately | GitLab pipeline/job data and runner monitoring documentation | High | [VERIFY] Identify fields available in target UI/API |
| C35 | 3.8 | CI/CD security requires threat modeling beyond configuration linting | OWASP Top 10 CI/CD Security Risks | High | [VERIFY] Review current official OWASP document |
| C36 | 3.8 | SLSA concepts concern software supply-chain integrity/provenance | SLSA specification and threat model | High | [VERIFY] Consult current specification and avoid unsupported compliance claims |
| C37 | 3.8 | Runner trust boundaries and privileged capabilities matter for untrusted code | GitLab Runner security docs; OWASP CI/CD risks | High | [VERIFY] Inspect executor, host, network, and token permissions |
| C38 | 3.9–3.10 | Private test projects and redacted evidence reduce external side effects and leakage | Operational safety practice; GitLab project/runner docs | High | Check project visibility and cleanup before labs |
| C39 | 3.6 | Shared pipeline libraries need ownership, versioning, compatibility, and rollback | Engineering design practice; GitLab include docs | High | Record owner/version policy in the consuming repository |
| C40 | 3.7 | SLO targets should be based on observed workload and impact, not universal invented values | SRE measurement practice | High | Establish baseline before setting numeric targets |

### Ten-pass self-audit report

This is a document-level review, not a claim that GitLab CI Lint or a runner executed the examples.

| Pass | Name | Defects found/fixed/open | Result |
|---|---|---|---|
| 1 | Completeness | Included sections 3.0–3.14, L1–L4, five labs, mapping table, evidence list, five interview questions, and 40 claim rows. | Pass with live validation open |
| 2 | Technical accuracy | Avoided claiming unverified version-/plan-sensitive details as universal; flagged `spec:inputs`, `!reference`, `needs`, `id_tokens`, `resource_group`, runner, and cancellation behavior. | Open: official docs must be checked |
| 3 | Executability | Supplied source/config/test files in lesson and a minimal pipeline; examples are internally reviewed for intent. | Open: CI YAML not executed or linted |
| 4 | Currency | Uses `rules` and `workflow:rules`; labels `only/except` as legacy. | Open: current migration guidance not live-verified |
| 5 | Security correctness | Warns against secret dumps, untrusted privileged runners, cache/artifact misuse, and equating OIDC identity with authorization. | Pass for teaching intent; target settings need review |
| 6 | Fabrication scan | No actual run results, speedups, quotas, versions, or API paths are claimed. Expected output is labeled representative. | Pass; URLs intentionally omitted where not verified |
| 7 | Pedagogical consistency | Progresses from minimal Python pipeline to rules/DAG, reuse, operations, and migration using a coherent service/library/ETL example. | Pass |
| 8 | Cross-consistency | Objectives map to sections/labs/evidence; labs include cleanup and verification; self-checks cover taught concepts. | Pass with target-instance checks open |
| 9 | Adversarial review | Reviewed likely objections below; unresolved live-doc/runtime concerns remain visible. | Open items listed |
| 10 | Lab safety and feasibility | No real deployment or public publication is required; Git push is explicitly labeled outward-facing and limited to a private test project. | Pass subject to runner/plan verification |

**Ten likely skeptical staff-engineer objections and resolution**

1. **“This YAML might not lint on our GitLab version.”** Resolved transparently: the artifact is not CI-Lint-validated; validate all snippets on the target instance before use.
2. **“The duplicate-pipeline rule may not match our exact event policy.”** Resolved by providing an event matrix and requiring observed testing for push/MR/tag/schedule/manual sources.
3. **“`needs` may change artifact downloads.”** Kept as an explicit verification item; declare required artifact behavior and test a producer/consumer pipeline.
4. **“The child pipeline trigger strategy may be version-sensitive.”** Marked `[VERIFY]`; treat the snippet as illustrative until current docs and CI Lint confirm it.
5. **“The component/inputs section is not a runnable component.”** Deliberate: no live docs were consulted, so the lesson explains the concept and refuses to fabricate syntax.
6. **“Masked secrets are still exfiltratable.”** Explicitly stated; masking is not treated as a security boundary.
7. **“The regex hygiene check can be bypassed.”** Explicitly labeled a text guardrail, not a semantic YAML parser or security proof.
8. **“A local emulator cannot reproduce our scheduler/runner.”** Explicitly stated; local simulation is supplemental and server-side validation/runtime evidence is required.
9. **“Free-tier assumptions may be wrong.”** No quotas are stated; current plan, runner, and retention constraints must be verified.
10. **“The sample has no real FastAPI/ETL integration.”** The core project remains intentionally resource-light and uses a scoring library plus schema fixture; the service/ETL domains are used for design scenarios, not misrepresented as a full application.

**Open verification items and exact follow-up**

- Open current official GitLab docs for YAML syntax, `rules`, `workflow:rules`, `needs`, artifacts, cache, variables/predefined variables, runners/executors, downstream pipelines, components/inputs, `id_tokens`, `resource_group`, cancellation, and CI Lint.
- Run CI Lint on each final combined YAML file and inspect expanded configuration.
- Execute Lab A in a private project with an approved runner; record observed pipeline/job IDs and outputs.
- Test the duplicate-pipeline event matrix in Lab B.
- Test artifact retrieval and cold/warm cache behavior in Lab C.
- Validate child pipeline support and failure propagation in Lab D; mark simulated if not permitted.
- Complete the GitHub Actions mapping against the actual Unit 2 workflow before claiming exact translation parity.
- Review the target project's runner scope, protected variables, project visibility, retention policy, and current subscription features.
- Do not mark the document production-verified until these items are closed and evidence is attached.

### 3.14 Sources and verification notes

**Documentation status:** Current official documentation was not live-consulted while authoring this file. The following are the official document names to consult; they are listed as verification targets, not as sources already checked. Canonical URLs are omitted rather than risk inventing or misremembering them.

1. **GitLab CI/CD YAML syntax reference** — `stages`, jobs, `script`, `image`, `variables`, `rules`, `workflow`, `needs`, `parallel:matrix`, `extends`, `include`, `!reference`, `trigger`, `interruptible`, `resource_group`, and `id_tokens`. **[VERIFY]**
2. **GitLab CI/CD job artifacts** — artifact paths, expiry/retention, downloads, and downstream use. **[VERIFY]**
3. **GitLab CI/CD caching in pipelines** — cache keys, paths, backend and trust behavior. **[VERIFY]**
4. **GitLab CI/CD variables** — masked, hidden, protected variables, scope, precedence, and settings/plan differences. **[VERIFY]**
5. **GitLab predefined CI/CD variables** — exact variable names, meanings, and availability by pipeline source. **[VERIFY]**
6. **GitLab Runner documentation** — runner scope/terminology, registration, tags, executors, protected jobs, and security. **[VERIFY]**
7. **GitLab downstream pipelines documentation** — parent-child, multi-project, dynamic child pipelines, `trigger`, and status/variable handoff. **[VERIFY]**
8. **GitLab CI/CD components and inputs documentation** — current component format, `spec:inputs`, support/version/plan constraints. **[VERIFY]**
9. **GitLab CI Lint documentation** — current UI and API capabilities, supported request fields, include expansion, and validation limitations. **[VERIFY]**
10. **GitHub Actions workflow syntax** — events, jobs, `needs`, matrix, variables, environments, concurrency, services, and cancellation. **[VERIFY]**
11. **GitHub Actions artifact and cache documentation/actions** — transfer and reuse semantics. **[VERIFY]**
12. **OWASP Top 10 CI/CD Security Risks** — relevant CI/CD threat categories and mitigations. **[VERIFY]**
13. **SLSA specification and threat model/concepts** — supply-chain integrity and provenance concepts. **[VERIFY]**
14. **OpenID Connect Core and the target identity provider's federation documentation** — token validation, issuer, audience, claims, and authorization policy. Provider-specific setup is deferred to M09. **[VERIFY]**
15. **YAML specification** — anchors and aliases as YAML-level constructs. **[VERIFY]**

**Before production use:** Check the GitLab server and Runner versions, runner executor, project/group configuration, available plan features, and the actual repository's event policy. Validate the combined `.gitlab-ci.yml` with current GitLab CI Lint, then run a private pipeline with non-sensitive test data. Review logs and artifacts for accidental secrets. Keep all unresolved `[VERIFY]` items in the change request; do not treat this authoring audit as runtime proof.

**Scope boundary:** Unit 2 remains the primary GitHub Actions reference workflow. This lesson develops GitLab CI working fluency. Unit 4 owns detailed cache/parallelism optimization; Unit 5 complex monorepo/path-based pipelines; Unit 6 quality gates and flaky-test management; Unit 7 artifact publishing; Unit 9 environment approvals/protected branches; Unit 10 self-hosted runner security/scaling; M09 secrets and identity/OIDC architecture; M12 supply-chain security and attestations; and M08 GitOps/reconciliation-based delivery.
