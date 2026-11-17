# Stage 2D — Data Architecture
# Practice Questions and Module Readiness Assessment

**Module:** Enterprise Data Platform and Lakehouse Architecture  
**Scope:** Topics 01–08  
**Assessment type:** formative practice, design assessment, and final-project readiness  
**Source alignment:** `roadmap-Enterprise-Data-Platform-and-Lakehouse-Architecture.md`

> **Source-status note.** The module roadmap states that this file and the eight topic lesson files were empty when the roadmap was written. This is a newly authored assessment aligned to that roadmap; it does not claim to review or preserve pre-existing questions. All organizations, data, target values, costs, and scenarios described as illustrative are teaching assumptions, not universal standards or production recommendations.

---

## 1. Purpose and how to use this file

This assessment checks whether you can explain, apply, troubleshoot, and defend enterprise data-platform architecture decisions—not merely recall terminology. It complements, but does not replace, the eight lesson files, their deliverables and completion gates, or the final `Projects/07-enterprise-lakehouse-reference-architecture.md` project.

### 1.1 Learning outcomes

After completing the question set and design exercises, you should be able to:

1. Describe platform capabilities independently of vendor products and draw a logical reference architecture.
2. Trace data through ingestion, storage, processing, and consumption zones, including validation, quarantine, replay, access, and retention boundaries.
3. Explain bronze, silver, and gold refinement layers; define promotion tests; and distinguish a layer from a consumer-facing data product.
4. Place services in compute, storage, and control planes and reason about their interactions, failure modes, and cost implications.
5. Distinguish catalog, metastore, and other platform metadata; define owners, sources, workflows, and drift detection.
6. Design guarded self-service journeys and classify controls as enforced, defaulted, or recommended.
7. Select tenant boundaries, state residual risks, and design quotas, priorities, and cost allocation.
8. Define measurable service indicators and objectives, compose dependency availability carefully, and run the platform as a product with users, outcomes, support, and feedback.
9. Integrate these decisions into a vendor-neutral architecture and justify alternatives through architecture decision records (ADRs).

### 1.2 Prerequisites

Study the module roadmap and the relevant lesson before attempting each section. Topic 01 specifically assumes P1, P5, and P6 from the module roadmap, plus the vocabulary for reference models, reference architectures, and blueprints. Later topics build sequentially on earlier topics and their stated prerequisites. The module also assumes familiarity with data ownership and architecture principles, measurable requirements, constraints and assumptions, governance, and basic reliability concepts. Where a question supplies a fictional fact or numeric assumption, use it rather than silently introducing a new one.

### 1.3 Recommended assessment sequence

| When | Attempt | Method | Purpose |
|---|---|---|---|
| After Topic 01 | T01 questions | Closed-book, then explain missed answers | Capability vocabulary and logical diagram |
| After Topic 02 | T02 questions | Draw flows and boundary rules | Zones, reject paths, replay |
| After Topic 03 | T03 questions | Specify promotion and a product | Layers, quality, product contracts |
| After Topic 04 | T04 questions | Matrix and failure trace | Planes, dependencies, cost |
| After Topics 01–04 | Checkpoint A | Timed, mixed questions | Test the structural core |
| After Topic 05 | T05 questions | Metadata model and workflow | Catalog/metastore/metadata distinctions |
| After Topic 06 | T06 questions | Journey and guardrail classification | Self-service and developer experience |
| After Topic 07 | T07 questions | Boundary table and threat analysis | Isolation, quotas, residual risks |
| After Topic 08 | T08 questions | SLI/SLO table and product canvas | Promises, support, outcome measures |
| After Topics 05–08 | Checkpoint B | Timed, mixed questions | Test the operating model |
| Before final project | Integrated assessment + exercises | Design, defend, revise | End-to-end readiness |
| After project review | Reattempt missed questions | Closed-book | Confirm gaps have been closed |

### 1.4 Rules for answering

- **Multiple choice:** choose one answer unless the question explicitly says “select all that apply.” Do not assume unstated vendor behaviour.
- **Short answer:** answer the question asked, then give a reason or example. A concise, correct explanation is better than a list of unrelated terms.
- **Design questions:** there may be several valid designs. State assumptions, requirements, boundaries, ownership, alternatives, trade-offs, and residual risks. The rubric—not one prescribed diagram—determines credit.
- **Calculations:** show formula, units, assumptions, and interpretation. Distinguish a mathematical illustration from a contractual promise.
- **Evidence:** preserve diagrams, tables, ADRs, test results, and reviewer comments as evidence for the corresponding topic gate.

### 1.5 Gap log

Copy one row for each missed or partly correct question. A gap is not closed merely because the answer has been reread; it is closed when the learner can answer again and demonstrate the underlying skill.

| Question ID | Topic | Error or misconception | Corrective lesson/exercise | Reattempt date | Result / evidence |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

**Recommended review cadence:** attempt once after the lesson; reattempt incorrect answers after 2–4 days without looking at the key; reattempt persistent gaps after 7–10 days and redo the topic exercise if the same misconception appears twice. The intervals are a study recommendation, not a universal learning-science guarantee. Keep the gap log until all material gaps are resolved.

---

## 2. Topic-to-question map

| Topic | Question IDs | Skills tested | Related completion gate / deliverable |
|---|---|---|---|
| 01 — Capabilities and logical reference architecture | T01-F1–F3, T01-A1–A3, T01-D1 | Capability/component/interface/data-flow distinctions; logical vs physical; cross-cutting controls; centralized/federated/hybrid trade-offs; ownership and end-to-end trace | Capability inventory, logical diagram, trace, scope ADR; diagram reviewed and unexplained hops removed |
| 02 — Ingestion, storage, processing, consumption zones | T02-F1–F3, T02-A1–A3, T02-D1 | Zone purpose, movement rules, batch/stream, quarantine, replay, access and retention | Zone table and flow diagrams; every source has reject/replay path and each boundary has a rule |
| 03 — Bronze, silver, gold, data products | T03-F1–F3, T03-A1–A3, T03-D1 | Layer purpose, promotion tests, layer vs product, consumer boundaries | Layer table, promotion criteria, product specification, layer-model ADR |
| 04 — Compute, storage, control planes | T04-F1–F3, T04-A1–A3, T04-D1 | Plane responsibilities, interactions, dependency failures, coupling and cost | Plane matrix, read/write/job interaction diagram, cost/failure analysis, separation ADR |
| 05 — Catalogs, metastores, metadata | T05-F1–F3, T05-A1–A3, T05-D1 | Metadata types, discoverability, lineage, owners, access, drift | Metadata model, catalog topology/workflow, quality indicators, topology ADR |
| 06 — Self-service and developer experience | T06-F1–F3, T06-A1–A3, T06-D1 | User journey, golden paths, enforceable guardrails, exceptions, DX metrics | Journey map, self-service workflow, control classification, DX measures, autonomy ADR |
| 07 — Isolation and tenant boundaries | T07-F1–F3, T07-A1–A3, T07-D1 | Isolation dimensions, logical/physical limits, noisy neighbour, quotas, cost | Tenant boundary/responsibility model, residual-risk table, quota/priority policy, allocation method, isolation ADR |
| 08 — Service levels and product thinking | T08-F1–F3, T08-A1–A3, T08-D1 | Output vs outcome, measurable SLI/SLO, dependency chain, support, product discovery | Persona/outcome list, service catalogue and SLI/SLO table, support model, product canvas and feedback plan |
| Cross-topic | CA-1–CA-5, CB-1–CB-5, INT-1–INT-8, EX-1–EX-5 | Integration, prioritization, fault analysis, architecture defense | Integrated design exercise, cross-topic deliverables, at least five justified ADRs for module completion |


### 2.1 Question-level traceability matrix

The assessment contains **56 topic-level questions** (seven per topic), **10 checkpoint questions**, **8 integrated-case questions**, and **5 supplementary practical exercises**. Skill labels describe the dominant cognitive task; a complex prompt may test more than one skill. “Roadmap” references below refer to the corresponding Topic 5.x section, the integrated design exercise in §7.6, or practice-validation guidance in §8.

| Question ID | Topic mapping | Skill level | Learning objective tested | Evidence of alignment (roadmap and available lesson) |
|---|---|---|---|---|
| T01-F1 | 01 | Recall | Recognize a logical reference architecture and distinguish it from a physical/vendor deployment. | `01-platform-capabilities-and-logical-reference-architecture.md` §§3–7; Roadmap §5.1.2; lesson §§3.3–3.4, 5 |
| T01-F2 | 01 | Explain | Define capability, component, interface, data flow, and data product; distinguish the concepts. | `01-platform-capabilities-and-logical-reference-architecture.md` §§3–7; Roadmap §5.1.2; lesson §§3.1–3.4 |
| T01-F3 | 01 | Analyze | Explain cross-cutting controls and consequences of missing ownership/enforcement. | `01-platform-capabilities-and-logical-reference-architecture.md` §§3–7; Roadmap §§5.1.5–5.1.6; lesson §§4.5–4.8, 6–7 |
| T01-A1 | 01 | Design | Produce a vendor-neutral capability diagram with flows, controls, and owners. | `01-platform-capabilities-and-logical-reference-architecture.md` §§3–7; Roadmap §§5.1.6–5.1.9; lesson §§5–7 |
| T01-A2 | 01 | Analyze | Diagnose missing capability boundaries, ownership, controls, and unexplained flow hops. | `01-platform-capabilities-and-logical-reference-architecture.md` §§3–7; Roadmap §§5.1.8–5.1.10; lesson §§5–8 |
| T01-A3 | 01 | Apply | Translate product-specific components into logical capabilities and ownership questions. | `01-platform-capabilities-and-logical-reference-architecture.md` §§3–7; Roadmap §§5.1.4–5.1.6; lesson §§3–6 |
| T01-D1 | 01 | Evaluate / Design | Compare centralized/federated/hybrid patterns and defend a scope/ownership ADR. | `01-platform-capabilities-and-logical-reference-architecture.md` §§3–7; Roadmap §§5.1.6–5.1.9; lesson §§8–11 |
| T02-F1 | 02 | Apply | Choose a safe response to malformed/duplicate source records. | `02-ingestion-storage-processing-and-consumption-zones.md` §§2–9; Roadmap §§5.2.4–5.2.6; lesson §§6.1–6.3 |
| T02-F2 | 02 | Explain | Define zone purposes and adjacent-zone boundary rules. | `02-ingestion-storage-processing-and-consumption-zones.md` §§2–9; Roadmap §§5.2.4–5.2.5; lesson §§2.1–2.3, 4 |
| T02-F3 | 02 | Analyze | Explain how batch and streaming differ while sharing platform controls and consumers. | `02-ingestion-storage-processing-and-consumption-zones.md` §§2–9; Roadmap §§5.2.4–5.2.6; lesson §§5.1–5.4 |
| T02-A1 | 02 | Analyze | Diagnose false success, lost source evidence, missing quarantine, and unsafe retry. | `02-ingestion-storage-processing-and-consumption-zones.md` §§2–9; Roadmap §§5.2.5–5.2.8; lesson §§6–7 |
| T02-A2 | 02 | Design | Specify zone purpose, interfaces, owners, access, retention, validation, and recovery. | `02-ingestion-storage-processing-and-consumption-zones.md` §§2–9; Roadmap §§5.2.7–5.2.9; lesson §§4–9 |
| T02-A3 | 02 | Analyze | Assess sensitivity, lineage, and operational risks of broad raw-data access. | `02-ingestion-storage-processing-and-consumption-zones.md` §§2–9; Roadmap §§5.2.5–5.2.8; lesson §§6.3, 9.4 |
| T02-D1 | 02 | Evaluate / Design | Defend zone granularity and movement, promotion, access, retention, and replay rules. | `02-ingestion-storage-processing-and-consumption-zones.md` §§2–9; Roadmap §§5.2.6–5.2.9; lesson §§8–10 |
| T03-F1 | 03 | Recall / Explain | Distinguish refinement layers from a consumer-facing data product. | `03-bronze-silver-gold-and-data-product-boundaries.md` §§3–10; Roadmap §§5.3.2, 5.3.4; lesson §§3, 8.3 |
| T03-F2 | 03 | Explain | Describe typical layer purposes and when the model should be adapted. | `03-bronze-silver-gold-and-data-product-boundaries.md` §§3–10; Roadmap §§5.3.4–5.3.6; lesson §§2, 5, 10 |
| T03-F3 | 03 | Analyze | Explain risks of consumer dependence on internal bronze representations. | `03-bronze-silver-gold-and-data-product-boundaries.md` §§3–10; Roadmap §§5.3.5, 5.3.10; lesson §§7–8 |
| T03-A1 | 03 | Apply / Design | Define testable promotion and product-readiness criteria with ownership/failure handling. | `03-bronze-silver-gold-and-data-product-boundaries.md` §§3–10; Roadmap §§5.3.6–5.3.9; lesson §§6, 11 |
| T03-A2 | 03 | Analyze | Compare gold-layer status with product ownership, contract, support, and lifecycle. | `03-bronze-silver-gold-and-data-product-boundaries.md` §§3–10; Roadmap §§5.3.4, 5.3.6, 5.3.9; lesson §§3, 8 |
| T03-A3 | 03 | Analyze | Identify missing obligations for a purported gold reporting product. | `03-bronze-silver-gold-and-data-product-boundaries.md` §§3–10; Roadmap §§5.3.8–5.3.10; lesson §§8–9, 11 |
| T03-D1 | 03 | Evaluate / Design | Adapt refinement stages for latency requirements while protecting stable consumer contracts. | `03-bronze-silver-gold-and-data-product-boundaries.md` §§3–10; Roadmap §§5.3.6–5.3.9; lesson §§6–10 |
| T04-F1 | 04 | Recall / Explain | Identify compute, storage, and control-plane responsibilities without assuming physical separation. | `04-compute-storage-and-control-plane-separation.md` §§2–10; Roadmap §§5.4.2, 5.4.4; lesson §§2–3 |
| T04-F2 | 04 | Apply | Trace a query through compute, storage, and control dependencies. | `04-compute-storage-and-control-plane-separation.md` §§2–10; Roadmap §§5.4.4–5.4.6; lesson §§4, 6 |
| T04-F3 | 04 | Analyze | Compare a benefit and cost of separation and a shared control plane. | `04-compute-storage-and-control-plane-separation.md` §§2–10; Roadmap §§5.4.5, 5.4.8; lesson §§7, 9 |
| T04-A1 | 04 | Analyze | Explain catalog/identity outage impact despite durable stored data. | `04-compute-storage-and-control-plane-separation.md` §§2–10; Roadmap §§5.4.7–5.4.8; lesson §§7.5, 8, 10 |
| T04-A2 | 04 | Analyze | Identify cost and utilization variables for dedicated versus elastic compute. | `04-compute-storage-and-control-plane-separation.md` §§2–10; Roadmap §§5.4.6–5.4.9; lesson §§7, 9–10 |
| T04-A3 | 04 | Apply / Classify | Map responsibilities to planes and explain implementation-dependent overlap. | `04-compute-storage-and-control-plane-separation.md` §§2–10; Roadmap §§5.4.4–5.4.6; lesson §§2, 5 |
| T04-D1 | 04 | Evaluate / Design | Choose coupled/separated architecture using workload, dependency, cost, and failure evidence. | `04-compute-storage-and-control-plane-separation.md` §§2–10; Roadmap §§5.4.8–5.4.12; lesson §§8–12 |
| T05-F1 | 05 | Recall / Explain | Distinguish catalog, metastore, and broader metadata responsibilities. | `05-catalogs-metastores-and-platform-metadata.md` §§2–10; Roadmap §§5.5.1–5.5.4; lesson §§2–3 |
| T05-F2 | 05 | Apply | Classify metadata fields and identify plausible authoritative sources/maintainers. | `05-catalogs-metastores-and-platform-metadata.md` §§2–10; Roadmap §§5.5.4–5.5.5; lesson §§2, 5 |
| T05-F3 | 05 | Explain | Explain limits of automated metadata harvesting. | `05-catalogs-metastores-and-platform-metadata.md` §§2–10; Roadmap §§5.5.5–5.5.8; lesson §§5–6 |
| T05-A1 | 05 | Design | Define registration, review, publication, change, and retirement workflow. | `05-catalogs-metastores-and-platform-metadata.md` §§2–10; Roadmap §§5.5.5–5.5.9; lesson §§5–7 |
| T05-A2 | 05 | Analyze | Diagnose stale ownership, missing lineage, and sensitive metadata exposure. | `05-catalogs-metastores-and-platform-metadata.md` §§2–10; Roadmap §§5.5.6–5.5.8; lesson §§6, 8–9 |
| T05-A3 | 05 | Apply / Design | Define measurable metadata-quality indicators and breach actions. | `05-catalogs-metastores-and-platform-metadata.md` §§2–10; Roadmap §§5.5.6–5.5.9; lesson §6.3 |
| T05-D1 | 05 | Evaluate / Design | Choose metadata topology with authority, synchronization, security, and failure trade-offs. | `05-catalogs-metastores-and-platform-metadata.md` §§2–10; Roadmap §§5.5.6–5.5.9; lesson §§4, 8–12 |
| T06-F1 | 06 | Apply | Identify an actually enforced guardrail rather than documentation or a UI-only warning. | `06-self-service-platforms-and-developer-experience.md` §§5–15; Roadmap §§5.6.4–5.6.6; lesson §§7–9, 14 |
| T06-F2 | 06 | Explain | Define golden path and explain governed self-service. | `06-self-service-platforms-and-developer-experience.md` §§5–15; Roadmap §§5.6.4–5.6.5; lesson §§4, 9 |
| T06-F3 | 06 | Apply / Classify | Classify enforced, default-with-exception, and recommended controls. | `06-self-service-platforms-and-developer-experience.md` §§5–15; Roadmap §§5.6.5–5.6.9; lesson §§8–9, 14 |
| T06-A1 | 06 | Design | Map discovery-to-use/support journey with friction, owners, automation, and evidence. | `06-self-service-platforms-and-developer-experience.md` §§5–15; Roadmap §§5.6.5–5.6.9; lesson §§5–7, 10 |
| T06-A2 | 06 | Design | Specify a scoped, auditable, expiring policy exception. | `06-self-service-platforms-and-developer-experience.md` §§5–15; Roadmap §§5.6.6–5.6.9; lesson §§8–9, 14 |
| T06-A3 | 06 | Evaluate | Choose measurable DX indicators and explain segmentation/confounding. | `06-self-service-platforms-and-developer-experience.md` §§5–15; Roadmap §§5.6.7–5.6.9; lesson §§10–12 |
| T06-D1 | 06 | Evaluate / Design | Design a golden-path workflow with controls, exception/template lifecycle, and adoption measures. | `06-self-service-platforms-and-developer-experience.md` §§5–15; Roadmap §§5.6.5–5.6.12; lesson §§6–15 |
| T07-F1 | 07 | Explain | Recognize that namespace/account labels do not guarantee complete isolation. | `07-multi-team-isolation-and-tenant-boundaries.md` §§4–12; Roadmap §§5.7.2–5.7.5; lesson §§4–7, 11 |
| T07-F2 | 07 | Explain | Define tenant/isolation terms and separate data from workload/failure isolation. | `07-multi-team-isolation-and-tenant-boundaries.md` §§4–12; Roadmap §§5.7.2–5.7.5; lesson §§4–5, 11 |
| T07-F3 | 07 | Apply / Classify | Map cross-team read, contention, shared credentials, and cost visibility to control gaps. | `07-multi-team-isolation-and-tenant-boundaries.md` §§4–12; Roadmap §§5.7.4–5.7.5; lesson §§5, 8–9, 12 |
| T07-A1 | 07 | Design | Choose shared/isolated boundaries across data, compute, identity, metadata, keys, logs, and cost. | `07-multi-team-isolation-and-tenant-boundaries.md` §§4–12; Roadmap §§5.7.5–5.7.9; lesson §§5–7, 12 |
| T07-A2 | 07 | Analyze | Threat-model cross-tenant access, identity misuse, compromise, admin misuse, contention, and metadata leakage. | `07-multi-team-isolation-and-tenant-boundaries.md` §§4–12; Roadmap §§5.7.5–5.7.9; lesson §§8–10 |
| T07-A3 | 07 | Apply / Evaluate | Calculate burst capacity and justify a fair allocation policy under contention. | `07-multi-team-isolation-and-tenant-boundaries.md` §§4–12; Roadmap §§5.7.6–5.7.9; lesson §12.2 |
| T07-D1 | 07 | Evaluate / Design | Choose isolation strength and justify security, cost, operations, recovery, and residual risk. | `07-multi-team-isolation-and-tenant-boundaries.md` §§4–12; Roadmap §§5.7.6–5.7.12; lesson §§7–13 |
| T08-F1 | 08 | Recall / Explain | Distinguish SLI, SLO, and SLA. | `08-platform-service-levels-and-product-thinking.md` §§4–14; Roadmap §§5.8.2–5.8.5; lesson §§4.2–4.3 |
| T08-F2 | 08 | Explain | Distinguish platform service/data product and output/outcome metrics. | `08-platform-service-levels-and-product-thinking.md` §§4–14; Roadmap §§5.8.4–5.8.5; lesson §§4.4–5.1 |
| T08-F3 | 08 | Analyze / Evaluate | Explain why service targets depend on criticality, dependencies, support, and cost. | `08-platform-service-levels-and-product-thinking.md` §§4–14; Roadmap §§5.8.5–5.8.8; lesson §§7–9, 11 |
| T08-A1 | 08 | Apply / Design | Specify a measurable SLI/SLO with event definition, denominator, window, target basis, owner, action, and evidence. | `08-platform-service-levels-and-product-thinking.md` §§4–14; Roadmap §§5.8.5–5.8.9; lesson §§6–7 |
| T08-A2 | 08 | Apply | Calculate serial dependency availability and explain model limitations. | `08-platform-service-levels-and-product-thinking.md` §§4–14; Roadmap §§5.8.5–5.8.8; lesson §8 |
| T08-A3 | 08 | Analyze / Evaluate | Plan product discovery, adoption/outcome measures, prioritization, and proportionate controls. | `08-platform-service-levels-and-product-thinking.md` §§4–14; Roadmap §§5.8.4–5.8.9; lesson §§5, 10–12 |
| T08-D1 | 08 | Evaluate / Design | Create a service charter/product canvas with measurable promises, support, cost, feedback, and risk. | `08-platform-service-levels-and-product-thinking.md` §§4–14; Roadmap §§5.8.7–5.8.12; lesson §§6, 9–14 |
| CA-1 | 01–04 | Apply / Analyze | Correct a vendor-centric logical architecture by adding capability boundaries, owners, and cross-cutting controls. | Roadmap Topics 01–04; lesson 01 §§3–7; checkpoint A objective. |
| CA-2 | 01–03 | Design | Trace partner-file movement across zones to a supported product with controls and owners. | Roadmap Topics 01–03; lessons 02 §§3–7 and 03 §§4–8. |
| CA-3 | 02–03 | Analyze | Diagnose zone, evidence-retention, access, and unsupported-product defects. | Roadmap Topics 02–03; lessons 02 §§6–9 and 03 §§6–8. |
| CA-4 | 04 | Analyze | Explain a metastore/control dependency failure and compare recovery/degraded modes. | Roadmap Topic 04; lesson 04 §§6–10. |
| CA-5 | 02–03 | Design | Specify refinement stages, promotion tests, and a Finance product contract. | Roadmap Topic 03; lesson 03 §§5–11. |
| CB-1 | 05 | Analyze | Assess harvested metadata against authority, ownership, classification, and semantic freshness. | Roadmap Topic 05; lesson 05 §§5–8. |
| CB-2 | 06 | Design | Design a self-service path and justify control classes and exception handling. | Roadmap Topic 06; lesson 06 §§6–15. |
| CB-3 | 07 | Evaluate / Design | Select isolation boundaries for sensitive data and document residual risks. | Roadmap Topic 07; lesson 07 §§5–11. |
| CB-4 | 08 + 03 | Apply / Design | Separate platform SLO from product freshness promise with measurable boundaries and owners. | Roadmap Topic 08; lessons 08 §§7–9 and 03 §§8–9. |
| CB-5 | 06–08 | Evaluate / Design | Respond to low adoption, support load, and rising cost with outcome metrics and operating controls. | Roadmap Topics 06 and 08; lessons 06 §§10–13 and 08 §§5–12. |
| INT-1 | 01, 06, 07 | Evaluate / Design | Allocate central, domain, and joint ownership based on capability and risk. | Roadmap integrated exercise §7.6 and Topics 01, 06, 07; lessons 01 §§6–8, 06 §10, 07 §12. |
| INT-2 | 02, 03, 05 | Apply / Design | Trace a payment record through controls, refinement, metadata, and product publication. | Roadmap integrated exercise §7.6; lessons 02 §§5–7, 03 §§6–8, 05 §§6–7. |
| INT-3 | 03, 08 | Design | Specify a supported product contract and its ownership, quality/freshness, support, and change policy. | Roadmap Topics 03 and 08; lessons 03 §8 and 08 §§4–9. |
| INT-4 | 04, 05 | Analyze | Analyze catalog unavailability effects on discovery, authorization, and query execution. | Roadmap Topics 04–05; lessons 04 §§7–8 and 05 §§3, 7, 9. |
| INT-5 | 05 | Evaluate / Design | Choose authoritative metadata sources and resolve conflicts/drift. | Roadmap Topic 05; lesson 05 §§5–8. |
| INT-6 | 06, 07 | Design | Design a governed self-service journey with risk-based controls and exceptions. | Roadmap Topics 06–07; lessons 06 §§6–9 and 07 §§9–10. |
| INT-7 | 07 | Evaluate / Design | Select isolation boundaries and map threats, controls, evidence, and residual risk. | Roadmap integrated exercise §7.6 and Topic 07; lesson 07 §§7–11. |
| INT-8 | 08, 03, 04 | Design / Evaluate | Define platform and product promises, measurement boundaries, dependencies, and communication. | Roadmap integrated exercise §7.6; lessons 08 §§7–9 and 03 §8. |
| EX-1 | 01 | Design | Draw a logical reference architecture and produce capability inventory and trace. | Roadmap §8.6 supplementary exercise 1; lesson 01 §§5–7. |
| EX-2 | 01–08 | Analyze | Diagnose cross-topic architecture, security, metadata, cost, and service-level defects. | Roadmap §8.6 supplementary exercise 2; lessons 01–08. |
| EX-3 | 07 | Evaluate / Design | Write an isolation ADR comparing shared and isolated sensitive-domain designs. | Roadmap §8.6 supplementary exercise 3; lesson 07 §§7–13. |
| EX-4 | 04, 08 | Apply | Calculate serial dependency availability and interpret assumptions. | Roadmap §8.6 supplementary exercise 4; lesson 08 §8. |
| EX-5 | 05, 07 | Evaluate / Design | Defend catalog/tenant controls with evidence, containment, and residual risks. | Roadmap §8.6 supplementary exercise 5; lesson 05 §§3, 7–9 and lesson 07 §§8–11. |

---

# Part I — Topic-level practice

## 3. Topic 01 — Platform capabilities and logical reference architecture

### Foundation

**T01-F1 — MCQ (one answer).** Which statement best describes a *logical reference architecture*?

A. A deployment diagram listing exact products, versions, and instance sizes.  
B. A vendor-neutral view of platform capabilities and their relationships.  
C. A list of all data tables currently in production.  
D. A contractual service-level agreement for each platform component.

**T01-F2 — Short answer.** Define *capability*, *component*, *interface*, and *data flow*. Distinguish a capability from a component and give one example of each. Briefly distinguish both from a consumer-facing data product.

**T01-F3 — Explain why.** Why should identity/access, encryption, audit, lineage, observability, and cost attribution be considered across the architecture rather than only inside one ingestion or storage box? State one risk if any one of these concerns has no clear owner or enforcement point.

### Application

**T01-A1 — Diagram-design prompt.** A fictional enterprise receives operational database extracts, partner files, and event streams. Analysts use governed reporting datasets; data scientists use approved features and curated datasets. Draw a logical reference architecture with source, ingestion, storage/refinement, processing, consumption, catalog/metadata, identity/policy, encryption, audit/lineage, observability/cost attribution, orchestration, and ownership. Label interfaces, data flows, and cross-cutting control flows. Do not use vendor product names.

**T01-A2 — Scenario diagnosis.** An architecture diagram consists entirely of product logos and arrows. No component has an owner, no audit/identity service is shown, and one arrow jumps from “source” to “dashboard.” Identify at least four defects and describe how to repair them.

**T01-A3 — Short answer.** A capability inventory contains “Spark cluster,” “cloud object store,” and “dashboard tool.” Rewrite these as logical capability statements and identify one ownership question for each.

### Advanced / design

**T01-D1 — ADR prompt.** Compare centralized, federated, and hybrid platform operating/architecture patterns. Decide which capabilities belong in a shared enterprise platform and which may remain domain-owned. State assumptions, criteria (including skills, cost, time to value, governance, scale, and failure domains), alternatives, build/buy/defer choices, rationale, cross-cutting capabilities, ownership gaps, residual risks, and review triggers. Provide a one-record end-to-end trace with no unexplained hop. Do not assume one pattern is universally best.

---

## 4. Topic 02 — Ingestion, storage, processing, and consumption zones

### Foundation

**T02-F1 — MCQ (one answer).** A source file arrives with malformed rows and duplicate records. What is the best general design response?

A. Silently discard malformed rows and continue.  
B. Publish the file directly to consumers and ask them to clean it.  
C. Preserve source fidelity where required, validate at the boundary, quarantine rejects with reason/evidence, and define replay or correction.  
D. Treat every malformed row as proof the entire platform is unavailable.

**T02-F2 — Short answer.** Define the purpose of ingestion, storage, processing, and consumption zones. State one boundary rule for any two adjacent zones.

**T02-F3 — Compare/contrast.** Explain how batch ingestion and streaming ingestion can use different transport patterns but still share governance, metadata, storage, and consumption concepts.

### Application

**T02-A1 — Failure analysis.** A pipeline marks a source as “successful” after downloading a file, but schema validation later fails. The team has no quarantine location and retries overwrite the original file. Identify the failure-path defects and propose a recoverable design.

**T02-A2 — Design table.** For a daily payment file, specify each zone's purpose, input/output, owner, access policy, retention consideration, validation, and failure/replay path. Label any assumptions.

**T02-A3 — Explain why.** Why can unrestricted access to raw/landing data be inappropriate even when those data are “not yet cleaned”? Include sensitivity, lineage, and operational considerations.

### Advanced / design

**T02-D1 — Zone-granularity ADR.** Decide whether a platform needs separate landing, quarantine, raw/bronze, curated/silver, serving/gold, and consumption boundaries for a given workload. Justify what must be separate versus what can be logical labels, and state movement, promotion, access, retention, and replay rules.

---

## 5. Topic 03 — Bronze, silver, gold, and data-product boundaries

### Foundation

**T03-F1 — MCQ (one answer).** Which statement is most accurate?

A. Every gold table is automatically a data product.  
B. Bronze, silver, and gold are refinement-stage concepts; a data product additionally needs an owned consumer interface, documentation/contract, and defined quality or service expectations appropriate to its use.  
C. A data product must always contain exactly three physical copies.  
D. A silver table can never be consumed by another team under any circumstances.

**T03-F2 — Short answer.** Describe the typical purpose of bronze, silver, and gold layers. State why the model may be adapted rather than applied mechanically to every dataset.

**T03-F3 — Explain why.** What could go wrong if consumer reports query internal bronze tables directly?

### Application

**T03-A1 — Promotion criteria.** Define at least four testable criteria for promoting a fictional customer-payment dataset from raw/bronze to silver and at least three additional criteria for a curated reporting product. Include owner and failure handling.

**T03-A2 — Compare/contrast.** Compare a gold table with a data product using ownership, consumers, interface/contract, metadata, quality, change management, and support.

**T03-A3 — Scenario diagnosis.** A “gold” revenue table has no declared grain, owner, definition of revenue, freshness expectation, or compatibility policy. A dashboard depends on it. List the missing product obligations and the minimum remediation before treating it as a supported product.

### Advanced / design

**T03-D1 — Layer-model ADR.** For an event stream with a strict latency requirement, propose a refinement and product model. Explain whether every bronze/silver/gold step is necessary, how quality gates work, and how consumers are prevented from depending on unstable internal representations.

---

## 6. Topic 04 — Compute, storage, and control-plane separation

### Foundation

**T04-F1 — MCQ (one answer).** Which option best captures the three planes?

A. Compute performs work; storage retains data; the control plane manages, coordinates, or governs resources and operations.  
B. Compute stores metadata; storage makes policy decisions; the control plane is only the billing screen.  
C. The planes are three mandatory physical servers.  
D. Separating the planes guarantees lower cost and no failures.

**T04-F2 — Short answer.** Trace a query from user request to result. Name at least one compute, storage, and control-plane interaction.

**T04-F3 — Compare/contrast.** Give one benefit and one cost or risk of separating compute from storage, and one benefit and risk of relying on a shared control plane.

### Application

**T04-A1 — Failure analysis.** Stored data remain intact, but the catalog or identity service is unavailable and new jobs cannot resolve tables or obtain authorization. Explain why this can still be a platform outage and list mitigations or degraded-mode decisions to evaluate.

**T04-A2 — Cost reasoning.** A dedicated compute pool improves workload predictability but is idle much of the week. Identify the variables needed to compare it with shared elastic compute. Do not assume separation always reduces total cost.

**T04-A3 — Matrix.** Assign each concern to its primary plane or mark it cross-cutting: query execution, durable object/table data, table definitions, scheduling, policy decisions, audit events, compute autoscaling. Explain any overlap.

### Advanced / design

**T04-D1 — Separation ADR.** Compare a coupled engine/storage design with independently scalable compute and storage for a mixed BI and machine-learning workload. Include read/write/job interaction diagrams, performance and failure domains, data-transfer cost, utilization, control-plane dependency, operational ownership, and review triggers.

---

## 7. Topic 05 — Catalogs, metastores, and platform metadata

### Foundation

**T05-F1 — MCQ (one answer).** Which statement best distinguishes a catalog from a metastore and broader platform metadata?

A. They are always interchangeable names for one database.  
B. A catalog supports discovery and navigation; a metastore commonly holds technical object/table definitions used by engines; broader metadata also includes ownership, classification, lineage, policy, quality, and operational context. Exact product boundaries vary.  
C. A metastore is only a dashboard for business users.  
D. Metadata is only the file format and column types.

**T05-F2 — Short answer.** For a customer-payment data product, name one technical, business, governance, lineage, quality, and operational metadata field. Assign a plausible source or maintainer for each.

**T05-F3 — Explain why.** Why is automatically harvested metadata not necessarily correct or complete?

### Application

**T05-A1 — Workflow design.** Define the metadata registration workflow for a newly created data product: required fields, owners, automated collection, human review, access controls, publication, and change/retirement updates.

**T05-A2 — Troubleshooting.** A catalog shows a dataset as owned by a team that disbanded six months ago; lineage stops at a transformation job; a sensitive column description is visible to users who cannot read the data. Identify metadata quality and security issues and corrective actions.

**T05-A3 — Indicator design.** Define three measurable metadata quality indicators. For each, state numerator/denominator or measurement method, owner, and what action follows a breach.

### Advanced / design

**T05-D1 — Catalog-topology ADR.** Choose a centralized, federated, or hybrid catalog/metadata topology for multiple domains. State discovery needs, authority/source-of-truth rules, synchronization and drift handling, access to sensitive metadata, lineage coverage, failure behaviour, and operational ownership.

---

## 8. Topic 06 — Self-service platforms and developer experience

### Foundation

**T06-F1 — MCQ (one answer).** Which is the strongest example of an enforceable guardrail?

A. A warning in documentation saying “please remember security.”  
B. A UI label saying a dataset is sensitive, with no access enforcement.  
C. Provisioning automation rejects a request whose requested access exceeds the approved policy and records the decision.  
D. A quarterly slide deck describing ideal practices.

**T06-F2 — Short answer.** Define a golden path/paved road and explain how it can reduce friction without removing governance.

**T06-F3 — Classify controls.** Classify these as enforced, default, or recommended, and justify: (i) platform blocks public exposure for restricted data; (ii) new pipelines inherit logging by default but can override only with an approved exception; (iii) teams are advised to use a standard naming pattern that is not automatically checked.

### Application

**T06-A1 — Journey map.** A new analyst needs a governed dataset. Map discovery → request → approval or policy decision → access provisioning → validation → use → support. Identify friction points, automation opportunities, owners, and evidence.

**T06-A2 — Exception design.** A team requests an exception to a default retention policy. Define an auditable exception process with justification, risk, approver, scope, expiry/review, compensating controls, monitoring, and revocation.

**T06-A3 — DX metrics.** Propose four measurable developer-experience indicators, including a definition, segmentation, and a possible misleading interpretation for each. Include at least one outcome metric rather than only an activity count.

### Advanced / design

**T06-D1 — Autonomy ADR.** Design a self-service pipeline creation workflow. Identify what is automated, what is blocked, what warns, what requires human approval, and how templates are versioned and retired. Explain how you will measure adoption and friction without rewarding unsafe shortcuts.

---

## 9. Topic 07 — Multi-team isolation and tenant boundaries

### Foundation

**T07-F1 — MCQ (one answer).** Which statement is correct?

A. A separate schema automatically provides strong isolation against every threat.  
B. A separate cloud account automatically removes the need for least privilege or audit.  
C. Isolation is multidimensional; a namespace can help with logical separation, but effective boundaries depend on enforcement, identities, permissions, shared services, and threat model.  
D. Physical separation prevents administrator misuse by definition.

**T07-F2 — Short answer.** Define tenant, tenant boundary, logical isolation, physical isolation, and noisy neighbour. Explain why data isolation alone may not provide workload or failure isolation.

**T07-F3 — Identify dimensions.** A team can read another team's data; a large ML job slows reporting; shared credentials are used by multiple teams; one tenant's usage is not visible in billing. Name the main isolation dimension or control gap for each.

### Application

**T07-A1 — Boundary table.** For six fictional teams—Retail Analytics, Risk, Fraud, Finance, Marketing, and Data Science—choose shared versus isolated resources for data, compute, identity/admin, metadata, keys, logs, and cost. State sensitivity assumptions and residual risks.

**T07-A2 — Threat analysis.** For each case, identify threat actor or trigger, asset, boundary crossed, preventive control, detective evidence, corrective response, owner, and residual risk: accidental cross-team read; misconfigured service identity; compromised workload; administrator misuse; resource starvation; metadata leakage.

**T07-A3 — Capacity and cost.** An illustrative shared pool has 100 compute units. Five tenants each receive a guaranteed 15 units. Calculate the remaining burst pool and define a fair rule if three tenants simultaneously request 20 additional units each. State the fairness and service-level trade-off.

### Advanced / design

**T07-D1 — Isolation ADR.** Choose between strong logical controls in a shared environment, dedicated workspace/account/project boundaries, dedicated compute, separate storage/security domains, or fully separate environments for a sensitive domain. Compare security, performance, shared-control-plane risk, operational burden, cost, recovery, cross-domain sharing, and residual risks. Do not claim physical separation alone solves weak internal access controls.

---

## 10. Topic 08 — Platform service levels and product thinking

### Foundation

**T08-F1 — MCQ (one answer).** Which statement best distinguishes SLI, SLO, and SLA?

A. An SLI is a measured indicator; an SLO is an internal objective for that indicator; an SLA is an agreement that may define commitments and consequences.  
B. An SLI is a product name, an SLO is an implementation detail, and an SLA is a dashboard.  
C. An SLO and SLA must always have identical targets.  
D. A target is measurable even if no event, window, numerator, or denominator is defined.

**T08-F2 — Short answer.** Distinguish a platform service from a data product, and distinguish an output metric from a user/business outcome. Give one example of each distinction.

**T08-F3 — Explain why.** Why should a platform not promise the same availability target for every service without considering criticality, dependencies, support needs, and cost?

### Application

**T08-A1 — SLI/SLO definition.** Define an SLI and illustrative SLO for a scheduled reporting service. Include good-event numerator, eligible-event denominator, measurement window, target assumption, exclusions/caveats, owner, alert/action, and evidence. Explain how the target should be derived from requirements.

**T08-A2 — Dependency chain.** A service relies on four serial dependencies with illustrative availabilities 0.999, 0.9995, 0.9999, and 0.999. Assuming independent failures and no redundancy, calculate the approximate combined availability. Explain why this is only a simplified model.

**T08-A3 — Product discovery.** Adoption of a self-service platform is low, but leadership proposes mandatory migration. Design a discovery plan using user interviews, journey friction, adoption and outcome metrics, feedback loops, prioritization, and build/buy/defer criteria. State when mandatory controls may still be justified.

### Advanced / design

**T08-D1 — Service charter / product canvas.** Create a charter for a fictional enterprise data platform. Include users, jobs-to-be-done, outcomes, capabilities, service catalogue, SLI/SLO table, dependencies, service tiers, support hours, escalation, incident communications, change/deprecation policy, cost model, feedback channels, owners, assumptions, and risks. Mark all targets as illustrative assumptions and explain their derivation.

---

# Part II — Mixed checkpoints

## 11. Checkpoint A — after Topics 01–04

**Recommended time:** 45–60 minutes. **Suggested points:** 40. Questions combine the platform's logical structure, data movement, refinement, and planes.

**CA-1 — MCQ (4 points).** A logical architecture diagram uses vendor product names as its main boxes and omits owners and cross-cutting controls. What is the best correction?

A. Add more vendor logos.  
B. Replace the view with capability-oriented components, state responsibilities and owners, and show cross-cutting controls and data/control flows.  
C. Remove all arrows.  
D. Convert the diagram into a list of data tables.

**CA-2 — Flow trace (8 points).** Trace a daily partner file from receipt to a supported reporting product. Include ingestion, validation, quarantine/replay, storage/refinement, processing, metadata, identity/policy, and consumption. Mark owner and a control at every boundary.

**CA-3 — Defect diagnosis (8 points).** A design transforms files in the landing zone, drops invalid rows without evidence, lets all users query raw data, and sends dashboards directly to an unowned “gold” table. Identify four defects and give one corrective action for each.

**CA-4 — Plane reasoning (8 points).** A job scheduler accepts work, compute starts, but the metastore is unavailable. Explain which plane is failing, what can still be functioning, what the user experiences, and two recovery/degraded-mode choices with trade-offs.

**CA-5 — Layer/product distinction (12 points).** Define a three-stage refinement model for a fictional payment dataset and specify one supported product for Finance. Include layer purposes, promotion tests, product owner, grain/contract, consumer boundary, and one reason the model might be adapted.

### Checkpoint A answer key and rubric

- **CA-1:** B. Full credit requires capability view, responsibility/ownership, and cross-cutting flows; one element missing earns partial credit.
- **CA-2:** 8 points: correct zone/refinement sequence (2); validation/quarantine/replay (2); owner and boundary control (2); metadata/access/consumer product path (2). Accept alternative layouts if responsibilities and failure paths are explicit.
- **CA-3:** 2 points per defect/action pair, maximum 8. Expected issues: landing-zone transformation obscures source fidelity; reject data are lost; raw access is too broad; gold table is not an owned/contracted product. Other technically valid defects can earn credit.
- **CA-4:** 8 points: identify control-plane metadata dependency (2); distinguish intact data/compute from failed table resolution or job authorization (2); state user impact (1); two viable mitigations with trade-offs (3). Do not claim stored data are necessarily lost.
- **CA-5:** 12 points: layer purpose and ownership (3); measurable promotion criteria (3); product contract/grain/owner (3); consumer boundary and adaptation rationale (3). Accept equivalent layer names if purpose and gates are clear.

---

## 12. Checkpoint B — after Topics 05–08

**Recommended time:** 45–60 minutes. **Suggested points:** 40. Questions combine metadata, guarded self-service, isolation, and service promises.

**CB-1 — MCQ (4 points).** A catalog harvests a dataset's columns automatically, but its owner, classification, and business definition are stale. Which conclusion is best?

A. Harvested metadata are always authoritative.  
B. Metadata collection must be combined with ownership, authoritative-source rules, quality checks, and drift remediation.  
C. Delete the catalog.  
D. Allow all users to edit every metadata field without audit.

**CB-2 — Control classification (8 points).** Design a self-service path for a new pipeline and classify at least four controls as enforced, default, recommended, or approval-required. Explain the reason for each classification and define an auditable exception path.

**CB-3 — Isolation decision (8 points).** A sensitive Risk dataset shares storage, identity, catalog, and compute with low-risk exploratory analytics. Recommend a boundary model and identify at least four residual risks or controls that still need attention.

**CB-4 — SLI/SLO feasibility (8 points).** Define one measurable platform SLI/SLO and one data-product freshness promise. Explain the difference in owner, measurement boundary, and upstream dependency caveats.

**CB-5 — Product outcomes and cost (12 points).** Low adoption, rising support tickets, and rising compute cost occur after self-service launches. Propose a prioritized response with user discovery, outcome measures, cost transparency, quotas or tiers, support ownership, and review triggers. Distinguish activity/output metrics from outcomes.

### Checkpoint B answer key and rubric

- **CB-1:** B. The core point is that harvesting does not guarantee semantic accuracy, current ownership, classification, or authority.
- **CB-2:** 8 points: controls are enforceable and proportionate (3); exceptions include owner, rationale, approval, scope, expiry/review and evidence (3); workflow is observable and usable (2). Multiple classifications can be valid if justified.
- **CB-3:** 8 points: boundary selection tied to sensitivity/threat model (2); data and identity controls (2); shared catalog/control-plane and compute considerations (2); residual risks and incident containment (2). Dedicated resources may be justified, but “separate schema” alone is not sufficient evidence.
- **CB-4:** 8 points: measurable numerator/denominator or method and window (3); separate platform vs product boundary/owner (2); explicit assumptions/dependencies (2); realistic alert/action (1).
- **CB-5:** 12 points: discovery and prioritization (3); outcome-oriented metrics (2); cost/usage visibility and quota/tier policy (3); ownership/support response (2); review triggers and trade-offs (2). “Force everyone to migrate” alone earns little credit without evidence and risk justification.

---

# Part III — Integrated assessment and supplementary design exercises

## 13. Integrated case study — Northbridge Bank (illustrative)

### 13.1 Scenario and explicit assumptions

Northbridge Bank is a **fictional teaching scenario**. It has six teams: Retail Analytics, Risk, Fraud, Finance, Marketing, and Data Science. It receives operational database extracts, daily partner files, and event streams. It wants a governed lakehouse-style platform with shared capabilities, self-service onboarding, clear data ownership, and measurable service expectations.

For this exercise, assume:

- Payment and customer data are sensitive and access must be restricted to approved purposes.
- Risk and Finance need dependable reporting; Data Science runs variable, resource-intensive exploratory jobs.
- The organization wants cross-team reuse through owned, documented data products rather than broad raw-data access.
- The platform has shared identity/policy, catalog/metadata, orchestration, observability, and billing/cost-metering capabilities.
- No specific cloud provider, regulatory clause, product implementation, or legal interpretation is prescribed. If you need one to make a decision, state it as an assumption and explain how it could change the design.
- Any service target, cost, workload volume, retention period, or recovery objective you invent is illustrative and must be derived from a stated requirement rather than presented as universal.

### 13.2 Required deliverables

Produce an architecture package with the following artifacts. You may use a diagramming tool or Markdown/Mermaid; the diagram must remain logical and vendor-neutral.

1. **Logical reference architecture (Topic 01):** capabilities and relationships; data flows and control flows; owner for each capability; source-to-consumer trace for one payment record.
2. **Zone model (Topic 02):** zone purpose, input/output, owner, access, retention, boundary checks, quarantine, replay, and batch/stream convergence.
3. **Layer and product definitions (Topic 03):** bronze/silver/gold purpose and promotion tests; one Finance or Risk data-product specification with owner, grain, interface, definitions, quality, freshness, change policy, and consumer support.
4. **Plane-responsibility matrix (Topic 04):** compute/storage/control responsibilities; read, write, and job-run interactions; behavior during catalog/identity/storage/compute failures; cost and coupling analysis.
5. **Metadata model (Topic 05):** technical, business, governance, lineage, quality, and operational fields; authoritative source and maintainer; catalog/metastore roles; registration and drift-detection workflow.
6. **Self-service workflow (Topic 06):** user journey from discovery to production; template/golden path; enforced/default/recommended controls; approval and time-bounded exception path; measurable DX indicators.
7. **Isolation model (Topic 07):** boundary per team and dimension (identity, data, compute, network where relevant, keys, metadata, control plane, audit, quotas, administration); residual risks; shared/isolated responsibility; quota/priority and cost-allocation method.
8. **Service catalogue and SLI/SLO table (Topic 08):** user journey/service, SLI definition, measurement window, target assumption, exclusions/caveats, owner, alert/action, evidence; support model and escalation; separate platform SLOs from data-product promises.
9. **At least one justified ADR:** state context, requirements, constraints, assumptions, options, decision, rationale, rejected alternatives, consequences, residual risks, and review triggers. Across module completion, the roadmap recommends at least five ADRs.
10. **Security-review defense:** a short response to a skeptical reviewer who challenges the isolation boundary, shared catalog, service identity, and ability to recover from cross-tenant exposure.

### 13.3 Case-study questions

**INT-1 — Capability scope.** Which capabilities should be centrally operated, which responsibilities remain with domain teams, and where is joint ownership required? Give reasons, not only a list.

**INT-2 — Record trace.** Trace one fictional payment record from source through landing/validation, quarantine if invalid, refinement, metadata, and a governed Finance/Risk product. Name the control and owner at each transition.

**INT-3 — Product contract.** Define a Finance reporting product's grain, semantics, owner, consumers, quality checks, freshness promise, support route, and compatibility/deprecation process. State what is not promised.

**INT-4 — Plane failure.** If the catalog is unavailable but underlying files remain present, describe the likely effect on discovery, authorization, query execution, and recovery. Avoid assuming all systems behave identically.

**INT-5 — Metadata authority.** Decide which fields are harvested and which require a human/domain owner. Explain how conflicting ownership or classification values are resolved.

**INT-6 — Self-service governance.** Design the shortest safe path for a new team to publish a product. Identify which controls block, which are defaults, and what requires approval.

**INT-7 — Isolation and threat model.** Select boundaries for Risk and exploratory Data Science. Name at least five threats, controls, evidence, and residual risks. Explain the limits of logical isolation and why physical separation is not a complete security strategy.

**INT-8 — Service promises.** Define at least two platform service SLOs and two product-level promises. For each, define the measurement boundary and owner. Explain the dependency chain and how upstream failures are communicated.

### 13.3.1 Integrated-case answer anchors (not a single mandated design)

Use these anchors alongside the 100-point rubric below. They describe evidence a strong answer should address; alternative architectures are acceptable when they satisfy the stated assumptions and explain their trade-offs.

| ID | Expected reasoning anchors |
|---|---|
| INT-1 | Central platform ownership for shared capabilities such as identity/policy baseline, orchestration patterns, catalog services, observability, provisioning, and cost meters; domain ownership for definitions, pipeline logic, data quality rules, product contracts, and consumer support; joint ownership for onboarding, classification, access approvals, and incident coordination. Explicitly assign owners rather than assuming centralization solves accountability. |
| INT-2 | Identify source receipt and immutable/evidence-preserving capture where justified; validate schema and business rules; quarantine rejects with reason and replay path; apply classification/access controls; transform through defined refinement stages; register lineage and ownership; publish only through an owned product interface; trace who can read each step. |
| INT-3 | Define grain and semantics, accountable product owner, intended consumers and purpose, interface/schema, quality and reconciliation checks, freshness measurement, support route, change compatibility/versioning, and deprecation notice. State exclusions and upstream dependency caveats. |
| INT-4 | Treat catalog/metadata and identity as dependencies that may prevent discovery, authorization, or query planning even if bytes remain durable. Describe actual behaviour as implementation-dependent; include detection, incident communication, recovery, and any safe degraded mode without bypassing authorization. |
| INT-5 | Harvest objective technical fields where reliable; require accountable owners for business meaning, classification, and product promise; define authoritative source per field, conflict resolution, versioned changes, sensitive-metadata access, freshness checks, and stale/unknown states. |
| INT-6 | Provide discoverable template-based onboarding with least-privilege identity, classification, resource quotas/tags, contract and quality tests, logging/lineage, and production-readiness checks. Explain which controls block automatically, which are defaults, which are advice, and which approvals are risk-based; make exceptions scoped, owned, evidenced, and time-bounded where appropriate. |
| INT-7 | Choose boundaries by data sensitivity, threat model, blast radius, workload interference, recovery, and cost. Cover data/identity, compute, metadata/control plane, admin paths, keys, audit, quotas, and governed sharing. Include threats such as mis-scoped identity, metadata leakage, resource starvation, and administrator misuse; state residual risks even for dedicated infrastructure. |
| INT-8 | Define each platform SLI with a measurable good/eligible event or equivalent method, denominator, window, target assumption, owner, alert/action, and evidence. Separately define product freshness/quality promises and their product owner. Show dependency-chain feasibility, upstream ownership and exclusions, incident communications, and user/business outcome measures. |

### 13.4 Integrated-case rubric (100 points)

| Area | Points | Full-credit evidence |
|---|---:|---|
| Logical architecture and ownership | 10 | Vendor-neutral capabilities, owners, control plane, clear data/control flows, complete trace |
| Zones and failure paths | 10 | Explicit boundary checks, reject/quarantine, replay, access and retention |
| Layers and data product | 10 | Purpose and promotion tests; product has owner, contract, consumers, quality/freshness and change expectations |
| Plane separation and failure/cost reasoning | 10 | Correct responsibilities, interactions, dependencies, cost and failure trade-offs |
| Metadata and governance | 10 | Distinct metadata categories, source/owner, catalog/metastore roles, drift detection and access controls |
| Self-service and DX | 10 | Usable journey, enforceable guardrails, justified approvals/exceptions, measurable friction/outcome indicators |
| Tenant isolation and threat model | 15 | Per-dimension boundary choices, threat/control/evidence mapping, residual risks, quotas and allocation |
| Service levels and product thinking | 15 | Measurable SLIs/SLOs, stated target assumptions, dependency reasoning, support/escalation and outcome metrics |
| ADR, assumptions, and defense | 10 | Alternatives, rationale, consequences, residual risks, review triggers, coherent security defense |

**Partial credit:** award credit for a defensible alternative if it satisfies stated requirements and identifies trade-offs. Deduct where the design silently assumes guarantees, confuses zones with refinement layers, treats a gold table as a product without a contract, omits ownership, or states an unmeasurable SLO. A polished diagram does not compensate for missing controls or operational ownership.

---

## 14. Required supplementary practical exercises

These five exercises are explicitly included because the module roadmap says multiple-choice and short-answer questions alone are insufficient for design assessment.

### EX-1 — Draw a logical reference architecture

**Prompt:** Use the Northbridge brief in Section 13.1. In 30 minutes, draw the capabilities and relationships without vendor names. Include data and control flows, identity/policy, catalog/metadata, orchestration, observability, and ownership.

**Deliverable:** One logical diagram, a capability inventory with owners, and a source-to-consumer trace.

**Validation:** Every box has a one-sentence responsibility; every flow has a direction and purpose; cross-cutting controls are visible; no unexplained hop remains; logical capabilities are not confused with physical product choices.

### EX-2 — Diagnose a flawed architecture

**Prompt:** Review this fictional design: all source files are transformed in the landing area; invalid records are dropped; raw data is readable by all teams; dashboards query a shared gold table with no owner; the catalog is not part of the job dependency model; all teams share one service credential; there are no quotas, cost tags, or SLO measurement windows; “99.99% uptime” is written on a slide but no SLI exists.

**Deliverable:** At least ten defects, each paired with severity/impact, corrective action, owner, and evidence that would prove remediation.

**Validation:** At least ten distinct defects are identified; fixes cover data flow, ownership, security, metadata, control-plane dependency, tenant isolation, cost, and measurable service levels. Duplicate restatements do not count as distinct defects.

### EX-3 — ADR for shared versus isolated sensitive domain

**Prompt:** Choose an isolation model for the fictional Risk domain. Compare (a) shared environment with enforced logical controls, (b) dedicated workspace/account/project and compute, and (c) separate environment/security domain. State assumptions about data sensitivity, threat model, scale, recovery, staff, cost, and cross-domain sharing.

**Deliverable:** An ADR with context, requirements, options, decision, rationale, consequences, residual risks, and review triggers.

**Validation:** The chosen mechanism is not described as risk-free; data, identity, compute, metadata/control plane, administrator, and recovery risks are considered; alternatives are compared fairly; cross-team sharing uses a governed interface.

### EX-4 — Availability across a dependency chain

**Prompt:** A service depends on four serial dependencies with illustrative availability values of 99.9%, 99.95%, 99.99%, and 99.9%. Assume independent failures, each dependency must be available for the service to succeed, no redundancy, and values measured over the same window. Estimate the combined availability.

**Deliverable:** Formula, calculation, assumptions, and interpretation for a proposed service target.

**Validation:** Convert percentages to decimals and multiply: `0.999 × 0.9995 × 0.9999 × 0.999 ≈ 0.9974`, or about **99.74%**. Explain that this simplified series model is not a substitute for observed end-to-end measurement; correlated failures, retries, caching, redundancy, partial success, and different measurement windows can change the result. A service should not promise a higher target without a design and evidence that justify it.

### EX-5 — Defend the design to a skeptical security reviewer

**Prompt:** The reviewer asks: “Why should I trust your shared catalog and tenant model? What prevents a service identity from reading another team's data? How will you detect misuse? What happens if an administrator is compromised? How do you share data without opening broad access?”

**Deliverable:** A two-page defense with a threat/control/evidence/residual-risk table and one cross-team data-sharing flow.

**Validation:** Responses name enforceable controls, identity scope, least privilege, separation of duties/break-glass auditing, independent detection, containment/revocation, evidence retention, and governed product interfaces. “The schema names are different” or “the infrastructure is physical” alone is not sufficient.

---

# Part IV — Answer key and marking guidance

## 15. Topic 01 answer key

- **T01-F1:** B. A logical reference architecture describes capabilities and relationships independently of a specific deployment. A physical deployment view may later map capabilities to products and infrastructure.
- **T01-F2:** Capability = what the platform must be able to do (e.g., ingest and validate data); component = a logical or physical element that implements a responsibility (e.g., validation service); interface = the defined way a component or product is requested or consumed (e.g., API, event contract, or documented table contract); data flow = movement of data between steps; data product = an owned, supported interface for defined consumers. Credit correct definitions and examples; do not require a specific implementation.
- **T01-F3:** These concerns cross multiple flows and stages. Consistent enforcement and evidence reduce gaps, but each control still needs a clear owner and enforcement point. Encryption protects data in transit/at rest according to the threat model; audit supports investigation; lineage supports traceability; observability supports operations; cost attribution supports accountability. Accept other technically sound examples of failure from an unowned control.
- **T01-A1 rubric (10 points):** sources and ingestion (2); storage/refinement/processing/consumption (2); identity/policy and metadata (2); orchestration/observability (1); data vs control flows (1); ownership and traceability (2).
- **T01-A2 expected defects:** product logos obscure capabilities; no component responsibilities; missing owners; missing cross-cutting controls; unexplained source-to-dashboard hop; no boundaries or failure paths. Award one point per distinct defect plus one for a practical correction, up to 8.
- **T01-A3 examples:** “execute distributed transformations” rather than “Spark cluster”; “durably store governed datasets” rather than “object store”; “present governed metrics to consumers” rather than “dashboard tool.” Ownership questions include who manages runtime/configuration, access/retention, or metric definitions and support.
- **T01-D1 rubric (12 points):** assumptions and decision criteria (2); comparison of centralized/federated/hybrid patterns and their trade-offs (3); central/domain/joint ownership rationale (2); cross-cutting controls and complete trace (3); residual risks and review triggers (2). Accept any pattern if it fits stated requirements and the alternatives are fairly evaluated.

## 16. Topic 02 answer key

- **T02-F1:** C. It preserves evidence, contains invalid data, and makes recovery explicit. Whether the source file itself is retained and for how long depends on classification, replay needs, and policy.
- **T02-F2:** Ingestion receives and validates source data; storage retains data under defined access/retention; processing transforms and validates; consumption exposes fit-for-purpose interfaces. Boundary rules may include schema/contract checks, classification, quality gates, access changes, or promotion approvals.
- **T02-F3:** Transport and latency differ, but metadata, access, storage, quality, lineage, and consumers still need coherent treatment. Streaming is not automatically a disconnected architecture.
- **T02-A1 rubric (8 points):** separates download from validated success (2); immutable/source-preserving capture or explicit retention rationale (1); quarantine with reason and owner (2); idempotent retry/replay (2); alert/evidence (1).
- **T02-A2 rubric (10 points):** correct zone purposes and interfaces (3); ownership/access/retention (2); validation and reject path (2); failure/replay handling (2); assumptions stated (1). Do not require a streaming design for this daily-file prompt; credit batch/stream convergence only if the learner identifies it as a relevant, explicitly stated design assumption.
- **T02-A3 key points:** raw data may contain sensitive fields, malformed records, or source-specific semantics; broad access increases exposure and operational coupling; raw access should be purpose-bound, audited, and governed. “Unclean” does not mean “safe to expose.”
- **T02-D1 rubric (12 points):** requirements/latency and sensitivity (2); justified boundaries (2); movement/promotion rules (3); access/retention (2); reject/replay (2); alternatives and rationale (1).

## 17. Topic 03 answer key

- **T03-F1:** B. A layer is a refinement stage; a product has an owned consumer interface and suitable contract, documentation, and service/quality expectations. Physical implementation can vary.
- **T03-F2:** Bronze commonly preserves source-oriented/raw history; silver applies validation, normalization, and integration; gold serves curated analytics or use cases. Names and number of layers can be adapted when a simpler or different design better meets requirements while retaining explicit quality and ownership boundaries.
- **T03-F3:** Internal representations may change without notice; access may be too broad; transformations and definitions may be bypassed; data quality and lineage become harder to govern.
- **T03-A1 rubric (10 points):** measurable validation/duplicate/schema criteria (3); semantic and reconciliation criteria (2); promotion failure handling (2); owner/evidence (1); additional product-level criteria and consumer expectations (2).
- **T03-A2 key points:** gold describes refinement/serving position; product adds purpose, owner, interface, contract, consumers, metadata, quality/freshness expectations, compatibility, support and change process.
- **T03-A3 expected remediation:** define grain and metric semantics; assign accountable owner; define source lineage; add tests and quality thresholds; document freshness and support; declare interface and version/change policy; review consumer permissions.
- **T03-D1 rubric (12 points):** latency/use-case requirements (2); coherent stages and rationale (3); promotion tests (3); stable consumer contract (2); trade-offs and failure behavior (2).

## 18. Topic 04 answer key

- **T04-F1:** A. These are responsibility groupings, not necessarily three physical servers. Exact placement varies by implementation; cross-cutting services may span planes.
- **T04-F2:** A valid trace includes request/authentication and metadata resolution (control-plane interactions), query/job execution (compute), reads/writes to durable tables/files (storage), and return of results. State that implementations may combine or reorder some steps.
- **T04-F3:** Separation can scale compute independently and improve workload isolation, but adds orchestration, data transfer, and operational complexity. A shared control plane centralizes governance but can become a dependency or common failure domain.
- **T04-A1 rubric (8 points):** identifies metadata/identity as control-plane dependencies (2); distinguishes data persistence from service usability (2); explains user impact (1); gives two mitigations/degraded modes and their trade-offs (3).
- **T04-A2 key variables:** utilization profile, concurrency, idle time, autoscaling latency, workload interference, reserved capacity, data movement, storage/compute rates, operational overhead, reliability, and recovery. Use measured workloads and stated assumptions.
- **T04-A3 expected classification:** query execution—compute; durable data—storage; table definitions—often metastore/catalog and therefore control/metadata plane; scheduling—control plane; policy decisions—control plane/cross-cutting; audit events—cross-cutting observability/control; autoscaling—control plane managing compute. Credit nuanced answers that explain implementation-dependent overlap.
- **T04-D1 rubric (12 points):** workload requirements (2); correct plane matrix and interactions (3); dependency/failure model (2); cost/performance analysis (2); operational ownership and alternatives (2); review triggers (1).

## 19. Topic 05 answer key

- **T05-F1:** B. These terms overlap in some implementations, so explain the responsibilities rather than assuming one universal product boundary.
- **T05-F2:** Examples: technical—schema/version (engine or automated scanner); business—definition of payment status (domain owner); governance—classification (governance owner/policy workflow); lineage—upstream source/job (lineage collector and pipeline owner); quality—reconciliation pass rate (test system/product owner); operational—last successful run (orchestrator). Field sources should be plausible and ownership explicit.
- **T05-F3:** Harvesters can discover structure but not reliably infer business meaning, legal basis, accountable owner, current policy, or correct lineage in every case. Metadata may also become stale after changes.
- **T05-A1 rubric (10 points):** required fields/owners (2); automated vs human responsibilities (2); access/security (2); publication/change/retirement workflow (2); drift detection and evidence (2).
- **T05-A2 expected actions:** reconcile owner with accountable domain; mark unknown/stale lineage and repair collection; restrict sensitive descriptions/metadata where appropriate; log changes; alert owner; review downstream impact.
- **T05-A3 examples:** percentage of active products with accountable owner = owned active products / all active products; percentage with current classification; lineage coverage = in-scope assets with required lineage / all in-scope assets. Define scope, time, and action on breach.
- **T05-D1 rubric (12 points):** topology rationale (2); authority and sync (3); access/privacy (2); lineage/quality and drift (2); failure and ownership (2); alternatives (1).

## 20. Topic 06 answer key

- **T06-F1:** C. It enforces policy at the decision point and records evidence. Documentation and UI labels may help but do not themselves enforce access.
- **T06-F2:** A golden path is a supported, repeatable route with templates and safe defaults. Governance remains in automated policy, access controls, validation, audit, and justified approvals.
- **T06-F3:** (i) enforced; (ii) default with a controlled exception, and the exception approval is enforced; (iii) recommended. If a “default” can be bypassed without control, it is not a security enforcement.
- **T06-A1 rubric (8 points):** complete journey (2); friction/automation (2); owner and policy decision (2); validation/support/evidence (2).
- **T06-A2 expected fields:** requester/asset/scope, business reason, risk assessment, data owner and control owner, authorized approver, compensating controls, start/expiry/review, monitoring, audit record, and revocation/exit criteria.
- **T06-A3 examples:** time to first successful governed query; onboarding lead time; first-pass validation success; support tickets per active team; template adoption; time to production-ready product; user satisfaction. Explain segmentation and possible confounders; activity counts alone do not prove value.
- **T06-D1 rubric (12 points):** usable workflow (2); correct control classification (3); exception/version/retirement lifecycle (3); adoption/friction/outcome measures (2); governance and trade-offs (2).

## 21. Topic 07 answer key

- **T07-F1:** C. Naming a namespace does not by itself enforce a boundary. Permissions, service identities, admin paths, shared services, and configuration must be tested against the threat model.
- **T07-F2:** Tenant = unit sharing a platform under defined boundaries; boundary = enforced scope of access/resources/administration; logical isolation = software/policy separation on shared infrastructure; physical isolation = dedicated infrastructure or security domains; noisy neighbour = one tenant's resource use degrades another's experience. Data controls do not automatically isolate compute, failure, metadata, or admin privileges.
- **T07-F3:** cross-team read—data/identity authorization; large job—compute/workload isolation; shared credentials—identity attribution/least-privilege gap; missing billing visibility—cost metering/allocation gap.
- **T07-A1 rubric (10 points):** sensitivity/rationale (2); choices across required dimensions (3); shared vs tenant ownership (1); quotas/cost (2); residual risks (2). Several designs can be valid if threats and consequences are explicit.
- **T07-A2 rubric (12 points):** across the six specified cases, score (1) coverage of each trigger/threat, asset, and boundary crossed (3 points); (2) preventive controls that address the stated threat (2); (3) detective evidence and monitoring (2); (4) corrective containment/recovery response (2); (5) accountable owner and auditable evidence trail (1); and (6) explicit residual risk or limitation (2). The answer must address all six cases to earn full credit; award partial credit for sound controls on a subset. Accept technically equivalent controls.
- **T07-A3 answer:** guaranteed total = `5 × 15 = 75` units; burst pool = `100 − 75 = 25` units. Three tenants requesting 20 additional units each demand 60 units, exceeding the 25-unit burst pool by 35. A defensible rule might allocate burst by priority, weighted fair share, queueing, or pre-agreed caps; specify whether work queues, slows, or is rejected. No single policy is universal; state how fairness, deadlines, and service tiers interact.
- **T07-D1 rubric (12 points):** threat/sensitivity/requirements (2); comparison across dimensions (3); operational/cost/recovery consequences (2); residual risks and admin controls (2); governed sharing and review triggers (3).

## 22. Topic 08 answer key

- **T08-F1:** A. An SLI measures observed behaviour; an SLO is a target for that indicator over a defined window; an SLA is a formal agreement that may include commitments, exclusions, reporting, and consequences. Contractual meanings vary by agreement and jurisdiction.
- **T08-F2:** A platform service is a reusable capability/operating service (e.g., governed ingestion or catalog access); a data product is a defined dataset/interface for specific consumers (e.g., daily delinquency product). Output: number of pipelines created; outcome: time for an analyst to obtain a trusted answer or business process impact.
- **T08-F3:** Services have different criticality and dependency chains. Higher targets may require redundancy, staffing, capacity, and cost; one target may overpromise for low-criticality services or under-serve critical workflows.
- **T08-A1 rubric (10 points):** unambiguous event and good/bad definitions (3); numerator/denominator and window (2); target explicitly illustrative and requirement-derived (2); owner/action/evidence/caveats (3).
- **T08-A2 answer:** `0.999 × 0.9995 × 0.9999 × 0.999 ≈ 0.9974`, approximately **99.74%**. Under independent serial availability assumptions, every dependency must be available. Real dependencies may be correlated; retries, redundancy, caching, partial functionality, and different windows change effective end-to-end results. The end-to-end SLI should be measured directly where possible.
- **T08-A3 rubric (10 points):** user research and journey analysis (3); adoption plus outcomes (2); feedback/prioritization and build/buy/defer (3); proportionate mandatory controls where risk warrants (2).
- **T08-D1 rubric (12 points):** users/jobs/outcomes (2); capabilities/catalogue (2); measurable SLI/SLO and dependency assumptions (3); support/incident/change model (2); cost/feedback/risks/ownership (3).

---

# Part V — Scoring, readiness, and final-project gate

## 23. Scoring guide

### 23.1 Topic-level scoring

For the topic-level sections, use this recommended allocation per topic:

| Question type | Suggested points per topic | What is being evaluated |
|---|---:|---|
| Foundation items (three questions) | 6 | Correct distinctions and explanations, not memorized labels alone |
| Application items (three questions) | 9 | Diagnosis, measurable rules, ownership, and practical reasoning |
| Advanced design item | 5 | Assumptions, alternatives, rationale, residual risks, and review triggers |
| **Total per topic** | **20** | **100% topic score** |

For reproducible scoring, normalize each topic to 20 points as follows: Foundation = 6 points (F1 = 1; F2 = 2.5; F3 = 2.5); Application = 9 points (score A1, A2, and A3 against their local rubric, then convert each result proportionally to 3 points); Advanced design = 5 points (score D1 against its local rubric, then convert proportionally to 5 points). For foundation short answers F2/F3, use the answer-key points for that item: full credit (2.5) when all essential requested distinctions/reasons are correct; partial credit (1.25–2.0) when the core is correct but one or more material elements are missing; limited credit (0.5–1.0) when the answer contains a relevant correct point but is materially incomplete; no credit (0) when it is incorrect, irrelevant, or blank. For an application item without a stated raw-point rubric, use the three-point task-appropriate template below rather than forcing irrelevant criteria onto every question:

- **Concept/explanation or comparison:** correctness (1), explanation/evidence (1), relevant example, limitation, or trade-off (1).
- **Calculation:** correct formula and assumptions/units (1), arithmetic (1), interpretation and limitations (1).
- **Classification:** correct classifications (1), rationale (1), treatment of overlap/edge cases where relevant (1).
- **Diagnosis/troubleshooting:** identifies the material defect (1), explains impact or cause (1), proposes a corrective action and evidence (1).
- **Design/workflow:** satisfies required steps and boundaries (1), assigns owners/controls/evidence (1), explains trade-offs, failure paths, or residual risks (1).

For any item with a local maximum, normalized points = raw points earned ÷ raw maximum × normalized maximum. Record raw and normalized scores so the denominator is reproducible. If a question requires several deliverables, award partial credit proportionally against its stated rubric; do not add an unstated requirement after the response is submitted. These allocations are assessment-design recommendations, not roadmap-mandated weights.

### 23.2 Mixed checkpoints

Checkpoint A and B each use the 40-point allocation specified in their sections. These checkpoints are diagnostic and should be scored separately from the eight topic scores unless the assessor documents a combined weighting in advance.

### 23.3 Partial credit and fairness

Apply these rules to every constructed-response item, in addition to its item-specific criteria:

- **Full credit:** every essential criterion listed in the question/rubric is satisfied; the reasoning is technically sound; assumptions and requested evidence are explicit.
- **Partial credit:** award points criterion by criterion. A criterion earns 100% of its weight when fully met, 50% when the core is correct but materially incomplete, and 0% when absent, incorrect, or unsupported. For a multi-part answer, do not let a correct section erase a material omission elsewhere.
- **No credit:** the response is blank, irrelevant, or fundamentally incorrect on the criterion being scored. A technically sound alternative earns credit even if it differs from the answer anchor.
- Accept alternate architectures when they satisfy the stated requirements and explain trade-offs, assumptions, ownership, and residual risk.
- Do not award full credit for unsupported absolutes such as “separate schema is secure,” “physical isolation solves security,” “gold means product,” or “99.99% is always the right SLO.”
- For arithmetic, award method credit if the formula and assumptions are correct even when a minor rounding error occurs; apply the calculation rubric's formula, arithmetic, and interpretation criteria separately.
- For open-ended work, use the stated rubric and document why points were withheld; do not grade based on preference for one vendor or diagram style.

### 23.4 Readiness thresholds

The module roadmap recommends **at least 85% across the full topic-level question set and no topic below 70%** before the final project. For a reproducible calculation, use the eight normalized topic scores from §23.1: combined topic-level readiness = total normalized points earned across Topics 01–08 ÷ 160 × 100. The topic floor is calculated separately for each topic out of 20. The mixed checkpoints (40 points each) and integrated case (100 points) are reported separately as diagnostic/design evidence and do not change the roadmap's 85% question-set score unless the assessor declares a combined weighting policy before the attempt. These are roadmap-recommended readiness thresholds, not universal industry standards or guarantees of professional competence.

Readiness should also require all eight topic gates signed off, completion of the integrated case, reviewed deliverables, at least five justified ADRs across the module, and no unresolved material gap older than one week. A high quiz score does not compensate for an incomplete architecture deliverable.

## 24. Spaced reattempt and remediation procedure

1. **First attempt:** complete the relevant section closed-book; mark confidence as high, medium, or low before checking the key.
2. **Diagnose:** mark each answer correct, partly correct, or wrong and write a one-sentence explanation of the error or uncertainty.
3. **Map:** link the error to the topic and its completion gate in Section 2.
4. **Remediate:** reread the exact lesson subsection, then redo a corresponding deliverable or exercise. Avoid merely copying the answer key.
5. **Reattempt after 2–4 days:** answer without the lesson or key. Record the date and evidence in the gap log.
6. **Persistent gap:** if the same misconception appears twice, redo the topic exercise and request peer review. Reattempt again after 7–10 days.
7. **Close:** mark a gap resolved only after a correct reattempt and, for design skills, a reviewed artifact that meets its validation criteria.
8. **Recheck before the project:** complete Checkpoint A, Checkpoint B, and the integrated case. Resolve contradictions discovered during integration, even if individual topic scores previously passed.

## 25. Final project readiness checklist

Use this as the gate before beginning or submitting `Projects/07-enterprise-lakehouse-reference-architecture.md`.

### Knowledge and assessment

- [ ] All eight topic sections attempted; every answer has been scored against the key/rubric.
- [ ] Overall score meets the roadmap's recommended 85% threshold, and every topic meets the recommended 70% minimum.
- [ ] Checkpoint A (Topics 01–04) and Checkpoint B (Topics 05–08) completed and reviewed.
- [ ] Gap log contains no unresolved material items older than one week; repeated errors triggered a practical redo.

### Topic deliverables and gates

- [ ] **Topic 01:** capability inventory and logical reference architecture reviewed; complete end-to-end trace; no unexplained hop.
- [ ] **Topic 02:** zone table and flows reviewed; every source has reject/replay path; every boundary has a rule; raw-data retention rationale stated.
- [ ] **Topic 03:** layer table, promotion tests, and one product specification reviewed; consumers depend on supported products/interfaces rather than unstable internal layers by default.
- [ ] **Topic 04:** plane responsibility matrix, interaction diagrams, and cost/failure analysis reviewed; control-plane failure behaviour documented.
- [ ] **Topic 05:** metadata model and workflow reviewed; owners and sources defined; drift detection exists; sensitive metadata access considered.
- [ ] **Topic 06:** user journey and self-service workflow reviewed; controls classified and justified; approvals have reasons; DX measures are observable.
- [ ] **Topic 07:** tenant boundaries list residual risks; quota and allocation arithmetic reproduced by a reviewer; cross-tenant sharing uses a defined governed interface.
- [ ] **Topic 08:** service catalogue, SLI/SLO table, support model, and product canvas reviewed; at least one dependency-chain calculation included; all sample targets labeled assumptions.

### Integrated architecture

- [ ] Integrated Northbridge case completed with all ten artifacts in Section 13.2.
- [ ] All assumptions, constraints, ownership boundaries, and alternatives are explicit.
- [ ] At least one sensitive-domain isolation ADR is complete; the module package contains at least five justified ADRs as recommended by the roadmap.
- [ ] At least one skeptical security review has been answered with controls, evidence, and residual risks.
- [ ] Architecture distinguishes logical capability views from physical vendor mapping and distinguishes platform service SLOs from data-product promises.
- [ ] The final project is reviewed by another person; feedback and resulting revisions are recorded.

## 26. Glossary

| Term | Meaning in this assessment |
|---|---|
| ADR | Architecture decision record: context, options, decision, rationale, consequences, risks, and review triggers |
| Bronze / silver / gold | Common data-refinement stages, with purpose and promotion criteria defined by the design |
| Capability | A thing the platform must be able to do, independent of a specific product |
| Catalog | A discovery/navigation capability for data assets and their context; exact implementation varies |
| Control plane | Services that manage, coordinate, configure, or govern platform operations |
| Data product | An owned data interface for defined consumers with a documented contract and appropriate expectations |
| DX | Developer/developer-user experience: how effectively users discover, build, operate, and get support for platform work |
| Error budget | The tolerated amount of SLO failure over a defined window, where an organization uses an error-budget policy |
| Golden path | A supported workflow/template that makes the safe, repeatable way the easiest way |
| Logical architecture | Vendor-neutral capabilities and relationships, distinct from a physical deployment/product map |
| Metastore | A service/store commonly holding technical metadata such as table and schema definitions for engines |
| Metadata | Data describing assets and their meaning, structure, ownership, lineage, policy, quality, or operation |
| Noisy neighbour | A tenant/workload that consumes shared resources and degrades others' service |
| Output metric | A measure of delivered activity or artifact, such as pipelines created |
| Outcome metric | A measure of user or business effect, such as time to a trusted decision |
| Quarantine | A controlled location/state for rejected or suspicious data, with reasons and recovery rules |
| SLA | Service-level agreement; a formal agreement whose commitments and remedies depend on its terms |
| SLI | Service-level indicator: a defined measure of observed service behaviour |
| SLO | Service-level objective: a target for an SLI over a stated measurement window |
| Tenant boundary | An enforced boundary for data, access, resources, administration, or failure scope for a tenant |
| Zone | A platform area with a defined purpose in the data lifecycle, such as ingestion or consumption |

---

## 27. Assessment integrity and use limitations

This is a vendor-neutral learning assessment based on the module roadmap. It is not a certification exam, compliance attestation, security sign-off, or substitute for workload measurements and production threat modeling. The fictional Northbridge scenarios and numeric examples are illustrative. A real platform's target values, regulatory obligations, isolation guarantees, and support commitments must be derived from actual requirements, implementation behaviour, evidence, and accountable review.


## 28. Assessment audit register and re-audit status

This register records defects found in the assessment structure and scoring guidance during the audit. “Resolved” means the correction is present in this revised file; it does not imply an independent human assessment has been performed.

**Source inventory used for this audit:** the available project-tree file was `Roadmap_ptree(20261020-122943).md`, and the available module roadmap was `roadmap-Enterprise-Data-Platform-and-Lakehouse-Architecture(1).md`. All eight lesson files named in that tree were present and checked for topic terminology, learning outcomes, examples, and section-level alignment. The exact unversioned basenames `Roadmap_ptree.md` and `roadmap-Enterprise-Data-Platform-and-Lakehouse-Architecture.md` were not present in the working directory; the available variants were used instead.

| Finding ID | Question / area | Topic mapping | Skill level | Defect | Severity | Required correction | Final status |
|---|---|---|---|---|---|---|---|
| AUD-01 | §2 topic-to-question map | Topics 01–08 | All | The summary map grouped question IDs and broad skills but did not map each question to a specific skill, objective, and source evidence. | Major | Add §2.1 question-level traceability for all 74 numbered questions and five practical exercises, using the available lesson sections and roadmap. | **Resolved** — matrix added; all listed IDs mapped. |
| AUD-02 | §23.1 scoring guidance | Topics 01–08 | Apply / Analyze / Evaluate / Design | The fallback rubric for any application item without a local rubric required “ownership/trade-offs,” which is not relevant to every explanation, classification, or calculation and could make scoring arbitrary. | Major | Replace the single fallback with task-appropriate three-point templates for explanation/comparison, calculation, classification, diagnosis, and design. | **Resolved** — scoring templates added. |
| AUD-03 | T07-A2 answer-key rubric | Topic 07 | Analyze | The 12-point rubric did not state an unambiguous point allocation and did not clearly show how the six required cases were covered. | Minor | Define a 12-point rubric with explicit allocations and require coverage of all six cases while allowing partial credit. | **Resolved** — rubric rewritten and totals 12. |
| AUD-04 | §§23.1, 23.3, 23.4 | Topics 01–08 | Apply / Analyze / Evaluate / Design | Constructed-response partial-credit rules were broad, and the roadmap's 85% threshold lacked an explicit denominator once checkpoints and the integrated case were added. | Major | Define full/partial/no-credit rules; calculate the readiness score from the eight normalized topic scores (160-point maximum), and report checkpoints/integrated case separately unless weights are declared in advance. | **Resolved** — scoring rules and denominator are explicit. |
| AUD-05 | T02-A2 answer-key rubric | Topic 02 | Design | The rubric rewarded batch/stream convergence even though the prompt specifically asks for a daily-file zone table; this could penalize an answer that correctly stays within scope. | Minor | Replace the criterion with failure/replay handling and make streaming convergence optional only when justified by an explicit assumption. | **Resolved** — rubric aligned to the prompt. |

### Re-audit verification summary

- **Numbered question inventory:** 56 topic-level + 10 checkpoint + 8 integrated-case questions = **74**. Five supplementary practical exercises are separately identified as EX-1–EX-5.
- **Topic coverage:** all eight topics have seven topic-level questions each, plus cross-topic checkpoint/integrated assessment coverage.
- **Answer keys:** all eight topic sections have answer-key entries for F1–F3, A1–A3, and D1; checkpoint A/B have keys and rubrics for all ten questions; integrated-case questions have answer anchors and a 100-point rubric.
- **Scoring arithmetic:** Checkpoint A = 4 + 8 + 8 + 8 + 12 = **40**; Checkpoint B = 4 + 8 + 8 + 8 + 12 = **40**; integrated rubric = 10 + 10 + 10 + 10 + 10 + 10 + 15 + 15 + 10 = **100**; T07-A2 rubric = **12**. Topic scoring normalizes each topic to 20 points, for a fixed **160-point topic-level readiness denominator**. Checkpoints and the integrated assessment remain separately reported unless a weighting policy is declared before the attempt.
- **Numerical examples:** the T07-A3 burst pool is 100 − (5 × 15) = 25 units; simultaneous requests of 3 × 20 = 60 units exceed burst capacity by 35 units. T08-A2 and EX-4 both calculate 0.999 × 0.9995 × 0.9999 × 0.999 ≈ 0.997402, or approximately **99.74%**.
- **Assessment structure:** Checkpoint A covers Topics 01–04; Checkpoint B covers Topics 05–08; the Northbridge integrated case covers the full module and asks for synthesis rather than simply repeating one-topic items.
