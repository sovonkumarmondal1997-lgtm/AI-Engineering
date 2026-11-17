# Chart Repositories, OCI Registries, and Signing

**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Module:** M06 — Helm, Kustomize, and Kubernetes Packaging  
**Unit:** 7 — Chart repositories, OCI registries, and signing  
**Target file:** `07-chart-repositories-oci-registries-and-signing.md`

> **Source-verification note:** The Unit 7 requirements supplied with this chapter were available and used as the authoritative scope. The separate `Roadmap_ptree.md` and the full M06 syllabus source were not available for independent inspection in this authoring context. The chapter therefore preserves the supplied Unit 7 requirements, refers to M01/M02/M09/M12 as requested, and does not claim to have verified repository paths or prior-lab configuration. Where local setup or tool behavior may vary, use the explicit `[VERIFY]` steps.

> **Operational status:** All commands and file contents below are instructional examples. They have not been executed against your machine, registry, or cluster. Do not treat illustrative references, digests, or outcomes as observed evidence.

## 1. Module placement

This unit teaches the release and consumption lifecycle of Helm charts after chart authoring, testing, and packaging basics. The objective is not merely to upload a `.tgz`; it is to make the exact chart content identifiable, retrievable, verifiable, reviewable, and supportable throughout its lifecycle.

The unit builds on:

- M01 registry fundamentals, including the local `registry:2` instance, TLS/basic authentication, and registry/replication concepts.
- M02 CI/CD design and protected release pipelines.
- M06 Units 2–4 for chart structure, values, dependencies, testing, and versioning.
- M06 Units 5–6 for Kustomize and packaging decisions.
- M09 for secrets and identity.
- M12 for attestations and broader supply-chain policy/enforcement.

This unit does **not** implement a complete organization-wide signing service, keyless identity system, admission controller, vulnerability-management program, or artifact-attestation platform.

## 2. Why chart distribution and signing matter

A Helm chart is executable deployment logic in the broad operational sense: templates and values determine Kubernetes objects that can create workloads, services, roles, service accounts, network policies, storage, and other resources. A chart may be syntactically valid and still be dangerous. A chart that arrives intact may still come from an unapproved publisher. A signature may validate mathematically while the signing key is not trusted or the signer is not authorized.

A production chart lifecycle must answer separate questions:

| Question | Control/evidence |
|---|---|
| What exact bytes were released? | Package checksum or OCI digest, recorded with release evidence |
| Where did the package come from? | Approved source, registry audit logs, source revision, publisher identity |
| Were the bytes altered after signing? | Signature or provenance verification against the exact artifact |
| Is the signer trusted? | Independently authenticated trust root and explicit trust policy |
| Is the signer authorized for this chart? | Policy mapping identities/keys to repositories, projects, and release scopes |
| Is the chart safe to deploy? | Template and rendered-manifest review, policy checks, dependency/image assessment |
| What will run? | Pinned image references, deployment inventory, rollout evidence, runtime controls |

These are different controls. Do not collapse them into the single statement “the chart is signed.”

A reliable release policy also avoids overwriting published chart versions. If the same human-readable version can resolve to different content over time, incident response and forensic reconstruction become much harder. Immutable release behavior should be enforced by CI policy and registry permissions, even if a particular backend technically allows replacement.

## 3. Prerequisites and safety boundaries

### Required tools

- Helm 3 or a compatible installed Helm release.
- Python 3 for the local HTTP server.
- A GPG implementation for the classic Helm provenance lab.
- Cosign for the OCI signature lab.
- The M01 local `registry:2` service, configured as described in M01 Unit 6.
- Optional: `kind` and `kubectl` for the final install exercise.
- Optional: `sha256sum`, `jq`, Syft, and registry-specific inspection tools.

Record actual versions; do not copy versions from this chapter as if they described your machine.

```bash
# Run from a terminal in the lab workspace or home directory.
mkdir -p chart-distribution-lab/evidence
cd chart-distribution-lab

{
  date -Is
  helm version
  cosign version
  gpg --version | head -n 2
  python3 --version
  kubectl version --client 2>/dev/null || true
  kind version 2>/dev/null || true
} > evidence/versions.txt
```

`cosign version` and optional client commands can differ across releases. If a command is unavailable, record that fact rather than fabricating a version. Determine the registry implementation and version from the M01 setup, container image reference, or its operator interface.

### Define local placeholders

Substitute the actual values from M01 Unit 6 before running OCI commands:

- `<LOCAL_REGISTRY_HOST>`: registry hostname reachable from the terminal where Helm runs.
- `<LOCAL_REGISTRY_PORT>`: actual exposed port.
- `<LOCAL_REGISTRY>`: host and port combined, without a scheme, e.g. the value you verified locally.
- `<REGISTRY_CA_FILE>`: CA certificate path if the registry uses a private CA.
- `<REGISTRY_READ_USER>` / `<REGISTRY_PUSH_USER>`: account names with pull-only or push permissions.
- Passwords: enter interactively or through a supported standard-input mechanism; do not put a real password in a command, source file, shell history, screenshot, or log.
- `<CHART_NAME>` and `<CHART_VERSION>`: values read from `Chart.yaml`.
- `<NAMESPACE>`: a disposable lab namespace, not a production namespace.
- `<PUBLIC_KEY_PATH>`: path to a lab public verification key.

**Do not infer registry host, port, certificates, username, password, or TLS behavior.** Inspect M01 Unit 6 and confirm the registry is reachable from your WSL2 environment. A host address that works from the host OS may not work from a container or a `kind` node.

### Safety rules

1. Use throwaway GPG and Cosign keys only.
2. Never commit private keys or registry credentials.
3. Do not disable TLS verification as a generic fix for certificate errors.
4. If a disposable lab registry is HTTP-only, use only the exact local-only option documented by the installed Helm version; do not send production credentials over plaintext HTTP.
5. Before cluster operations, check `kubectl config current-context`, the cluster identity, and the namespace.
6. Never delete a shared registry namespace or all registry storage as cleanup.
7. Preserve original packages, signatures, digests, and evidence until tamper tests and incident exercises are complete.

## 4. Learning objectives and success criteria

By the end of this unit, the learner should be able to:

- Explain HTTP chart repositories and OCI registry distribution without conflating their storage/indexing models.
- Package a chart, create a local HTTP repository, publish its index, and consume the chart through Helm.
- Push and pull a chart through the existing M01 OCI registry after verifying its configuration.
- Explain chart `version`, `appVersion`, SemVer pre-release/build metadata, tags, and digests.
- Distinguish Helm `.prov`/GPG verification from Cosign signing of an OCI artifact.
- Establish a trust root independently and explain why a successful cryptographic check is not a complete authorization decision.
- Verify before install, inspect rendered manifests, examine image references, and fail closed when required checks fail.
- Design a release pipeline that captures immutable evidence and does not silently overwrite a published version.
- Respond to compromised versions, leaked keys, stale mirrors, and changed transitive dependencies.

Success is evidence-based. Fill in the evidence tables with observations from your environment. Do not mark a lab complete just because the commands look plausible.

## 5. L1 — Chart distribution fundamentals

### 5.1 Chart source, package, and release

A **chart source/repository** is the place from which a consumer discovers and retrieves chart packages. A **chart archive/package** is the packaged chart content. A **chart version** identifies a release of the chart, not necessarily the version of the application inside it. A **release** in Helm's deployment model is an installation/upgrade instance of a chart into a Kubernetes cluster; it is not the same thing as the published chart package.

Helm supports two broad distribution patterns:

1. **Classic HTTP chart repository:** a web-accessible `index.yaml` describes chart versions and links to downloadable packaged chart archives, commonly `.tgz`.
2. **OCI registry distribution:** a chart is stored as an OCI artifact in a registry repository and retrieved using registry APIs, tags, and digests.

A local directory is not automatically a usable HTTP repository; it needs a generated index and a server. Likewise, a registry path is not an HTTP chart URL. The clients and metadata models differ.

### 5.2 Classic HTTP chart repositories

A classic repository commonly contains:

```text
http-chart-repo/
├── index.yaml
└── fastapi-service-0.1.0.tgz
```

The `.tgz` is a gzip-compressed tar archive. It includes chart metadata, templates, default values, and other chart files. The index records available chart versions and package locations. An index entry is metadata for discovery; it is not itself the chart package and is not automatically a cryptographic trust statement.

The normal command sequence is:

```bash
# From the directory containing the unpacked chart.
helm lint ./fastapi-service
helm package ./fastapi-service --destination ./dist

# From a directory that will contain the repository's index and packages.
mkdir -p ./http-chart-repo
cp ./dist/fastapi-service-0.1.0.tgz ./http-chart-repo/
helm repo index ./http-chart-repo

# Start the server from the repository directory in a dedicated terminal.
cd ./http-chart-repo
python3 -m http.server 8879 --bind 127.0.0.1
```

The port `8879` and directory names are illustrative choices. The server is intentionally bound to loopback for a local exercise. It is not an authenticated production repository service. Leave that terminal running while testing, and stop it with `Ctrl+C`.

In a second terminal:

```bash
helm repo add local-lab http://127.0.0.1:8879
helm repo update
helm search repo local-lab
helm pull local-lab/fastapi-service --version 0.1.0
```

These commands illustrate the classic workflow. Confirm installed Helm syntax with `helm help repo`, `helm help search repo`, and `helm help pull` if options differ. `helm repo add` stores a local client-side repository alias; `helm repo update` refreshes cached index metadata; `helm search repo` searches that cached metadata; `helm pull` downloads the selected archive.

The `--url` option to `helm repo index` is useful when the published package URLs should point at a canonical base URL rather than the paths inferred from the current directory. For example, `helm repo index ./http-chart-repo --url https://charts.example.invalid/releases` is an illustrative URL only. Verify how relative URLs are formed by inspecting the resulting `index.yaml`; do not assume the server directory layout and index URLs match automatically.

**Stale index behavior:** if a package is copied into the repository directory but the index is not regenerated, clients may not discover that version. Regenerate `index.yaml`, publish the index and package atomically where possible, then run `helm repo update`. In production, publish a new chart version instead of replacing an archive under an existing version.

### 5.3 OCI registry distribution

An OCI registry stores artifacts using registry repository names, tags, manifests, and content-addressed blobs. Helm's OCI support maps chart distribution onto this model. An OCI registry does not use the classic Helm `index.yaml` discovery model in the same way; registry discovery and user-facing catalog capabilities vary by implementation.

Typical conceptual flow:

```bash
helm registry login <LOCAL_REGISTRY>
helm push fastapi-service-0.1.0.tgz oci://<LOCAL_REGISTRY>/helm-charts
helm pull oci://<LOCAL_REGISTRY>/helm-charts/fastapi-service --version 0.1.0
helm show chart oci://<LOCAL_REGISTRY>/helm-charts/fastapi-service --version 0.1.0
```

**[VERSION-SENSITIVE]** These are representative modern Helm OCI command forms. Before running them, check `helm version`, `helm help registry login`, `helm help push`, `helm help pull`, `helm help show`, and the official Helm OCI documentation. Confirm the registry path conventions and authentication configuration in M01 Unit 6.

Helm OCI push generally takes a packaged chart archive and an OCI destination that names the registry/repository destination; it does not take the same kind of direct `.tgz` URL as a classic HTTP repository. Helm derives the chart name/version metadata from the package and maps the chart version to the OCI tag. The exact validation and accepted path form must be checked against the installed Helm release.

An OCI **tag** is a human-readable reference that may be mutable depending on registry policy. A **digest** identifies content by cryptographic hash at a particular OCI object layer. A chart's tag and a recorded digest answer different questions: the tag helps a human select a release; the digest identifies specific bytes/manifests. Do not assume a tag is immutable unless the registry and release policy enforce it.

**[VERIFY]** Digest pull/install reference syntax is not universal across all Helm versions and registry combinations. Consult the installed Helm help and official documentation. If direct digest pinning is not supported for the operation you need, pull by the approved version, compare the retrieved artifact's digest with independently recorded release evidence, verify its signature/provenance, and install only the verified local package. Document that this is a verification workflow rather than a claim of universal digest-reference support.

### 5.4 Chart package layout and SemVer

A minimal chart looks like this:

```text
fastapi-service/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   └── service.yaml
└── README.md
```

`Chart.yaml` includes `apiVersion`, `name`, `version`, and optionally `appVersion`. `version` is the chart package's release version and must be a valid chart version. `appVersion` is descriptive application-version metadata; it does not automatically update `version`, build the image, or pin an image digest.

Example:

```yaml
apiVersion: v2
name: fastapi-service
description: Illustrative FastAPI service chart for a local distribution lab
type: application
version: 0.1.0
appVersion: "1.4.2"
```

SemVer typically uses `MAJOR.MINOR.PATCH`, with optional pre-release identifiers such as `1.2.0-rc.1` and optional build metadata such as `1.2.0+build.17`. Pre-release versions have SemVer precedence rules; build metadata does not affect SemVer precedence. Helm's OCI tag handling has special behavior for `+` build metadata, commonly representing `+` as `_` because OCI tags do not permit `+` in the same way. **[VERIFY]** Confirm the exact mapping with the installed Helm release and official documentation before scripting it.

Changing chart `version`, changing `appVersion`, changing a container image tag, and changing an OCI digest are distinct events. A chart-only template change should result in a new chart version even if the application image remains the same. A new application image should be reflected in reviewed values/templates and release metadata. Prefer immutable image digests where organizational policy requires them; `appVersion` alone is not a pin.

### 5.5 Immutability as a release principle

Never intentionally overwrite a published chart version. If a package is wrong or vulnerable, publish a corrected new version and deprecate or block the old one through supported controls. Even if a backend rejects duplicate tags, enforce immutability in the release process and record digests.

A version label is not proof that the underlying content stayed unchanged. Registries may permit tag replacement, retention policies may remove content, and mirrors may be stale. Record the chart version, package checksum, OCI digest when available, source revision, signer identity/key fingerprint, and verification result. An overwrite attempt in a disposable lab should compare before/after digests and stop if the result is ambiguous.

### 5.6 Artifact Hub: discovery versus trust

Artifact Hub is a catalog/discovery platform for cloud-native packages and related artifacts. It can help locate charts and view publisher-provided metadata, but a listing or search result is not a security review, proof of publisher authorization, signature guarantee, or substitute for reviewing the source and verifying the exact package. Treat discovery as the beginning of due diligence, not the final trust decision.

**Remember:** discover from an approved source, fetch the exact package, independently verify its identity/integrity, inspect the chart and rendered resources, and apply local policy before installation.

## 6. HTTP repository, step by step

The essential HTTP repository artifacts are:

- `Chart.yaml`: metadata inside the chart.
- `.tgz`: packaged chart archive.
- `index.yaml`: repository-level version catalogue with package locations.
- HTTP server: makes the index and archive retrievable.
- Helm client repository alias/cache: allows search and pull.

`helm repo index` builds or updates index metadata from packages in a directory. The index is not a substitute for package integrity checks. Publish the index only after the referenced packages are available, and avoid exposing partial releases to consumers.

A checksum is useful evidence for byte-for-byte comparison:

```bash
sha256sum fastapi-service-0.1.0.tgz
tar -tzf fastapi-service-0.1.0.tgz | head -n 30
```

The checksum identifies the local archive bytes. It is not a publisher signature, and it does not prove the chart is safe. Keep the checksum in release evidence from a trusted build process; comparing two values copied from the same compromised channel does not create independent trust.

## 7. OCI registries, step by step

### 7.1 Login and transport security

Inspect M01 Unit 6 before logging in. Confirm the registry's hostname, port, TLS certificate chain, authentication configuration, and client reachability. If a private CA is used, configure trust through the documented client/OS mechanism. Do not “fix” a TLS failure by disabling verification.

Where supported, use standard input for the password so it is not embedded directly in the command line:

```bash
# [VERSION-SENSITIVE] Confirm stdin/password options with `helm help registry login`.
printf '%s' "$REGISTRY_PASSWORD" |
  helm registry login <LOCAL_REGISTRY> \
    --username "$REGISTRY_USERNAME" \
    --password-stdin
```

This example assumes the two environment variables were injected securely by the learner's shell/secret manager and are not printed or persisted. Do not export literal secrets in a shared shell profile. Environment variables can still be exposed to processes or diagnostics on some systems; use the organization's approved secret-injection method.

**Prominent lab-only warning:** if, and only if, the existing disposable M01 registry is verified to be HTTP-only, use the exact plaintext/local transport option supported by your installed Helm version. Some Helm releases document a `--plain-http` option for relevant OCI commands, but its availability and scope must be checked with `helm help registry login`, `helm help push`, and `helm help pull`. Bind the registry to loopback or an isolated lab network where feasible. Never send production credentials or untrusted-network traffic over plaintext HTTP.

Helm's registry credentials are stored according to its configuration and credential-helper behavior. **[VERIFY]** Inspect `helm env`, the configured Helm registry config path, and official Helm documentation. Do not print credential files into terminal logs or upload them as evidence. Credential helpers and paths differ by platform; WSL2 may interact with Linux-side configuration independently of native Windows tools.

Use separate read-only pull credentials and push credentials. A learner who only consumes charts should not have permission to publish, delete, or overwrite artifacts. CI should mask secrets and avoid shell tracing around credential commands. Connect these practices to M02 CI/CD and M09 secrets/identity; this chapter does not replace those modules.

### 7.2 Push and pull

After packaging the chart and confirming its metadata:

```bash
# Run from the directory containing the package.
helm push fastapi-service-0.1.0.tgz \
  oci://<LOCAL_REGISTRY>/helm-charts
```

The destination path and repository layout are implementation/configuration dependent; follow the Helm OCI rules and local registry configuration. Do not append a guessed filename or version segment merely because HTTP URLs include filenames. Confirm the command's output and the registry's repository/tag view.

Pull by chart name and version:

```bash
helm pull oci://<LOCAL_REGISTRY>/helm-charts/fastapi-service \
  --version 0.1.0
```

Inspect the downloaded archive and compare its checksum with the publisher's release evidence:

```bash
sha256sum fastapi-service-0.1.0.tgz
tar -tzf fastapi-service-0.1.0.tgz | head -n 40
helm show chart fastapi-service-0.1.0.tgz
helm show values fastapi-service-0.1.0.tgz
helm show readme fastapi-service-0.1.0.tgz
```

`helm show readme` and accepted reference forms can vary. **[VERSION-SENSITIVE]** Check `helm help show` and the installed Helm documentation. If `helm show` requires an OCI reference rather than a local archive for a particular subcommand, use the documented form and record it. To extract the chart for inspection:

```bash
mkdir -p ./inspect-oci-pull
helm pull oci://<LOCAL_REGISTRY>/helm-charts/fastapi-service \
  --version 0.1.0 --untar --untardir ./inspect-oci-pull
find ./inspect-oci-pull -maxdepth 3 -type f -print
```

Again, check `helm help pull` for the installed version. Never edit the original release package during inspection.

### 7.3 Chart dependencies from OCI

A chart can declare dependencies in `Chart.yaml`, with name, version constraint, and repository. An OCI dependency repository commonly uses an `oci://` reference that names the registry/repository base; chart name and version resolution follow Helm's OCI dependency rules. Do not assume dependency syntax and behavior are identical between HTTP and OCI sources or across Helm versions.

Illustrative dependency declaration:

```yaml
apiVersion: v2
name: platform-bundle
version: 0.1.0
dependencies:
  - name: fastapi-service
    version: "0.1.0"
    repository: "oci://<LOCAL_REGISTRY>/helm-charts"
```

**[VERIFY]** Check the official Helm dependency/OCI docs and `helm dependency` help for the installed version. Then run the supported workflow from the dependent chart directory, commonly:

```bash
helm dependency update
helm dependency list
helm lint .
```

`helm dependency update` may resolve versions allowed by constraints and update the lock file. Review `Chart.lock`, package the resolved dependencies, and commit the lock file where the team's workflow requires it. For a release pipeline, record resolved dependency versions and package digests. Avoid loose ranges when repeatable production releases are required.

### 7.4 Digest discovery and pinning

A registry may expose digest information through its API, UI, or implementation-specific CLI. Do not invent a universal command. Use the local registry's documented interface or the M01 tooling to identify the manifest digest and record the exact object layer the digest describes.

- A **package SHA-256** hashes the `.tgz` bytes.
- An **OCI manifest digest** hashes an OCI manifest document.
- An OCI chart may have more than one relevant digest across layers; do not compare values from different layers as if they were equivalent.

Where the installed Helm/registry pair supports a digest reference for pull or install, test it against a known artifact and record the exact syntax. Otherwise, use the supported pull-by-version workflow, verify the package against a trusted release record/signature, and install that exact verified local archive. The limitation must be documented rather than hidden.

## 8. HTTP repository versus OCI comparison matrix

| Dimension | Classic HTTP chart repository | OCI registry |
|---|---|---|
| Discovery | `index.yaml`, repository aliases, search over cached index | Registry repository/tag APIs and optional catalog/UI; capability varies |
| Storage | Downloadable `.tgz` archives plus index | OCI manifests and blobs in registry repositories |
| Access control | Often web-server/object-store access controls; implementation varies | Registry authentication and repository-scoped permissions; implementation varies |
| Integrity identifiers | Package checksum and optional Helm provenance | OCI manifest/layer digests and signatures/referrers or other storage mechanisms |
| Signing | Helm `.prov` can accompany a chart archive; transport/storage policy matters | Cosign or other OCI-compatible signing can associate signature evidence; registry support matters |
| Replication | Copy packages and index, preserve URL correctness and index freshness | Registry replication/copy operations; ensure digest and signature evidence remain valid |
| Deletion/retention | Remove package/index entries according to repository implementation | Registry deletion, tag mutability, retention, and garbage collection are implementation-specific |
| Client behavior | `helm repo add/update/search/pull` | `helm registry login`, OCI `push/pull/show/install` forms |
| Operational ownership | Host index and package files consistently | Operate registry authentication, storage, replication, retention, and artifact metadata |
| Common failure | Stale index or invalid package URL | TLS/auth/path/tag/digest/referrer mismatch |

Neither model is inherently trustworthy by itself. Select based on ecosystem fit, access controls, retention, replication, verification support, and operational capability.

## 9. L2 — Hands-on local HTTP repository and FastAPI chart package

### Lab A: Package and consume from a local HTTP repository

**Purpose:** learn packaging, index generation, publication, and consumption without a cluster.

**Needs:** Helm, Python 3, local disk; no registry, cluster, GPG, or Cosign required. Network access is not required for the loopback HTTP portion. Resource impact is small. The commands use an illustrative workspace `~/chart-distribution-lab`; adapt it to your machine.

#### A1. Create a minimal chart if a prior M06 chart is not available

```bash
mkdir -p ~/chart-distribution-lab/fastapi-service/templates
cd ~/chart-distribution-lab
```

Create `fastapi-service/Chart.yaml`:

```yaml
apiVersion: v2
name: fastapi-service
description: Minimal FastAPI service chart for a chart-distribution lab
type: application
version: 0.1.0
appVersion: "1.4.2"
```

Create `fastapi-service/values.yaml`:

```yaml
replicaCount: 1

image:
  repository: python
  tag: "3.12-slim"
  pullPolicy: IfNotPresent

containerPort: 8000

service:
  type: ClusterIP
  port: 80

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

Create `fastapi-service/templates/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
  labels:
    app.kubernetes.io/name: {{ .Chart.Name }}
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ .Chart.Name }}
        app.kubernetes.io/instance: {{ .Release.Name }}
    spec:
      containers:
        - name: api
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.containerPort }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

Create `fastapi-service/templates/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}
spec:
  type: {{ .Values.service.type }}
  selector:
    app.kubernetes.io/instance: {{ .Release.Name }}
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: http
```

This is a distribution example, not a production FastAPI application chart: the example image does not include a FastAPI application or an application health endpoint. Do not use this chart as evidence that the workload itself is deployable. If using a prior M06 FastAPI chart, substitute that chart and keep its real image reference. For the package/repository lab, no cluster is required.

#### A2. Lint, render, and package

```bash
cd ~/chart-distribution-lab
helm lint ./fastapi-service
helm template lab ./fastapi-service > ./rendered.yaml
mkdir -p ./dist
helm package ./fastapi-service --destination ./dist
sha256sum ./dist/fastapi-service-0.1.0.tgz \
  > ./dist/fastapi-service-0.1.0.tgz.sha256
tar -tzf ./dist/fastapi-service-0.1.0.tgz
helm show chart ./dist/fastapi-service-0.1.0.tgz
```

Expected evidence to observe, not assumed output: a lint result, a rendered YAML file, the `.tgz` archive, a checksum file, archive member names, and chart metadata showing the chart version. If a command fails, capture the error and investigate rather than continuing to publish a broken package.

#### A3. Build the local HTTP repository

```bash
cd ~/chart-distribution-lab
mkdir -p ./http-chart-repo
cp ./dist/fastapi-service-0.1.0.tgz ./http-chart-repo/
helm repo index ./http-chart-repo
```

Inspect the generated index:

```bash
sed -n '1,160p' ./http-chart-repo/index.yaml
```

Confirm that the index entry names `fastapi-service`, identifies version `0.1.0`, and references a package URL that the local server can actually serve. The exact fields and generated timestamps are Helm-generated; do not hand-edit them to fake a successful release.

Start a server in terminal A:

```bash
cd ~/chart-distribution-lab/http-chart-repo
python3 -m http.server 8879 --bind 127.0.0.1
```

In terminal B:

```bash
helm repo add local-lab http://127.0.0.1:8879
helm repo update
helm search repo local-lab
helm pull local-lab/fastapi-service --version 0.1.0
sha256sum fastapi-service-0.1.0.tgz
helm show chart fastapi-service-0.1.0.tgz
```

Compare the downloaded archive checksum with the packaged archive checksum. If they differ, stop and investigate the source, path, and package content. A checksum match supports byte identity between these two files, not publisher trust or chart safety.

#### A4. Demonstrate a stale index safely

Copy a **new version** of the chart into the repository directory only after changing `Chart.yaml` to a new SemVer version (for example, `0.1.1` in this disposable exercise), then package that version. Before regenerating the index, run `helm repo update` and `helm search repo local-lab`; observe whether the new version appears. Then run:

```bash
helm repo index ~/chart-distribution-lab/http-chart-repo
helm repo update
helm search repo local-lab
```

Do not expect a package to be discoverable solely because the `.tgz` exists on disk. The index is the catalogue for this repository model.

#### A5. Evidence and cleanup

Record:

| Evidence | Actual observation |
|---|---|
| Chart directory and `Chart.yaml` version | [RECORD YOUR RESULT] |
| `helm lint` result | [RECORD YOUR RESULT] |
| Package filename | [RECORD YOUR RESULT] |
| Package SHA-256 | [RECORD YOUR RESULT] |
| `index.yaml` package URL | [RECORD YOUR RESULT] |
| Local repository search result | [RECORD YOUR RESULT] |
| Pulled archive checksum | [RECORD YOUR RESULT] |
| Stale-index behavior and resolution | [RECORD YOUR RESULT] |

Stop the server with `Ctrl+C`. Remove only the disposable local repo alias if desired:

```bash
helm repo remove local-lab
```

Delete the lab directory only after saving the evidence you need. This lab does not use or delete the M01 registry.

## 10. L2 — Push/pull through the M01 local OCI registry

### Lab B: Use the existing local registry

**Purpose:** publish and consume the same chart through the OCI workflow and compare artifact evidence.

**Needs:** Helm, the running M01 registry, local disk, and registry authentication/TLS configuration. No cluster is required for package push/pull. Network access is limited to the local registry. GPG and Cosign are not required for this lab. Registry storage and resource impact are determined by the existing M01 service.

#### B1. Verify the registry configuration first

Open M01 Unit 6 and inspect the actual `registry:2` configuration. Verify:

- actual hostname and port reachable from WSL2;
- whether TLS is enabled and which CA certificate is trusted;
- whether basic authentication is enabled and which accounts are configured;
- which repository namespace/path is intended for this lab;
- whether tag overwrite, deletion, referrers, and digest inspection are supported;
- whether the service is shared by other labs or users.

Do not proceed if you cannot establish the registry endpoint and authentication model. Do not invent an address or credentials.

#### B2. Authenticate and push

Confirm the package exists and inspect it:

```bash
cd ~/chart-distribution-lab
test -f ./dist/fastapi-service-0.1.0.tgz
helm show chart ./dist/fastapi-service-0.1.0.tgz
sha256sum ./dist/fastapi-service-0.1.0.tgz
```

Login using the secure, supported method for your installed Helm version:

```bash
# [VERSION-SENSITIVE] Verify `--password-stdin` with `helm help registry login`.
printf '%s' "$REGISTRY_PASSWORD" |
  helm registry login <LOCAL_REGISTRY> \
    --username "$REGISTRY_USERNAME" \
    --password-stdin
```

Push the package:

```bash
helm push ./dist/fastapi-service-0.1.0.tgz \
  oci://<LOCAL_REGISTRY>/helm-charts
```

The path `helm-charts` is an illustrative repository namespace, not a claim about your existing registry. Replace it with the namespace agreed in M01. If the registry is HTTP-only, stop and verify the exact local-only transport option in the installed Helm help before using it. **Plaintext mode is lab-only and must not carry production credentials or untrusted-network traffic.**

#### B3. Pull, inspect, and compare

```bash
mkdir -p ./oci-pull
helm pull oci://<LOCAL_REGISTRY>/helm-charts/fastapi-service \
  --version 0.1.0 --destination ./oci-pull
sha256sum ./oci-pull/fastapi-service-0.1.0.tgz
helm show chart ./oci-pull/fastapi-service-0.1.0.tgz
helm show values ./oci-pull/fastapi-service-0.1.0.tgz
```

Use `helm show readme` and `--untar` only after checking their installed syntax. Compare the pulled package checksum with the original package checksum. For registry manifest digests, use the implementation's documented inspection method and record which manifest/layer the digest identifies.

#### B4. OCI tag/version correspondence

The chart `version` determines the expected OCI tag under Helm's OCI convention. `appVersion` does not become the chart tag. Pre-release versions may be valid tags according to the installed tool/registry behavior. Build metadata containing `+` is commonly normalized to `_` in OCI tags; **[VERIFY]** the exact mapping in the installed Helm version and test it with a disposable chart version before automating release naming.

#### B5. Credentials, roles, and logout

Use a pull-only account for consumers and a push account only in the publishing stage. Grant deletion or administrative access only to designated registry operators. Mask secret values in CI logs and do not enable shell tracing around login commands. Check configured Helm credential storage with `helm env` and official documentation; do not publish credential files as evidence.

Log out when supported:

```bash
# [VERSION-SENSITIVE] Verify exact syntax with `helm help registry logout`.
helm registry logout <LOCAL_REGISTRY>
```

#### B6. OCI dependency check

For a dependent chart, declare an OCI dependency in `Chart.yaml` as shown in Section 7.3, then use the supported `helm dependency update` and `helm dependency list` commands. Confirm the resolved chart version and lockfile. Do not rely on a loose dependency constraint if you need reproducible production builds.

#### B7. Lab evidence and cleanup

| Evidence | Actual observation |
|---|---|
| Registry host/port and TLS mode from M01 | [RECORD YOUR RESULT] |
| Registry implementation/version | [RECORD YOUR RESULT] |
| Account permission scope | [RECORD YOUR RESULT] |
| Chart package checksum before push | [RECORD YOUR RESULT] |
| OCI reference and tag | [RECORD YOUR RESULT] |
| Pulled archive checksum | [RECORD YOUR RESULT] |
| Manifest/layer digest and method used | [RECORD YOUR RESULT] |
| Digest pull/install support verified? | [RECORD YOUR RESULT] |
| `+` to `_` behavior tested? | [RECORD YOUR RESULT] |

Remove only the temporary local pull directory and log out. Do not delete the shared registry repository or tag as routine cleanup. If an overwrite test is needed later, use a dedicated disposable namespace approved for the lab and preserve before/after evidence.

## 11. Chart inspection, dependency handling, digest pinning, and credentials

A chart archive should be inspected before it is trusted. `helm show chart`, `helm show values`, and `helm show readme` expose metadata, default configuration, and documentation where supported. `helm pull --untar` extracts a copy for template review. `helm template` renders manifests without needing a Kubernetes API server; it is a review step, not proof that the resources will be accepted by the target cluster.

For a third-party chart:

```bash
# Use an approved source and an explicit version.
helm pull <APPROVED_REPOSITORY>/<CHART_NAME> \
  --version <CHART_VERSION> --untar --untardir ./third-party-review

helm template review ./third-party-review/<CHART_NAME> \
  --namespace review \
  > ./third-party-review/rendered.yaml
```

These are classic repository reference examples; adapt the reference form for OCI and verify the installed Helm syntax. Review templates and helpers, hooks, RBAC, service accounts, host paths, host networking, privileged settings, security contexts, network exposure, persistent storage, CRDs, and any resource with broad permissions. Extract image references from rendered manifests and check whether images use approved repositories and immutable digests when required.

For dependency review, inspect `Chart.yaml`, `Chart.lock`, and `charts/`. Record each dependency name/version/source and any available package digest/signature evidence. A parent chart signature does not automatically establish that every transitive dependency is safe or authorized.

Never blindly automate `helm repo add` for unknown URLs or install a chart directly from a search result. A chart catalogue is discovery, not trust.

## 12. L3 — Helm provenance and GPG verification

### 12.1 What Helm provenance means

Classic Helm provenance uses a `.prov` file associated with a packaged chart. The provenance workflow records chart package information and a cryptographic signature so a consumer can check whether the package matches the signed metadata and whether the signature verifies against a key available to the verifier. This is distinct from an SBOM or vulnerability scan.

A `.prov` file does not enumerate all runtime risks, prove that images are safe, authorize the publisher for your environment, or show that the chart complies with your policy. Verification must be performed against the exact archive before installation.

### 12.2 Key roles and trust bootstrap

- The **private signing key** is held by the authorized publisher and must be protected.
- The **public verification key** is distributed to consumers through an authenticated, independent channel.
- The **fingerprint** identifies a key; consumers should compare it against a fingerprint communicated through a separate trusted channel.
- The **keyring** is the local store used by the relevant GPG/Helm workflow.
- Expiration and revocation must be handled as lifecycle events, not ignored because a previous verification succeeded.

A public key fetched from the same untrusted location as a chart is not sufficient trust bootstrap. An attacker who can replace both the chart and the verification key may be able to make a false package appear internally consistent. Obtain the expected fingerprint independently, validate it, and record which key is authorized for which chart/source.

### 12.3 Lab C — Helm provenance with a throwaway GPG key

**Needs:** Helm, GPG, local disk; no cluster or registry is required. Network access is not required if the tools are installed. Use a disposable key and package only. Resource impact is small. Keep the original archive intact for the Cosign and end-to-end labs.

**[VERSION-SENSITIVE]** Helm's provenance flags and keyring format can differ by Helm release and GPG setup. Before starting, inspect:

```bash
helm help package
helm help verify
helm help pull
gpg --version
```

Consult official Helm chart provenance documentation. Do not guess the keyring path or silently substitute an unsupported option.

Create a dedicated lab GPG home:

```bash
export GNUPGHOME="$HOME/chart-distribution-lab/gnupg-lab"
mkdir -p "$GNUPGHOME"
chmod 700 "$GNUPGHOME"
```

Generate a throwaway key using the interactive GPG workflow documented by your installed GPG version. Choose a clearly lab-only identity; do not use an organizational email identity. Avoid putting a passphrase in a command line. Record the resulting public-key fingerprint:

```bash
gpg --list-secret-keys --fingerprint
gpg --list-keys --fingerprint
```

Validate the fingerprint through a separate trusted channel before treating the key as trusted for any purpose beyond the exercise. In this isolated lab, the key is intentionally not trusted outside the lab.

Export the public key to a lab evidence path only:

```bash
mkdir -p "$HOME/chart-distribution-lab/gpg-evidence"
gpg --armor --export <LAB_KEY_FINGERPRINT> \
  > "$HOME/chart-distribution-lab/gpg-evidence/lab-public-key.asc"
```

The fingerprint placeholder must be replaced by the exact fingerprint shown by GPG. Never export or commit the private key as part of the evidence bundle.

**[VERIFY]** Helm's classic signing flow has used `helm package --sign` with key/keyring-related options, but the exact accepted flags and keyring format must be confirmed with the installed Helm help and official documentation. After configuring the documented keyring for that release, package a new chart version or use a dedicated copy:

```bash
# Illustrative shape only; add only flags documented by installed Helm.
helm package ./fastapi-service \
  --destination ./signed-dist \
  --sign
```

If the installed command requires a signing key identifier or keyring option, add the exact documented flags; do not assume this abbreviated command will work unchanged. Verify that the `.tgz` and corresponding `.prov` exist:

```bash
find ./signed-dist -maxdepth 1 -type f -print
```

Verify the package using the documented keyring configuration:

```bash
# [VERSION-SENSITIVE] Use the keyring/public-key arrangement documented for this Helm release.
helm verify ./signed-dist/fastapi-service-<CHART_VERSION>.tgz
```

Where the installed Helm supports `--verify` for `helm pull` or install, check the exact syntax and keyring semantics first. Do not claim that `helm install` enforces Cosign policy; it does not automatically become a Cosign policy engine merely because an OCI artifact has a signature.

### 12.4 Tamper test

Preserve the original package and `.prov`. Make a copy and modify only the copy:

```bash
mkdir -p ./tamper-test
cp ./signed-dist/fastapi-service-<CHART_VERSION>.tgz ./tamper-test/
cp ./signed-dist/fastapi-service-<CHART_VERSION>.tgz.prov ./tamper-test/
```

Use an archive-aware tool to extract the copy, make a harmless file-content change, and repackage it as a separate test artifact. Do not overwrite the original signed archive and do not reuse the original version for a replacement release. Run `helm verify` against the altered copy and record the actual result. A valid verification should fail if the package bytes no longer match the signed provenance; if it does not, stop and investigate what file was verified and how the command resolved the package/provenance pair.

Do not fabricate a failure message. Record the command, tool version, file checksum, and observed outcome.

### 12.5 Three different conclusions

1. **Signature mathematically verifies:** the cryptographic relationship between the signature and the artifact/key is valid under the mechanism's rules.
2. **Key is trusted:** the verifier has independently established that this public key is an approved trust root for the relevant purpose.
3. **Publisher is authorized:** policy permits that key/person/workload identity to publish this chart in this repository and environment.

These are not interchangeable. Key rotation, expiration, and revocation require the consumer's trust store and policy to be updated through a controlled process.

## 13. L3 — Cosign key-based signing and verification for OCI chart artifacts

### 13.1 Model and prerequisites

Cosign can sign container images and other supported OCI artifacts. For an OCI chart, the critical subject is the exact artifact digest, and the signature must be stored and discoverable through a mechanism supported by the registry and Cosign version. Registry support for OCI referrers or tag-based signature storage varies; a successful chart push does not prove that signature storage will work.

**Needs:** Cosign, Helm, a reachable local OCI registry, and local disk. No Kubernetes cluster is required for signing and verification. A local registry and authentication are required for a registry-backed exercise. Network access may be required to fetch tool documentation but public infrastructure is not a requirement for the lab. Use only throwaway keys.

Inspect installed syntax first:

```bash
cosign version
cosign help
cosign help generate-key-pair
cosign help sign
cosign help verify
```

**[VERSION-SENSITIVE]** Cosign flags and signature-storage behavior evolve. Use the installed command help and official Sigstore documentation; do not paste an internet example without checking it against your version and registry.

### 13.2 Generate a throwaway key pair

From the lab workspace, use the documented `cosign generate-key-pair` workflow for the installed version. It commonly creates a private key and corresponding public key, but file names, prompts, password handling, and flags should be verified locally. Keep the private key outside source control with restrictive filesystem permissions. Do not place the private key in the evidence bundle.

Record a checksum/fingerprint of the public key and the tool version. A public key checksum is useful for comparing files, but production trust should also validate the key through an independent authenticated channel.

### 13.3 Identify and sign the exact OCI artifact

First identify the OCI chart reference and immutable digest using the registry's supported interface. Record both. Then use the installed Cosign's documented key-based signing syntax to sign the chart artifact by digest. The exact command is deliberately not hard-coded here because the accepted subject reference, flags, registry auth configuration, and signature storage may vary across Cosign and registry versions.

Before signing, verify that:

- the subject reference resolves to the expected chart;
- the digest is the intended immutable artifact digest;
- the signing identity/key is the throwaway lab key;
- registry credentials have only the permissions needed for the exercise;
- the signature storage path is supported by the registry/Cosign pair.

After signing, verify the signature against the **same digest** using the public key and the documented verification command. Record the exact command form from your installed help and the observed output. Do not write “verified” unless the command completed successfully and the subject digest matches the release record.

### 13.4 Tamper and fallback

Do not overwrite the original chart version to test tampering. Create a distinct test artifact with changed content and a distinct name/version, or test a local OCI layout if the installed tooling documents that workflow. Attempt verification of the changed artifact against the original signature and record the actual outcome.

If registry-backed signing fails because the registry does not support the needed referrer/tag storage or the installed Cosign version cannot discover the signature, diagnose the limitation. Preserve the original artifact and use an explicitly documented local OCI-layout fallback only if supported by the installed tool. The fallback proves the supported local workflow, not that the registry-backed deployment path works. Mark registry compatibility as unresolved until verified.

### 13.5 Key-based trust bootstrap and keyless awareness

For production, the consumer must obtain the trusted public key through a separate authenticated channel, validate its fingerprint/checksum, and know which publisher or release role it represents. If an attacker can replace the artifact and substitute a different public key that the consumer accepts without independent validation, the trust model has failed.

Keyless/OIDC signing uses a workload or user identity established through an identity provider, often with short-lived signing credentials and a transparency-log model. The verifier checks identity-related claims against a trust policy. This chapter requires awareness only: no live keyless lab is required because it depends on public infrastructure, OIDC identity configuration, and external trust setup. A valid identity claim still needs policy to decide whether that identity is authorized to sign this chart.

### 13.6 What signing does and does not prove

Signing can provide evidence of artifact integrity and that a signature was produced by a particular key or identity under stated trust assumptions. It does **not**, by itself, prove:

- the chart is safe or well-designed;
- referenced container images are safe;
- the publisher is reputable or authorized;
- templates do not create dangerous permissions or resources;
- dependencies are free of vulnerabilities;
- the artifact complies with organizational policy;
- the artifact was deployed as intended.

Review rendered manifests, publisher identity, dependencies, image provenance and vulnerabilities, and local policy. A signature is one gate in a defense-in-depth workflow.

## 14. L3 — Consumer trust policy, SBOMs, image references, and third-party review

### 14.1 Verify before installation

A consumer-side gate should follow this order:

1. Select an approved source.
2. Fetch the exact chart version and, where supported, digest.
3. Verify expected key/identity and signature/provenance.
4. Compare package checksum/digest against trusted release evidence.
5. Inspect chart metadata, templates, dependencies, hooks, and default values.
6. Render with the intended environment values.
7. Review Kubernetes resources, permissions, and image references.
8. Scan/validate dependencies and images; apply schema and policy checks.
9. Install only if required gates pass.

Do not assume `helm install` alone automatically enforces Cosign signatures. Helm provenance verification options, where supported, are not the same thing as a general Cosign trust policy.

Illustrative consumer pipeline pseudocode:

```bash
set -eu

# Fetch from an approved source using the pinned version.
helm pull oci://<APPROVED_REGISTRY>/<REPOSITORY>/<CHART_NAME> \
  --version <CHART_VERSION> --destination ./verified-input

# Verify the exact artifact with the documented mechanism:
# - helm verify for a chart with trusted .prov metadata, and/or
# - cosign verify against the recorded OCI digest and trusted public key.
# Exact syntax is version-sensitive; do not skip this gate if required.

# Compare package checksum/digest with independent release evidence.
# Render, inspect manifests and images, run policy/scan gates.
helm template reviewed ./verified-input/<CHART_NAME>-<CHART_VERSION>.tgz \
  --namespace <NAMESPACE> > ./evidence/rendered.yaml

# Install only after all mandatory gates have succeeded.
```

The verification commands must be real commands documented for the installed tool versions, not comments left in a production pipeline. The example shows the policy sequence, not a ready-to-run universal Cosign invocation.

CI should fail closed: if a required verification command fails, stop the pipeline and preserve logs/evidence. Exceptions must be explicit, time-limited, approved, and auditable. Never convert a signature failure into a warning without an authorized exception.

### 14.2 Chart SBOM versus image SBOM

An SBOM describes components known to be present in a software artifact. A chart-package SBOM and an image SBOM are different:

- A chart-package SBOM can describe files and dependencies inside the chart archive to the extent the SBOM tool understands the format and data available.
- An image SBOM describes packages/components in a referenced container image.
- A chart may reference multiple images and external dependencies that are not included in the chart archive.

Syft is an M01 forward/reference point for generating SBOMs. Do not assume it automatically recognizes every Helm chart format or generates a complete chart SBOM. Check Syft's installed help and official documentation for the supported source type. Record the input, tool version, and limitations. Image SBOMs should be generated for the exact image digests used by the deployment.

Extract and review image references from rendered manifests. For example, a simple text inspection may help:

```bash
grep -nE '^[[:space:]]*image:' ./evidence/rendered.yaml
```

This is a quick inspection, not a complete YAML parser; image fields may occur in different structures or be templated. Use a YAML-aware parser or policy tooling for robust extraction. Prefer immutable image digests where required by release policy. M12 covers attestations and their broader verification/enforcement lifecycle; this chapter only establishes the connection.

### 14.3 Access control, retention, and mirroring

Separate pull/read from push/write permissions. Rotate credentials, remove unused accounts, monitor unusual pushes/deletes, and retain audit logs. Reference M01 Unit 7 for registry access controls.

Retention and garbage collection behavior depends on the registry implementation. Deleting a tag may not immediately delete content-addressed blobs; garbage collection may later remove unreferenced content. Signature/referrer metadata may be stored or discoverable differently. **[VERIFY]** Consult the documentation for the actual registry and Cosign version before assuming deletion behavior or signature survival.

Mirroring third-party charts into an internal registry can improve availability and centralize review, but it creates an operational responsibility. Preserve source URL, chart version, package/manifest digest, signature/provenance evidence, dependency versions, review outcome, mirror timestamp, and the identity of the person or automation that approved the mirror. Compare source and destination digests after transfer and verify signatures against the intended artifact. A copied tag alone is not evidence that content stayed unchanged.

Trust policy should define approved registries, allowed publishers/keys/identities, required signatures, allowed versions, and the required consumer-side verification steps. Admission enforcement is an M08/M12 forward reference, not a full lab here.

## 15. L4 — Production chart release pipeline

### 15.1 Required release sequence

The release pipeline is:

**lint → test → package → sign → push → verify-pull → attach SBOM → release notes**

The order matters. Lint and tests occur before publication. The package is signed before it is pushed. The published artifact is pulled and verified, so the pipeline tests the consumer path rather than trusting only the local build output. SBOM and release notes are associated with the release evidence. M02 Unit 7/8 provides the wider CI/CD context.

### 15.2 Platform-neutral workflow

The following pseudocode intentionally uses placeholders. It is not a ready-to-run workflow for any specific CI provider.

```yaml
# [ILLUSTRATIVE] Platform-neutral release workflow.
# Configure the actual CI provider, protected environment, and secret injection.
steps:
  - name: Checkout immutable source revision
    run: checkout-protected-commit

  - name: Record tool versions
    run: |
      helm version
      cosign version
      write-versions-to-evidence

  - name: Validate chart
    run: |
      helm lint ./chart
      run-chart-tests
      helm template release ./chart > evidence/rendered.yaml
      run-schema-policy-and-manifest-review

  - name: Enforce unique chart version
    run: |
      read-chart-version-from-Chart.yaml
      check-version-not-already-published
      fail-if-existing-version-has-different-digest

  - name: Package chart
    run: |
      helm package ./chart --destination ./dist
      calculate-package-checksum
      record-source-revision-and-chart-metadata

  - name: Sign
    run: |
      # Use protected signing credentials or approved signing service.
      # Never write a private key into the repository or print it in logs.
      sign-exact-artifact

  - name: Push to local/approved registry
    permissions:
      registry: push-only-to-designated-repository
    run: |
      authenticate-through-secret-injection
      push-chart-package
      record-OCI-digest

  - name: Verify-pull
    permissions:
      registry: pull-only
    run: |
      pull-exact-chart-version
      verify-signature-or-provenance
      compare-package-checksum-and-OCI-digest
      fail-if-any-required-check-fails

  - name: Attach SBOM
    run: |
      generate-chart-and-image-SBOMs-where-supported
      attach-or-publish-SBOM-using-documented-platform-mechanism
      record-SBOM-location-and-tool-version

  - name: Release notes and evidence bundle
    run: |
      write-release-notes
      bundle-chart-version-source-revision-digest-signature-result-SBOM-location
      publish-release-evidence
```

The placeholder names above are explanatory pseudocode, not existing repository commands or secret identifiers. The lab publishes only to the local M01 registry; it does not require or perform publication to a public or paid registry.

A retry must not silently overwrite an existing version. If a version already exists, compare the expected digest and stop if the content differs. Even if the same digest exists, the release system should record that the operation is idempotent and not replace the artifact. Registry-side immutable-tag policy is useful where available, but CI must also enforce unique versions.

Release evidence should capture at minimum:

- source revision and build inputs;
- chart name/version and `appVersion`;
- package filename and checksum;
- OCI reference and manifest digest, where available;
- signer key fingerprint or verified identity;
- signature/provenance verification result;
- dependency versions and image references;
- chart/image SBOM locations and tool versions;
- rendered-manifest validation result;
- release notes and publication timestamp;
- approval and exception records.

This pipeline does not prove the chart is safe, that every image is vulnerability-free, that the signer is authorized under every deployment policy, or that the cluster deployed the intended artifact. Those need separate controls, including M09 secrets/identity and M12 attestations/policy enforcement.

### 15.3 Consumer-side verification before install

The consumer should independently verify the exact release, not merely trust a publisher's pipeline badge. Pull the approved version, compare its digest to trusted release evidence, verify `.prov` and/or Cosign signature using the established trust root, inspect dependencies and rendered resources, then install. A required verification failure is a hard stop. Any exception should identify the approver, reason, scope, expiry, and compensating control.

## 16. L4 — Key lifecycle, mirroring, deprecation, and incident response

### 16.1 Signing-key lifecycle

A controlled signing-key lifecycle includes:

- **Generation:** create keys in an approved environment with documented algorithms and ownership.
- **Protected storage:** limit private-key access; use protected CI environments, secret managers, KMS, or HSM where appropriate. KMS/HSM are awareness concepts, not required paid lab infrastructure.
- **Separation of duties:** the person who authors a change should not automatically have unrestricted production signing authority when risk warrants separate approval.
- **Rotation:** publish a new public key/trust record, validate its fingerprint independently, transition signers and consumers, and define overlap periods.
- **Expiration/revocation:** update policy and trust stores, and define how historical signatures are evaluated.
- **Leak response:** revoke or distrust the affected key as appropriate, block releases signed by it, identify the exposure window, investigate artifacts, and notify consumers. Merely generating a replacement key is not enough.
- **Recovery:** test backup/recovery and access revocation without making private-key copies broadly available.

M09 covers secrets and identity controls; M12 covers wider attestations and enforcement.

### 16.2 Compromised or withdrawn chart versions

There is no universal, portable OCI “yank” semantic that every client and registry implements identically. Deletion, tag removal, retention, and garbage collection behavior must be verified for the specific registry. Even if future pulls are blocked, a compromised chart may already be deployed, cached, mirrored, or installed into clusters. Recall is not rollback.

Response playbook:

1. Stop promotion and release automation for the affected chart.
2. Identify all affected chart versions, package checksums, OCI digests, signatures, and dependencies.
3. Block/quarantine the artifact at registry and policy layers where supported.
4. Preserve registry audit logs, CI evidence, signatures, package files, and deployment records.
5. Publish a corrected **new chart version**; do not overwrite the same version as the fix.
6. Deprecate the affected version where the repository/tool supports it and publish a consumer migration plan.
7. Notify consumers and identify affected clusters from deployment inventory.
8. Review rendered resources, hooks, RBAC, and referenced image digests; assess whether workloads or data were affected.
9. Rotate or revoke signing keys if compromise is suspected; update trust stores and policies.
10. Verify mirror consistency, identify stale copies, and document follow-up controls.

### 16.3 Mirroring, replication, and tag drift

Replication is more than copying a tag. A destination may have a different digest, missing signature artifact, stale tag, incomplete dependency set, or different retention state. Compare the source and destination manifest digests using each registry's documented tooling, then verify signature/provenance at the destination. Do not assume signatures are copied automatically or that a destination signature is still discoverable.

A portable detection strategy is pseudocode because registry CLIs differ:

```text
for each approved chart reference:
    source_digest = query_digest(source_registry, repository, tag)
    mirror_digest = query_digest(mirror_registry, repository, tag)

    if either digest is missing:
        alert("missing artifact or metadata")
    else if source_digest != mirror_digest:
        quarantine_mirror_reference()
        alert("tag drift detected")

    verify_signature_at_source()
    verify_signature_at_mirror()
    compare_dependency_versions_and_release_evidence()
```

Record the command/tool used for each digest lookup. M01 Unit 5 is the forward reference for registry replication concepts.

### 16.4 Incident scenario 1 — A chart version was overwritten

**Detection:** two clusters report the same chart version but their package checksums, OCI digests, rendered manifests, or deployment behavior differ. Compare CI release evidence and registry audit logs. Use the registry's documented digest lookup; the command is implementation-specific `[VERIFY]`.

**Immediate containment:** stop promotion; block the affected tag or repository if supported; preserve both artifacts and audit records; avoid pulling and reinstalling the ambiguous tag.

**Investigation:** identify which clusters pulled which digest, timestamps, CI runs, source revisions, signature results, and mirrors. A matching version string alone cannot identify the content. If a signature was verified against one digest, determine whether both artifacts were signed and by which key.

**Recovery:** publish a corrected new chart version; update consumers to a verified digest/version; rotate credentials or keys if unauthorized overwrite is plausible; assess rendered resources and image references in affected clusters.

**Communication:** notify platform owners and service teams with affected versions/digests, known impact, mitigation, and next update time.

**Prevention:** enforce unique versions, immutable registry policy where available, least-privilege push permissions, digest capture, signature verification, audit alerts, and deployment inventory.

**Evidence versus uncertainty:** registry logs and digests can establish which artifact was present at recorded times; they may not establish which bytes a cluster originally fetched if no deployment evidence was retained.

### 16.5 Incident scenario 2 — Signing key leaked

**Detection:** unexpected signing activity, private-key exposure in logs or source control, suspicious signature timestamps, or a CI compromise indicates potential leakage.

**Immediate containment:** suspend signing jobs using the key, restrict affected credentials, preserve logs, and follow the organization's revocation process. Do not continue publishing while assuming that a newly generated key alone resolves the issue.

**Investigation:** identify where the key existed, who/processes accessed it, exposure window, artifacts signed during that window, and whether signatures were created by legitimate or unauthorized actors. Check fingerprints and release evidence. A valid signature from the leaked key no longer proves the intended publisher produced it.

**Recovery:** establish a new trust root, distribute and authenticate its public key independently, update consumer policy, re-sign only through a controlled process when appropriate, and block or explicitly re-evaluate artifacts signed during the exposure window.

**Communication:** notify security, platform owners, and consumers; explain the key identity, time window, affected releases, and required verification steps.

**Prevention:** protected signing environment, separation of duties, minimal access, short-lived credentials where appropriate, log redaction, rotation drills, and key access monitoring.

**Evidence versus uncertainty:** access logs may show reads or signing events, but absence of logs does not prove the key was not copied.

### 16.6 Incident scenario 3 — A mirror served a stale chart with a known CVE

**Detection:** vulnerability intelligence or deployment scanning identifies an old chart/image version at the mirror; compare source and mirror digests, chart version, image references, and mirror timestamps.

**Immediate containment:** stop new promotion from the stale mirror, quarantine or block the affected artifact, and direct consumers to an approved verified release. Do not delete evidence before determining the scope.

**Investigation:** determine whether the chart itself is vulnerable or whether a referenced image carries the CVE. Review the exact image digest, not just the image tag. Check mirror synchronization logs, retention behavior, dependency resolution, and whether signatures/SBOMs were copied.

**Recovery:** synchronize a reviewed new chart release, verify destination digests and signatures, update image references and SBOMs, and redeploy according to the service's risk/availability plan.

**Communication:** identify affected consumers and clusters, explain whether the CVE is exploitable in the deployed configuration, and state the mitigation timeline.

**Prevention:** digest comparison, scheduled mirror reconciliation, vulnerability/SBOM refresh, explicit mirror freshness SLOs, and alerts for missing signature metadata.

**Evidence versus uncertainty:** a mirror timestamp and digest mismatch establish staleness or divergence; they do not by themselves prove exploitability in a particular runtime configuration.

### 16.7 Incident scenario 4 — A transitive subchart changed upstream

**Detection:** a dependency update changes `Chart.lock`, packaged dependency contents, rendered resources, or dependency digests unexpectedly.

**Immediate containment:** stop the release and preserve the lockfile, package, dependency archive, and source metadata. Do not re-run an unconstrained update and overwrite the evidence.

**Investigation:** compare parent `Chart.yaml`, `Chart.lock`, dependency package versions/checksums, upstream repository/OCI digest, and rendered resource diff. Check whether a version constraint allowed a newer dependency or whether the same upstream version was replaced.

**Recovery:** pin an approved dependency version, re-vendor or resolve dependencies from a trusted source, review the diff, test, package a new parent chart version, and sign the new artifact.

**Communication:** notify the owning service team and chart maintainers; explain the changed dependency and whether resources or images changed.

**Prevention:** reviewed lockfiles, constrained dependency versions, mirrored dependencies, digest/signature verification, automated rendered-manifest diffs, and release evidence for transitive content.

**Evidence versus uncertainty:** a lockfile and package diff can show what changed; if the upstream registry did not retain prior content, reconstructing the exact previous dependency may require CI artifact backups.

## 17. Mandatory end-to-end lab and evidence checklist

This integrated lab combines Labs A–D. It is intentionally staged: finish each step and record the real observation before continuing.

**Needs:** Helm, Python, existing M01 registry, GPG and Cosign for their respective steps, optional `kind` for installation. Cluster is not required until the install step. Network access is limited to local registry access unless fetching dependencies/tool docs. Use a disposable registry namespace only if M01 explicitly provides one. Resource impact is modest, but `kind` consumes additional CPU, memory, and disk.

### End-to-end sequence

1. **Package:** run `helm lint`, tests, and `helm template`; package a FastAPI chart and record chart metadata, source revision, package filename, and SHA-256.
2. **Optional GPG provenance:** create a throwaway key, package a dedicated version with the supported Helm signing workflow, verify the `.prov`, and record the fingerprint and result.
3. **HTTP publication:** publish the `.tgz` and `index.yaml` to the local HTTP repository from Lab A. Pull it through the repository and compare package checksums.
4. **OCI publication:** verify M01 TLS/basic-auth configuration, log in, and push the package to the approved local repository path.
5. **Pull by version:** pull the chart and compare the package checksum to the original package.
6. **Pull by digest:** attempt only if the installed Helm/registry pair documents support. Record the exact command and result. If unsupported, document the limitation and use pull-by-version plus independent digest/checksum/signature verification as the supported alternative.
7. **Verify before install:** verify the applicable Helm provenance and/or Cosign signature against the exact artifact. Confirm trust-root fingerprint and release evidence independently.
8. **Inspect and render:** run `helm show chart`, `helm show values`, `helm show readme` where supported; extract the chart; render with the intended values; inspect RBAC, hooks, service accounts, resource privileges, and image references.
9. **Install only after gates pass:** check the active context and namespace before using `kind`.

   ```bash
   kubectl config current-context
   kubectl get namespaces
   ```

   Create or use a clearly disposable namespace on the intended lab cluster. Do not proceed if the context is unclear. Install the verified local archive using the intended release name and namespace. If the example chart uses the generic Python image without a FastAPI application, do not treat application readiness as a successful application test; use the actual FastAPI chart from earlier M06 lessons for workload testing.

10. **Controlled overwrite attempt:** use only a dedicated disposable registry namespace/repository approved for this lab. Record the digest before the attempt. Try the duplicate-version publication only if it is safe and the backend behavior is understood. Record whether it rejects, accepts, or changes the tag. Capture the digest afterward. Never perform this test against a shared/production namespace, and never overwrite the original release to test tampering.
11. **Cosign:** identify the exact OCI artifact digest, use a throwaway Cosign key pair, sign and verify using installed-version syntax and supported registry storage. Record the public-key checksum/fingerprint, subject digest, and actual result.
12. **Tamper test:** alter a copy or create a distinct test artifact with a distinct version/name. Run the applicable verification against changed content and record the result. Preserve the original signed package and signature evidence.
13. **Incident note:** document what happened, what was detected, which evidence supports the conclusion, what was blocked, what remains uncertain, and what remediation is required.
14. **Cleanup:** remove only disposable local files and the disposable `kind` cluster/namespace created for this lab. Do not delete shared registry artifacts, shared registry namespaces, production resources, or organizational keys.

### Evidence table — fill with actual observations

| Evidence item | Observation |
|---|---|
| `versions.txt` path and contents captured | [RECORD YOUR RESULT] |
| Chart name/version/`appVersion` | [RECORD YOUR RESULT] |
| Package filename and SHA-256 | [RECORD YOUR RESULT] |
| HTTP index entry and package URL | [RECORD YOUR RESULT] |
| HTTP pull checksum match/mismatch | [RECORD YOUR RESULT] |
| OCI reference and tag | [RECORD YOUR RESULT] |
| OCI digest and how it was obtained | [RECORD YOUR RESULT] |
| Pull-by-digest support and command tested | [RECORD YOUR RESULT] |
| GPG fingerprint and `helm verify` outcome, if run | [RECORD YOUR RESULT] |
| Cosign subject digest and verification outcome | [RECORD YOUR RESULT] |
| Trusted public-key fingerprint/checksum | [RECORD YOUR RESULT] |
| Rendered manifest review and image references | [RECORD YOUR RESULT] |
| Cluster context/namespace used, if installed | [RECORD YOUR RESULT] |
| Duplicate-version attempt and before/after digest | [RECORD YOUR RESULT] |
| Tamper-test result | [RECORD YOUR RESULT] |
| Registry implementation/version and limitations | [RECORD YOUR RESULT] |
| Incident note path | [RECORD YOUR RESULT] |

### Example incident note template

```text
Incident title:
Date/time:
Affected chart/version:
Affected package checksum / OCI digest:
Detection signal:
Evidence collected:
Containment performed:
Verification results:
Known impact:
Uncertainties:
Corrected version/digest:
Consumer communication:
Follow-up controls:
Owner and due date:
```

If a required capability is unsupported by the local registry or tool version, preserve the learning objective by documenting the blocker and using a valid, documented fallback. Do not fabricate successful verification.

## 18. Troubleshooting and failure analysis

| Symptom | Likely causes | Diagnostic checks | Remediation and prevention |
|---|---|---|---|
| `helm repo update` cannot reach local HTTP repository | Server stopped, wrong port/path, loopback mismatch, firewall, URL typo | Check server terminal, `curl -I http://127.0.0.1:8879/index.yaml`, confirm bind address | Restart from repository directory; use reachable address; bind to loopback for local-only lab |
| Repository responds but chart absent from search | Stale cached index, missing index entry, wrong alias | Inspect served `index.yaml`; run `helm repo update`; `helm search repo <alias>` | Regenerate index after package is present; update cache; validate chart name/version |
| `index.yaml` points to invalid/unreachable package URL | Wrong `--url`, bad relative path, package not uploaded | Open index and test the exact package URL | Correct base URL and publish package/index consistently; verify URLs before release |
| `helm pull` gets 404 or wrong version | Version not indexed, wrong repository alias, URL/path mismatch, stale cache | Inspect index entry, package URL, `helm search repo --versions` | Regenerate index and update cache; use explicit version; never overwrite a version |
| OCI login fails TLS | Wrong hostname/SAN, untrusted CA, expired cert, scheme/port mismatch | Check actual M01 cert/host; inspect Helm help and registry logs | Correct hostname/CA/cert; do not disable TLS verification as a general fix |
| OCI login fails authentication | Wrong credentials, wrong registry endpoint, account lacks access | Verify account and registry auth logs; do not print secrets | Re-inject credentials securely; grant least privilege; rotate exposed credentials |
| Local HTTP registry rejected | Helm expects TLS or option differs by version | `helm help registry login/push/pull`; verify M01 transport mode | Use TLS if configured; for disposable HTTP lab only use the installed tool's verified local-only option |
| OCI push fails path/name/version validation | Destination path includes incorrect chart name/version or archive metadata mismatch | Inspect `Chart.yaml`, package filename, command help | Use documented OCI destination convention; confirm name/version in packaged chart |
| Chart tag does not match expected version | Pushed wrong archive, stale tag, registry tag mutation | Inspect package metadata and registry tag/digest | Publish a new unique version; compare release evidence; enforce immutable-version policy |
| SemVer build metadata tag differs (`+` vs `_`) | OCI tag normalization | Inspect chart version and resulting registry tag | Verify Helm behavior and official docs; encode naming consistently; do not assume literal `+` tag |
| Pulled chart digest/checksum differs from evidence | Wrong artifact, overwritten tag, mirror drift, different digest layer compared | Compare `.tgz` SHA-256 separately from OCI manifest digest; inspect logs | Quarantine artifact; fetch trusted evidence; verify signature; investigate before install |
| `helm verify` cannot find provenance/keyring | `.prov` absent, wrong path, key not imported, keyring format mismatch | Inspect package and `.prov`; `helm help verify`; GPG key list | Use documented keyring workflow; obtain public key independently; stop if required provenance is missing |
| GPG verification fails after package modification | Archive bytes changed or mismatched `.prov` | Compare checksums and confirm exact archive path | Restore original package; create a new version for correction; do not bypass verification |
| Cosign cannot find signature/referrer | Registry storage unsupported, wrong digest/reference, credentials, version mismatch | `cosign help`; registry docs/logs; inspect exact subject digest | Verify supported signature-storage mechanism; use documented compatible configuration; do not claim success |
| Cosign signature exists but verification fails for another digest | Verification subject differs from signed subject | Compare exact source and destination digest and command arguments | Verify against the exact signed digest; sign a new artifact if content changed |
| Signing key missing/expired/revoked/suspected compromised | Key lifecycle problem, wrong key path, trust-store mismatch | Check key fingerprint, expiration/revocation status, CI audit records | Stop signing/promotion; follow key incident procedure; rotate and update trust policy |
| Dependency resolves unexpectedly | Loose version constraint, changed upstream, lockfile missing/stale | Inspect `Chart.yaml`, `Chart.lock`, `charts/`, dependency list | Pin approved versions, review lockfile diff, mirror verified dependencies |
| Mirror is stale or signature metadata missing | Replication lag/failure, incomplete copy, retention cleanup | Compare source/destination digest and signature verification; inspect sync logs | Quarantine stale mirror, resync through documented mechanism, verify after transfer |
| Registry GC/retention removed artifact or signature | Retention policy, untagged blob cleanup, signature storage relationship | Check registry policy/logs and implementation docs | Restore from trusted backup/mirror; adjust retention; test signature survival before rollout |
| CI logs expose credential/private key | Debug tracing, unmasked secret, command-line secret, artifact upload | Restrict log access; review pipeline configuration and audit logs | Revoke/rotate immediately; remove exposure where possible; use protected injection and redaction |
| Version overwrite rejected or changes digest | Backend-specific immutability or mutable tag behavior | Compare before/after digest and registry logs | Accept rejection as protective behavior; if changed, quarantine and investigate; enforce unique versions in CI |
| Signed chart renders unsafe resources | Signature verifies but policy/review absent | `helm template`; inspect RBAC/hooks/privilege/image references; run policy checks | Block installation, review publisher and chart, remediate with a new version; signing is not safety approval |

Do not apply a one-size-fits-all fix. Separate DNS/network, TLS, authentication, path/version, digest, signature-storage, cryptographic verification, trust, authorization, and policy failures.

## 19. Security and SRE operational checklists

### Publisher checklist

- [ ] Assign a unique chart version to every content change.
- [ ] Lint, test, render, and review the chart before packaging.
- [ ] Sign only from a protected CI or controlled signing environment.
- [ ] Use least-privilege push credentials.
- [ ] Keep secrets out of Git, terminal output, screenshots, and logs.
- [ ] Capture package checksum and OCI digest where available.
- [ ] Verify the published artifact by pulling it back.
- [ ] Record source revision, dependencies, image references, SBOMs, and release notes.
- [ ] Enforce immutable release policy and detect duplicate-version attempts.
- [ ] Promote the same verified digest across environments; do not rebuild different content silently.
- [ ] Define retention and rollback/migration procedures.

### Consumer checklist

- [ ] Use an approved registry and source.
- [ ] Pin an exact chart version and digest where supported.
- [ ] Authenticate the trusted key or publisher identity independently.
- [ ] Verify signature/provenance before installation.
- [ ] Inspect chart metadata, templates, hooks, and dependencies.
- [ ] Render with intended values and review Kubernetes resources.
- [ ] Inspect image references and scan/validate images and dependencies.
- [ ] Run schema, policy, and compatibility checks.
- [ ] Fail closed on required verification failure.
- [ ] Document any exception, approver, scope, expiry, and compensating controls.

### SRE/registry operator checklist

- [ ] Separate read/pull and write/push roles.
- [ ] Enforce TLS and authentication where appropriate.
- [ ] Monitor audit logs for unusual pushes, deletes, or tag changes.
- [ ] Document retention and garbage-collection behavior.
- [ ] Test backup, mirror, and recovery processes.
- [ ] Compare digests across replicas and verify signature evidence after transfer.
- [ ] Maintain a key rotation/revocation runbook.
- [ ] Maintain a compromised-version response playbook.
- [ ] Inventory consumers/clusters and maintain communication paths.
- [ ] Test registry and signature storage behavior before depending on it in production.

Keep five concepts separate: **artifact integrity** (content has not changed under the relevant digest/signature model), **publisher authentication** (which key/identity signed), **authorization** (whether that identity is allowed), **artifact safety** (whether its behavior is acceptable), and **runtime security** (how the deployed workload behaves and is controlled).

## 20. Common mistakes and anti-patterns

1. Treating a chart version string as proof of immutable content.
2. Treating an Artifact Hub listing as an endorsement or signature.
3. Assuming HTTP chart repositories and OCI registries use the same index/deletion model.
4. Publishing a changed chart under an existing version.
5. Comparing an archive checksum to an OCI manifest digest as if they were the same hash layer.
6. Trusting a public key downloaded from the same untrusted channel as the artifact without independent validation.
7. Treating signature verification as proof that the signer is authorized.
8. Treating a valid signature as proof that chart templates or images are safe.
9. Installing a third-party chart without `helm pull`, template, dependency, and image review.
10. Using plaintext registry transport with real credentials.
11. Giving CI administrative/delete permissions when push-only access is sufficient.
12. Putting private keys or passwords into source control, shell history, command arguments, or CI logs.
13. Assuming a registry supports OCI referrers, signature discovery, immutable tags, or portable yank behavior.
14. Assuming Cosign verification is automatically enforced by `helm install`.
15. Rebuilding a different chart for each environment instead of promoting the same verified artifact.
16. Ignoring transitive dependency changes because the top-level chart version stayed constant.
17. Deleting lab artifacts before recording evidence or finishing the tamper test.
18. Claiming a command succeeded because it appears in a guide rather than because it was executed and observed.

## 21. Knowledge checks and review questions

### Questions

1. What does `index.yaml` do in a classic HTTP chart repository?
2. Why does a chart archive's `.tgz` filename not establish trust?
3. What is the difference between chart `version` and `appVersion`?
4. Why should published chart versions be immutable even if a registry rejects overwrites?
5. What is the main architectural difference between HTTP chart repositories and OCI registries?
6. What does an OCI tag identify, and why is it weaker than an immutable digest as a content identifier?
7. Why should `helm repo update` follow a repository index change?
8. What does Helm provenance verify, and what does it not prove?
9. Why must the public signing key's fingerprint be checked through an independent channel?
10. What is the difference between a mathematically valid signature and an authorized publisher?
11. Why does Cosign verification need to refer to the exact artifact digest?
12. Why is signature verification not a replacement for chart template and image review?
13. How does a chart-package SBOM differ from an image SBOM?
14. Why is a mirror tag copy not enough to prove the mirror is current?
15. What should a CI pipeline do if a required signature verification fails?
16. Why is creating a new signing key insufficient by itself after a key leak?
17. What evidence helps investigate an overwritten chart version?
18. Why should a tamper test modify a copy or a distinct artifact rather than the original release?

### Answer key with reasoning

1. `index.yaml` catalogs chart names, versions, and package locations so Helm can search and resolve HTTP repository packages. It is discovery metadata, not the package or a complete trust mechanism.
2. A filename can be renamed and a package can be replaced. Trust needs a checksum/digest tied to trusted release evidence and, where required, signature/provenance verification.
3. `version` versions the chart package; `appVersion` describes the application version. Changing one does not automatically change the other or pin the image.
4. Immutable versions preserve reproducibility and incident evidence. Backend behavior varies, so CI and registry policy should prevent replacement even when the backend happens to allow it.
5. HTTP repositories typically use `index.yaml` and downloadable archives; OCI registries use registry APIs, repositories, tags, manifests, and blobs. Their access, replication, and deletion models differ.
6. A tag is a human-readable reference that may be mutable. A digest identifies specific content at a particular OCI object layer, but the operator must know which layer was hashed.
7. Helm searches its cached index. Refreshing updates the client's view of available versions and locations.
8. Provenance checks the chart archive against signed metadata and a key. It does not establish chart safety, publisher authorization, image security, or policy compliance.
9. Otherwise an attacker may substitute both artifact and key. Independent fingerprint validation establishes the intended trust root.
10. Mathematical validity establishes a cryptographic relationship; authorization requires policy to permit that key/identity to release this chart in this context.
11. A tag may resolve to different content over time. Verification against the exact digest ties the signature decision to the content intended for release.
12. A signer may sign unsafe code accidentally or maliciously. Rendered resources, dependencies, image references, and policy still require review.
13. A chart SBOM describes the chart package's contents as the tool can identify them; image SBOMs describe components inside referenced container images. They cover different artifacts.
14. The destination may point at a different digest, have stale content, or lack signature metadata. Compare digests and verify at the destination.
15. It should stop the release/install path, preserve evidence, and require an explicit documented exception if policy permits one. It should not silently downgrade failure to a warning.
16. The old key may still be used or trusted, and previously signed artifacts may be suspect. Investigate the exposure window, revoke/distrust the key, update consumers, and evaluate affected releases.
17. Package checksums, OCI digests, registry audit logs, CI source revisions, signature evidence, pull times, rendered manifests, and cluster deployment inventory help reconstruct what happened.
18. Preserving the original provides a reliable reference for comparing tampered content and keeps the release evidence intact.

## 22. Interview questions with model-answer outlines

Exactly six senior-level questions are included.

### 1. Compare HTTP chart repositories and OCI registry architecture and trade-offs.

**Model-answer outline:** Explain `index.yaml` plus `.tgz` download semantics versus OCI repositories, tags, manifests, and blobs. Compare discovery, access control, digest identity, signature storage, replication, retention/deletion, client behavior, and operational ownership. Note implementation variation and state the decision criteria for the organization's environment.

### 2. Compare Helm provenance and Cosign signatures, including trust bootstrapping.

**Model-answer outline:** Describe `.prov` metadata and GPG verification of a chart archive; contrast this with Cosign signatures associated with an OCI artifact. Explain exact subject identity/digest, public-key distribution, independent fingerprint validation, identity policy, signature-storage compatibility, and the distinction between cryptographic validity and authorization.

### 3. Why does signing not prove that a chart is safe?

**Model-answer outline:** A signature is evidence about integrity and signer/key under trust assumptions. It does not guarantee safe templates, minimal RBAC, secure images, vulnerability-free dependencies, publisher authorization, or correct runtime behavior. Add rendered-manifest review, dependency/image scanning, policy checks, and deployment monitoring.

### 4. Design a fail-closed chart release pipeline.

**Model-answer outline:** Follow lint → test → package → sign → push → verify-pull → attach SBOM → release notes. Use protected signing credentials, least-privilege push permissions, unique versions, digest/checksum capture, verification against the exact artifact, a duplicate-version guard, masked logs, release evidence, and consumer-side verification before installation. Required failures block release.

### 5. How would you respond to a compromised chart version or leaked signing key?

**Model-answer outline:** Stop promotion; preserve artifacts/logs; identify versions, digests, signatures, consumers, and clusters; quarantine/block affected content; assess key exposure and revoke/distrust as appropriate; publish a corrected new version; notify consumers; inspect rendered resources and image digests; verify mirrors; update trust policy; document follow-up controls. Do not overwrite the same version and do not assume deletion recalls installed workloads.

### 6. How do you keep mirrors and transitive dependencies trustworthy?

**Model-answer outline:** Pin dependency versions and review lockfiles; record dependency digests and provenance; mirror only after review; compare source/destination digests; verify signatures after transfer; detect tag drift and stale content; track SBOMs and CVEs; monitor missing metadata and retention; maintain audit trails and a consumer migration plan.

## 23. Glossary

- **Chart repository/source:** A location from which chart packages are discovered and retrieved.
- **`index.yaml`:** Catalogue metadata used by classic HTTP chart repositories to list versions and package URLs.
- **Chart archive/package:** A packaged Helm chart, commonly a `.tgz`, containing metadata, templates, values, and other chart files.
- **OCI:** Open Container Initiative specifications and formats for artifacts and distribution.
- **Manifest:** An OCI object describing an artifact and its referenced content; its digest identifies the exact manifest bytes.
- **Tag:** A human-readable registry reference that may be mutable unless policy/implementation prevents changes.
- **Digest:** A content-derived identifier for a particular object, such as an OCI manifest or a local package checksum.
- **SemVer:** Semantic Versioning, commonly `MAJOR.MINOR.PATCH`, with optional pre-release and build metadata.
- **Provenance:** Metadata and signature evidence associated with a packaged chart, such as Helm's `.prov` workflow.
- **Signature:** Cryptographic evidence that binds a signer key/identity to an artifact or digest under a defined scheme.
- **Trust root:** A public key, certificate, identity provider, or policy anchor accepted as a starting point for verification.
- **SBOM:** Software Bill of Materials describing components identified in a software artifact.
- **Attestation:** A structured statement about an artifact or process, often linked to a subject digest; M12 covers broader workflows.
- **Mirror:** A secondary copy of artifacts from a source registry/repository.
- **Immutable release:** A release whose published version is not intentionally replaced with different content.
- **Key revocation:** A process for invalidating or distrusting a key, usually with trust-store and policy updates.
- **Publisher identity:** The key or authenticated identity that signs or publishes an artifact.
- **Verification policy:** Rules defining acceptable sources, signers, versions, digests, signatures, and required checks.
- **Artifact integrity:** Evidence that the artifact matches an expected checksum/digest/signature.
- **Authorization:** A policy decision that an authenticated identity may perform a specific action.
- **Tag drift:** A tag resolving to different content across time or registry locations.
- **Transitive dependency:** A dependency brought in by another chart or component rather than declared only at the top level.

## 24. Official references and version-verification notes

Use primary documentation and the actual installed tool help. Documentation can change; record the date checked and the version to which the instructions apply. The URLs below are official project/documentation entry points known to be relevant; verify the exact page and current command form before production use.

| Topic | Official reference / search target | What to verify |
|---|---|---|
| Helm chart repositories | Helm documentation: `https://helm.sh/docs/topics/chart_repository/` | `index.yaml`, package URL behavior, repository commands |
| Helm OCI registries | Helm documentation: `https://helm.sh/docs/topics/registries/` | OCI support, login/push/pull forms, tag mapping, digest behavior |
| Helm chart packaging | Helm command reference: `https://helm.sh/docs/helm/helm_package/` | `helm package` flags and signing support |
| Helm verification | Helm command reference: `https://helm.sh/docs/helm/helm_verify/` | provenance/keyring behavior and exact flags |
| Helm dependency management | Helm documentation: `https://helm.sh/docs/helm/helm_dependency/` | OCI dependency syntax, update/build/list behavior |
| Helm CLI help | `helm help`, `helm help package`, `helm help verify`, `helm help pull`, `helm help registry login` | Installed-release syntax; treat help as version-specific |
| Cosign | Sigstore documentation: `https://docs.sigstore.dev/cosign/` | key-based signing, verification, keyless/OIDC concepts, signature storage |
| OCI Distribution Specification | OCI specifications: `https://github.com/opencontainers/distribution-spec` | Registry API, manifests, tags, digest semantics |
| OCI artifacts/referrers | OCI specifications: `https://github.com/opencontainers/image-spec` and related OCI artifact/referrers documentation | Artifact media types and referrer compatibility |
| Artifact Hub | Official site/documentation: `https://artifacthub.io/` | Catalog/discovery role and publisher-provided metadata |
| Docker Distribution / registry | `https://distribution.github.io/distribution/` | Auth, TLS, deletion, garbage collection, storage configuration |
| Syft | Anchore documentation: `https://github.com/anchore/syft` | Supported input types, output formats, chart-package limitations |
| Kubernetes | `https://kubernetes.io/docs/` | Resource behavior and cluster-side validation |
| Helm registry credential config | Helm documentation plus `helm env` | Config path, credential helper support, platform behavior |

If an official URL redirects or a specific page has moved, use the official documentation site's search rather than substituting an unverified third-party tutorial. The installed command help is useful for syntax, but it is not a substitute for understanding registry behavior or trust policy.

### Version verification record

Fill this table using your environment; do not leave a guessed version.

| Component | Command used | Installed version | Behaviors/flags to verify | Official documentation checked | Date checked |
|---|---|---|---|---|---|
| Helm | `helm version` | [FILL IN] | OCI support; `--plain-http` or equivalent; digest refs; OCI dependencies; `+` to `_`; provenance flags/keyring; `helm show readme` | [FILL IN] | [FILL IN] |
| Cosign | `cosign version` | [FILL IN] | Key generation; sign/verify syntax; OCI subject digest; signature storage/referrers | [FILL IN] | [FILL IN] |
| GPG | `gpg --version` | [FILL IN] | Key creation/export, fingerprint, keyring configuration, expiry/revocation | [FILL IN] | [FILL IN] |
| Registry implementation | M01 configuration / documented version command | [FILL IN] | TLS/basic auth; overwrite behavior; digest lookup; referrers; deletion/retention/GC | [FILL IN] | [FILL IN] |
| Python | `python3 --version` | [FILL IN] | `http.server` behavior and binding | [FILL IN] | [FILL IN] |
| kind (if used) | `kind version` | [FILL IN] | Disposable cluster and image pull/network behavior | [FILL IN] | [FILL IN] |
| kubectl (if used) | `kubectl version --client` | [FILL IN] | Context, namespace, API compatibility | [FILL IN] | [FILL IN] |
| Syft (if used) | `syft version` | [FILL IN] | Supported chart/archive source types and SBOM output | [FILL IN] | [FILL IN] |

At minimum, verify these before using commands in a production pipeline: Helm OCI command syntax; local plaintext transport options; digest pull/install behavior; OCI dependencies; SemVer build-metadata tag mapping; provenance flags and keyring format; Cosign signing/verification and registry signature storage; registry overwrite/deletion/retention/GC; and SBOM/attestation attachment commands.

## 25. Roadmap coverage audit

Statuses are intentionally conservative. Items that depend on the installed Helm/Cosign release, local registry, or unexecuted labs remain **Needs local verification**. “Covered” means the chapter teaches the concept and provides the corresponding workflow or evidence task; it does not mean the lab has been executed.

| Roadmap item | Required coverage | Chapter section(s) | Lab/evidence proving it | Status |
|---|---|---|---|---|
| HTTP chart repositories | `index.yaml`, `.tgz`, package/index/add/update/search/pull | 5, 6, 9 | Lab A package, index, search, pull, checksum | Covered |
| OCI distribution | login/push/pull/install | 5, 7, 10, 17 | Lab B and end-to-end workflow | Needs local verification |
| Chart archive and SemVer | Archive structure, chart versioning | 5.4, 6 | `helm show chart`, archive listing, versions file | Covered |
| Published-version immutability | Never intentionally overwrite; version label is not digest | 5.5, 15, 16 | Controlled overwrite attempt and digest record | Covered |
| Artifact Hub discovery versus trust | Catalog is not trust authority | 5.6, 14 | Third-party review checklist | Covered |
| FastAPI chart package | Minimal chart files and packaging | 9 | Package filename, metadata, checksum | Covered |
| Local HTTP repository | `python -m http.server`, `helm repo index` | 6, 9 | Index URL and server response | Covered |
| Consumption from HTTP repository | Add/update/search/pull | 5.2, 9 | Pull result and checksum comparison | Covered |
| M01 local `registry:2` workflow | TLS/basic-auth reference | 3, 7, 10 | M01 configuration and registry evidence | Needs local verification |
| Local-only insecure/plain HTTP behavior | Verify syntax; warn prominently | 7.1, 10 | Installed help output and transport mode | Needs local verification |
| Pull and inspect chart | `show chart/values/readme`, untar | 7.2, 11 | Inspection evidence | Needs local verification |
| Pull/install by version and digest | Verify support; fallback if unsupported | 7.2, 7.4, 17 | Digest syntax and actual result | Needs local verification |
| OCI chart dependencies | `Chart.yaml`, dependency resolution, lockfile | 7.3, 10, 11 | Dependency list and `Chart.lock` | Needs local verification |
| Credential helpers/no passwords in logs/M02/M09 | Secure login, least privilege, references | 7.1, 10, 15 | Version/config record and CI review | Covered |
| OCI tag/version and `+` to `_` | Mapping and verification | 5.4, 7.4 | Disposable version test | Needs local verification |
| Helm `.prov`, GPG, `package --sign`, `verify`, applicable `--verify` | Provenance workflow and limits | 12 | Lab C fingerprint, `.prov`, verification result | Needs local verification |
| Cosign key-based signing/verification | OCI artifact, digest, registry storage | 13 | Lab D command/result evidence | Needs local verification |
| Keyless/OIDC awareness only | Identity/transparency/policy | 13.5 | Conceptual review; no live lab required | Covered |
| What signatures prove/do not prove | Integrity, identity, authorization, safety | 2, 12, 13.6, 19 | Review and policy checklist | Covered |
| Verify before install in CI | Fail-closed sequence | 14, 15 | Consumer gate evidence | Covered |
| Pin versions/digests | Human-readable version vs immutable content | 5.5, 7.4, 14 | Digest and package evidence | Covered |
| Chart/image SBOM distinction and image extraction | Syft limits, rendered image references, M12 forward ref | 14.2 | SBOM and image reference record | Covered |
| Read/push controls and M01 Unit 7 | Least privilege and audit | 7.1, 14.3 | Role and permission evidence | Covered |
| Retention/garbage collection | Registry-specific behavior | 14.3, 16.2 | Registry documentation and test | Needs local verification |
| Mirroring/proxying third-party charts | Preserve source/version/digest/signature/review | 14.3, 16.3 | Source/destination digest record | Covered |
| Approved-source/signature policy and M12/M08 | Policy and enforcement awareness | 14.1, 14.3 | Consumer policy review | Covered |
| Review third-party charts with `helm pull` and `helm template` | Pull, render, inspect | 11, 14 | Rendered manifest and review notes | Covered |
| Avoid blind `helm repo add` | Source review and approved-source policy | 11, 14.3 | Consumer checklist | Covered |
| Release pipeline sequence | lint → test → package → sign → push → verify-pull → SBOM → release notes | 15 | Pipeline and evidence bundle | Covered |
| Least-privilege CI; local-registry-only lab | Protected credentials and local publishing | 10, 15, 17 | CI design and local registry record | Needs local verification |
| Key rotation/revocation/KMS-HSM/M09/M12 | Lifecycle and references | 16.1 | Key lifecycle runbook | Covered |
| Compromised/yanked version response | Limits of recall and response | 16.2, 16.4 | Incident note | Covered |
| Mirroring/replication/tag drift/M01 Unit 5 | Digest comparison and pseudocode | 16.3 | Source/mirror digest evidence | Covered |
| Chart deprecation | Consumer migration plan | 16.2 | Deprecation/migration note | Covered |
| Consumer approved-source/signature policy | Verification before install | 14, 15.3 | Consumer-side gate | Covered |
| Incident: overwritten chart version | Detection, containment, investigation, recovery, communication, prevention | 16.4 | Incident evidence | Covered |
| Incident: leaked signing key | Key exposure response | 16.5 | Key incident record | Covered |
| Incident: stale mirror with CVE | Mirror/image assessment | 16.6 | Digest, image, and CVE evidence | Covered |
| Incident: changed transitive subchart | Lockfile/dependency diff and remediation | 16.7 | Dependency evidence | Covered |
| End-to-end package/publish/pull/verify/install/overwrite/Cosign/tamper | Integrated local workflow | 17 | End-to-end evidence table | Needs local verification |
| Throwaway keys and plaintext warning | Lab-only key and transport boundary | 3, 7.1, 12, 13, 17 | Key and transport records | Covered |

### Final learner evidence checklist

- [ ] `evidence/versions.txt` records actual tool versions.
- [ ] Lab A records chart metadata, `.tgz` checksum, index entry, HTTP search/pull, and stale-index behavior.
- [ ] Lab B records actual M01 registry TLS/auth configuration, OCI reference/tag, package checksum, and digest lookup method.
- [ ] The installed Helm version's OCI, digest, dependency, build-metadata, and provenance behavior is documented.
- [ ] Lab C records the throwaway GPG fingerprint, `.prov` file, verification result, and tamper result if the workflow is supported.
- [ ] Lab D records the throwaway Cosign public-key fingerprint/checksum, exact subject digest, signing/verification commands, registry compatibility, and tamper result.
- [ ] Consumer review includes rendered manifests, dependency versions, image references, and policy/scan evidence.
- [ ] The release pipeline is fail-closed and cannot silently overwrite a published chart version.
- [ ] The end-to-end evidence table contains real observations rather than assumed successes.
- [ ] Cleanup preserves shared registry artifacts and all evidence required for the labs and any incident review.

**Unit completion criterion:** the learner can explain the difference between finding a chart, identifying its exact content, verifying its signer, deciding whether the signer is trusted and authorized, and deciding whether the chart is safe to deploy—and can show local evidence for each applicable gate.
