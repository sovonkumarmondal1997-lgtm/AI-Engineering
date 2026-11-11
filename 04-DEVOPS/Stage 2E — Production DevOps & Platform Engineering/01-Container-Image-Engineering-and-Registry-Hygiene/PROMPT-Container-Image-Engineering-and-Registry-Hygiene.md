# PROMPT — Generate `SYLLABUS-Container-Image-Engineering-and-Registry-Hygiene.md`

> Paste everything below the line `=== BEGIN PROMPT ===` into a capable LLM. Because the output is very large, use the **Delivery Protocol** (Section 14), which generates it in numbered parts and then concatenates them into one file.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior DevOps Engineer and SRE with 15 years of production experience** running container platforms for data-intensive organizations. You have been on call for registry outages, rebuilt images after supply-chain incidents, cut CI build times from 40 minutes to 4, and mentored engineers from junior to senior. You teach the way you work: **evidence over opinion, reproducibility over cleverness, and every claim verifiable.**

You are also a careful technical author. You never invent a flag, a field, a default, or a version. When unsure, you say so and mark it `[VERIFY]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 2E — Production DevOps & Platform Engineering / 01-Container-Image-Engineering-and-Registry-Hygiene/` (module code **M01**)

Output file name: **`SYLLABUS-Container-Image-Engineering-and-Registry-Hygiene.md`**

It must teach, **one after another, from beginner to advanced**, these 12 units in this exact order. Each unit maps to a file that will later be written from this syllabus:

| # | Unit | Target file |
|---|---|---|
| 0 | Folder orientation | `README.md` |
| 1 | Multi-stage builds and layer optimization | `01-multi-stage-builds-and-layer-optimization.md` |
| 2 | Minimal and distroless base images | `02-minimal-and-distroless-base-images.md` |
| 3 | Reproducible and deterministic image builds | `03-reproducible-and-deterministic-image-builds.md` |
| 4 | Build caching, BuildKit, and build performance | `04-build-caching-buildkit-and-build-performance.md` |
| 5 | Image tagging, versioning, and immutability | `05-image-tagging-versioning-and-immutability.md` |
| 6 | Container registries, mirrors, and pull-through caches | `06-container-registries-mirrors-and-pull-through-caches.md` |
| 7 | Registry retention, garbage collection, and access control | `07-registry-retention-garbage-collection-and-access-control.md` |
| 8 | Non-root containers and runtime defaults | `08-non-root-containers-and-runtime-defaults.md` |
| 9 | Practice questions | `practice-questions.md` |
| 10 | Capstone project | `Projects/README.md` + `Projects/01-hardened-optimized-image-pipeline-for-data-services.md` |

Do **not** add, merge, skip, or reorder units. Do not produce shallow summaries: this is the **teaching content itself**, not an outline of it.

# 3. LEARNER AND CONTEXT

- **Learner:** a data/AI engineer who has finished Stages 0–2D (Python, data engineering, data architecture). They can build and run a basic container, use Git, a Linux shell, and read Python. They have **not** operated production container platforms.
- **Stage constraint — zero budget.** All hands-on work must run on a **local laptop** (WSL2 Ubuntu primary, native Linux secondary): ~4 CPU cores, 8 GB RAM, 30 GB disk. No paid cloud, no paid registry, no paid scanner. Use free/local tools only.
- **Core tools** (hands-on, required): OCI image format, Docker Engine/CLI, **BuildKit / `docker buildx`**, a **local registry** (`registry:2` / CNCF Distribution), **Trivy** (scanning), **Syft** (SBOM).
- **Awareness tools** (explain and compare, no operation required): `cosign`/Sigstore, hosted registries (Docker Hub, GHCR, ECR, GCR/Artifact Registry, ACR, Harbor), Podman, Buildah, Kaniko, ko, Jib, Bazel `rules_oci`, Nix, Grype, Dive, Hadolint (Hadolint and Dive may be used as optional helpers, flagged as such).
- **Domain flavor:** examples should come from **data services**: a Python FastAPI inference/API service, a Python batch ETL job (pandas/pyarrow), an Airflow-style worker, a PySpark job image, and a small Go or Java sidecar/CLI for contrast. Avoid toy "hello world" examples after Level 1.
- **Cross-module links:** point forward to M02 (CI/CD), M03 (Kubernetes ops), M08 (GitOps), M09 (secrets), M12 (supply-chain security), M13 (backup/DR). State clearly what is **taught here vs. deferred** so no topic is half-covered.

# 4. TEACHING MODEL — THE FOUR LEVELS (APPLY TO UNITS 1–8)

Every unit 1–8 progresses through **exactly these four levels**, each building on the last. Use the same headings in every unit.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Explains the concept, runs the basic command, reads the output. |
| **L2** | Intermediate — Working Practice | Applies it to a real data service; uses standard patterns and avoids common mistakes. |
| **L3** | Advanced — Production Engineering | Designs, measures, and defends choices under constraints (size, speed, security, cost, reliability). |
| **L4** | Expert — Operating at Scale and Under Failure | Diagnoses failures, writes policy/automation, reasons about trade-offs for a team or organization. |

# 5. MANDATORY STRUCTURE FOR EACH UNIT 1–8

Use this exact skeleton, in this order, for every module. Do not omit a section; if a section is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Awareness:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in production
(3–6 sentences. A concrete incident or cost/risk this prevents. No hype.)

### N.1 Learning objectives
(6–10 measurable outcomes, each starting with an action verb: build, measure, diagnose, justify…
Tag each with its level L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception.)
(One text diagram or mermaid diagram of the mechanism.)

### N.3 Level 1 — Beginner
- Explanation from first principles (how it works internally, not just what to type)
- Guided lab with exact commands, expected output, and how to read it
- "What just happened?" walkthrough
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Real data-service example (complete, runnable files)
- Pattern catalogue: pattern | when to use | when NOT to use
- Anti-pattern catalogue: bad example → why it hurts → corrected version
- Lab with measurable before/after numbers

### N.5 Level 3 — Advanced
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Hardening, performance, and reliability techniques
- Measurement method (what to measure, with which command, how to avoid fooling yourself)
- Lab that requires a defended decision, not just a copied command

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Policy-as-code or automation (scripts, lint rules, CI checks, admission/registry policy sketches)
- Organizational concerns: standards, review checklists, ownership, migration strategy
- Edge cases and platform differences (WSL2, rootless Docker, architectures)

### N.7 SRE lens
- SLIs/SLOs relevant to this topic (e.g., image pull success rate, p95 build time)
- Failure modes and blast radius
- Runbook snippet: alert → triage → mitigation → follow-up
- Cost and capacity notes

### N.8 Security lens
- Threats addressed (map to STRIDE or supply-chain stages), with what is NOT addressed
- Controls and how to verify each with a command

### N.9 Production checklist
(Checkbox list the learner can apply to a real repository. Every item is verifiable.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | **expected evidence** | **cleanup** | stretch goal.
Labs must be idempotent and safe to re-run.)

### N.11 Self-check questions
(6–10 questions with concise answer keys and a "why the wrong answers are tempting" note for MCQs.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves under this module to prove completion.)

### N.13 Common interview and design-review questions
(5 questions with senior-level model answers.)

### N.14 Sources and verification notes
(Official docs consulted by name and section; items tagged [VERIFY]; version-sensitive claims.)
```

# 6. MODULE-SPECIFIC CONTENT REQUIREMENTS

The following topics are the **minimum**. Add depth, never remove. Place each topic at the level indicated.

## Unit 1 — Multi-stage builds and layer optimization
- **L1:** image vs container; layers, the union filesystem, image config, manifest; `docker history`, `docker image inspect`; why every `RUN`/`COPY`/`ADD` creates a layer; single-stage vs multi-stage; `FROM … AS`, `COPY --from`; `.dockerignore`.
- **L2:** builder/runtime split for Python (wheel build stage, virtualenv copy), Go (static binary), Java (JRE-only runtime); instruction ordering for cache friendliness; combining `RUN` steps; cleaning package caches *in the same layer*; `--no-install-recommends`; why deleting a file in a later layer does not shrink the image; `COPY` vs `ADD`; `ARG` vs `ENV` scope and leakage.
- **L3:** `--target` for test/dev/prod stages; a `deps` → `test` → `runtime` stage graph; build-time secrets with `RUN --mount=type=secret` (and why `ARG` secrets leak in `docker history`); `--mount=type=cache`; size-vs-debuggability trade-off; shrinking pyarrow/pandas/numpy images honestly (wheels vs source, `manylinux` vs musl pitfalls, `PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED`); analyzing layers with `dive` (optional) and with plain CLI.
- **L4:** layer-diff forensics ("why did this rebuild balloon by 400 MB?"); squash/flatten trade-offs; image-size budgets enforced in CI; Dockerfile lint policy (Hadolint rules, custom checks); multi-arch (`linux/amd64`, `linux/arm64`) stage design; stage-graph parallelism in BuildKit.
- **Must include:** a "Dockerfile review checklist" and a worked before/after of a naive 1.2 GB Python image reduced with a **reported, reproducible measurement table**. All numbers must come from stated commands the learner can run; label any number you did not measure as "illustrative — measure yours".

## Unit 2 — Minimal and distroless base images
- **L1:** what a base image contains; `scratch`, `busybox`, `alpine`, `debian-slim`, `ubuntu`, distroless, Wolfi/Chainguard-style minimal images; libc differences (glibc vs musl); attack surface vs usability.
- **L2:** selecting a base per workload (Python/Go/Java/Node); musl pitfalls with Python wheels, DNS and locale behavior; `-slim` vs distroless trade-offs; static vs dynamic linking and `ldd`; CA certificates, timezone data, and `/etc/passwd` needs in `scratch`.
- **L3:** distroless variants (static, base, cc, python3, java); `:debug` variants and the "no shell" operational reality; debugging without a shell (`docker debug`-style tooling, ephemeral containers in Kubernetes — forward reference to M03, `docker cp`, `nsenter` concept); comparing vulnerability counts between bases with Trivy **and explaining why counts are not a quality score** (database freshness, unfixed CVEs, VEX); license and provenance concerns of base images; base-image **update cadence** policy.
- **L4:** curated internal "golden base image" program: ownership, rebuild cadence, deprecation, SLA for CVE patch propagation, downstream rebuild triggers; build-your-own minimal rootfs (conceptual + small lab); FIPS/compliance considerations (Awareness); trade-off decision record (ADR template) for choosing a base.
- **Must include:** a comparison lab (same app on 4 bases) with size, scan result, startup time, debuggability, and a **written decision memo**.

## Unit 3 — Reproducible and deterministic image builds
- **L1:** what "reproducible" means vs "repeatable"; why `FROM python:3.12` and `apt-get install` drift; digests (`sha256:…`) vs tags.
- **L2:** pin base images by digest (with a human-readable tag comment); pin OS packages and Python dependencies (`pip-compile --generate-hashes` / `uv` lockfiles, `--require-hashes`); lockfile discipline; `apt` snapshot repositories (e.g., snapshot.debian.org) conceptually; avoiding `latest` and `curl | sh`.
- **L3:** `SOURCE_DATE_EPOCH`, timestamp normalization, file ordering, `--output type=oci,rewrite-timestamp=true` (verify current BuildKit support) `[VERIFY]`; comparing two builds with `diffoci`/`container-diff`-style tools or manual layer-digest comparison; sources of nondeterminism (timestamps, `.pyc`, `pip` build isolation, random temp paths, locale, uid/gid, tar ordering); the honest limits of reproducibility for Python/Debian images.
- **L4:** hermetic builds, vendoring, offline/air-gapped build design, Bazel/Nix as Awareness; **build provenance** (SLSA concepts, BuildKit `--provenance`, `--sbom`) with a clear statement of what is attested and what is not; automated dependency update strategy (Renovate/Dependabot as Awareness) that preserves pinning without becoming stale; a **rebuild-verification procedure** ("build twice, compare digests, record result").
- **Must include:** a lab that builds the same source twice, shows a differing digest, fixes sources of drift one by one, and reports which differences remain and why.

## Unit 4 — Build caching, BuildKit, and build performance
- **L1:** how Docker's layer cache decides hit/miss; cache invalidation rule (a changed instruction or input invalidates it and all later layers); `docker build --no-cache`; BuildKit vs the legacy builder; reading BuildKit progress output.
- **L2:** dependency-manifest-first ordering; `--mount=type=cache` for pip/apt/go/maven; `.dockerignore` effect on context size and cache; build context transfer cost; parallel stages.
- **L3:** `docker buildx` builders and drivers (`docker`, `docker-container`, `kubernetes`, `remote`); cache backends: `inline`, `registry`, `local`, `gha` (Awareness), `s3` (Awareness) — with exact `--cache-from/--cache-to` syntax and `mode=min|max` trade-offs `[VERIFY]` current syntax; measuring with `time`, `BUILDKIT_PROGRESS=plain`, and build-history tooling; cache-key pitfalls (`ARG` changes, `COPY . .`, timestamps, `git` metadata).
- **L4:** CI cache strategy across ephemeral runners (forward reference M02); cache poisoning and trust boundaries for shared caches; remote/shared builders and their security model; monorepo build graph design; multi-platform build performance (QEMU vs native nodes); defining a **build-time SLO** and a regression guard; garbage-collecting the builder cache (`docker buildx prune`, GC policy in `buildkitd.toml`).
- **Must include:** a benchmark harness (shell or Python script) that runs cold/warm/partial-change builds N times and prints a median/p95 table, plus guidance on avoiding benchmark errors (page cache, network variance, warm-up).

## Unit 5 — Image tagging, versioning, and immutability
- **L1:** repository, tag, digest, manifest, manifest list/image index; tags are mutable pointers; `docker pull repo@sha256:…`.
- **L2:** tagging schemes (SemVer, Git SHA, build number, date, environment tags) with pros/cons; why `latest` is an anti-pattern in deployment; multiple tags → one digest; `docker tag`/`push`/`inspect`; OCI labels (`org.opencontainers.image.*`) populated automatically from Git/CI.
- **L3:** **immutability** as a policy (registry-enforced tag immutability, promotion by digest rather than rebuild); promotion pipelines (dev → staging → prod) with digest pinning; multi-arch indexes and platform-specific digests; referrers/artifacts API for SBOM/signature attachment (concept; `cosign` as Awareness); how Kubernetes resolves tags and what `imagePullPolicy` does (link to M03).
- **L4:** rollback by digest; tag-drift detection and "tag moved" incident analysis; versioning strategy for a fleet of data-service images and shared base images; release-metadata contract (labels + SBOM + provenance + changelog); reproducibility link to Unit 3; automating tag policy as a CI check and a registry-side rule.
- **Must include:** a lab where a mutable tag is re-pushed, a "deployment" silently changes, and the learner then enforces digest-pinned deployment and detects the drift automatically.

## Unit 6 — Container registries, mirrors, and pull-through caches
- **L1:** what a registry is; OCI Distribution API in plain terms (blobs, manifests, tags/list, upload sessions); `docker login/push/pull`; credentials in `~/.docker/config.json` (and why plaintext is a risk; credential helpers).
- **L2:** run a local registry (`registry:2`) with persistent storage; push/pull; inspect with `curl` against `/v2/`; `insecure-registries` vs TLS (local CA, `mkcert`); hosted-registry landscape (Docker Hub, GHCR, ECR, Artifact Registry, ACR, Harbor, Quay) as a comparison table with **rate-limit/pricing statements marked `[VERIFY]`** — never present a limit as fact without tagging it.
- **L3:** **pull-through cache / mirror** configuration (`proxy.remoteurl` for the Distribution registry; daemon `registry-mirrors`; containerd `hosts.toml`) `[VERIFY]` current syntax; Docker Hub rate-limit mitigation; registry as a dependency: HA, failure modes, caching semantics, what happens when upstream or the mirror is down; air-gapped replication; multi-region distribution (concept); Kubernetes `imagePullSecrets` and node-level mirrors (forward reference M03/M09).
- **L4:** registry architecture for an organization (central vs per-team vs per-environment); mirror/proxy trust and poisoning risks; supply-chain gate at the registry (only approved upstreams; scan-on-push as Awareness via Harbor/Trivy); disaster recovery for a registry (forward reference M13); observability for registries (metrics, pull latency, error rates; forward reference M11); a **registry outage runbook**.
- **Must include:** a lab with a local registry + a pull-through cache, demonstrating cache hit/miss with registry logs and proving that an image remains pullable when upstream is made unreachable (simulated by blocking egress locally or stopping the upstream stand-in).

## Unit 7 — Registry retention, garbage collection, and access control
- **L1:** why registries grow without bound; what "untagged" and "dangling" mean; storage = blobs shared across manifests; reference counting.
- **L2:** retention policy design (keep last N, keep by age, keep released/promoted, keep anything referenced by a deployed digest); Distribution registry deletion API and `registry garbage-collect` (dry-run, read-only mode requirement, the risk of GC during pushes) `[VERIFY]`; local `docker system prune`/`image prune` semantics and risks.
- **L3:** safe GC procedure and ordering; "never delete what production references" — inventory of in-use digests; retention for compliance/forensics; tag-immutability interplay; cost modeling of storage and egress; authentication vs authorization (basic auth with `htpasswd`, token auth concept); **least-privilege roles** (pull-only for runtime, push for CI, delete for admins only); robot/service accounts; short-lived credentials (concept; OIDC federation as Awareness).
- **L4:** policy-as-code for retention and access; audit logging and "who pushed/deleted what" investigation; break-glass procedure; multi-tenant registry namespaces; vulnerability-driven retention (quarantine/blocked images); incident drill: "someone deleted a production image" → recover; lifecycle ADR template.
- **Must include:** a lab that populates a registry with synthetic images, applies a retention policy via a script (dry-run first, then real), runs GC, shows the reclaimed bytes, and proves a protected/in-use digest survived. Include a restore drill.

## Unit 8 — Non-root containers and runtime defaults
- **L1:** UID/GID, root in a container ≠ root on host (and why it is still dangerous); user namespaces concept; `USER` instruction; `id`, `ps`, `/proc/self/status` checks.
- **L2:** create a dedicated user/group with a fixed numeric UID; file ownership with `COPY --chown`; writable directories (`/tmp`, app cache) and read-only root filesystems; binding ports > 1024; fixing "permission denied" failures systematically; numeric `USER` for Kubernetes `runAsNonRoot` compatibility.
- **L3:** runtime hardening flags with `docker run`: `--read-only`, `--tmpfs`, `--cap-drop=ALL`, `--cap-add` only as needed, `--security-opt no-new-privileges`, `--pids-limit`, `--memory`, `--cpus`, default seccomp, AppArmor (concept); `HEALTHCHECK` design; signal handling and PID 1 (`tini`/`--init`, exec-form `CMD`, graceful `SIGTERM`); locale/timezone/umask defaults; rootless Docker/Podman as a different threat model; mapping the same defaults to Kubernetes `securityContext` (forward reference M03/M12) and Pod Security Standards (concept).
- **L4:** a hardening baseline as **policy-as-code** (e.g., a Conftest/OPA or script-based check against Dockerfiles/images: non-root, no `latest`, health check present, no secrets, labels present); verifying controls with an automated test suite (`docker inspect` assertions, run-as-user check, write-attempt-fails check); escape-class risks (privileged, host mounts, Docker socket mount) and detection; runtime defaults for data services that need write access (Spark scratch, Airflow logs, model caches) done safely; exception-handling process (documented, time-boxed).
- **Must include:** a "hardening conformance test" script the learner runs against any image, producing a pass/fail report with evidence.

# 7. PRACTICE QUESTIONS (Unit 9) — REQUIREMENTS

Generate a full `practice-questions.md` body with **at least 120 questions** across the eight modules plus ~15 cross-module integration questions. Required distribution per module (≥ 14 each):

- 4 × conceptual short-answer
- 3 × multiple choice (4 options; answer + explanation of every distractor)
- 3 × command/output interpretation ("Given this output, what is wrong?")
- 2 × Dockerfile/config review (find ≥ 3 defects and fix)
- 2 × incident/troubleshooting scenarios (symptom → diagnose → fix → prevent)
- (Modules 3–8) 1 × design question with a rubric

Every question carries: ID, level (L1–L4), objective it tests, time estimate, **model answer**, and **common wrong answers**. Include a difficulty progression and a scoring rubric with pass thresholds (80% proceed; 60–79% remediate; below 60% repeat), consistent with the stage's gate rules. Include 6 "whiteboard / design-review" prompts that require written trade-off reasoning.

# 8. CAPSTONE PROJECT (Unit 10) — REQUIREMENTS

**Project:** *Hardened, Optimized Image Pipeline for Data Services.*

Deliver both `Projects/README.md` (index, grading, how to submit evidence) and the full project specification.

**Scenario:** A data platform team ships three services — (a) FastAPI model-serving API, (b) pandas/pyarrow batch ETL job, (c) PySpark or Airflow-worker-style job image. Images are slow to build, 1 GB+, run as root, tagged `latest`, rebuilt non-deterministically, and pushed to an unmanaged registry that has run out of disk. The learner builds the pipeline that fixes this, locally and for free.

**Required deliverables (each with acceptance criteria that can be checked by command):**
1. Repository layout and a `Makefile` (or `justfile`) with targets: `lint`, `build`, `test`, `scan`, `sbom`, `size-check`, `repro-check`, `push`, `promote`, `gc`, `conformance`, `clean`, `all`.
2. Three optimized multi-stage Dockerfiles (Unit 1), minimal/distroless-or-slim runtime bases chosen with an ADR (Unit 2).
3. Pinned inputs by digest and hashed lockfiles; a `repro-check` that builds twice and compares (Unit 3).
4. BuildKit cache configuration and a benchmark report with cold/warm numbers and an SLO (Unit 4).
5. Tagging and promotion scheme: SemVer + Git SHA + digest promotion; OCI labels; drift-detection script (Unit 5).
6. Local registry + pull-through cache with TLS and basic auth, documented failure behavior (Unit 6).
7. Retention + GC script with dry-run, in-use protection, and a restore drill (Unit 7).
8. Non-root, read-only-rootfs, capability-dropped runtime defaults and an automated conformance suite (Unit 8).
9. Trivy scan gate and Syft SBOM per image, stored as artifacts, with a **severity threshold policy and a documented exception (VEX-style) file**; `cosign` signing described as an optional stretch.
10. A **CI workflow file** (GitHub Actions YAML, written but runnable locally via `act` as optional) that runs the same Make targets — kept as Awareness until M02, but syntactically valid.
11. Documentation: architecture diagram, ADRs (≥ 4), a runbook for 3 incident types (disk-full registry, tag drift, upstream rate-limit), and a one-page **production-readiness review** using the checklists from Units 1–8.
12. A **before/after results table** (image size, build time cold/warm, vulnerability counts by severity, run-as-user, reproducibility result) filled by the learner's own measurements. Provide the template; do not fabricate results.

**Include:** milestone plan (5–6 milestones with time estimates), a grading rubric (100 points, criterion-level descriptors for Poor/Adequate/Strong/Exemplary), stretch goals, common failure points, a self-review checklist, and the exact evidence folder structure.

**Provide complete, runnable starter code** for the three services (small but realistic), every Dockerfile, the Makefile, scripts, and config. Do not leave `TODO: implement` in required deliverables.

# 9. README ORIENTATION (Unit 0) — REQUIREMENTS

Include: purpose of the folder; who it is for; prerequisites (Gate In) mapped to the Stage 2E prerequisites; a **dependency graph of the 8 modules** and why the order matters; recommended pacing (e.g., 4-week and 8-week plans); tool matrix (Core vs Awareness, with install verification commands); lab-environment checklist (disk space, Docker version check, buildx available, ports used, cleanup commands); a **glossary**; a **module-to-exit-criteria mapping**; how evidence is stored; how to use the practice questions and project; a "how this connects to M02/M03/M08/M09/M12/M13" table.

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. **Every code block states its language** and, where relevant, its file path as a first-line comment (e.g., `# File: services/api/Dockerfile`).
2. **Every command is paired with expected output** (representative, clearly labeled as "example — yours will differ in digests/sizes/timings") and a short interpretation.
3. **Commands must be real.** Use only flags and syntax you are confident exist. If a flag, default, or behavior changed across Docker/BuildKit/Trivy/Syft/containerd versions, tag it `[VERIFY: <what to check and where>]`. Do not guess.
4. **No unpinned examples presented as best practice.** When an example must use a tag for readability, add a comment showing the digest-pinned form and why.
5. **No secrets in code.** Use obviously fake values (`example-password-do-not-use`). Demonstrate secret handling with `--mount=type=secret`.
6. **Label every destructive command** (`docker system prune`, registry deletion, `rm -rf`) with `⚠ DESTRUCTIVE`, state what it removes, and show a dry-run or inspection alternative first.
7. **Scripts must be safe by default:** `set -euo pipefail`, quoted variables, explicit exit codes, a `--dry-run` where deleting, idempotent where possible, ShellCheck-clean in style.
8. **Python code** must be typed where practical, minimal-dependency, with a test.
9. **Dockerfiles** must follow the standards taught (non-root, pinned, minimal, exec-form `CMD`, `HEALTHCHECK` where meaningful) unless the example is deliberately an anti-pattern — in which case it is labeled `# ANTI-PATTERN — DO NOT COPY` with the defect list.
10. **WSL2 notes:** call out WSL2/Docker Desktop vs native Docker differences where they affect a lab (filesystem performance, `/mnt/c`, resource limits).
11. **Every lab ends with cleanup commands** and a verification that no stray containers/volumes/registries remain.
12. **Every performance claim** (size reduction, speedup) is tied to a measurement command. Never state a specific improvement as a fact unless the learner can reproduce it; otherwise label it "typical range — measure yours".

# 11. PEDAGOGY RULES

- **Mechanism before recipe:** explain *why* it works, then show the command.
- **One new idea at a time** within a level; reuse prior examples so learners see the same app improve over the whole folder (a "running example" thread: naive → optimized → hardened → pipelined).
- **Show failure on purpose:** every unit has at least one lab where the learner breaks something and diagnoses it.
- **Prefer diagrams** (mermaid or ASCII) for layer stacks, cache invalidation, tag→digest→manifest relationships, registry request flow, and promotion pipelines.
- **Plain, precise English.** No filler, no marketing, no emoji decoration (⚠ and ✔ allowed only as markers). Define acronyms on first use.
- **Be honest about trade-offs.** No "always"/"never" without a stated reason and exceptions.
- Use consistent terms: *image*, *container*, *layer*, *manifest*, *digest*, *tag*, *registry*, *repository*.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You will act as author, then as an independent auditor of your own work, and you will include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base every technical claim on **official documentation or specifications**: Docker/BuildKit docs, OCI Image/Distribution/Runtime specs, CNCF Distribution docs, Trivy and Syft docs, containerd docs, Kubernetes docs (for forward references), Dockerfile reference, NIST SP 800-190 (container security), CIS Docker Benchmark, SLSA spec. Cite by **document name and section/title**, not by invented URLs. Provide a URL only if you are certain it is canonical; otherwise cite the document and mark `[VERIFY]`.
- **Do not fabricate:** version numbers, release dates, rate limits, prices, CVE IDs, benchmark results, statistics, quotes, or tool behaviors. If you need a number, derive it from a stated command or label it illustrative.
- **Mark uncertainty** with one of: `[VERIFY]` (check against current docs), `[ILLUSTRATIVE]` (example value, not a claim), `[VERSION-SENSITIVE]` (behavior varies by version; state the version range you assume), `[ASSUMPTION]`.
- Keep a running **Claim Register** (Section 12.3) for every non-trivial factual claim.

## 12.2 Mandatory multi-pass self-audit (perform after drafting, before delivering)

Run these passes **in order** and fix every defect found. Do not skip a pass.

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 12 units present, in order, with every required section (Section 5), every module-specific topic (Section 6), level coverage L1–L4. | Any missing section/topic. |
| 2 | **Technical accuracy** | Each command, flag, config key, Dockerfile instruction, and API path is real and used correctly. Mentally execute each lab against current tool behavior. | Any invented or misused syntax. |
| 3 | **Executability** | Each code block is syntactically valid; file paths and cross-references between files resolve; every lab has steps, expected evidence, and cleanup; scripts would pass `shellcheck`/`hadolint`-style review in principle. | Any broken, ambiguous, or unrunnable step. |
| 4 | **Currency** | Version-sensitive or fast-moving claims are tagged `[VERSION-SENSITIVE]`/`[VERIFY]`; no deprecated practice taught as current (e.g., legacy builder, `docker-compose` v1, unnecessary `ADD` of URLs). | Stale or untagged claims. |
| 5 | **Security correctness** | Security statements are accurate and not overstated (e.g., "non-root" ≠ "secure", "SBOM" ≠ "safe", "scan clean" ≠ "no vulnerabilities", "distroless" ≠ "immune"). No insecure practice shown as good. | Overclaim or insecure example unlabeled. |
| 6 | **Fabrication scan** | Hunt for invented statistics, fake citations, made-up CVEs, fabricated benchmark outputs presented as measured, invented tool features. | Any unsupported specific. |
| 7 | **Pedagogical consistency** | Beginner → advanced progression is real; no concept used before it is introduced; terminology consistent; the running example evolves coherently; difficulty ramps smoothly. | Forward dependency without a note; terminology drift. |
| 8 | **Cross-consistency** | Practice questions only test taught content; project deliverables map 1:1 to units; checklists agree with lessons; README claims match actual content. | Orphan question, orphan deliverable, or contradiction. |
| 9 | **Adversarial review** | Re-read as a skeptical staff engineer: "What here would be wrong, risky, or misleading on a real production system?" List the 10 most likely objections and resolve each. | Unresolved objection. |
| 10 | **Reproducibility of labs** | Confirm labs are idempotent, run within the 4 CPU / 8 GB / 30 GB baseline, require no paid service, and clean up. | Hidden cost, resource blowout, or leftover state. |

## 12.3 Audit artifacts to include **inside the syllabus file** (final appendix)

Append these sections at the end of the file:

**Appendix A — Claim Register** (table): `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag ([VERIFY]/[VERSION-SENSITIVE]/none)`. Include at least **60 entries**, covering every version-sensitive or security-relevant claim.

**Appendix B — Audit Report** (table for passes 1–10): `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`. Be candid: report real defects you fixed, not a uniform "PASS".

**Appendix C — Verification Checklist for the Human Reviewer:** a list of **all `[VERIFY]` / `[VERSION-SENSITIVE]` items** grouped by tool (Docker, BuildKit/buildx, Distribution registry, Trivy, Syft, containerd, Kubernetes), each with: *what to check*, *where to check (official doc name)*, *how to test it locally with one command*. The reviewer must be able to close every item in under 3 hours.

**Appendix D — Known Limitations and Assumptions:** what the syllabus intentionally does not cover, assumed tool versions, WSL2 caveats, and anything you could not verify.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor role: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace human execution of the labs.

## 12.4 Trust rules
- If a self-audit pass finds a problem you cannot fix confidently, **leave it visible** as an `OPEN` item in Appendix B and list it in Appendix C. Never hide uncertainty to look polished.
- Never claim a command "was tested/executed" unless it was actually executed in your environment. Use "expected output (representative)" instead.
- Never state that the content "has been verified against live documentation" unless you actually consulted it. Say "written from knowledge of the documentation; verify against current docs" otherwise.

# 13. OUTPUT FORMAT

- **One Markdown document**, named `SYLLABUS-Container-Image-Engineering-and-Registry-Hygiene.md`.
- Start with: title, one-paragraph abstract, metadata block (`Module: M01`, `Stage: 2E`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 0–10 in order, then Appendices A–E.
- Use `#` for the document title, `##` for units, `###`/`####` below. Consistent anchors. Tables for comparisons, fenced code blocks for all code, mermaid for diagrams.
- Each unit must be **self-contained but cross-linked** (relative links to sibling target files).
- **Depth target:** Units 1–8 each ≥ 2,500 words of teaching text excluding code; practice questions ≥ 120 items; project spec complete with all code. Total expected length: very large. **Do not compress to fit.** Use the Delivery Protocol instead.
- No placeholder text, no "etc." in required lists, no "left as an exercise" for required deliverables, no references to "the previous section" without a link.

# 14. DELIVERY PROTOCOL (OUTPUT IS TOO LARGE FOR ONE RESPONSE)

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0 (README), Unit 1 |
| 2 | Unit 2, Unit 3 |
| 3 | Unit 4, Unit 5 |
| 4 | Unit 6, Unit 7 |
| 5 | Unit 8 |
| 6 | Unit 9 (practice questions) |
| 7 | Unit 10 (capstone project, full code) |
| 8 | Appendices A–E (including the completed multi-pass audit across **all** parts) |

Rules:
- At the end of each part print: `PART n/8 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–10, scoped to that unit) **before** printing each part, and keep a running Claim Register.
- Part 8 must then run the **cross-part** audit (passes 7, 8, 9 especially) and may require you to **correct earlier parts**: list every correction as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If you are approaching the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 8, print the final assembly instruction: "Concatenate Parts 1–8 in order into `SYLLABUS-Container-Image-Engineering-and-Registry-Hygiene.md`", and apply all listed corrections.

# 15. QUALITY BAR — DEFINITION OF DONE

The syllabus is complete only when **all** are true:

- [ ] All 12 units present, in the specified order, each unit 1–8 with levels L1–L4 and sections N.0–N.14.
- [ ] Every module-specific topic in Section 6 is taught at its stated level.
- [ ] ≥ 120 practice questions with model answers and distractor analysis.
- [ ] Capstone has complete runnable code, acceptance criteria, rubric, and measurement template.
- [ ] Every lab has steps, expected evidence, and cleanup; all run within the free local baseline.
- [ ] No fabricated numbers, citations, versions, or CVEs; every uncertain item is tagged.
- [ ] Appendices A–E present; Claim Register ≥ 60 entries; audit passes 1–10 reported candidly.
- [ ] Running example evolves coherently from naive to hardened across all units.
- [ ] Forward references to M02, M03, M08, M09, M11, M12, M13 are explicit and not half-taught.
- [ ] A human can verify every open item in under 3 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/8**. Do not ask clarifying questions; where information is missing, record an `[ASSUMPTION]` and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. **Use a long-context, high-capability model**, and keep one conversation across all 8 parts so the Claim Register and running example stay consistent.
2. **Do the human verification yourself.** The prompt makes the LLM list what to check (Appendix C), but an AI self-audit is not independent. Run the labs, and close each `[VERIFY]` item against current official docs: Docker/BuildKit, CNCF Distribution, Trivy, Syft, containerd.
3. **Spot-check fabrication risk areas** first: registry-mirror config keys, `buildx` cache flags, `rewrite-timestamp` support, Docker Hub rate limits, distroless variant names, Trivy flags.
4. **Final file layout:** save the LLM output as `SYLLABUS-Container-Image-Engineering-and-Registry-Hygiene.md` in this folder. Later, split it into the 12 target files (`README.md`, `01-…08-…`, `practice-questions.md`, `Projects/…`).
