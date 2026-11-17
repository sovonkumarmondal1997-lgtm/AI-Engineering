# PROMPT — Generate `SYLLABUS-Helm-Kustomize-and-Kubernetes-Packaging.md`

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a capable, long-context LLM. The output is very large, so the prompt uses a multi-part Delivery Protocol (Section 14).

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior DevOps Engineer and SRE with 15 years of production experience** packaging and delivering Kubernetes applications across many teams and environments. You have untangled 4,000-line `values.yaml` files, debugged `helm upgrade` stuck in `pending-upgrade`, found out that `--reuse-values` silently kept a stale setting, shipped a chart change that broke every consumer, and replaced copy-pasted manifests with something reviewable. You teach with **evidence over opinion, rendered output over assumptions, and every claim verifiable.**

You are also a careful technical author. You never invent a chart field, a template function, a Helm/Kustomize flag, a plugin behavior, a default, or a version number. When unsure, you say so and mark it `[VERIFY]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 2E — Production DevOps & Platform Engineering / 06-Helm-Kustomize-and-Kubernetes-Packaging/` (module code **M06**)

Output file name: **`SYLLABUS-Helm-Kustomize-and-Kubernetes-Packaging.md`**

It must teach, **one after another, from beginner to advanced**, these 11 units in this exact order:

| # | Unit | Target file |
|---|---|---|
| 0 | Folder orientation | `README.md` |
| 1 | Kubernetes manifest management and the templating problem | `01-kubernetes-manifest-management-and-the-templating-problem.md` |
| 2 | Helm charts, values, and templates | `02-helm-charts-values-and-templates.md` |
| 3 | Helm hooks, dependencies, and subcharts | `03-helm-hooks-dependencies-and-subcharts.md` |
| 4 | Helm chart testing, linting, and versioning | `04-helm-chart-testing-linting-and-versioning.md` |
| 5 | Kustomize bases, overlays, and patches | `05-kustomize-bases-overlays-and-patches.md` |
| 6 | Choosing Helm vs Kustomize, and combining them | `06-choosing-helm-vs-kustomize-and-combining-them.md` |
| 7 | Chart repositories, OCI registries, and signing | `07-chart-repositories-oci-registries-and-signing.md` |
| 8 | Operators, CRDs, and custom controllers overview | `08-operators-crds-and-custom-controllers-overview.md` |
| 9 | Practice questions | `practice-questions.md` |
| 10 | Capstone project | `Projects/README.md` + `Projects/01-reusable-chart-and-overlays-for-multi-environment-delivery.md` |

Do **not** add, merge, skip, or reorder units. This is the **teaching content itself**, not an outline.

# 3. LEARNER AND CONTEXT

- **Learner:** a data/AI engineer who completed Stages 0–2D and Stage 2E modules M01–M05. They can write plain Kubernetes manifests (Deployments, Services, StatefulSets, Jobs, CronJobs, ConfigMaps, Secrets, PVCs, RBAC, NetworkPolicy), build/push images to a local registry (M01), run CI pipelines (M02), and operate a kind cluster (M03–M05). They have **not** managed multi-environment packaging.
- **Stage constraint — zero budget.** All hands-on work runs on a laptop (WSL2 Ubuntu primary, native Linux secondary; ~4 CPU, 8 GB RAM, 30 GB disk). No paid registries, no paid services. A kind cluster is needed for install/upgrade/rollback/hook/test labs; **most rendering, linting, diffing, and packaging labs need no cluster at all** (`helm template`, `helm lint`, `kubectl kustomize`/`kustomize build`, `kubeconform`) — prefer cluster-free labs and say which labs need a cluster, to keep the 8 GB budget free.
- **Primary lab platform: `kind`**, plus a local OCI registry (from M01) for chart publishing and signing labs.
- **Version-sensitivity note (state in the README and tag throughout):** Helm has multiple major versions with behavioral differences, and Kustomize ships both standalone and embedded in `kubectl` at potentially different versions. Do **not** assume a version. Teach to **record `helm version` and `kustomize version`/`kubectl version --client` in `versions.txt`**, tag every behavior that differs by major version as `[VERSION-SENSITIVE]`, and tell the learner to verify against the installed version's docs. Where the syntax for a feature changed (e.g., Helm plugin system, post-renderers, OCI commands, `--wait` behavior, server-side apply support, `helm install --take-ownership` or similar flags, chart API versions `apiVersion: v2`), tag `[VERIFY]` rather than asserting.
- **Tooling-map alignment and scope decisions** (state to the learner in the README):
  - **Core (hands-on):** Helm, Kustomize.
  - **Taught at working depth because this folder has dedicated modules, though the tooling map lists OCI chart distribution as Awareness:** OCI-based chart publishing to the **local registry**, `helm package`/`helm push`/`helm pull`, chart provenance and signing (Helm's GPG-based provenance **and** `cosign` for OCI artifacts as an alternative — compare them; cosign was Awareness in M01, so keep keyless/online parts as **Awareness** and demonstrate **key-based local signing** only `[VERIFY]`), and operators/CRDs/controllers (concepts + a hands-on CRD and a toy controller, plus inspection of a real operator installed via Helm — reuse CloudNativePG from M05 as the example, not a new one).
  - **Awareness only:** Jsonnet/Tanka, CUE, cdk8s, Pulumi (Kubernetes), ytt/Carvel, kpt, Timoni, Helmfile, Skaffold, Tilt, Garden, Terraform/OpenTofu Helm and Kubernetes providers (forward ref M07), Argo CD/Flux Helm and Kustomize controllers (forward ref M08 — **do not teach GitOps reconciliation here**), Artifact Hub, ChartMuseum/Harbor/Nexus as chart hosts, operator frameworks (Kubebuilder, Operator SDK, Kopf, Metacontroller, Crossplane compositions — forward ref M16), OLM (Operator Lifecycle Manager), kube-linter/kube-score/Polaris/Datree-style linters (one may be used as an optional lab helper `[VERIFY]` maintenance status), Conftest/OPA for manifest policy (optional helper; forward ref M12).
  - **Key principle to teach repeatedly:** *Packaging tools produce Kubernetes manifests; they do not make manifests correct, secure, or safe to deploy.* The unit of review is the **rendered output**, not the template. Templating adds an abstraction layer that must earn its place.
- **Domain flavor:** a data/ML platform application suite: a FastAPI model-scoring API, an ETL CronJob/Job, a worker Deployment, a database dependency (CloudNativePG `Cluster` or a simple PostgreSQL subchart for lab use), an Ingress/Gateway route (M04), NetworkPolicy, ServiceAccount/RBAC, HPA/PDB (M03), and per-environment differences (dev/staging/prod: replica counts, resources, image digests, hostnames, feature flags, storage classes, node pools/tolerations).
- **Cross-module links:** M01 (digest-pinned images, labels, non-root), M02 (CI builds/lints/packages/publishes charts; release automation and SemVer), M03 (the manifests being packaged; probes, PDBs, HPA, PSS), M04 (Ingress/Gateway, NetworkPolicy, cert-manager objects as chart content), M05 (StatefulSets, PVCs, operator-managed databases), M07 (IaC installing Helm releases — Awareness handoff), M08 (GitOps consuming charts/overlays: **Argo CD/Flux render and reconcile — deferred**), M09 (secrets: `Secret` handling in charts/overlays — teach the risks and patterns at concept level; sealed-secrets/SOPS/External Secrets belong to M09), M12 (supply-chain: signing/provenance/SBOM for charts), M16 (platform golden paths). State clearly what is **taught here vs. deferred**.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1–8)

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Explains the concept, runs the basic commands, and reads the rendered output. |
| **L2** | Intermediate — Working Practice | Builds a correct, maintainable package for a real multi-component application and avoids common mistakes. |
| **L3** | Advanced — Production Engineering | Designs packages as versioned interfaces; tests, secures, publishes, and defends choices under constraints. |
| **L4** | Expert — Operating at Scale and Under Failure | Diagnoses failed releases, enforces standards via policy and automation, and manages package lifecycles across teams and clusters. |

# 5. MANDATORY STRUCTURE FOR EACH UNIT 1–8

Use this exact skeleton, same headings, same order, in every unit. If a section is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Awareness:** …  |  **Last reviewed:** <date>  |  **Tool baseline assumed:** <Helm/Kustomize/Kubernetes ranges, [VERIFY]>  |  **Needs a cluster:** yes/no per lab

### N.0 Why this matters in production
(3–6 sentences; a concrete outage, drift incident, or review failure this prevents. No hype.)

### N.1 Learning objectives
(6–10 measurable outcomes, action verbs, each tagged L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception. At least one diagram — mermaid or ASCII — showing inputs (templates/bases/values/overlays) → rendering/patching → rendered manifests → API server, and where each artifact is stored/versioned.)

### N.3 Level 1 — Beginner
- First-principles explanation (what the tool does to your files, step by step; what it does NOT do)
- Guided lab: exact files/commands, expected rendered output, how to read it
- "What just happened?" walkthrough (trace from input files to rendered YAML to cluster objects)
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Complete, runnable packaging for the data/ML platform running example
- Pattern catalogue: pattern | when to use | when NOT to use
- Anti-pattern catalogue: bad template/overlay → how it breaks or hides problems → corrected version
- Lab with observable before/after behavior (always show a rendered-diff)

### N.5 Level 3 — Advanced
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Interface design, security, reliability, and maintainability techniques
- Verification method (render → validate → diff → dry-run → apply; how to avoid fooling yourself)
- Lab requiring a defended decision, not a copied snippet

### N.6 Level 4 — Expert
- Failure scenarios (symptom → hypothesis → test → root cause → fix → prevention)
- Policy-as-code and automation (lint rules, schema validation, rendered-manifest policy checks, CI gates)
- Fleet/organizational concerns: standards, ownership, compatibility policy, deprecation, review checklists
- Edge cases and platform differences (tool versions, kind vs production, WSL2, CRD ordering)

### N.7 SRE lens
- SLIs/SLOs relevant here (e.g., release success rate, change failure rate for packaging changes, render-time/CI time, config-drift count, rollback time)
- Failure modes and blast radius (e.g., a shared chart bump hitting 40 services)
- Runbook snippet: alert → triage → mitigation → follow-up
- Cost and capacity notes

### N.8 Security lens
- Threats addressed (e.g., secrets in values/overlays, untrusted charts/plugins/remote bases, tampered artifacts, overprivileged RBAC templates, privilege defaults, hook-borne code execution) and what is NOT addressed
- Controls and how to verify each with a concrete check

### N.9 Production checklist
(Checkbox list; every item verifiable by command.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch. Idempotent, safe to re-run, within the local baseline; each marked **cluster needed / not needed**.)

### N.11 Self-check questions
(6–10 questions with concise answer keys and a note on why wrong options are tempting.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves to prove completion.)

### N.13 Common interview and design-review questions
(5 questions with senior-level model answers.)

### N.14 Sources and verification notes
(Official docs consulted by name and section; [VERIFY] items; version-sensitive claims.)
```

# 6. MODULE-SPECIFIC CONTENT REQUIREMENTS

Minimum topics. Add depth, never remove.

## Unit 1 — Kubernetes manifest management and the templating problem
- **L1:** the problem: one application needs different config per environment; why copy-paste YAML drifts; declarative config and the desired-state file as source of truth; `kubectl apply` vs `create` vs `replace`; `kubectl diff`; `--dry-run=client` vs `--dry-run=server`; labels/annotations conventions (`app.kubernetes.io/*` recommended labels); organizing plain manifests in directories; `kubectl apply -f dir/` and ordering/dependency problems (CRDs before custom resources, namespace before namespaced objects).
- **L2:** the **configuration-management spectrum**: plain YAML → overlay/patching (Kustomize) → templating (Helm) → programmatic (Jsonnet/CUE/cdk8s/Pulumi — Awareness) — with the trade-off axes (readability, reuse, validation, type safety, learning curve, debuggability, diffability); the "templating YAML as text" problem (indentation, quoting, type coercion, `{{ }}` string-pasting into a structured language); data vs logic separation; what must vary per environment and what must **not** (a rule: the smaller the varying surface, the safer); configuration vs secrets vs code; schema validation with `kubeconform`/`kubectl --dry-run=server` and why client-side validation alone is insufficient; server-side apply and field ownership (concept, `[VERSION-SENSITIVE]` defaults); `kubectl apply` last-applied annotation and three-way merge; pruning (`--prune` risks `[VERIFY]`, labels) and orphaned objects after a manifest is removed.
- **L3:** config design principles: minimal and explicit interfaces, defaults that are safe in production, immutability (digest-pinned images, ConfigMap/Secret checksum annotations to roll pods on config change, immutable ConfigMaps), 12-factor config, avoiding "boolean explosion"; environment promotion model (same artifact + different config vs different artifacts; link M02 Unit 9); the **rendered-manifest-as-review-artifact** principle (render in CI, diff against the previous render, review the diff — "rendered manifests pattern" and its trade-offs); handling drift between declared and live state (`kubectl diff`, server-side dry-run); API deprecations in packaged manifests (link M03 Unit 8) and how packaging tools hide them; ownership and blast radius of shared packages; CRD lifecycle as a packaging problem (install order, upgrade, deletion cascades).
- **L4:** manifest-management governance (repo layout standards: monorepo of apps vs config repo vs per-app; promotion via directories vs branches — directory-per-environment is the usually recommended pattern, with trade-offs, `[ASSUMPTION]` labelled as opinion where applicable); policy-as-code over rendered output (schema, security baseline, required labels/limits/probes); change-impact analysis tooling (render diff across all environments for every PR); migration strategy from copy-paste YAML to a package; incident analysis: "a template change silently dropped `securityContext` in prod," "type coercion turned `"true"` into a boolean / `0123` into an integer," "orphaned resources survived a removal because nothing pruned them."
- **Must include:** a lab starting from three copy-pasted environment directories with deliberate drift, detecting the drift by diffing, and showing the maintenance cost; a lab demonstrating YAML type-coercion and quoting pitfalls with rendered evidence; and a baseline CI script (`render → kubeconform → server-side dry-run → diff`) that later units reuse.

## Unit 2 — Helm charts, values, and templates
- **L1:** what Helm is (package manager + templating + release manager); core vocabulary: **chart, release, revision, values, repository, template, manifest**; chart anatomy (`Chart.yaml`, `values.yaml`, `templates/`, `charts/`, `crds/`, `templates/_helpers.tpl`, `templates/NOTES.txt`, `.helmignore`, `values.schema.json`); `helm create`; `helm template`; `helm install/upgrade/uninstall/list/status/get manifest/get values/history/rollback`; release storage (Secrets in the release namespace by default `[VERIFY]`); `--set`, `-f`, `--values` precedence; the Go template basics and the `.Values`, `.Release`, `.Chart`, `.Capabilities`, `.Template` objects; `apiVersion: v2` charts; `appVersion` vs chart `version`.
- **L2:** template language essentials: `{{ }}`, whitespace control (`{{-`, `-}}`), pipelines, `default`, `quote`, `required`, `toYaml` + `nindent`/`indent`, `include` vs `template`, `with`, `range`, `if`/`else`, `eq`/`and`/`or`/`not`, `printf`, `tpl`, `lookup` (and why `lookup` returns empty under `helm template` and the consequences), `lower`/`trunc`/`trimSuffix`, `b64enc`, `sha256sum` (checksum annotations), `fail`; named templates in `_helpers.tpl` (fullname/labels/selectorLabels patterns and why selector labels must be **immutable and minimal**); `values.yaml` design (flat vs nested, documenting every key, safe defaults); `values.schema.json` (JSON Schema validation of values `[VERIFY]` draft support); writing a **complete chart for the FastAPI service** (Deployment, Service, ServiceAccount, ConfigMap, HPA, PDB, Ingress or HTTPRoute, NetworkPolicy — all optional via values toggles, **non-root securityContext defaults, resource requests/limits defaults, probes, digest-pinned image support**); `helm lint`; `helm template --debug`; `--dry-run=server` `[VERIFY]` flag form; `helm install --atomic/--wait/--timeout` semantics `[VERIFY]` and their interplay with probes/PDBs; `helm upgrade --install`; `helm diff` plugin (Awareness-level helper `[VERIFY]`); release names and namespace behavior (`--create-namespace`).
- **L3:** the **three-way strategic merge** Helm performs on upgrade (old manifest, new manifest, live state) and the consequences for out-of-band edits; `--reuse-values` vs `--reset-values` vs `--reset-then-reuse-values` `[VERIFY]` and the stale-value trap; `helm rollback` semantics (rollback creates a new revision; does not roll back data/PVCs/CRDs; hooks behavior); failed-release states (`pending-install`, `pending-upgrade`, `failed`, `superseded`) and recovery; values layering strategy (chart defaults < env file < per-release overrides; **never put secrets in values files committed to Git** — link M09); designing values as a **stable public API** (backward compatibility, deprecation, renamed keys with `fail`/warnings, schema validation, documentation with `helm-docs`-style generation `[VERIFY]` as optional); library charts (`type: library`) for shared helpers; avoiding anti-patterns (giant `if` forests, templating selectors with release-specific labels that change, logic in templates that belongs in code, passing raw YAML via values for every field "just in case" — the `extraObjects` / `extraEnv` escape-hatch trade-offs); `tpl` risks; `lookup` risks (breaks GitOps/rendered-diff workflows); idempotent rendering (no `randAlphaNum` in secrets without `lookup` retention → rotating passwords on every upgrade) and the standard fix with its caveats; resource ownership/adoption (`meta.helm.sh/release-name` annotations, adopting existing resources `[VERIFY]`); `--post-renderer` (Awareness, plus its security implications `[VERIFY]`); `helm get hooks/notes/all`; Helm's **size limits** (release Secret size, 1 MiB object limit) `[VERIFY]` and when charts hit them.
- **L4:** chart design reviews; upgrade-safety classification of changes (immutable field changes like Deployment `spec.selector`, StatefulSet `volumeClaimTemplates`, Service `clusterIP` → requires delete/recreate; Job template immutability → hooks or unique names); Helm and CRDs: why `crds/` is install-only (not upgraded/deleted by Helm `[VERIFY]` for the installed major version), patterns for CRD lifecycle (separate CRD chart, pre-upgrade hook, kubectl apply in pipeline), and their risks; multi-release dependencies and ordering; release-metadata hygiene (release history limit `--history-max`); Helm in CI (`lint`, schema validation, render-for-all-environments, kubeconform, policy on rendered output, `helm template | diff`); incident analysis: "`--reuse-values` carried an old image tag into prod," "upgrade failed with `field is immutable`," "chart upgrade deleted a resource unexpectedly," "release stuck `pending-upgrade` after interrupted CI job," "random secret regenerated on every upgrade broke DB auth" → diagnose → fix → prevent.
- **Must include:** a lab building the FastAPI chart from scratch with a values schema; a lab comparing `helm template` output across dev/staging/prod values with rendered diffs; install/upgrade/rollback on kind with history inspection; a deliberate `--reuse-values` stale-config failure; a deliberate `field is immutable` upgrade failure and its safe fix.

## Unit 3 — Helm hooks, dependencies, subcharts
- **L1:** what hooks are (resources annotated `helm.sh/hook` run at lifecycle points: `pre-install`, `post-install`, `pre-upgrade`, `post-upgrade`, `pre-delete`, `post-delete`, `pre-rollback`, `post-rollback`, `test`); hook weights and deletion policies (`helm.sh/hook-weight`, `helm.sh/hook-delete-policy`); hooks are **not part of the release manifest** in the same way (not tracked/cleaned like normal resources `[VERIFY]`); dependencies in `Chart.yaml` (`dependencies:` with `name`, `version`, `repository`, `condition`, `tags`, `alias`, `import-values`), `helm dependency update/build/list`, `Chart.lock`, `charts/` directory; what a subchart is.
- **L2:** a database-migration `Job` as a `pre-upgrade` hook and its failure semantics; waiting for dependencies (init containers vs hooks); subchart value overrides (`<subchart>.key`), `global` values, `condition`/`tags` to toggle subcharts (e.g., optional PostgreSQL for dev vs external DB in prod); `alias` for multiple instances; `import-values` `[VERIFY]` semantics; version constraints (SemVer ranges `^`, `~` in dependencies) and why ranges are risky vs `Chart.lock`-pinned; local file dependencies (`file://`) for monorepos; `helm template` renders hooks (they appear in output with annotations — learn to recognize them).
- **L3:** hook design rules (idempotent, short, bounded with `backoffLimit`/`activeDeadlineSeconds`, uniquely named or delete-policy managed, with least-privilege ServiceAccounts, **do not use hooks for things that belong in an operator or an init container**); hook ordering vs `--wait`; hook failure leaves releases in `failed` and the partial effects of `pre-upgrade` migrations (design migrations to be backward-compatible — expand/contract; link M03 Unit 4); hook deletion policies and leftover Jobs/Pods; `test` hooks (`helm test`) as smoke tests (link Unit 4); subchart pitfalls (naming collisions via `fullname`, resource duplication, global value leakage, **chart bloat from third-party subcharts with hundreds of values**, upgrading subcharts transparently changes your release, supply-chain trust of third-party charts — pin, vendor, review rendered output, and consider an internal mirror); **umbrella chart vs app-of-apps (GitOps, M08) vs independent releases** trade-off table; dependency on CRD-providing charts (ordering, `crds/` limitation); overriding subchart templates is not possible (explain the workarounds and why forking/vendoring or post-render patching has costs); `helm pull --untar` + review before use; chart version pinning and `Chart.lock` digest verification `[VERIFY]`.
- **L4:** release orchestration for suites (ordering across releases without GitOps: scripts/Helmfile — Awareness); upgrade strategy for third-party subcharts (render-diff the upgrade in CI; read changelogs; test in ephemeral kind); migration hooks in zero-downtime deployments; hook security (a hook is arbitrary workload execution at install time — threat-model the RBAC and image provenance; review third-party hooks); policy on allowed chart sources; incident analysis: "pre-upgrade migration hook timed out and left the schema half-migrated," "subchart bump changed a Service name and broke clients," "orphaned hook Jobs filled the namespace quota," "dependency version range pulled a breaking minor into prod."
- **Must include:** a lab with an umbrella chart for api + worker + optional PostgreSQL subchart toggled by `condition`; a migration hook lab with success, failure, and delete-policy behavior shown on kind; a lab pinning dependencies with `Chart.lock` and reviewing a third-party subchart's rendered output for risky defaults (privileged containers, `latest` tags, broad RBAC, `hostPath`).

## Unit 4 — Helm chart testing, linting, and versioning
- **L1:** why test packaging; the testing ladder for charts: `helm lint` → schema validation → render checks → manifest validation (`kubeconform`) → server-side dry-run → install tests on a throwaway cluster → upgrade tests → policy checks; what `helm lint` does and does not catch.
- **L2:** `helm template` + `kubeconform` against the right Kubernetes version schema and CRD schemas `[VERIFY]` flags (`-kubernetes-version`, `-schema-location` for CRDs); `helm test` with a test Pod (`helm.sh/hook: test`) and `helm test --logs` `[VERIFY]`; unit tests with the `helm-unittest` plugin (assertions on rendered documents) `[VERIFY]` install and syntax, or plain `helm template | yq` assertions in a shell/pytest harness as the fallback; chart-testing (`ct lint`, `ct install`, `ct list-changed`) `[VERIFY]` for the CI flow; test matrices over multiple values files (`ci/*-values.yaml` convention); **Chart.yaml versioning:** chart `version` (SemVer, the chart package version) vs `appVersion` (informational app version) and how they move independently; SemVer rules applied to charts (what is a MAJOR change in a chart: values removed/renamed, required value added, default behavior change, selector/immutable field change, minimum Kubernetes version raised).
- **L3:** **upgrade testing** (install version N, upgrade to N+1 with realistic values, verify hooks/PVCs/Services; `ct install --upgrade` `[VERIFY]`); rendered-diff gates in CI (diff the rendered output between `main` and the PR for every environment values file; fail or flag on risky diffs like selector changes, removed securityContext, replica to zero); **values compatibility testing** (golden files of old values rendered with new chart); policy tests on rendered output (Conftest/OPA rules, kube-linter/kube-score/Polaris-style checks, Kyverno CLI `[VERIFY]` — Awareness-level with one worked policy such as "no `latest` tags, requests/limits required, non-root required"); security scanning of charts (`trivy config` on rendered manifests/chart dirs `[VERIFY]` flag — Trivy is a Core tool from M01); image reference extraction from rendered manifests to feed image scanning (link M01/M12); `Chart.yaml` `kubeVersion` constraint and `.Capabilities` checks `[VERIFY]`; API-deprecation detection on rendered output (link M03 Unit 8); `README`/values documentation checks; changelog and release automation for charts with Conventional Commits and SemVer (link M02 Unit 8: `ct`/release tooling, `chart-releaser` Awareness `[VERIFY]`); deprecation policy for values (warn for N releases, then remove in a MAJOR).
- **L4:** a chart CI pipeline design (GitHub Actions workflow file, valid and SHA-pinned per M02 rules, matrix over Kubernetes versions using ephemeral kind — footprint note); flaky-install-test management (link M02 Unit 6); testing against multiple Kubernetes minor versions and the version-skew you promise to support; consumer-driven contract tests for shared charts (consumers publish representative values; the chart CI renders all of them — "downstream render matrix"); org-level standards (minimum chart quality bar: schema, docs, tests, security defaults, upgrade notes); chart deprecation/EOL process; incident analysis: "a patch release changed a default and altered production behavior," "schema validation was missing and a typo'd key was silently ignored in prod," "CI tested install but never upgrade," → diagnose → fix → prevent.
- **Must include:** a lab producing a full local chart-CI script/Makefile (`lint`, `schema`, `render-all`, `kubeconform`, `unittest`, `policy`, `install-test`, `upgrade-test`, `diff`) that exits non-zero on failure; a lab planting 5 defects (typo'd values key, missing selector label, `latest` tag, privileged container, deprecated API) and proving each is caught by a specific stage; a SemVer-classification exercise on 10 realistic chart changes with model answers.

## Unit 5 — Kustomize bases, overlays, and patches
- **L1:** what Kustomize is (template-free customization: declarative composition of plain YAML); `kustomization.yaml`; `kubectl kustomize` / `kubectl apply -k` vs standalone `kustomize build` and the version difference `[VERIFY]`; resources, `namespace`, `namePrefix`/`nameSuffix`, `commonLabels` (**and why `commonLabels` is risky: it modifies selectors**; prefer `labels` with `includeSelectors: false` `[VERIFY]`), `commonAnnotations`, `images` (name/newName/newTag/digest), `replicas`; base and overlay layout (`base/`, `overlays/dev|staging|prod`); `kustomize build` output as the review artifact.
- **L2:** **patches**: `patches` (strategic merge and JSON 6902, inline or file, with `target` selectors) `[VERIFY]` current field names (the older `patchesStrategicMerge`/`patchesJson6902` are deprecated — teach the current form and flag the legacy); when strategic merge vs JSON patch (lists keyed by `name`, replacing vs merging containers, `$patch: delete/replace`); `configMapGenerator`/`secretGenerator` (name-suffix hashes that trigger rollouts, `behavior: create|replace|merge`, `disableNameSuffixHash`, `options.immutable`) and the **secretGenerator caveat** (literals/files in Git = secrets in Git — M09); `replacements` (modern replacement for `vars`; `vars` deprecated `[VERIFY]`); `components` (reusable optional feature bundles, e.g., `components/monitoring`, `components/network-policy`) `[VERIFY]` kind/apiVersion; remote bases/resources and the **supply-chain risk** of referencing remote URLs/branches (pin to commit SHAs; vendor instead); `kubectl kustomize --load-restrictor` and file-reference restrictions (security rationale) `[VERIFY]`; transformer ordering surprises; name references and how generators/prefixes rewrite references (`nameReference`), Kustomize's handling of CRDs via `configurations` `[VERIFY]`.
- **L3:** overlay design (shallow overlays; prefer 2–3 layers; avoid patching everything; keep the variance surface small); **base design as an API** (what overlays may legitimately change; stable resource names); patch hygiene (small targeted patches with comments; prefer `images:` and `replicas:` over patches; avoid whole-resource replacement hiding drift); multi-base composition (compose app + shared platform base like NetworkPolicy/PDB defaults); **Helm-output-as-base** pattern preview (full treatment Unit 6); `helmCharts` inflation field (requires `--enable-helm`, relies on a `helm` binary, `[VERIFY]` behavior) and its pitfalls; validating overlays (`kustomize build` → `kubeconform` → `kubectl diff` → `--dry-run=server`); handling Jobs/immutable fields and generators; ConfigMap hash rollouts vs external config; strategic-merge-patch pitfalls with lists and `containers[*]` ordering; JSON-patch fragility (index-based paths); debugging with `kustomize build --enable-alpha-plugins` (Awareness: plugins are **disabled by default for good reasons** — arbitrary code execution) `[VERIFY]`; Kustomize and CRDs/patching custom resources.
- **L4:** large-scale overlay governance (per-team bases, per-cluster overlays, naming/labeling standards, ownership via CODEOWNERS — link M02); policy checks over `kustomize build` output; CI render-diff across all overlays; detecting "overlay sprawl" and "patch spaghetti"; migration strategies (Helm → Kustomize and Kustomize → Helm; fork/vendor third-party bases); Kustomize in GitOps (what Argo CD/Flux do — **forward ref M08, do not teach**); incident analysis: "`commonLabels` changed selectors and the Deployment upgrade failed (immutable field)," "a patch targeted the wrong resource after a rename and silently did nothing/everything," "secretGenerator committed a production password," "remote base moved and changed production," "hash-suffixed ConfigMap rolled all pods unexpectedly."
- **Must include:** a lab building a base and three overlays (dev/staging/prod) for the platform suite with replicas/resources/images-by-digest/hostnames/storage-class patches and a reusable `components/` bundle; rendered diffs across overlays; a `commonLabels` selector-immutability failure on kind and the fix; a generator-hash rollout demonstration; and a lab converting one patch from strategic-merge to JSON 6902 and back, noting when each breaks.

## Unit 6 — Choosing Helm vs Kustomize, and combining them
- **L1:** the central question: *packaging for others* (distribution, versioned interface, install/upgrade lifecycle) vs *customizing for yourself* (patching known manifests per environment); summary table of strengths/weaknesses; what each tool owns in the lifecycle (Helm: render + release tracking + hooks + rollback; Kustomize: render only — apply and tracking are `kubectl`/GitOps).
- **L2:** a **decision framework** with explicit criteria: audience (internal vs external consumers), variability (few fields vs many toggles), third-party software (vendor charts vs your own manifests), need for lifecycle features (hooks, tests, rollback), review ergonomics (rendered vs patch diffs), team skills, GitOps tooling support, secret handling needs, schema/validation needs; worked decisions for 6 realistic scenarios (internal microservice, vendor app like an observability stack, shared platform defaults, per-env differences of a third-party chart, a library consumed by 30 teams, a one-off job); rules of thumb stated with their exceptions.
- **L3:** **combining patterns** with trade-offs: (a) Helm chart for the app + Kustomize overlays on `helm template` output (render-then-patch; the rendered-manifest pipeline), (b) Kustomize `helmCharts` inflation, (c) Helm `--post-renderer` calling Kustomize `[VERIFY]` flag/behavior, (d) Kustomize bases + Helm only for third-party dependencies, (e) GitOps controllers rendering both (forward ref M08), (f) Helm values per env without Kustomize; for each: where drift can appear, where release tracking is lost or retained (Helm release metadata vs none), debuggability, CI integration, rollback story, and security surface (post-renderers and plugins execute code); **patching third-party charts safely** (prefer values; then post-render/overlay; fork last; track upstream); avoiding double-templating confusion; keeping one source of truth for image digests across both tools (CI updates one file); environment promotion with each approach (link M02 Unit 9); drift detection differences; naming of the standard "rendered manifests in Git" approach and its review benefits and noise costs.
- **L4:** platform-level standards (golden-path choices and exceptions process; forward ref M16); migration playbooks (copy-paste → Kustomize → Helm; Helm → plain rendered manifests; vendor chart → internal wrapper chart) with risks; "wrapper chart" pattern (a thin chart depending on a vendor chart with pinned values and extra resources) — benefits and pitfalls (value nesting, upgrade friction); long-term maintenance cost modeling (cost of each abstraction layer: onboarding, debugging time, upgrade work — qualitative, no invented numbers); incident analysis: "double rendering produced two conflicting Services," "post-renderer silently failed and shipped un-patched manifests," "team forked a vendor chart and missed a CVE fix"; ADR template for a packaging decision.
- **Must include:** a lab implementing the **same application packaged four ways** (plain manifests + Kustomize; Helm only; Helm → render → Kustomize overlays; Kustomize + `helmCharts`), each producing a rendered output; a comparison matrix the learner fills with their own observations (lines of config, review-diff size for a standard change, debuggability notes — qualitative, no fabricated numbers); and a **written decision memo** (ADR) choosing one approach for a stated scenario.

## Unit 7 — Chart repositories, OCI registries, and signing
- **L1:** how charts are distributed: classic **HTTP chart repositories** (`index.yaml` + `.tgz` files; `helm repo add/update/search/pull`, `helm package`, `helm repo index`) vs **OCI registries** (`helm push`/`helm pull`/`helm install oci://…`; `helm registry login`) `[VERSION-SENSITIVE]` command forms; chart packages are tarballs with a SemVer version; **immutability of published versions** as a principle (never overwrite a version); what Artifact Hub is (Awareness) and why it is not a trust authority.
- **L2:** package the FastAPI chart; serve a local HTTP repo (e.g., `python -m http.server` + `helm repo index`) and consume it; push to the **local registry from M01** over OCI (`registry:2` with TLS/basic auth as in M01 Unit 6 `[VERIFY]` insecure/plain-http flags such as `--plain-http` for local lab use only); pull and inspect (`helm pull --untar`, `helm show chart/values/readme`); install from OCI by version and by **digest** `[VERIFY]` support; `helm dependency` against OCI repos; credentials handling (`helm registry login`, credential helpers; no passwords in CI logs — link M02/M09); versioning/tagging for charts (OCI tag = chart version; SemVer `+` build metadata mapped to `_` `[VERIFY]`).
- **L3:** **provenance and signing**: Helm's **provenance** mechanism (`helm package --sign`, `.prov` files, `helm verify`, `--verify` on install/pull; GPG keyrings and their operational pain `[VERIFY]` flag names and keyring format under the installed Helm major) vs **cosign** signatures for OCI chart artifacts (key-based local signing and verification demonstrated; keyless/OIDC signing is **Awareness** requiring public infrastructure — explain the concept and its trust model, no live lab; `[VERIFY]` current cosign command syntax and the registry's referrers/tag-based signature storage); what signing proves (publisher key possession/identity and artifact integrity) and does not prove (the chart is safe, the images are safe, the publisher is trustworthy); verifying **before** install in CI; pinning chart versions and digests; SBOM and attestation for charts and images they reference (Syft from M01; attestations — forward ref M12); extracting and scanning image references from charts; repository access control (read vs push permissions; link M01 Unit 7); retention and garbage collection of chart artifacts; mirroring/proxying third-party charts into an internal registry (supply-chain resilience and review point); trust policy (allowed sources, required signatures — enforcement at admission is M12/M08 Awareness); `helm pull` + `helm template` review of third-party charts before adoption; avoiding `helm repo add` of unknown URLs in automation.
- **L4:** chart release pipeline design (CI: lint → test → package → sign → push → verify-pull → attach SBOM → release notes — link M02 Unit 7/8; writes the workflow file with least-privilege permissions; real publishing only to the local registry in the lab); key management (rotation, revocation, who holds signing keys, KMS/HSM concept — Awareness; forward ref M09/M12); handling a compromised/yanked chart version (OCI has no native yank; policy: publish a fixed version, deprecate, notify, block in admission — and what you can't recall); multi-registry replication/mirroring and tag-drift detection (link M01 Unit 5); deprecating charts; consumer-side policy (only signed charts from approved registries; render-time checks); incident analysis: "a chart version was overwritten in the registry and different clusters installed different content," "the signing key leaked," "mirror served a stale chart with a known CVE," "a transitive subchart changed upstream."
- **Must include:** a lab with the full cycle against the local registry: package → (optional GPG-signed with a throwaway key) → push → pull-by-version and by digest → verify → install → attempt to overwrite a version and detect the digest change → cosign key-based sign/verify of the OCI chart → tamper test (modify the package) proving verification fails. All key material is throwaway and labelled lab-only; local registry insecure-mode flags are lab-only with an explicit warning.

## Unit 8 — Operators, CRDs, and custom controllers overview
- **L1:** the Kubernetes extension model: **CustomResourceDefinitions** (new API types), **custom resources**, **controllers** (reconcile loops, watch/list, desired vs observed), the **operator pattern** (domain knowledge encoded in a controller); built-in vs custom controllers (Deployment controller as the model); `kubectl get crd`, `kubectl explain` for CRDs, `kubectl api-resources`; examples already used in this stage (cert-manager `Certificate`, CloudNativePG `Cluster`, Gateway API `HTTPRoute`, VolumeSnapshot).
- **L2:** CRD anatomy (`apiextensions.k8s.io/v1`; `group`, `names`, `scope`, `versions` with `served`/`storage`, OpenAPI v3 `schema`, `subresources: status/scale`, `additionalPrinterColumns`, defaults, validation, CEL `x-kubernetes-validations` `[VERIFY]`); write a CRD for a lab type (e.g., `DataPipeline` with `schedule`, `source`, `image` fields) and create instances; structural schema requirement and pruning of unknown fields; finalizers and owner references (garbage collection); status conditions conventions; **installing operators**: via Helm chart, plain manifests, or OLM (Awareness) — inspect what an operator install actually creates (CRDs, Deployment, RBAC, webhooks, ServiceAccount) using `helm template` on a real operator's chart (reuse CloudNativePG from M05 `[VERIFY]` chart location) and **review the RBAC and webhooks it requests before installing**.
- **L3:** controller anatomy: informers/caches, work queues, level-triggered reconciliation, idempotency, requeue/backoff, leader election, status updates, events, finalizers for cleanup, owner references for garbage collection, **conversion and admission webhooks** (and their blast radius — link M03 Unit 1); CRD **versioning and conversion** (`v1alpha1` → `v1beta1` → `v1`, storage version migration, conversion webhook vs `None` strategy `[VERIFY]`, why storage-version changes need care); **CRD lifecycle with Helm** (link Unit 2: install-only `crds/`; upgrade strategies; deletion cascades delete all custom resources — protect with policy/labels/backups); building controllers: frameworks overview (Kubebuilder/controller-runtime in Go, Operator SDK, Kopf in Python, Metacontroller, shell-operator — Awareness) and **a toy controller lab** (a small Python or shell reconcile loop using `kubectl`/the Kubernetes client that watches `DataPipeline` objects and creates/updates a CronJob, sets status and ownerReferences, handles deletion; `[VERIFY]` any library API used; clearly labelled a teaching toy, not production code); alternatives to writing operators (Helm, Kustomize, Crossplane/Compositions — Awareness, policy engines, admission mutation); **when to build an operator vs when not to** (decision framework: repeated complex day-2 operations, need for continuous reconciliation, domain-specific API for platform users vs the maintenance burden, API design commitments, upgrade/versioning obligations); operator maturity levels (Awareness).
- **L4:** **operator due diligence** for production (maintenance activity, governance, release cadence, upgrade path and CRD migration docs, RBAC scope, webhook policies, security posture, resource footprint, observability, test coverage evidence, backup/restore story, exit strategy — all `[VERIFY]` per candidate); operator blast radius (cluster-wide RBAC, webhook failure policy, controller bug that mass-deletes — design safeguards: finalizer discipline, dry-run modes, deletion protection, rate limits, resource quotas); upgrading operators and CRDs safely (read release notes; render-diff; test on ephemeral kind; backup custom resources via `kubectl get -o yaml` and etcd/Velero concept; staged rollout across clusters); running operators in multi-tenant clusters (namespace-scoped vs cluster-scoped, watch namespaces); API design for platform CRDs (spec/status separation, declarative semantics, immutability and validation, versioning policy — forward ref M16); policy-as-code for CRs (CEL validation, admission policies); incident analysis: "operator upgrade changed CRD schema and existing CRs became invalid," "deleting the CRD deleted every database object," "operator with a bad webhook blocked all pod creation," "controller hot-looped and hammered the API server (rate limits/backoff)," "finalizer never removed → namespace stuck terminating" → diagnose → fix → prevent.
- **Must include:** a lab defining a CRD with schema validation and printer columns, creating valid/invalid custom resources (showing validation rejection), running the toy controller to reconcile `DataPipeline` → CronJob with status and owner references (including deletion and drift correction), then deliberately breaking it (bad CR, controller down) and observing behavior; plus an **operator-inspection lab** rendering a real operator's Helm chart and producing a written risk review of its RBAC, webhooks, and CRDs (listing at least five findings and recommended mitigations). Clean up CRDs with the explicit warning that deleting a CRD deletes all its custom resources.

# 7. PRACTICE QUESTIONS (Unit 9)

At least **140 questions**: ≥ 12 per Units 1–8 plus ~25 cross-unit integration scenarios. Per unit:
- 3 × conceptual short-answer
- 3 × multiple choice (4 options; explain every distractor)
- 2 × output interpretation (given `helm template`/`helm upgrade`/`helm history`/`kustomize build` output or an error, what is wrong?)
- 2 × chart/overlay review (find ≥ 3 defects in a template, values file, or kustomization; fix them)
- 1 × incident/troubleshooting scenario (symptom → diagnose → fix → prevent)
- 1 × design question with a rubric

Each question: ID, level (L1–L4), objective tested, time estimate, **model answer**, **common wrong answers**. Include "predict the rendered output" questions (given templates and values, write the exact YAML), "SemVer-classify this chart change" questions, and "which tool and why" scenario questions. Include a scoring rubric (≥ 80% proceed; 60–79% remediate; < 60% repeat) and 8 "design-review" whiteboard prompts requiring written trade-off reasoning (e.g., values-as-API design, Helm vs Kustomize for a platform, handling a vendor chart, CRD lifecycle strategy, chart signing and trust policy, preventing breaking changes to a shared chart, build-an-operator-or-not, environment promotion of rendered manifests). Test only taught content.

# 8. CAPSTONE PROJECT (Unit 10)

**Project:** *Reusable Chart and Overlays for Multi-Environment Delivery.*

Deliver `Projects/README.md` (index, grading, evidence submission) and the full spec.

**Scenario:** A data/ML team has three copy-pasted manifest directories (dev/staging/prod) for a scoring API, a worker, an ETL CronJob, and a database. They have drifted: prod lost its `securityContext`, staging runs a stale image, hostnames are hand-edited, a secret value sits in a values file in Git, `helm upgrade --reuse-values` once carried an old tag into prod, and a shared vendor chart bump changed a Service name. The learner builds a **reusable, tested, versioned, signed, multi-environment packaging system** that makes those failures impossible or immediately visible — locally and for free.

**Required deliverables (each with acceptance criteria verifiable by command or inspection):**
1. Repository layout (`charts/`, `deploy/base`, `deploy/overlays/{dev,staging,prod}`, `deploy/components/`, `ci/`, `docs/`), bootstrap script with context safety checks, and `versions.txt` (Helm, Kustomize/kubectl, kind, Kubernetes, kubeconform, helm-unittest/ct versions).
2. A **reusable Helm chart** for the API + worker + CronJob (library chart or shared helpers for labels/security defaults), with `values.schema.json`, documented `values.yaml`, secure defaults (non-root, read-only rootfs where possible, resources, probes, PDB, HPA toggle, NetworkPolicy toggle, digest-pinned images), optional Ingress/HTTPRoute, optional PostgreSQL subchart or CloudNativePG `Cluster` template for dev only, and a `pre-upgrade` migration hook with safe semantics.
3. Kustomize **base + three overlays + at least two components** (e.g., `monitoring`, `network-policy`) built from the chart's **rendered output** (render-then-patch) — images by digest via `images:`, per-env replicas/resources/hostnames/storage classes; no `commonLabels` selector mutation; no secrets in Git (placeholder pattern with a documented hand-off to M09).
4. A **chart CI script** (`make ci`) running: `helm lint`, schema validation, render for all environments, `kubeconform` against pinned Kubernetes version and CRD schemas, `helm-unittest` (or shell fallback), policy checks on rendered output (no `latest`, requests/limits required, non-root required, no privileged, no `hostPath`), rendered-diff vs a baseline directory, and `trivy config` (or equivalent) on rendered manifests; exits non-zero on any failure.
5. A **GitHub Actions workflow file** for the same CI (valid, SHA-pinned placeholders per M02 rules, least-privilege permissions, matrix over two Kubernetes versions optional) — Awareness-level execution (runnable locally via `act` optionally).
6. **Install/upgrade/rollback tests** on kind: install N, upgrade to N+1, verify hook ran and data kept, roll back, verify; a documented failure drill (`field is immutable`, hook failure, stale `--reuse-values`) with recovery steps.
7. **Versioning and release:** chart SemVer policy document with a change-classification table; changelog; `Chart.yaml` `version`/`appVersion` handling; a script that refuses to publish if the version already exists.
8. **Publishing and trust:** package, push to the local OCI registry (from M01), pull by version and by digest, **cosign key-based signing and verification** (throwaway keys), optional Helm provenance with a throwaway GPG key, a tamper test proving verification fails, and a script that verifies before install.
9. **Operator/CRD component:** a small `DataPipeline` CRD + toy controller (from Unit 8) packaged in its own chart with the CRD lifecycle strategy documented; `crds/` limitation handled with a documented procedure; CR deletion-protection note.
10. **Packaging comparison memo (ADR):** the same app rendered via two of the Unit 6 approaches with the learner's own qualitative observations and a decision.
11. `Makefile` targets: `up`, `lint`, `render`, `validate`, `diff`, `test`, `install`, `upgrade`, `rollback`, `package`, `publish-local`, `verify-signature`, `ci`, `down`; `make verify` outputs a pass/fail report with evidence.
12. Documentation: architecture diagram (sources → render → validate → publish → sign → deploy, with artifact identities), ≥ 5 ADRs (Helm-vs-Kustomize split, values API design, CRD lifecycle, signing approach, environment promotion model), runbooks for 5 incidents (failed/stuck release, immutable-field upgrade failure, bad chart version published, signing key compromise, operator/CRD upgrade breaking CRs), and a production-readiness review using the Unit 1–8 checklists.
13. A before/after results table (drift count between environments, review-diff size for a standard change, number of defect classes caught by CI before apply, time to roll back, render time per environment, number of places an image digest is defined) filled from the learner's **own** measurements. Provide the template; never fabricate results.

**Include:** 6–7 milestones with time estimates; a 100-point rubric (Poor/Adequate/Strong/Exemplary descriptors, with strong weighting for **tested upgrades/rollbacks and verified-before-install trust**); stretch goals (Helmfile-style multi-release orchestration as Awareness; kube-linter/Kyverno CLI policy pack; render to a Git directory with a promotion PR flow — preview of M08; wrapper chart around a vendor chart); common failure points; self-review checklist; exact evidence folder structure; a resource-budget plan for 4 CPU / 8 GB / 30 GB noting which steps need a cluster.

**Provide complete, runnable starter code:** the chart (templates, helpers, schema, tests), overlays/components, the toy controller, scripts, Makefile, policy rules, CI workflow, signing/verification scripts. No `TODO: implement` in required deliverables. All credentials, keys, and signing material are throwaway fakes labelled lab-only (`example-password-do-not-use`); note that real secret handling is M09.

# 9. README ORIENTATION (Unit 0)

Include: purpose and audience; Gate In prerequisites (including M01–M05 outcomes consumed here); module dependency graph and why order matters (templating problem → Helm basics → hooks/deps → testing → Kustomize → choosing/combining → distribution/signing → operators/CRDs); 5-week and 8-week pacing plans; tool matrix (Core / working-depth / Awareness matching Section 3) with install-verification commands and a **version-recording step**; lab environment checklist (kind not required for most labs, local registry from M01, free-disk and RAM checks); **which labs need a cluster** table; **tool-version sensitivity table** (what to re-verify when Helm/Kustomize majors change); glossary; the **"templates are not truth; rendered output is"** primer; module-to-exit-criteria mapping; evidence rules; how to use practice questions and the project; table linking M06 to M01–M05, M07, M08, M09, M12, M16, M17; a **safety section**: context hygiene, never `helm install` untrusted charts into a cluster you care about, review rendered output and requested RBAC/webhooks/CRDs first, treat hooks/plugins/post-renderers as code execution, throwaway keys only, no secrets in values or overlays.

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block names its language and, for files, a first-line path comment (e.g., `# File: charts/scoring-api/templates/deployment.yaml`). Template files use the language tag `yaml` or `gotemplate` consistently and the surrounding text states that they are templates, not valid YAML before rendering.
2. **Show rendered output for every template and overlay example** (input → `helm template`/`kustomize build` → output), labelled "example — yours may differ in generated names and ordering", with a short interpretation. The learner must never see a template without its rendered result.
3. **Only real syntax.** Use Chart.yaml fields, template functions, Sprig functions, hook annotations, Kustomize fields, flags, and plugin commands you are confident exist for the stated tool versions. Anything that varies by Helm/Kustomize/Kubernetes version or plugin version is tagged `[VERIFY: what/where]` or `[VERSION-SENSITIVE]`. Never guess. Never use deprecated Kustomize fields (`bases`, `patchesStrategicMerge`, `patchesJson6902`, `vars`, `commonLabels` for selector-bearing resources) except in clearly labelled legacy/anti-pattern examples. For every tool install, **point to the official install documentation** and use `<VERSION>` placeholders — never invent version numbers.
4. **Context safety:** every cluster lab begins with a context check (`kubectl config current-context` asserted against the expected `kind-<name>`); destructive or cluster-wide commands (`helm uninstall`, `kubectl delete`, CRD deletion, `--force`, `--cleanup-on-fail`, `helm rollback` in a shared namespace) are labelled `⚠ DESTRUCTIVE` with the target and consequence named, and a read-only or dry-run alternative (`helm template`, `helm diff`, `--dry-run=server`, `kubectl diff`) comes first. CRD deletion carries a specific warning that it deletes all custom resources of that type.
5. **Manifests follow standards taught** in M01/M03/M04: pinned images (digest with tag comment), resource requests/limits, probes, non-root `securityContext`, explicit ServiceAccount, recommended labels, NetworkPolicy where applicable — unless a deliberate anti-pattern labelled `# ANTI-PATTERN — DO NOT COPY` with defect list, consequence, and fix beside it. Chart defaults must be **secure by default**; insecure options require explicit opt-in.
6. **No real secrets, keys, or credentials** in any chart, values file, or overlay; fake placeholders only; demonstrate the risk of secrets in values/`secretGenerator` and forward-reference M09. Signing keys are throwaway and lab-only. Warn that `helm get values`/release Secrets can expose sensitive values to anyone with read access to the namespace's Secrets.
7. **Supply-chain caution:** never instruct installing unreviewed third-party charts, plugins, or remote Kustomize bases into a non-throwaway cluster; always `helm pull --untar`/render and review first; pin versions and digests; plugins/post-renderers/Kustomize exec plugins are arbitrary code execution — say so wherever introduced.
8. **Scripts:** `set -euo pipefail`, quoted variables, explicit exit codes, context assertion, `--dry-run` default for anything mutating or deleting, idempotent where possible; CI/validation scripts exit non-zero on failure. Python: typed where practical, minimal dependencies, with tests.
9. **Resource realism:** every lab states whether it needs a cluster and its approximate CPU/RAM/disk footprint; prefer cluster-free labs; fit 4 CPU / 8 GB / 30 GB; do not require more than a single small kind cluster for this module except where explicitly optional.
10. **Every lab ends with cleanup** (helm uninstall releases created by the lab, delete namespaces/CRDs/clusters created, stop the local HTTP repo, remove local registry artifacts created, delete throwaway keys, remove kubeconfig contexts) and a verification that nothing stray remains.
11. **Every maintainability/size/speed claim** is tied to a measurement command (`wc -l`, `diff | wc -l`, `time`) or labelled "typical — measure yours". Never invent statistics about adoption, market share, or tool performance.
12. Call out WSL2 vs native Linux differences where they matter (local registry reachability from kind nodes, `localhost` semantics, file permissions on `/mnt/c`, line endings corrupting templates — LF only).
13. **Validate every template mentally by rendering it:** check indentation (`nindent`), quoting, whitespace control, `required`/`default` use, selector/label consistency, `include` names exist in `_helpers.tpl`, values keys exist in `values.yaml` and the schema, hook annotations are valid, overlay patch targets exist, and cross-file references resolve. Show the exact rendered YAML you expect.

# 11. PEDAGOGY RULES

- **Rendered output first:** for each feature, show input files, then the rendered result, then explain the transformation; teach the learner to distrust templates and trust `helm template`/`kustomize build` diffs.
- **One running example** (data/ML platform) evolving through the folder: copy-pasted YAML → templated → hook/dependency-aware → tested and versioned → overlaid → choice justified → published and signed → extended with a CRD/operator.
- **Show failure on purpose:** every unit has at least one lab where the learner triggers a realistic packaging failure (immutable field, stale values, bad patch target, selector mutation, tamper, broken CRD) and diagnoses it from rendered output, events, and release history.
- **Diagrams** for the configuration spectrum, Helm render/release pipeline and three-way merge, hook lifecycle, dependency/subchart value flow, test ladder, Kustomize base/overlay/patch composition, decision tree for Helm vs Kustomize, combined pipelines, chart publish/sign/verify flow, and the controller reconcile loop.
- Plain, precise English; no filler or marketing; define acronyms at first use; consistent terms (*chart, release, revision, values, template, render, overlay, base, patch, component, CRD, custom resource, controller, operator*).
- Honest trade-offs; avoid "always/never" without reasons and exceptions; be fair between Helm and Kustomize — neither is "the right answer" in general.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You act as author first, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base technical claims on **official documentation and specifications**: Helm documentation (Chart Template Guide, Chart Best Practices, Charts, Helm Hooks, Chart Tests, Dependencies, Provenance and Integrity, Registries/OCI, CLI reference, Plugins), Sprig function documentation, Go `text/template` documentation, Kustomize documentation (reference for `kustomization.yaml` fields, patches, generators, components, replacements), the Kubernetes docs (Manage Kubernetes Objects — declarative management, server-side apply, Extend the Kubernetes API: CRDs and controllers, Operator pattern, API deprecation guide, Recommended Labels), `kubeconform` and `helm-unittest` and `chart-testing` docs, cosign/Sigstore docs, OCI Distribution/Image specs (artifacts/referrers), Semantic Versioning 2.0.0, Google SRE Book/Workbook for release engineering principles. Cite by **document name and section/title**, not invented URLs; give a URL only if certain it is canonical, else mark `[VERIFY]`.
- **Do not fabricate:** versions, deprecation/removal dates, template functions, Chart.yaml fields, hook annotations, Kustomize fields, CLI flags, plugin syntax, default values, adoption statistics, benchmark numbers, CVE IDs, quotes, or tool behaviors. Derive numbers from stated commands or label `[ILLUSTRATIVE]`.
- Mark uncertainty with `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, or `[ASSUMPTION]`.
- Keep a running **Claim Register** for every non-trivial factual claim.

## 12.2 Mandatory multi-pass self-audit (before delivering each part)

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 11 units, all Section 5 sections, all Section 6 topics, L1–L4, all "Must include" labs. | Any gap. |
| 2 | **Technical accuracy** | Every template function, Chart.yaml field, hook annotation, Kustomize field, flag, and command is real and correctly used; render a mental `helm template`/`kustomize build` for every example and check the shown output matches the input; Helm release/merge/hook/CRD semantics are described correctly for the stated version. | Invented or misused syntax/behavior; shown output inconsistent with input. |
| 3 | **Executability** | Templates/YAML are valid after rendering; indentation and `nindent` correct; selectors/labels/names consistent; `include` names exist; values keys exist and satisfy the schema; overlays' patch targets exist; scripts pass ShellCheck in principle; labs have steps, evidence, cleanup; manifests pass `kubeconform` and server-side dry-run. | Broken or ambiguous step. |
| 4 | **Currency** | Version-sensitive items tagged; no deprecated/removed practice taught as current (e.g., Helm `apiVersion: v1` charts, `helm install` without `--version` pinning in CI, `stable` repo URL, Tiller/Helm 2 concepts, Kustomize `bases`/`patchesStrategicMerge`/`patchesJson6902`/`vars`, `commonLabels` mutating selectors, legacy Kustomize plugins as default, `helm repo add` of deprecated hosts, removed Kubernetes API versions in examples). | Stale or untagged claim. |
| 5 | **Security correctness** | No insecure practice shown as good; no overclaims (signing ≠ safe chart; verified ≠ trustworthy publisher; schema validation ≠ security; lint passing ≠ production-ready; `secretGenerator`/values ≠ secure secret storage; private repo ≠ safe from reading release Secrets; `--atomic` ≠ safe migration); plugin/post-renderer/hook code-execution risks stated; supply-chain risks of remote bases and third-party charts stated; secrets never shown realistically. | Overclaim or unlabeled insecure example. |
| 6 | **Fabrication scan** | Hunt for invented numbers, versions, fields, flags, plugin names/behaviors, outputs shown as measured, statistics, citations. | Any unsupported specific. |
| 7 | **Pedagogical consistency** | True beginner→advanced ramp; no concept used before introduced (e.g., no hooks before templates; no combining patterns before both tools are taught; no operator due diligence before CRDs); consistent terms; running example evolves coherently. | Undisclosed forward dependency; drift. |
| 8 | **Cross-consistency** | Questions test only taught content; capstone deliverables map to units; checklists match lessons; README matches content; cluster-needed/not-needed labels are correct; the Helm-vs-Kustomize guidance in Units 1, 2, 5, 6 and the capstone does not contradict itself; signing approach consistent between Unit 7 and the capstone. | Orphan item; contradiction. |
| 9 | **Adversarial review** | As a skeptical platform engineer and a security reviewer: list the 10 most likely objections ("what would break, mislead, or weaken supply-chain security in a real organization?") and resolve each. | Unresolved objection. |
| 10 | **Lab safety & feasibility** | Labs run within 4 CPU / 8 GB / 30 GB, are idempotent and context-guarded, never install unreviewed third-party code into a non-throwaway cluster, never publish outside the local registry, use throwaway keys, and clean up including CRDs and registry artifacts. | Hidden cost, resource blowout, wrong-cluster risk, unsafe supply-chain step, leftover state. |

## 12.3 Audit artifacts inside the syllabus (final appendices)

**Appendix A — Claim Register:** `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag`. ≥ **80 entries**, covering every version-sensitive, deprecation-related, and security-relevant claim.

**Appendix B — Audit Report:** `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk` for passes 1–10. Be candid; report real defects.

**Appendix C — Human Verification Checklist:** every `[VERIFY]` / `[VERSION-SENSITIVE]` item grouped by component (Helm CLI and chart spec, Helm hooks, Helm OCI/registry commands, Helm provenance, Kustomize fields and `kubectl kustomize` embedding, `helmCharts` inflation, kubeconform, helm-unittest, chart-testing, cosign, CRD/`apiextensions` fields, CloudNativePG chart location, Kubernetes API/deprecation items), each with *what to check*, *where (official doc name)*, *how to test with one command*. Closable by a reviewer in under 6 hours.

**Appendix D — Known Limitations and Assumptions:** what is out of scope (GitOps reconciliation — M08, secret management — M09, supply-chain enforcement — M12, IaC-managed Helm releases — M07, platform CRD design at scale — M16, production operator frameworks), assumed Helm/Kustomize/Kubernetes versions, local-registry insecure-mode caveats, anything unverified.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace a human running every template, overlay, and lab against the installed tool versions, and that **rendered output shown in the syllabus is representative, not captured from a real run**.

## 12.4 Trust rules
- If a pass finds a defect you cannot confidently fix, leave it visible as `OPEN` in Appendix B and list it in Appendix C. Never hide uncertainty.
- Never claim a command, template, or overlay "was run/tested" unless it actually was. Use "expected output (representative)".
- Never claim verification against live documentation unless you consulted it; otherwise say "written from knowledge of the documentation; verify against current docs".

# 13. OUTPUT FORMAT

- **One Markdown document:** `SYLLABUS-Helm-Kustomize-and-Kubernetes-Packaging.md`.
- Begin with: title, abstract paragraph, metadata block (`Module: M06`, `Stage: 2E`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 0–10 in order, then Appendices A–E.
- Headings: `#` title, `##` units, `###`/`####` below; tables for comparisons; fenced code with language tags; mermaid for diagrams. Helm template files in fenced blocks must not be mixed with their rendered output in the same block.
- Cross-link units with relative links to sibling target files.
- **Depth target:** Units 1–8 each ≥ 2,500 words of teaching text excluding code and manifests; ≥ 140 practice questions; capstone with complete code. **Do not compress to fit**—use the Delivery Protocol.
- No placeholder text, no "etc." in required lists, no "exercise left to the reader" for required deliverables.

# 14. DELIVERY PROTOCOL

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0, Unit 1 |
| 2 | Unit 2 |
| 3 | Units 3, 4 |
| 4 | Units 5, 6 |
| 5 | Units 7, 8 |
| 6 | Unit 9 (practice questions) |
| 7 | Unit 10 (capstone, full code) |
| 8 | Appendices A–E, including the cross-part audit |

Rules:
- End each part with: `PART n/8 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–10, scoped) **before** printing each part; maintain the Claim Register throughout.
- Part 8 runs the cross-part audit (passes 7, 8, 9 especially) and lists every correction to earlier parts as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If nearing the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 8 print: "Concatenate Parts 1–8 in order into `SYLLABUS-Helm-Kustomize-and-Kubernetes-Packaging.md` and apply all listed corrections."

# 15. DEFINITION OF DONE

- [ ] All 11 units present in order; Units 1–8 each have L1–L4 and sections N.0–N.14.
- [ ] Every Section 6 topic taught at its stated level; Helm/Kustomize version-sensitivity handled by tagging, never by assuming a version.
- [ ] Every template/overlay example shows its rendered output; the shown output is consistent with the input.
- [ ] The "rendered output is the review artifact" principle is taught, applied in CI scripts, and used in the capstone.
- [ ] Signing and provenance taught with explicit statements of what they do and do not prove; a tamper test is executed in a lab.
- [ ] ≥ 140 practice questions with model answers and distractor analysis, including "predict the rendered output" and SemVer-classification questions.
- [ ] Capstone has complete runnable code, acceptance criteria, rubric weighted toward tested upgrades/rollbacks and verify-before-install, `make verify`/`make ci`, and a blank measurement template.
- [ ] Every lab states cluster needed/not needed, has context guard (if cluster), steps, expected evidence, cleanup, and fits the local baseline; none installs unreviewed third-party code into a non-throwaway cluster.
- [ ] No fabricated versions, fields, flags, functions, numbers, or citations; every uncertainty tagged.
- [ ] Appendices A–E present; Claim Register ≥ 80; passes 1–10 reported candidly.
- [ ] Running example evolves coherently across all units.
- [ ] Forward references (M01–M05, M07, M08, M09, M12, M16, M17) explicit and not half-taught; the M08 GitOps handoff stated precisely.
- [ ] A human can close every open item in under 6 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/8**. Do not ask clarifying questions; record an `[ASSUMPTION]` where information is missing and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. Use one long conversation across all 8 parts so the Claim Register and running example stay consistent.
2. AI self-audit is not independent. Install your own Helm and Kustomize, render every example, and close every `[VERIFY]` item against the docs for your installed versions. The rendered outputs in the syllabus will be representative, not captured from real runs.
3. Highest fabrication risk, check first:
   - Helm behavior that differs between major versions (plugin system, OCI commands, `--wait`, `--reuse-values` variants, CRD handling).
   - Helm provenance flags and keyring format.
   - Current cosign command syntax.
   - Kustomize field names (`patches`, `replacements`, `components`, `helmCharts`, `labels` with `includeSelectors`).
   - The `kubectl` embedded Kustomize version.
   - helm-unittest, chart-testing and kubeconform flags.
   - The CloudNativePG chart location.
   - CRD conversion and CEL validation fields.
4. Scope decisions I made, which you can change:
   - The tooling map lists OCI chart distribution as Awareness, but this folder has a dedicated module for it. The prompt teaches it at working depth against the local registry from M01.
   - Keyless cosign signing stays Awareness only, because it needs public infrastructure. The lab uses key-based signing with throwaway keys.
   - GitOps reconciliation (Argo CD or Flux rendering charts and overlays) is deferred to M08, and the prompt says so wherever it comes up.
   - Operators are covered by concepts, a toy controller and inspection of CloudNativePG from M05. They are not taught as a Go development course.
5. Most labs in this module need no cluster. The prompt labels each lab "cluster needed" or "not needed", so you can save kind for the install, upgrade, rollback and hook labs.
6. Helm and Kustomize each have major-version differences. Record `helm version` and `kustomize version` in `versions.txt` before you start.
