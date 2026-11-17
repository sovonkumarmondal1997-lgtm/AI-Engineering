# GitHub Actions: Workflows, Runners, and Reusable Workflows

> **Abstract:** This lesson teaches GitHub Actions from the execution model outward: events trigger workflows; jobs are scheduled onto runners; steps invoke actions or shell commands; dependencies, outputs, artifacts, caches, and permissions determine whether the automation is maintainable and safe. It then develops reusable workflows, composite actions, and defensive handling of untrusted pull-request data, with labs designed for a private test repository and a zero-budget laptop.

**Module:** M02 — CI/CD Pipeline Engineering  
**Stage:** 2E — Production DevOps & Platform Engineering  
**Target file:** `02-github-actions-workflows-runners-and-reusable-workflows.md`  
**Estimated time:** 10–14 hours [ASSUMPTION; revise after completing labs]  
**Last reviewed:** 2026-10-24 (authoring date; current official documentation was not live-consulted)  
**Assumed tool baseline:** Git, Python 3.11 as an example baseline, `pytest`, Ruff, GitHub Actions, and container-image concepts from M01. Verify current supported versions and action SHAs before use.

## Contents

- [2.0 Why this matters in production](#20-why-this-matters-in-production)
- [2.1 Learning objectives](#21-learning-objectives)
- [2.2 Concept map and vocabulary](#22-concept-map-and-vocabulary)
- [2.3 Level 1 — Beginner](#23-level-1--beginner)
- [2.4 Level 2 — Intermediate](#24-level-2--intermediate)
- [2.5 Level 3 — Advanced](#25-level-3--advanced)
- [2.6 Level 4 — Expert](#26-level-4--expert)
- [2.7 SRE lens](#27-sre-lens)
- [2.8 Security lens](#28-security-lens)
- [2.9 Production checklist](#29-production-checklist)
- [2.10 Hands-on lab set](#210-hands-on-lab-set)
- [2.11 Self-check questions](#211-self-check-questions)
- [2.12 Evidence artifacts](#212-evidence-artifacts)
- [2.13 Common interview and design-review questions](#213-common-interview-and-design-review-questions)
- [2.14 Sources and verification notes](#214-sources-and-verification-notes)
- [Appendix A — Claim Register](#appendix-a--claim-register)
- [Appendix B — Audit Report](#appendix-b--audit-report)
- [Appendix C — Human Verification Checklist](#appendix-c--human-verification-checklist)
- [Appendix D — Known Limitations and Assumptions](#appendix-d--known-limitations-and-assumptions)
- [Appendix E — Sign-off](#appendix-e--sign-off)

## Unit 2 — GitHub Actions: workflows, runners, reusable workflows

**Target file:** 02-github-actions-workflows-runners-and-reusable-workflows.md | **Estimated time:** 10–14 hours | **Prerequisites:** Git, shell, Python, pytest basics, M01 image-building outcomes

**Core tools:** GitHub Actions, Git, Python, pytest, Ruff, GitHub-hosted or private-repository test runner | **Awareness:** actionlint, act/local workflow runners, GitLab CI comparison (Unit 3), OIDC (M09), artifact attestation (M12) | **Last reviewed:** 2026-10-24 (authoring date; official documentation not live-checked)

### 2.0 Why this matters in production

A workflow can pass tests and still be unsafe if an untrusted pull request can influence a privileged shell command. Broad token permissions and unreviewed actions can turn a routine validation job into a supply-chain or repository-control incident. Poorly scoped triggers can run workflows unexpectedly, while missing dependencies and unclear conditions produce skipped checks or confusing results. Reusable workflows and composite actions reduce duplicated logic only when their interfaces, permissions, and versioning are deliberate. This unit builds the habits needed to understand those boundaries before operating a production pipeline.

### 2.1 Learning objectives

- [L1] Trace an event through a workflow, job, runner, step, action, and final status.
- [L1] Create and interpret a minimal Python workflow that runs Ruff and `pytest`.
- [L2] Use a matrix, `needs`, outputs, conditions, artifacts, caches, concurrency, and a service-container pattern appropriately.
- [L2] Distinguish workflow artifacts from dependency caches and explain what should cross job boundaries.
- [L3] Select between a reusable workflow, composite action, custom action, and inline steps using explicit trade-offs.
- [L3] Scope `GITHUB_TOKEN` permissions, pin third-party actions by verified full commit SHA, and avoid direct shell interpolation of untrusted expressions.
- [L3] Explain the trust differences between `pull_request` and `pull_request_target`, and the authorization requirements for OIDC.
- [L4] Diagnose workflow failures involving runner availability, conditions, permissions, artifacts, concurrency, and secrets.
- [L4] Review shared workflow policy, migration, ownership, and evidence requirements across repositories.

### 2.2 Concept map and vocabulary

```mermaid
flowchart TD
  A[Event / trigger] --> B[Workflow YAML]
  B --> C[Job dependency graph]
  C --> D[Runner allocation]
  D --> E[Steps: shell commands and actions]
  E --> F[Outputs / artifacts / cache]
  F --> G[Status checks and evidence]
  G --> H[Review, release boundary, or follow-up workflow]
  subgraph TrustBoundary[Trust boundary]
    P[Untrusted pull request] --> V[Read-only validation]
    R[Trusted protected branch] --> S[Privileged release job, narrowly scoped]
  end
```

| Term | Precise definition | Common misconception |
|---|---|---|
| Workflow | A YAML-defined automation saved under `.github/workflows/` and started by configured events or manual invocation. | The workflow file alone explains all scheduling and trust behavior. |
| Event/trigger | A GitHub event or manual/scheduled condition that can start a workflow. | Every trigger means the same trust level or available secrets. |
| Job | A collection of steps scheduled as a unit onto a runner; jobs can depend on other jobs. | Jobs run in YAML order automatically. |
| Step | A command or action invocation inside a job. | Each step gets a fresh machine. |
| Action | A reusable unit invoked as a workflow step, implemented in JavaScript, a container, or composite steps. | An action is the same as a reusable workflow. |
| Runner | The execution environment that runs a job. | A runner label proves the machine is isolated or trusted. |
| Hosted runner | A runner managed by GitHub, with image/tool details that can change over time. | The image is immutable forever. |
| Self-hosted runner | A runner operated by the repository or organization owner. | It is automatically cheaper or safer. Unit 10 covers its security in depth. |
| Context | Structured runtime information exposed by GitHub Actions, such as `github`, `runner`, `matrix`, or `needs`. | Context data is always safe to interpolate into shell source. |
| Expression | An expression written with `${{ ... }}` that GitHub evaluates in supported workflow fields. | It is equivalent to shell variable expansion. |
| Environment variable | A name/value made available to a process through its environment. | Environment variables are inherently secret. |
| Repository/environment secret | A protected value managed by GitHub and exposed only under the applicable policy and workflow conditions. | Masking guarantees it cannot leak. |
| Variable (`vars`) | Configuration value stored in repository, organization, or environment settings, depending on scope/features. | Variables are confidential credentials. |
| Step output | A named value a step exposes for later workflow use through the supported output mechanism. | It is a safe place to put tokens. |
| Job output | A selected value from a job made available to dependent jobs through `needs`. | Outputs should carry arbitrary sensitive data. |
| Workflow artifact | A file or collection of files uploaded by a run for transfer or retention. | An artifact is the same thing as a cache. |
| Cache | A reusable performance aid, typically for dependencies or build intermediates. | Cache contents are trusted release artifacts. |
| Matrix | A strategy that expands one job definition into multiple job variants. | Every matrix combination is free or necessary. |
| `needs` | The job-level dependency declaration used to require upstream jobs before a downstream job runs. | It is just a visual grouping feature. |
| Concurrency group | A key used to coordinate/cancel overlapping workflow or job runs within the documented scope. | It is a universal mutex for external systems. |
| Reusable workflow | A workflow called at the job level through `workflow_call`. | It is merely a composite action with a different filename. |
| Composite action | An action that bundles multiple steps behind an action interface. | It can define a full workflow job graph. |
| Custom action | An action packaged with its own implementation/interface, often JavaScript or a container. | Every repeated shell command deserves a custom action. |
| Permission scope | The set of token capabilities granted to a workflow or job. | Read/write permissions can be inferred safely from intent. |
| OIDC | OpenID Connect federation that can let a workflow obtain short-lived cloud identity without storing a long-lived cloud key. | OIDC itself authorizes access; trust and role policies still decide access. |
| Deployment environment | A named environment that can hold configuration/secrets and protection rules where available. | Merely naming an environment guarantees approval or isolation. |

Actions are invoked as steps (`uses:`). Reusable workflows are called at the job level and can contain multiple jobs, dependencies, and runner choices. This difference matters for reuse boundaries and permission review.

### 2.3 Level 1 — Beginner

#### The execution model

A workflow file defines *when* automation can start and *what* jobs it contains. A job is scheduled on a runner. Within that job, steps run in order; a step may execute a shell command or invoke an action. Jobs that have no dependency relationship may run concurrently, subject to available runner capacity and platform scheduling. A downstream job that declares `needs` waits for the declared upstream job or jobs according to the platform’s documented status/condition rules.

The workflow’s final status is an outcome of its jobs and conditions, not a guarantee that a production service is correct. Keep logs, tests, artifact identities, and policy decisions linked to the change.

#### Minimal Python repository

```text
github-actions-example/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── scoring_service/
│       └── __init__.py
├── tests/
│   └── test_smoke.py
├── pyproject.toml
├── README.md
└── .gitignore
```

```toml
# File: pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "github-actions-scoring-example"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8,<9", "ruff>=0.6,<1"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]
```

```python
# File: src/scoring_service/__init__.py
def score(features: list[float]) -> float:
    """Return a simple mean score for CI teaching."""
    if not features:
        raise ValueError("features must not be empty")
    return sum(features) / len(features)
```

```python
# File: tests/test_smoke.py
import pytest

from scoring_service import score


def test_score_returns_mean() -> None:
    assert score([2.0, 4.0, 6.0]) == 4.0


def test_score_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        score([])
```

```yaml
# File: .github/workflows/ci.yml
name: Python CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Check out source
        uses: actions/checkout@<FULL_40_CHAR_COMMIT_SHA> # Replace only after verifying the official release SHA.
      - name: Set up Python
        uses: actions/setup-python@<FULL_40_CHAR_COMMIT_SHA> # Replace only after verifying the official release SHA.
        with:
          python-version: "3.11"
      - name: Install package and dev tools
        run: python -m pip install --upgrade pip && python -m pip install -e ".[dev]"
      - name: Run Ruff
        run: ruff check . && ruff format --check .
      - name: Run pytest
        run: pytest
```

**Action SHA note:** the action references are deliberately non-runnable placeholders. Do not replace them with a guessed SHA. Open the official `actions/checkout` and `actions/setup-python` repositories, select the intended release, verify the full commit SHA, review the pinned source/release, and substitute that SHA. Tag references are easier to read but can move; this lesson’s secure-practice policy is to pin third-party actions by full SHA.

```bash
# From github-actions-example/
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

**Example — yours will differ**

```text
All checks passed!
2 passed in 0.04s
```

Interpretation: the local checks passed. Exact output and duration vary; this is representative output, not a record of execution.

#### YAML anatomy and triggers

- `name` is a human-readable workflow name.
- `on` declares events such as `push`, `pull_request`, `workflow_dispatch`, and `schedule`.
- `permissions` scopes the automatically provided `GITHUB_TOKEN`.
- `jobs` contains named jobs.
- `runs-on` selects a runner label or label set.
- `steps` contains shell commands and action invocations.
- `with` supplies inputs to an action; `env` supplies environment variables.
- `if` controls whether a job or step is eligible to run under its conditions.

Indentation is meaningful in YAML. Use spaces, not tabs, and keep lists and mappings at consistent levels. Some generic YAML parsers treat the unquoted word `on` differently under older YAML interpretations; use GitHub-aware tooling when validating workflow files.

Minimal trigger meanings:

| Trigger | Typical purpose | Caution |
|---|---|---|
| `push` | Validate commits pushed to selected branches | Branch filters do not replace access controls. |
| `pull_request` | Validate proposed changes | Treat contributor-controlled code and metadata as untrusted. |
| `workflow_dispatch` | Allow an authorized user to start a run manually | Inputs must still be validated; manual does not mean safe. |
| `schedule` | Run periodic checks | Timing, default branch behavior, and availability can be version/plan-sensitive `[VERIFY: GitHub Docs, Events that trigger workflows]`. |

#### Contexts, expressions, and shell variables

An expression such as `${{ github.ref }}` is evaluated by the workflow engine in a supported expression position. A shell variable such as `"$REF"` is expanded later by the shell. If untrusted text is inserted directly into the source of a `run:` script, it may alter the shell program before it runs. Moving a value into `env:` prevents that direct source interpolation, but later uses must still be quoted and validated.

Examples of context families:

- `github`: event and workflow metadata.
- `env`: workflow/job/step environment values.
- `vars`: configured non-secret variables, where available.
- `secrets`: secret values exposed under applicable policy.
- `steps`: step outputs/status within the job.
- `needs`: outputs and results from declared prerequisite jobs.
- `runner`: runner metadata.
- `matrix`: the current matrix combination.

Use only documented properties. Check current context reference before relying on a specific field `[VERIFY: GitHub Docs, Contexts]`.

#### Logs, reruns, and `GITHUB_TOKEN`

Use the run summary to identify the failed job, then inspect the earliest failing step and surrounding log context. A non-zero command exit status generally fails that step unless the workflow deliberately changes the status behavior. Reruns are useful for separating transient infrastructure errors from deterministic failures, but blind reruns can hide flaky tests.

`GITHUB_TOKEN` is a GitHub-provided token for workflow automation. Declare permissions explicitly and grant only what the workflow needs. This sample needs repository content read access and no write permissions. Never print the token or place it in an artifact, cache, output, or command argument. Masking is not a security boundary.

**What just happened?** The event starts the workflow; GitHub schedules a job on a runner; the runner checks out source, installs the project, and runs two quality tools. The workflow returns a status that can be inspected and used as a required check if repository policy is configured accordingly. A workflow file is production code and should receive review like application code.

#### Beginner mistakes

| Symptom | Likely cause | Fix |
|---|---|---|
| Workflow never starts | Trigger does not match event/branch or workflow file is not in expected location | Check `.github/workflows/`, event filters, and run history. |
| YAML parser complains | Bad indentation or invalid mapping/list structure | Use consistent spaces and a GitHub-aware linter. |
| `ModuleNotFoundError` | Package was not installed or source discovery is wrong | Install with `pip install -e ".[dev]"` and check `pyproject.toml`. |
| Action cannot be resolved | Placeholder SHA remains or reference is incorrect | Verify official action release and full SHA. |
| Job is skipped | `if` condition or upstream dependency result excluded it | Inspect conditions and job results. |
| A secret is visible in output | It was printed or copied into an artifact | Treat as exposed; revoke/rotate and remove the leak path. |

### 2.4 Level 2 — Intermediate

#### Matrix builds

A matrix expands a single job definition into several jobs with different values. This is useful for testing a small supported Python-version set or component variations. It can also multiply setup time, runner usage, and failure combinations. Use only the versions you intend to support and verify current runtime availability before adopting a version set.

```yaml
# File: .github/workflows/matrix-example.yml
name: Python matrix example

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"] # Example versions; verify the support policy for your project.
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Check out source
        uses: actions/checkout@<FULL_40_CHAR_COMMIT_SHA> # Replace after verification.
      - name: Set up Python
        uses: actions/setup-python@<FULL_40_CHAR_COMMIT_SHA> # Replace after verification.
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install and test
        run: python -m pip install -e ".[dev]" && pytest
```

**Example — yours will differ**

```text
test (3.11)  ✓
test (3.12)  ✓
```

Interpretation: each matrix value becomes a distinct job instance. This example will not run until both SHA placeholders are replaced. `fail-fast: false` lets other matrix jobs continue after a failure; use it when results across versions are useful, not as a way to ignore failures.

#### `needs`, outputs, conditions, and status functions

Use `needs` to encode real job dependencies. Job outputs should carry small, non-sensitive metadata such as a computed version or manifest path, not secret material. For step outputs, use the supported output mechanism documented by GitHub; verify exact syntax and behavior before production use `[VERIFY: GitHub Docs, Workflow commands and workflow syntax]`.

```yaml
# File: .github/workflows/dependency-example.yml
name: Dependency example

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    outputs:
      verdict: ${{ steps.check.outputs.verdict }}
    steps:
      - name: Produce a non-sensitive result
        id: check
        shell: bash
        run: |
          set -euo pipefail
          echo "verdict=pass" >> "$GITHUB_OUTPUT"

  report:
    needs: validate
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Read upstream result
        env:
          VERDICT: ${{ needs.validate.outputs.verdict }}
        run: printf 'Validation verdict: %s\n' "$VERDICT"
```

**Example — yours will differ**

```text
Validation verdict: pass
```

Interpretation: `report` waits for `validate` and receives a small non-secret output. This sample uses the documented `GITHUB_OUTPUT` mechanism; verify current workflow-command documentation before relying on more advanced output behavior.

Conditions matter. A job with `needs` normally depends on upstream results; `if` and status functions can alter whether work runs after a failure or cancellation. `success()`, `failure()`, `always()`, and `cancelled()` are documented functions, but exact interaction with implicit conditions and skipped dependencies must be checked against the current expression syntax docs `[VERIFY]`. Do not put a publish/deploy action under a broad `always()` condition: a cleanup/report step and an outward-facing release step have different safety requirements.

#### Artifacts versus caches

| Workflow artifact | Dependency/build cache |
|---|---|
| Transfers or retains output from a run, such as JUnit reports, coverage, a wheel, or a manifest | Reuses data to reduce repeated computation, such as pip downloads |
| Should be traceable to a run and checked before release use | Should be treated as an optimization, not as release evidence |
| Retention and size behavior may depend on platform/plan `[VERIFY]` | Cache keys, restore scope, eviction, and trust boundaries need deliberate policy; advanced details are Unit 4 |
| Use upload/download actions or supported artifact APIs | Use `actions/cache` or setup actions’ documented caching support |

A dependency cache key should include meaningful inputs such as operating system, runtime, and lockfile hash. Cache restoration is not proof that dependencies are correct; installation and tests still matter. Avoid writing cache entries from untrusted jobs if a trusted release job may later consume them; cache-poisoning and performance detail belongs to Unit 4.

#### Variables, secrets, concurrency, and timeouts

Use repository/environment variables for non-secret configuration and secrets for credentials. Keep precedence and scope assumptions out of undocumented folklore; check current docs when overlapping scopes matter `[VERIFY]`. Do not place credentials in workflow outputs, caches, artifacts, or shell command arguments.

`concurrency` can cancel superseded pull-request runs to save resources. Cancellation is not always safe for jobs with external side effects. Treat it as workflow coordination, not a global lock for a registry, package index, or deployment system. Add `timeout-minutes` to prevent stuck jobs from consuming capacity indefinitely; a timeout is a guardrail, not a performance target.

#### Optional service container pattern

Service containers are useful for integration tests that need a database or other dependency. The example below illustrates the shape for PostgreSQL; confirm current supported image/health-check behavior and hosted runner constraints before use `[VERIFY: GitHub Docs, Communicating with Docker service containers]`.

```yaml
# File: .github/workflows/service-container-example.yml
name: Service container example

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  integration:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: example-token-do-not-use
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U test_user -d test_db"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10
    steps:
      - name: Check out source
        uses: actions/checkout@<FULL_40_CHAR_COMMIT_SHA> # Replace after verification.
      - name: Run integration test
        env:
          DATABASE_URL: postgresql://test_user:example-token-do-not-use@localhost:5432/test_db
        run: python -m pytest -m integration
```

**Example — yours will differ**

```text
1 passed, 2 deselected
```

Interpretation: a representative integration suite completed. The fake password is not a real secret and must never be reused as one. This file is a pattern example, not part of the minimal repository unless you also add the integration marker and tests.

#### Pattern catalogue

| Pattern | When to use | When NOT to use |
|---|---|---|
| Matrix | A bounded set of supported runtime/component combinations | Every possible Cartesian combination without a support reason |
| `needs` and job outputs | Explicit dependency and small metadata transfer | Passing secrets or large files through outputs |
| Workflow artifact | Transfer test reports/build output between jobs | As a substitute for a versioned artifact repository policy |
| Dependency cache | Reuse stable dependency downloads/build intermediates | As proof of release identity or trusted provenance |
| Conditions/status functions | Gate optional reports or trusted release actions with explicit logic | To hide required failures or run privileged actions after arbitrary failures |
| Concurrency cancellation | Superseded PR validation where cancellation is safe | Publishing/deployment steps with non-idempotent side effects |
| Service container | Integration tests against a controlled local service | As a replacement for production-like contract testing |
| Secret reference | Inject a credential into a trusted job that needs it | Printing or passing the credential through outputs/artifacts |
| Reusable workflow | Share a complete multi-job pipeline contract | Tiny one-line operations where an inline step is clearer |
| Composite action | Package a stable sequence of steps | Implementing a full job dependency graph |
| Separate PR and release jobs | Keep untrusted validation separate from privileged operations | Combining untrusted code and write credentials in one job |

#### Anti-pattern catalogue

| Bad example | Why it hurts | Corrected version |
|---|---|---|
| `permissions: write-all` | Large blast radius if code or action is compromised | Explicit read-only top-level permissions; job-level elevation only when justified |
| `run: echo "${{ github.event.pull_request.title }}"` | Untrusted title becomes shell source | Pass it through `env:` and use quoted, validated shell variables |
| Mutable action tag in a security-sensitive workflow | Reference may move without a workflow diff | Pin reviewed full commit SHA and maintain update process |
| Cache treated as release artifact | Cache is an optimization with its own trust/retention behavior | Upload/checksum the release output and record its identity |
| `always()` on publish/deploy | May run after failed or cancelled prerequisites | Use explicit success and gate conditions; verify semantics |
| Matrix over every component × runtime × OS | Cost and noise grow without a clear coverage goal | Use supported combinations and measure value |
| Same broad credentials in PR and release jobs | Untrusted changes can influence privileged execution | Separate jobs/workflows and restrict event, permissions, and runner |
| Duplicated copy-paste workflow logic | Fixes drift and standards diverge | Version a reusable workflow or composite action with clear ownership |

### 2.5 Level 3 — Advanced

#### Reusable workflow, composite action, custom action, or inline steps?

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Inline steps | Simple, transparent, easy to debug locally | Duplication across callers | Copy-paste drift | Logic is small and used once |
| Reusable workflow | Shares job-level structure, dependencies, runner settings, and policy | Inputs/outputs/secrets contract and version management | Central change affects many consumers | Teams need a consistent multi-job pipeline |
| Composite action | Bundles steps behind an action interface | Limited to step composition; needs tests/versioning | Hidden behavior can make debugging harder | A repeatable sequence of steps is shared by multiple workflows |
| Custom action | Can package specialized behavior behind a reusable interface | Implementation/build/test/maintenance burden | Action implementation can introduce supply-chain or runtime risk | The behavior is substantial enough to justify an action package |

#### Complete reusable workflow with two callers

This example shares a lint-and-test job. It deliberately uses no third-party actions so the reusable-workflow interface can be studied without extra action references. It assumes the caller repositories contain the same Python project layout and `pyproject.toml`. The exact `workflow_call` schema should be checked against current official documentation before use `[VERIFY: GitHub Docs, Reusing workflows]`.

```yaml
# File: .github/workflows/reusable-python-checks.yml
name: Reusable Python checks

on:
  workflow_call:
    inputs:
      python-version:
        description: Python version to use
        required: false
        type: string
        default: "3.11"
      test-path:
        description: Test path passed to pytest
        required: false
        type: string
        default: "tests"

permissions:
  contents: read

jobs:
  checks:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Check out caller repository
        uses: actions/checkout@<FULL_40_CHAR_COMMIT_SHA> # Replace after verifying official action release SHA.
      - name: Set up Python
        uses: actions/setup-python@<FULL_40_CHAR_COMMIT_SHA> # Replace after verifying official action release SHA.
        with:
          python-version: ${{ inputs.python-version }}
      - name: Install project
        run: python -m pip install -e ".[dev]"
      - name: Lint
        run: ruff check . && ruff format --check .
      - name: Test
        env:
          TEST_PATH: ${{ inputs.test-path }}
        shell: bash
        run: |
          set -euo pipefail
          pytest "$TEST_PATH"
```

```yaml
# File: .github/workflows/call-api-checks.yml
name: API checks

on:
  pull_request:
    paths:
      - "services/api/**"
      - ".github/workflows/**"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  api:
    uses: ./.github/workflows/reusable-python-checks.yml
    with:
      python-version: "3.11"
      test-path: "services/api/tests"
```

```yaml
# File: .github/workflows/call-etl-checks.yml
name: ETL checks

on:
  pull_request:
    paths:
      - "packages/etl/**"
      - ".github/workflows/**"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  etl:
    uses: ./.github/workflows/reusable-python-checks.yml
    with:
      python-version: "3.11"
      test-path: "packages/etl/tests"
```

These caller files show the reuse contract, but they assume the repository actually has `services/api` and `packages/etl` projects with compatible install configuration. Do not paste them into the minimal repository without adapting paths and package setup. All action SHA placeholders must be replaced before execution. A called workflow has its own workflow-level permissions, and the caller cannot safely grant more than the platform’s permitted token scope; verify current permission inheritance and restrictions in the official documentation. Avoid passing secrets unless required; if a reusable workflow needs a secret, declare and pass only that secret explicitly using documented syntax.

**Versioning guidance:** local reusable workflows (`./.github/workflows/...`) follow the caller repository’s version. Cross-repository reusable workflows are typically referenced by a tag, branch, or SHA; tags are readable but can move, while a full SHA is immutable as a reference. Establish a reviewed update policy and pin a known commit for production use. Verify the current syntax and support rules before relying on it.

#### Composite action example

A composite action packages a small set of steps. The following example runs a deterministic repository check and is intentionally minimal.

```yaml
# File: .github/actions/python-static-check/action.yml
name: Python static checks
description: Install local dev tools and run Ruff
inputs:
  project-directory:
    description: Directory containing pyproject.toml
    required: false
    default: "."
runs:
  using: composite
  steps:
    - name: Install project tools
      shell: bash
      working-directory: ${{ inputs.project-directory }}
      run: python -m pip install -e ".[dev]"
    - name: Run Ruff
      shell: bash
      working-directory: ${{ inputs.project-directory }}
      run: ruff check . && ruff format --check .
```

Caller step:

```yaml
# File: .github/workflows/use-composite-action.yml
name: Use composite action

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  static-check:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Check out source
        uses: actions/checkout@<FULL_40_CHAR_COMMIT_SHA> # Replace after verification.
      - name: Set up Python
        uses: actions/setup-python@<FULL_40_CHAR_COMMIT_SHA> # Replace after verification.
        with:
          python-version: "3.11"
      - name: Reuse static-check steps
        uses: ./.github/actions/python-static-check
```

**Example — yours will differ**

```text
All checks passed!
```

Interpretation: representative output for a successful Ruff run. The sample action must be tested in the target repository after replacing the SHA placeholders in the caller. Composite action steps that use `run` must declare a shell; a composite action does not itself create a separate runner or job graph.

#### Permissions, action pinning, and trust boundaries

Set `permissions` explicitly. Start with `contents: read` when the job only checks out source and runs tests. A job that publishes a release or writes a repository file may need additional permissions, but elevate only the job that performs that action and review the trigger and trust level. Token permissions are not a substitute for code trust boundaries.

For every external action:
1. Locate its official repository and intended release.
2. Inspect release notes and relevant source.
3. Resolve the release to a full commit SHA from the official repository.
4. Record the source/release reviewed and the update process.
5. Pin the workflow to that SHA and rerun workflow validation.

Pinning prevents a tag from silently changing the referenced commit, but does not prove the pinned code is benign, well-maintained, or vulnerability-free.

#### `pull_request` vs `pull_request_target`

A `pull_request` workflow is generally the appropriate place to validate proposed changes, but it must still treat contributor-controlled code and metadata as untrusted. Do not expose privileged credentials or run untrusted code on a sensitive persistent runner. `pull_request_target` runs in a different trust context and can have access to the base repository’s workflow context/permissions; checking out and executing untrusted pull-request code in such a workflow is a dangerous pattern. Exact token/secret availability and event semantics are platform-specific and must be verified in current docs `[VERIFY: GitHub Docs, Events that trigger workflows; Secure use reference]`.

#### Script injection: unsafe and safer patterns

The unsafe pattern below is for defensive analysis only and must be used only in the learner’s own private test repository. It contains no real secret and does not contact another system.

```yaml
# File: .github/workflows/injection-vulnerable.yml
# VULNERABLE — DO NOT COPY
name: Unsafe title interpolation

on:
  pull_request:

permissions:
  contents: read

jobs:
  demonstration:
    runs-on: ubuntu-latest
    steps:
      - name: Print PR title (unsafe interpolation)
        run: echo "PR title: ${{ github.event.pull_request.title }}"
```

**Defects:** GitHub substitutes the expression into shell source before Bash parses it. A title containing shell syntax can change the command structure. The problem is not that the title is a “secret”; it is untrusted data becoming program text.

Safer approach: pass the value through the environment and treat it as data.

```yaml
# File: .github/workflows/injection-safe.yml
name: Safe title handling

on:
  pull_request:

permissions:
  contents: read

jobs:
  demonstration:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Handle PR title as data
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        shell: bash
        run: |
          set -euo pipefail
          printf 'Received a pull request title (length only): %s characters\n' "${#PR_TITLE}"
```

The safe version does not insert the title into shell source. If a later command interprets the value as a path, query, argument, or template, that use still needs validation and correct quoting. Do not use a dangerous `pull_request_target` workflow to reproduce this lab.

#### OIDC, environments, `workflow_run`, and attestations

- **OIDC:** GitHub can issue a short-lived identity token that a cloud identity provider may exchange under a configured trust policy. The workflow’s identity claims and the cloud role’s trust/authorization rules must be constrained. OIDC is not authorization by itself; M09 covers provider-specific setup.
- **Environments:** named deployment environments can associate secrets and protection rules. Availability and required-review behavior can depend on configuration and plan `[VERIFY]`. Unit 9 covers approval and promotion design in detail.
- **`workflow_run`:** a workflow can be triggered by completion of another workflow. A privileged follow-up workflow must not blindly trust artifacts or code produced by an untrusted run; validate provenance and avoid executing contributor-controlled content with write credentials. Check exact event filters and default-branch semantics in current docs before use `[VERIFY]`.
- **Artifact attestations:** provenance/attestation can help connect an artifact to a build identity and process. It does not prove the source is correct, the builder is uncompromised, or the artifact is vulnerability-free. Implementation and policy are deferred to M12 `[VERIFY: current feature names, permissions, and availability]`.

#### Trade-off table

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Inline steps | Clear for a small job | Duplication | Drift | Used once and easy to review |
| Composite action | Reuses a step sequence | Requires action tests and versioning | Hidden behavior can surprise consumers | Multiple workflows need the same bounded steps |
| Reusable workflow | Shares jobs and dependencies | Inputs/permissions/version contract | A central change can break many callers | Standard multi-job CI or release process |
| Custom action | Encapsulates complex specialized behavior | Packaging and maintenance | Runtime/dependency supply-chain risk | Stable behavior deserves its own action interface |

### 2.6 Level 4 — Expert

#### Organization-level reuse and policy

A shared workflow is a platform interface. Define an owner, supported inputs, outputs, permissions, runner assumptions, compatibility policy, release notes, versioning scheme, deprecation window, and rollback procedure. Use a pilot cohort before broad rollout. Keep a documented exception process with an owner, rationale, compensating control, and expiry date.

Organization-level required workflows and policy controls can differ by plan and change over time `[VERIFY: current GitHub organization rulesets and required-workflow documentation]`. Do not assume a UI label or feature is available in every organization. Distinguish repository branch protection/required status checks from organization-enforced policies.

#### Policy-as-code checks

`actionlint` is an optional workflow linter. Install a verified release using the project’s official repository instructions and run it against the workflow directory. This lesson has not run the linter; a human must verify its current installation method and version.

```bash
actionlint .github/workflows/*.yml
```

**Example — yours will differ**

```text
(no output on success)
```

Interpretation: no diagnostics were reported by the installed version. Silence does not prove the workflow is secure or that hosted behavior matches local expectations.

A small script can identify obvious review gaps, but regular expressions are not a full YAML parser and can produce false positives/negatives.

```python
# File: scripts/check_workflow_basics.py
from pathlib import Path
import re
import sys

WORKFLOW_DIR = Path(".github/workflows")
EXTERNAL_ACTION = re.compile(r"^\s*uses:\s*([^./][^@\s]+)@([^\s#]+)", re.MULTILINE)


def main() -> int:
    failures: list[str] = []
    files = sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(WORKFLOW_DIR.glob("*.yaml"))
    if not files:
        print(f"No workflow YAML files found under {WORKFLOW_DIR}")
        return 1

    for path in files:
        text = path.read_text(encoding="utf-8")
        if not re.search(r"(?m)^permissions:\s*$", text):
            failures.append(f"{path}: missing explicit top-level permissions block")
        for reference, version in EXTERNAL_ACTION.findall(text):
            if not re.fullmatch(r"[0-9a-fA-F]{40}", version):
                failures.append(
                    f"{path}: action {reference} uses non-SHA ref {version!r}; review/pin it"
                )

    if failures:
        print("\n".join(failures))
        return 1
    print(f"Basic regex checks passed for {len(files)} workflow file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```bash
python scripts/check_workflow_basics.py
```

**Example — yours will differ**

```text
.github/workflows/ci.yml: action actions/checkout uses non-SHA ref '<FULL_40_CHAR_COMMIT_SHA>'; review/pin it
```

Interpretation: a placeholder is intentionally flagged. The script is a rough guardrail; it does not correctly parse every YAML construct, local action, reusable workflow, comment, or expression. A robust organization policy should parse workflow YAML, validate schemas, inspect action references, and include human review.

#### Failure diagnosis table

| Symptom | Hypothesis | Test | Root cause example | Fix | Prevention |
|---|---|---|---|---|---|
| Job stays queued | No matching runner or capacity | Inspect `runs-on`, labels, and queue state | Required label unavailable | Use an available trusted runner or repair label configuration | Monitor queue time and runner capacity |
| One matrix leg fails | Version-specific dependency or runtime issue | Compare matrix logs and resolved versions | Dependency incompatible with one supported version | Fix compatibility or revise support policy deliberately | Keep a bounded tested matrix |
| Job unexpectedly skipped | `if`, `needs`, or status-function behavior | Inspect upstream result and condition | Downstream job depended on a failed/skipped job | Correct dependency/condition; keep required gate reliable | Test pass/fail/cancel paths |
| Permission denied | Token scope insufficient or wrong identity | Read API/action error and inspect permissions | Job needs a specific write permission | Grant minimum required permission only to trusted job | Permission review on every workflow change |
| Artifact missing | Upload step failed, name/path mismatch, or job did not run | Inspect upload/download logs and job graph | Consumer expects a different artifact name | Align paths/names and gate consumer on producer | Contract test artifact paths |
| Cache unexpectedly stale | Key too broad or restored state unsuitable | Compare key, lockfile hash, and installed versions | Cache key omitted lockfile | Include lockfile hash and verify install | Unit 4 cache review |
| Run cancelled | Concurrency superseded run or manual cancellation | Inspect run reason and group | Cancel-in-progress enabled for a side-effecting workflow | Separate release concurrency policy from PR policy | Review cancellation safety |
| Secret missing | Event/approval/environment policy prevents exposure | Check event type and secret scope without printing value | Untrusted context cannot access protected secret | Separate trusted release path; use approved identity model | Test with fake marker and policy review |

#### Secret exposure incident response

1. Stop the source of further exposure; disable or correct the offending workflow if necessary.
2. Revoke or rotate the affected credential immediately. Do not rely on masking or log deletion alone.
3. Identify affected workflow runs, artifacts, caches, outputs, and users with access.
4. Preserve redacted evidence and timestamps without copying the secret into an incident ticket.
5. Determine whether the credential had write/deploy scope and review activity during the exposure window.
6. Remove the unsafe logging/interpolation path, add tests/review rules, and verify the fix with a fake marker.
7. Communicate impact through the organization’s incident process and record corrective actions with owners.

#### Fork pull-request threat model

Treat contributor-controlled source, titles, branch names, and generated artifacts as untrusted. A private repository can still have untrusted collaborators or automation boundaries; repository privacy does not make all workflow inputs safe. Do not run untrusted code on a sensitive persistent self-hosted runner or give it a privileged token. Separate read-only validation from trusted publishing, and ensure a privileged follow-up workflow does not execute artifacts from an untrusted run. Unit 10 covers runner isolation and scaling in depth.

#### Workflow testing levels

1. **Static review:** inspect triggers, permissions, `uses` references, conditions, and shell interpolation.
2. **Lint/parse:** run `actionlint` or a current compatible validator after installing a verified version.
3. **Script tests:** test helper scripts and composite action behavior independently.
4. **Controlled hosted run:** test in the learner’s private repository with fake values and no production side effects.
5. **Optional local emulation:** `act` can help with selected workflows, but may not reproduce GitHub-hosted services, token permissions, OIDC, environments, every context, or all platform behavior. Its current limitations and runner-image requirements must be checked `[VERIFY: official act documentation]`.

### 2.7 SRE lens

Define service-level indicators (SLIs) before setting service-level objectives (SLOs). Do not use a single green/red rate to hide queueing, cancellation, or intermittent failures.

| SLI | Definition | SLO method |
|---|---|---|
| Workflow success rate | Successful eligible runs divided by eligible completed runs; document how cancellations/skips count | Establish a baseline by workflow and change type |
| p50/p95 duration | Wall-clock time from a declared start boundary to terminal status | Compare representative runs and separate queue time |
| Queue time | Time waiting for a runner after a run/job is eligible | Use to decide whether capacity or job optimization is the bottleneck |
| Cancellation rate | Cancelled runs divided by eligible runs, with intentional superseded runs identified | Separate expected PR cancellation from harmful cancellation |
| Retry rate | Retries divided by failed or eligible jobs, with definition stated | Watch for transient infrastructure problems and hidden flakes |
| Recovery time | Time from pipeline incident detection to normal delivery restored | Record incidents and runbook execution |
| Flake rate | Inconsistent test outcomes under repeated comparable runs | Track by test and owner; detailed handling is Unit 6 |

**[ILLUSTRATIVE]** A team might set a p95 target only after measuring representative work for several weeks. Do not adopt an arbitrary duration as a universal standard.

**Runbook: alert → triage → mitigation → follow-up**

- **Alert:** success rate, queue time, or p95 duration crosses a locally derived threshold.
- **Triage:** identify whether failure is runner allocation, workflow syntax, dependency install, test, permission, artifact, or external service.
- **Mitigation:** revert the last workflow/template change if strongly correlated; reduce nonessential matrix expansion; preserve required safety gates.
- **Follow-up:** capture redacted run ID/log excerpt, assign an owner, add a regression check, and confirm the SLI recovers.

**Cost/capacity:** use a small matrix and private test repository. Check current GitHub plan and usage limits before scaling `[VERIFY: current GitHub plan and billing documentation]`. Hosted runner images change; local WSL2 file I/O can differ from native Linux, particularly when the repository is on a mounted Windows filesystem. `act` execution also differs from hosted execution and should be treated as an aid, not the final authority.

### 2.8 Security lens

This unit addresses workflow flow-control mistakes, excessive token permissions, unsafe handling of untrusted input, secret exposure, action/dependency supply-chain risk, weak auditability, and unsafe boundaries between pull-request validation and privileged release jobs. The categories below are a conceptual mapping to OWASP’s CI/CD risk framework and SLSA concepts, not a compliance or conformance claim.

| Risk | Control taught here | Verification |
|---|---|---|
| Excessive token permissions | Explicit top-level read-only permissions; narrowly scoped job-level elevation | Inspect every workflow and called workflow permission block |
| Untrusted input becomes shell source | Move expression data to `env`, quote variables, validate downstream use | Review every `${{ github.event.* }}` used in `run:` |
| Unsafe PR trust boundary | Separate untrusted validation from privileged publish/deploy; avoid dangerous `pull_request_target` use | Inspect event, checkout ref, secrets, token scope, runner |
| Mutable action reference | Pin third-party actions to reviewed full commit SHAs | Verify every external `uses:` reference and record source/release |
| Secret exposure | Never print; avoid output/cache/artifact/process-argument leakage | Review logs and artifacts; rotate immediately if exposed |
| Artifact substitution | Record artifact checksum/digest and link to run/evidence | Compare manifest identity to the artifact used later |
| Inadequate workflow review | Require review of triggers, permissions, action updates, outputs, cache, and side effects | Inspect workflow-change review evidence |
| Privileged runner contamination | Do not run untrusted code on sensitive persistent runners | Runner scope and trust review; deeper controls in Unit 10 |

**Explicit limits**

- SHA pinning does not prove an action is benign or free of vulnerabilities.
- `GITHUB_TOKEN` permissions must be scoped; least privilege does not replace trust-boundary analysis.
- Secret masking is not a security boundary and does not guarantee that secrets cannot leak.
- OIDC reduces the need for long-lived credentials only when trust conditions and role authorization are correct; OIDC does not grant safe authorization by itself.
- A passing linter, test, scan, or protected-branch rule does not prove the workflow is secure.
- Artifact attestations can support provenance claims but do not prove the source is correct or the artifact is vulnerability-free. Implementation belongs to M12.
- Detailed self-hosted runner isolation belongs to Unit 10; provider-specific OIDC and secret architecture belongs to M09.

### 2.9 Production checklist

- [ ] Workflow files are stored under `.github/workflows/` and reviewed as code.
- [ ] Every workflow declares explicit top-level `permissions`.
- [ ] Each job has only the permissions it needs; no default `write-all` policy is used.
- [ ] Triggers and branch/path filters match the intended trust boundary.
- [ ] `pull_request_target` is not used to execute untrusted pull-request code.
- [ ] Untrusted event data is not interpolated directly into shell source.
- [ ] Third-party actions are pinned to reviewed full commit SHAs.
- [ ] SHA updates have an owner, review process, and rollback plan.
- [ ] Jobs have reasonable `timeout-minutes` values.
- [ ] Concurrency cancellation is safe for the affected workflow’s side effects.
- [ ] Matrix combinations correspond to an explicit support policy.
- [ ] `needs`, outputs, and conditions are tested for success, failure, skip, and cancellation paths.
- [ ] Secrets are not printed or passed through outputs, caches, artifacts, or command arguments.
- [ ] Workflow artifacts are distinguished from dependency caches.
- [ ] Cache keys include relevant dependency/runtime inputs and cache trust is reviewed.
- [ ] Reusable workflow interfaces define supported inputs, outputs, permissions, and versioning.
- [ ] Composite actions are tested and declare shells for `run` steps.
- [ ] Called workflows and caller workflows have compatible permission assumptions.
- [ ] Service-container tests use readiness checks or bounded retries, not only fixed sleeps.
- [ ] Runner labels and trust are reviewed; labels alone are not treated as isolation.
- [ ] `workflow_run` follow-ups do not blindly execute untrusted artifacts/code.
- [ ] Environment protection and UI/plan-specific behavior are verified.
- [ ] Required status checks report reliably; path-filter pitfalls are handled in Unit 5.
- [ ] Logs/artifacts retained as evidence are redacted and have an owner.
- [ ] Incident response covers token rotation, run identification, and prevention.
- [ ] Every exception has rationale, owner, compensating control, and expiry.
- [ ] A linter and controlled private-repository run are part of validation; neither is treated as a security proof.

### 2.10 Hands-on lab set

All outputs below are representative and have **not** been executed during authoring. Perform remote exercises only in your own private test repository. Replace action SHA placeholders only after official verification. Every lab ends with cleanup and a check that cleanup occurred.

#### Lab 1 — Minimal Python CI and controlled failure

**Goal:** create the minimal project, run lint/tests locally, and observe a failure in a private GitHub repository.

**Prerequisites:** Git, Python, pip, and access to a private test repository.

**Steps**

1. Create the files in Section 2.3.
2. Create `.github/workflows/ci.yml` from the minimal workflow.
3. Verify and replace action SHA placeholders from official action repositories.
4. Run local checks, push to the private test repository, and inspect the run.
5. Change the expected mean from `4.0` to `5.0`, rerun, diagnose the failure, restore the test, and rerun.

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest -q
```

**Example — yours will differ**

```text
All checks passed!
2 passed in 0.04s
```

Interpretation: all local checks passed. If the deliberate test edit is made, pytest should fail with an assertion mismatch; restore the expected value before pushing the final change.

**Expected evidence:** workflow file, action SHA review note, successful run link/ID, redacted failure/success output, and cleanup confirmation.

**Cleanup and verification:** restore the test, remove `.venv`, verify no local environment remains, and archive only redacted evidence.

```bash
deactivate 2>/dev/null || true
rm -rf .venv
test ! -e .venv && echo "cleanup verified"
```

**Example — yours will differ**

```text
cleanup verified
```

Interpretation: local virtual environment removed. Removing the private repository is an optional **⚠ DESTRUCTIVE** action; export required evidence and verify the repository identity before deletion.

#### Lab 2 — Script injection: reproduce safely, then fix

**Goal:** understand why expression interpolation can turn untrusted pull-request metadata into shell syntax, then correct the pattern.

**Safety scope:** use only your own **private test repository**, fake data, and a benign marker. Do not add real secrets. Do not use `pull_request_target` to execute untrusted code. The vulnerable workflow below is for controlled defensive analysis only.

**Vulnerable version — do not copy**

```yaml
# File: .github/workflows/injection-vulnerable.yml
# VULNERABLE — DO NOT COPY
name: Injection training (private test repository only)

on:
  pull_request:

permissions:
  contents: read

jobs:
  demo:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Print title unsafely
        run: echo "Title: ${{ github.event.pull_request.title }}"
```

Defect: the expression is substituted into the shell program before the shell parses it. A title containing shell syntax can change the program structure. Use a benign title marker that causes only a harmless printed marker such as `INJECTION_PROOF`; do not include commands that read files, access credentials, make network requests, persist state, or modify resources. If your repository configuration does not allow safe control of PR title metadata, skip the live vulnerable run and perform a code review-only analysis.

**Corrected version**

```yaml
# File: .github/workflows/injection-safe.yml
name: Safe PR metadata handling

on:
  pull_request:

permissions:
  contents: read

jobs:
  demo:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Handle title as data
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        shell: bash
        run: |
          set -euo pipefail
          printf 'PR title length: %s\n' "${#PR_TITLE}"
```

**Steps**

1. Inspect the vulnerable line and write down the data-to-code risk before running anything.
2. If you can safely control the title in your own private repository, use only the benign marker. Do not attach secrets or elevated permissions.
3. Observe whether the unsafe version interprets shell syntax; save only redacted evidence. If safe reproduction cannot be guaranteed, skip execution and record a static review finding.
4. Replace the vulnerable version with the corrected version and rerun the controlled workflow.
5. Review all later uses of the environment variable; `env:` reduces direct interpolation risk but does not make every downstream use safe.

**Example — yours will differ**

```text
PR title length: 31
```

Interpretation: the corrected workflow treats the title as a string value and prints only its length. Output varies with the title. The vulnerable workflow’s exact output depends on the benign test input and should never be tried with a real secret or privileged context.

**Expected evidence:** before/after YAML, a short threat explanation, redacted run ID/output if safely executed, and a note confirming no real secret was used.

**Cleanup and verification:** remove the vulnerable workflow, keep only the corrected workflow if desired, verify no test token/secret was created, and check the final workflow has read-only permissions.

#### Lab 3 — Reusable workflow with two callers

**Goal:** create a shared workflow and invoke it from two distinct caller workflows.

**Prerequisites:** a private test repository with the API and ETL directories shown below, each with compatible Python package configuration. If your repo is a single-package repository, use two caller workflows with different `test-path` inputs that point to existing test directories.

**Steps**

1. Create `.github/workflows/reusable-python-checks.yml` from Section 2.5.
2. Create `.github/workflows/call-api-checks.yml` and `.github/workflows/call-etl-checks.yml`.
3. Replace action SHA placeholders after verification.
4. Confirm each caller uses the local reusable workflow at the job level and passes only non-secret inputs.
5. Run both callers manually or via a matching PR and compare run evidence.

**Example — yours will differ**

```text
API checks: success
ETL checks: success
```

Interpretation: two caller workflows invoked the same shared check contract with different test paths. The example is only valid if the caller repository layout and package install commands match.

**Expected evidence:** all three workflow files, successful caller run IDs, input/permission review, and a short note about what remains caller-specific.

**Cleanup and verification:** delete the temporary caller files if not retained, verify no secret was passed, and confirm no runner or external resource was created.

#### Lab 4 — Permissions, logs, and failed-job diagnosis

**Goal:** cause a harmless test failure or a read-only permission denial, inspect logs, fix it, and retain evidence.

**Steps**

1. Start from a private read-only validation workflow.
2. Prefer a harmless failing test first; do not attempt a write operation against a real resource merely to force a permission error.
3. Read the first failed step, capture its exit code and relevant redacted output, and identify whether the failure is code, configuration, or authorization.
4. Fix the test/configuration or remove the unnecessary write attempt.
5. Verify the workflow is green and the permissions remain least-privilege.

**Example — yours will differ**

```text
FAILED tests/test_smoke.py::test_score_returns_mean
assert 4.0 == 5.0
1 failed
```

Interpretation: the failure is a test assertion, not a permission issue. A deliberate permission-denial exercise should use a safe, non-mutating check in the private repository and must not expand permissions merely to make the run green.

**Expected evidence:** redacted failure and successful rerun, permissions review, and diagnosis note.

**Cleanup and verification:** restore the correct assertion, remove any temporary files, confirm no real token was created or printed, and run the basic workflow check again.

#### Lab 5 — Workflow policy review

**Goal:** use a repeatable checklist/script to find missing permissions, unpinned action references, unsafe shell interpolation, and unclear ownership.

**Steps**

1. Run `actionlint` after installing a verified release.
2. Run `python scripts/check_workflow_basics.py` from Section 2.6.
3. Manually inspect each `${{ github.event.* }}` occurrence in a `run:` field, every secret reference, all `if` conditions, and any publish/deploy side effect.
4. Create a risk-ranked review report with owner and remediation date.
5. Do not treat a clean regex report as proof that the workflow is secure.

```bash
python scripts/check_workflow_basics.py
```

**Example — yours will differ**

```text
.github/workflows/ci.yml: action actions/checkout uses non-SHA ref '<FULL_40_CHAR_COMMIT_SHA>'; review/pin it
```

Interpretation: the simple policy check flags a placeholder or mutable ref. The script is not a complete YAML parser and may produce false positives or miss constructs.

**Expected evidence:** linter output, policy script output, completed review checklist, and open-items report.

**Cleanup and verification:** remove temporary sample workflows or retain only approved versions, verify no fake secret appears in logs/artifacts, and ensure the private test repository has no unused credentials or runner registrations.

### 2.11 Self-check questions

1. **What is the difference between an action and a reusable workflow?**  
   **Answer:** An action is invoked as a step; a reusable workflow is called at the job level and can compose jobs/dependencies. **Tempting wrong answer:** both package repeated automation, but they have different execution boundaries.

2. **Why set `permissions: contents: read` in a validation workflow?**  
   **Answer:** It explicitly limits the token to the repository content access needed by the example. **Tempting wrong answer:** broad permissions seem convenient, but convenience expands blast radius.

3. **Why is a full action commit SHA preferable to a moving tag for secure pinning?**  
   **Answer:** The SHA pins a specific commit reference; a tag may move. **Tempting wrong answer:** a readable version tag feels fixed, but tags are mutable unless policy prevents movement.

4. **Why is direct `${{ github.event.* }}` interpolation inside `run:` risky?**  
   **Answer:** Untrusted data may become shell source before parsing. Pass it through `env:` and quote/validate subsequent use. **Tempting wrong answer:** the expression looks like a variable, but it is inserted into the script text.

5. **Does moving a value into `env:` make all uses of it safe?**  
   **Answer:** No; downstream commands may still interpret it as a path, query, or program fragment. **Tempting wrong answer:** environment variables are safer at the boundary but do not replace validation.

6. **What is the difference between an artifact and a cache?**  
   **Answer:** Artifacts transfer/retain outputs and evidence; caches optimize repeated work. **Tempting wrong answer:** both store files, but their trust and lifecycle purposes differ.

7. **When is `cancel-in-progress` inappropriate?**  
   **Answer:** When cancellation can interrupt a non-idempotent publish/deploy side effect or leave external state inconsistent. **Tempting wrong answer:** cancelling always saves capacity, but not every workflow is disposable.

8. **What does OIDC guarantee?**  
   **Answer:** It can provide a federated short-lived identity token; authorization still depends on correctly constrained trust conditions and role policy. **Tempting wrong answer:** identity issuance is confused with permission to act.

9. **Why is `pull_request_target` dangerous if it checks out and executes untrusted code?**  
   **Answer:** The workflow can have a more privileged trust context than the contributor’s code deserves. **Tempting wrong answer:** the event name sounds like an ordinary PR event, but the trust model differs.

10. **What should you do after discovering a secret in workflow logs?**  
    **Answer:** Stop exposure, revoke/rotate the credential, identify affected runs/artifacts/access, preserve redacted evidence, fix the leak, and verify prevention. **Tempting wrong answer:** deleting the line or relying on masking does not invalidate an exposed credential.

### 2.12 Evidence artifacts

Save the following locally. Do not upload secrets, customer data, or unredacted sensitive logs.

```text
evidence/M02-U02/
├── minimal-ci/
│   ├── ci.yml
│   ├── local-lint-output.txt
│   ├── local-test-output.txt
│   └── hosted-run-reference.md
├── reusable-workflows/
│   ├── reusable-python-checks.yml
│   ├── call-api-checks.yml
│   ├── call-etl-checks.yml
│   └── caller-run-results.md
├── security/
│   ├── injection-before-after.md
│   ├── permission-review.md
│   └── action-sha-review.md
├── policy/
│   ├── actionlint-output.txt
│   ├── policy-script-output.txt
│   └── workflow-review-checklist.md
└── verification/
    ├── cleanup-confirmation.md
    └── open-items.md
```

Keep only the minimum evidence needed. Run links/IDs can be recorded instead of copying full logs. Redact repository identifiers if organizational policy requires it. Clearly label synthetic outputs `[ILLUSTRATIVE]`.

### 2.13 Common interview and design-review questions

1. **When would you choose a reusable workflow over a composite action?**  
   A reusable workflow is appropriate when the shared unit includes jobs, dependencies, runner selection, permissions, or a multi-stage contract. A composite action is appropriate for a reusable sequence of steps inside a job. I would compare consumer needs, versioning, debuggability, interface stability, and ownership before deciding; a tiny one-off command may be clearest inline.

2. **How do you prevent pull-request metadata from becoming a shell-injection path?**  
   I avoid interpolating untrusted `${{ github.event.* }}` expressions directly into `run:` source. I pass values through `env:`, quote shell variables, validate values before using them in commands, and avoid running untrusted code in a privileged `pull_request_target` workflow. I test the pattern only in a private repository with a benign marker and no credentials.

3. **How do you secure action dependencies and `GITHUB_TOKEN`?**  
   I set explicit top-level read-only permissions, elevate only the job that requires additional access, and review the event trust boundary. I pin third-party actions to verified full commit SHAs, inspect the pinned source/release, and maintain an update process. SHA pinning reduces mutable-reference risk but does not prove the action is safe.

4. **A workflow is stuck or one matrix leg fails. How do you debug it?**  
   I separate queueing from execution, inspect runner labels and job logs, compare matrix-specific runtime/dependency versions, then inspect conditions, permissions, and artifact/cache paths. I preserve the first failure and avoid blind retries. I make one hypothesis-driven change, rerun the relevant case, and add a regression check if the failure is reproducible.

5. **How would you govern reusable workflows across hundreds of repositories?**  
   I would assign platform ownership, publish a versioned interface with documented inputs/outputs/permissions, test compatibility, pilot updates, and provide release notes and rollback. I would enforce pinning and review policy where supported, measure adoption and upgrade lag, and require exceptions to have an owner and expiry. Organization-level features and plan availability must be verified before committing to a specific enforcement mechanism.

### 2.14 Sources and verification notes

**Source status:** The supplied prompt was used to define scope. The official documentation below was **not live-consulted during authoring**. URLs are canonical candidates based on known documentation structure; a human must confirm current pages, fields, and behavior before production use. No workflow, command, or linter was executed while authoring this document.

- GitHub Docs — *Understanding GitHub Actions*: https://docs.github.com/en/actions/about-github-actions
- GitHub Docs — *Workflow syntax for GitHub Actions*: https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
- GitHub Docs — *Events that trigger workflows*: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows
- GitHub Docs — *Using jobs in a workflow*: https://docs.github.com/en/actions/using-jobs
- GitHub Docs — *Contexts*: https://docs.github.com/en/actions/learn-github-actions/contexts
- GitHub Docs — *Expressions*: https://docs.github.com/en/actions/learn-github-actions/expressions
- GitHub Docs — *Workflow commands*: https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions
- GitHub Docs — *Store and share data with workflow artifacts*: https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts
- GitHub Docs — *Dependency caching*: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows
- GitHub Docs — *Using secrets in GitHub Actions*: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
- GitHub Docs — *Controlling permissions for `GITHUB_TOKEN`*: https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication
- GitHub Docs — *Reusing workflows*: https://docs.github.com/en/actions/using-workflows/reusing-workflows
- GitHub Docs — *Creating a composite action*: https://docs.github.com/en/actions/creating-actions/creating-a-composite-action
- GitHub Docs — *Secure use reference*: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- GitHub Docs — *Workflow syntax / `pull_request_target` and `workflow_run` events*: use current event reference above and verify exact current event semantics.
- GitHub Docs — *Managing environments for deployment*: https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment
- GitHub Docs — *GitHub-hosted runners*: https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners
- GitHub Docs — *Self-hosted runners*: https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners
- GitHub Docs — *OpenID Connect*: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-for-github-actions/about-security-hardening-with-openid-connect
- GitHub Docs — *Artifact attestations*: https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations
- OWASP — *Top 10 CI/CD Security Risks*: https://owasp.org/www-project-top-10-ci-cd-security-risks/
- SLSA — official framework/specification: https://slsa.dev/
- `actionlint` — official repository and documentation: https://github.com/rhysd/actionlint
- `act` — official repository and documentation: https://github.com/nektos/act

**Open verification items**

- `[VERIFY: workflow syntax and contexts]` Confirm current keys, context properties, expression/status-function semantics, job outputs, and event filters.
- `[VERIFY: action SHAs]` Replace every placeholder only after reviewing the intended official action release and confirming its full commit SHA.
- `[VERIFY: Python and tool baseline]` Confirm Python and package/tool versions fit the target project’s support policy.
- `[VERIFY: reusable workflow contract]` Verify `workflow_call` inputs, outputs, permission inheritance, and caller syntax against current docs.
- `[VERIFY: event trust]` Confirm current `pull_request`, `pull_request_target`, and `workflow_run` semantics before adopting security-sensitive patterns.
- `[VERIFY: artifact/cache behavior]` Check current artifact action interfaces, retention, cache scope, eviction, and plan constraints.
- `[VERIFY: service containers]` Confirm runner constraints, service-container networking, health-check behavior, and image maintenance policy.
- `[VERIFY: environments and OIDC]` Confirm current UI/plan availability, environment protection behavior, OIDC claims, and cloud trust configuration.
- `[VERIFY: attestation]` Confirm current feature names, permissions, and plan/organization availability; this lesson does not implement attestation.
- `[VERIFY: actionlint and act]` Install verified releases and test current support/fidelity limits.
- `[VERIFY: free tier]` Check current plan and usage documentation; no quotas are asserted here.
- `[VERIFY: YAML parser]` Use GitHub-aware validation; generic YAML parser behavior can differ.

---

## Appendix A — Claim Register

| ID | Section | Claim | Source (official document + section/title) | Confidence | Tag / verification needed |
|---|---|---|---|---|---|
| A01 | 2.2–2.3 | Workflow files define triggers and jobs in GitHub Actions. | GitHub Docs, *Workflow syntax for GitHub Actions* | High | `[VERIFY]` live docs not consulted |
| A02 | 2.2 | Jobs run on runners and contain ordered steps. | GitHub Docs, *Using jobs in a workflow* | High | `[VERIFY]` |
| A03 | 2.2–2.4 | Reusable workflows are called at job level; actions are invoked as steps. | GitHub Docs, *Reusing workflows*; *Creating a composite action* | High | `[VERIFY]` |
| A04 | 2.3 | `push`, `pull_request`, `workflow_dispatch`, and `schedule` are workflow trigger events. | GitHub Docs, *Events that trigger workflows* | High | `[VERIFY]` current event details |
| A05 | 2.3 | Explicit `permissions: contents: read` fits the minimal read-only example. | GitHub Docs, *Automatic token authentication* | Medium | Run in private test repo |
| A06 | 2.3, 2.5 | Directly interpolating untrusted event data into shell source can create script-injection risk. | GitHub Docs, *Secure use reference* | High | `[VERIFY]` |
| A07 | 2.5 | Passing untrusted data through `env:` reduces direct expression-to-shell-source injection risk. | GitHub Docs, *Secure use reference* | High | Review downstream use; not a universal sanitizer |
| A08 | 2.4 | `needs` creates explicit job dependency relationships. | GitHub Docs, *Workflow syntax for GitHub Actions* | High | `[VERIFY]` exact conditions |
| A09 | 2.4 | `GITHUB_OUTPUT` is a supported mechanism for setting step outputs. | GitHub Docs, *Workflow commands* | High | `[VERIFY]` |
| A10 | 2.4 | Workflow artifacts transfer/retain outputs while caches optimize repeated work. | GitHub Docs, *Workflow artifacts*; *Dependency caching* | High | `[VERIFY]` current action interfaces/limits |
| A11 | 2.4 | Matrix strategy expands jobs across declared combinations. | GitHub Docs, *Workflow syntax for GitHub Actions* | High | `[VERIFY]` |
| A12 | 2.4 | `concurrency` can coordinate overlapping runs and cancel superseded work. | GitHub Docs, *Workflow syntax for GitHub Actions* | High | `[VERIFY]` scope and semantics |
| A13 | 2.4 | `timeout-minutes` can bound job duration. | GitHub Docs, *Workflow syntax for GitHub Actions* | High | `[VERIFY]` |
| A14 | 2.5 | Full-SHA action pinning avoids relying solely on a potentially moving tag. | GitHub Docs, *Secure use reference* | High | Verify each selected SHA |
| A15 | 2.5 | SHA pinning does not prove the pinned action is benign. | Security design limitation; GitHub Docs, *Secure use reference* | High | Human source review still required |
| A16 | 2.5 | `pull_request_target` has a different trust context and must not execute untrusted PR code with privileged access. | GitHub Docs, *Events that trigger workflows*; *Secure use reference* | High | `[VERIFY]` current event semantics |
| A17 | 2.5 | OIDC can reduce the need for long-lived cloud credentials. | GitHub Docs, *About security hardening with OpenID Connect* | High | `[VERIFY]` provider configuration |
| A18 | 2.5 | OIDC identity does not itself authorize cloud operations. | GitHub Docs, *About security hardening with OpenID Connect* | High | Trust and role policies must be reviewed |
| A19 | 2.5 | Environment protection behavior can depend on configuration and plan. | GitHub Docs, *Managing environments for deployment* | Medium | `[VERIFY]` current plan/UI |
| A20 | 2.5 | `workflow_run` follow-ups must treat upstream artifacts/code according to their trust level. | GitHub Docs, event reference; *Secure use reference* | High | `[VERIFY]` exact event behavior |
| A21 | 2.5 | Artifact attestations can support provenance claims but do not prove code correctness. | GitHub Docs, *Artifact attestations*; SLSA docs | High | `[VERIFY]` current features/availability |
| A22 | 2.6 | Regex policy checks are not a complete YAML/workflow parser. | General parser/tooling limitation | High | Validate with parsed YAML and human review |
| A23 | 2.7 | Queue time and execution time should be separated to diagnose pipeline delay. | SRE measurement design | High | Measure local baseline |
| A24 | 2.7 | No universal workflow-duration target is appropriate without local baseline/context. | SRE measurement design | High | Targets should be locally derived |
| A25 | 2.8 | Secret masking does not guarantee secret non-disclosure. | GitHub Docs, *Using secrets in GitHub Actions* | High | `[VERIFY]` |
| A26 | 2.8 | A passing linter or workflow run does not prove security. | Security engineering principle | High | Human threat review required |
| A27 | 2.10 | The vulnerable lab is restricted to a private test repository and benign marker. | Lab safety constraint in this lesson | High | Do not use real secrets or third-party targets |
| A28 | 2.10 | The reusable-workflow example assumes compatible package/test paths exist in the caller repository. | Explicit example assumption | High | `[ASSUMPTION]` adapt paths before use |
| A29 | 2.3–2.5 | Example outputs and durations are representative, not execution results. | Authoring record | High | Explicitly disclosed |
| A30 | 2.14 | Official docs were not live-consulted during authoring. | Authoring record | High | Human verification required |

## Appendix B — Audit Report

This is an AI self-audit, not an independent human audit or an execution-based validation. The status reflects content review only; no workflow, command, `actionlint`, or `act` run was performed during authoring.

| Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|
| 1 — Completeness | PASS | Risk of omitting mandatory labs or exact question count | Included sections 2.0–2.14, four levels, five labs, exactly five interview questions, and appendices A–E | Human should cross-check against source prompt |
| 2 — Technical accuracy | OPEN | Current syntax and platform behavior not live-verified | Used familiar documented patterns and marked uncertain/current details `[VERIFY]` | Workflow fields/conditions may change or need nuance |
| 3 — Executability | OPEN | Action SHA placeholders prevent direct execution; caller package paths are assumptions | Clearly marked placeholders and documented path assumptions | Replace SHAs and run in private repo; linter not run |
| 4 — Currency | OPEN | Current action releases, runner images, plan/UI behavior not checked | Added specific verification list | Human must consult current docs |
| 5 — Security correctness | PASS | Main risks are script injection, broad permissions, secrets, event trust | Added safe `env:` pattern, read-only permissions, private benign lab, incident steps | Safe pattern still requires downstream validation and human review |
| 6 — Fabrication scan | PASS | Risk of invented SHAs, quotas, timings, or execution claims | No SHA values or quotas invented; outputs labelled representative; no execution claimed | Current URLs/claims still need checking |
| 7 — Pedagogical consistency | PASS | Risk of jumping into advanced YAML before execution model | Introduced workflow/job/runner model before matrices and reuse | Learner may need additional practice with YAML |
| 8 — Cross-consistency | OPEN | Reusable caller example assumes multi-package paths | Documented assumption and adaptation requirement | Must align with actual repository layout |
| 9 — Adversarial review | PASS | Potential objections about SHA placeholders, OIDC, artifacts, and linter limitations | Explicitly documented limitations and review steps | Human security review still required |
| 10 — Lab safety and feasibility | OPEN | Live vulnerable demonstration can be unsafe if adapted carelessly | Restricted to private repository, benign marker, no credentials/network/destructive commands; static-review alternative supplied | Learner must follow scope exactly and remove vulnerable file |

### Ten likely skeptical staff-engineer objections

1. **“The workflows are not immediately runnable because the action SHAs are placeholders.”**  
   Accepted: no SHA is fabricated. Verify the official release and replace every placeholder before use. This is a deliberate safety control, not a claim of executability.

2. **“The package uses dependency version ranges rather than a complete lockfile.”**  
   Accepted: the small example is pedagogical. A production repository should use its chosen dependency manager and lockfile policy; cache and lockfile design are covered in Unit 4.

3. **“The reusable callers refer to paths not present in the minimal tree.”**  
   Accepted and disclosed: the callers are a separate multi-package example and assume those paths exist. Adapt the inputs or create the described layout before running.

4. **“The vulnerable script-injection lab should not be run in a privileged workflow.”**  
   Accepted: it is restricted to the learner’s private test repository, read-only permissions, fake metadata, and a benign marker. If safe control cannot be guaranteed, do static review only.

5. **“Using `env:` does not sanitize arbitrary downstream command use.”**  
   Accepted: the lesson explicitly states that downstream use still requires quoting and validation.

6. **“A read-only token can still read repository content and execute untrusted tests.”**  
   Accepted: read-only permissions reduce impact but do not remove all risk. Runner isolation and untrusted-code boundaries still matter; Unit 10 covers runner security.

7. **“The regex policy script is too weak for organization-wide enforcement.”**  
   Accepted: it is labelled a rough guardrail with false-positive/negative risks. Organization policy should parse workflow YAML and combine automated checks with review.

8. **“`act` may not reproduce hosted behavior.”**  
   Accepted: the lesson calls out limitations and requires controlled hosted validation for relevant behavior.

9. **“Environment, OIDC, and attestation features may vary by plan or change.”**  
   Accepted: these are marked `[VERIFY]` and implementation is deferred to M09/M12/Unit 9 where appropriate.

10. **“No workflow was run, so syntax and outputs remain unproven.”**  
    Accepted: authoring status is draft-audited; all outputs are representative and a human must run the linter and labs.

## Appendix C — Human Verification Checklist

| Area | What to verify | Official document / section | How to test |
|---|---|---|---|
| Workflow syntax/events | `on`, triggers, branches/paths, `workflow_dispatch`, `schedule`, `workflow_run` | GitHub Docs, *Workflow syntax for GitHub Actions*; *Events that trigger workflows* | Run a GitHub-aware linter and test each required trigger in a private repository |
| Contexts/expressions | Context names, properties, status functions, implicit conditions | GitHub Docs, *Contexts*; *Expressions* | Review every expression and test success/failure/cancel/skip paths |
| Permissions | Top-level/job-level permission semantics and token availability | GitHub Docs, *Controlling permissions for GITHUB_TOKEN* | Inspect workflow YAML and test only in a private repository |
| Action pinning | Intended action release and full commit SHA | Official action repository/release page; GitHub Docs, *Secure use reference* | Verify source/release, replace placeholder, run `actionlint`, then hosted test |
| Reusable workflows | `workflow_call` inputs/outputs, caller syntax, permission inheritance | GitHub Docs, *Reusing workflows* | Create the reusable workflow and both callers; verify inputs and job results |
| Composite actions | Metadata schema, `runs.using: composite`, shell requirements | GitHub Docs, *Creating a composite action* | Run action in a private workflow and test each supported input |
| Script injection/PR trust | Safe use of event metadata; `pull_request` vs `pull_request_target` | GitHub Docs, *Secure use reference*; event documentation | Inspect every expression inside `run`; use only benign private-repo test data |
| Secrets | Secret scopes, event restrictions, masking limitations | GitHub Docs, *Using secrets in GitHub Actions* | Use fake markers; inspect logs/artifacts without printing real values |
| Artifacts/cache | Current upload/download action interfaces, retention, cache behavior | GitHub Docs, *Workflow artifacts*; *Dependency caching* | Transfer a harmless report; compare cache keys and installed dependency state |
| Service containers | Networking, image behavior, health checks | GitHub Docs, *Communicating with Docker service containers* | Run bounded integration test; verify readiness before test execution |
| Environments | Protection rules, reviewers, environment-scoped secrets, plan availability | GitHub Docs, *Managing environments for deployment* | Verify current UI/configuration; test only in a private repo and non-production environment |
| OIDC | Claims, cloud trust policy, role permissions | GitHub Docs, *About security hardening with OpenID Connect* | Follow M09 provider-specific review; do not use broad role policies |
| Attestations | Current feature names, permissions, availability | GitHub Docs, *Artifact attestations*; SLSA | Confirm current docs and plan support; do not infer conformance from a successful run |
| `actionlint` | Current install/version and diagnostic behavior | Official `rhysd/actionlint` repository | Install a verified release and run against workflow directory |
| `act` | Current local-run support and known gaps | Official `nektos/act` repository/docs | Compare local result with hosted private-repository run |
| Plans/quotas | Current free-tier limits and organization feature availability | Current GitHub plan/usage docs | Check account/organization UI before enabling heavy workflows |
| WSL2/native Linux | Filesystem performance, Docker integration, local emulation | Local environment and Docker/WSL docs | Run the same local test in intended filesystem and record differences |

## Appendix D — Known Limitations and Assumptions

- This is an AI-authored lesson and AI self-audit; it is not an independent human review.
- Official documentation was not live-consulted during authoring. URLs and current platform semantics must be verified.
- The sample Python baseline and dependency constraints are teaching assumptions, not a claim that those are the latest supported versions.
- Action SHA placeholders are intentionally not executable until replaced with verified full commit SHAs.
- The reusable workflow callers assume `services/api/tests` and `packages/etl/tests` exist and that their projects support the shown installation command.
- The service-container example is optional and must be checked against current runner, networking, health-check, and container-image behavior.
- `act` is optional and may not reproduce hosted services, token permissions, OIDC, environments, all contexts, or all runner behavior.
- No free-tier quotas or current plan capabilities are asserted.
- No workflow, command, linter, or lab was executed during authoring. All output blocks are representative.
- Advanced cache design is deferred to Unit 4; monorepo/path filtering to Unit 5; quality gates/flaky-test management to Unit 6; approvals/environments to Unit 9; self-hosted runner security/scaling to Unit 10; OIDC/secrets architecture to M09; supply-chain signing/provenance/attestation to M12; GitOps reconciliation to M08.
- A successful workflow, SHA pin, linter, test, scan, or branch rule does not prove the entire delivery system is secure.

## Appendix E — Sign-off

- **Content status:** DRAFT-AUDITED
- **Audit date:** 2026-10-24 (authoring date)
- **Auditor:** AI self-audit (requires human verification)
- **Unverified item groups:** 8 primary groups in Section 2.14, plus tool/runner/plan and execution checks in Appendix C.
- **Execution status:** Not executed during authoring.
- **Sign-off condition:** A human reviewer must verify official documentation, replace action SHA placeholders, run `actionlint` or an equivalent validator, execute the labs in a private test repository, inspect permission and event-trust boundaries, and record any remaining open items.

AI self-audit does not replace a human running the workflows and labs.
