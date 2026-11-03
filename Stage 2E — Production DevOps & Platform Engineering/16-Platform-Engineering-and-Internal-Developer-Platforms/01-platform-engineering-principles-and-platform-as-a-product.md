# Platform Engineering Principles and Platform as a Product

**Purpose.** This lesson explains how to turn the engineering capabilities already built in M01–M15 into a coherent internal product for data and machine-learning (ML) teams. The emphasis is product and organizational design, not re-teaching Kubernetes, continuous integration, GitOps, infrastructure as code, security, or site reliability engineering (SRE) mechanisms.

**Module:** M16  
**Stage:** 2E — Production DevOps & Platform Engineering  
**Unit:** 1  
**Target file:** `01-platform-engineering-principles-and-platform-as-a-product.md`  
**Estimated time:** 10–14 hours core learning; 4–6 hours optional stretch exercises.  
**Prerequisites:** Stages 0–2D and M01–M15. In particular, understand the mechanisms for images, CI/CD, Kubernetes, packaging, IaC, GitOps, identity/secrets, SRE, observability, supply-chain security, backup/recovery, fleet operations, and capacity/cost governance.  
**Core tools:** Python standard library, local files, Markdown, shell, Git if available.  
**Awareness:** Backstage, Crossplane, Argo CD, Gitea, policy engines, commercial IDPs, Team Topologies, CNCF platform references.  
**Last reviewed:** 2026-11-03 (authoring date; not a claim that external documentation was checked).  
**Tool baseline assumed:** Python 3.10+ syntax in examples; verify the installed interpreter with `python3 --version`. No heavy platform tool is required.  
**Stack profile required:** Plat-Core.  
**Footprint:** Low-overhead local files and Python scripts; actual resource use varies—**measure yours**.  
**Synthetic users/data:** Yes. All personas, interview/ticket examples, scores, incidents, and organizational cases in this lesson are synthetic teaching material.

## Unit 1 — Platform engineering principles and platform as a product

### 1.0 Why this matters in production

A team can successfully deploy Kubernetes, GitOps, policy checks, observability, and cost controls yet still leave every product team to assemble those capabilities independently. The result is duplicated effort, inconsistent defaults, and unsafe shortcuts; alternatively, a central operations group can become a ticket queue through which every environment change must pass. A portal does not fix either problem if its catalog is stale, its workflows are unreliable, or developers cannot understand what happens behind the interface. This unit teaches you to design the shared capability as a product with identifiable users, measurable friction, ownership, support, and a sustainable roadmap.

### 1.1 Learning objectives

By the end of this unit, you can:

1. **[L1]** Explain the difference between platform engineering, an internal developer platform (IDP), and an internal developer portal.
2. **[L1]** Map a data/ML developer journey and record a reproducible manual time-and-step baseline.
3. **[L2]** Turn synthetic friction records into coded themes while explaining why the result is not real user research.
4. **[L2]** Write a platform vision, problem statements, a Now/Next/Later roadmap, and a complete first-slice product requirements document (PRD).
5. **[L3]** Classify platform capabilities as provided, integrated, or left to product teams and defend the boundary.
6. **[L3]** Design an abstraction that reduces incidental cognitive load while preserving inspectability and supported escape hatches.
7. **[L3]** Build a transparent, assumption-based cost/benefit model without presenting illustrative inputs as measured organizational outcomes.
8. **[L4]** Diagnose platform adoption, reliability, governance, privacy, and trust failures and propose evidence-based corrective actions.

### 1.2 Concept map and vocabulary

#### Why platform engineering exists

Modern product teams may need to understand container images, cluster policies, CI permissions, deployment promotion, secrets, telemetry, backup tiers, quotas, and cost allocation before they can deliver a useful data product. Each mechanism can be justified individually. The combined cognitive load can still be excessive.

There are two common organizational extremes:

- **Unbounded team autonomy:** every team solves the same infrastructure and operational problems. Local ownership is high, but duplication and inconsistent security/reliability practices grow.
- **Centralized ticket fulfillment:** one operations team controls every change. Standards may be consistent, but queues, handoffs, and waiting time can prevent teams from acting independently.

Platform engineering seeks a better balance: provide reusable, supported capabilities and interfaces so teams retain responsibility for their products without repeatedly solving undifferentiated infrastructure problems.

#### Glossary

| Term | Precise working definition | Common misconception |
|---|---|---|
| Platform engineering | Designing and operating shared toolchains, workflows, and capabilities that help product teams deliver and operate software with less friction. | It is merely installing Kubernetes or buying a portal. |
| Internal developer platform (IDP) | The integrated product of platform engineering: capabilities, APIs, workflows, automation, documentation, and operational support. | It is synonymous with a web portal. |
| Internal developer portal | A user-facing UI/catalog that helps people discover services, documentation, ownership, and platform actions. | A portal alone is the platform. |
| Golden path / paved road | An opinionated, supported route for a common task, with documented boundaries and alternatives. | It must be mandatory for every workload. |
| Self-service | A user obtains an authorized result through a supported interface without an operator manually fulfilling a ticket. | Self-service means unrestricted permissions. |
| Platform team | The team accountable for the platform product, its interfaces, reliability, roadmap, and support. | It owns every product team's application. |
| Stream-aligned/product team | A team organized around delivering a product or value stream and accountable for its service outcomes. | It should independently rebuild every shared capability. |
| Enabling team | A team that helps other teams acquire skills or overcome a temporary capability gap. | It should permanently take over the other team's work. |
| Cognitive load | The mental effort required to understand and perform a task. | Every concept can or should be hidden behind an abstraction. |
| Intrinsic / extraneous / germane load | Common cognitive-load-theory terms for task complexity, avoidable presentation burden, and effort devoted to learning/schema construction. Exact definitions and attribution should be checked against the chosen learning-science source **[VERIFY]**. | These labels are universally measured quantities or a platform metric. |
| Thinnest viable platform (TVP) | A useful design principle here: start with the smallest coherent set of capabilities that solves a demonstrated user problem. Exact phrase and attribution **[VERIFY]**. | “Thin” means insecure, incomplete, or unsupported. |
| DevOps | A culture and set of practices emphasizing collaboration, shared responsibility, automation, and feedback across development and operations. | A job title or a platform product. |
| SRE | An engineering discipline applying software and operational methods to reliability, with explicit objectives and operational controls. | A synonym for platform engineering. |
| Platform as a product | Treating internal developers as customers and managing shared capabilities with product discovery, value, roadmap, documentation, support, reliability, and outcome measures. | The platform team can mandate adoption and call the product successful. |

The DevOps/SRE/platform distinction above is a practical framing, not a universal taxonomy **[ASSUMPTION]**. Platform engineering productizes selected shared capabilities; it does not replace DevOps collaboration or SRE reliability engineering.

#### Platform architecture and ownership boundary

```text
Developer / data or ML team
        |
        +-- Portal UI / CLI / Git PR / documented API
        |       (front doors; not the source of authorization truth)
        v
Platform product interfaces
        |
        +-- Templates and platform APIs
        +-- Policy and entitlement checks  <--- preventive guardrails
        v
Automation and control
        |
        +-- CI validation and build
        +-- GitOps / controllers / provisioning workflows
        v
Infrastructure and runtime
        |
        +-- cluster, network, storage, database, queue, model runtime
        v
Running workload
        |
        +-- telemetry, cost allocation, support, incident feedback
        +----------------------------------------------+
                                                       |
                         product and platform roadmaps+
```

**Platform-team ownership:** supported templates and APIs, shared automation, platform control-plane components, documentation, guardrails, platform SLOs, support, compatibility, and lifecycle communication.

**Product-team ownership:** application behavior, data/model correctness, product-level SLOs, workload-specific configuration within policy, business decisions, and operating the service according to the agreed responsibility model.

**Shared boundary:** onboarding, production readiness, service ownership metadata, incident response, upgrades, and exception decisions. A platform should make the boundary visible rather than implying that responsibility disappears after a button is clicked.

#### Developer journey

```text
Idea -> Repository -> First deploy -> Production -> Operate
  -> Evolve / migrate -> Retire
```

At each step ask: what is the developer trying to accomplish, what must they know, what does the platform provide, what remains their responsibility, and how do they recover when it fails?

#### What the platform may provide, integrate, or leave to teams

- **Provide:** reusable service skeletons, supported workflow interfaces, standard CI entry points, baseline policies, ownership metadata conventions, and platform support.
- **Integrate:** cluster/runtime, databases, object storage, queues, identity, secrets, observability, backup, and cost systems through stable interfaces.
- **Leave to product teams:** business logic, data semantics, model quality, domain-specific release decisions, and service-level operational decisions that require product context.

The classification is contextual. A small organization may provide only a repository template and documented CI workflow; a larger data organization may integrate a broad set of managed capabilities. Do not create a platform feature merely because a tool exists.

For this data/ML platform, candidate provisionable capabilities include: a team namespace with quotas and policies; an approved PostgreSQL database class (M05); an object-store bucket or prefix (M13); a queue or event-consumer capability (M15/KEDA integration); a model-registry entry (M13 Unit 5); secret references and workload identity (M09); dashboards and alerts (M10/M11); a CI pipeline (M02); a GitOps application (M08); and cost-owner labels and showback metadata (M15). These are **candidate capabilities**, not a promise that Unit 1 provisions them. Each must have an entitlement, owner, lifecycle, support boundary, and verification contract before it becomes self-service.

The platform may provide the namespace and policy envelope, integrate a database operator or object store, and leave schema design, data retention decisions, model quality, and business-level queue semantics to the product team. This distinction prevents “self-service” from becoming a blank cheque for infrastructure privileges.

#### Synthetic data/ML personas

These are **synthetic teaching personas**, not findings from interviews:

| Persona | Job to be done | Likely friction to investigate |
|---|---|---|
| Data engineer | Deliver a repeatable batch/ETL pipeline safely. | Environment setup, data-store access, retries, observability. |
| ML engineer | Deploy and operate a model-serving endpoint. | Image/runtime standards, model artifact access, rollout and rollback. |
| Data scientist | Move an experiment toward a governed production workflow. | Excessive service ceremony, environment reproducibility, unclear handoff. |
| Analytics engineer | Publish tested transformations with clear ownership. | CI conventions, data quality checks, lineage/ownership metadata. |
| Platform engineer | Maintain reusable capabilities without becoming a ticket bottleneck. | Support load, compatibility, drift, unsafe requests. |
| SRE | Understand service dependencies and reliability posture. | Missing ownership, alert/runbook gaps, platform-wide blast radius. |
| Security reviewer | Verify policy and identity controls. | Unreviewed templates, excessive permissions, missing evidence. |
| Engineering manager | Improve delivery flow while managing risk and cost. | Unclear outcomes, duplicate investments, opaque support commitments. |

#### M01–M15 integration contract

M16 packages earlier mechanisms as a developer-facing product; it does not re-teach their implementation.

| Earlier module | Capability M16 should package | Example verification evidence |
|---|---|---|
| M01 | Hardened, digest-pinned images and base-image program. | Generated workload references an approved immutable image digest. |
| M02 | Reusable CI workflows and least privilege. | CI configuration calls the approved workflow; negative test rejects excess permissions. |
| M03 | Manifest standards, probes, requests/limits, PodDisruptionBudgets (PDBs), and Pod Security Standards (PSS). | Rendered manifests contain required fields; negative tests reject missing resource controls, probes, PDB requirements, or an invalid security posture. |
| M04 | Default-deny NetworkPolicy and TLS. | Generated network policy and a negative connectivity test. |
| M05 | Operator-managed databases and backups, including the approved PostgreSQL service class where applicable. | Provisioning request maps to an approved database class and backup policy; a request outside the allowed class is rejected. |
| M06 | Helm library chart and Kustomize components. | Template references a supported version and passes render/validation checks. |
| M07 | IaC modules and guardrails; Unit 9 build/adopt/buy decision practice; Unit 12 Crossplane foundations (providers, managed resources, XRDs/Compositions, claims, deletion semantics, and Crossplane-versus-Terraform trade-offs). | Platform API maps to reviewed modules/compositions; policy tests reject unsafe input. Unit 6 of M16 designs the product API and lifecycle on this foundation. |
| M08 | GitOps, rings, digest promotion, feature flags. | A change follows a staged promotion record. |
| M09 | Secret references and workload identity. | No secret value appears in generated repository; workload uses an approved identity reference. |
| M10 | SLO templates, alert packs, runbooks, Operational Readiness Review (ORR), on-call design, blameless postmortems, and DORA measurement/anti-gaming principles (including M10 Unit 11). | Service onboarding includes an owner, SLO proposal, alert/runbook references, and readiness record; platform on-call has an escalation path. |
| M11 | Instrumentation, dashboards-as-code, telemetry standards, and the service catalog as ownership/dependency metadata (M11 Unit 7 handoff). | Generated service emits required telemetry and has accurate ownership/dependency metadata. |
| M12 | Signing, SBOM/provenance, admission policy bundles. | Build evidence and admission test prove required attestations/policies. |
| M13 | Backup/restore defaults, DR tiers, and the model-registry capability introduced in M13 Unit 5. | Workload declares a tier and restore evidence is linked; model-registry access is an entitled reference, not a secret embedded in a repository. |
| M14 | Fleet/cluster vending, multi-region options, rollout rings, and tenancy alternatives (namespace, virtual-cluster, or cluster-per-tenant patterns as previously studied). | Target environment, tenant boundary, and rollout ring are explicit; M16 Units 3 and 7 apply the cluster-vending and tenancy handoffs. |
| M15 | Cost labels, quotas, priority classes, KEDA/spot patterns, release capacity/cost gates, and showback (including M15 Unit 4). | Generated workload has cost ownership labels and a quota/priority decision; portal showback is a later M16 integration, not a Unit 1 implementation. |

Example trace: M01 owns how the hardened base image is built. M16's golden path chooses that approved image by digest, documents the update channel, and adds a conformance check. The learner verifies the rendered/generated repository and a negative test; M16 does not re-teach image construction.

**This unit teaches:** platform product principles, user/problem discovery, baseline measurement, capability boundaries, platform-team operating model, and product-governance foundations.

**Deferred to later M16 units:** golden-path construction and secure template defaults (Unit 2); self-service provisioning and cluster vending (Unit 3); Backstage/catalog implementation and portal showback (Unit 4); Copier/Cookiecutter scaffolding implementation (Unit 5); Crossplane platform API design/lifecycle (Unit 6); tenant-isolation implementation and onboarding (Unit 7); detailed platform SLO/adoption/developer-experience measurement (Unit 8); and versioning, compatibility, deprecation, and migration automation (Unit 9). Practice questions and the self-service data/ML platform portal capstone consolidate these units.

**M17 forward reference:** M16 is the platform-engineering productization module. The separate `../17-Production-DevOps-Integrated-Capstone/` stage integrates the wider production DevOps/SRE capabilities. This lesson establishes the platform product boundary and evidence baseline; it does not implement or replace M17's integrated production capstone.

Reference frameworks for awareness: *CNCF Platforms White Paper*, *CNCF Platform Engineering Maturity Model*, and *Team Topologies* by Matthew Skelton and Manuel Pais. Current text, terminology, editions, and attribution are **[VERIFY]** items; this lesson does not reproduce framework text or claim exact definitions from memory.

### 1.3 Level 1 — Beginner

#### First-principles explanation

Imagine a data engineer needs to create a new batch pipeline. Without a platform product, they may independently choose a base image, create a repository, configure CI, write Kubernetes manifests, request credentials, set up telemetry, choose a backup tier, add cost labels, and arrange deployment promotion. Each action is reasonable, but the engineer must know many systems before delivering the pipeline.

A platform product reduces repeated decisions. It provides a documented supported path, automates safe defaults, and exposes the remaining choices. It does **not** decide whether the pipeline's business logic is correct, whether its output is useful, or whether the product team has met its domain SLO.

Self-service is not “give everyone cluster-admin.” It is “let an authorized team request a database class they are entitled to receive, with policy checks and traceable results.” A safe platform makes the authorized action easy and the unauthorized action fail clearly.

#### Guided local lab: create a baseline worksheet

Create a working directory:

```bash
mkdir -p unit1-platform-product-lab/{data,src,tests,artifacts,decisions}
cd unit1-platform-product-lab
python3 --version
```

Create `artifacts/manual-baseline.md`:

```markdown
# Manual baseline — learner measurement

Workload archetype: ______________________________
Start boundary: idea approved and service requirements recorded.
End boundary: deployed workload is reachable, observable, owned, and has
the agreed security/reliability/cost evidence.
Machine/OS: __________________  Date: ______________
Git commit or notes revision: ______________________

| # | Activity | Start | End | Elapsed | Steps | Blocker/rework | Evidence | Complete? |
|---|---|---|---|---|---:|---|---|---|
| 1 | Clarify workload and owner | | | | | | | |
| 2 | Create repository and structure | | | | | | | |
| 3 | Select hardened image | | | | | | | |
| 4 | Configure CI and tests | | | | | | | |
| 5 | Configure package/manifests | | | | | | | |
| 6 | Configure identity and secret references | | | | | | | |
| 7 | Configure network/security policy | | | | | | | |
| 8 | Configure deployment/promotion | | | | | | | |
| 9 | Configure telemetry, alerts, runbook | | | | | | | |
| 10 | Configure backup/DR and cost metadata | | | | | | | |
| 11 | Deploy and verify | | | | | | | |
| 12 | Record handoff and support boundary | | | | | | | |

Total elapsed time: __________
Total human steps: __________
Retries/rework count: ________
Blocked time (reported separately): __________
Unresolved risks: __________________________________
```

Use the same workload archetype, start/end boundaries, machine, and evidence standard if repeating the exercise. Record active work time and blocked/waiting time separately. Count a step when a distinct action or decision is completed; define your counting convention before timing. Do not compare one run that includes security review with another that omits it.

**Representative expected result:** a completed worksheet with actual learner-entered timings and evidence references. No times are prefilled because they must be measured by you. The measurement is laptop- and learner-specific, not a productivity benchmark. Retain it for comparison in the M16 capstone.

#### What just happened?

You selected a workload and defined a reproducible delivery boundary. You decomposed the journey into observable activities, recorded time and rework, and linked claims to evidence. This creates a baseline against which a later platform design can be evaluated. A shorter time is not automatically better if security, observability, or recovery evidence was removed.

#### Beginner mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Treating the portal as the platform | A polished page links to manual tickets. | Map the underlying workflows, APIs, automation, and support. |
| Timing only command execution | Waiting, approvals, and rework disappear. | Record active, blocked, and total elapsed time separately. |
| Hiding every system detail | Developers cannot debug failures. | Expose resource identity, logs/events, ownership, and recovery steps. |
| Assuming self-service means broad access | Users can request resources outside entitlement. | Enforce authorization and policy before provisioning. |
| Calling synthetic personas “users” | Product decisions are based on invented evidence. | Label simulations and validate with real users before adoption decisions. |

### 1.4 Level 2 — Intermediate

#### Platform product management

A platform team needs product discovery, not only a backlog of infrastructure requests. Research methods answer different questions:

| Method | What it can reveal | Blind spot |
|---|---|---|
| Interview | Motivation, context, perceived friction, workarounds. | Recall and selection bias; stated preference may differ from behavior. |
| Observation | Actual sequence, handoffs, interruptions, hidden work. | A small sample may not represent all teams. |
| Friction log | Repeated obstacles close to when they occur. | Depends on consistent recording and participation. |
| Survey | Structured feedback across a defined group. | Question wording and response bias; weak for discovering unknown problems. |
| Support-ticket analysis | Recurrent failure categories and support demand. | Captures people who ask for help, not silent workarounds. |
| Usage telemetry | Which platform paths are used and where they fail. | Usage does not explain motivation; privacy and interpretation matter. |

The lab below uses synthetic records solely to practice coding and analysis. Real product decisions require interviews/observation with actual developers, consent-appropriate telemetry, and validation across relevant workload types.

#### Jobs, problems, and prioritization

A useful job statement is: “When I need to [situation], I want to [motivation/action], so I can [outcome].” Example (synthetic): “When I promote a tested batch pipeline, I want the approved deployment path to carry the image digest and environment metadata, so I can release without reconstructing the process manually.”

Separate a symptom from a root problem:

- Symptom: “Teams ask for deployment help.”
- Possible root causes: unclear documentation, unreliable workflow, missing permission, confusing error, or no supported path.
- Evidence needed: observe a real onboarding attempt, inspect failed workflow records, and ask the requester what they were trying to achieve.

RICE-style prioritization is one optional method; the name and exact framework attribution are **[VERIFY]**. For a simple exercise, estimate reach, impact, confidence, and effort using a declared scale, then compute a score only if the chosen formula is documented. Never treat a synthetic score as objective truth. A transparent value-versus-effort discussion is often more useful than false numerical precision.

For practice only, one commonly encountered RICE-style calculation is `Reach × Impact × Confidence ÷ Effort`. The precise scales and attribution must be verified before organizational use **[VERIFY]**. A synthetic worked example could assign a candidate “standardize first-repository setup” Reach = 4 hypothetical teams, Impact = 2 on a declared 0–3 scale, Confidence = 0.5 (50%, an assumption), and Effort = 2 person-weeks, producing `4 × 2 × 0.5 ÷ 2 = 2`. These are **[ILLUSTRATIVE] synthetic inputs**, not a benchmark or a validated priority. The useful practice is to expose each assumption and compare it with an alternative, not to treat the resulting score as scientific precision.

#### Synthetic friction-analysis lab artifacts

Create `data/synthetic-friction-log.csv`:

```csv
record_id,source,persona,theme,severity,description
SYN-001,interview,data_engineer,environment_setup,3,"A new pipeline needs several manual environment decisions."
SYN-002,ticket,ml_engineer,ci_permissions,4,"A model build fails because the workflow identity lacks a required scoped permission."
SYN-003,friction_log,data_scientist,documentation,2,"The supported experiment-to-production handoff is unclear."
SYN-004,ticket,analytics_engineer,observability,3,"A deployed transformation has no obvious dashboard or owner link."
SYN-005,interview,platform_engineer,template_drift,4,"Teams copy an old starter repository and do not receive fixes."
SYN-006,usage_event,data_engineer,environment_setup,2,"A synthetic onboarding path stops before environment validation."
SYN-007,ticket,sre,ownership_metadata,3,"An alert has no reliable service owner metadata."
SYN-008,interview,engineering_manager,cost_visibility,2,"Teams cannot easily see the cost owner for a workload."
```

Create `src/analyze_friction.py`:

```python
"""Analyze a clearly synthetic platform-friction CSV using transparent rules."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

VALID_SEVERITY = {1, 2, 3, 4, 5}


def analyze(path: Path) -> list[dict[str, int | str]]:
    totals: dict[str, dict[str, int]] = defaultdict(
        lambda: {"frequency": 0, "severity_sum": 0}
    )
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"record_id", "theme", "severity"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"CSV must contain columns: {sorted(required)}")

        seen_ids: set[str] = set()
        for line_number, row in enumerate(reader, start=2):
            record_id = (row.get("record_id") or "").strip()
            theme = (row.get("theme") or "").strip().lower()
            if not record_id or not theme:
                raise ValueError(f"line {line_number}: record_id and theme are required")
            if record_id in seen_ids:
                raise ValueError(f"line {line_number}: duplicate record_id {record_id}")
            seen_ids.add(record_id)
            try:
                severity = int(row["severity"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"line {line_number}: severity must be an integer") from exc
            if severity not in VALID_SEVERITY:
                raise ValueError(f"line {line_number}: severity must be 1..5")
            totals[theme]["frequency"] += 1
            totals[theme]["severity_sum"] += severity

    results = []
    for theme, values in totals.items():
        frequency = values["frequency"]
        severity_sum = values["severity_sum"]
        # Transparent score: number of records multiplied by mean severity.
        score = frequency * (severity_sum / frequency)
        results.append({
            "theme": theme,
            "frequency": frequency,
            "mean_severity": round(severity_sum / frequency, 2),
            "frequency_x_mean_severity": round(score, 2),
        })
    return sorted(
        results,
        key=lambda item: (-float(item["frequency_x_mean_severity"]), str(item["theme"])),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    try:
        rows = analyze(args.csv_path)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print("SYNTHETIC DATA — not evidence about real developers")
    print("theme,frequency,mean_severity,frequency_x_mean_severity")
    for row in rows:
        print(
            f"{row['theme']},{row['frequency']},"
            f"{row['mean_severity']},{row['frequency_x_mean_severity']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Create `tests/test_analyze_friction.py`:

```python
import tempfile
import unittest
from pathlib import Path

from src.analyze_friction import analyze


class AnalyzeFrictionTests(unittest.TestCase):
    def write_csv(self, text: str) -> Path:
        temp = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", delete=False
        )
        temp.write(text)
        temp.close()
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        return Path(temp.name)

    def test_aggregates_and_sorts_deterministically(self):
        path = self.write_csv(
            "record_id,theme,severity\n"
            "a,docs,2\nb,setup,4\nc,setup,2\n"
        )
        result = analyze(path)
        self.assertEqual([row["theme"] for row in result], ["setup", "docs"])
        self.assertEqual(result[0]["frequency_x_mean_severity"], 6.0)

    def test_empty_csv_returns_empty_result(self):
        path = self.write_csv("record_id,theme,severity\n")
        self.assertEqual(analyze(path), [])

    def test_rejects_invalid_severity(self):
        path = self.write_csv("record_id,theme,severity\na,docs,9\n")
        with self.assertRaises(ValueError):
            analyze(path)

    def test_rejects_duplicate_ids(self):
        path = self.write_csv(
            "record_id,theme,severity\na,docs,2\na,setup,3\n"
        )
        with self.assertRaises(ValueError):
            analyze(path)

    def test_rejects_missing_columns(self):
        path = self.write_csv("id,theme\nx,docs\n")
        with self.assertRaises(ValueError):
            analyze(path)


if __name__ == "__main__":
    unittest.main()
```

From the `unit1-platform-product-lab` directory, run:

```bash
python3 src/analyze_friction.py data/synthetic-friction-log.csv
python3 -m unittest discover -s tests -v
```

**Representative expected output (not claimed as executed):**

```text
SYNTHETIC DATA — not evidence about real developers
theme,frequency,mean_severity,frequency_x_mean_severity
environment_setup,2,2.5,5.0
ci_permissions,1,4.0,4.0
template_drift,1,4.0,4.0
documentation,1,2.0,2.0
...
```

The score is frequency multiplied by mean severity, which algebraically equals the sum of severity values for a theme. It is a prioritization aid, not a validated measure of user pain. The script uses a deterministic alphabetical tie-breaker. Automated coding is only a starting aid: inspect records, challenge theme labels, and preserve contradictory evidence.

#### Personas, problem statements, vision, roadmap, and PRD

Create `artifacts/personas-and-journey.md` and adapt the synthetic personas above. For each persona record: context, job, desired outcome, current workaround, evidence required from real users, and what the platform must not assume. Add a journey row for idea, repository, first deploy, production, operate, evolve, and retire. At each stage record user action, friction hypothesis, platform response, product-team responsibility, and evidence.

Example problem statements (hypotheses, not findings):

1. A data engineer may repeat repository, CI, image, and deployment setup because supported defaults are not discoverable in one path.
2. An ML engineer may be unable to diagnose a deployment because the platform hides resource identity and runtime events.
3. A security reviewer may need to inspect generated defaults because policy evidence is not linked to the service.

A platform vision should describe an outcome, not a tool: “Data and ML teams can create, deploy, and operate supported workloads through understandable, secure, observable paths while retaining ownership of their product behavior.”

Create `artifacts/roadmap.md`:

```markdown
# Synthetic example roadmap — validate with real users

## Now
- Document one batch-pipeline path from repository creation to observable deployment.
- Add a local conformance checklist for image, CI, ownership, telemetry, and cost metadata.
- Publish support boundaries and an escalation route.

## Next
- Add one inference/API archetype after validating its distinct needs.
- Link service ownership and runbook metadata to a discoverable catalog.
- Add a measured template update and migration workflow.

## Later
- Evaluate self-service provisioning for approved data-store classes.
- Evaluate a portal only if discovery/action friction justifies its maintenance.
- Add tenant-specific capabilities after isolation requirements are tested.

## Outcomes and guardrails
- Outcome: reduce repeated manual decisions without removing required controls.
- Guardrails: no weakened security checks, no hidden owner, no unsupported workload forced onto the path.
- Evidence: repeatable baseline, real-user research, conformance tests, support records.
```

Create `artifacts/platform-prd.md`:

```markdown
# Platform PRD — first supported batch-pipeline path

## Problem
The current service bootstrap and delivery journey requires teams to assemble
repeated infrastructure and operational decisions. This is a hypothesis to
validate with actual developers; the lab personas and records are synthetic.

## Target users and jobs
- Data engineer: create and deploy a repeatable batch/ETL workload.
- Platform engineer: maintain safe reusable defaults without manual fulfillment.
- SRE/security reviewer: verify ownership, telemetry, policy, and readiness.

## Pain points to validate
Repository bootstrap, inconsistent CI configuration, missing owner/telemetry
metadata, unclear support boundaries, and cost ownership gaps.

## Non-goals
- Replacing every team's application architecture.
- Forcing notebooks into a microservice template.
- Building a custom portal or provisioning control plane in the first slice.
- Removing product-team ownership of business logic and service outcomes.

## Thin slice
A documented repository skeleton plus reusable CI entry point, approved image
reference, policy/validation checks, ownership and telemetry metadata, and a
clear deploy/operate handoff.

## Success measures
- Repeat the manual baseline and compare equivalent start/end boundaries.
- Record successful path completion and failure reasons.
- Validate required conformance evidence.
- Gather qualitative feedback from actual pilot developers.
- Track support demand in aggregate.

## Guardrails
Security and policy failures must remain visible; no secrets in generated
repositories; no individual productivity scoring; escape hatch and owner are
documented.

## Dependencies
M01 image program; M02 reusable CI; M03/M04 workload and network standards;
M06 packaging; M08 GitOps; M09 identity/secrets; M10/M11 reliability and
telemetry; M12 supply-chain controls; M13 recovery; M15 cost conventions.

## Security, reliability, and cost
Use approved defaults from the owning modules. Define the platform team's
support boundary and platform SLO proposal before production adoption.
Measure actual resource overhead; do not assume zero cost.

## Rollout and support
Start with one real design-partner team, one workload archetype, a documented
feedback channel, office hours, a canary rollout, and a rollback plan.

## Risks
Template drift, policy regression, hidden coupling, poor documentation,
unvalidated demand, and platform-team capacity constraints.

## Decision log
Record each accepted/rejected capability, evidence, owner, date, and revisit
condition.
```

Create `artifacts/assumptions-register.md` and record every unverified assumption with owner, validation method, and status. At minimum include: the batch pipeline is common enough to prioritize; existing CI and image mechanisms can be exposed cleanly; teams will accept the supported path; and the platform team can support the proposed interface.

Use this starter content:

```markdown
# Assumptions register — synthetic platform exercise
| ID | Assumption | Why it matters | Owner | Validation method | Status |
|---|---|---|---|---|---|
| A-001 | Batch/ETL is a useful first archetype. | Determines the first thin slice. | Product owner | Observe and interview real data teams. | Unvalidated |
| A-002 | Existing CI/image workflows can be consumed through stable interfaces. | Avoids rebuilding M01/M02. | Platform engineer | Prototype integration and negative tests. | Unvalidated |
| A-003 | The proposed supported path removes a repeated developer problem. | Core value proposition. | Research owner | Observe real onboarding and compare matched baselines. | Unvalidated |
| A-004 | Platform team can support the interface and on-call load. | Prevents an unsupported product promise. | Platform lead | Capacity and support review. | Unvalidated |

Never change a row to “validated” based only on synthetic lab data.
```

#### Product operating model

A platform team should have enough product, software, operations, and user-experience capability to own the whole service, not merely the cluster. Team size and shape must follow actual demand and service boundaries. A platform team provides a service, collaborates with product teams on new capabilities, and enables teams to use the platform effectively. Exact Team Topologies interaction-mode wording is **[VERIFY]**. As a practical, non-attributed operating hypothesis, a platform team commonly offers a supported service interface; temporarily collaborates with a stream-aligned team when designing a new capability; and enables teams through docs, examples, pairing, and office hours. If using Team Topologies labels such as “X-as-a-Service,” “collaboration,” or “facilitating,” verify the exact current wording and intended boundaries in the authoritative book/source before formal adoption.

A lightweight synthetic operating-model artifact can be saved as `artifacts/team-support-model.md`:

```markdown
# Synthetic platform operating model — exercise only

## Service boundary
- Platform team owns: shared templates, platform interfaces, guardrails,
  platform control-plane reliability, documentation, and platform support.
- Product team owns: application behavior, data/model correctness, service
  objectives, domain alerts, and workload-specific decisions within policy.
- Joint: onboarding, production readiness, exceptions, and cross-boundary incidents.

## Intake and triage
- Intake: local issue template with capability, tenant/team, impact, evidence,
  urgency, and requested outcome. Do not include credentials or secret values.
- Triage: rotating platform duty owner; security-sensitive requests route to
  the designated security reviewer.
- Escalation: platform incident lead for shared failures; product owner for
  workload-only failures; joint lead when ownership is ambiguous.
- Office hours: one published weekly session; attendance is optional.

## Illustrative internal response targets (not contractual guarantees)
- Critical shared-platform outage: acknowledge within 15 minutes during
  staffed coverage; publish impact and next update.
- High-impact blocked onboarding: acknowledge within one business day.
- Standard request: triage within three business days.
- Feature request: acknowledge and record a roadmap decision, not promise
  delivery. Replace these [ILLUSTRATIVE] targets with an agreed service model.

## RACI (synthetic example)
| Activity | Platform | Product team | SRE | Security |
|---|---|---|---|---|
| Template and shared workflow | A/R | C | C | C |
| Application behavior and tests | C | A/R | C | I |
| Platform incident | A/R | C | R/C | C |
| Workload incident | C | A/R | R/C | C |
| Policy baseline | R | C | C | A |
| Exception review | R | R | C | A |

A = accountable; R = responsible; C = consulted; I = informed. Confirm
that each activity has one accountable role in the real organization.
```

The targets and organization above are deliberately **[ILLUSTRATIVE]**. They are a template for discussion, not a service-level agreement or a claim about an actual team.

Support design should include:

- A documented intake channel and required request information.
- A rotating triage owner and clear escalation path.
- Office hours for design and onboarding questions.
- Severity definitions and response targets, explicitly described as internal targets unless a contract says otherwise.
- Known support boundaries: what the platform team owns, what the product team owns, and what requires a joint incident.
- A visible roadmap and a reasoned response to requests that are deferred or declined.

Adoption should normally be earned through value: recruit real design partners, observe onboarding, provide documentation and migration assistance, identify champions, and iterate. A safety-critical security or compliance baseline may be mandatory, but a mandate must come with enablement, a documented exception/appeal path, and clear ownership.

#### MVP and anti-pattern catalogue

A useful first release is a **walking skeleton**: one end-to-end workload path that can be created, validated, deployed, observed, and supported. It is preferable to ten disconnected portal tiles that do not complete a developer task.

| Pattern | Use when | Do not use when |
|---|---|---|
| Documentation plus validated template | A common path exists but automation demand is not yet proven. | Manual steps create unacceptable risk or delay. |
| Shared workflow/API | Multiple teams repeat the same action and its contract can be made stable. | Workloads differ materially and the abstraction would be forced. |
| Portal over stable APIs | Discovery and self-service are genuine user problems. | A small team can navigate a README and CLI more effectively. |
| Supported escape hatch | Advanced or unusual workloads need controlled flexibility. | It becomes an undocumented bypass around security controls. |
| Design-partner rollout | A capability needs feedback before broad release. | It is used to claim organization-wide adoption from one team. |

| Anti-pattern | Developer/business impact | Corrected version |
|---|---|---|
| Operations ticket queue renamed “platform” | Waiting remains; self-service is absent. | Automate bounded, authorized requests and measure queue causes. |
| Ivory-tower design | Capabilities solve imagined problems. | Observe real workflows and validate with users. |
| “Build it and they will come” | Adoption is assumed, not earned. | Recruit design partners and iterate from evidence. |
| One framework for every workload | Data science and batch jobs inherit irrelevant ceremony. | Shared core plus workload-specific archetypes. |
| Platform as bottleneck | Every change requires platform-team intervention. | Stable interfaces, clear entitlements, delegated ownership. |
| Over-abstraction | Debugging and advanced needs become impossible. | Expose underlying resources and supported escape hatches. |
| No success measures | The team cannot distinguish value from activity. | Measure journey outcomes and guardrails. |
| Neglected documentation | Users depend on tribal knowledge. | Version docs with the capability and test examples. |
| Platform team does not dogfood | Platform failures are discovered by customers first. | Use the supported path for platform-owned services where appropriate. |

#### Observable before/after exercise

Use the manual worksheet to record the current path. Then design a target path that removes repeated decisions but preserves security, reliability, and ownership checks. Do not claim improvement until you repeat the task with the same workload class, boundaries, and evidence criteria. Compare:

- elapsed time, active time, and blocked time separately;
- number of distinct human decisions/actions;
- failed checks and rework;
- completeness of security, observability, ownership, and cost evidence;
- support interventions required.

A path that is faster only because it skips controls is a regression. In this local exercise the target path is a design proposal, not an implemented production platform.

### 1.5 Level 3 — Advanced

#### Capability map and boundary decisions

| Capability | Default platform role | Product-team responsibility |
|---|---|---|
| Bootstrap/scaffolding | Provide supported skeletons and update guidance. | Select archetype and implement domain logic. |
| CI/CD | Integrate reusable build/test/deploy workflows. | Own application tests and release intent. |
| Runtime/compute | Integrate approved runtime classes and scaling controls. | Set workload behavior and validate capacity needs. |
| Data stores | Integrate approved database/object/queue options. | Own schema, data lifecycle, and query behavior. |
| Networking/ingress | Provide secure patterns and guardrails. | Declare legitimate service communication needs. |
| Secrets/identity | Provide reference patterns and workload identity integration. | Request least-privilege access for a justified purpose. |
| Observability | Provide instrumentation conventions, dashboard/alert templates. | Define domain signals and act on service alerts. |
| Security/policy | Provide preventive baseline controls and evidence. | Fix application vulnerabilities and own domain risk. |
| Cost/FinOps | Provide labels, quotas, showback, and safe defaults. | Own workload sizing and explain unusual consumption. |
| Reliability/DR | Provide tiers, templates, and shared recovery mechanisms. | Set product objectives and test application recovery. |
| Portal/docs | Provide discovery and supported interfaces where useful. | Keep service metadata and runbooks accurate. |
| Support | Provide platform incident support and enablement. | Operate the product service and engage the platform team at defined boundaries. |

#### Interfaces and layers

A platform should not require every developer to use one front door. A portal, command-line interface (CLI), Git pull request (PR), and API can all invoke the same underlying platform contract. This is API-first design: the capability and authorization contract should not be trapped inside a particular UI. If the portal is replaced, the underlying workflows and resource ownership should remain understandable.

```text
Developer experience: portal | CLI | Git/PR | API
                 |
Platform contract: templates | APIs | policy | entitlement
                 |
Orchestration: CI | GitOps | controllers | workflow automation
                 |
Providers: cluster | IaC modules | data services | identity
                 |
Runtime: workloads, data, telemetry, recovery
```

This extends M07's infrastructure-as-code foundations and M14's fleet/cluster operations. It does not mean every platform needs a custom orchestration layer. Prefer an adopted capability when it already solves the problem; build the product-specific integration, safe defaults, and developer experience where those are differentiating.

#### Abstraction, inspectability, and escape hatches

Abstract undifferentiated work: secure defaults, standard metadata, routine CI wiring, approved runtime classes, and policy validation. Preserve choices that differentiate workloads: model-serving performance requirements, batch scheduling needs, data semantics, and specialized hardware constraints.

A leaky abstraction is not automatically a defect. A platform API may expose a database class while the underlying database still has observable events, resource names, and failure modes. The defect is pretending the underlying system does not exist. Developers and on-call responders need to inspect generated resources, logs, events, configuration, and ownership.

Document an escape hatch for advanced users—for example, a supported path to submit reviewed raw Kubernetes or IaC changes—with explicit consequences: support tier, review requirements, security constraints, and upgrade compatibility. An escape hatch is not a policy bypass.

#### Thinnest viable platform and cognitive-load budget

Start with documentation, a validated template, and a repeatable check. Add self-service automation only when evidence shows that repeated manual work, error risk, or waiting justifies it. Remove features that do not solve a real problem or cannot be supported.

Inventory the concepts developers must understand:

| Concept | Manual path | Target path | Classification |
|---|---|---|---|
| Image provenance/digest | Select and verify manually | Approved default plus visible evidence | Essential outcome; incidental implementation can be reduced |
| CI permissions | Assemble workflow permissions | Reusable least-privilege workflow | Essential to understand failure/ownership |
| Workload resources/probes | Write and validate manifests | Archetype defaults with inspectable output | Essential to tune; boilerplate reduced |
| Secret values | Handle values directly | Reference identity/secret contract | Essential security concept; unsafe handling removed |
| Cost ownership | Remember labels | Generated cost metadata | Essential accountability; repeated syntax reduced |
| Service SLO/runbook | Assemble from scratch | Linked templates and checks | Essential product responsibility |

Count concepts using a consistent rule, and classify them as essential or incidental. Set a local target such as “reduce repeated manual configuration decisions while retaining all required controls.” Do not promise a universal percentage. A notional 80/15/5 split between common path, supported variation, and escape hatch is an **[ILLUSTRATIVE] heuristic only**, not an industry statistic or a required design ratio.

#### Workload archetypes

- **Inference/API service:** request/response runtime, latency/error objectives, model artifact access, controlled rollout.
- **Batch/ETL pipeline:** schedule/event trigger, retries, data access, idempotency, completion and freshness signals.
- **Streaming consumer:** throughput/lag, partitioning, backpressure, replay, and offset behavior.
- **Model-serving endpoint:** model loading, accelerator/runtime constraints where relevant, versioned model artifact, traffic and quality monitoring.
- **Notebook/experiment workspace:** interactive lifecycle, ephemeral or persistent storage, identity, data access, and a clear path to reproducible production artifacts.

Use a shared core for identity, ownership, policy, telemetry, and cost metadata, then archetype-specific layers. Do not force a data scientist's exploratory notebook into a microservice ceremony. Define a notebook-to-production transition that makes code, dependencies, data access, model artifacts, tests, and ownership reproducible.

#### Security, reliability, cost, and failure domains

The platform may become a critical dependency for delivery. A bad template, policy, API, or shared controller can affect many teams at once. Use canary tenants, staged rollout rings, compatibility checks, rollback plans, and clear change communication. Treat the platform's own SLO, backup, recovery, and on-call design as product requirements.

Secure defaults should be traceable to their source modules and verified, not merely asserted:

- M01 image: negative test rejects a mutable or unapproved image reference.
- M02 CI: test rejects excess workflow permissions.
- M03/M04 workload/network: validation rejects missing resource controls or required network policy.
- M09 identity: scan generated files for secret-like values and verify references rather than values.
- M10/M11 reliability/telemetry: readiness review rejects missing owner, telemetry, or runbook links.
- M12 supply chain: admission/conformance test rejects missing required provenance evidence.
- M13 recovery: verify declared tier and a restore-test record.
- M15 cost: validation rejects missing cost-owner labels or quota declaration.
- M03 availability/security posture: negative tests reject missing readiness/liveness probes where required, absent resource requests/limits, missing PDB for a workload class that requires one, or a prohibited Pod Security setting.
- M04 network: a generated workload without the required default-deny NetworkPolicy or TLS configuration fails conformance; verify both the positive approved path and the negative unapproved path.
- M08 promotion: a release cannot be promoted when the required digest/evidence is absent or when the environment ring is out of sequence.
- M13 model registry: an unauthorized team cannot read or publish a registry entry; verify entitlement denial without exposing model artifacts or credentials.

Do not re-teach those mechanisms here; use the earlier module's tests as integration contracts.

#### Build vs adopt vs buy

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Build | Exact fit and control over differentiated workflow. | Engineering and long-term maintenance. | Bespoke system becomes a product the team must operate. | No suitable capability exists and the workflow is strategically important. |
| Adopt open source | Existing ecosystem and inspectability. | Integration, upgrades, support, security review. | Project health or plugin compatibility changes. | It meets most needs and the team can operate it. |
| Buy managed | Reduced operational burden and vendor support. | Recurring cost and contract/vendor dependency. | Lock-in, data/control constraints, exit complexity. | Total operating value exceeds cost and risk is acceptable. |

Evaluate fit, differentiation, maintenance burden, team skills, security, ecosystem health **[VERIFY]**, lock-in, exit path, and total operating cost. Default to adopting an existing capability before building infrastructure. Build the integration, workflow, and safe defaults that create user value. Link this decision to M07 Unit 9 and M12 Unit 11.

Also choose deliberately between a thin and rich platform. A thin platform has fewer capabilities and lower maintenance burden but may leave more integration work to teams. A rich platform can reduce repeated effort but increases coupling, support obligations, and blast radius. A small organization may need documentation, templates, and shared CI only; do not recommend a portal by default for a handful of developers.

#### Illustrative economics model

Use variables, not invented facts:

- `H` = hours saved per workload, measured in a comparable pilot.
- `N` = number of eligible workloads in the chosen period.
- `C` = loaded labor cost per hour, supplied by the organization.
- `P` = platform build/operate cost for the same period.
- `D` = separately evidenced avoided duplication/incident cost, if any.

A simple modeled net value is:

`Net value = (H × N × C) + D − P`

Do not double-count time savings inside `D`. Do not assign a monetary value to an avoided incident without a defensible method. Sensitivity-test low/base/high assumptions for H and N. Mark every hypothetical input **[ILLUSTRATIVE]**, state the unit and period, and replace it with actual measured/approved inputs before a business case. The model does not establish causation or guarantee ROI.

For a sensitivity worksheet, keep the period and units fixed and vary assumptions rather than presenting a single precise result:

| Input | Low case | Base case | High case | Source/status |
|---|---:|---:|---:|---|
| `H` hours saved per eligible workload | [ILLUSTRATIVE] | [ILLUSTRATIVE] | [ILLUSTRATIVE] | Replace with matched pilot observations. |
| `N` eligible workloads per period | [ILLUSTRATIVE] | [ILLUSTRATIVE] | [ILLUSTRATIVE] | Replace with eligible workload count. |
| `C` loaded cost/hour | [ILLUSTRATIVE] | [ILLUSTRATIVE] | [ILLUSTRATIVE] | Finance-approved input. |
| `P` platform cost per same period | [ILLUSTRATIVE] | [ILLUSTRATIVE] | [ILLUSTRATIVE] | Include build, run, support, and allocated shared cost. |
| `D` independently evidenced avoided cost | 0 unless supported | [ILLUSTRATIVE] | [ILLUSTRATIVE] | Exclude time savings already counted in `H`. |

Do not insert made-up currency values merely to make the worksheet look complete. The learner must populate the cells with measured or explicitly approved inputs. A formula test should verify arithmetic, reject negative hours/workload counts/costs where the model disallows them, and confirm that `D` is not silently counted twice.

A minimal calculator can make the arithmetic inspectable. Add these files to the lab layout; this is a local model, not a financial forecast.

Create `src/roi_model.py`:

```python
"""Transparent platform value model; inputs must be measured or labelled illustrative."""
from math import isfinite


def net_value(
    hours_saved_per_workload: float,
    workloads_per_period: float,
    loaded_hourly_cost: float,
    platform_cost_per_period: float,
    separately_justified_avoided_cost: float = 0.0,
) -> float:
    values = {
        "hours_saved_per_workload": hours_saved_per_workload,
        "workloads_per_period": workloads_per_period,
        "loaded_hourly_cost": loaded_hourly_cost,
        "platform_cost_per_period": platform_cost_per_period,
        "separately_justified_avoided_cost": separately_justified_avoided_cost,
    }
    for name, value in values.items():
        if not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError(f"{name} must be a finite number")
        if value < 0:
            raise ValueError(f"{name} must not be negative")
    gross_labor_value = (
        hours_saved_per_workload * workloads_per_period * loaded_hourly_cost
    )
    return gross_labor_value + separately_justified_avoided_cost - platform_cost_per_period
```

Create `tests/test_roi_model.py`:

```python
import unittest

from src.roi_model import net_value


class RoiModelTests(unittest.TestCase):
    def test_calculates_net_value(self):
        self.assertEqual(net_value(2, 3, 50, 100, 0), 200)

    def test_allows_negative_net_value(self):
        self.assertEqual(net_value(0, 0, 0, 100), -100)

    def test_rejects_negative_input(self):
        with self.assertRaises(ValueError):
            net_value(-1, 2, 50, 100)

    def test_rejects_non_finite_input(self):
        with self.assertRaises(ValueError):
            net_value(float("nan"), 2, 50, 100)


if __name__ == "__main__":
    unittest.main()
```

Run both test modules from the `unit1-platform-product-lab` directory with `python3 -m unittest discover -s tests -v`. The numeric unit-test values are deliberately small arithmetic fixtures, not a platform business case. For a real sensitivity analysis, create low/base/high rows using the same time period and units, compute each scenario with this function, and attach the source and confidence for every input.

**Funding and incentives:** central funding is often simpler when the platform provides shared risk controls and broad organizational capabilities; chargeback can create cost visibility but may discourage adoption or cause teams to avoid useful controls if allocation is arbitrary. Showback (M15) can make consumption visible without directly billing each team. Define the allocation unit, explain shared overhead, and give teams a way to challenge incorrect attribution. Incentives should reward platform outcomes—reliable self-service, lower repeated friction, safe defaults, and healthy adoption—not the number of features shipped or individual developer activity.

#### Decision and cognitive-load artifact templates

For each of three decisions, create an ADR file under `decisions/` (for example, `ADR-001-template-engine.md`, `ADR-002-portal-choice.md`, and `ADR-003-provisioning-boundary.md`). Use the same complete structure:

```markdown
# ADR-NNN — <decision title>
- Status: proposed / accepted / rejected / superseded
- Date and decision owner: <fill in>
- User problem and evidence: <real evidence or explicitly synthetic hypothesis>
- Options: build / adopt open source / buy managed / defer
- Decision and rationale: <fit, differentiation, skills, security, ecosystem>
- Consequences: <maintenance, support, reliability, cost, cognitive load>
- Lock-in and exit: <data portability, migration path, replacement cost>
- Assumptions: <owner, validation method, status>
- Revisit trigger: <evidence or date that reopens this decision>
```

Create `artifacts/cognitive-load-inventory.md` with one row per distinct concept or decision, not one row per command:

```markdown
# Cognitive-load inventory — learner assessment
| Journey step | Concept/decision | Manual or target | Essential/incidental | Evidence |
|---|---|---|---|---|
| Repository | Choose and wire a service skeleton | Manual | Incidental repetition | Baseline observation |
| Build | Understand required CI permission boundary | Both | Essential | Workflow and negative test |
| Deploy | Understand rollout and rollback state | Both | Essential | Promotion record |
| Operate | Find owner, telemetry, runbook | Target path | Essential outcome | Catalog and runbook check |

Manual distinct-concept count: <measure>
Target distinct-concept count: <measure>
Counting rule: count a concept once per journey, even if it appears in multiple commands.
Proposed target: <state a local, testable reduction without dropping essential controls>.
```

The before/after counts are learner measurements. Do not populate them with invented values.

#### Organizational dynamics and decision exercise

Platform funding should reflect the services and risk the platform owns. Intake should be transparent: publish request criteria, roadmap status, decision rationale, and a route to challenge or appeal. “No” should include the reason, alternatives, and the condition under which the request may be reconsidered.

**Exercise:** propose the first release for a hypothetical data organization. Defend (a) one workload archetype, (b) three capabilities to provide/integrate, (c) at least three non-goals, (d) build/adopt/buy choices, (e) one escape hatch, (f) rollout/rollback, and (g) success and guardrail measures. Explicitly identify assumptions requiring real-user validation.

### 1.6 Level 4 — Expert

#### Maturity and portfolio governance

Maturity is not a badge. Assess each capability with evidence: named users, documented value, adoption path, support ownership, reliability target, security tests, upgrade policy, and feedback loop. A score without artifacts is opinion. The CNCF Platform Engineering Maturity Model is awareness material; verify the current model and wording before adopting its categories **[VERIFY]**.

For roadmap governance, review outcomes periodically, maintain a visible “not doing” list, define sunset criteria, and record why work was prioritized. A feature should be stopped when its user problem disappears, its maintenance cost exceeds value, or a better adopted capability replaces it.

#### Policy and lifecycle automation

Automation should detect drift and make remediation understandable; it should not silently rewrite production repositories or widen permissions. A Plat-Core conformance checker can inspect generated text/configuration and fail with a precise reason. In a production platform, extend that principle into three distinct controls:

- **Conformance scanner:** checks each generated or onboarded service for required owner metadata, approved image reference, least-privilege CI, resource/probe/security defaults, telemetry/runbook links, recovery tier, and cost labels. Output should identify the file/resource, failed rule, remediation, and rule version.
- **Template/API upgrade assistant:** detects repositories on supported older template/API versions and proposes a reviewed update (for example, a pull request). It must show the diff, compatibility result, migration notes, and rollback route. Do not auto-merge breaking changes or execute arbitrary repository code with broad credentials.
- **Catalog quality checks:** verify that each catalog record has an accountable owner, lifecycle state, repository/source location, supported system/dependency links, and a freshness signal. Stale or invalid entries should be routed to an owner and clearly marked; never invent an owner to make completeness look high.

For a new user verification, create a fresh repository from the supported template, run all checks from a clean working directory, then deliberately remove one required field and confirm a clear failure. For upgrades, test both a compatible patch and a breaking API/template migration against representative generated repositories before a canary rollout.

Use a quarterly review as a decision cadence, not as a reason to delay urgent fixes. For each roadmap item record: user problem, target outcome, evidence, accountable owner, guardrails, dependencies, support cost, review date, and continue/adjust/stop decision. Maintain a visible kill list for features that are unused, duplicative, too expensive to support, or superseded.

A compact evidence-based self-assessment worksheet:

| Capability | Progression state (teaching model) | Evidence required | Gap / next action |
|---|---|---|---|
| Service bootstrap | Ad hoc / documented / templated / self-service / product-managed / optimized | Versioned template, validation, real-user completion evidence, owner, support path. |  |
| Delivery workflow | Same progression | Reusable workflow, least-privilege test, promotion evidence, failure runbook. |  |
| Runtime and data access | Same progression | Entitlement model, quota/policy checks, lifecycle owner, recovery evidence. |  |
| Catalog and support | Same progression | Ownership freshness check, support intake, response review, user feedback. |  |
| Platform operations | Same progression | SLO, on-call, incident record, recovery test, change/rollback evidence. |  |

The progression is a **teaching model**, not an official maturity scale. Assign no level without attaching the evidence named in the third column.

#### Scaling the platform organization

A small organization may operate a single platform team covering runtime and developer experience. A larger organization may split domain-aligned data platform, runtime platform, developer experience, and security platform responsibilities. Splitting teams introduces interfaces and coordination costs; a “platform of platforms” can recreate the very complexity it was meant to remove. Define service ownership and interaction boundaries before creating organizational layers. Team Topologies team types and interaction-mode terminology are **[VERIFY]**; consult the current authoritative source rather than relying on memory.

Reassess build/adopt/buy as the organization changes. Check project maintenance, release activity, security response, compatibility, community/vendor support, migration path, data portability, and exit cost. A tool that fit a small team may not fit a regulated multi-team environment, and the reverse can also be true.

#### Trust, privacy, and AI-assisted tooling

Trust depends on an honest status page or equivalent status channel, changelogs, known limitations, timely support, clear incident updates, and blameless platform postmortems. If a platform outage or bad default affects teams, communicate scope, mitigation, next update, and follow-up actions. Connect incident practice to M10 Units 4–5 rather than re-teaching it.

Measure the platform and developer experience, not individual developer productivity. Do not build individual deployment leaderboards or surveillance dashboards. Use aggregation, purpose limitation, role-based access, retention limits, and transparent documentation for telemetry. Explain what is collected and why. A metric such as “time-to-first-deploy” is a property of a defined journey and cohort, not a performance rating for a person.

AI-assisted developer tooling is awareness-only in this unit. Treat model suggestions as untrusted advisory output. Risks include source-code or secret leakage, generated insecure code, dependency/supply-chain compromise, and over-trust in recommendations. Never place secrets or sensitive data into prompts. Require human review, approved data handling, policy checks, and traceability. Connect conceptually to M10 Unit 7's AI-ops safety framework.

#### Eight synthetic failure cases

All cases below are **synthetic scenarios**, not claims about real incidents. Diagnose each with symptom → hypothesis → evidence/test → root cause → fix → prevention.

| Synthetic case and symptom | Hypothesis and evidence/test | Likely root cause | Corrective action and prevention |
|---|---|---|---|
| Custom framework has almost no users beyond its creators. | Interview intended users; inspect actual task flow and usage. | Capability was built before validating a problem. | Stop expansion, observe real work, compare adopt/buy options, and retire unused pieces. |
| Ticket queue is renamed “platform requests”; lead time remains high. | Measure request age, handoffs, repeatable request types, and manual fulfillment. | Interface changed but operating model did not. | Automate bounded requests, publish entitlements, and retain tickets only for exceptions. |
| Mandatory golden path has no escape hatch; teams fork it. | Compare forks and exception requests; inspect policy evidence outside the path. | Standardization ignored workload diversity and developer needs. | Add supported variation and controlled escape hatches; preserve common guardrails. |
| Platform change breaks many pipelines on Friday. | Inspect change scope, rollout evidence, compatibility tests, and rollback readiness. | Fleet-wide release without canary or communication. | Roll back, notify affected owners, add staged rings and compatibility tests. |
| Template and platform API upgrades become impossible; repositories drift across incompatible contracts. | Inventory template versions and compare generated repos with current defaults. | No update mechanism, API/template compatibility contract, or migration ownership. | Define versions, update guidance/PR-bot strategy, API compatibility rules, deprecation windows, and migration tests. |
| Leadership tracks individual deploy counts; trust collapses. | Review dashboards, access, purpose, and feedback from affected teams. | Individual surveillance used as a proxy for productivity. | Remove individual rankings; use aggregated platform journey and guardrail measures. |
| Stale catalog pages on-call to the wrong team. | Compare catalog owner with repository metadata and current on-call roster. | No source of truth or catalog quality checks. | Establish ownership source, freshness checks, accountable metadata owners, and fallback escalation. |
| Platform has no SLO; users stop trusting it after outages. | Review incident records, availability history, user reports, and missing objectives. | Reliability ownership was not part of the product model. | Define platform SLIs/SLOs, on-call, status communication, recovery, and post-incident follow-up. |

#### 90-day improvement plan (illustrative structure)

- **Days 1–30 — Discover:** select one real workload journey; interview and observe actual users; establish baseline and service ownership; inventory existing M01–M15 mechanisms; publish assumptions and non-goals.
- **Days 31–60 — Deliver a thin slice:** implement one supported path; add conformance and negative tests; write docs/support boundaries; run with a design-partner team; stage changes and collect qualitative feedback.
- **Days 61–90 — Operate and decide:** review journey and guardrail measures; address failure modes; update roadmap; decide whether to expand, revise, or stop; document deprecation and migration implications.

The plan is a planning template, not a claim that every organization can deliver these outcomes in 90 days.

### 1.7 SRE lens

A platform is a product with reliability obligations. If its repository bootstrap, CI entry point, policy service, identity integration, or deployment workflow is unavailable, many teams may be blocked even when their applications are healthy.

Useful indicators include:

- Successful onboarding/provisioning attempts divided by valid attempts.
- Time from a defined onboarding start to a verified first deployment.
- Template generation or validation success rate.
- Conformance rate for required platform defaults.
- Support demand and recurring failure categories.
- Adoption by eligible teams, interpreted with qualitative context.
- Upgrade lag and number of unsupported template/API versions.

Detailed metric definitions and adoption/DX measurement belong to Unit 8. Define denominators, exclusions, cohorts, and measurement windows before interpreting any ratio. Never use a metric as an individual developer performance score.

**Blast-radius questions:** Does a bad template affect only new repositories or existing services too? Can a policy regression block all deploys? Is the portal merely unavailable, or are underlying APIs unavailable? Can teams continue operating existing workloads during a platform control-plane outage? Which changes can be rolled back independently?

**Runbook snippet**

1. **Trigger:** platform workflow failures exceed the locally defined alert threshold, or several teams report the same failure.
2. **Decide:** determine whether the fault is portal/front door, platform API, shared automation, policy, provider, or workload-specific.
3. **Act:** stop further rollout; preserve evidence; roll back the last safe change if the failure is correlated with it; use the documented fallback.
4. **Verify:** run a known-good synthetic onboarding/deploy check and confirm affected teams can proceed.
5. **Communicate:** publish impact, affected capabilities, workaround, owner, and next update time.
6. **Follow up:** record root cause, update tests/runbooks, review blast radius, and communicate remediation.

**Cost/capacity:** measure actual local CPU, memory, disk, and process footprint for each lab component. For production, allocate platform overhead by a declared unit such as namespace, workload, or tenant; use M15's cost labels and hypothetical units only where real billing data is unavailable. Do not invent per-tenant capacity figures. Backups/DR should align with M13; fleet and rollout dependencies with M14.

### 1.8 Security lens

| Threat | Control/design response | Negative test or review evidence |
|---|---|---|
| Privilege escalation through self-service | Authenticate users, authorize by tenant/entitlement, constrain allowed parameters, audit actions. | Submit a request outside the user's entitlement; it must be denied before resource creation. |
| Compromised template or generated supply chain | Protect template source, review changes, pin dependencies, scan outputs, require provenance/signing controls from M12. | Inject an unapproved image/dependency in a test branch; conformance must fail. |
| Cross-tenant access | Treat isolation as layered: identity, namespace/resource policy, network, storage, and control-plane boundaries. Implementation is Unit 7. | Attempt unauthorized cross-tenant read/write in an isolated test environment; verify denial and audit record. |
| Portal credential/token exposure | Minimize token scope/lifetime, avoid embedding secrets in generated output, protect auth integration. Portal implementation is Unit 4. | Scan generated artifacts/logs for test credentials; review token scope and storage. |
| Malicious or unmaintained plugin | Minimize plugins, review provenance/permissions, track maintenance and upgrade status. Awareness only. | Review plugin inventory, owners, permissions, update status, and removal procedure. |
| Excessive controller/provider privileges | Least privilege, scoped credentials, separated duties, auditable reconciliation. Crossplane implementation is Unit 6. | Review controller permissions and attempt a prohibited operation in a test environment. |
| Insecure defaults copied into every service | Secure templates and policy checks; stage rollout and test negative cases. | Generate a fresh service and deliberately remove a required control; validation must reject it. |

This conceptual local lesson does not prove production security. Production verification requires threat modeling, identity and policy review, runtime tests, supply-chain evidence, auditability, and operational ownership.

### 1.9 Production checklist

- [ ] Target developer groups and workload archetypes are named.
- [ ] User problems are supported by observations/interviews or explicitly marked as hypotheses.
- [ ] Synthetic data is labelled and excluded from claims about real developers.
- [ ] Manual baseline boundaries, timing rules, and evidence are recorded.
- [ ] Platform value proposition and non-goals are documented.
- [ ] Platform team and product-team responsibilities are explicit.
- [ ] One thin end-to-end first slice is selected.
- [ ] Build/adopt/buy decisions include maintenance, security, fit, lock-in, and exit path.
- [ ] Templates and workflows use M01–M15 defaults with traceable verification.
- [ ] Guardrails are preventive, explainable, and tested with negative cases.
- [ ] Developers can inspect generated resources and diagnose failures.
- [ ] A supported escape hatch and its support consequences are documented.
- [ ] Support intake, triage, escalation, office hours, and boundaries are published.
- [ ] Platform SLO ownership and incident communication are defined.
- [ ] Cost ownership, quotas, and measured platform overhead are addressed.
- [ ] Telemetry is transparent, aggregated appropriately, and not used for individual surveillance.
- [ ] Rollout uses canaries/rings and a rollback path for high-blast-radius changes.
- [ ] Roadmap decisions and declined requests have visible rationale.
- [ ] Upgrade, migration, and deprecation are handed off to Unit 9 governance.
- [ ] Real-user validation is planned before production adoption claims are made.
- [ ] M17 integrated-capstone scope is kept separate from this M16 product-design lesson.

### 1.10 Hands-on lab set

All labs use **Plat-Core**: local files, Python standard library, Markdown, and optional local Git. **Start:** no services; open a terminal in the lab directory. **Stop:** no background services exist. Each lab is safe to re-run; retain synthetic artifacts separately from any real organizational data.

| ID / lab | Goal and steps | Expected evidence | Cleanup / stretch |
|---|---|---|---|
| LAB-01 — Manual journey baseline | Fill `artifacts/manual-baseline.md` while completing a representative M01–M15 service path. Record start/end, active/blocked time, steps, retries, and evidence. Repeat only with the same workload and boundary. | Completed baseline worksheet with learner-measured values; no prefilled timings. | Keep the worksheet for the capstone. Stretch: repeat for a second archetype and explain why the runs may not be comparable. |
| LAB-02 — Synthetic friction analysis | Save the CSV and script above. Run `python3 src/analyze_friction.py data/synthetic-friction-log.csv`; run `python3 -m unittest discover -s tests -v`. Manually review the coding scheme and note ambiguity. | Input CSV, deterministic report, passing test output, and a short interpretation note. | Delete only temporary test files (the tests clean these up). Stretch: add a theme and test a tie. |
| LAB-03 — Product definition pack | Create synthetic personas, journey map, problem statements, vision, Now/Next/Later roadmap, PRD, and assumptions register using the templates above. | `personas-and-journey.md`, `roadmap.md`, `platform-prd.md`, `assumptions-register.md`. | Edit/re-run freely. Stretch: conduct actual interviews only in a real authorized setting and keep consent/privacy requirements. |
| LAB-04 — Platform boundary and economics | Build the capability map; write three build/adopt/buy ADRs; inventory manual/target cognitive load; model costs with variables and low/base/high assumptions; apply the eight-case diagnostic to at least five cases. | Capability map, three ADRs, cognitive-load inventory, ROI worksheet, anti-pattern diagnostic. | No infrastructure cleanup required. Stretch: add sensitivity tables and tests for formulas. |
| LAB-05 — Operating model and maturity | Propose team topology, interaction boundaries, RACI, support intake, response targets, office-hours schedule, evidence-based maturity assessment, and 90-day plan. | Team/support plan, RACI, maturity worksheet, 90-day plan. | No services to stop. Stretch: review the plan with real stakeholders when available. |

**Common fidelity caveat:** personas, tickets, cases, prioritization, and organization are synthetic; execution is local; timings depend on the learner's laptop and workflow. The exercises teach methods, not what a real developer population needs. Real product decisions require actual user research. No cloud, paid service, Docker, Kubernetes, Backstage, Crossplane, Argo CD, or live source-control service is required.

#### Additional required exercise specifications

1. **Manual baseline:** use the blank worksheet in Unit 1.3. Preserve measured times, steps, blockers, retries, evidence, and completion status.
2. **Synthetic friction matrix:** use the CSV, coding scheme, frequency × mean severity score, script, and tests in Unit 1.4. Interpret scores as a prompt for investigation, not a decision by themselves.
3. **Personas/journey/problem/vision/roadmap/PRD:** use the templates in Unit 1.4; save the complete artifacts locally.
4. **Capability map and three ADRs:** choose three real capability decisions for your hypothetical platform. For each ADR include context, options, decision, consequences, security, maintenance, lock-in, exit strategy, assumptions, and revisit trigger.
5. **Thinnest viable platform:** specify one first release, its success and guardrail criteria, and at least five explicit non-goals.
6. **Cognitive-load inventory:** count concepts and decisions on manual versus target paths using a consistent counting rule; classify essential/incidental and propose a locally testable target.
7. **ROI model:** implement `Net value = (H × N × C) + D − P`; include units, low/base/high sensitivity, formula tests, and an assumption register. All sample inputs must be **[ILLUSTRATIVE]**.
8. **Anti-pattern diagnostic:** apply symptom → hypothesis → evidence → root cause → fix → prevention to at least five of the eight synthetic cases.
9. **Team topology/support:** include proposed teams, interaction boundaries, RACI, support response targets (not contractual guarantees), escalation, intake, and office-hours schedule. Label all organization/support details synthetic.
10. **Maturity assessment:** assess evidence, not confidence; create a 90-day improvement plan with owners, evidence, and review points.

### 1.11 Self-check questions

1. **A company has a sophisticated portal, but every request still becomes an operations ticket. Is it an IDP?**  
   **Answer:** The portal is a front end; the existence of a portal does not prove that self-service platform capabilities exist. Inspect the workflows, authorization, automation, and fulfillment path.  
   **Why the wrong answer is tempting:** the UI is visible, so it is easy to confuse the interface with the product.

2. **A data scientist needs a notebook workspace. Should the platform force the same microservice template used by inference APIs?**  
   **Answer:** No. Reuse shared identity, policy, telemetry, and cost conventions, but provide an archetype suited to interactive experiments.  
   **Why tempting:** standardization appears easier to govern, but irrelevant ceremony creates workarounds.

3. **A synthetic ticket corpus shows environment setup as the top friction theme. Can the roadmap now prioritize it as a proven user need?**  
   **Answer:** No. It is a practice result from synthetic data. Validate the hypothesis with actual users and workflow observation.  
   **Why tempting:** a sorted score looks objective even when the input is invented.

4. **A platform team wants to hide all Kubernetes resources to reduce cognitive load. What is the risk?**  
   **Answer:** Debuggability and escape paths may disappear. Hide repetitive complexity, not the evidence needed to understand failures.  
   **Why tempting:** fewer visible concepts can look like simplicity, but hidden system behavior becomes operational debt.

5. **A golden path has strong security defaults but no supported exception path. What failure may follow?**  
   **Answer:** Teams with legitimate different needs may fork or bypass the path, reducing visibility and trust. Add a governed escape hatch while retaining mandatory guardrails.  
   **Why tempting:** strict uniformity feels safer, but unsupported workarounds can be less safe.

6. **Should platform adoption be measured by each developer's deployment count?**  
   **Answer:** No. Measure platform journey outcomes and guardrails in aggregate; do not create individual productivity surveillance.  
   **Why tempting:** individual counts are easy to collect but do not explain value, complexity, or quality.

7. **When should a team build its own portal?**  
   **Answer:** Only when discovery/action needs justify the build and operating burden; first compare documentation, templates, CLI/API, and adopted portals.  
   **Why tempting:** a custom portal is visible evidence of platform work, but may add maintenance without removing friction.

8. **A new template version improves defaults but may break existing repositories. What should happen before broad rollout?**  
   **Answer:** Test compatibility and migration, canary with selected teams, communicate changes, provide rollback, and define deprecation support.  
   **Why tempting:** templates look like static files, but their changes can have fleet-wide impact.

### 1.12 Evidence artifacts

Retain the following in the learner's local lab repository:

- `artifacts/manual-baseline.md` — completed measured steps, timings, blockers, retries, and evidence.
- `data/synthetic-friction-log.csv` — clearly labelled synthetic input.
- `src/analyze_friction.py` and `tests/test_analyze_friction.py` — analysis code and deterministic tests.
- `src/roi_model.py` and `tests/test_roi_model.py` — transparent ROI arithmetic and validation tests.
- Analysis output and a short interpretation note identifying limitations.
- `artifacts/personas-and-journey.md` — synthetic personas, journey map, and problem statements.
- `artifacts/platform-prd.md` — complete first-slice PRD.
- `artifacts/roadmap.md` — Now/Next/Later outcome roadmap.
- `artifacts/assumptions-register.md` — assumption, owner, validation method, status.
- Capability map with provided/integrated/left-to-product-team decisions.
- Three ADRs covering build/adopt/buy decisions (`decisions/ADR-001-template-engine.md`, `ADR-002-portal-choice.md`, and `ADR-003-provisioning-boundary.md`).
- Thinnest viable platform proposal, success/guardrail measures, and non-goals.
- `artifacts/cognitive-load-inventory.md` with a counting convention and learner-measured target.
- ROI model, formula tests, sensitivity analysis, and assumption register.
- Anti-pattern diagnostic for at least five synthetic cases.
- `artifacts/team-support-model.md` with team interaction proposal, RACI, intake/support plan, illustrative response targets, escalation, and office-hours schedule.
- Evidence-based maturity self-assessment and 90-day plan.

Use synthetic data only in this exercise. Do not commit secrets, personal information, real interview notes without authorization, or credentials. Keep the learner-measured baseline distinct from synthetic example data.

### 1.13 Common interview and design-review questions

**1. How would you convince developers to adopt an internal platform?**  
Start by identifying a real repeated friction point through interviews and observation. Deliver one end-to-end path that demonstrably removes work while preserving security, reliability, and ownership. Provide documentation, migration help, support, and a feedback loop. Measure the journey and guardrails in aggregate. Adoption is evidence of value, not a mandate or a portal page count.

**2. How do you decide what belongs in the platform, and whether to build, adopt, or buy it?**  
Abstract repeated undifferentiated work and keep domain-specific decisions with product teams. Compare existing open-source or managed capabilities before building infrastructure. Evaluate fit, differentiation, skills, maintenance, security, ecosystem health, lock-in, exit path, and total operating cost. Record assumptions and revisit triggers. A thin first release is preferable until evidence supports breadth.

**3. How do you reduce cognitive load without creating a black box?**  
Remove repeated incidental decisions through documented defaults and automation, but expose generated resources, logs, events, ownership, and failure reasons. Provide supported variation and a governed escape hatch. Compare manual and target journeys using a consistent concept/step inventory; do not claim a universal reduction percentage.

**4. How do you prevent one platform change from creating a fleet-wide incident?**  
Treat templates, policies, APIs, and shared controllers as high-blast-radius dependencies. Use versioning and compatibility tests, negative policy tests, canary tenants, rollout rings, rollback, and change communication. Define platform SLOs and an incident runbook. Verify the generated result as a new user would, not only from the platform team's development environment.

**5. What metrics show that a platform is working, and how do you govern it?**  
Use a defined developer journey: onboarding success, time-to-first-deploy, conformance, failure reasons, support demand, adoption among eligible teams, and upgrade lag. Pair outcome measures with security/reliability/cost guardrails and qualitative feedback. Aggregate and protect telemetry; never rank individual developers. Govern the roadmap with transparent prioritization, support boundaries, version/deprecation policies, and evidence-based review.

### 1.14 Sources and verification notes

#### Scope authority

- `Roadmap(20261103-134456).md` — current supplied repository tree and Stage 2E module context.
- `PROMPT-Platform-Engineering-and-Internal-Developer-Platforms(3).md` — current supplied M16 syllabus requirements, sequence, tooling constraints, and cross-module handoffs.
- `Pasted markdown(20261103-134435).md` — current Unit 1 output contract and detailed completeness requirements.
- Previously generated `01-platform-engineering-principles-and-platform-as-a-product.md` (31 October 2026) — used as the working draft; updated against the current source files rather than treated as an authority over them.

These supplied files are the authority for this lesson's scope. No claim is made that external documentation was live-checked during authoring.

**Neighboring lesson boundaries (relative links):** [Unit 2 — Golden paths](02-golden-paths-templates-and-paved-roads.md), [Unit 3 — Self-service provisioning](03-self-service-infrastructure-and-environment-provisioning.md), [Unit 4 — Developer portal and catalog](04-developer-portals-and-backstage-service-catalog.md), [Unit 5 — Scaffolding](05-scaffolding-and-software-templates.md), [Unit 6 — Crossplane platform APIs](06-platform-apis-with-crossplane-compositions.md), [Unit 7 — Multi-tenancy](07-multi-tenancy-isolation-and-tenant-onboarding.md), [Unit 8 — Platform SLOs and DX](08-platform-slos-adoption-metrics-and-developer-experience.md), and [Unit 9 — Governance and deprecation](09-platform-governance-deprecation-and-versioning.md). The repository tree also confirms the separate M17 folder at `../17-Production-DevOps-Integrated-Capstone/`; this unit does not assume or invent a file inside it.

#### Reference material to consult

- Cloud Native Computing Foundation (CNCF), *Platforms White Paper* — verify current official location, edition, and section wording before citing or applying it.
- CNCF, *Platform Engineering Maturity Model* — verify current official model and definitions.
- Matthew Skelton and Manuel Pais, *Team Topologies* — verify current publisher/author references and exact team/interaction terminology.
- Cognitive-load theory primary/authoritative learning-science references — verify intrinsic, extraneous, and germane terminology and attribution.
- Jobs-to-be-Done (JTBD) references — verify the chosen framing and attribution.
- RICE prioritization references — verify exact formula, scale, and attribution before organizational use.
- Official documentation for any later-unit implementation tool (Backstage, Copier, Cookiecutter, Crossplane, Argo CD, Kubernetes policy engines) should be consulted in the corresponding unit; no version-sensitive API or CLI claim is required for this unit's core labs.

#### `[VERIFY]` register

| Claim or item | Why it matters | Verification method |
|---|---|---|
| Current CNCF Platforms White Paper and Maturity Model wording | Frameworks evolve; stale terminology can mislead. | Locate the current CNCF-hosted documents and record edition/date/sections. |
| Team Topologies team types and interaction modes | Exact terminology and attribution matter. | Consult the current book/publisher or author-maintained reference. |
| “Thinnest viable platform” phrase/attribution | The principle is useful, but attribution is uncertain here. | Verify against the original source before attributing it. |
| Intrinsic/extraneous/germane cognitive-load definitions | Terms have a learning-science history and nuanced usage. | Consult an authoritative cognitive-load theory source. |
| JTBD and RICE framework attribution/formula | Different sources may define variants. | Select and cite a primary/authoritative reference; document the chosen method. |
| Tool versions and APIs for later units | Version-sensitive and outside this unit's core labs. | Check official release documentation at implementation time. |
| Team Topologies interaction-mode wording | Avoid reproducing or misattributing framework language. | Verify the edition and quote/paraphrase only within applicable limits. |

#### Authoring Audit

| Audit category | Status | Evidence / limitation |
|---|---|---|
| A — Scope and structure | PASS | Correct Unit 1 target; headings 1.0–1.14 are present in order; four learning levels are covered. No other file is an output deliverable. |
| B — Content coverage | PASS | L1 definitions/journey/personas/baseline; L2 research and product artifacts; L3 capability map/interfaces/abstractions/economics and funding; L4 governance/privacy/AI risks/eight synthetic cases; ten exercise families are grouped into five labs. Cross-module handoffs and M17 boundary are explicit. |
| C — Labs and code | PASS | Plat-Core only; Python standard library; matching CSV/script/tests plus a separately tested ROI calculator; safe commands; representative output explicitly labelled; blank manual timings; cleanup and fidelity caveats included. The friction analyzer and ROI calculator were extracted from the authored code blocks and executed locally; all 9 unit tests passed in this authoring session. The expected-output examples are labelled representative. |
| D — Evidence, security, and metrics | PASS | Verifiable checklist, threat/control/negative-test table, SRE lens/runbook/cost guidance, assumption-based ROI formula, and explicit rejection of individual surveillance. No industry statistics asserted. |
| E — Accuracy and sources | PASS WITH OPEN VERIFICATION | No fabricated versions or claims of live source review. Framework/tool attribution and version-sensitive items are explicitly `[VERIFY]`; external sources were not live-checked. |
| F — Output and file safety | PASS | One Markdown lesson is delivered. No other repository files were modified. |

**OPEN:** External framework terminology and future tool versions must be verified against current authoritative documentation before production adoption. The friction-analysis and ROI Python artifacts passed the local checks recorded in Audit C; learners should still rerun them in their own WSL2/Linux environment and retain their own test output. Synthetic support targets, RACI assignments, and all illustrative economic inputs must be replaced or validated with real organizational owners/data before use.
