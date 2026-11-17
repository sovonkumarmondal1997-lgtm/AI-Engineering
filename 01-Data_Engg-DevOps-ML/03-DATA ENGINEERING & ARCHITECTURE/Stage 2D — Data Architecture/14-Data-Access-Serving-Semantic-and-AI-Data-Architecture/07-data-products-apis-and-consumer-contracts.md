# Data Products, APIs and Consumer Contracts

> **Module:** Stage 2D — Data Architecture / Module 2D.14 — Data Access, Serving, Semantic and AI Data Architecture  
> **Topic:** 07 of 08  
> **Audience:** Beginner to advanced data architects, data engineers, platform engineers, product owners, and governance practitioners  
> **Scope:** Vendor-neutral. Northbridge Bank, products, users, endpoints, records, metrics, dates, and service targets are synthetic illustrative examples, not real commitments.

## 1. Overview and learning objectives

### 1.1 What this topic solves

A platform can store clean data and still fail its consumers. A dashboard may use a different definition of exposure from a risk application; a model may receive a feature with different semantics online than it saw during training; an AI assistant may call a retrieval endpoint whose permissions or freshness are unclear. Data products package useful data and its operating promises into a discoverable, governed, supportable capability.

A **data product** is data made usable for a defined purpose through a documented interface, with accountable ownership, clear semantics, quality and freshness expectations, access controls, lifecycle rules, and a support path. It can be implemented using tables/views, a semantic layer, an API, files, events, feature-serving endpoints, permission-aware retrieval, or a combination. No single protocol is mandatory for every product.

A **consumer contract** records what a provider promises and what a consumer must do in return. It covers structure and meaning, access, quality, freshness, service levels, change policy, operational responsibilities, and evidence of conformance.

### 1.2 Learning objectives

By the end, you should be able to:

1. Distinguish a data product from a table, dataset, pipeline, API, and data platform.
2. Define product ownership, intended purpose, consumers, discoverability, support, and lifecycle.
3. Select interfaces using consumer behavior, payload size, latency, throughput, freshness, governance, and operating cost.
4. Write a product specification covering schema, semantics, keys, types, units, nullability, quality, lineage, access, and retention.
5. Write provider and consumer obligations that are explicit and testable.
6. Design an API contract with resources, request/response schemas, pagination, errors, authentication, authorization, rate limits, and idempotency where applicable.
7. Define measurable availability, latency, freshness, quality, support, and recovery objectives.
8. Classify structural and semantic changes, plan versions and deprecation, and communicate changes to registered consumers.
9. Implement contract tests and monitor conformance in CI and production.
10. Govern product adoption, ownership, cost allocation, incidents, and end-of-life decisions.

### 1.3 Roadmap alignment and scope boundary

The Module 2D.14 roadmap defines Topic 07 around data-product definition, interface selection, consumer contracts, compatibility, validation, support, and secure access. It identifies prerequisites as learning sequence 2, 4, and 6, plus P7 (data products and contracts).

- **Topic 02 — Warehouses, marts and semantic layers:** provides analytical models, metric definitions, grain, and semantic relationships. This lesson specifies how a product exposes and governs such outputs; it does not re-teach semantic modelling.
- **Topic 04 — Feature platforms and training-serving consistency:** provides feature definitions, point-in-time correctness, offline/online parity, and feature lifecycle concepts. A feature product must contract those semantics, versions, freshness, and serving behavior.
- **Topic 06 — RAG knowledge data and permission-aware retrieval:** provides permission-aware retrieval and evidence/provenance behavior. A retrieval product contract must preserve identity propagation, authorized results, safe errors, provenance, and freshness; this lesson does not reproduce the RAG architecture.
- **P7 — Data products and contracts:** the roadmap names this prerequisite but does not supply its full source contents in the topic roadmap itself. The product and contract framework below is therefore taught directly.
- **Topic 08 — Access patterns, cache strategy and freshness:** receives interface, cacheability, freshness, invalidation, and staleness commitments from the product contract.

The roadmap notes that the topic files and related project files were empty when the roadmap was authored. Accordingly, its listed exercises and targets are recommendations. Every specific target in this lesson is an illustrative design assumption, not a universal requirement.

### 1.4 Synthetic scenario

Northbridge Bank publishes a **Customer Exposure Summary** product for authorized risk analysts, relationship managers, finance analysts, and downstream applications. It provides a consistent, time-stamped view of a synthetic customer’s credit exposure for a defined reporting scope. It is not a credit decision engine, not a complete customer master, and not a promise that every upstream source is real-time.

The example uses fictional identifiers such as `CUST-1042`, fictional amounts in USD, and synthetic exposure values. No real personal data or secrets are included.

## 2. Prerequisites and dependency mapping

### 2.1 Concepts to know first

| Concept | Needed for this topic |
|---|---|
| Analytical serving and consumer needs (Topic 01) | Identify who consumes data and the workload they need |
| Warehouse, marts and semantic layers (Topic 02) | Preserve metric definitions, grain, and conformed dimensions |
| Operational serving and low-latency access (Topic 03) | Understand lookup, concurrency, latency, and availability constraints |
| Feature platforms (Topic 04) | Contract feature semantics, timestamps, and training/serving consistency |
| Document/vector pipelines (Topic 05) | Understand upstream provenance and freshness for knowledge products |
| Permission-aware retrieval (Topic 06) | Preserve authorization in AI-facing product interfaces |
| Metadata, lineage and quality topics elsewhere in Stage 2D | Publish ownership, classification, lineage, quality rules, and stewardship |
| Performance and FinOps module | Set realistic service objectives, quotas, and cost allocation |

### 2.2 The product is a boundary, not just a storage object

A table is a storage/query object. A pipeline transforms or transports data. An API is an interface mechanism. A platform supplies shared capabilities. A **data product** packages one or more of these into an owned consumer-facing capability with an explicit purpose and contract.

| Thing | What it is | What it does not guarantee by itself |
|---|---|---|
| Table or view | Structured data representation | Ownership, stable meaning, support, change notice, or SLO |
| Dataset | Collection of related data | Consumer interface, lifecycle policy, operational accountability |
| Pipeline | Processing and delivery workflow | That output is understandable, secure, or fit for a consumer |
| API | Programmatic interface | Correct semantics, governed access, quality, or a supported lifecycle |
| Data platform | Shared infrastructure and capabilities | Product-specific ownership or consumer promises |
| Data product | Governed data capability with owner, purpose, interface(s), contract, and operations | Perfect data or zero failures; promises must be measured and managed |

### 2.3 Why ownership matters

Every product needs an accountable **product owner** who decides purpose, roadmap, and service tier; a **technical owner** who operates the implementation; and, where appropriate, a **data steward** who owns definitions, quality expectations, and governance. One person may hold more than one role in a small team, but responsibilities must still be explicit.

When a consumer breaks, the response should not begin with “which team owns that table?” The product catalogue and contract should identify who responds, which behavior was promised, what evidence is available, and whether the issue is a provider defect or a consumer misuse.

## 3. Beginner fundamentals: products, interfaces, and contracts

### 3.1 Product checklist

Use this checklist before calling a dataset a product.

- [ ] **Name and purpose:** clear product name, business problem, intended use, and exclusions.
- [ ] **Accountability:** product owner, technical owner, steward, on-call/support route.
- [ ] **Consumers:** target personas, known subscriptions, critical downstream dependencies.
- [ ] **Discoverability:** catalogue entry, documentation, sample queries, interface definition, ownership and classification.
- [ ] **Semantics:** grain, definitions, keys, units, time zone, null meanings, aggregation rules.
- [ ] **Interface:** tables/views, API, files, events, feature endpoint, retrieval endpoint, or a justified combination.
- [ ] **Quality:** measurable rules, thresholds, validation schedule, failure behavior.
- [ ] **Freshness:** source-to-consumer lag definition and target.
- [ ] **Service level:** availability/latency target, measurement window, exclusions, incident response.
- [ ] **Security:** authentication, authorization, least privilege, classification, masking, audit.
- [ ] **Lineage:** source systems, transformations, version, owner, data-quality evidence.
- [ ] **Change policy:** compatibility rules, versions, notice, deprecation and migration support.
- [ ] **Cost:** usage metering, quotas, service tier, allocation or showback.
- [ ] **Lifecycle:** launch criteria, review cadence, retirement process, retention/deletion rules.

A product need not have every interface type. It must have the interfaces its consumers actually need and a complete contract for each supported interface.

### 3.2 Interface selection

| Interface | Best fit | Benefits | Trade-offs and controls |
|---|---|---|---|
| Queryable tables/views | Analysts, BI, exploratory analysis, large scans | Flexible filtering/aggregation; efficient for analytical tools | Strong schema/semantic governance needed; avoid accidental direct access to raw internals |
| Semantic/metrics endpoint | Shared business metrics and dimensions | Central definitions, governed joins and measures | Requires semantic-model governance; may constrain arbitrary queries |
| REST-style API | Application lookups, small/medium payloads, request-response | Clear resource contract, per-caller authorization and quotas | Per-request overhead; pagination, rate limits and backward compatibility needed |
| GraphQL-style API | Consumers needing selectable fields across related resources | Flexible response shape | Complexity in query cost, authorization at field/resource level, and query limits |
| Bulk file/export | Large extracts, partner exchange, scheduled processing | High throughput and efficient bulk transfer | Delivery latency, encryption, expiry, schema manifests, replay and file lifecycle |
| Event stream | Reactive consumers, change propagation, near-real-time integration | Low-latency event delivery and multiple subscribers | Ordering, duplicates, schema evolution, replay, consumer lag and delivery semantics |
| Feature endpoint | Online ML inference | Low-latency feature access with feature-specific semantics | Training/serving parity, feature freshness, versioning and point-in-time semantics |
| Retrieval/semantic endpoint | AI assistants needing permitted evidence | Encapsulates retrieval, authorization and provenance | Relevance, authorization, citations, freshness, and prompt/context boundaries must be contracted |

No interface is “best” in general. Choose using consumer behavior, payload size, query flexibility, concurrency, latency, freshness, access model, retry semantics, cost, and supportability. A product can publish different interfaces over the same governed model if their semantics remain aligned.

### 3.3 Interface selection worksheet

For each candidate interface, answer:

1. Is the consumer asking for one entity, a broad analytical query, a bulk snapshot, a continuous change feed, a model feature, or relevant knowledge?
2. What are the expected request rate, concurrency, payload size, and peak-to-average ratio?
3. What is the freshness requirement, measured from which source event or committed state?
4. What latency percentile matters: p50, p95, p99, or batch completion time?
5. Does the consumer need historical point-in-time data, current state, or both?
6. What access policy applies, and where can it be enforced?
7. What happens on retry, duplicate delivery, partial response, or outage?
8. What are the costs to produce, serve, monitor, secure, and support the interface?

Record the choice and rejected alternatives in an architecture decision record (ADR). Do not choose an API merely because it is familiar, or a stream merely because it is described as real-time.

### 3.4 What belongs in a consumer contract?

A consumer contract says what each side can rely on. It should cover at least:

- **Shape:** resource names, field names/types, required/optional fields, keys, pagination, ordering guarantees.
- **Meaning:** definitions, grain, units, time semantics, enum meanings, nullability, aggregation and inclusion/exclusion rules.
- **Quality:** validity, completeness, uniqueness, reconciliation, freshness and thresholds.
- **Access:** authentication, authorization, purpose, classification, masking, quotas, audit and revocation.
- **Operations:** availability, latency, maintenance, support hours, severity definitions, incident communication.
- **Change:** compatibility policy, versioning, deprecation notice, migration assistance, sunset conditions.
- **Responsibilities:** provider controls and consumer obligations such as retries, timeout handling, schema validation and responsible use.
- **Evidence:** contract tests, quality reports, monitoring, catalogue entry and version history.

“Best effort” is not a measurable service promise. If a guarantee is not provided, explicitly mark it as not guaranteed.

## 4. Interface and product specification

### 4.1 Complete illustrative product specification

#### Product identity

| Field | Contract value |
|---|---|
| Product name | Customer Exposure Summary |
| Product ID | `risk.customer-exposure-summary` |
| Purpose | Provide a governed summary of committed credit exposure by customer and reporting currency |
| Intended consumers | Risk analytics, authorized relationship management, finance reporting, approved internal applications |
| Exclusions | Not a credit approval decision, not a customer master, not intraday trade execution state |
| Product owner | `team-risk-data-products` (fictional) |
| Technical owner | `team-risk-serving` (fictional) |
| Data steward | `team-credit-risk-stewards` (fictional) |
| Support route | `#risk-data-product-support` (fictional example; not a real channel) |
| Classification | Confidential business data; row-level access required |
| Source lineage | Synthetic credit facility ledger + committed exposure mart; lineage IDs published in catalogue |
| Product version | `v1` |
| Review cadence | Monthly service/quality review; quarterly contract and consumer review (illustrative) |

#### Consumer behavior and interfaces

| Interface | Consumer | Contract |
|---|---|---|
| REST-style lookup | Authorized application / analyst tooling | `GET /v1/customers/{customer_id}/exposure` |
| Query view | Risk analysts | Governed view `risk_product.customer_exposure_v1`, read-only, authorized role only |
| Bulk export | Approved finance reporting process | Scheduled encrypted snapshot with manifest, schema version, as-of timestamp and checksum |
| Event feed (optional) | Downstream monitoring | `customer-exposure-updated.v1` event; duplicate delivery possible; consumer must deduplicate by event ID |

These interfaces are alternatives for different workloads. The example API is specified in more detail below; the view, file and event interfaces must have their own complete access and operational contracts before production release.

#### Data grain and semantics

- **Grain:** one row per `customer_id`, `reporting_currency`, and `as_of_date` for a single published product snapshot.
- **Exposure amount:** sum of eligible committed facility exposure after approved transformations, expressed in `reporting_currency`; this is not account balance or total lifetime credit limit.
- **Reporting currency:** ISO-style three-letter currency code; values are converted using the published conversion policy and rate date. When conversion occurs, the product exposes the applied rate date, source, and conversion-policy version. If no conversion occurs, `conversion_metadata` is `null`; it is not evidence that an unknown rate was used.
- **As-of date:** business date to which the exposure snapshot applies, in the product’s documented reporting calendar.
- **Source freshness:** measured from the latest committed source watermark included in the product, not from request time.
- **Null semantics:** `null` is not a numeric zero. If exposure is unavailable or not computed, the API returns a defined availability/status signal or omits the record according to contract; it must not silently replace unknown with zero.
- **Negative values:** allowed only when the business definition permits credit adjustments; any such rule must be explicit and tested.
- **Key:** `(customer_id, reporting_currency, as_of_date)`; API lookup selects one customer and returns a declared current snapshot or requested supported date.

#### Illustrative quality commitments

All thresholds below are assumed for teaching and must be validated against actual consumer needs before adoption.

| Rule ID | Rule | Illustrative target | Measurement |
|---|---|---|---|
| Q-01 | Required identifiers and currency are non-null | 100% of published rows | Each publish |
| Q-02 | Product key is unique at declared grain | 100% unique | Each publish |
| Q-03 | Exposure amount is numeric and follows currency precision rules | 100% valid | Each publish |
| Q-04 | Reconciliation to approved source aggregate | Absolute difference ≤ USD 1 for the synthetic test scope, or documented currency-specific tolerance | Each daily close |
| Q-05 | Freshness | At least 99% of eligible scheduled daily snapshot runs publish within 30 minutes after the source watermark is committed | Rolling 90 days; report numerator and denominator because daily samples are sparse |
| Q-06 | Provenance | 100% of published snapshots carry source watermark, model version and publication timestamp | Each publish |
| Q-07 | Authorized row exposure | Zero known unauthorized responses in security regression tests | Every release and scheduled probe |

Quality rules must define sampling, denominator, exceptions, and remediation. A target without a measurement method is not a usable contract.

#### Illustrative service-level specification

| Indicator | Target (assumption) | Scope / method |
|---|---|---|
| API availability SLI | Successful eligible requests / total eligible requests; exclude only explicitly documented client-caused 4xx and formally excluded maintenance windows | Rolling 30-day window; do not automatically exclude provider-generated 429/5xx responses |
| Availability SLO | ≥ 99.9% per rolling 30 days | API endpoint, measured at gateway and validated by synthetic probes |
| Latency SLI | End-to-end server latency, including authorization and product lookup | p95 ≤ 300 ms and p99 ≤ 800 ms under the agreed workload |
| Freshness SLI | Eligible scheduled daily snapshot runs published within 30 minutes of source-watermark commit / all eligible scheduled daily runs | ≥ 99% over a rolling 90-day window; report raw counts and missed runs because the sample is small |
| Quality SLI | Published rows passing mandatory quality rules / all published rows | 100% for Q-01/Q-02/Q-03; Q-04 has stated tolerance |
| Support acknowledgement | Sev-1: 15 minutes; Sev-2: 1 business hour | Illustrative support-hours and escalation policy must be defined |
| Recovery objective | Restore API service within 2 hours for Sev-1 (illustrative RTO) | Recovery plan and dependency assumptions documented |
| Retention | Published snapshots retained for 13 months unless policy requires shorter/longer retention | Illustrative; legal and governance policy takes precedence |

An **SLI** is the measured indicator, an **SLO** is the internal target for that indicator, and an **SLA** is a formal agreement that may include remedies or exclusions. Do not label an internal target an SLA unless the organization has formally agreed to it. Availability denominator and exclusions must be explicit; otherwise teams can report incompatible numbers.

### 4.2 Security and governance specification

- Authenticate every caller using the organization’s approved identity mechanism; validate credentials and token audience/expiry.
- Authorize each requested customer row against the caller’s current entitlements. A broad service identity must not bypass the caller’s permissions.
- Derive tenant and purpose from trusted identity/policy context, not only caller-supplied request parameters.
- Apply least privilege to API, query, export, event subscription, logs, and support tooling.
- Mask or omit fields not authorized for the purpose; field-level access must be enforced before serialization.
- Log request ID, principal reference, decision, product version, and safe resource identifiers; do not log full sensitive payloads by default.
- Define retention, deletion, audit access, and incident handling according to governing policy.
- Do not expose internal table names, source paths, or other metadata unless they are part of the approved contract.
- For bulk exports, require an approved consumer, encrypted transport/storage, expiry, manifest, checksum, and controlled download access.
- For event streams, define the data retained in replay logs and how revocation/deletion affects downstream copies.

## 5. Intermediate API and consumer-contract design

### 5.1 Resource model and endpoint

Illustrative endpoint:

```http
GET /v1/customers/CUST-1042/exposure?reporting_currency=USD&as_of_date=2026-10-20
Authorization: Bearer <access-token>
Accept: application/json
X-Request-Id: req-example-0007
```

The token shown is a placeholder, not a real credential. Authentication verifies the caller; authorization decides whether the caller may view `CUST-1042` and the requested fields. The product must not trust the customer ID as proof of access. `reporting_currency` is required for this example. `as_of_date` is optional: when omitted, the endpoint returns the latest published snapshot; when supplied, it returns that exact supported snapshot or the documented unavailable response. It must not silently substitute a newer date for an unavailable requested date.

A possible successful response:

```json
{
  "data": {
    "customer_id": "CUST-1042",
    "reporting_currency": "USD",
    "as_of_date": "2026-10-20",
    "committed_exposure_amount": "1250.00",
    "conversion_metadata": null,
    "source_watermark": "2026-10-20T09:00:00Z",
    "published_at": "2026-10-20T09:12:00Z",
    "product_version": "v1",
    "quality_status": "passed"
  },
  "meta": {
    "request_id": "req-example-0007",
    "schema_version": "1.0"
  }
}
```

`committed_exposure_amount` is a decimal string to avoid ambiguity from binary floating-point serialization. Its currency and scale are explicit. This is an illustrative choice; a contract may use a JSON number if precision and consumer behavior are clearly defined.

### 5.2 Request validation and error semantics

Use stable machine-readable error codes and a documented mapping from condition to status. Do not leak whether a protected customer exists when policy requires hiding existence.

```json
{
  "error": {
    "code": "CUSTOMER_NOT_AVAILABLE",
    "message": "The requested resource is not available to this caller.",
    "retryable": false,
    "request_id": "req-example-0008"
  }
}
```

Illustrative error policy:

| HTTP-style status | Code | Meaning | Consumer action |
|---|---|---|---|
| `400` | `INVALID_ARGUMENT` | Malformed ID, unsupported currency, invalid parameter | Correct request; do not retry unchanged |
| `401` | `UNAUTHENTICATED` | Missing/invalid/expired credentials | Obtain valid credentials; retry only after reauthentication |
| `403` | `FORBIDDEN` | Caller authenticated but not permitted, when resource existence may be disclosed | Do not retry without entitlement change |
| `404` | `CUSTOMER_NOT_AVAILABLE` | Not found or intentionally concealed due to access policy | Do not infer existence; follow approved workflow |
| `409` | `CONTRACT_CONFLICT` | Request conflicts with resource/version state where applicable | Re-read current state or resolve conflict |
| `429` | `RATE_LIMITED` | Caller or consumer quota exceeded | Respect `Retry-After`; use backoff with jitter |
| `500` | `INTERNAL_ERROR` | Unexpected provider failure | Retry only if operation semantics and retry policy permit |
| `503` | `TEMPORARILY_UNAVAILABLE` | Dependency or capacity unavailable | Respect retry guidance; use bounded retries |
| `504` | `UPSTREAM_TIMEOUT` | Provider dependency timed out | Retry with bounded backoff if safe |

A `404` versus `403` choice depends on information-disclosure policy. The contract must be consistent across endpoints and explain whether resource existence is concealed.

### 5.3 Pagination for collection endpoints

For an illustrative collection endpoint:

```http
GET /v1/customers/exposure?as_of_date=2026-10-20&page_size=100&page_token=<opaque-token>
```

```json
{
  "data": [
    {
      "customer_id": "CUST-1042",
      "reporting_currency": "USD",
      "as_of_date": "2026-10-20",
      "committed_exposure_amount": "1250.00",
      "conversion_metadata": null,
      "source_watermark": "2026-10-20T09:00:00Z",
      "published_at": "2026-10-20T09:12:00Z",
      "product_version": "v1",
      "quality_status": "passed"
    }
  ],
  "meta": {
    "request_id": "req-example-page-0001",
    "next_page_token": "opaque-token-next",
    "snapshot_id": "exposure-snapshot-2026-10-20-r3",
    "schema_version": "1.0"
  }
}
```

Contract rules:
- `page_size` has a documented maximum (illustrative: 500); reject or clamp larger values consistently.
- Tokens are opaque, scoped to the authorized caller/tenant and snapshot, and must not grant access by themselves.
- Every page request revalidates authentication and authorization. A token must not become a bearer authorization grant.
- Define stable ordering and snapshot consistency. If a snapshot expires, return a documented error such as `410 SNAPSHOT_EXPIRED` or a contractually selected alternative.
- Do not return unauthorized rows simply because the page token was issued before an entitlement change.
- Document token expiry, invalid-token behavior, and whether concurrent source updates affect page consistency.

### 5.4 Authentication, authorization, rate limits, and idempotency

**Authentication** answers “who is calling?” **Authorization** answers “may this principal perform this action on this resource, with these fields, for this purpose?” Both must be enforced. Product interfaces should use approved identity mechanisms and avoid embedding long-lived secrets in code or URLs.

Rate limits should be specified per appropriate scope (principal, consumer application, tenant, or product tier), with burst and sustained limits, response behavior, and a `Retry-After` policy. A single global limit can allow one consumer to starve all others; quotas should reflect service tiers and fairness.

`GET` lookup is intended to be safe and idempotent. For write/command endpoints, define idempotency keys, key scope, retention window, duplicate-request behavior, and conflict semantics. Do not invent idempotency guarantees for a file upload or event publish operation unless its contract and implementation provide them.

### 5.5 Consumer contract template

Copy and complete this template for each product interface.

#### A. Product and contract identity
- Product name/ID:
- Product owner / technical owner / steward:
- Contract ID and version:
- Intended purpose and excluded uses:
- Consumer name, team, environment, and support contact:
- Criticality and service tier:
- Approved regions, tenants, and classification:

#### B. Interface and data semantics
- Interface type and version:
- Resource/table/topic/file names:
- Request/response/event schemas:
- Keys, grain, types, units, precision, time zone, null semantics:
- Definitions, inclusion/exclusion rules, and known limitations:
- Pagination, ordering, delivery, replay, and duplicate semantics:
- Lineage, source watermark, schema version, and provenance fields:

#### C. Quality and service levels
- Quality rules, denominator, threshold, measurement frequency:
- Freshness definition and target:
- Availability SLI/SLO and measurement window:
- Latency percentiles and workload envelope:
- Error budgets, maintenance windows, and exclusions:
- Support hours, severity levels, acknowledgement and recovery targets:

#### D. Security and governance
- Authentication method and trusted identity source:
- Authorization model, field/row controls, tenant and purpose rules:
- Classification, masking, audit events, and retention:
- Deletion/correction behavior and downstream-copy responsibilities:
- Rate limits, quotas, and usage/cost allocation:

#### E. Change and lifecycle
- Structural and semantic compatibility policy:
- Versioning strategy and supported versions:
- Deprecation notice and sunset criteria:
- Consumer registry and migration contact:
- Contract test suite and acceptance criteria:
- Incident communication and escalation:
- Effective date, approvers, and review date:

#### F. Responsibilities
**Provider commits to:** publish accurate contract documentation; enforce access controls; monitor declared SLOs; validate schema/quality; notify consumers of planned breaking changes; maintain version/deprecation records; provide incident communication; preserve lineage and audit evidence.

**Consumer commits to:** use only approved purposes; protect credentials and retrieved data; obey rate limits; set timeouts and bounded retries; tolerate documented optional fields and errors; validate schema; deduplicate events where required; avoid assumptions outside the contract; register the consuming workload; test changes before migration; report incidents with request IDs and timestamps.

### 5.6 Consumer registry and discoverability

A consumer registry records who uses each product/interface/version and how critical the dependency is. A minimal registry entry includes:
- consumer team/application and accountable contact;
- interface and contract version;
- purpose, tenant/region, data classification approval;
- usage pattern, peak rate, criticality and service tier;
- last successful contract test and last observed use;
- migration status, deprecation notices acknowledged, target date;
- downstream data copies and deletion obligations.

The catalogue tells users a product exists and how to request access. The consumer registry tells the provider who will be affected by a change. They complement each other; neither replaces access control.

## 6. Advanced compatibility, governance, and lifecycle management

### 6.1 Structural versus semantic compatibility

**Structural compatibility** concerns the shape of data: fields, types, nullability, keys, endpoints, required parameters, and response envelopes.

**Semantic compatibility** concerns meaning: what an amount represents, whether a date is event time or processing time, which records are included, the grain of a metric, how null is interpreted, how currency conversion works, or whether a feature is computed at prediction time or after the outcome.

A schema can remain byte-for-byte unchanged while the product becomes incompatible. Example: `committed_exposure_amount` previously excluded cancelled facilities but now includes them. The field name and decimal type remain the same; consumers’ risk totals change. This is a semantic breaking change and needs governance like a structural breaking change.

### 6.2 Compatibility matrix

Compatibility depends on consumer behavior, schema format, and policy. The classifications below are default guidance, not universal laws.

| Change | Typical classification | Conditions and action |
|---|---|---|
| Add optional response field | Usually backward-compatible for tolerant readers | Verify consumers ignore unknown fields; update docs/schema; test old consumers |
| Add required response field | Often breaking | Old readers or strict schemas may reject; introduce version or make optional first |
| Add new optional query parameter with unchanged default | Usually compatible | Ensure default preserves old behavior and parameter cannot weaken security |
| Add new enum value | Potentially breaking | Exhaustive switch statements may fail; consumer language and enum policy matter |
| Remove or rename field | Breaking | New version or expand/contract migration |
| Change field type or numeric precision | Breaking or high risk | Validate serialization, range, rounding, and consumer parsing |
| Change key, grain, ordering, pagination, or duplicate semantics | Breaking | Affects joins, deduplication and completeness; explicit migration needed |
| Change metric definition or inclusion rules | Semantic breaking | New semantic version/product version and side-by-side comparison |
| Change null meaning or zero/default behavior | Semantic breaking | Document and test; never silently redefine unknown as zero |
| Tighten authorization or masking | May break consumers operationally; security-required | Announce where permissible, preserve least privilege, do not delay urgent revocation merely for compatibility |
| Weaken authorization | Security-breaking | Requires security review; never treat as ordinary backward-compatible change |
| Improve freshness within promised bound | Usually compatible | Validate cost/load and ensure no changed meaning/order guarantees |
| Freshness worsens beyond contracted bound | Contract/SLO breach | Incident and remediation; not just a documentation change |
| Add optional field to a published event | Often compatible, but consumer parser matters | Schema registry/contract tests; preserve old fields |
| Change event ordering or delivery semantics | Breaking | Consumers may depend on ordering/idempotency/replay |
| Change feature computation timing or normalization | Semantic breaking for ML | Version feature definition and validate training/serving parity |
| Change retrieval authorization or citation semantics | Contract/security-impacting | Re-test permitted results, denial behavior, provenance and safe abstention |

### 6.3 Versioning policy

Choose and document a policy suitable for the interface. Common options include:
- **Major/minor schema version:** major for breaking changes, minor for compatible additions, patch for documentation or implementation fixes that do not alter contract behavior.
- **Versioned API path:** e.g. `/v1/...`, `/v2/...`; easy to see but creates multiple deployed surfaces.
- **Header/media-type versioning:** can reduce path duplication but requires clear tooling and observability.
- **Event schema version:** version the event contract independently from the transport/topic when appropriate.
- **Dataset/view version:** publish versioned views or contract identifiers rather than letting consumers bind to internal physical tables.

Version labels alone do not guarantee compatibility. A provider must define the rules, run tests, and communicate the migration plan. Avoid changing semantics in place just because the JSON schema validates.

### 6.4 Expand/contract change scenario

Assume the provider wants to rename `committed_exposure_amount` to `exposure_amount` and change the inclusion rule to include a newly approved facility category. Three consumers depend on v1:

- **Risk dashboard:** can migrate in two weeks; uses field name and metric meaning.
- **Limit monitoring service:** strict schema parser; requires four weeks for release validation.
- **Finance export:** uses the old definition for monthly close; needs side-by-side reconciliation for one full close cycle.

Recommended process:

1. Register the change request, reason, affected fields/definitions, risk, owner, target date, and rollback plan.
2. Classify it as both structural (rename) and semantic (definition change). Do not ship it as an ordinary additive change.
3. Define v2 with the new field and explicit new definition; retain v1’s original semantics while v1 is supported.
4. Publish v1/v2 comparison samples, schema definitions, metric reconciliation, and consumer-specific migration instructions.
5. Add contract tests for v1 and v2; run provider tests and consumer-driven tests for all registered critical consumers.
6. Notify registered consumers and record acknowledgement/migration plans. Agree on a deprecation period based on actual release cycles and criticality, not an arbitrary universal number.
7. Operate both versions with separate SLOs and usage telemetry. Reconcile values and investigate unexplained deltas.
8. Deprecate v1 only after critical consumers migrate or an explicit exception is approved; publish sunset date and escalation path.
9. Retire v1 only after usage reaches zero for the required observation window, backups/retention obligations are addressed, and rollback requirements are satisfied.
10. Close the change with evidence: test results, consumer sign-offs, migration metrics, incident record if applicable, and updated catalogue/lineage.

If a security defect requires immediate access restriction, security takes precedence over ordinary deprecation windows. Compatibility processes do not justify retaining unauthorized access.

### 6.5 Contract tests and responsibilities

A **provider contract test** verifies that the provider emits data matching the published schema, semantics, quality rules, and error behavior. A **consumer contract test** verifies that the provider’s real responses satisfy the assumptions a specific consumer depends on. Neither test type alone proves every consumer is safe; combine schema checks, semantic assertions, security tests, integration tests, and production monitoring.

Contract test coverage should include:
- valid and invalid requests;
- required and optional fields;
- types, precision, null semantics, key uniqueness and grain;
- authentication and authorization outcomes;
- pagination boundaries and token scope;
- rate limiting and retry guidance;
- compatible and incompatible schema samples;
- semantic metric fixtures with known expected results;
- freshness watermark and source lineage;
- event duplicates/replay if applicable;
- old/new version coexistence and deprecation telemetry;
- access-control regression for every row/field-sensitive interface.

### 6.6 Incident management and support

A contract should define severity, impact assessment, communication channel, acknowledgement target, update cadence, workaround, recovery, and post-incident review. For a data-quality incident, stop or quarantine publication if corrupted output could cause material harm; do not merely leave a green availability dashboard while serving invalid values.

Distinguish:
- **Availability incident:** consumers cannot access the interface.
- **Freshness incident:** interface responds, but data is too old.
- **Quality incident:** values violate declared rules or semantics.
- **Security incident:** data is exposed to an unauthorized principal or access controls fail.
- **Contract incident:** interface behavior differs from documented structure/semantics.
- **Consumer incident:** consumer violates documented usage (e.g., ignores rate limits); still coordinate to limit impact.

Define whether the product can serve last-known-good data. If so, disclose its `as_of`/watermark and status, enforce access using current permissions, and stop serving it once its allowed staleness expires. Stale-but-available data are not automatically safe.

### 6.7 Lifecycle and product portfolio governance

A typical lifecycle:

1. **Proposed:** purpose, consumers, owner, value hypothesis and risk identified.
2. **Designed:** interface options, semantics, governance, cost, SLOs and ADR reviewed.
3. **Built and validated:** contract/schema/quality/security tests pass.
4. **Published:** catalogue entry, docs, consumer registry, support and onboarding available.
5. **Operated:** SLOs, freshness, quality, cost, adoption, incidents and changes monitored.
6. **Deprecated:** consumers notified, alternatives provided, migration status tracked.
7. **Retired:** interface disabled safely; consumers migrated; retention/deletion/audit obligations met.

Review products for:
- active consumers and business value;
- data quality and freshness;
- availability, latency, incident rate and recovery;
- security posture and access recertification;
- change frequency and consumer migration burden;
- cost per query/call/export/event and chargeback/showback fairness;
- duplication with other products;
- owner continuity and runbook readiness.

A product with no owner, no active consumers, or unmanageable risk should not remain indefinitely just because it exists. Retirement requires impact analysis and controlled communication.

## 7. Worked specifications and contract tests

### 7.1 Data-product contract in compact form

```yaml
product:
  id: risk.customer-exposure-summary
  version: v1
  purpose: "Governed summary of committed customer credit exposure"
  grain:
    - customer_id
    - reporting_currency
    - as_of_date
  owner: team-risk-data-products
  technical_owner: team-risk-serving
  steward: team-credit-risk-stewards
  classification: confidential
  source_watermark_required: true
  interfaces:
    - type: rest
      method: GET
      path: /v1/customers/{customer_id}/exposure
      query_parameters:
        reporting_currency: "Required; uppercase three-letter code"
        as_of_date: "Optional YYYY-MM-DD; defaults to latest published snapshot; no silent fallback for a requested date"
    - type: query
      object: risk_product.customer_exposure_v1
      access: approved-risk-analyst-role
  semantics:
    committed_exposure_amount:
      type: decimal-string
      unit: reporting_currency
      null_meaning: "Unavailable is not zero"
    conversion_metadata:
      type: object-or-null
      when_present: "Requires rate_date, rate_source, and policy_version"
      when_null: "No currency conversion was applied"
    as_of_date:
      type: date
      meaning: "Product reporting business date"
    source_watermark:
      type: timestamp-with-timezone
      meaning: "Latest committed source state represented by this snapshot"
    published_at:
      type: timestamp-with-timezone
      meaning: "Publication time; must not precede source_watermark"
    product_version:
      type: string
      value: v1
    quality_status:
      type: enum
      allowed_success_value: passed
  response_metadata:
    request_id: non-empty-string
    schema_version: "1.0"
  quality:
    required_fields_non_null: 100%
    key_uniqueness: 100%
    freshness_target: "At least 99% of eligible scheduled daily snapshot runs publish within 30 minutes of source-watermark commit, measured over a rolling 90-day window; report numerator and denominator"
  security:
    authentication: "approved organizational identity"
    authorization: "per-customer and field-level policy"
    tenant_scope: "derived from trusted identity/policy context"
  compatibility:
    structural_breaking_change: "new major contract version"
    semantic_breaking_change: "new version plus consumer impact review"
  service_targets:
    availability_slo: "99.9% rolling 30 days (illustrative)"
    latency: "p95 <= 300ms, p99 <= 800ms (illustrative workload)"
```

This is a compact human-readable example, not a complete universal schema for a particular API specification language. A production contract must define precise machine validation rules for its chosen format.

### 7.2 Runnable Python contract example

The following standard-library program validates a synthetic response against a small provider contract. It checks required fields, types, key semantics, freshness metadata, and quality status. It does **not** test a live HTTP service, identity provider, row-level authorization, load, or availability SLO; those require integration and operational tests.

```python
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re

REQUIRED_DATA = {
    "customer_id": str,
    "reporting_currency": str,
    "as_of_date": str,
    "committed_exposure_amount": str,
    "conversion_metadata": (dict, type(None)),
    "source_watermark": str,
    "published_at": str,
    "product_version": str,
    "quality_status": str,
}


def parse_timestamp(value, field, errors):
    try:
        # Require an explicit UTC marker or numeric offset; naive timestamps are invalid.
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            errors.append(f"{field} must include a timezone")
            return None
        return parsed
    except (ValueError, AttributeError):
        errors.append(f"{field} must be an ISO timestamp with timezone")
        return None


def validate_exposure_response(response):
    errors = []
    if not isinstance(response, dict) or not isinstance(response.get("data"), dict):
        return ["response.data must be an object"]
    if not isinstance(response.get("meta"), dict):
        return ["response.meta must be an object"]

    meta = response["meta"]
    for field in ("request_id", "schema_version"):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            errors.append(f"meta.{field} must be a non-empty string")
    if meta.get("schema_version") != "1.0":
        errors.append("meta.schema_version must match the v1 schema contract (1.0)")

    data = response["data"]
    for field, expected_types in REQUIRED_DATA.items():
        allowed = expected_types if isinstance(expected_types, tuple) else (expected_types,)
        if field not in data:
            errors.append(f"missing required field: {field}")
        elif not isinstance(data[field], allowed):
            names = " or ".join(t.__name__ for t in allowed)
            errors.append(f"{field} must be {names}")
    if errors:
        return errors

    if not re.fullmatch(r"CUST-[A-Z0-9]+", data["customer_id"]):
        errors.append("customer_id must use the synthetic CUST- identifier format")
    if not re.fullmatch(r"[A-Z]{3}", data["reporting_currency"]):
        errors.append("reporting_currency must be an uppercase three-letter code")
    try:
        parsed_date = date.fromisoformat(data["as_of_date"])
        if parsed_date.isoformat() != data["as_of_date"]:
            errors.append("as_of_date must use canonical ISO YYYY-MM-DD format")
    except (ValueError, TypeError):
        errors.append("as_of_date must use canonical ISO YYYY-MM-DD format")

    try:
        amount_text = data["committed_exposure_amount"]
        amount = Decimal(amount_text)
        if not amount.is_finite():
            errors.append("committed_exposure_amount must be finite")
        elif not re.fullmatch(r"-?\d+\.\d{2}", amount_text):
            errors.append("USD committed_exposure_amount must use two decimal places")
    except (InvalidOperation, TypeError):
        errors.append("committed_exposure_amount must be a decimal string")

    source_watermark = parse_timestamp(data["source_watermark"], "source_watermark", errors)
    published_at = parse_timestamp(data["published_at"], "published_at", errors)
    if source_watermark is not None and published_at is not None and published_at < source_watermark:
        errors.append("published_at must not precede source_watermark")

    conversion = data["conversion_metadata"]
    if conversion is not None:
        for field in ("rate_date", "rate_source", "policy_version"):
            if not isinstance(conversion.get(field), str) or not conversion[field].strip():
                errors.append(f"conversion_metadata.{field} must be a non-empty string")
        try:
            rate_date = date.fromisoformat(conversion.get("rate_date", ""))
            if rate_date.isoformat() != conversion.get("rate_date"):
                errors.append("conversion_metadata.rate_date must use YYYY-MM-DD")
        except (ValueError, TypeError):
            errors.append("conversion_metadata.rate_date must use YYYY-MM-DD")

    if data["quality_status"] != "passed":
        errors.append("quality_status must be passed for this successful-response contract")
    if data["product_version"] != "v1":
        errors.append("product_version must match the v1 endpoint contract")
    return errors


valid = {
    "data": {
        "customer_id": "CUST-1042",
        "reporting_currency": "USD",
        "as_of_date": "2026-10-20",
        "committed_exposure_amount": "1250.00",
        "conversion_metadata": None,
        "source_watermark": "2026-10-20T09:00:00Z",
        "published_at": "2026-10-20T09:12:00Z",
        "product_version": "v1",
        "quality_status": "passed",
    },
    "meta": {"request_id": "req-example-0007", "schema_version": "1.0"},
}
assert validate_exposure_response(valid) == []

missing_field = {"data": dict(valid["data"]), "meta": dict(valid["meta"])}
del missing_field["data"]["source_watermark"]
assert any("missing required field: source_watermark" in e
           for e in validate_exposure_response(missing_field))

bad_amount = {"data": dict(valid["data"]), "meta": dict(valid["meta"])}
bad_amount["data"]["committed_exposure_amount"] = "not-a-number"
assert any("decimal string" in e for e in validate_exposure_response(bad_amount))

bad_scale = {"data": dict(valid["data"]), "meta": dict(valid["meta"])}
bad_scale["data"]["committed_exposure_amount"] = "1250.000"
assert any("two decimal places" in e for e in validate_exposure_response(bad_scale))

bad_date = {"data": dict(valid["data"]), "meta": dict(valid["meta"])}
bad_date["data"]["as_of_date"] = "20261020"
assert any("YYYY-MM-DD" in e for e in validate_exposure_response(bad_date))

bad_timezone = {"data": dict(valid["data"]), "meta": dict(valid["meta"])}
bad_timezone["data"]["published_at"] = "2026-10-20T09:12:00"
assert any("timezone" in e for e in validate_exposure_response(bad_timezone))

bad_chronology = {"data": dict(valid["data"]), "meta": dict(valid["meta"])}
bad_chronology["data"]["published_at"] = "2026-10-20T08:59:00Z"
assert any("must not precede" in e for e in validate_exposure_response(bad_chronology))

bad_currency = {"data": dict(valid["data"]), "meta": dict(valid["meta"])}
bad_currency["data"]["reporting_currency"] = "usd"
assert any("uppercase three-letter code" in e for e in validate_exposure_response(bad_currency))

bad_meta = {"data": dict(valid["data"]), "meta": {"request_id": "req-1"}}
assert any("meta.schema_version" in e for e in validate_exposure_response(bad_meta))

bad_conversion = {"data": dict(valid["data"]), "meta": dict(valid["meta"])}
bad_conversion["data"]["conversion_metadata"] = {"rate_date": "2026-10-20"}
assert any("rate_source" in e for e in validate_exposure_response(bad_conversion))

bad_quality = {"data": dict(valid["data"]), "meta": dict(valid["meta"])}
bad_quality["data"]["quality_status"] = "failed"
assert any("must be passed" in e for e in validate_exposure_response(bad_quality))

print("PASS: valid response and metadata accepted")
print("PASS: missing required field rejected")
print("PASS: invalid decimal and invalid scale rejected")
print("PASS: non-canonical date rejected")
print("PASS: timezone-free timestamp rejected")
print("PASS: publication before source watermark rejected")
print("PASS: lowercase currency rejected")
print("PASS: incomplete response metadata rejected")
print("PASS: incomplete conversion provenance rejected")
print("PASS: failed quality status rejected")
```

Expected output:

```text
PASS: valid response and metadata accepted
PASS: missing required field rejected
PASS: invalid decimal and invalid scale rejected
PASS: non-canonical date rejected
PASS: timezone-free timestamp rejected
PASS: publication before source watermark rejected
PASS: lowercase currency rejected
PASS: incomplete response metadata rejected
PASS: incomplete conversion provenance rejected
PASS: failed quality status rejected
```

The test is intentionally small. Production tests should also validate access decisions, schema compatibility, semantics, pagination, error mappings, and service objectives.

### 7.3 Semantic contract test

A schema test cannot prove that exposure is calculated correctly. Use a tiny synthetic fixture with known expected results:

| Customer | Eligible facility A | Eligible facility B | Cancelled facility | Expected committed exposure |
|---|---:|---:|---:|---:|
| `CUST-1042` | 700.00 USD | 550.00 USD | 900.00 USD | 1,250.00 USD |

Assumption: cancelled facilities are excluded from committed exposure. The expected result is `700 + 550 = 1,250 USD`, not `2,150 USD`. The test should fail if the producer changes the inclusion rule without a contract/version change. For a semantic change, publish a new definition/version, run side-by-side comparisons, and update consumers deliberately.

### 7.4 Consumer-driven contract test plan

For each registered consumer:
1. Capture only the fields, error codes, ordering, and semantics it actually relies on.
2. Run the consumer contract against provider test/staging responses.
3. Verify required fields, accepted optional fields, null handling, and unknown enum behavior.
4. Exercise 401/403/404/429/503 paths and the documented retry policy.
5. Verify a caller cannot access another customer’s row or a restricted field.
6. Verify pagination tokens cannot be reused across tenants or entitlements.
7. Compare semantic fixtures to known results.
8. Run old and new versions in parallel during migration.
9. Block release when a breaking consumer contract fails unless a reviewed exception is recorded.
10. Store versioned test evidence and link it from the product catalogue/change record.

## 8. Production scenarios and trade-offs

### 8.1 A product family across analytical, ML, and AI consumers

The same domain can publish related products without forcing all consumers through one interface:

- **Exposure analytical product:** governed mart and semantic definitions (Topic 02); contract defines grain, measures, filters, and historical behavior.
- **Exposure feature product:** offline/online feature contract (Topic 04); contract defines event/prediction time, point-in-time correctness, freshness, and feature version.
- **Knowledge retrieval product:** permission-aware retrieval API (Topic 06); contract defines identity propagation, allowed evidence, citations, abstention, and revocation behavior.
- **Customer exposure API:** operational lookup contract; contract defines request/response, per-customer authorization, latency, quotas, and errors.
- **Exposure event feed:** event contract; contract defines event identity, schema evolution, duplicate/replay semantics, ordering, and retention.

These products may share domain definitions and lineage but must not pretend their freshness or consistency guarantees are identical. A daily analytical snapshot, an online feature, and a permission-aware passage retrieval endpoint answer different consumer needs.

### 8.2 Multiple consumers and a breaking change

During the rename/definition change described in Section 6.4, the provider’s consumer registry reveals three downstream teams. The change is blocked from unannounced rollout because it affects both field shape and metric meaning. The provider creates v2, tests v1/v2 in parallel, and obtains consumer-specific migration evidence.

If one consumer cannot migrate by the proposed sunset, options include extending v1 temporarily, helping the consumer migrate, or approving an explicit exception with risk and cost documented. Do not indefinitely maintain every old version without an owner, support plan, or usage review. Do not silently change v1’s semantics to simplify the provider implementation.

### 8.3 Service tiers and fairness

An illustrative tiering model:

| Tier | Intended consumer | Illustrative service profile | Governance |
|---|---|---|---|
| Standard | Non-critical analysis | Daily freshness, business-hours support | Shared capacity, documented best effort within target |
| Business-critical | Operational workflow | Tighter freshness/latency and defined incident response | Reserved capacity or stronger redundancy; consumer acceptance |
| Regulated/high-impact | Sensitive risk or compliance use | Explicit access/audit, stricter recovery and change control | Formal approval, evidence retention, tighter change gates |

These are categories, not universal targets. A higher tier costs more to operate and support. Define eligibility, capacity reservation, quotas, price/showback, and downgrade/upgrade rules. Avoid promising every consumer the most expensive SLO by default.

### 8.4 Cost allocation and adoption

Measure:
- calls/queries/events/files by consumer and product version;
- successful and failed request volume;
- compute/storage/egress and reranking/model cost where relevant;
- cost per successful, authorized response or completed export;
- support incidents and engineering effort;
- active consumers, adoption trend, and consumer satisfaction;
- duplicate products and avoidable bespoke extracts.

Use chargeback when accurate metering and ownership are mature; use showback while building cost transparency. Cost allocation must not expose sensitive usage details to unauthorized teams. Optimize expensive consumers through quotas, bulk interfaces, caching within freshness/authorization constraints, or dedicated capacity where justified.

### 8.5 Operational failure decisions

| Failure | Contracted response |
|---|---|
| Upstream source late | Publish status/watermark; serve last-known-good only within agreed staleness and current access policy |
| Quality check fails | Quarantine publication or mark explicitly degraded according to risk policy; do not claim quality passed |
| API capacity exhausted | Return documented 429/503 and retry guidance; protect other consumers with fair quotas |
| Authorization dependency unavailable | Deny protected access or return safe temporary error; do not fail open |
| Consumer ignores schema contract | Notify consumer owner, provide evidence, and use documented throttling/support/escalation |
| New version fails tests | Block release, retain previous stable version, document rollback |
| Deprecated version still used | Contact registered consumer, agree migration or exception, do not silently break it |
| Data deletion/correction requested | Follow source-of-truth policy, propagate correction/deletion to product copies and caches, preserve only required audit evidence |

## 9. Practical exercises and expected deliverables

### 9.1 Beginner — describe an exposure product

**Task:** Write a one-page description of a synthetic Customer Exposure Summary product.

**Required fields:** purpose, exclusions, owner, steward, three consumer types, one interface, grain, one quality rule, access model, freshness expectation, support path.

**Expected output:** a named product with an accountable owner and a documented consumer-facing interface, not merely a table name.

**Acceptance criteria:**
- All required fields are present.
- Grain and exposure definition are unambiguous.
- At least one security constraint and one measurable quality/freshness target are stated.
- A reviewer can identify whom to contact for an incident.

### 9.2 Intermediate — complete specification and consumer contract

**Task:** Design the product using Section 4 and select two interfaces for two consumers.

**Deliverables:**
1. Product specification with schema, semantics, quality, lineage, access and retention.
2. API/interface definition with request, response, errors, pagination where applicable, authentication/authorization, and rate limits.
3. Provider/consumer responsibilities.
4. SLI/SLO table with denominators, windows and measurement methods.
5. Contract test suite with positive and negative cases.
6. Compatibility policy and consumer registry fields.

**Acceptance criteria:**
- Every promise is measurable or explicitly marked as not guaranteed.
- Null, zero, units, currency, grain, time and key semantics are explicit.
- Access is enforced per resource/row/field as needed.
- Tests include at least one unauthorized request, one invalid schema, one semantic fixture, and one stale-data case.
- The API schema, quality rules and tests agree on field names and types.

### 9.3 Advanced — govern a breaking product-family change

**Task:** Change an exposure metric definition and rename one field while three consumers have different migration windows.

**Deliverables:**
1. Impact analysis from the consumer registry and lineage graph.
2. Structural and semantic compatibility assessment.
3. Version/deprecation plan, timeline, owner, communications and rollback.
4. Parallel v1/v2 semantic reconciliation results.
5. Contract tests and consumer acceptance evidence.
6. SLO/error-budget impact and cost of dual-version operation.
7. ADR with options, risks, exceptions and retirement criteria.

**Acceptance criteria:**
- The field rename and metric definition change are both classified as breaking.
- v1 retains its documented semantics while supported.
- v2 passes provider and consumer contract tests.
- Every critical consumer has a migration owner and status.
- Sunset depends on measured usage and documented risk acceptance, not just a calendar date.
- Security revocation is not delayed by compatibility promises.

### 9.4 Review scenario

A producer changes `committed_exposure_amount` from decimal string to floating-point number, includes cancelled facilities, removes `source_watermark`, and increases freshness lag from 20 to 90 minutes. Identify the issues.

**Expected answer:**
- Type/precision change: structural breaking risk.
- Inclusion of cancelled facilities: semantic breaking change.
- Removing `source_watermark`: breaking if required for provenance/freshness contract.
- 90-minute lag: breach of the illustrative 30-minute freshness target.
- Required actions: stop unreviewed rollout, assess impact, restore or version behavior, notify consumers, test both schema and semantics, record incident/change, and update the contract only through governance. Updating documentation after silently changing production is not sufficient.

## 10. Common mistakes and troubleshooting

| Mistake / symptom | Why it fails | Corrective action |
|---|---|---|
| Calling a table a product without an owner | No accountability or support | Assign owner, steward, purpose, interface and lifecycle |
| Publishing an API without semantics | Consumers infer units, grain or null meaning | Specify business definitions and test them |
| Treating schema-valid as semantically correct | Values can change meaning without changing type | Add semantic fixtures, version metric definitions |
| Adding a required field and calling it additive | Strict consumers may reject the response | Prefer optional addition or new major contract |
| Assuming new enum values are always compatible | Exhaustive consumers may fail | Document enum evolution and test consumers |
| No consumer registry | Breaking impact is unknown | Register consumers, versions, criticality and contacts |
| One interface for every workload | Bulk, analytical, and low-latency needs conflict | Select interface per access pattern |
| SLO without a denominator/window | Teams calculate incompatible availability | Define eligible requests, exclusions, window and telemetry |
| Calling an SLO an SLA without agreement | Creates false expectations | Separate internal objectives from formal agreements |
| Silent semantic change | Historical reports/models diverge | Version definitions and run side-by-side comparison |
| Deprecation notice without usage evidence | Critical consumers remain undiscovered | Use registry plus telemetry and migration sign-off |
| Consumer retry storm after 429/503 | Worsens provider outage | Require bounded retries, exponential backoff and jitter |
| Idempotency claimed for all endpoints | Duplicate writes may still occur | Define idempotency only where implemented and tested |
| Shared service account bypasses row policy | Privilege escalation | Enforce end-user authorization at each access boundary |
| Exposing internal schema as public contract | Physical redesign breaks consumers | Publish stable logical interface, not accidental storage layout |
| Caching without freshness and access scope | Stale values or cross-consumer leakage | Define cache key, TTL, invalidation and reauthorization |
| No deletion/retention plan for exports/events | Data copies outlive source policy | Assign downstream deletion duties and audit retention |
| Product has no retirement plan | Unowned versions and cost accumulate | Define sunset criteria, owner, usage window and archive rules |

## 11. Review questions, mastery criteria, and completion gate

### 11.1 Review questions

1. What makes a data product different from a table, pipeline, API, or platform?
2. Which consumer needs determine whether you publish a view, API, file, stream, feature endpoint, or retrieval endpoint?
3. What is the grain of your product, and how are units, nulls, time, keys and business definitions represented?
4. Which promises are SLOs and which are formal SLAs?
5. How do provider and consumer responsibilities differ?
6. Why can a schema-compatible change still be semantically breaking?
7. What is your policy for adding fields, enum values, changing types, renaming fields, and changing metric definitions?
8. How will you find every consumer affected by a change?
9. How do authentication, authorization, tenant isolation, masking and audit apply to every interface?
10. How will you test quality, freshness, error semantics, pagination, and compatibility?
11. What happens if a source is late or a quality rule fails?
12. What evidence is required before deprecating or retiring a product version?

### 11.2 Mastery criteria

You can:
- Explain the product boundary and name its owner, purpose, consumer groups and supported interfaces.
- Select an interface based on measured consumer needs and trade-offs.
- Define product grain, schema, semantics, units, nullability, lineage, quality and access.
- Write a contract with provider and consumer obligations and measurable SLI/SLO definitions.
- Design authentication, authorization, rate limits, pagination, errors and idempotency where applicable.
- Distinguish structural from semantic compatibility and identify breaking changes.
- Plan version transitions with consumer registry, communication, parallel validation, rollback and retirement evidence.
- Execute a contract test and explain exactly what it does and does not prove.
- Track freshness, quality, availability, latency, adoption, cost and incident outcomes.
- Package analytical models, ML features and permission-aware retrieval without claiming their guarantees are interchangeable.

### 11.3 Completion checklist

- [ ] Product purpose, exclusions, owner, steward and support route are explicit.
- [ ] Intended consumers, catalogue entry and consumer registry are defined.
- [ ] Interface selection is justified against payload, latency, throughput, freshness, governance and cost.
- [ ] Schema and semantics define grain, keys, types, units, null behavior and timestamps.
- [ ] Quality rules specify threshold, denominator, cadence and failure behavior.
- [ ] Lineage, provenance, classification, access, masking, retention and deletion are defined.
- [ ] API or interface contract includes errors, pagination, authentication, authorization and quotas as applicable.
- [ ] Provider and consumer responsibilities are written and testable.
- [ ] SLI/SLO targets are explicitly illustrative or approved, with measurement windows and exclusions.
- [ ] Structural and semantic compatibility rules are documented.
- [ ] Breaking-change, versioning, deprecation and retirement procedures are defined.
- [ ] Provider and consumer contract tests run in CI; negative security tests are included.
- [ ] Monitoring, incident response, support escalation and rollback are documented.
- [ ] Cost metering and service-tier rules are defined.
- [ ] Product lifecycle review has owners, cadence, adoption measures and retirement criteria.
- [ ] Topic 02 semantic definitions, Topic 04 feature contracts, and Topic 06 permission-aware retrieval guarantees are preserved at their product interfaces.
- [ ] Topic 08 cache, invalidation, and freshness requirements are handed off explicitly.

### 11.4 Completion gate and handoff

Topic 07 is complete when a consumer can discover the product, understand its data and limitations, obtain authorized access, validate contract conformance, handle errors and freshness, and migrate safely when behavior changes. A schema file alone is not a consumer contract; the semantics, service behavior, governance and change process are part of the product.

**Handoff to Topic 08:** provide the interface access patterns, cacheability constraints, maximum staleness, freshness SLO, invalidation events, authorization scope, and tests for stale data or revoked access.

**Module integration:** the final analytics and AI data-serving architecture should show how analytical marts/semantic models, operational serving, ML features, document retrieval, data products, APIs, and caches serve distinct consumers under consistent governance. Products are the consumer-facing contracts across those serving layers—not a substitute for designing the layers themselves.
