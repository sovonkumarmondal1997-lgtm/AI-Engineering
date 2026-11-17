# Local Lab: kind, minikube and LocalStack — Stage 2E

> A zero-budget, repeatable local lab for learning Kubernetes mechanics and AWS API workflows while explicitly documenting where local behaviour diverges from production.

**Estimated time:** 6–10 hours for the first working setup; additional time for recipes and troubleshooting  
**Prerequisite:** `lab-environment-setup.md` complete (run `lab-doctor.sh` if it exists in that file)  
**Last reviewed:** 2026-10-24  
**Versions:** Check upstream at install time; record the exact versions and image tags used in your lab.

---

## 1. Purpose, scope, and the "local lab lies" principle

This guide uses kind as the primary local Kubernetes environment, minikube as a secondary alternative, and LocalStack for selected AWS API exercises. It assumes the base tools are already installed; it is not another installation guide. Use the sibling [lab-environment-setup.md](lab-environment-setup.md) for host setup and [production-devops-tooling-map.md](production-devops-tooling-map.md) for tool selection. Use [free-tier-cloud-account-and-cost-safety.md](free-tier-cloud-account-and-cost-safety.md) before any real-cloud exercise. A local lab is excellent for learning manifests, rollout mechanics, image workflows, Terraform state, and repeatable automation. It does not reproduce a production control plane, physical network, cloud IAM engine, multi-AZ topology, quota system, or billing behaviour. A senior operator does not merely know how to run a command; they can state what the experiment did and did not prove. For every exercise, keep a short note called **What this lab hid from me**.

**Core:** kind, Docker, `kubectl`, Git, and a reproducible config directory.  
**Optional:** minikube, LocalStack, Helm, Terraform/OpenTofu, policy-enforcing CNI, metrics-server, and observability/security tools when a recipe needs them.

---

## 2. Choosing your environment (decision table)

| Need | kind | minikube | LocalStack | Real free tier |
|---|---|---|---|---|
| Speed of create/destroy | Usually fast; nodes are containers | Depends on driver and profile | Container start/stop is usually quick | Provisioning and deletion are service-dependent |
| Multi-node clusters | Good fit; configure control-plane and worker node containers | Supported; topology depends on driver and configuration | Not a Kubernetes cluster | Multiple nodes/services are real but can incur cost |
| CI-friendliness | Strong fit for ephemeral Kubernetes tests | Possible; runner and driver matter | Useful for selected AWS API integration tests | Usually slower and needs account/network controls |
| Add-ons convenience | Install components explicitly | Convenient add-on workflow | Not applicable | Managed services have their own setup |
| GPU/driver options awareness | Not a GPU-learning environment by default | Some driver and GPU paths exist; platform-dependent `[VERIFY]` | Not applicable | Depends on service, region, quota, and cost |
| AWS API practice | Not its purpose | Not its purpose | Useful for supported APIs; fidelity varies | Real API behaviour |
| IAM realism | No cloud IAM engine | No cloud IAM engine | Partial/simplified behaviour; verify feature coverage | Real AWS IAM evaluation |
| Networking realism | Container network and local host paths; not a production network | Driver-dependent local networking | Emulated endpoints, not real VPC semantics | Real cloud network controls and constraints |
| Cost | No cloud charge; consumes local resources | No cloud charge; consumes local resources | Community/free scope only; check current terms | May be free within current limits; accidental spend is possible |
| Storage realism | Local container/host-backed behaviour; not production CSI | Driver/storage implementation differs from production | Not applicable | Real service/storage classes and managed-service behaviour |
| Best use in this stage | Repeatable cluster and CI-style exercises | Add-on convenience and learning minikube itself | AWS API and Terraform integration exercises | Only for explicitly planned exercises with guardrails |

**Default recommendation:** use **kind as the primary Kubernetes lab** because its container-node model is convenient for repeatable, multi-node, short-lived clusters and CI-style practice. Use minikube when its add-ons, profile workflow, or driver-specific experience is the learning objective. Use LocalStack only for APIs it currently supports in the free/community scope. Use a real free tier only when the learning objective depends on actual AWS behaviour and the cost-safety guide has been followed.

**Core decision rule:** choose the environment that can test the hypothesis with the least risk and least hidden complexity. Do not use a local result as proof of cloud correctness.

---

## 3. Lab architecture overview

The sketch below shows the intended traffic paths. The exact hostnames and network reachability depend on Docker, WSL2, and the chosen configuration.

```text
Windows host
└── WSL2 Ubuntu shell
    ├── kubectl / Helm / Kustomize
    │      │ Kubernetes API
    │      ▼
    │   kind cluster(s)
    │   ├── control-plane node container
    │   ├── worker node container(s)
    │   └── application pods / ingress controller
    │
    ├── Docker CLI ───────────────► Docker daemon
    │                                  ├── kind node containers
    │                                  ├── local registry container
    │                                  └── LocalStack container
    │
    ├── build tool ──push/pull────► local registry
    ├── Terraform/OpenTofu ───────► LocalStack endpoint
    └── AWS CLI / awslocal ───────► LocalStack endpoint
```

Do not assume that `localhost` inside a pod, inside a kind node, inside WSL2, and inside Windows means the same endpoint. It refers to the network namespace in which the command runs. A port published to the WSL2 host is not automatically reachable from every container or from Windows in every setup. When a pod must call LocalStack, test the route from the pod's network context and use a deliberate, documented address. Never solve a connectivity problem by replacing a local endpoint with a real AWS endpoint.

**Core layout suggestion:**

```text
stage-2e-labs/
├── kind/
│   ├── kind-single.yaml
│   ├── kind-three-node.yaml
│   └── ingress/
├── apps/
│   ├── demo/
│   └── network-policy/
├── registry/
├── localstack/
│   └── compose.yaml
├── terraform/
│   └── localstack-s3/
├── scripts/
└── notes/
    └── what-this-lab-hid-from-me.md
```

This is a **proposed convention**, not an existing roadmap path. Keep your actual repository naming consistent with the sibling setup guide.

---

## 4. Part 1 — kind (primary)

### 4.1 What kind is and what that implies

kind runs Kubernetes nodes as containers. The cluster is real enough to exercise many Kubernetes APIs and workflows, but each node is a container rather than a separate physical or virtual machine. That makes cluster creation and deletion convenient and supports multi-node topologies on a laptop. It also means kernel, storage, networking, node failure, and resource isolation do not match a production fleet. A worker container is not an independent physical failure domain. A multi-node kind cluster can test scheduling and rollout mechanics; it cannot prove resilience across availability zones.

**Core:** maintain cluster configuration in Git and recreate the cluster rather than relying on undocumented manual changes.  
**Optional:** use separate clusters for isolated exercises, but remember that every cluster adds resource overhead.

### 4.2 Check versions before creating a cluster

Run these commands in **WSL2 Ubuntu**, not PowerShell:

```bash
kind version
kubectl version --client
docker version
docker info
```

Each command reports a tool version or daemon details. `docker info` must be able to reach the intended Docker daemon. If any command fails, stop and fix the base environment using `lab-environment-setup.md`. Do not copy a node image tag from an old tutorial and assume it is still supported.

To inspect current releases, use the official kind releases/docs and Kubernetes version-skew policy. Supported combinations change. **[VERIFY]** Record the exact versions that worked:

```bash
mkdir -p notes
{
  date -Is
  kind version
  kubectl version --client
  docker version --format '{{.Client.Version}}'
} > notes/versions.txt
```

This records a local snapshot; it does not guarantee that the versions remain supported indefinitely.

### 4.3 Create a single-node cluster

**Core.** First inspect existing clusters:

```bash
kind get clusters
kubectl config get-contexts
```

If a cluster name already exists, do not blindly create another cluster with the same name. Choose a unique name or intentionally reuse the existing cluster. Create a simple cluster:

```bash
kind create cluster --name stage2e-dev
```

The command creates a local cluster and normally configures a kubeconfig context named for the cluster. Expected result: the command completes and prints connection instructions. Verify the current context and node:

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl cluster-info
```

Expected result: the current context corresponds to the intended cluster and the node eventually reports `Ready`. If the context is unexpected, do not apply manifests or delete anything until it is corrected.

### 4.4 Create a three-node cluster from a config file

Use a config file so the topology is reviewable and reproducible. The following is a minimal kind cluster configuration using the documented `kind` API shape; confirm it against the current kind configuration docs before relying on it. **[VERIFY]**

Save as `kind/kind-three-node.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: stage2e-multi
nodes:
  - role: control-plane
    image: kindest/node:<NODE_IMAGE_TAG>
  - role: worker
    image: kindest/node:<NODE_IMAGE_TAG>
  - role: worker
    image: kindest/node:<NODE_IMAGE_TAG>
```

Replace `<NODE_IMAGE_TAG>` with an actual supported tag before running the command. Angle-bracket placeholders are not valid image tags. The kind node image must match the Kubernetes version you intend to test. Check supported images and releases on the kind release page. **[VERIFY]** Pinning the tag makes the topology more reproducible; it does not remove the need to update security fixes deliberately.

Before creating, inspect current clusters and choose a unique name:

```bash
kind get clusters
```

Create the cluster:

```bash
kind create cluster --config kind/kind-three-node.yaml
```

Verify:

```bash
kubectl config get-contexts
kubectl config use-context kind-stage2e-multi
kubectl get nodes -o wide
```

Expected result: one control-plane node and two worker nodes eventually report `Ready`. If the context name differs, use the actual name shown by `kubectl config get-contexts`; do not guess.

**Cleanup warning:** deleting a cluster permanently removes its local cluster state and workloads. First confirm the exact cluster name:

```bash
kind get clusters
kubectl config get-contexts
```

Then delete only the intended lab cluster:

```bash
kind delete cluster --name stage2e-multi
```

Do not run a deletion command with an empty, substituted, or ambiguous cluster name.

### 4.5 Expose ingress ports and install an ingress controller

kind can map ports from the host to a node container through `extraPortMappings`. This is a port-forwarding arrangement, not a cloud load balancer. A cluster config with mappings must be applied when the cluster is created. Do not assume the mapping can be retrofitted to an existing cluster.

Example fragment for a cluster config:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: stage2e-ingress
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 80
        hostPort: 8080
        protocol: TCP
      - containerPort: 443
        hostPort: 8443
        protocol: TCP
  - role: worker
  - role: worker
```

This fragment maps host ports to ports on the control-plane node. An ingress controller must actually listen on the mapped node ports for traffic to flow. Follow the ingress controller's official kind-specific installation instructions; do not assume every controller uses host ports the same way. **[VERIFY]**

**Core workflow:**
1. Create the cluster from the reviewed config.
2. Install a maintained ingress controller using its official instructions.
3. Wait for its pods to become ready.
4. Create an application Service and Ingress resource compatible with that controller.
5. Test the host mapping using `curl` against the documented local port.
6. Record the controller version, manifest source, and any patch applied.

Example inspection commands:

```bash
kubectl get pods -A
kubectl get svc -A
kubectl get ingress -A
```

Expected result: the controller pods are ready and the Ingress resource is accepted by the controller. An Ingress object alone does not install a controller.

### 4.6 Local container registry attached to kind

A local registry allows images to be pushed and pulled through a registry endpoint. The documented kind local-registry pattern configures a registry container and makes it reachable from the kind node network. Follow the current kind documentation for the complete setup; the exact container network and configuration are environment-dependent. **[VERIFY]**

A registry setup typically requires:
- a registry container;
- a network path from kind nodes to the registry;
- a registry name/address that pods can resolve;
- kind node configuration that treats the registry as a mirror or otherwise trusts the intended endpoint, as required by the documented pattern;
- image references in manifests that match the registry path.

Do not invent a registry address from an example on the internet and assume it works on WSL2. Verify registry connectivity from both the WSL2 shell and a kind node/container when the workflow requires it.

**Alternative: `kind load docker-image`.** For a small exercise, load an image already present in the local Docker daemon directly into a kind cluster:

```bash
docker build -t demo-web:dev ./apps/demo
kind load docker-image demo-web:dev --name stage2e-dev
```

The build command assumes `./apps/demo` contains a valid Docker build context. If it does not, use your actual application directory. Expected result: Docker builds the image and kind loads it into the named cluster. Use an image reference such as `demo-web:dev` in the workload and avoid an image-pull policy that forces an unavailable registry pull.

| Approach | Benefits | Trade-offs | Best use |
|---|---|---|---|
| Local registry | Closer to a push/pull workflow; reusable across clusters when networking is correct | More setup; DNS, trust, and port mapping can be tricky | CI, multi-cluster, registry exercises |
| `kind load docker-image` | Simple; no registry service required | Image is loaded into a particular cluster; not a registry workflow | Quick app iteration and small labs |

### 4.7 NetworkPolicy practice requires a policy-enforcing CNI

Kubernetes NetworkPolicy resources describe intended pod traffic rules, but the network plugin must enforce them. The default kind networking setup does not enforce NetworkPolicy in the way required for this exercise. **[VERIFY against kind docs and the selected CNI docs]** Installing a policy-enforcing CNI is therefore a prerequisite for the deny-by-default recipe. Named options to investigate include Calico and Cilium; do not install either using a random copied manifest. Choose one supported installation path compatible with the Kubernetes version and kind topology, and follow its official documentation. **[VERIFY]**

**Core procedure:**
1. Create a disposable cluster specifically for the policy exercise.
2. Install the selected CNI using the official kind-compatible instructions.
3. Verify that the CNI pods are ready.
4. Deploy a client pod and a target Service/pod.
5. Prove connectivity before applying policy.
6. Apply a default-deny policy in the intended namespace.
7. Prove that the expected traffic is blocked.
8. Add a narrow allow policy and prove the intended traffic succeeds.
9. Save the before/after commands and observations.

Do not treat a failed connection as proof of policy enforcement until you have confirmed the pods were healthy and the baseline connection worked. A CNI change can disrupt the cluster. Use a disposable cluster and document the exact installation version.

### 4.8 Metrics with metrics-server

metrics-server provides resource metrics used by commands such as `kubectl top`, but it is not a full observability stack. Install it only by following the official metrics-server instructions appropriate to your cluster. In local clusters, kubelet certificate and address behaviour can create TLS errors; do not reflexively disable certificate verification. The exact workaround, if any, must come from the official documentation and be explicitly labelled as a local-only compromise. **[VERIFY]**

Verify:

```bash
kubectl get deployment -n kube-system metrics-server
kubectl top nodes
kubectl top pods -A
```

Expected result: after startup and metrics collection, `kubectl top` returns resource usage. Initial requests may fail while metrics are not yet available. If it fails, inspect logs and events before changing security settings:

```bash
kubectl logs -n kube-system deployment/metrics-server
kubectl get events -A --sort-by=.lastTimestamp
```

### 4.9 Multiple kind clusters side by side

Multiple clusters are useful for comparing versions, rehearsing GitOps patterns, or simulating two regions. They share laptop CPU, memory, disk, Docker, and often network resources. Use explicit names such as `stage2e-east-lab` and `stage2e-west-lab`; these are labels for the exercise, not real regions. Each cluster has a context. Confirm the target before every apply, rollout, or deletion.

```bash
kind get clusters
kubectl config get-contexts
kubectl config current-context
```

Switch intentionally:

```bash
kubectl config use-context kind-stage2e-east-lab
kubectl config current-context
```

Do not run a destructive command merely because the context name looks familiar. For multi-cluster work, keep a written mapping of cluster name, context name, intended purpose, and node image tag. Limit concurrent clusters to what your machine can support. Delete idle clusters only after checking their names and confirming that no work needs to be retained.

### 4.10 Snapshot and reset strategy

Treat config files, manifests, and scripts as the source of truth. Local cluster state is disposable. For a clean reset, first list clusters and contexts:

```bash
kind get clusters
kubectl config get-contexts
```

**Warning:** deleting a cluster destroys its local workloads, in-cluster state, and ephemeral data. Confirm the exact name before proceeding.

```bash
kind delete cluster --name stage2e-dev
```

Recreate from the saved config or the documented simple command, then redeploy from Git. Do not use Docker-wide prune commands as a routine cluster reset; they may remove images, caches, volumes, or resources used by unrelated projects. For a reset script, require the cluster name as an explicit argument, print the target, and ask for confirmation before deleting. Avoid a script that deletes every kind cluster by default.

### 4.11 kind limitations

- **LoadBalancer:** a Service of type `LoadBalancer` does not automatically receive a production cloud load balancer. Local helper options include MetalLB or `cloud-provider-kind`; support and setup differ. **[VERIFY]**
- **Storage:** local paths and container-backed volumes do not model production CSI drivers, cloud block storage, failure zones, or managed storage operations.
- **CNI:** policy enforcement depends on the selected CNI; the default kind network is not a NetworkPolicy test environment. **[VERIFY]**
- **Node lifecycle:** nodes are containers, not independent machines; a node restart is not equivalent to a host or availability-zone failure.
- **Ingress:** host-port mappings and local DNS are not equivalent to a managed cloud ingress/load-balancing path.
- **Security:** a local cluster does not prove production RBAC, identity integration, node hardening, admission policy, or network segmentation.
- **Scale:** laptop scheduling and resource pressure do not predict production capacity.
- **Failure domains:** a single laptop cannot demonstrate genuine multi-AZ or multi-region failure behaviour; those are simulated.

**Verify**
- `kind get clusters` shows only the intended clusters.
- `kubectl config current-context` points to the target.
- All nodes report `Ready`.
- Configs and image tags are committed to Git.

**Cleanup**
- Inspect cluster names and contexts first.
- Delete only the named disposable cluster.
- Avoid Docker-wide pruning unless you have reviewed exactly what it will remove.

**Fidelity caveat:** kind is excellent for Kubernetes mechanics and reproducible workflows, not proof of production infrastructure fidelity.

---

## 5. Part 2 — minikube (secondary, alternative)

### 5.1 When to use minikube

minikube runs a local Kubernetes cluster and offers driver choices, profiles, and convenient add-ons. Use it when the learning objective is minikube itself, when an official add-on simplifies a lab, or when its driver-specific behaviour is relevant. For this roadmap, use the Docker driver as the first option to investigate on WSL2, subject to the current minikube documentation and your Docker setup. **[VERIFY]** Do not assume a VM driver, nested virtualization, GPU path, or Windows/WSL2 networking behaviour is available on every machine.

### 5.2 Check version and driver readiness

Run in **WSL2 Ubuntu**:

```bash
minikube version
docker info
minikube profile list
```

If `minikube profile list` reports no profiles or a different output shape, follow the current command help. Do not infer that a profile exists. Check the current minikube docs for supported drivers and WSL2-specific caveats before creating a cluster. **[VERIFY]**

### 5.3 Start a profile

**Core example; check current flags with `minikube start --help` first.**

```bash
minikube start --profile stage2e-minikube --driver=docker
```

This asks minikube to create a profile using the Docker driver. Expected result: the cluster starts and its context is configured. Verify:

```bash
minikube profile list
kubectl config get-contexts
kubectl config current-context
kubectl get nodes -o wide
```

If you have a separate kind cluster, be deliberate about the active context. The `kubectl` CLI uses its current context unless you explicitly pass another context.

### 5.4 Resource flags and profiles

minikube exposes CPU and memory controls, but the exact supported flags and defaults can change. Check `minikube start --help` before using `--cpus` or `--memory`. **[VERIFY]** Choose conservative resource allocations and leave capacity for Windows, WSL2, Docker, your editor, and other workloads. A second profile consumes additional resources even if its workloads are idle.

Example with flags only after checking current help:

```bash
minikube start --profile stage2e-small --driver=docker --cpus=<CPU_COUNT> --memory=<MEMORY_MB>
```

Replace placeholders with valid values; do not paste the angle-bracket placeholders literally. If the command rejects a flag or value, stop and consult the installed version's help rather than trying random flags.

### 5.5 Add-ons

minikube provides an add-on workflow. List available add-ons before enabling one:

```bash
minikube addons list --profile stage2e-minikube
```

Enable only the add-on needed for the exercise, using the current official add-on name and documented command. **[VERIFY]** An add-on name or default may change between versions. Verify the resulting pods and resources:

```bash
kubectl get pods -A
kubectl get svc -A
```

Do not enable every add-on just because it is available. Extra components consume resources and can complicate diagnosis.

### 5.6 Load local images

Use minikube's image-loading workflow when the image is built in the local Docker environment and is not in a remote registry:

```bash
docker build -t demo-web:dev ./apps/demo
minikube image load demo-web:dev --profile stage2e-minikube
```

The build path must exist and contain a valid Dockerfile. Expected result: the image is available to workloads in the named minikube profile. Use an image reference and pull policy consistent with the local image workflow; otherwise Kubernetes may try to pull from a remote registry.

### 5.7 LoadBalancer and `minikube tunnel`

minikube documents `minikube tunnel` as a way to support local LoadBalancer service behaviour for supported configurations. It may require elevated privileges or host networking changes depending on the platform. **[VERIFY]** Read the official instructions before running it. Do not run it as an unattended background process without understanding how to stop it and undo host-side changes. In a separate terminal, inspect the Service:

```bash
kubectl get svc -A
```

A pending external address by itself is not proof of a cluster failure; it may mean the environment lacks a load-balancer implementation. Do not compare the result directly with a managed cloud load balancer.

### 5.8 WSL2 pitfalls

- The Docker daemon must be reachable from the WSL2 shell.
- Driver support and resource requirements vary by installed minikube version.
- Host-to-cluster access can differ from Windows-native instructions.
- A profile can remain after a terminal closes.
- A cluster can consume disk even when no application is running.
- Add-ons can create ports, services, and resources that affect later exercises.
- A running tunnel may alter local routing; stop it deliberately.
- Do not use `sudo` as a generic fix for every driver error; inspect the actual error first.

**Verify**
- `minikube profile list` identifies the intended profile.
- The current `kubectl` context is correct.
- Nodes are `Ready`.
- Only the add-ons needed for the current exercise are enabled.

**Cleanup**

**Warning:** deleting a profile removes its local cluster and workloads. Inspect profiles first:

```bash
minikube profile list
kubectl config get-contexts
```

Then delete only the named profile after confirming it is disposable:

```bash
minikube delete --profile stage2e-minikube
```

**Fidelity caveat:** minikube is a local learning cluster. Driver, add-on, storage, and network behaviours do not establish how a production managed Kubernetes service will behave.

---

## 6. Part 3 — LocalStack

### 6.1 What LocalStack is — and what it is not

LocalStack emulates selected AWS service APIs locally so developers can test some application and infrastructure workflows without provisioning those resources in AWS. It is not AWS running on your laptop. Service coverage, API operations, IAM semantics, persistence, and feature availability vary by service and product tier. The free/community coverage and current service matrix can change; check the official LocalStack docs and current pricing/feature documentation before designing an exercise. **[VERIFY]** This guide must not rely on a paid feature. If a needed capability is paid or unavailable in the free scope, mark the exercise conceptual or use a different free local approach.

### 6.2 Service coverage and conservative fidelity ratings

The following are **provisional learning ratings**, not a claim that every API operation is available in the current free tier. Verify service coverage and feature access before using a recipe. **[VERIFY]**

| AWS service or capability | Intended exercise | Provisional fidelity | Qualification |
|---|---|---|---|
| S3 | Create/list/delete a test bucket through CLI and Terraform | Medium | API coverage and edge cases differ from AWS |
| SQS | Basic queue operations if currently available in free scope | Medium/Conceptual | Confirm operations and free-tier coverage |
| SNS | Basic topic/subscription operations if currently available | Medium/Conceptual | Delivery and integration behaviour may differ |
| DynamoDB | Basic table/item workflow if supported in current free scope | Medium/Conceptual | Throughput, consistency, and edge cases are not production proof |
| Lambda | Basic packaging/invocation only if supported in current free scope | Low/Conceptual | Runtime and event-source behaviour may differ |
| IAM | Basic policy/configuration exploration only where supported | Low | Never use this to prove real AWS IAM evaluation |
| VPC/networking | Conceptual API shape only | Low/Conceptual | Does not reproduce real VPC dataplane, routing, or security-group behaviour |
| CloudWatch | Basic API workflow if supported | Low/Conceptual | Not a substitute for production metrics, alarms, or service integration testing |
| ECR | Registry workflow only if currently supported and available | Low/Conceptual | Prefer a local OCI registry for image-push learning |
| Other AWS APIs | Only after checking current service matrix | Conceptual until verified | Do not assume service support based on an SDK containing an API |

For this stage, the core LocalStack recipe uses S3 because it is a compact way to practise endpoint overrides, CLI requests, Terraform state, and drift detection. Verify the current free/community coverage first. Do not make a claim that LocalStack's service coverage is complete or production-equivalent.

### 6.3 Start LocalStack safely

Choose either the official LocalStack Docker/Compose instructions or a reviewed Compose file. Do not copy a stale image tag or unverified environment variable from a tutorial. The exact image, ports, health endpoint, environment variables, persistence settings, and free-tier behaviour must be checked against the current LocalStack docs. **[VERIFY]**

A conceptual Compose pattern is shown below. Treat the image and configuration as placeholders until checked against official documentation; do not run the file as-is.

```yaml
services:
  localstack:
    image: localstack/localstack:<LOCALSTACK_IMAGE_TAG>
    ports:
      - "127.0.0.1:4566:4566"
```

This illustrates binding the common edge endpoint to loopback, not a complete production Compose file. Replace the placeholder with a current tag and add only documented settings required by the exercise. Do not publish a local emulator broadly on your network without understanding the exposure.

Start it from the directory containing the reviewed Compose file:

```bash
docker compose up -d
docker compose ps
docker compose logs --tail=100 localstack
```

Expected result: the container is running and logs do not show a fatal startup error. Check the official health-check endpoint and response shape before using a health command. **[VERIFY]** A container being “running” does not prove all target services are ready.

### 6.4 Dummy credentials and explicit endpoints

For emulator-only exercises, use dummy credentials and an explicit endpoint override. Never leave a real AWS profile active in a shell used for LocalStack-targeted CLI or Terraform commands. Use a dedicated shell session and clearly named environment variables.

```bash
# WSL2 shell: these are dummy values for the local emulator, not real credentials.
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_DEFAULT_REGION="us-east-1"
export AWS_EC2_METADATA_DISABLED="true"
```

The values above are intentionally dummy strings. Do not replace them with real credentials. The region is a local test setting, not a statement about the actual location of a service.

Set the endpoint explicitly on each AWS CLI command:

```bash
aws --endpoint-url=http://localhost:4566 sts get-caller-identity
```

This example must be checked against the current LocalStack and AWS CLI docs. The emulator's supported STS response and exact endpoint behaviour may differ. **[VERIFY]** If the emulator does not support the command in the current free scope, do not remove the endpoint flag and rerun against AWS. Instead, verify the emulator target by its documented health endpoint and run an API call known to be supported. An `aws sts get-caller-identity` response is not a cryptographic proof that an endpoint is LocalStack; the endpoint URL and shell environment must also be inspected.

Optional convenience wrapper: `awslocal` may inject a LocalStack endpoint for AWS CLI commands, but wrapper behaviour and installation method should be checked against official LocalStack docs. **[VERIFY]** For safety-critical recipes, prefer the explicit `--endpoint-url` form so the destination is visible in the command.

### 6.5 Real-cloud accident prevention checklist

**Do not run `terraform apply` until every item is true.**

- [ ] The current shell is a dedicated emulator-only shell.
- [ ] `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` contain dummy values, not real credentials.
- [ ] No unexpected `AWS_PROFILE` is active.
- [ ] `AWS_EC2_METADATA_DISABLED=true` is set for the emulator shell.
- [ ] The AWS CLI command includes the explicit LocalStack endpoint.
- [ ] Terraform/OpenTofu configuration explicitly overrides the required provider endpoints according to the current provider and LocalStack documentation.
- [ ] The endpoint hostname and port were inspected immediately before the command.
- [ ] The plan shows only the intended test resources.
- [ ] No command can silently fall back to a real AWS endpoint.

Inspect relevant environment settings without printing secrets from unrelated variables:

```bash
printf 'AWS_PROFILE=%s\n' "${AWS_PROFILE-<unset>}"
printf 'AWS_DEFAULT_REGION=%s\n' "${AWS_DEFAULT_REGION-<unset>}"
printf 'AWS_EC2_METADATA_DISABLED=%s\n' "${AWS_EC2_METADATA_DISABLED-<unset>}"
printf 'AWS_ACCESS_KEY_ID is set: %s\n' "$([ -n "${AWS_ACCESS_KEY_ID-}" ] && echo yes || echo no)"
printf 'AWS_SECRET_ACCESS_KEY is set: %s\n' "$([ -n "${AWS_SECRET_ACCESS_KEY-}" ] && echo yes || echo no)"
```

This prints whether the key variables are set, not their values. If `AWS_PROFILE` names a real profile, stop and unset it in this dedicated shell:

```bash
unset AWS_PROFILE
```

Do not change global AWS configuration as a shortcut. For an intended endpoint check, inspect the literal endpoint in the command or configuration. If using a CLI identity command, pass the explicit endpoint and verify the result matches the emulator's documented behaviour.

### 6.6 AWS CLI workflow against LocalStack

Check the installed CLI version:

```bash
aws --version
```

Use a known-supported service operation only after verifying current free coverage. Example S3 workflow:

```bash
aws --endpoint-url=http://localhost:4566 s3api list-buckets
```

Expected result: a response from the local endpoint, usually with an empty bucket list on a fresh instance. Confirm this expected response against current LocalStack docs. **[VERIFY]** If connection fails, check container status, logs, endpoint binding, and whether the command runs inside WSL2 or another network namespace. Do not remove `--endpoint-url` to “see if it works”; that can send the request to real AWS.

Create a uniquely named lab bucket using a non-sensitive name:

```bash
aws --endpoint-url=http://localhost:4566 s3api create-bucket --bucket stage2e-lab-example-bucket
```

Bucket naming rules apply and a name may already exist in the emulator. If the name is taken, choose a different non-sensitive lab name. Verify:

```bash
aws --endpoint-url=http://localhost:4566 s3api list-buckets
```

**Warning:** deleting a bucket removes its local contents. First list buckets and confirm the exact bucket name and endpoint. For a bucket with objects, inspect and remove only the intended test objects before deleting the bucket.

```bash
aws --endpoint-url=http://localhost:4566 s3api list-objects-v2 --bucket stage2e-lab-example-bucket
```

Use the documented S3 delete workflow only after confirming the bucket contains disposable lab data. Do not run an unreviewed recursive delete.

### 6.7 Terraform/OpenTofu against LocalStack

Terraform and OpenTofu use provider configuration to talk to APIs. For LocalStack, the AWS provider must be configured to use the emulator's endpoints; the exact provider arguments and supported endpoint override shape depend on the provider version. **[VERIFY]** Do not assume setting one environment variable redirects every service or every provider resource. Use the current AWS provider documentation and LocalStack's Terraform guidance. If a dedicated wrapper is available and supported in your chosen toolchain, treat it as optional; inspect what it changes before relying on it.

The following is an **illustrative HCL shape**, not a copy-paste-ready verified configuration. Confirm provider endpoint settings and provider version constraints before running it.

```hcl
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  s3_use_path_style           = true

  # Add the documented S3 endpoint override for your provider version here.
  # Do not omit the endpoint override and assume the provider targets LocalStack.
}

resource "aws_s3_bucket" "lab" {
  bucket = "stage2e-localstack-terraform-bucket"
}
```

The resource block is intentionally simple. The provider's endpoint override is deliberately not guessed: insert the exact supported configuration from the official provider/LocalStack docs before `init`, `plan`, or `apply`. Do not execute this example until that endpoint override is in place and reviewed. Use dummy credentials only. Keep Terraform/OpenTofu state local to a dedicated lab directory and never commit state files, plans, credentials, or generated local metadata.

Suggested `.gitignore` entries for the lab directory:

```gitignore
.terraform/
.terraform.lock.hcl
terraform.tfstate
terraform.tfstate.*
*.tfplan
crash.log
crash.*.log
```

The lock file can be useful for reproducibility and is often intentionally committed in a real project; this proposed ignore pattern is for a disposable lab only. For a durable repository, decide lock-file policy deliberately and do not copy this pattern without review.

**Safe execution order:**
1. Review the endpoint override and provider version docs.
2. Confirm the emulator container is healthy.
3. Set dummy credentials in the dedicated shell.
4. Inspect the provider configuration for an explicit LocalStack endpoint.
5. Run `terraform init` or `tofu init`.
6. Run `terraform validate`.
7. Run `terraform plan` and review all resources.
8. Apply only after the plan and endpoint pass the pre-flight checklist.
9. Change the configuration to practise drift detection, then plan again.
10. Destroy only after confirming the state and endpoint still refer to the emulator.

### 6.8 State, drift, and cleanup

Terraform/OpenTofu state records the relationship between configuration and managed objects. For this exercise, keep state in the lab directory and do not share it with other experiments. State may contain sensitive values in other projects; treat it as sensitive even when this particular exercise uses dummy credentials. Drift detection is demonstrated by changing the local emulator resource outside the IaC tool, then running a plan and reviewing the difference. A plan does not guarantee that every difference is detected; the result depends on provider refresh behaviour and emulator fidelity.

Before destroy, confirm the current directory and inspect the plan/state:

```bash
pwd
terraform state list
terraform plan
```

Use the corresponding `tofu` command if OpenTofu is the selected tool.
**Warning:** destroy removes resources represented in the current state. Confirm that the configuration has the intended emulator endpoint and that the state belongs to this lab before running `terraform destroy` or `tofu destroy`.
Do not run destroy from an unknown directory or against a state file from another project.

### 6.9 Let Kubernetes pods reach LocalStack

A pod's `localhost` is the pod itself. `localhost:4566` inside a pod does not automatically refer to LocalStack running on the WSL2 host. A kind node is itself a container, and Docker network reachability from a node to a sibling container depends on the network configuration. Use a documented host-access or shared-network pattern for the specific kind/LocalStack setup. The correct address differs by topology, so do not hard-code an assumed gateway address. **[VERIFY]**

Debug in layers:
1. Confirm LocalStack is healthy from the WSL2 shell.
2. Inspect Docker networks and container names.
3. Confirm the kind node and LocalStack are connected through the intended route.
4. Test DNS and TCP reachability from a disposable pod.
5. Only then test the AWS API endpoint.
6. Keep the emulator endpoint explicit in application configuration.
7. If using a Kubernetes Secret for dummy values, do not put real credentials in the manifest or Git.

**What not to do:** do not set a pod endpoint to `localhost:4566` unless LocalStack is actually in the same pod/network namespace. Do not solve DNS failures by routing to the public AWS API.

### 6.10 What LocalStack cannot teach you

- Real AWS IAM policy evaluation, identity federation, permission boundaries, or every authorization edge case.
- Actual VPC dataplane, route propagation, security-group behaviour, private endpoints, or cross-account networking.
- Real service quotas, throttling limits, billing, or budget alarms.
- Genuine multi-region or multi-AZ failures.
- All eventual-consistency and distributed-system behaviours.
- Production-grade durability, disaster recovery, and managed-service operations.
- Every API operation or service in the free/community tier.
- The operational experience of support plans, AWS outages, or account-level controls.

Use the local emulator for cheap iteration and the [free-tier cloud safety guide](free-tier-cloud-account-and-cost-safety.md) for a real-cloud experiment only when needed. A real free tier can still incur charges if usage exceeds the current free limits or if a resource is not eligible. Verify pricing and delete resources after the exercise.

**Verify**
- The LocalStack endpoint is explicit in CLI commands and IaC provider configuration.
- Dummy credentials are active in the dedicated shell.
- No real AWS profile is active.
- A known-supported API call succeeds against the local endpoint.
- Terraform/OpenTofu plan output contains only intended lab resources.

**Cleanup**
- Inspect the endpoint and state before destroying IaC-managed resources.
- Inspect buckets and objects before deleting them.
- Stop only the LocalStack container/project you started.
- Do not prune all Docker resources as a shortcut.

**Fidelity caveat:** LocalStack is an API emulator with partial and evolving coverage. Treat all fidelity ratings as provisional and verify current free-tier scope in official docs.

---

## 7. Lab-to-module map

Use this map as a starting point. It identifies the most suitable local environment, not a claim that the environment fully reproduces the production target.

| Module (M01–M17) | Primary lab environment | What to practise | What the lab cannot show |
|---|---|---|---|
| M01 — Container images | Docker + kind; optional local registry | Build, tag, scan, push/load, image-pull diagnosis | Production registry auth, global distribution, real node cache behaviour |
| M02 — CI/CD | kind; optional LocalStack for supported API tests | Build/test/deploy steps, repeatable ephemeral clusters | Hosted runner isolation, production identity, external service reliability |
| M03 — Kubernetes operations | kind | Workloads, probes, rollout/rollback, events, scheduling | Managed control-plane operations and physical node failure |
| M04 — Networking | kind with selected CNI; minikube as comparison | Services, DNS, ingress, NetworkPolicy | Production VPC, cloud load balancers, real network path and failure domains |
| M05 — Storage | kind or minikube | PVC/PV mechanics and mount behaviour | Production CSI driver, zone-aware volumes, managed storage durability |
| M06 — Helm/Kustomize | kind | Render, apply, values/overlays, release upgrades | Production chart governance and external dependencies |
| M07 — Infrastructure as Code | LocalStack for supported APIs; local files for state workflows | Plan, apply, state, drift, destroy safeguards | Real AWS service behaviour, quota, billing, IAM, all provider edge cases |
| M08 — GitOps | kind | Reconcile a repo-backed app and observe drift | Production repo access, identity, multi-tenant control-plane load |
| M09 — Secrets | kind with dummy secrets only | Secret references, access patterns, rotation design | Managed KMS/HSM, enterprise identity, production secret lifecycle |
| M10 — SRE | kind + local app metrics/logs | Health checks, failure injection, recovery notes, simple SLO exercises | Real traffic distributions, paging fatigue, customer impact |
| M11 — Observability | kind/minikube and local telemetry components | Instrumentation, dashboards, logs, metrics, traces | Production scale, retention cost, telemetry loss under real load |
| M12 — Security and supply chain | Docker + kind; scanners locally | Scan images/manifests, provenance concepts, admission checks | Enterprise policy operations, real exploit exposure, full supply-chain trust |
| M13 — Backup/DR | kind and local data snapshots | Backup/restore workflow and documented recovery | Regional loss, cloud backup immutability, actual RPO/RTO at scale |
| M14 — Multi-cluster | Two named kind clusters | Context hygiene, deployment comparison, simulated failover | Real region isolation, inter-region latency, global control plane |
| M15 — FinOps | Local resource inventory; conceptual cost model | Resource requests/limits, waste inventory, tagging conventions | Real invoices, cloud metering, billing dimensions and discounts |
| M16 — Platform engineering | kind plus local templates/scripts | Golden-path template, developer docs, self-service workflow | Org-scale tenancy, adoption, support burden, governance politics |
| M17 — Capstone | kind + LocalStack only for supported APIs; real free tier only if separately approved | End-to-end repeatability, evidence, runbooks, rollback | End-to-end production readiness or customer-grade resilience |

---

## 8. Reference lab recipes

### Recipe 1 — Three-node kind cluster plus ingress

**Goal:** create a reproducible three-node cluster and expose a simple application through a local ingress path.

**Steps**

1. **Review the config.** Save the multi-node config from section 4.4 and use a supported pinned node image tag. The config defines one control-plane and two worker nodes.
2. **Check the host.**

   ```bash
   docker info
   kind get clusters
   ```

This confirms Docker access and shows existing clusters. Resolve name conflicts before creating anything.

3. **Create the cluster.**

   ```bash
   kind create cluster --config kind/kind-three-node.yaml
   ```

This creates the cluster from the saved file. Expected result: command completes and writes kubeconfig context.

4. **Confirm the context.**

   ```bash
   kubectl config get-contexts
   kubectl config current-context
   kubectl get nodes -o wide
   ```

Use the actual context shown. Wait until all three nodes are `Ready`.

5. **Add ingress mappings and controller.** If using the ingress recipe, the cluster must have the required port mappings from section 4.5 at creation time. Install a controller by following its official kind-specific instructions. Do not assume a controller can use a port mapping that was never configured.

6. **Deploy a simple test app.** Use a maintained sample image or your own image and a Service. Ensure the image source is reachable from the cluster.

7. **Verify the route.**

   ```bash
   kubectl get pods,svc,ingress -A
   curl --fail --show-error http://localhost:8080/
   ```

Run `curl` only if the chosen controller and host mapping are configured for port 8080. A non-200 response may indicate routing or application configuration, not necessarily cluster failure.

**Verify**
- Three nodes are ready.
- Current context points to the intended cluster.
- Controller pods are ready.
- The configured local route reaches the test application.

**Cleanup**

**Warning:** the following command permanently deletes the cluster and its local workloads. First inspect cluster names and contexts.

```bash
kind get clusters
kubectl config get-contexts
```

After confirming `stage2e-multi` is the disposable cluster:

```bash
kind delete cluster --name stage2e-multi
```

**Fidelity caveat:** host port mappings and ingress controllers in kind do not reproduce a managed cloud load balancer or a production ingress network path.

### Recipe 2 — Deploy an app with probes and resource limits; watch a rolling update

**Goal:** practise readiness/liveness probes, resource requests and limits, and deployment rollout observation.

**Steps**

1. Create a namespace and confirm the current context first:

   ```bash
   kubectl config current-context
   kubectl create namespace rollout-lab
   ```

If the namespace already exists, inspect it rather than treating that as a reason to delete resources.

2. Save the following manifest as `apps/demo/deployment.yaml`. Replace the image with a valid image available to the cluster. The example image is illustrative; verify its availability and behaviour before using it.

   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: demo-web
     namespace: rollout-lab
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: demo-web
     template:
       metadata:
         labels:
           app: demo-web
       spec:
         containers:
           - name: web
             image: nginx:stable
             ports:
               - containerPort: 80
             resources:
               requests:
                 cpu: "100m"
                 memory: "64Mi"
               limits:
                 cpu: "500m"
                 memory: "128Mi"
             readinessProbe:
               httpGet:
                 path: /
                 port: 80
               initialDelaySeconds: 5
               periodSeconds: 5
             livenessProbe:
               httpGet:
                 path: /
                 port: 80
               initialDelaySeconds: 10
               periodSeconds: 10
   ```

3. Apply it to the intended context:

   ```bash
   kubectl apply -f apps/demo/deployment.yaml
   kubectl rollout status deployment/demo-web -n rollout-lab
   kubectl get pods -n rollout-lab -o wide
   ```

Expected result: two replicas become ready. Image availability and local resource pressure can affect startup time.

4. Observe the current image and rollout history:

   ```bash
   kubectl get deployment demo-web -n rollout-lab -o wide
   kubectl rollout history deployment/demo-web -n rollout-lab
   ```

5. Change the image to another reviewed, compatible tag in the manifest and apply again. Do not use a random tag as a production recommendation.

   ```bash
   kubectl apply -f apps/demo/deployment.yaml
   kubectl rollout status deployment/demo-web -n rollout-lab
   kubectl get rs,pods -n rollout-lab
   ```

Watch the old ReplicaSet scale down and the new ReplicaSet become ready. If the rollout stalls, inspect events and pod status before rolling back.

6. If you intentionally need to rehearse rollback, use:

   ```bash
   kubectl rollout history deployment/demo-web -n rollout-lab
   kubectl rollout undo deployment/demo-web -n rollout-lab
   kubectl rollout status deployment/demo-web -n rollout-lab
   ```

This changes the Deployment to a previous revision; check the history first so you know what will be restored.

**Verify**
- Probes become healthy.
- Requests and limits appear on the Deployment.
- Rollout status completes.
- The rollout history and ReplicaSets show the update.

**Cleanup**

**Warning:** deleting the namespace deletes every object inside it. Inspect the namespace contents before deletion:

```bash
kubectl get all -n rollout-lab
kubectl get pvc,secrets,configmaps -n rollout-lab
```

If it contains only disposable recipe resources, delete it:

```bash
kubectl delete namespace rollout-lab
```

**Fidelity caveat:** local CPU/memory pressure and container startup behaviour are not a production capacity model. A successful rollout does not prove zero-downtime behaviour under real traffic.

### Recipe 3 — NetworkPolicy deny-by-default test

**Goal:** prove that a policy-enforcing CNI blocks traffic until a narrow allow rule is applied.

**Prerequisite:** a disposable kind cluster with a policy-enforcing CNI installed from its official instructions. The default kind network is not sufficient for this exercise. **[VERIFY]**

**Steps**

1. Confirm the cluster context and CNI pods:

   ```bash
   kubectl config current-context
   kubectl get pods -A
   ```

2. Create a namespace:

   ```bash
   kubectl create namespace netpol-lab
   ```

3. Deploy a target pod/service and a client pod using reviewed images that are available in the cluster. Keep the labels and namespace names stable for the test. Wait for both pods to become ready.

4. Prove baseline connectivity **before** applying policy. Use a client command that is present in the selected client image. Record the successful response. If baseline traffic fails, stop and diagnose DNS, labels, ports, and pod health.

5. Save the policy below as `apps/network-policy/default-deny.yaml`:

   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: default-deny-ingress
     namespace: netpol-lab
   spec:
     podSelector: {}
     policyTypes:
       - Ingress
   ```

This policy selects all pods in the namespace and denies ingress that is not allowed by another applicable policy, assuming the CNI enforces NetworkPolicy.

6. Apply it:

   ```bash
   kubectl apply -f apps/network-policy/default-deny.yaml
   ```

7. Repeat the exact baseline connectivity test. Expected result: ingress is blocked by the policy-enforcing CNI. If it still succeeds, verify CNI enforcement and policy selection; do not assume Kubernetes rejected the manifest.

8. Add a narrow allow rule that selects the intended target and permits only the required source labels and port. Verify the labels and port before applying. Save the allow rule in Git and test both allowed and disallowed traffic.

**Verify**
- Baseline traffic worked before policy.
- The default-deny policy is present.
- Expected traffic is blocked after applying policy.
- Only the intended allowed flow succeeds after the narrow allow rule.

**Cleanup**

**Warning:** remove only the disposable namespace and only after checking its contents.

```bash
kubectl get all -n netpol-lab
kubectl get networkpolicy -n netpol-lab
```

If the namespace contains only this exercise:

```bash
kubectl delete namespace netpol-lab
```

**Fidelity caveat:** policy behaviour depends on the CNI and version. This does not prove equivalence to cloud security groups, VPC routing, service meshes, or enterprise network controls.

### Recipe 4 — Push to a local registry and deploy

**Goal:** practise the registry workflow rather than only copying an image into a cluster.

**Steps**

1. Follow the current official kind local-registry pattern and record the registry endpoint, container name, Docker network, and kind configuration. Do not use an assumed address from a tutorial. **[VERIFY]**
2. Build the application image from a valid local build context:

   ```bash
   docker build -t demo-web:dev ./apps/demo
   ```

Expected result: a local image exists. Confirm with `docker image ls demo-web`.

3. Tag the image with the exact registry endpoint and repository path defined by your reviewed local-registry setup:

   ```bash
   docker tag demo-web:dev <REGISTRY_HOST_AND_PORT>/demo-web:dev
   ```

Replace the placeholder with the actual endpoint; do not paste it literally.

4. Push it:

   ```bash
   docker push <REGISTRY_HOST_AND_PORT>/demo-web:dev
   ```

Expected result: the registry accepts the image. If it fails, inspect DNS, registry reachability, and registry configuration; do not switch to a public registry without recording the change.

5. Set the Deployment image to the exact pushed image reference and apply it to the intended context:

   ```bash
   kubectl config current-context
   kubectl apply -f apps/demo/deployment.yaml
   kubectl rollout status deployment/demo-web -n rollout-lab
   ```

Ensure the manifest uses the correct namespace and registry reference. The manifest in recipe 2 uses a sample image until you edit it.

6. Verify image and pod state:

   ```bash
   kubectl get pods -n rollout-lab -o wide
   kubectl describe pods -n rollout-lab
   ```

**Verify**
- Image push completes.
- The manifest uses the exact registry/repository/tag.
- Pods start without `ImagePullBackOff`.
- The registry workflow is documented well enough to recreate from scratch.

**Cleanup**

**Warning:** removing registry containers or images can affect other labs. Inspect the exact container and image names first:

```bash
docker ps -a
docker image ls
```

Remove only the lab resources after confirming their names and that no other workload depends on them. Avoid broad Docker prune commands.

**Fidelity caveat:** a local registry does not reproduce production registry identity, retention policies, replication, scanning gates, or supply-chain governance.

### Recipe 5 — Terraform/OpenTofu creates an S3 bucket in LocalStack and detects drift

**Goal:** practise plan/apply/state/drift mechanics without provisioning an AWS bucket.

**Prerequisites:** LocalStack is running; free/community S3 coverage has been checked; the provider endpoint override has been filled in from official docs; the shell uses dummy credentials; no real profile is active. **[VERIFY]**

**Steps**

1. Run the pre-flight checklist in section 6.5. Do not proceed if the endpoint override is absent or uncertain.
2. Use a dedicated directory containing the reviewed HCL. The provider config must explicitly target the LocalStack endpoint. The illustrative HCL in section 6.7 is not ready to apply until the correct endpoint override is added.
3. Set emulator-only credentials in the current shell:

   ```bash
   export AWS_ACCESS_KEY_ID="test"
   export AWS_SECRET_ACCESS_KEY="test"
   export AWS_DEFAULT_REGION="us-east-1"
   export AWS_EC2_METADATA_DISABLED="true"
   unset AWS_PROFILE
   ```

These are dummy values for the local emulator. Do not use real credentials in this shell.

4. Review the provider configuration and endpoint. Run initialization and validation only after the endpoint is correct:

   ```bash
   terraform init
   terraform validate
   terraform plan
   ```

Use `tofu` instead if OpenTofu is the chosen tool. Review the plan; it must contain only the intended S3 bucket.

5. Apply only after confirming the endpoint and plan:

   ```bash
   terraform apply
   ```

Review the proposed action and confirm only when it matches the intended local resource. Do not auto-approve during initial learning.

6. Create or modify the test bucket through the explicitly targeted LocalStack CLI, using a documented operation, to simulate out-of-band drift. Verify the exact bucket name and endpoint before changing it.
7. Run a plan again:

   ```bash
   terraform plan
   ```

Review whether the provider reports a difference. The result depends on the provider's refresh behaviour and the emulator's fidelity.

8. Capture evidence: configuration, endpoint, plan output with sensitive data omitted, and a note describing what drift was detected or not detected.

**Verify**
- CLI calls explicitly use the LocalStack endpoint.
- Terraform/OpenTofu provider endpoints are explicitly overridden.
- Plan output contains only the intended local resource.
- Drift result is recorded with its limitations.

**Cleanup**

**Warning:** destroy removes resources in the current IaC state. Re-check `pwd`, provider endpoint, and state before proceeding.

```bash
pwd
terraform state list
terraform plan
```

Only after confirming the state belongs to this LocalStack lab and the endpoint is local:

```bash
terraform destroy
```

Use `tofu destroy` for OpenTofu. Confirm the proposed destruction interactively. Never remove the endpoint override as a way to “fix” a provider error.

**Fidelity caveat:** emulator drift detection does not prove the same refresh semantics, consistency model, or edge cases as AWS S3 and the AWS provider in production.

### Recipe 6 — Two kind clusters as two simulated regions and a failover drill

**Goal:** practise explicit cluster targeting, deployment parity, and a simple manual failover drill without claiming real regional resilience.

**Steps**

1. Create two clusters from the same reviewed configuration but with unique names, for example `stage2e-east-lab` and `stage2e-west-lab`. Keep node image tags consistent unless version skew is the experiment.
2. Verify both cluster names and contexts:

   ```bash
   kind get clusters
   kubectl config get-contexts
   ```

3. Deploy the same test application to each cluster, explicitly specifying the context:

   ```bash
   kubectl --context kind-stage2e-east-lab apply -f apps/demo/deployment.yaml
   kubectl --context kind-stage2e-west-lab apply -f apps/demo/deployment.yaml
   ```

Replace context names with the actual names returned by `kubectl config get-contexts`. Ensure the manifest namespace exists in both clusters.

4. Verify both deployments separately:

   ```bash
   kubectl --context kind-stage2e-east-lab get deploy,pods -A
   kubectl --context kind-stage2e-west-lab get deploy,pods -A
   ```

The second command should use the west context; do not accidentally repeat the east context when running the drill.

5. Define what “failover” means for this exercise. For example, mark the east app as unavailable by scaling its test Deployment to zero, then route your test client to the west endpoint. Do this only in the disposable lab and record the exact command and expected impact.

   ```bash
   kubectl --context kind-stage2e-east-lab scale deployment/demo-web --replicas=0 -n rollout-lab
   ```

6. Verify that the east Deployment has zero replicas and that the west deployment remains healthy. Test the chosen client path and record how routing was switched. This is a manual simulation, not automated global traffic management.
7. Restore the east deployment after the drill:

   ```bash
   kubectl --context kind-stage2e-east-lab scale deployment/demo-web --replicas=2 -n rollout-lab
   kubectl --context kind-stage2e-east-lab rollout status deployment/demo-web -n rollout-lab
   ```

**Verify**
- Two distinct clusters and contexts exist.
- The same app is deployed in both.
- The drill's trigger, routing change, observed interruption, and recovery are documented.
- Commands specify the intended context explicitly.

**Cleanup**

**Warning:** deleting either cluster removes its local workloads. List clusters and contexts before deleting:

```bash
kind get clusters
kubectl config get-contexts
```

Delete only the named disposable cluster after confirming its identity:

```bash
kind delete cluster --name stage2e-east-lab
kind delete cluster --name stage2e-west-lab
```

Run each deletion only if that exact cluster is intended to be removed.

**Fidelity caveat:** two clusters on one laptop are not two regions. They share hardware and often network, power, storage, and host failure domains; the drill simulates the workflow only.

---

## 9. Reset, cleanup, and cost-of-resources

### 9.1 Inventory before cleanup

Use read-only inventory commands before stopping or deleting anything:

```bash
kind get clusters
minikube profile list
docker ps
docker ps -a
docker image ls
docker volume ls
kubectl config get-contexts
```

Some commands may report that a tool or profile is unavailable; that is fine if the corresponding optional tool is not installed. Do not infer that every Docker container belongs to this roadmap.

### 9.2 Stop versus delete

Stopping a container or profile can preserve local state, but exact behaviour depends on the tool. Deleting a kind cluster removes its node containers and in-cluster resources. Deleting a minikube profile removes that local cluster. Stopping LocalStack is different from deleting any persistent data directory or volume that may be configured. Read the exact Compose file and tool help before stopping or deleting resources.

**Warning:** before any delete/reset command, list the target resources and verify their names. Do not use `kind delete clusters --all`, a global Docker prune, or a broad volume deletion as a routine reset.

### 9.3 Docker disk usage

Inspect Docker disk usage first:

```bash
docker system df
docker image ls
docker volume ls
```

Remove only known-unused images and containers after checking their names and dependencies. `docker system prune` and volume-prune commands can delete resources belonging to unrelated projects. Avoid them unless you understand the scope and have reviewed the confirmation prompt. Do not delete WSL virtual disks or Docker data directories manually as a first-line cleanup technique.

### 9.4 Avoid exhausting WSL2 resources

- Keep one primary kind cluster for most exercises.
- Create additional clusters only for multi-cluster exercises.
- Use the smallest topology that can test the hypothesis.
- Delete disposable clusters when the exercise is complete.
- Avoid running kind, minikube, LocalStack, multiple databases, and large observability stacks simultaneously unless needed.
- Monitor Docker disk usage and WSL2 memory pressure.
- Keep project files in the recommended Linux filesystem location for WSL workflows rather than repeatedly moving large build contexts across the Windows/Linux boundary.
- Treat memory and CPU settings as machine-specific. Check current WSL docs before editing `.wslconfig`; exact keys, defaults, and restart behaviour can change. **[VERIFY]**
- Leave enough resources for Windows and your editor; an oversized WSL allocation can make the host less stable.
- Avoid persistent data volumes unless the exercise specifically teaches persistence.

### 9.5 Rebuild target

Set a **reproducibility goal**, not a timing guarantee: be able to rebuild the base cluster, deploy the sample app, and run the core verification checks from tracked configuration and notes without guessing. The time will vary with image downloads, disk speed, CPU, Docker state, and network access. Record each manual step that was not yet automated. Do not optimise for speed before you can explain the setup.

**Verify**
- You can inventory all lab resources.
- You know which resources are disposable and which contain state you want to preserve.
- Your configs and notes are committed; no secrets or state files are committed.

**Cleanup**
- Inspect before delete.
- Delete only named lab resources.
- Avoid global prune commands unless the complete impact is understood.

**Fidelity caveat:** resource consumption on one laptop is not a reliable model of production capacity, scheduling density, or cloud cost.

---

## 10. Troubleshooting (symptom → cause → fix)

| Symptom | Possible cause | Safe diagnostic and fix |
|---|---|---|
| kind cluster will not start | Docker daemon unavailable, insufficient resources, unsupported image/tag, cgroup or WSL2 issue `[VERIFY]` | Run `docker info`, inspect kind output, check current kind and WSL docs, reduce cluster count, and retry with a supported node image |
| Node stays `NotReady` | CNI or node startup issue | Run `kubectl get nodes`, `kubectl describe node <NODE_NAME>`, and `kubectl get pods -A`; inspect events before changing configuration |
| `ImagePullBackOff` for a local image | Image was not loaded or registry reference is unreachable | Confirm image reference, inspect pod events, use `kind load docker-image` or the reviewed local registry path |
| Ingress is not reachable from Windows | Host mapping absent, controller not listening on mapped ports, WSL2 forwarding difference | Check kind config, controller Service/pods, and the actual host-side port; follow official kind/WSL docs `[VERIFY]` |
| `LoadBalancer` remains `<pending>` | No load-balancer implementation | Use an appropriate documented local helper such as MetalLB or `cloud-provider-kind` with compatible versions `[VERIFY]`; do not expect cloud behaviour by default |
| `kubectl top` fails with TLS error | metrics-server cannot validate kubelet certificate/address | Inspect metrics-server logs and official docs; do not disable TLS checks without a documented local-only reason `[VERIFY]` |
| LocalStack connection refused | Container stopped, endpoint/port wrong, or command runs in another network namespace | Run `docker compose ps`, inspect logs, and verify the endpoint from the command's network context |
| LocalStack CLI call hits real AWS | Endpoint override missing or profile/provider config is wrong | Stop immediately; inspect command and provider endpoint, unset the real profile in the dedicated shell, reset dummy credentials, and rerun only after the pre-flight passes |
| Terraform/OpenTofu tries real AWS | Provider endpoint override absent or incomplete | Do not apply; inspect provider docs and config, run a reviewed plan only after the endpoint is explicit |
| DNS fails in pods | CoreDNS, CNI, or upstream DNS path issue | Inspect `kubectl get pods -n kube-system`, DNS pod logs, and service names; distinguish cluster DNS from host DNS |
| Disk is full | Container images, cluster node layers, logs, or volumes grew | Run `docker system df`, inventory clusters and volumes, then remove only known disposable resources |
| Too many open files or inotify limits | Host/WSL limits or too many watched files `[VERIFY]` | Inspect exact error, current WSL/kernel guidance, and editor/watchers; do not copy arbitrary sysctl values |
| minikube driver error | Unsupported driver combination, Docker unavailable, stale profile | Check `minikube start --help`, `docker info`, profile list, and official WSL driver guidance `[VERIFY]` |
| Commands target wrong cluster | `kubectl` context changed | Run `kubectl config current-context` and `kubectl config get-contexts`; use explicit `--context` for critical commands |
| Clock-skew or signature error | Host clock/time sync problem or credential/signature mismatch | Check host time and local credentials; do not compensate by disabling verification or switching to real credentials |
| CNI install breaks networking | Incompatible manifest/version or conflicting CNI | Use a disposable cluster, inspect CNI pod logs/events, and rebuild from a known config instead of layering random patches |
| Local registry push works but pod pull fails | Node cannot resolve/reach registry, trust mismatch, wrong image path | Verify registry path and node network; follow kind's documented registry setup `[VERIFY]` |
| LocalStack service API returns unsupported operation | API/service is absent from current free scope or not emulated fully | Check current service matrix and pricing/feature documentation; downgrade exercise to conceptual or use a real free-tier exercise with guardrails |
| Resource pressure freezes WSL2 | Too many clusters or heavy components | Stop optional stacks, inspect inventory, delete only confirmed disposable clusters, and review current WSL resource configuration guidance |

For placeholder commands such as `kubectl describe node <NODE_NAME>`, substitute the exact name returned by `kubectl get nodes`. Do not paste the placeholder literally. If a troubleshooting step could destroy state or weaken security, stop and read the relevant official documentation first.

---

## 11. Good lab habits for production thinking

### 11.1 Lab-as-code

- Keep kind configuration, manifests, Terraform/OpenTofu files, and helper scripts in Git.
- Record tool versions, node image tags, CNI version, ingress controller version, and LocalStack image tag.
- Pin versions deliberately when reproducibility matters; update them deliberately when security or compatibility requires it.
- Do not commit kubeconfig files containing sensitive contexts, Terraform state, plan files, real credentials, tokens, or secret manifests.
- Keep setup instructions short enough that another learner can reproduce the lab.

### 11.2 Hypothesis before action

Before a disruptive experiment, write:
1. The hypothesis.
2. The smallest change that can test it.
3. The expected observation if the hypothesis is true.
4. The alternative explanations.
5. The rollback or rebuild path.
6. The evidence that will be saved.

This prevents a failed command from being mistaken for a successful experiment.

### 11.3 Record observations, not only outcomes

For each recipe, save:
- date and tool versions;
- cluster name and current context;
- config or manifest revision;
- command run;
- relevant events/logs;
- expected versus actual behaviour;
- cleanup performed;
- the limitation that remains untested.

Remove tokens, sensitive values, private hostnames, and account identifiers from evidence before committing it.

### 11.4 "What this lab hid from me" note

After each exercise, answer:
- Which production dependency was replaced by a local simplification?
- Which failure domain was absent?
- Which permission or network rule was not tested?
- What would need to be verified in a real environment?
- What evidence would be required before declaring the system production-ready?

A lab is complete when you can explain both the result and its boundary.

### 11.5 Context and destructive-command hygiene

Before `apply`, `rollout`, `scale`, or `delete`, ask:
- Which cluster am I targeting?
- Which namespace and object names are affected?
- Is this a disposable lab?
- Is the command using the intended LocalStack endpoint or real cloud?
- How will I verify the change?
- How will I recover if it fails?

Use explicit `--context` and `-n` values for high-impact Kubernetes commands. Use a dedicated local emulator shell and explicit endpoints for LocalStack. Do not build a muscle memory of running destructive commands first and checking their targets afterward.

---

## 12. Reference Sources

Use official documentation and release pages. Check current versions and platform caveats at the time you run the lab; this guide has not been live-validated against your machine.

### kind
- kind documentation
- kind configuration documentation
- kind release page and supported node images
- kind local registry documentation

### Kubernetes
- Kubernetes documentation
- Kubernetes version-skew policy
- Kubernetes NetworkPolicy documentation
- Kubernetes Ingress documentation
- Kubernetes Service documentation
- Kubernetes storage documentation
- Kubernetes kubectl reference

### minikube
- minikube documentation
- minikube drivers documentation
- minikube add-ons documentation
- minikube LoadBalancer/tunnel documentation
- minikube image loading documentation

### LocalStack
- LocalStack documentation
- LocalStack service coverage documentation
- LocalStack pricing and feature documentation
- LocalStack AWS CLI / `awslocal` documentation
- LocalStack Docker/Compose documentation
- LocalStack Terraform/OpenTofu guidance

### Terraform/OpenTofu and AWS
- Terraform AWS provider documentation
- Terraform CLI documentation
- OpenTofu documentation
- AWS CLI v2 documentation
- AWS IAM documentation
- AWS S3 API documentation
- AWS Free Tier and pricing documentation

### Docker and WSL2
- Docker Engine documentation
- Docker Compose documentation
- Docker security documentation
- Microsoft WSL documentation
- Microsoft WSL configuration documentation

### Networking, ingress, policy, and metrics
- Selected ingress controller's official documentation
- Selected CNI's official installation and NetworkPolicy documentation
- metrics-server documentation
- MetalLB documentation
- cloud-provider-kind documentation

---

=====AUDIT REPORT=====

## Summary

This is a static review of the generated guide. No live web documentation lookup, clean-machine build, or command execution against your WSL2 environment was performed. The classifications below describe the conservatism of the content, not a claim that each item was externally verified.

| Class | Count / scope | Meaning |
|---|---:|---|
| VERIFIED-STABLE | 28 command/config patterns | Common CLI and Kubernetes workflow patterns included as instructional examples; not executed here |
| VERIFY-AGAINST-DOCS | 31 command/config/behaviour items | Version-sensitive flags, endpoint overrides, free-tier coverage, platform networking, or add-on behaviour that must be checked upstream |
| REMOVED | 8 risky or unsupported specifics | Exact LocalStack Terraform endpoint arguments, assumed host-gateway addresses, unverified image tags, broad prune/reset commands, and unsupported fidelity claims were omitted or softened |

Counts are approximate editorial inventory counts, not an automated parser's count of every shell line.

## Audit findings and actions

| Item | Section | Issue found | Action taken |
|---|---|---|---|
| kind node image | 4.4 | A fixed tag would age quickly and may not match the target Kubernetes version | Used `<NODE_IMAGE_TAG>` and required checking the kind release page |
| kind config | 4.4–4.5 | Configuration API and port mapping need current documentation confirmation | Kept the known config shape, tagged for verification, and separated port mapping from controller installation |
| Registry setup | 4.6 and recipe 4 | Exact Docker network/registry details vary by setup | Described the documented pattern and retained explicit placeholders rather than inventing a reachable address |
| NetworkPolicy | 4.7 and recipe 3 | Default networking is not a reliable policy enforcement test | Required a policy-enforcing CNI and a baseline connectivity test before policy |
| metrics-server TLS | 4.8 | Local kubelet certificate behaviour can tempt unsafe workarounds | Required logs/docs review and warned against disabling TLS checks reflexively |
| LoadBalancer | 4.11 and troubleshooting | Local cluster does not create a cloud load balancer automatically | Named helper options as candidates and marked compatibility for verification |
| minikube driver | 5.1–5.2 | Driver support depends on current version and WSL2 setup | Recommended Docker driver as a first option to investigate, tagged `[VERIFY]` |
| LocalStack free tier | 6.1–6.2 | Service coverage and paid features change | Made ratings provisional, conservative, and explicitly subject to current service matrix/pricing checks |
| LocalStack health endpoint | 6.3 | Endpoint response and readiness behaviour are version-sensitive | Directed reader to official health docs instead of inventing a health-check command |
| AWS CLI endpoint | 6.4–6.6 | Missing endpoint can accidentally contact real AWS | Kept endpoint explicit in examples and added dummy credentials/profile checks |
| STS identity check | 6.4–6.5 | Emulator may not support the same response or prove endpoint identity by itself | Marked `[VERIFY]` and stated that endpoint inspection is also required |
| Terraform provider endpoint | 6.7 and recipe 5 | Provider endpoint arguments are version-sensitive; a wrong example is dangerous | Deliberately did not guess the exact endpoint argument; apply is blocked until the official shape is inserted |
| IaC state | 6.7–6.8 | State and plans may contain sensitive data | Kept state local, warned against committing state/plans, and added endpoint/state checks before destroy |
| Pod-to-LocalStack networking | 6.9 | `localhost` has different meanings across network namespaces | Avoided assuming a host gateway and prescribed layered diagnostics |
| Multi-cluster drill | Recipe 6 | Two local clusters could be misrepresented as real regions | Labelled the drill as simulated and required explicit contexts |
| Destructive cleanup | Throughout | Broad delete/prune commands could remove unrelated work | Added inventory and target-confirmation steps before deletion; avoided all-cluster delete recipes |
| Zero-budget scope | Throughout | Some LocalStack functionality may require a paid tier | Required a free-scope check and conceptual fallback for paid/unavailable features |

## Full `[VERIFY]` list

Check each item against the named official source before relying on the associated exercise.

1. **kind node image tags and Kubernetes version compatibility** — kind release page; kind configuration docs.
2. **kind config schema and `extraPortMappings` behaviour** — kind configuration docs.
3. **kind local registry topology and registry mirror/trust configuration** — kind local registry docs.
4. **kind default CNI NetworkPolicy enforcement behaviour** — kind docs; Kubernetes NetworkPolicy docs.
5. **Selected policy-enforcing CNI installation for the selected Kubernetes version** — Calico or Cilium official docs, whichever you choose.
6. **Ingress controller installation and port expectations** — selected ingress controller docs; kind docs.
7. **metrics-server installation and local kubelet TLS/address caveats** — metrics-server docs; Kubernetes docs.
8. **Local LoadBalancer helper compatibility** — MetalLB docs or cloud-provider-kind docs; kind docs.
9. **minikube Docker driver support and WSL2-specific requirements** — minikube drivers docs; Microsoft WSL docs.
10. **minikube CPU/memory flags and profile command behaviour** — minikube docs and installed `minikube start --help`. 11. **minikube add-on names and availability** — minikube add-ons docs. 12. **minikube tunnel requirements and host-side effects** — minikube LoadBalancer/tunnel docs. 13. **LocalStack current free/community service coverage and paid feature boundaries** — LocalStack service coverage and pricing/feature docs. 14. **LocalStack Docker image tag, exposed ports, environment settings, persistence, and readiness endpoint** — LocalStack Docker/Compose and health docs. 15. **`awslocal` behaviour and installation path** — LocalStack AWS CLI / `awslocal` docs. 16. **LocalStack STS support and response behaviour** — LocalStack service docs and AWS CLI docs. 17. **S3 operations and bucket naming/region behaviour in current LocalStack free scope** — LocalStack S3 service docs; AWS S3 API docs. 18. **AWS CLI `--endpoint-url` behaviour for the installed AWS CLI version** — AWS CLI v2 docs. 19. **AWS provider endpoint override syntax for the chosen Terraform/OpenTofu and provider versions** — Terraform AWS provider docs; LocalStack Terraform/OpenTofu guidance. 20. **Provider arguments such as `skip_credentials_validation`, `skip_metadata_api_check`, and `s3_use_path_style`** — Terraform AWS provider docs for the chosen version. 21. **Terraform/OpenTofu wrapper compatibility, if chosen** — LocalStack guidance and the wrapper's official docs. 22. **kind node startup/cgroup behaviour in the current WSL2/Docker setup** — kind docs; Docker Engine docs; Microsoft WSL docs. 23. **Ingress access from Windows host to WSL2-published ports** — kind docs; Microsoft WSL networking docs. 24. **DNS diagnosis and CoreDNS behaviour in the selected cluster** — Kubernetes DNS debugging docs. 25. **Open-file/inotify limit guidance for the current WSL kernel** — Microsoft WSL docs and relevant Linux kernel documentation. 26. **`.wslconfig` keys and resource-limit defaults, if edited** — Microsoft WSL configuration docs. 27. **Image availability and pull policy for the selected demo image/tag** — image publisher docs; Kubernetes Pod image docs. 28. **NetworkPolicy YAML behaviour with the selected CNI** — Kubernetes NetworkPolicy docs and selected CNI docs. 29. **LocalStack container/pod network connectivity for the actual Docker network topology** — Docker networking docs; kind local registry/network docs; LocalStack docs. 30. **Current AWS Free Tier limits and prices before any real-cloud exercise** — AWS Free Tier and pricing documentation. 31. **Any optional tool or service coverage not explicitly described as core** — that tool's official documentation before use.

## Confidence statement

**High:** the safety principles, explicit-context habit, local-versus-production caveats, and need for explicit LocalStack endpoints are appropriate baseline practices.  
**Medium:** the example command flow and YAML/HCL patterns are plausible starting points, but compatibility depends on installed versions and the final local topology.  
**Not verified:** no live docs were checked, no YAML/HCL validators were run, no cluster was created, no LocalStack API call or Terraform apply was executed, and no clean WSL2 machine was available for testing.

## Run it yourself: first five steps

1. **Check the base toolchain.** In WSL2, run `docker info`, `kind version`, `kubectl version --client`, and `lab-doctor.sh` if present; record versions and resolve any failures first.
2. **Create the three-node kind cluster.** Replace `<NODE_IMAGE_TAG>` with a supported image tag from the kind release docs, then create the cluster and verify all nodes are `Ready`.
3. **Run recipe 2.** Deploy the probe/resource-limited app, watch rollout status and ReplicaSets, then inspect namespace contents before cleanup.
4. **Complete the LocalStack pre-flight before any IaC action.** Confirm dummy credentials, no real profile, explicit endpoint overrides, current free-tier coverage, and a reviewed provider configuration. Do not run apply while any endpoint setting remains a placeholder.
5. **Run recipe 5 only after the endpoint is proven local, then tear down.** Review the plan before apply; inspect state and endpoint before destroy; finally inventory and delete only the named lab clusters and containers.
