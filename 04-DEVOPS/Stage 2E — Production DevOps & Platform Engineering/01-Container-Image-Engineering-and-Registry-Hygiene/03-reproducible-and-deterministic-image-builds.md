# Unit 3 — Reproducible and deterministic image builds

**Abstract.** This lesson develops a practical method for controlling container-image build inputs, diagnosing drift, and documenting what a rebuild test actually proves. It uses a Python data-service example and a local-only workflow. The emphasis is on evidence: pin inputs, compare equivalent builds, investigate differences at the OCI and filesystem layers, and retain an honest record of residual uncertainty.

**Module:** M01 — Container Image Engineering and Registry Hygiene  
**Stage:** 2E — Production DevOps & Platform Engineering  
**Target filename:** `03-reproducible-and-deterministic-image-builds.md`  
**Estimated time:** 8–12 hours across the lessons and labs  
**Last reviewed:** 2026-10-24 (AI self-audit; live documentation and labs not verified)  
**Assumed tool baseline:** Docker Engine/CLI with BuildKit, `docker buildx`, Git, Python 3.12, `pip-tools`, and optionally Syft/Trivy. Check installed versions before copying version-sensitive commands. WSL2 Ubuntu is the primary environment; native Linux is also supported.

> **Status and honesty rule:** Commands and output snippets are representative unless explicitly marked as learner-generated evidence. Image digests, versions, timings, and scan results vary. No digest, benchmark, scan finding, or successful lab result is asserted as measured here. The repository roadmap and syllabus source named in the supplied prompt were not available for inspection in this authoring context; this lesson follows the supplied Unit 3 requirements and records that limitation in Appendix D.

## Table of contents

- [3.0 Why this matters in production](#30-why-this-matters-in-production)
- [3.1 Learning objectives](#31-learning-objectives)
- [3.2 Concept map and vocabulary](#32-concept-map-and-vocabulary)
- [3.3 Level 1 — Beginner](#33-level-1--beginner)
- [3.4 Level 2 — Intermediate](#34-level-2--intermediate)
- [3.5 Level 3 — Advanced](#35-level-3--advanced)
- [3.6 Level 4 — Expert](#36-level-4--expert)
- [3.7 SRE lens](#37-sre-lens)
- [3.8 Security lens](#38-security-lens)
- [3.9 Production checklist](#39-production-checklist)
- [3.10 Hands-on lab set](#310-hands-on-lab-set)
- [3.11 Self-check questions](#311-self-check-questions)
- [3.12 Evidence artifacts](#312-evidence-artifacts)
- [3.13 Common interview and design-review questions](#313-common-interview-and-design-review-questions)
- [3.14 Sources and verification notes](#314-sources-and-verification-notes)
- [Appendix A — Claim Register](#appendix-a--claim-register)
- [Appendix B — Ten-Pass Audit Report](#appendix-b--ten-pass-audit-report)
- [Appendix C — Human Verification Checklist](#appendix-c--human-verification-checklist)
- [Appendix D — Known Limitations and Assumptions](#appendix-d--known-limitations-and-assumptions)
- [Appendix E — Sign-off](#appendix-e--sign-off)

---

### 3.0 Why this matters in production

Imagine rebuilding a Python batch ETL image six weeks after a production incident. The Dockerfile has not changed, but an unpinned base tag or OS repository has moved, and a transitive Python dependency now resolves to a different release. The new image may behave differently, contain a different vulnerability set, or fail to reproduce the original incident. A digest recorded in a release record can identify the artifact that actually ran, but it does not by itself explain how that artifact was built or prove its contents were trustworthy. Reproducible-build practices make incident reconstruction, rollback, audit, and controlled remediation more evidence-driven. They also expose the limits of the evidence instead of promising that one Dockerfile always produces one identical image.

### 3.1 Learning objectives

By the end of this unit, the learner can:

1. **[L1]** Distinguish repeatable, reproducible, deterministic, and hermetic builds and give a production example of each.
2. **[L1]** Inventory the major inputs that can change an image even when source code is unchanged.
3. **[L2]** Pin a base image by a verified digest and use a hash-locked Python dependency file.
4. **[L2]** Explain what Python package hashes cover and what they do not cover in the full build.
5. **[L3]** Compare two equivalent builds at image, manifest, config, layer, and extracted-filesystem levels.
6. **[L3]** Diagnose timestamp, platform, package-repository, build-backend, and generated-metadata differences without inventing a cause.
7. **[L4]** Design an offline or hermetic-oriented workflow while preserving signature and integrity checks.
8. **[L4]** Write a rebuild-verification record that distinguishes observed equality from a general reproducibility guarantee.

### 3.2 Concept map and vocabulary

A container image is the output of a build process, not a direct encoding of a source commit. Build inputs include explicit files and less-visible environmental state. The diagram below is a simplified dependency graph; any omitted input that can affect output is a potential reproducibility gap.

```text
source commit + build context + Dockerfile + .dockerignore
                     |
base image digest + OS repository state + Python lockfile/hashes
                     |
builder/frontend version + platform + build args/environment
                     |
timestamps + generated files + network-fetched artifacts
                     v
              resolution and build
                     |
          OCI image index / manifest
             |          |          |
          config      layers    attestations
             |          |
             +---- digest comparison ----+
                         |
            inspect metadata/filesystem
                         |
      result record: equal / unequal / unresolved
```

| Term | Precise meaning | Common misconception |
|---|---|---|
| **Repeatable build** | A build process that can be run again under defined conditions and produce an acceptable outcome. Define “acceptable”: it may mean same tests pass, same dependency versions resolve, or identical bytes. | Repeatable always means byte-identical. |
| **Reproducible build** | A build where independent executions from the same declared inputs and controlled conditions produce the same specified output. State whether the target is byte-level or semantic/filesystem-level. | A successful second build proves reproducibility for every machine and platform. |
| **Deterministic build** | A process whose output is a deterministic function of its complete inputs. If a relevant input is hidden or random, the process may not be deterministic in practice. | Pinning a few versions makes the whole build deterministic. |
| **Hermetic build** | A build constrained so it consumes only declared, controlled inputs rather than ambient machine state or arbitrary network state. | Offline means hermetic, or hermetic means secure. |
| **Build context** | The files made available to the builder, filtered in part by `.dockerignore`. | Git-tracked files are automatically the only files in the context. |
| **Tag** | A human-readable image reference that a registry can retarget. | A tag is an immutable identifier. |
| **Digest** | A content-derived identifier, commonly shown as `sha256:<hex>`, for a specific content object. | A digest proves the content is safe or its producer is trusted. |
| **Manifest** | OCI metadata describing an image configuration and layer descriptors for a platform-specific image. | Every digest associated with an image refers to the same object. |
| **Image index** | A higher-level OCI object that can point to manifests for multiple platforms. | Comparing an index digest with a platform manifest digest is an apples-to-apples test. |
| **Lockfile** | A record of resolved dependency choices and, depending on the tool, integrity data and other metadata. | Every lockfile format has identical semantics. |
| **Provenance** | Information about where an artifact came from and how it was built. | Provenance generation alone verifies the claims are true. |
| **SBOM** | A software bill of materials: an inventory of software components detected or represented in an artifact. | An SBOM proves the listed components are vulnerability-free. |
| **Attestation** | A structured statement about an artifact or process, often signed or otherwise bound to an identity. | An attestation is trustworthy merely because it exists. |
| **`SOURCE_DATE_EPOCH`** | A convention for communicating a stable timestamp to build tools that support it. | Setting the variable forces every tool and file format to normalize timestamps. |

An image reference may look like `registry.example/team/service:1.4.2`. A digest-qualified reference may look like `registry.example/team/service:1.4.2@sha256:<verified-digest>`. The angle-bracket text is a placeholder, not a valid digest. A digest normally identifies the exact object addressed; for multi-platform images, that object may be an image index rather than one platform manifest. Record which object was inspected.

### 3.3 Level 1 — Beginner

#### The same Dockerfile is not the same set of inputs

Consider:

```dockerfile
# File: Dockerfile.uncontrolled
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY service/ ./service/
CMD ["python", "-m", "service"]
```

This is an **ANTI-PATTERN — DO NOT COPY as a production pinning strategy**. The tag `python:3.12` is a mutable reference. The operating-system package state inside that image can change when the tag is updated. An unconstrained `requirements.txt` can resolve different versions later. A build can also vary with platform, builder version, package index state, timestamps, or files accidentally included in the context.

The build-input inventory should cover:

- Git commit and working-tree state.
- Dockerfile and `.dockerignore`.
- Entire build context, including generated or untracked files.
- Base-image reference and resolved digest.
- OS package repositories, package versions, and repository snapshot state.
- Direct and transitive Python dependencies, hashes, package index, and build backend.
- BuildKit/buildx version, builder driver, Dockerfile frontend, and relevant configuration.
- Target platform (`linux/amd64`, `linux/arm64`, etc.).
- Build arguments, environment variables, locale, timezone, and relevant host inputs.
- Timestamps, archive ordering, generated metadata, and downloaded artifacts.

#### Tags and digests

A tag is useful for humans; it is not a permanent content identity. A SHA-256 digest identifies a content object by its digest. To inspect a local image:

```bash
# Representative commands; run from a shell with Docker available.
docker image inspect python:3.12 --format '{{json .RepoDigests}}'
docker buildx imagetools inspect python:3.12
```

**EXPECTED / REPRESENTATIVE:** the first command may print a JSON array of repository digest references or `null` if no repository digest is recorded locally. The second prints available manifest/index information for the reference. Output varies with the reference and tool version. Interpret the result carefully: a multi-platform tag can resolve to an index digest and individual platform manifests.

To record local tool versions:

```bash
docker version
docker buildx version
docker buildx ls
```

**EXPECTED / REPRESENTATIVE:** client/server version details, a buildx version, and a list of configured builders. These are environment-specific. Save the output rather than copying an example version into an evidence record.

A digest is an identity mechanism, not a trust mechanism. A malicious or vulnerable image can have a perfectly valid digest. Trust requires separate controls over source, publisher, build process, signatures/attestations, review, and policy.

#### Guided L1 lab: observe tag drift risk

1. Create a dedicated directory, and record the current reference inspection output.
2. Inspect the base image tag using `docker buildx imagetools inspect`.
3. Record the index digest and, if relevant, the platform manifest digest.
4. Repeat at a later controlled point or compare with a documented digest update pull request. Do not assume the tag changed merely because the tag is mutable.

```bash
# File: commands-l1.sh
set -euo pipefail
mkdir -p evidence/unit-03/l1
date -u '+%Y-%m-%dT%H:%M:%SZ' | tee evidence/unit-03/l1/observed-at.txt
docker buildx imagetools inspect python:3.12 \
  | tee evidence/unit-03/l1/python-tag-inspection.txt
docker version | tee evidence/unit-03/l1/docker-version.txt
docker buildx version | tee evidence/unit-03/l1/buildx-version.txt
```

**EXPECTED / REPRESENTATIVE:** an inspection report containing a digest and platform entries, plus version output. The digest must be captured from your own command. If the command fails because buildx is unavailable or registry access is blocked, record the failure; do not substitute a fabricated digest.

**What just happened?** You captured a time-stamped observation of a mutable reference and the tools used to inspect it. This is useful evidence, but it does not prove that the tag will change or that the image is trustworthy.

| Symptom | Likely cause | Fix |
|---|---|---|
| Same Dockerfile, different image digest | One or more build inputs or generated metadata changed | Inventory and compare inputs before changing code |
| `pip install` chooses a new transitive version | Dependencies were not fully locked | Use a lock workflow with hashes and review updates |
| Local digest unavailable | Image was built locally or repository digest metadata is absent | Inspect the remote reference and record the exact object used |
| amd64 and arm64 digests differ | Platform-specific output differs by design | Compare builds for the same target platform |
| Same filesystem, different image digest | Config, layer bytes, timestamps, history, manifest, or attestations differ | Inspect the object hierarchy rather than assuming file contents explain all differences |

Common beginner mistakes are treating tags as immutable, comparing unlike platform objects, assuming a digest is a security certification, and changing several inputs at once during diagnosis.

### 3.4 Level 2 — Intermediate

#### Pin the base image and keep the reference readable

Resolve the current digest from an official registry inspection, then review it before placing it in the Dockerfile. The following illustrates the format but deliberately cannot be built until the placeholder is replaced:

```dockerfile
# File: service/Dockerfile
# Readability note: replace the placeholder only after verifying the digest
# from the intended publisher and target image/index.
FROM python:3.12-slim@sha256:<REPLACE_WITH_VERIFIED_SHA256_DIGEST>
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY requirements.lock .
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.lock
COPY service/ ./service/
CMD ["python", "-m", "service"]
```

The placeholder is intentionally non-executable. Do not invent a digest or paste one from an unrelated platform/object. A useful review process records the human tag, registry/repository, exact digest, source of verification, target platform, date, and reviewer. Update digest pins through a reviewed change with tests and vulnerability checks. Detailed base-image selection belongs to [Unit 2 — Minimal and distroless base images](02-minimal-and-distroless-base-images.md); tag and promotion policy belongs to [Unit 5 — Image tagging, versioning, and immutability](05-image-tagging-versioning-and-immutability.md).

#### Lock Python dependencies with hashes

`pip-compile --generate-hashes` from `pip-tools` can produce a pinned requirements file with hashes for resolved distributions. A typical workflow starts with a declared input file:

```text
# File: service/requirements.in
fastapi
uvicorn
pandas
pyarrow
```

The unconstrained declarations are intentional inputs to the lock-generation step, not the final installation specification. Run the lock-generation tool in a controlled environment:

```bash
python -m pip install pip-tools
pip-compile --generate-hashes --output-file service/requirements.lock service/requirements.in
```

**EXPECTED / REPRESENTATIVE:** a lock file with pinned versions and one or more `--hash=sha256:...` entries per distribution where supported by the resolver. The actual versions and hashes must come from the command. Pin the `pip-tools` version in the environment used to generate the lock and review the resulting diff. The exact command behavior and options should be checked against the official pip-tools documentation for the installed version.

Install using hash enforcement:

```bash
python -m pip install --require-hashes -r service/requirements.lock
```

**EXPECTED / REPRESENTATIVE:** pip installs only if the requirements satisfy hash-checking mode and the selected artifacts match the accepted hashes. If requirements are incomplete or a hash is missing, the install can fail. Hashes protect the downloaded package artifacts that are covered by the lock; they do not automatically pin the base image, OS packages, compiler, build backend, package index trust, or every output byte produced during a source build.

A lockfile discipline has four parts: declare direct dependencies, resolve and record transitive dependencies, retain integrity hashes, and review lock updates as code. Treat lockfile regeneration as a dependency update, not as a routine unreviewed side effect.

**`uv` alternative — [VERIFY].** `uv` has its own lockfile format and workflow. Do not assume a `uv.lock` file is interchangeable with a pip requirements file or that their resolution, export, and build semantics match. Consult the official uv documentation for the installed version and document the exact command used to export or install locked dependencies.

#### OS package pinning and Debian snapshots

A Dockerfile that runs `apt-get update` and installs packages from a moving repository can resolve different package versions on different dates. Explicit package versions help, but a version pin alone may not ensure the same package remains available forever. Debian's `snapshot.debian.org` provides access to historical repository states, which can support time-bounded, reviewable builds. Snapshot use requires correct suite/component selection, valid signing metadata, retention/availability checks, and current APT configuration. **[VERIFY]** Check the official snapshot documentation and Debian APT documentation before applying a production configuration. Do not disable signature validation to make a snapshot build work.

#### End-to-end Python data-service example

Project layout:

```text
service/
├── Dockerfile
├── requirements.in
├── requirements.lock
└── service/
    ├── __init__.py
    └── main.py
```

```python
# File: service/service/main.py
from __future__ import annotations

import os
from fastapi import FastAPI

app = FastAPI(title="ETL status API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/build-inputs")
def build_inputs() -> dict[str, str]:
    # Expose non-secret operational metadata only.
    return {
        "release": os.getenv("RELEASE_ID", "local"),
        "python": os.sys.version.split()[0],
    }
```

This example is a small API representative of a data platform service. A production ETL image may additionally compile `pandas`/`pyarrow` dependencies or consume native wheels. Those steps add toolchain, architecture, libc/ABI, and build-backend inputs. Do not expose secret environment variables or dump the full environment to make builds “debuggable.”

```dockerfile
# File: service/Dockerfile
# Replace the placeholder with a verified digest before building.
FROM python:3.12-slim@sha256:<REPLACE_WITH_VERIFIED_SHA256_DIGEST>
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=UTC
COPY requirements.lock .
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.lock
COPY service/ ./service/
CMD ["python", "-m", "service"]
```

**Build command after pinning:**

```bash
docker build --platform linux/amd64 -f service/Dockerfile -t etl-status:local service
docker image inspect etl-status:local --format '{{.Id}} {{json .RepoDigests}}'
```

**EXPECTED / REPRESENTATIVE:** build output followed by the local image ID and repository digest metadata if present. Replace the placeholder first. The local image ID is not necessarily the same object as a registry manifest digest; record what the field represents.

#### Pattern catalogue

| Pattern | Use when | Do not use when / limitation |
|---|---|---|
| Base image pinned by digest with a readable tag comment | You need stable content identity and human context | Do not let the pin remain stale indefinitely; establish an update cadence |
| Hash-locked Python requirements | Python package artifact integrity and version resolution matter | It does not pin OS packages or guarantee source-build byte identity |
| OS repository snapshot plus signature verification | Historical OS package state must be reconstructable | Snapshot availability and repository metadata need ongoing validation |
| Recorded platform and builder configuration | Rebuilds must be compared fairly | It cannot remove all toolchain nondeterminism by itself |
| Scheduled reviewed pin updates | You need reproducibility without permanent staleness | Do not merge blindly without tests and security review |

#### Anti-pattern catalogue

| Bad example | Why it hurts | Corrected approach |
|---|---|---|
| `FROM python:latest` | The reference can move and obscures the exact input | Choose a supported release and pin its verified digest |
| `RUN pip install fastapi` | Resolver state can change between builds | Install from a reviewed lockfile with hashes |
| `RUN apt-get update && apt-get install -y curl` without a controlled repository strategy | Package metadata and package versions can drift | Use a reviewed snapshot/version strategy and retain signature verification |
| `RUN curl -fsSL https://example.invalid/install.sh \| sh` | Executes network content without a separately reviewed artifact boundary | Fetch a versioned release artifact, verify its published checksum/signature where available, then execute the reviewed artifact |
| Generate lockfiles during every image build | Resolution is mixed into the release build and can drift | Generate lockfiles in a separate reviewed update workflow |
| Record only the tag in a release record | A later lookup may resolve a different object | Record the digest and platform/object type |

#### Measurable L2 lab: pin and lock

1. Create the project structure above and add the API file.
2. Record `git rev-parse HEAD` if tracked; otherwise record `LOCAL-SNAPSHOT` and hash the source files.
3. Generate a lockfile in a controlled Python environment.
4. Resolve and review the base digest; replace the explicit placeholder.
5. Build for one named platform and save logs.
6. Record Dockerfile and lockfile hashes using `sha256sum`.
7. Change one declared dependency in `requirements.in`, regenerate the lock, and inspect the diff. Do not silently accept a transitive change.

```bash
# File: commands-l2.sh
set -euo pipefail
mkdir -p evidence/unit-03/l2
sha256sum service/Dockerfile service/requirements.in service/requirements.lock \
  | tee evidence/unit-03/l2/input-hashes.txt
docker build --platform linux/amd64 --progress=plain \
  -f service/Dockerfile -t etl-status:l2 service \
  2>&1 | tee evidence/unit-03/l2/build.log
docker image inspect etl-status:l2 --format '{{.Id}}' \
  | tee evidence/unit-03/l2/image-id.txt
```

**EXPECTED / REPRESENTATIVE:** file hashes, a verbose build log, and an image ID. If a placeholder remains, the build should fail; that is a deliberate guard, not a reason to use an invented digest. Measure whether the intended inputs are recorded, whether the build fails closed on an invalid pin, and whether a lockfile change is reviewable.

### 3.5 Level 3 — Advanced

#### Timestamp normalization and hidden nondeterminism

Byte-level equality is harder than dependency pinning. Common sources of differences include:

- File modification times and image config/history creation timestamps.
- Archive member ordering and metadata such as owner/group IDs.
- Locale, timezone, filesystem traversal order, and environment-dependent generated files.
- Random temporary directories, generated UUIDs, build IDs, or embedded absolute paths.
- Python bytecode (`.pyc`) and timestamps or interpreter details that affect its creation.
- Python packaging build isolation, which may create an isolated environment and resolve build requirements separately from runtime dependencies.
- Source distributions that compile native code with a compiler, linker, headers, system libraries, and architecture-specific flags.
- Repository metadata, wheel availability, and platform-specific dependency selection.
- Builder/frontend versions and provenance metadata generated as part of the output.

Some controls are available to the project: fix locale/timezone, avoid embedding random identifiers, use stable archive ordering, normalize ownership, record `SOURCE_DATE_EPOCH`, and pin toolchains. Other behavior depends on upstream build tools or package backends. The `SOURCE_DATE_EPOCH` convention only helps tools that implement it; it is not a universal switch.

**[VERIFY] `[VERSION-SENSITIVE]`** The form `--output type=oci,rewrite-timestamp=true` may be available in some BuildKit/buildx versions and output paths. Before using it, check the official Buildx build-output documentation and the BuildKit documentation for the exact installed versions, driver, and output type. Do not assume this option is accepted by every builder or that it normalizes all timestamps.

#### Compare equivalent builds, then diagnose unequal output

First ensure the two builds use the same source snapshot, Dockerfile/context, target platform, build args, base digests, lockfile, builder/frontend configuration, and relevant repository/network state. Do not compare an amd64 output with an arm64 output as though byte equality were expected.

A digest comparison is the fastest detector:

```bash
docker image inspect etl-status:build-a --format '{{.Id}}'
docker image inspect etl-status:build-b --format '{{.Id}}'
docker image inspect etl-status:build-a --format '{{json .RootFS.Layers}}'
docker image inspect etl-status:build-b --format '{{json .RootFS.Layers}}'
```

**EXPECTED / REPRESENTATIVE:** image IDs and arrays of layer diff IDs. Values are environment-specific. Different image IDs show that the inspected local image config objects differ; layer arrays can help localize the divergence but do not alone explain it.

For remote manifest/index inspection:

```bash
docker buildx imagetools inspect registry.example/team/etl-status:build-a
docker buildx imagetools inspect registry.example/team/etl-status:build-b
```

**EXPECTED / REPRESENTATIVE:** manifest/index digests and platform descriptors for the references. Use your actual registry and tags. Do not confuse a local image ID/config digest, a compressed layer blob digest, an uncompressed layer diff ID, a platform manifest digest, and an index digest.

Optional tools such as `diffoci` or `container-diff` can help compare OCI images and filesystems. **[VERIFY]** Follow the chosen tool's official installation and usage documentation for the exact version. A manual fallback is to inspect image metadata, export/extract filesystems in an isolated directory, and compare file paths, content hashes, modes, owners, and timestamps. Extraction commands and output format vary; keep the extraction path dedicated to this lab.

```bash
# File: compare-layer-digests.sh
set -euo pipefail
for image in "$@"; do
  printf '\nIMAGE %s\n' "$image"
  docker image inspect "$image" --format 'ImageID={{.Id}}'
  docker image inspect "$image" --format 'Layers={{json .RootFS.Layers}}'
done
```

**EXPECTED / REPRESENTATIVE:** one image ID and layer list per image argument. This script detects some differences; it does not inspect every manifest, attestation, or extracted filesystem detail. If no arguments are passed, Docker may return an error; supply the two image references.

#### Debugging table

| Observed difference | Likely source | Diagnostic test | Remediation | Residual uncertainty |
|---|---|---|---|---|
| Different base manifest digest | Mutable tag or platform/index mismatch | Inspect tag/index and platform manifest | Pin the intended digest; record platform | Publisher may later issue a new, reviewed digest |
| Different Python package versions | Lock missing/incomplete or index changed | Compare lockfiles and installed package inventory | Regenerate lock in a reviewed update process | Source-build behavior may still vary |
| Same package versions, different layer digest | Metadata, ordering, timestamps, compression, or package build output | Compare layer digests and extracted files/metadata | Normalize controllable metadata; inspect package backend | Compressed bytes can differ despite equivalent extracted files |
| Same filesystem files, different image digest | Config/history/manifest/attestation differences | Inspect config and manifest objects | Define target level of equality; normalize supported fields | Builder metadata may remain intentionally unique |
| Only arm64 build differs | Architecture-specific wheel or compilation path | Compare same platform and dependency selection | Pin toolchain and test per platform | Native output may vary across toolchains |
| Build fails offline | Missing wheel, source archive, OS package, or build requirement | Run in isolated network-disabled environment and capture missing input | Vendor complete verified inputs or maintain controlled mirror | Mirror lifecycle and trust must be maintained |
| Provenance changes between builds | Build metadata or invocation fields vary | Compare attestation payloads and builder metadata | Define whether provenance is excluded from byte-level target or normalized | Attestations may intentionally describe distinct invocations |

#### Native wheels and source builds

Python package resolution can select different artifacts depending on Python version, ABI, platform, and architecture. A prebuilt wheel and a source distribution are not equivalent build inputs. A source distribution may trigger build isolation and compilation, introducing compiler version, linker behavior, headers, system libraries, and build-backend dependencies. For data services using `pandas` or `pyarrow`, record platform and the exact selected wheel/source artifact. Manylinux wheel compatibility labels are relevant to wheel selection, but they do not guarantee that every build step in the container is deterministic.

#### Design trade-offs

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Pin only application dependencies | Low effort; prevents common resolver drift | Base and OS state still drift | False confidence in whole-image reproducibility | Early learning or low-criticality prototype |
| Pin base digest and hash-lock Python packages | Stronger control over common inputs | Update workflow and lock maintenance | Stale pins if maintenance is neglected | Most production Python services |
| Add OS snapshots and pinned toolchains | Better reconstruction of OS/native builds | Repository and toolchain lifecycle complexity | Snapshot retention or build compatibility problems | Native dependencies or strict audit requirements |
| Normalize timestamps and generated metadata | Removes controllable sources of byte drift | Requires tool-by-tool validation | May not address upstream nondeterminism | Byte-level reproducibility is a real requirement |
| Hermetic/offline build graph | Limits ambient network and host inputs | Vendoring/mirror storage and update process | Missing input can block emergency patching | High-assurance or air-gapped environments |

**L3 decision lab:** Choose one target—byte-identical OCI artifact, equivalent extracted filesystem, or repeatable dependency resolution. Define acceptance criteria, run two builds under controlled conditions, and defend why the chosen target is sufficient for the service's risk. A passing filesystem comparison is not a byte-identical OCI result.

### 3.6 Level 4 — Expert

#### Hermeticity, offline builds, and vendoring

A hermetic build consumes declared inputs from controlled locations and avoids accidental dependence on the host, current network state, or untracked files. Network isolation is one possible control, not a proof of hermeticity. An offline build can still be non-deterministic because timestamps, random IDs, toolchain behavior, or generated metadata can vary. Conversely, a build that is reproducible is not automatically secure: it may reproduce vulnerable or malicious content exactly.

A robust offline workflow has a deliberate acquisition stage:

1. Resolve and review versions in a connected, controlled environment.
2. Download all required artifacts, including transitive Python packages, source archives, build-system requirements, OS packages, and toolchains.
3. Verify integrity using the package manager's checks and publisher signatures/checksums where available.
4. Store artifacts in an access-controlled, versioned mirror or vendor directory.
5. Transfer them into the isolated environment with an auditable manifest.
6. Build with network access disabled where feasible and fail if a required input is missing.
7. Update the offline set through a documented, reviewed process; never bypass TLS, signature, or hash checks just to make the build succeed.

Caches are performance mechanisms, not proof of hermeticity. A cache may be populated from mutable sources, omit inputs, or be bypassed on a clean machine. Detailed cache design belongs to [Unit 4 — Build caching, BuildKit, and build performance](04-build-caching-buildkit-and-build-performance.md).

#### Bazel and Nix awareness

Bazel emphasizes declared build actions and dependency graphs; Nix emphasizes reproducible package/build environments and explicit dependency inputs. Both can provide stronger input control than an unconstrained shell-based build when the project and toolchain are modeled correctly. They introduce learning and migration costs, require ecosystem/toolchain integration, and do not magically eliminate nondeterminism in arbitrary external tools. They are awareness-only here; installing them is not required for the labs.

#### Provenance, SLSA, BuildKit, and SBOM

Supply-chain Levels for Software Artifacts (SLSA) provides a framework for thinking about build integrity and provenance. A practical provenance statement can describe source identity, builder identity, build parameters, and materials/dependencies. Its value depends on how it was produced, bound to the artifact, stored, and verified against a trust policy.

**[VERIFY] `[VERSION-SENSITIVE]`** Buildx options such as `--provenance` and `--sbom` depend on Buildx/BuildKit versions, builder driver, exporter, and configuration. Consult current official Docker Buildx documentation for the installed version and test the exact syntax locally. Record whether attestations were emitted, where they are stored, what fields they contain, and how they are bound to the image. Do not assume every registry or output mode preserves them identically.

An SBOM is an inventory, not a guarantee that the inventory is complete or that components are safe. Provenance generation is not provenance verification. Verification requires a policy about trusted builders, expected source repository/commit, allowed parameters, artifact binding, and any signatures/identity claims. A compromised trusted builder can produce plausible but false claims. Do not put secrets in build args, environment variables, logs, or provenance-visible metadata. For builds requiring credentials, use BuildKit secret mounts and follow the separate secrets-management module (forward reference: M09).

#### Dependency update automation and ownership

Renovate and Dependabot can propose dependency updates while keeping pins explicit. They are awareness-only tools in this unit, not required services. A healthy update workflow includes:

- Scheduled updates for base images, OS packages, Python direct/transitive dependencies, and toolchains.
- Pull requests that show lockfile and digest diffs.
- Automated tests, image scans, and rebuild-verification checks appropriate to the service.
- A named owner for reviewing and merging updates.
- Emergency updates for material vulnerabilities, with an accelerated review path and recorded exception.
- A rollback mechanism to a known digest, plus a post-rollback plan to resolve the underlying issue.
- A maximum age policy for exceptions and stale pins.

Pinning without updates can make an image repeatably old and vulnerable. Balance reproducibility with patch freshness.

#### Formal rebuild-verification procedure

1. Select a source commit or create a named local source snapshot; capture dirty/untracked state.
2. Select one target platform and one output target (OCI index, platform manifest, image config, or extracted filesystem).
3. Record Dockerfile, `.dockerignore`, build context manifest, base digest, OS package source strategy, Python lock/hash file, build backend, toolchain, builder version/driver, build args, and relevant environment.
4. Build in a clean workspace twice under equivalent conditions. Use separate tags and save complete logs.
5. Record image ID, manifest/index digest, per-layer digest/diff ID, config metadata, and attestation digests if applicable.
6. Compare the selected target. If unequal, inspect manifest/config/layers and then extracted filesystem metadata/content.
7. Change one suspected input or normalization control at a time. Rebuild and preserve each attempt; do not rewrite the result table from memory.
8. Classify the outcome: byte-identical for the declared object, filesystem-equivalent under the stated comparison, dependency-resolution repeatable, or unresolved.
9. Record residual nondeterminism, assumptions, and unsupported guarantees.
10. Retain logs, input manifest, lockfile, SBOM/provenance outputs, comparison report, and a signed/reviewed decision record where organizational policy requires it.

A single pair of equal outputs proves only that the selected comparison was equal for those two runs under those conditions. It does not establish universal reproducibility across time, builders, or architectures. More attempts can increase confidence but still do not prove all possible environments.

#### Failure scenarios and organizational strategy

| Symptom | Hypothesis | Test | Root cause example | Fix | Prevention |
|---|---|---|---|---|---|
| Rebuild after incident has different digest | Hidden input changed | Compare recorded input manifests and layers | Base tag moved | Rebuild from recorded digest and lockfile | Release input manifest required |
| CI and WSL2 differ | Platform, filesystem, builder, or line-ending difference | Compare platform, versions, context hashes | Different target architecture or context contents | Align declared conditions or define separate outputs | Test WSL2 and native Linux assumptions explicitly |
| Offline build cannot install dependency | Artifact set incomplete | Capture exact missing package/build requirement | Build isolation needs an unvendored backend | Acquire and verify the missing artifact | Periodic offline rehearsal |
| Provenance exists but review rejects it | Builder/source claim not trusted | Validate identity and artifact binding | Attestation generated by untrusted builder | Configure trusted identity and policy | Verify attestations, not merely their presence |
| Pin update causes runtime failure | Update not behaviorally compatible | Run regression tests and compare dependency diff | Transitive API/ABI change | Roll back to known digest; investigate and re-update | Staged update and canary policy |

Organizational ownership must be explicit. Application owners own dependency compatibility; platform owners own builder baselines and base-image policies; security owns trust requirements and exception review; SRE owns rebuild runbooks and operational measurements. For CI implementation, see M02; Kubernetes runtime operations belong to M03; supply-chain signing and policy deep dives belong to M12.

### 3.7 SRE lens

Treat rebuild verification as an operational capability, not a checkbox. Candidate service-level indicators (SLIs) include:

- **Rebuild verification pass rate:** percentage of scheduled verification runs meeting the explicitly defined equality target.
- **Input-record completeness:** percentage of production image releases with source, base digest, dependency lock, platform, builder version, and build arguments recorded.
- **Artifact reconstruction time:** elapsed time to reconstruct or retrieve the exact artifact for a prior release.
- **Drift investigation time:** time from detecting an unexpected difference to recording a supported root cause or an explicit unresolved finding.
- **Dependency patch lead time:** time from an approved update becoming available to its deployment, balanced against change-failure rate.

Set service-level objectives (SLOs) only after measuring the current baseline and deciding what risk the service can accept; do not invent a universal target. A high reproducibility pass rate can still conceal stale vulnerable pins. Pair it with patch freshness and exception-age indicators.

**Runbook snippet**

1. **Signal:** scheduled rebuild produces a different digest, or release metadata is incomplete.
2. **Triage:** freeze promotion of the candidate; retain logs; confirm source commit, platform, builder, base digest, and lockfile.
3. **Mitigation:** continue running the last known approved digest if safe; do not blindly rebuild and overwrite the release reference.
4. **Diagnosis:** compare index/manifest, config, layers, and filesystem; change one input at a time.
5. **Follow-up:** record cause, update policy or tooling, run the verification again, and close or time-bound the exception.

Capacity planning: image pulls and clean builds consume disk, network, CPU, and registry bandwidth. The lab is designed for a small laptop, but Python scientific packages and multiple build outputs may consume substantial disk/network. Inspect Docker disk use before pruning. Prefer targeted cleanup; never run a global prune as a casual lab step.

### 3.8 Security lens

| Supply-chain stage / threat | Control | What the control does **not** prove |
|---|---|---|
| Mutable source or base reference | Record source commit; pin base by verified digest | Source code or base content is benign |
| Dependency substitution | Hash-locked Python artifacts; trusted package index; review transitive updates | OS packages and build tools are covered by Python hashes |
| Repository compromise or stale metadata | Signature verification and controlled repository/snapshot policy | A correctly signed package has no vulnerability |
| Build parameter manipulation | Record build args and use policy checks | Every hidden environment input is captured |
| Untrusted build execution | Trusted builder identity, access controls, isolated build environment | Builder cannot be compromised |
| Secret leakage | Avoid secrets in `ARG`, `ENV`, logs, lockfiles, and evidence; use secret mounts where needed | Every tool automatically prevents secret exfiltration |
| False provenance confidence | Verify artifact binding, builder identity, source, and policy | An attestation is true merely because it parses |
| Stale dependency pins | Scheduled updates, emergency process, exception expiry | Updating every dependency immediately is always safe |
| Incomplete component inventory | Generate and review an SBOM; compare with build inputs | SBOM completeness or vulnerability-free status |

Digest pinning is a content identity control. Hashes verify downloaded artifacts against recorded values. Repository trust determines whether those artifacts should be accepted. Provenance provides claims that must be verified. These controls are complementary, not substitutes. Threat modeling can use STRIDE (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege), but the key operational question is always: which attacker action is prevented or detected, and what trust boundary remains?

### 3.9 Production checklist

- [ ] **Source identity:** record Git commit, dirty state, submodules, and generated/untracked files. Evidence: `git status --short` and `git rev-parse HEAD`.
- [ ] **Context identity:** retain Dockerfile, `.dockerignore`, and a manifest/hash of the actual build context. Evidence: `sha256sum` of key files plus context inventory.
- [ ] **Base image:** pin the verified digest and record whether it is an index or platform manifest. Evidence: `docker buildx imagetools inspect`.
- [ ] **Python dependencies:** retain reviewed lockfile with hashes and controlled lock-generation tool version. Evidence: lockfile and its SHA-256 hash.
- [ ] **OS packages:** document package versions and repository/snapshot policy, including signature verification. Evidence: apt source configuration and package manifest.
- [ ] **Build toolchain:** record Docker, buildx/BuildKit, frontend, builder driver, target platform, and relevant configuration.
- [ ] **Build args/environment:** record non-secret values that can affect output; verify no credentials are included.
- [ ] **Nondeterminism controls:** document timestamp, ownership, ordering, locale/timezone, `.pyc`, and generated metadata policy.
- [ ] **Double-build test:** build twice in clean equivalent conditions and retain image/manifest/layer comparisons.
- [ ] **Difference diagnosis:** if unequal, inspect config, manifests, layers, and filesystem; record unresolved differences.
- [ ] **Provenance/SBOM:** document whether emitted, where stored, and how verification is performed; do not treat presence as proof.
- [ ] **Update policy:** define scheduled and emergency pin updates, automated tests/scans, reviewer, and rollback.
- [ ] **Exception process:** record owner, risk acceptance, expiry date, compensating control, and closure criteria.
- [ ] **Resource hygiene:** inspect disk and remove only lab-scoped temporary outputs after evidence is retained.

### 3.10 Hands-on lab set

All labs are local/free and intended for WSL2 Ubuntu or native Linux with Docker available. Network access is needed for initial image/package acquisition; builds may use several hundred MB or more depending on dependencies. Keep projects in a dedicated directory. Each lab must be rerun safely and must retain evidence before cleanup.

#### Lab 1 — Capture the input inventory

**Goal:** establish a baseline inventory for a small Python data service.  
**Prerequisites:** Git, Docker CLI, buildx, shell.  
**Steps:**

```bash
# File: lab-01-inventory.sh
set -euo pipefail
mkdir -p evidence/unit-03/lab-01
git rev-parse HEAD 2>&1 | tee evidence/unit-03/lab-01/source-commit.txt || \
  printf 'LOCAL-SNAPSHOT: not in a Git repository\n' \
  | tee evidence/unit-03/lab-01/source-commit.txt
git status --short 2>&1 | tee evidence/unit-03/lab-01/git-status.txt || true
docker version | tee evidence/unit-03/lab-01/docker-version.txt
docker buildx version | tee evidence/unit-03/lab-01/buildx-version.txt
sha256sum service/Dockerfile service/requirements.in service/requirements.lock \
  | tee evidence/unit-03/lab-01/input-hashes.txt
```

**EXPECTED / REPRESENTATIVE:** commit/status or local-snapshot marker, tool versions, and file hashes. If a file does not yet exist, create it before running the script; do not suppress missing input files.  
**Evidence:** `evidence/unit-03/lab-01/`.  
**Cleanup:** no containers are created; preserve evidence. Verify `docker ps --filter label=unit-03-lab` returns no rows (the lab should not create any).  
**Stretch:** add a sorted manifest of source file paths and content hashes.

#### Lab 2 — Pin base and lock Python dependencies

**Goal:** make common dependency inputs explicit.  
**Prerequisites:** Lab 1, package-index access, a verified base digest.  
**Steps:** generate the lock with `pip-compile --generate-hashes`, inspect the diff, resolve the base reference, and replace the Dockerfile placeholder only with a verified digest from the intended publisher. Build for one explicit platform and save logs. Use `--require-hashes` during installation.  
**EXPECTED / REPRESENTATIVE:** a pinned lock, an explicit base reference, and a build log. No output values should be copied from this lesson.  
**Evidence:** lockfile, Dockerfile, digest review note, build log, and hashes.  
**Cleanup:** stop/remove only a container created by this lab, if any; do not remove shared images. Confirm `docker ps -a --filter name=unit03-lab2` is empty after cleanup.  
**Stretch:** implement a pull-request checklist for digest/lock updates.

#### Lab 3 — Mandatory two-build drift investigation

**Goal:** build the same source twice, observe whether the image differs, investigate the difference, and change one variable at a time.  
**Prerequisites:** Labs 1–2; a buildable service; enough disk for two image references.  
**Important:** differences are not guaranteed on every machine. The first pair may be equal. Do not fabricate a differing digest. If equal, use the diagnostic branch to inspect which metadata fields and inputs are actually covered, then introduce a controlled variation (for example, an intentionally changed non-secret build argument consumed by a file) to demonstrate how an input change propagates. That controlled variation demonstrates input sensitivity, not spontaneous nondeterminism.

**Procedure:**

1. Choose a source commit or name a local snapshot. Record dirty state and hashes of Dockerfile, `.dockerignore`, lockfile, and source files.
2. Record base digest, platform, builder version/driver, relevant build args, and output references.
3. Build A and Build B with the same source/context and declared inputs in clean equivalent directories. Keep build logs.
4. Capture local image IDs and layer diff IDs. Inspect remote manifest/index data if the outputs are pushed to a registry; pushing is not required for this local lab.
5. Compare the results. If unequal, inspect metadata and filesystem differences. If equal, record equality at the exact object level tested.
6. Change one input only. A safe controlled test is to add a non-secret `BUILD_LABEL` build argument that is written to a metadata file. Rebuild both variants and compare. Then revert that change.
7. If the initial build differs without an intentional input change, test timestamp normalization and generated metadata only after checking current tool support. Keep every attempt and explain residual uncertainty.

```dockerfile
# File: service/Dockerfile.lab
# Replace the base digest placeholder with a verified digest before use.
FROM python:3.12-slim@sha256:<REPLACE_WITH_VERIFIED_SHA256_DIGEST>
WORKDIR /app
ARG BUILD_LABEL=baseline
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TZ=UTC
COPY requirements.lock .
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.lock
COPY service/ ./service/
RUN printf '%s\n' "$BUILD_LABEL" > /app/build-label.txt
CMD ["python", "-m", "service"]
```

**EXPECTED / REPRESENTATIVE:** builds should use the same declared source and platform. The resulting image IDs may match or differ. If `BUILD_LABEL` differs, `/app/build-label.txt` should differ; this is an intentional input change. Do not label this a spontaneous nondeterminism result.

```bash
# File: lab-03-build-twice.sh
set -euo pipefail
mkdir -p evidence/unit-03/lab-03
docker build --platform linux/amd64 --progress=plain \
  -f service/Dockerfile.lab --build-arg BUILD_LABEL=baseline \
  -t unit03-rebuild-a:local service 2>&1 \
  | tee evidence/unit-03/lab-03/build-a.log
docker build --platform linux/amd64 --progress=plain \
  -f service/Dockerfile.lab --build-arg BUILD_LABEL=baseline \
  -t unit03-rebuild-b:local service 2>&1 \
  | tee evidence/unit-03/lab-03/build-b.log
for image in unit03-rebuild-a:local unit03-rebuild-b:local; do
  docker image inspect "$image" --format \
    '{{.Id}} {{json .RootFS.Layers}}'
done | tee evidence/unit-03/lab-03/image-layer-comparison.txt
sha256sum service/Dockerfile.lab service/requirements.lock \
  | tee evidence/unit-03/lab-03/input-hashes.txt
```

**EXPECTED / REPRESENTATIVE:** two build logs and one image/layer comparison record. A successful build is not guaranteed until the placeholder is replaced and the dependency lock matches the environment.

Use this result table and populate every result value from your own commands:

| Attempt | Changed variable | Image digest/ID | Layer/filesystem observation | Result | Interpretation | Remaining uncertainty |
|---|---|---|---|---|---|---|
| A | Baseline inputs | `[MEASURE YOURS]` | `[MEASURE YOURS]` | `[MEASURE YOURS]` | First baseline | Tool/network state may be incompletely captured |
| B | No intentional change | `[MEASURE YOURS]` | `[MEASURE YOURS]` | `[MEASURE YOURS]` | Tests repeatability for this setup | Two runs do not prove universal reproducibility |
| C | One controlled build argument | `[MEASURE YOURS]` | `[MEASURE YOURS]` | `[MEASURE YOURS]` | Shows effect of declared input | Does not prove an uncontrolled source caused drift |
| D | One normalization/intervention, if justified | `[MEASURE YOURS]` | `[MEASURE YOURS]` | `[MEASURE YOURS]` | Record whether suspected difference disappeared | Upstream tools may retain other differences |

**Final conclusion must answer four separate questions:** Were the OCI image objects byte-identical? Were extracted files equivalent under a defined comparison? Did dependency resolution repeat under the recorded lock and platform? Was provenance emitted and verified under an explicit trust policy? Do not use one “yes” to answer the others.

**Cleanup:** first inspect resources. Remove only the two lab tags if they were created by this lab:

```bash
docker image inspect unit03-rebuild-a:local unit03-rebuild-b:local
docker image rm unit03-rebuild-a:local unit03-rebuild-b:local
docker ps -a --filter name=unit03-lab
```

`docker image rm` removes those named local image references; it does not remove unrelated images. If an image is shared or tagged elsewhere, inspect before removal. **Verification:** the two lab tags should no longer be returned by `docker image inspect`; containers created by the lab should not remain. Preserve logs and result table.

#### Lab 4 — Compare config, layers, and extracted files

**Goal:** demonstrate why image digest inequality is a detector, not a diagnosis.  
**Prerequisites:** two local images from Lab 3.  
**Steps:** compare image IDs and layer arrays; inspect config fields; optionally use a documented OCI comparison tool. If extracting, use unique directories under `evidence/unit-03/lab-04/tmp/`, hash file contents, and compare path/mode/owner/time separately. Do not treat timestamps as content changes without recording the comparison policy.  
**EXPECTED / REPRESENTATIVE:** a comparison report showing which layer/config/file properties differ. Actual findings are learner-generated.  
**Evidence:** command output, comparison script, and short diagnosis.  
**Cleanup:** **⚠ DESTRUCTIVE:** remove only the lab's temporary extraction directories after confirming evidence has been copied outside them. Safer inspection first: `find evidence/unit-03/lab-04/tmp -maxdepth 2 -print`. Then `rm -rf -- evidence/unit-03/lab-04/tmp` only after verifying the exact path. Verify the directory is absent and no lab containers remain.  
**Stretch:** explain whether equality was byte-level, metadata-level, or content-level.

#### Lab 5 — Offline-input rehearsal and decision record

**Goal:** understand what must be vendored and define an honest policy.  
**Prerequisites:** a working service and package lock; no paid services.  
**Steps:** inventory Python wheels/source archives and build requirements; list required OS packages and base image; copy verified artifacts into a dedicated local input directory or controlled local mirror. If testing network isolation, use a disposable environment and document the mechanism; do not alter global firewall settings. Confirm integrity checks remain enabled.  
**EXPECTED / REPRESENTATIVE:** an input inventory and a list of missing inputs if the offline build cannot complete. Do not claim an offline build passed unless it actually did.  
**Evidence:** vendored-input manifest, checksums, test log, and a decision record.  
**Cleanup:** remove only lab-specific temporary input copies after preserving the manifest; verify no lab containers remain. Retain artifacts required by the team's offline retention policy.  
**Stretch:** define how the mirror is updated during an emergency security patch.

### 3.11 Self-check questions

1. **Why does `FROM python:3.12` not guarantee the same image next month?**  
   **Answer:** the tag can point to a different image, and other inputs such as package repositories and dependencies may change.

2. **What does a SHA-256 image digest prove?**  
   **Answer:** it identifies the specific content object represented by that digest. It does not prove safety, publisher trust, or provenance correctness.

3. **Why compare the same platform?**  
   **Answer:** platform-specific manifests, wheels, and native compilation can legitimately differ between architectures.

4. **Does `pip install --require-hashes` pin the Debian package set?**  
   **Answer:** no. It checks accepted Python distribution hashes covered by the requirements; OS packages and other build inputs need separate controls.

5. **A and B have different image IDs but identical file contents. Is the image reproducible?**  
   **Answer:** not byte-identical at the inspected image-object level. It may be filesystem-equivalent under the comparison performed. State the target explicitly.

6. **Why is an offline build not necessarily hermetic or deterministic?**  
   **Answer:** it may still read undeclared local state or create random/timestamp-dependent output; offline only constrains network access.

7. **What does an SBOM establish?**  
   **Answer:** it provides a component inventory according to its generation method. It does not prove completeness or absence of vulnerabilities.

8. **Why is an attestation not automatically trusted?**  
   **Answer:** its producer, identity, binding to the artifact, and claims must be verified against a trust policy.

9. **What is the danger of pinning dependencies but never updating them?**  
   **Answer:** builds may remain repeatable while retaining vulnerable or unsupported dependencies. Pinning requires a freshness and emergency-update policy.

10. **What can one successful two-build comparison legitimately claim?**  
    **Answer:** only that the selected outputs matched or differed for those runs under the recorded conditions and comparison method—not a universal guarantee.

### 3.12 Evidence artifacts

Use a dedicated directory and preserve evidence separately from transient build outputs:

```text
evidence/unit-03/
├── l1/
│   ├── observed-at.txt
│   ├── python-tag-inspection.txt
│   ├── docker-version.txt
│   └── buildx-version.txt
├── l2/
│   ├── input-hashes.txt
│   ├── build.log
│   └── image-id.txt
├── lab-01/
│   ├── source-commit.txt
│   ├── git-status.txt
│   ├── docker-version.txt
│   ├── buildx-version.txt
│   └── input-hashes.txt
├── lab-03/
│   ├── build-a.log
│   ├── build-b.log
│   ├── image-layer-comparison.txt
│   ├── input-hashes.txt
│   ├── result-table.md
│   └── unresolved-differences.md
├── lab-04/
│   └── comparison-report.md
├── lab-05/
│   ├── vendored-input-manifest.txt
│   └── offline-test.log
└── decision-record.md
```

Include, when applicable, image/manifest/layer digests, lockfile and Dockerfile hashes, build logs, package inventory, SBOM, provenance/attestation payload and verification result, comparison report, unresolved differences, and reviewer decision. Redact credentials and private registry tokens. Evidence itself is a supply-chain artifact and should have access controls and retention rules.

### 3.13 Common interview and design-review questions

1. **How do you define reproducibility for a production container?**  
   **Model answer:** I first define the object and equality level: index/manifest bytes, image config and layers, or extracted filesystem semantics. I record source, context, base digest, dependency locks, OS repository state, builder, platform, arguments, and timestamps. Then I build twice in equivalent clean conditions, compare the chosen object, and retain differences and residual uncertainty. I do not claim a universal guarantee from one pair of builds.

2. **A rebuild has a different digest, but application tests pass. Can you ship it?**  
   **Model answer:** Passing tests establishes behavioral evidence, not artifact equality. I would freeze promotion, compare source and input records, inspect manifest/config/layers, and identify whether the difference is expected metadata, a dependency change, or an unexplained change. The release policy decides whether semantic equivalence is sufficient; critical services may require byte-level verification or an approved exception.

3. **Why are digest pinning and package hashes not enough?**  
   **Model answer:** They constrain particular objects and downloaded Python artifacts. They do not automatically pin OS repository state, compiler/toolchain, build backend, network-fetched build requirements, platform, timestamps, or generated metadata. They also do not establish that the pinned content is safe. Repository trust, review, provenance verification, vulnerability management, and updates remain separate controls.

4. **What does BuildKit provenance add, and how would you trust it?**  
   **Model answer:** Depending on version and configuration, it can emit metadata about the build invocation, builder, source, and materials. I verify the exact supported output mode, inspect the payload, establish artifact binding, and enforce expected builder/source identities. An emitted statement is not self-authenticating proof; trust depends on producer identity and verification policy.

5. **Would you require byte-for-byte reproducibility for every service?**  
   **Model answer:** No. I would set a risk-based target. A critical or regulated artifact may justify byte-level reproduction and controlled toolchains. For other services, pinned inputs, repeatable dependency resolution, semantic filesystem comparison, and a strong release record may be a pragmatic interim target. I would make the target measurable, monitor patch latency, time-bound exceptions, and avoid absolute guarantees unsupported by evidence.

### 3.14 Sources and verification notes

This lesson was authored from the supplied requirements; live web browsing and local lab execution were not performed. The following official references are the verification starting points. Check current documentation and installed versions before adopting version-sensitive behavior.

- Docker documentation, **Dockerfile reference** — `FROM`, `ARG`, `ENV`, `COPY`, build context, and related instruction semantics: https://docs.docker.com/reference/dockerfile/
- Docker documentation, **Build and push your image** and build documentation: https://docs.docker.com/build/
- Docker Buildx documentation, **Build command**, **Build outputs**, **Build attestations**, and **Multi-platform builds**: https://docs.docker.com/reference/cli/docker/buildx/
- OCI Image Specification — image index, manifest, config, and layer model: https://github.com/opencontainers/image-spec
- OCI Distribution Specification — registry content and digest-related distribution concepts: https://github.com/opencontainers/distribution-spec
- pip documentation, **Secure installs** and requirements-file reference: https://pip.pypa.io/en/stable/topics/secure-installs/ and https://pip.pypa.io/en/stable/reference/requirements-file-format/
- pip-tools documentation, `pip-compile` and hash generation: https://pip-tools.readthedocs.io/
- uv documentation, **Projects**, lockfile, and sync behavior: https://docs.astral.sh/uv/
- Debian APT documentation and `snapshot.debian.org`: https://www.debian.org/doc/manuals/apt-guide/ and https://snapshot.debian.org/
- Reproducible Builds, `SOURCE_DATE_EPOCH` documentation: https://reproducible-builds.org/docs/source-date-epoch/
- SLSA specification and provenance model: https://slsa.dev/
- Syft documentation for SBOM generation: https://github.com/anchore/syft
- Trivy documentation for relevant image/SBOM evidence: https://trivy.dev/

Items that must be verified before production use are enumerated in Appendix C. In particular, check exact support and syntax for `--output type=oci,rewrite-timestamp=true`, `--provenance`, and `--sbom`; do not assume a flag is available in the installed buildx/BuildKit version or supported by every driver/exporter.

---

## Appendix A — Claim Register

| ID | Section | Claim | Source (official document + section) | Confidence (High/Medium/Low) | Tag ([VERIFY]/[VERSION-SENSITIVE]/none) | Verification action |
|---|---|---|---|---|---|---|
| A01 | 3.2 | Tags are references that may be retargeted; record a digest for exact content identity. | Docker Build documentation; OCI Image Specification | High | none | Inspect a registry reference and record object type |
| A02 | 3.2 | A digest identifies a content object but does not establish safety or publisher trust. | OCI Image Specification; SLSA provenance model | High | none | Review trust policy separately from digest |
| A03 | 3.2 | An image index can reference platform-specific manifests. | OCI Image Specification, Image Index | High | none | Inspect multi-platform output with buildx |
| A04 | 3.3 | The same Dockerfile can yield different outputs when external inputs move. | Dockerfile reference; Docker build documentation | High | none | Compare recorded input manifests |
| A05 | 3.4 | Base images can be referenced using a digest-qualified reference. | Dockerfile reference, `FROM` | High | none | Validate syntax against intended registry reference |
| A06 | 3.4 | A digest should be resolved from the intended publisher/object, not invented. | Docker Buildx `imagetools inspect` documentation | High | none | Capture current inspection output |
| A07 | 3.4 | `pip-compile --generate-hashes` can generate a hash-enabled requirements lock. | pip-tools documentation, `pip-compile` | High | [VERIFY] | Confirm options against installed pip-tools version |
| A08 | 3.4 | `pip install --require-hashes` enforces hashes for requirements covered by hash-checking mode. | pip documentation, Secure installs | High | [VERIFY] | Test a valid lock and an intentionally missing hash in a disposable environment |
| A09 | 3.4 | Python hashes do not automatically pin OS packages or all build tools. | pip Secure installs; Debian APT docs | High | none | Check input inventory covers each ecosystem |
| A10 | 3.4 | `uv.lock` semantics are not interchangeable by assumption with pip requirements files. | uv project/lockfile documentation; pip requirements reference | High | [VERIFY] | Document exact export/sync workflow and version |
| A11 | 3.4 | Debian snapshot repositories can expose historical repository states. | snapshot.debian.org documentation | High | [VERIFY] | Check suite, retention, metadata and signature requirements |
| A12 | 3.4 | Repository signature checks should not be disabled to force an install. | Debian APT documentation | High | none | Review APT configuration and failure behavior |
| A13 | 3.5 | `SOURCE_DATE_EPOCH` is a convention supported by participating tools, not a universal normalizer. | Reproducible Builds, SOURCE_DATE_EPOCH | High | none | Identify which tools honor it |
| A14 | 3.5 | `rewrite-timestamp=true` support depends on current BuildKit/buildx output support. | Docker Buildx build-output docs; BuildKit docs | Medium | [VERIFY]/[VERSION-SENSITIVE] | Check exact installed versions, output type and driver |
| A15 | 3.5 | Image digest inequality detects a difference but does not diagnose its cause. | OCI Image Specification; Docker image inspect docs | High | none | Inspect config, manifest, layers and files |
| A16 | 3.5 | Layer diff IDs and compressed blob digests are different concepts. | OCI Image Specification, Image Manifest and Layer Descriptors | High | [VERIFY] | Compare descriptor digest with local RootFS diff IDs |
| A17 | 3.5 | Platform-specific native wheels and compilation can vary by architecture and ABI. | Python packaging documentation; wheel/platform compatibility docs | High | [VERIFY] | Inspect selected artifacts for each target platform |
| A18 | 3.5 | Python build isolation may introduce build-system dependencies separate from runtime dependencies. | pip documentation, Build System Interface | High | [VERIFY] | Inspect pyproject build-system requirements and pip behavior |
| A19 | 3.6 | Offline builds can still vary due to timestamps, random data, or toolchain behavior. | Reproducible Builds documentation | High | none | Run offline builds twice and compare |
| A20 | 3.6 | Vendored artifacts should retain integrity checks and a reviewed update lifecycle. | pip Secure installs; Debian APT docs | High | none | Verify artifacts and test update procedure |
| A21 | 3.6 | Bazel and Nix provide different approaches to build/input control and are not equivalent. | Official Bazel documentation; Nix manual | Medium | [VERIFY] | Review tool docs for project-specific fit |
| A22 | 3.6 | Buildx provenance support and output behavior are version/configuration sensitive. | Docker Buildx, Build attestations | Medium | [VERIFY]/[VERSION-SENSITIVE] | Test the exact flag and inspect emitted metadata |
| A23 | 3.6 | Buildx SBOM support and output behavior are version/configuration sensitive. | Docker Buildx, Build attestations | Medium | [VERIFY]/[VERSION-SENSITIVE] | Test exact syntax and locate SBOM output |
| A24 | 3.6 | An attestation's presence does not make its claims trustworthy without verification. | SLSA provenance model | High | none | Verify identity, binding, source and policy |
| A25 | 3.6 | An SBOM is an inventory, not a guarantee of vulnerability-free content. | Syft docs; Trivy SBOM docs | High | none | Review generation method and scan separately |
| A26 | 3.6 | Dependency update automation should preserve pins while producing reviewable changes. | Renovate documentation; Dependabot documentation | High | [VERIFY] | Configure a test PR workflow and review policy |
| A27 | 3.6 | A two-build comparison proves equality only for the tested conditions and object. | OCI Image Specification; reproducible-builds.org | High | none | State exact object, conditions, and attempt count |
| A28 | 3.7 | Rebuild pass rate alone can hide stale vulnerable dependencies. | Operational inference from reproducibility and update controls | High | none | Pair reproducibility metric with freshness/patch latency |
| A29 | 3.8 | Digest pinning and hash checks are complementary, not complete security guarantees. | OCI Image Specification; pip Secure installs; SLSA | High | none | Threat-model remaining trust boundaries |
| A30 | 3.8 | Build secrets should not be placed in Dockerfile `ARG`/`ENV` or logs. | Docker build secrets documentation | High | [VERIFY] | Review current BuildKit secret-mount guidance |
| A31 | 3.10 | Build results must be learner-generated rather than fabricated. | Unit lab evidence policy | High | none | Inspect raw logs and result table |
| A32 | 3.14 | Exact flags and support for `--provenance`/`--sbom` require current documentation verification. | Docker Buildx build command and attestations docs | High | [VERIFY]/[VERSION-SENSITIVE] | Run `docker buildx build --help` and consult docs |
| A33 | 3.14 | Registry output can affect where image and attestation metadata are stored. | Docker Buildx build outputs and attestations docs | Medium | [VERIFY] | Test the intended exporter/registry |
| A34 | 3.14 | Snapshot availability and retention should not be assumed indefinite. | snapshot.debian.org documentation | Medium | [VERIFY] | Confirm archive availability and retention terms |

## Appendix B — Ten-Pass Audit Report

This is an AI self-review, not an independent external audit. The roadmap tree and syllabus source were not available for direct cross-checking in this context, and no commands or labs were executed during authoring.

| Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|
| 1 — Completeness | FIXED | Required sections and appendices needed explicit coverage | Included sections 3.0–3.14 and Appendices A–E; included four levels and mandatory drift lab | Syllabus source tree not independently checked |
| 2 — Technical accuracy | OPEN | Several tool behaviors depend on installed versions and exporter/driver | Added explicit verification markers and conservative examples | Human must validate exact CLI behavior |
| 3 — Executability | OPEN | Digest placeholder prevents copy/paste build until replaced; lab assumes project files and tools exist | Clearly marked placeholder and preconditions; commands are scoped | No code blocks were executed; syntax/path issues may remain |
| 4 — Currency | FIXED | Buildx timestamp/provenance/SBOM options can change | Added `[VERIFY]` and `[VERSION-SENSITIVE]` notes and official docs | Current support not live-checked |
| 5 — Security correctness | FIXED | Risk of overstating digest, hash, SBOM, and provenance controls | Separated identity, integrity, trust, inventory, and verification | Organization-specific policy remains to be defined |
| 6 — Fabrication scan | PASS | Example outputs could be mistaken for measured results | Labeled representative outputs; no real digests/results included | Human should verify all learner-populated evidence |
| 7 — Pedagogical consistency | FIXED | Terms can be confused across levels | Added glossary and progressive input-control/diagnosis workflow | Some advanced tool details are intentionally brief |
| 8 — Cross-consistency | FIXED | Labs, checklist, objectives and evidence could drift | Cross-linked objective topics, labs, checklist, and artifacts | Human should confirm file names align with repository |
| 9 — Adversarial SRE review | OPEN | Staff engineer could challenge untested CLI syntax, incomplete context hashing, or undefined equality target | Added input inventory, result classification, runbook, and explicit limitations | See objections below; several require live tests |
| 10 — Reproducibility/resource review | OPEN | Actual disk/network use and cleanup behavior are environment-specific | Kept labs local, scoped cleanup, avoided global prune, required inspection | Resource use and idempotency need execution on target laptop |

**Ten likely staff-engineer objections and disposition**

1. **“A source commit is not the whole build context.”** Addressed by requiring context inventory, dirty-state capture, `.dockerignore`, and generated/untracked file review. Residual: exact context hashing procedure must be implemented by the learner.
2. **“You compare local image IDs but call them digests.”** Addressed by distinguishing local image ID/config digest, layer diff IDs, manifest digest, and index digest. Residual: commands must be selected for the object the policy targets.
3. **“The placeholder Dockerfile cannot build.”** Intentional safety measure; replace only with a verified digest. No plausible-looking digest is fabricated.
4. **“Two builds are not statistical proof.”** Addressed: the result is bounded to the tested conditions and attempts.
5. **“`SOURCE_DATE_EPOCH` is not magic.”** Addressed: only participating tools honor the convention.
6. **“Buildx flags change by version and exporter.”** Addressed with verification markers; live verification remains open.
7. **“Hash-locked requirements do not pin native build environments.”** Addressed through build isolation, toolchain, ABI, and OS package discussion.
8. **“Offline does not mean hermetic.”** Addressed through declared-input and ambient-state distinction.
9. **“Provenance can be generated by an untrusted builder.”** Addressed through identity, artifact binding, and trust-policy verification.
10. **“Reproducibility can delay security updates.”** Addressed through scheduled/emergency updates, freshness metrics, rollback, and expiring exceptions.

## Appendix C — Human Verification Checklist

### Docker / OCI

- [ ] **Digest and object terminology:** confirm the intended image reference resolves to an index or platform manifest as expected. Official docs: OCI Image Specification, Image Index and Image Manifest; Docker Buildx `imagetools inspect`. Local check: `docker buildx imagetools inspect <reference>`.
- [ ] **Build context:** verify the actual context sent to the builder, including `.dockerignore` behavior and generated files. Official doc: Docker build context documentation. Local check: inspect build logs and compare a sorted file/hash manifest.
- [ ] **Image config and layers:** confirm local `docker image inspect` fields used in evidence are interpreted correctly. Official doc: Docker CLI `image inspect`; OCI Image Specification. Local check: inspect `.Id` and `.RootFS.Layers`, and do not label these as the remote index digest.

### BuildKit / buildx

- [ ] **`--output type=oci,rewrite-timestamp=true`:** **[VERIFY] [VERSION-SENSITIVE]** check exact support, spelling, exporter and driver behavior in Docker Buildx build-output and BuildKit docs. Local check: `docker buildx build --help`; use a disposable test build only after confirming the installed docs.
- [ ] **`--provenance`:** **[VERIFY] [VERSION-SENSITIVE]** check supported values, default behavior, output mode, and where attestations are stored. Official doc: Docker Buildx, Build attestations. Local check: `docker buildx build --help` and inspect the emitted artifact/attestation.
- [ ] **`--sbom`:** **[VERIFY] [VERSION-SENSITIVE]** check exact syntax and storage behavior for the selected driver/exporter. Official doc: Docker Buildx, Build attestations. Local check: run a disposable build and confirm the SBOM can be retrieved.
- [ ] **Builder identity:** record builder driver and version. Official doc: Docker Buildx builders. Local check: `docker buildx ls` and `docker buildx inspect`.

### Python packaging

- [ ] **`pip-compile --generate-hashes`:** **[VERIFY]** confirm command options and output behavior for installed pip-tools. Official doc: pip-tools `pip-compile`. Local check: `pip-compile --help`.
- [ ] **`pip install --require-hashes`:** **[VERIFY]** confirm lock completeness and hash behavior. Official doc: pip Secure installs. Local check: test a valid lock in a disposable environment and confirm an altered/missing hash fails.
- [ ] **Build isolation:** **[VERIFY]** inspect the package's build-system requirements and whether source builds create additional inputs. Official doc: pip build system interface. Local check: inspect `pyproject.toml` and build logs.
- [ ] **uv lock semantics:** **[VERIFY]** confirm the intended `uv.lock`/sync/export flow for the selected version. Official doc: uv project/lockfile documentation. Local check: `uv --help` and the relevant subcommand help.

### Debian / APT snapshots

- [ ] **Snapshot suite and timestamp:** **[VERIFY]** confirm suite, component, archive URL, package availability, and repository metadata for the intended build. Official doc: snapshot.debian.org and Debian APT guide. Local check: inspect APT sources and run package metadata refresh with signature verification enabled.
- [ ] **Retention and signing:** **[VERIFY]** confirm current availability and signing metadata behavior. Do not disable signature validation as a workaround.

### Provenance / SLSA

- [ ] **Provenance fields and trust:** **[VERIFY]** inspect source, builder, invocation parameters, and materials. Official docs: Docker Build attestations and SLSA provenance. Local check: retrieve and parse the emitted statement, then validate it against a written trust policy.
- [ ] **Artifact binding:** **[VERIFY]** ensure the attestation refers to the artifact being promoted, not a different tag/build. Local check: compare subject digest with the exact artifact digest.
- [ ] **SBOM coverage:** **[VERIFY]** confirm how the chosen generator detects packages and what it may miss. Official docs: Syft and Trivy. Local check: compare SBOM output with lockfiles and OS package inventory.

### Comparison tooling

- [ ] **diffoci/container-diff:** **[VERIFY]** check official usage for the exact tool version and output type. If unavailable, use Docker/OCI inspection and a documented extraction/hash comparison.
- [ ] **Equality policy:** write down whether the release gate requires identical index digest, platform manifest/config/layers, or extracted filesystem semantics. Confirm the comparison actually measures that target.
- [ ] **WSL2/native Linux:** record Docker Desktop/WSL integration, filesystem location, target platform, and builder. Confirm builds are compared under equivalent conditions.

## Appendix D — Known Limitations and Assumptions

- The supplied prompt was available, but the repository roadmap tree and the named syllabus-authority file were not directly available for inspection in this authoring context. The lesson therefore follows the detailed requirements in the supplied prompt and does not claim independent repository conformance.
- Live browsing of official documentation was not performed. URLs are included as canonical starting points where known; exact current behavior must be verified.
- No lab commands, builds, image inspections, scans, SBOM generation, or provenance verification were executed while authoring. All output examples are representative, and all result-table values must be generated by the learner.
- The target baseline assumes Docker/BuildKit/buildx and network access for initial acquisition. WSL2 may add filesystem performance, path/line-ending, Docker Desktop integration, and architecture considerations. Prefer a Linux filesystem location for build contexts when using WSL2, and record the actual builder and target platform.
- The base digest placeholder is deliberately non-executable. Do not replace it with an unverified or guessed digest.
- Python and Debian image reproducibility can remain limited by upstream wheel availability, native compilation, timestamps, repository metadata, toolchain versions, build isolation, architecture, generated metadata, and nondeterministic build backends.
- Exact support for timestamp rewriting, provenance, and SBOM flags is version-sensitive and must be checked for the installed Buildx/BuildKit, builder driver, exporter, and registry/output mode.
- Optional comparison tools are not required. A manual inspection fallback is included, but the exact extraction workflow should be tested and scoped before use.
- This lesson does not replace base-image selection guidance (Unit 2), build caching/performance guidance (Unit 4), tag immutability/promotion policy (Unit 5), CI implementation (M02), Kubernetes operations (M03), secrets management (M09), or supply-chain signing/policy deep dives (M12).

## Appendix E — Sign-off

**Content status: DRAFT-AUDITED | Audit date: 2026-10-24 | Auditor role: AI self-audit (requires human verification) | Open verification items: 15**

AI self-audit does not replace running the labs, validating command behavior in the target environment, checking current official documentation, or having a human reviewer confirm repository-specific paths and policy. The open verification count is a working estimate of grouped verification items in Appendix C; it should be updated after each item is checked.
