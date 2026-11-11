# Build Caching, Parallelism, and Pipeline Speed

**Abstract:** Learn to measure CI pipeline performance before optimizing it. This lesson explains critical paths, dependency caches, Docker/BuildKit cache, test parallelism, cache trust boundaries, benchmark design, performance SLOs, and safe regression guards using a Python scoring service, shared library, ETL package, and lightweight ML evaluation as the running context. Caches are disposable acceleration state, not authoritative release artifacts or integrity controls.

> **Module:** M02 — CI/CD Pipeline Engineering  
> **Stage:** 2E — Production DevOps & Platform Engineering  
> **Unit:** 4  
> **Target file:** `04-build-caching-parallelism-and-pipeline-speed.md`  
> **Estimated time:** 8–12 hours  
> **Last reviewed:** Authoring date 2026-10-24; independent live-documentation review not performed  
> **Assumed baseline:** GitHub Actions; Python 3.11+; pytest; optional `pytest-xdist`; Docker/BuildKit for optional image work; `gh` CLI for run data  
> **Verification status:** DRAFT-AUDITED — HUMAN VERIFICATION REQUIRED. Workflows, scripts, GitHub CLI/API extraction, BuildKit commands, and labs were not executed. Current official docs were not live-checked.

## Contents

- [4.0 Why this matters in production](#40-why-this-matters-in-production)
- [4.1 Learning objectives](#41-learning-objectives)
- [4.2 Concept map and vocabulary](#42-concept-map-and-vocabulary)
- [4.3 Level 1 — Beginner](#43-level-1--beginner)
- [4.4 Level 2 — Intermediate](#44-level-2--intermediate)
- [4.5 Level 3 — Advanced](#45-level-3--advanced)
- [4.6 Level 4 — Expert](#46-level-4--expert)
- [4.7 SRE lens](#47-sre-lens)
- [4.8 Security lens](#48-security-lens)
- [4.9 Production checklist](#49-production-checklist)
- [4.10 Hands-on lab set](#410-hands-on-lab-set)
  - [Lab A — Baseline and critical path](#lab-a--baseline-and-critical-path)
  - [Lab B — Lockfile-keyed dependency cache](#lab-b--lockfile-keyed-dependency-cache)
  - [Lab C — Parallel test strategy](#lab-c--parallel-test-strategy)
  - [Lab D — Stale-cache simulation](#lab-d--stale-cache-simulation)
  - [Lab E — Workflow duration extraction](#lab-e--workflow-duration-extraction)
- [4.11 Self-check questions](#411-self-check-questions)
- [4.12 Evidence artifacts](#412-evidence-artifacts)
- [4.13 Interview and design-review questions](#413-common-interview-and-design-review-questions)
- [Claim Register](#claim-register)
- [Ten-pass self-audit](#ten-pass-self-audit)
- [Human verification checklist](#human-verification-checklist)
- [Known limitations and sign-off](#known-limitations-and-sign-off)
- [4.14 Sources and verification notes](#414-sources-and-verification-notes)

## Unit 4 — Build caching, parallelism, and pipeline speed

**Target file:** 04-build-caching-parallelism-and-pipeline-speed.md | **Estimated time:** 8–12 hours | **Prerequisites:** Git, shell, Python/pytest basics, Unit 2 GitHub Actions concepts, M01 Docker/BuildKit basics

**Core tools:** GitHub Actions, Python, pytest, pip/uv/Poetry (choose and distinguish), Docker/BuildKit, gh CLI, Git | **Awareness:** remote cache backends and test-impact-analysis systems not required for the core labs | **Last reviewed:** Authoring date 2026-10-24; independent review not performed

### 4.0 Why this matters in production

Repeated dependency downloads can consume more time than the tests themselves. A serial dependency chain can make one job dominate the critical path even when other work finishes early. Adding parallel jobs can increase wall time if each repeats setup, starts cold, or competes for limited memory and CPU. Caches may preserve stale or incompatible state, while shared-runner queue and network variation can make a single run misleading. Optimize from measured evidence while preserving every required correctness and security gate.

### 4.1 Learning objectives

| Objective | Level | Teaching content | Lab/evidence |
|---|---|---|---|
| Explain pipeline duration, queue time, job duration, and critical path | [L1] | 4.2–4.3 | Lab A timing table and DAG |
| Distinguish cache, artifact, Docker layer cache, and remote BuildKit cache | [L1] | 4.2–4.4 | Cache rationale |
| Implement lockfile-keyed dependency caching | [L2] | 4.4 | Lab B YAML and run IDs |
| Compare serial and parallel tests without reducing coverage | [L2] | 4.4–4.5 | Lab C benchmark |
| Design cache scope/fallbacks and diagnose stale or poisoned cache | [L3] | 4.5, 4.8 | Lab D incident notes |
| Measure cold/warm/partial-change performance using repeated runs | [L3] | 4.5–4.7 | Lab A/E CSV |
| Define a performance SLO, regression guard, and parameterized cost model | [L4] | 4.6–4.7 | Decision record |
| Extract run durations and explain measurement limits | [L4] | 4.6, 4.10 | Lab E script output |

### 4.2 Concept map and vocabulary

```text
Push / pull request
       |
       v
Queue / runner setup
       |
       v
       +----------+------------+
       |                       |
     lint                 unit tests
       |                       |
       +-----------+-----------+
                   |
             schema/data checks
                   |
            +------+------+
            |             |
      service package   ETL checks
            |             |
            +------+------+
                   |
             release evidence

Critical path = longest dependency-constrained path.
Caches can reduce work inside jobs; they do not remove required dependency edges.
Artifacts carry named outputs; caches carry disposable acceleration state.
```

| Term | Precise definition | Common misconception |
|---|---|---|
| Pipeline duration | Elapsed time from defined pipeline start to terminal state | Sum of all job durations |
| Queue time | Time a job waits before execution, if a trustworthy source exposes it | Script runtime |
| Job duration | Elapsed duration of an individual job per the platform's timing definition | Pure CPU time |
| Critical path | Longest dependency path constraining completion | Highest-CPU job |
| Cache hit/miss | Whether reusable state was found/restored for a requested key/scope | Proof the result is correct |
| Cold run | Run designed to begin without the relevant cache | Any slow run |
| Warm run | Run where relevant cache is expected to be available | Guaranteed faster run |
| Partial-change run | Run where only a controlled subset of inputs changes | A perfectly comparable run without controls |
| Cache key | Identifier derived from selected inputs to locate reusable state | Security boundary |
| Restore key/fallback | Secondary key searched if the exact key is absent | Proof fallback data matches current inputs |
| Cache scope | Workflows/branches/identities able to read or write cache state | Always identical to repository visibility |
| Cache poisoning | Malicious or accidental contamination causing unsafe/incorrect reuse | Only an intentional attack |
| Artifact | Named output/evidence intentionally uploaded and retained | Disposable dependency cache |
| Docker layer cache | Reusable image build steps/layers | pip cache |
| Remote BuildKit cache | Imported/exported build cache through a configured backend | Published image or release artifact |
| Test sharding | Splitting a suite into groups executed separately | Automatically balanced parallelism |
| Parallelism tax | Setup, coordination, contention, and fan-out/fan-in overhead | Reason never to parallelize |
| Runner right-sizing | Selecting CPU/RAM/disk/concurrency from measured workload | Always choosing the largest runner |
| Performance SLO | Objective for a defined pipeline performance indicator | Universal duration threshold |
| Regression guard | Check/alert for meaningful change against a baseline | Fail on every isolated slow run |

**Cache versus artifact:** cache is reusable acceleration state that may be absent, stale, or evicted and should be safe to recompute. An artifact is an output/evidence object with an intentional identity and retention path. A release archive, model evaluation report, package, or build output that must be retained should use an artifact/package channel, not only a cache. A cache hit is not proof of integrity.

**Worked critical-path example — [ILLUSTRATIVE]:** checkout/setup takes 1 minute; lint 2; unit tests 5; schema check 3; package 4; evidence collection 1. Lint and unit tests run in parallel, then schema waits for both, followed by package and evidence. Path A is 1+2+3+4+1 = 11 minutes. Path B is 1+5+3+4+1 = 14 minutes. The unit-test path is critical. Reducing lint from 2 to 1 minute does not reduce the 14-minute path; reducing unit tests may. These are arithmetic examples, not benchmark results.

### 4.3 Level 1 — Beginner

#### Why pipelines are slow

Separate the hypotheses before changing configuration:

1. **Queue/provisioning:** busy shared capacity, no eligible runner, startup, image preparation.
2. **Checkout/setup:** repository size, submodules, tool installation, repeated environment creation.
3. **Dependency resolution/download:** package-index latency, large wheels, changed lockfiles.
4. **Build/test:** expensive fixtures, image builds, schema checks, or model evaluation.
5. **Network/artifacts:** image pulls, package downloads, large outputs, uploads.
6. **Serialization:** stage barriers or unnecessary dependency edges.
7. **Contention:** too many workers competing for CPU, RAM, disk, services, or network.

A slow job is a symptom. Use logs and timestamps to distinguish the cause. Job elapsed time may include downloads and waits, not just Python execution.

#### Minimal local project

```text
pipeline-speed-lab/
├── pyproject.toml
├── src/scorelib.py
├── tests/test_scorelib.py
└── scripts/time_tests.py
```

```toml
# File: pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "pipeline-speed-lab"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8,<9"]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# File: src/scorelib.py
from __future__ import annotations


def bounded_score(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value
```

```python
# File: tests/test_scorelib.py
from scorelib import bounded_score


def test_middle_value() -> None:
    assert bounded_score(0.6) == 0.6


def test_low_value() -> None:
    assert bounded_score(-0.1) == 0.0


def test_high_value() -> None:
    assert bounded_score(1.2) == 1.0
```

```python
# File: scripts/time_tests.py
from __future__ import annotations

import subprocess
import sys
import time


def main() -> int:
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        check=False,
        text=True,
    )
    print(f"pytest_exit_code={result.returncode}")
    print(f"elapsed_seconds={time.perf_counter() - start:.3f}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
```

```bash
# File: commands/local-baseline.sh
set -euo pipefail
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/time_tests.py
```

**Example — yours will differ**
```text
3 passed
pytest_exit_code=0
elapsed_seconds=0.482
```

Interpretation: values are illustrative, not measured. The timer includes pytest process startup and test execution, but excludes environment creation and dependency installation. Time those phases separately if they matter.

**What just happened?** A monotonic timer measured a local test process. It does not measure hosted queue time, checkout, provisioning, artifact transfer, or end-to-end workflow duration. Local and hosted timings answer different questions.

#### Beginner mistake table

| Symptom | Likely cause | Fix |
|---|---|---|
| Second run faster | Warm package cache or changed external load | Record cache state and repeat controlled runs |
| Cache hit but tests fail | Stale/incompatible state or unrelated test defect | Compare with a clean run and dependency metadata |
| Parallel tests slower | Worker/setup overhead exceeds useful work | Compare end-to-end time and resource use |
| Pipeline exceeds sum of selected jobs | Queue, setup, waits, or omitted jobs | Collect all job timings and pipeline timestamps |
| Cache never hits | Key changes each run or scope/path differs | Inspect key inputs and restore logs |
| Artifact missing | Not uploaded or path/retrieval is wrong | Declare path and inspect upload/download evidence |
| ML tests vary | Nondeterminism, seed/data drift, or contention | Fix seeds where appropriate and report variance |

### 4.4 Level 2 — Intermediate

#### Dependency caching: choose one package manager

A cache should be keyed by the dependency source of truth plus compatibility dimensions. **[VERIFY]** Current GitHub cache limits, eviction behavior, branch/PR scope, action inputs, and plan rules in official docs; none are asserted here.

| Tool | Typical dependency source of truth | Cache strategy | Caveat |
|---|---|---|---|
| pip | `requirements.txt` or generated pinned requirements file | Cache pip download/wheel directory using documented support | A loose requirements file may not lock transitive dependencies |
| uv | `uv.lock` | Cache uv's documented cache location or use documented setup support | Do not hash `uv.lock` while installing from a different source |
| Poetry | `poetry.lock` | Cache Poetry's documented cache location | Virtual environment behavior/cache paths must match runner setup |

Pick one tool for each lab; do not install pip, uv, and Poetry just to compare mechanisms. **[VERIFY]** Consult current official pip, uv, and Poetry docs for cache directories and lockfile semantics.

```yaml
# File: .github/workflows/ci-explicit-cache.yml
name: Python CI with dependency cache

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@<full-40-char-sha> # VERIFY before use

      - name: Set up Python
        uses: actions/setup-python@<full-40-char-sha> # VERIFY before use
        with:
          python-version: "3.12"

      - name: Cache pip downloads
        uses: actions/cache@<full-40-char-sha> # VERIFY before use
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-python-3.12-pip-${{ hashFiles('requirements-ci.txt') }}
          restore-keys: |
            ${{ runner.os }}-python-3.12-pip-

      - name: Install dependencies
        run: python -m pip install -r requirements-ci.txt

      - name: Run tests
        run: python -m pytest -q
```

The full 40-character action SHAs are deliberately placeholders, not valid pins. Replace them with reviewed SHAs from official action sources before use. Do not invent SHAs. Verify current action inputs and the expression syntax in the official `actions/cache` documentation. `requirements-ci.txt` must be the authoritative file actually used by the install command.

The conceptual exact key is `OS + Python runtime + package manager + hash(authoritative dependency file)`. The fallback may reuse downloaded packages after a lockfile change, but dependency installation and integrity checks must still run. Avoid broad fallbacks for complete virtual environments or compiled binaries unless all compatibility dimensions are represented.

#### Docker layer cache, package cache, and artifact

These are separate mechanisms:

- pip cache: package downloads/wheels.
- GitHub Actions cache: files restored under a key.
- Docker/BuildKit layer cache: reusable image build steps.
- Artifact: named output/evidence retained for later inspection or transfer.
- Remote BuildKit cache: imported/exported cache through a configured backend.

```dockerfile
# File: Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements-ci.txt .
RUN python -m pip install --no-cache-dir -r requirements-ci.txt
COPY src/ src/
CMD ["python", "-c", "from scorelib import bounded_score; print(bounded_score(0.5))"]
```

Keep stable dependency inputs before frequently changing source files to make layer reuse possible. M01 Unit 4 covers layer ordering and BuildKit caching in depth. A pip cache does not automatically become a BuildKit cache.

```bash
# File: commands/buildkit-cache-shape.sh
# Illustrative only; verify current syntax, driver, registry, and access controls.
docker buildx build \
  --cache-from type=registry,ref=REGISTRY/PRIVATE-IMAGE:buildcache \
  --cache-to type=registry,ref=REGISTRY/PRIVATE-IMAGE:buildcache,mode=max \
  --tag local-score-service:test \
  .
```

**[VERIFY]** Confirm current Docker Buildx/BuildKit syntax, driver requirements, supported cache backend, export mode, and registry permissions before use. The destination is a placeholder; the core labs do not require registry access. Do not point it at a public or production registry.

#### Parallel tests, sharding, and fail-fast

`pytest-xdist` can run independent tests in worker processes, but shared mutable fixtures, global state, common temporary filenames, database contention, or order dependence can make parallel execution unsafe. Small suites may be slower because worker startup and setup dominate. Heavy dependencies such as `numpy`, `pandas`, `pyarrow`, and `scikit-learn` can multiply memory demand across workers.

```bash
# File: commands/test-serial-and-parallel.sh
set -euo pipefail
python -m pytest -q
python -m pytest -q -n 2
```

Install `pytest-xdist` in the chosen development dependency set before using `-n 2`. **[VERIFY]** Check current xdist support and command options.

**Example — yours will differ**
```text
# Serial
120 passed in 18.4s

# Two workers
120 passed in 11.2s
```

These values are `[ILLUSTRATIVE]`. Compare identical test coverage, wall time, setup, CPU/RAM pressure, and failure rate. Timing-based sharding assigns tests using historical per-test durations; it needs stable test identities and recent timing data. Equal test counts do not guarantee equal runtime. Unit 6 covers test strategy and flaky tests in more depth.

Fail-fast can save resources after a required prerequisite fails, but canceling work may hide diagnostics. GitHub Actions `concurrency` can coordinate runs/jobs in a group. **[VERIFY]** Check current group and cancellation semantics before use, especially for release or deployment jobs.

```yaml
# File: .github/workflows/ci-concurrency.yml
name: CI

on:
  push:
  pull_request:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: State policy
        run: echo "Validation only; no release or deployment occurs."
```

This is a validation-only example. Test the group behavior on a private branch. A ref-based group and a pull-request-identity group can behave differently. Do not apply cancel-in-progress indiscriminately to non-idempotent release, migration, or deployment work.

#### Pattern catalogue

| Pattern | When to use | When NOT to use |
|---|---|---|
| Lockfile-keyed dependency cache | Dependency downloads are significant | No reliable dependency source of truth |
| Exact key + narrow fallback | Cached data remains safe to recompute/validate | Complete environment/binaries may be incompatible |
| Docker layer cache | Repeated image builds share stable steps | Mistaking it for package cache or artifact storage |
| Parallel tests | Tests are independent and resources available | Shared mutable state or RAM contention dominates |
| Timing-based sharding | Suite is large and timing data maintained | Suite is tiny or timing data stale |
| Concurrency cancellation | Superseded validation work is safe to stop | Release/deploy may be left partially complete |
| Artifact for build/test output | Output must be identified and retained | Speeding up dependency downloads |
| Docs-only skip | Change classification is reliable and gates remain valid | Required tests/security gates can silently disappear |

#### Anti-pattern catalogue

| Bad example | Why it hurts | Corrected version |
|---|---|---|
| Cache virtualenv by branch only | Runtime/lockfile mismatch | Include runtime/platform and lockfile identity |
| Broad fallback for compiled extensions | Incompatible binary state may be reused | Avoid fallback or include ABI/toolchain/build dimensions |
| Cache `.env` or credentials | Exposes secrets across unintended jobs | Exclude sensitive paths; use approved secret mechanism |
| Add workers without measurement | Startup and contention may dominate | Benchmark serial and small worker counts |
| Store release archive only in cache | Cache may be absent or evicted | Use an artifact/package channel |
| Cancel every workflow | Release operation may stop midway | Separate validation and release cancellation policies |
| Skip all tests for docs changes | Required checks may be bypassed | Test path policy and preserve meaningful required statuses |

### 4.5 Level 3 — Advanced

#### Cache-key design, scope, and fallbacks

A key should identify compatibility-relevant inputs: operating system, architecture where relevant, language/runtime, package-manager version, lockfile hash, compiler/ABI, and build flags for compiled outputs. Too broad a key risks stale/incompatible state; too specific a key causes misses and cache fragmentation.

```text
Downloaded package cache:
  OS + Python runtime + package manager + lockfile hash

Compiled extension / virtual environment:
  OS + architecture + Python ABI + compiler/toolchain
  + lockfile hash + build flags
```

These are design descriptions, not literal GitHub expressions. **[VERIFY]** Use current official syntax for file hashes and restore keys. Fallback order matters: an exact match should be preferred; a broader fallback should only be used when the cached contents remain safe to validate/recompute.

```text
Trusted default-branch workflow -> reviewed cache namespace
       |                              |
       | controlled, documented read/write access
       v                              v
Trusted consumer workflow       Trusted build

Untrusted PR workflow -> isolated state / no write path to trusted release cache
```

Cache key is not a permission system. Verify actual branch/PR/fork cache access rules and token permissions. Never let an untrusted PR write cache state that a release workflow assumes is trusted. Do not store secrets, private keys, credential files, or sensitive datasets in cache paths.

#### Size, eviction, and cache poisoning

Caches can be unavailable due to eviction, key changes, storage pressure, or policy. **[VERIFY]** Current GitHub cache limits, quotas, retention, and free-tier rules in official docs and target organization settings. No numerical limit is asserted here. A correct pipeline must succeed from a cold cache.

Cache poisoning can be malicious or accidental. A benign failure occurs when a key omits the runtime or lockfile and reuses incompatible compiled output. Defenses: narrow keys, trust separation, package-manager integrity checks, clean rebuilds, and tests that prove installation uses authoritative inputs. A cache hit is not an integrity check. Use checksums/digests, lockfile integrity, and provenance mechanisms appropriate to the artifact; M12 covers deeper supply-chain evidence.

#### Benchmark protocol: cold, warm, partial-change

1. Define metrics: end-to-end duration, critical path, queue time where available, job duration, setup/download time, and cache outcome.
2. Fix the workload, runtime, runner class, dependency inputs, and event type where possible.
3. Collect N repeated runs; N = 5 or more is a feasible initial protocol choice, not a universal performance standard.
4. Run cold, warm, and partial-change cases. Document how cache state was controlled; never delete shared/production cache.
5. Record commit SHA, workflow/run ID, branch/event, runner type, queue time if exposed, job duration, cache state, lockfile changes, and environment changes.
6. Compute median and p95 using a named method. A small N gives a weak tail estimate; do not claim statistical robustness.
7. Note shared-runner noise, network variance, cache eviction, concurrent load, and warm-up effects.
8. Verify identical correctness gates. Faster results from skipped tests are not valid optimization.

| Run | State | SHA | Run ID | Event | Runner | Queue sec | Critical path sec | Pipeline sec | Cache note |
|---|---|---|---|---|---|---:|---:|---:|---|
| 1 | cold | fill | fill | push | fill | measure/unavailable | fill | fill | miss |
| 2 | warm | fill | fill | push | fill | measure/unavailable | fill | fill | hit/unknown |
| 3 | partial change | fill | fill | push | fill | measure/unavailable | fill | fill | record |
| 4 | warm repeat | fill | fill | push | fill | measure/unavailable | fill | fill | record |
| 5 | warm repeat | fill | fill | push | fill | measure/unavailable | fill | fill | record |

If the selected endpoint does not expose queue time, write “unavailable from selected endpoint”; do not infer it from unrelated timestamps.

#### Parallelism tax and runner right-sizing

Each parallel job may repeat checkout, environment setup, dependency installation, image pulls, service startup, and artifact transfer. Per-runner caches may be cold or fragmented. Fan-out/fan-in adds scheduling overhead; more workers may saturate CPU, RAM, disk, network, or shared services. Right-size from observations:

- CPU utilization/throttling for CPU-bound tests.
- Peak memory for heavy data/ML dependencies.
- Disk use for package caches, Docker layers, fixtures, and artifacts.
- Network time for images and packages.
- Queue time separately from runtime.
- End-to-end duration and critical path, not only the fastest job.

Do not prescribe universal runner sizes. WSL2 Docker integration and filesystem placement can change local results; compare identical setups. GitHub-hosted runner characteristics and plan availability are **[VERIFY]**.

#### Conditional execution and path-based skips

Skipping docs-only changes can save work only if change classification is reliable. Docs may contain generated API contracts, workflow examples, or release inputs. Required checks must still report meaningful statuses; security gates cannot silently disappear. Unit 5 owns monorepo/path filtering depth. Here, require a documented dependency map, safe default for unknown changes, and tests for the path policy.

#### Trade-off table

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Exact lockfile cache | Compatibility clarity | Miss after dependency change | Cache still untrusted/evictable | Downloads are material |
| Broad restore key | Reuse after lockfile change | Less predictable compatibility | Stale state/trust error | Data is safe to recompute and validate |
| Remote BuildKit cache | Persists build cache on ephemeral runners | Registry traffic and access maintenance | Unauthorized writer/stale build assumptions | Image build dominates |
| Parallel workers | May reduce wall time | CPU/RAM/setup cost | Flaky shared-state tests | Tests independent and long enough |
| Test-impact analysis | Skips irrelevant tests | Dependency map maintenance | False negatives | Mature dependency graph and safe fallback |
| Cancellation | Stops superseded validation | Discards some work | Partial release state if misapplied | Idempotent validation |
| Bigger runner | May relieve saturation | Cost/availability impact | Doesn't fix queue/network bottleneck | Metrics show resource saturation |

**Decision lab:** use your measurements to defend whether to add a cache, parallelize, or do neither. State the bottleneck, baseline sample count, correctness proof, cold-cache behavior, trust boundaries, rollback, and evidence that would reverse your decision. “No optimization yet” is a valid outcome.

### 4.6 Level 4 — Expert

#### Performance SLO and regression guard

Define an SLO for a specific population: for example, p50/p95 from push to required checks complete, p95 queue time, critical-path duration, or fraction of intended pipelines completing within a delivery target. Separate branch, PR, and nightly workflows. Define how canceled/superseded runs are counted; do not exclude inconvenient results after seeing the chart.

A regression guard requires a representative baseline, raw samples, sample count, percentile method, noise tolerance, an owner, and a safe response. **[ILLUSTRATIVE]** A team may warn when a rolling median exceeds its measured baseline beyond a chosen tolerance for several comparable runs. The threshold must come from observed variability and delivery needs, not a universal percentage. Never improve the speed metric by removing required tests.

#### Transparent cost model

Use measured runner minutes and an operator-supplied verified rate/multiplier. No prices or plan multipliers are invented.

```python
# File: scripts/estimate_runner_cost.py
from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner-minutes", type=float, required=True)
    parser.add_argument("--rate-per-minute", type=float, default=None)
    parser.add_argument("--multiplier", type=float, default=1.0)
    args = parser.parse_args()
    if args.runner_minutes < 0 or args.multiplier < 0:
        parser.error("minutes and multiplier must be non-negative")
    if args.rate_per_minute is None:
        print(f"effective_runner_units={args.runner_minutes * args.multiplier:.2f}")
        print("cost=not calculated; supply a verified rate")
        return 0
    if args.rate_per_minute < 0:
        parser.error("rate must be non-negative")
    print(
        f"estimated_cost="
        f"{args.runner_minutes * args.multiplier * args.rate_per_minute:.2f}"
    )
    print("estimate excludes unmodeled charges and depends on verified inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Command: `python scripts/estimate_runner_cost.py --runner-minutes 120 --multiplier 1.0`

**Example — yours will differ**
```text
effective_runner_units=120.00
cost=not calculated; supply a verified rate
```

This is a parameterized unit count, not an invoice. Verify current billing model, runner multipliers, included allowance, and billing scope before supplying a rate.

#### Ephemeral-runner cache strategies

| Strategy | Advantages | Costs/risks |
|---|---|---|
| No cache | Simple trust model, reproducible cold runs | Repeated downloads/build work |
| Dependency-manager cache | Reuses downloads | Eviction and trust scope still matter |
| Approved dependency proxy/mirror | Centralized policy and potentially fewer external downloads | Requires ownership/availability; may be outside zero-budget scope |
| External cache backend | Persists state across ephemeral runners | Credentials, network, lifecycle, access control |
| Remote BuildKit cache | Reuses image build steps | Registry access, writer trust, lifecycle |
| Long-lived self-hosted cache | Warm local state | Persistent compromise/staleness and scaling concerns; Unit 10 |

Ephemeral runners lose local state after the job, so persistence requires an external backend. That backend becomes part of the performance and security design. Cold-cache correctness remains mandatory.

#### Test-impact analysis

Test-impact analysis selects tests based on changed files and dependency relationships. It may save work but risks false negatives if indirect/generated dependencies are missing. Do not make it the default for a small repository. Require a maintained dependency map, safe fallback for unknown changes, periodic full-suite runs, and evidence that affected components are covered. Proprietary tooling is not required.

#### Incident: “cache restored stale dependencies and masked a break”

**Symptom → hypothesis → test → root cause → fix → prevention**

- **Symptom:** CI differs between a warm runner and a clean environment after a dependency change.
- **Hypothesis:** a cache contains a stale virtual environment or compiled dependency incompatible with the current lockfile/runtime.
- **Test:** record lockfile hash, runtime, package-manager version, cache key, and install logs; run in a fresh isolated environment without the affected cache. Compare package metadata and test outcomes without printing secrets.
- **Root cause:** key omitted a compatibility dimension or the workflow skipped installation after restore.
- **Fix:** install from authoritative dependency inputs; add relevant runtime/toolchain/lockfile dimensions; remove unsafe fallback or cached environment; rebuild cleanly.
- **Prevention:** test cold-cache correctness, review cache scope, and add a regression test proving installation and validation run.

Safe cache-busting should be scoped to the test workflow by changing a test key or temporarily disabling that cache. Do not delete organization-wide or production cache. Remote cache deletion/eviction is platform-dependent.

#### Workflow run duration extraction with `gh`

**[VERIFY]** Current `gh run list`/`gh run view` JSON fields, flags, pagination, and authentication behavior in official GitHub CLI docs. The script below intentionally leaves queue time blank; it does not infer queue time from creation-to-start timestamps. It extracts only run-level duration from `startedAt` to `completedAt` if those fields exist. This is not job-level timing or a complete paginated history.

```python
# File: scripts/collect_workflow_durations.py
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def seconds_between(start: Any, end: Any) -> float | None:
    a, b = parse_time(start), parse_time(end)
    if a is None or b is None:
        return None
    return max(0.0, (b - a).total_seconds())


def run_gh(args: list[str]) -> Any:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"gh exit {result.returncode}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("gh returned invalid JSON; verify CLI version and fields") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("workflow-durations.csv"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be in 1..100")

    try:
        runs = run_gh([
            "run", "list", "--limit", str(args.limit), "--json",
            "databaseId,workflowName,headBranch,event,status,conclusion,createdAt,startedAt,completedAt,headSha",
        ])
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not isinstance(runs, list):
        print("error: expected JSON array", file=sys.stderr)
        return 2

    fields = [
        "run_id", "workflow", "branch", "event", "status", "conclusion",
        "created_at", "started_at", "completed_at", "queue_seconds",
        "run_seconds", "head_sha",
    ]
    rows = []
    for run in runs:
        if not isinstance(run, dict):
            continue
        rows.append({
            "run_id": run.get("databaseId", ""),
            "workflow": run.get("workflowName", ""),
            "branch": run.get("headBranch", ""),
            "event": run.get("event", ""),
            "status": run.get("status", ""),
            "conclusion": run.get("conclusion", ""),
            "created_at": run.get("createdAt", ""),
            "started_at": run.get("startedAt", ""),
            "completed_at": run.get("completedAt", ""),
            "queue_seconds": "",
            "run_seconds": seconds_between(run.get("startedAt"), run.get("completedAt")),
            "head_sha": run.get("headSha", ""),
        })

    if args.dry_run:
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        return 0
    try:
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        print(f"error: could not write CSV: {exc}", file=sys.stderr)
        return 2
    print(f"wrote_rows={len(rows)}")
    print(f"output={args.output}")
    print("queue_seconds=unavailable from selected fields; not inferred")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# File: tests/test_collect_workflow_durations.py
from collect_workflow_durations import seconds_between


def test_valid_times() -> None:
    assert seconds_between("2026-01-01T00:00:00Z", "2026-01-01T00:00:10Z") == 10.0


def test_missing_time() -> None:
    assert seconds_between(None, "2026-01-01T00:00:10Z") is None


def test_invalid_time() -> None:
    assert seconds_between("bad", "2026-01-01T00:00:10Z") is None
```

Command: `python -m pytest -q tests/test_collect_workflow_durations.py`

**Example — yours will differ**
```text
3 passed
```

Interpretation: synthetic parser tests do not validate the live `gh` schema. Check current CLI documentation before using the script on repository data.

Command: `gh auth status && python scripts/collect_workflow_durations.py --limit 20 --dry-run`

**Example — yours will differ**
```text
run_id,workflow,branch,event,status,conclusion,created_at,started_at,completed_at,queue_seconds,run_seconds,head_sha
123456,CI,main,push,completed,success,2026-10-20T10:00:00Z,2026-10-20T10:00:20Z,2026-10-20T10:03:10Z,,170.0,abc123...
```

The row is synthetic, not measured. Authentication output varies; do not share sensitive account details. Missing timestamps remain blank/`None`. Queue time is explicitly unavailable from these selected fields.

#### Median and p95 summary

```python
# File: scripts/summarize_durations.py
from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


def nearest_rank_percentile(values: list[float], percentile: float) -> float:
    if not values or not 0 < percentile <= 100:
        raise ValueError("non-empty values and percentile in (0, 100] required")
    ordered = sorted(values)
    rank = max(1, int((percentile / 100) * len(ordered) + 0.999999))
    return ordered[min(rank - 1, len(ordered) - 1)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--column", default="run_seconds")
    args = parser.parse_args()
    values: list[float] = []
    with args.csv_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                value = float(row.get(args.column, ""))
            except (TypeError, ValueError):
                continue
            if value >= 0:
                values.append(value)
    if not values:
        print("no valid duration samples")
        return 1
    print(f"sample_count={len(values)}")
    print(f"median_seconds={statistics.median(values):.2f}")
    print(f"p95_nearest_rank_seconds={nearest_rank_percentile(values, 95):.2f}")
    print("small samples produce weak p95 estimates; inspect raw runs and variability")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Command: `python scripts/summarize_durations.py evidence/workflow-durations.csv`

**Example — yours will differ**
```text
sample_count=5
median_seconds=170.00
p95_nearest_rank_seconds=210.00
small samples produce weak p95 estimates; inspect raw runs and variability
```

These values are illustrative. The script uses nearest-rank p95; other tools may use a different method. Preserve raw samples and disclose the method.

### 4.7 SRE lens

A pipeline is a delivery service. Its users need predictable feedback, accurate required checks, and safe recovery—not simply a smaller duration number.

| SLI | Measurement | SLO design notes |
|---|---|---|
| p50/p95 end-to-end duration | Run timestamps for a defined event population | Segment push, PR, and nightly workflows |
| Queue time | Documented queue/start timestamps, if available | If unavailable, state it; do not infer it |
| Critical-path duration | Dependency graph and job timings | Verify every required edge is represented |
| Success rate | Successful completed runs / relevant completed runs | Define treatment of canceled/superseded runs |
| Cache hit/miss | Cache logs or supported telemetry | Hit rate is not integrity or correctness |
| Runner utilization | Approved runner/host telemetry | Shared runner metrics may not be available |
| Regression rate | Comparable runs beyond measured threshold | Define sample count, baseline, noise tolerance |

Derive targets from observed workload and delivery needs; no universal threshold is asserted. A single SLO for all event types may hide regressions. A faster run that skips required checks is not a success.

**Runbook — Alert → Triage → Mitigation → Follow-up**

```text
p95 pipeline duration rises
→ compare commit, event, runner, queue, job durations, and cache state
→ locate queue/setup/network/test/critical-path change
→ revert the optimization if correctness or stability regressed
→ add the workload to the benchmark and update the guard

Cache-related failures rise
→ compare key, lockfile hash, runtime, cache logs, clean-run outcome
→ disable/change only the affected test workflow cache
→ rebuild from authoritative inputs and verify tests
→ add stale/cold-cache regression coverage

Runner capacity saturates
→ separate queue from runtime and inspect resource pressure
→ reduce unnecessary fan-out or use an approved compatible capacity pool
→ review sizing with measurements and an owner
```

Record runner minutes, concurrency, queue delay, artifact transfer, image pulls, and dependency download. Shared-runner/network variance can dominate small benchmarks. Free-tier allowances, cache limits, billing multipliers, and prices are **[VERIFY]**; none are stated as fact.

### 4.8 Security lens

| Threat | Control | How to verify | Limitation |
|---|---|---|---|
| Untrusted PR writes cache consumed by release | Separate trust domains and cache write paths | Review triggers, token permissions, cache keys/scope, fork policy | Platform access behavior must be verified |
| Sensitive files cached | Narrow cache paths; exclude `.env`, keys, credentials, private datasets | Inspect paths and generated files | Tools may generate unexpected files |
| Broad fallback restores incompatible state | Exact lockfile/runtime/toolchain key; narrow fallback | Compare key inputs and cold run | Key correctness does not prove integrity |
| Secret in diagnostics | Allowlist logs; avoid shell tracing/environment dumps | Review scripts and redacted logs | Transformed secrets can still leak |
| Remote BuildKit cache writer compromise | Restrict registry write access; separate cache from release image | Review roles/tokens/destination | Trusted registry does not prove every layer safe |
| Dependency supply-chain risk | Lock and verify dependencies; review image/package sources | Inspect lockfiles, digests, build evidence | M12 covers deeper provenance |
| Excess workflow permissions | Explicit least-privilege `permissions` | Review workflow YAML and repo settings | Other credentials may be supplied by code |
| Unsafe cancellation | Limit cancellation to repeatable validation | Test superseded runs privately | External operations may still be left partial |

OWASP **Top 10 CI/CD Security Risks** is a threat-modeling reference, not a compliance badge. Cache keys are not permission controls, and cache hits are not integrity proof. No secrets, private keys, credentials, or sensitive datasets belong in cache paths.

### 4.9 Production checklist

- [ ] Baseline records SHA, run ID, event, runner type if known, cache state, and environment changes.
- [ ] Pipeline, queue, job, and critical-path durations are distinct; unavailable values are marked unavailable.
- [ ] Cold, warm, and partial-change runs use comparable workloads and documented setup.
- [ ] Repeated samples, median, p95 method, sample count, raw data, and noise notes are retained.
- [ ] Dependency key hashes the authoritative lockfile and relevant runtime/platform dimensions.
- [ ] One package manager is chosen and its lockfile matches the install source of truth.
- [ ] Cache paths exclude secrets, keys, credentials, and sensitive datasets.
- [ ] Untrusted PRs cannot write caches treated as trusted release state; current scope behavior is verified.
- [ ] Fallback keys are narrow; cold-cache runs remain correct.
- [ ] Docker/BuildKit cache, dependency cache, workflow cache, and artifacts are documented separately.
- [ ] Required release outputs use an artifact/package channel with intentional retention.
- [ ] Parallel test execution preserves test coverage and is compared to serial baseline.
- [ ] Shard timing data is maintained and stale timing data handled.
- [ ] Runner CPU/RAM/disk/network/queue are measured before right-sizing.
- [ ] Cancellation is limited to safe workflows and tested on a private branch.
- [ ] Path-based skips cannot silently bypass required checks.
- [ ] Performance SLO defines population, baseline, sample count, noise tolerance, and owner.
- [ ] Cost model uses measured minutes and verified billing inputs.
- [ ] `gh` extraction handles missing fields and labels unavailable queue time.
- [ ] Cache trust review, recovery steps, and ownership are documented.
- [ ] Current action pins, limits, billing, CLI fields, and BuildKit syntax are verified.

### 4.10 Hands-on lab set

All labs use local files or a learner-owned private repository. No public package publication or production deployment. Hosted workflows depend on account/project configuration; **[VERIFY]** current plan and runner availability. Replace all action SHA placeholders with verified full SHAs before running.

#### Lab A — Baseline and critical path

- **ID:** A
- **Goal:** Establish local timing and identify the workflow critical path.
- **Prerequisites:** Python, pytest, Git; private repo optional.
- **Steps:** Create the project from 4.3; run `python scripts/time_tests.py` five times; record results; draw the DAG and calculate its longest path; if hosted workflow is used, save run IDs and job timings.
- **Expected evidence:** baseline CSV/table, DAG, SHA, sample count, timing definitions.
- **Cleanup:** remove `.venv`, `.pytest_cache`, and temporary CSVs unless retained as evidence; verify paths are gone.
- **Stretch:** identify a non-critical job and explain why speeding it up may not change end-to-end duration.

Command: `python scripts/time_tests.py`

**Example — yours will differ**
```text
3 passed
pytest_exit_code=0
elapsed_seconds=0.482
```

Interpretation: illustrative local process time, not hosted pipeline duration.

#### Lab B — Lockfile-keyed dependency cache

- **ID:** B
- **Goal:** Add a dependency cache and measure repeat runs.
- **Prerequisites:** private repository, Actions enabled, verified action SHAs.
- **Steps:** Choose pip; create authoritative pinned `requirements-ci.txt`; add workflow from 4.4; replace SHA placeholders; run once and record key/cache status; repeat without lockfile changes; make a controlled dependency-file change and confirm key changes; restore the file.
- **Expected evidence:** workflow YAML, dependency file, pins, run IDs, cache keys, logs, durations.
- **Cleanup:** revert test dependency change; do not delete shared/production cache.
- **Stretch:** explain added dimensions for cached compiled extensions.

**Example — yours will differ:** cache logs show a lookup and hit or miss. Interpretation: only repeated comparable runs show whether end-to-end performance improved.

#### Lab C — Parallel test strategy

- **ID:** C
- **Goal:** Compare serial tests with a small worker count without weakening correctness.
- **Prerequisites:** local Python; optional `pytest-xdist`.
- **Steps:** run serial tests at least five times; run `pytest -q -n 2` at least five times if xdist is installed; record identical test count, duration, CPU/RAM notes, and failures; investigate shared-state failures before accepting parallel mode.
- **Expected evidence:** serial/parallel timing table, test count, worker count, resource notes, decision.
- **Cleanup:** restore chosen command and remove temporary artifacts.
- **Stretch:** design timing-based shards and list the historical duration data needed.

**Example — yours will differ**
```text
# Serial and parallel runs both report the same test count.
3 passed
```

Interpretation: equal test count is necessary but not enough; compare wall time and stability. A tiny suite may be slower in parallel.

#### Lab D — Stale-cache simulation

- **ID:** D
- **Goal:** Safely simulate stale state and diagnose it from evidence.
- **Prerequisites:** Python and shell.
- **Steps:** create `tmp-cache-lab/dependency-version.txt` with `v1`; test it against expected `v1`; change expected value to `v2` without updating temporary cache file; observe failure; compare expected/actual values; rebuild from authoritative input and rerun.
- **Expected evidence:** before/after file, failure, root-cause note, corrected result.
- **Cleanup:** delete only `tmp-cache-lab`; verify `test ! -e tmp-cache-lab && echo "cleanup verified"`.
- **Stretch:** add a synthetic cache-key function that changes when the authoritative input changes.

**Example — yours will differ**
```text
expected=v2 actual=v1
AssertionError: cached value does not match expected input
```

Interpretation: synthetic local stale-state simulation, not a cache attack or hosted cache experiment.

#### Lab E — Workflow duration extraction

- **ID:** E
- **Goal:** Export run durations and summarize them reproducibly.
- **Prerequisites:** `gh` CLI authenticated with read access; Python.
- **Steps:** verify current `gh run list` JSON fields/flags in official docs; save script from 4.6; run parser tests with synthetic input; check `gh auth status`; run `python scripts/collect_workflow_durations.py --limit 20 --dry-run`; save CSV and calculate median/p95; leave queue time unavailable unless documented data exists.
- **Expected evidence:** parser tests, CSV, sample count, percentile method, missing-field notes.
- **Cleanup:** remove local CSV if not needed; do not delete remote runs or modify workflows.
- **Stretch:** add job-level timing only after verifying current `gh run view` JSON schema and pagination.

Command: `python -m pytest -q tests/test_collect_workflow_durations.py`

**Example — yours will differ**
```text
3 passed
```

Command: `python scripts/collect_workflow_durations.py --limit 20 --dry-run`

**Example — yours will differ**
```text
run_id,workflow,branch,event,status,conclusion,created_at,started_at,completed_at,queue_seconds,run_seconds,head_sha
123456,CI,main,push,completed,success,2026-10-20T10:00:00Z,2026-10-20T10:00:20Z,2026-10-20T10:03:10Z,,170.0,abc123...
```

The row is synthetic, not measured. Verify actual CLI fields. Missing timestamps are not converted to zero; queue time is not inferred.

### 4.11 Self-check questions

1. **What is the critical path?**  
   **Answer:** The longest dependency-constrained path in the DAG.  
   **Why a wrong answer tempts:** the longest individual job looks important but may not constrain completion.

2. **Why is cache not an artifact?**  
   **Answer:** Cache is disposable acceleration state; artifacts are identified outputs/evidence with intentional retention.  
   **Why a wrong answer tempts:** both can make files available later.

3. **What belongs in a dependency cache key?**  
   **Answer:** Authoritative lockfile hash and relevant platform/runtime/toolchain dimensions.  
   **Why a wrong answer tempts:** branch name looks unique but does not define compatibility.

4. **What is the risk of a broad restore key?**  
   **Answer:** It may restore state from different inputs or environments; installation/integrity checks must still run.  
   **Why a wrong answer tempts:** reuse looks harmless but cached state can be incompatible.

5. **Why can more workers make a pipeline slower?**  
   **Answer:** Setup duplication, contention, startup, cache fragmentation, and fan-in overhead.  
   **Why a wrong answer tempts:** parallelism sounds like guaranteed speed.

6. **How should queue time be measured?**  
   **Answer:** Use documented queue/start data where available; otherwise mark unavailable.  
   **Why a wrong answer tempts:** creation-to-start time may include other phases.

7. **How can stale cache mask a dependency break?**  
   **Answer:** A key omits lockfile/runtime inputs or install is skipped after restore.  
   **Why a wrong answer tempts:** cache hit is mistaken for consistency.

8. **How should cold/warm/partial-change runs be compared?**  
   **Answer:** Repeat comparable runs, preserve raw data, compute median and a named p95 method, record noise/sample size.  
   **Why a wrong answer tempts:** one warm run may appear persuasive.

9. **When is test-impact analysis appropriate?**  
   **Answer:** When dependency mapping is maintained, false negatives controlled, unknown changes fall back safely, and full-suite runs validate coverage.  
   **Why a wrong answer tempts:** skipping tests seems easy until an indirect dependency is missed.

### 4.12 Evidence artifacts

Save non-sensitive evidence under:

```text
evidence/
├── baseline-runs.csv
├── optimized-runs.csv
├── workflow-durations.csv
├── benchmark-summary.txt
├── critical-path.md
├── cache-key-rationale.md
├── test-sharding-comparison.md
├── cache-trust-review.md
├── stale-cache-incident.md
├── performance-decision-record.md
└── validation-notes.md

.github/workflows/
├── ci-explicit-cache.yml
└── ci-concurrency.yml

scripts/
├── time_tests.py
├── collect_workflow_durations.py
├── summarize_durations.py
└── estimate_runner_cost.py

tests/
└── test_collect_workflow_durations.py
```

Include baseline/post-change run IDs and SHAs; cold/warm/partial-change labels; raw samples, median, p95 method and noise notes; extraction script and synthetic tests; final workflow YAML and verified action pins; cache-key rationale; serial/parallel comparison; cache-trust review; stale-cache incident; defended decision/rollback; and cleanup verification. Do not save credentials, raw tokens, full environment dumps, sensitive data, or private runner logs.

### 4.13 Common interview and design-review questions

1. **How would you prove caching made the pipeline faster?**  
   **Model answer:** Define the phase, compare cold/warm/partial-change runs, collect repeated samples, preserve run IDs/SHAs, report median and named p95 method, separate queue/runtime where possible, and document noise. Accept no speedup if evidence does not support one.

2. **How would you design a safe Python cache key?**  
   **Model answer:** Use authoritative lockfile hash plus OS/runtime/package-manager dimensions. For compiled output, include ABI/toolchain/build inputs. Keep fallbacks narrow, preserve integrity checks, test cold-cache correctness, and verify scope before sharing across trust boundaries.

3. **When would you parallelize or shard tests?**  
   **Model answer:** When serial baseline shows tests on the critical path and independent work exists. Compare wall time, setup duplication, memory/CPU, shard balance, and identical coverage. Revert if variance/failures increase.

4. **How do you handle stale cache or poisoning?**  
   **Model answer:** Identify key and writers/readers, compare lockfile/runtime, run cleanly without the affected cache, verify dependency state without exposing secrets, isolate untrusted writers, narrow keys/fallbacks, and add regression coverage.

5. **How would you define an SLO and cost model?**  
   **Model answer:** Define event population and metrics, derive thresholds from baseline/noise, set owner/review path, preserve correctness gates, and model cost using measured runner minutes with verified current rate/multiplier inputs.

### Claim Register

Confidence is about the general concept, not current-instance verification. Official docs were not live-consulted during authoring; current platform items remain verification actions.

| ID | Section | Claim | Source (official document + section/title) | Confidence | Tag/verification action |
|---|---|---|---|---|---|
| C01 | 4.2 | Pipeline duration differs from sum of overlapping job durations | GitHub Actions workflow/jobs documentation | High | Verify selected timing definitions |
| C02 | 4.2 | Critical path is longest dependency-constrained path | Workflow dependency concepts | High | Compare with actual DAG |
| C03 | 4.2–4.4 | Cache and artifact have distinct purposes | GitHub Actions cache and artifact docs | High | Verify current lifecycle/access |
| C04 | 4.4 | `actions/cache` supports keys and restore keys | `actions/cache` documentation | High | Verify current inputs/restore behavior |
| C05 | 4.4 | Lockfile hash helps invalidate dependency cache | GitHub dependency caching docs | High | Match hash to authoritative input |
| C06 | 4.4 | `setup-python` has documented cache support | `actions/setup-python` documentation | Medium | [VERIFY] Current inputs/cache paths |
| C07 | 4.4 | pip, uv, and Poetry differ in lockfile/cache behavior | Official pip, uv, Poetry docs | High | [VERIFY] Current paths and lock semantics |
| C08 | 4.4 | SHA pinning strengthens action supply-chain control | GitHub secure use reference | High | Replace placeholders with reviewed full SHAs |
| C09 | 4.4–4.5 | Cache hit does not prove dependency integrity | Package manager docs; OWASP CI/CD risks | High | Retain integrity checks |
| C10 | 4.4 | Docker layer cache differs from package cache | Docker BuildKit docs | High | Verify cache source/invalidation |
| C11 | 4.4–4.5 | BuildKit supports cache import/export backends | Docker Buildx cache docs | High | [VERIFY] Driver/backend syntax |
| C12 | 4.4 | pytest-xdist runs tests in workers | pytest-xdist docs | High | [VERIFY] Current options/compatibility |
| C13 | 4.4 | Parallelism can expose shared-state/order issues | pytest/pytest-xdist docs | High | Test suite independence |
| C14 | 4.4 | GitHub Actions concurrency coordinates runs/jobs by group | Workflow syntax: concurrency | High | [VERIFY] Current pending/cancel semantics |
| C15 | 4.4 | Cancellation can be unsafe for non-idempotent release work | GitHub Actions concurrency docs; operational design | High | Test only in private validation workflow |
| C16 | 4.5 | Cache keys should represent compatibility inputs | GitHub cache docs and toolchain docs | High | Review OS/runtime/ABI/toolchain/lockfile |
| C17 | 4.5 | Restore keys can return data from different inputs | `actions/cache` documentation | High | [VERIFY] Test restore order |
| C18 | 4.5 | Branch/PR cache scope is platform-specific | GitHub cache documentation | Medium | [VERIFY] Review fork/PR scope |
| C19 | 4.5, 4.8 | Untrusted PR must not write trusted release cache | OWASP CI/CD risks; GitHub security docs | High | Review triggers/permissions/cache scope |
| C20 | 4.5 | Cache limits/eviction/retention can change | GitHub cache usage/eviction docs | Medium | [VERIFY] No hard-coded quota |
| C21 | 4.5 | Cache key is not an access-control mechanism | GitHub cache docs; security design | High | Verify permissions separately |
| C22 | 4.5 | Queue time should be separated from job runtime | GitHub workflow/job data docs | High | [VERIFY] Identify documented fields |
| C23 | 4.5 | Shared runner/network noise affects benchmarks | Runner docs; benchmarking practice | High | Record runner/environment |
| C24 | 4.5 | Small samples give weak tail percentile estimates | Statistical percentile concepts | High | Report sample size/method |
| C25 | 4.5 | Parallelism adds setup/contention/fan-in costs | Workflow docs; performance practice | High | Measure wall time/resources |
| C26 | 4.5 | Test-impact analysis can miss tests if dependency edges are absent | Testing practice; OWASP CI/CD context | High | Safe fallback/full-suite checks |
| C27 | 4.6 | Cost model needs measured minutes and verified rates | GitHub billing documentation | Medium | [VERIFY] Current billing rules |
| C28 | 4.6 | Ephemeral runners need external cache persistence | Runner/cache documentation | High | Verify backend and trust |
| C29 | 4.6 | Stale or malicious cache can poison later builds | OWASP CI/CD risks; GitHub cache docs | High | Review writers/readers and clean build |
| C30 | 4.6 | `gh run list` offers structured output in documented versions | GitHub CLI manual: `gh run list` | Medium | [VERIFY] Flags/JSON fields |
| C31 | 4.6 | Selected run fields may not expose queue time | GitHub CLI/API run docs | Medium | [VERIFY] Keep unavailable unless documented |
| C32 | 4.6 | `gh` requires appropriate repository access/authentication | GitHub CLI authentication docs | High | Verify read access; protect credentials |
| C33 | 4.6 | Percentile methods differ across tools | Statistics concepts; script uses nearest-rank | High | Label method and preserve raw samples |
| C34 | 4.7 | SLOs need defined event population and baseline | SRE measurement practice | High | Derive from workload |
| C35 | 4.8 | Cache paths should exclude secrets/sensitive data | OWASP CI/CD risks; GitHub security docs | High | Inspect paths/generated files |
| C36 | 4.8 | Remote BuildKit cache needs controlled access | Docker BuildKit docs; OWASP risks | High | Verify registry roles/destination |
| C37 | 4.8 | Least-privilege workflow permissions reduce token authority | GitHub workflow/security docs | High | Review YAML and repo settings |
| C38 | 4.10 | Private labs reduce unintended external effects | Operational safety practice | High | Confirm repository visibility |
| C39 | 4.10 | Remote cache eviction/deletion is platform-dependent | GitHub cache docs | Medium | [VERIFY] Current cleanup behavior |
| C40 | 4.14 | OWASP CI/CD risks are a threat-modeling reference, not automatic compliance | OWASP Top 10 CI/CD Security Risks | High | Review current official document |

### Ten-pass self-audit

| Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|
| 1 Completeness | FIXED | Broad topic set risks omission | Sections 4.0–4.14, four levels, five labs, extraction, benchmark, and claim register included | Human should check repository-specific conventions |
| 2 Technical accuracy | OPEN | Current CLI/cache/BuildKit details not live-verified | Tagged sensitive items; no fabricated SHAs | Validate YAML and CLI against current docs |
| 3 Executability | OPEN | Hosted workflow and scripts not run | Supplied full scripts, tests, paths, cleanup, representative outputs | SHA placeholders must be replaced before workflow execution |
| 4 Currency | OPEN | Limits/billing/API fields change | No quota/prices asserted; verification list included | Check current docs and plan |
| 5 Security correctness | FIXED | Cache can cross trust boundaries | Explicitly prohibits trusted release cache writes from untrusted PRs and secrets in cache | Confirm actual platform scope/settings |
| 6 Fabrication scan | FIXED | Risk of invented pins/measurements | Placeholders and synthetic outputs clearly labeled | Example IDs/timings remain illustrative |
| 7 Pedagogical consistency | PASS | Cache/artifact/image cache easily conflated | Defined separately and reused Python example | Full FastAPI/ETL is domain context, not a capstone |
| 8 Cross-consistency | FIXED | Queue-time extraction could overstate available data | Script leaves queue blank; benchmark labels unavailable values | Job-level extraction needs verified schema |
| 9 Adversarial review | OPEN | Platform behavior and small-N p95 need scrutiny | Verification checklist and percentile caveats included | Human runtime review needed |
| 10 Lab safety | PASS | Hosted account/plan may vary | Local alternatives; private-only workflows; no public release/deploy | Verify account/runner availability |

**Ten likely skeptical staff-engineer objections**

1. Workflow action pins are placeholders and not directly runnable — intentional; replace with verified full SHAs.
2. `gh` JSON field names may differ — verify current docs; script fails honestly rather than inventing fields.
3. p95 from five runs is weak — explicitly disclose sample count and do not claim statistical robustness.
4. Cache hit can still be wrong — integrity checks and cold-cache tests are required.
5. Broad fallback may restore incompatible state — narrow fallback and key compatibility inputs.
6. BuildKit flags may need a particular driver/registry — example is illustrative and not part of required labs.
7. Parallelism may raise cost/flakiness — compare identical coverage, resource use, and wall time.
8. Queue time may be unavailable — script leaves it blank and explains why.
9. Docs-only skip may bypass gates — require explicit path policy and meaningful required statuses.
10. SLO threshold may be arbitrary — derive it from measured baseline and noise.

### Human verification checklist

**GitHub Actions cache/workflow/concurrency**
- [ ] Read current official dependency-cache and `actions/cache` docs; verify key, restore, scope, retention, eviction, and limits.
- [ ] Verify `setup-python` cache interface and dependency paths.
- [ ] Replace placeholders with verified full action SHAs.
- [ ] Verify `permissions`, `concurrency`, group, pending-run, and cancellation semantics.
- [ ] Run actionlint if available; record version/output. Lint is not runtime proof.

**`gh` CLI/API**
- [ ] Verify current `gh run list` JSON fields/flags and pagination.
- [ ] Verify `gh run view`/API before adding job-level extraction.
- [ ] Test parser on synthetic data; check authentication without sharing sensitive output.
- [ ] Confirm timestamp semantics; keep queue time unavailable unless a documented field supports it.

**Docker/BuildKit**
- [ ] Verify current Buildx syntax, cache mounts, import/export, drivers, modes, and registry permissions.
- [ ] Do not run remote cache command without an approved private destination and least-privilege access.
- [ ] Record WSL2/native Linux filesystem and Docker integration when comparing local timings.

**pip/uv/Poetry and pytest-xdist**
- [ ] Verify lockfile/cache behavior and chosen tool's authoritative dependency file.
- [ ] Include ABI/toolchain dimensions when caching compiled output.
- [ ] Verify xdist compatibility and compare serial/parallel correctness, duration, and resource use.

**Billing/runner**
- [ ] Verify current billing, multipliers, quotas, and plan rules before estimating cost.
- [ ] Record runner type and queue-time source; do not assume free capacity.
- [ ] Never promise a quota or speedup without measurement.

### Known limitations and sign-off

Out of scope: full GitLab implementation; Unit 5's monorepo/path-filtering depth; Unit 6's flaky-test strategy; M01 Unit 4's full Docker build-cache lesson; M10/M11's broader SRE/observability; M12's supply-chain attestations; proprietary test-impact systems.

Action SHA placeholders must be replaced before workflow execution. Cache scope/eviction, billing, `gh` JSON fields, BuildKit syntax, and package-manager cache details were not live-verified. Local timings do not equal hosted pipeline duration. Local emulators such as `act` are not perfectly equivalent to GitHub-hosted runners; **[VERIFY]** check their current fidelity limits before relying on them.

No workflow, benchmark, cache, or hosted runner was executed while authoring. All outputs are representative. AI self-audit does not replace running labs, validating workflow YAML/scripts, and checking current official documentation.

**Content status: DRAFT-AUDITED | Audit date: 2026-10-24 | Auditor: AI self-audit (human verification required) | Open verification items: 18**

### 4.14 Sources and verification notes

**Documentation status:** Official documentation was not live-consulted. These are verification targets, not sources already checked; canonical URLs are omitted where not independently verified.

1. GitHub Actions documentation — dependency caching: keys, restore keys, scope, eviction, limits. **[VERIFY]**
2. GitHub `actions/cache` documentation: inputs and cache lifecycle. **[VERIFY]**
3. GitHub `actions/setup-python` documentation: Python setup and caching. **[VERIFY]**
4. GitHub Actions workflow syntax: permissions, jobs, expressions, concurrency. **[VERIFY]**
5. GitHub Actions security hardening: SHA pinning, token permissions, untrusted contributions. **[VERIFY]**
6. GitHub Actions artifacts documentation: upload/download and retention. **[VERIFY]**
7. GitHub CLI manual: `gh run list` and `gh run view`. **[VERIFY]**
8. GitHub REST API docs for workflow runs/jobs: timestamps and job duration. **[VERIFY]**
9. GitHub Actions billing/usage docs: current runner billing and plan rules. **[VERIFY]**
10. Docker BuildKit and Buildx documentation: cache mounts, import/export, drivers, flags. **[VERIFY]**
11. Official pip documentation: requirements and cache behavior. **[VERIFY]**
12. Official uv documentation: `uv.lock`, synchronization, cache. **[VERIFY]**
13. Official Poetry documentation: `poetry.lock`, installation, cache. **[VERIFY]**
14. Official pytest documentation: test execution. **[VERIFY]**
15. Official pytest-xdist documentation: workers and parallel execution. **[VERIFY]**
16. OWASP Top 10 CI/CD Security Risks: cache trust, secret handling, permissions, supply-chain threats. **[VERIFY]**
17. GitHub Actions runner documentation: runner environment and resource characteristics. **[VERIFY]**

**Tag register**
- `[VERIFY]`: action inputs/SHAs, cache scope/eviction/limits, billing, CLI/API fields, BuildKit flags/driver support, package-manager cache behavior, pytest-xdist options, runner availability.
- `[VERSION-SENSITIVE]`: platform behavior, action interfaces, CLI/API schema, cache policy, billing, and tool compatibility.
- `[ILLUSTRATIVE]`: sample timings, DAG durations, run IDs/timestamps, and example outputs.
- `[ASSUMPTION]`: learner-owned private repository and permitted runner are available if hosted execution is chosen; local tools can be installed. If not, run local labs and mark hosted validation unexecuted.

**Final verification rule:** Do not mark production-verified until action SHAs are reviewed, workflow/scripts are validated, a private pipeline is run, benchmark samples are collected, cache trust is reviewed, and current-doc checks are closed. This lesson is a learning artifact, not proof of executed tests or measured performance.

**Content status: DRAFT-AUDITED | Audit date: 2026-10-24 | Auditor: AI self-audit (human verification required) | Open verification items: 18**
