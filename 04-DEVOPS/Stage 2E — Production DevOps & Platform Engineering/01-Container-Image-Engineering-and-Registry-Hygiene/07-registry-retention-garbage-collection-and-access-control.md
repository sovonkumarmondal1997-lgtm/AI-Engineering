# Unit 7 — Registry Retention, Garbage Collection, and Access Control

**Target file:** `07-registry-retention-garbage-collection-and-access-control.md`  
**Estimated time:** 8–12 hours, including the four labs and review  
**Prerequisites:** Units 5 and 6, basic Docker and shell use  
**Core tools:** Docker Engine/CLI, local Distribution registry, shell/Python  
**Awareness:** hosted registry lifecycle features, token auth, OIDC federation  
**Last reviewed:** 2026-10-24 (content structure reviewed; current official documentation was not independently checked in this run)

> **Safety status:** This is a learning lesson, not an authorization to operate a production registry. Distribution configuration, API behavior, garbage-collection requirements, and storage-driver behavior are version- and deployment-sensitive. Treat every `[VERIFY]` and `[VERSION-SENSITIVE]` marker as a stop sign until you have checked the exact version and deployment documentation. Commands and outputs marked `[ILLUSTRATIVE]` have not been executed here.

## 7.0 Why this matters in production

A container registry is part of the delivery and recovery path for a data platform. It stores the manifests and blobs needed to pull the exact application image used by a service. If the registry fills its storage, loses a manifest, or becomes unavailable, teams may be unable to publish a fix, scale a workload onto a new node, or roll back a deployment—even when the application is currently running.

Use one consistent example throughout this lesson. A data platform publishes:

- a FastAPI inference API;
- pandas/pyarrow ETL workers;
- Airflow-style task workers;
- PySpark job images.

A release is identified by an immutable image digest, and the release record stores that digest. Tags such as `latest`, `staging`, or `prod` are convenient references, but they are not a sufficient recovery record by themselves. Unit 5 introduced tags, digests, and immutability; Unit 6 covered registry architecture, storage, and distribution. This unit governs the lifecycle after publication: what to retain, what may be deleted, how unreferenced content is reclaimed, who may perform each action, and how to recover from mistakes.

### Why registries grow

Registry storage can grow even when a team deletes tags or believes it has removed old images:

1. A tag is a reference to a manifest, not the image's entire stored byte set.
2. Different manifests can share layers/blobs. Deleting one manifest may leave blobs needed by other manifests.
3. Removing a tag may only remove that reference; the manifest can remain reachable by another tag or reference.
4. A manifest deletion may make some blobs unreferenced, but physical storage reclamation may require a separate garbage-collection operation.
5. Replicas, caches, backups, audit retention, and storage-driver behavior affect physical disk use.
6. Local Docker images on a developer or CI host are separate from server-side registry storage.

**Business impact:** registry capacity is an availability concern, not just a housekeeping concern. Disk exhaustion can fail pushes, increase error rates, block urgent releases, and impair disaster recovery. Aggressive deletion can create a second incident by removing rollback or forensic artifacts while attempting to solve the first.

### Operating invariant

> **Never delete a manifest or artifact that is referenced by a deployed release, a rollback plan, a recovery copy, or a legal/compliance/forensic hold. If the reference inventory is missing, stale, or contradictory, fail closed: do not delete.**

A retention policy first calculates eligibility. Execution is a separate, explicitly approved step. Garbage collection (GC) is not a retention policy; it is a storage-reclamation mechanism that may remove blobs no longer referenced by retained manifests.

## 7.1 Learning objectives

By the end of this unit, you should be able to:

1. Explain tags, manifests, image indexes, layers/blobs, digests, shared content, and reachability.
2. Distinguish registry-side storage and GC from local Docker daemon pruning.
3. Design a retention policy using last-N, age, promoted/released, in-use digest, and hold requirements.
4. Explain why tag names, timestamps, and “untagged” status alone are unsafe deletion criteria.
5. Build a deterministic dry-run report from synthetic inventory and protected-digest inputs.
6. Describe the safe sequence for manifest deletion and GC in a disposable registry, including write control and recovery checks.
7. Distinguish authentication, authorization, TLS/transport security, and auditability.
8. Define least-privilege roles for runtime consumers, CI publishers, operators, and administrators.
9. Identify lifecycle threats, audit requirements, break-glass controls, and recovery options.
10. Gather evidence that supports a reviewable retention or GC change without exposing secrets.

## 7.2 Concept map and vocabulary

### Core terms

| Term | Meaning | Operational caution |
|---|---|---|
| Tag | A human-readable name that refers to an image manifest or index, for example `inference-api:2.4.1`. | Tags can be moved unless immutability or policy prevents it. |
| Digest | A content-derived identifier, commonly represented as an algorithm and hash, such as `sha256:…`. | Record the exact digest returned by the registry/runtime; do not reconstruct it from a tag. |
| Manifest | A document describing an image's configuration and layer/blob references. | A manifest can be referenced by more than one tag or other higher-level object. |
| Image index / manifest list | A higher-level document that points to platform-specific manifests, such as Linux/amd64 and Linux/arm64 variants. | Retain the index and the platform manifests needed by your deployment workflow. Exact behavior is implementation-sensitive. |
| Layer/blob | Content stored by the registry and referenced from manifests. | The same blob may be shared by many images; do not assume one manifest equals one unique set of bytes. |
| Tagged manifest | A manifest currently referenced by one or more tags in a registry namespace. | A tag listing is not necessarily a complete inventory of all content or external references. |
| Untagged manifest | A manifest with no tag reference visible under a particular registry's semantics/API. | “Untagged” does not universally mean “dangling,” “unused,” or “safe to delete.” |
| Dangling image | A term often used by local image tooling for an image without a tag or other local reference. | Its exact meaning depends on the tool and context; do not apply local Docker terminology blindly to registry objects. |
| Referenced / in-use digest | An image digest required by an active workload, release, rollback, recovery plan, or hold. | Runtime usage may be recorded outside the registry. Registry metadata alone cannot establish every production reference. |
| Reachability | Whether a retained object can be reached by following valid references from roots such as retained manifests/indexes. | GC implementations differ; verify the algorithm and operating requirements for the deployed version. |
| Retention | A policy deciding what artifacts must remain available and for how long. | Retention is a business, reliability, security, and compliance decision—not only a storage optimization. |
| Garbage collection (GC) | A mechanism that reclaims storage not needed by retained registry objects, according to the implementation's rules. | It is not equivalent to deleting tags, and it is not a substitute for backups. |
| Authentication (authn) | Establishing which identity is making a request. | A successful login does not mean the identity should be allowed to delete. |
| Authorization (authz) | Deciding which actions an authenticated identity may perform on which resources. | Basic auth alone does not automatically provide fine-grained repository permissions. |
| Auditability | The ability to attribute and reconstruct actions using reliable records. | Logs may be incomplete; verify event coverage and retention. |

### A reference graph

The diagram is conceptual. Real registry schemas and APIs vary.

```text
Protected release record
        |
        v
  digest sha256:PROD
        |
        v
  image index / manifest
      /          \
     v            v
 amd64 manifest  arm64 manifest
     |  \             |
     v   v            v
  blob A blob B      blob C
       ^
       |
Other ETL image manifest also references blob B

Tag `prod` ------> index / manifest (a movable name unless protected)
Tag `2.4.1` -----> index / manifest
```

A digest is protected because a release record references it, not because the tag looks important. `blob B` is shared. Removing one manifest does not make `blob B` reclaimable if another retained manifest still references it. The implementation's GC decides which blobs are unreachable according to its own rules.

### Registry storage versus local Docker storage

| Operation or location | Scope | What it does not do |
|---|---|---|
| `docker image prune` | Removes eligible images from the selected local Docker daemon. | Does not apply a retention policy to a remote registry. |
| `docker image prune -a` | Broader local image cleanup; exact eligibility semantics should be checked against the Docker CLI version. | Does not delete remote registry manifests or run registry GC. |
| `docker system prune` | Cleans selected unused local Docker resources according to its options and version. | Is not a server-side registry cleanup procedure. |
| Registry manifest deletion API | Deletes a registry-side manifest reference/object according to registry configuration and API semantics. | Does not guarantee immediate physical disk reclamation. |
| Distribution `registry garbage-collect` | Reclaims eligible registry storage according to the selected Distribution version and storage backend. | Is not a replacement for retention design, access control, or backups. |

Docker command semantics are documented in the Docker CLI reference; verify the exact options and prompts for your installed version before using them. Source to check: Docker CLI reference, `docker image prune` and `docker system prune` (URLs listed in §7.14). This lesson intentionally does not use local prune commands as registry GC.

### What is taught here and what is deferred

- **This unit:** retention decision logic, dry-run reports, deletion/GC safety, local synthetic labs, access-control concepts, evidence, audit, and recovery planning.
- **Unit 5:** tags, digests, immutable promotion, and versioning fundamentals.
- **Unit 6:** registry architecture, storage layout, mirrors, and pull-through caches.
- **Unit 3:** reproducible image builds and their limits as evidence of equivalence.
- **Unit 4:** BuildKit build cache. BuildKit cache records/blobs are not the same thing as published registry image manifests/blobs, even when a registry is used as a cache backend.
- **Unit 8:** non-root runtime defaults and container runtime hardening.
- **M02 CI/CD:** automation of approvals and release workflows.
- **M03 Kubernetes operations:** workload/deployment inventory and rollback references.
- **M09 secrets:** secret storage and rotation practices.
- **M11 observability:** telemetry pipelines and operational dashboards.
- **M12 supply-chain security:** provenance, SBOMs, signatures, and artifact verification.
- **M13 backup/disaster recovery:** enterprise backup architecture and DR exercises. This unit specifies the registry lifecycle recovery evidence that should feed that work; it does not replace a full DR design.

## 7.3 Level 1 — Beginner: Registry Storage and References

### 7.3.1 Why deleting a tag is not the same as deleting bytes

Think of a tag as a label on a reference. A registry manifest describes an image and points to its configuration and layers. A tag may point to a manifest or index. A layer can be shared by several images because image layers are content-addressed and reusable.

When one tag is removed, several possibilities exist:

- Another tag still points to the same manifest.
- The manifest remains available through an implementation-specific reference or API behavior.
- The manifest is deleted, but its blobs are still referenced by other manifests.
- Some blobs become unreachable, but physical space is not reclaimed until GC runs.
- A storage backend, cache, replica, or backup continues to retain data independently.

Therefore, do not estimate reclaimable bytes by summing image sizes shown by `docker image ls`. Logical image sizes may double-count shared layers, and registry filesystem usage can include metadata and implementation overhead.

### 7.3.2 A safe first inspection

Use a **disposable local registry** and a unique lab name. Never point these steps at a production registry or an unspecified remote endpoint.

**Prerequisites**

- Docker Engine is installed and running.
- WSL2 Ubuntu has enough free disk space for the small lab images and registry volume.
- The selected local port is unused.
- You understand that deleting the named lab container/volume removes lab data.

Check the environment:

```bash
docker version
docker info
df -h .
docker image ls
```

Expected exit status: `0` for successful inspection. Exact output varies by Docker version and host; no output is asserted here.

Create a unique temporary workspace and a named network/container. The following uses `registry:2` as the learning image requested by the syllabus. **[VERIFY]** The tag may resolve to a moving image over time; for repeatable exercises, record the actual pulled image digest and choose a version supported by current Distribution documentation.

```bash
export LAB_NAME="u7-registry-lab"
export LAB_PORT="5007"
export LAB_DIR="$(mktemp -d "${TMPDIR:-/tmp}/u7-registry.XXXXXX")"
printf 'LAB_DIR=%s\n' "$LAB_DIR"
docker network create "${LAB_NAME}-net"
docker volume create "${LAB_NAME}-data"
docker run -d \
  --name "${LAB_NAME}" \
  --network "${LAB_NAME}-net" \
  -p "127.0.0.1:${LAB_PORT}:5000" \
  -v "${LAB_NAME}-data:/var/lib/registry" \
  registry:2
```

These commands are a guided recipe, not executed evidence. The loopback bind limits the published port to the local host interface; confirm how your WSL2 and host networking configuration exposes it. If a command fails, stop and inspect the specific named resource before retrying. Do not switch to `0.0.0.0` to “make it work” without understanding the exposure.

Create two small synthetic images from a scratch workspace. The `alpine` base image is used only as a small lab base; it is not a recommendation for production. Pinning a digest is preferable for repeatability, but a digest must be obtained from a trusted source and verified for the target platform.

```bash
mkdir -p "$LAB_DIR/image"
cat > "$LAB_DIR/image/Dockerfile" <<'EOF'
FROM alpine:3.20
ARG BUILD_LABEL=sample
LABEL org.example.lab="unit-7" org.example.build-label="${BUILD_LABEL}"
CMD ["sh", "-c", "echo synthetic registry lab"]
EOF

docker build --build-arg BUILD_LABEL=v1 -t localhost:5007/u7-demo:1.0 "$LAB_DIR/image"
docker build --build-arg BUILD_LABEL=v2 -t localhost:5007/u7-demo:1.1 "$LAB_DIR/image"
docker push localhost:5007/u7-demo:1.0
docker push localhost:5007/u7-demo:1.1
```

**[VERSION-SENSITIVE]** A plain HTTP local registry may require explicit insecure-registry configuration depending on Docker daemon settings. Do not disable TLS or weaken a shared daemon globally just to run this lab. If the push fails because the endpoint is not trusted, consult the Docker Engine registry security documentation and configure only the isolated lab environment using a documented method. A production registry should use authenticated, validated TLS.

Inspect tags through the registry API. The Distribution API paths below are common examples, but API support and deletion behavior must be verified for the exact registry/version.

```bash
curl --fail --silent --show-error "http://127.0.0.1:${LAB_PORT}/v2/"
curl --fail --silent --show-error "http://127.0.0.1:${LAB_PORT}/v2/u7-demo/tags/list"
```

Expected successful responses are JSON, but exact bodies are **[ILLUSTRATIVE]**:

```json
{"repositories":["u7-demo"]}
```

```json
{"name":"u7-demo","tags":["1.0","1.1"]}
```

A tag listing reports tag references visible through that endpoint. It is not proof that all production or external references have been inventoried.

### 7.3.3 Understand shared blobs

The two synthetic images may share the same base layers. Whether they do depends on their build inputs and output. Compare their manifest/config/layer digests using the registry API or a suitable inspection tool that is installed and trusted. Do not infer sharing merely because the base image name is the same; compare the actual digest references.

A conceptual table:

| Object | Image `1.0` | Image `1.1` | Interpretation |
|---|---:|---:|---|
| Base layer digest | `sha256:BASE` | `sha256:BASE` | Shared blob; illustrative digest label only |
| App-specific config/metadata | `sha256:CFG1` | `sha256:CFG2` | May differ |
| Manifest digest | `sha256:MAN1` | `sha256:MAN2` | Separate manifest identities in this example |
| Protected release reference | none | `sha256:MAN2` | If deployed/rollback inventory points to `MAN2`, retain it |

All digest strings in this table are **[ILLUSTRATIVE]**, not actual hashes.

### 7.3.4 First-lab interpretation

If you remove tag `1.0`, do not conclude that its layers have been removed. Determine what operation the registry actually performed, whether a manifest still has another reference, whether the deletion API is enabled, and whether GC has run under the documented safe conditions. For this introductory lab, do not delete anything yet. Record:

- registry image/version and digest;
- registry configuration relevant to deletion;
- tag list before any changes;
- manifest/index digest for each synthetic tag;
- any shared blob digests observed;
- the difference between registry-side observations and local `docker image ls`.

**Success criterion:** you can explain the reference graph and identify why tag deletion, manifest deletion, and blob reclamation are separate concepts.

## 7.4 Level 2 — Intermediate: Retention Policy and Safe Deletion

### 7.4.1 Policy dimensions

A production retention policy normally combines several independent requirements.

| Rule | Purpose | Common failure if used alone |
|---|---|---|
| Keep last N versions per repository/channel | Retain recent release history. | A slow-moving but still deployed version may fall outside N. |
| Keep artifacts younger than an age threshold | Bound ordinary history. | A critical rollback or legal hold can be older than the threshold. |
| Keep promoted/released artifacts | Preserve known production releases. | Promotion metadata can be missing or incorrect. |
| Keep any digest referenced by deployed workloads | Protect live deployment dependencies. | Workload inventory may be stale or omit offline/DR environments. |
| Keep rollback artifacts | Preserve an explicitly approved rollback window. | A rollback plan may reference a digest not represented by a tag. |
| Keep compliance/forensic hold artifacts | Preserve evidence under policy or legal requirements. | A hold may be stored outside the registry and missed by the cleanup job. |
| Separate scratch/preview from release repositories | Apply different lifecycle policies by risk. | A naming convention alone does not enforce namespace isolation. |

No universal retention period is correct for every organization. Decide using release cadence, rollback objectives, incident investigation needs, regulatory obligations, storage capacity, replication, and restore capability. Record the policy owner and exception process.

### 7.4.2 Why simple heuristics are unsafe

**Bad pattern:** “Delete every image older than 30 days.”

- **Why unsafe:** age alone cannot identify a currently deployed digest, a release retained for a rollback, or an artifact under forensic hold.
- **Corrected pattern:** compute the candidate set from a complete inventory, then subtract deployed/rollback/promoted/held digests. If required metadata is missing, fail closed.

**Bad pattern:** “Delete all untagged manifests.”

- **Why unsafe:** “untagged” is an API- and implementation-specific state, and an untagged manifest can still matter to a deployment or index/platform relationship.
- **Corrected pattern:** resolve all protected digests and references first; validate the registry's deletion semantics and only then consider a candidate.

**Bad pattern:** “The tag is not `prod`, so it is safe.”

- **Why unsafe:** tags can move or be renamed; production records should refer to digests.
- **Corrected pattern:** use signed/reviewable release metadata and digest-based references.

**Bad pattern:** “The scanner found a critical vulnerability, so delete the image immediately.”

- **Why unsafe:** deletion can destroy evidence and the only known rollback artifact. A scan finding is one input into quarantine, remediation, and retention decisions—not a complete policy.
- **Corrected pattern:** block new promotion or quarantine the artifact, preserve digest and scan evidence, identify deployed references, remediate/replace, and delete only after explicit lifecycle criteria are met.

### 7.4.3 A deterministic synthetic policy

For the example data platform, use this policy for learning. It is **[ASSUMPTION]** and is not a recommended universal period.

1. **Protected first:** always keep any digest in the active-deployment, rollback, legal/forensic-hold, promoted-release, or explicitly protected inventory.
2. **Missing inventory:** if the protected digest file is missing, empty when it is expected to contain entries, stale, malformed, or cannot be reconciled to the source inventory, produce an error and do not produce executable deletion actions.
3. **Keep last N:** for each repository and release channel, keep the newest N candidates according to a documented deterministic ordering. Use a trustworthy creation timestamp plus a stable tie-breaker such as digest; do not rely on lexical tag order.
4. **Age rule:** candidates outside the ordinary age window may be eligible only after rules 1–3 and holds are applied.
5. **Scratch/preview:** apply a separate policy to explicitly designated scratch repositories; do not infer “scratch” solely from a tag prefix.
6. **Execution separation:** the policy tool emits candidate digests and reasons. A human or separate approved executor performs deletion using the documented registry API. A dry-run report never deletes.
7. **Unknown reference:** if any source of deployment, DR, or hold references is unavailable or contradictory, retain the candidate and raise a review item.

Precedence is important: explicit protection and holds override age and keep-last-N rules. Promoted releases are protected even if they are old. Deterministic ordering prevents repeated runs from selecting different candidates when timestamps tie.

### 7.4.4 Before-and-after policy table

All repository names, tags, timestamps, digests, and decisions below are **[ILLUSTRATIVE]**.

| Repository | Tag | Digest | Age | External reference / state | Policy decision | Reason |
|---|---|---|---:|---|---|---|
| `inference-api` | `2.4.3` | `sha256:A3` | 2 d | Active deployment | KEEP | In-use digest |
| `inference-api` | `2.4.2` | `sha256:A2` | 8 d | Approved rollback | KEEP | Rollback protection |
| `inference-api` | `2.4.1` | `sha256:A1` | 18 d | Promoted release | KEEP | Promoted release rule |
| `inference-api` | `2.3.0` | `sha256:A0` | 120 d | No known reference; inventory complete | REVIEW / possibly eligible | Age and keep-N candidate; separate approval required |
| `etl-worker` | `2026.10.20` | `sha256:E3` | 4 d | Active scheduled job | KEEP | In-use digest |
| `etl-worker` | `2026.09.10` | `sha256:E2` | 44 d | Hold status unknown | KEEP / BLOCK | Unknown hold state fails closed |
| `pyspark-job` | `build-991` | `sha256:P9` | 1 d | Scratch repository | KEEP | Within scratch retention window |
| `pyspark-job` | `build-700` | `sha256:P7` | 70 d | Explicitly disposable preview; no protected reference | CANDIDATE | Eligible under preview policy, not yet deleted |

“Candidate” means only that the policy permits review. It does not mean deletion has occurred or that GC will reclaim a particular number of bytes.

### 7.4.5 Distribution deletion and garbage collection

CNCF Distribution's registry supports an HTTP API, but manifest deletion depends on registry configuration and implementation/version. **[VERIFY] [VERSION-SENSITIVE]** Before attempting deletion:

1. Identify the exact Distribution version and storage backend.
2. Read the configuration reference for the `storage` and `delete` settings applicable to that version.
3. Confirm the API method and digest header/response semantics in the matching API documentation.
4. Test against the disposable registry with a synthetic manifest.
5. Record the status code, digest, and follow-up pull/tag-list behavior.
6. Only after manifest deletion should you consider GC under the version-specific documented maintenance conditions.

The manifest deletion API is not a universal “delete image and free all bytes now” operation. **[VERIFY]** Do not assume the API is enabled by default or that the same endpoint behavior applies to every hosted registry.

Distribution's `registry garbage-collect` command is commonly used to reclaim storage that is no longer referenced, but its exact flags and requirements must be checked against the deployed version. **[VERSION-SENSITIVE]** Official guidance for the selected version must determine whether the registry must be stopped or placed into a documented read-only/maintenance mode. Do not run GC while writes are occurring if the selected documentation says concurrent writes are unsafe. Do not invent or assume a `--dry-run` flag. If the installed command does not offer the dry-run capability you need, use a separate retention-script dry-run and run GC only after reviewed manifest deletion and a verified maintenance procedure.

A safe lab must have an explicit abort condition: if the version, storage driver, deletion configuration, write-freeze procedure, or backup/restore procedure cannot be verified, stop before destructive operations.

### 7.4.6 Local Docker prune: useful but different

The following are **local daemon** operations:

```bash
docker image prune
docker image prune -a
docker system prune
```

**[VERSION-SENSITIVE]** Check the installed Docker CLI's official reference for the precise eligibility rules, prompts, filters, and options. These commands can remove local data and may affect a developer's or CI worker's cache. They do not implement server-side registry retention and do not run Distribution GC. Do not use them to address registry backend disk exhaustion.

## 7.5 Level 3 — Advanced: Garbage Collection Operations and Access Control

### 7.5.1 Safe GC sequence

Use this order for a planned lifecycle operation. The order is deliberate: discovery and recovery evidence must precede deletion.

1. **Identify the target.** Record registry implementation, exact version/digest, deployment mode, storage backend, configuration, and API behavior.
2. **Control writes.** Schedule maintenance, notify stakeholders, and freeze or restrict pushes using the documented implementation-specific safe method. Do not improvise a read-only configuration change without understanding its effects.
3. **Inventory references.** Collect all active workload digests, deployment manifests, release records, rollback references, DR replicas, offline environments, and compliance/forensic holds.
4. **Take a consistent backup/snapshot.** Use a documented, consistency-aware procedure. A casual file copy while metadata or blobs are changing may not form a valid restore point. Record the backup identifier, timestamp, and verification evidence.
5. **Run retention dry-run.** Validate inputs, calculate candidates, emit machine-readable output, and review each candidate with the owning team.
6. **Approve separately.** Record approver, scope, reason, and time window. A dry-run report must not itself execute deletion.
7. **Delete manifests.** Use only the supported API/procedure for the exact version. Record response status and digest identity; never log authorization headers or tokens.
8. **Run GC safely.** Follow the selected version's documented maintenance/read-only requirement. Ensure writes are controlled for the required interval.
9. **Measure before/after.** Compare registry filesystem usage and backend metrics. Distinguish logical image size, unique blob bytes, registry metadata, and physical disk space.
10. **Validate and reopen.** Prove protected digests remain pullable, test known rollback artifacts, check logs/health and push/pull, then resume writes only after success. Record deviations and follow-up work.

### 7.5.2 Capacity and measurement

Use separate measurements for separate questions:

- **Logical image size:** what an image inspection tool reports; may include shared layers in multiple image totals.
- **Unique blob bytes:** sum of distinct blob objects visible to the chosen inventory method; may not equal filesystem usage.
- **Filesystem used/free bytes:** actual space on the registry's storage filesystem or volume.
- **Backend allocation:** may differ from apparent file sizes due to snapshots, compression, deduplication, object-store versions, or provider accounting.
- **Egress:** bytes transferred to clients/regions; a pull-through cache may reduce upstream requests but does not make egress universally free.
- **Backup footprint:** retained copies and snapshots may keep data after the live registry has reclaimed it.

Use a measurement template rather than promising a reclaim percentage:

| Measurement | Before | After | Method / timestamp | Notes |
|---|---:|---:|---|---|
| Registry filesystem used (bytes) | ______ | ______ | `df -B1` or backend metric | Measure same mount |
| Registry filesystem free (bytes) | ______ | ______ | `df -B1` or backend metric | Include headroom |
| Distinct blob bytes, if available | ______ | ______ | Documented inventory method | Avoid double-counting |
| Push success / latency | ______ | ______ | Existing monitoring | Compare like windows |
| Pull success / latency | ______ | ______ | Existing monitoring | Include protected digest test |
| GC start/end and exit status | ______ | ______ | Command/service logs | Version-specific |
| Protected digests verified | ______ | ______ | Pull by digest | Include rollback set |

Do not claim reclaimable bytes until measured. GC duration and space recovery depend on object count, storage backend, implementation, and concurrent activity constraints.

### 7.5.3 Tag immutability and retention

Immutable tags reduce accidental tag movement, but they do not guarantee that the underlying manifest cannot be deleted by an authorized administrator. Conversely, a digest is content-addressed, but it can become unavailable if the registry deletes the corresponding manifest/blob or loses its storage.

Use both:

- digest-based deployment/release records;
- tag immutability where supported and configured;
- protected digest inventories;
- restricted deletion permissions;
- audit logs and approval records;
- backup and restore tests.

A “protected” tag is not enough unless the registry's enforcement semantics are tested. **[VERIFY]** Hosted registry immutability and deletion policies differ by product, tier, repository type, and configuration.

### 7.5.4 Authentication, authorization, transport security, and auditability

These are separate control planes:

| Control | Question answered | Example | Does not guarantee |
|---|---|---|---|
| Authentication | Who is calling? | Username/password, robot identity, token, workload identity | That the identity has permission for a given repository/action |
| Authorization | What may this identity do? | Read-only pull permission on `inference-api` | That the credential cannot be stolen or that all actions are logged |
| Transport security | Is the connection protected and is the endpoint authenticated? | TLS with validated certificate | That the authenticated user is authorized or the registry is uncompromised |
| Auditability | Can we attribute and reconstruct actions? | Registry/API logs correlated with CI release metadata | Complete attribution if events are not logged or logs can be tampered with |

### 7.5.5 Local `htpasswd` authentication: learning example

A local `htpasswd` example can teach credential-based authentication. It is not a complete enterprise authorization system.

**[VERIFY] [VERSION-SENSITIVE]** Distribution configuration syntax, supported password hash formats, the expected path/mount, and exact image/configuration details must be checked against the documentation for the selected `registry:2`/Distribution version. Do not put passwords in shell history or commit credential files.

A generic setup pattern is:

```bash
# Create a private lab-only auth directory.
mkdir -p "$LAB_DIR/auth"
chmod 700 "$LAB_DIR/auth"

# Install/use htpasswd from a trusted package source.
# Exact package command depends on the WSL2 Ubuntu release.
htpasswd -Bbn 'lab-reader' 'REPLACE_WITH_A_UNIQUE_LAB_PASSWORD' \
  > "$LAB_DIR/auth/htpasswd"
chmod 600 "$LAB_DIR/auth/htpasswd"
```

This command is **[ILLUSTRATIVE]**. Passing a literal password as a command-line argument may expose it in process listings or shell history; prefer an interactive method supported by your installed `htpasswd` version and avoid real credentials. The output file contains password hashes, but it is still sensitive and should be protected.

A common Distribution configuration shape uses an `auth` section with an `htpasswd` type and a path to the file. **[VERIFY]** Consult the matching official configuration reference before applying it; do not copy a fragment into an existing registry config without checking the full schema and startup behavior.

Important limitation: Basic authentication establishes an identity using credentials, but it does not automatically implement fine-grained per-repository read/write/delete roles. If your registry only supports coarse access, isolate tenants or use a registry implementation/product that supports the needed authorization model rather than pretending a shared username is least privilege.

### 7.5.6 Token authentication and least-privilege roles

A token-authenticated registry flow commonly involves a client requesting a resource, receiving an authentication challenge, obtaining a scoped token from a token service, and retrying with that token. Exact challenge fields, token claims, scopes, issuer configuration, trust, and authorization behavior are implementation-specific. **[VERIFY]** Do not copy a token-auth configuration from another registry without verifying the issuer/audience, signing keys, service name, scopes, TLS, and expected claims.

Example role model:

| Identity | Allowed actions | Explicitly denied / restricted |
|---|---|---|
| Runtime consumer | Pull/read from named production repositories | Push, delete, alter registry configuration |
| CI publisher | Push to explicitly assigned repositories; read base images as required | Delete, change auth/configuration, publish to unrelated tenants |
| Registry operator | Health checks, approved maintenance, GC under change control | Routine use of broad admin credentials; unapproved deletion |
| Registry administrator | Manage configuration and narrowly scoped privileged actions | Shared use; unlogged changes; standing access where just-in-time access is feasible |
| Break-glass identity | Time-bound emergency action with explicit approval | Routine automation, permanent unattended use |

Use distinct identities for different systems. Store credentials in an approved secret manager or protected CI secret store, rotate them, and keep tokens out of logs. Short-lived credentials and OIDC federation can reduce long-lived secret exposure when the registry and CI platform support compatible flows. **[VERIFY]** Not every registry supports the same OIDC, workload identity, robot-account, or token features.

## 7.6 Level 4 — Expert: Lifecycle Governance, Audit, and Recovery

### 7.6.1 Policy-as-code contract

A safe retention tool should be a decision engine, not a generic remote deletion utility.

Required properties:

- deterministic candidate calculation;
- explicit protected/in-use digest inventory;
- explicit exclusions for promoted releases and holds;
- conservative behavior when references are unknown;
- schema and digest validation;
- dry-run as the default;
- machine-readable report with one reason per decision;
- nonzero exit on missing, stale, or invalid inputs;
- no registry endpoint or credentials embedded in the policy calculator;
- separate approval and execution process;
- explicit opt-in required even for any later executor, with scope restrictions and audit records.

The following Python script reads synthetic JSON files only. It does **not** connect to a registry and cannot delete images. It defaults to dry-run and fails closed if the protected inventory is missing, empty, stale, or malformed. For a real organization, “freshness” must be defined using the authoritative inventory system and evidence timestamp; this fixture uses an explicit timestamp and maximum age.

Save as `retention_dry_run.py` in your lab workspace:

```python
#!/usr/bin/env python3
"""Safe synthetic retention policy calculator; never contacts a registry."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must include timezone: {value!r}")
    return parsed.astimezone(timezone.utc)


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON from {path}: {exc}") from exc


def require_digest(value, where):
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise ValueError(f"{where}: invalid sha256 digest {value!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--protected", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--max-inventory-age-hours", type=int, default=24)
    parser.add_argument("--keep-last-n", type=int, default=3)
    args = parser.parse_args()

    if args.max_inventory_age_hours <= 0 or args.keep_last_n < 1:
        print("ERROR: age limit must be positive and keep-last-N >= 1", file=sys.stderr)
        return 2

    try:
        inventory = load_json(args.inventory)
        protected_doc = load_json(args.protected)
        now = datetime.now(timezone.utc)

        if not isinstance(inventory, dict) or not isinstance(inventory.get("images"), list):
            raise ValueError("inventory must contain an 'images' list")
        if not isinstance(protected_doc, dict):
            raise ValueError("protected inventory must be a JSON object")
        protected_at = parse_time(protected_doc.get("generated_at"))
        protected_digests = protected_doc.get("digests")
        if not isinstance(protected_digests, list) or not protected_digests:
            raise ValueError("protected inventory is missing/empty; fail closed")
        if (now - protected_at).total_seconds() > args.max_inventory_age_hours * 3600:
            raise ValueError("protected inventory is stale; fail closed")
        if protected_at > now:
            raise ValueError("protected inventory timestamp is in the future; fail closed")

        for digest in protected_digests:
            require_digest(digest, "protected inventory")

        rows = []
        seen = set()
        for i, item in enumerate(inventory["images"]):
            if not isinstance(item, dict):
                raise ValueError(f"images[{i}] must be an object")
            repo = item.get("repository")
            tag = item.get("tag")
            digest = item.get("digest")
            created = parse_time(item.get("created_at"))
            promoted = item.get("promoted", False)
            hold = item.get("hold", False)
            channel = item.get("channel", "release")
            if not isinstance(repo, str) or not repo or not isinstance(tag, str) or not tag:
                raise ValueError(f"images[{i}] repository/tag must be non-empty strings")
            require_digest(digest, f"images[{i}]")
            if digest in seen:
                raise ValueError(f"duplicate digest in fixture: {digest}")
            seen.add(digest)
            if not all(isinstance(flag, bool) for flag in (promoted, hold)):
                raise ValueError(f"images[{i}] promoted/hold must be booleans")
            if created > now:
                raise ValueError(f"images[{i}] created_at is in the future")
            rows.append({
                "repository": repo, "tag": tag, "digest": digest,
                "created_at": created, "promoted": promoted,
                "hold": hold, "channel": channel,
            })

        # Keep last N deterministically per repository/channel:
        # newest timestamp first, then digest as stable tie-breaker.
        keep_last = set()
        groups = {}
        for row in rows:
            groups.setdefault((row["repository"], row["channel"]), []).append(row)
        for group in groups.values():
            ordered = sorted(group, key=lambda r: (-r["created_at"].timestamp(), r["digest"]))
            keep_last.update(row["digest"] for row in ordered[:args.keep_last_n])

        protected = set(protected_digests)
        report_rows = []
        for row in sorted(rows, key=lambda r: (r["repository"], r["tag"], r["digest"])):
            reasons = []
            if row["digest"] in protected:
                reasons.append("protected/in-use inventory")
            if row["promoted"]:
                reasons.append("promoted release")
            if row["hold"]:
                reasons.append("compliance/forensic hold")
            if row["digest"] in keep_last:
                reasons.append(f"keep last {args.keep_last_n} for repository/channel")
            decision = "KEEP" if reasons else "CANDIDATE_REVIEW_ONLY"
            report_rows.append({
                "repository": row["repository"],
                "tag": row["tag"],
                "digest": row["digest"],
                "decision": decision,
                "reasons": reasons or ["outside configured keep rules; approval still required"],
            })

        report = {
            "mode": "DRY_RUN_ONLY",
            "generated_at": now.isoformat(),
            "inventory_file": str(args.inventory),
            "protected_inventory_file": str(args.protected),
            "candidate_count": sum(r["decision"] == "CANDIDATE_REVIEW_ONLY" for r in report_rows),
            "items": report_rows,
            "warning": "No deletion was performed. Review candidates and references separately.",
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "mode": report["mode"],
            "items": len(report_rows),
            "candidate_count": report["candidate_count"],
            "report": str(args.report),
        }, indent=2))
        return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

**Important interpretation:** this fixture intentionally treats the protected inventory as mandatory and freshness-bounded. It does not establish that the inventory is complete; an authoritative upstream process must attest that. The script is deliberately incapable of deleting registry content. A production policy must also reconcile all relevant deployment, rollback, DR, and hold systems before its output can be trusted.

### 7.6.2 Create synthetic input fixtures

The digest values below must be valid-shaped 64-hex strings; these are synthetic fixtures, not actual registry digests. Generate them for a local exercise:

```bash
python3 - <<'PY'
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

now = datetime.now(timezone.utc)
def stamp(days):
    return (now - timedelta(days=days)).isoformat()

images = []
for i, days in enumerate([2, 5, 12, 25, 60]):
    images.append({
        "repository": "inference-api",
        "tag": f"2.4.{i}",
        "digest": "sha256:" + f"{i + 1:064x}",
        "created_at": stamp(days),
        "promoted": i == 2,
        "hold": False,
        "channel": "release",
    })
Path("inventory.json").write_text(json.dumps({"images": images}, indent=2) + "\n")
protected = {
    "generated_at": now.isoformat(),
    "digests": ["sha256:" + f"{1:064x}"]
}
Path("protected.json").write_text(json.dumps(protected, indent=2) + "\n")
PY

python3 retention_dry_run.py \
  --inventory inventory.json \
  --protected protected.json \
  --report retention-dry-run.json \
  --keep-last-n 2
```

Expected exit status is `0` for valid fresh fixtures. The exact candidate count and report are determined by the generated data and current time; do not copy an invented count as evidence. Inspect `retention-dry-run.json`, verify that the protected and promoted digests are `KEEP`, and confirm the tool did not contact a registry.

Test fail-closed behavior by copying `protected.json` to a backup and temporarily setting `digests` to an empty list. The script should return exit status `2` and print an error. Restore the fixture after the test.

### 7.6.3 Audit logging and investigation

A useful lifecycle audit trail should answer:

- Who pushed, tagged, deleted, changed permissions, or changed registry configuration?
- Which repository, tag, manifest digest, or object was affected?
- When did the action occur, and from which identity/system?
- Which CI run, release record, change request, or incident authorized it?
- What was the API/command result?
- What was the before/after state, and which protected digests were checked?
- Were audit records retained outside the registry's mutable trust boundary?

Correlate registry/API logs with CI identity, release metadata, change tickets, workload rollout records, and storage metrics. Do not log passwords, bearer tokens, authorization headers, or full secret-bearing environment dumps. If the registry does not emit an event needed for attribution, document the gap and add a compensating control where feasible; do not claim the event is auditable merely because an access log exists.

### 7.6.4 Break-glass deletion procedure

A break-glass action is a controlled emergency exception, not an informal bypass.

Required record:

1. **Trigger and reason:** what incident or deadline requires the action?
2. **Authorizer:** who approved it, and who executes it?
3. **Scope:** exact repository and digest list; no wildcard deletion.
4. **Time bound:** start/end time and automatic expiry/revocation where possible.
5. **Pre-action evidence:** inventory, protected digest list, backup identifier, current permissions, and reason normal process is insufficient.
6. **Execution evidence:** API response, command status, operator identity, timestamps, and change/incident ID.
7. **Post-action validation:** protected digest pulls, rollback test, registry health, and storage measurement.
8. **Review:** assess why break-glass was needed and update policy or automation.

Never put credentials in the incident ticket. A break-glass credential should not be a shared everyday CI credential.

### 7.6.5 Multi-tenant boundaries

Repository naming is not, by itself, an authorization boundary. If multiple teams or tenants share a registry:

- assign distinct identities per workload/team;
- scope publisher permissions to explicit repository paths;
- restrict delete and configuration permissions separately from push;
- test cross-tenant read, push, and delete denial;
- keep tenant-specific audit trails;
- avoid shared administrator credentials;
- document which team owns retention exceptions and legal holds.

If the selected registry cannot enforce the required granularity, use stronger isolation (for example, separate registry instances/accounts/projects) rather than assuming naming conventions provide security.

### 7.6.6 Vulnerability quarantine and evidence preservation

When a scanner reports a vulnerable image:

1. Record the digest, image metadata, scanner/version, finding identifiers, timestamps, and relevant logs.
2. Prevent further promotion or deployment according to the organization's policy.
3. Identify whether the digest is deployed, referenced by rollback, or under investigation.
4. Preserve evidence and ensure the only forensic artifact is not deleted.
5. Build, test, scan, and promote a remediated image through the approved release process.
6. Update deployment and rollback records to the new digest.
7. Remove the old image only when retention, hold, and recovery criteria permit it.

A vulnerability finding alone does not answer whether the artifact should be deleted immediately. Quarantine, deny-listing, revocation, remediation, and retention are different actions. Unit M12 covers deeper supply-chain verification and provenance.

### 7.6.7 Incident exercise: “someone deleted a production image”

**Initial trigger:** a workload cannot pull the expected digest during a rollout or recovery event.

**Triage and response**

1. **Stabilize:** pause rollout automation if it would amplify failures. Do not blindly restart healthy workloads that still have a local copy.
2. **Assess blast radius:** identify affected repository/digest, clusters, regions, scheduled jobs, and release channels.
3. **Confirm facts:** inspect registry/API logs, tag and digest inventory, CI logs, change records, and current workload references. Distinguish authentication failures, network failures, and actual manifest/blob deletion.
4. **Preserve evidence:** save relevant logs, timestamps, digest identifiers, approval records, and registry health/storage metrics in a controlled incident location.
5. **Find recovery source:** check healthy replicas, tested backups/snapshots, immutable artifact stores, or the original build outputs. Verify integrity before republishing/restoring.
6. **Restore carefully:** follow the documented recovery method. Verify the digest and platform manifests, then test a pull by digest from a clean client.
7. **Validate deployment:** confirm the workload can retrieve the image and the release/rollback record points to the intended digest. Communicate status and residual risk.
8. **Prevent recurrence:** restrict delete privileges, add protected-digest checks, improve audit coverage, test restore, and review the approval path.

**Rebuilding is not automatically equivalent to restoring.** A rebuild from source can produce a different digest due to base-image movement, dependency resolution, timestamps, toolchain changes, build arguments, or unavailable inputs. Unit 3's reproducibility work can improve confidence, but equivalence requires verified inputs and reproducibility evidence. If the exact original artifact is required, restore or republish the verified original bytes when possible.

### 7.6.8 Recovery objectives and backup integrity

Define:

- **RPO (Recovery Point Objective):** how much registry/artifact state the organization can afford to lose.
- **RTO (Recovery Time Objective):** how long it can take to restore the registry or make required artifacts available.
- **Consistency point:** whether metadata and blob storage represent a mutually consistent state.
- **Integrity verification:** whether restored content matches the expected digest and can be pulled/used.
- **Availability alternative:** whether another region, registry, or retained artifact store can serve protected releases.

A snapshot is not a proven backup until a restore has been tested. Back up registry data using a documented, consistency-aware method for the chosen deployment and storage backend. Keep recovery metadata and authorization controls safe from the same failure domain as the registry. **[VERIFY]** There is no single backup command that is correct for every Distribution storage backend or hosted registry.

## 7.7 SRE lens

### 7.7.1 SLIs, SLOs, and alerting

Choose targets based on service criticality, actual workload patterns, and recovery requirements. Do not copy a universal percentage without measurement.

| Signal | Example SLI | Operational use |
|---|---|---|
| Push success | successful pushes / attempted pushes | Detect inability to publish fixes or releases |
| Pull success | successful pulls / attempted pulls, segmented by repository/region | Detect deployment and scale-out risk |
| Push/pull latency | request latency percentiles | Detect registry/backend degradation |
| Storage utilization | used bytes / capacity | Capacity alerting and maintenance planning |
| Time to exhaustion | remaining capacity divided by observed growth rate | Prioritize cleanup/expansion before failure |
| GC duration | elapsed time for a documented GC operation | Maintenance-window planning |
| Reclaimed physical bytes | same-filesystem/backend usage before and after | Evaluate actual capacity impact |
| Policy execution success | valid dry-runs / scheduled runs | Detect stale inputs and broken lifecycle automation |
| Protected-digest survival | protected digests successfully pulled / tested digests | Validate invariant after change |
| Restore success and time | tested restores that pass integrity / duration | Validate RPO/RTO assumptions |

Set warning and critical thresholds using measured growth and required headroom. If the registry stores images for production deployment, do not wait until the filesystem is nearly full to begin a cleanup. Keep enough headroom for expected pushes, temporary files, GC behavior, metadata, and recovery operations. Estimate time-to-capacity from trends, but account for bursty releases and retention holds.

### 7.7.2 Runbook: impending disk-full registry

**Trigger:** storage threshold breached, predicted time-to-full below the agreed buffer, or push failures correlated with storage exhaustion.

1. **Impact assessment:** check push/pull success, active deployments, release pipeline status, storage backend health, replication, and whether any write failures are occurring.
2. **Safe checks:** inspect filesystem/backend metrics, growth trend, recent image pushes, GC history, backups, and registry logs. Confirm the exact mount or object-store account involved.
3. **Mitigation options:** expand capacity if the platform supports a safe expansion; pause nonessential preview publishing; reduce redundant scratch builds through policy; schedule reviewed retention/GC; use an approved alternate registry if already validated.
4. **Do not:** run broad `docker system prune` on a registry host as if it were registry GC; delete all old/untagged content; run GC during writes when the selected implementation forbids it; delete protected digests; or remove the only backup.
5. **Validation:** check free capacity, push/pull health, protected digest pulls, and registry logs. Measure reclaimed bytes rather than estimating them from logical image sizes.
6. **Communication/escalation:** notify platform, release owners, and incident commander; state what operations are paused and the risk to rollback.
7. **Evidence:** preserve metrics, logs, inventory snapshots, dry-run report, approvals, and before/after measurements.
8. **Follow-up:** revisit headroom, retention rules, publication frequency, image size, registry capacity, and alerts.

### 7.7.3 Runbook: suspected accidental deletion

**Trigger:** a known digest cannot be pulled, a tag disappeared unexpectedly, or audit logs show an unapproved deletion.

1. Freeze further destructive lifecycle actions; pause affected rollouts if needed.
2. Confirm registry endpoint, repository, digest, and whether the issue is auth/network/replication rather than deletion.
3. Assess affected active workloads, rollback versions, regions, jobs, and compliance/forensic holds.
4. Preserve registry/API/CI logs, current inventory, release metadata, and relevant timestamps.
5. Identify replica, consistent backup, immutable artifact copy, or verified original build output.
6. Restore/republish through the documented procedure; verify digest and clean-client pull.
7. Validate workload recovery and the rollback path; communicate impact and residual risks.
8. Revoke or narrow compromised credentials, review authorization and audit gaps, and document preventive actions.

**Do not:** rebuild and declare success without checking digest equivalence; delete more artifacts to “clean up”; overwrite tags to hide the event; or expose tokens while collecting logs.

### 7.7.4 Capacity headroom and cost model

A simple planning model is:

`required_capacity = retained_unique_blobs + metadata_and_overhead + expected_growth_during_response + GC/maintenance_headroom + backup_or_snapshot_requirements`

This is a conceptual model, not a universal sizing formula. Validate each term against the registry's actual storage backend. Track storage and egress separately. Regional replication can improve availability but increases storage and transfer costs. Pull-through caches may reduce repeated upstream pulls but introduce cache capacity, freshness, and upstream-availability trade-offs (Unit 6).

## 7.8 Security lens

Use STRIDE as a prompt for threat analysis. The controls below reduce risk but do not guarantee security.

| Threat / STRIDE category | Example | Primary control | How to verify | What the control does not protect against |
|---|---|---|---|---|
| Spoofing | Stolen CI credential publishes an image | Unique service identity, short-lived credentials where supported, TLS, rotation | Review identity mapping; test expired/revoked credential; inspect auth logs | Compromised CI runner may still act as the legitimate identity |
| Tampering | Unauthorized manifest deletion or tag movement | Least privilege, immutable-tag policy where supported, digest-based releases, audit logs | Attempt unauthorized delete/tag update in a disposable test; verify event record | Registry admin compromise or storage-level tampering may bypass some controls |
| Repudiation | Operator denies deleting an image | Centralized, access-controlled audit records and change correlation | Trace a test operation from identity to API event and change record | Missing event coverage or compromised logging can leave gaps |
| Information disclosure | Public or cross-tenant pull reveals private image | Authz, namespace isolation, TLS, secret hygiene | Test anonymous and cross-tenant access; review exposure config | An authorized user can still copy image contents |
| Denial of service | Storage fills or malicious pushes consume capacity | Quotas where supported, monitoring, rate limits, capacity headroom, retention | Test alerts and quota behavior in a lab; review growth forecasts | Quotas and alerts cannot eliminate all capacity exhaustion |
| Elevation of privilege | CI identity has registry-admin permissions | Separate roles, scoped tokens, just-in-time admin access | Inspect effective permissions; negative-test delete/config actions | Identity-provider or registry authorization bugs may bypass policy |
| Malicious upstream artifact | Compromised base image or dependency is published | Trusted sources, digest pinning, provenance/signature verification, scanning | Verify digest and provenance under M12 process | A scan can miss vulnerabilities; trusted publisher can still be compromised |
| Recovery artifact tampering | Backup/replica is changed or deleted | Separate failure domain, access restrictions, integrity checks, tested restores | Restore and verify expected digests; review backup access logs | A digest alone does not prove provenance or benign content |
| Tenant boundary failure | Team A can pull/delete Team B images | Per-tenant identities and permissions; separate instances where necessary | Automated cross-tenant negative tests | Shared infrastructure or admin paths may remain common failure domains |
| Audit gap | Delete API events are not logged | Test event coverage; centralize logs; document compensating controls | Execute a controlled lab operation and verify event fields | If the implementation cannot emit an event, correlation may remain incomplete |

### Security design rules

- Treat registry credentials as secrets. Do not put them in source control, lesson evidence, screenshots, or support tickets.
- Keep publisher, runtime, operator, and administrator identities separate.
- Give CI only the write access it needs, and avoid delete privileges for ordinary publishing.
- Treat registry configuration changes as privileged changes requiring review.
- Use TLS with endpoint validation for networked registry traffic. TLS protects transport, not authorization correctness.
- Preserve vulnerability and incident evidence before deleting or quarantining artifacts.
- Verify the enforcement, not merely the configuration file: test allowed and denied operations.
- Do not assume hosted registry products provide identical immutable tags, retention rules, token scopes, audit events, quotas, or OIDC support.

## 7.9 Production checklist

Use this checklist before a real retention or GC change. A checked box means evidence exists, not that someone believes the step was done.

- [ ] Registry owner, operational owner, and policy approver are documented.
- [ ] Retention policy and exceptions are approved and version-controlled.
- [ ] Active deployed digests and rollback digests are inventoried.
- [ ] Compliance and forensic holds are represented in the protected inventory.
- [ ] Quarantine rules and vulnerability-evidence preservation are defined.
- [ ] Unknown or stale references cause the policy to fail closed.
- [ ] Dry-run output was reviewed and deletion has a separate approval.
- [ ] Exact registry implementation/version, storage backend, configuration, and deletion API behavior are verified.
- [ ] GC safe/read-only/maintenance requirements are verified for the exact version.
- [ ] Writes are controlled during GC where required by official guidance.
- [ ] A consistency-aware backup exists and its restore method has been tested.
- [ ] Protected and rollback digests are pull-tested after the operation.
- [ ] Runtime, CI publisher, operator, and administrator identities have least privilege and distinct credentials.
- [ ] Authentication, authorization, TLS, and audit logging are separately tested.
- [ ] Audit logs are retained and protected against unauthorized alteration.
- [ ] Storage, GC duration, push/pull success and latency, policy failures, and restore signals are monitored.
- [ ] Capacity headroom and time-to-exhaustion thresholds are defined.
- [ ] Break-glass actions are scoped, time-bound, attributable, and reviewed.
- [ ] Lab cleanup is scoped to named lab resources; no broad prune is used as a shortcut.
- [ ] Unresolved `[VERIFY]` tags are cleared or explicitly accepted by the responsible owner before production execution.

## 7.10 Hands-on lab set

### Lab safety rules

- Use only a disposable local registry bound to loopback and synthetic images.
- Confirm free disk before starting: `df -h .` and, if useful, `docker system df`.
- WSL2 stores Docker data according to the chosen Docker Desktop/Engine configuration; available Windows disk and the WSL virtual disk may differ from the path shown by `df`. Check both host and WSL2 capacity.
- Never point the policy script or lab commands at production or an unspecified remote registry.
- Do not run GC until the exact version, configuration, write-freeze procedure, and backup method are verified against official documentation.
- All outputs described below are **[ILLUSTRATIVE]** unless the learner executes the lab and saves actual evidence.
- Cleanup commands name only resources created for this lab. If a resource name already exists, stop and investigate instead of deleting it.

| ID | Goal | Prerequisites | Steps | Expected evidence | Cleanup | Stretch goal |
|---|---|---|---|---|---|---|
| **L7-LAB-01 — Inspect storage references** | Create synthetic images in a disposable local registry and explain tags, manifests, and shared blobs. | Docker running; free disk; `curl`; local port available. | Follow §7.3.2; push two versions; query `/v2/` and tags; record manifest digests using a documented inspection method. | Environment/version record, tag JSON, digest inventory, reference graph, notes on shared blobs. | After preserving evidence, stop/remove only `${LAB_NAME}` container and `${LAB_NAME}-net`; remove `${LAB_NAME}-data` volume only if you accept losing the lab registry; remove `$LAB_DIR` after checking its exact path. | Compare layer digests across FastAPI-like and ETL-like synthetic images. |
| **L7-LAB-02 — Retention policy dry-run** | Apply keep-last-N + promoted + protected/in-use rules to synthetic fixtures. | Python 3; JSON fixtures; script from §7.6.1. | Generate fixture files; run the script; inspect report; test missing/stale/empty protected inventory and malformed digest. | `inventory.json`, `protected.json`, `retention-dry-run.json`, failure-test results, review notes. | Delete only the named fixture files and script from the lab directory after verifying the path. | Add a policy exception field and test deterministic tie-breaking. |
| **L7-LAB-03 — Safe deletion and garbage collection** | Practice the approved sequence and measure actual storage changes in a disposable registry. | Lab 01; exact Distribution version/config known; official docs checked; consistent backup/restore path verified. | Record config/version; inventory protected digests; stop/control writes according to verified guidance; back up; delete only reviewed synthetic manifest digests via supported API; run documented GC command under required safe conditions; measure same storage mount before/after; pull protected digest. If any requirement cannot be verified, stop before deletion/GC. | Version/config record, backup identifier, approved digest list, API status, GC exit status/log, before/after measurement table, protected-pull result. | Restore or retain lab state according to evidence needs; remove only the named lab resources after verifying recovery is no longer needed. | Repeat with shared layers and explain why physical reclaimed bytes differ from image-size totals. |
| **L7-LAB-04 — Restore and access-control drill** | Restore a synthetic artifact and test a read-only identity where enforcement is supported. | Disposable registry; verified backup method; auth configured according to matching docs; no real credentials. | Back up synthetic registry; simulate removal of a test artifact using verified API procedure; restore or republish via documented method; verify digest/pull; attempt push/delete with a read-only identity only if the implementation can enforce that role. | Backup/restore report, digest verification, clean-client pull, allowed/denied permission matrix, sanitized logs. | Remove only named auth files, containers, network, volume, and workspace after evidence capture; never print or commit password hashes/secrets. | Add a negative test for cross-repository access and record the result. |

### Lab 01 — Expected commands, troubleshooting, and abort criteria

Example inspection commands:

```bash
docker ps --filter "name=u7-registry-lab"
docker logs --tail 100 u7-registry-lab
curl --fail --silent --show-error http://127.0.0.1:5007/v2/
curl --fail --silent --show-error http://127.0.0.1:5007/v2/u7-demo/tags/list
```

Expected successful exit status: `0`; exact output is **[ILLUSTRATIVE]** and depends on the image/tag sequence. A connection refusal may mean the container is stopped, the port is occupied, or the service is not reachable from that interface. A push rejection may mean the daemon does not trust the lab's HTTP endpoint. Do not weaken a shared daemon's security configuration to bypass this error.

**Abort if:** a resource name already exists unexpectedly; the endpoint resolves to a remote/production registry; disk space is insufficient; or you cannot tell which Docker daemon the CLI is targeting.

### Lab 02 — Success and failure tests

Success criteria:

- valid fixture input returns status `0`;
- report declares `DRY_RUN_ONLY`;
- protected and promoted digests remain `KEEP`;
- candidates are labelled `CANDIDATE_REVIEW_ONLY`;
- no registry endpoint is used and no deletion occurs;
- malformed/stale/empty protected inventory returns nonzero status.

Troubleshooting:

- JSON parse errors: validate the file and keep UTF-8 encoding.
- Digest validation errors: ensure the fixture uses `sha256:` followed by 64 lowercase hexadecimal characters.
- Stale inventory error: regenerate the synthetic protected fixture; do not disable freshness checks just to get a green run.
- Unexpected candidate: inspect policy precedence and protected digest membership before changing the code.

Cleanup should remove only the files you created. Do not use `rm -rf "$HOME"` or a broad path pattern. Check `printf '%s\n' "$LAB_DIR"` and inspect contents before deleting a temporary directory.

### Lab 03 — Safe deletion and GC: guarded procedure

This lab is intentionally gated by documentation verification. It is unsafe to publish a universal destructive command sequence without knowing the registry version, configuration, and storage backend.

Before proceeding, fill in this record:

```text
Registry implementation/version:
Container image digest or package version:
Storage backend/driver:
Deletion enabled and configuration reference:
Manifest deletion API behavior verified from:
GC command syntax verified from:
Documented write-freeze/read-only requirement:
Backup/snapshot method and restore test:
Protected digest inventory source and timestamp:
Maintenance window and approver:
Abort owner/contact:
```

Then:

1. Save the complete pre-change tag/manifest inventory.
2. Save the protected/in-use digest list and verify it against release/deployment/DR records.
3. Record storage used/free on the exact registry volume/backend.
4. Take a consistency-aware backup and confirm the recovery path.
5. Obtain approval for a short list of synthetic manifest digests.
6. Control writes exactly as required by the selected version's official documentation.
7. Delete only the approved synthetic manifests via the verified procedure.
8. Run the exact documented GC operation. Do not assume a `--dry-run` option exists.
9. Measure the same storage system before and after.
10. Pull the protected digest and a retained rollback artifact.
11. Resume writes only after health checks pass.

Results template (leave blank until measured):

| Field | Result |
|---|---|
| Registry version/config | ______ |
| Storage backend | ______ |
| Used bytes before | ______ |
| Free bytes before | ______ |
| GC start/end | ______ |
| GC exit status | ______ |
| Used bytes after | ______ |
| Free bytes after | ______ |
| Net physical free-space change | ______ |
| Protected digest pull result | ______ |
| Rollback artifact pull result | ______ |
| Push/pull health after maintenance | ______ |
| Evidence location | ______ |

**Success criterion:** the exact protected digests remain pullable, registry health is restored, the procedure is auditable, and all byte claims are based on measurements. If the version-specific safe procedure is unknown, the successful outcome is an aborted exercise with a documented verification gap—not an improvised GC run.

### Lab 04 — Restore and access-control drill

Use only a lab-specific identity and synthetic data. Do not reuse a personal or production credential. If the registry implementation cannot express read-only permissions, record the limitation rather than claiming a negative test passed.

Test matrix:

| Test | Expected result | Evidence |
|---|---|---|
| Anonymous pull, when anonymous access should be disabled | Denied | Sanitized status/result |
| Read-only identity pulls allowed repository | Allowed | Successful pull and identity label |
| Read-only identity pushes | Denied | Denial status and registry log |
| Read-only identity deletes | Denied or not exposed to that role | Denial status and permission config |
| CI publisher pushes to assigned repository | Allowed | CI identity and push result |
| CI publisher deletes or changes registry config | Denied | Negative-test result |
| Restored artifact pulled by digest | Allowed and digest matches expected record | Pull output and digest verification |

A failed negative test is a security finding. Do not solve it by granting broader permissions; change the policy or isolate the registry so the intended boundary is enforceable.

### Cleanup procedure

Only clean up when evidence has been captured and no restore test depends on the lab state. Verify each resource by its exact name first:

```bash
docker ps -a --filter "name=u7-registry-lab"
docker network ls --filter "name=u7-registry-lab-net"
docker volume ls --filter "name=u7-registry-lab-data"
```

Then, if and only if these are the resources created by your lab:

```bash
docker rm -f u7-registry-lab
docker network rm u7-registry-lab-net
# This removes the lab registry's persistent data; use only after evidence capture.
docker volume rm u7-registry-lab-data
```

Do not run broad `docker system prune` commands as cleanup. If the names conflict with pre-existing resources, do not run the removal commands.

## 7.11 Self-check questions

Answer before reading the key.

1. **MCQ — Shared blobs:** Image A and Image B reference the same layer digest. If A's manifest is deleted, what can you conclude about the shared blob?
   - A. It is always deleted immediately.
   - B. It remains needed if a retained manifest still references it; GC behavior must be verified.
   - C. The tag for B must be deleted too.
   - D. Local `docker image prune` will reclaim it from the registry.

2. **MCQ — Local versus registry cleanup:** Which statement is correct?
   - A. `docker system prune` is the standard server-side Distribution GC command.
   - B. `docker image prune -a` deletes remote registry tags.
   - C. Docker prune commands act on the selected local Docker daemon; registry retention/GC is separate.
   - D. Deleting a local image always deletes its remote manifest.

3. **Short answer — In-use digests:** Why is a complete deployed and rollback digest inventory required before calculating deletion candidates?

4. **MCQ — GC safety:** You have a registry that is accepting pushes. The GC documentation for its version requires a read-only/maintenance condition. What should you do?
   - A. Run GC quickly between pushes.
   - B. Run GC concurrently and monitor logs.
   - C. Follow the documented write-control procedure, take/verify backup, and run only in the approved window.
   - D. Assume `--dry-run` exists and test it on production.

5. **Short answer — Untagged:** Why is “untagged” not a universal synonym for “safe to delete”?

6. **MCQ — Authn/authz:** A user successfully authenticates to the registry. What remains to be established?
   - A. Nothing; authentication grants all repository actions.
   - B. Authorization must still decide whether the identity may pull, push, or delete the requested resource.
   - C. TLS can replace authorization.
   - D. Audit logs are no longer necessary.

7. **Short answer — Least privilege:** What permissions should a normal CI publisher have, and which permissions should ordinarily be withheld?

8. **Scenario — Disk pressure:** Registry storage is near full, and several old images appear untagged. State the safe first actions and at least three actions you must not take.

9. **Scenario — Accidental deletion:** A production digest cannot be pulled after an administrator's action. Describe triage, evidence preservation, recovery options, and validation. Why is rebuilding not automatically identical to restoring the original artifact?

10. **Short answer — Vulnerability response:** Why should a critical scanner finding trigger a lifecycle decision rather than automatic immediate deletion?

### Answer key and reasoning

1. **Correct: B.** Blobs can be shared. Deleting one manifest does not make a blob reclaimable if another retained manifest still references it; exact GC semantics depend on the registry implementation. A is tempting because manifest deletion feels like image deletion, but ignores shared references. C is wrong because tags and manifests are separate references. D is wrong because local prune is not registry GC.
2. **Correct: C.** Docker prune commands operate on local daemon resources. A confuses the local CLI with the registry's GC command; B confuses local image deletion with a remote API; D incorrectly assumes local and remote storage are coupled.
3. A workload or rollback record can refer to a digest even if no obvious tag remains. Without complete references, a policy can delete an artifact needed for production recovery. Unknown or stale inventory must fail closed.
4. **Correct: C.** The exact version's documented operating condition controls. A and B knowingly violate the requirement; D invents a flag and proposes production experimentation. A retention-script dry-run is not a substitute for GC safety.
5. Registry APIs and tools differ in how they define untagged content; there may also be index/platform or external references not represented by a tag list. Eligibility must be determined by policy and reference inventory, not a label alone.
6. **Correct: B.** Authentication identifies the caller; authorization decides the permitted action. A conflates identity with privilege, C conflates transport security with policy, and D ignores accountability.
7. CI should push only to designated repositories and read required base images. It should ordinarily have no delete, registry configuration, or broad administrator permissions. Separate CI identities by workload/team and test denied actions.
8. Inventory the exact registry/version/backend, assess push/pull impact and growth, preserve evidence, validate protected digests, and use a reviewed dry-run plus a documented maintenance/GC procedure. Do not run broad local prune as registry GC; do not delete all old/untagged images; do not run GC during writes if prohibited; do not delete protected artifacts or remove the only backup.
9. Pause destructive actions and risky rollouts; confirm endpoint/digest and distinguish deletion from auth/network failure; assess blast radius; preserve API/CI/release logs; locate a verified replica, consistent backup, or original artifact; restore/republish and verify digest/pull; validate workload and rollback. A rebuild may differ due to changed base images, dependencies, timestamps, or toolchain inputs.
10. The image may be deployed, required for rollback, under investigation, or the only forensic artifact. Quarantine/block promotion, preserve evidence, remediate, update references, and delete only when policy and holds permit.

## 7.12 Evidence artifacts

Suggested learner evidence layout under the module (these files are recommendations; they do not already exist merely because they are listed here):

```text
evidence/unit-07-registry-lifecycle/
├── environment-and-version-inventory.md
├── synthetic-registry-inventory.json
├── protected-digests.txt
├── retention-policy.yaml
├── retention-dry-run.json
├── deletion-approval.md
├── gc-before-after-measurements.md
├── access-control-test-results.md
├── restore-drill-report.md
├── incident-runbook-disk-full.md
├── incident-runbook-accidental-deletion.md
└── lessons-learned.md
```

Minimum useful evidence:

- exact registry implementation/version and image digest/package version;
- relevant configuration excerpts with secrets removed;
- complete synthetic tag/manifest/digest inventory;
- source and timestamp for protected/in-use digest inventory;
- retention policy version and dry-run output;
- approval record identifying exact candidate digests;
- GC command/version and exit status, if actually run;
- before/after storage measurements from the same backend/mount;
- protected-digest and rollback pull results;
- access-control positive and negative tests;
- backup/restore validation and elapsed time;
- incident communication and lessons learned, if an incident exercise was performed.

Do not commit passwords, password hashes unless specifically required in a protected training repository, access tokens, authorization headers, private registry addresses, customer identifiers, unredacted security findings, or sensitive logs. Use sanitized examples and keep secret-bearing raw evidence in the approved restricted system. Evidence should be sufficient for another engineer to reproduce the reasoning without granting them access to credentials.

## 7.13 Common interview and design-review questions

### 1. Defend a retention strategy for a regulated data platform with limited storage.

**Model answer:** Separate scratch/preview artifacts from production releases. Keep the last N for routine release history, but override that rule for active deployment digests, approved rollback versions, promoted releases, and legal/forensic holds. Keep digest-based release records and require an authoritative, fresh reference inventory. Calculate candidates deterministically, fail closed on missing references, emit a dry-run report, and require separate approval for deletion. Measure actual unique/physical storage and maintain capacity headroom. The retention period should be agreed by compliance, security, service owners, and platform operations based on applicable obligations, incident needs, release cadence, RPO/RTO, and cost—not chosen only to fit current disk. Trade-off: longer retention increases storage/egress/backup cost; shorter retention can reduce recovery options and forensic evidence.

### 2. Why can manifest deletion fail to reduce disk usage?

**Model answer:** The manifest may still be referenced by another tag or index; blobs may be shared by retained manifests; deletion may only remove metadata/reference state; and GC may be a separate maintenance operation. Storage backend allocation and snapshots can also delay visible physical-space reduction. I would inspect digest relationships and configuration, then measure actual filesystem/backend usage before and after a verified GC.

### 3. How would you prove a retention automation is safe?

**Model answer:** Validate schema and digest format; consume a complete and fresh protected inventory; treat unknown references as protected; make output deterministic; default to dry-run; emit machine-readable decisions and reasons; test malformed/stale/missing inputs; keep execution separate; require approval and exact digest scope; record audit events; test in a disposable registry; and prove protected digest survival and restore. A green unit test is not proof that the external inventory is complete.

### 4. How do authentication and authorization differ in registry operations?

**Model answer:** Authentication establishes identity; authorization maps that identity to permitted actions/resources. TLS protects the channel and authenticates the endpoint; auditability records actions. I would use separate runtime, CI, operator, and administrator identities, test negative actions, and verify the actual registry implementation enforces repository-level boundaries. A successful login or a TLS connection does not imply least privilege.

### 5. What is your response if a production image is accidentally deleted?

**Model answer:** Pause further destructive actions and risky rollouts; confirm the exact digest and whether the problem is truly deletion; assess blast radius; preserve audit and CI evidence; locate a verified replica, consistency-aware backup, or original artifact; restore and pull by digest from a clean client; validate the workload and rollback path; communicate status; then narrow permissions and improve audit/approval controls. Rebuild only if acceptable and inputs/reproducibility are proven; a new build digest is not automatically the original artifact.

## 7.14 Sources and verification notes

**Source verification status:** Current official source pages were not independently opened or checked during this lesson-generation run. The links below are primary documentation entry points to verify before executing version-sensitive commands. Therefore, claims requiring source confirmation remain `Needs verification`; no claim is marked `Verified` solely because a source URL is listed.

1. CNCF Distribution Registry documentation and repository: <https://distribution.github.io/distribution/> and <https://github.com/distribution/distribution>
2. Distribution configuration reference: <https://distribution.github.io/distribution/about/configuration/>
3. Distribution HTTP API reference: <https://distribution.github.io/distribution/spec/api/>
4. Docker CLI reference — `docker image prune`: <https://docs.docker.com/reference/cli/docker/image/prune/>
5. Docker CLI reference — `docker system prune`: <https://docs.docker.com/reference/cli/docker/system/prune/>
6. Docker Engine security / protect access to the daemon: <https://docs.docker.com/engine/security/>
7. Docker documentation — registry authentication/configuration: start from <https://docs.docker.com/> and follow the current registry/authentication documentation matching your Engine version.
8. STRIDE threat-modeling background: Microsoft Security Development Lifecycle threat modeling guidance, or an equivalent organizational standard; verify the current official page before citing it in a formal design.
9. OCI image specification, including image manifest/index concepts: <https://github.com/opencontainers/image-spec>

### Verification procedure

For every real registry, record the implementation, version, deployment mode, and storage backend before relying on a command. Then:

- read the matching version's deletion configuration and HTTP API documentation;
- verify whether manifest deletion is enabled and the exact request/response semantics;
- verify GC command syntax and documented safe operating conditions;
- confirm whether the selected release requires read-only mode or another write-control mechanism;
- verify storage-driver and backup consistency requirements;
- test authentication and authorization with positive and negative cases;
- verify audit event coverage and retention;
- run the full sequence against a disposable instance before proposing a production change.

Hosted registries may offer retention policies, immutable tags, quotas, repository-level roles, robot accounts, audit events, replication, and OIDC/workload identity, but these vary by product, tier, and configuration. Compare current official documentation and account-specific terms rather than assuming feature parity.

## Appendix A — Registry Lifecycle Decision Record (ADR) Template

```markdown
# ADR: Registry Retention, Deletion, and GC

- Status: Proposed / Accepted / Superseded
- Decision owner:
- Review date:
- Registry implementation and version:
- Deployment mode and storage backend:
- Repositories/tenants in scope:
- Related change / incident ID:

## Context
- Current capacity and growth:
- Release cadence and rollback requirements:
- Compliance/forensic requirements:
- RPO/RTO:
- Known failure modes:

## Constraints
- Registry/API/version limitations:
- Maintenance window:
- Budget and storage constraints:
- Access-control limitations:

## Options considered
1. Keep-last-N:
2. Age-based retention:
3. Promotion/in-use/hold protection:
4. Capacity expansion or alternate registry:
- Rejected alternatives and reasons:

## Decision and policy
- Keep-last-N by repository/channel:
- Age rule:
- Protected digest sources:
- Hold/quarantine rules:
- Missing/stale inventory behavior:
- Dry-run and approval requirements:
- Execution mechanism:

## Access roles
- Runtime pull:
- CI publisher:
- Operator:
- Administrator / break-glass:
- Credential storage and rotation:

## Operational safety
- Version-specific deletion/GC procedure:
- Write freeze/read-only requirement:
- Backup/snapshot procedure:
- Pre/post measurements:
- Abort criteria:

## Recovery
- Backup/replica location (avoid secrets):
- Restore verification:
- Protected digest test:
- RPO/RTO validation:
- Rollback/reversal plan:

## Cost and observability
- Storage and egress estimate/method:
- Capacity headroom:
- Push/pull SLI/SLO:
- GC and policy metrics:
- Audit log location/retention:

## Approval and review
- Service owner:
- Security/compliance:
- Platform/SRE:
- Approval date:
- Exceptions and expiry:
- Next review date:
```

## Appendix B — Retention Policy and Deletion Safety Checklist

### Policy design

- [ ] Scope is explicit by registry, repository, tenant, and artifact type.
- [ ] Policy includes keep-last-N and age rules where appropriate.
- [ ] Promoted/released artifacts are handled explicitly.
- [ ] Active and rollback digests are protected by digest, not only tag.
- [ ] Compliance, legal, and forensic holds override ordinary deletion rules.
- [ ] Quarantine state is distinct from deletion eligibility.
- [ ] Scratch/preview repositories have separately approved rules.
- [ ] Ordering and tie-breaking are deterministic.
- [ ] Missing/stale/contradictory references fail closed.
- [ ] Policy owner, approver, exception path, and review cadence are documented.

### Before deletion/GC

- [ ] Exact implementation/version/backend recorded.
- [ ] API/configuration and GC behavior verified for that version.
- [ ] Write-control procedure verified.
- [ ] Protected digest inventory reconciled and timestamped.
- [ ] Consistency-aware backup/snapshot completed and restore path tested.
- [ ] Dry-run report generated and reviewed.
- [ ] Candidate digest list scoped and approved separately.
- [ ] Credentials are not exposed in logs or shell history.
- [ ] Monitoring, maintenance window, communication, and abort owner are ready.

### After deletion/GC

- [ ] API response and command exit status captured.
- [ ] Physical/backend storage measured using the same method as before.
- [ ] Protected and rollback digests pulled and validated.
- [ ] Push/pull health, latency, and logs checked.
- [ ] Writes resumed only after the validation gate.
- [ ] Exceptions, deviations, and follow-up actions recorded.
- [ ] Backup and audit evidence retained under the approved policy.

## Appendix C — Claim Register

**Status definitions:** `Verified` means the exact cited source was checked during this run; `Needs verification` means it must be checked against current official documentation and the target version; `Illustrative` means it is a conceptual example or synthetic fixture. No technical behavior claim below is marked `Verified`, because current source pages and commands were not independently checked in this run.

| ID | Claim | Source or verification method | Version-sensitive? | Status | Notes |
|---|---|---|---|---|---|
| C01 | Tags are references and should not be the only production identity. | Unit 5; OCI image specification | Some implementation details | Needs verification | Store digest in release records. |
| C02 | A manifest describes config/layer references. | OCI image specification | Specification version may matter | Needs verification | Verify current OCI spec. |
| C03 | Image indexes can reference platform-specific manifests. | OCI image specification | Specification/version | Needs verification | Preserve required platform artifacts. |
| C04 | Multiple manifests can share content-addressed blobs. | OCI image specification; inspect manifest digests | Implementation details | Needs verification | Do not assume sharing without comparing digests. |
| C05 | Removing one manifest does not imply every referenced blob is reclaimable. | Distribution GC docs; test isolated registry | Yes | Needs verification | Shared blobs may remain referenced. |
| C06 | “Untagged” and “dangling” are not universal synonyms. | Compare API/tool semantics for target version | Yes | Needs verification | Terminology differs by context. |
| C07 | Registry storage and local Docker daemon storage are separate. | Docker CLI docs; Distribution docs | Some deployment details | Needs verification | Confirm daemon/endpoint in use. |
| C08 | `docker image prune` operates on local daemon images. | Docker CLI `image prune` reference | Yes, exact semantics | Needs verification | Not registry GC. |
| C09 | `docker image prune -a` has broader local eligibility than default prune. | Docker CLI `image prune` reference | Yes | Needs verification | Check current prompt/filter behavior. |
| C10 | `docker system prune` cleans local Docker resources according to options. | Docker CLI `system prune` reference | Yes | Needs verification | Never treat as registry GC. |
| C11 | Retention should protect deployed and rollback digests. | Organization's release/deployment policy | Policy-dependent | Needs verification | Requires authoritative inventory. |
| C12 | Keep-last-N alone can miss an older but required digest. | Policy scenario and release inventory | No | Illustrative | Demonstrated by synthetic example. |
| C13 | Age-only deletion can violate hold/rollback requirements. | Retention policy review | No | Illustrative | Explicit precedence is required. |
| C14 | Distribution deletion depends on configuration and version. | Matching Distribution configuration reference | Yes | Needs verification | Check exact release. |
| C15 | Manifest deletion API behavior must be checked for target deployment. | Distribution HTTP API reference and lab | Yes | Needs verification | Do not assume API is enabled. |
| C16 | Manifest deletion may not immediately reclaim physical bytes. | Distribution GC documentation and measurement | Yes | Needs verification | Measure backend usage. |
| C17 | Distribution GC syntax and flags are version-sensitive. | `registry garbage-collect` help/docs for installed release | Yes | Needs verification | Do not assume a dry-run flag. |
| C18 | GC can be unsafe during concurrent writes if docs prohibit them. | Official docs for selected Distribution version | Yes | Needs verification | Follow exact write-control procedure. |
| C19 | A separate policy dry-run can calculate candidates without deleting. | Inspect/test provided Python fixture | Script-specific | Illustrative | Script does not contact a registry. |
| C20 | Physical free space differs from logical image-size totals. | Measure filesystem/backend; inspect shared blobs | Backend-dependent | Needs verification | Keep before/after method consistent. |
| C21 | Authentication establishes identity; authorization decides permissions. | Security architecture and registry auth docs | Implementation-specific details | Needs verification | Test actual enforcement. |
| C22 | Basic/htpasswd auth alone does not imply fine-grained repository authorization. | Distribution auth docs and selected auth configuration | Yes | Needs verification | Avoid overstating basic auth. |
| C23 | Token-auth scope/challenge details are implementation-specific. | Target registry token-auth documentation | Yes | Needs verification | Verify issuer, audience, scopes, keys. |
| C24 | TLS protects transport but does not replace authorization. | TLS/registry security documentation | Configuration-dependent | Needs verification | Validate certificate and endpoint. |
| C25 | CI publishers should not routinely hold delete/admin permissions. | Least-privilege design review | Organization-specific | Illustrative | Validate with negative tests. |
| C26 | OIDC/short-lived identity support differs by registry and CI platform. | Current vendor docs for exact products | Yes | Needs verification | Awareness topic only. |
| C27 | Audit logs may be incomplete and need event-coverage testing. | Controlled test operation and log review | Yes | Needs verification | Document compensating controls. |
| C28 | Break-glass access should be scoped and time-bound. | Organization security/change policy | Policy-dependent | Illustrative | Template recommendation. |
| C29 | A vulnerability finding alone is not a complete retention decision. | Incident-response and evidence-retention policy | Policy-dependent | Illustrative | Quarantine and preserve evidence. |
| C30 | Rebuilding from source may not reproduce the exact original digest. | Unit 3 reproducibility tests; compare digests | Build-specific | Needs verification | Inputs and environment may have changed. |
| C31 | Registry backup consistency requirements depend on backend/deployment. | Official docs for chosen backend and restore test | Yes | Needs verification | Do not casually copy live storage. |
| C32 | A backup is not proven until a restore is tested. | Restore-drill evidence | Procedure-specific | Illustrative | Validate digest and pull. |
| C33 | RPO and RTO describe different recovery objectives. | Organization's DR policy/standard | Policy-specific | Needs verification | Define for registry/artifact service. |
| C34 | Capacity headroom should account for growth and recovery needs. | Observed growth and capacity planning | Environment-specific | Illustrative | No universal threshold prescribed. |
| C35 | Egress and storage costs are separate dimensions. | Provider pricing and measured usage | Provider-dependent | Needs verification | Verify current pricing/tier. |
| C36 | Hosted registry retention/immutability features vary by product/tier. | Current official vendor docs | Yes | Needs verification | Do not assume parity. |
| C37 | A protected tag does not necessarily prevent administrator deletion. | Test target registry's immutability/deletion controls | Yes | Needs verification | Digest protection and authorization both matter. |
| C38 | A digest match is not by itself proof of provenance or benign content. | OCI digest semantics; M12 supply-chain controls | No, policy-dependent | Needs verification | Verify signatures/provenance separately. |
| C39 | Cross-tenant authorization should be tested with negative cases. | Controlled access-control lab | Implementation-specific | Illustrative | Record denied push/pull/delete outcomes. |
| C40 | The provided synthetic script cannot delete registry content. | Code inspection; no registry client/API calls present | No | Illustrative | It only reads/writes local JSON. |
| C41 | Stale/missing protected inventory should stop destructive action. | Policy safety requirement and script tests | No | Illustrative | Fail closed. |
| C42 | A registry disk-full incident can impair push and deployment recovery. | Operational monitoring and incident records | Environment-specific | Needs verification | Measure local impact. |
| C43 | Restore by digest from a clean client is useful validation. | Controlled restore drill | Implementation-specific | Illustrative | Record actual digest and result. |
| C44 | A cache/mirror does not replace authoritative artifact retention. | Unit 6 architecture and target cache behavior | Yes | Needs verification | Verify cache eviction/freshness semantics. |
| C45 | BuildKit cache is distinct from published image retention. | Docker BuildKit documentation and registry model | Yes | Needs verification | Unit 4 cross-reference. |
| C46 | Quarantine and deletion are separate lifecycle actions. | Security/incident policy | Policy-dependent | Illustrative | Preserve evidence first. |
| C47 | A policy report is not deletion approval. | Change-control design | Organization-specific | Illustrative | Separate reviewer and executor. |
| C48 | Registry health checks should include push/pull success and latency. | SRE monitoring design | Environment-specific | Illustrative | Establish baselines and SLOs. |
| C49 | WSL2 free-space reporting may differ from host/virtual disk capacity. | Verify Docker/WSL2 storage setup on target machine | Environment-specific | Needs verification | Inspect host and guest capacity. |
| C50 | Cleanup should target only resources created by the lab. | Inspect named Docker resources before removal | No | Illustrative | No broad prune. |

## Appendix D — Human Verification Checklist

Before treating this lesson as executable guidance, verify each item:

- [ ] Exact registry implementation and version are recorded.
- [ ] The `registry:2` image/version/digest used in the lab is recorded.
- [ ] Storage backend/driver and registry data path are known.
- [ ] Exact configuration schema and deletion setting are checked against the matching official docs.
- [ ] Manifest deletion API method, digest header/identity, response codes, and behavior are verified.
- [ ] GC command syntax and flags are verified from the installed release's official docs/help.
- [ ] GC safe-write/read-only/maintenance requirement is confirmed for the exact version.
- [ ] No unverified `--dry-run` or other flag is used.
- [ ] Local Docker prune semantics are checked against the installed CLI reference.
- [ ] Lab HTTP/TLS behavior is understood; no shared daemon security was weakened.
- [ ] Authentication file format, hash algorithm support, mount path, and configuration syntax are verified.
- [ ] Authorization enforcement is tested for pull, push, delete, and cross-repository access.
- [ ] Protected inventory is complete, timestamped, and validated against deployment, rollback, DR, and hold records.
- [ ] Policy handles missing, stale, malformed, and contradictory input by failing closed.
- [ ] Dry-run report is deterministic and candidates have reasons.
- [ ] Deletion approval is separate from dry-run generation.
- [ ] Backup method is consistency-aware and restore has been tested.
- [ ] Protected and rollback digests survive and are pullable after the operation.
- [ ] Storage before/after measurements use the same filesystem/backend and units.
- [ ] Audit event coverage and retention are verified.
- [ ] Credentials/tokens/private registry addresses are not present in committed evidence.
- [ ] Cleanup commands reference only the named lab resources.
- [ ] All source links resolve to the intended official documentation.
- [ ] Every unresolved `[VERIFY]` or `[VERSION-SENSITIVE]` tag has an owner and disposition.
- [ ] No command or lab is described as executed unless an execution record exists.

## Appendix E — Known Limitations and Sign-off

### Execution record

- **Commands executed during authoring:** None.
- **Hands-on labs executed during authoring:** None.
- **Registry implementation/version tested during authoring:** None.
- **Live official documentation checked during authoring:** None.
- **Static content review:** Section order, required four levels, required lab themes, evidence layout, claim register count, and appendices were included in this draft.
- **Repository inspection:** The authoritative syllabus and `Roadmap_ptree.md` were not independently inspected in this run; this document follows the supplied Unit 7 prompt. No claim is made that repository placement or neighboring files were verified.
- **File write scope:** Intended output is only `07-registry-retention-garbage-collection-and-access-control.md`; no other repository file should be modified.

### Unresolved version-sensitive items

- Distribution version and exact `registry:2` image digest.
- Registry deletion configuration and API behavior.
- GC command flags, safe operating mode, and concurrent-write constraints.
- Storage-driver-specific GC and backup/restore behavior.
- Local Docker daemon handling of the lab's HTTP endpoint.
- `htpasswd` format/configuration and any token-auth integration.
- Hosted registry immutability, retention, authz granularity, OIDC, audit, quota, and cost features.
- Exact CLI output, exit status, response codes, physical bytes reclaimed, GC duration, and restoration time.

### Limitations of the synthetic lab

The local synthetic registry is useful for learning references, API inspection, and the change-control sequence. It does not prove production-scale capacity, hosted-registry behavior, multi-region replication, enterprise authorization, compliance retention, storage-driver semantics, or disaster recovery. The policy script processes local fixtures only; it is intentionally not a general-purpose remote registry cleanup tool. All sample digest labels and tables are synthetic unless produced by an actual learner run.

### Ten-pass audit summary

| Pass | Result | Evidence / limitation |
|---|---|---|
| 1. Scope audit | PASS — content scope | Target filename and Unit 7 scope are used; no unrelated lesson is authored. Repository tree itself was not independently inspected. |
| 2. Syllabus audit | PASS — prompt coverage | Required retention, GC, access control, governance, SRE, security, recovery, labs, and appendices are present. |
| 3. Progression audit | PASS | Exactly L1, L2, L3, and L4 appear in the required order. |
| 4. Operational safety audit | PASS WITH LIMITATION | Dry-run-only policy script, fail-closed protected inventory, explicit approval separation, lab isolation, and cleanup warnings included. Real GC remains gated on version-specific verification. |
| 5. Technical accuracy audit | NOT PRODUCTION-VERIFIED | Version/config/API/GC semantics are explicitly marked for verification; no live source or command execution was performed. |
| 6. Security audit | PASS — design coverage | Authn/authz/TLS/audit distinction, least privilege, secret hygiene, tenant boundaries, quarantine, and break-glass are covered; actual enforcement not tested. |
| 7. SRE audit | PASS — design coverage | SLIs/SLO framing, capacity headroom, disk-full and deletion runbooks, restore objectives, and validation included; no measurements collected. |
| 8. Lab audit | PASS — instructions supplied | Four local/free lab themes include evidence, troubleshooting, cleanup, and abort criteria; labs were not executed. |
| 9. Evidence/source audit | PASS WITH LIMITATION | Evidence layout, 50 claim rows, verification checklist, and limitations included. Official URLs are entry points, not claims of live verification. |
| 10. Repository protection audit | PASS — intended scope | Only the target lesson is intended to be generated. No repository edits were performed or independently verified. |

### Sign-off

**Status: DRAFT-AUDITED — NOT PRODUCTION-VERIFIED.**

The lesson meets the content structure and safety-design requirements of the supplied prompt, but the technical verification pass remains incomplete until the exact registry version, configuration, API, GC operating conditions, authentication/authorization enforcement, backup method, and restore procedure have been checked and tested. Do not use this document alone as authorization to delete registry artifacts or run garbage collection in production.
