# Helm Charts, Values, and Templates

**Module:** M06 — Helm, Kustomize, and Kubernetes Packaging  
**Unit:** 2 — Helm charts, values, and templates  
**Target file:** `02-helm-charts-values-and-templates.md`  
**Estimated time:** 14–20 hours: 5–6 hours reading, 6–8 hours cluster-free labs, 3–6 hours cluster labs.  
**Prerequisites:** M01–M05, Unit 1, and basic Kubernetes workload manifests.  
**Core tools:** Helm CLI, `kubectl`, shell, local YAML editor; optional `kubeconform`.  
**Awareness:** `helm-diff`, helm-docs-style generation, post-renderers; optional tools are not required.  
**Last reviewed:** Not independently verified.  
**Tool baseline assumed:** No fixed Helm or Kubernetes versions assumed. Record installed versions in `versions.txt` and verify version-sensitive behavior against the documentation for those versions.  
**Cluster needed:** Specified separately for each lab.

> **Core principle:** Helm packages and renders Kubernetes manifests; it does not make them correct, secure, compatible, or safe to deploy. The rendered manifest is the review artifact.

## 1. Why this matters in production

A chart is an interface used by application teams, release automation, and platform operators. A poorly designed chart can turn a simple replica-count change into a risky release because the values are unclear, defaults are unsafe, or a template silently omits a security field. The rendered output may differ from what reviewers assume the template produces. An upgrade can also retain stale values, hit immutable Kubernetes fields, or change a resource in ways that Helm cannot reverse completely.

Helm is valuable when an application has a meaningful set of reusable resources and configuration choices. Its abstraction has a cost: templates add a second language, values become a public API, and debugging requires tracing from input values through template evaluation to rendered YAML and then to live Kubernetes objects. A reliable workflow makes each step observable and validates the final output.

This chapter uses a small FastAPI model-scoring API as the running example. The chart includes a Deployment, Service, ServiceAccount, ConfigMap, and optional HPA, PDB, Ingress, and NetworkPolicy. The example image is a placeholder until replaced with an actual image reference produced by your M01 workflow.

## 2. Learning objectives

By completing this unit, you should be able to:

- **[L1]** Explain the difference between a chart, release, revision, values file, template, and rendered manifest.
- **[L1]** Inspect chart anatomy and use `helm create`, `helm template`, and `helm lint` appropriately.
- **[L1]** Explain chart `version` versus `appVersion` and record the tool versions that affect behavior.
- **[L2]** Use Go-template actions, pipelines, context, conditionals, loops, named templates, and common Sprig/Helm functions without producing malformed YAML.
- **[L2]** Build and render a FastAPI chart with schema-validated values, secure defaults, and optional resources.
- **[L2]** Compare environment renders and distinguish intentional configuration changes from risky drift.
- **[L3]** Design a stable values API and choose an explicit values-reuse strategy for upgrades.
- **[L3]** Diagnose immutable-field failures and explain what rollback cannot undo.
- **[L4]** Establish review gates, compatibility policy, evidence collection, and a safe incident-response workflow for shared charts.

## 3. Prerequisites, versions, and lab environment

Use a disposable workspace and, for live labs, a dedicated `kind` cluster. Do not run mutation commands against a context unless you have checked it. This unit is designed for a laptop with approximately 4 CPU cores, 8 GB RAM, and 30 GB disk. Most work is cluster-free; rendering and linting are cheap compared with running a cluster.

Create a workspace and record versions:

```bash
mkdir -p "$HOME/m06-unit2" && cd "$HOME/m06-unit2"
{
  helm version
  kubectl version --client
  kind version 2>/dev/null || true
  kubectl version 2>/dev/null || true
} > versions.txt
cat versions.txt
```

The output depends on your installation; do not copy example version numbers from tutorials into your evidence. Verify all version-sensitive options against the locally installed Helm help and official documentation. Items marked `[VERSION-SENSITIVE]` or `[VERIFY]` include schema-draft support, release storage configuration, values reset/reuse flags, `--atomic`/`--wait`/`--timeout` interactions, resource adoption, CRD handling, `--history-max`, post-renderer behavior, plugin behavior, and release/object size constraints.

Module boundaries:

- **M01:** image build/publish, digest pinning, non-root image practices.
- **M02:** CI, release automation, SemVer, code review.
- **M03:** workload behavior, probes, HPA/PDB, Pod Security Standards, API deprecations.
- **M04:** Ingress/Gateway, NetworkPolicy, cert-manager and networking.
- **M05:** stateful workloads, storage, operator-managed databases.
- **M06 Unit 1:** plain manifests and the templating problem.
- **M06 Unit 3:** hooks, dependencies, subcharts, migration-job lifecycle.
- **M06 Unit 4:** comprehensive chart tests, linting and versioning strategy.
- **M06 Units 5–8:** Kustomize, tool selection, distribution/signing, operators and CRDs.
- **M07/M08/M09/M12/M16:** IaC, GitOps reconciliation, production secret systems, supply-chain controls, and platform golden paths respectively.

## 4. Concept map and vocabulary

```text
Chart.yaml + templates/ + values.yaml + environment values + capabilities
                         |                 [cluster-free]
                         v
                    Helm rendering
                         |
                         v
                 Rendered Kubernetes YAML -----> save/version as review evidence
                         |                       (redact sensitive data)
                         v
             lint + schema + policy + diff review
                         |                 [mostly cluster-free]
                         v
                 Helm install/upgrade ----------> release metadata
                         |                         [cluster/API server]
                         v
                 Kubernetes API/admission
                         |
                         v
              controllers -> Pods -> application
                         |
                         v
                live state may drift from source
```

| Term | Precise definition | Common misconception |
|---|---|---|
| Chart | Versioned package containing metadata, templates, defaults and optional dependencies. | A chart is not a running application. |
| Release | An installed instance of a chart associated with a release name and namespace/context. | One chart can have only one installation. |
| Revision | A recorded revision of a release as it changes through install/upgrade/rollback. | A revision is the same as the chart version. |
| Values | Configuration inputs used when rendering chart templates. | Values files automatically validate themselves. |
| Template | Source containing Go-template actions that generate manifest text. | A template is itself the Kubernetes object sent to the API server. |
| Rendered manifest | YAML produced by applying values and template evaluation. | Successful rendering proves a live install will work. |
| Chart repository | A distribution endpoint for charts; OCI registries are another supported distribution path. | A local chart directory is a repository. |
| Dependency | Another chart declared or packaged as part of a parent chart. | Dependency ordering solves every runtime dependency. |
| `version` | Chart package version in `Chart.yaml`. | It must equal the application version. |
| `appVersion` | Informational application version metadata. | Helm uses it as the chart package version. |

### Chart anatomy

```text
scoring-api/
├── Chart.yaml             # chart metadata, version, appVersion
├── values.yaml            # documented default configuration
├── values.schema.json     # JSON Schema for values validation
├── .helmignore            # excludes unwanted files from packaging
├── templates/
│   ├── _helpers.tpl       # named templates shared by this chart
│   ├── deployment.yaml    # workload and Pod security settings
│   ├── service.yaml       # stable in-cluster service endpoint
│   ├── serviceaccount.yaml
│   ├── configmap.yaml     # non-secret configuration
│   ├── hpa.yaml           # optional autoscaler
│   ├── pdb.yaml           # optional disruption budget
│   ├── ingress.yaml       # optional; requires an Ingress controller
│   ├── networkpolicy.yaml # optional; requires an enforcing CNI
│   └── NOTES.txt          # post-install usage notes
├── charts/                # packaged dependencies, when used
└── crds/                  # special CRD handling; lifecycle limitations apply
```

Not every chart needs every file. `helm create scoring-api` generates a scaffold, but inspect and simplify it: generated examples may include resources and options your application does not need. A chart with fewer, explicit choices is often easier to review than a scaffold retained wholesale.

`apiVersion: v2` in `Chart.yaml` identifies the modern Helm chart format used by Helm 3 and later; verify compatibility with the installed Helm major version. The chart `version` changes when the package changes. `appVersion` describes the application release and does not control chart package versioning. `.Values` exposes supplied configuration; `.Release` describes the release name, namespace and related release metadata; `.Chart` exposes chart metadata; `.Capabilities` describes Kubernetes/API capabilities known to the render; `.Template` provides template-file context. Exact fields and behavior should be checked against the installed Helm documentation.

## 5. Level 1 — Beginner: Helm and chart anatomy

### 5.1 Helm's responsibilities and limits

Helm combines three roles: package manager, template renderer, and release manager. It packages related Kubernetes objects, substitutes values into templates, and tracks release history for install/upgrade operations. Kubernetes controllers still reconcile desired objects; Helm does not replace the Deployment controller, validate application business logic, or guarantee zero downtime.

A successful `helm template` means Helm generated output. It does not contact the API server by default, prove that the image exists, validate all admission policies, or show that Pods become Ready. `helm lint` checks chart structure and common problems, but is not a complete Kubernetes API, security-policy, or runtime test.

### 5.2 Essential commands

| Command | Purpose | Cluster required? | Does not prove |
|---|---|---:|---|
| `helm create NAME` | Scaffold a chart directory. | No | That generated choices suit your service. |
| `helm template RELEASE ./chart` | Render manifests locally. | No by default | API admission or rollout success. |
| `helm lint ./chart` | Check chart structure and common chart errors. | No | Complete schema, policy, or runtime safety. |
| `helm install RELEASE ./chart` | Install a release. | Yes | Application correctness beyond the configured wait behavior. |
| `helm upgrade RELEASE ./chart` | Update an existing release. | Yes | That external side effects can be rolled back. |
| `helm upgrade --install RELEASE ./chart` | Upgrade if present, otherwise install. | Yes | That the selected values strategy is appropriate. |
| `helm uninstall RELEASE` | Remove a release's managed resources subject to lifecycle details. | Yes | That external data or every hook side effect is removed. |
| `helm list -A` | List releases in accessible namespaces. | Yes | That every release is healthy. |
| `helm status RELEASE -n NS` | Inspect release status and notes. | Yes | That application-level SLOs are met. |
| `helm get manifest RELEASE -n NS` | Inspect the stored release manifest. | Yes | That live objects have not drifted. |
| `helm get values RELEASE -n NS` | Inspect user-supplied values; `--all` behavior should be checked. | Yes | That the values match current chart defaults. |
| `helm history RELEASE -n NS` | Inspect revision history. | Yes | That rollback can reverse database or external changes. |
| `helm rollback RELEASE REV -n NS` | Roll a release back to a prior revision. | Yes | That PVC contents, CRDs, or external effects revert. |

### 5.3 First end-to-end chart

```bash
mkdir -p hello/templates
cat > hello/Chart.yaml <<'YAML'
apiVersion: v2
name: hello
 description: Small demonstration chart
version: 0.1.0
appVersion: "1.0.0"
YAML
```

Correct the accidental leading space before `description` if you copied this exactly; YAML indentation at the root must be consistent. A valid version is:

```yaml
apiVersion: v2
name: hello
description: Small demonstration chart
type: application
version: 0.1.0
appVersion: "1.0.0"
```

```bash
cat > hello/values.yaml <<'YAML'
replicaCount: 1
image:
  repository: example.invalid/hello
  tag: "1.0.0"
service:
  port: 8080
YAML
cat > hello/templates/deployment.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
  labels:
    app.kubernetes.io/name: hello
    app.kubernetes.io/instance: {{ .Release.Name | quote }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/instance: {{ .Release.Name | quote }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: hello
        app.kubernetes.io/instance: {{ .Release.Name | quote }}
    spec:
      containers:
        - name: hello
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
YAML
helm lint hello
helm template demo hello
```

The image domain is intentionally invalid and is suitable only for rendering. Do not install it expecting a Ready workload. The Deployment selector exactly matches the Pod template's `app.kubernetes.io/instance` label; this relationship is essential. A mismatch can leave the Deployment unable to manage the intended Pods.

### 5.4 Values precedence

A useful mental model is chart defaults, then values files in the order supplied, then explicit command-line overrides. The exact supported override mechanisms and type parsing should be verified locally. For example:

```bash
helm template demo ./hello -f values-dev.yaml -f values-local.yaml --set replicaCount=2
```

Where keys conflict, later values files override earlier ones, and command-line `--set` overrides normally take precedence. Shell quoting and YAML parsing can change a value's type; quote strings that are contractually strings. Prefer a checked-in, documented environment values file over a long, opaque production command.

Helm commonly stores release metadata in Kubernetes Secrets by default, but this is `[VERIFY]` for the installed version and configuration. Release records can contain rendered manifests and configuration data; protect them with namespace RBAC and avoid putting secrets into chart values. A Kubernetes Secret's base64 encoding is not encryption.

## 6. Level 2 — Intermediate: Go templates and a complete FastAPI chart

### 6.1 Template language essentials

Helm templates use Go-template actions inside `{{ ... }}`. The dot (`.`) is the current context. `$` preserves the root context. `with` and `range` change dot inside their blocks, which is a common source of confusing references. A pipeline sends the result of one expression to the next function, such as `.Values.name | quote`.

| Function/operator | Purpose and example | Common pitfall |
|---|---|---|
| `{{ ... }}` | Evaluate an action: `{{ .Release.Name }}` | Forgetting that output is text later parsed as YAML. |
| `{{-` / `-}}` | Trim adjacent whitespace/newlines. | Over-trimming can concatenate YAML lines. |
| `|` pipeline | Pass output onward: `value | quote` | Function argument order may surprise newcomers. |
| `default` | Supply fallback: `default 1 .Values.replicaCount` | A legitimate `0`, `false`, or empty value may trigger fallback. |
| `quote` | Emit quoted text: `.Values.feature | quote` | Quoting does not validate semantic meaning. |
| `required` | Fail rendering if value is missing/empty. | Required fields can make optional features awkward. |
| `toYaml` | Serialize an object to YAML. | Incorrect indentation creates invalid manifests. |
| `nindent` / `indent` | Add indentation; `nindent` also begins with newline. | Using the wrong indentation level breaks nested structures. |
| `include` | Render a named template and return text; can be piped. | Helper output still needs correct YAML placement. |
| `template` | Execute a named template directly. | Unlike `include`, it cannot be piped as a returned string in the same way. |
| `with` | Set dot to a non-empty value in a block. | Root `.Values` paths may stop working; use `$`. |
| `range` | Iterate over a list/map. | Map ordering or context assumptions can affect output; do not rely on accidental order. |
| `if` / `else` | Conditional output. | Large conditional forests become hard to review. |
| `eq`, `and`, `or`, `not` | Boolean/logical comparisons. | Do not confuse template truthiness with application-level validation. |
| `printf` | Format strings, e.g. `printf "%s-%s" .Release.Name .Chart.Name` | Names may exceed Kubernetes length limits. |
| `tpl` | Evaluate a string as template source. | Untrusted values can cause unexpected evaluation. |
| `lookup` | Query a Kubernetes object when connected and supported. | Local renders commonly lack live cluster results; output becomes environment-dependent. |
| `lower`, `trunc`, `trimSuffix` | Normalize names: `... | lower | trunc 63 | trimSuffix "-"` | Truncation can create collisions. |
| `b64enc` | Base64-encode text. | Encoding is not encryption. |
| `sha256sum` | Hash text, e.g. ConfigMap render for rollout checksum. | Never hash or expose secret values casually. |
| `fail` | Stop rendering with an error. | Error conditions need clear messages and tests. |

Whitespace control is lexical: `{{-` trims whitespace before the action and `-}}` trims whitespace after it. It is not a YAML-aware formatter. Always inspect the final YAML. `toYaml` plus `nindent` is common for nested structured values:

```yaml
resources:
  {{- toYaml .Values.resources | nindent 2 }}
```

The precise indentation depends on the surrounding YAML; do not copy this fragment without checking its context. `include` is usually preferable for labels because its output can be piped through `nindent`. `tpl` should only evaluate trusted template content. `lookup` can make a render depend on live cluster state, harming reproducibility and reviewability; verify exact server-rendering options and behavior for your Helm version. Avoid random functions for persistent credentials: a new render can rotate a password on upgrade and break clients.

### 6.2 Complete chart file tree

The following files form a compact example chart. The image repository defaults to an obvious placeholder; replace it with your own image and preferably a real digest from M01 before deployment. Resource sizing is illustrative, not universal production sizing.

```text
scoring-api/
├── Chart.yaml
├── values.yaml
├── values.schema.json
├── .helmignore
├── values-dev.yaml
├── values-staging.yaml
├── values-prod.yaml
└── templates/
    ├── _helpers.tpl
    ├── deployment.yaml
    ├── service.yaml
    ├── serviceaccount.yaml
    ├── configmap.yaml
    ├── hpa.yaml
    ├── pdb.yaml
    ├── ingress.yaml
    ├── networkpolicy.yaml
    └── NOTES.txt
```

#### `Chart.yaml`

```yaml
apiVersion: v2
name: scoring-api
description: FastAPI model-scoring service chart
type: application
version: 0.1.0
appVersion: "1.0.0"
```

#### `values.yaml`

```yaml
replicaCount: 2
nameOverride: ""
fullnameOverride: ""
image:
  repository: example.invalid/scoring-api
  tag: "1.0.0"
  digest: ""
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 8000
containerPort: 8000
serviceAccount:
  create: true
  name: ""
config:
  logLevel: INFO
  modelName: baseline
  featureFlag: "false"
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
probes:
  path: /health
  startup:
    enabled: true
  readiness:
    enabled: true
  liveness:
    enabled: true
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  fsGroup: 10001
  readOnlyRootFilesystem: true
hpa:
  enabled: false
  minReplicas: 2
  maxReplicas: 5
  targetCPUUtilizationPercentage: 75
pdb:
  enabled: false
  minAvailable: 1
ingress:
  enabled: false
  className: ""
  host: scoring.example.invalid
  path: /
networkPolicy:
  enabled: false
  ingressFromNamespaceLabels: {}
```

#### `values.schema.json`

This schema intentionally validates key types and selected constraints. JSON Schema draft support varies; verify the installed Helm version's support. Expand the schema when the public values API grows.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["replicaCount", "image", "service", "containerPort", "resources", "securityContext"],
  "properties": {
    "replicaCount": {"type": "integer", "minimum": 1},
    "nameOverride": {"type": "string"},
    "fullnameOverride": {"type": "string"},
    "image": {
      "type": "object", "required": ["repository", "tag", "digest", "pullPolicy"],
      "properties": {
        "repository": {"type": "string", "minLength": 1},
        "tag": {"type": "string"},
        "digest": {"type": "string", "pattern": "^$|^sha256:[a-f0-9]{64}$"},
        "pullPolicy": {"type": "string", "enum": ["Always", "IfNotPresent", "Never"]}
      },
      "additionalProperties": false
    },
    "service": {
      "type": "object", "required": ["type", "port"],
      "properties": {
        "type": {"type": "string", "enum": ["ClusterIP", "NodePort", "LoadBalancer"]},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535}
      }, "additionalProperties": false
    },
    "containerPort": {"type": "integer", "minimum": 1, "maximum": 65535},
    "serviceAccount": {"type": "object", "properties": {"create": {"type": "boolean"}, "name": {"type": "string"}}, "additionalProperties": false},
    "config": {"type": "object", "properties": {"logLevel": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]}, "modelName": {"type": "string", "minLength": 1}, "featureFlag": {"type": "string", "enum": ["true", "false"]}}, "additionalProperties": false},
    "resources": {"type": "object", "required": ["requests", "limits"], "properties": {"requests": {"$ref": "#/definitions/resourceValues"}, "limits": {"$ref": "#/definitions/resourceValues"}}, "additionalProperties": false},
    "probes": {"type": "object", "properties": {"path": {"type": "string", "minLength": 1}, "startup": {"type": "object", "properties": {"enabled": {"type": "boolean"}}, "additionalProperties": false}, "readiness": {"type": "object", "properties": {"enabled": {"type": "boolean"}}, "additionalProperties": false}, "liveness": {"type": "object", "properties": {"enabled": {"type": "boolean"}}, "additionalProperties": false}}, "additionalProperties": false},
    "securityContext": {"type": "object", "required": ["runAsNonRoot", "runAsUser", "runAsGroup", "fsGroup", "readOnlyRootFilesystem"], "properties": {"runAsNonRoot": {"type": "boolean", "const": true}, "runAsUser": {"type": "integer", "minimum": 1}, "runAsGroup": {"type": "integer", "minimum": 1}, "fsGroup": {"type": "integer", "minimum": 1}, "readOnlyRootFilesystem": {"type": "boolean"}}, "additionalProperties": false},
    "hpa": {"type": "object", "properties": {"enabled": {"type": "boolean"}, "minReplicas": {"type": "integer", "minimum": 1}, "maxReplicas": {"type": "integer", "minimum": 1}, "targetCPUUtilizationPercentage": {"type": "integer", "minimum": 1, "maximum": 100}}, "additionalProperties": false},
    "pdb": {"type": "object", "properties": {"enabled": {"type": "boolean"}, "minAvailable": {"type": "integer", "minimum": 0}}, "additionalProperties": false},
    "ingress": {"type": "object", "properties": {"enabled": {"type": "boolean"}, "className": {"type": "string"}, "host": {"type": "string"}, "path": {"type": "string"}}, "additionalProperties": false},
    "networkPolicy": {"type": "object", "properties": {"enabled": {"type": "boolean"}, "ingressFromNamespaceLabels": {"type": "object", "additionalProperties": {"type": "string"}}}, "additionalProperties": false}
  },
  "definitions": {
    "resourceValues": {"type": "object", "required": ["cpu", "memory"], "properties": {"cpu": {"type": "string", "minLength": 1}, "memory": {"type": "string", "minLength": 1}}, "additionalProperties": false}
  },
  "additionalProperties": false
}
```

#### `.helmignore`

```text
.git/
.gitignore
*.swp
*.tmp
.DS_Store
versions.txt
lab-evidence/
```

#### `templates/_helpers.tpl`

```gotemplate
{{- define "scoring-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "scoring-api.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "scoring-api.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "scoring-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "scoring-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "scoring-api.labels" -}}
{{ include "scoring-api.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end -}}

{{- define "scoring-api.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "scoring-api.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}
```

Selector labels are deliberately minimal and stable. Do not add chart version or application version to selectors: a chart upgrade could change a Deployment selector, which is immutable for an existing Deployment. Descriptive labels can change more freely, but still deserve diff review. Helper names should be chart-prefixed to reduce collisions when templates from dependencies share a rendering context.

#### `templates/serviceaccount.yaml`

```gotemplate
{{- if .Values.serviceAccount.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "scoring-api.serviceAccountName" . }}
  labels:
    {{- include "scoring-api.labels" . | nindent 4 }}
automountServiceAccountToken: false
{{- end }}
```

#### `templates/configmap.yaml`

```gotemplate
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "scoring-api.fullname" . }}-config
  labels:
    {{- include "scoring-api.labels" . | nindent 4 }}
data:
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
  MODEL_NAME: {{ .Values.config.modelName | quote }}
  FEATURE_FLAG: {{ .Values.config.featureFlag | quote }}
```

#### `templates/deployment.yaml`

```gotemplate
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "scoring-api.fullname" . }}
  labels:
    {{- include "scoring-api.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "scoring-api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "scoring-api.selectorLabels" . | nindent 8 }}
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    spec:
      serviceAccountName: {{ include "scoring-api.serviceAccountName" . }}
      securityContext:
        runAsNonRoot: {{ .Values.securityContext.runAsNonRoot }}
        runAsUser: {{ .Values.securityContext.runAsUser }}
        runAsGroup: {{ .Values.securityContext.runAsGroup }}
        fsGroup: {{ .Values.securityContext.fsGroup }}
      containers:
        - name: scoring-api
          image: {{ if .Values.image.digest }}{{ printf "%s@%s" .Values.image.repository .Values.image.digest | quote }}{{ else }}{{ printf "%s:%s" .Values.image.repository .Values.image.tag | quote }}{{ end }}
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.containerPort }}
              protocol: TCP
          envFrom:
            - configMapRef:
                name: {{ include "scoring-api.fullname" . }}-config
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: {{ .Values.securityContext.readOnlyRootFilesystem }}
            capabilities:
              drop: ["ALL"]
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- if .Values.probes.startup.enabled }}
          startupProbe:
            httpGet:
              path: {{ .Values.probes.path | quote }}
              port: http
            periodSeconds: 5
            failureThreshold: 30
          {{- end }}
          {{- if .Values.probes.readiness.enabled }}
          readinessProbe:
            httpGet:
              path: {{ .Values.probes.path | quote }}
              port: http
            periodSeconds: 5
            failureThreshold: 3
          {{- end }}
          {{- if .Values.probes.liveness.enabled }}
          livenessProbe:
            httpGet:
              path: {{ .Values.probes.path | quote }}
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            failureThreshold: 3
          {{- end }}
```

The checksum annotation changes when rendered ConfigMap content changes and causes a Pod-template change, prompting a Deployment rollout. This is a common pattern; verify the exact hashing expression in your chart and do not include secret material in annotations. The application image must implement the configured `/health` endpoint and tolerate a read-only filesystem; otherwise adjust the image/runtime contract rather than weakening security silently.

#### `templates/service.yaml`

```gotemplate
apiVersion: v1
kind: Service
metadata:
  name: {{ include "scoring-api.fullname" . }}
  labels:
    {{- include "scoring-api.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
  selector:
    {{- include "scoring-api.selectorLabels" . | nindent 4 }}
```

#### `templates/hpa.yaml`

```gotemplate
{{- if .Values.hpa.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "scoring-api.fullname" . }}
  labels:
    {{- include "scoring-api.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "scoring-api.fullname" . }}
  minReplicas: {{ .Values.hpa.minReplicas }}
  maxReplicas: {{ .Values.hpa.maxReplicas }}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.hpa.targetCPUUtilizationPercentage }}
{{- end }}
```

HPA requires metrics support and appropriate CPU requests for utilization calculations. Verify `autoscaling/v2` against the target Kubernetes version. Do not set a fixed Deployment replica count through competing mechanisms without understanding HPA ownership.

#### `templates/pdb.yaml`

```gotemplate
{{- if .Values.pdb.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "scoring-api.fullname" . }}
  labels:
    {{- include "scoring-api.labels" . | nindent 4 }}
spec:
  minAvailable: {{ .Values.pdb.minAvailable }}
  selector:
    matchLabels:
      {{- include "scoring-api.selectorLabels" . | nindent 6 }}
{{- end }}
```

A PDB constrains certain voluntary disruptions; it does not guarantee application availability, prevent involuntary failures, or make an unsafe rollout safe. Ensure the selector matches the workload Pods.

#### `templates/ingress.yaml`

```gotemplate
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "scoring-api.fullname" . }}
  labels:
    {{- include "scoring-api.labels" . | nindent 4 }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className | quote }}
  {{- end }}
  rules:
    - host: {{ .Values.ingress.host | quote }}
      http:
        paths:
          - path: {{ .Values.ingress.path | quote }}
            pathType: Prefix
            backend:
              service:
                name: {{ include "scoring-api.fullname" . }}
                port:
                  number: {{ .Values.service.port }}
{{- end }}
```

Ingress is disabled by default. Enabling it requires an installed, compatible Ingress controller and appropriate DNS/TLS configuration. Verify the API version and controller-specific behavior in the target cluster.

#### `templates/networkpolicy.yaml`

```gotemplate
{{- if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "scoring-api.fullname" . }}
  labels:
    {{- include "scoring-api.labels" . | nindent 4 }}
spec:
  podSelector:
    matchLabels:
      {{- include "scoring-api.selectorLabels" . | nindent 6 }}
  policyTypes: ["Ingress"]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              {{- toYaml .Values.networkPolicy.ingressFromNamespaceLabels | nindent 14 }}
      ports:
        - protocol: TCP
          port: {{ .Values.containerPort }}
{{- end }}
```

An empty namespace-selector map matches all namespaces, so this example should be configured deliberately before enabling it. NetworkPolicy enforcement depends on the cluster's CNI implementation. A policy object can exist without providing the expected enforcement on a non-supporting network plugin. Validate the intended source namespace labels and ingress flows before enabling it.

#### `templates/NOTES.txt`

```text
Release: {{ .Release.Name }}
Namespace: {{ .Release.Namespace }}
Service: {{ include "scoring-api.fullname" . }}
Internal port: {{ .Values.service.port }}
{{- if .Values.ingress.enabled }}
Ingress host: {{ .Values.ingress.host }}
{{- else }}
Ingress is disabled. Use an approved internal access method or enable it after reviewing controller and DNS prerequisites.
{{- end }}
```

#### Environment values files

`values-dev.yaml`:

```yaml
replicaCount: 1
image:
  repository: example.invalid/scoring-api
  tag: "dev-placeholder"
  digest: ""
config:
  logLevel: DEBUG
  modelName: baseline
  featureFlag: "true"
resources:
  requests: {cpu: 100m, memory: 128Mi}
  limits: {cpu: 300m, memory: 256Mi}
```

`values-staging.yaml`:

```yaml
replicaCount: 2
image:
  repository: example.invalid/scoring-api
  tag: "staging-placeholder"
  digest: ""
config:
  logLevel: INFO
  modelName: candidate
  featureFlag: "false"
resources:
  requests: {cpu: 200m, memory: 256Mi}
  limits: {cpu: 500m, memory: 512Mi}
```

`values-prod.yaml`:

```yaml
replicaCount: 3
image:
  repository: registry.example.invalid/platform/scoring-api
  tag: "release-placeholder"
  digest: ""
config:
  logLevel: INFO
  modelName: approved
  featureFlag: "false"
resources:
  requests: {cpu: 300m, memory: 384Mi}
  limits: {cpu: "1", memory: 768Mi}
```

These are illustrative, non-runnable image references. Before production, substitute the exact immutable digest of the promoted image. The chart supports a digest by using `repository@sha256:...` when `image.digest` is non-empty; otherwise it uses `repository:tag`. A digest takes precedence. Schema validation checks digest format, but the chart does not verify that the referenced image exists or that it came from a trusted build.

### 6.3 Render and inspect the chart

From the directory containing `scoring-api/`:

```bash
helm lint ./scoring-api
helm template scoring-dev ./scoring-api -f ./scoring-api/values-dev.yaml > rendered-dev.yaml
helm template scoring-staging ./scoring-api -f ./scoring-api/values-staging.yaml > rendered-staging.yaml
helm template scoring-prod ./scoring-api -f ./scoring-api/values-prod.yaml > rendered-prod.yaml
```

All commands above are cluster-free. Inspect important fields instead of assuming the source template tells the full story:

```bash
grep -nE 'kind:|image:|replicas:|runAsNonRoot:|allowPrivilegeEscalation:|resources:|checksum/config:|host:' rendered-prod.yaml
diff -u rendered-staging.yaml rendered-prod.yaml || true
```

If `kubeconform` is installed, validate against a target Kubernetes version and ensure the schemas match the cluster you intend to support. Do not interpret a successful static validation as proof of installed CRDs, admission policy, network enforcement, image availability, or runtime health. `helm lint` may produce warnings that require review; a warning is neither automatically harmless nor automatically a release blocker.

### 6.4 Values schema and API design

A chart's values are a public interface. Document every key, use predictable names, validate types and allowed values, and choose defaults that are safe when a consumer supplies no override. A typo can be silently unused if no schema or template references the key. Schema validation catches many type and structure errors, but cannot fully express every cross-field or cluster-dependent constraint. Use explicit template-time checks for important relationships that schema cannot express cleanly, and test them.

| Poor design | Risk | Improved design | Validation |
|---|---|---|---|
| `enableIngress`, `useIngress`, `ingressOn` all coexist | Conflicting controls | One documented `ingress.enabled` boolean | Schema enum/type and render tests |
| Many undocumented raw YAML escape hatches | Hard-to-predict API and security gaps | Add only justified extension points | Review rendered diff and policy checks |
| `image.tag: latest` by default | Mutable, hard-to-reproduce release | Require explicit tag or digest; production policy prefers digest | CI checks rendered image refs |
| Selector labels include chart version | Upgrade can hit immutable selector error | Stable minimal selector helper | Compare selector fields between revisions |
| Secret placed in values file | Git/history/render/release record exposure | Integrate M09 secret workflow | Secret scanning and release access review |
| `tpl` applied to arbitrary input | Unexpected evaluation and injection risk | Avoid or restrict to trusted chart-owned strings | Review source and test untrusted-input handling |

A flat structure is easy for small charts; nested structures group related options but can become deeply nested. Avoid boolean explosion: if several toggles encode mutually exclusive modes, model the choice as a validated enum instead. Do not make a chart configurable for every hypothetical consumer at the expense of a clear contract.

## 7. Level 3 — Advanced: stable values APIs, upgrade safety, and failure recovery

### 7.1 Upgrade behavior and stale values

During an upgrade, Helm compares the previous release information with the newly rendered manifests and the cluster's live state. The exact internal patch and merge mechanics are implementation- and version-dependent `[VERSION-SENSITIVE][VERIFY]`; do not describe Helm upgrades as identical to Kubernetes server-side apply. Out-of-band changes can interact with the upgrade in surprising ways. Inspect the diff and live object when the result differs from expectation.

Values strategies matter:

- `--reset-values`: start from the new chart's defaults and the values explicitly supplied for this upgrade, where supported.
- `--reuse-values`: reuse prior release values, which can retain a stale image tag or deprecated setting.
- `--reset-then-reuse-values`: where available, reset to new defaults then merge prior values and new overrides according to the installed version's rules.

The availability and precedence of these flags must be checked with `helm upgrade --help` and the matching official docs. Choose a strategy explicitly; do not rely on a team's memory of previous commands. Example: release revision 3 was installed with `image.tag=2026.04.1`; the chart default later changes to `2026.05.0`, but an upgrade with reused values can continue to render `2026.04.1`. Check `helm get values`, render the intended inputs, and inspect `helm get manifest` before proceeding.

### 7.2 Rollback and failed-release triage

Rollback normally records a new release revision pointing back to a prior chart/manifest configuration. It does not reverse database migrations, external API calls, data written to PVCs, all CRD changes, or arbitrary hook side effects. A successful rollback command is not proof that the service recovered; check Pods, events, endpoints, application health, and SLO indicators.

For a release reported as `pending-install`, `pending-upgrade`, `failed`, or `superseded`, treat the exact state and recovery behavior as version/context-sensitive. First gather evidence:

```bash
kubectl config current-context
helm status scoring-api -n scoring
helm history scoring-api -n scoring
helm get values scoring-api -n scoring --all
helm get manifest scoring-api -n scoring
kubectl get events -n scoring --sort-by=.lastTimestamp
kubectl get deploy,pods,rs,svc -n scoring -o wide
```

Do not delete Helm release Secrets as a first-line fix. Determine whether CI was interrupted, admission rejected an object, an immutable field changed, an image cannot be pulled, or a Pod never became Ready. If a rollback is appropriate, record the target revision and inspect its manifests first. Use `--atomic`, `--wait`, and `--timeout` only after verifying their precise semantics for the installed version. Atomic behavior does not undo external effects.

### 7.3 Upgrade-safety classification

| Change | Risk class | Expected symptom | Verification and mitigation |
|---|---|---|---|
| Change a ConfigMap value | Usually reviewable | Pods may not restart without a Pod-template change | Check checksum annotation; verify rollout and application reload behavior. |
| Change image digest | High-impact but intended | New image starts; pull or readiness failure possible | Rendered diff, image provenance, staged rollout and health checks. |
| Change Deployment selector | Immutable-field risk | API rejects update | Keep selectors stable; use a planned replacement/cutover if identity truly must change. |
| Change StatefulSet `volumeClaimTemplates` | High/immutable lifecycle risk | Update rejected or storage migration required | Plan migration and backup; verify target API behavior. |
| Change Service `clusterIP` | Immutable-field risk where applicable | API rejects update | Preserve identity or explicitly plan replacement and endpoint impact. |
| Change Job Pod template | Commonly immutable | Upgrade fails | Use a deliberate new Job identity or lifecycle strategy; hooks are covered in Unit 3. |
| Remove a resource from templates | Potential deletion | Managed resource may be removed during upgrade | Inspect rendered diff and resource ownership; verify data and dependency impact. |
| Weaken security context | Security regression | Workload gains privileges or violates policy | Policy gate and security review of rendered Pod spec. |
| Widen RBAC | Security regression | Service account gains excess permissions | Compare verbs/resources; test least-privilege requirements. |
| Change probe path | Availability risk | Pods remain unready or restart | Confirm app endpoint and run a staged health test. |
| Change storage class/PVC settings | Data/availability risk | Provisioning failure or unsupported mutation | Validate storage lifecycle; do not assume rollback restores data. |

### 7.4 API compatibility, library charts, and extension points

Treat a chart like a versioned API. Renaming a values key can break downstream consumers even if the generated resource still exists. For a migration, document the replacement key, provide a deprecation window, test both paths if needed, emit a useful warning or fail clearly, and remove the old key only in a declared breaking release. `helm-docs`-style generation is optional `[VERIFY]`; generated docs still need review.

A library chart (`type: library`) can share named helpers across charts. It adds dependency and compatibility overhead and is not necessary for every small chart. Avoid giant nested `if` forests, logic that belongs in application code or release automation, and `extraObjects` values that accept arbitrary raw YAML without review. `extraEnv` can be useful as a narrow extension point, but document its schema and precedence. Avoid random generated secrets in templates. A `lookup`-based retention pattern is not universally safe and should only be used after validating the installed version, rendering path, permissions, and lifecycle requirements.

Resource ownership/adoption is a high-risk operation. Helm uses release metadata and ownership checks, but exact adoption behavior and any `--take-ownership` option are `[VERSION-SENSITIVE][VERIFY]`. Do not casually adopt resources that another release or controller owns. Inventory the object, verify owner labels/annotations and current management process, and rehearse in a disposable namespace. `--post-renderer` is awareness-only here: it executes an external program, so its binary, configuration, output and supply-chain trust become part of the deployment path.

Helm's `crds/` handling has lifecycle limitations and differs from normal templated resources; verify install, upgrade and delete semantics for your Helm version. A separate CRD lifecycle or controlled pipeline may be appropriate. Do not assume chart rollback restores CRD schemas or custom-resource data. Release history limits such as `--history-max`, `helm get hooks`, `helm get notes`, and `helm get all` should be checked with local help. Do not repeat a universal “chart size limit” without distinguishing Kubernetes object limits from Helm release storage/serialization constraints `[VERIFY]`.

### 7.5 Incident analyses

| Symptom | Hypotheses and evidence | Root cause pattern | Mitigation | Prevention/regression test |
|---|---|---|---|---|
| Production retained old image | Compare `helm get values`, intended values files, and `helm get manifest` | `--reuse-values` retained an old override | Render explicit intended values and upgrade with chosen reset/reuse strategy | CI asserts expected image digest in every environment render |
| Upgrade fails on immutable selector | Inspect API error and compare old/new Deployment selectors | Selector included changing metadata | Restore stable selector or plan controlled replacement | CI diff check rejects selector changes without approved migration |
| Resource unexpectedly removed/altered | Compare prior/current `helm get manifest`, chart versions and live object | Template conditional or rename changed resource identity | Restore intended manifest or recover through documented recreation | Rendered diff flags removed resources; destructive changes require approval |
| Release stuck `pending-upgrade` after CI interruption | `helm status/history`, events, pipeline logs and live resources | Interrupted release operation or unresolved failure | Identify actual live state; follow version-appropriate recovery and avoid deleting release metadata first | Serialized deployment pipeline and timeout/interrupt handling tests |
| Random secret breaks DB auth | Compare rendered values across revisions; inspect app/database auth symptoms without exposing secrets | Random value regenerated on each render | Restore credential through approved secret process; coordinate rotation | No random persistent credentials in chart; test repeated renders for determinism |
| Values typo/type passed unnoticed | Compare values schema, supplied file and rendered manifest | Unknown key or incorrect YAML scalar type | Correct input and re-render | Schema rejects unknown keys; tests include strings such as `"0123"` and `"true"` |
| CRD/API incompatibility blocks release | Inspect API discovery, CRD establishment, events and target version schemas | Wrong ordering, incompatible schema or removed API | Stop rollout; coordinate CRD lifecycle and compatible custom resources | Test against supported Kubernetes versions and installed CRDs |

A good investigation separates a chart defect from API/admission rejection, image pull failure, readiness failure, CNI behavior, and external dependency failure. Render the exact release inputs first, then inspect the API error and live state. Do not infer root cause from a generic `helm upgrade failed` message alone.

## 8. Level 4 — Expert: chart governance and operating at scale

A senior review should ask whether the values API is minimal and documented, defaults are safe, rendering is deterministic, selectors are stable, schemas are strict enough, the chart has an owner, compatibility is stated, and every supported environment has a rendered artifact. Review the diff as a resource change set: additions, removals, image changes, replica reductions, changed probes, changed security context, widened RBAC, storage changes and selector changes deserve explicit attention.

### CI gate sequence

1. Record tool versions and supported Kubernetes API versions.
2. Run `helm lint`.
3. Validate values against `values.schema.json` through normal chart rendering/lint behavior and explicit negative tests.
4. Render every supported environment with `helm template`.
5. Validate rendered YAML against the target Kubernetes schema (`kubeconform` or equivalent, with target version and CRD schemas accounted for).
6. Apply rendered-manifest policy checks for required labels, security context, resource requirements, probes, image tag/digest policy, privileged settings, host mounts, and approved API versions.
7. Save and review the rendered diff against the previous approved baseline.
8. Run install/upgrade tests in a disposable cluster; full chart-testing depth is Unit 4.
9. Publish/version/signing workflows belong to Units 4 and 7; do not treat a successful render as publication approval.

### Ownership and fleet impact

A shared helper can affect dozens of charts. Assign code ownership, define supported Helm/Kubernetes ranges, publish change notes, classify breaking changes, and stage rollout to a small set of consumers before fleet-wide adoption. Record who can approve emergency changes and who owns rollback decisions. Git records desired source; it does not prove that every live cluster matches it. Keep audit evidence of chart version, values inputs (without secrets), rendered output, validation results, approval, release revision and observed outcome.

### Decision framework

- **Remain with plain YAML** when the application has few environments and duplication is still understandable and controlled.
- **Adopt Kustomize** when most differences are structural overlays/patches over a common resource base.
- **Adopt Helm** when you need a reusable, parameterized package, a values API, and release lifecycle management.
- **Consider programmatic generation** (Jsonnet/Tanka, CUE, cdk8s, Pulumi) only when concrete type, abstraction, or composition requirements justify the additional toolchain and onboarding cost.

No option is universally best. Compare readability, reuse, type/validation support, learning curve, debugging, diffability, packaging/distribution, and intended consumers. Use the least complex tool that makes the real variation explicit and reviewable.

## 9. SRE lens

| Indicator | Definition | Measurement caveat |
|---|---|---|
| Render/lint/schema pass rate | Passing chart/environment validations divided by total runs | A passing check is not a runtime SLO. |
| Release success rate | Releases meeting a defined success criterion divided by attempted releases | Define success window and include aborted releases consistently. |
| Chart change failure rate | Releases requiring rollback/hotfix or causing defined user impact divided by chart releases | Attribution can be ambiguous when multiple changes ship together. |
| Rollback/mitigation time | Time from incident declaration to verified mitigation | Do not stop the clock when the command returns; verify service behavior. |
| Bad-diff identification time | Time from rendered change availability to correct risk identification | Depends on review complexity and alerting. |
| CI duration | Wall-clock time for render/validation gates | Track queue time separately from execution time. |
| Failed-upgrade count | Count of upgrades failing a defined release gate | Segment by chart, cause and environment. |

Illustrative SLO: “At least 98% of chart release attempts in a rolling 30-day window complete the defined release verification without a packaging-caused rollback.” Numerator: qualifying release attempts that pass rollout and post-release verification without a packaging-caused rollback. Denominator: all attempted chart releases in the window, including failed attempts under a documented rule. This is an example definition, not an industry benchmark; tune it to service risk and account for attribution limits.

**Blast radius:** a shared labels helper accidentally adds chart version to Deployment selectors. One chart may fail in staging, but a shared release used by 40 services can create a fleet-wide upgrade failure. Require rendered diffs across every consumer, immutable-field checks, staged rollout, and an owner-approved rollback plan.

**Runbook:** alert/symptom → inspect context and release status → compare prior/current manifests and values → identify chart/API/image/readiness/external cause → mitigate with a tested rollback or forward fix → verify endpoints and SLOs → record incident and add a regression test.

On an 8 GB laptop, prefer rendering and static validation first. Run only one local cluster when live API behavior is essential, and clean up only the resources owned by the lab.

## 10. Security lens

| Threat | Control | Verification evidence | Residual limitation |
|---|---|---|---|
| Secrets in values, `--set`, release records, rendered files or logs | Keep secrets out of chart inputs; use the M09 secret lifecycle; restrict release metadata access | Secret scanning, command review, RBAC review, sanitized artifacts | Scanners can miss encoded or transformed values. |
| Root/privileged workload defaults | Non-root, no privilege escalation, dropped capabilities, compatible read-only root filesystem | Inspect rendered Pod `securityContext`; policy checks | Image may require writable paths or unsupported settings. |
| Mutable image tags | Prefer digest-pinned promoted artifacts and provenance checks | Rendered image reference and build evidence | Digest alone does not establish trusted provenance. |
| Unsafe `tpl` | Do not evaluate untrusted values as template code | Template review and adversarial test cases | Trusted source can still be misconfigured. |
| `lookup`/nondeterministic rendering | Prefer deterministic inputs; document any live lookup | Repeat render and compare output | Cluster capability differences can still matter. |
| Random secret regeneration | Keep persistent credentials in managed secret lifecycle, not random template output | Repeat-render diff and upgrade test | Rotation still requires coordinated application/database changes. |
| Untrusted dependencies/plugins/post-renderers | Pin and review artifacts, limit execution, verify provenance | Dependency inventory and CI review | Unit 7/M12 expands artifact controls. |
| Mutable selectors | Keep selectors minimal and stable | Compare rendered selector fields between releases | Resource identity changes still require migration planning. |
| Overly broad NetworkPolicy/RBAC | Least privilege and explicit flow requirements | Rendered policy review and connectivity tests | NetworkPolicy may not be enforced by the CNI. |
| Unsafe rollback assumptions | Document external state and irreversible operations | Rollback drill and recovery notes | Data and external side effects may remain. |
| Wrong target Kubernetes version | Validate against the production target and installed CRDs | Version record and schema validation report | Admission/runtime behavior is not fully simulated. |

Schema validation, linting, and rendered-manifest inspection are complementary controls. None individually proves runtime safety. Base64 is not encryption; never put actual credentials into this chapter's example values, command lines, notes, screenshots, or evidence files.

## 11. Production checklist

- [ ] `Chart.yaml` metadata, `version`, and `appVersion` reviewed.
- [ ] Every public values key is documented and represented in schema where appropriate.
- [ ] `helm lint ./scoring-api` passes; warnings are triaged.
- [ ] All supported environment values files render successfully.
- [ ] Rendered YAML is saved, inspected, and diffed against an approved baseline.
- [ ] Deployment selectors are stable and minimal across revisions.
- [ ] Image reference follows the documented tag/digest policy.
- [ ] Non-root/security-context defaults and resource requests/limits are present in rendered output.
- [ ] Probe paths and ports match the application image contract.
- [ ] HPA metrics prerequisites and PDB limitations are documented.
- [ ] Ingress and NetworkPolicy are disabled by default or intentionally configured and verified.
- [ ] No secrets appear in source, CLI arguments, rendered artifacts, notes, logs, or evidence.
- [ ] Upgrade values reset/reuse strategy is explicit and locally verified.
- [ ] Immutable-field changes have a migration plan and review evidence.
- [ ] CRD lifecycle has an explicit owner and is not assumed to be rolled back automatically.
- [ ] Upgrade and rollback behavior has been tested in a disposable cluster.
- [ ] Version-sensitive flags/defaults are verified against installed versions.
- [ ] Chart owner, compatibility policy, release notes, runbook and rollback authority are documented.

## 12. Hands-on lab set

The labs below are deliberately scoped to a lab workspace. Save the chart from Section 6.2 into `scoring-api/` for Labs 1–5. Do not copy a placeholder image into a production release. Expected outputs are descriptions unless explicitly captured on your own machine; no terminal output is claimed to have been executed here.

### Lab 1 — Build and validate the FastAPI chart

- **Goal:** Create the full chart from Section 6.2 and demonstrate valid rendering for defaults and environment overrides.
- **Success criteria:** `helm lint` completes without unexplained errors; each environment renders; the schema rejects an invalid replica count; rendered selector labels match.
- **Time:** 90–150 minutes.
- **Prerequisites:** Helm, shell, editor.
- **Cluster required:** No.
- **File tree:** `scoring-api/Chart.yaml`, `values.yaml`, `values.schema.json`, `.helmignore`, `values-{dev,staging,prod}.yaml`, and all files under `templates/` shown in Section 6.2. Use the complete contents supplied there; do not omit a required template.
- **Commands:**

```bash
helm version
helm lint ./scoring-api
helm template scoring-dev ./scoring-api > rendered-default.yaml
helm template scoring-dev ./scoring-api -f ./scoring-api/values-dev.yaml > rendered-dev.yaml
helm template scoring-staging ./scoring-api -f ./scoring-api/values-staging.yaml > rendered-staging.yaml
helm template scoring-prod ./scoring-api -f ./scoring-api/values-prod.yaml > rendered-prod.yaml
helm template scoring-prod ./scoring-api --set replicaCount=0
```

The last command should fail schema validation if the installed Helm honors the schema and the chart file is complete. If it does not, inspect `helm lint`, schema support and the error carefully rather than assuming validation happened. If `kubeconform` is installed, run it against the target Kubernetes version on each rendered file.
- **Evidence:** `versions.txt`, lint output, rendered YAML, invalid-input error, and a short note identifying what lint/schema/rendering did and did not validate.
- **Cleanup:** Remove only the lab workspace files when finished.
- **Common failures:** Template indentation errors; schema/template mismatch; missing helper name; incorrect image format. Fix from the first failing command and rerun all renders.
- **Stretch:** Add a schema rule for a new bounded numeric value and a negative test.

### Lab 2 — Compare dev, staging, and production renders

- **Goal:** Explain every meaningful environment difference and catch unintended security regressions.
- **Success criteria:** Save all three renders and produce a diff; document intentional differences in replicas/resources/model feature flags; verify security context and selectors remain consistent.
- **Time:** 45–75 minutes.
- **Prerequisites:** Lab 1.
- **Cluster required:** No.
- **File tree:** `scoring-api/values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml`, plus `lab-evidence/rendered/`.
- **Commands:**

```bash
mkdir -p lab-evidence/rendered
helm template scoring-dev ./scoring-api -f ./scoring-api/values-dev.yaml > lab-evidence/rendered/dev.yaml
helm template scoring-staging ./scoring-api -f ./scoring-api/values-staging.yaml > lab-evidence/rendered/staging.yaml
helm template scoring-prod ./scoring-api -f ./scoring-api/values-prod.yaml > lab-evidence/rendered/prod.yaml
diff -u lab-evidence/rendered/staging.yaml lab-evidence/rendered/prod.yaml > lab-evidence/staging-prod.diff || true
grep -nE 'image:|replicas:|runAsNonRoot:|allowPrivilegeEscalation:|readOnlyRootFilesystem:|requests:|limits:|host:' lab-evidence/rendered/prod.yaml
```

- **Expected evidence:** A non-empty diff for intended differences and a checklist showing whether image reference, replicas, resources, hostname, feature flags, selectors and security settings are expected. Different output is not automatically a defect.
- **What it proves:** Inputs produce the recorded output and the differences were reviewed. It does not prove production admission or runtime readiness.
- **Cleanup:** Delete `lab-evidence/` when the evidence is no longer needed.
- **Common failures:** Wrong values-file path; diff noise caused by release names; production accidentally uses a weaker security setting. Fix the input and regenerate all files.
- **Stretch:** Add a CI script that fails if any environment render contains `:latest` or omits `runAsNonRoot: true`.

### Lab 3 — Install, upgrade, history, and rollback on kind

- **Goal:** Observe release revisions and distinguish chart rollback from data rollback.
- **Success criteria:** Install a release in a disposable cluster, upgrade a non-immutable value, inspect history and manifests, then rollback and verify the revision/history.
- **Time:** 60–120 minutes.
- **Prerequisites:** `kind`, `kubectl`, Helm. For a workload to become Ready, replace the placeholder image with an actual locally available image and follow your established M01 image-loading workflow; otherwise use the release for lifecycle observation and do not expect Ready Pods.
- **Cluster required:** Yes.
- **Safety:** The following creates a uniquely named lab cluster only. Never delete or reuse an existing user cluster. If the name already exists, choose another unique name.
- **Commands:**

```bash
kind create cluster --name m06-u2-lab
kubectl config current-context
kubectl cluster-info
kubectl create namespace m06-u2
helm install scoring-api ./scoring-api -n m06-u2 --set replicaCount=1
helm history scoring-api -n m06-u2
helm upgrade scoring-api ./scoring-api -n m06-u2 --set replicaCount=2
helm status scoring-api -n m06-u2
helm get manifest scoring-api -n m06-u2 > lab-evidence-installed-manifest.yaml
helm get values scoring-api -n m06-u2 > lab-evidence-user-values.yaml
helm history scoring-api -n m06-u2
```

Choose a revision from the displayed history, inspect it, then run `helm rollback scoring-api <REVISION> -n m06-u2` with that actual revision number. Verify `helm history`, `helm status`, and live resources afterward. Do not paste a made-up revision number.
- **Expected evidence:** Context name, history before/after, values, stored manifest, status and post-rollback observations. A successful Helm operation alone does not prove application readiness.
- **Cleanup:** First confirm `kubectl config current-context` is the lab context and verify the cluster name. Then remove only the cluster created by this lab with `kind delete cluster --name m06-u2-lab`.
- **Common failures:** Placeholder image cannot pull; port/health contract mismatch; cluster name collision; wrong context. Do not delete any other cluster to resolve these.
- **Stretch:** Introduce a values change that triggers a rollout via the ConfigMap checksum, and capture rollout status with an actual runnable image.

### Lab 4 — Reproduce the stale `--reuse-values` trap

- **Goal:** Show how an old explicit override can survive a chart default change and document a safe upgrade choice.
- **Success criteria:** Capture old/new defaults, release values and rendered manifest; compare supported reuse/reset strategies using the installed Helm version.
- **Time:** 60–90 minutes.
- **Prerequisites:** Lab 3's disposable cluster and chart workspace.
- **Cluster required:** Yes.
- **Commands:** First inspect the local syntax with `helm upgrade --help`; use only flags supported by the installed version. Install with an explicit override:

```bash
helm install stale-values ./scoring-api -n m06-u2 --set image.tag=old-lab-tag
helm get values stale-values -n m06-u2
helm get manifest stale-values -n m06-u2 | grep -n 'image:'
```

Now edit only the chart's default `image.tag` to `new-chart-default`, lint and render the new chart. Then perform separate experiments with `--reuse-values` and `--reset-values` (and `--reset-then-reuse-values` only if supported). Capture `helm get values` and `helm get manifest` after each experiment; reinstall a clean release or return to a known revision between comparisons so experiments do not contaminate one another.
- **Expected evidence:** A table of the old explicit value, new chart default, selected upgrade flag and resulting image. Exact precedence can depend on Helm version; label the observed behavior with the recorded version.
- **What it proves:** Release values and chart defaults are distinct inputs and the chosen upgrade strategy affects the result. It does not establish a universally correct flag for every release.
- **Cleanup:** Uninstall only `stale-values` in `m06-u2`, then clean the lab cluster after verifying context.
- **Common failures:** Comparing runs with different chart sources; forgetting an old override; unsupported flag. Reset to a clean release and record exact commands.
- **Stretch:** Add a CI assertion that the production render uses an approved image digest.

### Lab 5 — Immutable-field failure and safe remediation

- **Goal:** Demonstrate why selector changes require migration planning.
- **Success criteria:** Render two chart versions with different selector labels, capture the API rejection if it occurs, then correct the chart to preserve stable selectors.
- **Time:** 45–90 minutes.
- **Prerequisites:** Disposable cluster from Lab 3 and working chart.
- **Cluster required:** Yes.
- **Commands:** Save the original selector from `helm get manifest`, then change the selector helper temporarily (for example, add a chart-version label to `selectorLabels`) and run `helm template` to inspect the change. Attempt an upgrade only in the disposable namespace. If the API rejects the immutable selector change, save the actual error; if not executed, any sample error must be labeled illustrative. Restore the stable helper and render again. For a real identity change, plan a second resource name and controlled traffic cutover rather than blindly deleting the old Deployment.
- **Evidence:** Old/new selector diff, actual error if observed, corrected render, and a short migration decision record.
- **Cleanup:** Restore the chart source, uninstall only the lab release and verify the context before deleting the lab cluster.
- **Common failures:** Changing the wrong helper; testing against an existing non-lab release; assuming `--force` is harmless. Stop if context or ownership is uncertain.
- **Stretch:** Add a CI check that fails if the stable selector set changes between the previous approved render and a pull request.

## 13. Self-check questions

1. **Chart vs release:** What is the difference? **Answer:** A chart is the package; a release is an installed instance. **Tempting wrong answer:** “A release is just the chart version”; revisions and release names are separate concepts.
2. **`version` vs `appVersion`:** Which changes when chart templates change? **Answer:** Chart `version`; `appVersion` is application metadata. **Tempting wrong answer:** They always track the same release because applications and charts can be released together.
3. **Values precedence:** If two files set the same key, which usually wins? **Answer:** The later file; explicit command-line overrides normally take precedence. Verify exact mechanisms and quoting. **Tempting wrong answer:** Chart defaults always win because they are packaged.
4. **`include` vs `template`:** Why use `include` for labels? **Answer:** Its rendered string can be piped through functions such as `nindent`. **Tempting wrong answer:** Both have identical output-composition behavior.
5. **`toYaml`/`nindent`:** Why inspect rendered YAML? **Answer:** Indentation and whitespace trimming are textual operations; a template can render malformed YAML. **Tempting wrong answer:** Valid Go-template syntax guarantees valid YAML.
6. **`lookup`:** Why can it reduce reproducibility? **Answer:** It can make output depend on live cluster objects and permissions. **Tempting wrong answer:** Local `helm template` always queries the API server.
7. **Schema limits:** Does `values.schema.json` prove a live deployment will succeed? **Answer:** No; it validates values structure/types, not every Kubernetes policy or runtime behavior. **Tempting wrong answer:** Schema validation replaces API-server validation.
8. **`--reuse-values`:** What is the stale-value trap? **Answer:** A prior explicit override may survive a chart default change. **Tempting wrong answer:** New defaults always replace every old user value.
9. **Immutable selectors:** How should a selector change be handled? **Answer:** Preserve stable selectors or plan a controlled replacement/cutover. **Tempting wrong answer:** A normal upgrade always patches any field.
10. **Rollback:** What cannot reliably be undone? **Answer:** External data changes, database migrations, PVC contents, CRD effects and arbitrary side effects. **Tempting wrong answer:** A successful Helm rollback restores the entire system to its prior state.

## 14. Evidence artifacts

Save these under a local lab workspace, not as an assertion that any repository files have already been modified:

```text
lab-evidence/
├── versions.txt
├── chart-tree.txt
├── helm-lint.txt
├── rendered-default.yaml
├── rendered-dev.yaml
├── rendered-staging.yaml
├── rendered-prod.yaml
├── schema-negative-test.txt
├── rendered-diffs/
│   ├── dev-staging.diff
│   └── staging-prod.diff
├── cluster/
│   ├── context.txt
│   ├── history-before.txt
│   ├── history-after.txt
│   ├── status-after-upgrade.txt
│   ├── installed-manifest.yaml
│   └── rollback-notes.md
├── stale-values/
│   ├── values-before.txt
│   ├── values-after.txt
│   ├── manifest-before.yaml
│   └── strategy-comparison.md
├── immutable-field/
│   ├── selector-diff.txt
│   ├── api-error.txt
│   └── remediation.md
├── chart-api-decision-record.md
└── incident-notes.md
```

Capture only outputs actually produced by your commands. Redact credentials and sensitive internal data. For any test not executed, write “not run” rather than filling the evidence file with invented output.

## 15. Common interview and design-review questions

### 1. How would you design a stable values API for a shared chart?
**Model answer:** Start from real consumer variation, not hypothetical knobs. Give keys consistent names and types, document defaults, validate with `values.schema.json`, and keep selectors/security posture stable unless there is a justified exception. Version the chart independently from the application, publish migration notes for breaking changes, and test representative consumer values. Evidence should include schema-negative tests, rendered manifests for supported environments, and compatibility review. The trade-off is flexibility versus a contract that can be understood and tested.

### 2. What do you review in a rendered diff before production?
**Model answer:** Review additions/removals, names and namespaces, image digests, replica counts, resources, probes, security context, RBAC, selectors, storage, Service ports, NetworkPolicy and API versions. A source-template review alone is insufficient because values and conditionals determine the actual output. Validate against the target Kubernetes version, check policy gates, and understand any noisy generated changes. A clean diff does not prove runtime health, so follow with staged rollout and application verification.

### 3. How do you diagnose stale values or a failed upgrade?
**Model answer:** Record the release state and tool versions, inspect `helm history`, `helm get values`, `helm get manifest`, the exact new render, Kubernetes events and pipeline logs. Determine whether the problem is values precedence, immutable fields, API/admission rejection, image pull, readiness or an external dependency. Do not delete release metadata as a first response. Select an explicit reset/reuse strategy, rehearse rollback or forward-fix options, and add a regression assertion for the observed cause.

### 4. How do you balance secure defaults with usability?
**Model answer:** Use non-root execution, no privilege escalation, dropped capabilities, resource requests/limits and probes where the image contract supports them. Make optional integrations disabled by default and document prerequisites. Provide narrow extension points rather than arbitrary raw YAML for every field. Validate with schema and rendered-policy checks, then test with the real application image. Security defaults must be practical and explicit, but exceptions should be reviewed rather than silently weakening the chart.

### 5. How do you handle rollback, immutable fields and CRDs/data?
**Model answer:** First distinguish chart-managed manifests from external state. Helm rollback can restore a prior release configuration but does not reverse database migrations, PVC data changes, all CRD effects or external side effects. Immutable-field changes require a migration or controlled replacement, not a blind delete. CRDs need a separately owned lifecycle and compatibility testing. Evidence should include revision history, old/new rendered diffs, data/backup assumptions, and a rehearsed recovery procedure.

## 16. Sources and verification notes

The following official documentation areas are the appropriate references. Verify current URLs and the page/version that matches your installed tool; this chapter does not claim live consultation of each page.

| Topic/claim | Official source name and URL | Version-sensitive? | What to verify locally |
|---|---|---:|---|
| Charts and structure | Helm Docs, “Charts”: https://helm.sh/docs/topics/charts/ | Yes | Chart format, fields, dependency and packaging behavior. |
| Chart templates and built-in objects | Helm Docs, “Chart Template Guide”: https://helm.sh/docs/chart_template_guide/ | Yes | Built-in object fields and template context. |
| Template functions and pipelines | Helm Docs, “Template Function List”: https://helm.sh/docs/chart_template_guide/function_list/ | Yes | Function availability and output semantics. |
| Values files | Helm Docs, “Values Files”: https://helm.sh/docs/chart_template_guide/values_files/ | Yes | Merge precedence and CLI override behavior. |
| `helm create`, `template`, `lint` | Helm command reference: https://helm.sh/docs/helm/ | Yes | Installed command flags and output. |
| Install/upgrade/uninstall/status/history/get/rollback | Helm command reference: https://helm.sh/docs/helm/ | Yes | `--wait`, `--atomic`, timeout, reset/reuse and history flags. |
| Release storage | Helm Docs, storage backend/FAQ material: https://helm.sh/docs/ | Yes | Default storage driver and namespace/RBAC behavior. |
| CRDs | Helm Docs, “Custom Resource Definitions”: https://helm.sh/docs/chart_best_practices/custom_resource_definitions/ | Yes | Install/upgrade/delete lifecycle for `crds/`. |
| Kubernetes immutable fields and Deployments | Kubernetes Docs, Deployments: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | Yes | Selector immutability and supported API version. |
| Security contexts | Kubernetes Docs, Security Context: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/ | Yes | Supported fields and policy constraints. |
| Probes | Kubernetes Docs, Liveness/Readiness/Startup Probes: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/ | Yes | Probe semantics and version support. |
| HPA | Kubernetes Docs, Horizontal Pod Autoscaling: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | Yes | Metrics prerequisites and API version. |
| PDB | Kubernetes Docs, Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Yes | Voluntary-disruption behavior and limits. |
| NetworkPolicy | Kubernetes Docs, Network Policies: https://kubernetes.io/docs/concepts/services-networking/network-policies/ | Yes | CNI enforcement and supported policy fields. |
| JSON Schema draft | JSON Schema specifications: https://json-schema.org/specification | Yes | Draft support in the installed Helm release. |

### Source-grounded behavior

The chart format, template model, values-driven rendering, Kubernetes workload concepts, and command families described here are based on the documented Helm/Kubernetes interfaces. Always use documentation matching the installed version when behavior is version-sensitive.

### Version-sensitive items requiring local verification

Verify `apiVersion: v2` compatibility; JSON Schema draft support; `--dry-run=server` and other rendering flags; `--atomic`, `--wait`, and `--timeout`; values reset/reuse flags and precedence; release storage backend; resource adoption and `--take-ownership`; `crds/` lifecycle; plugins; `--history-max`; post-renderers; `helm get` subcommands; and release/object size constraints. Use `helm version`, `helm upgrade --help`, `helm install --help`, `helm get --help`, and the installed-version official docs. For Kubernetes API support, record the target server version and validate the rendered output against it.

### Engineering recommendations and assumptions

Recommendations in this chapter—such as digest-pinned production images, directory-specific environment values, stable selectors, explicit values strategies, rendered-diff gates, and narrow chart APIs—are engineering practices to reduce operational risk, not guarantees that one design suits every organization. Adapt them to service requirements and document exceptions.

## 17. Author's verification checklist

This checklist reports document coverage, not a claim that the example was executed in a real cluster.

- **PASS** — Prescribed main headings are present in the requested order.
- **PASS** — Complete chart file contents are included, including schema, helpers, required templates, and three environment files.
- **PASS** — Template functions/operators are covered with purpose, examples, and pitfalls.
- **PASS** — Upgrade safety, stale values, rollback limits, CRD lifecycle caveats, SRE and security lenses are included.
- **PASS** — Four mandatory labs plus the recommended immutable-field lab include prerequisites, commands, evidence, cleanup and stretch tasks.
- **PASS** — Self-check contains 10 questions; interview section contains exactly 5 questions.
- **PASS** — Version-sensitive claims and non-executed expected behavior are qualified rather than presented as observed output.
- **NOT VERIFIED** — Helm lint/render/schema validation has not been executed in this authoring environment; run the supplied commands with your installed Helm version.
- **NOT VERIFIED** — Live `kind` install/upgrade/rollback and immutable-field behavior have not been executed here; capture only actual local evidence.
- **NOT VERIFIED** — Documentation URLs and current version details have not been live-checked in this document; verify against the installed tool versions before production use.
- **PASS** — Only the target file content is provided; no claim is made that the user's repository was modified.
