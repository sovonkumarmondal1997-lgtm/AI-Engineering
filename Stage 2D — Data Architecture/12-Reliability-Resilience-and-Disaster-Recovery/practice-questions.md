# Reliability, Resilience and Disaster Recovery — Practice Questions

> **Purpose.** This question bank is a new learning resource created from the module roadmap. It does not reproduce pre-existing questions or answer keys: the roadmap says `practice-questions.md` was empty. All organisations, system names, targets, data volumes, costs, and numerical values in this file are **illustrative assumptions**, not requirements or benchmarks from the source roadmap.
>
> **Scope.** The eight roadmap topics are covered in the recommended learning order. This is a vendor-neutral design and documentation exercise. Nothing here requires a production outage or access to production infrastructure.

## Contents

- [A. How to use this question bank](#a-how-to-use-this-question-bank)
- [B. Beginner questions](#b-beginner-questions)
- [C. Intermediate questions](#c-intermediate-questions)
- [D. Advanced architecture and production scenarios](#d-advanced-architecture-and-production-scenarios)
- [E. Integrated case study](#e-integrated-case-study)
- [F. Answers and worked solutions](#f-answers-and-worked-solutions)
- [G. Scoring and evaluation rubric](#g-scoring-and-evaluation-rubric)
- [H. Gap log and remediation tracker](#h-gap-log-and-remediation-tracker)
- [I. Final readiness assessment](#i-final-readiness-assessment)
- [J. Completion checklist](#j-completion-checklist)

---

## A. How to use this question bank

### A1. Follow the roadmap sequence

Attempt the questions after studying the matching lesson. The roadmap's recommended sequence is:

1. `01-reliability-objectives-sli-slo-and-sla.md`
2. `02-failure-domains-and-blast-radius.md`
3. `03-high-availability-and-redundancy-patterns.md`
4. `04-backup-restore-and-recovery-validation.md`
5. `05-rpo-rto-and-disaster-recovery-strategies.md`
6. `06-replay-reprocessing-and-backfill-architecture.md`
7. `07-incident-response-runbooks-and-postmortems.md`
8. `08-business-continuity-and-resilience-testing.md`

The order builds from measurable objectives, through failure analysis and prevention, into data recovery, recovery strategy, replay, human response, and business-focused testing. Earlier topics may need to be revisited when a later calculation or scenario exposes a gap.

### A2. Use a repeatable attempt method

1. **Closed-book recall:** answer the beginner questions without notes. Mark uncertain claims rather than guessing.
2. **Show working:** for numerical questions, write the formula, substitute values with units, calculate, then interpret the result against the target.
3. **Separate facts from assumptions:** list facts supplied by the question and any assumptions you introduce. If a missing fact changes the decision, identify the evidence you would request.
4. **Defend decisions:** compare at least two viable options, explain trade-offs, and state why the selected option meets the stated business constraints.
5. **Use the answer key as feedback:** review the reasoning and plausible failure modes, not only the final number.
6. **Record gaps:** use Section H for every partial or incorrect answer. Assign a remedial lesson or exercise and a re-attempt date.
7. **Repeat:** re-attempt without looking at the solution. Close a gap only when the reasoning and evidence are correct on a later attempt.
8. **Prepare the capstone:** use the integrated case study to assemble a consistent recovery and resilience plan; use the final assessment as a readiness gate, not as a substitute for the project.

### A3. Calculation conventions

- Use decimal arithmetic for percentages unless otherwise stated; report availability percentages to at least four decimal places when relevant.
- A 30-day month has 30 × 24 = 720 hours. A 365-day year has 8,760 hours. State the window used.
- For simple series availability, assume independent component failures only when the question explicitly says so; then multiply component availabilities. Real failures may be correlated.
- For backup interval questions, distinguish the **maximum theoretical data-loss window** from actual achievable RPO. The latter also depends on successful backup completion, replication/log capture, retention, and recovery procedures.
- Treat time budgets as elapsed wall-clock time, including dependency restoration, replay, validation, approvals, and traffic switching when those activities are necessary for service recovery.
- For open-ended questions, multiple designs can be correct if assumptions, trade-offs, and verification criteria are defensible.

### A4. Error categories

Use these categories in the gap log: **vocabulary**, **calculation**, **scenario analysis**, **missing dependency**, and **missing validation**. Add a note if the main issue is an unsupported assumption, unclear communication, or unsafe operational sequencing.

---

## B. Beginner questions

Try these before reading Section F. Questions are grouped by roadmap topic and use a mix of multiple-choice, true/false with justification, short answer, and classification.

### Topic 1 — Reliability objectives, SLI, SLO and SLA

**B01 — Multiple choice (one best answer).** Which statement best describes an SLI?

A. A contractual remedy for a missed service commitment.  
B. A measured indicator of service behaviour, such as successful requests or data freshness.  
C. A target value set for a measurement window.  
D. A list of components that may fail together.

**B02 — True/false with justification.** “A pipeline can meet its infrastructure-availability SLO while failing the business need because the report is late or the data is incorrect.” Explain why.

### Topic 2 — Failure domains and blast radius

**B03 — Short answer.** Define a failure domain and blast radius. Explain how they are related but not identical.

**B04 — Classification.** A primary and standby data-serving cluster run in different zones but share one identity provider and one deployment control plane. Name two distinct failure domains or shared dependencies that should appear on the failure map, and explain the risk.

### Topic 3 — High availability and redundancy

**B05 — Multiple choice (one best answer).** Which is the strongest general statement about redundancy?

A. Two copies guarantee uninterrupted service.  
B. Redundancy is useful only when the copies use different vendors.  
C. Redundancy can reduce interruption from some failures, but shared dependencies and failover defects can defeat it.  
D. Replication replaces the need for backups.

**B06 — Short answer.** Distinguish active/standby from active/active. Give one operational trade-off for each.

### Topic 4 — Backup, restore and recovery validation

**B07 — True/false with justification.** “If backup jobs report success, recoverability has been proven.”

**B08 — Short answer.** List four checks that should be made after restoring a data platform, beyond confirming that the service process starts.

### Topic 5 — RPO, RTO and DR strategies

**B09 — Classification.** Classify each as an RPO or RTO concern:

1. No more than 10 minutes of committed transactions may be lost.  
2. Critical reports must be available within 90 minutes after a declared disaster.  
3. The recovery point must be no older than the last successfully captured change within the agreed tolerance.

**B10 — Short answer.** Why is “we have a replica in another region” insufficient evidence that a disaster recovery strategy meets business needs?

### Topic 6 — Replay, reprocessing and backfill

**B11 — Multiple choice (one best answer).** What is the main purpose of idempotency in a replayable pipeline?

A. Make every execution faster than the previous one.  
B. Ensure retrying the same logical input does not create unintended duplicate effects.  
C. Prevent all upstream data from arriving late.  
D. Guarantee that every downstream consumer is available.

**B12 — Short answer.** Distinguish replay, reprocessing, and backfill in practical terms.

### Topic 7 — Incident response, runbooks and postmortems

**B13 — Classification.** Match each activity to the most appropriate phase: **detect/triage**, **contain/mitigate**, **recover/validate**, or **learn/follow up**.

1. Stop a faulty deployment from propagating.  
2. Confirm that restored balances reconcile to the trusted source.  
3. Assign an incident commander and determine severity.  
4. Track a corrective action to a verified retest.

**B14 — Short answer.** What makes a postmortem blameless without making it consequence-free or vague?

### Topic 8 — Business continuity and resilience testing

**B15 — Multiple choice (one best answer).** What is the primary distinction between disaster recovery and business continuity?

A. DR is for databases; BC is only for people.  
B. DR restores technology and data; BC keeps critical business functions operating, potentially in a degraded mode.  
C. BC eliminates the need for DR.  
D. They are interchangeable terms.

**B16 — Short answer.** Name five elements of a useful resilience-test plan, including at least one measurable success criterion and one safety control.

---

## C. Intermediate questions

Show calculations and state assumptions. Unless a question says otherwise, all figures are illustrative and the model answers should explain what production evidence would still be needed.

### Topic 1 — Reliability objectives, SLI, SLO and SLA

**C01 — Error-budget arithmetic.** An illustrative data-delivery service has a monthly SLO of 99.9% successful eligible deliveries. The measurement window is 30 days and contains 720 hours. Assume all elapsed time is eligible and outages are the only failure mode.

1. What is the allowed unavailability in minutes for the month?  
2. If 38 minutes of qualifying unavailability occurred, how much time budget remains?  
3. State two reasons this simple calculation may not match a real delivery SLI.

**C02 — SLI/SLO/SLA design.** A finance report must be ready by 06:00 local time on business days, contain all expected source records, and reconcile within a defined tolerance. Propose three SLIs and corresponding illustrative SLOs. Explain why “the scheduler ran” is not sufficient.

### Topic 2 — Failure domains and blast radius

**C03 — Blast-radius calculation.** A platform has 12 data products. A shared catalogue failure blocks 5 products; a shared identity failure blocks 8 products; 3 products are blocked by both failures. Assuming these counts describe the affected sets in the same observation window, how many distinct products are affected by either failure? What fraction of the 12 products is that? Explain why a simple count does not fully describe business impact.

**C04 — Dependency map.** A streaming pipeline depends on a source API, network route, identity service, schema registry, event broker, processing cluster, object store, orchestration service, and BI semantic model. Choose a minimum of four failure domains, identify shared dependencies, and propose one containment or detection control per domain. State how lineage and ownership metadata help.

### Topic 3 — High availability and redundancy

**C05 — Series availability.** A critical read path requires three independent components in series, with illustrative availabilities of 99.95%, 99.9%, and 99.99%. Assuming independence, calculate end-to-end availability and approximate downtime over a 30-day month. Explain the limitations of the independence assumption.

**C06 — Redundancy decision.** A serving tier has two zone-local instances behind a load balancer. Both instances depend on a single-zone metadata service. Compare (a) adding a third serving instance in another zone and (b) making metadata highly available across zones. Which is likely to remove the more important single point of failure, and what evidence would you collect before deciding?

### Topic 4 — Backup, restore and recovery validation

**C07 — Backup interval and loss window.** A team has successful full-backup completion timestamps exactly 6 hours apart. Ignore incremental logs for this question and assume each backup remains usable. Immediately before the next backup completes, what is the limiting theoretical age of the latest completed backup? Can the design meet an illustrative 15-minute RPO? Explain why a real schedule would also need to account for backup duration or completion delays.

**C08 — Restore-time budget.** A recovery exercise has these elapsed-time components: provision environment 18 min; restore data 42 min; restore metadata and permissions 16 min; replay changes 24 min; validation and reconciliation 20 min; switch consumers 10 min. Calculate total recovery time. Does it meet an illustrative 120-minute RTO? How much headroom remains, if any?

### Topic 5 — RPO, RTO and DR strategies

**C09 — Feasibility review.** A business requires RPO ≤ 5 minutes and RTO ≤ 60 minutes. The proposed strategy uses a daily backup and an untested cross-region replica. Identify the gaps and propose a strategy/evidence package that could plausibly satisfy the objectives without assuming a specific vendor.

**C10 — Recovery budget.** A service has an illustrative RTO of 180 minutes. Detection and declaration consume 15 minutes; infrastructure and identity recovery consume 35 minutes; data restore consumes 55 minutes; replay consumes 40 minutes; validation consumes 25 minutes; consumer switching consumes 20 minutes. Calculate the total and determine whether the target is met. If not, quantify the overrun and name two legitimate design changes that could reduce it.

### Topic 6 — Replay, reprocessing and backfill

**C11 — Backlog catch-up.** A pipeline receives 900 records/minute and can process 1,200 records/minute during recovery. New records continue arriving at 900/minute. Initial backlog is 180,000 records. Assuming constant rates and no downstream bottleneck, calculate net backlog-drain rate and time to clear the backlog. Explain why merely stating “processing capacity is 1,200/minute” is misleading.

**C12 — Replay correctness.** A daily aggregate pipeline writes output by appending rows. A replay of the last three days would append duplicate aggregates. Propose a safer replay/backfill design, including idempotency, partition or key strategy, late-arriving corrections, and validation. State a trade-off of your design.

### Topic 7 — Incident response, runbooks and postmortems

**C13 — Incident timeline.** An alert fires at 02:10. The on-call acknowledges at 02:18, the incident is declared at 02:25, mitigation starts at 02:40, service is restored at 03:35, and correctness validation completes at 04:05. Calculate (a) detection-to-acknowledgement, (b) acknowledgement-to-declaration, (c) declaration-to-restoration, and (d) detection-to-validated recovery. Explain why restoration time and validated recovery time differ.

**C14 — Runbook diagnosis.** A runbook says “fail over to the secondary region” but omits authority to declare disaster, identity recovery, source-offset handling, data-integrity checks, and failback criteria. Identify at least five risks and propose a minimal runbook structure.

### Topic 8 — Business continuity and resilience testing

**C15 — BIA and workaround capacity.** A critical risk-reporting function generates 4,800 records per hour under normal conditions. A manual workaround can safely process 3,000 records per hour, while new work continues to arrive at 4,200 records per hour. (a) What is the net backlog growth per hour during workaround operation? (b) If 6,000 records are already queued, how long until the queue is cleared after the normal platform returns to a net processing surplus of 1,800 records/hour, assuming no further arrivals beyond the stated net surplus? (c) What additional BIA information is needed before declaring the workaround adequate?

**C16 — Test design.** Design a tabletop or controlled simulation for a zone outage. Include a falsifiable hypothesis, prerequisites, roles, success criteria, evidence, abort conditions, and follow-up ownership. Do not assume that an actual production outage is required.

---

## D. Advanced architecture and production scenarios

For each scenario, write: **facts**, **assumptions**, **impact**, **dependency/failure analysis**, **options**, **decision and trade-offs**, **validation evidence**, and **follow-up actions**. Model answers are in Section F.

**D01 — Available pipeline, missed business deadline.** Monitoring reports that every pipeline service is “up,” but a regulatory report missed its 06:00 deadline and contains only 92% of expected records. Diagnose how an infrastructure-centric SLI can hide business failure. Propose immediate response, data-quality/freshness indicators, dependency checks, and a revised objective set.

**D02 — Shared catalogue or deployment dependency.** A shared metadata catalogue change makes schemas unavailable to 7 of 10 products. Rollback is blocked because deployment tooling also depends on the same control plane. Design a failure-domain analysis and containment plan. Address independent recovery access, staged rollout, dependency ownership, and evidence required before declaring recovery.

**D03 — Zone outage in a redundant serving architecture.** Two serving instances are deployed in separate zones, but a zone outage causes a 45-minute interruption. Both instances share a single-zone metadata service and a load balancer whose health checks incorrectly treat stale data as healthy. Identify the architectural and operational defects. Propose corrective changes and a test that demonstrates business-level recovery.

**D04 — Corruption replicated to the secondary.** An erroneous transformation overwrites customer-risk aggregates. Replication copies the corrupted output to the secondary region within minutes. Explain why replica failover alone is unsafe. Design a recovery approach using a trusted recovery point, lineage, replay/reprocessing, reconciliation, and explicit authority to resume downstream consumers.

**D05 — RPO cannot be met by backup interval.** A platform takes a full backup every 4 hours, but the agreed RPO is 20 minutes. No continuous change capture is currently configured. Show the mismatch and compare feasible options. Include operational monitoring and a way to prove the achieved recovery point.

**D06 — RTO omits replay and validation.** An architecture plan claims a 50-minute RTO based on 20 minutes to provision and 30 minutes to restore data. In a realistic exercise, replay requires 35 minutes and validation requires 25 minutes. Evaluate the claim and propose a revised recovery budget and decision path if the business target is firm.

**D07 — Historical backfill competes with live processing.** A 14-day backfill is launched during peak hours. It doubles compute demand, increases live pipeline lag, and threatens a freshness SLO. Propose scheduling, isolation, prioritisation, throttling, checkpoints, idempotency, and rollback controls. Explain how to decide whether to pause the backfill.

**D08 — Unclear incident ownership and incomplete runbooks.** A data incident spans source ingestion, orchestration, catalogue, and reporting teams. Each team assumes another owns incident command. The report is restored but no one confirms reconciliation. Define incident roles, escalation, communications, recovery gates, and postmortem actions.

**D09 — Technical test passes, business objective fails.** A failover exercise restores the platform within the target time, but a business team cannot execute the critical process because its identity access, reference data, and manual workaround were not included in the test. Explain the gap and redesign the business continuity test. Include a risk-based retest plan.

---

## E. Integrated case study

### E1. Scenario: Northbridge Bank data platform (fictional)

All details below are **illustrative assumptions** created for this exercise.

Northbridge Bank runs an enterprise data platform supporting fraud operations, regulatory risk reporting, and customer-service analytics.

**Data flow**

1. Core banking and card systems publish changes through CDC and scheduled extracts.
2. An ingestion service writes raw events to an event broker and immutable object storage.
3. A processing layer validates schemas, deduplicates events, and builds curated risk and customer datasets.
4. A metadata catalogue stores schemas, ownership, and dataset relationships. An orchestrator schedules batch dependencies. A semantic model serves BI reports.
5. Fraud operations consume a near-real-time risk view; the regulatory risk report is due by 06:00 local time on business days; customer-service analytics can tolerate a longer delay.
6. The primary deployment uses two availability zones. A secondary region has replicated storage and a warm processing environment. Identity, deployment automation, and some catalogue capabilities have not yet been proven recoverable without the primary region.
7. Raw data is retained for 35 days. Curated daily snapshots are retained for 90 days. A daily backup exists, but backup restore, key recovery, replay, and consumer validation have not yet been exercised together.
8. A historical backfill can consume the same processing pool as live fraud processing unless throttled.

**Illustrative service objectives and constraints**

- Fraud risk view: 99.95% monthly availability SLO; freshness objective of no more than 2 minutes under normal conditions.
- Regulatory report: ready by 06:00 on business days; at least 99.5% of expected records must be present and reconciliation differences must be within an approved tolerance before release.
- Regulatory data RPO: no more than 10 minutes of committed changes lost.
- Regulatory report RTO: 3 hours from declared disaster to validated, usable report service.
- Fraud continuity: an approved degraded operating mode must be available within 30 minutes; this is a business continuity target, not proof that the full platform is recovered.
- Illustrative recovery budget: a test team estimates 15 minutes for declaration, 30 minutes for infrastructure and identity, 50 minutes for data restore, 45 minutes for replay, 25 minutes for validation, and 20 minutes for consumer switching.
- Teams: Data Platform Operations, Source Systems, Data Product Owners, Security/Identity, BI/Reporting, and Business Risk Operations. Incident command is currently assigned informally.

### E2. Integrated assignment

Produce one joined-up architecture and operations package. Each answer must refer back to the scenario facts and mark any new assumption.

**E2.1 — Objectives and indicators.** Define at least one availability SLI, one freshness SLI, one completeness/correctness SLI, and a suitable SLO or business deadline for each critical consumer. Explain why report readiness and report correctness are separate conditions.

**E2.2 — Failure domains and blast radius.** Draw or describe the source-to-consumer dependency chain. Identify at least six failure domains or shared dependencies, at least two common-cause risks, and a containment strategy for each high-impact risk.

**E2.3 — HA and availability.** Recommend a zone-level serving pattern for the fraud view and regulatory report. Identify single points of failure and state the availability calculation you would perform. Do not calculate end-to-end availability from unknown values; list the measurements needed.

**E2.4 — Backup, restore, validation.** Write a restore sequence that includes data, metadata/catalogue, identity/keys, offsets/checkpoints, orchestration, and consumers. Define evidence for backup integrity, completeness, referential consistency, reconciliation, and consumer usability.

**E2.5 — RPO/RTO and DR.** Assess whether the proposed recovery budget meets the 3-hour RTO. Propose a DR strategy that plausibly meets the 10-minute RPO and explain what must be tested before claiming compliance.

**E2.6 — Replay and backfill.** Design a safe recovery/replay plan for a 40-minute ingestion interruption. Include event identity, deduplication, idempotent writes, late-arriving events, ordering, checkpointing, and workload isolation from live fraud processing.

**E2.7 — Incident response and postmortem.** Create an incident timeline and role model from detection through validated recovery. Specify severity, incident command, communications, decision logs, stop/rollback conditions, and a blameless postmortem with measurable corrective actions.

**E2.8 — Business continuity and resilience testing.** Design a tabletop plus controlled simulation for (a) zone loss and (b) regional loss combined with replicated corruption. Include business function owners, workarounds, test hypothesis, success/failure thresholds, safety controls, evidence, and retest triggers.

**E2.9 — Consistency review.** Cross-check that the SLOs, failure map, HA design, backup schedule, RPO/RTO, replay plan, incident runbook, and business test use compatible assumptions. Identify at least five conflicts or missing proofs that must be resolved before sign-off.

---

## F. Answers and worked solutions

> **Use this section after attempting the questions.** The answers are model solutions, not the only acceptable architecture. For production decisions, replace illustrative assumptions with measured evidence, contractual obligations, business impact analysis, and approved risk decisions.

### F1. Beginner answer key

**B01.** **B.** An SLI is a measurement of service behaviour. An SLO is a target for an SLI over a defined window; an SLA is an agreement with commitments and possible consequences; a failure domain is a set of components that can fail together. **Production evidence:** metric definition, source of truth, eligible-event denominator, window, and measurement coverage.

**B02.** **True.** Infrastructure health does not prove that the business outcome was delivered. A pipeline may be running but delayed, incomplete, stale, duplicated, or incorrect. A suitable objective combines service operation with freshness, completeness, correctness, and business deadline criteria. **Evidence:** expected-vs-actual counts, data-quality checks, event-time freshness, reconciliation, and consumer acceptance.

**B03.** A failure domain is a set of components sharing a failure mode or fate; blast radius is the extent of service, data, users, or business processes affected by a failure. A domain is a design/analysis boundary; blast radius is the observed or predicted impact. One shared identity provider may be a domain whose failure affects several otherwise separate clusters. **Evidence:** dependency graph, ownership, observed incident impact, and fault-isolation tests.

**B04.** Examples: (1) shared identity provider, which may prevent both clusters from authenticating; (2) shared deployment/control plane, which may prevent rollback or recovery actions. Other defensible answers include network, DNS, key management, catalogue, or shared storage. **Evidence:** dependency inventory and a test of operation when the shared dependency is unavailable.

**B05.** **C.** Redundancy reduces certain single-component failures but is not a guarantee. Shared dependencies, common configuration, correlated faults, data corruption, or broken failover can affect both copies. Replication may also copy deletion or corruption, so it does not replace backup.

**B06.** Active/standby sends normal traffic to one primary and keeps another ready to take over; it can simplify consistency but may leave standby capacity underused and failover unproven. Active/active serves from multiple instances/locations; it can improve capacity and continuity but increases routing, consistency, conflict, and operational complexity. The best option depends on workload semantics and recovery objectives.

**B07.** **False.** A successful backup job proves at most that the job reported success. Recoverability requires restore tests, readable backup artifacts, keys and metadata, a consistent recovery point, sufficient capacity, correct permissions, and validation of data and consumers.

**B08.** Any four well-explained checks: row/record counts against expected ranges; checksums or object integrity; schema/version compatibility; referential and transaction consistency; reconciliation to trusted source totals; duplicate/missing-event checks; freshness/lag; permissions/key access; metadata/lineage presence; consumer query/report validation; successful replay; evidence captured with timestamps.

**B09.** (1) RPO. (2) RTO. (3) RPO. RPO concerns the age/amount of recoverable data expressed as time; RTO concerns the time to restore an agreed service to a usable state.

**B10.** A replica may share failure domains, replicate corruption/deletion, have lag beyond the RPO, lack identity/keys/metadata, lack sufficient compute capacity, or never have been tested. A DR claim needs measured recovery time, a verified recovery point, integrity checks, business-consumer validation, runbooks, roles, and evidence that dependencies can be recovered.

**B11.** **B.** Idempotency prevents retries of the same logical work from creating unintended duplicate effects. It does not automatically solve ordering, conflicting updates, late events, or every side effect; those require explicit design.

**B12.** **Replay** re-reads or re-emits previously captured events/changes to recover processing. **Reprocessing** reruns transformations against existing inputs, often with changed logic or to repair outputs. **Backfill** computes missing historical periods or partitions. They overlap operationally; state the input range, transformation version, write semantics, and validation for each job.

**B13.** 1 → contain/mitigate; 2 → recover/validate; 3 → detect/triage; 4 → learn/follow up. A complete incident may loop between phases as new evidence emerges.

**B14.** A blameless postmortem focuses on system conditions, decisions, controls, and incentives rather than scapegoating. It remains accountable by recording facts, impact, contributing factors, owners, due dates, measurable corrective actions, and retest/closure evidence. Blameless does not mean action-free.

**B15.** **B.** DR restores technology and data; BC keeps critical business functions operating, potentially through manual or degraded modes while full recovery continues.

**B16.** Include: objective and falsifiable hypothesis; scenario/scope; prerequisites and baseline; roles/communications; step-by-step actions; measurable pass/fail criteria; evidence collection; safety limits and abort conditions; rollback/restore plan; findings register, owner, and retest. Any five earn credit if a success criterion and safety control are included.

### F2. Intermediate worked solutions

**C01 — Error budget**

1. Allowed unavailability = window × (1 − SLO) = 720 hours × (1 − 0.999) = 0.72 hours. In minutes: 0.72 × 60 = **43.2 minutes**.
2. Remaining budget = 43.2 − 38 = **5.2 minutes**.
3. Real SLIs may count eligible deliveries rather than wall-clock downtime; may exclude scheduled maintenance or non-eligible events; may distinguish partial failure from total outage; and may use a rolling window or business-hour calendar. Any two with explanation are acceptable. **Evidence:** exact SLI specification and event-level data.

**C02 — SLI/SLO design.** A defensible set: (1) report-ready-by-deadline rate, e.g. illustrative target ≥ 99.5% of business days by 06:00; (2) completeness, e.g. ≥ 99.5% of expected records with exceptions handled under an approved release rule; (3) reconciliation/correctness, e.g. all critical totals within an explicitly approved tolerance before release. These thresholds are examples, not universal values. “Scheduler ran” measures an internal event, not whether the report is complete, accurate, or usable. **Evidence:** expected source manifests, record counts, reconciliation controls, timestamped report readiness, and business sign-off.

**C03 — Blast radius.** Inclusion-exclusion: affected by either = 5 + 8 − 3 = **10 products**. Fraction = 10/12 = 0.8333… = **83.33%**. A count does not capture criticality, customer/regulatory consequences, duration, data sensitivity, workarounds, or whether products are blocked versus serving incorrect data. **Evidence:** product criticality and dependency/impact map.

**C04 — Dependency map.** Example domains: (1) source/API and network; isolate source retries and alert on source lag; (2) identity/key service; test least-privilege recovery access and alternate emergency procedure; (3) schema registry/catalogue; cache versioned schemas where safe and stage changes; (4) event broker/processing; monitor lag, partition health, and consumer offsets; (5) object store; test object integrity, versioning, and access; (6) orchestration/semantic model; ensure manual recovery order and consumer checks. Lineage tells responders which downstream products depend on a failed asset; ownership metadata tells them who can decide, repair, and validate. Accept other well-justified domains.

**C05 — Series availability.** Convert percentages to decimals: 0.9995 × 0.999 × 0.9999 = **0.99840064995**, or approximately **99.8401%**. Monthly unavailable time = 720 × (1 − 0.99840064995) hours = 1.151532036 hours ≈ **69.1 minutes**. The independence assumption may fail because of shared power, network, identity, configuration, or deployment errors. Component SLIs may also have different windows and definitions, and simple multiplication assumes all three are mandatory series dependencies.

**C06 — Redundancy decision.** A third serving instance may add capacity but does not remove the shared metadata single point of failure. Making metadata highly available across independent zones is likely to remove the more important common dependency, assuming it is truly the limiting failure path. Before deciding, measure failure history and critical-path dependency, metadata service availability and recovery time, instance saturation, health-check semantics, and tested failover behaviour. Also assess whether metadata replication introduces consistency or split-brain risk.

**C07 — Backup interval.** With completion timestamps exactly 6 hours apart, immediately before the next completion the latest completed backup approaches **6 hours old**. This cannot meet a 15-minute RPO. In a real schedule, backup duration and delayed completion can increase the interval unless the cadence is defined by successful completion times. Actual loss can also be worse if jobs fail, backups are corrupt, log capture is absent, or restore/retention/key dependencies are unavailable. To meet 15 minutes, add sufficiently frequent and verified change capture/replication or snapshots, then measure the latest recoverable committed change during tests.

**C08 — Restore-time budget.** Total = 18 + 42 + 16 + 24 + 20 + 10 = **130 minutes**. It misses the 120-minute RTO by **10 minutes**; there is no headroom. A realistic plan should add uncertainty/contingency and ensure the target includes validated consumer service, not just data restored. **Evidence:** timestamped exercise records and a defined “usable” recovery endpoint.

**C09 — Feasibility review.** Daily backups alone permit a recovery point potentially almost 24 hours old, so they cannot prove a 5-minute RPO. An untested replica has no demonstrated lag, integrity, failover, capacity, or recovery time. Plausible plan: capture committed changes continuously or at intervals safely inside the 5-minute objective; retain independent point-in-time recovery for corruption; recover metadata, identity, and keys; rehearse failover and failback; validate data and consumers; measure RPO/RTO and document exceptions. Evidence includes observed replica lag/recovery point, restore tests, reconciliation, and signed test results. Avoid claiming the target is met until tested.

**C10 — Recovery budget.** Total = 15 + 35 + 55 + 40 + 25 + 20 = **190 minutes**. Overrun = 190 − 180 = **10 minutes**, before extra contingency. Legitimate changes include reducing replay through continuous change capture or pre-positioned recovery data; automating and rehearsing identity/infrastructure recovery; improving restore throughput; pre-validating dependencies; or reducing scope only if the business explicitly accepts the degraded service definition. Do not simply omit replay or validation from the budget.

**C11 — Backlog catch-up.** Net drain = processing rate − arrival rate = 1,200 − 900 = **300 records/minute**. Time = 180,000 / 300 = **600 minutes = 10 hours**. The gross capacity of 1,200/minute is not the backlog-clearing rate because new work continues to arrive. Assumptions: rates remain constant, no retries/duplicates, no downstream bottleneck, and recovery capacity is sustained.

**C12 — Replay correctness.** Use deterministic keys such as `(business_date, entity_id, metric_version)` and idempotent upsert/replace of the affected date partitions rather than blind append. Isolate the three-day range, pin the transformation version, checkpoint progress, handle late corrections according to event-time/watermark policy, and preserve a recoverable prior output or staging area. Validate counts, duplicates, aggregates, reconciliation, freshness, and downstream consumers before publishing. Trade-off: partition replacement can be expensive or temporarily unavailable and needs transaction/swap semantics; upserts require correct keys and conflict handling. Alternative designs are acceptable with equivalent guarantees.

**C13 — Incident timeline.** (a) 02:10 to 02:18 = **8 minutes**. (b) 02:18 to 02:25 = **7 minutes**. (c) 02:25 to 03:35 = **70 minutes**. (d) 02:10 to 04:05 = **115 minutes**. Restoration means service operation resumed; validated recovery additionally proves data correctness and business usability. The exact MTTD definition varies: an alert timestamp may be detection or alert emission, and MTTR may mean restore, resolve, or validated recovery. Define the metric before reporting it.

**C14 — Runbook diagnosis.** Risks include unauthorised or delayed disaster declaration; secondary region inaccessible due to identity/key dependencies; stale/missing offsets causing loss or duplication; corruption copied to secondary; consumers switched before correctness checks; unclear source-of-truth; no abort/rollback; uncontrolled split brain; untested failback; no evidence or owner. Minimal structure: purpose/scope; severity/trigger; authority and roles; prerequisites/access; dependency order; numbered actions with expected outputs; data/offset/metadata recovery; integrity and business validation gates; communications; abort/rollback; failback criteria; evidence capture; escalation and post-incident updates.

**C15 — BIA and workaround capacity.** (a) Net backlog growth = arrivals − manual processing = 4,200 − 3,000 = **1,200 records/hour**. (b) Once the platform returns and has a net processing surplus of 1,800 records/hour, time to clear 6,000 records = 6,000 / 1,800 = **3.333… hours**, or **3 hours 20 minutes**, under the stated assumption that the net surplus applies to that queue. (c) BIA needs maximum tolerable disruption, criticality by business time window, record priority, error tolerance, staffing/shift capacity, safety/quality controls, dependencies, legal/regulatory deadlines, manual throughput evidence, queue growth, communications, and exit criteria. A workaround that cannot handle incoming demand may only slow the failure, not sustain the function.

**C16 — Test design.** Example hypothesis: “If zone A becomes unavailable, eligible report and fraud-view traffic will continue in zone B, with the fraud view restored to its agreed degraded/full service within 10 minutes and no unreconciled data loss beyond the approved RPO.” Preconditions: approved test window, isolated simulation or controlled fault injection, known baseline, backups and rollback, on-call/business participants, access, and observability. Roles: test lead, incident commander, platform operator, data owner, security, business observer, safety controller. Pass criteria: measured service endpoint restored within target, lag/RPO inside tolerance, reconciliation passes, consumer query succeeds, and no unsafe writes occur. Abort for unexpected customer impact, loss of recovery access, corruption outside scope, or safety thresholds. Capture timestamps, dashboards, commands, data-quality evidence, decisions, and actions; assign owners and retest. Use tabletop if live fault injection is not approved.

### F3. Advanced scenario model solutions

**D01 — Available but business deadline missed.**

- **Facts:** services are reported up; deadline missed; only 92% of expected records present.
- **Likely gap:** infrastructure availability is not equivalent to successful delivery. Investigate source arrival/completeness, CDC lag, schema rejection, orchestration dependencies, catalogue freshness, processing lag, semantic model refresh, and business calendar/time zone.
- **Immediate response:** declare severity based on regulatory impact; appoint incident command; prevent release of an incomplete report; notify the report owner/compliance contact; preserve evidence; identify missing partitions/records; recover and validate before release or invoke approved continuity procedure.
- **Objective redesign:** service availability; end-to-end freshness; completeness against expected manifests; reconciliation/correctness; report-ready-by-deadline; and consumer usability. Define denominators, windows, exclusions, and alert thresholds.
- **Trade-off/evidence:** more checks may increase latency and operational work but prevent incorrect reporting. Evidence includes source manifests, event-time lag, rejected-record counts, lineage, reconciliation totals, and timestamped consumer acceptance. Assumption to state: whether 92% is record-count completeness or a weighted business measure.

**D02 — Shared catalogue/deployment failure.** Map the catalogue and deployment control plane as shared domains; identify affected products and dependencies through lineage. Stop rollout, freeze dependent changes, prevent partial schema adoption, and use an approved rollback/recovery path that does not depend on the failed control plane (for example, separately secured emergency access and versioned known-good artifacts). Recover the catalogue, validate schema versions and permissions, then restart products in priority order. Reduce recurrence with staged/canary changes, compatibility checks, independent break-glass access, versioned configuration, clear owners, and tested rollback. Do not declare recovery merely because the catalogue endpoint responds: verify consumers and data correctness. Evidence: change logs, affected-product list, schema checks, rollback rehearsal, and successful downstream tests.

**D03 — Zone outage.** Defects include the single-zone metadata service and a health check that tests process liveness rather than data freshness/validity. Correct by distributing critical metadata capability across failure domains, making health/readiness checks reflect required dependencies and stale-data limits, and defining safe degraded behaviour when metadata is unavailable. Test zone loss in a controlled simulation; measure traffic recovery, error rate, freshness, data correctness, and downstream report usability. Check shared network, identity, DNS, keys, and deployment controls to avoid another common dependency. A third serving instance alone does not fix the metadata dependency.

**D04 — Corruption replicated.** Do not fail over to the corrupted replica as if it were a clean copy. Contain writes and downstream publication; declare incident and identify corruption start time/version via lineage and audit evidence; choose a trusted point before corruption; restore from immutable/versioned recovery material; recover metadata, keys, and offsets; reprocess trusted raw inputs with a known transformation version; reconcile against source/business totals; verify duplicates, missing records, and consumer outputs; obtain data-owner approval before resuming publication. Preserve corrupt artifacts for investigation where policy permits. Corrective actions may include quality gates, versioned transformations, independent recovery points, and tests for replicated corruption. Evidence: identified clean recovery point, lineage, hashes/counts, reconciliation, and signed release gate.

**D05 — RPO/backup mismatch.** A four-hour backup interval permits a recovery point nearly four hours old under ideal scheduling, far beyond a 20-minute RPO. Options: continuous change capture with point-in-time recovery; frequent log/object snapshots with completion and retention controls; synchronous/asynchronous replication where latency and failure modes fit; or explicitly renegotiate the RPO if business analysis permits. Keep independent immutable backups for corruption/deletion scenarios. Monitor capture lag and backup completion; test restore to a timestamp and compare the latest committed source event with recovered state. A configured interval is not proof of achieved RPO.

**D06 — RTO omits replay/validation.** Total realistic time = 20 + 30 + 35 + 25 = **110 minutes**, not 50 minutes, before any unlisted declaration, identity, consumer-switching, or contingency time. The stated claim omits 60 minutes of required work. If the target is firm, reduce measured steps through pre-provisioning, faster restore, incremental change capture, automated replay, and parallelisable tasks; rehearse and measure the complete sequence. Alternatively define a clearly approved degraded service that meets business need sooner while full correctness validation continues—but do not mislabel degraded service as full recovery. Include a time budget and evidence for every dependency.

**D07 — Backfill competes with live work.** Prioritise live fraud freshness and allocate separate compute/queues or quotas; schedule backfill off-peak where possible; throttle based on live lag and error-budget thresholds; checkpoint bounded partitions; use idempotent writes and deterministic inputs; pin code/data versions; and maintain cancellation/resume controls. Pause when lag crosses the agreed threshold, the live SLO is at risk, resource saturation threatens recovery capacity, or correctness checks fail. Resume only after capacity and backlog are understood. Validate historical outputs separately before publication. Evidence: live lag, queue depth, compute saturation, checkpoint progress, and reconciliation.

**D08 — Ownership/runbook gap.** Assign one incident commander with authority to set severity and coordinate; named technical leads for ingestion, orchestration/catalogue, and reporting; a communications lead; and a business/data owner who approves correctness and release. Define escalation timers, status updates, decision log, timeline, and stop conditions. Keep the report withheld until expected counts and reconciliation pass or an approved exception is recorded. Postmortem actions should have an owner, due date, risk/severity, measurable acceptance test, and retest evidence. “Restored” must have a shared definition across teams.

**D09 — Test passes technically, fails business.** The test's success criteria were too narrow and the dependency map omitted identity, reference data, and manual operations. Reframe the objective around completion of the critical business function, not merely infrastructure recovery. Involve business operators, identity/security, reference-data owners, and downstream consumers. Exercise degraded-mode access and staffing, validate reference-data availability and quality, test the manual workaround and hand-back criteria, and include communications. Retest immediately for high-risk omissions, then schedule periodic tests based on business criticality and change/failure risk. Evidence includes task completion, elapsed time, data correctness, access proof, workload capacity, and business-owner sign-off.

### F4. Integrated case study model answer

**E2.1 — Objectives.** Example indicators: (1) fraud-view request success rate and latency; (2) event-time freshness/consumer lag; (3) expected-versus-ingested/curated record completeness; (4) reconciliation/correctness checks; (5) report-ready-by-06:00 rate; and (6) validated recovery time/RPO during DR tests. Use the scenario's illustrative 99.95% monthly availability and ≤2-minute freshness for fraud, report-by-06:00 with ≥99.5% completeness and approved reconciliation tolerance, RPO ≤10 minutes, report RTO ≤3 hours, and fraud degraded mode ≤30 minutes. A report can be ready but wrong, or correct but late; readiness and correctness are separate release gates. **Evidence:** metric definitions, source manifests, freshness timestamps, reconciliation rules, and business acceptance.

**E2.2 — Failure domains.** Map source systems/API; network/DNS; identity/keys; event broker; schema registry/catalogue; processing/compute; object storage; orchestration; deployment control plane; semantic/reporting layer; and business access/workaround. Common-cause risks include identity/deployment dependence on the primary region and catalogue failure affecting multiple products. Contain with independently recoverable access, versioned metadata/configuration, zone/region separation, bounded retries, immutable raw retention, explicit ownership, and tested degraded modes. Prioritise domains by product criticality and observed blast radius.

**E2.3 — HA.** Use zone-separated serving capacity with health/readiness checks that include freshness and dependency validity; isolate metadata/control dependencies or provide tested cross-zone capability; preserve safe routing and avoid split-brain writes. For the report, batch completion and correctness gates matter as much as serving availability. Do not invent end-to-end availability because component availabilities are not supplied. Measure each critical-path dependency's SLI, joint outage/correlation, failover time, capacity under single-zone loss, and consumer-level success. Calculate a series product only for a justified independent series path; model parallel paths using their actual failover/routing behaviour.

**E2.4 — Recovery sequence.** Declare incident and preserve evidence; establish authority/access and encryption keys; select a clean recovery point; provision environment and network; restore immutable raw and curated data plus metadata/catalogue/schema versions; recover orchestration/configuration; recover broker offsets/checkpoints; replay from the trusted point; reconcile counts and critical totals; validate permissions and consumer queries/reports; switch consumers in priority order; obtain business owner approval; monitor lag and errors; document timestamps. Evidence includes backup manifest/hash/readability, record counts, schema/version compatibility, referential integrity, expected-vs-actual reconciliation, freshness, and a consumer-level acceptance test.

**E2.5 — RPO/RTO.** Recovery budget = 15 + 30 + 50 + 45 + 25 + 20 = **185 minutes**. The illustrative 3-hour (180-minute) RTO is missed by **5 minutes**, with no contingency. For the 10-minute RPO, a daily backup alone is insufficient. A plausible strategy combines frequent/continuous change capture or low-lag replication with independent point-in-time/immutable recovery for corruption; warm secondary capacity; tested identity, keys, metadata, and deployment recovery; and replay/reconciliation. Prove with a timestamped regional recovery exercise that records the latest recovered committed change, complete time to validated usable service, and business sign-off. Optimise the full sequence and add contingency before asserting compliance.

**E2.6 — Replay/backfill.** Recover source offsets and immutable raw data, define the 40-minute event-time range, pin schema and transformation versions, use stable event IDs and deduplication, replay in order where business semantics require it, checkpoint bounded chunks, and use idempotent upserts/partition replacement. Treat late events by explicit event-time/watermark rules; reconcile input/output counts and business totals. Isolate backfill resources or throttle by live fraud lag; stop if the 2-minute freshness SLO is threatened. Publish only after validation and retain evidence of the selected recovery point.

**E2.7 — Incident response.** Define severity based on fraud and regulatory impact; incident commander owns decisions and coordination; technical leads own each recovery workstream; security/identity owns access and keys; business risk/report owner approves data correctness and report release; communications lead sends timed updates. Log detection, acknowledgement, declaration, mitigation, restore, validation, and release timestamps. Include runbook prerequisites, dependency order, abort/rollback, no-write/split-brain checks, reconciliation gates, and escalation. Postmortem identifies contributing system conditions and tracks corrective actions with owners, deadlines, tests, and evidence.

**E2.8 — BC/resilience tests.** First use a tabletop to validate roles, decision rights, communications, and degraded fraud operations within 30 minutes. Then use controlled simulation or approved non-production fault injection for zone loss. Test regional loss plus replicated corruption separately: replica availability is not sufficient; the exercise must recover a clean point, replay trusted raw data, reconcile, and gain business release approval. Success thresholds use scenario targets (RPO ≤10 minutes, report usable ≤3 hours, degraded fraud mode ≤30 minutes), with the caveat that the present recovery budget currently totals 185 minutes and needs improvement. Safety controls: scoped fault, test lead, abort authority, rollback, known-good recovery material, no uncontrolled production writes, and stop conditions. Capture timestamps, logs, data-quality outputs, decision records, and actions.

**E2.9 — Consistency review.** Conflicts/missing proofs include: (1) daily backup cannot prove 10-minute RPO; (2) recovery budget is 185 minutes versus 180-minute RTO; (3) identity/deployment are not proven recoverable without the primary region; (4) restore and replay have not been tested together; (5) replicated corruption requires independent clean recovery points; (6) shared processing pool creates live-vs-backfill contention; (7) informal incident command creates decision ambiguity; (8) correctness/reconciliation thresholds and release authority need explicit definition; (9) fraud degraded mode needs a tested access/reference-data workaround; (10) capacity during regional failover must be measured. Resolve each with a design change, owner, acceptance criterion, and retest evidence.

### F5. Production evidence checklist for any answer

When a response claims that a design meets an objective, request evidence appropriate to the claim:

- **Objective:** approved SLI/SLO definition, denominator, window, exclusions, and business owner.
- **Failure containment:** dependency map, ownership, fault-injection/tabletop results, and blast-radius observations.
- **HA:** tested failover/failback, capacity during failure, health-check semantics, and shared-dependency analysis.
- **Backup/restore:** readable recovery artifact, keys/metadata, restore log, integrity checks, and consumer validation.
- **RPO/RTO:** measured recovery point and elapsed time through validated usable service, including replay and approvals.
- **Replay/backfill:** stable identity, idempotency tests, bounded range, checkpoints, reconciliation, and live-workload protection.
- **Incident response:** timeline, role assignments, decision log, runbook execution evidence, communications, and follow-up owners.
- **BC/resilience:** business task completed, workaround capacity demonstrated, test safety controls, measurable criteria, and retest closure.

---

## G. Scoring and evaluation rubric

### G1. Per-question scoring

Use the point value specified by the instructor or assign a default of 4 points per short answer and 8–12 points per multi-step scenario. Score the response against the criteria below rather than matching wording verbatim.

| Dimension | Full credit | Partial credit | No/very low credit |
| --- | --- | --- | --- |
| Conceptual correctness | Correct distinctions and terminology; no material contradiction | Main idea correct but one distinction is weak | Core concept confused or incorrect |
| Calculation accuracy | Formula, units, substitution, result, and interpretation all correct | Method largely right with minor arithmetic/unit error | Formula or interpretation materially wrong |
| Dependency/failure analysis | Identifies critical path, shared dependencies, correlated failure, and impact | Finds direct dependency but misses a meaningful common cause | Treats components as isolated without justification |
| Trade-off reasoning | Compares viable options against stated constraints and explains consequences | Recommendation plausible but alternatives or trade-offs thin | Unsupported universal claim or no rationale |
| Recovery feasibility | Includes complete elapsed recovery path, RPO/RTO, capacity, and prerequisites | Some recovery steps or assumptions omitted | Omits material steps such as replay, identity, or validation |
| Validation/evidence | Defines observable pass/fail evidence and business usability gate | Mentions tests but criteria are vague | Assumes success without proof |
| Operational safety | Defines authority, scope, abort/rollback, and safe sequencing where applicable | Mentions safety but leaves key controls unclear | Recommends uncontrolled production impact or unsafe writes |
| Clarity/traceability | Facts, assumptions, decisions, owners, and units are explicit | Understandable but some ambiguity remains | Cannot be audited or reproduced |

### G2. Correct, partially correct, and incorrect

- **Correct:** meets the core requirement, has reproducible calculations, states necessary assumptions, and includes relevant evidence/validation. For open-ended design, an alternative can be correct if it satisfies the constraints and discusses trade-offs.
- **Partially correct:** demonstrates the core concept but misses one or more important dependencies, calculation steps, assumptions, safety controls, or validation gates. Record the specific gap; do not award full credit for a lucky final number with no working.
- **Incorrect:** confuses core definitions, uses invalid arithmetic, contradicts supplied facts, ignores a critical dependency, claims an untested target is proven, or recommends a recovery sequence that risks data integrity.

### G3. Suggested learning thresholds

These are **suggested study thresholds**, not formal roadmap requirements:

- Beginner gate: at least 80% overall, with no topic below 60%.
- Intermediate gate: at least 80% overall, all calculations shown, and no unresolved material RPO/RTO or correctness error.
- Advanced/capstone gate: every critical scenario has a defensible decision, dependency analysis, validation evidence, and safe execution/abort plan.
- Readiness for the integrated plan: all eight topic areas addressed; no critical gap marked open; calculations independently reproducible; and all claims about recovery backed by a proposed test or measured evidence.

### G4. Architecture answer review rubric

For each open-ended answer, assign 0–2 points per criterion (0 = absent/incorrect; 1 = partial; 2 = clear and defensible):

1. Requirements and business impact are explicit.
2. Facts are separated from assumptions.
3. Dependencies and common-cause failures are identified.
4. At least two options are compared where a real trade-off exists.
5. RPO/RTO, capacity, and time budgets are feasible.
6. Data correctness and consumer validation are included.
7. Safety, authority, and rollback are addressed.
8. Evidence, ownership, and follow-up are actionable.

Maximum 16 points per scenario. A high score does not override a critical safety failure or an invalid recovery objective calculation.

---

## H. Gap log and remediation tracker

### H1. Error categories

- **Vocabulary:** terminology or conceptual distinction is wrong (for example, confusing RPO with RTO).
- **Calculation:** formula, arithmetic, unit, denominator, or time window is wrong.
- **Scenario analysis:** misses impact, trade-off, chronology, or decision constraints.
- **Missing dependency:** omits a component/team/control that can block or corrupt recovery.
- **Missing validation:** claims recovery without correctness, reconciliation, consumer usability, or evidence.

Add an additional note for unsupported assumption, communication, or safety issue when needed.

### H2. Copy-paste gap log

| Question ID | Topic | Attempt date | Result (correct/partial/incorrect) | Error category | Incorrect assumption or misconception | Correct reasoning | Remedial lesson or exercise | Re-attempt date | Re-attempt result | Closure status |
|---|---|---|---|---|---|---|---|---|---|---|
| B01 | Topic 1 — SLI/SLO/SLA | YYYY-MM-DD |  |  |  |  | `01-reliability-objectives-sli-slo-and-sla.md` |  |  | Open |
| C05 | Topic 3 — HA | YYYY-MM-DD |  |  |  |  | `03-high-availability-and-redundancy-patterns.md` |  |  | Open |
| C08 | Topic 4 — Restore | YYYY-MM-DD |  |  |  |  | `04-backup-restore-and-recovery-validation.md` |  |  | Open |
| C10 | Topic 5 — RTO | YYYY-MM-DD |  |  |  |  | `05-rpo-rto-and-disaster-recovery-strategies.md` |  |  | Open |
| C12 | Topic 6 — Replay | YYYY-MM-DD |  |  |  |  | `06-replay-reprocessing-and-backfill-architecture.md` |  |  | Open |
| D08 | Topic 7 — Incident response | YYYY-MM-DD |  |  |  |  | `07-incident-response-runbooks-and-postmortems.md` |  |  | Open |
| D09 | Topic 8 — Resilience testing | YYYY-MM-DD |  |  |  |  | `08-business-continuity-and-resilience-testing.md` |  |  | Open |
| E2.9 | Integrated case | YYYY-MM-DD |  |  |  |  | Revisit linked topics and resolve cross-topic conflicts |  |  | Open |

Duplicate rows as needed. Use one row per material misconception, even when several questions reveal the same gap. **Closure rule:** a gap is closed only after a successful re-attempt with correct reasoning and, where relevant, reproducible calculations or validation evidence.

---

## I. Final readiness assessment

Complete this section without consulting earlier answers. Suggested total: **100 points**. All targets and scenario values are illustrative. Answers follow the questions.

### I1. Questions

**R01 — Recall and distinction (8 points).** Define SLI, SLO, SLA, failure domain, blast radius, RPO, and RTO in one sentence each. Give one example of how an availability metric can hide a business failure.

**R02 — Error budget (6 points).** A service has a 99.95% monthly SLO over a 30-day, 720-hour month. Calculate allowed unavailability in minutes. If 12 minutes have been consumed, calculate the remaining budget.

**R03 — Failure-domain analysis (8 points).** A primary and secondary region have separate compute and storage, but share identity, DNS, and deployment automation. Name the three common dependencies, explain how each can defeat regional recovery, and propose a control or test for each.

**R04 — Availability arithmetic (8 points).** Two mandatory independent dependencies have availability 99.9% and 99.8%. Calculate series availability and approximate downtime in a 30-day month. State at least two caveats.

**R05 — Backup and RPO (8 points).** An immutable backup is completed every 2 hours; no continuous log capture exists. The business RPO is 30 minutes. Does this design satisfy the RPO? Explain what additional capability and evidence are required.

**R06 — RTO budget (8 points).** A target RTO is 150 minutes. Declaration takes 10 minutes, infrastructure/identity 25, data restore 40, replay 35, validation 20, and consumer switch 15. Calculate the full recovery time and pass/fail against the target.

**R07 — Replay correctness (8 points).** A replay can process a day of events twice. Describe controls that prevent duplicate or inconsistent outputs and prove correctness before publication.

**R08 — Incident leadership (8 points).** During a regional incident, two teams give conflicting recovery instructions and the report has not been reconciled. State the immediate governance actions and the conditions for release.

**R09 — BC vs DR (8 points).** Full fraud-platform recovery takes 2 hours, but business operations must continue within 20 minutes. Propose a business continuity approach and identify the evidence required to show that it is safe and adequate.

**R10 — Integrated scenario (16 points).** A regional failover completes in 70 minutes. The replica has 25 minutes of lag at the failure point, the RPO is 10 minutes, and a transformation bug may have corrupted the previous 3 hours of data. Can the team declare full recovery? Propose a safe sequence and identify which targets are met or missed.

**R11 — Evidence quality (8 points).** A report states “DR tested successfully in 45 minutes” but provides no definition of recovery, timestamps, data checks, or business sign-off. List at least six pieces of evidence needed to make the claim auditable.

**R12 — Architecture defence (8 points).** Choose one high-availability or DR design (active/standby, active/active, warm standby, restore-from-backup, or another justified pattern). State the requirements it addresses, at least two trade-offs, its major shared-dependency risks, and how you would prove it works.

### I2. Final assessment answer key

**R01.** SLI = measured service behaviour; SLO = target for an SLI over a stated window; SLA = agreement with commitments and potential consequences; failure domain = components sharing a failure mode/fate; blast radius = extent of impact; RPO = maximum tolerable data-loss interval; RTO = maximum tolerable time to restore an agreed service. An “up” pipeline may still miss freshness, completeness, correctness, or deadline requirements.

**R02.** Allowed downtime = 720 × (1 − 0.9995) hours = 0.36 hours = **21.6 minutes**. Remaining = 21.6 − 12 = **9.6 minutes**. Assumes a 30-day window and downtime-based SLI.

**R03.** Identity can prevent operators/services from authenticating; DNS can prevent access/routing to the secondary; deployment automation can block rollback or configuration. Controls: independently tested emergency access/identity recovery, alternate or recoverable DNS/routing, and versioned offline/independent deployment artifacts with a rehearsed recovery procedure. Include least privilege and auditability.

**R04.** Series availability = 0.999 × 0.998 = **0.997002**, or **99.7002%**. Unavailable time = 720 × (1 − 0.997002) = 2.15856 hours = **129.5136 minutes**, approximately 129.5 minutes. Caveats: independence may be false; availability definitions/windows may differ; dependency may not be mandatory for all requests; recovery and partial degradation may not map to binary downtime.

**R05.** No. A 2-hour interval permits a recovery point almost 2 hours old, exceeding a 30-minute RPO. Add verified change capture/replication or more frequent recovery points within a safe margin, and retain independent immutable recovery material for corruption. Prove with timestamped restore-to-point exercises and compare the latest recovered committed change to the source of truth; monitor lag and failed capture.

**R06.** Total = 10 + 25 + 40 + 35 + 20 + 15 = **145 minutes**. It meets the 150-minute target by **5 minutes**, but headroom is small; verify that no omitted dependency, approval, or contingency time exists. A pass should be based on measured validated recovery, not arithmetic alone.

**R07.** Use stable event IDs, deduplication, deterministic transformation versions, idempotent upserts or partition replacement, bounded input ranges, checkpointing, ordering/watermark rules, and safe handling of late events. Validate expected input/output counts, uniqueness, aggregates, reconciliation, freshness, and downstream consumers. Publish only after the release gate passes; preserve rollback/recovery material.

**R08.** Establish one incident commander and decision authority; assign technical leads; record conflicting instructions and a single decision log; halt risky writes/publication until state is understood; preserve evidence; identify a trusted recovery point; execute the approved runbook. Release only after data owner/authorized business owner confirms reconciliation, completeness, freshness, permissions, and consumer usability or explicitly approves a documented exception.

**R09.** Establish an approved degraded operating mode (for example, a controlled manual triage queue or restricted read-only risk view) within 20 minutes while full recovery continues. Define scope, prioritisation, staff/access, reference data, quality checks, maximum duration, escalation, and hand-back. Evidence includes a timed exercise, throughput/capacity, correctness checks, access controls, business task completion, and business-owner approval. Do not assume the workaround is adequate without a BIA.

**R10.** Do not declare full recovery yet. The 70-minute failover time may meet a particular RTO only if the target and endpoint match, but the 25-minute lag exceeds the 10-minute RPO. The possible 3-hour corruption means the replica may not be a trusted recovery point even if it were current. Contain publication/writes; declare incident; identify corruption window through lineage/audit evidence; choose a clean point before the bug; restore independent trusted data; replay/reprocess with corrected logic; reconcile and validate; obtain business approval. Report failover elapsed time separately from validated recovery. RPO is missed on the supplied lag; correctness remains unproven.

**R11.** Any six: explicit recovery endpoint definition; timestamped start/declaration/restore/validation/release milestones; selected recovery point and measured RPO; restore logs and backup integrity; identity/key/metadata recovery evidence; input/output counts and reconciliation; replay details and deduplication checks; consumer-level tests; capacity/lag metrics; runbook/version used; participant/owner sign-off; exceptions/findings and retest evidence.

**R12.** Score against the G4 rubric. A strong answer states requirements and assumptions; compares options; covers cost, consistency, complexity, capacity, and correlated failure; identifies identity/DNS/network/catalogue/key/deployment dependencies where relevant; and proposes a controlled exercise with measurable RPO/RTO, integrity, and business validation criteria. No pattern is universally best.

### I3. Suggested scoring interpretation

- **90–100:** strong readiness if no critical safety or recovery-correctness error remains.
- **80–89:** generally ready to draft the integrated plan; remediate weak topics and re-attempt missed questions.
- **65–79:** partial readiness; revisit intermediate calculations and cross-topic dependencies.
- **Below 65:** return to the roadmap sequence and complete each topic's practical evidence before attempting the integrated project again.

These bands are study guidance, not a formal roadmap requirement. A score does not override an unsafe recovery recommendation or a failure to recognize an RPO/RTO breach.

---

## J. Completion checklist

Use this before considering the question bank complete for your own learning:

- [ ] I can distinguish SLI, SLO, and SLA and calculate error budgets.
- [ ] I can map failure domains, common dependencies, and blast radius.
- [ ] I can compare HA patterns and state the assumptions behind availability calculations.
- [ ] I can explain why backup success is not recovery proof and define restore validation.
- [ ] I can test whether a proposed backup/replication approach meets RPO and whether the full recovery path meets RTO.
- [ ] I can plan safe replay/reprocessing/backfill with idempotency, checkpoints, and reconciliation.
- [ ] I can write an incident runbook with roles, escalation, decision gates, rollback, and evidence.
- [ ] I can connect DR to BC, BIA, degraded modes, test safety, and business success criteria.
- [ ] I have completed the integrated case and resolved cross-topic contradictions.
- [ ] Every material gap has a remedial action, a re-attempt, and evidence of closure.

**Completion rule:** the roadmap's purpose is demonstrated when the learner can defend an integrated disaster recovery and resilience plan. A high question-bank score alone is not proof that an untested production system meets its objectives.
