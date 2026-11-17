# Containers, Images, and Registries for Data Engineering Users

> **Gap Module G1 — Docker Essentials for Data Labs | Topic 01**
>
> This module teaches Docker from the perspective of a **Data Engineer who consumes and operates container images**. It builds the mental model required for the remaining G1 topics and later Stage 2 data-engineering labs.

---

## 1. Learning Objectives

By the end of this module, you should be able to:

- Explain what a container is and how it differs from a process and a virtual machine.
- Explain what a Docker image is and how an image becomes a container.
- Explain image layers at an operator level.
- Manage the basic container lifecycle with `docker create`, `run`, `start`, `stop`, `restart`, and `rm`.
- Use `docker pull`, `docker ps`, `docker ps -a`, `docker images`, and `docker rmi`.
- Understand registries, repositories, namespaces, publishers, tags, and digests.
- Select Data Engineering images based on provenance, documentation, version, architecture, ports, configuration, and persistence requirements.
- Explain why `latest` is unsuitable for reproducible production-like labs.
- Distinguish a mutable tag from an exact image digest.
- Inspect an image with `docker image inspect`.
- Understand `linux/amd64`, `linux/arm64`, multi-architecture images, and `--platform`.
- Understand Docker restart policies and their operational trade-offs.
- Understand registry authentication and pull-rate limits.
- Maintain high-level awareness of Docker Engine, containerd, Podman, Docker Desktop, Colima, and Rancher Desktop.
- Apply these concepts to PostgreSQL, MinIO, Kafka, Redis, Python, and later Data Engineering labs.

The goal is not command memorization. The goal is to develop the reasoning:

> **What am I running? Where did it come from? Which exact version is it? Will it run on my architecture? What state will it create? How will I operate it safely?**

---

## 2. Prerequisites

You should already be comfortable with:

- Basic processes and exit codes.
- Basic filesystem concepts and permissions.
- Environment variables.
- Shell commands, pipes, quoting, and paths.
- `localhost`, ports, and basic local networking.
- Basic security hygiene around passwords and secrets.
- Python configuration and database connection concepts.

You do **not** need previous Docker experience.

### Tools

For this module you need:

- Docker Engine with the Docker Compose v2 plugin, normally installed through Docker Desktop on Windows/macOS or natively on Linux.
- On Windows, WSL2 with a Linux distribution and Docker integration.
- Python for later connection tests.
- `psql` is useful but not required for this topic.
- At least 8 GB RAM; 16 GB is recommended for later Stage 2 stacks.

Alternative runtimes such as Podman, Colima, and Rancher Desktop are discussed only at an awareness level.

---

## 3. What You Are Learning — and What You Are Not

### In scope

This topic teaches you to be a **consumer/operator of container images**:

- Understand images and containers.
- Pull images.
- Inspect images.
- Run and manage containers.
- Select versions.
- Understand registries.
- Understand tags and digests.
- Handle CPU architecture differences.
- Use restart policies.
- Authenticate with registries.
- Diagnose basic image/container selection problems.

### Explicitly out of scope

Do **not** turn this module into training on:

- Dockerfile authoring.
- Image-building strategies.
- Multi-stage builds.
- Advanced BuildKit.
- Authoring Docker Compose files.
- CI/CD image pipelines.
- Kubernetes.

Those belong to later parts of the roadmap, especially Module 2.18 for container authoring.

You will learn enough about image layers and image structure to understand what Docker is operating, but not how to build those images.

---

# 4. What Is a Container?

## 4.1 Start with a process

A **process** is a running program.

For example, when you start Python:

```bash
python
```

your operating system creates a process for the Python interpreter.

That process:

- has a process ID;
- consumes CPU and memory;
- opens files;
- may open network connections;
- has a lifecycle;
- can terminate with an exit code.

A container is built around this same fundamental idea.

> **A container is an isolated process environment managed by a container runtime.**

That statement is more useful than thinking of a container as a "small virtual machine."

---

## 4.2 What does isolation mean?

A container gives a process a controlled view of parts of the operating environment.

Conceptually, the process can have:

- an isolated filesystem view;
- an isolated network namespace;
- controlled resource limits;
- a process namespace;
- configured environment variables;
- a defined startup command.

This allows several services to run on one machine without requiring a separate full operating system for each service.

For a Data Engineer, that means you can run:

```text
PostgreSQL
MinIO
Kafka
Redis
Python
```

as separate services on one development machine.

---

## 4.3 Container as an isolated process

Think about a PostgreSQL container.

Conceptually:

```text
Your computer
│
├── PostgreSQL process
│     └── isolated/container environment
│
├── Python process
│     └── isolated/container environment
│
└── Redis process
      └── isolated/container environment
```

The container does not magically turn PostgreSQL into a different operating system.

It gives the PostgreSQL process a controlled environment in which it runs.

---

## 4.4 Why containers are lightweight

A traditional virtual machine normally includes:

```text
Application
Libraries
Guest OS
Guest kernel
Virtual hardware
Host OS
```

A container does not normally carry a complete guest kernel:

```text
Application
Libraries
Container filesystem
Container isolation
Host OS + kernel
```

This is one reason containers are generally faster to start and lighter than full virtual machines.

There are important platform details: Docker Desktop on Windows and macOS uses a Linux environment/VM underneath because Linux containers require a Linux kernel environment. That does not change the operator mental model.

---

# 5. Container vs Virtual Machine

| Area | Container | Virtual Machine |
|---|---|---|
| Primary unit | Isolated process environment | Virtual computer |
| Guest kernel | Normally shares host kernel | Has its own guest OS/kernel |
| Startup | Usually very fast | Usually slower |
| Resource overhead | Generally lower | Generally higher |
| Filesystem | Image + writable container layer | Virtual disk |
| Isolation model | OS-level isolation mechanisms | Hardware virtualization |
| Typical use | Services, applications, data labs | Full operating systems, strong VM isolation |
| Data Engineering example | PostgreSQL, Kafka, MinIO | Dedicated Linux VM hosting a full platform |

### Why Data Engineers use containers

Data Engineering requires many infrastructure services.

A local project might need:

```text
PostgreSQL
      +
MinIO
      +
Kafka
      +
Redis
      +
Python
```

Installing all of these directly onto a laptop can create:

- dependency conflicts;
- version conflicts;
- difficult cleanup;
- inconsistent environments.

Containers allow the services to be isolated and versioned more cleanly.

---

# 6. What Is a Docker Image?

A **Docker image** is a packaged, read-only template used to create containers.

A useful mental model is:

> **Image = template; container = runtime instance created from that template.**

Conceptually:

```text
Image
  │
  │ docker run
  ▼
Container
```

For example:

```bash
docker pull python:3.12-slim
```

downloads an image.

Then:

```bash
docker run python:3.12-slim
```

uses that image to create and start a container.

The image can contain:

- an operating-system userspace;
- libraries;
- an application/runtime;
- metadata;
- environment configuration;
- startup configuration.

It does not contain a separate kernel in the normal Linux-container model.

---

# 7. Image vs Container

| Image | Container |
|---|---|
| Read-only template | Runtime instance |
| Stored locally after pulling | Created from an image |
| Can be reused | Has its own runtime state |
| Can have multiple tags/references | Has a container name/ID |
| Can remain after containers are removed | Can be stopped or removed |
| Does not represent one running process | Represents a particular container instance |

One image can create many containers:

```text
              postgres:16 image
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      pg-dev      pg-test     pg-demo
```

Removing `pg-dev` does not automatically remove the image.

That separation is fundamental.

---

# 8. Image Layers

Docker images are composed of layers.

Conceptually:

```text
Container
┌──────────────────────────────┐
│ Writable container layer     │
├──────────────────────────────┤
│ Image layer                  │
├──────────────────────────────┤
│ Image layer                  │
├──────────────────────────────┤
│ Base image layer             │
└──────────────────────────────┘
```

The image layers are read-only from the running-container perspective. A container receives a writable layer above them.

## Why layers exist

Layers provide:

- reuse;
- storage efficiency;
- caching;
- faster distribution when common layers already exist locally.

For example:

```text
Python image A ──┐
                 ├── shared base layers
Python image B ──┘
```

Multiple images can share common layers.

### Important operator consequence

Removing a container does not mean:

> "Delete everything Docker downloaded."

The image can remain because it may be used by other containers.

Likewise, deleting an image can fail or behave differently depending on whether containers still reference it.

### Scope boundary

You only need the operational model of layers here.

You do **not** need to learn how to author the layers or construct Dockerfiles yet.

---

# 9. Container Lifecycle

A useful lifecycle is:

```text
                 Image
                   │
                   ▼
                Create
                   │
                   ▼
                 Start
                   │
                   ▼
                Running
                 /    \
              Stop   Restart
                │       │
                ▼       │
              Stopped ◄─┘
                │
                ▼
               Remove
```

## 9.1 `docker create`

Creates a container without starting it.

```bash
docker create --name python-lab python:3.12-slim
```

The image is used to define the container, but the main process is not running yet.

---

## 9.2 `docker start`

Starts an existing stopped container.

```bash
docker start python-lab
```

---

## 9.3 `docker run`

`docker run` is the common shortcut that conceptually performs:

```text
create + start
```

For example:

```bash
docker run --name python-lab python:3.12-slim
```

It creates a new container from the image and starts it.

---

## 9.4 `docker stop`

Stops a running container.

```bash
docker stop python-lab
```

Stopping does not remove the container.

---

## 9.5 `docker restart`

Restarts an existing container.

```bash
docker restart python-lab
```

Conceptually:

```text
stop → start
```

---

## 9.6 `docker rm`

Removes the container object.

```bash
docker rm python-lab
```

Removing the container does not normally remove the image from your local image store.

---

## 9.7 `docker ps`

Shows running containers:

```bash
docker ps
```

---

## 9.8 `docker ps -a`

Shows running and stopped containers:

```bash
docker ps -a
```

This is one of the first commands to use when you think:

> "Where did my container go?"

---

# 10. Core Docker Commands

## 10.1 `docker pull`

### Purpose

Download an image from a registry.

### Syntax

```bash
docker pull IMAGE[:TAG]
```

### Example

```bash
docker pull python:3.12-slim
```

### Data Engineering use

Before starting a reproducible local Python environment, explicitly retrieve the desired image version.

### Common mistake

Using:

```bash
docker pull python:latest
```

without considering reproducibility.

---

## 10.2 `docker run`

### Purpose

Create and start a container from an image.

```bash
docker run IMAGE
```

Example:

```bash
docker run python:3.12-slim
```

Useful options:

```bash
docker run --name python-lab -d python:3.12-slim
```

---

## 10.3 `docker ps`

```bash
docker ps
```

Shows currently running containers.

Use it when checking:

- whether a service is running;
- container names;
- published ports;
- uptime/state.

---

## 10.4 `docker ps -a`

```bash
docker ps -a
```

Shows running and stopped containers.

This is essential for lifecycle investigation.

---

## 10.5 `docker stop`

```bash
docker stop python-lab
```

Stops a running container.

---

## 10.6 `docker start`

```bash
docker start python-lab
```

Starts an existing stopped container.

---

## 10.7 `docker restart`

```bash
docker restart python-lab
```

Restarts the container.

---

## 10.8 `docker rm`

```bash
docker rm python-lab
```

Removes the container.

> **Warning:** Removing a container removes that container's writable state. Persistence of service data is covered deeply in Topic 04.

---

## 10.9 `docker images`

```bash
docker images
```

Lists locally stored images.

Modern Docker also supports:

```bash
docker image ls
```

---

## 10.10 `docker rmi`

```bash
docker rmi python:3.12-slim
```

Removes a local image reference/image data when it is no longer needed and can be removed.

Do not use image removal as casual housekeeping. First understand which images your remaining labs need.

---

# 11. Important `docker run` Options

## 11.1 `--name`

```bash
docker run --name pg-lab postgres:16
```

Assigns a predictable name.

This is especially useful in Data Engineering labs:

```bash
docker logs pg-lab
docker stop pg-lab
docker inspect pg-lab
```

Without a predictable name, Docker may generate a name that is harder to remember.

---

## 11.2 `-d`

Detached mode:

```bash
docker run -d --name redis-lab redis
```

The container runs in the background and Docker returns control to your shell.

This is useful for long-running services.

---

## 11.3 `--rm`

```bash
docker run --rm python:3.12-slim python --version
```

When the container stops, Docker automatically removes the container.

This is excellent for disposable one-off tasks.

Do not use it automatically for stateful learning services when you need to inspect or reuse the container.

---

## 11.4 `-it`

Interactive terminal:

```bash
docker run --rm -it python:3.12-slim
```

This is useful for exploration.

Inside the container you can run:

```python
>>> 2 + 3
5
```

Exit with:

```python
exit()
```

---

# 12. Container Registries

A natural question is:

> **Where does Docker get an image from?**

The answer is usually a **container registry**.

A registry is a service for storing and distributing container images.

Conceptually:

```text
Data Engineer
     │
     │ docker pull
     ▼
Container Registry
     │
     ▼
Repository
     │
     ▼
Image reference
     │
     ▼
Local image store
```

Common registry ecosystems include:

- Docker Hub.
- GitHub Container Registry.
- Cloud container registries.

This module focuses on consuming images, not administering registries.

---

# 13. Registry Vocabulary

## Registry

The distribution service.

Examples include Docker Hub and GitHub Container Registry.

## Namespace

A publisher or organizational namespace within a registry.

## Repository

A logical collection of image versions.

For example:

```text
postgres
```

or:

```text
some-company/data-service
```

## Tag

A human-friendly reference to an image version or release.

Example:

```text
postgres:16
```

## Digest

A content-addressed identifier for an exact image manifest/content reference.

Example:

```text
postgres@sha256:...
```

## Publisher

The organization or person responsible for publishing the image.

---

# 14. Docker Hub and Image Discovery

Before running an image, inspect its documentation.

Do not treat:

```bash
docker run SOME-IMAGE
```

as the end of the decision process.

Treat image selection as an engineering task.

## Image discovery checklist

For PostgreSQL, MinIO, Kafka, Redis, or another service, check:

1. Publisher.
2. Official/verified status where applicable.
3. Supported tags.
4. Supported architectures.
5. Required environment variables.
6. Ports.
7. Volumes/data directories.
8. Startup command.
9. Configuration requirements.
10. Health/readiness information.
11. Supported versions.
12. Official documentation.

### Example

Before using a PostgreSQL image, you should know:

```text
Image: PostgreSQL
Version: selected major version
Architecture: amd64/arm64/etc.
Port: 5432 inside the container
Required configuration: database/user/password settings
Data directory: image-documented PostgreSQL data path
Persistence: volume required for durable state
```

The complete service-operation curriculum comes in Topic 02.

---

# 15. Repository, Tags, and `latest`

Consider:

```text
postgres:16
```

Break it down:

```text
postgres
   │
   └── repository

16
 │
 └── tag
```

The tag is a convenient human-readable reference.

## Why `latest` is dangerous for reproducible labs

A tag is not necessarily immutable.

For example:

```text
my-service:latest
```

may refer to one image today and another image after the publisher updates the tag.

Therefore:

```text
latest
   ↓
human-friendly
   ↓
not a reliable immutable identity
```

For production-like learning environments, prefer deliberate version selection.

For example:

```bash
docker pull postgres:16
```

Then record the exact digest if reproducibility matters.

> **Professional habit:** choose versions deliberately rather than treating `latest` as a version-management strategy.

---

# 16. Tags vs Digests

This is one of the most important concepts in this topic.

## Tag

Example:

```text
postgres:16
```

A tag is a human-friendly reference.

It can move.

## Digest

Example:

```text
postgres@sha256:012345...
```

A digest identifies exact content at the registry/image-manifest level.

Conceptually:

```text
Tag
 ↓
"Give me the image currently referenced by this name"

Digest
 ↓
"Give me this exact content-addressed image reference"
```

### Why this matters

Imagine a team says:

> "Run PostgreSQL 16."

That gives you a version family.

For strict reproducibility, a digest provides a much stronger identity.

This matters when:

- reproducing a lab;
- comparing environments;
- investigating why two machines behave differently;
- creating deterministic test environments;
- recording exactly what was used.

---

# 17. Inspecting Images

Use:

```bash
docker image inspect IMAGE
```

Example:

```bash
docker pull python:3.12-slim
docker image inspect python:3.12-slim
```

The output contains structured metadata.

## Fields a Data Engineer should care about

### Architecture

Look for the image architecture.

This helps answer:

> Will this image run natively on my machine?

### OS

For example:

```text
linux
```

### Layers

Useful for understanding image structure and storage.

### Configuration

Inspect the image's configured runtime behavior.

### Environment

Useful for understanding image-provided environment configuration.

Do not assume an environment variable is safe merely because it appears in metadata.

### Entrypoint

The default program Docker expects to execute.

### Command

Default command behavior.

### Exposed ports

Signals which ports the image expects the application to use.

Important:

> An image exposing a port does not automatically publish that port to your host.

Publishing is a separate runtime operation covered in Topic 03.

### Volumes

Signals where the image expects persistent data.

Persistence is covered deeply in Topic 04.

---

# 18. Official, Verified, and Maintained Images

Not every image with a convincing name should be trusted.

Use a practical selection process:

```text
Need service
    ↓
Find candidate image
    ↓
Check publisher
    ↓
Read documentation
    ↓
Check supported versions
    ↓
Check architecture
    ↓
Check ports/configuration
    ↓
Check persistence requirements
    ↓
Choose and pin version
    ↓
Run
```

Prefer:

- official images where available;
- well-maintained publisher images;
- documented images;
- supported release lines;
- known provenance.

Be cautious with:

- random publishers;
- abandoned images;
- unexplained forks;
- images with unclear documentation;
- images that require unexplained privileged access.

> **"It runs" is not equivalent to "it is a good engineering dependency."**

This is an operational image-selection principle, not a guarantee that an official image is automatically free of all risk.

---

# 19. Image Architecture

Two important architectures are:

```text
linux/amd64
linux/arm64
```

### AMD64

Common on Intel and AMD x86-64 systems.

### ARM64

Common on:

- Apple Silicon Macs;
- many ARM servers;
- various ARM development machines.

Architecture matters because an image may support:

```text
linux/amd64
```

but not:

```text
linux/arm64
```

or vice versa.

---

# 20. Multi-Architecture Images

A modern image reference can represent multiple architecture-specific images.

Conceptually:

```text
postgres:16
     │
     ├── linux/amd64
     │
     ├── linux/arm64
     │
     └── other supported architectures
```

Docker can select the appropriate architecture for the machine when the image is published as multi-architecture.

This is a major reason containers are portable across developer machines.

### Why Data Engineers care

Suppose:

```text
Engineer A → Intel laptop
Engineer B → Apple Silicon laptop
```

Both use:

```bash
docker run postgres:16
```

If the image supports both architectures, Docker can obtain the appropriate image variant.

If it does not, architecture problems may appear.

---

# 21. Using `--platform`

You can explicitly request a platform:

```bash
docker run --platform linux/amd64 ...
```

For example:

```bash
docker run --rm --platform linux/amd64 python:3.12-slim python --version
```

## Why use it?

Possible reasons include:

- an image does not provide a native architecture variant;
- a lab explicitly requires a specific architecture;
- you need to reproduce an environment matching another system.

## Emulation

If your machine is ARM64 and the image is AMD64-only, Docker may use emulation when supported.

Conceptually:

```text
ARM64 machine
     │
     ▼
AMD64 container image
     │
     ▼
Emulation
     │
     ▼
Potential performance cost
```

Native architecture is generally preferable when available.

Do not treat:

```bash
--platform linux/amd64
```

as a universal fix.

First understand why the architecture differs.

---

# 22. Restart Policies

Docker supports restart policies including:

```text
no
on-failure
unless-stopped
always
```

## `no`

Do not automatically restart.

```bash
docker run --restart=no ...
```

Useful when you want failures to remain visible during troubleshooting.

## `on-failure`

Restart when the container exits with a failure status.

```bash
docker run --restart=on-failure ...
```

A restart limit can also be configured, for example:

```bash
docker run --restart=on-failure:5 ...
```

## `unless-stopped`

Restart the container unless it was deliberately stopped.

```bash
docker run --restart=unless-stopped ...
```

Useful for local services you want available across runtime restarts.

## `always`

Docker will always attempt to restart the container according to Docker's restart-policy behavior.

```bash
docker run --restart=always ...
```

## Operational warning

Restart policies can hide failures.

Imagine:

```text
Bad configuration
      ↓
Container exits
      ↓
Docker restarts it
      ↓
Container exits
      ↓
Docker restarts it
      ↓
Crash loop
```

If you only observe "it keeps restarting," you may miss the root cause.

During troubleshooting, inspect:

```bash
docker ps -a
docker logs <container>
docker inspect <container>
```

---

# 23. Registry Authentication and Rate Limits

Public registries can impose pull limits or other usage controls.

Repeated anonymous pulls may eventually fail or be throttled depending on the registry and account conditions.

A registry may support authenticated access.

Basic commands include:

```bash
docker login
```

and:

```bash
docker logout
```

Authentication can provide access to private repositories and, depending on the registry, different rate-limit behavior.

## Security rule

Never treat:

```bash
docker login
```

as permission to expose credentials.

Do not:

- commit registry credentials to Git;
- paste credentials into scripts;
- store credentials in plain text unnecessarily;
- reuse sensitive production passwords for local labs.

Use the credential-management mechanism provided by your runtime/registry.

---

# 24. Container Runtime Awareness

You should know the names of the major runtime components without turning this topic into a runtime-administration course.

## Docker Engine

The Docker platform commonly used to manage images and containers.

## containerd

A widely used container runtime component underneath many container platforms.

## Podman

An alternative container engine with strong Docker CLI compatibility for many workflows.

## Docker Desktop

A desktop environment that packages Docker functionality for development on platforms such as Windows and macOS.

## Colima

A lightweight development environment commonly used to provide a Linux container runtime on macOS.

## Rancher Desktop

A desktop container/Kubernetes development environment supporting container runtimes such as containerd and Docker-compatible workflows.

### Why this awareness matters

Your commands may look similar across runtimes:

```bash
docker ps
docker images
docker run ...
```

but:

- networking can differ;
- filesystem performance can differ;
- authentication/configuration can differ;
- platform integration can differ.

Do not assume "Docker-compatible" means "identical in every operational detail."

---

# 25. Data Engineering Use Cases

Containers become particularly valuable when you combine infrastructure services.

A typical local data lab might contain:

```text
┌───────────────────────────────────────────────┐
│                Local Data Lab                 │
│                                               │
│  PostgreSQL    MinIO      Kafka      Redis    │
│       ▲           ▲          ▲          ▲     │
│       └───────────┴──────────┴──────────┘     │
│                       │                       │
│                  Python code                  │
└───────────────────────────────────────────────┘
```

The fundamental chain is:

```text
Image
  ↓
Container
  ↓
Service
  ↓
Data Engineering pipeline
```

For example:

```text
Kafka
  ↓
Python consumer
  ↓
Transformation
  ↓
PostgreSQL / MinIO
```

Later topics will teach how services connect, persist data, configure credentials, and operate as a multi-service stack.

This topic establishes the first layer:

> **Know exactly what software you are running and where it came from.**

---

# 26. Hands-On Lab — `docker_lab/01`

Create:

```text
docker_lab/
└── 01/
    └── README.md
```

Record your commands, observations, and failures.

## Exercise 1 — Hello World

Run:

```bash
docker run hello-world
```

Observe the output.

Then run:

```bash
docker ps -a
```

### Questions

- Was a container created?
- Is it still running?
- Why did it stop?
- Does the image remain locally?

---

## Exercise 2 — Interactive Python

Run:

```bash
docker run --rm -it python:3.12-slim
```

Inside Python:

```python
print("Hello from a container")
2 + 3
```

Then:

```python
exit()
```

### Observe

The `--rm` option means the container is automatically removed after it stops.

Verify:

```bash
docker ps -a
```

The temporary container should not remain.

---

## Exercise 3 — Detached Container

Run:

```bash
docker run -d --name python-lab python:3.12-slim sleep 3600
```

Check:

```bash
docker ps
```

Then:

```bash
docker ps -a
```

Stop it:

```bash
docker stop python-lab
```

Check:

```bash
docker ps -a
```

Start it:

```bash
docker start python-lab
```

Restart it:

```bash
docker restart python-lab
```

Finally:

```bash
docker stop python-lab
docker rm python-lab
```

Check:

```bash
docker ps -a
```

### Record the lifecycle

```text
create/start
   ↓
running
   ↓
stop
   ↓
stopped
   ↓
start
   ↓
running
   ↓
stop
   ↓
remove
```

---

## Exercise 4 — `--rm`

Run:

```bash
docker run --rm python:3.12-slim python --version
```

Then:

```bash
docker ps -a
```

Explain why the container is absent.

Mental model:

```text
docker run
    ↓
create container
    ↓
run command
    ↓
command exits
    ↓
--rm removes container
```

---

## Exercise 5 — PostgreSQL Version Pinning

Pull a deliberate version:

```bash
docker pull postgres:16
```

Inspect it:

```bash
docker image inspect postgres:16
```

Record:

- repository;
- tag;
- architecture;
- OS;
- image ID;
- layer information;
- relevant configuration metadata.

Then identify the digest information returned by the image inspection.

Record the exact image identity you used in:

```text
docker_lab/01/notes.md
```

The objective is not merely:

> "I used PostgreSQL."

The objective is:

> "I used this PostgreSQL image reference, for this architecture, and I know how to identify the exact image content."

---

## Exercise 6 — Architecture

First identify your host architecture using your operating system's normal system-information command.

Then inspect the image:

```bash
docker image inspect postgres:16
```

Compare the architecture information.

If appropriate for your machine and the image:

```bash
docker run --rm --platform linux/amd64 postgres:16
```

Do not leave a long-running database process running just for this exercise.

The objective is to understand:

```text
Host architecture
       ↓
Image architecture
       ↓
Native execution OR emulation
       ↓
Potential performance difference
```

---

# 27. Break/Fix Troubleshooting Exercises

Professional operators learn from controlled failure.

Use:

> **Predict → Run → Inspect → Break → Diagnose → Fix**

## Failure 1 — Nonexistent Image Tag

Try:

```bash
docker pull postgres:this-tag-does-not-exist
```

Observe the error.

Determine:

- Is this a local container failure?
- Is the image reference invalid?
- What does the registry tell you?

Fix it using a valid documented tag.

---

## Failure 2 — Duplicate Container Name

Run:

```bash
docker run --name duplicate-lab --rm python:3.12-slim python --version
```

Then create a long-running container:

```bash
docker run -d --name duplicate-lab python:3.12-slim sleep 3600
```

Try to create another container with the same name:

```bash
docker run -d --name duplicate-lab python:3.12-slim sleep 3600
```

Diagnose the name collision.

Inspect:

```bash
docker ps -a
```

Fix deliberately rather than deleting containers blindly.

Clean up:

```bash
docker rm -f duplicate-lab
```

> **Warning:** `docker rm -f` force-removes a container. Use it only for this disposable lab.

---

## Failure 3 — Architecture Mismatch

On a platform where an appropriate incompatible image can be demonstrated, request an architecture deliberately:

```bash
docker run --rm --platform linux/amd64 IMAGE
```

Compare the result with a native architecture.

Record:

- host architecture;
- requested image architecture;
- whether emulation was involved;
- performance observations.

---

## Failure 4 — Unexpected Tag

Compare a deliberate version reference with an unpinned reference.

For example:

```bash
docker pull postgres:16
```

versus an image reference using a broad/mutable tag where supported.

Ask:

> If the publisher changes the mutable tag, will a future pull necessarily produce identical image content?

Answer: no.

This is why reproducibility requires deliberate version and, when necessary, digest pinning.

---

## Failure 5 — Stopped Containers

Create disposable containers:

```bash
docker run --name stopped-1 python:3.12-slim python --version
docker run --name stopped-2 python:3.12-slim python --version
```

Then:

```bash
docker ps
```

and:

```bash
docker ps -a
```

Explain why the containers appear in `docker ps -a` but not in `docker ps`.

Remove only the containers you created for the exercise:

```bash
docker rm stopped-1 stopped-2
```

---

# 28. Real-World Data Engineering Scenarios

## Scenario 1 — "I need PostgreSQL locally."

A professional workflow is:

```text
Need PostgreSQL
      ↓
Find documented image
      ↓
Check publisher
      ↓
Check supported version
      ↓
Check architecture
      ↓
Read configuration requirements
      ↓
Choose version
      ↓
Pull image
      ↓
Inspect image
      ↓
Run container
```

Do not begin by blindly typing:

```bash
docker run postgres
```

without understanding the image and version you selected.

Topic 02 will cover the complete PostgreSQL service-operation workflow.

---

## Scenario 2 — "My colleague's lab works, but mine behaves differently."

Compare:

```text
Image repository
Image tag
Image digest
Architecture
Container runtime
Host platform
```

A useful diagnostic question is:

> Are we actually running the same image content?

Two people can both say:

```text
postgres:16
```

while their locally resolved image content may differ if the tag has moved since one machine pulled it.

---

## Scenario 3 — "Kafka works on Intel but not Apple Silicon."

Investigate:

```text
Intel/AMD → linux/amd64
Apple Silicon → linux/arm64
```

Then determine whether the Kafka image supports both architectures.

Do not immediately assume Kafka itself is broken.

First establish:

```text
Host architecture
       ↓
Image architecture
       ↓
Native or emulated execution
       ↓
Runtime behavior
```

---

## Scenario 4 — "The image worked last month but behaves differently now."

Possible explanation:

```text
Mutable tag
     ↓
Publisher updates tag
     ↓
docker pull later
     ↓
Different image content
```

Use digest information to establish exact image identity.

---

## Scenario 5 — "My machine has many old containers."

Inspect:

```bash
docker ps -a
```

Then inspect local images:

```bash
docker images
```

Do not immediately run a broad destructive cleanup command.

First determine:

- which containers belong to active labs;
- which images are still needed;
- which containers are disposable.

Cleanup is covered systematically in Topic 09.

---

# 29. Mental Models You Must Remember

## Model 1 — Image vs Container

```text
Image     = reusable read-only template
Container = runtime instance
```

---

## Model 2 — Registry

```text
Registry
   ↓
Repository
   ↓
Image reference
   ↓
Local image
```

---

## Model 3 — Tag vs Digest

```text
Tag
 = human-friendly reference
 = can move

Digest
 = content-addressed identity
 = identifies exact referenced content
```

---

## Model 4 — Lifecycle

```text
Image
  ↓
Create
  ↓
Start
  ↓
Running
  ↓
Stop
  ↓
Start/Restart
  ↓
Remove
```

---

## Model 5 — Core Commands

```text
docker pull
    ↓
download image

docker run
    ↓
create + start container

docker stop
    ↓
stop container process

docker start
    ↓
start existing container

docker restart
    ↓
stop + start

docker rm
    ↓
remove container

docker rmi
    ↓
remove local image
```

---

## Model 6 — Architecture

```text
Image reference
      ↓
Architecture selection
      ↓
linux/amd64 OR linux/arm64
      ↓
Native execution preferred
```

---

## Model 7 — Professional Image Selection

```text
Need service
    ↓
Trustworthy publisher
    ↓
Documentation
    ↓
Supported version
    ↓
Architecture
    ↓
Configuration
    ↓
Persistence
    ↓
Pin version
    ↓
Run
```

---

# 30. Command Reference

## Image Commands

| Command | Purpose | Example | Data Engineering use |
|---|---|---|---|
| `docker pull` | Download an image | `docker pull postgres:16` | Acquire a selected service version |
| `docker images` | List local images | `docker images` | Inspect available lab images |
| `docker image inspect` | Inspect image metadata | `docker image inspect postgres:16` | Check architecture/configuration |
| `docker rmi` | Remove local image | `docker rmi IMAGE` | Deliberate image housekeeping |

## Container Commands

| Command | Purpose | Example | Data Engineering use |
|---|---|---|---|
| `docker run` | Create + start | `docker run --name pg postgres:16` | Start a service |
| `docker create` | Create without starting | `docker create --name pg postgres:16` | Inspect lifecycle explicitly |
| `docker ps` | Show running containers | `docker ps` | Check active services |
| `docker ps -a` | Show all containers | `docker ps -a` | Investigate stopped/failed containers |
| `docker stop` | Stop container | `docker stop pg` | Stop a lab service |
| `docker start` | Start stopped container | `docker start pg` | Resume a lab service |
| `docker restart` | Restart container | `docker restart pg` | Apply/retest runtime behavior |
| `docker rm` | Remove container | `docker rm pg` | Remove disposable lab state |

## Important `docker run` options

| Option | Meaning | Example |
|---|---|---|
| `--name` | Predictable container name | `--name pg-lab` |
| `-d` | Detached/background mode | `-d` |
| `--rm` | Remove container after it exits | `--rm` |
| `-it` | Interactive terminal | `-it` |
| `--platform` | Request a specific platform | `--platform linux/amd64` |
| `--restart` | Configure restart behavior | `--restart unless-stopped` |

## Registry Commands

```bash
docker login
docker logout
```

Use registry authentication only through appropriate credential handling.

---

# 31. Common Mistakes

## Mistake 1 — Using `latest` automatically

**Why it happens:** It is short and convenient.

**Problem:** The reference may move.

**Correct approach:** Select a deliberate supported version and record the exact identity when reproducibility matters.

---

## Mistake 2 — Confusing stopping with removing

```text
stop ≠ remove
```

`docker stop` stops the container.

`docker rm` removes the container.

---

## Mistake 3 — Accumulating stopped containers

Use:

```bash
docker ps -a
```

regularly during local labs.

---

## Mistake 4 — Running random images

A successful pull does not prove that an image is a good dependency.

Check:

- publisher;
- documentation;
- maintenance;
- version;
- architecture.

---

## Mistake 5 — Ignoring architecture

An image reference may not have the architecture your machine needs.

Check architecture before debugging application behavior.

---

## Mistake 6 — Assuming every image works on every CPU

```text
amd64 ≠ arm64
```

Multi-architecture support solves this when the publisher provides the appropriate variants.

---

## Mistake 7 — Blindly using `--platform`

`--platform` can request a different architecture, but it may invoke emulation.

Understand the trade-off first.

---

## Mistake 8 — Confusing tags and digests

A tag is convenient.

A digest provides exact content-addressed identity.

They solve different problems.

---

## Mistake 9 — Ignoring image documentation

Images are not interchangeable black boxes.

Different images can have different:

- commands;
- environment variables;
- ports;
- persistence paths;
- architectures;
- startup requirements.

---

## Mistake 10 — Misunderstanding restart policies

Automatic restarting can turn a failure into a confusing restart loop.

Always inspect:

```bash
docker ps -a
docker logs <container>
docker inspect <container>
```

---

## Mistake 11 — Repeatedly pulling images without understanding why

Repeated pulls can consume bandwidth and may interact with registry limits.

Understand what image version you already have.

---

## Mistake 12 — Exposing registry credentials insecurely

Do not put credentials into:

- Git;
- shared scripts;
- screenshots;
- public documentation;
- reusable lab files.

---

# 32. Knowledge Checkpoint

Do not move forward until you can answer these without relying on memorized commands.

- [ ] What is a container?
- [ ] How is a container different from a process?
- [ ] How is a container different from a virtual machine?
- [ ] What is an image?
- [ ] How does an image become a container?
- [ ] What are image layers?
- [ ] Why can multiple images share layers?
- [ ] What is the difference between an image and a container?
- [ ] What does `docker run` conceptually do?
- [ ] What is the difference between `docker stop` and `docker rm`?
- [ ] What is a registry?
- [ ] What is a repository?
- [ ] What is a tag?
- [ ] Why can `latest` be problematic?
- [ ] What is a digest?
- [ ] Why are digests useful for reproducibility?
- [ ] How do you inspect an image?
- [ ] How do you check image architecture?
- [ ] What are `linux/amd64` and `linux/arm64`?
- [ ] What is a multi-architecture image?
- [ ] What does `--platform` do?
- [ ] Why can emulation reduce performance?
- [ ] What does each restart policy mean?
- [ ] How can restart policies complicate troubleshooting?
- [ ] Why do registry rate limits matter?
- [ ] What does `docker login` do?
- [ ] What are Docker Engine, containerd, and Podman at a high level?

### Practical checkpoint

From a clean learning environment, demonstrate that you can:

1. Pull an image.
2. Inspect it.
3. Explain its architecture.
4. Run a named container.
5. Find it with `docker ps`.
6. Stop it.
7. Start it again.
8. Restart it.
9. Remove it.
10. Explain what happened to the image.

---

# 33. Practice Questions

## Beginner

### Q1. What is a container?

**Answer:** A container is an isolated runtime environment for a process, with controlled filesystem, networking, resources, and configuration.

---

### Q2. Is a container a virtual machine?

**Answer:** No. A normal Linux container does not contain its own guest kernel. It uses OS-level isolation and normally shares the host kernel.

---

### Q3. What is a Docker image?

**Answer:** A read-only packaged template used to create containers.

---

### Q4. What is the difference between an image and a container?

**Answer:** An image is the reusable template; a container is a runtime instance created from that image.

---

### Q5. What command lists running containers?

```bash
docker ps
```

---

### Q6. What command lists stopped containers too?

```bash
docker ps -a
```

---

### Q7. What does `--rm` do?

**Answer:** It tells Docker to automatically remove the container after it exits.

---

### Q8. Why would you use `--name`?

**Answer:** To give a container a predictable name that is easier to operate and troubleshoot.

---

## Intermediate

### Q9. What happens conceptually when you run:

```bash
docker run python:3.12-slim
```

**Answer:** Docker resolves the image reference, uses the image to create a container, and starts its configured process.

---

### Q10. You execute:

```bash
docker stop my-container
```

Is the container removed?

**Answer:** No. It is stopped. Use `docker rm` to remove the container.

---

### Q11. Why can an image remain after a container is removed?

**Answer:** The image and container are separate objects. The image can be reused to create other containers.

---

### Q12. Why does Docker use image layers?

**Answer:** Layers enable reuse, storage efficiency, and efficient distribution of shared image content.

---

### Q13. Why is `latest` not a reliable reproducibility mechanism?

**Answer:** Tags can move. A later pull of the same tag can resolve to different image content.

---

### Q14. Why use a digest?

**Answer:** To identify exact content-addressed image information and strengthen reproducibility.

---

### Q15. What should you inspect before selecting a PostgreSQL image?

**Answer:** Publisher/provenance, supported version, architecture, ports, environment variables, persistence requirements, startup behavior, and documentation.

---

## Advanced

### Q16. Two engineers both report that they are using `postgres:16`. Their behavior differs. What should you investigate?

**Answer:**

```text
Tag resolution
Digest
Architecture
Runtime
Platform
Configuration
```

First establish whether they are actually using the same image content.

---

### Q17. An ARM64 laptop is asked to run an AMD64-only image. What can happen?

**Answer:** Docker may be able to use emulation if supported. The image can run, but performance may be worse than native execution.

---

### Q18. Why can a restart policy make troubleshooting harder?

**Answer:** A failing process can be repeatedly restarted, producing a crash loop that hides the initial failure unless you inspect logs, state, and exit information.

---

### Q19. A container starts successfully but exits immediately. Is that necessarily an image problem?

**Answer:** No. The container's configured process may simply have completed, or the application may have failed. Inspect the container state and logs before concluding.

---

### Q20. What is the professional image-selection process?

**Answer:**

```text
Need service
→ publisher
→ documentation
→ supported version
→ architecture
→ configuration
→ persistence
→ version selection
→ inspect
→ run
```

---

# 34. Data Engineering Interview Practice

## Q1. What is a container?

### Short answer

A container is an isolated process environment managed by a container runtime.

### Detailed explanation

It provides controlled filesystem, networking, resources, and configuration while normally sharing the host kernel in the Linux-container model.

### Data Engineering example

PostgreSQL, Kafka, and MinIO can run as separate containers on a local data-lab machine.

---

## Q2. Container vs VM?

### Short answer

A container provides OS-level process isolation, while a VM virtualizes a complete machine and normally runs a guest OS/kernel.

### Data Engineering example

A local Kafka container is generally lighter than running an entire guest VM solely for Kafka.

---

## Q3. Image vs container?

### Short answer

Image = reusable read-only template.

Container = runtime instance.

### Data Engineering example

One PostgreSQL image can create separate development and test containers.

---

## Q4. What is an image layer?

### Short answer

An image layer is a component of an image's layered filesystem.

### Why it matters

Layers allow common content to be reused and reduce redundant storage/distribution.

---

## Q5. What is a registry?

### Short answer

A registry distributes container images.

### Example

Docker Hub or a company's private registry.

---

## Q6. Tag vs digest?

### Short answer

A tag is a human-friendly reference that can move; a digest provides content-addressed image identity.

### Data Engineering example

A team can record the digest used for a reproducible local integration test.

---

## Q7. Why can `latest` be dangerous?

### Short answer

Because `latest` is a mutable tag rather than a guarantee of immutable image content.

---

## Q8. What is a multi-architecture image?

### Short answer

An image reference that can resolve to architecture-specific image variants, such as `linux/amd64` and `linux/arm64`.

---

## Q9. Why can an image work on AMD64 but fail on ARM64?

### Short answer

The image may not contain a compatible ARM64 variant, or an application/dependency inside the image may not support the architecture.

---

## Q10. What does `--platform` do?

### Short answer

It requests a specific target platform, such as:

```bash
--platform linux/amd64
```

If the target differs from the host, emulation may be involved.

---

## Q11. What are restart policies?

### Short answer

Policies controlling whether Docker automatically restarts a container after it exits.

---

## Q12. Difference between `docker stop` and `docker rm`?

### Short answer

`stop` stops the container; `rm` removes the container object.

---

## Q13. What happens when you run `docker run`?

### Short answer

Conceptually, Docker resolves/uses an image, creates a new container, and starts its configured process.

---

## Q14. Why should production-like labs pin image versions?

### Short answer

To reduce unexpected environmental changes and improve reproducibility.

---

## Q15. How would you select a trustworthy PostgreSQL image?

### Strong answer

I would check the publisher and documentation, confirm supported PostgreSQL versions and architectures, review configuration and persistence requirements, select an intentional version rather than blindly using `latest`, inspect the image, and record the exact image identity when reproducibility matters.

---

# 35. Final Mastery Checklist

You have mastered Topic 01 when you can confidently explain and demonstrate:

### Container fundamentals

- [ ] Process vs container.
- [ ] Container isolation.
- [ ] Container vs VM.
- [ ] Container filesystem/network/resource concepts.
- [ ] Why containers are lightweight.

### Images

- [ ] Image definition.
- [ ] Image vs container.
- [ ] Image layers.
- [ ] Writable container layer.
- [ ] Image reuse.
- [ ] Image persistence after container removal.

### Lifecycle

- [ ] `docker create`
- [ ] `docker run`
- [ ] `docker start`
- [ ] `docker stop`
- [ ] `docker restart`
- [ ] `docker rm`
- [ ] `docker ps`
- [ ] `docker ps -a`

### Image operations

- [ ] `docker pull`
- [ ] `docker images`
- [ ] `docker image inspect`
- [ ] `docker rmi`
- [ ] `--name`
- [ ] `-d`
- [ ] `--rm`
- [ ] `-it`

### Registries

- [ ] Registry.
- [ ] Repository.
- [ ] Namespace.
- [ ] Publisher.
- [ ] Tag.
- [ ] Digest.
- [ ] Docker Hub awareness.
- [ ] GitHub Container Registry awareness.
- [ ] Cloud registry awareness.

### Reproducibility

- [ ] Understand mutable tags.
- [ ] Understand `latest`.
- [ ] Understand digests.
- [ ] Explain why version pinning matters.

### Architecture

- [ ] `linux/amd64`.
- [ ] `linux/arm64`.
- [ ] Multi-architecture images.
- [ ] `--platform`.
- [ ] Emulation trade-offs.
- [ ] Native execution preference.

### Operations

- [ ] Restart policies.
- [ ] Registry authentication.
- [ ] Registry rate-limit awareness.
- [ ] Docker Engine awareness.
- [ ] containerd awareness.
- [ ] Podman awareness.
- [ ] Docker Desktop awareness.
- [ ] Colima awareness.
- [ ] Rancher Desktop awareness.

### Data Engineering

- [ ] Explain why image/container knowledge matters for PostgreSQL.
- [ ] Explain why it matters for MinIO.
- [ ] Explain why it matters for Kafka.
- [ ] Explain why it matters for Redis.
- [ ] Explain why it matters for Python-based pipelines.

### Practical mastery

- [ ] Complete `docker_lab/01`.
- [ ] Complete break/fix exercises.
- [ ] Complete practice questions.
- [ ] Complete interview practice.
- [ ] Explain the entire image → container lifecycle without notes.

---

# 36. Final Professional Mental Model

When you encounter a containerized Data Engineering service, think in this order:

```text
                    DATA ENGINEERING SERVICE
                              │
                              ▼
                     What am I running?
                              │
                              ▼
                         Image source
                              │
                              ▼
                    Publisher / provenance
                              │
                              ▼
                       Repository + tag
                              │
                              ▼
                           Digest
                              │
                              ▼
                         Architecture
                              │
                              ▼
                    Image configuration
                              │
                              ▼
                         Container
                              │
                              ▼
                    Container lifecycle
                              │
                              ▼
                         Service
                              │
                              ▼
                    Data Engineering lab
```

A professional Data Engineer does not think:

> "What Docker command do I copy?"

They think:

> **"What exact software am I running, where did it come from, which version and architecture am I using, what state does the container represent, and how can I reproduce and operate it safely?"**

That mindset is the foundation for Topic 02 and every subsequent containerized Data Engineering lab.
