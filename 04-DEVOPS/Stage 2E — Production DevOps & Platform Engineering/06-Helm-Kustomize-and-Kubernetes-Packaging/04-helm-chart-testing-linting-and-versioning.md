# Helm Chart Testing, Linting, and Versioning

**Module:** M06 — Helm, Kustomize, and Kubernetes Packaging  
**Unit:** 4 — Helm chart testing, linting, and versioning  
**Target file:** `04-helm-chart-testing-linting-and-versioning.md`  
**Estimated time:** 12–16 hours: 3–4 hours reading, 4–5 hours cluster-free labs, 5–7 hours cluster labs  
**Prerequisites:** M01–M05 and M06 Units 1–3  
**Core tools:** Helm CLI, `kubectl`, `kind`, shell, YAML editor  
**Optional tools:** `kubeconform`, `helm-unittest`, chart-testing (`ct`), `yq`, `pytest`, Conftest/OPA, Trivy  
**Last reviewed:** Not independently verified  
**Tool baseline:** No versions assumed. Record installed versions and verify version-sensitive flags and plugin syntax against installed help and official documentation.

> **Core principle:** A chart passing one test stage does not prove production safety. Each stage detects different defects; rendered manifests and upgrade behavior must be reviewed.

## 1. Why this matters in production

Helm charts are executable packaging contracts for Kubernetes resources. A small template or values change can alter a Deployment selector, remove a security context, change a Service port, enable an optional resource, or change an image reference. A chart can pass `helm lint` and still fail when submitted to a real API server, admitted by cluster policy, scheduled, upgraded from an older release, or exercised by real traffic.

A reliable chart release therefore needs a testing ladder, not one green command. Metadata and template checks catch some defects cheaply. Values schema tests catch malformed configuration only when the schema expresses the contract. Rendering exposes environment-specific output. Kubernetes schema validation catches many object-shape errors, but does not necessarily understand admission policy or cross-resource relationships. Server-side dry-run asks the target API server to validate requests without persisting them, while disposable-cluster install and upgrade tests exercise more of the actual lifecycle. Policy checks target security and organization-specific requirements. Finally, rendered diffs and release review help humans detect risky behavioral changes.

Install-only testing is insufficient. A chart may install successfully but fail to upgrade because a field is immutable, a resource name changed, a hook behaves differently on upgrade, or an old values file no longer matches the new chart. Likewise, a patch release can change a default and unexpectedly change production behavior. Version numbers and changelogs are part of the operational interface, not decoration.

This unit continues the FastAPI scoring-service chart pattern from Unit 2. Where the original repository chart is not present, the labs define a small, self-contained fixture. Placeholder image references are intentionally non-runnable until replaced with an approved image. No digest is invented and no command output is represented as executed.

## 2. Learning objectives

By completing this unit, you should be able to:

- Explain the defects caught and missed by `helm lint`, values schema validation, render checks, `kubeconform`, server-side dry-run, install/upgrade tests, policy checks, and rendered diffs.
- Test all supported environment values files and verify that misspelled values are rejected when the schema contract is designed to reject unknown keys.
- Validate rendered manifests against an explicit Kubernetes version and handle custom-resource schemas deliberately.
- Write a smoke test using a `helm.sh/hook: test` Job or Pod and explain the limits of that test.
- Use a unit-test plugin when approved, while retaining a portable shell/Python fallback.
- Use chart-testing (`ct`) only after checking its configuration and installed version.
- Distinguish chart `version`, `appVersion`, image tags/digests, and `kubeVersion`.
- Classify chart changes under SemVer based on consumer impact, not just code size.
- Test install N → upgrade N+1, inspect rendered diffs, and test compatibility with old values fixtures.
- Build a fail-closed local chart CI script with explicit targets for lint, schema, render, manifest validation, unit assertions, policy, install, upgrade, and diff.
- Define a practical support matrix, manage flaky tests, and govern chart deprecation/EOL.

## 3. Prerequisites, tool versions, and lab safety

### 3.1 Record installed tools

Create a lab workspace outside any production repository:

```bash
mkdir -p "$HOME/m06-unit4-lab/evidence"
cd "$HOME/m06-unit4-lab"
{
  date -Is
  helm version
  kubectl version --client
  kind version
  python3 --version
  make --version
} > versions.txt 2>&1
cat versions.txt
```

If optional tools are installed, record their versions too. For a disposable cluster, capture the server version after checking the current context:

```bash
kubectl config current-context
kubectl version
```

Output varies by tool version. Do not claim the local `kubectl` client version equals the cluster server version. Do not include tokens, secret values, private credentials, or sensitive rendered configuration in evidence.

### 3.2 Safe lab rules

- Use a dedicated, disposable `kind` cluster and namespace for cluster-dependent tests.
- Before every cluster mutation, run `kubectl config current-context` and verify it is the cluster created for this lab. Stop if uncertain.
- Never use production credentials, production data, or production contexts.
- Use placeholder images only for render-only tests. For install/upgrade tests, build or select a known, approved image that is actually available to the cluster.
- Keep evidence in a lab directory; redact secrets before saving or sharing.
- Do not use `|| true` to mask required CI failures. Optional-tool absence must be an explicit documented profile or a clear error.
- Clean up only resources created by the lab.

### 3.3 Boundaries

Units 1–3 cover manifests, chart templates/values, hooks, and dependencies. Unit 4 owns systematic testing, compatibility, SemVer, release gates, and upgrade testing. Unit 5 covers Kustomize; Unit 6 compares Helm and Kustomize; Unit 7 covers chart distribution, OCI, provenance, and signing; Unit 8 covers operators and CRDs. M02 covers CI workflow hygiene; M03 covers Kubernetes behavior and deprecations; M08 covers GitOps; M09 covers secret lifecycle; M12 covers image/artifact supply-chain security.

## 4. Concept map and testing ladder

```text
                  Change to chart / values / dependency
                                |
                                v
                    1. helm lint (cluster-free)
                                |
                                v
                 2. values-schema positive/negative tests
                                |
                                v
                   3. render all environment values
                                |
                                v
             4. Kubernetes schema validation (kubeconform)
                                |
                                v
           5. server-side dry-run against disposable cluster
                                |
                                v
                   6. install test on throwaway cluster
                                |
                                v
                 7. upgrade N -> N+1 and rollback review
                                |
                                v
                   8. policy checks on rendered output
                                |
                                v
                   9. baseline/proposed diff review
                                |
                                v
                10. optional config/image scan and approval
```

Stages 1–4 and most of 8–10 can be cluster-free. Server-side validation, installation, upgrade, and runtime smoke tests need an API server or a cluster. The ordering is a teaching ladder, not a requirement that CI run every job serially; independent deterministic checks can run in parallel if their evidence and failure propagation remain clear.

| Stage | Defect classes caught | Example command | Cluster required? | Limitations |
|---|---|---|---:|---|
| `helm lint` | Chart structure, template-related problems and some warnings | `helm lint ./chart` | No | Not a full API, policy, runtime, or upgrade test |
| Values schema | Invalid types, required fields, enums; unknown keys if schema rejects them | `helm template demo ./chart -f bad-values.yaml` | No | Only enforces constraints encoded in the schema |
| Render checks | Wrong names, labels, selectors, ports, values, image refs, missing resources | `helm template demo ./chart -f values-prod.yaml` | No | Does not execute hooks or contact the API server |
| `kubeconform` | Many Kubernetes object-schema errors for chosen version | `kubeconform ... rendered.yaml` | No | CRDs need schemas; policy/runtime/cross-resource logic may be outside scope |
| Server-side dry-run | Target API validation and some admission failures | `kubectl apply --dry-run=server -f rendered.yaml` `[VERIFY]` | Yes | Does not persist objects or prove controllers will make them healthy |
| Install test | Admission, scheduling, startup, service reachability, install hooks | `helm install ...` | Yes | Does not prove upgrade behavior |
| Upgrade test | Immutable-field, lifecycle, compatibility and existing-state failures | `helm upgrade ...` | Yes | Test fixture may not represent all production state |
| Policy checks | Explicit security/org rules such as no `latest` or privileged containers | Custom script / Conftest | No | Rules can be incomplete or have false positives |
| Rendered diff | Unexpected behavior/configuration changes | `diff -u old.yaml new.yaml` | No | Raw diffs can be noisy; reviewer must assess impact |
| Config/image scan | Known configuration issues and image findings | Trivy or approved scanner | Usually no for config | Does not prove provenance or absence of all vulnerabilities |

## 5. Level 1 — Beginner: what each test stage catches

### 5.1 Why charts need tests

Chart defects can occur at multiple layers:

- **Metadata:** invalid or inconsistent `Chart.yaml` fields.
- **Template/YAML:** malformed templates or rendered YAML.
- **Values contract:** invalid types, missing required settings, or misspelled keys.
- **Kubernetes API:** unknown fields, invalid API versions, invalid object shapes.
- **Cross-resource behavior:** Service selector no longer matches Pod labels; an Ingress points to a missing Service.
- **Deprecation/compatibility:** an API is removed in a supported Kubernetes version.
- **Policy/security:** privileged containers, `hostPath`, root execution, missing resource budgets, or mutable image tags.
- **Environment configuration:** production accidentally enables a development dependency or sets replicas to zero.
- **Install/runtime:** admission denial, image pull failures, unschedulable Pods, failing probes.
- **Upgrade:** immutable selector changes, changed resource names, hooks that behave differently, or values reuse/reset incompatibility.
- **Behavioral regression:** a changed default, dropped security setting, or altered network policy.
- **Dependencies:** subchart defaults, names, RBAC, or images change.
- **Version compatibility:** chart requires a newer Kubernetes version than the cluster supports.

`helm lint` is valuable because it is cheap and fast. It is not proof that the chart is production-ready. A green result must be followed by tests that target the relevant failure modes.

### 5.2 `helm lint`

Basic usage:

```bash
helm lint ./scoring-chart
```

If your installed version supports additional strictness options, check `helm lint --help` and the matching official documentation before adding them to CI. Typical lint output may include errors and warnings about chart structure or templates; exact messages are version-dependent.

Lint can detect some chart construction problems, but it does not prove that all values are valid under every environment, that the Kubernetes API accepts every rendered object, that cluster admission policy passes, that selectors match, that Pods become Ready, or that an upgrade succeeds. Treat warnings as review items, not noise to suppress reflexively.

### 5.3 Values schema and negative testing

Helm can use a chart’s `values.schema.json` to validate values supplied to the chart. A schema can enforce types, required keys, enums, numeric bounds, and other JSON Schema constraints supported by the installed Helm version. Unknown keys are not necessarily rejected unless the schema is designed to reject them—for example, with `additionalProperties: false` at appropriate object levels. JSON Schema draft support is `[VERSION-SENSITIVE][VERIFY]`; check Helm’s documentation and the schema’s declared `$schema`.

Illustrative schema fragment:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "replicaCount": {"type": "integer", "minimum": 1},
    "image": {
      "type": "object",
      "properties": {
        "repository": {"type": "string", "minLength": 1},
        "digest": {"type": "string"}
      },
      "required": ["repository"],
      "additionalProperties": false
    }
  },
  "required": ["replicaCount", "image"],
  "additionalProperties": false
}
```

This is a compact example, not a full schema for every value used in this chapter. If the schema has no `additionalProperties: false` at the right level, a typo such as `replicaCounnt` may be ignored instead of rejected. Always test both valid and invalid values:

```bash
helm template scoring ./scoring-chart -f values-dev.yaml
helm template scoring ./scoring-chart -f bad-values-typo.yaml
```

The negative test should fail for the intended reason. A nonzero result alone is insufficient if the chart failed for an unrelated template error; inspect the message and keep a regression fixture.

### 5.4 Render checks

Render every supported environment values file:

```bash
helm template scoring ./scoring-chart -f values-dev.yaml > rendered-dev.yaml
helm template scoring ./scoring-chart -f values-staging.yaml > rendered-staging.yaml
helm template scoring ./scoring-chart -f values-prod.yaml > rendered-prod.yaml
```

Inspect resource kinds/counts, names, labels, selector/template-label consistency, ports, probes, security context, resources, image references, optional resources, RBAC, NetworkPolicies, and hook annotations. Save the rendered manifests as evidence. Rendering does not execute hooks, call the Kubernetes API server, or prove application health.

A deterministic render assertion should encode an intended contract. For example, a Service must select the same labels that the Deployment template applies. That is a cross-resource invariant and should be checked explicitly; generic Kubernetes schema validation does not necessarily enforce it.

## 6. Level 2 — Intermediate: rendering, schemas, unit tests, and SemVer

### 6.1 `kubeconform` and API schema validation

Use `kubeconform` or an equivalent validator to check rendered YAML against the intended Kubernetes version. Exact flags and schema-source behavior are `[VERIFY]`; check the installed version’s help and official project documentation before copying commands into a pipeline.

An illustrative command shape is:

```bash
kubeconform -strict -summary -kubernetes-version "$KUBERNETES_VERSION" rendered-prod.yaml
```

Verify that the installed release supports these flags and the expected version syntax. Choose the Kubernetes version(s) that the chart officially supports, not simply the version installed on the developer laptop. Standard Kubernetes resource schemas and custom-resource schemas are separate concerns. For CRDs, use a trusted schema source or an explicitly configured local schema set; verify the exact `-schema-location` behavior for your installed version.

Schema sources may be downloaded or cached. Consider source trust, offline operation, reproducibility, and whether CI can access the schema source. `kubeconform` cannot prove admission policy acceptance, runtime health, controller reconciliation, application logic, image provenance, or every cross-resource invariant.

### 6.2 Server-side dry-run

A server-side dry-run submits a request to the API server for validation/admission without persisting the object. It can expose target-cluster schema and admission differences that local rendering cannot. It still does not prove scheduling, rollout, hook execution, runtime behavior, or application health.

Before using a disposable cluster:

```bash
kubectl config current-context
kubectl version
```

An illustrative command is:

```bash
kubectl apply --dry-run=server -f rendered-prod.yaml
```

Verify syntax and semantics against the installed `kubectl` version. Use only the intended disposable context and a manifest set that is safe to submit for validation. Do not claim a dry-run mutates resources; equally, do not claim it validates everything a real installation will encounter.

### 6.3 `helm test` and test hooks

A chart can define a test Pod or Job using the `helm.sh/hook: test` annotation. A smoke test might call the service health endpoint from inside the cluster. `helm test` runs the chart’s test hooks for an installed release.

Illustrative Job template:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-smoke-test
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
          command:
            - sh
            - -c
            - curl --fail --silent --show-error http://scoring-api:8000/health
```

This snippet assumes the Service name, port, and endpoint are correct and that the image has the stated shell and `curl`; verify these in the selected image and chart. Pin a real, approved digest for a production pipeline. Do not invent one.

Run:

```bash
helm test scoring -n scoring-lab
```

Check `helm test --help` and the installed Helm docs before using `helm test --logs`; this flag is `[VERIFY]` because availability and behavior may vary by version. Test hooks need a bounded timeout, cleanup policy, clear assertions, and evidence retention. A successful smoke test proves only that its assertion passed in that environment. It does not replace integration, load, security, or data-correctness testing.

### 6.4 Unit testing: plugin and portable fallback

The `helm-unittest` plugin can assert rendered chart behavior using declarative test cases. Its install procedure, test-file conventions, and assertion syntax must be verified against the official project documentation and pinned to an approved version. Plugins are executable supply-chain dependencies; review source, version, permissions, and update policy.

A common convention is to keep test definitions under a chart `tests/` directory, but verify this convention and syntax against the version you install. Do not make the portable lab depend on an unverified plugin.

Portable fallback using Python standard library and rendered YAML text:

```python
# check_render.py
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
required = [
    "kind: Deployment",
    "kind: Service",
    "allowPrivilegeEscalation: false",
    "readOnlyRootFilesystem: true",
]
missing = [item for item in required if item not in text]
if missing:
    print("FAIL: missing required rendered fragments:", ", ".join(missing))
    raise SystemExit(1)
print("PASS: required rendered fragments found")
```

Run it after rendering:

```bash
python3 check_render.py rendered-dev.yaml
```

This fallback is intentionally simple and is not a YAML parser. It can produce false positives if a required string appears in the wrong resource or comments. For stronger assertions, use a reviewed YAML parser such as PyYAML if installed, or write pytest assertions that load YAML documents and inspect resource kinds and fields. Optional dependencies must be recorded and pinned by the project’s normal dependency process.

### 6.5 `chart-testing` (`ct`)

Chart-testing is useful in repositories with multiple charts because it can identify changed charts and run lint/install workflows. The syllabus includes `ct lint`, `ct install`, `ct list-changed`, and `ct install --upgrade`; exact syntax, flags, configuration requirements, and whether `--upgrade` is supported by the installed version must be verified `[VERIFY]` against the official project documentation.

| Tool/command | Purpose | Environment | Cluster required? | Limitation |
|---|---|---|---:|---|
| `ct lint` | Lint changed charts under tool configuration | Multi-chart repository | Usually no | Depends on configuration and chart selection |
| `ct list-changed` | Identify charts changed relative to a base | Git repository | No | Requires a valid base/ref and repository setup |
| `ct install` | Install charts in test cluster | CI or local cluster | Yes | Does not automatically prove all upgrade paths |
| `ct install --upgrade` | Potential install/upgrade workflow | Version-dependent | Yes | Use only if installed version supports the syntax |

Native Helm plus a small shell script is adequate for the zero-budget core lab. Adopt `ct` when its repository-level workflow provides value and the team is willing to maintain its configuration.

### 6.6 Environment values test matrix

A directory such as `ci/values/` or filenames such as `values-dev.yaml` are project conventions, not intrinsic Helm features. Render each supported environment explicitly. Avoid a combinatorial explosion by identifying critical dimensions: environment, optional components, ingress enabled/disabled, persistence, replica ranges, and supported Kubernetes versions. Test every supported combination that changes rendered behavior or risk, and document deliberately unsupported combinations.

### 6.7 Chart `version`, `appVersion`, image reference, and SemVer

- **`Chart.yaml` `version`:** the chart package version; use it to identify the chart contract and follow the team’s SemVer policy.
- **`appVersion`:** informational application version metadata. It is not a substitute for chart `version` and may change independently.
- **Image tag/digest:** identifies the application artifact referenced by the rendered workload. A chart version does not prove which image is deployed unless the chart values/template explicitly establish that relationship.
- **`kubeVersion`:** a chart metadata constraint on supported Kubernetes versions. Validate exact constraint behavior against installed Helm docs.

SemVer defines MAJOR for incompatible API changes, MINOR for backward-compatible functionality, and PATCH for backward-compatible fixes. Chart compatibility depends on the consumer contract, including values, rendered resource names/selectors, defaults, and supported Kubernetes versions.

| Change | Typical classification | Why / caveat |
|---|---|---|
| Remove or rename a documented values key | MAJOR | Existing consumers may fail or change behavior |
| Add a required value with no compatible default | MAJOR | Existing values no longer satisfy the contract |
| Add optional resource disabled by safe default | MINOR | Backward-compatible if defaults preserve behavior |
| Fix a bug without changing documented behavior | PATCH | Confirm the fix does not alter expected output unexpectedly |
| Change default replica count | Depends—state policy/impact | Can change availability/cost and be breaking operationally |
| Change default security context | Depends—often MAJOR if workloads break; security fix may be urgent | Test workload compatibility and communicate behavior |
| Change Deployment selector or resource names | Usually MAJOR | Selectors can be immutable; clients/ownership may break |
| Raise minimum Kubernetes version | MAJOR if it drops supported clusters | Update `kubeVersion`, support matrix, and migration notes |
| Change only `appVersion` | Often PATCH or release-policy-specific | Chart contract may be unchanged; app behavior may not be |
| Change image digest/default tag policy | Depends on behavior and compatibility | Artifact change can materially alter runtime behavior |

Do not classify by diff size. A one-line default change can be more disruptive than a large internal template refactor. `.Capabilities` lets templates inspect Helm/Kubernetes capabilities, but exact behavior and test controls are `[VERSION-SENSITIVE][VERIFY]`. Test capability-dependent branches against the target support matrix.

## 7. Level 3 — Advanced: upgrade tests, diff gates, policy, and compatibility

### 7.1 Upgrade testing: install N → upgrade N+1

A repeatable upgrade test should:

1. Render and review chart N with representative values.
2. Install N into a disposable cluster and capture status/history.
3. Verify readiness and any test hook.
4. Render N+1 with the same and representative updated values.
5. Review the diff before applying.
6. Upgrade the release.
7. Verify Deployment readiness, Service selectors/ports, hooks, logs, and application smoke tests.
8. If the fixture actually uses storage, verify PVC identity and data persistence; do not claim persistence was tested when there is no PVC.
9. Test rollback where appropriate and document what cannot be reversed.
10. Save evidence before cleanup.

Install-only tests miss immutable-field changes, changed resource names, values reuse/reset behavior, upgrade hooks, and compatibility with live state. A Deployment selector change is a classic upgrade risk because selectors have immutability constraints. Prefer stable selectors and test changes against an existing release.

Example commands, assuming a disposable cluster and an actual chart fixture:

```bash
kubectl config current-context
helm install scoring ./chart-v1 -n scoring-lab --create-namespace
helm status scoring -n scoring-lab
helm history scoring -n scoring-lab
helm upgrade scoring ./chart-v2 -n scoring-lab --timeout 120s
helm status scoring -n scoring-lab
helm history scoring -n scoring-lab
```

Do not run against a production context. Verify timeout and any optional flags against installed Helm docs. If upgrade fails, capture events/logs before cleanup.

### 7.2 Rendered-diff gates

Render baseline and proposed revisions using the same Helm version and values files:

```bash
helm template scoring ./baseline-chart -f values-prod.yaml > baseline-prod.yaml
helm template scoring ./candidate-chart -f values-prod.yaml > candidate-prod.yaml
diff -u baseline-prod.yaml candidate-prod.yaml
```

Repeat for dev, staging, and every supported consumer values fixture. Raw text diffs are easy to implement but may be noisy due to document ordering or whitespace. Semantic diff tooling can improve signal, but do not normalize away meaningful fields. Every normalization rule is itself a potential blind spot.

| Rendered change | Risk class | Review action |
|---|---|---|
| Deployment selector or Pod labels | High | Require explicit compatibility analysis and upgrade test |
| Security context/capabilities removed | High | Block unless approved security exception |
| Resource requests/limits or probes removed | High | Require workload and SRE review |
| Image tag/digest changed | High | Verify artifact, changelog, scan/provenance process |
| Replicas unexpectedly become zero | High | Block or require explicit scale-to-zero intent |
| Service name/port/selector changed | High | Check all consumers and service discovery |
| Ingress hostname / HTTPRoute change | High | Check traffic and DNS/certificate assumptions |
| NetworkPolicy/RBAC change | High | Security review and reachability tests |
| Resource deleted | High | Determine whether ownership/data/traffic is affected |
| Immutable field changed | High | Test upgrade path; plan replacement/migration if necessary |
| New cluster-scoped object | High | Review ownership, permissions, blast radius |
| Annotation/documentation-only change | Often lower | Confirm no controller behavior is attached to annotation |

A diff gate should fail or require explicit review when high-risk patterns appear. It should never auto-approve a risky change just because the diff was generated.

### 7.3 Values compatibility and golden tests

Keep sanitized, representative old values fixtures and render them against the candidate chart. This checks whether the new chart still accepts supported consumer configurations. Golden manifests capture expected render output and can detect unexpected changes, but snapshots become brittle if every harmless label/order change requires updates.

Use a disciplined golden-file process:

1. Generate output from a known chart/tool version.
2. Review the snapshot as a contract, not as unquestionable truth.
3. When output changes, inspect semantic impact.
4. Update golden files only with a linked change rationale and reviewer approval.
5. Keep targeted assertions for high-risk invariants even if a golden snapshot exists.

A golden test proves output matches a baseline; it does not prove the baseline was correct or production-safe.

### 7.4 Policy checks on rendered manifests

A self-contained policy script can reject `:latest`, privileged containers, hostPath volumes, missing resource budgets, and missing non-root configuration. It should inspect YAML structure for production use; simple `grep` is acceptable as a lab demonstration only if its limitations are documented.

Example shell policy gate for the controlled lab:

```bash
#!/usr/bin/env bash
set -euo pipefail
manifest="${1:?usage: policy.sh rendered.yaml}"
fail=0

if grep -Eq 'image:[[:space:]]*[^#[:space:]]+:latest([[:space:]]|$)' "$manifest"; then
  echo "FAIL: mutable latest image tag found"
  fail=1
fi
if grep -Eq 'privileged:[[:space:]]*true' "$manifest"; then
  echo "FAIL: privileged container found"
  fail=1
fi
if grep -Eq 'hostPath:' "$manifest"; then
  echo "FAIL: hostPath volume found"
  fail=1
fi
if [ "$fail" -ne 0 ]; then exit 1; fi
echo "PASS: basic text policy checks"
```

This does not robustly prove resource requests/limits or non-root settings because indentation and YAML structure vary. A production policy should parse YAML or use a maintained policy engine. Conftest/OPA, kube-linter, kube-score, Polaris, Kyverno CLI, and Trivy can help, but check their official documentation for installation and syntax. Exact Trivy configuration-scanning flags are `[VERIFY]`; do not copy a command into CI without checking the installed version’s help.

| Defect | Appropriate gate | Accuracy note |
|---|---|---|
| Misspelled values key | Schema with unknown-key rejection or explicit assertion | `helm lint` alone is not guaranteed to catch it |
| Selector/template-label mismatch | Render assertion or install/upgrade test | Generic object schema validation may not catch cross-resource mismatch |
| `:latest` image | Explicit policy rule | Basic lint may allow it |
| `privileged: true` | Explicit security policy | A syntactically valid manifest can be insecure |
| Deprecated API version | Target-version schema/deprecation rule and server validation | `kubeconform` does not automatically reject every deprecated API in every setup |

Document exceptions with owner, reason, expiry date, and compensating controls. Policy tools can disagree or produce false positives; exceptions should be narrow and reviewable, not blanket suppressions.

### 7.5 Image reference extraction and supply-chain handoff

Extract image references from rendered manifests so the pipeline can send them to an approved image scanner. A text grep can help in the lab, but production extraction should parse YAML and inspect containers, initContainers, and relevant workload kinds. Enforce a policy such as digest-pinned images or an explicitly governed tag scheme.

A syntactically valid digest reference does not prove the image publisher is trusted, that the image is vulnerability-free, or that it matches source code. Signing/provenance and publishing are Unit 7/M12 responsibilities.

### 7.6 Kubernetes API compatibility and deprecations

Define an explicit support matrix for Kubernetes minor versions. Example only:

| Chart release line | Oldest supported cluster | Newest tested cluster | Status |
|---|---|---|---|
| `1.x` | `1.N` | `1.N+2` | Illustrative only; replace with actual project policy |
| Candidate | Oldest supported minor | Newest supported minor | Run schema, server, install, and upgrade checks |

Do not leave `N` values as production documentation. Choose real versions based on the project’s support policy and currently available cluster versions. `Chart.yaml` `kubeVersion` expresses a compatibility constraint; verify its accepted constraint syntax and behavior with the installed Helm version. `.Capabilities` may influence template branches; test all supported branches and do not rely on the developer’s local cluster as the compatibility contract.

Local schema validation and a live API server can differ because the schema source, enabled APIs, admission policies, and CRD installation state differ. Custom resources require their CRD schemas or another explicit validation strategy. Deprecated API detection should be a named gate: target-version schema validation, explicit policy, and/or server validation, not an assumption that every tool detects every deprecation.

### 7.7 Documentation and release automation

Document every public value with its type, default, purpose, valid values, and security implications. Treat `values.schema.json` as an executable contract, but keep README examples and schema synchronized. Changelogs should state user-visible behavior, compatibility, migration steps, and known limitations.

Conventional Commits, automated changelog generation, and chart-releaser tools can fit an M02 release workflow; they are not substitutes for impact analysis. Verify tool commands and version-specific configuration before adopting them. Ensure chart package versions are unique: do not silently republish different content under an already released chart version. Follow Unit 7 for publication and provenance.

A values deprecation policy should define how many releases warn, how consumers are notified, what telemetry/feedback is used to assess adoption, and when a key can be removed. Remove a documented public key only in a breaking release when appropriate, with migration guidance. There is no universal deprecation timeline; define it in team policy.

## 8. Level 4 — Expert: CI architecture and chart lifecycle governance

### 8.1 Production CI sequence

A production-oriented pipeline should include:

1. Checkout with least privilege and immutable action references.
2. Capture tool versions.
3. `helm lint`.
4. Schema-positive and schema-negative tests.
5. Render all supported environment values.
6. Kubernetes schema validation for supported versions.
7. Unit assertions via approved plugin or portable fallback.
8. Policy checks.
9. Rendered diff against baseline for each environment.
10. Optional config/image scanning.
11. Install test on disposable `kind`.
12. Upgrade test from a prior chart version.
13. Smoke test and evidence capture.
14. Upload only scrubbed artifacts and summarize failures.

The local script below is the portable core. It deliberately fails with an actionable message when required tools are absent. Cluster targets require an existing, dedicated test cluster and an explicit context allowlist. Replace the fixture chart with your actual chart only after reviewing the values and image assumptions.

### 8.2 Complete local CI script

The lab fixture tree used below is:

```text
chart-ci-lab/
├── Makefile
├── ci.sh
├── policy.sh
├── check_render.py
├── chart/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values.schema.json
│   └── templates/
│       ├── _helpers.tpl
│       ├── deployment.yaml
│       └── service.yaml
├── values/
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── bad-values-typo.yaml
└── baseline/
    └── rendered-prod.yaml
```

`Makefile`:

```makefile
.PHONY: lint schema render-all kubeconform unittest policy install-test upgrade-test diff ci

lint:
	./ci.sh lint

schema:
	./ci.sh schema

render-all:
	./ci.sh render-all

kubeconform:
	./ci.sh kubeconform

unittest:
	./ci.sh unittest

policy:
	./ci.sh policy

install-test:
	./ci.sh install-test

upgrade-test:
	./ci.sh upgrade-test

diff:
	./ci.sh diff

ci:
	./ci.sh ci
```

`ci.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHART="${CHART_DIR:-$ROOT/chart}"
VALUES_DIR="${VALUES_DIR:-$ROOT/values}"
EVIDENCE="${EVIDENCE_DIR:-$ROOT/evidence}"
BASELINE_DIR="${BASELINE_DIR:-$ROOT/baseline}"
KUBERNETES_VERSION="${KUBERNETES_VERSION:-}"
EXPECTED_CONTEXT="${EXPECTED_CONTEXT:-}"
NAMESPACE="${NAMESPACE:-chart-ci-lab}"
RELEASE="${RELEASE:-scoring-ci}"

mkdir -p "$EVIDENCE"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: required command '$1' is missing; install and verify it first." >&2
    exit 127
  }
}

capture_versions() {
  {
    date -Is
    helm version
    kubectl version --client
    kind version
    if command -v kubeconform >/dev/null 2>&1; then kubeconform -v; fi
    python3 --version
  } > "$EVIDENCE/versions.txt" 2>&1
}

safe_context() {
  need kubectl
  current="$(kubectl config current-context)"
  echo "Current Kubernetes context: $current"
  if [[ -z "$EXPECTED_CONTEXT" ]]; then
    echo "ERROR: set EXPECTED_CONTEXT to the exact disposable lab context." >&2
    exit 2
  fi
  if [[ "$current" != "$EXPECTED_CONTEXT" ]]; then
    echo "ERROR: context mismatch; expected '$EXPECTED_CONTEXT', got '$current'." >&2
    exit 2
  fi
}

render_all() {
  need helm
  shopt -s nullglob
  files=("$VALUES_DIR"/*.yaml)
  if (( ${#files[@]} == 0 )); then
    echo "ERROR: no values YAML files found in $VALUES_DIR" >&2
    exit 2
  fi
  for f in "${files[@]}"; do
    name="$(basename "$f" .yaml)"
    echo "Rendering $name"
    helm template "$RELEASE" "$CHART" -f "$f" > "$EVIDENCE/rendered-$name.yaml"
  done
}

run_lint() {
  need helm
  helm lint "$CHART" | tee "$EVIDENCE/helm-lint.txt"
}

run_schema() {
  need helm
  # Positive schema test: every supported environment must render.
  render_all
  # Negative schema test: this fixture must be rejected by the chart schema.
  if helm template "$RELEASE" "$CHART" -f "$ROOT/bad-values-typo.yaml" \
      > "$EVIDENCE/schema-negative.stdout" 2> "$EVIDENCE/schema-negative.stderr"; then
    echo "ERROR: malformed values unexpectedly passed schema validation." >&2
    exit 1
  fi
  echo "PASS: malformed values rejected; inspect schema-negative.stderr for the expected reason."
}

run_kubeconform() {
  need kubeconform
  if [[ -z "$KUBERNETES_VERSION" ]]; then
    echo "ERROR: set KUBERNETES_VERSION to a supported target version." >&2
    exit 2
  fi
  for f in "$EVIDENCE"/rendered-*.yaml; do
    [[ -f "$f" ]] || continue
    kubeconform -strict -summary -kubernetes-version "$KUBERNETES_VERSION" "$f"
  done
}

run_unittest() {
  # Portable assertion fallback. No plugin is silently assumed.
  need python3
  for f in "$EVIDENCE"/rendered-*.yaml; do
    [[ -f "$f" ]] || continue
    python3 "$ROOT/check_render.py" "$f"
  done
}

run_policy() {
  need bash
  for f in "$EVIDENCE"/rendered-*.yaml; do
    [[ -f "$f" ]] || continue
    "$ROOT/policy.sh" "$f"
  done
}

run_diff() {
  render_all
  for candidate in "$EVIDENCE"/rendered-*.yaml; do
    [[ -f "$candidate" ]] || continue
    name="${candidate##*/rendered-}"
    baseline="$BASELINE_DIR/rendered-$name"
    if [[ ! -f "$baseline" ]]; then
      echo "ERROR: missing baseline $baseline; create and review an initial baseline." >&2
      exit 2
    fi
    diff -u "$baseline" "$candidate" > "$EVIDENCE/diff-$name" || {
      rc=$?
      if [[ "$rc" -eq 1 ]]; then
        echo "REVIEW REQUIRED: differences found for $name; see $EVIDENCE/diff-$name"
      else
        exit "$rc"
      fi
    }
  done
}

run_install_test() {
  need helm
  safe_context
  helm install "$RELEASE" "$CHART" -n "$NAMESPACE" --create-namespace --wait --timeout 120s
  helm status "$RELEASE" -n "$NAMESPACE" | tee "$EVIDENCE/install-status.txt"
  kubectl get deploy,pods,svc -n "$NAMESPACE" | tee "$EVIDENCE/install-resources.txt"
}

run_upgrade_test() {
  need helm
  safe_context
  helm upgrade "$RELEASE" "$CHART" -n "$NAMESPACE" --wait --timeout 120s
  helm status "$RELEASE" -n "$NAMESPACE" | tee "$EVIDENCE/upgrade-status.txt"
  helm history "$RELEASE" -n "$NAMESPACE" | tee "$EVIDENCE/upgrade-history.txt"
  kubectl get deploy,pods,svc -n "$NAMESPACE" | tee "$EVIDENCE/upgrade-resources.txt"
}

run_ci() {
  capture_versions
  run_lint
  run_schema
  render_all
  run_kubeconform
  run_unittest
  run_policy
  run_diff
  run_install_test
  run_upgrade_test
}

case "${1:-}" in
  lint) run_lint ;;
  schema) run_schema ;;
  render-all) render_all ;;
  kubeconform) run_kubeconform ;;
  unittest) run_unittest ;;
  policy) run_policy ;;
  install-test) run_install_test ;;
  upgrade-test) run_upgrade_test ;;
  diff) run_diff ;;
  ci) run_ci ;;
  *)
    echo "Usage: $0 {lint|schema|render-all|kubeconform|unittest|policy|install-test|upgrade-test|diff|ci}" >&2
    exit 2
    ;;
esac
```

Make the scripts executable:

```bash
chmod +x ci.sh policy.sh
```

Important: this portable script assumes a chart fixture and baseline exist, and that a disposable cluster is already running for install/upgrade. It does not create or delete clusters automatically. It fails if `EXPECTED_CONTEXT` is not set for cluster targets. The `diff` target reports differences for human review; in a release pipeline, configure risk-aware review/approval rather than treating any diff as automatically safe. Because a text diff is not semantic, use the risk table in Section 7.2.

`check_render.py`:

```python
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
required = ["kind: Deployment", "kind: Service", "allowPrivilegeEscalation: false"]
missing = [item for item in required if item not in text]
if missing:
    print(f"FAIL: {sys.argv[1]} is missing: {', '.join(missing)}")
    raise SystemExit(1)
print(f"PASS: {sys.argv[1]} contains required fragments")
```

`policy.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
file="${1:?usage: policy.sh rendered.yaml}"
fail=0
if grep -Eq 'image:[[:space:]]*[^#[:space:]]+:latest([[:space:]]|$)' "$file"; then
  echo "FAIL: latest image tag found in $file"; fail=1
fi
if grep -Eq 'privileged:[[:space:]]*true' "$file"; then
  echo "FAIL: privileged container found in $file"; fail=1
fi
if grep -Eq 'hostPath:' "$file"; then
  echo "FAIL: hostPath found in $file"; fail=1
fi
if [[ "$fail" -ne 0 ]]; then exit 1; fi
echo "PASS: basic policy checks for $file"
```

The simple policy script is intentionally a teaching fallback; production rules should parse YAML structure and validate resource budgets, non-root execution, capabilities, and image policy across every container and init container. Do not present grep as a complete security scanner.

### 8.3 Minimal fixture chart and values

`chart/Chart.yaml`:

```yaml
apiVersion: v2
name: scoring-chart
description: Self-contained chart testing lab fixture
type: application
version: 0.1.0
appVersion: "1.0.0"
kubeVersion: ">=1.27.0-0"
```

The `kubeVersion` constraint is illustrative. Replace it with the actual supported matrix and verify Helm’s constraint syntax for the installed version.

`chart/values.yaml`:

```yaml
replicaCount: 1
image:
  repository: example.invalid/scoring-api
  tag: "REPLACE_WITH_APPROVED_TAG"
  digest: ""
service:
  port: 8000
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
```

`chart/values.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "replicaCount": {"type": "integer", "minimum": 1},
    "image": {
      "type": "object",
      "properties": {
        "repository": {"type": "string", "minLength": 1},
        "tag": {"type": "string"},
        "digest": {"type": "string"}
      },
      "required": ["repository"],
      "additionalProperties": false
    },
    "service": {
      "type": "object",
      "properties": {"port": {"type": "integer", "minimum": 1, "maximum": 65535}},
      "required": ["port"],
      "additionalProperties": false
    },
    "resources": {"type": "object"},
    "securityContext": {
      "type": "object",
      "properties": {
        "runAsNonRoot": {"type": "boolean"},
        "allowPrivilegeEscalation": {"type": "boolean"},
        "readOnlyRootFilesystem": {"type": "boolean"}
      },
      "required": ["runAsNonRoot", "allowPrivilegeEscalation", "readOnlyRootFilesystem"],
      "additionalProperties": false
    }
  },
  "required": ["replicaCount", "image", "service", "resources", "securityContext"],
  "additionalProperties": false
}
```

`chart/templates/_helpers.tpl`:

```gotemplate
{{- define "scoring.name" -}}
{{- .Chart.Name -}}
{{- end -}}
{{- define "scoring.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
```

`chart/templates/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "scoring.fullname" . }}
  labels:
    app.kubernetes.io/name: {{ include "scoring.name" . }}
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ include "scoring.name" . }}
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ include "scoring.name" . }}
        app.kubernetes.io/instance: {{ .Release.Name }}
    spec:
      containers:
        - name: api
          image: {{- if .Values.image.digest }} {{ printf "%s@%s" .Values.image.repository .Values.image.digest | quote }}{{- else }} {{ printf "%s:%s" .Values.image.repository .Values.image.tag | quote }}{{- end }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 2
            periodSeconds: 5
```

`chart/templates/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "scoring.fullname" . }}
  labels:
    app.kubernetes.io/name: {{ include "scoring.name" . }}
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: {{ include "scoring.name" . }}
    app.kubernetes.io/instance: {{ .Release.Name }}
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: http
```

Environment values:

`values/dev.yaml`:

```yaml
replicaCount: 1
image:
  repository: example.invalid/scoring-api
  tag: "REPLACE_WITH_APPROVED_TAG"
  digest: ""
service:
  port: 8000
```

`values/staging.yaml`:

```yaml
replicaCount: 2
image:
  repository: example.invalid/scoring-api
  tag: "REPLACE_WITH_APPROVED_TAG"
  digest: ""
service:
  port: 8000
```

`values/prod.yaml`:

```yaml
replicaCount: 3
image:
  repository: example.invalid/scoring-api
  tag: "REPLACE_WITH_APPROVED_TAG"
  digest: ""
service:
  port: 8000
```

`bad-values-typo.yaml`:

```yaml
replicaCounnt: 2
```

This fixture is for rendering and test design. Its placeholder image cannot be expected to run. For install/upgrade labs, replace it with an approved test image that actually exposes `/health`, and verify it is available to the `kind` cluster.

`baseline/rendered-prod.yaml` must be generated once from a reviewed baseline and committed to the lab’s own evidence/workspace. Do not invent baseline contents or auto-approve its first generation.

### 8.4 CI workflow architecture

A GitHub Actions workflow should use least-privilege `permissions`, pinned actions by full immutable commit SHA, explicit tool versions, and a disposable Kubernetes-version matrix aligned with the support policy. Do not copy an unverified action SHA from an example. If you add a workflow, replace every `[VERIFY: replace with a reviewed immutable action SHA]` placeholder with a reviewed SHA from the action maintainer and record the selected version. The local `Makefile`/`ci.sh` remains the portable source of truth.

A matrix should cover the oldest and newest minor versions the project actually supports, plus any intermediate versions that have meaningful API/capability differences. More clusters cost CPU, RAM, and time; schedule parallel jobs only if the runner has sufficient capacity. Never use `continue-on-error` for required quality gates.

### 8.5 Kubernetes-version matrix and flakiness

Test the oldest and newest supported Kubernetes minor versions at minimum when feasible, and add intermediate versions where the chart uses capability-dependent branches or API changes. “Supported” must be a published contract, not a guess based on the developer’s workstation.

Flaky tests often indicate race conditions, weak readiness assumptions, image pull variability, shared state, leaked resources, or arbitrary sleeps. Avoid retrying every failure until green; that hides real defects. Use bounded waits, deterministic fixtures, context isolation, and collect events/logs before cleanup. On a 4 CPU / 8 GB / 30 GB laptop, run one small `kind` cluster at a time and remove images/workspaces only when evidence has been retained.

### 8.6 Consumer-driven contracts

For a shared chart, ask consumers to contribute sanitized, representative values fixtures. Render each fixture on chart changes and check high-risk invariants. Define ownership for fixtures, remove secrets/private endpoints, and document which configurations are supported. Rendering proves only the chart can produce output for that fixture; it does not prove the consumer’s live integration or application behavior.

### 8.7 Organization-level chart standards and EOL

A minimum organization standard should include:

- schema and documented values;
- secure defaults and explicit image policy;
- render checks for all supported environments;
- an explicit Kubernetes support matrix;
- unit/contract assertions;
- policy checks;
- install and upgrade tests;
- rendered diff review;
- SemVer and changelog;
- upgrade notes and recovery guidance;
- owner/support contact and dependency policy;
- deprecation and EOL process.

To deprecate a chart, communicate support status, limit or freeze new features, identify a replacement, publish migration guidance, define a support window, and state when new adoption is blocked. There is no universal timeline; set it according to risk, customer commitments, and organizational policy.

### 8.8 Incident analyses

#### Incident 1: Patch release changed a default and production behavior

**Symptom →** Production replica count, exposure, or resource behavior changes after a patch chart release.  
**Evidence/commands →** Compare the prior and candidate `Chart.yaml`, values defaults, and rendered manifests for production values; inspect changelog and release history.  
**Root cause →** A behavior-changing default was classified as a patch without impact analysis.  
**Mitigation →** Roll forward to a reviewed compatible chart version or restore the previous value explicitly if safe.  
**Regression test →** Render the production values fixture and assert the expected default.  
**Prevention →** Require SemVer classification and rendered diff review for default changes.

#### Incident 2: Missing schema allowed a misspelled values key

**Symptom →** A values override appears to have no effect.  
**Evidence/commands →** Render with the suspect values file; inspect schema and the rendered field. Run a negative fixture with the misspelled key.  
**Root cause →** The schema did not reject unknown keys at the relevant object level.  
**Mitigation →** Correct the key and add a schema rule or explicit assertion.  
**Regression test →** Require the negative values fixture to fail for the intended schema reason.  
**Prevention →** Treat values schema as a contract and test it negatively.

#### Incident 3: CI tested install but not upgrade; selector change broke upgrade

**Symptom →** New chart installs cleanly but upgrade fails against an existing Deployment.  
**Evidence/commands →** Reproduce install N then upgrade N+1 in disposable `kind`; inspect Helm history, events, and selector diff.  
**Root cause →** CI validated only fresh creation and missed immutable-field compatibility.  
**Mitigation →** Restore compatible selector behavior or design a controlled replacement/migration.  
**Regression test →** Add N → N+1 upgrade test and selector invariant assertion.  
**Prevention →** Require upgrade tests for every release candidate.

#### Incident 4: `latest` or privileged container passed lint

**Symptom →** A chart passes lint but violates image or workload security policy.  
**Evidence/commands →** Inspect rendered manifests and run the explicit policy gate.  
**Root cause →** Lint checks syntax/structure, not all organizational security rules.  
**Mitigation →** Pin an approved image and remove privileged settings or record a narrow exception.  
**Regression test →** Plant each defect and verify policy failure.  
**Prevention →** Make policy checks required CI gates.

#### Incident 5: Deprecated API passed render but failed on target cluster

**Symptom →** A manifest renders but target cluster rejects the API kind/version.  
**Evidence/commands →** Validate against the intended Kubernetes version, inspect API deprecation policy, and use server-side dry-run on a disposable matching cluster.  
**Root cause →** Render was mistaken for API compatibility validation.  
**Mitigation →** Replace the deprecated API and test against the supported matrix.  
**Regression test →** Add target-version schema/deprecation and server-validation checks.  
**Prevention →** Publish and enforce the Kubernetes support contract.

#### Incident 6: Old consumer values stop working

**Symptom →** A consumer’s established values file fails or silently changes behavior.  
**Evidence/commands →** Run the old fixture against the candidate chart and inspect schema errors/rendered diff.  
**Root cause →** A public values key was removed, renamed, or reinterpreted without a deprecation path.  
**Mitigation →** Restore compatible mapping or publish a breaking migration with clear instructions.  
**Regression test →** Keep sanitized old values contract fixtures.  
**Prevention →** Deprecate explicitly and remove only under documented compatibility policy.

#### Incident 7: Flaky install test hides a readiness defect

**Symptom →** Reruns alternate between green and red; CI retries eventually pass.  
**Evidence/commands →** Capture Pod events, readiness state, image pull status, and test timestamps before cleanup.  
**Root cause →** Race conditions, fixed sleeps, shared resources, or readiness assumptions.  
**Mitigation →** Remove broad retries; use bounded condition-based waits and isolated state.  
**Regression test →** Run repeated isolated tests and preserve failure evidence.  
**Prevention →** Track flake rate and require an owner for quarantined tests.

#### Incident 8: Render diff removes security context or resource limits

**Symptom →** A template refactor weakens workload controls without a visible functional failure.  
**Evidence/commands →** Compare baseline/candidate renders and inspect Pod/container security and resources fields.  
**Root cause →** Review focused on application behavior, not security invariants.  
**Mitigation →** Restore secure defaults or approve a narrow exception.  
**Regression test →** Add policy assertions for every container and init container.  
**Prevention →** Make security fields explicit and review high-risk rendered diffs.

## 9. SRE lens

| Indicator | Definition | Measurement caveat |
|---|---|---|
| Chart CI pass rate | Successful candidate CI runs / all candidate CI runs in a window | Separate code defects from infrastructure/tool failures |
| Install success rate | Successful install tests / attempted install tests | Does not measure upgrade compatibility |
| Upgrade success rate | Successful upgrade tests / attempted upgrade tests | Depends on fixture coverage and starting version |
| Change failure rate | Releases requiring rollback/hotfix due to chart-related defects / chart releases | Attribution may be disputed; define inclusion rules |
| Time to detect risky diff | Time from candidate render to flagged review finding | Depends on reviewer availability and diff tooling |
| Flaky test rate | Test executions with inconsistent outcomes under equivalent inputs / total comparable executions | Avoid conflating environmental failures with test flakiness |
| Rerun rate | CI jobs rerun after failure / CI jobs started | A high rerun rate can hide weak tests |
| Time to diagnose | Time from failure signal to evidence-backed root cause | Define start/end consistently |

Example metric definition, not a target: over a rolling 30-day window, **upgrade test success rate** = successful upgrade test executions divided by all upgrade test executions with valid test environments. Report environment/tool failures separately and show the sample size. Small samples and changing chart coverage can make percentages misleading; pair them with defect severity and production incidents.

Operational runbook: failure signal → verify commit/tool versions and context → reproduce render → compare baseline/candidate → identify failing stage → capture logs/events → mitigate using a reviewed release/value change → verify health → add a regression test and update the changelog. Keep ephemeral `kind` jobs bounded on the laptop; do not run several resource-heavy clusters in parallel on an 8-GB machine unless measured capacity permits it.

## 10. Security lens

| Threat | Control | Verification evidence | Residual limitation |
|---|---|---|---|
| Secrets in values/rendered files/logs/artifacts | Use synthetic values; redact evidence; scan artifact paths | Review saved outputs and CI logs | Secret detection can miss encoded or transformed data |
| Mutable image tags/unverified references | Digest pinning or explicit governed tag policy | Extract and inspect rendered image references | A digest does not prove publisher trust |
| Privileged/root/capabilities/`hostPath` | Policy checks and secure defaults | Rendered policy output and resource review | Policy rules can miss unusual YAML shapes |
| Missing resource budgets/probes | Require them for applicable workloads | Structured policy/unit assertions | Workload-specific sizing still needs evidence |
| Schema/policy gaps | Negative schema tests and explicit policies | Failure fixtures and test logs | Rules only cover what they encode |
| Malicious plugins/actions | Pin, review, and restrict executable dependencies | Version/SHA inventory and permission review | A reviewed dependency can still be compromised later |
| Overprivileged CI permissions/unpinned actions | Least-privilege workflow permissions and full SHA pinning | Workflow review | Runner compromise remains possible |
| Wrong Kubernetes schema version | Explicit version matrix | Captured tool/target versions | Schema source can lag or differ from cluster behavior |
| Custom-resource schema gaps | Trusted CRD schemas and target-cluster validation | CRD schema source and validation logs | Controllers may impose additional semantic rules |
| Tests target production accidentally | Exact context allowlist and disposable namespaces | Context capture before mutations | Misconfigured credentials/context can still exist |
| Diff normalization hides fields | Preserve meaningful fields; review normalization rules | Raw and semantic diff evidence | Diff review can still miss context-dependent behavior |
| Artifacts retain credentials | Synthetic fixtures, redaction, retention policy | Artifact inspection and access policy | Redaction is not perfect |

`helm lint` passing is not proof of security. Schema validation is not policy validation. Rendered YAML validation is not runtime testing. Policy checks do not prove image provenance. Test success does not prove production behavior for all traffic/data. CI artifacts must be scrubbed of secrets. Plugins and actions are executable supply-chain dependencies.

## 11. Production checklist

- [ ] Tool versions captured, including client and disposable cluster server versions.
- [ ] `helm lint` passes and warnings are reviewed.
- [ ] Schema-positive and schema-negative tests pass for intended reasons.
- [ ] Unknown keys are rejected where typo detection is required.
- [ ] All supported values configurations render.
- [ ] `kubeconform` uses the correct Kubernetes version and trusted CRD schemas where relevant.
- [ ] Server-side dry-run uses the intended disposable context.
- [ ] Unit assertions run using an approved plugin or documented fallback.
- [ ] Policy checks catch `latest`, privileged containers, `hostPath`, and applicable missing controls.
- [ ] Rendered diff reviewed for every supported environment.
- [ ] Install and upgrade tests run against a disposable cluster.
- [ ] Test hooks are exercised where present.
- [ ] Image references comply with tag/digest policy.
- [ ] No secrets appear in outputs, logs, or artifacts.
- [ ] Chart `version` and `appVersion` reviewed independently.
- [ ] SemVer classification and changelog are included.
- [ ] `kubeVersion` and `.Capabilities` behavior is reviewed.
- [ ] Deprecated APIs and supported Kubernetes versions are documented.
- [ ] CI fails closed for required gates.
- [ ] Rollback/recovery and chart EOL policy are documented.

## 12. Hands-on labs

### Lab 1 — Build a local chart CI script/Makefile

**Goal:** Build a repeatable local chart test pipeline with ten named targets.  
**Success criteria:** `lint`, `schema`, `render-all`, `kubeconform`, `unittest`, `policy`, `install-test`, `upgrade-test`, `diff`, and `ci` exist; required failures return nonzero; cluster targets refuse to run unless the current context matches an explicit disposable context.  
**Estimated time:** 3–4 hours.  
**Prerequisites:** Helm, Python 3, Bash, Make; optional `kubeconform`. **Cluster required: No** for core checks; **Yes** for install/upgrade targets.

Use the complete fixture tree and file contents in Section 8.2–8.3. Create the files exactly as shown, then:

```bash
cd "$HOME/m06-unit4-lab/chart-ci-lab"
chmod +x ci.sh policy.sh
helm lint ./chart
./ci.sh schema
./ci.sh render-all
./ci.sh unittest
./ci.sh policy
```

For `kubeconform`, install an approved version and record it. Set a real supported version before running:

```bash
KUBERNETES_VERSION=REPLACE_WITH_SUPPORTED_VERSION ./ci.sh kubeconform
```

Do not leave the placeholder in a real run. For `diff`, generate and review a baseline once, then save it under `baseline/rendered-prod.yaml` and the corresponding dev/staging files. Never treat first-time baseline generation as approval.

For cluster tests, create a disposable cluster and namespace, then set the exact context:

```bash
kind create cluster --name m06-u4-ci
kubectl config current-context
EXPECTED_CONTEXT=kind-m06-u4-ci ./ci.sh install-test
EXPECTED_CONTEXT=kind-m06-u4-ci ./ci.sh upgrade-test
```

This fixture’s image is a placeholder, so install may fail to pull it. Replace it with an approved local test image that exposes `/health`, load it into the named kind cluster, and verify readiness before claiming runtime success. The script intentionally does not create/delete clusters automatically.

**Evidence:** `evidence/versions.txt`, lint output, schema-negative stderr, rendered files, policy output, diff files, Helm history/status, and Kubernetes events/logs. These prove which gates ran and what they reported; they do not prove untested production conditions.

**Cleanup:** Capture evidence, verify the context, uninstall only the lab release and delete only the lab namespace/cluster you created.  
**Common failures:** missing optional tool should produce a clear error; a missing baseline should fail with instructions; context mismatch should stop cluster mutation.  
**Stretch:** Replace the grep-based policy fallback with structured YAML parsing and add assertions for selectors, resources, probes, and non-root settings.

### Lab 2 — Plant and catch five defects

**Goal:** Demonstrate the appropriate gate for five common chart defects.  
**Success criteria:** Each defect fails a specific check or triggers an explicit review gate; the corrected fixture passes the same check.  
**Estimated time:** 2–3 hours.  
**Prerequisites:** Lab 1 fixture. **Cluster required: No** for most checks; optional disposable `kind` for server-side validation.

Copy the fixture to a temporary directory before editing:

```bash
cp -a chart chart-defects
```

Never plant defects in the primary chart. Change one defect at a time, run the relevant gate, record the result, correct it, and rerun.

| Defect | Example | Appropriate gate | Expected result / limitation |
|---|---|---|---|
| Misspelled values key | `replicaCounnt: 2` | Schema with unknown-key rejection | Should fail if the schema rejects unknown top-level keys; `helm lint` alone is not reliable |
| Missing selector label | Remove `app.kubernetes.io/instance` from Pod labels but retain it in selector | Explicit render assertion or install/upgrade test | Generic schema validation may not catch cross-resource mismatch |
| `latest` image tag | `image: example.invalid/scoring-api:latest` | Explicit image policy | Lint may pass; policy should fail |
| Privileged container | `privileged: true` | Explicit security policy | Syntax may be valid; policy should fail |
| Deprecated API version | Replace a resource API with one removed from target Kubernetes | Target-version validation and/or server-side dry-run | `kubeconform` does not automatically catch every deprecation in every configuration |

For the selector defect, a simple Python assertion can check that the Deployment selector keys are present in the Pod template labels; use a YAML parser for a robust implementation. Do not claim the test passes if it only searches for a string anywhere in the manifest.

For the deprecated API defect, select a specific API that is actually removed in the target version you test and verify that status in official Kubernetes deprecation documentation. Do not invent a version/API combination. If you cannot verify the exact combination offline, record it as `[VERIFY]` and use a known test fixture from your supported version matrix.

**Evidence:** For each defect, save the modified snippet, command, exit status, actual output, corrected snippet, and rerun result. Do not fabricate output.  
**Cleanup:** Delete only the temporary `chart-defects` copy after evidence is saved.  
**Common failures:** a negative schema fixture may fail for the wrong reason; ensure the expected failure message points to the typo. A policy script may miss YAML variants; improve it or document the limitation.  
**Stretch:** Add a regression test for each defect to the main fixture and make the CI target fail if any defect reappears.

### Lab 3 — SemVer classification for 10 chart changes

**Goal:** Classify chart changes based on compatibility and consumer impact.  
**Success criteria:** Provide a written classification and rationale for all ten scenarios.  
**Estimated time:** 45–60 minutes.  
**Prerequisites:** Sections 6.7 and 7.7. **Cluster required: No.**

Classify each scenario as MAJOR, MINOR, PATCH, or `Depends—state the policy/impact`.

| # | Change | Model classification | Rationale / release-note requirement |
|---:|---|---|---|
| 1 | Remove or rename a documented values key | MAJOR | Existing consumers may fail or silently change behavior; provide migration mapping and upgrade notes |
| 2 | Add a required value with no safe compatible default | MAJOR | Existing values files no longer satisfy the contract; provide migration steps |
| 3 | Add an optional feature disabled by a safe default | MINOR | Backward-compatible if existing renders remain unchanged; document the new value |
| 4 | Fix a bug without changing documented behavior | PATCH | State the defect and expected correction; test no unintended output change |
| 5 | Change default replica count | Depends—state the policy/impact | Can change availability/cost; classify by actual operational impact and published compatibility contract |
| 6 | Change default security context | Depends—often MAJOR if workloads stop working; security fix may need expedited release | Document runtime effects, exceptions, and required workload changes |
| 7 | Change Deployment selector or resource names | Usually MAJOR | Selectors may be immutable and clients/ownership may break; include upgrade path |
| 8 | Raise minimum supported Kubernetes version | MAJOR if supported clusters are dropped | Update `kubeVersion`, support matrix, and migration notes |
| 9 | Change only `appVersion` | Often PATCH or policy-specific | Chart API may be unchanged, but application behavior can still change; document artifact change |
| 10 | Change image digest or default tag policy | Depends—state the policy/impact | Runtime artifact can change materially; include scan/provenance and rollback notes |

**Evidence:** Save the completed table and a brief release decision record.  
**Cleanup:** None.  
**Common failure:** classifying every small code diff as PATCH. SemVer describes compatibility, not code volume.  
**Stretch:** Review a real chart changelog and classify three past releases, citing the actual rendered/values changes.

## 13. Self-check questions

1. **What does `helm lint` prove?**  
   **Answer:** It checks chart structure and some template/chart issues. **Wrong answer:** “It proves production readiness” ignores API, policy, runtime, and upgrade behavior.

2. **Why reject unknown values keys in the schema?**  
   **Answer:** Otherwise a typo may be ignored rather than rejected. **Wrong answer:** “Helm catches every typo” is not guaranteed.

3. **How do render, `kubeconform`, and server-side dry-run differ?**  
   **Answer:** Render produces YAML; `kubeconform` validates against a selected schema; server-side dry-run asks the target API server/admission chain to validate. **Wrong answer:** none of these alone proves runtime health.

4. **Why are install tests not enough?**  
   **Answer:** Upgrade paths encounter immutable fields, existing state, hooks, and compatibility issues that fresh install misses. **Wrong answer:** a successful install does not establish upgrade safety.

5. **What does `helm test` prove?**  
   **Answer:** The test hook’s assertions passed in that environment. **Wrong answer:** it is not a full integration/load/security guarantee.

6. **How do `version` and `appVersion` differ?**  
   **Answer:** `version` identifies the chart package; `appVersion` is application metadata. **Wrong answer:** changing `appVersion` alone does not automatically version the chart contract.

7. **How should a renamed values key be classified?**  
   **Answer:** Usually MAJOR if it breaks the documented consumer contract. **Wrong answer:** calling it PATCH because the template edit is small ignores compatibility.

8. **Why render diffs for every environment?**  
   **Answer:** Values can alter resources and security posture differently per environment. **Wrong answer:** a dev render does not prove production values render safely.

9. **Why explicitly test for `latest` and privileged settings?**  
   **Answer:** These can be syntactically valid and pass lint. **Wrong answer:** schema/lint is not an organization security policy unless it encodes that policy.

10. **Why should the Kubernetes-version matrix match an explicit support policy?**  
    **Answer:** It defines which clusters the chart claims to support and tests API/capability differences. **Wrong answer:** testing only a developer’s current cluster leaves other supported versions unverified.

## 14. Evidence artifacts

Suggested learner-generated evidence under `~/m06-unit4-lab/evidence/`:

- `versions.txt`
- chart fixture tree and dev/staging/prod values files
- `helm-lint.txt`
- schema-positive and schema-negative output
- `rendered-dev.yaml`, `rendered-staging.yaml`, `rendered-prod.yaml`
- `kubeconform` output and target Kubernetes version
- unit assertion output
- policy-test output
- baseline/proposed rendered diffs
- install/upgrade Helm history and status
- smoke-test output, Job/Pod events and redacted logs
- five-defect test matrix and correction evidence
- SemVer exercise with model answers
- changelog and release decision record
- CI pass/fail summary

These artifacts are expected learner outputs, not files that already exist. Record command, tool version, exit status, and relevant non-sensitive output. Redact credentials, tokens, sensitive endpoints, and data.

## 15. Interview and design-review questions

### 1. Design a reliable testing ladder for a shared Helm chart.

**Model answer:** Start with lint and schema-positive/negative tests, render every supported values fixture, validate against target Kubernetes schemas, run policy and diff checks, then test install and upgrade on disposable clusters. Parallelize deterministic checks where safe, but fail closed on required gates. Keep evidence and review risky diffs. No single stage proves production safety: render does not execute, schema validation does not prove runtime behavior, and install does not prove upgrade compatibility.

### 2. How would you prevent a values typo from reaching production?

**Model answer:** Define a strict values schema with unknown-key rejection where appropriate, maintain positive and negative fixtures, render every supported environment, and add assertions for high-risk fields. A schema can only enforce rules it expresses, and schema draft behavior must be verified for the installed Helm version. Preserve a regression test for the exact typo.

### 3. How would you test an upgrade that changes an immutable selector?

**Model answer:** Render and diff baseline/candidate selectors, then install chart N and upgrade to N+1 in disposable `kind`. Capture Helm history and Kubernetes events. Do not assume an in-place upgrade can mutate an immutable selector; design a compatible selector or a controlled replacement/migration with availability implications. Add a selector invariant and upgrade test.

### 4. How do you classify a chart default change under SemVer?

**Model answer:** Assess the consumer contract and operational effect. A replica/security/image default can alter availability, cost, access, or runtime behavior even when the diff is one line. Classify as PATCH only if backward-compatible under policy; otherwise use MINOR for compatible functionality or MAJOR for breaking changes, and document the impact and migration path. SemVer does not replace review.

### 5. How do you balance CI coverage, flakiness, execution time, and Kubernetes versions?

**Model answer:** Define a supported version matrix, test oldest/newest supported versions and meaningful intermediate capability boundaries, and keep cluster-free gates fast. Use isolated ephemeral clusters for install/upgrade, bounded readiness waits, deterministic fixtures, and evidence collection before cleanup. Track flake/rerun rate rather than retrying every failure until green. A reduced matrix is acceptable only when the coverage trade-off is explicit.

## 16. Sources and verification notes

Use the official documentation matching installed tool versions. This chapter does not claim that live documentation was consulted or that any commands were executed.

| Topic | Official source/document and URL | Version-sensitive? | Local verification |
|---|---|---:|---|
| Helm chart testing/lint | Helm Docs, charts and CLI: https://helm.sh/docs/topics/charts/ and https://helm.sh/docs/helm/helm_lint/ | Yes | `helm lint --help`; chart metadata and warning behavior |
| Rendering and tests | Helm CLI docs: https://helm.sh/docs/helm/helm_template/ and https://helm.sh/docs/helm/helm_test/ | Yes | Supported flags and hook behavior |
| Chart metadata | Helm Docs, “The Chart.yaml File”: https://helm.sh/docs/topics/charts/ | Yes | `version`, `appVersion`, `kubeVersion`, capabilities |
| Values schema | Helm chart documentation: https://helm.sh/docs/topics/charts/ | Yes | Supported JSON Schema draft and unknown-key behavior |
| `kubeconform` | Project repository: https://github.com/yannh/kubeconform | Yes | Installed version, `--help`, Kubernetes version and schema-location syntax |
| `helm-unittest` | Project repository: https://github.com/helm-unittest/helm-unittest | Yes | Plugin version, install procedure, test-file and assertion syntax |
| `chart-testing` | Project repository: https://github.com/helm/chart-testing | Yes | `ct` version, configuration and command flags |
| Kubernetes API deprecations | Kubernetes Docs, “Deprecated API Migration Guide”: https://kubernetes.io/docs/reference/using-api/deprecation-guide/ | Yes | API removed in each target Kubernetes minor |
| Server-side dry-run | Kubernetes Docs, “Declarative Management of Kubernetes Objects Using Configuration Files”: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/ | Yes | `kubectl apply --dry-run=server` behavior in installed version |
| Jobs, probes, security context | Kubernetes Docs: https://kubernetes.io/docs/concepts/workloads/controllers/job/ and https://kubernetes.io/docs/tasks/configure-pod-container/security-context/ | Yes | API fields and behavior in target cluster |
| SemVer | Semantic Versioning 2.0.0: https://semver.org/ | Specification stable; chart policy is local | Apply compatibility impact to chart values/resources |
| Trivy config scan | Aqua Security Trivy documentation: https://trivy.dev/latest/docs/ | Yes | Installed command syntax and target types |
| GitHub Actions security | GitHub Docs, workflow syntax/security: https://docs.github.com/en/actions | Yes | Permissions, immutable action SHA, runner policy |

### Source-grounded behavior

The core distinctions are that chart linting, rendering, schema validation, API-server validation, install tests, upgrade tests, policy checks, and diff review test different properties. Values schemas enforce only declared constraints. A render is not an execution. Chart `version` and `appVersion` are distinct fields. SemVer classification must follow compatibility impact and the project’s contract.

### `[VERIFY]` / `[VERSION-SENSITIVE]` items

- Helm lint options and warning behavior.
- JSON Schema draft support and unknown-key behavior.
- `kubeconform` flags, schema source configuration, and CRD schemas.
- `helm test --logs` availability and behavior.
- `helm-unittest` plugin syntax and conventions.
- `ct lint`, `ct install`, `ct list-changed`, and `ct install --upgrade` support.
- `kubectl` server-side dry-run flags and behavior.
- Trivy config scanning syntax.
- `kubeVersion` constraints and `.Capabilities` behavior.
- Kubernetes APIs considered deprecated/removed in each target version.
- Any chart-releaser or release-automation commands.

### Engineering recommendations

- Make required CI gates fail closed and keep optional tools explicitly profiled.
- Preserve baseline renders and review high-risk diffs.
- Test supported environment values and upgrade paths, not only defaults and fresh installs.
- Treat plugin/action/tool versions as supply-chain dependencies.
- Keep chart EOL/deprecation policy explicit and avoid reusing published chart versions.

## 17. Author's verification checklist

| Gate | Status | Evidence note |
|---|---|---|
| Exact Unit 4 scope and target filename | PASS | Title and metadata identify the requested artifact |
| Full testing ladder and limitations | PASS | Section 4 and Section 5 distinguish stages and limitations |
| `kubeconform`, dry-run, test hooks, unit fallback, chart-testing | PASS | Covered with explicit version-verification notes |
| Chart `version`, `appVersion`, SemVer, `kubeVersion`, `.Capabilities` | PASS | Section 6.7 and Section 7.6 |
| Upgrade tests, diffs, policy, compatibility, image references | PASS | Section 7 |
| CI script/Makefile includes all required targets | PASS | Section 8.2 |
| Five planted defects mapped to appropriate gates | PASS | Lab 2 and policy mapping |
| Exactly 10 SemVer scenarios with model answers | PASS | Lab 3 contains 10 scenarios |
| SRE/security/checklist/self-check/interview/evidence/sources | PASS | Sections 9–16 |
| Local commands executed in a real Helm/kind environment | NOT VERIFIED | Learner must run in the installed versioned environment |
| Optional tool flags and plugin syntax live-verified | NOT VERIFIED | Explicit `[VERIFY]` items identify checks |
| Placeholder image successfully runs | NOT VERIFIED | Fixture images are placeholders; replace before cluster runtime tests |
| Only target artifact generated | PASS | This content is intended only for `04-helm-chart-testing-linting-and-versioning.md` |
