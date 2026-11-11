# M16 Practice Questions — Platform Engineering and Internal Developer Platforms

**Module:** M16 — Platform Engineering and Internal Developer Platforms  
**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Scope:** Units 1–9 plus cross-unit integration  
**Learner level:** L1–L4  
**Estimated completion time:** 35–50 hours, including design-review prompts and targeted remediation. This is an estimate, not a measured duration.  
**Last reviewed:** 2026-11-04 (authoring and editorial-audit date; not a claim that external documentation was checked)  
**Tool baseline / verification status:** Tool-neutral question bank. Version-sensitive Backstage, Crossplane, Copier/Cookiecutter, Kubernetes, Argo CD, Kyverno/VAP, KEDA, OpenCost and related API/CLI details are marked `[VERIFY]`; no current tool versions or live documentation checks are asserted.  
**Data fidelity:** All teams, incidents, usage tables, surveys, event streams and organizational scenarios in this bank are `SYNTHETIC` unless explicitly labelled `[LOCAL MEASUREMENT]`. Local laptop timings are n=1 evidence only.

## Purpose and how to use this question bank

This question bank assesses the nine M16 teaching units and their integration. It is designed for self-study, technical interviews, architecture reviews, incident exercises and platform design discussions. Answers appear immediately after each question so that the bank can teach the reasoning as well as test recall.

Use the bank in three passes:

1. **Closed-book attempt:** answer the prompt before reading the model answer. For artifact questions, annotate the supplied artifact and state what it proves, what it does not prove, and what evidence is missing.
2. **Reasoning review:** compare your answer with the model answer, distractor analysis and scoring guidance. Record the exact misconception, not just the missed score.
3. **Evidence-based remediation:** revisit the linked lesson, redo the relevant artifact or lab, and produce a new piece of evidence. Repeating an answer from memory is not practical remediation.

The bank is not a substitute for running the M16 labs. A correct answer demonstrates knowledge or reasoning; it does not prove that a template, portal, API, controller, isolation policy or cleanup workflow works in your installed environment.

### Learner and lab fidelity

The assumed learner completed Stages 0–2D and Stage 2E M01–M15. M16 integrates those mechanisms; it does not re-teach them as separate modules. The guaranteed path is **Plat-Core**: local files, Git where available, Python standard library, synthetic fixtures, deterministic checks and a thin static portal. **Plat+Control** adds a disposable `kind` cluster, Argo CD, Crossplane/cloud-free providers and one policy engine only where a lab requires them. **Plat+Portal** runs Backstage alone after Node/yarn/memory preflight; stop other heavy components first.

The planning machine is approximately 4 CPU, 8 GB RAM and 30 GB disk. It is not a promise that all components fit simultaneously. Measure the actual machine and use the source lesson's stack sequencing. No cloud account, paid service, SaaS SCM, real credential, production access or real developer data is required.

**Evidence labels:** `[SYNTHETIC]` means invented teaching data; `[LOCAL MEASUREMENT]` means a learner's own laptop observation; `[ASSUMPTION]` means an explicit design assumption; `[ILLUSTRATIVE]` means a hypothetical policy/value; `[VERIFY]` means check the exact version against official documentation; `[VERSION-SENSITIVE]` means behavior may differ by release; **representative expected output** is not execution evidence.

### M16 unit map

| Unit | Topic | Lesson |
|---:|---|---|
| 1 | Platform engineering principles and platform as a product | [01-platform-engineering-principles-and-platform-as-a-product.md](01-platform-engineering-principles-and-platform-as-a-product.md) |
| 2 | Golden paths, templates, and paved roads | [02-golden-paths-templates-and-paved-roads.md](02-golden-paths-templates-and-paved-roads.md) |
| 3 | Self-service infrastructure and environment provisioning | [03-self-service-infrastructure-and-environment-provisioning.md](03-self-service-infrastructure-and-environment-provisioning.md) |
| 4 | Developer portals and the Backstage service catalog | [04-developer-portals-and-backstage-service-catalog.md](04-developer-portals-and-backstage-service-catalog.md) |
| 5 | Scaffolding and software templates | [05-scaffolding-and-software-templates.md](05-scaffolding-and-software-templates.md) |
| 6 | Platform APIs with Crossplane compositions | [06-platform-apis-with-crossplane-compositions.md](06-platform-apis-with-crossplane-compositions.md) |
| 7 | Multi-tenancy, isolation, and tenant onboarding | [07-multi-tenancy-isolation-and-tenant-onboarding.md](07-multi-tenancy-isolation-and-tenant-onboarding.md) |
| 8 | Platform SLOs, adoption metrics, and developer experience | [08-platform-slos-adoption-metrics-and-developer-experience.md](08-platform-slos-adoption-metrics-and-developer-experience.md) |
| 9 | Platform governance, deprecation, and versioning | [09-platform-governance-deprecation-and-versioning.md](09-platform-governance-deprecation-and-versioning.md) |
| Capstone context | Self-Service Data and ML Platform Portal | [Projects/01-self-service-data-and-ml-platform-portal.md](Projects/01-self-service-data-and-ml-platform-portal.md) |

The capstone is an integration context, not a tenth teaching unit. The roadmap places the M16 capstone under `Projects/`; M17 remains the separate Production DevOps Integrated Capstone.

## Question taxonomy, levels and scoring

### Four teaching levels

| Level | Meaning | Expected performance |
|---|---|---|
| **L1 — Beginner / Foundations** | Explain terms and read basic artifacts. | Define concepts precisely, distinguish adjacent terms and identify the developer-facing purpose. |
| **L2 — Intermediate / Working Practice** | Build and test a correct local capability. | Interpret schemas, requests, templates, catalog entries, policies and status; identify normal failure layers. |
| **L3 — Advanced / Production Engineering** | Design a platform capability under constraints. | Defend trade-offs across security, reliability, cost, cognitive load, ownership, testing and upgradeability. |
| **L4 — Expert / Operating Under Failure** | Operate and evolve the platform under real constraints. | Contain incidents, bound blast radius, use evidence, govern changes, communicate and prevent recurrence. |

### Required question distribution

Each of Units 1–9 contains exactly 14 questions:

| Type per unit | Count | IDs |
|---|---:|---|
| Conceptual short answer | 3 | `U01-Q01`–`U01-Q03` (same pattern for U02–U09) |
| Multiple choice (four options) | 3 | `U01-Q04`–`U01-Q06` (same pattern for U02–U09) |
| Artifact interpretation | 3 | `U01-Q07`–`U01-Q09` (same pattern for U02–U09) |
| Artifact review (at least three defects) | 3 | `U01-Q10`–`U01-Q12` (same pattern for U02–U09) |
| Incident / diagnosis | 1 | `U01-Q13` (same pattern for U02–U09) |
| Design | 1 | `U01-Q14` (same pattern for U02–U09) |
| **Unit total** | **14** | **126** |

Additional required assessment:

- **40 cross-unit integration scenarios:** `XU-Q01`–`XU-Q40`.
- **26 additional synthesis questions:** `SYN-Q01`–`SYN-Q26`.
- **16 design-review / whiteboard prompts:** `DR-01`–`DR-16`. These are additional design assessments and do not replace the 185 numbered questions.

**Unique numbered-question total: 192** (126 unit questions + 40 cross-unit scenarios + 26 synthesis questions).

### Per-question answer format

Every numbered question states its scope, level, type, objective, suggested time and complete prompt. Each has a model answer, reasoning, common wrong answers and scoring guidance. MCQs have exactly four options, one best answer under stated assumptions, and an explanation for every distractor. Artifact questions contain a self-contained synthetic artifact or excerpt in the prompt; the learner must not need a live cluster or hidden file.

For artifact review, identify at least three defects, explain consequences and propose specific corrections/tests. For incident questions, use: symptom/scope → first safe action → evidence preservation → failure-layer localization → blast-radius bound → mitigation → communication → recovery verification → blameless cause/contributors → prevention. For design questions, state assumptions, alternatives, trade-offs, safety, operations, cost, migration, evidence and non-goals.

### Scoring method

Use each question's local scoring guidance. Calculate a percentage as:

`points earned ÷ points available × 100`

Do not compare raw scores between different question subsets unless their available points are normalized. Record a score by unit, question type and L1–L4 level. Cross-unit scenarios and design-review prompts should be scored separately from the per-unit knowledge check.



---

## Units 1–9 — prescribed per-unit question sets

Each unit below has the exact 14-question distribution specified in the prompt.

## Unit 1 — Platform engineering principles and platform as a product

**Lesson:** [`01-platform-engineering-principles-and-platform-as-a-product.md`](01-platform-engineering-principles-and-platform-as-a-product.md)  
**Coverage:** definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns

### U01-Q01 — Short Answer
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L1
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 6 minutes

**Prompt**
Define platform engineering, an internal developer platform (IDP), and an internal developer portal. Explain how they relate without treating them as synonyms.

**Model answer**
Platform engineering is the discipline of designing and operating shared toolchains, workflows and capabilities that reduce friction for product teams. The IDP is the integrated set of capabilities and interfaces produced by that work. A developer portal is one possible user interface/catalog front door to the platform; it is neither the whole platform nor proof that the underlying services work.

**Reasoning**
The distinction separates discipline, product/system and interface. A portal can be unavailable while APIs and Git workflows continue; a portal can also look polished while provisioning is broken.

**Common wrong answers / tempting mistakes**
Calling the portal the platform; calling an operations ticket queue an IDP; defining platform engineering as merely operating Kubernetes.

**Scoring guidance**
Score 1 point for each precise definition, 1 for the relationship, and 1 concrete example (5 total).


### U01-Q02 — Short Answer
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 6 minutes

**Prompt**
Why is adoption by voluntary choice an important product signal, and when may a baseline still be mandated?

**Model answer**
Adoption indicates that a supported path solves a real developer problem at acceptable friction. A mandate can be justified for a safety-critical security or compliance baseline, but it must include enablement, migration help, clear exceptions where appropriate, and an evidence-based reason. Mandating every product preference creates a golden cage and hides product failure.

**Reasoning**
The platform's value proposition should earn use. Safety controls can be mandatory independently of optional convenience features; those are different decisions.

**Common wrong answers / tempting mistakes**
Assuming adoption must always be voluntary even for critical controls; assuming leadership authority makes every platform feature valuable; treating usage count alone as outcome evidence.

**Scoring guidance**
Score: product-value rationale 2; justified mandate boundary 2; enablement and measurement 1.


### U01-Q03 — Short Answer
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 6 minutes

**Prompt**
Design a manual baseline measurement for shipping a new data/ML service. What must be recorded, and what may the result legitimately claim?

**Model answer**
Define a repeatable start/end boundary, service archetype, machine/profile, prerequisites, steps, elapsed and active time, waits, rework, failures, security/observability checks, and evidence. Repeat carefully if useful, preserve raw timings, and label a single learner run n=1/local. It can describe that learner's local workflow under stated conditions; it cannot estimate population productivity or claim causal platform impact.

**Reasoning**
A before/after comparison is meaningful only when tasks and boundaries are comparable. The manual baseline is a local reference reused by the capstone, not an industry benchmark.

**Common wrong answers / tempting mistakes**
Timing only the template command; counting setup omissions as platform savings; generalizing one laptop run to all developers.

**Scoring guidance**
Score: boundaries and context 2; complete measurement fields 2; fidelity caveat 1.


### U01-Q04 — Mcq
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L2
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform engineering principles and platform as a product principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A small organization has six data engineers and no evidence that a custom portal is needed. Which first move best follows the thinnest-viable-platform principle?

**Options**
A. Build a custom portal and framework before validating demand.
B. Start with documented defaults, a maintained template, shared CI checks and clear ownership/support.
C. Rename the existing operations ticket queue and keep manual fulfillment.
D. Buy the broadest IDP available because feature breadth proves value.

**Model answer**
**Correct option: B.** A thin set of documented defaults, a maintained template, shared CI checks and a trustworthy owner/runbook catalog can remove friction without creating a portal operations burden.

**Reasoning**
A is attractive because a custom framework appears differentiated, but it creates maintenance before validating demand. C renames the bottleneck rather than removing it. D is a tool-first solution with an operating cost that the scenario has not justified.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: premature bespoke build. C: ticket queue is not self-service. D: a portal is an interface, not the platform and not automatically valuable.

**Scoring guidance**
Score: 1 for B; 1 for identifying the premature-build risk; 1 for explaining why the thin slice tests demand (3).


### U01-Q05 — Mcq
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L3
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform engineering principles and platform as a product principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
Synthetic interviews show frequent complaints about missing runbooks. What is the strongest next step?

**Options**
A. Publish the synthetic frequencies as actual organizational research.
B. Mandate a portal immediately because runbooks are mentioned.
C. Map the affected journey, validate with real users when available, and test a small ownership/runbook improvement.
D. Discard the synthetic exercise because synthetic data cannot teach analysis.

**Model answer**
**Correct option: C.** Code the evidence with frequency and severity, validate the pattern with real users when available, map the affected journey, and test a small documentation/ownership improvement.

**Reasoning**
A mistakes synthetic records for real research. B jumps from a signal to a costly framework without checking the root cause. D mandates a UI rather than addressing runbook ownership and freshness.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: synthetic data teaches analysis only. B: solution before diagnosis. D: portal presence does not make operational data trustworthy.

**Scoring guidance**
Score: correct option 1; evidence and validation rationale 2.


### U01-Q06 — Mcq
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L4
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform engineering principles and platform as a product principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
Which statement best describes a build/adopt/buy decision for a shared platform capability?

**Options**
A. Compare user fit, differentiation, maintenance burden, skills, security, ecosystem/exit risk and operating ownership; adopt when an adequate option fits.
B. Build every shared capability internally to maximize customization.
C. Buy a managed tool and assume accountability for security and integration transfers to the vendor.
D. Choose the most popular tool without checking fit, ownership or exit cost.

**Model answer**
**Correct option: A.** Start by comparing user fit, differentiation, total maintenance burden, skills, security, ecosystem/exit risk and operational ownership. A reasonable default is to adopt an adequate existing capability and build the integration, policy and defaults that make it fit.

**Reasoning**
B overweights customization and ignores long-term ownership. C assumes managed service eliminates security and integration responsibilities. D treats popularity as sufficient evidence and ignores fit and exit costs.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
B: custom code increases support burden. C: buying transfers some operations, not accountability. D: adoption signals are context-dependent.

**Scoring guidance**
Score: correct choice 1; at least three decision criteria 2.


### U01-Q07 — Artifact Interpretation
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L2
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Friction coding output: `repo bootstrap` frequency 8, severity 3; `missing ownership/runbook` frequency 5, severity 5; `slow manual environment request` frequency 4, severity 4. Assume priority score = frequency × severity for this exercise. Which theme ranks first, and what does the ranking not prove?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Friction coding output: `repo bootstrap` frequency 8, severity 3; `missing ownership/runbook` frequency 5, severity 5; `slow manual environment request` frequency 4, severity 4. Assume priority score = frequency × severity for this exercise. Which theme ranks first, and what does the ranking not prove?
```

**Model answer**
Scores: bootstrap 24; ownership/runbook 25; manual environment 16. Ownership/runbook ranks first by one point. This is a prioritization aid under the stated synthetic coding and scoring assumption, not a statistically valid estimate of real-user prevalence or proof that a portal is the remedy.

**Reasoning**
The calculation follows the specified formula. The narrow gap should not be over-interpreted; severity coding and sample construction are assumptions.

**Common wrong answers / tempting mistakes**
Choosing bootstrap because it has the highest frequency only; calling 25 a real-world impact score; assuming the highest score dictates an automatic build decision.

**Scoring guidance**
Score: calculations 2; interpretation/limitations 2; next validation step 1.


### U01-Q08 — Artifact Interpretation
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Capability map: image hardening = `integrated`; CI workflow = `provided`; database schema design = `left to product team`; secrets reference = `integrated`; developer docs = `provided`. Explain one responsibility boundary and identify a missing field needed before this map can govern support.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Capability map: image hardening = `integrated`; CI workflow = `provided`; database schema design = `left to product team`; secrets reference = `integrated`; developer docs = `provided`. Explain one responsibility boundary and identify a missing field needed before this map can govern support.
```

**Model answer**
The map distinguishes who supplies a capability from who consumes or integrates it. For example, the platform provides a reusable CI workflow, while the product team owns application tests and service behavior. Add a named accountable owner and support level (and ideally evidence/source and lifecycle) before using the map for routing or promises.

**Reasoning**
A capability map is useful only when responsibilities are operationally actionable. A label without owner/support boundary creates ambiguity during incidents.

**Common wrong answers / tempting mistakes**
Treating integrated as full ownership of the product service; treating left-to-team as exempt from mandatory security controls; assuming the map itself proves delivery.

**Scoring guidance**
Score: correct boundary 2; missing owner/support metadata 2; limitation 1.


### U01-Q09 — Artifact Interpretation
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 8 minutes

**Prompt**
[LOCAL MEASUREMENT] A learner records 17 steps and 94 minutes for a local API-service manual baseline. After using a thin path, the same learner records 11 steps and 61 minutes. Calculate absolute and percentage time difference, then state the correct claim.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[LOCAL MEASUREMENT] A learner records 17 steps and 94 minutes for a local API-service manual baseline. After using a thin path, the same learner records 11 steps and 61 minutes. Calculate absolute and percentage time difference, then state the correct claim.
```

**Model answer**
Difference = 94 − 61 = 33 minutes. Relative reduction = 33/94 × 100 ≈ 35.1%. Correct claim: in this learner's recorded local run, under the stated task and machine conditions, elapsed time was 33 minutes (about 35.1%) lower. It is not a population estimate or causal proof without controlled repeated comparison.

**Reasoning**
The denominator is the baseline 94 minutes. The comparison is useful for local iteration but remains n=1 and may contain learning/order effects.

**Common wrong answers / tempting mistakes**
Using 61 as denominator; saying productivity improved by 35% for the organization; ignoring whether the task and start/end conditions matched.

**Scoring guidance**
Score: arithmetic 2; denominator 1; honest interpretation 2.


### U01-Q10 — Artifact Review
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L2
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this PRD and find at least three defects: `Goal: launch a company-wide Backstage portal. Users: all engineers. Success: 100% portal logins. Owner: Platform Team. Support: TBD. SLO: TBD. First release: catalog, scaffolder, cost dashboard, deployment controls, notebook service, and GPU scheduler. No explicit non-goals.`

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this PRD and find at least three defects: `Goal: launch a company-wide Backstage portal. Users: all engineers. Success: 100% portal logins. Owner: Platform Team. Support: TBD. SLO: TBD. First release: catalog, scaffolder, cost dashboard, deployment controls, notebook service, and GPU scheduler. No explicit non-goals.`
```

**Model answer**
Intended defects: (1) no evidence-backed user problem/personas/JTBD; (2) login rate is an output/vanity metric, not a developer outcome; (3) no owner individual/team boundary or support model; (4) no SLO/fallback; (5) over-broad first release violates TVP; (6) no non-goals or adoption/feedback plan; (7) no safety, privacy, capacity, cost or exit assumptions. Fix with a thin validated slice and measurable journey outcome.

**Reasoning**
The PRD jumps to a portal and bundles many capabilities before showing demand. A production-ready PRD states the user task, baseline friction, scope, owner, reliability, support and what will not be built.

**Common wrong answers / tempting mistakes**
Counting only the absence of a logo or UI mock; accepting login count as success; assuming all capabilities belong in the first release.

**Scoring guidance**
Score 1 per distinct valid defect up to 4; 1 point each for consequence and concrete correction (10 max).


### U01-Q11 — Artifact Review
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L3
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this hypothetical ROI worksheet: `Hours saved = 2 hours per developer per week; users = 500; annual savings = hours × users × 52; platform cost = salary of one engineer; ROI = 900%.` No source or sensitivity table is attached.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this hypothetical ROI worksheet: `Hours saved = 2 hours per developer per week; users = 500; annual savings = hours × users × 52; platform cost = salary of one engineer; ROI = 900%.` No source or sensitivity table is attached.
```

**Model answer**
Defects: (1) hours saved are unsupported/illustrative but presented as measured; (2) user count and eligible population are undefined; (3) gross hours are treated as cash savings without realization/loaded-cost assumptions; (4) platform cost omits engineering, infrastructure, support, migration and opportunity cost; (5) incidents/duplication may be double-counted; (6) no low/base/high sensitivity or assumption register; (7) precise ROI is false confidence. Mark inputs `[ILLUSTRATIVE]`, separate capacity released from cash savings, include full cost categories and sensitivity, and state what is unknowable.

**Reasoning**
A formula cannot make weak inputs factual. A decision model supports discussion only when each input has provenance, uncertainty and a clear unit.

**Common wrong answers / tempting mistakes**
Accepting the 900% as evidence; treating developer time as automatically cashable; omitting recurring maintenance and migration cost.

**Scoring guidance**
Score: identify 3+ defects 4; quantify consequences 2; redesign model and caveat 4.


### U01-Q12 — Artifact Review
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L4
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this platform-team charter: `Platform team owns all deployment decisions. Product teams submit requests in Jira. Security approves every repo. No escalation rota is defined. Platform has no on-call because it is an internal tool. All teams must use one framework. No user feedback is collected.`

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this platform-team charter: `Platform team owns all deployment decisions. Product teams submit requests in Jira. Security approves every repo. No escalation rota is defined. Platform has no on-call because it is an internal tool. All teams must use one framework. No user feedback is collected.`
```

**Model answer**
Defects: (1) ticket-centric operating model contradicts self-service/product intent; (2) centralized deployment approval creates bottleneck; (3) blanket security approval duplicates controls without risk tiering; (4) no platform on-call despite shared dependency; (5) no product-team ownership or responsibility boundary; (6) one framework creates a golden cage; (7) no feedback/intake/prioritization; (8) no support tiers or escalation. Replace with platform-owned reusable guardrails, clear service-team responsibility, risk-based approvals, support/on-call, office hours, feedback and supported escape hatches.

**Reasoning**
The charter confuses platform ownership of shared capability with ownership of every product deployment. Platform reliability and product autonomy both need explicit boundaries.

**Common wrong answers / tempting mistakes**
Assuming the platform team owns every workload; assuming an internal system needs no SLO/on-call; assuming mandatory uniformity is safer.

**Scoring guidance**
Score: 1 per defect up to 4; 1 per consequence/fix pair up to 6.


### U01-Q13 — Incident
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L4
- **Question type:** incident
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC INCIDENT] A bespoke internal framework launched to one founding team. Three months later, other teams still use their own pipelines; support requests rise; the platform team plans to force migration. Diagnose using the incident sequence.

**Model answer**
First preserve evidence: adoption by team/archetype, task-level friction, support themes, reliability, migration blockers and current service dependencies. Do not force migration yet. Interview/observe representative users (real users if available; synthetic case data only for the exercise), compare the framework's promised job with actual workflows, segment unmet needs, and identify whether the root cause is poor fit, missing docs, reliability, support or migration cost. Mitigate by narrowing scope, fixing the highest-friction defect, offering a supported integration/escape route and design partners. Communicate a transparent roadmap; define outcome measures and a revisit date. Prevent with discovery gates and sunset criteria for unused capabilities.

**Reasoning**
Low adoption is a product signal, not proof that users are resistant. Mandate would suppress the signal and may increase forks and hidden risk.

**Common wrong answers / tempting mistakes**
Immediate forced migration; adding features without discovery; blaming teams; measuring developer-level usage to punish non-adopters.

**Scoring guidance**
Score: symptom/scope 1; first safe action/evidence 2; root-cause hypotheses 2; mitigation/comms 2; prevention/measurement 3.


### U01-Q14 — Design
- **Scope:** Unit 1 — Platform engineering principles and platform as a product; definitions and boundaries; platform-as-product; manual baseline; synthetic discovery; personas/JTBD; problem statements and prioritization; TVP/MVP; build/adopt/buy; platform team and support; capability map; interfaces and escape hatches; cognitive load; platform economics; maturity, trust, ethics and anti-patterns
- **Level:** L3
- **Question type:** design
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform engineering principles and platform as a product topic.
- **Suggested time:** 25 minutes

**Prompt**
Design a thinnest viable first release for a data/ML organization with API, batch and model-serving teams. State the user task, included capabilities, exclusions, support boundary, success measures and build/adopt/buy decisions.

**Model answer**
Strong outline: select one painful end-to-end job based on discovery; deliver one maintained service skeleton with archetype-specific extension points, hardened image reference, reusable CI caller, policy checks, ownership/runbook/SLO/catalog metadata, documented deployment path and feedback/support. Provide common interface via Git/PR and documented CLI/API only if justified. Keep cluster vending, full portal, custom orchestrator, GPU scheduler and broad notebook platform out until evidence supports them. Reuse existing CI, registry, GitOps, policy and observability mechanisms; build only integration/glue/defaults. Define owner, support tier, SLO, escape hatch, security negative tests, local manual-baseline comparison and adoption research plan. Treat all local results as n=1.

**Reasoning**
The first slice is a walking skeleton: one supported path from repository to verified deployment and operation, not a collection of disconnected tools.

**Common wrong answers / tempting mistakes**
Starting with a broad portal; copying every M01–M15 tool into a new platform; no explicit non-goals; success measured only by portal logins.

**Scoring guidance**
Score 0–2 each: user/problem evidence, thin scope/non-goals, M01–M15 reuse, support/ownership, security/reliability, measurable outcome and fidelity caveat (14).


---

## Unit 2 — Golden paths, templates, and paved roads

**Lesson:** [`02-golden-paths-templates-and-paved-roads.md`](02-golden-paths-templates-and-paved-roads.md)  
**Coverage:** golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius

### U02-Q01 — Short Answer
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L1
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 6 minutes

**Prompt**
Distinguish a golden path, a template, and a golden cage.

**Model answer**
A golden path is a documented, owned, supported end-to-end route for a common developer task. A template is one artifact that starts a repository on that route. A golden cage removes legitimate alternatives, blocks escape hatches and feedback, and pushes teams toward forks or bypasses.

**Reasoning**
The path includes validation, delivery, operation and support; the template only generates starting files.

**Common wrong answers / tempting mistakes**
Equating the template with the entire path; treating any standardized default as a cage; assuming a path must be mandatory.

**Scoring guidance**
Score: three definitions 3; relation 1; example 1.


### U02-Q02 — Short Answer
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 6 minutes

**Prompt**
Explain the default → option → escape model and what guardrails apply at each level.

**Model answer**
Default is the fully supported, easiest path. Option is a documented, tested variation exposed through bounded parameters or values. Escape is a legitimate alternative with explicit support status (unsupported/best-effort where appropriate), ownership and review; mandatory security and policy guardrails still apply. The escape hatch is not a bypass of safety controls.

**Reasoning**
The model balances standardization with autonomy. Support boundaries must be clear before an incident.

**Common wrong answers / tempting mistakes**
Treating escape as policy bypass; exposing arbitrary configuration as a supported option; failing to test variants.

**Scoring guidance**
Score: three levels 3; guardrail/support distinction 2.


### U02-Q03 — Short Answer
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 6 minutes

**Prompt**
Why should API, batch/ETL, streaming, model-serving and notebook paths share a core but retain archetype-specific contracts?

**Model answer**
They share ownership, secure image, CI, supply-chain, observability, cost labels, documentation and support conventions. Their runtime behavior differs: batch needs scheduling/freshness/idempotency; streaming needs lag/backpressure; model serving needs model digest and rollout; notebooks need ephemeral quotas/idle lifecycle; APIs need request/latency behavior. Shared core reduces duplication without forcing irrelevant ceremony.

**Reasoning**
A single universal template tends to overfit one workload and burden the others.

**Common wrong answers / tempting mistakes**
Five entirely separate stacks with duplicated controls; one identical deployment shape for all workloads; assuming notebooks are long-lived services.

**Scoring guidance**
Score: shared core 2; three specific differences 2; trade-off 1.


### U02-Q04 — Mcq
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L2
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the golden paths, templates, and paved roads principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A repo passes template generation but contains a `:latest` base image and no resource requests. What is the strongest conformance decision?

**Options**
A. Treat successful template generation as proof that the repo conforms.
B. Pass because the developer says the unsafe defaults will be changed later.
C. Fail/block under the documented policy mode and report an actionable remediation.
D. Create a permanent broad exception because the template is widely used.

**Model answer**
**Correct option: C.** Fail or block according to the documented policy mode because generation success is not conformance. The scanner must inspect generated content and provide actionable rule/remediation messages; a planted unsafe default should be caught by a negative test.

**Reasoning**
A confuses rendering with safety. B relies on developer intent rather than enforceable policy. D hides a defect by changing the scanner instead of fixing the default.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: generation is not validation. B: a declared intention is not evidence. D: a broad exemption undermines conformance.

**Scoring guidance**
Score: correct option 1; generation-vs-conformance reasoning 2.


### U02-Q05 — Mcq
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L3
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the golden paths, templates, and paved roads principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
Which test best demonstrates that a required non-root default is actually enforced in the Core path?

**Options**
A. Plant a privileged/root setting and assert the policy suite fails with the expected actionable diagnostic.
B. Run only a positive test where a compliant template passes.
C. Check YAML syntax and assume semantic policy is covered.
D. Check that the policy file exists without executing a negative fixture.

**Model answer**
**Correct option: A.** Create a controlled template variant with a privileged/root setting and assert that the local validation/policy suite fails with the expected actionable diagnostic. This tests the rule rather than merely checking that a policy file exists.

**Reasoning**
B is a positive-path test only. C checks syntax, not policy semantics. D assumes a written policy is automatically executed.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
B: does not test denial. C: schema validity is not security policy. D: configuration presence is not enforcement evidence.

**Scoring guidance**
Score: correct option 1; negative-test reasoning 2.


### U02-Q06 — Mcq
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L4
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the golden paths, templates, and paved roads principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A model-serving template needs a different readiness and rollout contract from a batch pipeline. What is the best design?

**Options**
A. Duplicate every common control into a separate model-serving platform.
B. Force the batch pipeline's scheduling and freshness semantics onto model serving.
C. Remove archetype-specific settings so every workload has identical behavior.
D. Share common repo/security/ownership/observability contracts while adding model-digest, serving-readiness and rollout behavior.

**Model answer**
**Correct option: D.** Share common repository/security/ownership/observability contracts, but expose an archetype-specific model-serving layer with model digest verification, serving probes and rollout/rollback integration. Do not force batch semantics onto serving.

**Reasoning**
A duplicates common controls. B erases real workload differences. C creates a separate platform product for every archetype without need.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: duplication raises drift. B: batch and serving have different operational semantics. C: unnecessary fragmentation and maintenance.

**Scoring guidance**
Score: correct option 1; rationale 2.


### U02-Q07 — Artifact Interpretation
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L2
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Default register: `base image → M01 hardened image program → avoid mutable tag → policy rejects non-digest ref`; `cost label → M15 allocation contract → team showback → scanner requires label`; `runbook → M10 operations → incident diagnosis → owner review`. Which item lacks an explicit owner, and what should be added?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Default register: `base image → M01 hardened image program → avoid mutable tag → policy rejects non-digest ref`; `cost label → M15 allocation contract → team showback → scanner requires label`; `runbook → M10 operations → incident diagnosis → owner review`. Which item lacks an explicit owner, and what should be added?
```

**Model answer**
The table as given has no owner column for any item. Add a named accountable owner/team, source artifact/version, verification test identifier, support tier and review date. The default→source→reason→test chain is incomplete without ownership and maintenance.

**Reasoning**
The register explains why a default exists and how it is tested, but not who maintains it or what version applies.

**Common wrong answers / tempting mistakes**
Assuming the source module is automatically the owner; treating the test as ownership; claiming the table is complete because each row has a reason.

**Scoring guidance**
Score: identify ownership gap 2; specify useful metadata 3.


### U02-Q08 — Artifact Interpretation
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Conformance report: `svc-a: template v3, required files yes, policy pass, SLO yes, catalog yes`; `svc-b: template v2, required files yes, policy fail, SLO yes, catalog yes`; `svc-c: source provenance unknown, policy pass, SLO missing, catalog yes`. Classify each without overclaiming.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Conformance report: `svc-a: template v3, required files yes, policy pass, SLO yes, catalog yes`; `svc-b: template v2, required files yes, policy fail, SLO yes, catalog yes`; `svc-c: source provenance unknown, policy pass, SLO missing, catalog yes`. Classify each without overclaiming.
```

**Model answer**
svc-a appears conformant to the stated checks, subject to scanner freshness and rule coverage. svc-b is non-conformant because policy fails. svc-c is unknown/partially evidenced, not conformant: provenance is unknown and SLO is missing. Do not infer runtime safety or production readiness from repository checks.

**Reasoning**
Conformance is an evidence contract. Unknown must not be silently mapped to pass.

**Common wrong answers / tempting mistakes**
Calling all three conformant because files exist; treating unknown as fail without stating why; assuming conformance proves runtime behavior.

**Scoring guidance**
Score: classifications 3; limitations 2.


### U02-Q09 — Artifact Interpretation
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] A policy report says: `P-014 FAIL: resources.requests.cpu missing. Why: scheduler capacity and noisy-neighbor control. Fix: declare a request using the service tier guidance. Docs: /golden-path/resources`. What makes this message actionable, and what additional test checks message quality?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] A policy report says: `P-014 FAIL: resources.requests.cpu missing. Why: scheduler capacity and noisy-neighbor control. Fix: declare a request using the service tier guidance. Docs: /golden-path/resources`. What makes this message actionable, and what additional test checks message quality?
```

**Model answer**
It identifies a stable rule, failure, reason, concrete remediation and documentation pointer. A message-quality test can assert those fields exist and that the remediation does not recommend an unsafe blanket value. A separate negative fixture should trigger the rule and verify the diagnostic.

**Reasoning**
A policy can technically deny yet remain unusable if developers cannot fix it.

**Common wrong answers / tempting mistakes**
Only printing `policy failed`; testing the message but not the rule; hard-coding a one-size resource value without tier context.

**Scoring guidance**
Score: actionable elements 3; two test ideas 2.


### U02-Q10 — Artifact Review
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L2
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this golden-path manifest: `image: app:latest; runAsUser: 0; resources: {}; labels: {}; readinessProbe: absent; owner: TBD; SLO: absent; policy: warn forever`. Identify at least three defects and fixes.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this golden-path manifest: `image: app:latest; runAsUser: 0; resources: {}; labels: {}; readinessProbe: absent; owner: TBD; SLO: absent; policy: warn forever`. Identify at least three defects and fixes.
```

**Model answer**
Defects: mutable image tag/no digest; root execution; no resource requests/limits; missing ownership/cost labels; missing readiness; no SLO/operational evidence; warn-only policy with no promotion criteria. Fix with approved digest-pinned base, non-root, tiered resources, required labels/owner, appropriate probes, SLO/runbook and a documented warn→block gate after coverage and exception review.

**Reasoning**
These are inherited defaults: every generated repo receives them. One template defect can multiply across consumers.

**Common wrong answers / tempting mistakes**
Only adding documentation; claiming image scanning alone fixes `latest`; moving all rules to admission without CI feedback.

**Scoring guidance**
Score: 1 per defect up to 4; consequences/fixes 6.


### U02-Q11 — Artifact Review
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L3
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this support policy: `All deviations require platform approval. Any custom manifest is forbidden. Template generated files may be edited freely. No distinction between supported option and escape hatch. CI failures are generic. Exceptions never expire.`

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this support policy: `All deviations require platform approval. Any custom manifest is forbidden. Template generated files may be edited freely. No distinction between supported option and escape hatch. CI failures are generic. Exceptions never expire.`
```

**Model answer**
Defects: golden cage/no legitimate escape; platform approval bottleneck; no platform/team file ownership; unrestricted edits undermine updateability; no support tiers; no actionable diagnostics; no expiry/review for exceptions; mandatory rules and preferences are conflated. Fix with default/option/escape tiers, preserved mandatory controls, ownership metadata, file boundaries, reviewed exceptions with expiry and specific messages.

**Reasoning**
A supported path must be maintainable and debuggable. Autonomy and safety are not opposites when boundaries are explicit.

**Common wrong answers / tempting mistakes**
Assuming all deviation is malicious; assuming edits never affect updateability; making every rule optional to avoid a cage.

**Scoring guidance**
Score: identify 3+ defects 4; consequences and concrete repairs 6.


### U02-Q12 — Artifact Review
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L4
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this CI policy design: `Only scans source YAML. Does not render Helm/Kustomize. Checks syntax only. No negative fixtures. Policy errors say "invalid". Admission uses a separate untested policy set. No exception expiry.`

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this CI policy design: `Only scans source YAML. Does not render Helm/Kustomize. Checks syntax only. No negative fixtures. Policy errors say "invalid". Admission uses a separate untested policy set. No exception expiry.`
```

**Model answer**
Defects: unrendered manifests evade checks; syntax-only misses semantic/security policy; no negative tests; CI/admission policy drift; generic errors; no exception lifecycle; no owner/version for rules. Fix with render matrix, schema validation, policy tests with planted unsafe cases, CI/admission consistency checks, actionable messages and expiring exceptions.

**Reasoning**
A secure golden path must prove the rules on generated and rendered outputs, not just source files.

**Common wrong answers / tempting mistakes**
Assuming source scanning covers rendered output; assuming syntax validation equals policy; accepting two policy sets without equivalence tests.

**Scoring guidance**
Score: at least three defects 4; fixes/tests 6.


### U02-Q13 — Incident
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L4
- **Question type:** incident
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC INCIDENT] A shared template release introduces a bad CI workflow. A canary service passes, but several batch and model-serving repositories fail after broad update. Diagnose and recover.

**Model answer**
Freeze further propagation and preserve release, template, consumer-version and CI evidence. Identify affected archetypes and exact consumer revisions. Revert/pin the shared workflow or publish a corrected compatible release only after confirming rollback semantics; do not mass-edit all repos blindly. Communicate affected teams and support route. Reproduce with a matrix across archetypes and local customizations, add regression fixtures, improve canary representation and release gates, and review ownership/change notice.

**Reasoning**
One API-service canary did not represent batch/model-serving consumers. A release ring must cover risk-relevant archetypes, not just one friendly repository.

**Common wrong answers / tempting mistakes**
Continue rollout; overwrite team-owned files; roll back without checking compatibility; blame teams for local differences.

**Scoring guidance**
Score: containment 2; evidence/blast radius 2; safe mitigation/comms 3; prevention 3.


### U02-Q14 — Design
- **Scope:** Unit 2 — Golden paths, templates, and paved roads; golden path versus cage; template versus journey; service archetypes; shared and specific layers; default-option-escape; secure defaults; conformance; policy/validation; negative tests; actionable errors; template ownership; canary and blast radius
- **Level:** L3
- **Question type:** design
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated golden paths, templates, and paved roads topic.
- **Suggested time:** 25 minutes

**Prompt**
Design a golden-path family for API, batch/ETL and model-serving that has common controls and explicit variation/escape boundaries.

**Model answer**
Strong outline: shared repo metadata, hardened digest-pinned image policy, least-privilege reusable CI, security/supply-chain checks, catalog/owner/runbook/SLO skeleton, cost labels and docs. API layer defines health/readiness and request behavior; batch defines schedule, idempotency/checkpoint and freshness; model-serving defines immutable model digest/card, serving probes and controlled rollout. Define default, supported parameters and escape status; mandatory policy still applies. Build conformance scanner over template provenance, files and test evidence; negative-test each default; support policy and ring rollout.

**Reasoning**
A family avoids both duplication and false uniformity. Conformance should be transparent and not pretend static checks prove runtime health.

**Common wrong answers / tempting mistakes**
One template for every workload; one independent platform per archetype; ungoverned custom manifests.

**Scoring guidance**
Score 0–2 each: shared core, archetype variation, policy tests, escape/support model, observability, conformance and rollout (14).


---

## Unit 3 — Self-service infrastructure and environment provisioning

**Lesson:** [`03-self-service-infrastructure-and-environment-provisioning.md`](03-self-service-infrastructure-and-environment-provisioning.md)  
**Coverage:** developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning

### U03-Q01 — Short Answer
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L1
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 6 minutes

**Prompt**
What distinguishes self-service from a request form that still creates a ticket?

**Model answer**
Self-service completes a bounded, entitled request through an automated workflow and returns observable status and a usable result without a human manually executing the routine steps. Human approval may remain for risk-sensitive actions, but it should be explicit and risk-based rather than the default hidden work queue.

**Reasoning**
A front door is not self-service unless the backend, guardrails, lifecycle and feedback complete the task.

**Common wrong answers / tempting mistakes**
A portal form alone; removing every approval regardless of risk; treating accepted request as completed provisioning.

**Scoring guidance**
Score: end-to-end result 2; guardrail nuance 2; status/readiness 1.


### U03-Q02 — Short Answer
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 6 minutes

**Prompt**
Why should CLI, portal and Git/PR front doors share one canonical request contract and backend?

**Model answer**
One contract prevents divergent validation and entitlement semantics. Each front door becomes an adapter that submits the same typed intent to a shared validator/orchestrator and reports the same lifecycle status. This keeps policy consistent and makes the portal replaceable.

**Reasoning**
The API/contract is the product boundary; interfaces should not become separate authorization systems.

**Common wrong answers / tempting mistakes**
Duplicating business rules in each UI; allowing CLI to bypass checks; assuming a common YAML file alone enforces authorization.

**Scoring guidance**
Score: canonical contract 2; shared enforcement 2; interface adapter explanation 1.


### U03-Q03 — Short Answer
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 6 minutes

**Prompt**
Distinguish request accepted, resources reconciled, and usable environment ready.

**Model answer**
Accepted means the request passed an initial intake stage. Reconciled means controllers report desired resources created/observed. Usable ready means the developer-facing acceptance probe succeeds: required endpoint/data access works, credentials are safely referenced, policies are in place, and ownership/status are visible. Each state needs explicit conditions and evidence.

**Reasoning**
An API response or object creation is not proof that the environment can perform its intended job.

**Common wrong answers / tempting mistakes**
Equating HTTP 200 with readiness; treating namespace creation as full environment; hiding partial failure.

**Scoring guidance**
Score: three states 3; usable evidence 2.


### U03-Q04 — Mcq
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L2
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the self-service infrastructure and environment provisioning principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A request fails because `analytics` is not entitled to `gpu-large`. Which layer should reject it first?

**Options**
A. Reject only if the YAML cannot be parsed.
B. Reject at the entitlement layer before privileged provisioning.
C. Wait for admission to deny after resources have been submitted.
D. Return a generic capacity error even though the capability is not entitled.

**Model answer**
**Correct option: B.** The entitlement check should reject the request before privileged provisioning. Schema validation checks shape; entitlement checks whether the authenticated team may request that capability; later policy/admission/quota/controller layers remain defense in depth.

**Reasoning**
A only checks whether the field is syntactically valid. C is too late and could allow unnecessary privileged work. D hides an authorization decision inside a generic capacity error.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: syntax is not authorization. C: admission is a later control. D: capacity and entitlement are distinct denial reasons.

**Scoring guidance**
Score: correct option 1; layer reasoning 2.


### U03-Q05 — Mcq
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L3
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the self-service infrastructure and environment provisioning principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A GitOps request object is accepted, but the database is not reachable and readiness probe fails. What should the platform report?

**Options**
A. Mark the environment READY because the request was accepted.
B. Mark READY because GitOps synchronized the desired state.
C. Report degraded/failed readiness with the failing stage, safe diagnostic reference and correlation ID.
D. Delete all resources immediately and suppress the original request record.

**Model answer**
**Correct option: C.** Provisioning is not usable-ready. Report a specific degraded/failed status with the responsible stage, safe diagnostic reference, retry/remediation guidance and correlation ID. Preserve the request and controller evidence.

**Reasoning**
A confuses accepted with ready. B masks a partial failure. D may destroy evidence and create a second inconsistent resource.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: accepted is an earlier state. B: false success misleads developers. D: deleting first can obscure the root cause and data consequences.

**Scoring guidance**
Score: correct 1; status/evidence explanation 2.


### U03-Q06 — Mcq
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L4
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the self-service infrastructure and environment provisioning principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A preview environment reaches its TTL. It contains a synthetic database with a retention hold flag. What is the safest cleanup behavior?

**Options**
A. Delete the namespace because TTL overrides every data-retention decision.
B. Delete the namespace and ignore external database/bucket dependencies.
C. Disable the reaper globally whenever one hold is encountered.
D. Stop destructive cleanup at the hold gate, preserve evidence and require the approved retention decision.

**Model answer**
**Correct option: D.** The reaper should detect the hold and stop before destructive deletion, report the blocker, preserve data and audit evidence, and require the approved retention workflow. TTL is not authority to bypass retention or data-owner decisions.

**Reasoning**
A assumes TTL overrides data safety. B deletes the namespace but leaves dependent resources. C disables the reaper globally and creates orphan risk.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: lifecycle policy must respect hold. B: namespace deletion is not dependency-aware cleanup. C: broad disablement is not targeted remediation.

**Scoring guidance**
Score: correct 1; hold and dependency reasoning 2.


### U03-Q07 — Artifact Interpretation
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L2
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Request: `team=analytics, environment=dev, tier=standard, size=small, ttl=72h, needs.postgres=true`. Entitlement registry: `analytics: dev, standard, small; postgres=false`. Identify the correct rejection layer and response.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Request: `team=analytics, environment=dev, tier=standard, size=small, ttl=72h, needs.postgres=true`. Entitlement registry: `analytics: dev, standard, small; postgres=false`. Identify the correct rejection layer and response.
```

**Model answer**
Schema is valid. Entitlement denies PostgreSQL for analytics under this synthetic registry. Reject before GitOps/controller provisioning with a stable denial code, requested capability, entitlement source/version and safe remediation (request entitlement review). Do not silently provision without PostgreSQL or fall through to controller failure.

**Reasoning**
The contract is syntactically valid but unauthorized. Denial must be explicit and auditable.

**Common wrong answers / tempting mistakes**
Calling it malformed YAML; provisioning anyway; returning generic provider error.

**Scoring guidance**
Score: schema-vs-entitlement 2; correct stage 2; response evidence 1.


### U03-Q08 — Artifact Interpretation
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Status timeline: `10:00 request_received`; `10:01 schema_valid`; `10:02 entitlement_approved`; `10:03 policy_pass`; `10:05 gitops_synced`; `10:08 namespace_ready`; `10:09 database_secret_reference_created`; `10:10 connectivity_probe_failed`. Can the platform mark READY?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Status timeline: `10:00 request_received`; `10:01 schema_valid`; `10:02 entitlement_approved`; `10:03 policy_pass`; `10:05 gitops_synced`; `10:08 namespace_ready`; `10:09 database_secret_reference_created`; `10:10 connectivity_probe_failed`. Can the platform mark READY?
```

**Model answer**
No. The connectivity probe failed, so the environment has not demonstrated its advertised usable outcome. Report a failed/degraded stage with the probe result, safe correlation, retry policy and owner route. Do not expose secret values. A successful namespace and secret reference are partial readiness evidence only.

**Reasoning**
Readiness must be defined from the user's task, not the existence of child resources.

**Common wrong answers / tempting mistakes**
Marking READY after namespace creation; printing credential contents to aid debugging; retrying forever without a bound.

**Scoring guidance**
Score: decision 1; reasoning 2; safe status contents 2.


### U03-Q09 — Artifact Interpretation
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Retry log: `attempt 1: timeout after create`; `attempt 2: duplicate namespace`; `attempt 3: request accepted again`. Explain the likely design flaw and two controls.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Retry log: `attempt 1: timeout after create`; `attempt 2: duplicate namespace`; `attempt 3: request accepted again`. Explain the likely design flaw and two controls.
```

**Model answer**
Likely missing idempotency/correlation and reconciliation of desired versus actual state. Use a stable request ID/idempotency key, deterministic resource names, lookup-before-create, controller reconciliation, bounded retry/backoff and explicit duplicate-state handling. Test replaying the same request and a timeout after successful side effect.

**Reasoning**
Retries are normal in distributed workflows; they must not multiply resources.

**Common wrong answers / tempting mistakes**
Assuming retries never happen; using a new random resource name per retry; manually deleting all objects on timeout.

**Scoring guidance**
Score: root cause 2; two controls 2; test 1.


### U03-Q10 — Artifact Review
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L2
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 12 minutes

**Prompt**
Review request validator: `team` comes from request body; any `namespace` is accepted; `tier` accepts arbitrary strings; `ttl` is optional and unlimited; no entitlement lookup; `owner` can be set to `platform-admin`; errors return full submitted YAML including secrets.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review request validator: `team` comes from request body; any `namespace` is accepted; `tier` accepts arbitrary strings; `ttl` is optional and unlimited; no entitlement lookup; `owner` can be set to `platform-admin`; errors return full submitted YAML including secrets.
```

**Model answer**
Defects: tenant/team identity is caller-controlled; arbitrary namespace allows cross-scope targeting; no tier enum; no TTL bound; no entitlement authorization; caller can impersonate privileged owner; error echoes secrets/input; no stable error code or audit. Derive team from authenticated identity, validate namespace mapping, enum/limits, enforce entitlement, protect ownership fields, redact sensitive input and test injection/over-entitlement attempts.

**Reasoning**
Schema validation alone cannot authorize a request. Trust must come from authenticated principal and protected registries.

**Common wrong answers / tempting mistakes**
Only adding a YAML parser; accepting caller-supplied owner; logging full request for debugging.

**Scoring guidance**
Score: 1 per defect up to 4; fixes/consequences 6.


### U03-Q11 — Artifact Review
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L3
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 12 minutes

**Prompt**
Review a preview reaper: `for each expired namespace: kubectl delete namespace; ignore errors; mark request deleted`. No inventory, dry-run, hold check, dependency order, retry record or post-delete verification.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review a preview reaper: `for each expired namespace: kubectl delete namespace; ignore errors; mark request deleted`. No inventory, dry-run, hold check, dependency order, retry record or post-delete verification.
```

**Model answer**
Defects: blind namespace deletion; no data-retention/hold review; no dependency inventory for external DB/bucket/queue; ignored errors; false deleted status; no idempotency/retry state; no dry-run; no orphan check; no evidence. Fix with inventory and retention gate, dependency-aware ordered cleanup, explicit dry-run and approval for destructive steps, bounded retries, state machine, post-delete/orphan verification and audit record.

**Reasoning**
Namespace deletion may not delete external resources and may trigger destructive effects. A terminal status must reflect verified cleanup.

**Common wrong answers / tempting mistakes**
Treating namespace disappearance as complete deprovision; ignoring errors; relying on TTL as consent to delete all data.

**Scoring guidance**
Score: defects 4; consequences and fixes 6.


### U03-Q12 — Artifact Review
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L4
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this provisioning flow: `portal writes a resource directly; CLI writes another schema; entitlement only checked in portal; GitOps applies all requests; controller has broad cluster-admin; status shows 'done' after sync; no cost quota or cleanup owner`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this provisioning flow: `portal writes a resource directly; CLI writes another schema; entitlement only checked in portal; GitOps applies all requests; controller has broad cluster-admin; status shows 'done' after sync; no cost quota or cleanup owner`.
```

**Model answer**
Defects: multiple incompatible request contracts; front-door-specific authorization bypass; no shared policy; broad controller privilege; sync is mistaken for usable readiness; no quota/capacity/cost guard; no lifecycle owner/cleanup; no negative tests. Fix with canonical contract and backend, authenticated entitlement for every front door, least-privilege controller, layered policy, readiness probe, quota and cost checks, owner and lifecycle, and test matrix.

**Reasoning**
The architecture creates an alternate path around controls and overclaims completion.

**Common wrong answers / tempting mistakes**
Assuming portal authentication covers CLI; granting cluster-admin for convenience; equating GitOps sync with readiness.

**Scoring guidance**
Score: defects 4; fixes and impact 6.


### U03-Q13 — Incident
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L4
- **Question type:** incident
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC INCIDENT] A bulk preview request storm creates namespaces and databases faster than the lab can handle. Queue wait rises, some requests time out after creating resources, and cleanup is delayed. Diagnose and respond.

**Model answer**
First pause or rate-limit new preview intake at the narrowest safe boundary; preserve request IDs, queue, controller and resource evidence. Bound concurrency and per-tenant quotas; separate capacity exhaustion from provider/controller failure. Reconcile timed-out requests before retrying to avoid duplicates. Prioritize existing critical workloads, communicate degraded provisioning and ETA uncertainty, and monitor ready/failed/cleanup states. After stabilization, add admission/capacity prechecks, backpressure, idempotency, retry budgets, TTL cleanup capacity, storm tests and a provisioning SLO/error-budget policy.

**Reasoning**
A bulk storm is both a capacity and lifecycle problem. Blind retries and broad deletion can worsen it.

**Common wrong answers / tempting mistakes**
Scale all components without measuring; delete all preview namespaces; report success from accepted requests.

**Scoring guidance**
Score: first action 2; evidence/layer localization 2; safe mitigation/comms 3; prevention 3.


### U03-Q14 — Design
- **Scope:** Unit 3 — Self-service infrastructure and environment provisioning; developer request journey; canonical request; multiple front doors; entitlement registry; schema and policy layers; GitOps; data services; secret references; TTL; idempotency/reconciliation; status and usable readiness; cost/capacity; deprovisioning
- **Level:** L3
- **Question type:** design
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated self-service infrastructure and environment provisioning topic.
- **Suggested time:** 25 minutes

**Prompt**
Design a safe self-service request lifecycle for environments with PostgreSQL and object storage options.

**Model answer**
Strong outline: canonical schema with stable request ID, team/environment/tier/size/TTL/capabilities; derive team from authenticated identity; validate schema, entitlement, policy, cost/capacity and approvals; submit desired state through one backend/GitOps path; reconcile idempotently; report stage conditions; test usable readiness with connectivity/data access; store only secret references; inventory dependencies and owner; deprovision via retention/hold check, export, ordered delete, orphan scan and audit. Define SLOs for success and time-to-ready; test all denial layers and retries.

**Reasoning**
Self-service is a lifecycle contract, not a one-shot create call.

**Common wrong answers / tempting mistakes**
Portal-only validation; credentials in request; no cleanup or readiness probe.

**Scoring guidance**
Score 0–2 each: schema/identity, entitlement, layers, reconciliation/status, data/secret safety, lifecycle, SLO/evidence (14).


---

## Unit 4 — Developer portals and the Backstage service catalog

**Lesson:** [`04-developer-portals-and-backstage-service-catalog.md`](04-developer-portals-and-backstage-service-catalog.md)  
**Coverage:** portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs

### U04-Q01 — Short Answer
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L1
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 6 minutes

**Prompt**
Explain why a service catalog is a governed model rather than a list of repository links.

**Model answer**
A catalog models software entities and relationships: components, APIs, resources, systems, teams/groups, ownership, lifecycle, dependencies, runbooks and operational evidence. Links are useful, but without validated ownership, freshness and dependency data the catalog cannot safely support incident routing or platform automation.

**Reasoning**
The catalog is structured operational data. A portal merely presents it.

**Common wrong answers / tempting mistakes**
Treating URL presence as catalog quality; assuming Backstage automatically validates business truth; confusing catalog with a data catalog.

**Scoring guidance**
Score: model definition 2; operational facts 2; limitation 1.


### U04-Q02 — Short Answer
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 6 minutes

**Prompt**
Distinguish authentication from authorization in a developer portal.

**Model answer**
Authentication establishes who the user is. Authorization determines which actions and data that identity may access. A valid login does not justify admin-level catalog edits, scaffolder actions, secrets access or provider operations. Privileged actions need narrowly scoped permissions and separate trust boundaries.

**Reasoning**
Identity is necessary but insufficient. The portal may proxy or initiate powerful backend operations.

**Common wrong answers / tempting mistakes**
Assuming login means permission; using a shared admin token for every user; hiding the admin button as authorization.

**Scoring guidance**
Score: definitions 2; privileged action example 2; least-privilege implication 1.


### U04-Q03 — Short Answer
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 6 minutes

**Prompt**
Why is a thin static portal the guaranteed path and Backstage an optional profile in this course?

**Model answer**
The source syllabus requires a zero-budget laptop-first path and warns that Backstage's Node build/runtime is heavy on an 8 GB machine. A static portal over validated local catalog files is guaranteed; Backstage is attempted only after a preflight and run alone with heavy components stopped. The choice is based on user need and operating cost, not a claim that Backstage is inferior.

**Reasoning**
A portal framework adds lifecycle, authentication, plugin, dependency and availability responsibilities. The catalog data and fallback should remain usable independently.

**Common wrong answers / tempting mistakes**
Treating Backstage as mandatory; running every heavy component together; believing a static portal cannot be useful.

**Scoring guidance**
Score: resource/profile 2; product trade-off 2; independence 1.


### U04-Q04 — Mcq
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L2
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the developer portals and the backstage service catalog principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A service catalog entry says `owner: team-a`, but the normalized ownership registry maps the component to `analytics`. Which is the safest next step?

**Options**
A. Trust the catalog owner string because the entity resolves syntactically.
B. Treat the mismatch as a catalog-quality failure and reconcile against the authoritative ownership projection.
C. Assume the latest source is always correct without checking provenance or freshness.
D. Delete the catalog entity and leave alert routing without an owner.

**Model answer**
**Correct option: B.** Treat the mismatch as a catalog quality failure. Reconcile against the authoritative ownership projection and source-of-truth hierarchy, then validate references and notify the accountable owner. Do not silently route incidents using stale or ambiguous metadata.

**Reasoning**
A ignores the mismatch. C assumes the registry is always correct without checking provenance/freshness. D destroys useful evidence and creates a different data gap.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: unvalidated metadata is unsafe. C: every source needs authority/freshness rules. D: deleting the entity does not repair ownership.

**Scoring guidance**
Score: correct 1; source-of-truth and evidence reasoning 2.


### U04-Q05 — Mcq
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L3
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the developer portals and the backstage service catalog principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A catalog file is syntactically valid but contains an external URL that points to an untrusted location and is used by an automation plugin. What control is most relevant?

**Options**
A. Accept any URL if the YAML parses.
B. Give the automation plugin a broad admin token so it can read every entity.
C. Hide the link in the UI but allow backend automation to consume it.
D. Validate allowed locations/provenance, restrict automation to trusted metadata and test untrusted input.

**Model answer**
**Correct option: D.** Validate allowed locations and provenance for catalog ingestion, restrict automation to trusted metadata and least privilege, and test malicious/untrusted entity input. Syntax validation does not establish trust.

**Reasoning**
A validates format only. B gives the plugin more power and increases blast radius. C assumes a browser display is harmless even though automation consumes the data.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: syntax is not provenance. B: privilege expansion is the wrong direction. C: catalog data can influence automation and routing.

**Scoring guidance**
Score: correct 1; trust boundary explanation 2.


### U04-Q06 — Mcq
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L4
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the developer portals and the backstage service catalog principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A portal login succeeds, but a user is not allowed to create a privileged model endpoint. What must enforce the denial?

**Options**
A. Enforce authorization at the privileged backend/action/API boundary using authenticated identity and entitlement.
B. Hide the action button in the UI and rely on the frontend.
C. Assume successful login means the user can execute every portal action.
D. Move every request to a human queue without defining authorization rules.

**Model answer**
**Correct option: A.** Authorization must be checked at the privileged action/backend/API boundary using the authenticated principal and entitlement/policy context. UI hiding is not a security control.

**Reasoning**
B relies on presentation. C confuses authentication with permission. D moves the decision to a human queue without defining policy and audit.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
B: UI can be bypassed. C: identity is not entitlement. D: human approval may be a risk control but is not a substitute for authorization.

**Scoring guidance**
Score: correct 1; backend enforcement rationale 2.


### U04-Q07 — Artifact Interpretation
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L2
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Catalog entity: `kind: Component; name: risk-scoring-api; owner: group:default/analytics; system: risk-platform; lifecycle: production; links: runbook, repo; dependsOn: resource:default/fraud-model-endpoint`. What can an on-call engineer infer, and what must be checked?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Catalog entity: `kind: Component; name: risk-scoring-api; owner: group:default/analytics; system: risk-platform; lifecycle: production; links: runbook, repo; dependsOn: resource:default/fraud-model-endpoint`. What can an on-call engineer infer, and what must be checked?
```

**Model answer**
The entity claims an owner, system, lifecycle, two links and a dependency. The engineer can use these as discovery leads, not unquestioned truth. Check entity freshness, owner reference resolution, runbook reachability, dependency direction/validity and observed telemetry. Confirm on-call route against the current ownership source before paging.

**Reasoning**
Declared metadata and observed dependencies are different evidence sources; freshness and provenance matter.

**Common wrong answers / tempting mistakes**
Assuming declared dependency proves live traffic; assuming owner reference is valid because string exists; assuming production lifecycle means SLO met.

**Scoring guidance**
Score: infer 2; limitations 2; validation steps 1.


### U04-Q08 — Artifact Interpretation
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Catalog linter report: `8 entities scanned; 2 unresolved owners; 1 missing runbook; 1 orphan component; 2 stale source timestamps`. Explain whether a scorecard can pass the portal release gate.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Catalog linter report: `8 entities scanned; 2 unresolved owners; 1 missing runbook; 1 orphan component; 2 stale source timestamps`. Explain whether a scorecard can pass the portal release gate.
```

**Model answer**
Not without the release gate's defined thresholds and required fields. At minimum, unresolved ownership and stale records can undermine incident routing. The gate should classify critical versus warning findings, identify affected entities, require owner remediation or approved exception with expiry, and keep the static fallback. The count alone is not a universal pass/fail threshold.

**Reasoning**
A quality score needs explicit numerator, denominator, freshness window, severity and exceptions.

**Common wrong answers / tempting mistakes**
Declaring 8/8 entities valid; assuming all warnings equal; hiding defects by excluding stale records without documenting exclusions.

**Scoring guidance**
Score: no unsupported threshold 1; decision logic 2; required evidence 2.


### U04-Q09 — Artifact Interpretation
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Portal dependency graph says service A depends on B; telemetry-derived edge report shows no observed calls in the last 30 days. What are two plausible explanations and what should the portal display?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Portal dependency graph says service A depends on B; telemetry-derived edge report shows no observed calls in the last 30 days. What are two plausible explanations and what should the portal display?
```

**Model answer**
The dependency may be stale/unused, or telemetry coverage/window may be incomplete (rare batch jobs, dormant workflows, sampling or missing instrumentation). Display declared and observed edges separately with source, window and confidence/freshness; flag disagreement for owner review. Do not auto-delete the declared edge solely from absence of telemetry.

**Reasoning**
Declared intent and observed behavior answer different questions. Missing telemetry is not proof of no dependency.

**Common wrong answers / tempting mistakes**
Deleting the edge immediately; treating telemetry as complete; merging both sources into one unqualified relationship.

**Scoring guidance**
Score: two hypotheses 2; separate evidence labels 2; safe next step 1.


### U04-Q10 — Artifact Review
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L2
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this catalog record: `kind: Component; name: fraud-api; owner: team:default/unknown; lifecycle: prod; links: [{title: Runbook, url: javascript:...}]; dependsOn: [fraud-db]; lastUpdated: never`. Identify at least three defects.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this catalog record: `kind: Component; name: fraud-api; owner: team:default/unknown; lifecycle: prod; links: [{title: Runbook, url: javascript:...}]; dependsOn: [fraud-db]; lastUpdated: never`. Identify at least three defects.
```

**Model answer**
Defects: unresolved/noncanonical owner reference; unverified lifecycle value/semantics; unsafe URL scheme (injection); dependency lacks resolvable entity reference/type/namespace; no source provenance/freshness; no SLO/on-call/support metadata. Fix with validated entity refs and owner registry, allowed URL schemes/domains, schema validation, provenance timestamp and explicit dependency relation, and freshness/drift checks. Exact Backstage field schema/annotation behavior is `[VERIFY]` for the selected release.

**Reasoning**
Catalog data is consumed by UI and automation; malicious URLs and stale ownership are security/incident risks.

**Common wrong answers / tempting mistakes**
Only fixing YAML indentation; assuming browser escaping neutralizes all plugin actions; treating name-only dependency as resolved.

**Scoring guidance**
Score: defects 4; consequence and fixes 6.


### U04-Q11 — Artifact Review
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L3
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this portal deployment proposal: `Backstage latest; guest auth enabled for all networks; admin token shared by catalog, Scaffolder and plugins; no preflight; static fallback removed; catalog source can be any user URL; no upgrade owner.`

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this portal deployment proposal: `Backstage latest; guest auth enabled for all networks; admin token shared by catalog, Scaffolder and plugins; no preflight; static fallback removed; catalog source can be any user URL; no upgrade owner.`
```

**Model answer**
Defects: unpinned release; guest auth not constrained to lab; shared broad token; no authentication/authorization separation; no resource/toolchain preflight; no independent fallback; untrusted catalog ingestion; no plugin/action review; no owner or upgrade process. Fix with pinned/version-recorded local build, lab-only guest boundary, least privilege per action/service, trusted catalog locations, preflight and isolated Plat+Portal profile, static fallback, owner/SLO/upgrade/DR process.

**Reasoning**
The portal is a privileged control surface and catalog inputs may influence automation. Its outage should not disable the platform API/Git path.

**Common wrong answers / tempting mistakes**
Treating guest auth as harmless because data is synthetic; giving admin token to every plugin; removing fallback to force usage.

**Scoring guidance**
Score: defects 4; fixes and blast-radius reasoning 6.


### U04-Q12 — Artifact Review
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L4
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this scorecard: `Developer score = 100 × number of commits / engineer; red teams are low performers. Missing SLO evidence counts as pass. Cost is displayed as exact currency though source is HCU estimates. No timestamp or provenance.`

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this scorecard: `Developer score = 100 × number of commits / engineer; red teams are low performers. Missing SLO evidence counts as pass. Cost is displayed as exact currency though source is HCU estimates. No timestamp or provenance.`
```

**Model answer**
Defects: individual productivity ranking and surveillance; missing evidence is treated as pass; commits are a vanity/Goodhart-prone proxy; team/tenant aggregation and privacy controls absent; HCU is not currency; no source timestamp, owner, freshness or provenance; scorecard criteria lack definitions. Replace with service/team-level evidence-backed controls, unknown/stale state, synthetic HCU labels, provenance and no individual fields.

**Reasoning**
A scorecard should diagnose platform capability, not rank people. Missing evidence is not positive evidence.

**Common wrong answers / tempting mistakes**
Removing names but keeping per-person scores; using commit count as a productivity measure; converting HCU to currency without exchange basis.

**Scoring guidance**
Score: defects 4; repair design 6.


### U04-Q13 — Incident
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L4
- **Question type:** incident
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC INCIDENT] An incident alert routes to the wrong team because the portal catalog still lists the previous owner. What is the response sequence?

**Model answer**
Confirm the alert and affected service; preserve the catalog revision, ownership source, ingestion timestamp and routing event. Use the authoritative current ownership registry/on-call source to route the incident; do not rely on the stale portal value. Mark the catalog record degraded/stale, notify catalog owner and affected teams, repair the source and ingestion pipeline, validate references, and verify routing with a synthetic test. Add freshness SLO/alert, change ownership workflow, drift report and fallback routing.

**Reasoning**
The catalog is a discovery aid only if freshness and provenance are maintained. Incident response should use a trusted fallback when data is stale.

**Common wrong answers / tempting mistakes**
Paging both teams blindly; editing the portal cache only; treating the portal UI as the source of truth.

**Scoring guidance**
Score: immediate routing 2; evidence 2; correction/comms 2; prevention 4.


### U04-Q14 — Design
- **Scope:** Unit 4 — Developer portals and the Backstage service catalog; portal vs platform vs catalog; catalog-as-code; entity and ownership relationships; linter; thin portal; Backstage preflight; ingestion and trust; plugins/authn/authz; scorecards/showback; fallback and portal SLOs
- **Level:** L3
- **Question type:** design
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated developer portals and the backstage service catalog topic.
- **Suggested time:** 25 minutes

**Prompt**
Design a zero-budget portal/catalog approach for a 4-CPU/8-GB laptop, with Backstage as an optional extension.

**Model answer**
Strong outline: begin with catalog-as-code, validated entity relationships, ownership projection, deterministic Python static generator, safe HTML escaping, search/graph/freshness, evidence-backed scorecards, and independent static fallback. Preflight Node/yarn/memory; if feasible run Backstage alone under Plat+Portal with lab-only guest auth and local catalog source. Define catalog source-of-truth, allowed locations, authn/authz, plugin review, owner, SLO, backup/restore and upgrade path. Do not run Backstage alongside full Plat+Control stack.

**Reasoning**
The portal product should remain useful and available independently of a heavy framework.

**Common wrong answers / tempting mistakes**
Assuming Backstage must be used; running all services simultaneously; exposing guest-auth instance publicly.

**Scoring guidance**
Score 0–2 each: requirements, resource-fit, catalog trust, security, fallback, operations, evidence (14).


---

## Unit 5 — Scaffolding and software templates

**Lesson:** [`05-scaffolding-and-software-templates.md`](05-scaffolding-and-software-templates.md)  
**Coverage:** template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation

### U05-Q01 — Short Answer
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L1
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 6 minutes

**Prompt**
Why is scaffolding generation different from maintaining generated repositories?

**Model answer**
Generation applies a template revision and validated answers to create a starting repository. Maintenance requires provenance, recorded answers/source revision, compatibility policy, update preview, conflict handling, migrations, tests and owner review. A successful copy does not keep consumers aligned with later security fixes.

**Reasoning**
The source template and generated repository diverge after generation unless an update lifecycle exists.

**Common wrong answers / tempting mistakes**
Assuming a new template release updates all repositories automatically; assuming Git fork alone provides a safe migration; assuming generation success proves operational safety.

**Scoring guidance**
Score: distinction 2; maintenance controls 2; limitation 1.


### U05-Q02 — Short Answer
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 6 minutes

**Prompt**
Explain why template parameters should be minimal, validated and derived where possible.

**Model answer**
Each parameter is an input surface and a chance for invalid state, inconsistent naming or injection. Ask only for decisions the developer must make, validate type/format/allow-list and cross-field rules before tasks run, and derive repository/image/catalog names from a canonical slug. Never let user input choose privileged identity, namespace or arbitrary execution.

**Reasoning**
Parameter minimization reduces cognitive load and attack surface while improving reproducibility.

**Common wrong answers / tempting mistakes**
Asking users to enter redundant identifiers; trusting template answers; validating only after hooks execute.

**Scoring guidance**
Score: input-surface reasoning 2; validation/derivation 2; security consequence 1.


### U05-Q03 — Short Answer
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 6 minutes

**Prompt**
What belongs in a platform-owned versus team-owned generated-file boundary?

**Model answer**
Platform-owned files encode shared contracts/defaults such as reusable workflow callers, baseline policy, template metadata and controlled deployment scaffolding; team-owned files contain application logic, tests and intentional service-specific configuration. The boundary must be documented and reflected in update tooling so platform updates do not silently overwrite team work. Exact implementation depends on template engine/version `[VERIFY]`.

**Reasoning**
Ownership is needed for safe updates and conflict resolution.

**Common wrong answers / tempting mistakes**
Treating every generated file as platform-owned; allowing unreviewed overwrite; assuming a template marker automatically protects content.

**Scoring guidance**
Score: examples 2; update safety 2; version caveat 1.


### U05-Q04 — Mcq
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L2
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the scaffolding and software templates principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A template task would execute a downloaded script from a user-controlled URL. What is the safest action?

**Options**
A. Run the downloaded script, then scan the generated repository.
B. Allow the user-controlled URL if the template repository is pinned.
C. Do not run it; remove arbitrary execution or pin/verify reviewed content and validate inputs before tasks.
D. Run the task with a shared platform-admin identity to avoid permission errors.

**Model answer**
**Correct option: C.** Do not run it. Remove arbitrary network execution or pin and verify an approved source after review; validate parameters before any task; run with least privilege and no secrets; use an isolated environment and record provenance. Exact Copier trust/task behavior is `[VERIFY]` for the pinned version.

**Reasoning**
A trusts an untrusted input. B relies on post-execution scanning. D exposes credentials and expands blast radius.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: user-controlled code execution. B: detection after execution is too late. D: shared privileged identity is unsafe.

**Scoring guidance**
Score: correct 1; execution-boundary rationale 2.


### U05-Q05 — Mcq
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L3
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the scaffolding and software templates principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A template update changes a platform-owned workflow but conflicts with a team-owned application file. What should the updater do?

**Options**
A. Preview the diff, preserve team-owned changes, quarantine conflicts and require owner review/tests.
B. Overwrite the conflicted files with template output automatically.
C. Stop all template updates permanently because one repository conflicts.
D. Auto-merge every conflict when the basic CI test is green.

**Model answer**
**Correct option: A.** Produce a preview/diff and conflict report, preserve team-owned changes, require owner review and tests, and avoid auto-merging unresolved conflicts. A migration script may assist but must be tested and reversible.

**Reasoning**
B silently destroys local work. C abandons all future updates. D bypasses the ownership contract.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
B: data loss and unreviewed behavior. C: leaves security drift. D: violates review and provenance.

**Scoring guidance**
Score: correct 1; safe update rationale 2.


### U05-Q06 — Mcq
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L4
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the scaffolding and software templates principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
Which statement about Copier and Cookiecutter is appropriate for a tool-specific question when current versions are not verified?

**Options**
A. Invent a current Copier flag and make it mandatory for the assessment.
B. Attribute Copier's update behavior to Cookiecutter.
C. State that Cookiecutter can never be updated under any circumstances.
D. Use Copier as the course's update-aware path, compare Cookiecutter, and verify exact flags/trust/update semantics for pinned versions.

**Model answer**
**Correct option: D.** State the course's decision framing—Copier is the primary teaching tool because the syllabus expects an update-aware workflow, Cookiecutter is compared—but mark exact commands, flags, trust behavior and update semantics `[VERIFY]` against the selected versions. Do not make an uncertain CLI detail decisive.

**Reasoning**
A invents a flag. B attributes one tool's behavior to another. C overstates a tool limitation without verification.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: fabricated syntax risk. B: tool semantics must not be conflated. C: absolute unsupported claim.

**Scoring guidance**
Score: correct 1; version-verification explanation 2.


### U05-Q07 — Artifact Interpretation
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L2
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Template answers: `service_name=risk-score-api; team=analytics; namespace=tn-team-a; owner=platform-admin; image_tag=latest`. Identify which values should be derived, checked or rejected.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Template answers: `service_name=risk-score-api; team=analytics; namespace=tn-team-a; owner=platform-admin; image_tag=latest`. Identify which values should be derived, checked or rejected.
```

**Model answer**
Derive repository/image/catalog slug from canonical `service_name`; resolve team through authenticated/allow-listed team registry rather than trusting free text; derive namespace from approved tenant mapping instead of accepting arbitrary namespace; reject `owner=platform-admin` if caller cannot assign it; reject mutable `latest` and require approved digest/pinned reference. Preserve separate team/tenant/namespace/cost-center concepts.

**Reasoning**
The template is a privileged program input boundary. Derived values reduce mismatch and caller-controlled authority.

**Common wrong answers / tempting mistakes**
Copying every answer literally; treating a namespace as equivalent to team; accepting latest because it is convenient.

**Scoring guidance**
Score: correct handling of five fields 4; reasoning 1.


### U05-Q08 — Artifact Interpretation
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Generated repo has `.copier-answers.yml` naming template source/revision, but its `Dockerfile` was locally changed and the update preview shows a conflict. What evidence and decision are required?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Generated repo has `.copier-answers.yml` naming template source/revision, but its `Dockerfile` was locally changed and the update preview shows a conflict. What evidence and decision are required?
```

**Model answer**
Inspect template revision and answer/provenance metadata, diff and conflict class, file ownership contract, local reason for Dockerfile change, resulting image policy and tests. A service owner must resolve the conflict; preserve legitimate local requirements while ensuring mandatory security baseline. Run template conformance, build/test and negative policy checks before merge. The answers file is provenance evidence, not proof every generated file remains compliant.

**Reasoning**
Update workflow must preserve customization and restore safe baseline without overwriting blindly.

**Common wrong answers / tempting mistakes**
Auto-accept upstream; keep local edit without policy check; assume answers file guarantees no drift.

**Scoring guidance**
Score: evidence 2; ownership/review 2; post-update verification 1.


### U05-Q09 — Artifact Interpretation
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Update campaign: five repositories; four preview cleanly; one has conflict in platform-owned CI file and local permission changes. What is the correct campaign outcome?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Update campaign: five repositories; four preview cleanly; one has conflict in platform-owned CI file and local permission changes. What is the correct campaign outcome?
```

**Model answer**
Do not merge the conflicted repository automatically. Quarantine it from bulk merge, inspect local permissions and the desired least-privilege workflow, create a reviewed migration patch, run CI and security checks, and record a per-repository result. The other four may proceed only if each passes its own checks and approval policy. Report completion as 4/5 merged and 1 blocked, not 5/5.

**Reasoning**
Fleet update success is per consumer, not a single campaign-level green status.

**Common wrong answers / tempting mistakes**
Skipping the outlier; force-overwriting; stopping all four safe updates without explaining risk.

**Scoring guidance**
Score: isolate conflict 2; preserve permissions/evidence 2; accurate status 1.


### U05-Q10 — Artifact Review
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L2
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this template: `project_name` is interpolated into shell; task downloads `curl $URL | bash`; URL is user-controlled; task runs before validation; token is embedded in template; generated repo records no source revision.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this template: `project_name` is interpolated into shell; task downloads `curl $URL | bash`; URL is user-controlled; task runs before validation; token is embedded in template; generated repo records no source revision.
```

**Model answer**
Defects: shell injection via parameter; arbitrary remote code execution; untrusted URL; validation occurs too late; embedded credential; no least-privilege or isolation; missing provenance. Fix with strict parameter validation before task execution, no arbitrary shell interpolation, approved pinned content with integrity/provenance, no embedded secrets, least privilege, reviewed task behavior and source revision record.

**Reasoning**
Templates and hooks are executable supply-chain components, not passive text.

**Common wrong answers / tempting mistakes**
Escaping only the visible output; scanning after task; committing a fake token as a placeholder without secret hygiene.

**Scoring guidance**
Score: defects 4; fixes and consequences 6.


### U05-Q11 — Artifact Review
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L3
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this update bot: `bot has org-admin; scans all repos nightly; opens PRs and auto-merges if tests pass; no concurrency cap; no canary; no conflict policy; logs full environment; token stored in repo config`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this update bot: `bot has org-admin; scans all repos nightly; opens PRs and auto-merges if tests pass; no concurrency cap; no canary; no conflict policy; logs full environment; token stored in repo config`.
```

**Model answer**
Defects: excessive bot privilege; unbounded fleet scan/PR storm; no rate/concurrency limits; auto-merge lacks owner review and risk gating; no canary rings; no conflict handling; secret exposure in logs/config; no audit/rollback; no repo eligibility filter. Fix with short-lived least-privilege identity, secret injection, rate limits, staged cohorts, review gates, conflict quarantine, redacted logs, immutable release pin and rollback procedure.

**Reasoning**
A bot is a privileged actor and a shared-change multiplier.

**Common wrong answers / tempting mistakes**
Trusting green CI alone; hiding the token but keeping admin scope; running faster to reduce drift.

**Scoring guidance**
Score: defects 4; safety controls 6.


### U05-Q12 — Artifact Review
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L4
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this generated repository: `README says production-ready; Dockerfile uses mutable base; CI uses floating action refs and write-all permissions; no SLO evidence; catalog owner is unresolved; team-owned app file marked platform-owned; template revision missing`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this generated repository: `README says production-ready; Dockerfile uses mutable base; CI uses floating action refs and write-all permissions; no SLO evidence; catalog owner is unresolved; team-owned app file marked platform-owned; template revision missing`.
```

**Model answer**
Defects: unsupported production-ready claim; mutable image; unpinned privileged CI dependency and broad permissions; generated SLO is not measured evidence; unresolved owner; wrong file-ownership classification; missing template provenance. Fix with verified digest/pinned refs, least-privilege CI, evidence labels, owner registry, corrected file boundaries and source revision. Generated artifacts remain starting points until runtime and operational checks pass.

**Reasoning**
A generated file is not proof of production readiness.

**Common wrong answers / tempting mistakes**
Accepting README wording; treating static policy pass as full production readiness; assuming catalog metadata is accurate without validation.

**Scoring guidance**
Score: defects 4; fixes 6.


### U05-Q13 — Incident
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L4
- **Question type:** incident
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC INCIDENT] A template update campaign across six repositories overwrites local CI changes in two repositories. One repo loses a permission restriction; another fails deployment. What now?

**Model answer**
Stop the bot and further campaign merges. Preserve PRs, base revisions, generated diff, template release, bot identity and CI logs. Revert or repair the two affected repos using known-good commits; verify least-privilege permissions and deployment state before resuming. Notify owners and classify the conflicts as platform-owned/team-owned boundary failure. Add conflict detection, preview-only first phase, canary repo per archetype, owner approval, mutation tests and rollback evidence. Re-run remaining repos individually.

**Reasoning**
The bot's update authority and file ownership are the failure boundary; mass re-run risks repeating damage.

**Common wrong answers / tempting mistakes**
Delete all branches; force-push the new template everywhere; assume tests catch permission regressions.

**Scoring guidance**
Score: containment 2; preserve evidence 2; repair/comms 2; prevention 4.


### U05-Q14 — Design
- **Scope:** Unit 5 — Scaffolding and software templates; template lifecycle; Copier primary and Cookiecutter comparison; parameters/derived values; trusted execution; generated files; platform/team ownership; tests/mutation; provenance; update campaigns; conflicts; bot safety; versioning/deprecation
- **Level:** L3
- **Question type:** design
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated scaffolding and software templates topic.
- **Suggested time:** 25 minutes

**Prompt**
Design an update-aware template programme for at least five synthetic consumer repositories.

**Model answer**
Strong outline: minimal validated parameter contract; immutable/pinned template releases; provenance and answers file; platform/team file ownership; deterministic generation matrix; positive/negative/mutation tests; update preview and conflict report; migration scripts only where tested; least-privilege bot; bounded concurrency; canary by archetype; owner-reviewed PRs; per-repo status and rollback; support/deprecation policy; adoption lag measured at repository/team level. Verify Copier flags and trust semantics against pinned official docs.

**Reasoning**
The update programme is a fleet governance workflow, not just a CLI command.

**Common wrong answers / tempting mistakes**
Auto-merging every update; no provenance; using one successful repo as proof for all archetypes.

**Scoring guidance**
Score 0–2 each: template contract, security, provenance, test strategy, update/conflict handling, bot controls, rollout/metrics (14).


---

## Unit 6 — Platform APIs with Crossplane compositions

**Lesson:** [`06-platform-apis-with-crossplane-compositions.md`](06-platform-apis-with-crossplane-compositions.md)  
**Coverage:** platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives

### U06-Q01 — Short Answer
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L1
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 6 minutes

**Prompt**
What makes a platform API a developer-facing contract rather than a provider-shaped infrastructure form?

**Model answer**
It expresses developer intent using a small, documented, validated and versioned schema, safe defaults, ownership and lifecycle semantics, status conditions and supported guarantees. It hides provider credentials and arbitrary implementation knobs while exposing enough information to debug outcomes. The platform chooses implementation details.

**Reasoning**
An API is judged by the consumer task and stability, not by how many provider fields it exposes.

**Common wrong answers / tempting mistakes**
Exposing raw provider config; calling any custom resource a good platform API; omitting status and lifecycle.

**Scoring guidance**
Score: intent 2; schema/guarantees 2; security/debuggability 1.


### U06-Q02 — Short Answer
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 6 minutes

**Prompt**
Compare a reconciliation control plane with a reviewed PR/pipeline provisioning workflow. When is each appropriate?

**Model answer**
A control plane continuously compares desired and actual state and reconciles drift; it suits long-lived declarative capabilities with clear controller ownership. A PR/pipeline workflow offers reviewable, auditable change steps and can be simpler for bounded or approval-heavy operations. Choose based on lifecycle, drift needs, risk, team skill and operational cost; not every request needs a controller.

**Reasoning**
Reconciliation and pipeline are different operational models, not simply fast and slow versions of the same tool.

**Common wrong answers / tempting mistakes**
Assuming controllers are always more self-service; assuming PRs are not automated; choosing Crossplane because it is available.

**Scoring guidance**
Score: correct distinction 2; criteria 2; trade-off 1.


### U06-Q03 — Short Answer
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 6 minutes

**Prompt**
What should a `ModelEndpoint` status contract communicate to a developer?

**Model answer**
It should distinguish accepted/validated, composed resources, observed readiness and usable serving outcome; expose safe conditions, reason/message, observed generation or equivalent freshness where verified, and diagnostic references. It must not expose credentials or secrets. A created Deployment alone does not prove model load, digest trust, inference readiness or correct routing.

**Reasoning**
Status is part of the developer API. It should explain what the platform knows and what it has not proven.

**Common wrong answers / tempting mistakes**
Only showing `Ready=True`; returning secret values; treating composed children as usable inference endpoint.

**Scoring guidance**
Score: states 2; safe diagnostics 2; limits 1.


### U06-Q04 — Mcq
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L2
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform apis with crossplane compositions principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A proposed Composition update changes the database resource and may cause replacement. What is the safest default before rollout?

**Options**
A. Apply the Composition because the YAML rendered successfully.
B. Assume the controller will safely replace the database without data impact.
C. Render/diff affected resources, inspect immutability/deletion, create fan-out impact report and use a ring/rollback plan.
D. Apply the revision to every tenant at once to reduce version skew.

**Model answer**
**Correct option: C.** Treat it as a potentially destructive change: render and diff all affected composed resources, inspect immutable fields and deletion semantics, build a fan-out impact report, keep Manual update policy where the source design specifies it, and roll out through rings with backup/restore and rollback plan. Verify exact Crossplane model/version before applying.

**Reasoning**
A treats a successful render as enough. B assumes replacement is harmless. D applies broadly before impact analysis.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: render is necessary but not sufficient. B: database replacement can cause data loss. D: no staged control.

**Scoring guidance**
Score: correct 1; safety reasoning 2.


### U06-Q05 — Mcq
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L3
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform apis with crossplane compositions principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A `DataEnvironment` request includes `team: risk-platform`, but the authenticated principal belongs to `analytics`. Which control must prevent cross-team provisioning?

**Options**
A. Derive or validate team authority from the authenticated principal and entitlement registry before reconciliation.
B. Accept any team string that passes schema validation.
C. Detect the mismatch only after composed child resources are created.
D. Record the mismatch in audit logs but allow provisioning to continue.

**Model answer**
**Correct option: A.** Authorization must derive or validate team identity from the authenticated principal and entitlement registry, not trust the tenant-supplied spec field. Schema validation may accept the string shape, but authorization must deny the mismatch before reconciliation.

**Reasoning**
B only validates syntax. C detects only after child resources exist. D is not a substitute for authorization.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
B: syntactic validity is not authority. C: late detection expands blast radius. D: audit does not prevent the action.

**Scoring guidance**
Score: correct 1; principal/trust-boundary rationale 2.


### U06-Q06 — Mcq
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L4
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform apis with crossplane compositions principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
Which statement about current Crossplane composition fields and CLI commands is appropriate if the selected release is not known?

**Options**
A. Choose a guessed API version and CLI flag from a remembered example.
B. Assume a previous Crossplane composition model is still recommended.
C. Assume all cloud-free providers support every resource type needed.
D. Mark exact versions/fields/flags `[VERIFY]`, record the release and consult official docs before use.

**Model answer**
**Correct option: D.** Treat exact API versions, fields, CLI flags, composition function and provider behavior as `[VERIFY]`. Record the installed release and consult official docs before using the example. The conceptual design question can be answered without relying on unverified syntax.

**Reasoning**
A fabricates version specificity. B assumes an old model remains current. C invents a compatibility guarantee.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: unsupported specificity. B: version-sensitive model changes. C: unsupported guarantee.

**Scoring guidance**
Score: correct 1; verification procedure 2.


### U06-Q07 — Artifact Interpretation
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L2
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Request: `apiVersion: platform.example.org/v1alpha1; kind: DataEnvironment; team: analytics; environment: dev; tier: development; size: small; ttl: 72h; needs.objectStorage: true`. Explain what this request expresses and three guarantees it does not make by itself.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Request: `apiVersion: platform.example.org/v1alpha1; kind: DataEnvironment; team: analytics; environment: dev; tier: development; size: small; ttl: 72h; needs.objectStorage: true`. Explain what this request expresses and three guarantees it does not make by itself.
```

**Model answer**
It expresses intent for an analytics development environment with small size, a 72-hour lifecycle and object-storage capability. It does not by itself prove entitlement, isolation, successful provisioning, bucket policy/retention, network reachability or usable readiness. Those require authenticated authorization, schema/policy validation, composition/controller behavior and evidence tests.

**Reasoning**
The request is declarative intent, not an execution receipt or security proof.

**Common wrong answers / tempting mistakes**
Assuming namespace creation proves isolation; assuming objectStorage true proves data durability; assuming the field schema is live/current without verification.

**Scoring guidance**
Score: intent 2; three non-guarantees 3.


### U06-Q08 — Artifact Interpretation
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] `ModelEndpoint` specifies registry `registry.example.invalid/models/fraud-model-v3`, immutable digest `sha256:aaaa...`, model card link, tier `standard`, min replicas 1, max replicas 3, target concurrency 20. What is the key integrity property and what remains to verify?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] `ModelEndpoint` specifies registry `registry.example.invalid/models/fraud-model-v3`, immutable digest `sha256:aaaa...`, model card link, tier `standard`, min replicas 1, max replicas 3, target concurrency 20. What is the key integrity property and what remains to verify?
```

**Model answer**
The immutable digest binds the request to a specific model artifact rather than a mutable tag. Verify the digest against trusted registry/provenance/signature policy, model card availability, serving runtime compatibility, resource/GPU capacity, readiness and prediction regression. `.invalid` and the digest are synthetic placeholders, not a real model.

**Reasoning**
The digest is an identity anchor but is not automatically proof of trusted publisher or safe model behavior.

**Common wrong answers / tempting mistakes**
Trusting the registry path alone; treating a syntactically valid SHA string as signature verification; assuming replicas guarantee capacity.

**Scoring guidance**
Score: digest property 2; three verifications 3.


### U06-Q09 — Artifact Interpretation
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Composition impact report: `tenant namespace: unchanged; service account: permissions widened; Postgres Cluster: immutable storage field changed; NetworkPolicy: default-deny removed`. Which changes require a stop before rollout and why?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Composition impact report: `tenant namespace: unchanged; service account: permissions widened; Postgres Cluster: immutable storage field changed; NetworkPolicy: default-deny removed`. Which changes require a stop before rollout and why?
```

**Model answer**
Stop the rollout. Widened controller/workload permissions can create privilege escalation; changing immutable storage may trigger replacement or unsupported mutation; removing default-deny changes tenant network isolation. These require explicit authorization/security review, destructive-impact analysis, restore/rollback plan and negative tests. A namespace unchanged does not make the update safe.

**Reasoning**
The risk is semantic and blast-radius based, not simply whether the YAML renders.

**Common wrong answers / tempting mistakes**
Rolling out because the namespace is unchanged; assuming Crossplane handles every immutable change safely; accepting NetworkPolicy removal as a performance optimization without threat review.

**Scoring guidance**
Score: identify all three 3; reasoning 2.


### U06-Q10 — Artifact Review
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L2
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this API schema: `team: free string; providerConfig: user supplied; adminPassword: plain string; size: any string; no descriptions; no required fields; no immutable data identity; status contains connectionSecretData`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this API schema: `team: free string; providerConfig: user supplied; adminPassword: plain string; size: any string; no descriptions; no required fields; no immutable data identity; status contains connectionSecretData`.
```

**Model answer**
Defects: caller-controlled team/tenant; provider credential selector exposure; plaintext password field; unbounded size; absent required/enum/validation/defaults; no field documentation; no immutability/migration semantics; secret leakage in status. Fix with authenticated entitlement-derived identity, platform-owned provider credentials, secret references, enums/limits, required schema and descriptions, explicit immutable fields and secret-safe status. Exact CRD/CEL syntax is `[VERIFY]`.

**Reasoning**
The API exposes implementation and privilege rather than safe intent.

**Common wrong answers / tempting mistakes**
Only changing password name; relying on UI validation; exposing secrets because the user owns the resource.

**Scoring guidance**
Score: defects 4; fixes 6.


### U06-Q11 — Artifact Review
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L3
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this Composition rollout: `defaultCompositionUpdatePolicy: Automatic; provider package floats; controller ClusterRole is *; no render tests; no RBAC negative tests; database deletion policy is implicit; every XR updated at once`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this Composition rollout: `defaultCompositionUpdatePolicy: Automatic; provider package floats; controller ClusterRole is *; no render tests; no RBAC negative tests; database deletion policy is implicit; every XR updated at once`.
```

**Model answer**
Defects: uncontrolled automatic update; floating provider dependency; wildcard controller permissions; no render/golden tests; no authorization negative tests; ambiguous destructive semantics; no impact/fan-out report; no canary rings or rollback/restore. Fix with pinned package, explicit update policy, scoped RBAC, render and integration tests, explicit deletion contract, staged rollout and evidence. Verify exact fields/semantics for selected Crossplane version.

**Reasoning**
The composition is privileged code that can fan out across all consumer resources.

**Common wrong answers / tempting mistakes**
Assuming automatic updates reduce toil; assuming ClusterRole wildcard is temporary; rolling back without considering provider-managed external resources.

**Scoring guidance**
Score: defects 4; corrections 6.


### U06-Q12 — Artifact Review
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L4
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this status object: `Ready=True; message=all done; connectionSecretData={username,password}; no child conditions; no observed revision; no readiness probe; no owner/support link`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this status object: `Ready=True; message=all done; connectionSecretData={username,password}; no child conditions; no observed revision; no readiness probe; no owner/support link`.
```

**Model answer**
Defects: false-ready ambiguity; secret disclosure; no stage/child conditions; no observed revision/freshness; no usable endpoint probe; no owner/support link. Fix with staged conditions and reason codes, redacted diagnostics, safe references, readiness and inference smoke checks, owner/catalog link, and an explicit distinction between composed and usable-ready.

**Reasoning**
Status is an API contract and a security surface.

**Common wrong answers / tempting mistakes**
Exposing credentials to make debugging easy; adding only a longer message; treating child resource creation as readiness.

**Scoring guidance**
Score: defects 4; corrections 6.


### U06-Q13 — Incident
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L4
- **Question type:** incident
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC INCIDENT] A new Composition revision is promoted and three tenant databases begin replacement. A `ModelEndpoint` also loses its serving NetworkPolicy. What is the response?

**Model answer**
Halt further promotion and preserve Composition revision, provider/controller logs, XR/child state, audit and release evidence. Identify affected tenants/resources and whether replacement has begun; do not blindly delete claims or roll back if that causes further destructive reconciliation. Apply a known-safe prior revision or targeted mitigation only after checking semantics; restore from verified backups if data loss occurred. Reinstate network policy via a reviewed path and verify tenant connectivity boundaries. Communicate scope and recovery; add immutable-field and policy-diff gates, fan-out report, canary and restore drill.

**Reasoning**
The first action is containment and evidence, not automatic rollback. Controller reconciliation can make a rollback destructive too.

**Common wrong answers / tempting mistakes**
Deleting all XRs; applying a broad wildcard policy; assuming previous revision instantly restores external data.

**Scoring guidance**
Score: containment 2; evidence/scope 2; mitigation/recovery/comms 3; prevention 3.


### U06-Q14 — Design
- **Scope:** Unit 6 — Platform APIs with Crossplane compositions; platform API contract; reconciliation vs pipeline; API abstractions; DataEnvironment/PostgresDatabase/ObjectBucket/ModelEndpoint; schema/defaults/CEL; Crossplane v2/version verification; composition and function boundaries; controller RBAC; status/readiness; testing; deletion; rollout and alternatives
- **Level:** L3
- **Question type:** design
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform apis with crossplane compositions topic.
- **Suggested time:** 25 minutes

**Prompt**
Design a `PostgresDatabase` platform API and defend whether Crossplane, Terraform-via-PR or Helm-as-API is appropriate.

**Model answer**
Strong outline: expose tier/size/backup class/pooler intent, derive tenant from trusted identity, hide credentials/provider config, define ownership/retention/immutability/status. Use Crossplane if continuous reconciliation and controller ownership justify it and cloud-free provider semantics are verified; Terraform-via-PR if reviewed change history and bounded operations are more important; Helm-as-API only when a chart contract adequately models lifecycle and controller semantics are not needed. Include schema/CEL validation, render/golden tests, authorization and admission negative tests, readiness/connectivity, backups/restore, deletion semantics, versioning and rollout rings.

**Reasoning**
No tool is universally correct; choose based on lifecycle, failure mode, team capability and operational burden.

**Common wrong answers / tempting mistakes**
Choosing Crossplane for fashion; treating Helm release success as data recoverability; exposing provider secrets in the API.

**Scoring guidance**
Score 0–2 each: user contract, options/decision, security, lifecycle/deletion, test/evidence, SRE, migration (14).


---

## Unit 7 — Multi-tenancy, isolation, and tenant onboarding

**Lesson:** [`07-multi-tenancy-isolation-and-tenant-onboarding.md`](07-multi-tenancy-isolation-and-tenant-onboarding.md)  
**Coverage:** tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance

### U07-Q01 — Short Answer
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L1
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 6 minutes

**Prompt**
Why is a tenant not synonymous with a Kubernetes namespace?

**Model answer**
A tenant is the platform/business identity and lifecycle contract that owns workloads, access, data, cost and support. A namespace is one implementation scope. Identity-provider group, catalog Group, tenant key, namespace, cost center, business owner and data steward are distinct typed concepts with different authority and lifecycle.

**Reasoning**
Collapsing identifiers creates authorization, routing and billing errors.

**Common wrong answers / tempting mistakes**
Using namespace as the only tenant identity; treating cost center as authorization; assuming namespace isolation equals hard multi-tenancy.

**Scoring guidance**
Score: definition 2; distinction examples 2; consequence 1.


### U07-Q02 — Short Answer
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 6 minutes

**Prompt**
Distinguish soft and hard multi-tenancy and explain why the threat model determines the choice.

**Model answer**
Soft tenancy assumes tenants share an organizational trust model and uses layered controls to reduce accidental or low-sophistication access. Hard tenancy treats tenants as potentially adversarial and needs stronger boundaries for kernel, control plane, identity, network and data—often separate clusters or stronger isolation. No single model is universally secure; classify assets, adversaries and trust tier first.

**Reasoning**
Namespace policy cannot create a separate kernel or control plane.

**Common wrong answers / tempting mistakes**
Calling namespaces hard isolation; assuming cluster-per-tenant is always required; choosing model from cost alone.

**Scoring guidance**
Score: definitions 2; threat-model dependency 2; trade-off 1.


### U07-Q03 — Short Answer
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 6 minutes

**Prompt**
Describe the minimum evidence for an isolation test to count as a pass.

**Model answer**
Record authenticated principal, source tenant, target tenant/resource, attempted action, expected result, observed result, policy/plugin/cluster version, timestamp and safe evidence location. A negative test passes only if the forbidden action is denied for the expected reason; positive tests must prove permitted workflows still work. Mock tests prove only local decision logic.

**Reasoning**
A manifest existing is not evidence of enforcement. Positive and negative paths are both needed.

**Common wrong answers / tempting mistakes**
Counting policy YAML as a test; calling a timeout a denial; treating a mock as proof of CNI or kernel isolation.

**Scoring guidance**
Score: evidence fields 3; positive/negative distinction 1; fidelity caveat 1.


### U07-Q04 — Mcq
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L2
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the multi-tenancy, isolation, and tenant onboarding principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
Which identity should authorize a tenant's request to create an environment?

**Options**
A. Trust the tenant value supplied in the request body.
B. Authorize from the authenticated principal and authoritative entitlement mapping.
C. Use the cost-center label as the access-control identity.
D. Trust the catalog display owner string without authorization checks.

**Model answer**
**Correct option: B.** The authenticated principal and authoritative entitlement mapping should determine the team/tenant authority. Tenant-supplied labels or namespace strings are claims to validate, not the source of authority.

**Reasoning**
A trusts untrusted request data. C uses billing metadata as identity. D trusts catalog display data without authorization semantics.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: caller can spoof. C: cost allocation is not access control. D: catalog is a projection and may be stale.

**Scoring guidance**
Score: correct 1; identity reasoning 2.


### U07-Q05 — Mcq
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L3
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the multi-tenancy, isolation, and tenant onboarding principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A namespace has ResourceQuota, NetworkPolicy and RoleBindings. What conclusion is justified?

**Options**
A. Declare hard isolation because the namespace has quotas and NetworkPolicy.
B. Remove all controls because namespaces are never useful.
C. Treat the controls as useful layers but verify identity, admission, storage, secrets, ingress, registry, observability and control-plane boundaries.
D. Assume ResourceQuota alone prevents cross-tenant data access.

**Model answer**
**Correct option: C.** These are useful layers, but the namespace is not a hard boundary by itself. Verify identity, admission, storage, secrets, ingress, registry/CI, observability and control-plane access; consider kernel/control-plane trust requirements.

**Reasoning**
A overclaims hard isolation. B dismisses useful controls. D assumes quota alone prevents data access.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: controls reduce risk but don't create separate kernel/control plane. B: layered controls matter. D: quota is resource control, not data authorization.

**Scoring guidance**
Score: correct 1; layered isolation explanation 2.


### U07-Q06 — Mcq
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L4
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the multi-tenancy, isolation, and tenant onboarding principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A tenant offboarding request arrives, but the data steward has not resolved a retention hold. What should happen?

**Options**
A. Delete the namespace immediately because the offboarding request exists.
B. Retain credentials for convenience until someone asks for revocation.
C. Ignore the hold and finish deletion because TTL/offboarding is automatic.
D. Pause destructive deletion at the retention gate, preserve evidence and resolve the approved data-owner/steward decision.

**Model answer**
**Correct option: D.** Pause destructive deletion at the retention gate, preserve data and audit evidence, revoke or reduce access according to the approved process, notify owner/steward, and keep the workflow in a blocked state until the hold decision is resolved.

**Reasoning**
A treats offboarding as immediate delete. B risks unauthorized access or data loss. C silently ignores governance.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: deletion may violate retention policy. B: namespace deletion is not a complete lifecycle. C: a hold is a hard decision gate, not a warning.

**Scoring guidance**
Score: correct 1; data safety reasoning 2.


### U07-Q07 — Artifact Interpretation
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L2
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Tenant map: `team-a→analytics→tn-team-a→CC-SYNTH-ANALYTICS-01`; `team-b→ml-research→tn-team-b→CC-SYNTH-ML-RESEARCH-01`; `team-c→risk-platform→tn-team-c→CC-SYNTH-RISK-PLATFORM-01`. Why must these fields remain distinct?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Tenant map: `team-a→analytics→tn-team-a→CC-SYNTH-ANALYTICS-01`; `team-b→ml-research→tn-team-b→CC-SYNTH-ML-RESEARCH-01`; `team-c→risk-platform→tn-team-c→CC-SYNTH-RISK-PLATFORM-01`. Why must these fields remain distinct?
```

**Model answer**
They represent tenant lifecycle key, organization/team identity, namespace implementation and financial allocation. They may change independently and have different authorities. Authorization should use authenticated identity/entitlement; namespace is a target scope; cost center is showback; catalog owner is a relationship. Mapping must be explicit and validated.

**Reasoning**
String equality is not semantic identity. The map is a synthetic teaching contract.

**Common wrong answers / tempting mistakes**
Using cost center for RBAC; inferring tenant from namespace prefix alone; merging identity and catalog group.

**Scoring guidance**
Score: four distinctions 4; consequence 1.


### U07-Q08 — Artifact Interpretation
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Isolation report for tenant A→B: `secret read denied`; `cross-namespace service connect denied`; `foreign PVC mount denied`; `tenant label patch denied`; `cross-tenant hostname claim denied`; `shared registry pull allowed`; `platform metrics query returns only aggregate team metrics`. What needs review before calling isolation complete?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Isolation report for tenant A→B: `secret read denied`; `cross-namespace service connect denied`; `foreign PVC mount denied`; `tenant label patch denied`; `cross-tenant hostname claim denied`; `shared registry pull allowed`; `platform metrics query returns only aggregate team metrics`. What needs review before calling isolation complete?
```

**Model answer**
The reported tests cover selected controls, but the suite's scope and positive paths must be checked. Shared registry pull may be an intended shared service if image access and provenance are authorized; it needs explicit policy. Confirm all required layers and at least 25 tests per tenant pair as the capstone requirement, include reverse direction and positive permitted paths, test storage/data/ingress/CI/control-plane, version evidence and limitations. Do not call this proof against kernel adversaries.

**Reasoning**
Isolation is a matrix of principals, targets and actions; a short report cannot establish all possible behavior.

**Common wrong answers / tempting mistakes**
Assuming every allowed action is a leak; assuming six denials prove all isolation; ignoring reverse direction or positive tests.

**Scoring guidance**
Score: scope assessment 2; allowed registry interpretation 1; missing coverage/evidence 2.


### U07-Q09 — Artifact Interpretation
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] `admin-lite` Role allows get/list pods and logs, create/delete Jobs in one namespace, patch labels on Namespace, and create RoleBindings. Identify the highest-risk permissions and safer alternatives.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] `admin-lite` Role allows get/list pods and logs, create/delete Jobs in one namespace, patch labels on Namespace, and create RoleBindings. Identify the highest-risk permissions and safer alternatives.
```

**Model answer**
Patching namespace labels can bypass policy selectors if labels are trusted; creating RoleBindings can grant privilege escalation; deleting Jobs may disrupt workloads. Remove protected-label mutation and RoleBinding creation from delegated role; use an approved workflow for scoped Job operations and read-only diagnostics, with audit and tests.

**Reasoning**
Delegated admin should enable bounded operations without creating new authority.

**Common wrong answers / tempting mistakes**
Focusing only on pod list; allowing namespace label patch; granting RoleBinding create because tenant is namespace admin.

**Scoring guidance**
Score: risks 3; alternatives 2.


### U07-Q10 — Artifact Review
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L2
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this tenancy baseline: `namespace per team; allow-all NetworkPolicy; default service account; no ResourceQuota; secrets readable by all namespace users; tenant label mutable by tenant admin; no registry restriction`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this tenancy baseline: `namespace per team; allow-all NetworkPolicy; default service account; no ResourceQuota; secrets readable by all namespace users; tenant label mutable by tenant admin; no registry restriction`.
```

**Model answer**
Defects: namespace alone overclaimed; no default-deny network; weak identity/service account; no resource bounds; broad secret access; tenant label tampering; no image registry/supply-chain restriction; missing storage/ingress/observability/control-plane layers and positive/negative tests. Fix with authenticated tenant mapping, least-privilege RBAC, default-deny plus explicit allow, quotas, secret scoping/workload identity, protected labels, registry policy and evidence suite.

**Reasoning**
Isolation is layered across control plane, compute, network, storage, secrets, supply chain and shared services.

**Common wrong answers / tempting mistakes**
Assuming namespace boundary is sufficient; treating NetworkPolicy as identity; adding a label without protecting its writer.

**Scoring guidance**
Score: defects 4; corrections 6.


### U07-Q11 — Artifact Review
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L3
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this offboarding record: `tenant=team-b; action=delete namespace now; database export=not needed; hold=unknown; credentials=keep for 30 days; object bucket=not inventoried; audit record=none`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this offboarding record: `tenant=team-b; action=delete namespace now; database export=not needed; hold=unknown; credentials=keep for 30 days; object bucket=not inventoried; audit record=none`.
```

**Model answer**
Defects: hold unknown is not a pass; no data-owner/export decision; database/object-store resources not inventoried; credentials retained without justification and revocation plan; namespace deletion may orphan external resources; no dependency order; no post-delete/orphan check; no audit. Fix with owner/steward approval, export/retention decision, access revocation, dependency inventory, ordered deprovision, orphan verification and immutable audit evidence.

**Reasoning**
Offboarding is a data lifecycle and identity event, not namespace cleanup.

**Common wrong answers / tempting mistakes**
Delete namespace first and investigate later; retain credentials as a convenience; assume object storage is namespaced.

**Scoring guidance**
Score: defects 4; safe sequence 6.


### U07-Q12 — Artifact Review
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L4
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this isolation test report: `All 25 tests PASS. Test principal omitted. Only mock policy engine used. No target resource IDs. Timeout is recorded as DENIED. No policy version. No positive tests. Report claims hard multi-tenancy proven.`

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this isolation test report: `All 25 tests PASS. Test principal omitted. Only mock policy engine used. No target resource IDs. Timeout is recorded as DENIED. No policy version. No positive tests. Report claims hard multi-tenancy proven.`
```

**Model answer**
Defects: no principal/source identity; no target IDs/action evidence; mock-only fidelity overstated; timeout is not proof of denial; missing policy version/time; no positive permitted paths; insufficient detail for reproduction; claim of hard multi-tenancy is unsupported. Fix structured evidence fields, assert explicit denial reason, run bounded own-lab integration where available, include positive and negative matrix and state the residual kernel/control-plane limitation.

**Reasoning**
Test count without trustworthy evidence is a vanity number.

**Common wrong answers / tempting mistakes**
Accepting count; treating timeout as deny; equating policy model with live enforcement.

**Scoring guidance**
Score: defects 4; corrections and caveat 6.


### U07-Q13 — Incident
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L4
- **Question type:** incident
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC INCIDENT] A tenant-isolation canary reports that `team-a` can resolve and reach a service intended only for `team-b` during a platform rollout. What is the safe response?

**Model answer**
Halt the relevant rollout and preserve principal, source/destination, policy revision, network logs, cluster context and timestamps. Determine whether reachability is DNS-only or actual authorized data/service access; do not run broader scans outside the disposable lab. Contain with a targeted policy/route mitigation after verifying its impact, assess affected tenants/data and credentials, notify incident roles/owners, retest both denied and permitted paths, and restore only after the canary suite passes. Follow with root-cause, policy-selection and label-integrity tests.

**Reasoning**
The first objective is to bound and contain a potential trust-boundary failure while preserving evidence. Blind global deny can also break legitimate service paths.

**Common wrong answers / tempting mistakes**
Ignore because canary is synthetic; delete all namespaces; apply cluster-wide deny without dependency analysis.

**Scoring guidance**
Score: containment 2; evidence/localization 2; mitigation/comms/recovery 3; prevention 3.


### U07-Q14 — Design
- **Scope:** Unit 7 — Multi-tenancy, isolation, and tenant onboarding; tenant identity and trust tiers; soft/hard tenancy; threat model; layered isolation; identity/RBAC; network/compute/storage/secrets; onboarding gates; offboarding/retention/orphans; delegated admin; noisy neighbors; canary assurance
- **Level:** L3
- **Question type:** design
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated multi-tenancy, isolation, and tenant onboarding topic.
- **Suggested time:** 25 minutes

**Prompt**
Choose a tenancy model for three trust tiers: internal analytics teams, ML research teams sharing sensitive model artifacts, and a high-sensitivity risk workload.

**Model answer**
Strong outline: define adversaries/assets first; use shared namespaces/cluster only where trust and controls justify soft tenancy; add stronger node/control-plane/data boundaries for sensitive tiers; consider separate cluster or stronger isolation for high-sensitivity risk if threat model requires it. Specify identity, RBAC, network, compute, storage, secrets, registry/CI, ingress, observability and cost controls. Require onboarding isolation gate, continuous canary, offboarding retention/export/revoke/orphan process and tenant incident runbook. Cost and operational complexity are explicit trade-offs.

**Reasoning**
The choice is tier-specific and threat-model-driven; namespace per team is not a universal security answer.

**Common wrong answers / tempting mistakes**
One tenancy model for all; assuming cluster-per-tenant automatically solves all risks; using labels as the only isolation mechanism.

**Scoring guidance**
Score 0–2 each: threat model, tier choice, layered controls, onboarding/offboarding, evidence tests, operations, cost/trade-off (14).


---

## Unit 8 — Platform SLOs, adoption metrics, and developer experience

**Lesson:** [`08-platform-slos-adoption-metrics-and-developer-experience.md`](08-platform-slos-adoption-metrics-and-developer-experience.md)  
**Coverage:** platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards

### U08-Q01 — Short Answer
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L1
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 6 minutes

**Prompt**
Distinguish an SLI, SLO and KPI in the context of environment provisioning.

**Model answer**
An SLI is a measured indicator of service behavior, such as the proportion of valid entitled requests that reach usable-ready within a defined window. An SLO is the target for that SLI over a time window. A KPI is a broader decision metric for platform/product outcomes, such as supported-path coverage or support load. Define numerator, denominator, window, population and exclusions.

**Reasoning**
A platform needs user-visible reliability measures, not only component uptime.

**Common wrong answers / tempting mistakes**
Calling the target an SLI; calling every dashboard number an SLO; using request acceptance as usable readiness.

**Scoring guidance**
Score: definitions 3; complete provisioning example 2.


### U08-Q02 — Short Answer
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 6 minutes

**Prompt**
Why must adoption metrics define their denominator and eligibility population?

**Model answer**
A ratio is uninterpretable if eligible teams/services, time window, exclusions and event semantics are unclear. A denominator change can create apparent adoption improvement without any new consumer. Version changes, missing events and duplicate events must be handled and documented.

**Reasoning**
Metric contracts prevent definition drift and misleading comparisons.

**Common wrong answers / tempting mistakes**
Using all repos as denominator when only some are eligible; silently excluding non-adopters; comparing changed definitions without restatement.

**Scoring guidance**
Score: denominator reasoning 2; contract fields 2; confounder example 1.


### U08-Q03 — Short Answer
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 6 minutes

**Prompt**
Explain why correlation between golden-path adoption and DORA outcomes does not prove causal impact.

**Model answer**
Teams that adopt may differ in maturity, workload, staffing, release cadence or selection into the path. Concurrent changes and event quality also confound comparisons. Use explicit cohorts, pre/post definitions, sensitivity and qualitative evidence; difference-in-differences intuition can help but depends on assumptions. Do not claim causality from a simple correlation.

**Reasoning**
Selection bias and confounding can create apparent differences even when the path did not cause them.

**Common wrong answers / tempting mistakes**
Assuming adopters are representative; using a before/after chart without controls; claiming a causal uplift from synthetic data.

**Scoring guidance**
Score: two confounders 2; appropriate analysis/caveat 2; synthetic limitation 1.


### U08-Q04 — Mcq
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L2
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform slos, adoption metrics, and developer experience principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A provisioning dashboard reports 99% success because 99% of requests were accepted by the API. The user-facing readiness probe often fails later. What is the best correction?

**Options**
A. Define success as the advertised usable outcome and track accepted, reconciled and usable-ready stages separately.
B. Count every accepted request as success.
C. Change the denominator to exclude failures and late requests.
D. Use API availability as a substitute for usable provisioning.

**Model answer**
**Correct option: A.** Define success as the advertised usable outcome and track stage transitions separately. Keep accepted, reconciled and usable-ready distinct; add time-to-ready and failure-stage metrics.

**Reasoning**
B hides the failure. C mixes stages. D uses a component signal rather than developer outcome.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
B: false success. C: denominators/stages become ambiguous. D: API availability is not usable provisioning.

**Scoring guidance**
Score: correct 1; outcome reasoning 2.


### U08-Q05 — Mcq
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L3
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform slos, adoption metrics, and developer experience principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A team wants to publish a dashboard ranking developers by time-to-first-deploy. Which choice aligns with the course's ethics rule?

**Options**
A. Publish a public leaderboard because transparency makes it fair.
B. Rank developers within each team instead of across the organization.
C. Replace names with stable employee IDs and retain the same individual ranking.
D. Reject individual ranking and use aggregated service/team journey outcomes with privacy controls.

**Model answer**
**Correct option: D.** Do not rank individuals. Measure aggregated service/team journey outcomes with minimization, retention and transparency; use local n=1 measurements only as local evidence.

**Reasoning**
A is explicit ranking. B is still identifiable at small team level if linked to person. C does not remove individual surveillance if raw IDs are retained.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: prohibited. B: small cohorts can re-identify. C: hiding names is not sufficient minimization.

**Scoring guidance**
Score: correct 1; privacy rationale 2.


### U08-Q06 — Mcq
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L4
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform slos, adoption metrics, and developer experience principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A platform SLO is burning rapidly due to failed provisioning. What should the platform team do about a planned non-emergency platform rollout?

**Options**
A. Continue the planned non-emergency rollout because the dashboard is only informational.
B. Rollback immediately without diagnosis or checking rollback risk.
C. Apply the documented error-budget policy, defer risky changes, investigate the user-visible SLI and communicate; handle emergencies through an explicit risk path.
D. Ignore the burn because the platform is an internal service.

**Model answer**
**Correct option: C.** Apply the defined error-budget policy: halt or defer risky changes, investigate and restore the user-visible SLI, communicate, and resume only under documented criteria. Emergency security changes require a separate risk decision and mitigation plan.

**Reasoning**
A ignores reliability evidence. B blindly rolls back without diagnosis. D treats the error budget as a dashboard decoration.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: violates SLO-based change discipline. B: rollback may worsen or not address root cause. D: SLO must inform decisions.

**Scoring guidance**
Score: correct 1; error-budget rationale 2.


### U08-Q07 — Artifact Interpretation
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L2
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] SLO: `usable provisioning success = valid entitled requests reaching usable-ready within 30 minutes / all valid entitled requests in the window`. In one day: 90 valid requests, 81 usable-ready within 30 minutes, 5 ready after 30 minutes, 4 failed. Calculate the SLI and explain the treatment of late successes.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] SLO: `usable provisioning success = valid entitled requests reaching usable-ready within 30 minutes / all valid entitled requests in the window`. In one day: 90 valid requests, 81 usable-ready within 30 minutes, 5 ready after 30 minutes, 4 failed. Calculate the SLI and explain the treatment of late successes.
```

**Model answer**
SLI = 81/90 = 90%. The five late successes are not successes within the defined 30-minute objective, though they may be eventual successes. Four failures also miss the objective. Keep stage/failure and eventual readiness metrics separately; report sample/window and synthetic status.

**Reasoning**
The denominator is all valid entitled requests; the numerator is those meeting both readiness and latency conditions.

**Common wrong answers / tempting mistakes**
Using 86/90; excluding failures from denominator; reporting 90% as an industry benchmark.

**Scoring guidance**
Score: calculation 2; late-success treatment 2; caveat 1.


### U08-Q08 — Artifact Interpretation
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Six-month adoption table shows eligible services 20→40; golden-path services 10→18; coverage 50%→45%. A dashboard instead shows path repos 10→18 and claims adoption improved 80%. Explain the error.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Six-month adoption table shows eligible services 20→40; golden-path services 10→18; coverage 50%→45%. A dashboard instead shows path repos 10→18 and claims adoption improved 80%. Explain the error.
```

**Model answer**
Coverage is 10/20=50% then 18/40=45%, so it declined. The dashboard's 80% uses an inconsistent or unexplained denominator. It may count only repositories already classified as active/eligible, omit new services or change eligibility. Rebuild from a versioned denominator contract and audit missing/duplicate events and exclusions.

**Reasoning**
Counts alone are not rates. Eligibility and definition changes can reverse the conclusion.

**Common wrong answers / tempting mistakes**
Calling 18>10 proof of adoption increase; using the 80% without denominator; assuming new services are ineligible without evidence.

**Scoring guidance**
Score: calculation 2; denominator diagnosis 2; next checks 1.


### U08-Q09 — Artifact Interpretation
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Survey: 12 responses from 80 invited teams; 10 report positive experience. Calculate response rate and positive share among respondents. What cannot be inferred?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Survey: 12 responses from 80 invited teams; 10 report positive experience. Calculate response rate and positive share among respondents. What cannot be inferred?
```

**Model answer**
Response rate = 12/80 = 15%. Positive share among respondents = 10/12 ≈ 83.3%. It cannot be generalized to all 80 teams without assumptions about nonresponse; small sample and self-selection matter. Report counts, denominator, collection window, question wording and uncertainty; do not claim 83.3% of all teams are satisfied.

**Reasoning**
The respondent share is not the population share. The denominator must be named.

**Common wrong answers / tempting mistakes**
Calling it 83.3% of all teams; ignoring nonresponse; using a percentage without sample size.

**Scoring guidance**
Score: calculations 2; inference limit 2; reporting detail 1.


### U08-Q10 — Artifact Review
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L2
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this metric event: `event=deploy; user_email=alice@example; engineer_id=123; commit_count=17; deploy_count=9; manager_rank=1; timestamp=...`. It is used for a productivity leaderboard.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this metric event: `event=deploy; user_email=alice@example; engineer_id=123; commit_count=17; deploy_count=9; manager_rank=1; timestamp=...`. It is used for a productivity leaderboard.
```

**Model answer**
Defects: individual identifiers/email; individual activity counts; ranking/manager field; purpose is productivity surveillance; no minimization/retention/consent/transparency; events may not represent user outcome; no aggregation or access control. Remove individual fields, collect only necessary service/team-level journey events, define retention and purpose, aggregate with small-cell protections and fail schema validation when individual-level fields appear.

**Reasoning**
The source explicitly prohibits individual developer rankings and requires a scanner for individual-level fields.

**Common wrong answers / tempting mistakes**
Pseudonymizing email but retaining rank; hiding the dashboard from developers; retaining raw fields indefinitely for debugging.

**Scoring guidance**
Score: defects 4; privacy-safe redesign 6.


### U08-Q11 — Artifact Review
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L3
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this SLO: `portal uptime 99.9% monthly; success = HTTP 200 from homepage; no catalog freshness, search or fallback; no owner; no error-budget action`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this SLO: `portal uptime 99.9% monthly; success = HTTP 200 from homepage; no catalog freshness, search or fallback; no owner; no error-budget action`.
```

**Model answer**
Defects: uptime alone misses the developer journey; homepage 200 does not prove catalog search, ownership accuracy or critical workflows; no defined population/SLI window/measurement source; no fallback or dependency boundary; no owner; no error-budget decision policy. Add task-based portal/catalog SLIs, freshness, usable search/discovery, static fallback, ownership and alert/runbook; define exclusions and change policy.

**Reasoning**
The portal may be up while catalog data is stale or actions fail. Measure the user outcome.

**Common wrong answers / tempting mistakes**
Increasing uptime target; counting frontend health as all capability health; assuming portal outage equals platform outage.

**Scoring guidance**
Score: defects 4; corrected SLI and operations 6.


### U08-Q12 — Artifact Review
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L4
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this adoption analysis: `adoption rose from 40% to 65%; we forced all teams to migrate in the second month; non-adopters were excluded; denominator changed from eligible services to active repos; deploy count increased; therefore the platform caused a 25-point productivity gain.`

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this adoption analysis: `adoption rose from 40% to 65%; we forced all teams to migrate in the second month; non-adopters were excluded; denominator changed from eligible services to active repos; deploy count increased; therefore the platform caused a 25-point productivity gain.`
```

**Model answer**
Defects: forced migration confounds voluntary adoption; exclusion of non-adopters creates survivorship bias; denominator changed; deploy count is a proxy/Goodhart risk; no baseline/cohort equivalence or confounder analysis; causal claim unsupported; no uncertainty or qualitative research; productivity claim violates evidence rule. Restate metric with stable denominator, separate mandate cohorts, inspect event quality, pair adoption with reliability/DX and support, and use cautious causal design.

**Reasoning**
The claim combines measurement-definition drift, selection bias and an unsupported outcome inference.

**Common wrong answers / tempting mistakes**
Repeating the 25-point claim; adding a larger dashboard; assuming more deploys means better outcomes.

**Scoring guidance**
Score: defects 4; correction 6.


### U08-Q13 — Incident
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L4
- **Question type:** incident
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC INCIDENT] Provisioning success SLI burns through its defined error budget during a policy rollout. Product teams cannot create usable environments; portal uptime remains green. What should happen?

**Model answer**
Freeze the non-emergency policy rollout and further changes under the documented error-budget policy; preserve request, CI/admission, controller and readiness traces. Localize whether failures occur at schema, entitlement, CI policy, admission, quota/capacity or controller stage. Mitigate with a reviewed policy rollback/targeted exception only after checking blast radius and security implications. Communicate degraded self-service and fallback. Verify usable-ready recovery, update alert/runbook and add regression fixtures. Portal uptime is not a counterargument because the user outcome is failing.

**Reasoning**
The SLO measures usable provisioning, not homepage availability. Security policy rollback must be evidence-based.

**Common wrong answers / tempting mistakes**
Ignore because portal uptime is green; disable all policies; continue rollout to finish the release.

**Scoring guidance**
Score: decision 2; evidence/localization 2; safe mitigation/comms 3; prevention 3.


### U08-Q14 — Design
- **Scope:** Unit 8 — Platform SLOs, adoption metrics, and developer experience; platform SLIs/SLOs/error budget; usable developer journey; adoption denominator and definitions; synthetic dataset/data quality; DORA segmentation/confounders; surveys/interviews/usability; privacy; Goodhart; cost/ROI uncertainty; decision dashboards
- **Level:** L3
- **Question type:** design
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform slos, adoption metrics, and developer experience topic.
- **Suggested time:** 25 minutes

**Prompt**
Design a privacy-preserving developer-experience measurement plan for the platform's first six months.

**Model answer**
Strong outline: define platform user journeys and hypotheses; establish local n=1 manual baseline and synthetic data separately; instrument minimal service/team events with stable event semantics; define eligible population and denominators; platform SLOs for usable outcomes; adoption funnel/version spread; support themes; usability task time/errors and qualitative interviews with real users only when actually available. Add data-quality checks, missing/duplicate handling, retention, aggregation/small-cell protections, transparency, individual-field scanner, confounder register and quarterly continue/kill/invest decisions. Do not claim causality from correlation.

**Reasoning**
Measurement should improve platform decisions and respect people. Synthetic fixtures test analysis logic only.

**Common wrong answers / tempting mistakes**
Individual leaderboards; deploy-count goals; claiming causal productivity lift from synthetic metrics.

**Scoring guidance**
Score 0–2 each: outcome framing, definitions, data quality, privacy, research, causal caution, decision loop (14).


---

## Unit 9 — Platform governance, deprecation, and versioning

**Lesson:** [`09-platform-governance-deprecation-and-versioning.md`](09-platform-governance-deprecation-and-versioning.md)  
**Coverage:** artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset

### U09-Q01 — Short Answer
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L1
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 6 minutes

**Prompt**
Why is SemVer insufficient unless an artifact has a declared compatibility contract?

**Model answer**
SemVer communicates change intent only relative to a defined public contract. A template, API, policy bundle, workflow, image, chart or catalog schema has different compatibility semantics. Without specifying consumer-visible behavior and tests, a version number cannot prove that a consumer will continue to work.

**Reasoning**
Version labels are metadata; compatibility evidence comes from contract and tests.

**Common wrong answers / tempting mistakes**
Assuming every artifact follows the same API SemVer rules; assuming a patch number can never break consumers; assuming a major version automatically provides migration.

**Scoring guidance**
Score: contract 2; artifact differences 2; evidence distinction 1.


### U09-Q02 — Short Answer
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 6 minutes

**Prompt**
Distinguish deprecation, end-of-life (EOL), and removal.

**Model answer**
Deprecation announces that an artifact/contract is discouraged and provides replacement, owner, timeline and migration support. EOL ends normal support/maintenance under a declared policy. Removal actually withdraws the capability or version. These may be separate states and dates; a deprecated API may remain served temporarily.

**Reasoning**
The distinction allows consumers to plan and makes support expectations explicit.

**Common wrong answers / tempting mistakes**
Using the terms interchangeably; removing immediately after warning; calling EOL a security guarantee.

**Scoring guidance**
Score: three definitions 3; lifecycle implication 2.


### U09-Q03 — Short Answer
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L2
- **Question type:** short answer
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 6 minutes

**Prompt**
How should governance weight vary across a docs typo, template default change, policy enforcement change and breaking platform API change?

**Model answer**
Use blast radius, reversibility, security/data impact, consumer count and evidence to scale review. A docs typo may need lightweight owner review. A template default needs generated-output tests and canary consumers. A policy enforcement change needs impact analysis in audit mode and approved staged enforcement. A breaking API change needs RFC/consumer input, compatibility/migration plan, version lifecycle, staged rollout and rollback/restore evidence.

**Reasoning**
Governance should be proportional, not a committee for every edit or an uncontrolled change pipeline.

**Common wrong answers / tempting mistakes**
Same approval for every edit; no review for policy because YAML is small; requiring full council for typo.

**Scoring guidance**
Score: risk factors 2; relative weighting 2; examples 1.


### U09-Q04 — Mcq
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L2
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform governance, deprecation, and versioning principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
An API adds an optional response field that existing clients can ignore. Under the stated compatibility contract, what classification is most appropriate?

**Options**
A. Treat an optional additive field as compatible only if the declared contract allows it and tests confirm old consumers remain valid.
B. Classify every schema change as breaking regardless of consumer behavior.
C. Ignore the consumer contract because the API server accepts the object.
D. Wait until consumers fail before deciding whether the change was compatible.

**Model answer**
**Correct option: A.** Usually compatible if the contract explicitly permits additive optional fields and tests confirm existing consumers remain valid. The exact SemVer label depends on the declared versioning policy and API semantics.

**Reasoning**
B assumes all schema changes break. C ignores consumer contract. D changes only after consumers fail.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
B: overly conservative without evidence. C: compatibility is consumer-visible. D: reactive classification is unsafe.

**Scoring guidance**
Score: correct 1; contract caveat 2.


### U09-Q05 — Mcq
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L3
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform governance, deprecation, and versioning principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
A new policy bundle changes a rule from audit to enforce for all repositories. What must precede enforcement?

**Options**
A. Enforce the new policy globally immediately to remove all ambiguity.
B. Keep the policy in warn mode permanently and never review denials.
C. Run audit impact analysis, assess coverage/exceptions, communicate remediation and stage enforcement through rings with rollback criteria.
D. Change the policy source without consumer inventory because the rule is security-related.

**Model answer**
**Correct option: C.** Run policy impact analysis in audit mode against the known consumer population, measure coverage/freshness, identify false positives and exceptions, get accountable approval, communicate remediation and stage enforcement through rings with rollback criteria.

**Reasoning**
A enforces without impact evidence. B makes permanent warning ineffective. D bypasses consumers and changes source of truth.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: uncontrolled blast radius. B: no path to enforcement. D: hides impact and creates drift.

**Scoring guidance**
Score: correct 1; staged governance 2.


### U09-Q06 — Mcq
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L4
- **Question type:** mcq
- **Objective tested:** Assess the learner's ability to apply the platform governance, deprecation, and versioning principle in the stated scenario.
- **Suggested time:** 7 minutes

**Prompt**
An exception record has an owner and approval but no expiry or review date. What is the key defect?

**Options**
A. Keep the exception indefinitely because it has an owner.
B. Assume approval alone is enough; no review date is needed.
C. Treat the registry entry as proof that the risk is controlled.
D. Add a bounded expiry/review date, scope, reason, compensating controls, evidence and approver; detect stale exceptions.

**Model answer**
**Correct option: D.** The exception can become permanent unmanaged drift. Add expiry, review date, scope, reason, compensating controls, evidence, approver and renewal criteria; automate stale/expired exception detection.

**Reasoning**
A assumes approval is permanent. B ignores risk ownership. C treats a registry entry as control without lifecycle.

**Common wrong answers / tempting mistakes**
The tempting options confuse an intermediate artifact, untrusted input, tool preference or incomplete signal with the full platform contract.

**MCQ distractor analysis**
A: exceptions need bounded duration. B: owner alone is not approval/lifecycle. C: record existence does not enforce expiry.

**Scoring guidance**
Score: correct 1; lifecycle explanation 2.


### U09-Q07 — Artifact Interpretation
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L2
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Compatibility matrix: template v3 + workflow v2 + chart v4 + API v1 = supported; template v2 + workflow v2 + chart v4 + API v1 = unsupported; template v3 + workflow v3 + chart v4 + API v1 = unknown. How should the release gate treat each?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Compatibility matrix: template v3 + workflow v2 + chart v4 + API v1 = supported; template v2 + workflow v2 + chart v4 + API v1 = unsupported; template v3 + workflow v3 + chart v4 + API v1 = unknown. How should the release gate treat each?
```

**Model answer**
First combination may pass the compatibility gate if the matrix is current and tests pass. Second must fail or require a documented migration because explicitly unsupported. Third must not be treated as supported: unknown requires evidence/test or an explicit temporary decision. The matrix is a contract, not a substitute for consumer tests.

**Reasoning**
Pass, fail and unknown must remain distinct.

**Common wrong answers / tempting mistakes**
Treating unknown as pass; assuming newest workflow always works; ignoring matrix freshness.

**Scoring guidance**
Score: three states 3; evidence/freshness caveat 2.


### U09-Q08 — Artifact Interpretation
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] Deprecation record: artifact `base-image/python`; owner `platform-images`; replacement `python-runtime-v4`; affected repos 12; warnings sent to 9; migration PRs merged 7; approved exceptions 2 with expiry; last usage scan 45 days old. Can removal proceed?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] Deprecation record: artifact `base-image/python`; owner `platform-images`; replacement `python-runtime-v4`; affected repos 12; warnings sent to 9; migration PRs merged 7; approved exceptions 2 with expiry; last usage scan 45 days old. Can removal proceed?
```

**Model answer**
Not yet on this evidence alone. Usage scan may be stale; three affected repos have no confirmed warning and five are not merged, with exceptions requiring current review. Refresh usage and consumer inventory, identify remaining active consumers, confirm support timeline, migration readiness, rollback/recovery and exception expiry, then evaluate the explicit removal gate. Do not infer no usage from stale telemetry.

**Reasoning**
Removal requires fresh evidence, complete consumer impact and a governed exception decision.

**Common wrong answers / tempting mistakes**
Remove because seven PRs merged; treat old scan as current; ignore the uncontacted repos.

**Scoring guidance**
Score: decision 1; evidence gaps 2; removal-gate steps 2.


### U09-Q09 — Artifact Interpretation
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L3
- **Question type:** artifact interpretation
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 8 minutes

**Prompt**
[SYNTHETIC] RFC proposes `ModelEndpoint v1alpha1` to `v1beta1`, changes `scaling.maxReplicas` default from 3 to 10 and makes `model.digest` optional. What questions must compatibility review ask?

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
[SYNTHETIC] RFC proposes `ModelEndpoint v1alpha1` to `v1beta1`, changes `scaling.maxReplicas` default from 3 to 10 and makes `model.digest` optional. What questions must compatibility review ask?
```

**Model answer**
Does the default change increase cost/capacity or alter availability? Can existing consumers rely on maxReplicas=3? Does optional digest weaken model integrity/provenance? Are validation and readiness semantics changed? Which tenants/repos use the version? Is a new version or migration needed? What negative tests, impact report, ring rollout, exception and rollback/restore plan apply? The field contract and exact API schema are source/version-specific and must be verified.

**Reasoning**
A field remaining present does not guarantee semantic compatibility. Defaults and validation are part of the contract.

**Common wrong answers / tempting mistakes**
Calling it compatible because names are unchanged; treating beta as no consumers; assuming optional digest is harmless.

**Scoring guidance**
Score: identify default and digest risks 2; consumer/tests 2; rollout/migration 1.


### U09-Q10 — Artifact Review
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L2
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this exception entry: `id=EX-14; artifact=policy-bundle; reason=blocks team; owner=analytics; approved=true; expires=never; compensating_control=none; evidence=chat message; scope=all namespaces`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this exception entry: `id=EX-14; artifact=policy-bundle; reason=blocks team; owner=analytics; approved=true; expires=never; compensating_control=none; evidence=chat message; scope=all namespaces`.
```

**Model answer**
Defects: no bounded scope; no expiry/review; no compensating control; approval authority unclear; evidence weak/untraceable; no risk classification; no owner backup; broad exception undermines policy for all tenants. Fix with narrow resource/team scope, accountable approver, explicit risk and control, test evidence, expiration/review date and automatic expiry alert. Reject if no safe compensating control exists.

**Reasoning**
An exception is a temporary, auditable risk decision—not a policy bypass.

**Common wrong answers / tempting mistakes**
Accepting because owner exists; setting arbitrary long expiry without review; relying on chat.

**Scoring guidance**
Score: defects 4; repairs 6.


### U09-Q11 — Artifact Review
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L3
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this API change record: `removed required spec.model.digest; changed default tier from standard to critical; no compatibility matrix; no consumer inventory; release notes say minor; automatic rollout to all tenants; no rollback plan`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this API change record: `removed required spec.model.digest; changed default tier from standard to critical; no compatibility matrix; no consumer inventory; release notes say minor; automatic rollout to all tenants; no rollback plan`.
```

**Model answer**
Defects: removal of required integrity field is breaking; semantic default change may increase cost/privilege; no matrix/consumer impact; version label unsupported by contract; no migration; no ring/canary; no rollback/restore; no security review. Fix with explicit versioned migration, required digest/provenance, impact analysis, consumer design partners, compatibility tests and staged rollout.

**Reasoning**
Version classification must reflect consumer-visible semantics, not the author's chosen label.

**Common wrong answers / tempting mistakes**
Accepting minor label; assuming new default is safer; applying automatically because API server accepts it.

**Scoring guidance**
Score: defects 4; compatibility and rollout corrections 6.


### U09-Q12 — Artifact Review
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L4
- **Question type:** artifact review
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 12 minutes

**Prompt**
Review this release manifest: `artifact=platform-policy; version=2.0; source=main; digest=missing; signature=not checked; owner=blank; rollout=all; change freeze=ignored; rollback=manual TBD`.

**Synthetic artifact (SYNTHETIC; not executed)**
```text
SYNTHETIC ARTIFACT EXCERPT — reproduce and assess only the supplied scenario
Review this release manifest: `artifact=platform-policy; version=2.0; source=main; digest=missing; signature=not checked; owner=blank; rollout=all; change freeze=ignored; rollback=manual TBD`.
```

**Model answer**
Defects: mutable source ref; no immutable digest; signature/provenance not verified; no owner; no consumer impact or compatibility test; no rings/canary; ignores freeze; no concrete rollback/abort criteria; missing release notes and evidence. Fix with immutable source/artifact digest, verified provenance/signature, owner, compatibility matrix and impact report, staged rings, freeze policy and tested rollback instructions.

**Reasoning**
A release manifest is evidence of what is being deployed and under whose authority.

**Common wrong answers / tempting mistakes**
Trusting tag name; assuming signature field means verified; relying on a future manual rollback plan.

**Scoring guidance**
Score: defects 4; fixes 6.


### U09-Q13 — Incident
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L4
- **Question type:** incident
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC INCIDENT] A new platform API version is rolled out to all tenants. Existing claims fail because a required field was removed; one tenant has an approved temporary exception. What is the response?

**Model answer**
Stop further rollout and preserve API/XRD/Composition revisions, claims, compatibility tests, audit and tenant exception evidence. Determine affected consumers and whether controllers are mutating/deleting children. Mitigate with a compatible served version or restore the prior contract only after verifying rollback semantics; protect the exception's scope/expiry and do not widen it. Communicate affected owners and migration path. Verify claim reconciliation and usable outcomes. Add breaking-change classifier, consumer inventory, matrix tests, ring gate and deprecation notice.

**Reasoning**
The exception is not permission to bypass all checks. Rollback must consider controller and data semantics.

**Common wrong answers / tempting mistakes**
Delete failed claims; remove the exception; force every tenant to migrate immediately; assume reverting API schema reverses resource state.

**Scoring guidance**
Score: containment 2; evidence/scope 2; safe mitigation/comms 3; prevention 3.


### U09-Q14 — Design
- **Scope:** Unit 9 — Platform governance, deprecation, and versioning; artifact inventory and ownership; compatibility semantics; SemVer limits; compatibility matrix; RFC/ADR and decision rights; release manifests/rings/rollback; policy impact; deprecation; exceptions; EOL; docs/dependencies; API lifecycle; data/ML governance; portability/sunset
- **Level:** L3
- **Question type:** design
- **Objective tested:** Assess the learner's ability to explain, interpret or apply the stated platform governance, deprecation, and versioning topic.
- **Suggested time:** 25 minutes

**Prompt**
Design a governance lifecycle for a widely used platform artifact with a security fix and a planned breaking API change.

**Model answer**
Strong outline: inventory artifact/owner/backup/consumers/version/EOL; classify changes by security and compatibility; publish RFC/ADR and consumer input; pin immutable release and provenance; test old/new compatibility and negative policy cases; run impact analysis; announce deprecation with replacement, migration guide and fresh usage telemetry; handle scoped expiring exceptions; roll out security fix through rings with emergency path; stage breaking API version and consumer migrations; remove only after explicit gate; track support lag, migration debt, incident and risk metrics. State thresholds/timelines as `[ILLUSTRATIVE]` unless source-backed.

**Reasoning**
Security-critical urgency and compatibility obligations can coexist through explicit risk decisions and staged rollout.

**Common wrong answers / tempting mistakes**
Using SemVer as only proof; never removing old versions; immediate global breaking upgrade without migration.

**Scoring guidance**
Score 0–2 each: inventory, compatibility, decision rights, release security, deprecation, exception lifecycle, evidence/metrics (14).


---

## Cross-unit integration scenarios — 40 questions

These scenarios connect two or more M16 units and prior M01–M15 mechanisms. Each scenario is independently answerable from its stated context. The capstone is used as an integration setting, not as a replacement for unit coverage.

### XU-Q01 — Synthesis
- **Scope:** U1–U2–U5
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Integrate platform discovery, golden-path scope and template lifecycle.
- **Suggested time:** 15 minutes

**Prompt**
A team reports that starting a batch pipeline takes too long. Propose the evidence and decision sequence before creating a new template.

**Model answer**
Measure the manual journey and friction; validate the problem with actual users when available; distinguish repeated setup from workload-specific logic; choose a thin supported batch path only if repeated value exists; reuse hardened image, CI, policy, observability and cost contracts; create a versioned template with owner, tests and update path.

**Reasoning**
A user problem must precede the implementation. Unit 2 owns path design; Unit 5 owns its generated repository lifecycle.

**Common wrong answers / tempting mistakes**
Building a new portal first; copying an API template and renaming it; claiming synthetic friction counts prove demand.

**Scoring guidance**
10 points: evidence 2; path/template boundary 2; M01–M15 reuse 2; lifecycle 2; honest measurement 2.


### XU-Q02 — Synthesis
- **Scope:** U1–U2–U3–U4–U5–U6–U7–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Trace the full developer journey across all M16 units.
- **Suggested time:** 15 minutes

**Prompt**
Trace one synthetic `analytics` model-serving request from idea to retirement. Identify the owner of each stage and at least one evidence artifact per stage.

**Model answer**
Unit 1 frames user/job and baseline; Unit 2 defines path; Unit 5 generates repo; Unit 3 validates entitlement and provisions; Unit 6 reconciles API resources; Unit 7 gates tenant isolation; Unit 4 catalogs ownership/dependencies; Unit 8 measures usable journey and platform outcomes; Unit 9 versions, migrates and retires contracts. Evidence includes PRD, template provenance, request/status, API conditions, isolation report, catalog record, SLO/metric record, compatibility/deprecation record.

**Reasoning**
The sequence composes units without collapsing their responsibilities. Portal is a front door; API/controller is a separate contract; tenant safety is independently tested.

**Common wrong answers / tempting mistakes**
Assigning all responsibilities to Backstage; treating namespace creation as tenant isolation; omitting operations and retirement.

**Scoring guidance**
12 points: stage order 3; ownership boundaries 3; evidence 3; failure/retirement coverage 3.


### XU-Q03 — Synthesis
- **Scope:** U1–U2–U3–U6
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Defend a self-service API-first architecture.
- **Suggested time:** 15 minutes

**Prompt**
A developer prefers CLI while another uses a portal. Both must request the same `DataEnvironment`. How do you prevent policy divergence?

**Model answer**
Use one canonical request schema and backend. Portal, CLI and Git/PR are adapters; identity and entitlement are checked at the trusted backend boundary; shared validation/policy and status are used for all. The portal is replaceable. Log a correlation ID and expose consistent denial/readiness states.

**Reasoning**
Multiple front doors should not become separate authorization paths.

**Common wrong answers / tempting mistakes**
Duplicating validation in each front end; trusting the portal's login for CLI; using different resource schemas.

**Scoring guidance**
10 points: canonical contract 3; authorization boundary 2; status/evidence 2; replaceability 1; tests 2.


### XU-Q04 — Synthesis
- **Scope:** U1–U2–U3–U7
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Connect golden-path defaults to tenant controls.
- **Suggested time:** 15 minutes

**Prompt**
A service template requires default-deny networking, but a tenant's custom manifest removes it. What is the correct escape-hatch policy?

**Model answer**
A supported escape may change implementation details only within a documented support boundary; mandatory network isolation controls remain enforced in CI and admission. Record the exception only if policy allows a narrow, expiring, compensating-control-backed deviation. Test both denial and permitted paths for the tenant pair.

**Reasoning**
Golden path autonomy does not authorize bypassing safety controls. Unit 7 proves isolation; Unit 2 provides default/option/escape semantics.

**Common wrong answers / tempting mistakes**
Treating escape as policy bypass; blocking every legitimate variation; relying only on template contents.

**Scoring guidance**
10 points: mandatory-vs-optional distinction 3; layered enforcement 3; exception governance 2; positive/negative tests 2.


### XU-Q05 — Synthesis
- **Scope:** U1–U4–U8
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Avoid stale catalog and misleading measurement.
- **Suggested time:** 15 minutes

**Prompt**
The portal shows more services after a catalog ingestion change, but adoption metrics do not change. What should be checked?

**Model answer**
Check entity duplication, canonical identity, ingestion source, eligibility denominator, deduplication keys, event schema and time window. Distinguish catalog inventory coverage from golden-path adoption. Restate definitions if changed and preserve a definition-version note. Do not interpret more entities as more adoption.

**Reasoning**
Catalog completeness and adoption are related but distinct measures. A changed ingestion pipeline can alter counts without developer behavior changing.

**Common wrong answers / tempting mistakes**
Assuming more catalog entities mean adoption; changing the denominator silently; deleting duplicates without audit.

**Scoring guidance**
10 points: separate measures 2; data-quality checks 3; denominator/version 3; cautious interpretation 2.


### XU-Q06 — Synthesis
- **Scope:** U2–U5–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Plan safe template security fix propagation.
- **Suggested time:** 15 minutes

**Prompt**
A vulnerable base-image reference exists in six generated repos. Two have local Dockerfile changes. Plan the update campaign.

**Model answer**
Publish a pinned template fix with provenance and regression tests; inventory all six consumers and their source revisions; preview diffs; classify platform/team-owned conflicts; canary by archetype; open least-privilege reviewed PRs; quarantine the two conflicts; verify image digest and CI; record merged/blocked status; use an emergency policy if risk warrants but preserve migration evidence.

**Reasoning**
A security fix must propagate without silently destroying team-owned changes. Unit 9 governs release/deprecation; Unit 5 owns template update mechanics.

**Common wrong answers / tempting mistakes**
Force-overwrite all files; let bot auto-merge; leave conflict repos untracked; rely on a mutable tag.

**Scoring guidance**
12 points: inventory/release 2; conflict handling 3; bot safety 2; tests/rings 3; status/comms 2.


### XU-Q07 — Synthesis
- **Scope:** U3–U6–U7
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Localize a rejection or isolation failure at the correct boundary.
- **Suggested time:** 15 minutes

**Prompt**
A tenant request passes schema and entitlement, but admission denies the namespace because a protected label is missing. What evidence and response distinguish this from controller failure?

**Model answer**
Inspect request ID, identity/entitlement decision, rendered desired state, admission policy result/reason, namespace ownership labels and audit event. Admission denial means the API server rejected the object before controller reconciliation; do not debug provider reconciliation first. Fix the trusted label projection through the owning workflow and rerun positive/negative tenant tests.

**Reasoning**
Each rejection layer has different evidence. The correct diagnosis prevents unsafe bypasses.

**Common wrong answers / tempting mistakes**
Granting tenant label patch permission; changing controller settings; retrying until admission passes.

**Scoring guidance**
10 points: stage localization 3; evidence 3; safe fix 2; tests 2.


### XU-Q08 — Synthesis
- **Scope:** U3–U6–U8
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Define provisioning SLO from usable readiness.
- **Suggested time:** 15 minutes

**Prompt**
A controller reports `Synced=True` but the database endpoint is unreachable. Which SLI should the platform publish?

**Model answer**
Measure valid entitled requests reaching the usable-ready state within the defined latency window, with readiness including an approved connectivity/data-path probe. Report reconciliation and failure-stage metrics separately. Define denominator, exclusions, time window and event-quality checks.

**Reasoning**
Controller sync is an internal signal; the user task is a usable data capability.

**Common wrong answers / tempting mistakes**
Counting accepted requests or synced objects as success; excluding late/failed requests from denominator.

**Scoring guidance**
10 points: user outcome 3; numerator/denominator 3; stage metrics 2; caveat 2.


### XU-Q09 — Synthesis
- **Scope:** U4–U7–U8
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Use catalog data safely during tenant incident.
- **Suggested time:** 15 minutes

**Prompt**
An alert identifies `risk-scoring-api`, but catalog owner is stale and tenant telemetry indicates a possible cross-tenant path. What is the response?

**Model answer**
Use trusted current on-call/ownership source, not stale portal cache; contain the potential isolation issue via incident process; preserve catalog revision, principal, network and audit evidence; bound affected tenant/resource; halt relevant rollout; notify owners; verify both isolation and routing; repair catalog source/ingestion and add freshness/drift controls.

**Reasoning**
Catalog data helps locate owners but stale data must not control incident routing. Tenant isolation is a separate safety boundary.

**Common wrong answers / tempting mistakes**
Trusting portal owner field; editing cache without fixing source; delaying containment until catalog corrected.

**Scoring guidance**
12 points: safe routing 2; isolation containment 3; evidence 2; communication 2; prevention 3.


### XU-Q10 — Synthesis
- **Scope:** U5–U6–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Coordinate template and API contract evolution.
- **Suggested time:** 15 minutes

**Prompt**
A template begins generating a new required `ModelEndpoint` field before the platform API has graduated the version. What should the release order be?

**Model answer**
Define and test the API version/compatibility contract first; publish API support and migration path; ensure old/new consumers are understood; update template only after API availability and compatibility are verified; stage template rollout; preserve older supported template/API combinations in matrix; deprecate old versions with usage evidence.

**Reasoning**
A template is a consumer of the platform API. Releasing the consumer before the contract it requires creates version skew.

**Common wrong answers / tempting mistakes**
Ship template first and let reconciliation fail; make the field optional without contract review; float API version.

**Scoring guidance**
10 points: dependency order 3; compatibility matrix 3; rollout 2; deprecation 2.


### XU-Q11 — Synthesis
- **Scope:** U6–U7–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Prevent composition change from deleting tenant data.
- **Suggested time:** 15 minutes

**Prompt**
A composition revision changes a database immutable field and a tenant namespace label. What gates are required?

**Model answer**
Render/diff all affected resources; identify immutable replacement and deletion semantics; protect trusted labels; produce tenant fan-out impact report; require restore evidence and explicit owner approval; maintain Manual update policy as specified in the lesson; canary ring; positive/negative RBAC/admission/isolation tests; rollback decision based on controller semantics. Verify current Crossplane fields/version.

**Reasoning**
Composition code can change both resource lifecycle and trust boundaries. A rendered diff is necessary but not sufficient.

**Common wrong answers / tempting mistakes**
Apply globally because YAML validates; rely on namespace deletion; assume rollback restores external data.

**Scoring guidance**
12 points: destructive impact 3; label trust 2; test/evidence 3; ring/rollback 2; version verification 2.


### XU-Q12 — Synthesis
- **Scope:** U7–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Connect tenant baseline versioning with continuous assurance.
- **Suggested time:** 15 minutes

**Prompt**
A tenant's isolation suite passes on baseline v3, but policy bundle v4 changes network and label selectors. What is required before v4 is considered conformant?

**Model answer**
Run impact analysis and a versioned isolation suite against v4 for every tenant pair, including positive permitted paths; test protected labels, policy selection and canary tenant; record versions and evidence; classify failures and exceptions; rollout through rings; retain prior baseline/rollback plan; do not infer conformance from v3 evidence.

**Reasoning**
A tenant's pass is tied to the tested baseline and policy version. Version changes invalidate assumptions until retested.

**Common wrong answers / tempting mistakes**
Reuse v3 report as proof; test only one tenant; count timeout as denial.

**Scoring guidance**
10 points: version linkage 3; matrix/canary 3; exceptions/rollback 2; evidence 2.


### XU-Q13 — Synthesis
- **Scope:** U8–U9–U1
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Prevent metric definition drift from becoming a governance failure.
- **Suggested time:** 15 minutes

**Prompt**
A governance release changes the definition of `golden_path_coverage` and dashboard shows a jump. What records and communication are needed?

**Model answer**
Version the metric definition; record numerator, denominator, eligibility, exclusions, event source and effective date; compute old/new series or restate historical values only if valid; document discontinuity and consumer impact; review anti-gaming/privacy; communicate that a definition change is not adoption growth.

**Reasoning**
Metrics are governed artifacts. A definition change can break trend comparability.

**Common wrong answers / tempting mistakes**
Calling the jump improvement; silently replacing denominator; retaining individual-level raw events.

**Scoring guidance**
10 points: metric contract 4; comparability 2; privacy 2; communication 2.


### XU-Q14 — Synthesis
- **Scope:** U1–U2–U8
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Evaluate an escape hatch without undermining product value.
- **Suggested time:** 15 minutes

**Prompt**
A team opts out of the golden path because its streaming workload needs specialized backpressure. What is a product-oriented response?

**Model answer**
Understand the workload and task; determine whether a supported option should be added or the escape remains best-effort; preserve mandatory security, ownership, SLO and cost controls; document support boundary; compare friction and incident evidence; avoid forcing API/batch assumptions onto streaming.

**Reasoning**
Escape-hatch usage can reveal a real archetype gap, not developer noncompliance.

**Common wrong answers / tempting mistakes**
Forcing the path; permanently forking without conformance; treating every request as a new platform feature.

**Scoring guidance**
10 points: discovery 2; supported variation decision 3; mandatory controls 2; evidence/feedback 3.


### XU-Q15 — Synthesis
- **Scope:** U2–U3–U5
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Trace generated files into a self-service provisioning flow.
- **Suggested time:** 15 minutes

**Prompt**
A developer generates a repo and requests an environment. Which artifacts are owned by template generation versus provisioning, and how should the handoff work?

**Model answer**
Template owns starting repository files, parameters, provenance and catalog/SLO/runbook skeleton. Provisioning owns canonical environment request, entitlement, policy, desired-state submission, lifecycle and readiness. The generated repo may reference the request contract but must not embed credentials or directly grant provider permissions. Tests validate template output and provisioning separately.

**Reasoning**
Generation creates a repo; provisioning creates and operates a capability. The boundary avoids coupling a template to privileged infrastructure.

**Common wrong answers / tempting mistakes**
Using template hooks to provision privileged resources; treating generated YAML as an approved request; mixing credentials into repo.

**Scoring guidance**
10 points: boundary 4; secure handoff 3; separate tests 3.


### XU-Q16 — Synthesis
- **Scope:** U3–U4–U6
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Design multiple front doors with consistent ownership and catalog data.
- **Suggested time:** 15 minutes

**Prompt**
A portal, Git PR and CLI all create `DataEnvironment`. How should ownership and catalog metadata be projected?

**Model answer**
All front doors submit one request contract to the same backend. Authenticated identity maps through entitlement/ownership registry; platform API enforces contract; catalog ownership is a normalized projection, not caller-controlled arbitrary text. Record request/resource correlation and catalog source/freshness. Preserve team, tenant key, namespace, cost center and owner as distinct fields.

**Reasoning**
The catalog helps discovery and routing but is not the authorization source by itself.

**Common wrong answers / tempting mistakes**
Portal writes catalog owner directly; CLI bypasses entitlement; using namespace as team identity.

**Scoring guidance**
10 points: shared contract 3; identity projection 3; catalog trust/freshness 2; evidence 2.


### XU-Q17 — Synthesis
- **Scope:** U4–U5–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Govern portal catalog schema migration.
- **Suggested time:** 15 minutes

**Prompt**
A catalog schema change renames owner references while template v2 still emits the old form. What is the safe plan?

**Model answer**
Inventory producers and consumers; define compatibility and lifecycle; support old/new representation or staged migration; update template and linter with compatibility tests; validate owner resolution and catalog automation; publish migration guide and deprecation warnings; use canary repositories and freshness/drift reports; remove old form only after consumer evidence and exceptions close.

**Reasoning**
Catalog schema is consumed by templates, portal ingestion and automation; migration must be producer/consumer aware.

**Common wrong answers / tempting mistakes**
Change schema and templates simultaneously without matrix; rewrite catalog cache only; assume all repos update together.

**Scoring guidance**
10 points: inventory 2; compatibility plan 3; tests/rings 3; removal evidence 2.


### XU-Q18 — Synthesis
- **Scope:** U4–U8–U9
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Distinguish portal reliability from catalog data quality.
- **Suggested time:** 15 minutes

**Prompt**
Portal HTTP availability is green, but 30% of synthetic entities have stale owner metadata. Which SLI/KPI and remediation are appropriate?

**Model answer**
Keep portal availability separate from catalog freshness/ownership completeness. Define freshness SLI over eligible entities and owner-resolution KPI with source/window/denominator; show stale/unknown status; alert accountable catalog owners; maintain fallback routing from trusted ownership registry. Do not combine both into one uptime number.

**Reasoning**
A portal can be up while the information it serves is wrong.

**Common wrong answers / tempting mistakes**
Increase uptime target; remove stale entities without audit; assume UI rendering proves data quality.

**Scoring guidance**
10 points: separate measures 3; metric contract 3; fallback/remediation 2; caveat 2.


### XU-Q19 — Synthesis
- **Scope:** U5–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Measure template update adoption without ranking people.
- **Suggested time:** 15 minutes

**Prompt**
Five synthetic repos are offered a security template update; three merge within the stated window, one conflicts, one is not eligible. Define a useful measure.

**Model answer**
Eligible repo adoption = merged eligible repos / eligible repos offered update, so 3/4 = 75% if the conflict repo is eligible and the not-eligible repo is excluded by documented rule. Report conflict and blocked states separately, window and eligibility version. Do not rank developers; the sample is synthetic and tiny.

**Reasoning**
A transparent denominator and status taxonomy make update lag useful for governance.

**Common wrong answers / tempting mistakes**
3/5 without eligibility rule; 3/3 by excluding conflict; calling 75% a real-world adoption benchmark.

**Scoring guidance**
10 points: denominator 3; status treatment 3; privacy/synthetic caveat 2; decision use 2.


### XU-Q20 — Synthesis
- **Scope:** U6–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Define evidence for an API lifecycle graduation.
- **Suggested time:** 15 minutes

**Prompt**
A `ModelEndpoint` alpha has schema tests and a demo but no tenant negative tests, support owner or rollback. Can it graduate to beta?

**Model answer**
Not on that evidence. Graduation criteria should include contract documentation, consumer feedback, schema/render/integration tests, authorization and tenant negative tests, readiness/status behavior, support owner/on-call, compatibility/migration, security review, cost/capacity bounds and staged rollout/rollback. The exact policy thresholds are illustrative unless established.

**Reasoning**
A demo and schema test cover only a fraction of the production contract.

**Common wrong answers / tempting mistakes**
Graduating because the happy path works; assuming beta means no support; skipping rollback because alpha is experimental.

**Scoring guidance**
10 points: gaps 4; graduation evidence 4; honest lifecycle criteria 2.


### XU-Q21 — Synthesis
- **Scope:** U7–U9–U3
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Handle a tenant offboarding request during an API deprecation.
- **Suggested time:** 15 minutes

**Prompt**
A tenant still uses a deprecated database API and requests offboarding while a retention hold is unresolved. What sequence avoids data loss and stale access?

**Model answer**
Freeze destructive removal for the held data; verify tenant authority and data owner/steward; inventory database, buckets, secrets, endpoints and dependents; provide export/retention decision; revoke interactive/service access according to approved process; keep the old API only as long as required for safe transition with scoped exception and expiry; perform dependency-aware deletion and orphan verification after hold resolution; record audit.

**Reasoning**
Offboarding and deprecation interact: data safety and access revocation are distinct from deleting the API version.

**Common wrong answers / tempting mistakes**
Delete the namespace immediately; retain credentials indefinitely; remove API version before consumers are migrated.

**Scoring guidance**
12 points: hold gate 3; access revocation 2; dependency inventory 2; staged removal 2; evidence 3.


### XU-Q22 — Synthesis
- **Scope:** U1–U4–U5–U8
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Choose an adoption feedback loop for a new template and portal.
- **Suggested time:** 15 minutes

**Prompt**
Synthetic data shows template generation is high but first CI green is low. What does this tell you and what should you inspect?

**Model answer**
Generation is an output; first CI green is a downstream journey outcome. Inspect failure reasons, template version/archetype, policy messages, dependency availability, missing secrets references and docs. Segment by archetype and version; validate with actual user observation when available. Fix top friction and remeasure without individual ranking.

**Reasoning**
A funnel identifies where users stop but does not explain why. Event quality and eligibility matter.

**Common wrong answers / tempting mistakes**
Celebrate generation count; blame users; change policy to warn without risk review.

**Scoring guidance**
10 points: output/outcome distinction 2; diagnosis 3; research 2; safe iteration 3.


### XU-Q23 — Synthesis
- **Scope:** U2–U6–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Protect consumers during a breaking golden-path API change.
- **Suggested time:** 15 minutes

**Prompt**
A chart default change alters storage class and the Crossplane API still accepts the old value. How do you coordinate releases?

**Model answer**
Classify semantic compatibility for chart and API separately; inventory consumer combinations; add tests for old/new chart/API pairs; preserve old supported combination during migration; issue RFC/ADR and migration notes; stage template/chart/API releases in dependency order; run data safety and restore tests; remove old value only after usage evidence and exception review.

**Reasoning**
Compatibility is artifact-specific and combinations matter. A SemVer label alone cannot establish safe behavior.

**Common wrong answers / tempting mistakes**
Assuming chart minor version is compatible; upgrade API and chart simultaneously without matrix; ignore stateful storage semantics.

**Scoring guidance**
12 points: classification 2; matrix/tests 3; migration order 2; data safety 3; governance 2.


### XU-Q24 — Synthesis
- **Scope:** U3–U7–U8
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Investigate noisy-neighbor effects in self-service tenancy.
- **Suggested time:** 15 minutes

**Prompt**
Synthetic queue wait and provisioning latency rise only for `risk-platform` after a large batch job. What should be measured and controlled?

**Model answer**
Inspect tenant-scoped queue wait, CPU/memory/storage/network and API object consumption; correlate with workload and provisioning stages; preserve other tenants' SLOs. Apply documented quotas/priority/backpressure or placement controls appropriate to trust tier. Measure impact on usable-ready outcomes and cost; avoid exposing individual developer data.

**Reasoning**
Noisy-neighbor diagnosis is tenant/workload-level. A single cluster metric may hide tenant-specific contention.

**Common wrong answers / tempting mistakes**
Raise all quotas; attribute to one developer; scale blindly without checking capacity/cost.

**Scoring guidance**
10 points: signals 3; controls 3; SLO/cost 2; privacy 2.


### XU-Q25 — Synthesis
- **Scope:** U4–U6–U7–U8
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Respond when catalog and API status disagree.
- **Suggested time:** 15 minutes

**Prompt**
Catalog says `ModelEndpoint` is ready, but API status shows `Ready=False` and model load failed. Which source should the developer trust and how should it be corrected?

**Model answer**
Treat live API/controller status as current capability evidence; catalog should link to it and display freshness/provenance rather than override it. Mark catalog projection stale/degraded, preserve status and ingestion events, route to API owner, fix sync/freshness pipeline and test stale-state handling. A catalog entry is not a readiness authority.

**Reasoning**
Catalog is a discovery projection; status is a live resource contract, subject to its own semantics.

**Common wrong answers / tempting mistakes**
Trusting the green catalog card; manually changing API status; deleting catalog entity to hide mismatch.

**Scoring guidance**
10 points: source-of-truth distinction 3; response 3; correction/tests 4.


### XU-Q26 — Synthesis
- **Scope:** U5–U7–U8
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Test generated tenant metadata and isolation handoff.
- **Suggested time:** 15 minutes

**Prompt**
A template emits `team=analytics`, `namespace=tn-team-a`, `cost-center=CC-SYNTH-ANALYTICS-01`. Which checks should run before this metadata drives tenant policy?

**Model answer**
Validate each field against its authoritative registry and type; do not assume they are interchangeable. Derive/authorize tenant identity from authenticated principal; protect namespace labels; ensure cost center is only showback; validate catalog owner separately. Run positive/negative tests for spoofed team, namespace and cost center values.

**Reasoning**
Generated metadata is input to policy and catalog; its origin and semantics must be explicit.

**Common wrong answers / tempting mistakes**
Using cost-center as entitlement; trusting template output as authenticated identity; permitting tenant label patch.

**Scoring guidance**
10 points: distinct fields 3; trusted derivation 3; negative tests 2; owner/catalog distinction 2.


### XU-Q27 — Synthesis
- **Scope:** U2–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Use conformance and adoption metrics together.
- **Suggested time:** 15 minutes

**Prompt**
Conformance falls after a new mandatory policy; adoption rises because nonconforming repos are excluded from the denominator. What should the quarterly review do?

**Model answer**
Version metric definitions and denominator; include eligible nonconforming repos and report exclusion reasons; separate voluntary adoption from mandatory compliance; inspect policy false positives, migration support and developer friction; use paired security/reliability and DX measures; decide whether to fix policy, extend migration or change support. Never infer value from one metric.

**Reasoning**
A single metric can be gamed. Governance must preserve population and definition continuity.

**Common wrong answers / tempting mistakes**
Celebrate adoption increase; force more migration; drop nonconforming services from denominator.

**Scoring guidance**
10 points: metric integrity 3; paired measures 2; user impact 2; decision loop 3.


### XU-Q28 — Synthesis
- **Scope:** U1–U3–U6–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Defend a safe emergency security change.
- **Suggested time:** 15 minutes

**Prompt**
A critical image vulnerability requires a platform base-image change while some teams have pinned older template versions. How can the platform act quickly without uncontrolled breakage?

**Model answer**
Use the emergency change path with risk record, verified affected consumer inventory, immutable patched image release, compatibility and negative tests, scoped exception/upgrade instructions, canary rings where feasible, clear comms and rollback/mitigation. A security mandate may be justified but must include enablement and explicit expiry for temporary exceptions. Update template and governance inventory.

**Reasoning**
Security urgency can justify a mandate, not skipping evidence and blast-radius control.

**Common wrong answers / tempting mistakes**
Wait for a quarterly council; globally overwrite repos; allow indefinite exception for old images.

**Scoring guidance**
12 points: urgency/risk 2; impact 2; tests/rings 3; exception/comms 2; governance 3.


### XU-Q29 — Synthesis
- **Scope:** U2–U4–U6–U7
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Keep the portal replaceable and the platform API stable.
- **Suggested time:** 15 minutes

**Prompt**
The organization plans to replace Backstage with a static portal. What must remain stable and what should migrate?

**Model answer**
Keep platform APIs, request contracts, entitlement semantics, catalog source/projection, ownership model and evidence interfaces independent of portal-specific UI. Migrate presentation and portal integrations; validate auth boundaries and links; run both front doors during a bounded transition; preserve fallback and telemetry; deprecate old portal only after consumer and operational checks.

**Reasoning**
API-first interfaces reduce portal lock-in. The portal should not own core authorization or orchestration logic.

**Common wrong answers / tempting mistakes**
Reimplement provisioning in the new UI; move all policy into frontend; assume catalog entities are portable without schema checks.

**Scoring guidance**
10 points: stable contracts 3; migration boundary 3; security 2; fallback/deprecation 2.


### XU-Q30 — Synthesis
- **Scope:** U1–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Review a platform sunset decision.
- **Suggested time:** 15 minutes

**Prompt**
A capability has low voluntary use, high maintenance cost and no clear owner, but one critical workload still depends on it. What is a defensible sunset plan?

**Model answer**
Inventory the remaining consumer and risk; verify actual usage with fresh evidence; contact owner and identify supported alternative; assess migration cost and security obligations; define a time-boxed exception if justified; provide migration support and rollback; retire only after dependency and data checks; publish decision and post-sunset evidence. Low adoption alone is not enough to delete a critical dependency.

**Reasoning**
Sunset is a product/governance lifecycle with consumer safety, not an arbitrary usage threshold.

**Common wrong answers / tempting mistakes**
Delete because usage is low; keep indefinitely because one team objects; force migration without alternative.

**Scoring guidance**
10 points: inventory/evidence 2; migration/exception 3; safe removal 3; communication 2.


### XU-Q31 — Synthesis
- **Scope:** U2–U3–U5–U6–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Coordinate an end-to-end release of a new batch archetype.
- **Suggested time:** 15 minutes

**Prompt**
A new batch template depends on a new `DataEnvironment` option and a policy update. Give the release dependency order and gates.

**Model answer**
Agree user problem and support boundary; define API/request schema and entitlement semantics; update policy with audit impact analysis; add template output and provenance; test schema, entitlement, policy, generated repo and GitOps readiness; update catalog/docs; run compatibility matrix; canary with a design-partner synthetic tenant; publish release/rollback and support. Sequence contract and policy readiness before broad template adoption.

**Reasoning**
The developer-facing path is a composition of independently versioned contracts.

**Common wrong answers / tempting mistakes**
Ship template first; rely on docs; roll out policy enforcement before checking existing requests.

**Scoring guidance**
12 points: dependency order 3; tests 3; rollout 2; catalog/support 2; governance 2.


### XU-Q32 — Synthesis
- **Scope:** U3–U6–U7–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Diagnose a controller/provider outage without misreporting success.
- **Suggested time:** 15 minutes

**Prompt**
Requests pass validation and GitOps sync, but Crossplane provider is unhealthy; users see accepted requests and stale conditions. What must be reported?

**Model answer**
Report accepted/validated but provisioning degraded/failed, not ready. Preserve provider/controller health, request and child-resource evidence, affected tenant scope and status age. Apply the relevant controller runbook, halt risky changes, communicate degraded self-service, and define a stale-status SLI. Restore provider and verify actual usable readiness before closing.

**Reasoning**
Accepted and synced are intermediate states; stale status is itself a reliability issue.

**Common wrong answers / tempting mistakes**
Mark success because the request is in Git; delete and recreate all resources; report portal uptime only.

**Scoring guidance**
10 points: truthful status 3; evidence/scope 2; safe response 3; recovery verification 2.


### XU-Q33 — Synthesis
- **Scope:** U4–U5–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Handle malicious template/catalog content entering portal automation.
- **Suggested time:** 15 minutes

**Prompt**
A generated catalog file contains an unsafe URL and a Scaffolder parameter includes shell metacharacters. What are the boundaries and controls?

**Model answer**
Treat template input and catalog ingestion as untrusted. Validate/allow-list URL schemes and locations, escape rendered HTML, restrict catalog automation to trusted metadata, validate parameters before tasks, avoid shell interpolation and arbitrary downloads, use least-privilege action/bot identity, and test malicious fixtures. Pin and verify template source; log safe provenance without secrets.

**Reasoning**
The catalog and template are both data/code supply-chain surfaces. Portal automation can turn metadata into privileged actions.

**Common wrong answers / tempting mistakes**
Assuming YAML parsing makes content safe; relying on frontend hiding; granting admin token to avoid permission errors.

**Scoring guidance**
12 points: trust boundaries 3; input validation/escaping 3; least privilege 2; negative tests 2; provenance 2.


### XU-Q34 — Synthesis
- **Scope:** U5–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Interpret update lag and exception debt.
- **Suggested time:** 15 minutes

**Prompt**
[SYNTHETIC] A template release is 60 days old; 70% of eligible repos updated; 20% have approved exceptions expiring in 15 days; 10% are blocked by conflicts. What should governance report?

**Model answer**
Report update adoption with stable eligible denominator, time window and release; exception count/scope/expiry and compensating controls; conflict/blocker categories; security exposure and owners. Do not collapse exceptions and conflicts into updated/not-updated. Prioritize expiring high-risk exceptions and provide migration support. The values are synthetic and the 60-day window is illustrative.

**Reasoning**
Version spread and exception debt are separate operational risks.

**Common wrong answers / tempting mistakes**
Calling 70% complete and ignoring remaining 30%; treating exception as updated; assuming 60 days is a policy threshold.

**Scoring guidance**
10 points: metric definitions 3; exception/conflict distinction 3; prioritized action 2; synthetic caveat 2.


### XU-Q35 — Synthesis
- **Scope:** U1–U2–U4–U8
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Diagnose adoption that stalls after discovery.
- **Suggested time:** 15 minutes

**Prompt**
A portal has high visits but few completed golden-path journeys. What is the most useful next diagnostic?

**Model answer**
Instrument a privacy-safe funnel from discovery to template generation, first CI green, request accepted, usable-ready and first operated service. Validate event quality and denominator; inspect drop-off and failure reasons; run usability tasks and interviews; preserve a thin fallback and avoid person-level tracking. Page views are an output, not task completion.

**Reasoning**
A journey funnel locates friction. It must be paired with qualitative evidence and privacy.

**Common wrong answers / tempting mistakes**
Add more portal features; count unique named users; equate visits with adoption.

**Scoring guidance**
10 points: funnel stages 3; data-quality/privacy 3; diagnosis/research 2; iteration 2.


### XU-Q36 — Synthesis
- **Scope:** U6–U7–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Design a safe platform incident review after cross-tenant impact.
- **Suggested time:** 15 minutes

**Prompt**
A platform API change causes a network policy regression for one tenant. What should the blameless review contain?

**Model answer**
Timeline, scope/affected tenant pair, exact API/composition/policy revisions, identity and admission evidence, detection gap, containment and recovery, customer communication, data/service impact, contributing factors (test coverage, ownership, rollout, drift), and prevention actions with owners/dates. Avoid individual blame; verify actions with positive/negative isolation tests and canary assurance.

**Reasoning**
The incident is a platform contract and tenant trust failure. Review must connect technical and governance controls.

**Common wrong answers / tempting mistakes**
Blaming the tenant for using the API; only recording controller restart; declaring resolved after policy file changed.

**Scoring guidance**
10 points: evidence/timeline 3; scope/impact 2; root/contributing factors 2; verified actions 3.


### XU-Q37 — Synthesis
- **Scope:** U1–U3–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Defend a platform change freeze with an exception path.
- **Suggested time:** 15 minutes

**Prompt**
Provisioning SLO is burning but a critical security fix is ready. How should the platform decide?

**Model answer**
Apply the published error-budget/change-freeze policy to routine changes. For the security fix, make an explicit emergency risk decision: verify vulnerability scope, affected tenants, mitigation alternatives, blast radius, test evidence and rollback; stage as safely as urgency permits; communicate and monitor. Do not let 'security' become an undocumented bypass or let the freeze block necessary mitigation automatically.

**Reasoning**
SLO policy guides change risk; security emergencies require explicit exception governance and evidence.

**Common wrong answers / tempting mistakes**
Freeze all changes regardless of risk; bypass every gate for any security-labelled PR; rollback without diagnosis.

**Scoring guidance**
12 points: policy application 3; emergency assessment 3; staged control 3; communication/evidence 3.


### XU-Q38 — Synthesis
- **Scope:** U2–U5–U7–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Manage a tenant-specific template fork.
- **Suggested time:** 15 minutes

**Prompt**
`risk-platform` needs a custom dependency and cannot consume the default template unchanged. How do you avoid an unsupported permanent fork?

**Model answer**
Record the workload need and threat/risk reason; determine whether a supported option/add-on is reusable; preserve mandatory controls and ownership; if a fork is necessary, name owner/support tier, track source revision and compatibility, run conformance and security tests, and set review/deprecation criteria. Do not make a team-specific fork a platform default without evidence.

**Reasoning**
A controlled variation may be justified; untracked forks create drift and hidden support cost.

**Common wrong answers / tempting mistakes**
Reject every deviation; merge the fork into all templates without user evidence; allow untracked drift.

**Scoring guidance**
10 points: need evidence 2; option/fork decision 3; controls 2; governance 3.


### XU-Q39 — Synthesis
- **Scope:** U3–U6–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Assess a platform API deprecation that has active external dependencies.
- **Suggested time:** 15 minutes

**Prompt**
A `PostgresDatabase` version is deprecated, but a backup workflow still consumes its status field. What is the removal gate?

**Model answer**
Inventory direct and indirect consumers including backup automation; verify current usage and field semantics; publish replacement and migration; test backup/restore with new version; preserve compatibility or adapter until consumers migrate; manage expiring exceptions; remove only when dependency graph, data safety, support and rollback criteria pass.

**Reasoning**
The consumer graph includes automation not visible as a developer repository. Removal requires dependency-aware evidence.

**Common wrong answers / tempting mistakes**
Only search tenant YAML; delete the old CRD when no claims are listed; assume backup workflow will adapt.

**Scoring guidance**
10 points: consumer inventory 3; migration test 3; exception/removal gate 2; data safety 2.


### XU-Q40 — Synthesis
- **Scope:** U4–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Handle a portal outage without losing platform self-service.
- **Suggested time:** 15 minutes

**Prompt**
Backstage is down during a release window. How should the platform preserve operations and avoid unsafe workarounds?

**Model answer**
Use the independent static catalog and canonical Git/CLI/API request paths; communicate portal degradation; verify authorization remains enforced server-side; do not issue shared admin tokens or bypass policy. Preserve incident evidence, restore portal via its runbook, verify catalog freshness and actions, and review portal SLO/fallback.

**Reasoning**
Portal availability should not be a single point of control-plane authority.

**Common wrong answers / tempting mistakes**
Make portal guest mode public; bypass API entitlement; stop all platform services because UI is down.

**Scoring guidance**
10 points: fallback 3; authorization 2; comms/evidence 2; recovery/prevention 3.


---

## Additional synthesis questions — 26 questions

These questions target high-risk distinctions, debugging, measurement integrity, versioning and operational judgment that benefit from additional assessment beyond the prescribed unit distribution. Seven additional questions explicitly cover incident cases in the generated M16 lessons.

### SYN-Q01 — Synthesis
- **Scope:** U1–U8
- **Level:** L2
- **Question type:** synthesis
- **Objective tested:** Apply the no-individual-ranking rule.
- **Suggested time:** 10 minutes

**Prompt**
A synthetic event schema includes `developer_id`, `deploy_count` and `manager_rank`. Which fields should be removed or redesigned?

**Model answer**
Remove person identifiers and individual counts/rank. Retain only minimum service/team-level events needed for a declared platform decision; aggregate, define retention and access, and test the schema to reject individual-level fields. Synthetic data is not permission to build surveillance.

**Reasoning**
Pseudonymization does not automatically make individual tracking ethical. The source requires privacy and an individual-field scanner.

**Common wrong answers / tempting mistakes**
Hashing developer IDs but retaining ranks; hiding the dashboard; retaining raw events indefinitely.

**Scoring guidance**
5 points: identify fields 2; privacy-safe redesign 2; scanner 1.


### SYN-Q02 — Synthesis
- **Scope:** U2–U5
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Classify an update conflict.
- **Suggested time:** 10 minutes

**Prompt**
A generated repo has a conflict in a platform-owned CI file and a team-owned application file. What is the safe disposition?

**Model answer**
Treat the CI conflict as a platform contract conflict requiring platform-owner review; treat the application conflict as team-owned and preserve it. Produce a diff, require owner review, run generated-output/conformance tests and record the per-file resolution.

**Reasoning**
File ownership determines update responsibility; conflict resolution is not an automatic merge decision.

**Common wrong answers / tempting mistakes**
Overwriting both; skipping the CI conflict; declaring the entire repo permanently unsupported.

**Scoring guidance**
5 points: ownership distinction 2; review/tests 2; evidence 1.


### SYN-Q03 — Synthesis
- **Scope:** U3–U6
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Localize admission versus controller failure.
- **Suggested time:** 10 minutes

**Prompt**
An object is rejected by admission before it is stored. Which component should be investigated first?

**Model answer**
Inspect admission policy, request identity, object fields, policy version and denial reason. The controller cannot reconcile an object that the API server rejected before persistence. Do not broaden controller permissions to bypass admission.

**Reasoning**
The evidence identifies the rejection boundary and avoids debugging downstream systems.

**Common wrong answers / tempting mistakes**
Restarting Crossplane; retrying with a different namespace; disabling admission globally.

**Scoring guidance**
5 points: layer 2; evidence 2; safe response 1.


### SYN-Q04 — Synthesis
- **Scope:** U4
- **Level:** L2
- **Question type:** synthesis
- **Objective tested:** Assess catalog freshness.
- **Suggested time:** 10 minutes

**Prompt**
A catalog entity's owner resolves but its source timestamp is stale. Should incident routing trust it?

**Model answer**
Not without the defined freshness policy. Mark the entity stale/unknown, consult the authoritative ownership/on-call source, notify the catalog owner and repair ingestion. Preserve source and ingestion timestamps.

**Reasoning**
Resolvable does not mean current. Freshness is part of catalog quality.

**Common wrong answers / tempting mistakes**
Assuming owner resolution proves current ownership; deleting the entity; routing based on cached data only.

**Scoring guidance**
5 points: decision 2; fallback 2; remediation 1.


### SYN-Q05 — Synthesis
- **Scope:** U5
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Assess template trust.
- **Suggested time:** 10 minutes

**Prompt**
A template source is pinned to a Git tag but no digest, signature or trusted provenance is checked. What does pinning prove?

**Model answer**
It constrains the requested reference but does not alone authenticate publisher identity or prove artifact integrity. Verify the release artifact/source through the organization's trusted provenance/signature process and retain evidence. Exact tooling and semantics are `[VERIFY]`.

**Reasoning**
Pinning and authentication/integrity are separate supply-chain properties.

**Common wrong answers / tempting mistakes**
Claiming tag pinning equals signature verification; assuming HTTPS proves publisher authorization; embedding credentials in template.

**Scoring guidance**
5 points: distinction 2; verification action 2; caveat 1.


### SYN-Q06 — Synthesis
- **Scope:** U6
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Interpret API immutability.
- **Suggested time:** 10 minutes

**Prompt**
A request changes a model digest after provisioning. Why might the field be immutable and what is the safe alternative?

**Model answer**
The digest identifies the deployed model artifact; changing it in place may alter a production workload unexpectedly. Treat it as immutable if the API contract says so and create a new version/revision or controlled rollout with regression tests and rollback. Exact schema semantics must be verified.

**Reasoning**
Immutability protects stable identity and makes change explicit.

**Common wrong answers / tempting mistakes**
Allow any patch; silently mutate model; claim every API must make digest immutable without a declared contract.

**Scoring guidance**
5 points: rationale 2; safe lifecycle 2; contract caveat 1.


### SYN-Q07 — Synthesis
- **Scope:** U7
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Interpret a positive isolation test.
- **Suggested time:** 10 minutes

**Prompt**
A tenant can read its own secret and is denied reading another tenant's secret. Why are both results needed?

**Model answer**
The denied cross-tenant path checks isolation; the permitted own-tenant path checks that the control has not broken legitimate use. Both need principal/target/action/result evidence.

**Reasoning**
A blanket denial could appear secure while making the platform unusable.

**Common wrong answers / tempting mistakes**
Only test denial; count timeout as denial; assume secret names alone prove tenant ownership.

**Scoring guidance**
5 points: positive/negative distinction 2; evidence 2; limitation 1.


### SYN-Q08 — Synthesis
- **Scope:** U8
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Audit a denominator change.
- **Suggested time:** 10 minutes

**Prompt**
A metric moves from `eligible services` to `active repositories` as denominator. Can the trend be compared directly?

**Model answer**
No. The population and unit of analysis changed. Version the metric definition, report the discontinuity, calculate both definitions over a comparable period if data permits, and do not label the change as adoption improvement.

**Reasoning**
Metric definition is a governed contract. A ratio without stable denominator is not comparable.

**Common wrong answers / tempting mistakes**
Plotting both on one line; assuming denominator labels are interchangeable; hiding the definition change.

**Scoring guidance**
5 points: identify incompatibility 2; restatement plan 2; caveat 1.


### SYN-Q09 — Synthesis
- **Scope:** U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Classify a policy change.
- **Suggested time:** 10 minutes

**Prompt**
A policy changes from warn to deny for all workloads. What kind of change is this?

**Model answer**
It is a high-blast-radius behavioral/security change, not merely a text edit. Run audit impact analysis, coverage and exception review, consumer communication, staged enforcement, rollback and evidence capture. Compatibility semantics depend on the policy contract.

**Reasoning**
Enforcement mode changes can break previously accepted consumers.

**Common wrong answers / tempting mistakes**
Treating as patch-only documentation; applying to all tenants immediately; assuming version number proves compatibility.

**Scoring guidance**
5 points: classification 2; required gates 3.


### SYN-Q10 — Synthesis
- **Scope:** U1–U3
- **Level:** L2
- **Question type:** synthesis
- **Objective tested:** Calculate request completion rate.
- **Suggested time:** 10 minutes

**Prompt**
[SYNTHETIC] Of 50 valid entitled requests, 42 reach usable-ready within the objective window. Calculate the SLI and state the unit.

**Model answer**
42/50 = 84%. The unit is valid entitled requests meeting the defined usable-ready condition within the stated window. The data are synthetic; keep late and failed states visible.

**Reasoning**
The numerator and denominator are defined in the prompt; accepted requests are not the numerator unless accepted is the outcome.

**Common wrong answers / tempting mistakes**
42/58; excluding failed requests; calling 84% a production benchmark.

**Scoring guidance**
5 points: calculation 2; definition 2; caveat 1.


### SYN-Q11 — Synthesis
- **Scope:** U2–U8
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Separate conformance from adoption.
- **Suggested time:** 10 minutes

**Prompt**
A repo is policy-conformant but no team uses the template path. Is the platform successful?

**Model answer**
No conclusion follows from conformance alone. Conformance indicates a defined baseline check passes; adoption measures actual eligible use; developer outcomes and support/SLO evidence show value. Investigate why the path is unused.

**Reasoning**
A secure path nobody uses may still be a product failure or a mandatory control baseline; distinguish safety compliance from product adoption.

**Common wrong answers / tempting mistakes**
Treating conformance as adoption; forcing use to increase adoption; ignoring product outcomes.

**Scoring guidance**
5 points: distinction 3; next evidence 2.


### SYN-Q12 — Synthesis
- **Scope:** U3–U7
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Review delegated-admin privilege.
- **Suggested time:** 10 minutes

**Prompt**
A delegated role can create RoleBindings and patch protected namespace labels. What is the main risk?

**Model answer**
It can grant additional privileges or alter selectors used by isolation policies. Remove these capabilities from delegated admin; route changes through a trusted platform workflow and add negative tests for privilege escalation and label tampering.

**Reasoning**
Delegation should permit bounded operations, not authority expansion.

**Common wrong answers / tempting mistakes**
Only reducing CPU quota; trusting tenant admins to self-police; relying on audit without prevention.

**Scoring guidance**
5 points: risk 2; correction 2; test 1.


### SYN-Q13 — Synthesis
- **Scope:** U4–U5
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Assess portal scaffolder privilege.
- **Suggested time:** 10 minutes

**Prompt**
A Scaffolder action has access to a broad SCM token. What boundary should be reviewed?

**Model answer**
Treat the action as privileged automation. Scope identity to required repository operations, isolate actions, validate user parameters, restrict template locations, audit actions and avoid exposing token values. Exact action/plugin configuration is `[VERIFY]`.

**Reasoning**
Portal actions may create or modify repositories and execute tasks; their backend authority is a supply-chain boundary.

**Common wrong answers / tempting mistakes**
Trusting the UI role alone; sharing admin token with all plugins; logging token for troubleshooting.

**Scoring guidance**
5 points: threat 2; controls 2; verification caveat 1.


### SYN-Q14 — Synthesis
- **Scope:** U6–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Distinguish schema compatibility from behavioral compatibility.
- **Suggested time:** 10 minutes

**Prompt**
A new API schema accepts old YAML, but the default now provisions twice as many replicas. Is the change compatible?

**Model answer**
Not necessarily. The schema may be syntactically backward-compatible while behavior, cost and capacity change. Compare declared contract and observed consumer outcomes; test default behavior, resource impact and migration; classify according to the API's semantic compatibility policy.

**Reasoning**
Compatibility includes defaults and behavior, not just field presence.

**Common wrong answers / tempting mistakes**
Calling it compatible because schema validation passes; assuming higher replicas are always safer; ignoring cost.

**Scoring guidance**
5 points: semantic distinction 2; tests 2; caveat 1.


### SYN-Q15 — Synthesis
- **Scope:** U7–U8
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Interpret tenant-scoped SLO.
- **Suggested time:** 10 minutes

**Prompt**
A shared cluster is healthy overall, but one tenant's queue wait and usable-ready latency breach its target. What should the dashboard show?

**Model answer**
Show aggregate platform health and tenant/team-scoped service outcomes under privacy and access rules. The overall average must not hide a tenant-specific breach. Trigger the defined tenant SLO/runbook and inspect noisy-neighbor or entitlement/capacity factors.

**Reasoning**
Aggregation can conceal tail or tenant-specific failures; scope must match the promise.

**Common wrong answers / tempting mistakes**
Only show cluster average; expose individual developer identity; increase every tenant quota.

**Scoring guidance**
5 points: scoped signal 2; action 2; privacy/cost 1.


### SYN-Q16 — Synthesis
- **Scope:** U1–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Evaluate a forced migration.
- **Suggested time:** 10 minutes

**Prompt**
Leadership mandates a template/API upgrade to remove an unsafe version. What must accompany the mandate?

**Model answer**
A documented security/risk rationale, affected-consumer inventory, supported replacement, migration guide/automation, design-partner support, staged rollout, expiring exceptions with compensating controls, communication and removal gate. Mandatory safety baseline does not justify opaque or unsupported migration.

**Reasoning**
The syllabus allows mandates for safety-critical baselines with enablement; voluntary product adoption remains the default for convenience capabilities.

**Common wrong answers / tempting mistakes**
Mandate without support; indefinite exceptions; force update with no rollback or consumer inventory.

**Scoring guidance**
5 points: rationale 1; migration/support 2; exception/ring/evidence 2.


### SYN-Q17 — Synthesis
- **Scope:** U2–U7
- **Level:** L3
- **Question type:** synthesis
- **Objective tested:** Check default provenance.
- **Suggested time:** 10 minutes

**Prompt**
A golden-path default requires `runAsNonRoot`, but the register lists no source or negative test. What is missing?

**Model answer**
Record source module/control, reason, owner and exact verification test. Add a planted unsafe fixture and assert the policy rejects it; if the runtime layer is available, verify admission consistency separately. A documented default without a test is an assertion, not proof.

**Reasoning**
The default→source→reason→test chain makes policy reviewable.

**Common wrong answers / tempting mistakes**
Assuming the manifest value proves enforcement; using only a positive test; attributing an unsupported module requirement.

**Scoring guidance**
5 points: register fields 2; negative test 2; fidelity limit 1.


### SYN-Q18 — Synthesis
- **Scope:** U3–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Audit an exception renewal.
- **Suggested time:** 10 minutes

**Prompt**
An exception expires tomorrow; owner requests renewal but no new evidence is attached. What should the reviewer do?

**Model answer**
Do not auto-renew. Reassess scope, reason, compensating control, current exposure, migration progress and owner/approver; require fresh evidence and a new bounded expiry. If the control is mandatory and no safe compensation exists, deny renewal and plan mitigation.

**Reasoning**
Expiry is an active governance control, not a reminder date.

**Common wrong answers / tempting mistakes**
Renew automatically; convert to permanent waiver; ignore because the owner is known.

**Scoring guidance**
5 points: decision 2; review fields 2; safety gate 1.


### SYN-Q19 — Synthesis
- **Scope:** U4–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Separate portal availability from data correctness.
- **Suggested time:** 10 minutes

**Prompt**
A portal is available but a catalog ingestion job has been failing for 48 hours. What is the correct status?

**Model answer**
Portal availability may remain green, but catalog freshness/data quality should be degraded. Show the last successful ingestion, affected entities, fallback owner source and remediation. Avoid presenting stale data as current.

**Reasoning**
Different SLIs represent distinct user-visible capabilities and failure modes.

**Common wrong answers / tempting mistakes**
Mark all platform services down; ignore because HTTP health is green; delete stale metadata.

**Scoring guidance**
5 points: status distinction 2; evidence 2; fallback 1.


### SYN-Q20 — Synthesis
- **Scope:** U2–U7–U8
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Respond to a security-sensitive golden-path default copied into many services.
- **Suggested time:** 12 minutes

**Prompt**
[SYNTHETIC INCIDENT] A golden-path template disables TLS certificate verification. It has already been copied into several generated repositories. What is the safe response?

**Model answer**
Stop further template release/generation and preserve the exact template revision, generated-repository inventory and deployment evidence. Identify affected services and whether the insecure setting is active at runtime. Publish a clear advisory, issue a verified corrected release, scan consumers and open reviewed migration PRs. Add a planted negative fixture that fails when TLS verification is disabled; run conformance and runtime checks where available; canary by archetype. Do not silently rewrite team-owned files.

**Reasoning**
A template default has fleet blast radius. Generation count is not a measure of affected runtime use; evidence must distinguish generated, deployed and active.

**Common wrong answers / tempting mistakes**
Only edit the source template and assume existing repos update; disable all TLS; mass-overwrite every repository without owner review.

**Scoring guidance**
10 points: stop/scope 2; evidence 2; safe migration 2; negative test 2; communication 2.


### SYN-Q21 — Synthesis
- **Scope:** U2–U5–U7
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Contain credential exposure caused by a missing notebook archetype.
- **Suggested time:** 12 minutes

**Prompt**
[SYNTHETIC INCIDENT] Data scientists bypass the golden path and run notebooks containing embedded credentials because the supported path is too burdensome. What should the platform team do?

**Model answer**
Use the approved incident process to revoke/rotate any exposed credential and preserve authorized audit evidence. Do not copy or expose real secret values. Observe the notebook workflow and identify friction; provide an appropriate notebook/experiment archetype with workload identity, secret references, idle/TTL lifecycle and output/secret scanning. Keep mandatory controls in force and measure task friction with privacy-safe team-level signals.

**Reasoning**
The bypass indicates both a security incident and a product gap. Fixing only the credential leak may leave the incentive to bypass unchanged.

**Common wrong answers / tempting mistakes**
Blame users; add a policy ban without a usable alternative; keep credentials in notebooks but encrypt the file.

**Scoring guidance**
10 points: containment 2; evidence/secret safety 2; product diagnosis 2; safer path 2; tests/measurement 2.


### SYN-Q22 — Synthesis
- **Scope:** U2–U8–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Balance CI feedback latency and mandatory controls.
- **Suggested time:** 12 minutes

**Prompt**
[SYNTHETIC INCIDENT] Golden-path CI takes 25 minutes in the scenario. Teams use an admin bypass to skip checks. How should the platform respond?

**Model answer**
Treat 25 minutes as a synthetic scenario premise, not a benchmark. Preserve bypass/audit evidence; remove broad admin bypass authority; profile individual check stages and separate fast local/PR checks from slower integration checks. Optimize safe caching/parallelism and test reliability, but keep mandatory security checks. Define risk-based emergency exception with expiry, track feedback latency and bypass reasons, and remeasure.

**Reasoning**
The problem is not solved by making all checks optional. Slow feedback creates a predictable incentive to evade controls; the platform owns usability and safe enforcement.

**Common wrong answers / tempting mistakes**
Accept the bypass because CI is slow; remove every policy check; increase runner size without measuring bottlenecks.

**Scoring guidance**
10 points: containment 2; evidence 2; performance diagnosis 2; safe controls 2; remeasurement 2.


### SYN-Q23 — Synthesis
- **Scope:** U3–U5–U6–U7
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Prevent an unbacked database from being advertised as ready.
- **Suggested time:** 12 minutes

**Prompt**
[SYNTHETIC INCIDENT] A generated service provisions a database but the template omitted the required backup policy. The portal shows the database capability as ready. What is the correct response?

**Model answer**
Stop claiming the capability is production-ready and identify affected databases and data owners. Preserve provisioning/configuration evidence; determine whether safe backup can be taken and verify restore in the approved lab/operating process. Correct the template/API contract and readiness gate so backup class and evidence are required for the applicable tier. Add a planted missing-backup test and a restore acceptance check; communicate the current limitation and do not claim recoverability until tested.

**Reasoning**
A database object and endpoint do not prove recoverability. The platform default is part of the product contract.

**Common wrong answers / tempting mistakes**
Enable backups globally without checking data/retention; delete the database; mark ready because the connection works.

**Scoring guidance**
10 points: truthful status 2; inventory/data safety 2; restore evidence 2; contract/test fix 2; communication 2.


### SYN-Q24 — Synthesis
- **Scope:** U3–U7–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Contain cross-team impact from a shared development database.
- **Suggested time:** 12 minutes

**Prompt**
[SYNTHETIC INCIDENT] One team's test/reset process wipes data used by another team in a shared development database. What should happen?

**Model answer**
Contain writes/reset automation and preserve audit/query/job evidence. Identify affected schemas, principals, data owners and backup/restore options. Do not restore blindly over newer valid writes. Communicate scope and recovery choices; then separate schemas/instances or enforce tenant-scoped credentials, ownership, reset boundaries and retention. Add cross-team data-isolation and restore tests, plus an explicit shared-service support contract.

**Reasoning**
The failure is a data-isolation and lifecycle-boundary defect, not merely a bad developer command.

**Common wrong answers / tempting mistakes**
Immediately restore the oldest backup; grant both teams admin; assume namespaces isolate an external shared database.

**Scoring guidance**
10 points: containment/evidence 3; data-owner/recovery decision 2; isolation correction 3; regression/governance 2.


### SYN-Q25 — Synthesis
- **Scope:** U1–U9
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Repair governance that is too slow and drives unsafe bypasses.
- **Suggested time:** 12 minutes

**Prompt**
[SYNTHETIC INCIDENT] RFC review takes six weeks even for a low-risk documentation change. Teams bypass governance. How should the process change without weakening high-risk review?

**Model answer**
Classify changes by blast radius and reversibility. Move low-risk docs/internal edits to owner review and automated checks; retain time-boxed RFC/consumer input for high-impact policy/API/security changes. Publish decision rights, response targets as illustrative policy, escalation and sunset rules; monitor bypasses, cycle time and post-change defects. Preserve an emergency security path with explicit risk evidence.

**Reasoning**
Governance failure can be excessive friction as well as insufficient control. Proportionality and clear decision rights restore legitimacy.

**Common wrong answers / tempting mistakes**
Remove all RFCs; keep the same six-week queue; make every change a platform-council decision.

**Scoring guidance**
10 points: risk classification 2; proportional workflow 3; decision rights 2; measures 2; emergency path 1.


### SYN-Q26 — Synthesis
- **Scope:** U4–U9–U6
- **Level:** L4
- **Question type:** synthesis
- **Objective tested:** Respond to an unmaintained portal plugin vulnerability.
- **Suggested time:** 12 minutes

**Prompt**
[SYNTHETIC INCIDENT] A portal plugin has an unpatched vulnerability and no clear maintainer. What is the platform response?

**Model answer**
Preserve dependency inventory, version, exposure path and logs; disable or isolate the affected plugin if safe; assess privileged actions and data access; rotate/revoke exposed credentials if warranted; communicate portal capability degradation and use static fallback. Identify maintainer/project-health evidence, upgrade or replace with a supported alternative, and review plugin permissions. Add dependency-health ownership, security advisory intake, upgrade budget and exit strategy. Project status and vulnerability details require primary-source verification.

**Reasoning**
A plugin is a supply-chain and privileged-component dependency. The portal must remain useful without it.

**Common wrong answers / tempting mistakes**
Assume the plugin is safe because it is popular; update to latest without compatibility testing; keep it enabled because portal availability is important.

**Scoring guidance**
10 points: containment/evidence 2; exposure/identity assessment 2; fallback/communication 2; upgrade/exit plan 2; governance 2.


---

## Design-review / whiteboard prompts — 16 prompts

These prompts require a defended design rather than a copied architecture. They are additional assessments and are not included in the 185 numbered-question total.

### DR-01 — Platform vision and thinnest viable first release

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

A data/ML organization has repeated setup friction but no validated need for a full portal. Define the platform vision and first release.

**Required deliverables**

Deliver: user/job, baseline, first-slice scope/non-goals, capability map, owners/support, measures, build/adopt/buy ADRs.

**Strong model-answer outline**

Start with the manual developer journey and validated friction; define one end-to-end API or batch path; reuse M01–M15; document ownership, support, SLO and escape hatch; make defaults secure/observable/cost-aware; measure local n=1 and plan real user research. Exclude broad portal/orchestrator/GPU service until evidence supports it.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Problem/user evidence 2; TVP and non-goals 2; capability ownership 2; safety/operations 2; measurement/evidence 2.

**Common failure patterns**

Feature list without user job; treating synthetic interviews as real; no on-call/support; platform as mandatory framework.

**L4 follow-up**

At L4, what evidence would cause you to expand, narrow or sunset the first slice?


### DR-02 — Golden paths for API, batch and model-serving

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Three workload archetypes share a platform but have different runtime semantics. Design the golden-path family.

**Required deliverables**

Deliver: shared core, archetype layers, default/option/escape policy, policy tests, conformance definition and support tiers.

**Strong model-answer outline**

Share identity, repo metadata, hardened image, least-privilege CI, supply-chain, catalog, SLO/runbook and cost conventions. API adds request/readiness; batch adds schedule/idempotency/freshness; model-serving adds immutable model digest/card, serving readiness and rollout. Preserve escape hatches while mandatory controls remain enforced.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Shared controls 2; archetype-specific behavior 2; escape/support policy 2; conformance/negative tests 2; rollout/evidence 2.

**Common failure patterns**

One template for all; no escape; policy checked only on source YAML; generated output treated as production proof.

**L4 follow-up**

How would streaming and notebook/experiment paths change your design?


### DR-03 — Self-service request flow

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Design a safe request flow for a tenant environment with PostgreSQL and object storage options.

**Required deliverables**

Deliver: canonical schema, identity/entitlement checks, policy/cost, status state machine, GitOps/controller boundary, cleanup and SLOs.

**Strong model-answer outline**

One canonical request object; multiple front doors; authenticated principal mapped to entitlement; schema→entitlement→CI policy→admission→quota/capacity→controller stages; idempotent desired state; safe secret references; status distinguishes accepted/reconciled/usable-ready; cleanup checks retention, dependencies and orphans.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Contract 2; authz/layering 2; idempotency/status 2; data safety/cleanup 2; SLO/evidence 2.

**Common failure patterns**

Portal-only validation; credential in request; status `done` after sync; delete namespace without inventory.

**L4 follow-up**

How do you handle retries after a timeout that occurred after a database was created?


### DR-04 — Thin static portal versus Backstage

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

A learner has 4 CPU, 8 GB RAM and 30 GB disk. The organization needs service discovery and owner/runbook links.

**Required deliverables**

Deliver: architecture decision, resource plan, trust model, fallback, preflight and operating responsibilities.

**Strong model-answer outline**

Start with catalog-as-code, Python linter, deterministic static generator, safe escaping, freshness/drift, owner/dependency links and fallback. Backstage is optional only after Node/yarn/memory preflight and should run alone in Plat+Portal; lab guest auth and local catalog only. Keep platform API and authz independent of portal.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

User need 2; resource fit 2; catalog trust 2; auth/fallback 2; lifecycle/evidence 2.

**Common failure patterns**

Backstage mandatory; all heavy components together; guest auth publicly exposed; portal becomes policy authority.

**L4 follow-up**

What would justify migrating from the thin portal to Backstage in a larger organization?


### DR-05 — Copier versus Cookiecutter and update strategy

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

The platform needs new repo generation plus safe updates across existing repositories.

**Required deliverables**

Deliver: decision criteria, parameter contract, execution threat model, update workflow and version-verification list.

**Strong model-answer outline**

Use Copier as primary course path because the syllabus selects an update-aware workflow; compare Cookiecutter without asserting unverified update semantics. Validate minimal parameters before tasks, pin and verify template source, separate platform/team-owned files, preview updates, classify conflicts, require owner review and test every consumer. Verify exact CLI/trust/update behavior for installed versions.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Decision rationale 2; parameter/security contract 2; provenance 2; conflict/update plan 2; verification 2.

**Common failure patterns**

Claiming a CLI flag from memory; untrusted task execution; auto-overwrite; assuming `.copier-answers.yml` proves conformance.

**L4 follow-up**

How would you run an emergency security update across a repo fleet without auto-merging conflicts?


### DR-06 — Developer-friendly platform API

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Design one of `DataEnvironment`, `PostgresDatabase` or `ModelEndpoint` for the running platform.

**Required deliverables**

Deliver: user contract, schema, validation, status, ownership, security, lifecycle and migration.

**Strong model-answer outline**

Expose intent, few fields, safe defaults, enums, descriptions, immutable identity where needed and clear status conditions. Derive team from trusted principal; keep provider credentials private; define accepted/reconciled/usable states; provide secret-safe diagnostics, tests, support owner and API lifecycle. Exact Crossplane schema/field syntax is version-sensitive.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Consumer contract 2; validation/authz 2; status/debuggability 2; security/lifecycle 2; verification 2.

**Common failure patterns**

Provider-shaped form; raw credentials; no status contract; treating object creation as ready.

**L4 follow-up**

What evidence is needed before alpha becomes beta and beta becomes GA?


### DR-07 — Crossplane versus Terraform-via-PR versus Helm-as-API

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

A team needs to provision a database with retention and lifecycle controls. Defend an implementation approach.

**Required deliverables**

Deliver: decision matrix, lifecycle, ownership, state/deletion, audit and operating-cost analysis.

**Strong model-answer outline**

Choose Crossplane if persistent reconciliation and controller ownership justify it and provider/cloud-free capabilities are verified; Terraform-via-PR if reviewable plans and bounded lifecycle are central; Helm-as-API only if chart lifecycle maps the contract and no richer controller semantics are required. Include backups/restore, deletion, secret boundary, versioning and tests.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Use-case fit 2; lifecycle/deletion 2; security 2; cost/ops 2; evidence/verification 2.

**Common failure patterns**

Tool-first choice; treating Helm release as recoverability; ignoring external resource deletion semantics.

**L4 follow-up**

What changes if the database is multi-tenant and contains regulated business data?


### DR-08 — Tenancy model by trust tier

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Choose isolation models for analytics, ML research and high-sensitivity risk workloads.

**Required deliverables**

Deliver: adversary/asset model, tier matrix, control layers, cost and operational trade-offs.

**Strong model-answer outline**

Use soft tenancy only where shared trust assumptions are explicit and layered controls are adequate. Sensitive tiers may require stronger node, control-plane, identity or cluster boundaries. Specify identity/RBAC, network, compute, storage, secrets, registry/CI, ingress, observability, cost and control-plane controls. Do not call namespaces hard isolation.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Threat model 2; tier choice 2; layered controls 2; positive/negative evidence 2; cost/limits 2.

**Common failure patterns**

Same model for every tenant; namespace as hard boundary; no test of allowed paths.

**L4 follow-up**

Which new threat or evidence would force a tier upgrade to a separate cluster?


### DR-09 — Tenant onboarding and offboarding

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Design onboarding/offboarding as verified tenant lifecycle workflows.

**Required deliverables**

Deliver: request/state machine, approval/entitlement, isolation gate, data export/hold, revocation, deletion and audit.

**Strong model-answer outline**

Onboarding validates principal, entitlement, trust tier, owner, cost center and baseline; creates resources idempotently; runs at least the capstone-required isolation suite (≥25 tests per tenant pair) and positive checks before ready. Offboarding inventories data/dependencies, checks retention/hold, exports as approved, revokes access, deletes in dependency order, scans orphans and records audit.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Identity and owner 2; isolation tests 2; data/hold lifecycle 2; revocation/deletion 2; audit/recovery 2.

**Common failure patterns**

Namespace deletion as offboarding; TTL overrides hold; timeout counted as denial.

**L4 follow-up**

How should the workflow recover if the database is deleted but the bucket cleanup fails?


### DR-10 — Platform SLOs and developer journey probe

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Define platform SLOs and a synthetic developer-journey probe.

**Required deliverables**

Deliver: SLI/SLO definitions, probe stages, error-budget policy, failure alerts, fallback and fidelity statement.

**Strong model-answer outline**

Measure request accepted, provisioned and usable-ready separately; journey includes repo/template, CI-equivalent, deploy, observe and teardown. Define denominator, window, eligible population, exclusions and failure states. Add error-budget action for risky changes, burn alerts and synthetic probe with safe fixtures. Label local n=1 and synthetic results.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

User outcome 2; metric contract 2; probe stages 2; error-budget/runbook 2; fidelity 2.

**Common failure patterns**

Homepage HTTP 200 as full success; no teardown; synthetic probe results presented as real adoption.

**L4 follow-up**

How do you distinguish a platform SLO breach from a single tenant's workload-specific failure?


### DR-11 — Adoption data with confounders

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

A dashboard suggests teams using the golden path deploy more frequently. Design a defensible analysis.

**Required deliverables**

Deliver: metric contract, cohorts, data-quality checks, confounders, causal caution and privacy.

**Strong model-answer outline**

Define eligible population and adoption version; validate missing/duplicate events; segment by archetype and team-level cohort; inspect workload complexity, staffing, maturity, selection and concurrent changes; compare pre/post or matched cohorts cautiously; use qualitative research; report uncertainty. Never rank individuals; synthetic dataset demonstrates methods only.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Denominator 2; data quality 2; confounders 2; causal caveat 2; privacy 2.

**Common failure patterns**

Comparing unlike cohorts; changing definitions mid-series; claiming causation from correlation; individual tracking.

**L4 follow-up**

What evidence would make a difference-in-differences interpretation more credible, and what assumption remains fragile?


### DR-12 — Developer-experience research plan

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Plan a DX study for the first release without a real developer population in the lab.

**Required deliverables**

Deliver: synthetic method exercise, real-user research plan, tasks, metrics, consent/privacy approach and limitations.

**Strong model-answer outline**

Use supplied synthetic interviews/tickets to practice coding and prioritization; label synthetic. For real organizational claims, recruit real users with transparent purpose, representative roles, observation and usability tasks; measure task completion/time/errors and collect qualitative friction. Minimize data, aggregate, state n/response bias and avoid individual rankings.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Method fit 2; sample/uncertainty 2; task metrics 2; privacy 2; fidelity statement 2.

**Common failure patterns**

Treating synthetic personas as actual participants; ranking named engineers; treating response share as population satisfaction.

**L4 follow-up**

What changes when the sample is only three teams and one workload archetype?


### DR-13 — Deprecate a widely used artifact

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Deprecate a base image or platform API while consumers and approved exceptions remain.

**Required deliverables**

Deliver: inventory, owner, replacement, fresh usage evidence, migration, warnings, rings, exceptions, removal gate and rollback.

**Strong model-answer outline**

Inventory versions, owners, backup owners, direct/indirect consumers and support state; verify usage freshness; define replacement and compatibility; publish deprecation/migration guidance; open migration PRs; maintain scoped expiring exceptions; stage release rings; run positive/negative tests; remove only after consumer, data and rollback gates pass.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Inventory 2; migration 2; exception 2; rings/rollback 2; removal evidence 2.

**Common failure patterns**

Immediate removal; stale usage scan; indefinite exception; SemVer label as sole proof.

**L4 follow-up**

How does the process differ for a security-critical base image versus a noncritical catalog schema?


### DR-14 — Governance proportional to blast radius

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Set governance for a docs typo, template default, policy enforcement change and breaking API.

**Required deliverables**

Deliver: risk tiers, decision rights, review and test requirements, rollout and evidence.

**Strong model-answer outline**

Use reversibility, blast radius, security/data impact and consumer count. Docs typo: owner review. Template default: generated-output tests and canary. Policy enforcement: audit impact, coverage, exceptions, communication and staged enforcement. Breaking API: RFC/consumer input, compatibility matrix, migration, versioning, rings and rollback. State thresholds as illustrative.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Risk model 2; proportionality 2; consumer input 2; tests/rings 2; evidence 2.

**Common failure patterns**

Same approvals for every change; no review for policy; full council for typo.

**L4 follow-up**

What emergency path is justified for a vulnerability that cannot wait for the ordinary review window?


### DR-15 — Platform team boundaries, support and funding

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Design platform team boundaries and interactions with product, security, SRE and finance.

**Required deliverables**

Deliver: capability ownership map, RACI, support/intake, on-call, escalation, funding/showback and roadmap.

**Strong model-answer outline**

Platform team owns shared APIs, templates, portal/catalog, guardrails, documentation and platform reliability; product teams own application behavior and service operation within the contract; security defines mandatory policy and reviews high-risk exceptions; SRE partners on SLO/incident practices; finance provides cost allocation. Define support channel, office hours, triage, on-call and prioritization.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Ownership/RACI 2; support model 2; reliability 2; stakeholder/funding trade-offs 2; adoption/feedback 2.

**Common failure patterns**

Platform owns all deployments; no platform on-call; ticket queue as product; individual usage targets.

**L4 follow-up**

How should interaction modes change as the platform team grows from one small team to domain-aligned platform teams?


### DR-16 — Threat-model platform supply chain and privileged components

- **Scope:** M16 design review; related units are stated in the scenario.
- **Level:** L2–L4, increasing through the follow-up.
- **Question type:** design-review / whiteboard.
- **Suggested time:** 30–45 minutes.
- **Objective tested:** defend a platform design with explicit assumptions, evidence, safety and operating consequences.

**Scenario**

Threat-model templates, GitOps hub, Crossplane providers, portal tokens, plugins and update bots.

**Required deliverables**

Deliver: assets/trust boundaries, threat scenarios, least-privilege controls, negative tests, incident response and residual risk.

**Strong model-answer outline**

Identify code/data inputs, privileged identities, artifact sources, tenant boundaries and blast radius. Pin and verify template/provider/plugin sources; sign/provenance where supported; validate parameters before execution; isolate tasks; scope bot/provider/portal identities; protect secrets; restrict catalog locations; audit actions; run benign negative tests for injection, privilege escalation and unauthorized cross-tenant operations.

**Trade-off table**

| Option | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Lean / PR-first / static / bounded approach | Lower operating burden; easier to inspect and run on the laptop | Less integrated UX or continuous automation; some manual review remains | The user need is narrow, resource limits are binding, or the organization is small |
| Rich / controller-backed / framework-led approach | More discoverability, automation or continuous reconciliation | More components, privileges, upgrades, on-call and failure modes | Measured user demand and team capability justify the additional product surface |
| Hybrid / staged approach | Preserves a safe Core path while adding capability behind gates | Requires clear boundaries and version/compatibility discipline | The platform must serve varied teams without making heavy components mandatory |

**Scoring rubric (10 points)**

Assets/actors 2; trust boundaries 2; controls 2; negative tests 2; residual-risk statement 2.

**Common failure patterns**

Trusting tags; shared admin tokens; arbitrary template hooks; treating a passing namespace test as hard multi-tenancy proof.

**L4 follow-up**

What is the first containment action if a template source or portal bot identity is suspected compromised?


---

## Overall scoring, remediation and audit

## Overall scoring rubric and level-by-level interpretation

### Overall decision bands

| Normalized score | Decision | Required action |
|---:|---|---|
| **80% or higher** | Proceed to the next M16 learning activity | Review missed explanations and complete every failed practical check. A high percentage does not override a failed security, isolation or destructive-change safety gate. |
| **60–79%** | Targeted remediation | Revisit the weak unit/level/topic, redo its artifact or lab, then retake a different question subset. |
| **Below 60%** | Repeat core material | Re-study the relevant unit foundations and guided examples, complete the corresponding Core lab, then reattempt after practice. |

### Competence gates that override the percentage

A learner must remediate before progression if they:

- Accept an unauthorized tenant request or cannot identify the entitlement boundary.
- Treat a namespace as proof of hard multi-tenancy or count an ambiguous timeout as a successful denial.
- Approve unsafe template/task execution, broad bot/provider/portal privileges or credential exposure.
- Approve a destructive composition, database, bucket or tenant deletion without impact, retention, backup and recovery evidence.
- Treat request acceptance, GitOps sync or object creation as usable readiness.
- Use individual developer rankings or present synthetic/laptop data as real population evidence.
- Roll out a breaking shared change without compatibility evidence, impact analysis, rings and a defensible rollback/mitigation plan.

### Level interpretation

| Level | Evidence of competence | Remediation when weak |
|---|---|---|
| **L1** | Precise definitions, correct boundaries, correct reading of simple artifacts. | Re-read unit concept map and vocabulary; explain the concept in your own words and give a data/ML example. |
| **L2** | Correct local artifacts, schema/contract interpretation, positive and negative checks, safe guided workflow. | Re-run the relevant Plat-Core lab with a planted defect; retain the input, test result and corrected artifact. |
| **L3** | Defended architecture, explicit trade-offs, least privilege, operational evidence, versioning and cost/resource fit. | Write an ADR and test matrix; compare at least two options and document assumptions, rejected options and residual risks. |
| **L4** | Safe incident ordering, blast-radius control, change governance, communication, recovery verification and prevention. | Run a tabletop with a new inject; produce timeline, evidence list, mitigation decision, owner-assigned follow-ups and verification criteria. |

### Per-unit score and level breakdown

For each unit, record:

- normalized unit score;
- L1/L2/L3/L4 points available and earned;
- question-type scores (conceptual, MCQ, artifact interpretation, artifact review, incident, design);
- safety-gate status;
- remediation artifact and retake date.

Do not infer L4 competence from a high L1 score. A learner can know terminology yet still make unsafe incident or rollout decisions.

## Unit-by-unit remediation guide

| Missed concept / recurring mistake | Revisit | Required remediation evidence |
|---|---|---|
| Portal = platform; platform engineering = renamed ops queue; no user/job evidence | [Unit 1](01-platform-engineering-principles-and-platform-as-a-product.md) | One-page user/job/problem statement, manual-baseline record, capability map and explicit non-goals. |
| Treating golden path as mandatory; template = full path; no negative tests | [Unit 2](02-golden-paths-templates-and-paved-roads.md) | Default→source→reason→test register, supported escape policy and planted unsafe-default test. |
| Confusing schema, entitlement, admission, quota and controller failures; accepted = ready | [Unit 3](03-self-service-infrastructure-and-environment-provisioning.md) | Rejection-layer decision table, canonical request fixture, usable-readiness probe and safe cleanup evidence. |
| Catalog string treated as truth; authn confused with authz; Backstage required on 8 GB | [Unit 4](04-developer-portals-and-backstage-service-catalog.md) | Catalog linter output, owner/freshness report, static fallback and portal preflight decision. |
| Generation confused with updates; untrusted tasks; bot overwrites local changes | [Unit 5](05-scaffolding-and-software-templates.md) | Template provenance record, parameter negative tests, update preview, conflict resolution and bot permission review. |
| Provider-shaped API; secrets in spec/status; no deletion/rollout safety | [Unit 6](06-platform-apis-with-crossplane-compositions.md) | API contract, schema/render test, status contract, RBAC negative test and destructive-impact report. |
| Namespace called hard boundary; missing positive tests; unsafe offboarding | [Unit 7](07-multi-tenancy-isolation-and-tenant-onboarding.md) | Tenant threat model, per-pair isolation matrix, allowed/denied test evidence and offboarding/orphan report. |
| API uptime used as developer SLO; denominator drift; causal claims from correlation | [Unit 8](08-platform-slos-adoption-metrics-and-developer-experience.md) | Metric contract, data-quality tests, cohort/confounder note, privacy scan and usable-journey SLO. |
| SemVer treated as proof; exception has no expiry; policy enforcement rolled out globally | [Unit 9](09-platform-governance-deprecation-and-versioning.md) | Compatibility matrix, breaking-change classification, policy impact report, deprecation record and staged release plan. |

### Retake plan

1. Select the lowest-scoring unit and the highest-risk missed concept; do not retake all 185 questions immediately.
2. Read the relevant lesson section and the linked M01–M15 prerequisite only if the M16 question depends on that prior mechanism.
3. Recreate the synthetic artifact from scratch with different names/values.
4. Add one positive and one negative test where applicable.
5. Reattempt at least one conceptual, one artifact and one incident/design question from the weak topic.
6. Record the evidence and remaining uncertainty. Do not use memorized answer wording as the success criterion.

## Technical authenticity and source-verification register

No live external documentation was accessed while producing this question bank. The following checks are therefore `[VERIFY]`; the questions are written so the core reasoning can be answered without relying on an unverified CLI flag, field, plugin name or version-specific behavior.

| Claim / question area | Why version-sensitive or uncertain | Primary source to consult | Exact check needed | Status | Answerable without uncertain detail? |
|---|---|---|---|---|---|
| Backstage catalog descriptor, entity kinds, relations, annotations and locations | Schema and supported conventions may change by release. | Backstage Software Catalog documentation; descriptor format and entity model | Validate the exact fields/relations/annotations used by the pinned local release and test owner/dependency references. | `[VERIFY]` | Yes; questions test provenance, ownership and data quality. |
| Backstage Scaffolder templates/actions/custom actions | Action IDs, configuration and execution model are release-sensitive. | Backstage Scaffolder documentation; templates and actions | Confirm each action ID/config and task execution boundary for the pinned release. | `[VERIFY]` | Yes; privilege and input-validation reasoning remains applicable. |
| Backstage auth, permissions, guest mode, deployment and plugins | Auth configuration, permission framework and package/plugin status can change. | Backstage authentication, permissions, deployment and upgrade documentation | Verify lab-only guest auth, authorization enforcement, supported plugin packages and upgrade path. | `[VERIFY]` | Yes; authn/authz separation is version-independent. |
| Crossplane composition model, XRDs, claims and namespaced XRs | Recommended composition and claim patterns have changed across major versions. | Crossplane documentation; concepts, XRDs, Compositions, Composition Functions and claims | Record exact release and verify scope/model, fields and controller behavior before using examples. | `[VERIFY]` | Yes; contract, blast-radius and lifecycle questions do not depend on exact syntax. |
| Crossplane functions, CLI render/validate and provider-kubernetes/provider-helm | Package names, APIs, fields, flags and provider capabilities are version-specific. | Crossplane CLI and provider documentation | Confirm exact package, function, provider capability, API version and command flags for the pinned set. | `[VERIFY]` | Yes; treat exact syntax as a verification task. |
| Crossplane deletion, composition revision and update policy semantics | Resource lifecycle and update behavior can have destructive effects. | Crossplane documentation; managed resource deletion, composition revisions and update policies | Verify how selected release handles immutable fields, Delete/Orphan, revision promotion and rollback. | `[VERIFY]` | Yes; questions ask for impact analysis before mutation. |
| Copier questions, `copier.yml`, answers file, tasks, migrations and `--trust` | Trust/task and update semantics may vary by release. | Copier official documentation; configuration, questions, tasks, migrations and update | Verify exact CLI flags, trust behavior, answers file and migration/conflict semantics. | `[VERIFY]` | Yes; never rely on an unverified flag. |
| Cookiecutter hooks and update behavior | Cookiecutter generation/hook semantics must not be conflated with Copier updates. | Cookiecutter official documentation; templates, hooks and `cookiecutter.json` | Verify current hook behavior and do not attribute Copier update features to Cookiecutter. | `[VERIFY]` | Yes; comparison is based on stated needs and verified behavior. |
| Kubernetes CRD schema and CEL validation | API versions, CEL support and field placement depend on Kubernetes release. | Kubernetes documentation; Custom Resources and CEL validation | Validate CRD schema, CEL rule placement and API server support for selected cluster version. | `[VERIFY]` | Yes; questions test validation boundaries, not an unverified expression. |
| Kubernetes API deprecation, RBAC, namespaces, PSS, APF and multi-tenancy | Exact feature behavior and policy details vary by release and configuration. | Kubernetes documentation; API deprecation policy, RBAC, namespaces, Pod Security Standards, APF and multi-tenancy | Check feature maturity, defaults and selected cluster behavior. | `[VERIFY]` | Yes; namespace-not-hard-boundary and least-privilege principles remain. |
| Argo CD applications/projects/sync policies and rollout behavior | API fields and sync semantics can vary by version/configuration. | Argo CD official documentation; Application, Projects and sync policy | Verify selected release schema and how drift, pruning and sync are configured. | `[VERIFY]` | Yes; questions assess GitOps ownership and safe rollout. |
| Kyverno versus ValidatingAdmissionPolicy specifics | Policy syntax, admission integration and capabilities differ. | Kyverno documentation; Kubernetes ValidatingAdmissionPolicy documentation | Verify exact policy engine version, rule syntax and denial/audit behavior. Use one engine at a time in the lab. | `[VERIFY]` | Yes; questions focus on policy layers and negative tests. |
| KEDA scaling and queue semantics | Scaler metadata and supported metrics depend on version and backend. | KEDA official documentation; ScaledObject and scaler references | Verify exact scaler configuration and queue/lag semantics if used. | `[VERIFY]` | Yes; no exact KEDA field is required by these questions. |
| OpenCost and cost allocation semantics | Product health, configuration and allocation semantics can change. | OpenCost official documentation; allocation and integration guides | Verify selected release and allocation rules before using a real integration. | `[VERIFY]` | Yes; cost questions use hypothetical HCU or source-defined labels. |
| JSON Schema validation dialect | Keywords and dialect support depend on validator and schema version. | JSON Schema specification; selected dialect documentation | Pin the dialect and verify keyword support in the validator used by the lab. | `[VERIFY]` | Yes; conceptual schema/validation questions remain. |
| Team Topologies, TVP and interaction-mode terminology | Framework wording and attribution require primary-source verification. | Team Topologies (Skelton & Pais), by title | Verify exact terminology/attribution before quoting or presenting it as a formal definition. | `[VERIFY]` | Yes; questions use the M16 syllabus framing. |
| CNCF platform maturity references | White Paper and maturity model wording/status may evolve. | CNCF Platforms White Paper and Platform Engineering Maturity Model, by title | Verify current document title, edition and exact maturity terminology. | `[VERIFY]` | Yes; no maturity score is required. |
| SPACE, DevEx and DX Core 4 | Framework definitions and attribution should be checked from primary publications. | SPACE framework paper; DevEx and DX Core 4 materials, by title | Verify original source and wording; do not reproduce quotes or unsupported benchmarks. | `[VERIFY]` | Yes; questions test survey and measurement rigor. |
| DORA metrics and research publications | Definitions/report editions and measurement cautions need source/year context. | DORA research publications; M10 Unit 11 | Verify the relevant report/year and reuse M10 definitions; do not cite unverified industry figures. | `[VERIFY]` | Yes; no external benchmark figure is used. |
| Google SRE error-budget and release-engineering references | Exact guidance should be tied to source chapters and organizational policy. | Google SRE Book and Workbook; SLO, error-budget and release-engineering chapters | Confirm the relevant chapter and distinguish source guidance from local policy. | `[VERIFY]` | Yes; the bank asks for explicit policy reasoning. |
| SemVer and Kubernetes deprecation policy | SemVer labels require a declared artifact contract; Kubernetes policy is version-specific. | Semantic Versioning 2.0.0; Kubernetes API deprecation policy | Verify exact rules and define artifact-specific compatibility separately. | `[VERIFY]` | Yes; classification is based on stated consumer contract. |
| Sigstore/cosign, SLSA and OWASP supply-chain guidance | Exact signing/provenance formats and recommendations depend on version/context. | Sigstore/cosign documentation; SLSA documentation; OWASP guidance | Verify selected signing tool, trust root, attestation format and applicable threat guidance. | `[VERIFY]` | Yes; questions test trust boundaries and provenance principles. |
| Frameworks and external research statistics | The course forbids unverified quotes, adoption/productivity/ROI/survey figures. | Primary sources named above | Use only when a specific framework claim is needed; record source title/edition; do not insert external statistics. | `[VERIFY]` | Yes; no industry statistic is required. |

### Source-derived requirements versus supporting engineering judgment

The nine unit titles/order, learner prerequisites, lab profiles, synthetic-data rules, exact question counts/types, cross-unit targets, design-review prompts and safety constraints are source-derived requirements from the supplied prompt and authoritative M16 syllabus. Model answers include engineering judgment where the source requires a defended decision; where a choice is context-dependent, the answer states the assumptions rather than presenting one vendor or architecture as universally correct.

## Final audit and sign-off

### Pass A — Source fidelity

| Check | Result | Notes |
|---|---|---|
| Current generation prompt inspected in full | PASS | `Pasted markdown(20261103-185538).md` was read from the current upload. |
| Authoritative M16 syllabus-generation prompt inspected | PASS | The 417-line M16 syllabus prompt was inspected, including Unit 10, global constraints, source hierarchy, M01–M15 handoffs and capstone relationship. |
| Roadmap inspected for Stage 2E and complete M16 tree | PASS | The Stage 2E section and M16 tree were checked; target filename and sibling sequence match. |
| Generated M16 Units 1–9 inspected | PASS | All nine actual generated lesson files were available and inspected for objectives, vocabulary, labs, incidents, evidence and boundaries. |
| M16 capstone specification inspected | PASS | Used as an integration context only; it does not replace Unit 1–9 coverage. |
| M16 README and Projects/README actual contents | NOT INSPECTED | The roadmap lists these files, but their contents were not located among the accessible source files. No claims are made about their unseen contents. |
| Existing M16 question bank | NOT FOUND | A prior file named `practice-questions(20261031-172611).md` was inspected and is a Module 1.1 question set, not an M16 bank; it was not reused. |

### Pass B — Coverage completeness

| Check | Result | Notes |
|---|---|---|
| Units 1–9 in correct order | PASS | Nine unit sections present. |
| Exact 14-question distribution per unit | PASS | 3 conceptual + 3 MCQ + 3 interpretation + 3 review + 1 incident + 1 design. |
| At least 35 cross-unit scenarios | PASS | 40 unique `XU-Q` IDs. |
| At least 19 synthesis questions | PASS | 19 unique `SYN-Q` IDs. |
| At least 180 unique numbered questions | PASS | 185 unique IDs, excluding 16 additional design-review prompts. |
| All 16 design-review prompts | PASS | `DR-01` through `DR-16`. |
| Complete topic-to-ID matrix | PASS | 56 unit/topic rows plus required cross-unit integration checklist. |
| Capstone used only as integration context | PASS | The capstone is not treated as a tenth teaching unit. |

### Pass C — Answer correctness and pedagogy

| Check | Result | Notes |
|---|---|---|
| Every question has answer, reasoning, common mistakes and scoring | PASS | Included per question. |
| Every MCQ has exactly four options and distractor analysis | PASS | Three distractors explained per MCQ. |
| Every artifact review requires at least three defects and fixes | PASS | Three reviews per unit; synthetic artifacts included. |
| Incident sequence includes safe first action and evidence | PASS | Incident answers cover containment, localization, mitigation, communication and prevention. |
| Design reviews include trade-offs, rubric, failure patterns and L4 follow-up | PASS | Sixteen prompts. |
| Numeric/metric questions show calculations and denominator | PASS | Synthetic/local values labelled and interpreted. |
| Ambiguity and assumptions | PASS WITH LIMITATIONS | Context-dependent decisions state assumptions; version-sensitive syntax is not used as an answer dependency. |

### Pass D — Technical authenticity and safety

| Check | Result | Notes |
|---|---|---|
| Fabricated tool versions, flags, fields or project statuses | PASS | None asserted as verified. |
| Version-sensitive claims | OPEN | Listed in the verification register; no live documentation was accessed. |
| Synthetic data and local measurements labelled | PASS | Synthetic and n=1 boundaries are explicit. |
| Individual developer ranking prohibited | PASS | Multiple questions test the privacy rule. |
| Real credentials, production access or unauthorized tests required | PASS | None required; security scenarios are defensive and synthetic. |
| Tenant isolation overclaim avoided | PASS | The bank distinguishes configuration tests from hard multi-tenancy proof. |
| Laptop/stack-profile feasibility | PASS | Plat-Core is the guaranteed path; heavy optional components are sequenced. |

### Pass E — File and delivery integrity

| Check | Result | Notes |
|---|---|---|
| One standalone Markdown artifact | PASS | Only `practice-questions.md` was created in the isolated output directory. |
| Other repository files modified | NO | No repository source, lesson, README, capstone or roadmap was modified. |
| Executable platform labs run | NOT RUN | This deliverable is a question bank. No cluster, portal, Crossplane, policy engine or platform lab was executed. |
| Structural validation | RUN | Question IDs, per-unit distributions, cross-unit/synthesis/design-review counts, MCQ option counts, artifact-review counts and Markdown fence balance were checked. |
| Human review | REQUIRED | AI editorial audit does not replace a human technical review or live version verification. |

### Sign-off

```text
Content status: DRAFT-AUDITED
Audit date: 2026-11-04
Source inspection: Current practice-question prompt; authoritative M16 syllabus prompt; Roadmap(10).md Stage 2E/M16 tree; generated M16 Units 1–9; M16 capstone specification; prior M1.1 question-bank file (excluded as unrelated).
Question count: 192 unique numbered questions (126 unit + 40 cross-unit + 26 synthesis); 16 additional design-review prompts.
Unit coverage: All nine units have the prescribed 14-question distribution; 56 topic rows plus integration checklist mapped to IDs.
Cross-unit scenarios: 40
Design-review prompts: 16
Open [VERIFY] items: 23 grouped verification areas
Executable validation: NOT RUN (structural/editorial validation only)
Human review required: YES
Fidelity caveat: Synthetic lab data and local laptop measurements do not establish real developer adoption, productivity, satisfaction or platform value.
```

AI self-audit does not replace a human running the relevant templates, APIs, portal and labs with installed versions. All user research, adoption, survey and productivity examples in this bank are synthetic or local n=1; they prove nothing about real developers. No industry statistics are asserted. Tool APIs, composition models, project status and framework attributions must be re-verified against current primary sources. Isolation tests verify only the controls and paths actually tested; they do not prove resilience against all adversarial tenants. A platform's value must be demonstrated through measured outcomes with real developers over time.


---

## Complete topic-to-question coverage matrix

The matrix maps the source syllabus topic clusters to concrete IDs. `COVERED` means the question bank contains at least one directly scorable item for the stated topic; it does not mean a learner has passed the topic or executed its lab. Unit links point to the actual generated lesson files inspected for this bank.

| Source unit/topic | Level(s) | Question IDs | Question type(s) | Cross-unit links | Coverage status | Notes / verification |
|---|---|---|---|---|---|---|
| U1 — definitions: platform engineering, IDP, portal, DevOps/SRE, platform team and developer teams | L1 | U01-Q01; U01-Q02 | Short answer | XU-Q02; DR-01; DR-15 | COVERED | Distinguish discipline, product/system and interface; framework attributions remain [VERIFY]. |
| U1 — platform as product, personas, jobs, journey and manual baseline | L1–L2 | U01-Q02; U01-Q03; U01-Q09 | Short answer; artifact interpretation | XU-Q01; XU-Q02; DR-01 | COVERED | Local measurements are n=1; synthetic personas are not real users. |
| U1 — synthetic interviews/tickets, friction analysis, opportunity ranking and PRD | L2 | U01-Q05; U01-Q07; U01-Q10 | MCQ; artifact interpretation; artifact review | XU-Q01; XU-Q19; DR-01 | COVERED | Frequency×severity is an explicit exercise assumption. |
| U1 — TVP/MVP, build/adopt/buy, team topology, support/intake and mandates | L2–L4 | U01-Q04; U01-Q12; U01-Q14 | MCQ; artifact review; design | XU-Q01; XU-Q21; DR-01; DR-15 | COVERED | Interaction-mode terminology is awareness-level and source-verified separately. |
| U1 — capability map, multiple interfaces, abstraction, escape hatches and debuggability | L3 | U01-Q08; U01-Q14 | Artifact interpretation; design | XU-Q03; XU-Q13; XU-Q16; DR-01 | COVERED | Platform API/portal implementation remains owned by later units. |
| U1 — secure/reliable/observable/cost-aware defaults, blast radius and platform economics | L3 | U01-Q11; U01-Q14 | Artifact review; design | XU-Q04; XU-Q06; XU-Q11; DR-01; DR-16 | COVERED | ROI inputs remain hypothetical; no external ROI figures. |
| U1 — maturity, trust, ethics, AI-assisted tooling risks and organizational anti-patterns | L4 | U01-Q13; SYN-Q01 | Incident; synthesis | XU-Q39; DR-01; DR-15; DR-16 | COVERED | AI-assisted tooling is awareness; no vendor endorsement or real productivity claim. |
| U2 — golden path/paved road versus template/golden cage | L1 | U02-Q01 | Short answer | XU-Q13; DR-02 | COVERED | Golden path is supported journey, not a mandate. |
| U2 — shared service skeleton and M01–M15 default integration | L1–L2 | U02-Q03; U02-Q14 | Short answer; design | XU-Q01; XU-Q15; XU-Q31; DR-02 | COVERED | Earlier modules are integrated, not re-taught. |
| U2 — API, batch, streaming, model-serving and notebook archetypes | L2 | U02-Q03; U02-Q06; U02-Q14 | Short answer; MCQ; design | XU-Q13; XU-Q24; DR-02 | COVERED | Archetype-specific requirements are distinguished. |
| U2 — default→source→reason→test register and conformance definition | L2 | U02-Q04; U02-Q07; U02-Q08 | MCQ; artifact interpretation | XU-Q32; SYN-Q17; DR-02 | COVERED | Conformance report does not prove runtime production readiness. |
| U2 — CI/render/policy checks, negative tests and actionable diagnostics | L2–L3 | U02-Q05; U02-Q09; U02-Q12 | MCQ; artifact interpretation; artifact review | XU-Q06; DR-02; DR-16 | COVERED | Exact external policy engine syntax is [VERIFY]. |
| U2 — default/option/escape support policy and customization boundaries | L2–L3 | U02-Q02; U02-Q11 | Short answer; artifact review | XU-Q04; XU-Q13; XU-Q31; DR-02 | COVERED | Mandatory controls remain in force for escape paths. |
| U2 — rollout, template blast radius, conformance and support | L3–L4 | U02-Q10; U02-Q13; U02-Q14 | Artifact review; incident; design | XU-Q06; XU-Q21; XU-Q31; DR-02 | COVERED | Canary cohorts should represent affected archetypes. |
| U3 — developer request journey and self-service versus ticket form | L1 | U03-Q01; U03-Q02 | Short answer | XU-Q03; XU-Q15; DR-03 | COVERED | One canonical request object across front doors. |
| U3 — request schema, entitlement registry, policy, cost and approval layers | L2 | U03-Q04; U03-Q07; U03-Q10 | MCQ; artifact interpretation; artifact review | XU-Q07; XU-Q14; SYN-Q03; DR-03 | COVERED | Schema validity is distinct from authorization. |
| U3 — GitOps provisioning, data capabilities, secret references and status | L2 | U03-Q05; U03-Q08; U03-Q14 | MCQ; artifact interpretation; design | XU-Q08; XU-Q09; XU-Q15; DR-03 | COVERED | No real credentials; status separates accepted, reconciled and usable. |
| U3 — preview TTL, idempotency, retries, safe deprovision and orphan detection | L2–L3 | U03-Q06; U03-Q09; U03-Q11 | MCQ; artifact interpretation; artifact review | XU-Q20; XU-Q35; DR-03 | COVERED | Data retention/hold decisions are explicit policy gates. |
| U3 — front doors, approvals, engine selection, quota/capacity and SLOs | L3–L4 | U03-Q12; U03-Q13; U03-Q14 | Artifact review; incident; design | XU-Q03; XU-Q07; XU-Q28; XU-Q34; DR-03 | COVERED | Plat-Core is mandatory; Plat+Control optional. |
| U4 — portal versus platform versus catalog; Backstage context | L1 | U04-Q01; U04-Q03 | Short answer | XU-Q33; DR-04 | COVERED | Thin portal is guaranteed; Backstage is preflight-gated. |
| U4 — catalog-as-code, entity relationships, owner/system/API/resource metadata | L2 | U04-Q07; U04-Q08 | Artifact interpretation | XU-Q16; XU-Q17; XU-Q29; DR-04 | COVERED | Exact entity fields and annotations require selected-version verification. |
| U4 — catalog linting, owner/link validation, drift, orphan and injection | L2–L3 | U04-Q07; U04-Q10; U04-Q13 | Artifact interpretation; artifact review; incident | XU-Q17; XU-Q29; XU-Q39; DR-04; DR-16 | COVERED | Catalog is data consumed by automation; provenance/freshness matter. |
| U4 — thin portal generator, Backstage preflight, local auth and fallback | L2–L3 | U04-Q03; U04-Q11; U04-Q14 | Short answer; artifact review; design | XU-Q33; DR-04 | COVERED | Backstage must run alone in Plat+Portal. |
| U4 — scorecards, showback, catalog-driven automation and privacy | L2–L4 | U04-Q08; U04-Q12 | Artifact interpretation; artifact review | XU-Q05; XU-Q18; SYN-Q01; DR-04 | COVERED | Evidence-backed scorecards; no individual developer rankings. |
| U4 — portal reliability, authn/authz, plugin governance, SLO and incident response | L3–L4 | U04-Q02; U04-Q11; U04-Q13 | Short answer; artifact review; incident | XU-Q17; XU-Q33; DR-04; DR-16 | COVERED | Authentication is not authorization; plugin/action details [VERIFY]. |
| U5 — template versus path, generation versus update, tool trade-offs | L1 | U05-Q01; U05-Q06 | Short answer; MCQ | XU-Q06; XU-Q10; DR-05 | COVERED | Copier primary in the course; Cookiecutter semantics [VERIFY]. |
| U5 — parameter contract, validation, derived values and safe execution | L2 | U05-Q02; U05-Q07; U05-Q10 | Short answer; artifact interpretation; artifact review | XU-Q39; SYN-Q05; DR-05; DR-16 | COVERED | Validate before tasks; do not interpolate untrusted input into shell. |
| U5 — template anatomy, archetypes, generated files and ownership boundaries | L2 | U05-Q03; U05-Q12; U05-Q14 | Short answer; artifact review; design | XU-Q15; XU-Q30; DR-05 | COVERED | Generated files are starting points, not production evidence. |
| U5 — template test matrix, deterministic output, mutation and conformance | L2–L3 | U05-Q10; U05-Q12 | Artifact review | XU-Q06; SYN-Q17; DR-05 | COVERED | Test generated outputs and planted unsafe variants. |
| U5 — update campaign across five or more repos, conflicts and bot safety | L3–L4 | U05-Q08; U05-Q09; U05-Q11; U05-Q13 | Artifact interpretation; artifact review; incident | XU-Q06; XU-Q17; XU-Q21; DR-05 | COVERED | Per-repository result and owner review; dry-run/rate limits. |
| U5 — template versioning, support, deprecation and update metrics | L3–L4 | U05-Q14 | Design | XU-Q10; XU-Q17; XU-Q38; DR-05; DR-13 | COVERED | Update lag is not an individual performance metric. |
| U6 — platform API contract, abstraction and reconciliation versus pipeline | L1–L2 | U06-Q01; U06-Q02; U06-Q14 | Short answer; design | XU-Q03; XU-Q08; XU-Q30; DR-06; DR-07 | COVERED | M07 Unit 12 Crossplane fundamentals are prerequisite, not repeated. |
| U6 — DataEnvironment/PostgresDatabase/ModelEndpoint/ObjectBucket contracts | L2 | U06-Q07; U06-Q08; U06-Q14 | Artifact interpretation; design | XU-Q10; XU-Q11; DR-06 | COVERED | ObjectBucket optional where feasible; exact schemas are version-specific. |
| U6 — schema validation, CEL, defaults, immutability and secret boundaries | L2–L3 | U06-Q05; U06-Q07; U06-Q10; U06-Q12 | MCQ; artifact interpretation; artifact review | XU-Q11; XU-Q18; SYN-Q13; DR-06 | COVERED | Exact CRD/CEL syntax [VERIFY]. |
| U6 — composition functions, status conditions, readiness and testing | L2–L3 | U06-Q03; U06-Q08; U06-Q11 | Short answer; artifact interpretation; artifact review | XU-Q08; XU-Q10; XU-Q35; DR-06 | COVERED | Render, golden, integration, RBAC and admission tests prove different things. |
| U6 — controller RBAC, deletion semantics, Manual update, rings and fan-out | L3–L4 | U06-Q04; U06-Q09; U06-Q12; U06-Q13 | MCQ; artifact interpretation; artifact review; incident | XU-Q10; XU-Q11; XU-Q35; DR-06; DR-07 | COVERED | Destructive behavior and rollback semantics must be verified. |
| U6 — GitOps, API versioning/migration, DR/adoption and alternatives | L3–L4 | U06-Q14 | Design | XU-Q10; XU-Q18; XU-Q30; DR-07 | COVERED | Crossplane vs Terraform-via-PR vs Helm-as-API trade-off. |
| U7 — tenant identity, trust tiers, soft/hard tenancy and threat model | L1–L2 | U07-Q01; U07-Q02; U07-Q14 | Short answer; design | XU-Q11; XU-Q12; XU-Q20; DR-08 | COVERED | Team, tenant key, namespace, cost center and owner remain distinct. |
| U7 — layered identity/RBAC/network/compute/storage/secrets/registry/ingress/obs/cost | L2–L3 | U07-Q04; U07-Q05; U07-Q10 | MCQ; artifact interpretation; artifact review | XU-Q04; XU-Q11; XU-Q12; XU-Q28; DR-08 | COVERED | Namespace is not a hard security boundary. |
| U7 — ≥25 isolation tests per tenant pair, positive/negative and evidence | L2–L3 | U07-Q03; U07-Q08; U07-Q12 | Short answer; artifact interpretation; artifact review | XU-Q11; XU-Q12; XU-Q21; DR-08 | COVERED | Tests are benign and confined to own disposable lab. |
| U7 — onboarding/offboarding, retention, access revocation and orphans | L2–L3 | U07-Q06; U07-Q10; U07-Q11 | MCQ; artifact review | XU-Q20; XU-Q21; DR-09 | COVERED | Hold/export is a policy decision, not legal advice. |
| U7 — delegated admin, label tamper, hostname ownership, noisy neighbor, canary and compromise | L3–L4 | U07-Q09; U07-Q13; U07-Q14 | Artifact interpretation; incident; design | XU-Q12; XU-Q28; XU-Q35; DR-08; DR-09 | COVERED | Canary tenant and continuous assurance are explicit. |
| U8 — platform SLIs/SLOs, usable journey, error budgets and burn alerts | L1–L3 | U08-Q01; U08-Q04; U08-Q07; U08-Q13 | Short answer; MCQ; artifact interpretation; incident | XU-Q08; XU-Q34; DR-10 | COVERED | M10 SLO/error-budget foundations reused. |
| U8 — adoption KPI definitions, denominator, funnel, version spread and ticket categories | L2 | U08-Q02; U08-Q08; U08-Q12 | Short answer; artifact interpretation; artifact review | XU-Q05; XU-Q14; XU-Q17; SYN-Q07; DR-11 | COVERED | Metric definitions and exclusions are versioned. |
| U8 — six-month synthetic data, missing/duplicate events and DORA cohorts/confounders | L2–L3 | U08-Q03; U08-Q08; U08-Q12 | Short answer; artifact interpretation; artifact review | XU-Q05; XU-Q14; XU-Q22; DR-11 | COVERED | Synthetic ground truth is for method practice, not population claims. |
| U8 — surveys, response bias, small-n, interviews, friction logs and usability | L2–L3 | U08-Q09; U08-Q14 | Artifact interpretation; design | XU-Q22; XU-Q37; DR-12 | COVERED | Real-user research only when actual participants are available. |
| U8 — privacy, no individual fields, Goodhart, anti-gaming, ROI uncertainty | L3–L4 | U08-Q05; U08-Q10; U08-Q12 | MCQ; artifact review | XU-Q12; XU-Q18; SYN-Q01; SYN-Q11; DR-11; DR-12 | COVERED | No individual rankings; hypothetical HCU/cost assumptions only. |
| U8 — quarterly review, roadmap prioritization, cost and data/ML DX | L3–L4 | U08-Q11; U08-Q14 | Artifact review; design | XU-Q19; XU-Q27; DR-10; DR-12 | COVERED | Data/ML journey includes notebook, model and GPU/runtime context. |
| U9 — governed artifact inventory, owners, backup owners, support and EOL | L1–L2 | U09-Q01; U09-Q07; U09-Q08 | Short answer; artifact interpretation | XU-Q17; XU-Q38; DR-13 | COVERED | Freshness and direct/indirect consumers are required. |
| U9 — SemVer limits and artifact-specific compatibility semantics | L1–L2 | U09-Q01; U09-Q04; U09-Q09; U09-Q11 | Short answer; MCQ; artifact interpretation; artifact review | XU-Q10; XU-Q18; XU-Q30; DR-13 | COVERED | Version label is not compatibility proof. |
| U9 — compatibility matrix, version skew, pinning and support levels | L2–L3 | U09-Q07; U09-Q09; U09-Q11 | Artifact interpretation; artifact review | XU-Q10; XU-Q17; XU-Q30; DR-13 | COVERED | Unknown matrix state is not supported. |
| U9 — RFC/ADR, decision rights, consumer input, release manifest, rings and rollback | L2–L3 | U09-Q03; U09-Q05; U09-Q12; U09-Q14 | Short answer; MCQ; artifact review; design | XU-Q06; XU-Q11; XU-Q18; DR-14 | COVERED | Governance weight is proportional to blast radius. |
| U9 — policy impact audit→warn→enforce, deprecation, migration, brownout and removal | L2–L4 | U09-Q05; U09-Q06; U09-Q08; U09-Q10; U09-Q13 | MCQ; artifact interpretation; artifact review; incident | XU-Q10; XU-Q18; XU-Q20; XU-Q38; DR-13 | COVERED | Brownout is announced, bounded and rollback-capable. |
| U9 — exceptions, expiry, supported versions, documentation freshness and dependency exit | L2–L4 | U09-Q02; U09-Q06; U09-Q10; U09-Q12 | Short answer; MCQ; artifact review | XU-Q17; XU-Q38; DR-13 | COVERED | Exception registry requires scope, owner, approver, controls, evidence and expiry. |
| U9 — API lifecycle alpha/beta/GA/deprecated/removed and data/ML governance | L3–L4 | U09-Q09; U09-Q11; U09-Q14 | Artifact interpretation; artifact review; design | XU-Q18; XU-Q20; XU-Q30; DR-06; DR-13 | COVERED | Model/dataset/runtime/GPU/CUDA claims remain version-verified. |
| U9 — governance metrics, risk register, portability, platform sunset and incidents | L3–L4 | U09-Q03; U09-Q13; U09-Q14 | Short answer; incident; design | XU-Q19; XU-Q20; XU-Q37; DR-13; DR-14 | COVERED | Support windows and thresholds remain [ILLUSTRATIVE] unless source-backed. |

### Required cross-unit coverage checks

| Required integration theme | Question IDs | Status |
|---|---|---|
| Vision → TVP → golden path → generated repo → request → API → isolation → catalog → measurement → governance | `XU-Q02`, `XU-Q01`, `XU-Q03`, `XU-Q10`, `XU-Q11`, `XU-Q16`, `XU-Q18` | COVERED |
| Build/adopt/buy and platform-team boundaries | `U01-Q04`, `U01-Q12`, `U01-Q14`, `XU-Q01`, `DR-01`, `DR-15` | COVERED |
| Golden path versus golden cage and safe escape hatches | `U02-Q01`, `U02-Q02`, `U02-Q11`, `XU-Q04`, `XU-Q13`, `DR-02` | COVERED |
| Template security fix across five or more repos, including conflicts and staged rollout | `U05-Q08`, `U05-Q09`, `U05-Q11`, `U05-Q13`, `XU-Q06`, `DR-05` | COVERED |
| Rejection localized at schema, entitlement, CI, admission, quota/capacity or controller | `U03-Q04`, `U03-Q07`, `U03-Q10`, `XU-Q07`, `XU-Q08`, `SYN-Q03` | COVERED |
| Stale catalog ownership during incident and alert routing | `U04-Q13`, `XU-Q09`, `XU-Q17`, `XU-Q29`, `DR-04` | COVERED |
| Composition change with deletion risk, fan-out and safe rollout | `U06-Q04`, `U06-Q09`, `U06-Q12`, `U06-Q13`, `XU-Q10`, `XU-Q11`, `DR-06` | COVERED |
| Tenant-isolation alert during rollout, containment and recovery | `U07-Q13`, `XU-Q11`, `XU-Q12`, `XU-Q35`, `DR-08`, `DR-09` | COVERED |
| Adoption data distorted by selection bias or changed definitions | `U08-Q03`, `U08-Q08`, `U08-Q12`, `XU-Q05`, `XU-Q14`, `SYN-Q07`, `DR-11` | COVERED |
| Deprecation with fresh telemetry, migration and expiring exception | `U09-Q06`, `U09-Q08`, `U09-Q10`, `U09-Q13`, `XU-Q20`, `XU-Q38`, `DR-13` | COVERED |
| Platform SLO breach and error-budget change decision | `U08-Q06`, `U08-Q13`, `XU-Q34`, `XU-Q40`, `DR-10` | COVERED |
| Individual telemetry / unsupported ROI claim | `U01-Q11`, `U04-Q12`, `U08-Q05`, `U08-Q10`, `SYN-Q01`, `SYN-Q11`, `DR-11`, `DR-12` | COVERED |
| Privileged portal/bot/provider identity, template supply-chain or policy bypass | `U04-Q11`, `U05-Q10`, `U05-Q11`, `U06-Q10`, `XU-Q39`, `DR-05`, `DR-16` | COVERED |
| Cost contention, noisy neighbors, entitlements and self-service | `U03-Q10`, `U07-Q14`, `XU-Q28`, `SYN-Q14`, `DR-03`, `DR-08` | COVERED |
| Backstage infeasibility on an 8 GB laptop and thin-portal alternative | `U04-Q03`, `U04-Q14`, `XU-Q33`, `DR-04` | COVERED |
| Distinguish platform component failure, catalog data failure, user config, policy denial and process/governance failure | `U03-Q13`, `U04-Q13`, `U06-Q13`, `U08-Q13`, `U09-Q13`, `XU-Q07`, `XU-Q17`, `XU-Q35` | COVERED |


### Source-lesson incident-case traceability register

The generated M16 lessons contain eight synthetic incident cases per unit. This register maps all 72 source lesson cases to one or more question IDs. A mapped question assesses the relevant failure mode or decision; it does not claim that the incident occurred in a real organization.

| Source unit | Source lesson incident case | Question IDs | Coverage note |
|---:|---|---|---|
| U01 | Custom framework has almost no users beyond its creators | `U01-Q13` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U01 | Ticket queue renamed 'platform requests'; lead time remains high | `U01-Q12`; `XU-Q03` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U01 | Mandatory golden path has no escape hatch; teams fork it | `U02-Q11`; `XU-Q13` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U01 | Platform change breaks many pipelines on Friday | `XU-Q06`; `DR-14` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U01 | Template upgrades become impossible; repositories drift | `U05-Q08`; `XU-Q10` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U01 | Leadership tracks individual deploy counts; trust collapses | `SYN-Q01`; `U08-Q10` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U01 | Stale catalog pages on-call to the wrong team | `U04-Q13`; `XU-Q09` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U01 | Platform has no SLO; users stop trusting it after outages | `U08-Q13`; `XU-Q34` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U02 | Template default disables TLS verification and spreads to services | `SYN-Q20`; `U02-Q10` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U02 | Template upgrade conflicts with generated repositories' local changes | `U05-Q08`; `U05-Q13`; `XU-Q06` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U02 | Dashboard counts any repo containing template files as 'on path' | `U02-Q08`; `U08-Q12` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U02 | Data scientists bypass path and use notebooks with embedded credentials | `SYN-Q21`; `DR-02` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U02 | Slow CI checks drive teams to use an admin bypass | `SYN-Q22`; `U02-Q12` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U02 | Policy errors are cryptic and support tickets increase | `U02-Q09`; `U02-Q12` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U02 | Template tests check generation only, not deployability | `U02-Q12`; `U02-Q14` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U02 | Template requires a database for every service, including batch jobs | `U02-Q03`; `U02-Q14` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U03 | Arbitrary YAML injection attempts privileged pod settings | `U03-Q10`; `XU-Q07`; `DR-03` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U03 | Preview environments never expire and consume capacity | `U03-Q11`; `U03-Q14`; `DR-03` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U03 | Database capability is advertised without backup policy | `SYN-Q23`; `U03-Q14` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U03 | Approval queue becomes the ticket queue for routine requests | `U03-Q14`; `XU-Q03` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U03 | Quota exhaustion is silent and provisioning stalls | `U03-Q13`; `XU-Q35` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U03 | Template change deletes existing resources without migration review | `U03-Q11`; `U06-Q13`; `XU-Q10` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U03 | Shared development database is wiped by another team's test/reset | `SYN-Q24`; `U07-Q11` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U03 | Stale entitlement leaves a departed team's resources active | `U07-Q11`; `XU-Q20` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U04 | Catalog becomes stale after reorganization and pages wrong team | `U04-Q13`; `XU-Q09` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U04 | Broad SCM token leaks through plugin misconfiguration | `U04-Q11`; `XU-Q39`; `DR-16` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U04 | Portal upgrade breaks custom plugins and freezes portal | `U04-Q11`; `XU-Q17`; `DR-04` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U04 | No schema owner permits incompatible catalog annotations | `U04-Q10`; `XU-Q17` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U04 | Portal outage blocks runbook access | `XU-Q33`; `U04-Q14` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U04 | Scorecards are gamed with empty runbooks | `U04-Q12`; `XU-Q18` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U04 | Malicious entity claims critical-service ownership | `U04-Q10`; `XU-Q39`; `DR-16` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U04 | Retired service remains marked production | `U04-Q10`; `XU-Q17`; `U09-Q01` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U05 | Unpinned curl-to-shell template hook executes mutable remote script | `U05-Q10`; `XU-Q39`; `DR-16` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U05 | Template update overwrites local repository changes | `U05-Q13`; `XU-Q06` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U05 | Backstage Scaffolder action has organization-admin token risk | `U05-Q11`; `DR-16` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U05 | Workflow rename creates duplicate CI pipelines | `U05-Q12`; `XU-Q10` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U05 | New required template parameter stalls unattended automation | `U05-Q08`; `XU-Q10` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U05 | Update bot floods CI with pull requests | `U05-Q11`; `XU-Q06` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U05 | Placeholder password ships in generated deployment | `U05-Q10`; `XU-Q39` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U05 | Nunjucks/Jinja2 divergence produces inconsistent output | `U05-Q12`; `DR-05` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U06 | Composition update deletes or recreates databases | `U06-Q13`; `XU-Q10`; `DR-06` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U06 | Arbitrary manifest field creates privileged Pod | `U06-Q10`; `XU-Q39` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U06 | Provider/Crossplane service account is over-privileged | `U06-Q11`; `DR-16` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U06 | Argo CD and Crossplane fight over child resources | `U06-Q12`; `XU-Q30` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U06 | Breaking XRD version invalidates old requests | `U06-Q13`; `U09-Q13`; `XU-Q18` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U06 | Composition function crashes on rare input | `U06-Q13`; `XU-Q35` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U06 | Secret appears in status or function logs | `U06-Q12`; `XU-Q39` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U06 | Provider upgrade breaks fleet schema | `XU-Q10`; `XU-Q18`; `DR-07` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U07 | CI service account can view all tenant Secrets | `U07-Q10`; `XU-Q39`; `DR-16` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U07 | Namespace label tampering bypasses policy | `U07-Q10`; `SYN-Q13` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U07 | Shared ingress accepts another tenant's hostname | `U07-Q10`; `DR-08` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U07 | Noisy tenant creates excessive ConfigMaps and raises API latency | `U07-Q14`; `XU-Q28` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U07 | Offboarding leaves external resources and identities | `U07-Q11`; `XU-Q20`; `DR-09` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U07 | Isolation tests run only at onboarding and miss later drift | `U07-Q13`; `XU-Q12` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U07 | Shared GPU time-slicing crosses trust boundaries | `U07-Q14`; `DR-08` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U07 | Metrics proxy trusts client-supplied tenant header | `U07-Q10`; `U08-Q10`; `DR-16` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U08 | Individual deploy ranking causes gaming and trust erosion | `U08-Q10`; `SYN-Q01` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U08 | Mandated adoption worsens satisfaction and incidents | `U01-Q13`; `XU-Q13` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U08 | Small survey sample is generalized to the organization | `U08-Q09`; `DR-12` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U08 | API SLO is green while environment is unusable | `U08-Q13`; `U03-Q05`; `DR-10` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U08 | First-deploy definition silently changes | `U08-Q12`; `SYN-Q07` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U08 | Ticket count falls only because support channel moved | `U08-Q12`; `XU-Q17` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U08 | Portal analytics captures usernames | `U08-Q10`; `SYN-Q01` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U08 | ROI model is presented as measured fact | `U01-Q11`; `U08-Q11`; `SYN-Q11` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U09 | Breaking XRD change is shipped as a minor version | `U09-Q11`; `U09-Q13`; `XU-Q18` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U09 | Policy bundle enters enforce without impact report | `U09-Q05`; `U09-Q13`; `XU-Q11` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U09 | Deprecated base image is removed without usage telemetry | `U09-Q08`; `U09-Q13`; `XU-Q20` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U09 | Exceptions registry accumulates expired unreviewed entries | `U09-Q10`; `U09-Q06`; `SYN-Q19` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U09 | Forced migration without tooling creates shadow tooling | `U09-Q13`; `U01-Q13`; `XU-Q06` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U09 | Unmaintained OSS portal plugin has an unpatched vulnerability | `SYN-Q26`; `DR-16` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U09 | RFC process takes weeks for trivial changes and teams bypass it | `SYN-Q25`; `U09-Q03`; `DR-14` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |
| U09 | Multiple template versions prevent a security fix propagating | `U09-Q08`; `U05-Q08`; `XU-Q06` | Scenario, artifact, incident or design assessment; all source cases are synthetic. |

