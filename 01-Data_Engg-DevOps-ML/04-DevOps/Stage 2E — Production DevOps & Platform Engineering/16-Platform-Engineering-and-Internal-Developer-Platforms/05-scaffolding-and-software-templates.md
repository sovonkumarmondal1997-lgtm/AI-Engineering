# Scaffolding and Software Templates

Scaffolding turns an approved golden path into a repeatable, reviewable starting repository. A template is not merely a folder of boilerplate: it is a maintained software product with an input contract, generated-output contract, release process, security boundary, compatibility policy, tests, and update strategy. This unit builds that capability for Python data and ML teams while keeping the guaranteed path local, portable, and zero-budget.

> **Handoff from earlier units:** Unit 2 defined the golden-path components and archetypes; Unit 5 packages that design into repeatable, testable, versioned templates and a safe update mechanism. Unit 4 owns the software catalog and portal, so this unit generates catalog metadata and optionally integrates with Backstage Scaffolder without re-teaching the catalog. M01–M15 mechanisms (image hardening, CI/CD, Kubernetes, GitOps, identity, observability, supply-chain security, recovery, fleet operations, and cost controls) are consumed by the generated output rather than reimplemented here.

## Handoff, Scope, and Learning Outcomes

**Target file:** `05-scaffolding-and-software-templates.md` | **Estimated time:** 32–44 hours | **Prerequisites:** M16 Units 1–4; M01–M15 foundations

**Core tools:** Python 3.11+ (record the actual version), Git, Copier (pin locally after verifying the current release), Cookiecutter for comparison, standard-library Python test harness | **Optional:** Cruft, Backstage Scaffolder, local Gitea, `kind`, Docker/Podman, `kubeconform`

### Scope boundaries

- Unit 2 owns golden-path design and supported archetypes. This unit implements those decisions as templates.
- Unit 4 owns catalog entity design and portal operation. This unit emits `catalog-info.yaml` and explains optional registration only.
- Unit 6 owns Crossplane platform APIs; Unit 7 owns tenant isolation; Unit 8 owns platform SLO/adoption/DX measurement; Unit 9 owns broad governance and deprecation.
- Generated files are starting points. A generated Dockerfile, SLO, policy, or runbook is not evidence that a production system is secure, compliant, or operationally ready.

### Learning outcomes

By completion, you should be able to:

1. Explain scaffolding, template engines, golden paths, and the distinction between generation and ongoing maintenance.
2. Compare Cookiecutter, Copier, Cruft, and Backstage Scaffolder using explicit decision criteria and verified tool behavior.
3. Design a minimal parameter contract with validation, defaults, derived values, and conditional capabilities.
4. Build API, batch/ETL, and model-serving templates, plus a notebook/experiment extension.
5. Generate operationally useful files: app, tests, hardened-image starting point, pinned reusable CI caller, deployment/GitOps placeholders, policy, observability/SLO/runbook, catalog metadata, docs, ownership and hygiene files.
6. Test combinations, invalid inputs, deterministic output, snapshots, mutation detection, and update behavior.
7. Version templates, document breaking changes, and update local repositories without destroying team-owned changes.
8. Run a safe update campaign across at least five synthetic repositories and produce reviewable patches rather than silently merging.
9. Protect template execution, generated output, signatures/hashes, update bots, and portal actions.
10. Operate templates as a platform product using support ownership, release rings, metrics, incident response, and deprecation policy.

### Environment and profiles

| Profile | Purpose | Expected footprint | Required? |
|---|---|---|---|
| **Plat-Core** | Local files, Git, Python standard library, template CLI | Measure on your machine; no cluster or cloud | Yes |
| **Plat+Portal** | Backstage Scaffolder integration | Node toolchain, package install/build; measure before use | No |
| **Plat+Control** | Render/deploy smoke tests with `kind` and container runtime | Additional CPU, RAM and disk; measure first | No |

The baseline learner machine is approximately 4 CPU cores, 8 GB RAM and 30 GB disk. This is a planning constraint, not a guarantee that optional components fit. Do not install optional tools globally unless necessary. Record OS, architecture, Python, Git, template engine and runtime versions in `versions.txt`. Do not use real SCM credentials. Any local server token must be throwaway, least-privilege, injected through an environment or secret mechanism, and excluded from logs and Git.

Synthetic teams, repositories, owners, incidents and measurements in this unit are explicitly **synthetic**. Record your own timings and machine details; do not present them as population-level developer productivity evidence.

## 1. Scaffolding: From Golden Path to Generated Repository

### 1.1 Definition

**Scaffolding** generates a new project or repository from a parameterized template. The template contains the safe starting structure; parameters describe the project; the engine renders files and names; post-generation steps may initialize local tooling. Scaffolding is the delivery mechanism for the Unit 2 golden path. It does not replace CI/CD, IaC, GitOps, a platform API, or operational ownership.

A useful mental model is:

`approved template + validated answers + pinned template revision → generated repository + provenance metadata`

Generation is a point-in-time event. Keeping repositories aligned with later template releases is a separate update lifecycle.

### 1.2 Five approaches

| Approach | Strength | Weakness | Update characteristics | Appropriate use |
|---|---|---|---|---|
| Manual copy-paste | No tooling | Human error, stale defaults, hidden omissions | None | Tiny one-off examples only |
| Repository fork | Familiar Git workflow | Fork accumulates unrelated history and local drift | Merge/rebase is manual and often noisy | Long-lived product variants with deliberate divergence |
| One-time generator | Consistent initial output | Generated repository may lose template provenance | Usually no maintained update path | Disposable prototypes or stable generated assets |
| Update-aware template | Repeatable generation and a defined update workflow | Merge conflicts and migrations still require ownership | Recorded source/answers plus controlled update | Repositories expected to consume platform improvements |
| Portal-driven scaffolding | Discoverable self-service UX and integrated publishing | Portal backend gains privileges and operational burden | Depends on the underlying template source and action design | Organizations that already operate a secure portal |

### 1.3 Why copy-paste fails

Copying a service repository copies yesterday's defaults. A security workflow may be old, a runbook may point to the wrong owner, a cost label may be missing, and a new service may lack the catalog metadata needed during an incident. The problem compounds because copied repositories are independent after creation.

A template system improves consistency only when it also has: (a) an owner, (b) immutable releases, (c) tests against generated output, (d) update guidance, (e) a clear platform/team file boundary, and (f) a way to see which repositories consume which version.

### 1.4 Example

A developer asks for a new API named `risk-score-api`, owned by `analytics`, tier `standard`, with a database. The template derives `risk-score-api` as the repository name, container image name, Kubernetes namespace candidate and catalog name. It conditionally includes database configuration. The developer should not separately type five values that can be derived from one canonical name.

**Checkpoint:** Explain why generating a new repository and updating an existing one are different operations. Name two risks that remain even when generation is automated.

## 2. Why Copy-Paste Fails

### 2.1 Drift and entropy

**Drift** is the divergence between a repository and the intended supported baseline. It may be intentional (business logic) or accidental (old CI action, missing security setting, undocumented deployment). A template cannot prevent drift; it can make the starting state consistent and make later updates safer.

Common failure patterns:

- **Stale defaults:** a base image, runtime, or reusable workflow reference is copied for years.
- **Missing operational metadata:** no valid owner, runbook, service tier, SLO, or dependency declaration.
- **Inconsistent security:** one repository runs tests and scans; another silently omits them.
- **Hidden assumptions:** the copied sample embeds a cloud account, private URL, or placeholder password.
- **No fleet visibility:** platform engineers cannot identify consumers of an old template release.
- **No safe update path:** a platform engineer sends a wiki instruction and expects each team to apply it correctly.

### 2.2 A template is a program

A template consumes input and emits files. Treat it like a compiler pipeline:

1. Parse user answers.
2. Validate types, formats, choices and cross-field constraints.
3. Derive canonical values.
4. Render filenames and file contents.
5. Apply only explicitly declared optional features.
6. Run bounded post-generation tasks, if enabled.
7. Test generated output.
8. Record provenance: template identity, immutable revision and selected options.

Do not execute arbitrary hooks before validation. Do not interpolate untrusted values into shell strings. Prefer argument arrays, allow-lists and file APIs over shell construction.

### 2.3 When not to template

Do not create a template for a single throwaway script, a highly unique research prototype, or a project whose requirements are still changing daily. Start with a small documented example. Template only after repeated patterns and support needs are evidenced.

**Exercise:** List three copied defaults that would be dangerous in your organization. For each, state the owner and the test that would detect regression.

## 3. Template Tools and Their Trade-offs

Tool behavior changes. The exact versions, flags, hook semantics, schema fields, action IDs and compatibility must be checked against official documentation for the pinned release. Items below marked `[VERIFY]` are deliberately not presented as guaranteed current behavior.

### 3.1 Cookiecutter

Cookiecutter is a Python-oriented project generator using a template directory, a `cookiecutter.json` variables file and Jinja2 rendering for filenames and contents. Pre/post-generation hooks can execute code on the machine running generation; treat hooks as executable supply-chain input.

Representative source tree:

```text
cookiecutter-api/
├── cookiecutter.json
└── {{cookiecutter.project_slug}}/
    ├── pyproject.toml
    ├── src/{{cookiecutter.project_slug}}/__init__.py
    └── tests/test_health.py
```

`cookiecutter.json`:

```json
{
  "project_name": "sample-api",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-') }}",
  "owner": "analytics",
  "tier": ["standard", "critical"]
}
```

The exact supported variable-expression behavior in the JSON file is engine/version dependent; keep derived values in a documented hook or use a validated pre-generation wrapper if the chosen release does not evaluate expressions there. The example is illustrative, not a claim that every Cookiecutter version derives the second value this way.

Cookiecutter's native update support is described in many guides as limited; verify the selected version's official documentation before making a definitive claim. **Cruft** is an awareness-level option that adds update-oriented workflows around Cookiecutter templates. Verify its current compatibility, update semantics and limitations before adoption. Do not conflate Cruft behavior with Cookiecutter itself.

### 3.2 Copier

Copier is a template engine with a `copier.yml` configuration, questions, generation commands and an answers file commonly named `.copier-answers.yml`. It provides an update workflow through `copier update`. The exact merge algorithm, conflict artifacts, tasks/migrations, trust behavior, and flags are version-sensitive `[VERIFY]`.

Typical lifecycle:

```text
pinned template revision
        │
        ▼
  copier copy ─────► generated repository + answers/provenance
                              │
                     team-owned changes
                              │
new immutable template release ─► copier update / preview
                              │
                     inspect diff + resolve conflicts
                              │
                       tests + owner review
```

Before running any task-bearing template, verify the current Copier documentation for trust and task execution. Do not use a trust-enabling flag merely to make an error disappear. Use it only after source review and with the exact documented semantics for the pinned version.

### 3.3 Backstage Scaffolder

Backstage Scaffolder is a portal-driven workflow. A template definition commonly contains a `kind: Template`, metadata, parameter forms, steps that invoke actions, and output links. The prompt's example API version `scaffolder.backstage.io/v1beta3`, action names such as `fetch:template`, `publish:*`, and `catalog:register`, and any Gitea publishing action are `[VERIFY]` against the exact Backstage release and installed action packages. Do not copy an old action ID from a blog post and assume it exists.

The portal backend may hold SCM credentials and execute custom actions. It is a privileged execution environment, not a harmless UI. Apply per-action authorization, action allow-lists, narrow credentials, timeouts, audit logs, output sanitization and network egress controls.

### 3.4 Other tools

Yeoman is a generator ecosystem often used in JavaScript-oriented workflows. Projen synthesizes project configuration from code. Nx offers workspace generators. AWS CDK includes project initialization patterns. These are awareness-level alternatives; evaluate ecosystem fit, update model, testing ergonomics, security and maintenance rather than choosing by popularity.

### 3.5 Decision matrix

| Criterion | Cookiecutter | Copier | Cruft | Backstage Scaffolder |
|---|---|---|---|---|
| Ecosystem | Python/Jinja2 | Python/Jinja2-oriented templating | Cookiecutter ecosystem | Portal workflow/actions |
| UX | CLI prompts | CLI prompts/questions | CLI wrapper/workflow | Web forms and task output |
| Output | Files/directories | Files/directories | Cookiecutter output | Files plus configured actions |
| Update model | `[VERIFY]`; do not assume native fleet updates | `copier update` exists; merge semantics `[VERIFY]` | Update-aware wrapper; exact behavior `[VERIFY]` | Depends on source/action architecture |
| Extension | Hooks | Tasks/migrations `[VERIFY]` | Cookiecutter extensions | Built-in and custom actions |
| Security boundary | Generator machine executes hooks | Generator machine may execute tasks | Wrapper and Cookiecutter boundary | Portal backend privileges |
| Testing | Generate then test output | Generate/update then test output | Test generated/update result | Test action workflow and output |
| Operations | Low runtime; maintain template | Low runtime; maintain template and update contract | Additional tool to maintain | Portal, plugins, auth, backend and upgrades |
| Best fit | Simple one-time generation | Local-first generation plus updates | Existing Cookiecutter estate needing update workflow | Portal already justified and operated |

**Roadmap recommendation:** Start with Copier for the Plat-Core update-aware path, retain a Cookiecutter equivalent for comparison, and do not require Backstage. This is a reasoned fit for the lab requirements, not a universal tool ranking. Confirm current official docs and release compatibility before pinning versions.

**Checkpoint:** Which tool owns the template source? Which tool owns the portal UX? Why should those not become two independent sources of truth?

## 4. Template Anatomy and Parameter Design

### 4.1 Source and generated repository

The template repository is the maintained source. A generated repository is a consumer. Keep source-only files (template configuration, tests, fixture matrix, changelog) out of generated output unless they are intentionally part of the consumer contract.

```text
templates/
├── copier.yml
├── template-tests/
├── archetypes/
│   ├── api/
│   ├── batch/
│   └── model-serving/
├── add-ons/
│   ├── database/
│   └── queue-consumer/
├── releases/
│   ├── CHANGELOG.md
│   └── migrations/
└── docs/
```

### 4.2 Five learner-facing questions

1. Project/service name.
2. Owning team.
3. Service tier.
4. Archetype: API, batch/ETL or model-serving.
5. Database capability required?

The archetype determines the workload contract. The tier should be a controlled choice. The database flag should add only database-related configuration. A GPU option must not silently activate for a generic API; it belongs to an explicit model-serving contract and should be a separate capability decision if needed.

### 4.3 Canonical name validation

Use a conservative slug: lowercase ASCII letters/digits separated by single hyphens, 2– forty characters, beginning and ending with an alphanumeric character. A representative regular expression is:

```regex
^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$
```

This regex rejects underscores, spaces, uppercase letters, leading/trailing hyphens and consecutive hyphens. It is not a universal Kubernetes/DNS validator; confirm the stricter naming rules for the actual target resource. Validate before running hooks.

### 4.4 Derived values and cross-field rules

| Derived field | Derivation | Why not ask separately? |
|---|---|---|
| Repository slug | Canonical project name | Prevent inconsistent naming |
| Image name | Registry namespace + slug placeholder | Keep image naming deterministic |
| Catalog name | Slug | Align catalog entity with project identity |
| Namespace candidate | Team + slug, normalized | Avoid asking for duplicate metadata |
| Cost/team label | Owner registry key | Avoid free-form ownership strings |

Cross-field rules include: owner must exist in the synthetic ownership registry; tier must be in the approved set; model-serving may enable inference-specific resources; database capability is allowed only when the chosen archetype supports it; no user input may set an arbitrary filesystem path or shell command.

### 4.5 Representative Copier configuration

The following illustrates the intended contract. Copier's exact question keys, validator syntax, conditional behavior and templating expressions must be checked against the pinned release `[VERIFY]`; treat this as a design example until adapted and validated with the official schema.

```yaml
# copier.yml — representative, verify schema for pinned Copier release
_min_copier_version: "[PIN_AFTER_VERIFICATION]"
project_name:
  type: str
  help: "Project slug, for example risk-score-api"
  validator: "^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"
owner:
  type: str
  help: "Owning team from ownership registry"
  choices:
    - analytics
    - ml-research
tier:
  type: str
  default: standard
  choices:
    - standard
    - critical
archetype:
  type: str
  default: api
  choices:
    - api
    - batch
    - model-serving
needs_database:
  type: bool
  default: false
_answers_file: .copier-answers.yml
```

The keys above are a starting contract, not a claim of compatibility with every Copier version. Before use, compare each field with the official configuration reference for the exact release and run a generation test. If the pinned version's validator syntax differs, implement validation in a small wrapper that runs before Copier.

### 4.6 Plat-Core parameter validator

This dependency-free validator is the authoritative safety gate for the examples in this unit. It validates input before any template engine or task is invoked.

```python
# scripts/validate_request.py
import json
import re
import sys
from pathlib import Path

SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
OWNERS = {"analytics", "ml-research"}  # synthetic allow-list
TIERS = {"standard", "critical"}
ARCHETYPES = {"api", "batch", "model-serving"}


def validate(data: dict) -> dict:
    required = {"project_name", "owner", "tier", "archetype", "needs_database"}
    if set(data) != required:
        raise ValueError(f"expected exactly {sorted(required)}")
    if not isinstance(data["project_name"], str) or not SLUG.fullmatch(data["project_name"]):
        raise ValueError("project_name must be a lowercase hyphenated slug")
    if data["owner"] not in OWNERS:
        raise ValueError("owner is not in the approved ownership registry")
    if data["tier"] not in TIERS:
        raise ValueError("tier must be standard or critical")
    if data["archetype"] not in ARCHETYPES:
        raise ValueError("unsupported archetype")
    if type(data["needs_database"]) is not bool:
        raise ValueError("needs_database must be a boolean")
    if data["archetype"] == "batch" and data["needs_database"]:
        # This is a lab policy decision, not a universal engineering rule.
        raise ValueError("batch archetype database capability requires explicit extension review")
    slug = data["project_name"]
    return {
        **data,
        "repository_name": slug,
        "catalog_name": slug,
        "image_name": f"registry.example.invalid/{data['owner']}/{slug}",
        "namespace_candidate": f"{data['owner']}-{slug}",
        "labels": {"platform.example.invalid/team": data["owner"], "platform.example.invalid/tier": data["tier"]},
    }


if __name__ == "__main__":
    try:
        raw = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        print(json.dumps(validate(raw), indent=2, sort_keys=True))
    except (IndexError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        raise SystemExit(2)
```

Example input `examples/request-api.json`:

```json
{
  "project_name": "risk-score-api",
  "owner": "analytics",
  "tier": "standard",
  "archetype": "api",
  "needs_database": true
}
```

Command from the unit workspace: `python scripts/validate_request.py examples/request-api.json`. Expected behavior: validated JSON with derived values; actual output depends on the exact example input. Invalid names such as `../escape`, `Risk API`, `-bad`, `bad--name`, or `bad_name` must exit non-zero before any hook runs.

### 4.7 Conditional files and binary assets

Conditional generation should be explicit and testable. Database capability adds a DB settings example, migration directory and connection-secret reference documentation; it must not add a password. Queue capability adds a consumer contract and retry/idempotency guidance. Model-serving adds readiness/liveness semantics, model digest configuration and model-card links. Binary files need explicit copy rules and checksums; text templating engines may corrupt binary assets if they attempt to decode or render them. Prefer keeping binary assets in a separate non-rendered directory and verify exact engine support `[VERIFY]`.

Engine-specific exclusion markers such as `_exclude` or `_skip_if_exists` are `[VERIFY]`; do not depend on them without confirming the pinned release behavior. A safe fallback is to generate from separate archetype subdirectories and copy only the selected directory with a reviewed wrapper.

### 4.8 Platform-managed and team-owned contract

| Ownership | Examples | Update policy |
|---|---|---|
| Platform-managed | CI caller, policy baseline, template metadata, catalog schema contract | Prefer isolated files; update through reviewable campaign |
| Team-owned | Application code, domain tests, business configuration | Never overwrite automatically |
| Shared | `pyproject.toml`, Dockerfile, deployment values | Minimize; define merge/migration contract and owner |

Comments or marker blocks do not magically make co-edited files merge-safe. Separate files are the strongest default. Use codemods or manual migration for structural changes; test both against local modifications.

## 5. Build the First Copier Template

### 5.1 Minimal API template

Start with a small API service and then expand it. The template should generate a runnable local Python package, one health endpoint contract, a unit test, docs and catalog metadata. The following output tree is a consumer repository:

```text
risk-score-api/
├── src/risk_score_api/__init__.py
├── tests/test_health.py
├── pyproject.toml
├── Dockerfile
├── .github/workflows/ci.yml
├── platform/ci/reusable-workflow-contract.md
├── deploy/README.md
├── policy/baseline.rego
├── observability/alerts.yaml
├── slo/service.yaml
├── runbooks/README.md
├── catalog-info.yaml
├── docs/index.md
├── .pre-commit-config.yaml
├── .gitignore
├── CODEOWNERS
├── LICENSE-PLACEHOLDER.md
├── NOTICE-PLACEHOLDER.md
└── template-metadata.json
```

`src/risk_score_api/__init__.py`:

```python
SERVICE_NAME = "risk-score-api"


def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}
```

`tests/test_health.py`:

```python
from risk_score_api import health


def test_health_contract():
    assert health() == {"status": "ok", "service": "risk-score-api"}
```

`pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"] # Replace with an approved, locked build environment.
build-backend = "setuptools.build_meta"

[project]
name = "risk-score-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

For a production template, replace illustrative dependency constraints with a reviewed lock strategy and hashes consistent with M01. Do not imply that an unpinned build-system requirement is production-ready.

`Dockerfile` (teaching placeholder):

```dockerfile
# Replace with an approved digest-pinned, non-root base image from M01.
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY src ./src
RUN python -m pip install --no-cache-dir .
USER 10001:10001
EXPOSE 8080
CMD ["python", "-c", "from risk_score_api import health; print(health())"]
```

This file is illustrative only: the base image is not digest-pinned, the example process is not an HTTP server, and the Dockerfile has not been hardened against a real threat model. The production template must replace it with M01's approved image, immutable digest, non-root policy, health behavior, SBOM and image-scan gates.

`.github/workflows/ci.yml`:

```yaml
name: generated-project-ci
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  golden-path:
    # Provider syntax and reusable-workflow location are placeholders.
    # Replace with an approved reusable workflow pinned to an immutable ref.
    uses: YOUR_ORG/YOUR_PLATFORM_REPO/.github/workflows/python-service.yml@REPLACE_WITH_REVIEWED_IMMUTABLE_REF
```

The `uses` form is GitHub Actions-style and must be checked against the actual SCM/CI provider. A placeholder ref intentionally makes the workflow fail closed until configured. Do not replace it with a floating branch in production.

`catalog-info.yaml` (Unit 4 integration; values are synthetic):

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: risk-score-api
  description: Synthetic example API generated by the M16 template lab
  annotations:
    platform.example.invalid/template: python-api
    platform.example.invalid/template-version: "1.0.0"
spec:
  type: service
  lifecycle: experimental
  owner: group:default/analytics
  system: scoring-platform
```

The catalog schema and entity reference conventions must be checked against the Unit 4 catalog configuration and chosen Backstage release `[VERIFY]`. `group:default/analytics` is illustrative; it must resolve to a real Group entity in the catalog.

`template-metadata.json`:

```json
{
  "template_id": "python-api",
  "template_version": "1.0.0",
  "template_revision": "REPLACE_WITH_IMMUTABLE_COMMIT_SHA",
  "archetype": "api",
  "owner": "platform-engineering",
  "generated_at": "OMIT_OR_SET_BY_REPRODUCIBLE_POLICY",
  "project_name": "risk-score-api",
  "team": "analytics"
}
```

Avoid timestamps in generated output if deterministic snapshots are required. If generation time is recorded, isolate it in provenance and exclude it from reproducibility comparisons.

### 5.2 Docs, SLO and runbook are contracts, not claims

`docs/index.md`:

```markdown
# risk-score-api

## Purpose
TODO: describe the business capability and data classification.

## Local development
TODO: document the verified setup and test commands.

## Ownership
Team: analytics (synthetic lab value; replace with a verified owner).

## Operations
See `../runbooks/README.md` and `../slo/service.yaml`.
```

`slo/service.yaml`:

```yaml
service: risk-score-api
status: proposed
owner: analytics
indicators:
  - name: request_success_ratio
    numerator: successful_requests
    denominator: eligible_requests
objective: TODO_DEFINE_WITH_SERVICE_OWNER
window: TODO_DEFINE_WINDOW
source: TODO_LINK_TO_VERIFIED_TELEMETRY
```

`runbooks/README.md`:

```markdown
# Operational runbook — risk-score-api

> Status: SKELETON. Do not use as an incident procedure until completed and tested.

- Owner and escalation: TODO
- Dashboard: TODO
- SLO and alert definitions: TODO
- Rollback procedure: TODO
- Data classification and recovery dependencies: TODO
- Last drill and evidence: TODO
```

`policy/baseline.rego` should be an explicitly marked placeholder or a real tested policy. Do not generate an empty file that looks like a passing control. Example placeholder:

```rego
package platform.generated

# TODO: import the approved organization policy bundle and add tests.
# This placeholder intentionally makes no allow/deny decision.
```

`observability/alerts.yaml`:

```yaml
# Placeholder only. Replace with tested alert rules and owner routing.
groups: []
```

### 5.3 Batch/ETL and model-serving archetypes

| Concern | API/service | Batch/ETL | Model-serving |
|---|---|---|---|
| Entry point | HTTP/service module | Job runner | Prediction handler |
| Contract | Request/response schema | Input/output schema and partition contract | Prediction schema and model identity |
| Reliability | Readiness, timeout, request SLO | Retry, idempotency, checkpoint, backfill | Model-load readiness, timeout, rollback |
| Data | Request classification | Dataset/lineage/quality checks | Feature/data lineage and classification |
| Observability | Request metrics/logs/traces | Run duration, row counts, quality | Latency, error, model version, drift signals |
| Operations | Runbook and deployment | Schedule, replay, late data | Model registry, digest verification, capacity |

Batch template must define an orchestrator-agnostic job contract: configuration, input/output, retry policy, idempotency key, data-quality checks, lineage placeholders, schedule owner and backfill procedure. It must not hard-code Airflow, Dagster or another orchestrator unless the organization explicitly chooses one.

Model-serving template must reference a model registry artifact and immutable digest/hash, not download a real model in Plat-Core. Include prediction API skeleton, readiness check that fails until the model is verified and loaded, resource request placeholders, scaling/SLO placeholders, model-card link and rollback notes. A generated model-serving directory does not prove GPU access, model quality or serving performance.

Notebook/experiment extension should separate exploratory notebooks from production modules, record environment/dependency metadata, avoid secrets and sensitive data in notebook outputs, and provide a promotion path from experiment to tested pipeline. Notebook stripping hooks such as `nbstripout` are awareness-level `[VERIFY]` and must be tested before use.

### 5.4 Full generated content contract

| File group | Shared | Archetype-specific | Conditional |
|---|---|---|---|
| App + tests | Project metadata, test runner | API/job/predictor skeleton | Optional DB/queue modules |
| Dockerfile | Approved base-image pattern | Entrypoint and runtime | GPU image only by explicit approval |
| CI caller | Pinned reusable workflow | Test/build matrix | Optional integration tests |
| Deployment | Common labels/metadata | Service vs job vs inference | DB/queue references |
| GitOps | Environment overlay pattern | Workload kind | Capability resources |
| Policy | Approved baseline bundle reference | Workload-specific constraints | Feature policies |
| Observability | Labels and ownership | Request/job/model metrics | Dashboards for selected capabilities |
| SLO/runbook | Skeleton and TODOs | Relevant indicators and procedures | Backup/restore if stateful |
| Catalog | Owner/system/lifecycle | Component type and dependencies | API/resource entities |
| Hygiene | `.gitignore`, pre-commit, CODEOWNERS | Team code | License/notice values from organization |

Do not invent a license. Generate `LICENSE-PLACEHOLDER.md` instructing the repository owner to obtain an approved license. Do not fabricate compliance badges or claim that a generated repository is production approved.

## 6. Build and Compare a Cookiecutter Template

### 6.1 Equivalent API example

Create `cookiecutter-api/cookiecutter.json`:

```json
{
  "project_name": "risk-score-api",
  "owner": "analytics",
  "tier": "standard"
}
```

Use a template directory with Jinja2-rendered path names such as `{{cookiecutter.project_name}}/src/{{cookiecutter.project_name | replace('-', '_')}}/`. Exact escaping and variable behavior must be tested with the pinned Cookiecutter release. Add a pre-generation validation wrapper rather than relying on a hook that runs after files have already been rendered.

The generated output should be semantically equivalent to the Copier API archetype: same package contract, tests, Dockerfile placeholder, CI caller, catalog metadata, docs, SLO and runbook. Compare normalized file trees and file content after removing engine-specific provenance.

### 6.2 Compare update behavior honestly

1. Generate `api-v1` from each engine using the same synthetic answers.
2. Edit a team-owned application file in both generated repositories.
3. Change the template's platform-managed CI reference.
4. Release the changed template as a new immutable revision.
5. Run the documented update workflow for each tool, only after verifying the selected version's official commands.
6. Record whether local edits remain, whether conflicts are reported, what files change, and what manual work is needed.
7. If Cookiecutter alone does not provide the desired update workflow, test Cruft separately rather than attributing Cruft behavior to Cookiecutter.

Do not state that one engine always merges better. The result depends on template structure, file ownership, engine version, local modifications and migration complexity.

### 6.3 Tool behavior verification register

| Item | Status | Exact verification task |
|---|---|---|
| Copier question types/validators/conditions | `[VERIFY]` | Open official configuration reference for pinned release; validate every key with a real generation test |
| Copier non-interactive flags | `[VERIFY]` | Confirm `--data`, `--defaults`, `--skip-answered` and exact behavior from `copier copy --help` and docs |
| Copier update merge/conflict artifacts | `[VERIFY]` | Generate v1, edit files, update to v2; inspect actual conflicts and resulting files |
| Copier tasks/migrations/trust | `[VERIFY]` | Verify official tasks/migrations/trust docs; run only reviewed local fixture |
| Cookiecutter hooks and update support | `[VERIFY]` | Check official docs for pinned release; test hook ordering and exact update limitation |
| Cruft update behavior | `[VERIFY]` | Pin Cruft; test update against same v1/v2 fixture |
| Backstage API/action IDs | `[VERIFY]` | Check docs for exact Backstage and action-package versions; validate template schema |
| Backstage SCM publish integration | `[VERIFY]` | Confirm installed action ID exists; otherwise use local file output |
| Binary and skip/exclude behavior | `[VERIFY]` | Test exact engine/version on binary fixture and collision fixture |

## 7. Generate the Full Golden-Path Repository

### 7.1 Repository composition

The generated repository should be coherent and small. Do not produce every optional integration for every project. Use the parameter contract to select only the relevant archetype and capability files.

```text
<project>/
├── src/                         # API, job, or predictor code
├── tests/
├── pyproject.toml
├── Dockerfile                   # platform-managed starting point
├── .github/workflows/ci.yml     # platform-managed reusable workflow caller
├── platform/                    # platform-managed metadata and contracts
├── deploy/                      # archetype-aware manifests/overlays
├── gitops/                      # environment references; no secrets
├── policy/                      # approved bundle reference + local tests
├── observability/               # alerts/dashboard placeholders
├── slo/service.yaml              # proposed objective, not an achieved SLO
├── runbooks/                     # explicit TODO skeleton
├── catalog-info.yaml             # Unit 4 catalog registration metadata
├── docs/
├── .pre-commit-config.yaml       # pinned hooks after verification
├── .gitignore
├── CODEOWNERS                    # synthetic owner placeholder
├── LICENSE-PLACEHOLDER.md
├── NOTICE-PLACEHOLDER.md
└── template-metadata.json
```

### 7.2 CI, deployment and policy

The CI workflow should call a centrally maintained reusable workflow at an immutable reviewed reference. The template should not duplicate all CI steps because that creates a second maintenance surface. The caller file is platform-managed; application tests remain team-owned. Provider-specific syntax and permission semantics are `[VERIFY]`.

Deployment files should contain placeholders for approved chart/overlay references and resource requests. GitOps manifests should point to the approved repository layout. Never include credentials, kubeconfigs, tokens, internal hostnames or real account IDs. Policy configuration should reference an approved policy bundle or include a small tested policy; an empty placeholder must be labelled as such.

### 7.3 Post-generation tasks

Separate pure rendering from side effects. Safe optional tasks may:

- initialize a local Git repository;
- create an initial commit only after explicit user confirmation;
- install pre-commit hooks after showing the exact command;
- generate a lockfile using a pinned, approved toolchain;
- optionally create a remote repository through a local test server.

Do not automatically push, create remote repositories, install arbitrary dependencies, deploy infrastructure or delete files. Never construct shell commands by concatenating raw parameter values. Use subprocess argument lists, a fixed working directory, bounded timeout and explicit allow-list.

Local Git setup without remote server:

```bash
# Working directory: generated project root
# Purpose: initialize a local repository; no remote and no network access.
git init
git add .
git status --short
# Review staged files before committing.
git diff --cached --check
```

Do not run `git commit` until identity, license and generated content have been reviewed. A local Gitea integration is optional; if unavailable, a normal local Git repository and patch bundle are sufficient.

## 8. Post-Generation Tasks and Local Repository Setup

### 8.1 Task design principles

Tasks run code on the generator host or CI worker. They must be explicit, observable, bounded, and repeatable where possible. Validation must happen first. Tasks should not make hidden network calls. Avoid automatic dependency installation as a side effect of `copy`.

A safe task contract records: task name, purpose, allowed command, fixed working directory, input allow-list, timeout, expected output, failure behavior, and whether rerunning is safe. If the task is not required for the generated files, make it opt-in.

### 8.2 Local repository bootstrap

Use Git only after generation and validation. Check for an existing `.git` directory before initialization. Do not overwrite a pre-existing repository. For a local patch bundle, create a branch or temporary copy and keep the original untouched. The update campaign later in this unit uses isolated worktrees/copies and emits reviewable artifacts.

### 8.3 Remote repository creation

If a local server is used, create a throwaway account/token scoped to a single test organization/repository operation. Read the token from an environment variable or secret store. Never echo it, put it in a URL, commit it, or include it in the report. The server API, endpoint and token scopes are implementation-specific `[VERIFY]`. If there is no local server, generate a patch bundle and report; do not block the core lab.

**Failure mode:** a post-generation hook pushes to a remote repository before tests run. Containment: revoke the throwaway token, inspect audit logs, remove accidental repository if safe and authorized, and disable the hook. Prevention: separate render and publish stages, explicit confirmation, and negative tests proving default generation makes no network calls.

## 9. Automated Template Testing

### 9.1 Treat templates as compilers

A template test suite validates both the template source and every important class of generated project. A green template repository test does not prove all generated combinations work. Test generated output using the same quality gates expected of a real repository.

### 9.2 Matrix

| Dimension | Example values |
|---|---|
| Archetype | API, batch, model-serving |
| Tier | standard, critical |
| Database | false/true where allowed |
| Queue add-on | absent/present |
| Runtime | approved Python baseline(s) |

The full Cartesian product may be unnecessarily large. Use pairwise coverage for broad combinations plus explicit critical combinations and all invalid boundaries. Document the chosen coverage strategy.

### 9.3 Test categories

| Test | Defect detected | Plat-Core implementation |
|---|---|---|
| Schema/parameter tests | Invalid type, slug, owner or unsupported choice | `validate_request.py` unit tests |
| Snapshot/golden tests | Unexpected file/content change | Normalize and compare selected outputs |
| Negative tests | Injection, path traversal, invalid combination | Hostile fixture corpus |
| Determinism | Timestamps/random values change output | Generate twice and compare normalized trees |
| Idempotency | Repeated add-on duplicates content | Apply twice and compare tree |
| Mutation | Missing CI caller or required test | Remove/alter fixture file; assert harness fails |
| Static checks | Syntax, formatting, secrets, policy | Run only installed/pinned tools; record versions |
| Image build | Dockerfile invalid or dependency build failure | Optional when runtime exists |
| Manifest render/schema | Invalid YAML/API schema | Optional with pinned renderer/validator |
| Deployment smoke | Runtime behavior | Plat+Control only, never core prerequisite |

### 9.4 Standard-library test harness

`tests/test_contract.py`:

```python
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_request", ROOT / "scripts/validate_request.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

BASE = {
    "project_name": "risk-score-api",
    "owner": "analytics",
    "tier": "standard",
    "archetype": "api",
    "needs_database": True,
}


class ContractTests(unittest.TestCase):
    def test_valid_request_derives_names(self):
        result = module.validate(BASE)
        self.assertEqual(result["repository_name"], "risk-score-api")
        self.assertEqual(result["catalog_name"], "risk-score-api")
        self.assertIn("analytics", result["image_name"])

    def test_rejects_path_traversal(self):
        data = {**BASE, "project_name": "../escape"}
        with self.assertRaises(ValueError):
            module.validate(data)

    def test_rejects_shell_metacharacters(self):
        data = {**BASE, "project_name": "safe;touch-pwned"}
        with self.assertRaises(ValueError):
            module.validate(data)

    def test_rejects_unknown_owner(self):
        with self.assertRaises(ValueError):
            module.validate({**BASE, "owner": "admin"})

    def test_rejects_unknown_fields(self):
        with self.assertRaises(ValueError):
            module.validate({**BASE, "command": "echo unsafe"})

    def test_database_type_must_be_boolean(self):
        with self.assertRaises(ValueError):
            module.validate({**BASE, "needs_database": "true"})


if __name__ == "__main__":
    unittest.main()
```

The test module above imports the validator directly and runs without Copier. Add engine-specific integration tests only after installing and pinning the actual tool. Use `python -m unittest discover -s tests -v` from the template workspace.

### 9.5 Mutation testing

Mutation testing deliberately introduces a defect to prove the test suite catches it. Examples:

- Remove the CI caller: golden-path contract test must fail.
- Replace the owner with `unknown-team`: catalog validation must fail.
- Remove `tests/test_health.py`: generated-project test gate must fail.
- Change a pinned reusable-workflow ref to a floating branch: policy test must fail.
- Add a literal placeholder password: secret/placeholder scan must fail.

Do not claim a mutation test passes until you actually inject the mutation and observe a non-zero test result.

### 9.6 Optional Plat+Control

If Docker/Podman and `kind` fit the measured resource budget, render manifests, validate them with a pinned schema tool, deploy to a disposable local cluster, run a smoke test, and delete only that named cluster. Never make this a prerequisite. Record cluster version, images, resource use and teardown verification. If tools are unavailable, run static rendering and contract tests and state the fidelity limitation.

## 10. Versioning, Compatibility, and Release Engineering

### 10.1 Immutable releases

A template release should be identifiable by a version and immutable source revision. A Git tag is convenient but can be moved unless repository policy prevents it. Record both the human-readable release and the resolved commit SHA. Verify the tag/signature or hash before use.

SemVer is a policy choice, not an automatic property of a template engine:

- **Patch:** generated output correction that does not change the documented input/output contract.
- **Minor:** backward-compatible capability or optional file addition.
- **Major:** required parameter change, file removal/rename, changed behavior, incompatible metadata or changed default with operational impact.

A default change can be breaking even when no parameter name changes. Document migration steps.

### 10.2 Example metadata and changelog

`template-release.json` (illustrative convention, not engine-native metadata):

```json
{
  "template_id": "python-service",
  "version": "1.1.0",
  "commit": "REPLACE_WITH_FULL_IMMUTABLE_COMMIT_SHA",
  "supported_archetypes": ["api", "batch", "model-serving"],
  "support_status": "supported",
  "owner": "platform-engineering"
}
```

`CHANGELOG.md`:

```markdown
# Changelog

## 1.1.0 — YYYY-MM-DD
- Added explicit `service_tier` metadata to generated catalog entity.
- Updated the platform-managed reusable CI workflow reference.
- Migration: consumers without `service_tier` must use the documented default mapping before update.

## 1.0.0 — YYYY-MM-DD
- Initial API, batch and model-serving template contract.
```

Do not claim dates/releases that have not occurred. Replace placeholders at actual release time.

### 10.3 Compatibility policy

A local policy may support current release N and previous minor/major N−1 for a defined support window. That is an organization decision, not an industry standard. Unit 9 owns the broader governance process; this unit provides the mechanics.

Breaking examples:

- CI workflow filename rename can cause duplicate workflows.
- New required question can stall unattended updates.
- Changed default can alter resource tier or exposure.
- Removed file can erase team modifications if update is unsafe.
- Runtime/base image change can break dependencies.
- Moving platform-managed configuration changes ownership assumptions.
- Catalog metadata schema change can make entities invalid.

### 10.4 Release pipeline

`validate source → generate matrix → test generated output → security scan → verify/sign provenance → publish immutable release → canary consumers → announce → monitor adoption`

Only publish after the exact release artifacts have passed. If signing infrastructure is not available, use a local SHA-256 manifest for the lab and clearly state that a hash stored beside the artifact does not authenticate the publisher. Production signing and verification should follow M12 Unit 4's approved process.

## 11. Updating Existing Repositories Safely

### 11.1 Generation is not maintenance

The update lifecycle is:

`template source → immutable release → generated repository → local team changes → new template release → update preview/diff → CI and policy gates → reviewable PR → merge by owner → version inventory`

Copier's `copier update` is the expected update mechanism for Copier-generated repositories, but exact flags, answer-file behavior, merge behavior and conflict artifacts must be verified for the pinned version. Use a throwaway fixture before a real repository.

### 11.2 Conflict classes

| Conflict | Example | Safe response |
|---|---|---|
| Clean merge | CI caller changed; no local edit | Review diff and run CI |
| Content conflict | Team modified shared Dockerfile | Preserve intent; resolve with owner |
| Rename/delete | Template renames workflow | Search all references; ensure only one pipeline remains |
| New required parameter | v2 asks for a new tier | Provide deterministic migration/default or mark repo blocked |
| Local customization | Team has extra alert | Move to team-owned path or document merge contract |
| Dependency lock change | Template updates runtime lock | Regenerate with pinned toolchain and review dependency diff |

Never blind-overwrite local code. Never assume `.rej` files or inline conflict markers exist; inspect actual tool output.

### 11.3 Worked v1 to v2 migration

Synthetic v1 has `.github/workflows/ci.yml` and `template_version=1.0.0`. A team has modified `src/service.py`. v2 updates the CI caller to a reviewed reusable workflow reference and adds required `service_tier` metadata.

Safe sequence:

1. Clone/copy the v1 repository into an isolated worktree.
2. Preserve the original working tree and record `git status`.
3. Run the update against immutable v2 revision.
4. If the new question cannot be answered non-interactively, stop and mark `BLOCKED_INPUT`; do not guess a tier.
5. Inspect every changed/deleted/renamed file.
6. Confirm `src/service.py` still contains the team change.
7. Confirm exactly one active CI workflow remains.
8. Run generated-project tests, policy checks and secret scan.
9. Produce a patch/PR and assign the repository owner.

### 11.4 Update report schema

```json
{
  "repository": "synthetic-api-01",
  "owner": "analytics",
  "current_template": "1.0.0",
  "target_template": "2.0.0",
  "status": "CONFLICT",
  "changed_files": [".github/workflows/ci.yml"],
  "preserved_local_edits": true,
  "tests": "NOT_RUN",
  "review_artifact": "patches/synthetic-api-01.patch",
  "notes": "Owner must resolve service_tier and workflow rename"
}
```

All repository names and values in this example are synthetic.

## 12. Fleet Update Campaigns and Bot Safety

### 12.1 Five-repository campaign

The core lab creates five synthetic repositories at different template versions with different local edits. The campaign tool must be conservative: it produces isolated patches and a report; it does not merge automatically and does not push to a remote service by default.

Synthetic inventory:

| Repo | Owner | Current template | Local change | Expected outcome |
|---|---|---|---|---|
| `synthetic-api-01` | analytics | 1.0.0 | app code only | clean patch candidate |
| `synthetic-api-02` | analytics | 1.0.0 | shared Dockerfile edit | conflict/owner review |
| `synthetic-batch-03` | ml-research | 1.0.0 | job config | patch candidate |
| `synthetic-model-04` | ml-research | 0.9.0 | custom workflow | migration review |
| `synthetic-api-05` | analytics | 1.0.0 | missing owner metadata | blocked by validation |

### 12.2 Safe local campaign implementation

This simplified implementation demonstrates inventory processing, path allow-listing, diff-size limit, rate limit, kill switch and patch output. It does **not** run Copier or Git automatically; the `update_command` callback is an explicit integration point. This avoids pretending that unverified flags or engine semantics are stable.

`tools/update_campaign.py` (runnable local three-way-safe file campaign; no Copier dependency):

```python
from __future__ import annotations
import argparse
import difflib
import json
import os
import shutil
from pathlib import Path

ALLOWED_PREFIXES = (".github/", "platform/", "policy/", "catalog-info.yaml", "template-metadata.json")
MAX_REPOS_PER_RUN = 5
MAX_CHANGED_FILES = 20


def allowed_path(relative: str) -> bool:
    normalized = relative.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return any(normalized == item or normalized.startswith(item) for item in ALLOWED_PREFIXES)


def files_under(root: Path) -> dict[str, Path]:
    found = {}
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            relative = path.relative_to(root).as_posix()
            if not allowed_path(relative):
                raise ValueError(f"target contains forbidden path: {relative}")
            found[relative] = path
    return found


def update_one(repo: Path, base: Path, target: Path, out: Path) -> dict:
    original = {}
    work = out / f"work-{repo.name}"
    shutil.copytree(repo, work, ignore=shutil.ignore_patterns(".git"), dirs_exist_ok=True)
    base_files, target_files = files_under(base), files_under(target)
    changed, conflicts, diffs = [], [], []
    for relative, new_path in target_files.items():
        destination = work / relative
        new_text = new_path.read_text(encoding="utf-8")
        old_path = base_files.get(relative)
        old_text = old_path.read_text(encoding="utf-8") if old_path else None
        current_text = destination.read_text(encoding="utf-8") if destination.exists() else None
        if current_text == new_text:
            continue
        if current_text is None or (old_text is not None and current_text == old_text):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(new_text, encoding="utf-8")
            changed.append(relative)
            before = current_text or ""
            diffs.extend(difflib.unified_diff(before.splitlines(True), new_text.splitlines(True),
                                              fromfile=f"a/{repo.name}/{relative}",
                                              tofile=f"b/{repo.name}/{relative}"))
        else:
            conflicts.append(relative)  # Preserve local file; never overwrite it.
    if len(changed) > MAX_CHANGED_FILES:
        return {"repository": repo.name, "status": "BLOCKED_DIFF_LIMIT", "changed_files": changed,
                "conflicts": conflicts, "work_copy": str(work)}
    patch_path = out / f"{repo.name}.patch"
    patch_path.write_text("".join(diffs), encoding="utf-8")
    status = "CONFLICT" if conflicts else ("PATCH_READY" if changed else "NO_CHANGE")
    return {"repository": repo.name, "status": status, "changed_files": changed,
            "conflicts": conflicts, "patch": str(patch_path), "work_copy": str(work),
            "tests": "NOT_RUN", "merge": "NEVER_AUTOMATIC"}


def campaign(repos_root: Path, base: Path, target: Path, output: Path) -> list[dict]:
    if os.environ.get("TEMPLATE_CAMPAIGN_KILL_SWITCH") == "1":
        raise RuntimeError("kill switch is active")
    repos = sorted(p for p in repos_root.iterdir() if p.is_dir() and not p.name.startswith("."))
    if len(repos) < 5:
        raise ValueError("provide at least five synthetic repository directories")
    if len(repos) > MAX_REPOS_PER_RUN:
        raise ValueError(f"this lab run is limited to {MAX_REPOS_PER_RUN} repositories")
    output.mkdir(parents=True, exist_ok=True)
    report = []
    for repo in repos:
        if os.environ.get("TEMPLATE_CAMPAIGN_KILL_SWITCH") == "1":
            report.append({"repository": repo.name, "status": "STOPPED_KILL_SWITCH"})
            break
        report.append(update_one(repo, base, target, output))
    (output / "campaign-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="Safe local template update patch generator")
    parser.add_argument("--repos", type=Path, required=True, help="directory containing five synthetic repos")
    parser.add_argument("--base", type=Path, required=True, help="old platform-managed template files")
    parser.add_argument("--target", type=Path, required=True, help="new platform-managed template files")
    parser.add_argument("--out", type=Path, required=True, help="new output directory")
    args = parser.parse_args()
    rows = campaign(args.repos, args.base, args.target, args.out)
    print(json.dumps(rows, indent=2))

if __name__ == "__main__":
    main()
```

The script is intentionally a local patch-bundle implementation. It uses a base-template snapshot to distinguish untouched platform-managed files from local modifications; any locally modified file is preserved and reported as a conflict. It does not create remote PRs, execute Copier, run repository tests, resolve new required parameters, or prove semantic merge safety. Add owner inventory, per-repository tests, Git worktrees, a verified Copier adapter and a local-server PR publisher only after separately testing those integrations. `ALLOWED_PREFIXES` is an example policy; adapt it with repository owners and security reviewers.

### 12.3 Bot safety controls

| Control | Failure prevented | Required test |
|---|---|---|
| Least-privilege identity | Bot compromise becomes org-wide write access | Token scope review; no token in logs |
| Protected branches and required review | Silent merge of bad code | Assert campaign never merges |
| Path allow-list | Unexpected application-code changes | Forbidden path is rejected |
| Diff-size limit | Huge accidental rewrite | More than max files/lines is blocked |
| Rate/concurrency limit | CI queue saturation | Excessive repo count is rejected |
| Kill switch | Campaign continues during incident | Set env switch and verify stop |
| Audit log | No accountability | Every repo status and artifact recorded |
| Owner resolution | Unowned change | Missing owner is blocked |
| Dry-run default | Unreviewed side effects | Default invocation creates only local output |

Treat the update bot as a high-blast-radius identity. No auto-merge by default. If an organization later considers auto-merge for low-risk changes, that is an `[ASSUMPTION]` requiring a separately approved policy, strong tests and explicit risk acceptance.

### 12.4 Version spread and adoption lag

Track repository count by template version, owner, archetype, blocker, open update PR, conflict, test failure and security priority. Update lag is measured from release publication to repository adoption. Define numerator, denominator and time window. Do not invent lab results: record actual local run times and the synthetic sample size.

## 13. Backstage Scaffolder Integration

<badge color="secondary">Optional Plat+Portal</badge>

### 13.1 Architecture decision

Two broad approaches exist:

1. Maintain a separate Backstage-native template using the portal's templating engine.
2. Keep Copier as the single template source and invoke it through a controlled custom action or CI service.

**[ASSUMPTION]** For this roadmap, one source of truth is preferred because separate Jinja2 and Nunjucks implementations can diverge. The trade-off is that a custom action or CI service must safely invoke Copier, handle trust, pin the template revision, isolate execution, authorize the requester and report output. Verify that the selected Backstage version supports the required integration; do not assume a built-in Copier action exists.

### 13.2 Nunjucks versus Jinja2

Backstage Scaffolder's built-in templating is Nunjucks-oriented; Copier commonly uses Jinja2. They have similar ancestry but are not interchangeable languages. Filters, escaping, control flow, undefined variables and file naming may differ. If both engines render independently, add parity tests over the same fixture matrix and compare normalized generated trees. Better, keep the canonical template source in one engine and use the portal as a front door.

### 13.3 Representative Backstage Template YAML

This is a conceptual skeleton only. `apiVersion`, parameter schema, step/action IDs, output syntax and plugin availability are `[VERIFY]` against the pinned Backstage release and installed action packages.

```yaml
apiVersion: scaffolder.backstage.io/v1beta3 # [VERIFY] for pinned release
kind: Template
metadata:
  name: python-api-template
  title: Python API service
  description: Generate an API from the approved platform template
spec:
  owner: group:default/platform-engineering
  type: service
  parameters:
    - title: Service details
      required: [project_name, owner, tier]
      properties:
        project_name:
          title: Project slug
          type: string
          pattern: '^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$'
        owner:
          title: Owning team
          type: string
          enum: [analytics, ml-research]
        tier:
          title: Tier
          type: string
          enum: [standard, critical]
  steps:
    - id: generate
      name: Generate approved template
      action: platform:copier:generate # custom action; not built-in
      input:
        templateRevision: REPLACE_WITH_IMMUTABLE_SHA
        projectName: ${{ parameters.project_name }}
        owner: ${{ parameters.owner }}
        tier: ${{ parameters.tier }}
  output:
    text:
      - title: Generated project
        content: Review the task output and repository owner instructions.
```

Do not deploy this YAML as-is. The custom action name is deliberately illustrative. It must be implemented, reviewed, registered and allow-listed by the portal operators. If a safe custom action is not available, use the local file-output fallback and keep Backstage as a form/preview demonstration only.

### 13.4 Security review

- SCM token scoped to the single test repository or organization operation; no organization-admin token.
- Per-user authorization for template use and target repository; exact identity propagation is `[VERIFY]`.
- Action allow-list and reviewed custom action source.
- No arbitrary shell input from user parameters.
- Fixed template revision and source allow-list.
- Timeouts, resource limits, isolated execution and network egress controls.
- Audit task identity, input summary, template revision, target repository and result.
- Do not put static secrets in committed `app-config.yaml`.
- A catalog registration step must validate the generated `catalog-info.yaml` and target location; Unit 4 owns catalog trust policy.

### 13.5 Preflight and cleanup

Before installation, record CPU, memory, disk, OS, architecture, Node/package-manager versions, network access and estimated build footprint. Use official Backstage create-app instructions for the selected version. Exact command, Node range, package manager, guest auth setup, local catalog location and TechDocs steps are `[VERIFY]`. Run Backstage alone; stop other optional heavy services. If preflight fails, complete all Plat-Core labs. Stop the app and verify the local generated projects remain usable without the portal.

## 14. Template Security and Supply-Chain Controls

### 14.1 Threat model

Templates are executable supply-chain inputs. Cookiecutter hooks and Copier tasks may execute arbitrary commands on the generator host. A portal action can run with backend credentials. A malicious template can embed insecure defaults across many repositories. An update bot can modify multiple repositories with one identity.

| Asset | Threat actor/path | Impact | Prevention | Detection/recovery |
|---|---|---|---|---|
| Template source | Compromised maintainer or dependency | Fleet-wide malicious output | Protected review, immutable pin, release verification | Hash/signature mismatch; revoke release and publish fix |
| Generator host | Malicious hook/task | Local data theft or command execution | No untrusted hooks; isolated worker; least privilege | Process/network audit; rebuild worker |
| User parameters | Malicious requester | Path traversal, shell/YAML injection | Strict schema, allow-lists, no shell interpolation | Negative tests and rejected request logs |
| Generated repository | Insecure defaults/secrets | Deployment compromise | Output scanning and policy tests | Secret scan, conformance scan, incident response |
| Portal backend | Malicious custom action | SCM token abuse | Action allow-list, narrow tokens, code review | Audit logs, token revocation |
| Update bot | Credential compromise or bug | Multi-repo mass changes | PR-only, path/diff/rate limits, kill switch | Campaign telemetry and rapid disable |

### 14.2 Pin and verify template source

Pin by full commit SHA or immutable trusted release. A tag alone can be moved unless repository controls prevent it. Review template changes like code. Sign releases using the organization's M12-approved mechanism. Verify before executing any hook/task.

The local Plat-Core fallback can verify a SHA-256 manifest. This proves the bytes match a previously trusted digest only if the digest itself came through a trusted channel. A digest stored beside an attacker-controlled template is not authentication.

`tools/verify_template.py`:

```python
import hashlib
import json
import sys
from pathlib import Path


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts):
        rel = path.relative_to(root).as_posix().encode()
        digest.update(len(rel).to_bytes(4, "big"))
        digest.update(rel)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def verify(root: Path, manifest: Path) -> bool:
    expected = json.loads(manifest.read_text(encoding="utf-8"))
    if expected.get("revision_type") != "immutable-commit":
        return False
    if not expected.get("revision") or expected["revision"] == "main":
        return False
    return tree_hash(root) == expected.get("sha256")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_template.py TEMPLATE_DIR MANIFEST.json")
    ok = verify(Path(sys.argv[1]), Path(sys.argv[2]))
    print("VERIFIED" if ok else "REJECTED")
    raise SystemExit(0 if ok else 3)
```

Example manifest format:

```json
{
  "revision_type": "immutable-commit",
  "revision": "REPLACE_WITH_FULL_COMMIT_SHA",
  "sha256": "REPLACE_WITH_TRUSTED_TREE_SHA256"
}
```

The wrapper deliberately refuses a floating reference such as `main`. It is a local integrity demonstration, not a production signature system. For production, verify a signed provenance statement using the organization's approved signing/verification tools and trust roots. Do not invent signing CLI commands; use M12 Unit 4's verified process.

### 14.3 Injection tests

Hostile values to reject before rendering:

- Path traversal: `../../outside`.
- Shell metacharacters: `api; touch /tmp/pwned`.
- YAML-breaking text: `api\nowner: admin`.
- HTML/URL injection in descriptions or links.
- Oversized input and unexpected Unicode/control characters.

Do not test by executing hostile strings. Pass them to the validator and assert rejection. If a value is allowed as free text, encode it for the output context; YAML escaping, shell quoting and HTML escaping are different problems. Prefer fixed enumerations for owners, tiers and archetypes.

### 14.4 Secrets and dependency supply chain

Never store passwords, API keys, tokens, kubeconfigs or private keys in templates or generated examples. A placeholder password is still dangerous if it can reach a deployment. Use secret references and environment-specific secret delivery as taught in M09. Pin dependencies and CI actions to reviewed immutable references where supported. Scan generated output for secrets, vulnerable dependencies, unsafe workflow permissions and policy violations. Keep provenance linking template revision to generated repository.

### 14.5 Portal privilege boundary

Portal custom actions run in a backend trust domain. No cluster-admin kubeconfig. No broad SCM token. Separate read-only from write integrations. Review proxy endpoints for SSRF and internal network reachability. Exact Backstage permission and token propagation features are `[VERIFY]` for the selected version.

## 15. Composable Add-ons and Ownership Boundaries

### 15.1 Architecture choices

| Pattern | Benefit | Cost/risk |
|---|---|---|
| One monolithic template with many flags | Single entry point | Conditional explosion and hard-to-test combinations |
| Separate template per archetype | Clear contracts | Shared files duplicated |
| Shared base + add-ons | Reuse and optional capability | Add-on compatibility and ordering must be managed |
| Organization base → archetype → team overlay | Layered ownership | Inheritance and debugging complexity |

Avoid template explosion. Start with a small number of supported archetypes and a few independently valuable add-ons.

### 15.2 Add-on contract

Each add-on declares: ID/version, compatible base template versions, prerequisites, parameters, files added/modified, ownership, idempotency policy, tests, rollback/undo guidance and support owner. Reapplying an add-on should either be idempotent or fail with a clear conflict; it must never silently overwrite a team-owned file.

Example add-on manifest:

```json
{
  "addon_id": "queue-consumer",
  "version": "1.0.0",
  "compatible_base": ["1.0.x", "1.1.x"],
  "requires": ["batch-or-api-archetype"],
  "adds": ["src/queue_consumer/", "tests/test_queue_consumer.py"],
  "modifies": [],
  "owner": "platform-engineering",
  "idempotency": "same-input-same-output; refuse-existing-conflicting-files",
  "rollback": "remove only files listed in the manifest after owner review"
}
```

### 15.3 Safe file creation helper

```python
from pathlib import Path


def add_files(repo: Path, files: dict[str, str]) -> list[str]:
    created = []
    for relative, content in files.items():
        target = (repo / relative).resolve()
        root = repo.resolve()
        if root not in target.parents:
            raise ValueError(f"path escapes repository: {relative}")
        if target.exists():
            if target.read_text(encoding="utf-8") == content:
                continue  # idempotent no-op
            raise FileExistsError(f"conflicting existing file: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        created.append(relative)
    return created
```

This helper handles text files only. Binary assets need separate safe copy and checksum logic. The caller should run tests before recording the add-on as applied. For rollback, use the manifest and verify file hashes before deleting anything; never delete a file that has been modified since add-on application.

### 15.4 Platform-managed vs team-owned files

Prefer separate paths and stable file boundaries:

```text
.github/workflows/platform-ci.yml      # platform-managed
platform/policy/                       # platform-managed
platform/template-metadata.json        # platform-managed
src/                                    # team-owned
 tests/                                 # team-owned business tests
config/domain/                          # team-owned
Dockerfile                              # shared; minimize edits and document migration
```

Measure update conflicts before and after restructuring using the same synthetic repositories. Report actual conflict counts from your run only. A sample of five repos cannot establish enterprise-scale effect.

## 16. Data and ML Template Patterns

### 16.1 Batch/ETL

Template guarantees: a documented job interface, configuration schema placeholder, test layout, retry/idempotency guidance, data-quality test location, lineage metadata placeholder, schedule owner and runbook skeleton.

Template only scaffolds: orchestrator integration, storage connectivity, data permissions, schema registry, data contracts, monitoring thresholds and production schedule. The team must validate data classification, replay semantics, duplicate handling, backfill cost and recovery behavior.

### 16.2 Model-serving/inference

Template guarantees: prediction API skeleton, model identity field, expected model digest, readiness contract, resource placeholder, model-card link, SLO/runbook skeleton and rollback instructions.

Template only scaffolds: model loading, accelerator access, autoscaling, latency targets, model quality, feature freshness and registry authorization. The team must verify the model digest against a trusted registry, validate model-card provenance, load test, establish resource requests and prove rollback.

### 16.3 Experiment and notebook workspace

Provide:

```text
experiments/
├── README.md
├── notebooks/                 # exploration; no secrets or sensitive outputs
├── src/                       # reusable experiment code
├── configs/                   # non-secret parameters
├── reports/                   # generated, reviewed artifacts
├── environment/               # lock/environment capture
└── promotion/README.md        # path from experiment to tested pipeline
```

A notebook is not a production pipeline. Move reusable logic into tested modules, capture data/model versions, strip sensitive outputs, and make experiments reproducible. Dataset and feature definitions should link to the organization's data catalog; the software catalog is not a replacement for data lineage or governance.

### 16.4 Guarantees matrix

| Archetype | Template guarantees | Team must validate |
|---|---|---|
| API | package/test skeleton, CI caller, catalog metadata | auth, API contract, SLO, deployment and threat model |
| Batch/ETL | job contract, test/data-quality placeholders, retry guidance | idempotency, data access, lineage, backfill and schedule |
| Model-serving | inference skeleton, model identity/digest fields, readiness contract | trusted model provenance, accelerator, load/quality and rollback |
| Experiment | environment capture and promotion structure | reproducibility, data sensitivity, model governance and promotion criteria |

## 17. Template UX, Metrics, and Operating Cost

### 17.1 UX principles

A good template has a clear name, owner, description, archetype, supported versions, examples, docs, support status and deprecation status. Keep prompts short, defaults safe and validation errors actionable. CLI and portal should resolve to the same approved template release wherever possible. A preview should show the file tree and key parameters before side effects; if the selected engine has no verified dry-run, implement a safe local preview or mark it unavailable.

Design for API developers, data scientists and ML engineers. Notebook-oriented users need clear separation between exploration and production. Accessibility includes keyboard navigation, labels, readable error messages and screen-reader-compatible forms; verify the applicable WCAG target and test it rather than claiming compliance.

### 17.2 Metrics with definitions

| Metric | Numerator / denominator | Window/source | Caveat |
|---|---|---|---|
| Generation success | Successful generations / valid generation attempts | Weekly; CLI/portal task logs | Exclude invalid requests and report them separately |
| Template usage | Repositories by version and archetype | Snapshot; provenance metadata | Metadata may be stale |
| Update adoption lag | Time from release to accepted update | Per release; campaign inventory | Accepted PR is not necessarily deployed |
| Supported-version coverage | Repos within N/N−1 / repos with known template identity | Monthly; inventory | Detached repos need separate state |
| Conformance | Repos passing defined checks / repos scanned | Weekly; CI/conformance scanner | Checks must be meaningful, not vanity |
| Time-to-first-green-CI | Generation start to first passing CI | Per generated repo | Depends on external runners and dependencies |
| Update conflict rate | Updates requiring human conflict resolution / attempted updates | Per campaign | Classify conflict type |
| Bot PR failure rate | Bot PRs failing required checks / bot PRs tested | Per campaign | Not a developer performance measure |
| Template CI duration | Test pipeline wall time and resource use | Per template release | Measure machine and cache conditions |
| Support burden | Template-related support cases by category | Monthly; support system | Avoid interpreting ticket count without context |

Do not rank individual developers. Metrics should guide template improvement. Beware selection bias: teams that use templates may differ from teams that do not. Beware Goodhart's law: if a metric becomes a target, teams may optimize the number rather than the outcome (for example, empty runbooks to pass a scorecard).

### 17.3 Cost

Measure template test CPU/memory/time, generated image build cost where applicable, portal operating cost, engineering maintenance effort and support load. Use M15 labels/quotas in generated defaults. Do not invent prices or ROI. A local laptop measurement is not production capacity guidance.

## 18. Production Operations, Governance, and Incident Scenarios

### 18.1 Operating model

| Responsibility | Platform team | Product/service team |
|---|---|---|
| Template source and releases | Accountable | Contribute through review |
| Platform-managed CI/policy files | Owns contract and update path | Reviews and reports breakage |
| Application code/business tests | Provides supported starting point | Owns after generation |
| Shared files | Defines migration rules | Coordinates local changes |
| Catalog metadata | Defines schema and linter | Supplies correct owner/system details |
| Update PR | Creates campaign and evidence | Reviews, resolves and merges |
| Incident | Restores template platform | Reports generated-project impact |

### 18.2 Release rings and CVE response

1. Fix the template or approved base-image/workflow reference.
2. Run source and generated-output test matrix.
3. Verify provenance/signature using approved M12 process.
4. Publish immutable release and migration notes.
5. Canary a small opt-in set of synthetic or consenting repositories.
6. Open bounded fleet PRs with rate/diff/path limits.
7. Track adoption and failures against a locally defined response target.
8. Confirm deployed consumers through conformance evidence.

Do not invent an industry SLA. Unit 9 owns broader deprecation and support policy. A policy such as supporting N and N−1 must be written as a local rule with owners and dates.

### 18.3 Eight incident scenarios

| Incident | Symptom → likely cause | Investigation | Containment/fix | Prevention/test |
|---|---|---|---|---|
| 1. Unpinned `curl \| sh` hook | Unexpected network command; template executes mutable remote script | Inspect template diff, hook logs, process/network audit, affected generated repos | Disable hook, isolate worker, revoke exposed credentials, pin/review local dependency, rotate secrets if exposure possible | Reject network-fetching hooks; scan source; negative test that unpinned source is refused |
| 2. Update overwrites local changes | Many repos lose edits; update strategy blindly replaces files | Compare pre-update refs/backups, campaign logs, Git diffs and file ownership | Stop campaign, restore from refs/backups, re-run in isolated worktrees, require owner review | Conflict fixture; preserve team-owned paths; PR-only policy |
| 3. Backstage org-admin token risk (tabletop) | Custom action could expose broad SCM credential | Review secret store, action code, logs, token scope and audit events; do not attempt exfiltration | Disable action, revoke token, rotate credentials, inspect affected repos | Least-privilege token, action allow-list, static analysis and tabletop exercise |
| 4. v3 workflow rename duplicates pipelines | Two workflows run for same event | Inspect changed/deleted paths and workflow triggers | Disable duplicate only after owner review; migrate references | Rename migration test; assert exactly one active CI entrypoint |
| 5. New required parameter stalls automation | Update prompts or blocks unattended campaign | Inspect answer file, schema diff and campaign status | Pause affected repos; define owner-approved migration/default; resume in batches | Compatibility test for new questions; non-interactive update fixture |
| 6. Bot floods CI | Sudden PR/queue spike | Inspect campaign concurrency, rate, queue and audit logs | Activate kill switch, stop new PRs, prioritize critical repos | Max batch, delay, concurrency cap, queue-aware throttle, load test |
| 7. Placeholder password ships | Secret-like string appears in generated deployment | Trace template source, rendered output, CI scan and deployment history | Rotate/remove credential, redeploy safely, assess exposure | Secret scan and placeholder-deny test; no default passwords |
| 8. Nunjucks/Jinja2 divergence | Portal and CLI output differs | Compare engine versions, filters, conditionals and normalized file tree | Freeze one source of truth; patch adapter; regenerate only after review | Parity tests across shared fixture matrix; engine-specific syntax isolated |

### 18.4 Governance and scale

Maintain an inventory of templates, owners, languages, archetypes, supported runtimes, consumers and status. Consolidate duplicate templates. Offer support tiers for Python-first data/ML workloads and add JVM/Node/Go only when demand and ownership justify it. Retire unused templates through Unit 9's documented process. Inner-source contributions should use review rules and a lightweight RFC for breaking changes.

A template cannot keep repositories synchronized forever. Drift is natural. The platform should identify it, offer safe updates and make detachment visible rather than pretending all consumers remain compliant.

## 19. Hands-on Labs

All repository names and data in these labs are synthetic. Record your actual OS, tool versions, elapsed time, CPU/RAM/disk use, commands, outputs and cleanup verification. Do not run unreviewed hooks or supply real credentials. The commands below are examples; exact Copier/Cookiecutter flags must be checked against the pinned release before use.

### Lab 1 — Copier templates for three archetypes plus Cookiecutter comparison

**Objective:** Build API, batch/ETL and model-serving templates with validated inputs, derived values and conditional files; build one equivalent Cookiecutter template.

**Prerequisites:** Plat-Core Python, Git; Copier and Cookiecutter installed in an isolated virtual environment only after selecting and recording versions.

**Architecture/tree:** Use the `templates/` tree from Section 4.1. Each archetype has a minimal app, tests, docs, catalog metadata and operational placeholders. Share parameter validation in `scripts/validate_request.py`.

**Steps:**

1. Create a workspace and isolated virtual environment.
2. Record Python, Git, Copier and Cookiecutter versions in `versions.txt`.
3. Verify current official Copier configuration and non-interactive syntax. Adapt `copier.yml` to the pinned schema.
4. Implement API, batch and model-serving subdirectories; add explicit capability conditionals.
5. Run the Plat-Core validator before calling the engine.
6. Generate one project per archetype using pinned template revision and synthetic inputs.
7. Run generated-project tests; inspect tree and metadata.
8. Generate the API from Cookiecutter with equivalent inputs.
9. Change a platform-managed file in the template and update a disposable generated project using documented engine behavior.
10. Record actual merge/conflict results; test Cruft separately if evaluating it.

**Representative command pattern:** `copier copy <PINNED_TEMPLATE_SOURCE> <OUTPUT_DIR>` is a conceptual command; confirm exact syntax and trust/non-interactive flags for the pinned Copier version before execution. Cookiecutter command syntax must likewise be checked with its pinned `--help` and official docs.

**Expected evidence:** three generated trees, one Cookiecutter tree, tool inventory, normalized output comparison, update notes and test reports. Do not invent command output.

**Failure injection:** invalid slug; unknown owner; batch + unsupported database option; model-serving without model digest reference. Each must be rejected or explicitly blocked.

**Cleanup:** remove only the disposable lab workspace after checking its path; keep evidence outside it.

**Security notes:** do not execute unreviewed tasks/hooks; no secrets or real URLs; use immutable template refs.

**Completion criteria:** all three archetypes render coherently; negative inputs fail; Cookiecutter output is comparable; update behavior is documented from actual observation.

### Lab 2 — Template test harness and mutation testing

**Objective:** Prove that the template test suite catches invalid output and deliberate defects.

**Prerequisites:** Lab 1 output; standard-library unittest. Optional lint/build/manifest tools must be pinned and recorded.

**Steps:**

1. Define matrix dimensions: archetype × tier × allowed capabilities.
2. Generate representative combinations and invalid combinations.
3. Run parameter contract tests and generated-project tests.
4. Normalize generated files and compare golden snapshots; exclude timestamps and random identifiers by policy.
5. Generate twice with identical inputs and compare trees.
6. Apply add-on twice and verify idempotency.
7. Remove the CI caller from one disposable generated project; assert the harness fails.
8. Restore it and mutate owner metadata; assert catalog validation fails.
9. If Docker/Podman exists, build an image only after reviewing the Dockerfile; otherwise record `NOT_RUN`.
10. If a cluster is available and resources permit, run Plat+Control smoke test; otherwise use static validation.

**Commands:** From the template workspace, `python -m unittest discover -s tests -v`; optional `docker build`/manifest commands only after verifying installed tool versions and input paths.

**Expected evidence:** matrix file, test report, two normalized tree hashes, mutation failure logs, exact tool inventory.

**Failure injection:** remove a required file or alter a pinned workflow reference; the test harness must fail.

**Cleanup:** delete only disposable generated directories and optional named cluster; verify the original template repository is unchanged.

**Security notes:** never build an unreviewed image; no cluster-admin; no secret fixtures.

**Completion criteria:** normal matrix passes, negative matrix fails for the intended reason, mutation is detected, optional checks are honestly marked.

### Lab 3 — Update propagation to at least five generated repositories

**Objective:** Create five synthetic repositories from v1, introduce differing local edits, release v2 and produce reviewable update artifacts.

**Prerequisites:** Labs 1–2; Git; local filesystem. Local Git server is optional.

**Tree:**

```text
fleet-lab/
├── templates/v1/
├── templates/v2/
├── repos/synthetic-api-01/ ... synthetic-api-05/
├── campaign-output/
└── inventory.json
```

**Steps:**

1. Generate five repos from v1 with the inventory in Section 12.1.
2. Add local changes: app code, shared Dockerfile edit, batch config, custom workflow and missing owner.
3. Create v2 with a changed CI caller, new `service_tier` metadata and migration notes.
4. Snapshot/backup each repository and verify clean Git status before campaign.
5. Run campaign in dry-run mode; inspect each isolated work copy.
6. Integrate a Copier update adapter only after verifying exact pinned command/flags and conflict behavior.
7. Run tests in each work copy; classify clean, conflict, blocked input, validation failure and skipped.
8. Export patch bundles or open PRs on a local server using a least-privilege throwaway token.
9. Resolve one conflict manually and prove local team code remains intact.
10. Record elapsed time and version spread from actual run.

**Commands:** `python tools/update_campaign.py --repos fleet-lab/repos --base fleet-lab/templates/v1-managed --target fleet-lab/templates/v2-managed --out fleet-lab/campaign-output` from the Unit 5 workspace. The script performs a conservative three-way comparison of platform-managed files: it updates files unchanged from the old baseline, preserves locally modified files as conflicts, emits patch files and a JSON report, and never merges or pushes. It is an update-campaign fallback, not a Copier merge implementation or remote PR client.

**Expected evidence:** five status records, patch/work directories, report JSON, owner assignments, conflict-resolution diff and test logs.

**Failure injection:** one dirty worktree, one missing owner, one conflicting workflow rename, one failing test. Each must be reported and must not be merged.

**Cleanup:** retain report and patch evidence; remove only disposable work copies after confirming source repos remain unchanged.

**Security notes:** PR-only, no automatic merge, no broad credentials, rate limit and kill switch.

**Completion criteria:** five repositories processed or explicitly blocked; every outcome classified; local edits preserved; no automatic merge.

### Lab 4 — Template supply-chain and injection drill

**Objective:** Refuse floating/unverified template sources, detect template modification and reject hostile parameters.

**Prerequisites:** Plat-Core Python; local throwaway template directory; no network required.

**Steps:**

1. Create a disposable template directory with a few text files.
2. Compute a SHA-256 tree hash using `verify_template.py` and create a manifest with a fixed synthetic revision.
3. Verify the unchanged template.
4. Change one file and verify that the wrapper rejects it.
5. Change revision type to `branch` or revision to `main`; verify refusal.
6. Run the parameter validator with path traversal, shell metacharacters, YAML-breaking input and unknown fields.
7. Scan template and generated output for secret-like placeholders; confirm no credentials exist.
8. Document that a locally stored hash is integrity-only, not publisher authentication.
9. If signing keys are used, create throwaway keys in an isolated directory and use the approved M12 signing procedure only after checking the exact command. Do not invent a signing CLI.

**Expected evidence:** original hash, tampered hash, rejection output, negative-input test report and secret-scan report.

**Failure injection:** modify template after manifest creation; verification must fail.

**Cleanup:** securely remove throwaway private keys and temp directories; do not delete unrelated keys.

**Security notes:** never paste secrets into prompts or commit them; never execute the malicious hook example.

**Completion criteria:** unpinned/unverified source refused; tampering detected; hostile values rejected; signing limitation documented.

### Lab 5 — Add-on composition

**Objective:** Implement a database or queue-consumer add-on with explicit compatibility, idempotency and conflict behavior.

**Prerequisites:** one generated API or batch repository; helper in Section 15.3.

**Steps:**

1. Create add-on manifest using Section 15.2.
2. Add a small queue-consumer module and unit test as synthetic content.
3. Apply add-on using `add_files` helper.
4. Apply it a second time and verify no duplicate or changed file appears.
5. Modify an add-on-owned file manually and reapply; helper must raise a conflict rather than overwrite.
6. Test incompatible base version and missing prerequisite.
7. Document rollback and verify file hashes before any removal.

**Expected evidence:** add-on manifest, first/second apply reports, conflict log, tests and rollback notes.

**Failure injection:** pre-create a conflicting file and attempt application.

**Cleanup:** use disposable repository; no destructive cleanup on personal projects.

**Security notes:** validate all paths after resolution; do not permit `../` traversal.

**Completion criteria:** idempotent no-op on second identical apply; conflict is explicit; rollback is owner-reviewed.

### Lab 6 — Platform-managed versus team-owned file separation

**Objective:** Reduce co-editing conflicts by separating platform configuration from business code.

**Prerequisites:** synthetic repository from Lab 3.

**Steps:**

1. Create a v1 repository where CI, policy and application logic are mixed in a shared file layout.
2. Add local team modifications to shared files.
3. Run the v1→v2 update in an isolated copy and record conflict count/types.
4. Restructure template so CI caller, policy baseline and template metadata are isolated under platform-owned paths.
5. Keep application logic and business tests under team-owned paths.
6. Repeat the same update with equivalent local changes.
7. Compare observed conflicts and explain sample-size limitations.

**Expected evidence:** before/after trees, diffs, conflict log and ownership matrix.

**Failure injection:** change a platform-managed file locally; confirm campaign flags it for owner review.

**Cleanup:** keep evidence; discard only disposable copies.

**Security notes:** path ownership is a governance boundary, not a substitute for repository permissions.

**Completion criteria:** ownership is explicit; measured before/after observations are recorded without generalizing beyond the synthetic sample.

### Lab 7 — Update-bot safety

**Objective:** Test path allow-list, diff-size, rate/concurrency, missing-owner, audit and kill-switch controls.

**Prerequisites:** campaign script and synthetic repositories.

**Steps:**

1. Apply `allowed_path` to every changed path in the adapter.
2. Add a maximum changed-file and changed-line threshold.
3. Enforce maximum repositories per run and a delay/concurrency cap.
4. Require owner lookup from inventory; missing owner blocks the repo.
5. Ensure campaign creates patches/PRs only and never merges.
6. Write an audit report for each repository.
7. Set `TEMPLATE_CAMPAIGN_KILL_SWITCH=1` and verify the run stops.
8. Attempt forbidden path, excessive diff, excessive repo count and missing owner.

**Expected evidence:** four negative test logs, audit report, kill-switch record and bot permission review.

**Failure injection:** add a change under `src/` and exceed the configured diff limit.

**Cleanup:** revoke any throwaway token; remove disposable campaign output only after saving evidence.

**Security notes:** no organization-admin credentials; protect branches; require human review.

**Completion criteria:** all negative tests block; no automatic merge; kill switch works; audit record is complete.

### Lab 8 — Optional Backstage Scaffolder

<badge color="secondary">Optional</badge>

**Objective:** Expose the approved template through a portal form and safely produce local output or a repository.

**Prerequisites:** Plat+Portal preflight; Node/package-manager versions verified from official Backstage docs; enough measured RAM/disk. Skip if constrained.

**Steps:**

1. Record OS, CPU, RAM, disk and current toolchain.
2. Follow the official create-app guide for a pinned Backstage release; record exact package versions.
3. Configure lab-only guest auth only if the pinned release documents it.
4. Define a parameter form for project name, owner and tier.
5. Implement or install a verified action that calls the pinned Copier source in an isolated worker; otherwise use local file output.
6. Register the generated `catalog-info.yaml` only through an approved catalog location.
7. Review action allow-list, SCM token scope, secrets handling and audit logs.
8. Test unauthorized action and repository targets.
9. Measure install/build/idle footprint and upgrade work on your machine.
10. Stop Backstage and confirm local generated repositories and runbooks remain accessible independently.

**Expected evidence:** version inventory, preflight, action review, generated output, catalog entity and measured footprint.

**Failure injection:** deny an unauthorized target or action; verify no repository is published.

**Cleanup:** stop app, remove only named lab database/container and revoke throwaway token.

**Security notes:** no static tokens in config; no cluster-admin; no real user credentials.

**Completion criteria:** optional app works for the pinned release or is skipped with evidence; Plat-Core remains complete without it.

### Lab 9 — Template UX measurement

**Objective:** Compare manual baseline with generated output using a fixed synthetic task list.

**Prerequisites:** one API template and a manual baseline procedure.

**Steps:**

1. Define tasks: create package, add test, add CI caller, add Dockerfile placeholder, add catalog metadata, docs and runbook skeleton.
2. Run manual baseline once and record elapsed time and mistakes/omissions.
3. Generate from template and record elapsed time and prompt count.
4. Run CI-equivalent checks and record time-to-first-green-check.
5. Evaluate preview usefulness and validation error clarity using a short rubric.
6. Report sample size, environment, dependencies/cache and limitations.

**Expected evidence:** task sheet, raw timings, prompt count, CI output and short usability notes.

**Failure injection:** enter invalid project name; record whether error explains correction.

**Cleanup:** remove only disposable generated project.

**Security notes:** use synthetic values and no private repositories.

**Completion criteria:** measurements are reproducible and clearly labelled n=1/synthetic; no claims about real developer populations.

### Lab 10 — Tool-selection ADR

**Objective:** Make a defensible tool decision for the roadmap context.

**Prerequisites:** evidence from Labs 1–9 and official docs for selected versions.

**ADR template and sample decision:**

```markdown
# ADR-005: Local-first template engine

- Status: Proposed
- Context: M16 requires three archetypes, safe updates, five-repository campaigns and optional portal UX.
- Decision: Use Copier as the Plat-Core candidate; retain Cookiecutter as a comparison; keep Backstage optional.
- Evidence: Attach actual generation/update/test observations from Labs 1–3.
- Consequences: One primary engine reduces dual-template drift; Copier version and update semantics require verification; portal integration needs a reviewed adapter.
- Revisit when: official tool support changes, update conflicts remain excessive, or portal workflows justify a different architecture.
```

The decision above is an illustrative starting point, not a measured conclusion. Replace it with your lab evidence.

**Steps:** score Copier, Cookiecutter+Cruft and Backstage-native on update support, ecosystem, tests, portal integration, security, portability and operations. Cite official documentation and note unknowns. Include measured local effort, not vendor popularity.

**Failure injection:** remove evidence for one criterion; mark it unknown rather than inventing a score.

**Cleanup:** none beyond temporary notes.

**Security notes:** ADR must state credential and execution boundaries.

**Completion criteria:** decision includes context, alternatives, evidence, risks, consequences and revisit triggers.

## 20. Troubleshooting Guide

| Symptom | Probable cause | Diagnosis | Safe fix | Regression test |
|---|---|---|---|---|
| Variables render literally | Wrong delimiter/engine or variable undefined | Inspect engine docs and generated file | Correct syntax for pinned engine | Snapshot asserts rendered value |
| File/directory name wrong | Path templating disabled or wrong directory nesting | Inspect template tree and engine logs | Use verified path-rendering convention | Assert exact output path |
| Invalid names pass | Validation absent or runs after hook | Run hostile input corpus | Validate before rendering/tasks | Negative slug test |
| Conditional files wrong | Boolean/string mismatch or condition syntax mismatch | Print validated parameter object | Normalize booleans and test condition | Matrix for true/false |
| Non-interactive run hangs | Missing answer/default or wrong flags | Run help/docs for pinned version | Provide complete data input with verified syntax | CI timeout test |
| Output differs on repeat | Timestamp, random ID, unordered iteration | Compare normalized tree hashes | Remove nondeterminism or isolate provenance | Generate twice and compare |
| Template tests pass but CI fails | Template tests do not exercise generated project | Run consumer CI and inspect missing deps/secrets | Add generated-output CI-equivalent gate | End-to-end generated fixture |
| Update conflicts with local edits | Shared file ownership unclear | Inspect base/local/template diff | Preserve local intent and resolve manually | Conflict fixture |
| New required question blocks bot | Schema change not migration-compatible | Inspect answer file and release diff | Add safe migration or owner input gate | Non-interactive v1→v2 test |
| Repo drifts from template | No update inventory or local modifications | Compare recorded version and conformance | Open reviewable update; mark detached if necessary | Drift scanner fixture |
| Hash/signature fails | Modified file, wrong manifest or untrusted provenance | Recompute tree hash and inspect manifest origin | Reject; obtain trusted release | Tamper test |
| Hook attempts network/command | Unreviewed task or dependency | Inspect hook source and process logs | Stop execution; isolate; remove task | Static policy forbids unapproved hook |
| Portal action missing | Action package not installed or ID mismatch | Check pinned package docs and backend logs | Install verified action or local file fallback | Schema/action integration test |
| Portal/CLI outputs differ | Nunjucks/Jinja2 divergence | Compare normalized tree outputs | Single source of truth or parity test | Shared fixture parity test |
| Bot exceeds diff/rate | Missing guardrail or inventory too large | Inspect report and queue metrics | Activate kill switch; batch smaller | Limit negative tests |
| Catalog owner invalid | Group ref missing or wrong namespace | Run Unit 4 catalog linter | Correct owner to registered group | Unknown-owner fixture |
| Local Git server unavailable | Server stopped or network unreachable | Check local service and port | Use local Git and patch bundle | No-server fallback test |
| Backstage/kind exceeds budget | Insufficient RAM/disk or build contention | Recheck preflight and process footprint | Stop optional stack; finish Plat-Core | Core suite passes with optional tools absent |

For every incident, preserve the original repository, capture command output, record tool versions and add a regression test. Do not run broad cleanup commands such as deleting all containers or all local Git repositories.

## 21. Review Questions and Exercises

### 21.1 Questions

1. Define scaffolding and explain how it relates to a golden path.
2. Why is a generated repository not automatically kept up to date?
3. Give two risks of manual copy-paste that a template can reduce.
4. What is the difference between template source and generated repository?
5. Why should a template ask for fewer parameters and derive the rest?
6. Why must validation run before hooks or tasks?
7. Explain the difference between Cookiecutter, Copier and Cruft without attributing one tool's behavior to another.
8. What does `.copier-answers.yml` contribute to an update workflow? Verify exact behavior for the selected release.
9. Why is a template release tag not necessarily immutable?
10. Classify a required new parameter as a compatibility risk and propose a migration.
11. A team changed a shared Dockerfile locally. How should an update campaign handle it?
12. Why are platform-managed and team-owned files best separated?
13. How would you test that an add-on is idempotent?
14. Explain why a local SHA-256 manifest does not by itself authenticate a publisher.
15. A hook downloads and executes an unpinned script. What is the containment and prevention plan?
16. A user enters `../../outside` as a project name. Which validation boundary should reject it and why?
17. A Backstage custom action has an organization-admin token. Explain the blast radius and the first three containment steps.
18. Why can Nunjucks and Jinja2 generate different output from apparently similar templates?
19. An update bot opens too many PRs and saturates CI. Which controls should have prevented it?
20. How should update adoption lag be measured without ranking developers?
21. What should a model-serving template guarantee, and what must the service team validate?
22. When should a project remain a one-off rather than become a supported template?

### 21.2 Model answers

1. Scaffolding renders a project from validated parameters; it operationalizes the golden path but does not replace CI, infrastructure APIs or operations.
2. Generation is a one-time rendering event. Ongoing maintenance needs version provenance, update mechanism, conflict resolution and owner review.
3. Copy-paste can preserve stale security defaults and omit ownership/operational metadata.
4. Template source is maintained by the platform; generated repository is a consumer with team-owned changes.
5. Duplicate prompts create inconsistency. Derivation keeps repository, image, namespace and catalog identifiers aligned.
6. Hooks/tasks can execute arbitrary code; invalid or hostile input must be rejected before execution.
7. Cookiecutter is a Jinja2-oriented generator; Copier offers a generation/update workflow; Cruft adds update-oriented behavior around Cookiecutter. Verify pinned versions and don't overstate native capabilities.
8. It records answers/provenance used by Copier; exact fields and update semantics are release-specific and must be verified.
9. Git tags can be moved unless repository policy prevents mutation. Record the resolved commit SHA and verify provenance.
10. A new required input can block unattended updates. Provide a deterministic safe migration only if semantically valid; otherwise mark repo blocked for owner input.
11. Isolate update, inspect diff, preserve local intent and require human conflict resolution; never overwrite blindly.
12. Separate files reduce co-editing and make ownership and update permissions clearer.
13. Apply twice to the same fixture and compare tree hashes; second run should be a no-op or explicit conflict.
14. An attacker can replace both artifact and adjacent manifest. Trust in the digest must come from a separate authenticated channel.
15. Stop execution, isolate worker, revoke exposed credentials if needed, inspect affected output, remove untrusted hook and add policy/negative test.
16. The pre-generation schema validator should reject it before rendering or tasks; path resolution checks are a second boundary.
17. Disable the action, revoke/rotate token, inspect audit logs and affected repositories; then narrow scope and review action code.
18. They are different template languages with different filters, escaping and undefined-value behavior; use one source or parity tests.
19. Batch size, rate/concurrency limits, kill switch, PR-only workflow and queue-aware throttling.
20. Measure release-to-accepted-update time across repositories by version and owner, with a defined window; report aggregate and blockers.
21. Guarantee a code skeleton, digest field, readiness contract and operational placeholders; team validates trusted model provenance, load, quality, resources and rollback.
22. When requirements are unique/unstable, usage is one-off, or no team can maintain the template and update contract.

### 21.3 Hands-on exercises

1. **Parameter contract:** add an allowed owner and test invalid slug/owner; acceptance: all invalid inputs fail before any task.
2. **Archetype:** generate one batch and one model-serving project; acceptance: each has correct contract and no real model/data dependency.
3. **Mutation:** remove CI caller; acceptance: template harness fails with an actionable message.
4. **Update conflict:** edit a team-owned file, update template; acceptance: team edit is preserved and conflict is surfaced for shared file.
5. **Bot guardrail:** attempt forbidden path and exceed repo limit; acceptance: both are blocked and audited.
6. **Security:** modify template after hash creation; acceptance: verifier rejects and does not execute tasks.
7. **ADR:** compare tools using official docs and lab evidence; acceptance: decision includes unknowns and revisit triggers.

## 22. Glossary

- **Add-on:** independently versioned capability applied to a generated repository.
- **Archetype:** supported project category such as API, batch or model-serving.
- **Canonical parameter:** single source value from which related names/labels are derived.
- **Compatibility contract:** documented promise about supported inputs, outputs and updates.
- **Conformance:** evidence that a repository meets defined platform checks.
- **Drift:** divergence between a repository and its intended supported baseline.
- **Generated repository:** consumer project rendered from a template.
- **Golden path:** supported, tested route to build/run a workload.
- **Immutable revision:** template identity that cannot silently change, typically a resolved commit SHA plus trusted provenance.
- **Migration:** explicit transformation needed to move a generated repository between template contracts.
- **Mutation test:** deliberate defect introduced to prove a test catches it.
- **Post-generation task:** code executed after rendering; it has the generator's privileges.
- **Scaffolding:** parameterized generation of a project/repository.
- **Template engine:** software that renders a template using parameters.
- **Template source:** maintained template repository and release history.
- **Update campaign:** controlled fleet process that proposes template changes to consumer repositories.
- **Platform-managed file:** generated configuration whose contract is owned by the platform team.
- **Team-owned file:** application/domain content maintained by the consuming team.

## 23. Completion Gate and Self-Audit

### 23.1 Learner completion checklist

- [ ] I can explain generation versus update and identify the owners of both.
- [ ] I built API, batch and model-serving templates with validated parameters.
- [ ] I built an equivalent Cookiecutter template and recorded actual update behavior.
- [ ] I tested valid/invalid combinations, deterministic output and a deliberate mutation.
- [ ] I generated platform-managed and team-owned files with clear boundaries.
- [ ] I updated five synthetic repositories through isolated, reviewable artifacts.
- [ ] I resolved at least one conflict while preserving local team code.
- [ ] I verified a template hash/provenance and rejected a modified/unpinned source.
- [ ] I tested injection values without executing them.
- [ ] I applied an add-on twice and tested conflict behavior.
- [ ] I tested bot path, diff, rate, owner and kill-switch controls.
- [ ] I completed an ADR based on verified documentation and actual lab evidence.
- [ ] I completed Backstage only if optional preflight passed; otherwise I recorded why it was skipped.
- [ ] I saved command outputs, tool inventory, test reports, diffs, update report and cleanup verification.

### 23.2 Coverage matrix

| Requirement group | Lesson sections |
|---|---|
| L1: scaffolding, copy-paste, tools, anatomy, first Copier template | 1–6 |
| L2: parameter design, generated content, tasks, tests, versions, updates | 4–12 |
| L3: security, add-ons, ownership, Backstage, data/ML, metrics | 13–17 |
| L4: operations, releases, bot safety, governance, incidents | 12, 18 |
| Lab 1: three archetypes + Cookiecutter | 5, 6, 19.1 |
| Lab 2: harness + mutation | 9, 19.2 |
| Lab 3: five-repo campaign | 11, 12, 19.3 |
| Lab 4: supply chain + injection | 14, 19.4 |
| Lab 5: add-ons | 15, 19.5 |
| Lab 6: ownership separation | 4.8, 15.4, 19.6 |
| Lab 7: bot safety | 12.3, 19.7 |
| Lab 8: optional Backstage | 13, 19.8 |
| Lab 9: UX measurement | 17, 19.9 |
| Lab 10: tool-selection ADR | 3, 6, 19.10 |

### 23.3 Version-sensitive verification register

| Item | Authoritative source to check | Exact verification action | Status in this lesson |
|---|---|---|---|
| Copier question schema and validators | Official Copier docs for pinned release | Validate `copier.yml` with real copy; inspect schema and `--help` | OPEN — learner must pin and verify |
| Copier update merge and conflict behavior | Official Copier update docs | Generate v1, local edit, update to v2; inspect exact artifacts | OPEN |
| Copier task/migration/trust flags | Official Copier docs | Verify trust semantics and run reviewed fixture in isolation | OPEN |
| Cookiecutter hooks/update behavior | Official Cookiecutter docs | Inspect hook lifecycle and test pinned version; separate Cruft | OPEN |
| Cruft update semantics | Official Cruft docs | Pin and execute v1→v2 comparison | OPEN |
| Backstage API/action IDs | Official Backstage Scaffolder docs and installed action packages | Validate template against pinned release; verify each action exists | OPEN |
| Backstage identity/permission behavior | Official Backstage auth/permission docs | Test user/action authorization in isolated instance | OPEN |
| Git provider reusable workflow syntax | Provider's official CI docs | Validate workflow against provider and pinned reusable workflow | OPEN |
| Binary assets and exclusion markers | Official engine docs | Test binary and skip/exclude fixtures | OPEN |
| Signing/provenance CLI | Organization-approved M12 process | Verify exact command and trust root; test tamper rejection | OPEN |
| Notebook stripping integration | Official tool docs | Pin hook and test notebook output | OPEN |
| `kind`/manifest validation commands | Official tool docs | Record exact versions and run disposable cluster smoke test | OPEN |

### 23.4 Human verification checklist

- [ ] Confirm all CLI commands against installed pinned tool versions before execution.
- [ ] Review Copier and Cookiecutter templates and every hook/task before running.
- [ ] Verify all generated files, names, catalog owner references and conditional capabilities.
- [ ] Run parameter, generated-project, mutation and update tests.
- [ ] Inspect every update diff; confirm no local code was overwritten.
- [ ] Verify hash/signature from a trusted source before task execution.
- [ ] Scan source and generated output for secrets, unsafe workflow permissions and insecure placeholders.
- [ ] Review bot token scope, branch protection, path/diff/rate limits, audit and kill switch.
- [ ] Review Backstage action allow-list and credentials if optional lab is attempted.
- [ ] Verify cleanup only affected named disposable resources.
- [ ] Record optional tests as `NOT_RUN` if tools were unavailable.

### 23.5 Author self-audit

| Audit item | Status | Evidence / limitation |
|---|---|---|
| Uploaded Unit 5 prompt reviewed | PASS | Prompt sections 1–20 inspected |
| Authoritative M16 Unit 5 syllabus reviewed | PASS | Unit 5 L1–L4 and mandatory labs located in syllabus |
| Roadmap M16 tree reviewed | PASS | Target path and neighboring unit names confirmed |
| Units 1–4 reviewed as context | PASS | Prior generated lesson files located and inspected |
| Verbatim handoff included | PASS | Included near document beginning |
| Scope boundaries preserved | PASS | Units 2, 4, 5, 6–9 and M01–M15 boundaries stated |
| All ten labs included | PASS | Sections 19.1–19.10 |
| Eight incident scenarios included | PASS | Section 18.3 |
| At least 15 review questions and model answers | PASS | 22 questions with answers |
| Zero-budget Plat-Core path | PASS | Standard-library helper examples; optional tools separated |
| Copier/Cookiecutter/Backstage claims verified live | OPEN | Version-sensitive details explicitly marked; official release verification remains learner task |
| Copier/Cookiecutter engine commands executed | OPEN | Not claimed as executed in this document |
| Backstage or kind executed | OPEN | Optional; not claimed as executed |
| Template package test suite executed | OPEN | Code is provided for learner execution; no test pass is claimed here |
| Signature verification performed | OPEN | Local hash wrapper is a teaching implementation; no publisher signature verified |
| No other repository files modified | PASS | This deliverable is a standalone lesson file |

### 23.6 What is and is not verified

This lesson provides complete representative file examples, a dependency-free parameter validator, a local campaign skeleton, an integrity-check wrapper, an add-on file helper, test examples, and detailed lab procedures. These are teaching artifacts. The exact Copier/Cookiecutter/Backstage CLI and schema behavior is intentionally not asserted without a pinned toolchain and live official-document verification. No cloud resources, remote SCM, Backstage instance, `kind` cluster, or signing service is claimed to have been run. Learner execution is required to produce actual test reports, timings and machine-footprint evidence.

### 23.7 Cross-unit links

Use these exact M16 sibling filenames when the repository is laid out as confirmed by the roadmap:

- [Unit 2 — Golden paths, templates, and paved roads](02-golden-paths-templates-and-paved-roads.md)
- [Unit 4 — Developer portals and Backstage service catalog](04-developer-portals-and-backstage-service-catalog.md)
- [Unit 6 — Platform APIs with Crossplane compositions](06-platform-apis-with-crossplane-compositions.md)
- [Unit 7 — Multi-tenancy, isolation, and tenant onboarding](07-multi-tenancy-isolation-and-tenant-onboarding.md)
- [Unit 8 — Platform SLOs, adoption metrics, and developer experience](08-platform-slos-adoption-metrics-and-developer-experience.md)
- [Unit 9 — Platform governance, deprecation, and versioning](09-platform-governance-deprecation-and-versioning.md)

M01/M02/M06/M08/M09/M10/M11/M12/M13/M15 provide the underlying mechanisms; refer to their modules rather than inventing relative paths not verified in the supplied M16 tree.

**Unit completion standard:** the learner can generate, test, version, update and safely operate a small template system; can explain the remaining human review and production integration boundaries; and can show evidence rather than relying on generated boilerplate as proof of readiness.
