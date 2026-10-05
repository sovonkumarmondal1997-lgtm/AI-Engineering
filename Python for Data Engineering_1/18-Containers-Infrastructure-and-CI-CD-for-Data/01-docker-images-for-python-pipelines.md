# Docker Images for Python Pipelines

> **Module:** Stage 2 — Python for Data Engineering  
> **Topic:** 01 — Docker Images for Python Pipelines  
> **Goal:** Build secure, reproducible, efficient, production-ready Docker images for Python data-engineering workloads.

---

## Learning Objectives

By the end of this module, you should be able to:

- Explain why containers solve the “works on my machine” problem.
- Distinguish containers from virtual machines.
- Explain Dockerfiles, images, containers, layers, registries, repositories, tags, and digests.
- Build, run, inspect, debug, stop, and remove Docker containers.
- Write Dockerfiles for Python applications and data pipelines.
- Control Docker build context with `.dockerignore`.
- Design Dockerfiles for effective layer caching.
- Select an appropriate Python base image.
- Use `uv` and `uv.lock` for reproducible Python dependencies.
- Build multi-stage images.
- Run production containers as a non-root user.
- Externalize runtime configuration.
- Design correct `ENTRYPOINT`/`CMD` behavior and graceful signal handling.
- Understand PID 1 and container lifecycle behavior.
- Use `HEALTHCHECK` appropriately.
- Make images reproducible and identifiable by immutable tags and digests.
- Scan images for vulnerabilities and generate SBOMs.
- Use BuildKit build secrets without embedding credentials in image layers.
- Build images for `linux/amd64` and `linux/arm64` with `buildx`.
- Design images for Python pipelines, dbt, PySpark, and orchestrated workloads.
- Measure image size, build time, cache reuse, and vulnerability changes.
- Debug common production image failures.
- Explain Docker image engineering at Senior Data Engineer interview depth.

---

# 1. Why Containerization Matters in Data Engineering

## 1.1 The “It Works on My Machine” Problem

A data pipeline is not just Python source code.

A real pipeline depends on a runtime environment:

```text
Python version
+ Python packages
+ native libraries
+ operating-system packages
+ filesystem layout
+ environment configuration
+ executable binaries
+ runtime behavior
= execution environment
```

Suppose an engineer develops an API ingestion pipeline with:

```text
Python 3.12
requests
pyarrow
pandas
boto3
uv
```

It works locally.

The code is committed to Git and executed in CI. CI fails.

The code may be identical, but the environments are not.

For example:

```text
Developer laptop
Python 3.12.6
glibc version A
pyarrow version A
OpenSSL version A

CI runner
Python 3.12.4
glibc version B
pyarrow version B
OpenSSL version B
```

A dependency can behave differently because of:

- Python version
- package version
- operating-system library
- CPU architecture
- native binary compatibility
- environment variables
- filesystem permissions
- installed system tools

The result is the classic:

> “It works on my machine.”

## 1.2 What a Container Changes

A container packages an application with a controlled runtime environment.

Conceptually:

```text
Application
+
Python runtime
+
Python dependencies
+
Required OS libraries
+
Runtime configuration interface
+
Execution metadata
```

This creates a more consistent artifact that can move through:

```text
Developer
   ↓
Docker image
   ↓
CI
   ↓
Registry
   ↓
Staging
   ↓
Production
```

The important idea is:

> **The image becomes the portable unit of execution.**

This matters later in this module series because the same image can become the unit used by:

- Docker Compose
- Kubernetes
- CI/CD
- production data workloads

This topic therefore establishes the foundation for the remaining container and delivery topics.

## 1.3 Containerization Does Not Mean “Everything Is Identical”

Containers improve reproducibility; they do not magically eliminate every environmental dependency.

For example:

```text
Container image
    +
Host kernel
    +
CPU architecture
    +
Container runtime
    +
External services
    +
Runtime configuration
```

A container normally shares the host kernel rather than carrying a complete guest operating system.

Therefore, a production engineer still needs to understand:

- architecture compatibility
- kernel behavior
- permissions
- networking
- storage
- external services
- secrets
- configuration

### Data-engineering relevance

Data workloads are especially sensitive to environment differences because they commonly use packages containing native components:

- PyArrow
- NumPy
- pandas
- database drivers
- compression libraries
- cryptographic libraries
- Spark/JVM components

### Mental model

> **A container is a controlled execution environment, not a magic bubble that eliminates all dependencies.**

### Knowledge Check

Before continuing, you should be able to:

- [ ] Explain why the same Python source can behave differently in CI.
- [ ] Explain what an image packages.
- [ ] Explain why containers improve reproducibility.
- [ ] Name at least three dependencies outside Python source code.

---

# 2. Containers vs Virtual Machines

## 2.1 Virtual Machines

A virtual machine emulates or virtualizes a complete machine environment.

A simplified architecture is:

```text
Physical hardware
      ↓
Host OS / Hypervisor
      ↓
Guest OS
      ↓
Application
```

A VM normally includes:

- guest kernel
- system libraries
- filesystem
- application
- dependencies

This gives strong isolation, but it also introduces more overhead.

## 2.2 Containers

A simplified container architecture is:

```text
Physical hardware
      ↓
Host OS
      ↓
Container runtime
      ↓
Container process
      ↓
Application
```

Containers generally share the host kernel.

A useful conceptual comparison:

| Characteristic | Container | Virtual Machine |
|---|---|---|
| Isolation | Process-level / OS-level mechanisms | Full guest OS boundary |
| Kernel | Generally shares host kernel | Guest kernel |
| Startup | Usually fast | Usually slower |
| Resource overhead | Lower | Higher |
| Packaging | Application + runtime filesystem/configuration | Complete guest OS + application |
| Typical data-engineering use | Pipelines, services, jobs, task images | Stronger isolation or VM-based infrastructure |

Do not interpret this as “containers are always less secure.”

Security depends on:

- runtime configuration
- kernel hardening
- privileges
- isolation technology
- workload
- threat model

Containers are not automatically equivalent to VMs as an isolation boundary.

## 2.3 Why Containers Are Useful for Data Pipelines

A pipeline image can define:

```text
Python 3.12
uv.lock
system libraries
application code
entrypoint
runtime user
```

The scheduler can then execute the same artifact in multiple environments.

For example:

```text
Airflow task
    ↓
pipeline image
    ↓
Python ingestion process
    ↓
S3/object storage
```

The image is independent of the developer’s local Python installation.

### Mental model

> **VM = package a whole machine. Container = package an application runtime around a process.**

### Knowledge Check

- [ ] Can you explain why a container normally shares the host kernel?
- [ ] Can you explain why a VM carries a guest OS?
- [ ] Can you explain why neither abstraction should automatically be called “more secure”?

---

# 3. Docker Mental Model

A beginner should understand this relationship before memorizing commands:

```text
Dockerfile
    ↓
Docker Image
    ↓
Container
    ↓
Process
```

## 3.1 Dockerfile

A Dockerfile is a set of instructions describing how to construct an image.

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src

CMD ["python", "-m", "pipeline"]
```

## 3.2 Image

An image is a packaged filesystem plus metadata/configuration required to create a container.

It is not a running process.

An image can be stored in a registry.

## 3.3 Container

A container is a runtime instance of an image.

You can create multiple containers from the same image:

```text
pipeline:abc123
      ↓
 ┌────┴────┐
 ↓         ↓
container container
```

The image is the artifact. The container is the execution instance.

## 3.4 Layers

Images are assembled from layers.

Conceptually:

```text
Image
├── Base OS layer
├── Python runtime layer
├── Dependency layer
└── Application layer
```

Layers allow Docker to reuse unchanged work.

This is why Dockerfile structure affects build performance.

## 3.5 Registry

A registry stores container images.

Conceptually:

```text
Developer
   ↓
docker build
   ↓
Image
   ↓
docker push
   ↓
Registry
   ↓
docker pull
   ↓
CI / Production
```

A registry can be public or private.

## 3.6 Repository

A repository groups image versions under a name.

Example:

```text
company/data-pipelines
```

## 3.7 Tag

A tag is a human-readable reference.

Examples:

```text
company/data-pipelines:latest
company/data-pipelines:1.4.0
company/data-pipelines:git-abc123
```

A tag is generally mutable.

## 3.8 Digest

A digest identifies an image content-addressably.

Example:

```text
company/data-pipelines@sha256:...
```

The exact digest should be obtained from the registry or Docker tooling; never invent one.

### Critical production distinction

```text
Tag    → human-friendly reference
Digest → exact image content reference
Git SHA → source revision
```

They are related but not interchangeable.

### Mental model

> **Dockerfile describes. Image packages. Container runs. Registry distributes. Tag names. Digest identifies exact content.**

---

# 4. Images, Containers, Layers, Registries, Tags, and Digests

A useful lifecycle is:

```text
Dockerfile
   ↓
docker build
   ↓
Image
   ↓
Tag
   ↓
Registry
   ↓
Digest
   ↓
Container
```

For production, you want to be able to answer:

> “Exactly what artifact is running?”

A strong answer might identify:

```text
Repository:
company/ingestion

Git commit:
abc123...

Image tag:
git-abc123

Image digest:
sha256:...
```

This makes debugging and rollback substantially easier.

## 4.1 Mutable vs Immutable References

Avoid treating:

```text
latest
```

as a production release identifier.

If:

```text
company/pipeline:latest
```

points to a new image tomorrow, the same reference now means something different.

An immutable strategy is:

```text
company/pipeline:git-abc123
```

and preferably recording the resulting digest:

```text
company/pipeline@sha256:...
```

### Knowledge Check

- [ ] Can you distinguish an image from a container?
- [ ] Can you explain a layer?
- [ ] Can you explain what a registry does?
- [ ] Can you explain why a digest is stronger than a mutable tag for artifact identity?

---

# 5. Docker CLI Fundamentals

The following commands form the basic workflow.

## 5.1 `docker build`

Build an image:

```bash
docker build -t pipeline:dev .
```

Meaning:

- `docker build` — construct an image
- `-t pipeline:dev` — assign a name and tag
- `.` — use the current directory as build context

## 5.2 `docker run`

Run a container:

```bash
docker run --rm pipeline:dev
```

`--rm` removes the container after it exits.

## 5.3 `docker ps`

Show running containers:

```bash
docker ps
```

## 5.4 `docker ps -a`

Show running and stopped containers:

```bash
docker ps -a
```

## 5.5 `docker logs`

Read container output:

```bash
docker logs <container-id>
```

For a long-running process:

```bash
docker logs -f <container-id>
```

## 5.6 `docker exec`

Execute a command inside a running container:

```bash
docker exec -it <container-id> /bin/sh
```

This is useful for debugging.

Do not treat shell access as a substitute for observability in production.

## 5.7 `docker stop`

Request graceful termination:

```bash
docker stop <container-id>
```

Docker normally sends a termination signal before forcing termination after the configured grace period.

## 5.8 `docker rm`

Remove a stopped container:

```bash
docker rm <container-id>
```

## 5.9 `docker images`

List local images:

```bash
docker images
```

## 5.10 `docker pull`

Pull an image:

```bash
docker pull python:3.12-slim
```

## 5.11 `docker push`

Push an image:

```bash
docker push company/pipeline:git-abc123
```

This requires appropriate registry authentication and permissions.

## 5.12 Practical Workflow

```text
Build
  ↓
Run
  ↓
Inspect
  ↓
Read logs
  ↓
Execute debugging command
  ↓
Stop
  ↓
Remove
```

Example:

```bash
docker build -t pipeline:dev .
docker run --name pipeline-dev pipeline:dev
docker ps -a
docker logs pipeline-dev
docker exec -it pipeline-dev /bin/sh
docker stop pipeline-dev
docker rm pipeline-dev
```

### Common mistake

A common beginner pattern is:

```bash
docker run ...
```

followed by immediately assuming the application is working.

Instead:

```bash
docker ps -a
docker logs <container>
```

should become habitual debugging steps.

### Knowledge Check

- [ ] Can you build an image?
- [ ] Can you run it?
- [ ] Can you inspect stopped containers?
- [ ] Can you read logs?
- [ ] Can you execute a debugging command?

---

# 6. Dockerfile Fundamentals

A Dockerfile describes image construction.

We will start deliberately simple.

Repository:

```text
pipeline/
├── src/
│   └── pipeline/
│       ├── __init__.py
│       └── main.py
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

A minimal Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN pip install .

CMD ["python", "-m", "pipeline"]
```

This is intentionally not the final production design.

We will improve it progressively.

## 6.1 `FROM`

```dockerfile
FROM python:3.12-slim
```

Defines the base image.

It determines much of the starting filesystem and runtime environment.

Production considerations:

- choose a maintained base
- understand the OS distribution
- understand architecture availability
- pin more strongly when reproducibility requires it

## 6.2 `WORKDIR`

```dockerfile
WORKDIR /app
```

Sets the working directory for subsequent instructions and the default process working directory.

This is preferable to repeatedly writing:

```dockerfile
RUN cd /app && ...
```

## 6.3 `COPY`

```dockerfile
COPY pyproject.toml uv.lock ./
```

Copies files from the build context into the image.

Be careful about what exists in the build context.

## 6.4 `RUN`

```dockerfile
RUN python -m pip install ...
```

Executes a build-time command.

For example:

```dockerfile
RUN apt-get update && apt-get install -y ...
```

can add system dependencies.

Production consideration:

- minimize unnecessary packages
- clean package-manager metadata when appropriate
- avoid embedding credentials

## 6.5 `ENV`

```dockerfile
ENV PYTHONUNBUFFERED=1
```

Defines environment configuration in the image.

Use it for appropriate non-secret defaults.

Do not use it to bake credentials into the image.

## 6.6 `ARG`

```dockerfile
ARG APP_VERSION=dev
```

Defines a build-time argument.

It can influence image construction.

Example:

```bash
docker build --build-arg APP_VERSION=1.4.0 .
```

`ARG` is not a secrets mechanism.

## 6.7 `USER`

```dockerfile
USER app
```

Changes the user under which later runtime commands execute.

Running production workloads as non-root is an important least-privilege practice.

## 6.8 `ENTRYPOINT`

```dockerfile
ENTRYPOINT ["python", "-m", "pipeline"]
```

Defines the primary executable behavior.

Exec form is important for correct signal behavior.

## 6.9 `CMD`

```dockerfile
CMD ["--help"]
```

Provides default arguments or a default command depending on the image design.

Example:

```dockerfile
ENTRYPOINT ["python", "-m", "pipeline"]
CMD ["--help"]
```

Then:

```bash
docker run image
```

runs:

```text
python -m pipeline --help
```

while:

```bash
docker run image --date 2026-10-01
```

runs:

```text
python -m pipeline --date 2026-10-01
```

## 6.10 `EXPOSE`

```dockerfile
EXPOSE 8080
```

Documents a container port.

It does not itself publish the port.

For a batch pipeline, `EXPOSE` is often unnecessary.

## 6.11 `HEALTHCHECK`

Example:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"
```

A health check can test application health, but it is not automatically appropriate for every batch container.

### Knowledge Check

- [ ] Can you explain `FROM`, `WORKDIR`, `COPY`, and `RUN`?
- [ ] Can you distinguish `ARG` and `ENV`?
- [ ] Can you distinguish `ENTRYPOINT` and `CMD`?
- [ ] Can you explain why `EXPOSE` does not publish a port?
- [ ] Can you explain why a batch job may not need a health check?

---

# 7. Build Context

When you run:

```bash
docker build .
```

the `.` represents the build context.

Docker can access files within that context when processing `COPY` and related build operations.

## 7.1 Why Context Size Matters

Imagine:

```text
project/
├── src/
├── .git/
├── data/              # 20 GB
├── logs/
├── .venv/
├── notebooks/
└── Dockerfile
```

If all of that becomes build context, builds can become slower and risk exposing files that never belonged in the image.

Large contexts affect:

- transfer time
- build performance
- developer feedback time
- CI performance
- accidental data exposure

## 7.2 Dangerous Context Contents

Avoid sending:

```text
.git/
.env
data/
logs/
.venv/
__pycache__/
```

unless a specific build genuinely needs them.

The important point is:

> **Do not use the Docker image as a place to package your development workspace.**

### Data-engineering relevance

Data repositories often contain:

```text
data/
raw/
processed/
logs/
notebooks/
artifacts/
```

These can be enormous.

A pipeline image should normally contain code and runtime dependencies, not local datasets.

---

# 8. `.dockerignore`

A realistic `.dockerignore`:

```dockerignore
.git
.github
.env
.env.*
.venv
__pycache__
*.pyc
data/
logs/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

## 8.1 `.git`

Git history is not required by the runtime application.

It can be large and may contain sensitive historical content.

## 8.2 `.github`

CI definitions normally do not belong inside the application image.

## 8.3 `.env`

Local environment files may contain credentials or environment-specific settings.

Never copy them into production images.

## 8.4 `.env.*`

This catches environment variants such as:

```text
.env.dev
.env.test
.env.production
```

The exact policy should match repository conventions.

## 8.5 `.venv`

A local virtual environment should not be copied into the image.

The image should build its own runtime environment.

## 8.6 Python Caches

These are development artifacts:

```text
__pycache__
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

They are unnecessary for the production runtime.

## 8.7 Data and Logs

Local:

```text
data/
logs/
```

should normally not be image contents.

Data belongs in appropriate storage; logs belong in the runtime's logging system.

## 8.8 What Not to Ignore Accidentally

A careless `.dockerignore` can exclude required source or build metadata.

After adding it, always test:

```bash
docker build -t pipeline:dev .
```

and inspect whether the image actually contains the expected application.

### Mental model

> **`.dockerignore` defines what Docker should not even consider part of the build input.**

---

# 9. Docker Image Layers

Docker images are built from filesystem layers.

A conceptual image:

```text
Application layer
-----------------
Dependency layer
-----------------
Python/runtime layer
-----------------
Base OS layer
```

When a Dockerfile instruction changes, later build work may need to be rebuilt.

## 9.1 Why Layer Structure Matters

Consider:

```dockerfile
COPY . .
RUN uv sync
```

Every source change can invalidate the layer containing dependency installation.

That means changing:

```text
src/pipeline/main.py
```

could cause dependency installation to execute again.

For a large Python environment, this is wasteful.

A better structure is:

```dockerfile
COPY pyproject.toml uv.lock ./
RUN uv sync ...
COPY src ./src
```

Now a source-only change can preserve the dependency layer.

## 9.2 Copy-on-Write Mental Model

At runtime, container filesystems use layered storage mechanisms.

The important engineering idea is:

> **Unchanged image content can be shared; runtime changes occur in the container's writable layer.**

This is another reason not to treat containers as permanent mutable servers.

### Knowledge Check

- [ ] Why are layers useful?
- [ ] Why does instruction order affect build speed?
- [ ] Why should frequently changing source files generally be copied after dependency installation?

---

# 10. Layer Caching

Layer caching is one of the most valuable Docker performance concepts.

## 10.1 Experiment

Start with:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY src ./src

CMD ["python", "-m", "pipeline"]
```

Build:

```bash
docker build -t pipeline:dev .
```

Then modify only:

```text
src/pipeline/main.py
```

Build again:

```bash
docker build -t pipeline:dev .
```

Observe the build output.

The dependency installation should be reusable if its inputs have not changed.

Now modify:

```text
pyproject.toml
```

or:

```text
uv.lock
```

Build again.

The dependency layer must now be reconsidered because its inputs changed.

## 10.2 What Should Be Stable?

A good Dockerfile tries to put stable inputs before frequently changing inputs:

```text
Stable
  ↓
Base image
  ↓
Dependency metadata
  ↓
Dependency installation
  ↓
Application source
  ↓
Frequently changing
```

## 10.3 Measure Instead of Guess

Record:

| Experiment | Build Time | Dependency Layer Rebuilt? | Source Layer Rebuilt? |
|---|---:|---|---|
| Initial build | | | |
| Source-only change | | | |
| Dependency change | | | |

Do not invent values.

Use the actual build output and a timer if necessary.

### Production lesson

> **Good Dockerfiles turn dependency installation into an expensive, infrequent operation rather than an operation repeated on every source change.**

---

# 11. Python Base Images

Common official Python image forms include:

```text
python:<version>
python:<version>-slim
python:<version>-alpine
```

The exact available tags vary with the current Python image ecosystem.

## 11.1 Standard Debian-Based Image

A standard Python image generally provides more OS tooling.

Advantages:

- broader compatibility
- easier troubleshooting
- familiar Debian ecosystem
- fewer surprises for packages expecting common libraries

Trade-off:

- larger image

## 11.2 Slim

A slim Debian-based image removes many packages that are not necessary for typical runtime use.

It is often a practical production default for Python data workloads.

Trade-offs:

- smaller image
- lower attack surface
- fewer preinstalled build/debugging tools
- some packages may require explicit build dependencies

## 11.3 Alpine

Alpine uses a different libc environment from Debian-based distributions.

This can create compatibility or performance considerations for Python packages with native components.

That does not mean Alpine is universally bad.

It means:

> **Choose it deliberately after verifying the workload's dependencies.**

For data engineering workloads using packages such as:

- PyArrow
- NumPy
- pandas
- database libraries
- other native extensions

a Debian-based slim image is often a pragmatic default.

## 11.4 Native Wheels and Build Dependencies

Some Python packages install prebuilt wheels.

Others may require compilation.

That creates a distinction between:

```text
Build environment
```

and:

```text
Runtime environment
```

This becomes important when we introduce multi-stage builds.

### Knowledge Check

- [ ] Can you explain why slim is often a good production starting point?
- [ ] Can you explain why Alpine can create native-library compatibility issues?
- [ ] Can you explain why base-image selection should be driven by workload dependencies?

---

# 12. Using `uv` in Docker

`uv` is used in this roadmap as the Python dependency-management and installation tool.

The key production concept is:

```text
pyproject.toml
    ↓
Dependency declaration

uv.lock
    ↓
Resolved dependency lock
```

## 12.1 Declaration vs Lock

A declaration says approximately:

> “This project needs package X in a compatible version range.”

A lock file records the resolved dependency graph used to reproduce an environment.

For production image construction:

> **Use the lock file.**

## 12.2 Copy `uv` from Its Official Image

A common pattern is:

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```

For stronger reproducibility, production builds should consider pinning the tool image by an appropriate immutable reference rather than depending on a moving `latest` reference.

The exact pin should be selected from the currently approved `uv` release.

## 12.3 Basic `uv` Pattern

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev

COPY src ./src

CMD ["uv", "run", "python", "-m", "pipeline"]
```

A production design should be more deliberate about:

- virtual environment location
- runtime `PATH`
- build dependencies
- cache behavior
- non-root ownership
- final image contents

## 12.4 Dependency Cache

BuildKit can provide cache mounts.

A conceptual pattern:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev
```

This can improve rebuild performance without making the cache itself part of the final image.

## 12.5 Bytecode

Where appropriate, compiled Python bytecode can reduce startup work.

For example, `uv` supports bytecode compilation options in its workflow. The exact option should be used according to the current `uv` version and project layout.

Do not add options without understanding their effect.

## 12.6 Production Rule

A production image should not casually do:

```text
install whatever happens to be latest
```

Instead:

```text
locked dependency graph
+
known base image
+
known application revision
=
identifiable artifact
```

---

# 13. Progressive Dockerfile Optimization

The most useful way to learn production image engineering is to evolve a naive image.

## Version 1 — Basic Python Image

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install .

CMD ["python", "-m", "pipeline"]
```

### Problems

- entire build context is copied
- dependencies may be poorly cached
- local files can enter the image
- no explicit non-root user
- no clear reproducibility strategy
- no security workflow
- no multi-stage separation

## Version 2 — Add `.dockerignore`

Create:

```dockerignore
.git
.env
.env.*
.venv
__pycache__
*.pyc
data/
logs/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

### Improvement

The build receives a smaller and safer context.

## Version 3 — Improve Dependency Caching

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN ...

COPY src ./src

CMD ["python", "-m", "pipeline"]
```

### Improvement

Source changes do not necessarily invalidate dependency installation.

## Version 4 — Use `uv`

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev

COPY src ./src

CMD ["uv", "run", "python", "-m", "pipeline"]
```

### Improvement

Dependency installation is lock-aware and aligned with the project toolchain.

## Version 5 — Multi-Stage

Separate build requirements from runtime requirements.

```text
Builder
  ↓
build dependencies
  ↓
runtime artifacts
  ↓
Runtime
```

### Improvement

The runtime image can exclude compilers and development tooling.

## Version 6 — Non-Root

Create an application user and run:

```dockerfile
USER app
```

### Improvement

Reduced privileges.

## Version 7 — Correct Entry Point

Prefer:

```dockerfile
ENTRYPOINT ["python", "-m", "pipeline"]
```

over a shell wrapper when the application itself is the main process.

### Improvement

Better signal propagation and clearer process ownership.

## Version 8 — Reproducibility

Use:

- locked dependencies
- controlled base-image references
- immutable application tags
- recorded image digest

## Version 9 — Security

Add a process such as:

```text
build
→ scan
→ review
→ generate SBOM
→ remediate
→ rescan
```

## Version 10 — Multi-Platform

Use:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  ...
```

### The progression

```text
Works
 ↓
Controlled
 ↓
Fast
 ↓
Reproducible
 ↓
Least privilege
 ↓
Secure
 ↓
Portable
```

### Knowledge Check

For each version, answer:

- [ ] What problem did it solve?
- [ ] What did it make better?
- [ ] What new complexity did it introduce?
- [ ] Is that complexity justified for this workload?

---

# 14. Multi-Stage Builds

A multi-stage Dockerfile can separate build and runtime environments.

Conceptually:

```text
Builder stage
├── compiler
├── headers
├── build tools
├── source
└── dependency build process
        ↓
Runtime stage
├── Python
├── runtime libraries
├── application
└── runtime dependencies
```

## 14.1 Why This Matters

Build environments may need:

- compilers
- development headers
- package-manager tooling
- test dependencies

The runtime may need none of them.

Shipping build tools increases:

- image size
- attack surface
- maintenance burden

## 14.2 Generic Pattern

```dockerfile
FROM python:3.12-slim AS builder

WORKDIR /build

# Install only build-time requirements here.
# Build the application/runtime artifacts.

FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy only the artifacts needed at runtime.
COPY --from=builder /build/... /app/...

CMD ["python", "-m", "pipeline"]
```

The exact artifact-transfer strategy depends on the dependency model.

## 14.3 What Should Stay Out of Runtime?

Where not required:

```text
compilers
development headers
test tools
source-control metadata
dependency caches
local notebooks
development-only packages
```

### Data-engineering relevance

This becomes especially valuable when native Python packages require build dependencies but the resulting runtime only needs compiled artifacts.

### Trade-off

Multi-stage builds add Dockerfile complexity.

Use them when the reduction in runtime image size and attack surface justifies the complexity.

---

# 15. Non-Root Containers

A container process does not need to run as root merely because it is inside a container.

A production image can create an application user.

For example:

```dockerfile
RUN groupadd --system app && \
    useradd --system --gid app --create-home app
```

Then:

```dockerfile
USER app
```

The exact user-management commands depend on the base distribution.

## 15.1 Why Root Is Risky

If a compromised process has unnecessary privileges, the potential impact increases.

Least privilege means:

> Give the application only the permissions it actually needs.

## 15.2 Ownership Problems

A common failure is:

```text
files owned by root
        ↓
switch to app user
        ↓
application cannot write
```

Solutions may include:

```dockerfile
COPY --chown=app:app src ./src
```

or explicitly preparing writable directories.

Do not simply solve every permission problem by returning to root.

## 15.3 Runtime Filesystem

Ask:

- Which directories must be writable?
- Which files are read-only?
- Does the application write temporary files?
- Does it write checkpoints?
- Is persistent state actually supposed to be inside the container?

For many data jobs, durable state belongs in external storage rather than the image filesystem.

### Knowledge Check

- [ ] Can you explain least privilege?
- [ ] Can you identify why a non-root process may get permission errors?
- [ ] Can you explain how `COPY --chown` can help?

---

# 16. Configuration with `ARG` and `ENV`

Container images should be reusable across environments.

The image should not hard-code:

```text
production bucket
production database
production credentials
```

Instead, runtime configuration should be supplied externally.

## 16.1 Configuration vs Secrets

Configuration may include:

```text
LOG_LEVEL=INFO
AWS_REGION=...
PIPELINE_MODE=...
```

Secrets include:

```text
passwords
API tokens
private keys
database credentials
```

Secrets require stronger handling.

## 16.2 `ARG`

```dockerfile
ARG APP_VERSION=dev
```

`ARG` exists primarily during image construction.

It can be used to parameterize builds.

Do not treat it as a secure secret channel.

## 16.3 `ENV`

```dockerfile
ENV PYTHONUNBUFFERED=1
```

`ENV` establishes environment variables for image/container execution.

Runtime values can also be supplied when launching the container.

## 16.4 What Not to Do

Never do:

```dockerfile
ENV DATABASE_PASSWORD=...
```

Do not:

```dockerfile
COPY .env .
```

Do not hard-code credentials into application source.

Even if a secret is deleted in a later Dockerfile instruction, earlier layers may retain it.

### Mental model

> **Build an environment-neutral artifact; inject environment-specific configuration at runtime.**

---

# 17. ENTRYPOINT and CMD

These instructions define container startup behavior.

## 17.1 Exec Form

Preferred:

```dockerfile
ENTRYPOINT ["python", "-m", "pipeline"]
```

This directly launches the process.

## 17.2 Shell Form

For example:

```dockerfile
ENTRYPOINT python -m pipeline
```

The shell can become the process in the container, changing signal and process behavior.

For production applications, exec form is generally preferable when the application should directly own the container process.

## 17.3 `ENTRYPOINT` + `CMD`

A useful design:

```dockerfile
ENTRYPOINT ["python", "-m", "pipeline"]
CMD ["--help"]
```

Default:

```bash
docker run pipeline
```

runs:

```text
python -m pipeline --help
```

Override:

```bash
docker run pipeline --date 2026-10-01
```

runs:

```text
python -m pipeline --date 2026-10-01
```

This is useful for data jobs where the executable is stable but arguments vary.

### Knowledge Check

- [ ] What is the purpose of `ENTRYPOINT`?
- [ ] What is the purpose of `CMD`?
- [ ] Why is exec form important?

---

# 18. PID 1 and Signal Handling

This is one of the most important production concepts in containerized workloads.

## 18.1 PID 1

Inside a container, the primary process generally becomes PID 1.

Conceptually:

```text
Container
└── PID 1
    └── Python application
```

PID 1 has special process-management responsibilities.

## 18.2 Why Signals Matter

A scheduler or orchestrator may request graceful termination.

A common sequence is:

```text
SIGTERM
   ↓
Application stops accepting new work
   ↓
Finish or checkpoint safe work
   ↓
Close resources
   ↓
Exit
```

If graceful termination is not handled correctly, a process can be forcibly killed.

## 18.3 SIGTERM vs SIGKILL

Conceptually:

```text
SIGTERM
→ request graceful termination

SIGKILL
→ force termination; process cannot handle it
```

A production workload should use the grace period to shut down cleanly.

## 18.4 Data Pipeline Example

Imagine a batch job processing files:

```text
Read file A
Read file B
Read file C
```

A termination request arrives.

A robust application can:

1. stop starting new work
2. finish a safe unit of work
3. persist checkpoint/state if appropriate
4. close database/object-storage resources
5. exit

The exact checkpoint behavior depends on the pipeline.

## 18.5 Python Signal Handling

A simplified pattern:

```python
import signal
import time

shutdown_requested = False


def handle_sigterm(signum, frame):
    global shutdown_requested
    shutdown_requested = True


signal.signal(signal.SIGTERM, handle_sigterm)

while not shutdown_requested:
    process_one_unit()
    time.sleep(0.1)

cleanup()
```

Real applications should make shutdown behavior explicit and safe rather than blindly interrupting arbitrary operations.

## 18.6 Shell Wrappers

A shell wrapper can interfere with signal delivery.

If a wrapper is unavoidable, it should normally use `exec`:

```bash
#!/bin/sh
exec python -m pipeline "$@"
```

`exec` replaces the shell with the application process.

## 18.7 Init Processes

An init process can help with:

- signal handling
- child-process reaping

Docker can provide an init process with:

```bash
docker run --init ...
```

or an image/runtime can use a suitable init such as `tini`.

Do not add an init process automatically without understanding why it is needed.

### Production mental model

> **The process that Docker launches should be a well-behaved process that understands termination and does not leave child processes unmanaged.**

---

# 19. HEALTHCHECK

A health check asks a question about application health.

That is different from:

```text
Is a process running?
```

For a service, an appropriate check might test an endpoint.

For a batch job, the process exiting successfully may already be the meaningful success signal.

## 19.1 When Health Checks Help

Useful for:

- long-running services
- components with meaningful health endpoints
- local development feedback

## 19.2 What Health Checks Cannot Prove

A successful health check does not prove:

- the pipeline's data is correct
- upstream data is complete
- downstream systems are healthy
- business logic is correct

Do not blindly add:

```dockerfile
HEALTHCHECK ...
```

to every batch image.

### Mental model

> **Health checks test a defined health condition; they do not certify application correctness.**

---

# 20. Reproducible Images

Reproducibility means being able to understand and reliably reconstruct the intended artifact from controlled inputs.

The major inputs are:

```text
Source revision
+
Dependency lock
+
Base image
+
Build instructions
+
Build configuration
=
Image
```

## 20.1 Locked Dependencies

Use:

```text
uv.lock
```

rather than allowing a production build to resolve an uncontrolled dependency graph.

## 20.2 Base Image Pinning

A reference such as:

```dockerfile
FROM python:3.12-slim
```

is convenient but can move as the upstream image is updated.

For stronger reproducibility, production systems can pin an exact immutable image reference, including a digest.

Example form:

```dockerfile
FROM python:3.12-slim@sha256:<digest>
```

The real digest must come from the trusted image source.

## 20.3 Mutable Tags

Avoid relying on:

```text
latest
```

as the production identity.

A Git SHA tag is better:

```text
pipeline:git-abc123
```

A digest is stronger:

```text
pipeline@sha256:...
```

## 20.4 Why This Helps Debugging

Suppose production is broken.

If you know:

```text
Git SHA
+
image digest
+
dependency lock
```

you can identify the artifact precisely.

Without that information, debugging becomes guesswork.

## 20.5 Reproducibility Is Not Always Bit-for-Bit Identity

Different build environments can still introduce variation.

The engineering goal is to control the important inputs and produce a predictable, traceable artifact.

### Knowledge Check

- [ ] Can you distinguish tag and digest?
- [ ] Can you explain why `uv.lock` matters?
- [ ] Can you explain how base-image updates can affect reproducibility?
- [ ] Can you explain why artifact identity matters for rollback?

---

# 21. Image Security

A production image should be treated as a software supply-chain artifact.

Security concerns include:

- OS vulnerabilities
- Python dependency vulnerabilities
- unnecessary packages
- root execution
- leaked secrets
- untrusted base images
- unreviewed dependencies
- unknown contents

## 21.1 Minimal Images

Remove what the runtime does not need.

This can reduce:

- size
- attack surface
- patching burden

## 21.2 Non-Root

Use least privilege.

## 21.3 Scanning

A tool such as Trivy can scan an image:

```bash
trivy image pipeline:dev
```

Do not invent scanner output.

Interpret the results based on the actual scan.

Typical categories may include:

```text
OS package vulnerability
Python dependency vulnerability
Severity
Affected package
Installed version
Fixed version, if available
```

## 21.4 Remediation Workflow

```text
Build
  ↓
Scan
  ↓
Review findings
  ↓
Determine exploitability/relevance
  ↓
Upgrade or rebuild
  ↓
Rescan
  ↓
Record result
```

Do not automatically upgrade everything without testing.

A security fix can introduce compatibility changes.

## 21.5 Supply Chain

Know:

- where the base image comes from
- what dependencies are installed
- what source revision produced the image
- what image digest was deployed
- what security checks ran

---

# 22. SBOMs and Vulnerability Scanning

SBOM means:

> **Software Bill of Materials**

It is an inventory of software components present in an artifact.

Conceptually:

```text
Image
 ↓
SBOM
 ↓
Components
 ├── Python
 ├── OS packages
 ├── Python packages
 └── other included components
```

## 22.1 Why SBOMs Matter

If a vulnerability is announced in a package, the organization needs to answer:

> “Which deployed images contain this package?”

Without component visibility, that can become a slow manual investigation.

## 22.2 Workflow

```text
Build image
   ↓
Generate SBOM
   ↓
Scan dependencies
   ↓
Identify vulnerabilities
   ↓
Fix
   ↓
Rebuild
   ↓
Rescan
```

A tool such as Trivy may support SBOM generation depending on the installed version and workflow.

Example:

```bash
trivy image --format cyclonedx --output sbom.json pipeline:dev
```

Verify the command against the installed tool version before adopting it in production.

## 22.3 Audit Use

An SBOM can support:

- incident response
- vulnerability response
- compliance
- dependency inventory
- release review

### Knowledge Check

- [ ] Can you define an SBOM?
- [ ] Can you explain why an SBOM helps incident response?
- [ ] Can you explain why scanning should be followed by remediation and rescanning?

---

# 23. Build Secrets

A fundamental rule:

> **No secrets in image layers.**

Never do:

```dockerfile
ENV TOKEN=secret
```

or:

```dockerfile
COPY .env .
```

## 23.1 Why Deleting Later Is Not Enough

Imagine:

```dockerfile
COPY .env .
RUN rm .env
```

The final filesystem may no longer contain `.env`, but the earlier layer can still contain it.

Therefore, the secret may remain recoverable from image history/layers.

## 23.2 BuildKit Secret Mounts

BuildKit supports temporary secret mounts.

Conceptually:

```dockerfile
RUN --mount=type=secret,id=pypi_token \
    ...
```

The secret is made available during the build step without intentionally becoming part of the resulting image layer.

The exact command used to supply the secret depends on the build workflow.

Example pattern:

```bash
docker buildx build \
  --secret id=pypi_token,src="$HOME/.config/pypi/token" \
  -t pipeline:dev .
```

The Dockerfile can consume it during the required build step.

## 23.3 Private Package Index Example

The important design is:

```text
credential
   ↓
temporary BuildKit secret
   ↓
dependency installation
   ↓
final image
```

not:

```text
credential
   ↓
ENV
   ↓
image layer
```

Keep the credential out of:

- Dockerfile
- source code
- image layers
- logs
- Git history

### Important boundary

This section teaches safe secret handling during image construction.

The complete architecture for cloud secrets managers belongs in the later secrets-management topic.

---

# 24. Multi-Platform Builds with `buildx`

Modern development environments may use different CPU architectures.

Common architectures:

```text
linux/amd64
linux/arm64
```

Examples:

- x86 cloud instances → commonly amd64
- ARM laptops → commonly arm64
- ARM cloud instances → arm64

## 24.1 Why This Matters

A Python image that works on one architecture may fail on another because of:

- native Python extensions
- architecture-specific binaries
- package availability
- JVM/native dependencies
- compiled system libraries

## 24.2 Buildx

Example:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t company/pipeline:git-abc123 \
  .
```

When pushing:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t company/pipeline:git-abc123 \
  --push \
  .
```

A registry can expose a multi-platform manifest so clients retrieve the appropriate architecture image.

## 24.3 Verify

Use Docker inspection tooling to verify the published image supports the expected platforms.

For example:

```bash
docker buildx imagetools inspect company/pipeline:git-abc123
```

The exact output depends on the registry and image.

## 24.4 Architecture-Aware Dependencies

Before promising multi-platform support, test:

```text
dependency installation
application startup
pipeline execution
native libraries
```

Do not assume that a pure Python package and a package with native components have the same portability characteristics.

### Knowledge Check

- [ ] Can you explain amd64 vs arm64?
- [ ] Can you explain why native dependencies create portability problems?
- [ ] Can you explain what `buildx` contributes?

---

# 25. Python Data-Engineering Images

Now combine the concepts into a realistic Python pipeline image.

Repository:

```text
pipeline/
├── pyproject.toml
├── uv.lock
├── src/
│   └── pipeline/
│       ├── __init__.py
│       └── main.py
├── Dockerfile
└── .dockerignore
```

## 25.1 Example Application

`src/pipeline/main.py`:

```python
from __future__ import annotations

import argparse
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run(run_date: str) -> None:
    logger.info("Starting pipeline for %s", run_date)
    # Real pipeline work would:
    # 1. read from an API/database/object store
    # 2. validate/transform data
    # 3. write Parquet or another target
    logger.info("Pipeline completed for %s", run_date)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    run(args.date)


if __name__ == "__main__":
    main()
```

## 25.2 Runtime Configuration

Run:

```bash
docker run --rm pipeline:dev --date 2026-10-01
```

The image remains reusable across dates and environments.

The application does not need to bake:

```text
production date
production bucket
production database
```

into the image.

## 25.3 Production-Oriented Structure

A strong design aims for:

```text
locked dependencies
+
efficient cache
+
minimal runtime
+
non-root
+
exec-form entrypoint
+
external configuration
+
known artifact identity
```

---

# 26. dbt Images

dbt benefits from containerization because its runtime contains:

```text
dbt executable
+
adapter package
+
Python dependencies
+
project code
+
configuration interface
```

## 26.1 Why Containerize dbt?

A dbt image can provide:

- dependency reproducibility
- consistent adapter versions
- consistent runtime
- CI compatibility
- isolated execution

## 26.2 Adapter Packages

A dbt project may require a warehouse-specific adapter.

The image should lock its dependency graph.

For example, conceptually:

```text
dbt
+
warehouse adapter
+
project dependencies
```

The exact adapter depends on the warehouse.

## 26.3 Runtime Configuration

Do not bake credentials into the image.

The image should contain:

```text
dbt executable
project
dependency environment
```

while runtime execution supplies appropriate configuration and secret references.

## 26.4 Non-Root Execution

The dbt process should not require root simply because it runs in a container.

## 26.5 CI Usage

The same dbt runtime image can help ensure that development and CI execute the same dependency environment.

Do not turn this section into the complete dbt CI design; that belongs to the later CI topic.

### Mental model

> **The dbt image is the reproducible runtime; environment-specific warehouse access is supplied at execution time.**

---

# 27. PySpark Images

A PySpark image differs from an ordinary Python pipeline image because Spark has a JVM-based runtime.

Conceptually:

```text
Python
  +
PySpark
  +
JVM
  +
Java runtime
  +
Spark
  +
application code
```

## 27.1 Why This Is Different

A typical Python pipeline may require:

```text
Python
Python packages
```

A Spark workload additionally involves:

```text
Spark runtime
JVM
Java
```

This creates additional compatibility considerations.

## 27.2 Application Components

A Spark image may contain:

```text
Spark runtime
Python dependencies
application code
configuration interface
```

The exact packaging approach depends on how Spark will run.

## 27.3 Later Execution Targets

The same image concept can later be used by:

- Kubernetes
- managed Spark platforms
- orchestrators

The image therefore becomes a deployment artifact.

## 27.4 Image Construction Focus

This module is about constructing the image, not fully teaching:

- Spark cluster architecture
- Kubernetes Spark operators
- managed Spark platform administration

Those belong elsewhere in the roadmap.

### Mental model

> **A PySpark image packages the application runtime; the execution platform later supplies the Spark execution environment and resources.**

---

# 28. Images for Orchestrated Tasks

An orchestrator can launch an isolated workload from a container image.

Conceptually:

```text
Airflow
   ↓
Container image
   ↓
Pipeline task
```

The benefit is dependency isolation.

Suppose Task A needs:

```text
pandas 2.x
```

and Task B needs a different dependency set.

Containerized task execution can isolate those environments.

## 28.1 Reproducibility

The orchestrator does not need to rely on a mutable worker environment containing every package.

Instead:

```text
task definition
+
image digest
=
known runtime
```

## 28.2 Deployment Consistency

The same image can be tested before being used for a production task.

## 28.3 Dependency Isolation

This reduces “package conflict” problems between unrelated tasks.

### Important boundary

This module explains why images are useful for orchestrated tasks.

It does not re-teach Airflow.

---

# 29. Production Docker Image Design

## Production Docker Image Checklist

### Build

- [ ] Reproducible inputs
- [ ] Efficient caching
- [ ] Minimal build context
- [ ] `.dockerignore`
- [ ] Multi-stage build where appropriate

### Dependencies

- [ ] Locked dependencies
- [ ] Minimal runtime dependencies
- [ ] No unnecessary development packages
- [ ] Known base-image strategy

### Security

- [ ] Non-root
- [ ] No secrets in image
- [ ] Vulnerability scan
- [ ] SBOM
- [ ] Minimal attack surface

### Runtime

- [ ] Correct entrypoint
- [ ] Exec form where appropriate
- [ ] Graceful signal handling
- [ ] Externalized configuration
- [ ] Appropriate health check, if useful

### Release

- [ ] Immutable release tag
- [ ] Git SHA
- [ ] Image digest recorded
- [ ] Registry location known

### Portability

- [ ] amd64 support where required
- [ ] arm64 support where required
- [ ] Native dependencies tested across architectures

## Production Engineering Principles

### Reproducibility

The same controlled source and dependency inputs should produce a predictable artifact.

### Immutability

Production should run an identifiable artifact rather than a moving target.

### Least Privilege

Containers should not require unnecessary privileges.

### Minimal Attack Surface

Do not ship tools and packages that the runtime does not need.

### Secure Supply Chain

Know what is inside the image.

### Externalized Configuration

Environment-specific settings belong outside the immutable application artifact.

### No Secrets in Images

An image can be copied to many systems. Treat it as broadly distributable.

### Graceful Lifecycle Management

The application must respond correctly to termination.

### Measurability

Optimize image size and build time using measurements, not assumptions.

---

# 30. Debugging and Failure Scenarios

## Scenario 1 — Docker Build Is Unexpectedly Slow

### Symptoms

A tiny source change causes a long build.

### Diagnose

Check:

1. Build context size.
2. `.dockerignore`.
3. Dockerfile instruction ordering.
4. Whether dependency installation occurs before source copy.
5. Whether the dependency cache is being invalidated.

A useful structure is:

```dockerfile
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY src ./src
```

### Mental model

> Stable inputs should precede frequently changing inputs.

---

## Scenario 2 — Every Code Change Reinstalls Dependencies

### Likely cause

```dockerfile
COPY . .
RUN uv sync ...
```

### Better design

```dockerfile
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY src ./src
```

The dependency installation now depends on dependency metadata rather than every application source file.

---

## Scenario 3 — Container Exits Immediately

### Diagnose

Check:

```bash
docker ps -a
docker logs <container>
```

Then inspect:

- `ENTRYPOINT`
- `CMD`
- application arguments
- process lifecycle
- exit code

A container is expected to stop when its main process exits.

A stopped container is not necessarily a Docker failure.

For a batch pipeline:

```text
successful completion
→ process exits
→ container stops
```

That can be correct behavior.

---

## Scenario 4 — SIGTERM Does Not Reach Python Correctly

### Possible causes

- shell-form entrypoint
- wrapper process does not `exec`
- PID 1 behavior
- child process handling

Prefer:

```dockerfile
ENTRYPOINT ["python", "-m", "pipeline"]
```

If a shell wrapper is needed:

```bash
#!/bin/sh
exec python -m pipeline "$@"
```

---

## Scenario 5 — Permission Errors After Switching to Non-Root

### Symptoms

```text
Permission denied
```

### Diagnose

Inspect ownership and writable paths.

Common cause:

```text
COPY files as root
↓
USER app
↓
application cannot write
```

Possible solution:

```dockerfile
COPY --chown=app:app src ./src
```

and explicitly prepare required writable directories.

Do not make the entire filesystem writable.

---

## Scenario 6 — Image Contains a Secret

### How It Happened

Potential patterns:

```dockerfile
ENV TOKEN=...
```

or:

```dockerfile
COPY .env .
```

or:

```dockerfile
RUN echo "$TOKEN" > credentials.txt
```

### Why Deleting Is Insufficient

Earlier image layers may retain the secret.

### Response

1. Treat the secret as compromised.
2. Revoke/rotate it.
3. Remove the secret from the build process.
4. Rebuild the image safely.
5. Scan image/history as appropriate.
6. Remove exposed artifacts according to organizational policy.
7. Investigate where the secret was distributed.

The key principle is:

> **Rotate first; cleanup alone is not a credential response.**

---

## Scenario 7 — Works on ARM but Fails on amd64

### Diagnose

Check:

- platform-specific wheels
- native binaries
- base image architecture
- Java/Spark binaries
- compiled extensions

Build explicitly:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  ...
```

Then test both platforms.

Do not assume a successful image build means the application behaves identically on both architectures.

---

## Scenario 8 — Vulnerability Scan Reports Findings

### Workflow

```text
Scan
 ↓
Classify finding
 ↓
Identify affected component
 ↓
Determine available fix
 ↓
Upgrade/rebuild
 ↓
Run tests
 ↓
Rescan
```

Avoid blindly suppressing findings.

Also avoid blindly upgrading dependencies without testing.

The correct remediation depends on:

- severity
- exploitability
- runtime exposure
- fixed version
- compatibility
- compensating controls

---

# 31. Progressive Hands-On Lab

Create:

```text
docker/
├── pipeline.Dockerfile
├── dbt.Dockerfile
├── spark.Dockerfile
└── .dockerignore
```

The lab is intentionally progressive.

## Stage 1 — Naive Dockerfile

Create a minimal Python image.

Build:

```bash
docker build -f docker/pipeline.Dockerfile -t pipeline:naive .
```

Run:

```bash
docker run --rm pipeline:naive
```

Observe:

- build output
- image size
- startup behavior
- application output

Record the results.

---

## Stage 2 — Inspect the Container

Run without `--rm`:

```bash
docker run --name pipeline-lab pipeline:naive
```

Then:

```bash
docker ps -a
docker logs pipeline-lab
```

Remove it:

```bash
docker rm pipeline-lab
```

---

## Stage 3 — Add `.dockerignore`

Create:

```dockerignore
.git
.github
.env
.env.*
.venv
__pycache__
*.pyc
data/
logs/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

Rebuild.

Observe whether build context and build behavior change.

---

## Stage 4 — Optimize Layer Caching

Structure:

```dockerfile
COPY pyproject.toml uv.lock ./
RUN ...
COPY src ./src
```

Build once.

Change only application source.

Build again.

Record:

```text
build time
dependency layer reused?
```

Then change a dependency declaration or lock file.

Build again.

Compare.

---

## Stage 5 — Add `uv`

Use an appropriate `uv` image/tool reference and install from:

```text
uv.lock
```

Use:

```text
--locked
```

and exclude development dependencies for the runtime environment where appropriate.

---

## Stage 6 — Add Multi-Stage Build

Create:

```text
builder
runtime
```

Keep build-only dependencies in the builder.

Measure image size before and after.

---

## Stage 7 — Add Non-Root User

Run:

```dockerfile
USER app
```

Test the application.

If it fails:

1. identify the file/directory
2. inspect ownership
3. determine whether it actually needs to be writable
4. fix ownership narrowly

---

## Stage 8 — Test Signal Handling

Create a workload that stays alive long enough to receive a termination request.

Run it.

Then:

```bash
docker stop <container>
```

Observe whether the application receives termination and exits cleanly.

---

## Stage 9 — Reproducible Tags

Build using a Git-style identifier:

```text
pipeline:git-<commit-sha>
```

Record the resulting digest.

Do not use a moving `latest` reference as the only release identifier.

---

## Stage 10 — Vulnerability Scan

Run:

```bash
trivy image pipeline:...
```

Record actual findings.

Do not invent results.

---

## Stage 11 — SBOM

Generate an SBOM using the approved scanner/tooling.

For example, where supported:

```bash
trivy image --format cyclonedx --output sbom.json pipeline:...
```

Inspect the generated file.

---

## Stage 12 — Build Secrets

Create a controlled test using a non-production credential.

Use BuildKit secret mounting.

Verify that the credential is not intentionally present in the resulting runtime image.

Never use a real production secret for this exercise.

---

## Stage 13 — Multi-Platform Build

Build:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t pipeline:multiarch \
  .
```

If publishing:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <registry>/<repository>:<tag> \
  --push \
  .
```

Verify the manifest.

---

# 32. Measurement and Optimization

The roadmap requires measurement.

Record actual values.

| Version | Image Size | Build Time | Cache Reuse | Vulnerabilities |
|---|---:|---:|---|---:|
| Naive | | | | |
| Optimized | | | | |

Also record:

| Measurement | Result |
|---|---:|
| Initial image size | |
| Optimized image size | |
| Initial build time | |
| Optimized build time | |
| Dependency rebuild time | |
| Code-only rebuild time | |
| Vulnerabilities before remediation | |
| Vulnerabilities after remediation | |

## 32.1 Measuring Image Size

Use Docker's image listing:

```bash
docker images
```

Record the relevant image.

## 32.2 Measuring Build Time

Use the terminal's timing facilities or CI build duration.

Do not estimate.

## 32.3 Measuring Cache Reuse

Read the Docker build output and identify which steps were reused.

## 32.4 Measuring Security Improvements

Run the scanner before and after remediation.

Do not claim:

```text
zero vulnerabilities
```

unless the actual scan supports that result.

## 32.5 Optimization Rule

The engineering loop is:

```text
Measure
  ↓
Change
  ↓
Measure again
  ↓
Compare
```

Not:

```text
Assume
  ↓
Optimize
  ↓
Declare victory
```

---

# 33. Production Scenario

## Situation

A Python ingestion pipeline works on an engineer's laptop but fails in CI because dependency environments differ.

The team decides to containerize it.

## Desired Flow

```text
Developer
   ↓
Dockerfile
   ↓
Build
   ↓
Image
   ↓
Registry
   ↓
CI
   ↓
Production
```

## Failure 1 — Dependency Mismatch

### Symptom

CI and local environments use different dependency versions.

### Fix

Use:

```text
pyproject.toml
+
uv.lock
+
controlled image
```

---

## Failure 2 — Slow Builds

### Symptom

Every source change reinstalls all dependencies.

### Fix

Order:

```dockerfile
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY src ./src
```

---

## Failure 3 — Vulnerability

### Symptom

Scanner reports an affected OS or Python package.

### Fix

Determine:

- affected component
- severity
- available fixed version
- compatibility impact

Then upgrade/rebuild/test/rescan.

---

## Failure 4 — Secret Leakage

### Symptom

A token was copied into the image.

### Fix

1. Rotate/revoke the token.
2. Remove it from the build.
3. Rebuild.
4. Verify the new image.
5. Investigate exposure.

---

## Failure 5 — SIGTERM Problem

### Symptom

The pipeline does not shut down cleanly.

### Diagnose

Inspect:

- shell wrapper
- PID 1
- exec-form entrypoint
- signal handling

---

## Failure 6 — Architecture Mismatch

### Symptom

ARM development works; amd64 deployment fails.

### Diagnose

Check:

- native dependencies
- platform-specific wheels
- base image support
- compiled binaries

Then explicitly build/test required platforms.

---

# 34. Conceptual Exercises

## Exercise 1 — Image vs Container

Explain the difference.

### Solution

An image is the packaged artifact. A container is a runtime instance created from that image.

---

## Exercise 2 — Image Layers

Why does Docker use layers?

### Solution

Layers allow reusable filesystem/build components and improve storage and build efficiency when inputs remain unchanged.

---

## Exercise 3 — Build Context

Why can a huge build context be a problem?

### Solution

It can slow builds and may expose unnecessary data or sensitive files to the build process.

---

## Exercise 4 — `.dockerignore`

Why exclude `.git` and `.env`?

### Solution

They are normally unnecessary at runtime, can increase context size, and `.env` may contain sensitive configuration.

---

## Exercise 5 — Cache Invalidation

Why is this inefficient?

```dockerfile
COPY . .
RUN uv sync ...
```

### Solution

Any change to the copied source can invalidate the dependency installation step.

---

## Exercise 6 — `ARG` vs `ENV`

What is the basic distinction?

### Solution

`ARG` is primarily a build-time parameter. `ENV` defines environment configuration available during image construction and/or container runtime depending on how it is used.

Neither should be treated as a secure secret store.

---

## Exercise 7 — `ENTRYPOINT` vs `CMD`

Why use both?

### Solution

`ENTRYPOINT` can define the stable executable while `CMD` supplies default arguments that can be overridden at runtime.

---

## Exercise 8 — PID 1

Why does PID 1 matter?

### Solution

The primary container process has special process-management and signal-handling responsibilities. Incorrect process structure can prevent graceful shutdown and child-process reaping.

---

## Exercise 9 — Non-Root

Why run as non-root?

### Solution

Least privilege reduces the impact of a compromised process and avoids granting unnecessary permissions.

---

## Exercise 10 — Digest vs Tag

Which is more exact?

### Solution

A digest identifies specific image content. A tag is a human-readable reference that can be moved to different content.

---

## Exercise 11 — Multi-Stage

Why use a builder stage?

### Solution

To keep build-only tools and dependencies out of the runtime image.

---

## Exercise 12 — SBOM

Why generate an SBOM?

### Solution

It provides component visibility for vulnerability response, auditing, and software inventory.

---

## Exercise 13 — Build Secrets

Why is `COPY .env .` unsafe?

### Solution

The credential can become part of image layers and can remain recoverable even if the file is deleted later.

---

## Exercise 14 — Multi-Platform

Why can an image work on ARM but fail on amd64?

### Solution

Native dependencies and binaries may be architecture-specific.

---

# 35. Coding Exercises

## Exercise 1 — Basic Python Dockerfile

Write a Dockerfile for:

```text
src/pipeline/main.py
pyproject.toml
uv.lock
```

Requirements:

- Python base image
- working directory
- dependency metadata
- source
- startup command

### Solution

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
# Install dependencies according to the project setup.

COPY src ./src

CMD ["python", "-m", "pipeline"]
```

---

## Exercise 2 — Optimize Layer Caching

Change:

```dockerfile
COPY . .
RUN ...
```

into a structure that isolates dependency inputs.

### Solution

```dockerfile
COPY pyproject.toml uv.lock ./
RUN ...

COPY src ./src
```

---

## Exercise 3 — Add `uv`

Use the official `uv` image/tooling pattern and install from the lock file.

### Solution pattern

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev
```

For production, use a controlled immutable tool/base reference where required by the organization's reproducibility policy.

---

## Exercise 4 — Multi-Stage Build

Create:

```text
builder
runtime
```

and copy only runtime artifacts.

### Expected reasoning

The builder contains build tools; the runtime contains only what is needed for execution.

---

## Exercise 5 — Non-Root

Add an application user.

### Solution pattern

```dockerfile
RUN groupadd --system app && \
    useradd --system --gid app --create-home app

USER app
```

Use the appropriate commands for the selected base image.

---

## Exercise 6 — Signal Handling

Create an application that handles SIGTERM and exits gracefully.

### Solution pattern

```python
import signal

shutdown = False


def handle_sigterm(signum, frame):
    global shutdown
    shutdown = True


signal.signal(signal.SIGTERM, handle_sigterm)
```

The actual application loop must periodically reach a safe shutdown point.

---

## Exercise 7 — Reproducible Tagging

Build using a Git SHA.

Example:

```bash
docker build -t company/pipeline:git-abc123 .
```

Then record the resulting digest.

---

## Exercise 8 — Multi-Platform Build

Build:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t company/pipeline:multiarch \
  .
```

If publishing, use `--push`.

---

## Exercise 9 — Generate an SBOM

Use the installed approved tooling.

For Trivy where supported:

```bash
trivy image --format cyclonedx --output sbom.json company/pipeline:git-abc123
```

Inspect the generated SBOM.

---

## Exercise 10 — Scan and Remediate

Run:

```bash
trivy image company/pipeline:git-abc123
```

For every actionable finding:

1. identify the component
2. identify the fixed version if available
3. update the dependency/base image
4. rebuild
5. test
6. rescan

Do not invent scan results.

---

# 36. Knowledge Checkpoints

## After Fundamentals

You should be able to:

- [ ] Explain why containers improve reproducibility.
- [ ] Explain containers vs VMs.
- [ ] Explain image vs container.
- [ ] Explain layers and registries.

## After Dockerfile Basics

- [ ] Write a basic Dockerfile.
- [ ] Explain each required Dockerfile instruction.
- [ ] Build and run the image.
- [ ] Read container logs.

## After Build Optimization

- [ ] Explain build context.
- [ ] Write `.dockerignore`.
- [ ] Explain layer caching.
- [ ] Optimize dependency installation.

## After Runtime Engineering

- [ ] Use `uv`.
- [ ] Build multi-stage images.
- [ ] Run as non-root.
- [ ] Configure with `ARG`/`ENV`.
- [ ] Use `ENTRYPOINT` and `CMD` correctly.
- [ ] Explain PID 1 and SIGTERM.

## After Security

- [ ] Explain image reproducibility.
- [ ] Distinguish tags and digests.
- [ ] Scan images.
- [ ] Generate an SBOM.
- [ ] Use build secrets safely.

## After Portability

- [ ] Explain amd64 and arm64.
- [ ] Build with `buildx`.
- [ ] Identify native dependency risks.

## Final

- [ ] Build Python pipeline images.
- [ ] Build dbt images.
- [ ] Explain PySpark image construction.
- [ ] Explain orchestrator task images.
- [ ] Debug common failures.

---

# 37. Final Practical Assessment

## Objective

Build a production-style Python pipeline image satisfying all requirements.

## 37.1 Requirements

Your image must include:

- Python application
- `uv`
- locked dependencies
- `.dockerignore`
- optimized caching
- multi-stage build where appropriate
- non-root user
- correct `ENTRYPOINT`/`CMD`
- graceful SIGTERM handling
- reproducible base-image strategy
- immutable image tagging
- vulnerability scanning
- SBOM
- no embedded secrets
- multi-platform build

## 37.2 Expected Repository Structure

```text
pipeline/
├── src/
│   └── pipeline/
│       ├── __init__.py
│       └── main.py
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── .dockerignore
└── docs/
    └── image-engineering-notes.md
```

## 37.3 Tasks

### Task 1

Create a pipeline that accepts:

```bash
--date YYYY-MM-DD
```

### Task 2

Create a locked Python dependency environment.

### Task 3

Write an optimized Dockerfile.

### Task 4

Run the application as non-root.

### Task 5

Use exec-form process startup.

### Task 6

Implement graceful SIGTERM handling.

### Task 7

Build with an identifiable Git SHA tag.

### Task 8

Record the resulting image digest.

### Task 9

Scan the image.

### Task 10

Generate an SBOM.

### Task 11

Build for required architectures.

### Task 12

Document:

- image size
- build time
- cache behavior
- vulnerability findings
- remediation
- runtime user
- artifact identity

## 37.4 Validation Commands

Build:

```bash
docker build -t pipeline:assessment .
```

Run:

```bash
docker run --rm pipeline:assessment --date 2026-10-01
```

Inspect:

```bash
docker images
docker ps -a
```

Scan:

```bash
trivy image pipeline:assessment
```

Generate SBOM where supported:

```bash
trivy image --format cyclonedx --output sbom.json pipeline:assessment
```

Multi-platform:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <registry>/<repository>:<immutable-tag> \
  --push \
  .
```

Verify published platforms:

```bash
docker buildx imagetools inspect <registry>/<repository>:<immutable-tag>
```

## 37.5 Failure Scenarios

Intentionally test:

1. Change only source code.
2. Change a dependency.
3. Remove a required permission.
4. Send SIGTERM.
5. Run under the wrong architecture.
6. Introduce a deliberately detectable test secret through an unsafe build pattern, then remove it and rebuild safely.
7. Compare naive and optimized image sizes.
8. Compare initial and cached build times.

Use non-production credentials only.

## 37.6 Expected Learning Outcomes

A successful learner can explain:

```text
Why the Dockerfile is structured this way
Why dependencies are copied before source
Why the runtime is non-root
Why secrets are excluded
Why the image has an immutable identity
Why the image supports selected architectures
How vulnerabilities are discovered and remediated
How graceful shutdown works
```

---

# 38. Senior Data Engineer Interview Questions

## 1. Why use containers for data pipelines?

**Answer:** Containers package application dependencies and runtime configuration into a portable execution artifact, reducing environment drift between development, CI, and production.

## 2. What is the difference between an image and a container?

**Answer:** An image is an immutable-style packaged artifact containing filesystem contents and metadata; a container is a runtime instance of that image.

## 3. What are Docker layers?

**Answer:** Layers represent reusable filesystem/build changes that compose into an image. Layer reuse can reduce build time and storage.

## 4. Why does Docker build context matter?

**Answer:** The build context defines files available to the build. Large or sensitive contexts slow builds and can expose unnecessary data.

## 5. Why use `.dockerignore`?

**Answer:** It prevents unnecessary files from entering the build context, improving performance and reducing accidental exposure.

## 6. Why is `COPY . .` before dependency installation often inefficient?

**Answer:** Changes to any copied source file can invalidate the dependency-installation layer, forcing expensive dependency work to run again.

## 7. Why copy `pyproject.toml` and `uv.lock` first?

**Answer:** Dependency installation then depends primarily on dependency metadata, allowing source-only changes to reuse the dependency layer.

## 8. Why use `uv.lock` in production?

**Answer:** It records the resolved dependency graph so production builds are based on controlled versions rather than a newly resolved dependency set.

## 9. Why might Alpine be problematic for some Python workloads?

**Answer:** Its libc environment differs from Debian-based images, which can create compatibility or performance issues for packages with native components.

## 10. Why is Debian slim often a practical Python data-engineering base?

**Answer:** It balances relatively small image size with broad compatibility and a familiar Linux userspace.

## 11. What is a multi-stage build?

**Answer:** It separates build-time and runtime environments so build tools and unnecessary artifacts do not have to be shipped in the runtime image.

## 12. Why run containers as non-root?

**Answer:** Least privilege reduces unnecessary permissions and can limit the impact of a compromised application.

## 13. What is the difference between `ARG` and `ENV`?

**Answer:** `ARG` is primarily a build-time parameter; `ENV` defines environment configuration available to the image/container. Neither should be used as a secure secret store.

## 14. Why prefer exec-form `ENTRYPOINT`?

**Answer:** It allows the application process to receive signals more directly instead of introducing a shell as an unnecessary process layer.

## 15. What is PID 1?

**Answer:** PID 1 is the primary process in the container's process namespace and has special process-management and signal semantics.

## 16. Why does SIGTERM matter for data pipelines?

**Answer:** It gives a workload an opportunity to stop safely, finish or checkpoint appropriate work, release resources, and exit before forced termination.

## 17. What is the difference between `ENTRYPOINT` and `CMD`?

**Answer:** `ENTRYPOINT` can define the primary executable while `CMD` supplies default arguments or command behavior that can be overridden.

## 18. Does every batch image need a health check?

**Answer:** No. Health checks are particularly useful for long-running services. A batch workload may communicate health and success through its process lifecycle and exit status.

## 19. Why is `latest` a poor production identity?

**Answer:** It is mutable. The same tag can point to different image contents over time, making deployment identity and rollback ambiguous.

## 20. Why is a digest useful?

**Answer:** A digest identifies exact image content, making the artifact independently identifiable even if tags move.

## 21. Why should secrets never be baked into images?

**Answer:** Images are copied, cached, stored, and distributed. A secret embedded in an image can persist in layers and become widely exposed.

## 22. Why does deleting a secret in a later layer not solve the problem?

**Answer:** Earlier layers may still contain the original secret.

## 23. What are BuildKit secrets?

**Answer:** They provide temporary secret material to build steps without intentionally baking that secret into the resulting image.

## 24. What is an SBOM?

**Answer:** A Software Bill of Materials is an inventory of software components contained in an artifact.

## 25. Why do data platforms need SBOMs?

**Answer:** Data platforms depend on many Python, OS, native, and JVM components. An SBOM improves vulnerability identification, incident response, and inventory.

## 26. How would you handle an image vulnerability?

**Answer:** Identify the affected component, assess severity and applicability, determine a safe upgrade, rebuild, test, rescan, and record the result.

## 27. What is `buildx`?

**Answer:** Docker Buildx provides advanced BuildKit-based build functionality, including multi-platform builds.

## 28. Why can an image work on ARM but fail on amd64?

**Answer:** Native extensions, compiled binaries, or platform-specific dependencies may not be available or compatible on both architectures.

## 29. What makes a good Python pipeline image?

**Answer:** Controlled dependencies, efficient caching, minimal runtime contents, non-root execution, correct lifecycle behavior, externalized configuration, security scanning, and traceable artifact identity.

## 30. Why containerize dbt?

**Answer:** To make the dbt runtime, adapter dependencies, and project environment reproducible and isolated across development, CI, and execution environments.

## 31. Why is a PySpark image different from an ordinary Python image?

**Answer:** PySpark involves Python plus Spark and JVM/Java runtime components, creating additional compatibility and packaging considerations.

## 32. Why are container images useful for orchestrated tasks?

**Answer:** They provide dependency isolation and allow the orchestrator to execute a known runtime artifact rather than relying on a mutable worker environment.

## 33. How would you reduce Docker build time?

**Answer:** Reduce context size, improve layer ordering, isolate stable dependency inputs, use build caches appropriately, and measure actual build behavior.

## 34. How would you reduce image size?

**Answer:** Use an appropriate slim base, remove unnecessary runtime dependencies, use multi-stage builds, and avoid copying development artifacts.

## 35. How do you know an image is production-ready?

**Answer:** It should have controlled dependencies and base inputs, least privilege, no embedded secrets, appropriate runtime lifecycle behavior, security validation, SBOM visibility, immutable artifact identity, and measured performance.

---

# 39. Final Mastery Checklist

## Fundamentals

- [ ] I can explain “works on my machine.”
- [ ] I can explain containers vs VMs.
- [ ] I understand Dockerfile → image → container → process.
- [ ] I understand layers and registries.
- [ ] I understand tags and digests.

## CLI

- [ ] I can build an image.
- [ ] I can run a container.
- [ ] I can inspect running and stopped containers.
- [ ] I can read logs.
- [ ] I can execute a debugging command.
- [ ] I can stop and remove containers.
- [ ] I can pull and push images.

## Dockerfile

- [ ] I understand `FROM`.
- [ ] I understand `WORKDIR`.
- [ ] I understand `COPY`.
- [ ] I understand `RUN`.
- [ ] I understand `ENV`.
- [ ] I understand `ARG`.
- [ ] I understand `USER`.
- [ ] I understand `ENTRYPOINT`.
- [ ] I understand `CMD`.
- [ ] I understand `EXPOSE`.
- [ ] I understand `HEALTHCHECK`.

## Build Engineering

- [ ] I understand build context.
- [ ] I can write `.dockerignore`.
- [ ] I understand layer caching.
- [ ] I can isolate dependency installation from source changes.
- [ ] I can measure build improvements.

## Python

- [ ] I understand Python base-image choices.
- [ ] I understand slim images.
- [ ] I understand why Alpine can cause native-library compatibility issues.
- [ ] I can use `uv`.
- [ ] I understand `uv.lock`.
- [ ] I can install locked runtime dependencies.
- [ ] I understand dependency cache mounts.

## Runtime Security

- [ ] I can create a non-root runtime.
- [ ] I can diagnose file ownership problems.
- [ ] I can externalize configuration.
- [ ] I know not to put credentials in images.
- [ ] I understand build secrets.

## Process Lifecycle

- [ ] I understand PID 1.
- [ ] I understand SIGTERM.
- [ ] I understand SIGKILL.
- [ ] I can implement graceful shutdown.
- [ ] I understand exec-form entrypoints.
- [ ] I understand when an init process may help.
- [ ] I understand when a health check is appropriate.

## Reproducibility

- [ ] I use locked dependencies.
- [ ] I understand base-image pinning.
- [ ] I understand immutable tags.
- [ ] I record Git SHA.
- [ ] I can identify an image by digest.
- [ ] I understand why artifact identity matters for rollback.

## Security and Supply Chain

- [ ] I can scan an image.
- [ ] I can interpret vulnerability findings.
- [ ] I can remediate and rescan.
- [ ] I can generate an SBOM.
- [ ] I understand why image layers can retain secrets.
- [ ] I understand the basic supply-chain risks of container images.

## Portability

- [ ] I understand amd64.
- [ ] I understand arm64.
- [ ] I understand native dependency risks.
- [ ] I can use `buildx`.
- [ ] I can build for multiple platforms.
- [ ] I can verify published platform support.

## Data Engineering Workloads

- [ ] I can design a Python pipeline image.
- [ ] I understand how to design a dbt runtime image.
- [ ] I understand why PySpark images are different.
- [ ] I understand how orchestrators can execute task images.

## Production Engineering

- [ ] I measure image size.
- [ ] I measure build time.
- [ ] I measure cache reuse.
- [ ] I measure vulnerability changes.
- [ ] I can debug slow builds.
- [ ] I can debug immediate container exits.
- [ ] I can debug SIGTERM problems.
- [ ] I can debug permission problems.
- [ ] I can respond to image secret leakage.
- [ ] I can diagnose architecture mismatches.

---

# Closing Mental Model

A production Docker image for a data pipeline should be thought of as a **software release artifact**, not merely a convenient way to run Python.

The engineering chain is:

```text
Source code
    +
Locked dependencies
    +
Controlled base image
    +
Secure Dockerfile
    +
Efficient build context
    +
Layer-aware caching
    +
Least-privilege runtime
    +
Correct process lifecycle
    +
No embedded secrets
    +
Security scan
    +
SBOM
    +
Immutable artifact identity
    +
Required architecture support
        ↓
Production-ready image
```

The most important principles are:

> **Package once.**
>
> **Keep dependencies controlled.**
>
> **Build efficiently.**
>
> **Run with least privilege.**
>
> **Keep configuration outside the artifact.**
>
> **Never put credentials into image layers.**
>
> **Know what is inside the image.**
>
> **Identify the exact artifact that runs in production.**
>
> **Handle termination correctly.**
>
> **Measure optimization rather than guessing.**

Once these principles are understood, the same image can become the stable execution unit for the next layers of the data platform: local container stacks, Kubernetes workloads, CI/CD, and production data-engineering systems.
