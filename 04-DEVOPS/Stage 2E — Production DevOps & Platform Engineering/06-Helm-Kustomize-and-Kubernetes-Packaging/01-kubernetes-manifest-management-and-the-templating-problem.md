# Kubernetes Manifest Management and the Templating Problem

- **Module:** M06 — Helm, Kustomize, and Kubernetes Packaging
- **Unit:** 1 — Kubernetes manifest management and the templating problem
- **Target file:** `01-kubernetes-manifest-management-and-the-templating-problem.md`
- **Estimated time:** 8–12 hours: 3–4 hours reading and review, 3–5 hours cluster-free labs, 1–3 hours optional cluster labs.
- **Prerequisites:** Stage 2E M01–M05; familiarity with Deployments, Services, ConfigMaps, Secrets, ServiceAccounts, RBAC, NetworkPolicies, Jobs/CronJobs, probes, resources, HPA/PDB, and a local `kind` cluster.
- **Core tools:** `kubectl`, shell, Git, text editor, YAML-aware diff/editor; `kind` only for the optional cluster lab.
- **Awareness:** Helm and Kustomize are introduced conceptually, not fully implemented here. Jsonnet/Tanka, CUE, cdk8s, and Pulumi for Kubernetes are awareness-only.
- **Last reviewed:** Not independently verified.
- **Tool baseline assumed:** No versions assumed. Record installed versions in `versions.txt`; verify behavior against the documentation for the installed versions. Marked `[VERSION-SENSITIVE]` and `[VERIFY]` items require local confirmation.
- **Cluster needed:** Per lab below; most work is cluster-free.

> **Operating principle:** Packaging and configuration tools produce Kubernetes manifests; they do not make those manifests correct, secure, or safe to deploy. The rendered manifest is the review artifact. Abstraction must earn its complexity.

## 1. Why this matters in production

A Kubernetes manifest is an executable operational contract: it declares the workload, identity, network exposure, security posture, resources, and configuration that the cluster should attempt to maintain. A change that appears small in source control can remove a production `securityContext`, change a selector, point a service at the wrong port, or silently change an image. These failures often happen not because YAML is difficult to type, but because the same intent has been copied into multiple files and then changed unevenly.

Imagine a model-scoring API deployed to development, staging, and production. Development has two replicas and a mutable image tag; staging has one replica because someone copied an older file; production has four replicas but lost memory limits during a refactor. The files may all parse, yet they no longer describe the same application contract. A review that checks only the changed source lines can miss the operational result.

Configuration management should make intended differences explicit and accidental differences visible. It should not obscure what Kubernetes receives. The safest workflow is to generate or select the manifests, validate them, compare the result with the prior known-good version, review the diff, and only then apply them to an appropriately scoped environment. No static check can guarantee a healthy rollout, but a disciplined review catches many preventable failures before deployment.

## 2. Learning objectives

By completing this unit, the learner can:

1. **[L1]** Explain declarative desired state and distinguish `create`, `apply`, `replace`, `diff`, and dry-run operations.
2. **[L1]** Organize a consistent, internally wired set of Kubernetes manifests and read its labels, selectors, ports, and configuration references.
3. **[L2]** Detect accidental drift across copied environment directories and inventory which differences are intentional.
4. **[L2]** Explain the configuration-management spectrum from plain YAML through overlays and templates to programmatic generation.
5. **[L2]** Identify YAML quoting and scalar-typing hazards without assuming all parsers behave identically.
6. **[L3]** Design a small, explicit configuration surface and promote the same immutable application artifact with environment-specific configuration.
7. **[L3]** Produce and review rendered-manifest diffs, schema-validation evidence, and safe server-side dry-run evidence where available.
8. **[L4]** Define governance and policy checks for a fleet of services and analyze incidents caused by missing fields, drift, pruning, or CRD ordering.
9. **[L4]** Explain validation limitations, ownership boundaries, and how to safely migrate from copy-pasted manifests.

## 3. Prerequisites and lab environment

Use WSL2 Ubuntu or native Linux. The target budget is approximately 4 CPU cores, 8 GB RAM, and 30 GB disk. Most labs use only files and command-line tools. Do not run a cluster continuously if the lab does not need one.

Check available tools and record actual versions; do not infer them from a tutorial:

```bash
mkdir -p evidence
{
  date -Is
  kubectl version --client
  git --version
  (kubeconform -v 2>&1 || true)
  (yq --version 2>&1 || true)
  (kind version 2>&1 || true)
} | tee evidence/versions.txt
```

The `kubeconform`, `yq`, and `kind` commands are optional and may be absent. Verify their flags against the installed version. `kubectl diff` and server-side dry-run generally contact the API server; they are not offline validators. Never use a production context for labs.

### Scope boundaries

- **M01:** image building/publishing, digest pinning, common labels, non-root image defaults.
- **M02:** CI, release automation, SemVer, and change review.
- **M03:** workload behavior, probes, HPA/PDB, Pod Security Standards, API deprecations.
- **M04:** Ingress/Gateway, NetworkPolicy, cert-manager, and networking.
- **M05:** StatefulSets, PVCs, storage, and operator-managed databases.
- **M06 Units 2–8:** detailed Helm, Kustomize, chart testing/distribution/signing, and operators.
- **M07:** IaC installing Kubernetes/Helm resources; forward reference only.
- **M08:** Argo CD/Flux reconciliation and progressive delivery; deferred.
- **M09:** production secret-management systems; this unit covers risk, not setup.
- **M12:** supply-chain and policy systems; forward reference.
- **M16:** platform golden paths and operator frameworks; forward reference.

## 4. Concept map and vocabulary

```text
Versioned source files (Git)
  plain YAML + environment config
             |
             v
  selection / customization / generation
  (kubectl -f, Kustomize overlays, Helm templates,
   or programmatic generators — latter tools deferred)
             |
             v
  rendered YAML  ---> schema/static validation
             |                  |
             v                  v
       diff + human review <--- validation findings
             |
             v
  API server + authentication/authorization/admission
             |
             v
  controllers reconcile desired state toward live state
             |
             v
  runtime observation, alerts, and incident feedback

Versioned: source, configuration, scripts, reviewed rendered evidence.
Cluster state: live objects, managed fields, admission mutations, status.
The two can differ; a source diff is not a live-state health check.
```

| Term | Precise definition | Common misconception |
|---|---|---|
| Manifest | A serialized declaration of a Kubernetes API object. | Valid YAML means a valid or safe Kubernetes object. |
| Desired state | The configuration a user declares the system should converge toward. | Applying a file proves the workload is healthy. |
| Controller | A control loop that observes state and attempts reconciliation. | The API server itself runs the application. |
| Environment variance | A deliberate configuration difference between environments. | Every file difference is intentional. |
| Overlay/patch | A customization applied to a common set of resources. | A patch cannot accidentally remove or alter important fields. |
| Template | An input containing placeholders or logic that generates manifests. | Reviewing the template is equivalent to reviewing its output. |
| Rendered manifest | The final YAML produced after selection, customization, or templating. | It necessarily reflects admission changes or runtime state. |
| Drift | Difference between expected/source state and a comparison target, often live state or another environment. | Every difference is a defect; some are deliberate. |
| Client-side apply | Apply behavior historically based on the submitted object, live object, and last-applied configuration. | It has identical conflict semantics to server-side apply. |
| Server-side apply (SSA) | An API-server apply mechanism that tracks field management and can report ownership conflicts. | It is merely a faster spelling of client-side apply. |
| CRD / custom resource | A CustomResourceDefinition extends the API; a custom resource is an object of that API. | A directory apply always installs the CRD before its custom resources. |

### Four levels

- **L1 — Beginner:** understand files, commands, and output.
- **L2 — Intermediate:** manage a multi-component service and explicit environment differences.
- **L3 — Advanced:** create safe interfaces, validation, and promotion evidence.
- **L4 — Expert:** govern changes across teams and diagnose failure modes under operational constraints.

## 5. Level 1 — Beginner: plain manifests and desired state

### 5.1 Why environments differ—and why copied files drift

Development may use low replica counts, a local image, permissive test data, and a debug feature flag. Staging should resemble production enough to expose integration issues. Production usually needs stronger capacity, explicit resource settings, stable image identity, approved hostnames, and tighter security controls. Some variation is necessary; accidental variation is not.

Copy-paste starts simple but creates three recurring classes of drift:

1. **Workload drift:** `replicas: 2` in dev, `replicas: 1` in staging, and `replicas: 4` in prod, with no documented reason.
2. **Artifact drift:** dev references `scoring-api:latest`, staging uses `scoring-api:2026-10-01`, and prod uses an older tag. A tag may be mutable; it does not necessarily identify immutable bytes.
3. **Security/capacity drift:** production loses `runAsNonRoot` or a memory limit while someone updates only the dev and staging copies.

A fourth common class is metadata drift: inconsistent labels make inventory, policy, monitoring, or selectors less reliable. The point is not that environment directories are inherently bad; it is that every difference needs an explanation and a review mechanism.

### 5.2 Declarative configuration and desired state

A manifest says what object should exist and describes important properties. The API server validates and stores accepted objects, subject to authorization, admission, API schema, and cluster configuration. Controllers then attempt to reconcile actual state toward the declared state. For example, a Deployment controller creates or adjusts ReplicaSets and Pods to satisfy the Deployment specification. Scheduling, image pulls, storage, network policy, application startup, and dependencies can still fail after the object is accepted.

`kubectl` is a client. It sends requests, formats results, and performs local operations; it is not a guarantee engine. Successful submission means the request was accepted, not that the service is reachable or meeting its SLO. Observe rollout status, events, logs, probes, and service behavior separately.

### 5.3 `create`, `apply`, `replace`, `diff`, and dry-run

| Operation | Intended use | Important behavior / caution |
|---|---|---|
| `kubectl create -f file.yaml` | Create a new object from a manifest. | Fails if an object with the same identity already exists; not a general declarative update workflow. |
| `kubectl apply -f file.yaml` | Declare/update configuration using apply semantics. | Does not automatically delete every object whose file disappears. Apply mode and field ownership details matter. |
| `kubectl replace -f file.yaml` | Replace an existing object with the supplied representation. | More disruptive than many users expect; omitted fields and resource-version/concurrency behavior require care. Not interchangeable with apply. |
| `kubectl diff -f file.yaml` | Compare the submitted configuration with the server-side object representation that would result from apply. | Contacts the API server and requires suitable permissions. Exit status distinguishes no diff, diff found, and errors; confirm exact exit behavior for the installed version. `[VERIFY]` |
| `kubectl apply --dry-run=client -f file.yaml` | Exercise client-side processing without persisting the object. | Cannot fully validate server schema, admission, installed CRDs, or runtime behavior. |
| `kubectl apply --dry-run=server -f file.yaml` | Ask the API server to process the request without persisting it. | More authoritative for server validation/admission, but does not prove rollout, scheduling, dependency, or application success. Requires API connectivity and permissions. |

Do not write scripts that treat every non-zero `kubectl diff` exit as an API failure without accounting for the installed command's documented exit behavior. A robust CI wrapper should distinguish “diff exists” from “diff command failed”; check the exact version's reference before encoding exit codes.

Example commands (use a safe context and namespace):

```bash
kubectl config current-context
kubectl get namespace packaging-lab
kubectl apply --dry-run=client -f manifests/
kubectl apply --dry-run=server -n packaging-lab -f manifests/
kubectl diff -n packaging-lab -f manifests/
```

The namespace check above is only an example: create and inspect a dedicated namespace before mutating anything. Do not point a training script at a default or production context.

### 5.4 A complete, consistent baseline manifest set

Save the following as `baseline.yaml`. It contains a namespace, ConfigMap, Deployment, and Service. The image is a placeholder; it is **not asserted to be pullable**. The file is suitable for rendering and static inspection. To apply it, replace the image with an image available to your disposable cluster and verify image-loading requirements first.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: scoring-lab
  labels:
    app.kubernetes.io/part-of: ml-platform
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: scoring-api-config
  namespace: scoring-lab
  labels:
    app.kubernetes.io/name: scoring-api
    app.kubernetes.io/part-of: ml-platform
data:
  LOG_LEVEL: "info"
  FEATURE_SHADOW_MODE: "false"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: scoring-lab
  labels:
    app.kubernetes.io/name: scoring-api
    app.kubernetes.io/instance: scoring-lab
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: ml-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
      app.kubernetes.io/instance: scoring-lab
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
        app.kubernetes.io/instance: scoring-lab
        app.kubernetes.io/component: api
        app.kubernetes.io/part-of: ml-platform
    spec:
      serviceAccountName: default
      securityContext:
        runAsNonRoot: true
      containers:
        - name: api
          image: example.invalid/scoring-api@sha256:REPLACE_WITH_REAL_DIGEST
          ports:
            - name: http
              containerPort: 8080
          envFrom:
            - configMapRef:
                name: scoring-api-config
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: scoring-lab
  labels:
    app.kubernetes.io/name: scoring-api
    app.kubernetes.io/instance: scoring-lab
    app.kubernetes.io/part-of: ml-platform
spec:
  selector:
    app.kubernetes.io/name: scoring-api
    app.kubernetes.io/instance: scoring-lab
  ports:
    - name: http
      port: 80
      targetPort: http
  type: ClusterIP
```

**Important:** `example.invalid` and `REPLACE_WITH_REAL_DIGEST` are deliberate placeholders, so the Deployment is not runnable as written. The manifest is an instructional baseline, not a claim that a particular image exists. The `runAsNonRoot` setting is a starting control; some images need an explicit numeric UID, and pod-level security settings must be tested against the actual image. For a real application, grant a dedicated ServiceAccount and least-privilege RBAC instead of using `default` when appropriate.

Key wiring to inspect:

- The Deployment selector matches labels on its Pod template. The Service selector matches the same workload identity labels.
- The Service exposes port 80 and routes to the named container port `http`, which maps to 8080.
- The ConfigMap keys are environment variables via `envFrom`; changing the ConfigMap does not automatically restart Pods in every consumption mode.
- The `app.kubernetes.io/*` labels are useful conventions. Use labels for selection and querying; use annotations for non-selecting metadata. Keep selector labels minimal and stable. Changing a Deployment's selector is an immutable-field change in common supported API versions and may require a planned migration rather than a simple update. `[VERSION-SENSITIVE]`

### 5.5 Organizing plain manifests

A possible layout is:

```text
service/
  common/
    namespace.yaml
    configmap.yaml
    deployment.yaml
    service.yaml
  environments/
    dev/
    staging/
    prod/
```

This is an example, not the only correct layout. Small teams may prefer a single app directory; organizations may use a monorepo or a separate configuration repository. What matters is clear ownership, traceable promotion, and a way to see the final object set for each environment.

`kubectl apply -f directory/` processes supported manifest files in a directory, but it is not a general dependency orchestrator. Do not rely on it to discover arbitrary dependencies. A namespace should exist before namespaced objects are submitted; a CRD must be established and available before custom resources that use it can be accepted. Separate phases, wait for readiness where necessary, and verify API discovery. Exact ordering details are version-sensitive; do not assume a universal order beyond the documented behavior.

## 6. Level 2 — Intermediate: environment variance and the templating problem

### 6.1 Configuration-management spectrum

Choose the least complex tool that meets the actual reuse and distribution requirement. More abstraction can reduce repetition, but it also adds another language, execution step, or dependency to debug.

| Approach | Readability | Reuse | Validation/type safety | Learning curve | Debuggability | Diffability/review | Packaging/distribution | Best-fit consumers |
|---|---|---|---|---|---|---|---|---|
| Plain YAML | Very direct; duplication grows | Low without conventions | Kubernetes schema validation available; no built-in typed config interface | Low | Easy when files are small | Direct source diff; cross-file drift can be hard to see | Copy or repository checkout | Few services/environments, low variance |
| Kustomize overlays | Base plus explicit patches; patch intent can be clear | High for common resources | Output can be validated; patch semantics must be understood | Moderate | Inspect `kustomize build` output | Strong when rendered output is reviewed | Directory/repository based | Teams customizing a shared manifest set per environment |
| Helm | Templates and values separate common structure from inputs | High; charts can be versioned and distributed | Values schema and rendered-manifest validation; template logic can fail in subtle ways | Moderate to high | Must inspect rendered output and release state | Good if rendered output is retained; template diffs alone insufficient | Versioned chart/repository/OCI registry | Reusable applications consumed by many teams |
| Jsonnet/Tanka, CUE, cdk8s, Pulumi | Code or structured configuration; varies by tool | Potentially very high | Some offer stronger types/constraints; generated output still needs validation | High and tool-specific | Requires knowledge of generator and output | Generated diff is essential | Tool-specific packages/workflows | Large or highly programmatic configurations; awareness only here |

The choice is contextual. Plain YAML can be the clearest solution for a small static workload. Kustomize is attractive when environments share the same object shape but need targeted patches. Helm is useful when consumers need a configurable, versioned package. Programmatic generators can make complex constraints explicit, but introduce language/tooling dependencies. “Best” means lowest sustainable complexity for the real requirements—not most features.

### 6.2 Why templating YAML as text is hazardous

YAML has structure and scalar types. A template engine inserts text, controls whitespace, and may branch or loop before a YAML parser sees the result. An indentation error can move a field to the wrong parent; quoting mistakes can turn a string into a boolean or number; string concatenation can create invalid values; template syntax may collide with literal content. The generated text may be syntactically valid YAML but semantically invalid for Kubernetes. These are distinct validation stages:

1. Template/generation executes.
2. YAML parser interprets the output.
3. Kubernetes schema and API validation check the object.
4. Admission policies may mutate or reject it.
5. Controllers and the runtime attempt to make it work.

Each stage can fail independently. Review the final output, not just the template.

### 6.3 Configuration, secrets, code, and the variance surface

- **Code** implements behavior; changing it should normally create a new application artifact.
- **Configuration** changes behavior without rebuilding the artifact: log level, feature flag, endpoint, replica count, or resource request.
- **Secrets** are sensitive configuration such as credentials or keys. A Kubernetes Secret's base64 encoding is not encryption. Do not commit real credentials, put them in annotations, or expose them in logs/rendered evidence. Production secret systems are covered in M09.
- **Environment-specific settings** legitimately vary by environment. **Invariant settings** should remain stable unless a documented reason requires a difference.

| Setting | Common treatment | Rationale and exceptions |
|---|---|---|
| Replicas | Vary | Capacity and availability requirements differ; avoid accidental under-provisioning. |
| CPU/memory requests and limits | May vary deliberately | Capacity profiles differ; changes should be reviewed against load and SLOs. |
| Image digest | Usually invariant during promotion | Promoting the same digest improves traceability; rebuilding may be required for policy or platform reasons, but must be explicit. |
| Hostname / route | Vary | Environment endpoints differ; validate DNS/TLS and exposure. |
| Feature flag | May vary | Document rollout intent and guard against incompatible combinations. |
| Storage class / node placement | May vary | Infrastructure differs; these settings can affect availability and data durability. |
| Deployment selector | Usually invariant | Selector identity is operationally important and can be immutable. Migration requires planning. |
| Security posture | Usually invariant or stricter in production | Do not weaken security accidentally to make a lab pass. Exceptions require explicit risk acceptance. |
| Service port / application contract | Usually invariant | Changing it can break callers; coordinate contract changes. |

**Minimal variance surface:** expose only the values that need to change. Every extra knob is another state combination to test and document. A chart or generator with dozens of unrelated booleans can make invalid combinations possible; prefer a small, meaningful interface with validation.

### 6.4 Drift lab example: copied manifests

Assume three files each contain a Deployment named `scoring-api`. A deliberate drift inventory might be:

| Field | Dev | Staging | Prod | Assessment |
|---|---|---|---|---|
| Image | `scoring-api:latest` | `scoring-api:2026-10-01` | `scoring-api:2026-09-20` | Artifact mismatch; establish promotion policy. |
| Replicas | 1 | 2 | 4 | Possibly intentional; record capacity rationale. |
| `runAsNonRoot` | true | true | absent | Likely accidental security regression; investigate immediately. |
| Memory limit | 256Mi | 256Mi | absent | Likely accidental capacity/safety regression. |
| Labels | complete | missing `part-of` | different app name | Inventory/selection/policy inconsistency. |

Use `diff -u dev/deployment.yaml staging/deployment.yaml` or `git diff --no-index dev/deployment.yaml prod/deployment.yaml`. The command reveals textual differences; it cannot determine intent. A human must classify each difference as intentional, accidental, or unknown. Unknown differences are not automatically harmless.

The maintenance cost compounds: a common change must be implemented three times, tested three times, and reviewed across three copies. One omission can create an environment-specific incident. Kustomize and Helm address this duplication differently; their full mechanics belong to later units.

### 6.5 YAML scalar typing and quoting

A string contract should be written as a string. For example:

```yaml
# Ambiguous or parser-sensitive examples; do not rely on implicit typing.
featureEnabled: true
externalAccountCode: 0123
# Safer when the consuming contract expects strings:
featureEnabledText: "true"
externalAccountCodeText: "0123"
```

YAML parser/schema versions differ in how some scalar forms are interpreted. In particular, do not claim that every parser interprets `0123` identically. The key question is the intended type and the parser actually used by the toolchain. If a ConfigMap value or environment variable must be text, quote it. If a field is expected to be a boolean or integer by the Kubernetes API, use the documented type rather than quoting indiscriminately.

A simple reproducible check can use the parser installed in your environment; do not fabricate its output:

```bash
python - <<'PY'
try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is not installed; use a parser already in your toolchain or install it in a disposable virtual environment.")
from pathlib import Path
sample = "flag: true\ncode: 0123\nquoted_flag: \"true\"\nquoted_code: \"0123\"\n"
value = yaml.safe_load(sample)
for key, item in value.items():
    print(f"{key}: {item!r} ({type(item).__name__})")
PY
```

The output is parser-specific evidence, not a universal statement about YAML. Save the parser version and result with the lab. `kubeconform` validates Kubernetes object schemas against selected schema sets; it is useful but does not simulate every admission policy, installed CRD, or runtime dependency. `kubectl apply --dry-run=server` asks the API server to validate the request and is more authoritative for server-side schema/admission behavior, but still does not guarantee a successful rollout.

### 6.6 Apply models, field ownership, and pruning

Client-side apply traditionally uses the submitted configuration, the live object, and the `kubectl.kubernetes.io/last-applied-configuration` annotation to calculate a patch. The annotation is a record of the last applied configuration; it is not a complete audit trail or a guarantee of live-state equality. Apply modes and defaults evolve, so verify the behavior of your installed client/server versions.

Server-side apply (SSA) is processed by the API server and tracks field ownership in managed fields. Conflicting ownership may produce a conflict that requires deliberate resolution. Do not assume client-side and server-side apply have identical merge or conflict semantics. Use `kubectl explain`, official docs, and a disposable test to understand the mode used by your workflow. `[VERSION-SENSITIVE]`

Ordinary apply does not necessarily delete an object just because its manifest file was removed. The live object can become orphaned relative to source control. Pruning can delete objects based on selectors or ownership assumptions and is potentially destructive. `kubectl apply --prune` behavior and supported syntax are `[VERIFY]`; never trial it against a real cluster. Safer first steps are to inventory candidates, confirm namespace and owner, compare live object identities with the expected rendered set, and produce a deletion proposal for review. If pruning is used, scope it narrowly and prove the selector cannot match unrelated resources.

## 7. Level 3 — Advanced: safe configuration interfaces and rendered-manifest review

### 7.1 Design configuration as an interface

Treat environment configuration as a public interface consumed by operators and automation. Document each key, its type, allowed values, default, owner, and operational impact. Validate the interface before deployment. Defaults should be safe for the intended environment; do not rely on a hidden default that silently disables a probe or removes resource limits in production. Reject invalid combinations early rather than letting the API server or runtime discover them later.

Avoid boolean explosion. A poor interface might expose `enableIngress`, `useGateway`, `enableTls`, `useExternalTls`, `disableAuth`, `enablePublicAccess`, and many combinations that conflict. A better interface exposes a small number of mutually understandable modes, validates the chosen mode, and keeps security-sensitive decisions explicit. This is a design principle, not a universal schema shape.

### 7.2 Immutable artifacts and promotion

A mutable image tag such as `latest` can point to different bytes at different times. A digest identifies a specific image manifest and is therefore better evidence for promotion. Build once, test the artifact, and promote the same digest through dev, staging, and production while varying only approved configuration. Do not invent a digest; capture the actual digest from the build/publish workflow (M01/M02).

| Promotion model | Traceability | Reproducibility | Risk | Use when |
|---|---|---|---|---|
| Same digest, environment-specific config | Strong: same artifact identity | Strong if build and config are captured | Config differences can still create behavior differences | Default recommendation for most application promotion flows. |
| Build a distinct artifact per environment | Weaker unless build inputs and outputs are fully recorded | Lower; artifacts may diverge | Environment-specific builds can hide defects and invalidate staging evidence | Required when build-time targets or legal/security controls genuinely differ; document why. |

### 7.3 Rendered-manifest-as-review-artifact

The output after selecting files, applying overlays, or running templates is the actual object set proposed for deployment. A robust CI process should render every environment, validate the output against the intended Kubernetes API version and CRD schemas where available, save the result, diff it against the last reviewed baseline, and ask a reviewer to classify meaningful changes. Preserve the output and validation logs as release evidence.

This pattern has limitations. Generated YAML can contain secrets; redact or exclude sensitive data before storing artifacts. Some tools produce ordering or formatting noise. Nondeterministic values can make diffs unstable. Admission can mutate objects after submission, and the rendered file does not include live status. Normalize only where it is safe, preserve the original output for audit, and never normalize away a meaningful field. Do not assume that a clean diff proves runtime health.

### 7.4 A verification sequence

1. **Render/select:** produce the exact object set for the target environment.
2. **Schema/static validate:** validate YAML and target API schemas; include relevant CRD schemas when possible.
3. **Inspect diff:** compare with the prior reviewed render; look for removals, selector changes, image changes, privilege changes, and capacity reductions.
4. **Server-side dry-run:** where available and appropriate, ask the intended API server to validate/admit the objects without persistence.
5. **Disposable apply:** test behavior in a dedicated namespace/cluster, with a real local image if rollout behavior matters.
6. **Observe:** check rollout status, events, logs, endpoints, and application health.

Each step catches a different class of defect. A schema validator may catch a misspelled field but not a policy violation absent from its schema. A server-side dry-run can catch admission rejection but not prove a later image pull will succeed. A successful apply does not prove the application works.

### 7.5 Drift and API compatibility

Use `kubectl diff` to compare intended configuration with a server-side comparison when permissions and API connectivity allow. It is not a complete runtime test and can be affected by defaulting, admission, permissions, or cluster state. When validating deprecated APIs, target the Kubernetes version that will receive the package and inspect the rendered `apiVersion` values—not just the source templates. A packaging abstraction can hide an obsolete API until render time. Link this work to M03's API-deprecation learning.

### 7.6 Repository and promotion trade-offs

| Model | Benefits | Costs / risks | Appropriate when |
|---|---|---|---|
| Per-application repository | Clear ownership and release cadence; isolated history | Cross-service changes and fleet-wide policy can be harder | Teams own services independently. |
| Monorepo with app and environment directories | Centralized tooling, shared policy, easy fleet-wide diff | Large repository and ownership boundaries need discipline | Shared platform standards and cross-app automation matter. |
| Separate configuration repository | Separates app source from deployment intent; can centralize environment access controls | Artifact-to-config traceability and coordinated releases need explicit links | Platform/operations team owns deployment configuration separately. |

`[RECOMMENDATION]` Directory-per-environment promotion is often easier to review than branch-per-environment because all environments remain visible in one change, but it is not universally superior. Branch promotion may fit existing release processes; it can also create merge drift and make fleet-wide comparison harder. Select based on access controls, release cadence, ownership, and audit needs.

### 7.7 Shared packages and CRDs

A shared manifest or package change can affect dozens of workloads. Require a named owner, compatibility policy, changelog, rendered diff for every consumer/environment, staged rollout where possible, and a rollback or mitigation plan. A version bump is not harmless simply because the source diff is small.

CRDs create an ordering and lifecycle boundary. The CRD establishes the API schema; custom resources depend on that API being available. Upgrading a CRD may change validation or conversion expectations. Deleting a CRD can make its custom resources unavailable and may lead to data loss or deletion behavior depending on controllers and lifecycle. Do not assume a generic directory apply sequences CRDs safely. Plan installation, upgrade, compatibility, and deletion separately; detailed operator lifecycle belongs to M05/M06 Unit 8.

## 8. Level 4 — Expert: governance, fleet impact, and incident analysis

### 8.1 Governance and policy-as-code

Governance should make safe changes repeatable without pretending every service is identical. Establish ownership for each package, a compatibility promise, deprecation windows, review requirements, and an emergency-change path. Store source and evidence in version control, but remember source control does not equal live state. Periodically compare declared state with selected live-state evidence.

Automated policy should inspect the rendered objects. Useful checks include:

- required application labels and ownership metadata;
- non-root/security-context expectations appropriate to the workload;
- resource requests/limits where platform policy requires them;
- readiness/liveness probes for long-running services where appropriate;
- disallowing mutable `latest` tags unless an approved exception exists;
- rejecting privileged containers or risky host mounts unless explicitly approved;
- API versions compatible with the target Kubernetes version;
- digest pinning where the supply-chain policy requires it;
- RBAC scope and unexpected privilege expansion;
- resource removals and selector changes in diffs.

A lightweight CI flow can run `kubectl kustomize` or another explicit renderer, `kubeconform` if installed and configured, shell or policy checks over rendered YAML, and a review diff. Exact flags and schema download behavior must be checked against the installed versions. M12 owns the deeper supply-chain and policy implementation. Schema validation is not a security audit.

### 8.2 Change-impact analysis

For every proposed change, render all supported environments and compare with the previous baseline. Highlight resource deletions, changed selectors, reduced replicas, removed resource limits, missing probes, widened RBAC, changed images, new public routes, and security-context changes. High-risk changes should require an owner or security/platform approval. If one shared base affects 40 services, the review artifact should make the 40-service blast radius visible before rollout.

### 8.3 Migration from copied YAML to a package

1. Inventory resources, owners, namespaces, and deployment mechanisms.
2. Capture a known-good rendered baseline for each environment.
3. Diff environments and classify every difference as intentional, accidental, or unknown.
4. Resolve unknowns with service owners; do not blindly choose one environment as truth.
5. Select one low-risk service as a pilot and extract the common structure.
6. Add explicit environment configuration, validation, and generated-output review.
7. Compare the new rendered output with the approved baseline; explain every meaningful change.
8. Test in a disposable environment, then roll out gradually with health checks.
9. Keep an escape hatch: retain the prior manifest/release, define rollback criteria, and stop if unexplained drift appears.
10. Expand only after evidence shows that the new abstraction is easier to operate and does not weaken controls.

### 8.4 Failure analysis

| Symptom | Hypothesis | Test / evidence | Root cause pattern | Fix | Prevention |
|---|---|---|---|---|---|
| Production Pods run without expected non-root settings | Generator/template omitted a field | Compare prior and current rendered Pod specs; inspect live Deployment template | Refactor changed common structure and no rendered diff was reviewed | Restore required settings, validate policy, roll out under incident process | Rendered security policy gate and high-risk diff approval |
| A feature flag or identifier has the wrong type/value | YAML parser interpreted an unquoted scalar differently than expected | Reproduce with the exact parser/tool version; inspect rendered YAML and consuming API contract | Implicit scalar typing crossed a string/boolean/number boundary | Quote values where contract requires strings; fix schema and regression test | Type-focused tests and explicit config schema |
| Removed source manifest remains live | No deletion/pruning owner exists | Compare inventory of source identities with live objects in the scoped namespace; verify labels and owners | Apply updated existing objects but did not own cleanup of removed objects | Confirm ownership, assess dependents, schedule a scoped deletion after approval | Document lifecycle owner; add inventory/deletion review |
| Custom resource rejected as unknown kind | CRD not installed or API not yet established | Check `kubectl get crd`, API discovery, CRD readiness/events | Directory submission was treated as dependency-aware orchestration | Apply CRD in a separate phase, wait for establishment/API discovery, then apply CR | Explicit dependency stages and CRD compatibility tests |
| A shared change unexpectedly affects many services | Common source is consumed more broadly than expected | Render/diff every consumer and inspect ownership/usage index | Impact analysis covered only the edited repository path | Mitigate/rollback, then release staged versions | Consumer inventory, compatibility policy, staged rollout |

#### Incident A: production `securityContext` disappeared

**Symptom:** a policy alert or runtime inspection shows the expected `runAsNonRoot` field is absent. **Hypotheses:** source never declared it; an overlay replaced the Pod spec; a template branch omitted it; a prior change intentionally relaxed it. **Evidence:** compare the previous approved render with the current render, then inspect the live Deployment template and admission events. **Root cause:** the package refactor changed the shared field path and no rendered policy test failed. **Mitigation:** restore the required setting after checking image compatibility, validate the new render, and roll out with normal health observation. **Prevention:** policy checks against the rendered Pod template, regression fixtures, and explicit review of security-sensitive diffs.

#### Incident B: scalar type changed

**Symptom:** a string configuration value becomes a boolean or numeric value, or a downstream parser rejects it. **Hypotheses:** different YAML parser versions, unquoted scalar, template interpolation, or an API field whose contract is not a string. **Evidence:** reproduce using the exact parser/tool chain and print both the parsed type and rendered YAML; compare with the consumer schema. **Root cause:** the source relied on implicit typing where the contract required a string. **Fix:** quote the string and add a test that asserts both value and type. **Prevention:** schema validation, parser version recording, and a regression case for identifiers with leading zeros.

#### Incident C: orphaned resource survived removal

**Symptom:** a service account, Service, or workload still exists although its file was deleted. **Hypotheses:** the deployment workflow only applies present files; another package owns the resource; pruning was not configured; a label selector excluded the object. **Evidence:** identify the exact object by kind/namespace/name, inspect labels/annotations and ownership, check deployment logs and source history, and map dependents. **Root cause:** no explicit lifecycle owner handled removal. **Mitigation:** inventory and approve a scoped deletion only after confirming ownership and impact. **Prevention:** generated object inventory, deletion review, and a documented cleanup owner. Never run broad pruning to “clean things up” without a reviewed candidate list.

#### Incident D: CRD/custom resource ordering or incompatibility

**Symptom:** a custom resource is rejected as unknown kind or fails schema validation after a CRD upgrade. **Hypotheses:** CRD was not established; wrong API version; incompatible schema; controller unavailable; upgrade order wrong. **Evidence:** inspect CRD status, API discovery, events, custom-resource version, and controller logs; compare old/new CRD schemas and release notes. **Fix:** restore a compatible CRD/controller sequence and avoid deleting CRDs as a generic rollback. **Prevention:** separate CRD lifecycle from application rollout, test upgrades with representative custom resources, and document rollback limitations.

### 8.5 Migration decision tree

- **Remain with plain YAML** if the object set is small, duplication is limited, and the rendered result is already easy to review.
- **Adopt Kustomize** if most environments share the same resources and differences are naturally expressed as targeted patches or replacements.
- **Adopt Helm** if multiple consumers need a versioned, configurable package with a defined values interface and release lifecycle.
- **Consider programmatic generation** only when concrete complexity—such as constraints, composition, or large-scale generation—justifies the additional language/toolchain.

Before choosing, ask: what repetition is being removed, what new failure modes are introduced, who owns the abstraction, how will output be validated, and can a reviewer explain the rendered result? Do not select a tool because it is fashionable.

## 9. SRE lens

### 9.1 Useful indicators

Track indicators that describe both correctness and the speed of safe change:

- configuration-change failure rate;
- percentage of supported environments rendered and validated in CI;
- schema-validation pass rate and failure categories;
- number of unexplained environment differences;
- time required to review rendered diffs;
- time to mitigate or roll back a packaging regression;
- CI render/validation duration;
- count of drift findings between declared and live state.

An illustrative SLO might be: “Over a rolling 30-day window, at least 98% of deployment configuration changes reach the validation-and-review gate without an avoidable packaging defect.” Define the numerator as changes that pass the gate without a packaging-caused rollback or emergency correction within a chosen observation period; denominator is all deployment configuration changes in that window. This target is an example, not an industry benchmark. It can be gamed if incidents are not attributed consistently, and it does not replace availability or latency SLOs.

### 9.2 Blast radius and runbook

A shared base change can affect every consumer, not only the service used to test it. Model blast radius by consumer count, environment criticality, permissions, exposed routes, stateful resources, and rollback reversibility.

**Runbook: unexpected rollout/configuration alert**

1. **Alert/symptom:** rollout fails, policy gate detects a missing field, or service behavior changes after a manifest release.
2. **Triage:** stop further promotion; identify the exact release/commit, environment, affected object identities, and previous approved render.
3. **Mitigation:** if safe and supported, restore the prior known-good configuration or use the documented release rollback; do not blindly delete/recreate stateful resources.
4. **Verification:** compare rendered and live specs, inspect rollout status/events/logs, test service health, and confirm the risky field is restored.
5. **Follow-up:** add a regression fixture/policy, document root cause and affected consumers, and review whether release gates or ownership were insufficient.

### 9.3 Local cost and capacity

Use cluster-free rendering and schema checks first. A `kind` cluster consumes memory and disk even when idle; start it only for API-server behavior, live object observation, or rollout tests. Remove only the disposable cluster created for the lab. Avoid running several local clusters and heavyweight scanners simultaneously on an 8 GB laptop. Record which checks were not run because they require a real cluster or external service.

## 10. Security lens

| Threat | Control and concrete check | What the check does not prove |
|---|---|---|
| Secret leakage in ConfigMaps, Secret YAML, values, render output, logs, or shell history | Search source/evidence for known secret markers; review `Secret` use; keep real values out of Git and rendered artifacts; use M09 secret-management controls in production. | A simple text scan cannot detect every encoded, transformed, or externally injected secret. Kubernetes Secret base64 is not encryption. |
| Excessive RBAC or workload privileges | Review `Role`, `ClusterRole`, bindings, `privileged`, host namespaces/mounts, and service-account use; enforce policy against rendered YAML. | Static checks cannot know all runtime access paths or admission changes. |
| Untrusted remote bases or generated content | Pin reviewed dependencies/versions where supported, inspect downloaded source, and validate generated output. | Pinning alone does not establish that the source is benign. Supply-chain depth is M12. |
| Mutable image tags or unproven artifacts | Enforce digest policy where required and compare the rendered image reference with build evidence. | A digest identifies content but does not by itself prove who built or approved it. |
| Insecure defaults removed during refactor | Diff security-sensitive fields and require rendered-policy gates. | A field-presence check does not establish that the chosen value is appropriate. |
| Overly broad pruning/deletion | Inventory candidate objects, verify owner/namespace/labels/dependents, require approval, and use a disposable scope for experiments. | Inventory may be incomplete if other controllers create objects dynamically. |
| Unauthorized shared-manifest changes | Protect branches, require code-owner review, retain CI evidence, and audit release identity. | Repository controls do not prove the live cluster has not drifted. |
| Local validation differs from production admission | Run server-side dry-run against a representative target cluster when permitted; test in a disposable environment. | A different cluster version, CRD set, admission configuration, or runtime dependency can still behave differently. |

Additional rules:

- Never place secret values in labels, annotations, image names, or checksum annotations. A checksum of low-entropy secret data can itself leak information through guessing.
- Do not store unredacted rendered artifacts if templates can contain secrets. If a generated output must be retained, define redaction and access controls without destroying the evidence needed to review non-secret fields.
- Do not grant a workload cluster-wide permissions merely because a chart or manifest is easier to write that way.
- Static validation is a quality gate, not a security certification.

## 11. Production checklist

Use this as a release gate. Each checkbox should be backed by a command, CI result, file, or explicit review artifact.

- [ ] `versions.txt` records `kubectl version --client` and the installed parser/validator versions.
- [ ] Environment-specific manifests/configuration are documented, and each intentional difference has an owner or rationale.
- [ ] A drift inventory exists; no unexplained differences remain between dev, staging, and prod.
- [ ] Workload selectors match Pod-template labels; selector changes are explicitly reviewed.
- [ ] Required `app.kubernetes.io/*` labels and ownership metadata are present in rendered output.
- [ ] Image references comply with the declared tag/digest policy; evidence links the digest to the build.
- [ ] Production security context and resource settings are present and checked against policy.
- [ ] Strings are quoted where the configuration/API contract requires strings; type tests cover sensitive identifiers.
- [ ] Schema validation targets the intended Kubernetes version and relevant CRD schemas are considered.
- [ ] Rendered/selected YAML is saved or otherwise preserved as review evidence and diffed against the prior baseline.
- [ ] Server-side dry-run is run where appropriate and available; errors and skipped checks are recorded.
- [ ] CRD/custom-resource ordering, compatibility, and lifecycle have an explicit plan.
- [ ] No real secrets appear in source, rendered artifacts, annotations, logs, or evidence; review/search evidence is retained safely.
- [ ] Deletion/pruning ownership is documented; proposed deletions are inventoried and reviewed.
- [ ] Rollback/mitigation steps, package owner, and escalation path are known.
- [ ] Changes to probes, resources, RBAC, exposure, selectors, and security settings receive risk-appropriate review.
- [ ] Runtime rollout and application health are checked separately from static validation.

## 12. Hands-on lab set

All paths below are lab workspaces created by the learner, not repository files to overwrite. Expected outputs are illustrative unless explicitly generated by the learner. Keep the work under a new directory such as `~/m06-unit1-labs`.

### Lab 1 — Detect copy-paste drift across three environments

- **ID:** M06-U1-LAB1
- **Goal:** Find accidental drift and distinguish it from intended differences.
- **Estimated time:** 45–75 minutes
- **Prerequisites:** shell, `diff`; Git optional.
- **Cluster required:** No.

Create this tree:

```text
lab1/
  dev/deployment.yaml
  staging/deployment.yaml
  prod/deployment.yaml
  drift-inventory.md
```

Use this base content for `dev/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  labels:
    app.kubernetes.io/name: scoring-api
    app.kubernetes.io/part-of: ml-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
        app.kubernetes.io/part-of: ml-platform
    spec:
      containers:
        - name: api
          image: example.invalid/scoring-api:dev-placeholder
          securityContext:
            runAsNonRoot: true
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
```

Create `staging/deployment.yaml` and `prod/deployment.yaml` by copying the dev file, then make these deliberate edits:

- staging: `replicas: 2`; image `example.invalid/scoring-api:staging-placeholder`.
- prod: `replicas: 4`; image `example.invalid/scoring-api:prod-placeholder`; remove `runAsNonRoot: true` and remove the memory limit; remove the `app.kubernetes.io/part-of` Pod label.

Commands:

```bash
mkdir -p lab1/{dev,staging,prod}
# Save the supplied YAML into lab1/dev/deployment.yaml, then copy and edit:
cp lab1/dev/deployment.yaml lab1/staging/deployment.yaml
cp lab1/dev/deployment.yaml lab1/prod/deployment.yaml
# Apply the deliberate edits described above using your editor.
diff -u lab1/dev/deployment.yaml lab1/staging/deployment.yaml || true
diff -u lab1/staging/deployment.yaml lab1/prod/deployment.yaml || true
```

Write `lab1/drift-inventory.md` with columns `field`, `dev`, `staging`, `prod`, `intent`, `owner/evidence`, and `action`. Mark replica differences as “requires capacity rationale”; mark missing security context/limit/label as “likely accidental—confirm with owner.” Do not decide intent from diff alone.

**Expected evidence:** diff output showing replica/image differences and missing production fields; a drift inventory that separates expected differences from unresolved ones. The evidence proves differences are visible, not that a production configuration is correct.

**Cleanup:** remove only the lab directory after preserving the evidence you need.

**Common failures:** copied files were edited inconsistently; a diff command returns non-zero because differences were found (expected); indentation was damaged. Re-run `diff` and inspect the YAML.

**Stretch:** write a small shell script that fails if `runAsNonRoot` or required resource limits are missing from any environment file. Explain why grep-only checks are brittle for general YAML.

### Lab 2 — YAML scalar typing and quoting

- **ID:** M06-U1-LAB2
- **Goal:** Observe how the installed YAML parser interprets scalars and assert the types expected by the application contract.
- **Estimated time:** 30–60 minutes
- **Prerequisites:** Python; optional PyYAML installed in a virtual environment.
- **Cluster required:** No.

Create `lab2/scalars.yaml`:

```yaml
feature_enabled: true
account_code: 0123
quoted_feature_enabled: "true"
quoted_account_code: "0123"
```

Create `lab2/check_types.py`:

```python
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("PyYAML unavailable; install it in a disposable virtual environment or use the parser used by your deployment tooling.", file=sys.stderr)
    raise SystemExit(2)

payload = yaml.safe_load(Path("scalars.yaml").read_text(encoding="utf-8"))
for key, value in payload.items():
    print(f"{key}={value!r}; type={type(value).__name__}")

# These assertions express the contract that quoted values are strings.
assert isinstance(payload["quoted_feature_enabled"], str)
assert isinstance(payload["quoted_account_code"], str)
```

Run from `lab2/`:

```bash
python check_types.py | tee type-output.txt
python -c 'import yaml; print("PyYAML", yaml.__version__)'
```

If PyYAML is not installed, create a virtual environment and install it only if network access and local policy allow; otherwise use an already-installed parser and record its version. Do not assume the output for `0123` is universal. **Expected evidence:** actual parser output plus version and passing assertions for quoted values. The output is your local observation, not a universal YAML rule.

**Cleanup:** remove the temporary virtual environment if created; preserve or delete `lab2/` according to your learning-evidence policy.

**Common failures:** wrong working directory; parser missing; a parser-specific result differs from a tutorial. Record the actual result rather than forcing an expected interpretation.

**Stretch:** add assertions for the unquoted values based on the observed parser, then explain why the production contract should not depend on ambiguous implicit typing.

### Lab 3 — Baseline validation pipeline

- **ID:** M06-U1-LAB3
- **Goal:** Create a repeatable cluster-free validation script that selects plain YAML, parses/validates it, and preserves review evidence.
- **Estimated time:** 60–90 minutes
- **Prerequisites:** `kubectl`; optional `kubeconform`; a YAML-aware editor.
- **Cluster required:** No for the baseline; server-side checks are a separate optional step.

Create this tree:

```text
lab3/
  manifests/baseline.yaml
  scripts/validate.sh
  evidence/
```

Copy the baseline manifest set from Section 5.4 to `lab3/manifests/baseline.yaml`. Create `scripts/validate.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFESTS="$ROOT/manifests"
EVIDENCE="$ROOT/evidence"
mkdir -p "$EVIDENCE"

kubectl version --client > "$EVIDENCE/kubectl-version.txt"
# Client dry-run checks client-side processing only; it is not API-server validation.
kubectl apply --dry-run=client -f "$MANIFESTS" \
  > "$EVIDENCE/client-dry-run.txt" 2>&1

if command -v kubeconform >/dev/null 2>&1; then
  # Confirm flags/schema selection for your installed kubeconform version.
  kubeconform -summary "$MANIFESTS" \
    > "$EVIDENCE/kubeconform.txt" 2>&1 || {
      echo "kubeconform failed; inspect $EVIDENCE/kubeconform.txt" >&2
      exit 1
    }
else
  echo "kubeconform not installed; schema validation skipped" \
    > "$EVIDENCE/kubeconform.txt"
fi

# Preserve the source as the selected output for plain YAML. This is not templating.
cp "$MANIFESTS/baseline.yaml" "$EVIDENCE/selected-manifests.yaml"
sha256sum "$EVIDENCE/selected-manifests.yaml" \
  > "$EVIDENCE/selected-manifests.sha256"
echo "Cluster-free checks complete; inspect evidence and limitations."
```

Run:

```bash
cd lab3
chmod +x scripts/validate.sh
./scripts/validate.sh
```

Do not mistake `kubectl apply --dry-run=client` for server validation. `kubeconform` flags and schema behavior are `[VERIFY]` for the installed release. The script intentionally says “selected output” rather than “rendered output”: plain YAML has no template renderer. In later units, Helm/Kustomize output can replace this copy step with the exact renderer command. The future pipeline order is render/select → schema validate → diff → server-side dry-run where appropriate → apply to a disposable environment → observe.

**Expected evidence:** version file, client dry-run log, validator log or explicit skip note, selected manifest copy, and checksum. This proves the workflow ran and recorded its limitations; it does not prove a real API server would admit the objects or that the image runs.

**Cleanup:** remove the lab directory when evidence is no longer needed.

**Common failures:** `kubectl` missing; validator uses different flags; baseline contains the intentional placeholder image (static schema validation may pass even though runtime image pull cannot). Keep these distinctions explicit.

**Stretch:** add a diff step against a prior evidence baseline and fail CI when a high-risk field changes without a review note.

### Lab 4 — Optional server-side dry-run and diff in a disposable cluster

- **ID:** M06-U1-LAB4
- **Goal:** Observe the difference between cluster-free checks and API-server validation.
- **Estimated time:** 45–90 minutes
- **Prerequisites:** `kind`, `kubectl`, Docker or a compatible container runtime; a dedicated local cluster.
- **Cluster required:** Yes.

Create a disposable cluster with a unique name; do not reuse or delete a pre-existing cluster:

```bash
kind create cluster --name m06-u1-disposable
kubectl config current-context
kubectl cluster-info --context kind-m06-u1-disposable
kubectl create namespace packaging-lab --context kind-m06-u1-disposable
```

Before every mutating command, verify the context is `kind-m06-u1-disposable` and namespace is `packaging-lab`. Use a manifest with a real locally available image for rollout testing; the placeholder in Section 5.4 is not runnable. Then, using explicit context/namespace arguments:

```bash
kubectl apply --context kind-m06-u1-disposable -n packaging-lab \
  --dry-run=server -f manifests/
kubectl diff --context kind-m06-u1-disposable -n packaging-lab \
  -f manifests/ || test "$?" -eq 1
```

The `kubectl diff` shell handling above is illustrative and must be adjusted to the installed version's documented exit behavior so command errors are not accidentally swallowed. Do not use it as a production-ready CI wrapper without a tested exit-code policy. Save the actual output, context, client/server versions, and any error. A server-side dry-run can be rejected by admission/schema; it does not persist objects or prove later runtime success.

**Expected evidence:** current context, cluster identity, dry-run output, and diff output/exit interpretation. **Cleanup:** verify the context and exact cluster name, then run `kind delete cluster --name m06-u1-disposable` only if this lab created it. Do not delete other clusters. **Common failures:** incompatible runtime, context mismatch, missing CRDs, image placeholder, or permissions. **Stretch:** intentionally submit a disposable invalid field and document the difference between client-side and server-side feedback; remove it before any apply.

## 13. Self-check questions

1. **Why not use `create` for every deployment update?** Answer: create is for creating a new object and typically fails if the identity exists; apply is intended for declarative updates. Temptation: both accept YAML, but their lifecycle semantics differ.
2. **Does client dry-run prove a manifest will pass admission?** Answer: no; server-side dry-run is more authoritative for API-server validation/admission when supported. Temptation: client dry-run output looks successful but does not emulate the server.
3. **Why quote a value such as an account code when the contract requires a string?** Answer: explicit quoting avoids reliance on implicit scalar interpretation. Temptation: the value looks numeric, but its meaning may be an identifier, not a number.
4. **Are client-side apply and SSA identical?** Answer: no; SSA tracks managed field ownership and may report ownership conflicts. Temptation: both are called apply, but their merge/ownership models differ.
5. **What should reviewers inspect when a package changes?** Answer: the selected/rendered manifest diff for each environment, plus validation evidence. Temptation: the source template diff is shorter, but may hide generated changes.
6. **Does deleting a manifest file delete the live object?** Answer: not necessarily; ordinary apply does not inherently own cleanup of every removed object. Temptation: source control is mistaken for a reconciler.
7. **Which fields commonly vary by environment, and which need special caution?** Answer: replicas, resources, hostnames, and approved feature flags may vary; selectors and security posture should remain stable unless a reviewed reason exists. Temptation: all configuration is assumed safe to vary.
8. **Why separate CRD installation from custom-resource application?** Answer: the API type must be established and discoverable before the custom resource can be accepted. Temptation: a directory looks like one unit but is not dependency-aware orchestration.
9. **When might Kustomize be preferable to Helm?** Answer: when the object structure is common and differences are naturally expressed as targeted patches, without a need for a distributed configurable chart interface. Temptation: more features are assumed to mean a better fit.
10. **Does a schema pass prove security and runtime health?** Answer: no; it checks a subset of structural/API correctness and does not prove policy, image availability, scheduling, dependencies, or application behavior. Temptation: a green check is mistaken for end-to-end validation.

## 14. Evidence artifacts

Save learner-generated evidence in a lab workspace, for example `evidence/m06-u1/`:

- `versions.txt` — output from `kubectl version --client`, Git, and installed parser/validator versions.
- `environment-manifests/` — the dev/staging/prod manifest tree used in Lab 1.
- `drift-inventory.md` — classification of each difference and owner/rationale.
- `before-after-diff.txt` — representative diff output.
- `scalars.yaml`, `type-output.txt`, and parser version — actual type-coercion experiment evidence.
- `scripts/validate.sh` or an equivalent Makefile — validation workflow.
- `selected-manifests.yaml` and checksum — selected plain-manifest output; later units should save actual Helm/Kustomize rendered output separately.
- `schema-validation.log` — validator output or an explicit note that the validator was unavailable.
- `server-dry-run.log` and `kubectl-diff.log` — optional, only from a safe disposable context; redact sensitive values.
- `rendered-diff-review.md` — checklist, risk classification, reviewer decision, and unresolved questions.
- `learning-note.md` — what failed, what was learned, and which claims remain `[VERIFY]`.

These files do not exist until the learner creates them. Never include real credentials or unredacted secret values in evidence.

## 15. Common interview and design-review questions

### 1. How would you migrate a service fleet from copied YAML to a reusable configuration approach?

I would inventory objects and owners, capture the current rendered baseline for every environment, and classify all differences before selecting a tool. I would pilot one low-risk service, choose plain YAML/Kustomize/Helm based on the real reuse and consumer requirements, and compare generated output against the approved baseline. Every unexplained change—especially selectors, RBAC, image identity, resources, routes, and security fields—would block promotion. I would add validation and a rollback path before migrating additional consumers. The trade-off is migration effort versus lower long-term drift; a new abstraction is not successful if the output becomes harder to understand.

### 2. A rendered diff removes `runAsNonRoot`, reduces replicas, and widens RBAC. What do you do?

Treat it as high risk and stop promotion until each change has an explicit rationale and owner. Compare the previous and proposed renders, inspect the relevant source/template/overlay, and check whether a generator or default changed. Validate the intended Kubernetes schema and security policy, then ask the workload owner to justify capacity and RBAC changes. If accidental, restore the fields and add regression checks; if intentional, document the risk and staged rollout. A small source diff does not reduce the blast radius of the generated result.

### 3. How do you promote configuration between environments?

Prefer the same immutable image digest across environments with a small, documented set of environment-specific values. Capture build provenance and render each environment separately. This preserves artifact identity while acknowledging that configuration can still change behavior. Environment-specific builds may be necessary for some constraints, but require stronger reproducibility evidence because staging no longer tests the exact production artifact. I would review the rendered diff and validate against the target cluster version before promotion.

### 4. A deleted manifest left a live resource. How do you investigate drift and cleanup?

Identify the exact object by kind, namespace, and name; inspect labels, annotations, owner references, events, and source history; and determine whether another package or controller owns it. Compare live object inventory with the approved source set and inspect deployment logs to learn whether cleanup was ever configured. Do not run broad pruning or delete by name without dependency/owner review. Propose a scoped cleanup, obtain approval, execute it through the owning workflow, and add a deletion inventory gate so future removals are explicit.

### 5. How do you validate a package that includes CRDs, and what are the limits?

Validate generated manifests against the target Kubernetes API version and the relevant CRD schemas, then test the CRD and representative custom resources in a disposable cluster. Establish the CRD first, wait until the API is discoverable, and only then submit dependent custom resources. For upgrades, compare schema compatibility and controller expectations; do not assume deleting/reinstalling the CRD is a safe rollback. Static schema checks cannot fully reproduce admission policy, conversion webhooks, controller behavior, storage migration, or production-specific dependencies, so the release plan must state which checks are static and which are live-cluster tests.

## 16. Sources and verification notes

The following official documentation entry points are appropriate starting points. URLs are provided as stable documentation paths where known; confirm the current content for your installed Kubernetes/kubectl version. No claim is made that these pages were consulted live while authoring this document.

| Topic / claim | Source name and URL | Version-sensitive? | What to verify locally |
|---|---|---|---|
| Declarative management and apply | Kubernetes, “Declarative Management of Kubernetes Objects Using Configuration Files”: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/ | Yes | Apply mode, annotation behavior, and examples for the installed client/server. |
| `kubectl create` | Kubernetes kubectl reference: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/ | Yes | Available subcommands and flags. |
| `kubectl replace` | Kubernetes kubectl reference: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_replace/ | Yes | Replacement behavior, resource-version requirements, and flags. |
| `kubectl diff` | Kubernetes kubectl reference: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_diff/ | Yes | Exit status, server interaction, permissions, and flags. |
| `kubectl apply` | Kubernetes kubectl reference: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/ | Yes | Client/server apply modes, dry-run support, and pruning status. |
| Server-side apply / field management | Kubernetes, “Server-Side Apply”: https://kubernetes.io/docs/reference/using-api/server-side-apply/ | Yes | Managed fields, conflicts, force ownership, and server version. |
| Recommended labels | Kubernetes, “Labels and Selectors”: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/ | Low to moderate | Recommended label conventions and selector constraints. |
| ConfigMaps | Kubernetes, “ConfigMaps”: https://kubernetes.io/docs/concepts/configuration/configmap/ | Moderate | Update behavior for environment variables versus mounted volumes. |
| Secrets | Kubernetes, “Secrets”: https://kubernetes.io/docs/concepts/configuration/secret/ | Moderate | Encryption-at-rest and access-control configuration in the target cluster. |
| Immutable ConfigMaps and Secrets | Kubernetes documentation on ConfigMaps and Secrets above | Moderate | Immutable field behavior and operational replacement requirements. |
| Custom resources / CRDs | Kubernetes, “Custom Resources”: https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/ | Yes | CRD establishment, schema, conversion, and deletion lifecycle. |
| API deprecation policy | Kubernetes, “API Deprecation Policy”: https://kubernetes.io/docs/reference/using-api/deprecation-policy/ | Yes | APIs served by the target cluster version and removal schedule. |
| `kubeconform` | Project repository/documentation: https://github.com/yannh/kubeconform | Yes | Installed release flags, schema source, target Kubernetes version, and custom-resource schema support. |

### Source-grounded facts

The command references above are the primary place to verify kubectl behavior. The chapter distinguishes client-side checks, API-server validation, admission, and runtime behavior because they are different stages. The exact available flags, default apply mode, exit-code handling, and pruning behavior must be checked against installed versions.

### Version-sensitive items to verify

- `kubectl diff` exit statuses and how the installed CLI reports errors versus a detected diff.
- Client-side versus server-side apply defaults and managed-field conflict behavior.
- `kubectl apply --prune` syntax, maturity, selectors, and deletion semantics; do not experiment outside a disposable scope.
- Supported API versions, CRD schemas, admission behavior, and dry-run support on the target cluster.
- `kubeconform` flags, schema selection, and custom-resource validation support.
- YAML parser interpretation of unquoted scalar values, especially number-like identifiers.

### Engineering recommendations and assumptions

- `[RECOMMENDATION]` Keep environment-specific variance small and documented; prefer promotion of the same image digest when feasible.
- `[RECOMMENDATION]` Review rendered output and preserve it as a release artifact.
- `[RECOMMENDATION]` Use directory-per-environment only when it fits repository ownership and promotion requirements; it is not universal.
- `[ASSUMPTION]` Example resource requests, limits, replicas, and probe paths are illustrative. Tune them using actual workload measurements and application contracts.
- Placeholder images and digests are deliberately non-runnable. Replace them only with verified local or approved artifacts before a cluster rollout.

### Author’s verification checklist

| Category | Status | Evidence note |
|---|---|---|
| Required headings and progression | Pass | All 16 numbered main sections appear in the required order, with L1–L4 progression. |
| Configuration-management spectrum and trade-offs | Pass | Plain YAML, Kustomize, Helm, and awareness-only programmatic options compared across required axes. |
| Baseline consistent manifests | Pass with placeholder caveat | Namespace, ConfigMap, Deployment, and Service are included; image/digest are intentionally non-runnable placeholders. |
| Three mandatory labs | Pass with local verification required | Drift, scalar typing, and baseline validation labs are specified; an optional disposable-cluster lab is also included. Commands and outputs must be executed locally; no execution is claimed. |
| Cluster safety | Pass with user responsibility | Mutating cluster steps use a named disposable context/cluster and explicit checks; verify before executing. |
| Apply/diff/dry-run distinctions | Pass; version details to verify | Differences and limits are explained; exact exit codes/flags are marked for local documentation verification. |
| YAML typing and parser output | Pass | No fabricated parser output is presented; learners are instructed to record actual local output and parser version. |
| Pruning and orphaned resources | Pass; `[VERIFY]` | Pruning is treated as destructive/version-sensitive; inventory-first cleanup is recommended. |
| CRD ordering and lifecycle | Pass | Ordering, compatibility, and deletion risk are described without claiming directory apply is dependency-aware. |
| SRE and security lenses | Pass | Indicators, an illustrative SLO, runbook, threats, controls, and limitations are included. |
| Evidence, self-check, and interviews | Pass | Evidence paths, 10 self-check questions, and exactly 5 senior-level interview answers are included. |
| Official documentation URLs | Not independently verified live | URLs are known official entry points; verify current pages and installed-version details before relying on them. |
| Actual command execution | Not verified | No lab command is claimed to have been executed as part of authoring. |
