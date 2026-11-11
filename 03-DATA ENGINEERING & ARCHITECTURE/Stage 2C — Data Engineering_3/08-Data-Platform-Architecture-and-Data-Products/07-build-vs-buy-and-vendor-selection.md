# Build vs Buy and Vendor Selection
## Stage 2C — Data Engineering_3 · Module 2C.8 · Topic 07

> **Core principle:** choose the operating model that maximises business outcomes under explicit constraints—not the tool with the longest feature list or lowest licence line. The decision is incomplete until it includes people, risk, portability, an exit path, and evidence that could reverse the recommendation.

### Source and scope note

The controlling syllabus is Topic 07 in `roadmap-Data-Platform-Architecture-and-Data-Products.md`; `Roadmap_ptree.md` confirms the target filename and folder. The roadmap explicitly requires four implementation options, core-vs-commodity reasoning, data-stack mapping, TCO, weighted evaluation, a staged selection process, pricing traps, portability/lock-in, vendor and open-source risk, organisational factors, case studies, a 40-source ingestion decision, 1×/5×/10× scenarios, a time-boxed POC, and an ADR. This lesson follows those requirements. Current vendor descriptions are based on official documentation listed in Section 19. All financial inputs and candidate scores in the exercise are **illustrative planning assumptions, not vendor quotations or POC results**.

## 1. Learning objectives

After this lesson, you should be able to:

1. Distinguish custom build, SaaS, self-hosted open source, managed open source, and sensible hybrids.
2. Decide which capabilities differentiate the business and which are commodity infrastructure.
3. Map build/buy choices across ingestion, storage/compute, transformation, orchestration, observability, catalogue, BI, reverse ETL, and ML/data platform capabilities.
4. Calculate comparable one-year and three-year TCO, including engineering labour, on-call, upgrades, training, migration, integration, and exit.
5. Model consumption at 1×, 5×, and 10× without pretending cost scales linearly when pricing tiers or capacity constraints change.
6. Design weighted scorecards with precommitted criteria, evidence quality, uncertainty, and hard gates.
7. Run a time-boxed POC with test data, measurable criteria, and a decision rule.
8. Evaluate portability, open-source governance, vendor viability, security, support, and contractual exit terms.
9. Write and defend an ADR/RFC with alternatives, consequences, owners, review date, and reversal conditions.
10. Explain a recommendation to engineering, finance, security, procurement, and legal stakeholders.

## 2. Prerequisites and terminology

| Term | Meaning |
|---|---|
| Build | Own the implementation and its lifecycle, including design, upgrades, reliability, security, and support. |
| SaaS | Vendor operates the application/service; customer still owns configuration, access policy, integration, data governance, and vendor-risk management. |
| Open source, self-hosted | Use software with an open-source licence and operate the deployment yourself. “Free licence” does not mean zero TCO. |
| Managed open source | A provider operates a service based on open-source software; the service may include proprietary control-plane features or terms. Inspect the actual licence and service contract. |
| TCO | Total cost of ownership over a defined horizon, including recurring costs, one-time implementation, operating effort, risk-adjusted costs where justified, migration, and exit. |
| Fully loaded labour rate | Salary plus employer costs, benefits, equipment, and relevant overhead allocated per productive hour. |
| MAR / credits | Examples of vendor-defined consumption units. Read the precise billing definition; units are not interchangeable across vendors. |
| POC | Proof of concept: a time-boxed experiment testing the riskiest assumptions against pre-agreed success criteria. |
| ADR / RFC | Architecture Decision Record / Request for Comments: durable rationale, alternatives, consequences, ownership, and review conditions. |
| Lock-in | Cost or risk of changing provider, including data export, semantic differences, workflows, staff skills, contracts, and downtime. |
| Bus factor | How many people could maintain a critical system before knowledge concentration becomes an unacceptable risk. |
| SLO / SLA | Service objective measured by the operator / contractual service commitment and remedies. SLA credits rarely make an outage economically whole. |

## 3. Build, buy, open source, and managed options

Four principal options form a continuum. A real platform often combines them.

| Option | You own | Provider/project supplies | Typical advantages | Typical costs/risks |
|---|---|---|---|---|
| Custom build | Design, code, tests, operations, security, roadmap | Infrastructure primitives or libraries | Precise fit, control, differentiated behaviour | Highest ownership burden; key-person risk; long time to value |
| Buy SaaS | Requirements, configuration, access, integration, data lifecycle, contract oversight | Hosted application, updates, operational platform | Fast start; provider handles much routine operations | Usage/seat costs, service limits, vendor dependency, export/egress |
| Open source, self-host | Deployment, upgrades, scaling, security, backups, on-call | Source code and community ecosystem | Control, inspectability, flexibility, possible portability | Operations and integration labour; uneven support; governance/bus-factor risk |
| Managed open source | Configuration, architecture, data governance, contract and exit | Provider operates a service based on an OSS project | Less ops than self-hosting while retaining some ecosystem familiarity | Managed service may diverge from OSS; paid features/terms; migration still costs |

### Sensible combinations

- Buy commodity connectors; custom-build the few sources with unique business semantics.
- Use a managed warehouse but own SQL transformations, data contracts, and quality tests.
- Use open-source Airflow or Dagster with a managed execution/control-plane option when the operating model is acceptable.
- Start with a managed service, then move a stable, high-volume subset to self-hosted tooling only if measured TCO or strategic needs justify it.
- Use a common interface for credentials, lineage, retries, and metrics while allowing provider-specific capabilities where the abstraction would otherwise erase necessary features.

### What is core to the business?

Ask: if this capability became 10× better than competitors', would customers pay, stay, or choose us? Does it encode unique domain knowledge, proprietary algorithms, or product differentiation? If not, it may be commodity work.

A data ingestion engine is usually a means to an end; source-specific normalization, data quality guarantees, semantic models, and customer-facing insights may be differentiating. The answer depends on the business. A company selling ingestion technology itself may rationally build the engine.

**Opportunity cost:** every engineer maintaining commodity infrastructure is unavailable for product features, data products, customer reliability, or revenue-generating work. Compare the value of that displaced work—not just the direct salary against a subscription.

### Team and maturity effects

- A small team without a reliable on-call rotation often benefits from managed services, even if the invoice looks higher.
- A large team with platform/SRE expertise may operate self-hosted OSS efficiently, but only if the work is actually staffed and prioritised.
- A specialist team may build a custom system when the capability is strategic and requirements cannot be met economically by existing products.
- Time pressure favours faster time-to-value, but rushed procurement without a POC can create multi-year lock-in.
- Hiring availability matters: choosing an unfamiliar stack increases training and bus-factor risk. Do not choose technology mainly because it is fashionable or looks good on a résumé (“resume-driven development”).

## 4. Mapping the data stack

The goal is not to choose one vendor for every layer. Evaluate the capability and its interface with adjacent layers.

| Layer | Capability to evaluate | Illustrative candidates | Decision questions |
|---|---|---|---|
| Ingestion / ELT | API/database extraction, incremental sync, schema drift, deletes, retries, connector coverage | Fivetran, Airbyte, dlt, custom code | Are required sources maintained? How are limits, deletes, backfills, and schema changes handled? |
| Storage and compute | Durable storage, query engine, governance, concurrency, workload isolation | Snowflake, BigQuery, Databricks; object storage + open table formats | Workload fit, cost controls, open formats, IAM, regional availability, workload isolation |
| Transformation | SQL/Python transforms, dependency management, testing, incremental models | dbt, warehouse SQL, Spark/Databricks | Can transformations be versioned, tested, and moved? Are semantics portable? |
| Orchestration | Scheduling, dependency graph, retries, backfills, event-driven work | Airflow, Dagster, managed orchestration | Who operates scheduler/workers? How are secrets, deployment, state, and incident response handled? |
| Quality / observability | Freshness, volume, schema, anomaly detection, lineage, incident triage | Native warehouse checks, dbt tests, observability products, custom metrics | Signal quality, alert fatigue, ownership, evidence retention, metric cost |
| Catalogue / governance | Discovery, ownership, classification, policy, lineage, glossary | DataHub, OpenMetadata, cloud-native catalogues, commercial tools | Metadata ingestion, access integration, sensitive metadata, adoption and upkeep |
| BI / analytics | Semantic layer, dashboards, exploration, access controls | Looker, Tableau, Power BI, Superset, Metabase | Metric consistency, user experience, embedding, governance, seat pricing |
| Reverse ETL / activation | Sync curated data to CRM/marketing/product tools | Fivetran Activations, Hightouch, Census-like capabilities, custom APIs | Row/credit pricing, destination limits, retries, idempotency, auditability |
| Streaming / event platform | Durable event log, schema evolution, replay, consumer isolation, cross-region replication | Apache Kafka, Confluent, Amazon MSK, Redpanda | Throughput/latency, partitioning, retention, operations, replication semantics, support and cloud coupling |
| ML/data platform | Feature pipelines, experiment tracking, model serving, governance | Databricks, cloud ML platforms, MLflow-based stacks, custom platform services | Integration with data controls, workload economics, reproducibility, portability |

These names are examples of categories, not a ranking. A warehouse, lakehouse, orchestration engine, connector service, and BI tool solve different problems. Avoid a false “all-in-one” comparison unless the requirements genuinely overlap.

### Decision patterns for the other roadmap examples

| Decision area | Candidates to compare | Evidence that should drive the decision |
|---|---|---|
| Warehouse / lakehouse | Snowflake, BigQuery, Databricks | Replay the same representative SQL/ELT, concurrency, governance, and ML-adjacent workloads; measure cost under realistic schedules; compare data gravity, cloud/region constraints, operational skills, and exit path. Do not compare headline compute prices without matching workload and billing units. |
| Orchestration | Airflow, Dagster, managed orchestration | Test dependency semantics, backfills, asset/data-product visibility, deployment model, secrets, observability, upgrades, and operator on-call burden. DAG and asset models are not automatically interchangeable; managed operation reduces some toil but does not remove workflow ownership. |
| Streaming / event platform | Apache Kafka, Confluent, Amazon MSK, Redpanda | Test throughput, tail latency, retention/replay, schema governance, connector ecosystem, security, replication/failover requirements, and operational effort. Treat managed services and Kafka-compatible products as distinct offerings; validate protocol/API and feature compatibility rather than assuming parity. |

These are decision frameworks, not benchmark claims or product rankings. Use the same workload, acceptance thresholds, dated vendor evidence, and cost horizon for each candidate. The 40-source ingestion case study below is the only worked numerical procurement scenario in this lesson.

## 5. Requirements and candidate selection

Follow the roadmap's sequence:

**Requirements → Long List → Short List → Weighted Scorecard → Proof of Concept → Reference Checks → Negotiation**

### Step 1: Define requirements

Separate:
- **Business outcomes:** faster time to insight, fewer incidents, support for a product launch, lower operational burden.
- **Functional requirements:** source coverage, incremental extraction, deletes, replay, schema evolution, destinations, API support.
- **Non-functional requirements:** freshness, throughput, availability, recovery, security, region, audit, support response.
- **Constraints:** deadline, budget, headcount, cloud footprint, approved vendors, legal obligations.
- **Non-negotiable gates:** e.g., supported deployment region, SSO/RBAC, data-processing terms, export rights, required connector semantics.

Requirements should be testable. “Scalable” is not a requirement; “complete 40 source syncs within a 4-hour freshness objective at the expected 5× load without exceeding source API limits” is closer.

### Step 2: Establish differentiating capability

Identify the work that creates customer value and the work that is a repeated operational burden. Be explicit about the opportunity cost of maintaining the latter.

### Step 3: Build the long list

Include candidates from all four options, plus a hybrid. Gather official documentation, architecture fit, licensing, service region, security materials, integration effort, and pricing model. Avoid selecting only products the team already knows.

### Step 4: Shortlist against hard gates

Reject options that fail a non-negotiable requirement before weighted scoring. A high average cannot compensate for an unacceptable security or legal failure.

### Step 5: Score evidence, not vibes

Set weights before scoring. Use a consistent scale such as 1 = materially fails, 2 = major gaps, 3 = meets minimum, 4 = strong evidence, 5 = exceeds requirement with evidence. Mark unknowns as unknown; do not quietly score unknown as 3. A numerical result is a discussion aid, not an objective truth.

### Step 6: POC, references, and negotiation

Test the leading candidates with identical representative data and the same success criteria. Reference-check customers with similar source mix, scale, governance, and operating model. Negotiate usage definitions, overages, support, security, renewal increases, export, deletion, transition assistance, and termination rights.

### Step 7: Record and revisit

Write an ADR/RFC, name a decision owner, record rejected alternatives, and define evidence that would reverse the decision. Set a review date and triggers such as sustained usage growth, support failure, a major licence change, or a new residency requirement.

## 6. TCO methodology

Compare options over the same horizon, workload, currency, labour assumptions, and service level. A low invoice can hide substantial engineering and operational effort.

### Cost categories

**Recurring costs**
- Licence, subscription, consumption, and support contracts.
- Infrastructure, storage, compute, networking, observability, backup.
- Engineering maintenance, connector fixes, upgrades, security patching.
- On-call and incident response.
- Training/enablement refresh and operational administration.
- Integration and data movement, including egress and API costs.

**One-time or horizon-specific costs**
- Discovery, implementation, integration, security review, and rollout.
- Migration/backfill and parallel running.
- Training during adoption.
- Replacement/exit at the end of the horizon.
- Decommissioning, export, reconciliation, and transition support.

### Formula

For option \(o\), horizon \(H\) years, and usage multiplier \(m\):

\[
TCO(o,H,m) =
I_o + M_o + X_o +
\sum_{y=1}^{H}\left(V_{o,y}(m)+L_{o,y}(m)\right)
\]

Where:
- \(I\): initial implementation/integration cost.
- \(M\): migration/backfill cost.
- \(X\): exit/replacement cost assumed at the end of the evaluated horizon.
- \(V\): recurring vendor and infrastructure cost.
- \(L\): recurring labour, including maintenance, upgrades, training, and on-call.

Use either a fully loaded hourly labour rate or role-specific rates consistently. In a more advanced financial model, discount cash flows, account for inflation/contract escalators, and model probability-weighted risks. Do not add a vague “risk premium” without explaining its probability and impact.

### One-year versus three-year interpretation

The one-year model includes initial setup/migration and assumes exit at the end of year 1. The three-year model includes the same initial costs once, three years of recurring costs, and exit at the end of year 3. This is a conservative lifecycle comparison, not a claim that every company will replace the tool at those dates. If the likely decision is to continue past the horizon, also show TCO without terminal exit and report exit cost separately.

### Labour is real cost

For each option, estimate hours for:
- Initial build/configuration and integration.
- Connector development and source API changes.
- On-call and incident response.
- Upgrade, patching, dependency and runtime maintenance.
- Security reviews, access control, audit, and compliance evidence.
- Training, documentation, hiring/onboarding, and knowledge transfer.
- Migration, parallel run, reconciliation, and exit.

Use a range when uncertainty is high. Example: 300–500 engineering hours is more honest than 417.3 hours if there is no evidence for that precision.

## 7. Pricing models and cost traps

| Model | Typical unit | Trap to test |
|---|---|---|
| Per-seat | Named or active user | More analysts, service accounts, or external users can raise cost; confirm definition of billable seat. |
| Per-row / MAR | Distinct active rows under vendor-defined rules | Initial loads, re-syncs, deletes, activations, duplicate destinations, and connection-level counting may affect billing differently. |
| Credits / consumption | Vendor-defined credits | Credit conversion, included credits, minimums, and overages can change; do not compare credits across providers. |
| Capacity / compute | Worker, slot, warehouse, node, or compute unit | Idle capacity, concurrency, autoscaling, and minimum runtime may dominate. |
| Committed use | Minimum annual/monthly spend | Discounts may trade flexibility for stranded commitment or overage. |
| Egress / data movement | GB, requests, cross-region transfers | Replication, backfills, retries, and migration may create one-off spikes. |
| Connector / source minimum | Per connection/source or plan | 40 low-volume sources can cost more than a single aggregate usage estimate suggests. |
| Support tier | SLA / response window / named support | A cheaper plan may omit the response times, escalation, or recovery help the business needs. |

Official pricing pages are dynamic and commercial terms vary by plan, region, contract, and date. No vendor price is an input to the TCO model. As checked on 2026-10-19, Fivetran documents connection/activation usage in Monthly Active Rows (MAR), counted under specific connection/table/destination rules, and separately measures eligible transformation usage by successful monthly model runs ([MAR definition](https://fivetran.com/docs/getting-started/pricing), [transformation usage](https://fivetran.com/docs/core-concepts/usage-based-pricing/transformations-pricing)). Airbyte currently describes cloud plans with volume/credit-based options and capacity-based plans for some higher-scale offerings; Airbyte Core is the self-managed open-source candidate, not a currently sold Self-Managed Enterprise plan ([pricing](https://airbyte.com/pricing), [deployment documentation](https://docs.airbyte.com/platform/deploying-airbyte), [self-managed enterprise notice](https://docs.airbyte.com/platform/enterprise-setup)). Verify the exact product, licence, plan, source support, quote, and billing unit at procurement time.

### Growth modelling

Run 1×, 5×, and 10× usage. Do not assume every cost scales linearly:
- Usage fees may follow tiers, minimum charges, or volume discounts.
- Infrastructure may scale in steps, require new clusters, or hit capacity ceilings.
- Labour often has fixed and step-function components; 10× volume may require architecture changes, not 10× headcount.
- Egress/backfill costs may be episodic rather than monthly recurring.
- Vendor commitment can make 1× expensive and 10× comparatively attractive—or overage can reverse that.

In the exercise, vendor/infra usage components scale linearly by design so the formulas are auditable. That is a **scenario assumption**, not a prediction of any vendor's actual invoice. The model deliberately does not use current list prices.

## 8. Weighted evaluation scorecards

A weighted score is:

\[
Score(o) = \frac{\sum_i w_i s_{o,i}}{\sum_i w_i}
\]

where \(w_i\) is the criterion weight and \(s_{o,i}\) is the candidate score on a common scale. With weights summing to 100 and scores from 1 to 5, the result remains between 1 and 5.

### Example weights for managed ingestion versus alternatives

| Criterion | Weight | What evidence looks like |
|---|---:|---|
| Functionality/source coverage | 18 | Connector support matrix; test required objects, deletes, incremental sync, backfill |
| Scalability | 10 | POC at target and stress volume; documented limits and architecture |
| Security/compliance | 15 | Security docs, DPA, SSO/RBAC test, audit evidence, threat review |
| Integration | 12 | Destination, orchestration, secrets, network, CI/CD and lineage integration |
| Operability | 14 | Alerting, retries, replay, upgrade burden, incident workflow, on-call estimate |
| Ecosystem | 5 | Skills, integrations, community, hiring pool |
| Support | 7 | Contractual response/escalation, support references |
| Roadmap/viability | 5 | Release cadence, public roadmap, governance/financial signals |
| Lock-in/portability | 7 | Export formats, configuration/code export, destination neutrality, tested exit |
| Price predictability | 7 | Written quote, usage estimator, caps/alerts, overage/renewal terms |
| **Total** | **100** | |

### Why the example scores look this way (hypotheses only)

These are deliberately provisional priors to demonstrate the method; they are **not findings about the named vendors**. They must be replaced or revised after dated evidence, POC observations, and references. The rationale behind the teaching scores is:

| Candidate | Main assumptions behind the illustrative scores | Evidence that could change the scores |
|---|---|---|
| Fivetran managed ingestion | Higher expected operability and broad standard-source coverage; lower expected portability and price predictability due to service-specific state and usage billing | Inventory all 40 sources/objects, validate deletes/backfills, export and migration test, billing estimator, written quote, support references, security/legal review |
| Airbyte Core self-managed | Greater operational control and potentially more predictable licence economics, offset by team-owned deployment, upgrades, scaling, and support; exact connector coverage is unverified | Test exact Core version/connectors, cluster capacity, upgrade/recovery workflow, staffing/on-call hours, security hardening, licence and maintainer review |
| Custom dlt-based ingestion | High source-specific control and code ownership, offset by implementation effort, custom connector coverage, and ongoing maintenance/on-call burden | Measure engineering hours across six representative sources, seeded failures, replay/backfill, security review, production support estimate, and migration/export test |

The rationale is intentionally qualitative and conditional. If a requirement or evidence item is unknown, record it as **unknown** rather than presenting the score as fact. Security, legal, correctness, source coverage, recovery, and exit remain hard gates; a weighted score cannot clear them.

### Avoid false precision

- Score only after criteria/weights and gates are agreed.
- Record evidence URL, date, evaluator, confidence, and open questions per score.
- Distinguish vendor claims, documentation, POC observations, reference statements, and assumptions.
- Use score ranges or confidence labels for uncertain items.
- Run sensitivity analysis: does a reasonable weight change reverse the winner?
- A high score cannot override a failed legal/security gate.
- Record the decision narrative separately from the arithmetic.

The project includes a named candidate scorecard for Fivetran managed ingestion, Airbyte Core self-managed, and custom dlt-based ingestion. The scores are teaching hypotheses with qualitative rationale, not vendor rankings or measured findings. The TCO model remains separate and uses generic cost archetypes because no vendor quotes or POC measurements are available.

## 9. Proof-of-concept design

A POC should answer a small number of high-risk questions, not reproduce an entire production platform.

### POC brief

- **Duration:** 10 business days, time-boxed.
- **Candidates:** Fivetran managed ingestion, Airbyte Core self-managed, and custom dlt-based ingestion. Confirm the exact plan/product, version, licence, and source coverage before testing; do not treat Airbyte Cloud and Airbyte Core as equivalent.
- **Dataset:** same 6 representative SaaS sources from the 40-source inventory; include one high-volume, one rate-limited, one nested API, one source with deletes, one with schema drift, and one with poor/unstable API behaviour.
- **Destination:** same non-production warehouse/schema and same access controls.
- **Workload:** realistic incremental updates, one backfill, a simulated API rate limit, a schema change, and a controlled credential rotation.
- **Evidence capture:** versioned configuration, run logs, timings, error categories, row counts/checksums, resource use, operator time, and vendor support interactions.
- **Not a production result:** no POC was executed for this educational artifact. The project supplies a plan and a results template, not fabricated observations.

### Success criteria and decision rule

1. **Correctness:** 100% of agreed test records reconcile by key and expected deletes/updates; no silent loss or duplicate business keys.
2. **Freshness:** 95% of scheduled runs complete within the agreed 4-hour freshness window on the POC workload.
3. **Recovery:** transient failure resumes without manual state repair; one backfill completes and is reconcilable.
4. **Schema change:** documented behaviour; breaking change must alert or fail visibly rather than silently corrupt data.
5. **Security:** credentials are stored in approved secret management; least-privilege access and audit are demonstrated.
6. **Operations:** an engineer unfamiliar with the implementation can triage a seeded failure from runbook and logs in under 30 minutes.
7. **Cost model:** produce a vendor quote or usage estimate using the same source inventory and state the uncertain billing drivers.
8. **Exit:** export a representative source's data and configuration; document which parts are not portable.

**Decision rule:** a candidate failing correctness or security is disqualified. Among candidates passing all hard gates and freshness/operability thresholds, compare TCO and documented residual risks. Quantify risk-adjusted costs only when defensible probability/impact inputs exist; the current model does not calculate a risk premium. If no candidate passes, extend only the specific failed test or redesign requirements; do not select the highest weighted score by default.

### Results table template

| Test | Fivetran managed | Airbyte Core self-managed | Custom dlt-based | Evidence status |
|---|---|---|---|---|
| Correctness/reconciliation | Not run | Not run | Not run | POC required |
| Freshness objective | Not run | Not run | Not run | POC required |
| Rate-limit recovery | Not run | Not run | Not run | POC required |
| Schema drift behaviour | Not run | Not run | Not run | POC required |
| Operator triage time | Not run | Not run | Not run | POC required |
| Quote/usage estimate | Request quote | Infra estimate | Infra estimate | Not priced here |
| Export/exit exercise | Not run | Not run | Not run | POC required |

## 10. Lock-in and portability

Portability is a design property with a price—not an all-or-nothing label.

### Useful portability levers

- **Open data formats:** Parquet for columnar files; Apache Iceberg for table metadata/specification and interoperability across supporting engines. An open format does not make every engine feature, catalog, security policy, or workload portable.
- **Standard SQL:** keep core transformations understandable and testable; warehouses differ in SQL dialects, semi-structured types, UDFs, performance behaviour, and security semantics.
- **Portable orchestration:** separate business logic from scheduler-specific glue where it pays off. Airflow DAGs and Dagster definitions are not interchangeable just because both orchestrate work.
- **Configuration and code export:** retain source inventories, connector settings, schema mappings, transformation SQL, and operational runbooks in version control, with secrets excluded.
- **Stable internal contracts:** downstream consumers depend on versioned data contracts and semantic outputs rather than vendor-specific implementation details.
- **Regular export tests:** test actual data, metadata, history, deletes, and restore—not merely a contractual promise.

### Abstraction layers: benefit versus cost

An abstraction may reduce switching costs when it isolates a stable concept used across many providers. It also creates code, testing, documentation, feature-parity gaps, and a second API to maintain. Prematurely abstracting every connector behind a lowest-common-denominator interface can remove important source-specific capabilities while still failing to hide the differences that matter.

Use a thin adapter for genuinely repeated behaviour—credentials, run IDs, metrics, retry classification, lineage—while exposing vendor-specific capabilities explicitly. Estimate abstraction maintenance in TCO and delete it if it has no consumers or measurable portability benefit.

### Contract terms to negotiate

- Data ownership and export format, frequency, scope, and fees.
- Termination assistance, transition period, and deletion certification.
- SLA definition, exclusions, service credits, and escalation.
- Security incident notification, audit rights, subprocessor changes, residency, and DPA.
- Renewal uplift, minimum spend, overage alerts, consumption measurement, and price-change notice.
- Access to logs, run history, schema/configuration, and lineage at exit.
- Backups and deletion timelines after termination.

Service credits are not a substitute for an operational workaround or recovery plan; they are often capped and may not cover lost business value.

## 11. Security, vendor, and open-source risks

### Vendor risks

Review financial viability, ownership/acquisition signals, release and incident history, support quality, roadmap fit, regional footprint, subprocessors, security practices, and the ability to export data. A contract and a SOC report do not eliminate implementation risk; validate how the product is configured and used.

Security evaluation should include data classification, encryption, IAM/SSO/RBAC, secret handling, network boundaries, audit logs, incident notification, vulnerability management, backup/deletion, data processing terms, and support access. Finance should review committed spend and renewal terms; legal/privacy should review data rights and processing terms; security should approve controls; engineering should own operational fit.

### Open-source risks

- **Governance:** who accepts changes, releases security fixes, and decides direction?
- **Maintainer concentration / bus factor:** are critical releases dependent on one or two people?
- **Licence:** distinguish an open-source licence from source-available or commercial terms. Review dependency licences and redistribution/hosting obligations.
- **Relicensing:** projects can change licence for future versions or surrounding products. Assess the exact release and dependency tree, not rumours.
- **Security response:** vulnerability disclosure, patch cadence, dependency scanning, signed releases, provenance, and support availability.
- **Managed alternative:** may reduce operational burden but changes cost, control, and exit dynamics.

Self-hosting means your team is responsible for upgrades, availability, backup/restore, scaling, patching, monitoring, incident response, and often 24×7 coverage. Community support is not an SLA.

### Risk register

For each material risk, document probability, impact, detection, mitigation, owner, residual risk, and trigger. Avoid false numerical precision; a qualitative High/Medium/Low rating is often more defensible than invented percentages. Where expected monetary loss is used, state the evidence behind probability and impact.

## 12. Exit planning

Exit planning starts before contract signature. Define a “minimum viable exit” that the team can actually execute.

1. Inventory all sources, destinations, schemas, transformations, jobs, credentials, consumers, and dependencies.
2. Export representative and full data with schema, keys, timestamps, deletes/tombstones, and checksums.
3. Export configuration and runbook state without secrets; store secrets in the target's approved secret manager.
4. Rebuild target connectivity and access policies; verify data classification and retention.
5. Run parallel ingestion, reconcile row counts/checksums, compare downstream outputs, and validate freshness.
6. Cut over using a documented freeze/CDC/replay plan; define rollback and who can declare success.
7. Reconcile late-arriving events, duplicates, deletes, and historical backfills.
8. Terminate service, revoke credentials, verify provider deletion timelines, and preserve legally required audit records.
9. Record actual migration labour, downtime, data gaps, and surprises to improve the next decision.

Exit cost is not only “write a new connector.” It includes contract overlap, source API quotas, destination changes, semantic differences, data export/egress, consumer testing, migration failures, and temporary double-running.

## 13. Worked 40-source ingestion case study

### Problem statement

A B2B analytics company must ingest data from **40 SaaS sources** into its existing cloud warehouse. It needs daily/intraday incremental sync, schema-change visibility, backfill, retries, source-level observability, and a predictable support model. The team has 3 data engineers, one shared platform/SRE resource, and limited appetite for 24×7 connector operations. Some sources have rate limits and nested API responses.

### Non-negotiable gates

- Required source coverage or a documented plan for unsupported sources.
- Secure credential storage, least privilege, audit, and approved data-processing terms.
- Correct incremental sync/update/delete semantics for agreed source objects.
- Visible failures and recoverable backfills.
- Export path and termination/deletion terms acceptable to legal/security.
- Destination, region, and network integration compatible with policy.

### Candidate approaches

1. **Fivetran managed ingestion** — candidate for reducing routine connector operations. Verify exact source/object coverage, delete and backfill semantics, region, plan, and written quote.
2. **Airbyte Core self-managed** — candidate for more deployment control, with the team owning Kubernetes/host operations, upgrades, scaling, security, and incident response. Do not assume Airbyte Cloud pricing or features apply to Airbyte Core.
3. **Custom dlt-based ingestion** — build selected source pipelines using the dlt open-source Python loading library plus source-specific code. The team owns the connectors and production operations; dlt is not itself a full managed connector service. dltHub is a separate managed offering.

These are candidates, not claims that all 40 sources are supported. Connector coverage and required semantics must be checked against the exact product/version and current commercial offer. The TCO figures below remain generic archetypes, not prices for these named candidates.

### Initial recommendation

**Shortlist Fivetran managed ingestion and Airbyte Core self-managed, with custom dlt-based ingestion as a targeted alternative for unsupported or strategically unique sources.** Do not commit to a vendor from the illustrative scorecard. Run the 10-business-day POC and obtain written quotes. If the managed candidate passes correctness, security, source-coverage, recovery, and exit gates and the quoted three-year TCO remains within budget, it is the provisional choice because the team has limited on-call capacity and ingestion is not assumed to be the product differentiator.

This is a conditional decision. If managed source coverage is poor, its usage economics become unacceptable, or security/legal gates fail, re-score using evidence and consider a hybrid: managed connectors for common sources and custom/dlt-based connectors for the remainder.

## 14. TCO model and growth scenarios

The project at `experiments/07_build_vs_buy/` contains a runnable Python model. It calculates one-time implementation, migration, and training; recurring vendor, infrastructure, data movement/egress, and labour; and terminal exit cost. Every input is in `assumptions.json`. Inputs are explicit illustrative planning assumptions, not vendor quotes or measured observations.

### Example input assumptions (USD)

- Fully loaded engineering labour: **$125/hour**.
- Usage multipliers: **1×, 5×, 10×**; horizons: **1 year and 3 years**.
- Vendor usage, ingestion infrastructure, shared destination/storage/observability, and egress scale linearly with usage in this baseline. This is a modelling simplification, not a prediction of actual billing or capacity.
- **Managed SaaS archetype:** $48,000/year base vendor assumption + $24,000/year variable vendor usage at 1×; $0 incremental ingestion infrastructure; $18,000/year common destination/storage/observability; $6,000/year egress; 400 initial engineering hours; 240 maintenance/operations, 100 on-call, 40 upgrade, and 24 training-refresh hours per year; 40 one-time training hours; 100 migration hours; 200 terminal-exit hours.
- **Self-hosted OSS archetype:** $10,000/year support/tooling assumption (not a licence fee) + $30,000/year ingestion infrastructure + $18,000/year common destination/storage/observability + $8,000/year egress at 1×; 900 initial hours; 600 maintenance/operations, 240 on-call, 180 upgrade, and 40 training-refresh hours per year; 80 one-time training hours; 160 migration hours; 400 terminal-exit hours. The assumed OSS licence cost is $0, but operating/support costs are not zero.
- **Custom dlt-based ingestion archetype:** $0 assumed library licence cost + $22,000/year ingestion infrastructure + $18,000/year common destination/storage/observability + $5,000/year egress at 1×; 1,200 initial hours; 720 maintenance/operations, 300 on-call, 240 upgrade, and 32 training-refresh hours per year; 100 one-time training hours; 200 migration hours; 600 terminal-exit hours.

The model keeps one-time training separate from recurring training refresh to avoid omission or double counting. Egress is a separate line item and must not also be included in the infrastructure input. It assumes annual labour hours remain constant across usage multipliers; this is a known limitation. A production estimate should add staffing/capacity step functions when volume increases support, concurrency, incident, or upgrade burden.

### Formula and accounting rules

For option \(o\), horizon \(H\) years, and usage multiplier \(m\):

\[
TCO(o,H,m)=I_o+M_o+T_o+X_o+\sum_{y=1}^{H}[V_{o,y}(m)+F_{o,y}(m)+E_{o,y}(m)+L_{o,y}]
\]

Where \(I\) is initial implementation/integration; \(M\) is migration/backfill; \(T\) is one-time training; \(X\) is terminal exit; \(V\) is vendor fees; \(F\) is infrastructure and shared destination/storage/observability; \(E\) is data movement/egress; and \(L\) is recurring labour, including maintenance, on-call, upgrades, and training refresh. The model uses a constant fully loaded hourly rate and does not discount cash flows, model inflation, or add unsupported probability-weighted risk costs. These should be added for a real investment case where material.

The one-year model includes one year of recurring costs and terminal exit at the end of year 1. The three-year model includes the same one-time costs once, three years of recurring costs, and terminal exit at the end of year 3. This deliberately exposes exit exposure; it does not predict that a company will actually replace the service at that time. `operating_tco_excluding_exit` is also emitted by the code.

### Example model outputs

These values were generated by executing the bundled Python model after adding explicit egress and recurring training-refresh inputs. USD amounts are illustrative and include terminal exit cost at the end of the horizon.

**One-year TCO including terminal exit**

| Candidate archetype | 1× usage | 5× usage | 10× usage |
|---|---:|---:|---:|
| Managed SaaS | $239,000 | $431,000 | $671,000 |
| Self-hosted OSS | $391,000 | $615,000 | $895,000 |
| Custom dlt-based | $469,000 | $649,000 | $874,000 |

**Three-year TCO including terminal exit**

| Candidate archetype | 1× usage | 5× usage | 10× usage |
|---|---:|---:|---:|
| Managed SaaS | $532,000 | $1,108,000 | $1,828,000 |
| Self-hosted OSS | $788,000 | $1,460,000 | $2,300,000 |
| Custom dlt-based | $882,000 | $1,422,000 | $2,097,000 |

**Illustrative weighted-score output (1–5 scale)**

| Candidate | Weighted score | Evidence status | Hard-gate status |
|---|---:|---|---|
| Fivetran managed ingestion | 3.710 | Hypothesis only; not measured | NOT ASSESSED |
| Airbyte Core self-managed | 3.200 | Hypothesis only; not measured | NOT ASSESSED |
| Custom dlt-based ingestion | 2.870 | Hypothesis only; not measured | NOT ASSESSED |

The TCO candidates are **generic cost archetypes** and are not intended to estimate Fivetran, Airbyte, or any named vendor's actual invoice. The scorecard uses those named candidate options but its scores are illustrative hypotheses, not measured vendor facts. The score-generation code explicitly marks every hard gate `NOT_ASSESSED` and every candidate `NO—HARD GATES NOT ASSESSED`; the numerical score is not an eligibility decision. No option can be selected until security/legal, source coverage, correctness, recovery, and exit gates are evidenced.

Under the current illustrative inputs, the managed SaaS archetype has the lowest modelled TCO at all shown horizons/multipliers. At 10× over three years, the custom scenario is less expensive than self-hosted OSS but still more expensive than managed SaaS in this linear-cost model. These rankings are not robust procurement evidence: real quotes, tiering, minimum commitments, source counts, egress, and additional staffing could change the order. The conditional recommendation in the ADR is therefore to shortlist and test, not to sign based on the table.

### How to use sensitivity analysis

- Replace illustrative vendor inputs with written quotes and the vendor's documented billing units.
- Model source count separately from row/data volume: 40 connectors may have minimum charges even when data volume is low.
- Add nonlinear pricing tiers, minimum commitments, capacity step costs, egress bursts, and usage-driven labour changes.
- Run 25–50% lower/higher labour scenarios and double migration/exit costs.
- Compare TCO with and without terminal exit cost; disclose any discount rate or risk-adjusted cost used.
- If a candidate wins only under narrow optimistic assumptions, the decision is not robust.

## 15. Sample ADR

### ADR-007: Managed-first SaaS ingestion with an explicit custom-source escape hatch

**Status:** Proposed, pending POC, security review, and written commercial quote  
**Owner:** Data Platform Lead  
**Stakeholders:** Data Engineering, Platform/SRE, Finance, Security, Legal/Privacy, Analytics consumers  
**Decision date:** 2026-10-19  
**Review date:** 2027-01-19 (or earlier if a trigger fires)

#### Context

We need reliable ingestion from 40 SaaS sources into the existing warehouse. The data engineering team has three engineers and limited on-call capacity. Ingestion is assumed to be commodity infrastructure; source-specific semantics and data products are more likely to differentiate the business. The named shortlist is Fivetran managed ingestion, Airbyte Core self-managed, and a custom dlt-based approach. Cost estimates are generic archetypes, not estimates of those vendors’ actual prices; the scorecard is hypothesis-only and all hard gates remain unassessed pending quote and POC evidence.

#### Decision

Shortlist Fivetran managed ingestion and Airbyte Core self-managed, with custom dlt-based ingestion as a targeted alternative. Prefer managed ingestion only if it passes the POC's correctness, security, source coverage, recovery, and operational gates and the negotiated three-year TCO remains within the approved budget. Use custom dlt-style code only for sources that are unsupported or require semantics that cannot be implemented safely in the managed service. Do not buy before security/legal review and exit clauses are agreed.

#### Alternatives considered

1. **Fivetran managed ingestion:** likely lower routine connector-operations burden; verify exact connectors, deletes/backfills, plan, MAR/other billing definitions, quote, and exit terms.
2. **Airbyte Core self-managed:** more control; team owns deployment, upgrades, scaling, security, and incident response. Do not confuse Airbyte Core with a no-longer-sold self-managed enterprise offer; verify the current product/licence.
3. **Custom dlt-based ingestion:** flexible and inspectable; team owns source code, tests, deployment, monitoring, and on-call. dlt is an OSS loading library, not a complete managed connector service by itself.
4. **Hybrid:** managed connectors for commodity sources and custom/dlt-based code for exceptions; adds two operating paths and requires clear ownership.

#### Consequences

- The platform team must validate connector coverage and document unsupported sources.
- Source inventory, transformation contracts, credentials, and operational runbooks remain in version control.
- POC outputs and vendor quotes replace assumptions in the model before contract approval.
- Exit export and deletion terms are procurement gates, not post-signature tasks.
- A hybrid architecture is permitted only with explicit ownership, alerting, and lifecycle standards.

#### Risks and mitigations

- **Hidden usage cost:** test billing unit with representative data; negotiate caps/alerts and overage terms.
- **Connector gaps:** test all critical source semantics; use a custom escape hatch.
- **Vendor outage:** maintain runbooks, recovery/replay procedures, and destination-side validation.
- **Lock-in:** export data/config and test one source migration annually.
- **Security/privacy gap:** complete threat, DPA, subprocessor, residency, access, and audit reviews.
- **Operational underestimation:** record actual engineer/on-call hours during POC and first quarter.

#### Reversal conditions

Reopen the decision if any occurs:
- POC fails correctness, security, or critical-source coverage.
- Quoted 3-year TCO exceeds approved budget by more than 20% after usage assumptions are reconciled.
- Measured operations/on-call exceeds the model by more than 30% for two consecutive months.
- Vendor fails a material support/SLA obligation or changes pricing/licensing/region terms adversely.
- A residency, data-processing, or customer contract requirement cannot be met.
- Self-hosted/custom alternative demonstrates lower comparable TCO with acceptable documented residual risk and team opportunity cost.

#### Review and evidence

Review by **2027-01-19**. Store source inventory, weights, scores, POC logs, security/legal decisions, written quote, reference-check notes, final TCO, and exit test in `docs/vendor-eval/`. Finance approves the spend; Security and Legal approve their gates; the Data Platform Lead owns operational fit and review.

## 16. Common mistakes and misconceptions

- **“Open source is free.”** Licence cost may be zero; deployment, upgrades, security, support, and on-call are not.
- **“Build is cheaper because there is no licence.”** Engineering and opportunity cost often dominate.
- **“Buy always means less risk.”** It shifts some operational risk but adds vendor, contract, data-processing, and service-dependency risks.
- **“The weighted winner is objectively best.”** Weights and scores encode assumptions; hard gates and decision narrative remain essential.
- **“A POC is a demo.”** A demo proves the happy path; a POC tests the riskiest requirements with failure and recovery cases.
- **“All connectors listed means our sources work.”** Verify exact objects, deletes, rate limits, backfills, schema drift, and support status.
- **“The licence price is TCO.”** Include labour, incidents, training, migration, egress, parallel run, and exit.
- **“A three-year model is precise.”** It is a scenario; expose uncertain assumptions and sensitivity.
- **“An abstraction removes lock-in.”** It may only move lock-in into the abstraction and its feature gaps.
- **“Open format guarantees portability.”** Catalogue, governance, compute semantics, UDFs, history, and operational workflows can remain proprietary.
- **“SLA credits cover the impact.”** They are limited contractual remedies, not business continuity.
- **“A vendor roadmap is a commitment.”** Distinguish public intent from contractual obligation.
- **“Build because the team wants to learn it.”** Learning can be valuable, but must be weighed against delivery, support, and opportunity cost.

## 17. Practice questions with answers

**Q1. When should a team build instead of buy?**  
When the capability creates meaningful differentiation or no existing option meets critical requirements at acceptable TCO/risk, and the organisation can staff its lifecycle.

**Q2. Why can a managed product have lower TCO than open source?**  
Because provider-operated reliability, upgrades, and support can reduce engineering/on-call effort enough to offset licence and usage fees. Prove it with the team's labour and quote assumptions.

**Q3. What is the correct order for vendor selection?**  
Requirements, long list, short list, weighted scorecard, POC with success criteria, reference checks, negotiation, then ADR and review.

**Q4. Why define weights before scoring?**  
To reduce post-hoc manipulation to favour a preferred vendor. Record evidence and confidence per score.

**Q5. What does 10× growth modelling reveal?**  
Potential non-linear pricing, minimum/overage effects, capacity step changes, egress spikes, and labour/operational bottlenecks. A linear scenario is only a baseline assumption.

**Q6. How should open-source risk be assessed?**  
Review licence, project governance, maintainer concentration, release/security response, dependencies, support, and the team's ability to operate or migrate it.

**Q7. Why include exit cost if the organisation plans to stay?**  
It exposes the cost of the option and supports resilience against vendor changes. Show both lifecycle TCO including exit and operating TCO without terminal exit.

**Q8. What evidence should reverse an ADR?**  
Predefined triggers such as failed POC gates, material quote/TCO change, sustained operational burden, contractual breach, security/residency change, or a better-tested alternative.

## 18. Completion checklist

- [ ] I can explain build, SaaS, self-hosted OSS, managed OSS, and hybrid options.
- [ ] I can distinguish business differentiation from commodity engineering.
- [ ] I can map choices across all data-stack layers.
- [ ] I can model 1-year/3-year TCO and 1×/5×/10× usage with people and exit costs.
- [ ] I can explain per-seat, MAR, credits, commitment, egress, and overage traps.
- [ ] I can set gates, criteria, weights, and evidence confidence before scoring.
- [ ] I can write a time-boxed POC with measurable criteria and a decision rule.
- [ ] I can assess portability, contracts, vendor risk, OSS governance, and bus factor.
- [ ] I can defend an ADR to engineering, finance, security, and legal.
- [ ] I can state exactly what evidence would cause the decision to change.

## 19. Verified references and further reading

Vendor-specific descriptions below are intentionally narrow and based on official documentation checked on **2026-10-19** where noted. Product features, plans, pricing, and licence terms change; verify the exact product/version, region, commercial offer, and contract before a decision. The TCO inputs in this lesson are not derived from any of these pricing pages.

1. Fivetran — Usage-Based Pricing / Monthly Active Rows (MAR): https://fivetran.com/docs/getting-started/pricing
2. Fivetran — Transformation usage measured in successful monthly model runs: https://fivetran.com/docs/core-concepts/usage-based-pricing/transformations-pricing
3. Fivetran — Pricing and current plan overview: https://www.fivetran.com/pricing
4. Airbyte — Current pricing plans, including volume/credit and capacity-based plan distinctions: https://airbyte.com/pricing
5. Airbyte — Deployment documentation for self-managed deployments: https://docs.airbyte.com/platform/deploying-airbyte
6. Airbyte — Notice about the no-longer-sold Self-Managed Enterprise offer: https://docs.airbyte.com/platform/enterprise-setup
7. dlt — Official documentation for the open-source Python loading library: https://dlthub.com/docs/intro
8. dlt and dltHub — OSS library versus managed platform: https://dlthub.com/docs/hub/getting-started/oss-and-dlthub
9. Apache Iceberg — Official project: https://iceberg.apache.org/
10. Apache Parquet — Official project: https://parquet.apache.org/
11. Apache Airflow — Official documentation: https://airflow.apache.org/docs/
12. Dagster — Official documentation: https://docs.dagster.io/
13. dbt — Official documentation: https://docs.getdbt.com/
14. Snowflake — Official documentation and pricing entry point: https://docs.snowflake.com/ and https://www.snowflake.com/en/pricing/
15. Google BigQuery — Pricing: https://cloud.google.com/bigquery/pricing
16. Databricks — Pricing: https://www.databricks.com/product/pricing
17. Apache Kafka — Official documentation: https://kafka.apache.org/documentation/
18. Confluent — Official documentation: https://docs.confluent.io/
19. Amazon MSK — Official documentation and pricing entry point: https://docs.aws.amazon.com/msk/ and https://aws.amazon.com/msk/pricing/
20. Redpanda — Official documentation: https://docs.redpanda.com/
21. GitHub — About open-source licences: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-licenses
22. OpenSSF — Scorecard project for open-source supply-chain signals: https://scorecard.dev/
23. NIST — Cybersecurity Supply Chain Risk Management Practices (SP 800-161 Rev. 1): https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final
24. Michael Nygard — Documenting Architecture Decisions (ADR): https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions

### Roadmap alignment

This lesson follows Topic 07's required decision-heavy scope: four sourcing models; core-vs-commodity reasoning; data-stack mapping; TCO; weighted criteria; selection sequence; pricing traps; 10× growth; open formats and abstraction trade-offs; vendor and OSS risks; organisational factors; warehouse/orchestration/ingestion/streaming examples; the 40-source managed-vs-custom exercise; scorecard; TCO model; POC; ADR; review conditions; and common mistakes. The tree confirms the exact target at `Stage 2C — Data Engineering_3/08-Data-Platform-Architecture-and-Data-Products/07-build-vs-buy-and-vendor-selection.md`.
