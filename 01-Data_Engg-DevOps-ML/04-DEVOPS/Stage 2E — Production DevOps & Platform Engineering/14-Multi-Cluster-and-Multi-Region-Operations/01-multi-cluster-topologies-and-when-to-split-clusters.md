# Unit 1 — Multi-cluster topologies and when to split clusters

> **Module:** M14 — Multi-Cluster and Multi-Region Operations  
> **Stage:** Stage 2E — Production DevOps & Platform Engineering  
> **Target filename:** `01-multi-cluster-topologies-and-when-to-split-clusters.md`  
> **Prerequisites:** M03 Kubernetes operations; M04 networking/CNI/Services/Gateway; M05 stateful workloads; M07 IaC; M08 GitOps; M09 secrets and identity; M10 SRE; M11 observability; M12 supply-chain security/admission; M13 backup, DR, and resilience.  
> **Estimated time:** 12–18 hours: 5–7 hours concepts and design exercises; 7–11 hours staged labs and review.  
> **Last reviewed:** 2026-10-29 (source and content review; live documentation verification was not performed in this drafting pass).  
> **Tool baseline assumed:** Linux/WSL2 Ubuntu, Bash, Docker, `kind`, `kubectl`, Python 3, and `pytest`; exact installed versions are environment-specific. Verify current `kind` config fields and all version-sensitive interfaces marked `[VERIFY]` before running.  
> **Required profile:** `Fleet-Core`.  
> **Footprint:** two small `kind` clusters and local scripts; exact CPU/RAM/disk use varies—**measure yours**. Do not run all optional components simultaneously on an 8 GB laptop.  
> **Clusters touched:** `stage2e-east-lab`, `stage2e-west-lab`.  
> **Destructive labs:** Lab 06 only, optional, explicitly gated, and restricted to a freshly created disposable lab cluster. All other labs are non-destructive or use explicit cleanup of lab-only resources.

## Learning contract and operating rules

This unit teaches how to decide **whether** to split a Kubernetes platform into multiple clusters and how to operate that decision safely. The default is one cluster until a specific isolation, lifecycle, latency, residency, scale, ownership, or availability requirement justifies more. A cluster boundary can reduce some failure modes, but it does not automatically isolate shared networks, credentials, registries, DNS, Git servers, data stores, management systems, or the laptop hosting the lab.

The two lab clusters use east/west names only as labels. They share one laptop, host kernel, Docker daemon, power source, and often network and storage. They are **not two regions**. These labs demonstrate context safety, inventory, topology reasoning, and workflow mechanics; they cannot prove regional independence, WAN behavior, provider-level failover, or true global routing.

**Safety invariant:** every mutating Kubernetes command in this unit targets an explicitly named disposable lab context or goes through the `kctl` guard described below. Never copy a destructive command from this unit into a production or unspecified context. A context name is a client-side selection, not an authorization boundary. RBAC, scoped identities, admission policy, short-lived credentials, and reviewed change procedures remain necessary.

---

## 1. Why this matters in production

A multi-cluster platform creates more than one place where commands, configuration, policies, workloads, and telemetry can land. A mistaken context selection can turn an ordinary maintenance action into a production incident; a bad controller or admission webhook can affect every workload sharing one cluster; a missing inventory can leave unsupported clusters unnoticed; and a “regional” architecture can still share a registry, identity provider, or management hub that defeats the intended isolation. This unit gives you a repeatable way to choose boundaries, prove which cluster you are operating, and identify the dependencies that remain shared.

## 2. Learning objectives

By the end of this unit, you will be able to:

- **[L1]** Explain why one cluster is the default and identify requirements that justify a separate cluster.
- **[L1]** Distinguish cluster, region, zone, cell, environment, tenant, control plane, data plane, fleet, and failure domain.
- **[L1]** Compare common topologies and state what each isolates and what it leaves shared.
- **[L1]** Inspect Kubernetes contexts and execute read operations with explicit `--context`.
- **[L2]** Create two small kind clusters from reviewable configuration and discover their actual context names.
- **[L2]** Inspect and compare pod/service CIDRs, explain overlap risks, and maintain a documented fleet allocation plan.
- **[L2]** Maintain a cluster registry and validate required metadata, CIDR overlap, ownership, tier, and lifecycle state.
- **[L2]** Use a context guard and explain its limitations compared with RBAC and admission controls.
- **[L2]** Score six platform scenarios and defend a topology recommendation with an ADR.
- **[L3]** Map blast radius, shared dependencies, capacity, data gravity, and management-plane failure modes.
- **[L3]** Compare cell-based, hub-and-spoke, tiered, regional, and workload-class designs using explicit trade-offs.
- **[L4]** Define fleet standards, lifecycle governance, split/merge controls, and measurable triggers for revisiting topology decisions.

## 3. Concept map and vocabulary

### 3.1 First principles: what is coordinated?

A Kubernetes cluster has an API endpoint and control plane that coordinate its own desired state. Nodes run workloads scheduled by that cluster. Kubernetes Service discovery is native **within** a cluster; it does not automatically create a fleet-wide Service namespace. Separate clusters have separate API state, scheduling decisions, RBAC configuration, and usually separate cluster-scoped resources. Cross-cluster coordination requires additional mechanisms: GitOps, infrastructure lifecycle tooling, explicit network connectivity, service discovery, traffic routing, identity trust, data replication, and observability aggregation.

```text
                 MANAGEMENT / GOVERNANCE PLANE
          Git + review -> fleet inventory / policy / promotion
                    |                         |
              scoped config              scoped config
                    v                         v
       +------------------------+  +------------------------+
       | Cluster: east lab      |  | Cluster: west lab      |
       | Control plane / API    |  | Control plane / API    |
       | Workloads + Services   |  | Workloads + Services   |
       | Local identity/policy  |  | Local identity/policy  |
       +-----------+------------+  +------------+-----------+
                   |                            |
              local data                  local data
                   |                            |
                   +---- explicit cross-cluster paths ----+
                        traffic / identity / data / telemetry

   Shared lab failure domain: one laptop, OS/kernel, Docker daemon,
   power, and potentially shared registry, Git, DNS, and storage.
   Network latency/partition, regional independence, and cloud routing
   are NOT represented by two kind clusters on one host.
```

### 3.2 Vocabulary

| Term | Precise definition | Common misconception |
|---|---|---|
| Cluster | A Kubernetes control-plane and workload environment with its own API state and cluster-scoped resources. | A cluster is not the same thing as a region or a namespace. |
| Fleet | A set of clusters governed, inventoried, and operated under shared standards. | A fleet is not automatically one Kubernetes API or one failure domain. |
| Management/hub cluster | A cluster hosting management functions such as fleet controllers, GitOps, or central policy. | The hub is not necessarily required for already-running workloads to keep running. Behavior depends on architecture. |
| Workload/spoke cluster | A cluster primarily hosting applications or platform workloads. | A spoke is not automatically isolated from shared dependencies. |
| Region | A geographic provider or organizational location containing one or more failure domains. | Two cluster names containing “east” and “west” do not create regions. |
| Availability zone (AZ) | A provider-defined location/failure domain within a region. Exact independence is provider-specific. | Different zones are not guaranteed to have no shared dependencies. |
| Cell | A relatively self-contained service stack serving a partition of users, tenants, or traffic. A cell may contain one or more clusters. | A cell is not synonymous with a cluster or region. |
| Tenant | A customer, team, or workload owner sharing a platform under defined isolation controls. | A namespace alone does not provide every form of tenant isolation. |
| Environment | A lifecycle stage such as development, staging, or production. | An environment label is not a security boundary by itself. |
| Failure domain | A component or boundary whose failure can affect a set of services. | A deployment boundary does not prove failure-domain independence. |
| Blast radius | The maximum plausible scope of impact from one failure or change. | A cluster boundary reduces some blast radii but does not eliminate shared fate. |
| Control plane | Components that expose the API and reconcile/schedule desired state. | Control-plane health does not guarantee application health. |
| Data plane | Components that carry application traffic or execute workload behavior. | A healthy data plane may continue while management operations are unavailable. |
| Cluster boundary | A separation between Kubernetes control-plane/API domains. | It is not automatically a network, identity, data, or host boundary. |
| Shared dependency | A service or resource used by multiple clusters/cells, such as DNS, registry, Git, identity, or storage. | A shared dependency can invalidate an assumed isolation boundary. |
| Cluster sprawl | Uncontrolled growth of clusters without clear owner, purpose, lifecycle, or policy. | More clusters do not automatically mean better resilience. |
| CIDR plan | A documented allocation of non-overlapping network ranges for pods, Services, nodes, hosts, VPNs, and future connections. | Unique CIDRs alone do not provide routing or service discovery. |
| Context | A kubeconfig selection of cluster, user credentials, and optional default namespace. | A context is not an RBAC policy or proof that a command reached the intended cluster. |
| Canary cluster | A designated cluster that receives a platform/configuration change before broader rollout. | A canary is useful only if representative and promotion is gated by evidence. |

### 3.3 Why one cluster is the default

One cluster usually offers one API surface, one primary upgrade path, one baseline policy configuration, native Service discovery, and a simpler observability and incident-response view. It reduces duplicated controllers, agents, policy engines, platform add-ons, access paths, and operational toil. Those are real advantages, not a universal rule: if a single control plane creates unacceptable shared risk, combines incompatible trust zones, violates residency requirements, or cannot meet latency/scale needs, the operational simplicity may be outweighed by the cost of sharing.

### 3.4 What a cluster boundary buys—and what it does not

- **Blast radius:** a broken controller, API-server issue, admission webhook, CRD rollout, or cluster upgrade may be limited to one cluster. A shared GitOps hub or common credential can still spread a bad change fleet-wide.
- **Security and tenancy:** separate API servers, RBAC configurations, and cluster-admin domains can be a stronger administrative boundary than namespaces. Shared identity, network, storage, or privileged fleet credentials can still create lateral paths.
- **Lifecycle:** clusters can have independent upgrades, maintenance windows, certificate rotation, and rollback. This adds more upgrade work and drift opportunities.
- **Geography, latency, and residency:** workloads can be placed closer to users/data or in a required jurisdiction. This is an architecture concern, not legal advice; confirm obligations with the appropriate legal/compliance owner.
- **Scale:** API-server, controller, CRD, watch/list, namespace, and workload pressure can be partitioned. Consult the current Kubernetes scalability guidance before setting thresholds; do not rely on remembered numbers. [VERIFY: review the current official Kubernetes “Scalability” documentation for the version and workload shape in question.]
- **Ownership:** separate teams or service tiers can own lifecycle and access independently. Too many ownership boundaries can create handoff overhead and inconsistent standards.
- **Cost:** each cluster can add control-plane/system components, agents, policy engines, monitoring, networking, and operational overhead. Managed-control-plane pricing and cross-region transfer are outside this free lab; do not infer cloud costs from laptop resource use.

### 3.5 Common topologies

| Topology | Isolation gained | What remains shared | Benefits | Costs | Common failure mode | Choose / avoid criteria |
|---|---|---|---|---|---|---|
| One cluster for many environments | Minimal; logical namespaces/policies only | Control plane, upgrades, cluster-scoped resources, admin plane | Lowest operational overhead; native discovery | Weak separation for production changes and cluster-scoped faults | Dev experiment or bad CRD affects production workloads | Suitable for low-risk sandboxes; generally avoid when production trust/lifecycle separation is required. |
| Cluster per environment | Environment-level control-plane and lifecycle separation | Git, identity provider, registries, CI, operators if shared | Clear promotion and access boundaries | Duplicated platform services and drift management | Same bad config promoted to all environments without gates | Good default when production needs stronger separation; avoid if team cannot operate the fleet safely. |
| Cluster per team/tenant | Administrative and control-plane isolation | Shared network, identity, DNS, storage, hub may remain | Tenant autonomy; bounded noisy-neighbor/control-plane risk | High fixed overhead and inconsistent configuration risk | Sprawl or leaked fleet-wide credentials defeat isolation | Use for meaningful trust/ownership boundaries; avoid one cluster per small service/team without a requirement. |
| Cluster per region | Regional placement and independent cluster lifecycle | Global identity, DNS, registry, management, replicated data | Locality; regional failure can be contained if dependencies support it | Replication, traffic management, regional capacity and operations | “Regional” clusters still depend on one region’s registry or hub | Use when geography, latency, residency, or availability demands it; avoid claiming independence without dependency analysis. |
| Cluster per workload class | Separates batch, online inference, GPU/training, or sensitive workloads | Shared platform/control services and possibly data | Tailored node pools, quotas, upgrades, scaling and risk | Duplicated platform overhead; cross-class integration | Training workload exhausts shared services or credentials | Use for materially different resource/security/lifecycle needs; avoid splitting only for naming neatness. |
| Hub-and-spoke management | Central policy/inventory with workload clusters separated | Hub credentials, Git, identity, network, central services | Fleet consistency and automation | Hub is high-value target and may become bottleneck | Hub compromise propagates malicious desired state | Use with scoped credentials, pull patterns, HA/recovery and break-glass; avoid a single all-powerful hub. |
| Cell-based | Limits impact by tenant/user partition and independent stack/data | Global routing, identity, registry, shared control dependencies may remain | Bounded blast radius and horizontal operational scaling | Data partitioning, routing, uneven capacity, duplicated services | “Independent” cells share a critical registry/database | Use when user/tenant partitioning and isolation justify it; avoid if shared state dominates request paths. |

**Cluster vs. zone vs. region vs. cell:** a cluster is a Kubernetes management/workload boundary; a zone is a provider-defined location; a region groups geographic infrastructure; a cell is a service-level partition designed to contain impact. A cell may map to one cluster, multiple clusters, or other infrastructure. State the mapping in the architecture rather than assuming it.

### 3.6 Anti-patterns

- **Stretched cluster across distant regions:** spanning one Kubernetes control plane/etcd quorum across high-latency or partition-prone links couples failure domains. Exact latency guidance is implementation/version-sensitive. [VERIFY: consult current Kubernetes and etcd operational guidance before designing control-plane placement.] Usually prefer independent regional clusters with explicit fleet-level coordination over stretching a single control plane for regional resilience.
- **Pets-per-snowflake clusters:** undocumented manual differences make upgrades and rebuilds fragile. Store configuration declaratively, record ownership, and test reconstruction.
- **One cluster per microservice:** often multiplies fixed overhead and operational surface without a proportionate isolation benefit. Split by meaningful risk, lifecycle, tenancy, or scale boundaries.
- **“Federation solves everything”:** no federation tool removes the need to decide data consistency, traffic ownership, identity, failure behavior, and who operates it. Tool maturity and APIs change; assess current project documentation before adoption. [VERIFY]
- **One shared management dependency:** a single registry, Git server, identity provider, DNS service, or hub may become the real fleet-wide failure domain.

## 4. Level 1 — Beginner: foundations and safe two-cluster basics

### 4.1 kubeconfig and context model

A kubeconfig typically contains **clusters** (API endpoint and certificate data), **users** (authentication information), and **contexts** (a named combination of cluster, user, and optional default namespace). The current context is the default selection for commands that do not specify another. `--context` overrides that default for a command and makes intent visible in scripts and runbooks.

```bash
# Read-only inspection. Run in WSL2 Ubuntu or native Linux.
kubectl config get-contexts
kubectl config current-context
kubectl config view --minify
```

Discover context names; do not assume a context string from a cluster name. `kind` context names commonly include a `kind-` prefix, but inspect the actual output before using one. `kubectl config use-context` changes the current selection in the kubeconfig used by that process environment; it is easy to change one terminal and forget another terminal, shell script, CI job, or `KUBECONFIG` merge.

`KUBECONFIG` may name multiple files separated by the platform-specific path separator. Merging can create surprising precedence and duplicate names. Inspect the effective view, keep environment/tier access separated, and do not place production cluster-admin credentials in the same casual laptop workflow as lab credentials. A shell prompt that displays context and namespace is useful awareness, not an authorization control. `kubectx`, `kubens`, and `kube-ps1` are optional awareness tools; verify current installation instructions and maintenance status before standardizing on them. [VERIFY]

**Context safety checklist:**

1. Name the target context explicitly in scripts and commands.
2. Read the context and cluster identity before mutation.
3. Keep lab, staging, and production credentials separated where possible.
4. Use read-only access for inventory and inspection.
5. Require review and typed confirmation for high-impact operations.
6. Verify the result against the same explicit context.
7. Treat a wrapper as defense in depth; enforce real permissions with RBAC/admission and scoped credentials.

### 4.2 Lab layout and setup preflight

The two exact cluster names are `stage2e-east-lab` and `stage2e-west-lab`. The first lab profile is **Fleet-Core**: two small kind clusters, contexts, guard scripts, registry, and inventory. Do not install GitOps, observability, replicated databases, DNS simulation, and cross-cluster networking together on an 8 GB laptop. Stop components between labs and measure local resource use.

Check prerequisites:

```bash
# WSL2 Ubuntu / native Linux; read-only version checks.
docker version
kind version
kubectl version --client
python3 --version
```

If Docker or `kind` is unavailable, install using the current official documentation for your OS; do not use unverified copy-paste installer URLs. Check available resources before creating clusters:

```bash
free -h
df -h .
docker system df
```

### 4.3 Deploy the same sample app and prove which cluster served it

The application response must identify the cluster so the learner does not mistake two queries against one context for cross-cluster evidence. The following uses a small Deployment and Service; `LAB_CLUSTER` is set differently in each cluster. Apply the manifest only through explicit contexts.

Create `app-east.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-identity
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-identity
  template:
    metadata:
      labels:
        app: cluster-identity
    spec:
      containers:
        - name: web
          image: hashicorp/http-echo:1.0.0
          args: ["-text=east-lab"]
          ports:
            - name: http
              containerPort: 5678
          resources:
            requests:
              cpu: 10m
              memory: 16Mi
            limits:
              cpu: 100m
              memory: 64Mi
---
apiVersion: v1
kind: Service
metadata:
  name: cluster-identity
  namespace: default
spec:
  selector:
    app: cluster-identity
  ports:
    - name: http
      port: 80
      targetPort: http
```

Create `app-west.yaml` with the same structure, changing the container argument to `-text=west-lab`. The image/tag is illustrative and may need availability verification in an offline or restricted environment. [VERIFY]

After creating the clusters in Lab 01, deploy and verify:

```bash
# Discover contexts first; replace values only with exact names shown by get-contexts.
kubectl config get-contexts
kubectl --context kind-stage2e-east-lab apply -f app-east.yaml
kubectl --context kind-stage2e-west-lab apply -f app-west.yaml
kubectl --context kind-stage2e-east-lab rollout status deployment/cluster-identity --timeout=90s
kubectl --context kind-stage2e-west-lab rollout status deployment/cluster-identity --timeout=90s
kubectl --context kind-stage2e-east-lab get pods,svc -l app=cluster-identity -o wide
kubectl --context kind-stage2e-west-lab get pods,svc -l app=cluster-identity -o wide
```

The context strings above are the common kind naming convention, not a guarantee. If discovery shows different names, use the exact discovered context strings. For a simple local request, use `kubectl port-forward` in separate terminals with explicit contexts, then query each local forwarded port. Stop each port-forward with Ctrl-C.

Representative procedure (not captured output):

```bash
# Terminal A: keep running while testing east.
kubectl --context kind-stage2e-east-lab port-forward service/cluster-identity 18080:80
# Terminal B, after Terminal A reports the forwarding address:
curl --fail http://127.0.0.1:18080
# Expected body: east-lab

# Stop Terminal A, then repeat for west on a different local port.
kubectl --context kind-stage2e-west-lab port-forward service/cluster-identity 18081:80
curl --fail http://127.0.0.1:18081
# Expected body: west-lab
```

This proves the requests were served by workloads configured differently in the two selected cluster contexts. It does **not** prove cross-cluster networking, regional failover, or network independence.

### 4.4 Common beginner mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Trusting the current context | A command queries or changes the wrong cluster | Use explicit `--context`, print target, verify afterward. |
| Assuming context equals authorization | A context can still hold broad credentials | Apply least privilege and RBAC; isolate credentials by environment/tier. |
| Assuming east/west names mean regions | Lab results are described as regional resilience | Label them simulated; document shared host and network dependencies. |
| Reusing overlapping CIDRs | Direct routing or interconnect design later becomes ambiguous/impossible | Inspect actual ranges and allocate from a fleet plan. |
| Treating unique CIDRs as connectivity | Packets still cannot route or services cannot be discovered | Plan routing, firewalls, CNI/interconnect, service discovery, and identity separately. |
| Assuming separate clusters have no shared fate | Registry, DNS, Git, or hub outage affects both | Maintain a dependency graph and failure-domain review. |

## 5. Level 2 — Intermediate: topology decisions and working practice

### 5.1 Reusable topology scoring worksheet

Score each criterion from **0 to 3**: 0 = little/no requirement; 1 = useful; 2 = strong; 3 = hard/critical requirement. Record evidence and confidence. A high score indicates the requirement matters; it does **not** mathematically prove a specific cluster count. Treat legal/residency, trust-boundary, and hard availability requirements as constraints, not just weighted preferences. If two options tie, prefer the simpler design unless a documented constraint breaks the tie.

| Criterion | Questions to ask | Evidence to gather |
|---|---|---|
| Blast-radius tolerance | How many workloads/tenants may one API/control-plane fault affect? | Dependency map, service tiers, incident objectives. |
| Tenancy/isolation | Are tenants mutually trusted? Is cluster-admin separation required? | Threat model, access model, M12 policy requirements. |
| Residency/classification | Must data or processing remain in a jurisdiction/trust zone? | Data classification and compliance-owner input; not legal advice. |
| Latency to users/data | Does traffic or compute need to be near users/data? | Measured request latency, data-transfer path, workload profile. |
| Scale/API load | Is control-plane/controller pressure a demonstrated bottleneck? | Current Kubernetes scalability guidance plus measured workload evidence. |
| Team autonomy/ownership | Do teams need independent access and release windows? | Ownership/on-call model, release cadence. |
| Lifecycle independence | Must upgrades, credentials, or maintenance be independent? | Upgrade policy and maintenance constraints. |
| Failure-domain independence | What independence does the M13 design require? | Recovery architecture and dependency graph; do not repeat DR drills here. |
| Cost/operational capacity | Can the team patch, observe, secure, and support more clusters? | Measured per-cluster overhead and toil budget. |
| Organizational maturity | Are inventory, automation, policy, and on-call processes reliable? | Fleet audit, drift metrics, incident reviews. |

**Decision rule:** start with one cluster. Add a cluster when a specific requirement cannot be met acceptably by namespaces, quotas, node pools, policy, or another lower-complexity option. Use the fewest clusters that satisfy the isolation and availability requirements. Record rejected options and revisit triggers.

### 5.2 Worked recommendations for six scenarios

| Scenario | Assumptions and recommended topology | Alternatives rejected and why | What could change the decision |
|---|---|---|---|
| Stateless inference API | Begin with cluster-per-environment; consider cluster-per-region when user latency, residency, or regional availability requires it. Use regional replicas and explicit traffic management only after dependencies are understood. | One cluster for dev and prod may expose production to experiments. One cluster per model endpoint is usually needless overhead. | Measured latency, distinct trust zones, GPU/runtime constraints, or a formal regional availability objective. |
| ETL/batch pipelines | Keep pipelines close to source data; isolate high-impact or noisy batch workloads using namespaces/quotas first, then a batch cluster if resource contention or lifecycle requires it. | Regionally mirroring every job without data locality evidence can add transfer cost and consistency complexity. | Sustained API/control-plane pressure, dedicated compute, data residency, or separate maintenance windows. |
| ML training/GPU | Use a dedicated workload class/node pool; a dedicated cluster when GPU driver/runtime, security, capacity, or upgrade lifecycle differ materially. | A dedicated cluster solely because “ML is special” may duplicate fixed overhead. | GPU operator lifecycle conflicts, hard tenant isolation, quota constraints, or observed noisy-neighbor impact. |
| Multi-tenant notebooks | Start with namespace, quotas, network policy, identity, and admission controls only if tenants are sufficiently trusted; use dedicated clusters for stronger administrative/trust isolation. | Namespace-only isolation is insufficient when tenants can influence cluster-scoped resources or need strong trust boundaries. | Threat model, privileged workloads, compliance requirements, or tenant-controlled operators. |
| Platform tooling (CI runners, registry, observability hub) | Place high-privilege management services in a dedicated, tightly controlled platform cluster or separate trust zone when their compromise could affect the fleet. Ensure workloads do not depend on a remote hub to boot. | Hosting fleet-wide credentials in a general workload cluster concentrates risk. | Recovery requirements, scale, provider capabilities, and whether per-cluster pull agents reduce hub dependency. |
| Regulated-data workloads | Use region/trust-zone-specific clusters only after data classification and compliance owners define the actual constraints; keep data and processing placement explicit. | “Multi-cloud” alone does not prove compliance or resilience. | Jurisdictional requirements, data-flow assessment, audit controls, approved services, and legal review. |

These are conditional recommendations, not universal answers. For each scenario, document assumptions, alternatives, failure domains, operational overhead, evidence gaps, and a revisit trigger.

### 5.3 CIDR planning and overlap detection

Pod and Service CIDRs should be planned across the fleet alongside node/host ranges, VPNs, peered networks, corporate networks, and future connectivity. Overlap can prevent direct routing or complicate interconnect tooling because the same destination address may refer to different networks. Unique ranges are necessary for many routing patterns but do not provide routes, firewall rules, service discovery, or identity trust by themselves.

Example allocation (illustrative only; check against the actual host/VPN environment):

| Network purpose | East lab example | West lab example |
|---|---|---|
| Pod CIDR | `10.240.0.0/16` | `10.241.0.0/16` |
| Service CIDR | `10.96.0.0/16` | `10.97.0.0/16` |
| Host/Docker/VPN | Inspect actual environment | Inspect actual environment |

Do not blindly use these ranges if they overlap with your LAN, VPN, Docker, or existing cluster networks. `kind` configuration fields such as `networking.podSubnet` and `networking.serviceSubnet` are **[VERIFY]** for your installed version. Consult the official kind configuration documentation before running the illustrative configuration below.

`kind-east.yaml` (illustrative; verify field names and support first):

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: stage2e-east-lab
networking:
  podSubnet: "10.240.0.0/16" # [VERIFY] against installed kind version
  serviceSubnet: "10.96.0.0/16" # [VERIFY] against installed kind version
nodes:
  - role: control-plane
```

`kind-west.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: stage2e-west-lab
networking:
  podSubnet: "10.241.0.0/16" # [VERIFY] against installed kind version
  serviceSubnet: "10.97.0.0/16" # [VERIFY] against installed kind version
nodes:
  - role: control-plane
```

The exact API version above is an illustrative configuration baseline, not a promise that every installed kind version accepts it unchanged. Confirm against official docs and local `kind version`. See Lab 01 for safe creation, inspection, and cleanup.

### 5.4 Cluster identity, metadata, and registry

Every cluster needs a stable name and structured metadata. `cluster` and `region` labels are useful universal dimensions for telemetry and policy (M11), but labels should not be the only source of truth. Maintain a reviewed registry in Git containing owner, environment, region designation, tier, Kubernetes version, creation source, lifecycle state, pod/service CIDRs, credential classification, and baseline/policy status. A validator can catch missing fields, duplicate names, invalid tiers, and CIDR overlap in the declared registry; it cannot prove the live cluster matches the registry without querying the API, nor can it prove routing works.

Suggested naming convention: `<org>-<env>-<purpose>-<location>-<ordinal>`, for example `example-prod-inference-region-a-01`. Do not embed secrets, personal data, or rapidly changing version numbers in names. Store simulated location and lifecycle metadata explicitly; names alone are not authoritative.

### 5.5 Kubeconfig hygiene and access patterns

- Generate credentials per user and scope permissions to the tasks required.
- Prefer short-lived/OIDC credentials where supported; static admin certificates are a lab convenience, not a production model. [VERIFY: exact provider and identity integration support.]
- Separate kubeconfigs or access paths by environment/tier. A laptop kubeconfig with cluster-admin access to every production cluster is effectively a fleet-wide credential.
- Use direct API access only where justified; audited bastion/jump access or GitOps-only change paths can improve control. Break-glass access should be narrow, time-bounded, logged, and reviewed.
- Keep API servers private where feasible in production; this is an awareness design pattern, not something the local kind lab configures.
- Aliases and prompt indicators improve ergonomics but do not enforce authorization.

### 5.6 `kctl` context guard

The guard below is a small defense-in-depth wrapper. It allow-lists exactly the two lab aliases and injects the discovered context explicitly. It blocks an explicitly recognized set of high-impact verbs unless the user types the required token. It refuses unknown aliases and refuses any alias tagged `prod-tier`. **It is not a complete Kubernetes authorization engine**: plugins, subcommands, imperative fields, or future CLI changes may evade verb classification. Use RBAC, admission policy, scoped credentials, and reviewed change processes for real protection.

Create `kctl.py`:

```python
#!/usr/bin/env python3
"""Lab-only kubectl context guard; not a replacement for Kubernetes RBAC."""
from __future__ import annotations
import os
import subprocess
import sys

# Replace context values only with names discovered from `kubectl config get-contexts`.
# These aliases are deliberately restricted to disposable lab clusters.
TARGETS = {
    "east": {"context": "kind-stage2e-east-lab", "tier": "lab", "cluster": "stage2e-east-lab"},
    "west": {"context": "kind-stage2e-west-lab", "tier": "lab", "cluster": "stage2e-west-lab"},
}
HIGH_IMPACT_VERBS = {"delete", "replace", "apply", "create", "patch", "edit", "scale", "drain", "cordon", "uncordon"}
CONFIRM_TOKEN = "I-UNDERSTAND-LAB-IMPACT"


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in TARGETS:
        print("usage: kctl.py <east|west> <kubectl arguments...>", file=sys.stderr)
        return 2
    alias, args = argv[0], argv[1:]
    target = TARGETS[alias]
    if target["tier"] == "prod-tier" and args and args[0] in HIGH_IMPACT_VERBS:
        print("BLOCKED: writes to prod-tier targets are not permitted by this lab wrapper", file=sys.stderr)
        return 3
    if not args:
        print("ERROR: missing kubectl arguments", file=sys.stderr)
        return 2
    verb = args[0]
    if verb in HIGH_IMPACT_VERBS:
        print(f"Target cluster: {target['cluster']} | context: {target['context']} | tier: {target['tier']}")
        if target["tier"] != "lab":
            print("BLOCKED: only disposable lab targets are allowed", file=sys.stderr)
            return 3
        try:
            token = input(f"Type {CONFIRM_TOKEN} to continue: ").strip()
        except EOFError:
            print("BLOCKED: confirmation unavailable", file=sys.stderr)
            return 4
        if token != CONFIRM_TOKEN:
            print("BLOCKED: confirmation did not match", file=sys.stderr)
            return 4
    else:
        print(f"Target cluster: {target['cluster']} | context: {target['context']} | tier: {target['tier']}")
    command = ["kubectl", "--context", target["context"], *args]
    # Do not print environment variables or credential contents.
    try:
        return subprocess.run(command, check=False, env=os.environ.copy()).returncode
    except FileNotFoundError:
        print("ERROR: kubectl not found on PATH", file=sys.stderr)
        return 127


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

Usage examples (after confirming context names):

```bash
python3 kctl.py east get nodes
python3 kctl.py west get pods -A
# A lab mutation prompts for the typed token:
python3 kctl.py east apply -f app-east.yaml
```

The script prints the selected cluster and always inserts `--context`. It does not inspect all possible subcommand grammars and its prod-tier block is a guardrail, not authorization. For this lab the allow-list contains no production context; do not add one.

Create `test_kctl.py`:

```python
import unittest
from unittest.mock import patch
import kctl

class KctlTests(unittest.TestCase):
    def test_unknown_alias_rejected(self):
        self.assertEqual(kctl.main(["unknown", "get", "nodes"]), 2)

    def test_missing_args_rejected(self):
        self.assertEqual(kctl.main(["east"]), 2)

    @patch("kctl.subprocess.run")
    def test_read_injects_explicit_context(self, run):
        run.return_value.returncode = 0
        with patch("builtins.print"):
            self.assertEqual(kctl.main(["east", "get", "nodes"]), 0)
        self.assertEqual(run.call_args.args[0][:3], ["kubectl", "--context", "kind-stage2e-east-lab"])

    @patch("kctl.subprocess.run")
    @patch("builtins.input", return_value="wrong")
    def test_high_impact_requires_confirmation(self, _input, run):
        with patch("builtins.print"):
            self.assertEqual(kctl.main(["west", "delete", "pod", "demo"]), 4)
        run.assert_not_called()

    @patch("kctl.subprocess.run")
    @patch("builtins.input", return_value=kctl.CONFIRM_TOKEN)
    def test_confirmed_lab_mutation_forwards_args(self, _input, run):
        run.return_value.returncode = 0
        with patch("builtins.print"):
            self.assertEqual(kctl.main(["west", "apply", "-f", "app-west.yaml"]), 0)
        self.assertEqual(run.call_args.args[0], ["kubectl", "--context", "kind-stage2e-west-lab", "apply", "-f", "app-west.yaml"])

    def test_prod_tier_write_blocked_if_configuration_changes(self):
        old = kctl.TARGETS["east"]["tier"]
        kctl.TARGETS["east"]["tier"] = "prod-tier"
        try:
            with patch("builtins.print"):
                self.assertEqual(kctl.main(["east", "delete", "pod", "demo"]), 3)
        finally:
            kctl.TARGETS["east"]["tier"] = old

if __name__ == "__main__":
    unittest.main()
```

Run tests from the directory containing both files: `python3 -m unittest -v test_kctl.py`. The tests use mocks and do not require a live cluster. Review statically before use; do not claim tests pass until you run them in your environment.

### 5.7 Wrong-cluster incident simulation

**Hypothetical, non-executable anti-pattern:** a human intends to delete a disposable test namespace in west, but a terminal's current context has changed to production. Do not run a destructive command to reproduce this against any real cluster.

Safe demonstration:

1. Run `kubectl config get-contexts` and record the current context.
2. Use only the lab wrapper to inspect both clusters: `python3 kctl.py east get namespaces` and `python3 kctl.py west get namespaces`.
3. Demonstrate the guard with a wrong confirmation token on a lab-only high-impact command; verify that `kubectl` was not called by the unit test.
4. Use a harmless lab-only `apply` only after the wrapper prints the target and you type the required token; verify the result with the same alias/context.
5. Save the command, selected context, target echo, confirmation outcome, and post-change query as evidence.

The important control is not “be careful.” It is explicit target selection, scoped credentials, a guardrail, authorization, verification, and a reviewable record.

### 5.8 Fleet registry and validator

Create `clusters.yaml` (the following example metadata is synthetic and describes the local lab only):

```yaml
clusters:
  - name: stage2e-east-lab
    context: kind-stage2e-east-lab
    environment: lab
    region: simulated-east
    owner: platform-learning
    tier: lab
    kubernetes_version: unknown
    creation_source: kind-config
    lifecycle_state: active
    pod_cidr: 10.240.0.0/16
    service_cidr: 10.96.0.0/16
    credential_type: local-kind-admin-lab-only
  - name: stage2e-west-lab
    context: kind-stage2e-west-lab
    environment: lab
    region: simulated-west
    owner: platform-learning
    tier: lab
    kubernetes_version: unknown
    creation_source: kind-config
    lifecycle_state: active
    pod_cidr: 10.241.0.0/16
    service_cidr: 10.97.0.0/16
    credential_type: local-kind-admin-lab-only
```

Create `validate_registry.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations
import ipaddress
import sys
import yaml

REQUIRED = {"name", "context", "environment", "region", "owner", "tier", "kubernetes_version", "creation_source", "lifecycle_state", "pod_cidr", "service_cidr", "credential_type"}
VALID_ENV = {"lab", "dev", "staging", "prod"}
VALID_TIER = {"lab", "sandbox", "general", "critical", "regulated", "platform"}
VALID_STATE = {"requested", "provisioning", "active", "decommissioning", "retired"}


def overlaps(items):
    parsed = []
    errors = []
    for cluster in items:
        for field in ("pod_cidr", "service_cidr"):
            try:
                parsed.append((cluster.get("name", "<unnamed>"), field, ipaddress.ip_network(cluster[field], strict=True)))
            except (KeyError, ValueError) as exc:
                errors.append(f"{cluster.get('name', '<unnamed>')}: invalid/missing {field}: {exc}")
    for i, left in enumerate(parsed):
        for right in parsed[i + 1:]:
            if left[2].version == right[2].version and left[2].overlaps(right[2]):
                errors.append(f"CIDR overlap: {left[0]}.{left[1]} {left[2]} overlaps {right[0]}.{right[1]} {right[2]}")
    return errors


def validate(document):
    errors = []
    items = document.get("clusters") if isinstance(document, dict) else None
    if not isinstance(items, list):
        return ["top-level 'clusters' must be a list"]
    names, contexts = set(), set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"clusters[{index}] must be a mapping")
            continue
        missing = sorted(REQUIRED - set(item))
        if missing:
            errors.append(f"{item.get('name', f'clusters[{index}]')}: missing fields: {', '.join(missing)}")
        name, context = item.get("name"), item.get("context")
        if name in names:
            errors.append(f"duplicate cluster name: {name}")
        if context in contexts:
            errors.append(f"duplicate context: {context}")
        if name: names.add(name)
        if context: contexts.add(context)
        if item.get("environment") not in VALID_ENV:
            errors.append(f"{name}: invalid environment {item.get('environment')!r}")
        if item.get("tier") not in VALID_TIER:
            errors.append(f"{name}: invalid tier {item.get('tier')!r}")
        if item.get("lifecycle_state") not in VALID_STATE:
            errors.append(f"{name}: invalid lifecycle_state {item.get('lifecycle_state')!r}")
        for field in ("owner", "region", "creation_source", "credential_type"):
            if not item.get(field):
                errors.append(f"{name}: {field} must be non-empty")
    errors.extend(overlaps([x for x in items if isinstance(x, dict)]))
    return errors


def main(path):
    try:
        with open(path, encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        print(f"ERROR: cannot read registry: {exc}", file=sys.stderr)
        return 2
    errors = validate(document)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Registry validation passed (declared metadata only; live drift not checked).")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_registry.py clusters.yaml", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
```

Install PyYAML only in a project virtual environment if it is not already present; pin dependencies in the learning repository rather than installing globally. [VERIFY: local dependency management convention from M01/Stage 1.] The validator checks declared data only. A production-grade registry pipeline also compares registry entries with live cluster inventory and requires ownership and lifecycle workflows.

### 5.9 Fleet inventory script

Create `fleet_inventory.py`. It uses explicit contexts and marks unavailable data rather than inventing it. `kubectl` output and some queries depend on permissions and Kubernetes versions; resource usage is reported only if the metrics API is available.

```python
#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
import sys

TARGETS = {
    "stage2e-east-lab": "kind-stage2e-east-lab",
    "stage2e-west-lab": "kind-stage2e-west-lab",
}


def run(context, args):
    command = ["kubectl", "--context", context, *args]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return None, (result.stderr.strip() or f"exit {result.returncode}")
    return result.stdout, None


def query_json(context, args):
    output, error = run(context, [*args, "-o", "json"])
    if error:
        return None, error
    try:
        return json.loads(output), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


def inspect(name, context):
    record = {"cluster": name, "context": context, "status": "unknown"}
    version, err = query_json(context, ["version", "--output=json"])
    record["server_version"] = version.get("serverVersion", {}).get("gitVersion", "unknown") if version else f"unknown: {err}"
    nodes, err = query_json(context, ["get", "nodes"])
    if nodes:
        record["node_count"] = len(nodes.get("items", []))
        record["nodes"] = [n.get("metadata", {}).get("name", "unknown") for n in nodes.get("items", [])]
        record["node_pod_cidrs"] = [
            {"node": n.get("metadata", {}).get("name", "unknown"),
             "podCIDR": n.get("spec", {}).get("podCIDR", "unknown"),
             "podCIDRs": n.get("spec", {}).get("podCIDRs", [])}
            for n in nodes.get("items", [])
        ]
        record["status"] = "reachable"
    else:
        record["node_count"] = "unknown"
        record["nodes"] = f"unknown: {err}"
    crds, err = query_json(context, ["get", "customresourcedefinitions"])
    record["crds"] = len(crds.get("items", [])) if crds else f"unknown: {err}"
    namespaces, ns_err = query_json(context, ["get", "namespaces"])
    record["namespace_pod_security_labels"] = []
    if namespaces:
        for ns in namespaces.get("items", []):
            labels = ns.get("metadata", {}).get("labels", {})
            selected = {k: v for k, v in labels.items() if k.startswith("pod-security.kubernetes.io/")}
            if selected:
                record["namespace_pod_security_labels"].append({"namespace": ns["metadata"]["name"], "labels": selected})
    else:
        record["namespace_pod_security_labels"] = f"unknown: {ns_err}"
    for resource, key in (("deployments", "deployments"), ("validatingwebhookconfigurations", "validating_webhooks"), ("clusterpolicies.kyverno.io", "kyverno_cluster_policies")):
        data, err = query_json(context, ["get", resource])
        record[key] = len(data.get("items", [])) if data else f"unknown/not installed: {err}"
    metrics, err = query_json(context, ["top", "nodes"])
    record["node_metrics"] = metrics if metrics else f"unknown/not installed: {err}"
    return record


def main():
    output = []
    failed = False
    for name, context in TARGETS.items():
        record = inspect(name, context)
        output.append(record)
        if record.get("status") != "reachable":
            failed = True
    print(json.dumps(output, indent=2, sort_keys=True))
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Important static-review note:** this script is a starter inventory, not a complete fleet discovery agent. `kubectl version --output=json` may not be accepted in every client/server combination, `top nodes` is text-oriented rather than JSON in common kubectl versions, and resource names for policy engines are installation-specific. Those details are intentionally reported as `[VERIFY]` candidates rather than claimed as universal. Before using the script, adjust each query to the installed `kubectl` and components, then test against fixtures/mocks and the lab. Do not interpret missing permissions or missing metrics-server as zero usage or zero policies.

Recommended automated tests should mock `subprocess.run` and cover: a reachable cluster; API failure; malformed JSON; no metrics API; missing CRDs; and explicit context on every invocation. Integration tests against live clusters are optional and should be separately labeled.

### 5.10 Architecture Decision Record (ADR)

**Worked example — inference API environment split**

- **Context:** a team operates a stateless inference API with separate development and production release cadence. The platform team has a single-cluster baseline and limited capacity to operate a large fleet.
- **Requirements:** prevent development changes from affecting production control-plane resources; support promotion and independent production maintenance; keep fixed overhead manageable.
- **Options:** (A) one cluster with namespaces/policy; (B) cluster per environment; (C) cluster per model service.
- **Decision:** choose B, two environment clusters, provided inventory, policy baseline, and GitOps promotion are automated before adding more clusters.
- **Trade-offs:** higher fixed overhead and duplicated add-ons; clearer control-plane/lifecycle separation. Shared Git, registry, identity, and deployment credentials remain common risks and must be reviewed.
- **Evidence:** change-impact review, production access requirements, measured per-cluster overhead, and successful staged promotion evidence. No numerical claim until measured.
- **Owner/review:** platform owner; review at the next major service tier or tenancy change.
- **Revisit triggers:** operational toil exceeds the agreed budget; control-plane load demonstrates a need for further split; residency/latency changes; shared dependencies dominate the desired isolation.

Reusable template:

```markdown
# ADR-NNN: <decision title>
- Status: proposed | accepted | superseded
- Owner:
- Created / review date:
- Context and problem:
- Requirements and hard constraints:
- Options considered:
- Decision and rationale:
- Trade-offs and rejected alternatives:
- Security and trust-boundary consequences:
- Failure-domain/shared-dependency consequences:
- Capacity/cost/operational consequences:
- Evidence and confidence:
- Evidence gaps:
- Rollback or migration plan:
- Revisit triggers:
```

### 5.11 Pattern catalogue

| Pattern | Use when | Do not use when |
|---|---|---|
| Few clusters with namespaces/quotas | Tenants are trusted enough and requirements are mostly logical/resource isolation | Hard admin/trust boundary is required. |
| Cluster per environment | Promotion and access separation matter | No team can maintain consistent baselines or inventory. |
| Cluster per region | Latency, residency, or regional service objectives require it | The design still depends on one remote region for critical boot/runtime paths. |
| Dedicated workload-class cluster | GPU/runtime, batch contention, or lifecycle differs materially | The difference can be safely handled with node pools and quotas. |
| Hub-and-spoke | Fleet-level policy and inventory are needed | Hub has unrestricted credentials and no failure/recovery plan. |
| Cell-based | User/tenant partitioning can bound impact | Every cell still calls one shared stateful dependency in its critical path. |
| Separate cluster per service | Rarely; only with strong independent security/lifecycle/scale requirements | It is done solely for organizational neatness. |

### 5.12 Anti-pattern catalogue

| Bad practice | How it fails | Correction |
|---|---|---|
| Rely on current context | Human or script operates on unintended cluster | Explicit context, target echo, least privilege, guard and verification. |
| Overlapping fleet CIDRs | Routing ambiguity and interconnect limitations | Fleet-wide CIDR registry including host/VPN/peer ranges. |
| Snowflake clusters | Drift and rebuild failure | Declarative config, inventory, conformance checks, lifecycle policy. |
| Stretched regional control plane | Network partitions/latency couple control-plane failure domains | Independent regional clusters plus explicit fleet coordination; verify architecture-specific guidance. |
| One cluster per microservice | Fixed overhead and on-call surface grow without commensurate isolation | Split on risk, tenancy, lifecycle, geography, or scale requirements. |
| All-powerful hub credentials | One compromise can alter the fleet | Scoped credentials, pull-based reconciliation where appropriate, separate trust zone, audit, break-glass. |
| Shared registry across all cells with no fallback | Registry outage can block deployment/recovery across cells | Local/replicated artifact strategy and explicit outage behavior. |

### 5.13 Per-cluster verification matrix

| Verification | East lab | West lab | Why it matters |
|---|---|---|---|
| Actual context name recorded | Required | Required | Avoid relying on assumed naming. |
| API endpoint/cluster reachable | Required | Required | Confirms independent API selections. |
| Node name/count captured | Required | Required | Basic inventory. |
| Pod/service CIDRs recorded or clearly marked unknown | Required | Required | CIDR plan validation. |
| Same app manifest deployed | Required | Required | Demonstrates repeatable configuration. |
| Response identifies east vs west | `east-lab` | `west-lab` | Proves different cluster-specific configuration served requests. |
| Owner/tier/lifecycle in registry | Required | Required | Governance and inventory. |
| Cleanup verified | Required | Required | Prevents leftover resources. |

## 6. Level 3 — Advanced: engineering the fleet shape

### 6.1 Blast-radius analysis

For every significant failure, ask: what is the largest set of workloads, tenants, data, and users affected? Analyze control-plane/API failure, bad upgrade, webhook/CRD/controller failure, leaked credentials, shared identity/DNS/registry outage, network partition, and data-store failure. Separate **cluster control-plane isolation** from **workload isolation**, **network isolation**, **identity isolation**, **data isolation**, and **management-plane isolation**.

| Failure | Likely scope if dependencies are shared | Boundary/control to consider | Evidence to collect |
|---|---|---|---|
| API/control-plane outage | Workloads in that cluster may continue partially, but scheduling/reconciliation/API operations degrade | Separate clusters for critical blast-radius needs; tested workload behavior | API health, workload behavior, recovery records. |
| Bad fail-closed webhook | API operations matching the webhook can be blocked in that cluster | Canary, narrow selectors/rules, rollback path, separate clusters for stronger isolation | Admission test, webhook reachability, safe recovery evidence. |
| Fleet-wide GitOps error | Every target receiving the same change | Canary cluster, rings, review gates, pause criteria | Promotion history and per-cluster diff. |
| Credential leak | All clusters accessible to leaked identity | Per-cluster/tier identities, least privilege, JIT, audit | Access review and negative authorization tests. |
| Shared registry outage | Deployments or scale-out may fail in all dependent clusters | Replication/cache/local fallback and dependency ownership | Pull behavior under outage, dependency graph. |
| Shared DNS/identity outage | Multiple clusters may fail discovery/authentication | Local resilience, fallback, independent failure-domain placement | Dependency test and SLO impact. |

A cluster boundary limits the scope only for failures that do not cross it. A shared management credential, common database, or host-level outage can defeat the boundary. Use a dependency graph and document residual risk rather than saying “clusters are isolated.”

### 6.2 Tiered fleets

Possible tiers include: (1) tier-0 platform/critical services with strict access and change control; (2) general-purpose workloads; (3) sandbox/experimentation with TTL and quotas; (4) ML/GPU and batch pools with specialized runtime/capacity; and (5) regulated or trust-zone-specific workloads. Tiering is useful when risk, ownership, or lifecycle differ. It is harmful when tiers become labels without enforceable policy or when each small variation creates another snowflake cluster.

### 6.3 Environment promotion, canary clusters, and rollout rings

Promote platform changes through development, staging, a representative canary cluster, then production waves. A canary cluster should receive platform changes first and be representative enough to expose important compatibility issues. Define success metrics and stop conditions before rollout: conformance checks, policy drift, workload health, error budgets, and rollback readiness. Use rings to bound the number of clusters exposed before evidence is reviewed. Unit 3 owns multi-cluster GitOps mechanics; this unit establishes why topology and change blast radius matter.

### 6.4 Regional placement and data gravity

Place compute near users when latency dominates and near data when data movement dominates. ETL and ML training often benefit from “compute follows data” because moving large datasets can increase latency, cost, and data exposure. Consider residency, service dependencies, model-artifact access, registry availability, local capacity, and on-call ownership. A region is not independent merely because workloads are deployed there; the request path, data replication, identity, DNS, and management dependencies must support the intended failure behavior. Refer to M05 Unit 7 for data placement and M13 for recovery objectives rather than repeating their procedures here.

### 6.5 Cell-based architecture

A cell is an independently operated service stack plus a partition of tenants/users/data. A routing layer maps a tenant to its assigned cell. For example, tenants A–M may be assigned to cell 1 and N–Z to cell 2; a request should usually stay within its cell rather than calling another cell synchronously. Cells can each contain one or multiple Kubernetes clusters. The mapping is a design choice, not a definition.

```text
                 Tenant-aware routing
                   /            \
             tenant group A   tenant group B
                  |                |
          +-------v------+  +------v-------+
          | Cell A       |  | Cell B       |
          | API + workers|  | API + workers|
          | data shard A |  | data shard B |
          +--------------+  +--------------+
             | local deps      | local deps
             +------X-----------+  Avoid cross-cell synchronous
                                   dependency in critical path

      Shared global routing/identity/registry may still be a common
      failure domain unless deliberately separated or made resilient.
```

Benefits: bounded tenant impact and independent scaling/rollout. Costs: duplicated services, uneven load, routing complexity, data partitioning, and difficult tenant movement. A cell failure may require routing away from the cell only if another cell can safely serve that tenant’s data and capacity. “Shuffle sharding” is an awareness concept for reducing correlated exposure; verify primary documentation and do not imply it automatically solves data consistency. [VERIFY]

### 6.6 Hub-and-spoke management topology

A hub may host GitOps controllers, Cluster API, central policy distribution, or observability aggregation, while spokes host workloads. This improves consistency but concentrates credentials and control. If the hub is unavailable, already-running workloads often continue, while changes, reconciliation, or central visibility may pause; exact behavior depends on where controllers run and what they manage. If the hub is compromised, an attacker may be able to alter many clusters.

Controls include a dedicated hub failure domain, high availability where justified, scoped per-cluster credentials, per-cluster pull agents where appropriate, audited break-glass access, recovery procedures for the management plane, and a defined “hub unavailable” operating mode. Do not host the sole management plane in the same failure domain it is intended to manage without a documented reason and recovery plan.

### 6.7 Shared-services strategy and dependency direction

| Dependency | Placement options | Main trade-off / outage question |
|---|---|---|
| Container registry | Local per cluster, regional mirror, or global service | Can existing workloads run if the registry is down? Can a new node pull critical images? |
| CI runners | Per environment/region or shared fleet | Do runners hold broad cluster credentials? Can one runner compromise all clusters? |
| Secrets backend | Per trust zone/region or replicated service | Can a region start/recover without a remote region? What is the trust boundary? |
| DNS | Local, regional, and/or global layers | Which resolvers/cache clients keep stale answers, and what is the fallback? |
| Identity provider | Shared global service with carefully defined fallback | Can workloads authenticate during IdP outage? Which credentials are cached? |
| Git server | Shared source of truth or replicated service | Does hub outage stop workload execution or only reconciliation? |
| Observability | Per-cluster agents plus central view | Can clusters operate if central telemetry is unavailable? Is the central view a shared dependency? |
| Artifact/object storage | Regional replicas or local copies | Is replication lag acceptable? What is the authoritative copy? |

Prefer local dependencies in the request and boot paths where feasible. Avoid making region B’s boot, recovery, or critical request path depend on remote region A. Document owners, timeouts, fallback behavior, and observability for every cross-cluster call. M13 Unit 3/6 owns recovery order and dependency-outage strategy; this unit applies those concepts to steady-state fleet design.

### 6.8 Capacity, quotas, cluster scale, and N+1 thinking

Capacity planning includes workload CPU/memory, node pools, pod density, DaemonSets, CRD count, namespaces, watches/lists, controllers, admission webhooks, API-server load, IP allocation, and system overhead. Use current official Kubernetes scalability guidance for limits and assumptions; do not quote thresholds from memory. [VERIFY: Kubernetes documentation → “Scalability” and relevant version-specific guidance.]

N+1 thinking asks whether the remaining clusters can serve required traffic after losing one cluster/region. It is not enough to count replicas: capacity, data availability, identity, routing, dependencies, and failover behavior must all be compatible. For the laptop lab, use measured resource units; do not infer production capacity from kind.

### 6.9 Many small clusters vs. fewer large clusters

**Many small clusters:** smaller control-plane blast radius and independent lifecycle, but more fixed overhead, repeated DaemonSets/controllers, more upgrades, more CIDR allocations, more access paths, and greater fleet automation needs. **Fewer large clusters:** better bin-packing and fewer duplicated components, but more workloads share API/control-plane failure modes and upgrades. Neither is universally superior. Model the operational and risk costs using measured baselines, and include team maturity as a design variable.

### 6.10 Measured platform-overhead model

Use a script or spreadsheet with measured inputs: per-cluster control-plane/system overhead, observability agents, policy engines, and workload capacity. Calculate total fixed overhead as cluster count increases and perform sensitivity analysis. Any example values must be explicitly synthetic. Cloud control-plane prices, cross-region egress, managed services, and standby capacity cannot be inferred from local CPU/RAM measurements.

Create `overhead_model.py`:

```python
#!/usr/bin/env python3
"""Calculate fleet overhead from user-measured resource units."""
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clusters", type=int, nargs="+", default=[1, 2, 4, 8])
    parser.add_argument("--system", type=float, required=True, help="measured system overhead units per cluster")
    parser.add_argument("--observability", type=float, default=0.0, help="measured agent overhead units per cluster")
    parser.add_argument("--policy", type=float, default=0.0, help="measured policy overhead units per cluster")
    parser.add_argument("--workload-capacity", type=float, help="measured total workload capacity units for comparison")
    args = parser.parse_args()
    if any(n < 1 for n in args.clusters) or min(args.system, args.observability, args.policy) < 0:
        parser.error("cluster counts must be positive and resource units non-negative")
    per_cluster = args.system + args.observability + args.policy
    print("clusters,per_cluster_overhead,total_overhead,overhead_pct_of_workload_capacity")
    for count in args.clusters:
        total = count * per_cluster
        pct = "unknown"
        if args.workload_capacity is not None:
            if args.workload_capacity <= 0:
                parser.error("workload capacity must be positive")
            pct = f"{100 * total / args.workload_capacity:.2f}%"
        print(f"{count},{per_cluster:.3f},{total:.3f},{pct}")

if __name__ == "__main__":
    main()
```

The units may be CPU cores, GiB, or an internally defined normalized unit, but do not mix them. Example values should be labelled synthetic and replaced with measurements from your lab. This model omits cloud pricing and does not predict production costs.

### 6.11 Multi-tenancy alternatives

| Option | Isolation | Advantages | Limitations / choose when |
|---|---|---|---|
| Namespaces + quotas + policy | Logical; depends on policy and privileges | Low overhead, simple tenancy for trusted teams | Not sufficient for all hostile or privileged tenants. Cross-reference M12 Unit 7. |
| Node-pool isolation | Scheduling/resource separation | Different hardware/runtime and noisy-neighbor control | Still shares cluster control plane and cluster-scoped admin surface. |
| Virtual clusters (e.g., vcluster) | Virtualized Kubernetes API experience; implementation-specific | Tenant autonomy with less physical-cluster overhead | Verify current project/docs, isolation properties, and operational model before adoption. [VERIFY] |
| Dedicated clusters | Separate API/control-plane and administrative configuration | Stronger boundary and independent lifecycle | Higher fixed overhead, drift risk, more operations. |

Choose based on threat model, administrative autonomy, resource contention, compliance, and the team’s ability to operate the boundary. A “harder” boundary is not automatically better if the fleet cannot be secured and maintained.

### 6.12 Cluster lifecycle and inventory automation

Define cluster states such as requested, provisioning, active, decommissioning, and retired. Record owner, creation source, supported Kubernetes version, upgrade window, baseline status, certificate/node-image rotation policy, maximum sandbox age, and retirement criteria. Clusters should be declarative and replaceable, but persistent data and external dependencies require migration plans. Build inventory automation now so Unit 2 can add lifecycle APIs, Unit 3 can drive safe promotion, and Unit 8 can aggregate policy/observability evidence.

### 6.13 Design exercise requiring a defended decision

Choose a topology for a platform with a stateless inference API, a PostgreSQL system of record, object storage for datasets/model artifacts, ETL pipelines, model registry, per-cluster secrets/identity, and a central observability view. State: (1) hard constraints; (2) cluster/region/cell boundaries; (3) which dependencies are local vs shared; (4) what continues if the management hub is down; (5) capacity after losing one cluster; (6) data and tenant placement; (7) evidence required before production; (8) what would trigger a redesign. A defensible answer is one that exposes assumptions and residual risks, not one that maximizes cluster count.

## 7. Level 4 — Expert: governance, migrations, and failure analysis

### 7.1 Fleet standards and topology ADR governance

A fleet standard should define supported Kubernetes versions and upgrade windows; mandatory platform components; baseline security and admission controls; required labels and owner metadata; CIDR allocation rules; access and credential requirements; observability requirements; inventory freshness; conformance/drift checks; lifecycle/retirement policy; and a time-bounded exception process. Topology decisions belong in ADRs with explicit revisit triggers. A policy without an owner, verifier, or remediation path is only documentation.

### 7.2 Cluster vending and golden paths (forward reference)

A future M16 golden path may follow: request → approval/quota/policy checks → IaC or Cluster API provisioning → baseline via GitOps → identity/access setup → registry registration → conformance checks → owner handoff. Add anti-sprawl controls: cluster-count quotas, sandbox TTLs, required owner, expiry alerts, exception approvals, and cost attribution/showback (M15 forward reference). This unit does not implement a full vending platform.

### 7.3 Cluster sprawl and shadow-cluster remediation

Discover clusters from cloud/provider inventories, kubeconfig sources, management APIs, network inventory, and billing/ownership records where available. Reconcile each with the registry. Flag ownerless clusters, stale inventory, unsupported versions, baseline drift, excessive idle resources, and unknown external dependencies. Before decommissioning, verify ownership, data/state, DNS, certificates, workloads, service consumers, and recovery/rollback requirements. Never delete a cluster merely because it is absent from one registry.

### 7.4 Fleet-scale automation, toil, and ownership

Automate inventory, version/upgrade status, node image rotation, certificate rotation, policy enforcement, identity review, drift detection, conformance, expiry, and decommission workflows. Assign an owner to each cluster and shared dependency; define on-call ownership and escalation. Track toil and operational burden (M10). Fleet automation must have staged rollout, observability, idempotency, pause controls, and a safe recovery path; automation can multiply both good and bad changes.

### 7.5 Split-cluster migration playbook

1. Record the requirement and measurable success criteria.
2. Map workload/tenant boundaries, state, identities, policies, network paths, and shared dependencies.
3. Provision and baseline the destination declaratively.
4. Verify quotas, policy, observability, credentials, image access, DNS, and network requirements.
5. Move stateless workloads progressively through the established delivery workflow.
6. Plan stateful migration separately; validate data correctness and consistency. Reference M13/Velero where applicable; do not treat backup as a complete migration strategy.
7. Shift traffic with a controlled mechanism (Unit 5), with explicit rollback triggers.
8. Verify SLOs, correctness, access, and operational ownership.
9. Retire old resources only after dependency/owner checks and a defined observation period.

Data migration and hidden dependencies are often the hardest parts. A successful Deployment rollout does not prove the data path or tenant routing is correct.

### 7.6 Merge/consolidation playbook

Consolidate only when duplicated overhead and operational cost outweigh the isolation benefit. Identify CIDR conflicts, identity/trust differences, policy and quota conflicts, cluster-scoped resources, data residency, ownership, and lifecycle differences. Test workload and data movement in stages, preserve trust boundaries, define rollback, and require a decommission checklist. Do not merge tenants merely because their CPU usage is low.

### 7.7 Shared-fate analysis and hidden dependencies

A useful dependency inventory for this lab:

```yaml
clusters:
  stage2e-east-lab:
    shared_dependencies: [host-os, docker-daemon, host-power, local-disk, docker-network]
    optional_dependencies: [local-registry, git-server, dns-simulator, minio]
  stage2e-west-lab:
    shared_dependencies: [host-os, docker-daemon, host-power, local-disk, docker-network]
    optional_dependencies: [local-registry, git-server, dns-simulator, minio]
```

Create a script that counts dependencies referenced by more than one cluster and flags them as shared-fate candidates. This graph is an inventory aid, not proof of actual failure independence. The lab cannot isolate laptop power, host kernel, Docker daemon, or a common physical disk. In production, add DNS, identity, registry, GitOps hub, CA, network transit, database, artifact storage, and cloud account/control-plane dependencies to the graph.

### 7.8 Security topology and hub-compromise scenarios

Use cluster-per-trust-zone where the threat model requires separate administrative/control-plane domains. Scope credentials to individual clusters or tiers, use just-in-time access where available, audit privileged operations, maintain policy parity, and run negative tests that prove an identity cannot access an unauthorized cluster. A hub compromise can become fleet compromise if it holds broad credentials or can publish unrestricted desired state. Reduce this risk with scoped identities, pull-based agents where appropriate, protected Git/review, signed artifacts/config where applicable, policy enforcement in each cluster, independent audit, and break-glass procedures. Cross-reference M09 and M12 rather than re-teaching them.

### 7.9 Edge, hybrid, and multi-cloud awareness

Edge/IoT clusters may have intermittent connectivity and constrained resources; pull-based reconciliation and offline-tolerant operation can be useful, but exact distribution capabilities must be verified. k3s-class distributions are awareness-only here. [VERIFY: current supported versions and project guidance.] Hybrid/multi-cloud can address residency, acquisitions, or vendor risk, but increases skills, networking, egress, observability, identity, and portability costs. “Multi-cloud” is not automatically multi-region resilience: two clouds can still share identity, data, DNS, management, or application dependencies.

### 7.10 Eight incident analyses (hypothetical scenarios)

These are design exercises, not claims about real incidents. No production event or metric is asserted.

1. **Wrong context and namespace deletion** — *Symptom:* an intended lab action appears to affect production. *Hypotheses:* stale current context, merged kubeconfig, script default. *Safe tests/evidence:* inspect contexts, effective kubeconfig, command logs, and credential identity without running a destructive command. *Root cause:* target was implicit and credentials were too broad. *Immediate mitigation:* halt changes, follow incident/change process, use authorized read-only verification. *Prevention:* explicit context, guard, least privilege, protected change workflow. *Residual risk:* a privileged identity can bypass a local wrapper.
2. **Default kind CIDR collision** — *Symptom:* later cross-cluster routing is ambiguous or cannot be established. *Hypotheses:* overlapping pod/service/host/VPN ranges. *Safe tests/evidence:* inspect actual ranges and compare network plans. *Root cause:* no fleet CIDR registry. *Mitigation:* redesign the lab network before interconnect work. *Prevention:* validate CIDRs at cluster registration. *Residual risk:* non-overlap does not create routes or service discovery.
3. **Fail-closed webhook disrupts one cluster** — *Symptom:* matching API operations are rejected or hang in east while west API remains queryable. *Hypotheses:* webhook unavailable, selector too broad, bad policy rollout. *Safe tests/evidence:* only in a disposable cluster, inspect webhook config/events and use a recovery plan; never reproduce on production. *Root cause:* unbounded admission dependency and no canary/rollback. *Mitigation:* use the documented lab recovery path or recreate the disposable cluster. *Prevention:* narrow rules, canary, timeouts, documented break-glass. *Residual risk:* cluster-scoped faults can still affect all matching operations.
4. **Stretched control plane partitions across sites** — *Symptom:* API/control-plane instability under latency or partition. *Hypotheses:* quorum/latency sensitivity and shared failure-domain assumptions. *Safe tests/evidence:* review topology and current etcd/Kubernetes guidance; do not simulate by damaging a real control plane. *Root cause:* regional resilience attempted with a single stretched control plane. *Mitigation:* restore supported connectivity/control-plane health using the architecture runbook. *Prevention:* verify control-plane placement and use independent regional clusters where appropriate. *Residual risk:* regional applications may still share data and management dependencies. [VERIFY]
5. **Forty clusters, no inventory** — *Symptom:* unknown owners and versions; patch posture cannot be established. *Hypotheses:* manual creation and no registry reconciliation. *Safe tests/evidence:* reconcile provider/management inventories, kubeconfigs, and ownership records. *Root cause:* lifecycle not treated as a governed fleet. *Mitigation:* build an inventory and prioritize unsupported/high-risk clusters. *Prevention:* registration gates, freshness SLO, owner enforcement, automated conformance. *Residual risk:* undiscovered clusters may remain outside known inventories.
6. **Single GitOps hub credential leaks** — *Symptom:* unexpected fleet-wide desired-state changes. *Hypotheses:* broad token, insufficient review, no scoped identities. *Safe tests/evidence:* review audit logs and granted permissions without exposing secrets. *Root cause:* one credential could mutate all clusters. *Mitigation:* revoke/rotate through authorized process and halt rollout. *Prevention:* scoped identities, protected source, canary rings, audit, break-glass. *Residual risk:* hub/source compromise can still affect many targets.
7. **All cells share one registry** — *Symptom:* deployment/scale-out fails across cells during registry outage. *Hypotheses:* uncached images, no regional mirror, boot path depends on remote service. *Safe tests/evidence:* inspect image pull events and dependency map; use controlled tests in a lab. *Root cause:* hidden shared dependency. *Mitigation:* rely on cached/replicated images where valid and restore registry service. *Prevention:* local/replicated artifacts and outage tests. *Residual risk:* a shared upstream may remain a common dependency.
8. **Sandbox clusters outlive their owners** — *Symptom:* idle clusters, unknown workloads, stale versions, unexplained overhead. *Hypotheses:* no TTL, owner, or lifecycle state. *Safe tests/evidence:* inventory workloads, owner records, dependencies, and resource use before action. *Root cause:* no expiry workflow. *Mitigation:* notify owners and quarantine/decommission only after dependency review. *Prevention:* TTLs, owner labels, alerts, quotas, retirement runbook. *Residual risk:* undocumented consumers can be missed.

### 7.11 Governance and change-review checklist

- [ ] The topology ADR states requirements, alternatives, owner, evidence, and revisit triggers.
- [ ] Each cluster has a unique name, owner, environment, tier, location designation, version, lifecycle state, and creation source.
- [ ] Pod, Service, node, host, VPN, and future peering ranges are recorded and validated.
- [ ] Cluster admin credentials are scoped; no casual laptop kubeconfig grants cluster-admin across production.
- [ ] Canary cluster and rollout rings are defined; pause/rollback criteria are measurable.
- [ ] Shared dependencies and owners are documented, including hub/DNS/identity/registry/Git/data services.
- [ ] Policy and observability baselines are verified per cluster.
- [ ] N+1 capacity and dependency behavior are documented for critical workloads.
- [ ] Cluster lifecycle, maximum sandbox age, upgrade cadence, and decommission procedure are defined.
- [ ] Exceptions have owners, compensating controls, and expiry dates.

## 8. SRE lens

Define service indicators for fleet convergence time, rollout-wave success rate, number of clusters out of policy, inventory freshness, cross-cluster call success/latency, replication lag (Unit 7), traffic-switch time (Unit 5), and per-region SLO attainment. Set targets from service requirements and observed baselines; do not invent a universal threshold. Track failures by cluster, region, tier, and owner. Ask “what happens to the other cluster if this fails?” for every dependency.

**Runbook snippet:** trigger (fleet drift, canary failure, cluster unreachable) → pause further rollout → identify affected clusters using explicit contexts → inspect read-only evidence → decide rollback/containment with incident owner → execute only through approved guarded workflow → verify each cluster independently → communicate scope and residual risk → record follow-up and prevention. Measure duplicated platform overhead and standby capacity; cloud transfer/egress and managed-service costs require real provider data, not laptop estimates.

## 9. Security lens

Threats include credential sprawl, hub compromise, lateral movement, inconsistent policy, trust-boundary mistakes, tampered config propagation, and exposed cross-cluster endpoints. This unit does not configure a production IdP, cloud private API endpoints, or a complete fleet policy controller.

| Control | Verification / negative test |
|---|---|
| Scoped per-cluster identities | Attempt a read against an unauthorized lab/test identity and verify authorization is denied; do not use production credentials. |
| Protected configuration changes | Confirm changes require review and that the canary is first in the promotion order. |
| Policy parity | Compare required policy presence and versions per cluster; missing capability is `unknown`, not a pass. |
| Context guard | Tests prove unknown aliases and wrong confirmation are blocked; separately verify RBAC because wrapper bypass is possible. |
| Credential hygiene | Review kubeconfig sources and credential types without printing tokens or private keys. |
| Cross-cluster endpoint exposure | Inspect service exposure, network controls, and authentication requirements; test unauthorized access in a disposable environment. |
| Shared management-plane risk | Document hub access scope and prove that workload operation during hub outage is understood for the chosen architecture. |

## 10. Production-readiness checklist

- [ ] A written requirement justifies each cluster boundary.
- [ ] The simplest alternative (namespace/quota/policy/node pool) was considered and accepted/rejected with evidence.
- [ ] All clusters are registered with owner, tier, lifecycle, version, and network metadata.
- [ ] Every automation command selects its context explicitly and verifies its target.
- [ ] Fleet CIDR allocation accounts for pods, Services, nodes, host, VPN, and future connections.
- [ ] No one assumes the two kind clusters are independent regions.
- [ ] Shared dependencies and their outage behavior are documented.
- [ ] The management plane has scoped credentials, a recovery plan, and a defined outage mode.
- [ ] Platform changes are promoted through canary/rings with pause criteria.
- [ ] Capacity after a cluster/region loss is considered for critical workloads.
- [ ] Cluster lifecycle, drift, policy conformance, access reviews, and decommissioning are automated or assigned.
- [ ] Every exception has an owner and expiry.

## 11. Hands-on lab set

All labs use the Fleet-Core profile unless explicitly stated. Start only the components required for the current lab. **Measure yours**: CPU, memory, and disk use vary by OS, Docker configuration, and image cache. The labs cannot establish real regional independence.

### M14-U1-LAB-01 — Create two kind clusters and inspect context/CIDR boundaries

- **Goal:** create two named lab clusters, discover contexts, inspect actual network ranges, and document a non-overlapping plan.
- **Profile:** Fleet-Core. **Clusters:** both. **Destructive:** creation/deletion of disposable lab clusters only.
- **Prerequisites:** Docker, kind, kubectl; review kind networking config docs first. `[VERIFY]` config fields.
- **Start list:** Docker only. **Stop list:** no optional GitOps, observability, database, or DNS components.
- **Steps (Bash, WSL2 Ubuntu/native Linux):**

```bash
set -euo pipefail
kind version
docker version
kubectl version --client
# Verify the two illustrative YAML files against the installed kind docs/version.
kind create cluster --config kind-east.yaml
kind create cluster --config kind-west.yaml
kubectl config get-contexts
kubectl --context kind-stage2e-east-lab get nodes -o wide
kubectl --context kind-stage2e-west-lab get nodes -o wide
kubectl --context kind-stage2e-east-lab get nodes -o jsonpath='{range .items[*]}{.metadata.name}{" podCIDR="}{.spec.podCIDR}{"\n"}{end}'
kubectl --context kind-stage2e-west-lab get nodes -o jsonpath='{range .items[*]}{.metadata.name}{" podCIDR="}{.spec.podCIDR}{"\n"}{end}'
kubectl --context kind-stage2e-east-lab get service kubernetes -o jsonpath='{.spec.clusterIP}{"\n"}'
kubectl --context kind-stage2e-west-lab get service kubernetes -o jsonpath='{.spec.clusterIP}{"\n"}'
```

  The Kubernetes Service IP shown is one address, not the full Service CIDR. Record the configured CIDRs from the kind configs and verify actual cluster/network evidence with version-appropriate methods. Do not claim a complete CIDR audit from a single Service IP.

- **Overlap demonstration:** inspect the actual default configs/cluster values for the installed kind version; compare the pod/service ranges. Do not assert all defaults overlap in every environment. If the defaults overlap, record the evidence, delete only these named disposable clusters, then recreate from the reviewed distinct-range configs. If they do not overlap, document that observed result and still maintain a fleet plan.
- **Expected evidence:** config files, discovered context names, node output, declared/observed CIDR table, and note of any unknowns.
- **Cleanup:** after verifying the cluster names in `kind get clusters`, delete only `stage2e-east-lab` and `stage2e-west-lab` if you intend to remove them: `kind delete cluster --name stage2e-east-lab` and `kind delete cluster --name stage2e-west-lab`. `kind` cluster deletion targets a cluster name rather than kubectl context; double-check names before running.
- **Stretch:** add registry validation for a host/VPN range. **Laptop caveat:** one host remains a shared failure domain.

### M14-U1-LAB-02 — Context guard and wrong-cluster safety

- **Goal:** prove the wrapper chooses an explicit context, blocks unknown aliases, and requires confirmation for high-impact lab verbs.
- **Profile:** Fleet-Core. **Clusters:** both. **Destructive:** none required; any apply/delete experiment must target only the disposable lab clusters.
- **Start list:** clusters from Lab 01. **Stop list:** none.
- **Steps:** save `kctl.py` and `test_kctl.py` from §5.6; run `python3 -m unittest -v test_kctl.py`; inspect `kubectl config get-contexts`; use `python3 kctl.py east get nodes` and `python3 kctl.py west get nodes`. Try an unknown alias and wrong confirmation; verify non-zero exit and no kubectl subprocess invocation via tests.
- **Expected evidence:** test output, target echo, rejected unknown alias, rejected confirmation, and exact context injected in test assertion.
- **Cleanup:** no cluster resources created. **Stretch:** add a `--dry-run` mode and test it. **Laptop caveat:** this tests wrapper behavior, not authorization or regional isolation.

### M14-U1-LAB-03 — Cluster registry and validator

- **Goal:** record metadata and catch missing fields, duplicate names, invalid tiers/states, and overlapping CIDRs.
- **Profile:** Fleet-Core. **Clusters:** registry data for both; no API mutations. **Destructive:** no.
- **Start list:** none. **Stop list:** none.
- **Steps:** save `clusters.yaml` and `validate_registry.py` from §5.8; install PyYAML in an isolated environment if needed; run `python3 validate_registry.py clusters.yaml`. Then make a temporary copy with an overlapping CIDR or missing owner and confirm the validator exits non-zero.
- **Expected evidence:** pass result for the synthetic registry and failure output for the intentionally invalid copy.
- **Cleanup:** remove temporary invalid copy and virtual environment only if no longer needed. **Stretch:** add checks for duplicate network names and live inventory drift. **Laptop caveat:** registry validation alone does not prove live cluster state or routing.

### M14-U1-LAB-04 — Fleet inventory script

- **Goal:** query both contexts explicitly and represent missing optional capabilities honestly.
- **Profile:** Fleet-Core. **Clusters:** both. **Destructive:** no.
- **Start list:** clusters from Lab 01. **Stop list:** no optional observability stack required.
- **Steps:** save `fleet_inventory.py` from §5.9; inspect every `kubectl` query against your installed client; run it against the two lab clusters. Create mocked tests for API failure, invalid JSON, missing metrics API, and missing policy CRDs before relying on the script.
- **Expected evidence:** JSON inventory with explicit cluster/context identity, node count/names, version or `unknown`, CRD count or error, PSA labels where present, and optional component/metrics status.
- **Cleanup:** no cluster resources created. **Stretch:** compare registry and live inventory. **Laptop caveat:** inventory is not proof of regional separation or complete resource usage.

### M14-U1-LAB-05 — Topology decision workshop

- **Goal:** score all six scenarios and write one ADR.
- **Profile:** Fleet-Core. **Clusters:** none required. **Destructive:** no.
- **Start list:** none. **Stop list:** none.
- **Steps:** score criteria in §5.1 for each scenario in §5.2; identify hard constraints; select a topology; record alternatives, evidence, confidence, shared dependencies, owner, and revisit triggers in the ADR template.
- **Expected evidence:** six completed scoring worksheets and one completed ADR with a defensible rationale.
- **Cleanup:** save documents to the learning repository. **Stretch:** ask a reviewer to challenge assumptions. **Laptop caveat:** decision quality comes from evidence, not lab geography.

### M14-U1-LAB-06 — Blast-radius boundary demonstration (optional, destructive)

- **Goal:** understand how a fail-closed admission webhook can disrupt matching API operations in one cluster and why recovery controls matter.
- **Profile:** Fleet-Core, fresh disposable cluster only. **Clusters:** east only; west used for independent read-only comparison. **Destructive:** yes; may disrupt API writes in east.
- **Do not include this lab in the default sequence.** Run only if you can safely recreate east and have read the current Kubernetes admission webhook documentation. `[VERIFY]` exact schema/API behavior. Never run against production or an unspecified context.
- **Preflight:** verify `kind get clusters`; verify east is the disposable lab; record `kubectl --context <east> get nodes`; ensure no valuable state exists; have a second terminal ready for inspection and the exact cluster deletion/recreation command. If any identity is ambiguous, stop.
- **Safer default:** perform a static failure analysis from §7.10 scenario 3. If live experimentation is not well-supported by the installed version or environment, mark it skipped. Do not improvise a fail-closed webhook.
- **Expected evidence:** preflight record, explanation of which operations would match, west read-only query, and recovery/cleanup record. Do not claim a live failure was reproduced unless it actually was.
- **Cleanup:** follow current official docs and your reviewed lab-specific recovery plan. If the disposable cluster is impaired, recreate only `stage2e-east-lab` from its reviewed config after confirming its name; do not delete any other cluster.
- **Laptop caveat:** this demonstrates a cluster-scoped API behavior only; it cannot prove real regional independence.

### M14-U1-LAB-07 — Platform-overhead model

- **Goal:** model fixed overhead as cluster count increases using measured or explicitly synthetic inputs.
- **Profile:** Fleet-Core. **Clusters:** none required after measurement. **Destructive:** no.
- **Start list:** none. **Stop list:** none.
- **Steps:** save `overhead_model.py` from §6.10. Run `python3 overhead_model.py --clusters 1 2 4 8 --system <measured-units> --observability 0 --policy 0`. Replace placeholders with actual non-negative measurements from your environment; do not mix units. Run a sensitivity scenario with a higher per-cluster overhead.
- **Expected evidence:** CSV-like output for cluster counts and notes describing unit definitions and data source.
- **Cleanup:** no resources created. **Stretch:** calculate overhead as a percentage of measured workload capacity. **Laptop caveat:** this is not cloud pricing or a production capacity benchmark.

### M14-U1-LAB-08 — Shared-fate/hidden-dependency review

- **Goal:** identify dependencies shared by both lab clusters and distinguish them from isolated cluster-level components.
- **Profile:** Fleet-Core. **Clusters:** both, plus host/network. **Destructive:** no.
- **Start list:** clusters and optional components only if already available; do not start all optional services just for this lab. **Stop list:** any optional service started only for the exercise.
- **Steps:** create a dependency file based on §7.7; add host OS, Docker daemon, power, disk, Docker network, registry/Git/DNS/MinIO if present; write a script/test that counts dependencies referenced by both clusters; review which failures would affect both.
- **Expected evidence:** dependency graph/list, shared-dependency report, and a written list of what the lab cannot isolate.
- **Cleanup:** stop only optional services started for the exercise. **Stretch:** add owners, timeouts, fallbacks, and failure tests to each dependency. **Laptop caveat:** the common host is an unavoidable shared failure domain.

## 12. Self-check questions

1. **Why is one cluster the default?** — It minimizes duplicated platform and fleet operations until a concrete isolation or availability requirement justifies splitting. *Tempting wrong answer:* “one cluster is always safer”; simplicity is not the same as isolation.
2. **Does a cluster boundary isolate a shared registry outage?** — No, not if both clusters depend on the same registry. *Tempting wrong answer:* separate API servers are mistaken for total independence.
3. **What is the difference between region and cell?** — Region is geographic/provider infrastructure; cell is a service partition designed to bound impact. A cell may span or contain clusters. *Tempting wrong answer:* assuming one cell equals one region.
4. **Does `--context` grant or restrict permissions?** — No; it selects a kubeconfig context. Authorization comes from credentials and server-side policy. *Tempting wrong answer:* confusing target selection with access control.
5. **Why is CIDR non-overlap insufficient for connectivity?** — Routes, firewall rules, CNI/interconnect support, service discovery, and identity are also needed. *Tempting wrong answer:* assuming address uniqueness creates a network path.
6. **Why are two kind clusters not two regions?** — They share the laptop and host-level failure domains and do not model WAN/provider behavior. *Tempting wrong answer:* interpreting labels as infrastructure facts.
7. **What is the primary risk of a fleet-wide hub credential?** — One compromise may alter many clusters. *Tempting wrong answer:* assuming GitOps itself makes changes safe.
8. **What should happen before adding more clusters?** — State the requirement, compare simpler alternatives, model overhead, and verify the team can maintain standards/inventory. *Tempting wrong answer:* treating more clusters as automatically more resilient.
9. **What is a canary cluster for?** — Expose platform/config changes to a bounded, representative target before broader rollout. *Tempting wrong answer:* thinking a canary is useful without promotion gates or evidence.
10. **What is the hard part of splitting a stateful platform?** — Data migration and hidden dependencies, not just deploying manifests. *Tempting wrong answer:* assuming a successful rollout proves data correctness.

## 13. Evidence artifacts

Save the following without credentials, tokens, private keys, or secret values:

- `evidence/lab01-contexts.txt` — actual context names and cluster identity checks.
- `evidence/lab01-cidr-plan.md` — declared and observed CIDR ranges, overlap result, and unresolved network assumptions.
- `evidence/lab01-app-proof.md` — per-cluster deployment verification and east/west response evidence.
- `evidence/kctl-tests.txt` — actual test output if run; otherwise label `not executed`.
- `evidence/registry-validation.txt` — valid and invalid fixture results.
- `evidence/fleet-inventory.json` — output with unknown/optional capabilities preserved honestly.
- `evidence/topology-scores.md` — all six scenarios and the scoring rationale.
- `evidence/adr-001.md` — completed ADR with evidence gaps and revisit triggers.
- `evidence/overhead-model.csv` — measured or explicitly synthetic inputs and results.
- `evidence/shared-fate.md` — dependency graph and the lab fidelity limitations.
- `evidence/cleanup.md` — resources stopped/deleted and verification of cleanup.

## 14. Common interview and design-review questions

1. **When should a team split a Kubernetes cluster?** — When a demonstrated blast-radius, trust/tenancy, residency, latency, scale, ownership, or lifecycle requirement cannot be met acceptably with a simpler boundary. I would record the constraint, compare alternatives, measure fixed overhead, and define revisit triggers.
2. **How do you prove two clusters are operationally independent?** — You cannot prove it from cluster count alone. Map shared host/network/identity/registry/DNS/data/management dependencies, test relevant failure modes, and state residual shared fate. The local kind lab cannot prove regional independence.
3. **What controls prevent wrong-cluster operations?** — Explicit context, target echo, separate credentials, least privilege, guardrails, review, audit, and post-change verification. Context names and wrappers are not authorization boundaries.
4. **How would you choose cell-based architecture?** — Use it when tenant/user partitioning can bound failure impact and the data model supports partitioning. Evaluate routing, cross-cell dependencies, uneven capacity, tenant movement, and shared global dependencies.
5. **What is the trade-off between many small clusters and a few large ones?** — More clusters reduce some shared control-plane blast radii and improve lifecycle independence, but increase fixed overhead, drift, upgrades, network allocation, access paths, and on-call toil. Decide from risk and measured operational capacity.

## 15. What this unit teaches vs. what later units own

- **M03:** cluster architecture, RBAC, version skew, upgrades, and blue/green upgrade concepts are applied at fleet scale; not re-taught from scratch.
- **M04:** CNI/CIDR planning, Services/DNS, Gateway/LB, TLS, mesh basics, and Cilium Cluster Mesh awareness are applied across clusters; cross-cluster discovery mechanics belong to Unit 4.
- **M05:** stateful placement and “compute follows data” are applied; data-platform implementation details remain in that module.
- **M07:** IaC and lifecycle principles are reused; Cluster API lifecycle mechanics are Unit 2.
- **M08:** controller hardening, ApplicationSet basics, repo layout, promotion by digest, drift handling, and evidence are reused; fleet delivery mechanics are Unit 3.
- **M09:** per-cluster identity, secrets, and trust are applied; identity mechanisms are not repeated.
- **M10:** SLO, incident ownership, and toil principles are applied.
- **M11:** `cluster`/`region` labels and inventory dimensions are applied; central multi-cluster observability is Unit 8.
- **M12:** policy and security baselines are applied; multi-cluster policy distribution is Unit 8.
- **M13:** recovery objectives, backup/DR drills, restore verification, and dependency-outage concepts are reused, not re-taught. Steady-state fleet operations are M14’s responsibility.
- **M15:** cross-region transfer, standby capacity cost, and FinOps are forward references.
- **M16:** fleet templates, cluster vending, and service catalog are forward references.
- **M17:** integrated capstone is a forward reference.

## 16. Sources and verification notes

The source files establish the curriculum scope and lab constraints. Live official documentation was **not accessed in this drafting pass**, so the following version-sensitive details remain explicitly unverified and must be checked before running or adopting them:

- **[VERIFY] kind configuration:** exact supported fields and behavior for `networking.podSubnet`, `networking.serviceSubnet`, node roles, and `kind.x-k8s.io` config API version. Official source to consult: kind documentation, “Configuring Your kind Cluster” and cluster creation documentation: https://kind.sigs.k8s.io/docs/user/configuration/ and https://kind.sigs.k8s.io/docs/user/quick-start/.
- **[VERIFY] Kubernetes kubeconfig/context behavior:** consult official Kubernetes documentation “Configure Access to Multiple Clusters” and kubeconfig reference: https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/ and https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/.
- **[VERIFY] Kubernetes scalability:** consult current official Kubernetes scalability guidance for the version and workload shape; do not quote thresholds without reading the current page: https://kubernetes.io/docs/setup/best-practices/cluster-large/.
- **[VERIFY] etcd latency/partition claims:** consult current official etcd operations/performance and Kubernetes control-plane guidance for quorum, latency, and topology; do not use this unit as a numeric latency specification: https://etcd.io/docs/.
- **[VERIFY] Context helper tools:** verify current installation and maintenance status for `kubectx`, `kubens`, and `kube-ps1` before standardizing on them.
- **[VERIFY] Cluster API, Karmada, Open Cluster Management, vcluster, edge distributions, shuffle sharding, and federation projects:** verify current primary project documentation, API versions, and support status before making implementation or adoption decisions. They are awareness references here, not required dependencies.
- **[VERIFY] Sample image:** confirm `hashicorp/http-echo:1.0.0` is available and suitable in the local environment; use an approved tiny local image if registry access is unavailable.
- **[VERIFY] Inventory query compatibility:** validate `kubectl version` JSON output, metrics queries, policy CRD resource names, and permissions against the installed versions. The starter inventory script explicitly treats missing data as unknown.

URLs above are provided as documentation destinations to verify, not as evidence that the pages were opened during this drafting pass. Review exact page contents and release-specific details before production use.

## Appendix A — Runnable lab files

The complete contents of the files referenced in this unit are included in their corresponding sections:

- `app-east.yaml` and `app-west.yaml`: §4.3 (same manifest structure; west changes the echo argument).
- `kind-east.yaml` and `kind-west.yaml`: §5.3 (illustrative and `[VERIFY]`).
- `kctl.py` and `test_kctl.py`: §5.6.
- `clusters.yaml` and `validate_registry.py`: §5.8.
- `fleet_inventory.py`: §5.9; inventory compatibility needs review and mocked tests before use.
- `overhead_model.py`: §6.10.
- Shared-fate dependency data: §7.7.

**Static consistency note:** scripts/configs were reviewed as text for internal intent and safety boundaries; they were not executed in this drafting pass. In particular, validate the exact kind config fields, sample image availability, and all `kubectl` JSON/query behavior against the installed tool versions before running. Do not treat the inventory starter as production-ready without completing its tests.

## Appendix B — Lab execution, cleanup, and recovery reference

Recommended sequence for an 8 GB laptop:

1. Run Lab 01 only; inspect resource use and save outputs.
2. Keep the two clusters for Labs 02–05, which add only small scripts/configs.
3. Do not add GitOps, observability, database replication, DNS simulation, and inter-cluster networking all at once. Start one optional profile only when a later unit requires it, then stop it.
4. Lab 06 is optional and destructive; static analysis is the default. If attempted, use a fresh disposable cluster and a reviewed recovery plan.
5. After labs, verify current clusters and stop/delete only the two named lab clusters if desired. Check `kind get clusters` before any deletion. Do not use a generic command that deletes all kind clusters.

Example cleanup (execute only after checking the names shown by `kind get clusters`):

```bash
kind get clusters
# Only if these are the disposable clusters you intend to remove:
kind delete cluster --name stage2e-east-lab
kind delete cluster --name stage2e-west-lab
kind get clusters
```

`kind delete cluster` is not a kubectl mutation and has no `--context` flag; safety comes from confirming the exact disposable cluster names before invoking it. Verify no other cluster is selected for deletion. Local image/container cleanup should be performed only after checking what else uses the Docker daemon.

## Appendix C — Traceable requirement audit

| Requirement group | Coverage location | Status |
|---|---|---|
| One-cluster default; boundary benefits/costs; vocabulary | §§3.2–3.4 | PASS (concept coverage) |
| All required topology types and comparison | §3.5 | PASS |
| Anti-patterns: stretched, snowflakes, per-microservice, federation, shared hub | §3.6, §5.12 | PASS; stretched-cluster claims remain [VERIFY] |
| Context/kubeconfig safety and wrong-cluster discipline | §§4.1, 5.5–5.7 | PASS (guard is defense-in-depth only) |
| Exact lab names and cluster-identifying app | §§4.2–4.3, Lab 01 | PASS; kind context string must be discovered/verified |
| Scoring framework and six scenarios | §§5.1–5.2 | PASS |
| CIDR overlap risk, distinct plan, kind fields | §5.3, Lab 01 | PARTIAL until current kind fields and local ranges are verified |
| Registry metadata and validator | §5.4, §5.8, Lab 03 | PASS for declared-data validation; live drift not covered |
| Kubeconfig hygiene/access patterns | §5.5 | PASS |
| `kctl` behavior and tests | §5.6, Lab 02 | PARTIAL: static only; execute tests and review verb-classification limitations |
| Inventory and tests | §5.9, Lab 04 | PARTIAL: starter code needs mocked tests and version-specific query corrections |
| ADR and revisit triggers | §5.10, Lab 05 | PASS |
| Blast radius, tiered fleets, canaries/rings | §§6.1–6.3 | PASS |
| Regional placement and data gravity | §6.4 | PASS |
| Cell-based design and limitations | §6.5 | PASS; shuffle-sharding details [VERIFY] |
| Hub risks and outage semantics | §6.6 | PASS (implementation-dependent behavior qualified) |
| Shared services/dependency direction | §6.7 | PASS |
| Capacity, N+1, scalability source | §6.8–6.9, §16 | PARTIAL until current thresholds guidance is reviewed |
| Measured overhead and sensitivity | §6.10, Lab 07 | PASS for simple model; requires measured inputs |
| Multi-tenancy alternatives | §6.11 | PASS; vcluster status [VERIFY] |
| Lifecycle/inventory automation | §6.12, §7.3–7.4 | PASS |
| Governance, vending, sprawl, toil | §§7.1–7.4 | PASS |
| Split/merge playbooks | §§7.5–7.6 | PASS |
| Shared-fate dependency analysis | §7.7, Lab 08 | PARTIAL until runnable analyzer/tests are added |
| Security topology/hub compromise | §7.8, §9 | PASS |
| Edge/hybrid/multi-cloud awareness | §7.9 | PASS; distribution/project status [VERIFY] |
| Eight incident analyses | §7.10 | PASS (hypothetical, no fabricated incident metrics) |
| SRE/security lenses, checklists, labs, questions, evidence, interview answers | §§8–14 | PASS, with lab execution outstanding |
| Cross-module boundaries and forward references | §15 | PASS |
| Sources and truthful verification statement | §16 and this appendix | PASS for transparent uncertainty; no live source verification claimed |

## Appendix D — Known limitations and open verification items

1. **OPEN:** This document was statically reviewed, not executed. All scripts and tests must be run in the learner’s environment before being treated as runnable evidence.
2. **OPEN:** Verify current kind config schema and actual local network ranges before creating clusters with custom pod/service CIDRs.
3. **OPEN:** `kctl.py` recognizes a list of high-impact verbs but cannot classify every possible Kubernetes mutation. Keep the allow-list lab-only and use server-side authorization.
4. **OPEN:** `fleet_inventory.py` needs compatibility corrections and mocked tests for version output, metrics output, and optional policy resources. Missing data must remain unknown rather than be treated as zero.
5. **OPEN:** The shared-fate analyzer is specified as a lab deliverable but a complete runnable analyzer/test file is not included in this version; Lab 08 currently provides the dependency data and implementation goal. Do not mark that script as completed.
6. **OPEN:** The optional fail-closed webhook live lab is intentionally not a copy-paste manifest. Verify current schema and design a recovery-tested disposable-only exercise before attempting it; static analysis is the safe default.
7. **OPEN:** Official documentation URLs are listed as verification destinations, but live pages were not accessed in this drafting pass. Review the current kind, Kubernetes, etcd, and awareness-tool documentation before production decisions.
8. **OPEN:** The two-cluster lab cannot prove regional independence, WAN behavior, global DNS/load-balancer failover, provider fault-domain separation, or production capacity.

**Truthful verification statement:** The document was statically reviewed for scope, terminology, lab safety, and consistency. Code and commands were **not executed**. Current official documentation was **not accessed** in this drafting pass; the version-sensitive items listed above remain `[VERIFY]`. AI self-review does not replace a human running the labs against installed versions, reviewing failure recovery, and validating the design for the target production environment.

### Appendix A.1 — Full sample app manifests

`app-east.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-identity
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-identity
  template:
    metadata:
      labels:
        app: cluster-identity
    spec:
      containers:
        - name: web
          image: hashicorp/http-echo:1.0.0
          args: ["-text=east-lab"]
          ports:
            - name: http
              containerPort: 5678
          resources:
            requests:
              cpu: 10m
              memory: 16Mi
            limits:
              cpu: 100m
              memory: 64Mi
---
apiVersion: v1
kind: Service
metadata:
  name: cluster-identity
  namespace: default
spec:
  selector:
    app: cluster-identity
  ports:
    - name: http
      port: 80
      targetPort: http
```

`app-west.yaml` (only the response body differs):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-identity
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-identity
  template:
    metadata:
      labels:
        app: cluster-identity
    spec:
      containers:
        - name: web
          image: hashicorp/http-echo:1.0.0
          args: ["-text=west-lab"]
          ports:
            - name: http
              containerPort: 5678
          resources:
            requests:
              cpu: 10m
              memory: 16Mi
            limits:
              cpu: 100m
              memory: 64Mi
---
apiVersion: v1
kind: Service
metadata:
  name: cluster-identity
  namespace: default
spec:
  selector:
    app: cluster-identity
  ports:
    - name: http
      port: 80
      targetPort: http
```

### Appendix A.2 — Shared-dependency analyzer and tests

Save the dependency data from §7.7 as `shared-dependencies.yaml`, then save the following as `shared_fate.py`. This intentionally analyzes only declared dependencies; it does not probe actual network paths or prove independent failure domains.

```python
#!/usr/bin/env python3
from __future__ import annotations
import sys
import yaml


def shared_dependencies(document):
    clusters = document.get("clusters") if isinstance(document, dict) else None
    if not isinstance(clusters, dict):
        raise ValueError("top-level 'clusters' must be a mapping")
    users = {}
    for cluster, entry in clusters.items():
        if not isinstance(entry, dict):
            raise ValueError(f"cluster {cluster!r} must map to an object")
        deps = entry.get("shared_dependencies", []) + entry.get("optional_dependencies", [])
        if not isinstance(deps, list) or not all(isinstance(dep, str) and dep for dep in deps):
            raise ValueError(f"cluster {cluster!r} dependencies must be non-empty strings")
        for dep in set(deps):
            users.setdefault(dep, []).append(cluster)
    return {dep: sorted(names) for dep, names in sorted(users.items()) if len(names) > 1}


def main(path):
    try:
        with open(path, encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
        shared = shared_dependencies(document)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not shared:
        print("No shared dependencies declared; this is not proof of independence.")
        return 0
    for dep, clusters in shared.items():
        print(f"SHARED: {dep}: {', '.join(clusters)}")
    print("Declared-dependency analysis only; verify actual runtime paths and host-level shared fate.")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: shared_fate.py shared-dependencies.yaml", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
```

Save `test_shared_fate.py`:

```python
import unittest
from shared_fate import shared_dependencies

class SharedFateTests(unittest.TestCase):
    def test_finds_dependency_used_by_both_clusters(self):
        doc = {"clusters": {
            "east": {"shared_dependencies": ["host", "docker"], "optional_dependencies": ["registry"]},
            "west": {"shared_dependencies": ["host"], "optional_dependencies": ["registry"]},
        }}
        self.assertEqual(shared_dependencies(doc), {"host": ["east", "west"], "registry": ["east", "west"]})

    def test_deduplicates_dependency_within_one_cluster(self):
        doc = {"clusters": {
            "east": {"shared_dependencies": ["host", "host"]},
            "west": {"shared_dependencies": ["host"]},
        }}
        self.assertEqual(shared_dependencies(doc), {"host": ["east", "west"]})

    def test_rejects_invalid_top_level(self):
        with self.assertRaises(ValueError):
            shared_dependencies({"clusters": []})

    def test_rejects_invalid_dependency(self):
        with self.assertRaises(ValueError):
            shared_dependencies({"clusters": {"east": {"shared_dependencies": [""]}}})

if __name__ == "__main__":
    unittest.main()
```

Run `python3 -m unittest -v test_shared_fate.py` and `python3 shared_fate.py shared-dependencies.yaml` after installing PyYAML in an isolated environment. Tests have not been executed as part of this document generation.

### Appendix A.3 — Registry validator tests

Save `test_validate_registry.py`:

```python
import copy
import unittest
from validate_registry import validate

VALID = {"clusters": [
    {"name": "east", "context": "kind-east", "environment": "lab", "region": "simulated-east", "owner": "platform-learning", "tier": "lab", "kubernetes_version": "unknown", "creation_source": "kind-config", "lifecycle_state": "active", "pod_cidr": "10.240.0.0/16", "service_cidr": "10.96.0.0/16", "credential_type": "local-kind-admin-lab-only"},
    {"name": "west", "context": "kind-west", "environment": "lab", "region": "simulated-west", "owner": "platform-learning", "tier": "lab", "kubernetes_version": "unknown", "creation_source": "kind-config", "lifecycle_state": "active", "pod_cidr": "10.241.0.0/16", "service_cidr": "10.97.0.0/16", "credential_type": "local-kind-admin-lab-only"},
]}

class RegistryTests(unittest.TestCase):
    def test_valid_registry(self):
        self.assertEqual(validate(copy.deepcopy(VALID)), [])

    def test_missing_owner(self):
        doc = copy.deepcopy(VALID)
        del doc["clusters"][0]["owner"]
        self.assertTrue(any("missing fields" in e for e in validate(doc)))

    def test_duplicate_name(self):
        doc = copy.deepcopy(VALID)
        doc["clusters"][1]["name"] = "east"
        self.assertTrue(any("duplicate cluster name" in e for e in validate(doc)))

    def test_overlapping_cidr(self):
        doc = copy.deepcopy(VALID)
        doc["clusters"][1]["pod_cidr"] = "10.240.0.0/17"
        self.assertTrue(any("CIDR overlap" in e for e in validate(doc)))

    def test_invalid_tier(self):
        doc = copy.deepcopy(VALID)
        doc["clusters"][0]["tier"] = "magic"
        self.assertTrue(any("invalid tier" in e for e in validate(doc)))

if __name__ == "__main__":
    unittest.main()
```

### Appendix A.4 — Inventory test strategy

Before adopting `fleet_inventory.py`, refactor its `run()` function to accept an injected runner and add mocked tests for: explicit `--context` in every invocation; API unreachable; invalid JSON; empty node list; missing CRDs; missing metrics API; absent policy CRDs; and permission-denied responses. A compatibility issue remains in the current starter: `kubectl top nodes` output is commonly tabular and may not support JSON output as written. Treat the metrics field as unknown until that query is corrected and tested for the installed client. **This is an open implementation item, not a completed test suite.**
