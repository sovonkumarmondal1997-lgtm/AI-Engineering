# Unit 12 — Observability Cost, Cardinality, and Data Retention

**Target file:** `12-observability-cost-cardinality-and-data-retention.md`  
**Module:** Stage 2E — Production DevOps & Platform Engineering / M11 — Production Observability Stack and Performance Operations  
**Scope:** Technical measurement, attribution, safe volume reduction, retention engineering, guardrails, and operational governance.

> This unit owns the **technical levers** of observability cost: measuring, attributing, and controlling series, log, and trace volume and retention. M15 owns the **financial model** (pricing, chargeback, budgeting, vendor negotiation). No real prices or vendor cost figures appear in this course; costs are expressed in measured units (series, bytes, spans, query-seconds, GB-days) and relative comparisons.

> **Evidence labels used throughout:** `[SYNTHETIC]` means generated data; `[ILLUSTRATIVE]` means arithmetic or a sample threshold that must be replaced with measured values; `[ASSUMPTION]` means a design choice inferred for this local lab; `[VERIFY]` means a metric, API, configuration field, UI, or behavior that must be checked against the installed version and official documentation.

## 0. Unit orientation and learning contract

### What this unit does

This unit teaches how to answer four questions with evidence:

1. **What telemetry are we producing?** Measure active time series, samples, log bytes, streams, spans, query activity, resource use, and retention.
2. **Where is the volume coming from?** Attribute measurements to jobs, namespaces, services, metrics, log levels, and trace services when trustworthy dimensions exist.
3. **What can safely be reduced?** Normalize labels, aggregate, sample carefully, adjust retention, reduce duplicate collection, and optimize queries without destroying incident evidence.
4. **How do we prevent regressions?** Maintain a metric catalog, measured-unit budgets, CI lint, fail-loud guardrails, staged deprecation, and a cardinality incident runbook.

It does **not** cover vendor pricing, financial chargeback, commercial negotiation, or a general replacement for M15. It does not require a SaaS service. Prometheus, Loki, OpenTelemetry Collector, Kubernetes, and long-term storage capabilities vary by version; every version-sensitive step is marked `[VERIFY]`.

### Prerequisites and readiness check

The learner should already understand Prometheus scraping and PromQL, Grafana dashboards, structured logs, OpenTelemetry spans, alert rules, SLOs, and scheduled-job monitoring (M11 Units 1–11). Before starting, verify that you can:

- distinguish a metric series from a sample;
- find a service or job in a local metrics endpoint;
- read a structured log line without exposing secrets;
- explain why a trace is not a population-level latency distribution;
- run Python 3 and unit tests;
- stop and clean up local containers.

If a full observability stack would exceed a laptop's capacity, use the **Core+Logs** profile for metrics and log labs, and fixture-based trace exercises. Start only the component needed for the current lab. A 4-core/8-GB/30-GB laptop is a constrained lab environment; never run every component at once merely to follow a diagram.

### Learning outcomes

By completion, you should be able to measure the major telemetry units, calculate label-combination upper bounds, identify high-cardinality patterns, generate a tested cost-driver report, safely reduce metrics/logs/traces, define retention decision records, forecast telemetry volume from measured ratios, run a bounded cardinality game day, and enforce a documented metric catalog.

### Study sequence and scope map

| Sequence | Focus | Artifact | Verification evidence |
|---|---|---|---|
| 1 | Cost vocabulary and cardinality | Hand calculations | Unit-checked arithmetic |
| 2 | Measurement and attribution | Cost-driver report | Source, window, unit, missing-data state |
| 3 | Safe reduction | Before/after record | Critical alerts and evidence preserved |
| 4 | Systematic governance | Catalog, unused detector, CI lint | Automated tests and owner review |
| 5 | Incident response | Runbook and emergency brake | Controlled game-day timeline |
| 6 | Retention and forecasting | Decision records and growth model | Deletion verification or explicit `[VERIFY]` limitation |

This unit builds on M11 Units 1–11. Unit 13 performance testing can use the resulting telemetry budgets and query baselines; M11 capstones can use the catalog and incident evidence bundle.

## 1. Mental model: why observability has a cost

Observability consumes compute, memory, disk, network, query capacity, and human attention. Every additional label combination, log event, span, dashboard panel, or frequent query adds work somewhere in the pipeline.

**Principle: unused telemetry is waste; missing telemetry is risk.** The target is not “the smallest possible telemetry footprint.” The target is the least expensive telemetry set that still answers required SLO, debugging, security, and incident questions with acceptable reliability.

### Measurable units (not prices)

| Signal or operation | Useful unit | What it tells you | What it does not tell you |
|---|---|---|---|
| Metrics | Active time series; samples/s; bytes stored | Series pressure and ingestion rate | Exact memory or storage from series count alone |
| Logs | Bytes/s, bytes/day, streams, records/s | Volume and stream churn | Whether the logs contain useful incident evidence |
| Traces | Spans/s, bytes/span, retained spans, sample fraction | Trace ingestion and retained detail | Whether rare errors are represented |
| Queries | Query-seconds, series scanned, evaluations/s, refreshes/min | Query workload and contention | A universal cross-backend cost score |
| Storage | Bytes, GB-days, retention duration, resolution | Stored volume over time | Monetary cost without a pricing model |
| Pipeline | CPU, memory, queue depth, dropped/accepted items | Processing pressure and data loss risk | Full downstream completeness from one component metric |
| Operations | Incident time, alert noise, investigation steps | Human cost and visibility | A defensible monetary estimate without evidence |

A time series is a metric name plus a unique label set. A sample is one timestamped value in that series. Cardinality is the number of distinct label combinations, not the number of label names. Ingestion volume is the number of samples or bytes written over time. They are related but different dimensions: a small number of series scraped very frequently can generate many samples; many series scraped infrequently can still create head-series pressure.

## 2. L1 — Understand what drives cost for each signal

### 2.1 Metrics

Prometheus typically maintains a head of active series and appends samples at scrape/evaluation time. More active series increase metadata and memory pressure; more frequent samples increase ingestion work and storage growth. Exact resource impact depends on labels, churn, sample rate, metric type, version, and workload. Do **not** use one universal “bytes per series” or “memory per series” constant.

A histogram generally exposes bucket series plus count and sum (and sometimes implementation-specific additional series). With \(B\) configured finite bucket boundaries, a classic histogram commonly has \(B+1\) bucket series including `+Inf`, plus count and sum per label set. Verify the actual exposition because generated buckets and naming differ by client and histogram type `[VERIFY]`.

### 2.2 Logs

A first-order volume estimate is:

\[
\text{bytes per day} \approx \text{average bytes per event} \times \text{events per second} \times 86{,}400
\]

This is raw volume arithmetic; compression, indexing, replication, and backend overhead alter stored size. Stream identity often depends on a label set. High-cardinality labels can create many streams and operational overhead `[VERIFY]` for the backend/version. Common causes include verbose debug logs, duplicate shippers, repeated stack traces, high-volume health checks, and raw payload logging.

Prefer structured fields and stable labels. Do not put arbitrary request IDs, user IDs, or full URLs in indexed labels. Keep sensitive values out of logs by default. A high-volume event that can be represented faithfully as a counter may be converted to a metric, but preserve sampled examples and incident context where needed.

### 2.3 Traces

A simplified volume model is:

\[
\text{retained spans/s} \approx \text{incoming spans/s} \times \text{sampling fraction}
\]

\[
\text{retained bytes/day} \approx \text{retained spans/s} \times \text{average bytes/span} \times 86{,}400
\]

This excludes indexes, replication, metadata, and variable span sizes. Head sampling decides early; tail sampling can decide after observing a trace but requires state/buffering and has operational constraints `[VERIFY]`. Sampling slow/error traces can improve diagnostic value, but only if the policy and implementation actually preserve them. Duplicate Collector pipelines, duplicate instrumentation, tight-loop spans, and health-check traffic can inflate volume. Attribute/event limits and sampling support vary by component/version `[VERIFY]`.

### 2.4 Query and dashboard work

A useful mental model is:

\[
\text{query work over a window} \propto \text{query frequency} \times \text{work per query}
\]

Broad selectors, large time ranges, expensive aggregations, high-cardinality grouping, short dashboard refresh intervals, many viewers, and repeated alert evaluations all contribute. A panel refreshed every 5 seconds creates 12 refreshes/minute per viewer; 20 concurrent viewers create up to 240 panel refreshes/minute for that panel before retries or dashboard panels are counted `[ILLUSTRATIVE]`.

Use tighter selectors, sensible time ranges, appropriate refresh intervals, recording rules for repeated expensive calculations, and query limits/timeouts where supported `[VERIFY]`. Query-cost proxies are backend-specific: scanned series, samples, bytes, query duration, and queue time are not interchangeable.

### 2.5 Worked multiplicative-cardinality example

`[ILLUSTRATIVE]` Suppose an instrumented request metric can have:

- 5 services;
- 20 route templates per service;
- 5 status classes;
- 3 methods;
- 100 pods per service fleet.

Upper-bound arithmetic:

1. \(5 \times 20 = 100\) service/route combinations.
2. \(100 \times 5 = 500\) combinations after status class.
3. \(500 \times 3 = 1{,}500\) after method.
4. \(1{,}500 \times 100 = 150{,}000\) possible series for a metric with that label set.

Assumptions: every combination occurs, label dimensions are independent, every pod exports each combination, and the count is for one metric family/series shape. Real counts may be lower because combinations are absent, or higher after adding more labels, histogram buckets, replicas, or separate metrics. For a classic histogram with 12 finite boundaries, the 13 bucket series including `+Inf`, count, and sum give 15 series per label set; the illustrative 150,000 label combinations could therefore imply up to \(150{,}000 \times 15 = 2{,}250{,}000\) histogram-related series before other metrics. Confirm actual bucket exposition `[VERIFY]`.

Adding a dimension multiplies possible combinations. It is not a small additive cost.

### 2.6 Cardinality explosion patterns

| Risky dimension | Why it grows | Safer replacement |
|---|---|---|
| `user_id`, `session_id`, `request_id` | Nearly unique per event | Trace/log field, not metric label |
| Raw URL with IDs/query string | Route count grows with identifiers | Framework route template, e.g. `/orders/{order_id}` |
| Timestamp or arbitrary error text | Unbounded values | Time-series timestamp; bounded error category |
| Hash of a user/request ID | Still many distinct hashes | Remove from metric labels |
| Churny pod/container IDs | New values across deploys/autoscaling | Aggregate by stable service/namespace for long-term views; retain instance labels only when needed |
| Arbitrary tenant ID | Tenant population may be large and changing | Bounded tier/segment or controlled tenant attribution outside high-volume metric labels |

Hashing hides the original value but does not reduce the number of distinct values. Exemplars can link a metric observation to a trace without turning every trace ID into a label, if supported and correctly configured `[VERIFY]`.

### 2.7 Retention fundamentals

Retention can be constrained by **time** (keep data for N days), **size** (cap disk usage), **resolution** (raw versus aggregated points), and **tier** (hot versus long-term storage). These controls interact. Size-based retention can remove data sooner during a volume spike. Recording rules pre-aggregate data and retain selected questions, but lose some drill-down detail. Storage-system downsampling is different: it is a backend capability with its own behavior `[VERIFY]`.

Thanos, Mimir, and VictoriaMetrics are awareness-level alternatives for longer-term metrics architectures; no installation is required. Verify current capabilities, operational complexity, and retention/deletion behavior in official documentation before adopting any of them.

### 2.8 Basic cost visibility signals

| Example signal | Potential use | Limitation |
|---|---|---|
| `prometheus_tsdb_head_series` `[VERIFY]` | Head-series pressure trend | Does not alone predict memory or stored bytes |
| `scrape_samples_scraped` `[VERIFY]` | Samples scraped by target/job | Scrape success is not the same as all samples being accepted/stored |
| `prometheus_tsdb_symbol_table_size_bytes` `[VERIFY]` | Symbol table size trend if exposed | Not a complete TSDB size metric |
| Loki bytes ingested by stream/tenant `[VERIFY]` | Attribute log volume where available | Exact names/labels depend on version/configuration |
| OpenTelemetry Collector accepted spans `[VERIFY]` | Track span input/processing | Exact names/components and dropped-span signals vary |

Discover actual names from the local `/metrics` endpoint, Prometheus UI/API, or component self-telemetry. Search metric metadata before writing rules. Monitor the telemetry pipeline itself: an absent cost metric can mean zero traffic, exporter failure, scraping failure, or a changed metric name.

## 3. L2 — Measure and find cost sources

### 3.1 Prometheus cardinality investigation

Start with a short, bounded measurement window. Inspect the TSDB status page and use `promtool tsdb analyze` only if supported by the installed version and local TSDB snapshot format `[VERIFY]`. Do not run expensive scans repeatedly against a stressed backend.

Illustrative PromQL (validate selector and API behavior against the installed version):

```promql
topk(10, count by (__name__) ({__name__=~".+"}))
count by (job) ({__name__=~".+"})
```

The first expression counts series per metric name and shows the ten largest counts; the second groups series by `job`. Both can be expensive because they select broadly. Run during a controlled window and consider a TSDB status/analyzer alternative. These queries are not a perfect cost ranking: sample rate, series churn, label length, metric type, retention, query usage, and storage layout matter.

Discover real series and labels before using a query:

```promql
up
count by (job, instance) (up)
```

Use the Prometheus UI/API to inspect label names/values `[VERIFY]`. Avoid copying all label values into a report if the set is huge or sensitive. For an exact target, compare a small time window and record query duration and backend resource behavior.

### 3.2 Log and trace volume measurement

If backend telemetry is unavailable, measure local fixtures reproducibly:

```bash
wc -c fixtures/logs/*.jsonl
du -b fixtures/logs/*.jsonl
python3 scripts/measure_fixtures.py --logs fixtures/logs --traces fixtures/traces
```

`wc -c` counts bytes in files; `du` reports filesystem allocation in a platform-dependent way, so do not confuse allocated blocks with logical bytes. For logs, attribute bytes by `app`/`level` only when those fields are present and parseable. For traces, count spans by service from a known export schema; do not assume every backend's JSON format is identical.

A local backend can provide richer counts through metrics or APIs, but names and response formats are `[VERIFY]`. Keep measurement window, source, unit, missing-data status, and caveats with every number.

### 3.3 Attribution and cost-driver report

A cost-driver report must not blend series, bytes, spans, and query-seconds into one arbitrary score. Produce separate top-N lists by unit, and attach evidence.

Minimum report columns:

- `measurement`, `value`, `unit`, `window_start`, `window_end`, `source`;
- `attribution_dimension`, `attribution_value`;
- `status` (`measured`, `missing`, `unsupported`, `invalid`);
- `caveat`.

Missing measurements must remain missing; never silently replace missing data with zero.

### 3.4 Measurement baselines

Before changing anything, capture: timestamp/window, active series, samples/s, log bytes, span count/bytes, process CPU/memory, disk use, query/dashboard latency, and critical telemetry to preserve. Keep workload, scrape interval, warm-up, deployment churn, and test duration comparable. Repeat measurements; one run is not a reliable baseline.

## 4. L2 — Technical levers to reduce volume safely

### 4.1 Metrics reduction

Prometheus relabeling controls can drop or retain selected samples/labels. A `metric_relabel_configs` example is shown below as a pattern, not a universal production policy:

```yaml
# [VERIFY] Validate against the installed Prometheus version and scrape job.
scrape_configs:
  - job_name: "lab-app"
    static_configs:
      - targets: ["<LAB_APP_HOST>:<LAB_APP_PORT>"]
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: "lab_debug_.*"
        action: drop
```

This removes matching samples after scrape processing and before ingestion. It does not fix the source of an unbounded label and may discard useful evidence. Prefer source-level normalization first. Validate with `promtool check config <PROMETHEUS_CONFIG>` `[VERIFY]`, inspect target/scrape health, and prove required SLO metrics remain. Roll back by restoring the reviewed config and reloading/restarting according to the deployment model.

Other levers:

- Tune scrape interval per job based on the question and acceptable detection latency.
- Use exporter collector allow/deny controls and kube-state-metrics allow-listing only after checking exact flags `[VERIFY]`.
- Bound route, status, method, error-category, and environment values.
- Design histogram buckets around actual decision thresholds; avoid excessive bucket counts.
- Use recording rules for repeated aggregations while retaining raw data for the necessary drill-down window.
- Compare counters, gauges, histograms, summaries, and native histograms based on semantics and support `[VERIFY]`.

`sample_limit`, `label_limit`, and label/value length limits are guardrails, not safe graceful degradation guarantees `[VERIFY]`. A limit breach may cause a scrape/target to fail. Pair every limit with an alert, owner, expected failure mode, and intentional breach test.

### 4.2 Log reduction

- Set levels intentionally; disable routine debug verbosity outside bounded debug windows.
- Drop routine health-check records only after proving they are not used for availability/security checks.
- Deduplicate repeated messages and sample repetitive noise while preserving the first occurrence, counts, representative examples, and rare errors.
- Avoid duplicate shippers and duplicate Collector pipelines.
- Use structured fields, compression, tiered retention, and bounded stream labels.
- Redact secrets and payloads before shipping.
- Convert high-volume repeated events into counters only when the count preserves the required semantics.

Test the filter against a replayable incident fixture. The fixture must include a rare critical line, error context, and required fields; the reduction must preserve those lines and fields.

### 4.3 Trace reduction

Use documented sampling policies, attribute allow-lists, size/event limits, and health-check/internal-noise filtering where supported `[VERIFY]`. Avoid creating a span for every iteration of a tight loop unless it answers a diagnostic question. Check for duplicate SDK instrumentation and duplicate Collector routes.

Required regression test: a fixture with an error trace and a slow trace must remain retained under the lab's policy. The guarantee is only as strong as the tested policy and actual topology; do not claim 100% error retention unless every relevant sampling stage is shown to preserve it.

### 4.4 Pipeline and query reduction

Inspect Collector CPU/memory, queues, retries, accepted/refused/dropped telemetry, and downstream errors using locally exposed self-telemetry `[VERIFY]`. Batching can reduce overhead; queues can absorb bursts but consume memory/disk and may eventually drop data. Backpressure should be visible, not hidden. Verify there is no duplicate agent or Collector shipping the same source twice.

For queries: reduce range and selector breadth, use recording rules for repeated expensive computations, slow dashboard refreshes, and tune alert evaluation frequency to the detection requirement. Query timeout/limit configuration is backend-specific `[VERIFY]`.

### 4.5 Retention policy design

Retention must be justified by questions and risk, not by habit. A policy record should state:

```yaml
# [ILLUSTRATIVE] Retention decision record
signal: metrics
owner: "<TEAM>"
question: "Can we investigate a latency regression and compare weekly SLO behavior?"
raw_resolution_window: "<TO_DECIDE>"
aggregate_window: "<TO_DECIDE>"
retention_basis: "time_and_size"
sensitivity: "low_after_label_review"
incident_window: "<TEAM_DEFINED>"
deletion_method: "<BACKEND_SPECIFIC_VERIFY>"
verification_evidence: "<QUERY_OR_TEST_RESULT>"
approval: "<OWNER>"
review_date: "<YYYY-MM-DD>"
rollback_plan: "<HOW_TO_RESTORE_POLICY>"
```

Create separate records for metrics, logs, and traces. Consider the incident investigation window, SLO/capacity trend needs, sensitivity, volume, operational deletion mechanics, compliance/audit constraints, evidence snapshots, legal-hold awareness, owner, approval, review date, and rollback. This is not legal advice.

Compliance-driven minimum retention and privacy-driven maximum retention can conflict; resolve with the responsible legal/security/privacy owners. Never promise deletion until it has been verified against the selected backend/version `[VERIFY]`. Test whether deletion applies to indexes, chunks/blocks, replicas, backups, and caches as relevant.

### 4.6 Attribution and budgets/guardrails

Attribute measured units to team/service/namespace/environment when trustworthy. A budget is a threshold in a single unit, for example “series for job X” or “log bytes/day for service Y,” not a blended cost score. Pair each limit with an owner, an alert, expected behavior, and an intentional failure test.

Potential controls include Prometheus scrape limits, Loki tenant/stream/ingestion limits, Collector processor limits, and Kubernetes admission-policy guardrails `[VERIFY]`. Fail loudly: a limit breach should create a visible signal and actionable event. Silently losing critical telemetry is a failed guardrail.

## 5. L3 — Systematic cost engineering

### 5.1 Telemetry value assessment

For each metric, stream, span attribute, dashboard, and alert, record:

- owner;
- question/SLO/incident workflow supported;
- evidence of usage;
- measured volume/cardinality/query behavior;
- removal risk;
- safer aggregation/replacement;
- review date.

An unused-telemetry detector can search Git-stored dashboards, alert rules, and recording rules for metric names. But **absence from Git references does not prove telemetry is unused**: ad-hoc incident queries, external consumers, automation, and undocumented runbooks may depend on it. The detector must produce candidates for owner review, never delete or disable telemetry automatically.

### 5.2 Cardinality budgets and metric catalog

A catalog entry should include metric name, type, unit, help/purpose, owner, bounded labels, maximum values per label, estimated series budget, histogram bucket count, scrape frequency, SLO/alert/dashboard consumers, sensitivity/PII status, retention tier, and deprecation state.

`[ASSUMPTION]` Example schema:

```yaml
metrics:
  - name: api_request_duration_seconds
    type: histogram
    unit: seconds
    purpose: "Measure request latency by bounded operation dimensions"
    owner: "team-api"
    labels:
      service: {max_values: 5, bounded: true}
      route: {max_values: 30, bounded: true}
      status_class: {max_values: 5, bounded: true}
    bucket_count: 12
    scrape_interval_seconds: 15
    estimated_series_budget: 15000
    consumers: ["api-latency-slo", "api-overview"]
    sensitivity: "no_pii"
    retention_tier: "raw-short"
    deprecation: "active"
```

The example budget is illustrative and must be recalculated using actual series shape and bucket behavior. CI lint should reject undocumented metric names and known dangerous labels such as `request_id`, `user_id`, `session_id`, raw URL, and timestamp. Keep the allow-list maintainable and permit reviewed exceptions with an owner and rationale.

### 5.3 Label design and alternatives

Prefer stable bounded labels. Use route templates instead of raw paths, status classes instead of arbitrary status text, and controlled error categories instead of exception messages. Put request/trace identifiers in logs/traces; use exemplars for metric-to-trace linking if supported `[VERIFY]`. Instance/pod labels can help short-term diagnosis but may create churn in long-term aggregates. Hashing does not make unbounded values bounded.

### 5.4 Aggregation and downsampling

A recording rule can precompute a repeated aggregation, for example a per-route request rate. This reduces repeated query work but does not automatically delete raw series or create backend-native downsampling.

```yaml
# [VERIFY] Example rule; validate names and rule syntax in the installed version.
groups:
  - name: lab-aggregates
    interval: 1m
    rules:
      - record: lab:http_requests:rate5m
        expr: sum by (service, route, status_class) (rate(http_requests_total[5m]))
```

This aggregate can answer “what was the request rate by service/route/status class?” It cannot reconstruct individual pod behavior, arbitrary labels that were dropped, or a high-resolution per-instance spike. Keep raw metrics for the short-term drill-down window and aggregates longer only if the storage architecture supports it. Storage-system downsampling is a separate backend feature `[VERIFY]`.

### 5.5 Growth forecasting and telemetry unit economics

Use measured ratios, not prices:

\[
\text{log bytes per 1,000 requests} =
\frac{\text{measured log bytes}}{\text{request count}} \times 1000
\]

\[
\text{projected log bytes/day} =
\text{bytes/request} \times \text{projected requests/day}
\]

For series, model stable series per instance plus label dimensions and churn; do not assume a linear model if cardinality grows with traffic. For traces, estimate spans/request × requests/s × sampling fraction × average span bytes.

`[SYNTHETIC]` If a fixture emits 2,400,000 bytes over 12,000 requests, that is 200 bytes/request, or 200,000 bytes per 1,000 requests. At 120,000 requests/day, the simple estimate is 24,000,000 bytes/day before compression/overhead. Check units: bytes/request × requests/day = bytes/day.

Sensitivity analysis should vary traffic, instance count, cardinality per instance, sampling fraction, and retention days. Learners must populate final results with local measurements; do not use the sample as a production prediction.

### 5.6 Cost versus visibility and tiered observability

A missing metric can delay detection; a missing error trace can lengthen diagnosis; short retention can make a regression unreproducible. These costs are real operational risks but must not be converted to fabricated monetary amounts.

Use service criticality to choose tiers of fidelity, not a universal taxonomy. Critical services may require higher-fidelity error/latency evidence; lower-criticality components may need a lighter baseline. Temporary debug verbosity or sampling escalation should be feature-flagged, time-bounded, monitored, and automatically reverted only if the reversion path itself is tested. Avoid cost-reduction changes during an incident or immediately before a launch.

**Before/after changes must prove that incident lines, error traces, alerts, dashboards, and SLO calculations remain usable.**

## 6. L4 — Production operating model and incident response

### 6.1 Observability FinOps program (technical scope only)

Use showback in measured units grouped by service/team/environment. Review monthly or at another explicitly owned cadence: top-N contributors per unit, unexpected growth, remediation status, budget exceptions, and owner. Keep budgets version-controlled and based on measured baselines. Do not introduce vendor pricing or financial chargeback here.

Create anomaly alerts for unexpected series, log-byte, span-rate, or query-load growth relative to a baseline. Use a stable comparison window and account for deployments, traffic changes, replay, and scheduled batch jobs.

### 6.2 Cardinality incident runbook

1. **Detect:** confirm growth in a bounded window and distinguish real series growth from a query/measurement artifact.
2. **Attribute:** identify metric, label, job, exporter, service, and recent deploy.
3. **Estimate impact:** inspect head-series trend, process memory, disk, scrape failures, and essential SLO telemetry.
4. **Mitigate:** apply a reviewed, narrow relabel rule or source-level feature toggle. Use only a pre-approved emergency brake.
5. **Verify:** confirm Prometheus remains healthy and essential SLO/error/incident telemetry still works.
6. **Fix source:** normalize or remove the unbounded label.
7. **Prevent:** add catalog/CI guardrail and regression test.
8. **Review:** preserve timeline, before/after evidence, trade-offs, and follow-ups.

Do not treat restart or TSDB/head cleanup as a routine first action; it can worsen recovery or discard useful state. Never silently delete broad metric sets. Roll back a mitigation if essential SLO metrics disappear, scrape health worsens beyond the agreed stop condition, or the intended series growth does not improve.

### 6.3 Lifecycle and governance

Deprecate metrics, dashboards, and streams through owner notification, grace period, usage review, staged warning, and removal only after approval. Generate catalogs from code/exporters where feasible; enforce undocumented-metric checks. In multi-tenant/multi-cluster systems, attribute noisy tenants and duplicated scrapes/agents. Review debug logging, health-check trace noise, and duplicate pipelines.

Maintain incident evidence bundles: measurement window, query output, configuration diff, resource signals, critical logs/traces, alert state, and rollback result. Long-term aggregate storage in open formats is an architectural awareness topic, not a required installation.

### 6.4 Privacy, security, and deletion

Design for no PII by default in metric labels, log attributes, span attributes, and payloads. PII increases exposure, cardinality, and deletion complexity. Use allow-lists, redaction, access controls, least-privilege writers, and audited configuration changes. Protect textfile directories and Pushgateway endpoints against unauthorized writes/spoofing.

Deletion-on-request is an architectural requirement where applicable, but exact Prometheus/Loki/backend mechanisms are `[VERIFY]`. Confirm the deletion scope and verify the data is no longer queryable after the backend's documented processing interval. Consider indexes, replicas, object storage, backups, caches, and retention compaction. This section is not legal advice.

## 7. Mandatory practical labs

**Common safety contract:** run locally only, use synthetic fixtures, keep each workload bounded, set a stop condition, and clean up temporary files/containers after each lab. No public endpoints, paid services, real customer data, or host clock changes. Record all actual measurements as **laptop measurements—not production guarantees**. Where a backend is unavailable, use the included fixture patterns and mark backend integration `[VERIFY]`.

### Lab 1 — Deliberate cardinality explosion and safe mitigation

**Objective:** observe series growth from an intentionally unbounded label, then remove the source of growth while preserving critical telemetry.

**Prerequisites/resources:** Python 3; optional local Prometheus. Low resource use with fixtures; TSDB lab may use more memory. Use a controlled branch/profile and a synthetic request ID.

**Files (illustrative lab layout):** `app_metrics.py`, `prometheus.yml`, `baseline.txt`, `reduced.txt`.

**Steps:**

1. Establish a baseline for active series, process memory, scrape health, and essential SLO metrics.
2. In the lab-only app, add a `request_id` label to a synthetic counter for a bounded request batch (for example, 100 requests). Never use this design in a real service.
3. Observe the series count and compare with baseline. If Prometheus is present, inspect TSDB status and `promtool tsdb analyze` if supported `[VERIFY]`.
4. Apply a targeted source fix that removes `request_id` from the metric labels. A relabel-drop rule can be a temporary mitigation, but removing the label at source is preferred.
5. Re-measure the same workload and verify critical telemetry remains.

**Expected assertions:** the unbounded-label fixture creates more distinct label sets than the bounded version; the bounded version retains the request/error/SLO signals needed by the lab. Do not predict an exact resource reduction.

**Failure cases:** the target is down; the metric name differs; the query is too broad; an essential metric was dropped. Stop if host resource use rises unexpectedly.

**Cleanup/rollback:** restore the baseline source/config; stop local Prometheus; remove only lab-generated TSDB data after preserving evidence. Never apply the experiment to production endpoints.

**Acceptance:** evidence includes baseline/reduced counts, measurement window, resource evidence if available, config diff, and proof that essential telemetry remains.

### Lab 2 — Cardinality calculator with tests

**Objective:** calculate theoretical series from bounded label dimensions and histogram expansion.

Create `cardinality_calc.py`:

```python
#!/usr/bin/env python3
"""Estimate series from explicit label cardinalities; not a memory estimator."""
import argparse
import json
import sys
from math import prod

def estimate(definition):
    if not isinstance(definition, dict):
        raise ValueError("each metric definition must be an object")
    name = definition.get("name")
    labels = definition.get("labels", {})
    if not isinstance(name, str) or not name.strip():
        raise ValueError("metric name must be a non-empty string")
    if not isinstance(labels, dict):
        raise ValueError(f"{name}: labels must be an object")
    cardinalities = []
    for label, count in labels.items():
        if not isinstance(label, str) or not label:
            raise ValueError(f"{name}: label names must be non-empty strings")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError(f"{name}: cardinality for {label} must be an integer >= 1")
        cardinalities.append(count)
    combinations = prod(cardinalities) if cardinalities else 1
    metric_type = definition.get("type", "gauge")
    if metric_type == "histogram":
        buckets = definition.get("finite_buckets")
        if isinstance(buckets, bool) or not isinstance(buckets, int) or buckets < 0:
            raise ValueError(f"{name}: finite_buckets must be an integer >= 0")
        # Classic histogram: finite buckets +Inf, _count and _sum.
        series_per_combination = buckets + 3
    else:
        series_per_combination = 1
    extra = definition.get("extra_series", 0)
    if isinstance(extra, bool) or not isinstance(extra, int) or extra < 0:
        raise ValueError(f"{name}: extra_series must be an integer >= 0")
    return {
        "name": name,
        "label_combinations": combinations,
        "series_per_combination": series_per_combination,
        "estimated_series": combinations * series_per_combination + extra,
        "assumption": "all combinations occur; classic histogram exposition assumed",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON file containing a list of metric definitions")
    parser.add_argument("--observed", type=int, help="optional observed series count for comparison")
    args = parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as f:
            definitions = json.load(f)
        if not isinstance(definitions, list):
            raise ValueError("input JSON must be a list")
        results = [estimate(d) for d in definitions]
        report = {"metrics": results, "total_estimated_series": sum(r["estimated_series"] for r in results)}
        if args.observed is not None:
            if args.observed < 0:
                raise ValueError("--observed must be >= 0")
            report["observed_series"] = args.observed
            report["difference_estimated_minus_observed"] = report["total_estimated_series"] - args.observed
        print(json.dumps(report, indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Example `metrics.json`:

```json
[
  {"name":"requests_total","type":"counter","labels":{"service":5,"route":20,"status_class":5}},
  {"name":"request_duration_seconds","type":"histogram","finite_buckets":12,"labels":{"service":5,"route":20}}
]
```

Run: `python3 cardinality_calc.py metrics.json --observed 2500`. Expected output is JSON with an estimated series total and an observed difference; actual output depends on the input. This is an upper-bound estimator, not a memory predictor. It assumes every label combination occurs; histogram schema and additional series may differ.

Tests (save as `test_cardinality_calc.py`):

```python
import unittest
from cardinality_calc import estimate

class CardinalityTests(unittest.TestCase):
    def test_no_labels(self):
        self.assertEqual(estimate({"name":"x"})["estimated_series"], 1)
    def test_product(self):
        self.assertEqual(estimate({"name":"x","labels":{"a":2,"b":3}})["estimated_series"], 6)
    def test_histogram(self):
        self.assertEqual(estimate({"name":"h","type":"histogram","finite_buckets":2})["estimated_series"], 5)
    def test_bad_cardinality(self):
        with self.assertRaises(ValueError):
            estimate({"name":"x","labels":{"request_id":0}})
    def test_extra_series(self):
        self.assertEqual(estimate({"name":"x","extra_series":4})["estimated_series"], 5)

if __name__ == "__main__":
    unittest.main()
```

Run `python3 -m unittest -v test_cardinality_calc.py`. **Expected behavior:** all five tests pass; this is expected behavior, not a claim that they were executed in the target repository.

**Cleanup/rollback:** remove temporary files after retaining the report. **Acceptance:** input validation, histogram multiplication, explicit assumptions, and observed-vs-estimated comparison work.

### Lab 3 — Cost-driver report generator with tests

**Objective:** report metrics, logs, and traces in their own units; do not combine incomparable units.

Create `cost_report.py` to consume a JSON measurement envelope:

```python
#!/usr/bin/env python3
"""Render measured-unit telemetry rows; missing measurements remain missing."""
import argparse, json, sys

REQUIRED = {"measurement", "unit", "window_start", "window_end", "source", "status"}

def validate_row(row):
    if not isinstance(row, dict):
        raise ValueError("each row must be an object")
    missing = REQUIRED - row.keys()
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    if row["status"] not in {"measured", "missing", "unsupported", "invalid"}:
        raise ValueError("status must be measured/missing/unsupported/invalid")
    if row["status"] == "measured":
        if not isinstance(row.get("value"), (int, float)) or isinstance(row.get("value"), bool):
            raise ValueError("measured rows require numeric value")
        if row["value"] < 0:
            raise ValueError("measurement cannot be negative")
    return row

def summarize(rows):
    checked = [validate_row(r) for r in rows]
    groups = {}
    for row in checked:
        key = (row["measurement"], row["unit"])
        groups.setdefault(key, []).append(row)
    output = []
    for (measurement, unit), group in sorted(groups.items()):
        measured = [r for r in group if r["status"] == "measured"]
        output.append({
            "measurement": measurement, "unit": unit,
            "measured_rows": len(measured),
            "missing_or_unavailable_rows": len(group) - len(measured),
            "top": sorted(measured, key=lambda r: r["value"], reverse=True)[:5],
            "note": "ranking is within this measurement and unit only",
        })
    return output

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    args = p.parse_args()
    try:
        with open(args.input, encoding="utf-8") as f:
            rows = json.load(f)
        print(json.dumps(summarize(rows), indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Fixture rows should include series by job/namespace/metric, log bytes by app/level, and spans by service. Add `window_start`, `window_end`, `source`, `status`, and `caveat`. A missing log backend should produce `status: "unsupported"` rather than `value: 0`.

Tests should assert that unavailable data is not ranked as zero, negative values are rejected, and rankings are separate by unit. Expected output is a JSON summary grouped by measurement/unit. Use the actual Prometheus/API or local file measurements where available.

**Acceptance:** top-N rankings show evidence, units and time windows; no blended score; unavailable values remain explicit.

Tests for `cost_report.py` (save as `test_cost_report.py`):

```python
import unittest
from cost_report import summarize, validate_row

def row(measurement, unit, value=None, status="measured"):
    result = {
        "measurement": measurement, "unit": unit,
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-01T00:05:00Z",
        "source": "synthetic-fixture", "status": status,
        "attribution_dimension": "service", "attribution_value": "api",
        "caveat": "synthetic",
    }
    if value is not None:
        result["value"] = value
    return result

class CostReportTests(unittest.TestCase):
    def test_missing_is_not_zero(self):
        report = summarize([row("log_bytes", "bytes", status="unsupported")])
        self.assertEqual(report[0]["measured_rows"], 0)
        self.assertEqual(report[0]["missing_or_unavailable_rows"], 1)
        self.assertEqual(report[0]["top"], [])
    def test_ranks_within_same_unit(self):
        report = summarize([row("log_bytes", "bytes", 10), row("log_bytes", "bytes", 20)])
        self.assertEqual(report[0]["top"][0]["value"], 20)
    def test_rejects_negative(self):
        with self.assertRaises(ValueError):
            validate_row(row("series", "series", -1))
    def test_distinct_units_are_not_combined(self):
        report = summarize([row("series", "series", 10), row("log_bytes", "bytes", 10)])
        self.assertEqual(len(report), 2)

if __name__ == "__main__":
    unittest.main()
```

Run `python3 -m unittest -v test_cost_report.py`. The test suite is expected to pass if the script and test file are saved as shown; no execution claim is made here.

### Lab 4 — Unused-telemetry detector with tests

**Objective:** find possible unreferenced metrics in Git-stored dashboards and rules without automatic deletion.

Create `unused_metrics.py`:

```python
#!/usr/bin/env python3
"""Conservative candidate detector; review results before deprecating anything."""
import argparse, json, re, sys
from pathlib import Path

def metric_tokens(text):
    # Approximate lexer for lab use, not a full PromQL/YAML parser.
    # Extract identifiers that look like metric names; false positives are expected.
    return set(re.findall(r"\b[a-zA-Z_:][a-zA-Z0-9_:]*\b", text))

def detect(exported_metrics, files):
    referenced = set()
    for path in files:
        try:
            referenced |= metric_tokens(Path(path).read_text(encoding="utf-8"))
        except OSError as exc:
            raise ValueError(f"cannot read {path}: {exc}") from exc
    return sorted(set(exported_metrics) - referenced)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metrics", required=True, help="JSON list of metric names")
    p.add_argument("files", nargs="+", help="dashboard/rule files to scan")
    a = p.parse_args()
    try:
        metrics = json.loads(Path(a.metrics).read_text(encoding="utf-8"))
        if not isinstance(metrics, list) or not all(isinstance(x, str) for x in metrics):
            raise ValueError("metrics file must be a JSON list of strings")
        print(json.dumps({"review_candidates": detect(metrics, a.files),
                          "action": "human review only; no deletion performed"}, indent=2))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Tests: referenced metric is not flagged; unreferenced metric is flagged; missing file fails clearly. A real parser should understand the query/config formats; this lab's regex is intentionally approximate. Ad-hoc queries, external consumers, automation, and runbooks are invisible to the detector.

**Acceptance:** the tool outputs candidates only, states its limitations, and never deletes/disables metrics.

Tests for `unused_metrics.py` (save as `test_unused_metrics.py`):

```python
import tempfile
import unittest
from pathlib import Path
from unused_metrics import detect

class UnusedMetricTests(unittest.TestCase):
    def test_referenced_metric_not_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td, "dashboard.promql")
            p.write_text("sum(rate(api_requests_total[5m]))", encoding="utf-8")
            self.assertNotIn("api_requests_total", detect(["api_requests_total", "unused_metric"], [p]))
    def test_unreferenced_metric_is_candidate_only(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td, "rules.yaml")
            p.write_text("expr: up", encoding="utf-8")
            self.assertEqual(detect(["unused_metric"], [p]), ["unused_metric"])
    def test_missing_file_fails(self):
        with self.assertRaises(ValueError):
            detect(["x"], ["/no/such/lab-file"])

if __name__ == "__main__":
    unittest.main()
```

Run `python3 -m unittest -v test_unused_metrics.py`. This detector intentionally uses an approximate token scanner. Treat results as review candidates, not proof of non-use.

### Lab 5 — Log-volume reduction with incident evidence preserved

**Objective:** reduce repetitive synthetic log volume without losing rare incident evidence.

Create a JSONL fixture with routine health checks, repeated warning lines, a critical error, and a synthetic stack context. Do not include PII or secrets. Use a deterministic filter that:

1. drops only explicitly allow-listed routine health-check events;
2. deduplicates exact repeated low-severity lines within a defined fixture window;
3. retains the first sample and a count for repetitive errors;
4. preserves every critical/error line and required structured fields;
5. runs redaction checks against forbidden field names (`token`, `password`, `email`, raw payload).

Measure bytes with `wc -c` before and after. Test that the critical line and stack context remain, the output is smaller for the chosen fixture, and no forbidden sensitive field/value is present. If output is not smaller, report the result rather than forcing a reduction.

**Cleanup:** delete generated fixture/output after saving the diff and measurements. **Rollback:** remove the filter and restore baseline fixture. **Acceptance:** bytes are measured; critical evidence is preserved; reduction is deterministic and testable.

### Lab 6 — Trace-volume reduction with error-trace preservation

**Objective:** apply a fixture-based sampling/attribute policy and test retention.

Use a sanitized JSON fixture with trace IDs, service, duration, status, and span count. Select a policy that preserves fixture traces marked error or above a documented slow threshold, while sampling a bounded fraction of normal traces. Remove high-cardinality attributes only after recording that trace/log correlation remains possible. Filter health-check spans only if they are not needed for the lab's health SLO.

Test:
- error fixture trace remains;
- slow fixture trace remains;
- normal traces follow the declared deterministic policy;
- sensitive attributes are removed;
- output span count/bytes are measured before/after.

Do not claim general tail-sampling guarantees from a fixture. A real Collector policy has queue, memory, ordering, and configuration constraints `[VERIFY]`.

**Acceptance:** error and slow retention is demonstrated for the actual fixture, with policy limitations documented.

### Lab 7 — Retention decision records and deletion verification

Create three records—metrics, logs, traces—using the template in §4.5. For each, document question, owner, retention time/resolution, sensitivity, incident window, deletion method, evidence, approval, review date, and rollback. Run deletion verification only if the chosen local backend supports a documented procedure `[VERIFY]`; otherwise test a fixture lifecycle and include a verification checklist.

Evidence must distinguish “deletion requested,” “backend accepted request,” and “data is no longer queryable/retained.” Do not claim deletion occurred without evidence. **Acceptance:** three records exist and each has an owner and verification method.

### Lab 8 — Recording-rule pre-aggregation

Use a local Prometheus only if available. Save a baseline query result, add the example recording rule from §5.4, validate rules using `promtool check rules <RULE_FILE>` `[VERIFY]`, and compare aggregate output with the raw query over the same window. Record the raw detail lost (for example, pod-level spikes) and the question still answerable (service/route rate). Retain raw data for a bounded drill-down period.

**Acceptance:** query equivalence is tested for the intended aggregation, rule errors are visible, and limitations are documented. If Prometheus is unavailable, compute the same aggregate over a fixture.

### Lab 9 — Budget/guardrail implementation with fail-loud tests

Choose one available limit: Prometheus scrape/sample limits, Loki tenant limit, or Collector processor/queue limit. Validate configuration against the installed version `[VERIFY]`. Define owner, threshold unit, alert, expected behavior, and rollback before enabling it. Create an intentional breach in the isolated lab and confirm an actionable failure signal (for example, scrape/target failure or explicit refused/dropped telemetry signal as appropriate to the component).

Do not use a limit that silently erases critical telemetry without alerting. Test essential SLO/error metrics during the breach. Roll back if the limit breaks required signals. **Acceptance:** breach is visible, owner/runbook are attached, and critical telemetry behavior is known.

### Lab 10 — Telemetry unit-economics model

Use the ratios in §5.5 and a local measurement file. Build scenarios for baseline, traffic +25%, instances +50%, label cardinality ×2, and retention +7 days `[ILLUSTRATIVE]`. Keep each scenario in compatible units. Tests should catch negative input, zero request count, inconsistent units, and arithmetic errors. Produce sensitivity results for each input independently.

**Acceptance:** report labels synthetic versus measured data, includes units, has tests, and makes no price claims.

A minimal unit-economics calculator for Lab 10 can be saved as `telemetry_forecast.py`:

```python
#!/usr/bin/env python3
"""Forecast log bytes from measured bytes/request and request volume."""
import argparse, json, sys

def forecast(bytes_per_request, requests_per_day, traffic_growth=0.0, retention_days=1):
    values = (bytes_per_request, requests_per_day, traffic_growth, retention_days)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in values):
        raise ValueError("all inputs must be numeric")
    if bytes_per_request < 0 or requests_per_day < 0 or traffic_growth < -1 or retention_days < 0:
        raise ValueError("bytes/requests/retention must be >= 0 and traffic_growth >= -1")
    projected_requests = requests_per_day * (1 + traffic_growth)
    daily_bytes = bytes_per_request * projected_requests
    return {
        "projected_requests_per_day": projected_requests,
        "projected_bytes_per_day": daily_bytes,
        "projected_bytes_over_retention": daily_bytes * retention_days,
        "unit": "bytes",
        "assumption": "bytes/request and traffic-growth factor remain stable",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bytes-per-request", type=float, required=True)
    p.add_argument("--requests-per-day", type=float, required=True)
    p.add_argument("--traffic-growth", type=float, default=0.0, help="fraction, e.g. 0.25 for +25%")
    p.add_argument("--retention-days", type=float, default=1)
    a = p.parse_args()
    try:
        print(json.dumps(forecast(a.bytes_per_request, a.requests_per_day,
                                  a.traffic_growth, a.retention_days), indent=2))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Tests (save as `test_telemetry_forecast.py`):

```python
import unittest
from telemetry_forecast import forecast

class ForecastTests(unittest.TestCase):
    def test_units_and_growth(self):
        result = forecast(180, 80000, 0.5, 7)
        self.assertEqual(result["projected_bytes_per_day"], 21600000)
        self.assertEqual(result["projected_bytes_over_retention"], 151200000)
    def test_zero_traffic(self):
        self.assertEqual(forecast(180, 0)["projected_bytes_per_day"], 0)
    def test_reject_negative_growth_below_minus_one(self):
        with self.assertRaises(ValueError):
            forecast(1, 10, -1.1)
    def test_reject_negative_bytes(self):
        with self.assertRaises(ValueError):
            forecast(-1, 10)

if __name__ == "__main__":
    unittest.main()
```

Run `python3 -m unittest -v test_telemetry_forecast.py`. Model instance growth and label-cardinality changes as separate sensitivity scenarios; do not multiply instance count into a total-traffic estimate unless measurements show it changes bytes/request or duplicated emission.

### Lab 11 — Cardinality incident game day

Reuse Lab 1's controlled failure. Before starting, test the emergency brake in a fixture or disposable local profile. During the game day record timestamps for detection, attribution, mitigation, source fix, and verification; calculate time-to-detect from injection to alert observation. Do not invent values—fill the result table only after running.

| Field | Result |
|---|---|
| Injection timestamp | `[TO MEASURE]` |
| Alert observed | `[TO MEASURE]` |
| Time-to-detect | `[TO MEASURE]` |
| Series/resource before/after | `[TO MEASURE]` |
| Essential telemetry preserved? | `[TO MEASURE]` |
| Rollback tested? | `[TO MEASURE]` |

Write a blameless review with contributing factors, detection gap, source fix, guardrail, and owner/date. **Acceptance:** emergency brake is tested, essential signals remain, and no production system is touched.

### Lab 12 — Metric catalog and CI lint

Create a catalog with a valid bounded metric and an invalid `request_id`-labelled metric. The linter should fail on undocumented metrics, dangerous label names, missing owner/purpose, invalid cardinality estimates, and missing retention/deprecation fields. Use the schema in §5.2 and tests for valid/invalid fixtures.

`[ASSUMPTION]` CI integration is a local script invoked from the repository's existing CI; no workflow file should be edited as part of this lesson. Onboarding requires a metric definition, owner, consumer, label bounds, series estimate, sensitivity review, retention tier, and deprecation policy.

**Acceptance:** valid fixture passes; invalid fixture fails with actionable errors; the linter never modifies telemetry or configuration.

A minimal metric-catalog linter for Lab 12 can be saved as `catalog_lint.py`. It validates a deliberately small JSON catalog; adapt the schema to the actual repository and CI `[ASSUMPTION]`.

```python
#!/usr/bin/env python3
"""Fail-loud catalog checks; this tool does not modify metrics or config."""
import argparse, json, re, sys
from pathlib import Path

DANGEROUS = re.compile(r"(request.?id|user.?id|session.?id|timestamp|raw.?url|email)", re.I)
REQUIRED = {"name", "type", "unit", "purpose", "owner", "labels",
            "estimated_series_budget", "consumers", "sensitivity",
            "retention_tier", "deprecation"}

def lint(entries):
    errors, seen = [], set()
    if not isinstance(entries, list):
        return ["catalog must be a list"]
    for index, item in enumerate(entries):
        prefix = f"entry[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        missing = REQUIRED - item.keys()
        if missing:
            errors.append(f"{prefix}: missing fields {sorted(missing)}")
            continue
        name = item["name"]
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{prefix}: name must be non-empty")
        elif name in seen:
            errors.append(f"{prefix}: duplicate metric name {name}")
        else:
            seen.add(name)
        if not isinstance(item["owner"], str) or not item["owner"].strip():
            errors.append(f"{prefix}: owner required")
        if not isinstance(item["purpose"], str) or not item["purpose"].strip():
            errors.append(f"{prefix}: purpose required")
        budget = item["estimated_series_budget"]
        if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
            errors.append(f"{prefix}: estimated_series_budget must be integer >= 1")
        if not isinstance(item["labels"], dict):
            errors.append(f"{prefix}: labels must map names to metadata")
        else:
            for label, metadata in item["labels"].items():
                if DANGEROUS.search(label):
                    errors.append(f"{prefix}: dangerous/unbounded label {label}")
                if not isinstance(metadata, dict) or metadata.get("bounded") is not True:
                    errors.append(f"{prefix}: label {label} must declare bounded: true")
                if isinstance(metadata, dict):
                    count = metadata.get("max_values")
                    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                        errors.append(f"{prefix}: label {label} max_values must be integer >= 1")
        if not isinstance(item["consumers"], list):
            errors.append(f"{prefix}: consumers must be a list")
    return errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument("catalog")
    a = p.parse_args()
    try:
        entries = json.loads(Path(a.catalog).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    errors = lint(entries)
    if errors:
        print("\\n".join(errors), file=sys.stderr)
        return 1
    print(f"catalog OK: {len(entries)} entries")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Tests (save as `test_catalog_lint.py`):

```python
import unittest
from catalog_lint import lint

VALID = {
    "name": "api_requests_total", "type": "counter", "unit": "requests",
    "purpose": "Request count", "owner": "team-api",
    "labels": {"route": {"bounded": True, "max_values": 20}},
    "estimated_series_budget": 100, "consumers": ["request-dashboard"],
    "sensitivity": "no_pii", "retention_tier": "raw-short", "deprecation": "active"
}

class CatalogLintTests(unittest.TestCase):
    def test_valid_entry(self):
        self.assertEqual(lint([VALID]), [])
    def test_unbounded_identifier_label(self):
        item = dict(VALID, labels={"request_id": {"bounded": True, "max_values": 100000}})
        self.assertTrue(any("dangerous" in e for e in lint([item])))
    def test_missing_owner(self):
        item = dict(VALID)
        item.pop("owner")
        self.assertTrue(any("missing fields" in e for e in lint([item])))
    def test_duplicate_metric(self):
        self.assertTrue(any("duplicate" in e for e in lint([VALID, VALID])))

if __name__ == "__main__":
    unittest.main()
```

Run `python3 -m unittest -v test_catalog_lint.py`. The linter is a small lab guardrail, not a full PromQL or exporter instrumentation parser; keep reviewed exceptions explicit and do not automatically remove metrics.

## 8. Additional required artifacts and operational exercises

Maintain these outputs as local lab artifacts:

- cardinality calculator and test output;
- top-series/job/service report;
- cost-driver report in measured units;
- unused-telemetry candidates report;
- before/after reduction experiment;
- retention decision records;
- metric catalog and CI lint report;
- guardrail config plus intentional breach evidence;
- growth-anomaly detection rule or fixture test;
- incident runbook and emergency-brake test;
- unit-economics forecast and sensitivity table;
- results table below.

### Before/after results table

| Measure | Baseline | Reduced | Window/source | Required evidence preserved? | Rollback condition |
|---|---:|---:|---|---|---|
| Active series | `[TO MEASURE]` | `[TO MEASURE]` | `[TO RECORD]` | SLO metrics queried | Essential series missing |
| Samples/s | `[TO MEASURE]` | `[TO MEASURE]` | `[TO RECORD]` | Alert evaluates | Scrape/alert failure |
| Log bytes/day | `[TO MEASURE]` | `[TO MEASURE]` | `[TO RECORD]` | Incident lines remain | Critical line missing |
| Span count/bytes | `[TO MEASURE]` | `[TO MEASURE]` | `[TO RECORD]` | Error/slow traces remain | Required trace disappears |
| Query behavior | `[TO MEASURE]` | `[TO MEASURE]` | `[TO RECORD]` | Dashboard and alert usable | Query/alert incorrect |
| Resource use | `[TO MEASURE]` | `[TO MEASURE]` | `[TO RECORD]` | Backend healthy | Resource pressure worsens |
| SLO compatibility | `[TO MEASURE]` | `[TO MEASURE]` | `[TO RECORD]` | SLO calculation unchanged | SLI becomes invalid |

Every experiment must state baseline method/window, exact change, expected reduction and mechanism, actual learner result fields, preservation tests, rollback condition, and restoration procedure. Laptop measurements do not predict production behavior.

## 9. Required worked incident analyses

All incidents below are `[SYNTHETIC]` teaching cases, not claims about the learner's environment.

### 9.1 Raw URL/ID label drives series growth and OOM risk

- **Symptom:** active series grows sharply after a deployment; memory and scrape/query pressure rise.
- **Evidence:** compare series by metric/job, inspect the new `endpoint` label values, deployment diff, process memory, and essential metric availability.
- **Hypothesis:** raw URLs and IDs create near-unique label sets.
- **Controlled reproduction:** replay a bounded synthetic request set with route-template labels versus raw URL labels.
- **Mitigation:** apply reviewed targeted drop only if necessary; fix instrumentation to use route templates.
- **Guardrail:** catalog/CI ban on raw URL and unbounded identifier labels.
- **Verification:** repeat identical fixture; compare series and ensure SLO/error metrics remain.
- **Lesson:** source normalization beats a permanent broad drop.

### 9.2 Histogram bucket expansion multiplies series

- **Symptom:** a histogram change causes an unexpected series increase. A 10× increase is an illustrative possible pattern, not a universal outcome.
- **Evidence:** compare bucket count, label dimensions, generated series, and deployment version.
- **Hypothesis:** more buckets multiplied by many label combinations.
- **Experiment/fix:** calculate expected series before rollout; use buckets tied to SLO thresholds and remove unnecessary dimensions.
- **Prevention:** catalog bucket count, estimate, and CI budget.
- **Verification:** compare observed series to the estimate; explain residual differences.

### 9.3 Debug logs fill disk and evict useful retention

- **Symptom:** log bytes/day rises while request rate remains stable; older incident context becomes unavailable.
- **Evidence:** bytes by app/level, debug config diff, duplicate shipper checks, disk/retention state.
- **Fix:** time-bound debug mode, lower routine verbosity, preserve error context, test a synthetic incident replay.
- **Guardrail:** debug-mode expiry and volume-growth alert.
- **Verification:** critical lines remain and measured bytes fall.

### 9.4 Cost reduction removes an SLO metric

- **Symptom:** an SLO alert no longer evaluates or produces no data after a relabel/filter change.
- **Evidence:** alert query, recording rules, metric catalog consumers, scrape/target health.
- **Fix:** restore required series and add a compatibility test before reapplying a narrower reduction.
- **Prevention:** consumer inventory and staged deprecation.
- **Verification:** known fixture causes the SLO/alert to evaluate as expected.

### 9.5 Duplicate Collectors double log volume

- **Symptom:** near-identical log lines and doubled bytes appear without traffic growth.
- **Evidence:** source path, agent/Collector deployment count, timestamps and labels.
- **Experiment:** disable one duplicate pipeline in a disposable environment and compare exact fixture counts.
- **Fix:** one authoritative shipping path per source; add duplicate-pipeline inventory.
- **Verification:** expected line count and incident evidence remain.

### 9.6 Retention shortened; five-week-old regression cannot be investigated

- **Symptom:** a regression predating current retention is not queryable.
- **Evidence:** retention config, last available data, aggregate coverage, incident timeline.
- **Fix:** preserve required long-term aggregates and incident evidence according to an owner-approved policy.
- **Prevention:** retention decision record and deletion verification.
- **Verification:** test a synthetic data lifecycle; document what raw detail is intentionally unavailable.

### 9.7 Dashboard refresh overloads query backend

- **Symptom:** query latency/resource use rises with many viewers and frequent refresh.
- **Evidence:** panel refresh interval, concurrent viewers, query range/selector, query duration/queue.
- **Experiment:** increase refresh interval and compare query load under same viewing pattern.
- **Fix:** recording rules/cache/tighter selectors and sensible refresh cadence.
- **Verification:** panel remains useful and alert evaluation stays timely.

### 9.8 Hashing is mistaken for cardinality control

- **Symptom:** `user_hash` still has huge distinct-value count.
- **Evidence:** count distinct values in the fixture and compare series estimates.
- **Fix:** remove identifier from metric labels; use logs/traces with access controls or aggregate to bounded segments.
- **Prevention:** lint for identifier-derived labels, including hash suffixes.

### 9.9 High-churn pod names inflate long-term series

- **Symptom:** series count grows across deployments/autoscaling while steady workload is similar.
- **Evidence:** series by instance/pod, churn rate, retention and recording-rule dimensions.
- **Fix:** preserve per-pod metrics for short-term debugging where needed, but aggregate long-term views by stable service/namespace.
- **Verification:** maintain required incident drill-down for the approved window.

### 9.10 Retention policy exists but deletion is unverified

- **Symptom:** a policy claims data should be gone, but queries still return it.
- **Evidence:** backend/version, deletion API/job status, object/index lifecycle, query results.
- **Fix:** follow official backend procedure `[VERIFY]`; confirm actual queryability and storage lifecycle.
- **Prevention:** deletion verification evidence and scheduled audit.
- **Caution:** a policy document is not proof of deletion.

### 9.11 Top-metrics query itself adds work

- **Symptom:** cardinality investigation query is slow or resource-intensive.
- **Evidence:** query duration, range, selector breadth, backend load.
- **Fix:** use TSDB status/analyzer or smaller windows, and avoid repeated broad queries during stress.
- **Prevention:** investigation playbook with safe query order and stop condition.

### 9.12 Sampling loses error evidence

- **Symptom:** incident reports an error but no matching trace is retained.
- **Evidence:** SDK head sampling, Collector tail-sampling policy, dropped-span telemetry, trace IDs in logs.
- **Fix:** test the end-to-end sampling path; preserve error/slow traces according to a verified policy.
- **Prevention:** synthetic error-trace regression test and a clear statement of sampling guarantee.

## 10. Troubleshooting and decision tables

### 10.1 Troubleshooting matrix

| Symptom | Likely causes | First evidence/check | Safe first action | Deeper fix / verification |
|---|---|---|---|---|
| Active series grows rapidly | New label dimension, churn, histogram expansion | Top series by metric/job; deploy diff | Bound the query window | Normalize labels; compare series before/after |
| Head pressure rises | Series growth, churn, ingestion | Head series, memory, scrape errors | Stop new lab traffic | Fix source; verify essential metrics |
| Pod-name churn | Autoscaling/deployments | Series by pod/instance over time | Compare stable aggregate | Short-term instance detail, long-term aggregation |
| One metric dominates | Label explosion/buckets | Metric-name series count | Inspect label dimensions | Catalog budget and CI lint |
| Logs grow while traffic flat | Debug mode, duplicates, noisy loop | Bytes by app/level and shipper inventory | Pause bounded lab replay | Fix level/pipeline; preserve incident lines |
| Duplicate logs | Duplicate agent/Collector | Matching line/timestamp/source | Identify duplicate path | Remove duplicate route and test counts |
| Span volume changes | Sampling, instrumentation, duplicate pipeline | Spans by service and policy diff | Compare fixture counts | Test error/slow retention |
| Errors vanish from traces | Sampling or exporter loss | Logs, trace IDs, dropped telemetry | Preserve evidence; avoid broad reduction | Verify complete sampling/export path |
| Queries slow after dashboards | Refresh × viewers × broad selectors | Query duration and refresh settings | Lengthen refresh | Recording rules, narrower queries, cache |
| Retention not removing data | Policy not applied, async deletion, wrong scope | Config and queryability | Avoid repeated destructive requests | Follow official procedure and verify |
| Guardrail causes target failure | Limit exceeded | Target health and failure reason | Alert owner, roll back if critical | Adjust source/limit and add test |
| Report has missing/zero values | Unsupported signal mistaken for zero | Status/source/window fields | Mark unavailable | Add adapter or fixture fallback |
| CI flags legitimate metric | Parser approximation or reviewed exception | Lint finding and consumer catalog | Human review | Improve parser/allowlist with rationale |
| Aggregation loses drill-down | Dropped labels/resolution | Compare raw and aggregate queries | Restore raw short window if available | Document aggregation's question boundary |
| SLO invalid after reduction | Required metric dropped/renamed | SLO rule and metric catalog | Restore metric | Consumer tests and staged deprecation |

### 10.2 Drop vs normalize vs aggregate vs retain

| Choice | Use when | Main risk | Required evidence |
|---|---|---|---|
| Drop | Signal is demonstrably noise or unsafe and has no required consumer | Blind spot | Owner review, consumer check, preserved critical signals |
| Normalize | Dimension is useful but unbounded | Incorrect mapping can merge distinct operations | Route/enum tests and before/after series |
| Aggregate | Long-term question does not require raw dimensions | Lost drill-down | Raw-vs-aggregate query comparison |
| Retain | Signal supports SLO/security/incident diagnosis | Volume/retention burden | Measured budget and review date |

### 10.3 Raw vs aggregate vs long-term data

| Tier | Answers well | Cannot answer well |
|---|---|---|
| Raw high-resolution short-term | Per-instance spikes, detailed incident window | Long history without high volume |
| Recording-rule aggregate | Stable trends and SLO dimensions | Labels removed by aggregation |
| Backend downsampled/long-term | Long-term trend if supported | Fine-grained raw reconstruction |

### 10.4 Metric label vs log field vs span attribute vs exemplar

| Location | Best for | Avoid |
|---|---|---|
| Metric label | Bounded grouping and alerting | IDs, raw paths, free-form text |
| Log field | Event-specific context with access controls | Secrets/PII; unbounded indexed labels |
| Span attribute | Per-operation diagnostic context | Huge payloads and sensitive values |
| Exemplar | Link metric observation to trace if supported | Assuming universal support or storing IDs as labels |

### 10.5 Time-based vs size-based retention

| Policy | Strength | Failure mode |
|---|---|---|
| Time-based | Predictable investigation window | Disk can fill during volume spike |
| Size-based | Protects disk bound | Data may expire sooner than expected |
| Tiered raw + aggregate | Balances detail and trend | Aggregates cannot restore raw detail |
| Hybrid | Combines explicit time and storage bounds | Needs monitoring and deletion verification |

### 10.6 Automatic guardrail vs human-approved mitigation

| Control | Appropriate use | Safety requirement |
|---|---|---|
| Automatic hard limit | Prevent runaway ingestion when failure behavior is understood | Visible alert, owner, tested failure, no silent loss |
| Automatic normalization | Stable route/status normalization with tests | Versioned mapping and regression suite |
| Human-approved targeted drop | Emergency mitigation with known affected signal | Explicit scope, stop condition, rollback |
| Broad deletion/disable | Generally unsafe as first response | Do not do silently; require formal review and evidence |

## 11. Reference implementations and code quality requirements

This section consolidates requirements for the scripts above.

### 11.1 Safe emergency brake

Use a feature flag in the local fixture to stop only the intentionally dangerous metric emission. Do not use a blanket “disable all metrics” switch.

```python
def emit_request_metric(metrics, route, status_class, emergency_brake=False):
    if emergency_brake:
        # Preserve essential bounded operational metrics elsewhere.
        return
    metrics["request_total"].labels(route=route, status_class=status_class).inc()
```

This is a conceptual adapter, not a specific Prometheus client API. Test two assertions: with the brake enabled, the dangerous/high-cardinality metric stops growing; the independent health/error/SLO metrics remain available. Verify the brake before a game day and define the rollback condition.

### 11.2 Growth anomaly detection

Use a relative baseline and absolute guardrail rather than a universal threshold. Example conceptual condition:

- current active series is above a team-approved upper bound; **and/or**
- growth over a fixed window is materially above its baseline;
- alert annotation names owner, affected job/service, measured window, runbook, and whether the signal itself is missing.

PromQL and metric names for the actual rule are `[VERIFY]`. Avoid using a single noisy sample or deployment event as proof of a cardinality incident.

### 11.3 Report quality checks

Every report must include:
- measurement time/window and source;
- unit and attribution dimension;
- status for missing/unsupported/invalid data;
- caveats and query cost where relevant;
- top-N ranking only within comparable units;
- preservation evidence for critical telemetry.

### 11.4 Configuration validation and rollback

Before applying a configuration:
1. record current config and version;
2. validate syntax with the installed tool (`promtool check config`, `promtool check rules`, or component-specific validator `[VERIFY]`);
3. test a known-good fixture and an intentional breach;
4. stage in the local profile;
5. compare resource and telemetry outputs;
6. keep a tested rollback copy;
7. verify alerts, dashboards, SLO calculations, error traces, and incident logs.

Do not present a configuration field as supported until the installed version's official documentation and validation command confirm it.

## 12. Practice questions and answer key

Exactly five end-of-unit questions follow. Lab questions elsewhere are separate exercises.

### Questions

1. A histogram has 10 finite bucket boundaries and label dimensions with cardinalities 4 services, 25 routes, and 5 status classes. Assuming every combination exists and classic histogram exposition, estimate histogram-related series before any other metrics. State the assumptions and why the number is an upper bound.
2. Your report says metrics grew 20%, log bytes doubled, and spans fell 30%. Why is it invalid to combine these into one “cost score” without an explicit model? What additional attribution/window evidence would you collect?
3. A metric label contains raw request IDs. Compare drop, normalize, aggregate, and retain options. Which is the preferred source-level change, and what evidence must be preserved before rollout?
4. A retention policy says logs are retained for a defined number of days, but older records remain queryable. What evidence and checks distinguish a configuration mistake, asynchronous deletion, wrong query scope, and backend retention behavior? Why is a policy document not enough?
5. A service's request rate is forecast to increase by 50%, instances by 25%, and average log bytes/request is measured at 180 bytes. Explain a unit-consistent first-order daily log-volume estimate if the current request count is 80,000/day, and list two reasons the forecast may be wrong. Do not assign prices.

### Answer key

1. Label combinations: \(4 \times 25 \times 5 = 500\). A classic histogram with 10 finite buckets has 11 bucket series including `+Inf`, plus `_count` and `_sum`, giving 13 series per label combination. \(500 \times 13 = 6{,}500\) series. Assumes all combinations occur, 10 finite boundaries are exposed as stated, and no extra implementation-specific series; actual exposition must be checked `[VERIFY]`.
2. Series, bytes, and spans are different units with different operational meaning; adding percentage changes does not create a dimensionally meaningful score. Collect matching time windows, source/measurement method, service/team attribution, traffic, sampling policy, retention, and query behavior. Rank top contributors separately by unit.
3. Normalize/remove request IDs at source; request-specific identifiers belong in logs/traces with appropriate controls. Drop is a possible narrow emergency mitigation but may remove useful telemetry; aggregation is appropriate only if the question can be answered without the ID; retain as a metric label is generally unsafe. Preserve baseline counts, SLO/error signals, trace/log correlation, config diff, and rollback plan.
4. Inspect backend/version, configured retention, effective runtime config, deletion job/API response, query time range and labels, index/chunk/object lifecycle, and whether replicas/backups/caches are in scope. Use official documentation `[VERIFY]`, then prove the data is no longer queryable after the documented processing interval. A policy states intent, not execution.
5. Current bytes/day = \(80{,}000 \text{ requests/day} \times 180 \text{ bytes/request} = 14{,}400{,}000\) bytes/day. If request count rises 50%, first-order future volume is \(120{,}000 \times 180 = 21{,}600{,}000\) bytes/day. The 25% instance growth is not automatically multiplied again if request count already captures total traffic; it may change logging duplication or per-instance behavior, so model it only if measurements justify it. Forecast may be wrong due to changing log volume/request, debug settings, duplicate shippers, compression/format, traffic mix, or retries.

## 13. Source/version discipline and evidence ledger

Use official documentation and installed version/help output. Do not claim documentation was checked unless you actually check it.

| Area | What to verify | Method |
|---|---|---|
| Prometheus metric names/TSDB status | Exact self-metrics and status UI/API | Inspect `/metrics`, installed UI/docs `[VERIFY]` |
| `promtool tsdb analyze` | Availability and input format | `promtool --version`; `promtool tsdb --help` `[VERIFY]` |
| PromQL broad selectors | Syntax, query cost, time range | Test a bounded query and observe duration/resource use |
| `sample_limit`, label limits, relabeling | Supported fields and failure semantics | Installed version docs and `promtool check config` `[VERIFY]` |
| Loki labels, ingestion, retention, deletion | Exact metrics, tenant limits, APIs, deletion semantics | Installed version docs/config and controlled test `[VERIFY]` |
| OpenTelemetry Collector | Accepted/refused/dropped metrics, processors, tail sampling | Component docs and `/metrics` endpoint `[VERIFY]` |
| Native histograms and recording rules | Feature support and rule semantics | Prometheus version/docs and `promtool check rules` `[VERIFY]` |
| Thanos/Mimir/VictoriaMetrics | Downsampling, retention, deletion | Official docs for selected release `[VERIFY]` |
| Retention/deletion enforcement | Data lifecycle including replicas/object store | Controlled test and queryability check `[VERIFY]` |

Useful local commands, subject to installation and path:

```bash
prometheus --version
promtool --version
promtool check config <PROMETHEUS_CONFIG>
promtool check rules <RULE_FILE>
promtool tsdb --help
curl -fsS http://<METRICS_HOST>:<METRICS_PORT>/metrics | grep -E 'prometheus_tsdb_head_series|scrape_samples_scraped'
```

All commands and names above must be checked against the installed release `[VERIFY]`. A healthy exporter only proves that the exporter endpoint responds; it does not prove that a pipeline is healthy. Missing metric, missing job, failed scrape, and exporter failure are distinct conditions.

### Evidence categories

- **Syllabus-derived requirements:** the unit scope, handoff boundary, twelve labs, incident patterns, and required audit.
- **General technical facts:** cardinality is label-set combinations; histogram series multiply label combinations; measured units must remain dimensionally consistent.
- **Assumptions:** the local synthetic app, schema, and fixture layout.
- **Synthetic/illustrative values:** all example cardinalities, byte counts, traffic growth, and example metric catalog budgets.
- **Local verification required:** installed metric names, flags, config fields, UI/API capabilities, deletion behavior, sampling policy, and resource impact.

## 14. Final completeness and correctness audit

The following audit reflects the lesson content and this authoring pass. It is not a claim that the learner's backend was installed or tested. A `PASS` means the requested content is present in the lesson; `NOT RUN` means an environment-dependent execution check has not been performed.

| # | Audit requirement | Status | Evidence / limitation |
|---:|---|---|---|
| 1 | Exact filename, module, and unit | PASS | Title and target filename stated at top; Unit 12 scope |
| 2 | Verbatim Unit 12 handoff | PASS | Included verbatim near beginning |
| 3 | M15 boundary; no real prices | PASS | Technical units only; M15 financial scope excluded |
| 4 | L1 cost foundations | PASS | Metrics/logs/traces/query cost, cardinality, retention, visibility |
| 5 | L2 measurement and attribution | PASS | TSDB/query guidance, fixture measurement, report contract |
| 6 | L2 reduction levers | PASS | Metrics, logs, traces, pipeline/query, retention, guardrails |
| 7 | L3 systematic techniques | PASS | Value review, unused detector, catalog, aggregation, forecasting |
| 8 | L4 governance/incident response | PASS | Anomaly approach, runbook, lifecycle, privacy/deletion |
| 9 | All 12 mandatory labs | PASS | Labs 1–12 included with acceptance/cleanup guidance |
| 10 | Additional required artifacts | PASS | Calculator, reports, detector, records, catalog, model, results table |
| 11 | All 12 incident analyses | PASS | Sections 9.1–9.12 |
| 12 | Troubleshooting and decision tables | PASS | Section 10 |
| 13 | Exactly five practice questions and key | PASS | Five numbered questions, separate answer key |
| 14 | Code examples and execution claims | PASS | Five Python unit-test suites executed in a temporary directory: 20 tests passed; code-block syntax checked |
| 15 | Version-sensitive items marked | PASS | `[VERIFY]` notes and source/version table |
| 16 | Synthetic/illustrative values labelled | PASS | Labels used for examples and assumptions |
| 17 | Evidence preservation after reduction | PASS | Explicit preservation requirement and results table |
| 18 | Fail-loud guardrails and breach test | PASS | Lab 9 and runbook require intentional breach |
| 19 | Retention deletion verification | PASS | Records and verification procedure; backend behavior `[VERIFY]` |
| 20 | Safety, cleanup, rollback, no external services | PASS | Common safety contract and lab-specific cleanup |
| 21 | No unintended repository modifications | NOT RUN | This lesson content alone cannot verify external repository state |
| 22 | Teaching progression, not outline only | PASS | Definitions, worked examples, code, labs, incidents, decisions |
| 23 | No fabricated URLs/benchmarks/production claims | PASS | No external URLs or claimed production measurements |

**Audit limitation:** The five embedded Python test suites were extracted into a temporary directory and executed: 20 tests passed across the cardinality calculator, cost-driver report, unused-telemetry detector, telemetry forecast, and catalog linter. This validates those reference functions against their fixtures, not a live observability stack. Prometheus/Loki/Collector features, exact metrics, and deletion behavior remain `[VERIFY]`.

## Completion checklist

- [ ] Complete the cardinality calculator and tests.
- [ ] Generate a cost-driver report with source/window/unit and explicit missing-data statuses.
- [ ] Review unused-telemetry candidates with an owner; do not auto-delete.
- [ ] Run one log-reduction test preserving critical incident lines.
- [ ] Run one trace-reduction test preserving the fixture's error and slow traces.
- [ ] Create metrics/logs/traces retention decision records and verify deletion behavior or record the `[VERIFY]` limitation.
- [ ] Compare raw and recording-rule aggregate queries.
- [ ] Demonstrate a guardrail breach with a visible failure signal.
- [ ] Produce a unit-economics forecast with units and sensitivity analysis.
- [ ] Execute the cardinality game day and fill the measured timeline.
- [ ] Pass metric-catalog CI lint tests for valid and invalid fixtures.
- [ ] Prove before/after that incident logs, error traces, alerts, dashboards, and SLO calculations remain usable.
- [ ] Save evidence, configuration diffs, rollback result, and follow-up owners.

**Completion standard:** do not declare the unit complete merely because series or bytes fell. Completion requires a measured baseline, a bounded and reversible change, tests for preserved incident evidence and SLO behavior, a tested rollback path, and a catalog/owner record that prevents the same failure from returning.
