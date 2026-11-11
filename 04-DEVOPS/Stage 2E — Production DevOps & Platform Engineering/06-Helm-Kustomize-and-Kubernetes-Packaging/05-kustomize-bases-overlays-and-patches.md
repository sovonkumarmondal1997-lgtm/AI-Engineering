# Kustomize Bases, Overlays, and Patches

**Module:** M06 — Helm, Kustomize, and Kubernetes Packaging  
**Unit:** 5 — Kustomize bases, overlays, and patches  
**Target filename:** `05-kustomize-bases-overlays-and-patches.md`  
**Estimated time:** Reading 3–4 hours; cluster-free labs 3–4 hours; cluster labs 2–3 hours  
**Prerequisites:** Stage 2E M01–M05 and M06 Units 1–4; Kubernetes manifests, Deployments, Services, Jobs, ConfigMaps, Secrets, PVCs, RBAC, NetworkPolicy, Helm render/testing basics  
**Core tools:** `kubectl`, Kustomize (embedded or standalone), Bash, Git, YAML editor  
**Optional tools:** `kind`, `kubeconform`, `yq`, Python with PyYAML, policy tools such as Conftest/OPA  
**Tool baseline:** No versions assumed; capture installed versions before the lab  
**Last reviewed:** Not independently verified

> **Operating principle:** Treat rendered YAML as the evidence artifact. Keep environment variance small and explicit, preserve stable selectors, and validate the final output—not just the source patch.

## 1. Why Kustomize exists

Teams often begin with a directory of Kubernetes YAML files and copy it into `dev`, `staging`, and `prod`. The copies diverge: a security fix reaches two environments but not the third, a port changes in one copy, or production silently loses a NetworkPolicy. This is configuration drift caused by duplicated sources of truth.

Kustomize addresses the composition problem without introducing a general-purpose template language. A **base** is a reusable set of plain Kubernetes resources. An **overlay** composes a base and expresses a limited set of environment-specific changes. The output is rendered Kubernetes YAML that can be reviewed, validated, diffed, and applied.

Helm and Kustomize solve related but different problems. Helm packages templates and values into a versioned chart and provides release-oriented operations such as install and upgrade. Kustomize transforms and composes YAML resources. Kustomize does not by itself act as a release manager, persistent reconciler, or secret manager. A GitOps controller may invoke Kustomize, but controller reconciliation is covered later in M08.

The central design goal is not to eliminate all duplication at any cost. It is to establish a stable common configuration and make justified differences visible. A 2–3-layer overlay structure is a useful heuristic, not a universal limit. If a new overlay requires many patches to undo the base, the base may encode the wrong defaults or the ownership boundaries may be unclear.

This chapter uses a FastAPI scoring API, a worker, and an ETL CronJob as a running example. Where a complete lab fixture is needed, files are defined below rather than pretending to inspect a repository that is not available. Image digests shown as placeholders are not real digests and must not be treated as pullable images.

## 2. Learning objectives

By the end of this unit, you should be able to:

- Explain Kustomize’s template-free composition model and the role of `kustomization.yaml`.
- Build a stable base and shallow `dev`, `staging`, and `prod` overlays.
- Render with embedded and standalone Kustomize while accounting for version differences.
- Use names, namespaces, annotations, image transformations, replica transformations, and safe label practices.
- Choose between strategic-merge and JSON 6902 patches and recognize list/index hazards.
- Use ConfigMap/Secret generators without confusing generation with secret management.
- Explain hash-suffix rollouts, `replacements`, components, remote resources, and transformer configuration.
- Validate rendered output against a target Kubernetes version and review meaningful diffs.
- Diagnose selector immutability failures, wrong patch targets, remote-source drift, and unexpected restarts.
- Govern overlay ownership, CI quality gates, migration, and supply-chain risk.

## 3. Prerequisites, versions, and lab safety

### 3.1 Record versions

Run from the lab workspace:

```bash
mkdir -p "$HOME/m06-kustomize-u5/evidence"
cd "$HOME/m06-kustomize-u5"
{
  date -Is
  kubectl version --client
  if command -v kustomize >/dev/null 2>&1; then kustomize version; else echo "standalone kustomize: not installed"; fi
  if command -v kind >/dev/null 2>&1; then kind version; else echo "kind: not installed"; fi
} > versions.txt 2>&1
cat versions.txt
```

The Kustomize version embedded in `kubectl` may differ from standalone Kustomize. The embedded version is not guaranteed to expose every feature available in a recent standalone release. Check the installed command’s help and documentation matching that version. Determining the embedded version can require checking the kubectl release notes or the Kustomize version mapping; mark the value `[VERIFY]` rather than guessing.

If a disposable cluster is used, append:

```bash
kubectl config current-context
kubectl version
```

Record the server version separately from the client version. Do not assume that the local API schema or Kustomize binary matches the target cluster.

### 3.2 Safety rules

- Never use production contexts, credentials, or production data in these labs.
- Use dummy values only. A secret-like value in a lab must be clearly fake.
- Before any apply/diff/rollout test, verify the exact disposable context.
- Keep generated output in a lab workspace and review it for sensitive data before sharing.
- Pin remote bases to immutable commit identifiers or vendor reviewed content.
- Do not enable untrusted plugins or alpha plugins in privileged CI.
- If a tool is optional and absent, use the stated fallback or stop with a clear message; do not silently skip a required gate.
- Capture evidence before deleting the test cluster.

## 4. Mental model: base, overlay, transformer, rendered output

```text
base resources + overlay resources
              |
              v
     kustomization.yaml
              |
              v
   built-in transformations
 names / namespace / labels / images
 patches / generators / replacements
              |
              v
       rendered YAML
              |
              v
 schema + policy + diff review
              |
              v
   safe apply / cluster validation
```

| Layer | Owns | Should usually avoid |
|---|---|---|
| `base/` | Stable workload structure, selectors, probes, security defaults, Services | Environment-specific hostnames or cluster-specific storage classes |
| `overlays/dev/` | Development replicas/resources, test hostnames, optional debug settings approved by policy | Repeating the entire Deployment |
| `overlays/staging/` | Production-like settings for pre-release validation | Diverging security controls without a documented reason |
| `overlays/prod/` | Production scale, hostname, storage class, strict policy resources | Hidden emergency exceptions without owner/expiry |
| `components/` | Reusable optional bundles such as NetworkPolicy or monitoring | Implicit ownership ambiguity or resources that assume undeclared names |
| Rendered output | Exact resources submitted for validation/review | Secrets or unreviewed generated artifacts |

Kustomize reads `kustomization.yaml`, collects resources, applies configured transformations and patches, and emits YAML. Exact transformation ordering and custom transformer behavior can be version-sensitive; do not rely on an undocumented ordering assumption. The final build is the artifact to inspect.

## 5. Level 1 — Fundamentals and first overlay

### 5.1 The three approaches

**Copied manifests per environment** are easy initially but create repeated sources of truth. Every security fix must be applied and verified in each copy.

**Helm** uses templates and values. It is useful when chart packaging, versioned values contracts, hooks, dependencies, and release lifecycle are needed. Those topics were covered in Units 2–4.

**Kustomize** starts with plain YAML and expresses transformations or patches. It is useful when teams want the manifest structure to remain visible and prefer overlays over a template language. Neither tool is universally better; Unit 6 handles the full decision framework.

### 5.2 Core commands

| Command | Purpose | Important limitation |
|---|---|---|
| `kubectl kustomize overlays/dev` | Render with kubectl’s embedded Kustomize | Feature set follows that embedded version |
| `kubectl apply -k overlays/dev` | Build and apply a Kustomize directory | Mutates the current cluster; context safety is mandatory |
| `kustomize build overlays/dev` | Render with standalone Kustomize | Standalone version may differ from kubectl |
| `kubectl diff -k overlays/dev` | Compare intended configuration with live state, if supported by installed kubectl | Requires cluster access and correct context; exact support is `[VERIFY]` |
| `kubectl version --client` | Capture client version | Does not report the cluster’s server version by itself |

For a cluster-free first pass, use `kubectl kustomize` or `kustomize build`. Do not run `apply` merely to see what a render looks like.

### 5.3 First base and overlays

The complete lab fixture is expanded in Lab 1. Its basic structure is:

```text
kustomize-lab/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── pvc.yaml
├── components/
│   └── network-policy/
│       ├── kustomization.yaml
│       └── network-policy.yaml
└── overlays/
    ├── dev/kustomization.yaml
    ├── staging/kustomization.yaml
    └── prod/kustomization.yaml
```

`resources` lists YAML files or other Kustomize directories. `namespace` sets the namespace for namespaced resources. `namePrefix` and `nameSuffix` alter resource names; Kustomize also rewrites recognized name references, but custom resource fields may need configuration. `commonAnnotations` adds annotations broadly. Modern `labels` configuration can control whether labels are included in selectors; check the installed version before using `includeSelectors: false` `[VERIFY][VERSION-SENSITIVE]`.

The `images` transformer can change image names and tags; digest support depends on the installed Kustomize version and syntax, so verify it. The `replicas` transformer provides a targeted way to set replica counts for supported workload kinds. Prefer these dedicated transformers for their intended purpose over a broad patch that duplicates an entire resource.

### 5.4 Labels and selectors

Labels are key-value metadata used for grouping, selection, policy, and observability. Standard labels such as `app.kubernetes.io/name`, `app.kubernetes.io/instance`, and `app.kubernetes.io/component` make resources easier to query. A Deployment’s `.spec.selector.matchLabels` identifies the Pods it owns, and those labels must match the Pod template labels.

Legacy `commonLabels` can affect selectors as well as object and Pod-template labels. If the resulting selector changes on an existing Deployment, Kubernetes may reject the update because Deployment selectors are immutable. Do not apply `commonLabels` globally without inspecting rendered output. Prefer modern `labels` with `includeSelectors: false` where the installed version supports it. Otherwise, apply labels explicitly to metadata while keeping selectors and Pod-template labels stable. The exact field support must be checked against the local Kustomize version.

### 5.5 Rendered output is the review artifact

Render all environments and inspect:

- resource kinds, names, and namespaces;
- image names and digest/tag policy;
- Deployment selectors and Pod labels;
- ports and Service selectors;
- security contexts, resource requests/limits, and probes;
- hostnames, RBAC, NetworkPolicy, PVCs and storage classes;
- generated ConfigMap/Secret names and references;
- optional component resources.

Do not infer final behavior solely from a source patch. For example, a `namePrefix` can change names and recognized references; an image transformer can change an image in multiple containers; a label transformer can change selectors. Save rendered YAML and compare overlays. Avoid committing generated manifests unless the repository deliberately uses generated YAML as its reviewed deployment artifact.

## 6. Level 2 — Patches, generators, replacements, and components

### 6.1 Current `patches` syntax

The current Kustomize configuration model uses the `patches` field for strategic-merge and JSON 6902 patches. Exact target fields and inline/file forms are version-sensitive; verify against the installed Kustomize reference. Older fields `patchesStrategicMerge` and `patchesJson6902` are legacy forms. Do not choose them for new work without a compatibility reason and a documented migration plan.

An illustrative strategic-merge patch file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: api
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
```

An overlay can reference it through a `patches` entry. The exact target selector is shown in Lab 3. This patch assumes the Deployment is named `scoring-api` before any name transformation; if the base name changes, the patch target must change or use a suitably precise target selector.

Strategic merge uses Kubernetes-aware merge semantics for supported resource kinds and fields. Some lists are merged by keys such as container `name`; others may be replaced or have resource-specific behavior. Do not assume every list merges by name. For example, container list patches generally identify the container by `name`, while arbitrary arrays can have different semantics.

Where supported, `$patch: delete` can delete a resource or item and `$patch: replace` can request replacement behavior. Verify the syntax for the installed version and target shape before relying on these directives. A whole-resource replacement can hide upstream changes and should be a deliberate decision.

### 6.2 JSON 6902 patches

JSON Patch operations use `op`, `path`, and (for operations such as `add` and `replace`) `value`. A patch may be expressed inline or in a file and paired with a target selector. Example file:

```yaml
- op: replace
  path: /spec/replicas
  value: 3
```

This path is appropriate for a Deployment-like resource with a `spec.replicas` field. A patch configuration must target the correct group/version/kind/name or other supported selector. Do not assume the filename alone selects a resource.

JSON Pointer path segments escape `~` as `~0` and `/` as `~1`. Array-index paths such as `/spec/template/spec/containers/0/image` are fragile: inserting or reordering a container can make index `0` point to a different container. JSON 6902 is precise and useful for fields where strategic merge is not suitable, but its precision can become fragility if targets and paths are not tested.

| Dimension | Strategic merge | JSON 6902 |
|---|---|---|
| Intent readability | Often resembles the target resource | Explicit operation and path |
| Lists | Kubernetes/resource-specific merge behavior | Explicit array index/path operations |
| Best fit | Named fields and supported merge keys | Precise add/replace/remove operations |
| Main hazard | Assuming every list merges by name | Index/path breaks after structural changes |
| Review practice | Inspect final list contents | Verify each path and operation against rendered target |

### 6.3 Generators and hash suffixes

`configMapGenerator` and `secretGenerator` create resources from literals, files, or environment-like inputs supported by the tool. Kustomize normally adds a content-derived suffix to generated resource names. When a generated ConfigMap is referenced by a recognized field in a Deployment, Kustomize can rewrite the reference to the generated name. A changed input changes the generated name and the Pod template reference; Kubernetes sees a changed Pod template and may roll out new Pods.

Example:

```yaml
configMapGenerator:
  - name: scoring-config
    literals:
      - LOG_LEVEL=info
      - MODEL_NAME=demo-model
```

The exact generated suffix is intentionally not shown because it depends on the content and tool implementation. Treat it as generated output, not a hand-maintained name.

| Setting/behavior | Effect | Caution |
|---|---|---|
| Default generated hash suffix | Content changes produce a different resource name | Verify reference rewriting in rendered output |
| `behavior: create` | Create a generated resource | Existing-name conflicts may fail |
| `behavior: replace` | Replace an existing resource with generated content | Exact merge/replace behavior should be verified for the installed version |
| `behavior: merge` | Merge generated data with an existing resource where supported | Requires a matching resource and predictable ownership |
| `disableNameSuffixHash` | Removes the generated content hash from the name | Config change may not alter Pod template, so rollout may not happen automatically |
| `options.immutable` | Requests an immutable generated ConfigMap/Secret where supported | Verify field support and Kubernetes behavior |

The exact support and semantics of `behavior`, `disableNameSuffixHash`, and `options.immutable` are `[VERIFY][VERSION-SENSITIVE]`. Do not copy a field into a production configuration until the installed Kustomize accepts it and the output is tested.

A hash-driven rollout is useful when configuration is intended to be versioned with the Pod template. If a workload reads an external configuration source or a stable-name ConfigMap, changing that external object does not guarantee a Pod restart. Define an explicit rollout mechanism or application reload behavior.

**Secret warning:** `secretGenerator` is not secret management. A secret literal or file committed to Git is still a secret committed to Git. Shell history, rendered YAML, build logs, and CI artifacts can also expose it. Kubernetes Secret data is commonly represented as base64 in YAML; base64 is encoding, not encryption by itself. Use dummy values in labs and follow M09 for secret lifecycle, external secret systems, rotation, and access control.

### 6.4 `replacements` and legacy `vars`

`replacements` copies a source field value into one or more target fields. It can avoid hard-coding the same value in multiple resources. The source and target field paths must match the resource structure; custom-resource paths may require configuration. Verify supported syntax and behavior for the installed version.

Illustrative example:

```yaml
replacements:
  - source:
      kind: Service
      name: scoring-api
      fieldPath: metadata.name
    targets:
      - select:
          kind: ConfigMap
          name: scoring-runtime
        fieldPaths:
          - data.SERVICE_NAME
```

This is illustrative: the source and target resources must exist, and the target field path must be supported. Verify the exact syntax against the installed Kustomize reference. The legacy `vars` feature has been deprecated/legacy in Kustomize documentation; confirm current status and replacement guidance `[VERIFY]`. Use `replacements` for new work where its source/target model fits, rather than introducing new legacy `vars` configuration.

### 6.5 Components

Components are reusable optional bundles that overlays can include. A monitoring component might add a ServiceMonitor where the relevant CRD is installed; a NetworkPolicy component might add a policy appropriate to the app’s labels and ports. Component syntax, `kind`/`apiVersion`, and compatibility are version-sensitive `[VERIFY]`.

Components reduce duplication only when their assumptions are explicit. Document resource names, expected labels, ports, required CRDs, and which environments include them. Test each supported overlay/component combination. A component should not silently change an application’s selector, expose a service, or assume a CRD exists in every cluster.

### 6.6 Remote resources and supply-chain risk

Kustomize can reference remote bases/resources. A floating branch can move, causing identical repository commits to render different output at different times. Prefer immutable commit SHAs or vendor reviewed content into the repository. Vendoring improves build reproducibility and offline availability but transfers update and vulnerability-patching responsibility to your team.

Evaluate remote content for provenance, licensing, ownership, network availability, and change review. A pinned source is more reproducible, but not automatically trustworthy. Pinning an unreviewed malicious commit only makes the malicious content stable.

`kubectl kustomize --load-restrictor` and file-reference restrictions are version-sensitive; check `kubectl kustomize --help` and the matching documentation before using an exact flag. Load restrictions help limit file access but do not turn untrusted sources into safe sources. Avoid broadening load permissions merely to make a build pass.

### 6.7 Transformer ordering, name references, and CRDs

Kustomize applies a set of built-in transformations and patches. Custom transformer configuration and version changes can affect the final result. Do not rely on a universal ordering claim without verifying the version and feature involved. Debug by rendering the full overlay and examining the output after all transformations.

Name prefix/suffix and generator hashes can rewrite known references such as a Deployment’s ConfigMap reference. Fields inside custom resources may not be recognized as references. Kustomize’s `nameReference` configuration can teach transformers about additional fields; custom configuration through `configurations` is `[VERIFY]` and should be tested against the installed version. CRDs and custom resources also complicate schema validation: the API server must know the CRD, and offline validators need appropriate schemas or an explicit exception/validation plan.

## 7. Level 3 — Safe overlay design and validation

### 7.1 Overlay design as an API

Treat the base as a public interface. Document which fields overlays may change, keep resource names and selectors stable, and avoid changing base behavior through broad patches. Keep overlays shallow and variance explicit. If every overlay repeatedly overrides the same fields, revise the base or split ownership cleanly.

| Acceptable environment variance | Suspicious variance needing explanation |
|---|---|
| Replica count and resource sizing | Production disables probes without a documented reason |
| Hostname or environment-specific ingress/route | Selector labels differ between environments |
| Storage class for an actual PVC | Storage class specified where no PVC uses it |
| Approved image digest | `latest` in one environment |
| Explicitly enabled NetworkPolicy/monitoring component | Production unexpectedly drops policy or RBAC |
| Different resource budgets supported by capacity evidence | Production requests/limits disappear |
| Non-secret environment-specific config | Credentials committed in overlay values |

Production should usually be stricter, not merely a copy with higher replicas. Differences should have owners, reasons, and review tests.

### 7.2 Compose application and platform resources

An overlay can combine application resources from `base/` with a reusable component or shared platform resource. Be explicit about resource names and ownership: duplicate names can cause build errors or confusing patch targets. NetworkPolicy labels and selectors must match the actual Pods; a syntactically valid policy can still select no Pods or block needed traffic. A PDB is meaningful only when its selector matches the workload and its availability intent is justified.

A Helm-rendered output can be used as input to a Kustomize stage in some workflows, but it adds a generation boundary and tool/version dependency. Render the chart first, then patch the generated YAML, and test the complete pipeline. Unit 6 owns the full Helm-versus-Kustomize comparison; this unit only introduces the pattern.

### 7.3 `helmCharts` inflation awareness

Kustomize supports Helm chart inflation through `helmCharts` in some standalone/version configurations, and may require `--enable-helm`. This is `[VERIFY][VERSION-SENSITIVE]`: embedded `kubectl` and standalone Kustomize may not expose the same behavior. The operation depends on Helm and chart repositories or local chart content, so pin chart versions and values inputs, review generated YAML, and account for additional execution and supply-chain surface. Do not assume a successful build means the chart’s runtime behavior is correct.

### 7.4 Validation pipeline

| Stage | Example | Cluster required? | What it proves / does not prove |
|---|---|---:|---|
| Build | `kubectl kustomize overlays/prod` | No | Produces final YAML; does not validate API acceptance |
| Schema | `kubeconform` on saved YAML | No | Validates known schemas for selected version; CRDs need schema handling |
| Policy | Organization rules on rendered YAML | No | Checks only encoded rules |
| Render diff | Compare baseline/candidate output | No | Reveals changes; reviewer must assess safety |
| `kubectl diff -k` | If supported by installed kubectl `[VERIFY]` | Yes | Compares desired/live state; permissions and context matter |
| Server-side dry-run | `kubectl apply --dry-run=server -f rendered.yaml` `[VERIFY]` | Yes | API/admission validation without persistence; not rollout/runtime proof |
| Apply/runtime | Apply only in disposable cluster and test readiness | Yes | Exercises selected cluster behavior; not every production condition |

Save rendered output in a controlled temporary directory. Validate against the intended Kubernetes version, not merely the local server. Before `kubectl diff`, dry-run, or apply, check the current context and require an exact disposable context name. If `kubectl diff -k` is not supported, render to a file and use a reviewed diff tool or the supported equivalent.

Safe context guard:

```bash
EXPECTED_CONTEXT="kind-m06-kustomize-u5"
CURRENT_CONTEXT="$(kubectl config current-context)"
printf 'Expected: %s\nCurrent:  %s\n' "$EXPECTED_CONTEXT" "$CURRENT_CONTEXT"
test "$CURRENT_CONTEXT" = "$EXPECTED_CONTEXT" || {
  echo "Refusing cluster operation: context mismatch" >&2
  exit 2
}
```

Never use this example with production credentials or contexts.

### 7.5 Jobs, immutable fields, and generated configuration

Jobs are one-shot workloads and have lifecycle expectations different from Deployments. Updating a Job’s pod template can encounter immutable-field restrictions; a new Job name or deliberate delete/recreate strategy may be necessary. Understand the consequences before removing resources. Never blindly delete a PVC or stateful resource as a patch fix.

A generated ConfigMap hash change usually changes the generated resource name and a recognized Pod-template reference, which can trigger a Deployment rollout. This is often intended. Unexpected churn may indicate an input file changed, line endings changed, an overlay generated different data, or tool versions differ. Compare generator input and rendered output before diagnosing a cluster issue.

### 7.6 Patch troubleshooting decision tree

- **Resource not changed:** verify the overlay includes the patch; inspect target group/version/kind/name/namespace/labels; verify the patch path and final build.
- **Wrong resource changed:** tighten the target selector and assert the expected number and identity of matches.
- **List item duplicated/replaced:** inspect strategic merge keys and resource semantics; consider JSON 6902 only when the path is stable.
- **Selector changed:** inspect `commonLabels` and label transformers; compare Deployment selector with Pod-template labels and immutable live selector.
- **Generated reference stale:** inspect generated name/hash and whether the reference field is recognized; configure custom name references if supported.
- **Output unexpectedly changes:** pin remote sources, compare embedded/standalone versions, inspect input files, and reproduce from a clean workspace.
- **Plugin/build behavior is unclear:** do not enable untrusted plugins to experiment. First reproduce with built-in features and consult version-matched docs.

`--enable-alpha-plugins` is awareness-only here. Plugin enablement and behavior are version-sensitive `[VERIFY]`; plugins or external executables may run arbitrary code. Never enable an unreviewed plugin in privileged CI.

## 8. Level 4 — Governance, CI, and migration

### 8.1 Governance at scale

At organization scale, assign ownership explicitly. A team base can own app-specific workload defaults; a platform base or component can own shared policy resources; a cluster overlay can encode cluster-specific endpoints or storage classes. Use naming and label conventions consistently. CODEOWNERS and review routing belong to the M02 workflow layer.

Overlay-sprawl symptoms include many near-identical overlays, repeated overrides of the same field, duplicated resources, deep inheritance, unexplained production-only exceptions, remote sources with no owner, and unsupported overlay/component combinations. Refactor in small steps:

1. Capture the current build output for every supported overlay.
2. Identify repeated resources and repeated patches.
3. Agree ownership and stable interfaces.
4. Extract a base/component or simplify overlay differences.
5. Build old and new trees with recorded tool versions.
6. Compare rendered output and explain every intentional difference.
7. Run schema/policy checks and cluster tests where behavior changes.
8. Merge with owners’ approval and preserve rollback evidence.

### 8.2 CI and rendered diffs

A local or CI pipeline should build every supported overlay, validate rendered YAML, apply policy checks, compare against a baseline, save non-sensitive evidence, and fail on required validation errors. Missing optional tools must be reported clearly; a required gate must not silently skip. Text diffs are portable but noisy; semantic diffs can improve signal but must not normalize away important fields.

Flag for review: selector changes, removed security contexts, image digest changes, replicas unexpectedly set to zero, new RBAC, deleted NetworkPolicy, hostname changes, PVC/storage changes, resource deletions, and remote base changes. Diff review is a decision gate, not automatic proof of safety.

A minimal cluster-free build/diff script is:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$ROOT/evidence"
mkdir -p "$OUT"
for env in dev staging prod; do
  kubectl kustomize "$ROOT/overlays/$env" > "$OUT/$env.yaml"
done
for env in dev staging prod; do
  baseline="$ROOT/baseline/$env.yaml"
  candidate="$OUT/$env.yaml"
  if [[ ! -f "$baseline" ]]; then
    echo "Missing reviewed baseline: $baseline" >&2
    exit 2
  fi
  diff -u "$baseline" "$candidate" > "$OUT/$env.diff" || rc=$?
  rc="${rc:-0}"
  if [[ "$rc" -gt 1 ]]; then exit "$rc"; fi
  if [[ "$rc" -eq 1 ]]; then
    echo "Review required: $env diff saved to $OUT/$env.diff"
  fi
  unset rc
done
```

This script intentionally reports differences for review instead of treating them as automatically safe. Extend it with the selected schema validator and policy engine, making their versions explicit. Do not use `|| true` to hide failures.

### 8.3 Migration strategies

**Copied manifests → Kustomize:** identify shared resources, establish a base, extract environment differences into overlays, compare old/new output, validate, and roll out one environment at a time. Risk: hidden differences in the copies may be lost during consolidation. Roll back by restoring the prior reviewed manifests.

**Kustomize → Helm:** consider it when distribution, a versioned values contract, hooks, dependencies, or release lifecycle are important. Translate overlays into chart values/templates carefully; compare rendered manifests across all environments. Risk: template behavior and release ownership may differ from the previous workflow.

**Helm → rendered manifests/Kustomize:** consider it when teams need plain YAML review and can own the lifecycle trade-offs. Pin chart version and values, render deterministically, then patch only what is necessary. Risk: chart upgrades may change generated structure and the Kustomize patch may no longer match.

**Remote base → vendored copy:** pin and review a known revision, vendor it, document the upstream origin and license, and create an update process. Risk: the team now owns monitoring and applying upstream fixes.

None of these is universally superior. Define compatibility tests and rollback plans before migration. Argo CD and Flux may invoke Kustomize; their reconciliation behavior belongs to M08.

### 8.4 Incident analyses

#### Incident 1 — `commonLabels` changes selectors and upgrade fails

**Symptom:** Applying a new overlay fails because a Deployment selector changed.  
**Evidence:** Compare `kubectl kustomize` output before/after; inspect `.spec.selector.matchLabels` and live Deployment selector; record the API error without fabricating its exact text.  
**Root cause:** A global label transformation affected selector fields.  
**Mitigation:** Restore stable selectors and use a supported label configuration that does not include selectors, or explicitly apply metadata labels.  
**Regression test:** Assert that selector labels remain unchanged across overlays.  
**Prevention:** Review rendered selectors and test upgrades against a disposable cluster.

#### Incident 2 — Patch targets wrong resource after rename

**Symptom:** Intended resource remains unchanged, or a different object changes.  
**Evidence:** Render the full overlay and compare target GVK/name/namespace; inspect patch target selectors.  
**Root cause:** Patch target was coupled to an old name or matched too broadly.  
**Mitigation:** Tighten the target and update the patch path/identity.  
**Regression test:** Assert the exact resource identity and changed field.  
**Prevention:** Keep patch targets explicit and review output after renames/prefixes.

#### Incident 3 — `secretGenerator` commits production password

**Symptom:** Secret material appears in Git history or rendered artifacts.  
**Evidence:** Search repository/history and CI artifacts using approved secret-scanning procedures; do not echo the secret.  
**Root cause:** Generator input was treated as a secure store.  
**Mitigation:** Rotate/revoke the credential immediately, remove access, and follow incident-response policy; deleting the latest file does not erase Git history.  
**Regression test:** Add secret scanning and ensure only dummy fixtures are committed.  
**Prevention:** Use M09-approved secret lifecycle and never store production secrets in Kustomize inputs.

#### Incident 4 — Remote base moves and changes production output

**Symptom:** Same local repository revision renders different resources later.  
**Evidence:** Compare remote reference, commit identity, tool versions, and previous rendered artifact.  
**Root cause:** A floating branch/tag or mutable source was referenced.  
**Mitigation:** Pin a reviewed immutable revision or vendor the content.  
**Regression test:** Rebuild from a clean workspace and compare output.  
**Prevention:** Require source pinning, ownership, and reviewed updates.

#### Incident 5 — ConfigMap hash causes unexpected restarts

**Symptom:** Pods roll out after a config change or seemingly unrelated edit.  
**Evidence:** Compare generated ConfigMap name/data and Deployment Pod-template reference before/after.  
**Root cause:** Input data changed, possibly due to line endings or an unintended overlay.  
**Mitigation:** Revert unintended input changes; if stable-name config is required, define an explicit reload/restart strategy.  
**Regression test:** Capture generated names and rendered references for known inputs.  
**Prevention:** Review generator input diffs and understand hash rollout semantics.

#### Incident 6 — JSON 6902 patch changes the wrong container

**Symptom:** An image or environment value changes on the wrong container after a container is inserted.  
**Evidence:** Inspect container order and patch path.  
**Root cause:** An array-index path was brittle.  
**Mitigation:** Correct the path and render the output; consider strategic merge where named-container merge is supported.  
**Regression test:** Assert container name and resulting image/env value.  
**Prevention:** Minimize index-based paths and test structural changes.

#### Incident 7 — CRD field is not transformed or validated

**Symptom:** A generated name is not rewritten in a custom resource or local validation cannot validate it.  
**Evidence:** Inspect CRD schema, field path, rendered reference, and validator configuration.  
**Root cause:** The field was unknown to built-in name-reference or schema handling.  
**Mitigation:** Add supported transformer configuration and use the CRD schema or target-cluster validation.  
**Regression test:** Render a fixture and assert the reference is correct.  
**Prevention:** Treat CRD configuration as an explicit compatibility dependency.

#### Incident 8 — Embedded and standalone versions differ

**Symptom:** A feature works with `kustomize build` but not with `kubectl kustomize`, or output differs.  
**Evidence:** Capture both versions and compare build output.  
**Root cause:** The binaries embed different Kustomize releases or feature support.  
**Mitigation:** Standardize the CI toolchain or constrain features to the supported intersection.  
**Regression test:** Build with the same pinned tool in CI and compare expected output.  
**Prevention:** Record versions and document the supported renderer.

## 9. SRE lens

| Indicator | Definition | Caveat |
|---|---|---|
| Overlay validation pass rate | Overlay builds passing required schema/policy gates divided by attempted overlay builds in a defined window | Separate tool outages from configuration defects |
| Change failure rate | Overlay changes requiring rollback/hotfix due to config defects divided by overlay releases in the window | Attribution and release count may be small |
| Unreviewed diff count | High-risk rendered changes merged without recorded approval | Requires a reliable review record |
| Remote change detection time | Time from upstream movement to detection by CI/review | Pinning reduces surprise but does not remove update workload |
| Config-induced restart rate | Rollouts attributed to config changes divided by relevant config changes | Some rollouts are intended; classify expected vs unexpected |
| Time to diagnose | Time from signal to evidence-backed root cause | Define start/end consistently |
| Overlay sprawl | Count/trend of duplicate patches, exceptions, and unsupported combinations | Counts are proxies, not quality by themselves |

Example metric: over a rolling 30-day window, **overlay validation pass rate** = number of overlay build attempts passing all required render/schema/policy gates divided by all overlay build attempts. Report the sample size and separate infrastructure/tool failures. Small samples and changing overlay counts make percentages unstable; do not compare teams without accounting for complexity.

Runbook: signal → reproduce with pinned tool versions → build each relevant overlay → inspect rendered diff → isolate base/overlay/transformer/remote source → validate schema and policy → mitigate using a reviewed change → verify cluster state if needed → add regression test → document the incident.

On a 4 CPU / 8 GB / 30 GB laptop, render overlays first without a cluster. Run one small `kind` cluster at a time, capture evidence, and delete it when finished. Do not leave multiple clusters and large image caches running unnecessarily.

## 10. Security lens

| Threat | Control | Evidence | Residual limitation |
|---|---|---|---|
| Secret committed via generator, YAML, shell history, or artifact | Dummy values, secret scanning, approved secret lifecycle | Scan results and reviewed artifact list | Scanners can miss transformed/encoded secrets |
| Floating remote base changes | Immutable revision pin or vendoring, code review | Source SHA and rendered diff | Pinned code may still be malicious or vulnerable |
| Plugin/external command executes code | Disable untrusted plugins; review/pin dependencies | Tool configuration and CI permissions | Reviewed dependencies can later be compromised |
| Broad RBAC, privileged/root workload, missing limits | Rendered policy checks and secure defaults | Policy report and manifest review | Rules may not cover all resource shapes |
| Labels/patches alter selectors or NetworkPolicy | Stable selector assertions and connectivity tests | Rendered diff and targeted tests | Render does not prove all traffic paths |
| Mutable image tags | Digest policy and approved image inventory | Extracted rendered image references | Digest alone does not establish provenance |
| Untrusted file references/load settings | Restrict source scope and review paths | Build logs and repository review | File restrictions are version/config dependent |
| Sensitive rendered artifact | Synthetic values, redaction, access/retention controls | Artifact review | Redaction is not perfect |
| Production context accidentally selected | Exact context guard and disposable credentials | Captured context before mutation | A misconfigured credential can still be dangerous |
| CRD transformation/schema gap | Explicit CRD schemas/configuration and cluster validation | Schema/version evidence | Controller semantics may remain untested |
| Hash disabled without rollout plan | Explicit reload/restart mechanism and test | Rendered Pod template and rollout evidence | External config can change outside the build |

Kustomize is not a secret manager. Rendering success does not prove the API server accepts every resource. `kubeconform` and other schema checks are not admission-policy or runtime checks. A pinned remote source is not automatically trustworthy. A rendered diff does not prove a change is safe. Plugins may execute arbitrary code. Never run unreviewed plugins or remote build sources in privileged CI, and never use production credentials or contexts in labs.

## 11. Production checklist

- [ ] Embedded and standalone Kustomize/kubectl versions are recorded.
- [ ] Base and overlay responsibilities are documented.
- [ ] Overlays are shallow and environment variance is small and explicit.
- [ ] `kustomize build` output is reviewed for every environment.
- [ ] Deployment selectors remain stable and match Pod-template labels.
- [ ] Modern label behavior is used where supported and verified.
- [ ] Patches target explicit resources and fields.
- [ ] Current `patches` syntax is used, or legacy syntax is documented with a migration plan.
- [ ] Generator hashes and rollout consequences are understood.
- [ ] Production secrets are not committed in generator inputs or rendered artifacts.
- [ ] Images follow digest/tag policy.
- [ ] Remote resources are pinned or vendored and reviewed.
- [ ] Components are tested in every supported overlay combination.
- [ ] CRDs/custom resources have an explicit validation strategy.
- [ ] Output is validated against the intended Kubernetes version.
- [ ] Policy checks and rendered diffs run in CI.
- [ ] CI fails on required failures and reports missing tools clearly.
- [ ] `diff`/apply uses an explicitly checked non-production context.
- [ ] Cleanup, rollback, and recovery procedures are documented.
- [ ] Overlay ownership, migration, and EOL policy are documented.

## 12. Hands-on labs

### Lab 1 — Build a base, three environment overlays, and a reusable component

**Goal:** Build a complete base with dev/staging/prod overlays and an optional NetworkPolicy component.  
**Acceptance criteria:** All three overlays render; replica/resource/image/hostname differences are explicit; selector and Pod labels match; the component renders only where included; output diffs are saved.  
**Estimated time:** 2–3 hours.  
**Prerequisites:** `kubectl` with Kustomize support or standalone `kustomize`, Bash, Git. **Cluster required: No** for core tasks.

Create this complete tree:

```text
kustomize-lab/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── pvc.yaml
├── components/
│   └── network-policy/
│       ├── kustomization.yaml
│       └── network-policy.yaml
├── overlays/
│   ├── dev/kustomization.yaml
│   ├── staging/kustomization.yaml
│   └── prod/kustomization.yaml
├── evidence/
└── versions.txt
```

`base/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
  - ingress.yaml
  - configmap.yaml
  - pvc.yaml
```

`base/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: scoring-ingress
spec:
  rules:
    - host: scoring.example.invalid
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: scoring-api
                port:
                  number: 8000
```

This is a manifest-shape example. An Ingress controller and valid DNS/TLS configuration are cluster-specific; the hostname uses the reserved illustrative `.invalid` domain and is not expected to route traffic.

`base/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  labels:
    app.kubernetes.io/name: scoring
    app.kubernetes.io/instance: scoring
    app.kubernetes.io/component: api
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring
      app.kubernetes.io/instance: scoring
      app.kubernetes.io/component: api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring
        app.kubernetes.io/instance: scoring
        app.kubernetes.io/component: api
    spec:
      serviceAccountName: scoring-api
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: api
          image: registry.example.invalid/scoring-api@sha256:REPLACE_WITH_VERIFIED_DIGEST
          ports:
            - name: http
              containerPort: 8000
          envFrom:
            - configMapRef:
                name: scoring-config
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
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: scoring-api
  labels:
    app.kubernetes.io/name: scoring
    app.kubernetes.io/instance: scoring
    app.kubernetes.io/component: api
```

`base/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  labels:
    app.kubernetes.io/name: scoring
    app.kubernetes.io/instance: scoring
spec:
  selector:
    app.kubernetes.io/name: scoring
    app.kubernetes.io/instance: scoring
    app.kubernetes.io/component: api
  ports:
    - name: http
      port: 8000
      targetPort: http
```

`base/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scoring-runtime
data:
  LOG_LEVEL: info
  MODEL_NAME: demo-model
```

`base/pvc.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: scoring-cache
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

The base includes a PVC to make storage-class overlays meaningful, but the API does not mount it in this minimal fixture. Treat it as a storage-policy example, not proof that application data persists. Add a mount only if the application genuinely needs persistent storage. Storage classes must exist in the target cluster.

`components/network-policy/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
resources:
  - network-policy.yaml
```

Component API/version support is `[VERIFY][VERSION-SENSITIVE]`; confirm with the installed version. If unsupported, use an ordinary resource directory included by the overlay as a compatibility fallback.

`components/network-policy/network-policy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scoring-api-ingress
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: scoring
      app.kubernetes.io/instance: scoring
      app.kubernetes.io/component: api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: scoring
              app.kubernetes.io/component: worker
      ports:
        - protocol: TCP
          port: 8000
```

This policy is illustrative and allows ingress only from matching worker Pods in the same namespace. It may block health checks or other legitimate callers if the cluster design differs. Review and test it before using it outside the lab.

`overlays/dev/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: scoring-dev
namePrefix: dev-
resources:
  - ../../base
components:
  - ../../components/network-policy
commonAnnotations:
  environment: dev
replicas:
  - name: scoring-api
    count: 1
images:
  - name: registry.example.invalid/scoring-api
    newName: registry.example.invalid/scoring-api
    digest: sha256:REPLACE_WITH_VERIFIED_DIGEST
patches:
  - target:
      version: v1
      kind: PersistentVolumeClaim
      name: scoring-cache
    patch: |-
      - op: add
        path: /spec/storageClassName
        value: standard
  - target:
      group: networking.k8s.io
      version: v1
      kind: Ingress
      name: scoring-ingress
    patch: |-
      - op: replace
        path: /spec/rules/0/host
        value: scoring-dev.example.invalid
```

The `images.digest` field and component support are version-sensitive; verify them. The digest is explicitly a placeholder and is not a valid image digest until replaced. If your version does not support `digest`, use the documented supported image syntax for that version and record the compatibility choice. The storage class `standard` is an illustrative name; it may not exist in your cluster.

`overlays/staging/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: scoring-staging
namePrefix: stg-
resources:
  - ../../base
components:
  - ../../components/network-policy
commonAnnotations:
  environment: staging
replicas:
  - name: scoring-api
    count: 2
images:
  - name: registry.example.invalid/scoring-api
    newName: registry.example.invalid/scoring-api
    digest: sha256:REPLACE_WITH_VERIFIED_DIGEST
patches:
  - target:
      version: v1
      kind: PersistentVolumeClaim
      name: scoring-cache
    patch: |-
      - op: add
        path: /spec/storageClassName
        value: fast
  - target:
      group: networking.k8s.io
      version: v1
      kind: Ingress
      name: scoring-ingress
    patch: |-
      - op: replace
        path: /spec/rules/0/host
        value: scoring-staging.example.invalid
```

`overlays/prod/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: scoring-prod
namePrefix: prod-
resources:
  - ../../base
components:
  - ../../components/network-policy
commonAnnotations:
  environment: prod
replicas:
  - name: scoring-api
    count: 3
images:
  - name: registry.example.invalid/scoring-api
    newName: registry.example.invalid/scoring-api
    digest: sha256:REPLACE_WITH_VERIFIED_DIGEST
patches:
  - target:
      version: v1
      kind: PersistentVolumeClaim
      name: scoring-cache
    patch: |-
      - op: add
        path: /spec/storageClassName
        value: premium
  - target:
      group: networking.k8s.io
      version: v1
      kind: Ingress
      name: scoring-ingress
    patch: |-
      - op: replace
        path: /spec/rules/0/host
        value: scoring.example.invalid
```

The environment-specific hostnames are illustrative and use the reserved `.invalid` domain; they are not expected to resolve. The Ingress resource renders cluster-free, but actual routing requires a compatible Ingress controller and environment-specific DNS/TLS configuration.

Build from the project root:

```bash
cd "$HOME/m06-kustomize-u5/kustomize-lab"
mkdir -p evidence
kubectl kustomize overlays/dev > evidence/dev.yaml
kubectl kustomize overlays/staging > evidence/staging.yaml
kubectl kustomize overlays/prod > evidence/prod.yaml
diff -u evidence/dev.yaml evidence/staging.yaml > evidence/dev-staging.diff || test "$?" -eq 1
diff -u evidence/staging.yaml evidence/prod.yaml > evidence/staging-prod.diff || test "$?" -eq 1
```

If using standalone Kustomize, replace `kubectl kustomize` with `kustomize build` and record the version. Inspect names, namespaces, selectors, labels, image references, resource budgets, PVC storage class, NetworkPolicy selection, and annotations. Representative output excerpt (not executed):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dev-scoring-api
  namespace: scoring-dev
  annotations:
    environment: dev
spec:
  replicas: 1
```

The exact output depends on tool version and transformations. The digest placeholders are not valid artifacts. Replace them with an approved verified digest before runtime tests. Also add an Ingress/HTTPRoute fixture if the lab needs hostname differences; document its controller/API assumptions.

**Evidence:** `versions.txt`, three rendered YAML files, diffs, and written explanations for each difference. This proves rendering and comparison only, not API acceptance or rollout.  
**Cleanup:** No cluster resources were created. Remove only the lab directory when evidence is no longer needed.  
**Common failures:** unsupported component/digest syntax—check version; storage class not found—verify cluster class; unexpected selector changes—inspect labels and selectors; missing hostname—add a valid route resource before testing hostnames.  
**Stretch:** Add an ETL CronJob and worker Deployment with their own selectors, resource limits, and an explicitly reviewed NetworkPolicy.

### Lab 2 — Demonstrate selector immutability and ConfigMap hash rollout

**Goal:** Reproduce or safely approximate a selector mutation failure and demonstrate a generated ConfigMap hash changing the Pod template.  
**Acceptance criteria:** Capture before/after render; show a failed selector update only if the installed version actually changes selectors; correct the configuration; show a changed generated ConfigMap name/reference after changing data.  
**Estimated time:** 2–3 hours.  
**Prerequisites:** `kind`, `kubectl`, Kustomize, disposable local cluster. **Cluster required: Yes** for the actual immutability and rollout demonstration.

#### Part A — Selector failure

Create a disposable cluster and verify its context:

```bash
kind create cluster --name m06-kustomize-u5
kubectl config current-context
kubectl version
```

Do not continue unless the current context is the cluster you just created. Use a small fixture with a Deployment whose selector is stable. To demonstrate the legacy hazard, create a temporary Kustomize overlay that applies `commonLabels` and inspect the build before applying:

```bash
kubectl kustomize selector-broken > evidence/selector-broken.yaml
```

Only proceed if the rendered `.spec.selector.matchLabels` actually changes compared with the initial live Deployment. Apply the initial version first, then attempt the changed output. Kubernetes treats Deployment selectors as immutable; if the selector changed, the update should be rejected. Exact error wording is version-dependent and must be captured from the actual run. If the installed Kustomize version does not produce a selector change for the chosen fixture, do not claim a failure occurred; retain the rendered comparison and use it as a cluster-free demonstration.

Correct the overlay by keeping selector labels stable. Where supported, use modern `labels` configuration with `includeSelectors: false`; otherwise apply metadata labels explicitly and preserve selector/template labels. Rebuild and verify the selector is unchanged before applying. Never leave the broken Deployment in place.

#### Part B — ConfigMap hash

Create `hash-lab/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
configMapGenerator:
  - name: scoring-config
    literals:
      - LOG_LEVEL=info
```

Create `hash-lab/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hash-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hash-demo
  template:
    metadata:
      labels:
        app: hash-demo
    spec:
      containers:
        - name: pause
          image: registry.k8s.io/pause:3.10
          envFrom:
            - configMapRef:
                name: scoring-config
```

The image is an illustrative public test image; verify availability and policy before applying. The example demonstrates reference rewriting, not application configuration consumption.

From the parent directory:

```bash
kubectl kustomize hash-lab > evidence/hash-before.yaml
grep -n -E 'name: scoring-config|configMapRef|LOG_LEVEL' evidence/hash-before.yaml
```

Change `LOG_LEVEL=info` to `LOG_LEVEL=debug`, then:

```bash
kubectl kustomize hash-lab > evidence/hash-after.yaml
diff -u evidence/hash-before.yaml evidence/hash-after.yaml
```

The generated ConfigMap name and Deployment reference should change if the installed Kustomize version supports the standard hash behavior as expected. For an actual rollout, apply only to the disposable context and use `kubectl rollout status deployment/hash-demo`; capture Pod names before and after. If a test image cannot be pulled, do not claim runtime success—render-only evidence still demonstrates the generated-name transformation.

With `disableNameSuffixHash`, the resource name remains stable, and a configuration change may not change the Pod template reference. That can prevent automatic Deployment rollout. Use a deliberate restart or application reload strategy when appropriate; do not assume all applications reread ConfigMaps automatically.

**Evidence:** context/version record, before/after rendered YAML, selector comparison, actual error only if observed, ConfigMap name/reference diff, rollout status and Pod evidence if runtime test succeeded.  
**Cleanup:** Verify the context, then delete the lab cluster with `kind delete cluster --name m06-kustomize-u5`.  
**Common failures:** wrong context—stop immediately; unsupported modern labels field—use explicit metadata labels; image pull failure—retain render evidence and do not claim rollout; hash did not change—verify generator input and build path.  
**Stretch:** Compare behavior with `disableNameSuffixHash: true` and document the missing Pod-template change.

### Lab 3 — Convert strategic merge to JSON 6902 and back

**Goal:** Represent the same replica change using both patch styles and observe their trade-offs.  
**Acceptance criteria:** Both patch forms render the same replica count; the JSON 6902 path targets the intended field; a documented array-index example shows why structural changes can break fragile paths.  
**Estimated time:** 60–90 minutes.  
**Prerequisites:** Lab 1 fixture and Kustomize. **Cluster required: No.**

Work from `kustomize-lab/`. Create `patches/replicas-merge.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
spec:
  replicas: 4
```

Create a temporary overlay `overlays/patch-merge/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
patches:
  - path: ../../patches/replicas-merge.yaml
```

Build it:

```bash
kubectl kustomize overlays/patch-merge > evidence/replicas-merge.yaml
grep -n -A2 'replicas:' evidence/replicas-merge.yaml
```

Now create `overlays/patch-json/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
patches:
  - target:
      group: apps
      version: v1
      kind: Deployment
      name: scoring-api
    patch: |-
      - op: replace
        path: /spec/replicas
        value: 4
```

Build and compare:

```bash
kubectl kustomize overlays/patch-json > evidence/replicas-json.yaml
diff -u evidence/replicas-merge.yaml evidence/replicas-json.yaml
```

The output should be equivalent for the intended field, apart from any irrelevant output ordering differences. Treat this as representative until run locally. Convert the JSON patch back to strategic merge and confirm the same output.

For the fragility exercise, consider a JSON path such as `/spec/template/spec/containers/0/image`. It targets the first container, not a container by semantic name. Insert a sidecar before the application container and render again; the index can now refer to the sidecar. Do not use this fragile path for the replica exercise itself. A named-container strategic merge patch is often clearer where the resource supports merge-by-name semantics.

**Evidence:** both patch files, rendered output, diff, and a short note describing which form is clearer for this field and why.  
**Cleanup:** Delete the temporary patch overlays/files or keep them as documented examples within the lab workspace. No cluster resources were created.  
**Common failures:** patch target name changed by a prefix; JSON path points to a missing field; old Kustomize does not support the selected `patches` syntax—verify version and use the supported documented form.  
**Stretch:** Convert a named container environment variable patch both ways and test what happens when the container is renamed.

## 13. Self-check questions

1. **What does Kustomize do, and what does it not do?**  
   **Answer:** It composes/transforms YAML into rendered manifests. It is not itself a release manager or reconciler. **Tempting wrong answer:** “Kustomize continuously keeps the cluster in sync” confuses it with a controller invoking it.

2. **Difference between `kubectl kustomize`, `kubectl apply -k`, and standalone `kustomize build`?**  
   **Answer:** The first renders with embedded Kustomize, the second builds and applies, and the third renders with standalone Kustomize. **Wrong answer:** treating their feature sets as identical ignores version divergence.

3. **Why can `commonLabels` break immutable selectors?**  
   **Answer:** It can transform selector labels as well as metadata labels. **Wrong answer:** “Labels are always harmless metadata” ignores selectors and workload identity.

4. **Strategic merge versus JSON 6902?**  
   **Answer:** Strategic merge expresses a partial resource using Kubernetes-aware merge semantics; JSON 6902 specifies explicit operations and paths. **Wrong answer:** assuming every list merges by name or every JSON path is stable.

5. **Why is an array-index JSON Patch fragile?**  
   **Answer:** Reordering/inserting array entries can make the index point to another item. **Wrong answer:** assuming index 0 means the same named container forever.

6. **How do generator hashes affect rollouts?**  
   **Answer:** Changed generated content can change the resource name and a recognized Pod-template reference, causing a rollout. **Wrong answer:** assuming any external ConfigMap edit automatically restarts Pods.

7. **Why does `secretGenerator` not make a Git-stored secret safe?**  
   **Answer:** The input remains in Git/history and may appear in rendered output or artifacts. **Wrong answer:** base64 or generation does not encrypt the source secret.

8. **How does `replacements` differ from legacy `vars`?**  
   **Answer:** `replacements` explicitly maps a source field into target field paths; `vars` is legacy/deprecated in current guidance, subject to verification. **Wrong answer:** introducing old syntax without checking support increases migration risk.

9. **Why pin or vendor remote bases?**  
   **Answer:** To make builds reproducible and changes reviewable. **Wrong answer:** a floating branch can change output without a local source change.

10. **How do you debug a patch that targets the wrong resource?**  
    **Answer:** Inspect final rendered output, verify target GVK/name/namespace/labels and path, tighten selectors, and add an assertion. **Wrong answer:** changing random patch fields without proving which resource matched.

## 14. Evidence artifacts

Learner-generated artifacts should be stored under the lab workspace:

- `versions.txt`;
- complete base/overlays/components tree;
- rendered YAML for dev/staging/prod;
- rendered diffs with explanations;
- schema and policy outputs;
- selector failure evidence and corrected output;
- ConfigMap hash before/after output and rollout evidence, if actually observed;
- strategic-merge and JSON 6902 patch variants;
- cleanup confirmation;
- incident postmortem notes;
- completed production checklist.

These are expected outputs, not artifacts that already exist. Redact sensitive output. Record the exact command and tool version. Label representative examples as illustrative; never convert an expected output into a claim of execution.

## 15. Interview and design-review questions

### 1. Design a base/overlay strategy for dev/staging/prod with minimal drift.

**Model answer:** Put stable workload structure, selectors, probes, and secure defaults in a base. Use shallow overlays for replicas, resource sizing, hostnames, storage classes where a PVC exists, and explicitly optional components. Test every overlay, preserve stable selectors, and review rendered diffs. The trade-off is that over-generalizing the base can make overlays complex; keep only genuinely shared behavior in it. Rendering proves composition, not runtime health.

### 2. Diagnose and safely fix a selector mutation caused by labels.

**Model answer:** Compare the old and new rendered `.spec.selector.matchLabels`, inspect the label transformer and live selector, and reproduce on a disposable cluster. Restore selector stability and use modern label behavior that excludes selectors where supported, or apply metadata labels explicitly. Add an invariant test. Do not claim every version of Kustomize produces identical behavior.

### 3. Choose strategic merge or JSON 6902 for a patch.

**Model answer:** Use strategic merge for readable partial resource changes and named list elements where supported; use JSON 6902 for explicit operations or cases where strategic merge is unsuitable. Check list semantics, target precision, and field paths. A JSON array index may break after reordering; strategic merge behavior varies by resource/field. Render and assert the final output either way.

### 4. Design secure CI for remote bases, plugins, diffs, and policy.

**Model answer:** Pin remote content or vendor reviewed revisions; capture tool versions; disable untrusted plugins; run builds with least privilege; validate schema and policy; render every overlay; review high-risk diffs; save scrubbed evidence; and fail closed on required checks. A pin is not a trust verdict, and policy rules can be incomplete. Never run unreviewed code in privileged CI.

### 5. When would you migrate from Kustomize to Helm or combine them?

**Model answer:** Consider Helm for packaged distribution, a versioned values API, dependencies/hooks, or release lifecycle. Consider Kustomize for plain-manifest composition and explicit overlays. Combining them can be justified when a chart is rendered and a small, stable Kustomize layer patches output, but it creates a tool/version boundary. Compare rendered output, test upgrades, document ownership, and plan rollback. Neither tool is universally superior; Unit 6 expands the decision framework.

## 16. Sources and verification notes

This chapter does not claim live documentation was consulted or commands were executed. Use official documentation matching installed tool versions.

| Topic | Official documentation/repository | URL | Version-sensitive? | Verify locally |
|---|---|---|---:|---|
| Kustomize concepts and overlays | Kubernetes Docs, Kustomize | https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/ | Yes | Supported fields and behavior |
| `kubectl kustomize`, `apply -k` | kubectl command reference | https://kubernetes.io/docs/reference/kubectl/ | Yes | Embedded version and supported commands |
| Standalone Kustomize | Kustomize project | https://kubectl.docs.kubernetes.io/ and https://github.com/kubernetes-sigs/kustomize | Yes | `kustomize version`, flags, output |
| Labels and selectors | Kubernetes labels/selectors docs | https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/ | API behavior stable; tooling varies | Selector immutability and transformer output |
| Patches | Kustomize reference | https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/patches/ | Yes | Current `patches` syntax and targets |
| JSON Patch | IETF RFC 6902 | https://www.rfc-editor.org/rfc/rfc6902 | Specification stable | Supported operations and path behavior |
| Generators | Kustomize reference | https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/configmapgenerator/ and https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/secretgenerator/ | Yes | Hashes, options, behavior |
| Components/replacements | Kustomize reference | https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/components/ and https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/replacements/ | Yes | `kind`/`apiVersion`, fields, target paths |
| Remote resources/load restrictions | Kustomize project docs | https://kubectl.docs.kubernetes.io/ and https://github.com/kubernetes-sigs/kustomize | Yes | Remote syntax, load-restrictor flags |
| Plugins/security | Kustomize project docs | https://github.com/kubernetes-sigs/kustomize | Yes | Plugin enablement and execution model |
| CRDs/custom resources | Kubernetes CRD docs | https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/ | Yes | Schema and transformer config |
| `kubectl diff` / dry-run | kubectl reference | https://kubernetes.io/docs/reference/kubectl/ | Yes | Exact installed command behavior |
| Deployment selectors | Kubernetes Deployment docs | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | API behavior depends on resource/version | Selector immutability and rollout behavior |
| ConfigMap behavior | Kubernetes ConfigMap docs | https://kubernetes.io/docs/concepts/configuration/configmap/ | Yes, by consumption method | Whether app reloads or needs restart |

### Source-grounded behavior versus recommendations

- Kustomize builds and transforms resource configurations; `kubectl apply -k` applies a Kustomize directory.
- Deployment selectors must remain consistent with Pod labels and cannot be casually changed on an existing Deployment.
- Generator hashes and recognized name references can affect rendered resource names and Pod templates.
- JSON Patch operations target explicit paths; array indices are positional.
- Remote content and plugins introduce reproducibility and supply-chain considerations.

Engineering recommendations in this chapter include keeping overlays shallow, requiring rendered diffs, pinning remote sources, preserving stable selectors, and making policy checks required. These are operational practices rather than claims that a tool guarantees safety.

### `[VERIFY]` / `[VERSION-SENSITIVE]` items

- Embedded versus standalone Kustomize feature parity.
- Modern `labels` field and `includeSelectors`.
- `patches` target fields and inline/file syntax.
- `$patch` directives and strategic merge behavior for specific resource lists.
- Generator `behavior`, `disableNameSuffixHash`, and `options.immutable`.
- `replacements`, component `kind`/`apiVersion`, and `vars` deprecation status.
- `kubectl kustomize --load-restrictor` syntax.
- Custom name-reference/transformer configuration for CRDs.
- `helmCharts` inflation and `--enable-helm`.
- `kubectl diff -k`, server-side dry-run syntax, and plugin enablement flags.

## 17. Author's verification checklist

| Gate | Status | Evidence note |
|---|---|---|
| Exact target filename and Unit 5 scope | PASS | Metadata and title match the requested chapter |
| L1–L4 concepts and boundaries | PASS | Fundamentals, patches, overlay design, governance, migration, incidents |
| Base/overlay commands and rendered review | PASS | Section 5 and Lab 1 |
| Patches, generators, replacements, components, remote resources, CRDs | PASS | Section 6 with version-sensitive caveats |
| Validation, selector safety, hash rollouts, troubleshooting | PASS | Section 7 and Lab 2 |
| Governance, CI, migration, eight incident analyses | PASS | Section 8 |
| Exactly three main labs | PASS | Labs 1–3 are present |
| Selector immutability and generator-hash lab | PASS | Lab 2 includes safe context instructions |
| Strategic merge ↔ JSON 6902 conversion lab | PASS | Lab 3 |
| SRE/security/checklist/self-check/interview/evidence/sources | PASS | Sections 9–16 |
| Live commands and cluster experiments executed | NOT VERIFIED | Learner must run in the versioned local environment |
| All example fields supported by installed Kustomize | NOT VERIFIED | Verify each `[VERIFY]` item against installed version |
| Placeholder digest/image is pullable | NOT VERIFIED | Placeholders are intentionally not real artifacts |
| Only the target artifact generated | PASS | This content is intended for `05-kustomize-bases-overlays-and-patches.md` |
