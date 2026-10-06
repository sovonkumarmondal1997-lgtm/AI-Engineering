# Docker Desktop, WSL2, and Platform Differences

## Learning Objectives

By the end of this module, you should be able to:

- Explain how Docker operates natively on Linux.
- Explain the Linux VM/backend model used by Docker Desktop on Windows and macOS.
- Explain Docker Desktop's role and resource settings.
- Understand Docker Desktop organisational licensing considerations.
- Recognise Podman, Colima, and Rancher Desktop as alternative container runtimes.
- Explain WSL2 architecture and why Linux-heavy projects generally belong in the WSL2 Linux filesystem.
- Understand why `/mnt/c` can be slower for Linux-heavy Data Engineering workloads.
- Diagnose filesystem permission differences.
- Configure WSL2 memory, CPU, and swap at a practical level.
- Understand `.wslconfig` and why WSL may need restarting after changes.
- Diagnose CRLF/LF line-ending failures.
- Configure Git/editor line endings for Linux-oriented projects.
- Troubleshoot host/container/WSL2 networking and `localhost` assumptions.
- Use `host.docker.internal` where supported and appropriate.
- Explain host-networking differences across platforms.
- Understand ARM64, amd64, multi-architecture images, and emulation.
- Diagnose file-watching and bind-mount performance problems.
- Understand clock drift after VM sleep and its effect on tokens and time-sensitive services.
- Understand Docker Desktop/WSL2 virtual-disk reclamation conceptually.
- Write Docker lab instructions that work across Linux, Windows/WSL2, macOS Intel, and Apple Silicon.

---

## Why Platform Differences Matter

Docker provides a strong level of application-environment portability, but it does not erase the behavior of the host operating system, filesystem, CPU architecture, or virtualization layer.

The important distinction is:

```text
Application portability
        ≠
Identical host-platform behavior
```

A useful model is:

```text
Your application
      ↓
Container
      ↓
Docker Engine / Runtime
      ↓
Host operating system
      ↓
CPU / Memory / Filesystem / Network
      ↓
Physical machine
```

The container can standardize:

- application dependencies;
- Linux userspace;
- environment variables;
- application filesystem layout;
- application startup behavior.

But the host platform can still influence:

- filesystem performance;
- bind mounts;
- permissions;
- networking;
- available memory;
- CPU architecture;
- file-change notifications;
- virtualization;
- clock behavior;
- Docker storage;
- resource limits.

This matters directly to Data Engineering workloads such as:

```text
PostgreSQL
Kafka
MinIO
Redis
Python pipelines
Spark
Airflow
Docker Compose
```

The same Compose file can therefore be functionally correct on several platforms while producing noticeably different performance or troubleshooting symptoms.

---

## Prerequisites

This module is the final topic of:

```text
Stage 2B
→ Gap Module G1
→ Docker Essentials for Data Labs
→ Phase D — Keeping Your Machine Healthy
→ Topic 10
```

Dependency chain:

```text
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10
```

You should already understand:

- containers and images;
- Docker networks and ports;
- volumes and persistence;
- environment variables;
- container logs and troubleshooting;
- Docker Compose;
- resource limits;
- disk cleanup and housekeeping.

Topic 04 is especially relevant for storage and bind-mount behavior. Topic 08 is relevant for CPU and memory limits. Topic 09 is relevant for Docker Desktop virtual-disk storage.

---

# 1. Docker Across Operating Systems

## 1.1 Linux

On Linux, Docker can run directly on the Linux host:

```text
Linux host
    ↓
Docker Engine
    ↓
Containers
```

Docker relies on Linux kernel facilities such as:

- namespaces;
- cgroups;
- Linux networking;
- Linux filesystem capabilities.

The practical result is that there is no requirement for a separate Linux VM merely to run ordinary Linux containers on a native Linux Docker Engine installation.

---

## 1.2 Windows

A typical Windows Docker Desktop architecture is conceptually:

```text
Windows
   ↓
WSL2 / Linux environment
   ↓
Docker Desktop integration
   ↓
Docker Engine
   ↓
Linux containers
```

Linux containers require a Linux kernel environment. WSL2 provides a lightweight Linux environment that Docker Desktop can integrate with.

The exact integration and networking details depend on Docker Desktop and WSL2 configuration.

---

## 1.3 macOS

A typical macOS architecture is:

```text
macOS
   ↓
Docker Desktop / Linux virtualization
   ↓
Linux environment
   ↓
Docker Engine
   ↓
Linux containers
```

macOS does not provide the Linux kernel used by ordinary Linux containers. Docker Desktop therefore provides the Linux environment required to run them.

---

# 2. Linux Docker Architecture

Linux users should think in terms of:

```text
Application
    ↓
Container
    ↓
Docker Engine
    ↓
Linux kernel
    ↓
Hardware
```

### Why this matters

Because the container and host share the Linux kernel environment more directly, some filesystem and networking operations can behave differently from Docker Desktop environments.

This does not mean Linux is automatically faster for every workload. It means the virtualization and filesystem boundary is different.

---

## 2.1 Kernel concepts in practical terms

### Namespaces

Namespaces provide isolation for things such as:

- processes;
- networking;
- mount points.

### cgroups

Control groups provide resource-management mechanisms for:

- CPU;
- memory;
- other resource controls.

You do not need to become a Linux kernel developer for this module.

The operational takeaway is:

> Native Linux Docker has a different architectural path from Docker Desktop running a Linux environment on Windows or macOS.

---

# 3. Windows + WSL2 Docker Architecture

## 3.1 WSL2 mental model

Think of WSL2 as:

```text
Windows
│
├── Windows applications
│
└── WSL2
      │
      └── Linux distribution
             │
             └── Docker integration
```

WSL2 is useful for Data Engineers because it provides a Linux environment while retaining access to the Windows desktop ecosystem.

---

## 3.2 Why Linux tooling fits naturally inside WSL2

Inside WSL2 you can use tools such as:

```bash
bash
python
ssh
grep
sed
awk
curl
git
```

with Linux filesystem semantics.

This is particularly useful for Docker-based Data Engineering work.

---

# 4. macOS Docker Architecture

On macOS, the useful mental model is:

```text
macOS
   ↓
Docker Desktop
   ↓
Linux virtualization
   ↓
Docker Engine
   ↓
Linux containers
```

The host is macOS, but the container environment is Linux.

That explains why:

```bash
docker exec <container> uname -a
```

can show a Linux kernel/environment even though the host laptop is running macOS.

---

# 5. Docker Desktop

## 5.1 What Docker Desktop is

Docker Desktop is a developer-oriented product that packages Docker workflows with platform integration, graphical management, resource controls, and a Linux backend where required.

It is commonly used on:

- Windows;
- macOS.

Docker Desktop is not simply another name for the Docker CLI.

A useful distinction is:

```text
Docker CLI
    ↓
Client commands

Docker Engine
    ↓
Container runtime/service

Docker Desktop
    ↓
Developer platform integrating Docker with the host OS
```

---

## 5.2 Why Data Engineers care

Docker Desktop resource configuration can directly affect:

```text
Kafka
PostgreSQL
MinIO
Redis
Spark
Airflow
```

A local Kafka + Spark + Airflow stack may require substantially more memory than a simple PostgreSQL + Redis stack.

Therefore:

```text
Docker configuration
        ↓
Available resources
        ↓
Service stability
        ↓
Data Engineering workload performance
```

---

# 6. Docker Desktop Settings and Resource Configuration

Relevant settings commonly include:

```text
Memory
CPU
Swap
Disk/storage
```

The exact UI and available settings can vary by Docker Desktop version and platform.

Do not memorize screenshots. Learn the diagnostic process.

---

## 6.1 Inspect the effective environment

Run:

```bash
docker version
```

This helps identify Docker client/server versions.

Run:

```bash
docker info
```

This provides information about the Docker environment.

Run:

```bash
docker context ls
```

This shows Docker contexts and helps identify which Docker endpoint your CLI is using.

Run:

```bash
docker system df
```

This shows Docker storage usage.

Run:

```bash
docker stats
```

This provides live container resource usage.

---

## 6.2 Build a platform inventory

Create a small record:

```text
OS:
Architecture:
Docker version:
Docker Engine:
Docker Desktop:
Runtime:
CPU:
Memory:
Swap:
Docker storage:
Project location:
Known quirks:
```

This is your:

> **My Platform** page.

When a problem appears, this inventory prevents you from troubleshooting without knowing what environment you actually have.

---

# 7. Docker Desktop Licensing and Alternative Runtimes

## 7.1 Docker Desktop licensing

Docker Desktop has its own licensing terms.

It should not be assumed that:

```text
Docker Engine
=
Docker Desktop
```

for licensing purposes.

Individual developers, organisations, and larger enterprises can have different obligations depending on current terms and organisational circumstances.

Licensing terms can change.

Therefore:

> Check the current Docker Desktop licensing terms for your organisation before standardising Docker Desktop for a team or enterprise.

This is operational awareness, not legal advice.

---

## 7.2 Alternative runtimes

Three alternatives worth knowing at operator level are:

```text
Podman
Colima
Rancher Desktop
```

### Podman

Podman is an alternative container engine with strong Linux roots and a daemonless architecture.

Docker-compatible workflows are often possible, but compatibility is not absolute.

### Colima

Colima provides a lightweight container/VM environment commonly used on macOS.

It can support Docker-compatible CLI workflows.

### Rancher Desktop

Rancher Desktop provides a local container development environment and can support Docker-compatible workflows and Kubernetes-oriented development.

---

## 7.3 Comparison

| Runtime | Typical use | Docker CLI compatibility | Platform notes |
|---|---|---|---|
| Docker Desktop | General development | High | Windows/macOS |
| Podman | Alternative container engine | Often compatible, not identical | Linux/macOS/Windows |
| Colima | Lightweight macOS container environment | Docker-compatible workflows | macOS |
| Rancher Desktop | Container/Kubernetes development | Docker-compatible options | Windows/macOS/Linux |

Important:

> "Docker-compatible" does not mean "every behavior is identical."

Networking, volume handling, context configuration, image-building workflows, and Kubernetes integration can differ.

---

# 8. WSL2 Fundamentals

## 8.1 What WSL2 provides

WSL2 gives Windows a Linux environment with a Linux kernel architecture.

A useful model is:

```text
Windows
   │
   ├── Windows applications
   │
   └── WSL2
        │
        └── Linux distribution
```

Docker Desktop can integrate with WSL2 so Docker workloads can interact naturally with Linux tooling.

---

## 8.2 Why Data Engineers use WSL2

Data Engineering tools often assume Linux-like behavior:

```text
Python
Bash
SSH
Git
Docker
Spark
Airflow
Linux utilities
```

Using the Linux side of WSL2 can reduce friction when developing for Linux-based production environments.

---

# 9. WSL2 Filesystem and Performance

This is one of the most important Windows concepts in the module.

Compare:

```text
/home/user/project
```

with:

```text
/mnt/c/Users/user/project
```

The first is inside the WSL2 Linux filesystem.

The second exposes a Windows filesystem path to Linux.

---

## 9.1 Why `/mnt/c` can be slower

When Linux workloads access Windows-mounted files, operations can cross a filesystem boundary.

That matters for workloads with:

- large numbers of small files;
- frequent metadata operations;
- source-tree scanning;
- Python package directories;
- dependency installation;
- file watchers;
- Spark workloads;
- generated datasets;
- tests.

The important mental model is:

```text
Linux process
     ↓
Linux filesystem
     ↓
Fast/native Linux path

versus

Linux process
     ↓
/mnt/c
     ↓
Windows filesystem boundary
     ↓
Potential overhead
```

The exact performance difference depends on workload and configuration.

---

## 9.2 Recommended project location

For Linux-heavy Docker/Data Engineering projects, generally prefer:

```text
/home/<user>/<project>
```

inside WSL2.

Avoid placing large, file-intensive development trees under `/mnt/c` unless there is a specific reason.

This does not mean `/mnt/c` is unusable.

It means:

> Keep Linux-heavy workloads close to the Linux filesystem when performance matters.

---

## 9.3 Database files

Do not casually place active database files on arbitrary Windows-mounted paths.

Databases perform many filesystem operations, and virtualization/filesystem boundaries can make performance and behavior less predictable.

Prefer Docker-managed volumes or storage appropriate to the platform and workload.

---

# 10. WSL2 Permissions

Windows and Linux use different permission models.

Common symptoms include:

```text
Permission denied
Unexpected owner
Executable bit missing
Mounted script will not execute
Files created with unexpected permissions
```

Inspect a Linux-side file with:

```bash
ls -la
```

Use:

```bash
stat <file>
```

Inspect your identity:

```bash
id
```

Confirm your working directory:

```bash
pwd
```

---

## 10.1 Why the Linux filesystem helps

Inside:

```text
/home/user/project
```

you get normal Linux ownership and permission semantics.

On Windows-mounted filesystems, translation between Windows and Linux permission models can produce confusing behavior.

This is one reason the Linux filesystem is usually the better home for Linux-heavy Docker development.

---

# 11. WSL2 Memory, CPU, and Swap

WSL2 resource configuration affects how much capacity is available for Linux workloads.

Important dimensions include:

```text
Memory
CPU
Swap
```

These interact with Docker Desktop and the workloads you run.

---

## 11.1 `.wslconfig`

A common configuration concept is a Windows-side `.wslconfig` file.

A representative example is:

```ini
[wsl2]
memory=8GB
processors=4
swap=4GB
```

Treat this as an example rather than a universal recommended configuration.

Exact supported settings and behavior depend on the current WSL2 implementation.

---

## 11.2 Resource trade-offs

If you allocate too much memory:

```text
WSL2/Docker
     ↓
Consumes more host capacity
     ↓
Windows becomes memory constrained
```

If you allocate too little:

```text
Kafka/Spark/Airflow
     ↓
Resource pressure
     ↓
Slowdowns / OOM / instability
```

The goal is not:

> Give Docker everything.

The goal is:

> Give the Data Engineering lab enough capacity while preserving a usable host.

---

## 11.3 Restart after configuration changes

After changing WSL2 configuration, a restart is generally required for the new configuration to take effect.

A common administrative command is:

```powershell
wsl --shutdown
```

Then start WSL/Docker Desktop again and verify.

A conceptual workflow is:

```text
Edit configuration
      ↓
Save
      ↓
Restart WSL
      ↓
Verify
      ↓
Run workload
      ↓
Measure
```

Do not assume every Docker resource number maps one-to-one to one WSL2 setting.

---

# 12. CRLF vs LF

## 12.1 The problem

Linux and Unix-like environments conventionally use:

```text
LF
```

Windows commonly uses:

```text
CRLF
```

The difference is small at the byte level but can be operationally significant.

---

## 12.2 How shell scripts fail

Suppose a shell script created with Windows line endings is mounted into a Linux container.

You may encounter:

```text
/bin/sh^M
```

The `^M` is evidence of a carriage-return character being interpreted where Linux expected a normal line ending.

The resulting error can be confusing because the script looks visually correct in an editor.

---

## 12.3 Diagnose line endings

Use:

```bash
file script.sh
```

and, where appropriate:

```bash
cat -A script.sh
```

If CRLF characters are present, you may see evidence such as:

```text
^M
```

---

## 12.4 Fix the problem

The long-term fix is not to manually repair every script.

Use:

```text
Git configuration
+
Editor configuration
+
Repository policy
```

to make line endings predictable.

---

# 13. Git and Editor Line-Ending Configuration

## 13.1 Git

Inspect the current setting:

```bash
git config --global core.autocrlf
```

Possible configurations depend on team workflow and target platforms.

Do not blindly set:

```bash
git config --global core.autocrlf true
```

for every project.

A repository can define explicit policies instead.

---

## 13.2 `.gitattributes`

For a Linux-oriented Docker repository:

```gitattributes
*.sh text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.env text eol=lf
```

This tells Git how selected text files should be represented.

It is especially useful for:

- shell scripts;
- Compose files;
- environment templates;
- Linux container configuration.

---

## 13.3 Editor settings

Configure the editor to display and select:

```text
LF
```

for files that are expected to run inside Linux containers.

The exact UI differs by editor.

The important practice is:

> Make line endings a repository policy, not an individual developer guess.

---

# 14. Cross-Platform Networking

Networking is another place where:

```text
localhost
```

can become misleading.

A useful model is:

```text
Host
Container
WSL2
Docker network
```

---

## 14.1 `localhost` is relative to the current network namespace/environment

From the host:

```text
localhost
```

usually means:

```text
the host itself
```

From inside a container:

```text
localhost
```

means:

```text
that container
```

It does not automatically mean:

```text
my physical laptop
```

From WSL2, the exact behavior can depend on the WSL2 networking mode and Docker/Windows configuration.

---

## 14.2 Common mistake

Suppose PostgreSQL is running on the Windows host at:

```text
127.0.0.1:5432
```

A Python container attempts:

```text
postgresql://localhost:5432
```

The container's `localhost` refers to itself, not necessarily the Windows host.

The resulting symptom may be:

```text
connection refused
```

The solution is to understand the actual network path rather than randomly changing ports.

---

# 15. Host Connectivity and `host.docker.internal`

Docker Desktop environments commonly provide:

```text
host.docker.internal
```

for reaching the host from a container.

For example:

```bash
curl http://host.docker.internal:8080
```

may allow a container to reach a service exposed by the host.

However:

> Do not treat `host.docker.internal` as a universal guarantee across every container runtime and platform configuration.

Support and behavior can vary.

If a runtime does not provide it automatically, use the runtime's documented host-connectivity mechanism.

---

## 15.1 Diagnostic sequence

When container → host connectivity fails:

```text
1. Is the host service running?
        ↓
2. Is it listening on the expected port?
        ↓
3. Is it bound only to loopback?
        ↓
4. Is the container using the expected network?
        ↓
5. Is host.docker.internal supported?
        ↓
6. Does the platform/networking mode require another address?
        ↓
7. Is a firewall involved?
```

This is more reliable than memorizing one address.

---

# 16. Windows, WSL2, and `localhost`

Consider:

```text
Windows application
        ↕
      WSL2
        ↕
     Container
```

There are several distinct connectivity paths:

```text
Windows → WSL2
WSL2 → Windows
Container → Windows
Container → WSL2
Container → Container
```

The correct address can depend on:

- WSL2 networking mode;
- Docker Desktop integration;
- port publishing;
- host binding;
- firewall rules;
- service listening address.

Therefore:

> Diagnose the actual path instead of assuming that all environments share one universal `localhost`.

---

# 17. Host Networking Differences

Host networking means that a container uses a host-oriented network namespace model rather than the normal isolated Docker network model.

The exact behavior varies across platforms.

Linux provides host-networking capabilities that should not automatically be assumed to behave identically on Docker Desktop.

A common mistake is:

```text
"It worked on Linux with host networking."
        ↓
"It must work identically on macOS/Windows."
```

That conclusion is unsafe.

Use ordinary published ports and Docker networks for portable local labs unless there is a clear reason to depend on host-network behavior.

---

# 18. Apple Silicon and ARM64

Apple Silicon Macs use ARM64 CPUs.

Common architecture names are:

```text
amd64
x86_64
```

and:

```text
arm64
aarch64
```

A simplified model:

```text
Apple Silicon
    ↓
ARM64 CPU
```

---

## 18.1 Why image architecture matters

A container image is not necessarily executable on every CPU architecture.

A tag may provide:

```text
linux/amd64
linux/arm64
```

or only one of them.

If an image is ARM64-native, it can generally run without CPU architecture emulation on Apple Silicon.

If it only provides amd64, Docker may need emulation.

---

# 19. Multi-Architecture Images

A multi-platform image can be thought of as:

```text
One image tag
      ↓
Platform manifests
      ├── linux/amd64
      └── linux/arm64
```

This allows:

```bash
docker pull postgres
```

to select an appropriate architecture when the published image supports the user's platform.

The important distinction is:

```text
Multi-architecture image
    ≠
Single-architecture image
```

---

## 19.1 Inspect architecture support

Inspect a local image:

```bash
docker image inspect <image>
```

For registry-level platform information, where supported:

```bash
docker buildx imagetools inspect <image>
```

The exact output depends on the image and registry.

---

# 20. amd64 Emulation on ARM

Suppose:

```text
ARM64 host
    ↓
amd64-only image
    ↓
emulation
```

You can explicitly request a platform when appropriate:

```bash
docker run --platform linux/amd64 <image>
```

---

## 20.1 What `--platform` does

It tells Docker which target platform to use.

This is useful when:

- an image is only published for amd64;
- you are testing a specific architecture;
- compatibility requires a particular image architecture.

But it should not automatically be the first solution.

Prefer:

```text
Native ARM64 image
```

when one is available and appropriate.

---

## 20.2 Emulation cost

Emulation can introduce performance overhead.

The effect depends on workload.

CPU-heavy or architecture-sensitive workloads may be affected more than lightweight services.

For a Data Engineering lab, this matters particularly for:

```text
Kafka
Spark
large Python workloads
compression
cryptography
native libraries
```

Do not assume:

```text
works
=
same performance
```

---

# 21. File-Change Watching

Development tools often need to detect:

```text
File created
File modified
File deleted
```

Examples:

- Python development servers;
- Airflow DAG development;
- Spark code;
- configuration reloaders;
- test runners.

---

## 21.1 Why platform boundaries matter

Native Linux filesystem events can behave differently from events crossing:

```text
Windows filesystem
    ↕
WSL2
    ↕
Docker
```

or:

```text
macOS
    ↕
Docker Desktop Linux environment
```

Some tools can use native filesystem events.

Others may use polling.

Polling can increase CPU usage and still behave differently from native event delivery.

---

## 21.2 Practical symptom

You edit:

```text
dags/example.py
```

but Airflow does not notice the change.

Do not immediately assume the application is broken.

Investigate:

```text
Where is the file stored?
Is it bind-mounted?
Is it crossing a virtualization boundary?
How does the application watch files?
Does the runtime support the expected event behavior?
```

---

# 22. Bind-Mount Performance

A bind mount creates a relationship like:

```text
Host filesystem
      ↓
Bind mount
      ↓
Container
```

This is convenient for source code and configuration.

But performance can vary.

---

## 22.1 WSL2 example

Compare:

```text
WSL2:
/home/user/project
```

with:

```text
Windows:
/mnt/c/Users/user/project
```

The second path may involve additional filesystem translation/boundary behavior.

---

## 22.2 macOS example

macOS Docker Desktop also needs to make host files available inside its Linux environment.

That means:

```text
macOS filesystem
      ↓
virtualization / file-sharing layer
      ↓
Linux container
```

The performance characteristics differ from native Linux.

---

## 22.3 Workloads most affected

Pay attention when working with:

- thousands or millions of small files;
- Python dependency trees;
- Spark projects;
- package caches;
- test suites;
- source trees;
- generated datasets.

A named Docker volume can sometimes perform differently from a bind mount because the storage path and sharing mechanism are different.

Do not claim that named volumes are always faster. Benchmark the workload.

---

# 23. Performance Experiment

The purpose of this experiment is not to memorize benchmark numbers.

The purpose is to learn:

> Measure your actual workload instead of assuming.

---

## 23.1 WSL2 experiment

Create equivalent project trees in:

```text
WSL2 Linux filesystem
/home/<user>/docker-platform-lab
```

and:

```text
Windows-mounted filesystem
/mnt/c/Users/<user>/docker-platform-lab
```

Use a controlled file-heavy workload.

Example Python:

```python
from pathlib import Path
import time

root = Path("benchmark-data")
root.mkdir(exist_ok=True)

start = time.perf_counter()

for i in range(5000):
    path = root / f"file-{i}.txt"
    path.write_text("data-engineering-test\n", encoding="utf-8")

elapsed = time.perf_counter() - start
print(f"Created 5000 files in {elapsed:.3f}s")
```

Run it from each location.

Record:

| Location | Workload | Runtime | File Count | Observation |
|---|---|---:|---:|---|
| WSL2 Linux filesystem | file creation | | 5000 | |
| `/mnt/c` | file creation | | 5000 | |

The result will depend on your machine and current configuration.

---

## 23.2 macOS variant

Repeat a file-heavy workload through a Docker bind mount from the macOS filesystem.

Compare it with a Docker-managed volume where appropriate.

Again:

```text
Measure
→ Compare
→ Explain
```

rather than:

```text
Assume
→ Repeat someone else's benchmark
```

---

# 24. Clock Drift and Virtual Machines

This is an advanced but important operational issue.

A virtualized environment can experience time synchronization changes around:

```text
Host laptop sleeps
        ↓
Virtual environment pauses
        ↓
Host resumes
        ↓
Virtual environment resumes
        ↓
Time synchronization may temporarily differ
```

Exact behavior varies by platform and runtime.

---

## 24.1 Why time matters

Time affects:

- authentication tokens;
- JWT expiration;
- TLS validation;
- scheduled jobs;
- Kafka timestamps;
- distributed systems;
- databases;
- Airflow;
- APIs.

---

## 24.2 Symptoms

You may see:

```text
Token expired unexpectedly
TLS certificate time errors
Scheduled task appears late
Timestamp anomalies
Service rejects authentication
```

---

## 24.3 Investigate host and container time

Linux:

```bash
date
```

On systems that provide it:

```bash
timedatectl
```

Windows PowerShell:

```powershell
Get-Date
```

Container:

```bash
docker exec <container> date
```

Compare timestamps.

The goal is not to invent a universal repair command.

The goal is to identify whether time synchronization is contributing to the incident.

---

# 25. Docker Virtual-Disk Reclamation

Topic 09 established the difference between logical Docker cleanup and physical disk reclamation.

The model is:

```text
Docker cleanup
      ↓
Unused Docker resources removed
      ↓
Logical Docker usage decreases
      ↓
Virtual disk may remain large
      ↓
Platform-specific disk reclamation may be needed
```

---

## 25.1 Why deleting data does not always shrink the disk

Imagine a virtual disk that has grown to:

```text
100 GB
```

After Docker cleanup:

```text
40 GB used
60 GB free internally
```

The virtual disk file may still occupy close to its previous allocated size.

Therefore:

```text
Docker logical usage
        ≠
Physical virtual-disk file size
```

---

# 26. Windows + WSL2 Disk Reclamation

On Windows, Docker Desktop and WSL2 can use virtualized storage.

The exact physical storage path and reclamation mechanism depend on:

- Docker Desktop version;
- WSL2 configuration;
- virtual disk implementation;
- filesystem;
- installation details.

Do not copy a destructive disk-management command from an old tutorial without understanding the current environment.

A safe workflow is:

```text
1. Clean Docker resources
2. Verify important data/backups
3. Confirm logical Docker usage decreased
4. Identify the actual virtual disk
5. Read current platform documentation
6. Perform platform-specific reclamation if justified
7. Verify Docker still works
```

---

# 27. macOS Docker Disk Reclamation

The same principle applies to Docker Desktop on macOS.

Conceptually:

```text
macOS
   ↓
Docker Desktop
   ↓
Linux virtual environment
   ↓
Docker storage
```

Cleaning Docker resources can free internal space without immediately reducing the host-visible virtual disk allocation.

The exact reclamation process is version- and configuration-dependent.

Use current Docker Desktop documentation for the supported procedure.

Do not invent or blindly execute VM/storage commands.

---

# 28. Designing Cross-Platform Data Engineering Labs

This is the final architectural skill of the module.

A good Docker lab should work for:

```text
Linux
Windows + WSL2
macOS Intel
macOS Apple Silicon
```

without pretending the environments are identical.

---

## 28.1 Avoid assumptions about

Do not assume:

- filesystem paths;
- `localhost`;
- shell syntax;
- line endings;
- CPU architecture;
- permissions;
- file watchers;
- Docker storage paths;
- available memory;
- host networking;
- virtualization behavior;
- executable bits.

---

## 28.2 Prefer

Prefer:

- Docker Compose;
- environment variables;
- relative project paths;
- documented platform-specific instructions;
- multi-architecture images;
- health checks;
- explicit resource budgets;
- reproducible commands;
- validation commands.

---

## 28.3 Example cross-platform project layout

Use a repository-relative layout:

```text
data-engineering-lab/
├── compose.yaml
├── .env.example
├── .gitattributes
├── scripts/
│   └── health-check.sh
├── config/
├── pipelines/
└── README.md
```

Avoid documentation such as:

```text
C:\Users\Alice\project
```

unless it is explicitly labeled as a Windows example.

Prefer:

```text
<project-root>
```

or:

```text
./config
```

---

# 29. Cross-Platform Command Strategy

Different users may work in:

```text
Bash
PowerShell
Windows Command Prompt
```

Documentation should clearly identify the shell.

Example:

### Linux/macOS/WSL Bash

```bash
pwd
```

### PowerShell

```powershell
Get-Location
```

The goal is not to teach complete PowerShell or Bash programming.

The goal is to prevent a learner from pasting a command into the wrong shell and assuming Docker is broken.

---

# 30. "My Platform" Documentation

Create a page in your personal lab notes using this template:

```markdown
# My Docker Platform

## Host OS

## Host CPU Architecture

## Docker Version

## Docker Engine

## Docker Desktop

## Container Runtime

## WSL2

## CPUs Available

## Memory Available

## Swap

## Docker Storage

## Project Location

## Filesystem Notes

## Networking Notes

## Architecture Notes

## Known Quirks

## Troubleshooting Notes
```

Populate it using:

```bash
docker version
docker info
docker context ls
```

On WSL2, also use:

```powershell
wsl --status
wsl --list --verbose
```

For CPU architecture inside Linux/WSL:

```bash
uname -m
```

For host date on Windows:

```powershell
Get-Date
```

The page should answer:

> What exactly is the environment in which this Docker lab is running?

---

# 31. Hands-On Lab — `docker_lab/10/`

Create a practice directory:

```text
docker_lab/
└── 10/
```

The exercises below are documented inside this module rather than requiring additional roadmap files.

---

## Exercise 1 — Filesystem Performance

On Windows/WSL2:

1. Create a project in the WSL2 Linux filesystem.
2. Create an equivalent project under `/mnt/c`.
3. Run a file-heavy Python workload.
4. Record execution time.
5. Compare the results.
6. Explain the filesystem boundary.

On macOS:

1. Create a host-directory bind mount.
2. Create an equivalent Docker-managed storage test where appropriate.
3. Run the same or comparable file-heavy workload.
4. Compare and explain.

Record:

| Platform | Location | Workload | Runtime | File Count | Observation |
|---|---|---|---:|---:|---|
| | | | | | |

---

## Exercise 2 — Resource Limits

Configure appropriate CPU/memory resources for your platform.

Inspect:

```bash
docker info
```

Observe live usage:

```bash
docker stats
```

Distinguish:

```text
Configured capacity/limit
        ≠
Actual container usage
```

Test a Data Engineering service such as PostgreSQL, Redis, or a controlled application workload.

Document:

```text
Allocated resources:
Observed usage:
Observed pressure:
Conclusion:
```

---

## Exercise 3 — CRLF Bug

Create a shell script using Windows CRLF line endings.

Example intended script:

```bash
#!/usr/bin/env bash
echo "hello from Linux"
```

Mount it into a Linux container.

A CRLF version can result in a symptom similar to:

```text
/bin/sh^M
```

Diagnose with:

```bash
file script.sh
cat -A script.sh
```

Fix the file so it uses LF.

Then run it again.

Document:

```text
Symptom:
Root cause:
Diagnosis:
Fix:
Prevention:
```

---

## Exercise 4 — Host Connectivity

Run a host service.

For example, a simple HTTP service can listen on a known host port.

From a container, test:

```bash
curl http://host.docker.internal:8080
```

if supported by your platform/runtime.

Document:

```text
Host platform:
Container runtime:
Host service address:
Container test address:
Result:
Why:
```

Do not assume `localhost` is correct.

---

## Exercise 5 — ARM64 / amd64

On an ARM64 machine:

1. Find a relevant image.
2. Determine whether it supports ARM64.
3. Determine whether it supports amd64.
4. Inspect its architecture metadata.
5. Run an amd64 variant only where appropriate.
6. Compare behavior with native ARM64 when available.

Useful commands:

```bash
uname -m
```

and:

```bash
docker image inspect <image>
```

For registry manifest inspection:

```bash
docker buildx imagetools inspect <image>
```

If needed:

```bash
docker run --platform linux/amd64 <image>
```

Record:

```text
Host architecture:
Image architectures:
Native platform:
Emulated platform:
Performance observation:
```

---

# 32. Break/Fix Exercises

## Scenario 1 — Slow Python Project

### Symptom

A project stored under:

```text
/mnt/c
```

performs file-heavy operations extremely slowly.

### Investigation

Check:

```text
Project location
File count
Bind mounts
Filesystem boundary
File watchers
```

### Fix

Move Linux-heavy project data into the WSL2 Linux filesystem where practical.

### Lesson

Filesystem location can be a performance characteristic.

---

## Scenario 2 — Shell Script Failure

### Symptom

A mounted shell script produces:

```text
/bin/sh^M
```

### Diagnosis

```bash
file script.sh
cat -A script.sh
```

### Root cause

CRLF line endings.

### Fix

Convert to LF and configure Git/editor policies to prevent recurrence.

---

## Scenario 3 — Permission Error

### Symptom

A container cannot read or write a mounted directory.

### Investigation

```bash
pwd
ls -la
stat <path>
id
```

Determine:

```text
Windows filesystem?
WSL2 filesystem?
Linux permissions?
UID/GID?
Mount behavior?
```

### Lesson

Do not treat all "permission denied" errors as Docker bugs.

---

## Scenario 4 — Connection Refused

### Symptom

A host service works from Windows but a container cannot reach it.

### Investigate

```text
localhost
host.docker.internal
published port
service binding
network
firewall
```

### Lesson

Container `localhost` is not automatically the physical host.

---

## Scenario 5 — ARM Image Failure

### Symptom

An ARM Mac cannot run an image normally.

### Investigate

```text
Host architecture
Image architecture
Available manifests
Emulation requirement
```

Use:

```bash
uname -m
docker buildx imagetools inspect <image>
```

### Lesson

Image architecture is part of application compatibility.

---

## Scenario 6 — Docker Disk Still Large

### Symptom

Docker cleanup succeeded but the host still reports a large Docker virtual disk.

### Diagnosis

Separate:

```text
Logical Docker cleanup
        from
Physical virtual-disk reclamation
```

### Lesson

Free blocks inside a virtual disk do not necessarily cause the virtual disk file to shrink immediately.

---

# 33. Real-World Data Engineering Scenarios

## Scenario A — PostgreSQL development on Windows

### Symptom

PostgreSQL development is unexpectedly slow.

### Investigation

The project/data path is under:

```text
/mnt/c
```

and contains heavy filesystem activity.

### Root cause

Filesystem boundary overhead.

### Fix

Keep Linux-heavy project data in the WSL2 Linux filesystem or use appropriate Docker-managed storage.

### Cross-platform lesson

Storage location is part of performance design.

---

## Scenario B — Kafka on Apple Silicon

### Symptom

A Kafka image has compatibility or performance issues.

### Investigation

```text
Host = ARM64
Image = amd64
```

### Root cause

Architecture mismatch requiring emulation.

### Fix

Prefer a native multi-architecture image where appropriate.

### Cross-platform lesson

Always consider CPU architecture when choosing images.

---

## Scenario C — Python pipeline with thousands of files

### Symptom

A Python pipeline is much slower on Docker Desktop than on native Linux.

### Investigation

Large numbers of file operations occur through a host bind mount.

### Root cause

Filesystem-sharing/virtualization overhead.

### Fix

Benchmark Docker-managed storage and alternative project locations.

---

## Scenario D — Airflow DAG development

### Symptom

A DAG change is not detected immediately.

### Investigation

Check:

```text
Bind mount
Project location
File watcher
Filesystem event delivery
Polling configuration
```

### Root cause

File-change notification behavior across platform boundaries.

### Lesson

File watching is an environment dependency.

---

## Scenario E — Authentication failure after laptop sleep

### Symptom

A service suddenly reports:

```text
token expired
TLS time error
```

after the laptop wakes.

### Investigation

Compare:

```bash
date
docker exec <container> date
```

and, on Windows:

```powershell
Get-Date
```

### Possible cause

Temporary time synchronization discrepancy.

### Lesson

Virtualized development environments depend on correct time.

---

## Scenario F — Cross-platform team documentation

### Requirement

A Docker lab must support:

```text
Linux
Windows + WSL2
macOS Intel
macOS Apple Silicon
```

### Design

Document:

```text
Prerequisites
Platform detection
Project location
Shell
Architecture
Resource budget
Networking
Line endings
Image architecture
Troubleshooting
```

### Lesson

Cross-platform documentation is itself an engineering artifact.

---

# 34. Platform Comparison

| Area | Linux | Windows + WSL2 | macOS Intel | macOS Apple Silicon |
|---|---|---|---|---|
| Docker execution | Native Linux Engine commonly available | Linux environment/backend | Linux virtualized environment | Linux virtualized environment |
| Linux container environment | Native Linux host | WSL2/Docker Desktop integration | Docker Desktop Linux environment | Docker Desktop Linux environment |
| Filesystem behavior | Native Linux semantics | Linux FS generally preferred for Linux workloads | Host-to-Linux sharing boundary | Host-to-Linux sharing boundary |
| Bind mounts | Often closest to native Linux | Can be slower across Windows boundary | Can have sharing overhead | Can have sharing + architecture considerations |
| Permissions | Linux-native | Can differ across WSL2 and Windows paths | Host-sharing semantics differ | Same plus ARM considerations |
| Networking | Linux-native behavior | WSL2/Docker Desktop integration | Docker Desktop networking | Docker Desktop networking |
| Memory limits | Host/kernel/container controls | WSL2 + Docker configuration | Docker Desktop resource configuration | Docker Desktop resource configuration |
| CPU architecture | Depends on host | Usually x86 Windows hardware, but varies | Intel or Apple Silicon depending on Mac | ARM64 |
| ARM considerations | Host-dependent | Host-dependent | Intel or ARM Mac model | Major consideration |
| File watching | Native Linux events generally straightforward | Boundary can affect events | Sharing layer can affect events | Sharing layer can affect events |
| Virtual disk | Native filesystem/Docker data root | WSL2/Docker Desktop virtualized storage | Docker Desktop virtualized storage | Docker Desktop virtualized storage |
| Common pitfalls | Resource/storage assumptions | `/mnt/c`, networking, permissions, CRLF | bind mounts, networking, virtualization | ARM/amd64, emulation, bind mounts |

This table is intentionally high-level. Exact behavior depends on Docker Desktop, WSL2, runtime, version, configuration, and hardware.

---

# 35. Common Mistakes

## 1. Working from `/mnt/c` for Linux-heavy workloads

Why it fails:

Frequent filesystem operations can cross the Windows/Linux filesystem boundary.

---

## 2. Keeping huge Data Engineering projects on slow cross-filesystem paths

Large source trees, dependency directories, and generated datasets can amplify filesystem overhead.

---

## 3. Ignoring WSL2 memory limits

Kafka, Spark, and Airflow can become unstable when the available memory is too small.

---

## 4. Allocating too much memory to Docker

The host operating system still needs memory.

A Docker environment that consumes nearly all physical memory can make Windows or macOS unusable.

---

## 5. Allocating too little memory

Services can become:

```text
slow
OOM-prone
unstable
```

---

## 6. Assuming `localhost` means the host

From a container:

```text
localhost = container
```

not automatically the host.

---

## 7. Assuming Linux networking is identical on Docker Desktop

Host networking and forwarding can differ.

---

## 8. Ignoring CRLF

A script can look correct while failing inside Linux.

---

## 9. Assuming every image supports ARM64

Some images are architecture-specific.

---

## 10. Using amd64 emulation without understanding the cost

Compatibility can come with performance overhead.

---

## 11. Ignoring file-watch behavior

Development tools may not receive expected filesystem events.

---

## 12. Ignoring bind-mount performance

Host filesystem sharing can become a bottleneck.

---

## 13. Ignoring permissions

Windows and Linux permission semantics are not identical.

---

## 14. Assuming Docker Desktop storage paths never change

Docker Desktop versions and configurations can change storage implementation details.

---

## 15. Assuming Docker cleanup automatically shrinks the virtual disk

Logical free space and physical virtual-disk size are different concepts.

---

## 16. Ignoring clock problems after sleep

Time-sensitive services can fail after virtualization/host sleep events if clocks temporarily diverge.

---

## 17. Writing Linux-only instructions for a multi-platform team

A tutorial that assumes:

```text
bash
/home/user
localhost
amd64
```

may fail for a significant portion of the team.

---

# 36. Mental Models

## Model 1 — Platform Stack

```text
Application
    ↓
Container
    ↓
Docker Engine
    ↓
Linux kernel / Linux VM
    ↓
Host OS
    ↓
Hardware
```

On Linux, the Linux kernel is native to the host.

On Windows and macOS, Docker Desktop generally provides a Linux environment through virtualization/integration.

---

## Model 2 — WSL2 Filesystem

```text
Windows filesystem
        │
        └── /mnt/c
               ↑
        boundary crossing
               ↓
        Linux filesystem
        /home/user/project
```

For Linux-heavy workloads, prefer the Linux filesystem when practical.

---

## Model 3 — Architecture

```text
ARM64 host
    ↓
ARM64 image
    ↓
Native execution
```

versus:

```text
ARM64 host
    ↓
amd64 image
    ↓
Emulation
    ↓
Potential performance cost
```

---

## Model 4 — Docker Disk

```text
Container/resource cleanup
       ↓
Docker logical data decreases
       ↓
Virtual disk may remain allocated
       ↓
Platform-specific reclamation
```

---

## Model 5 — Connectivity

```text
Container
   │
   ├── localhost
   │      └── container itself
   │
   ├── Docker service name
   │      └── another container on a Docker network
   │
   └── host.docker.internal
          └── host access where supported
```

The exact host-connectivity mechanism depends on platform/runtime.

---

# 37. Command Reference

## Docker environment

```bash
docker version
docker info
docker context ls
docker stats
docker system df
```

## Linux filesystem

```bash
pwd
ls -la
stat <file>
id
date
timedatectl
```

`timedatectl` is available on systems using systemd and may not exist everywhere.

## WSL2 / Windows

```powershell
wsl --status
wsl --list --verbose
wsl --shutdown
Get-Date
Get-Location
```

## Architecture

```bash
uname -m
docker image inspect <image>
docker buildx imagetools inspect <image>
```

## Networking

Where supported:

```bash
curl http://host.docker.internal:8080
```

Remember:

```text
host.docker.internal
```

is not a universal guarantee across every container runtime.

## Platform-specific caution

Commands involving:

- WSL2 configuration;
- Docker Desktop storage;
- virtual-disk reclamation;
- host networking;
- architecture emulation;

should be checked against the current platform/runtime documentation.

---

# 38. Practice Questions

## Beginner

1. What is Docker Desktop?
2. Why does Docker use a Linux environment on Windows?
3. Why does Docker use Linux containers on macOS?
4. What is WSL2?
5. What is the difference between Docker CLI and Docker Engine?
6. Why can the same container behave differently on two host platforms?

### Model answer

Docker standardizes much of the application environment, but host-platform differences remain in filesystem behavior, networking, resources, architecture, permissions, and virtualization.

---

## Intermediate

1. Why is `/mnt/c` often slower for Linux-heavy workloads?
2. Why can CRLF break a shell script?
3. Why does `localhost` behave differently from inside a container?
4. What is `host.docker.internal`?
5. What is a multi-architecture image?
6. Why can WSL2 memory configuration affect Kafka?
7. Why can Docker Desktop resource settings affect Spark?
8. Why can file watching behave differently across platforms?

### Model answer

The platform can change the filesystem event path, particularly when files cross Windows/Linux or host/Linux virtualization boundaries. Applications that rely on native file events may therefore need different behavior or polling.

---

## Advanced

1. Explain Docker's architecture on Windows + WSL2.
2. Explain Docker's architecture on Apple Silicon.
3. Why can bind mounts be slower across virtualization boundaries?
4. How would you troubleshoot a container-to-host networking problem?
5. How would you diagnose an ARM64/amd64 compatibility issue?
6. Why can a Docker virtual disk remain large after cleanup?
7. How can clock drift affect authentication?
8. How would you write one Docker lab instruction set for four platform classes?

### Model answer

Start by separating platform-independent Docker behavior from platform-dependent assumptions. Use relative paths, Compose, environment variables, multi-architecture images, explicit platform notes, shell-specific commands, validation commands, and troubleshooting branches for filesystem, networking, architecture, permissions, and resource differences.

---

## Scenario-Based

### Scenario 1

A Python pipeline is five times slower on Windows than on Linux.

What do you investigate first?

### Scenario 2

A container can reach another container but cannot reach a service running on Windows.

What network paths do you test?

### Scenario 3

A shell script works on Windows but fails with `/bin/sh^M` in a Linux container.

What is the root cause?

### Scenario 4

An Apple Silicon laptop runs a Kafka image successfully but much more slowly than another laptop.

What architecture questions do you ask?

### Scenario 5

A Docker Desktop virtual disk is still large after deleting unused images and containers.

What distinction explains this?

---

# 39. Interview Practice

## Q1. Does Docker eliminate platform differences?

### Model answer

No. Docker standardizes the containerized application environment, but host operating systems, filesystems, CPU architecture, networking, permissions, virtualization, resource configuration, and file watching can still differ.

---

## Q2. Why is `/mnt/c` often discouraged for Linux-heavy WSL2 projects?

### Model answer

`/mnt/c` exposes the Windows filesystem to Linux. Linux-heavy workloads with many filesystem operations can incur overhead crossing that boundary. Keeping projects inside the WSL2 Linux filesystem often gives more predictable Linux filesystem behavior and performance.

---

## Q3. Why does Docker Desktop use a Linux environment on macOS?

### Model answer

Ordinary Docker containers are generally Linux containers and depend on Linux kernel facilities. macOS does not provide that Linux kernel, so Docker Desktop provides a Linux environment through virtualization.

---

## Q4. What is the difference between ARM64 and amd64?

### Model answer

They are different CPU architectures. Apple Silicon is ARM64. Many traditional servers and Intel/AMD PCs use amd64. An image built only for amd64 may require emulation on ARM64 hardware.

---

## Q5. What is a multi-architecture image?

### Model answer

A multi-architecture image tag can point to platform-specific image manifests, such as `linux/amd64` and `linux/arm64`, allowing Docker to select an appropriate image for the host architecture.

---

## Q6. Why can amd64 emulation be slower on Apple Silicon?

### Model answer

The ARM64 CPU is executing software built for another instruction-set architecture through an emulation/translation layer. The overhead depends on the workload and can be material for CPU-intensive or native-library-heavy applications.

---

## Q7. Why is `localhost` dangerous in Docker troubleshooting?

### Model answer

`localhost` refers to the current network environment. Inside a container it normally means the container itself, not the host laptop. Therefore a host service cannot automatically be reached using `localhost` from a container.

---

## Q8. What is `host.docker.internal`?

### Model answer

It is a host-access hostname provided by Docker Desktop environments and some compatible runtimes. It can allow a container to reach a service on the host. Its availability and exact behavior are runtime/platform-dependent.

---

## Q9. Why can Docker cleanup leave a large virtual disk?

### Model answer

Docker cleanup can free logical storage inside a virtual disk without automatically shrinking the physical virtual-disk allocation. Platform-specific reclamation may be required.

---

## Q10. How can clock drift affect Data Engineering systems?

### Model answer

Time is used for token expiry, TLS validation, scheduled jobs, Kafka timestamps, databases, Airflow, and distributed systems. A temporary clock discrepancy can therefore produce authentication, scheduling, or timestamp failures.

---

## Q11. What should cross-platform Docker documentation avoid?

### Model answer

It should avoid assumptions about paths, shells, `localhost`, CPU architecture, line endings, permissions, host networking, Docker storage paths, and resource availability. It should instead use explicit platform notes and validation steps.

---

# 40. Final Knowledge Check

```text
[ ] I can explain how Docker runs on Linux.
[ ] I can explain how Docker runs on Windows with WSL2.
[ ] I can explain how Docker runs on macOS.
[ ] I understand Docker Desktop's role.
[ ] I know that Docker Desktop licensing should be checked for organisational use.
[ ] I understand Podman, Colima, and Rancher Desktop at a high level.
[ ] I know why WSL2 projects should generally live in the Linux filesystem.
[ ] I understand /mnt/c performance implications.
[ ] I understand Linux vs Windows filesystem permissions.
[ ] I can configure WSL2 memory, CPU, and swap conceptually.
[ ] I know when WSL2 needs restarting after configuration changes.
[ ] I understand CRLF vs LF.
[ ] I can diagnose CRLF shell-script failures.
[ ] I understand host/container networking differences.
[ ] I understand localhost from different environments.
[ ] I can use host.docker.internal where appropriate.
[ ] I understand host-networking platform differences.
[ ] I understand ARM64 vs amd64.
[ ] I understand multi-architecture images.
[ ] I understand emulation and its performance cost.
[ ] I understand file-change watching differences.
[ ] I understand bind-mount performance differences.
[ ] I understand clock drift after VM sleep.
[ ] I understand how clock problems can affect tokens and time-sensitive services.
[ ] I understand Docker virtual-disk reclamation.
[ ] I understand Windows/WSL2 disk reclamation conceptually.
[ ] I understand macOS Docker disk reclamation conceptually.
[ ] I can write cross-platform Docker lab instructions.
[ ] I can troubleshoot common platform-specific Docker problems.
```

---

# 41. Topic Completion Checklist

## Architecture

- [ ] I can draw the Linux Docker architecture.
- [ ] I can draw the Windows + WSL2 architecture.
- [ ] I can draw the macOS Docker architecture.
- [ ] I understand Docker Desktop's role.

## Docker Desktop

- [ ] I can inspect Docker version and context.
- [ ] I understand CPU/memory/swap/storage settings.
- [ ] I understand organisational licensing awareness.
- [ ] I know Podman, Colima, and Rancher Desktop exist and understand their basic positioning.

## WSL2

- [ ] I understand WSL2.
- [ ] I keep Linux-heavy projects in the Linux filesystem where practical.
- [ ] I understand `/mnt/c` performance implications.
- [ ] I can inspect permissions.
- [ ] I understand `.wslconfig`.
- [ ] I understand CPU/memory/swap trade-offs.
- [ ] I know WSL generally needs restarting after relevant configuration changes.

## Files

- [ ] I understand CRLF vs LF.
- [ ] I can diagnose `^M`.
- [ ] I can use `.gitattributes`.
- [ ] I can configure an editor appropriately.

## Networking

- [ ] I understand container `localhost`.
- [ ] I understand host connectivity.
- [ ] I understand `host.docker.internal` where supported.
- [ ] I understand platform-specific host networking.
- [ ] I can troubleshoot connectivity instead of guessing addresses.

## Architecture

- [ ] I understand ARM64.
- [ ] I understand amd64.
- [ ] I understand multi-architecture images.
- [ ] I understand emulation.
- [ ] I understand emulation performance cost.

## Advanced Operations

- [ ] I understand file-change watching.
- [ ] I understand bind-mount performance.
- [ ] I understand clock drift.
- [ ] I can investigate time-related failures.
- [ ] I understand virtual-disk reclamation.

## Cross-Platform Labs

- [ ] I can design platform-neutral project paths.
- [ ] I can document shell-specific commands.
- [ ] I can document architecture-specific behavior.
- [ ] I can document platform-specific networking.
- [ ] I can create a "My Platform" page.
- [ ] I can troubleshoot Linux, Windows/WSL2, macOS Intel, and Apple Silicon differences.

---

# 42. Final Roadmap Coverage Audit

This module explicitly covers the required Topic 10 concepts:

| Roadmap requirement | Covered |
|---|---|
| Linux native Docker | Yes |
| Windows + Linux backend | Yes |
| macOS + Linux backend | Yes |
| Docker Desktop role | Yes |
| Docker Desktop settings | Yes |
| Docker Desktop organisational licensing awareness | Yes |
| Podman | Yes |
| Colima | Yes |
| Rancher Desktop | Yes |
| WSL2 architecture | Yes |
| WSL2 Linux filesystem | Yes |
| `/mnt/c` performance | Yes |
| Windows-mounted filesystem permissions | Yes |
| WSL2 memory | Yes |
| WSL2 CPU | Yes |
| WSL2 swap | Yes |
| `.wslconfig` | Yes |
| WSL restart | Yes |
| CRLF vs LF | Yes |
| CRLF shell/configuration failure | Yes |
| Git line endings | Yes |
| Editor line endings | Yes |
| Cross-platform networking | Yes |
| Container → host connectivity | Yes |
| Windows/WSL2 `localhost` behavior | Yes |
| Host networking differences | Yes |
| Apple Silicon / ARM | Yes |
| Multi-architecture images | Yes |
| amd64 on ARM | Yes |
| Emulation | Yes |
| Emulation performance cost | Yes |
| File-change watching | Yes |
| Bind-mount performance | Yes |
| Clock drift | Yes |
| VM sleep/time issues | Yes |
| Token/authentication implications | Yes |
| Windows virtual-disk reclamation | Yes |
| macOS virtual-disk reclamation | Yes |
| Cross-platform lab design | Yes |
| `docker_lab/10/` exercises | Yes |
| Break/fix exercises | Yes |
| Platform comparison | Yes |
| My Platform template | Yes |
| Practice questions | Yes |
| Interview questions | Yes |
| Final knowledge check | Yes |

---

# 43. Scope Boundary

This remains:

```text
Stage 2B
→ Gap Module G1
→ Docker Essentials for Data Labs
```

The learner is becoming a **confident Docker user/operator**.

This topic does not become a complete course on:

- Dockerfile authoring;
- image-building internals;
- multi-stage builds;
- Kubernetes;
- enterprise container orchestration;
- CI/CD;
- advanced Linux administration;
- advanced Windows administration;
- advanced Git.

Those subjects belong elsewhere in the roadmap.

The purpose of Topic 10 is narrower and practical:

> Understand how the host platform changes the behavior, performance, networking, storage, permissions, architecture, and troubleshooting of Docker-based Data Engineering labs.

---

# 44. Professional Takeaway

Docker gives you portability, but portability does not mean identical execution conditions.

A professional Data Engineer thinks in layers:

```text
Application
    ↓
Container
    ↓
Docker Engine / Runtime
    ↓
Linux environment
    ↓
Host OS
    ↓
CPU / Memory / Filesystem / Network
```

When a lab behaves differently, ask:

```text
Is this an application problem?
        ↓
A container problem?
        ↓
A Docker runtime problem?
        ↓
A filesystem problem?
        ↓
A networking problem?
        ↓
A permissions problem?
        ↓
A CPU architecture problem?
        ↓
A resource problem?
        ↓
A virtualization problem?
        ↓
A platform-specific behavior?
```

The most important habits are:

1. **Know your platform before troubleshooting.**
2. **Keep Linux-heavy WSL2 projects in the Linux filesystem when practical.**
3. **Treat `/mnt/c` performance as a workload-dependent question.**
4. **Never assume `localhost` means the host from inside a container.**
5. **Treat CPU architecture as part of image compatibility.**
6. **Prefer native multi-architecture images when available.**
7. **Treat emulation as a compatibility mechanism with possible performance cost.**
8. **Control line endings in cross-platform repositories.**
9. **Benchmark bind mounts when filesystem performance matters.**
10. **Treat Docker Desktop and WSL2 resource settings as part of lab capacity planning.**
11. **Investigate clock synchronization when time-sensitive services fail after sleep.**
12. **Separate Docker logical cleanup from physical virtual-disk reclamation.**
13. **Write platform-aware instructions instead of Linux-only instructions.**
14. **Measure actual behavior instead of relying on assumptions.**

The final learner outcome is:

> **I can take the same Docker-based Data Engineering lab and understand, configure, troubleshoot, and operate it correctly on Linux, Windows + WSL2, macOS Intel, and Apple Silicon — while recognizing platform-specific differences instead of blindly assuming Docker behaves identically everywhere.**
