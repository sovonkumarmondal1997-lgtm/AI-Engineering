# DORA Metrics and Engineering Performance Measurement

**Target file:** `Stage 2E — Production DevOps & Platform Engineering/10-Site-Reliability-Engineering-and-Incident-Management/11-dora-metrics-and-engineering-performance-measurement.md`  
**Level:** L1–L4 · **Estimated study time:** 16–24 hours  
**Prerequisites:** M02 CI/CD foundations; M08 GitOps/progressive delivery; M10 Units 1, 4, 5, 7, 9, and 10 (read as needed).  
**Core tools:** Python 3 standard library; CSV/JSON; local synthetic data. `pandas` is optional, not required.  
**Awareness:** DORA Quick Check, Four Keys, engineering-intelligence products, GitHub/GitLab analytics.  
**Last reviewed:** 2026-10-28. **Tool baseline:** Python 3; no version-specific vendor API required.  
**Footprint:** negligible for the core lab; no cluster or external service required.  
**Solo-learner adaptation:** all examples use deterministic synthetic events. A solo simulation proves that definitions and calculations work on the fixture; it does not prove an organizational process, data integration, or team agreement.

> **Source and claim policy.** DORA's current public guide describes five delivery-performance metrics organized as throughput and instability, while older material commonly discusses four metrics. This chapter explicitly preserves both framings instead of presenting one timeless list. All numeric datasets are synthetic and labeled. Metrics are for system learning, not individual ranking.

## Table of contents

1. [Purpose, outcomes, and boundaries](#1-purpose-outcomes-and-boundaries)
2. [L1 — Foundations](#2-l1--foundations)
3. [Metric definitions and formula sheet](#3-metric-definitions-and-formula-sheet)
4. [L2 — Reproducible Python pipeline](#4-l2--reproducible-python-pipeline)
5. [Data quality and deployment-to-incident linkage](#5-data-quality-and-deployment-to-incident-linkage)
6. [L3 — Value stream, experiments, segmentation, and gaming](#6-l3--value-stream-experiments-segmentation-and-gaming)
7. [Privacy, platform teams, and data/ML delivery](#7-privacy-platform-teams-and-dataml-delivery)
8. [L4 — Measurement governance and executive reporting](#8-l4--measurement-governance-and-executive-reporting)
9. [Tool evaluation and organizational cases](#9-tool-evaluation-and-organizational-cases)
10. [Eight hands-on labs](#10-eight-hands-on-labs)
11. [Exercises and answer key](#11-exercises-and-answer-key)
12. [Checklist, glossary, references, and audit](#12-checklist-glossary-references-and-audit)

## 1. Purpose, outcomes, and boundaries

Delivery metrics help teams locate friction, learn whether a delivery-system change improved flow, and balance delivery throughput with production stability. They do **not** directly measure customer value, code quality, decision quality, or individual productivity. A metric is useful only when it has a defined decision, owner, source events, inclusion rules, known blind spots, and a review cadence.

### Measurable learning outcomes

By the end, the learner can:

- **L1:** explain the four historically common DORA metrics and distinguish them from the five-metric framing used in current DORA material.
- **L1:** identify the definitions and source events required before calculating a metric.
- **L2:** run a local Python pipeline that validates synthetic events and computes per-service/per-week delivery measures.
- **L2:** explain how deployment-to-incident matching assumptions change change-failure-rate results.
- **L3:** map a value stream, identify the largest wait stage in supplied data, and propose a testable improvement.
- **L3:** detect metric gaming, confounding, sample-size problems, and bad comparisons.
- **L4:** write a measurement charter, audit event lineage, and present a balanced delivery/reliability/customer scorecard.
- **L4:** reject individual productivity rankings and propose system-level alternatives with a documented rationale.

### Prerequisite check

Before starting, answer: (1) What event marks a production deployment in your M08 lab? (2) How is a service incident recorded? (3) Where is an SLO defined? (4) Can you link a change to a release artifact? If any answer is unknown, use the synthetic schema in this chapter first and treat integration with the local M02/M08 history as a later task.

### Scope boundaries

- M02 Unit 11 owns the initial CI/CD metrics computation approach; this unit adds definition governance, reliability interpretation, anti-gaming, privacy, and organizational use.
- M08 owns progressive delivery and automated abort mechanics. Here, an abort is classified transparently under competing local policies.
- M10 Units 1 and 9 own SLOs and error-budget policies; Units 4–5 own incident definitions and postmortem process; Unit 7 owns toil; Unit 10 owns on-call health.
- M11 owns observability architecture. This chapter consumes exported event data and does not build a telemetry platform.
- M16 owns deeper platform engineering/service-catalog concepts; Stage 5D owns deeper MLOps.

## 2. L1 — Foundations

### 2.1 What DORA measures

DORA (DevOps Research and Assessment) studies the capabilities and outcomes associated with software delivery and organizational performance. Its metric set has evolved:

- The **historically common four** are deployment frequency, lead time for changes, change failure rate (CFR), and time to restore service (often abbreviated MTTR in older descriptions).
- DORA's 2024 publication introduced a fifth measure, **deployment rework rate**, and grouped the metrics into throughput and stability.
- DORA's current public guide describes **five** metrics: change lead time, deployment frequency, failed deployment recovery time (throughput); change fail rate and deployment rework rate (instability).

Source: DORA, “A history of DORA’s software delivery metrics,” Nathen Harvey, 2 January 2026, https://dora.dev/insights/dora-metrics-history/; and “DORA’s software delivery performance metrics,” https://dora.dev/guides/dora-metrics/. These pages were consulted for this chapter. Terminology and questionnaire formulations may continue to evolve; review the live guide before adopting a production measurement charter.

This chapter computes the four commonly cited metrics requested by the syllabus, and also records deployment rework rate as an optional fifth metric where the event data supports it. Do not conflate the historical “time to restore service” phrasing with every current questionnaire's “failed deployment recovery time”; document the local event boundary.

### 2.2 The metrics and their limits

| Metric | What it tells you | What it does not tell you | Typical decision |
|---|---|---|---|
| Deployment frequency | Rate of production changes reaching users | Value, size, safety, or usefulness of changes | Investigate release friction or batch size |
| Lead time for changes | Elapsed time from a defined change event to successful production | Developer effort, customer value, or why time was spent waiting | Map and reduce a proven bottleneck |
| Change failure rate | Fraction of defined production changes associated with user-impacting degradation requiring remediation | Severity, duration, or all forms of poor quality | Improve test/release/rollback controls; inspect linkage quality |
| Time to restore / failed deployment recovery time | Elapsed time from defined failure onset/detection to defined restoration | Full incident cost, recurrence risk, or whether service quality is truly back | Improve detection, mitigation, rollback, and recovery |
| Deployment rework rate (newer framing) | Share of deployments that are unplanned bug-fix work under the selected definition | All technical debt or all corrective work | Find recurring rework sources |

Every number is an operational definition plus event data. The same label can yield different values if one team starts lead time at first commit and another at merge, or if one team counts a canary abort as a failed change and another treats it as a successful safety mechanism.

### 2.3 Worked calculations

Assume a synthetic service had 12 production deployments during a 14-day period. Deployment frequency is \(12/14 = 0.857\) deployments per day, or 6 per week. The rate alone does not establish that the team is effective; check the purpose, batch size, stability, and customer outcome.

Suppose five changes have lead times of 2, 4, 6, 8, and 10 hours. The arithmetic mean is \(30/5=6\) hours; the median is 6 hours. A p90 calculated from only five observations is highly sample-sensitive. Report the sample count and percentile method rather than treating the p90 as precise.

Suppose 2 of 20 changes caused user-impacting production degradation requiring remediation. Under that local definition, CFR \(=2/20=10\%\). If one team later decides to count aborted canaries as failures, the numerator may change even when the production user impact did not. Keep the old and new definitions visible when revising policy.

Suppose a change-related failure was first detected at 10:05 and user-facing service was restored at 10:35. Recovery duration is 30 minutes under those event boundaries. A later permanent root-cause fix at 13:00 is not the same as initial service restoration; record both if the decision needs both.

### 2.4 Throughput and stability are not enemies

Do not repeat “speed and stability always improve together” as a universal law. DORA's research models delivery performance with multiple measures and identifies distinct throughput and instability dimensions in recent work. A local system can improve one while worsening another. Use paired measures and user outcomes to detect that condition. DORA's guide recommends working in small batches as one improvement approach; treat this as a research-informed capability, not proof that every individual small change is safe or that batch size alone caused an outcome. Source: DORA, “Capabilities: Working in small batches,” https://dora.dev/capabilities/working-in-small-batches/.

### 2.5 Definitions are part of the metric

A definition document must specify:

- **Deployment:** production deployment, user-facing release, configuration-only change, feature-flag flip, model release, or data release.
- **Successful deployment:** the required artifact is running in the intended production scope and passes the chosen verification.
- **Failure:** user-impacting degradation attributable to a production change and requiring remediation, under a declared rule.
- **Restore:** the point when agreed user-facing service behavior is back within an acceptable condition; permanent repair may occur later.
- **Lead-time start/end:** e.g., first commit in the change set → successful production deployment. This chapter uses first commit timestamp → successful production timestamp for the synthetic pipeline.
- **Attribution:** the service/team that owns the changed component and the release event.
- **Clock/timezone:** all event timestamps must include UTC offset or be normalized to UTC; period grouping uses UTC unless a charter explicitly says otherwise.
- **Multi-service changes:** decide whether a release counts once per release bundle, once per service, or once per independently user-visible change.
- **Canary aborts:** classify separately from production failures until the policy explicitly says otherwise.

A definition is not “correct” just because it is common. It is useful when consistently applied, audited, and appropriate for the decision.

### 2.6 Historical bands and benchmarking

DORA performance bands are tied to a particular report, population, questionnaire, and year. Do not treat a past “elite/high/medium/low” category as a timeless target, and do not benchmark this laptop simulation against organizational bands. DORA's 2021 report used a five-metric formulation including reliability; later reports have evolved. If a leadership request requires benchmark comparison, cite the exact report year, population, question wording, and limitations. Current public quick-check material may expose different report versions and questions. See https://dora.dev/research/2021/dora-report/ and https://dora.dev/quickcheck/. No numeric benchmark threshold is asserted in this chapter.

### 2.7 Related frameworks

| Framework | Useful lens | Caution |
|---|---|---|
| SPACE | Satisfaction/well-being, Performance, Activity, Communication/collaboration, Efficiency/flow | A multidimensional framework, not one score or permission to surveil |
| DevEx | Developer friction, feedback loops, cognitive load, tool experience | Survey perception alongside behavioral evidence; do not treat one survey as ground truth |
| Flow metrics | Cycle time, WIP, throughput, wait time, flow efficiency | Define work item and boundaries; not identical to DORA lead time |
| SLO/error budget | User-centric reliability and tolerated unreliability | Reliability may worsen while delivery metrics improve |
| Product/customer outcomes | Adoption, task success, correctness, customer impact, business outcomes | Outcomes are affected by product choices and external factors, not delivery alone |

The SPACE paper states that developer productivity cannot be measured by one metric or activity data alone and describes five dimensions: satisfaction and well-being, performance, activity, communication and collaboration, and efficiency and flow. Source: Nicole Forsgren et al., “The SPACE of Developer Productivity: There’s more to it than you think,” ACM Queue 19(1), published 6 March 2021, https://doi.org/10.1145/3454122.3454124. A Microsoft Research publication page is also available at https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/.

**Goodhart's law (practical version):** when a measure becomes a target, people may optimize the measure rather than the outcome. If a deployment quota rewards counts, trivial deploys become attractive. **Campbell's law:** high-stakes use of a quantitative indicator can increase pressure to corrupt the indicator and distort the process it monitors. These are warnings to design incentives carefully, not excuses to stop measuring.

### L1 checkpoint

You should be able to explain why a DORA value without its event definition is incomplete, calculate each metric from a small table, and identify one customer or reliability measure that would keep a delivery scorecard honest.

## 3. Metric definitions and formula sheet

The definitions below are **[ILLUSTRATIVE local-lab definitions]**, not a claim that they are the only official DORA formulas.

| Metric | Local formula | Unit / denominator | Required events |
|---|---|---|---|
| Deployment frequency | Count of eligible successful production deployments / elapsed days | Deployments per day (also report raw count) | Deployment ID, service, environment, status, timestamp |
| Lead time for changes | Production-success timestamp − first-commit timestamp | Hours per eligible change; report median/p75/p90 | Change ID, first commit, production deployment |
| CFR | Eligible changes linked to confirmed remediation-worthy production failure / eligible production changes | Fraction or percentage of eligible changes | Deployment/change ID, incident ID, linkage confidence, remediation evidence |
| Restore time | Restored timestamp − failure start timestamp | Minutes per eligible change-related failure | Incident start/detection, restore timestamp, service, severity |
| Deployment rework rate | Unplanned bug-fix deployments / all eligible deployments | Fraction or percentage | Deployment purpose classification |

Percentiles use the **nearest-rank** method in the standard-library pipeline: sort \(n\) observations, select rank \(\lceil p n \rceil\) using one-based indexing. With small \(n\), percentiles are descriptive, not stable estimates of a population tail.

A zero is not the same as missing. A service with no eligible deployment in a week has a deployment count of zero but its lead time is **not observed**; do not report lead time as zero. A service with missing incident records has unknown CFR, not necessarily zero CFR.

## 4. L2 — Reproducible Python pipeline

### 4.1 Lab file map and synthetic input schema

The following files are **blocks inside this chapter only**. Copy them into a temporary directory if you want to run the lab; this generation task creates only the chapter.

- `data/services.csv`: service and ownership metadata.
- `data/changes.csv`: change ID and first commit timestamp.
- `data/pull_requests.csv`: synthetic PR opened/merged timestamps.
- `data/ci_runs.csv`: synthetic CI start/finish/status events.
- `data/deployments.csv`: deployment/release events.
- `data/incidents.csv`: incident start, detection, restore, severity, and optional deployment reference.
- `metrics-definitions.md`: explicit local definitions.
- `metrics_pipeline.py`: validation and calculation.
- `test_metrics_pipeline.py`: standard-library tests.

All data is synthetic, deterministic, and uses ISO 8601 UTC timestamps (`Z`). Service names and IDs are fictional. The dataset spans two services and several weeks. It includes failed/non-production events and a deliberately missing restore timestamp for validation.

```csv
# File: data/services.csv
service_id,service_name,team,tier
svc-api,Inference API,team-ml-platform,tier-1
svc-etl,Batch ETL,team-data-platform,tier-2
```

```csv
# File: data/changes.csv
change_id,service_id,first_commit_at,change_type
chg-001,svc-api,2026-09-01T08:00:00Z,application
chg-002,svc-api,2026-09-03T09:00:00Z,configuration
chg-003,svc-api,2026-09-08T10:00:00Z,application
chg-004,svc-api,2026-09-15T07:30:00Z,model
chg-005,svc-etl,2026-09-02T06:00:00Z,pipeline
chg-006,svc-etl,2026-09-05T06:00:00Z,pipeline
chg-007,svc-etl,2026-09-11T06:00:00Z,pipeline
chg-008,svc-etl,2026-09-18T06:00:00Z,pipeline
```

```csv
# File: data/pull_requests.csv
pr_id,change_id,opened_at,merged_at
pr-001,chg-001,2026-09-01T08:20:00Z,2026-09-01T11:00:00Z
pr-002,chg-002,2026-09-03T09:10:00Z,2026-09-03T09:45:00Z
pr-003,chg-003,2026-09-08T10:10:00Z,2026-09-08T11:15:00Z
pr-004,chg-004,2026-09-15T07:40:00Z,2026-09-15T08:30:00Z
pr-005,chg-005,2026-09-02T06:10:00Z,2026-09-02T07:20:00Z
pr-006,chg-006,2026-09-05T06:10:00Z,2026-09-05T07:10:00Z
pr-007,chg-007,2026-09-11T06:10:00Z,2026-09-11T07:00:00Z
pr-008,chg-008,2026-09-18T06:10:00Z,2026-09-18T06:45:00Z
```

```csv
# File: data/ci_runs.csv
ci_run_id,change_id,started_at,finished_at,status
ci-001,chg-001,2026-09-01T10:00:00Z,2026-09-01T10:25:00Z,success
ci-002,chg-002,2026-09-03T09:20:00Z,2026-09-03T09:35:00Z,success
ci-003,chg-003,2026-09-08T10:30:00Z,2026-09-08T10:55:00Z,success
ci-004,chg-004,2026-09-15T08:00:00Z,2026-09-15T08:25:00Z,success
ci-005,chg-005,2026-09-02T06:40:00Z,2026-09-02T07:05:00Z,success
ci-006,chg-006,2026-09-05T06:30:00Z,2026-09-05T06:55:00Z,success
ci-007,chg-007,2026-09-11T06:30:00Z,2026-09-11T06:55:00Z,success
ci-008,chg-008,2026-09-18T06:20:00Z,2026-09-18T06:40:00Z,success
```

```csv
# File: data/deployments.csv
deployment_id,change_id,service_id,environment,status,deployed_at,purpose,canary_aborted
dep-001,chg-001,svc-api,production,success,2026-09-01T12:00:00Z,planned,false
dep-002,chg-002,svc-api,production,success,2026-09-03T10:00:00Z,planned,false
dep-003,chg-003,svc-api,production,success,2026-09-08T12:00:00Z,planned,false
dep-004,chg-004,svc-api,production,success,2026-09-15T09:30:00Z,planned,false
dep-005,chg-005,svc-etl,production,success,2026-09-02T08:00:00Z,planned,false
dep-006,chg-006,svc-etl,production,success,2026-09-05T08:00:00Z,planned,false
dep-007,chg-007,svc-etl,staging,success,2026-09-11T07:00:00Z,planned,false
dep-008,chg-007,svc-etl,production,success,2026-09-11T08:30:00Z,planned,false
dep-009,chg-008,svc-etl,production,failed,2026-09-18T07:00:00Z,planned,false
dep-010,chg-008,svc-etl,production,success,2026-09-18T10:00:00Z,hotfix,false
dep-011,chg-003,svc-api,production,aborted,2026-09-08T11:30:00Z,canary,true
```

```csv
# File: data/incidents.csv
incident_id,service_id,severity,started_at,detected_at,restored_at,deployment_id,remediation_required
inc-001,svc-api,SEV2,2026-09-08T12:10:00Z,2026-09-08T12:12:00Z,2026-09-08T12:40:00Z,dep-003,true
inc-002,svc-etl,SEV2,2026-09-18T07:05:00Z,2026-09-18T07:10:00Z,2026-09-18T09:00:00Z,dep-009,true
inc-003,svc-api,SEV3,2026-09-20T08:00:00Z,2026-09-20T08:15:00Z,,unknown,true
```

### 4.2 Definition document

```markdown
<!-- File: metrics-definitions.md -->
# Metrics definitions — version 1.0 (illustrative)
Owner: Engineering Metrics Working Group (fictional)
Effective date: 2026-10-01
Review date: 2027-01-01
Timezone: UTC; source timestamps must carry timezone information.

Eligible deployment: an event in environment=production with status=success and a unique deployment_id.
Aborted canary: excluded from eligible production deployments; tracked separately.
Failed deployment: retained for audit, but does not count as a successful production deployment.
Deployment frequency: eligible deployment events per calendar week and per elapsed day.
Lead time: first_commit_at for a change to the first eligible successful production deployment for that change.
CFR: a change is classified as failed if at least one confirmed incident references a production deployment attempt for that change (status success or failed) and requires remediation. Denominator is distinct changes with a production deployment attempt (success or failed); aborted canaries are excluded. Confirmed deployment_id links are used for the primary estimate; heuristic links are reported separately.
Restore time: incident restored_at minus started_at. Missing restore time is unknown, not zero. This local definition is not interchangeable with every DORA survey question.
Deployment rework rate: share of eligible successful production deployments whose purpose is explicitly `hotfix` or `unplanned_bugfix`. Purpose classification is manually governed.
Multi-service release: count once per service deployment, not once per release bundle.
Owner attribution: service_id from the source event; unknown service is a validation finding.
No personal identifiers or real incident details are included.
Limitations: incomplete event collection, delayed incident declaration, ambiguous causal links, and small samples can materially change results.
```

### 4.3 Complete standard-library pipeline

This implementation deliberately uses Python's standard library so the core lab runs offline. It validates required fields and identifiers, parses timestamps with timezone enforcement, avoids silently converting missing restore times to zero, computes per-service/per-week aggregates, and reports percentiles. It writes a Markdown report to a caller-selected path. It is a teaching baseline, not a production event warehouse.

```python
# File: metrics_pipeline.py
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

REQUIRED = {
    "services": {"service_id", "service_name", "team", "tier"},
    "changes": {"change_id", "service_id", "first_commit_at", "change_type"},
    "pull_requests": {"pr_id", "change_id", "opened_at", "merged_at"},
    "ci_runs": {"ci_run_id", "change_id", "started_at", "finished_at", "status"},
    "deployments": {"deployment_id", "change_id", "service_id", "environment",
                    "status", "deployed_at", "purpose", "canary_aborted"},
    "incidents": {"incident_id", "service_id", "severity", "started_at",
                  "detected_at", "restored_at", "deployment_id", "remediation_required"},
}

def parse_ts(value: str, *, allow_missing: bool = False) -> datetime | None:
    if value is None or not value.strip():
        if allow_missing:
            return None
        raise ValueError("required timestamp is missing")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"timestamp must include timezone: {value!r}")
    return dt.astimezone(timezone.utc)

def read_csv(path: Path, kind: str) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED[kind] - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        rows = list(reader)
    return rows

def unique_ids(rows: list[dict[str, str]], key: str, kind: str, errors: list[str]) -> None:
    counts = Counter(r.get(key, "") for r in rows)
    for value, count in counts.items():
        if not value or count > 1:
            errors.append(f"{kind}: id {value!r} occurs {count} time(s)")

def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(p * len(ordered)))
    return ordered[rank - 1]

def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "UNKNOWN"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)

def load_and_compute(data_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    services = read_csv(data_dir / "services.csv", "services")
    changes = read_csv(data_dir / "changes.csv", "changes")
    pull_requests = read_csv(data_dir / "pull_requests.csv", "pull_requests")
    ci_runs = read_csv(data_dir / "ci_runs.csv", "ci_runs")
    deployments = read_csv(data_dir / "deployments.csv", "deployments")
    incidents = read_csv(data_dir / "incidents.csv", "incidents")

    unique_ids(services, "service_id", "services", errors)
    unique_ids(changes, "change_id", "changes", errors)
    unique_ids(pull_requests, "pr_id", "pull_requests", errors)
    unique_ids(ci_runs, "ci_run_id", "ci_runs", errors)
    unique_ids(deployments, "deployment_id", "deployments", errors)
    unique_ids(incidents, "incident_id", "incidents", errors)
    service_ids = {r["service_id"] for r in services}
    change_by_id = {r["change_id"]: r for r in changes}
    deploy_by_id = {r["deployment_id"]: r for r in deployments}
    service_by_id = {r["service_id"]: r for r in services}

    for row in changes:
        if row["service_id"] not in service_ids:
            errors.append(f"change {row['change_id']}: unknown service {row['service_id']}")
        try:
            parse_ts(row["first_commit_at"])
        except ValueError as exc:
            errors.append(f"change {row['change_id']}: {exc}")

    change_ids = set(change_by_id)
    for row in pull_requests:
        if row["change_id"] not in change_ids:
            errors.append(f"PR {row['pr_id']}: unknown change {row['change_id']}")
        try:
            opened = parse_ts(row["opened_at"])
            merged = parse_ts(row["merged_at"])
            if opened and merged and merged < opened:
                errors.append(f"PR {row['pr_id']}: merged before opened")
        except ValueError as exc:
            errors.append(f"PR {row['pr_id']}: {exc}")
    for row in ci_runs:
        if row["change_id"] not in change_ids:
            errors.append(f"CI run {row['ci_run_id']}: unknown change {row['change_id']}")
        try:
            started = parse_ts(row["started_at"])
            finished = parse_ts(row["finished_at"])
            if started and finished and finished < started:
                errors.append(f"CI run {row['ci_run_id']}: finished before started")
        except ValueError as exc:
            errors.append(f"CI run {row['ci_run_id']}: {exc}")

    for row in deployments:
        if row["service_id"] not in service_ids:
            errors.append(f"deployment {row['deployment_id']}: unknown service")
        if row["change_id"] not in change_by_id:
            errors.append(f"deployment {row['deployment_id']}: unknown change")
        try:
            deployed = parse_ts(row["deployed_at"])
            if row["change_id"] in change_by_id:
                committed = parse_ts(change_by_id[row["change_id"]]["first_commit_at"])
                if deployed and committed and deployed < committed:
                    errors.append(f"deployment {row['deployment_id']}: before first commit")
        except ValueError as exc:
            errors.append(f"deployment {row['deployment_id']}: {exc}")
        if row["environment"] not in {"production", "staging", "development"}:
            warnings.append(f"deployment {row['deployment_id']}: unusual environment")
        if row["status"] not in {"success", "failed", "aborted"}:
            errors.append(f"deployment {row['deployment_id']}: invalid status {row['status']!r}")

    for row in incidents:
        if row["service_id"] not in service_ids:
            errors.append(f"incident {row['incident_id']}: unknown service")
        try:
            started = parse_ts(row["started_at"])
            detected = parse_ts(row["detected_at"])
            restored = parse_ts(row["restored_at"], allow_missing=True)
            if started and detected and detected < started:
                errors.append(f"incident {row['incident_id']}: detection before start")
            if restored and started and restored < started:
                errors.append(f"incident {row['incident_id']}: restore before start")
            if restored and detected and restored < detected:
                warnings.append(f"incident {row['incident_id']}: restore before detection")
            if restored is None:
                warnings.append(f"incident {row['incident_id']}: missing restore time; excluded from restore distribution")
        except ValueError as exc:
            errors.append(f"incident {row['incident_id']}: {exc}")
        dep_id = row["deployment_id"]
        if dep_id and dep_id != "unknown" and dep_id not in deploy_by_id:
            warnings.append(f"incident {row['incident_id']}: unknown deployment link {dep_id}")

    if errors:
        raise ValueError("data validation failed:\n- " + "\n- ".join(errors))

    eligible = [d for d in deployments
                if d["environment"] == "production" and d["status"] == "success"]
    eligible_by_service = Counter(d["service_id"] for d in eligible)
    by_week = defaultdict(int)
    lead_by_service = defaultdict(list)
    lead_by_week = defaultdict(list)
    first_success: dict[str, datetime] = {}
    for d in eligible:
        deployed = parse_ts(d["deployed_at"])
        if deployed is not None:
            iso = deployed.isocalendar()
            by_week[(d["service_id"], f"{iso.year}-W{iso.week:02d}")] += 1
    for d in sorted(eligible, key=lambda x: parse_ts(x["deployed_at"])):
        change = change_by_id[d["change_id"]]
        deployed = parse_ts(d["deployed_at"])
        committed = parse_ts(change["first_commit_at"])
        if deployed is None or committed is None:
            continue
        if d["change_id"] not in first_success:
            first_success[d["change_id"]] = deployed
            hours = (deployed - committed).total_seconds() / 3600
            lead_by_service[d["service_id"]].append(hours)
            iso = deployed.isocalendar()
            lead_by_week[(d["service_id"], f"{iso.year}-W{iso.week:02d}")].append(hours)

    linked_confirmed = set()
    incident_restore_minutes = []
    restore_by_severity = defaultdict(list)
    cfr_eligible_deployments = [d for d in deployments
                                if d["environment"] == "production"
                                and d["status"] in {"success", "failed"}]
    for incident in incidents:
        dep_id = incident["deployment_id"]
        if dep_id in deploy_by_id and incident["remediation_required"].lower() == "true":
            dep = deploy_by_id[dep_id]
            if (dep in cfr_eligible_deployments
                    and dep["service_id"] == incident["service_id"]):
                linked_confirmed.add(dep["change_id"])
        started = parse_ts(incident["started_at"])
        restored = parse_ts(incident["restored_at"], allow_missing=True)
        if started and restored:
            minutes = (restored - started).total_seconds() / 60
            incident_restore_minutes.append(minutes)
            restore_by_severity[incident["severity"]].append(minutes)

    eligible_changes = set(d["change_id"] for d in cfr_eligible_deployments)
    cfr_denominator = len(eligible_changes)
    cfr_numerator = len(linked_confirmed & eligible_changes)
    cfr = cfr_numerator / cfr_denominator if cfr_denominator else None

    purposes = Counter(d["purpose"] for d in eligible)
    rework = sum(1 for d in eligible if d["purpose"] in {"hotfix", "unplanned_bugfix"})
    rework_rate = rework / len(eligible) if eligible else None
    service_metrics = {}
    for service_id, service in service_by_id.items():
        leads = lead_by_service.get(service_id, [])
        service_metrics[service_id] = {
            "name": service["service_name"],
            "team": service["team"],
            "eligible_deployments": eligible_by_service[service_id],
            "lead_time_hours": {
                "n": len(leads), "median": median(leads) if leads else None,
                "p75": percentile(leads, .75), "p90": percentile(leads, .90)
            },
            "weekly_deployments": {
                week: count for (sid, week), count in sorted(by_week.items()) if sid == service_id
            },
            "weekly_lead_time_hours": {
                week: {"n": len(vals), "median": median(vals), "p75": percentile(vals, .75),
                       "p90": percentile(vals, .90)}
                for (sid, week), vals in sorted(lead_by_week.items()) if sid == service_id
            }
        }

    dates = [parse_ts(d["deployed_at"]) for d in eligible]
    elapsed_days = ((max(dates) - min(dates)).total_seconds() / 86400 + 1) if dates else 0
    return {
        "data_quality": {"errors": errors, "warnings": warnings},
        "sample_counts": {
            "services": len(services), "changes": len(changes), "deployments_all": len(deployments),
            "eligible_production_deployments": len(eligible),
            "production_change_attempts_for_cfr": len(cfr_eligible_deployments), "incidents": len(incidents),
            "incidents_with_restore": len(incident_restore_minutes),
            "eligible_changes_for_cfr": cfr_denominator, "confirmed_failed_changes": cfr_numerator
        },
        "overall": {
            "deployment_frequency_per_elapsed_day": len(eligible) / elapsed_days if elapsed_days else None,
            "deployment_frequency_raw_count": len(eligible),
            "lead_time_hours": {
                "n": len([v for values in lead_by_service.values() for v in values]),
                "median": median([v for values in lead_by_service.values() for v in values]) if any(lead_by_service.values()) else None,
                "p75": percentile([v for values in lead_by_service.values() for v in values], .75),
                "p90": percentile([v for values in lead_by_service.values() for v in values], .90)
            },
            "cfr": cfr, "cfr_numerator": cfr_numerator, "cfr_denominator": cfr_denominator,
            "restore_minutes": {
                "n": len(incident_restore_minutes),
                "median": median(incident_restore_minutes) if incident_restore_minutes else None,
                "p75": percentile(incident_restore_minutes, .75),
                "p90": percentile(incident_restore_minutes, .90),
                "by_severity": {sev: {"n": len(vals), "median": median(vals),
                    "p75": percentile(vals, .75), "p90": percentile(vals, .90)}
                    for sev, vals in sorted(restore_by_severity.items())}
            },
            "deployment_rework_rate": rework_rate,
            "rework_deployments": rework,
            "rework_denominator": len(eligible),
            "purpose_counts": dict(purposes)
        },
        "per_service": service_metrics,
        "definitions": {
            "lead_time": "first commit to first successful production deployment for each change",
            "cfr": "confirmed incident deployment_id links requiring remediation / distinct changes with production deployment attempts (success or failed); aborted canaries excluded",
            "restore": "incident started_at to restored_at; missing restore excluded and warned",
            "percentile": "nearest-rank; small samples are unstable",
            "timezone": "timestamps normalized to UTC"
        }
    }

def render_markdown(result: dict[str, Any]) -> str:
    o = result["overall"]
    lines = [
        "# Synthetic delivery metrics report", "",
        "> Example — your values and timings will differ. This report is based only on supplied synthetic fixtures.", "",
        "## Data quality", "",
        f"- Errors: {len(result['data_quality']['errors'])}",
        f"- Warnings: {len(result['data_quality']['warnings'])}",
    ]
    lines.extend(f"- Warning: {w}" for w in result["data_quality"]["warnings"])
    lines += ["", "## Overall metrics", "",
        f"- Eligible production deployments: {result['sample_counts']['eligible_production_deployments']}",
        f"- Deployment frequency: {fmt(o['deployment_frequency_per_elapsed_day'])} per elapsed day (raw count {o['deployment_frequency_raw_count']})",
        f"- Lead time hours: n={o['lead_time_hours']['n']}, median={fmt(o['lead_time_hours']['median'])}, p75={fmt(o['lead_time_hours']['p75'])}, p90={fmt(o['lead_time_hours']['p90'])}",
        f"- CFR: {fmt(o['cfr'] * 100 if o['cfr'] is not None else None)}% ({o['cfr_numerator']}/{o['cfr_denominator']} eligible changes)",
        f"- Restore minutes: n={o['restore_minutes']['n']}, median={fmt(o['restore_minutes']['median'])}, p75={fmt(o['restore_minutes']['p75'])}, p90={fmt(o['restore_minutes']['p90'])}",
        f"- Deployment rework rate: {fmt(o['deployment_rework_rate'] * 100 if o['deployment_rework_rate'] is not None else None)}% ({o['rework_deployments']}/{o['rework_denominator']})",
        "", "## Per service", "", "| Service | Team | Eligible deployments | Lead time n | Median h | p75 h | p90 h |",
        "|---|---|---:|---:|---:|---:|---:|"]
    for sid, m in sorted(result["per_service"].items()):
        l = m["lead_time_hours"]
        lines.append(f"| {m['name']} (`{sid}`) | {m['team']} | {m['eligible_deployments']} | {l['n']} | {fmt(l['median'])} | {fmt(l['p75'])} | {fmt(l['p90'])} |")
    lines += ["", "## Interpretation guardrails", "",
        "- Do not compare teams without checking service mix, event completeness, definitions, and sample size.",
        "- Missing restore time is unknown, not zero.",
        "- CFR is based on confirmed deployment links only; heuristic associations are analyzed separately.",
        "- The synthetic data is too small for organizational benchmark claims.",
        ""]
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser(description="Compute transparent DORA-style metrics from local CSV fixtures.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("metrics-report.md"))
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()
    try:
        result = load_and_compute(args.data_dir)
        report = render_markdown(result)
        args.out.write_text(report, encoding="utf-8")
        if args.json_out:
            args.json_out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Report written: {args.out}")
        print(f"Eligible production deployments: {result['sample_counts']['eligible_production_deployments']}")
        print(f"Confirmed CFR: {fmt(result['overall']['cfr'] * 100 if result['overall']['cfr'] is not None else None)}%")
        print(f"Data-quality warnings: {len(result['data_quality']['warnings'])}")
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
```

### 4.4 Tests for the pipeline

The test module below tests formula helpers and core validation behavior. In a real project, extend it with fixture-level assertions and CI integration. The chapter's final execution report distinguishes tests actually run in this generation environment from tests supplied for learner use.

```python
# File: test_metrics_pipeline.py
import tempfile
import unittest
import shutil
from pathlib import Path
from metrics_pipeline import parse_ts, percentile, load_and_compute

class MetricHelperTests(unittest.TestCase):
    def test_timezone_normalizes_to_utc(self):
        a = parse_ts("2026-09-01T10:00:00+02:00")
        b = parse_ts("2026-09-01T08:00:00Z")
        self.assertEqual(a, b)

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            parse_ts("2026-09-01T08:00:00")

    def test_missing_restore_is_allowed_only_when_explicit(self):
        self.assertIsNone(parse_ts("", allow_missing=True))
        with self.assertRaises(ValueError):
            parse_ts("")

    def test_nearest_rank_percentile(self):
        self.assertEqual(percentile([10, 20, 30, 40], .75), 30)
        self.assertEqual(percentile([10, 20, 30, 40], .90), 40)

    def test_empty_percentile_is_unknown(self):
        self.assertIsNone(percentile([], .9))

    def test_fixture_cfr_and_missing_restore(self):
        result = load_and_compute(Path("data"))
        self.assertEqual(result["overall"]["cfr_numerator"], 2)
        self.assertEqual(result["overall"]["cfr_denominator"], 8)
        self.assertAlmostEqual(result["overall"]["cfr"], 0.25)
        self.assertEqual(result["sample_counts"]["eligible_production_deployments"], 8)
        self.assertTrue(any("missing restore time" in w for w in result["data_quality"]["warnings"]))

    def test_duplicate_deployment_id_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "data"
            shutil.copytree(Path("data"), dest)
            p = dest / "deployments.csv"
            lines = p.read_text(encoding="utf-8").splitlines()
            p.write_text("\n".join(lines + [lines[1]]) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "occurs 2 time"):
                load_and_compute(dest)

    def test_unknown_service_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "data"
            shutil.copytree(Path("data"), dest)
            p = dest / "changes.csv"
            p.write_text(p.read_text(encoding="utf-8").replace("chg-001,svc-api", "chg-001,svc-missing"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown service"):
                load_and_compute(dest)

if __name__ == "__main__":
    unittest.main()
```

**Important data-quality behavior:** the synthetic `inc-003` has no restore timestamp, so the pipeline should report a warning and exclude it from the restore-time distribution. The staging deployment is excluded from production frequency. The aborted canary is excluded from successful production deployment frequency but remains visible in source data. The failed production event is retained for audit but is not counted as a successful deployment.

### 4.5 Deployment-to-incident linker and CFR sensitivity

The main pipeline uses explicit deployment IDs for the primary CFR estimate. It validates PR and CI source event timestamps and change IDs, but does not yet derive a separate PR-stage or CI-stage distribution report from them. In production, links can be ambiguous. Use three declared local policies:

1. **Strict confirmed:** only incidents with an explicit deployment ID, matching service, and remediation evidence.
2. **Window association:** incident begins within 24 hours after a successful production deployment of the same service; this is heuristic, not causal proof.
3. **Canary-abort-inclusive:** count a canary abort as a failed change if it is associated with a production release attempt, even if users were not exposed. This measures rollout friction, not only production impact.

```python
# File: cfr_sensitivity.py
from datetime import datetime, timedelta, timezone

def parse(value):
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("timezone required")
    return dt.astimezone(timezone.utc)

def cfr_sensitivity(deployments, incidents, window_hours=24):
    # Production attempts include successful and failed attempts; aborted canaries are separate.
    attempts = [d for d in deployments if d["environment"] == "production"
                and d["status"] in {"success", "failed"}]
    successful = [d for d in attempts if d["status"] == "success"]
    eligible_changes = {d["change_id"] for d in attempts}
    strict_failed = set()
    window_failed = set()
    deployment_by_id = {d["deployment_id"]: d for d in deployments}
    for incident in incidents:
        if incident.get("remediation_required") != "true":
            continue
        dep_id = incident.get("deployment_id", "")
        if dep_id in deployment_by_id:
            d = deployment_by_id[dep_id]
            if (d in attempts and d["change_id"] in eligible_changes
                    and d["service_id"] == incident["service_id"]):
                strict_failed.add(d["change_id"])
        start = parse(incident["started_at"])
        for d in attempts:
            if d["service_id"] != incident["service_id"]:
                continue
            deployed = parse(d["deployed_at"])
            if timedelta(0) <= start - deployed <= timedelta(hours=window_hours):
                window_failed.add(d["change_id"])
    canary_failed = set(strict_failed)
    for d in deployments:
        if d.get("status") == "aborted" and d.get("canary_aborted") == "true":
            canary_failed.add(d["change_id"])
    denom = len(eligible_changes)
    def rate(s):
        return {"numerator": len(s & eligible_changes), "denominator": denom,
                "rate": len(s & eligible_changes) / denom if denom else None}
    return {
        "strict_confirmed": rate(strict_failed),
        "window_heuristic": rate(window_failed),
        "canary_abort_as_failure": {
            "production_change_attempt_rate": {
                "numerator": len(canary_failed | {d["change_id"] for d in deployments if d.get("status") == "aborted" and d.get("canary_aborted") == "true"}),
                "denominator": len(eligible_changes | {d["change_id"] for d in deployments if d.get("status") == "aborted" and d.get("canary_aborted") == "true"}),
                "rate": (len(canary_failed | {d["change_id"] for d in deployments if d.get("status") == "aborted" and d.get("canary_aborted") == "true"}) / len(eligible_changes | {d["change_id"] for d in deployments if d.get("status") == "aborted" and d.get("canary_aborted") == "true"})) if (eligible_changes | {d["change_id"] for d in deployments if d.get("status") == "aborted" and d.get("canary_aborted") == "true"}) else None
            },
            "note": "Aborted canaries are not production deployment failures; this separate release-attempt view intentionally adds them to both numerator/denominator."
        }
    }
```

This function demonstrates the design but its third result deliberately reports a different policy question. Since the denominator is eligible successful production changes, a canary-abort-only change that never reached production is not in the denominator; the note prevents the output from being misread. If your organization wants a release-attempt failure rate, create a separate denominator of all release attempts and label it separately. Do not quietly mix those populations.

**Matching edge cases to test in a real implementation:** exact time-window boundary, timezone offset conversion, no-match, multiple deployments preceding one incident, one deployment with multiple incidents, duplicate incident IDs, service mismatch, and unknown deployment ID. Confirmed and heuristic links must be shown separately; a 24-hour association is not proof of causation.

```python
# File: test_cfr_sensitivity.py
import unittest
from cfr_sensitivity import cfr_sensitivity

class LinkerTests(unittest.TestCase):
    def setUp(self):
        self.deployments = [
            {"deployment_id":"d1","change_id":"c1","service_id":"s1","environment":"production","status":"success","deployed_at":"2026-01-01T00:00:00Z","canary_aborted":"false"},
            {"deployment_id":"d2","change_id":"c2","service_id":"s1","environment":"production","status":"failed","deployed_at":"2026-01-02T00:00:00Z","canary_aborted":"false"},
            {"deployment_id":"d3","change_id":"c3","service_id":"s1","environment":"production","status":"aborted","deployed_at":"2026-01-03T00:00:00Z","canary_aborted":"true"},
        ]
        self.incidents = [
            {"incident_id":"i1","service_id":"s1","started_at":"2026-01-02T00:30:00Z","deployment_id":"d2","remediation_required":"true"}
        ]

    def test_failed_production_attempt_is_in_denominator(self):
        result = cfr_sensitivity(self.deployments, self.incidents)
        self.assertEqual(result["strict_confirmed"]["denominator"], 2)
        self.assertEqual(result["strict_confirmed"]["numerator"], 1)

    def test_heuristic_link_uses_time_window(self):
        result = cfr_sensitivity(self.deployments, self.incidents, window_hours=1)
        self.assertEqual(result["window_heuristic"]["numerator"], 1)

    def test_naive_timestamp_is_rejected(self):
        self.incidents[0]["started_at"] = "2026-01-02T00:30:00"
        with self.assertRaises(ValueError):
            cfr_sensitivity(self.deployments, self.incidents)

if __name__ == "__main__":
    unittest.main()
```

### 4.6 Example report interpretation

**Example — values are illustrative, not claimed as executed output.** The fixture has 8 eligible successful production deployment events and 8 distinct production change attempts for the CFR denominator (including a failed production attempt but excluding the staging event and aborted canary). Two confirmed deployment-linked incidents require remediation, so the example CFR is 2/8 = 25%. One additional incident has no deployment link and no restore timestamp; it is not counted as a confirmed failure link and is excluded from the restore distribution. The CFR denominator is distinct change IDs, not raw deployment event count. This distinction matters for retries and hotfixes. The exact generated output is whatever the included script prints after the CSV blocks are saved; never copy a hand-calculated number into a report without running it against the data.

## 5. Data quality and deployment-to-incident linkage

### 5.1 Required checks

| Defect | Risk | Control |
|---|---|---|
| Duplicate deployment ID | Frequency and denominator inflated | Uniqueness constraint and source reconciliation |
| Timestamp lacks timezone | Lead/restore duration shifted | Reject naive timestamps; normalize to UTC |
| Production/staging confusion | Invalid frequency and lead-time endpoint | Environment allowlist and deployment source audit |
| Missing restore time | Artificially low restore time if coerced to zero | Keep unknown and report missingness |
| Missing incident declaration | CFR appears better than reality | Reconcile alerts, rollback/hotfix events, and incident records |
| Unlinked deployment | CFR numerator misses failures or falsely links neighbors | Separate confirmed/heuristic linkage and review |
| Multiple services per release | Double count or misattribute | Document unit of analysis and release-to-service mapping |
| Long-lived branch / missing commit link | Lead time biased or uncomputable | Use a defined change identifier and report excluded records |
| Bot / automated change | Human-work interpretation distorted | Declare bot inclusion; report separately where useful |
| Clock skew | Negative or impossible durations | Clock-health check, source-of-truth timestamps, visible rejection |

Do not automatically delete bad rows. Preserve a quarantine copy, emit a finding, assign an owner, and record whether a correction changed a historical result. A silent backfill can make a trend look as if it always existed.

### 5.2 Data contract for learner M02/M08 history

The pipeline accepts the four CSV schemas above. To use local history, export **synthetic or sanitized** events into the same columns. Never paste secrets, production URLs, employee names, or customer data into the exercise. Map M08 GitOps syncs to deployment events only when they represent the intended production boundary. If the system uses one GitOps reconciliation for multiple services, decide whether the metric unit is one release bundle or one service deployment and record the mapping. If there is no reliable incident-to-deployment link, report “unknown association” rather than assigning the nearest deployment as a fact.

### 5.3 Distribution reporting and sample size

Report median, p75, and p90 for lead time and restore time along with `n`. With \(n=4\), p90 is effectively the maximum under nearest-rank; it should not be interpreted as a robust tail estimate. For CFR, always show numerator and denominator (e.g., 2/12), not only a rounded percentage. A change from 1/5 to 2/10 keeps the same percentage but the uncertainty is different. Avoid significance claims from tiny samples.

### L2 checkpoint

You can run the pipeline offline, explain every field in the report, identify missingness and ambiguous incident links, and state what additional event source would most improve confidence.

## 6. L3 — Value stream, experiments, segmentation, and gaming

### 6.1 Worked value-stream map

Synthetic change `chg-101` spends 20 minutes coding, 6 hours waiting for review, 25 minutes in CI, 90 minutes waiting for staging capacity, 15 minutes in approval, 20 minutes deploying, and 45 minutes in verification/bake.

| Stage | Touch time | Wait time | Elapsed contribution |
|---|---:|---:|---:|
| Coding | 20 min | 0 | 20 min |
| Review | 30 min | 360 min | 390 min |
| CI | 25 min | 0 | 25 min |
| Staging queue | 0 | 90 min | 90 min |
| Approval | 5 min | 15 min | 20 min |
| Deploy | 20 min | 0 | 20 min |
| Verify/bake | 45 min | 0 | 45 min |
| **Total** | **145 min** | **465 min** | **610 min (10 h 10 min)** |

The dominant wait stage is review waiting (6 hours), not coding. A plausible hypothesis is that a reviewer ownership queue or oversized PRs dominate lead time. Intervention: assign explicit review ownership and split a recurring oversized change class. Guardrails: review defect escape rate, rework, developer interruption, and SLO attainment. Measure a baseline and an agreed observation window; report counts and distributions, not just means.

### 6.2 Improvement experiment

**Experiment record — synthetic example**

- Question: will a review-owner rotation reduce review wait without increasing escaped defects?
- Baseline: 30 changes; median review wait 5.8 h; p75 11 h; 2 production incidents linked to changes.
- Intervention: named daily review owner and smaller independently releasable changes.
- Prediction: median review wait falls by 20%; no increase in linked production failures or review rework.
- Guardrails: CFR, post-release defects, reviewer interruptions, SLO/error-budget burn, and team survey.
- Result (synthetic): median review wait 4.6 h; p75 9.7 h; 2 linked incidents in 32 changes.
- Interpretation: the median fell 20.7% in this synthetic before/after example, but incident counts and sample sizes are too small to establish causation. Seasonality, change mix, and regression to the mean remain possible explanations.
- Decision: continue collecting data; do not declare success solely from the median.

### 6.3 Segmentation

Segment by service tier, team boundary, change type (application/config/infrastructure/data/model), change size, release method (standard/canary/abort), and cohort period. Segmentation reveals heterogeneity but can create misleading comparisons if cohorts differ in complexity, risk, traffic, or sample size. Document inclusion rules before looking at results to reduce cherry-picking.

### 6.4 Stability and reliability linkage

Keep these distinct:

- **CFR:** share of eligible changes linked to a defined production failure requiring remediation.
- **Incident rate:** number of incidents per time window or per exposure unit; it can include incidents unrelated to a deployment.
- **Rollback rate:** share of deployments followed by rollback under the declared policy.
- **Restore time:** elapsed time between defined failure onset and restoration.
- **Detection time:** elapsed time between failure onset and detection, when both timestamps are reliable.
- **Error-budget burn:** customer-impacting bad events relative to the SLO-allowed budget, per M10 Units 1 and 9.

A canary abort may prevent customer impact but still indicate a release attempt that failed its acceptance criteria. Report both production failure and rollout-abort rates if both decisions matter. Automated aborts are not automatically “good” or “bad”: the abort may be a successful safety control while the candidate change is not promotable.

### 6.5 Anti-gaming simulation

| Gaming behavior | Distorted result | Why it happens | Countermeasure |
|---|---|---|---|
| Trivial/empty deploys to hit frequency quota | Frequency rises without customer value | Reward is attached to count | Define eligible user-facing changes; pair with outcomes and audit samples |
| Skip review or move lead-time start later | Lead time falls while risk may rise | Definition gaming or unsafe shortcuts | Versioned definitions; review quality and escaped-defect guardrails |
| Stop declaring incidents | CFR falls artificially | Incident reporting is penalized | Reconcile incident, alert, rollback, and support evidence; blameless reporting |
| Declare restore before service is healthy | Restore time falls falsely | Premature closure incentive | Define restore by user-facing verification; sample audit |
| Double-count squash merges | Change volume/lead time skewed | Source events not mapped to one change | Stable change IDs and deduplication |
| Count every canary abort as a production failure | CFR discourages safe aborts | Metric mixes rollout attempts with user impact | Separate release-attempt failure from production CFR |
| Compare ETL with mobile app without context | Rankings reflect different work | Cohorts and work units differ | Contextualize mission, criticality, release constraints, sample size |
| DORA improves while customer outcome worsens | Dashboard rewards local optimization | Outcome omitted | Balanced scorecard and customer guardrails |

**Goodhart example:** if “deployments per week” becomes a quota, a team may redeploy the same artifact or split a change into empty releases. The number increases while delivery capability may not improve. **Campbell example:** if CFR determines bonuses, teams may redefine incidents as “support issues” or omit low-severity failures. Countermeasures include metric-definition versioning, source reconciliation, qualitative review, user outcomes, and prohibiting individual performance uses. Residual risk remains: no audit can prove that every hidden incident was declared.

### 6.6 SPACE, DevEx, privacy, and qualitative signals

Use a short anonymous team survey with consistent wording and a documented response window:

1. How often did tooling block or delay delivery this month?
2. How quickly did CI feedback arrive when a change failed?
3. How manageable was cognitive load during review, release, and incident response?
4. Could you safely release a small change and detect whether it worked?
5. What recurring wait or handoff should be removed?
6. What important context does the dashboard omit?

Report aggregate results only when the group is large enough to reduce re-identification risk; a small team can be identifiable even without names. Explain who sees the data, retention, purpose, and prohibited use. Do not combine survey responses with individual commit counts to infer a person's performance.

### 6.7 Platform topology and internal customers

A platform team may improve the lead time of many service teams by providing self-service deployment, paved paths, shared libraries, and better templates. But platform deployment frequency can rise while consuming consumer-team migration time. Measure platform outcomes through consumer task success, time-to-first-production, failed onboarding, support tickets, reliability, and qualitative feedback. This is a handoff to M16: the chapter provides measurement principles, not a service-catalog implementation.

### 6.8 Data/ML delivery adaptations

| Domain | Deployment / release unit | Failure | Lead-time start/end | Restore definition |
|---|---|---|---|---|
| Online inference API | Version/config promoted to serving traffic | User-impacting availability, latency, or correctness regression | Change first commit → verified production serving | User-facing SLI returns to defined acceptable state |
| Batch ETL | Pipeline code/config release or scheduled data release; track both separately | Freshness, completeness, correctness, or duration breach | Change commit → first successful production run, or approval → data publication (separate metrics) | Correct/fresh data restored or backfill/reprocess completed; report each milestone |
| Streaming consumer | Consumer version/config release | Lag, loss, duplicate processing, freshness/correctness regression | Change commit → production consumer verified | Lag and correctness return to acceptable state; backlog drained may be a later milestone |
| Model serving | Model artifact/version promoted to traffic | Latency, availability, quality, safety, or drift-related regression | Model approval/registration → production traffic enabled; code lead time reported separately | Previous model restored or serving quality meets explicit acceptance criteria |
| Feature store/database | Schema/index/config/migration release | Availability, stale feature, incorrect schema/value, or latency regression | Change recorded → verified production use | Queries and dependent workflows meet agreed correctness/latency targets |
| Retraining/reprocessing | Job definition or model/data artifact release | Bad data/model, missed schedule, incomplete output | Approved run/commit → validated output published | Correct output is available and downstream consumers validated |

For data and ML systems, application availability can be healthy while data is stale or model quality is poor. Add domain SLIs and customer outcomes. Do not assume “service restored” means “data corrected” or “model quality recovered.”

### L3 checkpoint

You can identify the actual bottleneck from stage data, propose an intervention with guardrails, and explain why metric improvements are not causal proof or a substitute for user outcomes.

## 7. Privacy, platform teams, and data/ML delivery

### 7.1 Measurement principles

1. **Purpose limitation:** state the decision before collecting the data.
2. **Data minimization:** collect event fields needed to compute the metric; avoid developer-level activity telemetry.
3. **Aggregation:** default to service/team/time-cohort summaries.
4. **Transparency:** make definitions, access, retention, and prohibited uses visible.
5. **Access control:** limit raw event access to roles that need to debug data quality.
6. **Retention:** define a schedule and delete or aggregate raw data when no longer needed.
7. **Correction and audit:** retain versioned definitions and an audit trail for historical backfills.
8. **No individual ranking:** do not use DORA, raw commits, lines of code, PR counts, keyboard activity, or on-call history as a standalone employee productivity score or direct bonus input.

### 7.2 Design trade-offs

| Option | Benefit | Cost/risk | Choose when |
|---|---|---|---|
| CSV/Python pipeline | Transparent, low-cost, easy to inspect | Manual integration and maintenance | Learning, small portfolio, first charter |
| Open-source reference pipeline | Faster initial integration | Maintenance and schema fit need review | Team has owners for updates and audit |
| Commercial engineering-intelligence tool | May provide integrations and workflow UI | Cost, lock-in, opaque definitions, privacy review | Benefits exceed governance and integration costs |
| Executive-only dashboard | Easier communication | Can hide data quality and nuance | Paired with an inspectable detailed report and review ritual |
| Team-level scorecard | Supports learning and system improvement | Can still encourage gaming | Definitions are transparent and no individual rankings are produced |

## 8. L4 — Measurement governance and executive reporting

### 8.1 Sample measurement charter

```markdown
<!-- File: metrics-charter.md -->
# Engineering delivery and reliability measurement charter
Version: 1.0 [ILLUSTRATIVE] | Owner: Engineering Systems Lead | Review: quarterly

Purpose:
Use delivery and reliability evidence to identify system constraints, improve customer outcomes, and evaluate engineering-system changes.

Decisions supported:
- Which value-stream bottleneck should be improved?
- Did an intervention improve flow without harming reliability or customer outcomes?
- Are event data and metric definitions trustworthy enough to inform investment?

In scope:
Named production services with event completeness reviewed each reporting period.
Excluded:
Services without reliable ownership, production boundaries, or enough event quality; exclusions must be listed rather than silently omitted.

Definitions:
Metric names, formula, event boundary, denominator, time zone, inclusion/exclusion, attribution, percentile method, and owner are version controlled. Definition changes require a before/after recalculation where possible.

Sources and lineage:
Deployment, change, incident, restore, SLO, toil, on-call, and customer outcome sources are listed with refresh cadence and data-quality owner.

Privacy:
Aggregate by service/team/cohort. Minimize raw developer-level data. Restrict access, define retention, document corrections, and disclose use to affected teams.

Prohibited uses:
No individual rankings, surveillance, direct compensation decisions, or performance ratings based on these metrics.

Anti-gaming:
Quarterly source reconciliation; inspect denominator changes; audit a sample of deployment and incident links; pair throughput with stability and customer outcomes.

Review:
Weekly working review of bottlenecks; monthly reliability/delivery scorecard; quarterly charter and privacy review.

Disputes:
Service owner files a definition/data-quality issue. Metrics owner records the issue, impact, resolution, and whether historical results changed. Unresolved high-impact disputes are marked unknown or provisional.

Sunset/revision:
Retire a metric if it no longer informs a decision, has persistent unfixable data quality, creates harmful incentives, or is superseded by a more appropriate measure.

Approval:
Product, engineering, SRE/reliability, and privacy/security representatives; fictional roles for this lab.
```

### 8.2 Review rituals

**Weekly 30-minute flow review:** inspect the current bottleneck, sample size, wait-stage distribution, guardrails, and one improvement experiment. Ask what evidence would change the hypothesis.

**Monthly delivery/reliability review:** review DORA-style metrics alongside SLO attainment/error budget, incident severity and restore, toil, on-call health, and customer outcomes. Review definition/data-quality changes first.

**Quarterly governance review:** review privacy, access, retention, incentive effects, excluded services, data-source coverage, and whether the metric still supports a decision.

Experiment log:

| Field | Example |
|---|---|
| Question | Does review ownership reduce waiting? |
| Baseline/cohort | Last 4 weeks; 30 eligible changes |
| Intervention | Named review owner |
| Predicted effect | Reduce median review wait |
| Guardrails | CFR, SLO, review rework, developer interruption |
| Result | Record measured values and sample counts |
| Caveats | Service mix, seasonality, small sample |
| Decision | Continue, adjust, roll back, or collect more evidence |

Avoid p-hacking (trying many analyses until one looks positive), cherry-picking windows, regression-to-the-mean mistakes, and multiple comparisons. Predefine the main outcome and guardrails. If several metrics are explored, label the analysis exploratory.

### 8.3 Responsible comparisons

Before comparing services or teams, record:

- Mission and customer journey.
- Criticality and reliability requirements.
- Application, data, model, or platform work type.
- Architecture and dependency constraints.
- Release process and change-size distribution.
- Regulatory or approval constraints.
- Data completeness and sample size.
- Period, seasonality, and service mix.
- Metric definition version.

Normalization helps but does not eliminate confounding. Prefer a team's trajectory under stable definitions and shared learning over a league table.

### 8.4 Executive scorecard (synthetic)

| Dimension | Synthetic observation | Interpretation / caveat | Next action |
|---|---|---|---|
| Deployment frequency | 8 → 12/week | Throughput increased; verify eligible events | Audit event definition |
| Median lead time | 2.4 → 1.6 days | Flow may have improved; inspect distribution | Review largest wait stage |
| CFR | 5% → 8% | Stability worsened under local confirmed-link rule | Review linked changes and missing incident records |
| Restore median | 35 → 55 min | Recovery worsened; small `n=4` | Review mitigation path and detection |
| SLO attainment | 99.95% → 99.70% | User-facing reliability declined [ILLUSTRATIVE] | Apply Unit 9 policy |
| Customer task success | 96% → 91% | Delivery speed did not produce better outcome | Investigate product/quality hypothesis |
| Toil | 6 → 5 h/week | Slight decrease; estimation uncertainty | Validate sampling method |
| On-call load | 3 → 7 night pages | Human cost increased; aggregate only | Reduce noisy pages and review coverage |
| Data quality | 2 missing deployment links | CFR uncertain | Assign data owner and re-run |

The correct narrative is not “performance improved because deployment frequency rose.” The scorecard shows throughput improved while stability, SLO attainment, customer task success, restore time, and on-call burden worsened. Investigate and mitigate rather than declaring success.

### 8.5 Leadership asks for individual rankings

**Scenario:** a director asks for a ranking of developers by lead time and deployment count.

Recommended response:
1. Explain that these measures reflect a delivery system and event definitions, not an individual's contribution or task difficulty.
2. Offer service-level trends, bottleneck analysis, work-type segmentation, peer-reviewed qualitative evidence, and an improvement experiment.
3. Document the request, the charter's prohibited-use clause, and the agreed alternative.
4. If leadership persists in a prohibited or privacy-unsafe use, escalate through the organization's governance/privacy route and restrict access as policy permits.

Do not quietly create a hidden ranking. If an organization chooses a different policy, it must undergo explicit privacy, ethics, and validity review; this chapter does not endorse individual ranking.

### 8.6 Metrics hygiene audit

Sample audit report (synthetic):

| Finding | Impact | Owner | Correction | Evidence to close |
|---|---|---|---|---|
| Duplicate `deployment_id` in export | Frequency inflated | CI/CD data owner | Deduplicate upstream and reject duplicates | Reconciled export and passing test |
| Staging event classified as production | Frequency and lead time biased | Release platform owner | Fix environment mapping | Source record and rerun diff |
| Incident has no restore timestamp | Restore distribution may be biased | Incident-data owner | Recover verified timestamp or leave unknown | Source evidence and audit record |
| Definition changed from merge to first commit | Trend discontinuity | Metrics charter owner | Version definition and recalculate historical series where possible | Versioned charter and change note |
| Unlinked incident near multiple deploys | CFR ambiguous | Service owner + SRE | Review change timeline; preserve uncertain label if unresolved | Link decision record |

Audit workflow: sample source events → compare IDs and timestamps → reconcile counts → inspect missingness and exclusions → review linkage → document correction → rerun metrics → diff outputs → record owner and closure evidence. Never silently rewrite historical numbers.

### 8.7 Integrated reliability + delivery scorecard template

| Dimension | Metric | Definition/version | Owner | Trend/sample | Confidence/data quality | Next action |
|---|---|---|---|---|---|---|
| Delivery | Deployment frequency |  |  |  |  |  |
| Delivery | Lead time median/p75/p90 |  |  |  |  |  |
| Stability | CFR + numerator/denominator |  |  |  |  |  |
| Stability | Restore-time distribution |  |  |  |  |  |
| Reliability | SLO attainment/error budget | M10 Units 1/9 |  |  |  |  |
| Incidents | Severity, detection, restore, action closure | M10 Units 4/5 |  |  |  |  |
| Operations | Toil hours reclaimed and method | M10 Unit 7 |  |  |  |  |
| Human health | Aggregate on-call load and off-hours interruptions | M10 Unit 10 |  |  |  |  |
| Customer | Task success, freshness, correctness, impact | Domain-defined |  |  |  |  |
| Leading indicators | Review wait, CI duration, rollout verification |  |  |  |  |  |
| Data quality | Missing/duplicate/ambiguous event counts |  |  |  |  |  |

## 9. Tool evaluation and organizational cases

### 9.1 Vendor-neutral evaluation matrix

| Criterion | Questions to ask | Evidence required |
|---|---|---|
| Definition transparency | Can we inspect formulas, denominators, exclusions, and version changes? | Exportable metric specification |
| Provenance | Can a displayed value trace to source events? | Event-level audit trail |
| Multi-service release handling | How are bundled releases and service ownership represented? | Test fixture results |
| Incident linkage | Are confirmed and heuristic links distinguished? | Link rules and correction workflow |
| Data quality | Are missingness, duplicates, backfills, and clock anomalies visible? | Validation report |
| Privacy | Can access be restricted and data aggregated? | Security/privacy documentation |
| Gaming resistance | Are metrics paired with stability and customer outcomes? | Governance controls |
| Integrations/maintenance | What breaks when source schemas change? | Ownership and support plan |
| Cost/lock-in | What is total cost and can data be exported? | Contract and export test |
| Fit | Does it handle platform, data, regulated, and ML delivery units? | Representative proof of concept |

**Four Keys status (verified at review):** the `dora-team/fourkeys` GitHub repository identifies itself as archived by its owner on 23 January 2024 and says it is not currently maintained. Source: https://github.com/dora-team/fourkeys. Treat it as a historical reference implementation, not a maintained default. The prompt's older `GoogleCloudPlatform/fourkeys` path should be checked for redirects/forks before use; do not assume it implements the current five-metric DORA framing or your local definitions.

**GitLab example (verified from current official documentation):** GitLab's DORA metrics docs describe four metrics and identify the DORA metrics feature/API as available for GitLab.com, Self-Managed, and Dedicated under the Ultimate tier. Its documented calculation boundaries are product-specific and can differ from this chapter's local policy. Sources: https://docs.gitlab.com/user/analytics/dora_metrics/ and https://docs.gitlab.com/api/dora/metrics/. Recheck the current edition/tier and calculations before purchase or adoption.

**GitHub:** this chapter makes no claim about current GitHub-native DORA metric availability or tier because an authoritative current documentation source was not verified during this review. **[VERIFY before making a product comparison]**.

**Commercial tooling:** products such as LinearB, Sleuth, Jellyfish, Faros, Swarmia, and platform-native analytics may offer engineering metrics features, but product scope, availability, pricing, privacy, and exact definitions are version-sensitive. **[VERIFY vendor claims against current official documentation]**. This chapter does not assert feature parity or recommend a vendor.

### 9.2 Seven organizational cases

All details below are **[ILLUSTRATIVE synthetic scenarios]**, not named-company case studies.

#### Case 1 — Deployment-frequency target triples empty deployments

- **Evidence/timeline:** dashboard target is announced; within a month, deployment count triples while artifact hashes and user-visible changes remain unchanged.
- **Diagnosis:** count became a target; eligibility rules did not require meaningful production change.
- **Immediate correction:** pause target-based reward, inspect event sample, publish the definition change and restated trend.
- **Durable control:** pair frequency with lead time, stability, customer outcome, and source audit.
- **Owner / completion evidence:** metrics charter owner; event reconciliation plus approved policy.
- **Metric to watch:** valid deployments, rework, customer outcomes.
- **Residual risk:** teams may split meaningful work into unnecessarily small releases; evaluate operational cost and user value.

#### Case 2 — Teams stop declaring incidents to improve CFR

- **Evidence/timeline:** CFR falls, but rollback and support signals remain flat; postmortem volume drops.
- **Diagnosis:** reporting is penalized or incident definition is inconsistent.
- **Immediate correction:** suspend performance interpretation; reconcile alerts, rollback/hotfix events, and incidents.
- **Durable control:** blameless incident declaration, explicit ownership, audit sampling, no direct individual bonuses from CFR.
- **Owner / evidence:** SRE and incident-data owner; sampled reconciliation closed.
- **Metric to watch:** unlinked rollback/hotfix events and customer-impact reports.
- **Residual risk:** not every customer impact is observable in available logs.

#### Case 3 — Individual dashboard ranking damages trust

- **Evidence/timeline:** leader shares a named ranking; developers optimize commit counts and avoid difficult work.
- **Diagnosis:** system metrics misused as individual productivity proxies.
- **Immediate correction:** remove ranking access and communicate correction.
- **Durable control:** charter prohibition, privacy/access review, team-level metrics, transparent purpose limitation.
- **Owner / evidence:** engineering leader/privacy partner; dashboard access and charter audit.
- **Metric to watch:** trust survey and whether reviews focus on system constraints.
- **Residual risk:** informal ranking may continue through screenshots or private spreadsheets.

#### Case 4 — Pipeline double-counts squash merges

- **Evidence/timeline:** merge count rises after source integration; production deploy count does not.
- **Diagnosis:** one change represented by several commit/PR records.
- **Immediate correction:** stop publishing affected metric as trusted; deduplicate by documented change identity.
- **Durable control:** data contract, uniqueness tests, source-to-report reconciliation.
- **Owner / evidence:** data pipeline owner; test fixture and reconciliation report.
- **Metric to watch:** duplicate and unmatched ID rates.
- **Residual risk:** squash/rebase workflows can still lose traceability if identifiers are not preserved.

#### Case 5 — Canary aborts count as production failures

- **Evidence/timeline:** CFR rises after automated aborts are included; teams become reluctant to use canaries.
- **Diagnosis:** rollout-attempt failures and customer-impacting production failures are conflated.
- **Immediate correction:** split production CFR and canary-abort rate; explain the historical definition.
- **Durable control:** versioned metric definitions and safety-mechanism review.
- **Owner / evidence:** progressive-delivery owner; tests show each event class.
- **Metric to watch:** user-impacting failures, abort rate, canary detection quality.
- **Residual risk:** teams may understate candidate defects if only customer impact is tracked.

#### Case 6 — Data pipeline compared with mobile app

- **Evidence/timeline:** leadership compares raw deployment frequency; ETL team appears slower.
- **Diagnosis:** different release units, validation windows, and risk constraints.
- **Immediate correction:** withdraw the league table and contextualize the cohorts.
- **Durable control:** service-specific definitions and trajectory-based reviews.
- **Owner / evidence:** portfolio metrics owner; comparison template completed.
- **Metric to watch:** pipeline freshness/correctness, lead-time distribution, customer outcomes.
- **Residual risk:** contextualization can be used to excuse avoidable delays; require evidence and hypotheses.

#### Case 7 — Metrics improve while customers get worse

- **Evidence/timeline:** deployment frequency rises and lead time falls; inference correctness and customer task success decline.
- **Diagnosis:** scorecard omitted outcome and reliability guardrails.
- **Immediate correction:** stop declaring the initiative successful; investigate quality regressions and apply relevant SLO/error-budget policy.
- **Durable control:** integrated scorecard, canary guardrails, incident linkage, product feedback.
- **Owner / evidence:** service owner + product owner; user-outcome recovery and post-change review.
- **Metric to watch:** correctness SLI, customer task success, CFR, error budget.
- **Residual risk:** customer outcomes may lag the release and be confounded by unrelated product changes.

### L4 checkpoint

You can defend a measurement charter, explain why an executive ranking is invalid, audit metric lineage, and recommend a next investment using delivery, reliability, toil, on-call, and customer evidence together.

## 10. Eight hands-on labs

**Safety for every lab:** work only in a disposable local directory with synthetic data. Do not use production exports, real incident data, employee records, credentials, or private URLs. No SaaS is required.

### Lab 1 — L1 metric literacy

- **Goal:** compute the four metrics manually and expose missing definitions.
- **Prerequisites/time/footprint:** this chapter; 25 minutes; negligible.
- **Steps:** use the worked calculations in Section 2.3. Create a table with deployment timestamp, commit timestamp, incident link, restore timestamp, and status.
- **Expected evidence:** calculation sheet containing numerator, denominator, event boundaries, and limitations.
- **Interpretation:** ask whether an aborted canary counts as production deployment and why.
- **Failure injection:** remove a restore timestamp; mark the metric unknown.
- **Cleanup:** discard the local worksheet if no longer needed.
- **Troubleshooting:** if calculations differ, check eligible environment, distinct change vs deployment event, and UTC normalization.

### Lab 2 — L2 build the pipeline

- **Goal:** run the standard-library pipeline.
- **Prerequisites:** Python 3; save the four CSV blocks plus `metrics_pipeline.py` in the indicated layout.
- **Setup:** work from a temporary folder, e.g. `mkdir dora-lab && cd dora-lab`; copy code blocks into their named files and data blocks into `data/`.
- **Command:** `python metrics_pipeline.py --data-dir data --out metrics-report.md --json-out metrics-report.json`
- **Expected output (example; actual values depend on saved fixture):** `Report written: metrics-report.md`, a count of eligible production deployments, a confirmed CFR value, and a data-quality warning count.
- **Verification:** open the Markdown report; verify the missing restore warning and per-service counts.
- **Failure injection:** rename a required CSV column; expect exit code 2 with a clear validation error.
- **Cleanup:** delete only the disposable `dora-lab` directory.
- **Safety/privacy:** no network access; no real events.
- **Evidence:** report, JSON, command output, and one paragraph explaining the assumptions.
- **Troubleshooting:** ensure `# File:` teaching comments are not included as actual CSV rows; save CSV data without the filename comment line.

### Lab 3 — L2 data-quality detective

- **Goal:** detect duplicate deployment IDs, naive timestamps, missing restore time, and a staging event misclassified as production.
- **Steps:** duplicate a deployment row; remove `Z` from one timestamp; alter the environment value; remove `restored_at`.
- **Expected behavior:** duplicate ID or naive timestamp causes a visible validation error; missing restore is a warning and is excluded from restore distribution; staging rows are excluded from production counts.
- **Verification:** restore each defect one at a time and compare report output.
- **Cleanup:** revert the synthetic fixture.
- **Troubleshooting:** the example pipeline fails on duplicate IDs and naive timestamps, while missing restore is deliberately allowed. A staging event is excluded by the eligibility rule; an unexpected environment value emits a warning.
- **Evidence:** defect → detection → correction table.

### Lab 4 — L2/L3 deployment-to-incident linker

- **Goal:** compare strict and heuristic incident links.
- **Steps:** copy `cfr_sensitivity.py`; create tiny in-memory `deployments` and `incidents` lists from Section 4.1; call `cfr_sensitivity(deployments, incidents)`.
- **Expected result:** three policy-labelled result objects; strict links are fewer or equal to heuristic links in many cases, but not guaranteed if the policies differ.
- **Failure injection:** incident occurs exactly at 24-hour boundary; test timezone offsets; give one incident two nearby deployments.
- **Verification:** record confirmed versus heuristic links separately.
- **Cleanup:** delete local fixture.
- **Evidence:** sensitivity table and an explanation of why time proximity is not causality.
- **Troubleshooting:** if a canary abort is not in eligible production denominator, do not force it into CFR; define a separate release-attempt failure rate if needed.

### Lab 5 — L3 lead-time decomposition

- **Goal:** find the dominant wait stage.
- **Steps:** use Section 6.1 table; calculate total touch time and total wait time.
- **Expected calculation:** touch time 145 minutes; wait time 465 minutes; elapsed total 610 minutes. Review waiting is the largest single wait at 360 minutes.
- **Verification:** propose one intervention, one prediction, and at least two guardrails.
- **Failure injection:** assume CI duration is cut in half; calculate the maximum elapsed-time reduction (12.5 minutes) and explain why this is smaller than fixing review wait.
- **Cleanup:** none.
- **Evidence:** value-stream map and experiment record.
- **Troubleshooting:** separate touch time from elapsed wait; don't call all lead time “coding time.”

### Lab 6 — L3 gaming and guardrails

- **Goal:** identify distortions and design a balanced countermeasure.
- **Steps:** choose three rows from Section 6.5; construct before/after values; add a paired stability or customer outcome measure.
- **Expected result:** each gaming case has an incentive, a distortion, and at least one control plus residual risk.
- **Failure injection:** assume CFR improves because no incidents are declared; identify which independent source could reveal the mismatch.
- **Cleanup:** none.
- **Evidence:** anti-gaming register.
- **Troubleshooting:** controls reduce risk but cannot prove no hidden gaming occurred.

### Lab 7 — L3 reliability/delivery scorecard

- **Goal:** integrate delivery, SLO/error budget, incidents, toil, on-call health, and customer outcomes.
- **Steps:** fill the template in Section 8.7 with synthetic values; include a case where delivery speeds up but customer outcome worsens.
- **Expected result:** recommendation prioritizes user impact and reliability rather than a single delivery metric.
- **Verification:** every metric has owner, definition, sample/trend, data-quality caveat, and next action.
- **Cleanup:** remove synthetic names if adapting the template.
- **Evidence:** one-page scorecard and narrative.
- **Troubleshooting:** if a metric has no denominator or source, mark it unknown/provisional.

### Lab 8 — L4 charter and executive review

- **Goal:** write a charter and defend against individual rankings.
- **Steps:** copy Section 8.1 charter; conduct a solo role-play with roles of engineering director, SRE, product lead, and privacy partner. Write the requested decision and final agreement.
- **Expected result:** purpose, owners, definitions, access, retention, anti-gaming audit, prohibited uses, and review cadence are explicit.
- **Failure injection:** director asks for a named developer ranking; propose a system-level alternative and document escalation if needed.
- **Cleanup:** store only synthetic evidence.
- **Evidence:** charter, meeting notes, audit checklist, decision record.
- **Troubleshooting:** a solo role-play is not proof of real stakeholder agreement.

### Optional Lab 9 — L3/L4 data/ML adaptation

- **Goal:** define separate code deployment and data/model release events.
- **Steps:** choose ETL or model serving; define deployment, failure, lead-time start/end, and restore; include data freshness/correctness or model-quality SLI.
- **Expected result:** a local metric definition avoids conflating service availability with data/model correctness.
- **Cleanup:** no external systems required.
- **Evidence:** one-page domain definition and a sample event table.

## 11. Exercises and answer key

### E01 — L1 terminology (10 min)

**Prompt:** Is deployment frequency a measure of customer value? What must accompany the number?  
**Model answer:** No. It counts eligible production deployment events over a defined period. Pair it with stability, user outcomes, and a transparent definition/source.  
**Reasoning:** release count can rise without meaningful change.  
**Common wrong answer:** “More deployments always means more productivity.” This ignores change size, safety, value, and gaming.

### E02 — L1 lead-time boundary (10 min)

**Prompt:** A change's first commit is Monday 09:00 UTC and it reaches verified production Tuesday 15:00 UTC. Calculate lead time. What changes if the organization starts at merge Tuesday 09:00?  
**Model answer:** 30 hours from first commit; 6 hours from merge. Both can be valid local definitions if documented, but trends cannot be compared without accounting for the definition change.  
**Common wrong answer:** report “one day” without timestamps or boundary.

### E03 — L1 CFR arithmetic (10 min)

**Prompt:** 3 of 25 eligible changes required remediation after user-impacting production degradation.  
**Model answer:** \(3/25=12\%\), with numerator 3 and denominator 25.  
**Reasoning:** display the counts so small samples are visible.  
**Common wrong answer:** divide by total incidents; incidents and changes are different units.

### E04 — L1 restore definition (10 min)

**Prompt:** failure starts 11:00, detected 11:04, service restored 11:32, permanent fix merged 14:00.  
**Model answer:** restore time is 32 minutes under the stated start-to-restore definition. Permanent repair time is a separate milestone.  
**Common wrong answer:** use 3 hours because the permanent fix came later without saying that the metric changed.

### E05 — L2 duplicate deployment (15 min)

**Prompt:** the export contains the same deployment ID twice. What should happen?  
**Model answer:** validation should fail or quarantine the duplicate, show the ID, and prevent it from silently inflating frequency/denominators.  
**Common wrong answer:** drop one row silently. That hides a source-system defect and destroys auditability.

### E06 — L2 missing restore (10 min)

**Prompt:** an incident has no `restored_at`.  
**Model answer:** exclude it from the restore-time distribution and report a missing-data warning; do not assign zero or invent a timestamp.  
**Common wrong answer:** treat missing as zero, which falsely improves recovery time.

### E07 — L2 incident linkage (15 min)

**Prompt:** two production deployments of the same service precede an incident by 3 and 8 hours; no deployment ID is linked.  
**Model answer:** mark the association ambiguous; the 24-hour window is heuristic and should not be called causal. Review source evidence and report sensitivity under documented rules.  
**Common wrong answer:** automatically blame the nearest deployment without evidence.

### E08 — L2 percentile (10 min)

**Prompt:** lead times are [2, 4, 6, 8] hours. Under nearest-rank, what are p75 and p90?  
**Model answer:** p75 = 6 hours (rank ceil(.75×4)=3); p90 = 8 hours (rank ceil(.90×4)=4). Sample size is four, so p90 is simply the maximum and unstable.  
**Common wrong answer:** interpolate without identifying the percentile method.

### E09 — L3 value-stream bottleneck (15 min)

**Prompt:** coding takes 20 minutes, review wait 6 hours, CI 25 minutes, staging wait 90 minutes. Where should you investigate first?  
**Model answer:** review wait is the largest observed wait, so investigate its queue and ownership before optimizing coding. Preserve quality and workload guardrails.  
**Common wrong answer:** optimize CI because it is easiest to measure, despite its smaller contribution.

### E10 — L3 before/after causality (15 min)

**Prompt:** median lead time falls from 5 to 4 days after a new review process. Can you conclude it caused the improvement?  
**Model answer:** not from that alone. Check sample sizes, change mix, seasonality, definition stability, distributions, guardrails, and a plausible comparison/baseline.  
**Common wrong answer:** “Yes, because the metric improved.” Correlation and timing alone do not establish causation.

### E11 — L3 Goodhart scenario (15 min)

**Prompt:** a deployment quota leads to empty redeployments. Give two countermeasures.  
**Model answer:** define eligible deployment semantics and audit source events; pair frequency with stability and customer outcomes; prohibit individual rankings.  
**Common wrong answer:** increase the quota, which intensifies the incentive.

### E12 — L3 canary aborts (15 min)

**Prompt:** a canary detects a regression and aborts before user exposure. Is it a production change failure?  
**Model answer:** under the primary local CFR definition, not automatically; it is a failed rollout attempt and a useful safety signal. Report abort rate separately. A different explicit policy can include it in a release-attempt failure rate.  
**Common wrong answer:** hide aborts entirely, losing evidence about candidate quality.

### E13 — L3 cross-team comparison (15 min)

**Prompt:** leadership compares an ETL service that releases weekly with a web app that releases hourly. What context is needed?  
**Model answer:** release unit, criticality, data validation/reprocessing requirements, change type, architecture, team mission, sample size, and customer outcome. Prefer within-team trajectories.  
**Common wrong answer:** rank the ETL team as slower without context.

### E14 — L3 reliability conflict (15 min)

**Prompt:** deployment frequency improves, but SLO attainment and customer task success worsen. What is the recommendation?  
**Model answer:** do not declare success; investigate reliability/customer regressions and apply the agreed SLO/error-budget policy. The integrated scorecard shows throughput is not the whole outcome.  
**Common wrong answer:** optimize frequency further because it is the DORA metric with the clearest gain.

### E15 — L4 individual ranking (20 min)

**Prompt:** an executive requests a named ranking by commits and lead time. Write a response.  
**Model answer:** explain that these metrics are system-level signals with confounding and definition sensitivity; offer team-level bottleneck and outcome analysis; cite the charter's prohibited use and document/escalate the request if necessary.  
**Common wrong answer:** comply but label the chart “for information only.” The ranking can still create surveillance and harmful incentives.

### E16 — L4 charter audit (20 min)

**Prompt:** the charter has a metric owner but no data-quality owner, retention policy, or definition version. Is it ready?  
**Model answer:** no. Add source lineage, data-quality responsibility, access/retention, definition version, audit and revision rules before executive use.  
**Common wrong answer:** “The owner can fix that later.” Without controls, the number may be untrustworthy or misused.

### E17 — L4 data/ML definition (20 min)

**Prompt:** a batch job is green but publishes stale data; the serving API is available. Is the pipeline restored?  
**Model answer:** not necessarily. Define restore as validated data freshness/correctness and distinguish job completion from downstream data availability. Track application availability and pipeline/data SLIs separately.  
**Common wrong answer:** treat successful process exit as customer-facing recovery.

### E18 — L4 executive narrative (20 min)

**Prompt:** deployment frequency rises, CFR is unknown because incident links are missing, and customer outcomes are flat. What do you report?  
**Model answer:** throughput appears to have changed, stability is unknown rather than good, and outcomes have not improved. Assign data-quality remediation, avoid causal claims, and defer investment conclusions until evidence improves.  
**Common wrong answer:** assume unknown CFR is zero and announce success.

### Assessment rubric

- **80% or above:** proceed; preserve the evidence and definitions.
- **60–79%:** remediate missed objectives and repeat the relevant labs.
- **Below 60%:** repeat the relevant level before moving to governance decisions.

Suggested scoring: 5 points per exercise; 90 total. Full credit requires the correct answer plus an explanation of assumptions/limitations. Partial credit for arithmetic with missing interpretation. This is a learning rubric, not a performance evaluation.

## 12. Checklist, glossary, references, and audit

### 12.1 Production checklist

- [ ] Each metric has a versioned definition, owner, unit, denominator, time window, and source.
- [ ] Production deployment eligibility and canary-abort semantics are explicit.
- [ ] Lead-time start/end and restore boundary are documented.
- [ ] Incident-to-deployment links distinguish confirmed from heuristic.
- [ ] Missing/invalid data is visible; no silent zero-fill.
- [ ] Reports include counts, distributions, sample size, and data-quality warnings.
- [ ] Historical definition changes are auditable and backfills are versioned.
- [ ] DORA is paired with SLO/error budget, incident/toil/on-call health, and customer outcomes.
- [ ] No individual ranking or surveillance use is allowed by the charter.
- [ ] Cross-team comparisons include mission, criticality, release unit, and sample caveats.
- [ ] Review cadence and corrective-action owners are explicit.
- [ ] Vendor and benchmark claims have current primary-source evidence.

### 12.2 Glossary

| Term | Definition |
|---|---|
| Deployment frequency | Count/rate of eligible production deployments over a defined period |
| Lead time for changes | Elapsed time between documented change start and successful production boundary |
| Change failure rate | Share of eligible changes linked to defined production failures requiring remediation |
| Restore time | Elapsed time between defined failure start and verified service restoration |
| Deployment rework rate | Share of deployments classified as unplanned bug-fix work under a documented definition |
| SLI | Quantitative measure of user-relevant service behavior |
| SLO | Target for an SLI over a defined window |
| Error budget | Allowed unreliability implied by an SLO; policy is covered in M10 Unit 9 |
| CFR sensitivity | Difference in CFR under alternative linkage/inclusion rules |
| Flow efficiency | Touch time divided by elapsed lead/cycle time, with boundaries stated |
| WIP | Work in progress in a defined workflow |
| Goodhart's law | Warning that a measure can stop being useful when optimized as a target |
| Campbell's law | Warning that high-stakes use of indicators can distort both data and the process measured |
| Data lineage | Trace from a reported metric back to its source events and transformations |
| Confirmed link | Association supported by explicit source evidence under the declared policy |
| Heuristic link | Candidate association inferred from a rule such as time proximity; not proof of causality |
| Deployment rework | Unplanned deployment to fix a user-facing bug under the local definition |
| SPACE | Multidimensional framework for understanding developer productivity |

### 12.3 References and source/claim register

1. **DORA, “A history of DORA’s software delivery metrics,” Nathen Harvey, 2 January 2026.** Current evolution from historical four to five metrics. https://dora.dev/insights/dora-metrics-history/
2. **DORA, “DORA’s software delivery performance metrics,” current guide.** Five-metric framing and practical improvement approach. https://dora.dev/guides/dora-metrics/
3. **DORA, “Evolving the measures of software delivery performance,” Accelerate State of DevOps Report 2024.** Explains deployment rework rate and throughput/instability grouping. https://dora.dev/research/2024/dora-report/2024-dora-accelerate-state-of-devops-report.pdf
4. **DORA, “Accelerate State of DevOps Report 2021.”** Historical benchmarking context, including the earlier five-metric formulation. https://dora.dev/research/2021/dora-report/
5. **DORA, “Capabilities: Working in small batches.”** DORA's published framing of small batches. https://dora.dev/capabilities/working-in-small-batches/
6. **Forsgren, Storey, Maddila, Zimmermann, Houck, Butler, “The SPACE of Developer Productivity: There’s more to it than you think,” ACM Queue 19(1), 6 March 2021.** https://doi.org/10.1145/3454122.3454124
7. **DORA Team, Four Keys repository.** Repository marked archived on 23 January 2024 and not currently maintained. https://github.com/dora-team/fourkeys
8. **GitLab, DORA metrics documentation and API.** Product-specific four-metric definitions and availability/tier information. https://docs.gitlab.com/user/analytics/dora_metrics/ and https://docs.gitlab.com/api/dora/metrics/

#### Source/claim register

| Claim | Classification | Evidence / status |
|---|---|---|
| Current DORA guide uses five delivery metrics | Verified sourced fact | DORA current guide and 2026 history page consulted |
| Historical four-metric framing is common | Verified sourced fact | DORA metric history page consulted |
| SPACE has five dimensions and cautions against single-metric productivity | Verified sourced fact | Original ACM Queue paper and Microsoft Research publication page consulted |
| Small batches are a DORA capability associated with delivery outcomes | Verified sourced fact | DORA small-batches capability page consulted; not treated as proof of causality for a local intervention |
| All CSV event data and cases in this chapter | Synthetic / illustrative | Generated for learning; not production evidence |
| Metric formulas and event inclusion rules in Section 3 | Engineering interpretation / local lab policy | Explicitly illustrative; not claimed as universal DORA formula |
| Four Keys current maintenance | Verified sourced fact | `dora-team/fourkeys` GitHub repository says archived on 23 January 2024 and not currently maintained |
| GitLab DORA feature scope | Verified sourced fact, product-specific | Current official docs describe four metrics and Ultimate-tier availability; verify current plan before adoption |
| Current GitHub DORA-related feature scope | `[VERIFY]` | No authoritative current GitHub source verified; no feature claim made |
| Current vendor features/prices | `[VERIFY]` | No specific capability or price claim made |
| Historical benchmark thresholds | Not asserted | Must verify exact report/year/population before use |

### 12.4 Syllabus coverage audit

| Syllabus requirement | Level | Chapter section(s) | Evidence/artifact present | Status | Remaining gap or corrective action |
|---|---|---|---|---|---|
| DORA and historical/current metric framing | L1 | 2.1–2.2, 12.3 | Current five-metric framing, historical four, references | PASS | Recheck live guide at next review |
| Four metrics, definitions, examples, limitations | L1 | 2.2–2.5, 3 | Formula table and worked calculations | PASS | Local definitions must be adapted |
| Historical performance bands qualified | L1 | 2.6 | No thresholds quoted; report-year caveat | PASS | Add only with exact report citation |
| SPACE, DevEx, flow, SLO, outcomes | L1/L3 | 2.7, 6.6 | Comparison table and survey | PASS | Survey must be locally reviewed |
| Goodhart/Campbell applied | L1/L3 | 2.7, 6.5 | Concrete gaming examples | PASS | None |
| Synthetic source events and schema | L2 | 4.1 | Services, changes, deployments, incidents CSV | PARTIAL | CI/PR stage timestamps are discussed but not represented as separate CSV source table |
| Definition document | L2 | 4.2 | Complete definitions markdown block | PASS | Local owners/date need replacing |
| Pipeline computes four metrics and optional fifth | L2 | 4.3 | Python standard-library pipeline | PARTIAL | The pipeline computes deployment frequency, lead time, CFR, restore distribution, rework rate; not separate CI/PR data-stage computation |
| Per-service and per-week outputs | L2 | 4.3 | Service and weekly deployment/lead-time output | PARTIAL | Weekly output is derived from eligible successful deployments; no full zero-activity week calendar is generated |
| Percentiles, small-sample limits, severity split | L2 | 4.3 | Median/p75/p90, severity split | PASS | Nearest-rank method stated |
| Data quality and automated tests | L2 | 4.3–5.2 | Validation, five standard-library unit tests | PARTIAL | The included test module is focused, not exhaustive for every syllabus edge case |
| Deployment-to-incident linker | L2/L3 | 4.5 | Strict/window/canary policy code | PARTIAL | Code is a teaching example; expanded overlapping-incident boundary tests should be added before production use |
| CFR sensitivity under three definitions | L2/L3 | 4.5 | Three policy views and caveats | PARTIAL | Canary-abort result is intentionally a separate policy question; not a fully harmonized shared denominator |
| Value-stream mapping and dominant constraint | L3 | 6.1 | Touch/wait calculation | PASS | Synthetic data only |
| Improvement experiment and statistical caveats | L3 | 6.2 | Experiment record and limitations | PASS | No causal claim |
| Segmentation and small batches | L3 | 6.3 | Segmentation guidance | PASS | No empirical benchmark claimed |
| Reliability linkage, leading/lagging metrics | L3 | 6.4, 8.7 | Integrated scorecard | PASS | Requires local Unit 1/9 definitions |
| Gaming simulation and countermeasures | L3 | 6.5 | Eight gaming patterns | PASS | Illustrative cases |
| Privacy, SPACE/DevEx survey | L3/L4 | 6.6, 7.1 | Survey and privacy controls | PASS | Survey needs local privacy review |
| Platform topology/M16 handoff | L3 | 6.7 | Internal platform example | PASS | Not a platform implementation |
| Data/ML adaptation | L3 | 6.8, Lab 9 | Domain definition table | PASS | Local data/model acceptance criteria required |
| Measurement charter | L4 | 8.1 | Complete charter block | PASS | Requires actual stakeholder agreement |
| Review rituals and experiment log | L4 | 8.2 | Weekly/monthly/quarterly model | PASS | No real meeting was conducted |
| Responsible comparisons | L4 | 8.3 | Context checklist | PASS | Normalization cannot remove all confounding |
| Executive scorecard and ranking request | L4 | 8.4 | Synthetic scorecard and response | PASS | Synthetic only |
| Metrics hygiene audit | L4 | 8.6 | Audit table and workflow | PASS | No production source reconciliation performed |
| Integrated reliability/delivery scorecard | L4 | 8.7 | Template plus conflicting-outcome example | PASS | Fill with local data only after privacy review |
| Four Keys/vendor landscape | L4 | 9.1, 12.3 | Archived status of dora-team/fourkeys and GitLab official docs checked; vendor-neutral matrix | PARTIAL | GitHub current feature scope and commercial vendor claims remain `[VERIFY]` |
| Seven organizational case studies | L4 | 9.2 | Seven diagnose/fix/prevent cases | PASS | Synthetic scenarios |
| At least eight complete labs | L1–L4 | 10 | Labs 1–9 | PARTIAL | Labs are executable learning procedures but the CSV/code blocks must be copied into a temp directory; pipeline output should be run by learner to confirm |
| At least 15 exercises with answers | L1–L4 | 11 | 18 answered exercises | PASS | Scoring is formative |
| All code runnable, all tests executed | L2 | 4.3–4.5 | Complete core pipeline and tests supplied | NOT VERIFIED | See execution report; do not treat expected output as executed |
| Current GitHub/GitLab feature claims verified | L4 | 9.1 | No unverified specific feature claims asserted | PARTIAL | No product feature claims made; revisit only if vendor comparison is needed |
| No other repository file changed | — | 12.5 | Standalone output created outside repository | NOT VERIFIED | Repository checkout was unavailable; no repository change is claimed |

### 12.5 Execution/evidence report and remaining limitations

- **Source verification performed:** consulted official DORA pages on current metrics, metric history, small batches, DORA's 2021 report, and the original SPACE publication page.
- **Designed:** synthetic CSV fixtures, definition document, pipeline, CFR sensitivity function, charter, scorecard, audit template, labs, and exercises.
- **Execution:** after extracting the named Python/CSV blocks into a temporary directory, Python syntax compilation passed for the four Python scripts; the pipeline CLI completed successfully against the synthetic CSVs and reported 8 eligible production deployment events, confirmed CFR 25.00% (2/8), and one data-quality warning; 11 unit tests passed across the pipeline and CFR-linker suites. This validates the included synthetic fixture and the tested paths only, not production readiness. The sample CLI output in Lab 2 remains labelled as an example because a learner's environment and file paths differ.
- **Not performed:** no actual repository checkout/tree inspection, no modification of repository files, no M02/M08 integration, no production data access, no dashboard/provider setup, no organizational survey or meeting.
- **Repository boundary:** only the standalone target Markdown artifact was created in the working output area. The actual repository write state cannot be verified because the repository checkout was unavailable.
- **Open verification items:** current Four Keys maintenance/scope; any future vendor-specific features; exact report/year if benchmark thresholds are later added; local metric policy and privacy requirements.
- **Known technical gaps:** PR/CI events are included and validated as source data but are not used to compute stage-level duration distributions in the core DORA report; the core script's unit tests are focused rather than exhaustive; the canary-abort sensitivity view intentionally changes the measurement question and should not be compared as if it were identical to production CFR; no complete zero-activity weekly calendar is emitted. These are recorded as `PARTIAL` rather than concealed.

The goal is not a perfect-looking dashboard. The goal is a transparent measurement system that helps a team improve delivery and customer outcomes without making the metric the mission.
