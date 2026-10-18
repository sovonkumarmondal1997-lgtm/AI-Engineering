# Trusted Publishing and Signed Releases

**Stage 1 — Programming & Computational Thinking · Module 18 · Lesson 06**  
**Target baseline:** Python 3.12+, `uv`, Git, GitHub Actions, PyPI/TestPyPI  
**Running example:** `tinytools`

> This is a learning guide and a security design pattern, not a claim that any workflow below has run or that a real PyPI project has been configured. Publishing requires access to the repository, the PyPI/TestPyPI project, and their settings. Pin third-party GitHub Actions to verified full commit SHAs before adopting the example for production.

## Learning objectives

By the end, you should be able to:

- Explain the threats posed by leaked API tokens, compromised maintainers, and malicious releases.
- Describe how OpenID Connect (OIDC) lets a configured CI identity obtain short-lived publishing credentials without storing a long-lived PyPI upload token.
- Configure separate Trusted Publishers for TestPyPI and PyPI, and design a workflow with distinct build and publish jobs.
- Distinguish authentication, artifact integrity, digital signatures, publisher identity, and build provenance.
- Explain PyPI attestations and PEP 740, Sigstore, Fulcio, Rekor, and SLSA provenance without overclaiming their guarantees.
- Threat-model release automation and apply least privilege, environment protection, dependency controls, and incident response.

## Prerequisites

You should already understand `pyproject.toml`, building wheels and source distributions (`sdist`), versioning, clean-environment testing, Git tags, GitHub Actions basics, hashes, and dependency auditing. Review the earlier Module 18 lessons on building artifacts and publishing to TestPyPI/PyPI, plus secure coding topics on tokens, secrets, and `pip-audit`.

## 1. Threat model and vocabulary

A Python release is a chain of trust: source code → build environment → wheel/sdist → publisher identity → package index → consumer installation. A control at one point does not automatically secure the others.

### Threats

- **Leaked long-lived API token:** a copied token, log line, compromised workstation, or exposed CI secret can permit unauthorized uploads for as long as the token remains valid and authorized.
- **Compromised maintainer or account:** an attacker who can change repository settings, workflow files, release tags, or PyPI ownership may be able to publish a malicious release even without stealing a token.
- **Malicious or compromised dependency/action:** build-time code runs with the permissions available to the job. It may alter output, steal accessible secrets, or abuse a token.
- **Malicious release path:** an unprotected branch/tag, unsafe workflow trigger, poisoned cache, or compromised self-hosted runner can cause unreviewed code to reach a release job.
- **Misleading integrity evidence:** a hash proves that two byte sequences match; it does not prove that the bytes are benign. A signature identifies a signer under a trust policy; it does not prove the signed code is safe.

### Security vocabulary

| Term | What it answers | What it does not answer |
|---|---|---|
| Authentication / identity | Who or what is requesting an operation? | Whether the requested artifact is safe. |
| Authorization | Is that identity allowed to perform this operation on this project? | Whether its build inputs were trustworthy. |
| Hash / digest | Are these bytes identical to bytes with this trusted digest? | Who produced the bytes or whether they are malicious. |
| Digital signature | Does the signature verify for this artifact and a trusted signing identity/key? | Whether the signer or build process was uncompromised. |
| Attestation | A signed statement binds claims to an artifact digest. | Whether every claim is complete or true unless its issuer and process are trusted. |
| Provenance | Evidence describing source, builder, inputs, and build process. | A guarantee that source code is safe or that all dependencies were benign. |
| Reproducible build | Independent builds can produce matching outputs under specified conditions. | That the source itself is non-malicious. |

A useful rule: **identity, integrity, provenance, and code safety are related but distinct properties.**

## 2. OIDC and PyPI Trusted Publishing

### The mental model

Traditional publishing often stores a PyPI API token in CI secrets. Trusted Publishing replaces that long-lived upload secret with a federated identity exchange between a supported CI provider and PyPI.

```text
Protected source/tag + trusted workflow
                 |
                 v
       GitHub Actions job identity
                 |
     job has id-token: write permission
                 |
                 v
       GitHub issues short-lived OIDC token
                 |
                 v
 PyPI checks issuer, claims, and configured publisher
 (owner/repository/workflow/environment identity)
                 |
                 v
 PyPI issues a short-lived upload credential
                 |
                 v
       Upload distributions to the project
                 |
                 v
 Optional/automatic attestations associated with files
```

The OIDC token is not itself the package upload token. It is an identity assertion from the CI provider. PyPI validates it against the Trusted Publisher configuration and exchanges it for a short-lived credential. The official PyPA publishing action handles this exchange; ordinary users should use that supported interface rather than reimplementing provider-specific token-exchange details.

### What must be configured

For an existing project, open the project’s publishing settings on the target index and add a Trusted Publisher. For GitHub Actions, specify the exact:

- GitHub owner or organization;
- repository name;
- workflow filename (for example, `.github/workflows/release.yml`);
- GitHub environment name, if the publisher is configured to use one (for example, `testpypi` or `pypi`).

These values are part of the identity boundary. A typo, renamed workflow, wrong repository, or mismatched environment can cause the exchange to fail. Conversely, a workflow that matches the configured identity should be treated like access to a publishing credential.

**TestPyPI and PyPI are separate services.** Configure a separate Trusted Publisher on each service, and test against TestPyPI first. Do not assume a TestPyPI publisher configuration authorizes PyPI publication.

### Why short-lived credentials help—and what remains risky

Trusted Publishing avoids keeping a manually generated, long-lived PyPI upload token in CI. It narrows the lifetime of the upload credential and ties issuance to an external CI identity and project configuration.

It does **not** make the workflow inherently safe. A compromised workflow, maintainer, dependency, action, or runner that can obtain the expected OIDC identity may still publish malicious artifacts. PyPI’s security guidance explicitly recommends treating a Trusted Publisher as if it were an API token: only workflows that you would trust with a publishing token should be able to invoke it.

## 3. Design a secure build/publish workflow

The roadmap’s basic pattern is a tag-triggered release workflow with a build job and a separate publish job. The important boundary is that **the build job does not need `id-token: write` or PyPI publishing authority**. The publish job downloads the build output and obtains the OIDC credential only when publishing.

### Repository assumptions

- The package metadata and source live at the repository root.
- `uv build` creates wheel and sdist files under `dist/`.
- A release tag uses the `v*` naming convention, such as `v1.2.0rc1`.
- A GitHub environment named `testpypi` is configured with required reviewers or other protection as appropriate.
- TestPyPI has a Trusted Publisher configured for this exact repository, workflow, and environment.
- The action references below are readable version tags for teaching. Before production use, resolve each third-party action to a reviewed, full-length commit SHA and keep an update process for those pins.

### Conceptual workflow for TestPyPI

Save as `.github/workflows/release-testpypi.yml`. This is a teaching example; it deliberately publishes only to TestPyPI. It must be adapted and reviewed for the repository’s branch/tag policy, dependency model, and action pinning policy.

```yaml
name: TestPyPI release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: read

jobs:
  build:
    name: Build and validate distributions
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Check out source
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: false

      - name: Build wheel and sdist
        run: uv build

      - name: Validate distribution metadata
        run: uvx twine check --strict dist/*

      - name: Record artifact digests in the workflow log
        shell: bash
        run: sha256sum dist/*

      - name: Upload distributions
        uses: actions/upload-artifact@v4
        with:
          name: python-distributions
          path: dist/*
          if-no-files-found: error
          retention-days: 7

  publish-testpypi:
    name: Publish to TestPyPI
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: testpypi
      url: https://test.pypi.org/p/tinytools
    permissions:
      id-token: write
    steps:
      - name: Download the built distributions
        uses: actions/download-artifact@v4
        with:
          name: python-distributions
          path: dist

      - name: Publish to TestPyPI with Trusted Publishing
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
          packages-dir: dist/
```

#### Review the example before using it

- **Triggers:** `push.tags` allows any matching tag to start the workflow. A `v*` pattern is not, by itself, a security boundary. Restrict who may create or update release tags, protect the release branch, and review the tag’s commit. GitHub tag rulesets and environment protections should match your release policy. This example intentionally has no manual-dispatch trigger.
- **Permissions:** repository defaults are reduced to `contents: read`. Only the publish job has `id-token: write`. Do not grant that permission to all jobs. `id-token: write` allows requesting an OIDC token; it is not itself a write permission to repository contents.
- **Job separation:** the build job runs package/build code without publishing authority. The publish job receives the exact output artifact and has only the identity permission needed for OIDC. Separation reduces exposure but does not make a malicious artifact harmless; the publish job still uploads what it receives.
- **Artifact transfer:** the build job transfers only the distribution files through a named Actions artifact. The publishing job downloads them into `dist/`; the publishing action does not rebuild them. Keep the artifact name, paths, and job dependency consistent. Review artifact provenance and retention settings for your threat model.
- **Digest recording:** `sha256sum dist/*` records hashes in the build log. Those hashes are generated by the same build job and are not an independent signature or trust anchor. Consumers should obtain an expected digest from a trusted channel or verify signed provenance.
- **Environment:** the `testpypi` environment name must match the configured Trusted Publisher if that configuration includes an environment. Configure required reviewers, deployment branch/tag restrictions, and environment access in GitHub settings. YAML alone does not enable those protections.
- **Action pinning:** `@v4`, `@v5`, and `@release/v1` are tags and can move. For a hardened release workflow, replace them with full commit SHAs verified against the upstream repositories; comment the corresponding version and maintain a deliberate update process.
- **Account state:** the workflow will not work until the TestPyPI project/publisher and GitHub environment are configured. It has not been executed merely because it appears in this lesson.

For a production PyPI workflow, use a separate workflow or a carefully gated production job with a distinct `pypi` GitHub environment and a Trusted Publisher configured on **PyPI**. Avoid a casual boolean input that lets any workflow run choose production. A protected environment with required reviewers is a useful approval boundary.

### Build once, publish the same artifact

Prefer building and validating once, then publishing the transferred artifact. If the publish job rebuilds from source, the bytes it uploads may differ from the bytes tested or reviewed in the build job. Stronger pipelines can additionally attest the build artifact and verify that the release tag and source commit are the expected ones.

A build/publish split is not sufficient if an attacker can alter the workflow or artifact transfer. Protect workflow files, pin actions, restrict tag creation, minimize job permissions, and review external actions and build dependencies.

## 4. GitHub release protections

### Recommended baseline

1. **Protected branches:** require review and CI checks for the branch from which releases are cut. Restrict who can modify `.github/workflows/` and build configuration.
2. **Tag protection:** use rulesets to restrict creation, update, and deletion of release tags. Treat a release tag as a privileged input, not merely a string matching `v*`.
3. **Environment protection:** use a dedicated environment such as `testpypi` or `pypi`; configure required reviewers and deployment restrictions in GitHub settings. Ensure the configured publisher identity and workflow refer to the same environment name.
4. **Least privilege:** set workflow/job permissions explicitly. Grant `id-token: write` only to the job that must exchange identity with PyPI. Do not give publishing authority to test jobs.
5. **Pin actions:** full-length commit SHA pinning is the strongest immutable-reference option for GitHub Actions. Verify the SHA belongs to the expected upstream repository; monitor updates and review changes before moving pins.
6. **Untrusted contributions:** run pull-request tests without publishing permissions or secrets. Never execute untrusted pull-request code in a privileged context. `pull_request_target` is especially dangerous when a workflow checks out or executes attacker-controlled code because it can run with base-repository privileges.
7. **Runner trust:** prefer fresh hosted runners for publishing. Persistent self-hosted runners may retain files, credentials, processes, or caches between jobs; isolate and harden them if they are unavoidable.
8. **Cache safety:** avoid sharing writable caches between untrusted PR builds and privileged release jobs. A cache hit is not proof of integrity; scope caches carefully and validate critical inputs.
9. **Runner and network hardening:** where appropriate, consider a maintained control such as `step-security/harden-runner` pinned to a verified full commit SHA, with an explicitly reviewed egress policy. This can improve visibility or restrict unexpected network access, but it is not a substitute for least privilege, action pinning, clean runners, and review of code that executes in the job.

### Maintainer account security

Enable PyPI account two-factor authentication and prefer hardware security keys (WebAuthn/FIDO) where supported. Store recovery codes securely offline or in an approved secrets manager; test recovery procedures before an emergency. Maintain multiple trusted maintainers so a single lost account does not permanently block releases, but grant each person only the roles they need. Review maintainers and Trusted Publisher settings periodically.

## 5. PyPI attestations and PEP 740

PyPI supports digital attestations under **PEP 740**. An attestation is a signed statement bound to a distribution digest; it is evidence to verify under an explicit trust policy, not a generic security certificate. When used with supported Trusted Publishing, the official `pypa/gh-action-pypi-publish` action generates and uploads attestations by default. Its default PyPI Publish attestation records that the distribution was uploaded through a configured Trusted Publisher. **Do not infer that a separate SLSA build-provenance attestation exists merely because this action published the package or because a PyPI Publish attestation is present.** SLSA provenance is a distinct predicate with claims about the build process and must be generated and verified through a workflow/tooling path that actually supplies it. Confirm current behavior in the official documentation when adopting or upgrading the action.

Two concepts are particularly relevant:

- **PyPI Publish attestation:** evidence that a particular distribution was uploaded via a specific Trusted Publisher identity rather than a manually held API token. It communicates publishing intent/identity; it does not by itself prove which source commit produced the bytes, or that the source is safe.
- **SLSA provenance attestation:** structured claims about the build definition, builder, inputs/dependencies, and output artifact. The artifact should be identified by digest so the claim is bound to specific bytes. A provenance generator, its permissions, and its isolation must be evaluated separately; do not claim a SLSA level without checking the applicable specification and all required platform controls.

### What an attestation can and cannot prove

An attestation can make it possible to ask: “Does this exact wheel digest have evidence associated with the expected workflow identity and build process?” A consumer must still verify the attestation’s signature, issuer, subject digest, predicate, and expected repository/workflow identity according to policy.

An attestation is **not** a security audit, a guarantee that dependencies were benign, or proof that the source code is non-malicious. A validly attested malicious release is still malicious. A provenance claim is only as trustworthy as the builder, the identities, and the evidence-generation process behind it.

### How to inspect and verify evidence

- Open the project/release file on PyPI and inspect the attestations shown for that exact distribution, where available. A page display is useful evidence to inspect, but for a security decision verify the attestation cryptographically and constrain the expected identity.
- For production PyPI, the current `pypi-attestations` CLI documents verification against the index. In a disposable environment, install the tool using its official instructions and replace the example repository and filename with the expected values:

  ```bash
  python -m pip install pypi-attestations
  pypi-attestations verify pypi \
    --repository https://github.com/OWNER/REPOSITORY \
    pypi:tinytools-1.2.0-py3-none-any.whl
  ```

  The filename must exactly match a published distribution. This command verifies the artifact/provenance available from production PyPI and checks the repository identity; review the CLI's current documentation because the CLI is described as an evolving/experimental interface. For higher-assurance policy, also inspect the exact workflow identity and any required predicate/claims rather than accepting any attestation from the repository.
- **Do not assume that the production-PyPI verification command works against TestPyPI.** Current `pypi-attestations` CLI documentation states that `verify pypi` targets production PyPI and TestPyPI verification is not supported by that CLI release. For a TestPyPI exercise, inspect whatever evidence the service exposes and record the limitation; do not claim cryptographic CLI verification unless the selected tool explicitly supports that index and you actually ran it.
- Check that the verified subject digest matches the exact wheel or sdist you intend to install, and that the trusted identity corresponds to the expected repository/workflow and OIDC issuer. If the available attestation only establishes the publishing identity, do not describe it as build provenance.
- Do not infer production PyPI state from a TestPyPI test, or infer that an attestation exists from a successful upload alone.

## 6. Sigstore: keyless signing, Fulcio, and Rekor

Sigstore provides a signing ecosystem designed to reduce the need to distribute and protect long-lived private signing keys in some CI workflows.

- **Keyless signing:** the signer uses an OIDC identity to obtain a short-lived signing certificate rather than using a long-lived private key distributed to CI. The identity and certificate policy must still be checked by the verifier.
- **Fulcio:** the Sigstore certificate authority that issues short-lived signing certificates based on an authenticated identity.
- **Rekor:** a transparency log that records signed metadata about signing events, enabling later auditing and helping detect inconsistent or suspicious records.
- **Bundle/verification:** a signature or Sigstore bundle carries evidence needed for verification. Verification should constrain the expected signer identity and OIDC issuer, not merely report that some signature is cryptographically valid.

### Manual example: sign and verify a file

Install the Sigstore Python client in a dedicated environment using the official instructions. The exact CLI options depend on the client version and the identity context; consult its current documentation. A typical local file-signing pattern is:

```bash
sigstore sign dist/tinytools-1.2.0-py3-none-any.whl
sigstore verify identity dist/tinytools-1.2.0-py3-none-any.whl \
  --cert-identity 'EXPECTED_SIGNER_IDENTITY' \
  --cert-oidc-issuer 'EXPECTED_OIDC_ISSUER'
```

This is illustrative, not an executed signing operation. The identity string and issuer must match the real expected signer and CI provider. Do not use a placeholder identity in production. Keep the generated signature/bundle with the artifact and make verification instructions available to consumers. PyPI attestations produced through Trusted Publishing and a separately run `sigstore sign` operation are related but not interchangeable processes; choose the mechanism that fits your distribution and consumer-verification model.

## 7. SLSA, provenance, and reproducible builds

SLSA is a framework for progressively strengthening software supply-chain guarantees. Its build track describes provenance quality and the trustworthiness of the build platform. At a high level:

- **Build L1:** provenance exists and describes the build at a basic level.
- **Build L2:** provenance is generated by a hosted build service and signed under the level’s requirements.
- **Build L3:** the build platform provides stronger isolation and protection against tampering during the build.

Do not claim a level just because a workflow uploads an attestation. Assess the exact SLSA version, track, platform guarantees, build type, and requirements. Levels and specification details can evolve; consult the current SLSA specification.

### Reproducibility and comparison

A reproducible build aims to produce identical output from the same inputs under documented conditions. To evaluate it:

1. Record the exact source commit/tag, Python/toolchain versions, build backend and dependencies, environment, and build command.
2. Build from a clean checkout in a second isolated environment.
3. Compare artifact hashes. Matching hashes establish byte identity for those outputs.
4. If they differ, use `diffoscope` to inspect archive contents and metadata, timestamps, generated files, paths, and build-environment differences.
5. Document non-reproducible fields and decide whether they can be eliminated or normalized.

Reproducibility improves auditability, but matching artifacts do not prove that the source was benign. A compromised source commit can be reproducibly malicious.

## 8. Dependency integrity and build isolation

Build systems and dependencies are executable inputs. A malicious dependency can run during installation or build, alter artifacts, exfiltrate accessible secrets, or tamper with caches.

- Commit and review a lockfile where your workflow uses one. Pin build requirements where practical and update them deliberately.
- For pip requirements files, `--require-hashes` can enforce expected hashes for all resolved requirements when used with a fully pinned, hash-complete requirements set. It is not a general flag that can safely be added to any arbitrary requirements file.
- Use `pip-audit` or an equivalent tool to identify known vulnerabilities in dependencies. It does not detect every malicious package or unknown vulnerability.
- Prefer known, reviewed package sources and explicit index/mirror policy. Avoid mixing public and private indexes in a way that allows a public package with the same normalized name to supersede an internal dependency (dependency confusion).
- Keep build and publish jobs separate; never expose publishing OIDC permissions to code that does not need them.
- Treat build caches as optimization, not trust anchors. Avoid cache sharing across trust boundaries and invalidate caches when policy requires it.

Example checks in a local clean environment (adapt the dependency setup to the project):

```bash
uv lock --check
uv run --group dev pytest
uv run pip-audit
uv build
uvx twine check --strict dist/*
sha256sum dist/*
```

These commands are examples; they only test the controls actually configured in your project. They do not independently establish provenance or certify a release.

## 9. Additional signing and SBOM practices

- **Git commits/tags:** `git commit -S -m "release preparation"` can sign a commit, and `git tag -s v1.2.0` can create a signed annotated tag when a signing key is configured. Verify with `git verify-commit <commit>` and `git verify-tag v1.2.0`, and establish trust in the corresponding key/identity. Signed commits/tags help establish who signed Git objects; they do not prove the CI built the published wheel from that tag.
- **Container images:** tools such as `cosign` can sign container image digests and attach attestations. Sign and verify immutable digests, not only mutable tags like `latest`.
- **SBOMs:** generate a Software Bill of Materials (SBOM) for relevant artifacts, record tool/version and inputs, and consider attaching a signed attestation that binds the SBOM to the artifact digest. An SBOM is an inventory, not proof that all dependencies are safe or that the inventory is complete.
- **Commit-to-artifact linkage:** a strong release policy verifies that the published artifact digest is linked through trusted provenance to the intended source commit and build workflow.

## 10. STRIDE threat-modeling exercise

Use STRIDE to reason about threats in a release workflow. The table is a starting point; adapt it to the actual repository and CI provider.

| STRIDE category | Example release threat | Concrete mitigation |
|---|---|---|
| **Spoofing** | An unexpected repository/workflow identity attempts to publish. | Configure the exact Trusted Publisher owner, repository, workflow, and environment; verify attestation identity and issuer. |
| **Tampering** | An attacker changes a tag, workflow, or build artifact after review. | Protect branches/tags, require reviews, transfer the exact build artifact, record digests, and verify provenance. |
| **Repudiation** | A team cannot establish who approved or initiated a release. | Retain workflow logs, use protected environments with reviewer approvals, record release metadata, and audit publisher changes. |
| **Information disclosure** | A malicious build dependency reads a token or secret from its job. | Keep publish credentials out of build jobs, use OIDC only in the publish job, avoid unnecessary secrets, and restrict network/runner access where feasible. |
| **Denial of service** | A compromised account or malicious release blocks or disrupts users. | Use multiple maintainers, recovery procedures, monitoring, yank/remediation guidance, backups of release metadata, and a rehearsed incident plan. |
| **Elevation of privilege** | A test/build/PR workflow gains publishing authority, or a contributor changes a trusted workflow or release environment to publish without the intended approval. | Keep OIDC permission only on a minimal publish job; protect workflow files, tags, environments, and reviewer policy; do not execute untrusted code in privileged contexts; audit publisher and repository permissions. |

### Required exercise: choose five mitigations

For your own workflow, select and justify at least five concrete controls. A strong baseline is:

1. Protect the release branch and restrict tag creation/update/deletion.
2. Require approval through a protected GitHub environment before production publishing.
3. Grant `id-token: write` only to the publish job.
4. Pin all third-party actions to reviewed full commit SHAs and maintain an update process.
5. Build in an isolated job without publishing credentials; transfer and publish the same artifact.

Also assess dependencies, cache scope, `pull_request_target`, self-hosted runner persistence, maintainer recovery, and the verification consumers will perform. Record residual risks and the person responsible for each control.

## 11. Incident response

Treat a suspected compromise as an incident; preserve evidence and coordinate with PyPI/GitHub support where needed.

### If a release or workflow is compromised

1. **Contain:** pause releases, disable or remove the affected Trusted Publisher configuration if needed, revoke any remaining API tokens, restrict compromised maintainer access, and secure repository/organization accounts.
2. **Preserve evidence:** record affected versions and file hashes, release/tag commit IDs, workflow runs, audit logs, publisher configuration changes, and the timeline. Do not destroy evidence by force-pushing or deleting logs.
3. **Assess scope:** identify affected wheels/sdists, dependencies, tags, GitHub releases, and downstream consumers. Compare artifact digests and attestations against known-good evidence.
4. **Use index controls carefully:** yank affected versions where appropriate and supported, following the index’s current policy. Yanking discourages new resolution but does not remove files from existing environments or guarantee that all installers avoid the version. Do not assume a yank reverses installations. Coordinate removal requests with the index if the situation warrants it.
5. **Correct:** prepare a reviewed fix and publish a new version rather than attempting to overwrite an immutable release. Communicate clear upgrade/remediation instructions.
6. **Notify:** publish an advisory through appropriate channels such as GitHub Security Advisories and relevant ecosystem databases when warranted; notify downstream maintainers and affected users with facts and mitigations.
7. **Recover:** rotate credentials, repair branch/tag/environment protections, review maintainers and actions, invalidate risky caches, and verify the new trusted publisher identity and artifact evidence.
8. **Learn:** conduct a blameless postmortem documenting root cause, impact, detection gaps, action owners, and due dates.

### If an API token leaks

Revoke it immediately in the relevant index account/project settings; do not rely only on deleting it from the current commit. Search logs, workflow artifacts, shell history, package registries, and repository history for exposure. If the token may have been used, inspect release history and access logs where available. Remove it from CI secrets and migrate to Trusted Publishing if supported. Treat a leaked token as compromised even if logs show no obvious use.

### If a maintainer account or project is taken over

Secure the account and recovery channels, revoke sessions/tokens where supported, review ownership and Trusted Publisher settings, contact PyPI/GitHub support through official channels, and inspect project releases and configuration changes. Coordinate communication so users receive a consistent, factual response. A workflow that is correctly configured today can become unsafe if its repository or environment controls are later changed.

## 12. Policy documents and maintainer operations

A trustworthy release process needs human procedures as well as CI configuration.

- **`SECURITY.md`:** publish supported reporting channels, response expectations, and scope. Do not put secrets or sensitive incident details in a public issue.
- **Release procedure:** document who reviews releases, how tags are created, which tests run, which environment approves publishing, how to verify artifacts/attestations, and how to respond to failures.
- **Maintainer roles:** use least privilege for repository, package index, organization, and environment roles. Review membership periodically and remove access promptly when responsibilities change.
- **Bus factor:** have at least two trusted maintainers able to recover access, understand the release workflow, and rotate credentials. Store recovery instructions securely and test them.
- **Support policy:** state supported Python versions, vulnerability-reporting policy, issue triage expectations, deprecation windows, and sunset plans. Document how maintainership or project ownership is handed off.

## 13. Ecosystem comparison

These ecosystems have related but different mechanisms. Do not assume an assurance from one registry transfers to another.

| Ecosystem | Common supply-chain mechanisms | Important distinction |
|---|---|---|
| **Python / PyPI** | Trusted Publishing via OIDC; PEP 740 attestations; supported provenance predicates; project/index-level ownership and release files. | Trusted Publishing authenticates the publishing workflow. Attestations bind claims to distribution digests, but consumers must verify expected identity and claims. |
| **npm** | Provenance attestations can link packages to source repositories and CI workflows; publishing supports granular access tokens and trusted publishing features in supported contexts. | npm’s provenance format, identity model, and package lifecycle differ from PyPI; verify npm-specific guidance and policy. |
| **Maven Central** | Artifact signing (historically PGP-based workflows) and repository publication requirements; build metadata/provenance practices vary by project. | A signature on a Maven artifact is not automatically equivalent to a PyPI Trusted Publisher attestation. Verify the signer and repository-specific rules. |
| **Go** | The public checksum database (`sum.golang.org`) and module proxy ecosystem provide transparency and integrity checks for module versions. | A checksum database records module content checksums; it is not the same as a CI OIDC publishing exchange or a general build-provenance attestation. |

For cross-ecosystem comparisons, use current official documentation because supported features, terminology, and policy evolve.

## 14. Hands-on lab: TestPyPI Trusted Publishing

### Goal

Build a `tinytools` distribution, publish a pre-release to TestPyPI from a protected CI workflow using OIDC, then inspect and verify available attestation evidence.

### Steps

1. **Prepare source:** ensure `pyproject.toml` contains valid package metadata and a PEP 440 pre-release version, such as `1.2.0rc1`. Confirm tests pass locally and build both wheel and sdist.
2. **Validate locally:** run `uv build`, `uvx twine check --strict dist/*`, and install the built wheel into a fresh virtual environment. Run a small import/CLI smoke test.
3. **Protect GitHub:** protect the release branch; configure a release tag ruleset; add a `testpypi` environment with reviewer approval or other appropriate restrictions. Review who can modify the workflow.
4. **Configure TestPyPI:** sign in to TestPyPI and add a Trusted Publisher for the exact GitHub owner, repository, workflow filename, and environment `testpypi`. Do not reuse the PyPI project’s settings; TestPyPI is separate.
5. **Review workflow security:** keep `id-token: write` only on the publish job; ensure build and publish are separate; pin third-party actions to verified full commit SHAs before production adoption; ensure no untrusted PR workflow can invoke the publisher.
6. **Commit and tag:** merge reviewed source, then create the agreed pre-release tag (for example, `v1.2.0rc1`) only after verifying it points to the intended commit. If the example includes manual dispatch, restrict its use and ensure the correct tag/ref is checked.
7. **Run CI:** inspect build logs, test/metadata validation results, artifact transfer, environment approval, and publish logs. A successful local build is not evidence that TestPyPI publication succeeded.
8. **Verify the index:** open the TestPyPI project page, confirm the expected version and files, and inspect any attestation evidence the service exposes. Compare the artifact digest with recorded build evidence where available. Record precisely what you verified. Do not state that the current `pypi-attestations verify pypi` command verified TestPyPI: that CLI command targets production PyPI, and TestPyPI verification support may differ by tool/version.
9. **Install cleanly:** create a new virtual environment and install the exact pre-release from TestPyPI. Use a safe index strategy; do not blindly add `--extra-index-url` alongside PyPI when dependencies could share names. Prefer a dedicated test environment, explicit primary index strategy, and trusted dependency sources. For a package with dependencies, install dependencies from an intentional, reviewed source rather than letting an untrusted index compete by package name.
10. **Record a runbook:** include commit/tag, package version, build tool versions, workflow run URL, artifact filenames and SHA-256 digests, TestPyPI project URL, attestation verification result, install/smoke-test result, approvals, and unresolved risks. Never include credentials or OIDC tokens.
11. **Production readiness review:** only after TestPyPI validation, configure a separate PyPI Trusted Publisher and `pypi` environment. Require explicit approval and review the exact artifact and version before the first production publication.

### Safe installation note

TestPyPI may not contain all dependencies your package needs. A common pattern using `--extra-index-url` can create dependency-confusion risk because pip considers candidates from configured indexes together. Avoid using a secondary index as if it were a strict fallback. For a no-dependency smoke test, install the artifact in a fresh environment with dependency installation disabled and install only trusted test dependencies separately. For dependency testing, use a deliberate index/mirror configuration and verify where every dependency resolves from.

### Acceptance criteria

- [ ] Local build produces the expected wheel and sdist; `twine check --strict` succeeds.
- [ ] The release workflow has a build job without `id-token: write` and a separate publish job with only the required OIDC permission.
- [ ] TestPyPI publisher settings exactly match the intended repository/workflow/environment.
- [ ] Branch/tag/environment controls are documented and configured in GitHub settings, not assumed from YAML alone.
- [ ] The workflow run and uploaded version are confirmed in the actual TestPyPI UI/API.
- [ ] A clean environment installs the intended pre-release and passes a smoke test.
- [ ] Artifact digests and available attestation evidence are recorded and interpreted correctly; TestPyPI evidence is not described as cryptographically verified unless a supported verification method was actually used.
- [ ] No token or other secret is committed, printed, or included in the runbook.
- [ ] The runbook clearly distinguishes verified results from checks that were unavailable or not performed.

## 15. Troubleshooting

| Symptom | Likely cause | Checks and remedy |
|---|---|---|
| OIDC exchange or publishing fails | Publisher identity mismatch, wrong index, missing `id-token: write`, unsupported provider configuration, or environment mismatch. | Compare exact owner/repo/workflow/environment settings; verify the job has the required permission; ensure the action targets TestPyPI or PyPI as intended. Never add a token as a shortcut without reviewing the failure. |
| `id-token` request denied | The job lacks OIDC permission or the trigger context cannot request the expected identity. | Check workflow/job permissions and trigger. Do not grant the permission to every job. Avoid privileged execution of untrusted PR code. |
| Publisher is not recognized | The Trusted Publisher is configured on the wrong service/project or identity fields differ. | TestPyPI and PyPI settings are separate. Re-check exact workflow filename and environment. |
| Publish job has no files | Artifact name/path mismatch or build job did not upload output. | Confirm `needs: build`, upload/download artifact names, and that `dist/` contains wheel and sdist files. Keep artifact paths consistent. |
| Existing version/file is rejected | Index release files are immutable or that filename/version already exists. | Do not attempt to replace a published file. Fix source and publish a new PEP 440 version. Avoid `--skip-existing` as a blanket workaround that hides a wrong artifact. |
| Attestation is missing | Trusted Publishing was not used, action/configuration differs, or the index/tooling does not expose the expected evidence. | Consult current PyPI attestation documentation and inspect the exact file. Do not infer provenance merely from a successful upload. |
| Signature verifies but identity is unexpected | Verification checked cryptographic validity but not the intended identity policy. | Verify expected certificate identity, OIDC issuer, subject digest, and predicate; reject evidence from an untrusted signer. |
| Rebuild hashes differ | Non-deterministic metadata, timestamps, environment differences, dependency drift, or generated files. | Record build inputs, rebuild in a clean environment, inspect with `diffoscope`, and document or remove non-determinism. |
| PR workflow could reach publish steps | Trigger or job conditions are too broad; privileged context is used unsafely. | Remove publishing permissions from PR jobs, protect release environments/tags, and never execute untrusted code in privileged `pull_request_target` flows. |

## 16. Self-checks with answers

### 1. What does the OIDC exchange establish for PyPI, and which long-lived publishing secret can it eliminate?

It lets PyPI validate a short-lived identity assertion from the configured CI provider against the Trusted Publisher’s expected issuer and identity claims (such as repository, workflow, and configured environment), then issue a short-lived upload credential. It can eliminate the need to store a manually generated, long-lived PyPI API upload token in that CI workflow. It does not eliminate all secrets or risks, and a compromised workflow that is authorized to publish can still abuse its identity.

### 2. Why separate the build job from the publish job?

Build steps execute project code and dependencies, which are broader attack surfaces. They generally need read access to source and package/build dependencies, not publishing identity. A separate publish job can receive a reviewed/transferred artifact and request OIDC only at the point of upload. This reduces credential exposure and blast radius. It is not a complete defense if the artifact, workflow, action, or runner is compromised; artifact identity and workflow integrity still need controls.

### 3. How do you configure TestPyPI Trusted Publishing, publish a pre-release through CI, and verify available attestation evidence?

Set a PEP 440 pre-release version in package metadata, build and validate locally, protect the release branch/tag and GitHub `testpypi` environment, and configure TestPyPI’s Trusted Publisher with the exact owner, repository, workflow file, and environment name. Commit reviewed code, create the intended pre-release tag, and run the tag-triggered workflow. Confirm the build and transfer steps, approve the environment if required, and verify the publishing job targets `https://test.pypi.org/legacy/`. On TestPyPI, confirm the uploaded version and files. Inspect available attestations using the current official verification guidance, validate the expected identity/issuer and predicate, and confirm the attested subject digest matches the exact downloaded artifact. Install that artifact in a clean environment and record results. A successful workflow run or a visible attestation alone is not equivalent to verifying every provenance claim.

## 17. Release-security checklist

### Source and build

- [ ] Source commit is reviewed and tests pass on the supported Python matrix.
- [ ] Release tag points to the intended commit; tag creation/update/deletion is restricted.
- [ ] `pyproject.toml`, version, README, license, and package contents are reviewed.
- [ ] Build tools and dependencies are pinned/locked where practical and updates are reviewed.
- [ ] Wheel and sdist are built once, inspected, validated, and tested from a clean environment.
- [ ] Dependency vulnerability checks run; results and known limitations are recorded.

### CI identity and authorization

- [ ] Trusted Publisher uses the exact repository, workflow, and environment identity.
- [ ] TestPyPI and PyPI have separate configurations.
- [ ] Only the publish job has `id-token: write`.
- [ ] Build/test jobs do not have PyPI publishing credentials.
- [ ] Publish job consumes the intended build artifact rather than silently rebuilding.
- [ ] Third-party actions are pinned to reviewed full commit SHAs and updates are managed.
- [ ] Branch, tag, workflow-file, environment, and reviewer policies are configured in service settings.
- [ ] Untrusted PR code cannot reach privileged release steps; cache and runner trust boundaries are reviewed, with runner/network hardening applied where appropriate.

### Evidence and verification

- [ ] Artifact SHA-256 digests are recorded through a trusted process.
- [ ] Available PEP 740 attestations are checked for the expected identity, issuer, subject digest, and predicate.
- [ ] Provenance claims are interpreted within the builder’s actual guarantees.
- [ ] Reproducibility claims are backed by independent rebuilds and hash comparison, not assumptions.
- [ ] Release notes explain changes, compatibility, support policy, and known issues.

### Operations and response

- [ ] Maintainer 2FA and recovery procedures are in place; multiple trusted maintainers can recover the project.
- [ ] Old publishing tokens have been revoked after Trusted Publishing migration and any suspected exposure is investigated.
- [ ] `SECURITY.md`, advisory contacts, incident response steps, and release runbook are current.
- [ ] Yank/remediation/new-version procedure is understood and tested as a tabletop exercise.
- [ ] Runbook records approvals, workflow URL, version, artifact hashes, attestation results, and smoke tests without secrets.
- [ ] Handoff, deprecation, and sunset procedures are documented.

## 18. Authoritative references

Use these sources as the current authority for platform-specific behavior. Details and supported features can change.

- [Module 18 roadmap — Packaging, Distribution and Publishing](roadmap-Packaging-Distribution-and-Publishing.md) — syllabus and progression for this lesson.
- [PyPI: Trusted Publishing overview](https://docs.pypi.org/trusted-publishers/) — OIDC model and setup.
- [PyPI: Publishing with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/) — supported workflow and publishing action.
- [PyPI: Trusted Publisher security model](https://docs.pypi.org/trusted-publishers/security-model/) — trust assumptions and provider-specific considerations.
- [PyPI: Attestations overview](https://docs.pypi.org/attestations/) — PEP 740, supported attestation types, and verification.
- [PyPI: Producing attestations](https://docs.pypi.org/attestations/producing-attestations/) — supported publication flows.
- [PEP 740 — Index support for digital attestations](https://peps.python.org/pep-0740/) — Python packaging standard.
- [GitHub Actions: Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) — action pinning, permissions, and workflow security.
- [GitHub Actions: OIDC reference](https://docs.github.com/en/actions/concepts/security/openid-connect) — workload identity federation concepts.
- [Sigstore Python client documentation](https://docs.sigstore.dev/language_clients/python/) — signing and identity verification.
- [Sigstore documentation](https://docs.sigstore.dev/) — Fulcio, Rekor, and keyless signing model.
- [SLSA specification](https://slsa.dev/spec/v1.2/) — build/source tracks and assurance levels.
- [SLSA build provenance specification](https://github.com/slsa-framework/slsa/blob/main/spec/build-provenance.md) — provenance model and fields.
- [pip-audit documentation](https://github.com/pypa/pip-audit) — known vulnerability auditing for Python environments.
- [diffoscope documentation](https://diffoscope.org/) — investigation of differing build artifacts.
- [GitHub: About code owners and repository rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository) — branch/tag governance (see current relevant pages for your plan and repository type).

---

## Final competency checklist

You are ready to design a basic trusted release when you can explain the OIDC exchange without confusing the OIDC token with the upload credential; configure separate TestPyPI and PyPI publishers; build and validate once; restrict `id-token: write` to the publish job; protect branches, tags, and environments; verify the exact artifact digest and expected attestation identity; articulate what the evidence cannot prove; and follow an incident runbook if a release or account is compromised.
