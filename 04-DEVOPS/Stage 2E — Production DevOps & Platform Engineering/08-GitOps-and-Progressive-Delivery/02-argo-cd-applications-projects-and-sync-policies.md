# Unit 2 — Argo CD: Applications, Projects, and Sync Policies

**Target file:** `02-argo-cd-applications-projects-and-sync-policies.md`  
**Module:** M08 — GitOps and Progressive Delivery | **Stage:** 2E  
**Estimated time:** 24–32 hours, including seven labs  
**Prerequisites:** M01–M07; `kind`, `kubectl`, Git, basic Helm/Kustomize rendering, Kubernetes RBAC and workload troubleshooting  
**Core tools:** Argo CD, `kind`, `kubectl`, `argocd` CLI, local Git server, Kustomize, Helm  
**Awareness only:** SSO, HA/sharding, notification integrations, admission-policy enforcement  
**Last reviewed:** 2026-10-28. Official documentation pages listed in Section 2.14 were consulted; no lab commands were executed.  
**Tool baseline:** `argoproj.io/v1alpha1` Application API as required by the curriculum; choose and record a release, then verify version-sensitive fields against it.  
**Footprint:** Planning estimates only, not measured results. The full local lab needs approximately 4 CPU cores, 8 GB RAM, and 30 GB disk. Run only one Argo CD lab stack at a time; stop other clusters, service meshes, Flux, and full observability stacks.

## Unit 2 — Argo CD: applications, projects, sync policies

> **Safety boundary:** Every lab is for a disposable local `kind` cluster and synthetic data. Do not use production repositories, real credentials, customer data, public endpoints, or clusters you do not own. Do not install Flux into the same cluster for these labs. Sample output is representative and was not captured from a run.

### 2.0 Why this matters in production

Argo CD makes Kubernetes delivery reviewable and repeatable, but it can also repeatedly apply a dangerous change. If an ApplicationSet generator stops producing an Application, the Application may be deleted; depending on owner references, finalizers, and policy, its workloads may be deleted too. If a permissive AppProject allows an Application to target another namespace or create a cluster-scoped `ClusterRoleBinding`, a team’s deployment workflow can become a privilege-escalation path.

The control objective is not merely to “install Argo CD.” It is to define source authority, allowed destinations and resource kinds, sync policy, deletion semantics, controller permissions, approval gates, evidence retention, and recovery procedures. Sync status, resource health, runtime SLI, and business correctness are different signals. A healthy model-scoring API can still produce bad predictions; a synced ETL workload can still deliver stale or incorrect data.

### 2.1 Learning objectives

- **[L1]** Explain Argo CD component roles and trust boundaries; verify the installed component inventory.
- **[L1]** Install a selected Argo CD release into disposable `kind`, verify readiness, access UI/CLI, and handle initial admin access safely.
- **[L1]** Read an `Application` manifest and trace source revision → fetch/render → diff → sync → live API state → health/status.
- **[L1]** Distinguish Sync (`Synced`/`OutOfSync`) from Health (`Healthy`, `Progressing`, `Degraded`, `Missing`, `Suspended`, `Unknown`) and business correctness.
- **[L2]** Deploy the same synthetic FastAPI scoring service from plain manifests, Kustomize, and Helm chart sources.
- **[L2]** Configure and verify manual/automated sync, `prune`, `selfHeal`, `allowEmpty`, retries, and sync options.
- **[L2]** Prove AppProject restrictions for unauthorized destinations and cluster-scoped kinds.
- **[L2]** Explain hooks/waves and migration Job idempotency without treating ordering as a transaction.
- **[L3]** Design ApplicationSets, compare app-of-apps with ApplicationSet, and reason about generated Application deletion.
- **[L3]** Harden RBAC, source/destination restrictions, repository credentials, admin access, TLS, plugins, network access, and diff customization.
- **[L4]** Plan Argo CD recovery/re-adoption, upgrades, tenancy, policy gates, performance, evidence retention, and incident response.
- **[L4]** Defend environment-specific sync/deletion policy with explicit trade-offs and residual risks.

### 2.2 Concept map and vocabulary

#### Architecture and trust boundaries

```mermaid
flowchart LR
    Dev[Engineer / bot] --> PR[Git PR, checks, approvals]
    PR --> Git[(Git desired-state repository)]
    Git -->|read-only source access| Repo[repo-server: fetch/cache/render]
    Repo --> Ctrl[application controller: diff and reconcile]
    Ctrl -->|Kubernetes API identity| KAPI[(Kubernetes API)]
    KAPI --> Workloads[Deployments, Services, Jobs, CRDs]
    KAPI --> Status[Live status, events, health assessment]
    Status --> Ctrl
    Ctrl --> API[Argo CD API server]
    User[UI / argocd CLI] <--> API
    API --> Auth[RBAC / SSO / local auth]
    API --> Redis[(Redis cache)]
    AppSet[ApplicationSet controller] -->|creates/updates Applications| KAPI
    Notify[Notifications controller, if installed] --> Sink[Webhook / notification sink]
    Policy[AppProject + Argo RBAC + cluster RBAC + admission policy] -. constrains .-> Ctrl
    Evidence[Git history + sync history + durable event export + runtime evidence] <-- Status
```

The diagram is conceptual. The exact component inventory varies by release and installation method. **[VERIFY]** inspect actual pods, deployments, CRDs, and release documentation; do not assume every optional component is installed.

| Component | Responsibility | Failure/trust boundary |
|---|---|---|
| API server | UI/CLI/API operations, authentication delegation, authorization, app status/operations, repository/cluster credential management and configured webhook entry points | Login or API operations may fail while existing workloads continue |
| repo-server | Fetches/caches source and renders Kubernetes manifests from revision/path and renderer settings | Fetch/render errors occur before Kubernetes apply |
| application controller | Compares desired and live state, orchestrates sync/hooks, reports app state | Failure/queue pressure delays reconciliation |
| Redis | Cache used by Argo CD components | Not the source of truth; cache issues can affect availability/performance |
| Dex/auth integration | Authentication broker when included/configured | Login/SSO failure may block users but not necessarily workloads |
| ApplicationSet controller | Generates/manages Applications from templates/generators | Generator/template change may affect many Applications |
| Notifications controller | Sends configured notifications when installed/configured | Notification failure does not necessarily mean sync failed; notifications alone are not durable audit |
| AppProject | Restricts source repos, destinations, resource kinds, optional project roles | Permissive project can widen deployment authority |
| Argo CD RBAC | Controls user actions through Argo CD | Does not replace Kubernetes RBAC |
| Kubernetes RBAC | Controls what controller identity may do to cluster API | Broad controller permissions increase blast radius |

#### Vocabulary

| Term | Definition | Misconception |
|---|---|---|
| `Application` | Custom resource describing source, destination, project, and sync policy | It is the workload itself |
| `AppProject` | Policy grouping that restricts sources, destinations, resource kinds, and project roles | It replaces Kubernetes RBAC |
| `ApplicationSet` | Controller-managed template/generator for multiple Application objects | It is just a YAML shortcut without deletion risks |
| Source | Repo/chart/OCI location and revision/path/renderer inputs | URL alone uniquely identifies deployed content |
| Destination | Target cluster and namespace | Namespace restriction alone prevents cluster-scoped privilege escalation |
| Sync status | Desired-versus-live comparison assessment | `Synced` means service is healthy/correct |
| Health status | Resource/application condition assessment | It proves business metrics are within SLO |
| Automated sync | Controller may initiate sync when comparison detects a change | It automatically implies prune and self-heal |
| Prune | Deletes tracked resources no longer rendered when enabled/applicable | Removing any file always deletes a live object |
| Self-heal | Corrects supported out-of-band differences when configured | It knows a manual edit was an emergency fix |
| `allowEmpty` | Controls whether automated sync may proceed when rendered desired resource set is empty | Harmless convenience flag |
| Hook / wave | Mechanisms for lifecycle phase and ordering | Makes multi-resource changes transactional |
| Finalizer | Delays object deletion while a controller performs cleanup | Deleting an Application only removes metadata |
| Resource tracking | Identifies live resources managed by an Application | Any matching label proves safe ownership |
| `ignoreDifferences` | Suppresses selected diffs under configured rules | Broad ignore rules are harmless |
| Render failure | Desired manifests cannot be fetched/generated | Same as API apply failure |
| Re-adoption | Re-establishing management of existing resources after controller rebuild | Safe to enable prune before ownership review |

#### Reconciliation flow

```text
Git revision → repo-server fetch/render → controller diff
            → policy/permissions → Kubernetes API apply
            → Kubernetes controllers converge → health/status
            → runtime checks + business checks + durable evidence
```

An apply is not a transaction across all resources. It does not prove that an API produces correct scores or that a data pipeline is fresh.

#### Sync versus Health

| Observation | Sync question | Health question | Additional evidence |
|---|---|---|---|
| Deployment spec matches desired | Does tracked live state match rendered desired state? | Are resources operational under health rules? | Readiness, logs, dependencies, SLI |
| Replica count differs after manual scale | Does comparison flag the field? | Are replicas ready? | Field owner, HPA config, live diff |
| `Synced` but image pull fails | Desired config may match | Resource likely not healthy | Pod events, registry and credentials |
| `Healthy` but prediction error rises | Resource comparison may be fine | Kubernetes health may not represent domain quality | Evaluation metrics and fallback ratio |
| `OutOfSync` because HPA manages replicas | A field differs | Service may be healthy | Ownership decision and narrow diff strategy |

**[VERIFY]** exact state vocabulary and health semantics for the selected Argo CD version and resource types.

#### Responsibility boundaries

| Object/control | Main responsibility | Does not replace |
|---|---|---|
| Application | One source/destination and sync policy | AppProject, RBAC, runtime monitoring |
| AppProject | Allowed sources/destinations/kinds and project roles | Git review, cluster RBAC, admission policy |
| ApplicationSet | Generates/manages Applications | Safe deletion policy or tenant isolation by itself |
| Argo CD RBAC | Who can manipulate Argo CD objects | Controller’s Kubernetes API authorization |
| Kubernetes RBAC | What controller identity may apply | Git review and source trust |
| CI policy | Pre-merge/render/schema checks | Admission enforcement or runtime proof |
| Admission policy | Rejects disallowed API requests | Correct application behavior |
| Evidence pipeline | Durable records and runtime signals | Source of desired state |

### 2.3 Level 1 — Beginner

#### 2.3.1 Choose and record a release

Do not invent a release number. Select a supported Argo CD release, read its release notes and installation instructions, and record the exact version.

```bash
kubectl version --client
kind version
argocd version --client
```

If `argocd` is not installed, the final command is expected to fail. Install the CLI using the selected release’s official instructions. **[VERIFY]** download path and CLI flags for your OS/release.

```bash
# Replace with the exact version chosen from official release notes.
ARGOCD_VERSION='<ARGOCD_VERSION>'
printf 'Selected Argo CD version: %s\n' "$ARGOCD_VERSION"
```

A placeholder is not executable until replaced.

#### 2.3.2 Create disposable kind cluster and guard context

**Footprint:** plan for 4 CPU/8 GB RAM/30 GB disk for the full lab; this is an estimate, not a measurement. Stop other heavy clusters, Flux, service mesh, and full observability stacks first.

```bash
kind create cluster --name argocd-unit2 --wait 120s
kubectl config get-contexts
kubectl config current-context
kubectl cluster-info
```

Set the expected context to the exact value printed by `kubectl config current-context`; do not assume it is named `kind-argocd-unit2`.

```bash
EXPECTED_CONTEXT='<EXACT_CONTEXT_FROM_YOUR_OUTPUT>'
CURRENT_CONTEXT="$(kubectl config current-context)"
if [ "$CURRENT_CONTEXT" != "$EXPECTED_CONTEXT" ]; then
  printf 'Refusing: expected %s, got %s\n' "$EXPECTED_CONTEXT" "$CURRENT_CONTEXT" >&2
  exit 1
fi
```

A context guard is not proof that a cluster is disposable. Confirm cluster identity and ownership before destructive actions.

#### 2.3.3 Install Argo CD

**[VERIFY]** follow the official installation instructions for the selected release. The URL below is a pattern, not a tested URL or a claim that installation was performed.

```bash
# Replace <ARGOCD_VERSION> with a verified release tag.
kubectl create namespace argocd
kubectl apply -n argocd \
  -f "https://raw.githubusercontent.com/argoproj/argo-cd/<ARGOCD_VERSION>/manifests/install.yaml"
kubectl get pods -n argocd -w
```

If pods fail readiness, inspect before retrying:

```bash
kubectl get deployments,statefulsets,pods -n argocd
kubectl get events -n argocd --sort-by=.lastTimestamp
kubectl describe pods -n argocd
```

**Representative expected output — not captured from a run:**

```text
NAME                                READY   STATUS    RESTARTS
argocd-server-...                   1/1     Running   0
argocd-repo-server-...               1/1     Running   0
argocd-application-controller-...   1/1     Running   0
```

Actual names, component count, and readiness depend on release/install mode.

#### 2.3.4 Access UI and CLI safely

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open `https://localhost:8080`. Do not create a public Ingress/LoadBalancer for this lab. A local certificate warning is not justification to disable TLS verification for production.

Retrieve the initial admin password only for this disposable lab; avoid printing it into logs or shell history. The exact secret name/workflow is release-sensitive. Inspect the secrets and follow the selected version’s official bootstrap guide. Rotate the password or disable built-in admin access after bootstrap according to the supported workflow. Do not leave bootstrap credentials as the final state.

For CLI login, use the forwarded endpoint and verify `argocd login --help` for the selected version. Do not use `--insecure` as a general fix.

#### 2.3.5 First Application: plain manifests

The Application API group/version required by the curriculum is `argoproj.io/v1alpha1`; validate it against the installed CRD before applying.

**File: `config-repo/apps/scoring-api/plain/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: dev
  labels:
    app.kubernetes.io/name: scoring-api
    app.kubernetes.io/part-of: data-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
        app.kubernetes.io/part-of: data-platform
    spec:
      containers:
        - name: api
          # Replace with a reachable, approved digest from M01.
          image: registry.example.invalid/data/scoring-api@sha256:<REPLACE_WITH_REAL_DIGEST>
          ports:
            - name: http
              containerPort: 8000
          readinessProbe:
            httpGet:
              path: /ready
              port: http
          livenessProbe:
            httpGet:
              path: /health
              port: http
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
```

The image is intentionally a placeholder and is not deployable until replaced. The service is assumed to expose `/health`, `/ready`, and port 8000; align with the actual M01 implementation.

**File: `config-repo/apps/scoring-api/plain/service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: dev
  labels:
    app.kubernetes.io/name: scoring-api
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
  type: ClusterIP
```

For the **plain-manifest phase**, keep only the Kubernetes YAML files in this directory and do not include a `kustomization.yaml`; that lets Argo CD interpret the directory as plain manifests. The separate Kustomize phase below deliberately includes a `kustomization.yaml`. Verify rendered output in the selected Argo CD release before syncing.

**File: `config-repo/argocd/applications/scoring-api-dev-plain.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: scoring-api-dev-plain
  namespace: argocd
spec:
  project: data-platform-dev
  source:
    repoURL: http://gitea.gitops-lab.svc.cluster.local:3000/lab/config-repo.git
    targetRevision: main
    path: apps/scoring-api/plain
  destination:
    server: https://kubernetes.default.svc
    namespace: dev
  syncPolicy: {}
```

The URL assumes a local Gitea service named `gitea` in namespace `gitops-lab` and repo path `lab/config-repo.git`; match it to your actual setup. Plain HTTP is only for the disposable local lab, not production. `Application` lives in `argocd`; workload targets `dev`. Create the AppProject first.

Inspect the CRD and Application:

```bash
kubectl get crd applications.argoproj.io
kubectl get application scoring-api-dev-plain -n argocd -o yaml
```

With manual sync, inspect the diff and explicitly sync through UI/CLI. Creating an Application does not prove its resources have been applied.

#### 2.3.6 Status and diff

```bash
argocd app get scoring-api-dev-plain
argocd app diff scoring-api-dev-plain
argocd app history scoring-api-dev-plain
kubectl get deployments,services,pods -n dev
kubectl get events -n dev --sort-by=.lastTimestamp
```

Triage by phase:
- **Source/render:** repository auth, revision, path, renderer/chart values, repo-server logs.
- **Comparison:** inspect the resource-level diff and tracking ownership.
- **Apply/sync:** inspect operation details, API errors, RBAC, quotas, admission, and CRDs.
- **Health:** inspect scheduling, image pull, probes, logs, dependencies.
- **Business:** inspect prediction quality, fallback ratio, data freshness, latency, and domain metrics.

**Representative expected output — not captured from a run:**

```text
Name:               argocd/scoring-api-dev-plain
Project:            data-platform-dev
Sync Status:        OutOfSync
Health Status:      Missing
```

This is illustrative only; exact labels/format may vary.

#### 2.3.7 Application deletion and finalizer

**⚠ DESTRUCTIVE — DISPOSABLE LAB ONLY**

An Application may carry `resources-finalizer.argocd.argoproj.io` (foreground) or `resources-finalizer.argocd.argoproj.io/background`. With the finalizer, deleting the Application can cause Argo CD to delete managed resources. Verify exact semantics for the chosen release and deletion path.

Before deletion:
1. Confirm context.
2. Inspect source, destination, project, finalizers, sync policy, and tracked resource list.
3. Confirm all listed resources are disposable.
4. Decide whether the intent is to delete workloads or preserve them and stop Argo CD management.
5. Use the version-verified retain/non-cascade procedure; do not strip finalizers blindly.

A manifest that omits the finalizer may be appropriate for a retain-resource lifecycle, but ApplicationSet owner references and other deletion policies still matter. Lab F demonstrates this safely.

#### Common beginner mistakes

| Symptom | Cause | Safe diagnosis | Correction |
|---|---|---|---|
| App exists, no workload | Manual sync not run or source/render failed | App status, source path, repo-server logs, diff | Fix source and sync after diff review |
| Synced but service fails | Sync is not runtime/business health | Pods, events, logs, SLIs | Fix readiness/dependency and add domain checks |
| Destination rejected | AppProject disallows it | Inspect project and app status | Explicitly allow only the intended target |
| Deleting Application removes workload | Cascading finalizer/policy | Inspect finalizers, owner refs, audit/events | Restore only after impact and ownership review |
| Helm render fails | Wrong chart/source/values or unsupported field | repo-server logs and local `helm template` | Align source and version-specific schema |
| OutOfSync on replicas repeatedly | HPA/operator and Argo CD compete | Diff, HPA, managed fields | Assign field ownership; narrow ignore only if justified |
| CLI login fails | Port-forward/TLS/credentials/version mismatch | Check local endpoint and exact error | Fix endpoint/auth; don't disable TLS globally |

### 2.4 Level 2 — Intermediate

#### 2.4.1 Three source types for the FastAPI service

The M01 image should be digest-pinned; this unit does not rebuild or sign it. CI tests/publishes the immutable artifact and proposes a desired-state change to Git (M02 handoff). The same service contract is assumed: synthetic scoring endpoint, `/health`, `/ready`, version/build metadata, and optionally a local metrics endpoint.

#### Kustomize base and dev overlay

**File: `config-repo/apps/scoring-api/kustomize/base/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  labels:
    app.kubernetes.io/name: scoring-api
    app.kubernetes.io/part-of: data-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
        app.kubernetes.io/part-of: data-platform
    spec:
      containers:
        - name: api
          image: registry.example.invalid/data/scoring-api@sha256:<REPLACE_WITH_REAL_DIGEST>
          ports:
            - name: http
              containerPort: 8000
          readinessProbe:
            httpGet:
              path: /ready
              port: http
          livenessProbe:
            httpGet:
              path: /health
              port: http
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
```

**File: `config-repo/apps/scoring-api/kustomize/base/service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  labels:
    app.kubernetes.io/name: scoring-api
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
```

**File: `config-repo/apps/scoring-api/kustomize/base/kustomization.yaml`**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
```

**File: `config-repo/apps/scoring-api/kustomize/overlays/dev/kustomization.yaml`**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: dev
resources:
  - ../../base
replicas:
  - name: scoring-api
    count: 1
commonLabels:
  app.kubernetes.io/environment: dev
images:
  - name: registry.example.invalid/data/scoring-api
    newName: registry.example.invalid/data/scoring-api
    digest: sha256:<REPLACE_WITH_REAL_DIGEST_HEX>
```

Replace the digest placeholder with a real approved digest; ensure `images.name` matches the base image. Verify the rendered output:

```bash
kubectl kustomize apps/scoring-api/kustomize/overlays/dev
```

**File: `config-repo/argocd/applications/scoring-api-dev-kustomize.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: scoring-api-dev-kustomize
  namespace: argocd
spec:
  project: data-platform-dev
  source:
    repoURL: http://gitea.gitops-lab.svc.cluster.local:3000/lab/config-repo.git
    targetRevision: main
    path: apps/scoring-api/kustomize/overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: dev
  syncPolicy: {}
```

Argo CD renders Kustomize; do not run `kubectl apply -k` as a second owner of the same resources.

#### Helm chart in Git

Argo CD generally renders Helm sources and applies rendered resources; this differs from `helm install` owning a conventional Helm release lifecycle. Verify hooks, `lookup`, tests, and `helm list` behavior for the selected version. The chart is committed locally to avoid public chart dependencies.

**File: `config-repo/apps/scoring-api/helm/Chart.yaml`**

```yaml
apiVersion: v2
name: scoring-api
description: Disposable FastAPI scoring chart for Argo CD training
type: application
version: 0.1.0
appVersion: "1.0.0"
```

**File: `config-repo/apps/scoring-api/helm/values.yaml`**

```yaml
replicaCount: 1
image:
  repository: registry.example.invalid/data/scoring-api
  digest: "sha256:<REPLACE_WITH_REAL_DIGEST_HEX>"
service:
  port: 80
  targetPort: 8000
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**File: `config-repo/apps/scoring-api/helm/templates/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
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
      containers:
        - name: api
          image: "{{ .Values.image.repository }}@{{ .Values.image.digest }}"
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
          readinessProbe:
            httpGet:
              path: /ready
              port: http
          livenessProbe:
            httpGet:
              path: /health
              port: http
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

**File: `config-repo/apps/scoring-api/helm/templates/service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}
  labels:
    app.kubernetes.io/name: scoring-api
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: http
```

**File: `config-repo/argocd/applications/scoring-api-dev-helm.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: scoring-api-dev-helm
  namespace: argocd
spec:
  project: data-platform-dev
  source:
    repoURL: http://gitea.gitops-lab.svc.cluster.local:3000/lab/config-repo.git
    targetRevision: main
    path: apps/scoring-api/helm
    helm:
      valueFiles:
        - values.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: dev
  syncPolicy: {}
```

**[VERIFY]** Application source schema, `valueFiles` behavior, `valuesObject`, and multi-source capability for the chosen release. Do not deploy the plain/Kustomize/Helm examples concurrently into the same namespace with colliding resource names. Use separate phases, unique names, or separate namespaces; remove prior test resources only after inspecting ownership and deletion behavior.

#### 2.4.2 AppProject: restrictive by default

**File: `config-repo/argocd/projects/data-platform-dev.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: data-platform-dev
  namespace: argocd
spec:
  description: Disposable dev-only project for model scoring training
  sourceRepos:
    - http://gitea.gitops-lab.svc.cluster.local:3000/lab/config-repo.git
  destinations:
    - server: https://kubernetes.default.svc
      namespace: dev
  clusterResourceWhitelist: []
  namespaceResourceWhitelist:
    - group: apps
      kind: Deployment
    - group: ""
      kind: Service
    - group: ""
      kind: ConfigMap
```

The example does not allow cluster-scoped resources. Add only the namespaced kinds required by the service. If a Secret is required, allowing the Kubernetes Secret kind does not authorize committing plaintext secrets to Git. Namespace creation and CRD/operator management should usually be owned by a separate platform path.

**Restriction proof**
1. Apply the project in `argocd`.
2. Deploy the service to allowed namespace `dev`.
3. Create a throwaway Application that targets `staging`; inspect the denial/failure.
4. Create another throwaway Application containing a `ClusterRoleBinding`; inspect whether AppProject validation, Kubernetes RBAC, or admission rejected it.
5. Confirm allowed deployment still works.
6. Do not use cluster-admin success as evidence of tenant isolation. Test the intended Application/project path and record the enforcement layer.

#### 2.4.3 Sync policy and sync options

Automated sync, self-heal, prune, and allow-empty are separate controls.

| Mode/option | Effect | Benefit | Risk | Starting point |
|---|---|---|---|---|
| Manual sync | Human/authorized automation initiates sync | Explicit review point | Pending changes can be forgotten | First app and sensitive environments |
| Automated sync | Controller initiates sync when OutOfSync | Faster repeatable delivery | Bad merge may deploy quickly | Dev/staging after CI and ownership controls |
| `selfHeal: true` | Corrects supported out-of-band live differences | Reduces drift | Can undo emergency fix or fight HPA/operator | Enable after field ownership and break-glass are clear |
| `prune: true` | Deletes tracked resources absent from desired render | Removes stale objects | Wrong path or empty render can delete resources | Stage after inventory/deletion tests |
| `allowEmpty: false` | Guards against automated sync with zero rendered resources | Reduces accidental mass deletion | Does not protect against every wrong non-empty render | Keep false unless a reviewed need exists |
| `CreateNamespace=true` | Creates destination namespace as part of sync, subject to policy/permissions | Convenience | Namespace ownership/lifecycle risk | Prefer platform-owned namespace until lifecycle is clear |
| `PruneLast=true` | Makes pruning a final implicit wave after other sync resources complete/healthy | Can protect dependency ordering | Does not make deletion safe or transactional | Consider for a tested dependency case |
| `Replace=true` | Uses replace/create semantics instead of normal apply | Can solve a narrow apply limitation | May recreate resource/cause outage | Avoid global enablement |
| `ServerSideApply=true` | Uses server-side apply and field management | Useful for some large/shared objects | Conflicts/force behavior may overwrite fields | Only with explicit field-owner plan |
| `ApplyOutOfSyncOnly=true` | Applies only resources considered OutOfSync | May reduce API pressure | Hooks/history have special behavior | Consider after measurement |
| `RespectIgnoreDifferences=true` | Applies ignored-field behavior during sync as documented | Avoids overwriting fields delegated elsewhere | Broad ignores conceal dangerous drift | Narrow reviewed paths only |
| `Validate=false` | Disables normal validation in the documented apply path | Narrow special cases | Hides schema errors | Do not use to silence unexplained failures |

**[VERIFY]** names, defaults, and semantics against the selected release’s Application specification and Sync Options docs. Inspect the diff and prove behavior with a disposable resource.

#### 2.4.4 Retry/backoff and failure analysis

Retries help transient source/API conditions. They do not fix invalid YAML, forbidden destinations, missing CRDs, inadequate permissions, bad digests, or permanently unreachable repositories. Blind retries can create noise and obscure the first useful failure.

1. Confirm Application, project, source revision, cluster, namespace.
2. Check repository access, revision/path, renderer/chart values.
3. Inspect repo-server logs and render locally with matching tool versions.
4. Check AppProject, global Argo RBAC, Kubernetes RBAC, and admission.
5. Check API errors, quota, CRDs, validation, immutable fields, and events.
6. Check scheduling, image pull, probes, dependencies, and logs.
7. Check runtime/business signals.
8. Retry only after correcting the root cause or identifying a transient condition.

#### 2.4.5 Sync waves and hooks

Hooks define lifecycle phases; waves order resources within a sync. Common phases include `PreSync`, `Sync`, `PostSync`, and `SyncFail`. Exact current hook list and semantics are `[VERIFY]`. Neither hooks nor waves make a multi-resource operation transactional.

**File: `config-repo/apps/scoring-api/hooks/migration-marker.yaml`**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: scoring-api-schema-marker
  namespace: dev
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/sync-wave: "-1"
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation,HookSucceeded
spec:
  backoffLimit: 1
  activeDeadlineSeconds: 120
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api-schema-marker
    spec:
      restartPolicy: Never
      containers:
        - name: marker
          image: busybox:1.36
          command: ["/bin/sh", "-ec"]
          args:
            - |
              # Teaching marker only; this is not a database migration.
              test -f /etc/os-release
              echo "pre-sync marker passed"
```

This is an ordering demo only; it does not connect to a database. A real migration needs a dedicated immutable image, credentials, idempotency, migration ledger, compatibility checks, timeout/locking strategy, backup/PITR, and recovery procedure. See [Unit 11 — Database and data-platform migration safety](11-database-and-data-platform-migration-safety.md).

To test failure, change the marker command in a separate commit to exit non-zero, sync, and capture Job logs, events, and Application operation state. Do not blindly retry if a hook may have changed external state.

#### 2.4.6 RBAC and project roles

Global Argo CD RBAC and Kubernetes RBAC are different layers. The former controls user actions through Argo CD; AppProject roles can scope application actions; Kubernetes RBAC controls what the controller identity can do. Verify policy syntax and group mappings for the installed release.

**File: `config-repo/argocd/rbac/argocd-rbac-cm.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
data:
  policy.default: role:readonly
  policy.csv: |
    p, role:dev-readonly, applications, get, data-platform-dev/*, allow
    p, role:dev-sync, applications, get, data-platform-dev/*, allow
    p, role:dev-sync, applications, sync, data-platform-dev/*, allow
    g, data-platform-dev-readers, role:dev-readonly
    g, data-platform-dev-deployers, role:dev-sync
  scopes: '[groups]'
```

This is a teaching example, not a validated production policy. Verify ConfigMap name/namespace, action/object syntax, group claims, and whether another permission path allows users to edit Applications/Projects. A role intended only to sync must not accidentally allow source/destination edits.

#### 2.4.7 Repository credentials and destination registration

- Use read-only, narrowly scoped repository credentials.
- Verify SSH host keys/TLS certificates; do not disable verification as a default fix.
- Keep credentials out of Git, manifests, logs, command history, and evidence.
- For local Gitea, Argo CD must resolve a service DNS name from its own network. `localhost` inside a container is not the host or another container.
- Same-cluster destination is commonly `https://kubernetes.default.svc`; verify the selected install and destination registration.
- External-cluster registration is awareness-only here; it requires separate identity, network, and blast-radius design.
- Never store cluster-admin credentials in the config repository.

#### 2.4.8 Declarative configuration and app-of-apps

Argo CD Applications, AppProjects, repository configuration, and selected controller settings can themselves be managed declaratively. App-of-apps uses a parent Application to manage child Application manifests. It introduces an ownership/deletion relationship: pruning or deleting a child Application may delete its workloads depending on finalizers and policy.

Use it only when parent source/permissions are tightly controlled, child ownership is explicit, deletion behavior is tested, privileged child apps are restricted, bootstrap ordering is documented, and a recovery path is understood. ApplicationSet can be better for many templated Applications, but it has its own generator and deletion risks.

#### 2.4.9 Pattern catalogue

| Pattern | Use when | Avoid when |
|---|---|---|
| Manual production sync | Explicit release decision is required | Pending changes become an unmonitored queue |
| Auto-sync dev/staging | CI gates and rollback are mature | Review/test bypass is possible |
| Self-heal stateless config | Drift should be corrected | Emergency changes have no record or field ownership conflicts |
| Selective prune | Ownership inventory is proven | Resource lifecycle is ambiguous |
| Dedicated AppProject | Team/environment boundaries differ | Project can be edited by the same untrusted team |
| App-of-apps | Small central hierarchy | Parent source can create privileged child apps |
| ApplicationSet | Repeated templated Applications | Generator input is untrusted or deletion is unguarded |
| Chart in Git | Reproducible local training and review | Team assumes traditional Helm release semantics |
| Narrow ignore-diff | Field is owned by another controller | It hides image/security/RBAC changes |
| `Replace=true` for one resource | A documented apply limitation exists | It is globally enabled without testing |

#### 2.4.10 Anti-pattern catalogue

| Bad workflow/config | Failure mechanism | Safer alternative |
|---|---|---|
| Source/destination/resource wildcards | Broad deployment authority | Explicit allow-lists and negative tests |
| All apps use permissive `default` project | Weak tenant boundary | Dedicated projects and protected project edits |
| Prune before inventory review | Manifest/path mistake deletes resources | Inspect deletion diff; staged prune |
| `allowEmpty: true` plus prune | Empty render may remove all tracked objects | Keep false unless use case and safeguards are explicit |
| Plaintext secret in Git/Helm values | Secret persists in history/clones | Reference/encrypted workflow and rotation |
| Global `Replace=true` | Resource recreation/outage | Resource-specific justified setting |
| Broad ignore rules | Dangerous drift hidden | Narrow field paths and regression test |
| Untrusted CMP plugin | Code executes in render trust boundary | Pin/review/sandbox/restrict plugin |
| Delete Application to clean UI | Finalizer may delete workloads | Explicit retain/cascade decision |
| Rename ApplicationSet directory without preview | Generated app deletion/cascade | Preview generated inventory and test policy |
| Two Applications own same resource | Conflicting sync/prune | One authoritative owner |
| Retry forever | Permanent failure persists and logs get noisy | Diagnose source, render, policy, apply, health phases |

### 2.5 Level 3 — Advanced

#### 2.5.1 ApplicationSet generators and templates

ApplicationSet generates Applications from templates and generator inputs. The curriculum names List, Cluster, Git directory/files, Matrix/Merge, and Pull Request generators. **[VERIFY]** generator availability, API fields, Go-template behavior, and deletion policy against the selected release.

| Generator | Input | Benefit | Risk |
|---|---|---|---|
| List | Explicit key/value entries | Small bounded set | Editing list can alter many destinations |
| Cluster | Registered cluster inventory | Fleet-oriented generation | Newly registered clusters may become targets |
| Git directory | Repository directories | Simple per-environment/service generation | Rename/removal can delete generated Applications |
| Git files | Structured metadata files | Flexible app/environment metadata | Missing/wrong fields can target wrong config |
| Matrix/Merge | Combined generator results | Flexible composition | Expansion and precedence can be hard to reason about |
| Pull Request | SCM provider PR inventory | Preview environments | Usually requires provider API credentials; not required in this local lab |

**File: `config-repo/argocd/applicationsets/scoring-api-environments.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: scoring-api-environments
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: http://gitea.gitops-lab.svc.cluster.local:3000/lab/config-repo.git
        revision: main
        directories:
          - path: apps/scoring-api/environments/dev
          - path: apps/scoring-api/environments/staging
  # Safe lab posture: preserve generated Applications' managed resources on
  # ApplicationSet deletion. Verify field and semantics for selected release.
  syncPolicy:
    preserveResourcesOnDeletion: true
  template:
    metadata:
      name: 'scoring-api-{{path.basename}}'
      labels:
        app.kubernetes.io/name: scoring-api
        app.kubernetes.io/managed-by: applicationset
    spec:
      project: data-platform-dev
      source:
        repoURL: http://gitea.gitops-lab.svc.cluster.local:3000/lab/config-repo.git
        targetRevision: main
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: false
          selfHeal: false
```

This is illustrative; validate against installed CRDs. The AppProject must explicitly permit only `dev` and `staging` for this example. The source repository must contain both directories, each with valid resources. Template fields such as `path` and `path.basename` depend on generator/template mode; verify the exact syntax.

**Deletion hazard:** removing/renaming a generated directory can remove an Application from generator output. Owner references, finalizers, and preservation/deletion policy determine whether workloads are also removed. Inspect generated inventory before every path change.

#### 2.5.2 App-of-apps versus ApplicationSet

| Dimension | App-of-apps | ApplicationSet |
|---|---|---|
| Model | Parent Application manages child Application YAML | Generator creates/manages Applications from templates/input |
| Best fit | Small centrally reviewed hierarchy | Many similar apps/environments/clusters |
| Reviewability | Child Application changes explicit in repo | Template changes can affect many apps; generated output needs review |
| Dynamic discovery | Usually parent manifests and repo structure | Built-in generator families |
| Deletion risk | Parent prune/deletion can remove child Applications | Generator input/removal can delete generated Applications |
| Security | Parent source must not create privileged child apps | Generator/template must constrain source/destination |
| Debugging | Parent → child Application → workload | Generator input → generated Application → workload |

Neither pattern automatically provides tenant isolation. A user who can change a parent or ApplicationSet may indirectly request privileged deployment unless projects, Argo RBAC, Kubernetes RBAC, and admission policy constrain it.

#### 2.5.3 Multi-source Applications

Multi-source Applications can combine sources such as a chart and configuration from another repository. Exact fields, precedence, status display, and revision behavior are `[VERIFY]`. Multiple sources improve composition but complicate provenance: record every source revision, define who owns each input, and preserve the rendered output/diff. A single source is easier to audit when composition provides little value.

#### 2.5.4 Resource tracking and diff customization

Argo CD must associate live objects with Applications. Tracking modes and collision behavior are release-sensitive; verify label/annotation-related modes before changing them. Never copy tracking metadata from one Application to another or let two Applications own the same resource identity.

`ignoreDifferences` is appropriate only when a field is intentionally owned by another controller, such as HPA-managed replicas. It is not a generic way to silence drift.

**File: `config-repo/argocd/applications/scoring-api-hpa-aware.yaml`**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: scoring-api-hpa-aware
  namespace: argocd
spec:
  project: data-platform-dev
  source:
    repoURL: http://gitea.gitops-lab.svc.cluster.local:3000/lab/config-repo.git
    targetRevision: main
    path: apps/scoring-api/kustomize/overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: dev
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
  syncPolicy:
    syncOptions:
      - RespectIgnoreDifferences=true
```

Use this only if an HPA or other named owner controls `spec.replicas`. Verify current semantics; do not apply it to another Application managing the same resources. Test that image, security context, and RBAC changes still appear in diffs.

#### 2.5.5 Security hardening matrix

| Threat | Control | Verification evidence | Residual risk |
|---|---|---|---|
| Malicious Git change | Protected branches, review, checks, digest pinning | Test PR, approval and CI records | Reviewer/CI compromise |
| Broad AppProject | Explicit source/destination/kind allow-lists | Project YAML + negative tests | Project editor can weaken it |
| Overbroad global Argo RBAC | Least-privilege roles | RBAC config + prohibited-action test | Other group mappings may grant access |
| Controller has cluster-admin | Reduce supported permissions; separate scope | Effective bindings and denied-operation test | Some features may require broad access |
| Admin credential leak | Rotate/disable built-in admin; audit | Account config, rotation evidence | Break-glass account still sensitive |
| Repo credential leak | Read-only, scoped, rotated credentials | Inventory, access audit, secret scan | Repo-server/cache/log exposure |
| CMP plugin compromise | Pin/review/sandbox; restrict file/network access | Plugin image/config and network tests | Plugin processes rendered data |
| TLS/host-key bypass | Verify certificate and host key | Repo connection/trust config | Lab HTTP is not production-safe |
| Unsafe prune | Review deletion diff, staged prune, backups | Disposable prune test | Reviewer can still approve bad deletion |
| ApplicationSet cascade | Inventory preview, preserve/deletion policy | Before/after generated app list | Version-specific behavior |
| Broad ignore rule | Narrow paths and regression tests | Test that image/RBAC changes remain visible | Rules may become stale |
| Unauthorized network access | NetworkPolicy after mapping required flows | Allowed/denied connectivity tests | CNI and actual ports vary |
| Cluster-scoped escalation | Restrict kinds and controller RBAC; admission controls | ClusterRoleBinding negative test | Other privileged paths may remain |
| Secrets in Git | References/approved encryption, scanning | CI scan and sanitized review | Decrypted render/cache may still be sensitive |
| Sync-window emergency conflict | Bounded break-glass and post-review | Blocked-sync proof and change record | Human process may fail |

M04 covers NetworkPolicy. Do not apply default-deny policy before mapping DNS, Kubernetes API, Git, UI/CLI, Redis, repo-server, notifications, and metrics flows. CMP plugins execute code in the render trust boundary; only trusted, pinned, reviewed plugins should be considered.

#### 2.5.6 Production approval and sync windows

A common starting point—not a universal standard—is automated sync in dev/staging after CI gates and reviewed promotion/manual sync in production. Automated production sync can be appropriate when checks, immutable artifacts, blast-radius controls, and recovery are mature. Manual sync reduces some accidental deployment risk but can delay urgent changes and create unmonitored queues.

**[VERIFY]** sync-window schema and behavior for the chosen release. Document break-glass requester, approver, scope, time limit, pause/override mechanism, Git follow-up, verification, and post-incident review. Do not disable reconciliation indefinitely.

#### 2.5.7 Upgrade, scaling, and repo-server performance

- Pin and record the Argo CD release.
- Read release notes and check CRD changes before upgrades.
- Test upgrade/rebuild on an ephemeral kind cluster.
- Preserve Git access, credentials, and bootstrap configuration independently of the controller.
- Monitor repo-server render time, Git fetch failures, pending repository work, plugin execution, cache behavior, large repos/charts, and provider rate limits.
- Do not invent metric names. Official current documentation includes repo-server Git request/fetch and repository parallelism indicators; verify actual endpoint/labels for the installed version.
- HA/sharding and production sizing are awareness-level here; a laptop install is not HA.

#### 2.5.8 Notifications and audit

Notifications are useful alerts, not automatically durable evidence. Configure notification triggers and sinks using the selected release docs. A local HTTP receiver or log sink can demonstrate delivery without external services. Test whether records survive controller restart and whether they contain commit, Application, result, and timestamp. See [Unit 13 — Release evidence and audit trails](13-release-evidence-and-audit-trails.md).

### 2.6 Level 4 — Expert

#### 2.6.1 HA/DR and re-adoption

Git can reconstruct declarative configuration but is not a complete backup. Recovery also requires credentials/keys, application data, database backups/PITR, external resource inventory, image/chart availability, identity access, and tested restoration.

**Rebuild/re-adopt runbook**
1. **Blast-radius check:** identify clusters, controller release, affected Applications, namespaces, source repos, and ongoing deletions.
2. Preserve Application YAML, resource inventory, logs/events, and audit evidence.
3. Recover Git access and credentials through approved identity/secret processes; do not put missing secrets in Git.
4. Rebuild the controller from recorded release/bootstrap inputs.
5. Before enabling sync/prune, inspect every Application’s source/destination/project and compare rendered desired state to live resources.
6. Verify tracking and adoption behavior for the selected release.
7. Start with a low-risk app with prune disabled; compare diffs and ensure no unexpected delete/create actions.
8. Re-adopt in batches. Enable self-heal/prune only after ownership is confirmed.
9. Verify runtime SLIs, business metrics, and data integrity.
10. Record what Git could not restore and update the DR test.

#### 2.6.2 Multi-tenancy and privilege escalation

A Project per team is useful only if Project edit rights and controller Kubernetes permissions are also bounded. A user who can edit an Application’s source/destination or an ApplicationSet template may exercise the controller identity. A project allowing dangerous cluster-scoped resources can expand authority beyond a namespace.

Separate powers to write source, write config, approve prod, create/edit Applications, create/edit AppProjects, register repos/clusters, change controller config, perform Kubernetes writes, and approve break-glass. For every identity, record allowed actions and test one prohibited action. AppProject restrictions are necessary but not a standalone tenant-isolation guarantee.

#### 2.6.3 Policy-as-code

CI should render the exact source and fail for unapproved sources/destinations, missing project assignment, forbidden resource kinds, missing ownership labels, placeholders/mutable production images, plaintext secrets, prohibited prune/allowEmpty, and broad ignore rules. CI policy is not admission enforcement: a privileged user or alternate API path may bypass it. M12 covers admission and signature enforcement.

**File: `config-repo/scripts/check-argocd-policy.py`**

```python
#!/usr/bin/env python3
"""Illustrative policy sketch only; not a production YAML security boundary."""
from pathlib import Path
import re
import sys

ALLOWED_PROJECTS = {"data-platform-dev", "data-platform-staging", "data-platform-prod"}
ALLOWED_SOURCES = {"http://gitea.gitops-lab.svc.cluster.local:3000/lab/config-repo.git"}
FORBIDDEN_KINDS = {"ClusterRoleBinding", "ClusterRole", "CustomResourceDefinition"}

def main(path: str) -> int:
    text = Path(path).read_text(encoding="utf-8")
    failures = []
    if "kind: Application" in text:
        if not re.search(r"(?m)^\s*project:\s*(data-platform-dev|data-platform-staging|data-platform-prod)\s*$", text):
            failures.append("Application must name an allowed project")
        for source in re.findall(r"(?m)^\s*repoURL:\s*(\S+)\s*$", text):
            if source not in ALLOWED_SOURCES:
                failures.append(f"Unapproved source: {source}")
    for kind in FORBIDDEN_KINDS:
        if re.search(rf"(?m)^\s*kind:\s*{re.escape(kind)}\s*$", text):
            failures.append(f"Forbidden kind: {kind}")
    if "REPLACE_WITH_REAL_DIGEST" in text or "<REPLACE_WITH_REAL_DIGEST" in text:
        failures.append("Placeholder digest remains")
    if failures:
        print("\n".join("FAIL: " + item for item in failures), file=sys.stderr)
        return 1
    print("PASS: static subset only; YAML parsing, schema, RBAC and admission need separate checks")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} <rendered-yaml>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
```

This regex-based sketch can be bypassed by YAML structure variations. It is intentionally not production-grade. Replace with a maintained YAML parser, CRD/schema validation, per-object policy evaluation, and negative fixtures before use in CI.

#### 2.6.4 Seven incident playbooks

Use **symptom → hypothesis → safe test → blast-radius/rollback check → mitigation → prevention → evidence**. Do not remediate by broad deletion or blind finalizer removal.

**Incident 1 — Prune deleted a namespace/resource**
- Symptom: namespace or workload disappears after a path/config change.
- Hypotheses: tracked Namespace pruned, wrong owner, empty render, prune enabled, no confirmation.
- Safe test: inspect Git diff, rendered output, Application tree, operation, events, finalizers and audit logs; reproduce only with a ConfigMap.
- Blast radius: enumerate workloads, PVC/PV/data dependencies, and backup state.
- Mitigation: stop further deletion through approved procedure; restore source and determine whether object/data can be recreated safely. Use backup/PITR for data loss; Git revert alone is insufficient.
- Prevention/evidence: deletion review, `allowEmpty: false`, selective prune, ownership, commit/diff, deleted inventory, recovery proof.

**Incident 2 — ApplicationSet change removed many Applications**
- Symptom: template/generator/path change removes or rewrites generated apps.
- Hypotheses: input directory disappeared, template name changed, deletion policy allows cleanup, finalizers cascade.
- Safe test: compare generator output and generated-app inventory in disposable cluster.
- Blast radius: list affected Applications/workloads before revert.
- Mitigation: restore reviewed template/input; re-create/re-adopt in batches.
- Prevention/evidence: PR preview, protected generator paths, explicit deletion policy, old/new inventory and recovery record.

**Incident 3 — Application finalizer deleted workloads**
- Symptom: deleting an Application removes its resources.
- Hypotheses: cascading finalizer, cascade CLI/UI choice, ApplicationSet owner relationship.
- Safe test: inspect finalizers/owner references and current deletion docs; test only in Lab F.
- Blast radius: determine recreate safety and data/external side effects.
- Mitigation: restore desired source and re-create/adopt only after ownership/dependency review; do not strip finalizers blindly.
- Prevention/evidence: cleanup runbook, explicit retain/cascade choice, Application YAML and deletion event.

**Incident 4 — repo-server OOM/slow render**
- Symptom: pending app/ComparisonError, restarts, render queue growth.
- Hypotheses: large chart/repo, expensive plugin, memory pressure, Git rate limits, cache contention.
- Safe test: inspect pod events/resources/logs/metrics and render exact revision locally with matching tools.
- Blast radius: identify all apps sharing repo-server; avoid broad simultaneous changes.
- Mitigation: restore capacity/source reachability, reduce render scope, fix plugin/input; reconcile low-risk app first.
- Prevention/evidence: resource monitoring, pinned render tools, bounded plugins, render timing and logs.

**Incident 5 — OutOfSync loop from another controller**
- Symptom: field repeatedly differs or sync undoes HPA/operator changes.
- Hypotheses: two owners for replicas, admission mutation, defaulting, field-manager conflict.
- Safe test: compare desired/live YAML and managed fields; identify writer; reproduce harmlessly.
- Blast radius: check whether field affects capacity/security/traffic.
- Mitigation: assign one field owner; adjust source or narrowly scoped ignore rule.
- Prevention/evidence: ownership map, regression test, before/after diff and rationale.

**Incident 6 — admin credentials left default or leaked**
- Symptom: unexpected API actions or exposed bootstrap secret.
- Hypotheses: password not rotated, secret copied to logs/history, broad credential sharing.
- Safe test: authorized identity/audit review; never test a suspected leaked password by logging in with it.
- Blast radius: enumerate repos, clusters, Applications, credentials and exposure window.
- Mitigation: revoke/rotate, restrict/disable built-in admin per version-supported process, inspect actions in exposure window.
- Prevention/evidence: post-bootstrap checklist, least privilege, access reviews, rotation records and audit results.

**Incident 7 — sync window blocks emergency fix**
- Symptom: urgent change is blocked by window/approval rule.
- Hypotheses: policy/schedule error, no emergency path, unclear approver.
- Safe test: inspect policy without modifying production; reproduce in disposable project.
- Blast radius: assess current SLO impact and risk of bypass.
- Mitigation: approved, time-bounded break-glass with narrow scope and Git follow-up; do not disable all windows globally.
- Prevention/evidence: rehearsed emergency process, approver list, blocked-sync reason, approval, diff, recovery and post-review.

#### 2.6.5 What runs during Argo CD outage?

Already-running workloads normally continue if they do not require Argo CD at request time and Kubernetes/runtime dependencies remain healthy. New Git-driven deployment and Argo CD drift correction are unavailable/delayed. A workload may still depend on secret providers, registries, operators, or external systems; the control-plane outage does not guarantee all dependent systems remain healthy.

#### 2.6.6 Expert trade-offs

| Decision | Benefit | Cost/risk | Choose when |
|---|---|---|---|
| Auto-sync dev/staging | Fast feedback | Bad merged config deploys quickly | CI and immutable artifact checks are proven |
| Manual prod sync | Explicit decision point | Delay/human error | Release approval is required |
| Self-heal | Drift correction | Can undo hotfix or fight HPA | Field ownership and break-glass are clear |
| Prune | Inventory cleanup | Deletion risk | Ownership and recovery are tested |
| `allowEmpty: true` | Intentionally empty app | Empty render may delete all tracked resources | Rare, reviewed use case |
| AppProject per team | Source/destination/kind boundaries | More governance | Project edits are separately controlled |
| ApplicationSet | Templated fleet management | Generator change blast radius | Generator input and deletion policy are reviewed |
| Namespace-scoped controller | Smaller blast radius | Some features may be constrained | Supported and tested by chosen install |
| Broad ignore-diff | Fewer noisy diffs | Hides real security/image drift | Generally avoid |

#### Adoption maturity

1. Pilot one stateless dev service, manual sync, no prune.
2. Protect Git, require checks, pin artifact digest.
3. Establish AppProject, Argo RBAC, controller RBAC, repository credential scope.
4. Test auto-sync/self-heal; measure drift and failures.
5. Test prune, Application deletion, and ApplicationSet deletion on harmless objects.
6. Add production promotion, runtime/business gates, break-glass, durable evidence.
7. Test controller rebuild/re-adoption, credential rotation, source outage, and data recovery.
8. Scale tenancy only after negative tests prove boundaries.

### 2.7 SRE lens

| Indicator | Example definition | Measurement | Caveat |
|---|---|---|---|
| Sync success rate | Successful sync operations / completed sync operations in a window | Export Application history/events | Define retry counting |
| Sync failure rate | Failed sync operations / total sync operations | Segment source/render/policy/apply/health causes | Retry count can obscure root cause |
| Commit-to-running latency | Approved config merge to verified workload running | Correlate Git timestamp, observed revision, rollout and runtime checks | Sync complete is not service verified |
| Drift age | Time from first diff detection to resolution/accepted exception | Controller events and drift inventory | Some differences are intentional |
| Bad-release detection time | Harmful signal to detection | Incident + telemetry timeline | Depends on alert quality |
| Time to mitigate | Release decision to verified mitigation | Incident timeline and runtime metrics | Data repairs may require forward fix |
| Approved GitOps coverage | Eligible apps meeting platform standard / eligible inventory | Application/project/owner inventory | Define eligible population |
| Failed retry count | Retry attempts by cause | Controller operation history | Retries are not root-cause resolution |
| Accidental prune incidents | Count/severity of unintended deletions | Audit logs, events, incidents | Low count does not prove safe policy |
| Render/fetch health | Render latency and Git fetch failures | Version-verified metrics/logs | Do not invent metric names |

No universal target values are asserted. Define thresholds based on workload criticality and error budget. M10 owns SLO policy; M11 owns full observability architecture.

**Sync failure runbook:** confirm app/context/revision/runtime SLO → classify source/render/compare/policy/apply/health/business phase → preserve logs/events/diff/commit/digest → check blast radius and rollback → fix source/policy/permission → reconcile a low-risk app → verify service and business metrics → record evidence and prevention.

### 2.8 Security lens

Security is layered: Git permissions govern proposals; review/CI govern merges; AppProject constrains source/destination/kinds; Argo CD RBAC controls users; Kubernetes RBAC constrains controller API operations; admission policy rejects unsafe objects. No single layer is sufficient.

| Threat | Control | Evidence | Residual risk |
|---|---|---|---|
| Compromised Git credentials | Scoped read-only repo credential, rotation, protected branch | Credential inventory/access audit | Malicious writer may propose change |
| Malicious commit | Reviews, checks, immutable digest | PR/CI/render evidence | Reviewer or CI compromise |
| Overbroad AppProject | Explicit allow-lists | Project YAML and denied tests | Project editor can weaken it |
| Cluster privilege escalation | Restrict cluster kinds/controller RBAC/admission | Failed ClusterRoleBinding test | Other privileged path may exist |
| Admin credential leak | Rotate/disable admin, least privilege | Rotation and audit | Break-glass remains sensitive |
| CMP plugin compromise | Pin/review/sandbox/restrict network | Plugin inventory and permissions | Plugin processes rendered data |
| TLS/host-key bypass | Verify cert/key | Repo trust config | Lab HTTP is not production safe |
| Unsafe prune | Deletion review, inventory, backups | Lab C evidence | Reviewer can approve bad deletion |
| ApplicationSet cascade | Inventory preview and policy test | Lab E/F evidence | Version-specific semantics |
| Broad ignore rule | Narrow field path and regression test | Image/RBAC diff remains visible | Rules can become stale |
| Secrets in Git | References/approved encryption/scanning | CI scan | Render/cache may still be sensitive |
| Network misconfiguration | NetworkPolicy after mapping flows | Allowed/denied connectivity | CNI behavior varies |
| Sync-window emergency conflict | Bounded break-glass and post-review | Approval/change record | Human process failure |

Deep secrets are Unit 5/M09; Kubernetes RBAC/PSS are M03; NetworkPolicy is M04; artifact provenance/admission enforcement is M12; full observability is M11; DR is M13; multi-cluster fleet is M14. If a credential is committed, treat it as exposed: revoke/rotate first, investigate usage, then coordinate history cleanup. Deleting the file does not un-leak it.

### 2.9 Production checklist

- [ ] Pin Argo CD release and review release notes/CRD changes.
- [ ] Document bootstrap/rebuild procedure independent of running controller.
- [ ] Restrict UI/CLI; rotate/disable bootstrap admin per supported procedure.
- [ ] Use explicit AppProjects; do not rely on permissive `default`.
- [ ] Allow-list source repos, destinations, and resource kinds.
- [ ] Review global Argo RBAC, AppProject roles, and Kubernetes controller RBAC separately.
- [ ] Scope repository credentials read-only and verify TLS/SSH host keys.
- [ ] Use immutable image digests and CI render/schema/policy checks.
- [ ] Make manual/auto-sync policy explicit by environment.
- [ ] Decide `selfHeal`, `prune`, and `allowEmpty` separately.
- [ ] Review deletion diffs and test prune on disposable resources.
- [ ] Test Application/ApplicationSet deletion and finalizer semantics.
- [ ] Keep hook Jobs idempotent; do not treat waves as transactions.
- [ ] Keep `ignoreDifferences` narrow and tested.
- [ ] Pin/review Helm/Kustomize/plugin inputs.
- [ ] Export events/history to durable evidence store.
- [ ] Monitor repo-server/controller performance and Git rate limits.
- [ ] Test upgrade/rebuild and re-adoption with prune initially disabled.
- [ ] Verify runtime/business outcomes beyond Sync/Health.
- [ ] Rehearse break-glass and record Git follow-up.
- [ ] Link commit, digest, approval, sync result, live imageID, and post-deploy check.
- [ ] Ensure no lab command silently assumes current context or performs broad deletion.

### 2.10 Hands-on lab set

#### Lab acceptance matrix

| ID | Goal | Level | Duration | Footprint | Components | Evidence | Cleanup |
|---|---|---|---|---|---|---|---|
| A | Install Argo CD; deploy from local Git using plain/Kustomize/Helm | L1–L2 | 4–6 h | 4 CPU/8 GB/30 GB planning estimate | kind, Argo CD, local Gitea, CLI, Helm/Kustomize | Versions, YAML, diff/status, revision, runtime checks | Inspect inventory; delete disposable cluster only |
| B | Prove AppProject denies unauthorized namespace and cluster kind | L2 | 1–2 h | Existing lab cluster | AppProject, disposable apps | Denial reason and allowed deployment proof | Review finalizers/resources first |
| C | Manual → auto → selfHeal → prune and allowEmpty | L2 | 2–3 h | One ConfigMap/Deployment | Argo CD, Git | Git/live/status before and after each policy | Restore known-good source and verify |
| D | PreSync ordering, deliberate failure, recovery | L2–L3 | 2–3 h | One marker Job | Argo CD, Git | Job status/logs, events, sync outcome | Check hook policy and inventory |
| E | ApplicationSet generates dev/staging apps | L3 | 2–3 h | Two small apps | ApplicationSet, Git dirs | Generated-app inventory before/after | Restore directories; verify apps |
| F | Application/ApplicationSet cascade and retain guard | L3–L4 | 2–3 h | Harmless objects only | App, AppSet, finalizers | Finalizers/owner refs and sentinel proof | Delete only known test objects |
| G | Security checklist, negative test, break-glass rehearsal | L3–L4 | 2–4 h | Existing lab cluster | Project/RBAC/policy; local sink optional | Pass/fail checklist and denied action | Restore original lab policy |

Every lab is restricted to the disposable cluster and repository. Confirm exact CLI/API semantics before execution.

#### Lab A — Install Argo CD and deploy from local Git

**Objective:** Establish local-only GitOps and deploy the same service through three isolated source paths.  
**Prerequisites:** Docker/compatible runtime, kind, kubectl, Git, Argo CD CLI, Helm, local Git server.  
**Footprint:** 4 CPU, 8 GB RAM, 30 GB disk planning estimate; not measured. Stop other clusters, Flux, meshes, and full observability stacks.  
**Context guard:** use the exact context inspected in Section 2.3.2.  
**Stop condition:** unexpected context, source URL leaving the local cluster, unreviewed deletion diff, or non-disposable resource in the app inventory.

**A1 — Local Git server.** Use a verified Gitea image version. The following ephemeral Deployment is a lab template, not hardened Git hosting.

**File: `lab/gitea.yaml`**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: gitops-lab
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gitea
  namespace: gitops-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: gitea
  template:
    metadata:
      labels:
        app.kubernetes.io/name: gitea
    spec:
      containers:
        - name: gitea
          image: gitea/gitea:<GITEA_VERSION>
          ports:
            - name: http
              containerPort: 3000
          env:
            - name: GITEA__database__DB_TYPE
              value: sqlite3
            - name: GITEA__server__HTTP_PORT
              value: "3000"
          volumeMounts:
            - name: data
              mountPath: /data
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 768Mi
      volumes:
        - name: data
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: gitea
  namespace: gitops-lab
spec:
  selector:
    app.kubernetes.io/name: gitea
  ports:
    - name: http
      port: 3000
      targetPort: http
  type: ClusterIP
```

Replace `<GITEA_VERSION>` with a verified image tag. `emptyDir` loses data when the Pod is replaced; use only for a disposable lab.

```bash
EXPECTED_CONTEXT='<EXACT_DISPOSABLE_CONTEXT>'
CURRENT_CONTEXT="$(kubectl config current-context)"
if [ "$CURRENT_CONTEXT" != "$EXPECTED_CONTEXT" ]; then
  printf 'Refusing to mutate wrong context: %s\n' "$CURRENT_CONTEXT" >&2
  exit 1
fi
kubectl apply -f lab/gitea.yaml
kubectl rollout status deployment/gitea -n gitops-lab --timeout=180s
kubectl get svc,pods -n gitops-lab
kubectl port-forward -n gitops-lab svc/gitea 3000:3000
```

Open `http://localhost:3000` locally. Configure a disposable local instance, create a lab user and repository named `config-repo`, and push the configuration tree. Use synthetic content only. Argo CD should use a service URL like `http://gitea.gitops-lab.svc.cluster.local:3000/<OWNER>/config-repo.git`; the owner/repo path must match. Plain HTTP is local-lab-only. If Argo CD cannot fetch, inspect service DNS/connectivity and repo errors; do not substitute a public repository.

**A2 — Install Argo CD and verify.** Follow the selected release’s official install instructions, using the verified version in the install URL/Helm command. Verify pods, CRDs, events, and CLI/server version. Access UI via the local port-forward. Rotate/disable bootstrap admin access per version-specific docs.

**A3 — Deploy one source type at a time.**
1. Apply the restrictive AppProject from Section 2.4.2.
2. Push plain manifests; apply the Application object; inspect source/destination/project.
3. Inspect `argocd app diff`, sync manually, capture status/history, and verify service readiness/health plus one synthetic scoring request.
4. Commit one harmless config change; inspect the diff before sync; record the commit SHA and observed revision.
5. Repeat with Kustomize overlay, rendering locally with `kubectl kustomize`.
6. Repeat with Helm chart in Git, rendering locally with `helm lint`/`helm template` if installed.
7. Use unique resource names or fully remove the previous test app and verify cleanup before changing source type. Never allow multiple Applications to manage the same resource identities.
8. Record renderer versions and any untested behavior.

**Evidence:** versions, context, Gitea repo path, Application/AppProject YAML, source revision, render output, diff, sync history/status, events, local readiness/scoring response, and not-tested items.

**Cleanup:** stop port-forward; inspect all Applications/resources. If deleting the cluster, first run `kind get clusters` and confirm the target. **⚠ DESTRUCTIVE — DISPOSABLE LAB ONLY**

```bash
# Run only after confirming argocd-unit2 is the intended disposable cluster.
kind get clusters
kubectl config current-context
kind delete cluster --name argocd-unit2
kind get clusters
```

**Rerun:** create a new cluster and Gitea repository; ephemeral storage means previous Git data is not preserved.  
**Proves:** the selected local setup can fetch/render/apply/report state if the lab succeeds.  
**Does not prove:** HA, production identity, real tenancy isolation, public Git security, or business correctness beyond tested checks.  
**Stretch:** add CI render/schema checks and compare output with Argo CD’s diff.

#### Lab B — AppProject restriction proof

**Objective:** prove allowed deployment and denied namespace/cluster-kind attempts.  
**Prerequisites/footprint:** Lab A and one disposable cluster; no additional heavy components.  
**Stop first:** any other controller owning test resources.

1. Save current AppProject YAML.
2. Deploy to allowed `dev`; verify app state and runtime.
3. Create a disposable Application targeting `staging`, which is not allowed by the project. Capture status and denial reason.
4. Create a second disposable Application containing a `ClusterRoleBinding`. Capture whether AppProject validation, Kubernetes RBAC, or admission rejected it.
5. Confirm the allowed `dev` app still works.
6. Do not use cluster-admin success as proof of tenant isolation; test the intended Application/project path.

**Evidence:** project YAML, allowed deployment proof, denied namespace/kind output, event/status details.  
**Cleanup:** inspect each test Application’s finalizers and tracked resources; remove only the test objects and verify the allowed service remains.  
**Rerun:** use unique Application names and the same restricted project.  
**Proves:** the specific policy path rejected the tested action. **Does not prove:** complete isolation or safety against project editors.  
**Stretch:** test a second role that may sync but may not edit Application source/destination.

#### Lab C — Manual → auto → selfHeal → prune and allowEmpty

**⚠ DESTRUCTIVE — DISPOSABLE LAB ONLY**

**Objective:** observe each policy separately.  
**Footprint:** one ConfigMap and a small Deployment.  
**Prerequisites:** Lab A, Git repo, namespace `argocd-lab-policy`, one test Application.  
**Stop first:** other controllers/Applications owning these resources.

1. Commit a test ConfigMap and Deployment with manual sync, no prune/self-heal. Sync and capture initial state.
2. Change ConfigMap data in Git. Capture OutOfSync and diff; manually sync; confirm live value changes.
3. Enable automated sync only. Commit another harmless ConfigMap change and observe automatic sync.
4. Enable `selfHeal: true`; use a context-guarded out-of-band scale or ConfigMap edit. Observe correction and record timing/status.
5. Enable `prune: true`; remove only the test ConfigMap manifest. Inspect the deletion diff and inventory before sync. Verify actual deletion behavior.
6. Commit a throwaway path change that renders zero resources with `allowEmpty: false`; capture the selected release’s result.
7. In a separate disposable Application, demonstrate `allowEmpty: true` only after reviewing the exact deletion set. Never test this with namespace/PVC/valuable resources.
8. Revert to a known-good Git state, wait for reconciliation, and verify the resource inventory.

```bash
EXPECTED_CONTEXT='<EXACT_DISPOSABLE_CONTEXT>'
CURRENT_CONTEXT="$(kubectl config current-context)"
if [ "$CURRENT_CONTEXT" != "$EXPECTED_CONTEXT" ]; then
  printf 'Refusing scale: expected %s, got %s\n' "$EXPECTED_CONTEXT" "$CURRENT_CONTEXT" >&2
  exit 1
fi
kubectl scale deployment/policy-demo --replicas=3 --namespace=argocd-lab-policy
kubectl get deployment policy-demo -n argocd-lab-policy
```

**Evidence:** commits, policy variants, diff, live state, app status/events, empty-render outcome.  
**Cleanup:** restore known-good source, inspect inventory, remove only test resources via verified deletion flow, verify no unrelated objects changed.  
**Rerun:** create fresh ConfigMap names/commits or reset the disposable repository deliberately; do not rewrite shared history.  
**Proves:** observed policy behavior for selected version/config. **Does not prove:** all kinds behave identically or Git revert reverses external side effects.  
**Stretch:** compare sync latency with/without `ApplyOutOfSyncOnly` using a defined small test, not a universal benchmark.

#### Lab D — PreSync hook and failure recovery

**Objective:** observe hook ordering/failure without touching a real database.  
**Footprint:** one marker Job.  
**Prerequisites:** Git repo, Application, disposable namespace.  
**Stop first:** any real migration/production database.

1. Add the marker Job from Section 2.4.5 with `PreSync` and wave `-1`.
2. Render/inspect YAML and commit.
3. Sync and capture Job status/logs, Application operation state, events, and ordering.
4. In a separate commit, change the marker to exit non-zero. Sync and capture failure.
5. Inspect logs and operation details before retrying; a real hook may have partial side effects.
6. Revert the marker failure and sync again.
7. Document why ordering is not transactionality: idempotency, compatibility, locking, backup/PITR, expand-migrate-contract and recovery are Unit 11 concerns.

**Evidence:** hook YAML, commits, Job logs/status, events, failure/recovery timeline.  
**Cleanup:** inspect hook deletion policy and Application inventory before cleanup; no database is involved.  
**Rerun:** use a fresh Job name or verify hook cleanup semantics.  
**Proves:** observed hook ordering/reporting. **Does not prove:** database migration safety or transactional rollback.  
**Stretch:** draft a migration runbook and compatibility matrix without executing DDL.

#### Lab E — ApplicationSet dev/staging generation

**Objective:** generate two Applications from controlled directories.  
**Footprint:** two small app instances; ApplicationSet controller included in Argo CD install.  
**Prerequisites:** Lab A and a project allowing only dev/staging.  
**Stop first:** any other generator using same Application names.

1. Create `apps/scoring-api/environments/dev` and `.../staging`, with unique resource names/labels or separate app namespaces.
2. Apply the ApplicationSet from Section 2.5.1 after verifying generator syntax.
3. Record generated Application name, project, source path, destination, owner reference, finalizer.
4. Verify the project denies `prod`.
5. Add a throwaway `qa` directory. Observe generation and verify the project still blocks unauthorized destination.
6. Rename/remove only the throwaway directory after inspecting generated inventory; capture deletion outcome and resource effects.
7. Restore the original tree and verify dev/staging apps and resources remain.

**Evidence:** ApplicationSet YAML, commits/tree, generated app inventory, owner references, policy results, before/after path diff.  
**Cleanup:** remove only the QA test app/resources after checking cascade policy.  
**Rerun:** restore the exact two directories and re-check generator status.  
**Proves:** generator behavior for selected version/input. **Does not prove:** production branch protection or multi-cluster isolation.  
**Stretch:** add a CI step that compares generated Application inventory before and after a PR.

#### Lab F — Application/ApplicationSet cascade and guard

**⚠ DESTRUCTIVE — DISPOSABLE LAB ONLY**

**Objective:** observe retain versus cascade behavior and prove unrelated resources survive.  
**Footprint:** one throwaway Application/AppSet and harmless ConfigMap/Deployment.  
**Prerequisites:** Lab E and current deletion docs for selected release.  
**Stop first:** any ApplicationSet with valuable resources.

1. Assert context; save Application/AppSet YAML.
2. Inspect finalizers, owner references, `preserveResourcesOnDeletion`, sync policy, and full tracked inventory.
3. Create an unrelated sentinel ConfigMap in a separate test namespace and record its UID.
4. Create a test Application owning one harmless ConfigMap. Inspect finalizer.
5. Use the documented non-cascading deletion path and verify the Application is removed while intended resource remains. Exact CLI/UI semantics are version-sensitive.
6. Re-adopt or clean the retained object through a reviewed path; do not leave unmanaged resources.
7. Create a separate ApplicationSet generating a disposable Application; inspect owner reference and finalizer.
8. Test the documented preservation/deletion policy; then test cascading deletion only after inspecting the exact resource inventory and confirming the target.
9. Verify the sentinel ConfigMap still exists with the same UID and unrelated namespaces are unchanged.

**Guard script — intentionally does not execute deletion automatically:**

```bash
#!/usr/bin/env bash
set -euo pipefail
EXPECTED_CONTEXT='<EXACT_DISPOSABLE_CONTEXT>'
APP_NAME='argocd-lab-delete-me'
APP_NAMESPACE='argocd'
current_context="$(kubectl config current-context)"
if [[ "$current_context" != "$EXPECTED_CONTEXT" ]]; then
  echo "Refusing: expected $EXPECTED_CONTEXT, got $current_context" >&2
  exit 2
fi
kubectl get application "$APP_NAME" -n "$APP_NAMESPACE" -o yaml
kubectl describe application "$APP_NAME" -n "$APP_NAMESPACE"
echo "This may cascade-delete managed resources."
read -r -p "Type DELETE-$APP_NAME to continue: " confirmation
if [[ "$confirmation" != "DELETE-$APP_NAME" ]]; then
  echo "Cancelled."
  exit 0
fi
echo "Confirmation accepted. Execute the version-verified retain/cascade procedure manually."
```

After the context guard and resource-inventory review, choose exactly one version-verified path. These commands are examples to validate against the selected release; do not run both.

```bash
# Retain managed workloads while deleting only the Application:
# [VERIFY] CLI flag syntax for the selected argocd version.
argocd app delete argocd-lab-delete-me --cascade=false

# Controlled cascading deletion (separate throwaway Application only):
# [VERIFY] CLI flag syntax and propagation semantics for the selected release.
argocd app delete argocd-lab-cascade-me --cascade --propagation-policy foreground

# ApplicationSet deletion while orphaning generated Application objects:
# [VERIFY] Owner-reference and Application finalizer effects.
kubectl delete applicationset argocd-lab-appset --namespace=argocd --cascade=orphan
```

Orphaning the ApplicationSet does not automatically remove resource finalizers from generated Applications. Inspect generated Application finalizers and apply the documented preservation strategy before expecting workloads to remain. Do not use broad `--all`, wildcard deletion, or namespace deletion as a cleanup shortcut.

**Evidence:** pre/post YAML, finalizers, owner references, inventory, chosen deletion option, sentinel UID.  
**Cleanup:** remove only known test objects and verify sentinel/unrelated inventory survives.  
**Rerun:** use fresh names and reset source tree deliberately.  
**Proves:** observed lifecycle behavior in this version. **Does not prove:** every finalizer/outage state behaves identically.  
**Stretch:** create a PR policy that requires generated-app inventory diff for ApplicationSet changes.

#### Lab G — Security hardening checklist and negative test

**Objective:** produce pass/fail/evidence review and prove an unauthorized action is rejected.  
**Footprint:** existing lab cluster; no external SSO/cloud.  
**Prerequisites:** Labs A/B and access to AppProject/RBAC config.  
**Stop first:** production credentials or real cluster registration.

1. Inspect AppProject source/destination/kind allow-lists.
2. Inspect global Argo RBAC and project roles; identify who can create/edit Apps/Projects.
3. Verify bootstrap admin handling.
4. Inspect repo credentials and TLS/SSH host verification.
5. Inspect controller Kubernetes RBAC; document any broad permissions and supported reduction path.
6. Review TLS/port-forward and NetworkPolicy dependencies.
7. Review CMP plugins; no untrusted plugins in the lab.
8. Review secrets, prune/self-heal/allowEmpty, finalizers, sync windows, ignore rules, and evidence export.
9. Attempt an unauthorized namespace or cluster-kind deployment; capture the exact error and enforcement layer.
10. Rehearse an emergency path when a sync window/policy blocks a harmless test change. Record approver, scope, time limit, Git follow-up, and policy restoration. Do not bypass production controls.
11. If using a local notification sink, trigger an event and test that the record survives a controller restart before claiming durable evidence.

**Evidence:** security checklist, negative-test output, project/RBAC snapshots, local event record, break-glass timeline.  
**Cleanup:** restore original lab policy, remove temporary permissions, verify intended apps still sync.  
**Rerun:** repeat negative test after each policy change.  
**Proves:** specific controls worked in this environment. **Does not prove:** enterprise SSO, full tenant isolation, or compliance certification.  
**Stretch:** review one policy change from staff SRE, security, platform, and auditor perspectives.

### 2.11 Self-check questions

1. **Why are Sync and Health different?**  
   **Answer:** Sync compares rendered desired state and live state; Health assesses resource conditions. Neither alone proves business correctness. **Tempting wrong answer:** “Synced means all pods are ready.” A spec can match while pods fail.

2. **What does an AppProject constrain?**  
   **Answer:** Source repos, destinations, resource kinds, and optional project roles. **Wrong answer:** “It replaces Kubernetes RBAC.” Controller API permissions and Argo RBAC remain separate.

3. **Why are automated sync, self-heal, and prune separate?**  
   **Answer:** Automated sync initiates reconciliation; self-heal corrects supported out-of-band changes; prune removes tracked resources absent from desired output. **Wrong answer:** “Auto-sync always deletes missing resources.” Prune is a separate policy.

4. **Why keep `allowEmpty` false by default?**  
   **Answer:** An accidental empty render plus prune can remove all tracked resources. **Wrong answer:** “An empty render is harmless.” It can represent destructive desired state.

5. **Why is the default AppProject not a tenant boundary?**  
   **Answer:** It is commonly initialized with broad permissions. **Wrong answer:** “Applications are isolated automatically.” Explicit project membership does not establish full isolation.

6. **Why can deleting an ApplicationSet directory be dangerous?**  
   **Answer:** The generator may stop producing an Application; owner references/finalizers/policy can cascade to workloads. **Wrong answer:** “Only metadata disappears.” Managed resources may be deleted.

7. **Do sync waves make a migration transactional?**  
   **Answer:** No; they order operations but do not guarantee database rollback, compatibility, or no partial side effects. **Wrong answer:** “PreSync makes the schema safe.” Migration design remains separate.

8. **When should `ignoreDifferences` be used?**  
   **Answer:** For a narrow, justified field owned by another controller, with tests proving important fields remain visible. **Wrong answer:** “Ignore everything to clear alerts.” That hides dangerous drift.

9. **How does repo-server failure differ from apply failure?**  
   **Answer:** Repo-server failure prevents desired manifests from being fetched/rendered; apply failure occurs when Kubernetes cannot accept/apply rendered resources. **Wrong answer:** “Both are schema errors.” Fetch/render can fail before API calls.

10. **What continues during an Argo CD outage?**  
    **Answer:** Existing workloads normally continue if runtime dependencies remain healthy; new Git-driven deployment and drift correction pause/delay. **Wrong answer:** “All apps stop immediately.” Argo CD is usually not in the request path.

11. **Why is controller Kubernetes RBAC a high-impact boundary?**  
    **Answer:** The controller applies desired state using its identity; malicious desired state can exercise those permissions. **Wrong answer:** “Source allow-lists are enough.” They do not replace RBAC/admission.

12. **What proves the expected image digest is running?**  
    **Answer:** Correlate approved config commit/digest, observed Application revision, live Pod image spec/imageID, CI provenance and runtime checks. **Wrong answer:** “The Git tag says 1.2.” Mutable tags do not prove bytes.

13. **Why is `Replace=true` risky?**  
    **Answer:** Replace/create semantics may recreate resources and cause outage. **Wrong answer:** “It is just a faster apply.” It changes update behavior.

14. **Why are notifications not a complete audit trail?**  
    **Answer:** They may be dropped, expire, or omit digest/approval context. **Wrong answer:** “A chat message proves what ran.” Evidence must correlate source, artifact, controller and runtime.

15. **What is the difference between AppProject and Argo CD RBAC?**  
    **Answer:** AppProject restricts what an Application may deploy; Argo RBAC restricts user actions through Argo CD. Kubernetes RBAC separately constrains controller API operations. **Wrong answer:** “Project permissions control everything.”

### 2.12 Evidence artifacts

Save sanitized artifacts outside this lesson in the learner’s designated lab evidence directory. Never save secrets, tokens, private keys, passwords, full sensitive Secret YAML, or production logs.

1. `versions.txt`: Kubernetes client/server, kind, Argo CD CLI/server, Helm, Kustomize versions.
2. `context.txt`: exact context and disposable cluster inventory.
3. `argocd-components.txt`: observed pods/deployments/CRDs and optional components present.
4. Application manifests for plain, Kustomize, and Helm sources.
5. AppProject YAML and the allowed/denied namespace and cluster-kind results.
6. Rendered manifests and `argocd app diff` for the exact source revision.
7. Sync history/status and sanitized events for manual/automated sync.
8. Before/after live state for self-heal, prune, and allowEmpty tests.
9. Hook YAML, Job status/logs, sync failure, and recovery evidence.
10. ApplicationSet YAML, generated Application inventory, owner references, and directory-change result.
11. Application/ApplicationSet finalizer snapshots, deletion procedure, retained-resource proof, and unrelated sentinel UID before/after.
12. Security checklist with pass/fail/evidence for every control.
13. CI policy-check output and its explicit limitations.
14. Release trace linking source commit, artifact digest, sync result, live Pod imageID, runtime health, and business check.
15. Claim register and human verification checklist.

### 2.13 Common interview and design-review questions

#### 1. Why separate Sync and Health?

Sync is a desired-versus-live comparison; Health is a resource/application condition assessment. A matching Deployment can still fail probes, and a healthy Pod can still produce poor model predictions or stale ETL output. A release gate needs resource state plus runtime/business evidence.

#### 2. What exactly can `selfHeal` undo?

It can correct supported out-of-band differences toward rendered desired state when configured. It does not know a manual edit was an emergency fix. Record emergency changes, reconcile them into Git, or use a documented time-bounded exception.

#### 3. Why is `prune` dangerous?

It may delete tracked resources that disappear from rendered desired output. A wrong path, generator input, or empty render can delete more than intended. Establish ownership, review deletion diffs, test disposable objects, and plan data recovery separately.

#### 4. When is automated sync appropriate?

When source controls, CI gates, immutable artifacts, permissions, monitoring, and recovery match the environment’s risk. Dev/staging are common starting points. Production may use automation or manual approval; neither is universally correct.

#### 5. How can an AppProject fail to provide a security boundary?

It may allow broad source/destination/kinds, be editable by untrusted users, or be paired with overbroad Argo/Kubernetes permissions. ApplicationSet templates may indirectly exercise controller authority. Test negative actions.

#### 6. App-of-apps versus ApplicationSet?

App-of-apps manages child Application manifests through a parent; ApplicationSet generates Applications from templates and inputs. Choose based on fleet scale, reviewability, ownership, and deletion behavior. Neither automatically isolates tenants.

#### 7. How do you safely delete an Application?

Confirm context, inspect source/destination/project, finalizers, owner references, sync policy, and tracked resources. Decide retain versus cascade, use the version-verified procedure, and verify unrelated resources survive.

#### 8. What happens during Argo CD outage?

Existing workloads normally continue if they do not depend on Argo CD at runtime; new Git-driven deployments and drift correction pause/delay. Restore controller/source access, re-adopt with prune disabled initially, inspect diffs, then enable automation deliberately.

#### 9. How do you debug repo-server rendering versus apply/health failure?

Classify phase first. For fetch/render, check repo URL/revision/path, credentials, Helm/Kustomize, plugins and repo-server logs. For apply, check API error, RBAC, admission, quota, CRDs and events. For health, inspect scheduling, image pull, probes, logs and dependencies. Then verify business metrics.

#### 10. What evidence proves the desired digest is running?

Correlate approved config commit and immutable digest with Application revision, live Pod image spec/imageID, CI provenance, approval, sync history, and post-deploy checks. A mutable tag alone is insufficient.

#### 11. When would you enable `allowEmpty`?

Only when an empty rendered resource set is an expected, reviewed state and deletion consequences are understood. Otherwise keep it false and use an explicit deletion workflow.

#### 12. How do you resolve an OutOfSync loop caused by HPA/operator?

Identify exact field and writer using desired/live YAML, managed fields, events and controller config. Assign one owner; change source or use a narrow documented ignore/field-management setting, then test that image/security/RBAC changes remain visible.

#### 13. What does AppProject not control?

It does not replace user RBAC, Kubernetes controller permissions, Git branch protection, admission policy, or business-health checks. It must be one layer of a defense-in-depth design.

#### 14. How do you recover after an ApplicationSet deletion incident?

Preserve source revision, generated-app inventory, owner references, finalizers, events, and affected resources. Restore the reviewed generator inputs, calculate the impact, and recreate/re-adopt in batches with prune disabled until ownership is verified. Recover data from backups if needed.

### 2.14 Sources and verification notes

#### Cross-module handoffs

- Unit 1 — [GitOps principles and desired-state reconciliation](01-gitops-principles-and-desired-state-reconciliation.md): operating model, desired/live state, reconciliation, and push/pull boundary.
- Unit 3 — [Flux controllers and Kustomize/Helm reconciliation](03-flux-controllers-and-kustomize-helm-reconciliation.md): Flux-specific mechanics; never run Argo CD and Flux as competing owners in the same lab cluster.
- Unit 4 — [Repository layout and multi-environment promotion](04-repository-layout-and-multi-environment-promotion.md): repo structure, promotion, and approval workflow.
- Unit 5 — [Configuration and secret reference management](05-configuration-and-secret-reference-management.md): secret references, encryption, rotation, and controller access.
- Unit 6 — [Deployment drift detection and reconciliation](06-deployment-drift-detection-and-reconciliation.md): drift classification, field ownership, and ignore rules.
- Unit 11 — [Database and data-platform migration safety](11-database-and-data-platform-migration-safety.md): migration compatibility, locking, recovery, and rollback limits.
- Unit 13 — [Release evidence and audit trails](13-release-evidence-and-audit-trails.md): durable evidence, event export, and audit queries.
- [M08 project index](Projects/README.md) and [GitOps-controlled data-service release capstone](Projects/01-gitops-controlled-data-service-release.md): integrate this unit without duplicating the whole capstone.

Stage boundaries: M01 owns image creation/digest/provenance; M02 owns CI tests and CI-to-Git handoff; M03 owns Kubernetes RBAC/PSS/probes; M04 owns NetworkPolicy; M05 owns stateful workloads/backups; M06 owns Helm/Kustomize rendering; M07 owns IaC boundaries; M09 owns deep secrets/identity; M10 owns SLO/error-budget policy; M11 owns full observability; M12 owns supply-chain/admission enforcement; M13 owns disaster recovery; M14 owns fleet/multi-cluster GitOps; M16 owns platform golden paths.

#### Source coverage and limitations

- The supplied roadmap snapshot was inspected for the M08 sibling filenames, target path, and unit order.
- The authoritative `PROMPT-GitOps-and-Progressive-Delivery.md` was inspected for Unit 2 requirements and global rules. This lesson keeps deep Flux, secrets, drift, migration, and audit implementation in the designated sibling units.
- Unit 1’s generated lesson was available for terminology alignment. No claim is made that the actual repository was modified.
- Official documentation pages listed below were consulted during generation. The selected installed version remains the authority for runnable labs.
- **Not executed:** no Argo CD/kind/Gitea command, YAML validation, install, sync, policy denial, or deletion lab was run. Examples must be validated against installed CRDs and versions.
- A full repository checkout with actual Unit 2/README/project files was not available as a mounted repository. The roadmap tree and curriculum prompt were accessible; do not infer that every sibling lesson was inspected.

#### Official documents consulted

1. **Argo CD — Architectural Overview**, API Server, Repository Server, Application Controller.  
   https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/
2. **Argo CD — Application Specification Reference**, Application fields, sync policy, finalizer examples.  
   https://argo-cd.readthedocs.io/en/latest/user-guide/application-specification/
3. **Argo CD — Projects**, source/destination/resource restrictions and project roles.  
   https://argo-cd.readthedocs.io/en/stable/user-guide/projects/
4. **Argo CD — RBAC Configuration**, global RBAC and project roles.  
   https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/
5. **Argo CD — Sync Options**, prune/delete confirmation, Replace, ServerSideApply, PruneLast, RespectIgnoreDifferences.  
   https://argo-cd.readthedocs.io/en/latest/user-guide/sync-options/
6. **Argo CD — Sync Phases and Waves**, hook phases and ordering.  
   https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/
7. **Argo CD — Generating Applications with ApplicationSet**, generators and templates.  
   https://argo-cd.readthedocs.io/en/stable/user-guide/application-set/
8. **Argo CD — ApplicationSet Specification Reference**, generator/template fields.  
   https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/applicationset-specification/
9. **Argo CD — Application Pruning & Resource Deletion**, ApplicationSet ownership and preserve-resource behavior.  
   https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Application-Deletion/
10. **Argo CD — App Deletion**, finalizer and cascade/non-cascade behavior.  
    https://argo-cd.readthedocs.io/en/latest/user-guide/app_deletion/
11. **Argo CD — Controlling Resource Modification (ApplicationSet)**, deletion-policy caveats.  
    https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Controlling-Resource-Modification/
12. **Argo CD — Security Overview**, controller cluster permissions.  
    https://argo-cd.readthedocs.io/en/latest/operator-manual/security/
13. **Argo CD — Metrics**, repo-server metric examples.  
    https://argo-cd.readthedocs.io/en/latest/operator-manual/metrics/
14. **Kubernetes — kubectl Reference**, context/CLI commands.  
    https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands
15. **Kubernetes — kubectl Quick Reference**, context and inspection commands.  
    https://kubernetes.io/docs/reference/kubectl/quick-reference/

#### Claim register — 55 technical claims

| ID | Claim | Source or verification method | Version sensitivity | Status | Residual action |
|---|---|---|---|---|---|
| C01 | API server serves UI/CLI/API and authorization | Architecture, API Server | Medium | Consulted | Confirm install topology |
| C02 | repo-server fetches/caches source and renders manifests | Architecture, Repository Server | Medium | Consulted | Test chosen renderer |
| C03 | Application controller compares desired/live state | Architecture, Application Controller | Medium | Consulted | Inspect actual status |
| C04 | Redis is a cache, not source of truth | Architecture | Medium | Consulted | Verify installed component |
| C05 | Dex/auth component depends on install/config | Architecture/auth docs | High | `[VERIFY]` | Inspect pods/config |
| C06 | ApplicationSet controller generates Applications | ApplicationSet docs | Medium | Consulted | Check installed CRD |
| C07 | Notifications component/config may be optional | Install/docs | High | `[VERIFY]` | Inspect installation |
| C08 | Application API uses `argoproj.io/v1alpha1` in curriculum | Application spec | Medium | Consulted | Validate installed CRD |
| C09 | `spec.project` selects AppProject | Application spec/Projects | Low | Consulted | Confirm project exists |
| C10 | source repo/path/revision identify rendering inputs | Application spec | Medium | Consulted | Test source connectivity |
| C11 | destination selects cluster/server and namespace | Application spec | Medium | Consulted | Validate destination |
| C12 | Sync and Health are distinct | Application docs | Medium | Consulted | Verify resource health rules |
| C13 | Sync status includes Synced/OutOfSync | Curriculum/status docs | Medium | `[VERIFY]` exact vocabulary | Capture selected-version status |
| C14 | Health labels include listed common states | Curriculum | Medium | `[VERIFY]` semantics | Confirm selected release |
| C15 | automated sync is separate from prune | Application spec | Medium | Consulted | Test Lab C |
| C16 | self-heal is a separate behavior | Application spec | Medium | Consulted | Test out-of-band change |
| C17 | prune can remove tracked resources absent from render | Sync Options | High | Consulted | Test disposable object |
| C18 | allowEmpty guards empty-render auto-sync | Application spec | High | Consulted | Verify selected version |
| C19 | CreateNamespace is a sync option | Application spec | Medium | Consulted | Review namespace ownership |
| C20 | PruneLast moves prune to final implicit wave | Sync Options | Medium | Consulted | Test dependencies |
| C21 | Replace can be destructive | Sync Options | Medium | Consulted | Avoid global use |
| C22 | ServerSideApply changes field management | Sync Options | High | Consulted | Test ownership |
| C23 | ApplyOutOfSyncOnly limits applied resources | Sync Options | Medium | Consulted | Verify hook/history semantics |
| C24 | RespectIgnoreDifferences affects sync handling | Sync Options | High | Consulted | Test field behavior |
| C25 | Validate=false disables normal validation path | Application spec/Sync Options | High | Consulted | Avoid unless justified |
| C26 | AppProject restricts source/destination/kinds | Projects docs | Medium | Consulted | Apply and test |
| C27 | Default project can be permissive | Projects docs | Medium | Consulted | Inspect local config |
| C28 | Project roles use Argo RBAC policy model | Projects/RBAC docs | Medium | Consulted | Verify group mapping |
| C29 | AppProject does not replace global Argo RBAC | Projects/RBAC docs | Low | Consulted | Audit both layers |
| C30 | Controller Kubernetes permissions govern API actions | Security docs | High | Consulted | Inspect effective RBAC |
| C31 | Admin bootstrap workflow is version-sensitive | Getting started/RBAC docs | High | `[VERIFY]` | Rotate/disable per release |
| C32 | Gitea service DNS can be used as local source endpoint | K8s service networking | Low | Design example | Test repo-server connectivity |
| C33 | Plain HTTP is lab-only, not production recommendation | Security design | Low | Recommendation | Use verified TLS/SSH in production |
| C34 | Argo CD supports Kustomize sources | Argo CD source docs | Medium | General/consulted | Validate path |
| C35 | Helm source rendering differs from `helm install` lifecycle | Argo CD Helm docs | Medium | `[VERIFY]` exact behavior | Check hooks/lookup/release visibility |
| C36 | `valueFiles` is a Helm source field | Application spec | Medium | Consulted | Validate path/version |
| C37 | `valuesObject` support is version-sensitive | Application spec | High | `[VERIFY]` | Inspect current CRD/docs |
| C38 | PreSync/Sync/PostSync/SyncFail are hook phases | Sync Phases/Waves | Medium | Consulted | Verify selected release |
| C39 | Hook deletion policy affects Job lifecycle | Sync Phases/Waves | High | `[VERIFY]` | Test marker Job |
| C40 | Waves provide ordering, not transactions | Docs + engineering inference | Medium | Qualified | Preserve migration safeguards |
| C41 | Git directory generator can generate Applications | ApplicationSet docs | High | Consulted | Validate template syntax |
| C42 | Generator changes can alter generated Applications | ApplicationSet docs | High | Consulted | Review inventory diff |
| C43 | AppSet deletion can cascade via owner refs/finalizers | Deletion docs | High | Consulted | Verify policy |
| C44 | preserveResourcesOnDeletion affects generated-app finalizer | Deletion docs | High | Consulted | Test exact semantics |
| C45 | Application finalizer can cascade-delete resources | App deletion docs | High | Consulted | Test Lab F |
| C46 | Non-cascade deletion can preserve resources | App deletion docs | High | Consulted | Verify CLI/UI procedure |
| C47 | AppSet deletion policy may not prevent owner-ref deletion | Controlling Resource Modification docs | High | Consulted | Review both policies |
| C48 | Resource tracking modes/collisions are version/config-specific | Resource tracking docs | High | `[VERIFY]` | Inspect selected release |
| C49 | Broad ignore rules can conceal meaningful drift | Sync docs + inference | Medium | Qualified | Add negative tests |
| C50 | AppProject alone is not full tenant isolation | Projects/security docs + inference | Medium | Qualified | Test all permission layers |
| C51 | CMP plugins need trust/sandbox controls | CMP/security docs | High | `[VERIFY]` details | Inspect plugin permissions |
| C52 | NetworkPolicy flows depend on CNI/architecture | K8s/M04 boundary | High | `[VERIFY]` | Test lab flows |
| C53 | Repo-server metric names/labels need version check | Metrics docs | High | Consulted | Validate actual endpoint |
| C54 | Controller outage usually delays Git sync/drift correction | Architecture + inference | Medium | Qualified | Test dependencies/recovery |
| C55 | Local kind does not prove HA/SSO/tenant isolation | Lab constraints | Low | Scope limitation | Test separately |

#### Human verification checklist

- [ ] Choose a release and record version/release notes.
- [ ] Verify install instructions, component inventory, and CRDs.
- [ ] Verify CLI install/login flags and initial admin rotation/disable workflow.
- [ ] Validate Application, AppProject, ApplicationSet manifests against installed CRDs.
- [ ] Verify sync options/defaults: CreateNamespace, PruneLast, ServerSideApply, Replace, ApplyOutOfSyncOnly, RespectIgnoreDifferences, Validate, allowEmpty.
- [ ] Verify status/health vocabulary and resource health behavior.
- [ ] Verify project restrictions and negative-test results.
- [ ] Verify hook phases, waves, hook deletion policy, and Job idempotency.
- [ ] Verify Application finalizer and non-cascade procedure.
- [ ] Verify ApplicationSet generator syntax and deletion policy.
- [ ] Verify resource tracking and ignoreDifferences behavior.
- [ ] Verify RBAC syntax and identity group mappings.
- [ ] Verify repository credentials and TLS/SSH host-key handling.
- [ ] Verify CMP plugin sandbox/network restrictions.
- [ ] Verify sync windows and notification configuration if used.
- [ ] Verify metrics endpoints/labels and durable event export.
- [ ] Render plain/Kustomize/Helm examples and inspect output before sync.
- [ ] Run all labs in disposable context; save actual output separately.
- [ ] Measure resource footprint; replace estimates only with measurements.
- [ ] Have a second reviewer inspect prune, cascade, controller RBAC, and cleanup.

#### Known limitations

1. This is a generated lesson artifact, not a claim that a source repository checkout was modified.
2. Official docs were consulted, but no particular Argo CD release was installed or selected.
3. Commands, manifests, policy denials, rendering, sync, and cleanup were not executed or validated.
4. Gitea and Helm/Kustomize snippets are teaching templates; replace version/digest placeholders and validate before use.
5. Gitea uses ephemeral storage and local HTTP; it is not production-grade Git hosting.
6. The CI policy script is regex-based and intentionally insufficient for production enforcement.
7. Local kind cannot demonstrate production HA, enterprise SSO, durable audit, or genuine multi-cluster isolation.
8. API fields, generators, sync options, finalizer/deletion semantics, tracking modes, notifications, metrics, and plugin security are version-sensitive.
9. Self-audit does not replace lab execution or human security review.

#### Ten-pass independent self-audit

| Pass | Status | Evidence and residual risk |
|---|---|---|
| 1. Completeness | FIXED | Sections 2.0–2.14, seven labs, source examples, claim register, checklists, questions and incidents are present; execution remains open |
| 2. Source fidelity | PASS | Target, scope, learner baseline, resource budget and handoffs follow supplied curriculum |
| 3. Technical accuracy | OPEN | Official docs consulted, but examples not validated against pinned release |
| 4. Version/currency | OPEN | No release installed; version-sensitive claims tagged |
| 5. Security | FIXED | Context guards, disposable objects, no real secrets, project restrictions and deletion guards included; effective RBAC/network still must be tested |
| 6. Pedagogy | PASS | Beginner-to-expert sequence, examples, failures, labs and evidence included |
| 7. Consistency | OPEN | Names/paths intended to align; manifests need render/schema validation |
| 8. Executability/evidence | OPEN | Commands have guards/evidence/cleanup; none were run |
| 9. Traceability | FIXED | Curriculum coverage and 55-claim register included; some details remain unverified |
| 10. Adversarial review | FIXED | Threat matrix and incident playbooks cover destructive deletion, cascade, overbroad project, credentials, admin, privilege escalation, repo-server pressure, sync/health confusion, migration hook, ignore rules, emergency windows and outage |

#### Adversarial review — objections and mitigations

| Objection | Mitigation | Residual risk |
|---|---|---|
| Accidental prune deletes namespace/resource | Inventory, deletion review, disposable ConfigMap lab | Bad deletion may still be approved |
| ApplicationSet deletes many Applications | Generator inventory preview and deletion policy tests | Version-specific semantics |
| AppProject too broad | Explicit allow-lists and negative tests | Project editor can weaken it |
| Repo credential compromised | Scoped read-only credentials and rotation | Malicious source changes still possible |
| Admin credential unsafe | Post-bootstrap rotation/disable and audit | Break-glass remains sensitive |
| Cluster-scoped privilege escalation | Restrict kinds/RBAC/admission; denied ClusterRoleBinding test | Other privileged paths may exist |
| repo-server OOM blocks sync | Render/performance diagnosis and metrics verification | Exact sizing needs measurement |
| Sync/Health confusion hides bad release | Business/runtime gates | Domain SLIs must be designed |
| Migration hook partial failure | Idempotency/recovery and Unit 11 handoff | Real DB-specific testing remains |
| Ignore-diff hides image/security change | Narrow field paths and negative test | Rules can become stale |
| Sync window blocks emergency fix | Bounded break-glass and post-review | Human process can fail |
| Controller outage blocks deployment | Recovery/re-adoption runbook | Other dependencies may fail too |
| Replace causes recreation/outage | No global default; resource-specific test | Behavior varies by resource |
| Plaintext secret in Git | Secret references/scanning/rotation | Render cache may still be sensitive |
| Local lab mistaken for production HA | Explicit limitations | Production design remains separate |
| Notification mistaken for durable audit | Durable export and restart test | Export pipeline may drop events |
| Regex policy treated as security boundary | Label as illustrative; require parser/schema/policy engine | Must replace before production |
| Git revert assumed to undo data effects | Explicit migration/data recovery caveat | Workload-specific recovery required |

#### Sign-off

**Content status:** DRAFT-AUDITED  
**Audit date:** 2026-10-28  
**Auditor:** AI self-audit (human verification required)  
**Unverified items count:** 25 grouped claim rows contain `[VERIFY]`, `[VERSION-SENSITIVE]`, or require human validation; individual rows may include multiple sub-checks.  
**Labs executed:** No. No commands, manifests, policy denials, installs, syncs, or cleanup procedures were executed in this generation.  
**Repository mutation:** This is a standalone generated artifact. No other repository file was intentionally modified.
