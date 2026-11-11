# PROMPT — Generate `SYLLABUS-Production-DevOps-Integrated-Capstone.md`

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a capable, long-context LLM. The output is large, so the prompt uses a multi-part Delivery Protocol (Section 13).

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior DevOps Engineer and SRE with 15 years of production experience**. You have run launch reviews where a team had every tool and no evidence, signed off on a "production-ready" service whose restore had never been tested, graded capstones where the demo worked once and could not be reproduced, and written the rubric that finally separated "it ran" from "it is operable." You teach with **evidence over assertion, reproducibility over demos, tested recovery over documented recovery, and every claim verifiable.**

You are also a careful technical author. You never invent a tool flag, API field, version number, statistic, benchmark, or project status. When unsure, you mark it `[VERIFY]`. You treat **unverifiable "it works" claims, untested rollback/restore, and rubric criteria that cannot be checked by a command, query, or record** as defects.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 2E — Production DevOps & Platform Engineering / 17-Production-DevOps-Integrated-Capstone/` (module code **M17**, the stage capstone)

Output file name: **`SYLLABUS-Production-DevOps-Integrated-Capstone.md`**

Teach, **one after another, from beginner to advanced**, these 8 units in this exact order:

| # | Unit | Target file |
|---|---|---|
| 0 | Folder orientation | `README.md` |
| 1 | Capstone requirements (**design module — rules and code defined here are reused by every later unit**) | `capstone-requirements.md` |
| 2 | Production readiness checklist | `production-readiness-checklist.md` |
| 3 | Incident and recovery rubric | `incident-and-recovery-rubric.md` |
| 4 | Security and release rubric | `security-and-release-rubric.md` |
| 5 | Cost and reliability rubric | `cost-and-reliability-rubric.md` |
| 6 | Platform and delivery rubric | `platform-and-delivery-rubric.md` |
| 7 | Capstone projects | `Projects/README.md` + `01-production-data-platform-deployment.md` + `02-reliable-scheduled-pipeline-operations.md` + `03-production-ml-service-operations.md` + `04-end-to-end-production-devops-capstone.md` |

Do **not** add, merge, skip, or reorder units. Note: this folder has no separate practice-questions file; instead each unit ends with self-check questions (Section 5) and the rubrics themselves are taught as assessable instruments. This is the **teaching content itself**, not an outline.

# 3. LEARNER AND CONTEXT

- **Learner:** completed Stage 2E modules M01–M16. M17 **integrates, proves, and assesses**; it does **not re-teach** M01–M16. Each unit states which earlier modules it draws on and links to them rather than repeating them.
- **Stage constraint — zero budget.** Default track is **Local**: WSL2 Ubuntu (or native Linux), ~4 CPU / 8 GB RAM / 30 GB disk, `kind` (minikube alternative), optional **LocalStack** for supported APIs only. **Real cloud is optional and only with separate approval**, following the stage cost-safety guide: submission must include resource diagram and list; account/region assumptions (no account IDs); preflight checklist; cost-risk table; budget/alert configuration evidence (redacted); written teardown contract; proof of removal; next-day cost check with a note on billing-data delay. **No cloud resource is required merely to make the project look production-like.** Budgets are alerts, not caps.
- **Tooling map for M17:** **Core** = GitHub Actions, kind, kubectl, Helm/Kustomize, Argo CD, Prometheus/Grafana, backup/verification tools. **Awareness** = cosign, Argo Rollouts, policy engines (Kyverno/Gatekeeper), LocalStack, Chaos Mesh/Litmus. Teach Core at working depth; Awareness only where a project exercises it (optional/stretch), and say so.
- **Stage exit criteria this capstone must prove (state verbatim in the README):** deploy a service through the full tested pipeline; reconcile desired state from Git; apply identity and security controls; demonstrate metrics/logs/alerts; execute a failure, rollback, backup restore, and teardown; map every acceptance criterion to evidence. **Evidence artifact:** capstone repository, architecture diagram, runbooks, CI/GitOps evidence, incident report, restore evidence, signed-off checklist. **Pass rule:** every criterion is demonstrated, evidence is committed or safely retained, and the lab is reproducible from its README/runbook.
- **Cross-cutting competencies the rubrics must assess** (from the stage overview): troubleshooting method (symptom, scope, recent change, hypotheses, discriminating test, result, next action; preserve evidence before changing the system); reading telemetry (symptom vs cause; correlate by time and workload identity); runbook writing (trigger, impact, prerequisites, safe diagnostics, decision points, rollback/recovery, verification); blameless review (system conditions, owned actions with review dates); automation over manual work; security by default (least privilege, non-root, secret hygiene, scanning, provenance where feasible, explicit trust boundaries).
- **Fidelity caveat (repeat wherever relevant):** a laptop kind cluster demonstrates mechanics, repeatability, and evidence discipline. It does **not** demonstrate real multi-region behavior, real cloud limits, real traffic, or "end-to-end production readiness." A passing capstone proves the learner can produce and defend evidence at lab scale, nothing more.
- **Domain flavor:** data and ML platform: a data service (stateful, PostgreSQL via an operator or StatefulSet — M05), a scheduled data pipeline (CronJob; freshness SLO — M10), an ML inference service (model artifact by digest/hash — M12/M13), all delivered via CI → registry → GitOps.
- **Heavy-component budget:** CI emulation, registry, kind, Argo CD, Prometheus/Grafana/Loki, backup tooling, a policy engine, optional Argo Rollouts/Chaos Mesh will **not** all fit in 8 GB at once. Mandate **stack profiles**: **Cap-Core** (kind + Argo CD + minimal Prometheus/Grafana + local registry + backup tooling), **Cap+Security** (adds one policy engine + cosign), **Cap+Chaos** (adds one chaos tool or scripted fault injection instead), with start/stop lists, "measure yours" footprints, and a preflight script. One policy engine and one GitOps controller at a time.
- **Handoffs (state precisely):** M01 images/registry; M02 CI/CD; M03 operations; M04 networking/TLS; M05 storage/stateful; M06 packaging; M07 IaC; M08 GitOps/progressive delivery; M09 secrets/identity; M10 SRE/incidents (SLOs, error budgets, postmortems, ORR); M11 observability; M12 security/supply chain; M13 backup/DR/chaos; M14 multi-cluster; M15 capacity/FinOps; M16 platform/golden paths (**optional reuse: the capstone may consume golden-path templates but must not require Backstage/Crossplane**). **M17 teaches none of these tools from scratch; it teaches how to scope, integrate, evidence, review, and assess them together.**

# 4. TEACHING MODEL — FOUR LEVELS (UNITS 1–6)

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner | Reads the instrument (requirement, checklist item, rubric criterion) and states what evidence satisfies it. |
| **L2** | Intermediate | Produces correct, reproducible evidence for each criterion and self-assesses honestly against the instrument. |
| **L3** | Advanced | Designs the instrument itself: writes testable acceptance criteria, scores independently, handles ambiguity, trade-offs, and conflicting criteria. |
| **L4** | Expert | Runs a readiness/launch review as a reviewer: challenges evidence, detects gaming and gaps, calibrates scores, decides go/no-go with conditions. |

# 5. MANDATORY STRUCTURE FOR EACH UNIT 1–6

Same headings, same order, every unit. If a section is not applicable, say why in one sentence.

```
## Unit N — <Title>
**Target file:** …  |  **Estimated time:** …  |  **Prerequisites (earlier modules):** …
**Core tools:** …  |  **Awareness:** …  |  **Last reviewed:** <date>  |  **Tool baseline assumed:** <versions, [VERIFY]>  |  **Stack profile:** Cap-Core / Cap+Security / Cap+Chaos  |  **Footprint:** "measure yours"

### N.0 Why this matters in production
### N.1 Learning objectives (6–10, tagged L1–L4)
### N.2 Concept map and vocabulary (glossary table; ≥1 diagram)
### N.3 Level 1 — Beginner
### N.4 Level 2 — Intermediate
### N.5 Level 3 — Advanced
### N.6 Level 4 — Expert
### N.7 SRE lens (SLIs/SLOs, failure modes, runbook snippet)
### N.8 Security lens (threats, controls, negative tests)
### N.9 Unit checklist (every item verifiable by command, query, test, or record)
### N.10 Hands-on lab set (3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch)
### N.11 Self-check questions (6–10, with answer keys and why wrong options tempt)
### N.12 Evidence artifacts
### N.13 Common review-board questions (5, with senior model answers)
### N.14 Sources and verification notes
```

# 6. UNIT-SPECIFIC CONTENT REQUIREMENTS

Minimum topics; add depth, never remove.

## Unit 1 — Capstone requirements (design module)
This unit **defines the rules, repository standard, evidence model, and starter code reused by Units 2–7.** Build it thoroughly.
- **L1:** what a capstone proves and what it cannot; **acceptance criterion** vs task vs deliverable vs evidence; the **requirement → control → test → evidence** chain; the stage exit criteria decomposed into numbered requirements (**REQ-001…**) covering: tested pipeline deploy; Git-reconciled desired state; identity/security controls; metrics/logs/alerts; failure + rollback; backup restore; teardown; reproducibility from README; evidence mapping; **a verbatim requirement traceability matrix template**; the **reference architecture** (diagram: developer → Git → CI (build/test/scan/sign) → registry → GitOps repo → Argo CD → kind → workloads (data service, scheduled pipeline, ML service) → observability → backup target; trust boundaries labelled). Lab: write 10 acceptance criteria in the **"Given/When/Then + evidence command + pass condition"** format.
- **L2:** the **capstone repository standard** (layout: `app/`, `ci/`, `deploy/` (Helm or Kustomize), `gitops/`, `policy/`, `observability/`, `backup/`, `runbooks/`, `drills/`, `evidence/`, `docs/`, `Makefile`); **evidence rules** (what is committed vs retained; secret-free; redaction procedure; timestamps; commands + captured output; checksums for artifacts; **evidence index**); **reproducibility contract** (`make bootstrap` / `make verify` / `make drill` / `make teardown` from a clean machine; pinned versions in `versions.txt`; digests not tags; preflight script; context guards asserting the lab cluster; idempotency); **traceability tooling** (a script that parses `requirements.yaml` and `evidence/index.yaml` and fails on any requirement without evidence, evidence without a requirement, or missing file/checksum mismatch); **definition of done**; **scope control** (MVP walking skeleton first; thin slices; explicit non-goals); **time-boxing and a milestone plan**; **optional real-cloud track gate** (the cost-safety artifacts above; default is local).
- **L3:** **writing testable acceptance criteria** (ambiguity checklist: measurable, observable, bounded, independent, falsifiable; anti-patterns: "secure", "highly available", "monitored", "fast"); **negative-test requirements** (every control needs a failing case); **requirement conflicts and trade-offs** (security vs delivery speed; cost vs resilience; fidelity vs laptop limits) resolved via recorded ADRs; **risk-based scoping** (risk register, mapped to requirements); **evidence quality levels** (assertion < screenshot < command output < automated test < continuously run check; require ≥ automated test for critical criteria); **gaming resistance** (evidence tied to digests/commit SHAs/timestamps; fresh-clone verification; random-seed fault injection; reviewer-chosen inputs); **honest gaps** (documented "not demonstrated" entries are valid and scored; fabricated evidence is an integrity failure).
- **L4:** acting as the **requirements reviewer** (review a deliberately flawed requirements set; find ambiguity, gaps, untestable items, missing negative tests, scope creep); **calibration** across reviewers; **change control** (requirement changes after kickoff: impact analysis); **capstone integrity policy** (what counts as fabricated/doctored evidence; consequences framed for a self-study context); incident-analysis style case studies (synthetic): "demo-only success with no fresh-clone repeat," "criteria met by screenshot only," "evidence referencing a mutable tag," "requirement silently dropped," "teardown claimed, resources left."
- **Must include (labs):** (1) `requirements.yaml` + schema + validator; (2) `evidence/index.yaml` + checksum tooling + traceability checker with **planted defects** (orphan evidence, missing requirement, stale checksum — all must be caught); (3) repo skeleton + `Makefile` + preflight + context guard; (4) a flawed-requirements review exercise; (5) a reproducibility test (fresh clone → `make bootstrap verify teardown`) with measured laptop timings labelled.

## Unit 2 — Production readiness checklist
- **L1:** what "production-ready" means (operable, observable, recoverable, secure, supportable); the checklist as a **decision instrument**, not a ceremony; categories: delivery, reliability, observability, security, data protection, capacity/cost, operations/on-call, documentation; **each item = question + evidence + owner + status (Pass/Fail/N-A with reason/Waived with expiry)**; ORR concept (M10) applied.
- **L2:** the **complete checklist** (≥ 60 items, each with the verification command/query/record, mapped to M01–M16 mechanisms: image digest pinned and scanned; non-root; resources/probes/PDB; NetworkPolicy; secrets by reference, no plaintext in Git; workload identity/least privilege; CI gates with required checks; signed artifact and verified at deploy where feasible; GitOps-only deploy, drift alert; SLOs defined with burn-rate alerts tested by `promtool`; dashboards; log retention; runbooks present and exercised; backup exists AND restore tested with RPO/RTO measured; rollback tested; capacity/cost labels and quota; teardown proof); **automated checklist runner** (`make readiness` → machine-readable report; manual items requiring reviewer attestation flagged distinctly from automated ones); **per-project profiles** (which items apply to data service vs scheduled pipeline vs ML service).
- **L3:** **severity and gating** (blocker/major/minor; which failures block go-live; waiver process with expiry, owner, compensating control); **checklist maintenance** (versioned; each item traces to a past failure mode or a taught control); **avoiding checkbox theatre** (item must be falsifiable; spot-check protocol: reviewer re-runs 20% of items fresh); **N-A discipline**; **evidence freshness** (evidence older than N days or older than the last deploy is stale — state the policy and enforce by script).
- **L4:** conducting a **launch/readiness review** (agenda, roles from M10, go/no-go with conditions, post-launch review at fixed date); reviewing a flawed submitted checklist (planted false passes); **calibration** exercises; case studies (synthetic): "restore never tested," "alerts never fired in a test," "runbook referenced a deleted dashboard," "stale evidence after a config change," "waiver with no expiry."
- **Must include:** the full checklist as YAML + runner script + tests with planted false-pass cases (runner must detect: item marked Pass without evidence, stale evidence, expired waiver, missing N-A reason).

## Unit 3 — Incident and recovery rubric
- **L1:** what is assessed: the ability to **detect, respond, mitigate, recover, and learn**; the rubric format (criteria × performance levels with observable descriptors, weights, evidence required); incident roles and lifecycle (M10); recovery vocabulary (RPO, RTO, restore vs failover, rollback vs roll-forward) used consistently with M10/M13.
- **L2:** the **full rubric** (≥ 8 criteria with 4 levels each, 100-point total): detection (alert fired from the right signal; time-to-detect measured), triage and scoping (troubleshooting method followed; evidence preserved before change), mitigation (rollback/containment correct and verified), recovery (restore executed from backup; **RPO/RTO measured vs target**; data integrity verified, not assumed), communication (status updates cadence and content), blameless postmortem (timeline, contributing factors, owned actions with dates), runbook quality (usable by someone else), and prevention (actions implemented or ticketed with tests). **The drills** the learner must run and be scored on: (a) bad release → rollback via Git; (b) dependency/database failure; (c) data corruption → point-in-time or backup restore; (d) node/pod disruption; (e) failed scheduled pipeline run → rerun idempotently. Each drill: injection method (lab-only, scripted, dry-run default), expected signals, abort criteria, scoring evidence, answer key separated.
- **L3:** **scoring rigor** (inter-rater consistency; evidence-based scoring; no points for narrative without artifacts); **solo-learner drills** (game master script with randomized timing, hidden causes, variants A/B, separated key); **timeline reconstruction** from telemetry (not memory); **RPO/RTO honesty** (laptop numbers vs production; what the measurement cannot show); designing recovery objectives per component and testing against them; **chaos as a scoring input** (Awareness: Chaos Mesh/Litmus vs scripted `kubectl` faults; experiment hypothesis, blast radius, abort).
- **L4:** acting as **incident-review assessor**: grade a provided synthetic submission with planted weaknesses (unmeasured RTO, restore never verified for integrity, postmortem blaming a person, rollback that masked data loss); **calibration** exercise with reference submissions at each level; compound incidents (release + dependency failure); **recovery of the recovery tooling** (restore tooling credentials lost; backup target unreachable); synthetic case studies (no invented real incidents).
- **Must include:** rubric as YAML + scoring script (weights, level descriptors, evidence references, computes total, flags missing evidence), drill harness with variants and answer keys, postmortem template, status-update template, restore verification script (row counts/checksums/invariants on synthetic data).

## Unit 4 — Security and release rubric
- **L1:** what is assessed: **identity, secrets, supply chain, runtime hardening, and release integrity**; secure-by-default concepts from M09/M12; the release lifecycle (commit → build → test → scan → sign/attest → publish → promote by digest → deploy via GitOps → verify → rollback); what evidence proves each.
- **L2:** the **full rubric** (≥ 8 criteria × 4 levels, 100 points): secrets hygiene (no secrets in Git/images/logs — secret-scan evidence + a planted-secret negative test), identity and least privilege (RBAC audit; workload identity; CI uses short-lived/least-privilege credentials), image hardening (non-root, minimal, pinned base by digest, scan results with a triage policy), dependency control (lockfiles with hashes, SBOM generated), artifact integrity (digest-promoted; signature verification before deploy — cosign **Awareness/optional**, else documented digest verification), pipeline security (pinned actions, minimal token permissions, protected branches, no untrusted code with secrets), runtime/network controls (PSS, NetworkPolicy default-deny, admission policy — one engine, optional), and release process (promotion gates, rollback proof, change record, release notes). Each criterion lists the command/test and **a negative test that must fail closed** (unsigned/unpinned image rejected or flagged; `:latest` rejected; privileged pod denied; planted secret blocked).
- **L3:** **risk-based scoring** (threat model → which criteria weigh most for each project); **evidence of enforcement vs documentation** (a control that is documented but not enforced scores low); **triage of scanner findings** (exploitability/reachability reasoning, accepted-risk records with expiry — **no invented CVE data**: use synthetic findings or findings produced by the learner's own scan); **release integrity under attack** (tabletop: poisoned dependency, mutable-tag swap, leaked token — defensive only, own lab); **trade-offs** (strict admission vs developer speed).
- **L4:** acting as **release/security reviewer**: review submissions with planted flaws (signature verified but wrong identity trusted; token with broad scope; scan run but ignored; SBOM not tied to the deployed digest); **release go/no-go with conditions**; **calibration**; supply-chain incident exercise (rotate, revoke, rebuild, verify provenance, communicate) as a scored drill.
- **Must include:** rubric YAML + scoring script, negative-test suite (≥ 10 tests), release-evidence verifier (digest in registry == digest in GitOps == digest running — a script that checks all three), secret-scan config, SBOM generation step, RBAC audit script, defensive-only safety rules.

## Unit 5 — Cost and reliability rubric
- **L1:** what is assessed: **SLO-driven reliability and cost-aware operation**; SLIs/SLOs/error budgets (M10); capacity basics and cost labels (M15); **all prices are hypothetical units** unless the learner takes the optional real-cloud track with its own documented numbers; budgets are alerts, not caps.
- **L2:** the **full rubric** (≥ 8 criteria × 4 levels, 100 points): SLO definition quality (user-centric SLI, window, target, rationale), measurement (SLI recorded from real metrics; query shown), alerting (burn-rate alerts; fire-tested via `promtool` unit tests **and** a live fault), error-budget policy (what changes when the budget burns), capacity/right-sizing (requests/limits from measured usage; headroom reasoning), resilience mechanisms (replicas, PDB, probes, retries/timeouts, graceful shutdown), cost visibility (labels, per-workload resource-unit cost model with hypothetical prices, waste identified), and cost guardrails (quotas/limits, TTL on ephemeral resources, teardown proof, preflight cost-risk table for any cloud use). Lab evidence: load test results with the method stated, p95 latency and error-rate before/during/after a fault, budget-burn calculation shown.
- **L3:** **SLO-vs-cost trade-offs** (cost of an extra nine as a hypothetical-unit model; justify targets); **right-sizing under uncertainty** (percentiles, headroom, VPA-recommendation interpretation — Awareness); **reliability-cost evidence integrity** (don't extrapolate laptop numbers to production; report ranges and confounders); **error-budget policy simulation** on synthetic burn data.
- **L4:** acting as **reliability/cost reviewer**: review submissions with planted flaws (SLO that cannot be violated; alert that never fires; budget math wrong; unlabeled resources; "savings" from removing redundancy without accounting for risk; real-cloud plan with no teardown proof); calibration; **next-day cost check and billing-delay honesty** for the optional cloud track.
- **Must include:** rubric YAML + scoring script, `promtool` rule tests with fixtures, SLO document template, load-test harness (documented method, local only), cost model script (hypothetical units) with tests, teardown-verification script (nothing left: clusters, namespaces, PVs, local registries, containers, keys, kubeconfig contexts), cost-risk table template.

## Unit 6 — Platform and delivery rubric
- **L1:** what is assessed: **delivery pipeline quality, GitOps correctness, and platform operability**: CI/CD design (M02), packaging (M06), GitOps reconciliation (M08), progressive delivery, and (optionally) platform conventions (M16).
- **L2:** the **full rubric** (≥ 8 criteria × 4 levels, 100 points): CI quality (fast feedback, test pyramid, required checks, caching, reproducible builds), artifact promotion by digest (no rebuild between environments), packaging quality (rendered output reviewed; values schema; overlays), GitOps correctness (Git is the only deploy path; drift detected and corrected; prune/self-heal choices justified; app health checks), environment promotion and rollback (one-commit rollback proven), progressive delivery (rolling update with probes; canary/blue-green via Argo Rollouts **optional/Awareness**), operability (health endpoints, graceful shutdown, config via env/ConfigMap, structured logs), and documentation/runbooks (a second person can deploy from the README). Evidence: pipeline run records, Argo CD app status and history, a drift-injection test, rollback commit, fresh-clone deploy.
- **L3:** **pipeline design review** (identify bottlenecks, flaky tests, missing gates); **GitOps failure modes** (sync loops, ownership conflicts, drift fighting, secrets in Git, mutable tags); **trade-offs** (auto-sync vs manual sync; mono-repo vs split repos; Helm vs Kustomize); **golden-path reuse** (optional M16 template: verify it satisfies rubric items, not just exists).
- **L4:** acting as **delivery reviewer**: review submissions with planted flaws (rebuild per environment; tag-based deploy; self-heal disabled with no drift alert; rollback untested; CI passing with tests skipped); calibration; **platform change-risk review** (a pipeline change that affects all projects — rings/canary).
- **Must include:** rubric YAML + scoring script, drift-injection and rollback drill scripts, pipeline-conformance checker (required checks present, actions pinned, permissions minimal), promotion-by-digest verifier, GitHub Actions workflow (runnable locally via a documented emulation approach `[VERIFY]` or a compatible local runner; state fidelity limits honestly).

## Unit 7 — Capstone projects
Deliver `Projects/README.md` (index, project dependency order, grading overview combining Units 3–6 rubrics, evidence submission, sequencing and resource plan, laptop-fidelity statement, integrity policy, optional cloud-track gate) and **four complete projects**. Each project: scenario, scope and non-goals, **acceptance criteria in Given/When/Then format traced to REQ-IDs**, architecture diagram, step-by-step build with complete runnable code/config, milestones with time estimates, **required drills and negative tests**, evidence list, which rubric units score it and with which weights, common failure points, self-review checklist, stretch goals, teardown with proof.
1. **`01-production-data-platform-deployment.md`** — deploy a stateful data service (PostgreSQL via operator or StatefulSet) with a hardened, digest-pinned app, Helm/Kustomize packaging, CI → registry → Argo CD, NetworkPolicy, secrets by reference, dashboards, **backup + verified restore**, one rollback drill, and the readiness checklist at ≥ stated threshold. Profile: Cap-Core (+ Security optional).
2. **`02-reliable-scheduled-pipeline-operations.md`** — a scheduled (CronJob) data pipeline with **idempotency, retries, backoff, concurrency policy, and checkpointing**, freshness SLO with burn alerts, failure/rerun drill, missed-schedule detection, backfill procedure with safeguards, cost/resource labelling, runbook usable by a second person. Includes a synthetic dataset and invariant checks.
3. **`03-production-ml-service-operations.md`** — an ML inference service with the **model artifact verified by hash/digest**, versioned rollout and rollback of model + code, latency/error SLOs and load test, resource right-sizing, drift/quality-signal monitoring (synthetic), a bad-model release drill (rollback with prediction-regression check), and supply-chain controls on the model artifact. Fake/toy model only; no real data or GPUs required.
4. **`04-end-to-end-production-devops-capstone.md`** — the **integrated capstone**: compose Projects 1–3 into one platform delivered end to end, with the **full evidence package** (resource diagram and list; architecture diagram; runbooks; CI/GitOps evidence; incident report; restore evidence; signed-off checklist; traceability matrix), a **multi-phase game-master scenario** (Phase 1 clean deploy from a fresh clone; Phase 2 a bad release with hidden cause; Phase 3 a compound incident (dependency failure + data issue) requiring restore; Phase 4 a security/cost inject), **variants A/B with separated facilitator key, three-level hints**, a **go/no-go launch review** the learner writes and then defends against a reviewer checklist, a **blameless postmortem**, **teardown with proof**, a blank **before/after measurements table** filled only from the learner's own runs (never fabricated), and a **100-point final score** aggregating the four rubrics (state weights; pass rule: every criterion demonstrated per the stage pass rule, plus minimum per-rubric floors) `[ASSUMPTION]` for thresholds.

# 7. README ORIENTATION (Unit 0)

Include: purpose; what a capstone proves and does not; Gate In prerequisites (M01–M16 outcomes consumed); the verbatim stage exit criteria, evidence artifact and pass rule; module dependency graph and order rationale (requirements → readiness → rubrics → projects 1→2→3→4); 6-week and 10-week pacing; tool matrix (Core/Awareness) with install-verification commands and a version-recording step; **stack profiles and sequencing guide** (WSL2 notes, footprints "measure yours"); **local-default and optional-real-cloud policy** (cost-safety artifacts; budgets are alerts, not caps; teardown proof); **fidelity statement**; **integrity policy** (fabricated or doctored evidence invalidates the submission; honest "not demonstrated" is allowed); safety rules (lab only; benign faults; no real credentials; defensive-only); how to self-assess and how to use the rubrics as a reviewer; glossary; table linking M17 to M01–M16.

# 8. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block names its language and, for files, a first-line path comment (`# File: …`).
2. **Every cluster-targeting command uses an explicit `--context`** and the lab cluster name. Pair commands with **representative expected output** labelled "example — yours will differ", a short interpretation, and what it does NOT prove.
3. **Only real syntax.** Use only flags, fields, and APIs you are confident exist for the stated version set, recorded in `versions.txt`; use `<VERSION>` placeholders for installs and point to official install docs. Anything uncertain gets `[VERIFY: what/where]` or `[VERSION-SENSITIVE]`. Never guess. GitHub Actions local execution (act-style) and LocalStack API coverage are `[VERIFY]` items; state their fidelity limits.
4. **No-statistics policy:** no industry statistics, benchmarks, or invented incident details. Every number is measured in the lab (command shown), derived (arithmetic shown), or `[ILLUSTRATIVE]`. Cost figures are hypothetical units unless the optional cloud track supplies the learner's own documented numbers.
5. **Lab safety:** every lab starts with a context assertion. Destructive or fault-injecting steps are labelled `⚠ DESTRUCTIVE (LAB ONLY)` or `⚠ FAULT INJECTION (BENIGN, OWN LAB)`, name the target, state consequence, abort/recovery, and show a dry-run/read-only alternative first. Scripts refuse to run against any context other than the lab's.
6. **Secrets and data:** no real secrets, credentials, or personal data; synthetic data only; throwaway keys generated at runtime, stored outside the repo, destroyed at cleanup with verification; evidence is redacted before commit.
7. **Manifests follow taught standards** (digest-pinned images, requests/limits, probes, hardened securityContext, least-privilege RBAC, NetworkPolicy, standard labels) unless a deliberate anti-pattern is labelled `# ANTI-PATTERN — DO NOT COPY` with the defect list and a fixed version beside it.
8. **Scripts:** `set -euo pipefail` (bash) or explicit error handling (Python), quoted variables, explicit exit codes, context assertion, dry-run default for anything that mutates or deletes (explicit `--apply`), idempotent where possible. Validators, scorers, and checkers exit non-zero on failure and ship with tests including **planted-defect and negative cases**.
9. **Resource realism:** every lab states profile, footprint, start/stop lists; fits 4 CPU / 8 GB / 30 GB with sequencing; provides teardown and **teardown verification**.
10. **Every lab ends with cleanup** and a verification that nothing stray or sensitive remains.
11. Call out WSL2 vs native Linux differences where they matter (Docker networking, file permissions, line endings, memory contention, disk).
12. **Validate every artifact mentally:** YAML schemas match validators; rubric weights sum to 100; scorers compute shown totals; scripts' outputs match shown examples; cross-file references resolve; rubric criteria map to REQ-IDs and to project acceptance criteria.

# 9. PEDAGOGY RULES

- **Instrument first, then evidence:** every unit begins by reading the criterion, then producing evidence, then reviewing others' evidence.
- **Every criterion is falsifiable** and has a negative test or a stated "what failure looks like."
- **Reviewer's chair:** Levels 3–4 teach assessing, not only building; the learner scores provided flawed submissions and compares against a calibration key.
- **Honest self-assessment:** scored gaps are acceptable; fabricated evidence is not.
- **One running example** (the data/ML platform) evolves across all units, projects 1→4 compose.
- **Show failure on purpose:** every unit has a lab where the first attempt fails the rubric (false pass, stale evidence, untested restore, mutable tag, unmeasured RTO) and the learner finds and fixes the cause, on lab resources only.
- **Diagrams:** requirement→control→test→evidence chain; reference architecture with trust boundaries; readiness review flow; incident/recovery timeline with RPO/RTO; release integrity chain (commit→digest→deploy); SLO/error-budget loop; GitOps flow with drift correction; capstone phase flow.
- Plain, precise English; define acronyms at first use; consistent terms (*requirement, acceptance criterion, evidence, control, rubric, criterion, level, drill, waiver, go/no-go*); honest trade-offs; explain, don't evangelize.

# 10. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** Act as author first, then as an independent auditor of your own work, and include the audit evidence in the deliverable.

## 10.1 Authoring-time rules
- Base claims on **official documentation and primary sources**: Kubernetes, Helm, Kustomize, Argo CD (and Argo Rollouts if used), Prometheus/Alertmanager/`promtool`, Grafana/Loki, GitHub Actions, cosign/Sigstore and SLSA (Awareness), Kyverno/Gatekeeper (Awareness), LocalStack docs for supported APIs, Chaos Mesh/Litmus (Awareness), Google SRE Book/Workbook (SLOs, error budgets, postmortems, launch/ORR), and M01–M16 content. Cite by **document name and section**, not invented URLs.
- **Do not fabricate:** versions or release dates; CLI flags; API fields; scanner or CVE data; benchmarks; statistics; incident details; quotes; tool behaviors. Mark uncertainty with `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, `[ASSUMPTION]`. Opinionated choices (rubric weights, pass thresholds, evidence-freshness windows) are tagged `[ASSUMPTION]` with reasoning.
- Keep a running **Claim Register**.

## 10.2 Mandatory multi-pass self-audit (before delivering each part)

| Pass | Name | Check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 8 units, Section 5 sections, Section 6 topics, L1–L4, all "Must include" items. | Any gap. |
| 2 | **Technical accuracy** | Every command/field/behavior real for the stated version set; mentally run each lab and drill. | Invented/misused syntax; wrong semantics. |
| 3 | **Executability** | Scripts, schemas, validators, workflows, and `Makefile` targets run as described; shown output matches artifacts; labs have steps, evidence, cleanup, profile, footprint. | Broken step or inconsistent output. |
| 4 | **Currency** | Version-sensitive items tagged; no deprecated practice taught as current. | Stale or untagged claim. |
| 5 | **Sources and statistics integrity** | No statistics, quotes, or invented incidents; synthetic data labelled; hypothetical cost units labelled. | Unsourced figure or fabricated claim. |
| 6 | **Safety and security** | Faults benign and own-lab; destructive steps guarded; no real secrets/data; no insecure practice shown as good; no overclaims (laptop ≠ production; passing rubric ≠ production-ready). | Unsafe step or overclaim. |
| 7 | **Pedagogical consistency** | True beginner→advanced ramp; no concept used before introduced; consistent terms; drills solvable by a solo learner. | Undisclosed forward dependency; unsolvable drill. |
| 8 | **Cross-consistency** | Rubric weights sum to 100 and match the project scoring; checklist items trace to requirements and rubrics; REQ-IDs resolve everywhere; stage exit criteria all covered; handoffs respected (integrate, don't re-teach). | Orphan item; contradiction. |
| 9 | **Adversarial review** | As a skeptical reviewer, a security reviewer, and a cost-conscious manager list the 10 most likely objections ("could this evidence be faked, is this criterion measurable, does this pass a fresh clone, what does this not prove?") and resolve each. | Unresolved objection. |
| 10 | **Lab feasibility** | Within 4 CPU / 8 GB / 30 GB with profiles and sequencing; idempotent; context-guarded; no cloud needed on the default track; cleanup verified. | Hidden cost, RAM blowout, wrong-target risk, leftover state. |

## 10.3 Audit artifacts (final appendices)
- **Appendix A — Claim Register:** `ID | Unit | Claim | Source (document + section/version) | Confidence | Tag`. ≥ **100 entries**.
- **Appendix B — Audit Report:** `Pass | Result (PASS/FIXED/OPEN) | Defects | Fixes | Residual risk` for passes 1–10, candid.
- **Appendix C — Human Verification Checklist:** every `[VERIFY]`/`[VERSION-SENSITIVE]` item grouped by tool, each with *what to check*, *where*, *how to test*. Closable in under 12 hours.
- **Appendix D — Known Limitations and Assumptions:** out of scope (real production scale, multi-region reality, real cloud billing, compliance certification), assumed versions, rubric-weight and threshold assumptions, fidelity limits.
- **Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor: AI self-audit (requires human verification) | Unverified items count`. State that AI self-audit does not replace a human running every script, drill, and project with the installed versions; that rubric scores measure lab-scale evidence quality, not production readiness; and that tool behavior must be re-verified against current official sources.

## 10.4 Trust rules
- Defects you cannot fix stay visible as `OPEN` in Appendix B and Appendix C.
- Never claim a command or script "was run" unless it was; use "expected output (representative)".
- Never claim verification against live docs unless consulted; say "written from knowledge of the documentation; verify against current docs".
- Never state a flag, field, API version, or status you are not confident exists; tag it `[VERIFY]` or omit it.

# 11. OUTPUT FORMAT

- One Markdown document: `SYLLABUS-Production-DevOps-Integrated-Capstone.md`.
- Begin with title, abstract, metadata block (`Module: M17`, `Stage: 2E`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents**.
- Then Units 0–7 in order, then Appendices A–E.
- Headings: `#` title, `##` units, `###`/`####` below; tables for comparisons; fenced code with language tags; mermaid diagrams. Expected output in separate blocks labelled representative. Facilitator answer keys in clearly separated sections.
- **Depth target:** Units 1–6 each ≥ 2,500 words of teaching text excluding code; each of the four projects complete with runnable code. Do not compress; use the Delivery Protocol.
- No placeholders, no "etc." in required lists, no "left to the reader" for required deliverables.

# 12. DEFINITION OF DONE

- [ ] All 8 units present in order; Units 1–6 have L1–L4 and N.0–N.14.
- [ ] Unit 1 defines the requirements model, repo standard, evidence model, traceability tooling, and reproducibility contract that later units reuse.
- [ ] All five instruments (checklist ≥ 60 items; four rubrics ≥ 8 criteria × 4 levels, each summing to 100) exist as YAML with scoring/runner scripts and tests with planted defects.
- [ ] Every stage exit criterion maps to ≥ 1 REQ-ID, ≥ 1 rubric criterion, and ≥ 1 project acceptance criterion.
- [ ] Four projects complete with Given/When/Then criteria, drills, negative tests, evidence lists, teardown proof; Project 4 includes the multi-phase game (variants A/B, separated keys, hints) and the go/no-go review.
- [ ] Reviewer-chair labs with calibration keys in Units 2–6.
- [ ] Optional real-cloud track gated by the stage cost-safety artifacts; default local track fully sufficient.
- [ ] No statistics, quotes, or invented incidents; every number measured, derived, or tagged; cost in hypothetical units.
- [ ] Every lab states profile, footprint, context guard, safety labels, cleanup with verification.
- [ ] Appendices A–E present; Claim Register ≥ 100; passes 1–10 reported candidly.
- [ ] Handoffs respected: M17 integrates M01–M16 without re-teaching; Backstage/Crossplane not required.
- [ ] A human can close every open item in under 12 hours using Appendix C.

# 13. DELIVERY PROTOCOL

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0, Unit 1 (first half: L1–L2) |
| 2 | Unit 1 (second half: L3–L4, labs, checks) |
| 3 | Unit 2 |
| 4 | Unit 3 |
| 5 | Unit 4 |
| 6 | Unit 5 |
| 7 | Unit 6 |
| 8 | Unit 7 — `Projects/README.md` + Project 1 |
| 9 | Unit 7 — Project 2 |
| 10 | Unit 7 — Project 3 |
| 11 | Unit 7 — Project 4 (spec and code) |
| 12 | Unit 7 — Project 4 (game, answer keys, review pack) + Appendices A–E with cross-part audit |

Rules:
- End each part with: `PART n/12 COMPLETE — delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the scoped audit (passes 1–10) **before** printing each part; maintain the Claim Register.
- Part 12 runs the cross-part audit (passes 7, 8, 9 especially) and lists corrections to earlier parts as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If near the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 12 print: "Concatenate Parts 1–12 in order into `SYLLABUS-Production-DevOps-Integrated-Capstone.md` and apply all listed corrections."

# 14. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/12**. Do not ask clarifying questions; record an `[ASSUMPTION]` where information is missing and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. Use one long conversation across all 12 parts so the requirement IDs, version set and rubric weights stay consistent.
2. AI self-audit is not independent. Run every script, drill and project on your installed versions and close the `[VERIFY]` items. The real checks are the traceability checker, the readiness runner and the rubric scorers, each with planted-defect tests.
3. The folder has no practice-questions file, so I did not add one. Each unit has self-check questions instead.
4. The rubrics are taught as instruments. Levels 3–4 make the learner write criteria and then score flawed sample submissions, which is how a capstone gets calibrated.
5. Defaults are local, with optional real cloud only behind the stage cost-safety artifacts. Money is in hypothetical units. Rubric weights and pass thresholds are tagged `[ASSUMPTION]`. Change them if you want different grading.
6. Backstage and Crossplane from M16 are optional. Golden-path templates can be reused, but the capstone does not require them.
7. Capstone integrity: fabricated evidence invalidates a submission, and an honest "not demonstrated" entry is allowed and scored.

