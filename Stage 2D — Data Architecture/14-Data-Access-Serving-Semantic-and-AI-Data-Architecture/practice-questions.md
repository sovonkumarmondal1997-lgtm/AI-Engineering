# Module 2D.14 — Practice Questions and Readiness Assessment

**Stage:** 2D — Data Architecture  
**Module:** 14 — Data Access, Serving, Semantic and AI Data Architecture  
**Purpose:** Practice, self-assessment, evidence collection, and readiness review before the final project  
**Scenario convention:** Northbridge Bank is fictional. Every organization, record, number, rate, target, and cost in this resource is synthetic and illustrative unless explicitly described as a formula.

> **Source and scope note:** This bank is aligned to the Module 2D.14 roadmap and all eight lesson files. The project tree confirms the expected module structure. The actual module `README.md` and `Projects/14-analytics-and-ai-data-serving-architecture.md` were not available among the inspected files; the roadmap itself says the project file was empty when authored and describes its proposed guide as recommending that ML-feature and RAG components remain optional unless the real project requires them. This bank assesses all eight module outcomes, but it does not make every topic component mandatory in the separate final project. Where a lesson leaves an implementation choice open, state assumptions and justify them rather than inventing a universal rule.

## Contents

- [A. Assessment instructions](#a-assessment-instructions)
  - [Question-to-outcome coverage matrix](#a6-question-to-outcome-coverage-matrix)
  - [Source alignment and limitations](#a7-source-alignment-and-limitations)
- [B. Topic-wise question bank](#b-topic-wise-question-bank)
- [C. Cross-topic integration scenarios](#c-cross-topic-integration-scenarios)
- [D. Answer key and explanations](#d-answer-key-and-explanations)
- [E. Practical assessment and evidence](#e-practical-assessment-and-evidence)
- [F. Scoring and readiness criteria](#f-scoring-and-readiness-criteria)
- [G. Knowledge-gap log](#g-knowledge-gap-log)
- [H. Final module-readiness assessment](#h-final-module-readiness-assessment)

---

# A. Assessment instructions

## A1. How to use the bank

1. **Before a lesson:** skim the beginner questions to identify what you already know and what you need to learn.
2. **After a lesson:** answer that topic's questions without copying from the lesson. Mark any answer that depends on an assumption.
3. **At the end of a topic:** compare your answer with the answer key. Score the answer, record the gap, and revisit the referenced lesson section.
4. **After Topics 1–8:** complete the integrated scenarios. These test whether you can connect requirements, serving patterns, semantics, ML features, retrieval, contracts, caching, and freshness.
5. **Before the final project:** complete the practical evidence tasks and final readiness checklist. A high quiz score alone is not sufficient evidence of design ability.

You do not need prior professional data-architecture experience. Define technical terms when first using them, show calculations step by step, and state assumptions explicitly.

## A2. Question formats and notation

- **MCQ:** choose one best answer unless the question explicitly permits more than one.
- **T/F + justify:** mark true or false and provide a reason; a bare choice earns at most half credit.
- **Short answer / difference:** explain in your own words and give an example.
- **Calculation:** show formula, inputs, units, result, and interpretation.
- **Code/SQL reading:** explain behavior and identify the limitation or defect; do not assume a particular vendor.
- **Scenario/design review:** state constraints, alternatives, decision, trade-offs, failure behavior, security controls, and validation.
- **Practical task:** submit the named artifact and evidence that it meets acceptance criteria.

Difficulty is cumulative: Level 2 assumes the fundamentals in Level 1; Level 3 assumes both and requires defensible decisions under constraints.

## A3. Recording answers and resolving gaps

Use a separate answer document or copy the question IDs into your notes. For every wrong or incomplete answer, log:
- the question and topic;
- the error type (conceptual, technical, calculation, security, or design);
- the underlying cause rather than only the symptom;
- the exact lesson section to revisit;
- a retest date and evidence.

A gap is resolved only when you can answer a parallel question correctly and explain why the tempting incorrect answer fails. For architecture questions, evidence means a coherent diagram, decision matrix, test plan, or other requested deliverable—not merely a confident explanation.

## A4. Evaluating answers fairly

- Objective questions have one keyed answer; distractors are explained.
- Open-ended questions can have multiple valid architectures. Credit a different approach if it meets the stated requirements, explains assumptions and trade-offs, and includes measurable validation.
- Mandatory correctness and safety requirements are not optional: correct metric semantics, point-in-time feature correctness, authorization enforcement, tenant isolation, deletion/revocation handling, and explicit failure behavior must be addressed when relevant.
- Do not assume a particular cloud, database, vector engine, cache, or API framework.
- Numerical targets in scenarios are illustrative requirements, not universal industry standards.

## A5. Recommended review cadence

| Checkpoint | Required activity | Evidence |
|---|---|---|
| After each topic | Answer its six questions; review all missed items | Score and gap-log entries |
| After Topic 2 | Reconcile a metric across two consumers | Metric definition and test |
| After Topics 4–6 | Review feature correctness, pipeline refresh, and permissions | Flow diagrams and negative tests |
| After Topic 8 | Validate cache and freshness calculations | Decision matrix with units and assumptions |
| Before final project | Complete integrated scenarios and practical tasks | Architecture package, ADRs, test plan, readiness checklist |

---


## A6. Question-to-outcome coverage matrix

The roadmap's ten learning outcomes are abbreviated as follows: **O1** consumer needs and analytical serving; **O2** warehouses, marts, and semantic layers; **O3** operational serving and low-latency access; **O4** feature platforms and training-serving consistency; **O5** document ingestion, embeddings, and vector pipelines; **O6** RAG knowledge data and permission-aware retrieval; **O7** data products, API contracts, and consumer expectations; **O8** access patterns, caching, and freshness; **O9** integration into a coherent serving architecture; **O10** justification of architecture decisions using requirements, assumptions, constraints, and trade-offs.

This matrix maps every topic question and cross-topic scenario to its primary roadmap outcomes, difficulty, and format. Some open-ended questions assess more than one outcome; acceptable designs are not limited to the reference answer when they satisfy the stated constraints and safety requirements.

| ID | Topic | Roadmap outcome(s) | Difficulty | Question type |
|---|---|---|---|---|
| T01-B1 | 01 · Analytical serving | O1 | Beginner | MCQ |
| T01-B2 | 01 · Analytical serving | O1, O10 | Beginner | Short answer |
| T01-I1 | 01 · Analytical serving | O1, O3, O8, O10 | Intermediate | Scenario |
| T01-I2 | 01 · Analytical serving | O1, O2, O7 | Intermediate | True/false + justification |
| T01-A1 | 01 · Analytical serving | O1, O2, O3, O7, O8, O9, O10 | Advanced | Design review |
| T01-A2 | 01 · Analytical serving | O1, O3, O7, O8, O9, O10 | Advanced | ADR |
| T02-B1 | 02 · Warehouses/marts/semantics | O2 | Beginner | Explain/difference |
| T02-B2 | 02 · Warehouses/marts/semantics | O2 | Beginner | MCQ |
| T02-I1 | 02 · Warehouses/marts/semantics | O2, O10 | Intermediate | Calculation |
| T02-I2 | 02 · Warehouses/marts/semantics | O2, O10 | Intermediate | Metric-contract design |
| T02-A1 | 02 · Warehouses/marts/semantics | O2, O7, O9, O10 | Advanced | SQL/code review |
| T02-A2 | 02 · Warehouses/marts/semantics | O2, O7, O9, O10 | Advanced | Design review |
| T03-B1 | 03 · Operational serving | O3 | Beginner | Explain/difference |
| T03-B2 | 03 · Operational serving | O3 | Beginner | MCQ |
| T03-I1 | 03 · Operational serving | O3, O10 | Intermediate | Calculation |
| T03-I2 | 03 · Operational serving | O1, O3, O10 | Intermediate | Pattern selection |
| T03-A1 | 03 · Operational serving | O3, O8, O10 | Advanced | Incident review |
| T03-A2 | 03 · Operational serving | O3, O8, O10 | Advanced | Architecture decision |
| T04-B1 | 04 · Feature platforms | O4 | Beginner | Explain/difference |
| T04-B2 | 04 · Feature platforms | O4 | Beginner | True/false + justification |
| T04-I1 | 04 · Feature platforms | O4 | Intermediate | Temporal scenario |
| T04-I2 | 04 · Feature platforms | O4 | Intermediate | Validation plan |
| T04-A1 | 04 · Feature platforms | O3, O4, O10 | Advanced | Failure analysis |
| T04-A2 | 04 · Feature platforms | O3, O4, O7, O8, O10 | Advanced | Architecture design |
| T05-B1 | 05 · Document/vector pipelines | O5 | Beginner | Ordering + validation |
| T05-B2 | 05 · Document/vector pipelines | O5, O6 | Beginner | Short answer |
| T05-I1 | 05 · Document/vector pipelines | O5, O10 | Intermediate | Calculation |
| T05-I2 | 05 · Document/vector pipelines | O5, O10 | Intermediate | Debugging |
| T05-A1 | 05 · Document/vector pipelines | O5, O6, O10 | Advanced | Migration plan |
| T05-A2 | 05 · Document/vector pipelines | O5, O6, O7, O8, O10 | Advanced | Security/freshness review |
| T06-B1 | 06 · RAG/permission-aware retrieval | O6 | Beginner | Explain |
| T06-B2 | 06 · RAG/permission-aware retrieval | O6 | Beginner | MCQ |
| T06-I1 | 06 · RAG/permission-aware retrieval | O5, O6, O8 | Intermediate | Scenario |
| T06-I2 | 06 · RAG/permission-aware retrieval | O6, O7, O8 | Intermediate | Permission test matrix |
| T06-A1 | 06 · RAG/permission-aware retrieval | O6, O10 | Advanced | Threat review |
| T06-A2 | 06 · RAG/permission-aware retrieval | O5, O6, O7, O8, O10 | Advanced | Architecture design |
| T07-B1 | 07 · Data products/contracts | O7 | Beginner | Short answer |
| T07-B2 | 07 · Data products/contracts | O7 | Beginner | MCQ |
| T07-I1 | 07 · Data products/contracts | O2, O6, O7, O10 | Intermediate | Contract design |
| T07-I2 | 07 · Data products/contracts | O2, O7, O10 | Intermediate | Explain/difference |
| T07-A1 | 07 · Data products/contracts | O2, O4, O7, O10 | Advanced | Change review |
| T07-A2 | 07 · Data products/contracts | O7, O9, O10 | Advanced | Operating-model design |
| T08-B1 | 08 · Cache/freshness | O8 | Beginner | MCQ |
| T08-B2 | 08 · Cache/freshness | O8 | Beginner | Explain/difference |
| T08-I1 | 08 · Cache/freshness | O8, O10 | Intermediate | Calculation |
| T08-I2 | 08 · Cache/freshness | O3, O7, O8, O10 | Intermediate | Pattern choice |
| T08-A1 | 08 · Cache/freshness | O3, O7, O8, O10 | Advanced | Pseudocode/incident review |
| T08-A2 | 08 · Cache/freshness | O6, O7, O8, O10 | Advanced | Security/stampede design |
| X1 | Cross-topic: 01, 02, 03, 07, 08 | O1, O2, O3, O7, O8, O9, O10 | Integrated / advanced | Architecture scenario |
| X2 | Cross-topic: 02, 04, 07 | O2, O4, O7, O9, O10 | Integrated / advanced | Metric-reconciliation scenario |
| X3 | Cross-topic: 03, 04, 07, 08 | O3, O4, O7, O8, O9, O10 | Integrated / advanced | Feature-skew scenario |
| X4 | Cross-topic: 05, 06, 07, 08 | O5, O6, O7, O8, O9, O10 | Integrated / advanced | Lifecycle/security scenario |
| X5 | Cross-topic: 05, 06, 07, 08 | O5, O6, O7, O8, O9, O10 | Integrated / advanced | Security/cache scenario |
| X6 | Cross-topic: 02, 04, 06, 07 | O2, O4, O6, O7, O9, O10 | Integrated / advanced | Compatibility/change scenario |
| X7 | Cross-topic: 03, 07, 08 | O3, O7, O8, O9, O10 | Integrated / advanced | Cache incident scenario |
| X8 | Cross-topic: 01–08 | O1–O10 | Integrated / advanced | Integrated architecture scenario |

## A7. Source alignment and limitations

- The audit basis includes the supplied project-tree snapshot `Roadmap_ptree(20261021-002804).md`, the complete module roadmap `roadmap-Data-Access-Serving-Semantic-and-AI-Data-Architecture(2).md`, this question bank, and all eight lesson files named in Section B. The topic questions were checked against the corresponding lesson scope and the roadmap learning outcomes.
- The roadmap's project guide states that `Projects/14-analytics-and-ai-data-serving-architecture.md` was empty when the guide was authored and that its proposed scope is provisional; it specifically says ML-feature and RAG components are optional unless the actual project requires them. The actual project file and module `README.md` were not present among the inspected files. Consequently, the bank tests all eight module outcomes, while final-project scope must follow the project specification once available.
- Numerical examples use synthetic values. The join-fan-out defect in T02-A1 was checked with a synthetic SQLite fixture; the displayed query itself is an illustrative parameterized snippet without its full schema or execution environment. No production API, model, vector index, or serving platform was tested.

# B. Topic-wise question bank

Each topic has two questions at each level, six per topic. The answer key is in Section D. Use the lesson filename listed under each topic as the principal reference.

## Topic 01 — Analytical serving patterns and consumer needs

**Primary lesson:** `01-analytical-serving-patterns-and-consumer-needs.md`  
**Focus:** consumer personas, access patterns, measurable requirements, analytical serving options, concurrency, freshness, governance, workload isolation, cost, and ADRs.

### Level 1 — Beginner

**T01-B1 · MCQ.** A finance analyst needs a reconciled monthly revenue report, while a customer-facing application needs a current balance for one account in tens of milliseconds. What is the best initial architecture conclusion?

A. Use one shared query path for both because the subject area is the same.  
B. Define separate consumer requirements and choose serving paths that fit each workload.  
C. Put both requests against raw files to maximize flexibility.  
D. Cache every result for one hour.

**T01-B2 · Short answer.** Name four requirements you would capture before choosing an analytical serving pattern. Explain why “fast” is not a sufficient requirement.

### Level 2 — Intermediate

**T01-I1 · Scenario.** A dashboard has 400 concurrent users at 09:00, uses a 30-minute-old mart, and runs a costly aggregation. An operational application has a low-latency point lookup requirement. Propose a serving approach for each and list two measurements for each workload.

**T01-I2 · T/F + justify.** “If a data set is governed, it is automatically suitable for every consumer.” State true or false and explain at least two missing dimensions.

### Level 3 — Advanced

**T01-A1 · Design review.** Northbridge Bank wants executive dashboards, analyst ad hoc queries, scheduled regulatory extracts, and embedded operational views over related data. Some consumers require near-current values; others require reconciled month-end results. Produce the structure of a consumer-requirement matrix and explain how you would resolve conflicting freshness, latency, auditability, and cost requirements.

**T01-A2 · ADR.** Write the decision outline for choosing between a shared serving platform and workload-isolated serving paths. Include options, decision drivers, failure blast radius, governance, cost, validation, and review triggers.

## Topic 02 — Warehouses, marts and semantic layers

**Primary lesson:** `02-warehouse-marts-and-semantic-layers.md`  
**Focus:** layer distinctions, grain, facts, dimensions, metric definitions, relationships, aggregation rules, security, lineage, and consistency.

### Level 1 — Beginner

**T02-B1 · Explain the difference.** Distinguish a data warehouse, a data mart, and a semantic layer. State what each does and what it does not necessarily do.

**T02-B2 · MCQ.** A fact table has one row per order line. An analyst joins it to a customer table that has two active rows per customer because of a faulty slowly changing dimension load. Revenue doubles for affected customers. What is the most direct diagnosis?

A. The semantic layer always changes numeric values.  
B. Join fan-out caused by a violated uniqueness/relationship assumption.  
C. Revenue is non-additive by definition.  
D. The dashboard cache has too many entries.

### Level 2 — Intermediate

**T02-I1 · Calculation.** A synthetic `order_line` fact contains 3 lines: order A has 2 lines worth 40 and 60 currency units; order B has 1 line worth 25. Compute total line revenue. If a join duplicates the two rows from order A once each, what incorrect total results? State the grain assumption.

**T02-I2 · Design.** Define a metric contract for “active customers at month end.” Include formula, grain/time boundary, inclusion/exclusion rules, owner, additivity or non-additivity, lineage, and at least two tests.

### Level 3 — Advanced

**T02-A1 · SQL/code reading + debugging.** The dashboard shows revenue of 12.4 million, the API reports 11.8 million, and a model-training extract reports 12.1 million for the same period. Review this simplified, parameterized query. The schema and bind-parameter setup are intentionally omitted; treat it as a diagnostic snippet, not a standalone runnable script:

```sql
SELECT SUM(f.line_amount) AS revenue
FROM order_line f
JOIN customer_dim d
  ON f.customer_id = d.customer_id
WHERE f.order_date >= :period_start
  AND f.order_date < :period_end;
```

Assume `customer_dim` can contain multiple effective-dated rows per customer. Identify the likely defect and explain how you would correct the join and investigate the three totals. Include grain, filters, time zones, late data, snapshots, and semantic versions in your plan.

**T02-A2 · Design review.** Design a governed semantic model used by finance and risk teams with different access rights. Explain how you preserve a common metric definition while enforcing access controls and versioning semantic changes without silently breaking consumers.

## Topic 03 — Operational data serving and low-latency access

**Primary lesson:** `03-operational-data-serving-and-low-latency-access.md`  
**Focus:** OLTP versus OLAP, point lookups, latency budgets, p95/p99, concurrency, throughput, store selection, consistency, materialized views, failure handling, and capacity validation.

### Level 1 — Beginner

**T03-B1 · Difference.** Compare an operational point lookup with an analytical aggregation in terms of access shape, workload, latency expectations, and failure impact.

**T03-B2 · MCQ.** What does p99 latency of 120 ms mean, under the same measurement boundary and observation window?

A. Every request takes exactly 120 ms.  
B. About 99% of measured requests complete in 120 ms or less; about 1% take longer.  
C. The service processes 120 requests per second.  
D. The average latency is 120 ms.

### Level 2 — Intermediate

**T03-I1 · Calculation.** A synthetic service receives 2,400 requests/s. At the busiest point, the average request spends 50 ms in the system. Using Little’s Law \(L = \lambda W\), estimate average in-flight requests. Show units and state why this is not a complete capacity plan.

**T03-I2 · Selection.** A customer application needs key-based reads and updates, while a risk analyst runs broad historical aggregations. Compare suitable serving patterns and explain why routing both workloads to one resource can be risky.

### Level 3 — Advanced

**T03-A1 · Incident review.** Under a traffic spike, p50 remains 20 ms but p99 rises from 80 ms to 1.8 s. The connection pool is saturated and retries increase. Identify likely feedback loops and propose bounded mitigations, instrumentation, and load-test cases.

**T03-A2 · Architecture decision.** Compare a read replica, a serving store populated by CDC, a materialized view, and a cache in front of a store for a consumer needing low latency and explicitly bounded freshness. Define the evidence needed to choose.

## Topic 04 — Feature platforms and training-serving consistency

**Primary lesson:** `04-feature-platforms-and-training-serving-consistency.md`  
**Focus:** offline/online features, definitions, point-in-time correctness, event time, training-serving skew, temporal joins, late data, freshness, and validation.

### Level 1 — Beginner

**T04-B1 · Explain the difference.** What are offline and online features, and why should their definitions remain consistent even when storage and access patterns differ?

**T04-B2 · T/F + justify.** “For a training row dated last Monday, joining to the entity’s latest feature value today is safe because the latest value is the most accurate.” True or false? Explain point-in-time correctness and leakage.

### Level 2 — Intermediate

**T04-I1 · Temporal scenario.** A fraud event occurred at 10:00. A customer-risk feature was updated at 10:05 based on information unavailable at 10:00. Should that feature value be used to reconstruct the 10:00 training example? Explain which timestamps and join conditions matter.

**T04-I2 · Validation plan.** Give four checks for detecting training-serving skew, including at least one point-in-time test, one offline/online parity test, and one freshness or missing-feature check.

### Level 3 — Advanced

**T04-A1 · Failure analysis.** Offline model evaluation is strong, but production precision drops after a streaming feature pipeline changes its window boundary and late-event policy. Design a diagnosis plan covering event time, processing time, windows, late events, default values, versions, and shadow comparison.

**T04-A2 · Architecture design.** Design batch and real-time feature paths for a synthetic fraud model. Include feature definitions, online latency budget, freshness tiers, parity tests, backfill/replay, deletion propagation, ownership, and degraded behavior when an online feature is missing.

## Topic 05 — Document data, embedding and vector pipelines

**Primary lesson:** `05-document-data-embedding-and-vector-pipelines.md`  
**Focus:** ingestion, normalization, chunking, embeddings, vector indexes, metadata, model versions, incremental updates, deletion, idempotency, recovery, and retrieval quality.

### Level 1 — Beginner

**T05-B1 · Ordering.** Put these stages into a sensible document-to-vector pipeline and state one validation for each: index vectors and metadata; ingest source; extract/clean; chunk; embed.

**T05-B2 · Short answer.** Why must a chunk retain source document identity, version, location/section, timestamps, and relevant classification or access metadata?

### Level 2 — Intermediate

**T05-I1 · Calculation.** A synthetic corpus has 40,000 documents and averages 25 chunks/document. Each raw vector has 512 dimensions stored as 4-byte values. Calculate chunk count and raw vector storage in bytes and decimal GB. Exclude index and metadata overhead explicitly.

**T05-I2 · Debugging.** A pipeline retries an embedding job after a worker crash and creates duplicate chunks and vectors. Describe an idempotency key, checkpoint strategy, and reconciliation checks that would prevent or detect duplication.

### Level 3 — Advanced

**T05-A1 · Migration plan.** The embedding model must change for a million-chunk corpus while the service remains available. Design a versioned re-embedding and cutover plan that covers parallel indexes, evaluation, rollback, cost, and deletion of old vectors.

**T05-A2 · Security/freshness review.** A source document is changed, then later deleted or access-revoked, but its chunk remains searchable. Trace the required update and deletion path from source to chunks, embeddings, index, caches, and retrieval metadata. Include measurable validation.

## Topic 06 — RAG knowledge data and permission-aware retrieval

**Primary lesson:** `06-rag-knowledge-data-and-permission-aware-retrieval.md`  
**Focus:** RAG, retrieval patterns, identity, authorization, ACL propagation, revocation, tenant isolation, stale metadata, fail-closed behavior, provenance, and security.

### Level 1 — Beginner

**T06-B1 · Explain.** Describe the RAG flow from user question through retrieval to generated answer. Identify where access control must be enforced.

**T06-B2 · MCQ.** A user lacks permission to read a document. What is the safest default if the authorization service cannot establish whether access is allowed?

A. Return the passage if vector similarity is high.  
B. Return it from cache if another user retrieved it.  
C. Do not disclose the protected content; fail closed or follow an explicitly approved safe degraded path.  
D. Ask the language model whether the user seems trustworthy.

### Level 2 — Intermediate

**T06-I1 · Scenario.** A document ACL changes at 12:00, but the retrieval index receives the update at 12:04. Specify the checks and temporary behavior required to prevent unauthorized retrieval during the propagation window.

**T06-I2 · Design.** Create a permission test matrix covering authorized user, unauthorized user, different tenant, revoked access, deleted document, stale ACL metadata, and authorization-service failure. State the expected outcome for each.

### Level 3 — Advanced

**T06-A1 · Threat review.** A retrieved passage contains instructions telling the assistant to ignore its system rules and disclose another tenant’s data. Explain why retrieved text is untrusted input and specify controls across retrieval filtering, prompt construction, tool authorization, output handling, and audit logging.

**T06-A2 · Architecture design.** Design permission-aware retrieval for multi-tenant policy documents. Include authoritative identity, document/chunk provenance, ACL propagation, revocation and deletion SLOs, fail-closed behavior, tenant isolation, retrieval evaluation, and negative tests. Explain when cross-user result caching should be disabled.

## Topic 07 — Data products, APIs and consumer contracts

**Primary lesson:** `07-data-products-apis-and-consumer-contracts.md`  
**Focus:** product ownership, interface selection, schemas, contracts, API behavior, quality, service objectives, compatibility, versioning, deprecation, tests, and consumer responsibilities.

### Level 1 — Beginner

**T07-B1 · Short answer.** What makes a data product more than a table or endpoint? Name at least four elements of an accountable product.

**T07-B2 · MCQ.** A producer wants to rename a required API field consumed by multiple clients. What is generally the safest migration pattern?

A. Rename it immediately and notify consumers after deployment.  
B. Add a compatible field or version, document deprecation, track consumers, and remove the old field only after the migration policy is satisfied.  
C. Keep the schema but change the field's meaning silently.  
D. Rely on clients to discover the change from production errors.

### Level 2 — Intermediate

**T07-I1 · Contract design.** Define a contract for a synthetic `Customer Exposure Summary` API: required fields, types, currency/time semantics, freshness, quality behavior, authorization, error handling, pagination or response limits, and versioning.

**T07-I2 · Difference.** Distinguish SLI, SLO, and SLA. Give one example of each for an API and explain why a syntactically compatible schema can still be semantically breaking.

### Level 3 — Advanced

**T07-A1 · Change review.** An API adds an optional field, changes a currency field from USD to account-local currency without renaming it, and tightens a quality filter. Classify structural and semantic risks; propose versioning, consumer communication, tests, and rollback criteria.

**T07-A2 · Product operating model.** Design the ownership, consumer registry, quality/lineage, support, versioning, service objectives, and cost-allocation approach for a shared data product with consumers in finance, risk, and ML serving.

## Topic 08 — Access patterns, cache strategy and freshness

**Primary lesson:** `08-access-patterns-cache-strategy-and-freshness.md`  
**Focus:** cache patterns, TTL, invalidation, hit ratio, freshness lag, consistency, stale data, hot keys, stampedes, permission-aware caching, materialization, and freshness validation.

### Level 1 — Beginner

**T08-B1 · MCQ.** A cache receives 8,000 hits and 2,000 misses in the same measurement window. What are the hit and miss ratios?

A. 80% hit, 20% miss.  
B. 20% hit, 80% miss.  
C. 8% hit, 2% miss.  
D. A ratio cannot be calculated without the cache's byte size.

**T08-B2 · Explain the difference.** Distinguish latency, freshness, correctness, and authorization. Give one example where a result is fast but fails another property.

### Level 2 — Intermediate

**T08-I1 · Calculation.** A service receives 2,000 cache lookups/s and has a 0.85 hit ratio. Assuming one backing-store read per miss and no bypasses or retries, calculate miss ratio and backing-store reads/s. State why the estimate may differ from production.

**T08-I2 · Pattern choice.** Compare cache-aside, read-through, write-through, write-behind, and refresh-ahead. Select a reasonable starting pattern for a read-heavy product lookup that can tolerate bounded staleness, and identify required invalidation and failure controls.

### Level 3 — Advanced

**T08-A1 · Code reading + freshness incident.** A source update commits, invalidation is lost, and a delayed replica read repopulates an old cache value. Review this simplified pseudocode:

```text
on_cache_miss(key):
    value = read_replica(key)
    cache.put(key, value, ttl=60 seconds)
    return value
```

Identify at least three correctness/operational weaknesses. Propose versioning, durable invalidation/reconciliation, freshness telemetry, and regression tests. Explain why TTL alone may not enforce the desired source-to-response age.

**T08-A2 · Security/stampede design.** A shared RAG service caches retrieval results by normalized query only. A popular query's cache entry expires and many callers simultaneously miss. Design a safer key and request path; address tenant/permission changes, request coalescing, hot-key load, stale-while-revalidate limits, and source/cache outage behavior.

---

# C. Cross-topic integration scenarios

For each scenario, produce a concise analysis using: **problem → requirements/constraints → options → decision → risks → validation evidence**. The answer key provides reference reasoning, not the only acceptable design.

## X1 — Executive dashboard versus operational application

**Topics:** 01, 02, 03, 07, 08  
**Problem:** The executive dashboard needs reconciled revenue for the prior day. A customer-facing application needs an account-level risk indicator in a low-latency request. Both currently query the same analytical warehouse.

**Constraints (illustrative):**
- Dashboard users accept up to 30 minutes of delay during the business day.
- Application requests target p95 under 100 ms and source-to-response age under 10 seconds.
- Both paths must use governed definitions and tenant/customer access controls.
- Online traffic must not be starved by large dashboard scans.

**Required analysis:** choose serving paths; identify source of truth and metric semantics; define workload isolation; state latency/freshness measurements and failure behavior.

**Deliverables:** consumer matrix, serving diagram, SLO table, and one ADR.

**Evaluation:** separate access patterns justified; target metrics have units and measurement boundaries; shared semantics are preserved; workload isolation and safe degraded behavior are explicit.

## X2 — Metric disagreement across dashboard, API, and model

**Topics:** 02, 04, 07  
**Problem:** The finance dashboard and risk API both report total revenue of 12.4 million, but their product-level breakdowns disagree. The ML extract reports 12.7 million after applying late-arriving adjustments.

**Constraints:** currency is synthetic; the dashboard snapshot was produced at 06:00, the API uses its latest successful refresh, and the ML extract was built at 12:00. Filters, business time zones, FX cutoffs, late data, or metric versions may differ.

**Required analysis:** establish metric definition, grain, time boundary, filters, joins, currency conversion, late-arriving data, snapshot IDs, and semantic version before editing code.

**Deliverables:** discrepancy tree, canonical metric contract, reconciliation SQL/pseudocode, and regression-test plan.

**Evaluation:** do not choose a number by majority vote; isolate the cause; tests prove equivalence or document an intentional difference.

## X3 — Online ML features differ from training features

**Topics:** 03, 04, 07, 08  
**Problem:** Offline model evaluation is good; online fraud decisions degrade after a feature pipeline update.

**Constraints:** events can arrive late; online requests have a latency budget; historical training rows must not see future information.

**Required analysis:** compare feature definitions, event/processing/availability times, point-in-time joins, window boundaries, missing values, versions, freshness, and serving logs.

**Deliverables:** offline/online flow diagram, point-in-time test, parity test, freshness SLO, and rollback plan.

**Evaluation:** no future leakage; late-event handling is explicit; online and offline logic is comparable; missing-feature behavior is safe and observable.

## X4 — Updated or deleted document remains retrievable

**Topics:** 05, 06, 07, 08  
**Problem:** A policy document is updated and later deleted, but the old passage remains in search results and in a cached response.

**Constraints:** document provenance must be retained; access revocation cannot be bypassed by stale caches; retrieval service must be observable.

**Required analysis:** trace source change/deletion through extraction, chunks, embeddings, index, metadata, cache, and response; define idempotency, retry, reconciliation, and revocation behavior.

**Deliverables:** lifecycle diagram, deletion propagation matrix, negative tests, and freshness/revocation SLOs.

**Evaluation:** every derived copy has an owner and removal/update path; the system does not rely only on eventual TTL expiration for security revocation.

## X5 — AI assistant retrieves unauthorized content

**Topics:** 05, 06, 07, 08  
**Problem:** User B receives a passage cached after User A's authorized query.

**Constraints:** multi-tenant corpus; permissions can change; some retrieval candidates are shared but final content is restricted.

**Required analysis:** identity source, authoritative authorization check, cache-key scope, policy version, ACL lag, tenant boundary, fail-closed behavior, and indirect prompt injection.

**Deliverables:** trust-boundary diagram, permission matrix, cache-key design, and negative security tests.

**Evaluation:** cache key is not treated as authorization; unauthorized content is blocked at retrieval/response; revocation and cache behavior are tested.

## X6 — API schema change breaks consumers

**Topics:** 07, 02, 04, 06  
**Problem:** A producer renames a required field and silently changes a currency's meaning. Finance, ML, and RAG consumers behave differently after deployment.

**Constraints:** multiple consumers, differing release cadences, a need for auditability and rollback.

**Required analysis:** classify structural and semantic compatibility, locate consumers, define versions/deprecation, contract tests, ownership, and communication.

**Deliverables:** change-impact matrix, consumer migration plan, contract tests, and rollback trigger.

**Evaluation:** semantic changes are treated as breaking even if the type remains unchanged; no unknown consumer is silently abandoned.

## X7 — Cache serves stale data or a hot key overloads the source

**Topics:** 03, 07, 08  
**Problem:** Cache hit ratio looks healthy, but some users receive old data. During expiry, a hot key causes a burst of backend requests.

**Constraints:** bounded freshness; no unbounded retries; the source is also needed for non-cache traffic.

**Required analysis:** source version and event timestamps, invalidation delivery, cache TTL origin, hot-key distribution, request coalescing, backpressure, stale policy, and fallback.

**Deliverables:** incident timeline, cache decision matrix, metrics, load/failure tests, and ADR.

**Evaluation:** hit ratio is not treated as freshness proof; backend concurrency is bounded; stale serving is contract-controlled.

## X8 — Enterprise serving architecture trade-offs

**Topics:** 01–08  
**Problem:** Design an integrated platform for analytics, customer APIs, fraud ML, and permission-aware policy retrieval.

**Constraints (illustrative):**
- Dashboard: prior-day reconciliation, 30-minute freshness.
- Customer API: p95 under 100 ms, freshness under 10 seconds.
- Fraud model: online feature retrieval within a defined inference budget and point-in-time-correct training.
- RAG: current document versions, authorization per request, deletion/revocation propagation.
- Budget is limited; teams need clear ownership and observable contracts.

**Required analysis:** architecture components and data flows; semantic definitions; operational stores; feature lifecycle; document/vector pipeline; retrieval authorization; product contracts; cache/freshness; failure isolation; costs and governance.

**Deliverables for X8 (short-form scenario, not the full capstone):** a one-page architecture summary showing the major serving paths, shared contracts, the five highest-risk cross-topic decisions, and one validation signal/owner for each. Do not reproduce the full artifact package required by H1.

**Evaluation:** all eight topic areas are represented at a decision level; no security invariant is traded away for performance; requirements are measurable; major trade-offs and failure paths are explicit; validation is testable. The detailed diagrams, contracts, matrices, and test evidence belong to the separate H1 readiness challenge.

---

# D. Answer key and explanations

Answers below are reference answers. For design questions, alternatives are acceptable when assumptions are stated and all mandatory correctness, security, and validation requirements are met.

## D1. Topic 01 answers

**T01-B1 — Correct: B.** Requirements should precede technology selection. Finance needs reconciliation and auditability; the operational application needs key-based access and a strict latency budget. A is wrong because a shared subject area does not make workload shapes identical. C is wrong because raw files do not inherently provide the required low-latency key access or reconciliation. D is wrong because a one-hour TTL is invented without a freshness requirement.  
**Lesson:** `01-analytical-serving-patterns-and-consumer-needs.md`.  
**Common error:** treating subject-area similarity as proof that access pattern and service objectives are identical.

**T01-B2 — Reference answer.** Capture consumer/purpose, access pattern, freshness, latency percentile/target, concurrency/peak rate, data volume, skill/usability, security, auditability, availability, and cost. “Fast” lacks a percentile, boundary, workload, and acceptance threshold.  
**Complete answer:** at least four measurable requirements plus explanation of why they influence design.  
**Common error:** choosing a product before defining the workload.

**T01-I1 — Reference answer.** Dashboard: governed mart/semantic model, preaggregation or materialized view if measured query cost warrants it, and possibly result caching; measure concurrency/peak requests, p95/p99, query duration, refresh lag, and reconciliation. Operational application: serving store optimized for point access, possibly a carefully bounded cache; measure p95/p99, request rate, concurrency, source-to-serving lag, and error rate. Isolate dashboard scans from online resources.  
**Complete answer:** different paths justified by access pattern and explicit measurements.  
**Common error:** assuming the dashboard's 30-minute data age is acceptable for an operational application.

**T01-I2 — False.** Governance addresses ownership, access, lineage, quality, and policy, but does not guarantee the right latency, freshness, query shape, concurrency, or usability.  
**Common error:** conflating governance with service fitness.

**T01-A1 — Reference answer.** Matrix columns should include consumer, decision/purpose, access pattern, data scope/grain, freshness, latency percentile, concurrency/peak rate, consistency/audit requirements, security, availability, cost, proposed serving path, owner, and validation. Resolve conflicts by separating workloads, defining a common semantic contract, publishing explicit service tiers, and documenting any negotiated objective. Do not weaken mandatory access controls or auditability to improve latency.  
**Scoring focus:** complete requirements, alternatives, justified isolation, and measurable validation.

**T01-A2 — Reference answer.** Compare a shared platform (less duplication and simpler governance, but noisy-neighbor and correlated-failure risk) with isolated serving paths (better workload and failure isolation, but higher cost and operational complexity). Decide using measured workload, SLOs, security boundaries, recovery objectives, and team capacity. Validate with mixed-workload tests, failure injection, cost per consumer, and SLO telemetry. Review when traffic, freshness, cost, or risk changes.  
**Common error:** assuming “shared” is always cheaper after operational incidents are counted.

## D2. Topic 02 answers

**T02-B1 — Reference answer.** A warehouse integrates and stores analytical data; a mart is a subject- or consumer-oriented analytical data set/model; a semantic layer defines business entities, relationships, metric meaning, and governed access over underlying data. Physical storage and semantic meaning are related but not identical. Implementations vary.  
**Common error:** calling a semantic layer a database by definition.

**T02-B2 — Correct: B.** Duplicate dimension rows violate the expected relationship and multiply matching fact rows. A is wrong because a semantic layer does not inherently change values; incorrect joins can. C is wrong because revenue is commonly additive across order lines when defined appropriately. D is wrong because cache entry count does not explain relational row multiplication. Verify dimension uniqueness, effective-date predicates, and join cardinality.  
**Lesson:** `02-warehouse-marts-and-semantic-layers.md`.

**T02-I1 — Calculation.** Correct revenue = 40 + 60 + 25 = **125 currency units**. If the two order-A line rows are duplicated once, total = 40 + 60 + 40 + 60 + 25 = **225 currency units**. The fact grain is one row per order line. This assumes the duplicate join repeats both order-A rows exactly once and order B remains single.  
**Common error:** summing after a many-to-many or non-unique join without checking row counts.

**T02-I2 — Reference answer.** Example contract: count distinct customer IDs with an active status at the last instant of the month, under a defined business timezone and effective-dated status logic. Specify treatment of closed accounts, test accounts, merges, and late-arriving changes; owner and lineage; snapshot/version; and whether the metric is additive across time (month-end counts are generally not additive across months). Tests: unique customer snapshot key; compare sample to source; ensure month-end boundary handling; verify no duplicate entity contributes twice.  
**Common error:** summing month-end customer counts across months as if they were additive.

**T02-A1 — Reference answer.** The join can fan out because `customer_dim` is not unique on `customer_id`; select the dimension row valid for the fact's effective timestamp, or join to a tested current-row projection if the metric explicitly uses current attributes. Do not arbitrarily `DISTINCT` the revenue. Freeze the comparison period and source snapshot; compare canonical formula, grain, filters, inclusion/exclusion rules, currency/FX timestamp, business timezone, join cardinality, late-arriving records, model version, and refresh timestamp. Reconcile known records and intermediate row counts before changing code; then add cross-consumer regression tests.  
**Mandatory:** do not pick the majority value without evidence.

**T02-A2 — Reference answer.** Define common metrics centrally with owner, formula, grain, additivity, lineage, version, and tests. Enforce access through approved row/column policies or governed views; ensure access rules do not silently change metric meaning. Add version/deprecation and impact analysis, notify registered consumers, and run reconciliation and permission tests. Different authorized subsets may produce different totals if the access policy requires it; label that scope rather than pretending totals are universally comparable.  
**Common error:** allowing a security filter to create an undocumented semantic difference.

## D3. Topic 03 answers

**T03-B1 — Reference answer.** Operational: selective reads/writes, often keyed by entity, high concurrency, low latency, and immediate customer or process impact. Analytical: scans/joins/aggregations over many records, often historical, with different latency and resource shape. Failure impact and acceptable staleness depend on the consumer.  
**Common error:** assuming every operational path must use a particular database technology.

**T03-B2 — Correct: B.** p99 is a percentile: about 99% of measured requests are at or below the value and about 1% exceed it, subject to the measurement method and sample. A is wrong because requests have a latency distribution; C confuses milliseconds with requests/second; D confuses a percentile with the arithmetic mean.  
**Common error:** interpreting p99 as the worst possible request.

**T03-I1 — Calculation.** \(L = \lambda W = 2{,}400\ \text{requests/s} \times 0.050\ \text{s} = 120\) average in-flight requests. Units cancel to requests. This is an average based on the stated rate and average time; it does not size peak concurrency, connection pools, CPU, memory, queueing, retries, payload variation, or p99 behavior.  
**Common error:** treating 120 as a complete pool-size recommendation.

**T03-I2 — Reference answer.** Use a point-access operational store for customer reads/writes with explicit consistency and latency controls; use an analytical warehouse/mart or precomputed aggregate for broad historical queries. A shared resource can cause scans to compete with online traffic and create noisy-neighbor effects. Measure mixed workload and isolate capacity where needed.  
**Common error:** assuming a read replica automatically removes all consistency and capacity issues.

**T03-A1 — Reference answer.** Likely loop: queueing increases tail latency, clients time out and retry, retries add load, connection pool remains saturated, and more requests queue. Mitigate with bounded concurrency/queues, deadline propagation, retry budgets with backoff/jitter, circuit breaking, load shedding, pool sizing based on measurement, and isolation of bulk work. Instrument queue wait, pool wait, request rate, retries, backend latency, saturation, and p95/p99. Test burst, slow dependency, timeout, retry, and recovery scenarios.  
**Common error:** increasing retries or pool size without bounding the workload.

**T03-A2 — Reference answer.** A read replica can reduce read load but has replication lag; CDC-fed serving store enables workload-specific access but introduces event lag and recovery concerns; a materialized view precomputes a defined query but has refresh cost/lag; cache reduces repeated-read latency but adds invalidation and stale-read risk. Choose based on measured request shape, freshness bound, consistency, operations, failure behavior, and cost. Validate source-to-response age, p99 under peak load, replay/recovery, and failure modes.  
**Common error:** assuming one option is universally superior.

## D4. Topic 04 answers

**T04-B1 — Reference answer.** Offline features support historical training/analysis at scale; online features support low-latency inference. They may use different stores and refresh mechanisms, but the feature definition, entity key, time/window semantics, null/default behavior, and version must remain aligned or be explicitly tested.  
**Common error:** equating same feature name with same calculation.

**T04-B2 — False.** Using a future value leaks information unavailable at prediction time. Training examples must use feature state available at the event/prediction timestamp according to the declared availability semantics, not simply the latest value today.  
**Common error:** treating later information as “more accurate” for historical prediction reconstruction.

**T04-I1 — Reference answer.** No, not if the 10:05 update depends on information unavailable at 10:00. Use a point-in-time join that limits features to values available by the prediction/event timestamp, respecting event time, processing/availability time, window boundary, and late-event policy.  
**Common error:** joining only on entity ID.

**T04-I2 — Reference answer.** Tests can include: point-in-time leakage fixtures; offline/online parity for the same entity/time; distribution/value comparison from shadow logs; freshness/lag thresholds; missing/default-rate alerts; version/schema checks; and late-event replay tests.  
**Complete answer:** four checks with measurable expected behavior.

**T04-A1 — Reference answer.** Compare model version, feature definitions, window endpoints, event time vs processing time, watermark/late-event policy, source lag, null/default rate, online store values, and logged prediction-time features. Replay known events through old and new pipeline versions, shadow-compare outputs, run point-in-time tests, and roll back the changed feature definition if the change violates acceptance thresholds.  
**Common error:** retraining first without establishing the source of skew.

**T04-A2 — Reference answer.** Define each feature's entity, formula, time window, event-time/availability semantics, owner, version, and freshness tier. Batch path writes point-in-time-correct offline values; stream/hybrid path updates online values with idempotent versioned upserts and late-event handling. Specify inference latency budget, missing-feature behavior, parity tests, replay/backfill, deletion propagation, and lag/skew alerts.  
**Mandatory:** point-in-time correctness and privacy/deletion controls where relevant.

## D5. Topic 05 answers

**T05-B1 — Reference answer.** Ingest source → extract/clean → chunk → embed → index vectors with metadata. Example validations: source/version captured; extraction completeness and OCR/table quality; chunk boundaries and metadata present; embedding model/version and dimensions valid; index count/metadata/known retrieval cases pass.  
**Common error:** indexing before the required vectors or metadata are ready.

**T05-B2 — Reference answer.** Provenance allows traceability to the authoritative source and version; location enables citations and debugging; timestamps support freshness; classification/access metadata enables policy filtering; model/index versions enable safe migration and reproducibility.  
**Common error:** storing vectors without the metadata required to update or delete them.

**T05-I1 — Calculation.** Chunks = 40,000 documents × 25 chunks/document = **1,000,000 chunks**. Raw bytes = 1,000,000 × 512 dimensions × 4 bytes/dimension = **2,048,000,000 bytes**, or **2.048 decimal GB**. This excludes index structures, metadata, replicas, and allocator overhead.  
**Common error:** reporting 2.048 GB as total production storage.

**T05-I2 — Reference answer.** Use a stable idempotency key such as `(source_document_id, source_version, chunking_version, chunk_position/content_hash, embedding_model_version)`. Persist stage checkpoints only after durable outputs, make writes upserts keyed by deterministic IDs, and retry safely. Reconcile expected vs actual chunk counts, unique IDs, orphan vectors, source-version coverage, and duplicate hashes.  
**Common error:** generating a fresh random chunk ID on every retry.

**T05-A1 — Reference answer.** Keep old and new embedding/index versions separate; re-embed in bounded batches; record source/model/chunk versions; evaluate labelled retrieval queries for quality and latency; dual-write or replay changes during migration; cut over only after parity and freshness checks; retain a rollback window; then delete old vectors according to retention policy. Estimate token volume, compute, storage, and query overhead.  
**Common error:** mixing vectors from incompatible embedding spaces without a validated strategy.

**T05-A2 — Reference answer.** Propagate source version/deletion event through extraction records, chunks, embeddings, vector index, metadata filters, result caches, and any downstream copies. Make events idempotent, retryable, ordered/version-checked, and reconcilable. Validate with seeded updates/deletions and prove that deleted or revoked content cannot be retrieved or served from cache within the defined policy/SLO.  
**Common error:** deleting only the source file while leaving indexed derived copies.

## D6. Topic 06 answers

**T06-B1 — Reference answer.** User question → authenticate identity → retrieve only authorized candidates → rank/filter passages → build grounded context → generate answer → validate/output with provenance as required. Authorization must constrain retrieval and returned content; a model prompt alone is not an authorization boundary.  
**Common error:** checking permission only after the full passage has already been disclosed to an untrusted downstream component.

**T06-B2 — Correct: C.** When permission cannot be established, do not disclose protected content. A is wrong because relevance is not permission; B is wrong because another user's cache entry conveys no entitlement; D is wrong because the model is not an authoritative identity or policy engine. An approved safe degraded path may provide non-sensitive information or a clear error.  
**Common error:** treating relevance as permission.

**T06-I1 — Reference answer.** During the four-minute propagation gap, enforce authoritative or sufficiently current authorization at retrieval/response, or exclude content until ACL state is current. Do not trust stale index ACLs alone. Track ACL event lag, recheck versions, fail closed when access cannot be verified, and purge caches.  
**Common error:** waiting for eventual index refresh while serving the old result.

**T06-I2 — Reference answer.** Authorized user: allow scoped passage. Unauthorized user: deny/filter. Different tenant: no cross-tenant result. Revoked access: deny after revocation contract bound. Deleted document: no passage from index/cache. Stale ACL: recheck or exclude/fail closed. Authorization outage: do not disclose restricted content; return approved safe error/degradation. Tests should verify both status and absence of protected text in output/logs.  
**Common error:** testing only the happy path.

**T06-A1 — Reference answer.** Retrieved content is untrusted data, not policy or authority. Apply identity-based authorization and tenant filters before content reaches the generation context; isolate tool permissions from document text; constrain tools with server-side authorization; treat prompt injection as content to analyze, not instructions to obey; validate outputs and audit source IDs/policy decisions without logging secrets.  
**Common error:** relying solely on a prompt instruction to ignore malicious text.

**T06-A2 — Reference answer.** Use authoritative identity and policy source; store source document/version, chunk provenance, classification, tenant and ACL metadata; filter retrieval using current authorization; recheck before response where needed; track ACL and deletion lag; fail closed on uncertain access; use negative cross-tenant/revocation tests. Cache final results only if identity/policy scope is safely represented and revalidated; otherwise disable cross-user result caching or cache only permission-independent candidates and authorize before returning content.  
**Mandatory:** no unauthorized content disclosure.

## D7. Topic 07 answers

**T07-B1 — Reference answer.** A data product has a named owner, purpose and consumers, documented interface/schema/semantics, quality and freshness promises, access policy, lineage, support/operating model, versioning, and lifecycle. A table or endpoint alone does not establish these commitments.  
**Common error:** calling an unmanaged table a product without ownership or contract.

**T07-B2 — Correct: B.** Compatible additions, explicit deprecation, consumer inventory, migration period, and contract tests reduce breakage. A is wrong because immediate rename breaks consumers before they can migrate. C is wrong because an unchanged schema with changed meaning can silently corrupt decisions. D is wrong because production errors are a late and unreliable change-management mechanism.  
**Common error:** assuming all consumers can upgrade at once.

**T07-I1 — Reference answer.** Contract should define identity and authorization, required fields and types, units/currency/timezone, metric meaning/grain, freshness and quality behavior, timestamps/version, error codes, limits/pagination, latency/availability objectives, compatibility, and support/ownership. Include valid and invalid fixtures plus contract tests.  
**Common error:** specifying field types but omitting meaning and freshness.

**T07-I2 — Reference answer.** SLI is the measured indicator (e.g. successful responses within 100 ms); SLO is the target for that indicator over a defined window; SLA is a formal agreement with commitments and consequences. Changing USD to account-local currency is semantic breakage even if the field remains a decimal.  
**Common error:** using SLI, SLO, and SLA interchangeably.

**T07-A1 — Reference answer.** Optional field addition is often structurally compatible if consumers tolerate unknown fields; changing currency semantics is breaking; tightening a quality filter can be semantically breaking by changing population or completeness. Publish a version or staged migration, identify consumers, update contract tests and metric definitions, communicate a deprecation date, monitor results, and define rollback triggers.  
**Common error:** classifying compatibility from schema shape alone.

**T07-A2 — Reference answer.** Assign accountable product owner and technical steward; publish schema and semantic contract, lineage, quality checks, security and retention; maintain consumer registry; define SLI/SLO and incident response; version/deprecate changes; test contracts in CI and against consumers; allocate costs transparently with quotas or tiers.  
**Common error:** leaving support and consumer impact unspecified.

## D8. Topic 08 answers

**T08-B1 — Correct: A.** Total lookups = 8,000 + 2,000 = 10,000. Hit ratio = 8,000/10,000 = **80%**; miss ratio = 2,000/10,000 = **20%**. B reverses hit and miss; C uses counts as percentages without dividing by total; D is wrong because ratios require comparable hit/miss counts, not cache byte size. Counts must share the same boundary and window.  
**Common error:** dividing hits by misses or assuming hit ratio proves freshness.

**T08-B2 — Reference answer.** Latency is response time; freshness is age/propagation delay relative to an authoritative source; correctness is semantic/value validity; authorization is permission to disclose. A result may return in 5 ms but contain yesterday's value or another tenant's data.  
**Common error:** describing stale and unauthorized as merely “slow cache issues.”

**T08-I1 — Calculation.** Miss ratio = 1 − 0.85 = **0.15 (15%)**. Backend reads = 2,000 lookups/s × 0.15 = **300 reads/s**, under the stated one-read-per-miss assumption. Actual load can differ because of bypasses, retries, multi-read loaders, coalescing, or non-cache traffic.  
**Common error:** treating 300 as a universal backend QPS forecast.

**T08-I2 — Reference answer.** Cache-aside: caller checks cache and loads on miss; flexible but caller manages invalidation and races. Read-through: cache loader owns miss path. Write-through: write path updates cache/source synchronously, adding latency and dual-write complexity. Write-behind: asynchronously persists writes, with durability/order/replay risk. Refresh-ahead: refreshes hot entries before expiry but may waste work or race with updates. For read-heavy bounded-staleness product lookup, cache-aside/read-through with source-versioned values, explicit invalidation/event path, TTL backstop, miss coalescing, and measurable freshness is a defensible start.  
**Common error:** using write-behind for authoritative writes without a durability contract.

**T08-A1 — Reference answer.** The code reads an unspecified-lag replica, carries no source version or authoritative commit timestamp, writes unconditionally, and treats TTL as if it bounded source age. The source commit succeeds, invalidation is lost, and an older replica value may repopulate the cache. Add durable invalidation/CDC or outbox, version checks that reject older writes, reconciliation, source-to-response age metrics, invalidation lag/error alerts, and tests for dropped events and stale replicas. TTL alone may start when stale data is inserted, may not account for upstream lag, and may not bound stale-while-revalidate or failed-refresh behavior.  
**Common error:** monitoring only hit ratio and TTL.

**T08-A2 — Reference answer.** Key by normalized query plus tenant, effective authorization scope/policy version, corpus/index version, and any result-affecting parameters; never use the key as the sole authorization check. Reauthorize before returning protected content; purge or invalidate on revocation/deletion. Use request coalescing, bounded refresh concurrency, TTL jitter, rate limits and backpressure; stale-while-revalidate only for data whose contract allows it and never to bypass revocation. Define cache/source outage behavior and negative cross-tenant tests.  
**Common error:** query-only cache keys and unlimited fallback traffic.

## D9. Cross-topic scenario answer guidance

**X1 — Dashboard vs operational app.** Separate the analytical path from the low-latency operational path. Define shared semantics but different service objectives and refresh mechanisms. Use mixed-workload tests and source-to-response age measurements. The 30-minute dashboard delay must not be inherited by the API. Score for matrix, diagram, SLO boundaries, and isolation/failure behavior.

**X2 — Metric disagreement.** Establish a canonical metric contract and compare grain, filters, joins, timezone, currency, source snapshot, late-arriving data, and versions. Reconcile intermediate records; do not average or choose the majority result. Add cross-consumer regression tests. Score for evidence-driven root-cause analysis.

**X3 — Feature skew.** Compare exact feature versions and timestamps; ensure training rows only see values available at prediction time. Test late events, windows, missing values, and online/offline parity. Shadow compare and roll back the changed pipeline if acceptance criteria fail. Score for point-in-time correctness and safe operations.

**X4 — Stale/deleted document.** Trace all derived copies, including caches. Use idempotent versioned updates/deletions, retry and reconciliation, and validate retrieval denial after deletion/revocation. TTL alone is not a security deletion strategy. Score for end-to-end provenance and negative tests.

**X5 — Unauthorized AI retrieval.** The likely root cause is query-only cache reuse without authorization scope/recheck. Enforce server-side authorization on each response, use tenant/policy-aware scope, handle revocation, and treat retrieved instructions as untrusted. Test absence of protected text. Score for fail-closed behavior and trust boundaries.

**X6 — API breakage.** A required field rename and currency semantic change are potentially breaking; the semantic change is breaking even if structurally compatible. Use consumer registry, version/deprecation, contract tests, staged migration, monitoring and rollback. Score for structural and semantic analysis.

**X7 — Stale/hot cache.** Correlate source versions, event lag, invalidation and cache insertion. Add version guards, durable invalidation, reconciliation, request coalescing, bounded concurrency, and explicit stale policy. A high hit ratio only measures reuse at the chosen boundary. Score for both freshness and capacity controls.

**X8 — Integrated architecture.** Produce an architecture with fit-for-purpose paths, governed semantic contracts, online serving, point-in-time feature pipeline, versioned document/vector pipeline, permission-aware retrieval, data-product contracts, and cache/freshness controls. Make owners, SLOs, tests, lineage, cost and failure behavior explicit. No single tool or cache strategy is required. Score for end-to-end consistency, safety, and evidence.

---

# E. Practical assessment and evidence

Complete these tasks using synthetic records and local diagrams or pseudocode. No cloud deployment, production credentials, or real personal data are required.

## P1 — Consumer-requirement matrix

- **Objective:** choose serving patterns from consumer needs.
- **Inputs/assumptions:** executive dashboard, analyst workspace, regulatory extract, customer API, fraud model, and RAG assistant.
- **Required work:** document access pattern, grain/scope, rate/concurrency, latency, freshness, security, auditability, cost, proposed path, and failure behavior.
- **Expected deliverable:** matrix plus a short rationale and ADR.
- **Validation:** each pattern can be traced to at least one explicit requirement.
- **Acceptance criteria:** no universal one-size-fits-all path; freshness and latency are separately measurable; governance and workload isolation addressed.
- **Common failure modes:** vague “fast” targets, missing security boundaries, technology-first selection.
- **Lessons:** Topics 01, 03, 07, 08.

## P2 — Analytical model and metric definition

- **Objective:** preserve semantic consistency.
- **Inputs/assumptions:** synthetic order-line facts, customer dimension, date dimension, revenue and active-customer requirements.
- **Required work:** state grain, facts, dimensions, relationships, metric formula, filters, additivity, ownership, lineage, access policy, and versioning.
- **Expected deliverable:** model diagram, metric catalogue, reconciliation query/pseudocode, and test cases.
- **Validation:** manually compute totals for a small fixture and compare model output.
- **Acceptance criteria:** grain is explicit; join fan-out is tested; metric semantics and time boundaries are unambiguous; security does not silently alter meaning.
- **Common failure modes:** duplicate dimension joins, non-additive measures summed across time, metric defined independently in each dashboard.
- **Lessons:** Topic 02, with Topic 07 contracts.

## P3 — Operational serving comparison

- **Objective:** select an operational access path and validate its workload.
- **Inputs/assumptions:** point lookups, update rate, target p95/p99, peak request rate, payload size, freshness and availability.
- **Required work:** compare relational/key-value/search/replica/CDC-serving/cache options as applicable; define latency budget, consistency, failure behavior, and capacity test.
- **Expected deliverable:** comparison table, decision rationale, and performance test plan.
- **Validation:** workload test includes warm/cold paths, peak load, failure, retries, and recovery.
- **Acceptance criteria:** p95/p99 have a measurement boundary; concurrency and throughput are addressed; no unsupported capacity claim.
- **Common failure modes:** using averages only; ignoring tail latency, replica lag, and retry storms.
- **Lessons:** Topic 03.

## P4 — Feature lifecycle and consistency validation

- **Objective:** prevent leakage and training-serving skew.
- **Inputs/assumptions:** synthetic events with entity ID, event time, processing time, feature value, source version, and prediction time.
- **Required work:** draw offline/online flow; specify feature contract and point-in-time join; define late-event, backfill, missing-value, freshness, and deletion policies.
- **Expected deliverable:** feature flow diagram, feature definitions, parity/leakage tests, and monitoring list.
- **Validation:** include a seeded future-value leakage case and an offline/online mismatch case.
- **Acceptance criteria:** tests fail for future leakage; definitions/versioning align; freshness and missing values are observable.
- **Common failure modes:** joining on entity only; using the latest value; ignoring late events.
- **Lessons:** Topics 03, 04, 07, 08.

## P5 — Document-to-vector pipeline

- **Objective:** make document ingestion, updates, versioning, and deletion reproducible.
- **Inputs/assumptions:** synthetic policy documents with versions, classification, ACL, timestamps, and deletion events.
- **Required work:** define ingest/extract/clean/chunk/embed/index stages, deterministic IDs, metadata, model versions, retries, checkpoints, and evaluation.
- **Expected deliverable:** pipeline diagram, schema, refresh/deletion matrix, and retrieval evaluation set.
- **Validation:** replay an event twice and verify idempotency; update and delete a document and verify index state.
- **Acceptance criteria:** each chunk has provenance; model version is recorded; deletion path includes all derived copies; retrieval quality is measured with labelled queries.
- **Common failure modes:** duplicate chunks after retries, stale vectors, missing ACL metadata.
- **Lessons:** Topic 05, with Topic 06 security.

## P6 — Permission-aware retrieval and security tests

- **Objective:** prevent unauthorized content from reaching a requester or generation context.
- **Inputs/assumptions:** two tenants, three users with differing permissions, synthetic documents, one revoked ACL, one deleted document, one adversarial passage.
- **Required work:** draw trust boundaries, design identity/authorization path, define cache-key scope, and write a permission matrix.
- **Expected deliverable:** retrieval architecture, positive/negative test matrix, revocation/deletion SLO, and incident response.
- **Validation:** run or manually trace each matrix case; verify protected text is absent from response and logs.
- **Acceptance criteria:** cross-tenant access denied; revocation/deletion respected; authorization outage fails closed for protected content; retrieved prompt injection does not grant authority.
- **Common failure modes:** permission check only in prompt; query-only cache key; stale ACL trusted.
- **Lessons:** Topics 05, 06, 07, 08.

## P7 — Data-product specification and consumer contract

- **Objective:** make product promises explicit and testable.
- **Inputs/assumptions:** synthetic Customer Exposure Summary consumed by finance, risk API, and ML.
- **Required work:** define owner, purpose, schema, semantics, quality, freshness, access, lineage, SLI/SLO, compatibility, deprecation, errors, and support.
- **Expected deliverable:** product spec, contract, consumer registry, compatibility matrix, and test plan.
- **Validation:** test valid/invalid fixtures and review a proposed breaking change.
- **Acceptance criteria:** semantic changes are assessed; consumer impact is traceable; each promise has a measurable test or monitoring signal.
- **Common failure modes:** table-only “product”; no consumer inventory; schema-only compatibility.
- **Lessons:** Topics 02, 04, 06, 07, 08.

## P8 — Cache and freshness decision matrix

- **Objective:** select a bounded and tested cache policy.
- **Inputs/assumptions:** one repeated point lookup, one repeated dashboard aggregation, one sensitive RAG query, and one bulk export; use illustrative workload numbers and label them.
- **Required work:** compare cache/no-cache/materialization/recompute; define key dimensions, TTL, invalidation, refresh, freshness SLO, stampede controls, security, failure behavior, and cost metrics.
- **Expected deliverable:** decision matrix, source-to-response freshness calculation, cache test plan, and ADR.
- **Validation:** recompute hit/miss and backend-load estimates; simulate invalidation loss, out-of-order update, permission revocation, and hot-key expiry.
- **Acceptance criteria:** units and assumptions shown; hit ratio not treated as freshness proof; TTL limitations stated; no unauthorized stale serving; backend load bounded.
- **Common failure modes:** TTL-only consistency claims; missing tenant/policy scope; no fallback limits.
- **Lessons:** Topic 08, informed by Topics 02, 03, and 07.

---

# F. Scoring and readiness criteria

## F1. Topic-question scoring

Each of the 48 topic questions is worth 2 points for a total of 96 points. The eight integrated scenarios add up to 80 points, so the maximum written-assessment score is **176 points**. Report topic and scenario results separately; do not use a combined total to hide a weak topic or a failed safety gate. Practical tasks are separate evidence gates and are not included in the 176-point total.

Topic-question scoring rules:
- MCQ: 2 for the correct answer, 0 otherwise.
- True/false with justification: 1 for the correct choice, 1 for a technically sound justification.
- Short answer/difference: 0–2 based on required concepts and example.
- Calculation: 1 for correct setup/units, 1 for result and interpretation.
- Design/scenario questions: use the rubric below; do not score purely for length.

Each cross-topic scenario is scored out of 10 using F3. Practical tasks are assessed separately against their stated acceptance criteria.

## F2. Open-ended answer rubric (0–4)

| Score | Description |
|---:|---|
| 0 | Missing, unrelated, or unsafe answer |
| 1 | Some relevant terms, but major omissions or unsupported claims |
| 2 | Mostly correct fundamentals; assumptions or validation are incomplete |
| 3 | Correct and well-structured; trade-offs, failure modes, and tests addressed |
| 4 | Complete, evidence-driven, measurable, and explicit about constraints and alternatives |

For a question originally worth 2 points, convert rubric score to 0, 0.5, 1, 1.5, or 2 points as appropriate.

## F3. Integrated-scenario rubric (0–10)

Score each dimension 0–2:
1. Requirements and assumptions are explicit.
2. Architecture/pattern choices are justified against requirements.
3. Correctness, semantics, freshness, and security are addressed.
4. Failure modes, reliability, and workload/cost trade-offs are covered.
5. Validation evidence, owners, and acceptance criteria are measurable.

**Safety cap:** if the design allows unauthorized data disclosure, uses future information in training, or silently changes critical metric semantics without controls, the scenario cannot score above 4/10 until corrected.

## F4. Topic readiness and remediation

Track each topic independently. Each topic has six questions worth 2 points each (12 points maximum). A suggested learning diagnostic is:
- **80% or above:** at least 10/12 points (83.3%, the first attainable score above 80% with the half-point scoring increments); likely ready to move forward if practical evidence passes.
- **60–79%:** review missed concepts and retest weak areas.
- **Below 60%:** 0–7/12 points; revisit the lesson systematically and redo its practical task. Scores of 7.5–9.5/12 fall in the 60–79% review band.

These are study thresholds, not proof of professional competence. Regardless of score, unresolved security/correctness defects or failed practical acceptance criteria block readiness for the relevant design task.

Remediation loop:
1. Categorize the error.
2. Return to the referenced lesson and re-read the relevant concept, example, or failure mode.
3. Rewrite the answer without looking.
4. Solve a parallel problem with changed values or conditions.
5. Update the gap log with the retest evidence.
6. Ask for review if the answer still depends on an unstated assumption.

## F5. Evidence gates

To claim module readiness for the final project, the learner must show:
- all eight topic sections attempted and a score plus open-gap list for each topic;
- P1–P8 artifacts completed against their acceptance criteria; an incomplete task may be scheduled as remediation, but scheduling is **not** a passed gate;
- all applicable mandatory security and point-in-time tests pass on the synthetic cases, with evidence recorded;
- an integrated architecture with traceable requirements, owners, SLOs, failure behavior, and validation.

Any unresolved high-risk gap in authorization, tenant isolation, point-in-time correctness, deletion/revocation, metric semantics, or bounded failure behavior blocks a readiness claim.

---

# G. Knowledge-gap log

Copy this table into a separate working document and add one row for every unresolved issue.

| Date | Topic | Question or task | Error type | Root cause | Corrective action | Retest result / evidence | Status |
|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | T__ | Q ID / artifact | Conceptual / technical / calculation / security / design | What assumption or concept failed? | Lesson section, exercise, or test to repeat | Parallel question or artifact evidence | Open / Resolved |
| | | | | | | | |

## G1. How to maintain the log

- Add a row immediately when an answer is wrong, vague, unsupported, or missing a required test.
- State the root cause precisely: for example, “used cache insertion time as source age,” not “cache topic weak.”
- Link the corrective action to a lesson filename and specific subsection or example.
- Retest with changed values or a different scenario; do not simply copy the answer key.
- Mark **Resolved** only when the retest is correct and the explanation identifies why the prior reasoning failed.
- Before the final project, review open gaps by risk. Security, metric correctness, point-in-time leakage, deletion/revocation, and unbounded failure behavior take priority over presentation polish.

---

# H. Final module-readiness assessment

## H1. Integrated capstone readiness challenge

**Scope note:** This is a module-wide readiness exercise designed to test integration across all eight topics. It is not a claim that every component below is automatically mandatory in the separate final project; use the project specification when available to determine project scope.

**Scenario:** Northbridge Bank wants a coherent data-serving architecture for:
1. Executive reporting on reconciled prior-day performance.
2. A customer API serving current account exposure.
3. A fraud model using offline training and online features.
4. An internal RAG assistant over policy and procedure documents.
5. Shared data products consumed by finance, risk, ML, and AI teams.

All data and numeric targets below are illustrative:
- Executive dashboard: data delay no greater than 30 minutes for intraday operational indicators; month-end figures must be reconciled and auditable.
- Customer API: p95 response time under 100 ms; source-to-response age under 10 seconds for the designated risk indicator.
- Fraud inference: feature retrieval has a declared sub-budget within the total inference latency; training examples must be point-in-time correct.
- RAG: authorization must be checked for every request; revoked/deleted content must not be disclosed beyond the approved revocation/deletion bound.
- Shared product: schema, semantics, quality, ownership, and versioning must be explicit.

### Required work

1. **Requirements:** produce the consumer-requirement matrix with latency, freshness, consistency, quality, access, availability, cost, and audit needs.
2. **Analytical semantics:** define core entities and at least two metrics, including grain, formula, additivity, time boundary, owner, and tests.
3. **Operational serving:** select access paths; define workload isolation, capacity evidence, timeouts/retries, and degraded behavior.
4. **Feature architecture:** draw offline/online flow; define temporal semantics, point-in-time joins, parity tests, late-event handling, and missing-feature behavior.
5. **Document/vector pipeline:** define ingestion, chunking, embedding/index versioning, provenance, incremental refresh, replay, and deletion.
6. **Permission-aware retrieval:** draw identity and authorization boundaries; create positive/negative tenant, ACL, revocation, deletion, and outage tests.
7. **Data products/contracts:** provide one product specification and API/consumer contract with compatibility and deprecation rules.
8. **Cache/freshness:** create a per-path cache decision matrix, source-to-response freshness calculation, invalidation strategy, stampede controls, and SLO monitoring.
9. **Operations and governance:** assign owners; define lineage, quality checks, observability, incident response, cost drivers, and ADRs.
10. **Validation:** trace each major requirement to a component, test, metric, owner, and acceptance criterion.

### Expected final deliverables

- Context and data-flow architecture diagram(s).
- Consumer-requirement matrix.
- Analytical model and metric catalogue.
- Operational serving comparison and capacity/performance test plan.
- Feature lifecycle diagram and point-in-time/parity tests.
- Document-to-vector pipeline and refresh/deletion test plan.
- Permission-aware retrieval diagram and security test matrix.
- Data-product specification, API/consumer contract, and version/deprecation policy.
- Cache/freshness decision matrix, calculations, and ADR.
- SLO/SLI table, risk register, lineage/ownership plan, and validation evidence.

## H2. Final checklist

### Requirements and serving
- [ ] All consumer personas and decision needs are explicit.
- [ ] Each access pattern has a justified serving option.
- [ ] Latency and freshness are separate measurable objectives.
- [ ] Workload isolation, capacity, and cost assumptions are documented.

### Analytical semantics
- [ ] Grain, facts, dimensions, relationships, and metric definitions are explicit.
- [ ] Aggregation/additivity and join-cardinality tests are included.
- [ ] Lineage, owners, access controls, and semantic versioning are defined.

### Operational and ML paths
- [ ] Operational latency budgets and p95/p99 measurements are defined.
- [ ] Retries, timeouts, backpressure, and degraded behavior are bounded.
- [ ] Feature definitions and offline/online versions are aligned.
- [ ] Point-in-time tests prevent future leakage.
- [ ] Late-event, backfill, missing-feature, and deletion behavior are tested.

### Document, retrieval, and security
- [ ] Every chunk is traceable to source/version and model/index version.
- [ ] Incremental update, retry, replay, and deletion paths are documented.
- [ ] Authorization is enforced before protected content is returned.
- [ ] Cross-tenant, revoked-access, deleted-document, and authorization-outage tests pass.
- [ ] Retrieved content is treated as untrusted data, not as authority.

### Products, APIs, cache, and freshness
- [ ] Product owner, consumer registry, schema, semantics, and support are documented.
- [ ] Compatibility includes semantic changes, not just field types.
- [ ] Cache keys cover result-affecting and security-relevant dimensions.
- [ ] Hit/miss and freshness calculations show units and assumptions.
- [ ] TTL is not treated as a universal consistency guarantee.
- [ ] Cache stampede, hot-key, invalidation-loss, and fallback behavior are tested.
- [ ] Freshness SLO has a measurement boundary, window, and alert rule.

### Evidence and readiness
- [ ] Each topic has a score, evidence, and gap-log status.
- [ ] Practical tasks P1–P8 meet their acceptance criteria; scheduled-but-unfinished tasks remain open gaps, not passed gates.
- [ ] Integrated scenarios X1–X8 have been attempted.
- [ ] Open high-risk gaps are resolved or explicitly block project readiness.
- [ ] Architecture decisions include alternatives, trade-offs, validation, owners, and review triggers.

## H3. Proceeding to the final project

Proceed to `Projects/14-analytics-and-ai-data-serving-architecture.md` only when the relevant checklist items are supported by actual artifacts and tests. The actual project file was not available in the inspected source set; the module roadmap says its project guide is provisional and explicitly treats ML-feature and RAG components as optional unless the real project requires them. Therefore, apply the full eight-topic checklist to module readiness, but make project deliverables mandatory only when the project specification requires them. For every in-scope component, unresolved correctness, point-in-time, authorization, tenant-isolation, deletion/revocation, metric-semantics, or failure-bound defects block readiness.

The question-bank score is diagnostic, not a guarantee of professional competence. **Module completion gate:** the learner can explain the design, defend the trade-offs, reproduce the calculations, show test evidence, and trace every major in-scope consumer requirement to an owned component and measurable acceptance criterion.
