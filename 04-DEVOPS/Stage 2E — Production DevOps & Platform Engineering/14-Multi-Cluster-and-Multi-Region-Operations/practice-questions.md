# M14 Practice Questions --- Multi-Cluster and Multi-Region Operations

> **Target filename:** `practice-questions.md`\
> **Target path:**
> `Stage 2E — Production DevOps & Platform Engineering/14-Multi-Cluster-and-Multi-Region-Operations/practice-questions.md`\
> **Stage:** Stage 2E --- Production DevOps & Platform Engineering\
> **Module:** M14 --- Multi-Cluster and Multi-Region Operations, Unit 9
> assessment bank\
> **Estimated time:** 25--40 hours, illustrative\
> **Tool baseline:** exact versions not inventoried; version-sensitive
> details are `[VERIFY]`\
> **Last reviewed:** 2026-10-29

## Scope and source notes

This is an assessment bank, not a replacement syllabus. The supplied
Unit 9 prompt is the authority for required counts, question types,
safety constraints, and cross-unit scope. A related readable
`Roadmap(20261029-114814).md` tree excerpt confirms the Stage 2E/M14
context, but the exact file `Roadmap_ptree.md` was not available under
that name. The Unit 9 prompt was read; the primary M14 prompt and final
Unit 1--8 lesson files were not independently verified line-by-line.
Therefore, this bank is aligned to the supplied assessment prompt and
readable M14 excerpts, not claimed to be cross-checked against every
final lesson.

Labels: **\[ROADMAP REQUIREMENT\]** is explicit in the supplied prompt;
**\[ASSUMPTION\]** states a premise; **\[SYNTHETIC\]/\[ILLUSTRATIVE\]**
marks invented data; **\[VERIFY\]** marks version/environment-sensitive
behavior. No commands, tests, failovers, or production incidents are
claimed to have been executed.

## How to use this bank

Attempt each prompt before reading the answer. Score reasoning and
evidence, not guessing. Every scored question has a unique ID, domain,
level, type, objective, time estimate, model answer and common wrong
answer. MCQs have exactly four options with an explanation for every
distractor. Configuration reviews identify at least three defects,
corrections, and failure consequences. Accept alternative designs when
assumptions and trade-offs are defensible.

The zero-budget baseline uses two local `kind` clusters on one laptop.
They share host and failure domains; they are not two geographic regions
and cannot prove real WAN behavior, independent regional resilience,
provider routing, or production-scale capacity. No question requires
destructive action against real systems or production credentials.

## Levels and scoring

-   **L1 --- Foundations:** explain concepts and interpret basic
    artifacts.
-   **L2 --- Working practice:** reason about two lab clusters and
    diagnose common mistakes.
-   **L3 --- Production engineering:** design under blast-radius,
    consistency, latency, cost, compliance, and operability constraints.
-   **L4 --- Under failure:** govern a fleet, handle management-plane
    failures, and reason with incomplete evidence.

**Scoring:** 80--100% proceed to the next activity; 60--79% remediate
weak areas and retry; below 60% repeat the unit and associated labs.
Quiz performance alone is not production readiness; hands-on execution,
measured evidence, peer review and real-environment validation are also
required.

## Count contract

  Set                                  Required        Included
  -------------------------------- ------------ ---------------
  Unit 1--8                            ≥19 each   19 each = 152
  Cross-unit scenarios                      ≥40              40
  **Scored total**                     **≥192**         **192**
  Separate design-review prompts     exactly 16              16

Each unit has 3 conceptual short answers, 3 four-option MCQs, 3
synthetic artifact interpretations, 3 configuration reviews, 1 incident,
1 rubric-scored design question, and 5 additional questions. IDs are
unique and no question is double-counted.

## Table of contents

1.  [Unit 1 --- Multi-Cluster Topologies and When to Split
    Clusters](#unit-1)
2.  [Unit 2 --- Fleet Management and Cluster Lifecycle with Cluster
    API](#unit-2)
3.  [Unit 3 --- Multi-Cluster GitOps and Config Propagation](#unit-3)
4.  [Unit 4 --- Cross-Cluster Service Discovery and Traffic
    Routing](#unit-4)
5.  [Unit 5 --- Global Load Balancing and DNS Failover](#unit-5)
6.  [Unit 6 --- Active-Active vs Active-Passive Regional
    Designs](#unit-6)
7.  [Unit 7 --- Data Replication and Consistency Across
    Regions](#unit-7)
8.  [Unit 8 --- Multi-Cluster Observability and Policy
    Governance](#unit-8)
9.  [Cross-unit integration
    scenarios](#cross-unit-integration-scenarios)
10. [Design-review whiteboard
    prompts](#design-review-whiteboard-prompts)
11. [Glossary](#glossary)
12. [Coverage matrix and verification
    notes](#coverage-matrix-and-verification-notes)
13. [Roadmap Alignment and Authenticity
    Audit](#roadmap-alignment-and-authenticity-audit)

## Unit 1 --- Multi-Cluster Topologies and When to Split Clusters

**Scope:** topology, blast radius, isolation, residency, team
boundaries, failure domains, cost and ADRs.

### U1-L1-SA-01 --- Conceptual short answer

-   **Domain:** Unit 1\
-   **Level:** L1\
-   **Objective:** Explain split versus single cluster and its
    operational consequence.\
-   **Estimated time:** 5 minutes

**Question**

Explain **split versus single cluster**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Split versus single cluster must be evaluated against the stated
topology, blast radius, isolation, residency, team boundaries, failure
domains, cost and ADRs. A strong answer identifies the requirement,
names the relevant cluster/failure boundary, distinguishes desired state
from observed evidence, and proposes a verification method plus a
corrective action. Record owner, timestamp and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U1-L1-SA-02 --- Conceptual short answer

-   **Domain:** Unit 1\
-   **Level:** L1\
-   **Objective:** Explain cluster-per-region and cluster-per-tenant and
    its operational consequence.\
-   **Estimated time:** 6 minutes

**Question**

Explain **cluster-per-region and cluster-per-tenant**. State why it
matters, one failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Cluster-per-region and cluster-per-tenant must be evaluated against the
stated topology, blast radius, isolation, residency, team boundaries,
failure domains, cost and ADRs. A strong answer identifies the
requirement, names the relevant cluster/failure boundary, distinguishes
desired state from observed evidence, and proposes a verification method
plus a corrective action. Record owner, timestamp and scope where
relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U1-L2-SA-03 --- Conceptual short answer

-   **Domain:** Unit 1\
-   **Level:** L2\
-   **Objective:** Explain shared dependencies and correlated failures
    and its operational consequence.\
-   **Estimated time:** 7 minutes

**Question**

Explain **shared dependencies and correlated failures**. State why it
matters, one failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Shared dependencies and correlated failures must be evaluated against
the stated topology, blast radius, isolation, residency, team
boundaries, failure domains, cost and ADRs. A strong answer identifies
the requirement, names the relevant cluster/failure boundary,
distinguishes desired state from observed evidence, and proposes a
verification method plus a corrective action. Record owner, timestamp
and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U1-L1-MCQ-01 --- Multiple choice (exactly four options)

-   **Domain:** Unit 1\
-   **Level:** L1\
-   **Objective:** Choose a safe decision about stateful versus
    stateless placement.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **stateful versus stateless
placement** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for stateful versus stateless placement.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U1-L2-MCQ-02 --- Multiple choice (exactly four options)

-   **Domain:** Unit 1\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about residency and telemetry
    boundaries.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **residency and telemetry
boundaries** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for residency and telemetry boundaries.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U1-L2-MCQ-03 --- Multiple choice (exactly four options)

-   **Domain:** Unit 1\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about team ownership and
    on-call.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **team ownership and on-call**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for team ownership and on-call.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U1-L2-ART-01 --- Artifact interpretation

-   **Domain:** Unit 1\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    capacity and workload placement is safe.\
-   **Estimated time:** 6 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
cluster=stage2e-east-lab status=PASS timestamp=10:00Z
cluster=stage2e-west-lab status=UNKNOWN timestamp=09:00Z
expected_cluster_count=2 fresh_reports=1
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

East has fresh PASS evidence; West is UNKNOWN with stale evidence. The
fleet is not green. Identify West's local state and obtain fresh
evidence before a gated action. Preserve timestamps and source identity.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U1-L2-ART-02 --- Artifact interpretation

-   **Domain:** Unit 1\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    networking and identity overhead is safe.\
-   **Estimated time:** 7 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
revision=r42 target_clusters=2 ring=canary
stage2e-east-lab: health=PASS evidence=fresh
stage2e-west-lab: health=FAIL evidence=fresh
next_action=promote
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

Promotion is unsafe: West has a fresh FAIL. Halt the ring, preserve
revision and health evidence, mitigate the failing cluster, and require
fresh passing evidence before promotion. Sync/selection status does not
override health. Verify per cluster and retain the timestamp, revision,
target identity and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U1-L3-ART-03 --- Artifact interpretation

-   **Domain:** Unit 1\
-   **Level:** L3\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    ADR and scored decision matrix is safe.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
source=stage2e-east-lab target=stage2e-west-lab
last_seen=unknown; owner=platform
change_time=10:03Z; alert_time=10:04Z
summary=green
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

The summary conflicts with missing source/last-seen evidence. Mark the
affected path UNKNOWN, check source and target independently, correlate
the change and alert, and do not treat missing telemetry as healthy.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U1-L2-CFG-01 --- Configuration/artifact review

-   **Domain:** Unit 1\
-   **Level:** L2\
-   **Objective:** Review a scope/ownership artifact for at least three
    defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
target=all-clusters
owner=unspecified
health_gate=disabled
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Target is broad/ambiguous. **Correction:** Resolve and
    display the exact intended cluster set. **Failure avoided:**
    unintended clusters can be changed.
2.  **Defect:** Owner is missing. **Correction:** Assign accountable
    owner and approver. **Failure avoided:** incident response and
    decisions stall.
3.  **Defect:** Health gate is disabled. **Correction:** Add measurable
    per-cluster gates and halt conditions. **Failure avoided:** bad
    changes propagate unchecked.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U1-L3-CFG-02 --- Configuration/artifact review

-   **Domain:** Unit 1\
-   **Level:** L3\
-   **Objective:** Review a rollout/consistency artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
promote_on=sync-success-only
unknown_evidence=pass
rollback_revision=none
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Sync success is the only gate. **Correction:** Check
    runtime health and relevant data/policy/route signals. **Failure
    avoided:** desired state can apply while service fails.
2.  **Defect:** Unknown evidence passes. **Correction:** Represent
    UNKNOWN/UNREACHABLE and block critical promotion. **Failure
    avoided:** missing data creates false green.
3.  **Defect:** No rollback revision. **Correction:** Record a
    known-good revision and rollback criteria. **Failure avoided:**
    recovery is improvised under pressure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U1-L3-CFG-03 --- Configuration/artifact review

-   **Domain:** Unit 1\
-   **Level:** L3\
-   **Objective:** Review a security/evidence artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
credential_scope=fleet-admin
report_timestamp=omitted
verification=central-only
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Credential is overbroad. **Correction:** Use least
    privilege and narrower cluster scope. **Failure avoided:** hub
    compromise can affect the fleet.
2.  **Defect:** Timestamp/freshness omitted. **Correction:** Record
    timestamp, source and freshness threshold. **Failure avoided:**
    stale report can be mistaken for current.
3.  **Defect:** Only central verification. **Correction:** Verify
    affected clusters independently and retain local evidence. **Failure
    avoided:** hub outage/compromise can conceal failure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U1-L4-INC-01 --- Incident/diagnosis

-   **Domain:** Unit 1\

-   **Level:** L4\

-   **Objective:** Sequence an incident response involving topology,
    blast radius, isolation, residency, team boundaries, failure
    domains, cost and ADRs.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario only;
    no real-system mutation. **Question**

\[SYNTHETIC\] A change related to hidden shared failure domain is
followed by degraded behavior in stage2e-west-lab; stage2e-east-lab
telemetry is stale. Respond in this order: first safe action → localize
→ mitigate → verify per cluster → communicate → prevent.

**Model answer and reasoning**

First halt further ring promotion/fan-out and preserve evidence.
Localize by verifying explicit contexts, cluster identity, last-seen
timestamps, local health and change revision. Mitigate only the
implicated ring/dependency using an approved rollback or isolation path
after checking data/write authority where relevant. Verify East and West
independently: service health, configuration/policy revision,
data/traffic state and alert delivery. Communicate scope, known facts,
uncertainty, owner and next update per region. Prevent recurrence with a
regression test, stronger freshness/health gate, rollback rehearsal and
named follow-up.

**Common wrong answer(s)**

Wrong: change both clusters at once, assume stale telemetry means
recovery, declare a root cause without evidence, or fail to communicate
uncertainty.

**Scoring rubric**

5 points: safe halt/evidence preservation (1); correct localization (1);
bounded mitigation (1); independent verification and communication (1);
durable prevention (1).

### U1-L3-DES-01 --- Design question

-   **Domain:** Unit 1\
-   **Level:** L3\
-   **Objective:** Design an operating pattern for topology, blast
    radius, isolation, residency, team boundaries, failure domains, cost
    and ADRs.\
-   **Estimated time:** 15 minutes

**Question**

Design a zero-budget two-kind-cluster lab pattern that can later inform
a production design for topology, blast radius, isolation, residency,
team boundaries, failure domains, cost and ADRs. State requirements,
architecture, ownership, failure modes, safety gates, evidence, rollback
and limits of the lab.

**Model answer and reasoning**

A defensible design starts with business/security/SLO constraints and
failure domains, chooses the simplest architecture that meets them,
identifies the owner and exact target scope, defines per-cluster health
and UNKNOWN states, protects credentials, and gives a bounded
rollout/rollback plan. Explain cost, latency, consistency and
operational trade-offs. Explicitly state that two local kind clusters
share a host and do not prove geographic resilience.

**Common wrong answer(s)**

Wrong: select tools before requirements, omit ownership/rollback, rely
on a green aggregate, or claim a local lab proves production regions.

**Scoring rubric**

Score 0--4 each: correctness; trade-off reasoning; safety/blast-radius
control; evidence/verification; operational feasibility (20 points
total).

### U1-L2-CALC-01 --- Calculation

-   **Domain:** Unit 1\
-   **Level:** L2\
-   **Objective:** Calculate a fleet outcome from synthetic counts.\
-   **Estimated time:** 6 minutes

**Question**

\[SYNTHETIC\] East: 8,000 requests/min, 99.9% good. West: 2,000
requests/min, 90% good. Compute global success.

**Model answer and reasoning**

East good=8,000×0.999=7,992; West=2,000×0.90=1,800;
total=9,792/10,000=97.92%. Keep regional guardrails; a global ratio can
hide local harm.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U1-L3-EVID-02 --- Evidence quality

-   **Domain:** Unit 1\
-   **Level:** L3\
-   **Objective:** Distinguish workflow evidence from production
    assurance.\
-   **Estimated time:** 7 minutes

**Question**

An engineer says two local kind clusters passing a lab proves two-region
resilience. Is the claim justified?

**Model answer and reasoning**

No. The lab tests workflow mechanics only. Real proof needs independent
failure domains, real WAN/routing, data authority/recovery, capacity,
production telemetry and rehearsed operations.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U1-L3-COMP-03 --- Comparison

-   **Domain:** Unit 1\
-   **Level:** L3\
-   **Objective:** Compare simple lab and production architecture.\
-   **Estimated time:** 8 minutes

**Question**

Compare a low-cost local approach with a production fleet approach for
reliability objectives. Give one benefit, one cost and one failure mode
each.

**Model answer and reasoning**

Local is cheap and inspectable but shares host/failure domains and has
limited scale. Production can improve isolation/automation but adds
cost, control-plane dependencies and more failure modes. Choose from
requirements.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U1-L2-CTX-04 --- Context safety

-   **Domain:** Unit 1\
-   **Level:** L2\
-   **Objective:** Verify target before a cluster-scoped action.\
-   **Estimated time:** 9 minutes

**Question**

\[SYNTHETIC\] Context list: `* kind-stage2e-east-lab`;
`kind-stage2e-west-lab`. A change is intended for West. What must be
checked?

**Model answer and reasoning**

Use an explicit reviewed `--context kind-stage2e-west-lab`, verify it
maps to the intended disposable cluster, inspect namespace/resources and
use dry-run where useful. Verify results per cluster. Do not rely on the
current `*` context.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U1-L4-GATE-05 --- Evidence under uncertainty

-   **Domain:** Unit 1\
-   **Level:** L4\
-   **Objective:** Name evidence that should block promotion.\
-   **Estimated time:** 10 minutes

**Question**

For hard constraints versus weighted scores, list three independent
signals and one blocking condition.

**Model answer and reasoning**

Check source identity/freshness, local health/alert evidence, and the
unit-specific control (capacity/data/policy/routing/desired state).
Block on critical FAIL, UNKNOWN, stale evidence or ambiguous target.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

## Unit 2 --- Fleet Management and Cluster Lifecycle with Cluster API

**Scope:** cluster registry, context safety, CIDR planning, lifecycle,
upgrades, replacement, decommission and management-plane loss.

### U2-L1-SA-01 --- Conceptual short answer

-   **Domain:** Unit 2\
-   **Level:** L1\
-   **Objective:** Explain registry identity and owner fields and its
    operational consequence.\
-   **Estimated time:** 5 minutes

**Question**

Explain **registry identity and owner fields**. State why it matters,
one failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Registry identity and owner fields must be evaluated against the stated
cluster registry, context safety, CIDR planning, lifecycle, upgrades,
replacement, decommission and management-plane loss. A strong answer
identifies the requirement, names the relevant cluster/failure boundary,
distinguishes desired state from observed evidence, and proposes a
verification method plus a corrective action. Record owner, timestamp
and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U2-L1-SA-02 --- Conceptual short answer

-   **Domain:** Unit 2\
-   **Level:** L1\
-   **Objective:** Explain explicit kubectl context safety and its
    operational consequence.\
-   **Estimated time:** 6 minutes

**Question**

Explain **explicit kubectl context safety**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Explicit kubectl context safety must be evaluated against the stated
cluster registry, context safety, CIDR planning, lifecycle, upgrades,
replacement, decommission and management-plane loss. A strong answer
identifies the requirement, names the relevant cluster/failure boundary,
distinguishes desired state from observed evidence, and proposes a
verification method plus a corrective action. Record owner, timestamp
and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U2-L2-SA-03 --- Conceptual short answer

-   **Domain:** Unit 2\
-   **Level:** L2\
-   **Objective:** Explain pod/service CIDR overlap and its operational
    consequence.\
-   **Estimated time:** 7 minutes

**Question**

Explain **pod/service CIDR overlap**. State why it matters, one failure
mode, and what evidence would verify the claim.

**Model answer and reasoning**

Pod/service cidr overlap must be evaluated against the stated cluster
registry, context safety, CIDR planning, lifecycle, upgrades,
replacement, decommission and management-plane loss. A strong answer
identifies the requirement, names the relevant cluster/failure boundary,
distinguishes desired state from observed evidence, and proposes a
verification method plus a corrective action. Record owner, timestamp
and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U2-L1-MCQ-01 --- Multiple choice (exactly four options)

-   **Domain:** Unit 2\
-   **Level:** L1\
-   **Objective:** Choose a safe decision about lifecycle states and
    gates.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **lifecycle states and gates**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for lifecycle states and gates.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U2-L2-MCQ-02 --- Multiple choice (exactly four options)

-   **Domain:** Unit 2\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about Cluster API/provider
    version verification.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **Cluster API/provider version
verification** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for Cluster API/provider version verification.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U2-L2-MCQ-03 --- Multiple choice (exactly four options)

-   **Domain:** Unit 2\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about staged fleet upgrades.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **staged fleet upgrades** under
the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for staged fleet upgrades.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U2-L2-ART-01 --- Artifact interpretation

-   **Domain:** Unit 2\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    blue/green cluster replacement is safe.\
-   **Estimated time:** 6 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
cluster=stage2e-east-lab status=PASS timestamp=10:00Z
cluster=stage2e-west-lab status=UNKNOWN timestamp=09:00Z
expected_cluster_count=2 fresh_reports=1
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

East has fresh PASS evidence; West is UNKNOWN with stale evidence. The
fleet is not green. Identify West's local state and obtain fresh
evidence before a gated action. Preserve timestamps and source identity.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U2-L2-ART-02 --- Artifact interpretation

-   **Domain:** Unit 2\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    decommission evidence is safe.\
-   **Estimated time:** 7 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
revision=r42 target_clusters=2 ring=canary
stage2e-east-lab: health=PASS evidence=fresh
stage2e-west-lab: health=FAIL evidence=fresh
next_action=promote
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

Promotion is unsafe: West has a fresh FAIL. Halt the ring, preserve
revision and health evidence, mitigate the failing cluster, and require
fresh passing evidence before promotion. Sync/selection status does not
override health. Verify per cluster and retain the timestamp, revision,
target identity and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U2-L3-ART-03 --- Artifact interpretation

-   **Domain:** Unit 2\
-   **Level:** L3\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    management-plane outage is safe.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
source=stage2e-east-lab target=stage2e-west-lab
last_seen=unknown; owner=platform
change_time=10:03Z; alert_time=10:04Z
summary=green
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

The summary conflicts with missing source/last-seen evidence. Mark the
affected path UNKNOWN, check source and target independently, correlate
the change and alert, and do not treat missing telemetry as healthy.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U2-L2-CFG-01 --- Configuration/artifact review

-   **Domain:** Unit 2\
-   **Level:** L2\
-   **Objective:** Review a scope/ownership artifact for at least three
    defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
target=all-clusters
owner=unspecified
health_gate=disabled
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Target is broad/ambiguous. **Correction:** Resolve and
    display the exact intended cluster set. **Failure avoided:**
    unintended clusters can be changed.
2.  **Defect:** Owner is missing. **Correction:** Assign accountable
    owner and approver. **Failure avoided:** incident response and
    decisions stall.
3.  **Defect:** Health gate is disabled. **Correction:** Add measurable
    per-cluster gates and halt conditions. **Failure avoided:** bad
    changes propagate unchecked.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U2-L3-CFG-02 --- Configuration/artifact review

-   **Domain:** Unit 2\
-   **Level:** L3\
-   **Objective:** Review a rollout/consistency artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
promote_on=sync-success-only
unknown_evidence=pass
rollback_revision=none
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Sync success is the only gate. **Correction:** Check
    runtime health and relevant data/policy/route signals. **Failure
    avoided:** desired state can apply while service fails.
2.  **Defect:** Unknown evidence passes. **Correction:** Represent
    UNKNOWN/UNREACHABLE and block critical promotion. **Failure
    avoided:** missing data creates false green.
3.  **Defect:** No rollback revision. **Correction:** Record a
    known-good revision and rollback criteria. **Failure avoided:**
    recovery is improvised under pressure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U2-L3-CFG-03 --- Configuration/artifact review

-   **Domain:** Unit 2\
-   **Level:** L3\
-   **Objective:** Review a security/evidence artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
credential_scope=fleet-admin
report_timestamp=omitted
verification=central-only
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Credential is overbroad. **Correction:** Use least
    privilege and narrower cluster scope. **Failure avoided:** hub
    compromise can affect the fleet.
2.  **Defect:** Timestamp/freshness omitted. **Correction:** Record
    timestamp, source and freshness threshold. **Failure avoided:**
    stale report can be mistaken for current.
3.  **Defect:** Only central verification. **Correction:** Verify
    affected clusters independently and retain local evidence. **Failure
    avoided:** hub outage/compromise can conceal failure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U2-L4-INC-01 --- Incident/diagnosis

-   **Domain:** Unit 2\

-   **Level:** L4\

-   **Objective:** Sequence an incident response involving cluster
    registry, context safety, CIDR planning, lifecycle, upgrades,
    replacement, decommission and management-plane loss.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario only;
    no real-system mutation. **Question**

\[SYNTHETIC\] A change related to version/support inventory is followed
by degraded behavior in stage2e-west-lab; stage2e-east-lab telemetry is
stale. Respond in this order: first safe action → localize → mitigate →
verify per cluster → communicate → prevent.

**Model answer and reasoning**

First halt further ring promotion/fan-out and preserve evidence.
Localize by verifying explicit contexts, cluster identity, last-seen
timestamps, local health and change revision. Mitigate only the
implicated ring/dependency using an approved rollback or isolation path
after checking data/write authority where relevant. Verify East and West
independently: service health, configuration/policy revision,
data/traffic state and alert delivery. Communicate scope, known facts,
uncertainty, owner and next update per region. Prevent recurrence with a
regression test, stronger freshness/health gate, rollback rehearsal and
named follow-up.

**Common wrong answer(s)**

Wrong: change both clusters at once, assume stale telemetry means
recovery, declare a root cause without evidence, or fail to communicate
uncertainty.

**Scoring rubric**

5 points: safe halt/evidence preservation (1); correct localization (1);
bounded mitigation (1); independent verification and communication (1);
durable prevention (1).

### U2-L3-DES-01 --- Design question

-   **Domain:** Unit 2\
-   **Level:** L3\
-   **Objective:** Design an operating pattern for cluster registry,
    context safety, CIDR planning, lifecycle, upgrades, replacement,
    decommission and management-plane loss.\
-   **Estimated time:** 15 minutes

**Question**

Design a zero-budget two-kind-cluster lab pattern that can later inform
a production design for cluster registry, context safety, CIDR planning,
lifecycle, upgrades, replacement, decommission and management-plane
loss. State requirements, architecture, ownership, failure modes, safety
gates, evidence, rollback and limits of the lab.

**Model answer and reasoning**

A defensible design starts with business/security/SLO constraints and
failure domains, chooses the simplest architecture that meets them,
identifies the owner and exact target scope, defines per-cluster health
and UNKNOWN states, protects credentials, and gives a bounded
rollout/rollback plan. Explain cost, latency, consistency and
operational trade-offs. Explicitly state that two local kind clusters
share a host and do not prove geographic resilience.

**Common wrong answer(s)**

Wrong: select tools before requirements, omit ownership/rollback, rely
on a green aggregate, or claim a local lab proves production regions.

**Scoring rubric**

Score 0--4 each: correctness; trade-off reasoning; safety/blast-radius
control; evidence/verification; operational feasibility (20 points
total).

### U2-L2-CALC-01 --- Calculation

-   **Domain:** Unit 2\
-   **Level:** L2\
-   **Objective:** Calculate a fleet outcome from synthetic counts.\
-   **Estimated time:** 6 minutes

**Question**

\[SYNTHETIC\] East: 8,000 requests/min, 99.9% good. West: 2,000
requests/min, 90% good. Compute global success.

**Model answer and reasoning**

East good=8,000×0.999=7,992; West=2,000×0.90=1,800;
total=9,792/10,000=97.92%. Keep regional guardrails; a global ratio can
hide local harm.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U2-L3-EVID-02 --- Evidence quality

-   **Domain:** Unit 2\
-   **Level:** L3\
-   **Objective:** Distinguish workflow evidence from production
    assurance.\
-   **Estimated time:** 7 minutes

**Question**

An engineer says two local kind clusters passing a lab proves two-region
resilience. Is the claim justified?

**Model answer and reasoning**

No. The lab tests workflow mechanics only. Real proof needs independent
failure domains, real WAN/routing, data authority/recovery, capacity,
production telemetry and rehearsed operations.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U2-L3-COMP-03 --- Comparison

-   **Domain:** Unit 2\
-   **Level:** L3\
-   **Objective:** Compare simple lab and production architecture.\
-   **Estimated time:** 8 minutes

**Question**

Compare a low-cost local approach with a production fleet approach for
network ranges in route plan. Give one benefit, one cost and one failure
mode each.

**Model answer and reasoning**

Local is cheap and inspectable but shares host/failure domains and has
limited scale. Production can improve isolation/automation but adds
cost, control-plane dependencies and more failure modes. Choose from
requirements.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U2-L2-CTX-04 --- Context safety

-   **Domain:** Unit 2\
-   **Level:** L2\
-   **Objective:** Verify target before a cluster-scoped action.\
-   **Estimated time:** 9 minutes

**Question**

\[SYNTHETIC\] Context list: `* kind-stage2e-east-lab`;
`kind-stage2e-west-lab`. A change is intended for West. What must be
checked?

**Model answer and reasoning**

Use an explicit reviewed `--context kind-stage2e-west-lab`, verify it
maps to the intended disposable cluster, inspect namespace/resources and
use dry-run where useful. Verify results per cluster. Do not rely on the
current `*` context.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U2-L4-GATE-05 --- Evidence under uncertainty

-   **Domain:** Unit 2\
-   **Level:** L4\
-   **Objective:** Name evidence that should block promotion.\
-   **Estimated time:** 10 minutes

**Question**

For provider variability, list three independent signals and one
blocking condition.

**Model answer and reasoning**

Check source identity/freshness, local health/alert evidence, and the
unit-specific control (capacity/data/policy/routing/desired state).
Block on critical FAIL, UNKNOWN, stale evidence or ambiguous target.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

## Unit 3 --- Multi-Cluster GitOps and Config Propagation

**Scope:** hub/spoke, selectors, fan-out, rings, dependency ordering,
least privilege, rollback and hub failure.

### U3-L1-SA-01 --- Conceptual short answer

-   **Domain:** Unit 3\
-   **Level:** L1\
-   **Objective:** Explain hub/spoke trust boundary and its operational
    consequence.\
-   **Estimated time:** 5 minutes

**Question**

Explain **hub/spoke trust boundary**. State why it matters, one failure
mode, and what evidence would verify the claim.

**Model answer and reasoning**

Hub/spoke trust boundary must be evaluated against the stated hub/spoke,
selectors, fan-out, rings, dependency ordering, least privilege,
rollback and hub failure. A strong answer identifies the requirement,
names the relevant cluster/failure boundary, distinguishes desired state
from observed evidence, and proposes a verification method plus a
corrective action. Record owner, timestamp and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U3-L1-SA-02 --- Conceptual short answer

-   **Domain:** Unit 3\
-   **Level:** L1\
-   **Objective:** Explain resolved fan-out target set and its
    operational consequence.\
-   **Estimated time:** 6 minutes

**Question**

Explain **resolved fan-out target set**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Resolved fan-out target set must be evaluated against the stated
hub/spoke, selectors, fan-out, rings, dependency ordering, least
privilege, rollback and hub failure. A strong answer identifies the
requirement, names the relevant cluster/failure boundary, distinguishes
desired state from observed evidence, and proposes a verification method
plus a corrective action. Record owner, timestamp and scope where
relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U3-L2-SA-03 --- Conceptual short answer

-   **Domain:** Unit 3\
-   **Level:** L2\
-   **Objective:** Explain canary ring and promotion gates and its
    operational consequence.\
-   **Estimated time:** 7 minutes

**Question**

Explain **canary ring and promotion gates**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Canary ring and promotion gates must be evaluated against the stated
hub/spoke, selectors, fan-out, rings, dependency ordering, least
privilege, rollback and hub failure. A strong answer identifies the
requirement, names the relevant cluster/failure boundary, distinguishes
desired state from observed evidence, and proposes a verification method
plus a corrective action. Record owner, timestamp and scope where
relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U3-L1-MCQ-01 --- Multiple choice (exactly four options)

-   **Domain:** Unit 3\
-   **Level:** L1\
-   **Objective:** Choose a safe decision about
    CRD-before-custom-resource ordering.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **CRD-before-custom-resource
ordering** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for CRD-before-custom-resource ordering.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U3-L2-MCQ-02 --- Multiple choice (exactly four options)

-   **Domain:** Unit 3\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about selector drift and
    deletion scope.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **selector drift and deletion
scope** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for selector drift and deletion scope.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U3-L2-MCQ-03 --- Multiple choice (exactly four options)

-   **Domain:** Unit 3\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about least-privilege spoke
    credentials.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **least-privilege spoke
credentials** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for least-privilege spoke credentials.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U3-L2-ART-01 --- Artifact interpretation

-   **Domain:** Unit 3\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    hub outage and running workloads is safe.\
-   **Estimated time:** 6 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
cluster=stage2e-east-lab status=PASS timestamp=10:00Z
cluster=stage2e-west-lab status=UNKNOWN timestamp=09:00Z
expected_cluster_count=2 fresh_reports=1
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

East has fresh PASS evidence; West is UNKNOWN with stale evidence. The
fleet is not green. Identify West's local state and obtain fresh
evidence before a gated action. Preserve timestamps and source identity.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U3-L2-ART-02 --- Artifact interpretation

-   **Domain:** Unit 3\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    rollback verification is safe.\
-   **Estimated time:** 7 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
revision=r42 target_clusters=2 ring=canary
stage2e-east-lab: health=PASS evidence=fresh
stage2e-west-lab: health=FAIL evidence=fresh
next_action=promote
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

Promotion is unsafe: West has a fresh FAIL. Halt the ring, preserve
revision and health evidence, mitigate the failing cluster, and require
fresh passing evidence before promotion. Sync/selection status does not
override health. Verify per cluster and retain the timestamp, revision,
target identity and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U3-L3-ART-03 --- Artifact interpretation

-   **Domain:** Unit 3\
-   **Level:** L3\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    quarantine and ring advancement is safe.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
source=stage2e-east-lab target=stage2e-west-lab
last_seen=unknown; owner=platform
change_time=10:03Z; alert_time=10:04Z
summary=green
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

The summary conflicts with missing source/last-seen evidence. Mark the
affected path UNKNOWN, check source and target independently, correlate
the change and alert, and do not treat missing telemetry as healthy.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U3-L2-CFG-01 --- Configuration/artifact review

-   **Domain:** Unit 3\
-   **Level:** L2\
-   **Objective:** Review a scope/ownership artifact for at least three
    defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
target=all-clusters
owner=unspecified
health_gate=disabled
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Target is broad/ambiguous. **Correction:** Resolve and
    display the exact intended cluster set. **Failure avoided:**
    unintended clusters can be changed.
2.  **Defect:** Owner is missing. **Correction:** Assign accountable
    owner and approver. **Failure avoided:** incident response and
    decisions stall.
3.  **Defect:** Health gate is disabled. **Correction:** Add measurable
    per-cluster gates and halt conditions. **Failure avoided:** bad
    changes propagate unchecked.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U3-L3-CFG-02 --- Configuration/artifact review

-   **Domain:** Unit 3\
-   **Level:** L3\
-   **Objective:** Review a rollout/consistency artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
promote_on=sync-success-only
unknown_evidence=pass
rollback_revision=none
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Sync success is the only gate. **Correction:** Check
    runtime health and relevant data/policy/route signals. **Failure
    avoided:** desired state can apply while service fails.
2.  **Defect:** Unknown evidence passes. **Correction:** Represent
    UNKNOWN/UNREACHABLE and block critical promotion. **Failure
    avoided:** missing data creates false green.
3.  **Defect:** No rollback revision. **Correction:** Record a
    known-good revision and rollback criteria. **Failure avoided:**
    recovery is improvised under pressure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U3-L3-CFG-03 --- Configuration/artifact review

-   **Domain:** Unit 3\
-   **Level:** L3\
-   **Objective:** Review a security/evidence artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
credential_scope=fleet-admin
report_timestamp=omitted
verification=central-only
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Credential is overbroad. **Correction:** Use least
    privilege and narrower cluster scope. **Failure avoided:** hub
    compromise can affect the fleet.
2.  **Defect:** Timestamp/freshness omitted. **Correction:** Record
    timestamp, source and freshness threshold. **Failure avoided:**
    stale report can be mistaken for current.
3.  **Defect:** Only central verification. **Correction:** Verify
    affected clusters independently and retain local evidence. **Failure
    avoided:** hub outage/compromise can conceal failure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U3-L4-INC-01 --- Incident/diagnosis

-   **Domain:** Unit 3\

-   **Level:** L4\

-   **Objective:** Sequence an incident response involving hub/spoke,
    selectors, fan-out, rings, dependency ordering, least privilege,
    rollback and hub failure.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario only;
    no real-system mutation. **Question**

\[SYNTHETIC\] A change related to cluster registration labels is
followed by degraded behavior in stage2e-west-lab; stage2e-east-lab
telemetry is stale. Respond in this order: first safe action → localize
→ mitigate → verify per cluster → communicate → prevent.

**Model answer and reasoning**

First halt further ring promotion/fan-out and preserve evidence.
Localize by verifying explicit contexts, cluster identity, last-seen
timestamps, local health and change revision. Mitigate only the
implicated ring/dependency using an approved rollback or isolation path
after checking data/write authority where relevant. Verify East and West
independently: service health, configuration/policy revision,
data/traffic state and alert delivery. Communicate scope, known facts,
uncertainty, owner and next update per region. Prevent recurrence with a
regression test, stronger freshness/health gate, rollback rehearsal and
named follow-up.

**Common wrong answer(s)**

Wrong: change both clusters at once, assume stale telemetry means
recovery, declare a root cause without evidence, or fail to communicate
uncertainty.

**Scoring rubric**

5 points: safe halt/evidence preservation (1); correct localization (1);
bounded mitigation (1); independent verification and communication (1);
durable prevention (1).

### U3-L3-DES-01 --- Design question

-   **Domain:** Unit 3\
-   **Level:** L3\
-   **Objective:** Design an operating pattern for hub/spoke, selectors,
    fan-out, rings, dependency ordering, least privilege, rollback and
    hub failure.\
-   **Estimated time:** 15 minutes

**Question**

Design a zero-budget two-kind-cluster lab pattern that can later inform
a production design for hub/spoke, selectors, fan-out, rings, dependency
ordering, least privilege, rollback and hub failure. State requirements,
architecture, ownership, failure modes, safety gates, evidence, rollback
and limits of the lab.

**Model answer and reasoning**

A defensible design starts with business/security/SLO constraints and
failure domains, chooses the simplest architecture that meets them,
identifies the owner and exact target scope, defines per-cluster health
and UNKNOWN states, protects credentials, and gives a bounded
rollout/rollback plan. Explain cost, latency, consistency and
operational trade-offs. Explicitly state that two local kind clusters
share a host and do not prove geographic resilience.

**Common wrong answer(s)**

Wrong: select tools before requirements, omit ownership/rollback, rely
on a green aggregate, or claim a local lab proves production regions.

**Scoring rubric**

Score 0--4 each: correctness; trade-off reasoning; safety/blast-radius
control; evidence/verification; operational feasibility (20 points
total).

### U3-L2-CALC-01 --- Calculation

-   **Domain:** Unit 3\
-   **Level:** L2\
-   **Objective:** Calculate a fleet outcome from synthetic counts.\
-   **Estimated time:** 6 minutes

**Question**

\[SYNTHETIC\] East: 8,000 requests/min, 99.9% good. West: 2,000
requests/min, 90% good. Compute global success.

**Model answer and reasoning**

East good=8,000×0.999=7,992; West=2,000×0.90=1,800;
total=9,792/10,000=97.92%. Keep regional guardrails; a global ratio can
hide local harm.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U3-L3-EVID-02 --- Evidence quality

-   **Domain:** Unit 3\
-   **Level:** L3\
-   **Objective:** Distinguish workflow evidence from production
    assurance.\
-   **Estimated time:** 7 minutes

**Question**

An engineer says two local kind clusters passing a lab proves two-region
resilience. Is the claim justified?

**Model answer and reasoning**

No. The lab tests workflow mechanics only. Real proof needs independent
failure domains, real WAN/routing, data authority/recovery, capacity,
production telemetry and rehearsed operations.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U3-L3-COMP-03 --- Comparison

-   **Domain:** Unit 3\
-   **Level:** L3\
-   **Objective:** Compare simple lab and production architecture.\
-   **Estimated time:** 8 minutes

**Question**

Compare a low-cost local approach with a production fleet approach for
image trust/admission verification. Give one benefit, one cost and one
failure mode each.

**Model answer and reasoning**

Local is cheap and inspectable but shares host/failure domains and has
limited scale. Production can improve isolation/automation but adds
cost, control-plane dependencies and more failure modes. Choose from
requirements.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U3-L2-CTX-04 --- Context safety

-   **Domain:** Unit 3\
-   **Level:** L2\
-   **Objective:** Verify target before a cluster-scoped action.\
-   **Estimated time:** 9 minutes

**Question**

\[SYNTHETIC\] Context list: `* kind-stage2e-east-lab`;
`kind-stage2e-west-lab`. A change is intended for West. What must be
checked?

**Model answer and reasoning**

Use an explicit reviewed `--context kind-stage2e-west-lab`, verify it
maps to the intended disposable cluster, inspect namespace/resources and
use dry-run where useful. Verify results per cluster. Do not rely on the
current `*` context.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U3-L4-GATE-05 --- Evidence under uncertainty

-   **Domain:** Unit 3\
-   **Level:** L4\
-   **Objective:** Name evidence that should block promotion.\
-   **Estimated time:** 10 minutes

**Question**

For dependency ordering, list three independent signals and one blocking
condition.

**Model answer and reasoning**

Check source identity/freshness, local health/alert evidence, and the
unit-specific control (capacity/data/policy/routing/desired state).
Block on critical FAIL, UNKNOWN, stale evidence or ambiguous target.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

## Unit 4 --- Cross-Cluster Service Discovery and Traffic Routing

**Scope:** endpoint patterns, DNS, EndpointSlices, NetworkPolicy,
TLS/mTLS, retries, locality and isolation.

### U4-L1-SA-01 --- Conceptual short answer

-   **Domain:** Unit 4\
-   **Level:** L1\
-   **Objective:** Explain exposed endpoint versus interconnect and its
    operational consequence.\
-   **Estimated time:** 5 minutes

**Question**

Explain **exposed endpoint versus interconnect**. State why it matters,
one failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Exposed endpoint versus interconnect must be evaluated against the
stated endpoint patterns, DNS, EndpointSlices, NetworkPolicy, TLS/mTLS,
retries, locality and isolation. A strong answer identifies the
requirement, names the relevant cluster/failure boundary, distinguishes
desired state from observed evidence, and proposes a verification method
plus a corrective action. Record owner, timestamp and scope where
relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U4-L1-SA-02 --- Conceptual short answer

-   **Domain:** Unit 4\
-   **Level:** L1\
-   **Objective:** Explain local Service versus cross-cluster discovery
    and its operational consequence.\
-   **Estimated time:** 6 minutes

**Question**

Explain **local Service versus cross-cluster discovery**. State why it
matters, one failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Local service versus cross-cluster discovery must be evaluated against
the stated endpoint patterns, DNS, EndpointSlices, NetworkPolicy,
TLS/mTLS, retries, locality and isolation. A strong answer identifies
the requirement, names the relevant cluster/failure boundary,
distinguishes desired state from observed evidence, and proposes a
verification method plus a corrective action. Record owner, timestamp
and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U4-L2-SA-03 --- Conceptual short answer

-   **Domain:** Unit 4\
-   **Level:** L2\
-   **Objective:** Explain EndpointSlice evidence limits and its
    operational consequence.\
-   **Estimated time:** 7 minutes

**Question**

Explain **EndpointSlice evidence limits**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Endpointslice evidence limits must be evaluated against the stated
endpoint patterns, DNS, EndpointSlices, NetworkPolicy, TLS/mTLS,
retries, locality and isolation. A strong answer identifies the
requirement, names the relevant cluster/failure boundary, distinguishes
desired state from observed evidence, and proposes a verification method
plus a corrective action. Record owner, timestamp and scope where
relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U4-L1-MCQ-01 --- Multiple choice (exactly four options)

-   **Domain:** Unit 4\
-   **Level:** L1\
-   **Objective:** Choose a safe decision about DNS forwarding
    diagnosis.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **DNS forwarding diagnosis**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for DNS forwarding diagnosis.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U4-L2-MCQ-02 --- Multiple choice (exactly four options)

-   **Domain:** Unit 4\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about mTLS trust-root
    rotation.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **mTLS trust-root rotation**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for mTLS trust-root rotation.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U4-L2-MCQ-03 --- Multiple choice (exactly four options)

-   **Domain:** Unit 4\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about negative NetworkPolicy
    tests.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **negative NetworkPolicy tests**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for negative NetworkPolicy tests.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U4-L2-ART-01 --- Artifact interpretation

-   **Domain:** Unit 4\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    retry amplification is safe.\
-   **Estimated time:** 6 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
cluster=stage2e-east-lab status=PASS timestamp=10:00Z
cluster=stage2e-west-lab status=UNKNOWN timestamp=09:00Z
expected_cluster_count=2 fresh_reports=1
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

East has fresh PASS evidence; West is UNKNOWN with stale evidence. The
fleet is not green. Identify West's local state and obtain fresh
evidence before a gated action. Preserve timestamps and source identity.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U4-L2-ART-02 --- Artifact interpretation

-   **Domain:** Unit 4\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    locality and failure coupling is safe.\
-   **Estimated time:** 7 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
revision=r42 target_clusters=2 ring=canary
stage2e-east-lab: health=PASS evidence=fresh
stage2e-west-lab: health=FAIL evidence=fresh
next_action=promote
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

Promotion is unsafe: West has a fresh FAIL. Halt the ring, preserve
revision and health evidence, mitigate the failing cluster, and require
fresh passing evidence before promotion. Sync/selection status does not
override health. Verify per cluster and retain the timestamp, revision,
target identity and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U4-L3-ART-03 --- Artifact interpretation

-   **Domain:** Unit 4\
-   **Level:** L3\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    trust bundle consistency is safe.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
source=stage2e-east-lab target=stage2e-west-lab
last_seen=unknown; owner=platform
change_time=10:03Z; alert_time=10:04Z
summary=green
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

The summary conflicts with missing source/last-seen evidence. Mark the
affected path UNKNOWN, check source and target independently, correlate
the change and alert, and do not treat missing telemetry as healthy.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U4-L2-CFG-01 --- Configuration/artifact review

-   **Domain:** Unit 4\
-   **Level:** L2\
-   **Objective:** Review a scope/ownership artifact for at least three
    defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
target=all-clusters
owner=unspecified
health_gate=disabled
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Target is broad/ambiguous. **Correction:** Resolve and
    display the exact intended cluster set. **Failure avoided:**
    unintended clusters can be changed.
2.  **Defect:** Owner is missing. **Correction:** Assign accountable
    owner and approver. **Failure avoided:** incident response and
    decisions stall.
3.  **Defect:** Health gate is disabled. **Correction:** Add measurable
    per-cluster gates and halt conditions. **Failure avoided:** bad
    changes propagate unchecked.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U4-L3-CFG-02 --- Configuration/artifact review

-   **Domain:** Unit 4\
-   **Level:** L3\
-   **Objective:** Review a rollout/consistency artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
promote_on=sync-success-only
unknown_evidence=pass
rollback_revision=none
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Sync success is the only gate. **Correction:** Check
    runtime health and relevant data/policy/route signals. **Failure
    avoided:** desired state can apply while service fails.
2.  **Defect:** Unknown evidence passes. **Correction:** Represent
    UNKNOWN/UNREACHABLE and block critical promotion. **Failure
    avoided:** missing data creates false green.
3.  **Defect:** No rollback revision. **Correction:** Record a
    known-good revision and rollback criteria. **Failure avoided:**
    recovery is improvised under pressure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U4-L3-CFG-03 --- Configuration/artifact review

-   **Domain:** Unit 4\
-   **Level:** L3\
-   **Objective:** Review a security/evidence artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
credential_scope=fleet-admin
report_timestamp=omitted
verification=central-only
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Credential is overbroad. **Correction:** Use least
    privilege and narrower cluster scope. **Failure avoided:** hub
    compromise can affect the fleet.
2.  **Defect:** Timestamp/freshness omitted. **Correction:** Record
    timestamp, source and freshness threshold. **Failure avoided:**
    stale report can be mistaken for current.
3.  **Defect:** Only central verification. **Correction:** Verify
    affected clusters independently and retain local evidence. **Failure
    avoided:** hub outage/compromise can conceal failure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U4-L4-INC-01 --- Incident/diagnosis

-   **Domain:** Unit 4\

-   **Level:** L4\

-   **Objective:** Sequence an incident response involving endpoint
    patterns, DNS, EndpointSlices, NetworkPolicy, TLS/mTLS, retries,
    locality and isolation.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario only;
    no real-system mutation. **Question**

\[SYNTHETIC\] A change related to compromised-cluster isolation is
followed by degraded behavior in stage2e-west-lab; stage2e-east-lab
telemetry is stale. Respond in this order: first safe action → localize
→ mitigate → verify per cluster → communicate → prevent.

**Model answer and reasoning**

First halt further ring promotion/fan-out and preserve evidence.
Localize by verifying explicit contexts, cluster identity, last-seen
timestamps, local health and change revision. Mitigate only the
implicated ring/dependency using an approved rollback or isolation path
after checking data/write authority where relevant. Verify East and West
independently: service health, configuration/policy revision,
data/traffic state and alert delivery. Communicate scope, known facts,
uncertainty, owner and next update per region. Prevent recurrence with a
regression test, stronger freshness/health gate, rollback rehearsal and
named follow-up.

**Common wrong answer(s)**

Wrong: change both clusters at once, assume stale telemetry means
recovery, declare a root cause without evidence, or fail to communicate
uncertainty.

**Scoring rubric**

5 points: safe halt/evidence preservation (1); correct localization (1);
bounded mitigation (1); independent verification and communication (1);
durable prevention (1).

### U4-L3-DES-01 --- Design question

-   **Domain:** Unit 4\
-   **Level:** L3\
-   **Objective:** Design an operating pattern for endpoint patterns,
    DNS, EndpointSlices, NetworkPolicy, TLS/mTLS, retries, locality and
    isolation.\
-   **Estimated time:** 15 minutes

**Question**

Design a zero-budget two-kind-cluster lab pattern that can later inform
a production design for endpoint patterns, DNS, EndpointSlices,
NetworkPolicy, TLS/mTLS, retries, locality and isolation. State
requirements, architecture, ownership, failure modes, safety gates,
evidence, rollback and limits of the lab.

**Model answer and reasoning**

A defensible design starts with business/security/SLO constraints and
failure domains, chooses the simplest architecture that meets them,
identifies the owner and exact target scope, defines per-cluster health
and UNKNOWN states, protects credentials, and gives a bounded
rollout/rollback plan. Explain cost, latency, consistency and
operational trade-offs. Explicitly state that two local kind clusters
share a host and do not prove geographic resilience.

**Common wrong answer(s)**

Wrong: select tools before requirements, omit ownership/rollback, rely
on a green aggregate, or claim a local lab proves production regions.

**Scoring rubric**

Score 0--4 each: correctness; trade-off reasoning; safety/blast-radius
control; evidence/verification; operational feasibility (20 points
total).

### U4-L2-CALC-01 --- Calculation

-   **Domain:** Unit 4\
-   **Level:** L2\
-   **Objective:** Calculate a fleet outcome from synthetic counts.\
-   **Estimated time:** 6 minutes

**Question**

\[SYNTHETIC\] East: 8,000 requests/min, 99.9% good. West: 2,000
requests/min, 90% good. Compute global success.

**Model answer and reasoning**

East good=8,000×0.999=7,992; West=2,000×0.90=1,800;
total=9,792/10,000=97.92%. Keep regional guardrails; a global ratio can
hide local harm.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U4-L3-EVID-02 --- Evidence quality

-   **Domain:** Unit 4\
-   **Level:** L3\
-   **Objective:** Distinguish workflow evidence from production
    assurance.\
-   **Estimated time:** 7 minutes

**Question**

An engineer says two local kind clusters passing a lab proves two-region
resilience. Is the claim justified?

**Model answer and reasoning**

No. The lab tests workflow mechanics only. Real proof needs independent
failure domains, real WAN/routing, data authority/recovery, capacity,
production telemetry and rehearsed operations.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U4-L3-COMP-03 --- Comparison

-   **Domain:** Unit 4\
-   **Level:** L3\
-   **Objective:** Compare simple lab and production architecture.\
-   **Estimated time:** 8 minutes

**Question**

Compare a low-cost local approach with a production fleet approach for
negative-path test quality. Give one benefit, one cost and one failure
mode each.

**Model answer and reasoning**

Local is cheap and inspectable but shares host/failure domains and has
limited scale. Production can improve isolation/automation but adds
cost, control-plane dependencies and more failure modes. Choose from
requirements.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U4-L2-CTX-04 --- Context safety

-   **Domain:** Unit 4\
-   **Level:** L2\
-   **Objective:** Verify target before a cluster-scoped action.\
-   **Estimated time:** 9 minutes

**Question**

\[SYNTHETIC\] Context list: `* kind-stage2e-east-lab`;
`kind-stage2e-west-lab`. A change is intended for West. What must be
checked?

**Model answer and reasoning**

Use an explicit reviewed `--context kind-stage2e-west-lab`, verify it
maps to the intended disposable cluster, inspect namespace/resources and
use dry-run where useful. Verify results per cluster. Do not rely on the
current `*` context.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U4-L4-GATE-05 --- Evidence under uncertainty

-   **Domain:** Unit 4\
-   **Level:** L4\
-   **Objective:** Name evidence that should block promotion.\
-   **Estimated time:** 10 minutes

**Question**

For certificate versus DNS diagnosis, list three independent signals and
one blocking condition.

**Model answer and reasoning**

Check source identity/freshness, local health/alert evidence, and the
unit-specific control (capacity/data/policy/routing/desired state).
Block on critical FAIL, UNKNOWN, stale evidence or ambiguous target.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

## Unit 5 --- Global Load Balancing and DNS Failover

**Scope:** DNS steering, TTL/client tail, health checks, false
positives, proxy comparison, failover timing and write safety.

### U5-L1-SA-01 --- Conceptual short answer

-   **Domain:** Unit 5\
-   **Level:** L1\
-   **Objective:** Explain DNS steering and client behavior and its
    operational consequence.\
-   **Estimated time:** 5 minutes

**Question**

Explain **DNS steering and client behavior**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Dns steering and client behavior must be evaluated against the stated
DNS steering, TTL/client tail, health checks, false positives, proxy
comparison, failover timing and write safety. A strong answer identifies
the requirement, names the relevant cluster/failure boundary,
distinguishes desired state from observed evidence, and proposes a
verification method plus a corrective action. Record owner, timestamp
and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U5-L1-SA-02 --- Conceptual short answer

-   **Domain:** Unit 5\
-   **Level:** L1\
-   **Objective:** Explain TTL versus observed failover bound and its
    operational consequence.\
-   **Estimated time:** 6 minutes

**Question**

Explain **TTL versus observed failover bound**. State why it matters,
one failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Ttl versus observed failover bound must be evaluated against the stated
DNS steering, TTL/client tail, health checks, false positives, proxy
comparison, failover timing and write safety. A strong answer identifies
the requirement, names the relevant cluster/failure boundary,
distinguishes desired state from observed evidence, and proposes a
verification method plus a corrective action. Record owner, timestamp
and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U5-L2-SA-03 --- Conceptual short answer

-   **Domain:** Unit 5\
-   **Level:** L2\
-   **Objective:** Explain health-check depth and its operational
    consequence.\
-   **Estimated time:** 7 minutes

**Question**

Explain **health-check depth**. State why it matters, one failure mode,
and what evidence would verify the claim.

**Model answer and reasoning**

Health-check depth must be evaluated against the stated DNS steering,
TTL/client tail, health checks, false positives, proxy comparison,
failover timing and write safety. A strong answer identifies the
requirement, names the relevant cluster/failure boundary, distinguishes
desired state from observed evidence, and proposes a verification method
plus a corrective action. Record owner, timestamp and scope where
relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U5-L1-MCQ-01 --- Multiple choice (exactly four options)

-   **Domain:** Unit 5\
-   **Level:** L1\
-   **Objective:** Choose a safe decision about false positives and
    hysteresis.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **false positives and
hysteresis** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for false positives and hysteresis.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U5-L2-MCQ-02 --- Multiple choice (exactly four options)

-   **Domain:** Unit 5\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about DNS versus proxy entry
    point.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **DNS versus proxy entry point**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for DNS versus proxy entry point.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U5-L2-MCQ-03 --- Multiple choice (exactly four options)

-   **Domain:** Unit 5\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about failover-time
    components.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **failover-time components**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for failover-time components.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U5-L2-ART-01 --- Artifact interpretation

-   **Domain:** Unit 5\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    write routing and fencing is safe.\
-   **Estimated time:** 6 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
cluster=stage2e-east-lab status=PASS timestamp=10:00Z
cluster=stage2e-west-lab status=UNKNOWN timestamp=09:00Z
expected_cluster_count=2 fresh_reports=1
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

East has fresh PASS evidence; West is UNKNOWN with stale evidence. The
fleet is not green. Identify West's local state and obtain fresh
evidence before a gated action. Preserve timestamps and source identity.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U5-L2-ART-02 --- Artifact interpretation

-   **Domain:** Unit 5\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    fail-static behavior is safe.\
-   **Estimated time:** 7 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
revision=r42 target_clusters=2 ring=canary
stage2e-east-lab: health=PASS evidence=fresh
stage2e-west-lab: health=FAIL evidence=fresh
next_action=promote
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

Promotion is unsafe: West has a fresh FAIL. Halt the ring, preserve
revision and health evidence, mitigate the failing cluster, and require
fresh passing evidence before promotion. Sync/selection status does not
override health. Verify per cluster and retain the timestamp, revision,
target identity and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U5-L3-ART-03 --- Artifact interpretation

-   **Domain:** Unit 5\
-   **Level:** L3\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    gradual traffic shift is safe.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
source=stage2e-east-lab target=stage2e-west-lab
last_seen=unknown; owner=platform
change_time=10:03Z; alert_time=10:04Z
summary=green
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

The summary conflicts with missing source/last-seen evidence. Mark the
affected path UNKNOWN, check source and target independently, correlate
the change and alert, and do not treat missing telemetry as healthy.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U5-L2-CFG-01 --- Configuration/artifact review

-   **Domain:** Unit 5\
-   **Level:** L2\
-   **Objective:** Review a scope/ownership artifact for at least three
    defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
target=all-clusters
owner=unspecified
health_gate=disabled
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Target is broad/ambiguous. **Correction:** Resolve and
    display the exact intended cluster set. **Failure avoided:**
    unintended clusters can be changed.
2.  **Defect:** Owner is missing. **Correction:** Assign accountable
    owner and approver. **Failure avoided:** incident response and
    decisions stall.
3.  **Defect:** Health gate is disabled. **Correction:** Add measurable
    per-cluster gates and halt conditions. **Failure avoided:** bad
    changes propagate unchecked.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U5-L3-CFG-02 --- Configuration/artifact review

-   **Domain:** Unit 5\
-   **Level:** L3\
-   **Objective:** Review a rollout/consistency artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
promote_on=sync-success-only
unknown_evidence=pass
rollback_revision=none
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Sync success is the only gate. **Correction:** Check
    runtime health and relevant data/policy/route signals. **Failure
    avoided:** desired state can apply while service fails.
2.  **Defect:** Unknown evidence passes. **Correction:** Represent
    UNKNOWN/UNREACHABLE and block critical promotion. **Failure
    avoided:** missing data creates false green.
3.  **Defect:** No rollback revision. **Correction:** Record a
    known-good revision and rollback criteria. **Failure avoided:**
    recovery is improvised under pressure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U5-L3-CFG-03 --- Configuration/artifact review

-   **Domain:** Unit 5\
-   **Level:** L3\
-   **Objective:** Review a security/evidence artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
credential_scope=fleet-admin
report_timestamp=omitted
verification=central-only
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Credential is overbroad. **Correction:** Use least
    privilege and narrower cluster scope. **Failure avoided:** hub
    compromise can affect the fleet.
2.  **Defect:** Timestamp/freshness omitted. **Correction:** Record
    timestamp, source and freshness threshold. **Failure avoided:**
    stale report can be mistaken for current.
3.  **Defect:** Only central verification. **Correction:** Verify
    affected clusters independently and retain local evidence. **Failure
    avoided:** hub outage/compromise can conceal failure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U5-L4-INC-01 --- Incident/diagnosis

-   **Domain:** Unit 5\

-   **Level:** L4\

-   **Objective:** Sequence an incident response involving DNS steering,
    TTL/client tail, health checks, false positives, proxy comparison,
    failover timing and write safety.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario only;
    no real-system mutation. **Question**

\[SYNTHETIC\] A change related to failback readiness is followed by
degraded behavior in stage2e-west-lab; stage2e-east-lab telemetry is
stale. Respond in this order: first safe action → localize → mitigate →
verify per cluster → communicate → prevent.

**Model answer and reasoning**

First halt further ring promotion/fan-out and preserve evidence.
Localize by verifying explicit contexts, cluster identity, last-seen
timestamps, local health and change revision. Mitigate only the
implicated ring/dependency using an approved rollback or isolation path
after checking data/write authority where relevant. Verify East and West
independently: service health, configuration/policy revision,
data/traffic state and alert delivery. Communicate scope, known facts,
uncertainty, owner and next update per region. Prevent recurrence with a
regression test, stronger freshness/health gate, rollback rehearsal and
named follow-up.

**Common wrong answer(s)**

Wrong: change both clusters at once, assume stale telemetry means
recovery, declare a root cause without evidence, or fail to communicate
uncertainty.

**Scoring rubric**

5 points: safe halt/evidence preservation (1); correct localization (1);
bounded mitigation (1); independent verification and communication (1);
durable prevention (1).

### U5-L3-DES-01 --- Design question

-   **Domain:** Unit 5\
-   **Level:** L3\
-   **Objective:** Design an operating pattern for DNS steering,
    TTL/client tail, health checks, false positives, proxy comparison,
    failover timing and write safety.\
-   **Estimated time:** 15 minutes

**Question**

Design a zero-budget two-kind-cluster lab pattern that can later inform
a production design for DNS steering, TTL/client tail, health checks,
false positives, proxy comparison, failover timing and write safety.
State requirements, architecture, ownership, failure modes, safety
gates, evidence, rollback and limits of the lab.

**Model answer and reasoning**

A defensible design starts with business/security/SLO constraints and
failure domains, chooses the simplest architecture that meets them,
identifies the owner and exact target scope, defines per-cluster health
and UNKNOWN states, protects credentials, and gives a bounded
rollout/rollback plan. Explain cost, latency, consistency and
operational trade-offs. Explicitly state that two local kind clusters
share a host and do not prove geographic resilience.

**Common wrong answer(s)**

Wrong: select tools before requirements, omit ownership/rollback, rely
on a green aggregate, or claim a local lab proves production regions.

**Scoring rubric**

Score 0--4 each: correctness; trade-off reasoning; safety/blast-radius
control; evidence/verification; operational feasibility (20 points
total).

### U5-L2-CALC-01 --- Calculation

-   **Domain:** Unit 5\
-   **Level:** L2\
-   **Objective:** Calculate a fleet outcome from synthetic counts.\
-   **Estimated time:** 6 minutes

**Question**

\[SYNTHETIC\] East: 8,000 requests/min, 99.9% good. West: 2,000
requests/min, 90% good. Compute global success.

**Model answer and reasoning**

East good=8,000×0.999=7,992; West=2,000×0.90=1,800;
total=9,792/10,000=97.92%. Keep regional guardrails; a global ratio can
hide local harm.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U5-L3-EVID-02 --- Evidence quality

-   **Domain:** Unit 5\
-   **Level:** L3\
-   **Objective:** Distinguish workflow evidence from production
    assurance.\
-   **Estimated time:** 7 minutes

**Question**

An engineer says two local kind clusters passing a lab proves two-region
resilience. Is the claim justified?

**Model answer and reasoning**

No. The lab tests workflow mechanics only. Real proof needs independent
failure domains, real WAN/routing, data authority/recovery, capacity,
production telemetry and rehearsed operations.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U5-L3-COMP-03 --- Comparison

-   **Domain:** Unit 5\
-   **Level:** L3\
-   **Objective:** Compare simple lab and production architecture.\
-   **Estimated time:** 8 minutes

**Question**

Compare a low-cost local approach with a production fleet approach for
health signal diversity. Give one benefit, one cost and one failure mode
each.

**Model answer and reasoning**

Local is cheap and inspectable but shares host/failure domains and has
limited scale. Production can improve isolation/automation but adds
cost, control-plane dependencies and more failure modes. Choose from
requirements.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U5-L2-CTX-04 --- Context safety

-   **Domain:** Unit 5\
-   **Level:** L2\
-   **Objective:** Verify target before a cluster-scoped action.\
-   **Estimated time:** 9 minutes

**Question**

\[SYNTHETIC\] Context list: `* kind-stage2e-east-lab`;
`kind-stage2e-west-lab`. A change is intended for West. What must be
checked?

**Model answer and reasoning**

Use an explicit reviewed `--context kind-stage2e-west-lab`, verify it
maps to the intended disposable cluster, inspect namespace/resources and
use dry-run where useful. Verify results per cluster. Do not rely on the
current `*` context.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U5-L4-GATE-05 --- Evidence under uncertainty

-   **Domain:** Unit 5\
-   **Level:** L4\
-   **Objective:** Name evidence that should block promotion.\
-   **Estimated time:** 10 minutes

**Question**

For TLS readiness, list three independent signals and one blocking
condition.

**Model answer and reasoning**

Check source identity/freshness, local health/alert evidence, and the
unit-specific control (capacity/data/policy/routing/desired state).
Block on critical FAIL, UNKNOWN, stale evidence or ambiguous target.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

## Unit 6 --- Active-Active vs Active-Passive Regional Designs

**Scope:** per-tier patterns, N+1 capacity, readiness, evacuation,
fencing, ownership, dependencies and failback.

### U6-L1-SA-01 --- Conceptual short answer

-   **Domain:** Unit 6\
-   **Level:** L1\
-   **Objective:** Explain per-tier regional pattern choice and its
    operational consequence.\
-   **Estimated time:** 5 minutes

**Question**

Explain **per-tier regional pattern choice**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Per-tier regional pattern choice must be evaluated against the stated
per-tier patterns, N+1 capacity, readiness, evacuation, fencing,
ownership, dependencies and failback. A strong answer identifies the
requirement, names the relevant cluster/failure boundary, distinguishes
desired state from observed evidence, and proposes a verification method
plus a corrective action. Record owner, timestamp and scope where
relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U6-L1-SA-02 --- Conceptual short answer

-   **Domain:** Unit 6\
-   **Level:** L1\
-   **Objective:** Explain active-active readiness and its operational
    consequence.\
-   **Estimated time:** 6 minutes

**Question**

Explain **active-active readiness**. State why it matters, one failure
mode, and what evidence would verify the claim.

**Model answer and reasoning**

Active-active readiness must be evaluated against the stated per-tier
patterns, N+1 capacity, readiness, evacuation, fencing, ownership,
dependencies and failback. A strong answer identifies the requirement,
names the relevant cluster/failure boundary, distinguishes desired state
from observed evidence, and proposes a verification method plus a
corrective action. Record owner, timestamp and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U6-L2-SA-03 --- Conceptual short answer

-   **Domain:** Unit 6\
-   **Level:** L2\
-   **Objective:** Explain active-passive standby parity and its
    operational consequence.\
-   **Estimated time:** 7 minutes

**Question**

Explain **active-passive standby parity**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Active-passive standby parity must be evaluated against the stated
per-tier patterns, N+1 capacity, readiness, evacuation, fencing,
ownership, dependencies and failback. A strong answer identifies the
requirement, names the relevant cluster/failure boundary, distinguishes
desired state from observed evidence, and proposes a verification method
plus a corrective action. Record owner, timestamp and scope where
relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U6-L1-MCQ-01 --- Multiple choice (exactly four options)

-   **Domain:** Unit 6\
-   **Level:** L1\
-   **Objective:** Choose a safe decision about N+1 capacity.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **N+1 capacity** under the stated
fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for N+1 capacity.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U6-L2-MCQ-02 --- Multiple choice (exactly four options)

-   **Domain:** Unit 6\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about fencing versus health
    detection.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **fencing versus health
detection** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for fencing versus health detection.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U6-L2-MCQ-03 --- Multiple choice (exactly four options)

-   **Domain:** Unit 6\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about split-brain and write
    ownership.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **split-brain and write
ownership** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for split-brain and write ownership.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U6-L2-ART-01 --- Artifact interpretation

-   **Domain:** Unit 6\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    tenant home-region routing is safe.\
-   **Estimated time:** 6 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
cluster=stage2e-east-lab status=PASS timestamp=10:00Z
cluster=stage2e-west-lab status=UNKNOWN timestamp=09:00Z
expected_cluster_count=2 fresh_reports=1
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

East has fresh PASS evidence; West is UNKNOWN with stale evidence. The
fleet is not green. Identify West's local state and obtain fresh
evidence before a gated action. Preserve timestamps and source identity.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U6-L2-ART-02 --- Artifact interpretation

-   **Domain:** Unit 6\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    local dependency resolution is safe.\
-   **Estimated time:** 7 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
revision=r42 target_clusters=2 ring=canary
stage2e-east-lab: health=PASS evidence=fresh
stage2e-west-lab: health=FAIL evidence=fresh
next_action=promote
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

Promotion is unsafe: West has a fresh FAIL. Halt the ring, preserve
revision and health evidence, mitigate the failing cluster, and require
fresh passing evidence before promotion. Sync/selection status does not
override health. Verify per cluster and retain the timestamp, revision,
target identity and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U6-L3-ART-03 --- Artifact interpretation

-   **Domain:** Unit 6\
-   **Level:** L3\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    post-failure utilization is safe.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
source=stage2e-east-lab target=stage2e-west-lab
last_seen=unknown; owner=platform
change_time=10:03Z; alert_time=10:04Z
summary=green
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

The summary conflicts with missing source/last-seen evidence. Mark the
affected path UNKNOWN, check source and target independently, correlate
the change and alert, and do not treat missing telemetry as healthy.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U6-L2-CFG-01 --- Configuration/artifact review

-   **Domain:** Unit 6\
-   **Level:** L2\
-   **Objective:** Review a scope/ownership artifact for at least three
    defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
target=all-clusters
owner=unspecified
health_gate=disabled
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Target is broad/ambiguous. **Correction:** Resolve and
    display the exact intended cluster set. **Failure avoided:**
    unintended clusters can be changed.
2.  **Defect:** Owner is missing. **Correction:** Assign accountable
    owner and approver. **Failure avoided:** incident response and
    decisions stall.
3.  **Defect:** Health gate is disabled. **Correction:** Add measurable
    per-cluster gates and halt conditions. **Failure avoided:** bad
    changes propagate unchecked.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U6-L3-CFG-02 --- Configuration/artifact review

-   **Domain:** Unit 6\
-   **Level:** L3\
-   **Objective:** Review a rollout/consistency artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
promote_on=sync-success-only
unknown_evidence=pass
rollback_revision=none
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Sync success is the only gate. **Correction:** Check
    runtime health and relevant data/policy/route signals. **Failure
    avoided:** desired state can apply while service fails.
2.  **Defect:** Unknown evidence passes. **Correction:** Represent
    UNKNOWN/UNREACHABLE and block critical promotion. **Failure
    avoided:** missing data creates false green.
3.  **Defect:** No rollback revision. **Correction:** Record a
    known-good revision and rollback criteria. **Failure avoided:**
    recovery is improvised under pressure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U6-L3-CFG-03 --- Configuration/artifact review

-   **Domain:** Unit 6\
-   **Level:** L3\
-   **Objective:** Review a security/evidence artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
credential_scope=fleet-admin
report_timestamp=omitted
verification=central-only
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Credential is overbroad. **Correction:** Use least
    privilege and narrower cluster scope. **Failure avoided:** hub
    compromise can affect the fleet.
2.  **Defect:** Timestamp/freshness omitted. **Correction:** Record
    timestamp, source and freshness threshold. **Failure avoided:**
    stale report can be mistaken for current.
3.  **Defect:** Only central verification. **Correction:** Verify
    affected clusters independently and retain local evidence. **Failure
    avoided:** hub outage/compromise can conceal failure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U6-L4-INC-01 --- Incident/diagnosis

-   **Domain:** Unit 6\

-   **Level:** L4\

-   **Objective:** Sequence an incident response involving per-tier
    patterns, N+1 capacity, readiness, evacuation, fencing, ownership,
    dependencies and failback.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario only;
    no real-system mutation. **Question**

\[SYNTHETIC\] A change related to regional readiness evidence is
followed by degraded behavior in stage2e-west-lab; stage2e-east-lab
telemetry is stale. Respond in this order: first safe action → localize
→ mitigate → verify per cluster → communicate → prevent.

**Model answer and reasoning**

First halt further ring promotion/fan-out and preserve evidence.
Localize by verifying explicit contexts, cluster identity, last-seen
timestamps, local health and change revision. Mitigate only the
implicated ring/dependency using an approved rollback or isolation path
after checking data/write authority where relevant. Verify East and West
independently: service health, configuration/policy revision,
data/traffic state and alert delivery. Communicate scope, known facts,
uncertainty, owner and next update per region. Prevent recurrence with a
regression test, stronger freshness/health gate, rollback rehearsal and
named follow-up.

**Common wrong answer(s)**

Wrong: change both clusters at once, assume stale telemetry means
recovery, declare a root cause without evidence, or fail to communicate
uncertainty.

**Scoring rubric**

5 points: safe halt/evidence preservation (1); correct localization (1);
bounded mitigation (1); independent verification and communication (1);
durable prevention (1).

### U6-L3-DES-01 --- Design question

-   **Domain:** Unit 6\
-   **Level:** L3\
-   **Objective:** Design an operating pattern for per-tier patterns,
    N+1 capacity, readiness, evacuation, fencing, ownership,
    dependencies and failback.\
-   **Estimated time:** 15 minutes

**Question**

Design a zero-budget two-kind-cluster lab pattern that can later inform
a production design for per-tier patterns, N+1 capacity, readiness,
evacuation, fencing, ownership, dependencies and failback. State
requirements, architecture, ownership, failure modes, safety gates,
evidence, rollback and limits of the lab.

**Model answer and reasoning**

A defensible design starts with business/security/SLO constraints and
failure domains, chooses the simplest architecture that meets them,
identifies the owner and exact target scope, defines per-cluster health
and UNKNOWN states, protects credentials, and gives a bounded
rollout/rollback plan. Explain cost, latency, consistency and
operational trade-offs. Explicitly state that two local kind clusters
share a host and do not prove geographic resilience.

**Common wrong answer(s)**

Wrong: select tools before requirements, omit ownership/rollback, rely
on a green aggregate, or claim a local lab proves production regions.

**Scoring rubric**

Score 0--4 each: correctness; trade-off reasoning; safety/blast-radius
control; evidence/verification; operational feasibility (20 points
total).

### U6-L2-CALC-01 --- Calculation

-   **Domain:** Unit 6\
-   **Level:** L2\
-   **Objective:** Calculate a fleet outcome from synthetic counts.\
-   **Estimated time:** 6 minutes

**Question**

\[SYNTHETIC\] East: 8,000 requests/min, 99.9% good. West: 2,000
requests/min, 90% good. Compute global success.

**Model answer and reasoning**

East good=8,000×0.999=7,992; West=2,000×0.90=1,800;
total=9,792/10,000=97.92%. Keep regional guardrails; a global ratio can
hide local harm.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U6-L3-EVID-02 --- Evidence quality

-   **Domain:** Unit 6\
-   **Level:** L3\
-   **Objective:** Distinguish workflow evidence from production
    assurance.\
-   **Estimated time:** 7 minutes

**Question**

An engineer says two local kind clusters passing a lab proves two-region
resilience. Is the claim justified?

**Model answer and reasoning**

No. The lab tests workflow mechanics only. Real proof needs independent
failure domains, real WAN/routing, data authority/recovery, capacity,
production telemetry and rehearsed operations.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U6-L3-COMP-03 --- Comparison

-   **Domain:** Unit 6\
-   **Level:** L3\
-   **Objective:** Compare simple lab and production architecture.\
-   **Estimated time:** 8 minutes

**Question**

Compare a low-cost local approach with a production fleet approach for
CPU versus downstream capacity. Give one benefit, one cost and one
failure mode each.

**Model answer and reasoning**

Local is cheap and inspectable but shares host/failure domains and has
limited scale. Production can improve isolation/automation but adds
cost, control-plane dependencies and more failure modes. Choose from
requirements.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U6-L2-CTX-04 --- Context safety

-   **Domain:** Unit 6\
-   **Level:** L2\
-   **Objective:** Verify target before a cluster-scoped action.\
-   **Estimated time:** 9 minutes

**Question**

\[SYNTHETIC\] Context list: `* kind-stage2e-east-lab`;
`kind-stage2e-west-lab`. A change is intended for West. What must be
checked?

**Model answer and reasoning**

Use an explicit reviewed `--context kind-stage2e-west-lab`, verify it
maps to the intended disposable cluster, inspect namespace/resources and
use dry-run where useful. Verify results per cluster. Do not rely on the
current `*` context.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U6-L4-GATE-05 --- Evidence under uncertainty

-   **Domain:** Unit 6\
-   **Level:** L4\
-   **Objective:** Name evidence that should block promotion.\
-   **Estimated time:** 10 minutes

**Question**

For missing capacity telemetry, list three independent signals and one
blocking condition.

**Model answer and reasoning**

Check source identity/freshness, local health/alert evidence, and the
unit-specific control (capacity/data/policy/routing/desired state).
Block on critical FAIL, UNKNOWN, stale evidence or ambiguous target.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

## Unit 7 --- Data Replication and Consistency Across Regions

**Scope:** consistency anomalies, sync/async, lag/RPO, WAL retention,
object replication, artifact hashes and schema evolution.

### U7-L1-SA-01 --- Conceptual short answer

-   **Domain:** Unit 7\
-   **Level:** L1\
-   **Objective:** Explain stale read and its operational consequence.\
-   **Estimated time:** 5 minutes

**Question**

Explain **stale read**. State why it matters, one failure mode, and what
evidence would verify the claim.

**Model answer and reasoning**

Stale read must be evaluated against the stated consistency anomalies,
sync/async, lag/RPO, WAL retention, object replication, artifact hashes
and schema evolution. A strong answer identifies the requirement, names
the relevant cluster/failure boundary, distinguishes desired state from
observed evidence, and proposes a verification method plus a corrective
action. Record owner, timestamp and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U7-L1-SA-02 --- Conceptual short answer

-   **Domain:** Unit 7\
-   **Level:** L1\
-   **Objective:** Explain lost acknowledged write and its operational
    consequence.\
-   **Estimated time:** 6 minutes

**Question**

Explain **lost acknowledged write**. State why it matters, one failure
mode, and what evidence would verify the claim.

**Model answer and reasoning**

Lost acknowledged write must be evaluated against the stated consistency
anomalies, sync/async, lag/RPO, WAL retention, object replication,
artifact hashes and schema evolution. A strong answer identifies the
requirement, names the relevant cluster/failure boundary, distinguishes
desired state from observed evidence, and proposes a verification method
plus a corrective action. Record owner, timestamp and scope where
relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U7-L2-SA-03 --- Conceptual short answer

-   **Domain:** Unit 7\
-   **Level:** L2\
-   **Objective:** Explain lost update and its operational consequence.\
-   **Estimated time:** 7 minutes

**Question**

Explain **lost update**. State why it matters, one failure mode, and
what evidence would verify the claim.

**Model answer and reasoning**

Lost update must be evaluated against the stated consistency anomalies,
sync/async, lag/RPO, WAL retention, object replication, artifact hashes
and schema evolution. A strong answer identifies the requirement, names
the relevant cluster/failure boundary, distinguishes desired state from
observed evidence, and proposes a verification method plus a corrective
action. Record owner, timestamp and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U7-L1-MCQ-01 --- Multiple choice (exactly four options)

-   **Domain:** Unit 7\
-   **Level:** L1\
-   **Objective:** Choose a safe decision about monotonic-read
    violation.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **monotonic-read violation**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for monotonic-read violation.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U7-L2-MCQ-02 --- Multiple choice (exactly four options)

-   **Domain:** Unit 7\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about synchronous versus
    asynchronous replication.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **synchronous versus asynchronous
replication** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for synchronous versus asynchronous replication.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U7-L2-MCQ-03 --- Multiple choice (exactly four options)

-   **Domain:** Unit 7\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about lag percentile versus
    maximum.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **lag percentile versus maximum**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for lag percentile versus maximum.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U7-L2-ART-01 --- Artifact interpretation

-   **Domain:** Unit 7\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    RPO and acknowledged-write evidence is safe.\
-   **Estimated time:** 6 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
cluster=stage2e-east-lab status=PASS timestamp=10:00Z
cluster=stage2e-west-lab status=UNKNOWN timestamp=09:00Z
expected_cluster_count=2 fresh_reports=1
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

East has fresh PASS evidence; West is UNKNOWN with stale evidence. The
fleet is not green. Identify West's local state and obtain fresh
evidence before a gated action. Preserve timestamps and source identity.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U7-L2-ART-02 --- Artifact interpretation

-   **Domain:** Unit 7\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    WAL/replication-slot retention is safe.\
-   **Estimated time:** 7 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
revision=r42 target_clusters=2 ring=canary
stage2e-east-lab: health=PASS evidence=fresh
stage2e-west-lab: health=FAIL evidence=fresh
next_action=promote
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

Promotion is unsafe: West has a fresh FAIL. Halt the ring, preserve
revision and health evidence, mitigate the failing cluster, and require
fresh passing evidence before promotion. Sync/selection status does not
override health. Verify per cluster and retain the timestamp, revision,
target identity and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U7-L3-ART-03 --- Artifact interpretation

-   **Domain:** Unit 7\
-   **Level:** L3\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    replication versus backup is safe.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
source=stage2e-east-lab target=stage2e-west-lab
last_seen=unknown; owner=platform
change_time=10:03Z; alert_time=10:04Z
summary=green
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

The summary conflicts with missing source/last-seen evidence. Mark the
affected path UNKNOWN, check source and target independently, correlate
the change and alert, and do not treat missing telemetry as healthy.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U7-L2-CFG-01 --- Configuration/artifact review

-   **Domain:** Unit 7\
-   **Level:** L2\
-   **Objective:** Review a scope/ownership artifact for at least three
    defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
target=all-clusters
owner=unspecified
health_gate=disabled
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Target is broad/ambiguous. **Correction:** Resolve and
    display the exact intended cluster set. **Failure avoided:**
    unintended clusters can be changed.
2.  **Defect:** Owner is missing. **Correction:** Assign accountable
    owner and approver. **Failure avoided:** incident response and
    decisions stall.
3.  **Defect:** Health gate is disabled. **Correction:** Add measurable
    per-cluster gates and halt conditions. **Failure avoided:** bad
    changes propagate unchecked.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U7-L3-CFG-02 --- Configuration/artifact review

-   **Domain:** Unit 7\
-   **Level:** L3\
-   **Objective:** Review a rollout/consistency artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
promote_on=sync-success-only
unknown_evidence=pass
rollback_revision=none
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Sync success is the only gate. **Correction:** Check
    runtime health and relevant data/policy/route signals. **Failure
    avoided:** desired state can apply while service fails.
2.  **Defect:** Unknown evidence passes. **Correction:** Represent
    UNKNOWN/UNREACHABLE and block critical promotion. **Failure
    avoided:** missing data creates false green.
3.  **Defect:** No rollback revision. **Correction:** Record a
    known-good revision and rollback criteria. **Failure avoided:**
    recovery is improvised under pressure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U7-L3-CFG-03 --- Configuration/artifact review

-   **Domain:** Unit 7\
-   **Level:** L3\
-   **Objective:** Review a security/evidence artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
credential_scope=fleet-admin
report_timestamp=omitted
verification=central-only
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Credential is overbroad. **Correction:** Use least
    privilege and narrower cluster scope. **Failure avoided:** hub
    compromise can affect the fleet.
2.  **Defect:** Timestamp/freshness omitted. **Correction:** Record
    timestamp, source and freshness threshold. **Failure avoided:**
    stale report can be mistaken for current.
3.  **Defect:** Only central verification. **Correction:** Verify
    affected clusters independently and retain local evidence. **Failure
    avoided:** hub outage/compromise can conceal failure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U7-L4-INC-01 --- Incident/diagnosis

-   **Domain:** Unit 7\

-   **Level:** L4\

-   **Objective:** Sequence an incident response involving consistency
    anomalies, sync/async, lag/RPO, WAL retention, object replication,
    artifact hashes and schema evolution.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario only;
    no real-system mutation. **Question**

\[SYNTHETIC\] A change related to artifact completeness and hash gate is
followed by degraded behavior in stage2e-west-lab; stage2e-east-lab
telemetry is stale. Respond in this order: first safe action → localize
→ mitigate → verify per cluster → communicate → prevent.

**Model answer and reasoning**

First halt further ring promotion/fan-out and preserve evidence.
Localize by verifying explicit contexts, cluster identity, last-seen
timestamps, local health and change revision. Mitigate only the
implicated ring/dependency using an approved rollback or isolation path
after checking data/write authority where relevant. Verify East and West
independently: service health, configuration/policy revision,
data/traffic state and alert delivery. Communicate scope, known facts,
uncertainty, owner and next update per region. Prevent recurrence with a
regression test, stronger freshness/health gate, rollback rehearsal and
named follow-up.

**Common wrong answer(s)**

Wrong: change both clusters at once, assume stale telemetry means
recovery, declare a root cause without evidence, or fail to communicate
uncertainty.

**Scoring rubric**

5 points: safe halt/evidence preservation (1); correct localization (1);
bounded mitigation (1); independent verification and communication (1);
durable prevention (1).

### U7-L3-DES-01 --- Design question

-   **Domain:** Unit 7\
-   **Level:** L3\
-   **Objective:** Design an operating pattern for consistency
    anomalies, sync/async, lag/RPO, WAL retention, object replication,
    artifact hashes and schema evolution.\
-   **Estimated time:** 15 minutes

**Question**

Design a zero-budget two-kind-cluster lab pattern that can later inform
a production design for consistency anomalies, sync/async, lag/RPO, WAL
retention, object replication, artifact hashes and schema evolution.
State requirements, architecture, ownership, failure modes, safety
gates, evidence, rollback and limits of the lab.

**Model answer and reasoning**

A defensible design starts with business/security/SLO constraints and
failure domains, chooses the simplest architecture that meets them,
identifies the owner and exact target scope, defines per-cluster health
and UNKNOWN states, protects credentials, and gives a bounded
rollout/rollback plan. Explain cost, latency, consistency and
operational trade-offs. Explicitly state that two local kind clusters
share a host and do not prove geographic resilience.

**Common wrong answer(s)**

Wrong: select tools before requirements, omit ownership/rollback, rely
on a green aggregate, or claim a local lab proves production regions.

**Scoring rubric**

Score 0--4 each: correctness; trade-off reasoning; safety/blast-radius
control; evidence/verification; operational feasibility (20 points
total).

### U7-L2-CALC-01 --- Calculation

-   **Domain:** Unit 7\
-   **Level:** L2\
-   **Objective:** Calculate a fleet outcome from synthetic counts.\
-   **Estimated time:** 6 minutes

**Question**

\[SYNTHETIC\] East: 8,000 requests/min, 99.9% good. West: 2,000
requests/min, 90% good. Compute global success.

**Model answer and reasoning**

East good=8,000×0.999=7,992; West=2,000×0.90=1,800;
total=9,792/10,000=97.92%. Keep regional guardrails; a global ratio can
hide local harm.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U7-L3-EVID-02 --- Evidence quality

-   **Domain:** Unit 7\
-   **Level:** L3\
-   **Objective:** Distinguish workflow evidence from production
    assurance.\
-   **Estimated time:** 7 minutes

**Question**

An engineer says two local kind clusters passing a lab proves two-region
resilience. Is the claim justified?

**Model answer and reasoning**

No. The lab tests workflow mechanics only. Real proof needs independent
failure domains, real WAN/routing, data authority/recovery, capacity,
production telemetry and rehearsed operations.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U7-L3-COMP-03 --- Comparison

-   **Domain:** Unit 7\
-   **Level:** L3\
-   **Objective:** Compare simple lab and production architecture.\
-   **Estimated time:** 8 minutes

**Question**

Compare a low-cost local approach with a production fleet approach for
quorum and partition assumptions. Give one benefit, one cost and one
failure mode each.

**Model answer and reasoning**

Local is cheap and inspectable but shares host/failure domains and has
limited scale. Production can improve isolation/automation but adds
cost, control-plane dependencies and more failure modes. Choose from
requirements.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U7-L2-CTX-04 --- Context safety

-   **Domain:** Unit 7\
-   **Level:** L2\
-   **Objective:** Verify target before a cluster-scoped action.\
-   **Estimated time:** 9 minutes

**Question**

\[SYNTHETIC\] Context list: `* kind-stage2e-east-lab`;
`kind-stage2e-west-lab`. A change is intended for West. What must be
checked?

**Model answer and reasoning**

Use an explicit reviewed `--context kind-stage2e-west-lab`, verify it
maps to the intended disposable cluster, inspect namespace/resources and
use dry-run where useful. Verify results per cluster. Do not rely on the
current `*` context.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U7-L4-GATE-05 --- Evidence under uncertainty

-   **Domain:** Unit 7\
-   **Level:** L4\
-   **Objective:** Name evidence that should block promotion.\
-   **Estimated time:** 10 minutes

**Question**

For replicated canary heartbeat, list three independent signals and one
blocking condition.

**Model answer and reasoning**

Check source identity/freshness, local health/alert evidence, and the
unit-specific control (capacity/data/policy/routing/desired state).
Block on critical FAIL, UNKNOWN, stale evidence or ambiguous target.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

## Unit 8 --- Multi-Cluster Observability and Policy Governance

**Scope:** telemetry identity/cardinality, aggregation, SLO arithmetic,
local alerts, conformance, quarantine, policy rings, RBAC and hub
compromise.

### U8-L1-SA-01 --- Conceptual short answer

-   **Domain:** Unit 8\
-   **Level:** L1\
-   **Objective:** Explain expected-cluster inventory and its
    operational consequence.\
-   **Estimated time:** 5 minutes

**Question**

Explain **expected-cluster inventory**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Expected-cluster inventory must be evaluated against the stated
telemetry identity/cardinality, aggregation, SLO arithmetic, local
alerts, conformance, quarantine, policy rings, RBAC and hub compromise.
A strong answer identifies the requirement, names the relevant
cluster/failure boundary, distinguishes desired state from observed
evidence, and proposes a verification method plus a corrective action.
Record owner, timestamp and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U8-L1-SA-02 --- Conceptual short answer

-   **Domain:** Unit 8\
-   **Level:** L1\
-   **Objective:** Explain unique cluster identity labels and its
    operational consequence.\
-   **Estimated time:** 6 minutes

**Question**

Explain **unique cluster identity labels**. State why it matters, one
failure mode, and what evidence would verify the claim.

**Model answer and reasoning**

Unique cluster identity labels must be evaluated against the stated
telemetry identity/cardinality, aggregation, SLO arithmetic, local
alerts, conformance, quarantine, policy rings, RBAC and hub compromise.
A strong answer identifies the requirement, names the relevant
cluster/failure boundary, distinguishes desired state from observed
evidence, and proposes a verification method plus a corrective action.
Record owner, timestamp and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U8-L2-SA-03 --- Conceptual short answer

-   **Domain:** Unit 8\
-   **Level:** L2\
-   **Objective:** Explain metric cardinality and its operational
    consequence.\
-   **Estimated time:** 7 minutes

**Question**

Explain **metric cardinality**. State why it matters, one failure mode,
and what evidence would verify the claim.

**Model answer and reasoning**

Metric cardinality must be evaluated against the stated telemetry
identity/cardinality, aggregation, SLO arithmetic, local alerts,
conformance, quarantine, policy rings, RBAC and hub compromise. A strong
answer identifies the requirement, names the relevant cluster/failure
boundary, distinguishes desired state from observed evidence, and
proposes a verification method plus a corrective action. Record owner,
timestamp and scope where relevant.

**Common wrong answer(s)**

Common wrong answer: define the term without explaining its failure mode
or how to verify it.

### U8-L1-MCQ-01 --- Multiple choice (exactly four options)

-   **Domain:** Unit 8\
-   **Level:** L1\
-   **Objective:** Choose a safe decision about ratio-of-sums global
    SLO.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **ratio-of-sums global SLO**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for ratio-of-sums global SLO.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U8-L2-MCQ-02 --- Multiple choice (exactly four options)

-   **Domain:** Unit 8\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about local alerts during hub
    outage.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **local alerts during hub
outage** under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for local alerts during hub outage.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U8-L2-MCQ-03 --- Multiple choice (exactly four options)

-   **Domain:** Unit 8\
-   **Level:** L2\
-   **Objective:** Choose a safe decision about absent-cluster
    detection.\
-   **Estimated time:** 4 minutes

**Question**

Which response is best when evaluating **absent-cluster detection**
under the stated fleet constraints?

A. Use explicit scope, verified evidence, and a bounded action with
rollback for absent-cluster detection.

B. Assume the fleet-wide summary is sufficient and skip per-cluster
checks.

C. Treat missing or stale evidence as a successful result.

D. Apply the change everywhere immediately to reduce operational
overhead.

**Model answer and reasoning**

**A is correct.** It preserves explicit scope, verifies the target and
evidence, limits blast radius and retains rollback. **B is wrong**
because aggregate views can hide cluster-specific failure. **C is
wrong** because unknown/stale evidence is not a pass. **D is wrong**
because broad immediate rollout removes the canary and health gates.

**Common wrong answer(s)**

B ignores per-cluster failure; C converts uncertainty into false
confidence; D increases blast radius before the result is known.

### U8-L2-ART-01 --- Artifact interpretation

-   **Domain:** Unit 8\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    FAIL versus UNKNOWN is safe.\
-   **Estimated time:** 6 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
cluster=stage2e-east-lab status=PASS timestamp=10:00Z
cluster=stage2e-west-lab status=UNKNOWN timestamp=09:00Z
expected_cluster_count=2 fresh_reports=1
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

East has fresh PASS evidence; West is UNKNOWN with stale evidence. The
fleet is not green. Identify West's local state and obtain fresh
evidence before a gated action. Preserve timestamps and source identity.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U8-L2-ART-02 --- Artifact interpretation

-   **Domain:** Unit 8\
-   **Level:** L2\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    quarantine and ring gate is safe.\
-   **Estimated time:** 7 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
revision=r42 target_clusters=2 ring=canary
stage2e-east-lab: health=PASS evidence=fresh
stage2e-west-lab: health=FAIL evidence=fresh
next_action=promote
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

Promotion is unsafe: West has a fresh FAIL. Halt the ring, preserve
revision and health evidence, mitigate the failing cluster, and require
fresh passing evidence before promotion. Sync/selection status does not
override health. Verify per cluster and retain the timestamp, revision,
target identity and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U8-L3-ART-03 --- Artifact interpretation

-   **Domain:** Unit 8\
-   **Level:** L3\
-   **Objective:** Read a synthetic fleet artifact and decide whether
    audit-warn-enforce progression is safe.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
source=stage2e-east-lab target=stage2e-west-lab
last_seen=unknown; owner=platform
change_time=10:03Z; alert_time=10:04Z
summary=green
```

**Question**

What does the artifact prove, what remains unknown, and what is the next
safe action?

**Model answer and reasoning**

The summary conflicts with missing source/last-seen evidence. Mark the
affected path UNKNOWN, check source and target independently, correlate
the change and alert, and do not treat missing telemetry as healthy.
Verify per cluster and retain the timestamp, revision, target identity
and observed state.

**Common wrong answer(s)**

Common wrong answer: accept `summary=green` or proceed because one
cluster passed; this ignores contradictory or stale evidence.

### U8-L2-CFG-01 --- Configuration/artifact review

-   **Domain:** Unit 8\
-   **Level:** L2\
-   **Objective:** Review a scope/ownership artifact for at least three
    defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
target=all-clusters
owner=unspecified
health_gate=disabled
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Target is broad/ambiguous. **Correction:** Resolve and
    display the exact intended cluster set. **Failure avoided:**
    unintended clusters can be changed.
2.  **Defect:** Owner is missing. **Correction:** Assign accountable
    owner and approver. **Failure avoided:** incident response and
    decisions stall.
3.  **Defect:** Health gate is disabled. **Correction:** Add measurable
    per-cluster gates and halt conditions. **Failure avoided:** bad
    changes propagate unchecked.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U8-L3-CFG-02 --- Configuration/artifact review

-   **Domain:** Unit 8\
-   **Level:** L3\
-   **Objective:** Review a rollout/consistency artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
promote_on=sync-success-only
unknown_evidence=pass
rollback_revision=none
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Sync success is the only gate. **Correction:** Check
    runtime health and relevant data/policy/route signals. **Failure
    avoided:** desired state can apply while service fails.
2.  **Defect:** Unknown evidence passes. **Correction:** Represent
    UNKNOWN/UNREACHABLE and block critical promotion. **Failure
    avoided:** missing data creates false green.
3.  **Defect:** No rollback revision. **Correction:** Record a
    known-good revision and rollback criteria. **Failure avoided:**
    recovery is improvised under pressure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U8-L3-CFG-03 --- Configuration/artifact review

-   **Domain:** Unit 8\
-   **Level:** L3\
-   **Objective:** Review a security/evidence artifact for at least
    three defects.\
-   **Estimated time:** 8 minutes

**\[SYNTHETIC ARTIFACT\]**

``` text
credential_scope=fleet-admin
report_timestamp=omitted
verification=central-only
```

**Question**

Identify at least three defects. For each, provide the correction and
name the operational failure it could cause.

**Model answer and reasoning**

1.  **Defect:** Credential is overbroad. **Correction:** Use least
    privilege and narrower cluster scope. **Failure avoided:** hub
    compromise can affect the fleet.
2.  **Defect:** Timestamp/freshness omitted. **Correction:** Record
    timestamp, source and freshness threshold. **Failure avoided:**
    stale report can be mistaken for current.
3.  **Defect:** Only central verification. **Correction:** Verify
    affected clusters independently and retain local evidence. **Failure
    avoided:** hub outage/compromise can conceal failure.

**Common wrong answer(s)**

Common wrong answer: offer generic advice such as 'make it safer'
without identifying the defect, fix and failure.

### U8-L4-INC-01 --- Incident/diagnosis

-   **Domain:** Unit 8\

-   **Level:** L4\

-   **Objective:** Sequence an incident response involving telemetry
    identity/cardinality, aggregation, SLO arithmetic, local alerts,
    conformance, quarantine, policy rings, RBAC and hub compromise.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario only;
    no real-system mutation. **Question**

\[SYNTHETIC\] A change related to policy version skew is followed by
degraded behavior in stage2e-west-lab; stage2e-east-lab telemetry is
stale. Respond in this order: first safe action → localize → mitigate →
verify per cluster → communicate → prevent.

**Model answer and reasoning**

First halt further ring promotion/fan-out and preserve evidence.
Localize by verifying explicit contexts, cluster identity, last-seen
timestamps, local health and change revision. Mitigate only the
implicated ring/dependency using an approved rollback or isolation path
after checking data/write authority where relevant. Verify East and West
independently: service health, configuration/policy revision,
data/traffic state and alert delivery. Communicate scope, known facts,
uncertainty, owner and next update per region. Prevent recurrence with a
regression test, stronger freshness/health gate, rollback rehearsal and
named follow-up.

**Common wrong answer(s)**

Wrong: change both clusters at once, assume stale telemetry means
recovery, declare a root cause without evidence, or fail to communicate
uncertainty.

**Scoring rubric**

5 points: safe halt/evidence preservation (1); correct localization (1);
bounded mitigation (1); independent verification and communication (1);
durable prevention (1).

### U8-L3-DES-01 --- Design question

-   **Domain:** Unit 8\
-   **Level:** L3\
-   **Objective:** Design an operating pattern for telemetry
    identity/cardinality, aggregation, SLO arithmetic, local alerts,
    conformance, quarantine, policy rings, RBAC and hub compromise.\
-   **Estimated time:** 15 minutes

**Question**

Design a zero-budget two-kind-cluster lab pattern that can later inform
a production design for telemetry identity/cardinality, aggregation, SLO
arithmetic, local alerts, conformance, quarantine, policy rings, RBAC
and hub compromise. State requirements, architecture, ownership, failure
modes, safety gates, evidence, rollback and limits of the lab.

**Model answer and reasoning**

A defensible design starts with business/security/SLO constraints and
failure domains, chooses the simplest architecture that meets them,
identifies the owner and exact target scope, defines per-cluster health
and UNKNOWN states, protects credentials, and gives a bounded
rollout/rollback plan. Explain cost, latency, consistency and
operational trade-offs. Explicitly state that two local kind clusters
share a host and do not prove geographic resilience.

**Common wrong answer(s)**

Wrong: select tools before requirements, omit ownership/rollback, rely
on a green aggregate, or claim a local lab proves production regions.

**Scoring rubric**

Score 0--4 each: correctness; trade-off reasoning; safety/blast-radius
control; evidence/verification; operational feasibility (20 points
total).

### U8-L2-CALC-01 --- Calculation

-   **Domain:** Unit 8\
-   **Level:** L2\
-   **Objective:** Calculate a fleet outcome from synthetic counts.\
-   **Estimated time:** 6 minutes

**Question**

\[SYNTHETIC\] East: 8,000 requests/min, 99.9% good. West: 2,000
requests/min, 90% good. Compute global success.

**Model answer and reasoning**

East good=8,000×0.999=7,992; West=2,000×0.90=1,800;
total=9,792/10,000=97.92%. Keep regional guardrails; a global ratio can
hide local harm.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U8-L3-EVID-02 --- Evidence quality

-   **Domain:** Unit 8\
-   **Level:** L3\
-   **Objective:** Distinguish workflow evidence from production
    assurance.\
-   **Estimated time:** 7 minutes

**Question**

An engineer says two local kind clusters passing a lab proves two-region
resilience. Is the claim justified?

**Model answer and reasoning**

No. The lab tests workflow mechanics only. Real proof needs independent
failure domains, real WAN/routing, data authority/recovery, capacity,
production telemetry and rehearsed operations.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U8-L3-COMP-03 --- Comparison

-   **Domain:** Unit 8\
-   **Level:** L3\
-   **Objective:** Compare simple lab and production architecture.\
-   **Estimated time:** 8 minutes

**Question**

Compare a low-cost local approach with a production fleet approach for
metadata-only credential inventory. Give one benefit, one cost and one
failure mode each.

**Model answer and reasoning**

Local is cheap and inspectable but shares host/failure domains and has
limited scale. Production can improve isolation/automation but adds
cost, control-plane dependencies and more failure modes. Choose from
requirements.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U8-L2-CTX-04 --- Context safety

-   **Domain:** Unit 8\
-   **Level:** L2\
-   **Objective:** Verify target before a cluster-scoped action.\
-   **Estimated time:** 9 minutes

**Question**

\[SYNTHETIC\] Context list: `* kind-stage2e-east-lab`;
`kind-stage2e-west-lab`. A change is intended for West. What must be
checked?

**Model answer and reasoning**

Use an explicit reviewed `--context kind-stage2e-west-lab`, verify it
maps to the intended disposable cluster, inspect namespace/resources and
use dry-run where useful. Verify results per cluster. Do not rely on the
current `*` context.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

### U8-L4-GATE-05 --- Evidence under uncertainty

-   **Domain:** Unit 8\
-   **Level:** L4\
-   **Objective:** Name evidence that should block promotion.\
-   **Estimated time:** 10 minutes

**Question**

For regional SLO guardrails, list three independent signals and one
blocking condition.

**Model answer and reasoning**

Check source identity/freshness, local health/alert evidence, and the
unit-specific control (capacity/data/policy/routing/desired state).
Block on critical FAIL, UNKNOWN, stale evidence or ambiguous target.

**Common wrong answer(s)**

Wrong: average percentages without denominators, infer production
guarantees from local tests, or promote with unknown/stale evidence.

## Cross-unit integration scenarios

These scenarios combine two or more units. Artifacts and values are
`[SYNTHETIC]`; no live incident or command execution is implied.

### X-L3-INT-01 --- Cross-unit integration scenario

-   **Domain:** U1/U2\

-   **Level:** L3\

-   **Objective:** Combine U1/U2 reasoning under topology + lifecycle +
    cidr.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East pod CIDR=10.20.0.0/16; West pod CIDR=10.20.0.0/16; routed interconnect proposed.
```

**Question**

**Scenario:** Topology + lifecycle + CIDR. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Stop rollout. Overlapping ranges can create ambiguous/unreachable
routes. Replan non-overlapping pod/service and connected networks,
update registry and verify routes in a throwaway lab. Record ADR and
owner.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-02 --- Cross-unit integration scenario

-   **Domain:** U2/U3\

-   **Level:** L3\

-   **Objective:** Combine U2/U3 reasoning under context + gitops
    fan-out.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Active context is East; selector resolves East and West; change intended for East only.
```

**Question**

**Scenario:** Context + GitOps fan-out. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Freeze mutation, inspect explicit context and resolved target set,
constrain selector/ring and require preview. Verify each cluster's
revision. A small diff does not imply small fan-out.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-03 --- Cross-unit integration scenario

-   **Domain:** U2/U3\

-   **Level:** L3\

-   **Objective:** Combine U2/U3 reasoning under registry + selector +
    wrong target.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] West is tier=prod; selector `tier!=sandbox` selects East, West and analytics-prod.
```

**Question**

**Scenario:** Registry + selector + wrong target. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Do not apply. Print resolved targets and use explicit reviewed
allowlist/labels. Add selector tests and verify actual inventory. Count
YAML files, not target clusters, is the wrong blast-radius measure.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-04 --- Cross-unit integration scenario

-   **Domain:** U3/U8\

-   **Level:** L3\

-   **Objective:** Combine U3/U8 reasoning under ring + slo + rollback.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Sync PASS; West success ratio falls to 96% against 99% regional guardrail.
```

**Question**

**Scenario:** Ring + SLO + rollback. Provide first safe action, affected
cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Halt promotion, preserve revision and numerator/denominator, rollback
ring if safe, verify per cluster and add an SLO regression gate.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-05 --- Cross-unit integration scenario

-   **Domain:** U3/U8\

-   **Level:** L3\

-   **Objective:** Combine U3/U8 reasoning under gitops hub outage.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Hub is unavailable; running workloads respond; sync status is unavailable.
```

**Question**

**Scenario:** GitOps hub outage. Provide first safe action, affected
cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Treat reconciliation/visibility as degraded, not necessarily workloads.
Use local telemetry and verified cluster access, pause changes, recover
hub safely, reconcile inventory before resuming.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-06 --- Cross-unit integration scenario

-   **Domain:** U4/U8\

-   **Level:** L3\

-   **Objective:** Combine U4/U8 reasoning under endpoint + dns + local
    alerting.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East resolves West service to stale endpoint; West local service is healthy; central dashboard is delayed.
```

**Question**

**Scenario:** Endpoint + DNS + local alerting. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Localize caller resolver and target endpoint; inspect
forwarding/cache/record freshness and local alert path. Verify
end-to-end request after bounded correction.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-07 --- Cross-unit integration scenario

-   **Domain:** U4/U8\

-   **Level:** L3\

-   **Objective:** Combine U4/U8 reasoning under tls rotation +
    routing + communication.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] West endpoint resolves but mTLS handshake fails after trust-root update; East-local calls work.
```

**Question**

**Scenario:** TLS rotation + routing + communication. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Pause rotation/fan-out; compare trust bundle, certificate validity and
peer identity. Restore known-good overlap through approved path, verify
both clusters and communicate uncertainty.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-08 --- Cross-unit integration scenario

-   **Domain:** U5\

-   **Level:** L3\

-   **Objective:** Combine U5 reasoning under dns ttl + client tail.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Detection=20 s; decision/propagation=15 s; TTL=60 s; client cache/connection tail=90 s; sequential worst-case assumption.
```

**Question**

**Scenario:** DNS TTL + client tail. Provide first safe action, affected
cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Estimate=20+15+60+90=185 s, excluding capacity warmup. This is
illustrative, not measured; actual clients vary and TTL is not a hard
bound.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-09 --- Cross-unit integration scenario

-   **Domain:** U5/U6\

-   **Level:** L3\

-   **Objective:** Combine U5/U6 reasoning under false-positive health +
    capacity.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] One probe fails once; West has 55% spare capacity but shift adds 70% of East load.
```

**Question**

**Scenario:** False-positive health + capacity. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Do not shift automatically on one probe. Validate independent
signals/hysteresis and per-resource/downstream capacity; use bounded
shift or human approval.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-10 --- Cross-unit integration scenario

-   **Domain:** U6\

-   **Level:** L3\

-   **Objective:** Combine U6 reasoning under active-active stateless +
    n+1.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East load=600 req/s; West=400 req/s; West capacity=700 req/s; East fails.
```

**Question**

**Scenario:** Active-active stateless + N+1. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

West receives 1,000 req/s; utilization=1,000/700=142.9%, over capacity.
Add capacity, shed load, partially shift or choose another pattern.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-11 --- Cross-unit integration scenario

-   **Domain:** U5/U6/U7\

-   **Level:** L3\

-   **Objective:** Combine U5/U6/U7 reasoning under fencing + routing +
    async replication.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] West promoted while old East writer may still accept writes; DNS shift is underway.
```

**Question**

**Scenario:** Fencing + routing + async replication. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Do not route authoritative writes until old writer is fenced and
ownership/promotion verified. Health/DNS does not establish write
authority.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-12 --- Cross-unit integration scenario

-   **Domain:** U7/U6\

-   **Level:** L3\

-   **Objective:** Combine U7/U6 reasoning under lag spike + rpo +
    maintenance.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] p99 replication lag rises from 2 s to 45 s during backfill; RPO target=10 s; acknowledged-write timeline unavailable.
```

**Question**

**Scenario:** Lag spike + RPO + maintenance. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

RPO target is at risk; pause/rate-limit backfill and inspect canary/lag.
Exact lost writes cannot be inferred from lag alone.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-13 --- Cross-unit integration scenario

-   **Domain:** U7/U4\

-   **Level:** L3\

-   **Objective:** Combine U7/U4 reasoning under stale reads +
    sessions + reconciliation.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Client writes version 12 in East; after route shift West returns version 10.
```

**Question**

**Scenario:** Stale reads + sessions + reconciliation. Provide first
safe action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Stale read/monotonic-read risk. Apply data-class policy such as
read-your-writes/session routing or wait for freshness; preserve and
reconcile divergence.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-14 --- Cross-unit integration scenario

-   **Domain:** U7\

-   **Level:** L3\

-   **Objective:** Combine U7 reasoning under object replication + model
    hash.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] West has `model-v17.bin` but SHA-256 differs from approved manifest.
```

**Question**

**Scenario:** Object replication + model hash. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Block alias promotion; verify completeness and approved hash, then
re-replicate/reconcile. Filename alone is not integrity; replication is
not backup.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-15 --- Cross-unit integration scenario

-   **Domain:** U7/U3\

-   **Level:** L3\

-   **Objective:** Combine U7/U3 reasoning under schema migration +
    replication.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] New app writes `feature_v2`; West app/replica is incompatible; selector includes both clusters.
```

**Question**

**Scenario:** Schema migration + replication. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Halt ring; use expand-contract and backward-compatible rollout, verify
both regions before contraction. Do not drop old schema first.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-16 --- Cross-unit integration scenario

-   **Domain:** U8/U3\

-   **Level:** L3\

-   **Objective:** Combine U8/U3 reasoning under global slo hides
    region.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East 99,900/100,000 good; West 600/1,000 good.
```

**Question**

**Scenario:** Global SLO hides region. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Global=100,500/101,000=99.50495%; unweighted
average=(99.9%+60%)/2=79.95%. Use ratio-of-sums plus regional guardrail.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-17 --- Cross-unit integration scenario

-   **Domain:** U8/U2\

-   **Level:** L3\

-   **Objective:** Combine U8/U2 reasoning under missing telemetry +
    conformance.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] West heartbeat missing 8 min; last conformance PASS is 1 h old; inventory expects West.
```

**Question**

**Scenario:** Missing telemetry + conformance. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Mark UNKNOWN/UNREACHABLE; block gated promotion, investigate
collection/API path, require fresh evidence. Do not reuse old PASS as
current.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-18 --- Cross-unit integration scenario

-   **Domain:** U8/U3\

-   **Level:** L3\

-   **Objective:** Combine U8/U3 reasoning under quarantine + ring +
    exception.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East critical admission policy FAIL; exception covers another namespace and expired yesterday.
```

**Question**

**Scenario:** Quarantine + ring + exception. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Block East and gated promotion; exception is out of scope and expired.
Require fresh evidence and authorized review.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-19 --- Cross-unit integration scenario

-   **Domain:** U8/U3\

-   **Level:** L3\

-   **Objective:** Combine U8/U3 reasoning under policy version skew.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East capability is known; West policy-engine version unknown and report stale.
```

**Question**

**Scenario:** Policy version skew. Provide first safe action, affected
cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Do not promote enforcement until compatibility matrix and fresh report
are verified. Unsupported fields may not always fail loudly.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-20 --- Cross-unit integration scenario

-   **Domain:** U3/U8\

-   **Level:** L3\

-   **Objective:** Combine U3/U8 reasoning under hub credential
    compromise.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Hub can write policies, dashboards and alert routes in both clusters; independent audit shows unexpected change.
```

**Question**

**Scenario:** Hub credential compromise. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Stop fanout, preserve evidence, map credential reach, revoke/rotate
through incident process, independently inspect clusters and restore
trusted state only after verification.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-21 --- Cross-unit integration scenario

-   **Domain:** U2/U8\

-   **Level:** L3\

-   **Objective:** Combine U2/U8 reasoning under broad kubeconfig +
    rotation.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Fleet-admin credential has no owner, expiry or scope metadata.
```

**Question**

**Scenario:** Broad kubeconfig + rotation. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Restrict use, establish owner/reach from approved metadata/audit,
replace with scoped identities and rotate/revoke. Never print token
values.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-22 --- Cross-unit integration scenario

-   **Domain:** U8/U3\

-   **Level:** L3\

-   **Objective:** Combine U8/U3 reasoning under debug logs + egress
    surge.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Ring enables verbose logging; log bytes triple and central queue grows.
```

**Question**

**Scenario:** Debug logs + egress surge. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Halt ring, measure by cluster/service, revert or bound debug, preserve
required evidence and add volume/cardinality budget gate.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-23 --- Cross-unit integration scenario

-   **Domain:** U6/U5\

-   **Level:** L3\

-   **Objective:** Combine U6/U5 reasoning under region evacuation +
    capacity.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East=700 req/s; West=500 req/s; West safe capacity=900 req/s; East lost.
```

**Question**

**Scenario:** Region evacuation + capacity. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Total=1,200/900=133.3% capacity. Full evacuation is unsafe; shed load,
add capacity or use partial service plan before shifting.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-24 --- Cross-unit integration scenario

-   **Domain:** U2/U3\

-   **Level:** L3\

-   **Objective:** Combine U2/U3 reasoning under unsupported version +
    replacement.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] West marked unsupported by verified inventory; rollout targets all READY clusters.
```

**Question**

**Scenario:** Unsupported version + replacement. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Quarantine/upgrade/replace West through lifecycle plan; keep it out
until version and baseline are verified. READY alone is insufficient.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-25 --- Cross-unit integration scenario

-   **Domain:** U7/U5/U6\

-   **Level:** L3\

-   **Objective:** Combine U7/U5/U6 reasoning under failback after
    divergence.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East returns; 17 keys differ; traffic remains West-primary.
```

**Question**

**Scenario:** Failback after divergence. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Keep one write authority, preserve both values, reconcile by policy,
verify parity/capacity/policy, then gate gradual failback.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-26 --- Cross-unit integration scenario

-   **Domain:** U2/U3/U8\

-   **Level:** L3\

-   **Objective:** Combine U2/U3/U8 reasoning under new cluster
    onboarding.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] New cluster has region label but missing team, datasource, alert receiver and policy baseline.
```

**Question**

**Scenario:** New cluster onboarding. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Do not mark ready. Complete identity, policy, telemetry, datasource,
routes and conformance before bounded ring onboarding.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-27 --- Cross-unit integration scenario

-   **Domain:** U4/U8\

-   **Level:** L3\

-   **Objective:** Combine U4/U8 reasoning under trace missing + clock
    skew.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East log at 10:01:04; West at 10:01:02; trace span missing; clock offsets unknown.
```

**Question**

**Scenario:** Trace missing + clock skew. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Use correlation ID/trace context where available; wall-clock order is
uncertain. Inspect sampling/export gaps and clock metadata.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-28 --- Cross-unit integration scenario

-   **Domain:** U5/U7\

-   **Level:** L3\

-   **Objective:** Combine U5/U7 reasoning under dns simulation + data
    freshness.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Client reads shift to West; canary lag=25 s against 5 s target.
```

**Question**

**Scenario:** DNS simulation + data freshness. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Do not enable authoritative writes or claim data readiness; preserve
read/write policy and gate traffic by data role/freshness.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-29 --- Cross-unit integration scenario

-   **Domain:** U3/U8\

-   **Level:** L3\

-   **Objective:** Combine U3/U8 reasoning under hub down during bad
    policy rollout.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Hub unreachable during partial policy rollout; East FAIL, West UNKNOWN.
```

**Question**

**Scenario:** Hub down during bad policy rollout. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Stop promotion through approved independent control, preserve
per-cluster evidence, inspect both locally and reconcile trusted
revision only after scope is known.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L3-INT-30 --- Cross-unit integration scenario

-   **Domain:** U8/U5\

-   **Level:** L3\

-   **Objective:** Combine U8/U5 reasoning under alert inhibition hides
    region.\

-   **Estimated time:** 8 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Shared dependency alert inhibits regional errors for both regions because matching omits region.
```

**Question**

**Scenario:** Alert inhibition hides region. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Narrow inhibition scope to intended derivatives, retain regional
symptoms and test routing. Overbroad inhibition hides impact.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-31 --- Cross-unit integration scenario

-   **Domain:** U8/U2\

-   **Level:** L4\

-   **Objective:** Combine U8/U2 reasoning under unreachable conformance
    scan.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East fresh PASS; West UNREACHABLE; weighted fleet score=98%.
```

**Question**

**Scenario:** Unreachable conformance scan. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Critical gate overrides aggregate score. Keep West not eligible until
reachability and fresh evidence return.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-32 --- Cross-unit integration scenario

-   **Domain:** U2/U3\

-   **Level:** L4\

-   **Objective:** Combine U2/U3 reasoning under management-plane loss
    during upgrade.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Lifecycle controller fails halfway through staged upgrade; clusters have mixed versions.
```

**Question**

**Scenario:** Management-plane loss during upgrade. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Pause next ring, inspect actual version/health per cluster, preserve
state and recover management plane safely; do not blindly rerun
mutations.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-33 --- Cross-unit integration scenario

-   **Domain:** U2/U6\

-   **Level:** L4\

-   **Objective:** Combine U2/U6 reasoning under decommission with
    home-region tenants.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Cluster looks idle but tenant registry assigns three tenants' home region to it.
```

**Question**

**Scenario:** Decommission with home-region tenants. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Block deletion; migrate ownership/data/routes with gates, verify new
home region, update registry/credentials and then decommission.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-34 --- Cross-unit integration scenario

-   **Domain:** U7/U6\

-   **Level:** L4\

-   **Objective:** Combine U7/U6 reasoning under multi-writer conflict +
    ownership.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] East and West update same record; timestamps differ by 3 s; clock quality unknown.
```

**Question**

**Scenario:** Multi-writer conflict + ownership. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Preserve both writes and apply domain ownership/version/merge policy. Do
not blindly trust wall-clock last-write-wins.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-35 --- Cross-unit integration scenario

-   **Domain:** U7/U6\

-   **Level:** L4\

-   **Objective:** Combine U7/U6 reasoning under seeding saturates
    link.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Bulk seeding drives link to 98% utilization and p99 replication lag breaches target.
```

**Question**

**Scenario:** Seeding saturates link. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Throttle/pause seed, protect production traffic, monitor lag and resume
in bounded batches; gate readiness on freshness.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-36 --- Cross-unit integration scenario

-   **Domain:** U8/U3\

-   **Level:** L4\

-   **Objective:** Combine U8/U3 reasoning under policy rollback +
    independent alert.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Rollback changes policy from enforce to audit while central hub reports healthy.
```

**Question**

**Scenario:** Policy rollback + independent alert. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Block ring; independently verify observed mode per cluster, restore
approved bundle through trusted path, inspect audit and test bypass
alert.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-37 --- Cross-unit integration scenario

-   **Domain:** U6/U8\

-   **Level:** L4\

-   **Objective:** Combine U6/U8 reasoning under capacity surge +
    telemetry overload.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Failover doubles West requests; telemetry queue grows and critical alerts delay.
```

**Question**

**Scenario:** Capacity surge + telemetry overload. Provide first safe
action, affected cluster/region, mitigation/decision, per-cluster
verification, communication and durable prevention. State uncertainty
explicitly.

**Model answer and reasoning**

Protect critical telemetry, bound debug volume, measure queue and
service capacity separately, stage traffic and preserve local alerting.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-38 --- Cross-unit integration scenario

-   **Domain:** U3/U5/U7/U8\

-   **Level:** L4\

-   **Objective:** Combine U3/U5/U7/U8 reasoning under incident
    commander handoff.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Ring begins; lag breaches target; region health uncertain; on-call shift changes.
```

**Question**

**Scenario:** Incident commander handoff. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Handoff timeline, owners, write authority, data uncertainty and next
actions. Halt ring, localize, gate writes/failover, communicate per
region and record acceptance.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-39 --- Cross-unit integration scenario

-   **Domain:** U2/U6/U7/U8\

-   **Level:** L4\

-   **Objective:** Combine U2/U6/U7/U8 reasoning under readiness
    review.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Standby passes cluster checks but data canary stale, one credential expired and regional SLO panel missing.
```

**Question**

**Scenario:** Readiness review. Provide first safe action, affected
cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Not ready: freshness, credentials and observability gates fail/unknown.
Assign owners and retest before promotion.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

### X-L4-INT-40 --- Cross-unit integration scenario

-   **Domain:** U3/U5/U6/U7/U8\

-   **Level:** L4\

-   **Objective:** Combine U3/U5/U6/U7/U8 reasoning under integrated
    capstone ordering.\

-   **Estimated time:** 12 minutes

-   **Safety / assumptions:** Conceptual or throwaway-lab scenario;
    never apply to production. **\[SYNTHETIC ARTIFACT\]**

``` text
[SYNTHETIC] Bad ring revision → p99 lag breach → East unreachable → West capacity unknown → traffic shift requested → East returns with divergent keys.
```

**Question**

**Scenario:** Integrated capstone ordering. Provide first safe action,
affected cluster/region, mitigation/decision, per-cluster verification,
communication and durable prevention. State uncertainty explicitly.

**Model answer and reasoning**

Order safely: halt rollout; preserve evidence/localize; verify West
capacity and data freshness; establish/fence write authority before
write routing; shift gradually only after gates; monitor SLO/lag; on
East return keep one writer, reconcile divergence, verify
parity/capacity/policy, gate gradual failback, and run blameless
postmortem. Do not inject or fail back while authority/data is
ambiguous.

**Evidence:** timestamped identity, relevant per-cluster
health/data/policy/traffic evidence, change revision, and
cleanup/rollback record. **Communication:** impact, uncertainty,
decision owner and next update. **Prevention:** regression test/gate
with a named owner.

**Common wrong answer(s)**

Wrong: act before verifying authority/target, infer health from missing
data, or omit per-cluster verification.

**Scoring (0--5):** safe first action (1); localization (1); bounded
mitigation (1); evidence/communication (1); prevention (1).

## Design-review whiteboard prompts

These 16 prompts are additional to the 192 scored questions. Score each
of five dimensions from 0--4: 0 absent/unsafe; 1 major gaps; 2 partial;
3 strong; 4 complete, justified and evidence-based (20 points total).

### DR-01 --- Split versus single cluster for a data/ML platform

**Scenario and constraints:** One small platform team, one regulated
dataset, GPU serving, limited budget and a defined recovery objective.

**Expected design artifacts:** Topology diagram, ADR, scored decision
matrix and failure-domain map.

**Trade-offs to discuss:** Discuss isolation/residency, shared
dependencies, stateful/stateless placement, capacity, cost, staffing and
recovery evidence.

**Minimum acceptance criteria:** Hard constraints and owners explicit;
alternatives compared; lab fidelity stated.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Choose multi-cluster by default or ignore
networking/telemetry/on-call cost.

### DR-02 --- GitOps hub versus agent-based fleet management

**Scenario and constraints:** Hypothetical 50-cluster fleet, constrained
connectivity and least-privilege requirements.

**Expected design artifacts:** Trust-boundary diagram, credential matrix
and hub recovery runbook.

**Trade-offs to discuss:** Central governance, credential scope, hub
outage, reconciliation, audit and recovery.

**Minimum acceptance criteria:** Blast radius bounded; per-cluster
verification and recovery path defined; no universal vendor claim.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** One fleet-admin credential and no
independent verification.

### DR-03 --- Ring design, health gates, quarantine and automatic halt

**Scenario and constraints:** Two lab clusters and a hypothetical
80-cluster fleet.

**Expected design artifacts:** Ring table, gate definitions, quarantine
state machine and rollback runbook.

**Trade-offs to discuss:** Ring size, representativeness,
SLO/data/policy gates, stale evidence and race conditions.

**Minimum acceptance criteria:** Resolved target preview; UNKNOWN blocks
critical promotion; final eligibility rechecked before promotion.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Promote on sync-success only.

### DR-04 --- Cross-cluster dependency policy and isolation boundaries

**Scenario and constraints:** Public API, internal data service,
compromised-cluster scenario and strict egress control.

**Expected design artifacts:** Dependency graph, allow-list policy,
negative-test plan and isolation runbook.

**Trade-offs to discuss:** Endpoint exposure, identity, DNS, retries,
timeouts, policy and isolation.

**Minimum acceptance criteria:** Caller/target ownership and ports
documented; negative and positive controls defined.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Open all east-west traffic.

### DR-05 --- DNS-based versus proxy-based global entry point

**Scenario and constraints:** Unknown client-cache tail, cost ceiling,
TLS requirements and partial provider outage.

**Expected design artifacts:** Decision matrix, health model and
client-harness measurement plan.

**Trade-offs to discuss:** TTL, cache/connection reuse, false positives,
proxy dependency, latency and cost.

**Minimum acceptance criteria:** Failover-time components explicit;
local simulation caveat; writes gated separately.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Equate TTL with total failover time.

### DR-06 --- Automated failover versus human approval under incomplete information

**Scenario and constraints:** Conflicting health signals, lag above
target and stale standby-capacity evidence.

**Expected design artifacts:** Decision tree, authority/fencing diagram
and incident runbook.

**Trade-offs to discuss:** Blast radius, evidence freshness, RTA/RPA,
service tier and approval thresholds.

**Minimum acceptance criteria:** No writes before fencing/authority;
unknown data/capacity blocks unsafe action.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Automate on one failed probe.

### DR-07 --- Active-active data-tier design with explicit consistency requirements

**Scenario and constraints:** Local reads, authoritative financial
writes and analytics tolerant of bounded staleness.

**Expected design artifacts:** Per-data-class consistency matrix and
regional ownership diagram.

**Trade-offs to discuss:** Ownership, quorum/partition assumptions,
latency, conflicts, stale reads and reconciliation.

**Minimum acceptance criteria:** Each class states tolerated
loss/staleness, authority and failover gate.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Label whole platform active-active without
write semantics.

### DR-08 --- Consistency choices for ten data classes

**Scenario and constraints:** Session cache, model artifact, model
alias, feature store, training manifest, job status, audit log, tenant
config, metrics and billing ledger.

**Expected design artifacts:** Matrix of owner, freshness, loss
tolerance, conflict policy and recovery.

**Trade-offs to discuss:** Sync/async replication, immutability, source
of truth, residency and cost.

**Minimum acceptance criteria:** All ten classes receive justified
requirements and mechanisms.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** One consistency level for all data.

### DR-09 --- Two-region quorum and witness/tie-breaker design

**Scenario and constraints:** Two data regions, partition risk and a
possible independent witness.

**Expected design artifacts:** Quorum/fencing diagram and partition
decision table.

**Trade-offs to discuss:** Voter placement, witness independence, quorum
loss and write availability.

**Minimum acceptance criteria:** Every partition case identifies who may
write and why.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Assume two nodes always decide safely
during partition.

### DR-10 --- Global SLO definition and regional guardrails

**Scenario and constraints:** Skewed traffic, low-volume region with
severe errors and possible missing telemetry.

**Expected design artifacts:** SLI contract, formulas, dashboard and
alert plan.

**Trade-offs to discuss:** Eligibility, numerator/denominator,
ratio-of-sums, no-data semantics and burn windows.

**Minimum acceptance criteria:** Worked calculation, regional views and
missing-data alert included.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Average regional percentages and show only
global green.

### DR-11 --- Fleet observability architecture and hub failure

**Scenario and constraints:** Two local kind clusters, 8 GB RAM, no paid
SaaS and local alert authority required.

**Expected design artifacts:** Staged architecture, identity contract
and hub-down test plan.

**Trade-offs to discuss:** Multi-datasource versus
federation/remote-write, cost, cardinality, privacy and local alerts.

**Minimum acceptance criteria:** Staged profiles, unique identity
labels, independent local alert path and fidelity caveat.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Install every component at once and make
hub sole alert authority.

### DR-12 --- Policy rollout across a heterogeneous fleet

**Scenario and constraints:** Two policy-engine versions and one unknown
capability.

**Expected design artifacts:** Compatibility matrix, rings, report
contract and rollback plan.

**Trade-offs to discuss:** Audit/warn/enforce, API compatibility,
freshness, denial rate and bypass alerts.

**Minimum acceptance criteria:** One engine selected; unknown
compatibility blocks enforce; observed mode checked per cluster.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Assume same Git revision means same
behavior.

### DR-13 --- Fleet RBAC, credential inventory and hub-compromise governance

**Scenario and constraints:** Hub reaches many clusters; secret values
must never be printed.

**Expected design artifacts:** Role matrix, metadata-only inventory
schema and tabletop plan.

**Trade-offs to discuss:** Least privilege, scope, owner/expiry,
JIT/break-glass, audit, rotation and revocation.

**Minimum acceptance criteria:** No secret values; compromise response
stops fanout and independently verifies clusters.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Paste kubeconfig into report.

### DR-14 --- Region bring-up, seeding, readiness, decommission and fail-back

**Scenario and constraints:** Large dataset, bandwidth limit and old
region returns with divergence.

**Expected design artifacts:** Lifecycle state machine, data gates,
traffic plan and decommission checklist.

**Trade-offs to discuss:** Seed throttling, lag, parity, ownership,
credentials, traffic drain and reconciliation.

**Minimum acceptance criteria:** No deletion before
ownership/data/traffic checks; failback separately gated.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Return traffic as soon as old region is
reachable.

### DR-15 --- Multi-cloud/hybrid governance without assuming uniformity

**Scenario and constraints:** Provider-specific APIs/network/policy
capabilities and a shared fleet scorecard.

**Expected design artifacts:** Capability matrix and exception workflow.

**Trade-offs to discuss:** Identity normalization, provider metadata,
unsupported controls, residency and adapters.

**Minimum acceptance criteria:** UNKNOWN is not PASS; differences
retained; exceptions have owner/scope/expiry.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Erase provider differences in a generic
abstraction.

### DR-16 --- Cost of regions, standby capacity, telemetry retention and transfer

**Scenario and constraints:** Limited budget, standby surge, retention
and cross-region transfer.

**Expected design artifacts:** Transparent cost model with sensitivity
scenarios.

**Trade-offs to discuss:** Standby, storage/retention, transfer,
cardinality, staffing and SLO value.

**Minimum acceptance criteria:** Assumptions/uncertainty explicit; no
fabricated prices; hard safety constraints preserved.

**Scoring rubric:** correctness/completeness (0--4); trade-off reasoning
(0--4); safety/blast-radius control (0--4); evidence/verification
(0--4); operational feasibility/ownership/rollback (0--4).

**Common failure patterns:** Compare only compute cost or treat local
bytes as a cloud bill.

## Glossary

-   **ADR:** Architecture Decision Record: context, options, decision,
    trade-offs and review triggers.
-   **CAPI:** Cluster API; provider/API behavior is version-dependent
    and `[VERIFY]`.
-   **CIDR:** Classless Inter-Domain Routing network range.
-   **DNS:** Domain Name System; resolver/client behavior affects
    observed failover.
-   **Fencing:** Mechanism preventing an old/competing writer from
    retaining authority after promotion.
-   **GitOps:** Reconciliation of version-controlled desired state with
    observed state.
-   **mTLS:** Mutual Transport Layer Security; peers authenticate each
    other.
-   **N+1:** Capacity sufficient to tolerate loss of one defined failure
    domain at target load.
-   **RPO:** Recovery Point Objective; acceptable data-loss boundary,
    not automatically equal to lag percentile.
-   **RTA/RPA:** Roadmap terms for recovery-time/recovery-point
    objectives; use the roadmap's definitions.
-   **SLO/SLI:** Service-Level Objective / Service-Level Indicator.
-   **WAL:** Write-Ahead Log; retention may grow when a replication
    consumer lags.
-   **kind:** Kubernetes-in-Docker local cluster tool; clusters share
    host failure domains.
-   **UNKNOWN/UNREACHABLE:** States that do not establish
    health/conformance and must not silently count as PASS.
-   **p99:** 99th percentile of a defined sample/window, not a maximum
    or future guarantee.
-   **Quarantine:** State blocking rollout eligibility until required
    evidence and approval clear it.
-   **Ratio-of-sums:** Sum of good events divided by sum of eligible
    events for an event-weighted global ratio.

## Coverage matrix and verification notes

  -----------------------------------------------------------------------
  Curriculum domain                   Coverage
  ----------------------------------- -----------------------------------
  Unit 1: Multi-Cluster Topologies    U1-... (19 scored questions);
  and When to Split Clusters          cross-unit scenarios; related
                                      whiteboard prompt(s).

  Unit 2: Fleet Management and        U2-... (19 scored questions);
  Cluster Lifecycle with Cluster API  cross-unit scenarios; related
                                      whiteboard prompt(s).

  Unit 3: Multi-Cluster GitOps and    U3-... (19 scored questions);
  Config Propagation                  cross-unit scenarios; related
                                      whiteboard prompt(s).

  Unit 4: Cross-Cluster Service       U4-... (19 scored questions);
  Discovery and Traffic Routing       cross-unit scenarios; related
                                      whiteboard prompt(s).

  Unit 5: Global Load Balancing and   U5-... (19 scored questions);
  DNS Failover                        cross-unit scenarios; related
                                      whiteboard prompt(s).

  Unit 6: Active-Active vs            U6-... (19 scored questions);
  Active-Passive Regional Designs     cross-unit scenarios; related
                                      whiteboard prompt(s).

  Unit 7: Data Replication and        U7-... (19 scored questions);
  Consistency Across Regions          cross-unit scenarios; related
                                      whiteboard prompt(s).

  Unit 8: Multi-Cluster Observability U8-... (19 scored questions);
  and Policy Governance               cross-unit scenarios; related
                                      whiteboard prompt(s).

  Cross-unit integration themes       X-L3-INT-01--X-L4-INT-40; includes
                                      context, CIDR, fan-out, failover
                                      timing, capacity, consistency, RPO,
                                      SLO aggregation, conformance, hub
                                      failure and capstone ordering.

  Design reviews                      DR-01--DR-16.
  -----------------------------------------------------------------------

**Source limitations:** the exact `Roadmap_ptree.md` was not available
under that filename; a related `Roadmap(20261029-114814).md` tree
excerpt was read. The Unit 9 prompt was read, but the primary M14
curriculum prompt and final Unit 1--8 lesson files were not
independently verified line-by-line. Check final lesson terminology
before using this as a formal examination.

**Live verification:** no official documentation was consulted live.
CAPI/provider APIs, ApplicationSet selector/prune semantics, network
interconnect/mesh features, DNS/global-routing behavior, database
replication queries/settings, Prometheus/Alertmanager syntax,
policy-engine behavior, and Kubernetes support windows remain
`[VERIFY]`. Questions test principles instead of unverified flags.

Canonical entry points for later verification (not claimed reviewed):

-   [Kubernetes documentation](https://kubernetes.io/docs/)
-   [Cluster API documentation](https://cluster-api.sigs.k8s.io/)
-   [Argo CD documentation](https://argo-cd.readthedocs.io/)
-   [Prometheus documentation](https://prometheus.io/docs/)
-   [Grafana documentation](https://grafana.com/docs/grafana/latest/)
-   [OpenTelemetry documentation](https://opentelemetry.io/docs/)
-   [PostgreSQL documentation](https://www.postgresql.org/docs/)
-   [kind documentation](https://kind.sigs.k8s.io/)
-   [Kyverno documentation](https://kyverno.io/docs/)

No commands, tests, DNS changes, cluster operations, failovers or policy
mutations were executed to create this bank. All artifacts are
synthetic; local results from future learner labs must be labelled
`[LOCAL LAB MEASUREMENT]` and not generalized to geographic production
behavior.

## Roadmap Alignment and Authenticity Audit

  ---------------------------------------------------------------------------------------
  Requirement              Status (PASS /    Evidence          Notes / follow-up
                           PARTIAL /         section(s)        
                           BLOCKED)                            
  ------------------------ ----------------- ----------------- --------------------------
  Exact target             PASS              Metadata          Standalone
  filename/path; only one                                      `practice-questions.md`;
  artifact                                                     no repository files
                                                               modified.

  At least 19 scored       PASS              Unit 1--8         19 each; 152 total.
  questions per Unit 1--8                                      

  At least 40 distinct     PASS              Cross-unit        40 unique IDs; no double
  scored cross-unit                          integration       counting.
  scenarios                                  scenarios         

  At least 192 scored      PASS              Unit 1--8 and     152 + 40 = 192.
  questions overall                          cross-unit        

  Exactly 16 separate      PASS              Design-review     DR-01--DR-16, each with
  design-review prompts                      whiteboard        constraints, artifacts,
                                             prompts           trade-offs, acceptance and
                                                               scoring rubric.

  Required unit            PASS              Unit 1--8         3 short answer, 3 MCQ, 3
  question-type mix                                            artifacts, 3 config
                                                               reviews, 1 incident, 1
                                                               design, 5 extras each.

  Exactly four MCQ options PASS              Unit 1--8 MCQs    One best answer and
  and explanations for all                                     distractor rationale
  distractors                                                  included.

  Three defects,           PASS              Unit 1--8 CFG     Three specific defects per
  corrections and failure                    questions         review.
  consequences per config                                      
  review                                                       

  All required             PARTIAL           Unit questions;   Includes capacity, DNS
  calculations and                           cross-unit        failover, RPO/lag,
  technical details fully                    scenarios         consistency and SLO
  verified                                                     arithmetic; exact
                                                               lesson-level alignment not
                                                               independently verified.

  Incident sequence and    PASS              Unit incidents    Safe first action,
  safety boundaries                          and cross-unit    localization, mitigation,
                                             scenarios         per-cluster verification,
                                                               communication and
                                                               prevention included.

  All 40 roadmap           PASS              Cross-unit        40 unique scenarios cover
  integration themes                         integration       supplied theme list.
  represented                                scenarios         

  Exact Roadmap_ptree.md   PARTIAL           Scope and source  Related Roadmap excerpt
  inspected                                  notes             read; exact named file
                                                               unavailable.

  Primary M14 prompt and   PARTIAL           Scope and         Unit 9 prompt read;
  every final lesson                         verification      primary curriculum and
  verified in full                           notes             lesson files not fully
                                                               independently checked.

  Live official docs       BLOCKED           Verification      Not consulted live;
  verified                                   notes             version-sensitive facts
                                                               marked `[VERIFY]`.

  Commands/tests/cluster   BLOCKED           Verification      None executed; no success
  operations executed                        notes             claims.

  No other repository file PASS              Metadata and      Only the standalone
  modified                                   audit             artifact was created.
  ---------------------------------------------------------------------------------------

**Final trust statement:** this bank is authored to the supplied Unit 9
assessment prompt. Structural counts are checked below, but the bank has
not been independently validated against every final lesson file or
current product version. It is not a verified production exam, and no
command or test execution is claimed.
