# Platform SLOs, Adoption Metrics, and Developer Experience

**Target file:** `08-platform-slos-adoption-metrics-and-developer-experience.md`  
**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Module:** M16 — Platform Engineering and Internal Developer Platforms  
**Unit:** 8 of 9  
**Estimated study time:** 32–44 hours, including ten labs  
**Prerequisites:** Stages 0–2D and Stage 2E M01–M15; especially M10 Units 1/11, M11 Units 2/3, M15 Units 4/12, and M16 Units 1–7  
**Core tools:** Python 3 standard library, `unittest`, Git, CSV, JSON, YAML, Markdown, shell; optional Prometheus, `promtool`, Grafana, Docker/Podman, and `kind`  
**Awareness:** SPACE, DevEx, DX Core 4, CNCF platform maturity, opportunity-solution trees, RICE/ICE, AI-assisted developer tooling measurement  
**Last reviewed:** 2026-11-03  
**Tool baseline assumed:** Python 3.11+ syntax; record exact local Python, Prometheus, `promtool`, Grafana, Docker/Podman, Kubernetes, and `kind` versions. Grafana dashboard schemas and Prometheus rule behavior are `[VERIFY]` against the selected release.  
**Stack profile required:** Plat-Core required; Plat+Control optional  
**Footprint:** Plat-Core uses local files/Python; optional Prometheus/Grafana and `kind` can materially increase CPU/RAM/disk. Measure actual use.  
**Prices used:** hypothetical cost units (HCU) only; no vendor prices, invoices, or currency claims.

> **Core ethics rule:** measure the platform's effect on developers' work, never rank or surveil individual developers. All datasets are synthetic except the learner's own local golden-path task, which must be labelled `n=1`. Synthetic results demonstrate analysis mechanics only; they are not evidence of real developer behavior, productivity, adoption, satisfaction, or business impact.

## Table of contents

- [Handoff, Scope, and Learning Outcomes](#handoff-scope-and-learning-outcomes)
- [1. Why Platform Measurement Matters](#1-why-platform-measurement-matters)
- [2. The Three Families of Platform Measures](#2-the-three-families-of-platform-measures)
- [3. Metric Definitions, Outputs, Outcomes, and Vanity Metrics](#3-metric-definitions-outputs-outcomes-and-vanity-metrics)
- [4. Platform SLOs from the Developer's Perspective](#4-platform-slos-from-the-developers-perspective)
- [5. Instrumentation and the Synthetic Developer Journey](#5-instrumentation-and-the-synthetic-developer-journey)
- [6. Adoption Metrics and KPI Pipeline](#6-adoption-metrics-and-kpi-pipeline)
- [7. DORA Metrics by Golden-path Adoption Segment](#7-dora-metrics-by-golden-path-adoption-segment)
- [8. Developer-Experience Research Methods](#8-developer-experience-research-methods)
- [9. Measurement Rigor, Causal Caution, and Survey Science](#9-measurement-rigor-causal-caution-and-survey-science)
- [10. Privacy, Ethics, and Anti-gaming Safeguards](#10-privacy-ethics-and-anti-gaming-safeguards)
- [11. Dashboards, Feedback Loops, and Roadmap Prioritization](#11-dashboards-feedback-loops-and-roadmap-prioritization)
- [12. Platform Cost, Unit Economics, and ROI Uncertainty](#12-platform-cost-unit-economics-and-roi-uncertainty)
- [13. Data/ML Developer Experience](#13-dataml-developer-experience)
- [14. Advanced Measurement Operations and Governance](#14-advanced-measurement-operations-and-governance)
- [15. Ten Mandatory Hands-on Labs](#15-ten-mandatory-hands-on-labs)
- [16. Troubleshooting and Measurement Failure Cases](#16-troubleshooting-and-measurement-failure-cases)
- [17. Review Questions and Exercises](#17-review-questions-and-exercises)
- [18. Glossary](#18-glossary)
- [19. Completion Gate and Self-Audit](#19-completion-gate-and-self-audit)

---

## Handoff, Scope, and Learning Outcomes

> **Handoff from earlier modules:** M10 Unit 1 taught SLIs/SLOs and error budgets; M10 Unit 11 taught DORA metrics, their definitions and limits, Goodhart's law, anti-gaming safeguards, and the ethics of measuring people; M15 Unit 4 taught showback and unit economics. This unit applies them to the platform itself: SLOs for platform services, **adoption metrics**, and **developer-experience measurement and research** — without re-deriving those foundations, and with the same rule: **measure the platform's effect on developers' work, never individual developers.**

### Scope boundaries and continuity

| Prior / sibling unit | Reuse here | Boundary retained |
|---|---|---|
| M10 Unit 1 | SLI/SLO/error-budget vocabulary and SLO document discipline | Do not re-derive SLO mathematics; specify platform-facing SLIs and decisions |
| M10 Unit 11 | DORA definitions, event quality, segmentation, Goodhart, anti-gaming, privacy | Reuse definitions/caution; no individual performance ranking |
| M11 Units 2–3 | Prometheus metrics/PromQL and Grafana dashboard-as-code | Consume signals; do not rebuild telemetry architecture or re-teach PromQL |
| M11 Unit 8 | Synthetic probes and actionable symptom monitoring | Complete Unit 8 lesson was not located in the inspected session files; probe integration is `[VERIFY]` |
| M15 Unit 4 | Team/project/workload allocation, shared cost, HCU conventions | Apply to platform units; do not rebuild allocation foundations |
| M15 Unit 12 | GPU queue wait and ML workload economics | Treat queue wait as a DX measure, not a GPU scheduler lesson |
| M16 Units 1–2 | Platform-as-product, golden paths and paved roads | Measure platform value and supported-path adoption |
| M16 Units 3–6 | Provisioning, portal/catalog, scaffolding/templates, Crossplane APIs | Measure those capabilities; do not re-teach implementation |
| M16 Unit 7 | Tenant onboarding and lifecycle | Reuse onboarding time; tenant isolation remains Unit 7 |
| M16 Unit 9 | Governance, versioning, deprecation, compatibility | Forward reference; measure consequences, do not duplicate policy |

Confirmed sibling links:

- [`01-platform-engineering-principles-and-platform-as-a-product.md`](01-platform-engineering-principles-and-platform-as-a-product.md)
- [`02-golden-paths-templates-and-paved-roads.md`](02-golden-paths-templates-and-paved-roads.md)
- [`03-self-service-infrastructure-and-environment-provisioning.md`](03-self-service-infrastructure-and-environment-provisioning.md)
- [`04-developer-portals-and-backstage-service-catalog.md`](04-developer-portals-and-backstage-service-catalog.md)
- [`05-scaffolding-and-software-templates.md`](05-scaffolding-and-software-templates.md)
- [`06-platform-apis-with-crossplane-compositions.md`](06-platform-apis-with-crossplane-compositions.md)
- [`07-multi-tenancy-isolation-and-tenant-onboarding.md`](07-multi-tenancy-isolation-and-tenant-onboarding.md)
- [`09-platform-governance-deprecation-and-versioning.md`](09-platform-governance-deprecation-and-versioning.md)

**Repository-path note:** the roadmap confirms these M16 filenames/order. Root-relative M10/M11/M15 paths were not all confirmed in the attached roadmap excerpt, so this lesson does not invent them.

### Learning outcomes

1. **[L1]** Explain why a technically healthy platform can fail through non-adoption, workarounds, or loss of trust.
2. **[L1]** Separate reliability, adoption/usage, and DX/outcome measures; distinguish outputs/outcomes and leading/lagging indicators.
3. **[L2]** Define platform SLIs/SLOs, error-budget actions, and developer-journey probes for portal, templates, provisioning, GitOps, CI, catalog, and support.
4. **[L2]** Generate six months of reproducible synthetic events and calculate adoption KPIs with explicit denominators, windows, cohorts, and exclusions.
5. **[L2]** Compare DORA outcomes by golden-path adoption segment without unsupported causal claims.
6. **[L2]** Design surveys, interviews, friction logs, usability tests, journey maps, and support-ticket analysis.
7. **[L3]** Govern metric definitions as code and test missingness, duplicates, timezones, bots, denominator drift, and schema changes.
8. **[L3]** Explain selection bias, regression to the mean, Simpson's paradox, matched cohorts, DiD intuition, and small-sample uncertainty.
9. **[L3]** Build privacy-safe dashboards and a scanner that rejects person-level fields/rankings.
10. **[L4]** Operate a metrics charter, review cadence, definition-change process, data-quality SLO, and quarterly product review.

### Plat-Core and Plat+Control

| Profile | Includes | Limitations |
|---|---|---|
| **Plat-Core (required)** | Python, synthetic CSV/JSON, definitions, tests, KPI reports, survey analysis, privacy scanner, HCU model, review pack | No live cluster, CI, portal, or real developer telemetry; all generated results are synthetic |
| **Plat+Control (optional)** | Local Prometheus + `promtool`, Grafana, disposable `kind` journey | Versions, schemas, compatibility, footprint, and cluster integration require local verification |

Preflight: record OS/WSL2, CPU/RAM/disk baseline, Python, Git, and optional tool versions. Start one optional component at a time. Plat-Core is the safe fallback.

---

## 1. Why Platform Measurement Matters

A platform is an internal product. Its customers are the teams trying to build, deploy, operate, and improve services and data/ML workloads. Measurement answers whether the platform reliably enables those tasks, whether eligible teams voluntarily adopt the supported path, where friction accumulates, and whether investment is justified.

A platform can fail silently. The portal may return HTTP 200, the template service may be up, and the provisioning API may report success while teams avoid the portal, copy old repositories, open manual tickets, wait for permissions, or maintain private scripts. Component uptime is necessary but insufficient. The platform's customer-facing unit is a completed developer task, not a green pod.

### 1.1 Decisions measurement should support

- **Reliability:** Is the capability dependable enough for its workflow?
- **Adoption:** Do eligible services use a supported path voluntarily and sustainably?
- **Experience:** Where do developers wait, retry, become confused, or lose confidence?
- **Safety:** Did the path improve safe delivery, or merely artifact creation?
- **Investment:** Should a capability be repaired, simplified, expanded, consolidated, or retired?
- **Unintended consequences:** Did cost, security debt, support load, cognitive load, or operational risk increase?

Every metric should have a decision owner. If nobody can name what decision changes when it moves, it is likely reporting decoration.

### 1.2 What component monitoring misses

| Healthy technical signal | Hidden developer failure | Better evidence |
|---|---|---|
| Portal HTTP success | Search is stale or template is undiscoverable | Catalog freshness, task success, usability observation |
| Template API success | Generated repo fails first CI | Template-to-first-green-CI journey SLI |
| Provisioning accepted | Environment is not usable | p95 time-to-ready and readiness check |
| GitOps controller healthy | Application never becomes healthy | Desired-to-healthy journey |
| Ticket count falls | Support moved to chat/private channels | Channel inventory + interviews + friction logs |
| Golden-path usage rises | Teams were forced to migrate | Voluntary adoption, task success, incidents, escape-hatch reasons |

### 1.3 Measurement feedback system

```text
Developer need -> platform capability/golden path
     | reliability telemetry | aggregate adoption | DX research | outcomes
     v
Metric definitions + data quality + privacy controls
     v
Interpretation with context and uncertainty
     v
Repair / invest / simplify / investigate / retire
     v
“You said, we did” -> re-measure
```

The loop breaks when developers do not trust collection, definitions change silently, incentives reward the wrong behavior, or feedback is collected but ignored.

### 1.4 Outputs versus outcomes

An **output** is something shipped or recorded: templates generated, portal views, plugins published, APIs created, or requests accepted. An **outcome** changes a developer's ability to complete meaningful work: safe first deployment, reduced waiting, fewer avoidable failures, less rework, predictable operations, or lower cognitive load.

Outputs are useful leading indicators, not proof of outcomes. If template generation doubles but first-green-CI success is unchanged, the first click may be easier while delivery is not.

### 1.5 Testable hypothesis

> `[ASSUMPTION]` If template defaults and the reproducible environment path improve, eligible services using the supported path should show higher first-deploy task success and fewer avoidable provisioning retries, without worsening change-failure rate, security conformance, or cost per active service.

The hypothesis names treatment, population, outcomes, countermetrics, and guardrails. It does not assume the hypothesis is true.

---

## 2. The Three Families of Platform Measures

| Family | Purpose | Examples | Unit / grain | Owner | Leading/lagging | Common misuse |
|---|---|---|---|---|---|---|
| Platform reliability | Does the capability deliver its promise? | Portal availability; template generation; provisioning success/p95 ready; first-green-CI; CI success/duration/wait; GitOps convergence; Crossplane reconcile; catalog freshness; support response; journey success | Request, journey, capability, window | Capability owner/SRE | Mostly leading operational signals; journey outcome may lag | Component health mistaken for developer success |
| Adoption and usage | Do eligible services voluntarily use supported paths? | Golden-path coverage; version spread; self-service ratio; aggregate portal use; ticket/self-service ratio; time-to-first-deploy; onboarding; escape hatch; cohort retention | Eligible service, cohort, month | Platform product/catalog owner | Leading reach/fit signals | Clicks mistaken for adoption; denominator omitted |
| DX and outcomes | Is work easier, safer, predictable? | Satisfaction/confidence; friction; cognitive load; task success/errors/time; DORA outcomes; CI wait/flakiness; restore time; data/ML workflow waits | Task, service/team aggregate, survey wave | Platform product/research | Mix of leading perception/flow and lagging outcomes | Activity counts called productivity |

### 2.1 Platform reliability

- **Portal availability:** can a developer discover a service and retrieve usable metadata?
- **Template generation:** does the generated repository meet its contract and pass first CI?
- **Provisioning success:** does the request reach verified readiness, not merely acceptance?
- **p95 time-to-ready:** how long until a database, namespace, environment, or model-serving path is usable?
- **CI reliability/duration:** is feedback deterministic, timely, and not excessively queued?
- **GitOps convergence:** does desired state become healthy and usable within the promise?
- **Crossplane reconciliation:** does a platform API claim reach a usable Ready state? Metric/condition mapping is `[VERIFY]` by controller version.
- **Catalog freshness:** does the portal reflect authoritative ownership/status?
- **Support responsiveness:** how long until a meaningful response, not auto-acknowledgement?
- **End-to-end journey:** can a synthetic user generate, validate, deploy, verify, and tear down a sample service?

### 2.2 Adoption and usage

Adoption is conditional on eligibility. Unsupported services must not be counted as failed adopters. Define denominator first:

- `golden_path_coverage = conformant_eligible_services / eligible_services`
- `self_service_ratio = completed_self_service / (completed_self_service + completed_manual)`
- `escape_hatch_rate = eligible_services_using_approved_escape_hatch / eligible_services`
- `version_share = services_on_supported_version / adopted_services`
- `retention = cohort_services_still_conformant / cohort_services_adopted_at_start`

Publish denominators, windows, eligibility, exclusions, and missing-data status. A percentage without them is not reproducible.

### 2.3 Developer experience and outcomes

Use system data and perceptual evidence together:

- satisfaction/confidence: short, neutral, repeated surveys;
- friction: waits, retries, blockers, confusing steps, workarounds;
- flow: CI feedback delay, time-to-first-deploy, pipeline authoring friction;
- cognitive load: perceived effort to understand and operate the path;
- usability: task completion, elapsed time, errors, help requests;
- production outcomes: change failure, recovery, reliability, reproducibility, handoff quality.

SPACE is awareness-level context: Satisfaction, Performance, Activity, Communication, Efficiency. DevEx discussions emphasize feedback loops, cognitive load, and flow state. DX Core 4 is also awareness-level. Details must be `[VERIFY]` against primary publications; no benchmark figures are quoted here. No single metric captures productivity; activity counts alone mislead.

### 2.4 Leading versus lagging

A **leading indicator** may move before an outcome: template generation success, readiness latency, or supported-path coverage. A **lagging indicator** describes a result after work: change failure, restore time, or verified deployment outcome. Leading indicators are not automatically causal. Adoption may rise because of a mandate or eligibility change. Track mechanism and countermetrics.

### 2.5 Misleading dashboard example

“2,400 template generations”, “94% adoption”, “tickets down 35%”, and “average portal latency 80 ms” look successful but omit eligible-service denominator, conformance definition, first-green-CI, channel changes, p95, survey bias, and end-to-end journey. Pair each headline with a countermetric and qualitative follow-up.

---

## 3. Metric Definitions, Outputs, Outcomes, and Vanity Metrics

A metric is a governed definition, not a chart label. Specify question, event grain, numerator, denominator, eligibility, exclusions, timezone, window, source, owner, privacy class, and limitations.

### 3.1 Paired metrics

| Headline | Pair with | Why |
|---|---|---|
| Template generations | First-green-CI and first-deploy success | Scaffolds may not work |
| Golden-path coverage | Voluntary adoption, escape-hatch reasons, task success | Forced migration is not product fit |
| Ticket count | Channel inventory, ticket rate, friction themes | Channel move may masquerade as improvement |
| Portal usage | Task completion and catalog freshness | Views do not prove usefulness |
| Time-to-first-deploy | Stable definition, failure rate, quality | Prevents definition gaming |
| CI duration | Queue wait, flakiness, feedback quality, runner cost | Speed may trade away reliability/cost |
| Satisfaction | Response rate, distribution, n, qualitative themes | Small/pressured sample misleads |
| Cost per service | Reliability, mix, shared-cost assumptions | Cost cutting may hide risk |

### 3.2 Vanity metrics

Portal page views can debug navigation but do not prove task completion. Template/plugin counts can increase complexity. Raw activity can be bots/retries/tests. Individual deploy counts are prohibited as developer-performance measures. Ticket count without channel context is ambiguous. Adoption without eligibility can be manufactured. Average latency hides tails.

### 3.3 Metric definition contract

```yaml
metric_id: platform.golden_path_coverage
version: 1
question: "What share of eligible services conforms to a supported golden path?"
unit: ratio
entity_grain: service_month
numerator: "eligible services with supported path and passing conformance"
denominator: "services marked eligible in authoritative catalog snapshot"
window: calendar_month
timezone: UTC
eligibility_rule: "month-end catalog snapshot; approved exceptions excluded with reason"
exclusions: ["synthetic_test_services", "retired_services", "bot_fixtures"]
source_tables: ["catalog_services", "conformance_results"]
owner: platform-product
privacy_classification: aggregate_team_service
retention_days: 180
known_limitations:
  - "catalog completeness affects denominator"
  - "conformance is not developer satisfaction"
```

This is a teaching schema, not a standard. Validate it with JSON Schema or a custom checker before production.

### 3.4 Define the nouns

| Noun | Recommended definition | Local decision needed |
|---|---|---|
| Service | Cataloged deployable/independently operated capability with stable ownership | Are jobs, notebooks, libraries, models services? |
| Eligible service | Meets documented technical/policy prerequisites for the path in the window | Who approves exceptions and expiry? |
| Deployment | Production or agreed target-environment change making an artifact/config active | How are canary aborts/rollbacks represented? Reuse M10 Unit 11 |
| Adoption | Currently uses supported path and passes conformance | Template generation alone is insufficient |
| Active usage | Aggregate capability use by eligible service/team in a period | Define event/window; no person tracking |
| First deploy | First successful verified deployment after journey start | What counts as verified? |
| Ticket | Support request in approved system/channel with stable synthetic ID/category | What other channels exist? |
| Escape hatch | Documented approved alternative because default path does not fit | Distinguish valid exception from undocumented bypass |

### 3.5 Denominator example

`[ILLUSTRATIVE]` Catalog has 120 services: 10 retired, 8 test fixtures, 12 unsupported/ineligible. Eligible denominator = 90. If 54 conform, coverage = 54/90 = 60%. Using 120 answers a different question; using only the 54 adopters gives a meaningless 100%.

### 3.6 Definition changes

Changing first deploy from “verified production deploy” to “preview deploy” can manufacture improvement. Version definitions, preserve old logic, dual-run where possible, document trend breaks, and restate history only when raw evidence supports backfill.

---

## 4. Platform SLOs from the Developer's Perspective

Platform developers are internal customers. Define a promise around the task they need to complete, capability boundary, user-visible failure, measurement window, owner, and support expectation. Not every component needs the same criticality tier.

### 4.1 Capability tiers `[ILLUSTRATIVE]`

| Tier | Example | Reason | Policy posture |
|---|---|---|---|
| Critical delivery path | CI runners, provisioning API | Failure blocks delivery | Conservative rollout and reliability review |
| Important shared capability | Templates, GitOps convergence, registry integration | Degrades delivery/reproducibility | Defined SLO and staged changes |
| Supporting experience | Portal search, docs rendering | Workaround may exist but friction rises | Lower criticality; avoid over-engineering |

Set tiers from actual internal dependencies and user impact.

### 4.2 Reusable SLO document

```markdown
# Platform SLO: <capability>
- Developer promise:
- Customer/workflow:
- Capability boundary:
- Owner and escalation contact:
- SLI name and unit:
- Good event definition:
- Valid event definition:
- Numerator / denominator or measurement method:
- Measurement window and timezone:
- Exclusions (with rationale):
- Target: [ILLUSTRATIVE until justified]
- Data source and instrumentation:
- Error-budget reference: M10 Unit 1
- Burn-rate alert and runbook:
- Budget-depletion policy: M10 Unit 9 handoff
- Dependencies and blind spots:
- Missing-data behavior:
- Review date and evidence link:
```

### 4.3 Platform SLI/SLO inventory

Targets are `[ILLUSTRATIVE]`, not universal recommendations. Definitions and event boundaries matter more than the example numbers.

| Capability | SLI | Example target | Developer boundary | Pitfall |
|---|---|---|---|---|
| Provisioning | Verified-ready requests / valid requests | 98% / rolling 28d | Accepted → readiness and connection check | HTTP 202 counted as success |
| Time-to-ready | p95(`ready_at - accepted_at`) by capability | p95 ≤ 12 min | Request → usable resource | Mix unlike capabilities; omit timeouts |
| Template + first CI | Repos first-green within 60m / valid generated repos with CI | 90% | Generate → first CI result | Exclude repos never reaching CI |
| Portal availability | Successful valid page/search requests / valid requests | 99.5% | Discover and retrieve usable metadata | Shell loads while search is broken |
| Catalog freshness | Fresh eligible records / eligible records | 98% within 24h | Current owner/status/docs visible | Missing records omitted |
| GitOps convergence | Changes healthy within window / valid desired changes | 95% within 15m | Submit → workload healthy | Controller sync ≠ app readiness |
| CI success | Valid non-flaky successful required runs / valid runs | 97% | Required feedback completed | Retries mask flakiness |
| CI duration | p95 trigger-to-required-result; split queue/execution | p95 ≤ 18m | Trigger → required result | Average hides tail; mix queue/execution |
| Support response | p90 time to meaningful response | p90 ≤ 4 business hours | Ticket → actionable response | Auto-ack counted as response |
| End-to-end journey | Full successful journeys / valid attempts; p95 elapsed | 95%, p95 ≤ 30m | Generate → CI → deploy → verify → teardown | Component-only health hides integration failure |
| Crossplane reconcile | Ready claims / valid claims | `[VERIFY]` metric/condition mapping | Claim → composed resources usable | Controller-specific metric assumed universal |

### 4.4 Accepted is not ready

`[ILLUSTRATIVE]` 100 valid requests are accepted, 98 return an HTTP acceptance response, but only 91 environments become ready and pass a connection check. Acceptance SLI = 98%; usable-readiness SLI = 91%. The latter is the developer promise. Keep both as diagnostics, but set the SLO against the promised outcome.

### 4.5 Error-budget policy for platform changes

Reuse M10 error-budget and release-governance foundations:

1. Within budget: routine changes follow normal review and rollout controls.
2. Rapid burn: verify telemetry, assess developer impact, pause risky rollout if policy requires, prioritize the affected journey.
3. Budget exhausted: platform/product owners decide which nonessential changes pause and communicate the reliability plan.
4. Do not freeze unrelated capabilities automatically; assess dependency and blast radius.
5. Resume risky changes only after recovery evidence and reviewed mitigation.

Exact burn windows/thresholds must reuse the organization's M10 policy. The following is only a short-window symptom example, not a complete multi-window burn-rate policy.

### 4.6 Prometheus-style alert rule example

Assumes the application exports these illustrative counters. Verify syntax/labels with the installed `promtool` version.

```yaml
groups:
  - name: platform-developer-journey
    interval: 1m
    rules:
      - alert: PlatformJourneySuccessLow
        expr: |
          sum(rate(platform_journey_attempts_total{result="success"}[10m]))
          /
          clamp_min(sum(rate(platform_journey_attempts_total[10m])), 1e-9)
          < 0.95
        for: 5m
        labels:
          severity: ticket
          team: platform
        annotations:
          summary: "Synthetic journey success is below illustrative threshold"
          description: "Check probe freshness, stage results, and readiness."
      - alert: ProvisioningBadEventRatioHigh
        expr: |
          1 - sum(rate(platform_provision_requests_total{result="good"}[5m]))
          / clamp_min(sum(rate(platform_provision_requests_total[5m])), 1e-9) > 0.02
        for: 5m
        labels:
          severity: ticket
          team: platform
        annotations:
          summary: "Provisioning bad-event ratio exceeds illustrative guardrail"
          description: "Validate denominator and missing events before changing rollout state."
```

`clamp_min` avoids division by zero; it does not make absent telemetry healthy. Add independent probe-freshness detection. No traffic/missing series must be unknown, not 100%. Use M10's actual burn-rate policy in production. Do not page on a metric without an action.

Optional syntax check: `promtool check rules platform-alerts.yml`. The following is a **version-sensitive test-fixture pattern**; validate the exact field names and rule-test syntax against the installed Prometheus release before use.

```yaml
rule_files:
  - platform-alerts.yml
evaluation_interval: 1m
tests:
  - interval: 1m
    input_series:
      - series: 'platform_journey_attempts_total{result="success"}'
        values: '0+0x20'
      - series: 'platform_journey_attempts_total{result="failure"}'
        values: '0+1x20'
    alert_rule_test:
      - eval_time: 10m
        alertname: PlatformJourneySuccessLow
        exp_alerts:
          - exp_labels:
              severity: ticket
              team: platform
            exp_annotations:
              summary: "Synthetic journey success is below illustrative threshold"
              description: "Check probe freshness, stage results, and readiness."
```

Run `promtool test rules platform-alerts.test.yml` after `promtool check rules`. This fixture is an authored example, not a claim of local Prometheus execution. Official Prometheus docs were consulted for recording rules, alerting rules, and `promtool`; local validation remains open. If `promtool` is unavailable, Plat-Core tests validate only Python logic, not PromQL semantics.

### 4.7 Dashboard-as-code specification

Minimum panels: provisioning verified-ready ratio and denominator; p50/p95 time-to-ready by capability; template-to-first-green-CI; journey success/p95; GitOps convergence; CI queue wait/duration; catalog freshness/missing records; support response distribution; error-budget/burn-rate and probe freshness.

Grafana file provisioning supports version-controlled datasource/dashboard configuration. Dashboard JSON and provisioning schemas are release-sensitive; pin a release and validate its exported model. The M11 Unit 3 lesson is the implementation reference. No usernames, email addresses, payloads, code, secrets, or individual deploy counts in labels. Official reference: https://grafana.com/docs/grafana/latest/administration/provisioning/ `[VERIFY]` selected release.

---

## 5. Instrumentation and the Synthetic Developer Journey

Instrumentation is the contract between platform behavior and measurement. Capture enough workflow context without collecting unnecessary personal data.

### 5.1 Minimal event schema

```json
{
  "schema_version": "1.0",
  "event_id": "evt-000001",
  "event_ts": "2026-05-01T09:30:00Z",
  "event_type": "provisioning_completed",
  "team_id": "team-analytics",
  "service_id": "svc-analytics-api",
  "capability": "database",
  "template_version": "python-service-v2",
  "environment": "dev",
  "journey_id": "journey-0001",
  "outcome": "success",
  "duration_seconds": 214,
  "error_category": null,
  "golden_path_state": "conformant",
  "source_system": "synthetic-generator",
  "is_synthetic": true
}
```

Controls: UTC timestamps with timezone; synthetic team/service IDs; short-lived non-personal journey ID; no keystrokes, code, notebooks, secrets, tokens, or customer data; explicit schema version/provenance; enumerated event/state transitions; bounded metric labels to avoid high cardinality.

### 5.2 Instrumentation sources and bias

| Source | Evidence | Bias / provenance to record |
|---|---|---|
| Provisioning lifecycle | Accepted, ready, failed, duration | Async completion, retries, cancellations, manual work |
| Template CLI/CI | Generation, commit fixture, first green CI | CI disabled, bots, retries, forks |
| Git/CI metadata | Commit-to-deploy, wait, failure | Service mapping, bot activity, missing repos |
| GitOps | Sync, health, drift, convergence | Controller health does not prove workload usability |
| Crossplane | Claim/reconcile state | Controller metric/condition `[VERIFY]` |
| Portal analytics | Aggregate discovery/search | Consent, bots, anonymization, instrumentation `[VERIFY]` |
| Catalog | Eligibility, owner, path, version, status | Stale/missing records alter denominator |
| Tickets | Category, first response, resolution | Channel migration, avoidance, auto-ack |
| Research | Satisfaction, confidence, friction | Non-response, self-selection, small n |

For each source record owner, cadence, timezone, schema, missingness, retention, and known bias. A source table is not automatically ground truth.

### 5.3 Journey state machine

`generate → commit/CI-equivalent → deploy → verify → teardown`

```text
START -> GENERATED -> CI_GREEN -> DEPLOYED -> VERIFIED -> TORN_DOWN
Any stage may become FAILED, TIMED_OUT, or CLEANUP_FAILED.
Retries are separate attempts under a synthetic journey ID.
Success requires verification AND teardown.
```

Use bounded timeouts. Do not retry irreversible actions without idempotency checks. Cleanup runs even after failure and is reported separately. Failed cleanup means the journey did not complete safely.

### 5.4 Plat-Core and real `kind` probe

The shared program in Lab 2 contains a deterministic local state-machine simulation. It does not create a cluster, run real CI, or prove Kubernetes behavior. A real optional `kind` probe should create a uniquely named disposable cluster, run a harmless sample service, perform local CI-equivalent validation, deploy and wait for readiness, verify, delete resources, and inventory leftovers. Record actual hardware/software and measured timing. Do not invent timings. Kubernetes manifests, image loading, ingress, and readiness depend on local cluster profile `[VERIFY]`. If resource use is high, use Plat-Core.

### 5.5 Measurements

Record stage start/end, duration, outcome/error category, retries, journey success, cleanup outcome, and environment metadata. Do not average stage success percentages to create journey success. A journey is good only when every required stage passes. Missing stage events are unknown/bad according to the contract, never silently successful.

---

## 6. Adoption Metrics and KPI Pipeline

The KPI pipeline transforms raw events into validated, normalized, decision-ready measures. Preserve denominator and quality status with every result.

### 6.1 Denominator definitions

| KPI | Numerator | Denominator | Grain/window |
|---|---|---|---|
| Golden-path coverage | Eligible services on supported path and conformant | Eligible services in catalog snapshot | Service-month |
| Template/API version spread | Services on each version | Adopted services | Service-month |
| Self-service ratio | Completed self-service requests | Self-service + manual completed requests | Request-month |
| Time-to-first-deploy | Verified deploy timestamp minus journey start | Successful journeys; failures/censored separately | Service journey |
| Tenant onboarding time | Tenant ready minus onboarding start | Completed onboarding requests | Tenant onboarding |
| Ticket rate | Tickets by category | Eligible services or requests (choose one) | Category-month |
| Escape-hatch rate | Eligible services with approved escape hatch | Eligible services | Service-month |
| Retention | Cohort still conformant at period end | Cohort conformant at start | Cohort-month |
| Cohort adoption | Adopted by day N | Eligible cohort members | Onboarding month |
| Catalog freshness | Fresh eligible records | Eligible catalog records | Snapshot |

### 6.2 Synthetic six-month dataset and planted confounders

Lab 2 generates synthetic events with fixed seed, six months, varying team maturity, service age/workload, adoption curves, template versions, provisioning, CI, deployments, incidents/tickets, and survey responses. Planted confounders: mature teams adopt earlier; newer services use newer templates; workload complexity varies; a documentation intervention changes a funnel stage; selected missing/duplicate events are added for quality tests; survey response propensity varies by maturity. Known ground truth exists only because the data is synthetic.

### 6.3 Pipeline

```text
synthetic events + catalog/CI/deploy/ticket/survey fixtures
 -> schema validation -> deduplication/normalization
 -> eligibility snapshot -> KPI calculation
 -> data-quality report -> aggregate dashboard/report -> decision record
```

If a source is missing or denominator invalid, emit `UNKNOWN` with reason, not zero or 100%.

### 6.4 Core formulas

- Coverage = conformant eligible services / eligible services.
- Self-service ratio = completed self-service / (self-service + manual completed).
- Escape-hatch rate = eligible services using approved escape hatch / eligible services.
- Version share = services on version / adopted services.
- Time-to-first-deploy = distribution of verified-deploy timestamp minus journey start; report non-completion separately.
- Ticket rate = tickets / eligible services **or** tickets / requests; choose and version.
- Retention = retained conformant services / cohort services at start.
- Cohort adoption = adopted by day N / eligible cohort members.

### 6.5 Support-ticket analysis

Use stable categories: access, documentation, template, provisioning, CI, GitOps, catalog, data access, GPU queue, policy exception, incident, other. Analyze count/rate, median/p90 resolution, reopened rate, and themes. A ticket reduction alone is ambiguous. Compare channel inventory, task success/failure, friction/interview themes, response time, and aggregate self-service success.

### 6.6 Escape-hatch diagnostic funnel

```text
Eligible -> aware? -> discoverable? -> capability fit?
         -> onboarding works? -> reliable/fast enough?
         -> trusted and retained?
```

Non-adoption may reflect awareness, discoverability, capability gap, onboarding friction, poor performance, prior breakage, migration cost, support gaps, trust, or mandate resistance. An escape hatch is a product signal, not developer failure.

---

## 7. DORA Metrics by Golden-path Adoption Segment

Reuse M10 Unit 11 definitions/limits. Ask whether services using a supported path show different outcomes; do not rank developers or claim the platform caused the difference.

### 7.1 Outcomes

Lead time for changes, deployment frequency, change failure rate, and time to restore. Keep event definitions consistent with M10 Unit 11. If definitions evolved or event semantics differ, document local policy; never compare unlike measures silently.

### 7.2 Cohort definition

Synthetic adopter: eligible service conformant for the majority of the observation window using monthly snapshots. Non-adopter: eligible service not meeting that rule. Window: six synthetic months. Grain: service-month; report aggregates only. The “majority” threshold is an analytical choice and needs versioning/sensitivity testing.

### 7.3 Naive versus adjusted analysis

| Method | Description | Limitation |
|---|---|---|
| Naive | Compare adopter/non-adopter medians/means | Maturity, age, workload differ |
| Stratified | Compare within maturity/age/workload strata | Unmeasured confounders and small n remain |
| Matched cohort | Match on pre-treatment attributes | Cannot balance unobserved variables; overlap may be poor |
| Difference-in-differences | Compare changes in treated/comparison groups | Requires plausible parallel trends and stable composition |
| Staged rollout | Predeclared eligible rollout groups and guardrails | Critical-path risk; sample may be too small |

### 7.4 Confounders

Team maturity, service age/criticality, workload, incident exposure, migration timing, team size, prior automation, support intensity, and selection bias. Strong teams may adopt first; complex teams may delay. Adoption can be an effect of capability as well as a cause of outcomes.

### 7.5 Difference-in-differences intuition

`[ILLUSTRATIVE]` Adopters move from 10 to 8 days median lead-time proxy; comparison services move from 12 to 11 days. DiD = `(8-10) - (11-12) = -1 day`. Synthetic arithmetic only. It depends on parallel trends and no differential co-intervention. Do not say “the platform saved one day”.

### 7.6 Causal-caution statement

> Segment differences in this report are descriptive associations in synthetic data. They do not establish that golden-path adoption caused delivery outcomes. Team maturity, service age, workload complexity, selection into adoption, concurrent interventions, measurement error, and cohort composition may explain some or all observed differences. The dataset's planted ground truth is known only because it is synthetic; real organizational data requires additional design, validation, and uncertainty analysis.

### 7.7 Simpson's paradox

An aggregate comparison can reverse after stratification. Adopters might have lower failure rates within simple and complex workloads, yet look worse overall because the adopter segment contains more complex services. Inspect composition and within-stratum outcomes.

---

## 8. Developer-Experience Research Methods

Telemetry suggests where friction exists. Research helps explain what it feels like and why. Keep observed facts separate from inferred causes.

### 8.1 Surveys

Use a short, stable instrument with neutral wording and clear anchors:

1. “How easy was it to find the supported path for your task?” (1 = very difficult, 5 = very easy)
2. “How confident were you that generated configuration was safe to deploy?” (1 = not confident, 5 = very confident)
3. “How often did you wait for a platform capability?” (Never / Once / A few times / Many times)
4. “Which step caused the most friction?” (Discovery / Template / CI / Provisioning / Deploy / Verification / Other)
5. “What one change would most improve this workflow?” (optional)

Report invitations, responses, response rate, scale distribution, missing answers, and collection window. A 5-point Likert response is ordinal; do not assume every step is equal. Compare trends only with stable wording/population. Use qualitative follow-up for unexpected changes.

### 8.2 Survey bias and small samples

- **Non-response bias:** respondents differ from non-respondents.
- **Self-selection:** highly satisfied/frustrated people may respond more.
- **Social desirability:** respondents feel pressure to be positive.
- **Question-order effects:** earlier prompts influence later answers.
- **Small-n instability:** a few responses move the distribution sharply.
- **Survivorship bias:** teams that abandoned the path may be absent from current-user surveys.

A survey of 12 responses is “12 responses”, not organization-wide satisfaction. Show counts/distribution, mark exploratory, and avoid overconfident averages.

### 8.3 Interviews and observation

Interview guide:

1. Describe the last time you created or changed a service using the platform.
2. What did you expect at each stage?
3. Where did you wait, retry, ask for help, or use a workaround?
4. What information was difficult to find?
5. What did you not trust, and why?
6. What capability was missing?
7. What would make you choose this path again?

Observation protocol: give a defined task; do not request passwords/private code/customer data; record step, timestamp, visible error, help request, and outcome; separate observation from interpretation; anonymize notes; never evaluate the individual.

Synthetic transcript for coding practice:

> “I found the template, but I was unsure which environment option was safe. CI failed because the generated example referenced an old image. I copied a repository from another team because I needed to finish.”

Possible codes: discovery succeeded; confidence low; template drift; first-CI failure; workaround; trust risk. Do not infer laziness or incompetence.

### 8.4 Friction log and journey map

Learner performs one golden-path task as a new user and records a local `n=1` log:

| Field | Entry |
|---|---|
| Task / starting state | |
| Expected outcome | |
| Step and timestamp | |
| Elapsed / waiting time | |
| Confusion / uncertainty | |
| Retry / error / workaround | |
| Expected vs actual | |
| Severity / frequency / impact | |
| Non-sensitive evidence | |
| Observed fact vs inferred cause | |
| Proposed fix / owner | |

| Journey stage | Developer question | Potential friction | Evidence |
|---|---|---|---|
| Discovery | Where is supported path? | Search/ownership/docs stale | Search task success, catalog freshness |
| Template | Right archetype? | Options unclear, unsafe defaults | Selection errors, observation |
| First commit | What should I change? | Generated config/docs unclear | Time-to-first-commit |
| CI | Why validation failed? | Queue, flaky test, unclear feedback | Queue duration, first-green-CI |
| Provisioning | When usable? | Accepted but not ready, access friction | Ready timestamp, retries |
| First deploy | Is it healthy? | GitOps drift, deploy failure | Verified deployment |
| Production handoff | Who owns operations? | Missing catalog/runbook/alerts | Ownership/readiness checks |

### 8.5 Usability tests

Define task success before observing. Record completion, elapsed time, errors, help requests, and confidence. The learner's before/after runs are both `n=1`; useful for obvious friction, not population estimates. Fix top three observed issues and repeat under comparable conditions. Report learning effects and environment drift.

### 8.6 Support-ticket analysis and funnel

`portal discovery → template generated → first commit → first CI green → first deploy → production-ready`

Calculate transition completion/drop-off for the same cohort/window. A drop-off is not automatically UX failure: some services are ineligible, some tasks are abandoned for valid reasons, and some event sources may be missing.

---

## 9. Measurement Rigor, Causal Caution, and Survey Science

A trustworthy pipeline needs correct arithmetic and defensible measurement design. Precise numbers from biased, incomplete, or unstable events remain misleading.

### 9.1 Metrics as code

Store definitions in version control and review like application code. Include name/question, formula, event grain, numerator/denominator, eligibility/exclusions, timezone/window, source lineage, owner/consumers, data-quality tests, privacy/retention, limitations, version history, and effective date. A change needs compatibility note, test fixture, and history-recalculation decision.

### 9.2 Data-quality checks

Test missing required events, duplicate IDs, timezone-naive timestamps, bots/test traffic, invalid transitions, unknown service IDs, stale catalog snapshots, late events, denominator drift, impossible durations/outliers, and schema drift. Report **FAIL** (unsafe), **WARN** (usable with caveat), or **PASS**. Never silently drop bad rows to improve a KPI.

### 9.3 Data-quality SLO `[ILLUSTRATIVE]`

Example: 99% of required event batches arrive within two hours of event time over rolling 28 days. Justify the target against decision cadence. Measure freshness and completeness separately: a fresh batch can still be incomplete. Alert data owners when missingness/schema drift makes KPIs stale.

### 9.4 Causal caution concepts

- **Selection bias:** early adopters may already be more capable/motivated.
- **Regression to the mean:** intervention follows an unusually bad period; metrics improve without the intervention.
- **Simpson's paradox:** aggregate trends reverse when group composition differs.
- **Before/after limitation:** workload, staffing, incidents, version, and seasonality may change simultaneously.
- **Matched cohorts:** match observed pre-treatment attributes; unobserved confounding remains.
- **Difference-in-differences:** compare changes across treated/comparison groups; parallel trends is critical.
- **A/B or staged rollout:** only when eligible, safe, transparent, and operationally acceptable; no involuntary critical-path experimentation.
- **Small samples:** report counts/ranges/uncertainty; inconclusive is valid.

### 9.5 Experiment design contract

Document question/hypothesis; eligible population/exclusions; treatment/comparison; primary outcome/countermetrics; reliability/security/cost/support guardrails; rollout/rollback; sample/window assumptions; analysis/uncertainty plan; stop condition; communication/privacy review. Predeclare main analysis; label exploratory cuts; do not p-hack.

### 9.6 Survey science

Use stable neutral wording, balanced options, consistent timing, response-rate reporting, and review question order, missingness, and social pressure. Trends are useful only when population and questions remain comparable. No invented industry benchmarks.

---

## 10. Privacy, Ethics, and Anti-gaming Safeguards

Privacy is architectural, not just a dashboard setting. Minimize at source, aggregate early, restrict access, limit retention, and publish the purpose and limits.

### 10.1 Prohibited patterns

Do not collect/publish per-person deployment/commit/ticket counts or productivity scores; leaderboards; keystrokes/screen recordings/editor activity; code/notebook/model/dataset/customer/secret payloads; person-level browsing profiles; or individual-linked survey responses as part of this learning unit. Team/service aggregates can still be sensitive.

### 10.2 Privacy-by-design controls

| Control | Minimum practice | Evidence |
|---|---|---|
| Data minimization | Only fields needed for a named decision | Event schema review |
| Aggregation | Team/service/platform grain; no person-level output | Query/dashboard scanner |
| Minimum group size | Suppress small groups; `[ILLUSTRATIVE]` k=5, context-reviewed | Suppression tests |
| Retention | Purpose-based deletion schedule | Retention policy/deletion log |
| Access | RBAC; raw access narrower than aggregate | Access matrix/audit |
| Transparency | Publish what/why/who/how to challenge | Developer notice |
| Correction | Service owners can challenge inaccurate catalog/metrics | Dispute workflow |
| Ethical review | Review every new event field/dimension | Review record |

A minimum group size is not an anonymity guarantee. Consider differencing, rare combinations, repeated queries, and outside knowledge. Works-council, employment, privacy, and regulatory issues require qualified local advice; this is not legal advice.

### 10.3 Privacy scanner

Lab 7's Plat-Core scanner scans dashboard/query text for prohibited identifiers. Regex is conservative and can false-positive or miss obfuscation. Production requires parsing actual query languages/dashboard schemas, source-level minimization, data-source permissions, and independent review.

Prohibited patterns include `developer_email`, `username`, `user_id`, `employee_id`, `person_id`, `individual_deploy_count`, `keystrokes`, `screen_recording`, `developer_rank`. Safe aggregate dimensions may include `team_id`, `service_id`, `capability`, `template_version`, `month`, subject to threshold/access review.

### 10.4 Goodhart and gaming

| Gaming behavior | Headline improves | Outcome worsens | Countermetric / guardrail |
|---|---|---|---|
| Forced migration | Coverage rises | Satisfaction/incidents worsen | Voluntary adoption, task success, interviews |
| Ticket suppression | Ticket count falls | Developers stop asking for help | Channel inventory, task failure, friction |
| Survey pressure | Satisfaction rises | Trust/response quality falls | Anonymous neutral survey, response rate, interviews |
| Meaningless deploy splitting | Frequency rises | Change quality/risk worsens | Change failure, rollback, impact, definition audit |
| Weakened first-deploy definition | Time appears shorter | No workflow improvement | Versioned event boundary, dual-run |
| Exclude hard cases from SLO | SLI improves | Hard workloads abandoned/unmeasured | Eligibility audit, exclusion register |

Never attach individual incentives/employment decisions to these measures. Targets guide platform learning, not contests.

---

## 11. Dashboards, Feedback Loops, and Roadmap Prioritization

### 11.1 Balanced scorecard

| Dimension | Signals | Guardrail |
|---|---|---|
| Reliability | Journey success, provisioning p95, CI success, catalog freshness, SLO/error budget | Probe freshness/missing data visible |
| Adoption | Eligible coverage, version spread, self-service, retention | Eligibility and voluntary use visible |
| DX | Satisfaction, friction themes, task errors/time, cognitive load | Response rate/sample size shown |
| Delivery | DORA by service adoption segment | Descriptive association only; no people ranking |
| Cost | HCU per service/team/deploy; shared allocation | Assumptions and reliability context visible |
| Security | Policy conformance, secret controls, access review | Never trade controls for adoption |

Do not compress these into one developer-productivity score.

### 11.2 Audience views

- **Executive:** aggregate trends, investment, risks, uncertainty, decisions; no league tables.
- **Service owner:** only own service/team conformance/outcomes subject to threshold; no cross-team ranking.
- **Platform team:** capability reliability, adoption, friction, cost, support, measurement quality.
- **Research:** anonymized themes, sample caveats, controlled evidence links.

### 11.3 Monthly review

Validate data quality/definition versions; review SLO/error budget; inspect eligibility/adoption/cohorts; review friction/usability/support; examine DORA associations/confounders; review cost/security/privacy/team health; decide repair/investigate/continue/simplify/retire; assign owners/dates/re-measurement; publish “you said, we did”.

### 11.4 Quarterly product review

Show failures and uncertainty, not only success stories. A costly capability with low voluntary adoption may need redesign, research, or retirement. A critical capability with low adoption due to missing support may merit investment. Never decide from one score.

### 11.5 Adoption plays

Awareness: design partners/examples. Discoverability: portal search/catalog/docs. Onboarding: migration kits/safe defaults. Capability gap: extend path or support escape hatch. Performance: fix p95/CI/GitOps. Trust: publish incidents/postmortems. Migration cost: compatibility guides. Support: improve ownership/runbooks. Mandate resistance: investigate workflow mismatch. Detailed deprecation policy belongs to M16 Unit 9.

### 11.6 Prioritization

RICE/ICE-style scoring is an illustrative decision aid `[VERIFY]`; scores depend on subjective reach, impact, confidence, effort, and cost. Opportunity-solution trees are awareness-level. Cost of delay may use hypothetical units with explicit assumptions. Balance reliability/debt, developer friction, capability features, security/privacy, data-quality debt, and maintenance. Numeric score never overrides safety or direct evidence.

---

## 12. Platform Cost, Unit Economics, and ROI Uncertainty

Reuse M15 Unit 4. Cost models must be explainable, reconciled, and explicit about shared costs. Cost per active service/successful journey is useful only with stable units and allocation rules.

### 12.1 Cost categories

Platform compute/storage; CI runners/build cache; observability ingestion/storage/query/retention; network/data transfer; verified licensing; engineering/support/on-call time; shared idle and unallocated overhead.

### 12.2 Unit economics

`[ILLUSTRATIVE]` Monthly platform cost 1,200 HCU / 60 active services = simple average 20 HCU/service. This is not every service's actual cost; workloads and shared-cost allocation differ. Preserve direct/shared/idle/unallocated buckets from M15 Unit 4.

Possible units: cost per active service-month, successful journey, self-service request, CI minute, tenant onboarding, or GPU queue context (M15 Unit 12).

### 12.3 Benefit evidence

| Benefit | Evidence | Limitation |
|---|---|---|
| Workflow time reduced | Comparable task timings, stable definition, environment | Sample elapsed time ≠ cash savings |
| Duplicate tooling reduced | Inventory, ownership, usage, retirement proof | Must prove old tools retired |
| Avoidable incidents reduced | Taxonomy, counterfactual, exposure/severity | Difficult to prove; scenario analysis |
| Infrastructure cost reduced | Reconciled allocation/billing + reliability guardrails | Account for shifted costs |
| Reproducibility improved | Conformance, reproducibility tests, drift | Monetization may be speculative |

### 12.4 ROI discipline

Separate measured cost, measured task time, estimated avoided cost, and speculative benefit. Do not multiply one local timing delta by all employees and guessed hourly rate and call it realized savings. Recovered time may not reduce payroll/cash. State what cannot be known.

### 12.5 Scenario model

The executable `roi_model()` in Lab 8 returns cost per active service and a hypothetical time-value scenario, while deliberately returning `roi_claim: NOT_COMPUTED`. Example scenarios below are `[ILLUSTRATIVE]` and are not measurements:

| Scenario | Monthly platform cost | Active services | Adoption share | Minutes/task | Tasks/month | HCU/hour | Cost/service | Hypothetical time-value HCU |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Low | 1,200 | 60 | 0.30 | 5 | 50 | 1.0 | 20 | 4.17 |
| Base | 1,200 | 60 | 0.50 | 10 | 100 | 1.0 | 20 | 16.67 |
| High | 1,200 | 60 | 0.70 | 15 | 150 | 1.0 | 20 | 37.50 |

These are scenario inputs, not realized benefits. Vary one assumption at a time for sensitivity; include a combined stress case if assumptions may move together. Do not subtract hypothetical time-value HCU from platform cost and label the remainder ROI. HCU is a teaching unit, not currency or vendor pricing.

### 12.6 Showback incentives

Showback may improve cost awareness but suppress adoption or encourage shadow accounts. Explain allocation rules, shared-cost handling, disputes, and reliability relationship. Detailed mechanics remain M15 Unit 4.

---

## 13. Data/ML Developer Experience

Measure workflow friction without collecting notebook contents, code, model data, training examples, feature values, or sensitive datasets.

| Measure | Definition | Safe evidence | Caveat |
|---|---|---|---|
| Notebook readiness | Request → usable compliant environment | Synthetic timestamps/environment class | No notebook content/activity |
| Experiment-to-registry | Time/failures to approved registry artifact | Aggregate stage events/status | No weights/prompts/datasets/code |
| Experiment-to-production model | Experiment milestone → verified production handoff | Synthetic model/service IDs/events | Model risk review may be valid wait |
| Pipeline authoring | Task time to create/validate pipeline | Own `n=1` friction log | No skill comparison |
| GPU queue wait | Submit-to-start by queue class | Aggregate timestamps/GPU class | Reuse M15 Unit 12 |
| Data-access lead time | Request → approved usable access | Aggregate approval-stage times | Governance wait may be intentional |
| Dataset discovery | Time/errors locating catalog dataset | Synthetic catalog tasks | Never expose sensitive dataset metadata |
| Local-dev parity | Difference between local/production-like validation | Conformance results | Local parity ≠ production correctness |
| Reproducibility/lineage | Recreate artifact from declared metadata | Synthetic lineage fixture | Respect real data boundaries |
| Perceived cognitive load | Anchored survey distribution | Synthetic survey | Small n/non-response |

Example ML journey: `dataset discovery → access request → notebook ready → experiment → pipeline authored → artifact registered → validation → deployment → monitoring handoff`. Measure wait/completion/retry/failure by aggregate stage. M15 Unit 12 owns GPU scheduling; M16 Units 3–6 own provisioning/catalog/templates/platform APIs.

Safe fields: `team_id`, `service_id`, `workflow_stage`, `environment_class`, `gpu_class`, `duration_seconds`, `outcome`, `error_category`, `schema_version`. Avoid `notebook_text`, `dataset_rows`, `prompt_content`, `model_weights`, `developer_email`, and tokens.

---

## 14. Advanced Measurement Operations and Governance

### 14.1 Metrics charter

```markdown
# Platform Measurement Charter
## Purpose and decisions
- Decisions supported:
- Intended audiences:
## Scope and non-goals
- Capabilities included:
- Explicitly excluded person/activity measures:
## Definitions and owners
- Metric ID/version/definition/owner:
- Sources and lineage:
## Data quality
- Checks, data-quality SLO, failure policy, backfill/late-event rules:
## Privacy and ethics
- Minimization, aggregation threshold [ILLUSTRATIVE], retention, deletion,
  access, transparency, developer challenge route:
## Anti-gaming
- Paired metrics, denominator audit, no individual rankings:
## Governance
- Cadence, definition change, history restatement, incident owner/runbook:
```

### 14.2 Measurement operations

Version event schemas, definitions, tests, dashboards, and reports in Git. Run CI validation before merge. Add freshness/data-quality alerts. Track late events and idempotent backfills. Preserve old definition logic. Restate history only with raw evidence and publish change records. Review dashboard queries/dimensions for privacy. Restrict raw access, audit exports, assign pipeline owner/runbook.

### 14.3 Definition change/history restatement

Record old/new definitions, reason, effective date, numerator/denominator impact, historical recalculation feasibility, parallel-run results, dashboard migration, consumer notification, and approval. If history cannot be reconstructed, show a discontinuity; do not invent backfill.

### 14.4 Quarterly review pack

Goals/outcomes; SLO/error budget/incidents/probe; adoption/eligibility/cohorts/escape hatches; DX research/sample caveats; DORA comparison/causal caution; HCU economics/uncertainty; security/privacy/data quality; failures/unknowns; kill/continue/invest/investigate/simplify decisions; roadmap/owners/dates; “you said, we did”.

### 14.5 Maturity and team health

Use evidence-based self-assessment over time. CNCF maturity models are awareness-only `[VERIFY]`; do not chase levels. Track platform-team on-call load, toil, support backlog, interruptions, and sustainability at team level. No individual on-call rankings or burnout inference from activity telemetry. M10 Units 7/10 own deeper toil/on-call foundations.

### 14.6 External benchmarks and AI-assisted tools

DORA, State of Platform Engineering, SPACE, DevEx, DX Core 4, and vendor-sponsored reports require primary-source verification and context. No benchmark numbers quoted. AI tooling effects are contested; assess privacy, security, attribution, code quality, review load, retention. Do not infer productivity from generated-code volume or assistant usage counts.

### 14.7 Scaling across organizations

Normalize definitions before comparing trajectories. Preserve context: service mix, criticality, regulatory constraints, maturity, platform scope, rollout timing. Avoid league tables. Use justified opt-outs/alternative measures subject to qualified governance. Run recurring “measure experience, not people” audits.

---

## 15. Ten Mandatory Hands-on Labs

All teams, services, events, tickets, and surveys are synthetic. The only exception is Lab 6, which measures the learner's own local task as `n=1`. No cloud account, paid SaaS, external telemetry, or real user data is required.

### Shared lab layout

```text
platform-measurement-lab/
├── data/{events.csv,catalog.csv,tickets.csv,surveys.csv,requests.csv}
├── definitions/{metrics.yaml,slo-suite.md,privacy-charter.md}
├── src/platform_measurement.py
├── tests/test_platform_measurement.py
├── dashboards/{platform-scorecard.json,privacy-negative-fixture.json}
└── reports/{kpi-report.json,causal-caution.md,unit-economics.md,quarterly-review.md}
```

The examples below are teaching files to copy into a learner-owned lab directory. This deliverable remains one Markdown file; those paths are not additional files created by this authoring task.

### Shared Plat-Core implementation (Labs 2–9)

The following Python 3 standard-library program generates six synthetic months, computes basic KPIs and DORA segment summaries, checks data quality, runs a simulated journey, scans for prohibited dashboard fields, and models HCU scenarios. The seed is deterministic. It contains no personal identifiers.

**File: `src/platform_measurement.py`**

```python
from __future__ import annotations
import argparse, csv, json, random, re, statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEED = 20261103
UTC = timezone.utc
TEAMS = ["team-analytics", "team-ml", "team-risk", "team-data", "team-inference", "team-platform"]
MATURITY = dict(zip(TEAMS, [0.85, 0.78, 0.62, 0.70, 0.90, 0.95]))
VERSIONS = ["v1", "v2", "v3"]
START = datetime(2026, 1, 1, tzinfo=UTC)
PROHIBITED = re.compile(
    r"(?i)(developer_email|username|user_id|employee_id|person_id|"
    r"individual_deploy_count|keystrokes|screen_recording|developer_rank|person_name)"
)


def iso(dt):
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_ts(value):
    if not value.endswith("Z") and "+" not in value:
        raise ValueError("timezone required")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generate_dataset(out_dir: Path, seed=SEED):
    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    events, catalog, tickets, surveys, requests = [], [], [], [], []
    eid = 0
    for team in TEAMS:
        for idx in range(1, 6):
            service = f"svc-{team[5:]}-{idx:02d}"
            age = rng.randint(20, 540)
            eligible = idx != 5
            catalog.append({"service_id": service, "team_id": team,
                "eligible": str(eligible).lower(), "retired": "false",
                "service_age_days": age, "workload": "batch" if idx % 2 else "api",
                "maturity": MATURITY[team], "cohort_month": rng.randint(0, 5)})
            for month in range(6):
                month_start = START + timedelta(days=30 * month + rng.randint(0, 20))
                # Planted confounder: mature teams adopt earlier.
                adopted = eligible and rng.random() < min(0.90, 0.12 + MATURITY[team] * 0.48 + month * 0.055)
                version = VERSIONS[min(2, month // 2)] if adopted else "none"
                state = "conformant" if adopted else "non_adopter"
                for j in range(rng.randint(1, 4)):
                    journey = f"j-{service}-{month}-{j}"
                    stages = ["template_generated", "ci_completed", "provisioning_completed", "deploy_completed"]
                    durations = [rng.randint(20, 100), rng.randint(60, 900), rng.randint(90, 1200), rng.randint(30, 300)]
                    failed = rng.random() > (0.76 + (0.10 if adopted else 0))
                    failure_at = rng.randrange(4) if failed else -1
                    cursor = month_start
                    for i, stage in enumerate(stages):
                        eid += 1
                        cursor += timedelta(seconds=durations[i])
                        ok = not failed or i < failure_at
                        if i == failure_at:
                            ok = False
                        events.append({"event_id": f"evt-{eid:07d}", "event_ts": iso(cursor),
                            "event_type": stage, "team_id": team, "service_id": service,
                            "journey_id": journey, "capability": ["template", "ci", "provisioning", "deploy"][i],
                            "template_version": version, "outcome": "success" if ok else "failure",
                            "duration_seconds": durations[i], "golden_path_state": state,
                            "is_synthetic": "true"})
                        if not ok:
                            break
                # Synthetic service-month delivery data with maturity/complexity confounding.
                complexity = 1.0 if idx <= 3 else 1.6
                lead = max(1.0, rng.gauss(9 - 2 * MATURITY[team] - (1 if adopted else 0), 1.8) * complexity)
                deploys = max(1, int(rng.gauss(4 + MATURITY[team] * 4 + (1 if adopted else 0), 1.5)))
                cfr = min(0.7, max(0.0, rng.gauss(0.18 - (0.04 if adopted else 0), 0.06) * complexity))
                restore = max(0.5, rng.gauss(5.5 - MATURITY[team] - (0.5 if adopted else 0), 1.2))
                eid += 1
                events.append({"event_id": f"evt-{eid:07d}", "event_ts": iso(month_start + timedelta(days=28)),
                    "event_type": "service_month_outcome", "team_id": team, "service_id": service,
                    "journey_id": f"month-{service}-{month}", "template_version": version,
                    "golden_path_state": state, "lead_time_days": round(lead, 3),
                    "deployments": deploys, "change_failure_rate": round(cfr, 4),
                    "time_to_restore_hours": round(restore, 3), "month_index": month,
                    "service_age_days": age, "team_maturity": MATURITY[team],
                    "workload": "batch" if idx % 2 else "api",
                    "escape_hatch": str((not adopted) and rng.random() < 0.22).lower(),
                    "onboarding_seconds": rng.randint(300, 7200),
                    "platform_api_version": f"api-v{1 + (month // 3)}", "is_synthetic": "true"})
                if rng.random() < 0.12:
                    eid += 1
                    events.append({"event_id": f"evt-{eid:07d}", "event_ts": iso(month_start + timedelta(days=25)),
                        "event_type": "incident", "team_id": team, "service_id": service,
                        "journey_id": f"incident-{service}-{month}", "outcome": "failure",
                        "error_category": rng.choice(["provisioning", "ci", "gitops", "catalog"]),
                        "severity": rng.choice(["SEV2", "SEV3"]), "is_synthetic": "true"})
                if rng.random() < 0.35:
                    tickets.append({"ticket_id": f"t-{service}-{month}", "service_id": service,
                        "team_id": team, "month_index": month,
                        "category": rng.choice(["provisioning", "ci", "docs", "access", "catalog"]),
                        "first_response_hours": round(rng.uniform(0.2, 12), 2),
                        "resolution_hours": round(rng.uniform(1, 48), 2), "is_synthetic": "true"})
                for request_no in range(rng.randint(1, 3)):
                    requests.append({"request_id": f"req-{service}-{month}-{request_no}",
                        "service_id": service, "team_id": team, "month_index": month,
                        "channel": "self_service" if rng.random() < 0.68 else "manual",
                        "status": "completed" if rng.random() < 0.91 else "failed",
                        "is_synthetic": "true"})
        # Planted non-response bias: response probability varies with maturity.
        for month in range(6):
            invited = 5
            responded = sum(rng.random() < 0.25 + 0.55 * MATURITY[team] for _ in range(invited))
            for _ in range(responded):
                surveys.append({"team_id": team, "month_index": month,
                    "satisfaction_1_to_5": rng.choice([2, 3, 3, 4, 4, 5]),
                    "cognitive_load_1_to_5": rng.choice([1, 2, 3, 3, 4]),
                    "confidence_1_to_5": rng.choice([2, 3, 4, 4, 5]), "is_synthetic": "true"})
    for name, rows in [("events.csv", events), ("catalog.csv", catalog),
                       ("tickets.csv", tickets), ("surveys.csv", surveys), ("requests.csv", requests)]:
        write_csv(out_dir / name, rows)
    return {"events": len(events), "catalog": len(catalog), "tickets": len(tickets),
            "surveys": len(surveys), "requests": len(requests), "seed": seed, "synthetic": True}


def quality_report(events, catalog):
    ids = [e.get("event_id") for e in events]
    duplicates = [k for k, n in Counter(ids).items() if n > 1]
    missing = [i for i, e in enumerate(events) if not e.get("event_id") or not e.get("event_ts") or not e.get("event_type")]
    bad_time = []
    for i, e in enumerate(events):
        try:
            parse_ts(e["event_ts"])
        except Exception:
            bad_time.append(i)
    known = {c["service_id"] for c in catalog}
    unknown_service = [i for i, e in enumerate(events) if e.get("service_id") not in known]
    bad_duration = []
    for i, e in enumerate(events):
        try:
            if e.get("duration_seconds") not in (None, "") and float(e["duration_seconds"]) < 0:
                bad_duration.append(i)
        except (TypeError, ValueError):
            bad_duration.append(i)
    allowed = {"template_generated", "ci_completed", "provisioning_completed", "deploy_completed"}
    by_journey = defaultdict(list)
    for e in events:
        if e.get("event_type") in allowed:
            by_journey[e.get("journey_id")].append(e.get("event_type"))
    order = ["template_generated", "ci_completed", "provisioning_completed", "deploy_completed"]
    invalid_transitions = []
    for journey, stages in by_journey.items():
        positions = [order.index(x) for x in stages]
        if positions != sorted(positions) or len(positions) != len(set(positions)):
            invalid_transitions.append(journey)
    bot_rows = [i for i, e in enumerate(events) if str(e.get("is_bot", "false")).lower() == "true"]
    test_rows = [i for i, e in enumerate(events) if str(e.get("is_test", "false")).lower() == "true"]
    stale_catalog = [i for i, c in enumerate(catalog) if str(c.get("catalog_stale", "false")).lower() == "true"]
    warnings = []
    if bot_rows: warnings.append("bot traffic must be excluded")
    if test_rows: warnings.append("test traffic must be excluded")
    if stale_catalog: warnings.append("catalog snapshot is stale")
    failed = any([duplicates, missing, bad_time, unknown_service, bad_duration, invalid_transitions])
    status = "FAIL" if failed else ("WARN" if warnings else "PASS")
    return {"duplicate_ids": duplicates, "missing_rows": missing, "bad_timestamps": bad_time,
            "unknown_services": unknown_service, "negative_or_invalid_durations": bad_duration,
            "invalid_state_transitions": invalid_transitions, "bot_rows_to_exclude": bot_rows,
            "test_traffic_rows_to_exclude": test_rows, "stale_catalog_rows": stale_catalog,
            "warnings": warnings, "status": status}


def calculate_kpis(events, catalog, tickets=None, requests=None):
    tickets = tickets or []
    requests = requests or []
    eligible = [c for c in catalog if c["eligible"] == "true" and c["retired"] != "true"
                and str(c.get("is_test", "false")).lower() != "true"]
    service_rows = defaultdict(list)
    for e in events:
        if str(e.get("is_bot", "false")).lower() == "true" or str(e.get("is_test", "false")).lower() == "true":
            continue
        if e.get("event_type") == "service_month_outcome":
            service_rows[e["service_id"]].append(e)
    latest = {sid: sorted(rows, key=lambda r: int(r["month_index"]))[-1] for sid, rows in service_rows.items()}
    conformant = sum(latest.get(c["service_id"], {}).get("golden_path_state") == "conformant" for c in eligible)
    adopted = [c for c in eligible if latest.get(c["service_id"], {}).get("golden_path_state") == "conformant"]
    journeys = defaultdict(list)
    for e in events:
        if e.get("event_type") in {"template_generated", "ci_completed", "provisioning_completed", "deploy_completed"}:
            journeys[e["journey_id"]].append(e)
    successful = sum(len(rows) == 4 and all(r["outcome"] == "success" for r in rows) for rows in journeys.values())
    versions = Counter(cast.get("template_version", "unknown") for cast in latest.values() if cast.get("golden_path_state") == "conformant")
    api_versions = Counter(cast.get("platform_api_version", "unknown") for cast in latest.values() if cast.get("golden_path_state") == "conformant")
    escape_count = sum(latest.get(c["service_id"], {}).get("escape_hatch") == "true" for c in eligible)
    onboarding = [int(latest[c["service_id"]]["onboarding_seconds"]) for c in eligible if c["service_id"] in latest]
    cohort_counts = defaultdict(lambda: {"eligible": 0, "adopted": 0})
    for c in eligible:
        cohort = str(c.get("cohort_month", "unknown"))
        cohort_counts[cohort]["eligible"] += 1
        if latest.get(c["service_id"], {}).get("golden_path_state") == "conformant":
            cohort_counts[cohort]["adopted"] += 1
    completed_requests = [r for r in requests if r.get("status") == "completed"
                          and str(r.get("is_bot", "false")).lower() != "true"
                          and str(r.get("is_test", "false")).lower() != "true"]
    ss = sum(r.get("channel") == "self_service" for r in completed_requests)
    manual = sum(r.get("channel") == "manual" for r in completed_requests)
    first_adopters = [sid for sid, rows in service_rows.items()
                      if any(int(r.get("month_index", 99)) == 0 and r.get("golden_path_state") == "conformant" for r in rows)]
    retained = sum(latest.get(sid, {}).get("golden_path_state") == "conformant" for sid in first_adopters)
    return {"eligible_services": len(eligible), "conformant_services": conformant,
        "golden_path_coverage": conformant / len(eligible) if eligible else None,
        "template_version_spread": dict(versions), "platform_api_version_spread": dict(api_versions),
        "self_service_ratio": ss / (ss + manual) if ss + manual else None,
        "completed_self_service_requests": ss, "completed_manual_requests": manual,
        "journeys": len(journeys), "successful_journeys": successful,
        "journey_success_ratio": successful / len(journeys) if journeys else None,
        "time_to_first_deploy_seconds_median": statistics.median([
            sum(float(e.get("duration_seconds", 0) or 0) for e in rows)
            for rows in journeys.values() if len(rows) == 4 and all(e["outcome"] == "success" for e in rows)
        ]) if successful else None,
        "onboarding_time_seconds_median": statistics.median(onboarding) if onboarding else None,
        "ticket_count": len(tickets), "incident_event_count": sum(e.get("event_type") == "incident" for e in events),
        "ticket_rate_per_eligible_service": len(tickets) / len(eligible) if eligible else None,
        "ticket_categories": dict(Counter(t.get("category", "unknown") for t in tickets)),
        "median_ticket_first_response_hours": statistics.median([float(t["first_response_hours"]) for t in tickets]) if tickets else None,
        "median_ticket_resolution_hours": statistics.median([float(t["resolution_hours"]) for t in tickets]) if tickets else None,
        "escape_hatch_rate": escape_count / len(eligible) if eligible else None,
        "retention_cohort_month_0_to_latest": retained / len(first_adopters) if first_adopters else None,
        "cohort_adoption": {k: (v["adopted"] / v["eligible"] if v["eligible"] else None) for k, v in cohort_counts.items()},
        "synthetic_only": True,
        "limitation": "Self-service ratio uses a synthetic channel-complete request fixture; validate channel coverage and event semantics before production."}


def denominator_drift(previous_count, current_count, threshold=0.10):
    if previous_count <= 0:
        return {"status": "UNKNOWN", "reason": "previous denominator missing or zero"}
    change = abs(current_count - previous_count) / previous_count
    return {"status": "WARN" if change > threshold else "PASS",
            "relative_change": round(change, 4), "threshold": threshold}


def dora_summary(events):
    rows = [e for e in events if e.get("event_type") == "service_month_outcome"]
    result = {}
    for segment in ["conformant", "non_adopter"]:
        subset = [r for r in rows if r["golden_path_state"] == segment]
        result[segment] = ({"n": 0, "status": "INCONCLUSIVE"} if not subset else {
            "n": len(subset), "median_lead_time_days": statistics.median(float(r["lead_time_days"]) for r in subset),
            "mean_deployments": statistics.mean(float(r["deployments"]) for r in subset),
            "mean_change_failure_rate": statistics.mean(float(r["change_failure_rate"]) for r in subset),
            "median_restore_hours": statistics.median(float(r["time_to_restore_hours"]) for r in subset),
            "status": "DESCRIPTIVE_SYNTHETIC_ONLY"})
    return {"segments": result, "causal_caution": "Descriptive association only; maturity, age, workload and selection confound."}


def privacy_scan(text):
    return sorted(set(m.group(0) for m in PROHIBITED.finditer(text)))


def run_journey(fail_stage=None):
    durations = {"generate": 2, "ci_equivalent": 5, "deploy": 3, "verify": 1, "teardown": 1}
    rows, failed, elapsed = [], False, 0
    for stage, duration in durations.items():
        elapsed += duration
        outcome = "failure" if stage == fail_stage else "success"
        rows.append({"stage": stage, "duration_seconds": duration, "outcome": outcome})
        if outcome == "failure":
            failed = True
            break
    cleanup = {"attempted": True, "outcome": "success"}
    return {"stages": rows, "elapsed_seconds": elapsed, "cleanup": cleanup,
            "journey_success": not failed and len(rows) == len(durations), "synthetic_simulation": True}


def roi_model(monthly_cost_hcu, active_services, adoption_share, task_minutes, monthly_tasks, hcu_per_hour):
    if monthly_cost_hcu < 0 or active_services <= 0 or not 0 <= adoption_share <= 1:
        raise ValueError("invalid cost, service count, or adoption share")
    if min(task_minutes, monthly_tasks, hcu_per_hour) < 0:
        raise ValueError("negative scenario input")
    return {"cost_per_active_service_hcu": round(monthly_cost_hcu / active_services, 3),
        "adopted_services_scenario": active_services * adoption_share,
        "hypothetical_time_value_hcu": round(task_minutes / 60 * monthly_tasks * hcu_per_hour, 3),
        "roi_claim": "NOT_COMPUTED", "classification": "HYPOTHETICAL_NOT_MEASURED_CASH_SAVINGS",
        "what_cannot_be_known": ["whether time becomes cash savings", "whether avoided incidents would occur"]}


def survey_summary(surveys):
    invited = len(TEAMS) * 6 * 5  # generator's documented invitation fixture
    return {"invited": invited, "responses": len(surveys),
        "response_rate": len(surveys) / invited if invited else None,
        "satisfaction_mean": round(statistics.mean(int(r["satisfaction_1_to_5"]) for r in surveys), 3) if surveys else None,
        "confidence_mean": round(statistics.mean(int(r["confidence_1_to_5"]) for r in surveys), 3) if surveys else None,
        "cognitive_load_mean": round(statistics.mean(int(r["cognitive_load_1_to_5"]) for r in surveys), 3) if surveys else None,
        "evidence_class": "SYNTHETIC ONLY; response propensity is planted by team maturity"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["generate", "report", "journey", "scan"])
    p.add_argument("--out", type=Path, default=Path("data"))
    p.add_argument("--fail-stage")
    p.add_argument("--file", type=Path)
    a = p.parse_args()
    if a.command == "generate":
        print(json.dumps(generate_dataset(a.out), indent=2))
    elif a.command == "report":
        events, catalog = read_csv(a.out / "events.csv"), read_csv(a.out / "catalog.csv")
        tickets = read_csv(a.out / "tickets.csv")
        requests = read_csv(a.out / "requests.csv")
        surveys = read_csv(a.out / "surveys.csv")
        report = {"quality": quality_report(events, catalog), "kpis": calculate_kpis(events, catalog, tickets, requests),
                  "dora": dora_summary(events), "survey": survey_summary(surveys),
                  "evidence_class": "SYNTHETIC ONLY"}
        (a.out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
    elif a.command == "journey":
        print(json.dumps(run_journey(a.fail_stage), indent=2))
    else:
        if not a.file:
            p.error("scan requires --file")
        findings = privacy_scan(a.file.read_text(encoding="utf-8"))
        print(json.dumps({"findings": findings, "status": "FAIL" if findings else "PASS"}, indent=2))
        if findings:
            raise SystemExit(2)

if __name__ == "__main__":
    main()
```

**File: `tests/test_platform_measurement.py`**

```python
import tempfile
import unittest
from pathlib import Path
from src.platform_measurement import (generate_dataset, read_csv, quality_report,
    privacy_scan, run_journey, roi_model, denominator_drift, survey_summary)

class MeasurementTests(unittest.TestCase):
    def test_seed_is_reproducible_and_has_six_months(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            generate_dataset(Path(a), 123); generate_dataset(Path(b), 123)
            x = read_csv(Path(a) / "events.csv"); y = read_csv(Path(b) / "events.csv")
            self.assertEqual(x, y)
            months = {r["month_index"] for r in x if r["event_type"] == "service_month_outcome"}
            self.assertEqual(months, {"0", "1", "2", "3", "4", "5"})

    def test_duplicate_missing_and_bad_timestamp_detected(self):
        rows = [{"event_id":"x", "event_ts":"2026-01-01T00:00:00Z", "event_type":"a", "service_id":"s"},
                {"event_id":"x", "event_ts":"2026-01-01T00:00:00Z", "event_type":"a", "service_id":"s"},
                {"event_id":"", "event_ts":"bad", "event_type":"", "service_id":"unknown"}]
        q = quality_report(rows, [{"service_id":"s"}])
        self.assertEqual(q["status"], "FAIL")
        self.assertTrue(q["duplicate_ids"] and q["missing_rows"] and q["bad_timestamps"])

    def test_bot_test_stale_catalog_and_denominator_drift_are_visible(self):
        events = [{"event_id":"b", "event_ts":"2026-01-01T00:00:00Z", "event_type":"probe", "service_id":"s", "is_bot":"true"},
                  {"event_id":"t", "event_ts":"2026-01-01T00:00:00Z", "event_type":"probe", "service_id":"s", "is_test":"true"}]
        q = quality_report(events, [{"service_id":"s", "catalog_stale":"true"}])
        self.assertEqual(q["status"], "WARN")
        self.assertTrue(q["bot_rows_to_exclude"] and q["test_traffic_rows_to_exclude"] and q["stale_catalog_rows"])
        self.assertEqual(denominator_drift(100, 125)["status"], "WARN")
        self.assertEqual(denominator_drift(0, 10)["status"], "UNKNOWN")

    def test_invalid_transition_is_detected(self):
        rows = [{"event_id":"1", "event_ts":"2026-01-01T00:00:00Z", "event_type":"deploy_completed", "service_id":"s", "journey_id":"j"},
                {"event_id":"2", "event_ts":"2026-01-01T00:01:00Z", "event_type":"template_generated", "service_id":"s", "journey_id":"j"}]
        q = quality_report(rows, [{"service_id":"s"}])
        self.assertEqual(q["status"], "FAIL")
        self.assertTrue(q["invalid_state_transitions"])

    def test_survey_summary_reports_denominator_and_synthetic_status(self):
        result = survey_summary([{"satisfaction_1_to_5":"4", "confidence_1_to_5":"4", "cognitive_load_1_to_5":"2"}])
        self.assertEqual(result["invited"], 180)
        self.assertEqual(result["responses"], 1)
        self.assertIn("SYNTHETIC", result["evidence_class"])

    def test_journey_failure_is_not_success_and_cleanup_is_attempted(self):
        self.assertTrue(run_journey()["journey_success"])
        failed = run_journey("deploy")
        self.assertFalse(failed["journey_success"])
        self.assertTrue(failed["cleanup"]["attempted"])

    def test_privacy_scanner_safe_and_unsafe(self):
        self.assertEqual(privacy_scan('{"team_id":"team-a"}'), [])
        self.assertTrue(privacy_scan('{"username":"fake","developer_rank":1}'))

    def test_roi_never_claims_cash(self):
        result = roi_model(1200, 60, .5, 10, 100, 1)
        self.assertEqual(result["roi_claim"], "NOT_COMPUTED")
        with self.assertRaises(ValueError):
            roi_model(100, 0, .5, 10, 100, 1)

if __name__ == "__main__":
    unittest.main()
```

Run from the project root:

```bash
python -m src.platform_measurement generate --out data
python -m src.platform_measurement report --out data
python -m src.platform_measurement journey
python -m unittest discover -s tests -v
```

Representative output shape (not observed output):

```json
{"events":"<deterministic count>","catalog":30,"tickets":"<deterministic count>","surveys":"<deterministic count>","requests":"<deterministic count>","seed":20261103,"synthetic":true}
```

### Lab 1 — Platform SLO suite and developer-journey probe

**Objective:** Define at least six SLIs/SLOs, owners/windows/error-budget actions, and a synthetic generate → CI-equivalent → deploy → verify → teardown probe.

**Profile/prerequisites:** Plat-Core required; Plat+Control optional. Reuse M10 Unit 1 and M11 Unit 3. No cluster required.

**Safety:** Synthetic IDs only; no usernames, source code, secrets, or production endpoints. Use disposable cluster only for extension.

**Files:** `definitions/slo-suite.md`, `src/platform_measurement.py`, `reports/journey-run.json`, `dashboards/platform-scorecard.json`.

**Steps:** choose six capabilities; complete the SLO template; define good/valid events and missing-data behavior; mark targets `[ILLUSTRATIVE]`; run `journey`; inject `--fail-stage deploy`; write dashboard spec; optionally run `promtool check rules`; record actual timing only for a real local journey with hardware/software metadata.

**Positive tests:** six complete SLOs; default journey completes. **Negative tests:** missing stage, failure, absent telemetry, failed cleanup, and no traffic never report success.

**Expected:** deterministic simulation reports success normally and failure on injected deploy fault; these are not cluster observations.

**Cleanup:** Plat-Core creates no external resources. Delete unique `kind` cluster and verify no lab namespace/deployment/image remains.

**Evidence/acceptance:** six SLO docs, probe JSON, dashboard spec, version log, tests, limitations. **Limit:** simulation does not prove live integrations.

### Lab 2 — Six-month synthetic dataset generator

**Objective:** Generate six months of events across synthetic teams with varying maturity, adoption, CI/deploys, tickets, and surveys.

**Profile/prerequisites:** Plat-Core, Python 3.11+ recommended; no external packages. **Safety:** never merge real company/developer records.

**Files:** `data/events.csv`, `catalog.csv`, `tickets.csv`, `surveys.csv`, `reports/generator-manifest.json`.

**Steps:** copy code/tests; run `generate`; inspect headers and event types; verify month indices 0–5; run twice with same seed and compare; change seed and confirm data changes but schema stays; document planted confounders.

**Positive:** six months; `is_synthetic=true`; deterministic same-seed output. **Negative:** remove required field/duplicate ID and verify Lab 3 detects it.

**Expected:** manifest contains seed/counts/synthetic marker; do not guess counts. **Cleanup:** remove generated synthetic `data/`. **Evidence:** manifest, schema, seed, ground truth, test output. **Limit:** known planted confounders are not representative of real organizations.

### Lab 3 — Adoption KPI pipeline and data-quality tests

**Objective:** Calculate coverage, version spread, self-service ratio, first-deploy time, onboarding, tickets, escape hatches, retention, cohorts; gate on data quality.

**Profile/prerequisites:** Plat-Core; Lab 2. **Safety:** synthetic aggregate only.

**Files:** shared script/tests, `reports/kpi-report.json`, `reports/data-quality.json`, `definitions/metrics.yaml`.

**Steps:** run report; define each KPI; add duplicate row and missing event; add timezone-naive timestamp; add bot/test service; add unknown service/stale catalog; add invalid state transition; compare catalog denominator month-to-month; report value, numerator, denominator, grain, window, quality, caveat.

**Positive:** correct eligibility; ratios in [0,1]; timezone/cohort explicit. **Negative:** duplicates, missingness, timezone, bots, stale catalog, unknown service, impossible duration, invalid transition, denominator drift caught.

**Expected:** report contains quality/KPI/DORA sections. Generator includes a synthetic manual/self-service request fixture; validate channel completeness before production. **Cleanup:** remove copied defect fixtures/reports. **Evidence:** definitions, outputs, defects, tests. **Limit:** teaching pipeline, not warehouse-grade ETL.

### Lab 4 — DORA by adoption segment with confounder analysis

**Objective:** Compare synthetic adopter/non-adopter outcomes and show naive comparisons mislead.

**Profile/prerequisites:** Plat-Core, Labs 2–3, M10 Unit 11. **Safety:** service-month aggregates only.

**Files:** `reports/dora-segment-report.json`, `causal-caution.md`, `definitions/segment-policy.md`.

**Steps:** run report; group service-month outcomes by conformance; report n, lead-time median, deployment mean, CFR mean, restore median; stratify by maturity/age/workload; define matched cohort from pre-adoption variables; record unmatched cases; calculate a synthetic DiD example; add causal-caution statement.

**Positive:** M10 definitions reused, n shown, missing segment = `INCONCLUSIVE`. **Negative:** no causal verbs without design; confounders listed.

**Expected:** `DESCRIPTIVE_SYNTHETIC_ONLY`. **Cleanup:** synthetic reports only. **Evidence:** segment rule, n, naive/stratified table, match criteria, DiD assumptions, uncertainty. **Limit:** base code is descriptive, not a matched estimator.

### Lab 5 — Survey instrument and synthetic survey analysis

**Objective:** Design neutral survey; analyze response rate, distribution, trend, uncertainty, non-response, small-n.

**Profile/prerequisites:** Plat-Core, Lab 2. **Safety:** synthetic responses only.

**Files:** `definitions/survey.md`, `data/surveys.csv`, `reports/survey-analysis.md`.

**Steps:** use Section 8 instrument; document invite population/window/anchors/anonymity; calculate response rate from invitations; report distribution and missingness; compare monthly waves with n; discuss non-responders; include n=12 synthetic illustration; propose qualitative follow-up.

**Positive:** denominator, synthetic label, n, response rate. **Negative:** reject “organization-wide satisfaction” from 12 responses; missing invitation denominator => `UNKNOWN`. **Cleanup:** synthetic files only. **Evidence:** instrument, report, response rate, bias caveat. **Limit:** synthetic response process cannot estimate real sentiment.

### Lab 6 — Friction log and usability test

**Objective:** Learner performs own golden-path task, logs friction, fixes top three issues, re-measures.

**Profile/prerequisites:** local M16 golden path or documented equivalent. If walkthrough only, label simulated, not observed.

**Safety:** only own local task, `n=1` both times; no keystrokes, recordings, personal/confidential data.

**Files:** `reports/friction-log-before.md`, `friction-log-after.md`, `fix-prioritization.md`.

**Steps:** choose task; record start state/environment/hardware/software; perform as new user; log steps/waits/errors/confusion/workarounds; separate observation/hypothesis; prioritize; fix top three in local copy/mock only; repeat same task/conditions; compare and note learning/environment effects.

**Positive:** task definition and metadata; observed/inferred separated; both runs n=1. **Negative:** no population generalization, productivity claim, or cash conversion. **Expected:** logs and top-three fixes; timing only from actual run. **Cleanup:** revert temporary changes/delete temporary environment. **Evidence:** before/after logs and n=1 caveat. **Limit:** one learner cannot estimate population or causality.

### Lab 7 — Privacy and ethics controls

**Objective:** Enforce aggregate reporting, configurable minimum group size/retention, and scanner catching person-level fields.

**Profile/prerequisites:** Plat-Core. **Safety:** fake field names only, no real personal data.

**Files:** privacy charter, safe dashboard fixture, negative fixture, scan report.

**Steps:** define purpose/fields/access/retention/deletion/threshold/transparency/challenge; create safe `team_id/service_id/capability/month` dashboard; scan (expect pass); plant `username`, `developer_email`, `individual_deploy_count`, `developer_rank`; scan (expect nonzero exit); add alias tests; review differencing/access/retention.

**Positive:** safe fixture passes and small groups suppressed. **Negative:** person-level fixture fails. **Cleanup:** delete or clearly label negative fixture. **Evidence:** charter, scan outputs, tests, threshold rationale, access matrix. **Limit:** regex is not a privacy proof; production requires parser/source/access review.

### Lab 8 — ROI and unit economics model

**Objective:** Build HCU scenarios, sensitivity, assumption register, tests, and explicit “what we cannot know”.

**Profile/prerequisites:** Plat-Core, M15 Unit 4. **Safety:** HCU only; no real prices/payroll/invoices.

**Files:** `reports/unit-economics.md`, `definitions/assumption-register.yaml`, tests.

**Steps:** choose hypothetical cost/services/adoption/time/task-volume/HCU rate; call `roi_model`; vary low/base/high assumptions; calculate cost per service and scenario time value; separate measured local timing from hypothetical volume; sensitivity analysis; list unknown cash/avoided incidents/counterfactual; prohibit ROI percentage.

**Positive:** arithmetic reconciles and assumptions have status/owner. **Negative:** reject negative inputs and “measured cash savings” from scenario. **Expected:** `roi_claim: NOT_COMPUTED`. **Cleanup:** no external resources. **Evidence:** scenarios/sensitivity/assumptions/unknowns. **Limit:** not accounting advice or proof of ROI.

### Lab 9 — Goodhart/gaming simulation

**Objective:** Simulate adoption mandate, ticket avoidance, survey pressure, and meaningless deploy splitting; redesign measures.

**Profile/prerequisites:** Plat-Core, Sections 3/10/11. **Safety:** no employee targets/compensation.

**Files:** `reports/gaming-simulation.md`, `measurement-redesign-memo.md`.

**Steps:** create four scenarios; record headline/countermetric before/after; add qualitative check and transparency measure; design paired metrics and denominator audit; write memo removing individual activity measures/single score; assign review cadence/owner.

**Positive:** each scenario has countermetric, qualitative check, transparency, guardrail. **Negative:** reject developer ranking, forced adoption for target, ticket suppression. **Cleanup:** synthetic reports only. **Evidence:** table, memo, owner. **Limit:** plausible scenarios, not behavioral prediction.

### Lab 10 — Quarterly platform review pack

**Objective:** Produce capstone quarterly review covering reliability/adoption/DX/cost/security/privacy/risks/uncertainty and decisions.

**Profile/prerequisites:** Labs 1–9 and M16 Units 1–7. **Safety:** synthetic evidence only.

**Files:** `reports/quarterly-review.md`, `you-said-we-did.md`, `roadmap-priorities.md`.

**Steps:** state goals; include SLO/budget/probe/data quality; adoption denominator/cohorts/voluntary caveat; DX research/n; DORA caution; HCU assumptions; security/privacy; decide kill/continue/invest/investigate for three capabilities; prioritize with explicit assumptions; publish owner/action/next measurement.

**Positive:** decisions cite evidence/limits; synthetic label and owners/dates. **Negative:** no fabricated ROI, ranking, causal claim, or benchmark. **Cleanup:** local report only; no infra remains. **Evidence:** review pack/decisions/risk/roadmap/feedback. **Limit:** process simulation, not platform impact proof.

---

## 16. Troubleshooting and Measurement Failure Cases

| Symptom | Diagnosis | Safe mitigation | Recovery | Regression test |
|---|---|---|---|---|
| SLO green, journey fails | Component SLI excludes readiness | Mark journey degraded; pause risky rollout if required | Redefine good event/add probe | Inject unusable environment |
| Provisioning events missing/double | Async completion lost/retries duplicate | Mark KPI unknown/quality fail | Idempotent IDs/reconciliation | Duplicate/missing fixture fails |
| First-deploy time changed | Definition boundary changed | Freeze trend interpretation | Version/dual-run/restatement if valid | Definition version test |
| Catalog staleness corrupts denominator | Snapshot late/missing records | Mark denominator stale | Refresh/show stale separately | Stale fixture warns |
| Bots inflate usage | Automation not filtered | Exclude known test traffic with audit | Source classification | Bot fixture excluded |
| Timezone shifts cohort | Naive/local timestamps | Stop cohort report | Normalize UTC/backfill if safe | Naive timestamp rejected |
| Adoption rises, first deploy flat | Output without outcome | Do not declare success | Funnel + qualitative research | Pair metrics required |
| DORA shifts after maturity split | Confounding/composition | Descriptive only | Stratify/match, disclose uncertainty | Confounder list required |
| Survey response rate falls | Non-response/channel fatigue | Report n/rate | Qualitative follow-up | Invitation denominator required |
| Small-n generalized | Overclaim | Correct report/notify | Show distribution/exploratory status | Small-n claim lint |
| Tickets fall after channel move | Channel migration | Freeze friction-improved claim | Inventory channels | Channel inventory required |
| Telemetry misses friction | Qualitative blind spot | Preserve observation | Interview/observe | Link research evidence |
| Prometheus rule incompatible | Version/schema mismatch | Do not deploy | Check docs/`promtool` | CI rule check |
| Dashboard has usernames | Privacy failure | Remove/restrict; preserve audit | Scanner/source minimization/review | Negative fixture fails |
| Scanner misses alias | Regex/query parsing gap | Treat scanner insufficient | Parse query AST/schema | Obfuscation tests |
| ROI treats time as cash | Category error | Retract/correct claim | Separate time/value/cash | ROI test forbids cash claim |
| Target gamed | Incentive design failure | Stop target-based reward | Paired metrics/review | Gaming scenario test |
| Quality pipeline fails | Event integrity issue | Mark metric invalid | Repair/backfill with lineage | Defect fixtures fail |
| Dashboard/report disagree | Window/filter/timezone/cache/version | Mark discrepancy | Trace lineage/align definitions | Golden-query comparison |
| Probe leaks resources | Teardown/idempotency defect | Stop repeat runs | Inventory and clean resources | Forced failure still cleans |
| Stack exceeds laptop | Too many components/cardinality | Stop optional services; Plat-Core | Start one component at a time | Preflight/resource check |

### 16.1 Incident ordering

Protect developers/users; stop harmful rollout or unsafe dashboard exposure; communicate; assess metric/decision blast radius; preserve evidence/definition versions; repair instrumentation/definitions/access/incentives; restate history only when justified; add regression controls; publish changes and unknowns.

---

## 17. Review Questions and Exercises

### 17.1 Review questions with model answers

1. **Why can a healthy portal still mean platform failure?** Component health does not prove discoverability, task completion, usable provisioning, or adoption; measure the journey and workarounds.
2. **Three measure families?** Reliability, adoption/usage, DX/outcomes; they answer different questions.
3. **Why is template generation an output?** It records artifact creation; outcome is safe first deployment/reduced friction.
4. **Golden-path denominator?** Eligible services in authoritative snapshot/window after documented exclusions.
5. **Why is HTTP acceptance insufficient?** Async provisioning may not reach usable readiness.
6. **What if telemetry is missing?** Unknown/quality fail per contract, never assumed success/zero.
7. **Why pair adoption with first-deploy and escape-hatch?** Mandates/weak definitions can raise adoption while outcomes worsen.
8. **Selection bias?** Adopters may differ in maturity/motivation before adopting.
9. **DiD assumptions?** Plausible parallel trends, stable composition, no differential co-intervention.
10. **Why not generalize survey n=12?** Small, self-selected/non-response-biased sample; report 12 responses only.
11. **Why can fewer tickets mislead?** Support channel moved or users avoid help; compare channel inventory/task outcomes.
12. **Simpson's paradox?** Aggregate trend reverses after grouping by composition; inspect strata.
13. **Why no per-person deploy counts?** Surveillance, gaming, invalid productivity proxy; use platform/service evidence.
14. **Safe provisioning SLO burn response?** Validate telemetry, assess impact, pause risky changes per policy, prioritize reliability, communicate.
15. **Measured time vs cash savings?** Elapsed task time is not proof costs were reduced.
16. **Why version metric definitions?** Silent changes break comparability and manufacture improvement.
17. **Minimum group threshold purpose?** Reduce disclosure risk, not guarantee anonymity.
18. **Why no ROI claim from synthetic data?** No real usage/cost/counterfactual/business evidence.
19. **What does journey SLI add?** Measures complete task across integrations/readiness.
20. **How respond to escape hatch?** Investigate fit, reliability, migration, discoverability, trust/support.
21. **Why DORA by service adoption not individual?** Service outcomes inform platform design; person-level activity creates surveillance.
22. **What does privacy scanner prove?** Only detection of defined patterns in parsed inputs; not privacy assurance.
23. **Why report survey response rate?** Respondents may not represent invite population.
24. **When is inconclusive valid?** Poor quality, small sample, no overlap, or weak design.
25. **What is “you said, we did”?** Theme, action/reason, owner, status, next measurement date.
26. **Why no productivity composite?** Work is multidimensional/contextual; score hides trade-offs and invites gaming.

### 17.2 Eight practical exercises with acceptance criteria

1. **Define an SLO:** task boundary, good/valid events, denominator, owner, window, missing-data policy, action.
2. **Audit vanity dashboard:** find three missing denominators/countermetrics and harm.
3. **Build KPI dictionary:** service, eligible service, adoption, active usage, first deploy, ticket, escape hatch; each has grain/source/owner/window/exclusions.
4. **Diagnose funnel drop-off:** distinguish observation from inferred cause and propose research.
5. **Review DORA segments:** name confounders and avoid causal language.
6. **Design survey:** neutral questions, anchors, response-rate plan, anonymity, small-n caveat, follow-up.
7. **Privacy review:** safe fixture passes, unsafe fixture fails, limitations documented.
8. **Quarterly review:** evidence, uncertainty, owners, decisions, “you said, we did”.

### 17.3 Defect review

Dashboard says “100% adoption; tickets down 40%; productivity up 25%; ROI 3.2x.” It omits services without catalog metadata, uses only old ticket system, ranks people by deploy count, and multiplies assumed time by guessed hourly rate. Defects: denominator bias, channel migration, individual surveillance, time/cash category error, missing outcome countermetrics, missing sample/window/uncertainty, no causal design, trust/privacy harm.

### 17.4 Incident ordering

If individual deploy rankings were shared with executives: remove/restrict harmful view; communicate; preserve audit evidence; assess decisions made from it; repair dashboard/query scanner; inspect source collection; publish correction/regression controls. Do not begin by defending the metric or blaming people.

---

## 18. Glossary

| Term | Definition | Misconception |
|---|---|---|
| Adoption | Eligible service uses supported capability and meets conformance | Template click = adoption |
| Active usage | Aggregate capability use in defined window | Login = value |
| Cohort | Group sharing start event/period | Any groups are comparable |
| Countermetric | Measure showing downside of headline improvement | Only positive metrics matter |
| DX | Experience completing work through tools/processes/systems | One satisfaction score |
| DiD | Difference in outcome changes across groups | Automatically causal |
| Escape hatch | Approved alternative when default path does not fit | Bypass means developer failure |
| Goodhart | Targeted measure can stop being a good measure | Metrics should never have targets |
| Golden-path coverage | Conformant eligible services / eligible services | Template count |
| Leading indicator | Signal that may precede outcome | Leading means causal |
| Lagging indicator | Result after event/period | Lagging means unimportant |
| Metric grain | Entity/time level represented by observation | Grain can change silently |
| Non-response bias | Respondents differ from non-respondents | Large invite list removes bias |
| Output | Activity/artifact produced | Output equals user value |
| Outcome | Change in task success/reliability/flow/result | Page views prove outcome |
| p95 | 95th percentile for defined population/window | Average latency |
| Platform SLO | Objective for developer-facing capability | Every component needs same target |
| Selection bias | Systematic group/treatment entry differences | Adoption groups comparable |
| Simpson's paradox | Aggregate reversal due to group composition | Aggregate tells whole story |
| Synthetic data | Artificial data for method practice | Synthetic proves real behavior |
| Time-to-first-deploy | Journey start to first verified deploy | Accepted/preview = deploy |
| Unit economics | Cost/value per defined unit | Cost per user is always fair |
| Vanity metric | Impressive-looking metric without useful decision | Every count is useless |

---

## 19. Completion Gate and Self-Audit

### 19.1 Learner checklist

- [ ] Explain reliability, adoption, and DX/outcome measures.
- [ ] Distinguish outputs/outcomes, leading/lagging, and vanity metrics.
- [ ] Define six+ developer-facing SLOs with owner/window/denominator/error-budget action.
- [ ] Run/simulate journey and prove failure/cleanup behavior.
- [ ] Generate six months of synthetic data with seed/confounders.
- [ ] Calculate adoption KPIs with eligibility/numerator/denominator/grain/window.
- [ ] Detect missing, duplicate, timezone, bot, stale catalog, invalid transition, denominator drift.
- [ ] Compare DORA by adoption segment and publish causal caution.
- [ ] Design survey/interview/observation/friction/journey/usability methods.
- [ ] Scan safe and planted unsafe dashboards.
- [ ] Produce HCU scenarios and explicit unknowns.
- [ ] Complete Goodhart simulation and redesign memo.
- [ ] Produce quarterly review and “you said, we did”.
- [ ] Label synthetic outputs and learner task `n=1`.
- [ ] Confirm no individual ranking or surveillance field.

### 19.2 Coverage matrix — syllabus requirements

| Requirement | Lesson location | Audit |
|---|---|---|
| L1 motivation and silent non-adoption | Sections 1–2 | PASS |
| Three families and metrics | Section 2 | PASS |
| Leading/lagging, outputs/outcomes, vanity, SPACE/DevEx/DX Core 4 awareness | Sections 2–3 | PASS |
| Platform SLOs and error-budget actions | Section 4 | PASS |
| Alert rules/dashboard-as-code | Section 4.6–4.7 | OPEN — local `promtool`/Grafana validation |
| Event schema/instrumentation | Section 5 | PASS |
| Synthetic journey and cleanup | Section 5/Lab 1 | PASS — simulation; live cluster not run |
| Six-month synthetic generator/confounders | Lab 2 | PASS — code included, run pending |
| Adoption KPI definitions/denominators | Section 6/Lab 3 | PASS |
| Data-quality checks | Lab 3/shared code | PASS — authored, execution pending |
| DORA segmentation/confounders/matched/DiD | Section 7/Lab 4 | PASS |
| Surveys/interviews/friction/usability/support/funnel | Section 8/Labs 5–6 | PASS |
| Metric-as-code/data quality/privacy/causal/survey science | Sections 9–10 | PASS |
| Scorecard/Goodhart/feedback/prioritization | Sections 10–11/Lab 9 | PASS |
| Cost/unit economics/sensitivity/unknowns | Section 12/Lab 8 | PASS |
| Data/ML DX | Section 13 | PASS |
| Metrics charter/measurement ops | Section 14 | PASS |
| Quarterly review/maturity/team health/benchmarks/AI | Section 14/Lab 10 | PASS |
| Ten mandatory labs | Section 15 | PASS — content present; learner execution pending |
| Troubleshooting | Section 16 | PASS |
| 24+ questions and 8 exercises | Section 17 | PASS — 26 and 8 |
| Completion, inventories, verification | Section 19 | PASS |

### 19.3 Eight incident scenarios

| Scenario | Location | Audit |
|---|---|---|
| Individual deploy ranking/gaming/trust erosion | 10, 16, 17.4 | PASS |
| Mandated adoption worsens satisfaction/incidents | 10.4, 11.5, 16 | PASS |
| n=12 survey generalized | 8.2, 9.6, 17.1 Q10 | PASS |
| API SLO green, environment unusable | 4.3–4.4, 5, 16 | PASS |
| First-deploy definition silently changes | 3.6, 9, 16 | PASS |
| Ticket fall after channel migration | 6.5, 8.6, 16 | PASS |
| Portal analytics captures usernames | 10.1–10.3, 16 | PASS |
| ROI presented as measured fact | 12, Labs 8, 16 | PASS |

### 19.4 Ten-lab inventory

| Lab | Output | Audit |
|---|---|---|
| 1 SLO/journey | SLO suite, probe, dashboard spec | PASS; live integrations OPEN |
| 2 six-month dataset | Seeded generator, ground truth | PASS; run pending |
| 3 KPI/data quality | Definitions, KPI report, defect tests | PASS; run pending |
| 4 DORA segmentation | Segment report, confounders, caution | PASS; full matching is learner extension |
| 5 survey | Instrument, response/small-n analysis | PASS |
| 6 friction/usability | Own-task n=1 before/after, fixes | PASS; learner run pending |
| 7 privacy | Safe/unsafe fixtures and scanner | PASS; regex limits noted |
| 8 economics | HCU scenarios/sensitivity/unknowns | PASS |
| 9 gaming | Simulation/redesign memo | PASS |
| 10 quarterly review | Synthetic review/decisions/owners | PASS |

### 19.5 Metric inventory

| Metric | Numerator/definition | Denominator | Grain/window | Source | Owner | Privacy | Caveat |
|---|---|---|---|---|---|---|---|
| Provisioning success | Verified-ready requests | Valid requests | Request/28d | Provisioning + readiness | Provisioning owner | Service aggregate | Acceptance ≠ ready |
| p95 ready | p95 ready-accepted | Complete valid timestamps; failures separately | Capability/request/28d | Lifecycle | Capability owner | Service aggregate | Exclusions affect tail |
| Template-first-CI | First green within window | Valid generated repos with CI | Journey/month | Template+CI | Template owner | Service aggregate | CI-disabled eligibility |
| Portal availability | Successful valid requests | Valid requests | Request/rolling | Portal | Portal owner | Aggregate | Shell ≠ search |
| Catalog freshness | Fresh eligible records | Eligible records | Snapshot | Catalog | Catalog owner | Service aggregate | Missing records distort |
| GitOps convergence | Healthy in window | Valid desired changes | Change/rolling | GitOps | Delivery owner | Service aggregate | Sync ≠ app ready |
| CI success | Valid successful required runs | Valid required runs | Pipeline/month | CI | CI owner | Aggregate | Retry/flaky policy |
| Support response | p90 meaningful response time | Valid requests | Ticket/business window | Support | Support owner | Aggregate | Auto-ack ≠ response |
| Journey success | Full journeys incl teardown | Valid attempts | Journey/rolling | Synthetic probe | Platform SRE | Synthetic aggregate | Probe is proxy |
| Coverage | Conformant eligible services | Eligible services | Service-month | Catalog/conformance | Platform product | Aggregate | Eligibility governance |
| Self-service | Completed self-service | Self-service + manual completed | Request-month | Requests/channels | Product | Aggregate | All channels required |
| Escape hatch | Eligible services using approved alternative | Eligible services | Service-month | Catalog/exception | Product | Aggregate | May be valid gap |
| Retention | Cohort still conformant | Cohort conformant at start | Cohort-month | Catalog snapshots | Product | Aggregate | Eligibility drift |
| First deploy | Verified deploy minus start | Successful journeys; failures separately | Journey | Template/CI/deploy | Journey owner | Synthetic/service | Definition must version |
| DORA | M10 Unit 11 definitions | Valid service delivery events | Service-month | CI/deploy/incident | Analytics owner | Aggregate | Association ≠ cause |
| Satisfaction | Survey response distribution | Responses; invitations/rate also | Survey wave | Survey | Research | Aggregate | Non-response/small n |
| Cognitive load | Anchored response distribution | Responses | Survey wave | Survey | Research | Aggregate | Perception only |
| Cost/service | Allocated HCU | Active services | Service-month | M15 allocation | FinOps | Aggregate | Allocation assumptions |
| GPU wait | Submit-to-start | Valid queued jobs | Workload/window | Scheduler | ML platform | Aggregate | M15 Unit 12 |

### 19.6 SLO inventory

| SLO | SLI | Target | Error-budget action | Alert/runbook | Verification |
|---|---|---|---|---|---|
| Provisioning | Verified-ready / valid | `[ILLUSTRATIVE]` | Pause risky changes on sustained burn | Provisioning runbook | OPEN instrumentation |
| Time-to-ready | p95 by capability | `[ILLUSTRATIVE]` | Investigate slow capability/queue | Latency runbook | OPEN histogram |
| Template-first-CI | First green / valid repos | `[ILLUSTRATIVE]` | Stop regressing template rollout | Template rollback | OPEN CI mapping |
| Portal/catalog | Request success + freshness | `[ILLUSTRATIVE]` | Fix source/search | Portal/catalog runbook | OPEN portal telemetry |
| GitOps | Healthy in window / valid changes | `[ILLUSTRATIVE]` | Pause risky broad change | GitOps runbook | OPEN controller mapping |
| CI | Required success + p95 | `[ILLUSTRATIVE]` | Prioritize runner/queue | CI runbook | OPEN CI schema |
| Support | Meaningful response distribution | `[ILLUSTRATIVE]` | Escalate coverage/ownership | Support workflow | OPEN ticket semantics |
| Journey | Full success incl teardown | `[ILLUSTRATIVE]` | Pause risky path rollout | Probe runbook | OPEN live probe |

### 19.7 Verification register

| Claim | Source/action | Version/date | Status |
|---|---|---|---|
| Prometheus recording/alert rules and `promtool` | Official docs: https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/ ; https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/ ; https://prometheus.io/docs/prometheus/latest/configuration/promtool/ | Consulted 2026-11-03; local version to record | PASS concept; OPEN local rules/tests |
| Histogram quantile semantics | https://prometheus.io/docs/practices/histograms/ ; https://prometheus.io/docs/prometheus/latest/querying/functions/ | Consulted 2026-11-03; installed release `[VERIFY]` | PASS concept; OPEN local buckets |
| Grafana file provisioning | https://grafana.com/docs/grafana/latest/administration/provisioning/ | Consulted 2026-11-03; release-specific schema `[VERIFY]` | PASS concept; OPEN local dashboard |
| Crossplane metrics/conditions | Inspect installed controller metrics and CRD status | Installed version required | OPEN |
| Portal aggregate analytics | Inspect portal version, privacy settings, schema, retention | Portal version required | OPEN |
| M11 Unit 8 probe integration | Inspect full lesson and probe implementation | Not located in session files | OPEN |
| SPACE/DevEx/DX Core 4 | Verify primary publications; names only used here | Source/year required | OPEN |
| CNCF maturity | Verify current CNCF publication | Current model required | OPEN |
| RICE/ICE/opportunity trees | Verify selected framework source | Source required | OPEN |
| Grafana dashboard JSON | Pin release and validate exported JSON | Local release | OPEN |
| Prometheus rule tests | Run `promtool check rules` and `test rules` | Local release | OPEN |

### 19.8 Human verification checklist

- [ ] Journey matches actual workflow and safe teardown.
- [ ] Six+ SLOs have owner, boundary, denominator, action.
- [ ] Prometheus rules/tests pass installed release.
- [ ] Grafana dashboard JSON/provisioning validates pinned release.
- [ ] KPI definitions match catalog/CI/GitOps/ticket/provisioning semantics.
- [ ] Data quality catches missing/duplicate/timezone/bot/stale/invalid/denominator defects.
- [ ] DORA reuses M10 definitions and reports confounders.
- [ ] Survey neutral; response rate and small-n caveats explicit.
- [ ] Scanner catches planted fields and is supplemented by source/query/access review.
- [ ] Unit economics separates measured cost/time/estimated/speculative benefits.
- [ ] Cleanup leaves no cluster, namespace, workload, or optional stack running.

### 19.9 Author execution statement

**Inspected:** attached Unit 8 prompt; complete Unit 8 section of authoritative M16 syllabus prompt; roadmap; generated M16 Units 1–7; M07 Unit 12 Crossplane lesson; M10 Unit 1 SLO and M10 Unit 11 DORA lessons from Library; M15 Unit 4 cost allocation and Unit 12 GPU lessons; M11 Unit 3 Grafana lesson and prompt. Complete M11 Unit 8 lesson was not located; probe integration remains `[VERIFY]`.

**Official docs consulted:** Prometheus recording rules, alerting rules, `promtool`, histograms/query functions; Grafana file provisioning. URLs above.

**Execution status:** The embedded Plat-Core Python module and unit-test file were extracted from this Markdown into an isolated temporary directory and executed. **8/8 unit tests passed.** The six-month generator ran with seed `20261103` and produced 1,896 synthetic events, 30 catalog records, 50 synthetic tickets, 126 synthetic survey responses, and 354 synthetic self-service/manual request records. The KPI report ran with an initial data-quality status of `PASS`; all figures are synthetic and are not claims about a real platform. The failure-injected journey was exercised by the unit test and correctly reported failure while attempting cleanup. No `promtool`, Grafana, Docker/Podman, `kind`, Kubernetes, Crossplane, portal, CI, ticketing, or production integration was run. No dashboard/alert/experiment is claimed deployed. Targets/HCU are illustrative; generated data is synthetic; learner timing must be measured locally and labelled `n=1`.

**Scope integrity:** only this standalone Markdown lesson was created in `/mnt/data/unit8-output/`. No source, roadmap, sibling lesson, or repository file was modified.
