# Lab Environment Setup — Stage 2E

> Prepare a reproducible, zero-budget workstation for the Stage 2E DevOps, SRE, and platform-engineering labs.

- **Estimated time:** 4–8 hours, depending on downloads, workstation permissions, and prior experience
- **Platforms covered:** WSL2 with Ubuntu (primary); native Ubuntu/Linux (secondary)
- **Last reviewed:** 2026-10-24
- **Tool versions:** check the official upstream source at install time; record the installed versions in `versions.txt`
- **Default IaC convention proposed here:** OpenTofu for hands-on labs; Terraform is covered comparatively. Confirm this proposal against `production-devops-tooling-map.md` before adopting it repository-wide.

## 1. Purpose and scope

This file prepares the base workstation and toolchain used throughout Stage 2E. It covers OS readiness, a shell and editor baseline, a container runtime, Kubernetes command-line tools, Infrastructure as Code (IaC), cloud and supporting CLIs, security tools, and a read-only readiness check.

It is **not** the cluster or LocalStack walkthrough, the cloud-account and billing guide, the tool catalogue, or a tutorial for every tool. Use the sibling files for their specific jobs:

- [README.md](README.md) — stage entry point and module map.
- [learning-plan.md](learning-plan.md) — learning order and checkpoints.
- [prerequisites-and-exit-criteria.md](prerequisites-and-exit-criteria.md) — entry and completion gates.
- [production-devops-tooling-map.md](production-devops-tooling-map.md) — tool purpose, alternatives, and trade-offs.
- [local-lab-kind-minikube-and-localstack.md](local-lab-kind-minikube-and-localstack.md) — local Kubernetes and LocalStack lab setup.
- [free-tier-cloud-account-and-cost-safety.md](free-tier-cloud-account-and-cost-safety.md) — cloud-account safeguards and cost controls.
- [Projects/01-production-readiness-baseline.md](Projects/01-production-readiness-baseline.md) — first readiness-audit project.

**Core** tools are needed for the stage's primary workflows. **Optional/Awareness** tools are installed only when a module needs them or are studied conceptually. This guide avoids pinned versions because upstream releases and supported combinations change.

## 2. Setup roadmap at a glance

| Phase | Outcome | Verification gate |
|---|---|---|
| 0. Hardware and OS readiness | WSL2/Linux is usable and has adequate resources and disk | Distribution is running; Linux filesystem has working space; virtualization and WSL status are understood |
| 1. Base system | Shell, package manager, Git, certificates, editor, and SSH basics are ready | `git --version`, `curl --version`, and `jq --version` succeed |
| 2. Container runtime | One container runtime works | `docker run --rm hello-world` succeeds, or the chosen compatible engine's equivalent is documented |
| 3. Kubernetes CLI toolchain | `kubectl`, Helm, Kustomize, and selected optional tools are available | Client commands return versions; no cluster is required yet |
| 4. IaC and cloud CLIs | OpenTofu and AWS CLI are available without creating paid resources | Version checks pass; no credentials are required for local-only work |
| 5. Supporting CLIs | JSON/YAML, network, TLS, and troubleshooting tools are ready | Core commands return versions/help and basic local checks work |
| 6. Security and supply chain | Optional scanners, SBOM, signing, and pre-commit tools are ready when needed | Each selected tool's local version/smoke check passes |
| 7. Verification gate | A read-only doctor script checks the baseline | All required checks pass, or each failure has a recorded remediation plan |

Proceed in order. Do not install every optional tool at once. The smallest reliable toolchain is easier to troubleshoot and less likely to exhaust a modest laptop.

## 3. Phase 0 — Hardware and OS readiness

### 3.1 Resource planning

A single local Kubernetes cluster plus a small service and a lightweight telemetry stack is the intended baseline. More clusters, service meshes, log indexing, and traces consume additional CPU, memory, and disk.

| Resource | Practical guidance | Check |
|---|---|---|
| CPU | Hardware virtualization should be available; multiple cores improve container builds and local cluster responsiveness | Windows Task Manager or Windows system information; Linux `lscpu` |
| RAM | Leave memory for Windows, the WSL distribution, editor, browser, and container workloads. Avoid running all observability components and multiple clusters simultaneously on a constrained machine | Windows Task Manager; Linux `free -h` |
| Disk | Keep room for package caches, images, cluster state, logs, and project files. Image layers and local volumes accumulate over time | Windows storage settings; Linux `df -h` and `du -sh` |
| OS | Use a currently supported Ubuntu release appropriate for the selected tools | `lsb_release -a` if installed; otherwise inspect `/etc/os-release` |
| Network | Downloads and package repositories need DNS and HTTPS connectivity | `getent hosts ubuntu.com` and `curl -I https://ubuntu.com` if outbound access is permitted |

These are qualitative guidelines, not hardware guarantees. Check each project's current documented requirements before adding heavy components.

### 3.2 Check Windows virtualization and WSL

Run the following in **Windows PowerShell**, not inside the Linux shell:

```powershell
wsl --status
```

- **What it does:** reports WSL status and related default information supported by the installed WSL release.
- **Expected result:** WSL status is displayed. If the command is unsupported, update or inspect WSL using current Microsoft Learn guidance.

```powershell
wsl --list --verbose
```

- **What it does:** lists installed distributions and whether they use WSL 1 or WSL 2.
- **Expected result:** your Ubuntu distribution appears and its version column shows `2`.
- **If not:** consult Microsoft Learn: WSL installation and conversion guidance. Do not blindly convert a distribution used for important work without a backup.

Check virtualization in **Task Manager → Performance → CPU** and inspect the virtualization status. Windows features and firmware settings vary by device. If virtualization is disabled, follow the device manufacturer's instructions and your organization's policy; do not change firmware settings on a managed device without authorization.

### 3.3 Check the Linux environment

Run these commands **inside the Ubuntu/WSL terminal**:

```bash
cat /etc/os-release
uname -a
nproc
free -h
df -h /
```

- `cat /etc/os-release` identifies the distribution.
- `uname -a` reports kernel information.
- `nproc` reports available processing units.
- `free -h` summarizes memory.
- `df -h /` shows free space for the root filesystem.

**Expected result:** the commands complete without errors and the root filesystem has room for the planned lab. Record constraints in your notes rather than assuming a local cluster will fit.

### 3.4 Recommended filesystem location

Keep the repository and active lab files in the Linux filesystem, for example under your Linux home directory, rather than under a Windows-mounted path such as `/mnt/c/...`. Cross-filesystem access can have different performance and file-permission behavior; the exact impact depends on the workload and WSL configuration.

Example, run **inside Ubuntu/WSL**:

```bash
mkdir -p "$HOME/src"
cd "$HOME/src"
pwd
```

- **What it does:** creates a source-work directory and enters it.
- **Expected result:** `pwd` prints a path below your Linux home directory.

Do not move or delete an existing repository until you have checked for uncommitted work and made a backup.

### 3.5 WSL memory and configuration

WSL supports configuration through `.wslconfig` on Windows and per-distribution configuration mechanisms. Available options and defaults can depend on the installed WSL version and Windows build. **[VERIFY]** the current Microsoft Learn documentation before editing configuration.

Guidance:

- Start with defaults and measure actual memory/disk pressure before changing limits.
- Leave enough memory for Windows and other applications.
- Change one setting at a time and keep a copy of the prior configuration.
- After a `.wslconfig` change, follow Microsoft's current restart procedure; do not assume every setting takes effect without restarting WSL.
- Do not copy numeric settings from a different machine without understanding the available RAM and workload.

**Verify**

- [ ] `wsl --list --verbose` shows the intended distribution running WSL 2.
- [ ] The Linux commands above complete.
- [ ] The repository will live under the Linux filesystem.
- [ ] You understand how to restore any WSL configuration you change.

**Rollback:** no system changes are required in this phase. If you edited a WSL configuration file, restore your saved copy and follow current Microsoft Learn instructions to apply it.

## 4. Phase 1 — Base system

### 4.1 Update package metadata and install baseline packages

Run these commands **inside Ubuntu/WSL or native Ubuntu**. The first command refreshes package metadata; the second installs common command-line utilities. Both use `sudo` because they change system package state.

```bash
sudo apt update
```

- **Elevated privilege:** yes. Refreshes the package index.
- **Expected result:** repository metadata is fetched without unresolved repository or signature errors.

```bash
sudo apt install --yes ca-certificates curl git jq unzip zip make build-essential gnupg lsb-release file less vim nano openssh-client
```

- **Elevated privilege:** yes. Installs the listed packages using the configured Ubuntu repositories.
- **Expected result:** apt completes and reports packages installed or already current.
- **Rollback:** remove only packages you deliberately added and no longer need; do not run a broad autoremove command without reviewing its proposed removals.

If apt reports a repository signature/key error, stop and resolve the repository configuration using official Ubuntu or vendor instructions. Do not disable signature checking.

### 4.2 Verify the base packages

Run inside Ubuntu/WSL:

```bash
git --version
curl --version
jq --version
unzip -v
make --version
ssh -V
```

Each command should print its version or usage information. Record the results in `versions.txt` later in this guide.

### 4.3 Minimal shell setup

Keep the shell configuration small and understandable. Add only aliases or functions you know how to debug. Avoid aliases that hide destructive flags or change command meaning.

Useful shell habits:

- Use `set -o` to inspect shell options rather than copying opaque shell configuration.
- Use command history for non-sensitive commands only.
- Use `command -v <tool>` to check whether a command is available.
- Use `type <command>` to determine whether a command resolves to an alias, function, or executable.
- Use shell completion only when provided by the installed tool/package and its official documentation.

Do not place access tokens, passwords, private keys, or cloud credentials in `.bashrc`, `.profile`, aliases, scripts, or command history.

### 4.4 Editor

Use the editor you can operate reliably. VS Code with WSL support is one option; terminal editors such as Vim or Nano are also sufficient. **[VERIFY]** current licensing and organization-use terms for desktop products such as Docker Desktop or editor extensions before using them in a professional setting.

For WSL, open the project from the Linux filesystem using the editor's documented WSL integration. Avoid editing Linux project files through a workflow that silently changes executable bits, symlinks, or line endings.

### 4.5 Git identity and repository safety

Check your Git configuration:

```bash
git config --get user.name
git config --get user.email
git status --short
```

- The first two commands print the configured identity if set; a missing value is not a command failure in every shell context.
- Run `git status --short` inside the repository directory to see uncommitted changes.
- Set identity only if you want it configured. Use a work-approved identity for work repositories.

Example configuration, run inside Ubuntu/WSL:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.invalid"
```

Replace the placeholders with an identity you control. These commands modify your user-level Git configuration; reverse them with `git config --global --unset user.name` or `git config --global --unset user.email` if needed. Do not use a real work email in a public repository unless policy permits it.

### 4.6 SSH key basics

SSH keys are used by some Git hosts and remote systems. Generate a key only if you need one and first check whether you already have an appropriate key.

```bash
ls -la "$HOME/.ssh"
```

If there is no suitable key, use the key-generation method documented by your Git host or OpenSSH. A common OpenSSH command is:

```bash
ssh-keygen -t ed25519 -C "your-email@example.invalid"
```

- **What it does:** creates a public/private key pair interactively.
- **Expected result:** a private key and matching `.pub` public key are created at the chosen path.
- **Security:** protect the private key, use a passphrase where appropriate, and never commit it. Only the public key is added to a Git host.
- **Rollback:** remove a key only after confirming it is not used by another service and you have a replacement if required.

Optional: signed Git commits can improve attribution and integrity workflows, but the exact setup depends on your chosen signing method and Git host. Follow the official Git and hosting-provider documentation; do not paste private signing material into the repository.

**Verify**

- [ ] Base package commands return version information.
- [ ] Git identity is intentional.
- [ ] SSH private keys, if any, are outside the repository.
- [ ] You can explain which files the package and Git commands changed.

**Rollback:** restore prior user-level Git configuration if needed. For package changes, inspect the exact package list before removing anything.

## 5. Phase 2 — Container runtime

Choose **one** primary path. Do not install Docker Engine inside WSL and Docker Desktop integration simultaneously without a specific reason and a clear plan for which daemon the CLI targets.

### 5.1 Choose a path

| Path | Use it when | Benefits | Trade-offs |
|---|---|---|---|
| A. Docker Engine inside WSL2 | You want a Linux-native engine inside the distribution and are comfortable managing its service | Direct Linux environment; useful for understanding daemon/service behavior | You manage the daemon and updates; systemd availability/configuration depends on the WSL setup |
| B. Docker Desktop with WSL integration | You already use Docker Desktop and its current terms permit your use | Integrated desktop workflow and documented WSL integration | Licensing terms may depend on usage/organization; product behavior and integration options can change. **[VERIFY]** |
| Alternative: Podman/rootless containers | You want to explore daemonless/rootless workflows or avoid Docker Engine's group model | Different security and runtime model | Some lab instructions and integrations may need adaptation; treat as Awareness until verified against module needs |

This roadmap's examples use the Docker CLI and Docker Engine-compatible behavior. If you choose Podman, document the compatibility differences instead of assuming every command and Kubernetes workflow is identical.

### 5.2 Path A — Docker Engine inside WSL2

Use the official **Docker Engine docs: Install on Ubuntu**. The repository configuration and key-verification details can change; follow the current official instructions for your Ubuntu release. Do not add an unofficial package repository or copy a key from a blog.

The official installation flow generally includes:

1. Remove or account for conflicting packages only after reviewing the official documentation and the packages installed on your system.
2. Add Docker's official apt repository and signing key using the exact current method documented by Docker.
3. Refresh apt metadata and install the engine and CLI packages named by the official instructions.
4. Enable/start the service using the supported service manager for your WSL configuration.
5. Verify the client and daemon before proceeding.

Do not paste a repository setup command from memory. Check the current Docker documentation for the exact repository/key commands, supported Ubuntu releases, and package names.

#### systemd versus manual daemon startup

WSL systemd support depends on WSL version and distribution configuration. **[VERIFY]** the current Microsoft Learn documentation for enabling systemd in WSL and the Docker documentation for the supported service-management approach.

- If systemd is enabled and supported in your distribution, use the documented service command and verify the service state.
- If systemd is not enabled, do not assume `systemctl` will work. Follow the current Docker and Microsoft documentation for a supported alternative.
- Avoid leaving a manually started daemon running in the background without understanding how it is stopped, restarted, and logged.

Check service state only after installing the engine:

```bash
systemctl is-active docker
```

- **Expected result:** `active` when systemd manages a running Docker service.
- **If systemd is not available:** this check is not applicable; follow the documented service path instead.

### 5.3 Path B — Docker Desktop with WSL integration

Install Docker Desktop only from the official Docker Desktop documentation. Review current licensing terms for your use case, especially for organizational use. **[VERIFY]** terms before relying on it as a long-term team standard; this guide does not provide legal advice.

High-level steps:

1. Install Docker Desktop using the official instructions for Windows.
2. Confirm its WSL 2 backend and resource settings using current documentation.
3. Enable integration for the intended Ubuntu distribution using Docker Desktop's current settings.
4. Open Ubuntu/WSL and verify that `docker` resolves to the intended CLI and can contact the expected daemon.
5. Avoid installing a second engine inside WSL unless you intentionally isolate and document both.

Run inside Ubuntu/WSL:

```bash
docker version
docker info
```

- `docker version` displays client and server information when the daemon is reachable.
- `docker info` reports daemon configuration and runtime details.
- **Expected result:** both client and server sections appear. If the server section is missing, the CLI cannot reach a daemon.

### 5.4 Docker group security

On a Linux Engine installation, the Docker documentation may instruct adding a user to the `docker` group to run Docker commands without `sudo`. Membership in this group can grant effectively root-level control of the host. Treat it as a security decision, not a harmless convenience.

- Prefer the documented security model that fits your machine and threat model.
- Do not add users to the group on a shared or managed machine without authorization.
- If you choose group membership, follow the current Docker docs and start a new login session before testing.
- To undo group membership, use the documented group-management command for your distribution; verify the exact user and group before changing it.
- Do not solve a socket permission problem by making the Docker socket world-writable.

### 5.5 Verify the runtime

Run inside the terminal where you will do the labs:

```bash
docker --version
docker version
docker run --rm hello-world
```

- `docker --version` checks the CLI.
- `docker version` checks client and daemon communication.
- `docker run --rm hello-world` pulls/runs a small test image if needed and removes the stopped container afterward.
- **Expected result:** the test prints a success message. It may require internet access to pull the image.

If the image is already cached, the test may not download anything. This is a smoke check, not a security assessment.

### 5.6 Inspect and clean up safely

```bash
docker system df
docker ps -a
docker image ls
```

These commands inspect disk use, containers, and images. They do not delete resources.

**Warning — destructive cleanup:** the following commands can remove stopped containers, unused networks, dangling images, and build cache. Review what is in use first; do not run them on a shared daemon or a machine holding work you need.

```bash
docker container prune
docker image prune
docker builder prune
```

Each prune command prompts for confirmation by default unless options change that behavior. Read the prompt before confirming. Avoid broad `docker system prune --all --volumes` cleanup unless you understand that it can delete unused images and volumes containing data.

**Verify**

- [ ] One runtime path is documented.
- [ ] `docker version` shows client and server information.
- [ ] `docker run --rm hello-world` succeeds.
- [ ] You understand the Docker group risk if using Docker Engine.
- [ ] You know how to inspect disk use before cleanup.

**Rollback:** stop the service or close the desktop runtime using its documented method. Uninstall only by following the official instructions for the path you chose; do not delete Docker data directories by guesswork.

## 6. Phase 3 — Kubernetes CLI toolchain

This phase installs clients, not a cluster. Create clusters in [local-lab-kind-minikube-and-localstack.md](local-lab-kind-minikube-and-localstack.md).

### 6.1 `kubectl` — Core

**Purpose:** communicate with Kubernetes API servers and inspect/manage cluster resources.

Install `kubectl` using **Kubernetes docs: Install Tools** for your platform. Use the official package repository or the documented binary-download procedure. If using a binary download, verify it using the checksum/signature method documented by Kubernetes; do not invent a checksum command or skip verification.

Kubernetes clients and clusters have a supported version-skew relationship. Check the current Kubernetes documentation for the exact rule and the cluster's version before choosing a client version. Do not assume the newest client is compatible with every cluster.

Verify:

```bash
kubectl version --client
```

Expected result: client version information is printed without attempting to connect to a cluster. Record the installed version in `versions.txt`.

### 6.2 `helm` — Core

**Purpose:** manage Kubernetes application packages called charts.

Install using **Helm docs: Installing Helm** and select the official method appropriate for your platform. Avoid third-party shell scripts and package sources that you have not reviewed.

Verify:

```bash
helm version
```

Expected result: Helm version/build information is printed. Record it in `versions.txt`.

### 6.3 `kustomize` — Core concept, separate CLI optional

**Purpose:** compose and customize Kubernetes YAML manifests using bases, overlays, and patches.

Kustomize functionality is also available through `kubectl kustomize`. A separate `kustomize` executable is optional unless a module or workflow needs it. Install a standalone binary only by following the official Kustomize project instructions and its documented integrity checks.

Verify the built-in command:

```bash
kubectl kustomize --help
```

Expected result: help text is displayed. Record a separate standalone version only if you installed the standalone binary.

### 6.4 `kubectx` / `kubens` — Optional

**Purpose:** make switching Kubernetes contexts and namespaces more convenient.

They are convenience tools, not requirements for the stage. Install only from the official project documentation or a trusted distribution package whose provenance you can verify. The underlying safe habits remain important even if these tools are installed.

Baseline commands that do not require these tools:

```bash
kubectl config get-contexts
kubectl config current-context
kubectl get namespaces
```

Expected result: configured contexts, the current context if set, and namespaces if a reachable cluster is configured. Before any change command, confirm the context and namespace.

### 6.5 `k9s` — Optional

**Purpose:** provide a terminal UI for inspecting Kubernetes resources.

Install using the official K9s project documentation and its current integrity instructions. Do not make K9s a prerequisite for learning `kubectl`; the raw CLI is necessary for scripts and debugging.

Verify:

```bash
k9s version
```

Expected result: version output. If the installed release uses a different documented syntax, follow its official help output rather than forcing this example.

**Verify**

- [ ] `kubectl version --client` succeeds.
- [ ] `helm version` succeeds.
- [ ] `kubectl kustomize --help` succeeds.
- [ ] Optional tools are explicitly recorded as installed or deferred.
- [ ] No cluster was created in this phase.

**Rollback:** remove only the CLI binaries/packages you installed, using the same official installation method. Do not delete kubeconfig files merely to uninstall a CLI.

## 7. Phase 4 — Infrastructure as Code and cloud CLIs

### 7.1 OpenTofu versus Terraform

Terraform and OpenTofu are related declarative Infrastructure as Code tools with overlapping workflows, but their governance, licensing, release processes, and compatibility must be checked against current official sources. This guide does not make legal claims or assume perfect compatibility.

**Proposed Stage 2E convention:** use **OpenTofu** for the primary hands-on workflow, and learn Terraform's relationship and migration/compatibility considerations at Awareness level. This is a repository convention proposal, not a claim that OpenTofu is universally preferable. Before committing it, reconcile it with `production-devops-tooling-map.md` and any existing project files. **[VERIFY]** current OpenTofu/Terraform documentation and governance notices.

Install OpenTofu using **OpenTofu documentation: Install** and its official package/binary method. If the method uses a repository key or downloaded binary, follow the current documented key/checksum/signature steps exactly. Do not add an unverified repository or use `curl | sudo bash`.

Verify:

```bash
tofu version
```

Expected result: the installed OpenTofu version is printed. Record it in `versions.txt`.

Do not run `tofu apply` against a real cloud account as a setup test. Use a local-only example or the module-specific LocalStack workflow. Review every plan before applying it.

### 7.2 AWS CLI v2 — Core for later cloud-facing labs

**Purpose:** configure and invoke AWS APIs from the command line.

Install AWS CLI v2 using **AWS CLI docs: Installing or updating the latest version of the AWS CLI** for your OS and architecture. Use the official installer and the integrity verification method documented by AWS. Do not use a random mirror or invent a checksum command.

Verify:

```bash
aws --version
```

Expected result: the command identifies AWS CLI v2. Record the version in `versions.txt`.

You do not need cloud credentials to complete the local-only parts of this workstation setup. Do not run `aws configure` merely to make the command work.

### 7.3 AWS credentials and profiles

When a later lab genuinely requires AWS access:

- Follow [free-tier-cloud-account-and-cost-safety.md](free-tier-cloud-account-and-cost-safety.md) first.
- Prefer a supported short-lived credential or role-based flow where available.
- If a named profile is necessary, use a profile name that identifies the lab and environment, not a secret.
- Never commit `~/.aws`, credential files, tokens, private keys, or screenshots that expose credentials.
- Do not put credentials in shell command arguments, `.bashrc`, scripts, issue reports, or logs.
- Use `aws sts get-caller-identity --profile <profile-name>` only after the profile has been intentionally configured; it identifies the authenticated principal but does not prove that the permissions are appropriately restricted.
- Verify the active account and region before any mutating operation. Never assume a profile name alone proves the account is safe.

### 7.4 `awscli-local` and LocalStack CLI — Optional

These tools can simplify some LocalStack interactions, but their packaging and supported commands may change. **[VERIFY]** current LocalStack documentation for installation, edition-dependent features, and supported service coverage. Do not install them just to complete the base workstation.

Use [local-lab-kind-minikube-and-localstack.md](local-lab-kind-minikube-and-localstack.md) for the actual local AWS-emulation workflow.

### 7.5 IaC linters — Optional

- **TFLint:** checks Terraform configuration using the selected tool and plugins. Confirm the current official installation method and compatibility before use.
- **Checkov:** scans IaC and related configuration for selected policy/security issues. Install from the official Checkov documentation; rule coverage and results need review.
- These are additional feedback, not a substitute for reviewing a plan, state, provider configuration, permissions, or destructive changes.

Verify optional installations using their official documented version command. Record only tools you actually installed.

**Verify**

- [ ] `tofu version` succeeds.
- [ ] `aws --version` identifies AWS CLI v2.
- [ ] No cloud account or paid resource was required for the base setup.
- [ ] Credential files are outside the repository and excluded from version control.
- [ ] Terraform/OpenTofu convention has been reconciled with the tooling map before the repo standard is finalized.

**Rollback:** remove optional CLIs using the same official installation method. Do not delete state files or credential files as a generic rollback step; inspect and back up data first.

## 8. Phase 5 — Supporting CLIs

The table distinguishes Core tools from optional diagnostics. Package names can differ by distribution; verify the package mapping for your supported OS before installing.

| Tool | Scope | Purpose | Verification |
|---|---|---|---|
| `jq` | Core | Query and transform JSON | `jq --version` |
| `yq` | Optional | Process YAML using a command-line interface | Follow the selected project's official version/help command; several unrelated tools use the name `yq` |
| `dig` / `nslookup` | Core | Diagnose DNS resolution | `dig example.com` or `nslookup example.com` if installed and network access exists |
| `netcat` (`nc`) | Optional | Test basic TCP connectivity | `nc -h` or the installed implementation's documented help |
| `openssl` | Core | Inspect certificates and perform TLS-related diagnostics | `openssl version` |
| `ss` | Core | Inspect local sockets and listening ports | `ss -lnt` |
| `tcpdump` | Awareness/Optional | Capture packets for network troubleshooting | `tcpdump --version` where supported; packet capture may require elevated privileges |
| `strace` | Awareness/Optional | Trace system calls for process-level diagnosis | `strace -V` |

### 8.1 Install baseline network tools

Some packages are already installed by Phase 1. On Ubuntu, `dnsutils` commonly provides `dig`/`nslookup`, `netcat-openbsd` provides `nc`, and `iproute2` provides `ss`; verify package names against the current Ubuntu package index for your release.

Install only what is missing. Example, inside Ubuntu/WSL; `sudo` is required because apt changes system package state:

```bash
sudo apt install --yes dnsutils netcat-openbsd iproute2 openssl
```

Verify:

```bash
command -v dig
command -v nslookup
command -v nc
command -v ss
openssl version
```

Expected result: each installed command has a path and OpenSSL prints version information.

### 8.2 Optional YAML CLI

There are multiple tools named `yq` with different syntax. Select the intended project from the official documentation before installation. Do not copy a command written for one implementation and assume it works for another.

### 8.3 Debug toolbox

- Start with `getent hosts`, `ss`, `curl -v`, and application logs before packet capture.
- Use `tcpdump` only when you understand the interface, capture scope, and privacy implications.
- `tcpdump` may require `sudo` to capture packets. Elevated capture can expose sensitive traffic; limit capture duration and protect output files.
- Use `strace` when ordinary logs and process inspection are insufficient. It can expose file paths, arguments, and other sensitive operational details.
- Avoid capturing traffic from networks or systems you do not own or have permission to diagnose.

**Verify**

- [ ] `jq` and `openssl` work.
- [ ] DNS and socket tools are available when needed.
- [ ] Optional tools are marked as deferred if not required.
- [ ] No packet capture was run against third-party traffic.

**Rollback:** remove only optional packages you installed and no longer need, after reviewing the package manager's removal plan.

## 9. Phase 6 — Security and supply-chain CLIs

Install these only when the corresponding module begins. Their installation methods, signing flows, database behavior, and supported artifact types can change; check the current official project documentation.

| Tool | Scope | Purpose | Safe verification approach |
|---|---|---|---|
| Trivy | Core for M01/M12 | Scan images and selected files/configurations for known issues | Follow official install instructions, then run the documented version command |
| Syft | Core for SBOM work | Generate a software bill of materials | Follow official install and integrity instructions; run the documented version command |
| cosign | Awareness until signing lab | Sign/verify container artifacts and related attestations | Follow Sigstore/cosign docs; use a local test artifact and never use production signing credentials in a learning lab |
| pre-commit | Optional | Run configured checks before commits | Install using the project's official docs and run its documented version check |
| Checkov / TFLint | Optional | Scan IaC for selected policy or configuration issues | Use official install instructions and documented version/help commands |

Do not treat `--version` as a security verification. For downloaded binaries, verify checksums or signatures exactly as described by the project's official release instructions. If you cannot establish the integrity method, stop and consult the official documentation rather than guessing.

### 9.1 Image scanner smoke check

After installing Trivy, use the exact current command from the official Trivy documentation. A version check is a low-risk first check; an image scan may download vulnerability databases and an image, so it needs network access and disk space. Treat scan results as triage signals, not a guarantee of safety.

### 9.2 SBOM generator smoke check

After installing Syft, run its documented version command, then generate an SBOM for a small local test image using the official usage example. Confirm the output is readable and record the command and output format in the lab notes.

### 9.3 Signing tool smoke check

After installing cosign, first use the official documentation's local/test signing and verification workflow. Do not create or upload production keys for this exercise. Keep test key material out of Git and delete it only after confirming the lab no longer needs it.

### 9.4 Pre-commit smoke check

After installing pre-commit, run its documented version command and use a small test repository or the actual repository only after reviewing `.pre-commit-config.yaml`. Hooks may modify files or download environments; inspect the proposed configuration before running them across a repository.

**Verify**

- [ ] Security tools are installed only when their module needs them.
- [ ] Binary integrity was checked according to official documentation where applicable.
- [ ] Test keys and scanner output containing sensitive details are not committed.
- [ ] No production credentials were used.

**Rollback:** remove optional binaries/packages using their documented install method. Before deleting test keys or scanner databases, confirm they are not needed for another lab.

## 10. Verification gate — the `lab-doctor.sh` script

The doctor script checks the workstation baseline without installing packages, changing configuration, creating cloud resources, or requiring `sudo`. It reports PASS/FAIL for required checks and returns a nonzero exit code if any required check fails. Optional tools are reported as SKIP if absent.

### 10.1 Create the script

Create `lab-doctor.sh` in the repository root or a local tools directory. Read the script before running it.

```bash
#!/usr/bin/env bash
# Read-only Stage 2E workstation checks. No sudo and no system changes.
set -u

failures=0

pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1"; failures=$((failures + 1)); }
skip() { printf 'SKIP: %s\n' "$1"; }

check_command() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    pass "$name is available ($(command -v "$name"))"
  else
    fail "$name is missing"
  fi
}

check_version() {
  local name="$1"
  shift
  if command -v "$name" >/dev/null 2>&1; then
    if "$@" >/dev/null 2>&1; then
      pass "$name version command works"
    else
      fail "$name is installed but its version command failed"
    fi
  else
    fail "$name is missing"
  fi
}

printf '%s\n' 'Stage 2E lab doctor — read-only checks'

check_version git git --version
check_version curl curl --version
check_version jq jq --version
check_version docker docker --version
check_version kubectl kubectl version --client
check_version helm helm version
check_version tofu tofu version
check_version aws aws --version

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    pass 'Docker daemon is reachable'
  else
    fail 'Docker daemon is not reachable (check selected runtime path)'
  fi
else
  skip 'Docker daemon check skipped because docker CLI is missing'
fi

if command -v git >/dev/null 2>&1; then
  if git config --get user.name >/dev/null 2>&1 &&
     git config --get user.email >/dev/null 2>&1; then
    pass 'Git user.name and user.email are configured'
  else
    fail 'Git identity is incomplete (configure intentionally or adapt this check)'
  fi
else
  skip 'Git identity check skipped because git is missing'
fi

if command -v kubectl >/dev/null 2>&1; then
  if kubectl version --client >/dev/null 2>&1; then
    pass 'kubectl client responds'
  else
    fail 'kubectl client check failed'
  fi
else
  skip 'kubectl client check skipped because kubectl is missing'
fi

printf '\nFailures: %s\n' "$failures"
if [ "$failures" -eq 0 ]; then
  printf '%s\n' 'Overall result: PASS'
  exit 0
fi

printf '%s\n' 'Overall result: FAIL — fix required checks before starting cluster labs'
exit 1
```

### 10.2 Review and run it

Inside Ubuntu/WSL, inspect the script:

```bash
sed -n '1,240p' lab-doctor.sh
```

Run it without changing permissions:

```bash
bash lab-doctor.sh
```

This invokes Bash directly and does not require `chmod`. If you later choose to execute it as `./lab-doctor.sh`, you must first set its executable bit; that changes file metadata but not system configuration.

**Important:** the doctor is a baseline gate, not a full integration test. It deliberately does not create a Kubernetes cluster, make cloud API calls, install dependencies, or verify that every optional tool is installed. If you intentionally selected Docker Desktop/WSL integration, `docker info` should still work from the intended terminal. If you intentionally defer AWS or IaC tools, edit the script and mark those checks optional rather than silently treating missing tools as success.

### 10.3 Manual verification checklist

| Check | Command | Expected result |
|---|---|---|
| OS identity | `cat /etc/os-release` | Supported Linux distribution details |
| Disk space | `df -h /` | Root filesystem has room for the planned lab |
| Git | `git --version` | Git version prints |
| Git identity | `git config --get user.name` and `git config --get user.email` | Intentional identity is configured |
| Container CLI | `docker --version` | Client version prints |
| Container daemon | `docker info` | Server/daemon details print |
| Test container | `docker run --rm hello-world` | Test image runs and prints success |
| Kubernetes client | `kubectl version --client` | Client information prints without a cluster |
| Helm | `helm version` | Version information prints |
| Kustomize built into kubectl | `kubectl kustomize --help` | Help output prints |
| OpenTofu | `tofu version` | Version information prints |
| AWS CLI | `aws --version` | AWS CLI v2 is identified |
| Doctor script | `bash lab-doctor.sh` | PASS/FAIL output and correct exit code |

**Verify**

- [ ] The script has been reviewed before execution.
- [ ] The script exits zero only when all required checks pass.
- [ ] Any intentional deferrals are documented rather than hidden.
- [ ] No system changes or cloud resources were created by the script.

**Rollback:** the script is read-only. Remove the file if you do not want to keep it; do not run an uninstall or reset command to undo it.

## 11. Proposed lab conventions (adopt or adjust)

The actual repository conventions were not supplied as authoritative policy. The following are **proposals**, not claims about existing repository rules. Adopt them explicitly and keep them consistent across modules.

### 11.1 Naming

- Prefix disposable local clusters with `stage2e-` or `lab-`, for example `stage2e-ops`.
- Prefix namespaces for learning exercises with `lab-` where Kubernetes naming rules permit it.
- Use descriptive names for repositories, branches, and files; avoid embedding credentials or personal information in names.
- For cloud resources, use a tag such as `Project=stage2e-lab` and a `ManagedBy=learner` tag where the provider/resource supports tags. Use a `lab-` prefix for resource names where allowed.
- Treat naming/tagging as identification, not access control. Not all resources support the same tags or naming formats.

### 11.2 Git and `.gitignore`

At minimum, review whether the repository should ignore:

```gitignore
# Local environment and credentials
.env
.env.*
!.env.example
.aws/
.ssh/
*.pem
*.key
kubeconfig
kubeconfig.*
.kube/

# IaC state and local working data
*.tfstate
*.tfstate.*
.terraform/
.tofu/
crash.log
crash.*.log
*.tfplan
*.plan

# Local outputs and temporary files
*.log
*.tmp
.DS_Store
```

This is a starting proposal, not a complete universal `.gitignore`. Check whether any ignore rule would hide a legitimate, non-secret project file. Never commit credentials, private keys, real kubeconfigs, Terraform/OpenTofu state, or plan files without a deliberate security review. State may contain sensitive values even if the source configuration does not.

### 11.3 Kubeconfig and current-context safety

- Keep personal kubeconfig data outside the repository.
- Do not paste kubeconfig contents into issues, screenshots, or logs.
- Before applying or deleting resources, run:

```bash
kubectl config current-context
kubectl config get-contexts
kubectl get namespaces
```

- If the current context is not the intended lab cluster, stop and switch only after checking the context list.
- Never assume a context name proves the target is disposable; inspect the cluster identity and configuration.

### 11.4 Environment variables

Use environment variables for non-secret configuration such as lab names or local endpoints. For secrets, prefer an appropriate credential manager or short-lived identity flow; do not export secrets into shell startup files.

Example for a non-secret label, in the current shell only:

```bash
export STAGE2E_LAB_NAME="stage2e-lab"
printf '%s\n' "$STAGE2E_LAB_NAME"
```

Expected result: the label is printed. It disappears when the shell exits unless you intentionally persist it. Do not place tokens or passwords in example values.

### 11.5 Version record

Create a text file in the repository that records the tool versions you actually installed. It must contain version output only—never credentials or environment dumps.

Example format:

```text
Recorded on: YYYY-MM-DD
OS: paste the relevant /etc/os-release identification
Git: output of git --version
Docker CLI/Server: output of docker version
kubectl: output of kubectl version --client
Helm: output of helm version
OpenTofu: output of tofu version
AWS CLI: output of aws --version
```

Replace placeholders with actual output. If you choose a different tool, record that choice and the reason. Do not claim a tool is installed because it appears in this template.

**Verify**

- [ ] Naming and ignore rules have been reviewed.
- [ ] No state, credential, private-key, or kubeconfig files are tracked.
- [ ] Current context is checked before cluster mutations.
- [ ] `versions.txt` records actual local tool output.

**Rollback:** revert only the convention changes you intentionally made. Before removing ignore rules, inspect `git status` and confirm no sensitive files would become trackable.

## 12. Time-saving and quality-of-life

### 12.1 Use a command pattern for safe inspection

Prefer a sequence that observes before it changes:

1. Inspect current context, state, or disk use.
2. Read the planned change.
3. Apply the smallest scoped change.
4. Verify the result.
5. Record rollback steps and evidence.

For containers, inspect with `docker ps -a`, `docker image ls`, and `docker system df` before pruning. For IaC, inspect the plan before applying. For Kubernetes, inspect context and namespace before mutations.

### 12.2 Use a project-local environment file carefully

A `.env.example` can document required non-secret variable names. Keep actual `.env` files ignored and never use real secrets in example files. If an application requires secrets, document how to obtain them securely rather than storing them in the repository.

### 12.3 Keep shell aliases transparent

Safe convenience aliases may shorten read-only commands, but avoid aliases that hide destructive flags, suppress confirmation, or change the meaning of `rm`, `kubectl`, `tofu`, `terraform`, or `docker`. If a command is dangerous, prefer writing the full command and reading it before execution.

### 12.4 Record evidence as you learn

For each module, capture:

- Tool versions and environment details relevant to reproduction.
- The exact command that was run, excluding secrets.
- Expected versus observed output.
- Any failure and the verified correction.
- Cleanup/rollback performed.
- What the local simulation does not prove about production.

**Verify**

- [ ] The repository contains useful evidence, not credentials or machine-specific secrets.
- [ ] Aliases do not hide destructive behavior.
- [ ] Repeated commands are understandable to a reviewer.

**Rollback:** remove convenience aliases or local environment files if they create ambiguity. Preserve learning notes and evidence that do not contain sensitive data.

## 13. Troubleshooting

Use this sequence: inspect the exact error, check the relevant service/context, confirm DNS/network access, check disk and permissions, and then change one thing at a time. Do not disable TLS verification, package signature checks, or security controls to make a setup step pass.

| Symptom | Possible cause | Conservative fix |
|---|---|---|
| Docker CLI works but daemon does not | Engine is stopped, Docker Desktop integration is disabled, or CLI targets a different daemon | Check the selected runtime path; inspect `docker context ls`, `docker context show`, `docker info`, and the documented service state |
| `systemctl` does not work in WSL | systemd is not enabled or supported in the current configuration | Check current Microsoft Learn guidance; do not assume service-management behavior |
| Permission denied on Docker socket | User permissions/group membership do not match the chosen engine setup | Check socket ownership and the official Docker guidance; do not make the socket world-writable |
| `kubectl` says connection refused | No cluster is running, current context points to a stopped endpoint, or API server is unreachable | Run `kubectl config current-context` and `kubectl config get-contexts`; create/start the lab cluster only in the cluster guide |
| `kubectl` targets an unexpected cluster | Wrong context or kubeconfig selected | Stop before making changes; inspect contexts and explicitly select the intended lab context |
| DNS fails inside WSL | Temporary resolver issue, VPN/proxy configuration, or network policy | Compare Windows and WSL resolution; inspect `/etc/resolv.conf` without overwriting it blindly; follow current Microsoft guidance for the environment |
| HTTPS/TLS requests fail | Clock skew, proxy interception, missing CA certificates, or a genuine certificate problem | Check system time and CA package state; follow organization proxy policy; never bypass certificate validation as a fix |
| apt repository signature/key error | Incorrect or expired repository key, wrong repository entry, or metadata issue | Stop and follow the official repository instructions; do not use insecure apt flags or disable signature checking |
| Slow file operations | Active project resides on a Windows-mounted path or filesystem contention | Move/copy the working tree into the Linux filesystem after checking Git status and making a backup |
| Disk usage grows unexpectedly | Image layers, build cache, volumes, or cluster data accumulated | Inspect `docker system df`, `docker ps -a`, and image/volume lists; remove only reviewed disposable resources |
| WSL becomes memory constrained | Too many clusters/services or configuration that limits available memory | Stop unused workloads; inspect resource use; verify current WSL configuration docs before changing limits |
| `kubectl` version-skew warning | Client and cluster versions are outside the currently supported relationship | Check Kubernetes version-skew documentation and select a compatible client version |
| AWS CLI reports no credentials | No profile or identity has been configured | For local-only work, leave it unconfigured; for a real cloud lab, follow the cost-safety and official identity instructions |
| OpenTofu provider download fails | Network/proxy issue, provider registry issue, or configuration mismatch | Inspect the full error and network path; do not disable TLS or blindly delete lock/state files |
| `docker run hello-world` cannot pull | Network/DNS/proxy issue or registry access issue | Check DNS and HTTPS, inspect the full error, and retry only after connectivity is understood |
| Port is already in use | Another process or container owns the port | Inspect with `ss -lntp` where permitted and `docker ps`; change the lab port deliberately instead of killing unknown processes |
| `yq` syntax behaves unexpectedly | A different `yq` implementation is installed | Check its official documentation and version; do not assume similarly named tools share syntax |

### 13.1 Safe diagnostic commands

These are read-only or observational in ordinary use:

```bash
command -v docker
docker context ls
docker context show
docker info
kubectl config current-context
kubectl config get-contexts
df -h /
free -h
ss -lnt
getent hosts ubuntu.com
date -Is
```

Some commands may reveal hostnames, network details, usernames, or environment information. Redact those details before sharing output publicly.

**Verify**

- [ ] The cause is supported by observed output rather than guesswork.
- [ ] Security checks were not disabled.
- [ ] Any cleanup or configuration change has a documented rollback.
- [ ] Secrets and sensitive diagnostics were not pasted into public issues.

**Rollback:** undo only the specific change that caused the regression, using the saved prior configuration or official uninstall/recovery guidance. If the root cause is uncertain, stop and gather more evidence.

## 14. Maintenance, upgrade, and rollback

### 14.1 Record versions

After setup, record actual versions in `versions.txt`. Refresh the record after intentional upgrades. Do not record a version from a tutorial as if it were installed on your machine.

Useful checks include:

```bash
git --version
docker version
kubectl version --client
helm version
tofu version
aws --version
```

Some tools have separate client/server versions. Record both where that distinction affects compatibility.

### 14.2 Check upstream changes

Before upgrading or adopting a tool:

1. Read the official release notes and installation/upgrade instructions.
2. Check security advisories and supported platform compatibility.
3. Check Kubernetes client/server compatibility where relevant.
4. Back up configuration and valuable local state.
5. Upgrade one layer at a time.
6. Run the doctor script and the relevant module smoke tests.
7. Record the result and any rollback steps.

For tools whose licence, governance, maintenance status, or supported APIs may change, review those details directly from the project's own sources. Do not rely solely on old blog posts or search snippets.

### 14.3 Rollback principles

- Prefer an official downgrade/rollback method when the project documents one.
- Do not assume that downgrading a CLI also rolls back a cluster, provider, schema, state file, or database.
- Back up important local state before upgrades.
- Keep disposable lab resources disposable; do not store irreplaceable work only inside a container or cluster.
- Do not delete Terraform/OpenTofu state or Kubernetes data directories as a generic troubleshooting step.
- If a tool upgrade changes state or configuration formats, stop and follow its migration guidance.

**Verify**

- [ ] `versions.txt` matches the actual installed toolchain.
- [ ] Release notes/security advisories were checked before intentional upgrades.
- [ ] Important notes and project files are backed up.
- [ ] Rollback steps account for data and state, not just binaries.

**Rollback:** follow the specific tool's documented procedure. If there is no documented safe downgrade path, restore from a verified backup or rebuild the disposable lab from source rather than deleting state blindly.

## 15. Uninstall and clean reset

There is no single safe “reset everything” command. Uninstall only the components you installed and confirm whether local data must be preserved.

### 15.1 Before uninstalling

- Commit or back up learning notes and project files.
- Check Git status for uncommitted work.
- Identify whether containers or volumes hold data you need.
- Identify which Kubernetes clusters and contexts are disposable.
- Back up IaC state only using a method appropriate to the backend and security requirements.
- Confirm you are not operating on a shared machine or daemon.

### 15.2 Remove individual tools

Use the same official method used to install the tool. For apt-managed packages, inspect the installed package and proposed removal before confirming. For manually downloaded binaries, remove only the binary path you installed and verified; do not delete broad directories based on a guessed location.

### 15.3 Container cleanup

**Warning — destructive:** pruning containers, images, build cache, and volumes can remove data. Inspect first:

```bash
docker ps -a
docker image ls
docker volume ls
docker system df
```

Remove only resources you have identified as disposable. Do not run broad volume pruning on a machine with data you have not backed up. A container being stopped does not mean its volume data is unimportant.

### 15.4 Local Kubernetes cleanup

Use the cluster tool's official delete command for the named disposable cluster, after confirming the cluster name and that it contains no data you need. This guide intentionally does not provide a generic cluster-delete command because the right command depends on whether you used kind, minikube, or another tool.

### 15.5 WSL distribution reset

Unregistering a WSL distribution is destructive and can delete its filesystem. Do not use `wsl --unregister` as a routine cleanup step. If you truly intend to remove a distribution, follow current Microsoft Learn guidance, verify the exact distribution name, and back up its contents first.

**Verify**

- [ ] Valuable work is backed up.
- [ ] Resource names and target contexts were checked before deletion.
- [ ] No broad prune/unregister command was used without a deliberate data-loss decision.
- [ ] You can rebuild the disposable lab from documented steps.

**Rollback:** deletion may be irreversible without a backup. Treat cleanup commands as destructive operations and verify targets before confirmation.

## 16. Security checklist for your workstation

- [ ] Keep OS and tools supported; apply security updates through official channels.
- [ ] Install tools from official project documentation or trusted distribution repositories.
- [ ] Verify binary checksums/signatures when the project documents them.
- [ ] Never use unreviewed `curl | sudo bash` commands.
- [ ] Review every command that uses `sudo`; understand what it changes and how to undo it.
- [ ] Understand the security implications of Docker group membership.
- [ ] Never commit passwords, API tokens, private keys, cloud credential files, or real kubeconfigs.
- [ ] Keep `.env` files and IaC state/plan files out of Git unless an explicit security review approves a safe, non-sensitive artifact.
- [ ] Prefer short-lived credentials or workload identity over long-lived cloud keys when supported.
- [ ] Use least-privilege cloud identities and verify account/region before mutating operations.
- [ ] Keep local clusters and test resources clearly named and disposable.
- [ ] Check current Kubernetes context before applying or deleting resources.
- [ ] Avoid sharing screenshots or logs that reveal credentials, hostnames, IPs, account IDs, or private repository details.
- [ ] Lock the workstation when unattended and follow device encryption and backup policy.
- [ ] Back up learning notes and configuration, but do not back up secrets to an unapproved destination.
- [ ] Use vulnerability and SBOM tools as evidence for triage, not as guarantees of safety.
- [ ] Confirm cloud teardown and billing safeguards in the sibling cost-safety guide before using a real account.

## 17. Reference Sources

Use the current official documentation for your OS, tool, and selected installation method. Source names below are provided for lookup; verify current pages and commands rather than relying on copied snippets.

### Windows and WSL

- Microsoft Learn: Install WSL.
- Microsoft Learn: WSL basic commands.
- Microsoft Learn: WSL configuration (`.wslconfig` and per-distribution settings).
- Microsoft Learn: Run Linux GUI apps and editor integration, if relevant.

### Linux and base packages

- Ubuntu Documentation.
- Ubuntu package documentation and package index.
- Git Documentation.
- OpenSSH Manual Pages.
- GNU Bash Manual.

### Containers

- Docker Engine Documentation: Install on Ubuntu.
- Docker Documentation: Post-installation steps for Linux.
- Docker Desktop Documentation: WSL 2 backend and WSL integration.
- Podman Documentation.

### Kubernetes and packaging

- Kubernetes Documentation: Install Tools.
- Kubernetes Documentation: Version Skew Policy.
- Helm Documentation: Installing Helm.
- Kustomize Documentation.
- kubectx/kubens project documentation.
- K9s project documentation.

### Infrastructure as Code and cloud

- OpenTofu Documentation: Installation.
- Terraform Documentation and current HashiCorp licensing/governance notices.
- AWS CLI Documentation: Install, update, and verify.
- LocalStack Documentation.
- TFLint Documentation.
- Checkov Documentation.

### Supporting and security tools

- jq Documentation.
- The selected yq project's official documentation.
- OpenSSL Documentation.
- Nmap/ncat or netcat implementation documentation, as applicable.
- tcpdump and strace manual pages.
- Trivy Documentation.
- Syft Documentation.
- Sigstore/cosign Documentation.
- pre-commit Documentation.

---

**Maintenance note:** This file is a setup baseline, not a substitute for current official installation instructions. Any `[VERIFY]` item must be checked against the named authoritative source before the associated change is made.
