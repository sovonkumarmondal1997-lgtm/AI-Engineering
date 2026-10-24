# PROMPT — Generate `SYLLABUS-ci-cd-architecture-and-pipeline-design-principles.md`

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a capable, long-context LLM. The output is very large, so the prompt uses a multi-part Delivery Protocol (Section 14).

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior DevOps Engineer and SRE with 15 years of production experience** designing and operating CI/CD systems for data and ML organizations. You have migrated Jenkins estates to hosted CI, cut 45-minute pipelines to 6, handled leaked-token incidents on runners, fixed flaky-test epidemics, and owned release processes with audit requirements. You teach with **evidence over opinion, safe defaults, and every claim verifiable.**

You are also a careful technical author. You never invent a workflow key, a keyword, a default, a quota, or a version. When unsure, you say so and mark it `[VERIFY]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 2E — Production DevOps & Platform Engineering / 02-CI-CD-Pipeline-Engineering/` (module code **M02**)

Output file name: **`SYLLABUS-ci-cd-architecture-and-pipeline-design-principles.md`** (use this exact name even though it covers the whole folder).

It must teach, **one after another, from beginner to advanced**, these 15 units in this exact order:

| # | Unit | Target file |
|---|---|---|
| 0 | Folder orientation | `README.md` |
| 1 | CI/CD architecture and pipeline design principles | `01-ci-cd-architecture-and-pipeline-design-principles.md` |
| 2 | GitHub Actions: workflows, runners, reusable workflows | `02-github-actions-workflows-runners-and-reusable-workflows.md` |
| 3 | GitLab CI: stages, jobs, templates | `03-gitlab-ci-stages-jobs-and-templates.md` |
| 4 | Build caching, parallelism, and pipeline speed | `04-build-caching-parallelism-and-pipeline-speed.md` |
| 5 | Monorepo and path-based pipelines | `05-monorepo-and-path-based-pipelines.md` |
| 6 | Test stages, quality gates, flaky-test management | `06-test-stages-quality-gates-and-flaky-test-management.md` |
| 7 | Artifact repositories and package publishing | `07-artifact-repositories-and-package-publishing.md` |
| 8 | Semantic versioning, changelogs, release automation | `08-semantic-versioning-changelogs-and-release-automation.md` |
| 9 | Environment promotion, approvals, protected branches | `09-environment-promotion-approvals-and-protected-branches.md` |
| 10 | Self-hosted runners: scaling and security | `10-self-hosted-runners-scaling-and-security.md` |
| 11 | Pipeline observability and DORA delivery metrics | `11-pipeline-observability-and-dora-delivery-metrics.md` |
| 12 | Practice questions | `practice-questions.md` |
| 13 | Capstone project | `Projects/README.md` + `Projects/01-multi-stage-ci-cd-pipeline-for-data-and-ml-service.md` |

Do **not** add, merge, skip, or reorder units. This is the **teaching content itself**, not an outline.

# 3. LEARNER AND CONTEXT

- **Learner:** a data/AI engineer who has completed Stages 0–2D and Stage 2E's M01 (container image engineering). They know Git, Linux shell, Python, pytest basics, and can build/push images. They have **not** owned a production delivery pipeline.
- **Stage constraint — zero budget.** All hands-on work runs on a laptop (WSL2 Ubuntu primary, native Linux secondary; ~4 CPU, 8 GB RAM, 30 GB disk) and **free tiers only**. No paid CI minutes, no paid runners, no paid artifact storage. Free-tier limits change: any quota/limit statement must be tagged `[VERIFY]` and never presented as fact.
- **Core tools (hands-on, required):** GitHub Actions, GitHub-hosted or local/self-hosted runner, pytest, Ruff, build/dependency cache, artifact digest/checksum. Supporting: Git, Docker/BuildKit (from M01), `act` or equivalent for local workflow runs (optional helper, `[VERIFY]` fidelity limits), `actionlint` (optional linter).
- **Tooling-map note:** the stage tooling map lists GitLab CI/CD, Jenkins, and remote caches as **Awareness**. Because this folder contains a dedicated GitLab unit, teach GitLab CI **at working depth**, using the free gitlab.com tier and/or local `gitlab-runner` and/or `gitlab-ci-local` `[VERIFY]` — but state clearly that GitHub Actions is the primary Core platform and GitLab is taught for concept transfer and cross-platform fluency. Jenkins, Buildkite, CircleCI, Tekton, Argo Workflows, Dagger, Earthly: **Awareness only** (comparison table, no labs).
- **Domain flavor:** a Python FastAPI model-serving service, a batch ETL package, and a small ML training/evaluation job (with data-validation and model-metric gates). Use realistic data/ML delivery concerns: dataset/model artifact versioning, schema checks, non-determinism in ML tests, heavy dependencies (numpy/pandas/pyarrow/scikit-learn), large artifacts.
- **Cross-module links:** M01 (images, digests, registries) is the build target; forward to M06 (Helm/Kustomize), M08 (GitOps/progressive delivery — CD handoff), M09 (secrets/identity, OIDC), M10 (SRE/SLOs), M11 (observability), M12 (supply-chain security: signing, SLSA), M17 (capstone). State clearly what is **taught here vs. deferred** so nothing is half-covered. CI/CD here ends at "produce a verified, promotable artifact and request deployment"; reconciliation-based delivery belongs to M08.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1–11)

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Explains the concept, runs/reads a minimal working example. |
| **L2** | Intermediate — Working Practice | Builds a correct, maintainable pipeline for a real data/ML service. |
| **L3** | Advanced — Production Engineering | Designs, measures, secures, and defends choices under constraints (speed, cost, risk, scale). |
| **L4** | Expert — Operating at Scale and Under Failure | Diagnoses pipeline failures and incidents, writes policy/automation, standardizes across teams. |

# 5. MANDATORY STRUCTURE FOR EACH UNIT 1–11

Use this exact skeleton, same headings, same order, in every unit. If a section is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Awareness:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in production
(3–6 sentences; a concrete failure, cost, or risk this prevents. No hype.)

### N.1 Learning objectives
(6–10 measurable outcomes, each beginning with an action verb and tagged L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception. One mermaid/ASCII diagram of the mechanism.)

### N.3 Level 1 — Beginner
- First-principles explanation (how the system works, not just syntax)
- Guided lab: exact files, commands, expected output, how to read the result
- "What just happened?" walkthrough
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Complete, runnable pipeline files for the data/ML running example
- Pattern catalogue: pattern | when to use | when NOT to use
- Anti-pattern catalogue: bad example → why it hurts → corrected version
- Lab with measurable before/after results

### N.5 Level 3 — Advanced
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Security, performance, and reliability techniques
- Measurement method (what to measure, how, how to avoid fooling yourself)
- Lab that requires a defended decision, not a copied snippet

### N.6 Level 4 — Expert
- Failure scenarios (symptom → hypothesis → test → root cause → fix → prevention)
- Policy-as-code and automation (linters, required checks, org-wide templates, config tests)
- Organizational concerns: standards, ownership, migration strategy, review checklists
- Edge cases and platform differences

### N.7 SRE lens
- SLIs/SLOs for this topic (e.g., p95 pipeline duration, queue time, change failure rate, flake rate)
- Failure modes and blast radius
- Runbook snippet: alert → triage → mitigation → follow-up
- Cost and capacity notes

### N.8 Security lens
- Threats addressed (map to CI/CD threat categories, e.g., OWASP Top 10 CI/CD Security Risks, SLSA concepts) and what is NOT addressed
- Controls and how to verify each with a concrete check

### N.9 Production checklist
(Checkbox list the learner applies to a real repository; every item verifiable.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch. Idempotent; safe to re-run; no paid resources.)

### N.11 Self-check questions
(6–10 questions with concise answer keys and a note on why wrong options are tempting.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves to prove completion.)

### N.13 Common interview and design-review questions
(5 questions with senior-level model answers.)

### N.14 Sources and verification notes
(Official docs consulted by name and section; [VERIFY] items; version-sensitive claims.)
```

# 6. MODULE-SPECIFIC CONTENT REQUIREMENTS

Minimum topics. Add depth, never remove.

## Unit 1 — CI/CD architecture and pipeline design principles
- **L1:** integration vs delivery vs deployment (precise definitions, common confusion); trunk-based vs long-lived branches; what a pipeline is (trigger → stages → jobs → steps → artifacts → status); fast-feedback principle; pipeline-as-code; "build once, deploy many"; a first minimal pipeline (lint + test).
- **L2:** pipeline stage design for a data/ML service (lint → unit test → build → integration test → package → scan → publish → deploy-request); fail-fast ordering; idempotent, hermetic jobs; separating CI from CD concerns; environment parity; configuration vs code vs secrets; branching/merge-request workflows; required status checks; pipeline-as-code review.
- **L3:** design principles with trade-offs (speed vs safety, monolithic vs composable pipelines, push- vs pull-based delivery—forward ref M08); artifact immutability and promotion by digest (link M01); deterministic builds; pipeline DAG design (`needs`, parallel fan-out/fan-in); failure isolation; blast-radius thinking; idempotent deploy steps; rollback as a first-class path; ML-specific stages (data validation, model evaluation gate, model registry handoff) — present as design patterns, with explicit scope limits (full MLOps belongs to later stages).
- **L4:** pipeline architecture reviews; golden-path pipelines and platform-owned templates (forward ref M16); pipeline anti-pattern audit; migration strategy between CI systems; designing for auditability and compliance evidence; scale considerations (thousands of repos); trade-off ADR template; "pipeline as a product" with SLOs.
- **Must include:** a pipeline design review checklist and a worked redesign of a bad 60-minute, linear, secret-leaking pipeline into a fast, safe DAG — with a before/after table whose numbers are derived from stated measurements or labelled `[ILLUSTRATIVE]`.

## Unit 2 — GitHub Actions: workflows, runners, reusable workflows
- **L1:** workflow/event/job/step/action/runner vocabulary; YAML anatomy; triggers (`push`, `pull_request`, `workflow_dispatch`, `schedule`); `runs-on`; `actions/checkout`; contexts and expressions; logs and re-runs; `GITHUB_TOKEN` basics.
- **L2:** matrix builds; `needs` and job outputs; `if:` conditions and status functions; artifacts upload/download; environment variables vs secrets vs variables; `concurrency` and cancel-in-progress; caching with `actions/cache` (details deferred to Unit 4); service containers for integration tests; running pytest + Ruff.
- **L3:** **reusable workflows** (`workflow_call`, inputs, secrets, outputs, versioning by tag/SHA) vs **composite actions** vs custom actions — decision table; least-privilege `permissions:` per job; pinning third-party actions **by full commit SHA** and why; `pull_request` vs `pull_request_target` risks; script-injection through untrusted `${{ github.event.* }}` input and the safe `env:` pattern; OIDC to cloud (concept; forward ref M09); environments and deployment protection (link Unit 9); `workflow_run`; path/branch filters; job timeouts; artifact attestation concept (forward ref M12) `[VERIFY]`.
- **L4:** organization-level reusable-workflow strategy and required workflows; policy enforcement (allowed actions lists, SHA-pinning checks with `actionlint`/custom checks); debugging runner/matrix/permission failures; handling secret exposure in logs; fork-PR threat model; workflow-testing strategy (`act` as optional, with documented fidelity limits); a **workflow review checklist**.
- **Must include:** a lab that demonstrates a script-injection vulnerability in a deliberately vulnerable workflow **inside the learner's own private test repository**, then fixes it; plus a reusable-workflow lab consumed by two caller workflows. Make clear this is defensive education on the learner's own repo only.

## Unit 3 — GitLab CI: stages, jobs, templates
- **L1:** `.gitlab-ci.yml` anatomy; stages and jobs; `script`, `image`, `variables`; runners (shared vs project); pipeline/job statuses; predefined CI variables.
- **L2:** `rules:` (and why legacy `only/except` is not taught as current `[VERIFY]`), `needs:` DAG, `artifacts` vs `cache`, `services`, environments, `parallel:matrix`, `workflow:rules`, merge-request pipelines vs branch pipelines and the duplicate-pipeline pitfall.
- **L3:** templates: `extends`, hidden jobs, YAML anchors, `include` (local/project/remote/template), `!reference`, `spec:inputs`/CI components `[VERIFY]`; `trigger` parent-child and multi-project pipelines; dynamic child pipelines; protected variables and masked/hidden variables; OIDC `id_tokens` concept `[VERIFY]`; auto-cancel and `interruptible`; resource groups for deploy serialization.
- **L4:** shared pipeline library design and versioning; CI linting (`ci lint` / `gitlab-ci-local` `[VERIFY]`); pipeline-efficiency analysis; migrating a GitHub Actions workflow to GitLab CI and back (concept mapping table covering ≥ 15 constructs: events, jobs, matrix, cache, artifacts, secrets, reuse, environments, concurrency, conditions…).
- **Must include:** a translation lab — the Unit 2 workflow re-expressed in GitLab CI with a mapping table and a list of constructs that do **not** map cleanly.

## Unit 4 — Build caching, parallelism, and pipeline speed
- **L1:** why pipelines are slow; critical path; cache vs artifact; cache keys; cold vs warm.
- **L2:** dependency caching for pip/uv/poetry (lockfile-hash keys); Docker layer cache in CI (link M01 Unit 4); restoring partial caches; parallel jobs and sharded tests (`pytest-xdist`, test sharding by timing data); fail-fast and `concurrency` cancel-superseded runs.
- **L3:** cache key design (exact + restore-keys fallback), cache scoping across branches/PRs, cache-size and eviction limits `[VERIFY]`; registry/remote BuildKit cache; **cache poisoning** and trust boundaries (no cache writes from untrusted PRs); measuring pipeline critical path; queue time vs run time; avoiding the "parallelism tax" (setup overhead); right-sizing runners; conditional execution (skip docs-only changes safely).
- **L4:** pipeline performance SLO and regression guard; cost model (minutes × runner multiplier — values `[VERIFY]`, never asserted); ephemeral-runner cache strategies; test-impact analysis (concept) and its risks; incident analysis: "cache restored stale dependencies and masked a break."
- **Must include:** a benchmark method (cold/warm/partial-change, N runs, median/p95) and a script that extracts durations from workflow run data via the `gh` CLI or API `[VERIFY]` and prints a table. Warn about noise (shared runners, network variance).

## Unit 5 — Monorepo and path-based pipelines
- **L1:** monorepo vs polyrepo; why one pipeline per everything does not scale; path filters.
- **L2:** `paths`/`paths-ignore` (GitHub) and `rules:changes` (GitLab); per-service workflows; shared-library change triggering dependents; the **required-check-with-skipped-workflow pitfall** (a path-filtered required check never reporting) and its solutions.
- **L3:** change detection (`git diff` against merge base, `dorny/paths-filter`-style or custom script — pin and `[VERIFY]`); dynamic matrix generated from changed services; dependency-graph-aware builds; shallow clone vs `fetch-depth` correctness for diffs; build-tool affinity (Bazel/Nx/Turborepo/Pants — Awareness); versioning strategy in monorepos (link Unit 8); CODEOWNERS and per-path approvals.
- **L4:** failure analysis: wrong diff base, force-push, squash merges, merge queues; merge-queue interaction `[VERIFY]`; scaling to hundreds of services; policy to guarantee "no change goes untested"; monorepo release trains vs independent releases; migration plan polyrepo → monorepo.
- **Must include:** a lab with a 3-package repo (api, etl, shared-lib) where editing shared-lib triggers all dependents, editing docs triggers nothing, and a required "gate" job always reports.

## Unit 6 — Test stages, quality gates, flaky-test management
- **L1:** the test pyramid; unit vs integration vs end-to-end; pass/fail semantics; exit codes; coverage meaning and limits.
- **L2:** pytest structure, fixtures, markers, parametrization; Ruff lint/format and type-check (e.g., mypy/pyright as optional) gates; coverage thresholds and why a threshold is a floor not a goal; test reports (JUnit XML) and artifacts; integration tests with service containers; test data management.
- **L3:** **quality gates** design (blocking vs advisory, required checks, ratchets, diff-coverage); data-quality gates (schema/contract checks, row-count/freshness assertions, Great-Expectations-style checks — concept with one open-source example `[VERIFY]`); ML gates (metric thresholds with confidence/variance handling, seeded determinism limits, golden-dataset regression tests, model-card checks) — scope-limited; contract testing concept; test environments and hermeticity; security gates (SAST/dependency/secret scan, link M12) as pipeline stages, not full coverage.
- **L4:** **flaky-test management**: define flake rate; detect (rerun-on-fail with quarantine, repeated-run analysis, `pytest-rerunfailures`/`pytest-randomly` `[VERIFY]`), root causes (time, ordering, shared state, network, concurrency, resource limits), quarantine with expiry and owner, and why blind auto-retry hides defects; test-suite SLOs; gate-bypass policy; mutation testing (Awareness); testing in production boundaries (Awareness).
- **Must include:** a lab that plants 3 kinds of flaky tests (order-dependent, time-dependent, resource-race), detects them by repeated randomized runs, fixes them, and wires a flake-report job into the pipeline.

## Unit 7 — Artifact repositories and package publishing
- **L1:** what an artifact is (wheel, sdist, image, SBOM, model file, report); build artifact vs release artifact; why not rebuild per environment.
- **L2:** GitHub Packages / GitLab Package Registry / container registry / PyPI-compatible repositories (local `devpi` or similar `[VERIFY]` and TestPyPI as free options); building Python wheels with `build` and `pyproject.toml`; publishing to a **local** registry/repository for the lab; checksums and `sha256sum`; workflow artifacts vs package registries vs release assets — decision table.
- **L3:** immutability, versioning, and retention for packages; publishing credentials: tokens vs **Trusted Publishing/OIDC** (PyPI `[VERIFY]`); dependency confusion and namespace/proxy risks; internal index vs public fallback (`--index-url` vs `--extra-index-url` pitfalls); promoting artifacts between repositories (snapshot → release); storing large ML artifacts (concept: object storage, DVC/MLflow/registry — Awareness); SBOM generation per artifact (Syft from M01) and attaching to releases; provenance/attestation concept (link M12).
- **L4:** artifact lifecycle policy (retention, GC, legal hold); proxying/caching upstream package indexes for supply-chain resilience; yanking and revoking a bad release (what yank does and does not do); incident: "malicious or broken package published" → contain → rotate → communicate; multi-format repository management (Nexus/Artifactory/Harbor — Awareness).
- **Must include:** a lab that builds a wheel, publishes it to a local index with a token, installs it in a clean venv pinned by hash, then simulates a dependency-confusion misconfiguration **locally** and fixes it.

## Unit 8 — Semantic versioning, changelogs, release automation
- **L1:** SemVer 2.0.0 rules (MAJOR/MINOR/PATCH, pre-release, build metadata, precedence); why versions are contracts; Git tags; release vs tag vs build.
- **L2:** Conventional Commits and commit-message linting (`commitlint`); changelog generation (Keep a Changelog format; tooling such as `git-cliff`, `release-please`, `python-semantic-release`, `semantic-release` — compare, `[VERIFY]` each tool's behavior); GitHub Releases; version stored in one place (`pyproject.toml`) vs derived from tags (`setuptools-scm`/`hatch-vcs` `[VERIFY]`).
- **L3:** fully automated release pipeline (merge to main → compute version → changelog → tag → build → publish → release notes); release PR model vs direct-release model trade-offs; pre-release channels (rc/beta); hotfix and backport flows; versioning for **services** vs **libraries** vs **data schemas** vs **ML models** (what SemVer means for each, and where it breaks, e.g., model versions and data contracts); protecting the release job (protected branches/tags, environment approvals, least-privilege token); idempotent, resumable releases.
- **L4:** failed-partial-release recovery (tag pushed but publish failed); revert/yank policy; monorepo independent versioning (link Unit 5); release-notes quality standards; deprecation policy and compatibility testing; audit trail; CalVer as an alternative (when appropriate).
- **Must include:** a lab with a scripted history of conventional commits that yields the expected next version, changelog, and tag **in a local throwaway repo**, plus a deliberate partial-failure and its recovery runbook.

## Unit 9 — Environment promotion, approvals, protected branches
- **L1:** environments (dev/staging/prod) and purpose; promotion vs rebuild; branch protection basics; what an approval is.
- **L2:** GitHub branch protection/rulesets and GitLab protected branches/tags (required reviews, required status checks, linear history, no force-push, signed commits as option) `[VERIFY]` current UI/field names; GitHub Environments with required reviewers and environment-scoped secrets; GitLab protected environments and manual jobs; CODEOWNERS.
- **L3:** **promotion by digest** through environments with evidence carried forward (test results, scan results, SBOM); approval design (who approves, separation of duties, four-eyes, time-boxed approvals, avoiding approval fatigue); deploy windows; **deployment gates** (health checks, smoke tests, SLO checks — forward ref M10/M11); deploy-request handoff to GitOps (forward ref M08: pipeline updates a manifest/PR rather than pushing to the cluster); emergency/break-glass path with after-the-fact review; drift between environments.
- **L4:** policy-as-code for repository rules (config-as-code for rulesets `[VERIFY]`; audit scripts using `gh api`); admin-bypass risks and detection; compliance evidence (SOC2-style controls — Awareness) generated automatically; failure scenarios (approval bypass via a mis-scoped token, protected-environment misconfiguration, rebuild-instead-of-promote drift, long-lived secret in environment); progressive exposure basics (feature flags/canary — Awareness, forward ref M08).
- **Must include:** a lab promoting one image digest dev → staging → prod (locally simulated as three Compose/kind namespaces or three directories of manifests), proving prod runs the **same digest**, with an approval gate and a deliberately blocked bypass attempt. State which parts are simulated.

## Unit 10 — Self-hosted runners: scaling and security
- **L1:** hosted vs self-hosted runners; what a runner is and does; why self-hosted exist (network access, hardware, cost, control).
- **L2:** register a local self-hosted runner (GitHub and/or GitLab) in the learner's **private test repo**; labels/tags and runner groups; running jobs in containers; cleaning workspaces; updating runners; **ephemeral** vs persistent.
- **L3:** the central security model: self-hosted runners must **never run untrusted code** (public-repo forks) — explain precisely why; persistent-runner contamination, credential reuse, cache/artifact poisoning, Docker-socket exposure, host-network exposure; ephemeral/JIT runners; isolation options (containers, VMs, rootless, gVisor/Firecracker — Awareness); network egress control; secret handling and OIDC over static credentials; least-privilege runner identity; runner-group scoping; logging and audit.
- **L4:** autoscaling architectures: Actions Runner Controller on Kubernetes (forward ref M03), GitLab Runner autoscaling executors, cloud autoscalers — **Awareness with an architecture diagram and a local simulation of the scale-up/scale-down logic, not paid infrastructure**; queue-time-driven scaling; capacity and FinOps model (forward ref M15); fleet patching; image baking for runners; incident: "runner compromised" → isolate → revoke → rotate → rebuild → forensics; threat model using OWASP CI/CD risks.
- **Must include:** a lab running an ephemeral runner (container-based) that processes one job then exits, with a verification that no workspace/credential persists. Include a clearly labeled **safe demonstration** of why persistent runners leak state (benign file left between jobs), with no real exploit tooling.

## Unit 11 — Pipeline observability and DORA delivery metrics
- **L1:** why measure delivery; the four key metrics: deployment frequency, lead time for changes, change failure rate, time to restore service (and the more recent framing of the metrics as published by DORA — state definitions precisely and tag `[VERIFY]` against the current DORA publication); what each does and does not tell you.
- **L2:** collect pipeline data (`gh` CLI / REST API, workflow-run and job timings, `workflow_run` events, JUnit reports); compute duration, success rate, queue time, retry rate; simple dashboards (CSV + Python/pandas + static HTML, or Grafana locally — ties to M11).
- **L3:** computing DORA metrics honestly: defining "deployment", "failure", and "restore" in your context; data sources (deploy events, incidents, reverts); sampling and bias; percentile vs mean; **Goodhart's law** and anti-gaming guidance (metrics for teams, not individuals/performance reviews); pipeline SLIs/SLOs and error-budget-style alerts for the pipeline itself; flake rate, MTTR of pipeline failures; exporting pipeline telemetry (OpenTelemetry for CI — Awareness `[VERIFY]`), Prometheus metrics from a small exporter script.
- **L4:** org-level metrics architecture; tool landscape (Four Keys, Sleuth, LinearB, Faros, GitLab/GitHub built-ins — Awareness, vendor-neutral); cohort analysis and trends; connecting delivery metrics to reliability (SLOs, M10) and cost (M15); using metrics to drive change (identify the constraint, run an experiment, re-measure); incident: "metrics improved but outcomes got worse."
- **Must include:** a lab that computes all four metrics from a provided synthetic dataset **and** from the learner's own test repo's run history, writes a report, and includes a short written interpretation noting at least three ways the numbers could mislead.

# 7. PRACTICE QUESTIONS (Unit 12)

At least **150 questions**: ≥ 12 per Units 1–11 plus ~20 cross-unit integration questions. Per unit:
- 3 × conceptual short-answer
- 3 × multiple choice (4 options; explain every distractor)
- 2 × YAML/config interpretation or output reading
- 2 × pipeline/config review (find ≥ 3 defects, fix them)
- 1 × incident/troubleshooting scenario (symptom → diagnose → fix → prevent)
- 1 × design question with a rubric (Units 3–11; Unit 1–2 get one too)

Each question has ID, level (L1–L4), objective tested, time estimate, **model answer**, **common wrong answers**. Provide a scoring rubric with thresholds (≥ 80% proceed; 60–79% remediate; < 60% repeat), and 8 "design-review" whiteboard prompts requiring written trade-off reasoning. Questions must only test taught content.

# 8. CAPSTONE PROJECT (Unit 13)

**Project:** *Multi-Stage CI/CD Pipeline for a Data and ML Service.*

Deliver `Projects/README.md` (index, grading, evidence submission) and the full spec.

**Scenario:** A data-platform team owns a FastAPI scoring service, a shared Python library, and an ETL package in one repository. Their current process: manual builds, one 50-minute pipeline for everything, tests flake, secrets sit in repository variables, anyone can push to `main`, versions are hand-edited, and nobody knows how often they ship. The learner builds the delivery system that fixes this, locally and on free tiers.

**Required deliverables (each with acceptance criteria verifiable by command or inspection):**
1. Repository layout with three components, `pyproject.toml` files, lockfiles, `Makefile`/`justfile` giving local parity with CI (`lint`, `test`, `build`, `scan`, `package`, `release-dry-run`).
2. GitHub Actions pipeline: PR pipeline (lint, type check, unit tests, data-contract checks, ML metric gate on a small seeded dataset) and main pipeline (build, integration test, package, publish, promote) — least-privilege `permissions`, SHA-pinned actions, `concurrency`, timeouts.
3. A reusable workflow plus a composite action consumed by ≥ 2 components.
4. Path-based triggering with a **required aggregate gate job** that always reports.
5. Caching strategy with a measured cold/warm benchmark and a pipeline-speed SLO.
6. Flaky-test detection job and quarantine mechanism with owner/expiry metadata.
7. Artifact publishing: wheel to a local index; container image (M01 pipeline reused) pushed to a local registry; checksums, SBOM, and digest recorded in a `release-manifest.json`.
8. Automated semantic versioning, changelog, tag, and GitHub Release (dry-run capable; real release only in the learner's private repo).
9. Environment promotion dev → staging → prod by **digest**, with approvals via environments/protected rules; prod simulated locally; bypass attempt blocked and documented.
10. A GitLab CI equivalent of the PR pipeline (`.gitlab-ci.yml`) validated by lint or local runner, with a mapping table to the Actions version.
11. An ephemeral self-hosted runner setup (local container) with a security checklist; documented rule that untrusted PRs never run on it.
12. Delivery metrics: a script that computes the four DORA metrics + pipeline SLIs from run history, producing a report with caveats.
13. Documentation: architecture diagram, ≥ 4 ADRs, runbooks for 4 incidents (secret leaked in logs, broken release partially published, flaky-test epidemic, runner compromised), and a production-readiness review using the Unit 1–11 checklists.
14. A before/after results table (pipeline duration p50/p95, queue time, flake rate, cache hit rate, change failure rate proxy, lead time) filled from the learner's **own** measurements. Provide the template; never fabricate results.

**Include:** 6–7 milestones with time estimates; a 100-point rubric (Poor/Adequate/Strong/Exemplary descriptors); stretch goals; common failure points; self-review checklist; exact evidence folder structure.

**Provide complete, runnable starter code**: the three small components with tests, all workflow/CI files, scripts, Makefile, release configuration, metric script. No `TODO: implement` in required deliverables. Keep every secret fake (`example-token-do-not-use`) and every real-publishing step gated behind an explicit variable defaulting to dry-run.

# 9. README ORIENTATION (Unit 0)

Include: purpose and audience; Gate In prerequisites mapped to Stage 2E (including M01 outcomes consumed here); module dependency graph and why order matters; 4-week and 8-week pacing plans; tool matrix (Core vs Awareness) with install-verification commands; lab setup checklist (GitHub private test repo, tokens with minimal scope, `gh` auth, optional `act`, local registry from M01, free-tier safety notes with cost-safety link); glossary; module-to-exit-criteria mapping; evidence storage rules; how to use practice questions and the project; table linking M02 to M01, M03, M06, M08, M09, M10, M11, M12, M15, M16, M17.

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block names its language and, where relevant, a file-path first-line comment (e.g., `# File: .github/workflows/pr.yml`).
2. Every command is paired with **representative expected output**, labelled "example — yours will differ", plus a short interpretation.
3. **Only real syntax.** Use keys, flags, and API fields you are confident exist. Anything that differs across versions, plans, or UI revisions is tagged `[VERIFY: what/where]` or `[VERSION-SENSITIVE]`. Never guess. This is especially important for GitHub Actions/GitLab keywords, ruleset/branch-protection field names, `gh api` endpoints, cache limits, and free-tier quotas.
4. **Pin third-party actions by full commit SHA** in all examples (use a clearly marked placeholder such as `<full-40-char-sha> # vX.Y.Z — look up and verify` rather than inventing a SHA). First-party `actions/*` may be shown by tag only with a comment explaining that SHA pinning is the stricter policy.
5. **Least privilege everywhere:** every workflow example declares top-level `permissions:` (default read-only) and elevates per job only as needed.
6. **No real secrets.** Fake values only; demonstrate secrets via the platform secret store, never echoed. Show masking behavior and its limits.
7. **Deliberately vulnerable examples** (script injection, `pull_request_target` misuse, persistent-runner leakage) are allowed **only** as defensive teaching on the learner's own private test repository, labelled `# VULNERABLE — DO NOT COPY` with the defect list and the fixed version beside it. No weaponized payloads, no real credential exfiltration techniques, no targeting of third-party systems.
8. **Destructive/outward-facing commands** (publishing a package, creating a release, pushing tags, deleting packages/branches, changing branch protection) are labelled `⚠ OUTWARD-FACING` or `⚠ DESTRUCTIVE`, with a dry-run or local-throwaway-repo alternative first. Real publishing steps are limited to the learner's own private test repository and TestPyPI/local index.
9. Scripts: `set -euo pipefail`, quoted variables, explicit exit codes, `--dry-run` where mutating, idempotent where possible. Python: typed where practical, minimal dependencies, with tests.
10. **Every lab ends with cleanup** (delete test releases/tags/packages, revoke tokens, remove runners, remove local containers/registries) and verification.
11. **Every performance/cost claim** is tied to a measurement command or labelled "typical range — measure yours". Never state minutes, quotas, prices, or speedups as fact without a `[VERIFY]`.
12. Call out WSL2 vs native Linux differences (Docker integration, filesystem performance, `act` behavior) where they affect a lab.
13. Pipeline files must be valid for the platform's current syntax; mentally run `actionlint`-style validation on every workflow and CI-lint on every GitLab file before output.

# 11. PEDAGOGY RULES

- **Mechanism before recipe.**
- **One running example** (FastAPI service + shared lib + ETL package) that evolves across all units: naive → structured → fast → safe → automated → promoted → measured.
- **Show failure on purpose:** every unit includes at least one lab where the learner breaks something and diagnoses it from logs.
- **Diagrams** for pipeline DAGs, promotion flows, trust boundaries, cache scoping, release state machines, and runner isolation.
- Plain, precise English; no filler or marketing; define acronyms at first use; consistent terms (*pipeline, workflow, job, step, runner, artifact, digest, environment, promotion, gate*).
- Be honest about trade-offs; avoid "always/never" without reasons and exceptions.
- Be vendor-fair: explain the concept first, then the GitHub and GitLab expressions of it.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You act as author first, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base technical claims on **official documentation and specifications**: GitHub Actions docs, GitLab CI/CD docs, Semantic Versioning 2.0.0 spec, Conventional Commits spec, Keep a Changelog, PyPA packaging docs (`pyproject.toml`, build, Trusted Publishing), pytest and Ruff docs, DORA published research/definitions, OWASP Top 10 CI/CD Security Risks, SLSA spec, NIST SSDF (SP 800-218) as Awareness, OpenSSF Scorecard guidance as Awareness. Cite by **document name and section/title**, not invented URLs; give a URL only if certain it is canonical, else mark `[VERIFY]`.
- **Do not fabricate:** versions, SHAs, release dates, quotas, prices, statistics, benchmark results, quotes, CVE IDs, API fields, or tool behaviors. Derive numbers from stated commands or label `[ILLUSTRATIVE]`.
- Mark uncertainty with `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, or `[ASSUMPTION]`.
- Keep a running **Claim Register** for every non-trivial factual claim.

## 12.2 Mandatory multi-pass self-audit (before delivering each part)

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 15 units, all Section 5 sections, all Section 6 topics, L1–L4. | Any gap. |
| 2 | **Technical accuracy** | Every YAML key, keyword, flag, expression, and API path is real and correctly used; mentally run each pipeline. | Invented or misused syntax. |
| 3 | **Executability** | YAML/code is syntactically valid; cross-references resolve; each lab has steps, expected evidence, cleanup; workflows would pass `actionlint`, GitLab files would pass CI lint, scripts would pass ShellCheck in principle. | Broken or ambiguous step. |
| 4 | **Currency** | Version- or UI-sensitive items are tagged; no deprecated practice taught as current (e.g., `set-output`, `save-state`, unpinned actions as best practice, legacy `only/except` as current, `--extra-index-url` as a safe default). | Stale or untagged claim. |
| 5 | **Security correctness** | No insecure practice shown as good; no overclaiming (SHA pinning ≠ safe action; OIDC ≠ authorization; "protected branch" ≠ unbypassable for admins; "scan passed" ≠ secure; masking ≠ secrecy). | Overclaim or unlabeled insecure example. |
| 6 | **Fabrication scan** | Hunt for invented stats, SHAs, versions, quotas, citations, DORA numbers, outputs presented as measured. | Any unsupported specific. |
| 7 | **Pedagogical consistency** | Real beginner→advanced ramp; no concept used before introduced; consistent terms; running example evolves coherently. | Forward dependency without note; drift. |
| 8 | **Cross-consistency** | Questions test only taught content; capstone deliverables map to units; checklists match lessons; README matches content; GitHub and GitLab mapping tables agree with the units. | Orphan question/deliverable; contradiction. |
| 9 | **Adversarial review** | As a skeptical staff engineer: list the 10 most likely objections ("what would break or mislead in a real org?") and resolve each. | Unresolved objection. |
| 10 | **Lab safety & feasibility** | Labs run on free tiers within the local baseline, are idempotent, touch only the learner's own private repo, never publish to real public indexes beyond TestPyPI-style sandboxes, and clean up. | Hidden cost, public side-effect, leftover state, or unsafe step. |

## 12.3 Audit artifacts inside the syllabus (final appendices)

**Appendix A — Claim Register:** `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag`. ≥ **70 entries**, covering every version-sensitive, quota-related, or security-relevant claim.

**Appendix B — Audit Report:** `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk`, for passes 1–10. Be candid; report real defects.

**Appendix C — Human Verification Checklist:** every `[VERIFY]` / `[VERSION-SENSITIVE]` item grouped by platform/tool (GitHub Actions, GitHub repo settings/rulesets, GitLab CI, PyPI/TestPyPI/packaging, pytest/Ruff plugins, release tools, DORA, `gh` CLI), each with *what to check*, *where (official doc name)*, *how to test with one command or UI path*. Closable by a reviewer in under 4 hours.

**Appendix D — Known Limitations and Assumptions:** what is intentionally out of scope (e.g., Jenkins depth, full MLOps, GitOps reconciliation), assumed tool versions, free-tier caveats, anything unverified.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace a human running the labs.

## 12.4 Trust rules
- If a pass finds a defect you cannot confidently fix, leave it visible as `OPEN` in Appendix B and list it in Appendix C. Never hide uncertainty.
- Never claim a command or workflow "was run/tested" unless it was actually executed. Use "expected output (representative)".
- Never claim verification against live documentation unless you consulted it; otherwise say "written from knowledge of the documentation; verify against current docs".

# 13. OUTPUT FORMAT

- **One Markdown document:** `SYLLABUS-ci-cd-architecture-and-pipeline-design-principles.md`.
- Begin with: title, abstract paragraph, metadata block (`Module: M02`, `Stage: 2E`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 0–13 in order, then Appendices A–E.
- Headings: `#` title, `##` units, `###`/`####` below; tables for comparisons; fenced code for all code; mermaid for diagrams.
- Units cross-linked with relative links to sibling target files.
- **Depth target:** Units 1–11 each ≥ 2,500 words of teaching text excluding code; ≥ 150 practice questions; capstone with complete code. **Do not compress to fit**—use the Delivery Protocol.
- No placeholder text, no "etc." in required lists, no "exercise left to the reader" for required deliverables.

# 14. DELIVERY PROTOCOL

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0, Unit 1 |
| 2 | Units 2, 3 |
| 3 | Units 4, 5 |
| 4 | Units 6, 7 |
| 5 | Units 8, 9 |
| 6 | Units 10, 11 |
| 7 | Unit 12 (practice questions) |
| 8 | Unit 13 (capstone, full code) |
| 9 | Appendices A–E, including the cross-part audit |

Rules:
- End each part with: `PART n/9 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–10, scoped) **before** printing each part; maintain the Claim Register throughout.
- Part 9 runs the cross-part audit (passes 7, 8, 9 especially) and lists every correction to earlier parts as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If nearing the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 9 print: "Concatenate Parts 1–9 in order into `SYLLABUS-ci-cd-architecture-and-pipeline-design-principles.md` and apply all listed corrections."

# 15. DEFINITION OF DONE

- [ ] All 15 units present in order; Units 1–11 each have L1–L4 and sections N.0–N.14.
- [ ] Every Section 6 topic taught at its stated level; GitHub Actions is the primary Core platform and GitLab is taught at working depth with a mapping table.
- [ ] ≥ 150 practice questions with model answers and distractor analysis.
- [ ] Capstone has complete runnable code, acceptance criteria, rubric, and a blank measurement template.
- [ ] Every lab has steps, expected evidence, cleanup; all run free and locally/privately; no public side effects.
- [ ] No fabricated SHAs, versions, quotas, numbers, or citations; every uncertainty tagged.
- [ ] Appendices A–E present; Claim Register ≥ 70; passes 1–10 reported candidly.
- [ ] Running example evolves coherently across all units.
- [ ] Forward references (M01, M03, M06, M08–M12, M15–M17) explicit and not half-taught.
- [ ] A human can close every open item in under 4 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/9**. Do not ask clarifying questions; record an `[ASSUMPTION]` where information is missing and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. Use one long conversation across all 9 parts so the Claim Register and running example stay consistent.
2. AI self-audit is not independent. Run the labs and close every `[VERIFY]` item against current official docs.
3. Highest fabrication risk, check first: GitHub ruleset/branch-protection field names, `gh api` endpoints, cache size/eviction limits, free-tier quotas, GitLab `spec:inputs`/CI components and `id_tokens` syntax, PyPI Trusted Publishing steps, third-party action SHAs, DORA metric wording.
4. Use only a private test repository for the labs. Revoke tokens and delete test releases/packages afterwards.
5. The stage tooling map marks GitLab CI as Awareness. This prompt teaches it at working depth because the folder has a dedicated unit, so you may want to update the tooling map to match.
