# Roadmap — Module 1.18: Packaging, Distribution and Publishing

This is the learning roadmap for the eighteenth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about turning Python code into installable, versioned, trustworthy
packages, **in what order**, **how** to practise each topic, and **how to
prove to yourself** that you have learned it.

Module 1.6 taught you how to *organise* a project (layout, `pyproject.toml`,
lock files, `uv`, dependency management, semantic versioning). This module
teaches how to *ship* it: build backends, wheels and sdists, console scripts,
plugin entry points, publishing to (Test)PyPI, trusted publishing and
signing, release automation, monorepos, private indexes, and software
supply-chain hygiene (SBOMs and licences).

Shipping matters in AI and data engineering: internal shared libraries,
CLI tools for your team, model-serving packages, plugins for frameworks, and
open-source contributions all depend on this knowledge. Docker packaging and
CI/CD pipelines are covered in Stage 2 (modules 18 and Docker Essentials in
`Python for Data Engineering_2`); this module covers the **Python package
layer** underneath them.

> Target: **Python 3.12+**, `uv` (build/publish), `hatchling`/`setuptools`/`maturin` backends, PyPA standards (PEP 517/518/621/660/740/751).

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain the PEP 517/518 build model and choose a build backend.
- Build and inspect **sdists** and **wheels**, and explain wheel tags and `manylinux`.
- Declare dependencies, extras, dependency groups and console scripts in `pyproject.toml`.
- Create **entry points** for CLIs and for plugin discovery with `importlib.metadata`.
- Publish to **TestPyPI** and PyPI safely using **Trusted Publishing**, with attestations.
- Automate versioning, changelogs and releases.
- Structure namespace packages and monorepos with workspaces.
- Use a **private index**/internal registry and understand dependency confusion.
- Produce an **SBOM**, audit licences and vulnerabilities, and write a release checklist.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Imports, modules, `__main__` | Module 1.6 (01) | Entry points call functions |
| Project layout, `src/` layout | Module 1.6 (02) | Building and testing the installed package |
| `pyproject.toml`, lock files, `uv` | Module 1.6 (03) | Metadata and tooling |
| Semantic versioning, dependency management | Module 1.6 (04) | Versioning policy |
| Docs, READMEs | Module 1.6 (07) | Package long description |
| Release basics, supply-chain awareness | Module 1.10 (07, 08) | Release checklist |
| `tox`/`nox`, testing installed artifacts | Module 1.16 (08) | Pre-publish validation |
| Hashing, signing basics | Module 1.13 (06) | Provenance and attestations |
| Git and GitHub basics | Stage 0 — Module 0.4 (10) | Tags, releases, CI |
| Plugin/registry patterns | Module 1.12 (05) | Entry-point plugins |

**Tools:** `uv` (`uv build`, `uv publish`), `build`, `twine`, `hatchling`, `setuptools`,
`pipx`/`uvx`, `check-wheel-contents`, `auditwheel` (Linux), `cyclonedx-py` or `syft`, `pip-audit`, `pip-licenses`, a GitHub account, and accounts on **TestPyPI** (and PyPI when ready).

---

## 3. How the module is organised

```text
Phase A — Build and Artifacts                    (Basics)
  01 build backends and PEP 517
  02 wheels, sdists and binary compatibility
Phase B — Interfaces to Your Package             (Intermediate)
  03 entry points and console scripts
  04 plugin architectures with entry points
Phase C — Publishing and Releasing               (Intermediate → Advanced)
  05 publishing to TestPyPI and PyPI
  06 trusted publishing and signed releases
  07 versioning, changelogs and release automation
Phase D — Organisations and Supply Chain         (Advanced)
  08 namespace packages and monorepos
  09 private indexes and internal packages
  10 SBOM and licence compliance
```

Pace: about 3 weeks part-time. Use one package, `tinytools`, as the running
example; publish only to **TestPyPI** until the final checklist.

---

## Lesson 01 — `01-build-backends-and-pep-517.md`

**Why it matters.** "How does `pip install .` actually work?" Understanding
the build-frontend/backend split explains confusing errors, slow installs,
and why `setup.py` is no longer the way.

### Basic — what to learn

- Historical context: `setup.py`, `distutils` (removed in 3.12), `setuptools`, `easy_install`, `egg`.
- Standards: **PEP 518** (`[build-system]` table), **PEP 517** (frontend/backend API), **PEP 621**
  (`[project]` metadata), **PEP 660** (editable installs), **PEP 639** (licence expressions).
- Minimal `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "tinytools"
version = "0.1.0"
description = "Small utilities"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
dependencies = ["httpx>=0.27"]

[project.urls]
Homepage = "https://github.com/you/tinytools"
```

- Frontends (`pip`, `uv`, `build`) vs backends (`hatchling`, `setuptools`, `flit-core`, `pdm-backend`, `maturin`, `scikit-build-core`, `poetry-core`).

### Intermediate — what to learn

- What a build does: create an isolated environment, install `requires`, call backend hooks
  (`build_wheel`, `build_sdist`, `get_requires_for_build_wheel`, `prepare_metadata_for_build_wheel`).
- Choosing a backend: pure Python → `hatchling`/`flit-core`/`setuptools`; native Rust → `maturin`;
  C/C++/CMake → `scikit-build-core`; dynamic versions from git tags → `hatch-vcs`/`setuptools-scm`.
- Project metadata fields: `classifiers`, `keywords`, `authors`, `urls`, `optional-dependencies` (extras),
  `dependency-groups` (PEP 735, dev-only), `dynamic`, `readme` content-type, `license-files`.
- Source layout and including data files: `[tool.hatch.build.targets.wheel] packages = ["src/tinytools"]`; `package-data`; `py.typed`.
- Editable installs: `uv pip install -e .` / `pip install -e .` (PEP 660) and their limitations.
- Build isolation and reproducibility: `--no-build-isolation` pitfalls; pinning build requirements.

```bash
uv build                     # creates dist/tinytools-0.1.0.tar.gz and .whl
python -m build --installer uv
```

### Advanced — what to learn

- Writing a **minimal in-tree backend** (`backend-path`) to understand the hook contract (educational).
- Build-time dependency problems: sdists that need compilers/system libs; `build-system.requires` pins; conflicts.
- Dynamic metadata: version from `__version__`, from VCS tags, from a file; trade-offs; ensuring sdist contains the data to rebuild.
- Reproducible builds: `SOURCE_DATE_EPOCH`, deterministic file ordering, avoiding timestamps; verifying by rebuilding.
- Migrating from `setup.py`/`setup.cfg`/Poetry to `[project]` metadata; `uv` project tooling vs older tools.
- PEP 751 `pylock.toml` (standard lock file format) awareness and how it relates to `uv.lock`.
- Security of the build step: build scripts execute code — treat unknown sdists as untrusted; prefer wheels (`--only-binary :all:`).
- Packaging "doctor" checklist: `twine check`, `check-wheel-contents`, `validate-pyproject`, installing the built wheel in a clean venv and importing.

### Common mistakes

- Missing `build-system` (falls back to legacy `setuptools`).
- Forgetting to include non-Python files.
- Testing only the editable install.

### Self-check

1. What is the difference between a build frontend and a build backend?
2. Why does `pip install .` create an isolated environment?
3. Convert a legacy `setup.py` project to `pyproject.toml` with `hatchling` and verify by building both artifacts.

---

## Lesson 02 — `02-wheels-sdists-and-binary-compatibility.md`

**Why it matters.** "Why does this install take 10 minutes and fail with a
compiler error?" — because no compatible wheel existed and `pip` built from
source. Understanding wheel tags explains install speed, reproducibility and
platform support.

### Basic — what to learn

- **sdist** (`.tar.gz`): source + metadata; may require a build. **wheel** (`.whl`): zip with built files, installed by unpacking — no code execution at install time.
- Wheel filename: `{name}-{version}-{python tag}-{abi tag}-{platform tag}.whl`, e.g. `tinytools-0.1.0-py3-none-any.whl` (pure Python) vs `numpy-2.1.0-cp313-cp313-manylinux_2_17_x86_64.whl`.
- Inspect: `unzip -l dist/*.whl`; `METADATA`, `WHEEL`, `RECORD`, `entry_points.txt`.

```bash
uv build
unzip -l dist/tinytools-0.1.0-py3-none-any.whl
uv pip install dist/tinytools-0.1.0-py3-none-any.whl
```

### Intermediate — what to learn

- Compatibility tags: `cp312` (CPython 3.12), `abi3` (stable ABI, one wheel for many versions), `py3-none-any`;
  platform tags `manylinux_2_28`, `musllinux_1_2`, `macosx_11_0_arm64`, `win_amd64`; `cp313t` (free-threaded).
- How installers choose: they rank compatible tags; `pip debug --verbose`; `uv pip install --python-platform`.
- Why wheels are preferred: speed, no compiler, reproducibility, security (no `setup.py` execution).
- `--only-binary :all:`, `--no-binary`, finding missing wheels for new Python versions (the "ecosystem lag").
- Include/exclude rules; what ends up in the sdist vs wheel; `MANIFEST.in` (setuptools) vs backend include patterns.
- Metadata: `Requires-Python`, `Requires-Dist`, `Provides-Extra`, `Classifier`; core metadata spec; dynamic fields.

### Advanced — what to learn

- Building native wheels: `cibuildwheel` (matrix of OS × Python), `auditwheel repair` (vendors shared libs, sets `manylinux` tag), `delocate` (macOS), `delvewheel` (Windows).
- `manylinux` policy: glibc baseline, why you build in old containers; `musllinux` for Alpine; ARM64 builds (cross-compile or native runners).
- Stable ABI (`abi3`) and limited API: fewer wheels, constraints; free-threaded wheel support.
- Wheel size reduction (strip debug symbols, avoid vendoring duplicates, exclude tests/data); PyPI file size limits (and requesting increases).
- Metadata 2.x features (PEP 639 licence expressions, PEP 658 metadata files for fast resolution) and how resolvers use them.
- Installing from VCS/URL/path/index, direct references (`pkg @ git+...`) and why PyPI forbids direct references in uploaded metadata.
- Failure analysis: reading a "no matching distribution" or "failed building wheel" error; fix strategies (pin versions, upgrade pip/uv, install build deps, use conda for binary stacks).
- Verifying wheel contents in CI: install the wheel into a clean environment and run a smoke test (`python -c "import tinytools; ..."`).

### Common mistakes

- Uploading only an sdist for a package with native code.
- Missing `py.typed`/data files in the wheel.
- Building `manylinux` wheels on a modern host distro (wrong glibc baseline).

### Self-check

1. Decode `numpy-2.1.0-cp313-cp313-manylinux_2_17_x86_64.whl`.
2. Why do wheels improve security compared with sdists?
3. Build a wheel, list its contents, and explain each file in `*.dist-info`.

---

## Lesson 03 — `03-entry-points-and-console-scripts.md`

**Why it matters.** `pip install tinytools` should give users a `tinytools`
command on their PATH — a proper CLI, not `python path/to/script.py`.
Entry points are also the mechanism for plugin discovery (next lesson).

### Basic — what to learn

- `[project.scripts]` creates executables: `tinytools = "tinytools.cli:main"` — the function takes no
  required arguments and returns an exit code (or `None`).
- `[project.gui-scripts]` (Windows no-console) awareness.
- Run as module too: `tinytools/__main__.py` so `python -m tinytools` works.

```toml
[project.scripts]
tinytools = "tinytools.cli:main"
```
```python
# tinytools/cli.py
import argparse, sys

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tinytools")
    p.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    p.parse_args(argv)
    print("hello")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

### Intermediate — what to learn

- How scripts are generated at install time: shim executables (`bin/` or `Scripts/`), shebang to the venv interpreter.
- `pipx install tinytools` / `uv tool install tinytools` / `uvx tinytools` for isolated CLI installs; `uv run`.
- `importlib.metadata.version("tinytools")` to expose `--version` from package metadata (single source of truth).
- Return codes: `raise SystemExit(main())` vs returning from `main` (the generated script wraps with `sys.exit(main())`).
- Choosing CLI frameworks: `argparse` (stdlib), `click`, `typer`, `cyclopts`; shell completion; packaging their dependencies.
- Data files and resources inside the package: `importlib.resources.files("tinytools") / "data.json"` (never `__file__` paths).
- Testing the console script: install the wheel and invoke it (Module 1.16 lessons 06, 08).

```python
from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("tinytools")
except PackageNotFoundError:        # running from source tree
    __version__ = "0+unknown"
```

### Advanced — what to learn

- Startup time of CLIs: lazy imports (`import` inside functions), `python -X importtime`, avoiding heavy imports at module top (important for `--help` speed).
- Zipapps (`python -m zipapp`), `shiv`, `pex`, PyInstaller/Nuitka for single-file distribution — when and trade-offs (size, platform specific).
- Cross-platform concerns: Windows `.exe` launchers, PATH issues, `pipx ensurepath`, shebang length limits, user vs system installs (PEP 668 externally-managed environments).
- Security: scripts run with user privileges; avoid `sudo pip`; typosquatting names; careful with `shell=True` in CLI internals (Module 1.13 lesson 04).
- Backwards compatibility of CLI interface: treat command names, flags and exit codes as a public API (Module 1.20); deprecate flags with warnings.
- Multiple commands via subcommands, `python -m` dispatch, `[project.scripts]` aliases.
- Packaging a CLI for a team: internal index + `uv tool install --from`, versions pinned in runbooks, self-update policy.

### Common mistakes

- Using `if __name__ == "__main__"` only and no entry point.
- Reading data files via relative paths.
- Heavy imports slowing every command.

### Self-check

1. What does `tinytools = "tinytools.cli:main"` generate at install time?
2. How can the CLI report its version without hard-coding it twice?
3. Package the sample CLI, install it with `pipx`/`uv tool`, and verify `--help` and exit codes.

---

## Lesson 04 — `04-plugin-architectures-with-entry-points.md`

**Why it matters.** Extensible tools (pytest, Flask, Airflow, dbt, Sphinx,
OpenTelemetry, LangChain integrations) let third parties add behaviour
without modifying the host. Entry points are the standard Python mechanism:
install a package → the host discovers it.

### Basic — what to learn

- Entry point groups: `[project.entry-points."tinytools.formats"]` mapping names to `module:object`.
- Discovery: `importlib.metadata.entry_points(group="tinytools.formats")` returns `EntryPoint` objects; `.load()` imports the target.

```toml
# plugin package: tinytools-yaml/pyproject.toml
[project.entry-points."tinytools.formats"]
yaml = "tinytools_yaml:YamlFormat"
```
```python
# host package
from importlib.metadata import entry_points

def load_formats() -> dict[str, type]:
    return {ep.name: ep.load() for ep in entry_points(group="tinytools.formats")}
```

### Intermediate — what to learn

- Designing the plugin contract: a `Protocol`/ABC (Module 1.11 lesson 10) defining required methods; version the contract (`api_version`).
- Lazy loading: list names without importing; load on demand; error isolation (one broken plugin must not crash the host; log and skip).
- Name collisions & precedence; allow users to select plugins via config/CLI.
- Registration alternatives: `__init_subclass__` registries (Module 1.12 lesson 05) need imports; entry points work across distributions without imports.
- Real examples to read: pytest plugins (`pytest11`), Flask extensions, `console_scripts`, `setuptools.finalize_distribution_options`, Airflow providers, dbt adapters.
- Testing plugin systems: create a tiny plugin package in `tests/`, install it in a temp venv, or build `EntryPoint` objects/`monkeypatch` `entry_points`; contract tests all plugins must pass.
- Documenting how to write a plugin: template repository (`cookiecutter`/`copier`), cookbook.

### Advanced — what to learn

- Security: plugins execute arbitrary code at import → treat installed plugins as trusted code; allow-lists; sandboxing/IPC (separate processes) for untrusted plugins; supply-chain implications.
- Versioning & compatibility: capability negotiation, deprecation of plugin APIs, compatibility matrices, `Requires-Dist: tinytools>=1,<2`.
- Performance: entry-point scanning cost (reads metadata of all installed dists) — caching, restricting groups, avoiding scans on every call.
- Dependency injection for plugins; configuration schemas per plugin (validated); lifecycle hooks (`setup`, `teardown`); ordering and hooks (pluggy library: hook specs/implementations — used by pytest/tox).
- Namespace package alternative (`tinytools_plugins.*`) and its drawbacks.
- Observability: list installed plugins in `--version`/`doctor` command with versions and load status.
- Entry-point misuse: global side effects, import cycles, heavy imports at load.
- Case study: implement a mini `pluggy`-style system with hook specs and ordered execution; compare with writing it directly using entry points.

### Common mistakes

- Plugin import errors crashing the host.
- No versioned contract.
- Scanning entry points repeatedly in hot paths.

### Self-check

1. How does the host discover a plugin it has never imported?
2. How do you stop one failing plugin from taking down the host?
3. Build `tinytools` with two plugin packages (`tinytools-json`, `tinytools-yaml`), a `list-plugins` command, and tests with a fake plugin.

---

## Lesson 05 — `05-publishing-to-testpypi-and-pypi.md`

**Why it matters.** Publishing makes your package installable by anyone
with `pip install` — and publishing is effectively **irreversible** (versions
cannot be reused; deleting doesn't erase history). Practice on TestPyPI and
follow a checklist.

### Basic — what to learn

- PyPI vs TestPyPI (separate databases and accounts); project names, normalisation and name availability.
- Required metadata: unique name, version, README rendering, licence, classifiers, `requires-python`, URLs.
- Build + check + upload (manual first time):

```bash
uv build
uvx twine check dist/*
uv publish --publish-url https://test.pypi.org/legacy/ --token "$TEST_PYPI_TOKEN"
uv pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ tinytools
```

- Install in a clean venv and run a smoke test.

### Intermediate — what to learn

- Authentication: API tokens scoped to a project; 2FA required; never commit tokens; environment variables / keyring / CI secrets.
- Immutability: you cannot overwrite a version; yanking (`yank` with a reason) vs deleting; post-releases (`1.0.0.post1`) and fixing metadata only.
- Pre-releases and PEP 440 versions: `1.0.0a1`, `b1`, `rc1`, `.dev0`, `.post1`, local versions (`+local`) not allowed on PyPI;
  pre-release installation requires `--pre`.
- README as long description (`readme = "README.md"` with content-type), relative links/images (use absolute URLs).
- Project page hygiene: classifiers, `Project-URL`s (Source, Issues, Changelog, Documentation), licence expression, `Development Status`.
- Name squatting, typosquatting, and the PyPI naming policy (`pypi.org/help`); reserve your own names responsibly; prohibition of abandoned-name reuse.
- Release checklist: tests pass on matrix, version bumped, changelog updated, tag created, build from clean checkout, TestPyPI dry run, install test, publish, GitHub release, announce.

### Advanced — what to learn

- Handling mistakes: broken release → yank + post-release/new version; leaked token → revoke immediately; malicious takeover scenarios; owner/maintainer roles on PyPI.
- Organisations and teams on PyPI; project ownership transfer; archived projects and project status markers (PEP 792) plus PyPI's limits on deleting releases (PEP 763).
- Upload API details: `twine` vs `uv publish`; hash verification; `--skip-existing`; uploading multiple artifacts atomically (wheels first or all together).
- Rate limits and size limits (default 100 MB per file; request more if justified); wheel matrix upload ordering.
- Supply-chain expectations from consumers: provenance attestations (next lesson), reproducible builds, pinned build deps, clear security policy (`SECURITY.md`), CVE reporting contacts.
- Alternatives to public PyPI: GitHub Packages, private registries (lesson 09), conda-forge feedstocks, distribution via GitHub releases.
- Licensing choices (MIT/Apache-2.0/BSD/GPL/AGPL), contributor agreements (DCO/CLA), third-party licence notices (lesson 10).
- Long-term maintenance: issue triage, support policy for Python versions, handoff plan, deprecation and sunset messaging.

### Common mistakes

- Publishing from a dirty working tree.
- Hard-coded tokens in CI logs.
- Reusing a version number after failed upload.

### Self-check

1. Why can't you re-upload a file with the same version to PyPI?
2. What is the difference between yanking and deleting a release?
3. Publish `tinytools` to TestPyPI, install it in a fresh environment, and write down every step as a runbook.

---

## Lesson 06 — `06-trusted-publishing-and-signed-releases.md`

**Why it matters.** Long-lived API tokens leak. Trusted Publishing uses
OIDC so your CI proves its identity to PyPI and gets a short-lived token —
no secrets to store. Attestations then let users verify *which repository
and workflow built* each artifact.

### Basic — what to learn

- The problem: stolen tokens, compromised maintainers, malicious uploads.
- **Trusted Publishing (OIDC)**: configure on PyPI ("Add a trusted publisher": owner, repo, workflow file, environment); CI requests an OIDC token; PyPI exchanges it for a short-lived upload token.
- Minimal GitHub Actions publish job (conceptual; CI details are covered in Stage 2):

```yaml
# .github/workflows/release.yml
name: release
on:
  push:
    tags: ["v*"]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv build
      - uses: actions/upload-artifact@v4
        with: {name: dist, path: dist/}
  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi            # protected environment w/ required reviewers
    permissions:
      id-token: write            # required for OIDC
    steps:
      - uses: actions/download-artifact@v4
        with: {name: dist, path: dist/}
      - uses: pypa/gh-action-pypi-publish@release/v1
```

### Intermediate — what to learn

- Protecting the release: GitHub **environments** with required reviewers, tag protection rules, branch protection, least-privilege `permissions`, pinned action versions/SHAs.
- **Attestations** (PEP 740): `pypa/gh-action-pypi-publish` generates and uploads Sigstore-based attestations; consumers can verify provenance (`pypi-attestations`, `pip` support evolving).
- **Sigstore** concepts: keyless signing, Fulcio certificates, Rekor transparency log; `sigstore sign`/`verify`.
- SLSA framework levels (awareness): build provenance, isolated builds, hermetic/reproducible builds.
- Secrets hygiene: remove old tokens after enabling trusted publishing; separate TestPyPI and PyPI publishers.
- 2FA, recovery codes, hardware keys for maintainers; separate "release" identity.

### Advanced — what to learn

- Threat modelling a release pipeline: compromised dependency in the build, malicious PR modifying workflow, cache poisoning, tag hijack, self-hosted runners, `pull_request_target` pitfalls; mitigations (pin by SHA, `harden-runner`, isolated build job without publish permissions — as in the example above).
- Reproducible builds as verification: rebuild from a tag and compare hashes; `diffoscope`.
- Verifying dependencies' provenance in your own installs: `pip-audit`, `uv` hash checking (`--require-hashes`), lock files with hashes, mirror policies.
- Signing other artifacts: container images (`cosign`), git tags/commits (`git tag -s`, SSH/GPG signing), SBOM attestations (lesson 10).
- Incident response: revoke publisher, yank versions, publish advisory (GitHub Security Advisories, GHSA/OSV/PYSEC), notify downstream; post-mortem.
- Policy documents: `SECURITY.md`, release procedure, key/identity management, maintainers' roles, bus-factor mitigation.
- Compare ecosystems: npm provenance, Maven Central signing, Go checksum database — what Python's model provides.
- Exercise: threat-model your own workflow with STRIDE and list 5 mitigations you will apply.

### Common mistakes

- Granting `id-token: write` to every job.
- Publishing from unprotected branches or arbitrary tags.
- Leaving old API tokens active after migration.

### Self-check

1. What does the OIDC exchange prove to PyPI and what secret is no longer needed?
2. Why separate the build job from the publish job?
3. Configure a trusted publisher for TestPyPI, publish a pre-release via CI, and verify the attestation on the project page.

---

## Lesson 07 — `07-versioning-changelogs-and-release-automation.md`

**Why it matters.** Consistent versions and changelogs tell users what
changed and whether upgrading is safe; automation removes manual mistakes
and makes releases boring.

### Basic — what to learn

- Semantic Versioning recap (`MAJOR.MINOR.PATCH`) and PEP 440 mapping; `0.x` instability convention.
- **Single source of truth** for the version: static in `pyproject.toml`, or dynamic from git tags (`hatch-vcs`, `setuptools-scm`), exposed via `importlib.metadata`.
- Changelog format: **Keep a Changelog** (Added/Changed/Deprecated/Removed/Fixed/Security) and linking versions to diffs.
- Git tags: annotated `v1.2.3`; GitHub Releases with notes.

```markdown
## [1.2.0] - 2026-10-14
### Added
- `tinytools convert --format yaml` (#42)
### Deprecated
- `--fmt` flag; use `--format` (removal in 2.0)
```

### Intermediate — what to learn

- Conventional Commits (`feat:`, `fix:`, `feat!:`/`BREAKING CHANGE`) as input for automation; commit linting.
- Tools: `towncrier` (news fragments per PR → changelog), `release-please`, `python-semantic-release`, `bump-my-version`, `commitizen`, `uv version --bump`.
- Release workflow: protected `main` → release PR (bumps version, updates changelog) → merge → tag → CI builds and publishes (lesson 06).
- Pre-release and release-candidate channels; backports to maintenance branches (`1.x`), cherry-picking, patch releases.
- Defining your **public API** for SemVer (what counts as breaking: functions, CLI flags, config keys, exit codes, file formats, minimum Python version, dependency lower bounds).
- Python version support policy and dependency range policy (lower bounds tested — Module 1.16 lesson 08; avoid upper caps unless necessary).
- Release notes for humans: highlights, upgrade notes, migration snippets, contributors.

### Advanced — what to learn

- Calendar versioning (CalVer) vs SemVer: when each fits (data/ML datasets, apps vs libraries, `pip`, `black`, `ubuntu`).
- Versioning non-code artifacts: data schemas, model versions, prompts, configs — link to model registries and data contracts (Stage 2/ML stages); compatibility matrices.
- Breaking-change management: deprecation windows (Module 1.15 lesson 09), compatibility shims, codemods, `FutureWarning` flags for opt-in behaviour.
- Monorepo/multi-package versioning: independent vs lockstep versions, changesets, dependency bump propagation (lesson 08).
- Automated compatibility checks: public-API diff tools (`griffe check`, `api-diff`), type stubs checks, `pip install` of previous versions' tests against the new release.
- Release metrics and quality gates: tests green, coverage, mutation score on core modules, security scan, docs build, wheel smoke tests across OS.
- Rollback strategy: yank, fix-forward, revert tags; communicating incidents.
- Governance: who can release, review requirements, release calendar, LTS lines.

### Common mistakes

- Version defined in three places and drifting.
- Breaking changes in a patch release.
- Changelogs written after the fact from `git log`.

### Self-check

1. Which of these is a breaking change under SemVer: removing a CLI flag, raising the minimum Python version, changing a default? Defend each.
2. Set up `towncrier` (or `release-please`) for `tinytools` and produce a release PR.
3. Write a release checklist that CI enforces automatically.

---

## Lesson 08 — `08-namespace-packages-and-monorepos.md`

**Why it matters.** Organisations split code across many packages
(`company-core`, `company-ml`, `company-etl`) that share a top-level import
namespace, and keep them in one repository for atomic changes. Python's
tooling now supports this well — but the pitfalls are many.

### Basic — what to learn

- **Regular package**: directory with `__init__.py`. **Namespace package** (PEP 420): directory *without* `__init__.py`,
  portions can be spread across multiple distributions/directories (`acme.core`, `acme.ml`).
- Import behaviour: `acme` has no code of its own; each distribution contributes subpackages.
- Typical layouts: `src/acme/core/...` in one distribution, `src/acme/ml/...` in another — no `acme/__init__.py` in either.

```text
acme-core/ pyproject.toml  src/acme/core/__init__.py
acme-ml/   pyproject.toml  src/acme/ml/__init__.py
# pip install acme-core acme-ml  ->  import acme.core, acme.ml
```

### Intermediate — what to learn

- Build configuration for namespace packages (`[tool.hatch.build.targets.wheel] packages = ["src/acme"]`, `setuptools.packages.find` with `namespaces = true`).
- Pitfalls: accidentally adding `__init__.py`, shadowing, editable installs with namespace packages, type checkers/IDEs (`namespace_packages`, `mypy --namespace-packages`, `explicit_package_bases`), pytest import modes (`importmode=importlib`).
- **Monorepos with `uv` workspaces**: root `pyproject.toml` with `[tool.uv.workspace] members = ["packages/*"]`, `{ workspace = true }` sources, single lock file, `uv sync --all-packages`, `uv run --package acme-ml pytest`.
- Alternative tools: Pants, Bazel, Poetry multi-project plugins, Hatch environments; trade-offs.
- Shared dev tooling at root (`ruff`, `pytest`, `mypy` config); per-package tests; CI path filters to test only affected packages.
- Dependency direction rules: `core` ← `ml`/`etl`; forbid cycles (import-linter).

```toml
# root pyproject.toml
[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
acme-core = { workspace = true }
```

### Advanced — what to learn

- Versioning strategies: lockstep releases vs independent versions; internal dependency pinning (`acme-core>=1.4,<2`) vs workspace sources; publishing order and "release train" automation.
- Affected-package detection (git diff → package graph) to keep CI fast; remote caching; build graphs.
- Boundaries and ownership: CODEOWNERS, public API per package (`__all__`, `_internal`), import-linter contracts, architecture tests.
- Large-repo ergonomics: dev containers, one-command setup (`uv sync`), shared pre-commit config, documentation site aggregating packages.
- Migration playbooks: splitting a monolith into packages gradually (strangler pattern), moving modules while keeping import paths via compat shims and deprecation warnings.
- Namespace package gotchas in production: duplicate installs from different indexes, partial uninstalls leaving directories, zipped distributions, frozen apps (PyInstaller).
- Monorepo vs polyrepo decision record: coordination cost, atomic refactors, access control, CI cost, release independence.
- Data/ML monorepo structure: libraries, pipelines, services, notebooks, shared schemas — where each lives and how they depend on each other.

### Common mistakes

- Having `__init__.py` in the shared namespace directory in one distribution (breaks the namespace).
- Circular dependencies between packages.
- CI running everything on every change.

### Self-check

1. What happens if one distribution ships `acme/__init__.py`?
2. Create a two-package namespace workspace and make `import acme.core, acme.ml` work from a clean venv.
3. Write an `import-linter` contract that forbids `acme.core` from importing `acme.ml`.

---

## Lesson 09 — `09-private-indexes-and-internal-packages.md`

**Why it matters.** Companies publish internal libraries (data clients,
feature code, shared models) to private indexes. Misconfiguring index
resolution creates **dependency-confusion** vulnerabilities, a real class of
supply-chain attacks.

### Basic — what to learn

- Options: private PyPI servers (Artifactory, Nexus, AWS CodeArtifact, Google Artifact Registry, Azure Artifacts, GitLab/GitHub Packages, `devpi`, simple static index on object storage).
- The Simple Repository API (PEP 503/691): `/simple/<project>/` links; how installers query indexes.
- Configuring installers: `pip.conf`/`PIP_INDEX_URL`, `uv` `[[tool.uv.index]]` with names and `explicit = true`, `--index-url` vs `--extra-index-url`.

```toml
# pyproject.toml (uv)
[[tool.uv.index]]
name = "internal"
url = "https://pypi.internal.example.com/simple"
explicit = true            # only used for packages pinned to it

[tool.uv.sources]
acme-core = { index = "internal" }
```

### Intermediate — what to learn

- **Dependency confusion**: an attacker publishes a higher-versioned `acme-core` on public PyPI; with `--extra-index-url`, the resolver may prefer it. Mitigations: single trusted proxy index that mirrors PyPI and blocks internal names; explicit index pinning per package; namespace reservation on PyPI; hash-pinned lock files.
- Authentication: tokens in `~/.netrc`, keyring, `UV_INDEX_*` env vars, short-lived cloud credentials (`gcloud`, `aws codeartifact login`), CI secrets; never commit credentials.
- Publishing internally: `uv publish --publish-url`, `twine`, CI jobs with OIDC to the cloud registry; separate indexes for dev/staging/prod channels.
- Proxy/mirror/caching behaviour, allow-lists for upstream packages, quarantine of new releases (cooldown windows), vulnerability scanning on ingest.
- Versioning internal packages: pre-release channels (`.devN`), promotion between indexes, immutability policy, retention.
- Local development: `uv sync`, path/workspace dependencies vs index dependencies; lock files including hashes and index URLs.

### Advanced — what to learn

- Designing an organisation package platform: golden paths (templates), CI that builds/tests/publishes, ownership metadata, deprecation process, discoverability (internal docs/catalog), SLAs.
- Offline and air-gapped installs: `uv pip download`/`pip download` into a wheelhouse, `--no-index --find-links`, vendoring, artifact attestations and hash verification, mirroring policy.
- Supply-chain controls: allow-listing, SBOM generation per release (lesson 10), signature/provenance verification at install time, typosquatting detection, Renovate/Dependabot with grouped updates and cooldowns.
- Security incidents: compromised internal package → revoke, yank, rebuild trust; audit logs; who installed which version where (inventory).
- Large-binary and model artifacts: not in Python packages — use artifact stores/model registries (ML stages); keep wheels small.
- Compatibility with conda/pip mixed environments; Docker build caching with private indexes (BuildKit secrets) — see Stage 2 containers.
- Cost & performance: CDN/caching for CI, rate limits, network failures and retries.
- Write an "internal packaging standard": naming, licences headers, supported Python versions, release cadence, security contact.

### Common mistakes

- `--extra-index-url` with internal package names (dependency confusion).
- Committing index credentials in `pip.conf` or lock files.
- No immutability policy on the internal index.

### Self-check

1. Explain a dependency-confusion attack end to end and two mitigations.
2. Configure `uv` to resolve one package from an internal index only, and show the resulting lock entry.
3. Stand up `devpi` (or a static simple index), publish a package to it, and install from a clean venv.

---

## Lesson 10 — `10-sbom-and-license-compliance.md`

**Why it matters.** Customers, regulators and security teams increasingly
ask: *what exactly is inside this software, and under which licences and
known vulnerabilities?* An **SBOM** (software bill of materials) plus
licence and vulnerability scanning is now a standard release artifact.

### Basic — what to learn

- SBOM = inventory of components (name, version, supplier, hashes, licences, relationships).
- Formats: **CycloneDX** (JSON/XML) and **SPDX** (JSON/tag-value); NTIA minimum elements.
- Generate for a Python project: `cyclonedx-py environment|requirements|poetry|pipenv`, `uv export --format cyclonedx1.5` (where supported), `syft`, `pip-licenses`.
- Vulnerability scanning: `pip-audit` (PyPI advisory DB / OSV), `osv-scanner`, GitHub Dependabot alerts, `safety`.

```bash
uv export --no-dev --format requirements-txt > requirements.txt
uvx pip-audit -r requirements.txt
uvx cyclonedx-py requirements requirements.txt -o sbom.cdx.json
uvx pip-licenses --format=markdown --with-urls
```

### Intermediate — what to learn

- Licence families: permissive (MIT, BSD, Apache-2.0), weak copyleft (LGPL, MPL), strong copyleft (GPL), network copyleft (AGPL), "source-available"/non-commercial licences; SPDX identifiers and expressions (`MIT OR Apache-2.0`); PEP 639 `license` / `license-files` metadata.
- Obligations: attribution/NOTICE files, preserving licence texts, linking and distribution concerns (static vs dynamic, wheels vendoring libs), patent clauses.
- Policy as code: allow/deny lists in CI (`pip-licenses --fail-on`, `liccheck`, `reuse lint` for file-level SPDX headers, `ScanCode`), exceptions process.
- Direct vs transitive dependencies; `uv tree`, `pipdeptree`; reading the dependency graph; pinning and hash-checking.
- Triage of vulnerabilities: reachability (is the vulnerable code path used?), severity (CVSS/EPSS), fix availability, workarounds, VEX statements (vulnerability exploitability exchange).
- Update strategy: Dependabot/Renovate PRs, grouped updates, cooldown/minimum release age to reduce malicious-release risk, automated tests as safety net.
- Attach the SBOM to releases (GitHub release assets, container image attestations with `cosign attest`).

### Advanced — what to learn

- SBOM accuracy problems: environment vs lock file vs built artifact vs container; native libs bundled in wheels (`auditwheel` vendored libs) missing from Python-level SBOMs; OS packages in images (`syft` on images).
- SLSA provenance + SBOM + VEX as a coherent supply-chain story; verifying at deployment (admission policies, `cosign verify-attestation`).
- Regulation & customer demands: US Executive Order 14028, EU Cyber Resilience Act, ISO/IEC 5962 (SPDX), security questionnaires; what evidence to prepare.
- Data/AI specifics: AI-BOM / model cards (datasets, models, licences — RAIL, Llama licence terms, dataset licences), model weights as artifacts with provenance and licence obligations (links to LLMOps/Safety stages).
- Open-source compliance programme: OSPO basics, contribution policy, inbound/outbound licence policy, review gates, record keeping, handling licence conflicts.
- Handling a vulnerable dependency with no fix: pin/patch/fork, mitigations (WAF, config), accept risk with expiry, replace library.
- Incident exercise: a critical CVE drops in a transitive dependency — use the SBOM to find affected services in minutes, produce impact report and rollout plan.
- Writing `SECURITY.md`, `NOTICE`, `THIRD_PARTY_LICENSES`, and a release "compliance" job that fails the build on policy violations.

### Common mistakes

- Treating the SBOM as a one-time document rather than a per-release artifact.
- Ignoring transitive and vendored components.
- Blocking on every low-severity CVE without reachability analysis.

### Self-check

1. What is the difference between CycloneDX and SPDX and which would you pick for vulnerability workflows vs licence compliance?
2. Why can an SBOM generated from `requirements.txt` miss risk present in the shipped wheel/container?
3. Add a CI job that generates an SBOM, runs `pip-audit` and licence checks, and fails on GPL/AGPL in a permissive-only project.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Decode wheel names; fix a broken `pyproject.toml`; explain build isolation; inspect artifacts |
| B | Design entry points for a CLI; define a plugin contract; handle a broken plugin |
| C | TestPyPI runbook; trusted-publishing threat model; SemVer classification of changes |
| D | Namespace package puzzles; dependency-confusion scenario; SBOM/licence policy decisions |

Include 6 **"what went wrong?"** scenarios (yanked release, leaked token, GPL transitive dependency, wrong `manylinux` tag, namespace `__init__.py`, extra-index confusion).

---

## 5. Module mini-project

**Ship `tinytools`** end to end:

1. A `src/`-layout package with a CLI (`tinytools`), a plugin group (`tinytools.formats`), `py.typed`, resources via `importlib.resources`.
2. `pyproject.toml` with `hatchling`, extras, dependency groups, classifiers, licence expression.
3. Two plugin distributions (`tinytools-json`, `tinytools-yaml`) in a `uv` workspace monorepo; a namespace-free design with entry points.
4. `nox` sessions that build the wheel, install it in a clean env and run the test suite and CLI smoke tests (Module 1.16).
5. A GitHub Actions workflow: tests on 3.12–3.14 → build → publish to **TestPyPI via Trusted Publishing** with attestations, protected environment, least-privilege permissions.
6. Release automation: Conventional Commits + `release-please` or `towncrier`, version from one source, changelog, tag and GitHub Release.
7. A CI job producing a CycloneDX SBOM, `pip-audit` report and licence report as release assets.
8. `RELEASING.md` (runbook incl. rollback/yank), `SECURITY.md`, `CONTRIBUTING.md`.
9. Optional: a local `devpi`/simple-index demo plus a written dependency-confusion threat assessment.

Acceptance: a fresh machine can `uvx --index-url <testpypi> tinytools --help`; wheels pass `twine check`/`check-wheel-contents`; releases are fully automated and reproducible; the threat model lists mitigations implemented.

---

## 6. Completion checklist

- [ ] I can explain PEP 517/518 and choose a build backend.
- [ ] I can build and inspect wheels and sdists and decode wheel tags.
- [ ] I can ship a CLI via entry points and package data safely.
- [ ] I can design and test a plugin system using entry points.
- [ ] I can publish to TestPyPI and PyPI following a checklist.
- [ ] I use Trusted Publishing with attestations and protected releases.
- [ ] I automate versioning, changelogs and releases with a clear SemVer policy.
- [ ] I can structure namespace packages and a `uv` workspace monorepo.
- [ ] I can configure private indexes and prevent dependency confusion.
- [ ] I can produce SBOMs and enforce licence and vulnerability policies.
- [ ] I completed the `tinytools` mini-project.

**Next:** Module 1.19 — CPython Internals and Runtime Behaviour.
