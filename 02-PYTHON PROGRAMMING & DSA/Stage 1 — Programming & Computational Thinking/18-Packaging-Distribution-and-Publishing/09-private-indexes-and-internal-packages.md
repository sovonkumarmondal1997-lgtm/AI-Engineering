# Private Indexes and Internal Python Packages

> **Audience:** Python developers, data engineers, platform engineers, and software-supply-chain practitioners  
> **Target:** Python 3.12+, `uv` projects, PEP 503/691-compatible indexes  
> **Security principle:** A package index is a source of artifacts, not proof that those artifacts are trustworthy. Control which source may supply each package, then verify the artifact and the process that produced it.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain why organizations publish internal libraries and distinguish a package name from an import name.
- Describe how installers discover distributions through the Simple Repository API (PEP 503 HTML and PEP 691 JSON).
- Configure `uv` so an internal distribution is resolved from one named index only, and interpret the source in `uv.lock`.
- Explain dependency confusion, why unsafe multi-index resolution creates risk, and which controls address the different parts of that risk.
- Authenticate without committing credentials; separate read, publish, administer, and promote permissions.
- Build and publish an internal wheel to a development registry or a static Simple API index, then install and test it in a clean environment.
- Design retention, quarantine, provenance, recovery, and incident-response controls for an organization package platform.

### Prerequisites

You should already understand `pyproject.toml`, wheels and source distributions, build backends, semantic versioning, dependency constraints, virtual environments, `uv` locking/syncing, CI secrets, and basic hashes/signatures. Earlier packaging lessons cover building and publishing public packages, Trusted Publishing, release automation, and namespace packages. This lesson focuses on the **source and governance of distributions**.

### Vocabulary

- **Distribution/package project:** The named artifact installers resolve, e.g. `acme-data-client`.
- **Import package:** The Python name imported by code, e.g. `acme_data_client`. The names need not match.
- **Index/registry:** An HTTP service or static site that exposes package files and metadata through a package-index protocol.
- **Repository:** A provider-specific term that may mean a hosted, proxy, virtual, staging, or release repository. Check the provider's semantics.
- **Lockfile:** A record of a resolved dependency graph, versions, sources, and artifact hashes where supported. It is not a policy engine or an attestation by itself.
- **Promotion:** Moving or authorizing an already-built artifact from a development/quarantine channel to a release channel without rebuilding it.

## 2. Private-index architecture

### 2.1 Why internal packages exist

A well-governed internal package avoids copy-and-paste implementations and gives a team a maintained, versioned interface. Typical examples include:

| Distribution | Example import | Purpose | Ownership example |
|---|---|---|---|
| `acme-data-client` | `acme_data_client` | Authenticated access to company data APIs | Data Platform |
| `acme-feature-kit` | `acme_feature_kit` | Reusable feature transformations and validation | ML Platform |
| `acme-shared-models` | `acme_shared_models` | Shared request/response and event schemas | Architecture/API team |
| `acme-platform-cli` | `acme_platform_cli` | Repeatable developer and operations workflows | Developer Platform |

Internal packages should have an owner, supported Python versions, a documented public API, a security contact, a release cadence, a deprecation policy, and a defined compatibility promise. Avoid publishing large datasets, model weights, or other large binaries as Python wheels; use artifact or model registries designed for those objects.

### 2.2 Public versus private indexes

A public index such as PyPI is broadly accessible. A private index restricts some combination of visibility, upload, deletion, and administration. A registry may also proxy or cache public packages. Those are separate properties:

- **Visibility** controls who can discover/download an artifact.
- **Authentication** establishes an identity; **authorization** decides what that identity can do.
- **Resolution policy** determines which source may supply a dependency.
- **Integrity/provenance controls** help determine whether the bytes match an expected artifact and whether the build process is trustworthy.
- **Availability controls** determine whether clients can install during outages or network isolation.

A private URL does not automatically provide safe dependency resolution, immutable releases, malware scanning, provenance, or disaster recovery. Validate those capabilities against the specific registry product and configuration.

### 2.3 Common deployment models

| Model | Strengths | Costs and risks | Good fit |
|---|---|---|---|
| Managed registry (for example, AWS CodeArtifact, Google Artifact Registry, Azure Artifacts, GitLab/GitHub Packages, Artifactory Cloud) | Provider identity integrations, audit logs, access controls, managed availability | Provider-specific behavior and costs; features vary by tier | Teams already using the provider's identity and CI |
| Self-hosted registry (for example, `devpi`, Nexus, Artifactory) | Control over policy, network boundaries, upstreams, and retention | Operations, patching, backups, storage, certificates, on-call burden | Organizations needing control or on-premises/air-gapped use |
| Virtual/proxy registry | One approved endpoint can serve internal packages and vetted public packages | Proxy rules, upstream outages, and cache poisoning/staleness need management | Strong default for most organizations that need public and internal dependencies |
| Mirror/cache | Faster CI and partial resilience; can support controlled egress | A cache is not necessarily a policy boundary; freshness and purge semantics vary | CI acceleration and egress reduction, ideally behind a policy-enforcing proxy |
| Static Simple API index | Minimal infrastructure; can serve immutable files from object storage/CDN | No built-in upload workflow, auth, quarantine, or metadata management unless added separately | Small internal use, offline/wheelhouse delivery, controlled environments |

`devpi` is useful for learning and self-hosted workflows. Managed registries may offer stronger identity integration and operational guarantees. A static index is only as secure as the object store, web server, publishing pipeline, and access controls around it.

### 2.4 Reference architecture

A mature platform commonly separates the following paths:

1. **Developer/CI read path:** authenticated access to an approved virtual/proxy index.
2. **Build path:** source checkout, isolated build, tests, vulnerability/license checks, SBOM, provenance/attestation.
3. **Upload path:** narrowly scoped CI identity uploads to a staging repository; developers generally do not have production upload rights.
4. **Quarantine and review:** scan, verify metadata, inspect suspicious changes, apply cooldowns where appropriate, and record exceptions.
5. **Promotion path:** promote the same artifact digest to release; do not rebuild it between stages.
6. **Consumption path:** deployments use a release index or approved mirror with locked dependencies and auditable source configuration.
7. **Recovery path:** backups, replication or mirror, restore drills, and an inventory of consumers and installed versions.

The registry should enforce what it can; CI and deployment policy should independently validate the artifact and its provenance. Do not rely on a developer workstation's global configuration as the only control.

## 3. Package discovery and resolution fundamentals

### 3.1 The Simple Repository API

The Python Packaging Authority's Simple Repository API is the standard interface used by installers to discover distribution files. PEP 503 defines the original HTML representation; PEP 691 defines a JSON representation negotiated through HTTP `Accept` headers. A typical base URL is `https://packages.example.com/simple/` and a project page is:

```text
GET /simple/acme-data-client/
```

The page links to downloadable wheels and/or source distributions, optionally with metadata such as hashes, `Requires-Python`, yanked status, or separately available core metadata. Project names are normalized for URLs (runs of `.`, `_`, and `-` are treated equivalently and normalized to lowercase with hyphens). The API tells an installer where candidate files are; the resolver then considers versions, Python compatibility, platform tags, dependency metadata, and policy.

Useful references: [Simple Repository API specification](https://packaging.python.org/en/latest/specifications/simple-repository-api/), [PEP 503](https://peps.python.org/pep-0503/), and [PEP 691](https://peps.python.org/pep-0691/).

A simple index is not the same as a package-upload API. PEP 503/691 describe discovery, not how a maintainer uploads a distribution. Uploads use a registry-specific interface, such as a provider API, `twine`, or a `devpi` upload command.

### 3.2 Resolution at a high level

For a declared requirement such as `acme-data-client>=2,<3`, an installer generally:

1. Reads project metadata and constraints from the project and its lockfile, if applicable.
2. Determines the permitted indexes/sources from command-line options, project config, environment, and tool-specific policy.
3. Queries project pages and filters available files by version constraints, `Requires-Python`, wheel tags, yanking, and other metadata.
4. Resolves the full dependency graph and reports conflicts if constraints cannot be satisfied.
5. Downloads selected artifacts, checks available hashes/integrity data, and installs them.

The exact index search and tie-breaking rules are **package-manager-specific**. Do not assume pip and uv have identical behavior.

### 3.3 `--index-url`, `--extra-index-url`, and uv indexes

With pip, `--index-url` selects the primary index URL, while `--extra-index-url` adds another index. Pip does not provide a security boundary that says “internal packages always come from this source”; candidates across configured locations may be considered together. A higher version on a public index can therefore win for an internal-looking name.

In uv project configuration, use `[[tool.uv.index]]` entries and, for internal names, `tool.uv.sources` package-to-index mapping. The current uv default strategy is `first-index`: for a given project, uv stops at the first index where that project exists and restricts candidates to that index. This is safer than merging all candidate versions, but it is not a substitute for explicit source pinning and registry policy. Do not enable `unsafe-best-match` for production dependency resolution unless a documented exception has been reviewed; it deliberately removes an important defense against dependency confusion.

`default = true` changes which index is treated as the default and can replace PyPI as the default fallback. It does **not** mean the index is used only for one package. `explicit = true` means the index is only considered for packages explicitly mapped to it via `tool.uv.sources`. These are distinct settings.

## 4. Dependency-confusion threat model

### 4.1 Attack sequence

Suppose a company uses a private package named `acme-feature-kit`, but the name is not reserved on the public index. An attacker discovers the name and uploads a malicious public distribution with the same normalized project name and a higher version. A build configured to search both public and private sources without a source-selection rule may select the attacker's artifact. Its installation/build hooks or imported code can execute in CI or production, potentially stealing credentials, modifying artifacts, or accessing data.

This is a source-selection problem as much as a versioning problem. Merely using a private registry does not solve it if the package manager can choose the public copy. Likewise, using a higher private version is not a robust defense: an attacker can publish an even higher one, and version comparisons are not ownership controls.

### 4.2 Controls and what each one protects

1. **Use one policy-enforcing virtual/proxy index** for normal consumption. It should serve approved public packages and internal packages while preventing upstream resolution of reserved internal names. This centralizes policy and reduces client configuration drift.
2. **Explicitly map internal distributions to a named uv index** and mark that index `explicit = true`. This makes the intended source clear in the project configuration.
3. **Reserve relevant names on public registries** when feasible. Reservation reduces name squatting but is not a substitute for source pinning.
4. **Apply registry ownership and upstream-blocking rules.** Internal namespaces should not silently fall through to public upstreams. Test the policy with a deliberately duplicated test name in a non-production registry.
5. **Lock dependencies and review lockfile changes.** Locks improve reproducibility and record expected versions, source locations, and hashes. A lockfile can faithfully lock a malicious artifact if the original resolution was unsafe or the lock was updated carelessly.
6. **Verify artifact integrity and provenance.** Hashes detect byte changes relative to the expected hash; they do not establish that the artifact is benign. Provenance/attestation verification can connect an artifact to an expected repository/workflow/identity, if the verifier and policy actually enforce it.
7. **Restrict publishing rights and make releases immutable.** A compromised developer token should not be able to overwrite a production release or change upstream policy.
8. **Audit installed versions and source.** Know which workloads consumed an affected package so response can be targeted.

### 4.3 Why hashes and lockfiles are not enough

A hash answers, “Are these bytes the same as the bytes represented by this digest?” It does not answer, “Was this the right publisher, was the build trustworthy, or is the code safe?” A lockfile can include a registry source and hash, but if it was created from an attacker-controlled source, the lock can make that malicious choice repeatable. Lockfiles need source policy, review, and CI enforcement around them.

### 4.4 Package naming and ownership

Choose names that communicate organization and ownership, for example `acme-data-client`, `acme-feature-kit`, and `acme-platform-cli`. Normalize names when checking for collisions: `acme_feature_kit`, `acme-feature-kit`, and `acme.feature.kit` normalize to the same project name. Keep a registry catalog with owner, support status, repository, license, release channel, security contact, and public/private classification. Avoid publishing internal source, secrets, or proprietary metadata to public registries.

## 5. Safe index configuration with uv

### 5.1 Recommended project-level pattern

The following is a complete, illustrative `pyproject.toml` for an application that uses public packages from PyPI and obtains `acme-data-client` only from the internal index. The hostname is an example; replace it with the approved endpoint. Do not put credentials in the URL.

```toml
[project]
name = "analytics-job"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "acme-data-client>=2.4,<3",
  "httpx>=0.27,<1",
]

[tool.uv]
package = false

[[tool.uv.index]]
name = "internal"
url = "https://packages.example.com/simple"
explicit = true

[tool.uv.sources]
acme-data-client = { index = "internal" }
```

The `explicit = true` setting prevents the internal index from being searched for arbitrary dependencies unless a package is explicitly mapped to it. The `tool.uv.sources` entry maps this distribution to that index. Other dependencies use the default PyPI index unless organization policy configures a different default. For stricter organizations, point the default to an approved virtual/proxy registry instead of public PyPI.

Commands from the project directory:

```bash
uv lock
uv sync --locked
uv run --locked python -c "import acme_data_client; print(acme_data_client.__file__)"
```

`--locked` tells uv to use the committed lock without silently updating it; the exact command options can vary by uv release, so consult the [uv CLI reference](https://docs.astral.sh/uv/reference/cli/). For CI, pin the uv version, review lockfile diffs, and run a clean sync.

### 5.2 Understanding the lock entry

A uv lockfile entry for a registry-sourced package contains package metadata, a registry source, and one or more distribution records with hashes. A representative entry can look like this (fields and ordering can vary by uv version and package/artifact selection):

```toml
[[package]]
name = "acme-data-client"
version = "2.4.1"
source = { registry = "https://packages.example.com/simple" }
sdist = { url = "https://packages.example.com/files/acme_data_client-2.4.1.tar.gz", hash = "sha256:REPLACE_WITH_REAL_DIGEST", size = 12345 }
wheels = [
  { url = "https://packages.example.com/files/acme_data_client-2.4.1-py3-none-any.whl", hash = "sha256:REPLACE_WITH_REAL_DIGEST", size = 9876 },
]
```

**This is an explanatory shape, not a copyable lockfile.** Real URLs, digests, sizes, dependency entries, and selected files must come from the registry. Do not invent a digest or hand-edit `uv.lock`. The key evidence is the `source.registry` field plus artifact hashes and URLs. A lockfile may use a registry URL or another source representation depending on the dependency type and uv version. It does not store registry credentials.

Review lockfile changes like code: verify that internal packages still point at the intended host, versions are expected, hashes change only with approved artifact updates, and no direct URL or unapproved registry was introduced. A package's lock source is valuable audit evidence, but runtime/network policy should still restrict permitted sources.

### 5.3 Index priority and source mapping

- **Named index + `explicit = true` + source mapping:** strong project-level expression of which index may supply a specific internal package.
- **A single approved proxy/default index:** centralizes public/private policy and is often the easiest organization-wide default.
- **Multiple non-explicit indexes:** increase configuration complexity; do not assume their order gives equivalent protection across tools.
- **`default = true`:** makes that configured index the default and removes the implicit PyPI fallback. Useful when all public dependencies must flow through an approved proxy.
- **`--index-url` / `--extra-index-url`:** useful for compatibility and one-off operations, but avoid scattering security-critical source policy across shell history and CI flags. For uv, prefer `--index` for additional indexes where applicable; legacy options may be deprecated in some commands.

Avoid configuring `UV_INDEX_STRATEGY=unsafe-best-match` in production. Do not rely on “the private index is listed first” as the sole policy. Prefer explicit source mapping and a registry that prevents internal names from being proxied from upstream.

### 5.4 pip configuration: a warning, not the primary recommendation

pip can use a private index with `--index-url` or `PIP_INDEX_URL`. For example, in a controlled environment where the private registry is an approved virtual index for **all** dependencies:

```bash
python -m pip install --index-url https://packages.example.com/simple acme-data-client==2.4.1
```

Do not recommend this unsafe pattern for production internal packages:

```bash
# UNSAFE EXAMPLE — do not use as a dependency-confusion mitigation
python -m pip install acme-data-client --extra-index-url https://packages.example.com/simple
```

The unsafe example is shown only to explain the failure mode. pip may consider candidates from multiple indexes without a trusted source preference; an attacker-controlled higher version can win. If an organization uses pip, the preferred mitigation is a single approved proxy/virtual index with upstream controls, plus lock and artifact verification. pip's `--require-hashes` can enforce hashes for the fully pinned requirements set, but it does not repair a malicious initial resolution.

## 6. Authentication and registry operations

### 6.1 Authentication versus authorization

Use separate roles:

- **Consumer/read:** download approved artifacts only.
- **Publisher:** upload to a development/staging repository only.
- **Promoter/releaser:** promote an approved digest to release.
- **Administrator:** configure upstreams, permissions, retention, and registry settings.

Use least privilege and separate identities for developer machines, CI jobs, and production deployments. Read tokens should not be able to publish; publisher tokens should not administer repositories; routine jobs should not hold administrator credentials.

### 6.2 uv credentials without secrets in source control

Keep the index URL credential-free in `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "internal"
url = "https://packages.example.com/simple"
explicit = true
```

For an index named `internal`, uv supports environment variables such as:

```bash
# POSIX shell examples. Inject these from a secret manager; do not hard-code values.
export UV_INDEX_INTERNAL_USERNAME="token-user"
export UV_INDEX_INTERNAL_PASSWORD="$PACKAGE_READ_TOKEN"
uv sync --locked
```

The environment variable suffix is derived from the configured index name: uppercase it and replace non-alphanumeric characters with underscores. Confirm the exact behavior against the uv version pinned by your organization. uv also supports `.netrc`, its credentials store, and keyring integration; provider-specific authentication may use short-lived cloud credentials or workload identity. The uv credentials store has historically used a plaintext state file on some platforms; do not assume it is OS-keychain-backed unless the selected feature/version is explicitly configured and verified.

Security practices:

- Prefer short-lived tokens or workload identity/OIDC where the registry supports it.
- Scope tokens to a repository, action, and expiration; rotate and revoke them on schedule and incident.
- Never commit credentials to `pyproject.toml`, lockfiles, shell scripts, Dockerfiles, notebooks, logs, or CI artifacts.
- Redact URLs and environment dumps from logs; credentials embedded in URLs may leak through process listings, logs, shell history, or exception traces.
- Do not pass secrets as ordinary Docker build arguments. Use BuildKit secret mounts or the CI platform's secret mechanism; see the container-stage lesson.
- Use TLS with certificate validation. Do not “fix” certificate failures by disabling TLS verification; install the correct CA or configure the approved trust bundle.
- Ensure CI's read token cannot upload packages. Use a separate publish job with a narrowly scoped token and protected environment.

### 6.3 Publishing: build, inspect, upload

Build artifacts in CI from a tagged commit, test the built wheel, and publish only after checks pass. A minimal package project might use this `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling>=1.26"]
build-backend = "hatchling.build"

[project]
name = "acme-data-client"
version = "2.4.1"
description = "Internal client for Acme data services"
requires-python = ">=3.12"
readme = "README.md"
license = "MIT"
dependencies = ["httpx>=0.27,<1"]

[tool.hatch.build.targets.wheel]
packages = ["src/acme_data_client"]
```

Example layout:

```text
acme-data-client/
├── pyproject.toml
├── README.md
├── src/
│   └── acme_data_client/
│       ├── __init__.py
│       └── client.py
└── tests/
    └── test_client.py
```

Build and inspect locally (with a current uv and the project's build backend installed by the build process):

```bash
uv build
python -m zipfile -l dist/acme_data_client-2.4.1-py3-none-any.whl
```

Run tests against the installed wheel in a clean environment before upload. Do not use a working tree or editable install as the only test; it can hide packaging mistakes. The version in the filename must match the project metadata and the version intended for release.

#### Upload with uv

For a registry that accepts the PyPI upload protocol, `uv publish` can publish built artifacts. A generic command is:

```bash
uv publish --publish-url https://upload.example.com/legacy/ dist/*
```

The upload URL is provider-specific and is not necessarily the same as the `/simple` install URL. Set authentication using the supported uv/publishing credential mechanism or CI secret, and confirm the provider's upload protocol and URL before running. Never assume a generic example URL works against a real registry. If the provider requires `twine`, use its documented upload endpoint, for example:

```bash
python -m twine upload --repository-url https://upload.example.com/legacy/ dist/*
```

The preceding commands are templates, not executed uploads. For cloud registries, follow the official provider integration and prefer federated/short-lived credentials when available.

### 6.4 Development, staging, and release channels

Use separate repositories or channels for development, quarantine/staging, and production releases. Mark development versions clearly, such as `2.5.0.dev3`, and avoid allowing production services to resolve prereleases unless explicitly intended. Define whether releases are immutable, how yanking/deletion works, and whether old artifacts are retained for incident investigation. Promotion should move the same artifact digest, not rebuild from a potentially changed source or dependency environment.

### 6.5 Upstream proxying, caching, and mirroring

A proxy may fetch public packages on demand, cache them, and apply allow/deny rules. A mirror may replicate upstream content on a schedule or snapshot. A cache may improve speed without enforcing policy. Decide and document:

- Which upstreams are allowed and whether direct egress to public package hosts is blocked.
- Whether internal names are blocked from upstream resolution.
- Whether new versions are quarantined or delayed for a cooldown period.
- How yanked, malicious, and vulnerable releases are handled in cache and mirrors.
- Cache TTL, invalidation, stale-data behavior, and how to purge compromised artifacts.
- Whether mirror snapshots are reproducible and whether offline installs can be verified.

A mirror can improve resilience, but if it blindly mirrors a malicious artifact it also preserves the threat. Apply policy at ingest and keep audit evidence.

## 7. Hands-on internal package publication

This lab demonstrates a local development registry using `devpi`. It is a learning setup, not a production-hardening recipe. Pin the tool versions in a disposable environment and consult the current [devpi documentation](https://devpi.net/docs/devpi/devpi/stable/+doc/index.html) for command changes. Use loopback binding only; do not expose an unauthenticated development service to a network.

### 7.1 Create a package

Create the layout from Section 6.3, add a simple implementation:

```python
# src/acme_data_client/__init__.py
__version__ = "2.4.1"


def normalize_dataset_name(name: str) -> str:
    """Return a normalized identifier used by internal data jobs."""
    return "_".join(name.strip().lower().replace("-", " ").split())
```

And a test:

```python
# tests/test_client.py
from acme_data_client import normalize_dataset_name


def test_normalize_dataset_name() -> None:
    assert normalize_dataset_name("  Customer-Events ") == "customer_events"
```

Run tests and build the wheel:

```bash
uv run --with pytest pytest
uv build
```

If your project does not declare pytest as a development dependency, use the project's established dev-dependency mechanism rather than relying on an implicit global installation.

### 7.2 Start a local devpi server

In a separate disposable environment, install the devpi server and client tools. Initialize a dedicated server directory, then run the server in a separate terminal bound only to loopback. This avoids relying on a convenience command whose availability can vary by devpi release. Consult the current [devpi documentation](https://devpi.net/docs/devpi/devpi/stable/+doc/index.html) for version-specific flags and lifecycle commands.

```bash
python -m venv .devpi-venv
. .devpi-venv/bin/activate        # Windows: .devpi-venv\Scripts\activate
python -m pip install devpi-server devpi-client
mkdir .devpi-server
# Initialize the disposable server state.
devpi-init --serverdir .devpi-server
```

In a second terminal, activate the same tool environment and start the server:

```bash
devpi-server --serverdir .devpi-server --host 127.0.0.1 --port 3141
```

Then, in the client terminal, configure a dedicated lab user and index:

```bash
devpi use http://127.0.0.1:3141
devpi user -c alice email=alice@example.invalid
# Set a unique lab password using the prompt or documented option for your devpi-client version.
devpi login alice
devpi index -c dev bases=root/pypi
devpi use alice/dev
```

Use a unique disposable password; do not reuse a real credential or expose the service to a network. If a command or flag differs in the installed release, use that release's `--help` and official documentation. Stop the server when the exercise is complete.

### 7.3 Upload to devpi

With the upload index selected, upload the distribution from the package project:

```bash
# From the package project directory, with dist/ containing the wheel and sdist.
devpi upload dist/*
```

Confirm that the package/version appears on the devpi project page and that the upload user has only the intended permissions. If upload fails, check the selected index, credentials, project version, and server logs. Do not enable anonymous upload to make the lab easier.

### 7.4 Install from a clean virtual environment

Create a separate consumer directory and virtual environment, not inside the package source tree. In the consumer project's `pyproject.toml`, point a named uv index at the local Simple API endpoint for the selected devpi index. For the lab index `alice/dev`, the Simple API URL is typically `http://127.0.0.1:3141/alice/dev/+simple/`; verify the exact URL from devpi's project page/CLI.

For a disposable local lab only, an example configuration is:

```toml
[project]
name = "internal-client-smoke-test"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["acme-data-client==2.4.1"]

[tool.uv]
package = false

[[tool.uv.index]]
name = "devpi-internal"
url = "http://127.0.0.1:3141/alice/dev/+simple/"
explicit = true

[tool.uv.sources]
acme-data-client = { index = "devpi-internal" }
```

Replace `alice/dev` with the actual index you created. The HTTP URL is acceptable only because this is loopback-only and disposable. Use HTTPS and certificate validation for any networked registry.

```bash
uv lock
uv sync --locked
uv run --locked python -c "import acme_data_client; print(acme_data_client.__file__)"
uv run --locked python -c "from acme_data_client import normalize_dataset_name; assert normalize_dataset_name('Customer-Events') == 'customer_events'"
uv tree
```

Inspect `uv.lock` and verify the package source points to the local devpi index. Confirm the imported file lives under the consumer virtual environment's `site-packages`, not the package checkout. If `uv` cannot authenticate or cannot see the package, inspect the Simple API URL, selected devpi index, server logs, and credentials. The lab is not complete until the clean environment installs the expected version and the import/test succeeds.

### 7.5 Static Simple API index alternative

A static index can be hosted on controlled object storage or a web server. A minimal structure is:

```text
simple-root/
└── simple/
    └── acme-data-client/
        ├── index.html
        └── acme_data_client-2.4.1-py3-none-any.whl
```

`index.html` must link to the artifact with a URL relative to the project page, for example:

```html
<!doctype html>
<html><body>
  <a href="acme_data_client-2.4.1-py3-none-any.whl#sha256=REPLACE_WITH_REAL_SHA256">acme_data_client-2.4.1-py3-none-any.whl</a>
</body></html>
```

Replace the placeholder with the actual SHA-256 digest of the exact wheel. Generate it from the built artifact, for example `python -c "import hashlib,pathlib; p=pathlib.Path('dist/acme_data_client-2.4.1-py3-none-any.whl'); print(hashlib.sha256(p.read_bytes()).hexdigest())"`. Host the file and HTML so the project page resolves under `/simple/acme-data-client/`. Include the root project listing at `/simple/` if your clients/server require it. The static index has no upload API; publishing means updating the controlled storage and index files through a secured deployment pipeline. Add authentication/authorization at the hosting layer if private access is required. Validate with an actual clean client before relying on it.

## 8. Lockfiles, artifact integrity, and verification

### 8.1 What to verify

For each release and installation, record:

- Normalized distribution name and version.
- Intended registry/source and actual lockfile source.
- Artifact filename, SHA-256 digest, and size.
- Build commit, build workflow identity, build environment, and dependency lock used during build.
- SBOM and vulnerability/license scan results.
- Provenance/attestation identity and verification result, where supported.
- Publisher identity, upload time, approval/promotion record, and consumer inventory.

A lockfile is a resolution snapshot; it does not replace SBOM generation, vulnerability scanning, provenance verification, registry access controls, or testing. A lockfile can contain multiple platform-specific wheels and hashes. Review the exact lock format emitted by your pinned tool rather than relying on a manually fabricated example.

### 8.2 Reproducible installation checks

A useful CI sequence is:

```bash
uv lock --check
uv sync --locked
uv tree
uv run --locked python -m pytest
uv run --locked python -c "import importlib.metadata as m; print(m.version('acme-data-client'))"
```

Commands assume the project has pytest available and that the pinned uv version supports the options shown. For release CI, also inspect the wheel and sdist, test the built wheel in a fresh environment, generate an SBOM, scan dependencies, and verify the expected index host. Keep logs free of tokens and credentials.

### 8.3 Offline and air-gapped installs

For controlled offline deployment, download the complete dependency set and wheels in a connected staging environment, verify and record hashes, then transfer the wheelhouse through an approved channel. Example shape:

```bash
python -m pip download --python-version 3.12 --dest wheelhouse -r requirements.txt
python -m pip install --no-index --find-links wheelhouse --require-hashes -r requirements.txt
```

Use `pip download` for this operation: the `uv pip` interface does not provide a `download` subcommand in the uv CLI version checked for this audit. The requirements file must be fully pinned and contain valid hashes for every artifact; generate it using a documented workflow and test it against the target Python/platform. Cross-platform wheel selection and native dependencies need explicit attention. `--no-index` disables index access; `--find-links` tells pip where to find local artifacts. Air-gapped mode does not make unverified files safe—validate the bundle before transfer and verify hashes/signatures/attestations according to policy. Re-check the pinned tool's CLI before adapting this command to a future uv release.

### 8.4 Integrity, signatures, and provenance

- **Digest/hash:** detects mismatch against a trusted expected digest; the digest itself must come from a trusted channel.
- **Signature:** binds a signer identity to a signed statement or artifact, subject to key/identity trust and verification policy.
- **Provenance:** records how, where, and by which workflow an artifact was built. Verify expected repository, commit, workflow identity, and issuer—not just that some attestation exists.
- **SBOM:** inventories components and relationships; it is not proof that components are secure or that the SBOM matches the deployed artifact unless generated and tied to that artifact.

Prefer modern provenance/attestation workflows supported by the registry and CI provider. Require verification at promotion or deployment, not merely generation. Store the verification result and policy version for auditability.

## 9. Advanced enterprise controls and incident response

### 9.1 Access-control model

Apply least privilege to the registry, object store, CI identities, and cloud control plane. Use separate roles for read, upload, promote, delete/yank, and administer. Restrict who can modify upstreams and package namespace rules. Protect release workflows with branch/tag protections, reviewed changes, environment approvals, and short-lived identity. Log reads, uploads, deletions, promotions, permission changes, and upstream changes where supported.

### 9.2 Quarantine and vulnerability response

On ingest, validate metadata and file type, scan for known vulnerabilities and malware where available, check provenance, detect typosquatting/name collisions, and apply a cooldown policy for new upstream releases if the risk warrants it. A cooldown is a risk-reduction measure, not proof of safety; urgent security fixes may need a documented exception.

When a package is found vulnerable or compromised:

1. **Contain:** block new installs or promotion of the affected version; disable or revoke compromised publisher credentials; prevent the affected upstream from being fetched.
2. **Preserve evidence:** retain artifact digests, registry/audit logs, upload metadata, attestations, and relevant CI logs. Do not destroy evidence by immediately deleting all traces.
3. **Scope impact:** search lockfiles, SBOMs, deployment inventories, CI logs, and registry download logs for affected versions and consumers.
4. **Assess execution:** determine whether the package was only downloaded, installed, imported, built from source, or executed in a privileged workflow. Rotate credentials that may have been exposed.
5. **Remediate:** publish a corrected release, rebuild from a trusted commit/environment, and promote the verified artifact. Yank/block the bad version where supported, but do not assume yanking removes already-installed copies or every cache.
6. **Recover:** invalidate/purge caches safely, update lockfiles, redeploy, and verify running workloads.
7. **Learn:** document timeline, scope, root cause, control failures, and preventive actions; test that the policy blocks a repeat.

Never assume deleting a package is sufficient. It may remain in caches, wheelhouses, container layers, or deployed environments.

### 9.3 Availability, backup, and recovery

Define a registry SLO and operational owner. Track request latency/error rate, upstream failures, storage growth, cache hit rate, token failures, and upload/promotion errors. For self-hosted systems, back up metadata and artifacts consistently, protect backups from registry-admin credentials, encrypt them, and test restoration in an isolated environment. For managed registries, understand the provider's durability/availability guarantees and export/replicate artifacts if your recovery objectives require it.

Document recovery objectives:

- **RPO:** acceptable amount of package metadata/artifact history that could be lost.
- **RTO:** time to restore package consumption or publishing.
- **Degraded mode:** whether existing lockfiles and cached/wheelhouse artifacts allow critical builds during an outage.
- **Restore validation:** compare artifact hashes, verify metadata/permissions, and perform a clean install from the recovered endpoint.

For air-gapped or regulated environments, maintain signed/hashed snapshots of approved packages, a controlled transfer process, and an inventory tying each snapshot to its source and timestamp.

### 9.4 Organizational internal-packaging standard

A practical policy should define:

- Approved package sources and whether direct public egress is permitted.
- Package naming, ownership, visibility, license metadata, supported Python versions, and security contact.
- Allowed dependency ranges and versioning/deprecation rules.
- Required CI tests, built-artifact tests, SBOM, vulnerability/license checks, and provenance policy.
- Upload, quarantine, approval, promotion, immutability, yank, and retention rules.
- Credential lifetime, role separation, secret storage, audit log retention, and rotation/revocation process.
- Cache/mirror behavior, outage response, backup/recovery objectives, and restore-test cadence.
- Exception process with owner, rationale, expiration date, and compensating controls.

Keep the policy executable where possible: CI should reject unapproved registry hosts, missing lockfiles, unreviewed source changes, failed provenance checks, disallowed licenses, and high-risk vulnerabilities according to policy.

### 9.5 CI, containers, and mixed environments

Pin the uv version used by CI and developers. Inject read credentials only into the dependency-fetching step. For Docker, use BuildKit secret mounts rather than `ARG` or copied credential files; ensure the secret is not persisted in an image layer. Keep private index configuration non-secret and cache-safe, and ensure build logs don't reveal credentials. With mixed pip/uv/conda environments, document which tool owns resolution and locking; avoid installing the same dependency graph through multiple tools with inconsistent sources. For packages containing native extensions, validate platform tags and runtime system-library dependencies separately from registry trust.

## 10. Troubleshooting

| Symptom | Likely causes | Diagnostic steps | Safe remediation |
|---|---|---|---|
| `401 Unauthorized` | Missing/expired token, wrong username, credential not discovered | Confirm index name and environment variable suffix; check token scope/expiry; inspect redacted registry logs | Refresh a least-privilege token; don't embed it in URL or commit config |
| `403 Forbidden` | Authenticated identity lacks read permission, or provider uses 403 for a missing project | Check registry role and provider semantics; distinguish authorization from package absence | Grant only required read access or correct endpoint; do not blindly ignore all 403s |
| `404 Not Found` | Wrong `/simple` base, normalized project path, wrong repository, package not published | Open the project page directly; verify selected repository and project name | Fix URL or publish/promote the intended artifact; don't add public fallback as a shortcut |
| Internal package resolves from public source | No source mapping, unsafe multi-index policy, unapproved lock update | Inspect `uv.lock` source and `pyproject.toml`; review CLI/environment index overrides | Pin package to explicit index; enforce internal-name blocking in proxy; regenerate/review lock |
| Expected version is missing | Version not uploaded, yanked, incompatible `Requires-Python`/wheel tag, wrong channel | Inspect project page, metadata, interpreter/platform, yanked state | Publish/promote a compatible version or correct metadata after review |
| Stale version still appears | HTTP/CDN/client cache, stale mirror snapshot, registry metadata cache | Check cache headers, index sync time, uv cache and mirror freshness | Use documented invalidation/revalidation process; avoid deleting caches indiscriminately in production |
| Lock differs on clean machine | uv version mismatch, platform-specific artifacts, uncommitted lock update, source config differs | Compare uv versions, project config, lock diff, platform markers | Pin tool version; run locked sync; review and commit intentional lock changes |
| Hash mismatch | Artifact changed in place, corrupted download, wrong expected hash, compromised registry | Preserve artifact and logs; compare known digest and registry audit records | Stop installation/promotion, quarantine artifact, investigate; never bypass hash checks |
| Works on workstation, fails in CI | Global config or cached credentials, network/CA differences, missing secret, source config not checked in | Use clean runner, print redacted config, inspect trust store and DNS | Make source policy explicit in project/CI; configure CA correctly; inject scoped secret |
| `uv` doesn't find credentials | Index name/env suffix mismatch, credential provider disabled, URL host differs | Confirm `UV_INDEX_<NAME>_USERNAME/PASSWORD`, `.netrc`, host and auth mode | Fix env mapping or use approved credential provider; avoid putting credentials in TOML |
| Upload succeeds but install fails | Upload endpoint differs from Simple API URL, index not selected, package page not refreshed | Check provider upload logs, package page, and consumer source mapping | Configure the correct `/simple` endpoint; verify publication and metadata before retrying |

Do not troubleshoot by disabling TLS, using a broader admin token, switching to `unsafe-best-match`, or adding public fallback without understanding the source-selection failure.

## 11. Self-check answers and practical security checklist

### Self-check 1 — Explain a dependency-confusion attack end to end and two mitigations.

**Answer:** A project declares an internal distribution such as `acme-feature-kit`. The organization permits resolution from both an internal registry and a public index without binding the package to the trusted source. An attacker publishes a public distribution with the same normalized name and a higher version. The resolver may choose the attacker's artifact; installation/build/import can then execute malicious code in a privileged environment.

Two core mitigations are:

1. Use a single approved proxy/virtual index that blocks internal names from upstream resolution and enforces allow-list/ownership rules.
2. Explicitly map the internal package to a named uv index with `explicit = true`, then review the lockfile source. Also reserve public names where possible and verify provenance/hashes; these are defense-in-depth, not replacements for source control.

### Self-check 2 — Configure uv to resolve one package from an internal index only, and show the resulting lock entry.

**Answer:** Put the internal source in the project config and map the package to it:

```toml
[project]
name = "analytics-job"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["acme-data-client>=2.4,<3", "httpx>=0.27,<1"]

[tool.uv]
package = false

[[tool.uv.index]]
name = "internal"
url = "https://packages.example.com/simple"
explicit = true

[tool.uv.sources]
acme-data-client = { index = "internal" }
```

Then run `uv lock` and review the actual `uv.lock`. The package entry should identify the internal registry as its source, for example:

```toml
[[package]]
name = "acme-data-client"
version = "2.4.1"
source = { registry = "https://packages.example.com/simple" }
```

The real lock entry will also include actual artifact URLs/hashes and other metadata; do not paste the abbreviated example over the generated lockfile. Run `uv sync --locked` in a clean environment and confirm that the expected version imports from that environment. The source mapping controls resolution; the registry must still enforce access and upstream policy.

### Self-check 3 — Stand up devpi (or a static simple index), publish a package to it, and install from a clean venv.

**Answer / acceptance criteria:**

1. Build `acme-data-client` version `2.4.1` from the package project; test the built wheel in a clean environment.
2. Start a disposable devpi server on `127.0.0.1`, create a dedicated user/index, and upload the built artifacts using the current devpi CLI documented for the installed version. Alternatively, host the wheel and a PEP 503-compatible project page in a static index.
3. Configure a consumer project with a named internal index, `explicit = true`, and `acme-data-client = { index = "devpi-internal" }`.
4. Create a new virtual environment and run `uv lock`, `uv sync --locked`, an import smoke test, and a behavior assertion.
5. Inspect `uv.lock` and verify the source URL; inspect `acme_data_client.__file__` and confirm it points into the clean environment's `site-packages`.
6. Record the artifact digest and confirm that no credentials appear in the project file or lockfile.

Do not mark the task complete merely because upload succeeded. The clean consumer install, source verification, and import/test must pass.

### Practical security checklist

Use this as a release gate; adapt severity thresholds and evidence retention to organizational policy.

- [ ] Every internal distribution has an owner, security contact, supported Python versions, license metadata, and documented release policy.
- [ ] Internal names are normalized and checked for public-name collisions; public names are reserved where feasible.
- [ ] Consumption uses approved index URLs; internal packages are explicitly mapped or protected by a single policy-enforcing proxy.
- [ ] No production workflow uses unsafe multi-index best-match resolution for internal packages.
- [ ] Registry roles separate read, upload, promotion, deletion, and administration.
- [ ] Tokens are scoped, short-lived where supported, rotated, revocable, and injected via a secret manager/workload identity.
- [ ] No credentials are committed to project files, lockfiles, source code, images, logs, or artifacts.
- [ ] Builds are performed by controlled CI from protected commits; built artifacts are tested before publication.
- [ ] Releases are immutable or changes are auditable; promotion preserves the artifact digest.
- [ ] Lockfiles are reviewed for unexpected source/version/hash changes and installed with locked mode in CI.
- [ ] Artifact hashes are verified; provenance and signatures are verified against explicit identities/policy where supported.
- [ ] SBOM, vulnerability, license, and malware/name-confusion checks are part of release or ingest policy.
- [ ] Upstream allow-lists, quarantine/cooldown, cache invalidation, yanking, and retention policies are documented and tested.
- [ ] Registry audit logs, artifact inventory, and consumer/deployment inventory are available during an incident.
- [ ] Backup/restore or managed-registry recovery procedures are tested against defined RPO/RTO.
- [ ] CI and container builds do not leak tokens through arguments, image layers, cache exports, or logs.
- [ ] Offline/air-gapped wheelhouses are hashed, inventoried, and transferred through an approved process.
- [ ] Exceptions have an owner, expiration date, rationale, and compensating controls.

## 12. Authoritative references

Use the current documentation for the exact tool and registry version deployed. Provider-specific upload endpoints, identity integration, immutable-release semantics, and retention features differ.

1. [Python Packaging User Guide — Simple Repository API](https://packaging.python.org/en/latest/specifications/simple-repository-api/) — living specification and PEP 503/691 history.
2. [PEP 503 — Simple Repository API](https://peps.python.org/pep-0503/) — HTML project pages and normalized names.
3. [PEP 691 — JSON-based Simple API](https://peps.python.org/pep-0691/) — JSON content negotiation and representation.
4. [uv — Package indexes](https://docs.astral.sh/uv/concepts/indexes/) — named indexes, `explicit`, source mapping, index strategy, authentication variables, and cache controls.
5. [uv — HTTP credentials](https://docs.astral.sh/uv/concepts/authentication/http/) — `.netrc`, credential store, keyring providers, and credential persistence.
6. [uv — CLI reference](https://docs.astral.sh/uv/reference/cli/) — verify commands/options for the pinned uv release.
7. [devpi documentation](https://devpi.net/docs/devpi/devpi/stable/+doc/index.html) — self-hosted package index setup, users, indexes, and uploads.
8. [pip user guide — Package finding](https://pip.pypa.io/en/stable/cli/pip_install/#finding-packages) — pip index options and candidate selection.
9. [PyPA Trusted Publishing](https://docs.pypi.org/trusted-publishers/) — publishing identity model on supported services; do not assume every private registry supports it.
10. [PEP 740 — Index-hosted attestations](https://peps.python.org/pep-0740/) — provenance/attestation support in compatible indexes.
11. [CycloneDX Python tooling](https://cyclonedx-bom-tool.readthedocs.io/) and [SPDX](https://spdx.dev/) — SBOM formats and tooling.

---

**Operational rule of thumb:** Pin the source for internal packages, centralize public-package policy, lock and review the graph, verify the artifact, and make the registry's permissions and recovery behavior part of the software supply-chain design.
