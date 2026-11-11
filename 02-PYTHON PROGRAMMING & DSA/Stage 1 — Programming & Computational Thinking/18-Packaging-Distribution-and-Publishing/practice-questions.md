# Module 1.18 — Packaging, Distribution and Publishing
## Practice Questions, Answer Key, and Evaluation Rubric

**Curriculum location:** Stage 1 — Programming & Computational Thinking → `18-Packaging-Distribution-and-Publishing/`  
**Source of truth:** `Roadmap_ptree.md` defines the target path and the ten lesson filenames; `roadmap-Packaging-Distribution-and-Publishing.md` defines scope, sequence, outcomes, common mistakes, and self-checks.  
**Baseline:** Python 3.12+, `uv`, and PyPA packaging standards. Tool-specific behavior can vary by installed version; verify CLI help and official documentation before applying commands to a release.  
**Question count:** 35 · **Suggested score:** 100 points · **Phases:** A → B → C → D.

## How to use this document

1. Attempt the question bank before opening the answer key.
2. For code and configuration tasks, submit the artifact, the command(s) used to validate it, and the observed output. Do not claim a build, publication, scan, or CI run unless you actually performed it.
3. For design and security questions, identify assumptions, trust boundaries, failure modes, and trade-offs. A named tool alone is not a complete answer.
4. The answer key gives one model solution. Equivalent approaches are acceptable when they satisfy the stated requirements and safety constraints.
5. External accounts are **not** required for the conceptual questions. Questions involving TestPyPI, GitHub Actions, OIDC, Linux wheel inspection, or a registry explicitly state their prerequisites.

### Phase plan

| Phase | Lessons | Questions | Points | Focus |
|---|---|---:|---:|---|
| A — Build and Artifacts | 01–02 | Q01–Q09 | 26 | Build standards, metadata, artifacts, tags, clean installs |
| B — Interfaces to Your Package | 03–04 | Q10–Q15 | 17 | CLI entry points, metadata, resources, plugin contracts |
| C — Publishing and Releasing | 05–07 | Q16–Q24 | 25 | Publishing, trusted publishing, provenance, versioning, release recovery |
| D — Organisations and Supply Chain | 08–10 | Q25–Q35 | 32 | Namespace/workspaces, private indexes, SBOM, license and vulnerability policy |
| **Total** | **All 10 lessons** | **35** | **100** | |

Difficulty is tagged on each question: **Beginner**, **Intermediate**, or **Advanced**. Phase order intentionally follows the module roadmap.

---

# Part I — Question Bank

## Phase A — Build and Artifacts

### Q01 — Frontend, backend, and build isolation
- **Lesson:** `01-build-backends-and-pep-517.md`
- **Difficulty:** Beginner
- **Type:** Conceptual comparison
- **Points:** 2

**Question**

Explain the difference between a build frontend and a build backend. Describe the roles of PEP 517 and PEP 518, and explain why `pip install .` commonly builds in an isolated environment.

**Expected answer format:** 150–250 words or a labelled flow diagram.

**Evaluation criteria:** Correctly distinguishes the caller/orchestrator from the build implementation; explains backend hooks and build-system requirements; identifies isolation as a way to install declared build requirements without relying on the ambient environment; mentions that build code still executes and is not automatically trustworthy.

### Q02 — Repair a `pyproject.toml`
- **Lesson:** `01-build-backends-and-pep-517.md`
- **Difficulty:** Intermediate
- **Type:** Configuration debugging
- **Points:** 3

**Question**

The following legacy project should be migrated to Hatchling, require Python 3.12+, publish a `tinytools` distribution, and declare an MIT license. Identify the defects and provide a corrected `pyproject.toml`. Explain how you would verify that both the wheel and sdist build.

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "setuptools.build_meta"

[project]
name = "tinytools"
version = "0.1.0"
requires-python = ">=3.12"
license = "MIT"
dependencies = ["httpx>=0.27"]
```

**Expected deliverable:** Correct TOML plus a short explanation. Assume the project has a `src/tinytools/` package and a compatible Hatchling version is available.

**Evaluation criteria:** Backend and build requirements agree; metadata is valid for the chosen tooling; package discovery/build configuration is included if required by the chosen Hatchling setup; license metadata is treated according to the project's supported PEP 639/tool version rather than guessed; no unrelated runtime dependencies are added.

### Q03 — Dynamic metadata and reproducible builds
- **Lesson:** `01-build-backends-and-pep-517.md`
- **Difficulty:** Advanced
- **Type:** Design/trade-off analysis
- **Points:** 3

**Question**

A package gets its version from a Git tag using a VCS plugin. A source distribution builds correctly in the maintainer's checkout but fails to rebuild in an offline release environment because the `.git` directory is absent. Explain the failure and propose a robust release design. Include build isolation, source-distribution contents, build-requirement pinning, and reproducibility checks in your answer.

**Expected deliverable:** Root-cause analysis and a release checklist.

**Evaluation criteria:** Explains why VCS-derived metadata can depend on checkout state; ensures the sdist contains the necessary generated/version metadata or has a documented supported versioning path; pins or constrains build requirements appropriately; distinguishes repeatable inputs from byte-for-byte reproducibility; proposes rebuilding and comparing artifacts where feasible.

### Q04 — Decode a wheel filename
- **Lesson:** `02-wheels-sdists-and-binary-compatibility.md`
- **Difficulty:** Beginner
- **Type:** Code/filename reading
- **Points:** 2

**Question**

Decode this wheel filename and state what it does—and does not—tell you:

`numpy-2.1.0-cp313-cp313-manylinux_2_17_x86_64.whl`

**Expected answer format:** Explain distribution/version, Python tag, ABI tag, platform tag, and compatibility implications.

**Evaluation criteria:** Correctly identifies distribution `numpy`, version `2.1.0`, CPython 3.13 (`cp313`), the CPython 3.13 ABI (`cp313`), and the `manylinux_2_17_x86_64` Linux x86-64 platform tag (glibc 2.17 compatibility baseline); notes that the filename does not prove the wheel is safe, correctly built, or compatible with every Linux system.

### Q05 — Wheel versus sdist and native compatibility
- **Lesson:** `02-wheels-sdists-and-binary-compatibility.md`
- **Difficulty:** Intermediate
- **Type:** Comparison/scenario
- **Points:** 3

**Question**

A package installs quickly on a glibc-based Linux CI runner but fails on Alpine Linux with a native-library error. Explain the likely wheel-tag/runtime-library issue and compare the roles of wheels, sdists, `manylinux`, `musllinux`, and tools such as `auditwheel`.

**Expected answer format:** Root-cause hypothesis, verification commands/tools, and at least two remediation options.

**Evaluation criteria:** Recognizes Alpine's usual musl libc versus glibc-based manylinux assumptions; explains why prebuilt wheels can reduce exposure to arbitrary source-build execution (but are not inherently trustworthy); checks actual wheel tags and bundled/external libraries; does not claim `auditwheel` magically makes every wheel portable; suggests a compatible musllinux wheel, a supported source build with toolchain, or a documented platform constraint.

### Q06 — Inspect artifacts, not just the checkout
- **Lesson:** `02-wheels-sdists-and-binary-compatibility.md`
- **Difficulty:** Intermediate
- **Type:** Command-line/hands-on
- **Points:** 3

**Question**

Create a reproducible validation sequence for a `src/`-layout pure-Python package that builds both a wheel and an sdist. Include artifact listing, metadata/archive inspection, wheel-content validation, and installation/import testing in a fresh environment. State what each step can catch.

**Prerequisites:** Python 3.12+, `uv`, and optionally `twine` and `check-wheel-contents` installed in a tooling environment.

**Expected deliverable:** Commands and acceptance criteria; do not upload anything.

**Evaluation criteria:** Uses `uv build` or an equivalent build frontend; inspects `dist/`; runs `twine check` and/or `check-wheel-contents` where available; lists wheel contents and explains key `*.dist-info` files (METADATA, WHEEL, RECORD, and entry_points.txt if present); creates a clean venv and installs the built wheel rather than relying on editable mode; imports the installed package from outside the repository; verifies expected resources/files are present.

### Q07 — PEP map and metadata choices
- **Lesson:** `01-build-backends-and-pep-517.md`
- **Difficulty:** Intermediate
- **Type:** Standards comparison
- **Points:** 3

**Question**

Match each standard to its primary concern: PEP 517, 518, 621, 660, 639, 735, and 751. Then explain the distinction between runtime dependencies, optional extras, and development dependency groups. What should a project do when a tool's support for a standard varies by version?

**Expected answer format:** A compact table and one example use case for each dependency category.

**Evaluation criteria:** Correctly identifies frontend/backend API, build-system requirements, project metadata, editable installs, license metadata/files, dependency groups, and standardized lock-file format awareness; does not claim all tools implement every standard identically; recommends checking supported versions and generated metadata.

### Q08 — Missing package data
- **Lesson:** `01-build-backends-and-pep-517.md`; `02-wheels-sdists-and-binary-compatibility.md`
- **Difficulty:** Intermediate
- **Type:** Debugging
- **Points:** 3

**Question**

Tests pass from the repository, but the installed wheel raises `FileNotFoundError` for `tinytools/templates/default.json`. The file exists under `src/tinytools/templates/`. Describe how you would inspect the wheel, correct package-data configuration, and load the resource portably. Include a regression test that exercises the installed distribution.

**Expected deliverable:** Diagnostic commands, corrected configuration concept, and a Python test/example.

**Evaluation criteria:** Inspects the wheel archive; configures the selected backend to include the resource; recommends `importlib.resources` rather than assuming a filesystem path beside source code; validates the built wheel in a clean environment.

### Q09 — Build security and legacy migration
- **Lesson:** `01-build-backends-and-pep-517.md`; `02-wheels-sdists-and-binary-compatibility.md`
- **Difficulty:** Advanced
- **Type:** Security review
- **Points:** 4

**Question**

A CI job installs an unknown source distribution with `--no-build-isolation` to make the build faster, then publishes the resulting wheel using a long-lived upload token. Identify at least four distinct risks and redesign the pipeline. Your answer must distinguish build isolation, build dependency control, artifact validation, and publication credentials.

**Expected deliverable:** Threat model and staged CI design.

**Evaluation criteria:** Recognizes that building source executes build code; notes `--no-build-isolation` can use unintended ambient dependencies; proposes trusted/pinned build inputs and clean build jobs; validates artifacts before publication; separates untrusted PR jobs from publishing jobs; prefers Trusted Publishing/OIDC where supported or tightly scoped secrets otherwise.

## Phase B — Interfaces to Your Package

### Q10 — Console scripts and exit codes
- **Lesson:** `03-entry-points-and-console-scripts.md`
- **Difficulty:** Beginner
- **Type:** Conceptual/code reading
- **Points:** 2

**Question**

What does a declaration such as `tinytools = "tinytools.cli:main"` generate at install time? Compare the installed console script with `python -m tinytools`. Explain how the CLI can report its version without hard-coding it twice, how it should report exit status, and how you would install/test it with `pipx` or `uv tool`.

**Expected answer format:** Short explanation plus a minimal test strategy.

**Evaluation criteria:** Explains generated entry-point wrapper behavior and the `module:callable` target; recognizes `sys.exit(main())`/return codes; uses `importlib.metadata.version` for installed version lookup; distinguishes output assertions from process exit-code assertions; describes a `pipx`/`uv tool` install smoke test; allows `python -m` when `__main__.py` is intentionally supported.

### Q11 — Version lookup and package resources
- **Lesson:** `03-entry-points-and-console-scripts.md`
- **Difficulty:** Intermediate
- **Type:** Implementation
- **Points:** 3

**Question**

Write a small function that reports the installed distribution version of `tinytools` using `importlib.metadata`, and show how the CLI should behave if the distribution metadata is absent. Also outline how the package should read an embedded `data/schema.json` resource without relying on the current working directory.

**Expected deliverable:** Python snippet and two tests.

**Evaluation criteria:** Uses `importlib.metadata.version` and handles `PackageNotFoundError` intentionally; avoids silently reporting an invented version; uses `importlib.resources` for packaged resources; tests normal and missing-metadata/resource cases.

### Q12 — Entry-point plugin discovery
- **Lesson:** `04-plugin-architectures-with-entry-points.md`
- **Difficulty:** Intermediate
- **Type:** Configuration/code reading
- **Points:** 3

**Question**

A plugin distribution declares this metadata:

```toml
[project.entry-points."tinytools.formats"]
json = "tinytools_json.plugin:JsonFormat"
```

Explain how a host discovers the plugin group with `importlib.metadata`, loads the selected entry point, and validates that the loaded object follows the host's plugin contract. Include one failure mode for a broken plugin.

**Expected deliverable:** Pseudocode or Python code plus error-handling notes.

**Evaluation criteria:** Uses the correct group name; separates metadata enumeration from loading; validates required methods/attributes or a protocol; catches and reports per-plugin load/initialization errors without making false guarantees that arbitrary plugin code is safe.

### Q13 — Plugin contract, compatibility, and lazy loading
- **Lesson:** `04-plugin-architectures-with-entry-points.md`
- **Difficulty:** Advanced
- **Type:** Architecture/design
- **Points:** 3

**Question**

Design a plugin contract for `tinytools.formats` that supports third-party packages. Address API versioning, capability validation, lazy loading, error isolation, naming collisions, testability, and how the host should communicate incompatible plugins. Explain why entry-point discovery is not a security sandbox.

**Expected deliverable:** Contract sketch, discovery lifecycle, and test plan.

**Evaluation criteria:** Defines a narrow documented contract; avoids importing every plugin during unrelated startup paths; specifies compatibility behavior and actionable diagnostics; isolates failures at sensible boundaries; acknowledges plugins execute with the host process's privileges and recommends trust/permission controls for untrusted plugins.

### Q14 — Test a plugin independently
- **Lesson:** `04-plugin-architectures-with-entry-points.md`
- **Difficulty:** Intermediate
- **Type:** Hands-on implementation
- **Points:** 3

**Question**

Create two plugin distributions, `tinytools-json` and `tinytools-yaml`, that register the `tinytools.formats` entry-point group. Add a `list-plugins` host command. Install the built wheels into a clean environment and demonstrate discovery, contract validation, and smoke tests without importing plugins directly from their source checkouts. Include a fake plugin in tests to exercise a broken or incompatible implementation.

**Prerequisites:** Local Python build tooling; no public publication required.

**Acceptance criteria:** Both wheels contain their plugin modules and entry-point metadata; `list-plugins` discovers both expected names/groups; the host can invoke both; a fake incompatible or broken plugin yields a useful failure rather than an unexplained traceback.

### Q15 — Six “what went wrong?”: plugin trust and CLI packaging
- **Lesson:** `03-entry-points-and-console-scripts.md`; `04-plugin-architectures-with-entry-points.md`
- **Difficulty:** Advanced
- **Type:** Debugging/security scenario
- **Points:** 3

**Question**

The `tinytools` command works in a developer checkout but not after installation. In another incident, startup fails because one optional plugin raises during import. Give a prioritized investigation for both incidents and identify the design changes that prevent recurrence.

**Expected deliverable:** Two incident checklists with commands/tests and design mitigations.

**Evaluation criteria:** Checks built wheel contents, installed metadata, script installation/path, callable target, clean-environment behavior, and exit code; checks plugin entry-point group, import path, dependency availability, and load timing; recommends artifact-level smoke tests and per-plugin error reporting/lazy loading.

## Phase C — Publishing and Releasing

### Q16 — TestPyPI release runbook
- **Lesson:** `05-publishing-to-testpypi-and-pypi.md`
- **Difficulty:** Intermediate
- **Type:** Hands-on/command line
- **Points:** 3

**Question**

Write a release runbook that builds `tinytools` and publishes to TestPyPI before any PyPI release. Include artifact validation, version uniqueness, credentials handling, installation from TestPyPI, and a clean-environment smoke test. Do not actually publish unless you have explicit authorization and a configured account.

**Prerequisites:** Optional TestPyPI account and a test-only credential or Trusted Publishing setup; otherwise submit a dry-run runbook.

**Expected deliverable:** Ordered commands/checklist and pass/fail criteria.

**Evaluation criteria:** Builds both expected artifacts; runs metadata/artifact checks; verifies the version and repository target; keeps credentials out of shell history/source control; installs from the intended index in a clean environment; confirms the package CLI/import works; does not confuse TestPyPI with production PyPI.

### Q17 — Token leak response
- **Lesson:** `05-publishing-to-testpypi-and-pypi.md`; `06-trusted-publishing-and-signed-releases.md`
- **Difficulty:** Advanced
- **Type:** Security incident
- **Points:** 3

**Question**

A developer accidentally commits a PyPI API token to a public repository. The token was removed in a later commit. Describe immediate containment and investigation steps, and explain why deleting the visible line is insufficient. Compare long-lived token publishing with Trusted Publishing.

**Expected deliverable:** Prioritized incident response and prevention controls.

**Evaluation criteria:** Revokes/rotates the credential immediately; checks audit/release activity and potentially affected packages; treats Git history and clones as exposed; removes the secret from history where appropriate but does not rely on history rewrite as containment; scopes credentials and prefers OIDC-based Trusted Publishing where supported.

### Q18 — Trusted Publishing, signing, and provenance
- **Lesson:** `06-trusted-publishing-and-signed-releases.md`
- **Difficulty:** Advanced
- **Type:** Security architecture
- **Points:** 3

**Question**

Explain the role of OIDC in Trusted Publishing and distinguish authentication to a package registry from artifact signing, attestations, and provenance. List at least three claims an attestation may help a verifier evaluate and at least three things it does not prove by itself.

**Expected answer format:** Trust-flow diagram or structured bullets.

**Evaluation criteria:** Describes short-lived identity exchange bound to a trusted workflow/repository/environment according to provider configuration; distinguishes who may publish from evidence about how an artifact was built; avoids equating a signature with safe code; notes that claims depend on the attestation format, identity, workflow, and verifier policy.

### Q19 — SemVer versus PEP 440
- **Lesson:** `07-versioning-changelogs-and-release-automation.md`
- **Difficulty:** Intermediate
- **Type:** Comparison/scenario
- **Points:** 3

**Question**

For each change, recommend a versioning/release decision and explain it: (a) adding an optional public function; (b) removing a documented public function or CLI flag; (c) raising the minimum supported Python version; (d) changing a documented default; (e) fixing a bug without changing the documented API; (f) publishing a pre-release candidate for `2.0`; (g) a downstream project needs to accept `1.4.0rc1` but reject stable versions below `1.4.0`. Explain where SemVer guidance and PEP 440 syntax differ.

**Expected deliverable:** Table of change, compatibility impact, version suggestion, and rationale.

**Evaluation criteria:** Reasons about public API compatibility; understands SemVer's major/minor/patch intent and PEP 440's Python-specific version/pre-release ordering; does not assume all version strings have identical syntax or resolver semantics; gives a defensible policy rather than presenting one policy as universally mandatory.

### Q20 — Changelog and release automation
- **Lesson:** `07-versioning-changelogs-and-release-automation.md`
- **Difficulty:** Intermediate
- **Type:** Configuration/design
- **Points:** 3

**Question**

Design a minimal release process using Conventional Commits plus either `release-please` or `towncrier`, including the release PR/changelog update. Explain how the version, changelog, Git tag, build artifacts, and GitHub Release remain consistent. Include safeguards against publishing a tag that points to an unvalidated commit and list checks CI should enforce automatically.

**Expected deliverable:** Workflow outline and release invariants.

**Evaluation criteria:** Defines one authoritative version/changelog path; tests and builds the tagged commit; validates artifacts before publication; uses protected permissions/approvals where appropriate; preserves traceability between commit, tag, artifacts, and release assets.

### Q21 — Yanking and a faulty release
- **Lesson:** `05-publishing-to-testpypi-and-pypi.md`; `07-versioning-changelogs-and-release-automation.md`
- **Difficulty:** Advanced
- **Type:** Incident response
- **Points:** 3

**Question**

Version `1.8.2` of a library contains a regression and has already been downloaded by customers. Propose a recovery plan covering yanking, a corrected release, dependency constraints, communication, and audit evidence. Explain what yanking does not do.

**Expected deliverable:** Timeline from detection to verified recovery.

**Evaluation criteria:** Stops further promotion; assesses severity and affected users; uses yanking where supported to discourage new resolution while recognizing existing installs/caches are not removed; publishes a corrected new version rather than trying to overwrite an immutable release; communicates upgrade guidance and retains evidence.

### Q22 — Six “what went wrong?”: release and provenance
- **Lesson:** `05-publishing-to-testpypi-and-pypi.md`; `06-trusted-publishing-and-signed-releases.md`; `07-versioning-changelogs-and-release-automation.md`
- **Difficulty:** Advanced
- **Type:** Security/debugging
- **Points:** 3

**Question**

A release workflow can be triggered by pull requests from forks, has write permissions for every job, and publishes whatever files happen to be in `dist/`. Identify the attack paths and redesign the workflow's trust boundaries. Include artifact provenance and a rollback plan.

**Expected deliverable:** Threat model and staged workflow diagram.

**Evaluation criteria:** Separates untrusted validation from privileged publication; uses least-privilege job permissions and protected environments/tags; builds from a reviewed immutable commit; validates the exact artifacts that will be published; uses Trusted Publishing and attestations where supported; defines incident response/release recovery.

### Q23 — Backward compatibility and deprecation
- **Lesson:** `07-versioning-changelogs-and-release-automation.md`
- **Difficulty:** Intermediate
- **Type:** Scenario-based design
- **Points:** 2

**Question**

A public function's behavior must change because the old behavior is unsafe. Design a deprecation/migration plan that balances compatibility, security urgency, release notes, and support for downstream users. State when a breaking change may need to happen sooner than a normal deprecation schedule.

**Expected answer format:** Short migration plan and release-note outline.

**Evaluation criteria:** Identifies callers and behavioral contract; documents migration path and timeline; adds tests/warnings where appropriate; uses a versioning policy consistently; recognizes that urgent security remediation may justify accelerated breaking change with explicit communication.

### Q24 — Release evidence package
- **Lesson:** `05-publishing-to-testpypi-and-pypi.md`; `06-trusted-publishing-and-signed-releases.md`; `07-versioning-changelogs-and-release-automation.md`
- **Difficulty:** Advanced
- **Type:** Production-readiness assessment
- **Points:** 2

**Question**

Define the minimum evidence bundle you would retain for a release so that another engineer can establish what source was released, what artifacts were published, which validation ran, and which identity published them. Explain the limits of hashes, signatures, and provenance.

**Expected deliverable:** Evidence checklist.

**Evaluation criteria:** Includes source commit/tag, version, artifact names and cryptographic hashes, test/build logs or summaries, workflow identity/run, publication destination/time, SBOM or attestation where used, and incident contact; correctly explains that hashes establish byte identity, signatures bind identity to signed data, and provenance supports—but does not guarantee—trust in build inputs/process.

## Phase D — Organisations and Supply Chain

### Q25 — PEP 420 namespace packages and monorepos
- **Lesson:** `08-namespace-packages-and-monorepos.md`
- **Difficulty:** Intermediate
- **Type:** Configuration/design
- **Points:** 3

**Question**

Two distributions, `acme-core` and `acme-ml`, both provide modules under `acme/`. Explain how an implicit namespace package works, why neither distribution should normally ship `acme/__init__.py` for this design, and how a workspace helps coordinate development without forcing lockstep releases.

**Expected deliverable:** Package-tree sketch, build-discovery notes, and release strategy comparison.

**Evaluation criteria:** Correctly describes PEP 420 namespace portions; identifies a regular root `__init__.py` as a potential namespace-breaking conflict; separates distribution names from import package names; explains workspace/lockfile trade-offs and independent versus lockstep versioning.

### Q26 — Dependency confusion and registry controls
- **Lesson:** `09-private-indexes-and-internal-packages.md`
- **Difficulty:** Advanced
- **Type:** Security scenario
- **Points:** 3

**Question**

An organization installs `acme-analytics` from an internal registry but also configures the public index as an extra index. An attacker uploads a higher-version public project with that name. Explain the dependency-confusion path and give at least three mitigations. Distinguish package-manager selection policy from registry access controls.

**Expected deliverable:** Attack sequence and prioritized mitigations.

**Evaluation criteria:** Explains that unsafe multi-index resolution can select the attacker-controlled public candidate depending on tool/policy; proposes explicit package-to-index mapping or a single controlled proxy/registry, private-name governance, upstream allowlists/quarantine, and source verification; does not claim an extra index is automatically a safe fallback.

### Q27 — Lockfile and source verification
- **Lesson:** `09-private-indexes-and-internal-packages.md`
- **Difficulty:** Intermediate
- **Type:** Configuration/diagnostic
- **Points:** 3

**Question**

Show how you would configure `uv` so `acme-analytics` resolves from an internal index only. Describe what you would inspect in `uv.lock` and what a lockfile does not guarantee. Use placeholder internal URLs and no real credentials.

**Expected deliverable:** `pyproject.toml` fragment, lock/update commands, and source-verification checklist.

**Evaluation criteria:** Uses a named index and explicit package source mapping consistent with the documented `uv` version; avoids unsafe public-plus-private fallback assumptions; inspects the resolved source and hashes in the lockfile; notes that a lockfile cannot by itself establish the publisher's legitimacy, prevent compromise of an authorized registry, or validate source code.

### Q28 — Internal package publishing lab
- **Lesson:** `09-private-indexes-and-internal-packages.md`
- **Difficulty:** Intermediate
- **Type:** Hands-on implementation
- **Points:** 3

**Question**

Set up a local `devpi` instance or a static Simple API index, build and publish a toy package, and install it from a clean virtual environment. Document package ownership, authentication, source selection, and verification that the installed package came from the intended index.

**Prerequisites:** Local environment and network loopback access; use a disposable test registry and a non-sensitive toy package. Do not expose the service publicly.

**Acceptance criteria:** A wheel is built and listed by the test index; clean-venv installation succeeds with an explicitly selected source; import/version checks pass; registry credentials are not committed; the report includes exact tool versions and explains how registry/source provenance was verified.

### Q29 — SBOM format and inventory scope
- **Lesson:** `10-sbom-and-license-compliance.md`
- **Difficulty:** Intermediate
- **Type:** Comparison/analysis
- **Points:** 3

**Question**

Compare CycloneDX and SPDX for vulnerability workflows and license compliance. Explain why an SBOM generated from `requirements.txt` may miss risk in the final wheel or container, and distinguish a dependency declaration, resolved environment, built distribution, and shipped application.

**Expected deliverable:** Comparison table and four-stage inventory diagram.

**Evaluation criteria:** Describes both as SBOM standards with different ecosystems/features rather than asserting one is universally superior; includes direct/transitive components, identity, version, relationships, hashes/licensing where available; identifies vendored/native libraries and OS packages as potential gaps; recommends artifact/container-aware inventory for shipped outputs.

### Q30 — License policy and scanner limitations
- **Lesson:** `10-sbom-and-license-compliance.md`
- **Difficulty:** Advanced
- **Type:** Policy/code design
- **Points:** 3

**Question**

A project follows a permissive-only license policy. Design a CI gate that generates an SBOM, runs `pip-audit`, produces a license report, and fails on GPL/AGPL findings. Explain how you handle unknown or conflicting license metadata and why the gate's result is evidence for review rather than a definitive legal conclusion.

**Expected deliverable:** CI job outline, policy configuration approach, exception process, and limitations.

**Evaluation criteria:** Scans the intended resolved environment/artifact; keeps SBOM, audit report, license report, and tool versions as release evidence; defines deny/allow/unknown behavior explicitly; requires a documented, scoped, expiring exception with owner/reviewer; does not rely solely on package metadata or claim scanners decide legal obligations.

### Q31 — Vulnerability triage and VEX-style reasoning
- **Lesson:** `10-sbom-and-license-compliance.md`
- **Difficulty:** Advanced
- **Type:** Incident analysis
- **Points:** 3

**Question**

A critical CVE appears in a transitive dependency used by three services. The SBOM identifies the component, but the affected code path may not be reachable in one service. Create a triage and remediation plan that addresses severity, exploitability/reachability, fix availability, mitigations, exceptions, and communication. Explain how a VEX statement may help and what evidence is needed to support it.

**Expected deliverable:** Service impact matrix and rollout plan.

**Evaluation criteria:** Uses the SBOM to enumerate affected releases/services; does not dismiss the CVE solely because it appears unreachable; prioritizes by severity, exposure, reachability, and available fixes; includes update/patch/fork/mitigate options, verification tests, time-bounded risk acceptance, and a defensible record of VEX rationale where used.

### Q32 — Six “what went wrong?” scenarios
- **Lessons:** `02-wheels-sdists-and-binary-compatibility.md`; `07-versioning-changelogs-and-release-automation.md`; `08-namespace-packages-and-monorepos.md`; `09-private-indexes-and-internal-packages.md`; `10-sbom-and-license-compliance.md`
- **Difficulty:** Advanced
- **Type:** Multi-incident debugging
- **Points:** 3

**Question**

For each incident below, give the likely cause, one verification step, and one corrective action:

1. A release was yanked, but an existing deployment still runs the vulnerable version.
2. A publishing token appeared in Git history.
3. A GPL-licensed transitive dependency appears in a permissive-only project.
4. A wheel tagged for one Linux libc/platform fails on another.
5. Adding `acme/__init__.py` breaks a shared namespace package.
6. A private package name resolves to a public distribution after an index configuration change.

**Expected deliverable:** Six-row incident table.

**Evaluation criteria:** Correctly separates resolution behavior from installed-state remediation; revokes exposed credentials; triggers license review rather than assuming scanner metadata settles legality; checks wheel tags/runtime libraries; restores PEP 420-compatible package discovery; hardens source selection and registry controls.

### Q33 — Organization-wide packaging and supply-chain standard
- **Lessons:** `08-namespace-packages-and-monorepos.md`; `09-private-indexes-and-internal-packages.md`; `10-sbom-and-license-compliance.md`
- **Difficulty:** Advanced
- **Type:** Architecture/design
- **Points:** 3

**Question**

Design an internal Python packaging standard for a data/ML organization. Cover ownership, naming, supported Python versions, package index policy, versioning, immutable releases, SBOM/license/vulnerability gates, deprecation, incident contacts, and large model/data artifacts. Include monorepo-versus-polyrepo decision criteria.

**Expected deliverable:** One-page standard outline and decision table.

**Evaluation criteria:** Assigns clear ownership and release responsibilities; controls public/private source selection; separates Python packages from large model/data artifact registries where appropriate; defines release evidence and exception handling; explains operational trade-offs rather than asserting one repository topology is always best.

### Q34 — CI release compliance job
- **Lesson:** `10-sbom-and-license-compliance.md`
- **Difficulty:** Advanced
- **Type:** Hands-on implementation
- **Points:** 3

**Question**

Implement or specify a CI job for a built Python package that (1) builds and validates wheel/sdist artifacts, (2) generates a CycloneDX SBOM, (3) runs `pip-audit`, (4) generates a license report and enforces the GPL/AGPL policy, and (5) archives reports with the release. Define how failures and exceptions are handled.

**Prerequisites:** CI runner with Python and package tooling; registry credentials are not needed for a local build/scan. Exact CLI flags must be checked against the selected versions of `cyclonedx-py`, `pip-audit`, and `pip-licenses`.

**Acceptance criteria:** Job is reproducible and fails closed for policy violations; scans a documented dependency scope; stores SBOM and reports with the exact version/commit; records tool versions; distinguishes security findings from license findings; exception approvals are auditable and expire; no claim of successful execution without a real run.

### Q35 — Integrated `tinytools` release review
- **Lessons:** All ten lessons, especially `05-publishing-to-testpypi-and-pypi.md`, `06-trusted-publishing-and-signed-releases.md`, `07-versioning-changelogs-and-release-automation.md`, `09-private-indexes-and-internal-packages.md`, and `10-sbom-and-license-compliance.md`
- **Difficulty:** Advanced
- **Type:** Integrated capstone/release-readiness review
- **Points:** 2

**Question**

Review a proposed `tinytools` release with a CLI, two entry-point plugins, a native optional extension, a private internal dependency, and a container image. Produce a release decision and evidence checklist that covers artifact compatibility, clean-install testing, plugin contract tests, trusted publication, version/changelog/tag consistency, private source pinning, SBOM/license/vulnerability checks, provenance, and rollback. Identify what additional evidence is needed before approval.

**Expected deliverable:** Go/no-go memo with blockers, mitigations, owners, and evidence links/filenames.

**Evaluation criteria:** Distinguishes wheel, sdist, environment, and container scope; validates platform tags and runtime libraries; tests installed artifacts and plugin failures; checks private dependency source and lockfile; requires least-privilege publishing and traceable provenance; attaches per-release SBOM and scan reports; states uncertainties and does not treat green scanners as proof of safety or legal compliance.

---

# Part II — Answer Key and Evaluation Rubric

Do not use this section until you have attempted the question bank. Answers below are model responses, not the only acceptable designs. Normative standards and metadata requirements should be distinguished from tool-specific behavior and organizational policy.

## Phase A — Build and Artifacts

### Q01 — Model answer

A **build frontend** coordinates a build: it reads project configuration, creates or manages the build environment, invokes backend hooks, and collects artifacts. A **build backend** implements the packaging-specific work, such as producing a wheel or sdist. PEP 517 defines the frontend/backend interface; PEP 518 defines how a project declares the requirements needed to start its build system in `[build-system]`. During a typical `pip install .`, the frontend creates an isolated build environment and installs the declared build requirements so the build does not accidentally depend on packages in the user's runtime environment. Isolation improves repeatability but is not a sandbox: backend code and build dependencies execute code and must be treated as supply-chain inputs.

**Common incorrect answer:** “The backend installs packages and the frontend compiles Python.” This oversimplifies the responsibilities and ignores metadata preparation/build hooks. Isolation also does not mean the build is safe by default.

**Scoring (2):** frontend/backend distinction (1); PEP roles and isolation/security caveat (1).

### Q02 — Model answer

The backend is inconsistent: `requires` installs Hatchling but `build-backend` names setuptools. A minimal Hatchling configuration for a `src/` layout is:

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "tinytools"
version = "0.1.0"
requires-python = ">=3.12"
license = "MIT"
dependencies = ["httpx>=0.27"]

[tool.hatch.build.targets.wheel]
packages = ["src/tinytools"]
```

The project must verify the installed Hatchling version supports the metadata syntax being used; newer PEP 639-style license metadata may be preferable when supported by the chosen backend, and `license-files` should be configured/verified when needed. Then run `uv build`, inspect the artifacts, and test the wheel in a clean environment.

**Common incorrect answers:** Keeping `setuptools.build_meta` while installing only Hatchling; assuming source-tree imports prove wheel completeness; adding `license-files` without checking backend/version behavior.

**Scoring (3):** consistent backend (1); valid package discovery and metadata awareness (1); validation plan (1).

### Q03 — Model answer

The sdist rebuild has no Git metadata from which to derive the version. The checkout build works because the VCS plugin can inspect tags and history; the sdist is a distribution artifact and may not contain `.git`. A robust design should derive the version at release time and ensure the resulting version is represented in the sdist metadata or that the backend's documented sdist-rebuild mechanism works without VCS data. Include all required source files and versioning configuration. Pin or constrain build-system requirements to known-compatible versions, use build isolation, and validate both wheel and sdist from a clean checkout/environment. For reproducibility, rebuild with controlled inputs and compare hashes or normalized contents where feasible; deterministic output is not guaranteed merely by pinning dependencies.

**Common incorrect answer:** “Add `.git` to the sdist.” This is usually not an appropriate general solution and can be undesirable for size/security reasons. “Use `--no-build-isolation`” does not solve missing VCS data and can make the environment less controlled.

**Scoring (3):** correct root cause (1); robust sdist/version strategy (1); controlled build and verification (1).

### Q04 — Model answer

- `numpy`: distribution name.
- `2.1.0`: distribution version.
- `cp313`: Python implementation/version tag, CPython 3.13.
- `cp313`: ABI tag for the CPython 3.13 ABI.
- `manylinux_2_17_x86_64`: Linux x86-64 platform tag targeting the manylinux glibc compatibility policy with a glibc 2.17 baseline.

The tag is an install-compatibility declaration, not a security certificate. Actual compatibility depends on the wheel's contents, external shared libraries, architecture, and runtime environment. A compatible tag does not mean the wheel works on every Linux distribution, especially systems with incompatible libc assumptions, nor does it prove that the artifact was built correctly or safely. A prebuilt wheel can avoid executing package build code during installation when selected, but it can still be malicious or vulnerable. The filename does not establish provenance or correctness.

**Common incorrect answer:** Reading `cp313` as Python 3.12, treating `manylinux_2_17` as “works on every Linux,” or assuming the tag proves the binary is safe.

**Scoring (2):** tags decoded (1); limitations explained (1).

### Q05 — Model answer

Alpine typically uses musl libc, while manylinux wheels target glibc-based Linux compatibility. A manylinux wheel may therefore be unavailable or incompatible, causing the installer to fall back to an sdist build or producing runtime linker failures. Inspect available wheel tags and the selected artifact, for example with `python -m pip debug --verbose`, package index listings, wheel filename inspection, and `auditwheel show` on a Linux host. Remediations include publishing a compatible musllinux wheel, using a documented and supported source-build toolchain, or restricting support to platforms where the package is tested. `auditwheel` helps inspect/repair Linux wheel compatibility and bundle eligible libraries; it cannot make arbitrary system dependencies portable or replace runtime testing.

**Common incorrect answer:** “Rename the wheel to musllinux.” Renaming does not rebuild or validate binary compatibility.

**Scoring (3):** libc/tag issue (1); useful verification (1); realistic remediation and tool limits (1).

### Q06 — Model answer

One acceptable sequence (install optional validators in a separate tooling environment as appropriate):

```bash
uv build
ls -l dist/
uvx twine check dist/*
uvx check-wheel-contents dist/*.whl
python -m venv /tmp/tinytools-check
# POSIX shell:
/tmp/tinytools-check/bin/python -m pip install --upgrade pip
/tmp/tinytools-check/bin/python -m pip install dist/tinytools-0.1.0-py3-none-any.whl
cd /tmp
/tmp/tinytools-check/bin/python -c "import tinytools; print(tinytools.__file__)"
```

Use the actual wheel filename emitted by the build. On Windows, use the corresponding `Scripts\python.exe` path. Inspect the sdist and wheel archive contents with `unzip -l` or Python's `zipfile`/`tarfile` tools; verify expected modules and resources are present. In `*.dist-info`, `METADATA` contains distribution metadata and dependency declarations, `WHEEL` records wheel format/tag metadata, `RECORD` lists installed archive paths and hashes/sizes where applicable, and `entry_points.txt` appears when entry points are declared. `twine check` validates distribution metadata/long-description rendering, `check-wheel-contents` catches common wheel layout problems, and clean installation catches missing files or accidental source-tree imports. This sequence is illustrative; tool availability and flags must be checked in the selected versions.

**Common incorrect answer:** Testing only `uv sync` or an editable install, which can mask missing wheel files.

**Scoring (3):** build/artifact checks (1); clean wheel install/import (1); explains what checks detect (1).

### Q07 — Model answer

| PEP | Main concern |
|---|---|
| 517 | Build frontend/backend hook interface |
| 518 | Declaring build-system requirements in `pyproject.toml` |
| 621 | Standard project metadata in `[project]` |
| 660 | Editable-install hooks for modern build backends |
| 639 | License metadata and license-file handling |
| 735 | Dependency groups, commonly development/test tooling not intended as runtime dependencies |
| 751 | Standardized `pylock.toml` lock-file format awareness; tool support and workflow may vary |

Runtime dependencies are needed by installed users. Optional dependencies/extras are named install-time feature sets commonly declared in `[project.optional-dependencies]`. Dependency groups are named sets for development, testing, docs, or tooling and are not the same as published runtime extras. Support is tool/version dependent, so validate metadata and CLI support with the chosen tool version rather than assuming every frontend understands every standard identically.

**Common incorrect answer:** Treating `uv.lock` and standardized `pylock.toml` as interchangeable in every tool/version, or publishing dev groups as runtime dependencies by default.

**Scoring (3):** at least six PEP mappings correct (2); dependency category distinctions/tool-version caveat (1).

### Q08 — Model answer

Inspect the built wheel, not only the source tree:

```bash
uv build
python -m zipfile -l dist/tinytools-0.1.0-py3-none-any.whl
```

Configure the selected backend to include `src/tinytools/templates/default.json` in the wheel. For Hatchling, package discovery and artifact selection should explicitly include the package tree/resources as needed. Load the resource through `importlib.resources`, for example:

```python
from importlib.resources import files

def default_template() -> str:
    return files("tinytools").joinpath("templates/default.json").read_text(encoding="utf-8")
```

Add a test that installs the built wheel in a fresh environment and calls `default_template()` from outside the repository. A test that reads the file by a repository-relative path does not verify package inclusion.

**Common incorrect answer:** Constructing a path from `Path.cwd()` or assuming every resource is a normal filesystem file after installation.

**Scoring (3):** artifact inspection (1); package data/resource API fix (1); clean-install regression test (1).

### Q09 — Model answer

Risks include: (1) untrusted sdist build code executes; (2) disabling build isolation makes ambient packages/tool versions influence the build; (3) unknown build requirements may be compromised or non-reproducible; (4) no proof that the artifact is the reviewed source's output; (5) long-lived token theft from logs, runner, or dependencies; (6) PR code may reach publishing credentials if trust boundaries are weak. Redesign as separate stages: validate untrusted contributions with no publish secrets; build from a reviewed commit in a controlled environment with declared/pinned build requirements; produce wheel and sdist; run metadata/content checks and clean-install tests; record hashes and provenance/attestation where supported; publish only from a protected release workflow with least privilege and Trusted Publishing/OIDC where available. Keep secrets out of logs and source control.

**Common incorrect answer:** “Build isolation prevents malicious build code.” It isolates dependencies; it is not a sandbox. “A token in a secret store makes all workflows safe” ignores who can invoke a workflow and read its environment.

**Scoring (4):** at least four distinct risks (2); controlled build/artifact checks (1); publication trust/credential separation (1).

## Phase B — Interfaces to Your Package

### Q10 — Model answer

A console-script declaration such as `tinytools = "tinytools.cli:main"` tells installers to create a platform-specific wrapper that imports and calls that target. `python -m tinytools` executes `tinytools.__main__` when that module exists; it is a separate invocation interface. Use `importlib.metadata.version("tinytools")` to avoid duplicating the installed version, and handle `PackageNotFoundError` intentionally. A CLI should return an integer status from `main()` and use `raise SystemExit(main())` or equivalent. Install with `pipx` or `uv tool` in a disposable tool environment, then test `tinytools --help` and failure exit codes as a subprocess; the exact install command depends on whether the selected tool installs from the local project, a built wheel, or an index. Unit-testing the function alone does not prove the installed wrapper works.

**Common incorrect answer:** Assuming declaring a console script automatically creates `tinytools/__main__.py`, or that printing an error sets a nonzero exit code.

**Scoring (2):** interface distinction (1); exit-code test concept (1).

### Q11 — Model answer

```python
from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files

def installed_version() -> str:
    try:
        return version("tinytools")
    except PackageNotFoundError as exc:
        raise RuntimeError("tinytools distribution metadata is not installed") from exc

def schema_text() -> str:
    return files("tinytools").joinpath("data/schema.json").read_text(encoding="utf-8")
```

Tests should assert the installed version is returned when metadata exists and that the missing-distribution case is handled with the intended error. A resource test should verify the expected JSON can be read from an installed wheel. Some packages may choose a fallback for development builds, but it must be explicit and must not silently invent a production version.

**Common incorrect answer:** Reading `__version__` as if it always exists or reading `./data/schema.json` relative to the process working directory.

**Scoring (3):** metadata API and error path (1); portable resource API (1); meaningful tests (1).

### Q12 — Model answer

The host enumerates the `tinytools.formats` group using `importlib.metadata.entry_points()` and selects the `json` entry. It should load only when needed, catch import/initialization errors, and validate the returned object against a documented protocol or required methods. A simplified example for current Python versions is:

```python
from importlib.metadata import entry_points

for ep in entry_points(group="tinytools.formats"):
    if ep.name == "json":
        try:
            plugin_type = ep.load()
            plugin = plugin_type()
            if not callable(getattr(plugin, "decode", None)):
                raise TypeError("plugin must implement decode(data)")
        except Exception as exc:
            # Report the plugin name and actionable failure context.
            raise RuntimeError(f"Could not load plugin {ep.name!r}") from exc
```

The exact `entry_points` API has evolved; Python 3.12+ supports the group-selection form shown. A host may continue loading other plugins if its policy allows per-plugin isolation.

**Common incorrect answer:** Assuming entry-point metadata guarantees the target exists or conforms to the interface.

**Scoring (3):** discovery/group correctness (1); load and contract validation (1); actionable error handling (1).

### Q13 — Model answer

Define a narrow protocol such as `decode(data: bytes) -> object`, `encode(value) -> bytes`, and stable capability metadata. Version the host/plugin API separately from package versions and define supported compatibility ranges. Enumerate metadata cheaply; load a plugin only when selected or when its capability is requested. Validate the contract and report plugin name, version, and cause when initialization fails. Test against a fake plugin, a valid installed plugin, an incompatible plugin, and a plugin with missing dependencies. Entry points are discovery metadata, not a sandbox: imported code runs in the host process with the host's privileges. Only install trusted plugins; if untrusted code must run, use a process/container boundary and explicit IPC/security controls.

**Common incorrect answer:** “Entry points make plugins safe because the host controls discovery.” Discovery does not constrain behavior after import.

**Scoring (3):** contract/API compatibility (1); lazy loading/error isolation/testing (1); trust-boundary recognition (1).

### Q14 — Model answer

An acceptable implementation has a plugin package whose `pyproject.toml` contains:

```toml
[project]
name = "tinytools-json"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["tinytools>=0.1,<1"]

[project.entry-points."tinytools.formats"]
json = "tinytools_json.plugin:JsonFormat"
```

Build both plugin wheels with `uv build`, create a clean venv, install the host wheel and both plugin wheels (plus their required dependencies), then query `importlib.metadata.entry_points(group="tinytools.formats")` and exercise `list-plugins` and the host discovery/invocation path. Do not run the test from a working directory that shadows installed modules. Acceptance evidence includes wheel listing, installed distribution metadata, both discovered entry points, successful invocation of both plugins, and a fake-plugin test for a deliberately invalid implementation. A local wheel installation is sufficient; public publication is unnecessary.

**Common incorrect answer:** Importing `tinytools_json.plugin` directly from the repository and claiming that proves entry-point metadata works.

**Scoring (3):** valid package metadata/wheel (1); clean installed discovery (1); failure-path test (1).

### Q15 — Model answer

For the CLI: verify the distribution was built and installed; inspect the wheel's `entry_points.txt` and package modules; check `python -m pip show tinytools`/`importlib.metadata`; verify the executable's environment path and target function; run it as a subprocess and inspect the return code. The checkout can mask packaging defects because imports find source files. For the optional plugin: check group/name/target, import dependencies, and whether loading occurs during startup; defer loading until needed and catch/report plugin-specific errors. Add clean-wheel smoke tests and test missing/incompatible plugins.

**Common incorrect answer:** Reinstalling repeatedly without inspecting the built artifact or attributing every plugin exception to the host application.

**Scoring (3):** CLI diagnosis (1); plugin diagnosis (1); preventive regression controls (1).

## Phase C — Publishing and Releasing

### Q16 — Model answer

A safe runbook is: confirm the release version and changelog; build wheel and sdist; run `twine check` and wheel-content validation; inspect filenames and metadata; test the wheel in a clean environment; verify the target is TestPyPI; configure a TestPyPI Trusted Publisher bound to the intended repository/workflow/environment if available, then publish a pre-release from a protected CI release event; otherwise use a scoped test-only credential and document the limitation; install the exact version from TestPyPI using an explicit index; test import and CLI; verify the generated attestation against the expected artifact/workflow identity where the service exposes one; record artifact hashes, tool versions, logs, and outcome. Example commands (verify exact flags against current versions):

```bash
uv build
uvx twine check dist/*
uv publish --publish-url https://test.pypi.org/legacy/ dist/*
python -m venv /tmp/tinytools-test
/tmp/tinytools-test/bin/python -m pip install --index-url https://test.pypi.org/simple/ tinytools==0.1.0
```

Use the actual release version and platform-specific venv path. Some workflows use `twine upload --repository-url ...`; never publish to the production index by accidentally reusing a URL or secret. Do not commit credentials.

**Common incorrect answer:** Installing from TestPyPI without specifying the index or treating a successful upload as proof that the installed artifact works.

**Scoring (3):** artifact checks (1); explicit test target and clean install (1); safe credential/evidence handling (1).

### Q17 — Model answer

Immediately revoke the exposed token and replace it only if needed; do not wait for history rewriting. Review registry audit logs, release events, package versions, and any suspicious uploads; coordinate incident response and assess whether published artifacts must be yanked or replaced. Removing the line in a later commit leaves the token in Git history, caches, clones, logs, and possibly forks. Rewrite history where appropriate to reduce future exposure, but treat the credential as compromised regardless. Trusted Publishing exchanges a workflow identity via OIDC for short-lived publishing authorization, reducing long-lived token handling; it still requires tight workflow permissions, protected release triggers, and correct registry-side trust configuration.

**Common incorrect answer:** “Force-push the secret away and the token is safe.” History rewriting cannot guarantee all copies are gone.

**Scoring (3):** immediate revoke and audit (1); history/exposure reasoning (1); correct Trusted Publishing comparison (1).

### Q18 — Model answer

OIDC lets a CI workflow present an identity token to a registry that is configured to trust the repository/workflow/environment, which can grant short-lived publication authority without storing a long-lived PyPI API upload token. This answers **who is authorized to publish**. A signature or attestation is evidence associated with an artifact; provenance may describe source revision, builder/workflow identity, build invocation, and materials, depending on the format and issuer. A verifier can use this to check that the artifact is associated with an expected source/workflow and has not changed since the evidence was created. It does not prove that source code is benign, that dependencies were uncompromised, that tests cover all behavior, that the identity/workflow was configured correctly, or that every claim is independently true. Verification must check the expected issuer, subject/artifact digest, identity, workflow, and policy.

**Common incorrect answer:** “Signed means secure” or “OIDC automatically signs every package.” Authentication, signatures, and provenance are related but distinct controls.

**Scoring (3):** OIDC role (1); distinguishes authorization/signing/provenance (1); at least three limitations (1).

### Q19 — Model answer

One defensible policy:

| Change | Example decision |
|---|---|
| Add optional public function | Minor release under SemVer if backward-compatible |
| Remove documented public function or CLI flag | Breaking change; normally major release after a deprecation period, unless a security urgency justifies faster action |
| Raise minimum supported Python version | Often a breaking compatibility change for users on the dropped Python version; state policy explicitly and consider a major release |
| Change a documented default | Potentially breaking if callers depend on the old behavior; assess behavioral compatibility rather than classifying by code diff size |
| Compatible bug fix | Patch release |
| Pre-release candidate for 2.0 | PEP 440 form such as `2.0.0rc1` |
| Accept `1.4.0rc1`, reject stable versions below 1.4.0 | Use PEP 440 specifiers/ordering intentionally; pre-release inclusion rules and explicit constraints must be tested with the chosen resolver |

SemVer is a compatibility/versioning convention with major/minor/patch meaning. PEP 440 defines Python package version syntax and ordering, including pre-releases, post-releases, and development releases. A project should publish one documented policy and avoid assuming every SemVer-valid string is interpreted identically by Python tooling.

**Common incorrect answer:** Treating `rc1` as a stable patch release or using SemVer alone to describe resolver behavior.

**Scoring (3):** reasonable classifications (1); PEP 440/SemVer distinction (1); correct pre-release caveat (1).

### Q20 — Model answer

Choose one release tool and define the workflow: conventional commit messages or towncrier fragments feed a generated changelog/version proposal; review and merge that proposal; CI tests the exact commit; create a protected tag; build from that tag; inspect/test artifacts; publish those exact files; attach checksums, reports, and release notes to the corresponding release. Enforce invariants: the package metadata version equals the tag/release version; the changelog describes that version; the build uses the tagged commit; artifact hashes match the published assets; publishing cannot be invoked by arbitrary PR code.

**Common incorrect answer:** Generating a version from the current branch but publishing artifacts built from a different commit, or allowing mutable tags to silently change release identity.

**Scoring (3):** version/changelog consistency (1); exact commit/artifact traceability (1); workflow protection (1).

### Q21 — Model answer

First assess the regression and its security/data impact. Stop further promotion, notify maintainers and affected consumers, and consider yanking `1.8.2` to discourage new resolution. Publish a corrected version such as `1.8.3` with a changelog and tests; communicate upgrade instructions and any temporary constraint. Identify deployed consumers through inventory/SBOMs or internal usage records and verify remediation. Yanking does not uninstall the version from existing environments, erase caches, or guarantee that all resolvers will avoid it in every context. Do not overwrite an immutable published release; release a new version and preserve incident evidence.

**Common incorrect answer:** Assuming yanking automatically repairs deployed applications.

**Scoring (3):** containment and impact assessment (1); corrected release/communication (1); yanking limitation (1).

### Q22 — Model answer

Fork PRs and other untrusted jobs must not receive publication secrets or write privileges. Use read-only/minimal permissions for tests; build and publish only from a protected branch/tag or reviewed release event. Separate jobs so the privileged publishing job downloads only the artifact produced by the trusted build job and verifies its identity/hash. Pin action versions where feasible, protect environments, use Trusted Publishing/OIDC, and retain attestation/provenance tied to the artifact digest. Define response steps to revoke trust/credentials, stop releases, assess affected artifacts, yank or supersede faulty releases, and communicate with consumers.

**Common incorrect answer:** Giving all jobs `contents: write` and `id-token: write` because the workflow file is in the repository. Permissions should be narrowly scoped to the job that needs them.

**Scoring (3):** trust-boundary defects (1); least-privilege staged workflow (1); provenance/recovery (1).

### Q23 — Model answer

Document the old behavior and why it must change; identify callers and offer a migration path or safer replacement. If practical, introduce a warning/deprecation window, tests, and clear release notes. Choose versioning according to the public compatibility contract and communicate a removal date. If the old behavior creates an urgent security vulnerability, a shorter deprecation window or immediate breaking change may be justified; record the rationale, provide upgrade guidance, and avoid promising compatibility that cannot safely be maintained.

**Common incorrect answer:** Always delaying a security fix until the next major release, or treating all behavior changes as patch-level changes.

**Scoring (2):** migration/release communication (1); defensible urgency/versioning reasoning (1).

### Q24 — Model answer

Retain: source commit and protected tag; package version and release notes; exact wheel/sdist filenames and SHA-256 hashes; build/test/artifact-check summaries; Python/tool/build-backend versions; publishing workflow run and identity; registry target and publication time; SBOM, vulnerability/license reports, and attestation/provenance where generated; exception approvals and incident contact. A hash establishes byte identity only when compared to a trusted reference. A signature associates signed data with a signing identity/key, whose trust must be checked. Provenance can describe build origin and process but is only as reliable as its issuer, builder, and verification policy.

**Common incorrect answer:** Treating a checksum file stored beside an artifact on the same untrusted channel as independent provenance.

**Scoring (2):** useful evidence set (1); hash/signature/provenance limitations (1).

## Phase D — Organisations and Supply Chain

### Q25 — Model answer

PEP 420 implicit namespace packages allow multiple distributions to contribute portions of the same import namespace without a root `acme/__init__.py`. `acme-core` may ship `acme/core/...` and `acme-ml` may ship `acme/ml/...`; their distribution names are separate from their import paths. If one distribution installs a regular `acme/__init__.py`, it can change import resolution and interfere with namespace portions. Create a two-package workspace and prove `import acme.core, acme.ml` works in a clean venv. Add an `import-linter` contract that forbids `acme.core` from importing `acme.ml`. A workspace can make local packages editable and coordinate dependency constraints with a shared lockfile, but independent releases remain possible if compatibility constraints and CI enforce the supported combinations. Lockstep versioning is simpler when components are tightly coupled; independent versioning reduces unnecessary coordinated releases but needs clear compatibility policy.

**Common incorrect answer:** Assuming distribution name and import package name must match, or assuming a monorepo inherently requires one version for every package.

**Scoring (3):** PEP 420 behavior and `__init__.py` risk (1); clean workspace import proof (1); dependency contract and workspace/versioning trade-off (1).

### Q26 — Model answer

The installer is configured to consider both internal and public candidates. If selection policy permits the public package to win—for example, based on version preference or the tool's multi-index behavior—the attacker-controlled project can be installed in place of the internal package. Mitigations include explicit package-to-index mapping supported by the chosen package manager, a single organization-controlled proxy/index with upstream allowlists, reserving/monitoring public names, quarantine/cooldown of upstream releases, immutable internal releases, and verifying resolved source in the lockfile/build evidence. Package-manager policy decides which source candidates are eligible/selected; registry controls determine who can publish, which upstream packages are available, and whether artifacts are quarantined or immutable. Use current tool docs for exact resolution semantics; do not assume all package managers treat multiple indexes the same.

**Common incorrect answer:** “Private packages are safe if the internal index is listed first” or “the package version is pinned, so source cannot change.” A version pin does not by itself guarantee the source or publisher.

**Scoring (3):** attack path (1); multiple concrete mitigations (1); tool-versus-registry distinction (1).

### Q27 — Model answer

A `uv` pattern is to define a named index and explicitly map the private distribution to it. Exact syntax and resolution semantics should be checked against the installed `uv` version; a representative pattern is:

```toml
[[tool.uv.index]]
name = "internal"
url = "https://packages.example.invalid/simple/"
explicit = true

[tool.uv.sources]
acme-analytics = { index = "internal" }
```

Then lock/sync with the project workflow (for example, `uv lock` followed by `uv sync`) and inspect `uv.lock` for the package version, source/index information, and artifact hashes where recorded. Use a placeholder URL and environment-based authentication; do not embed credentials. Confirm the resolved artifact and index through lockfile review, verbose resolution output, registry logs, or a controlled clean install. A lockfile helps reproduce a selected resolution, but does not prove that an authorized registry was uncompromised, that package code is benign, or that a private package name is owned by the intended organization. The exact source mapping should be tested with the project's `uv` version.

**Common incorrect answer:** Adding the internal URL as an ordinary extra index and assuming it has priority, or claiming the lockfile alone prevents dependency confusion.

**Scoring (3):** explicit source mapping (1); lock/source/hash inspection (1); lockfile limitations and secret hygiene (1).

### Q28 — Model answer

Use a disposable local registry, for example devpi, bound to loopback and configured with a test user/index; follow the installed devpi version's documented initialization and server commands. Build a toy package with `uv build`; upload the wheel using the registry's documented upload endpoint/client; verify it appears in the Simple API listing. Create a clean venv, configure an explicit index URL/source for the test package, install it, then check `importlib.metadata.version(...)` and import behavior. Record tool versions and registry URL, but never include credentials in the report. For a static Simple API index, serve a correctly structured index with package links and hashes, then verify the same clean install. Do not expose a demo registry to the public internet or reuse production credentials.

**Common incorrect answer:** Installing from the developer's current directory or assuming that successful upload proves the index served the installed file.

**Scoring (3):** build/publish and index evidence (1); clean explicit-source install (1); safe registry/auth/source verification (1).

### Q29 — Model answer

CycloneDX and SPDX are both SBOM standards. CycloneDX is often selected for vulnerability/security workflows and supports security-oriented use cases; SPDX has a strong license-compliance and software-supply-chain use history. Both can represent components, versions, relationships, and licensing/provenance data to varying extents; the choice should follow consumers and tooling rather than an absolute ranking. A `requirements.txt` describes dependency inputs, not necessarily the resolved environment or shipped bytes. The environment may contain extras or packages not shipped; the wheel may vendor native libraries/resources not represented as Python dependencies; the container may add OS packages, shared libraries, and application files. Produce a release-associated SBOM with an explicitly stated scope and supplement it with wheel/container scanning where appropriate.

**Common incorrect answer:** Treating an SBOM as a vulnerability report or claiming one format guarantees completeness.

**Scoring (3):** balanced format comparison (1); scope distinctions (1); artifact/container gaps (1).

### Q30 — Model answer

Build and test the exact release candidate; generate a CycloneDX SBOM for a documented environment/artifact scope; run `pip-audit` against the resolved environment; generate a license report with `pip-licenses` or a stronger file/package scanner as appropriate. Use explicit, version-controlled policy configuration to reject identified GPL/AGPL components under the organization's permissive-only policy. Unknown/conflicting metadata should fail closed into manual review or a defined quarantine state rather than being silently treated as permissive. An exception must identify the component/version, rationale, scope, owner, approver, compensating actions, and expiry date; exceptions should be re-reviewed on upgrades/releases. Keep reports, SBOM, tool versions, and exact release hashes as evidence. A scanner reports metadata and matching rules; package metadata can be wrong or incomplete, vendored code may be missed, and legal obligations depend on license texts, use/distribution facts, and applicable law. Route uncertain/high-impact findings to qualified legal/compliance review.

Tool flags vary by release; check `pip-licenses --help` for the selected version rather than assuming a particular `--fail-on` syntax. A policy script that parses structured output can be more explicit than brittle text matching.

**Common incorrect answer:** Treating every scanner match as a definitive legal verdict or allowing unknown licenses by default without review.

**Scoring (3):** CI scope and tools (1); fail/exception policy (1); scanner/legal limitations (1).

### Q31 — Model answer

Use the SBOM to identify each affected component version and map it to services/releases. Record CVE/advisory identifiers, severity (such as CVSS), exposure, reachability evidence, exploit prerequisites, fix availability, and operational impact. Prefer a fixed upstream version after compatibility/security testing; if no fix exists, consider a patch/fork, configuration mitigation, isolation, feature disablement, or a time-bounded risk acceptance with an owner and expiry. Roll out in stages with regression tests and monitor results. A VEX statement can communicate whether a product is affected and why, but a “not affected” assertion needs evidence: version/component mapping, code-path/reachability analysis, configuration facts, test results, and reviewer identity. Reassess when versions/configuration change.

**Common incorrect answer:** “No direct dependency means no exposure,” or “not reachable” without evidence. Transitive dependencies can be shipped and reachable.

**Scoring (3):** impact mapping and triage (1); remediation/mitigation plan (1); evidence-based VEX/communication (1).

### Q32 — Model answer

| Incident | Likely cause | Verification | Corrective action |
|---|---|---|---|
| 1. Yanked release still deployed | Yanking affects future resolution, not installed deployments | Inspect lockfile, environment, and deployed package version | Upgrade/rebuild/redeploy; verify rollout |
| 2. Token in Git history | Credential was exposed to anyone with history access | Revoke immediately; inspect registry/audit events | Rotate/revoke, investigate, remove from history as hygiene, adopt secret scanning/Trusted Publishing |
| 3. GPL transitive dependency | Dependency graph includes a component whose declared license triggers policy | Trace dependency path and inspect package/license files | Block release pending compliance review, replacement, or approved exception |
| 4. Linux wheel fails elsewhere | Incompatible platform/libc tag or external shared-library assumption | Inspect wheel tags, architecture, libc, and linked libraries | Publish supported wheel/build path or restrict support and document it |
| 5. Namespace broken | Root `acme/__init__.py` changed implicit namespace behavior | Inspect wheel contents and import paths | Remove conflicting root init where PEP 420 is intended; test multiple distributions together |
| 6. Public package selected | Unsafe multi-index/source policy or mapping drift | Inspect lockfile source, verbose resolver output, registry logs | Explicit source mapping/controlled proxy, name governance, quarantine, and clean re-resolution |

**Common incorrect answer:** Fixing only the visible symptom—for example, yanking without redeploying, or rewriting Git history without revoking the token.

**Scoring (3):** 0.5 per incident with plausible cause and actionable verification/remediation; award full credit for equivalent safe responses.

### Q33 — Model answer

A strong standard assigns an owner and security contact to each distribution; defines naming and public-name conflict rules; sets supported Python versions and metadata/license-file requirements; uses an organization-controlled package source with explicit source mapping, upstream allowlists, quarantine, and immutable published versions; requires build/test/clean-install checks, SBOM/license/vulnerability reports, release provenance, changelog and deprecation policy; and defines incident response, yank/rebuild/notification procedures, and time-bounded exceptions. Large datasets/model weights should normally use an artifact or model registry with its own access, versioning, provenance, and license metadata rather than being hidden in oversized Python wheels. A monorepo/workspace is useful when coordinated changes, shared tooling, and a unified lockfile matter; polyrepos can improve ownership and independent lifecycle boundaries but increase integration/version coordination cost.

**Common incorrect answer:** “Always use a monorepo” or “package registry metadata alone is a complete inventory for model weights and OS packages.”

**Scoring (3):** policy/ownership/source security (1); compliance/incident controls (1); repo/artifact trade-offs (1).

### Q34 — Model answer

A robust job is split into explicit steps: (1) install pinned tooling; (2) build wheel/sdist from the intended commit; (3) run metadata/content checks and clean-install tests; (4) generate an SBOM for the documented target; (5) run `pip-audit` against the resolved environment or artifact scope; (6) emit structured license data and evaluate it against a version-controlled policy; (7) upload reports and the SBOM as immutable release artifacts with the package version/commit. Fail the job on policy violations or unresolved unknown licenses according to policy. Exceptions require an auditable approval with scope, reason, owner, expiry, and compensating controls. Record tool versions and exact artifact hashes. Do not run a scan of a development environment and describe it as a complete container SBOM. Validate exact command flags using each installed tool's help/documentation.

**Common incorrect answer:** `pip-audit` is not a license scanner; `pip-licenses` is not a vulnerability scanner; a green result does not prove no unknown/vendored components exist.

**Scoring (3):** coherent steps/scope (1); correct distinct tool roles and retained evidence (1); fail/exception handling (1).

### Q35 — Model answer

A defensible review is **no-go until evidence closes the release blockers**. Require platform-specific wheel validation for the native extension and a documented source-build path; clean installs of the built wheel and sdist; CLI exit-code and resource tests; plugin discovery/contract/error-isolation tests; a lockfile and explicit source mapping for the private dependency plus source verification; protected release workflow with least privilege and Trusted Publishing where supported; version/tag/changelog consistency; SBOMs for the Python release and container image with clear scope; `pip-audit` and license policy reports; provenance/attestation verified against the expected workflow identity and artifact digest; and a rollback/yank/notification runbook. Identify missing evidence by owner and deadline. A green scanner cannot establish absence of unknown vulnerabilities, prove plugin code is benign, or decide legal obligations; unknown findings and exceptions need explicit disposition.

**Common incorrect answer:** Approving because unit tests pass or because a single Python-level SBOM exists, without checking the native extension, private source, and container contents.

**Scoring (2):** artifact/plugin/platform coverage and source/publishing/provenance checks (1); SBOM/compliance/rollback and uncertainty handling (1).

---

# Part III — Learning Assessment

## A. Coverage Matrix

| Question | Phase | Lesson reference(s) | Learning objective | Difficulty |
|---|---|---|---|---|
| Q01 | A | 01 | Explain frontend/backend, PEP 517/518, and build isolation | Beginner |
| Q02 | A | 01 | Repair consistent build-system and project metadata | Intermediate |
| Q03 | A | 01 | Design dynamic metadata and reproducible sdist rebuilds | Advanced |
| Q04 | A | 02 | Decode wheel compatibility tags | Beginner |
| Q05 | A | 02 | Diagnose libc/platform wheel incompatibility | Intermediate |
| Q06 | A | 02 | Validate built artifacts in a clean environment | Intermediate |
| Q07 | A | 01 | Distinguish packaging PEPs and dependency categories | Intermediate |
| Q08 | A | 01, 02 | Debug missing package resources in a wheel | Intermediate |
| Q09 | A | 01, 02 | Threat-model builds and separate build/publish trust | Advanced |
| Q10 | B | 03 | Explain console scripts and exit-code testing | Beginner |
| Q11 | B | 03 | Use installed metadata and portable package resources | Intermediate |
| Q12 | B | 04 | Discover and validate entry-point plugins | Intermediate |
| Q13 | B | 04 | Design a compatible, lazy, failure-isolated plugin API | Advanced |
| Q14 | B | 04 | Build/test a plugin distribution from a clean install | Intermediate |
| Q15 | B | 03, 04 | Diagnose CLI packaging and plugin startup failures | Advanced |
| Q16 | C | 05 | Publish safely to TestPyPI and verify installation | Intermediate |
| Q17 | C | 05, 06 | Respond to leaked token and compare publishing auth | Advanced |
| Q18 | C | 06 | Distinguish OIDC, signatures, attestations, provenance | Advanced |
| Q19 | C | 07 | Apply SemVer and PEP 440 correctly | Intermediate |
| Q20 | C | 07 | Preserve release version/tag/changelog/artifact consistency | Intermediate |
| Q21 | C | 05, 07 | Recover from a faulty/yanked release | Advanced |
| Q22 | C | 05, 06, 07 | Secure release workflows and provenance | Advanced |
| Q23 | C | 07 | Plan deprecation and urgent compatibility changes | Intermediate |
| Q24 | C | 05, 06, 07 | Define auditable release evidence | Advanced |
| Q25 | D | 08 | Explain PEP 420 and workspace/versioning trade-offs | Intermediate |
| Q26 | D | 09 | Analyze dependency confusion and registry controls | Advanced |
| Q27 | D | 09 | Configure explicit private source mapping and inspect lock | Intermediate |
| Q28 | D | 09 | Publish/install through a disposable private index | Intermediate |
| Q29 | D | 10 | Compare SBOM formats and inventory scopes | Intermediate |
| Q30 | D | 10 | Enforce license policy with exception governance | Advanced |
| Q31 | D | 10 | Triage transitive vulnerabilities with evidence | Advanced |
| Q32 | D | 02, 07, 08, 09, 10 | Diagnose six cross-module supply-chain failures | Advanced |
| Q33 | D | 08, 09, 10 | Design an organization-wide packaging standard | Advanced |
| Q34 | D | 10 | Design a release compliance CI job | Advanced |
| Q35 | D | 01–10 | Conduct integrated release-readiness review | Advanced |

### Lesson coverage check

| Lesson file | Questions |
|---|---|
| `01-build-backends-and-pep-517.md` | Q01–Q03, Q07–Q09 |
| `02-wheels-sdists-and-binary-compatibility.md` | Q04–Q06, Q08–Q09, Q32, Q35 |
| `03-entry-points-and-console-scripts.md` | Q10–Q11, Q15 |
| `04-plugin-architectures-with-entry-points.md` | Q12–Q15, Q35 |
| `05-publishing-to-testpypi-and-pypi.md` | Q16–Q17, Q21–Q22, Q24, Q35 |
| `06-trusted-publishing-and-signed-releases.md` | Q09, Q17–Q18, Q22, Q24, Q35 |
| `07-versioning-changelogs-and-release-automation.md` | Q19–Q24, Q32, Q35 |
| `08-namespace-packages-and-monorepos.md` | Q25, Q32–Q33, Q35 |
| `09-private-indexes-and-internal-packages.md` | Q26–Q28, Q32–Q33, Q35 |
| `10-sbom-and-license-compliance.md` | Q29–Q35 |

## B. Self-Assessment Rubric

Score each dimension from 0 to 4. A high score requires demonstrated work and evidence, not familiarity with terminology alone.

| Dimension | 0 — Not yet | 1 — Emerging | 2 — Competent | 3 — Strong | 4 — Independent |
|---|---|---|---|---|---|
| Foundational understanding | Cannot explain core terms | Recalls terms with major confusion | Explains main mechanisms | Connects standards to behavior | Explains edge cases and boundaries accurately |
| Practical implementation | No working artifact | Partial steps, not reproducible | Builds and tests with guidance | Clean artifact and repeatable commands | Reproducible workflow with evidence and failure tests |
| Debugging/problem solving | Guesses without evidence | Checks symptoms only | Uses targeted diagnostics | Finds root cause and regression test | Prioritizes hypotheses and prevents recurrence |
| Security/supply-chain awareness | Misses trust boundaries | Names risks but no controls | Applies baseline controls | Threat-models and verifies controls | Handles exceptions/incidents with traceable evidence |
| Production-readiness judgment | Approves without evidence | Checklist incomplete | Identifies major blockers | Makes reasoned go/no-go decisions | Explicitly manages uncertainty, ownership, and recovery |

**Interpretation:** 0–7 per dimension means revisit the relevant lessons and redo practical tasks; 8–13 means continue guided practice; 14–17 means the core outcome is demonstrated with some gaps; 18–20 means strong performance on this assessment. A high score is evidence of learning, not proof of professional production readiness or a substitute for supervised release experience.

## C. Remediation Guidance

Use the exact lesson filenames from the project tree.

| Weak area | Revisit | Recommended redo task |
|---|---|---|
| Build frontend/backend, metadata, build isolation | `01-build-backends-and-pep-517.md` | Redo Q01–Q03 and explain why a build is executable supply-chain input |
| Wheel tags, native compatibility, artifact contents | `02-wheels-sdists-and-binary-compatibility.md` | Redo Q04–Q08; inspect a built wheel and test it outside the repository |
| Console scripts, metadata, resources, exit codes | `03-entry-points-and-console-scripts.md` | Redo Q10–Q11 and test the installed CLI as a subprocess |
| Entry-point plugins and failure handling | `04-plugin-architectures-with-entry-points.md` | Redo Q12–Q15 with a valid and deliberately broken plugin |
| TestPyPI and safe artifact publication | `05-publishing-to-testpypi-and-pypi.md` | Redo Q16–Q17 and produce a dry-run release checklist |
| OIDC, signatures, attestations, provenance | `06-trusted-publishing-and-signed-releases.md` | Redo Q18/Q22/Q24 and diagram the expected trust chain |
| SemVer, PEP 440, changelog, tags, yanking | `07-versioning-changelogs-and-release-automation.md` | Redo Q19–Q24 and simulate a faulty-release recovery plan |
| PEP 420, workspace layout, independent releases | `08-namespace-packages-and-monorepos.md` | Redo Q25/Q32 and test two distributions sharing a namespace |
| Private indexes, explicit source mapping, lockfiles | `09-private-indexes-and-internal-packages.md` | Redo Q26–Q28 with a disposable local registry and clean venv |
| SBOM scope, license policy, vulnerability triage | `10-sbom-and-license-compliance.md` | Redo Q29–Q34 and generate scoped release evidence |
| Cross-module release judgment | All ten lesson files | Redo Q35 as a written go/no-go review with evidence gaps and owners |

## D. Completion Criteria

A learner has completed this assessment when they can:

- Explain the build frontend/backend model and the roles of the relevant PEPs without confusing standards with tool-specific behavior.
- Build both wheel and sdist, inspect their contents, and validate an installation in a clean environment.
- Implement and test console scripts and entry-point plugins, including incompatibility/error cases.
- Describe a safe TestPyPI-to-PyPI release process and distinguish Trusted Publishing, signatures, attestations, and provenance.
- Apply a documented versioning/deprecation policy and explain recovery from a faulty release.
- Explain namespace packages and choose a workspace/release strategy based on explicit trade-offs.
- Prevent common dependency-confusion patterns through source policy, registry controls, and lock/source verification.
- Produce per-release SBOM, license, and vulnerability evidence with stated scope, tool versions, and exception handling.
- Diagnose the six required “what went wrong?” scenarios and justify a release go/no-go decision.

Suggested completion threshold: **80/100**, with no zero in security/supply-chain awareness and successful completion of at least one artifact-validation task and one source/registry or compliance task. If a practical task was not executed, mark it **not demonstrated** rather than awarding implementation credit based on a written plan alone. Passing this question bank demonstrates learning against the module syllabus; it does not independently certify production readiness, legal compliance, or security of a released package.

---

# Authoritative References

The module lessons should remain the primary study material. These external references help verify standards and current tool behavior; check their current versions before applying a workflow.

- Python Packaging User Guide: <https://packaging.python.org/en/latest/>
- PyPA build frontend (`build`): <https://build.pypa.io/en/stable/>
- PEP 517 — A build-system independent format for source trees: <https://peps.python.org/pep-0517/>
- PEP 518 — Specifying minimum build system requirements: <https://peps.python.org/pep-0518/>
- PEP 621 — Storing project metadata in `pyproject.toml`: <https://peps.python.org/pep-0621/>
- PEP 660 — Editable installs for pyproject.toml based builds: <https://peps.python.org/pep-0660/>
- PEP 639 — Improving license clarity with better package metadata: <https://peps.python.org/pep-0639/>
- PEP 735 — Dependency Groups in `pyproject.toml`: <https://peps.python.org/pep-0735/>
- PEP 751 — `pylock.toml` specification: <https://peps.python.org/pep-0751/>
- `uv` documentation: <https://docs.astral.sh/uv/>
- `importlib.metadata`: <https://docs.python.org/3/library/importlib.metadata.html>
- `importlib.resources`: <https://docs.python.org/3/library/importlib.resources.html>
- Python Packaging User Guide — entry points: <https://packaging.python.org/en/latest/specifications/entry-points/>
- PyPI Trusted Publishers: <https://docs.pypi.org/trusted-publishers/>
- TestPyPI: <https://test.pypi.org/>
- Python version specifiers / PEP 440: <https://packaging.python.org/en/latest/specifications/version-specifiers/>
- CycloneDX: <https://cyclonedx.org/specification/overview/>
- SPDX specifications: <https://spdx.github.io/spdx-spec/>
- `pip-audit`: <https://github.com/pypa/pip-audit>
- `cyclonedx-python`: <https://cyclonedx-bom-tool.readthedocs.io/> (verify current project/tool documentation for the installed `cyclonedx-py` CLI)
- `pip-licenses`: <https://github.com/raimon49/pip-licenses>
- Syft: <https://github.com/anchore/syft>
- `devpi`: <https://devpi.net/docs/devpi/devpi/stable/>
- `auditwheel`: <https://github.com/pypa/auditwheel>

