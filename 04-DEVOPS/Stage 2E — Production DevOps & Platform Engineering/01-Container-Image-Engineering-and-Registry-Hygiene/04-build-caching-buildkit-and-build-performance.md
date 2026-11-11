# Unit 4 — Build Caching, BuildKit, and Build Performance

**Build reliable speed, not just fast builds.** This lesson explains how Docker and BuildKit reuse build work, how to design cache-friendly data-service images, how to measure build performance without fooling yourself, and how to operate shared caches and builders without treating cached content as trusted by default.

**Target file:** `04-build-caching-buildkit-and-build-performance.md` | **Module:** M01 | **Stage:** 2E  
**Estimated time:** 8–12 hours | **Prerequisites:** Git, Linux shell, Python basics, Docker build/run basics  
**Core tools:** Docker Engine/CLI, BuildKit, `docker buildx`, shell, Python, `time`, Git  
**Awareness tools:** GitHub Actions `gha` cache, S3 cache backend, remote/hosted builders, Kubernetes driver, Bazel, Nix, commercial build analytics  
**Last reviewed:** 2026-10-24 (AI self-audit; live documentation and labs not executed)  
**Assumed baseline:** WSL2 Ubuntu or native Linux, approximately 4 CPU cores, 8 GB RAM, 30 GB free disk. Docker Desktop and native Docker Engine differ; record which one you use.

> **Scope note:** The supplied prompt is the syllabus authority available for this draft. The repository roadmap and live official documentation were not available for direct inspection in this authoring context. All command outputs below are representative unless explicitly labeled as learner-generated. Do not treat example timings, cache messages, IDs, sizes, or ratios as measurements.

## Table of Contents

- [4.0 Why this matters in production](#40-why-this-matters-in-production)
- [4.1 Learning objectives](#41-learning-objectives)
- [4.2 Concept map and vocabulary](#42-concept-map-and-vocabulary)
- [4.3 Level 1 — Beginner: Foundations](#43-level-1--beginner-foundations)
- [4.4 Level 2 — Intermediate: Working Practice](#44-level-2--intermediate-working-practice)
- [4.5 Level 3 — Advanced: Production Engineering](#45-level-3--advanced-production-engineering)
- [4.6 Level 4 — Expert: Operating at Scale and Under Failure](#46-level-4--expert-operating-at-scale-and-under-failure)
- [4.7 SRE lens](#47-sre-lens)
- [4.8 Security lens](#48-security-lens)
- [4.9 Production checklist](#49-production-checklist)
- [4.10 Hands-on lab set](#410-hands-on-lab-set)
- [4.11 Self-check questions](#411-self-check-questions)
- [4.12 Evidence artifacts](#412-evidence-artifacts)
- [4.13 Common interview and design-review questions](#413-common-interview-and-design-review-questions)
- [4.14 Sources and verification notes](#414-sources-and-verification-notes)
- [Appendix A — Claim Register](#appendix-a--claim-register)
- [Appendix B — Audit Report](#appendix-b--audit-report)
- [Appendix C — Verification Checklist for the Human Reviewer](#appendix-c--verification-checklist-for-the-human-reviewer)
- [Appendix D — Known Limitations and Assumptions](#appendix-d--known-limitations-and-assumptions)
- [Appendix E — Sign-off](#appendix-e--sign-off)

## 4.0 Why this matters in production

A slow image build is not merely an inconvenience: it lengthens feedback loops, increases CI queue time, consumes runner capacity, and can delay a safe dependency or security patch. A shared cache can reduce repeated work, but it can also become a failure domain if its credentials expire, its storage fills, or a less-trusted branch can publish cache state consumed by a release build. Aggressive cache retention may exhaust disk; aggressive pruning can turn a routine build into a cold build during an incident. Production engineering therefore treats build performance as a measured reliability property, with explicit cache ownership, trust boundaries, cleanup policy, and a tested fallback when cache reuse disappears.

## 4.1 Learning objectives

1. **[L1] Explain** how Docker/BuildKit decide whether a build step can be reused and what a cache hit does not prove.
2. **[L1] Demonstrate** cold, unchanged warm, and deliberate source-change builds while reading progress output.
3. **[L2] Refactor** a Python data-service Dockerfile to copy dependency manifests before application code and use an appropriate cache mount.
4. **[L2] Measure** build context size, cache reuse, and before/after performance without inventing results.
5. **[L3] Compare** buildx drivers and cache backends by portability, security, operational complexity, and failure modes.
6. **[L3] Run** a repeatable benchmark harness that reports median and p95 for cold, warm, and partial-change scenarios.
7. **[L4] Design** cache boundaries for ephemeral CI runners, monorepos, multiple platforms, and trusted versus untrusted branches.
8. **[L4] Define** a measurable build-time SLO, a regression guard, and a safe cache-loss incident runbook.

## 4.2 Concept map and vocabulary

```text
Dockerfile + build context + ARGs + base image + prior stage outputs
                              |
                        cache-key inputs
                              |
                    cache lookup (builder)
                       /              \
                  cache hit          cache miss
                     |                   |
                reuse result        execute instruction
                     |                   |
                     +------ next step --+
                               |
                    changed output invalidates
                    dependent downstream work
                               |
              optional cache export/import backend
                               |
              later build may reuse eligible results
```

| Term | Definition | Common misconception |
|---|---|---|
| **Build step/instruction** | A Dockerfile operation or BuildKit graph operation that produces an output. | Every line always corresponds to one simple legacy layer operation. |
| **Instruction cache** | Stored result of an eligible build operation, reused when its relevant cache inputs match. | A cache hit validates that external systems are unchanged or trustworthy. |
| **Cache key** | Identity derived from the operation and relevant inputs as defined by the builder. Exact implementation details vary. | It is always a hash of only the Dockerfile line. |
| **Cache invalidation** | A change causes a step to miss cache and often requires dependent downstream steps to execute again. | Every change invalidates the entire build, or every change is detected. |
| **Build context** | Files available to the builder, after exclusions such as `.dockerignore`. | The context contains only Git-tracked files. |
| **BuildKit** | Docker's modern build engine with a build graph, concurrent work where possible, and configurable cache/export features. | Every installation has the same defaults or legacy builder behavior. |
| **Cache mount** | Mutable build-time cache storage mounted into a `RUN` operation, commonly for package-manager downloads. | It is automatically included in the final runtime image. |
| **Exported cache** | Cache metadata/results exported to a local directory, registry, inline image metadata, or supported backend. | It is the same thing as a pushed runtime image. |
| **Builder** | The configured build execution environment managed through buildx. | A builder always runs inside the Docker daemon you happen to use for `docker ps`. |
| **Driver** | The mechanism by which buildx connects to or manages a builder, such as `docker` or `docker-container`. | Driver choice affects only performance, not isolation or capabilities. |
| **Cold build** | For a defined experiment, a build with the relevant reusable instruction cache unavailable. | `--no-cache` makes every other condition cold, including OS page cache and registry state. |
| **Warm build** | A repeat using the same eligible inputs with relevant build cache available. | The result must be fast on every machine. |
| **Partial-change build** | A controlled change to one input class, such as application source while dependency manifests remain unchanged. | Any source change should invalidate dependency installation. |
| **Cache poisoning** | A less-trusted actor influences cache data consumed by a more-trusted build. | A cache is trustworthy because the builder produced it. |
| **Build-time SLO** | A defined objective for a measured build class and time window. | A single average build time is a meaningful SLO. |
| **p95** | The 95th percentile under a specified percentile convention. | p95 is the same as maximum or average. |

Important distinctions:

- **Instruction cache** reuses the result of a build operation.
- **Cache mount** preserves package-manager state for later build operations on a builder that retains it.
- **Exported/imported cache** allows eligible build cache to be shared beyond a local builder, subject to backend support and trust policy.
- **Runtime image layers** are part of the produced image. A cache mount is not automatically committed into those layers.
- **Registry layer blobs** are image distribution objects. A registry cache may store build-cache metadata and records in a way that is not equivalent to a normal runnable image.
- **Build history** and progress output are observability aids; availability and exact commands depend on tool version.

## 4.3 Level 1 — Beginner: Foundations

### How cache hits and misses work

A build is a dependency graph. BuildKit can reuse a previous operation result when its relevant inputs and cache metadata match. A changed Dockerfile instruction can alter the operation; changed copied files can alter the input checksum; changed build arguments can affect instructions that consume them; changed prior-stage output can affect a dependent stage. Exact cache-key rules are builder-defined, so avoid simplistic claims such as “Docker hashes every line” or “timestamps always invalidate COPY.” Verify the behavior with a controlled experiment.

A common, simplified Dockerfile:

```dockerfile
# File: Dockerfile.l1
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN python -m pip install fastapi uvicorn
CMD ["python", "-m", "service"]
```

This is suitable only as an early demonstration, not a production pattern. The dependency installation is after `COPY . .`, so changing a source file may force the install step to run again. Dependencies are also not locked, and the base tag is mutable. The image selection and pinning details are covered in Unit 2; reproducibility and digest identity are covered in Unit 3.

### Read BuildKit progress

```bash
docker build --progress=plain -f Dockerfile.l1 -t cache-demo:l1 .
```

**EXPECTED / REPRESENTATIVE:** progress lines may include `CACHED`, a running `RUN` step, context transfer, and final image export. Exact wording and step identifiers vary by builder/version. A `CACHED` marker indicates reuse of that eligible operation; it does not establish dependency freshness, security, correctness, or trustworthy inputs.

`docker build --no-cache ...` requests a build without reusing the ordinary instruction cache for the build. It is useful to test whether a build can execute from its declared sources or to diagnose cache-related assumptions. It does **not** guarantee a fully controlled cold benchmark: base images may remain locally available, OS page cache remains warm, network and registry state vary, and package managers may have their own caches. It also does not automatically disable every cache mount or external service cache. Check current CLI behavior for your installed version.

### BuildKit versus legacy builder

Conceptually, the legacy builder processed Dockerfile steps with a more linear model, while BuildKit models build work as a graph and can execute independent work concurrently, support richer mounts, and export/import caches. This is a conceptual comparison, not a guarantee about every feature or default. The legacy builder may be unavailable, deprecated, or not the default in current installations. **[VERIFY]** Inspect your Docker version and current Docker build documentation instead of assuming a switch exists.

### Guided L1 lab: cold, warm, source change

Create a dedicated lab directory, not a repository root with unrelated files:

```bash
# File: lab-l1.sh
set -euo pipefail
mkdir -p "$HOME/unit04-cache-lab"
cd "$HOME/unit04-cache-lab"
mkdir -p service
printf 'from http.server import BaseHTTPRequestHandler, HTTPServer\n' > service/app.py
printf 'print("service ready")\n' > service/__main__.py
cat > Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY service/ ./service/
CMD ["python", "-m", "service"]
EOF
docker build --progress=plain -t unit04-l1:local .
docker build --progress=plain -t unit04-l1:local .
printf '\n# controlled source change\n' >> service/app.py
docker build --progress=plain -t unit04-l1:local .
```

**EXPECTED / REPRESENTATIVE:** first build performs transfers and executes uncached steps; second may report eligible steps as cached; third should show cache behavior affected by the source change, although exact downstream messages vary. The example's Python module is intentionally minimal and may exit immediately; it is for cache observation, not a production API.

**What just happened?** The second invocation used the same declared inputs, making prior results eligible for reuse. The source edit changes an input consumed by `COPY`; dependent operations may need reevaluation. The build may still use cache for unrelated independent operations.

**Common mistakes**

| Symptom | Likely cause | Fix |
|---|---|---|
| Every source edit repeats dependency install | Dependencies installed after broad source copy | Copy manifest first; install dependencies; copy source later |
| Build unexpectedly misses cache | Relevant input changed, cache unavailable, or operation not cacheable | Compare logs and inputs; do not assume a bug |
| `--no-cache` is slower but proves little | It changes cache reuse but not all environmental state | Define the experiment and record what was cleared/retained |
| Large “transferring context” step | Unnecessary files included | Add and validate `.dockerignore` |
| Cached output contains stale external content | External input was not represented/pinned adequately | Pin versions/digests and avoid hidden network dependencies |

## 4.4 Level 2 — Intermediate: Working Practice

### Dependency-manifest-first ordering

A Python data service should separate slowly changing dependency inputs from frequently changing source:

```dockerfile
# File: service/Dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY service/ ./service/
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

The `requirements.txt` must exist at `service/requirements.txt` relative to the chosen context and contain the application's actual dependencies. In production, use a reviewed lock strategy; this example focuses on cache ordering and is not a substitute for Unit 3's reproducibility controls.

When application source changes but `requirements.txt` does not, the dependency-install operation may remain cache-eligible. When the manifest changes, the install operation should be reevaluated. This reduces repeated work without concealing dependency changes.

A contrasting Go pattern:

```dockerfile
# File: go-service/Dockerfile
FROM golang:1.24 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/service ./cmd/service
FROM scratch
COPY --from=build /out/service /service
ENTRYPOINT ["/service"]
```

**[VERIFY]** The version is an illustrative example tag, not a recommendation to use an unpinned tag in production; check the official Go image and current toolchain support before adopting it. The cache lesson is that `go.mod`/`go.sum` are copied before source so unchanged dependency manifests can preserve the download step. This Dockerfile requires a matching Go project and is not intended to run as-is without one.

### Cache mounts

A cache mount can preserve package-manager download/build cache between `RUN` operations when the builder retains that mount state:

```dockerfile
# File: service/Dockerfile.cache-mount
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt
COPY service/ ./service/
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**[VERSION-SENSITIVE]** `RUN --mount=type=cache` requires a BuildKit-capable frontend/builder and compatible configuration. Check Dockerfile reference, BuildKit documentation, and `docker buildx build --help` for the installed versions.

The mount stores pip cache files at build time. It is not automatically included in the final runtime image, unlike files written to ordinary image filesystem paths by a `RUN` step. Its lifetime and sharing depend on builder configuration and cache retention; a new ephemeral builder may not have the mount. Do not treat it as a durable package repository or trust boundary. Keep package integrity checks enabled.

### `.dockerignore` and build-context transfer

Example:

```text
# File: service/.dockerignore
.git
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
data/
datasets/
notebooks/
.env
.env.*
*.pem
*.key
```

Review patterns against your project: ignoring `data/` is correct only if the build does not require those files. `.dockerignore` is both a performance and confidentiality control. A secret excluded from the context is less likely to be accidentally copied into an image, but this does not replace secret management.

Measure context size before and after using a bounded file inventory and build progress:

```bash
du -sh service
find service -type f -not -path '*/.git/*' | wc -l
docker build --progress=plain -f service/Dockerfile -t etl-api:context-test service
```

**EXPECTED / REPRESENTATIVE:** `du` reports the directory's current size, `find` counts files, and build progress may show a context transfer step. The directory size is not exactly the transmitted context size; Docker ignores patterns and may package metadata differently. Record both values before/after a `.dockerignore` change. Do not claim a reduction until you measure it.

Local builders may prepare context on the client and transfer it to a builder; remote builders can incur network transfer across a boundary. The visible progress and exact accounting differ by builder. Avoid sending `.git`, virtual environments, datasets, local wheels, or credentials unless the build explicitly needs them.

### Parallel stages and build graph

Independent stages can execute concurrently when the build graph and builder permit it. For example, a test stage and a runtime dependency preparation stage may share a base but have no dependency on each other's outputs. A final stage that copies from both must wait for both.

```dockerfile
# File: service/Dockerfile.parallel
FROM python:3.12-slim AS deps
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim AS source
WORKDIR /src
COPY service/ .
RUN python -m compileall -q .

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=deps /install /usr/local
COPY --from=source /src /app/service
CMD ["python", "-m", "service"]
```

This illustrates stage dependencies, not a claim that all three stages will always run in parallel or that this is a complete packaging pattern. A real runtime stage must ensure the copied Python package layout and installed dependencies are correct. The graph determines what must wait; the builder schedules eligible independent work subject to resource limits.

### Before/after pattern catalogue

| Pattern | When to use | When not to use |
|---|---|---|
| Copy dependency manifest, install, then copy source | Application code changes more often than dependencies | Manifest generation itself depends on source in an inseparable way |
| Cache mount for package manager | Repeated downloads/build artifacts are expensive and safe to cache | Cache contents are untrusted or the tool cannot use the mount |
| Narrow `.dockerignore` | Repository has large local artifacts or sensitive files | A needed build input is accidentally excluded |
| Split build/test/runtime stages | Independent work or runtime minimization benefits from separation | Stages add complexity without reuse or clarity |
| Pin inputs and lock dependencies | Controlled release and repeatable dependency resolution matter | Never update pins; stale vulnerable dependencies become a risk |

### Anti-pattern catalogue

| Anti-pattern | Why it hurts | Better alternative |
|---|---|---|
| `COPY . .` before dependency install | Every source change can invalidate dependency installation | Copy lock/manifest first |
| Build context includes `.venv`, datasets, `.git`, and secrets | Slow transfers, accidental leaks, noisy cache invalidation | Use a reviewed `.dockerignore` and narrow context |
| Cache mount assumed to persist across ephemeral builders | Builds slow down after builder replacement | Export/import supported cache or accept measured cold behavior |
| Cache mount used as the only integrity control | Cache may contain stale or compromised artifacts | Keep hash/signature/package-manager verification |
| Add `--no-cache` to every build for “correctness” | Discards useful instruction cache without proving correctness | Use controlled invalidation tests and explicit input pinning |

## 4.5 Level 3 — Advanced: Production Engineering

### Buildx builders and drivers

A buildx builder is the environment that executes BuildKit work. Driver capabilities and defaults vary; verify installed versions and the selected driver.

| Driver | Where work runs | Benefit | Operational/security implication |
|---|---|---|---|
| `docker` | BuildKit integrated with the Docker daemon | Simple local workflow | Capabilities and cache export behavior may be limited by the installed Docker integration |
| `docker-container` | BuildKit runs in a dedicated container managed by Docker | Separate BuildKit lifecycle and commonly used for buildx features | Requires builder container image, storage, lifecycle, and resource management |
| `kubernetes` | BuildKit workers run in Kubernetes | Can use cluster capacity and shared operations | Cluster RBAC, workload isolation, secrets, network policy, node capacity, and tenant separation matter |
| `remote` | buildx connects to a separately managed BuildKit endpoint | Flexible centralized/remote builder | Endpoint authentication, TLS, authorization, builder trust, network access, and ownership must be designed |

**[VERIFY]** Driver availability, options, defaults, and cache compatibility depend on buildx/BuildKit version and environment. Inspect local configuration:

```bash
docker buildx ls
docker buildx inspect
docker buildx version
```

**EXPECTED / REPRESENTATIVE:** a list of builders, current builder details, and buildx version. Save the output in evidence. Do not infer remote isolation or authentication merely from a driver name.

### Cache backends

| Backend | Requirements / portability | Runner fit | Trust boundary | Complexity and trade-off |
|---|---|---|---|---|
| `inline` | Cache metadata is associated with image output; exact export behavior is version-sensitive | Simple when publishing an image and cache together | Writers of the image/cache metadata influence future cache consumers | Easy to start; may constrain cache export mode compared with separate cache exporters |
| `registry` | Registry access and supported buildx/BuildKit configuration | Useful for ephemeral runners that can pull/push a dedicated cache reference | Registry permissions and cache-reference separation are critical | Portable across runners; storage and retention must be managed |
| `local` | Local filesystem path available to builder/client as required by configuration | Persistent self-hosted runner or local experiments | Host filesystem access and permissions | Simple and inspectable, but not automatically shared across ephemeral hosts |
| `gha` | GitHub Actions cache service and supported BuildKit/buildx integration | GitHub Actions workflow | Branch/ref cache access rules and token permissions matter | Convenient but provider-specific quotas/eviction/permissions apply; awareness-only |
| `s3` | **[VERIFY]** support may require specific BuildKit version/configuration or a plugin/implementation; do not assume universal availability | Environments already operating controlled object storage | Bucket IAM, key prefixes, encryption, and tenant separation | Portable conceptually, but availability and syntax must be verified for the exact implementation |

`mode=min` generally exports cache records needed for the final result, while `mode=max` can retain intermediate-stage cache records and may improve reuse for multi-stage builds at additional storage/transfer cost. **[VERIFY]** Confirm exact semantics and accepted values for the selected exporter and installed BuildKit/buildx version.

Representative registry cache pattern:

```bash
docker buildx build \
  --cache-from type=registry,ref=registry.example/team/etl-api:buildcache \
  --cache-to type=registry,ref=registry.example/team/etl-api:buildcache,mode=max \
  --tag registry.example/team/etl-api:dev \
  --push .
```

**[VERIFY]** This is a pattern, not a runnable command until the registry/repository is replaced and the selected builder supports the exporter/options. It requires appropriate authentication and write permission. Do not use a release image tag as a cache reference unless your cache and promotion policy intentionally couples them.

Representative local cache pattern:

```bash
docker buildx build \
  --cache-from type=local,src="$PWD/.buildx-cache" \
  --cache-to type=local,dest="$PWD/.buildx-cache-next",mode=max \
  --load -t etl-api:local .
```

This avoids reading and writing the same local cache directory in one command. After confirming the build succeeded, rotate directories in a controlled script; do not blindly overwrite a live cache. **[VERIFY]** Exact exporter support and output requirements depend on driver/version. `--load` is intended for loading a single-platform result into the local Docker image store in supported configurations; verify for your builder.

### Measurement protocol

A benchmark is a controlled experiment. Before measuring:

1. Define workload and target platform; keep source and dependencies fixed.
2. Record commit or local snapshot, Dockerfile, lockfile, builder/driver, CPU/RAM/disk, and Docker/Buildx versions.
3. Define **cold** precisely (relevant instruction cache unavailable), **warm** (same inputs and cache retained), and **partial change** (one controlled source change while manifests remain unchanged).
4. Perform one warm-up outside the scored sample where appropriate; for cold trials, restore the defined cold condition for every repetition.
5. Run at least several repetitions (default harness uses N=3 to fit the laptop budget; use more for decision-grade evidence).
6. Capture wall-clock durations with a monotonic clock and save raw logs. Report median and p95 using the nearest-rank convention, explicitly stated.
7. Keep package downloads and remote network effects consistent or measure them separately. Do not mix a network outage with a cache comparison.
8. Avoid concurrent builds and note CPU throttling, WSL2 filesystem location, page cache, registry latency, and builder warm-up.

`time` can provide a quick wall-clock observation:

```bash
/usr/bin/time -f 'elapsed_seconds=%e user_seconds=%U sys_seconds=%S' \
  docker build --progress=plain -t etl-api:timing .
```

**EXPECTED / REPRESENTATIVE:** elapsed, user, and system seconds after the build command. The numbers are not portable or measured here. Use `BUILDKIT_PROGRESS=plain` or `--progress=plain` to preserve readable logs. **[VERIFY]** Build-history commands such as `docker buildx history` and their exact subcommands depend on buildx version; consult the current buildx reference and local `docker buildx --help`.

### Cache-key pitfalls and invalidation matrix

| Change/input | Likely affected operations | Verify | Mitigation |
|---|---|---|---|
| Application source changed after manifest-first install | Source copy and downstream packaging/runtime steps | Plain progress log; compare step cache messages | Keep dependency install before source copy |
| Lockfile/manifest changed | Dependency installation and dependent stages | Hash/diff lockfile; inspect build log | Review dependency updates and avoid needless lock regeneration |
| Build `ARG` changed | Operations that consume the argument and downstream outputs | Compare exact build args and logs | Use args only where needed; do not encode volatile metadata into expensive steps |
| Broad `COPY . .` | Copy and downstream steps on many file changes | Inspect context manifest and ignore rules | Narrow `COPY` paths and improve `.dockerignore` |
| Generated files or timestamps in context | Copy/build steps consuming them | Hash context files before/after | Generate deterministically or exclude irrelevant generated artifacts |
| `.git` or build output included | Context transfer and copy cache keys | `du`, `find`, plain progress | Exclude non-input files |
| Platform/architecture changes | Base, dependency selection, compilation, output | Record `--platform`; inspect manifests | Benchmark each platform separately |
| Builder/cache backend changed | Cache import/reuse and execution | `buildx ls/inspect`, cache logs | Record builder identity and test import/export |
| Hidden network download in `RUN` | May not invalidate merely because remote content changed | Review Dockerfile and external inputs | Pin URL/version/hash; fetch and verify controlled artifact |
| Environment/locale/timezone changes | Operations that read environment; generated files | Record relevant env, inspect output | Normalize relevant values and avoid ambient dependencies |

A cache key cannot reliably represent an external mutable resource that the build command reads without an explicit input boundary. For example, `RUN curl https://example.invalid/current.tar.gz` may reuse an old cached result even if the remote file changed; forcing execution can instead fetch new content. The remedy is to use an explicit versioned artifact and verify its checksum/signature, not to rely on cache behavior.

### Trade-off table

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Local instruction cache | Lowest setup complexity | Limited to builder's retained state | Cache lost with builder or disk cleanup | Developer workstation or persistent runner |
| Cache mount | Reuses package-manager downloads | State is mutable and builder-dependent | Cross-build trust and lifecycle concerns | Downloads/compilation dominate repeated builds |
| Registry cache, `mode=min` | Portable cache with smaller footprint | May not preserve all intermediate results | Misses some multi-stage reuse | Simple release build or storage-constrained environment |
| Registry cache, `mode=max` | More intermediate-stage reuse | More storage and transfer | Cache grows and requires retention/permissions | Expensive multi-stage builds with trusted writers |
| Local cache export | Inspectable, no paid service | Local storage and rotation logic | Stale/permission issues | Local labs or persistent self-hosted workers |
| Remote/shared builder | Central capacity and shared cache | Network, access control, ownership | Central failure domain or tenant exposure | Multiple teams with platform support |
| QEMU emulation for foreign architecture | Convenient cross-platform builds on one host | Emulation overhead for some workloads | Misleading timing and architecture-specific failures | Convenience or modest build workloads |
| Native per-architecture nodes | Better native execution characteristics | More infrastructure and cache coordination | Node drift and duplicated capacity | High-volume multi-platform production builds |

### L3 lab decision: choose the cache architecture

Use your own evidence from the benchmark harness in Section 4.10. Decide between local cache, local exported cache, or a registry cache for ephemeral workers. Defend the choice with measured cold/warm/partial-change p50/p95, cache storage size, transfer time, trust boundaries, and failure behavior. If registry access or a second runner is unavailable, produce a design record with explicit assumptions; do not claim cross-runner performance was measured.

## 4.6 Level 4 — Expert: Operating at Scale and Under Failure

### Ephemeral CI runners

Ephemeral runners start without a local instruction cache unless one is restored or imported. A typical strategy is:

- Use a narrowly scoped, versioned cache reference per service and trust class.
- Import cache at build start and export only after a successful build.
- Separate untrusted pull-request caches from protected release caches.
- Grant write permission only to trusted workflows; give read-only access where possible.
- Include platform and meaningful build inputs in cache scope; avoid broad keys that cross incompatible builds.
- Define fallback behavior when the cache service is unavailable: build without cache if safe, but alert on latency or repeated import/export failures.
- Keep pipeline orchestration in M02; this unit defines the cache design and evidence expected from it.

A cache is an optimization, not a required source of truth. Release correctness must not depend on a cache being present. The image should still be buildable from declared, verified inputs, even if slower.

### Cache poisoning and shared-cache trust boundaries

A cache-poisoning scenario occurs when an untrusted branch can write cache records later consumed by a protected release build. Even if the builder checks cache metadata, teams should not assume cache entries are trusted artifacts or that every external input is represented. A safe baseline:

1. Separate cache references/namespaces by trust level and service.
2. Prevent forks/untrusted branches from writing release cache.
3. Restrict registry/object-store credentials to the minimum read/write scope.
4. Treat cache export as a privileged action; export after relevant checks succeed.
5. Keep package hashes/signature verification enabled; do not accept a cache hit as proof of integrity.
6. Audit cache writers, cache reference changes, and builder configuration.
7. Test a cache-miss fallback so cache loss does not force unsafe shortcuts.

### Remote/shared builder security model

Before adopting a remote or shared builder, answer: who authenticates to it; who can submit builds; who can read build logs and contexts; what network destinations can build steps access; where secrets are mounted; whether tenants share worker state; who patches the daemon/buildkitd; who can export cache; and who owns incident response. Build contexts can contain proprietary source and accidental secrets. A remote builder is not automatically safer because it is centrally managed; centralization can increase blast radius if authorization or isolation is weak.

### Monorepo build graph

```text
shared/python-base ───────┬────────> service/api deps ──> api image
                          ├────────> service/etl deps ──> etl image
                          └────────> service/airflow deps -> worker image

api source change ───────────────────────────────────────> api image
etl source change ────────────────────────────────> etl image
shared base change ───────> api + etl + worker dependent stages
```

A change to API source should not invalidate ETL dependency installation unless the build graph intentionally couples them. A change to a shared base or shared lock can correctly invalidate multiple services. Design separate contexts and stages around real dependency boundaries; do not split stages merely to maximize cache hits if that makes dependency ownership unclear.

### Multi-platform builds: QEMU versus native nodes

QEMU emulation can make cross-architecture builds possible on a single host, but CPU-heavy compilation may behave differently or be slower under emulation. Native architecture nodes can improve execution fidelity and performance but add capacity, orchestration, and cache-coordination complexity. There is no universal speed ratio. Benchmark the actual workload separately per target platform, record whether compilation ran natively or under emulation, and avoid comparing an arm64 emulated build to an amd64 native build as though the only changed variable were caching.

### Build-time SLO and regression guard

Example policy, **all numbers below are `[ILLUSTRATIVE]`, not measured**:

- **Build class:** single-platform `linux/amd64` Python ETL image, fixed source/lockfile fixture, designated runner size.
- **SLI:** wall-clock duration from build command start to successful image availability, measured per completed build; failed builds are separately counted, not silently dropped.
- **SLO:** p95 duration below **[ILLUSTRATIVE: 8 minutes]** over a rolling **[ILLUSTRATIVE: 7-day]** window, with at least **[ILLUSTRATIVE: 30]** eligible builds.
- **Exclusions:** planned base-image/toolchain migration and declared registry outage may be tagged separately, but must remain visible in incident reporting.
- **Guard:** compare current benchmark median/p95 to a stable baseline under the same fixture and platform; fail or warn if a pre-agreed regression threshold is exceeded. Set the threshold from baseline variance, not a guessed universal percentage.
- **Action:** on regression, preserve logs and cache state, inspect context size, cache import/export, package download time, builder resource pressure, and dependency changes before changing cache policy.

A regression guard should not reward unsafe behavior such as skipping tests, disabling package verification, or consuming an untrusted cache. If sample count is too small, report “insufficient data” rather than a false green.

### Cache cleanup, GC, and disk pressure

Inspect before pruning:

```bash
docker system df
docker buildx du
docker buildx ls
docker buildx inspect
```

**[VERIFY]** `docker buildx du` availability and output depend on buildx version/builder. Consult the installed buildx command reference. These commands are inspection-first; retain their output as evidence before cleanup.

`docker buildx prune` removes build cache for a selected builder. **⚠ DESTRUCTIVE:** it can remove useful cached build results and increase future build latency. First inspect the target builder and cache usage. Use `docker buildx prune --help` and current documentation to confirm supported scoping and confirmation options. Do not paste a broad prune command into a shared runner without understanding its impact. A safer practice is to test on a disposable lab builder or use the narrowest supported scope, then verify what was removed.

BuildKit garbage collection can be configured through `buildkitd.toml` in supported deployments. **[VERIFY] [VERSION-SENSITIVE]** GC keys, policies, units, and configuration paths depend on BuildKit version and how the builder is managed. Use the official BuildKit configuration documentation. Do not assume a config file mounted into one builder controls every buildx driver.

Cache retention is a capacity policy: more retention can improve warm builds but consumes disk; less retention reduces disk pressure but increases cold rebuilds. Track disk headroom and rebuild latency together.

### Failure scenario: cache disappears or becomes unusable

| Symptom | Hypothesis | Test | Likely root cause | Fix | Prevention |
|---|---|---|---|---|---|
| Sudden increase in build duration | Cache export/import failed or builder was replaced | Inspect build logs, builder identity, backend permissions | Expired credentials or ephemeral runner with no restored cache | Build safely without cache; restore permissions and export path | Alert on cache transfer errors and builder changes |
| Cache import says missing/incompatible | Reference or cache format/driver changed | Inspect exact `--cache-from` reference and buildx version | Wrong cache scope or unsupported backend combination | Correct reference or rebuild cache under supported configuration | Versioned cache contract and smoke test |
| Disk pressure on builder | Cache retention too broad | Inspect disk/cache usage before pruning | Unbounded retained records | Apply documented GC policy or scoped prune | Capacity thresholds and retention owner |
| Release build consumes untrusted cache | Trust namespaces overlap | Audit writer permissions and cache reference | Fork/branch can publish shared cache | Separate namespaces; revoke unauthorized writer | Policy-as-code and periodic permission review |
| Build fails only on remote builder | Context, network, secret, or architecture mismatch | Compare builder details, platform, context transfer and logs | Remote environment lacks input or has restricted egress | Provide declared input or correct access policy | Remote builder contract and canary test |

**Runbook:** alert → preserve logs and current cache metadata → inspect builder, credentials, cache import/export references, context transfer, and disk pressure → use a safe uncached fallback if policy permits → restore cache service or builder → compare performance and trust policy after recovery. Do not delete cache or logs before collecting evidence. For backup/disaster-recovery design, see M13; this unit covers cache recovery, not full platform DR.

### WSL2 and native Linux considerations

On WSL2, building from `/mnt/c/...` may have different filesystem performance from building inside the Linux filesystem. Docker Desktop integration and native Docker Engine also differ in daemon placement, resource limits, and builder lifecycle. Record where the context lives, which daemon/builder is active, and target platform. For timing, avoid comparing runs from different filesystem locations or changing Docker Desktop CPU/RAM limits mid-experiment. Keep at least enough disk headroom for base layers, package downloads, two image outputs, and logs; inspect before repeated builds.

## 4.7 SRE lens

### Metrics with actionable definitions

| Indicator | Definition / denominator | Window | Decision it supports |
|---|---|---|---|
| Build duration p50/p95 | Wall time from command start to image available, grouped by build class; report successful and failed attempts separately | Rolling window with stated minimum sample count | Detect slow feedback and regressions |
| Build success rate | Successful eligible builds divided by all eligible build attempts | Daily/weekly | Detect reliability degradation |
| Cache import success rate | Successful cache imports divided by builds that attempted import | Per backend and trust class | Detect cache service/credential issues |
| Cache export success rate | Successful exports divided by builds that attempted export | Per backend | Detect loss of future reuse |
| Context size | Measured context estimate/transfer where observable, plus source inventory | Per build or sampled | Detect accidental data/context growth |
| Cache storage pressure | Used cache bytes and remaining disk capacity, measured for each builder | Frequent enough to prevent exhaustion | Trigger GC review before failures |
| Patch delivery lead time | Time from approved dependency/base update to production rollout | Monthly/rolling | Ensure cache optimization does not freeze dependencies |

Do not use a cache-hit ratio unless the builder exposes a reliable numerator and denominator. If inferred from logs, define the parsing method and version assumptions.

### Failure modes and blast radius

- **Local developer cache loss:** one developer experiences slower builds.
- **Shared cache outage:** many jobs become slow; correctness should remain possible from declared inputs.
- **Shared cache poisoning:** protected releases may consume influenced build results; this is a trust-boundary incident.
- **Builder disk exhaustion:** jobs fail across every workload assigned to that builder.
- **Over-broad cache keys:** unrelated changes trigger large rebuilds, increasing queueing and cost.
- **Overly permissive cache sharing:** private source or artifacts may cross tenant boundaries.
- **Aggressive pruning:** cold-build load spikes can worsen an incident.

### Runbook snippet

1. **Alert:** p95 build duration breaches SLO, cache import/export errors rise, or builder disk headroom falls below the local policy threshold.
2. **Triage:** segment by builder, service, platform, cache backend, branch trust class, and success/failure. Preserve representative logs.
3. **Mitigation:** if safe, continue with cache disabled or a known trusted cache; do not bypass integrity checks or grant broad credentials.
4. **Diagnosis:** check builder status, cache references, credentials, network/registry latency, context size, dependency changes, CPU/RAM/disk, and GC events.
5. **Follow-up:** repair permissions/configuration, rerun the controlled benchmark, record recovery duration, and update the capacity or trust policy.

Cost/capacity notes: remote cache reduces repeated computation only if transfer and lookup costs are lower than recomputation. Large cache exports can increase registry storage and network traffic. Measure transfer time and bytes where available; do not optimize only for the number of `CACHED` lines.

## 4.8 Security lens

| Threat / trust boundary | Control | What it does not solve |
|---|---|---|
| Cache poisoning by untrusted branch | Separate cache references by trust class; prevent untrusted writes to release cache | Does not prove cached dependencies are safe |
| Unauthorized cache writes | Least-privilege registry/object-store permissions and audit logs | Does not prevent a compromised authorized writer |
| Cross-tenant cache exposure | Separate builders or namespaces; narrow access; review cache contents and context | Does not eliminate all side channels or configuration errors |
| Secret copied into context | Narrow context, `.dockerignore`, secret scanning/review | `.dockerignore` is not a complete secrets-management system |
| Secret persisted in image layer | Use supported secret mounts; avoid `ARG`/`ENV` for credentials | A malicious build command can still exfiltrate a mounted secret |
| Remote builder compromise | Authenticated endpoint, authorization, TLS as appropriate, patching, tenant isolation, network policy | Centralized builder can still be a high-blast-radius dependency |
| Stale cache output | Pin and verify inputs; periodically test clean builds | Cache hits do not prove freshness or reproducibility |
| False confidence from successful cached build | Independent tests/scans and provenance policy | Tests and scans are not complete proofs of safety |

STRIDE can help organize threat analysis: spoofing builder identity, tampering with cache outputs, repudiating cache changes, information disclosure through contexts/logs, denial of service via cache or disk exhaustion, and elevation of privilege through overbroad builder credentials. M12 covers deeper supply-chain signing/provenance controls; this unit does not claim to eliminate supply-chain risk.

Useful checks include:

```bash
docker buildx ls
docker buildx inspect
git status --short
find . -maxdepth 2 -type f \( -name '.env' -o -name '*.pem' -o -name '*.key' \) -print
```

**EXPECTED / REPRESENTATIVE:** builder information, working-tree state, and a list of matching file paths if any. This file-name scan is only a narrow hygiene check; it does not detect every secret or inspect file contents. Do not print secret values into logs.

## 4.9 Production checklist

- [ ] Dockerfile copies dependency manifests before frequently changing source where appropriate; verify order in the file.
- [ ] `.dockerignore` excludes irrelevant, large, generated, and sensitive paths; test that required build inputs remain included.
- [ ] Context size/file inventory is recorded for the representative build class.
- [ ] Build inputs and target platform are explicit; hidden network downloads are pinned and integrity-checked.
- [ ] Cache mounts are used only where appropriate; their mutable state and lifecycle are documented.
- [ ] Builder driver, BuildKit/buildx versions, platform, and resource limits are recorded.
- [ ] Cache backend, cache reference, export/import mode, retention, and trust namespace are documented.
- [ ] Untrusted branches cannot write cache consumed by protected release builds.
- [ ] Cache export/import failure has a tested fallback that does not bypass integrity checks.
- [ ] Benchmark harness reports N, median, p95, units, revision, tool baseline, cache state, and notes.
- [ ] Cold, warm, and partial-change scenarios are precisely defined and comparable.
- [ ] Build-time SLO has a workload class, denominator, time window, minimum sample count, exclusions, and action.
- [ ] Regression guard compares equivalent fixtures and does not silently drop failed builds.
- [ ] Disk/cache usage is inspected before cleanup; GC policy is owned and version-checked.
- [ ] Remote builders have documented authentication, authorization, network, isolation, secret, and ownership controls.
- [ ] Multi-platform benchmarks separate native and emulated execution.
- [ ] Evidence and logs are retained without secrets; destructive cleanup is scoped and verified.
- [ ] Cross-module responsibilities are clear: M02 CI/CD, M03 Kubernetes, M08 GitOps, M09 secrets, M12 supply-chain security, M13 backup/DR.

## 4.10 Hands-on lab set

All labs are local/free and designed for the stated laptop. Initial image and dependency pulls require network and may consume hundreds of megabytes. Use a dedicated directory under `$HOME`, preferably within the WSL2 Linux filesystem rather than `/mnt/c` for performance comparisons. Do not run global prune commands as routine cleanup.

### Lab 1 — Cache hits, misses, and dependency-first ordering

**Estimated time:** 45–75 minutes  
**Goal:** observe cache behavior and prove how changing source versus a dependency manifest affects reuse.  
**Prerequisites:** Docker and buildx installed; shell; network for initial base pull.

**Steps**

1. Create a dedicated directory and a small FastAPI-style service.
2. Build once with source copied before dependency installation, then rebuild after a source-only change.
3. Refactor to copy `requirements.txt` first, install dependencies, then copy source.
4. Repeat the source-only change and compare progress logs.
5. Change the manifest intentionally and observe the dependency-install operation.

```bash
# File: lab-01.sh
set -euo pipefail
LAB="$HOME/unit04-lab01"
mkdir -p "$LAB/service"
cd "$LAB"
cat > requirements.txt <<'EOF'
fastapi
uvicorn
EOF
cat > service/main.py <<'EOF'
from fastapi import FastAPI
app = FastAPI()
@app.get("/health")
def health():
    return {"status": "ok"}
EOF
cat > Dockerfile.bad <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN python -m pip install -r requirements.txt
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF
cat > Dockerfile.good <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY service/ ./service/
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF
docker build --progress=plain -f Dockerfile.bad -t unit04-lab1-bad:local .
printf '\n# source-only comment\n' >> service/main.py
docker build --progress=plain -f Dockerfile.bad -t unit04-lab1-bad:local .
docker build --progress=plain -f Dockerfile.good -t unit04-lab1-good:local .
printf '\n# second source-only change\n' >> service/main.py
docker build --progress=plain -f Dockerfile.good -t unit04-lab1-good:local .
```

**EXPECTED / REPRESENTATIVE:** the bad ordering can rerun installation after a source/context change; the good ordering may reuse the install step if `requirements.txt` is unchanged. Because `COPY . .` also copies Dockerfiles and other context files, the bad example is especially sensitive to context changes. Actual messages vary.

**Interpretation:** a cache hit is evidence of reuse for a particular operation, not a correctness/security proof.  
**Evidence:** save both build logs and a short comparison table under `evidence/unit-04/lab-01/`.  
**Success criteria:** explain which operation changed, why, and what remained cache-eligible.  
**Cleanup:** inspect tags first with `docker image inspect unit04-lab1-bad:local unit04-lab1-good:local`; remove only these lab tags if not needed. Verify `docker ps -a --filter name=unit04-lab1` returns no lab containers. Preserve evidence.  
**Stretch:** add `.dockerignore`, measure context size, and repeat the experiment.

### Lab 2 — Optimize context and use a cache mount

**Estimated time:** 60–90 minutes  
**Goal:** compare manifest-first ordering, `.dockerignore`, and a pip cache mount.  
**Prerequisites:** Lab 1; disk space for dependencies.

**Steps**

1. Add `.dockerignore` with `.git`, `.venv`, `__pycache__`, local datasets, build output, and secret file patterns appropriate to your project.
2. Measure directory size and file count; record build progress context-transfer observations.
3. Add `RUN --mount=type=cache,target=/root/.cache/pip` to the dependency install operation.
4. Build twice with unchanged inputs and record logs and elapsed times. Do not call the first build “cold” unless the relevant cache state is controlled.
5. Confirm the cache mount's contents are not copied into the runtime image as a normal layer.

```bash
# File: lab-02-measure.sh
set -euo pipefail
LAB="$HOME/unit04-lab01"
cd "$LAB"
mkdir -p evidence/unit-04/lab-02
du -sh . | tee evidence/unit-04/lab-02/directory-size.txt
find . -type f | wc -l | tee evidence/unit-04/lab-02/file-count.txt
/usr/bin/time -f 'elapsed_seconds=%e' \
  docker build --progress=plain -f Dockerfile.good \
  -t unit04-lab2:local . \
  2>&1 | tee evidence/unit-04/lab-02/build.log
```

**EXPECTED / REPRESENTATIVE:** directory size, file count, and a build log with a time measurement. The shell pipeline may affect timing/error propagation depending on shell and `time` placement; verify the command's exit status and preserve the build log. If precise timing is required, use Lab 3's Python harness.  
**Success criteria:** report actual measured context proxy and build time, explain why directory size is only a proxy, and document cache mount availability.  
**Cleanup:** preserve evidence; inspect the lab tag before removing it. Verify no lab containers or temporary context directories remain.  
**Stretch:** compare with and without the mount after a controlled builder restart, documenting that a new builder may not retain cache-mount state.

### Lab 3 — Benchmark harness: cold, warm, partial change

**Estimated time:** 90–150 minutes  
**Goal:** run repeated measurements with median and p95 and produce an auditable report.  
**Prerequisites:** Python 3.10+ (standard library only), Docker, buildx, network for base/dependency acquisition. The harness builds a small realistic dependency-free HTTP service to keep resource use bounded; adapt it to the locked data-service image only after validating the harness.

#### Experiment definitions

- **Cold:** before each scored trial, create a disposable buildx builder and remove it afterward, so its instruction cache is not reused. This is an approximation: base layers, host page cache, registry caches, and external network state may remain warm. The harness does not run global prune.
- **Warm:** build the same fixture twice on one disposable builder; the first run warms that builder, and the second is the scored warm run.
- **Partial-change:** build baseline on a disposable builder, then change only a source file in a temporary fixture copy and build again while the dependency manifest is unchanged. The temporary fixture is generated outside the learner's working tree.

The harness uses N repeats per scenario. Default N=3 is intentionally small for a laptop; use a larger N for decision-grade comparisons. It creates temporary directories and a uniquely named builder, captures logs, records revision/tool baseline, and removes the builder/temp files on exit. It does not delete global cache or modify your project. The disposable builder may download its own BuildKit image and base image, increasing network/disk usage.

```python
# File: benchmark_build_cache.py
from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

DOCKERFILE = """\
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY service/ ./service/
CMD ["python", "-m", "service"]
"""

REQUIREMENTS = "# Deliberately empty: the harness isolates build-cache mechanics.\n"
APP = """\
from http.server import BaseHTTPRequestHandler, HTTPServer
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'{"status":"ok"}\\n'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
"""
MAIN = "from service.app import *\n"

def run(command: list[str], *, log_path: Path | None = None,
        check: bool = True, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    started = time.monotonic()
    result = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False, timeout=timeout,
        env={**os.environ, "BUILDKIT_PROGRESS": "plain"},
    )
    elapsed = time.monotonic() - started
    if log_path:
        log_path.write_text(result.stdout, encoding="utf-8")
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}), elapsed={elapsed:.3f}s: "
            f"{' '.join(command)}\nLog:\n{result.stdout[-4000:]}"
        )
    return subprocess.CompletedProcess(
        result.args, result.returncode,
        result.stdout + f"\nHARNESS_ELAPSED_SECONDS={elapsed:.6f}\n",
        result.stderr,
    )

def make_fixture(root: Path) -> None:
    (root / "service").mkdir(parents=True)
    (root / "requirements.txt").write_text(REQUIREMENTS, encoding="utf-8")
    (root / "service" / "__init__.py").write_text("", encoding="utf-8")
    (root / "service" / "app.py").write_text(APP, encoding="utf-8")
    (root / "service" / "__main__.py").write_text(MAIN, encoding="utf-8")
    (root / "Dockerfile").write_text(DOCKERFILE, encoding="utf-8")
    (root / ".dockerignore").write_text(
        ".git\\n.venv/\\n__pycache__/\\n*.py[cod]\\nevidence/\\n",
        encoding="utf-8",
    )

def build(builder: str, context: Path, tag: str, log: Path) -> float:
    started = time.monotonic()
    result = run([
        "docker", "buildx", "build", "--builder", builder,
        "--progress=plain", "--load", "--tag", tag, str(context),
    ], log_path=log, timeout=900)
    # Use a monotonic timer around the command rather than parsing human output.
    # The helper's elapsed value is also embedded in its log for traceability.
    marker = "HARNESS_ELAPSED_SECONDS="
    value = next((line.split("=", 1)[1] for line in result.stdout.splitlines()
                  if line.startswith(marker)), None)
    if value is None:
        return time.monotonic() - started
    return float(value)

def percentile_nearest_rank(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("No measurements")
    if not 0 < percentile <= 100:
        raise ValueError("percentile must be in (0, 100]")
    ordered = sorted(values)
    index = max(0, int((percentile / 100.0) * len(ordered) + 0.999999) - 1)
    return ordered[min(index, len(ordered) - 1)]

def summarize(name: str, values: list[float], n: int) -> dict[str, Any]:
    return {
        "scenario": name,
        "n": n,
        "median_seconds": statistics.median(values),
        "p95_seconds": percentile_nearest_rank(values, 95),
        "samples_seconds": [round(v, 3) for v in values],
    }

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Local-only Docker build cache benchmark; outputs measured local results."
    )
    parser.add_argument("--n", type=int, default=3, help="repeats per scenario (default: 3)")
    parser.add_argument("--output", type=Path, default=Path("benchmark-results"),
                        help="directory for logs and JSON (default: benchmark-results)")
    args = parser.parse_args()
    if args.n < 2 or args.n > 10:
        parser.error("--n must be between 2 and 10 for this laptop-safe harness")
    if shutil.which("docker") is None:
        parser.error("docker CLI not found")
    args.output.mkdir(parents=True, exist_ok=True)
    builder = "unit04-bench-" + uuid.uuid4().hex[:8]
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="unit04-bench-") as tmp:
        root = Path(tmp)
        fixture = root / "fixture"
        make_fixture(fixture)
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], text=True, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, check=False,
        )
        metadata = {
            "revision": revision.stdout.strip() if revision.returncode == 0 else "LOCAL-GENERATED-FIXTURE",
            "python": sys.version,
            "platform": sys.platform,
            "docker_version": run(["docker", "version", "--format", "{{.Client.Version}}"]).stdout.strip(),
            "buildx_version": run(["docker", "buildx", "version"]).stdout.strip(),
            "n": args.n,
            "builder": builder,
            "percentile_convention": "nearest-rank p95",
            "notes": "Temporary generated fixture; cold is builder-cache-cold, not a fully cold host/network.",
        }
        try:
            run(["docker", "buildx", "create", "--name", builder,
                 "--driver", "docker-container", "--use"], timeout=120)
            run(["docker", "buildx", "inspect", "--builder", builder, "--bootstrap"],
                timeout=300, log_path=args.output / "builder-inspect.log")
            cold_values: list[float] = []
            for i in range(args.n):
                # A new disposable builder per trial approximates an instruction-cache-cold run.
                trial_builder = f"{builder}-cold-{i}"
                run(["docker", "buildx", "create", "--name", trial_builder,
                     "--driver", "docker-container"], timeout=120)
                try:
                    cold_values.append(build(
                        trial_builder, fixture, f"unit04-bench-cold-{i}:local",
                        args.output / f"cold-{i}.log",
                    ))
                finally:
                    run(["docker", "buildx", "rm", trial_builder], check=False, timeout=120)
            results.append(summarize("cold-new-builder", cold_values, args.n))

            warm_values: list[float] = []
            for i in range(args.n):
                build(builder, fixture, f"unit04-bench-warm-prime-{i}:local",
                      args.output / f"warm-prime-{i}.log")
                warm_values.append(build(
                    builder, fixture, f"unit04-bench-warm-{i}:local",
                    args.output / f"warm-{i}.log",
                ))
            results.append(summarize("warm-same-builder", warm_values, args.n))

            partial_values: list[float] = []
            for i in range(args.n):
                build(builder, fixture, f"unit04-bench-partial-prime-{i}:local",
                      args.output / f"partial-prime-{i}.log")
                changed = root / f"partial-{i}"
                shutil.copytree(fixture, changed)
                with (changed / "service" / "app.py").open("a", encoding="utf-8") as f:
                    f.write(f"\\n# controlled partial change {i}\\n")
                partial_values.append(build(
                    builder, changed, f"unit04-bench-partial-{i}:local",
                    args.output / f"partial-{i}.log",
                ))
            results.append(summarize("partial-source-change", partial_values, args.n))
            metadata["results"] = results
            (args.output / "summary.json").write_text(
                json.dumps(metadata, indent=2), encoding="utf-8"
            )
            print(f"{'scenario':<26} {'N':>3} {'median (s)':>13} {'p95 (s)':>12}")
            for row in results:
                print(f"{row['scenario']:<26} {row['n']:>3} "
                      f"{row['median_seconds']:>13.3f} {row['p95_seconds']:>12.3f}")
            print(f"Measured results written to: {args.output.resolve()}")
            print("These are measurements of this local environment, not universal performance claims.")
        finally:
            # Remove the disposable main builder; per-trial builders are removed above.
            run(["docker", "buildx", "rm", builder], check=False, timeout=120)
            # Images are tagged with the unit04-bench prefix. They are left for inspection by default.
            # Remove only those exact tags after reviewing `docker image ls`.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Important harness notes and limits**

- The harness is complete Python code and uses the standard library only. It creates a generated fixture in a temporary directory and does not alter the learner's working tree.
- **[VERIFY]** `docker buildx create`, `--driver docker-container`, `--builder`, and `--load` behavior must be checked against installed buildx/daemon support.
- The cold scenario creates a new builder for each trial; this makes its BuildKit instruction cache fresh, but it does not clear host page cache, registry state, or every layer stored by the Docker daemon. Treat it as **builder-cache-cold**, not a universally cold machine.
- The harness leaves tagged images for inspection; this avoids destroying evidence or deleting unrelated images. Review them and remove only exact `unit04-bench-*` tags when done.
- p95 uses the nearest-rank convention. With a small N, p95 often equals the largest sample; increase N before using results for an SLO decision.
- The fixture is intentionally dependency-light to bound resource use. Repeat the protocol with a real locked data-service image before making production decisions.
- The `time.monotonic()` clock measures elapsed wall time. CPU contention, network and registry latency, package mirror state, image pulls, builder bootstrap, page cache, WSL2 filesystem location, and other processes can dominate results. Save raw logs and metadata.

Invocation:

```bash
python3 benchmark_build_cache.py --n 3 --output evidence/unit-04/benchmark
```

**EXPECTED / REPRESENTATIVE OUTPUT SHAPE — `[ILLUSTRATIVE]`, NOT MEASURED:**

```text
scenario                     N    median (s)      p95 (s)
cold-new-builder             3        [VALUE]        [VALUE]
warm-same-builder            3        [VALUE]        [VALUE]
partial-source-change        3        [VALUE]        [VALUE]
Measured results written to: /path/to/evidence/unit-04/benchmark
These are measurements of this local environment, not universal performance claims.
```

The literal bracketed values above are placeholders for the table shape; actual execution prints numeric measurements. Do not substitute illustrative numbers into the report. If the harness fails, preserve the error and logs, fix the environment or command only after checking the cause, and rerun.

**Cleanup:** inspect `docker buildx ls` and `docker image ls --filter reference='unit04-bench-*'`. The script removes its disposable builders but leaves tagged images for inspection. **⚠ DESTRUCTIVE:** after saving the report, remove only the exact tags created by the harness, after reviewing each image reference. Do not run global prune. Verify no builder names beginning `unit04-bench-` remain and that the evidence directory still exists.  
**Success criteria:** report N, median, p95, platform, versions, revision/fixture identity, cache definitions, and at least three error sources that limit interpretation.  
**Stretch:** rerun with a real hash-locked FastAPI/pandas service and compare dependency-first ordering, but keep it within disk limits.

### Lab 4 — Diagnose a poor cache key or monorepo invalidation

**Estimated time:** 60–90 minutes  
**Goal:** distinguish legitimate invalidation from an overly broad build graph.  
**Prerequisites:** Labs 1–3 or an equivalent monorepo fixture.

**Steps**

1. Create `api/`, `etl/`, and `shared/` source directories in a disposable fixture.
2. Build separate API and ETL targets with dependency manifests copied before source.
3. Change only `api/main.py`; inspect whether ETL dependency installation runs again.
4. Introduce an intentionally broad `COPY . .` in the ETL stage and repeat.
5. Restore narrow contexts and document the invalidation graph.

**EXPECTED / REPRESENTATIVE:** API output should be affected by API source; ETL dependency installation should remain cache-eligible when ETL manifest and shared dependencies are unchanged. A broad shared context may invalidate unrelated operations. Exact messages depend on the Dockerfile graph and builder.

**Evidence:** cache-invalidation matrix, logs, graph diagram, and defended explanation.  
**Success criteria:** explain which invalidations are necessary due to dependency edges and which are accidental coupling.  
**Cleanup:** remove only the dedicated temporary fixture and lab-tagged images after inspecting them; verify no lab containers remain.  
**Stretch:** model a shared base change and explain why it should invalidate dependent services.

### Lab 5 — Shared-cache trust incident and SLO guard

**Estimated time:** 60–90 minutes  
**Goal:** respond to a hypothetical cache poisoning or cache-loss incident without unsafe shortcuts.  
**Prerequisites:** no registry or paid service required; use a written design or local namespaces.

**Steps**

1. Draw trusted release, internal branch, and untrusted fork trust classes.
2. Assign read/write permissions to each cache namespace. Ensure an untrusted class cannot write the release cache.
3. Simulate cache loss by building with no imported cache in a disposable environment; do not prune a shared builder.
4. Define a build-time SLI/SLO using a fixed fixture and an illustrative threshold marked `[ILLUSTRATIVE]`.
5. Write a regression guard that compares repeated measurements only when the baseline fixture, platform, builder class, and cache state match.
6. Write a runbook covering preservation of logs, builder inspection, credentials, import/export, disk pressure, and safe fallback.

**EXPECTED / REPRESENTATIVE:** a trust matrix, SLO definition, and runbook. No actual poisoning or credential attack is required. If no second cache backend is available, state that cross-backend failover was designed but not measured.  
**Evidence:** `trust-matrix.md`, `build-slo.md`, `cache-loss-runbook.md`.  
**Success criteria:** untrusted writers are separated; cache loss does not require bypassing integrity checks; SLO denominator/window/exclusions are explicit.  
**Cleanup:** no resources should be created. Verify no lab containers/builders remain from earlier labs.  
**Stretch:** implement permission checks as policy-as-code in M02, and provenance/signing verification under M12.

## 4.11 Self-check questions

1. **What does a cache hit tell you?**  
   It tells you the builder reused an eligible prior result under its cache rules. It does not prove correctness, freshness, security, or complete input capture.

2. **Why does manifest-first ordering help?**  
   It separates relatively stable dependency inputs from frequently changing source, allowing the dependency step to remain cache-eligible when source changes.

3. **Is a cache mount a runtime image layer?**  
   Not automatically. It is mutable build-time state mounted into an operation; files written to ordinary image paths are different.

4. **Why is `--no-cache` not a complete cold benchmark?**  
   It does not control all host, registry, network, page-cache, or package-manager state, and may not disable every external cache mechanism.

5. **Which cache backend is always best for ephemeral runners?**  
   None. Compare transfer cost, portability, storage, trust boundaries, supported features, and failure behavior for the actual environment.

6. **Why separate untrusted branch cache from release cache?**  
   To prevent untrusted writers from influencing cache consumed by protected builds. Separation still does not make all cached content inherently safe.

7. **What does p95 mean in the harness?**  
   It is the nearest-rank 95th percentile of recorded elapsed durations. With small N, it often equals the maximum observed sample and should be treated cautiously.

8. **When can stages run concurrently?**  
   When the build graph has no dependency edge requiring one stage's output before the other and the builder has resources to schedule both.

9. **What should you do before pruning cache on a shared builder?**  
   Inspect builder/cache usage and scope, preserve evidence, understand who depends on it, and use the narrowest verified cleanup action.

10. **Why can a cache hit be a security risk?**  
    If trust boundaries and cache writers are poorly controlled, a protected build may consume results influenced by an untrusted actor. Use least privilege and separate namespaces.

## 4.12 Evidence artifacts

Suggested evidence directory inside the learner's working area:

```text
evidence/unit-04/
├── baseline/
│   ├── docker-version.txt
│   ├── buildx-version.txt
│   ├── builder-list.txt
│   ├── builder-inspect.txt
│   ├── machine-notes.md
│   └── source-revision.txt
├── lab-01/
│   ├── bad-first-build.log
│   ├── bad-source-change.log
│   ├── good-first-build.log
│   ├── good-source-change.log
│   └── invalidation-analysis.md
├── lab-02/
│   ├── directory-size.txt
│   ├── file-count.txt
│   ├── before-after-context.md
│   └── cache-mount-build.log
├── benchmark/
│   ├── summary.json
│   ├── builder-inspect.log
│   ├── cold-*.log
│   ├── warm-*.log
│   ├── partial-*.log
│   └── benchmark-report.md
├── lab-04/
│   ├── graph.mmd
│   ├── cache-logs/
│   └── diagnosis.md
├── lab-05/
│   ├── trust-matrix.md
│   ├── build-slo.md
│   └── cache-loss-runbook.md
└── decision-record.md
```

Record the commit or generated-fixture identity, Docker/buildx versions, builder driver, target platform, resource limits, cache state, N, raw durations, median/p95, and measurement caveats. Keep logs free of secrets and redact private registry credentials. Retain failures: a failed cache import is evidence, not clutter to delete before diagnosis.

## 4.13 Common interview and design-review questions

1. **How do you make a Python image build faster without compromising dependency integrity?**  
   **Model answer:** I first measure the workload and inspect progress logs. I copy a lock/manifest before source, use a reviewed dependency lock, add `.dockerignore`, and consider a package-manager cache mount. I preserve hash/signature checks, compare cold/warm/partial-change builds, and record the toolchain/platform. I do not claim the optimization is effective until measured, and I do not equate cache hits with integrity.

2. **When would you use a registry cache with `mode=max` instead of inline or local cache?**  
   **Model answer:** For ephemeral runners or expensive multi-stage builds, a registry cache can be portable across workers, and retaining intermediate stage records may improve reuse. It costs storage and transfer, needs permissions/retention policy, and increases the importance of cache namespace trust. Exact mode/export support is version-sensitive; I verify it on the selected builder. Local cache is simpler for persistent hosts; inline may be adequate for simpler image-coupled workflows.

3. **A cache import failure increases p95 build time. What is your response?**  
   **Model answer:** I preserve logs and classify the impact by builder/backend/trust class. I inspect builder status, credentials, cache reference, export/import mode, network/registry latency, disk pressure, and recent version changes. If safe, builds continue from declared inputs without cache; I do not disable package integrity checks. After repair, I rerun a controlled benchmark and update the runbook.

4. **How do you prevent cache poisoning in CI?**  
   **Model answer:** Separate trusted release caches from untrusted branch/fork caches, restrict cache writers, use least-privilege credentials, audit references, and only export protected cache after the required checks. Treat cache as an optimization rather than a trusted artifact. Broader artifact signing/provenance controls and policy belong in the supply-chain security module, but the cache trust boundary must be enforced here.

5. **How would you set a build-time SLO for a monorepo with several image types?**  
   **Model answer:** Define build classes by service, platform, runner, and cache state; measure wall time and failures with a stated denominator and sample threshold; use p95 over a rolling window; tag planned migrations/outages without hiding them; and set the target from observed baseline and delivery needs. A regression guard compares equivalent fixtures and should warn or fail only when sample size and variance support the decision. I also track cache storage and patch lead time so performance goals do not reward stale dependencies.

## 4.14 Sources and verification notes

Live documentation browsing was not performed for this draft. The following official references are starting points; check current headings and syntax for the installed versions before production use.

- Docker documentation, **Dockerfile reference** — `COPY`, `ARG`, `RUN`, build context, and `.dockerignore`: https://docs.docker.com/reference/dockerfile/
- Docker documentation, **Build overview** and **Cache optimization**: https://docs.docker.com/build/
- Docker documentation, **Cache optimization**: https://docs.docker.com/build/cache/optimize/
- Docker Buildx CLI reference, `build`, `create`, `inspect`, `ls`, `prune`, and related commands: https://docs.docker.com/reference/cli/docker/buildx/
- Docker documentation, **Cache backends**: https://docs.docker.com/build/cache/backends/
- Docker documentation, **Build drivers**: https://docs.docker.com/build/builders/drivers/
- BuildKit project documentation and configuration (`buildkitd.toml`): https://github.com/moby/buildkit
- OCI Image Specification for image/layer concepts: https://github.com/opencontainers/image-spec
- GitHub Actions cache documentation for the awareness-only `gha` backend context: https://docs.github.com/en/actions
- Docker documentation for build secrets and sensitive build inputs: https://docs.docker.com/build/building/secrets/
- Official Go image and Go module documentation if using the contrasting example: https://hub.docker.com/_/golang and https://go.dev/doc/

### Verification notes

- **[VERIFY] [VERSION-SENSITIVE]** BuildKit enablement/defaults and legacy builder availability: inspect Docker version and current Docker build docs.
- **[VERIFY] [VERSION-SENSITIVE]** `RUN --mount=type=cache`: check Dockerfile frontend, BuildKit version, and builder configuration.
- **[VERIFY] [VERSION-SENSITIVE]** buildx driver availability/capabilities and `--load`: check buildx reference and local `docker buildx inspect`.
- **[VERIFY] [VERSION-SENSITIVE]** `inline`, `registry`, `local`, `gha`, `s3` support and `mode=min|max`: check the official cache-backend documentation for the exact builder/version. Do not assume S3 is universally built in.
- **[VERIFY] [VERSION-SENSITIVE]** `docker buildx history` and other history commands: check current buildx CLI help and official reference.
- **[VERIFY] [VERSION-SENSITIVE]** `docker buildx du`, `prune` options, and GC behavior: check the installed CLI and builder-specific documentation before cleanup.
- **[VERIFY] [VERSION-SENSITIVE]** `buildkitd.toml` GC keys and configuration path: use official BuildKit config docs for the deployed version/driver.
- **[VERIFY]** Buildx cache exporter behavior and registry/inline cache persistence: run a disposable smoke test and verify the imported cache actually produces expected reuse.
- **[VERIFY]** Remote builder security/tenant isolation: inspect actual endpoint auth, RBAC, network controls, worker isolation, and ownership; driver name alone is insufficient.
- **[VERIFY]** Benchmark harness compatibility: run first with `--n 2`, inspect builder/image cleanup, and verify the chosen Docker daemon supports the docker-container driver.
- **[VERIFY]** Shell timing and pipeline exit behavior: use the Python harness for monotonic timing and preserve command failures rather than relying on a pipeline that hides nonzero exit status.

---

## Appendix A — Claim Register

| ID | Section | Claim | Source (document + section) | Confidence | Tag |
|---|---|---|---|---|---|
| A01 | 4.2 | Build cache can reuse prior eligible operation results. | Docker Build documentation, Cache optimization | High | none |
| A02 | 4.2 | Cache behavior depends on operation inputs and builder rules, not just the instruction text. | Dockerfile reference; BuildKit docs | High | none |
| A03 | 4.3 | `--no-cache` disables ordinary instruction-cache reuse for a build but does not make every environmental input cold. | Docker build CLI reference | High | [VERIFY] |
| A04 | 4.3 | BuildKit supports a build graph and can schedule independent work concurrently when dependencies/resources permit. | Docker Build overview; BuildKit docs | High | none |
| A05 | 4.4 | Manifest-first Dockerfile ordering can preserve dependency-install cache on source-only changes. | Docker Cache optimization docs | High | none |
| A06 | 4.4 | `.dockerignore` reduces files sent as build context and can exclude sensitive/unneeded files. | Docker build context docs | High | none |
| A07 | 4.4 | `RUN --mount=type=cache` is a BuildKit feature and is not automatically a runtime image layer. | Dockerfile reference, `RUN --mount`; BuildKit docs | High | [VERIFY]/[VERSION-SENSITIVE] |
| A08 | 4.4 | Cache-mount persistence depends on builder lifecycle/configuration. | BuildKit docs; cache mount docs | Medium | [VERIFY] |
| A09 | 4.4 | Context directory size is only a proxy for actual transmitted build context. | Docker build context docs | High | none |
| A10 | 4.5 | buildx supports multiple driver models, but exact capabilities vary. | Docker docs, Build drivers | High | [VERIFY]/[VERSION-SENSITIVE] |
| A11 | 4.5 | `docker` and `docker-container` drivers have different builder lifecycle/capability trade-offs. | Docker docs, Build drivers | High | [VERIFY] |
| A12 | 4.5 | `kubernetes` and `remote` drivers have additional cluster/endpoint trust boundaries. | Docker docs, Build drivers | High | [VERIFY] |
| A13 | 4.5 | Registry cache can be imported/exported for cross-runner reuse when supported/configured. | Docker docs, Cache backends | High | [VERIFY] |
| A14 | 4.5 | `mode=min` and `mode=max` have different cache-record retention trade-offs. | Docker docs, Cache backends | Medium | [VERIFY]/[VERSION-SENSITIVE] |
| A15 | 4.5 | Local cache uses a filesystem path and is not automatically shared across ephemeral hosts. | Docker docs, Cache backends | High | [VERIFY] |
| A16 | 4.5 | `gha` backend behavior is tied to GitHub Actions cache integration and access rules. | Docker docs, Cache backends; GitHub Actions cache docs | High | [VERIFY] |
| A17 | 4.5 | S3 cache support should not be assumed universal; verify exact implementation/version. | BuildKit docs and supported backend docs | Medium | [VERIFY] |
| A18 | 4.5 | `--progress=plain` makes build progress easier to retain in logs. | Docker build CLI reference | High | [VERIFY] |
| A19 | 4.5 | A single `--no-cache` build is not a controlled performance benchmark. | Methodological inference from Docker cache behavior | High | none |
| A20 | 4.6 | Ephemeral runners need an explicit strategy to import/export cache or accept cold builds. | Docker Cache backends docs; operational design inference | High | none |
| A21 | 4.6 | Cache writer permissions should be separated by trust class to reduce poisoning risk. | Docker build security guidance; CI-provider security docs | High | none |
| A22 | 4.6 | Remote builders require explicit authentication, authorization, network and tenant controls. | Docker Build drivers docs; BuildKit docs | High | [VERIFY] |
| A23 | 4.6 | Monorepo build graph boundaries affect invalidation scope. | Docker multi-stage/build graph docs | High | none |
| A24 | 4.6 | QEMU emulation and native builds have workload-dependent performance trade-offs. | Docker multi-platform build docs | High | [VERIFY] |
| A25 | 4.6 | p95 SLOs require a defined workload class, window, and denominator. | SRE measurement practice; lesson policy | High | none |
| A26 | 4.6 | Buildx prune removes cache and can increase later rebuild latency. | Docker buildx `prune` reference | High | [VERIFY] |
| A27 | 4.6 | BuildKit garbage collection configuration is version/deployment sensitive. | BuildKit configuration docs | High | [VERIFY]/[VERSION-SENSITIVE] |
| A28 | 4.7 | Cache import/export failures should be measured separately from overall build failures. | Operational measurement design | High | none |
| A29 | 4.8 | A cache hit does not prove freshness or security. | Docker cache docs; supply-chain threat reasoning | High | none |
| A30 | 4.8 | Narrow contexts and secret mounts reduce some secret exposure paths but do not eliminate all exfiltration risk. | Docker build secrets docs | High | [VERIFY] |
| A31 | 4.10 | Harness cold state is builder-cache-cold, not fully cold host/network state. | Harness design and benchmark methodology | High | none |
| A32 | 4.10 | Nearest-rank p95 with small N is coarse and often equals a high sample. | Statistical definition used by harness | High | none |
| A33 | 4.14 | Exact buildx history command availability depends on installed version. | Docker buildx CLI reference | Medium | [VERIFY] |
| A34 | 4.14 | Cache exporter compatibility and output requirements must be validated for the selected driver. | Docker docs, Cache backends and Build drivers | High | [VERIFY] |

## Appendix B — Audit Report

This is an AI self-audit, not an independent external review. The repository syllabus and live official docs were not directly inspected, and no lab was executed during authoring.

| Pass | Result (PASS/FIXED/OPEN) | Defect found | Remediation | Residual risk |
|---|---|---|---|---|
| 1 — Completeness | FIXED | Required L1–L4 topics, labs, harness, and appendices needed explicit mapping | Included sections 4.0–4.14 and Appendices A–E, five labs, benchmark harness | Repository-specific syllabus alignment not independently verified |
| 2 — Technical accuracy | OPEN | Buildx drivers, cache exporters, modes, history, and GC vary by version | Added verification markers and conservative backend examples | Human must verify current syntax and support |
| 3 — Executability | OPEN | Harness depends on Docker/buildx driver support and has not been run | Included full Python code, bounded N, temp fixture, builder cleanup, and troubleshooting notes | Syntax/runtime issues may remain until executed |
| 4 — Currency | FIXED | Defaults and feature support can change | Marked version-sensitive claims and named official docs | Live docs not checked |
| 5 — Security correctness | FIXED | Shared cache can be mistaken for trusted output | Added trust classes, least privilege, secret boundaries, and fallback policy | Org-specific permissions need review |
| 6 — Fabrication scan | PASS | Risk of presenting timings or output as observed | All sample timing values are placeholders; no measured improvement claimed | Verify generated report is based on raw logs |
| 7 — Pedagogical progression | FIXED | Advanced cache concepts could be introduced before basic cache behavior | Progresses from simple cache experiment to backends, measurement, security and SLOs | Some implementation detail deferred to other modules |
| 8 — Cross-consistency | FIXED | Labs/evidence/checklists needed alignment | Each lab defines evidence, success criteria, cleanup and stretch | File paths may need adapting to the learner's repository |
| 9 — Adversarial review | OPEN | Staff reviewer could challenge cold-build definition, cache trust assumptions, and incomplete execution validation | Explicitly bounded cold definition, trust policy, SLO denominator, and verification list added | Harness and backend examples need local smoke tests |
| 10 — Reproducibility/resource safety | OPEN | Fresh builders can still use host/network caches and consume disk; outputs left for inspection | Clearly qualified cold scenario, bounded N, temporary fixture, no global prune, exact-tag cleanup | Must inspect image/builder state on the actual laptop |

### Ten likely objections from a skeptical senior engineer

1. **“Your cold build is not truly cold.”** Correct: it is explicitly named `cold-new-builder` and described as builder-cache-cold; page cache, registry state, and base layers may remain warm.
2. **“The benchmark has only three runs.”** Default N=3 is a resource-conscious teaching default, not SLO-grade evidence. The harness allows N up to 10 and explains the need for more samples.
3. **“The harness may fail on my Docker setup.”** Driver support is marked for verification; run `--n 2` first and inspect builder logs.
4. **“You left image tags behind.”** Deliberate: they remain inspectable evidence. Cleanup is exact-tag and inspection-first.
5. **“Cache keys do not capture arbitrary network state.”** Explicitly discussed; pin/version/hash external artifacts instead of relying on cache.
6. **“`mode=max` syntax and meaning can vary.”** Marked `[VERIFY]`; current cache backend documentation must be consulted.
7. **“S3 is not universally available.”** The table explicitly says not to assume universal support and requires verifying the exact implementation.
8. **“A remote builder centralizes risk.”** The lesson discusses endpoint authentication, authorization, tenant isolation, network access, secret boundaries, and ownership.
9. **“A p95 target without baseline is meaningless.”** Numeric SLO targets are marked illustrative and must be set from observed baseline and variance.
10. **“The lesson says self-audit but did not run the code.”** The status and residual risk state that no labs were executed; this is a draft audit, not runtime verification.

## Appendix C — Verification Checklist for the Human Reviewer

### Docker

- [ ] **Legacy builder and BuildKit defaults — [VERIFY] [VERSION-SENSITIVE].** Check current Docker build documentation and installed Engine behavior. Local check: `docker version`, `docker build --help`, and a controlled `--progress=plain` build.
- [ ] **Build context and `.dockerignore`.** Check Dockerfile reference/build context docs. Local check: record `du -sh`, file inventory, and progress output before/after ignore changes.
- [ ] **`--no-cache` behavior.** Check current Docker CLI reference. Local check: compare a normal rebuild with a `--no-cache` build and document what remains warm.
- [ ] **`--load` constraints.** Check buildx build reference for driver/platform/output requirements. Local check: run a disposable single-platform build and inspect the resulting local image.
- [ ] **Image/context paths on WSL2.** Check Docker Desktop/WSL integration or native Engine setup. Local check: record context path, builder, platform, and measured timing.

### BuildKit / buildx

- [ ] **`RUN --mount=type=cache` — [VERIFY] [VERSION-SENSITIVE].** Check Dockerfile reference and BuildKit docs. Local check: run a disposable build twice and inspect cache behavior.
- [ ] **Driver support and lifecycle — [VERIFY] [VERSION-SENSITIVE].** Check Docker Build drivers documentation. Local check: `docker buildx ls` and `docker buildx inspect`.
- [ ] **`docker buildx history` — [VERIFY] [VERSION-SENSITIVE].** Check the current buildx CLI reference. Local check: `docker buildx --help` and `docker buildx history --help` if present.
- [ ] **`docker buildx du` and `prune` — [VERIFY] [VERSION-SENSITIVE].** Check current CLI reference and selected builder. Local check: `docker buildx du` and `docker buildx prune --help`; inspect first and avoid broad cleanup.
- [ ] **`buildkitd.toml` GC — [VERIFY] [VERSION-SENSITIVE].** Check BuildKit configuration docs for the installed version/driver. Local check: inspect builder configuration path and run a disposable builder test.

### Cache backends

- [ ] **`inline` exporter/importer — [VERIFY].** Check Docker Cache backends docs for supported mode and output behavior. Local check: build a disposable image and confirm the cache can be imported as expected.
- [ ] **`registry` backend and `mode=min|max` — [VERIFY] [VERSION-SENSITIVE].** Check current cache backend docs. Local check: use a dedicated non-release cache reference and inspect the next build's progress.
- [ ] **`local` cache — [VERIFY].** Check path semantics and exporter requirements. Local check: export to a new temp path, then import from that path.
- [ ] **`gha` backend — [VERIFY].** Check Docker cache docs and GitHub Actions documentation for cache permissions/eviction. Local check: not available in a local-only lab; validate in a non-production workflow if adopted.
- [ ] **`s3` backend — [VERIFY] [VERSION-SENSITIVE].** Confirm exact BuildKit distribution/plugin/config supports it. Local check: inspect official documentation for the exact implementation; do not assume the `type=s3` form works on every installation.
- [ ] **Cache trust namespace.** Check registry/object-store ACLs and branch policy. Local check: review read/write permission for trusted and untrusted identities.

### Drivers and remote builders

- [ ] **`docker`, `docker-container`, `kubernetes`, `remote` — [VERIFY] [VERSION-SENSITIVE].** Check official Build drivers docs. Local check: inspect builder list and selected builder configuration.
- [ ] **Remote authentication and tenant isolation — [VERIFY].** Review endpoint auth, TLS, RBAC, network policy, context confidentiality, worker state, and patch ownership. Local check: a security review of actual config; a driver name is insufficient.
- [ ] **QEMU/native multi-platform behavior — [VERIFY].** Check Docker multi-platform docs. Local check: build each target separately and record execution mode and timings.

### Measurement tooling

- [ ] **Benchmark harness — [VERIFY].** Run with `--n 2` on a disposable fixture, verify exit code, builder cleanup, logs, and image tags. Do not use the result as an SLO baseline until sample size and variance are adequate.
- [ ] **Nearest-rank p95.** Confirm the report records the convention and sample count. Local check: compare a small known duration list with the calculation.
- [ ] **`/usr/bin/time` and shell pipelines.** Check installed implementation and ensure command failure is not hidden. Local check: intentionally run a failing command in a disposable test and confirm the harness returns nonzero.
- [ ] **Progress output parsing.** Do not depend on exact log wording across versions. Local check: retain raw logs and manually inspect representative steps.

### CI provider awareness

- [ ] **GitHub Actions cache permissions/retention — [VERIFY].** Check current GitHub Actions cache docs and Docker `gha` backend docs. Local-only labs cannot verify hosted cache behavior.
- [ ] **S3/object-store permissions — [VERIFY].** Check the exact implementation's docs and cloud IAM policy if adopted. No cloud access is required for this lesson.
- [ ] **Cross-job cache behavior.** Verify actual workflow boundaries, key scope, and protected-branch/fork access in M02; this unit does not replace CI implementation.

## Appendix D — Known Limitations and Assumptions

- The uploaded prompt supplied the requirements, but the repository roadmap/syllabus source was not available for direct inspection. The lesson follows the prompt's stated Unit 4 requirements; repository path and neighboring-unit links should be checked against the actual tree.
- Live official documentation was not consulted. URLs are canonical starting points where known; exact current support, defaults, syntax, and headings must be verified.
- No lab, benchmark, build, or cleanup command was executed during authoring. All command output descriptions are representative. No measured speedup, cache-hit ratio, SLO attainment, or benchmark duration is claimed.
- The benchmark harness is designed for a local Docker environment and uses the `docker-container` driver. That driver may not be available or suitable in every Docker Desktop/native Engine configuration. Run a small test first.
- The harness's cold condition is fresh builder instruction cache, not a fully cold machine. Host page cache, base-image storage, network, registries, and other system caches may remain warm.
- The generated harness fixture is intentionally dependency-light to bound runtime and disk. It tests cache mechanics, not the full performance profile of pandas/pyarrow compilation. A real service benchmark is a follow-up once the harness is validated.
- The harness leaves tagged images for inspection. Review and remove only exact lab tags; no global prune is recommended.
- `s3` cache backend support, `mode=min|max`, build history, cache usage/prune commands, GC configuration, builder drivers, and cache-mount behavior are version/configuration sensitive.
- WSL2 performance depends on Docker Desktop/native Engine configuration, filesystem location, resource limits, and architecture. Keep these constant during comparison.
- M02 covers full CI/CD workflow implementation; M03 Kubernetes operations; M08 GitOps; M09 secrets; M12 supply-chain signing/provenance; M13 backup/disaster recovery. This unit defines build cache mechanics, performance measurement, and cache operations without replacing those modules.

## Appendix E — Sign-off

**Content status: DRAFT-AUDITED | Audit date: 2026-10-24 | Auditor role: AI self-audit (requires human verification) | Unverified items count: 20**

AI self-audit does not replace running the labs on the learner's environment, verifying current official documentation, reviewing cache permissions, or validating the benchmark harness and cleanup behavior. The unverified-item count is a grouped working estimate from Appendix C and should be updated after human checks.
