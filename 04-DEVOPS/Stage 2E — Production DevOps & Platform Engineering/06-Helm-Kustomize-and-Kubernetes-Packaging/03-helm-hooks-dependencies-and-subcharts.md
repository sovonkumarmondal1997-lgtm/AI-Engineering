# Helm Hooks, Dependencies, and Subcharts

**Module:** M06 — Helm, Kustomize, and Kubernetes Packaging  
**Unit:** 3 — Helm hooks, dependencies, and subcharts  
**Target file:** `03-helm-hooks-dependencies-and-subcharts.md`  
**Estimated time:** 10–14 hours: 3–4 hours reading, 3–4 hours cluster-free work, 4–6 hours `kind` work  
**Prerequisites:** M01–M05 and M06 Units 1–2; Kubernetes Jobs, Deployments, Services, ConfigMaps, Secrets, and Helm chart basics  
**Core tools:** Helm CLI, `kubectl`, `kind`, shell, local chart workspace  
**Optional / awareness:** Helmfile, GitOps app-of-apps, chart-review/scanning utilities; no paid tool required  
**Last reviewed:** Not independently verified  
**Tool baseline assumed:** No fixed versions assumed. Record installed versions and verify version-sensitive behavior with official documentation and `helm <command> --help`.

> **Safety and accuracy rule:** Hooks and dependencies add lifecycle behavior and execution risk; they do not make an operation transactional, safe, or correct. Review rendered manifests and understand side effects before installing or upgrading. Examples below are educational. Outputs are marked illustrative unless explicitly produced by your own commands. Never use production credentials, data, clusters, or release names in these labs.

## 1. Why this matters in production

Helm hooks run workloads at specific release lifecycle points. A migration hook can fail after it has already changed a database, leaving the application and schema in an incompatible state. A hook Job may also remain after the release operation finishes, consuming quota or exposing logs longer than intended. Dependencies introduce another source of change: a parent chart can render different Services, RBAC rules, images, or security settings after a subchart update even when the parent templates did not change. A version range is a selection rule, not proof that every selected version has been tested with your application.

The production engineering task is therefore larger than “add an annotation” or “run `helm dependency update`.” You must reason about ordering, retry behavior, side effects, compatibility, ownership, cleanup, dependency provenance, and rollback limits. A successful Helm command does not prove that a database migration was semantically correct or that the application is healthy. A committed `Chart.lock` improves repeatability but is not a signature, security review, or guarantee that a dependency is trustworthy.

This unit uses a FastAPI scoring API, a background worker, an optional local PostgreSQL subchart, a migration Job, and a smoke-test hook. The database is enabled only for local development; production-like values point to an externally managed database using secret injection supplied outside this chart. Migration hooks are a teaching pattern, not a universal recommendation.

## 2. Learning objectives

By the end of this unit, you should be able to:

- **L1:** Explain all nine Helm hook events and identify when rendering differs from execution.
- **L1:** Read `helm.sh/hook`, `helm.sh/hook-weight`, and `helm.sh/hook-delete-policy` annotations and explain cleanup caveats.
- **L1:** Explain parent charts, subcharts, dependencies, `Chart.lock`, and `charts/`.
- **L2:** Build a local umbrella chart with API and worker dependencies and an optional database controlled by `condition`.
- **L2:** Render hook resources and identify their annotations without claiming that rendering executes them.
- **L2:** Compare `helm dependency update`, `helm dependency build`, and `helm dependency list`.
- **L3:** Design bounded, observable, least-privilege, idempotent migration hooks with deliberate retry and cleanup behavior.
- **L3:** Select among an init container, Helm hook, standalone Job, operator, or application-managed migration.
- **L3:** Review dependency changes using lock-file diffs, rendered manifests, security inspection, and a disposable-cluster test.
- **L4:** Diagnose failed hooks, orphaned Jobs, dependency regressions, and partial migration side effects without assuming rollback can undo them.
- **L4:** Define dependency-source policy, ownership, upgrade approval, and evidence requirements for a platform team.

## 3. Prerequisites, versions, and lab safety

### 3.1 Record versions first

Create a workspace outside any production repository:

```bash
mkdir -p "$HOME/m06-unit3-lab"
cd "$HOME/m06-unit3-lab"
{
  date -Is
  helm version
  kubectl version --client
  kind version
} > versions.txt 2>&1
cat versions.txt
```

For a disposable cluster, add the server version only after you have verified the current context:

```bash
kubectl config current-context
kubectl version
```

The exact output shape differs across releases. Do not paste credentials, tokens, or secret values into evidence. Helm behavior, hook timing, dependency parsing, flags, and release-storage details can change; mark and locally verify `[VERSION-SENSITIVE][VERIFY]` items using the documentation matching your installed version.

### 3.2 Lab safety rules

- Use a uniquely named `kind` cluster and a dedicated namespace.
- Before every mutation, inspect `kubectl config current-context`; stop if it is not the lab cluster.
- Never delete an existing cluster or namespace that you did not create for this lab.
- Do not use real database credentials. Examples refer to an externally injected Secret by name but do not create a real credential.
- Do not treat `--atomic` as a transaction across Helm, database state, PVC data, CRDs, or external systems.
- Keep hooks short and bounded. A long backfill is usually a poor fit for a release-blocking hook.
- Render and inspect first. `helm template` does not execute hooks or contact the API server.

### 3.3 Scope boundaries

Unit 2 owns the basic chart/template/values/schema concepts. Unit 4 owns comprehensive chart testing, linting, SemVer release policy, and upgrade-test automation. Unit 7 owns OCI chart distribution, signing, and provenance. Unit 8 owns deeper CRD/operator/controller lifecycle. M03 covers Jobs and rollout behavior; M05 covers persistence and stateful-workload risks; M08 owns GitOps reconciliation; M09 owns production secret-management systems; M12 expands supply-chain security; M16 covers platform golden paths. Helmfile and GitOps app-of-apps are awareness topics here, not required installations.

## 4. Concept map and vocabulary

```text
Chart.yaml dependencies + parent values + subchart values
                     |
                     v
          helm dependency build/update
                     |
           Chart.lock + charts/*.tgz
                     |
                     v
        helm template (cluster-free render)
          |                         |
          | regular resources       | hook-annotated resources
          v                         v
   rendered manifests         rendered hook manifests
          |                         |
          +------------+------------+
                       |
              inspect / diff / validate
                       |
             helm install / upgrade
                       |
       hook execution at lifecycle events
                       |
        API server -> controllers -> Pods/Jobs
                       |
          database / application side effects
```

`helm template` is a render-time step. Hook execution happens during an install, upgrade, rollback, delete, or test workflow that invokes Helm against a cluster. Rendering is necessary evidence, but it does not prove API-server acceptance, Job completion, migration correctness, or application health.

| Term | Precise definition | Common misconception |
|---|---|---|
| Parent chart | Chart that declares one or more dependencies | It does not create a distributed transaction across dependencies |
| Dependency | Another chart included by a parent chart | A dependency update is not automatically safe |
| Subchart | A chart rendered as a dependency of another chart | Parent templates cannot generally override arbitrary subchart templates directly |
| Umbrella chart | Parent chart used to coordinate related components | It does not guarantee all components upgrade or roll back atomically |
| Hook | A Kubernetes resource annotated for a Helm lifecycle event | It is not managed exactly like an ordinary release resource |
| Hook weight | Ordering value used among hooks for an event | Do not rely on undocumented tie ordering |
| Deletion policy | Annotation controlling selected hook-resource cleanup moments | It is not a general garbage collector |
| `Chart.lock` | Resolution record produced for declared dependencies | It is not a signature or proof of trust |
| `charts/` | Conventional directory for packaged chart dependencies | Contents are not inherently safe just because they are vendored |
| `condition` | Values path used to enable/disable a dependency | A condition does not prove its external prerequisites exist |
| `tags` | Grouping mechanism for enabling/disabling dependencies | Tags should not be used as a substitute for clear environment design |
| `alias` | Alternate dependency name for a chart instance | Aliasing does not isolate the chart’s security or resource behavior |
| `import-values` | Mechanism for importing selected child values into parent values | Exact mapping semantics should be checked for the installed Helm version |
| Migration | Change to database schema or data | Helm rollback does not reverse arbitrary database effects |
| Expand/contract | Compatibility strategy that separates additive changes from later removals | It does not remove the need to test real application/schema compatibility |

### 4.1 Hook lifecycle events

| Event | Broad timing | Plausible use | Key risk |
|---|---|---|---|
| `pre-install` | Before ordinary resources are installed | A bounded prerequisite check | The expected release resources may not exist yet |
| `post-install` | After installation; interaction with wait settings is version-sensitive | Smoke test after rollout | “Hook succeeded” may not mean the application is correct |
| `pre-upgrade` | Before new ordinary upgrade resources are applied | Backward-compatible schema migration | Partial database changes may remain if the upgrade fails |
| `post-upgrade` | After upgrade resources are applied; wait interaction must be verified | Post-deployment smoke check | New application may not be healthy or semantically correct |
| `pre-delete` | Before ordinary release resources are deleted | Controlled external deregistration | Cleanup may be destructive or fail, blocking the operation |
| `post-delete` | After release deletion | Notify an external system | Ordinary release resources may already be gone |
| `pre-rollback` | Before rollback resources are applied | Validate a rollback prerequisite | External state may not be rollback-compatible |
| `post-rollback` | After rollback resources are applied | Smoke test after rollback | It cannot reverse database or external side effects |
| `test` | When `helm test` is invoked | A smoke-test Job | A test is only as meaningful as its assertions |

Exact sequencing, wait interactions, supported annotations, and command options are `[VERSION-SENSITIVE][VERIFY]`. Check the official Helm hook documentation for your installed major version. Do not assume that same-weight hooks have a stable ordering unless the documentation explicitly guarantees it.

### 4.2 Hook annotations and cleanup

Common annotations include:

```yaml
metadata:
  annotations:
    helm.sh/hook: pre-upgrade
    helm.sh/hook-weight: "-5"
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
```

The event annotation identifies when Helm should execute the resource. The weight influences ordering among hooks for the same event. Deletion policies specify selected cleanup moments. Common policy names include `before-hook-creation`, `hook-succeeded`, and `hook-failed`; verify accepted values and precise behavior locally.

| Policy | Broad effect | Caveat |
|---|---|---|
| `before-hook-creation` | Removes a previous hook resource before creating a new instance, according to Helm’s documented behavior | Verify exact behavior for the installed version; it does not clean every historical object |
| `hook-succeeded` | Requests deletion after successful hook execution | A failed Job may remain for diagnosis |
| `hook-failed` | Requests deletion after hook failure | Removing failed evidence too early can make incident analysis harder |

Hook-created resources do not participate in release tracking and cleanup exactly like ordinary resources. Never assume `helm uninstall` will remove every hook-created object. Use explicit naming, deletion policies, labels, inspection, and an owner-aware cleanup runbook.

Minimal example:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: scoring-migration
  annotations:
    helm.sh/hook: pre-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
spec:
  backoffLimit: 1
  activeDeadlineSeconds: 120
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migration
          image: example.invalid/scoring-migrator:REPLACE_ME
          command: ["python", "-m", "app.migrate"]
```

This is illustrative, not a runnable image. It lacks the full security context, resource budget, connection configuration, and chart-specific naming. Do not deploy it unchanged. `helm template` should show the Job with its hook annotations; it will not execute the command.

### 4.3 Dependency metadata

| Field | Meaning | Example | Common pitfall |
|---|---|---|---|
| `name` | Dependency chart name | `worker` | Must match the dependency chart identity |
| `version` | Version constraint for the chart package | `"1.2.3"` | A range can select a newer, untested release |
| `repository` | Chart source or local dependency location | `"file://../worker"` | Relative paths must resolve from the parent chart as expected |
| `condition` | Values path controlling dependency enablement | `postgresql.enabled` | Misspelled paths can leave expected resources enabled/disabled incorrectly |
| `tags` | One or more dependency tags | `["data"]` | Conflicting environment values can make feature intent unclear |
| `alias` | Alternate name for the dependency instance | `worker-canary` | Two instances can still collide if templates generate weak names |
| `import-values` | Import mapping from child values to parent values | `- child: exports\n  parent: importedWorker` | Mapping syntax and behavior require version-matched documentation |

Example parent `Chart.yaml` with local dependencies:

```yaml
apiVersion: v2
name: scoring-platform
description: Local teaching umbrella chart
type: application
version: 0.1.0
appVersion: "1.0.0"
dependencies:
  - name: api
    version: "0.1.0"
    repository: "file://charts-src/api"
  - name: worker
    version: "0.1.0"
    repository: "file://charts-src/worker"
    tags:
      - background
  - name: postgresql
    version: "0.1.0"
    repository: "file://charts-src/postgresql"
    condition: postgresql.enabled
```

The local `file://` layout is used for the self-contained lab. The `version` values must match the child charts’ `Chart.yaml` versions. Exact support and syntax should be checked against your installed Helm version.

### 4.4 Dependency commands

| Command | Purpose | Cluster needed? | What it does not prove |
|---|---|---:|---|
| `helm dependency update ./scoring-platform` | Resolves declared dependencies and updates packaged dependencies/lock information | No | Does not prove compatibility, security, or runtime correctness |
| `helm dependency build ./scoring-platform` | Builds dependencies using the lock file when available | No | Does not make the locked chart trustworthy |
| `helm dependency list ./scoring-platform` | Lists declared/resolved dependency information | No | Does not replace inspection of chart contents |
| `helm template demo ./scoring-platform -f values.yaml` | Renders resources | No | Does not execute hooks or validate runtime behavior |
| `helm get hooks demo -n lab` | Retrieves hook information for a release, where supported | Yes | Does not prove a hook succeeded semantically |
| `helm test demo -n lab` | Runs test hooks for a release | Yes | Does not prove all production scenarios are correct |

A dependency range is a selection rule, not a compatibility promise. `Chart.lock` records dependency resolution and helps repeat a chosen dependency set. It is not a cryptographic signature, vulnerability scan, provenance proof, or guarantee that remote artifacts will remain available. Commit the lock file when your team’s workflow uses it and review every lock-file change. Decide explicitly whether packaged dependencies under `charts/` are committed or rebuilt in CI; either approach needs a reproducible process.

## 5. Level 1 — Beginner: hooks and dependency anatomy

### 5.1 The lifecycle model

Helm templates resources and then orchestrates selected lifecycle actions. A hook is still a Kubernetes object such as a Job or Pod, but its timing is controlled by Helm annotations. Ordinary release resources and hook resources have different lifecycle/cleanup characteristics. For example, a Deployment is normally part of the release manifest; a migration Job annotated `pre-upgrade` is executed at the upgrade event and may require explicit cleanup policy.

```text
Install / Upgrade / Rollback / Delete / Test command
                    |
                    v
          Helm evaluates lifecycle
                    |
        +-----------+-----------+
        |                       |
        v                       v
  relevant pre-hook       ordinary resources
        |                       |
        v                       v
  wait for hook result     API/controller behavior
        |                       |
        +-----------+-----------+
                    |
                    v
       relevant post-hook / result
```

This is a conceptual diagram, not a universal exact ordering guarantee. Consult the installed version’s hook documentation, especially for `--wait`, timeout, and atomic behavior.

### 5.2 Inspect hooks without running them

Given a chart with a hook template:

```bash
helm template scoring ./scoring-chart --debug > rendered.yaml
grep -n -B4 -A8 'helm.sh/hook' rendered.yaml
```

Expected evidence is a Job manifest containing the hook annotation. **Illustrative expected output — not executed:**

```text
metadata:
  annotations:
    helm.sh/hook: pre-upgrade
```

This proves that the template rendered hook metadata. It does not prove that Kubernetes accepts the Job, that the image exists, that the database is reachable, or that the migration succeeds.

### 5.3 A first dependency tree

```text
scoring-platform/
├── Chart.yaml
├── values.yaml
├── Chart.lock                 # generated when dependency resolution is performed
├── charts/                    # packaged dependencies, depending on workflow
└── charts-src/                # local source for the self-contained lab
    ├── api/
    ├── worker/
    └── postgresql/
```

The parent chart controls whether a dependency is enabled and supplies dependency values. A subchart can read its own values namespace and selected global values; it does not automatically get arbitrary parent values as if all values were one flat dictionary. Use clear, documented values and render each supported configuration.

### 5.4 What a hook failure means

A failed hook generally causes the associated Helm operation to fail, but the exact release state and wait behavior must be verified for the installed version. Crucially, failure of the Helm operation does not imply that all side effects were undone. A migration may have added a column before failing. A script may have sent a notification or updated an external service. The next action is evidence collection and compatibility assessment, not automatic destructive rollback.

## 6. Level 2 — Intermediate: migration hooks and umbrella charts

### 6.1 Migration Job design

A migration Job should be short, bounded, observable, and safe to retry. Use a purpose-built image that contains the migration code; do not assume a random application image contains a shell or migration executable. The following is a template pattern to adapt, not a complete standalone chart:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "scoring.fullname" . }}-migration
  labels:
    app.kubernetes.io/name: {{ include "scoring.name" . }}
    app.kubernetes.io/instance: {{ .Release.Name }}
  annotations:
    helm.sh/hook: pre-upgrade
    helm.sh/hook-weight: "-5"
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
spec:
  backoffLimit: {{ .Values.migration.backoffLimit }}
  activeDeadlineSeconds: {{ .Values.migration.activeDeadlineSeconds }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ include "scoring.name" . }}
        app.kubernetes.io/instance: {{ .Release.Name }}
    spec:
      restartPolicy: Never
      serviceAccountName: {{ include "scoring.serviceAccountName" . }}
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: migrate
          image: {{ .Values.migration.image | quote }}
          imagePullPolicy: IfNotPresent
          command: ["python", "-m", "app.migrate"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ .Values.database.existingSecret | quote }}
                  key: {{ .Values.database.secretKey | quote }}
          resources:
            requests:
              cpu: {{ .Values.migration.resources.requests.cpu | quote }}
              memory: {{ .Values.migration.resources.requests.memory | quote }}
            limits:
              cpu: {{ .Values.migration.resources.limits.cpu | quote }}
              memory: {{ .Values.migration.resources.limits.memory | quote }}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
```

This example assumes the migration executable works with a read-only root filesystem and that the referenced ServiceAccount, Secret, image, helper templates, and values exist. It does not grant Kubernetes API permissions; a migration that only talks to a database usually should not need them. Ensure the image supports the chosen UID and runtime restrictions.

A values fragment might be:

```yaml
migration:
  image: "registry.example.invalid/scoring-migrator@sha256:REPLACE_WITH_REAL_DIGEST"
  backoffLimit: 1
  activeDeadlineSeconds: 300
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"

database:
  existingSecret: scoring-database-connection
  secretKey: DATABASE_URL
```

The digest is an explicit placeholder, not a valid digest. Replace it with an actual digest from your image pipeline. Do not commit credentials or the contents of the referenced Secret. Avoid printing the connection string in logs.

### 6.2 Failure modes to distinguish

| Symptom | Evidence | Likely cause | Safe next action |
|---|---|---|---|
| Job never starts | `kubectl describe job`, Pod events | Scheduling, quota, admission, or image pull issue | Diagnose the actual event before changing migration logic |
| `ImagePullBackOff` | `kubectl describe pod` | Invalid image/tag/digest or unavailable registry credentials | Verify image reference and pull configuration |
| Job exits non-zero | `kubectl logs job/<name>` where supported, or Pod logs | Migration code/schema/database error | Inspect redacted logs and determine committed side effects |
| Missing Secret/key | Pod events and Job logs | Secret name/key mismatch or missing external injection | Verify Secret metadata without printing values |
| Database connection failure | Redacted logs, database-side evidence | DNS, network, TLS, credentials, endpoint, or availability | Check connectivity and credential provisioning securely |
| Timeout | Job status, events, Helm status/history | Work exceeds configured deadline or waits on a lock | Determine whether work partially committed before retry |
| Helm release failed/pending | `helm status`, `helm history` | Hook failed, timed out, or command was interrupted | Collect state and logs; avoid deleting release metadata as first response |

Do not invent error strings in runbooks. Record the actual error from the environment and redact secrets.

### 6.3 Expand/contract migration sequence

A safer rollout often separates additive schema changes from destructive cleanup:

1. **Expand:** add a compatible column/table/index or other additive schema.
2. Deploy application code that can work with both old and new schema.
3. Perform a bounded migration/backfill under a separately chosen execution model.
4. Verify new code no longer needs the old schema.
5. **Contract:** remove obsolete schema in a later release after old application versions and consumers are gone.

A `pre-upgrade` hook can be suitable for a short, backward-compatible migration, but is a poor fit for a multi-hour backfill or a change that makes the currently running version incompatible. Helm does not create a database transaction around the hook and cannot infer how to reverse its changes.

### 6.4 Hook vs other execution mechanisms

| Mechanism | Timing | Strength | Risk / limitation | Often suitable for |
|---|---|---|---|---|
| Init container | Before each Pod’s app containers start | Per-Pod initialization; naturally tied to Pod lifecycle | Runs per Pod and can race across replicas; poor fit for one-time coordinated schema changes | Downloading/validating per-Pod prerequisites |
| Helm hook | At a Helm release lifecycle event | Explicitly tied to install/upgrade/rollback/test | Can block release; cleanup and partial side effects need design | Short, bounded release prerequisite or smoke test |
| Standalone Job from pipeline | Explicitly invoked by release automation | Separate approval, logging, retry, and timeout controls | Pipeline must coordinate ordering and failure handling | Controlled migrations or backfills |
| Operator/controller | Continuously reconciles desired state | Handles ongoing lifecycle and retries | Requires controller lifecycle and operational expertise | Long-running reconciliation of a domain resource |
| Application startup migration | On application startup | Convenient for small applications | Multiple replicas can race; startup/readiness may be coupled to schema work | Small apps with explicit locking and compatibility guarantees |

Choose based on coordination needs, not convenience alone. A database migration is usually a once-per-release coordination problem, while an init container is per-Pod. An operator is appropriate for continuous reconciliation, not just because a task is complex.

### 6.5 Umbrella chart values

A parent chart can use a condition to disable a local database in production-like environments:

```yaml
# Parent values.yaml
global:
  imagePullPolicy: IfNotPresent
api:
  replicaCount: 2
worker:
  replicaCount: 1
postgresql:
  enabled: true
  auth:
    existingSecret: scoring-postgresql
database:
  mode: embedded
  existingSecret: scoring-database-connection
```

Development values can enable the toy PostgreSQL dependency. Production-like values should disable it and select external database configuration:

```yaml
# values-prod.yaml
api:
  replicaCount: 3
worker:
  replicaCount: 2
postgresql:
  enabled: false
database:
  mode: external
  existingSecret: scoring-database-connection
```

The external Secret must be provisioned by an approved secret-management workflow. The chart must not create a fake password or place real credentials in values.

Subchart values are commonly provided under the dependency name, such as `worker.replicaCount`. `global` values are useful for genuinely shared configuration, but excessive global settings couple otherwise independent charts. Tags group optional features; aliases allow multiple dependency instances; `import-values` can expose selected child values to the parent. Exact semantics for dependency fields should be checked in the installed Helm version’s official docs.

### 6.6 Version constraints and dependency resolution

An exact version pin expresses a specific requested chart version. A SemVer range such as `^1.2.0` or `~1.2.0` is a range-selection rule whose precise interpretation depends on Helm’s dependency version parser and version format. A range does not mean the whole range is compatible with your application. For production, use a tested dependency set and review lock-file changes.

| Strategy | Repeatability | Flexibility | Main risk |
|---|---|---|---|
| Exact pin | High for declared version selection | Low | Updates require deliberate edits |
| Version range | Lower unless resolved and locked | Higher | A newly eligible version may be untested |
| Committed `Chart.lock` | Helps repeat the resolved set | Requires intentional lock updates | Not a signature or trust guarantee |
| Local `file://` dependency | Good for a controlled monorepo lab | Local layout coupling | Relative paths/layout can break builds |

Commands, from the parent chart’s directory:

```bash
helm dependency list .
helm dependency update .
git diff -- Chart.yaml Chart.lock
helm dependency build .
helm dependency list .
```

Use `helm dependency update` when intentionally resolving dependencies. Use `helm dependency build` when you intend to rebuild from the recorded lock state. Confirm exact behavior with the installed version’s help and docs. Do not silently accept a lock-file diff in a production dependency update.

### 6.7 Recognizing hook resources

```bash
helm template scoring ./scoring-chart -f values-prod.yaml > rendered-prod.yaml
grep -n -B3 -A6 'helm.sh/hook' rendered-prod.yaml
```

These are separate checkpoints:

1. **Render-time correctness:** the chart generated the intended objects and annotations.
2. **API-server acceptance:** the target cluster accepts the objects and policies.
3. **Hook execution:** the Job actually runs and reaches a Kubernetes terminal state.
4. **Semantic success:** the migration or smoke test verifies the intended database/application outcome.

Passing one checkpoint does not prove the next.

## 7. Level 3 — Advanced: lifecycle reliability and dependency control

### 7.1 Production hook design rules

A robust hook should be:

- **Idempotent:** retrying it should not duplicate destructive side effects.
- **Bounded:** configure `backoffLimit` and `activeDeadlineSeconds` based on the task’s expected duration and safe retry budget.
- **Observable:** capture Job state, events, exit status, and redacted logs.
- **Least privilege:** do not grant Kubernetes API permissions to a migration container unless it demonstrably needs them.
- **Resource-bounded:** requests and limits should reflect tested workload behavior.
- **Deterministically named or safely recreated:** Job templates are subject to Kubernetes immutability constraints; avoid reusing a name in a way that collides with a previous Job.
- **Explicitly owned:** document who cleans up failed and successful hook resources and how evidence is retained.
- **Secret-safe:** do not log credentials, SQL parameters containing personal data, or sensitive rows.
- **Compatibility-aware:** the migration must be compatible with currently running code and the new code during the rollout.

Retries can make a bad migration worse. A migration should use database transactions where appropriate, checkpoints, idempotent DDL/data operations, or explicit resume logic. These techniques depend on the database and migration framework; do not assume every DDL operation is transactional in every database.

### 7.2 Hook ordering, wait, timeout, and atomic behavior

Hook weights help order hooks for the same lifecycle event. They do not replace dependency readiness checks or make a sequence transactional. `[VERSION-SENSITIVE][VERIFY]` exact hook sequencing relative to ordinary resources and `--wait` for the installed Helm version.

`--wait`, `--timeout`, and `--atomic` affect Helm’s handling of release operations, but exact semantics and defaults must be verified against installed documentation. Do not promise that atomic behavior reverses a database migration, external API call, PVC contents, CRD effect, or any side effect outside Helm-managed Kubernetes resources. If a hook fails after partial database changes, investigate schema state before retrying or rolling back.

### 7.3 Hook failure and cleanup runbook

1. Verify cluster context and namespace.
2. Capture `helm status`, `helm history`, and the exact command/options used.
3. Inspect the relevant Job and Pods with `kubectl get`, `kubectl describe`, and logs.
4. Determine whether the hook failed before doing work, during work, or after partial commit.
5. Verify database schema/application compatibility using database-safe procedures.
6. Choose a mitigation: fix a transient infrastructure issue, resume an idempotent migration, apply a reviewed forward fix, or restore data only under a database-specific recovery plan.
7. Clean up only known lab-owned resources after evidence has been retained.
8. Add a regression test, timeout/retry adjustment, or migration compatibility check.

Do not delete Helm release Secrets or database objects as a first-line fix. Such deletion can destroy useful state or make recovery harder.

### 7.4 Helm test hooks

A test hook can run a bounded smoke-test Job when `helm test` is invoked. Example:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "scoring.fullname" . }}-smoke
  annotations:
    helm.sh/hook: test
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
spec:
  backoffLimit: 0
  activeDeadlineSeconds: 60
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: smoke
          image: curlimages/curl:REPLACE_WITH_APPROVED_TAG_OR_DIGEST
          command: ["sh", "-c", "curl --fail --silent --show-error http://{{ include \"scoring.fullname\" . }}:{{ .Values.service.port }}/health"]
```

This snippet is illustrative and must be adapted: verify the image reference, shell availability, Service DNS/name, port, and health endpoint. For a security-sensitive deployment, pin the image by digest and review its provenance. A successful test proves only that the assertion in the test passed in that environment. It does not prove full load capacity, all routes, data correctness, or production network policy behavior. Verify `helm test` flags against the installed version.

### 7.5 Subchart pitfalls

| Pitfall | Failure mode | Control |
|---|---|---|
| Weak `fullname` convention | Two subcharts create colliding names | Render all dependencies; use release/component-aware names |
| Same chart included twice | Duplicate resource names/selectors | Use aliases only with verified unique naming support |
| Global value leakage | Unintended settings shared across components | Keep globals minimal and documented |
| Large third-party values surface | Unreviewed knobs and unsafe combinations | Expose only a narrow parent interface; document overrides |
| Dependency upgrade changes Service/selector/port | Clients break despite unchanged parent templates | Diff rendered output and test consumers |
| Directly overriding dependency templates | Unsupported/fragile customization | Configure supported values, fork/vendor, upstream a change, or use a reviewed post-renderer |
| Untrusted dependency | Privileged Pod, broad RBAC, `hostPath`, or unsafe image | Inspect source, templates, values, hooks, and rendered output |
| Range resolves newer version | Untested API or behavior change | Pin intentionally, inspect `Chart.lock`, test upgrade |

`helm pull --untar` is a useful inspection technique for chart sources from supported repositories, but verify exact syntax and source configuration for the installed version. A lock file is not a security boundary. Review chart templates and rendered output for privileged containers, `latest` tags, broad RBAC, host mounts, cluster-scoped resources, hooks, unexpected Services/ports, and schema/value complexity.

### 7.6 Release architecture trade-offs

| Architecture | Benefits | Costs / risks | Choose when |
|---|---|---|---|
| Umbrella chart: API + worker + optional DB | One coordinated release interface; convenient local lab | Shared blast radius; lifecycle coupling; rollback is not a distributed transaction | Components are tightly coupled and tested together |
| Independent Helm releases | Independent lifecycles and ownership | Ordering and compatibility coordination must be implemented | Teams/components need separate release cadences |
| Scripts / Helmfile orchestration | Explicit sequence and repeatable command execution | Scripts must report partial completion and handle retries/timeouts | A small number of releases need deterministic orchestration |
| GitOps app-of-apps | Declarative orchestration and reconciliation | Controller-specific ordering/health semantics; complexity | Platform has an established GitOps model; detailed coverage is M08 |

Helm does not provide a distributed transaction across multiple releases. If API upgrade succeeds and worker upgrade fails, you may have a mixed-version system. Define compatible version ranges, sequencing, health gates, and recovery options.

### 7.7 CRD-providing dependencies

A dependency can install CRDs and custom resources, but CRD establishment and custom-resource acceptance introduce ordering and readiness concerns. A dependency condition merely controls whether a chart is included; it does not prove the CRD is established or its controller is ready. Helm’s special handling of files under `crds/` has lifecycle limitations, including version-dependent install/upgrade/delete behavior `[VERSION-SENSITIVE][VERIFY]`. A separately managed CRD lifecycle or a controlled platform pipeline may be safer. Unit 8 covers operators and CRDs in greater depth.

## 8. Level 4 — Expert: release orchestration and incident response

### 8.1 Release orchestration and policy

A release script should have explicit steps, fail-fast behavior, bounded retries, timeouts, and a final status that accurately reports partial completion. It should not report “all released” if the API upgraded but the worker did not. Record each release’s previous and target versions, render/diff evidence, and rollback limitations. Awareness tools such as Helmfile can coordinate independent releases; full GitOps reconciliation is deferred to M08.

A dependency-source policy should include:

- an allowlist of approved repositories/registries;
- intentional dependency pins and reviewed `Chart.lock` changes;
- source, maintainer, changelog, and breaking-change review;
- rendered output inspection for every supported environment;
- optional internal mirroring;
- a documented accept / accept-with-overrides / fork-vendor / reject decision;
- supply-chain integrity/signing handoff to Unit 7 and M12.

### 8.2 Third-party dependency upgrade workflow

1. Identify the proposed chart version and source.
2. Read release notes, changelog, and breaking changes.
3. Edit dependency metadata intentionally.
4. Run `helm dependency update` only when deliberately resolving new versions.
5. Review the `Chart.lock` diff.
6. Fetch/unpack the dependency in an isolated workspace and inspect templates, values, schema, hooks, images, RBAC, volumes, and security context.
7. Render all supported environment values.
8. Diff the previous and proposed rendered manifests.
9. Validate against the target Kubernetes version and organizational policies.
10. Test install/upgrade in a disposable `kind` cluster.
11. Record acceptance or rejection and the rollback constraints.

Steps 1–9 can largely be performed without a cluster. Live install/upgrade and runtime verification require a disposable cluster. None of these steps alone proves the publisher or image is trustworthy; use the Unit 7/M12 supply-chain process.

### 8.3 Zero-downtime migration strategy

A zero-downtime claim requires assumptions: application versions are backward-compatible with the intermediate schema, migration locks do not block critical traffic, traffic shifting is controlled, readiness signals are meaningful, and the database supports the planned operations safely. A short hook may perform a small expand step. Long backfills should usually be separate, resumable, observable jobs with explicit coordination.

```text
Release A: old code + old schema
        |
        v
Expand schema additively (compatible with old code)
        |
        v
Deploy code that supports old and new schema
        |
        v
Run bounded backfill / verify data
        |
        v
Observe and confirm old code is no longer used
        |
        v
Later release: contract/remove old schema
```

Rollback after the expand step may be possible for application code if the old code still supports the expanded schema. Rollback after destructive contraction or irreversible data transformations may not be safe. The runbook must state what is reversible, how to restore data, who approves recovery, and how to avoid concurrent migrations.

### 8.4 Incident analyses

#### Incident 1: `pre-upgrade` migration times out after partial schema changes

**Symptom →** Helm upgrade fails or times out; the new app is not deployed, but the database schema has changed.

**Hypotheses →** Job deadline too short; database lock contention; migration partially committed; connection failure; application/schema compatibility assumption was wrong.

**Commands/evidence →**
```bash
kubectl config current-context
helm status scoring -n lab
helm history scoring -n lab
kubectl get jobs,pods -n lab
kubectl describe job <lab-owned-migration-job> -n lab
kubectl logs job/<lab-owned-migration-job> -n lab
```

**Root cause →** Determine from actual logs and database-side migration state; do not assume timeout means no changes occurred.

**Immediate mitigation →** Stop automatic retries until side effects are understood. Check schema state with a database-approved read-only inspection. Resume with an idempotent forward migration or a reviewed recovery plan.

**Prevention/regression check →** Add migration checkpoints, compatibility tests, bounded retries, a realistic deadline, and a test that simulates interruption after a partial step.

#### Incident 2: Subchart upgrade changes Service name or selector

**Symptom →** Clients cannot reach the dependency after a chart upgrade.

**Hypotheses →** Fullname helper changed; alias or release name changed; selector labels changed; dependency default changed.

**Commands/evidence →**
```bash
helm template scoring ./parent -f values-prod.yaml > proposed.yaml
grep -n -A20 -B4 'kind: Service' proposed.yaml
git diff -- previous-rendered.yaml proposed.yaml
```

**Root cause →** Confirm from rendered resource names, selectors, and the dependency changelog.

**Immediate mitigation →** If the upgrade has not occurred, block it. If live, use a compatibility route or controlled corrective release rather than blindly deleting a Service.

**Prevention/regression check →** Add rendered-name/selector assertions and a consumer smoke test.

#### Incident 3: Hook Jobs accumulate and exhaust namespace quota

**Symptom →** New Jobs or Pods cannot be created; quota events appear.

**Hypotheses →** Missing deletion policy; failed hooks retained for diagnosis; unique names generated every time without retention policy.

**Commands/evidence →**
```bash
kubectl get jobs,pods -n lab --show-labels
kubectl describe resourcequota -n lab
kubectl get events -n lab --sort-by=.lastTimestamp
```

**Root cause →** Hook lifecycle cleanup and retention policy did not match operational needs.

**Immediate mitigation →** Inventory objects and verify ownership labels/annotations. Delete only resources confirmed to belong to the lab/release and retain needed evidence first.

**Prevention/regression check →** Define success/failure retention, alert on old hook Jobs, and test cleanup after both success and failure.

#### Incident 4: Dependency range resolves a breaking release

**Symptom →** A dependency update changes rendered resources or runtime behavior without a parent-template change.

**Hypotheses →** Range selected a newer version; lock file changed; dependency repository metadata changed.

**Commands/evidence →**
```bash
helm dependency list .
git diff -- Chart.yaml Chart.lock
helm template scoring . -f values-prod.yaml > proposed.yaml
git diff -- previous-rendered.yaml proposed.yaml
```

**Root cause →** Dependency selection was treated as a compatibility guarantee.

**Immediate mitigation →** Restore the last reviewed dependency resolution and re-render/test before deployment.

**Prevention/regression check →** Pin intentionally, review lock changes, require dependency changelog review and rendered diffs.

#### Incident 5: Hook succeeds but application never becomes Ready

**Symptom →** Migration Job completes, but Deployment Pods fail readiness.

**Hypotheses →** App config mismatch; health endpoint incorrect; image unavailable; schema change incompatible; Service/port changed.

**Commands/evidence →**
```bash
helm status scoring -n lab
kubectl get deploy,pods,svc -n lab
kubectl describe pod <pod> -n lab
kubectl logs <pod> -n lab
kubectl get events -n lab --sort-by=.lastTimestamp
```

**Root cause →** Hook success was mistaken for end-to-end release success.

**Immediate mitigation →** Diagnose readiness and compatibility; roll back application manifests only if compatible with the current schema.

**Prevention/regression check →** Add a post-deployment smoke test plus readiness and database compatibility checks.

#### Incident 6: Custom resource fails because CRD is not established

**Symptom →** A custom resource cannot be created or its API kind is unavailable.

**Hypotheses →** CRD absent; CRD not established; incompatible CRD version; dependency ordering assumption incorrect.

**Commands/evidence →**
```bash
kubectl get crd
kubectl describe crd <expected-crd-name>
kubectl get events -n lab --sort-by=.lastTimestamp
helm history scoring -n lab
```

**Root cause →** Dependency presence was mistaken for CRD readiness or compatibility.

**Immediate mitigation →** Pause dependent release; follow the CRD owner’s documented installation/upgrade procedure.

**Prevention/regression check →** Separate CRD lifecycle where appropriate and test CRD establishment and custom-resource compatibility.

#### Incident 7: Dependency introduces risky security defaults

**Symptom →** Rendered dependency includes privileged settings, broad RBAC, `latest`, or `hostPath`.

**Hypotheses →** New default; values override removed; unexpected dependency source/version.

**Commands/evidence →**
```bash
grep -nE 'privileged: true|runAsUser: 0|image:.*:latest|hostPath:|kind: ClusterRole' proposed.yaml
git diff -- previous-rendered.yaml proposed.yaml
```

**Root cause →** Dependency was trusted without source and rendered-output review.

**Immediate mitigation →** Block deployment; use supported values to harden, fork/vendor, or reject the dependency.

**Prevention/regression check →** Add rendered policy checks and approved-source policy.

#### Incident 8: Retry repeats non-idempotent migration side effects

**Symptom →** Duplicate rows, repeated external actions, or inconsistent state after retry.

**Hypotheses →** Migration lacks transaction/checkpoint; retry semantics were not designed; hook execution was duplicated.

**Commands/evidence →** Inspect actual Job attempts, redacted logs, migration history, and database state using approved read-only procedures.

**Root cause →** The job was retryable operationally but not safe semantically.

**Immediate mitigation →** Stop retries; determine which operations committed; perform a reviewed forward repair or database recovery.

**Prevention/regression check →** Make operations idempotent, use unique constraints/checkpoints/transactions where supported, and test interruption/retry behavior.

## 9. SRE lens

| Indicator | Definition | Measurement caveat |
|---|---|---|
| Hook success rate | Successful hook executions / all completed hook executions in a window | Exclude or separately report still-running hooks; small samples are noisy |
| Migration duration | Time from Job start to terminal completion | Separate queue/scheduling time from actual migration runtime |
| Hook timeout count | Number of hook operations ending due to timeout in a window | Verify whether Helm timeout or Job deadline was the trigger |
| Orphaned hook Job count | Hook Jobs older than the team’s retention policy and still present | Requires reliable labels/ownership and a defined retention policy |
| Dependency drift | Count of unreviewed dependency/lock changes | A diff count does not measure severity |
| Upgrade failure rate | Failed upgrades / attempted upgrades in a window | Segment by cause; not all failures are chart defects |
| Time to diagnose | Time from alert to evidence-backed cause | Define start/end timestamps consistently |

**Illustrative SLO definition, not a benchmark:** “At least 99% of hook executions complete within their declared deadline over a rolling 30-day window.” Numerator: hook executions reaching a successful terminal state before the declared deadline. Denominator: eligible hook executions started in the window. State exclusions explicitly, such as canceled lab runs. This metric alone can hide semantic migration failures; pair it with post-release health and migration correctness signals.

### Bounded hook runbook

**Alert/symptom →** release failure, migration timeout, or old Job alert.  
**Triage →** verify context and release; capture `helm status/history`; inspect Job/Pod state, events, and redacted logs.  
**Mitigation →** assess database side effects before retrying; choose a reviewed forward fix or database recovery procedure.  
**Verification →** check schema state, workload readiness, smoke tests, and remaining hook objects.  
**Follow-up →** document root cause, improve idempotency/timeout/cleanup policy, and add regression evidence.

On a 4-CPU/8-GB laptop, render and inspect first. Run one small `kind` cluster at a time, avoid heavy operators for this unit, and remove only lab-owned resources after preserving evidence. A shared subchart helper change can affect dozens of services; use ownership, staged rollout, and fleet-wide rendered diffs to bound blast radius.

## 10. Security lens

| Threat | Control | Verification evidence | Residual limitation |
|---|---|---|---|
| Hook is arbitrary code executed during release | Review image/source, pin digest, restrict release permissions | Inspect hook template, image reference, rendered Job | Review cannot prove image contents without supply-chain controls |
| Overprivileged ServiceAccount | Do not grant API permissions unless needed; narrow RBAC | Inspect rendered Role/RoleBinding and ServiceAccount | External database permissions are outside Kubernetes RBAC |
| Credentials in values, args, or logs | Reference externally injected Secrets; redact logs | Search source/rendered evidence for known secret patterns without printing values | Secret names/metadata may still reveal architecture |
| Untrusted third-party chart | Approved-source allowlist, review and pin | Inspect repository/source, `Chart.lock`, templates, rendered YAML | Lock file is not signature or trust proof |
| Mutable image tags/unverified provenance | Prefer digest pins and verified artifact process | Inspect rendered image references | Digest alone does not prove the publisher is trusted |
| Privileged/root/hostPath/capability risk | Policy checks and hardened security context | Search rendered manifests for `privileged`, `hostPath`, root UID, capabilities | Workload compatibility must be tested |
| Destructive/non-idempotent migration | Bounded, reviewed, resumable migration; backups/recovery plan | Migration tests and interruption/retry evidence | Database semantics vary |
| Condition/alias mistake enables unwanted dependency | Render each supported values configuration | Compare dev/prod renders and dependency list | Runtime connectivity still requires testing |
| Hook cleanup omission | Explicit retention/deletion policy and old-Job alert | Inspect Jobs after success/failure | Cleanup policy is not a general garbage collector |
| CRD ordering assumption | Explicit CRD ownership and readiness checks | Inspect CRDs/events and test dependency install order | Version-specific Helm lifecycle behavior remains |
| Dependency range drift | Pin intentionally and review lock diff | `git diff Chart.yaml Chart.lock` | Locked content may still contain vulnerabilities |
| Plugin/post-renderer execution | Use trusted binaries and review invocation | Record versions and command lines | Local supply-chain compromise remains possible |

Helm hooks are workloads and must be threat-modeled like other workloads. A `Chart.lock` is not a signature. Rendering and linting do not prove runtime safety. Base64 is encoding, not encryption. Do not commit real secrets or include them in logs/evidence. Use Unit 7/M12 for artifact integrity and signing; this unit does not implement a complete signing workflow.

## 11. Production checklist

- [ ] Hook event is necessary and matches the intended lifecycle.
- [ ] Hook behavior is bounded, observable, and idempotent where possible.
- [ ] `backoffLimit` and `activeDeadlineSeconds` are justified by measured task behavior.
- [ ] Hook naming and deletion policy prevent collisions and uncontrolled leaks.
- [ ] Hook ServiceAccount/RBAC is least-privilege; unnecessary Kubernetes API access is absent.
- [ ] Migration compatibility and rollback constraints are documented.
- [ ] Secrets are injected externally and never logged or committed.
- [ ] Installed-version `--wait`, timeout, and atomic semantics have been checked against official docs.
- [ ] Dependencies have approved sources and intentional version constraints.
- [ ] `Chart.lock` changes are reviewed and committed according to team policy.
- [ ] `condition`, tags, aliases, and `import-values` are tested in supported configurations.
- [ ] Production-like values disable local PostgreSQL when an external database is intended.
- [ ] Every supported values configuration renders.
- [ ] Dependency rendered output is reviewed for naming, selectors, images, RBAC, volumes, hooks, and security context.
- [ ] CRD lifecycle has an explicit owner and documented sequence.
- [ ] Install, upgrade, failure, retry, and cleanup behavior has evidence.
- [ ] Third-party dependency source and support policy are documented.
- [ ] A runbook and recovery decision authority are available.

## 12. Hands-on labs

All labs use a disposable workspace. The commands below are examples to run locally; any output not produced by your run is labeled illustrative. Verify syntax with your installed Helm/Kubernetes versions. Never run destructive cleanup against an unknown context.

### Lab 1 — Umbrella chart for API, worker, and optional PostgreSQL

**Goal:** Build a parent chart with local toy subcharts and prove that the PostgreSQL resources are rendered only when enabled.  
**Success criteria:** dependency commands complete; a lock file is created; dev render contains the toy DB object; production-like render omits it and uses external DB configuration.  
**Estimated time:** 90–120 minutes.  
**Prerequisites:** Helm CLI and shell. **Cluster required: No** for the core lab.

File tree:

```text
umbrella-lab/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── charts-src/
    ├── api/
    │   ├── Chart.yaml
    │   ├── values.yaml
    │   └── templates/deployment.yaml
    ├── worker/
    │   ├── Chart.yaml
    │   ├── values.yaml
    │   └── templates/deployment.yaml
    └── postgresql/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/configmap.yaml
```

Create files:

```bash
mkdir -p umbrella-lab/charts-src/{api,worker,postgresql}/templates
cd umbrella-lab
```

`Chart.yaml`:

```yaml
apiVersion: v2
name: scoring-platform
description: Local umbrella chart lab
type: application
version: 0.1.0
appVersion: "1.0.0"
dependencies:
  - name: api
    version: "0.1.0"
    repository: "file://charts-src/api"
  - name: worker
    version: "0.1.0"
    repository: "file://charts-src/worker"
    tags: ["background"]
  - name: postgresql
    version: "0.1.0"
    repository: "file://charts-src/postgresql"
    condition: postgresql.enabled
```

`values.yaml`:

```yaml
global:
  environment: local
api:
  replicaCount: 1
worker:
  replicaCount: 1
postgresql:
  enabled: true
  databaseName: scoring
database:
  mode: embedded
  existingSecret: scoring-database-connection
```

`values-dev.yaml`:

```yaml
global:
  environment: dev
postgresql:
  enabled: true
database:
  mode: embedded
```

`values-prod.yaml`:

```yaml
global:
  environment: prod
postgresql:
  enabled: false
database:
  mode: external
  existingSecret: scoring-database-connection
```

`charts-src/api/Chart.yaml`:

```yaml
apiVersion: v2
name: api
description: Toy API subchart
type: application
version: 0.1.0
appVersion: "1.0.0"
```

`charts-src/api/values.yaml`:

```yaml
replicaCount: 1
```

`charts-src/api/templates/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-api
  labels:
    app.kubernetes.io/name: api
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: api
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: api
        app.kubernetes.io/instance: {{ .Release.Name }}
    spec:
      containers:
        - name: api
          image: example.invalid/scoring-api:REPLACE_ME
          ports:
            - name: http
              containerPort: 8000
```

`charts-src/worker/Chart.yaml`:

```yaml
apiVersion: v2
name: worker
description: Toy worker subchart
type: application
version: 0.1.0
appVersion: "1.0.0"
```

`charts-src/worker/values.yaml`:

```yaml
replicaCount: 1
```

`charts-src/worker/templates/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-worker
  labels:
    app.kubernetes.io/name: worker
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: worker
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: worker
        app.kubernetes.io/instance: {{ .Release.Name }}
    spec:
      containers:
        - name: worker
          image: example.invalid/scoring-worker:REPLACE_ME
```

`charts-src/postgresql/Chart.yaml`:

```yaml
apiVersion: v2
name: postgresql
description: Toy PostgreSQL dependency placeholder; not a database server
type: application
version: 0.1.0
appVersion: "1.0.0"
```

`charts-src/postgresql/values.yaml`:

```yaml
enabled: true
databaseName: scoring
```

`charts-src/postgresql/templates/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-postgresql-lab
  labels:
    app.kubernetes.io/name: postgresql-lab
    app.kubernetes.io/instance: {{ .Release.Name }}
data:
  DATABASE_NAME: {{ .Values.databaseName | quote }}
  NOTE: "Toy dependency marker only; no database server is deployed"
```

Resolve and render:

```bash
helm dependency update .
helm dependency list .
git diff -- Chart.yaml Chart.lock 2>/dev/null || true
helm template scoring . -f values-dev.yaml > rendered-dev.yaml
helm template scoring . -f values-prod.yaml > rendered-prod.yaml
grep -n 'postgresql-lab' rendered-dev.yaml
if grep -q 'postgresql-lab' rendered-prod.yaml; then
  echo "ERROR: toy PostgreSQL marker unexpectedly rendered"
  exit 1
else
  echo "PASS: PostgreSQL marker absent from production-like render"
fi
```

**Evidence and interpretation:** `Chart.lock`, dependency list output, and the two rendered manifests show dependency resolution and condition behavior. This toy “PostgreSQL” dependency deliberately renders only a ConfigMap marker; it is not a database and must not be described as one. The placeholder API/worker images are not expected to run.

**Cleanup:** From the lab workspace, remove only generated evidence files if desired; no cluster resources were created.

**Common failures:** If dependency update cannot resolve a local chart, check relative paths and child chart versions. If the DB marker appears in production, inspect the exact values path and dependency condition.  
**Stretch:** Add an `alias` or `import-values` example after checking the installed Helm documentation; render it and explain how the values shape changes.

### Lab 2 — Migration hook success, failure, and deletion behavior on `kind`

**Goal:** Observe hook execution and failure evidence in a disposable cluster.  
**Estimated time:** 2–3 hours.  
**Prerequisites:** Helm, `kind`, `kubectl`, Docker or another supported container runtime. **Cluster required: Yes.**

This lab requires a locally available test image whose command behavior you control. Do not assume a placeholder image works. A safe approach is to build a tiny image locally that contains a Python script accepting an explicit `MIGRATION_MODE` value (`success` or `fail`), and use `kind load docker-image` for the exact cluster name. Do not use a production image or credentials.

Before any mutation:

```bash
kind create cluster --name m06-u3-hooks
kubectl config current-context
kubectl cluster-info
kubectl create namespace m06-u3-hooks
```

Stop if the current context is not the cluster you created. Build and load a local image named `m06-u3-migration:lab` using a local Dockerfile and script, then verify it is loaded into the intended `kind` cluster. Use a non-root image and do not mount host directories or credentials. The script should exit zero for `success` and non-zero for `fail`; it should not connect to a database or make external changes.

Example chart template `templates/migration.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-migration
  annotations:
    helm.sh/hook: pre-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
spec:
  backoffLimit: 0
  activeDeadlineSeconds: 30
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migration
          image: m06-u3-migration:lab
          imagePullPolicy: IfNotPresent
          env:
            - name: MIGRATION_MODE
              value: {{ .Values.migration.mode | quote }}
```

`values.yaml`:

```yaml
migration:
  mode: success
```

For the first install, use a separate ordinary workload or an explicitly configured hook event that is valid for the scenario. The template above uses `pre-upgrade`, so it runs on upgrade, not as a proof of install behavior. Install the chart, then run an upgrade that triggers the hook:

```bash
kubectl config current-context
helm install scoring ./hook-lab -n m06-u3-hooks
helm upgrade scoring ./hook-lab -n m06-u3-hooks --set migration.mode=success --timeout 90s
helm status scoring -n m06-u3-hooks
helm history scoring -n m06-u3-hooks
kubectl get jobs,pods -n m06-u3-hooks
```

For controlled failure:

```bash
helm upgrade scoring ./hook-lab -n m06-u3-hooks \
  --set migration.mode=fail --timeout 90s
helm status scoring -n m06-u3-hooks
helm history scoring -n m06-u3-hooks
kubectl get jobs,pods -n m06-u3-hooks --show-labels
kubectl get events -n m06-u3-hooks --sort-by=.lastTimestamp
kubectl describe jobs -n m06-u3-hooks
kubectl logs -n m06-u3-hooks job/scoring-migration
```

The actual release state, Job name, and output depend on the installed Helm/Kubernetes version and the chart. **Illustrative expected behavior — not executed:** the failing Job reaches a failed state and Helm reports the upgrade failure; the previous application release may remain, but the test has not undone arbitrary side effects. This lab’s test image has no database side effects, so it demonstrates lifecycle failure, not real migration recovery.

Test deletion behavior by inspecting Jobs after success and failure. Because the example uses `hook-succeeded`, successful hook resources may be deleted; a failed Job may remain for diagnosis. Confirm actual behavior locally and do not assume it. Re-run only after inspecting the previous Job and its annotations.

**Evidence:** context name, Helm status/history, Job/Pod descriptions, events, redacted logs, and post-run Job inventory. This proves lifecycle behavior in the lab, not migration correctness against a real database.

**Cleanup:** Confirm the context is `kind-m06-u3-hooks`, then remove only the release and namespace you created. Delete the named kind cluster only if you created it for this lab and have preserved evidence. Never run a broad cluster deletion command against an unknown context.

**Common failures:** image pull errors mean the image was not loaded or its name/pull policy is wrong; no Job on install is expected for a `pre-upgrade` hook; logs may be unavailable if cleanup removed the successful Job.  
**Stretch:** Add a `test` hook and invoke `helm test`; document exactly what its assertion proves.

### Lab 3 — Pin dependencies with `Chart.lock` and review a chart

**Goal:** Demonstrate intentional dependency resolution and security review.  
**Estimated time:** 60–90 minutes.  
**Prerequisites:** Lab 1 chart tree. **Cluster required: No.**

From the umbrella chart directory:

```bash
helm dependency list .
helm dependency update .
git diff -- Chart.yaml Chart.lock 2>/dev/null || true
cp Chart.lock Chart.lock.reviewed
helm dependency build .
helm dependency list .
diff -u Chart.lock.reviewed Chart.lock
```

The `diff` is evidence only if your workspace is a Git repository or the files exist. For a clean review, initialize a lab-only Git repository and commit the initial state before making changes. Do not fabricate expected lock-file content; inspect the actual generated file.

Review the packaged child chart source in `charts/` according to the chosen workflow. For a real third-party chart, first select an approved source and a version verified from that source. If you use `helm pull --untar`, check `helm pull --help` and the official documentation for exact syntax and repository setup. Do not use an unreviewed chart just to complete the exercise.

Search rendered output:

```bash
helm template scoring . -f values-prod.yaml > rendered-prod.yaml
grep -nE 'privileged: true|runAsUser: 0|image:.*:latest|hostPath:|kind: ClusterRole|helm.sh/hook' rendered-prod.yaml || true
grep -nE 'kind: Service|port:|targetPort:|kind: Role|kind: RoleBinding' rendered-prod.yaml
```

A match is a review lead, not automatically proof of a vulnerability; inspect context and legitimate exceptions. Also inspect templates and default values because a disabled branch may not appear in one render.

Produce a review table in `dependency-review.md`:

| Check | Evidence | Decision |
|---|---|---|
| Source and maintainer | Repository metadata and release notes | Accept / reject / investigate |
| Version and lock | `Chart.yaml`, `Chart.lock` diff | Pin / update intentionally |
| Privileged/root settings | Templates and rendered output | Fix / exception with rationale |
| Images and digests | Image references and provenance evidence | Approve / replace / reject |
| RBAC and cluster scope | Roles, bindings, cluster-scoped objects | Narrow / approve / reject |
| Volumes and host access | `hostPath`, mounts, volumes | Remove / justify / reject |
| Hooks | Hook annotations and commands | Review execution risk |
| Services/ports/selectors | Rendered resource diff | Verify consumer compatibility |
| Values surface | `values.yaml`, schema, docs | Narrow or document |
| Final decision | Evidence and owner | Accept / overrides / fork / reject |

**Evidence and interpretation:** `Chart.lock` before/after, dependency command output, rendered manifests, and review table show whether the dependency set and generated resources were inspected. They do not prove image contents, runtime behavior, API admission, NetworkPolicy enforcement, or supply-chain authenticity.

**Cleanup:** Keep the workspace as evidence or remove only the lab workspace you created. No cluster resources were created.  
**Common failures:** an unchanged lock file may be correct if resolution did not change; a dependency build may fail if the package is missing; do not run update just to make the lock file change.  
**Stretch:** Create two local versions of a toy chart, change a range in a lab-only branch, and compare the selected dependency and lock-file diff. Do not claim a specific resolution unless your command demonstrates it.

### Optional stretch lab — Dependency range drift simulation

Create two toy dependency chart versions in a separate workspace, each with a visible `data.version-marker` value. Reference them using a supported range, run dependency resolution, and inspect `Chart.lock` and rendered output. Then pin an exact version and compare. The point is to observe that a range is a selection rule and that a lock file records a resolution; it is not to assume any particular version will be selected without running the tool.

## 13. Self-check questions

1. **What is a Helm hook, and why is it not exactly like an ordinary release resource?**  
   **Answer:** A Kubernetes resource annotated for a Helm lifecycle event. Its execution timing and cleanup/tracking behavior differ from ordinary release resources. **Tempting wrong answer:** “It is just another Deployment” ignores lifecycle and cleanup semantics.

2. **How does `pre-upgrade` differ from `post-upgrade`?**  
   **Answer:** The former runs before the new ordinary upgrade resources are applied; the latter runs after the upgrade resource phase, subject to version-specific wait semantics. **Tempting wrong answer:** assuming both run at the same time can cause incompatible migration sequencing.

3. **Do hook deletion policies guarantee all old Jobs disappear?**  
   **Answer:** No. They apply at defined lifecycle moments and are not a general garbage collector. **Tempting wrong answer:** treating a policy as a namespace-wide cleanup controller.

4. **What is the difference between a failed hook Job and a rolled-back database?**  
   **Answer:** Job failure describes execution status; database changes may already have committed. **Tempting wrong answer:** assuming Helm reverses all side effects.

5. **How do subchart values and `global` values differ?**  
   **Answer:** Values are usually scoped under the dependency name; `global` values are shared by design across charts. **Tempting wrong answer:** putting every setting in `global` creates unnecessary coupling.

6. **How do `condition` and `tags` differ?**  
   **Answer:** A condition is a values path used to enable/disable a dependency; tags group dependencies for feature toggles. **Tempting wrong answer:** assuming either one proves external dependencies are ready.

7. **Why use an exact dependency pin and `Chart.lock`?**  
   **Answer:** A pin narrows selection; a lock file records a resolved dependency set for repeatability. **Tempting wrong answer:** treating the lock file as a signature or vulnerability scan.

8. **Does `helm template` execute hooks?**  
   **Answer:** No; it renders hook-annotated resources. **Tempting wrong answer:** seeing a Job in rendered YAML does not mean the Job ran.

9. **When is a hook a poor migration mechanism?**  
   **Answer:** Long-running backfills, operations requiring separate approval/retries, or migrations with unsafe partial side effects may need a standalone Job/pipeline or another design. **Tempting wrong answer:** release coupling is not always worth the operational risk.

10. **Why can Helm rollback not undo arbitrary database changes?**  
    **Answer:** Helm manages Kubernetes release resources, not a universal transaction over external database state. **Tempting wrong answer:** restoring old manifests does not reverse data mutations.

## 14. Evidence artifacts

Save learner-generated evidence under a lab workspace, for example:

```text
~/m06-unit3-lab/evidence/
├── versions.txt
├── umbrella-chart-tree.txt
├── dependency-list.txt
├── Chart.lock.initial
├── Chart.lock.reviewed
├── rendered-dev.yaml
├── rendered-prod.yaml
├── rendered-dev-vs-prod.diff
├── hook-success-status.txt
├── hook-failure-status.txt
├── hook-history.txt
├── hook-jobs-pods-events.txt
├── hook-logs-redacted.txt
├── cleanup-observation.txt
├── dependency-review.md
├── migration-safety-decision.md
└── incident-report.md
```

These are recommended outputs, not files that already exist. Redact secret values, tokens, private endpoints where appropriate, and sensitive data. Include enough context to reproduce a finding: tool versions, command, exit status, and the relevant non-sensitive output.

## 15. Interview and design-review questions

### 1. How would you design a migration hook for a zero-downtime deployment?

**Model answer:** First establish compatibility requirements between old/new code and intermediate schema. Prefer an additive expand step, a bounded idempotent migration, a separate resumable job for long backfills, and a later contract step. If a `pre-upgrade` hook is justified, give it least privilege, a pinned image, bounded retries/deadline, explicit cleanup, and redacted observability. Validate the rendered Job and test interruption/retry in a disposable environment. Do not claim zero downtime unless lock behavior, traffic, readiness, and rollback assumptions are demonstrated.

### 2. A migration hook failed after partially applying schema changes. What do you do?

**Model answer:** Stop automatic retries. Verify context/release and collect Helm status/history, Job/Pod events, and redacted logs. Ask the database owner to inspect migration state using an approved procedure. Determine which operations committed and whether the old application remains compatible. Choose a reviewed forward repair or database-specific recovery; do not assume Helm rollback reverses the schema. Add an interruption test and make the migration resumable/idempotent where feasible.

### 3. A dependency upgrade changed the API Service name. How do you find and prevent the regression?

**Model answer:** Compare `Chart.yaml` and `Chart.lock`, inspect the dependency changelog, render old and proposed dependency sets with identical values, and diff Service names, selectors, ports, and endpoints. Verify client references and live events. Block the change until compatibility is preserved or a controlled cutover is designed. Add rendered-output assertions and a consumer smoke test to CI.

### 4. When would you choose an umbrella chart, independent releases, or GitOps app-of-apps?

**Model answer:** Use an umbrella chart when components are tightly coupled and share a coordinated release contract. Use independent releases when ownership and cadence differ, accepting the need for explicit ordering and compatibility management. Use GitOps orchestration when the platform has an established reconciliation model and its controller semantics are understood. Helm itself does not provide a distributed transaction across releases; define partial-failure and recovery behavior.

### 5. How do you govern third-party subcharts and dependency versions?

**Model answer:** Maintain an approved source allowlist, pin versions intentionally, review lock-file changes and release notes, inspect templates/defaults/hooks/RBAC/images/volumes, render every supported environment, validate policies, and test upgrades in a disposable cluster. Record the accept/override/fork/reject decision and an owner. A lock file helps repeatability but does not prove integrity or trust; signing and provenance belong to the Unit 7/M12 workflow.

## 16. Sources and verification notes

Do not claim live documentation consultation unless you performed it. Use the official documentation matching the installed Helm/Kubernetes versions.

| Topic | Official source | Version-sensitive? | Verify locally |
|---|---|---:|---|
| Chart dependencies and `Chart.yaml` | Helm Docs, “Chart Dependencies”: https://helm.sh/docs/topics/charts/ | Yes | Dependency fields, ranges, local `file://` paths |
| Hook lifecycle and annotations | Helm Docs, “Chart Hooks”: https://helm.sh/docs/topics/charts_hooks/ | Yes | Event order, hook weights, deletion policy values |
| Dependency commands | Helm CLI docs: https://helm.sh/docs/helm/helm_dependency/ | Yes | `update`, `build`, and `list` options and lock behavior |
| Template rendering | Helm CLI docs: https://helm.sh/docs/helm/helm_template/ | Yes | Exact render flags; confirm no execution of hooks |
| Release status/history | Helm CLI docs: https://helm.sh/docs/helm/helm_status/ and https://helm.sh/docs/helm/helm_history/ | Yes | Available flags and release state reporting |
| Hook retrieval/testing | Helm CLI docs: https://helm.sh/docs/helm/helm_get_hooks/ and https://helm.sh/docs/helm/helm_test/ | Yes | Command availability and supported flags |
| Kubernetes Jobs | Kubernetes Docs, “Jobs”: https://kubernetes.io/docs/concepts/workloads/controllers/job/ | Yes | Deadline/retry behavior and API version |
| Pod security context | Kubernetes Docs, “Configure a Security Context”: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/ | Yes | Supported fields and cluster policy |
| RBAC | Kubernetes Docs, “Using RBAC Authorization”: https://kubernetes.io/docs/reference/access-authn-authz/rbac/ | Yes | Role/RoleBinding scope and permissions |
| CRD lifecycle | Helm chart docs and Kubernetes CRD docs: https://helm.sh/docs/topics/charts/ and https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/ | Yes | `crds/` lifecycle and establishment semantics |
| SemVer concepts | Semantic Versioning specification: https://semver.org/ | Parser behavior is tool-specific | Do not assume Helm range semantics are identical to every SemVer library |

### Source-grounded behavior

The chapter’s central distinctions are: a hook is a resource tied to a Helm lifecycle event; `helm template` renders rather than executes it; dependencies are declared in chart metadata and resolved by Helm dependency commands; a lock file records a dependency resolution but is not a signature; and Helm rollback cannot universally undo external side effects. Confirm exact details in documentation for your installed version.

### Version-sensitive items requiring local verification

- Hook event sequencing and interactions with `--wait`.
- Accepted hook deletion policies and precise cleanup semantics.
- Dependency version-range parsing and lock-file behavior.
- `helm get hooks`, `helm test`, `helm pull --untar`, and optional flags.
- CRD handling under `crds/`.
- `--atomic`, `--timeout`, and `--wait` behavior.
- Release status/storage behavior and cleanup edge cases.

### Engineering recommendations and assumptions

- Use short, bounded, idempotent hooks only when release lifecycle coupling is valuable.
- Prefer additive expand/contract migrations for compatibility across rollout and rollback.
- Keep global values small, dependency sources approved, and lock-file changes reviewed.
- Treat rendered output as the review artifact and keep evidence for every supported environment.
- Use separate releases or an explicit migration pipeline when a hook’s failure/timeout behavior would create unacceptable release coupling.

## 17. Author's verification checklist

| Gate | Status | Evidence note |
|---|---|---|
| Exact Unit 3 scope and filename | PASS | Title and metadata identify the requested target |
| All nine hook lifecycle events explained | PASS | Event table includes all required events |
| Hook annotations, ordering, deletion and cleanup caveats | PASS | Dedicated tables and version-verification notes |
| Dependency fields, commands, `Chart.lock`, `charts/`, and `file://` | PASS | Metadata table, commands, and local umbrella lab |
| Migration hook, partial side effects, and expand/contract | PASS | Migration section and incident analysis |
| Init container / hook / Job / operator comparison | PASS | Decision table included |
| Umbrella chart and optional database condition | PASS | Complete local toy chart lab |
| Three mandatory labs and optional stretch lab | PASS | Labs 1–3 plus optional range-drift exercise |
| SRE and security lenses | PASS | Indicator and threat/control tables included |
| Interview, self-check, evidence, sources | PASS | All required sections included |
| Live Helm/Kubernetes commands executed here | NOT VERIFIED | Learner must execute in their versioned lab environment |
| All version-sensitive behavior confirmed against installed docs | NOT VERIFIED | Explicit `[VERSION-SENSITIVE][VERIFY]` notes identify checks |
| No claim that database side effects are transactional/reversible | PASS | Failure and rollback limits stated repeatedly |
| No claim that `Chart.lock` proves trust | PASS | Lock-file limitations stated |
| Only target artifact requested | PASS | Content is for `03-helm-hooks-dependencies-and-subcharts.md` only |
