# Software Bills of Materials (SBOMs) and License Compliance

> **Audience:** Python developers, release engineers, platform teams, security engineers, and open-source program offices (OSPOs).  
> **Target:** Python 3.12+; modern `pyproject.toml` metadata; `uv`, wheels, and CI-based release validation.  
> **Scope:** This lesson teaches technical inventory and policy workflows. It is not legal advice, and automated findings are not a definitive legal determination.

## 1. Learning objectives and prerequisites

By the end, you should be able to:

- Explain an SBOM and identify its consumers, minimum data, and limitations.
- Distinguish a dependency declaration, resolved lock, installed environment, wheel/sdist, and shipped application or container.
- Choose CycloneDX or SPDX for a use case and inspect component identity, relationships, hashes, licenses, and provenance.
- Generate an SBOM for a Python environment and inspect a built wheel or container independently.
- Run license and vulnerability scanners, interpret their evidence, and fail CI on a clearly defined policy violation.
- Handle unknown license metadata, transitive dependencies, vendored code, exceptions, and newly discovered risks.
- Retain per-release evidence and connect it to the exact artifact digest that was shipped.

### Prerequisites

You should understand Python package metadata (`pyproject.toml`), direct and transitive dependencies, virtual environments, `uv` and lockfiles, wheel and sdist builds, semantic versioning, CI workflows, hashing, and basic release security. Review package building and release security before applying this lesson to a production pipeline.

## 2. SBOM mental model and terminology

An **SBOM (Software Bill of Materials)** is a machine-readable record of software components and their relationships. It helps answer: *what components were identified in this product, in which versions, and what evidence connects them to this release?* Consumers include product security, vulnerability management, procurement, customers, auditors, incident responders, and maintainers.

An SBOM is an inventory, not a guarantee that a product is secure, compliant, complete, or free of malicious code. It can be used as input to vulnerability and license analysis, but it is not itself a vulnerability report or a legal opinion. The NTIA minimum-elements guidance includes supplier, component name/version, unique identifiers, dependency relationships, SBOM author, timestamp, automation support, and operating practices such as frequency, depth, known unknowns, distribution, access control, and accommodation of mistakes.

### 2.1 Direct and transitive dependencies

- **Direct dependency:** declared by the project (for example, `requests`).
- **Transitive dependency:** required by another dependency (for example, `urllib3` required by `requests`).
- **Build dependency:** used to build a distribution, such as a build backend. It may not be installed at runtime, but remains part of the build supply chain.
- **Optional dependency / extra:** installed only for a feature or environment.
- **Vendored component:** source or binaries copied into a project rather than installed as a separately visible distribution.
- **Native/system component:** shared libraries, operating-system packages, or native code that may not appear in a Python package inventory.

A project dependency declaration expresses intent and version constraints. A lockfile records a resolution under a particular tool, platform, and configuration. An installed environment records what is installed there. A wheel records a specific built distribution. A container records the combined application and runtime filesystem. These are related but not interchangeable inventories. Build-system requirements in `[build-system].requires` and isolated build environments may not appear in a runtime export; inventory build inputs separately when they are in scope for your supply-chain policy.

### 2.2 The four inventory scopes

| Evidence source | What it can tell you | What it can miss or misrepresent |
|---|---|---|
| `pyproject.toml` / requirements declarations | Intended direct dependencies and constraints | Actual versions selected, conditional dependencies, unlisted/vendored code, build-time tools |
| Lockfile / exported fully resolved requirements | Chosen versions and often artifact hashes/source details for the lock's target scope | Installed drift, omitted extras/platforms, code copied into the project, native libraries bundled later |
| Installed environment | Distributions installed in that interpreter/environment | Files bundled in a wheel but not represented as distributions, other environments, image OS packages, vendored code |
| Built wheel/sdist or shipped directory | Files and metadata in that specific artifact | Runtime environment added at deployment, base-image packages, external services, components not detectable by the scanner |
| Container image | Python distributions plus detectable OS/native components in the image | Runtime downloads, mounted files, external services, dynamically fetched models/data, scanner blind spots |

**Production rule:** create multiple complementary views where appropriate. At minimum, preserve the resolved dependency evidence, inspect the built distribution, and scan the final container if a container is what you ship. State exactly what each SBOM describes.

### 2.3 Component identity and provenance

Useful component fields include name, version, supplier/author when known, package URL (PURL), hashes, declared/concluded license evidence, external references, dependency relationships, and source or build provenance. A PURL identifies a package using an ecosystem-aware coordinate; it is not proof that the package is authentic. A cryptographic digest identifies bytes; it does not establish whether those bytes are safe or licensed correctly.

Record at least:

- Product/distribution name and version.
- Source revision and build run identifier.
- SBOM generator and version, format and spec version.
- Generation timestamp and scope (environment, requirements, wheel, image).
- Artifact filename, digest, and immutable release identifier.
- Known gaps, ignored paths, excluded optional dependencies, and exceptions.

## 3. Formats and component identification

### 3.1 CycloneDX and SPDX

**CycloneDX** is a BOM standard designed for supply-chain risk use cases. It supports component inventories, dependency relationships, hashes, license data, vulnerabilities, and related security metadata. JSON and XML are common encodings. It is a strong default when a team wants a compact BOM integrated with vulnerability workflows and related VEX/attestation processes.

**SPDX** is an international standard for communicating software component, license, copyright, and provenance information. SPDX supports detailed licensing evidence and expressions, as well as JSON and tag-value formats. It is often a good fit for license compliance and software transparency workflows.

Both formats can serve both security and compliance workflows. Neither format guarantees that a generator found every component or that metadata is correct. Choose based on downstream consumer support, required fields, and validation needs; do not assume a format alone determines quality.

| Consideration | CycloneDX | SPDX |
|---|---|---|
| Typical strength | Supply-chain and security-risk workflows; links to vulnerability/VEX practices | License, copyright, package and file-level compliance evidence |
| Common encodings | JSON, XML (and other supported encodings depending on version/tool) | JSON, tag-value, and other standard serializations |
| Dependencies/relationships | Yes | Yes |
| License expressions and evidence | Yes | Yes; detailed licensing is a central use case |
| Selection principle | Match the consumer's required spec/tool support | Match the consumer's required spec/tool support |

Always check the **actual specification version emitted by the tool**. Tool versions may change defaults and supported schema versions. Validate the generated document with the appropriate validator when it is used as a contractual release artifact.

### 3.2 License identifiers and expressions

An SPDX identifier such as `MIT`, `Apache-2.0`, or `GPL-3.0-only` is a standardized label. A license expression describes how multiple terms relate:

- `MIT` — one license.
- `MIT OR Apache-2.0` — alternative terms may be available; confirm the exact license grant and context.
- `MIT AND Apache-2.0` — obligations from both licenses may need to be satisfied.
- `GPL-3.0-only WITH Classpath-exception-2.0` — a license plus a named exception.
- `NOASSERTION` — the document does not assert a conclusion; it is not equivalent to a permissive license.
- `LicenseRef-Proprietary` — a custom reference that requires corresponding evidence and review.

Use current identifiers and syntax from the [SPDX License List](https://spdx.org/licenses/) and [SPDX license-expression specification](https://spdx.github.io/spdx-spec/). Do not convert free-form strings into SPDX identifiers by guessing.

## 4. License fundamentals and policy interpretation

### 4.1 Common families

- **Permissive** (for example, MIT, BSD, Apache-2.0): generally allow broad use and redistribution subject to conditions such as preserving notices. Apache-2.0 includes express patent-license and termination provisions that matter in some situations.
- **Weak copyleft** (for example, MPL-2.0 and LGPL variants): obligations can depend on file boundaries, linking, modifications, distribution mode, and the exact license text.
- **Strong copyleft** (for example, GPL variants): distribution and combination facts may trigger source-availability and other obligations. The result depends on the applicable license and how the software is used and distributed.
- **Network copyleft** (for example, AGPL variants): includes provisions addressing certain network interactions; details depend on the license version and deployment facts.
- **Source-available / non-commercial / custom terms:** not necessarily open-source licenses. Read the actual terms and seek legal review where needed.
- **Proprietary / commercial:** permission may depend on a contract, entitlement, or license key. A public SPDX identifier may not exist.

These are useful screening categories, not legal conclusions. A scanner's label does not decide whether a specific use or distribution complies with the license. Obligations can depend on the code actually included, modifications, distribution, linking, notices, contracts, and applicable law.

### 4.2 Declared metadata versus actual obligations

A project's `[project].license` metadata describes the distribution's declared license expression. It does not prove that every file in the repository or wheel is covered by that license. A package may include third-party code, generated code, assets, vendored libraries, license exceptions, or incorrect metadata. Conversely, older packages may have accurate license files but incomplete metadata.

For modern packaging metadata, PEP 639 defines a string SPDX expression and `license-files` patterns. For example, with a build backend that supports PEP 639:

```toml
[project]
name = "tinytools"
version = "1.2.0"
requires-python = ">=3.12"
license = "MIT"
license-files = ["LICENSE", "NOTICE", "licenses/**"]
```

This declares the project's license expression and the license/notice files to include. It does not automatically resolve the licenses of dependencies or certify that the declaration is factually correct. Check your build backend version: support for PEP 639 differs by backend and version. See the [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/licensing-examples-and-user-scenarios/) and [PEP 639](https://peps.python.org/pep-0639/).

### 4.3 Notices, attribution, and review

A release compliance process may need to:

1. Preserve third-party license texts and copyright notices.
2. Include required attribution and `NOTICE` content.
3. Generate a `THIRD_PARTY_LICENSES` report or equivalent notice bundle.
4. Identify vendored code and its license separately from package metadata.
5. Record decisions, evidence, reviewers, scope, and expiry for exceptions.
6. Check source and binary distributions independently when their contents differ.

Do not treat a package's metadata field as a substitute for reading the license file when the risk or policy requires it.

## 5. Generate an SBOM for a Python project

The commands below assume a project using `uv`, a committed `uv.lock`, and a virtual environment. Pin tool versions in a real release pipeline and retain the exact command/tool version in the evidence directory. The examples show current command families but do not pin the ephemeral `uvx` tools by themselves; for release use, replace floating invocations with approved exact versions and inspect `--help` after upgrades because flags and output formats can evolve.

### 5.1 Export a resolved dependency set

From the project root:

```bash
uv lock --check
uv export --locked --no-dev --format requirements-txt -o requirements-runtime.txt
uv tree --locked
```

`requirements-runtime.txt` is a useful export of the selected runtime dependency set for the chosen project configuration. Check whether your project has extras, platform markers, optional groups, or multiple deployment targets; produce a distinct export for each supported deployment configuration when required. Do not assume one export represents every platform.

### 5.2 Generate from an installed environment

Create a dedicated environment that mirrors the target runtime configuration, install the project or its locked runtime requirements, and generate an environment SBOM:

```bash
uv venv .venv-sbom
uv pip install --python .venv-sbom/bin/python -r requirements-runtime.txt
uvx --from cyclonedx-bom cyclonedx-py environment .venv-sbom/bin/python --output-file sbom-environment.cdx.json
```

The `cyclonedx-py environment` subcommand inventories a Python environment; the interpreter is a positional argument in the documented CLI. Verify the exact options for your installed `cyclonedx-py` release with `uvx --from cyclonedx-bom cyclonedx-py environment --help`. If your platform uses Windows, substitute `.venv-sbom\\Scripts\\python.exe` for `.venv-sbom/bin/python`.

A requirements-based SBOM is another useful view:

```bash
uvx --from cyclonedx-bom cyclonedx-py requirements requirements-runtime.txt -o sbom-requirements.cdx.json
```

This describes the dependency information the generator can derive from that requirements file. It is not an inventory of every file in a wheel or container. The [CycloneDX Python tool documentation](https://github.com/CycloneDX/cyclonedx-python) documents the supported `environment`, `requirements`, `poetry`, and `pipenv` workflows and their options.

### 5.3 Scan with Syft

[Syft](https://github.com/anchore/syft) can catalog packages in directories, archives, and container images and emit CycloneDX or SPDX formats. Install it from its official distribution channel and verify the downloaded binary according to your organization's tool-installation policy.

```bash
# Scan the repository directory (useful, but not the same as a release-artifact scan)
syft scan . -o cyclonedx-json=sbom-source-tree.cdx.json

# Scan the built wheel itself
syft scan dist/tinytools-1.2.0-py3-none-any.whl -o cyclonedx-json=sbom-wheel.cdx.json

# Scan the final image, if the shipped product is a container
syft scan registry.example.com/team/tinytools@sha256:<image-digest> -o cyclonedx-json=sbom-image.cdx.json
```

Confirm the CLI syntax for the installed Syft version (`syft version`, `syft scan --help`) and the input type support. Replace `<image-digest>` with the real digest before running the command. Pin the image by immutable digest for release evidence, not only a mutable tag; the placeholder above is intentionally not executable. If the tool uses a different command form in your installed version, follow its current official documentation. Syft can identify many ecosystem packages and OS packages, but scanners have blind spots and format encodings may differ in which relationships or file-level details they preserve.

### 5.4 What the outputs mean

- `sbom-requirements.cdx.json`: what the generator can infer from the exported dependency list.
- `sbom-environment.cdx.json`: what the generator detected in the target Python environment.
- `sbom-source-tree.cdx.json`: components detected while scanning the source tree.
- `sbom-wheel.cdx.json`: components detected inside or associated with the wheel archive.
- `sbom-image.cdx.json`: components detected in the final container image.

Keep the scopes separate. Do not rename a requirements-derived SBOM to imply it is an exhaustive wheel or image inventory. Review duplicate names, missing versions, unresolved components, and packages whose license or supplier is unknown.

## 6. Artifact-aware validation

### 6.1 Build and inspect the exact distribution

Build with your project's configured backend and locked build dependencies. For example:

```bash
uv build
python -m pip install --upgrade twine
python -m twine check dist/*
sha256sum dist/*
```

`uv build` creates distribution artifacts in `dist/`; `twine check` checks core distribution metadata/rendering, not license compliance or security. On Windows, use a platform-appropriate SHA-256 command, such as PowerShell `Get-FileHash`. Record each filename and digest in the release manifest.

Inspect wheel contents and metadata:

```bash
python -m zipfile -l dist/tinytools-1.2.0-py3-none-any.whl
```

A wheel is a ZIP archive. Inspect its `.dist-info/METADATA` for `Requires-Dist`, `License-Expression`, and `License-File` fields where present, and inspect `.dist-info/licenses/` for included license and notice files. Metadata may be absent or legacy in older packages; absence should trigger a review rather than an invented license.

For a deeper wheel inspection, use `unzip -l` or a wheel-inspection tool, and compare the archive contents to the source tree. Identify vendored packages and bundled shared libraries. Python-level SBOM tools may not fully enumerate native libraries bundled inside binary wheels (for example, libraries copied into wheels during platform repair). Use suitable native-binary inspection and container scanning for those cases.

### 6.2 Clean install test

A release should be validated independently from the developer's working environment:

```bash
python -m venv .venv-clean
# POSIX:
.venv-clean/bin/python -m pip install --upgrade pip
.venv-clean/bin/python -m pip install dist/tinytools-1.2.0-py3-none-any.whl
.venv-clean/bin/python -m pip check
.venv-clean/bin/python -c "import tinytools; print(tinytools.__file__)"
```

On Windows, use `.venv-clean\\Scripts\\python.exe`. Run the package's documented smoke tests from outside the source tree so the current directory does not shadow the installed distribution. A clean install validates installability and basic runtime behavior; it does not establish that every shipped component has been inventoried.

### 6.3 Reconcile the scopes

Before release, compare:

- Locked/exported runtime dependencies against installed runtime distributions.
- Installed distributions against package relationships in the SBOM.
- Wheel files and metadata against the source tree and expected package contents.
- Container Python packages against the wheel/environment SBOMs.
- Vendored/native/system components against additional scans and manual evidence.

Investigate unexplained differences. Expected differences can include build-only dependencies, optional extras, platform-specific markers, vendored code, and operating-system packages. Record the reason rather than forcing all SBOMs to match byte-for-byte.

## 7. License and vulnerability scanning

### 7.1 License inventory with `pip-licenses`

`pip-licenses` reads installed distribution metadata. Use it against the intended application environment, not a global Python installation:

```bash
uvx pip-licenses --python .venv-sbom/bin/python --format=json --output-file license-report.json
uvx pip-licenses --python .venv-sbom/bin/python --format=markdown --with-urls
```

Check the exact `--python` and output flags with `uvx pip-licenses --help` for the pinned version. If the tool cannot target a separate interpreter in your selected release, run it in the target environment or use a tool that can scan the desired target. Do not accidentally scan the CI tool environment and call the result the application's inventory.

License scanners usually rely on package metadata and heuristics. They can return free-form strings, omit license files, or fail to recognize vendored components. `Unknown`, `NOASSERTION`, blank, proprietary, and custom identifiers should be triaged according to policy, not silently accepted. Preserve the raw report.

`pip-licenses --fail-on` can fail on specified **license-name strings**, but metadata strings vary by package and version. For a policy based on SPDX expressions or families, prefer normalized SPDX-aware policy tooling or a reviewed policy script operating on a known schema. Do not assume a substring match or a single display name covers every GPL/AGPL variant.

### 7.2 Vulnerability scanning with `pip-audit`

For a resolved requirements export:

```bash
uvx pip-audit -r requirements-runtime.txt --format json --output pip-audit.json
```

For a live environment, run `pip-audit` against that environment using the documented interpreter/environment options for the pinned version. Keep the scan target and advisory database/source explicit. A vulnerability scanner correlates component identities and versions with advisory data; it does not prove exploitability or absence of unknown vulnerabilities.

A finding should be triaged using:

1. Advisory ID, affected/fixed version range, and source.
2. Severity (for example, CVSS) and exploit-likelihood context (for example, EPSS where available).
3. Whether the vulnerable code path is reachable in this product and configuration.
4. Exposure, permissions, inputs, and deployment context.
5. Fixed version availability, compatibility tests, mitigations, and residual risk.
6. Owner, deadline, and a documented exception expiry if a fix cannot be applied immediately.

Do not block every low-severity finding without context, but do not dismiss a high-severity issue merely because the vulnerable code is believed unused. Record evidence and reassess after changes.

### 7.3 Dependency graph analysis

Use the resolver's graph to understand why a component is present:

```bash
uv tree --locked
```

For pip-based environments, `pipdeptree` can render dependency relationships. The graph helps identify which direct dependency introduces a vulnerable or restricted transitive component. It does not tell you whether the component's code is reachable at runtime, nor whether a license obligation is triggered by a particular combination. Dependency graphs and license review are complementary evidence.

### 7.4 Handling ambiguous licenses

If a component's license is missing, contradictory, or nonstandard:

1. Keep the release in a review state if policy requires known licenses.
2. Inspect the exact wheel/sdist and the upstream repository's license and notices at the corresponding version/tag.
3. Determine whether the distribution vendors additional code and inspect those files separately.
4. Compare metadata with authoritative upstream evidence; record source URLs and artifact hashes.
5. Ask the component owner or legal reviewer to resolve ambiguity.
6. Update the internal record and exception decision; do not rewrite the upstream package's license in your report without evidence.

A scan result is evidence for review, not a legal determination.

## 8. CI integration and release evidence

### 8.1 Recommended release pipeline

A strong pipeline runs tests, builds the exact wheel/sdist, installs the wheel in a clean environment, generates a dependency/environment SBOM, scans the built artifact and final image where relevant, runs vulnerability and license policy checks, validates notices, hashes the outputs, and publishes evidence with the same immutable release identity as the artifacts.

**Important scope rule:** a job that installs scanner tools into the application environment can pollute the inventory with the scanners' own dependencies. Prefer isolated scanner tooling and explicit target selection, or clearly label a tool-inclusive environment. A lockfile SBOM and a wheel/image SBOM answer different questions.

### 8.2 A concrete GitHub Actions pattern

The following is a **starting template** for a project with `pyproject.toml`, `uv.lock`, a wheel build, and a license policy that rejects GPL/AGPL-family findings. Pin third-party actions to reviewed immutable commit SHAs in production; the readable major-version references below are illustrative. Pin Python/tool versions and validate every command against the pinned release before adopting the workflow.

```yaml
# .github/workflows/compliance.yml
name: Release compliance

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Verify lock and build distributions
        run: |
          uv lock --check
          uv sync --locked
          uv run --locked pytest
          uv build
          python -m pip install --upgrade twine
          python -m twine check dist/*
          mkdir -p evidence
          sha256sum dist/* > evidence/artifact-sha256.txt
          uv --version > evidence/tool-versions.txt
          python --version >> evidence/tool-versions.txt
          python -m pip --version >> evidence/tool-versions.txt

      - name: Export runtime dependencies
        run: |
          uv export --locked --no-dev --no-emit-project --format requirements-txt -o evidence/requirements-runtime.txt

      - name: Audit known vulnerabilities
        run: |
          uvx pip-audit -r evidence/requirements-runtime.txt --format json --output evidence/pip-audit.json

      - name: Generate dependency SBOM
        run: |
          uvx --from cyclonedx-bom cyclonedx-py requirements evidence/requirements-runtime.txt -o evidence/sbom-requirements.cdx.json

      - name: Install pinned Syft CLI
        run: |
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/v1.44.0/install.sh | sh -s -- -v -b "$HOME/.local/bin" v1.44.0
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"
          syft version

      - name: Scan built wheel with Syft
        shell: bash
        run: |
          mapfile -t wheels < <(find dist -maxdepth 1 -type f -name '*.whl' -print | sort)
          test "${#wheels[@]}" -eq 1 || { echo "Expected exactly one wheel; found ${#wheels[@]}" >&2; exit 1; }
          syft scan "${wheels[0]}" -o cyclonedx-json=evidence/sbom-wheel.cdx.json

      - name: Create a clean runtime environment and license inventory
        shell: bash
        run: |
          python -m venv .venv-compliance
          .venv-compliance/bin/python -m pip install --upgrade pip
          .venv-compliance/bin/python -m pip install -r evidence/requirements-runtime.txt
          .venv-compliance/bin/python -m pip install --no-deps dist/*.whl
          .venv-compliance/bin/python -m pip check
          uvx pip-licenses --python .venv-compliance/bin/python --format=json --output-file evidence/licenses.json
          uvx pip-licenses --python .venv-compliance/bin/python --format=markdown --with-urls > evidence/licenses.md

      - name: Enforce license policy
        run: python scripts/check_license_policy.py evidence/licenses.json

      - name: Upload compliance evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: compliance-evidence
          path: evidence/
          if-no-files-found: warn
```

**Before using this template:** the workflow above *does* include a Syft installer step; the command is an example, not a claim that its downloaded binary was verified in this lesson. In production, prefer an organization-maintained runner/container with Syft preinstalled. This example requests Syft's installer signature-verification mode (`-v`); that mode requires a separately installed and trusted `cosign` executable, and the installer itself must still be obtained from a reviewed source. If verification prerequisites are absent or verification fails, stop the job rather than silently installing without verification. Pin every action to a reviewed immutable commit SHA and every CLI tool to an approved version (for example, through a checked-in CI-tools constraints/requirements file or a pinned runner image); the `uvx` examples above show command shape and must be adapted to that pinning strategy. Ensure `uv run --locked pytest` runs tests in the correct project context and that the default development dependency group contains the test runner, or explicitly install the test group. The `dist/` scan step selects one wheel; if you need evidence for the sdist or multiple wheels, scan each exact artifact separately and use a distinct output filename. Validate the exact `cyclonedx-py`, `pip-licenses`, `pip-audit`, and Syft CLI options against the pinned versions.

A nonzero exit from `pip-audit` or the policy checker is a blocking result in this job; the `if: always()` upload step is intended to preserve any evidence generated before failure, not to convert failure into success. The workflow should not be considered production-ready until its tool versions and actions are pinned, the target scopes are confirmed, the license-policy parser is tested against real reports, the SBOMs are validated, and the uploaded evidence is tied to the exact artifact digest. Because the evidence upload uses a workflow artifact rather than a release attachment, a separate protected release job should promote the reviewed evidence alongside the exact published artifact if durable release-level traceability is required.

### 8.3 Example license-policy checker

`pip-licenses` output is intended as a metadata report; its license names are not guaranteed to be SPDX-normalized. The following **illustrative fail-closed gate** detects common GPL/AGPL labels and also fails on missing/unknown metadata. It intentionally requires human review of unrecognized strings. It is not a complete SPDX-expression parser and must be tested and extended for the organization's package ecosystem before use.

```python
# scripts/check_license_policy.py
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Conservative heuristic only: catches common labels, not every possible expression.
RESTRICTED = re.compile(
    r"\b(?:GNU\s+)?(?:Affero\s+)?General Public License\b|"
    r"\b(?:AGPL|GPL)(?:[- ]?\d+(?:\.\d+)?(?:[- ]?(?:only|or[- ]?later))?)?\b",
    re.IGNORECASE,
)
UNKNOWN = {"", "unknown", "noassertion", "none", "n/a", "not found", "unlicensed"}


def main(report_path: str) -> int:
    data = json.loads(Path(report_path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("ERROR: expected pip-licenses JSON list; review tool output/schema.", file=sys.stderr)
        return 2

    failures: list[str] = []
    for item in data:
        if not isinstance(item, dict):
            failures.append(f"Malformed row: {item!r}")
            continue
        name = str(item.get("Name", item.get("name", "<unknown package>")))
        version = str(item.get("Version", item.get("version", "<unknown version>")))
        license_name = str(item.get("License", item.get("license", ""))).strip()
        if license_name.casefold() in UNKNOWN:
            failures.append(f"UNKNOWN LICENSE: {name}=={version}: {license_name or '<blank>'}")
        elif RESTRICTED.search(license_name):
            failures.append(f"RESTRICTED LICENSE REVIEW: {name}=={version}: {license_name}")

    if failures:
        print("License policy gate failed; review these findings:", file=sys.stderr)
        for finding in failures:
            print(f" - {finding}", file=sys.stderr)
        return 1
    print("No restricted or unknown license labels detected by this heuristic.")
    print("This is not proof of legal compliance; review vendored files and metadata quality.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
```

#### Policy caveats

- The checker is intentionally conservative and may produce false positives or miss unusual labels, custom names, SPDX expressions, and vendored components.
- The text `MIT OR GPL-3.0-only` includes a GPL option; whether the project's use is permissible depends on the actual license grant and policy. A strict permissive-only policy should route any expression containing a restricted option to review rather than infer that `OR` automatically makes it safe.
- A production-grade policy should normalize metadata using an SPDX-aware parser, understand `AND`/`OR`/`WITH` expressions, define how alternatives are evaluated, and inspect license files and vendored code. Treat unknown results as review-required.
- Do not use a regex-only policy as the sole legal compliance control. Use the report as a gate and attach human-reviewed decisions to exceptions.

### 8.4 Exceptions workflow

An exception should include package and version, artifact digest, evidence and scope, affected license/CVE, reason, risk assessment, mitigation, approver, owner, expiry date, and a re-review trigger. Keep exceptions in version control or an auditable policy system. Expired exceptions must fail CI or create a blocking review. A license exception and a vulnerability-risk acceptance are different decision types and should have different approvers where policy requires it.

## 9. Advanced governance and incident response

### 9.1 SBOMs, provenance, hashes, and attestations

A hash binds evidence to bytes. A signature or attestation can bind a statement to an identity and build context. Neither proves the source code is benign or the license conclusion is correct. Use these controls together:

1. Generate SBOMs after the relevant build stage, with the exact artifact or image digest recorded.
2. Generate build provenance that identifies source revision, builder identity, workflow, and materials where supported (for example, SLSA provenance or an in-toto attestation).
3. Sign or attest the SBOM/provenance using your organization's keyless or managed-key trust model.
4. Verify signatures and identities at release/deployment, not merely at generation.
5. Retain the SBOM, provenance, artifact hashes, scan outputs, policy decisions, and tool versions together.

For containers, tools such as `cosign attest` and `cosign verify-attestation` can be part of the workflow, but their exact predicate types, identity constraints, and CLI options depend on the chosen attestation format and cosign version. Validate the official documentation and pin versions. Do not claim a signature verifies an SBOM's completeness; it verifies integrity/authenticity under the configured trust policy.

### 9.2 Policy and governance

A mature program defines:

- Approved inbound and outbound licenses, prohibited or review-required families, and criteria for `LicenseRef` and proprietary dependencies.
- Required attribution/notice files and how to generate `THIRD_PARTY_LICENSES`.
- Who can approve exceptions and how they expire.
- Minimum metadata quality, SBOM formats, release frequency, and retention period.
- Required artifact scopes: source, wheel, runtime environment, container, and any model/data artifacts in scope.
- Vulnerability severity and exploitability thresholds, SLAs, escalation, and waiver policy.
- Component ownership, security contact, deprecation policy, and incident response process.
- Required tool versions, policy versions, scan data sources, and audit logs.

An OSPO or equivalent function can coordinate inbound/outbound policy, contribution rules, notices, and records. Engineering owns technical accuracy; legal counsel should advise on legal interpretation where required.

### 9.3 Python wheels, containers, native libraries, and AI assets

- **Python wheel:** inspect distribution metadata, packaged files, bundled resources, and vendored code.
- **Container:** scan the final image, including OS packages, Python distributions, native libraries, and build/runtime layer differences. Multi-stage builds can mean the final image differs substantially from the build environment.
- **Native wheel dependencies:** a wheel may include shared libraries not represented as separate Python distributions. Inspect wheel contents and native dependencies with appropriate platform tools.
- **Vendored source:** inventory copied code even if it does not appear in `pip list` or the dependency graph.
- **Models and datasets:** model weights, datasets, tokenizer files, and generated assets can have separate licenses, usage restrictions, provenance, and attribution needs. A Python SBOM alone is not an AI/model/data bill of materials. Track model/dataset identity, version/digest, origin, and license separately where applicable.
- **Conda/mixed environments:** pip-based tools may not inventory Conda packages or system packages completely. Use ecosystem-aware tooling and reconcile the environment manager's inventory with the Python-level SBOM.

### 9.4 Vulnerability with no fix available

When a critical vulnerability affects a transitive dependency and no fixed version exists:

1. Use the SBOM and dependency graph to identify all affected products, versions, and services.
2. Confirm component identity and affected version range; rule out name/version mismatches.
3. Assess reachability, exposure, exploitability, and operational impact.
4. Consider temporary mitigations, configuration changes, isolation, disabling the feature, replacing the dependency, or maintaining a reviewed patch/fork.
5. Record the decision, owner, deadline, evidence, and expiry. Do not silently pin a vulnerable version indefinitely.
6. Test the mitigation and monitor advisory updates.
7. Rebuild, regenerate SBOMs, rescan, and publish a new artifact when remediation is available.

A VEX statement can communicate whether a vulnerability is affected, not affected, fixed, or under investigation according to its format and evidence. It should be scoped to a product/version and justified, not used as a blanket dismissal.

### 9.5 Incident exercise: critical transitive CVE

Suppose a critical advisory is published for `example-parser`, a transitive dependency of `tinytools`.

- Query retained SBOMs for `example-parser` and its affected versions.
- Use dependency relationships to identify which direct dependency introduced it.
- Join SBOM records to artifact digests and deployment inventory to list affected services.
- Confirm versions and platform-specific artifacts; inspect whether the vulnerable code path is present/reachable.
- Notify service owners, set a remediation SLA, and apply an upgrade, patch, replacement, or time-bounded mitigation.
- Produce an impact report with affected releases, exposure, decision, and rollout status.
- Rebuild and rescan; attach the new SBOM and provenance to the remediated artifact.
- Preserve prior evidence and the post-incident review.

The goal is to answer *which exact releases are affected?* in minutes, without relying on a developer remembering every dependency.

## 10. Troubleshooting

| Symptom | Likely causes | Response |
|---|---|---|
| SBOM omits a package | Wrong environment, optional extra not installed, unsupported ecosystem, scanner limitation | Confirm scope; inspect lock/export, installed metadata, wheel/image; add a separate scan where needed |
| Many packages appear unexpectedly | Build/test tools installed in target environment, global interpreter used, multiple environments scanned | Use a clean target environment and isolate scanner tools; document scope |
| License is blank or `UNKNOWN` | Legacy metadata, nonstandard license string, incomplete wheel metadata | Inspect exact artifact, upstream license and notices; route for review; do not auto-approve |
| License report says GPL but upstream says otherwise | Stale or inaccurate metadata, fork, vendored code, heuristic classification | Verify package version, source tag, license files and provenance; retain evidence and correct internal record after review |
| Vulnerability result is surprising | Wrong component identity, advisory range nuance, distro backport, stale database | Verify PURL/name/version and advisory; use ecosystem-specific data; investigate vendor patches and false-positive rationale |
| `pip-audit` finds nothing but image scanner reports issues | OS/native packages or different image contents | Treat as different scopes; scan final image and address system packages separately |
| SBOM changes between builds | Unlocked dependencies, different platforms/extras, tool/spec version changes, timestamps/IDs | Lock dependencies; pin tools; document target matrix; compare normalized component sets and artifact digests |
| `License-Expression` is missing | Older metadata/backend or legacy package | Inspect license files and upstream evidence; do not infer a license from package name |
| Wheel contains bundled `.so`/`.dll`/`.dylib` | Native library bundled by build/repair process | Inspect native dependencies; use wheel and image scanning; document components not captured by Python metadata |
| CI policy fails on a new license label | New metadata spelling, SPDX expression, new dependency | Fail closed, review the component and update normalized policy only after approval |
| CI policy passes unexpectedly | Scanner omitted target, wrong interpreter, parser schema changed, license represented as an unrecognized expression | Test tool target selection and parser schema; add fixtures for unknown and restricted variants; pin tool versions |
| Evidence cannot be tied to release | Mutable tags, missing hashes, overwritten artifacts, no build metadata | Use immutable release identifiers and SHA-256 digests; retain provenance and SBOM alongside each artifact |

## 11. Hands-on lab

This lab is a reproducible pattern, not a claim that a registry, CI job, or scan has been run. Use a disposable repository and a pinned toolchain.

### Lab A — Create a minimal package with explicit license metadata

1. Create a `src/`-layout Python package and tests.
2. Add a `LICENSE` file whose contents match the license you have authority to use.
3. Use a backend version that supports PEP 639, and declare `license` and `license-files` in `pyproject.toml`.
4. Declare runtime dependencies and lock them using `uv lock`.
5. Build with `uv build` and inspect the wheel's `.dist-info/METADATA` and `.dist-info/licenses/`.

### Lab B — Generate and compare SBOMs

```bash
uv export --locked --no-dev --format requirements-txt -o requirements-runtime.txt
uvx --from cyclonedx-bom cyclonedx-py requirements requirements-runtime.txt -o sbom-requirements.cdx.json
uv build
syft scan dist/ -o cyclonedx-json=sbom-dist.cdx.json
```

If `dist/` contains multiple artifacts, repeat the Syft command for each exact artifact and use a separate output filename. Validate tool options against the pinned version. Compare component names, versions, dependency edges, and license metadata across the requirements and artifact SBOMs. Explain every meaningful difference.

### Lab C — Scan and enforce policy

1. Install the built wheel into a fresh environment with its runtime dependencies.
2. Generate `pip-licenses` JSON from that environment.
3. Run `pip-audit` against the pinned runtime requirements export and retain the JSON report. Treat this as a scan of the package/version set represented by that export; it does not automatically cover build tools, other extras/platforms, installed drift, native/OS packages, or vendored code.
4. Add the policy checker from Section 8.3, then create test fixtures containing `MIT`, `GPL-3.0-only`, `AGPL-3.0-only`, an unknown license, and a compound expression such as `MIT OR GPL-3.0-only`.
5. Verify the gate fails on restricted and unknown findings. Extend the policy to use a real SPDX parser before production use.
6. Add an exception fixture with an expiry date and ensure expired exceptions fail.
7. Attach the SBOMs, scan outputs, artifact hashes, tool versions, and policy decision to the same release record.

**Acceptance criteria:** You can state what each SBOM describes, identify the exact shipped artifact digest, explain all unknown or restricted license findings, locate transitive dependencies behind a finding, and demonstrate that CI fails for the intended policy conditions. Do not claim legal compliance solely because the automated job passes.

## 12. Self-check answers

### 1. What is the difference between CycloneDX and SPDX and which would you pick for vulnerability workflows vs license compliance?

CycloneDX is commonly chosen for supply-chain security and vulnerability-oriented workflows, with component/dependency data and support for related vulnerability and VEX processes. SPDX is especially strong for software transparency, license/copyright evidence, and compliance records. Both support component inventories, relationships, and license data; both can serve either workflow. Select based on the fields and integrations required by downstream consumers, then validate the emitted specification version and completeness. For a typical vulnerability pipeline I would start with CycloneDX; for a detailed license-compliance record I would consider SPDX, while retaining the ability to generate both if required.

### 2. Why can an SBOM generated from `requirements.txt` miss risk present in the shipped wheel/container?

A requirements file describes dependency constraints or a resolved package list, not every file shipped. A wheel can include vendored source, bundled native libraries, package data, generated assets, or different metadata. A container adds OS packages, shared libraries, application files, and base-image contents. Requirements may also omit build dependencies, optional extras, platform-specific packages, and runtime additions. Scan the built wheel and final image in addition to generating a dependency-based SBOM, and document the scope of each output.

### 3. Add a CI job that generates an SBOM, runs `pip-audit` and license checks, and fails on GPL/AGPL in a permissive-only project.

Use the workflow in Section 8.2 as a starting point: verify the lock, export the runtime set, run `pip-audit`, generate a CycloneDX SBOM, build and scan the wheel, install the wheel into a clean runtime environment, and generate a license report with `pip-licenses`. The gate in Section 8.3 fails on common GPL/AGPL labels and unknown metadata. Its regex is intentionally illustrative; a production policy must normalize SPDX expressions with a parser, cover variants and custom labels, inspect vendored code, and test the parser against fixtures. A reviewer must decide exceptions and record owner, evidence, approval, and expiry. The automated result establishes only that the selected scanner and policy detected no matching findings within their scope; it does not prove every component was found, every license declaration is accurate, or that the product is legally compliant.

## 13. Release-compliance checklist

### Inventory and build

- [ ] SBOM generated for each relevant release and not treated as a one-time document.
- [ ] SBOM scope is explicit: lock/export, installed environment, wheel/sdist, container, or other artifact.
- [ ] Direct, transitive, optional, build-time, vendored, native, and OS components have been considered.
- [ ] The exact artifact digest, release version, source revision, build run, tool versions, and SBOM spec version are retained.
- [ ] The wheel/sdist was inspected and tested in a clean environment.
- [ ] The final container was scanned if it is the shipped artifact.

### License compliance

- [ ] Project metadata uses an appropriate license expression and includes required license/notice files.
- [ ] Dependency licenses and license expressions have been reviewed; unknown and ambiguous findings are not silently accepted.
- [ ] Vendored components and non-Python assets are inventoried.
- [ ] `NOTICE` and `THIRD_PARTY_LICENSES` content has been reviewed where applicable.
- [ ] Restricted licenses are blocked or routed according to policy; GPL/AGPL decisions are not inferred from a regex alone.
- [ ] Exceptions include evidence, approver, owner, mitigation, and expiry.

### Vulnerability and release evidence

- [ ] Vulnerability scans use an identified advisory source and preserve machine-readable output.
- [ ] Findings are triaged using severity, reachability, exposure, fix availability, and mitigation evidence.
- [ ] No-fix risks have a time-bounded owner and review date.
- [ ] SBOM, provenance, hashes, scan reports, and policy decisions are attached to the same immutable release identity.
- [ ] CI fails on defined policy violations and has tests for unknown metadata, restricted licenses, parser changes, and expired exceptions.
- [ ] Previous release evidence is retained for incident response and audit.

## 14. Authoritative references

Use official documentation and the versions pinned by your organization. Tool CLIs and supported SBOM specification versions evolve.

- [NTIA — The Minimum Elements for a Software Bill of Materials](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom)
- [CycloneDX specification and tools](https://cyclonedx.org/) and [CycloneDX Python CLI documentation](https://github.com/CycloneDX/cyclonedx-python)
- [SPDX specifications](https://spdx.github.io/spdx-spec/) and [SPDX License List](https://spdx.org/licenses/)
- [Python Packaging User Guide — licensing examples and scenarios](https://packaging.python.org/en/latest/guides/licensing-examples-and-user-scenarios/)
- [PEP 639 — Improving License Clarity with Better Package Metadata](https://peps.python.org/pep-0639/)
- [Python Packaging — license expression specification](https://packaging.python.org/en/latest/specifications/license-expression/)
- [pip-audit project and documentation](https://github.com/pypa/pip-audit)
- [pip-licenses project and documentation](https://github.com/raimon49/pip-licenses)
- [Syft documentation](https://oss.anchore.com/docs/guides/sbom/) and [Syft source](https://github.com/anchore/syft)
- [SLSA provenance](https://slsa.dev/spec/v1.0/provenance) and [in-toto attestations](https://github.com/in-toto/attestation)
- [Sigstore Cosign documentation](https://docs.sigstore.dev/cosign/)
- [OSV — Open Source Vulnerabilities](https://osv.dev/)
- [GitHub — About dependency review](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review)

---

**Core principle:** generate inventory from the right object, preserve evidence for the exact release, and treat automated license/vulnerability results as decision-support evidence—not proof of security or a substitute for legal review.
