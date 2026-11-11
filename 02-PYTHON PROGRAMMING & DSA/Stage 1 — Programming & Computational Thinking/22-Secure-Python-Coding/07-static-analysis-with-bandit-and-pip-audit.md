# Static Analysis with Bandit and pip-audit

> **Module 22 — Secure Python Coding · Lesson 07**  
> Audience: Python application, backend, data-platform, and AI/ML engineers  
> Scope: local development, pull requests, CI, dependency supply chain, and security triage

## Learning outcomes

By the end of this lesson, you should be able to:

- Distinguish SAST, SCA, secret scanning, and policy-as-code, and choose the right control for each risk.
- Run Bandit, Ruff's `S` rules, `pip-audit`, and secret scanners reproducibly; interpret results without treating a clean report as proof of security.
- Triage findings using severity, confidence, exploitability, reachability, impact, and compensating controls.
- Fix findings before suppressing them, document narrow exceptions, and manage legacy baselines without hiding new issues.
- Add pre-commit hooks and CI gates, publish Bandit SARIF where supported, and test the gates by introducing a harmless seeded issue.
- Review dependency provenance, lockfiles, hashes, maintainer/release risk, licenses, release-age policies, and vulnerability exceptions.
- Write and test a custom Semgrep rule and harden the `vulnpy` mini-project with a security gate.

## Prerequisites and lab safety

You should already understand Python modules, exceptions, logging, tests, virtual environments, `subprocess`, file/network boundaries, secrets hygiene, and dependency installation. Familiarity with Git and CI is useful. This lesson uses only a local sample repository. Never commit real credentials to demonstrate a secret scanner; use a clearly fake marker such as `EXAMPLE_NOT_A_REAL_TOKEN_12345`.

The roadmap describes `vulnpy` as a deliberately vulnerable, roughly 300-line upload-and-summarise service with file upload, report generation, URL fetching, configuration loading, and an admin CLI. Exploit demonstrations belong only in a disposable local checkout. The goal is to detect, fix, and regression-test defects—not to publish working exploit payloads against third-party systems.

---

## 1. Vocabulary and assurance layers

### 1.1 Four related but different controls

| Control | Primary question | Typical tools | What it does not prove |
|---|---|---|---|
| **SAST** (static application security testing) | Does source code contain suspicious security patterns or data flows? | Bandit, Ruff `S`, Semgrep, CodeQL | Correct authorization, business logic, or runtime configuration |
| **SCA** (software composition analysis) | Do declared/installed dependencies match known vulnerable components or policy violations? | `pip-audit`, OSV-Scanner, Safety, Snyk, Trivy, Grype | That a vulnerable code path is reachable, or that no unknown vulnerability exists |
| **Secret scanning** | Do tracked files or repository history appear to contain credentials/private keys? | `detect-secrets`, Gitleaks, GitHub secret scanning, TruffleHog | That every credential source was scanned or that a detected token is valid |
| **Policy-as-code** | Does the repository/build/deployment comply with explicit rules? | CI conditions, Semgrep policies, OPA/Conftest, dependency allow-lists, custom checks | That the policy is complete or correctly models the threat |

These layers overlap, but they are not interchangeable. Bandit can flag `subprocess` patterns; it does not check whether a transitive package version has a published CVE. `pip-audit` can identify a known vulnerable distribution; it does not inspect your authorization logic. Secret scanners can find likely credentials, but they do not rotate them.

### 1.2 Where the controls fit

```text
Developer edit
   ├── editor / Ruff ── quick feedback
   ├── pre-commit ───── S rules, Bandit, secret checks
   └── local tests ──── regression and behaviour checks
             |
             v
Pull request CI
   ├── unit/integration/security tests
   ├── SAST (Bandit + Semgrep; optional CodeQL)
   ├── SCA (locked dependency set + pip-audit / OSV)
   ├── secret scan (Gitleaks + baseline-aware detector)
   ├── dependency/build policy + SBOM/provenance checks
   └── required checks + review of exceptions
             |
             v
Release/deploy
   ├── scan final artifact/container and notebooks
   ├── verify hashes, provenance, signatures, SBOM
   └── runtime monitoring + incident response
```

A scan is useful only if the repository scope is correct, results are retained, findings have owners, and the pipeline enforces an explicit decision. A “green” result means only that the configured tools did not report a gate-blocking issue in the scanned scope at that time.

---

## 2. Reproducible setup and local workflow

### 2.1 Example repository layout

```text
vulnpy/
├── pyproject.toml
├── uv.lock
├── .pre-commit-config.yaml
├── .secrets.baseline
├── .gitleaks.toml
├── .semgrep/
│   └── requests-timeout.yml
├── src/
│   └── vulnpy/
├── tests/
│   └── security/
├── SECURITY.md
└── .github/workflows/security.yml
```

Adapt paths to the actual repository. If the project uses a `src/` layout, scan `src`; do not accidentally scan only the repository root or omit application modules. Tests should be included in linting and secret scanning; whether Bandit scans tests depends on the project’s policy. Test-only assertions are common, but `assert` must not implement production authorization or input validation because Python can remove assertions under optimization.

### 2.2 Choose one environment workflow: `uv`

This lesson uses `uv` consistently. Pin tool versions in the project’s development dependency set and commit `uv.lock`. The version numbers below are intentionally not invented: choose approved versions, record them in `pyproject.toml`, and update them through reviewed update PRs.

From the repository root:

```bash
uv init --src --name vulnpy
uv add --dev 'bandit[toml,sarif]' ruff pip-audit detect-secrets semgrep pre-commit pytest
uv lock
uv sync --locked
```

If the repository already exists, do **not** run `uv init` over it. Add the required tools to its existing project instead. `gitleaks` is a separate CLI binary; install it using your organization’s approved package source and pin or verify the binary version in CI. GitHub secret scanning is a hosted repository feature, not a Python package.

Useful local commands:

```bash
# Roadmap's primary Bandit workflow: medium severity and above.
uv run bandit -r src -ll

# Keep machine-readable results for triage or CI artifacts.
uv run bandit -r src -ll -f json -o bandit.json

# SARIF output uses Bandit's documented optional extra (included in setup above).
uv run bandit -r src -ll -f sarif -o bandit.sarif

# Ruff's Bandit-derived security rules; inspect both application and tests.
uv run ruff check --select S src tests

# Audit the currently synced environment.
uv run pip-audit --strict

# If the pinned pip-audit supports project lockfile auditing, audit the lock directly.
uv run pip-audit --locked

# Portable fallback: scan an explicit export of the chosen locked runtime set.
uv export --locked --no-dev --format requirements.txt -o /tmp/vulnpy-runtime-requirements.txt
uv run pip-audit --strict -r /tmp/vulnpy-runtime-requirements.txt

# Secret scanning. The first command creates/replaces a baseline; review it before committing.
uv run detect-secrets scan > .secrets.baseline
git ls-files -z | xargs -0 uv run detect-secrets-hook --baseline .secrets.baseline

# Scan Git history. Pin Gitleaks and verify syntax for that release.
gitleaks git . --redact

# Scan working-tree files too; configure exclusions for generated/virtualenv directories.
gitleaks dir . --redact

# Run the custom Semgrep rule and its test fixtures (see section 9).
uv run semgrep --config .semgrep/requests-timeout.yml src tests
uv run semgrep --test .semgrep/requests-timeout.yml
```

**Important distinctions:** `pip-audit`’s environment scan and a dependency-file scan answer different questions. The exported requirements file above intentionally represents runtime dependencies because `--no-dev` is used; run a separate development-dependency audit if developer tools are installed in CI or are part of the build risk. If your `uv` version or project structure does not support the exact export options shown, consult that pinned version’s `uv export --help` and verify that the exported file actually includes the intended groups. Do not silently audit a partial environment and call it complete.

`pip-audit` supports machine-readable formats such as JSON and CycloneDX; inspect `uv run pip-audit --help` for the installed release’s format names and output options. The `--locked` project/lockfile mode is version-sensitive, so keep the requirements-export fallback if the pinned release or project backend does not support it. The documented short output option is `-o`. Example:

```bash
uv run pip-audit --strict --format json -o pip-audit.json
uv run pip-audit --strict --format cyclonedx-json -o sbom-audit.json
```

These flags are version-sensitive. Validate the exact format name against the locked tool version before wiring it into a gate. A JSON report is not automatically a complete SBOM; use a dedicated SBOM generator when that is a requirement.

### 2.3 Keep tool inputs stable

- Commit `uv.lock`; use `uv sync --locked` in CI so an unexpected lockfile change fails instead of being silently rewritten.
- Pin CI actions to reviewed immutable commit SHAs in production workflows. Tags are easier to read but can move.
- Keep scanner versions in a controlled update process. Tool upgrades can change findings and rule coverage.
- Store reports as CI artifacts with appropriate access controls; reports can contain file paths, snippets, package names, and possibly secret-like values.
- Record the scan scope and tool version in the build log. Avoid logging full environment variables or authenticated package URLs.

---

## 3. Bandit: Python SAST

### 3.1 How it works

Bandit parses Python into an abstract syntax tree and runs plugins that flag patterns associated with common security mistakes. It is particularly useful for dangerous APIs and risky constructs. It is not a full proof system or a substitute for code review and tests.

The roadmap’s standard workflow is:

```bash
uv run bandit -r src -ll
```

`-r` scans recursively. `-ll` sets the minimum severity to **MEDIUM**; it is not “high only.” Use `-lll` for HIGH severity only. Confidence is a separate dimension and can be filtered independently. During initial adoption, run a broad scan and inspect all results before narrowing the gate.

For machine-readable reports:

```bash
uv run bandit -r src -f json -o bandit.json
uv run bandit -r src -ll -f sarif -o bandit.sarif
```

Bandit documents TOML and SARIF support as optional extras. Install `bandit[toml,sarif]` in the locked development environment, and confirm the pinned version supports the formatter by running the command in a clean CI environment. GitHub code scanning can ingest SARIF using `github/codeql-action/upload-sarif` after appropriate permissions are granted. If the formatter is not available, do not rename JSON to `.sarif`; install the supported extra or use a reviewed converter.

### 3.2 Common rule IDs (illustrative, not exhaustive)

| Rule | Typical concern | First response |
|---|---|---|
| `B101` | `assert` used in production code | Replace security-critical assertions with explicit checks and exceptions; test-only asserts may be appropriate |
| `B105` / `B106` / `B107` | Possible hard-coded password in a string, argument, or default | Determine whether it is a real credential; move secrets to an approved secret source and rotate any exposed credential |
| `B301` | Risky pickle-related deserialization | Use a non-executable data format or tightly controlled trusted-artifact design |
| `B303` / `B324` | Weak or inappropriate cryptographic hash usage | Choose a modern primitive based on the requirement; legacy hashes may be acceptable for non-security checks only |
| `B307` | `eval` usage | Replace with a parser/allow-list or remove dynamic evaluation |
| `B602` | Subprocess call with `shell=True` | Prefer an argument list with `shell=False`; validate options and executable separately |
| `B603` | Subprocess call without a shell | Review executable/argv trust boundaries; this is a review prompt, not proof of exploitability |
| `B605` / `B606` / `B607` | Shell/process calls and executable resolution concerns | Check shell use, absolute executable path, PATH, and user-controlled arguments |
| `B608` | Possible SQL string construction | Use parameterized SQL and review query composition |
| `B110` | `try/except/pass`-style suppression patterns | Avoid silently swallowing security-relevant failures |

Rule mappings and messages evolve; consult the installed Bandit documentation for the precise rule semantics. Severity is Bandit’s estimate of impact, while confidence estimates confidence in the pattern match. Neither is the same as exploitability in your application. A medium-severity, high-confidence finding on an attacker-controlled path may deserve more urgency than a high-severity, low-confidence pattern in unreachable test code.

### 3.3 Configuration and baselines

Keep configuration explicit and narrow. Example `pyproject.toml` sections:

```toml
[tool.bandit]
exclude_dirs = [".venv", "build", "dist"]
# Do not add broad skips merely to make CI green.

[tool.ruff]
target-version = "py313"  # Match the project's actual minimum supported Python.

[tool.ruff.lint]
select = ["E", "F", "S"]

[tool.ruff.lint.per-file-ignores]
# Only test code may use assert statements for test assertions.
"tests/**/*.py" = ["S101"]
```

Use a target version that matches the project’s declared minimum, not necessarily the interpreter currently running CI. Ruff’s rule namespace and configuration syntax are versioned; validate configuration with the pinned Ruff release. Do not suppress `S101` globally, because production assertions can be optimized away.

A Bandit baseline is useful for legacy code. Generate it using the same severity threshold as the CI scan, review it, commit it, and use it to distinguish existing findings from new ones:

```bash
uv run bandit -r src -ll -f json -o bandit-baseline.json
# After human review, compare future scans with the committed baseline:
uv run bandit -r src -ll -b bandit-baseline.json
```

Baselines are not remediation. Assign owners and due dates for legacy findings, review changes to the baseline like code, and never regenerate it automatically on every pull request. A new finding should fail the gate according to policy.

### 3.4 `# nosec`: narrow, justified exceptions

A `# nosec` comment suppresses Bandit on that line. It is not a fix. If an exception is truly needed, name the specific rule and state the reason in the code and in the exception record. Example format only:

```python
# This test asserts that our wrapper rejects shell mode; no subprocess is executed here.
example = "subprocess.run(command, shell=True)"  # nosec B602 - inert test fixture string, not executed
```

This example is a **string fixture**, not an actual call. Do not use `# nosec` for real code merely because the input “should be safe.” If the line truly triggers a finding, prefer restructuring the test or adding a precise scanner fixture. A real exception should include owner, scope, rationale, compensating control, review date, and expiry in the repository’s exception registry. Run periodic scans with `--ignore-nosec` during review to discover suppressions that need scrutiny.

---

## 4. Ruff `S`, pip-audit, and secret scanning

### 4.1 Ruff `S` rules

Ruff’s `S` rules port checks from flake8-bandit and run quickly alongside normal linting:

```bash
uv run ruff check --select S src tests
```

Use them continuously in editor/pre-commit/CI. Ruff and Bandit overlap but are not identical in rule coverage, context, configuration, or reporting. Run both if the project policy calls for both. Avoid treating duplicate findings as separate vulnerabilities; link them to one triage ticket.

Test-specific exceptions should be explicit and minimal. `assert` is a core testing idiom, so a per-file `S101` ignore for `tests/**/*.py` is often reasonable. Do not ignore all security rules in tests: tests can leak secrets, use unsafe subprocesses, or accidentally ship dangerous helpers.

### 4.2 `pip-audit`: known vulnerability matching

`pip-audit` checks Python distributions against vulnerability data sources, including the Python Packaging Advisory Database and OSV data depending on configuration/version. It can inspect the active environment or a requirements input. It reports known matches, not every defect.

Typical uses:

```bash
# Current interpreter environment
uv run pip-audit --strict

# Explicit requirements input
uv run pip-audit --strict -r requirements.txt

# JSON report (confirm options against the pinned version)
uv run pip-audit --strict --format json -o pip-audit.json
```

The command’s default exit behavior, `--strict`, format names, and supported input formats can vary by release. In CI, test the exact pinned version and document the intended exit policy. `--strict` makes dependency-collection failures fail the audit; it is not a “scan more deeply” switch and does not by itself guarantee that every policy violation causes a non-zero exit. Do not infer that the scan is complete just because it exits zero.

**Understand the scanned set:**

- Installed-environment scan: reflects packages installed in that environment; it may include tools not shipped at runtime and may omit packages installed in other environments.
- Requirements/lock scan: reflects only the dependencies represented in that input. A lockfile may use a format the scanner does not consume directly; export it to a supported requirements format or use a supported integration.
- Runtime-only scan: may intentionally omit dev dependencies, but build and CI dependencies still create supply-chain risk. Scan them in a separate job or environment.
- Advisory matching: depends on package name/version normalization, advisory coverage, and database freshness. Forks, backports, vendored code, platform-specific distributions, and false-positive matches may require manual review.

`pip-audit --fix` can suggest or apply package upgrades in supported workflows, but do not run automatic fixes blindly in CI. Review the proposed version changes, compatibility, lockfile changes, tests, and transitive dependency effects. An upgrade is not complete until the repository rebuilds and its tests pass.

### 4.3 Secret scanning

Use more than one point in the lifecycle:

- `detect-secrets` can build a baseline and check new changes against it. A baseline can contain fingerprints/metadata; review the actual file before committing.
- Gitleaks can scan repository history with `gitleaks git . --redact`; scan the working tree separately with the pinned release’s directory mode when needed. Its CLI changed in v8.19.0: `detect` is deprecated but remains available in some releases. Pin the CLI and verify syntax before CI enforcement.
- GitHub secret scanning can add hosted detection and provider-specific revocation/validity signals when enabled and supported.
- `pre-commit` catches many accidental additions before commit, but hooks can be bypassed. CI and hosted scanning remain necessary.

Example `.pre-commit-config.yaml` (replace every placeholder revision with a reviewed, real tag or immutable commit SHA):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: <REVIEWED_RUFF_PRE_COMMIT_REV>
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/PyCQA/bandit
    rev: <REVIEWED_BANDIT_REV>
    hooks:
      - id: bandit
        args: ["-ll"]
        pass_filenames: true

  - repo: https://github.com/Yelp/detect-secrets
    rev: <REVIEWED_DETECT_SECRETS_REV>
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: <REVIEWED_PRE_COMMIT_HOOKS_REV>
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
```

The `<...>` values are deliberate placeholders, not valid revisions. Replace them before use. Hook IDs and supported args must be verified against the selected repository revision. Run `pre-commit validate-config`, `pre-commit run --all-files`, and commit the validated config. Add Gitleaks as a separate pinned CLI or supported hook if desired; avoid maintaining two conflicting secret baselines without an owner.

**If a real secret is committed:** revoke or rotate it first, immediately assess what it could access, and notify the owner/security team. Then remove it from current files and, if appropriate, clean repository history. History rewriting does not revoke the credential; forks, caches, CI logs, package artifacts, and clones may retain copies. Preserve incident evidence and follow the organization’s response procedure. Do not paste the secret into tickets, chat, logs, or the scanner exception.

---

## 5. Triage, fixes, exceptions, and legacy baselines

### 5.1 A repeatable triage workflow

1. **Confirm the finding.** Identify the exact file, line, rule ID, tool version, and scanned revision. Re-run narrowly if needed.
2. **Identify the sink and source.** Is attacker-controlled input involved? Does it reach a dangerous API? Is there validation or a safer wrapper?
3. **Assess severity and confidence.** Understand the scanner’s definitions; do not confuse its labels with your organization’s risk rating.
4. **Assess reachability and exposure.** Is the code executed in production? Is the component installed? Is the vulnerable function reachable from an untrusted request or job? Are runtime mitigations effective?
5. **Check exploitability and impact.** Consider authentication requirements, privileges, data sensitivity, network exposure, and available public exploit evidence. Tools such as EPSS and CISA KEV can inform priority but do not replace local analysis.
6. **Choose a response.** Prefer removing the unsafe pattern or upgrading the dependency. If no fix exists, reduce exposure, document the risk, add tests/monitoring, and set an expiry.
7. **Prove the fix.** Add a regression test, re-run the scanner, run relevant tests, and review the diff.
8. **Record ownership.** Assign a person/team and deadline. Exceptions without an owner and review date are unowned risk.

A practical priority model is:

`priority = impact × exposure × exploitability`, adjusted by confidence, reachability, and compensating controls.

This is a prioritization aid, not a mathematically precise score. A high-severity CVE in an unreachable optional parser may be lower urgency than a medium-confidence command-injection finding in a public endpoint. Still, “dev dependency” is not an automatic exemption: build tools and CI packages execute with valuable permissions.

### 5.2 Fix, suppress, or accept?

| Choice | Appropriate when | Required evidence |
|---|---|---|
| Fix | The pattern is unsafe or the dependency has a compatible fix | Code change/version bump plus regression/compatibility tests |
| False-positive disposition | The finding does not represent the reported issue in this context | Explanation tied to exact rule, line, data flow, and tool version; reviewer approval |
| Temporary risk acceptance | No timely fix exists and the risk is understood | Owner, scope, impact, compensating controls, approver, expiry, review date |
| Baseline existing issue | Legacy issue is known but not yet fixed | Stable baseline, ticket/owner/deadline, policy that new findings still fail |

Do not use a blanket `# nosec`, broad Semgrep exclusion, or giant allow-list to silence a difficult report. Exceptions should be specific and expire. If a vulnerability advisory has no fixed version, record the affected range, determine whether the vulnerable code is reachable, consider a temporary mitigation or dependency replacement, and monitor for a fix. Remove the exception when the dependency is upgraded or the risk no longer applies.

### 5.3 Suggested service-level objectives

The roadmap gives an example policy of **critical: 7 days; high: 30 days**. Treat these as an organizational starting point, not a universal law. Define your own SLA, including what happens when a fix is impossible. Track mean time to remediate, overdue exceptions, recurring rule families, dependency age, and newly introduced findings. Metrics should encourage fixes, not reward hiding findings.

---

## 6. Pre-commit and CI security gate

### 6.1 Gate design

A practical pull-request gate should:

- Run on the same locked tool versions as local development.
- Scan application source, tests, notebooks, dependency manifests/lock exports, and repository history where appropriate.
- Fail on the findings selected by each configured threshold and on scanner execution errors; distinguish a tool outage from a clean scan. The workflow below runs Bandit at medium severity and above, so it may also fail on medium findings. To fail only on new findings in a legacy repository, configure a reviewed baseline or a separate baseline-diff gate; do not claim new-only behavior without implementing it.
- Publish reports for review, but redact secrets and restrict artifact access.
- Use required status checks so merging cannot bypass the gate.
- Run deeper/nightly scans and container/artifact scans in addition to PR checks.

Start with a small deterministic gate. Add expensive or noisy scanners only when there is an owner and triage process.

### 6.2 GitHub Actions example

This is an implementation template, not a verified drop-in workflow. Replace placeholder action SHAs with reviewed immutable SHAs and adapt the Python version to your support matrix. The example assumes `pyproject.toml` and `uv.lock` are committed, Gitleaks is installed as a pinned binary, and Bandit’s pinned formatter supports SARIF. It fails on the configured scanner findings rather than implementing a new-findings-only baseline gate.

```yaml
name: Security
on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "23 4 * * 2"

permissions:
  contents: read

jobs:
  security:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write # required for SARIF upload
    steps:
      - uses: actions/checkout@<REVIEWED_IMMUTABLE_SHA>
        with:
          fetch-depth: 0 # needed if the secret scanner should inspect history

      - uses: astral-sh/setup-uv@<REVIEWED_IMMUTABLE_SHA>
        with:
          enable-cache: true

      - uses: actions/setup-python@<REVIEWED_IMMUTABLE_SHA>
        with:
          python-version: "3.13" # match the project support policy

      - name: Install locked environment
        run: uv sync --locked

      - name: Ruff security rules
        run: uv run ruff check --select S src tests

      - name: Bandit SARIF
        run: uv run bandit -r src -ll -f sarif -o bandit.sarif

      - name: Upload Bandit SARIF
        uses: github/codeql-action/upload-sarif@<REVIEWED_IMMUTABLE_SHA>
        if: >-
          always() && hashFiles('bandit.sarif') != '' &&
          (github.event_name != 'pull_request' ||
           github.event.pull_request.head.repo.full_name == github.repository)
        with:
          sarif_file: bandit.sarif

      - name: Test suite
        run: uv run pytest

      - name: Audit installed development/build environment
        run: uv run pip-audit --strict

      - name: Audit runtime dependency export
        run: |
          uv export --locked --no-dev --format requirements.txt -o runtime-requirements.txt
          uv run pip-audit --strict -r runtime-requirements.txt

      - name: Custom Semgrep rule
        run: uv run semgrep --error --config .semgrep/requests-timeout.yml src tests

      - name: Test Semgrep rule fixtures
        run: uv run semgrep --test .semgrep/requests-timeout.yml

      - name: Secret scanning
        run: gitleaks git . --redact
```

**Before adopting:**

- Action references are placeholders and will not run until replaced. Pin actions to a reviewed commit SHA, not an invented hash.
- Install Gitleaks as a pinned, verified binary or use a maintained action pinned to a SHA. The example assumes the `gitleaks` executable is already available; add the installation step your organization approves.
- SARIF upload requires repository/code-scanning support and appropriate permissions. The example skips upload for pull requests from forks because their token permissions may not permit SARIF upload; the scan itself still runs. If the report is missing because the scanner failed, the job must not silently pass. Verify the `hashFiles`/event condition in the actual repository workflow.
- The workflow uses the project-pinned `pip-audit` tool through `uv run`, rather than fetching a floating scanner version at runtime. It audits both the installed development/build environment and a runtime-only export.
- Gitleaks command flags differ across releases; this workflow uses the modern `gitleaks git . --redact` command. Verify it against the pinned CLI and add a directory scan if uncommitted/generated working-tree files are in scope.
- The runtime export and installed-environment scan intentionally answer different questions; verify that both environments reflect the dependency groups your policy requires.
- A real workflow should run unit and security regression tests and use an explicit strategy for baselines and “new findings only.”

### 6.3 Failure policy and SARIF

A scanner can fail for two fundamentally different reasons: it found a policy violation, or it could not complete. Both need visible CI status; neither should be treated as clean. SARIF is a standardized result format that can associate findings with source locations and rule metadata. Use it for annotations/code scanning, but keep a human-readable report and an issue-triage workflow too.

For a baseline-aware rollout, define a trusted baseline from a reviewed commit and compare subsequent scans against it. Never let unreviewed pull-request code rewrite the baseline used to judge that same pull request. Baselines should shrink over time as issues are fixed.

---

## 7. Dependency and software supply-chain controls

### 7.1 Lock, hash, minimize, review

- **Lock dependencies.** Commit `uv.lock` or the lockfile used by the chosen package manager. Review lockfile diffs like code.
- **Verify hashes.** Use the package manager’s supported lock integrity and hash verification. For pip requirements workflows, `pip-compile --generate-hashes` can generate hash-pinned requirements. Do not hand-maintain partial hashes.
- **Minimize dependencies.** Every dependency adds code, transitive dependencies, update burden, and possible build-time execution.
- **Review provenance.** Check package name carefully, maintainers, release history, project URLs, source repository, release artifacts, ownership changes, and whether the package is an expected dependency. Popularity is one signal, not a trust guarantee.
- **Watch for typosquatting and dependency confusion.** Verify exact names and use controlled private indexes/mirrors with clear namespace rules.
- **Review licenses.** Use organization-approved policy and preserve notices. A scanner’s license classification may require legal review.
- **Automate updates.** Dependabot/Renovate PRs should run tests, scans, and compatibility checks. Avoid merging blindly based on a green bot status.
- **Consider release-age delay.** A minimum release-age policy can reduce exposure to newly published malicious packages, but it delays security fixes too. Define emergency exceptions for urgent patches and use a trusted mirror/allow-list where needed. Exact support depends on package manager/version; verify the feature before promising enforcement.
- **Treat source builds as code execution.** Source distributions and build backends can execute code during builds. Prefer trusted wheels where feasible, isolate builds, and review unusual build requirements. `--only-binary :all:` can be useful when supported packages exist, but it may make installation impossible for some dependencies and is not a universal policy.
- **Verify artifacts.** Generate an SBOM, retain provenance/attestation where available, sign release artifacts, and verify signatures/attestations at deploy. Signing proves a relationship to a key/identity, not that the artifact is benign.

### 7.2 Vulnerability matching and no-fix cases

A dependency finding requires context:

- Is the package present in the deployed artifact or only in a developer environment?
- Is the vulnerable code path reachable with the current configuration and inputs?
- Is the vulnerable feature disabled, and is that disablement tested and monitored?
- Is there a patched version, safe backport, vendor advisory, or replacement?
- Does the organization’s policy require immediate blocking regardless of reachability?

Do not ignore a transitive dependency because your code does not import it directly. Another dependency may call it, or an optional feature may become reachable after a configuration change. If no fix exists, document the affected version range, exposure, mitigation, owner, review date, and expiry. Monitor advisory updates and remove the exception after remediation.

### 7.3 Other tools: where they fit

| Tool | Main use | Important limitation |
|---|---|---|
| **Semgrep** | Fast pattern and data-flow rules; custom organization policies | Rule coverage depends on language mode, rule quality, and data-flow model |
| **CodeQL** | Semantic code queries and data-flow analysis in supported languages/platforms | Requires setup and query coverage; not all repositories/platforms have the same features |
| **OSV-Scanner** | Match dependency manifests/lockfiles to OSV advisories | Input format and lockfile support must match the project |
| **Trivy / Grype** | Container, filesystem, SBOM and package vulnerability scanning | Results depend on artifact contents, database freshness, and configuration |
| **Safety / Snyk** | Dependency vulnerability and policy workflows; some capabilities are commercial | Data sources, coverage, licensing, and policy features vary by product/plan |
| **mypy / pyright** | Type checking that can catch invalid assumptions and some error paths | Type correctness is not security correctness; runtime validation is still needed |
| **`ruff` `UP` / `pyupgrade`** | Modernize syntax and remove legacy patterns | Modern syntax is not automatically safer |
| **vulture** | Identify potentially unused code | False positives and dynamic use require review |
| **deptry** | Detect unused/missing dependency declarations | Does not replace vulnerability scanning |
| **nbqa / notebook scanners** | Apply linters/security checks to notebook code | Notebook outputs and metadata may still contain secrets or sensitive data |
| **ModelScan / picklescan** | Inspect selected model artifacts for risky patterns | Artifact scanning is incomplete; use safe formats and isolation as well |

Choose tools based on your threat model and ability to act on findings. Two overlapping tools with no triage owner can create more alert fatigue than assurance.

### 7.4 What static analysis cannot prove

Static analysis may miss authorization defects, multi-step business-logic abuse, unsafe defaults supplied only at runtime, dynamic SSRF/DNS rebinding, incorrect tenant isolation, races, and vulnerabilities in external services. Data-flow and taint analysis are approximations; custom wrappers and framework conventions can affect detection. Use security regression tests, integration tests, property-based/fuzz testing, manual review, DAST against authorized staging systems, runtime monitoring, and architecture controls.

For AI/data pipelines, include notebook source **and outputs**, prompt/config templates, model/dataset manifests, external model download hashes, PII/licensing review, and artifact scanning. Never assume a prompt template or downloaded model is trusted merely because the application source passed SAST.

---

## 8. Hands-on lab: scan, triage, fix, and gate `vulnpy`

### 8.1 Lab goals

You will introduce harmless, local examples of patterns a scanner can flag; observe which tool catches each pattern; fix the issue; add regression coverage; and verify that CI rejects a newly introduced finding. Do not place real credentials in the repository. Keep the lab checkout disposable and do not expose the sample service to a public network.

### 8.2 Seed a small finding set

Create `src/vulnpy/security_examples.py`:

```python
"""Tiny local fixtures for learning scanner output; do not use as app code."""
import subprocess


def run_report_tool(user_value: str) -> None:
    # VULNERABLE / LAB ONLY: user input reaches a shell command.
    # This is intentionally seeded for Bandit; do not call it in the lab.
    subprocess.run("echo " + user_value, shell=True, check=False)


def parse_legacy_payload(text: str):
    # VULNERABLE / LAB ONLY: dynamic evaluation of input.
    # Do not call this function; a scanner should be able to inspect it statically.
    return eval(text)
```

Do not execute either vulnerable function. They are static-analysis fixtures only. Run:

```bash
uv run bandit -r src -f json -o /tmp/bandit-lab.json
uv run ruff check --select S src
```

The exact findings and exit status depend on the pinned scanner versions and configuration. Do not assume a specific output line or count; inspect the generated reports and record the actual rule IDs and locations. These commands are examples only; this lesson audit did not execute Bandit, Ruff, pip-audit, detect-secrets, Gitleaks, Semgrep, or GitHub Actions.

### 8.3 Fix the examples rather than suppressing them

If the report tool’s legitimate job is to echo a value, no subprocess is needed. Replace the first function with a library operation or remove it. For a real external tool that genuinely must run, use an absolute/controlled executable and argv list, keep `shell=False`, set a timeout, check the return code, validate arguments against the tool’s own option grammar, and bound captured output. `shell=False` avoids shell parsing but does not prevent option injection into the target program.

Replace dynamic `eval` with a data parser such as `json.loads` when the accepted input format is JSON:

```python
import json
from typing import Any


def parse_payload(text: str) -> Any:
    """Parse JSON data; never evaluate Python expressions from untrusted input."""
    return json.loads(text)
```

Add regression tests:

```python
import json
import pytest

from vulnpy.safe_payload import parse_payload


def test_parse_payload_accepts_json_object() -> None:
    assert parse_payload('{"status": "ok"}') == {"status": "ok"}


def test_parse_payload_rejects_python_expression() -> None:
    with pytest.raises(json.JSONDecodeError):
        parse_payload("__import__('os').getcwd()")
```

These tests demonstrate that JSON data is accepted and Python expression syntax is rejected by the JSON parser. They do not prove all application logic is secure.

### 8.4 Triage worksheet

For every finding, fill in:

| Field | What to record |
|---|---|
| Tool/rule | Tool name, version, rule ID, severity/confidence |
| Location | File, line, commit SHA |
| Source → sink | Where input originates and which sensitive API receives it |
| Reachability | How a request/job/config can reach the code |
| Impact/exposure | Privileges, data, network, tenant boundaries, attacker requirements |
| Decision | Fix, false positive, baseline, or temporary acceptance |
| Evidence | Test, code review, dependency advisory, or runtime mitigation |
| Owner/expiry | Named team/person, due date, exception expiry/review date |

Do not use “scanner false positive” as the entire justification. Explain the context that makes the rule inapplicable and obtain a reviewer’s approval.

### 8.5 Demonstrate a gate failure safely

1. Start with the seeded vulnerable file and run the same command CI will run. Save the report and exit status.
2. Verify the job fails under your policy. If the scanner reports findings but exits zero by default, add an explicit report-policy step or configure the tool’s exit behavior so the gate truly fails; do not assume every reporting mode returns non-zero for every finding.
3. Fix the vulnerable code, add tests, and re-run the gate.
4. Confirm the pipeline passes only after the code and tests are fixed.
5. Keep the original finding report as a lab artifact only if it contains no secrets. Document which tools detected which seeded issues in a detection matrix.

### 8.6 Detection matrix

| Seeded issue | Bandit | Ruff `S` | Semgrep custom rule | Test/review |
|---|---|---|---|---|
| Shell subprocess | Record actual result | Record actual result | Not covered by the HTTP rule below | Review argv, shell, options, timeout |
| `eval` on text | Record actual result | Record actual result | Not covered by the HTTP rule below | Regression test for data parser |
| HTTP call without timeout | May or may not flag depending on call/API/rule | Check enabled rules | Covered by custom rule below for matched syntax | Test timeout/error behavior |
| Hard-coded secret marker | Scanner-specific; do not rely on SAST alone | Not a secret scanner | Not covered | `detect-secrets` / Gitleaks |
| Known vulnerable dependency | Not covered | Not covered | Not covered | `pip-audit` / SCA tool |

Fill the matrix from actual output in your own pinned environment. Never invent detections. A tool failing to catch a seeded issue is valuable information about coverage, not a reason to alter the recorded result.

---

## 9. Custom Semgrep rule, test fixtures, and code-review checklist

### 9.1 Rule: require `timeout=` for `requests.get`

This starter rule flags direct `requests.get(...)` calls that do not syntactically include a `timeout` keyword. It is intentionally narrow: it does not understand every alias, wrapper, or runtime timeout policy. Centralizing HTTP calls behind a reviewed client is stronger than relying on this rule alone.

Create `.semgrep/requests-timeout.yml`:

```yaml
rules:
  - id: python.requests-get-requires-timeout
    languages: [python]
    severity: ERROR
    message: "Use a bounded timeout for requests.get; prefer the project's reviewed safe_http wrapper."
    metadata:
      category: security
      cwe: "CWE-400"
      confidence: MEDIUM
    patterns:
      - pattern: requests.get(...)
      - pattern-not: requests.get(..., timeout=$TIMEOUT, ...)
```

Create `.semgrep/requests-timeout.py` alongside the rule file, using Semgrep test annotations (the test fixture should be discoverable by the pinned Semgrep release):

```python
import requests


def unsafe(url: str):
    # ruleid: python.requests-get-requires-timeout
    return requests.get(url)


def safe_syntax(url: str):
    # ok: python.requests-get-requires-timeout
    return requests.get(url, timeout=(2.0, 5.0))
```

Run:

```bash
uv run semgrep --test .semgrep/requests-timeout.yml
uv run semgrep --error --config .semgrep/requests-timeout.yml src tests
```

The `--test` command verifies the positive and negative fixture annotations for the rule; keep the fixture beside the rule and confirm that your pinned Semgrep release discovers it. Confirm syntax with the pinned Semgrep release; rule-pattern behavior can vary with language support. This rule does not prove that the timeout values are appropriate, that redirects/response sizes are bounded, or that DNS/SSRF policy is enforced. It can also miss aliased imports (`import requests as r`) and calls routed through wrappers. Expand tests before widening the rule.

### 9.2 Secure code-review checklist

- [ ] **Inputs:** Are HTTP bodies, files, headers, database values, environment variables, notebook outputs, model outputs, and configuration treated as untrusted at the boundary?
- [ ] **Authorization:** Is access checked server-side for each object and tenant, not inferred from identifiers or UI state?
- [ ] **Secrets:** Are credentials absent from source, logs, URLs, command arguments, test fixtures, notebooks, and artifacts? Are real leaks revoked/rotated?
- [ ] **Subprocesses:** Are shell strings avoided? Are executable, argv, options, timeout, output, environment, and working directory controlled?
- [ ] **Files:** Are paths contained, symlinks/races considered, uploads size-limited, temp files secure, and archive members validated?
- [ ] **Network:** Are HTTP calls centralized, timeouts/TLS/redirects/size limits configured, and SSRF/egress controls enforced?
- [ ] **Deserialization:** Are untrusted pickle-like formats and dynamic evaluation avoided?
- [ ] **Logging/errors:** Are sensitive values redacted and external errors generic without hiding useful internal diagnostics?
- [ ] **Dependencies:** Are new packages justified, correctly named, maintained, license-reviewed, locked, and audited? Are build steps isolated?
- [ ] **Tests:** Does every fixed vulnerability have a regression test? Are both rejection and legitimate-use cases covered?
- [ ] **Exceptions:** Are suppressions narrow, justified, owned, reviewed, and expiring?
- [ ] **CI/artifacts:** Are checks required, reports retained safely, actions/tools pinned, and build outputs attested or signed as required?

### 9.3 `SECURITY.md` and reporting workflow

The roadmap mini-project requires a `SECURITY.md` describing reporting and SLAs. At minimum, provide a private reporting route, what information to include, a statement not to publish exploit details before coordination, acknowledgement/triage expectations, severity definitions, patch/release process, and escalation path. Do not publish private incident contacts or secrets in the public repository. Keep SLAs consistent with the organization’s policy; the roadmap’s critical 7-day/high 30-day values are examples to consider, not universal guarantees.

---

## 10. Common mistakes, self-check answers, and completion checklist

### 10.1 Common mistakes

- **Blanket `# nosec`:** hides real issues and removes context. Prefer a fix; otherwise suppress only the specific rule with a documented reason and expiry.
- **“The scan passed, so the code is secure”:** scanner coverage is incomplete and logic/runtime flaws remain. Add tests, review, and architecture controls.
- **Ignoring dev dependencies:** build tools and CI dependencies execute code and may access tokens. Audit build/dev environments separately.
- **Running scans without enforcing them:** if findings do not affect merge/release decisions, they are reports—not gates.
- **Treating severity as the full priority score:** incorporate reachability, exploitability, exposure, impact, and compensating controls.
- **Committing baselines without review:** a baseline can silently legitimize newly introduced problems if it is regenerated from an untrusted PR.
- **Using `--fix` blindly:** automated upgrades can break compatibility or change the dependency graph. Review, test, and lock the result.
- **Scanning only `src/`:** notebooks, tests, CI workflows, Dockerfiles, build scripts, lockfiles, generated artifacts, and repository history can carry risk too.
- **Trusting package popularity alone:** popular projects can be compromised; small projects can be legitimate. Review provenance and necessity.
- **Treating a type checker as a security scanner:** types can reduce mistakes but do not prove authorization, input validity, or safe data flow.
- **Using mutable CI action tags in a high-assurance pipeline:** pin reviewed SHAs and update them deliberately.
- **Failing open when a scanner is unavailable:** a failed scan is not a clean scan. Decide whether the gate blocks or requires explicit incident/exception handling.

### 10.2 Self-check answers

**1. Which vulnerability classes can’t Bandit find reliably, and what covers them?**  
Bandit is pattern-oriented and cannot reliably prove business logic, object-level authorization, tenant isolation, complex multi-step abuse, dynamic DNS rebinding/SSRF behavior, runtime deployment policy, or all data flows through custom wrappers. Use security regression/integration tests, code review, Semgrep/CodeQL where suitable, DAST against authorized staging, runtime/network controls, and architecture review. No single tool covers all gaps.

**2. How should you handle a CVE in a transitive dependency with no fixed release?**  
Confirm the package/version and advisory, identify the dependency path and deployed artifacts, assess reachability/exposure/impact, and check vendor advisories or safe backports. If no safe upgrade exists, reduce exposure or disable the affected feature where reliable, add regression/monitoring controls, consider replacement/forking, document owner/approver/expiry, and monitor for a fix. Do not permanently allow-list it without review.

**3. Write a Semgrep rule forbidding `requests.get(...)` without `timeout=` and test it.**  
Use the rule and `ruleid`/`ok` fixtures in Section 9.1. Run `semgrep --test` and the normal scan; expand coverage for aliases/wrappers if your codebase uses them. The rule checks syntax, not the adequacy of the timeout or complete HTTP safety.

### 10.3 Completion checklist

- [ ] I can explain SAST, SCA, secret scanning, and policy-as-code without conflating them.
- [ ] I ran `bandit -r src -ll`, inspected a machine-readable report, and understand severity versus confidence.
- [ ] I enabled Ruff `S` rules and scoped any test-specific exception narrowly.
- [ ] I ran `pip-audit` against both the intended runtime set and the appropriate dev/build environment, or documented why one is not applicable.
- [ ] I configured secret scanning and understand that committed credentials must be revoked/rotated before history cleanup.
- [ ] I triaged a finding end-to-end, preferred a fix, and documented any exception with owner and expiry.
- [ ] I validated pre-commit configuration and CI failure behavior with a seeded issue.
- [ ] I tested the custom Semgrep rule with positive and negative fixtures.
- [ ] I reviewed lockfile/hash policy, dependency provenance, licenses, updates, and release-age trade-offs.
- [ ] I added or verified regression tests for each fixed vulnerability.
- [ ] I created/updated `SECURITY.md` with reporting instructions and remediation SLAs.
- [ ] I completed the `vulnpy` hardening mini-project and wrote a detection matrix showing actual tool results.

---

## Further reading

Use the documentation matching the versions pinned in your repository:

- Bandit: <https://bandit.readthedocs.io/en/latest/> (rules, configuration, baselines, SARIF formatter extra)
- Ruff: <https://docs.astral.sh/ruff/> (lint rules and `S` rule selection)
- pip-audit: <https://github.com/pypa/pip-audit> (supported inputs, advisory sources, formats, exit behavior)
- detect-secrets: <https://github.com/Yelp/detect-secrets> (baseline workflow)
- Gitleaks: <https://github.com/gitleaks/gitleaks> (CLI syntax and history scanning)
- pre-commit: <https://pre-commit.com/> (hook configuration and validation)
- Semgrep: <https://semgrep.dev/docs/> (rule syntax and test fixtures)
- OSV-Scanner: <https://google.github.io/osv-scanner/> (supported manifests and advisories)
- GitHub code scanning/SARIF: <https://docs.github.com/en/code-security/code-scanning> (permissions, supported SARIF, upload behavior)

Treat external documentation as version-specific: check the release actually locked by your project before copying a flag or configuration field into a required gate.
