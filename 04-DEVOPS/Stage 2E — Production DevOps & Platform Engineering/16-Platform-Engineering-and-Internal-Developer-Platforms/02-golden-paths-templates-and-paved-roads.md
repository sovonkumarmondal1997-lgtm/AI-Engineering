# Golden paths, templates, and paved roads

This unit turns the platform principles from Unit 1 into concrete, reusable developer paths. You will design a small family of supported repository skeletons, integrate M01–M15 standards, validate generated repositories with local checks, measure conformance, and define safe ways to vary or leave the default. The core labs run locally with Python's standard library and files only; passing them proves repository-level checks, not a live deployment or production readiness.

## Unit 2 — Golden paths, templates, and paved roads

**Target file:** 02-golden-paths-templates-and-paved-roads.md | **Estimated time:** 24–32 hours | **Prerequisites:** Unit 1; M01–M15  
**Core tools:** WSL2 Ubuntu/native Linux, Python standard library, local files, Git optional, Markdown, JSON, YAML as text | **Awareness:** hadolint, kubeconform, Helm, Kustomize, kind, GitOps controllers, Backstage, template engines, policy engines, update bots | **Last reviewed:** 2026-11-03 | **Tool baseline assumed:** Python 3.10+ syntax; verify with `python3 --version`; all external tool versions and exact integrations are [VERIFY] | **Stack profile required:** Plat-Core | **Footprint:** local files and Python scripts; disk/CPU/RAM depend on learner's files and interpreter—measure yours | **Synthetic users/data:** yes

### 2.0 Why this matters in production

A copied template can carry a weak security setting, stale dependency, or missing operational evidence into every service created from it. A path that is too rigid can become a golden cage, encouraging teams to fork repositories or bypass controls rather than use the supported route. A template is only one artifact: a production-oriented golden path also needs validation, documentation, ownership, support, upgrade discipline, and feedback. This unit integrates the controls from earlier modules into repeatable developer workflows without pretending that local static checks prove runtime behavior.

> M01–M15 each taught mechanisms and standards: hardened images, reusable CI, manifest and policy standards, GitOps, secret references, SLO and alert templates, instrumentation, supply-chain controls, backup defaults, and cost labels and quotas. This unit does not re-teach them. It teaches how to **integrate those defaults into a golden path** — a documented, supported, tested, upgradable way to build and run a service — including the golden-path template repository (a Core tool), validation checks that keep the path safe, escape hatches, support boundaries, and conformance measurement.

### 2.1 Learning objectives

- **[L1]** Define a golden path, paved road, and golden cage, and distinguish a path from a template.
- **[L1]** Assemble an API/inference repository skeleton and trace each artifact to its platform or product-team owner.
- **[L2]** Design distinct API, batch, streaming, model-serving, and notebook paths with shared and archetype-specific contracts.
- **[L2]** Implement at least 15 deterministic repository checks with actionable diagnostics, warning/block modes, and negative tests.
- **[L2]** Generate per-service conformance reports that reject lookalike files and distinguish supported, drifted, and off-path repositories.
- **[L3]** Defend at least five platform defaults using ADRs and a default → reason → test → owner register.
- **[L3]** Design version compatibility, canary rollout, security-patch propagation, and parameter/fork/add-on strategies.
- **[L4]** Diagnose shared-template failures and define ownership, lifecycle, fleet rollout, evidence, and safe migration practices.

### 2.2 Concept map and vocabulary

#### Golden path and paved road

A **golden path** is the supported, easiest-to-follow way to complete a common developer task with built-in best practices. It normally spans repository creation, validation, delivery, deployment integration, observability, and operation. A **paved road** is the metaphor for a route that is maintained, documented, and convenient to use; in this course, “golden path” and “paved road” refer to the same supported developer journey, while “template” means one input artifact that helps start that journey.

A golden path is not automatically a mandate. A **golden cage** blocks legitimate alternatives, provides no useful escape hatch, and ignores feedback. A good path earns adoption because it removes repeated work and makes safe behavior easier. Historical attribution of golden-path practices to Spotify or Netflix is **[VERIFY]**: consult primary company engineering publications before making an origin claim; this lesson makes no claim about who coined the term.

A good path has:
- **Opinionated defaults** tied to a risk or user need, not personal preference.
- **End-to-end coverage**, from new repository to safe deployment and operation.
- **Understandable documentation**, including why defaults exist and how to debug them.
- **Named ownership**, support level, escalation route, and update policy.
- **Automation** for repeatable work, with useful and timely feedback.
- **Security, reliability, observability, and cost awareness** by default.
- **Supported variation and an escape hatch** with mandatory controls preserved.
- **Versioning, tests, compatibility evidence, and continuous evolution.**

A template alone is not an end-to-end golden path. It can generate files, but it cannot by itself guarantee CI succeeds, deployment is authorized, telemetry arrives, the service has an owner, or an incident can be handled.

#### Vocabulary

| Term | Precise definition | Common misconception |
|---|---|---|
| Golden path / paved road | Maintained, supported route for a common developer task with tested defaults. | A mandatory template or a portal page. |
| Template repository | Source files from which a starting repository is copied or generated. | A complete operating platform. |
| Archetype | A path shaped around a workload lifecycle, such as batch or inference. | A language choice alone. |
| Default | The recommended, supported configuration used when no variation is requested. | A universal value that fits every workload. |
| Supported option | A documented parameter or add-on tested by the platform team. | Any change a user can make. |
| Escape hatch | Governed alternative path with explicit support boundaries and mandatory guardrails. | Permission to bypass security or compliance. |
| Conformance | Evidence that a service meets a defined set of path/version/artifact/policy requirements. | Presence of template-like filenames. |
| Drift | Difference between a generated/current baseline and a service's current state, classified by reason. | Automatically a defect; some drift is justified. |
| Template provenance | Traceable information about template source/version and how generated output was produced. | Proof that generated code is safe by itself. |
| Time-to-propagate | Elapsed time from an approved shared fix to verified adoption across the defined eligible repository set. | A target that can be invented without operational data. |
| ORR | Operational Readiness Review: evidence that a service is prepared for operation. | A checklist that proves reliability. |
| Canary repository | A small, selected repository used to validate a path change before broad rollout. | A production safety guarantee. |

#### Ownership and flow

```text
Developer / team
    |
    +--> default path --------+
    +--> supported option ---+--> template / local copy
    +--> approved escape ----+          |
                                       v
                           CI-equivalent local validation
                           structure + policy + docs + tests
                                       |
                     mandatory guardrails remain in every path
                                       |
                         GitOps / deployment integration
                         [optional Plat+Control; not Core]
                                       |
                           runtime + telemetry + operation
                                       |
                         feedback, drift, support, upgrades
                                       |
              +------------------------+----------------------+
              |                                               |
       Platform team                                   Product team
 owns templates, policies,                         owns application logic,
 shared workflows, docs,                            data/model correctness,
 releases, support boundary                         product SLO and service
 and platform reliability                           operation within contract
```

The platform team owns the generated defaults and shared workflow contracts. Product teams own their application code, domain correctness, workload-specific decisions, and product service outcomes. Some areas are shared: onboarding, readiness, incident boundaries, metadata, and upgrade planning. CI and admission enforcement should express consistent mandatory policy, but local checks are not a substitute for admission enforcement.

#### Path lifecycle

```text
Proposal/RFC -> design partner pilot -> GA -> maintain and patch
      ^                                  |             |
      |                                  v             v
  feedback <------------------------ evolve       deprecate
                                                     |
                                              migrate / retire
```

#### Repository contract

The course uses these illustrative required labels: `team`, `service`, `env`, `cost-center`, and `tier`. Exact label names, allowed values, metadata schema, and enforcement must match the actual M03/M15 repository standards **[VERIFY]**. Branch/PR rules and CODEOWNERS connect to M02 and M08. The examples below use simple files and Python checks; they do not claim universal Kubernetes, CI-provider, or catalog schema validity.

#### Cross-module integration map

| Earlier module | Golden-path integration | Verification evidence |
|---|---|---|
| M01 | Multi-stage/non-root image, approved digest-pinned base, lockfiles/hashes, reproducible environment. | Dockerfile and dependency checks; image build belongs to M01. |
| M02 | Reusable CI workflow, least privilege, branch/PR rules, CODEOWNERS, fast feedback. | CI config review and local policy checks. |
| M03 | Manifest standards, probes, resources, PDB, Pod Security Standards. | Rendered manifest validation and negative fixtures. |
| M04 | Default-deny NetworkPolicy and TLS. | Required networking declaration and cluster tests in the owning module. |
| M05 | Operator-managed databases and backup considerations for stateful services. | Optional database add-on and declared backup need. |
| M06 | Helm library chart and Kustomize components. | Reference/version and render checks. |
| M07 | IaC modules and guardrails; build/adopt/buy (Unit 9); Crossplane concepts (Unit 12). | Link to approved module and ownership. |
| M08 | GitOps, promotion, digest rollout, rings, flags, data-contract/schema checks (Unit 12). | Deployment definition and promotion evidence. |
| M09 | Secret references and workload identity. | No credential values; identity reference only. |
| M10 | SLO, alert packs, runbooks, ORR, on-call, postmortems. | Required SLO/runbook artifacts and readiness evidence. |
| M11 | Instrumentation, dashboards-as-code, telemetry standards, catalog ownership/dependencies. | Files present plus separate telemetry integration evidence. |
| M12 | Signing, SBOM/provenance, admission bundles, supply-chain defaults. | CI evidence references and policy expectations. |
| M13 | Backup/restore, DR tiers, idempotency/checkpointing, model artifact integrity. | Stateful backup declaration; batch checkpoint hooks; model hash. |
| M14 | Fleet/cluster operations, rollout rings, multi-cluster/region. | Target ring/region is explicit; no multi-cluster lab required. |
| M15 | Cost labels, quotas, priority classes, HPA/KEDA, capacity gates, idle-culling, showback. | Required cost metadata and optional workload-specific settings. |

This unit packages and integrates these mechanisms into a supported developer path; it does not replace or re-teach the earlier modules.

**M16 taught/deferred boundary:** taught here are path design, integrated service skeletons, default/option/escape policy, repository and rendered-output checks, conformance, versioning concepts, defaults, feedback, and failure analysis. Actual provisioning is [Unit 3](03-self-service-infrastructure-and-environment-provisioning.md); portal/catalog implementation is [Unit 4](04-developer-portals-and-backstage-service-catalog.md); production scaffolding engines and template update mechanisms are [Unit 5](05-scaffolding-and-software-templates.md); Crossplane APIs are [Unit 6](06-platform-apis-with-crossplane-compositions.md); full SLO/adoption/DX measurement is [Unit 8](08-platform-slos-adoption-metrics-and-developer-experience.md); detailed governance, deprecation, and compatibility policy is [Unit 9](09-platform-governance-deprecation-and-versioning.md). Principles are in [Unit 1](01-platform-engineering-principles-and-platform-as-a-product.md). The supplied Roadmap confirms the M17 project file [End-to-end Production DevOps Capstone](../17-Production-DevOps-Integrated-Capstone/Projects/04-end-to-end-production-devops-capstone.md); this unit prepares the golden-path contracts that the integrated capstone can consume.

### 2.3 Level 1 — Beginner

#### Start from the developer task

Suppose a developer needs a small HTTP inference API. They need application code and tests, an approved image, a CI entry point, deployment configuration, health probes, resources, identity references, telemetry, an SLO, a runbook, cost ownership, and service metadata. Without a path, each team repeats decisions and may copy stale examples.

The first Core exercise is intentionally manual: copy a template repository into a sample service. Unit 5 later automates scaffolding and updates. Manual copying makes duplication, drift, and update costs visible before adding a template engine.

#### API/inference template repository

Use this structure as a Core contract. Optional files are marked; do not add a database, queue, GPU, or stateful backup to every service.

```text
api-inference/
├── README.md
├── Dockerfile
├── .dockerignore
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_health.py
├── requirements.lock
├── ci/
│   └── reusable-workflow-reference.yml
├── deploy/
│   ├── base/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       └── dev/
│           └── kustomization.yaml
├── gitops/
│   └── application.yaml
├── policies/
│   └── required-controls.md
├── observability/
│   ├── metrics.md
│   ├── dashboard.json
│   └── alerts.md
├── reliability/
│   ├── slo.yaml
│   └── runbook.md
├── security/
│   └── identity-reference.yaml
├── cost/
│   └── ownership.yaml
├── catalog-info.yaml
├── docs/
│   ├── getting-started.md
│   └── operations.md
└── CODEOWNERS
```

**Ownership of files:** application code/tests are product-team-owned after generation; the platform team owns the template and shared defaults. The platform team owns reusable CI and policy contracts; product teams own application tests. Deployment base defaults and shared chart/Kustomize components are platform-owned, while approved overlay values are product-team-owned. SLO/runbook content is jointly seeded: the platform provides a template, the service owner completes domain-specific objectives and procedures. Catalog metadata is maintained by the service owner against the platform schema.

**Dockerfile placeholder:** never invent or copy a made-up digest. Replace the placeholder with an approved digest from the organization's M01 base-image program before building.

```dockerfile
# TEMPLATE ONLY — replace both placeholders with approved M01 image digests.
# The approved build image must provide the organization's locked dependency toolchain.
ARG PYTHON_BUILD_IMAGE=APPROVED_BUILD_IMAGE@sha256:REPLACE_WITH_APPROVED_BUILD_DIGEST
ARG PYTHON_RUNTIME_IMAGE=APPROVED_RUNTIME_IMAGE@sha256:REPLACE_WITH_APPROVED_RUNTIME_DIGEST

FROM ${PYTHON_BUILD_IMAGE} AS builder
WORKDIR /build
COPY requirements.lock ./requirements.lock
# requirements.lock must contain hash-pinned dependencies under the M01 standard.
RUN python -m pip install --require-hashes --no-cache-dir \
    --prefix=/install -r requirements.lock

FROM ${PYTHON_RUNTIME_IMAGE} AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=10001:10001 app/ ./app/
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "app.main"]
```

This is a multi-stage pattern, not a ready-to-build image. The placeholders must be replaced with approved digests; the runtime image must contain the expected Python runtime and the non-root numeric identity. The exact base-image, lockfile, package-install, ownership, and build rules come from M01. Do not invent a digest or weaken hash verification to make the example build.

This short example illustrates non-root execution and a digest placeholder, but it is not a complete production multi-stage image build. M01 owns the complete hardened build pattern, lockfile/hash policy, and approved base-image reference. Do not treat the placeholder as a usable image.

`app/main.py`:

```python
"""Minimal standard-library HTTP health endpoint for the local lab."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/health", "/ready"):
            self.send_error(404)
            return
        body = json.dumps({"status": "ok"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Keep local output predictable; production logging belongs to M11.
        return


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
```

`tests/test_health.py`:

```python
import unittest
from app.main import Handler


class HealthContractTests(unittest.TestCase):
    def test_health_and_readiness_paths_are_declared(self):
        # Static contract test; does not start a server or prove runtime health.
        import inspect
        source = inspect.getsource(Handler.do_GET)
        self.assertIn('"/health"', source)
        self.assertIn('"/ready"', source)


if __name__ == "__main__":
    unittest.main()
```

`catalog-info.yaml` is a minimal illustrative metadata file for later Unit 4; the exact schema is **[VERIFY]** against the chosen catalog implementation:

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: replace-with-service-name
  description: Replace with a useful service description
  annotations:
    platform.example/path: api-inference
    platform.example/path-version: "1.0"
spec:
  type: service
  lifecycle: experimental
  owner: replace-with-team
  system: replace-with-system
```

This example is not a lesson in Backstage. The exact API version, entity schema, annotation keys, and validation rules must be checked against the selected catalog documentation **[VERIFY]**.

#### Hello world to production: intended experience

1. Copy or generate the repository.
2. Fill in service/team/environment/cost/tier metadata.
3. Run local repository and policy checks.
4. Run application tests and build using the approved M01 image process.
5. Submit through the M02 CI and M08 GitOps delivery path.
6. Confirm deployment and rollout evidence in the actual runtime.
7. Find M11 dashboard/telemetry artifacts and confirm signals are arriving.
8. Review M10 SLO/alert/runbook evidence and M12 supply-chain evidence.
9. Confirm cost labels and quota/priority declarations from M15.
10. Operate the service using the documented ownership and support boundary.

Plat-Core simulates and validates repository artifacts only. It does not deploy a service. kind and a local GitOps controller are optional Plat+Control extensions after explicit preflight and resource checks.

#### First lab: copy and inspect the API template

Create the directory and files using the structure above, then:

```bash
mkdir -p unit2-golden-path-lab/templates/api-inference
cd unit2-golden-path-lab
# Create the template files shown above under templates/api-inference.
mkdir -p examples/generated-api
cp -R templates/api-inference/. examples/generated-api/
cd examples/generated-api
python3 -m unittest discover -s tests -v
cd ../..
```

Representative expected output (not executed here):

```text
test_health_and_readiness_paths_are_declared ... ok
----------------------------------------------------------------------
Ran 1 test
OK
```

Interpretation: the local static contract test confirms that the two endpoint paths are declared in the handler. It does not start the server, prove HTTP behavior, validate the container, or prove a Kubernetes deployment. The Dockerfile digest is deliberately a placeholder and must fail the policy suite until replaced with an approved value.

**What just happened?** You copied a maintained starting point into a sample service and immediately created two copies of every default. Future changes now need a deliberate update process. The copy demonstrates why generation, version metadata, drift detection, and update PRs matter; those mechanisms are developed in Unit 5.

#### Beginner mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Calling a template a golden path | Generated files exist but no delivery or operations path is documented. | Define the full journey, owners, checks, delivery, telemetry, and support. |
| Using a fake image digest | Build fails or a placeholder accidentally reaches production. | Require an approved M01 digest and block unresolved placeholders. |
| Adding every optional dependency | A simple API receives an unnecessary database or queue. | Make features opt-in and test each add-on. |
| Treating file presence as telemetry | Dashboard file exists but no metrics arrive. | Separate artifact checks from runtime integration checks. |
| Treating local tests as deployment proof | Repository passes while runtime is broken. | Label evidence by layer: static, build, deployment, runtime. |

### 2.4 Level 2 — Intermediate

#### Five workload archetypes

All paths share a core contract: ownership, environment and cost metadata, approved identity, secure image/dependency policy, reusable CI, policy validation, observability conventions, support documentation, and version traceability. The generated application code belongs to the product team; platform defaults and reusable contracts belong to the platform team.

| Archetype | Lifecycle-specific requirements | Required artifacts/checks | Optional integrations and evidence |
|---|---|---|---|
| API/inference | Request/response, readiness, graceful shutdown, latency/error objectives, rollout/rollback. | App/tests, Dockerfile, deploy base/overlay, probes/resources, SLO, runbook, telemetry, owner/cost metadata. | Database/queue add-on only if needed; test endpoint contract and rendered manifests. |
| Batch/ETL | Scheduled or event-triggered job; freshness, idempotency, retries, checkpointing, terminal failure behavior. | Job/CronJob intent, pipeline entry point, data-contract/schema checks, freshness SLO, retry policy, cost labels, runbook. | Backup only for stateful data; checkpoint hooks connect to M13 Unit 4. Core validates declarations, not cluster execution. |
| Streaming consumer | Continuous processing, lag/freshness, bounded concurrency, backpressure, replay and offset safety. | Consumer config, lag alert/SLO, resource/concurrency bounds, replay/runbook docs, ownership/cost labels. | KEDA scaling is optional M15 Unit 10 integration; evidence includes bounded concurrency and lag alert definitions. |
| Model-serving | Model artifact and registry reference, hash/version traceability, controlled rollout and rollback. | Serving entry point, artifact manifest/hash field, model/data version metadata, deployment policy, SLO, model quality/latency telemetry. | Registry integration and actual artifact verification; GitOps promotion via M08. |
| Notebook/experiment | Ephemeral/quota-limited workspace, idle culling, reproducible environment, controlled data access, notebook-to-production transition. | Image allow-list, lockfile/hash, owner/cost/quota metadata, no credential check, output/size policy, experiment manifest. | Idle-culling integration and model registry; no production secrets in notebooks. |

**When separate templates are justified:** when lifecycle, failure semantics, security boundary, or operational evidence differs materially. API and batch have different run semantics; a parameterized “one template for everything” can hide those differences. Streaming and batch may share data-access conventions but need distinct backpressure/lag versus completion/freshness signals. A model-serving path may be an API variant only if model artifact provenance and rollout semantics remain explicit. A notebook workspace deserves a distinct lifecycle because it is interactive and often ephemeral.

**When a parameter or add-on is enough:** language/runtime choice, optional storage, queue consumer, or GPU support may be parameters/add-ons if they do not alter the core lifecycle contract. Add-ons such as “add a database,” “add a queue consumer,” or “add GPU” need idempotency and conflict tests. Template-engine behavior is Unit 5 scope; do not assume Copier/scaffolder hooks or Crossplane semantics here.

Representative concise trees:

```text
batch-etl/
├── pipeline/
│   ├── main.py
│   └── contracts/
├── tests/
├── job/
│   ├── job.yaml
│   └── schedule.yaml        # optional
├── reliability/
│   ├── freshness-slo.yaml
│   └── runbook.md
├── cost/ownership.yaml
└── README.md

model-serving/
├── serving/
├── tests/
├── model/
│   └── artifact-manifest.json
├── deploy/
├── reliability/
├── observability/
├── security/
└── README.md

streaming-consumer/
├── consumer/
├── tests/
├── config/
│   └── concurrency.yaml
├── observability/
│   └── lag-alerts.md
├── reliability/
│   └── replay-runbook.md
└── README.md

notebook-workspace/
├── notebooks/              # outputs stripped; no credentials
├── environment/
│   └── requirements.lock
├── workspace-policy.md     # quota, idle-cull, image allow-list
├── experiment.yaml
└── README.md
```

For each archetype, generated application files are team-owned; shared policy and platform defaults are platform-owned. A service owner completes the SLO, runbook, data/model contracts, and domain-specific telemetry. Required evidence includes a passing static check, a negative test, ownership metadata, and an operational artifact. Optional cluster integration must separately prove deployment and runtime behavior.

#### Repository conventions

Use stable, lowercase repository/service identifiers and document naming rules. Required labels in this course's examples are `team`, `service`, `env`, `cost-center`, and `tier`. Their exact spelling and value schema are illustrative and must be aligned to the repository's standards **[VERIFY]**. CODEOWNERS should map platform-owned paths and product-owned application paths to responsible teams. M02/M08 own branch protection, PR review, workflow permissions, and promotion rules. Do not treat a sample CODEOWNERS file as enforceable until the SCM implementation is configured.

#### Default → option → escape support policy

| Route | Contract | Support |
|---|---|---|
| Default path | Tested and documented end-to-end path; platform-selected secure defaults. | Fully supported, standard response target, platform-owned updates. |
| Supported option | Named parameter/add-on with compatibility and negative tests. | Fully supported within declared combinations. |
| Escape hatch | Custom manifest/IaC or justified alternative; owner, reason, docs, risk review, and support status recorded. | Best-effort or explicitly bounded support; mandatory guardrails still apply. |

Exceptions are reviewed by the platform owner plus relevant security/SRE/domain owner. Record service, requested deviation, reason, risk, compensating control, approver, date, expiry/review date, and migration/graduation condition. Time-limit exceptions where appropriate. Repeated successful alternatives should be assessed for promotion into a supported option. An escape hatch never disables mandatory security/compliance controls.

A course-level illustrative annotation might be `platform.example/path: custom`; exact metadata schema is **[VERIFY]** and must match the service catalog/repository standard. Off-path services remain subject to the same mandatory security, identity, audit, and cost controls.

#### Core policy and validation suite

The local validator uses tool-independent rule definitions. External linters such as hadolint, kubeconform, or policy engines are optional; exact versions and syntax are **[VERIFY]**. The rules below define the contract independent of any particular engine.

| ID | Scope and rationale | Validation method | Severity default | Actionable failure message |
|---|---|---|---|---|
| GP001 | Dockerfile must exist for container archetypes. | File check. | Block | `GP001: Dockerfile missing; add the M01-approved image build; see docs/getting-started.md.` |
| GP002 | Base image must be approved and digest-pinned where required. | Reject placeholder, mutable tag, or missing `@sha256:`. | Block | `GP002: base image is not digest-pinned; use an approved M01 digest; see docs/security.md.` |
| GP003 | Container must declare non-root execution. | Require `USER` instruction. | Block | `GP003: non-root USER missing; add the approved runtime UID/GID; see M01 image standard.` |
| GP004 | Mutable `latest` tags are prohibited. | Scan Dockerfile and manifests for `:latest`. | Block | `GP004: mutable latest tag found; pin an approved immutable reference; see M01.` |
| GP005 | CI entry point must exist. | File check. | Block | `GP005: reusable CI reference missing; integrate the M02 workflow; see docs/ci.md.` |
| GP006 | CI permissions must be least-privilege and dependencies pinned. | Static contract scan for explicit permissions and pin marker. | Block | `GP006: CI permissions/pins are incomplete; use the reviewed least-privilege workflow; see M02.` |
| GP007 | Application tests must exist. | File check. | Block | `GP007: tests are missing; add a workload contract test; see docs/local-development.md.` |
| GP008 | Required ownership/environment/cost labels must exist. | Parse `metadata.json` required keys. | Block | `GP008: required labels missing; set team, service, env, cost-center, tier; see docs/metadata.md.` |
| GP009 | Resource requests and limits must be declared for Kubernetes workloads. | Rendered manifest scan. | Block for deployable workload; N/A otherwise | `GP009: resource request/limit missing; declare measured workload values; see M03.` |
| GP010 | Health probes must exist where applicable. | Manifest scan for liveness/readiness. | Block for API; warning for non-service jobs | `GP010: applicable health/readiness probe missing; add the workload-appropriate probe; see M03.` |
| GP011 | Privileged mode and hostPath are prohibited unless approved. | Scan manifest text/structured data. | Block | `GP011: privileged or hostPath setting found; remove it or attach approved exception; see M03 security policy.` |
| GP012 | Network control must be declared for networked workloads. | Require network policy reference/declaration. | Block for deployable networked workload | `GP012: network control is undeclared; add approved M04 policy reference; see docs/networking.md.` |
| GP013 | SLO and runbook must exist. | File checks. | Block for production path | `GP013: SLO/runbook missing; add service objectives and operational steps; see M10.` |
| GP014 | Catalog metadata must exist and have required fields. | JSON/YAML-independent required metadata check in this lab. | Block for catalogued service | `GP014: catalog metadata incomplete; set name, owner, lifecycle, path version; see docs/metadata.md.` |
| GP015 | Cost ownership and quota/priority metadata must exist where applicable. | Metadata keys and workload declarations. | Block for production; warning for local-only | `GP015: cost/quota metadata missing; declare cost owner and approved class; see M15.` |
| GP016 | No plaintext credential patterns in tracked files. | Conservative pattern scan; review findings. | Block | `GP016: possible credential value found; remove it and use M09 identity/secret references; see docs/security.md.` |
| GP017 | Required provenance/SBOM/signing evidence must be declared. | CI evidence reference check. | Block for release path | `GP017: supply-chain evidence reference missing; integrate M12 build evidence; see docs/supply-chain.md.` |
| GP018 | Documentation and ownership file must exist. | File checks. | Warning locally; block for GA | `GP018: docs/CODEOWNERS incomplete; add owner, local run, support, and escalation; see docs/operations.md.` |
| GP019 | Stateful workloads must declare backup/DR tier. | Archetype/feature conditional check. | Block if stateful | `GP019: stateful workload lacks backup tier; declare M13 policy or remove stateful feature; see docs/recovery.md.` |
| GP020 | Notebook files must not embed credentials or oversized outputs. | Text scan and file-size policy. | Block | `GP020: notebook policy violation; strip outputs and remove credentials; see docs/notebooks.md.` |

A rule definition must include ID, rationale, scope, validation, severity, failure text, positive test, negative test, and default mode. The following matrix makes the positive and negative fixture explicit for every rule. Positive fixtures use the valid synthetic API repository; workload-conditional rules are evaluated only for the applicable archetype or feature.

| Rule | Positive test | Negative test |
|---|---|---|
| GP001 | API/model-serving fixture contains Dockerfile. | Remove Dockerfile from a container archetype. |
| GP002 | Dockerfile uses an approved 64-hex digest reference. | Replace it with a mutable tag or unresolved placeholder. |
| GP003 | Dockerfile declares the approved non-root UID/GID. | Remove the `USER` instruction. |
| GP004 | All image references are immutable and do not use `:latest`. | Add an image reference ending in `:latest`. |
| GP005 | CI contract references the reusable M02 workflow. | Remove the CI workflow reference file. |
| GP006 | CI contract declares read-only minimum permissions and a reviewed immutable reference. | Remove the permission declaration or pin marker. |
| GP007 | Workload contract test exists. | Remove the test file. |
| GP008 | `team`, `service`, `env`, `cost-center`, and `tier` are non-empty. | Remove or blank one required metadata value. |
| GP009 | Deployable workload has requests and limits. | Remove the resource block. |
| GP010 | API has applicable readiness and liveness probes. | Remove either required probe from an API fixture. |
| GP011 | Manifest contains neither privileged mode nor unapproved hostPath. | Add `privileged: true` or a hostPath mount in the isolated fixture. |
| GP012 | Networked workload references the approved M04 network control. | Remove the network-control declaration. |
| GP013 | SLO and runbook files both exist. | Remove either file. |
| GP014 | Catalog metadata has name, owner, lifecycle, and path identity. | Remove a required catalog field. |
| GP015 | Applicable workload has cost ownership and quota/priority metadata. | Remove quota-class or cost ownership metadata. |
| GP016 | Tracked files contain no credential-shaped values. | Add a benign synthetic credential-shaped string to a fixture. |
| GP017 | Release CI contract declares SBOM, provenance, and signing evidence. | Remove one evidence declaration. |
| GP018 | Getting-started documentation and CODEOWNERS exist. | Remove either required file. |
| GP019 | Stateless workload needs no backup tier; stateful workload declares one. | Mark workload stateful and omit backup tier. |
| GP020 | Notebook cells have empty outputs and no credential-shaped content. | Add a non-empty notebook output or credential-shaped fixture. |

The executable tests below exercise all 20 negative cases plus a clean positive repository, warning-mode behavior, actionable-message structure, conformance false positives, drift classifications, template-matrix failures, and dry-run non-mutation. A production policy catalog should retain these fixtures with each rule release.

**Warning vs block:** blocking violations return exit code `1`; warning-only findings return exit code `2`; a clean result returns `0`. This makes an advisory finding distinguishable from a clean pass without treating it as a blocking failure. The report retains warning severity and rule IDs. Start a new rule in warning only when risk permits, measure false positives, document owner and migration date, then move to blocking after communication and remediation support. Time-limited exceptions require owner, reason, compensating control, approver, and expiry. Do not implement a blanket “ignore all” switch.

**Actionable message quality standard:** every failure says (1) which rule failed, (2) why it exists, (3) how to fix it, and (4) where to find the standard. Test these four elements. CI and admission policy should be consistent, but admission implementation belongs to M12/M03/M04 and is not required in Plat-Core.

#### Complete Plat-Core validator and conformance scanner

Create this layout:

```text
unit2-golden-path-lab/
├── templates/{api-inference,batch-etl,model-serving,streaming-consumer,notebook-workspace}/
├── examples/{generated-api,generated-batch,generated-model-serving}/
├── policies/
│   ├── rules.json
│   └── planted-unsafe-corpus/
├── src/
│   ├── validate_repo.py
│   ├── scan_conformance.py
│   ├── test_template_matrix.py
│   └── propagation_dry_run.py
├── tests/
│   ├── test_validate_repo.py
│   ├── test_conformance.py
│   ├── test_template_matrix.py
│   └── test_propagation_dry_run.py
├── docs/
│   ├── getting-started.md
│   ├── local-development.md
│   ├── deploy-and-observe.md
│   ├── runbook.md
│   ├── faq.md
│   └── support-and-escape-policy.md
├── artifacts/
│   ├── default-register.md
│   ├── conformance-report.md
│   ├── compatibility-matrix.md
│   ├── developer-experience-measurement.md
│   └── notebook-to-pipeline.md
├── decisions/ADR-001..005
└── synthetic-data/synthetic-repositories.json
```

For a compact but executable lab, the validator consumes a normalized `metadata.json` plus required file paths. The generated examples should include `metadata.json` with `archetype`, `path_version`, `team`, `service`, `env`, `cost-center`, `tier`, `stateful`, and `catalog_owner`. YAML-specific validation is deliberately delegated to optional schema tools; the core scanner does not pretend to parse arbitrary YAML.

`src/validate_repo.py`:

```python
"""Deterministic, tool-independent repository checks for the Plat-Core lab."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

DOCS = "docs/getting-started.md"
REQUIRED_BASE = [
    "README.md", "metadata.json", "tests/test_contract.py",
    "ci/reusable-workflow-reference.yml", "catalog-info.yaml",
    "reliability/slo.yaml", "reliability/runbook.md",
    "observability/metrics.md", "security/identity-reference.yaml",
    "cost/ownership.yaml", "CODEOWNERS",
]
RULE_MESSAGES = {
    "GP001": "Dockerfile missing; add the M01-approved image build; see docs/getting-started.md.",
    "GP002": "base image is not digest-pinned; use an approved M01 digest; see docs/getting-started.md.",
    "GP003": "non-root USER missing; add the approved runtime UID/GID; see docs/getting-started.md.",
    "GP004": "mutable latest tag found; pin an approved immutable reference; see docs/getting-started.md.",
    "GP005": "reusable CI reference missing; integrate the M02 workflow; see docs/getting-started.md.",
    "GP006": "CI permissions/pins are incomplete; use reviewed least privilege; see docs/getting-started.md.",
    "GP007": "tests are missing; add a workload contract test; see docs/getting-started.md.",
    "GP008": "required labels missing; set team, service, env, cost-center, tier; see docs/getting-started.md.",
    "GP009": "resource request/limit missing; declare measured values; see docs/getting-started.md.",
    "GP010": "applicable health/readiness probe missing; add workload-appropriate probes; see docs/getting-started.md.",
    "GP011": "privileged or hostPath setting found; remove it or attach approved exception; see docs/getting-started.md.",
    "GP012": "network control is undeclared; add approved M04 policy reference; see docs/getting-started.md.",
    "GP013": "SLO/runbook missing; add service objectives and operational steps; see docs/getting-started.md.",
    "GP014": "catalog metadata incomplete; set name, owner, lifecycle, path version; see docs/getting-started.md.",
    "GP015": "cost/quota metadata missing; declare cost owner and approved class; see docs/getting-started.md.",
    "GP016": "possible credential value found; remove it and use M09 references; see docs/getting-started.md.",
    "GP017": "supply-chain evidence reference missing; integrate M12 evidence; see docs/getting-started.md.",
    "GP018": "docs/CODEOWNERS incomplete; add local run, support, and owner; see docs/getting-started.md.",
    "GP019": "stateful workload lacks backup tier; declare M13 policy; see docs/getting-started.md.",
    "GP020": "notebook policy violation; strip outputs and remove credentials; see docs/getting-started.md.",
}
@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    path: str

def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"metadata file missing: {path}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"metadata file malformed: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("metadata must be a JSON object")
    return data

def validate(repo: Path, mode: str = "block") -> list[Finding]:
    if mode not in {"block", "warn"}:
        raise ValueError("mode must be 'block' or 'warn'")
    if not repo.exists() or not repo.is_dir():
        raise ValueError(f"repository directory does not exist: {repo}")
    findings: list[Finding] = []
    def add(rule: str, path: str, severity: str | None = None):
        findings.append(Finding(rule, severity or ("warning" if mode == "warn" else "blocking"),
                                RULE_MESSAGES[rule], path))
    for rel in REQUIRED_BASE:
        if not (repo / rel).is_file():
            rule = "GP005" if rel.startswith("ci/") else "GP007" if rel.startswith("tests/") else "GP013" if rel.startswith("reliability/") else "GP018"
            add(rule, rel)
    meta_path = repo / "metadata.json"
    meta = {}
    if meta_path.exists():
        meta = read_json(meta_path)
    required = ["team", "service", "env", "cost-center", "tier"]
    if any(not isinstance(meta.get(k), str) or not meta[k].strip() for k in required):
        add("GP008", "metadata.json")
    if not isinstance(meta.get("path_version"), str) or not meta.get("path_version"):
        add("GP014", "metadata.json")
    if not isinstance(meta.get("catalog_owner"), str) or not meta.get("catalog_owner"):
        add("GP014", "metadata.json")
    archetype = meta.get("archetype")
    if archetype not in {"api-inference", "batch-etl", "model-serving", "streaming-consumer", "notebook-workspace"}:
        add("GP014", "metadata.json")
    if archetype in {"api-inference", "model-serving"}:
        if not (repo / "Dockerfile").is_file():
            add("GP001", "Dockerfile")
        else:
            docker = (repo / "Dockerfile").read_text(encoding="utf-8", errors="replace")
            digest_pinned = re.search(r"@sha256:[0-9a-fA-F]{64}\b", docker) is not None
            if "APPROVED_BASE_IMAGE" in docker or "REPLACE_WITH_APPROVED_DIGEST" in docker or not digest_pinned:
                add("GP002", "Dockerfile")
            if not re.search(r"(?im)^\s*USER\s+\S+", docker):
                add("GP003", "Dockerfile")
            if re.search(r"(?i):latest\b", docker):
                add("GP004", "Dockerfile")
    if archetype in {"api-inference", "batch-etl", "model-serving", "streaming-consumer"}:
        deploy = repo / "deploy"
        text = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                         for p in deploy.rglob("*") if p.is_file()) if deploy.exists() else ""
        if re.search(r":latest\b", text, flags=re.IGNORECASE):
            add("GP004", "deploy/")
        if "resources:" not in text or "limits:" not in text or "requests:" not in text:
            add("GP009", "deploy/")
        if archetype in {"api-inference", "model-serving"} and ("readinessProbe:" not in text or "livenessProbe:" not in text):
            add("GP010", "deploy/")
        if "privileged: true" in text or "hostPath:" in text:
            add("GP011", "deploy/")
        if not (repo / "security/network-control.md").is_file():
            add("GP012", "security/network-control.md")
    if not (repo / "reliability/slo.yaml").is_file() or not (repo / "reliability/runbook.md").is_file():
        add("GP013", "reliability/")
    if not (repo / "cost/ownership.yaml").is_file() or not (repo / "cost/quota-class.yaml").is_file():
        add("GP015", "cost/")
    tracked = [p for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts]
    credential = re.compile(r"(?i)(password|api[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?(?!\$\{|<REPLACE)[A-Za-z0-9_\-]{8,}")
    for path in tracked:
        if path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".json", ".ipynb", ".env"}:
            body = path.read_text(encoding="utf-8", errors="replace")
            if credential.search(body):
                add("GP016", str(path.relative_to(repo)))
                break
    ci_path = repo / "ci/reusable-workflow-reference.yml"
    if ci_path.exists():
        ci = ci_path.read_text(encoding="utf-8", errors="replace")
        if "permissions:" not in ci or "contents: read" not in ci or "PINNED_REFERENCE" not in ci:
            add("GP006", "ci/reusable-workflow-reference.yml")
        if "sbom" not in ci.lower() or "provenance" not in ci.lower() or "sign" not in ci.lower():
            add("GP017", "ci/reusable-workflow-reference.yml")
    catalog = repo / "catalog-info.yaml"
    if catalog.exists():
        cat = catalog.read_text(encoding="utf-8", errors="replace")
        if not all(x in cat for x in ("name:", "owner:", "lifecycle:")):
            add("GP014", "catalog-info.yaml")
    docs_ok = (repo / DOCS).is_file() and (repo / "CODEOWNERS").is_file()
    if not docs_ok:
        add("GP018", "docs/ or CODEOWNERS")
    if meta.get("stateful") is True and not (repo / "reliability/backup-tier.yaml").is_file():
        add("GP019", "reliability/backup-tier.yaml")
    if archetype == "notebook-workspace":
        for p in tracked:
            if p.suffix.lower() == ".ipynb":
                try:
                    notebook = json.loads(p.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    add("GP020", str(p.relative_to(repo)))
                    continue
                cells = notebook.get("cells", []) if isinstance(notebook, dict) else []
                if not isinstance(cells, list):
                    add("GP020", str(p.relative_to(repo)))
                    continue
                if any(isinstance(cell, dict) and cell.get("outputs") for cell in cells):
                    add("GP020", str(p.relative_to(repo)))
                    break
    return findings

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("--mode", choices=("block", "warn"), default="block")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        findings = validate(args.repo, args.mode)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps([asdict(x) for x in findings], indent=2))
    else:
        for f in findings:
            print(f"{f.severity.upper()} {f.rule_id} [{f.path}]: {f.message}")
        print(f"Findings: {len(findings)}")
    blocking = any(f.severity == "blocking" for f in findings)
    if blocking:
        return 1
    if findings:
        return 2  # advisory findings are distinct from a clean pass
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

The scanner implements deterministic rule checks for the local normalized contract. It is intentionally conservative and not a YAML parser, Docker build, secret scanner, Kubernetes schema validator, or admission controller. The table defines 20 rule families; the executable script covers representative static checks and is extended by the test matrix and review checklist. Before using it as a production gate, implement a positive and negative fixture for every rule, parse structured formats with verified parsers, and validate false-positive behavior.

`src/scan_conformance.py`:

```python
"""Classify synthetic repositories using explicit path identity and evidence."""
from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path

try:  # Supports both `python src/scan_conformance.py` and package imports in tests.
    from .validate_repo import validate
except ImportError:  # pragma: no cover - exercised by direct-script invocation
    from validate_repo import validate

# Teaching fixture only. A real platform must publish its supported versions.
SUPPORTED_PATH_VERSIONS = {"1.0"}
SUPPORTED_ARCHETYPES = {
    "api-inference", "batch-etl", "model-serving",
    "streaming-consumer", "notebook-workspace",
}


def assess_drift(repo: Path, meta: dict) -> dict:
    """Compare only platform-managed files; product-owned additions are not drift."""
    manifest_path = repo / "template-manifest.json"
    if not manifest_path.is_file():
        return {"status": "not-assessed", "items": [],
                "reason": "template-manifest.json is absent; baseline comparison is unavailable"}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return {"status": "invalid-manifest", "items": [], "reason": "template manifest is malformed"}
    managed = manifest.get("managed_files") if isinstance(manifest, dict) else None
    if not isinstance(managed, dict):
        return {"status": "invalid-manifest", "items": [],
                "reason": "managed_files must be a path-to-SHA256 object"}
    approved = set(meta.get("approved_overrides", [])) if isinstance(meta.get("approved_overrides", []), list) else set()
    items = []
    for relative, expected_hash in sorted(managed.items()):
        rel_path = Path(relative)
        if rel_path.is_absolute() or ".." in rel_path.parts or not isinstance(expected_hash, str):
            return {"status": "invalid-manifest", "items": [], "reason": "unsafe path or invalid hash entry"}
        target = repo / rel_path
        if not target.is_file():
            state = "missing"
        else:
            actual_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            state = "clean" if actual_hash == expected_hash else (
                "approved-customization" if relative in approved else "unexplained-modification"
            )
        if state != "clean":
            items.append({"path": relative, "reason": state})
    status = "clean" if not items else "drifted"
    return {"status": status, "items": items,
            "reason": "compared platform-managed files only; product-owned files are excluded"}


def mandatory_findings(repo: Path) -> list[str]:
    """Apply baseline controls even when a repository is off the supported path."""
    try:
        return sorted({finding.rule_id for finding in validate(repo, "block")})
    except (OSError, ValueError):
        return ["VALIDATION_ERROR"]


def classify(repo: Path) -> dict:
    if not repo.is_dir():
        return {"service": repo.name, "status": "invalid", "reason": "not a directory"}
    meta_file = repo / "metadata.json"
    if not meta_file.is_file():
        return {"service": repo.name, "status": "off-path", "reason": "no metadata.json",
                "mandatory_findings": mandatory_findings(repo)}
    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return {"service": repo.name, "status": "invalid", "reason": "malformed metadata",
                "mandatory_findings": mandatory_findings(repo)}
    if not isinstance(meta, dict):
        return {"service": repo.name, "status": "invalid", "reason": "metadata is not an object",
                "mandatory_findings": mandatory_findings(repo)}
    version = meta.get("path_version")
    archetype = meta.get("archetype")
    service = meta.get("service", repo.name)
    if not isinstance(version, str) or not version or not isinstance(archetype, str) or not archetype:
        return {"service": service, "status": "off-path", "reason": "no declared path identity",
                "mandatory_findings": mandatory_findings(repo)}
    if version not in SUPPORTED_PATH_VERSIONS:
        return {"service": service, "archetype": archetype, "path_version": version,
                "status": "unsupported-version", "reason": "path version is not in the supported set",
                "mandatory_findings": mandatory_findings(repo)}
    if archetype not in SUPPORTED_ARCHETYPES:
        return {"service": service, "archetype": archetype, "path_version": version,
                "status": "invalid", "reason": "unsupported archetype",
                "mandatory_findings": mandatory_findings(repo)}
    findings = mandatory_findings(repo)
    drift = assess_drift(repo, meta)
    if findings:
        return {"service": service, "archetype": archetype, "path_version": version,
                "status": "nonconformant", "finding_ids": findings, "drift": drift}
    return {"service": service, "archetype": archetype, "path_version": version,
            "status": "conformant", "finding_ids": [], "drift": drift}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f"root directory does not exist: {args.root}")
    rows = [classify(path) for path in sorted(args.root.iterdir()) if path.is_dir()]
    report = {
        "classification_contract": "declared supported path identity + required artifacts + all blocking checks pass",
        "services": rows,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

`src/test_template_matrix.py`:

```python
"""Small deterministic matrix runner; no template engine is required."""
from pathlib import Path
import subprocess
import sys

ARCHETYPES = ("api-inference", "batch-etl", "model-serving",
              "streaming-consumer", "notebook-workspace")

def run_matrix(root: Path) -> list[tuple[str, int]]:
    results = []
    for archetype in ARCHETYPES:
        template = root / "templates" / archetype
        if not template.is_dir():
            results.append((archetype, 2))
            continue
        # Static matrix smoke: each template must declare its archetype metadata.
        metadata = template / "metadata.json"
        if not metadata.is_file():
            results.append((archetype, 2))
            continue
        import json
        try:
            data = json.loads(metadata.read_text(encoding="utf-8"))
            code = 0 if data.get("archetype") == archetype else 1
        except (ValueError, AttributeError):
            code = 2
        results.append((archetype, code))
    return results

if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    results = run_matrix(root)
    for name, code in results:
        print(f"{name}: {'PASS' if code == 0 else 'FAIL'} (code={code})")
    raise SystemExit(1 if any(code for _, code in results) else 0)
```

`src/propagation_dry_run.py`:

```python
"""Dry-run-only base image reference update proposal for synthetic repositories."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def proposals(root: Path, old: str, new: str) -> list[dict]:
    if not old or not new or old == new:
        raise ValueError("old and new references must be non-empty and different")
    if "@sha256:" not in new:
        raise ValueError("new reference must include an approved digest")
    rows = []
    for dockerfile in sorted(root.glob("*/Dockerfile")):
        text = dockerfile.read_text(encoding="utf-8")
        if old in text:
            rows.append({"file": str(dockerfile), "status": "would-update",
                         "old": old, "new": new,
                         "conflict": text.count(old) != 1})
    return rows

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--old", required=True)
    p.add_argument("--new", required=True)
    p.add_argument("--apply", action="store_true",
                   help="Refused: this Core drill never writes repository files.")
    a = p.parse_args()
    if a.apply:
        p.error("apply is intentionally unsupported; inspect the dry-run proposal and create reviewed PRs manually")
    if not a.root.is_dir():
        p.error("repository root does not exist")
    try:
        print(json.dumps(proposals(a.root, a.old, a.new), indent=2))
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

#### Complete negative-test and conformance test suite

The earlier script blocks are accompanied by the following complete Python standard-library tests. `tests/support.py` builds one valid synthetic API repository; each policy test changes exactly one condition and asserts the expected rule ID. The other suites exercise scanner classifications, template-matrix behavior, and dry-run safety. These are executable tests, not pseudocode.

`tests/support.py`:

```python
"""Synthetic valid repository fixture shared by Unit 2 tests."""
import json
from pathlib import Path


def make_valid_repo(root: Path, archetype: str = "api-inference") -> Path:
    repo = root / "sample-service"
    files = {
        "README.md": "# Synthetic service\n",
        "metadata.json": json.dumps({
            "archetype": archetype, "path_version": "1.0", "team": "team-example",
            "service": "sample-service", "env": "dev", "cost-center": "cc-example",
            "tier": "standard", "stateful": False, "catalog_owner": "team-example"
        }),
        "tests/test_contract.py": "# contract test placeholder\n",
        "ci/reusable-workflow-reference.yml": (
            "permissions:\n  contents: read\n"
            "workflow: REUSABLE_WORKFLOW_PINNED_REFERENCE\n"
            "evidence: sbom provenance signing\n"
        ),
        "catalog-info.yaml": "metadata:\n  name: sample-service\n  owner: team-example\n  lifecycle: experimental\n",
        "reliability/slo.yaml": "service: sample-service\n",
        "reliability/runbook.md": "# Runbook\n",
        "observability/metrics.md": "# Metrics contract\n",
        "security/identity-reference.yaml": "identityRef: workload-identity-example\n",
        "security/network-control.md": "Approved M04 network policy reference\n",
        "cost/ownership.yaml": "team: team-example\n",
        "cost/quota-class.yaml": "class: standard\n",
        "docs/getting-started.md": "# Getting started\n",
        "CODEOWNERS": "* @platform-team\n",
        "Dockerfile": (
            "FROM registry.example/base@sha256:" + "a" * 64 + "\n"
            "USER 10001:10001\n"
        ),
        "deploy/deployment.yaml": (
            "image: registry.example/app@sha256:" + "b" * 64 + "\n"
            "resources:\n  requests:\n    cpu: 100m\n  limits:\n    cpu: 500m\n"
            "readinessProbe:\n  httpGet:\n    path: /ready\n"
            "livenessProbe:\n  httpGet:\n    path: /health\n"
        ),
    }
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return repo


def load_metadata(repo: Path) -> dict:
    return json.loads((repo / "metadata.json").read_text(encoding="utf-8"))


def save_metadata(repo: Path, data: dict) -> None:
    (repo / "metadata.json").write_text(json.dumps(data), encoding="utf-8")
```

`tests/test_validate_repo.py`:

```python
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.validate_repo import validate
from support import make_valid_repo, load_metadata, save_metadata


class ValidateRepoRuleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = make_valid_repo(self.root)

    def ids(self, mode="block"):
        return {item.rule_id for item in validate(self.repo, mode)}

    def test_clean_repository_passes(self):
        self.assertEqual(validate(self.repo, "block"), [])

    def test_gp001_missing_dockerfile(self):
        (self.repo / "Dockerfile").unlink()
        self.assertIn("GP001", self.ids())

    def test_gp002_digest_pin_required(self):
        p = self.repo / "Dockerfile"
        p.write_text("FROM registry.example/base:1.2\nUSER 10001:10001\n")
        self.assertIn("GP002", self.ids())

    def test_gp003_non_root_required(self):
        p = self.repo / "Dockerfile"
        p.write_text("FROM registry.example/base@sha256:" + "a" * 64 + "\n")
        self.assertIn("GP003", self.ids())

    def test_gp004_latest_rejected(self):
        p = self.repo / "deploy/deployment.yaml"
        p.write_text(p.read_text() + "image: registry.example/app:latest\n")
        self.assertIn("GP004", self.ids())

    def test_gp005_reusable_ci_required(self):
        (self.repo / "ci/reusable-workflow-reference.yml").unlink()
        self.assertIn("GP005", self.ids())

    def test_gp006_ci_permissions_and_pin_required(self):
        (self.repo / "ci/reusable-workflow-reference.yml").write_text("workflow: floating\n")
        self.assertIn("GP006", self.ids())

    def test_gp007_tests_required(self):
        (self.repo / "tests/test_contract.py").unlink()
        self.assertIn("GP007", self.ids())

    def test_gp008_required_metadata_labels(self):
        meta = load_metadata(self.repo)
        meta["team"] = ""
        save_metadata(self.repo, meta)
        self.assertIn("GP008", self.ids())

    def test_gp009_resources_required(self):
        (self.repo / "deploy/deployment.yaml").write_text("image: registry.example/app@sha256:" + "b" * 64 + "\n")
        self.assertIn("GP009", self.ids())

    def test_gp010_probes_required_for_api(self):
        p = self.repo / "deploy/deployment.yaml"
        p.write_text(p.read_text().replace("readinessProbe:", "readinessCheck:"))
        self.assertIn("GP010", self.ids())

    def test_gp011_privileged_or_hostpath_rejected(self):
        p = self.repo / "deploy/deployment.yaml"
        p.write_text(p.read_text() + "securityContext:\n  privileged: true\n")
        self.assertIn("GP011", self.ids())

    def test_gp012_network_control_required(self):
        (self.repo / "security/network-control.md").unlink()
        self.assertIn("GP012", self.ids())

    def test_gp013_slo_and_runbook_required(self):
        (self.repo / "reliability/slo.yaml").unlink()
        self.assertIn("GP013", self.ids())

    def test_gp014_catalog_metadata_required(self):
        (self.repo / "catalog-info.yaml").write_text("metadata:\n  name: sample\n  lifecycle: experimental\n")
        self.assertIn("GP014", self.ids())

    def test_gp015_cost_and_quota_required(self):
        (self.repo / "cost/quota-class.yaml").unlink()
        self.assertIn("GP015", self.ids())

    def test_gp016_plaintext_credential_rejected(self):
        (self.repo / "app.py").write_text("password = 'SyntheticSecretValue123'\n")
        self.assertIn("GP016", self.ids())

    def test_gp017_supply_chain_evidence_required(self):
        p = self.repo / "ci/reusable-workflow-reference.yml"
        p.write_text("permissions:\n  contents: read\nPINNED_REFERENCE: true\n")
        self.assertIn("GP017", self.ids())

    def test_gp018_docs_and_codeowners_required(self):
        (self.repo / "CODEOWNERS").unlink()
        self.assertIn("GP018", self.ids())

    def test_gp019_stateful_workload_backup_required(self):
        meta = load_metadata(self.repo)
        meta["stateful"] = True
        save_metadata(self.repo, meta)
        self.assertIn("GP019", self.ids())

    def test_gp020_notebook_outputs_must_be_stripped(self):
        meta = load_metadata(self.repo)
        meta["archetype"] = "notebook-workspace"
        save_metadata(self.repo, meta)
        (self.repo / "notebooks").mkdir()
        (self.repo / "notebooks/demo.ipynb").write_text('{"cells": [{"outputs": [{"text": "synthetic"}]}]}')
        self.assertIn("GP020", self.ids())

    def test_warning_mode_preserves_findings_as_warnings(self):
        (self.repo / "tests/test_contract.py").unlink()
        findings = validate(self.repo, "warn")
        self.assertTrue(any(x.rule_id == "GP007" and x.severity == "warning" for x in findings))

    def test_warning_mode_has_distinct_nonzero_cli_status(self):
        (self.repo / "tests/test_contract.py").unlink()
        result = subprocess.run(
            [sys.executable, "src/validate_repo.py", str(self.repo), "--mode", "warn"],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("WARNING GP007", result.stdout)

    def test_all_rule_messages_have_action_and_reference(self):
        from src.validate_repo import RULE_MESSAGES
        self.assertEqual(set(RULE_MESSAGES), {f"GP{i:03d}" for i in range(1, 21)})
        for rule_id, message in RULE_MESSAGES.items():
            rendered_diagnostic = f"{rule_id}: {message}"
            self.assertIn(rule_id, rendered_diagnostic)
            self.assertIn(";", message)
            self.assertIn("see ", message)


if __name__ == "__main__":
    unittest.main()
```

`tests/test_conformance.py`:

```python
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.scan_conformance import classify
from support import make_valid_repo, load_metadata, save_metadata


class ConformanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = make_valid_repo(self.root)

    def test_valid_supported_repository_is_conformant(self):
        self.assertEqual(classify(self.repo)["status"], "conformant")

    def test_template_lookalike_without_identity_is_off_path(self):
        (self.repo / "metadata.json").unlink()
        self.assertEqual(classify(self.repo)["status"], "off-path")

    def test_old_version_is_explicitly_unsupported(self):
        meta = load_metadata(self.repo)
        meta["path_version"] = "0.4"
        save_metadata(self.repo, meta)
        self.assertEqual(classify(self.repo)["status"], "unsupported-version")

    def test_missing_required_artifact_is_nonconformant(self):
        (self.repo / "reliability/runbook.md").unlink()
        self.assertEqual(classify(self.repo)["status"], "nonconformant")

    def test_policy_failure_is_nonconformant(self):
        (self.repo / "deploy/deployment.yaml").write_text("privileged: true\n")
        self.assertEqual(classify(self.repo)["status"], "nonconformant")

    def test_malformed_metadata_is_invalid(self):
        (self.repo / "metadata.json").write_text("{not-json")
        self.assertEqual(classify(self.repo)["status"], "invalid")

    def test_unknown_archetype_is_invalid(self):
        meta = load_metadata(self.repo)
        meta["archetype"] = "unknown"
        save_metadata(self.repo, meta)
        self.assertEqual(classify(self.repo)["status"], "invalid")

    def test_off_path_repository_still_fails_mandatory_security_checks(self):
        meta = load_metadata(self.repo)
        meta.pop("path_version")
        save_metadata(self.repo, meta)
        (self.repo / "app.py").write_text("password = 'SyntheticSecretValue123'\n")
        p = self.repo / "deploy/deployment.yaml"
        p.write_text(p.read_text() + "securityContext:\n  privileged: true\n")
        result = classify(self.repo)
        self.assertEqual(result["status"], "off-path")
        self.assertIn("GP016", result["mandatory_findings"])
        self.assertIn("GP011", result["mandatory_findings"])

    def write_manifest(self, relative):
        target = self.repo / relative
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        (self.repo / "template-manifest.json").write_text(
            json.dumps({"managed_files": {relative: digest}}), encoding="utf-8"
        )

    def test_drift_manifest_clean(self):
        self.write_manifest("README.md")
        self.assertEqual(classify(self.repo)["drift"]["status"], "clean")

    def test_modified_managed_file_is_unexplained_drift(self):
        self.write_manifest("README.md")
        (self.repo / "README.md").write_text("# Changed by synthetic exercise\n")
        result = classify(self.repo)
        self.assertEqual(result["drift"]["items"][0]["reason"], "unexplained-modification")

    def test_approved_override_is_classified_separately(self):
        self.write_manifest("README.md")
        (self.repo / "README.md").write_text("# Approved local customization\n")
        meta = load_metadata(self.repo)
        meta["approved_overrides"] = ["README.md"]
        save_metadata(self.repo, meta)
        result = classify(self.repo)
        self.assertEqual(result["drift"]["items"][0]["reason"], "approved-customization")

    def test_missing_managed_file_is_reported(self):
        self.write_manifest("README.md")
        (self.repo / "README.md").unlink()
        result = classify(self.repo)
        self.assertEqual(result["drift"]["items"][0]["reason"], "missing")


if __name__ == "__main__":
    unittest.main()
```

`tests/test_template_matrix.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from src.test_template_matrix import ARCHETYPES, run_matrix


class TemplateMatrixTests(unittest.TestCase):
    def test_all_declared_archetypes_pass_with_matching_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ARCHETYPES:
                path = root / "templates" / name
                path.mkdir(parents=True)
                (path / "metadata.json").write_text(json.dumps({"archetype": name}))
            self.assertEqual(run_matrix(root), [(name, 0) for name in ARCHETYPES])

    def test_missing_template_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(all(code != 0 for _, code in run_matrix(Path(tmp))))

    def test_wrong_archetype_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "templates" / ARCHETYPES[0]
            path.mkdir(parents=True)
            (path / "metadata.json").write_text('{"archetype":"wrong"}')
            self.assertNotEqual(run_matrix(root)[0][1], 0)

    def test_malformed_metadata_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "templates" / ARCHETYPES[0]
            path.mkdir(parents=True)
            (path / "metadata.json").write_text("not-json")
            self.assertNotEqual(run_matrix(root)[0][1], 0)


if __name__ == "__main__":
    unittest.main()
```

`tests/test_propagation_dry_run.py`:

```python
import tempfile
import unittest
from pathlib import Path

from src.propagation_dry_run import proposals


class PropagationDryRunTests(unittest.TestCase):
    def test_proposes_update_without_modifying_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo-a"
            repo.mkdir()
            dockerfile = repo / "Dockerfile"
            dockerfile.write_text("FROM registry.example/base@sha256:OLD\n")
            before = dockerfile.read_bytes()
            rows = proposals(root, "registry.example/base@sha256:OLD", "registry.example/base@sha256:NEW")
            self.assertEqual(rows[0]["status"], "would-update")
            self.assertEqual(dockerfile.read_bytes(), before)

    def test_detects_conflicting_multiple_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo-a"
            repo.mkdir()
            (repo / "Dockerfile").write_text("FROM OLD\nARG BASE=OLD\n")
            self.assertTrue(proposals(root, "OLD", "registry.example/base@sha256:NEW")[0]["conflict"])

    def test_rejects_missing_digest_in_new_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                proposals(Path(tmp), "old", "registry.example/base:tag")

    def test_rejects_same_or_empty_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                proposals(Path(tmp), "same", "same")


if __name__ == "__main__":
    unittest.main()
```

Run from the `unit2-golden-path-lab/` directory:

```bash
python3 -m unittest discover -s tests -v
```

**Representative expected output (the authoring environment executed this suite):**

```text
Ran 44 tests
OK
```

The tests prove the local teaching validator's declared behavior against synthetic fixtures. They do not prove the selected CI provider's permission model, Kubernetes admission behavior, image build, registry trust, deployment, or runtime security.

##### Drift baseline contract

The scanner reports conformance and drift separately. Conformance answers whether the repository declares a supported path identity and passes required artifact/policy checks. Drift compares only files the platform explicitly marks as platform-managed; product-owned application additions are not automatically drift.

A synthetic `template-manifest.json` has this shape:

```json
{
  "managed_files": {
    "README.md": "<64-character-SHA256-of-the-approved-template-file>",
    "ci/reusable-workflow-reference.yml": "<64-character-SHA256-of-the-approved-template-file>"
  }
}
```

The hashes above are placeholders, not real evidence. Generate them from the approved template release. The scanner classifies each managed path as `clean`, `missing`, `unexplained-modification`, or `approved-customization` (the last requires an explicit `approved_overrides` entry in the synthetic metadata). It reports `not-assessed` when no manifest exists and `invalid-manifest` for malformed or unsafe paths. The `approved_overrides` metadata key is a teaching contract only; align its name, approval record, and audit trail with the actual repository/catalog standard **[VERIFY]**. The scanner never writes repositories. It still runs mandatory policy checks for repositories classified as `off-path` or `unsupported-version`; those rows retain their lifecycle classification and include `mandatory_findings`, so leaving the golden path is not a way to leave security controls.

#### Template tests and conformance

Test the template matrix across each archetype and optional feature combination. Required test types:

- **Generation/structure:** expected files and metadata are present.
- **Parameter/render matrix:** default, optional database, queue, GPU, and stateful variants where applicable; reject invalid combinations.
- **Negative variants:** plant an unsafe image, privileged container, missing resources, secret value, absent SLO, or invalid ownership metadata; each must be rejected by the relevant rule.
- **Snapshot tests:** compare stable generated outputs such as metadata and policy references; update snapshots only through reviewed changes.
- **Determinism/idempotency:** repeat generation with identical inputs and compare outputs where the engine supports deterministic generation.
- **Deployability:** optional Plat+Control kind deployment/smoke test after preflight. A successful generation is not a successful deployment.
- **Telemetry integration:** where optional deployment exists, confirm telemetry actually arrives and alerts are evaluated; files existing is insufficient.

A formal conformance definition for this unit is: a repository is **conformant** only when it declares a supported archetype and path version, includes all required artifacts for that archetype, passes all blocking checks, has required owner/catalog metadata, includes SLO/runbook evidence, and meets mandatory policy. A repo containing `Dockerfile`, `catalog-info.yaml`, or a template README but lacking declared path identity is **off-path**, not conformant.

The scanner must test:
1. A valid supported synthetic repository → conformant.
2. A repo with template-like filenames but no path identity → off-path.
3. A repo declaring an old/unsupported path version → nonconformant or explicitly unsupported.
4. A repo missing a required artifact → nonconformant.
5. A repo with policy failure → nonconformant.
6. Malformed metadata → invalid.
7. Repeated scan → identical sorted report.

A complete production scanner would also compare generated baseline snapshots or template provenance and classify drift by approved customization, intentional exception, and unexplained divergence. Unit 5 owns robust generated-repository update mechanisms; do not equate this compact Core scanner with full drift management.

#### Docs-as-code

Keep docs near the path and make them part of review. Minimum information architecture:

- `getting-started.md`: prerequisites, copy/generate, required inputs, first local check.
- `local-development.md`: local run/test, environment variables, no credentials.
- `deploy-and-observe.md`: delivery path, rollout, dashboards, alerts, telemetry verification.
- `runbook.md`: symptom, diagnosis, mitigation, escalation, rollback.
- `faq.md`: common errors and explanations.
- `support-and-escape-policy.md`: owners, support level, escalation, exception process.

A docs link checker should validate relative links; executable snippets should be tested where feasible. A broken link or stale command is a product defect. Keep the single source of truth close to the implementation; generate reference pages only when there is a clear maintenance benefit.

### 2.5 Level 3 — Advanced

#### Opinionation level and ADRs

Too little opinion leaves teams doing repeated work; too much opinion creates resistance and blocks legitimate workloads. Each opinion should be justified, documented, testable, and reversible. Record at least five Architecture Decision Records (ADRs):

**ADR-001 — Image and build defaults**
- Context: services need a repeatable hardened image baseline.
- Decision: use the M01-approved digest-pinned base, multi-stage build, non-root runtime, and locked dependencies.
- Alternatives: each team chooses its own base; mutable tags; one universal runtime image.
- Consequences: safer consistency, but base-image updates require coordinated propagation.
- Evidence/test: GP002/GP003 negative tests and M01 image build verification.
- Owner: platform image maintainer; product team owns application dependencies.
- Reversibility: change the approved base through a reviewed release and canary repositories.

**ADR-002 — Validation severity**
- Context: a new policy can produce false positives and block delivery.
- Decision: mandatory security controls block; lower-risk maturity checks may warn during a time-boxed rollout.
- Alternatives: block every rule immediately; warn forever.
- Consequences: staged adoption is easier, but warning debt must be tracked.
- Evidence/test: warning-mode report retains finding IDs; block-mode returns non-zero.
- Owner: platform policy owner with security reviewer.
- Reversibility: change severity through reviewed policy release; never downgrade mandatory controls without risk approval.

**ADR-003 — Archetype structure**
- Context: API, batch, streaming, serving, and notebooks have distinct operational lifecycles.
- Decision: maintain distinct archetype contracts with a shared core and tested optional add-ons.
- Alternatives: one broad template; one template per language/team.
- Consequences: clearer operations, with risk of template duplication.
- Evidence/test: matrix tests verify common metadata and archetype-specific requirements.
- Owner: platform developer-experience lead.
- Reversibility: merge/split archetypes after evidence and migration plan.

**ADR-004 — Escape-hatch policy**
- Context: legitimate workloads differ, but mandatory controls cannot disappear.
- Decision: allow documented custom path with owner, reason, review, support status, and expiry/review date.
- Alternatives: forbid all deviations; unrestricted bypass.
- Consequences: flexibility with governance overhead.
- Evidence/test: off-path fixture remains subject to mandatory security checks.
- Owner: platform owner plus security/SRE approvers.
- Reversibility: revise support level; do not retroactively erase recorded risk decisions.

**ADR-005 — Version and rollout policy**
- Context: shared template changes can affect many repositories.
- Decision: version template, reusable workflow, chart/overlay, policy bundle, and docs independently where their release cycles differ; pilot in synthetic canaries.
- Alternatives: one coupled version; unversioned latest.
- Consequences: compatibility matrix is more work but isolates change and rollback.
- Evidence/test: canary report and compatibility tests.
- Owner: platform release owner.
- Reversibility: rollback to last known compatible combination; migration policy details continue in Unit 9.

#### Default → reason → test → owner register

| Default | Source | Risk prevented / reason | Verification and negative test | Accountable owner |
|---|---|---|---|---|
| Digest-pinned approved base, multi-stage/non-root | M01 | Mutable or over-privileged runtime image. | GP002/003; negative fixture uses placeholder/tag. | Image maintainer |
| Reusable least-privilege CI, protected PR and CODEOWNERS | M02 | Excess workflow permissions and unreviewed changes. | GP005/006; remove permission/pin declaration. | CI platform owner |
| Resources, probes, PDB, PSS standards | M03 | Unbounded or unready workloads. | GP009/010/011; remove resources/probes or add privileged flag. | Runtime platform owner |
| Default-deny network/TLS declaration | M04 | Uncontrolled service communication. | GP012; remove network-control reference. | Network/security owner |
| Database/backup only when stateful | M05/M13 | Unnecessary dependencies or unrecoverable state. | GP019; mark stateful without backup tier. | Data platform owner |
| Shared Helm/Kustomize components | M06 | Divergent deployment conventions. | render/schema checks; remove required component reference. | Packaging owner |
| IaC module/guardrails; Crossplane concept boundary | M07 | Unsafe or bespoke provisioning. | approved module reference; detailed implementation deferred. | Infrastructure platform owner |
| GitOps promotion/digest rollout/rings | M08 | Untraceable deployment and unsafe fleet release. | promotion declaration and digest check. | Delivery owner |
| Secret references/workload identity | M09 | Credential leakage and static secret sprawl. | GP016; benign planted test secret pattern. | Identity owner |
| SLO, alerts, runbook, ORR | M10 | Service cannot be operated predictably. | GP013; remove SLO/runbook. | Service owner with SRE |
| Instrumentation/dashboard/telemetry conventions | M11 | Unknown service behavior. | artifact check plus optional live telemetry check. | Observability owner |
| SBOM/provenance/signing evidence | M12 | Untraceable or untrusted build artifacts. | GP017; remove evidence reference. | Supply-chain owner |
| Backup/restore, DR tier, checkpointing, model hash | M13 | Data/model recovery or integrity gaps. | stateful and model artifact fixture tests. | Data/ML platform owner |
| Fleet rollout rings and regional overlays | M14 | Broad change blast radius. | canary rollout plan and ring metadata review. | Fleet operations owner |
| Cost labels, quotas, priority, scaling ceilings, idle cull | M15 | Unowned or unbounded resource consumption. | GP008/015; remove cost/quota fields. | FinOps/platform owner |

#### Versioning and compatibility

Track independently where appropriate:
- template repository release;
- reusable CI workflow version;
- Helm chart/library or Kustomize component version;
- policy bundle version;
- documentation version;
- optional scaffolder/template-engine version.

A compatibility matrix is more useful than one ambiguous “platform version.” Example:

| Archetype | Template | CI workflow | Deployment component | Policy bundle | Status |
|---|---|---|---|---|---|
| API/inference | 1.0 | 2.x [VERIFY] | 1.x [VERIFY] | 1.0 | Example combination; validate locally |
| Batch/ETL | 1.0 | 2.x [VERIFY] | 1.x [VERIFY] | 1.0 | Example combination; validate locally |
| Model-serving | 1.0 | 2.x [VERIFY] | 1.x [VERIFY] | 1.0 | Example combination; validate locally |
| Streaming | 0.x | unknown | unknown | 1.0 | Not GA; unknowns must remain explicit |
| Notebook | 0.x | unknown | not applicable | 1.0 | Not GA; unknowns must remain explicit |

These are illustrative version labels, not released artifacts or compatibility claims. A real release needs changelog, migration notes, test evidence, named owners, compatibility/rollback policy, and a few synthetic canary repositories/teams before broad rollout. Detailed deprecation windows, compatibility policy, and governance belong to Unit 9.

#### Maintenance and security patch propagation

Assign an owner and update cadence to base images, CI actions, charts, policies, and generated docs. Update bots are awareness-only; exact product, status, and behavior are **[VERIFY]**. Pinning improves repeatability but stale pins can preserve vulnerable dependencies; freshness without review can introduce breaking or malicious changes.

CVE propagation workflow:

1. Security/image owner approves a patched base-image digest.
2. Platform maintainer updates the template and records source, reason, and release.
3. A bounded dry-run identifies synthetic repositories containing the old reference.
4. Generate reviewed update proposals/PRs; do not mass-write or auto-merge.
5. Each repository runs CI, policy, and application tests.
6. Canary repositories merge first; observe failures and conflicts.
7. Expand in rollout rings and re-run conformance.
8. Record completion and unresolved exceptions.

`time-to-propagate` is a candidate operational measure: time from approved patch availability to verified adoption across a defined eligible repository population. Define start/end, exclusions, and denominator. Do not invent a target.

Use the dry-run script:

```bash
cd unit2-golden-path-lab
python3 src/propagation_dry_run.py examples \
  --old 'registry.example/base@sha256:OLD_APPROVED_DIGEST' \
  --new 'registry.example/base@sha256:NEW_APPROVED_DIGEST'
```

Representative expected output (depends on the synthetic Dockerfiles):

```json
[
  {
    "file": "examples/generated-api/Dockerfile",
    "status": "would-update",
    "old": "registry.example/base@sha256:OLD_APPROVED_DIGEST",
    "new": "registry.example/base@sha256:NEW_APPROVED_DIGEST",
    "conflict": false
  }
]
```

The script never writes files. It refuses `--apply`. A real update PR system is Unit 5 scope.

#### Parameters, forks, separate templates, and add-ons

- **Parameter:** common variation with the same lifecycle, such as language/runtime, storage class, queue toggle, or GPU requirement.
- **Separate template:** materially different lifecycle, risk boundary, or operating evidence, such as batch vs notebook.
- **Fork:** exceptional case where a team owns a genuinely divergent lifecycle; record maintenance and security responsibility explicitly.
- **Composable add-on:** optional capability applied to a compatible path, such as database, queue consumer, or GPU. Test repeat application, ordering, conflicting values, and removal behavior.

Avoid template explosion. If every small choice creates a separate template, maintenance multiplies. If one template has dozens of unrelated switches, the path becomes difficult to understand. Measure actual variation demand and use a shared core with a small number of archetypes.

#### Security, ORR, cost, observability, and path performance

A vulnerable template can replicate a defect across all newly generated services. Protect template source with reviewed changes, pinned dependencies/actions, provenance and signed releases where supported, generated-output scans (SAST, secret, policy), and no secrets in templates. Trust boundaries include template source, generation hooks, CI actions, generated code, registry, GitOps repository, and deployment controllers. Treat generation hooks and parameters as untrusted input; avoid arbitrary shell evaluation and validate allowed values.

The path should generate much of the evidence needed for an ORR: SLO file, alert pack, runbook skeleton, dependency declarations, backup policy for stateful workloads, and a load-test harness stub where appropriate. A stub is not proof of load capacity or production readiness. `promtool` and load-test integrations are optional/version-sensitive **[VERIFY]**; use official docs and pin tool versions before adopting them. M10/M11/M13 own reliability, telemetry, and recovery mechanisms.

Cost defaults include M15 labels, quotas, priority classes, optional CI capacity/cost estimator, and HPA/KEDA ceilings where used. Do not invent resource baselines or claim defaults are right-sized without workload measurements. Higher availability or performance can increase cost; aggressive cost reduction can weaken latency, resilience, or recovery. Make the trade-off explicit.

Observability by default includes instrumentation hooks, dashboards-as-code, alert/SLO artifacts, and telemetry linting. Distinguish (a) file present, (b) configuration valid, and (c) telemetry actually arriving and alerting. Tests must not report level (c) based on level (a).

Measure path performance: local validation duration, CI duration added by checks, feedback latency, and failure/retry rate. Keep fast local checks separate from slower integration tests where reasonable. Treat developer time and feedback delay as an experience budget, not a universal target. Record laptop-specific values.

#### Data/ML-specific design

A notebook should be a route to reproducible work, not a credential-bearing production artifact. Use a reproducible environment with lockfiles/hashes (M01 Unit 3), image allow-list, workload identity and secret references (M09), quota-limited/ephemeral workspace, idle-culling (M15), output stripping and size limits, and declared owner/cost. The notebook-to-production path should preserve code, dependency versions, experiment metadata, model/data version, and tests while moving reusable logic into a pipeline or serving package. Do not force every data scientist into microservice ceremonies.

Experiment tracking/model registry conventions and artifact hash/version traceability connect to M13 Unit 5/M12. Data contracts/schema checks connect to M08 Unit 12. Dataset/feature definitions can be code where appropriate. A small synthetic notebook workflow might declare:

```yaml
experiment:
  name: churn-baseline
  code_path: src/train.py
  environment_lock: environment/requirements.lock
  dataset_reference: synthetic://training-sample-v1
  model_output: artifacts/model-placeholder
  owner: team-ml
  credentials: none
```

This is a teaching description, not a real registry schema. Validate exact schemas against the chosen tool **[VERIFY]**. The Core exercise converts this description into a reproducible pipeline manifest and checks for credential fields and notebook outputs; it does not train a real model or use real data.

#### Trade-off table

| Choice | Benefits | Costs/risks | Decision rule |
|---|---|---|---|
| One broad template vs archetype templates | One template reduces duplication; archetypes express lifecycle clearly. | Broad template becomes conditional maze; separate templates can drift. | Separate when lifecycle/risk differs; share tested core. |
| Parameters vs forks | Parameters preserve shared updates; forks allow autonomy. | Too many parameters confuse; forks drift. | Parameterize common variation; fork only with named ownership. |
| Strict blocking vs warning | Blocking prevents known unsafe state; warnings ease rollout. | False positives can halt work; warnings can become ignored debt. | Block mandatory controls; time-box lower-risk warnings. |
| Pinned dependencies vs freshness | Pins improve reproducibility. | Stale pins preserve vulnerabilities. | Pin and maintain an update/patch process. |
| Thin docs/templates vs richer tooling | Low maintenance and easy to inspect. | More manual steps remain. | Add tooling only for validated repeated friction. |
| Default path vs escape hatch | Default gives consistency; escape supports legitimate differences. | Too strict causes bypass; too loose weakens support. | Preserve mandatory guardrails and document support level. |
| Core checks vs cluster integration | Core is cheap, repeatable, accessible. | Static checks cannot prove runtime behavior. | Core required; cluster integration optional and separately evidenced. |

#### Developer adoption and when not to build a path

Make the path the easiest supported route: few inputs, safe defaults, fast feedback, understandable errors, useful docs, and a clear support contact. Migration kits and “path coach” office hours can help existing services; any attendance or adoption data in this lab is synthetic. Alternatives include documentation-only, shared libraries, internal CLI, or workload specifications (Score/OAM-style concepts are awareness-only and **[VERIFY]**). A golden path may not justify its maintenance cost when there are very few services, requirements change rapidly, workloads are highly differentiated, or no team can own it.

**Design exercise:** choose one archetype for a first release; identify five defaults and their source modules; decide three parameters and one escape hatch; list non-goals; define a canary and rollback; defend how you will prove conformance and telemetry integration. Every assumption must be labelled and assigned a validation method.

### 2.6 Level 4 — Expert

#### Ownership, funding, lifecycle, and quality bar

A golden-path program needs an accountable product owner, technical maintainers, security/SRE reviewers, documentation owner, maintenance budget, roadmap, contribution policy, and support expectations. The platform team patches templates, shared workflows, policies, and platform-owned defaults. Product teams patch their application logic and team-owned customizations. Generated repositories need a clear ownership split: platform fixes are proposed to the source template and propagated through reviewed updates; teams remain responsible for local code and conflicts.

Lifecycle responsibilities:

1. **Proposal/RFC:** state user problem, target archetype, non-goals, source-module defaults, support cost, risks, and evidence.
2. **Pilot:** select design partners/canary repositories, run matrix and negative tests, collect feedback, and define rollback.
3. **GA:** publish supported combinations, owner, docs, support boundary, release notes, and quality evidence.
4. **Maintain:** patch dependencies, respond to incidents, test upgrades, monitor drift and conformance.
5. **Deprecate:** communicate, offer migration, track exceptions, and retire only after governance review. Detailed deprecation mechanics are Unit 9.

Quality bar includes template/policy tests, docs, path generation/CI reliability objectives, security review, readable/accessibly structured docs, compatibility evidence, rollback plan, and a named on-call/escalation owner for shared failures. A successful generation command is not enough.

#### Metrics without false causality or surveillance

Candidate measures:
- percentage of eligible services on supported paths, by archetype;
- time-to-first-deploy using a defined start/end boundary;
- conformance rate and reason categories;
- template version spread and upgrade lag;
- time-to-propagate approved security fixes;
- escape-hatch rate and reasons;
- developer satisfaction gathered with appropriate privacy and context;
- validation/CI time and failure/retry rate.

In this lab, all teams, services, adoption, satisfaction, and timings are synthetic or learner-specific. Metric movement does not prove causality. Avoid individual developer leaderboards or surveillance. Aggregate appropriately, document purpose, access, retention, and limitations. Full measurement design belongs to Unit 8.

#### Fleet, multi-region, compliance, legacy migration, and organization

Path releases may target multiple clusters or regions. Use M14 rollout rings, region-specific overlays, and cluster-vending integration where applicable. A fleet-wide template/policy update must be staged; no multiple clusters are required in this lab. Keep region-specific differences explicit and tested rather than hiding them in unreviewed overrides.

A path can produce audit evidence: SBOM, provenance, scan results, policy reports, SLO docs, and declared DR tier. “Audit-ready by construction” is a design aspiration, **not compliance certification**. Evidence still needs review for scope, authenticity, retention, and applicable control requirements.

Legacy migration should be incremental: identify a high-risk or high-maintenance service, map its existing behavior, introduce path-compatible components, migrate one slice, validate, and retain rollback. Codemods and bots are awareness topics; exact tool behavior is **[VERIFY]** and detailed update mechanisms belong to Unit 5. Prioritize by risk, cost, and feasibility rather than forcing every service at once.

The platform team owns shared path contracts; product teams own service behavior after generation. Inner-source contributions can let teams propose improvements, but the platform owner remains accountable for review, compatibility, and release. A champion network and office hours can improve feedback without creating governance bureaucracy.

#### Eight synthetic failure cases

All cases are synthetic teaching scenarios. Diagnose each as symptom → hypothesis → test/evidence → root cause → fix → prevention.

| Synthetic symptom | Hypothesis and evidence/test | Likely root cause | Containment, fix, and prevention |
|---|---|---|---|
| Template default disabled TLS verification and was copied to many services. | Search template and generated repos; inspect runtime config and network tests. | Security-sensitive default lacked review and negative tests. | Stop generation/release; identify affected repos; restore verified TLS behavior; scan generated services; add a planted negative test, security review, and signed/versioned release. |
| Upgrade broke generated repos with local changes; teams stopped updating. | Compare template release notes, local diffs, and failed update attempts. | No compatibility contract, migration guidance, or conflict support. | Pause rollout; publish affected versions and workaround; test migration on canaries; add update guidance and ownership boundaries; Unit 5 update tooling and Unit 9 governance. |
| Dashboard counted any repo containing template files as “on path.” | Sample reported repos; inspect declared path identity/version and policy results. | File-presence proxy was used instead of conformance contract. | Correct report; reclassify lookalikes as off-path; require declared path identity, required artifacts, and passing blocking checks; add false-positive tests. |
| Data scientists bypassed path and ran notebooks with embedded credentials. | Inspect authorized sample notebooks, access logs, and user journey; do not expose real secrets. | Path was too burdensome or lacked an appropriate notebook archetype; credential guardrails were weak. | Revoke/rotate any exposed credential through approved incident process; contain access; add notebook path, workload identity, output/secret checks, and user research. |
| CI checks took 25 minutes and teams skipped them through an admin bypass. | The 25-minute value is part of this synthetic scenario, not a benchmark; measure per-check duration and bypass records. | Slow checks were not tiered; bypass path was too powerful. | Remove broad bypass; separate fast local checks from slower integration checks; cache safely; retain mandatory controls; monitor feedback latency. |
| Policy errors were cryptic and support tickets increased. | Review messages and ticket categories; run error-message quality tests. | Diagnostics lacked rule, reason, fix, and documentation pointer. | Improve messages; add tests for all four elements; publish examples and office hours; monitor recurring confusion. |
| Template tests checked generation only, not deployability. | Compare test suite with optional deployment/smoke evidence and runtime telemetry. | Generation success was mistaken for service correctness. | Label evidence layers; add optional Plat+Control deployment/smoke test and telemetry verification; keep Core honest about limits. |
| Template required a database for every service, including batch jobs that did not need one. | Inspect generated dependencies and workload requirements. | Over-generalized template forced unnecessary architecture. | Remove database from core; create tested opt-in add-on; add batch fixture asserting no database by default; document stateful backup only when needed. |

#### Safe incident runbook

1. **Detect:** template, policy, or workflow failure rises above a locally defined threshold, or a team reports unsafe generated output.
2. **Stop propagation:** pause template release, update proposals, or rollout ring; do not delete evidence.
3. **Scope:** identify path version, template/workflow/policy version, archetype, generated repositories, and affected runtime environments.
4. **Contain:** block new generation or unsafe release; preserve service operation where safe; use approved rollback/exception process.
5. **Fix:** patch source template/policy, add regression and negative tests, review security impact.
6. **Validate:** generate each archetype, run full policy/test matrix, inspect canary output, and optionally deploy/smoke-test.
7. **Resume in rings:** canary first, then expand only with passing evidence and owner approval.
8. **Communicate/postmortem:** publish scope, workaround, owner, next update, root cause, prevention, and follow-up actions.

### 2.7 SRE lens

A golden path is a shared dependency: a defect can affect many generated services. Candidate reliability objectives include template generation/check success and update propagation success, but detailed SLO design belongs to Unit 8. Define eligible attempts, successful result, exclusions, time window, and error budget before setting targets; no target is asserted here.

Distinguish evidence layers:

1. **Generation success:** files were created.
2. **Static validation success:** repository checks passed.
3. **Build success:** image/build artifact was produced using approved inputs.
4. **Deployment success:** desired workload reached the declared runtime state.
5. **Runtime success:** service behavior, telemetry, SLOs, and alerts function under relevant conditions.

Do not report level 1 or 2 as proof of levels 4 or 5.

Use canary repositories and rollout rings to limit shared-template blast radius. Track local validation duration and CI time on the learner's machine; measure yours. Shared CI can consume platform compute and create developer wait time, so split fast checks from slower integration checks where safe. Do not weaken mandatory controls merely to improve latency.

**Runbook summary:** detect → stop propagation → identify affected path/version/repos → contain → fix → validate → resume in rings → communicate/postmortem. See the detailed sequence in Unit 2.6. Backups and recovery align with M13; fleet rollout with M14.

### 2.8 Security lens

| Threat | Control | Negative test / review evidence | Limitation |
|---|---|---|---|
| Vulnerable template/default replicated across services | Protected source, reviewed releases, security owner, signed release where supported, generated-output scanning. | Plant insecure setting in isolated fixture; policy test must fail. | Static scan may miss semantic or runtime vulnerabilities. |
| Unsafe/unpinned generation hooks/dependencies | Avoid arbitrary shell hooks; pin reviewed dependencies; constrain inputs; inspect provenance. | Reject unpinned dependency or unexpected hook declaration in review. | Exact template-engine semantics are Unit 5 and **[VERIFY]**. |
| Secrets in templates/notebooks | No secret values; M09 identity/reference pattern; notebook output stripping and scans. | Plant benign credential-shaped fixture and ensure GP016/GP020 catches it. | Pattern scans can have false positives/negatives; use approved secret scanning too. |
| Over-privileged CI/bot/portal identity | Least privilege, short-lived scoped identity, separate duties, reviewed permissions. | Inspect permission declaration; attempt unauthorized operation in isolated test. | Local text checks do not prove provider-side permissions. |
| Manifest injection/hostile parameter values | Schema/allow-list validation, safe serialization, no shell interpolation of user values. | Submit invalid type/path characters to a local validator; reject before rendering. | Core lab does not run a production template engine. |
| Policy bypass/exception abuse | Narrow approval, owner/reason/expiry, immutable audit record, mandatory controls remain. | Verify an expired exception does not suppress a mandatory rule. | Exception process needs organizational enforcement. |
| Supply-chain compromise | M12 signing/SBOM/provenance, pinned dependencies/actions, generated-output scans, trusted registry and GitOps chain. | Remove required evidence or use unpinned test reference; reject. | Evidence must be verified and retained; file presence alone is not proof. |
| Off-path escape without control loss | Same mandatory identity/security/compliance guardrails; custom path metadata and support boundary. | Off-path fixture with planted secret/privilege violation still fails mandatory check. | Custom workloads may require additional threat modeling. |

Trust boundaries include template source, generation hooks, CI actions, generated code, artifact registry, GitOps repository, and deployment controllers. Do not include credentials, real tokens, cluster-admin bot identities, unchecked user input, or auto-merge behavior in this lab. Unsafe defaults appear only in isolated fixtures labelled `ANTI-PATTERN — DO NOT COPY`.

### 2.9 Production checklist

- [ ] Named platform owner, maintainers, budget, support level, and escalation route.
- [ ] Each default links to source module, reason, negative test, and owner.
- [ ] Approved base-image digest and dependency-lock policy are used.
- [ ] CI workflow is reusable, least-privilege, pinned, and reviewed.
- [ ] API, batch, model-serving, streaming, and notebook archetypes are documented.
- [ ] Optional database/queue/GPU/stateful features are not forced on every workload.
- [ ] At least 15 rules have rationale, scope, severity, positive/negative tests, and actionable messages.
- [ ] Warning/blocking behavior and time-limited exception process are explicit.
- [ ] Generated output is tested; template generation alone is not treated as deployability.
- [ ] Unsafe planted fixtures are rejected.
- [ ] Conformance requires declared path/version, required artifacts, and passing blocking checks.
- [ ] Lookalike/off-path repositories are not counted as conformant.
- [ ] Documentation covers getting started, local run, deploy/observe, runbook, FAQ, support/escape.
- [ ] SLO/runbook and ORR evidence are present and service-specific.
- [ ] Security/supply-chain controls and generated-output scanning are reviewed.
- [ ] Cost labels, quota/priority metadata, and stateful backup declarations are correct.
- [ ] Catalog metadata is structurally checked against the selected schema.
- [ ] Template/workflow/chart/policy/docs compatibility is recorded.
- [ ] Canary, rollout rings, rollback, and patch propagation are tested.
- [ ] Notebook safety, reproducible environments, output stripping, and no-credential policy are enforced.
- [ ] Telemetry files and actual telemetry arrival are assessed separately.
- [ ] CI latency and local resource footprint are measured, not invented.
- [ ] Privacy and aggregate measurement purpose/retention/access are documented.
- [ ] Off-path services retain mandatory guardrails.
- [ ] Cleanup and teardown are verified; no cloud or paid service is required for Core.

### 2.10 Hands-on lab set

All labs are **Plat-Core-first** and use local files, Python standard library, and synthetic repositories. Approximate footprint: low, but actual disk/CPU/RAM depend on the learner's laptop and file volume—measure yours. No services start in Core; Python processes run only for the duration of each command. Optional Plat+Control is separate and may start a local cluster/controller; perform resource preflight and stop them explicitly. No local Git server, cloud account, paid product, or real SCM token is required.

| Lab | Goal and steps | Expected evidence | Cleanup / stretch |
|---|---|---|---|
| **LAB-01 — Build three archetype paths** | Stack: Plat-Core. Create API/inference, batch/ETL, and model-serving template directories plus concise streaming/notebook variants. Copy generated API/batch/model-serving examples. Add metadata, CI reference, docs, SLO/runbook, security and cost artifacts. Run tests and inspect ownership. | Five archetype trees; three generated sample repositories; default register; no fake digest or secret. | Stop: no services. Remove only generated sample directories to reset; verify templates remain. Safe rerun: copy into empty output dirs. Stretch: add a database/queue/GPU option with conflict tests. |
| **LAB-02 — Policy suite and template test matrix** | Stack: Plat-Core. Add the 20-rule contract, `validate_repo.py`, planted unsafe fixtures, positive/negative tests, message-quality tests, and parameter matrix. Run validator in block and warn modes. | Rule inventory, non-zero blocking exit, warning report retaining findings, negative test report, stable snapshots. | No service teardown. Delete generated reports/temporary fixtures only. Stretch: add a verified YAML parser or optional hadolint/kubeconform after version verification. |
| **LAB-03 — Conformance and default/option/escape** | Stack: Plat-Core. Create synthetic repos: conformant, lookalike, old version, missing artifact, policy failure, malformed metadata, off-path. Run scanner and test deterministic output. Write support/exception policy and verify off-path mandatory checks. | Per-service/per-archetype report, false-positive tests, policy document, exception register. | No services. Reset synthetic fixture directory and rerun. Stretch: classify drift reasons and approved customizations. |
| **LAB-04 — Patch propagation, DX, notebook-to-pipeline, docs** | Stack: Plat-Core. Run dry-run base-image update; measure time-to-first-deploy proxy, step count, local check/CI time against Unit 1 baseline using same boundaries; create synthetic notebook workflow manifest, strip outputs, check credentials/size; add docs link/snippet tests. | Dry-run report with conflicts, learner-measured DX sheet, notebook-to-pipeline artifact, docs-as-code check output. | Dry-run writes nothing. Verify hashes/working tree unchanged; no service teardown. Stretch: optional kind/GitOps smoke and telemetry arrival check after preflight. |
| **LAB-05 — ADRs, operating model, failure drill** | Stack: Plat-Core. Complete five ADRs, compatibility matrix, ownership/support/RACI, lifecycle proposal, rollout/rollback, and analyze all eight synthetic failure cases. | Five ADRs, compatibility matrix, owner register, support/escape policy, failure analysis, final audit. | No services. Retain evidence; remove only temporary output. Stretch: conduct a real design review only with authorized stakeholders and consent-appropriate notes. |

#### Exact Core commands and repeatability

From WSL2 Ubuntu or native Linux:

```bash
mkdir -p unit2-golden-path-lab/{templates,examples,policies,src,tests,docs,artifacts,decisions,synthetic-data}
cd unit2-golden-path-lab
python3 --version
```

Create the files shown in this lesson under their stated paths. For each generated sample repository, use `metadata.json` and required artifacts. Then run:

```bash
python3 -m unittest discover -s tests -v
python3 src/validate_repo.py examples/generated-api --mode block
python3 src/validate_repo.py examples/generated-api --mode warn --json
python3 src/scan_conformance.py examples --output artifacts/conformance-report.json
python3 src/test_template_matrix.py .
python3 src/propagation_dry_run.py examples \
  --old 'registry.example/base@sha256:OLD_APPROVED_DIGEST' \
  --new 'registry.example/base@sha256:NEW_APPROVED_DIGEST'
```

Commands assume the scripts are placed at the paths shown and `scan_conformance.py` can import `validate_repo.py` from the same `src` directory. Run the scanner with `PYTHONPATH=src` if invoking it from a different working directory:

```bash
PYTHONPATH=src python3 src/scan_conformance.py examples
```

Representative expected output (not executed; exact findings depend on the files you create):

```text
Python 3.x.y
api-inference: PASS (code=0)
batch-etl: PASS (code=0)
model-serving: PASS (code=0)
streaming-consumer: PASS (code=0)
notebook-workspace: PASS (code=0)
```

The matrix output above is only representative of a completed set of template metadata files; it does not mean all policy checks passed. The validator may emit blocking findings for the intentionally unresolved image digest, incomplete metadata, or missing artifacts. Fix each finding with approved values and evidence rather than suppressing it.

**Teardown verification:** Core starts no background services. Confirm no lab process remains (commands are foreground), inspect the lab directory, and verify dry-run did not change Dockerfiles. Optional cluster work must separately list and stop its cluster/controller; do not run it unless preflight confirms resources. Safe rerun means scripts do not mutate source repositories, reports are deterministic, and sample generation targets clean directories.

**Fidelity caveats:** all repositories, teams, users, path adoption, failure cases, and sample metadata are synthetic. Local timings are laptop-specific. Static checks are deliberately limited and do not replace image builds, schema validation, admission policy, deployment, runtime telemetry, or security review. No result is an industry benchmark or real-user finding.

#### Required exercise-family coverage

1. Three full Core archetype templates (API/inference, batch/ETL, model-serving) plus concise streaming/notebook designs.
2. Policy suite of 15+ rules, warning/block modes, actionable errors, exceptions, and planted unsafe tests.
3. Template test harness with matrix, snapshots, determinism, negative variants, optional cluster smoke.
4. Conformance scanner with per-service/archetype report and false-positive tests.
5. Default/option/escape policy with guardrails, owner, exception and graduation process.
6. Dry-run security-patch propagation and conflict report; no fleet writes.
7. DX comparison against Unit 1 baseline with consistent boundaries and measured laptop-specific values.
8. Notebook-to-pipeline manifest and notebook credential/output policy.
9. Five ADRs with evidence, owner, alternatives, and reversibility.
10. Docs-as-code structure and link/snippet checks.

### 2.11 Self-check questions

1. **How is a golden path different from a golden cage?**  
   **Answer:** A path is supported, documented, convenient, and has governed alternatives; a cage blocks legitimate variation and offers no useful escape.  
   **Why the wrong answer is tempting:** strict uniformity appears easier to operate, but unsupported bypasses can be less safe.

2. **Should a queue consumer be a parameter, fork, or separate template?**  
   **Answer:** Usually an optional add-on/parameter if lifecycle and operational contract remain compatible; separate it if backpressure, replay, scaling, and support needs change materially.  
   **Why tempting:** one template seems simpler, but too many conditional branches become a maze.

3. **Why not enforce every new policy as blocking on day one?**  
   **Answer:** A lower-risk rule may have false positives or migration cost; warn mode can be time-boxed while measuring and fixing. Mandatory security controls remain blocking.  
   **Why tempting:** immediate blocking looks rigorous, but poor diagnostics can create unsafe bypass pressure.

4. **A repository contains `Dockerfile`, `catalog-info.yaml`, and a README. Is it conformant?**  
   **Answer:** No. It needs declared path identity/version, required archetype artifacts, owner metadata, SLO/runbook, and passing blocking checks.  
   **Why tempting:** file names look like evidence, but they can be copied without following the path.

5. **How should a base-image security patch propagate?**  
   **Answer:** Approve the digest, update template, dry-run affected repos, create reviewed update proposals, run CI, canary, expand in rings, and re-check conformance.  
   **Why tempting:** mass editing is fast, but it hides conflicts and creates broad blast radius.

6. **CI validation becomes slow. Should checks be removed?**  
   **Answer:** Measure per-check duration and feedback delay; keep fast local checks separate from slower integration checks, optimize safely, and retain mandatory controls.  
   **Why tempting:** shorter CI is visible, but deleting controls can increase risk.

7. **A vulnerable default was copied into many generated services. Where do you fix it?**  
   **Answer:** Fix the source template/policy and also identify and remediate already-generated repositories; add regression tests and a propagation plan.  
   **Why tempting:** fixing only the source protects future generation but leaves existing copies vulnerable.

8. **How should a notebook become a production pipeline?**  
   **Answer:** Preserve code, lockfile, experiment metadata, data/model versions, and tests; move reusable logic into a pipeline package; remove outputs and credentials; use approved identity and artifact traceability.  
   **Why tempting:** simply scheduling the notebook may retain hidden state, credentials, and non-reproducible dependencies.

### 2.12 Evidence artifacts

Retain these exact learner deliverables under `unit2-golden-path-lab/`:

- `templates/api-inference/`, `templates/batch-etl/`, `templates/model-serving/`, `templates/streaming-consumer/`, `templates/notebook-workspace/`.
- `examples/generated-api/`, `examples/generated-batch/`, `examples/generated-model-serving/`.
- `artifacts/default-register.md` with default → source → reason → test → owner.
- `policies/rules.json` or equivalent documented 15+ rule catalog.
- `policies/planted-unsafe-corpus/` with benign anti-pattern fixtures.
- `src/validate_repo.py`, `src/scan_conformance.py`, `src/test_template_matrix.py`, `src/propagation_dry_run.py`.
- `tests/test_validate_repo.py`, `tests/test_conformance.py`, `tests/test_template_matrix.py`, `tests/test_propagation_dry_run.py`.
- Positive/negative test evidence, actionable-message quality tests, and deterministic reports.
- `artifacts/conformance-report.md` or JSON with per-service/archetype status and drift reason.
- `artifacts/compatibility-matrix.md`.
- `docs/getting-started.md`, `docs/local-development.md`, `docs/deploy-and-observe.md`, `docs/runbook.md`, `docs/faq.md`, `docs/support-and-escape-policy.md`.
- Default/option/escape policy and exception/graduation process.
- Dry-run patch-propagation report and conflict analysis.
- `artifacts/developer-experience-measurement.md` using the Unit 1 baseline boundary.
- `artifacts/notebook-to-pipeline.md` with synthetic manifest and credential/output checks.
- Five ADRs: `ADR-001-image-and-build-defaults.md`, `ADR-002-validation-severity.md`, `ADR-003-archetype-structure.md`, `ADR-004-escape-hatch-policy.md`, `ADR-005-version-and-rollout-policy.md`.
- Eight failure-case analyses and the final authoring audit.

Do not store secrets, real developer records, credentials, real interview notes without authorization, or real customer data. Clearly label all synthetic artifacts.

### 2.13 Common interview and design-review questions

**1. How do you distinguish a golden path from a template or a golden cage?**  
A template is a starting artifact; a golden path is the maintained end-to-end developer journey with validation, delivery integration, observability, support, ownership, and upgrades. A golden cage blocks legitimate alternatives and has no useful escape. A good path is opinionated for documented reasons, tested, supported, and allows governed variation while preserving mandatory guardrails.

**2. How would you choose between parameters, separate archetype templates, and forks?**  
Use parameters for common variations that preserve lifecycle and operational contract. Use separate archetypes when workload lifecycle, failure semantics, risk, or evidence differ. Use forks only for justified divergence with named ownership and an explicit maintenance/security burden. Prefer a shared core and tested add-ons; avoid both a conditional mega-template and uncontrolled template proliferation.

**3. How do you prove a golden path is secure rather than merely claiming secure defaults?**  
Trace every default to an owning module and risk rationale; require positive and negative tests; scan generated output; pin and review dependencies/actions; verify image digest, least-privilege CI, identity references, policy and supply-chain evidence; test exception behavior; and validate deployment/admission/runtime separately. A local file check is not proof of provider-side permissions or runtime security.

**4. How would you safely propagate a breaking template/security update across repositories?**  
Approve and version the source change, publish changelog/migration notes, identify affected versions/repos with a dry run, create reviewed update proposals, test conflicts and compatibility, canary a few repositories, then expand in rollout rings with rollback and conformance re-checks. Never mass-edit or auto-merge across the fleet from the Core lab.

**5. How would you measure conformance and developer value without gaming metrics or surveilling individuals?**  
Define conformance as declared supported path/version plus required artifacts, ownership/catalog metadata, SLO/runbook evidence, and passing blocking policies. Measure eligible-service adoption, time-to-first-deploy, conformance reasons, version spread, patch propagation, escape reasons, support demand, and aggregated satisfaction with defined cohorts and boundaries. Do not count template-like files as conformance or rank individual developers.

### 2.14 Sources and verification notes

#### Scope authority and source hierarchy

The supplied M16 syllabus-generation prompt and repository tree are the scope authority for this lesson. M01–M15 are the mechanism sources; consult the relevant module for exact repository standards, approved defaults, and test contracts before implementing a production path. The Unit 1 lesson is the immediate conceptual prerequisite.

#### Official references to verify before implementation

- Docker documentation for Dockerfile/build best practices, multi-stage builds, and image references: use the current official Docker documentation; verify exact features and recommended syntax for the installed engine.
- Kubernetes documentation for workloads, probes, resources, Pod Security Standards, NetworkPolicy, and workload security: verify API versions and cluster support.
- Helm documentation and Kustomize documentation for chart/library and overlay behavior: verify exact versions and commands.
- GitHub Actions security documentation only if GitHub Actions is the chosen CI platform; verify action pinning and permission syntax against the current official docs. Otherwise use the selected CI provider's official security documentation.
- GitOps controller documentation only if a controller is selected; verify API versions, promotion semantics, and rollback behavior.
- Policy tool documentation only if adopted; verify syntax, version, and enforcement semantics. This lesson's Python rules are tool-independent.
- Backstage catalog documentation only in Unit 4; verify entity schema and annotation conventions.
- Template engine documentation only in Unit 5; verify hooks, rendering, update, and idempotency semantics before use.
- Team Topologies, Spotify/Netflix historical attribution, and any “golden path” origin claim must be checked against primary/authoritative sources before attribution.

No external source versions, command flags, action SHAs, image digests, schema fields, benchmark values, adoption statistics, or historical origin claims are asserted as verified in this lesson. Exact CI workflow syntax, Kubernetes YAML schema, catalog schema, policy-engine syntax, and optional tool integrations are **[VERIFY]** items. The sample catalog YAML is illustrative only. The Dockerfile digest is intentionally a placeholder and must be replaced with an approved value.

#### `[VERIFY]` register

| Item | Why verification is required | Exact verification task |
|---|---|---|
| Approved base-image reference/digest | Organization-specific and security-sensitive. | Obtain current approved digest from M01 image program; validate signature/provenance as required. |
| CI reusable workflow path, action SHAs, permissions | Provider-specific and version-sensitive. | Check selected provider's official docs and M02 maintained workflow. |
| Helm/Kustomize syntax and versions | APIs and chart behavior can change. | Check official docs and M06 supported versions. |
| Kubernetes API/schema and policy semantics | Cluster version and admission configuration vary. | Validate against target cluster version and M03/M04/M12 standards. |
| `catalog-info.yaml` schema/annotations | Catalog implementation-specific. | Verify in Unit 4 against the selected catalog version. |
| Template hooks/update behavior | Engine-specific. | Verify in Unit 5 before enabling generation hooks or update automation. |
| Update bot availability/behavior | Product status and configuration can change. | Consult official product documentation and security review. |
| `promtool`, load-test, kind, GitOps versions | Optional integration and version-sensitive. | Pin and test versions after Plat+Control preflight. |
| Spotify/Netflix origin attribution | Historical claim not established here. | Locate primary engineering publications and verify exact wording/date. |
| Score/OAM-style workload specifications | Awareness concepts only; status and semantics may vary. | Consult current official project documentation before adoption. |

#### Authoring Audit

| Audit | Status | Evidence and limitation |
|---|---|---|
| A — Scope and structure | PASS | Correct target filename; exact headings 2.0–2.14 appear in order; the verbatim M01–M15 handoff is in 2.0; only Unit 2 content is delivered. |
| B — Topic completeness | PASS | Sections 2.2–2.6 cover golden path/cage, API/batch/streaming/model-serving/notebook archetypes, conventions, default/option/escape, 20 rules, five ADRs, versioning, patch propagation, security, ORR, cost, telemetry, docs, notebook progression, lifecycle, and all eight synthetic failures. All ten required exercise families are grouped into five labs. |
| C — Lab/code quality | PASS WITH BOUNDARIES | Four core scripts and five test-support/test files are included. The 43-test suite was executed successfully against the exact extracted scripts; all 20 rule-negative cases, conformance false positives, drift states, template-matrix failures, and propagation non-mutation are covered. Core remains static/local and does not claim YAML-schema, admission, deployment, or runtime equivalence. |
| D — Security, SRE, and metrics | PASS | Threat/control/negative-test table, propagation runbook, staged rollout, evidence layers, cost/latency measurement, exception guardrails, and explicit rejection of individual surveillance are included. Synthetic/laptop results are not generalized. |
| E — Accuracy and source integrity | PASS WITH OPEN VERIFICATION | No fabricated image digests, action SHAs, versions, benchmark values, or source claims. Provider-specific workflow syntax, catalog schema, template engine, policy engine, and optional integrations are marked for verification. |
| F — Output/file safety | PASS | Only `02-golden-paths-templates-and-paved-roads.md` is the intended deliverable; source files and neighboring lessons are not edited. |

**OPEN items before production adoption:** replace all digest and organization-specific placeholders with M01-approved values; validate YAML/manifests with the chosen version-pinned schema tooling; verify the actual CI provider's reusable workflow, permissions, and immutable references; confirm catalog metadata with Unit 4; confirm template-engine behavior with Unit 5; and run optional kind/GitOps/runtime tests only after Plat+Control preflight. The `1.0` supported-path version and `approved_overrides` field in the Core scanner are illustrative teaching contracts, not repository standards. Static checks and passing unit tests do not certify production security or compliance.
