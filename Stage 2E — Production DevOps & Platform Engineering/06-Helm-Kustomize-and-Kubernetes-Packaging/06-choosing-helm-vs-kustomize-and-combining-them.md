# Choosing Helm vs Kustomize, and Combining Them

**Module:** M06 — Helm, Kustomize, and Kubernetes Packaging  
**Unit:** 6 — Choosing Helm vs Kustomize, and combining them  
**Target filename:** `06-choosing-helm-vs-kustomize-and-combining-them.md`  
**Estimated time:** Reading 3–4 hours; cluster-free lab 3–5 hours; optional cluster validation 1–2 hours  
**Prerequisites:** M06 Units 1–5; Kubernetes manifests, Helm charts/values/templates, chart tests/versioning, Kustomize bases/overlays/patches, `kubectl`, and `kind`  
**Core tools:** Helm, kubectl, Kustomize (embedded or standalone), Git, Bash  
**Optional tools:** `kind`, `kubeconform`, a YAML-aware diff tool, policy tooling  
**Version baseline:** Not assumed; record installed versions and verify version-sensitive features  
**Last reviewed:** Not independently verified

> **Decision principle:** Choose the packaging tool based on ownership, consumers, configuration variance, and lifecycle requirements. Then inspect and validate the final rendered manifests. Combining tools is justified only when every transformation has a clear owner and test boundary.

## 1. Why this decision matters in production

Helm and Kustomize can both produce Kubernetes YAML, but they create different abstractions and lifecycle expectations. The wrong choice can leave a team with a chart that is difficult to maintain, dozens of nearly identical overlays, an undocumented values interface, or a deployment pipeline where nobody knows which tool owns the final object.

The cost is operational, not merely aesthetic. When an incident occurs, an on-call engineer must determine which source is authoritative, which renderer produced the manifest, what changed, which system owns the release, and which rollback mechanism is valid. A pipeline with multiple renderers can be sound, but only if its intermediate artifacts are inspectable and its ownership boundaries are explicit.

Helm is often the stronger choice when a team packages and distributes an application to independent consumers. A chart can define a versioned values interface, dependencies, optional resources, hooks, tests, release history, and lifecycle commands. That abstraction has a cost: chart authors must design and maintain templates and a stable values contract.

Kustomize is often the stronger choice when a team owns known plain manifests and needs a small, declarative set of environment-specific changes. Its base-and-overlay model avoids a general-purpose template language, but patches can become brittle when they depend on resource names, list indexes, or upstream output that changes.

Neither tool makes a manifest valid, secure, or operationally correct by itself. Rendering is not applying. Applying is not reconciliation. A rendered diff is not proof of safety. A successful Helm upgrade does not roll back database data or undo every external side effect. A Kustomize build does not provide Helm-style release history.

This unit builds on M06 Units 1–5. It focuses on making a defensible decision, combining tools without creating ambiguous ownership, and documenting the choice so that future maintainers can operate it.

## 2. Learning objectives

After this unit, you should be able to:

- Explain the different abstractions and lifecycle responsibilities of Helm and Kustomize.
- Select a packaging approach using audience, variability, third-party dependencies, release needs, review ergonomics, team skills, validation, and maintenance burden.
- Make defensible choices for six common workload scenarios.
- Compare six integration patterns without confusing rendering with release installation or reconciliation.
- Customize vendor charts safely and keep one source of truth for image digests.
- Design a four-way experiment that packages the same application using plain manifests plus Kustomize, Helm only, Helm render-then-Kustomize, and Kustomize `helmCharts`.
- Identify where drift can appear and who owns rollback.
- Plan migrations, wrapper charts, golden paths, and exceptions.
- Produce an Architecture Decision Record (ADR) supported by rendered output and measured local observations.

## 3. Prerequisites, versions, and lab safety

### 3.1 Record the toolchain

Use a clean local workspace and record versions before comparing outputs:

```bash
mkdir -p "$HOME/m06-u6-packaging/evidence"
cd "$HOME/m06-u6-packaging"
{
  date -Is
  helm version
  kubectl version --client
  if command -v kustomize >/dev/null 2>&1; then
    kustomize version
  else
    echo "standalone kustomize: not installed"
  fi
  if command -v kind >/dev/null 2>&1; then
    kind version
  else
    echo "kind: not installed"
  fi
} > versions.txt 2>&1
cat versions.txt
```

If you use a disposable cluster, also record:

```bash
kubectl config current-context
kubectl version
```

The Kustomize version embedded in `kubectl` can differ from standalone Kustomize. Helm chart inflation through Kustomize and Helm post-renderer behavior must be verified against the installed versions. Do not assume that a command accepted by a recent standalone binary is accepted by the embedded version.

### 3.2 Safety rules

- Use local tools and a disposable `kind` cluster only where cluster behavior is needed.
- Never use production credentials, contexts, data, or namespaces in this lab.
- Use placeholder image references unless you have an approved, pullable test image. A placeholder digest is not a real digest.
- Do not put secrets in values files, chart templates, render outputs, shell history, or lab artifacts.
- Do not execute unreviewed post-renderers, plugins, remote build sources, or chart dependencies in privileged CI.
- Record all intermediate render outputs in a controlled workspace and inspect them before sharing.
- Do not claim measured line counts, diff sizes, timings, or command success until you collect them locally.
- If a feature is version-sensitive, verify it against the installed tool and record the result.

## 4. Mental model: packaging, rendering, applying, and lifecycle

```text
HELM-ONLY
Chart + values + dependencies
          |
          v
   Helm render / install / upgrade
          |
          v
  rendered manifests + Helm release state
          |
          v
      Kubernetes API

KUSTOMIZE-ONLY
Base + overlay + patches
          |
          v
      Kustomize build
          |
          v
      rendered manifests
          |
          v
 kubectl apply / a GitOps controller
          |
          v
      Kubernetes API

COMBINED PATHS
Helm chart -> render -> Kustomize -> final YAML -> explicit apply owner
       OR
Helm install/upgrade -> Helm post-renderer -> final YAML -> Kubernetes API
       OR
Kustomize -> helmCharts inflation -> rendered YAML -> explicit apply owner
```

| Responsibility | Helm-only | Kustomize-only | Combined path |
|---|---|---|---|
| Source abstraction | Chart templates and values | Plain resources and overlays | Multiple source formats |
| Rendering | Helm | Kustomize | Defined sequence of renderers |
| Apply owner | Helm for normal install/upgrade | `kubectl` or a controller | Must be explicitly chosen |
| Release state | Helm release metadata/history | Not provided by Kustomize itself | Retained when Helm owns install/upgrade; not equivalent when rendered output is applied directly |
| Rollback owner | Helm release operations, subject to limitations | Git/deployment workflow or controller | Depends on the selected lifecycle path |
| Primary review artifact | Rendered chart output and release diff | Rendered overlay output | Output after the final transformation |
| Main complexity | Template/value contract | Patch and overlay correctness | Tool/version boundaries and lifecycle ambiguity |

A Helm chart rendered with `helm template` and then applied with `kubectl` is not the same lifecycle as `helm install` or `helm upgrade`. In the former, Helm generated YAML but did not create an ordinary Helm release for those directly applied objects. A Helm post-renderer used during Helm install/upgrade is different: Helm remains the release owner, and the post-rendered manifests are part of that operation. Exact behavior should be checked against the Helm version and command used.

A GitOps controller may render Helm or Kustomize and reconcile desired state, but that workflow belongs to M08. This unit only requires that the team identify the authoritative desired-state path and avoid competing systems applying the same objects.

## 5. Level 1 — Helm and Kustomize fundamentals

### 5.1 The core distinction

Helm is a packaging and release tool. A chart can be distributed to teams that do not own its templates. Chart authors expose a values interface, maintain defaults, declare dependencies, and manage compatibility. Helm supports release operations and chart mechanisms such as hooks and tests. These capabilities are useful when consumers need a supported installation and upgrade contract.

Kustomize is a manifest composition and customization tool. A base holds stable YAML; overlays express environment-specific differences. It is effective when the team already owns the resources and needs limited changes without introducing a template language. It does not provide Helm-style release history or rollback.

The tools overlap in that both can render YAML, but their source abstractions and lifecycle contracts differ. Choosing based only on whether one can render the required YAML misses the important questions: Who consumes the package? Who upgrades it? Who owns failures? How will the operator know which artifact was deployed?

### 5.2 Comparison table

| Dimension | Helm | Kustomize |
|---|---|---|
| Primary problem | Package and release reusable applications | Compose and customize known YAML resources |
| Input | Chart metadata, templates, values, dependencies | Plain YAML resources and `kustomization.yaml` |
| Abstraction | Template language plus values interface | Declarative transformations and patches |
| Learning curve | More template/value concepts; logic can become complex | Easier to start; patch semantics and transformations still require care |
| Reusable distribution | Strong fit for versioned chart distribution | Can distribute bases/overlays, but not a Helm-style values API |
| Environment differences | Values files and template conditionals | Overlays, patches, transformers, components |
| Optional resources | Template conditionals and chart design | Resource inclusion and overlays/components |
| Dependencies | Chart dependency model | Resource composition; `helmCharts` is version-sensitive integration |
| Release tracking | Helm release metadata/history | Not provided by Kustomize itself |
| Hooks/tests | Helm chart hooks/tests where implemented | Kubernetes Jobs/tests can be represented, but no Helm-equivalent lifecycle contract |
| Rollback | Helm release rollback, with limits | Reapply a previous reviewed configuration or use controller workflow |
| Review ergonomics | Review values and templates plus rendered output | Review patches and final rendered output |
| Schema/policy | Chart values schema and external manifest validation/policy | External schema/policy checks on rendered output |
| Third-party applications | Often good fit when vendor publishes a chart | Useful for a stable manifest set or controlled post-render changes |
| Upgrade complexity | Chart API compatibility and dependencies | Patch compatibility with upstream manifest structure |
| Executable extension risk | Templates, dependencies, hooks and optional post-renderers add surface | Remote resources/plugins and external build integrations add surface |
| Ownership | Chart maintainer owns contract; release operator owns deployment | Manifest owner and apply/reconciliation workflow own deployment |
| CI | Chart lint/render/schema/policy/install/upgrade tests as appropriate | Build all overlays/schema/policy/render diff and selected cluster tests |

Helm rollback is not a universal undo button. It may restore a prior release’s Kubernetes manifests, but it does not automatically reverse database migrations, external service changes, data loss, or every CRD/API compatibility change. Similarly, Kustomize can render a previous revision, but the apply/reconciliation system and operational runbook determine how rollback is performed.

### 5.3 Beginner example: same Deployment and Service

A minimal Kustomize base could contain a Deployment and Service:

```yaml
# base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  labels:
    app.kubernetes.io/name: scoring-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
    spec:
      containers:
        - name: api
          image: registry.example.invalid/scoring-api:REPLACE_WITH_APPROVED_REFERENCE
          ports:
            - name: http
              containerPort: 8000
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
---
# base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: 8000
      targetPort: http
```

`base/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
```

`overlays/dev/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: scoring-dev
replicas:
  - name: scoring-api
    count: 1
```

Build from the repository root:

```bash
kubectl kustomize overlays/dev
```

Representative output excerpt, not executed:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: scoring-dev
spec:
  replicas: 1
```

An equivalent Helm chart would put the replica count and image in `values.yaml`, use templates for the Deployment and Service, and accept environment-specific values files. Helm adds a reusable chart interface and release lifecycle. Kustomize adds a declarative overlay. Both should be evaluated by the final rendered manifests, not by source files alone.

### 5.4 Helm example: values as an interface

A minimal chart might have:

```text
scoring-chart/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    └── service.yaml
```

`Chart.yaml`:

```yaml
apiVersion: v2
name: scoring-api
description: Illustrative FastAPI scoring API chart
type: application
version: 0.1.0
appVersion: "0.1.0"
```

`values.yaml`:

```yaml
replicaCount: 1
image:
  repository: registry.example.invalid/scoring-api
  tag: REPLACE_WITH_APPROVED_REFERENCE
service:
  port: 8000
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

A Deployment template reads the values and emits the corresponding fields. The chart author must ensure names, labels, selectors, and Service selectors remain consistent. A values schema can document and constrain the supported interface. Avoid exposing every internal field as a configurable value; each exposed option becomes part of the compatibility burden.

Render with a pinned local chart and inspect the output:

```bash
helm lint ./scoring-chart
helm template scoring-api ./scoring-chart -f ./scoring-chart/values.yaml
```

These commands are examples, not claims of execution. The chart is a minimal illustration and requires complete templates before it is runnable. Helm’s abstraction is valuable when consumers need a stable contract; it is overhead if a team has one simple manifest set and only a couple of environment changes.

## 6. Level 2 — A practical decision framework

### 6.1 Criteria

| Criterion | Helm tends to fit when… | Kustomize tends to fit when… | Ask before deciding |
|---|---|---|---|
| Audience | Independent teams or external consumers need a versioned package | A team owns a known manifest set | Who supports the interface? |
| Variability | Many optional features and configurable resources | Few explicit environment differences | Are differences fields or structural features? |
| App ownership | Vendor supplies a chart or team distributes an app | Team owns the YAML and wants direct visibility | Who updates upstream? |
| Lifecycle | Hooks, release history, chart dependencies, rollback matter | Applying a reviewed manifest revision is sufficient | Who owns rollback and external side effects? |
| Review | Values/templates plus rendered review are manageable | Small patches and rendered diff are clear | Can reviewers understand final output? |
| Team skills | Chart templating and release operations are understood | YAML composition and patch semantics are understood | Who will be on call? |
| GitOps | Controller supports the chosen chart/release mode | Controller supports Kustomize source mode | Defer implementation details to M08 |
| Secrets | Chart needs to integrate with an approved secret workflow | Overlay needs references/config, not embedded secret values | M09 owns lifecycle details |
| Validation | Values schema and chart test path are useful | Rendered manifest validation/policy is central | What does CI actually prove? |
| Upgrade cadence | Chart dependency upgrades are managed and tested | Upstream YAML changes are limited and patch-compatible | Who handles CVEs? |
| Supply chain | Chart and dependencies can be pinned and reviewed | Base/source can be pinned or vendored | Are plugins/remotes required? |

A qualitative scorecard can help structure discussion, but avoid universal numeric weights. For each criterion, record `strong fit`, `acceptable`, or `poor fit` and the evidence supporting the assessment. A score informs architecture judgment; it does not replace it.

### 6.2 Exactly six worked scenarios

#### Scenario 1 — Internal microservice

**Constraints:** One team owns the FastAPI API, with a worker and ETL CronJob; only a few fields differ between dev, staging, and prod.

**Recommendation:** Start with plain manifests plus Kustomize if the app has a small configuration surface and no need to distribute a chart. Use stable bases and shallow overlays.

**Why it fits:** Workload structure remains visible, environment changes are explicit, and rendered output is easy to diff. A chart is still reasonable if the service will become a supported package for many independent consumers or requires chart lifecycle features.

**Rejected alternatives:** A complex Helm chart with many conditionals is likely over-engineering for a single simple deployment. A full copy of manifests per environment duplicates security and resource defaults.

**Risks and mitigations:** Patches can become brittle after resource renames. Test every overlay and assert selectors, image references, resource limits, and security fields.

**Verification:** Build all overlays, validate schemas/policy, compare rendered diffs, and optionally test apply/rollout in `kind`.

**Revisit when:** Several teams need a versioned install contract, dependency packaging, or release lifecycle.

#### Scenario 2 — Third-party vendor application such as an observability stack

**Constraints:** The vendor publishes a maintained Helm chart and releases security fixes regularly.

**Recommendation:** Prefer the vendor chart with pinned chart version and reviewed values. Avoid forking templates as the first response to a missing setting.

**Why it fits:** Vendor chart updates can deliver fixes and compatibility improvements. Helm provides a package interface and release operations.

**Rejected alternatives:** Copying all rendered manifests creates an ongoing synchronization burden. A fork makes the organization responsible for merging upstream changes and tracking CVEs.

**Risks and mitigations:** Values can be renamed or semantics changed. Review release notes, dependency metadata, rendered diffs, schema/policy, and upgrade tests before promotion.

**Verification:** Render the pinned chart with the exact values; inspect RBAC, Service exposure, resources, security context, and image references.

**Revisit when:** No supported chart exists, the chart is abandoned, or policy requirements cannot be met through supported values/extensions.

#### Scenario 3 — Shared platform defaults

**Constraints:** Platform engineering wants consistent labels, resource defaults, security settings, and perhaps NetworkPolicy across many owned services.

**Recommendation:** Use a documented Kustomize base/component or a shared manifest library where the resources are known and the intended variation is small. A Helm library chart or wrapper may be appropriate if teams consume a versioned packaging interface.

**Why it fits:** Shared defaults can be reviewed centrally and reused without forcing every service into the same full application chart.

**Rejected alternatives:** A single global patch that changes every selector is unsafe. One universal chart can become an abstraction that does not fit distinct workloads.

**Risks and mitigations:** Shared changes have a wide blast radius. Use ownership, versioning, compatibility tests, rendered diff review, and staged rollout.

**Verification:** Test all supported consumer fixtures, not just one service. Validate that selector labels and policy selectors still match.

**Revisit when:** Consumers need stronger versioned contracts, optional feature sets, or release lifecycle.

#### Scenario 4 — Per-environment differences in a third-party chart

**Constraints:** Vendor chart is the supported package, but dev/staging/prod need different replicas, ingress hosts, storage settings, or resource budgets.

**Recommendation:** First use documented chart values. Add a controlled Kustomize post-render or render-then-patch stage only for gaps the chart does not expose and that cannot be solved through supported extension points.

**Why it fits:** Values preserve the vendor-supported interface; a small patch layer can address exceptional structural differences.

**Rejected alternatives:** Forking the entire chart to change one field creates avoidable update burden. Adding Kustomize just to transform values already supported by the chart adds complexity without value.

**Risks and mitigations:** Chart upgrades can invalidate patches. Test each pinned chart version and compare final output for every environment.

**Verification:** Render chart → apply controlled patch stage → run schema/policy checks → review final diff. Keep the lifecycle model explicit: direct apply of rendered output is not a normal Helm release.

**Revisit when:** The patch layer becomes broad or repeatedly conflicts with upstream chart changes.

#### Scenario 5 — Reusable library consumed by 30 teams

**Constraints:** Many independent consumers need a stable contract, support policy, and predictable upgrades.

**Recommendation:** Usually choose a versioned Helm chart or thin wrapper chart, with a deliberately small values API and consumer compatibility tests. Kustomize bases can still serve teams that need plain YAML, but they do not provide the same chart lifecycle contract.

**Why it fits:** A versioned package gives consumers a supported interface and an explicit upgrade path.

**Rejected alternatives:** An unversioned shared Kustomize directory creates implicit coupling: a base change can alter all consumers when they pull it. A chart with every internal implementation field exposed becomes hard to evolve.

**Risks and mitigations:** Values become a public API; deprecate fields deliberately and test representative consumer configurations.

**Verification:** Test chart rendering for supported values profiles, schema validation, install/upgrade behavior, policy, and rendered output.

**Revisit when:** Consumers do not need packaging/lifecycle features and a plain-manifest contract is demonstrably simpler.

#### Scenario 6 — One-off Job

**Constraints:** A team runs a short ETL or maintenance Job with few environment-specific fields and no reusable package contract.

**Recommendation:** A plain Job manifest with Kustomize or a small direct manifest may be enough. Use Helm if the Job is part of a charted application lifecycle, needs chart dependencies, or is consumed repeatedly by independent teams.

**Why it fits:** A simple one-off task may not justify chart abstractions. Kustomize can safely vary namespace, image reference, and resource budget.

**Rejected alternatives:** A complex chart can obscure a one-off operation. Conversely, hand-copying a recurring production Job across environments can create drift.

**Risks and mitigations:** Job pod templates and related fields can have immutable/update constraints; use deliberate naming and lifecycle strategy. Avoid blind deletion of resources with persistent data.

**Verification:** Render the exact Job, inspect command/args, service account, permissions, image, resources, and retry/deadline policy; run in a disposable namespace if needed.

**Revisit when:** The Job becomes a supported reusable product or needs coordinated release operations.

### 6.3 Rules of thumb and exceptions

- **Prefer documented chart values before patches.** Exception: a chart’s values interface is incomplete, or a patch is a temporary, tested bridge while upstream support is pursued.
- **Prefer small Kustomize patches for a limited set of known manifest changes.** Exception: if patches grow into many conditional resources and an interface for independent consumers, Helm may be clearer.
- **Prefer Helm when distributing a reusable package with a versioned values contract and release lifecycle.** Exception: a team may intentionally distribute plain YAML when consumers require direct review and can own applying/rollback.
- **Use a wrapper chart only when it removes repeated meaningful work.** Exception: a one-time wrapper with no maintenance owner can become a second, stale abstraction.
- **Do not combine tools without assigning an owner to each transformation.** Exception: an approved platform standard may require a common post-render stage, but it still needs version pinning, tests, and failure handling.
- **Review final rendered output regardless of tool.** Exception: none for production changes; the amount of review may vary, but the final artifact remains the evidence.
- **Keep one authoritative image digest.** Exception: genuinely distinct components may use different digests, but each digest must have one source of truth.

## 7. Level 3 — Combining the tools safely

Every combination adds a boundary. At each boundary, record the input artifact, tool version, output artifact, owner, and validation gates. Avoid pipelines where the same manifest is independently templated or applied by two systems.

### 7.1 Pattern A — Helm chart plus Kustomize overlays on `helm template` output

**Flow:** pinned chart + values → `helm template` → controlled output directory → Kustomize overlay → final YAML → schema/policy/diff → explicit apply owner.

Example tree:

```text
render-then-patch/
├── chart/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── values/
│   ├── dev.yaml
│   └── prod.yaml
├── overlays/
│   ├── dev/kustomization.yaml
│   └── prod/kustomization.yaml
└── build/
```

Render the chart into a controlled directory. Exact chart template completeness and output paths depend on the chart, so use a pinned chart and verified command options:

```bash
helm template scoring-api ./chart -f ./values/dev.yaml > ./build/dev-helm.yaml
```

The `helm template` output must be placed where the overlay can consume it as resources. Do not manually edit generated YAML. The overlay should patch only the specific exceptional field and then emit final output. Build and validate final YAML after patching.

**Critical lifecycle distinction:** If you apply the final YAML with `kubectl`, Helm has not created a normal release for those objects. Helm release history and `helm rollback` should not be assumed to manage them. If the same transformation is invoked as a Helm post-renderer during `helm install`/`helm upgrade`, Helm owns the release operation instead; that is Pattern C.

- **Drift:** chart version/values, render tool version, patch target, and output directory can drift independently.
- **Review:** inspect both chart output and final output; preserve intermediate artifacts.
- **CI:** pin chart and tool versions; render all environments; validate schema/policy; diff final output.
- **Rollback:** owned by the apply workflow when using render-then-apply.
- **Security:** avoid untrusted chart sources and scripts; output can contain sensitive values.
- **Use when:** a small stable patch is needed but chart values cannot express it.
- **Avoid when:** values already support the change or patch targets change every chart release.

### 7.2 Pattern B — Kustomize `helmCharts` inflation

Kustomize supports a Helm chart inflation integration in some versions. The `helmCharts` configuration and whether `--enable-helm` is required are `[VERIFY][VERSION-SENSITIVE]`. Do not assume embedded Kustomize and standalone Kustomize behave identically.

Illustrative configuration:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
helmCharts:
  - name: scoring-api
    releaseName: scoring-api
    namespace: scoring-dev
    version: 0.1.0
    repo: https://charts.example.invalid
    valuesFile: values-dev.yaml
```

This is a schema-shaped illustration, not a claim that the placeholder repository exists or that this exact field set works with every version. Verify fields and chart source support against the installed Kustomize documentation. A local chart path may be preferable for a controlled lab if supported by the selected version.

Render using the exact documented command for your version, possibly including `--enable-helm`. Inspect the inflated manifests, then run schema/policy/diff checks. Inflation renders resources; it does not itself perform a Helm install or create ordinary Helm release tracking.

- **Drift:** chart source/version, Helm version, values file, Kustomize version, and source availability.
- **Review:** final Kustomize output is reviewable, but source and chart metadata must also be reviewed.
- **CI:** pin tools and dependencies; fail clearly if chart inflation cannot run.
- **Rollback:** belongs to the apply/controller workflow, not to inflation itself.
- **Security:** chart fetch and Helm execution add dependency and supply-chain exposure.
- **Use when:** a repository intentionally treats chart output as part of a Kustomize build.
- **Avoid when:** your toolchain cannot pin/reproduce the chart or when Helm release lifecycle is required.

### 7.3 Pattern C — Helm post-renderer invoking Kustomize

A Helm post-renderer is an executable that receives rendered manifests and emits transformed manifests according to Helm’s post-renderer contract. The exact command and executable interface must be checked against the installed Helm version `[VERIFY]`. A wrapper might invoke Kustomize against a prepared overlay, but it must preserve input/output and exit status correctly.

A safe conceptual flow:

```text
Helm chart + values
        |
        v
  Helm rendering
        |
        v
 reviewed post-renderer executable
        |
        v
 final manifests -> Helm install/upgrade -> release state
```

Do not use a wrapper that swallows errors, prints diagnostics into YAML output, or returns success after Kustomize fails. During upgrades, the same intended transformation must be used consistently; otherwise the stored release manifest and new rendered output may differ in surprising ways.

- **Drift:** chart/values, renderer binary, post-renderer source, and executable environment.
- **Release tracking:** Helm remains the release owner when the post-renderer is used in Helm install/upgrade.
- **Rollback:** use Helm release operations with the appropriate post-renderer strategy, while understanding data/external side-effect limits.
- **CI:** run the renderer independently, test its exit code and output, then compare final manifests.
- **Security:** executable code runs as part of the deployment path. Pin, review, and least-privilege it.
- **Use when:** a controlled transformation must be part of the Helm release lifecycle.
- **Avoid when:** the team cannot maintain the executable or guarantee it is used consistently.

A post-renderer that fails should normally cause the Helm command to fail. The incident in Section 8 describes a defective wrapper that incorrectly suppresses the error, not expected Helm behavior.

### 7.4 Pattern D — Kustomize for owned manifests, Helm for third-party dependencies

A repository can use Kustomize for an owned FastAPI service while managing a third-party observability stack as a separate Helm release. This is often a clean boundary because the owned application and vendor dependency have different update owners.

```text
repo/
├── apps/scoring-api/       # base + overlays
└── vendor-releases/
    └── observability/      # pinned chart version + values
```

Define namespaces, resource names, and ownership explicitly. Do not let both Kustomize and Helm manage the same Service or Deployment. Pin chart versions and values; review vendor release notes and rendered output independently from app changes.

A local scripted sequence can render/validate the Kustomize app and separately run chart validation for the vendor release, but ordering and installation are environment-specific. Avoid implying that the script is a reconciliation controller.

- **Drift:** app overlay drift and vendor values/chart drift are separate.
- **Release tracking:** Helm owns the vendor release; the app apply workflow owns Kustomize resources.
- **Rollback:** separate owners and runbooks.
- **CI:** validate each path and test cross-resource contracts such as Service endpoints and NetworkPolicy selectors.
- **Security:** update vendor chart promptly and review all permissions.
- **Use when:** owned app manifests and vendor package have clear, separate lifecycles.
- **Avoid when:** ownership boundaries overlap or both paths create the same resources.

### 7.5 Pattern E — GitOps controllers rendering both

Argo CD and Flux may render Helm charts or Kustomize sources depending on the controller and configuration. This is a forward reference to M08, not a controller setup guide. Verify the selected controller’s version and supported rendering behavior in that module.

The key design requirement is one authoritative desired-state path for each resource. If a controller owns an object, a separate script or Helm command should not compete by applying the same object independently. Record which source defines the desired state, which renderer produces it, and how changes are promoted.

- **Drift:** source changes and live-cluster drift are different signals.
- **Release/rollback:** controller and packaging semantics depend on the configured integration; confirm in M08.
- **CI:** render with compatible versions and test the source before merge.
- **Security:** protect source repositories, credentials, and build extensions.
- **Use when:** an organization already operates a supported GitOps workflow.
- **Avoid when:** two controllers or a controller and manual release process compete for the same resources.

### 7.6 Pattern F — Helm values per environment without Kustomize

Use a chart’s default `values.yaml` plus environment-specific values files:

```text
scoring-chart/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-staging.yaml
├── values-prod.yaml
└── templates/
```

Render each environment with the pinned chart and values. This is often enough when differences are already exposed by the chart and the template structure remains stable. Do not add Kustomize solely to make the repository more sophisticated.

It becomes difficult when many structural changes are not supported by values, patch requirements are large, or chart upgrades repeatedly break downstream transformations. At that point, either improve the chart interface, use a small controlled post-render stage, or reconsider the packaging approach.

- **Drift:** values files can diverge, and chart upgrades can change defaults.
- **Release tracking:** retained when installed/upgraded through Helm.
- **Rollback:** Helm release owner, subject to known limitations.
- **CI:** render every values profile, schema/policy check, and test relevant upgrade paths.
- **Security:** avoid embedding secrets in values files; keep dependencies pinned.
- **Use when:** values fully express the required differences.
- **Avoid when:** unsupported structural differences require broad and fragile patches.

### 7.7 Six-pattern comparison matrix

| Pattern | Helm release metadata retained? | Apply/rollback owner | Drift and review risk | Complexity/security surface | Best fit |
|---|---|---|---|---|---|
| A. Helm render → Kustomize → direct apply | No ordinary Helm release for directly applied output | `kubectl`/deployment workflow | Chart output and patches can diverge; inspect final output | Extra render stage and patch target risk | Small stable patch when direct-manifest lifecycle is acceptable |
| B. Kustomize `helmCharts` | Inflation alone does not create a release | `kubectl`/controller | Tool/chart/version drift | Helm dependency plus Kustomize feature compatibility | Build pipeline intentionally owns rendered output |
| C. Helm post-renderer | Yes, when used during Helm install/upgrade | Helm release workflow | Post-renderer version/output can drift | Executable extension and error-handling risk | Transformation must be part of Helm release |
| D. Kustomize owned app + Helm vendor release | Vendor release only | Separate owners per resource set | Cross-resource contracts can drift | Moderate; boundaries can be clear | Owned app plus independent third-party package |
| E. GitOps renders both | Depends on controller integration | Controller/source workflow | Multiple desired-state paths are dangerous | Controller-specific behavior and credentials | Organization already supports that workflow |
| F. Helm values per environment | Yes, for normal Helm release operations | Helm | Values/defaults can drift | Lowest combination complexity | Chart values express all required differences |

## 8. Level 4 — Platform standards, migrations, and incidents

### 8.1 Third-party chart customization

Use this order of preference:

1. Use an existing documented chart value.
2. Use a supported chart extension mechanism.
3. Use a controlled post-renderer or render-then-patch pipeline with tests.
4. Fork/vendor only when necessary, with explicit upstream tracking and a security-update plan.

A fork may be justified when the upstream chart is abandoned or a critical requirement cannot be met otherwise. It should not be the default response to a small missing option. A fork transfers responsibility for merging fixes, monitoring CVEs, preserving compatibility, and testing upstream changes.

For every chart upgrade, review release notes, chart/dependency metadata and lock information where applicable, values schema changes, rendered diff, policy results, install/upgrade tests, and representative consumer configurations. A successful render is only one gate.

### 8.2 Avoid double-templating confusion

Helm template expressions belong to Helm’s chart-rendering phase. Kustomize patch syntax belongs to a later YAML transformation phase. Once Helm has rendered YAML, the output should be treated as Kubernetes manifests, not as a second Helm template source.

```text
Chart templates + values
        |
        v
Helm-rendered YAML (no intended Helm template phase remaining)
        |
        v
Kustomize patches / transformations
        |
        v
Final rendered YAML
```

Do not render a chart, patch it, and then feed it through a second unrelated Helm template operation unless the pipeline explicitly defines that contract. That can create duplicated resources, unresolved template syntax, or surprising changes in resource names. Preserve the intermediate output at each stage so that the team can identify where a difference first appeared.

### 8.3 One source of truth for image digests

Do not maintain separate independently edited image digests in Helm values, Kustomize `images`, and shell scripts. Define one canonical input and have CI update or read it. Each packaging path should consume that same value through its supported interface.

```text
CI image build/promotion
          |
          v
canonical image reference file
          |
          +----> Helm values generation/input
          |
          +----> Kustomize image transformation/input
          |
          v
final rendered manifests
          |
          v
CI assertion: every expected workload uses approved digest
```

The canonical file can be a small YAML/JSON file, a release metadata artifact, or another approved source. The important point is one authoritative value per image. A placeholder such as `sha256:REPLACE_WITH_VERIFIED_DIGEST` is documentation only and must never pass a production digest policy.

Verify the final output, not merely the canonical input. Extract all rendered image references and compare them with the expected inventory. This catches cases where a chart template hardcodes a tag or a post-render stage overwrites the intended digest.

### 8.4 Environment promotion

M02 Unit 9 covers the detailed promotion workflow. At this level:

- Promote the same tested image/artifact across environments where the architecture allows.
- Keep environment-specific configuration separate and reviewed.
- Render every target environment and compare meaningful differences.
- Record the artifact identity, source revision, tool versions, and approval.
- Avoid rebuilding or mutating an image separately for each environment.
- Treat a change in chart version or renderer version as a change to the deployment artifact, not merely a harmless tooling update.

### 8.5 Drift detection

| Drift type | What to compare | What it does not prove |
|---|---|---|
| Chart/values drift | Chart version, values files, dependency metadata, rendered chart output | Does not show live-cluster drift by itself |
| Overlay patch drift | Kustomization files, patch targets, rendered overlay output | Does not prove API admission or runtime behavior |
| Post-renderer drift | Renderer source/version, command contract, input/output | Does not prove the executable ran in the intended release |
| Rendered-manifest-in-Git drift | Committed output versus reproducible build | Does not guarantee the cluster matches Git |
| Live-cluster drift | Desired state versus observed cluster state through the selected workflow | Does not identify the source of every difference without provenance |

Text diffs are transparent but may include ordering or formatting noise. Semantic diff tools can reduce noise, but normalization must not hide selector, security context, RBAC, image, storage, or deletion changes. Keep the original rendered artifact for auditability.

### 8.6 Golden path and exception process

An organization may define defaults by workload type: for example, Kustomize for owned applications with a small variance surface, Helm for distributed packages and vendor charts, and an approved combination only for a documented need. M16 covers the broader platform golden path.

A useful standard includes: tool ownership, supported versions, mandatory CI checks, minimum security defaults, source pinning, upgrade cadence, review ownership, deprecation policy, and a documented exception process. Exceptions should include the reason, risk, owner, expiration/revisit date, and validation plan. A golden path should reduce repeated decisions, not force every workload into one tool regardless of fit.

### 8.7 Migration playbooks

| Migration | Steps | Main risk | Rollback and exit criteria |
|---|---|---|---|
| Copy-paste manifests → Kustomize | Inventory copies; render/baseline each environment; extract common base; create shallow overlays; compare output; validate; stage rollout | Hidden environment differences disappear during consolidation | Restore previous manifests if output diverges unexpectedly; exit when all overlays have reviewed parity and tests |
| Helm → rendered manifests/Kustomize | Capture pinned chart/values and rendered output; identify hooks/dependencies/release assumptions; build reproducible render pipeline; apply to a disposable environment; compare lifecycle | Loss/change of Helm release history, hooks, rollback, and chart upgrade workflow | Roll back using the explicitly chosen manifest owner; exit when lifecycle ownership and upgrade tests are documented |
| Vendor chart → internal wrapper chart | Pin vendor dependency; define small internal values API; add only stable defaults/resources; test consumer values; document upstream tracking; test upgrades | Nested values and hidden upstream changes create upgrade friction | Keep prior wrapper/dependency version and test rollback; exit when consumer contract, CVE process, and upgrade tests are operational |

For Helm-to-rendered-manifests migration, rendered YAML does not preserve Helm release semantics. Hooks, release history, dependency resolution, and rollback ownership may change. Inventory them before migration; if those capabilities remain essential, retain Helm as the release owner and consider a post-renderer instead.

### 8.8 Wrapper chart pattern

A wrapper chart is a thin internal chart that depends on a pinned vendor chart and supplies controlled defaults or additional resources.

**Benefits:** A stable internal interface, organizational defaults, reduced repeated values, and a place to document supported settings.

**Pitfalls:** Vendor values are often nested under a subchart name; overrides can be confusing. The wrapper may not be able to modify subchart templates. Dependency upgrades can change defaults or resource structure. The team must test and version the wrapper, track CVEs, and communicate compatibility to consumers.

A wrapper chart should expose only supported settings and keep the underlying dependency version explicit. Do not create one simply to rename a values file. Avoid it if the wrapper adds no meaningful stable contract or no team will own its updates.

### 8.9 Qualitative maintenance-cost model

| Cost area | Helm only | Kustomize only | Combined path |
|---|---|---|---|
| Onboarding | Medium if chart/value concepts are new | Low–medium; patch semantics still matter | High unless boundaries are documented |
| Debugging | Template/value and rendered-output inspection | Patch/transformer and rendered-output inspection | Stage-by-stage reproduction required |
| Standard change review | Values and rendered diff | Patch and rendered diff | Every intermediate and final artifact |
| Vendor upgrade | Often manageable with upstream chart discipline | Can be costly if patches track upstream YAML | Can be costly due to chart and patch compatibility |
| Environment drift | Values/defaults may diverge | Overlay patches may diverge | More sources of configuration can drift |
| CI complexity | Chart lint/render/schema and lifecycle tests | Build/schema/policy/diff and selected cluster tests | Additional version and boundary tests |
| Security patch turnaround | Good when vendor chart is maintained and upgraded | Depends on manifest/base ownership | Depends on who monitors and updates every dependency |
| Ownership burden | Chart maintainer and release operator | Manifest owner and apply workflow | Must assign ownership per stage |

These labels are qualitative, scenario-dependent judgments, not measured benchmarks. Complexity does not disappear; it moves. A combination can reduce patch duplication but increase build and debugging work.

### 8.10 Incident analyses

#### Incident 1 — Double rendering creates conflicting Services

**Symptom:** Two Services appear, or the same logical endpoint has conflicting names/selectors.  
**Evidence/commands:** Save output after each render stage; compare resource `kind`, `metadata.name`, namespace, selectors, and labels. Use a duplicate-resource check on the final YAML.  
**Root cause:** A resource was emitted by both the chart and an overlay/component, or an intermediate rendered file was included alongside the final output.  
**Mitigation:** Establish one authoritative resource definition and remove duplicate inclusion.  
**Regression test:** Assert uniqueness of `(apiVersion, kind, namespace, name)` in final output.  
**Prevention:** Document each artifact boundary and never feed both pre-render and post-render resources into the same final build unintentionally.

#### Incident 2 — Post-renderer failure is suppressed

**Symptom:** An expected policy patch is missing from the released manifests even though the deployment wrapper reports success.  
**Evidence/commands:** Run the post-renderer independently with captured input/output; inspect its exit code and stderr; compare pre- and post-render output.  
**Root cause:** A defective wrapper swallowed an error or returned success after the transformation failed. This is a wrapper defect, not expected Helm behavior.  
**Mitigation:** Make non-zero renderer exit fail the pipeline; stop release promotion and correct the deployment using the proper lifecycle owner.  
**Regression test:** Inject a controlled failure and assert CI fails and does not publish final output.  
**Prevention:** Use `set -euo pipefail` where appropriate, preserve exit status, and test the exact executable contract.

#### Incident 3 — Vendor chart fork misses a CVE fix

**Symptom:** The organization’s fork lacks a security fix already available upstream.  
**Evidence/commands:** Compare fork revision with upstream release history, dependency versions, and security advisories; inspect rendered image and RBAC changes.  
**Root cause:** No upstream tracking owner or scheduled merge process.  
**Mitigation:** Assess exposure, update the fork or return to upstream-supported values if feasible, then run render/policy/upgrade tests.  
**Regression test:** Add an upstream-version inventory and stale-dependency gate.  
**Prevention:** Fork only as a last resort and assign a named update/security owner.

#### Incident 4 — `helmCharts` output differs locally and in CI

**Symptom:** A manifest appears in one environment but not the other.  
**Evidence/commands:** Record Helm and Kustomize versions, chart version, values, remote source revision, and intermediate/final output.  
**Root cause:** Different embedded/standalone Kustomize versions, Helm versions, or dependency source resolution.  
**Mitigation:** Standardize and pin the toolchain and chart source; rebuild from a clean workspace.  
**Regression test:** Build with the pinned CI image/toolchain and compare expected output.  
**Prevention:** Treat toolchain changes as reviewed deployment changes.

#### Incident 5 — Wrong values nesting in a wrapper chart

**Symptom:** A value intended for a vendor subchart has no effect.  
**Evidence/commands:** Inspect the wrapper’s dependency alias/name and rendered output; run chart lint/schema validation and compare expected field values.  
**Root cause:** Values were supplied at the wrong nesting level or the vendor chart changed its values API.  
**Mitigation:** Correct the values hierarchy and validate against the pinned dependency version.  
**Regression test:** Add a consumer fixture that asserts the rendered field.  
**Prevention:** Document the wrapper’s supported values and test dependency upgrades.

#### Incident 6 — Image digest configured independently in Helm and Kustomize

**Symptom:** Different environments render different images even though the release is intended to promote one artifact.  
**Evidence/commands:** Extract all image references from each final rendered manifest and compare them with the canonical digest input.  
**Root cause:** Multiple independent sources of truth or a later transformer overwrote an earlier value.  
**Mitigation:** Restore one canonical digest source and regenerate outputs.  
**Regression test:** CI asserts expected image references in all supported overlays.  
**Prevention:** Let CI update one file/artifact and make every packaging path consume it.

#### Incident 7 — Render-then-apply loses Helm release history

**Symptom:** On-call expects `helm rollback` to restore objects that were actually applied with `kubectl`.  
**Evidence/commands:** Inspect deployment logs and Helm release list/history; determine which command applied the resources.  
**Root cause:** Rendering with Helm was confused with installing/upgrading a Helm release.  
**Mitigation:** Use the actual owner’s rollback process; restore a prior reviewed manifest revision if that is the documented lifecycle.  
**Regression test:** Document and rehearse rollback in a disposable environment.  
**Prevention:** State lifecycle ownership in the ADR and deployment runbook.

#### Incident 8 — Two systems apply the same resource

**Symptom:** A resource repeatedly changes between two configurations or produces confusing drift.  
**Evidence/commands:** Inspect resource ownership metadata where available, controller/release records, deployment logs, and both desired-state sources.  
**Root cause:** A manual script, Helm release, and/or controller all attempted to manage the same object.  
**Mitigation:** Select one authoritative owner and remove the competing apply path through a controlled change.  
**Regression test:** Inventory resource identities across all generated outputs and ownership declarations.  
**Prevention:** Enforce ownership boundaries and do not let multiple release systems manage the same object.

## 9. SRE lens

Track packaging quality as operational evidence rather than as a contest between tools.

| Indicator | Definition | Caveat |
|---|---|---|
| Packaging change failure rate | Packaging changes requiring rollback/hotfix due to configuration defects divided by packaging changes in a defined window | Root cause may span application, platform, and tooling |
| Validated environment percentage | Environments with passing render/schema/policy checks divided by supported environments | A passing render is not runtime proof |
| Unexplained rendered diffs | High-risk output changes merged without recorded explanation/approval | Requires a consistent review process |
| Mitigation time | Time from packaging-related alert to safe mitigation | Rollback mechanisms differ by lifecycle |
| Renderer identification time | Time to identify exact tool/version/source that produced a manifest | Provenance logging is required |
| Vendor update latency | Time from relevant upstream security release to validated internal adoption | Must define when the clock starts |
| Duplicate ownership incidents | Count of incidents involving multiple systems applying the same resource | Low counts can still hide serious risk |
| CI duration/flakiness | Pipeline duration and intermittent failure rate | Separate infrastructure failures from configuration failures |

Example metric: **validated environment percentage** over a rolling 30-day window = number of supported environment builds that pass all required render/schema/policy checks divided by the number of supported environment builds attempted. Record the numerator, denominator, sample size, and tool failures. Small samples make percentages unstable; do not invent industry benchmarks.

Runbook:

1. Capture signal and affected release/resource identity.
2. Record Helm, kubectl/embedded Kustomize, standalone Kustomize, and dependency versions.
3. Reproduce rendering from a clean workspace.
4. Save output after each stage and inspect the final output.
5. Compare expected source, final rendered manifests, and live state.
6. Identify the lifecycle owner and select the correct mitigation/rollback mechanism.
7. Validate the mitigation and confirm runtime health.
8. Add a regression test and document the incident.

The architecture should make it clear who is on call for each stage. If the first response to an incident is “we do not know which renderer produced this,” the pipeline needs better provenance and ownership.

## 10. Security lens

| Threat | Control | Evidence | Residual limitation |
|---|---|---|---|
| Post-renderer/plugin executes arbitrary code | Review and pin executable; least privilege; test failure behavior | Source/version, CI permissions, test results | Reviewed code may still contain defects |
| Remote chart/base changes | Pin versions/revisions and review updates | Lock/version metadata and rendered diff | Pinning does not prove trustworthiness |
| Vendor fork misses security updates | Upstream owner, CVE tracking, upgrade cadence | Dependency inventory and update records | Upstream may not provide timely fixes |
| Duplicate image digest sources | Canonical digest input and rendered-image assertion | CI comparison report | Wrong canonical input can still be promoted |
| Secrets in values/render output | Use approved secret lifecycle; scan and redact artifacts | Secret-scan and artifact review | Scanners can miss leaks |
| Patch weakens RBAC/security defaults | Policy gates and review sensitive fields | Policy output and rendered diff | Policy rules may be incomplete |
| Two systems own one resource | Ownership inventory and single desired-state path | Resource inventory and release/controller records | Manual emergency actions need audit |
| Helm lifecycle lost in render-then-apply | ADR/runbook names apply and rollback owner | Tested rollback evidence | External side effects remain separate |
| CI tool-version drift | Pin and record toolchain; reproduce in CI image | Version manifest and build artifact metadata | Dependency vulnerabilities still require updates |
| `helmCharts`/remote supply chain | Pin chart, source, Helm/Kustomize versions; review dependencies | Source provenance and rendered output | A trusted source may still contain vulnerable content |
| Sensitive generated manifests | Synthetic values, access/retention limits, redaction | Artifact inspection and access controls | Redaction may be imperfect |

Neither Helm nor Kustomize guarantees security. Rendering and schema validation are not policy validation; policy validation is not runtime verification. Chart signature/trust topics belong to Unit 7. Secret lifecycle details belong to M09. GitOps reconciliation details belong to M08. Post-renderers and plugins are executable dependencies. Never use production credentials or clusters in this lab.

## 11. Production checklist

- [ ] Decision criteria, tool choice, and lifecycle owner are documented.
- [ ] Rendered output is reviewed for all supported environments.
- [ ] Each configuration value and image digest has one authoritative source.
- [ ] Helm, kubectl/embedded Kustomize, standalone Kustomize, and dependency versions are recorded/pinned as appropriate.
- [ ] Release tracking and rollback owner are identified.
- [ ] CI covers render, schema, policy, diff, and relevant install/upgrade paths.
- [ ] Vendor dependencies are pinned, reviewed, and assigned an update owner.
- [ ] Post-renderer failure causes the pipeline/release operation to fail.
- [ ] Duplicate resource ownership is prevented.
- [ ] Environment promotion strategy is documented.
- [ ] Secrets are excluded from repositories and rendered artifacts.
- [ ] Deprecation, upgrade, and end-of-life policies are documented.
- [ ] ADR includes rejected alternatives, consequences, and revisit triggers.
- [ ] M08, M09, M16, and Unit 7 boundaries are respected.

## 12. Hands-on lab: package the same app four ways

**Goal:** Render the same conceptual FastAPI scoring API using four packaging patterns and compare the actual artifacts.  
**Acceptance criteria:** All four approaches produce inspectable YAML; the learner records versions, diffs, lifecycle ownership, and risks; the comparison matrix is filled with local observations; an ADR selects one approach and rejects alternatives with reasons.  
**Estimated time:** 3–5 hours. **Cluster required: No** for the core lab; optional disposable `kind` for apply/runtime checks.

### Lab setup and shared contract

Use a placeholder image reference until you substitute an approved test image and verified digest. The examples focus on packaging structure, not a pullable image. The four outputs should preserve the same intended workload behavior wherever the packaging approach is meant to be equivalent:

- Deployment `scoring-api`, container port 8000, named selector labels;
- Service `scoring-api` targeting the same Pod labels and port;
- ConfigMap `scoring-runtime`;
- ServiceAccount `scoring-api`;
- non-root security defaults, probes, requests/limits;
- environment-specific replica count and namespace.

For cluster-free rendering, image pullability is irrelevant. Do not claim a successful rollout unless you actually run one in a disposable cluster.

Create a workspace:

```bash
mkdir -p "$HOME/m06-u6-packaging"/{evidence,plain,helm-only,render-then-kustomize,helmcharts}
cd "$HOME/m06-u6-packaging"
```

Record versions using Section 3. Save each approach’s outputs in its own directory. Use the same chart/image contract and compare the final output rather than expecting identical formatting.

### Part A — Plain manifests + Kustomize

**Goal:** Use a base and dev/prod overlays.  
**Prerequisites:** `kubectl` with Kustomize support or standalone Kustomize. **Cluster required: No.**

File tree:

```text
plain/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── serviceaccount.yaml
└── overlays/
    ├── dev/kustomization.yaml
    └── prod/kustomization.yaml
```

`plain/base/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
  - configmap.yaml
  - serviceaccount.yaml
```

`plain/base/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  labels:
    app.kubernetes.io/name: scoring-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
    spec:
      serviceAccountName: scoring-api
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: api
          image: registry.example.invalid/scoring-api:REPLACE_WITH_APPROVED_REFERENCE
          ports:
            - name: http
              containerPort: 8000
          envFrom:
            - configMapRef:
                name: scoring-runtime
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 3
            periodSeconds: 5
```

`plain/base/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: 8000
      targetPort: http
```

`plain/base/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scoring-runtime
data:
  LOG_LEVEL: info
  MODEL_NAME: demo-model
```

`plain/base/serviceaccount.yaml`:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: scoring-api
automountServiceAccountToken: false
```

`plain/overlays/dev/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: scoring-dev
replicas:
  - name: scoring-api
    count: 1
```

`plain/overlays/prod/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: scoring-prod
replicas:
  - name: scoring-api
    count: 3
```

Render:

```bash
kubectl kustomize plain/overlays/dev > evidence/plain-dev.yaml
kubectl kustomize plain/overlays/prod > evidence/plain-prod.yaml
diff -u evidence/plain-dev.yaml evidence/plain-prod.yaml > evidence/plain-dev-prod.diff || test "$?" -eq 1
```

Representative output excerpt, not executed:

```yaml
kind: Deployment
metadata:
  name: scoring-api
  namespace: scoring-dev
spec:
  replicas: 1
```

**Observe:** Which fields are shared? Which differences are explicit? Is the Service selector identical to the Pod-template label?  
**Failure modes:** unsupported Kustomize field—verify version; mismatched selector—inspect rendered Deployment/Service; image placeholder—do not apply until replaced.  
**Cleanup:** Cluster-free; remove only the lab workspace when finished.

### Part B — Helm only

**Goal:** Represent the same app using a small chart and environment values.  
**Prerequisites:** Helm. **Cluster required: No.**

File tree:

```text
helm-only/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── configmap.yaml
    └── serviceaccount.yaml
```

`helm-only/Chart.yaml`:

```yaml
apiVersion: v2
name: scoring-api
description: Illustrative scoring API chart for M06 Unit 6
type: application
version: 0.1.0
appVersion: "0.1.0"
```

`helm-only/values.yaml`:

```yaml
replicaCount: 1
namespace: scoring-dev
image:
  repository: registry.example.invalid/scoring-api
  tag: REPLACE_WITH_APPROVED_REFERENCE
service:
  port: 8000
config:
  logLevel: info
  modelName: demo-model
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

`helm-only/values-dev.yaml`:

```yaml
namespace: scoring-dev
replicaCount: 1
```

`helm-only/values-prod.yaml`:

```yaml
namespace: scoring-prod
replicaCount: 3
```

`helm-only/templates/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: {{ .Values.namespace }}
  labels:
    app.kubernetes.io/name: scoring-api
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
    spec:
      serviceAccountName: scoring-api
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: api
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - name: http
              containerPort: 8000
          envFrom:
            - configMapRef:
                name: scoring-runtime
          resources:
{{ toYaml .Values.resources | indent 12 }}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 3
            periodSeconds: 5
```

`helm-only/templates/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: {{ .Values.namespace }}
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: http
```

`helm-only/templates/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scoring-runtime
  namespace: {{ .Values.namespace }}
data:
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
  MODEL_NAME: {{ .Values.config.modelName | quote }}
```

`helm-only/templates/serviceaccount.yaml`:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: scoring-api
  namespace: {{ .Values.namespace }}
automountServiceAccountToken: false
```

Render and inspect:

```bash
helm lint ./helm-only
helm template scoring-api ./helm-only -f ./helm-only/values-dev.yaml > evidence/helm-dev.yaml
helm template scoring-api ./helm-only -f ./helm-only/values-prod.yaml > evidence/helm-prod.yaml
diff -u evidence/helm-dev.yaml evidence/helm-prod.yaml > evidence/helm-dev-prod.diff || test "$?" -eq 1
```

These commands are not claimed to have been run. Verify template indentation and rendered YAML locally. **Observe:** How many values define the supported interface? Which defaults are shared? Which fields are hidden in templates?  
**Failure modes:** indentation errors, wrong values path, and image tag/digest policy mismatch. If using a digest, model the image reference so the rendered value does not append an unintended tag; verify the chart template and final output.  
**Cleanup:** No cluster resources were created.

### Part C — Helm render → Kustomize overlays

**Goal:** Render the same chart, then apply a small Kustomize environment overlay to the rendered YAML.  
**Prerequisites:** Helm and Kustomize. **Cluster required: No.**

The chart render must be a controlled artifact. For a reproducible lab, render one environment into its own build directory and create a Kustomize root that consumes that file. This is a direct render-then-apply pattern, not a Helm post-renderer.

Example tree:

```text
render-then-kustomize/
├── build/
│   ├── dev-helm.yaml
│   └── prod-helm.yaml
└── overlays/
    ├── dev/kustomization.yaml
    └── prod/kustomization.yaml
```

Render the chart first:

```bash
helm template scoring-api ./helm-only -f ./helm-only/values-dev.yaml \
  > ./render-then-kustomize/build/dev-helm.yaml
helm template scoring-api ./helm-only -f ./helm-only/values-prod.yaml \
  > ./render-then-kustomize/build/prod-helm.yaml
```

`render-then-kustomize/overlays/dev/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../build/dev-helm.yaml
commonAnnotations:
  packaging.example.invalid/pipeline: helm-render-then-kustomize
```

`render-then-kustomize/overlays/prod/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../build/prod-helm.yaml
commonAnnotations:
  packaging.example.invalid/pipeline: helm-render-then-kustomize
```

Render the final stage:

```bash
kubectl kustomize render-then-kustomize/overlays/dev > evidence/render-then-kustomize-dev.yaml
kubectl kustomize render-then-kustomize/overlays/prod > evidence/render-then-kustomize-prod.yaml
```

This minimal overlay adds an annotation so the transformation is visible. A real use case might patch a chart field not exposed through values, but the patch should be small, targeted, and tested against the pinned chart output.

**Lifecycle:** Applying these final manifests directly with `kubectl` does not create ordinary Helm release tracking. If you require Helm release history, use a Helm install/upgrade path with a verified post-renderer instead; do not mix the two models.  
**Observe:** Compare the pre-overlay chart output with the final Kustomize output. Identify the exact transformation.  
**Failure modes:** build directory missing, patch/resource target mismatch, chart upgrade changes names, or accidentally including both intermediate and final output in one resource list.  
**Cleanup:** No cluster resources were created.

### Part D — Kustomize + `helmCharts`

**Goal:** Explore Kustomize’s Helm chart inflation integration and record the installed version’s exact requirements.  
**Prerequisites:** Helm and a Kustomize version supporting the feature. **Cluster required: No.**

`helmCharts` syntax and the `--enable-helm` requirement are `[VERIFY][VERSION-SENSITIVE]`. Use a local chart path if the installed version supports it, or a pinned chart repository/version verified against the matching reference. Do not use a fabricated remote repository as a real source.

Illustrative `helmcharts/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
helmCharts:
  - name: scoring-api
    releaseName: scoring-api
    namespace: scoring-dev
    version: 0.1.0
    valuesFile: ../helm-only/values-dev.yaml
```

This is a schema illustration only. Before running, verify whether your Kustomize version supports the shown chart source and path configuration. Depending on the version and configuration, chart repository fields or a local chart path may be required; do not guess. Run the installed command’s help and use the exact supported configuration.

After validating the config, run the documented build command for that version, potentially:

```bash
kustomize build ./helmcharts --enable-helm > evidence/helmcharts-dev.yaml
```

The command is `[VERIFY]`; do not assume it works in embedded Kustomize. Inspect output and compare it with Part B. Inflation is rendering, not Helm installation or release tracking.

**Observe:** What extra tool/source dependencies exist? Is the output reproducible from a clean workspace? Which metadata and values are required?  
**Failure modes:** unsupported feature, missing Helm binary, chart fetch/network failure, wrong values path, or different local/CI versions.  
**Cleanup:** No cluster resources were created.

### Comparison matrix to fill with real observations

Do not fill in counts until you measure your local files and diffs. Count generated and source files consistently, state whether blank/comment lines are included, and choose one standard change (for example, changing replicas from 1 to 3) for each approach.

| Approach | Files/lines of configuration (measure locally) | Review diff for a standard change | Debugging notes | Release/rollback owner | Tool/version requirements | Main risks |
|---|---|---|---|---|---|---|
| Plain manifests + Kustomize | Learner records | Learner records | Learner records | Learner records | Learner records | Learner records |
| Helm only | Learner records | Learner records | Learner records | Learner records | Learner records | Learner records |
| Helm → render → Kustomize | Learner records | Learner records | Learner records | Learner records | Learner records | Learner records |
| Kustomize + `helmCharts` | Learner records | Learner records | Learner records | Learner records | Learner records | Learner records |

For each approach, save final rendered output and use the same diff tool/options. Note that line counts and diff size are not quality metrics by themselves; the review question is whether the meaningful change is visible and attributable.

### Written decision memo / ADR exercise

Choose a packaging approach for this scenario: an internal data/ML platform team owns the FastAPI scoring service, needs dev/staging/prod configuration, wants safe rendered-diff review, and expects other teams to consume the package.

Your ADR should choose one approach, compare at least two alternatives, state consequences and lifecycle ownership, and define what evidence would trigger reconsideration. There is no single mandatory answer. A versioned Helm chart may fit if teams truly consume it as a supported package; Kustomize may fit if the platform team distributes reviewed manifests and the consumers own apply/rollback. A combined approach is defensible only when the extra stage solves a specific gap.

## 13. Self-check questions

1. **What is the fundamental distinction between Helm and Kustomize?**  
   **Answer:** Helm packages reusable applications and supports release lifecycle; Kustomize composes/customizes plain manifests. **Tempting wrong answer:** “They are identical YAML generators” ignores the package contract and release state.

2. **Why is rendered output the review artifact?**  
   **Answer:** It shows the final names, selectors, images, resources, security fields, and references after all transformations. **Wrong answer:** reviewing only source values/patches can miss effects introduced by templates or later transforms.

3. **What changes when rendered Helm manifests are applied outside Helm?**  
   **Answer:** Helm did not create the ordinary release state for those direct-applied objects, so Helm history/rollback should not be assumed to own them. **Wrong answer:** `helm template` is not equivalent to `helm install`.

4. **What is a good default for a vendor application?**  
   **Answer:** Usually a pinned, maintained vendor chart with reviewed values. **Wrong answer:** immediately forking the chart creates update and CVE maintenance burden.

5. **What is the safe order for customizing a third-party chart?**  
   **Answer:** documented values, supported extension, controlled tested post-render/overlay, fork/vendor only as last resort. **Wrong answer:** forking first makes every upstream fix the consumer’s responsibility.

6. **Render-then-patch versus Helm post-renderer?**  
   **Answer:** Direct render-then-apply usually places apply/rollback outside Helm; a post-renderer used during Helm install/upgrade keeps Helm as release owner. **Wrong answer:** both paths are not lifecycle-equivalent.

7. **What does Kustomize `helmCharts` inflation do and not do?**  
   **Answer:** It renders chart resources through a version-dependent integration; it does not itself install a Helm release. **Wrong answer:** chart inflation is not `helm install`.

8. **How do you keep image digests consistent?**  
   **Answer:** Maintain one canonical image reference and assert the final rendered images match it. **Wrong answer:** independently updating Helm values and Kustomize `images` invites drift.

9. **Why does a vendor chart fork add security risk?**  
   **Answer:** It can miss upstream CVE fixes and compatibility updates without an explicit tracking process. **Wrong answer:** a fork does not automatically inherit upstream maintenance.

10. **What evidence belongs in a packaging ADR?**  
    **Answer:** Requirements, alternatives, rendered output/diffs, tool versions, lifecycle owner, risks, tests, rollback, and revisit triggers. **Wrong answer:** a tool preference without evidence is not a durable architecture decision.

## 14. Evidence artifacts

Create these learner-generated artifacts under the workspace:

- `versions.txt`;
- all four approach file trees;
- rendered output for each environment and approach;
- render diffs and notes identifying meaningful differences;
- schema/policy results where tools are available;
- image digest source-of-truth and final-render assertion evidence;
- completed comparison matrix with locally measured observations;
- ADR with rejected alternatives, lifecycle ownership, risks, and revisit triggers;
- cleanup confirmation if a cluster was used;
- failure-drill notes for duplicate resources, a failed post-renderer, or an unsupported `helmCharts` feature.

These artifacts are expected learner outputs; they do not already exist. Redact sensitive values and never share production manifests or credentials.

## 15. Interview and design-review questions

### 1. Choose a packaging approach for a service shared by 30 teams.

**Model answer:** Usually prefer a versioned Helm chart or thin wrapper chart with a small supported values API, compatibility policy, schema validation, and consumer fixtures. The trade-off is chart authoring and API maintenance. Kustomize may still suit teams that require plain manifests, but a shared unversioned base can create implicit coupling. Evidence should include consumer requirements, rendered profiles, upgrade tests, and ownership. Revisit if consumers need no release contract and a simpler manifest interface demonstrably works.

### 2. Explain lifecycle and rollback differences between Helm-only and render-then-apply.

**Model answer:** Helm install/upgrade tracks a release and provides release history/rollback subject to external side-effect limitations. `helm template` followed by `kubectl apply` does not create the ordinary Helm release state for those objects; rollback belongs to the manifest deployment workflow. Evidence includes the exact deployment commands, release records, rendered artifacts, and a rehearsed rollback. A post-renderer used during Helm operations is a different pattern.

### 3. Design safe third-party chart customization and updates.

**Model answer:** Pin the chart, use documented values first, validate schemas, review release notes and rendered diffs, run policy and upgrade tests, and use a small post-render stage only when needed. Fork/vendor only with upstream tracking and CVE ownership. Failure modes include values API changes, patch targets breaking, and stale forks. A rendered diff helps but cannot prove runtime safety.

### 4. Diagnose double rendering or a failed post-renderer.

**Model answer:** Capture output after each stage, compare resource identities and final manifests, and verify exit codes. Check whether intermediate and final resources were both included. For a failed post-renderer, ensure the wrapper propagates non-zero status and the release operation stops. Add duplicate identity and failure-injection tests. Do not assume Helm silently ignores post-renderer failures; that symptom points to a defective wrapper or surrounding automation.

### 5. Create a golden-path policy that allows exceptions without tool sprawl.

**Model answer:** Define defaults by workload type, minimum validation/security gates, ownership, supported versions, and update cadence. Require an ADR for exceptions with owner, risk, expiry/revisit date, and evidence. Avoid a blanket tool mandate because workloads have different lifecycle needs. Review exceptions periodically and retire them when the original reason disappears. Evidence includes adoption, failure patterns, upgrade burden, and consumer feedback—not invented universal benchmarks.

## 16. ADR template

Use this template for a durable packaging decision.

```markdown
# ADR-NNN: <Packaging decision title>

- Status: Proposed | Accepted | Superseded
- Date: YYYY-MM-DD
- Decision owner:
- Reviewers:
- Affected services/teams:
- Review/revisit date:

## Context
- Workload and consumers:
- Deployment environments:
- Lifecycle and rollback requirements:
- Required security/validation gates:
- Operational constraints:

## Decision drivers
- Consumer audience and support contract:
- Configuration variance:
- Vendor/third-party dependencies:
- Release history/hooks/rollback needs:
- Review and debugging requirements:
- Team skills and ownership:
- Supply-chain and secret-handling constraints:

## Considered options
1. Helm only:
   - Advantages:
   - Costs/risks:
2. Kustomize only:
   - Advantages:
   - Costs/risks:
3. Combined pattern:
   - Advantages:
   - Costs/risks:
4. Other:

## Decision
- Selected approach:
- Why it fits:
- Explicit lifecycle owner:
- Source of truth for images/configuration:
- Rendered artifact and validation gates:

## Consequences
- Positive:
- Negative:
- Security implications:
- Migration/maintenance burden:
- Rollback plan:

## Evidence
- Tool versions:
- Rendered outputs/diffs:
- Schema/policy/test results:
- Consumer compatibility evidence:
- Known limitations:

## Revisit triggers
- Requirement change:
- Upgrade/CVE burden:
- Failure or drift signal:
- Consumer count/contract change:
```

### [ILLUSTRATIVE] Model ADR

**Title:** Use a versioned Helm chart for the shared scoring API package, with no Kustomize post-render stage initially.

**Context:** An internal platform team owns a FastAPI scoring API and expects other teams to consume it. The service needs dev/staging/prod configuration, rendered-diff review, and predictable upgrades. The initial workload has a manageable set of configurable fields, and the team can own chart tests and release operations.

**Decision:** Use Helm as the package and release lifecycle owner. Keep a small values API for replicas, image reference, resources, service settings, and approved configuration. Render each environment in CI and validate schema/policy/diffs. Maintain one canonical image digest input and verify every final rendered image. Do not introduce Kustomize until a concrete customization requirement is not expressible through the supported chart interface.

**Alternatives considered:**
- *Kustomize only:* simpler source YAML and overlays, but less aligned with the intended versioned package contract for independent consumers.
- *Helm render → Kustomize → direct apply:* can solve a patch gap, but complicates lifecycle ownership and loses ordinary Helm release tracking for directly applied objects.
- *Helm post-renderer:* preserves Helm release ownership but adds an executable dependency and a second transformation contract that is not currently required.

**Consequences:** The team owns chart interface compatibility, dependency updates, rendered review, and Helm rollback operations. Rollback does not reverse external side effects. CI must test all supported values profiles. If Kustomize is added later, it requires a separate ADR update or amendment, pinned tool versions, a clear post-render/apply lifecycle, and tests for chart upgrades.

**Revisit triggers:** Consumers require a stable plain-manifest artifact; chart values cannot express a required safe customization; the chart becomes difficult to maintain; or the team’s supported deployment workflow changes. This is one defensible decision, not the only correct answer.

## 17. Sources and verification notes

This chapter does not claim live documentation was consulted or commands were executed. Check documentation matching the installed tool versions before adopting version-sensitive syntax.

| Topic | Official source/document | URL | Version-sensitive? | Verify locally |
|---|---|---|---:|---|
| Helm chart format and values | Helm documentation | https://helm.sh/docs/ | Yes | Chart API version, values schema, commands |
| Helm rendering | Helm command reference, `helm template` | https://helm.sh/docs/helm/helm_template/ | Yes | Exact flags and output behavior |
| Helm install/upgrade/history/rollback | Helm command reference | https://helm.sh/docs/helm/ | Yes | Release state and rollback workflow |
| Helm post-renderers | Helm documentation, post-rendering | https://helm.sh/docs/topics/advanced/ | Yes | Exact executable contract and CLI flag |
| Kustomize bases/overlays | Kubernetes Docs, Kustomize | https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/ | Yes | Embedded version and supported features |
| Kustomize `helmCharts` | Kustomize project documentation | https://kubectl.docs.kubernetes.io/ and https://github.com/kubernetes-sigs/kustomize | Yes | `helmCharts` fields and enablement flag |
| Kubernetes apply/diff/dry-run | kubectl reference | https://kubernetes.io/docs/reference/kubectl/ | Yes | Exact command support |
| Semantic Versioning | Semantic Versioning specification | https://semver.org/ | Specification stable; chart conventions may vary | Versioning policy for chart API |
| Kubernetes workload behavior | Kubernetes workload docs | https://kubernetes.io/docs/concepts/workloads/ | API/resource-version dependent | Selectors, updates, immutable fields |
| GitHub Actions security | GitHub Docs, secure use reference | https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions | Yes | Pin actions and secure CI permissions |
| M02 Unit 9 promotion | Supplied roadmap | URL not applicable | Depends on local curriculum | Follow the authoritative M02 chapter |
| M08 GitOps | Supplied roadmap | URL not applicable | Controller/version dependent | Verify controller-specific support in M08 |
| M09 secret lifecycle | Supplied roadmap | URL not applicable | Depends on local curriculum | Follow approved secret lifecycle guidance |
| M16 platform golden paths | Supplied roadmap | URL not applicable | Depends on local curriculum | Follow platform standards in M16 |

### Verification notes

- `helmCharts` syntax, source fields, and `--enable-helm` are `[VERIFY][VERSION-SENSITIVE]`.
- Helm `--post-renderer` exact command behavior and executable contract must be verified against the installed Helm version.
- Embedded and standalone Kustomize may differ.
- A placeholder chart repository or `.invalid` image reference is not a real dependency.
- Helm rendering followed by direct `kubectl apply` is not equivalent to a Helm release install/upgrade.
- Rendering/schema validation, policy checks, and runtime tests are separate gates.
- Roadmap-specific boundaries: M08 owns GitOps details; M09 owns secret lifecycle; M16 owns broader platform golden paths; Unit 7 owns chart signature/trust topics.
- Engineering recommendations include pinning dependencies, reviewing final output, assigning a single owner per resource, and using ADRs for exceptions. These are recommendations, not guarantees provided by either tool.

## 18. Author's verification checklist

| Gate | Status | Evidence note |
|---|---|---|
| Exact target filename and M06 Unit 6 scope | PASS | Title and metadata match |
| L1–L4 topics | PASS | Fundamentals, framework, combinations, migrations, incidents |
| Exactly six worked decision scenarios | PASS | Section 6.2 |
| All six combination patterns | PASS | Section 7 |
| Lifecycle, drift, review, rollback, CI, security trade-offs | PASS | Each pattern discusses ownership and risks |
| Third-party chart customization, digest source, promotion, drift | PASS | Section 8 |
| Three migration playbooks and wrapper chart | PASS | Section 8 |
| Qualitative cost model without fabricated measurements | PASS | Section 8.9 |
| Eight incident analyses | PASS | Section 8.10 |
| Four-way same-app lab and comparison matrix | PASS | Section 12 |
| ADR template and illustrative model ADR | PASS | Section 16 |
| SRE/security/checklists/self-check/interview/evidence/sources | PASS | Sections 9–17 |
| Commands and rendered outputs executed locally | NOT VERIFIED | Learner must run using the recorded local toolchain |
| `helmCharts` compatibility with installed version | NOT VERIFIED | Syntax and flags are explicitly version-sensitive |
| Post-renderer behavior with installed Helm | NOT VERIFIED | Verify command contract and failure handling |
| Placeholder image/chart references are usable | NOT VERIFIED | Placeholders are intentionally illustrative |
| Repository modified | NOT CLAIMED | Only the requested Markdown artifact is generated |
