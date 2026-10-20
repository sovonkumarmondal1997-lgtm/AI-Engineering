# `practice-questions.md` — Module 2D.2 Assessment
## Requirements, Constraints and Architecture Decisions

**Assessment purpose:** Test whether you can discover stakeholder needs, write testable requirements, estimate data workloads, define service targets, classify constraints and uncertainty, compare architecture alternatives, and document decisions so another architect can audit the reasoning.

**Authoritative scope:** This assessment follows `roadmap-Requirements-Constraints-and-Architecture-Decisions.md` and the Stage 2D tree in `Roadmap_ptree.md`. It covers all seven roadmap topics in their prescribed learning order. The roadmap states that the seven lesson files, this assessment file, the module/project READMEs, and `Projects/02-requirements-and-architecture-decision-pack.md` were empty in the referenced repository state. Therefore, the assessment is derived from the written topic roadmap and its project/completion-gate requirements; it does not assume unseen lesson content or reproduce unseen question banks. The roadmap states that the repository does not mandate an ADR template; the Topic 7 structure is a practical recommendation, not repository policy.

**Case convention:** Northbridge Bank is fictional. All numerical values, targets, stakeholder statements, IDs, roles, and scenario extensions explicitly described as illustrative are exercise inputs—not facts about any real organisation or recommended targets. In an actual project, distinguish observed facts, approved requirements, estimates, assumptions, and unknowns.

---

# Section A — Assessment Instructions

## A1. How to attempt the assessment

The assessment has four levels: beginner, intermediate, advanced, and industry application. Work in order unless you are taking a timed diagnostic. The questions assess reasoning and artefact quality, not just vocabulary.

| Attempt | Notes/tools | Purpose |
|---|---|---|
| Closed-book diagnostic | No notes, web search, or AI assistance. Basic calculator permitted only where stated. | Measure recall and unaided reasoning. |
| Applied assessment | Notes and calculator permitted; cite the source/artefact used and label assumptions. | Test practical application. |
| Industry case | Use the supplied case facts, create registers/tables, and show evidence links or provisional IDs. | Test reviewable work products. |
| Correction pass | Consult the roadmap and answer key after completing the attempt. | Identify the reasoning error, correct it, then re-attempt later. |

Do not look at Section H until you have completed the relevant questions. For quantitative questions, show **formula, substituted values, units, result, assumptions, and interpretation**. A correct final number with no working may receive partial credit only.

## A2. Response rules

1. **Use evidence labels:** observed/supplied fact, approved requirement, estimate, assumption, unknown, or judgement.
2. **Do not invent missing inputs.** If a question intentionally omits an input, identify it, explain why it matters, and say how you would obtain it.
3. **Use consistent units.** Unless a question says otherwise, use decimal storage units: 1 GB = \(10^9\) bytes, 1 TB = \(10^{12}\) bytes. Use 1 KiB = 1,024 bytes and 1 GiB = \(2^{30}\) bytes only when explicitly indicated. A byte is 8 bits.
4. **Round transparently.** Carry sufficient precision through calculations and round only the displayed result.
5. **For requirements:** identify source, type, scope, metric/target where relevant, acceptance method, priority, and dependencies.
6. **For risks:** state the probability/impact scale before calculating exposure. Ordinal products prioritise work; they are not precise probabilities of loss.
7. **For decisions:** test hard gates before weighted scoring. Fix criteria and weights before reviewing totals. Scores do not replace evidence or judgement.
8. **For ADRs:** status must reflect actual approval. A proposed recommendation is not an accepted decision.
9. **For open-ended questions:** the answer key gives a model response and evaluation criteria. Equivalent answers earn credit if they satisfy the same underlying requirement and are internally consistent.
10. **Use provisional IDs** such as `BO-01`, `REQ-01`, `TGT-01`, `CON-01`, `ASM-01`, `DEP-01`, `RSK-01`, `DC-01`, and `ADR-01` only as exercise labels. Do not imply that they already exist in the repository.
11. **Marking rule:** unless a question gives a more specific breakdown, award marks proportionally across the distinct deliverables and reasoning criteria in its prompt/model answer; do not double-count the same point. For a two-mark multiple-choice item, award both marks for the correct option. For a two-mark true/false-with-correction item, award one mark for the correct verdict and one for a valid reason/correction. Equivalent technically sound answers are acceptable.

## A3. Suggested time and scoring

- Sections B–D: 90–120 minutes.
- Section E: 60–90 minutes.
- Section F: 45–60 minutes.
- Section G: 2–4 hours, preferably as a take-home artefact exercise.
- Total scored questions: **368 marks**. Section G is a capstone scored within the 368 marks; Section H supplies answers for all scored items.
- The scoring bands in Section I are diagnostic, not a substitute for the roadmap’s evidence-based completion gate.

If you split the assessment over several days, keep the first attempt closed-book and the correction attempt separate.

---

## A4. Roadmap coverage map

The scored items cover the seven topics in the roadmap’s prescribed order. Supplementary exercises U01–U07 are unscored but required for completion where the written roadmap specifies a concrete practice output not fully evidenced by the scored items.

| Roadmap topic | Scored coverage | Supplementary completion evidence |
|---|---|---|
| 1. Stakeholder discovery and business requirements | B01–B02, B11, B18, C01, C07–C08, C11, D04, E01, G01 | U01: validation agenda and record template |
| 2. Functional and non-functional requirements | B03–B04, B12, B19, C02, C05–C06, C09, D05, E02, G02 | U02: 20-statement classification; U03: 12-requirement register |
| 3. Volume, velocity, variety and growth | B05, B13, B20, C13–C14, D06, E03, F01–F05, F13, G03 | U04: multi-stream, three-year capacity estimate |
| 4. Latency, throughput, freshness and availability | B06, B14, B21, C03, C15–C17, D07, E04, F06–F08, F14, G03 | U05: four-target monthly/annual downtime table |
| 5. Constraints, assumptions, dependencies and risks | B07, B15, B22, C10, C12, D01, D08, D13, E05, G04 | E05/U-style register, dependency map, risk response and triggers |
| 6. Architecture trade-offs and decision criteria | B08, B16, B23, C04, D02, D09–D10, E06, F09–F12, G05 | U06: technical and sponsor recommendation versions |
| 7. Architecture decision records | B09, B17, B24, D03, D11–D12, E07, G06–G07 | U07: three ADRs, log, review finding and proportionality rationale |

The map is a navigation aid, not a claim that one question alone proves mastery. The topic gates and integrated-project evidence remain mandatory.

---

# Section B — Beginner-Level Questions

**Purpose:** Terminology, distinctions, basic classification, and recognition of common mistakes. Unless stated otherwise, answer closed-book first.

## B1. Multiple choice

**B01 — Topic 1: Stakeholder discovery and business requirements | Beginner | 2 marks**  
Which statement is a business outcome rather than a solution request?

A. “Build a lakehouse.”  
B. “Use Kafka for card events.”  
C. “Fraud analysts need to see relevant card activity early enough to intervene before a subsequent attempt.”  
D. “Create a dashboard by the end of the quarter.”

**B02 — Topic 1 | Beginner | 2 marks**  
Which stakeholder group is most commonly omitted when discovery focuses only on the sponsor and business users?

A. Operations/support and control functions  
B. The project logo designer  
C. A vendor salesperson only  
D. No group; sponsor input is sufficient

**B03 — Topic 2: Functional and non-functional requirements | Beginner | 2 marks**  
“Validate each incoming customer record against the approved identity rules” is primarily:

A. A functional requirement  
B. A non-functional requirement  
C. A risk  
D. A preference

**B04 — Topic 2 | Beginner | 2 marks**  
Which requirement is most testable as written?

A. “The service must be fast.”  
B. “The platform must be highly scalable.”  
C. “The report shall be available by 07:00 local time on 99% of business days in a rolling quarter, measured by completion timestamp.”  
D. “Users must be happy.”

**B05 — Topic 3: Volume, velocity, variety and growth | Beginner | 2 marks**  
Using decimal units, 2,000,000 records/day × 500 bytes/record equals:

A. 1 MB/day  
B. 100 MB/day  
C. 1 GB/day  
D. 1 TB/day

**B06 — Topic 4: Latency, throughput, freshness and availability | Beginner | 2 marks**  
Which statement correctly distinguishes throughput from latency?

A. They are synonyms.  
B. Throughput is work processed per unit time; latency is elapsed time for an operation/event to produce an observable result.  
C. Throughput measures data age; latency measures uptime.  
D. Latency can be measured only as an average.

**B07 — Topic 5: Constraints, assumptions, dependencies and risks | Beginner | 2 marks**  
A team believes a source system will expose a change-data feed next quarter, but the source owner has not confirmed it. This is best recorded initially as:

A. A verified fact  
B. An assumption, with a dependency and validation action if the solution relies on it  
C. A completed mitigation  
D. A hard constraint without further investigation

**B08 — Topic 6: Trade-offs and criteria | Beginner | 2 marks**  
An option fails a mandatory data-residency constraint. What should happen before weighted scoring?

A. Give it a high cost score to compensate.  
B. Keep it because its average score is highest.  
C. Mark it ineligible and document the gate failure.  
D. Change the weight until it wins.

**B09 — Topic 7: ADRs | Beginner | 2 marks**  
Which statement best describes an ADR?

A. A complete implementation specification for the whole platform  
B. A durable record of a significant decision, context, alternatives, rationale, consequences, and review conditions  
C. A meeting transcript with no outcome  
D. A list of requirements only

**B10 — Topics 1–7 | Beginner | 2 marks**  
Which is the correct traceability direction?

A. ADR → chosen technology only  
B. Business objective → requirement/acceptance criteria and relevant estimates/constraints/risks → criteria and comparison → ADR  
C. Vendor brochure → ADR → invent requirements  
D. Meeting note → architecture diagram; no links required

## B2. True/false with correction

For each, state **True** or **False** and justify/correct it in one or two sentences.

**B11 — Topic 1 | Beginner | 2 marks**  
If a sponsor says “build a dashboard,” that phrase alone is a complete business requirement.

**B12 — Topic 2 | Beginner | 2 marks**  
A requirement can be considered ready even if no one can describe how it will be tested.

**B13 — Topic 3 | Beginner | 2 marks**  
A record’s size in a database, CSV export, and compressed columnar file can differ.

**B14 — Topic 4 | Beginner | 2 marks**  
A pipeline can have high throughput and still have high latency or stale data.

**B15 — Topic 5 | Beginner | 2 marks**  
A dependency is the same thing as a risk, so one register entry is enough in every case.

**B16 — Topic 6 | Beginner | 2 marks**  
A weighted score is an objective measurement that removes stakeholder judgement.

**B17 — Topic 7 | Beginner | 2 marks**  
When an accepted ADR’s outcome changes, silently editing the old record is the preferred way to preserve a clean history.

## B3. Short answer and classification

**B18 — Topic 1 | Beginner | 3 marks**  
Define **stakeholder**, **request**, **underlying need**, and **business objective**. Give one example showing how a request can differ from a need.

**B19 — Topic 2 | Beginner | 3 marks**  
Explain the difference between functional requirement, non-functional requirement, and constraint. Give one data-platform example of each.

**B20 — Topic 3 | Beginner | 3 marks**  
Define volume, velocity, and variety. Classify a relational customer table, JSON API payload, and scanned loan document.

**B21 — Topic 4 | Beginner | 3 marks**  
Define latency, freshness, throughput, and availability. State why a single “real-time” label is insufficient.

**B22 — Topic 5 | Beginner | 3 marks**  
Classify each item and explain the test used:
1. “Personal data must remain in the approved region under current policy.”
2. “We expect 10% annual growth, based on an unvalidated estimate.”
3. “A source team must deliver an interface before ingestion can begin.”
4. “The source team may miss the interface date, delaying the milestone.”
5. “The team prefers its existing BI tool, but it can be changed.”

**B23 — Topic 6 | Beginner | 3 marks**  
Name five possible decision criteria categories and explain why hard gates must be separated from scored preferences.

**B24 — Topic 7 | Beginner | 3 marks**  
What is the difference between ADR **context** and **rationale**? Why should rejected alternatives be recorded?

---

# Section C — Intermediate-Level Questions

**Purpose:** Apply the roadmap techniques to short cases. State assumptions and provide structured responses.

## C1. Multiple choice and error detection

**C01 — Topic 1 | Intermediate | 2 marks**  
The head of marketing says, “Put all customer data in one place.” What is the best immediate response?

A. Choose a lakehouse.  
B. Ask about the business outcome, consumers, data scope, access boundaries, definition of “customer,” success criteria, and constraints before proposing a solution.  
C. Treat the request as an approved requirement.  
D. Ask engineering to select a database.

**C02 — Topic 2 | Intermediate | 2 marks**  
Which is the strongest acceptance criterion for a customer-data ingestion requirement?

A. “The pipeline should be reliable.”  
B. “Use a managed service.”  
C. “For the agreed test dataset and source conditions, every record failing the approved identity validation rule is quarantined, counted, and traceable to a reason code; the data owner signs off the test results.”  
D. “The team will test it.”

**C03 — Topic 4 | Intermediate | 2 marks**  
An upstream source emits its only extract after the core-banking batch window closes at 02:30. A downstream target requires source events to be visible before they exist in the extract. What is the sound conclusion?

A. Set the target anyway; architecture will solve it.  
B. The target is infeasible under the stated source dependency unless the source interface/window or requirement changes.  
C. Replace p95 with average and claim success.  
D. Increase the storage tier.

**C04 — Topic 6 | Intermediate | 2 marks**  
Two options score 4.10 and 4.12 on a five-point weighted model. What is the best interpretation?

A. The second option is definitively better.  
B. The difference may be noise; inspect evidence, score sensitivity, discriminating criteria, and tie-breaks.  
C. Delete the lower-scoring option from the record.  
D. Change weights after seeing the scores.

## C2. Rewrite and acceptance criteria

**C05 — Topic 2 | Intermediate | 5 marks**  
Rewrite “The customer platform must be secure and fast” as **two separate candidate requirements**: one security/access requirement and one measurable performance requirement. State the missing stakeholder decisions or inputs needed before either becomes approved.

**C06 — Topic 2 | Intermediate | 5 marks**  
Write one functional and one non-functional requirement for the Northbridge customer-consolidation problem. For each include: ID, source stakeholder, rationale/objective, priority, measurable acceptance criterion or verification method, and dependencies. Clearly label any invented target as illustrative and pending approval.

**C07 — Topic 1 | Intermediate | 5 marks**  
Prepare an elicitation plan for at least six stakeholder groups in the Northbridge scenario. Include each group’s concern and one open question. Cover business, operations, and control functions.

**C08 — Topic 1 | Intermediate | 4 marks**  
Marketing wants broad customer-attribute access; Compliance wants data minimisation and restricted access. Frame the conflict by **interests**, identify the decision forum/roles, and list evidence needed before resolving it. Do not resolve it by seniority alone.

## C3. Registers and traceability

**C09 — Topic 2 | Intermediate | 5 marks**  
A draft requirement set contains these statements:
1. “Use Kafka for card transactions.”
2. “The fraud case tool shall display transaction data quickly.”
3. “The pipeline must ingest card transactions.”
4. “All customer records must be accurate.”
5. “The report shall be available by 07:00 on 99% of business days in a rolling quarter, measured by completion timestamp.”
For each, identify the defect or classification and state how to repair it.

**C10 — Topic 5 | Intermediate | 5 marks**  
Create a register of five Northbridge items with ID, class (`CON`, `ASM`, `DEP`, `RSK`, or `UNK`), owner role, validation/response, and linked decision. Include at least one of each class. All additional details must be labelled illustrative.

**C11 — Topic 1 | Intermediate | 4 marks**  
A stakeholder is unavailable until after the design deadline. What do you record, what can proceed, and what must remain conditional? Name at least three artefacts or decisions affected.

**C12 — Topic 5 | Intermediate | 4 marks**  
A vendor says an API will be available “next quarter.” Classify the statement, describe the dependency/risk distinction, and provide a validation plan and fallback.

## C4. Intermediate calculations and service targets

**C13 — Topic 3 | Intermediate | 4 marks**  
A source produces 3,200,000 records/day at an average 750 bytes/record. Using decimal units, calculate daily and 365-day annual raw volume. State two assumptions/limitations.

**C14 — Topic 3 | Intermediate | 4 marks**  
A dataset starts at 12 TB/year and grows at 20% compound annual growth. Calculate the annual volume in Year 3 if Year 1 is 12 TB, and the sum of annual volumes in Years 1–3. Use decimal TB and show your interpretation.

**C15 — Topic 4 | Intermediate | 4 marks**  
Calculate allowed downtime for a 30-day month at 99.9% availability. Then calculate the allowed downtime for a 365-day year at 99.9%, in hours. State whether these are service targets or observed results.

**C16 — Topic 4 | Intermediate | 5 marks**  
An end-to-end freshness target is 30 seconds. Proposed stage budgets are: source handoff 8 s, transport 4 s, processing 9 s, load 5 s, publish 3 s. Calculate the total and decide whether the budget passes. If not, propose one mathematically valid adjustment without claiming that it is operationally achievable.

**C17 — Topic 4 | Intermediate | 4 marks**  
A service processes 2,400,000 events over 8 hours. Calculate the average events/second. If the stated peak factor is 4, calculate the estimated peak rate. Explain why this estimate is not a measured peak.

---

# Section D — Advanced-Level Questions

**Purpose:** Resolve ambiguity, reason about interacting requirements, uncertainty, sensitivity, reversibility, and evidence.

## D1. Advanced multiple choice

**D01 — Topic 5 | Advanced | 3 marks**  
A source-schema stability assumption fails during design. What should happen first?

A. Edit the ADR to remove the old assumption.  
B. Update the source assumption/dependency/risk artefacts with evidence, then trace the impact to estimates, targets, criteria, alternatives, and ADRs.  
C. Ignore it until production.  
D. Replace all requirements with a new platform design.

**D02 — Topic 6 | Advanced | 3 marks**  
The cheapest option misses a formally approved mandatory freshness target. What is the correct treatment?

A. Let low cost compensate in the weighted score.  
B. Remove or redesign the option as ineligible; if the target may change, use an authorised requirement-change process before re-evaluating.  
C. Reduce the freshness weight after scoring.  
D. Keep the option without recording the failure.

**D03 — Topic 7 | Advanced | 3 marks**  
An accepted ADR relies on a vendor commitment that is withdrawn. Which is the best action?

A. Silently rewrite the old ADR.  
B. Update dependency/risk records, reassess feasibility and alternatives, create a successor ADR if the outcome changes, and link/supersede the old record.  
C. Leave the ADR untouched and do nothing.  
D. Delete the ADR from the index.

## D2. Advanced analysis and artefact design

**D04 — Topic 1 | Advanced | 5 marks**  
Northbridge’s Risk and Finance teams report different customer counts and each claims its count is correct. Design a discovery and resolution approach. Include hypotheses to test, stakeholders, evidence, a conflict log entry, and a validation/sign-off method.

**D05 — Topic 2 | Advanced | 5 marks**  
A new regulator-driven requirement arrives late and may conflict with broad analytical access. Give a structured impact-analysis method, including requirement quality checks, privacy/security review, traceability, and decision reopening.

**D06 — Topic 3 | Advanced | 5 marks**  
An estimate of daily events differs by a factor of five between two teams. List at least five causes to investigate, propose an evidence plan, and explain how to record the revised estimate and confidence.

**D07 — Topic 4 | Advanced | 5 marks**  
A dashboard meets its average latency target, but users complain about slowness. Specify what to measure next and why. Include percentiles, workload segmentation, measurement boundary, peak/queueing behaviour, and an action if the target itself is wrong.

**D08 — Topic 5 | Advanced | 5 marks**  
Rank the following illustrative assumptions for validation and justify the ranking: (a) source event interface exists, confidence low, failure would block the freshness path; (b) annual storage growth is 8% rather than 10%, confidence medium, low short-term impact; (c) two additional operators will be available, confidence low, failure could undermine 24×7 support. Give a trigger and fallback for each.

**D09 — Topic 6 | Advanced | 6 marks**  
Two feasible options have nearly identical weighted scores. Explain how you would test robustness and decide. Include criteria fixed before scoring, evidence quality, correlated criteria, score uncertainty, sensitivity to weights/inputs, tie-breaks, reversibility, and what would change the recommendation.

**D10 — Topic 6 | Advanced | 5 marks**  
The preferred option depends on an unconfirmed vendor commitment. Write the conditions of a conditional recommendation: what may proceed, what is blocked, missing evidence, owner/date, pass/fail criterion, fallback, status, and revisit trigger.

**D11 — Topic 7 | Advanced | 5 marks**  
Critique this ADR excerpt and list at least six material defects:

> **Title:** Use streaming  
> **Status:** Accepted  
> **Context:** Streaming is modern.  
> **Decision:** Use the event platform because it is best practice.  
> **Alternatives:** Batch was rejected because it is old.  
> **Consequences:** Better performance.  
> **References:** None.

**D12 — Topic 7 | Advanced | 5 marks**  
A decision was made verbally, but the meeting notes do not contain the rationale or approval. Explain how to create a truthful ADR without inventing facts. Include status, owner confirmation, evidence recovery, open issues, and review history.

**D13 — Topics 1–7 | Advanced | 6 marks**  
A sponsor asks to deliver a “real-time single customer view” within a fixed regulatory milestone. The existing core extract ends at 02:30; the card platform emits batch files every 15 minutes; customer data must stay in an approved jurisdiction; the source event contract is unconfirmed; budget is capped. Identify at least four requirement/constraint interactions, which must be gates, which are assumptions/dependencies, and which questions must be answered before a final recommendation.

---

# Section E — Industry-Application Case Studies

**Purpose:** Produce reviewable artefacts. Use supplied scenario facts only where provided; mark extensions as assumptions.

## E1. Northbridge stakeholder and business-requirements pack

**E01 — Topic 1 | Industry | 8 marks**  
Using the shared Northbridge scenario, produce:
- A stakeholder register with at least six groups and fields: role, interest, influence/decision rights, elicitation technique, one question.
- A one-page business problem/objective/scope/exclusions summary.
- At least three measurable or observable success criteria, clearly labelled as proposed pending stakeholder validation.
- A conflict/open-questions log with owner role and evidence needed.

**Expected response format:** Markdown tables plus a short narrative. Label any proposed numeric targets illustrative.

## E2. Requirements register and traceability

**E02 — Topic 2 | Industry | 8 marks**  
Create six requirements for customer/account/card-transaction consolidation: at least two functional and two non-functional, with remaining two chosen by you. For every row include ID, type, statement, source, priority, objective, acceptance criterion/verification method, dependencies, status, and architecture significance. Create a traceability chain for at least three rows from business objective to requirement to target/estimate/constraint/risk to decision criterion.

## E3. Capacity and evidence pack

**E03 — Topic 3 | Industry | 8 marks**  
Prepare a volume/growth worksheet for the supplied illustrative workload:
- 2,000,000 card transactions/day, 500 bytes/record.
- 3,000,000 customer profiles; assume for this exercise an average exported profile payload of 2,000 bytes and a full profile snapshot daily.
- Transaction history retained for 7 years.
- Annual transaction volume growth: 12% compound.
- For this exercise only, use 365 days/year and decimal units.
- For storage planning, assume transaction data has two retained copies and 25% overhead on each copy; do not add compression unless you state and quantify a separate assumption.

Calculate raw daily transaction volume, Year 1 annual volume, Year 7 annual transaction volume (Year 1 is base year), sum of annual transaction volumes across Years 1–7, and an illustrative seven-year retained transaction-storage estimate with copies and overhead. Calculate one daily profile snapshot volume. Also compare the cumulative transaction flow and illustrative retained-storage estimate for 7-year versus 10-year retention under the same growth and storage assumptions. State limitations and identify which assumptions should be sampled/validated.

## E4. Service-target specification

**E04 — Topic 4 | Industry | 8 marks**  
Draft targets for five Northbridge consumers: fraud analysts, risk reporting, regulatory submission, marketing segmentation, and executive dashboard. For each specify indicator, target, percentile where relevant, window, scope, measurement method, acceptor, and rationale. At least one target must include a timing budget; all targets must be labelled proposed/illustrative until validated. Explain why the consumers should not automatically share one target.

## E5. Constraint, assumption, dependency and risk pack

**E05 — Topic 5 | Industry | 8 marks**  
Create at least ten register entries across all required categories: fact/supplied evidence, constraint, preference, assumption, dependency, risk, and unknown. Include ID/class, statement, source/evidence, owner, probability/impact or flexibility where relevant, validation/response, trigger, linked requirement/decision. Produce a dependency map in text and identify the critical path. Write an escalation note for one high-exposure risk.

## E6. Decision matrix and sensitivity

**E06 — Topic 6 | Industry | 8 marks**  
For the fraud freshness path compare:
- Option A: retain/minimally improve batch.
- Option B: managed micro-batch.
- Option C: event-driven delivery.

First define at least one mandatory freshness gate and one applicable control gate. Then create a matrix with at least four scored criteria, weights summing to 1, ratings on a stated 1–5 scale, evidence/uncertainty labels, and rationale. Do not declare an option feasible unless the gates pass. Run sensitivity analysis on the two least certain inputs and state what changes the ranking. The scenario provides no measured performance or approved target, so label all ratings as hypothetical or leave feasibility conditional.

## E7. ADR set and review

**E07 — Topic 7 | Industry | 8 marks**  
Draft an ADR for one major decision boundary. Include status/date/owner, context, drivers linked to IDs, at least three credible options, outcome, rationale, rejected alternatives, positive and negative consequences, accepted trade-offs, assumptions, dependencies/open issues, evidence references, and revisit conditions. Then create a decision-log row and complete at least six checks from the ADR review checklist. If evidence is missing, keep the ADR status Proposed and record the conditions for approval; do not invent approval or use “Conditional” as a separate status unless the project explicitly adopts that vocabulary.

---

# Section F — Quantitative and Calculation Exercises

**Purpose:** Demonstrate reproducible calculations with units and interpretation. Use decimal units unless explicitly stated.

**F01 — Topic 3 | Intermediate | 4 marks**  
A source emits 2,000,000 records/day at 500 bytes/record. Calculate daily raw volume in bytes and decimal GB/day.

**F02 — Topic 3 | Intermediate | 4 marks**  
Using F01, calculate the 30-day raw volume and 365-day raw volume in decimal GB and TB.

**F03 — Topic 3 | Intermediate | 5 marks**  
Daily raw volume is 1.0 GB. For this exercise, assume three layers:
- raw: 1.0 GB/day, 1 copy, 10% overhead;
- processed: 0.8 GB/day, 1 copy, 20% overhead;
- replica of raw: 1.0 GB/day, 1 copy, 10% overhead.
Using `total_storage = Σ(layer_volume × copies × (1 + overhead_factor))`, calculate one day’s total storage footprint and the 30-day footprint if the same daily volumes are retained for 30 days. State what is excluded.

**F04 — Topic 3 | Advanced | 5 marks**  
A workload averages 2,000,000 events/day. Use 86,400 seconds/day. Calculate average events/second and estimated peak events/second for a stated peak factor of 4. If a separate safety factor of 1.5 is applied to the estimated peak, calculate the design throughput. Explain the difference between a peak factor and a safety factor.

**F05 — Topic 3 | Advanced | 5 marks**  
Year 1 volume is 12 TB and annual compound growth is 20%. Calculate Year 2, Year 3, and the cumulative total across Years 1–3. State why cumulative retained volume may differ from this simple sum.

**F06 — Topic 4 | Intermediate | 5 marks**  
Calculate allowed downtime at 99.9% availability for:
1. a 30-day month in minutes;
2. a 365-day year in hours.
Use `allowed downtime = (1 − target) × period`.

**F07 — Topic 4 | Advanced | 5 marks**  
Three serial components each have availability 99.9%. Calculate end-to-end availability as `A = A1 × A2 × A3`. Then calculate the approximate downtime in a 30-day month. State the assumptions behind the serial model.

**F08 — Topic 4 | Advanced | 4 marks**  
A freshness target is p95 ≤ 30 seconds. A sample has 100 observations sorted by freshness; the 95th observation is 28 seconds and the 96th is 34 seconds. Using the simplified nearest-rank method `rank = ceil(p × N)`, calculate the p95 observation and say whether this sample meets the target. Note that production percentile conventions may vary.

**F09 — Topic 5 | Intermediate | 4 marks**  
Using a 1–5 ordinal scale where higher numbers mean more likelihood and impact, calculate exposure for:
- Risk A: likelihood 4, impact 5.
- Risk B: likelihood 2, impact 4.
Explain one limitation of multiplying ordinal scores.

**F10 — Topic 6 | Intermediate | 6 marks**  
Weights sum to 1. Ratings are 1–5, where 5 is most preferred. Use:
- Freshness (0.40): A=2, B=4, C=5
- Whole-life cost (0.25): A=5, B=4, C=2
- Operability (0.20): A=4, B=3, C=2
- Reversibility (0.15): A=4, B=3, C=2
Calculate each weighted score using `score = Σ(weight × rating)`. Rank the options **only if all have passed the mandatory gates**. Explain the limit of the score.

**F11 — Topic 6 | Advanced | 5 marks**  
Use `TCO = build cost + Σ(run cost + support cost per year) + exit cost`. Over three years:
- Option A: build 100, run 30/year, support 20/year, exit 10.
- Option B: build 140, run 20/year, support 15/year, exit 15.
All costs are illustrative thousands of currency units, undiscounted. Calculate TCO for both and state which is lower and what the model omits.

**F12 — Topic 6 | Advanced | 5 marks**  
Using F10 ratings, test a sensitivity case where freshness weight becomes 0.60 and the other weights are rescaled proportionally to preserve their original ratio. Original non-freshness weights are 0.25, 0.20, 0.15 (sum 0.60). Calculate new weights and new scores. Does the ranking change? Assume gates pass for this hypothetical arithmetic only.

**F13 — Topic 3 | Advanced | 5 marks**  
A 1.5 GB/day dataset grows 10% annually. Calculate annual volume in Year 5 if Year 1 is 1.5 GB, and cumulative annual volume across Years 1–5. Use compound growth and decimal GB.

**F14 — Topic 4 | Intermediate | 4 marks**  
A service has 99.5% availability target over a 30-day month. Calculate allowed downtime in minutes and hours. Explain why the calculation does not define maintenance exclusions or measurement scope.

---

# Section F2 — Roadmap-Prescribed Extension Exercises (Unscored, Required for Completion)

These exercises close specific coverage gaps between the scored assessment and the written roadmap. They are **not included in the 368-mark total**, but their artefacts must be reviewed for the corresponding topic completion gate. Use the same evidence-labeling rules as the scored questions.

**U01 — Topic 1 | Unscored completion exercise**  
Create (a) a 30-minute validation-session agenda for the Northbridge business-requirements summary, (b) a reusable validation-record template, and (c) a brief hypothetical interview record. Include participants/decision rights, artefacts to validate, questions/conflicts, acceptance criteria, dissent, decisions, actions with owners/dates, and version/sign-off evidence. In the interview record, preserve a sample statement and classify it as request, need, requirement, constraint, assumption, or solution preference without silently changing its meaning.

**U02 — Topic 2 | Unscored completion exercise**  
Classify each of the 20 statements below by primary category (business outcome, functional, non-functional, data-quality, constraint, assumption/dependency, preference, or solution request) and mark it **testable as written: yes/no/partly**. For each “no,” state the missing information or rewrite direction.

1. “Build a lakehouse.”
2. “The capability shall ingest approved card transactions from the card source.”
3. “The service must be fast.”
4. “p95 query latency shall be at most 2 seconds for the agreed workload, measured from request receipt to complete response.”
5. “Personal data must remain in the approved region under the confirmed policy.”
6. “Use Kafka for card events.”
7. “Invalid customer records shall be quarantined with a reason code and source reference.”
8. “All customer data must be accurate.”
9. “The daily risk report shall be available by 07:00 local time on 99% of business days in a rolling quarter, measured by completion timestamp.”
10. “The vendor says its API will be available next quarter.”
11. “The source team will provide an event contract by 1 December; the source owner has not confirmed this.”
12. “The team prefers its existing BI tool, but it can be changed.”
13. “The system shall retain approved transaction history for seven years, subject to confirmation by the accountable policy owner.”
14. “The pipeline should be highly scalable.”
15. “The service shall log every privileged access attempt with actor, timestamp, target, and outcome.”
16. “The platform shall be available 99.9% over each calendar month, measured by the agreed synthetic check and excluding only documented approved maintenance.”
17. “All duplicate customer identities must be reconciled.”
18. “The system shall support the approved identity provider.”
19. “We estimate annual transaction growth at 12%, but have not validated the estimate against historical data.”
20. “Fraud analysts need transaction information early enough to intervene before a subsequent attempt.”

**U03 — Topic 2 | Unscored completion exercise**  
Write twelve Northbridge requirements: six functional and six non-functional. Each row must include ID, type, source, objective, priority/status, scope, acceptance criterion or verification method, dependency, and architecture significance. At least two must address data quality/governance and at least two must address service quality. Do not turn an unapproved target into an accepted requirement.

**U04 — Topic 3 | Unscored completion exercise**  
Prepare a three-year capacity worksheet for the following explicitly illustrative streams. Use 365 days/year and decimal GB/TB. Assume two copies and 20% overhead per copy, with no compression. Apply each stream’s stated annual compound growth to its Year 1 annual flow.

| Stream | Daily workload | Average payload | Annual growth |
|---|---:|---:|---:|
| Transactions | 2,000,000 records/day | 500 bytes/record | 12% |
| Card events | 2,500,000 events/day | 300 bytes/event | 8% |
| Customer-profile changes | 150,000 changes/day | 2,000 bytes/change | 10% |

Calculate each stream’s Year 1 daily raw volume, annual flow in Years 1–3, three-year cumulative flow, combined raw cumulative flow, and illustrative footprint after copies/overhead. Label the estimate’s limitations, propose low/expected/high inputs for at least one uncertain driver, identify the most decision-sensitive input, and state one architecture implication. Also explain how a month-end workload at four times the average for three days affects peak-rate and capacity planning, and list five questions to validate a source team’s “about a million events a day” estimate. This is a separate illustrative exercise, not an assertion about Northbridge’s actual workloads.

**U05 — Topic 4 | Unscored completion exercise**  
Calculate allowed downtime for 99%, 99.5%, 99.9%, and 99.99% availability for both a 30-day month (minutes) and a 365-day year (hours). Explain why 100% availability is usually not a defensible target, why these values are target budgets rather than observed results, how an SLO error budget relates to allowed failure, and identify at least three required SLO scope/measurement decisions.

**U06 — Topic 6 | Unscored completion exercise**  
Using one decision matrix from E06/G05, write two recommendations from the same evidence: (a) a technical-review version with gates, criteria, evidence quality, sensitivity, trade-offs, reversibility, and reversal conditions; (b) a non-specialist sponsor version stating the business outcome, cost/risk, cost of delay or doing nothing, accepted trade-offs, open evidence, and the approval required. Do not change the recommendation between versions without explaining why.

**U07 — Topic 7 | Unscored completion exercise**  
Using the three Northbridge decision boundaries from the roadmap (fraud freshness path, authoritative customer-record approach, and retention/storage tiering), draft three separately scoped ADRs from the Topic 6 comparisons, plus a consistent decision-log index. Include at least one review finding and corrective action. Also create a short communication note for affected teams. Answer: if a team asks to skip ADRs “to go faster,” how would you apply proportionality and decide which decisions still warrant records? Preserve the distinction between a conditional decision and a formal status label.

---

# Section G — Integrated Northbridge Bank Case Study

**Case facts supplied by the roadmap (illustrative, not factual):** Northbridge is a fictional mid-sized retail and business bank. It has a core banking system, a separate cards platform, CRM, loan origination system, nightly extracts feeding an enterprise warehouse, and a data lake containing copies of some sources. Risk, Finance, Marketing, and Compliance report different customer counts. Fraud analysts see card transactions hours after the fact. A regulator has requested clearer evidence of lineage and customer-data accountability within a stated period.

**Additional scenario assumptions supplied for this case only (illustrative):**
- About 3 million retail customers.
- About 2 million card transactions/day on average.
- The card platform currently emits batch files every 15 minutes.
- Transaction retention is assumed to be seven years, pending validation.
- Personal data must remain in an approved jurisdiction.
- The core banking batch window ends at 02:30.
- The existing identity provider must be used.
- The sponsor has set a budget ceiling, but the amount is not supplied.
- The regulatory milestone date exists, but its exact date is not supplied.
- The source event contract, measured end-to-end freshness, and approved freshness target are unknown.

**Scope:** High-level requirements and option-category decisions only. Do not select detailed products, design schemas, or implement the platform.

**G01 — Topics 1–7 | Industry | 8 marks**  
Write the problem statement, three business objectives, scope, exclusions, and at least five stakeholder groups. Identify which statements are supplied scenario facts/assumptions and which objectives you are proposing for validation.

**G02 — Topics 1–2 | Industry | 8 marks**  
Create a requirement set with at least eight items: four functional and four non-functional/data-quality/governance requirements. Each must have an ID, source, type, priority, acceptance criterion or explicit open question, and links to business objectives. Do not embed technology choices. If the target is unknown, mark it pending rather than inventing an approved value.

**G03 — Topics 3–4 | Industry | 8 marks**  
Build a compact estimation worksheet and service-target proposal. Use supplied volumes and F01/F02-style calculations; identify peak, retention, growth, record-size, and profile-snapshot assumptions needing validation. Propose targets for fraud freshness, reporting, and availability with measurement boundary and acceptance method. Clearly label proposals as illustrative and pending approval.

**G04 — Topic 5 | Industry | 8 marks**  
Create a register with at least eight entries across constraints, assumptions, dependencies, risks, and unknowns. Include owners, validation dates or “to be agreed,” triggers, responses, and linked requirements/decisions. Identify at least two high-impact assumptions and explain how failure changes the architecture work.

**G05 — Topic 6 | Industry | 8 marks**  
Define the decision statement and scope for the fraud freshness path. Establish hard gates and scored criteria before scoring. Compare at least three alternatives including a minimal-change baseline. Use evidence labels, show a sensitivity analysis for the two least certain inputs, and recommend an option or explicitly state why no final recommendation is yet justified.

**G06 — Topic 7 | Industry | 8 marks**  
Write a complete ADR for one major decision. Include status, owner/deciders, context, drivers, alternatives, outcome, evidence-based rationale, rejected alternatives, consequences, assumptions, dependencies, open issues, and revisit conditions. If critical evidence is missing, keep the ADR Proposed, document the conditions and evidence needed for approval, and do not imply that “Conditional” is a repository-mandated status.

**G07 — Topics 1–7 | Industry | 8 marks**  
Create a traceability matrix with at least three business objectives linked to requirements, targets/estimates, constraints/assumptions/risks, decision criteria, and ADRs. Explain how you would test traceability in both directions and resolve a contradiction between the ADR and a source requirement.

**G08 — Topics 1–7 | Industry | 8 marks**  
Prepare a one-page sponsor summary and an independent-review checklist. The summary must state what is known, what remains open, major trade-offs, conditional decisions, and the next approval needed. Do not claim that a platform has been designed or built.

---

# Section H — Answer Key and Worked Solutions

## H1. Beginner answers

**B01 — C.** It describes a business outcome and decision need, not a technology. The wording still needs stakeholder validation and measurable success criteria.

**B02 — A.** Operations/support and control functions (risk, compliance, security, internal audit) often reveal requirements and constraints that the sponsor alone cannot provide.

**B03 — A.** It specifies system behaviour. Its validation rules and outcomes should be sourced and testable.

**B04 — C.** It has a deadline, frequency, window, and measurement point. It still needs a named source, scope, acceptor, and feasibility review.

**B05 — C.** \(2{,}000{,}000 \times 500 = 1{,}000{,}000{,}000\) bytes/day = 1.0 decimal GB/day.

**B06 — B.** Throughput is a rate; latency is elapsed time. Freshness measures data age relative to a source/event time, and availability measures whether the service meets its stated expectation.

**B07 — B.** It is an unverified assumption and an external dependency if the design requires the feed. Track owner, validation date, and fallback.

**B08 — C.** A mandatory gate is a feasibility condition, not a preference to be compensated for by other scores.

**B09 — B.** An ADR preserves one significant decision’s context, outcome, reasoning, alternatives, consequences, and lifecycle.

**B10 — B.** The chain begins with business need and follows through measurable requirements and evidence to criteria, comparison, and ADR. Traceability must also work backward.

**B11 — False.** “Build a dashboard” is a solution request. Ask what decision/outcome it supports, which users/data are in scope, and how success will be measured.

**B12 — False.** Important requirements should be testable. If the method is unknown, record the gap and resolve it before approval or explicitly justify why it cannot yet be measured.

**B13 — True.** Storage encoding, delimiters, metadata, indexes, null representation, compression, and physical layout change size.

**B14 — True.** High throughput can coexist with long queues or delayed publication; freshness depends on event age at consumption, not just processing rate.

**B15 — False.** A dependency is something the solution relies on; a risk is an uncertain event that could affect objectives. A late dependency can create a risk, so link the records rather than conflating them.

**B16 — False.** Weights and ratings contain judgement; criteria can be correlated and evidence uncertain. Scoring supports—not replaces—reasoning and sensitivity analysis.

**B17 — False.** Preserve history. Create a successor ADR when the outcome changes, link it to the old record, and mark the old one superseded.

**B18 — Model answer (3 marks).**
- Stakeholder: person/group that affects, uses, operates, controls, funds, or is affected by the capability.
- Request: what someone asks for, often solution-shaped.
- Underlying need: the problem or outcome behind the request.
- Business objective: desired organisational result.
Example: “Build a dashboard” (request) may arise from a need to reconcile inconsistent customer counts, supporting an objective of consistent governed reporting.

**B19 — Model answer (3 marks).**
- Functional: behaviour, e.g., ingest and validate card transaction records.
- Non-functional: quality of behaviour, e.g., p95 freshness ≤ an approved target, measured end-to-end.
- Constraint: a boundary, e.g., personal data must remain in an approved jurisdiction. Examples should be sourced and not presented as approved if invented.

**B20 — Model answer (3 marks).** Volume = amount of data; velocity = arrival/processing rate and burst pattern; variety = formats and structures. Relational customer table is structured; JSON API payload is semi-structured; scanned loan document is unstructured. Format alone does not establish size or workload.

**B21 — Model answer (3 marks).** Latency is elapsed time; freshness is data age relative to event/source time; throughput is quantity per time; availability is proportion of time the service meets its stated expectation. “Real-time” omits consumer, start/end timestamps, percentile, window, scope, and failure meaning.

**B22 — Model answer (3 marks).**
1. Constraint if current policy is confirmed and mandatory; cite policy and authority.
2. Assumption/estimate, because it is unvalidated.
3. Dependency, because ingestion relies on an external delivery.
4. Risk, because the uncertain delay could affect a milestone.
5. Preference, because it is explicitly negotiable. Award credit for noting that classification depends on evidence and who can change the item.

**B23 — Model answer (3 marks).** Requirements-based, quality, cost, time, risk, operability, strategic fit are valid categories. Hard gates determine eligibility; a failure cannot be offset by a low cost or high score elsewhere.

**B24 — Model answer (3 marks).** Context explains the problem, scope, and why a decision is needed. Rationale explains why the chosen outcome best fits the drivers and evidence. Rejected alternatives preserve fair comparison, show trade-offs, and prevent future teams from repeating the same analysis without understanding why an option lost.

## H2. Intermediate answers

**C01 — B.** Discover the need and boundaries before proposing a solution.

**C02 — C.** It defines observable behaviour, failure handling, traceability, and an acceptor. Exact rules and dataset still need an approved source.

**C03 — B.** A target cannot be met if the required data is not available until after the target boundary. Change the dependency/interface or negotiate an authorised requirement change.

**C04 — B.** A 0.02 score difference is not proof. Check rating evidence, score granularity, uncertainty, and whether a meaningful tie-break is needed.

**C05 — Model answer (5 marks).**
- Security/access candidate: “The customer-data capability shall enforce approved role- and purpose-based access rules for each classified customer attribute; verification shall test positive and negative access cases against the approved access matrix, with results accepted by the data owner and security reviewer.” Missing inputs: data classification, roles/purposes, policy owner, audit expectations, test set.
- Performance candidate (illustrative): “For the agreed customer-query workload, p95 response latency shall be ≤ 2 seconds over a 30-minute representative peak test, measured from request receipt to complete response.” The 2-second value is illustrative, not approved. Missing inputs: consumer, query mix, peak load, service boundary, percentile/window, acceptable error rate and business justification.

**C06 — Model answer (5 marks).** Award up to 2.5 marks per requirement for correct type, source/objective, testability, priority/status, and dependencies. Example:
- `REQ-EX-01` functional: “The capability shall ingest customer identity attributes from the approved source systems and retain source provenance.” Source: proposed data owner; priority Must (pending validation); acceptance: source-to-target reconciliation and lineage test on an agreed sample; dependency: source access and mapping approval.
- `REQ-EX-02` non-functional: “The agreed customer-count report shall be available by an agreed business deadline on a specified proportion of business days, measured by report-completion timestamp.” Target pending stakeholder validation; acceptance method must be defined. Do not mark an invented target approved.

**C07 — Model answer (5 marks).** Example stakeholder plan:
| Group | Concern | Technique | Open question |
|---|---|---|---|
| CDO/sponsor | Business outcomes, budget, milestone | Structured interview | Which outcome and deadline are mandatory? |
| Risk | Consistent exposure/customer counts | Workshop | Which definition and reconciliation tolerance are acceptable? |
| Finance | Reporting close and count definitions | Interview/document review | What is the accounting/reporting cut-off? |
| Fraud operations | Transaction freshness and case workflow | Workflow observation | At what delay does intervention value materially fall? |
| Compliance | Lineage, accountability, data minimisation | Requirements workshop | What evidence must be retained and reviewed? |
| Security | Identity/access/residency | Control review | Which approved policy and access model apply? |
| Source/card platform owner | Interface and throughput | Technical interview | What feed/event contract and peak rate are supported? |
| Operations | Monitoring, recovery, staffing | Operational readiness review | Who owns incidents and what recovery is required? |
Full credit needs six groups and questions, including operations/control.

**C08 — Model answer (4 marks).** Interests: Marketing needs useful, timely analysis; Compliance needs lawful/policy-aligned access, minimisation, and evidence. Do not assume either objective overrides the other. Decision forum should include accountable business/data owner and compliance/privacy/security authorities. Evidence: data classification, purpose/use cases, access policy, legal/policy interpretation from responsible experts, attribute-level need, audit requirements, risk assessment, and feasible access alternatives. Record unresolved conflict and owner/date.

**C09 — Model answer (5 marks).**
1. “Use Kafka” embeds a solution; rewrite as behaviour/need and treat Kafka only as an option.
2. “Quickly” is vague; define consumer, boundary, percentile, target, window, and method.
3. Functional but underspecified: define scope, source, required fields/quality, failure handling, and acceptance test.
4. “Accurate” is vague and overbroad; define dimensions (e.g., completeness, validity, reconciliation tolerance), population, source of truth, and measurement.
5. Most measurable of the set; still add source, scope, acceptor, exception rules, and validation method if missing.

**C10 — Model answer (5 marks).** One example per class:
| ID/class | Statement | Owner | Validation/response | Linked decision |
|---|---|---|---|---|
| CON-01 | Personal data stays in approved jurisdiction (illustrative scenario constraint) | Compliance/privacy role | Confirm applicable policy and region | Customer-record/storage ADR |
| ASM-01 | Card platform can supply a usable feed beyond current batch files (assumption) | Card platform owner | Confirm interface and test | Freshness ADR |
| DEP-01 | Source interface delivery precedes ingestion test (dependency) | Source owner | Commitment/date and escalation | Freshness ADR |
| RSK-01 | Interface delay threatens milestone (risk) | Programme lead | Mitigate/fallback/trigger | Freshness ADR |
| UNK-01 | Exact approved p95 freshness target is not yet known | Fraud product owner | Elicit, approve and record target | Freshness ADR |
Classifications can vary if evidence changes. All need source/owner and actionable validation/response.

**C11 — Model answer (4 marks).** Record the missing stakeholder, expected return date, questions/requirements they own, and the risk of proceeding without them. Continue reversible discovery/estimation and mark affected requirements or decisions provisional. Keep any choice dependent on their input conditional. Reopen stakeholder register, requirements/conflict log, target/constraint registers, decision criteria and related ADRs as needed.

**C12 — Model answer (4 marks).** The statement is an unconfirmed vendor claim; record it as an assumption/statement requiring verification and a dependency if the design relies on the API. Risk: API delay or absence could block delivery. Validate through a named vendor/source owner, written commitment, interface specification, date, service limits and test evidence. Assign owner/date/trigger; fallback could be current batch or another feasible option, but do not assume it meets the target.

**C13 — Worked solution (4 marks).**
Daily raw bytes = 3,200,000 records/day × 750 bytes/record = 2,400,000,000 bytes/day = **2.4 GB/day**.
Annual raw volume = 2.4 GB/day × 365 days/year = **876 GB/year = 0.876 TB/year**.
Assumptions/limits: record size is average and excludes indexes/metadata/compression/replicas; every day has the same volume; no retention or growth adjustment is included.

**C14 — Worked solution (4 marks).** Year 1 = 12 TB. Year 2 = 12 × 1.20 = 14.4 TB. Year 3 = 14.4 × 1.20 = **17.28 TB**. Sum Years 1–3 = 12 + 14.4 + 17.28 = **43.68 TB** of annual generated volume across the three years. This is not automatically the end-of-Year-3 retained footprint: retention, deletions, copies, overhead, compression, and whether the measure is annual flow or retained stock must be defined.

**C15 — Worked solution (4 marks).** 99.9% availability means downtime fraction = 1 − 0.999 = 0.001. Thirty days = 30 × 24 × 60 = 43,200 minutes; allowed downtime = 43,200 × 0.001 = **43.2 minutes**. A 365-day year = 8,760 hours; 8,760 × 0.001 = **8.76 hours**. These are mathematical budgets for a target, not observed service results. Scope and exclusions still need definition.

**C16 — Worked solution (5 marks).** Total = 8 + 4 + 9 + 5 + 3 = **29 seconds**. It passes a 30-second arithmetic budget with 1 second remaining, but this does not prove operational feasibility; measurement boundary, queueing, variability, and percentile must be tested. Because the stated sum is 29 seconds, no adjustment is required for the arithmetic gate. If the design needs a 2-second reserve for unallocated overhead, reduce one or more stage budgets by a total of 1 second so the planned stages sum to 28 seconds; whether any allocation is achievable must still be measured. Award credit for checking the sum and distinguishing arithmetic from operational feasibility.

**C17 — Worked solution (4 marks).** Eight hours = 8 × 3,600 = 28,800 seconds. Average = 2,400,000 / 28,800 = **83.33 events/s**. Estimated peak = 83.33 × 4 = **333.33 events/s**. This is an estimate derived from an assumed peak factor, not a measured peak; validate using time-series source observations and bursts/seasonality.

## H3. Advanced answers

**D01 — B.** Update the source artefact first and follow traceability links forward. This preserves provenance and identifies affected estimates, targets, criteria, risks, and ADRs.

**D02 — B.** A hard gate is not a weighted preference. Only an authorised requirement change can alter the gate; then rerun feasibility and comparison.

**D03 — B.** Preserve history, validate the change, reassess options, and create a linked successor if the outcome changes.

**D04 — Model answer (5 marks).**
- Hypotheses: different “customer” definitions; different reporting cut-offs; duplicate/merged identities; inclusion/exclusion of closed/inactive records; different source freshness; different filters.
- Stakeholders: Risk, Finance, data owners, CRM/core/card source owners, compliance/data governance, report operators.
- Evidence: query definitions, source extracts, timestamps, lineage, reconciliation samples, data-quality rules, ownership definitions.
- Conflict-log row: “Risk and Finance counts differ; business impact: inconsistent reporting; owner: data governance lead; evidence: query logic, population definition, cut-off, sample reconciliation; due date: agreed; status: open.”
- Resolution: agree a business definition and authoritative stewardship, test sample cases, play results back to both groups, record acceptance/sign-off. Do not assume a single count is correct before investigation.

**D05 — Model answer (5 marks).** Record the new stakeholder/source and version; classify and clarify the requirement; define scope, measurable acceptance criteria and acceptor; consult responsible compliance/privacy/security experts; assess conflicts with access requirements; trace to affected requirements, targets, constraints, risks, criteria and ADRs; update the source records first; rerun gates and alternatives; record the approved change and any successor ADR. Avoid interpreting legal obligations without authoritative advice.

**D06 — Model answer (5 marks).** Investigate time window, event definition, duplicates/retries, average versus peak, records versus messages, inclusion/exclusion filters, late-arriving events, timezone/day boundaries, sampling bias, and units. Obtain source counts/logs over representative periods, reconcile a sample, document formula/source/date/units and low/expected/high range, assign confidence, and identify the estimate’s impact on capacity/target decisions.

**D07 — Model answer (5 marks).** Measure p50/p95/p99 and distribution, not only mean; segment by query/report, user group, data size, time of day and concurrency; define start/end boundary and client/server instrumentation; inspect queueing/utilisation near capacity and upstream waits; compare representative peak and normal windows. If the target does not represent business need, return to stakeholders to revise it formally rather than hide failure by changing the metric.

**D08 — Model answer (5 marks).** Validate (a) first: low confidence and failure blocks the freshness path. Validate (c) next: low confidence and failure could make support infeasible. (b) may be lower priority if short-term impact is low, though its long-term cost effect should be quantified. For (a), trigger = interface cannot be demonstrated by agreed date; fallback = reassess micro-batch/batch or reopen target. For (c), trigger = staffing plan not approved by readiness gate; fallback = funded support model, managed operation, reduced scope, or delayed approval. For (b), trigger = observed growth deviates beyond agreed range; update estimate/TCO/tiering. Order can differ if evidence shows different impacts.

**D09 — Model answer (6 marks).** Fix criteria/weights before scoring; verify each option passes hard gates; use comparable evidence and disclose unknowns. Check correlated criteria to avoid double counting; vary weights and low/base/high uncertain inputs; report whether and where rankings flip. If rankings remain stable, recommendation is more robust. If they flip easily, run a discriminating test, record a justified tie-break, or choose a reversible/pilot path. Record what the decision gives up and what evidence would make the runner-up preferable. Small score differences are not proof.

**D10 — Model answer (5 marks).** State that only a bounded pilot or preparatory work is authorised (if the actual owner approves); production selection remains blocked. Missing evidence: written vendor commitment/interface contract, limits, test results, security review, support readiness. Name owner, due date, pass/fail threshold and verifier. Fallback if failed; status Proposed with explicit conditions for approval; revisit when evidence arrives or the deadline/commitment changes.

**D11 — Model answer (5 marks).** Defects include: no decision scope; no business problem; adjective-only context/rationale; no decision owner/deciders/date; unsupported Accepted status; no measurable drivers or linked requirements; straw-man alternative; no fair comparison/evidence; no negative consequences/trade-offs; no assumptions/dependencies/open issues; no revisit conditions; no references; no traceability; no approval history. Award marks for six distinct material defects and why they matter.

**D12 — Model answer (5 marks).** Record only what notes/participants can substantiate. Mark Proposed or decision confirmation required until the accountable owner confirms outcome/status. Recover evidence from comparison matrices, requirements, risk records and review notes; distinguish confirmed facts from reconstructed context. Assign open issues/owners/dates, document approval and review history when confirmed, and do not invent rationale. If approval cannot be established, do not label Accepted.

**D13 — Model answer (6 marks).**
- A “real-time” request must be converted into a consumer-specific measurable freshness target; the value and measurement boundary are unknown.
- Core batch cutoff at 02:30 constrains core-source freshness; a target requiring data before the source publishes is infeasible unless the source path/requirement changes.
- Card files every 15 minutes impose a source cadence constraint/assumption; end-to-end target may be tighter than the source interface permits.
- Residency is a hard gate if confirmed mandatory; options violating it are ineligible.
- Unconfirmed event contract is an assumption/dependency; failure threatens the target and milestone.
- Budget ceiling is a constraint, but amount and cost model are missing.
- Regulatory milestone is a time constraint, but exact date and evidence expected are missing.
- Ask owners to confirm definition of “customer,” source of truth, freshness need, acceptable availability, target acceptance, residency policy, budget amount, milestone date, interface commitment, and operational support. No final option should be declared until gates and evidence are known.

## H4. Industry case model answers

**E01 — Model answer (8 marks).** Full credit requires a coherent register and summary, not a single prescribed stakeholder list. At minimum include sponsor/CDO, Risk, Finance, Fraud Operations, Marketing, Compliance, Security, source-system owners, Operations, and Internal Audit as relevant. Questions should address objective, definition of customer, reconciliation, freshness, access, lineage, controls, operational support, and decision authority. Proposed success criteria should be validated, for example: agreed customer definition; traceable lineage for in-scope fields; fraud freshness target approved by Fraud; reconciliation test accepted by Risk and Finance. Do not invent a final numerical target.

**E02 — Model answer (8 marks).** Example requirements:
- Functional: ingest customer/account/card transaction records from approved sources; preserve source provenance; reconcile duplicate/customer identity cases; quarantine invalid records with reason codes.
- Non-functional/data quality/governance: freshness target pending approval; approved-region residency; role/purpose access; lineage/audit evidence; reconciliation tolerance defined with owners.
Every row needs source, priority, objective link, verification, dependencies, status. Mark unresolved values `TBD` with owner/date. Trace at least three rows through `BO → REQ → TGT/EST/CON/ASM/RSK → DC → ADR`.

**E03 — Worked solution (8 marks).**
- Transactions/day = 2,000,000 × 500 bytes = 1,000,000,000 bytes = **1.0 GB/day**.
- Year 1 raw transaction volume = 1.0 × 365 = **365 GB = 0.365 TB**.
- Year 7 annual flow with 12% compound growth: \(365 \times 1.12^6\) GB ≈ **720.445 GB ≈ 0.720 TB**. Year 1 is base year, so Year 7 has six growth intervals.
- Seven-year cumulative raw transaction flow = \(365 \times \sum_{k=0}^{6}1.12^k\) GB ≈ **3,682.5 GB ≈ 3.682 TB**.
- Two retained copies, 25% overhead on each copy: multiply raw cumulative flow by 2 × 1.25 = 2.5, giving **about 9.206 TB** illustrative footprint.
- Daily profile snapshot = 3,000,000 × 2,000 bytes = 6,000,000,000 bytes = **6 GB/day**.
- Ten-year cumulative raw transaction flow = \(365 \times \sum_{k=0}^{9}1.12^k\) GB ≈ **6,405.3 GB = 6.405 TB**. With two copies and 25% overhead per copy (factor 2.5), the illustrative footprint is **16.013 TB**, versus **9.206 TB** for seven years. This comparison assumes every year’s generated flow remains retained and applies the same overhead to all retained data.
Limitations: assumes average record sizes, constant daily counts except specified transaction growth, no compression, no additional processed layers/indexes/logs, snapshots retained daily without deduplication, and overhead exactly 25%. Validate sample sizes, growth, copies, retention semantics, deletion/updates, peak/burst rates, and whether profile snapshot is full daily snapshot or change-only.

**E04 — Model answer (8 marks).** Targets should differ by consumer. Fraud may need low-latency transaction freshness; risk reports may be due before a business deadline; regulatory submissions need accuracy, lineage and submission deadline; marketing segmentation may tolerate longer freshness but require purpose-based access; executive dashboards may need scheduled freshness and availability. Each target must name indicator, target, percentile if applicable, window, scope, measurement method, acceptor and rationale. Any numbers must be illustrative and approved by stakeholders. For the fraud path, decompose end-to-end budget into source handoff, transport, processing, load and publish, ensuring the sum does not exceed the approved end-to-end budget.

**E05 — Model answer (8 marks).** A complete register includes at least ten classified entries with owner/source and action. Example categories: current systems and reported delayed fraud data as supplied scenario facts; approved jurisdiction and identity-provider use as illustrative constraints; interface capability as an assumption; source owner delivery as a dependency; late interface/regulatory milestone as a risk; exact freshness target/budget/milestone date as unknown; BI tool preference as negotiable. Text dependency map: `source owner/interface → ingestion validation → transformation/quality → fraud case tool publication → measured acceptance`; in parallel `policy/control approval → access and residency sign-off`; critical path depends on confirmed milestone and source interface. Escalation note should state exposure, evidence, response options, decision needed, owner, trigger, and deadline.

**E06 — Model answer (8 marks).** Define a hard freshness gate and confirmed control/residency gate. Use at least four scored criteria such as TCO, operational burden, delivery time, capacity/headroom, and reversibility; weights sum to 1 and are fixed before ratings. Option A may be cheaper/easier but may not meet a stricter target; B may balance freshness and operations; C may offer lower delay but higher continuous-operation burden. Because no approved target or measured performance is supplied, feasibility remains **unverified**. Do not claim a score can compensate for a failed gate. Sensitivity should vary two least-certain inputs, such as peak factor and event-contract delivery/cost; report if ranking flips and what evidence resolves uncertainty.

**E07 — Model answer (8 marks).** The ADR must have one coherent decision, truthful status, owner/deciders, context, traceable drivers, three credible options, outcome, evidence-backed rationale, rejected alternatives, positive/negative consequences, accepted trade-offs, assumptions/dependencies, open issues, evidence links and revisit conditions. If no validated target or comparison evidence exists, status should be Proposed, with the outstanding approval conditions and evidence recorded explicitly. Decision-log row must match the ADR. Review checks should include scope, alternatives, gates, traceability, consequences, uncertainty, status/approval, references, revisit trigger and consistency with other ADRs.

## H5. Quantitative solutions

**F01 — Worked solution (4 marks).**  
\(2{,}000{,}000\ \text{records/day} \times 500\ \text{bytes/record} = 1{,}000{,}000{,}000\ \text{bytes/day}\). Decimal GB: \(1{,}000{,}000{,}000 / 10^9 = \mathbf{1.0\ GB/day}\).

**F02 — Worked solution (4 marks).**  
30-day volume = 1.0 GB/day × 30 = **30 GB**.  
365-day volume = 1.0 GB/day × 365 = **365 GB = 0.365 TB**.  
These are raw flow totals, not necessarily retained storage footprint.

**F03 — Worked solution (5 marks).**  
Raw layer: 1.0 × 1 × 1.10 = 1.10 GB/day.  
Processed: 0.8 × 1 × 1.20 = 0.96 GB/day.  
Replica: 1.0 × 1 × 1.10 = 1.10 GB/day.  
Total = 1.10 + 0.96 + 1.10 = **3.16 GB/day**.  
Thirty days retained = 3.16 × 30 = **94.8 GB**.  
Excludes indexes, snapshots, backup copies beyond those named, metadata, compression, data growth, and operational logs. Assumes each layer’s stated daily volume is retained for the same 30 days.

**F04 — Worked solution (5 marks).**  
Average = 2,000,000 / 86,400 = **23.148 events/s**.  
Estimated peak = 23.148 × 4 = **92.593 events/s**.  
Design throughput = 92.593 × 1.5 = **138.889 events/s** (about 139 events/s).  
Peak factor estimates a workload’s peak relative to average; safety factor adds design headroom to the estimated peak. Neither is measured evidence unless validated against observations.

**F05 — Worked solution (5 marks).**  
Year 1 = 12 TB. Year 2 = 12 × 1.2 = **14.4 TB**. Year 3 = 14.4 × 1.2 = **17.28 TB**. Cumulative flow = 12 + 14.4 + 17.28 = **43.68 TB**. Retained storage may differ due to retention/deletion, multiple layers/copies, overhead, compression, and whether annual volume is generated flow or end-of-year stock.

**F06 — Worked solution (5 marks).**  
99.9% target means unavailability = 0.001. Month: 30 × 24 × 60 = 43,200 min; downtime = 43,200 × 0.001 = **43.2 min**. Year: 365 × 24 = 8,760 h; downtime = 8,760 × 0.001 = **8.76 h**.

**F07 — Worked solution (5 marks).**  
Each component availability = 0.999. Serial end-to-end availability = \(0.999^3 = 0.997002999\), or **99.7003% (approximately 99.7%)**. Monthly unavailability = 1 − 0.997002999 = 0.002997001. Downtime = 43,200 min × 0.002997001 ≈ **129.47 minutes**, about **2.16 hours**. Assumes all three components are serially required, availability events are independent enough for the multiplication model, and the same 30-day window/scope applies. Correlated failures or redundancy require a different model.

**F08 — Worked solution (4 marks).**  
Nearest-rank p95 rank = ceil(0.95 × 100) = ceil(95) = 95. The 95th observation is **28 seconds**, so the sample meets p95 ≤ 30 seconds under the stated simplified method. The 96th observation is not used for this method’s p95. Real measurement systems may use another documented percentile convention; state it.

**F09 — Worked solution (4 marks).**  
Risk A exposure = 4 × 5 = **20**. Risk B = 2 × 4 = **8**. Under the stated ordinal scale, A receives higher priority for review. Limitation: ordinal numbers do not guarantee equal intervals; multiplying them is a prioritisation heuristic, not a precise loss estimate or probability.

**F10 — Worked solution (6 marks).**  
Option A = 0.40×2 + 0.25×5 + 0.20×4 + 0.15×4 = 0.80 + 1.25 + 0.80 + 0.60 = **3.45**.  
Option B = 0.40×4 + 0.25×4 + 0.20×3 + 0.15×3 = 1.60 + 1.00 + 0.60 + 0.45 = **3.65**.  
Option C = 0.40×5 + 0.25×2 + 0.20×2 + 0.15×2 = 2.00 + 0.50 + 0.40 + 0.30 = **3.20**.  
Arithmetic ranking: **B (3.65), A (3.45), C (3.20)**, but this ranking is usable only if every option passes the mandatory gates. Scores are judgement-dependent, may double-count correlated criteria, and hide evidence uncertainty.

**F11 — Worked solution (5 marks).**  
Option A: 100 + 3×(30+20) + 10 = 100 + 150 + 10 = **260 thousand**.  
Option B: 140 + 3×(20+15) + 15 = 140 + 105 + 15 = **260 thousand**.  
They tie under this undiscounted model. It omits discount rate/time value, inflation, taxes, contingency, detailed staffing ramp, cost uncertainty, cost of delay, failure/incident costs, benefits, and the possibility that costs change over time. Do not call either cheaper.

**F12 — Worked solution (5 marks).**  
Freshness weight = 0.60. Remaining 0.40 is split in original ratio 0.25:0.20:0.15, total 0.60:
- Cost = 0.40 × (0.25/0.60) = **0.166667**.
- Operability = 0.40 × (0.20/0.60) = **0.133333**.
- Reversibility = 0.40 × (0.15/0.60) = **0.100000**.
New A = 0.60×2 + 0.166667×5 + 0.133333×4 + 0.10×4 ≈ **2.9667**.  
New B = 0.60×4 + 0.166667×4 + 0.133333×3 + 0.10×3 ≈ **3.7667**.  
New C = 0.60×5 + 0.166667×2 + 0.133333×2 + 0.10×2 ≈ **3.8000**.  
Ranking changes from B > A > C to **C > B > A** (C exceeds B by about 0.0333). This tiny margin is fragile; investigate evidence and other plausible weights. The question explicitly assumes gates pass only for this arithmetic exercise.

**F13 — Worked solution (5 marks).**  
Year 1 = 1.5 GB. Year 5 = \(1.5 × 1.10^4 = 1.5 × 1.4641 = \mathbf{2.19615\ GB}\). Cumulative Years 1–5 = 1.5 × (1 + 1.1 + 1.21 + 1.331 + 1.4641) = 1.5 × 6.1051 = **9.15765 GB**. Rounded results should preserve the assumptions and unit.

**F14 — Worked solution (4 marks).**  
99.5% availability means downtime fraction = 0.005. Thirty days = 43,200 minutes; allowed downtime = 43,200 × 0.005 = **216 minutes = 3.6 hours**. The calculation is only a budget under the stated period. It does not define service scope, maintenance exclusions, incident counting, dependencies, or measurement source; those must be specified.

## H6. Integrated case answer guidance

**G01 (8 marks):** Strong answer states the inconsistent customer counts, delayed fraud signals, and lineage/accountability evidence gap. Objectives should be proposed for stakeholder validation: agreed customer definition/count, fraud data delivered within an approved measurable target, and auditable lineage/ownership. Scope includes customer/account/card transaction data and high-level consolidation/timeliness/governance decisions. Exclusions include detailed schemas, product choice, implementation, migration, and later-module designs. Clearly separate supplied scenario assumptions from proposed objectives.

**G02 (8 marks):** Strong answer has eight distinct requirements, no embedded technology, source and objective links, measurable acceptance or a named unresolved input/owner. Functional examples: ingest approved sources, validate records, preserve provenance, reconcile customer identities. Non-functional/data/governance examples: approved-region residency, access controls, measurable freshness target pending approval, lineage evidence, reconciliation quality target pending agreement. Mark unapproved targets `Proposed/TBD`, not Accepted.

**G03 (8 marks):** Must show correct raw transaction calculation: 2,000,000 × 500 = 1.0 GB/day; 365 GB/year at a flat daily rate before growth/copies. Identify missing profile record size if not using the supplied profile assumption, peak factor, growth basis, retention semantics, storage overhead, and source event timing. Targets need indicator, scope, percentile/window where relevant, start/end measurement, method and acceptor. Proposed target values are illustrative until approved.

**G04 (8 marks):** Strong register distinguishes constraint from preference, assumption from fact, dependency from risk, and unknown from all of them. Each high-exposure risk has response/owner/trigger; each high-impact assumption has validation method/date. Failure of source interface assumption reopens freshness estimates, targets, criteria, alternatives and ADR; residency constraint can eliminate options before scoring.

**G05 (8 marks):** A valid answer defines scope and decision-maker, identifies mandatory gates, fixes scored criteria before scoring, includes at least three credible alternatives including minimal-change baseline, links ratings to evidence, runs sensitivity on two uncertain inputs, and states trade-offs. Given missing target and performance evidence, a conditional recommendation/no final choice is often the strongest answer. A choice is not required if the evidence does not support one.

**G06 (8 marks):** Assess one coherent decision. Full credit requires all key ADR sections, linked IDs, fair rejected alternatives, honest status, positive/negative consequences, open issues and revisit conditions. If approval/evidence is missing, do not label Accepted.

**G07 (8 marks):** Matrix should support both directions: objective-to-current ADR and ADR-to-business objective. Check links, source artefact versions, IDs and status. If ADR contradicts a requirement, update/validate the source requirement first, perform impact analysis, rerun gates/comparison, and create a successor ADR if the decision changes.

**G08 (8 marks):** Sponsor summary is concise and plain-language. It distinguishes known facts, assumptions, estimates, open issues, conditional decisions, accepted trade-offs and the specific approval needed. Review checklist verifies requirements/targets, arithmetic, risk owners/triggers, alternatives/gates, sensitivity, ADR status/traceability, and no unflagged contradictions. Do not claim implementation.

---

## H7. Roadmap-prescribed extension exercise evaluation criteria

These are unscored completion-gate exercises; evaluate them against the criteria below rather than adding marks to the 368-mark total.

**U01 — Evaluation criteria.** Full evidence includes a timed agenda with purpose, participants and decision rights, artefacts/version to validate, requirement/objective walk-through, unresolved conflicts, acceptance criteria, sign-off method, and a record template capturing decision, dissent, action owner/date, and version. The interview record preserves the statement and labels its type without turning a solution request into a requirement. A meeting invitation alone is insufficient.

**U02 — Classification key (primary category; reasonable secondary labels may be accepted where explained).**

| # | Primary classification | Testable as written? | Required reasoning/repair |
|---:|---|---|---|
| 1 | Solution request | No | Elicit outcome, consumers, scope, success criteria before selecting a platform. |
| 2 | Functional requirement | Partly | Behaviour is clear, but source/scope and acceptance test need confirmation. |
| 3 | Vague non-functional requirement | No | Define consumer, workload, metric, target, percentile/window, boundary and method. |
| 4 | Non-functional performance requirement | Yes, subject to workload approval | Workload and boundary must be agreed and reproducible. |
| 5 | Constraint/policy requirement | Partly | It becomes a verified constraint only after the authoritative policy, approved region, scope and owner are confirmed. |
| 6 | Solution request | No | Treat Kafka as an option, not a requirement. |
| 7 | Functional/data-quality requirement | Partly | Define invalidity rules, source population, quarantine handling and acceptance test. |
| 8 | Vague data-quality requirement | No | Define quality dimensions, thresholds, population, source of truth and measurement. |
| 9 | Non-functional/reporting availability requirement | Yes, subject to scope/acceptor confirmation | The target and measurement point are explicit; confirm calendar, exclusions and owner. |
| 10 | Unverified vendor claim; assumption/dependency if relied on | No | Obtain named owner, commitment, interface specification, limits, date and test evidence. |
| 11 | Assumption and potential dependency | No | It is expressly unconfirmed; validate with source owner and fallback. |
| 12 | Preference | No | It is negotiable and should not be treated as a system requirement or constraint. |
| 13 | Retention requirement pending policy validation | Not yet approved/testable as a final requirement | Confirm authoritative retention basis, scope, deletion rules and acceptance evidence. |
| 14 | Vague non-functional requirement | No | Define workload, scale envelope, latency/capacity and test method. |
| 15 | Functional/security audit requirement | Partly | Confirm event coverage, retention, access to logs, failure handling and test. |
| 16 | Non-functional availability requirement | Yes, if the check and exclusions are formally agreed | Clarify dependency coverage and whether planned maintenance exclusions are authorised. |
| 17 | Vague data-quality requirement | No | Define duplicate identity, matching rules, exception handling, tolerance and acceptor. |
| 18 | Constraint or compatibility requirement | Partly | Name the provider, confirm the constraint authority, specify integration behaviour and verification. |
| 19 | Assumption/estimate | No | Validate against historical time-series data and record range/confidence. |
| 20 | Business need/outcome statement | No | Elicit measurable intervention window, consumer, timestamp boundary and success evidence. |

**U03 — Evaluation criteria.** Review all twelve rows for six functional and six non-functional requirements, correct type, source/objective traceability, priority/status, scope, testable acceptance/verification, dependency, and architecture significance. Full credit is not tied to the exact example wording. Any target not approved by its owner must remain proposed/TBD with an action to resolve it.

**U04 — Worked solution.** Daily raw volumes: transactions = **1.0 GB/day**; card events = **0.75 GB/day**; customer-profile changes = **0.30 GB/day**. Annual Year 1 flow is respectively **365 GB**, **273.75 GB**, and **109.5 GB**.

| Stream | Year 1 (GB) | Year 2 (GB) | Year 3 (GB) | Three-year cumulative (GB) |
|---|---:|---:|---:|---:|
| Transactions | 365.000 | 408.800 | 457.856 | 1,231.656 |
| Card events | 273.750 | 295.650 | 319.302 | 888.702 |
| Customer-profile changes | 109.500 | 120.450 | 132.495 | 362.445 |
| **Total** | **748.250** | **824.900** | **909.653** | **2,482.803** |

Combined cumulative raw flow = **2,482.803 GB = 2.482803 TB**. Two copies with 20% overhead per copy gives factor `2 × 1.20 = 2.4`, so illustrative footprint = **5,958.7272 GB ≈ 5.959 TB**. This assumes each year’s generated flow is retained, applies growth as stated, and excludes indexes, metadata, logs, backup beyond the two copies, compression, and workload variation. Suitable sensitivity inputs include daily counts, average payload, growth, peak factor, and retention. The most decision-sensitive input must be justified from the scenario and tested by varying it; do not simply assert a ranking without calculation. A month-end burst at four times average for three days raises peak ingestion/processing and queueing needs even if annual storage flow is unchanged; confirm the peak factor from time-series evidence. Five estimate-validation questions should cover event definition, time window/time zone, duplicates/retries, average versus peak/bursts, and source/log evidence (equivalent questions accepted).

**U05 — Worked solution.**

| Availability target | 30-day month allowed downtime | 365-day year allowed downtime |
|---:|---:|---:|
| 99% | 432 minutes (7.2 hours) | 87.6 hours |
| 99.5% | 216 minutes (3.6 hours) | 43.8 hours |
| 99.9% | 43.2 minutes | 8.76 hours |
| 99.99% | 4.32 minutes | 0.876 hours (52.56 minutes) |

These are mathematical budgets, not measured results. A valid SLO still needs service/consumer scope, measurement method and source, period, dependency coverage, incident counting, and maintenance/exclusion policy. A 100% target leaves no allowance for any failure and may be infeasible across dependent components; the business must choose a defensible target and understand the reliability/cost trade-off. The error budget is the allowed failure/downtime implied by the SLO over its measurement window, not a promise that failures will occur only within a predictable pattern.

**U06 — Evaluation criteria.** The two versions must be consistent with each other and the matrix. The technical version should preserve gates, evidence, uncertainty, sensitivity, trade-offs, reversibility and reversal conditions. The sponsor version should state the decision requested, business consequence, cost/risk, cost of delay/doing nothing, accepted trade-off, unresolved evidence, and next approval in plain language. Do not hide uncertainty or introduce new claims.

**U07 — Evaluation criteria.** Three distinct ADRs should cover the specified decision boundaries, each with one coherent outcome, accurate status, owner/deciders, date, context, traceable drivers, at least three credible options where applicable, rationale, rejected alternatives, consequences, assumptions, dependencies/open issues, evidence references and revisit conditions. The index must agree with each ADR’s ID/status/date/owner and supersession links. Review finding must name defect, evidence, correction and status. The communication note should state the decision, rationale, consequences, owners/actions and where the record lives. ADR effort should be proportional: skip trivial reversible implementation choices, but record decisions that are hard to reverse, cross teams/quality attributes, accept material risk, or are likely to be revisited. Conditional describes the decision’s conditions; the roadmap’s proposed formal status vocabulary is Proposed, Accepted, Deprecated and Superseded.

---

# Section I — Scoring Rubric and Mastery Assessment

## I1. Score bands

The maximum is **368 marks**. Use these bands as diagnostic indicators; the roadmap’s artefact-based completion gate remains mandatory.

| Level | Score band | Observable standard |
|---|---:|---|
| Beginner | 0–220 | Gaps remain in terminology, classification, unit handling, or basic distinctions. Re-study and re-attempt. |
| Intermediate | 221–276 | Applies basic methods, but may miss evidence, acceptance criteria, assumptions, or consistent traceability. |
| Advanced | 277–322 | Handles ambiguity, trade-offs, uncertainty and calculations; answers need only limited correction. |
| Industry-application candidate | 323–368 | Produces defensible artefacts and can explain decisions under review. Must still pass all completion-gate evidence checks. |

These ranges do not override minimum capability requirements. A high total cannot compensate for a critical failure such as an unmeasurable “must,” a wrong unit conversion used in a decision, a hard-gate failure hidden by a weighted score, or an ADR falsely labelled accepted.

## I2. Artefact quality rubric

Score each industry deliverable from 0–4 for each dimension, then record evidence. Use this to guide feedback; do not add these points to the 368-mark scored-question total unless the assessor explicitly defines a separate supplementary score.

| Dimension | 0 — Missing | 1 — Weak | 2 — Partial | 3 — Good | 4 — Review-ready |
|---|---|---|---|---|---|
| Source and provenance | No source | Vague source | Some IDs/sources | Sources mostly traceable | Every material claim has provenance/evidence label |
| Testability/measurement | Not testable | Mostly adjectives | Some metrics | Measurable with minor gaps | Metric, target, scope, method, acceptor all clear |
| Assumptions/uncertainty | Hidden | Labelled inconsistently | Main assumptions stated | Owners and validation present | Impact/confidence, date, trigger and fallback explicit |
| Quantitative accuracy | Incorrect | Major omissions | Mostly correct | Correct with minor presentation gaps | Reproducible formulas, units, ranges and interpretation |
| Decision quality | No comparison | Straw-man options | Partial matrix | Fair alternatives and trade-offs | Gates first, evidence-backed matrix, sensitivity and reversal conditions |
| Traceability | None | Broken links | Partial chain | Main links work | Bidirectional objective-to-ADR trace passes |
| Reviewability | Unstructured | Hard to audit | Understandable with questions | Clear and consistent | Independent reviewer can reproduce reasoning |
| Governance/lifecycle | No owners/status | Ambiguous approval | Basic ownership | Status/history maintained | Approval, review, supersession and log are coherent |

## I3. Critical errors requiring correction regardless of score

- Requirement embeds a technology choice without a business/functional reason.
- Mandatory requirement has no measurable acceptance criterion and no explicit justification.
- Quantitative result has a material unit or arithmetic error.
- Constraint/assumption/dependency/risk is misclassified in a way that changes feasibility.
- An option that fails a hard gate remains eligible because of its weighted score.
- Criteria or weights were changed after observing totals without transparent re-baselining.
- Recommendation has no evidence or ignores the sensitivity result.
- ADR claims approval without evidence, omits rejected alternatives/consequences, or silently erases decision history.
- High-exposure risk or high-impact assumption has no owner/action/trigger.
- Material contradictions between the requirement register, comparison matrix and ADR are presented as settled.

## I4. Feedback format

For every wrong or partial answer, record:
1. Question ID.
2. Error category (concept, classification, arithmetic, measurement, traceability, decision logic, governance).
3. What was wrong and why.
4. Corrected answer or artefact.
5. What evidence would verify it.
6. Re-attempt date/result.

Re-attempt incorrect questions after a delay and use new examples. Memorising the answer key is not evidence of mastery.

---

# Section J — Final Completion Gate

The module is complete only when the evidence requirements below are met. Finishing this question set alone is insufficient.

## J1. Topic-by-topic gate

### Topic 1 — Stakeholder discovery and business requirements
- [ ] Stakeholder register and elicitation plan reviewed.
- [ ] Business requirements summary has scope, exclusions, success criteria and source stakeholders.
- [ ] No unlabelled solution is presented as a business requirement.
- [ ] Conflict/open-questions log has owners and evidence needs.
- [ ] Validation-session agenda and validation-record template completed (U01).
- [ ] Topic 1 questions answered, corrected, and re-attempted.

### Topic 2 — Functional and non-functional requirements
- [ ] Every requirement has type, priority, source and acceptance criterion.
- [ ] No “must” requirement is unmeasurable without explicit justification.
- [ ] Functional and non-functional statements are distinguished; no solution is smuggled in as a requirement.
- [ ] Requirement traceability matrix connects objectives to requirements and acceptance criteria.
- [ ] Defect review records categories found and fixed.
- [ ] Twenty-statement classification exercise and twelve-requirement exercise reviewed (U02–U03).
- [ ] Topic 2 questions answered, corrected, and re-attempted.

### Topic 3 — Data volume, velocity, variety and growth
- [ ] Estimation worksheet includes formula, units, assumptions, evidence label, range and interpretation for material estimates.
- [ ] Decimal/binary units and bits/bytes are handled consistently.
- [ ] Reviewer independently recomputes at least three figures and obtains the same results.
- [ ] Peaks/bursts, retention, replication, overhead, growth and sensitivity are addressed.
- [ ] Material input confidence is labelled; illustrative values are marked.
- [ ] Three-stream, three-year capacity worksheet and assumptions reviewed (U04).
- [ ] Topic 3 questions answered, corrected, and re-attempted.

### Topic 4 — Latency, throughput, freshness and availability
- [ ] Every target names indicator, percentile where relevant, target, window, scope and measurement method.
- [ ] Vague-to-measurable conversion table exists.
- [ ] Timing budget stages sum correctly to the end-to-end target.
- [ ] Allowed downtime and serial/redundant availability composition are checked against the dependency model.
- [ ] Achievability and trade-offs are stated; targets are not presented as approved without confirmation.
- [ ] 99%, 99.5%, 99.9% and 99.99% monthly/annual downtime table checked (U05).
- [ ] Topic 4 questions answered, corrected, and re-attempted.

### Topic 5 — Constraints, assumptions, dependencies and risks
- [ ] Register contains no unclassified or ownerless item.
- [ ] Constraints are distinguished from preferences; facts from assumptions; dependencies from risks; unknowns are explicit.
- [ ] Every high-exposure risk has an owner, response and trigger.
- [ ] Every high-impact assumption has validation method and date.
- [ ] Dependency map identifies critical path and escalation route.
- [ ] Linked decisions are reopened when a source constraint/assumption changes.
- [ ] Topic 5 questions answered, corrected, and re-attempted.

### Topic 6 — Architecture trade-offs and decision criteria
- [ ] Decision statement names scope, deadline and decision-maker.
- [ ] Every criterion traces to a requirement, constraint or principle.
- [ ] Hard gates are checked before scoring.
- [ ] Every major decision has at least three feasible alternatives including a baseline, or failed options are removed with a reason.
- [ ] Criteria and weights are fixed before scoring and version-dated.
- [ ] Matrix ratings cite evidence; TCO includes build, run, support/people and exit/migration where relevant.
- [ ] Sensitivity analysis tests the two least-certain inputs and reports ranking changes/flip points.
- [ ] Recommendation states assumptions, trade-offs, reversibility and reversal conditions.
- [ ] Technical and business recommendations are both prepared (U06).
- [ ] Topic 6 questions answered, corrected, and re-attempted.

### Topic 7 — Architecture decision records
- [ ] ADR set reviewed; no ADR lacks rejected alternatives or consequences.
- [ ] Every ADR links to requirement, constraint, assumption or risk IDs and relevant objectives/criteria/evidence.
- [ ] Decision log status, owner, date and supersession chain are consistent.
- [ ] One superseding example preserves the prior decision history.
- [ ] Review checklist and review notes are complete and material defects fixed.
- [ ] Conditional decisions name missing evidence, owner, date and fallback.
- [ ] Three-ADR set, decision log, review finding, and proportionality rationale completed (U07).
- [ ] Topic 7 questions answered, corrected, and re-attempted.

## J2. Integrated project gate — D1–D13

- [ ] **D1:** Project scope and business problem statement.
- [ ] **D2:** Stakeholder register.
- [ ] **D3:** Business requirements document.
- [ ] **D4:** Functional and non-functional requirements register.
- [ ] **D5:** Requirement traceability matrix.
- [ ] **D6:** Data volume and growth estimation worksheet.
- [ ] **D7:** Performance and service-target specification.
- [ ] **D8:** Constraints, assumptions, dependencies and risks register.
- [ ] **D9:** Decision criteria and prioritisation method.
- [ ] **D10:** Architecture alternatives comparison.
- [ ] **D11:** Trade-off analysis and recommendation.
- [ ] **D12:** ADRs and decision log.
- [ ] **D13:** Final requirements and architecture decision summary.

All D1–D13 artefacts must be version-dated and use consistent IDs.

- [ ] At least 90% of “must” requirements have measurable acceptance criteria; no requirement embeds a technology choice.
- [ ] Every estimate has units, formula, assumption and evidence label; at least three are independently recomputed.
- [ ] Targets are measurable and timing budget sums correctly.
- [ ] Every risk is classified; high-exposure risks have owners, responses and triggers; high-impact assumptions have validation methods and dates.
- [ ] Each major decision has at least three feasible alternatives including a baseline, compared using criteria fixed before scoring.
- [ ] Sensitivity analysis exists for the two least-certain inputs and says whether ranking changes.
- [ ] Every major decision has an ADR with rejected alternatives, consequences and revisit conditions; conditional decisions name missing evidence.
- [ ] A random trace from three ADRs back to business objectives and from three business objectives forward to ADRs succeeds.
- [ ] Final recommendation states decisions, assumptions, accepted trade-offs, risks and open items, and is readable by a non-specialist in ten minutes.
- [ ] Independent reviewer agrees the evidence supports the conclusions.
- [ ] Reviewer challenge round completed: defend a recommendation against at least two objections using recorded evidence, criteria and sensitivity results.
- [ ] Open questions are logged for the next module, 2D.3.

## J3. Final sign-off record

| Field | Entry |
|---|---|
| Learner | |
| Assessment date/version | |
| Total score / 368 | |
| Beginner → Intermediate gate | Pass / Rework |
| Intermediate → Advanced gate | Pass / Rework |
| Advanced → Industry gate | Pass / Rework |
| Quantitative verification reviewer | |
| Artefact reviewer | |
| Critical errors corrected | |
| Topic gates passed (1–7) | |
| D1–D13 project gate passed | Yes / No |
| Two reviewer challenges answered | Yes / No |
| Remaining open questions | |
| Final decision | Complete / Not complete |
| Reviewer evidence/reference | |

**Completion rule:** mark the module complete only when all seven topic gates, the integrated project gate, corrected/re-attempted practice questions, and the reviewer challenge are complete. A high test score does not override missing artefacts, unsupported claims, or unresolved material contradictions.
