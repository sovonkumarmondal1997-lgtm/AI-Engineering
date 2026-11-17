# Production DevOps Tooling Map — Stage 2E

> A vendor-neutral catalogue for selecting, practising, and operating the tools used across Stage 2E.

- **Last reviewed:** 2026-10-24
- **Tool-status data is point-in-time:** re-verify before adopting or standardizing a tool.
- **Scope:** tool catalogue and decision aid; not an installation guide, learning schedule, or tutorial.

## 1. Purpose and how to use this map

Use this map to answer four questions: what a tool does, which module introduces it, whether it fits the zero-budget lab, and what trade-offs matter. It intentionally separates hands-on Core tools from Awareness tools so a solo learner can build depth without installing every product named here.

Use [lab-environment-setup.md](lab-environment-setup.md) for installation steps, [local-lab-kind-minikube-and-localstack.md](local-lab-kind-minikube-and-localstack.md) for lab design, [free-tier-cloud-account-and-cost-safety.md](free-tier-cloud-account-and-cost-safety.md) for cloud safeguards, and [learning-plan.md](learning-plan.md) for sequencing. Use [prerequisites-and-exit-criteria.md](prerequisites-and-exit-criteria.md) for the gates.

**Legend**

- **Local:** intended to run on a local machine, local cluster, or local container engine; resource requirements still vary.
- **LocalStack:** uses AWS API emulation where supported; it is partial emulation, not cloud parity. Service/feature availability may vary by edition and change over time: **[VERIFY]**.
- **Free tier:** requires a real cloud or hosted-service account; terms and limits can change. Follow the cost-safety file.
- **Not feasible free:** the real capability depends on paid or external infrastructure; use the stated local simulation.
- **[VERIFY]:** confirm current maintenance, support, licensing/governance, API support, or service coverage from the named project's own documentation before adoption.
- **Core:** hands-on tool or workflow required by the stage's exit criteria. A Core workflow can use a small number of complementary tools where no single tool covers the whole job.
- **Awareness:** describe, compare, and explain trade-offs; operation is not required for stage completion.

## 2. How to choose a tool (decision framework)

1. **Problem fit:** state the production problem and the failure mode the tool is expected to reduce. Do not start with a product name.
2. **Operational burden:** estimate upgrades, backups, on-call, permissions, data retention, debugging, and recovery effort—not just installation time.
3. **Team skills:** prefer tools the team can diagnose under pressure. A technically capable tool that nobody can operate is operational risk.
4. **Ecosystem and community health:** review documentation quality, issue handling, release practices, security advisories, integrations, and the path for reporting defects.
5. **Licence and governance risk:** verify current licence, project governance, trademark/redistribution terms, and any enterprise/community feature split. Treat old blog posts as stale until confirmed.
6. **Integration with the existing stack:** check identity, source control, artifact formats, telemetry, policy, deployment model, and automation APIs.
7. **Lock-in and exit cost:** identify proprietary configuration, stored state, APIs, data formats, and the practical cost of exporting or replacing them.
8. **Security posture:** review permissions, credential flow, network exposure, auditability, patch response, signing/provenance support, and the default configuration.
9. **Cost at scale:** estimate compute, storage, telemetry retention, support, and engineer time. A free local demo says little about production total cost of ownership.
10. **Boring technology test:** ask whether a simpler, widely understood component already solves the problem. Add complexity only when it buys a measurable capability.

**Red flags when adopting a tool**

- The proposal starts with a demo rather than a problem statement or acceptance criteria.
- The operator cannot explain backup, restore, upgrade, and rollback procedures.
- Required features depend on an unverified paid tier or undocumented plugin.
- The project’s maintenance, ownership, licensing, or security response is unclear.
- It duplicates existing capabilities without a migration or ownership plan.
- A pilot has no exit criteria, no export path, or no way to measure operational burden.

## 3. Learning scope: Core vs Awareness

**Core** means hands-on practice is required and contributes evidence to the Gate Out criteria. **Awareness** means you can describe the problem, compare credible alternatives, explain trade-offs, and identify what would need validation before adoption; you are not expected to operate it in this stage.

The Core set is intentionally narrow: one primary choice per category where practical, with only the supporting components required to complete a real workflow. Core selections are driven by lab feasibility, inspectable evidence, and transferable concepts—not a claim that one product is universally superior.

Several categories necessarily use a workflow rather than a single product: CI/CD needs a runner plus tests/build steps; observability needs instrumentation and a backend; backup needs both a backup method and restore verification. In those cases, the map marks the minimum workable combination as Core.

## 4. Master tooling table

| Category | Tool | What it does (1 line) | Core/Awareness | Taught in (M##) | Free-lab feasibility | Main alternatives | Status note |
|---|---|---|---|---|---|---|---|
| Containers & registries | OCI image format | Shared image/artifact conventions | Core | M01 | Local | Docker image format; OCI Distribution Specification | Stable concept; verify selected implementation details. |
| Containers & registries | Docker Engine / Docker CLI | Build, run, inspect, and manage containers | Core | M01 | Local | Podman | Choose when the local lab already uses Docker; avoid assuming container runtime behavior is identical across platforms. |
| Containers & registries | BuildKit | Build images with reusable build steps and cache | Core | M01 | Local | Buildah; Buildah/Podman build | Choose for cache-aware builds; validate builder configuration and provenance needs. |
| Containers & registries | Local registry | Store and retrieve test images without a hosted registry | Core | M01 | Local | A registry supplied by the local cluster; hosted registries | Choose for digest and pull-policy practice; local access/authentication may differ from production. |
| Containers & registries | Trivy | Scan images and related artifacts for known vulnerabilities and configuration issues | Core | M01, M12 | Local | Grype; vendor scanners | Choose when a simple local scan is sufficient; findings depend on database freshness and image contents. |
| Containers & registries | Syft | Generate a software bill of materials (SBOM) | Core | M01, M12 | Local | Other SBOM generators | Choose to create inspectable inventory; an SBOM does not prove an artifact is safe. |
| Containers & registries | cosign | Sign and verify container artifacts and related attestations | Awareness | M01, M12 | Local | Other Sigstore components; registry-native signing | Choose when artifact identity and verification are requirements; trust-root and key management need deliberate design. |
| CI/CD | GitHub Actions | Run repository-triggered workflows and CI jobs | Core | M02 | Free tier | GitLab CI/CD; Jenkins; Buildkite | Choose if the repository and free allowance fit; avoid tying critical deployments to unreviewed third-party actions. |
| CI/CD | GitHub-hosted or local runner | Execute pipeline jobs in an isolated environment | Core | M02 | Free tier / Local | GitLab runners; Jenkins agents | Choose hosted runners for simplicity or local runners for lab control; isolate credentials and untrusted pull-request jobs. |
| CI/CD | pytest | Run Python tests as a CI quality gate | Core | M02 | Local | Language-specific test frameworks | Choose for Python services; tests must be deterministic and useful. |
| CI/CD | Ruff | Lint and format Python code in automated checks | Core | M02 | Local | Other linters and formatters | Choose for a compact Python toolchain; agree on configuration rather than mixing competing formatters. |
| CI/CD | Build cache | Reuse valid build/dependency outputs | Core | M02 | Local / Free tier | Remote cache services | Choose when measured build time justifies it; do not cache secrets or trust untrusted cache writes. |
| CI/CD | Artifact digest / checksum | Identify the exact artifact promoted between stages | Core | M02, M17 | Local | Signed provenance systems | Choose immutable identifiers over mutable tags; digest alone does not establish provenance. |
| Kubernetes platform & operations | kind | Run Kubernetes clusters using containers | Core | M03, M14 | Local | minikube; k3d | Choose for repeatable disposable clusters; host networking and cloud integrations differ from production. |
| Kubernetes platform & operations | kubectl | Inspect and change Kubernetes resources | Core | M03 | Local | Kubernetes client libraries | Choose as the baseline operational interface; always confirm context and namespace before destructive commands. |
| Kubernetes platform & operations | minikube | Run a local Kubernetes learning cluster | Awareness | M03 | Local | kind; k3d | Choose when its add-ons fit the lab; avoid running several local distributions without a learning reason. |
| Kubernetes platform & operations | Metrics Server | Provide resource metrics used by some Kubernetes features and commands | Core | M03, M15 | Local | Other compatible metrics providers | Choose for basic resource metrics and HPA practice; it is not a full observability backend. |
| Kubernetes platform & operations | Kubernetes HPA | Scale workload replicas based on configured metrics | Core | M03, M15 | Local | KEDA for event-driven scaling; custom controllers | Choose when the metric and scaling behavior are understood; avoid scaling on noisy or irrelevant signals. |
| Kubernetes platform & operations | Admission policy (Kyverno or OPA Gatekeeper) | Enforce selected resource policies at admission time | Awareness | M03, M12, M16 | Local | Built-in admission controls; other policy engines | Choose when preventive guardrails are needed; policy failures can block deployments. [VERIFY] APIs and maintenance. |
| Kubernetes platform & operations | Kubernetes version/support policy | Guide upgrade and client/control-plane compatibility | Core | M03 | Local | Distribution-specific support policy | Choose supported combinations and rehearse upgrades; verify upstream policy before changing versions. |
| Networking, ingress & service mesh | CNI plugin | Provide pod networking and possibly NetworkPolicy enforcement | Core | M04 | Local | Cilium; Calico; cluster-provided CNI | Choose based on required policy/features; confirm the chosen local cluster actually enforces policies. |
| Networking, ingress & service mesh | Kubernetes Service and DNS | Provide stable service discovery and in-cluster routing | Core | M04 | Local | Application-specific discovery | Choose as the baseline; stale endpoints and wrong selectors commonly cause outages. |
| Networking, ingress & service mesh | Ingress API / controller | Route HTTP(S) traffic into a cluster | Core | M04 | Local | Gateway API implementations | Choose for a simple HTTP routing lab where supported; controller maintenance status must be checked. [VERIFY] |
| Networking, ingress & service mesh | Gateway API | Express Kubernetes traffic-routing intent through role-oriented APIs | Awareness | M04 | Local | Ingress API and controllers | Choose when supported by the chosen implementation and use case; API support varies. [VERIFY] |
| Networking, ingress & service mesh | cert-manager | Automate certificate lifecycle for supported Kubernetes integrations | Awareness | M04, M09 | Local | External certificate automation | Choose when certificate automation is part of the lab; issuer and trust setup are easy to misconfigure. |
| Networking, ingress & service mesh | Service mesh (for example Istio or Linkerd) | Add service-to-service traffic policy, telemetry, and potentially mTLS | Awareness | M04, M11 | Local | Native Kubernetes networking; application libraries | Choose only for demonstrated cross-service requirements; avoid introducing a mesh to solve a single routing problem. [VERIFY] |
| Networking, ingress & service mesh | CoreDNS | Provide cluster DNS service | Core | M04 | Local | Distribution-provided DNS | Choose the cluster's supported DNS implementation; DNS failures can look like application failures. |
| Storage & stateful workloads | PersistentVolume / PersistentVolumeClaim | Request and bind persistent storage for workloads | Core | M05 | Local | Cloud block/file storage integrations | Choose for Kubernetes storage lifecycle practice; local provisioners do not model cloud durability guarantees. |
| Storage & stateful workloads | Container Storage Interface (CSI) | Standardize storage integration with Kubernetes | Awareness | M05 | Local / Free tier | Distribution-specific storage plugins | Choose according to the storage backend; driver capabilities vary. |
| Storage & stateful workloads | StatefulSet | Manage workloads with stable identity and storage association | Core | M05 | Local | Operators; other workload controllers | Choose when stable identity/order matters; it does not itself provide database high availability. |
| Storage & stateful workloads | Volume snapshots | Capture supported point-in-time volume state | Awareness | M05, M13 | Local / Free tier | Application-consistent backups | Choose only if the driver supports snapshots; verify restore consistency separately. |
| Storage & stateful workloads | CloudNativePG or another database operator | Automate selected database lifecycle tasks in Kubernetes | Awareness | M05 | Local | Managed database service; manual database operations | Choose when operator behavior is the learning objective; operator complexity is not a substitute for database expertise. [VERIFY] |
| Storage & stateful workloads | Velero | Back up and restore Kubernetes resources and supported persistent data integrations | Awareness | M13 | Local / Free tier | Application-native backups; storage snapshots | Choose after validating the exact storage/plugin path; local object-store simulation has limits. |
| Packaging | Helm | Template, package, install, and upgrade Kubernetes applications | Core | M06 | Local | Kustomize; plain manifests | Choose for reusable charts and release lifecycle; avoid treating chart values as a stable public API without compatibility discipline. |
| Packaging | Kustomize | Compose Kubernetes manifests with bases and overlays | Core | M06 | Local | Helm; plain manifests | Choose for patch-based environment differences; complex overlays can become hard to reason about. |
| Packaging | OCI chart distribution | Distribute charts through compatible OCI registries | Awareness | M06 | Local | Chart repositories | Choose when registry-based artifact workflows are desired; verify registry and tooling support. |
| Infrastructure as Code & cloud operations | Terraform | Declare infrastructure and produce plans before changes | Core | M07 | Local / Free tier | OpenTofu; cloud-native IaC tools | Choose when the team already depends on its ecosystem; verify licence/governance and provider needs. Status note: [VERIFY] current licensing and governance. |
| Infrastructure as Code & cloud operations | OpenTofu | Open-source Terraform-compatible IaC workflow | Awareness | M07 | Local / Free tier | Terraform | Choose when governance requirements favor it; test provider/module compatibility. Status note: [VERIFY] project governance and compatibility. |
| Infrastructure as Code & cloud operations | LocalStack | Emulate selected cloud APIs for local development | Core | M07, M17 | LocalStack | Cloud provider SDKs against a real account | Choose for fast local integration tests; emulation is partial and some services/features may require a paid tier. [VERIFY] |
| Infrastructure as Code & cloud operations | Terraform/OpenTofu local provider or local resources | Practice plans and state without provisioning paid cloud resources | Core | M07 | Local | LocalStack; real cloud free tier | Choose for lifecycle and state concepts; it does not prove cloud IAM/networking parity. |
| Infrastructure as Code & cloud operations | Checkov | Scan IaC for selected policy/security issues | Awareness | M07, M12 | Local | tfsec-class scanners; provider policy tools | Choose for an additional automated review layer; verify rule relevance and false positives. |
| Infrastructure as Code & cloud operations | Ansible | Configure systems through repeatable automation | Awareness | M07 | Local | Cloud-init; image baking; configuration management alternatives | Choose when configuration management is actually required; avoid using it to duplicate declarative platform controllers. |
| GitOps & progressive delivery | Argo CD | Reconcile Kubernetes applications from Git | Core | M08 | Local | Flux | Choose when a visible UI and application-oriented workflow suit the team; protect its control plane and credentials. |
| GitOps & progressive delivery | Flux | Reconcile cluster state from Git using controllers | Awareness | M08 | Local | Argo CD | Choose for controller/composition-oriented workflows; compare operational model and team familiarity. |
| GitOps & progressive delivery | Argo Rollouts | Manage canary and blue/green application rollout strategies | Awareness | M08, M17 | Local | Native Deployment rolling updates; Flagger | Choose when progressive analysis/traffic control is needed; requires compatible metrics/traffic integrations. [VERIFY] |
| GitOps & progressive delivery | Flagger | Automate progressive delivery with supported routing/metrics integrations | Awareness | M08 | Local | Argo Rollouts; native rolling updates | Choose where the selected integrations are supported; verify current maintenance and compatibility. [VERIFY] |
| Secrets & identity | Kubernetes Secrets and RBAC | Store cluster secret objects and constrain access | Core | M09 | Local | External secret manager integrations | Choose for the first local exercise; configure least privilege and understand encryption-at-rest limitations. |
| Secrets & identity | External Secrets Operator | Sync secrets from supported external providers into Kubernetes | Awareness | M09 | Local / Free tier | Secrets Store CSI Driver; provider-specific integrations | Choose when a real external secret backend exists; a local demo does not prove cloud identity setup. [VERIFY] |
| Secrets & identity | HashiCorp Vault | Centralize secret storage, access policies, and selected dynamic-secret/PKI workflows | Awareness | M09 | Local / Free tier | OpenBao; cloud secret managers | Choose when its operational capabilities justify operating it; plan unsealing, upgrades, backups, and policy management. Status note: [VERIFY] licensing/governance. |
| Secrets & identity | OpenBao | Secret-management alternative in the Vault ecosystem | Awareness | M09 | Local | Vault; cloud secret managers | Compare feature compatibility and support requirements before migration. Status note: [VERIFY] governance and compatibility. |
| Secrets & identity | OIDC / SSO | Federate identity and authenticate users or workloads through supported flows | Awareness | M09, M16 | Local / Free tier | SAML-based SSO; platform identity integrations | Choose based on identity provider and application support; validate issuer, audience, and redirect configuration. |
| Secrets & identity | Workload identity | Give workloads short-lived identity without embedding long-lived cloud keys | Awareness | M09 | Free tier / Not feasible free | Cloud-specific identity integrations | Choose in a real cloud when supported; simulate the trust flow locally and do not claim cloud parity. |
| SRE & incident management | SLI/SLO and error-budget worksheet | Define service outcomes and a risk-based reliability target | Core | M10 | Local | Dedicated SLO platforms | Choose a transparent worksheet first; avoid targets without user relevance or measurement quality. |
| SRE & incident management | Prometheus alert rules | Express measurable conditions that require action | Core | M10, M11 | Local | Other alerting backends | Choose when signals are available and the alert has an owner/runbook; avoid paging on every transient symptom. |
| SRE & incident management | Incident timeline and postmortem template | Record impact, detection, response, contributing factors, and actions | Core | M10 | Local | Incident-management platforms | Choose a simple template for solo labs; do not confuse a written simulation with a real on-call system. |
| SRE & incident management | On-call/paging platform | Route actionable alerts to responders | Awareness | M10 | Free tier / Not feasible free | PagerDuty-class services; Opsgenie-class services | Choose when real responder rotations exist; use a local simulated escalation for zero-budget study. [VERIFY] product status and terms. |
| Observability | Prometheus | Collect and query time-series metrics | Core | M11 | Local | VictoriaMetrics; managed metrics services | Choose for local metrics and alert practice; high-cardinality labels can create cost and memory problems. |
| Observability | Grafana | Explore metrics and build operational dashboards | Core | M11 | Local | Backend-native dashboards | Choose for multi-source visualisation; dashboards need ownership and meaningful units. |
| Observability | OpenTelemetry | Provide APIs/SDKs and collection conventions for telemetry | Core | M11 | Local | Vendor-specific agents/SDKs | Choose for portable instrumentation; collector pipelines and semantic conventions still require configuration. |
| Observability | Loki | Aggregate and query logs using a label-oriented model | Awareness | M11 | Local | OpenSearch; Elasticsearch-class systems | Choose when a compact local log stack fits; label design and retention need care. |
| Observability | Jaeger | Collect and inspect distributed traces | Awareness | M11 | Local | Tempo; vendor tracing services | Choose for trace learning; traces require instrumentation and sampling decisions. |
| Observability | Alertmanager | Group, route, and manage Prometheus alerts | Core | M10, M11 | Local | Other alert-routing systems | Choose with Prometheus alerting; routing mistakes can silence important incidents or flood responders. |
| Security & supply chain | SBOM | Inventory components included in an artifact | Core | M12 | Local | Other SBOM formats/generators | Choose as an inventory artifact; ensure the format and completeness fit downstream consumers. |
| Security & supply chain | cosign signing/verification | Bind artifact identity to a verifiable signature or attestation | Awareness | M12 | Local | Other artifact-signing approaches | Choose when verification policy is defined; keyless/key-based trust setup must be reviewed. |
| Security & supply chain | Trivy | Scan image and dependency inputs for known vulnerabilities | Core | M12 | Local | Grype; vendor scanners | Choose for local triage; keep databases current and prioritize exploitability/context rather than raw counts. |
| Security & supply chain | Kyverno / OPA Gatekeeper | Validate or mutate Kubernetes resources against policy | Awareness | M12, M16 | Local | Admission policies and CI policy checks | Choose for enforceable guardrails; start in audit/reporting mode where possible. [VERIFY] current APIs and maintenance. |
| Security & supply chain | Falco | Detect selected runtime behaviors using rules and runtime signals | Awareness | M12 | Local | Cloud runtime detection; other runtime sensors | Choose when runtime detection is a stated objective; kernel/runtime support and alert tuning matter. [VERIFY] |
| Security & supply chain | kube-bench | Check selected Kubernetes configuration against CIS benchmark guidance | Awareness | M12 | Local | Distribution security checks; manual benchmark review | Choose for structured audit practice; confirm benchmark version and applicability. [VERIFY] |
| Backup, DR & resilience testing | Application-native backup | Export data using the application's supported consistency mechanism | Core | M13 | Local | Volume snapshots; database-specific backup tools | Choose when transaction consistency matters; test the restore path and required dependencies. |
| Backup, DR & resilience testing | Checksums / verification queries | Prove restored files or records match expected data | Core | M13 | Local | Application-specific integrity checks | Choose a deterministic verification method; matching a file checksum does not prove the whole service works. |
| Backup, DR & resilience testing | Velero | Back up and restore supported Kubernetes resources and persistent data integrations | Awareness | M13 | Local / Free tier | Application-native backup; storage-native snapshots | Choose only after validating plugin and storage support; test restore to a clean target. |
| Backup, DR & resilience testing | Chaos Mesh / LitmusChaos | Inject controlled failures for resilience experiments | Awareness | M13, M17 | Local | Manual fault injection; application-level tests | Choose when the experiment has clear hypotheses and guardrails; avoid uncontrolled experiments. [VERIFY] current compatibility. |
| Multi-cluster & multi-region | Two kind clusters | Simulate separate cluster failure domains | Core | M14 | Local | Two minikube clusters; separate namespaces for limited exercises | Choose for low-cost failover reasoning; do not claim real regional independence. |
| Multi-cluster & multi-region | kubectl contexts | Select and inspect multiple cluster endpoints | Core | M14 | Local | Fleet-management tools | Choose for small-scale learning; context mistakes can direct commands to the wrong cluster. |
| Multi-cluster & multi-region | Cluster API | Manage Kubernetes cluster lifecycle through declarative APIs | Awareness | M14 | Local / Free tier | Provider-managed cluster lifecycle tools | Choose when cluster lifecycle automation is in scope; provider and infrastructure integration increase complexity. [VERIFY] |
| Multi-cluster & multi-region | Global traffic management | Direct users across endpoints or regions based on policy/health | Awareness | M14 | Not feasible free | DNS failover; cloud global load balancing | Simulate endpoint switching locally; true global routing and failure detection require real infrastructure. |
| Multi-cluster & multi-region | Fleet management (for example, a multi-cluster GitOps pattern) | Apply consistent desired state across multiple clusters | Awareness | M14 | Local | Argo CD multi-cluster patterns; Flux patterns | Choose when fleet policy and drift control are required; verify the chosen project's current supported pattern. |
| FinOps & capacity | kubectl top / Metrics Server | Observe current pod/node resource usage | Core | M15 | Local | Prometheus-based usage dashboards | Choose for basic snapshots; short windows and missing historical context limit conclusions. |
| FinOps & capacity | HPA | Scale replicas based on configured metrics | Core | M15 | Local | KEDA; custom controllers | Choose when the target metric tracks demand; account for startup delay, min/max replicas, and downstream bottlenecks. |
| FinOps & capacity | Capacity and unit-economics worksheet | Model resource demand and cost per request/job from explicit assumptions | Core | M15 | Local | FinOps platforms | Choose first for a solo learner; label prices as hypothetical unless verified from provider pricing sources. |
| FinOps & capacity | OpenCost | Attribute Kubernetes resource costs using supported data sources | Awareness | M15 | Local | Kubecost-class tools; cloud billing exports | Choose when cluster cost allocation is required; verify compatibility and current project status. [VERIFY] |
| FinOps & capacity | Cluster autoscaler | Adjust cluster node capacity based on scheduling demand | Awareness | M15 | Not feasible free / Free tier | Managed node autoscaling; Karpenter-class provisioning | Simulate pending pods and capacity decisions locally; actual node provisioning requires a compatible infrastructure provider. |
| Platform engineering & IDPs | Golden-path template repository | Provide a reusable service skeleton with documented defaults | Core | M16 | Local | Cookiecutter; Copier; internal templates | Choose the simplest scaffold that users can maintain; avoid generating a framework larger than the service. |
| Platform engineering & IDPs | Backstage | Provide a developer portal and software catalog extensibility | Awareness | M16 | Local | A lightweight docs/catalog site; other IDP portals | Choose when catalog, ownership, and workflow integration justify operating a portal; plugin governance and upgrades add work. [VERIFY] |
| Platform engineering & IDPs | Crossplane | Manage external infrastructure through Kubernetes-style APIs | Awareness | M16 | Local / Free tier | Terraform/OpenTofu; cloud-native IaC | Choose when platform APIs and control-plane composition are needed; avoid adding a second control plane without a clear boundary. [VERIFY] |
| Platform engineering & IDPs | Cookiecutter / Copier | Generate projects from templates | Awareness | M16 | Local | Repository templates; custom scaffolding | Choose when consistent project initialization saves real effort; test template upgrades and generated defaults. |
| Platform engineering & IDPs | Policy and validation checks | Prevent unsafe defaults in the golden path | Core | M16 | Local | CI checks; admission policy | Choose the least complex enforceable control; make failures actionable and documented. |

## 5. Category deep-dives

### Containers & registries

Container images package an application and its runtime dependencies; registries store and distribute those artifacts. Image hygiene reduces attack surface and makes releases traceable.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| OCI image format | Shared image/artifact conventions | Stable concept; verify selected implementation details. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Docker image format; OCI Distribution Specification. | Core |
| Docker Engine / Docker CLI | Build, run, inspect, and manage containers | Choose when the local lab already uses Docker; avoid assuming container runtime behavior is identical across platforms. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Podman. | Core |
| BuildKit | Build images with reusable build steps and cache | Choose for cache-aware builds; validate builder configuration and provenance needs. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Buildah; Buildah/Podman build. | Core |
| Local registry | Store and retrieve test images without a hosted registry | Choose for digest and pull-policy practice; local access/authentication may differ from production. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: A registry supplied by the local cluster; hosted registries. | Core |
| Trivy | Scan images and related artifacts for known vulnerabilities and configuration issues | Choose when a simple local scan is sufficient; findings depend on database freshness and image contents. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Grype; vendor scanners. | Core |
| Syft | Generate a software bill of materials (SBOM) | Choose to create inspectable inventory; an SBOM does not prove an artifact is safe. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Other SBOM generators. | Core |
| cosign | Sign and verify container artifacts and related attestations | Choose when artifact identity and verification are requirements; trust-root and key management need deliberate design. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Other Sigstore components; registry-native signing. | Awareness |

**Production gotchas**

- Mutable tags can cause a redeploy to pull a different image than the one tested.
- A scan report without triage, ownership, and remediation policy becomes dashboard noise.
- Registry credentials or build secrets can leak through build arguments, logs, or layers.

**Core smoke checks**

- **Docker Engine / Docker CLI:**
```bash
docker version
```
- **BuildKit:**
```bash
docker buildx version
```
- **Local registry:**
```bash
docker ps
```
- **Trivy:**
```bash
trivy --version
```
- **Syft:**
```bash
syft version
```

### CI/CD

CI validates changes before they become releasable; delivery automation promotes known artifacts with repeatable controls. The runner, credentials, cache, and artifact boundary are part of the security design.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| GitHub Actions | Run repository-triggered workflows and CI jobs | Choose if the repository and free allowance fit; avoid tying critical deployments to unreviewed third-party actions. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: GitLab CI/CD; Jenkins; Buildkite. | Core |
| GitHub-hosted or local runner | Execute pipeline jobs in an isolated environment | Choose hosted runners for simplicity or local runners for lab control; isolate credentials and untrusted pull-request jobs. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: GitLab runners; Jenkins agents. | Core |
| pytest | Run Python tests as a CI quality gate | Choose for Python services; tests must be deterministic and useful. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Language-specific test frameworks. | Core |
| Ruff | Lint and format Python code in automated checks | Choose for a compact Python toolchain; agree on configuration rather than mixing competing formatters. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Other linters and formatters. | Core |
| Build cache | Reuse valid build/dependency outputs | Choose when measured build time justifies it; do not cache secrets or trust untrusted cache writes. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Remote cache services. | Core |
| Artifact digest / checksum | Identify the exact artifact promoted between stages | Choose immutable identifiers over mutable tags; digest alone does not establish provenance. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Signed provenance systems. | Core |

**Production gotchas**

- Untrusted pull-request code can exfiltrate runner credentials if job boundaries are weak.
- Cache poisoning or over-broad cache reuse can undermine reproducibility.
- A green pipeline is not proof that rollback and runtime health work.

**Core smoke checks**

- **GitHub Actions:**
```bash
git status --short
```
- **GitHub-hosted or local runner:**
```bash
git status --short
```
- **pytest:**
```bash
python -m pytest --version
```
- **Ruff:**
```bash
ruff --version
```
- **Build cache:**
```bash
docker buildx du
```
- **Artifact digest / checksum:**
```bash
sha256sum <artifact-file>
```

### Kubernetes platform & operations

Kubernetes schedules and reconciles workloads, while operators remain responsible for application health, capacity, upgrades, and failure handling. Local clusters teach core APIs but cannot reproduce every managed-control-plane behavior.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| kind | Run Kubernetes clusters using containers | Choose for repeatable disposable clusters; host networking and cloud integrations differ from production. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: minikube; k3d. | Core |
| kubectl | Inspect and change Kubernetes resources | Choose as the baseline operational interface; always confirm context and namespace before destructive commands. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Kubernetes client libraries. | Core |
| minikube | Run a local Kubernetes learning cluster | Choose when its add-ons fit the lab; avoid running several local distributions without a learning reason. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: kind; k3d. | Awareness |
| Metrics Server | Provide resource metrics used by some Kubernetes features and commands | Choose for basic resource metrics and HPA practice; it is not a full observability backend. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Other compatible metrics providers. | Core |
| Kubernetes HPA | Scale workload replicas based on configured metrics | Scaling only helps when metrics reflect demand and downstream capacity exists. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: KEDA for event-driven scaling; custom controllers. | Core |
| Admission policy (Kyverno or OPA Gatekeeper) | Enforce selected resource policies at admission time | Choose when preventive guardrails are needed; policy failures can block deployments. [VERIFY] APIs and maintenance. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Built-in admission controls; other policy engines. | Awareness |
| Kubernetes version/support policy | Guide upgrade and client/control-plane compatibility | Choose supported combinations and rehearse upgrades; verify upstream policy before changing versions. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Distribution-specific support policy. | Core |

**Production gotchas**

- Wrong context or namespace can turn a safe command into a production incident.
- Bad probes can cause restart loops or send traffic to unready pods.
- Requests and limits that ignore workload behavior cause scheduling failures or throttling.

**Core smoke checks**

- **kind:**
```bash
kind get clusters
```
- **kubectl:**
```bash
kubectl config current-context
```
- **Metrics Server:**
```bash
kubectl top nodes
```
- **Kubernetes HPA:**
```bash
kubectl get hpa --all-namespaces
```

### Networking, ingress & service mesh

Cluster networking connects workloads and exposes services to clients. NetworkPolicy, ingress routing, DNS, and certificate handling solve different layers and should be tested independently.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| CNI plugin | Provide pod networking and possibly NetworkPolicy enforcement | Choose based on required policy/features; confirm the chosen local cluster actually enforces policies. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Cilium; Calico; cluster-provided CNI. | Core |
| Kubernetes Service and DNS | Provide stable service discovery and in-cluster routing | DNS errors can resemble application failures; inspect selectors, endpoints, and resolution separately. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Application-specific discovery. | Core |
| Ingress API / controller | Route HTTP(S) traffic into a cluster | Choose for a simple HTTP routing lab where supported; controller maintenance status must be checked. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Gateway API implementations. | Core |
| Gateway API | Express Kubernetes traffic-routing intent through role-oriented APIs | Choose when supported by the chosen implementation and use case; API support varies. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Ingress API and controllers. | Awareness |
| cert-manager | Automate certificate lifecycle for supported Kubernetes integrations | Choose when certificate automation is part of the lab; issuer and trust setup are easy to misconfigure. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: External certificate automation. | Awareness |
| Service mesh (for example Istio or Linkerd) | Add service-to-service traffic policy, telemetry, and potentially mTLS | Adds control-plane, policy, and debugging complexity. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Native Kubernetes networking; application libraries. | Awareness |
| CoreDNS | Provide cluster DNS service | DNS errors can resemble application failures; inspect selectors, endpoints, and resolution separately. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Distribution-provided DNS. | Core |

**Production gotchas**

- NetworkPolicy has no effect unless the network implementation enforces it.
- A missing service endpoint or DNS issue can be misdiagnosed as an application bug.
- A mesh adds certificate, policy, sidecar, and observability failure modes.

**Core smoke checks**

- **CNI plugin:**
```bash
kubectl get pods --all-namespaces
```
- **Kubernetes Service and DNS:**
```bash
kubectl get services --all-namespaces
```
- **Ingress API / controller:**
```bash
kubectl get ingress --all-namespaces
```
- **CoreDNS:**
```bash
kubectl get pods -n kube-system
```

### Storage & stateful workloads

Stateful services need persistent storage, lifecycle management, and verified recovery. A pod restart test is not the same as a node-loss or storage-system disaster-recovery test.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| PersistentVolume / PersistentVolumeClaim | Request and bind persistent storage for workloads | Choose for Kubernetes storage lifecycle practice; local provisioners do not model cloud durability guarantees. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Cloud block/file storage integrations. | Core |
| Container Storage Interface (CSI) | Standardize storage integration with Kubernetes | Choose according to the storage backend; driver capabilities vary. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Distribution-specific storage plugins. | Awareness |
| StatefulSet | Manage workloads with stable identity and storage association | Choose when stable identity/order matters; it does not itself provide database high availability. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Operators; other workload controllers. | Core |
| Volume snapshots | Capture supported point-in-time volume state | Driver/plugin support and restore consistency must be tested. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Application-consistent backups. | Awareness |
| CloudNativePG or another database operator | Automate selected database lifecycle tasks in Kubernetes | Choose when operator behavior is the learning objective; operator complexity is not a substitute for database expertise. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Managed database service; manual database operations. | Awareness |
| Velero | Back up and restore Kubernetes resources and supported persistent data integrations | Driver/plugin support and restore consistency must be tested. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Application-native backups; storage snapshots. | Awareness |

**Production gotchas**

- A PVC being bound does not guarantee application-level consistency.
- Snapshots may require a compatible driver and may not be application-consistent.
- StatefulSet does not automatically provide database replication or disaster recovery.

**Core smoke checks**

- **PersistentVolume / PersistentVolumeClaim:**
```bash
kubectl get pv,pvc --all-namespaces
```
- **StatefulSet:**
```bash
kubectl get statefulsets --all-namespaces
```

### Packaging

Packaging separates reusable application configuration from environment-specific values. Rendering and reviewing the final manifests matters more than choosing a fashionable packaging tool.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| Helm | Template, package, install, and upgrade Kubernetes applications | Templating and values compatibility need review discipline. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Kustomize; plain manifests. | Core |
| Kustomize | Compose Kubernetes manifests with bases and overlays | Choose for patch-based environment differences; complex overlays can become hard to reason about. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Helm; plain manifests. | Core |
| OCI chart distribution | Distribute charts through compatible OCI registries | Choose when registry-based artifact workflows are desired; verify registry and tooling support. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Chart repositories. | Awareness |

**Production gotchas**

- Rendered manifests can differ from what a learner assumes the chart emits.
- Environment overlays can silently diverge and become difficult to review.
- Breaking chart values can break downstream users even when templates render.

**Core smoke checks**

- **Helm:**
```bash
helm version
```
- **Kustomize:**
```bash
kubectl kustomize .
```

### Infrastructure as Code & cloud operations

IaC makes infrastructure changes reviewable and repeatable. State, credentials, provider behavior, drift, and deletion are operational concerns, not incidental details.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| Terraform | Declare infrastructure and produce plans before changes | State and provider behavior require careful handling; verify current governance. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: OpenTofu; cloud-native IaC tools. | Core |
| OpenTofu | Open-source Terraform-compatible IaC workflow | State and provider behavior require careful handling; verify current governance. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Terraform. | Awareness |
| LocalStack | Emulate selected cloud APIs for local development | Emulation is partial; do not assume service parity. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Cloud provider SDKs against a real account. | Core |
| Terraform/OpenTofu local provider or local resources | Practice plans and state without provisioning paid cloud resources | State and provider behavior require careful handling; verify current governance. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: LocalStack; real cloud free tier. | Core |
| Checkov | Scan IaC for selected policy/security issues | Choose for an additional automated review layer; verify rule relevance and false positives. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: tfsec-class scanners; provider policy tools. | Awareness |
| Ansible | Configure systems through repeatable automation | Choose when configuration management is actually required; avoid using it to duplicate declarative platform controllers. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Cloud-init; image baking; configuration management alternatives. | Awareness |

**Production gotchas**

- State loss or concurrent changes can corrupt the operator's view of infrastructure.
- A plan can still be unsafe if provider assumptions or credentials are wrong.
- Local emulation does not prove real cloud IAM, networking, or billing behavior.

**Core smoke checks**

- **Terraform:**
```bash
terraform version
```
- **LocalStack:**
```bash
localstack --version
```

### GitOps & progressive delivery

GitOps reconciles declared state from version control; progressive delivery controls how changes reach users. Git history alone is not a rollout safety strategy.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| Argo CD | Reconcile Kubernetes applications from Git | Choose when a visible UI and application-oriented workflow suit the team; protect its control plane and credentials. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Flux. | Core |
| Flux | Reconcile cluster state from Git using controllers | Choose for controller/composition-oriented workflows; compare operational model and team familiarity. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Argo CD. | Awareness |
| Argo Rollouts | Manage canary and blue/green application rollout strategies | Choose when progressive analysis/traffic control is needed; requires compatible metrics/traffic integrations. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Native Deployment rolling updates; Flagger. | Awareness |
| Flagger | Automate progressive delivery with supported routing/metrics integrations | Choose where the selected integrations are supported; verify current maintenance and compatibility. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Argo Rollouts; native rolling updates. | Awareness |

**Production gotchas**

- A reconciler can faithfully restore an unsafe desired state.
- Secrets committed to Git remain a security incident even after deletion from the latest commit.
- Canary analysis without reliable signals can promote a broken release.

**Core smoke checks**

- **Argo CD:**
```bash
argocd version --client
```

### Secrets & identity

Secret systems control sensitive values; identity systems determine who or what can act. Encryption alone does not solve authorization, rotation, audit, or workload identity.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| Kubernetes Secrets and RBAC | Store cluster secret objects and constrain access | Choose for the first local exercise; configure least privilege and understand encryption-at-rest limitations. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: External secret manager integrations. | Core |
| External Secrets Operator | Sync secrets from supported external providers into Kubernetes | Choose when a real external secret backend exists; a local demo does not prove cloud identity setup. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Secrets Store CSI Driver; provider-specific integrations. | Awareness |
| HashiCorp Vault | Centralize secret storage, access policies, and selected dynamic-secret/PKI workflows | Secret-manager operation, policy, backups, and upgrade burden are significant. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: OpenBao; cloud secret managers. | Awareness |
| OpenBao | Secret-management alternative in the Vault ecosystem | Secret-manager operation, policy, backups, and upgrade burden are significant. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Vault; cloud secret managers. | Awareness |
| OIDC / SSO | Federate identity and authenticate users or workloads through supported flows | Choose based on identity provider and application support; validate issuer, audience, and redirect configuration. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: SAML-based SSO; platform identity integrations. | Awareness |
| Workload identity | Give workloads short-lived identity without embedding long-lived cloud keys | Choose in a real cloud when supported; simulate the trust flow locally and do not claim cloud parity. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Cloud-specific identity integrations. | Awareness |

**Production gotchas**

- Over-broad RBAC exposes secrets to unrelated workloads or users.
- Rotation is incomplete until consumers have reloaded credentials and the old credential is rejected.
- Long-lived cloud keys in workloads defeat workload-identity goals.

**Core smoke checks**

- **Kubernetes Secrets and RBAC:**
```bash
kubectl auth can-i get secrets --namespace <namespace>
```

### SRE & incident management

SRE makes reliability goals explicit and uses operational evidence to manage risk. Incident tooling supports coordination, but clear roles, runbooks, and learning matter more than a vendor interface.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| SLI/SLO and error-budget worksheet | Define service outcomes and a risk-based reliability target | Choose a transparent worksheet first; avoid targets without user relevance or measurement quality. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Dedicated SLO platforms. | Core |
| Prometheus alert rules | Express measurable conditions that require action | Retention and label cardinality affect memory and operating cost. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Other alerting backends. | Core |
| Incident timeline and postmortem template | Record impact, detection, response, contributing factors, and actions | Choose a simple template for solo labs; do not confuse a written simulation with a real on-call system. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Incident-management platforms. | Core |
| On-call/paging platform | Route actionable alerts to responders | Choose when real responder rotations exist; use a local simulated escalation for zero-budget study. [VERIFY] product status and terms. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: PagerDuty-class services; Opsgenie-class services. | Awareness |

**Production gotchas**

- An SLO without a measurable user outcome is not operationally useful.
- Alerts without owners or runbooks create noise and delayed response.
- Postmortem actions without owners and follow-up do not reduce recurrence.

**Core smoke checks**

- **SLI/SLO and error-budget worksheet:**
```bash
python -c "print('SLI/SLO worksheet: record numerator, denominator, window, target')"
```
- **Prometheus alert rules:**
```bash
promtool check rules <rules-file>
```
- **Incident timeline and postmortem template:**
```bash
git status --short
```

### Observability

Metrics show trends, logs capture event detail, and traces connect work across service boundaries. Instrumentation, cardinality, retention, sampling, and alert quality determine operational usefulness.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| Prometheus | Collect and query time-series metrics | Retention and label cardinality affect memory and operating cost. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: VictoriaMetrics; managed metrics services. | Core |
| Grafana | Explore metrics and build operational dashboards | Choose for multi-source visualisation; dashboards need ownership and meaningful units. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Backend-native dashboards. | Core |
| OpenTelemetry | Provide APIs/SDKs and collection conventions for telemetry | Choose for portable instrumentation; collector pipelines and semantic conventions still require configuration. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Vendor-specific agents/SDKs. | Core |
| Loki | Aggregate and query logs using a label-oriented model | Choose when a compact local log stack fits; label design and retention need care. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: OpenSearch; Elasticsearch-class systems. | Awareness |
| Jaeger | Collect and inspect distributed traces | Choose for trace learning; traces require instrumentation and sampling decisions. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Tempo; vendor tracing services. | Awareness |
| Alertmanager | Group, route, and manage Prometheus alerts | Choose with Prometheus alerting; routing mistakes can silence important incidents or flood responders. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Other alert-routing systems. | Core |

**Production gotchas**

- High-cardinality labels can overwhelm a metrics backend.
- Logs without request IDs or useful structure are hard to correlate.
- Dashboards can look healthy while the user-facing request path is failing.

**Core smoke checks**

- **Prometheus:**
```bash
promtool --version
```
- **Grafana:**
```bash
grafana server -v
```
- **OpenTelemetry:**
```bash
otelcol --version
```
- **Alertmanager:**
```bash
amtool --version
```

### Security & supply chain

Supply-chain controls establish what went into an artifact, who built or approved it, and whether policy permits its use. Scanners are signals for triage, not proof of absence of risk.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| SBOM | Inventory components included in an artifact | Choose as an inventory artifact; ensure the format and completeness fit downstream consumers. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Other SBOM formats/generators. | Core |
| cosign signing/verification | Bind artifact identity to a verifiable signature or attestation | Choose when verification policy is defined; keyless/key-based trust setup must be reviewed. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Other artifact-signing approaches. | Awareness |
| Trivy | Scan image and dependency inputs for known vulnerabilities | Choose for local triage; keep databases current and prioritize exploitability/context rather than raw counts. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Grype; vendor scanners. | Core |
| Kyverno / OPA Gatekeeper | Validate or mutate Kubernetes resources against policy | Choose for enforceable guardrails; start in audit/reporting mode where possible. [VERIFY] current APIs and maintenance. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Admission policies and CI policy checks. | Awareness |
| Falco | Detect selected runtime behaviors using rules and runtime signals | Choose when runtime detection is a stated objective; kernel/runtime support and alert tuning matter. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Cloud runtime detection; other runtime sensors. | Awareness |
| kube-bench | Check selected Kubernetes configuration against CIS benchmark guidance | Choose for structured audit practice; confirm benchmark version and applicability. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Distribution security checks; manual benchmark review. | Awareness |

**Production gotchas**

- An SBOM is inventory, not a guarantee of safety or provenance.
- Signing is only useful when the deployment path verifies identity and trust policy.
- Scanner findings need triage, ownership, and an explicit remediation policy.

**Core smoke checks**

- **SBOM:**
```bash
syft version
```
- **Trivy:**
```bash
trivy --version
```

### Backup, DR & resilience testing

Recovery is proven by restoring into a clean target and validating service/data, not by the existence of a backup job. Resilience tests should have a bounded blast radius and a rollback plan.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| Application-native backup | Export data using the application's supported consistency mechanism | Choose when transaction consistency matters; test the restore path and required dependencies. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Volume snapshots; database-specific backup tools. | Core |
| Checksums / verification queries | Prove restored files or records match expected data | Choose a deterministic verification method; matching a file checksum does not prove the whole service works. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Application-specific integrity checks. | Core |
| Velero | Back up and restore supported Kubernetes resources and persistent data integrations | Driver/plugin support and restore consistency must be tested. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Application-native backup; storage-native snapshots. | Awareness |
| Chaos Mesh / LitmusChaos | Inject controlled failures for resilience experiments | Choose when the experiment has clear hypotheses and guardrails; avoid uncontrolled experiments. [VERIFY] current compatibility. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Manual fault injection; application-level tests. | Awareness |

**Production gotchas**

- A successful backup job does not prove a restore works.
- A checksum proves selected content equality, not full application correctness.
- Chaos tests without a bounded blast radius can damage the lab or external services.

**Core smoke checks**

- **Application-native backup:**
```bash
sha256sum <backup-file>
```
- **Checksums / verification queries:**
```bash
sha256sum <backup-file>
```

### Multi-cluster & multi-region

Fleet operations coordinate policies and releases across clusters. Real multi-region resilience depends on networking, identity, data replication, global traffic, and provider failure domains; two local clusters only simulate part of that system.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| Two kind clusters | Simulate separate cluster failure domains | Choose for low-cost failover reasoning; do not claim real regional independence. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Two minikube clusters; separate namespaces for limited exercises. | Core |
| kubectl contexts | Select and inspect multiple cluster endpoints | Choose for small-scale learning; context mistakes can direct commands to the wrong cluster. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Fleet-management tools. | Core |
| Cluster API | Manage Kubernetes cluster lifecycle through declarative APIs | Choose when cluster lifecycle automation is in scope; provider and infrastructure integration increase complexity. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Provider-managed cluster lifecycle tools. | Awareness |
| Global traffic management | Direct users across endpoints or regions based on policy/health | Real failover needs external routing and failure-domain independence. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: DNS failover; cloud global load balancing. | Awareness |
| Fleet management (for example, a multi-cluster GitOps pattern) | Apply consistent desired state across multiple clusters | Choose when fleet policy and drift control are required; verify the chosen project's current supported pattern. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Argo CD multi-cluster patterns; Flux patterns. | Awareness |

**Production gotchas**

- Two local clusters do not share real regional failure domains.
- Data replication lag can undermine failover correctness.
- A failover procedure is incomplete until clients, credentials, data, and DNS/routing are considered.

**Core smoke checks**

- **Two kind clusters:**
```bash
kind get clusters
```
- **kubectl contexts:**
```bash
kubectl config get-contexts
```

### FinOps & capacity

Capacity planning relates workload demand to resource limits, performance, and cost. FinOps turns usage into accountable decisions; a local simulation can teach method but cannot establish actual provider pricing.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| kubectl top / Metrics Server | Observe current pod/node resource usage | Choose for basic snapshots; short windows and missing historical context limit conclusions. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Prometheus-based usage dashboards. | Core |
| HPA | Scale replicas based on configured metrics | Scaling only helps when metrics reflect demand and downstream capacity exists. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: KEDA; custom controllers. | Core |
| Capacity and unit-economics worksheet | Model resource demand and cost per request/job from explicit assumptions | Choose first for a solo learner; label prices as hypothetical unless verified from provider pricing sources. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: FinOps platforms. | Core |
| OpenCost | Attribute Kubernetes resource costs using supported data sources | Choose when cluster cost allocation is required; verify compatibility and current project status. [VERIFY] | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Kubecost-class tools; cloud billing exports. | Awareness |
| Cluster autoscaler | Adjust cluster node capacity based on scheduling demand | Simulate pending pods and capacity decisions locally; actual node provisioning requires a compatible infrastructure provider. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Managed node autoscaling; Karpenter-class provisioning. | Awareness |

**Production gotchas**

- A snapshot of usage is not enough to model peaks or seasonality.
- Autoscaling can increase cost without resolving downstream bottlenecks.
- Hypothetical unit costs must not be presented as actual provider bills.

**Core smoke checks**

- **kubectl top / Metrics Server:**
```bash
kubectl top pods --all-namespaces
```
- **HPA:**
```bash
kubectl get hpa --all-namespaces
```
- **Capacity and unit-economics worksheet:**
```bash
python -c "print('Record demand, resource use, unit, assumed unit price, and uncertainty')"
```

### Platform engineering & IDPs

An internal developer platform packages paved paths, templates, policy, and operational defaults so teams can deliver safely. A portal is only one possible interface; the platform contract and ownership model matter more.

| Tool | Strengths | Trade-offs | Choose this when / avoid this when | Scope |
|---|---|---|---|---|
| Golden-path template repository | Provide a reusable service skeleton with documented defaults | Choose the simplest scaffold that users can maintain; avoid generating a framework larger than the service. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Cookiecutter; Copier; internal templates. | Core |
| Backstage | Provide a developer portal and software catalog extensibility | Introduces platform ownership and ongoing upgrade work. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: A lightweight docs/catalog site; other IDP portals. | Awareness |
| Crossplane | Manage external infrastructure through Kubernetes-style APIs | Introduces platform ownership and ongoing upgrade work. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Terraform/OpenTofu; cloud-native IaC. | Awareness |
| Cookiecutter / Copier | Generate projects from templates | Choose when consistent project initialization saves real effort; test template upgrades and generated defaults. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: Repository templates; custom scaffolding. | Awareness |
| Policy and validation checks | Prevent unsafe defaults in the golden path | Choose the least complex enforceable control; make failures actionable and documented. | Choose when the stated problem and integration fit; avoid when a simpler existing capability meets the acceptance criteria. Alternatives: CI checks; admission policy. | Core |

**Production gotchas**

- A portal without ownership and support contracts becomes a stale catalogue.
- Golden paths can become a bottleneck if exceptions are impossible or unsafe.
- Templates need versioning, migration guidance, and validation.

**Core smoke checks**

- **Golden-path template repository:**
```bash
git status --short
```
- **Policy and validation checks:**
```bash
python -m pytest --version
```

## 6. Module-to-tool matrix

| Module | Exact module name | Core tools used | Awareness tools | Lab environment |
|---|---|---|---|---|
| M01 | 01-Container-Image-Engineering-and-Registry-Hygiene | Docker CLI, BuildKit, local registry, Trivy, Syft | cosign, hosted registries | Local |
| M02 | 02-CI-CD-Pipeline-Engineering | GitHub Actions, pytest, Ruff, build cache | Jenkins, GitLab CI/CD, remote cache | Local / Free tier |
| M03 | 03-Production-Kubernetes-Operations | kind, kubectl, Metrics Server, HPA | minikube, admission policy engines | Local |
| M04 | 04-Kubernetes-Networking-Ingress-and-Service-Mesh | CNI plugin, Service/DNS, Ingress controller | Gateway API, cert-manager, service mesh | Local |
| M05 | 05-Kubernetes-Storage-and-Stateful-Data-Workloads | PVC/PV, StatefulSet | CSI, snapshots, database operators | Local |
| M06 | 06-Helm-Kustomize-and-Kubernetes-Packaging | Helm, Kustomize | OCI chart distribution | Local |
| M07 | 07-Advanced-Infrastructure-as-Code-and-Cloud-Operations | Terraform/OpenTofu workflow, LocalStack | Checkov, Ansible, real cloud providers | Local / LocalStack |
| M08 | 08-GitOps-and-Progressive-Delivery | Argo CD | Flux, Argo Rollouts, Flagger | Local |
| M09 | 09-Secrets-and-Identity-Management | Kubernetes Secrets, RBAC | External Secrets Operator, Vault/OpenBao, OIDC, workload identity | Local |
| M10 | 10-Site-Reliability-Engineering-and-Incident-Management | SLI/SLO worksheet, Prometheus alert rules, postmortem template | On-call platforms, dedicated SLO platforms | Local |
| M11 | 11-Production-Observability-Stack-and-Performance-Operations | Prometheus, Grafana, OpenTelemetry, Alertmanager | Loki, Jaeger | Local |
| M12 | 12-Production-Security-and-Software-Supply-Chain | SBOM, Trivy | cosign, policy engines, Falco, kube-bench | Local |
| M13 | 13-Backup-Disaster-Recovery-and-Resilience-Testing | Application-native backup, checksums/verification queries | Velero, Chaos Mesh, LitmusChaos | Local |
| M14 | 14-Multi-Cluster-and-Multi-Region-Operations | Two kind clusters, kubectl contexts | Cluster API, global traffic management, fleet management | Local simulation |
| M15 | 15-Platform-Capacity-Compute-Economics-and-FinOps | Metrics Server, HPA, unit-economics worksheet | OpenCost, cluster autoscaler | Local |
| M16 | 16-Platform-Engineering-and-Internal-Developer-Platforms | Golden-path template repository, policy/validation checks | Backstage, Crossplane, Cookiecutter/Copier | Local |
| M17 | 17-Production-DevOps-Integrated-Capstone | GitHub Actions, kind, kubectl, Helm/Kustomize, Argo CD, Prometheus/Grafana, backup/verification tools | cosign, Argo Rollouts, policy engines, LocalStack | Local / LocalStack |

Every module has at least one Core workflow. Core tools listed in the master table are mapped to at least one module. Some Core entries are concepts with a concrete local test (for example artifact digest verification, SLI/SLO calculation, or backup validation), rather than a standalone server to install.

## 7. The minimum viable lab stack

The minimum stack is intentionally modest. Do not install every Awareness tool. Start with the following components, add only what the active module needs, and tear them down when finished.

### Install first

1. **Linux/WSL2 shell, Git, Python tooling, and a code editor.** These are the foundation for scripts, test evidence, and reproducible notes.
2. **Docker or a compatible local container engine, BuildKit support, Trivy, and Syft.** This covers image build, inspection, scanning, and SBOM work.
3. **kind and kubectl.** Use one disposable cluster for core workload, rollout, and networking exercises.
4. **Helm and Kustomize.** Use them only after a basic manifest deploy is understood.
5. **GitHub Actions or a local runner, plus pytest and Ruff.** Keep CI gates simple and demonstrate both passing and failing cases.
6. **Terraform/OpenTofu and LocalStack only when a module needs them.** Prefer a local provider/workflow first; do not create cloud infrastructure merely to prove that an IaC command runs.
7. **Prometheus, Grafana, OpenTelemetry Collector, and Alertmanager.** Start with a small service and one signal path; add logs/traces only when the lab requires them.
8. **Argo CD for the GitOps module.** Install it into the disposable cluster and remove it when finished if resource pressure is an issue.

### Defer until needed

- Service mesh, multi-cluster fleet managers, Backstage, Crossplane, database operators, runtime security, chaos platforms, and hosted paging services.
- Multiple Kubernetes distributions at once; one primary local cluster is enough until M14.
- Large log/search stacks or long-retention telemetry on a modest laptop.
- Real cloud managed Kubernetes, paid global traffic management, and multi-region infrastructure; use the explicit simulation instead.

Resource use depends on the selected components and workload. Check each project's documented requirements; observability stacks and multiple clusters can be the heaviest local workloads. Keep only one cluster and a small set of services running at a time if the machine becomes constrained.

Installation steps belong in [lab-environment-setup.md](lab-environment-setup.md); this section is an order of operations, not a replacement for that guide.

## 8. Local vs LocalStack vs free tier vs simulation

| Category | Local | LocalStack | Free tier | Simulation / limits |
|---|---|---|---|---|
| Containers and image security | Yes: build, scan, SBOM, digest workflows. | Not normally needed. | Hosted registries/CI may have free allowances. | Local registry auth and trust differ from production. |
| CI/CD | Local tests/runners; hosted repository workflow may be available. | Not normally needed. | Hosted CI limits and terms change. | Never expose secrets to untrusted jobs. |
| Kubernetes operations | kind/minikube. | Does not replace Kubernetes. | Optional real cloud resources. | Local clusters do not model managed control-plane failure modes. |
| Networking and mesh | Basic service, DNS, and compatible CNI features. | Does not provide cluster networking parity. | Real load balancers/certificates may incur charges. | Simulate global traffic and provider-specific routing. |
| Storage and stateful workloads | Local provisioner and local volumes. | Can emulate selected cloud APIs, not all storage semantics. | Cloud storage is possible but cost/cleanup must be checked. | Verify application-level restore; local disks are not cloud durability proof. |
| Packaging | Fully local. | Not needed. | Not needed for basic learning. | Render and inspect manifests before applying. |
| IaC and cloud operations | Local providers/resources. | Selected AWS API emulation. | Real provider integration only with cost controls. | IAM, networking, quotas, and service behavior are not fully equivalent. **[VERIFY]** current service coverage. |
| GitOps and rollout | Local cluster and Git repository. | Not needed for core flow. | Hosted Git/CI may have free allowances. | Simulate production traffic splitting if local routing integrations are unavailable. |
| Secrets and identity | Kubernetes Secrets/RBAC and local OIDC/secret-manager labs where feasible. | Some cloud APIs may be emulated. | Real workload identity requires a compatible cloud account. | Do not claim cloud identity parity from a local mock. |
| SRE and incident response | Synthetic traffic, alert rules, local postmortem. | Not needed. | Hosted paging tools are optional and terms vary. | Simulate on-call escalation; it is not a real staffed rotation. |
| Observability | Prometheus/Grafana/OpenTelemetry and selected local log/trace tools. | Not needed. | Managed observability may have free limits. | Retention, scale, and managed-service failure modes differ. |
| Supply-chain security | Local scanners, SBOM, signing/verification practice. | Not needed. | Hosted artifact services may have free limits. | Real production trust roots and policy need explicit setup. |
| Backup and DR | Local backup/restore to a clean target. | May emulate an object-store API if supported. | Real cloud backups need cost and retention controls. | Local restore cannot prove cross-region recovery. |
| Multi-cluster and multi-region | Two local clusters. | Does not create independent regions. | Real multi-region is usually not a zero-cost assumption. | Treat as a failover simulation only. |
| FinOps and capacity | Local usage metrics and hypothetical unit costs. | Limited relevance. | Provider billing data only if real resources are used. | Never present hypothetical prices as actual spend. |
| Platform engineering | Templates, validation, and local catalogue. | Not needed. | Hosted portals are optional. | A local golden path demonstrates workflow, not enterprise adoption. |

Use [local-lab-kind-minikube-and-localstack.md](local-lab-kind-minikube-and-localstack.md) for the local lab design and [free-tier-cloud-account-and-cost-safety.md](free-tier-cloud-account-and-cost-safety.md) before any real cloud experiment.

## 9. Tool-selection scenarios

| Scenario | Starting stack | Why | What would change the decision |
|---|---|---|---|
| **A 5-person startup** | Hosted Git CI, container build, Kubernetes only if operational needs justify it, basic metrics and error tracking. | Low operational overhead and fast feedback matter more than a large platform. | Move to a managed platform when uptime, team capacity, and service complexity justify the cost. |
| **Regulated fintech** | Controlled CI runners, artifact scanning/SBOM, signed artifact verification, strict IAM/RBAC, audit logs, tested backup/restore, and policy gates. | Evidence, least privilege, traceability, and recovery are core requirements. | Select tools after compliance counsel, threat model, provider controls, and current licence/support review. |
| **Multi-tenant platform team** | Kubernetes, explicit tenancy boundaries, admission policy, identity integration, GitOps, quota/capacity controls, and a documented golden path. | Tenant isolation and consistent operations need enforceable boundaries. | Use stronger isolation or separate clusters when threat model and blast radius require it. |
| **Solo learner on a modest laptop** | kind, kubectl, Helm/Kustomize, a small CI flow, Trivy/Syft, and a minimal observability stack used one module at a time. | Local repeatability and low resource use matter most. | Defer multi-cluster tools, service mesh, and large telemetry stacks until the module needs them. |
| **Data/ML platform team** | Container build and scan, CI, Kubernetes or an appropriate managed runtime, object/data storage integration, metrics/logs/traces, and rollbackable model/service release. | Model services inherit software delivery and reliability needs plus model/data-specific monitoring. | Add GPU scheduling, model registry, feature platform, or workflow orchestration only after requirements are known. |
| **Team already standardized on Terraform** | Keep Terraform if its current licence/governance and organization policy fit; add plan review, state protections, and policy checks. | Avoid a migration whose benefits do not exceed compatibility and training costs. | Evaluate OpenTofu when governance, policy, or ecosystem changes justify a measured compatibility test. **[VERIFY]** |
| **Team needing progressive delivery** | Start with safe rolling updates and reliable metrics; evaluate Argo Rollouts or Flagger when canary/blue-green acceptance criteria require them. | Traffic control and automated analysis add complexity and require trustworthy signals. | Choose based on supported ingress/mesh integration, maintenance status, and operational ownership. **[VERIFY]** |
| **Cloud migration with strict cost limits** | LocalStack for supported integration tests, local IaC plan workflows, then a narrowly scoped real-cloud proof with budget and teardown checks. | Emulation lowers iteration cost but cannot validate every provider behavior. | Use real resources only for questions that cannot be answered locally; review billing and resource inventory immediately. |

## 10. Common tooling mistakes

- **Tool sprawl:** choose one Core tool per category and add another only to answer a documented requirement.
- **Adopting a mesh too early:** first prove that native Services, DNS, TLS, and NetworkPolicy cannot meet the requirement.
- **Running stateful workloads without tested restores:** require a clean-target restore and data verification before claiming readiness.
- **Treating Helm values as a stable API by accident:** document values, validate them, and use compatibility/versioning discipline.
- **GitOps without a drift policy:** define which changes Git may reconcile, how emergency changes are handled, and how drift is reviewed.
- **No cost visibility:** estimate demand, set available billing controls, and check teardown after every cloud lab.
- **Hand-rolling everything:** use established components for standard problems unless the learning objective explicitly requires a small implementation.
- **Resume-driven development:** select tools to satisfy a system requirement, not to maximize the number of products listed.
- **Treating scans as a pass/fail oracle:** triage findings by impact, exploitability, reachability, and remediation options.
- **Calling a local demo production proof:** document what the simulation does and does not validate.
- **Keeping all telemetry forever:** define retention and sampling based on investigation needs and resource limits.
- **Skipping upgrades and rollback tests:** rehearse a controlled upgrade, observe failure signals, and prove recovery before increasing blast radius.

## 11. Staying current

Treat this file as a point-in-time map. Before starting a new module, check the chosen tool's official documentation and release/support notes. Before adopting a tool for a real system, perform a separate technical and security review.

- **At each module start:** verify install instructions, supported Kubernetes compatibility, required APIs, and whether the tool still supports the planned local workflow.
- **Before a real adoption or migration:** verify licence, governance/ownership, maintenance activity, support model, release cadence, security advisories, data export, and upgrade/rollback procedure.
- **At least periodically during a long learning project:** review dependency and image advisories, remove unused tools, and retest the minimum viable stack.
- **After any major incident or tool change:** update the runbook, compatibility notes, and evidence commands.
- **Source hierarchy:** official project documentation and security advisories first; release notes and project governance records next; vendor-neutral landscapes and secondary articles as discovery aids, not final authority.

## 12. Reference Sources

Names only; consult the current official documentation for the selected versions and distributions.

### Containers, registries, and supply chain

- Open Container Initiative (OCI) Specifications.
- Docker Documentation and BuildKit Documentation.
- Podman Documentation.
- Trivy Documentation.
- Syft Documentation.
- Sigstore/cosign Documentation.
- SLSA Specification.

### CI/CD and source control

- Git Documentation.
- GitHub Actions Documentation.
- GitLab CI/CD Documentation.
- Jenkins Documentation.
- pytest Documentation.
- Ruff Documentation.

### Kubernetes, networking, storage, and packaging

- Kubernetes Documentation: Concepts, Tasks, Security, Networking, Storage, Probes, Resource Management, and Cluster Administration.
- kind Documentation and minikube Documentation.
- Metrics Server Documentation.
- Gateway API Documentation.
- CNI project documentation for the selected plugin.
- CoreDNS Documentation.
- Helm Documentation and Kustomize Documentation.
- cert-manager Documentation.

### IaC, GitOps, and policy

- Terraform Documentation and current HashiCorp licensing/governance notices.
- OpenTofu Documentation.
- LocalStack Documentation and current service-coverage/edition information.
- Checkov Documentation and Ansible Documentation.
- Argo CD Documentation, Flux Documentation, Argo Rollouts Documentation, and Flagger Documentation.
- Kyverno Documentation and Open Policy Agent / Gatekeeper Documentation.
- Cluster API Documentation.

### Secrets, identity, and security

- Kubernetes Documentation: Secrets, RBAC, Service Accounts, and Security.
- External Secrets Operator Documentation.
- HashiCorp Vault Documentation and current licensing/governance notices.
- OpenBao Documentation.
- OpenID Connect Core specification and the selected identity provider's documentation.
- Falco Documentation and kube-bench documentation.

### Reliability, observability, and recovery

- Google SRE Book and Site Reliability Engineering Workbook.
- Prometheus Documentation, Alertmanager Documentation, and Prometheus Operator documentation where applicable.
- Grafana Documentation, Loki Documentation, and Jaeger Documentation.
- OpenTelemetry Documentation.
- Velero Documentation.
- Chaos Mesh Documentation and LitmusChaos Documentation.

### FinOps and platform engineering

- OpenCost Documentation.
- Backstage Documentation.
- Crossplane Documentation.
- Cookiecutter Documentation and Copier Documentation.
- CNCF Landscape as a discovery aid; verify current project status directly with the project.

---

**Maintenance rule:** do not remove a `[VERIFY]` tag merely because a secondary article looks current. Remove it only after checking the named authoritative source and recording the review in the repository.
