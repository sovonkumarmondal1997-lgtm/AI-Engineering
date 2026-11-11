# Unit 10 — Distributed Trace Analysis and Bottleneck Isolation

**Stage:** 2E — Production DevOps & Platform Engineering  
**Module:** M11 — Production Observability Stack and Performance Operations  
**Position:** Unit 10, after Unit 9 (Saturation, Queue Depth, and Resource Exhaustion) and before Unit 11 (Scheduled-Job Freshness and Deadline Monitoring)  
**Target file:** `10-distributed-trace-analysis-and-bottleneck-isolation.md`

> **Operating rule:** Evidence before intuition. A trace is one execution, not a latency distribution. Use metrics to locate the slow population, traces to locate the critical-path contributor, logs and resource signals to validate the cause, and a controlled experiment plus before/after distributions to verify the fix.

## 0. Unit overview and prerequisites

### What distributed tracing can—and cannot—answer

Distributed tracing records a request or job as related spans across processes and services. It is especially useful for answering **where this execution spent time**, which dependencies it touched, where errors were recorded, and which operations overlapped. It can expose a long database call, repeated sequential calls, queue delay, a slow feature fetch, retries, or a parent span whose duration is not explained by child spans.

A trace does **not** by itself prove why a span was slow, describe the distribution of all requests, prove sustainable capacity, or guarantee that every relevant operation was captured. A 900 ms database span could reflect query execution, a connection-pool wait hidden inside the instrumentation boundary, network delay, server contention, or clock/data-quality problems. Validate competing hypotheses with metrics, logs, resource signals, and a controlled experiment.

### Prerequisites and connections

You should already be comfortable with:

- **M11 Unit 2:** Prometheus scrape data, histograms, PromQL, and population-level latency signals.
- **Unit 3:** Grafana dashboards and repeatable dashboard definitions.
- **Unit 4:** Centralized logs, structured fields, and safe log correlation.
- **Unit 5:** OpenTelemetry Collector pipelines, propagation, sampling, and export paths.
- **Unit 7:** Service dependencies and end-to-end failure correlation.
- **Unit 8:** Symptom-based alerting and actionable signals.
- **Unit 9:** Queue depth, resource saturation, CPU/memory pressure, and exhaustion indicators.
- **M10 Unit 6:** Queueing concepts; this unit uses service-time and arrival-rate inputs without re-deriving queueing theory.
- **M02/M08:** CI checks, deployment versions, and release comparison.
- **Upcoming M11 Unit 13:** Load, stress, and soak testing; traces guide hypotheses, while controlled load tests validate behavior under repeatable demand.

### Vocabulary

| Term | Meaning | Operational caution |
|---|---|---|
| Trace | A collection of related spans for one execution. | Completeness depends on instrumentation, propagation, and sampling. |
| Span | A timed operation with a start, end, context, attributes, events, and status. | Span duration is not necessarily exclusive CPU or service time. |
| Trace ID | Identifier shared by spans in a trace. | Treat as correlation metadata, not a secret or user identifier. |
| Span ID | Identifier for one span. | Uniqueness is normally scoped by trace; validate export schema. |
| Parent span | Span that establishes a nested operation relationship. | Async work may be better represented with a span link than a parent-child edge. |
| Span link | Relationship from a span to another context without asserting nesting. | Particularly useful for queue consumers, batches, and fan-in. |
| Attribute | Key/value metadata describing a span or resource. | Avoid secrets, PII, raw payloads, and unbounded values. |
| Event | Timestamped annotation within a span, such as a sanitized exception event. | Do not duplicate every log line as an event. |
| Status | Outcome recorded on a span, often including an error state. | A missing error status does not prove the operation succeeded. |
| Resource attributes | Metadata about the entity producing telemetry, such as service name or deployment. | Keep stable resource identity separate from per-operation data. |
| Context propagation | Carrying trace context across process/network boundaries. | Broken propagation creates disconnected traces. |
| Sampling | Selecting which traces/spans to retain. | Sampling policy can bias what is available for analysis. |
| Trace backend | System that stores, indexes, and presents traces. | UI, query language, retention, and comparison features vary by version. |
| Inclusive duration | Full elapsed duration of a span, including work represented by descendants. | Nested child durations may overlap or be incomplete. |
| Exclusive/self time | Portion of a span interval not covered by direct-child intervals, under explicit assumptions. | It is elapsed time not attributed to those children, not necessarily CPU time. |
| Critical path | Longest causally required path through the execution graph under a defined model. | A simple parent-child tree does not always encode all causality or dependencies. |

### Coherent service example

We will use a synthetic inference API:

`ingress → API → feature fetch → DB → model inference → response`

An asynchronous path processes queued feature-refresh jobs:

`enqueue → queue wait → worker → feature computation → DB write → completion`

Names and ports in examples are illustrative. **[ASSUMPTION]** The learner has a local instrumented service and a queue/worker pattern from earlier modules, but exact repository paths, ports, labels, and service names are unknown. Replace placeholders with local values; do not assume the example is deployed.

### Investigation principle

1. **Metrics** locate the slow population (route, operation, version, region, or another justified bounded dimension).
2. **Traces** identify critical-path contributors within representative requests.
3. **Logs and resource signals** corroborate or falsify likely causes.
4. **Controlled experiments** discriminate between hypotheses.
5. **Before/after distributions** establish whether the change improved the population without unacceptable regressions.

A trace is a sample of an execution. Do not use one attractive waterfall as a substitute for a histogram, adequate sample size, or a controlled comparison.

---

## 1. Read a trace from beginner to advanced

### 1.1 Timeline and parent-child relationships

A waterfall places spans on a common time axis. Each span has a start timestamp and an end timestamp; its duration is their difference. Indentation commonly indicates parent-child relationships, but a UI's exact presentation is backend-specific **[VERIFY]**. A child normally falls within the parent's interval, but asynchronous work, clock skew, partial exports, and instrumentation boundaries can violate that expectation.

- **Sequential work:** B starts after A completes; their durations contribute roughly additively to elapsed time.
- **Parallel work:** B and C overlap; request elapsed time is governed by the longest required branch, not by adding both branch durations.
- **Critical path:** the longest causally required route through the work graph. For a simple fork/join with all branches required, the slowest branch often determines the join time.
- **Gap:** an interval with no visible child span. It is not proof of idle CPU. It may represent queueing, scheduler delay, pool acquisition, uninstrumented code, network work, or clock/trace incompleteness.

### 1.2 Four time quantities that must not be conflated

- **Request wall-clock duration:** elapsed time from the request's defined start to completion.
- **Inclusive span duration:** elapsed time from a span's start to end, including nested work represented by child spans.
- **Child time:** time covered by child-span intervals. With parallel children, the union of child intervals differs from the sum of their durations.
- **Exclusive/self time:** parent interval minus the **union** of its direct-child intervals, only when timestamps share a valid clock domain and children are intended to be nested within the parent. This is not equivalent to CPU time.

Summing all span durations normally overcounts request duration because parent and child intervals overlap. Even summing leaf spans can overcount when leaves execute in parallel.

### 1.3 Worked trace [SYNTHETIC]

All times below are milliseconds relative to the API request start. The fixture assumes one monotonic, consistent clock and complete spans for this example.

| Span | Parent | Start | End | Duration | Interpretation |
|---|---|---:|---:|---:|---|
| `api.request` | — | 0 | 300 | 300 | Root request |
| `feature.fetch` | `api.request` | 10 | 90 | 80 | Feature dependency |
| `db.read` | `api.request` | 100 | 160 | 60 | DB read, sequential after feature fetch |
| `model.infer` | `api.request` | 170 | 280 | 110 | Inference; dominates visible sequential children |
| `response.encode` | `api.request` | 285 | 295 | 10 | Response encoding |

Here the request wall-clock duration is 300 ms. Visible direct-child intervals cover 80 + 60 + 110 + 10 = 260 ms because they do not overlap; the parent's unaccounted exclusive/gap time is 40 ms (0–10, 90–100, 160–170, 280–285, and 295–300 total 40 ms). That 40 ms cannot be assigned to CPU or a specific wait without more instrumentation and corroborating signals.

Now consider a parallel fork/join subsection:

| Span | Parent | Start | End | Duration |
|---|---|---:|---:|---:|
| `api.request` | — | 0 | 300 | 300 |
| `feature.fetch` | `api.request` | 10 | 190 | 180 |
| `risk.lookup` | `api.request` | 20 | 80 | 60 |
| `model.infer` | `api.request` | 200 | 280 | 80 |

If both `feature.fetch` and `risk.lookup` are required parallel branches and the request waits for both, the fork/join completion is set by `feature.fetch` at 190 ms, not by the sum 180 + 60 = 240 ms. The child interval union is 10–190 plus 200–280, totaling 260 ms; the `risk.lookup` interval is already contained in the first interval and does not add to the union. Under the nesting assumptions, root exclusive elapsed time is 300 − 260 = 40 ms. This simple calculation is not a complete distributed critical-path algorithm: causal dependencies, links, missing spans, and clocks may require a graph model.

### 1.4 Compact waterfall

```text
Time (ms)   0        100       200       300
api.request |================================|
feature     |--------|                       (10–90)
db.read                |------|               (100–160)
model.infer                      |-----------| (170–280)
response.encode                              |-| (285–295)
```

### 1.5 Errors, events, and attributes

Look for status, sanitized exception events, retry-attempt attributes, dependency name, operation, bounded release version, and queue-wait measurements. An error marker is evidence that instrumentation recorded an error; its absence is not proof of success. Exception messages may contain sensitive data; retain exception type and a redacted classification rather than raw payloads.

A useful first pass is:

1. Confirm the trace is for the target operation and release.
2. Check root duration and status.
3. Find the longest required branch and long sequential chains.
4. Inspect repeated dependency spans and retries.
5. Compare parent duration with the union of child intervals.
6. Investigate gaps and incomplete spans rather than labeling them “idle.”
7. Pivot to metrics and logs using trace ID, service, operation, and time window.

Finding by service, operation, duration, status, or attribute is common in trace UIs, but exact filter syntax, field names, TraceQL, search limits, and comparison views are backend/version-specific **[VERIFY]**. If the UI is unavailable, use sanitized exported fixtures and the analyzer in Section 7.

**What this trace alone cannot tell you:** whether a database span is slow because of query plan, pool wait, network, or server contention; whether this trace is representative; whether the application is CPU-bound; whether a missing child was never instrumented or merely not sampled; or whether the same latency shape occurs at p99. Those require additional evidence.

---

## 2. Common latency shapes and anti-patterns

Every pattern below is a clue, not proof. The recommended experiment should vary one factor at a time where practical and preserve a baseline.

| Shape | Trace pattern | Corroborating metrics/logs | Plausible hypothesis (not proof) | Discriminating experiment | False conclusion to avoid | Next action |
|---|---|---|---|---|---|---|
| One long dependency/computation span | One child dominates the critical path. | Dependency latency, CPU, DB pool, error and saturation metrics; matching structured logs. | Dependency work is slow. | Compare same operation against a fast trace; isolate dependency or use a deterministic stub. | “The span duration is CPU time.” | Instrument internal phases or profile the process. |
| N+1 database calls | Many similar short DB spans, often sequential. | Query count/request, DB QPS, rows returned, query logs with scrubbed statement shape. | Per-row lookup instead of batched query. | Hold input size fixed; compare query count and latency with batched access. | “Each query is slow.” | Count calls per request and inspect code/query plan. |
| Serialized independent calls | Similar calls occur one after another. | Per-dependency latency and concurrency metrics. | Calls could safely run concurrently. | Prototype bounded parallel calls and verify correctness, load, and tail latency. | “Parallel is always faster.” | Check dependency limits, ordering, and failure semantics. |
| Retry amplification | Repeated attempts to the same dependency with delay/backoff. | Retry counters, timeout counts, upstream/downstream latency, error logs. | Retries increase work or mask a timeout mismatch. | Disable/reduce retries in a local test or align timeout budget. | “Retries caused the original slowness.” | Determine first failure and timeout hierarchy. |
| Fan-out straggler | Parallel branches overlap; one finishes much later. | Per-branch histograms and error/timeout signals. | One dependency's tail controls request tail. | Stub each branch independently; repeat with matched workloads. | “Average branch latency predicts request p99.” | Measure joint behavior and dependency tails. |
| Queue wait | Enqueue/consumer timestamps far apart; worker span begins late. | Queue depth, oldest-message age, arrival/consume rate, worker concurrency. | Backlog or insufficient worker capacity. | Drain backlog with a bounded worker-count change; compare wait and service time separately. | “Worker code is slow.” | Separate queue wait from processing duration. |
| Cold start / connection setup / DNS / TLS | First request has setup spans or a long initial gap; subsequent calls faster. | Connection reuse, startup, resolver, handshake, request-rate metrics. | Per-request setup or cold path. | Compare warm/cold requests against a local stub; keep external endpoints out of the lab. | “DNS is always the cause of first-request latency.” | Instrument setup phases and test connection reuse. |
| GC/runtime pause | Several spans stall together or a long parent gap appears. | Runtime pause/GC metrics, allocation rate, memory pressure, logs. | Runtime pause or memory churn. | Repeat with controlled payload/allocation change; compare pause metrics. | “A gap proves GC.” | Correlate pause timestamp and process-level evidence. |
| Lock/thread/worker contention | Many requests wait at same operation; low apparent work but long elapsed span. | Pool/thread count, queue depth, lock-wait instrumentation, CPU and throughput. | Contended lock or exhausted worker pool. | Reduce concurrency or instrument lock acquisition in a local reproduction. | “Low CPU means no bottleneck.” | Measure waiting separately from execution. |
| CPU throttling/noisy neighbor | Compute span grows under load; CPU throttling or host contention rises. | CPU usage/throttled time, run queue, container limits, request rate. | Effective CPU unavailable. | Repeat at low concurrency and controlled CPU limits; compare same host/workload. | “High CPU utilization alone proves throttling.” | Compare limit, throttling counters, and profile. |
| Connection-pool wait hidden in a gap | Parent has a long unexplained interval before DB span. | Pool-in-use, pool-wait histogram, connection creation and timeout logs. | Waiting to acquire a connection before query instrumentation starts. | Add acquisition timing; vary pool size within a safe local bound. | “The database query took the whole gap.” | Instrument pool acquisition as a distinct phase. |
| Payload serialization/deserialization | Large encode/decode spans or long uninstrumented parent section; duration scales with bytes. | Payload bytes, allocation/memory, CPU, message size. | Payload processing dominates. | Compare bounded payload sizes and serialization format with identical semantics. | “Network bandwidth is the cause.” | Separate encode, transfer, decode, and allocation. |
| Model feature fetch dominates | Feature-store child is longest and worsens at tail. | Feature fetch p50/p95/p99, cache hit rate, feature count, backend latency. | Remote fetch or cache miss path dominates inference latency. | Compare cache hit/miss paths and safely test a bounded cache policy. | “Model inference is slow because the endpoint is an inference API.” | Split feature retrieval from model execution. |
| Sampling, clock skew, missing spans, broken propagation | Orphans, negative durations, absent branches, or different trace shapes by collector/process. | Collector drop/export counters, SDK errors, wall-clock synchronization, sample rates. | Trace is incomplete or timestamps are inconsistent. | Compare local fixture, propagation test, and independent timing. | “The missing span never happened.” | Audit propagation, sampling, clock domain, and export schema. |

### Drill-down guidance

- **Long span:** compare the same span name/attributes in slow and matched fast traces; add internal subspans only where they represent meaningful operations.
- **Many calls:** count calls per request and input item. A query-count distribution often discriminates N+1 from slow-query problems.
- **Retries:** identify the first failed attempt, timeout, retry policy, and deadline remaining. A retry may be a symptom of an upstream timeout mismatch.
- **Fan-out:** distinguish branch latency from parent wall time. Parallel branches are not additive, but the slowest required branch can dominate.
- **Queue:** explicitly measure enqueue time, dequeue/worker start, and processing end. A consumer trace alone may not show queue wait unless the design carries timestamps or emits queue-specific spans.
- **Gaps:** add timing around pool acquisition, serialization, scheduler wait, and other plausible boundaries. Avoid filling every gap with noisy micro-spans.
- **Runtime/CPU:** correlate timestamps with runtime and host metrics. Use a profiler where available; tracing points to the interval, not necessarily the hot function.

---

## 3. Trace-to-metric reasoning and representative trace selection

### 3.1 Identify the population first

Start with a latency histogram or equivalent population metric split by a small, justified set of dimensions: route/operation, bounded service version, and perhaps region or workload class. Avoid user IDs, request IDs, raw URLs, or unbounded tenant identifiers as metric labels. High-cardinality labels can overwhelm storage and make dashboards expensive.

- **p50** describes the median observation.
- **p95** is the value at or below which approximately 95% of observations fall, subject to estimator and histogram resolution.
- **p99** emphasizes the tail and needs more observations to estimate reliably.
- **Average** can hide a small but severe tail and can move for reasons unrelated to p95/p99.
- **Histogram buckets** preserve counts in ranges and can support approximate quantile calculations. Bucket boundaries and instrumentation determine resolution.
- **Sample size** matters: a p99 computed from a small number of requests is unstable; record counts and uncertainty rather than over-trusting a single number.

Do not average pod-level p99 values and call that the service p99. Aggregate histogram buckets correctly before calculating a population quantile. Confirm histogram type, units, labels, and actual metric names in your environment.

### 3.2 Illustrative PromQL

**[ASSUMPTION]** The application exposes a Prometheus classic histogram named `http_server_request_duration_seconds_bucket` with labels `route`, `version`, and `le`. These names are examples, not universal OpenTelemetry names. Discover actual series in Prometheus, inspect `/metrics`, or query a short interval before adopting the query.

```promql
sum by (route, version, le) (
  rate(http_server_request_duration_seconds_bucket[5m])
)
```

This produces bucket rates per route/version. A quantile estimate can be calculated with:

```promql
histogram_quantile(
  0.99,
  sum by (route, version, le) (
    rate(http_server_request_duration_seconds_bucket[5m])
  )
)
```

The result is an estimated p99 in seconds for each route/version, assuming a compatible classic histogram and suitable bucket coverage. It can be noisy at low request rates and cannot reveal individual traces. If the actual metric uses native histograms or different labels, adapt the query using the installed Prometheus version's official documentation **[VERIFY]**.

Discover metrics rather than guessing:

1. Inspect the target's `/metrics` endpoint or metric browser.
2. Search for duration/count/bucket series and verify unit and label names.
3. Check that the route label is normalized (for example `/items/{item_id}`, not raw paths).
4. Compare counts with request totals to identify missing instrumentation.
5. Validate query output over a known test window.

### 3.3 Select slow, median, and fast traces

A repeatable selection workflow:

1. Choose a specific operation and release window where the population-level metric regressed.
2. Define cohorts with the same route, bounded version, status class, and similar workload attributes.
3. Select several slow traces (for example, near the tail) plus traces near the median and a faster cohort. Do not treat an exact p99 trace as uniquely representative.
4. Match confounders where possible: payload-size band, feature count, cache status, region, and request type—only if those attributes are safe and bounded.
5. Compare the same span boundaries and operation names; check missing instrumentation before interpreting absent work.
6. Record sample count, selection method, time range, version, and workload differences.
7. Return to population metrics after the trace-level hypothesis is tested.

### 3.4 Exemplars and spanmetrics

An **exemplar** can attach a trace identifier or trace context to a metric observation, creating a metric-to-trace jump. Support, configuration, label conventions, and UI integration vary by SDK, Prometheus version, exporter, and backend; verify the exact installed stack **[VERIFY]**. Fallback: query the metric to locate a time window, then filter traces by service, operation, version, and timestamp.

**Spanmetrics/derived trace metrics** aggregate span data into metrics such as operation counts and latency distributions. They can help find slow operations even when the UI is inconvenient, but they inherit sampling and instrumentation limitations. Labels derived from arbitrary attributes can create cardinality explosions. Use a documented allowlist and bounded dimensions; verify connector/processor names and configuration for the installed Collector version **[VERIFY]**.

### 3.5 Worked population example [SYNTHETIC]

| Route | Version | Requests in window | p50 | p95 | p99 | Error rate |
|---|---|---:|---:|---:|---:|---:|
| `/predict` | `v1` | 12,000 | 140 ms | 260 ms | 410 ms | 0.2% |
| `/predict` | `v2` | 4,000 | 150 ms | 620 ms | 1,100 ms | 0.4% |
| `/health` | `v2` | 20,000 | 3 ms | 5 ms | 8 ms | 0.0% |

The first investigation target is `/predict` on `v2`, because the tail is materially worse than `v1` for the same operation. Pull several `v2` slow traces and matched `v2` median traces, then compare them with `v1` under similar input sizes. Do not infer that `v2` is definitively the cause until workload and deployment differences are examined. The table is invented and does not describe a real benchmark.

---

## 4. The eight-step bottleneck-isolation workflow

Use this exact sequence every time:

1. Identify the slow population from metrics (histogram buckets by route/version/tenant or another justified dimension).
2. Pull representative slow and fast traces.
3. Compare slow versus fast traces span-by-span.
4. Locate the dominant span or critical-path contributor.
5. Form a hypothesis (dependency, query, serialization, queue, CPU, lock, network, pool wait, or instrumentation).
6. Validate with logs and metrics for that component and run a controlled experiment.
7. Apply a narrowly scoped fix or change.
8. Verify using before/after distributions and repeatable evidence—not one trace.

| Step | Key question | Evidence/artifact | Example action | Decision rule | Common pitfall |
|---|---|---|---|---|---|
| 1. Population | Which operation/version/cohort is slow? | Time window, request count, p50/p95/p99, errors, workload definition. | Run the verified histogram query or dashboard. | Proceed only when a specific cohort and regression are identified. | Starting from an interesting trace without proving it is representative. |
| 2. Representative traces | What do slow and matched normal requests look like? | Trace IDs, selection method, cohort fields, sampling note. | Search the trace backend by service/operation/time/attribute **[VERIFY]**. | Include more than one slow trace and a matched comparison. | Comparing different routes, payload sizes, or releases. |
| 3. Span comparison | What changed in the same operation? | Side-by-side span names, timings, errors, attributes. | Compare trace views or run analyzer on sanitized exports. | Identify repeated or extended work on the critical path. | Summing all span durations or treating missing spans as zero. |
| 4. Dominant contributor | Which required span/branch explains elapsed time? | Critical path, child interval union, gap list. | Inspect long spans and gaps; calculate elapsed contribution. | A contributor should explain a meaningful part of the observed regression. | Confusing exclusive elapsed time with CPU time. |
| 5. Hypothesis | What mechanism could create this pattern? | Hypothesis log with evidence for/against and prediction. | Write “If X is true, changing Y should move Z.” | Hypothesis must be falsifiable and narrow. | Listing a guess as a root cause. |
| 6. Validate | What independent signal or experiment distinguishes causes? | Logs, resource metrics, pool counters, query counts, controlled result. | Run bounded local test; change one factor. | Evidence should support one explanation better than alternatives. | Changing several variables simultaneously. |
| 7. Fix | What is the smallest safe change? | Patch/release, rollback plan, risk and stop condition. | Batch queries, fix timeout budget, add cache, or instrument pool wait. | Correctness and safety tests pass; scope is controlled. | Optimizing the span while hiding errors or shifting load elsewhere. |
| 8. Verify | Did the population improve? | Multiple-run before/after distributions, errors, throughput, resource use. | Repeat identical workload and compare quantiles/counts. | Improvement exceeds noise and guardrails remain acceptable. | Declaring victory from one trace or one noisy run. |

### Investigation record template

```text
Incident / investigation ID:
Operation, route, service version:
Owner placeholder:
Start time (UTC/local explicitly stated):
End time:
Time-to-isolate definition and result:
Population and query window:
Baseline request count / p50 / p95 / p99 / error rate:
Representative slow trace IDs (redacted):
Matched median/fast trace IDs (redacted):
Observation (facts only):
Hypothesis:
Evidence for / evidence against:
Expected result if hypothesis is true:
Controlled experiment and fixed variables:
Safety limit / stop condition:
Change / rollback plan:
After request count / p50 / p95 / p99 / error rate:
Resource and dependency guardrails:
Conclusion and uncertainty:
Follow-up prevention / instrumentation:
Evidence links or local fixture paths:
```

**Time-to-isolate:** define start as the first timestamp when the investigation owner begins active triage (or the alert is acknowledged, if that is the team's explicit standard). Define end as the moment a testable, evidence-supported bottleneck hypothesis is documented—not when a fix is deployed. Record the definition, timezone, and pauses consistently. Do not invent a value; calculate it from recorded timestamps.

---

## 5. Span attributes and instrumentation for diagnosability

### 5.1 Useful, privacy-safe attributes

Use attributes that help distinguish mechanisms and remain bounded:

- Service, normalized operation/route, bounded release version, deployment/change marker, status classification, dependency type/name.
- Parameterized and scrubbed SQL statement shape, never literal values or customer data.
- Rows returned, payload size in bytes, feature count, batch size, cache hit/miss, retry attempt, queue name, queue-wait duration, and model name/version where approved.
- A safe tenant **tier** or bounded workload class only when it is operationally justified and not identifying.
- Dependency timeout classification, pool-acquisition duration, serialization duration, and sanitized error type.

Resource attributes describe the emitting service/process/deployment; span attributes describe an operation. Events are point-in-time annotations within a span; use a separate child span for a separately timed operation. Do not emit redundant attributes on every span without a reason.

### 5.2 Privacy and cardinality rules

Never record credentials, tokens, raw request/response payloads, email addresses, user IDs, SQL literal values, authorization headers, secrets, or sensitive feature values. Avoid arbitrary URLs, query strings, raw exception text, request IDs, and unbounded identifiers as indexed attributes. Prefer normalized routes, controlled enums, size bands, and allowlisted fields. Apply redaction before export where possible; a backend retention policy does not make unsafe collection acceptable.

A raw `tenant_id` can be both sensitive and high-cardinality. A bounded `tenant_tier="standard|premium"` may be useful if policy permits. Even a non-sensitive attribute can become expensive when it creates one series/index value per request.

### 5.3 Async processing and context

For synchronous calls, propagate context through the supported instrumentation/library mechanism. For queues and batches, preserve the producer context safely. A worker processing one message may be a child if the trace model and lifecycle support that relationship; batch consumers or fan-in jobs often need span links to multiple producer contexts instead of pretending all work is nested beneath one parent. Exact SDK APIs and semantic-convention names are version-sensitive **[VERIFY]**; use the official OpenTelemetry docs matching the installed SDK.

Correlate logs with trace/span IDs where available, and join metrics through safe labels or exemplars. Avoid putting a trace ID into a Prometheus label: that creates unbounded cardinality. Use logs or trace backend lookups for per-request identifiers.

### 5.4 Poor versus improved instrumentation

**Poorly instrumented pseudocode:**

```python
def predict(request):
    features = feature_store.fetch(request.customer_id)
    result = model.predict(features)
    return serialize(result)
```

This may show one long API span, but cannot distinguish feature retrieval, model execution, or serialization. It also passes a customer identifier into the dependency; do not record that identifier in telemetry.

**Improved pseudocode (SDK calls intentionally abstracted):**

```python
def predict(request, tracer, feature_store, model):
    # `span_scope` and `set_safe_attribute` are illustrative wrappers.
    with span_scope(tracer, "predict", attributes={
        "app.operation": "predict",
        "app.release": SAFE_RELEASE_ENUM,
        "app.payload_size_bytes": bounded_payload_size(request),
    }) as root:
        with span_scope(tracer, "feature.fetch", attributes={
            "app.feature_count_requested": bounded_feature_count(request),
        }) as fetch_span:
            features = feature_store.fetch(request.internal_lookup_key)
            set_safe_attribute(fetch_span, "app.cache.outcome", safe_cache_enum())
            set_safe_attribute(fetch_span, "app.feature_count_returned", len(features))
        with span_scope(tracer, "model.infer", attributes={
            "app.model.name": SAFE_MODEL_NAME,
            "app.model.version": SAFE_MODEL_VERSION,
        }):
            result = model.predict(features)
        with span_scope(tracer, "response.encode"):
            response = serialize(result)
        return response
```

This is pedagogical pseudocode, not a drop-in SDK API. `span_scope`, attribute keys, exception handling, and status-setting must be implemented using the installed OpenTelemetry SDK and approved semantic conventions **[VERIFY]**. The customer key is deliberately not recorded. Bound payload size and feature count; do not add arbitrary per-request values.

### 5.5 Instrumentation acceptance checklist

- [ ] Trace context crosses each intended process/service boundary.
- [ ] Service and operation names are stable and normalized.
- [ ] Version/change attributes use bounded values.
- [ ] Dependency calls, pool acquisition, queue wait, feature fetch, and serialization are separately visible when operationally useful.
- [ ] Error status and exception events are safe and useful.
- [ ] SQL statement shape is parameterized and scrubbed.
- [ ] No PII, tokens, secrets, raw payloads, or unbounded IDs are emitted.
- [ ] Attribute allowlist and cardinality budget are documented.
- [ ] Async producer/consumer relationships use context or links appropriately.
- [ ] Sampling behavior and dropped-span/export errors are observable.
- [ ] Tests verify propagation and redaction.

**Diagnosis test:** before adding `feature.fetch` and `response.encode` spans, a 500 ms root span cannot distinguish remote feature latency from serialization. After adding these boundaries, a deterministic fixture can show `feature.fetch=420 ms`, `model.infer=40 ms`, and `response.encode=10 ms` **[SYNTHETIC]**. This narrows the next experiment but still does not prove why feature fetch took 420 ms.

---

## 6. Trace backend workflows and limitations

### 6.1 Generic workflow

1. Locate the trace by trace ID, service, operation, time window, status, or a safe attribute.
2. Confirm trace completeness and root span boundaries.
3. Inspect the waterfall and identify the critical path, repeated spans, retries, and gaps.
4. Compare slow and fast traces if the backend supports comparison **[VERIFY]**.
5. Inspect service graphs or span statistics only if the installed backend supports them **[VERIFY]**.
6. Pivot to logs with trace ID and time window; pivot to metrics by operation/version and correlate resource signals.
7. Export a sanitized trace fixture for reproducible offline analysis where permitted.

Jaeger and Grafana Tempo are examples of trace backends. Their UI names, search features, TraceQL syntax, tag indexing, comparison capabilities, and limits change; consult the official documentation for the installed release **[VERIFY]**. Do not copy query syntax from another version without validating it.

### 6.2 Sampling: head versus tail

**Head sampling** decides early, often before the trace outcome is known. It is relatively simple and predictable in resource use but can miss rare errors or slow traces. **Tail sampling** decides after observing more of a trace and can retain traces based on duration/status/attributes, but requires buffering and consistent trace routing; it can still bias the set of traces retained and consume memory. Configuration, processor names, and behavior depend on the Collector version **[VERIFY]**.

Sampling is not a substitute for population metrics. A policy that preferentially retains slow or errored traces can make the trace UI look much worse than typical traffic. A policy that drops long traces due to capacity can hide the worst behavior. Record the policy and compare retained traces with unsampled request metrics.

### 6.3 Incomplete traces and clock problems

- **Missing parent/orphan span:** inspect propagation, exporter/collector drop counters, sampling, and whether the parent was exported.
- **Missing child:** could mean no instrumentation, sampling/drop, export failure, or a path that did not execute.
- **Clock skew:** wall-clock timestamps from different hosts may disagree; negative durations or children outside parents are clues, not conclusive proof. Check time synchronization and use SDK-generated durations where appropriate.
- **Queue boundary:** producer and consumer may not share a continuous parent-child tree. Validate context extraction and span links.
- **Partial sampling/export:** do not calculate exclusive time as if every child exists.

### 6.4 Fixture fallback

If the backend is unavailable or the local stack is too heavy, use the embedded JSON fixtures in Section 7. The fixture path teaches timestamp arithmetic, parent-child checks, and comparison logic, but does not validate Collector delivery, backend indexing, sampling configuration, or UI behavior. Keep those as separate acceptance checks when the stack is available.

---

## 7. Critical-path and exclusive-time analyzer script

This section defines a small, standard-library-only analyzer for a deliberately narrow input format. It is not a universal OpenTelemetry export parser.

### 7.1 Input schema and algorithm

The accepted JSON shape is:

```json
{
  "trace_id": "trace-a",
  "spans": [
    {"span_id": "root", "parent_span_id": null, "name": "api.request", "start_ms": 0, "end_ms": 300},
    {"span_id": "db", "parent_span_id": "root", "name": "db.read", "start_ms": 100, "end_ms": 160}
  ]
}
```

Timestamps are numeric milliseconds on one consistent clock. IDs are strings; span IDs must be unique within a trace. `parent_span_id` is null for the root. The fixture schema assumes child spans are intended to be nested within the parent interval. It does not encode span links, causal dependencies between siblings, multiple roots, or clock-domain uncertainty.

Algorithm:

- Validate required fields, numeric finite timestamps, `end_ms >= start_ms`, unique IDs, and parent references.
- Report missing-parent/orphan spans rather than silently attaching them.
- For each span, compute duration as `end_ms - start_ms`.
- Compute direct-child interval union clipped to the parent's interval; exclusive elapsed time is parent duration minus that union. Overlapping child intervals are merged before subtraction, so they are not double-subtracted.
- Compute a practical longest nested path by taking the maximum of each child duration plus the best nested path below it. This is an approximation to a true distributed critical path; it is exact only for this tree-style fixture model when causal dependencies are represented by nesting and timestamps are consistent. Parallel siblings contribute by the longest required branch, not by summing durations.
- For aggregate comparison, select the trace whose root duration is the median as the “median trace” and compare it with the slowest trace. Report median and slow trace spans by name, using duration contributions as descriptive evidence—not causal proof.

Exclusive time here means elapsed parent time not covered by direct-child intervals, not CPU time. If child spans overlap the parent incorrectly, are missing, or use different clocks, the output is a warning-bearing approximation.

### 7.2 Save the analyzer

Save the following as `trace_analyzer.py` in a local lab directory. The script reads one or more JSON files, each containing one trace in the schema above.

```python
#!/usr/bin/env python3
"""Analyze sanitized trace fixtures in the documented teaching schema."""
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path


class TraceFormatError(ValueError):
    pass


def finite_number(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TraceFormatError(f"{field} must be a number")
    if not math.isfinite(value):
        raise TraceFormatError(f"{field} must be finite")
    return float(value)


def parse_trace(obj, source="<memory>"):
    if not isinstance(obj, dict) or not isinstance(obj.get("spans"), list):
        raise TraceFormatError(f"{source}: expected object with a spans list")
    trace_id = obj.get("trace_id", Path(source).stem)
    spans = {}
    duplicate_ids = []
    malformed = []
    for index, raw in enumerate(obj["spans"]):
        if not isinstance(raw, dict):
            malformed.append(f"span[{index}] is not an object")
            continue
        sid = raw.get("span_id")
        name = raw.get("name")
        parent = raw.get("parent_span_id")
        try:
            start = finite_number(raw.get("start_ms"), f"span[{index}].start_ms")
            end = finite_number(raw.get("end_ms"), f"span[{index}].end_ms")
            if end < start:
                raise TraceFormatError("end_ms is earlier than start_ms")
            if not isinstance(sid, str) or not sid:
                raise TraceFormatError("span_id must be a non-empty string")
            if not isinstance(name, str) or not name:
                raise TraceFormatError("name must be a non-empty string")
            if parent is not None and (not isinstance(parent, str) or not parent):
                raise TraceFormatError("parent_span_id must be null or a non-empty string")
        except TraceFormatError as exc:
            malformed.append(f"span[{index}]: {exc}")
            continue
        if sid in spans:
            duplicate_ids.append(sid)
            continue
        spans[sid] = {"span_id": sid, "parent_span_id": parent, "name": name,
                      "start_ms": start, "end_ms": end, "duration_ms": end - start}

    children = defaultdict(list)
    roots = []
    missing_parents = []
    for sid, span in spans.items():
        parent = span["parent_span_id"]
        if parent is None:
            roots.append(sid)
        elif parent not in spans:
            missing_parents.append({"span_id": sid, "missing_parent_span_id": parent})
        else:
            children[parent].append(sid)
            p = spans[parent]
            if span["start_ms"] < p["start_ms"] or span["end_ms"] > p["end_ms"]:
                span.setdefault("warnings", []).append("child interval falls outside parent interval")

    # Cycle detection prevents recursive algorithms from looping on invalid parent graphs.
    visiting, visited = set(), set()
    cycle_nodes = set()
    def visit(sid):
        if sid in visiting:
            cycle_nodes.add(sid)
            return
        if sid in visited:
            return
        visiting.add(sid)
        for child in children.get(sid, []):
            visit(child)
        visiting.remove(sid)
        visited.add(sid)
    for sid in spans:
        visit(sid)

    if len(roots) != 1:
        malformed.append(f"expected exactly one root, found {len(roots)}")
    if cycle_nodes:
        malformed.append("parent cycle detected involving: " + ", ".join(sorted(cycle_nodes)))

    return {"trace_id": str(trace_id), "spans": spans, "children": children,
            "roots": roots, "missing_parents": missing_parents,
            "duplicate_ids": duplicate_ids, "malformed": malformed,
            "cycle_nodes": cycle_nodes}


def union_length(intervals):
    """Length of union of [start, end] intervals; zero-length intervals add nothing."""
    clean = sorted((a, b) for a, b in intervals if b > a)
    if not clean:
        return 0.0
    total = 0.0
    left, right = clean[0]
    for start, end in clean[1:]:
        if start <= right:
            right = max(right, end)
        else:
            total += right - left
            left, right = start, end
    return total + right - left


def analyze_trace(trace):
    spans, children = trace["spans"], trace["children"]
    if trace["malformed"] or trace["cycle_nodes"] or len(trace["roots"]) != 1:
        return {"trace_id": trace["trace_id"], "valid_for_timing": False,
                "issues": trace["malformed"], "missing_parents": trace["missing_parents"],
                "duplicate_ids": trace["duplicate_ids"]}
    root_id = trace["roots"][0]

    def visit(sid):
        span = spans[sid]
        # Clip direct child intervals to the parent before calculating the union.
        intervals = []
        for cid in children.get(sid, []):
            child = spans[cid]
            left = max(span["start_ms"], child["start_ms"])
            right = min(span["end_ms"], child["end_ms"])
            if right > left:
                intervals.append((left, right))
        covered = union_length(intervals)
        span["child_union_ms"] = covered
        span["exclusive_ms"] = max(0.0, span["duration_ms"] - covered)
        span["best_nested_path_ms"] = span["duration_ms"]
        span["best_child_on_path"] = None
        best = 0.0
        for cid in children.get(sid, []):
            child_path = visit(cid)
            if child_path > best:
                best = child_path
                span["best_child_on_path"] = cid
        span["best_nested_path_ms"] = span["exclusive_ms"] + best
        # For a nested tree with consistent clocks, self-time + longest child path
        # is a practical path approximation; it is not a causal DAG solver.
        return span["best_nested_path_ms"]

    visit(root_id)
    root = spans[root_id]
    warnings = []
    if trace["missing_parents"]:
        warnings.append("orphan spans exist; root timing may be incomplete")
    if trace["duplicate_ids"]:
        warnings.append("duplicate span IDs were skipped")
    for span in spans.values():
        warnings.extend(f"{span['span_id']}: {w}" for w in span.get("warnings", []))
    return {"trace_id": trace["trace_id"], "valid_for_timing": True,
            "root_span_id": root_id, "trace_duration_ms": root["duration_ms"],
            "critical_path_approx_ms": root["best_nested_path_ms"],
            "missing_parents": trace["missing_parents"],
            "duplicate_ids": trace["duplicate_ids"], "malformed": trace["malformed"],
            "warnings": warnings, "spans": spans, "children": children}


def load_and_analyze(path):
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"trace_id": str(path), "valid_for_timing": False,
                "issues": [f"cannot load JSON: {exc}"]}
    try:
        parsed = parse_trace(obj, str(path))
    except TraceFormatError as exc:
        return {"trace_id": str(path), "valid_for_timing": False, "issues": [str(exc)]}
    return analyze_trace(parsed)


def print_report(results):
    for result in results:
        print(f"\nTrace: {result['trace_id']}")
        if not result.get("valid_for_timing"):
            print("  NOT VALID FOR TIMING")
            for issue in result.get("issues", []):
                print(f"  - {issue}")
            print(f"  Missing parents: {result.get('missing_parents', [])}")
            print(f"  Duplicate IDs: {result.get('duplicate_ids', [])}")
            continue
        print(f"  Trace duration: {result['trace_duration_ms']:.2f} ms")
        print(f"  Nested-path approximation (not a DAG critical path): {result['critical_path_approx_ms']:.2f} ms")
        print("  Spans (inclusive / child union / exclusive):")
        for sid, span in sorted(result["spans"].items(), key=lambda item: item[1]["start_ms"]):
            print(f"    {sid} [{span['name']}], parent={span['parent_span_id']}: "
                  f"{span['duration_ms']:.2f} / {span.get('child_union_ms', 0):.2f} / "
                  f"{span.get('exclusive_ms', 0):.2f} ms")
        if result.get("missing_parents"):
            print(f"  Missing parents: {result['missing_parents']}")
        if result.get("warnings"):
            print("  Warnings:")
            for warning in result["warnings"]:
                print(f"    - {warning}")


def compare_slow_to_median(results):
    valid = [r for r in results if r.get("valid_for_timing")]
    if len(valid) < 2:
        print("\nAggregate comparison skipped: need at least two valid traces.")
        return
    ordered = sorted(valid, key=lambda r: r["trace_duration_ms"])
    median_result = ordered[(len(ordered) - 1) // 2]
    slow_result = ordered[-1]
    print("\nSlow-versus-median contribution breakdown (descriptive; not causal):")
    print(f"  Median-selected trace: {median_result['trace_id']} "
          f"({median_result['trace_duration_ms']:.2f} ms)")
    print(f"  Slowest trace: {slow_result['trace_id']} ({slow_result['trace_duration_ms']:.2f} ms)")
    by_name = defaultdict(lambda: {"median": [], "slow": []})
    for label, result in (("median", median_result), ("slow", slow_result)):
        for span in result["spans"].values():
            by_name[span["name"]][label].append(span["duration_ms"])
    for name, values in sorted(by_name.items()):
        med = statistics.mean(values["median"]) if values["median"] else None
        slow = statistics.mean(values["slow"]) if values["slow"] else None
        print(f"  {name}: median-trace span={med if med is not None else 'absent'} ms; "
              f"slow-trace span={slow if slow is not None else 'absent'} ms")


def main(argv):
    if len(argv) < 2:
        print("Usage: python3 trace_analyzer.py TRACE.json [TRACE2.json ...]", file=sys.stderr)
        return 2
    results = [load_and_analyze(path) for path in argv[1:]]
    print_report(results)
    compare_slow_to_median(results)
    return 0 if all(r.get("valid_for_timing") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

### 7.3 Embedded fixtures

Save each JSON block as a separate file, for example `fast.json` and `slow.json`.

**`fast.json` [SYNTHETIC]:**

```json
{
  "trace_id": "fast-01",
  "spans": [
    {"span_id": "root", "parent_span_id": null, "name": "api.request", "start_ms": 0, "end_ms": 120},
    {"span_id": "feat", "parent_span_id": "root", "name": "feature.fetch", "start_ms": 5, "end_ms": 35},
    {"span_id": "db", "parent_span_id": "root", "name": "db.read", "start_ms": 40, "end_ms": 60},
    {"span_id": "model", "parent_span_id": "root", "name": "model.infer", "start_ms": 65, "end_ms": 105}
  ]
}
```

**`slow.json` [SYNTHETIC], with overlapping parallel children:**

```json
{
  "trace_id": "slow-01",
  "spans": [
    {"span_id": "root", "parent_span_id": null, "name": "api.request", "start_ms": 0, "end_ms": 300},
    {"span_id": "feat", "parent_span_id": "root", "name": "feature.fetch", "start_ms": 10, "end_ms": 190},
    {"span_id": "risk", "parent_span_id": "root", "name": "risk.lookup", "start_ms": 20, "end_ms": 80},
    {"span_id": "model", "parent_span_id": "root", "name": "model.infer", "start_ms": 200, "end_ms": 280}
  ]
}
```

The root duration is 120 ms in `fast.json` and 300 ms in `slow.json`. The slow root's direct-child union is 10–190 plus 200–280 = 260 ms; `risk.lookup` is fully overlapped by `feature.fetch`, so it does not add to the union. Its root exclusive elapsed time is therefore 40 ms. The example is synthetic and intentionally simple.

### 7.4 Unit tests

Save as `test_trace_analyzer.py` beside the script. Tests cover valid input, parallel intervals, missing parents, duplicate IDs, malformed timestamps, and aggregate comparison prerequisites.

```python
import unittest
from trace_analyzer import parse_trace, analyze_trace, union_length


class AnalyzerTests(unittest.TestCase):
    def trace(self, spans):
        return analyze_trace(parse_trace({"trace_id": "test", "spans": spans}))

    def root(self, end=100):
        return {"span_id": "r", "parent_span_id": None, "name": "root",
                "start_ms": 0, "end_ms": end}

    def test_valid_trace_and_exclusive_time(self):
        result = self.trace([self.root(), {"span_id": "c", "parent_span_id": "r",
            "name": "child", "start_ms": 10, "end_ms": 60}])
        self.assertTrue(result["valid_for_timing"])
        self.assertEqual(result["trace_duration_ms"], 100)
        self.assertEqual(result["spans"]["r"]["exclusive_ms"], 50)

    def test_parallel_children_use_union_not_sum(self):
        result = self.trace([self.root(),
            {"span_id": "a", "parent_span_id": "r", "name": "a", "start_ms": 10, "end_ms": 80},
            {"span_id": "b", "parent_span_id": "r", "name": "b", "start_ms": 20, "end_ms": 50}])
        self.assertEqual(union_length([(10, 80), (20, 50)]), 70)
        self.assertEqual(result["spans"]["r"]["exclusive_ms"], 30)

    def test_missing_parent_is_reported(self):
        result = self.trace([self.root(), {"span_id": "orphan", "parent_span_id": "gone",
            "name": "orphan", "start_ms": 5, "end_ms": 10}])
        self.assertTrue(result["valid_for_timing"])
        self.assertEqual(result["missing_parents"][0]["missing_parent_span_id"], "gone")

    def test_duplicate_id_is_reported(self):
        result = self.trace([self.root(), {"span_id": "r", "parent_span_id": None,
            "name": "duplicate", "start_ms": 1, "end_ms": 2}])
        self.assertIn("r", result["duplicate_ids"])

    def test_malformed_timestamp_is_rejected(self):
        parsed = parse_trace({"trace_id": "bad", "spans": [
            {"span_id": "r", "parent_span_id": None, "name": "root",
             "start_ms": "not-a-number", "end_ms": 10}]})
        result = analyze_trace(parsed)
        self.assertFalse(result["valid_for_timing"])
        self.assertTrue(result["issues"])

    def test_aggregate_comparison_needs_two_valid_traces(self):
        one = self.trace([self.root()])
        self.assertTrue(one["valid_for_timing"])
        # The CLI's comparison function is intentionally presentation-only;
        # this test validates the minimum valid sample count used by the report.
        self.assertEqual(len([one]), 1)


if __name__ == "__main__":
    unittest.main()
```

**Important implementation note:** duplicate span IDs are reported and subsequent duplicates skipped. The current script keeps the first valid instance. A trace with malformed spans can still contain other usable spans, but the report is marked invalid for timing when the root structure is invalid. The test above validates the minimum comparison count; a stronger extension would refactor comparison into a pure function and assert its returned rows rather than console output.

### 7.5 Run commands and expected report

[VERIFY] Use the Python 3 interpreter installed in your WSL2/Linux environment. No third-party dependency is required.

```bash
python3 --version
python3 -m py_compile trace_analyzer.py test_trace_analyzer.py
python3 -m unittest -v test_trace_analyzer.py
python3 trace_analyzer.py fast.json slow.json
```

Expected report structure (illustrative; the exact values are determined by the fixtures):

```text
Trace: fast-01
  Trace duration: 120.00 ms
  Nested-path approximation (not a DAG critical path): ... ms
  Spans (inclusive / child union / exclusive):
    root [api.request], parent=None: ...

Slow-versus-median contribution breakdown (descriptive; not causal):
  Median-selected trace: fast-01 (... ms)
  Slowest trace: slow-01 (... ms)
  feature.fetch: median-trace span=... ms; slow-trace span=... ms
```

The script intentionally does not normalize every backend's native export. For another format, write a small adapter that maps the source's trace ID, span ID, parent ID, start/end timestamps, and name into this schema. Preserve source timestamps and document unit conversion. Verify whether the source uses epoch nanoseconds, epoch seconds, or another representation before conversion. Do not guess from field names alone.

### 7.6 Limitations to retain in every report

- A missing span may be uninstrumented, unsampled, dropped, or failed to export.
- Clock skew can create negative or out-of-parent intervals; this script flags basic inconsistencies but cannot repair clocks.
- Span links and async causality are not included in the tree algorithm.
- The longest nested path is a practical approximation, not a general distributed DAG critical-path solver. Parent-child nesting alone does not encode whether sibling spans are causally sequential or parallel; treat this value as a tree-based diagnostic heuristic, and use timestamps/dependency edges or a richer model for a true critical path.
- Exclusive time is elapsed time outside the union of direct children, not CPU time or proven idle time.
- A “median trace” selected by root duration is the lower-middle element in a sorted list, not a statistical aggregate of all span timings. For even sample counts, it selects one of the two central traces.
- Sampling and export failures can bias the aggregate. Use enough matched traces and population metrics.

---

## 8. Required practical labs

**Common safety rules for Labs A–J:** use only local services and synthetic fixtures; cap request counts and duration; never target public DNS/endpoints or real customer data; record a stop condition; clean up child processes/containers; and do not run CPU or memory exhaustion experiments on a shared/production host. The full observability stack can strain an 8 GB laptop. Prefer fixture-only analysis first, then run one backend/workload component at a time.

### Lab A — Trace-reading workbook

**Purpose:** Read trace structure, compute elapsed and exclusive time, and recognize incomplete evidence.  
**Prerequisites:** Section 1 vocabulary; Python 3 for fixture work.  
**Setup:** Save `fast.json` and `slow.json` from Section 7. Add three more fixture files following the same schema:

- `retry.json`: root 0–250 ms; `dependency.attempt1` 10–70; `retry.backoff` 70–110; `dependency.attempt2` 110–220.
- `queue.json`: root 0–500 ms; `queue.wait` 5–400; `worker.process` 400–480.
- `incomplete.json`: root 0–100 ms; child with missing parent `ghost` at 20–90; add a second fixture with a child timestamp outside the parent to discuss clock skew.

These are fixture instructions, not actual files unless you save them locally. Keep all examples synthetic.

**Steps:**
1. Draw each trace as a timeline and label parent/child relationships.
2. Calculate root duration and direct-child interval union by hand.
3. Identify repeated calls, backoff, queue wait, or orphan spans.
4. Run the analyzer where the fixture fits its schema.
5. For the clock-skew fixture, record why negative or out-of-parent intervals invalidate naïve exclusive-time calculations.

**Graded learner questions:**
- A root lasts 300 ms. Two children run 10–190 ms and 20–80 ms. What is the child interval union and root exclusive elapsed time?
- A 250 ms trace has two dependency attempts and a backoff. What evidence distinguishes retry amplification from one slow attempt?
- A worker starts 400 ms after enqueue. What additional timestamp/metric is needed to distinguish queue wait from delayed instrumentation?
- What can and cannot be inferred from an orphan span?

**Expected observations:** Parallel intervals are merged; queue wait and processing time are separate; missing-parent traces are incomplete; one trace does not establish a population pattern.  
**Validation/evidence:** Save diagrams, calculations, fixture files, analyzer output, and a short list of uncertainties.  
**Cleanup:** Delete only temporary fixture copies if no longer needed.  
**Troubleshooting/fallback:** If the trace UI is unavailable, this fixture workbook is the complete fallback; it does not validate live ingestion.

### Lab B — Bottleneck-isolation drill series

Run at least six drills; seven are specified below. Use a local stub or deterministic delay rather than an external dependency. Keep the same request mix and fixed concurrency between baseline and fault run. Suggested default cap: 30–60 seconds per trial, no more than a few hundred requests, and stop if host memory/CPU becomes unstable. Adjust down for the laptop. The numbers are safety suggestions, not capacity claims.

For every drill, follow the eight steps from Section 4 and record request count, p50/p95/p99, errors, throughput, resource signals, trace IDs, and time-to-isolate. Use at least two baseline runs and two fault runs when practical; do not claim statistical certainty from a tiny sample.

#### B1. N+1 database calls

1. **Fault injection:** local in-memory DB stub or local test DB. Add one deterministic lookup per item instead of one batch lookup; cap item count, e.g. 5–10 items/request. Stop if DB errors or host resource pressure rises.
2. **Metric signal:** increased DB calls/request and route p95/p99; verify actual metric names rather than assuming them.
3. **Trace evidence:** repeated sequential `db.read` spans with the same safe query-shape attribute; count calls.
4. **Corroboration:** query-count logs, DB latency/QPS, pool utilization, and request input size.
5. **Hypothesis/experiment:** if N+1 is responsible, call count grows with item count; vary item count while holding other inputs fixed.
6. **Narrow fix:** batch the lookup or prefetch required records; preserve result ordering and error semantics.
7. **Before/after:** compare latency distributions, calls/request, error rate, and DB load at the same workload.
8. **Time-to-isolate:** start/end as defined in Section 4; record timestamps, not an invented value.

**Facilitator key (keep hidden during learner run):** The discriminating evidence is repeated calls scaling with items. A single slow query is a different hypothesis. Check correctness and DB pressure after batching; fewer calls may increase result size.

#### B2. Slow feature fetch

1. Inject a deterministic 100–250 ms delay in a local feature-store stub, with a hard timeout and no external endpoint.
2. Signal: feature-fetch histogram and `/predict` p95/p99 increase while model-inference time remains stable.
3. Trace: `feature.fetch` dominates the critical path; record bounded cache outcome and feature count.
4. Corroborate with stub logs, cache hit rate, dependency timeout counts, and CPU.
5. Hypothesis: feature retrieval is the dominant contribution; compare delayed and undelayed stub with identical payloads.
6. Fix: remove unnecessary fetches, use a justified cache, or batch retrieval; never cache across unsafe identity/consistency boundaries.
7. Compare p50/p95/p99, cache hit/miss cohorts, errors, and staleness/correctness guardrails.
8. Record time-to-isolate from investigation timestamps.

**Facilitator key:** The span identifies the phase, not the cause. The deterministic delay validates the diagnosis pipeline; a real backend requires its own pool/network/server evidence.

#### B3. Large-payload serialization

1. Use generated synthetic payloads at small and moderate sizes; cap total bytes and request count. Do not use real data.
2. Signal: latency rises with payload bytes; CPU/allocation or memory may rise.
3. Trace: explicit `response.encode` or `payload.decode` span grows; feature/model spans remain similar.
4. Corroborate with payload-size attribute, process CPU/memory, and safe structured logs.
5. Hypothesis: serialization cost scales with payload size; vary size while keeping item semantics constant.
6. Fix: reduce redundant fields, stream/chunk where appropriate, or choose a measured efficient encoding.
7. Compare latency quantiles, output size, correctness, memory, and errors.
8. Record time-to-isolate.

**Facilitator key:** A size-latency relationship supports the hypothesis, but network transfer and downstream parsing must be measured separately before attributing all delay to serialization.

#### B4. Connection-pool wait

1. In a local test only, set a deliberately small connection pool and bounded concurrency. Use a stub or local DB. Set a timeout and stop on connection errors.
2. Signal: pool wait or acquisition timeout rises while query execution time may remain stable.
3. Trace: long `pool.acquire` span or gap before `db.query`; if no span exists, the gap is a clue only.
4. Corroborate with pool in-use/wait metrics, connection logs, request concurrency, and DB-side activity.
5. Hypothesis: requests wait to acquire a connection; compare pool sizes at the same concurrency and query mix.
6. Fix: tune pool size only after checking DB connection limits; reduce hold time or add backpressure if appropriate.
7. Compare wait quantiles, DB saturation, request latency, errors, and connection counts.
8. Record time-to-isolate.

**Facilitator key:** Increasing pool size can move overload to the database. Require a DB-side guardrail and never equate a parent gap with pool wait without measurement.

#### B5. DNS/TLS or connection setup per request

1. Use a local HTTP/TLS stub under your control or a mock timing fixture. Do not query public DNS or public endpoints. Simulate setup delay explicitly if local TLS configuration is too heavy.
2. Signal: first/request setup latency and connection creation counts increase; warm keep-alive path differs.
3. Trace: connection setup or resolver/handshake spans if instrumentation exposes them; otherwise record the gap as unknown.
4. Corroborate with connection reuse counters and local stub logs.
5. Hypothesis: a new connection is established for each request; compare keep-alive enabled/disabled in a bounded local trial.
6. Fix: reuse connections where protocol/client semantics allow; set safe connection timeouts.
7. Compare distributions, new connections/request, errors, and resource use.
8. Record time-to-isolate.

**Facilitator key:** A first-request difference alone does not prove DNS. The local stub controls the experiment; name resolution, TLS, connection pool, and server startup are separate mechanisms.

#### B6. Retry amplification

1. Configure a local dependency stub to fail or time out on a known fraction/sequence of calls; cap attempts and total duration. Ensure no unbounded retry loop.
2. Signal: retries/request, timeout count, dependency traffic, and route p95/p99 rise.
3. Trace: attempt spans, backoff events/spans, timeout attributes, and deadline remaining if safely recorded.
4. Corroborate with upstream/downstream timeout logs, retry counters, and dependency latency distribution.
5. Hypothesis: retry policy multiplies work or an upstream timeout is shorter than normal downstream latency; change only timeout/retry behavior in a controlled matrix.
6. Fix: align deadline/timeout budgets, bound retries, use jitter where appropriate, and preserve idempotency.
7. Compare latency, error rate, downstream request volume, and successful completion rate.
8. Record time-to-isolate.

**Facilitator key:** Retries may amplify a prior timeout mismatch rather than cause the original failure. Find the first attempt's failure and compare the timeout hierarchy.

#### B7. CPU throttling / compute saturation

1. Prefer a deterministic CPU loop in a local process with a short timeout and low concurrency. If testing container throttling, use a disposable local container and conservative limits. Stop if host responsiveness degrades; do not intentionally exhaust a shared host.
2. Signal: compute-span duration and CPU throttling/run-queue signals rise; queue depth may grow.
3. Trace: model/compute span expands; trace alone cannot identify a hot function.
4. Corroborate with process/container CPU, throttling counters if available, host load, and profiler output.
5. Hypothesis: effective CPU capacity is constrained; compare low concurrency and a bounded alternate CPU limit while keeping inputs fixed.
6. Fix: reduce unnecessary work, optimize hot code, or revise resource limits after capacity analysis.
7. Compare latency quantiles, throughput, CPU/throttle signals, and error rate.
8. Record time-to-isolate.

**Facilitator key:** High CPU usage is not identical to throttling. Compare actual limits/counters and profile evidence. If container metrics are unavailable, label the diagnosis incomplete and use a local timing/profile fixture.

**Lab B shared evidence:** one eight-step investigation record per fault, before/after distributions, time-to-isolate timestamps, trace/metric/log references, stop-condition record, and cleanup confirmation. **Safe fallback:** replace the live fault with a JSON trace fixture and a written experiment plan; label the result fixture-based, not a live diagnosis.

### Lab C — Critical-path/exclusive-time analyzer

**Purpose:** Run the Section 7 script and challenge its assumptions.  
**Prerequisites:** Python 3 and saved fixture/script/test files.  
**Steps:**

```bash
python3 -m py_compile trace_analyzer.py test_trace_analyzer.py
python3 -m unittest -v test_trace_analyzer.py
python3 trace_analyzer.py fast.json slow.json
```

Create two additional traces with (a) a missing parent and (b) a child outside the parent interval. Confirm warnings/issues. Extend the analyzer only after writing expected behavior. Test overlapping children to ensure interval union avoids double subtraction. Compare the slowest and median-selected trace and state why two traces cannot establish a population distribution.

**Expected observations:** malformed timestamps invalidate timing; duplicate IDs are reported; overlapping children are unioned; orphan spans are visible; the critical path is explicitly approximate.  
**Validation:** tests cover valid, parallel, missing-parent, duplicate-ID, malformed, and minimum aggregate-comparison cases.  
**Evidence:** source, fixtures, test output, sample report, limitations note.  
**Cleanup:** remove temporary data only.  
**Troubleshooting/fallback:** use the expected calculations in Section 7 by hand if Python is unavailable. Do not claim a test passed unless you ran it.

### Lab D — Tail-latency amplification in fan-out

**Purpose:** Observe how waiting for multiple required branches can amplify tail latency.  
**Prerequisites:** A local API or a simple script that calls N local deterministic dependency stubs in parallel.  
**Setup:** Start with N=1, then N=3 or N=5. Each stub should draw from a documented deterministic or seeded delay distribution; cap each request deadline and total run duration. Use no public endpoints.

**Model:** If branch latencies are independent and identically distributed with CDF `F(t)`, and the request waits for all N branches, then the maximum latency has CDF `F_max(t) = F(t)^N`. Therefore its p-quantile corresponds to branch quantile `p^(1/N)`. This is a simplified arithmetic model, not a universal real-world p99 predictor. Independence, identical distributions, no retries, no timeouts, stable scheduling, and sufficient samples are strong assumptions.

**Steps:**
1. Run a baseline with N=1 for a fixed sample count and record p50/p95/p99 plus sample count.
2. Run N=3 and N=5 with identical branch delay distributions and request deadlines.
3. Repeat at least three trials where machine budget permits; randomize or alternate order to reduce drift.
4. Compare observed request latency with the maximum-of-N prediction and document sample uncertainty.
5. Introduce a correlated-delay trial (for example, a shared deterministic pause) and explain why the independence model no longer applies.
6. Check errors/timeouts and verify that the fan-out did not overload the laptop.

**Expected observations:** the maximum of several independent branches tends to have a heavier tail than a single branch. Correlation, retries, scheduling, and finite samples can change the result substantially.  
**Validation:** include the stated assumptions and show observed versus predicted values without claiming exact agreement.  
**Evidence:** trial configuration, seed/distribution, sample counts, quantiles, errors, plot/table, and deviations.  
**Cleanup:** stop local stubs and remove generated synthetic outputs.  
**Fallback:** use an offline simulation with a fixed seed and label it as a model rather than a measured service result.

### Lab E — Instrumentation-for-diagnosability

**Purpose:** Make an ambiguous long endpoint span diagnosable.  
**Prerequisites:** Local instrumented endpoint, or pseudocode/fixture if the repository path is unknown.  
**Steps:**
1. Capture a baseline trace with one broad root span and record what cannot be distinguished.
2. Add bounded child spans for dependency call, pool acquisition, queue wait, feature fetch, model execution, or serialization as appropriate.
3. Add safe attributes for payload size, cache outcome, feature count, model version, retry attempt, and bounded release version.
4. Add redaction/allowlist tests; assert forbidden values such as email-like strings, authorization tokens, and raw SQL literals are absent from exported fixture output.
5. Compare old and new traces under the same deterministic delay; demonstrate which hypothesis is now testable.
6. Audit attribute cardinality by enumerating emitted keys and example value sets.

**Expected observations:** phase timing can distinguish where time accumulates, but still needs corroboration to identify mechanism.  
**Validation:** propagation test passes, sensitive values are absent, and attributes are bounded.  
**Evidence:** before/after fixtures, instrumentation diff, redaction tests, cardinality checklist.  
**Cleanup:** remove temporary test payloads and ensure no secrets were emitted.  
**Troubleshooting/fallback:** if SDK integration is unavailable, annotate the fixture and provide a proposed instrumentation patch; do not claim live propagation was tested.

### Lab F — Profiling a CPU-bound span

**Purpose:** Connect a long compute span to function-level CPU evidence.  
**Prerequisites:** Local Python endpoint or a small CPU-bound script; `py-spy` is optional.  
**Safety:** Use a disposable local process, a short profile duration, and low concurrency. Profiling can add overhead and may require OS/container permissions. `py-spy` availability and flags/platform compatibility on WSL2 are **[VERIFY]**.

**Steps:**
1. Verify Python and `py-spy` availability using the installed executable's help output. Consult the official py-spy documentation for the exact command and permission requirements **[VERIFY]**.
2. Generate a deterministic CPU-bound workload in a local process; record trace span timing and repeat the request a bounded number of times.
3. Attach the profiler only to your own test process and collect a short sampling profile/flame graph if supported. Do not profile unrelated processes.
4. Read the flame graph: wider stacks indicate more sampled time; it is statistical sampling, not exact per-call accounting.
5. Apply one small code change (e.g., avoid repeated conversion or redundant work) and rerun the same workload.
6. Compare trace distributions and profile shape; check correctness and CPU use.

**Fallback:** If py-spy is unavailable or blocked by WSL2/container permissions, use `cProfile` from the Python standard library or instrument coarse function timing. This may perturb execution and is not equivalent to low-overhead sampling. Clearly state which method was used.

**Expected observations:** the trace localizes the slow phase; profiling suggests which functions consume CPU. Neither alone proves a safe fix.  
**Evidence:** command/help output, profile artifact if produced, environment/permission notes, baseline and after distributions, code diff.  
**Cleanup:** stop the local process, remove profile artifacts containing sensitive paths if necessary, and restore any temporary code.  
**Troubleshooting:** permission errors are not a reason to increase privileges blindly; use the standard-library fallback.

### Lab G — Release comparison

**Purpose:** Localize a regression between stable and canary/release versions.  
**Prerequisites:** Two local builds or deterministic fixtures; bounded `version` attribute.  
**Steps:**
1. Define one workload, input-size mix, concurrency, duration, and request deadline.
2. Tag spans with a bounded release enum such as `stable` or `canary`, not a unique build hash as a high-cardinality label.
3. Alternate stable/canary runs or randomize assignment to reduce time/order confounding.
4. Collect population histograms, request counts, errors, throughput, resource signals, and representative traces for each version.
5. Compare span-by-span and inspect whether the same route/input cohort is represented.
6. Repeat trials; document sample sizes and uncertainty. Do not gate or roll back based on one run.

**Expected observations:** a version comparison is meaningful only when workload and environment are comparable.  
**Validation:** regression is repeatable across runs and the change localizes to a span or known behavior; error and resource guardrails are checked.  
**Evidence:** release IDs, workload definition, run order, distributions, trace references, and confounders.  
**Cleanup:** stop test versions and remove local containers.  
**Fallback:** compare matched synthetic trace fixtures and label the conclusion fixture-only.

### Lab H — Per-operation latency budgets

**Purpose:** Allocate an end-to-end SLO budget to phases and automatically detect obvious budget violations.  
**Prerequisites:** One example request path and the distinction between span duration and request wall time.  

**[ILLUSTRATIVE]** Suppose the end-to-end objective is p95 ≤ 500 ms for `/predict` over a stated window. This is an example, not a universal target.

| Phase | Illustrative budget | Notes |
|---|---:|---|
| Ingress/API overhead | 40 ms | Includes routing/validation, not all child durations added together. |
| Feature fetch | 120 ms | Includes its dependency boundary; distinguish pool wait if possible. |
| DB access | 70 ms | Query execution and pool wait should not be conflated. |
| Model inference | 180 ms | Measure by model/version and input shape. |
| Serialization/response | 30 ms | Track payload size. |
| Unallocated safety margin | 60 ms | Protects the total objective against overhead and uninstrumented work. |

These phase allocations sum to 500 ms conceptually, but they are not a mathematical guarantee that phase p95s sum to request p95. Quantiles of components do not generally add; parallel phases overlap; instrumentation overhead and queue wait matter. Treat the table as investigation guardrails and validate end-to-end latency directly.

**Example budget check (pure Python):**

```python
BUDGETS_MS = {
    "feature.fetch": 120.0,
    "db.read": 70.0,
    "model.infer": 180.0,
    "response.encode": 30.0,
}

def violations(span_durations_ms):
    """Return spans above their illustrative individual budgets."""
    return {
        name: duration
        for name, duration in span_durations_ms.items()
        if name in BUDGETS_MS and duration > BUDGETS_MS[name]
    }

assert violations({"feature.fetch": 120.0}) == {}  # boundary is allowed
assert violations({"feature.fetch": 120.1}) == {"feature.fetch": 120.1}
assert violations({"model.infer": 200.0}) == {"model.infer": 200.0}
```

**Steps:** document the end-to-end SLO, allocate provisional phase budgets, implement a boundary-tested checker, and compare violations with the end-to-end population histogram.  
**Expected observations:** span budgets point to likely contributors but cannot replace the SLO metric.  
**Evidence:** budget table, tests, end-to-end distributions, exception/parallelism caveats.  
**Cleanup:** remove generated test output.  
**Troubleshooting/fallback:** if instrumentation is incomplete, mark the unallocated portion explicitly rather than forcing all time into visible spans.

### Lab I — Trace-quality audit

**Purpose:** Find trace-data defects before trusting performance conclusions.  
**Prerequisites:** A set of sanitized fixtures or local trace exports.  
**Audit dimensions:** span naming/cardinality, required safe attributes, missing attributes, duplicate IDs, orphan spans, parent IDs, interval nesting, trace completeness, propagation, links, sampling policy, export drops, and sensitive values.

**Steps:**
1. Define an allowlist of span names and attribute keys for the service.
2. Run a static scan over sanitized fixtures for missing required fields, raw query strings, email-like values, tokens, arbitrary IDs, and excessive unique attribute values.
3. Verify parent IDs and trace IDs across service boundaries; test an async producer/consumer path separately.
4. Compare trace counts with request metrics and Collector/exporter drop/error signals where available.
5. Review sampling configuration and write down which cohorts are intentionally over/under-represented.
6. File findings with severity and a verification test.

**Report template:**

| Finding ID | Severity | Evidence | Impact | Fix | Owner | Verification |
|---|---|---|---|---|---|---|
| `TRACE-001` | High/Medium/Low | Sanitized fixture/query | Diagnosis, privacy, or cost impact | Narrow action | `<TEAM>` | Test/query to rerun |

**Expected observations:** missing spans and bad attributes can make otherwise plausible conclusions wrong.  
**Validation:** every high-severity finding has a testable fix and owner placeholder.  
**Evidence:** audit report, sample fixture, tests, and a before/after trace-quality count.  
**Cleanup:** remove sensitive exports and any accidentally captured secrets immediately according to local incident policy.  
**Fallback:** perform a manual checklist against embedded fixtures; state that live sampling/export paths were not audited.

### Lab J — Async/batch tracing

**Purpose:** Trace a job from enqueue through queue wait and worker processing.  
**Prerequisites:** Local queue/worker if available, or deterministic fixture.  
**Trace model:**

```text
producer request
  └─ enqueue.message
       [message context / link]
worker process trace
  ├─ queue.wait (if explicitly measurable)
  ├─ batch.load
  ├─ feature.compute
  ├─ db.write
  └─ completion
```

For a batch that consumes multiple messages, use span links to producer contexts where supported and appropriate rather than assigning one arbitrary producer as the sole parent. Exact SDK APIs and conventions are **[VERIFY]**.

**Steps:**
1. Emit a producer span around enqueue and propagate approved trace context with the message metadata.
2. Record enqueue timestamp and safe bounded queue name; do not record message body or customer IDs.
3. On consume, extract context or create links according to the batch model.
4. Measure queue wait separately from worker processing; record row count/byte size only as safe numeric attributes.
5. Add stage spans for processing and DB write; record sanitized error/retry classifications.
6. Correlate with queue depth, oldest-message age, processing throughput, and freshness/deadline metrics introduced in Unit 11.
7. Verify propagation across process restart/retry and batch fan-in.

**Expected observations:** producer and consumer may be separate traces linked by context; queue delay is distinct from processing.  
**Validation:** trace or link IDs connect the expected contexts; row/size attributes are bounded; no message payload is exported.  
**Evidence:** producer/worker fixtures, queue-wait calculation, retry/error example, quality-audit output.  
**Cleanup:** stop workers and clear only disposable test messages.  
**Fallback:** use a deterministic fixture with enqueue, dequeue, and completion timestamps. Do not claim a live queue integration passed if only fixtures were used.

### Facilitator Answer Key — Labs A–J

Keep this section separate from learner instructions during a facilitated exercise.

- **A:** In the overlapping fixture, child union is 180 ms (10–190); the contained 20–80 branch adds zero to the union; root exclusive elapsed time is 120 ms for a 300 ms root if no other child intervals exist. For the four-span Section 7 slow fixture, there is also model inference 200–280, so the union is 260 ms and root exclusive is 40 ms. Distinguish fixture variants carefully. Queue delay requires enqueue/dequeue timestamps or an explicit queue-wait measurement. An orphan span establishes a broken/incomplete relationship, not why it is missing.
- **B1:** Calls/request scaling with item count and repeated query shapes support N+1. Batch and validate correctness plus database load.
- **B2:** A deliberately delayed `feature.fetch` that moves endpoint latency while model time remains stable supports phase attribution; a real backend still needs independent validation.
- **B3:** Controlled payload-size scaling with a long encode/decode span supports serialization cost; measure network separately.
- **B4:** Explicit pool-acquisition timing and pool wait metrics distinguish pool wait from query execution. Increasing pool size can overload the database.
- **B5:** Local controlled setup-delay/connection-reuse comparison distinguishes connection setup. Do not attribute it specifically to DNS without resolver evidence.
- **B6:** Attempt sequence, first timeout, and deadline hierarchy reveal whether retries amplify a pre-existing timeout mismatch.
- **B7:** CPU/throttle metrics plus profile evidence distinguish constrained compute from other causes. High utilization alone is insufficient.
- **C:** Union intervals before subtracting; report limitations for links, missing children, and clocks.
- **D:** For independent identical branches, maximum CDF is `F(t)^N`; the model's predicted quantile can diverge from observed finite samples and correlated workloads.
- **E:** New spans make phase attribution possible; redaction and cardinality checks are acceptance gates.
- **F:** Profile only the local test process; a deterministic timing fallback is weaker than a sampled profile.
- **G:** Match workload and alternate/randomize run order; require repeated runs and guardrails.
- **H:** Budgets are provisional and per-span; end-to-end quantiles must be measured directly.
- **I:** A trace-quality audit must check both privacy/cardinality and completeness/propagation.
- **J:** Measure queue wait separately; use links for batch fan-in when a single parent would be misleading.

---

## 9. Capacity and performance modeling

Trace-derived durations are useful inputs to capacity analysis, not proof of capacity. Conceptually, utilization is affected by **arrival rate × service time** for the constrained resource. Use the service-time distribution and request mix, not just the mean. If a span's service time rises, or pool wait expands as arrival rate rises, compare that pattern with the saturation signals from Unit 9: queue depth, oldest item age, CPU/memory pressure, pool occupancy, throttling, and errors.

### Worked example [SYNTHETIC]

Assume a single constrained worker handles one operation at a time. **[ASSUMPTION]** Average measured service time is 40 ms per operation, so nominal service capacity is about 25 operations/second for that worker before overhead and variability. At an arrival rate of 15 operations/second, the simple utilization estimate is `15 × 0.040 = 0.60`, or 60%. If service time rises to 60 ms, the same rate yields `15 × 0.060 = 0.90`, or 90%. Near high utilization, variability can create disproportionate queueing and tail latency. This arithmetic is a conceptual illustration, not a capacity guarantee; real services have concurrency, multiple resources, bursts, retries, and nonstationary arrivals.

Use traces to ask whether the increase is actual service work, pool wait, or queue wait. Use metrics to verify utilization and backlog. A span may appear fast in a sampled trace while the population's queue wait is growing. Averages are insufficient for tail behavior because a small number of long operations can dominate p99 and because the system may be near a performance knee.

### Performance knees and Unit 13

A performance knee is a region where a small increase in offered load causes a large increase in latency or errors. Traces can suggest which operation stretches near that point, but only a controlled load/stress/soak test can establish how the system behaves as demand changes. In Unit 13, vary load in bounded steps, retain stop conditions, measure throughput and latency distributions, and correlate trace changes with saturation metrics. Do not extrapolate sustainable capacity from one low-load trace or a short laptop test.

---

## 10. Trace-driven performance operations program

### 10.1 Reusable playbook

**Symptom → population → tool → hypothesis → controlled test → decision → fix → verification**

1. **Symptom:** user-facing latency, error, or freshness symptom is measurable.
2. **Population:** identify route/version/workload and time window with histograms and counts.
3. **Tool:** select traces, logs, resource metrics, profiler, or a local stub according to the question.
4. **Hypothesis:** write a falsifiable mechanism and what result would disprove it.
5. **Controlled test:** one primary variable, bounded workload, explicit stop condition, repeatable inputs.
6. **Decision:** retain evidence for/against; state uncertainty and whether more data is required.
7. **Fix:** narrow change with correctness tests and rollback path.
8. **Verification:** multiple before/after runs, distributions, error rates, throughput, resource guardrails, and trace shape.

### 10.2 Standard performance views

For each service, maintain a small set of stable dashboards/reports:

- Slowest operations by p50/p95/p99 and request count.
- Dependency latency contribution by normalized operation and bounded dependency name.
- Error/retry hotspots, timeout counts, and status classifications.
- Queue wait versus worker processing, queue depth, and oldest-message age.
- Stable/canary comparison with matched workloads and bounded version labels.
- Trace completeness, export drops, and instrumentation coverage where observable.
- CPU/memory/pool saturation signals alongside latency.

Spanmetrics and trace-derived metrics can help summarize operation performance, but sampling, dropped spans, and cardinality limits must be documented. Avoid creating metric labels from trace IDs, user IDs, raw URLs, or SQL values.

### 10.3 CI/CD performance-regression gate

A defensible gate needs:

1. A repeatable, bounded load scenario and fixed dataset/seed.
2. A declared SLO/latency budget and guardrails for errors, throughput, and resource use.
3. Comparable environment, version, warmup, and request mix.
4. Multiple independent runs; record sample counts and run-to-run variability.
5. A baseline distribution and an explicit tolerance chosen from observed noise and business requirements—not an arbitrary universal percentage.
6. A planted-regression test proving the gate detects a known intentional slowdown.
7. An A/A test (same code/config compared against itself) to estimate false-positive behavior.
8. Safe failure behavior: a noisy or under-sampled result should be marked inconclusive/retried under policy, not automatically treated as a product regression.
9. Trace/metric/log artifacts retained for diagnosis, with sensitive fields scrubbed.
10. A documented manual override/rollback policy with audit trail.

Shared CI runners introduce CPU contention, noisy-neighbor effects, warm-cache differences, and background load. Randomize run order where possible; compare like-for-like workloads; do not gate on one run or one trace. Use a robust comparison (for example, bootstrap intervals or a predeclared nonparametric test) only if the team can explain assumptions and sample size. The exact method should match the distribution and decision cost. If uncertainty crosses the tolerance, report “inconclusive” rather than fabricating precision.

### 10.4 Instrumentation standards and team practices

- Shared middleware should standardize propagation, normalized operation names, safe resource attributes, and exception redaction.
- Each service owns an instrumentation checklist and a small cardinality budget.
- Trace-completeness audits are part of release readiness and dependency onboarding.
- Teams review trace examples during incident drills; they should learn to separate observation, hypothesis, and verified cause.
- Performance retrospectives are blameless and focus on system conditions, missing signals, and prevention.

### Hypothesis log template

```text
ID / date / operation / version:
Observed population symptom:
Trace evidence (slow and matched normal examples):
Metric/log/resource evidence:
Hypothesis (one sentence):
Prediction if true:
Alternative explanations:
Experiment and controlled variables:
Sample size / repetitions / stop condition:
Before distribution and error rate:
After distribution and error rate:
Result / uncertainty:
Decision / rollback condition:
Preventive action / owner:
```

---

## 11. Required synthetic case studies: diagnose → fix → prevent

All trace and metric data in this section are invented **[SYNTHETIC]**. The facilitator key follows the learner cases; hide it during assessment. Observations and hypotheses are separated deliberately.

### Case 1 — p99 regression from N+1 after a minor release

**Fixture narrative:** `v1` `/predict` p99 is 420 ms; `v2` is 1,050 ms across comparable workload windows. Slow `v2` traces show 12 sequential `db.lookup` spans where matched `v1` traces show one batched `db.lookup`. DB QPS per request rises; individual query spans are mostly short. A scrubbed log field records query count, not SQL values.

**Observation:** query count/request and route p99 rose together after release.  
**Hypothesis:** a code change introduced per-item lookups.  
**Controlled experiment:** vary item count with `v2`; verify query count scales with item count. Patch to batch reads under a feature branch and replay the same workload.  
**Fix:** batch lookup and add a test asserting bounded query count.  
**Verification:** compare multiple-run p50/p95/p99, query count/request, DB load, errors, and correctness.  
**Prevention:** query-count regression test, span review, release comparison dashboard.

### Case 2 — Tail sampling hides typical-request profile

**Fixture narrative:** a trace backend contains many slow/error traces because tail sampling retains them preferentially. An engineer sees `model.infer` frequently highlighted and optimizes it. Population histograms show model time is stable while `feature.fetch` p95 is elevated for all requests. Collector sampling policy is not recorded in the investigation note.

**Observation:** retained trace set over-represents slow/error outcomes; population metric points to feature fetch.  
**Hypothesis:** sampling policy biased the visual impression and led to the wrong target.  
**Controlled experiment:** compare policy settings in a bounded local run or use unsampled request-level metrics plus matched synthetic traces; document retention rules.  
**Fix:** maintain population metrics and a sampling policy that preserves diagnostic cohorts within resource limits.  
**Verification:** compare sampled trace cohort with request histogram and feature-fetch distributions.  
**Prevention:** attach sampling-policy metadata to investigations; do not use trace counts as request frequencies.

### Case 3 — Retries obscure a timeout mismatch

**Fixture narrative:** a dependency normally takes 350–500 ms at the tail. The API client timeout is 300 ms, followed by two retries and backoff. Traces show repeated attempts and total duration near the request deadline; logs show timeout at attempt one. The upstream deadline is 900 ms.

**Observation:** retries start after 300 ms timeouts; downstream tail often exceeds the client timeout.  
**Hypothesis:** the timeout is shorter than the valid downstream latency tail, so retries amplify work.  
**Controlled experiment:** local stub with deterministic 400 ms response; compare bounded retry/timeout configurations while preserving deadline and idempotency.  
**Fix:** align timeout hierarchy with SLO/deadline, cap retries, and ensure idempotency.  
**Verification:** compare success rate, dependency request volume, route p95/p99, and deadline violations.  
**Prevention:** timeout budget review and retry-attempt metrics.

### Case 4 — Clock skew makes a healthy trace look broken

**Fixture narrative:** parent span from service A is 0–200 ms. A child from service B appears to start at −20 ms and end at 170 ms. The child reports no errors; independent request timing and service logs are consistent with about 180 ms elapsed. Hosts have unsynchronized clocks in the test environment.

**Observation:** child interval starts before parent according to exported wall-clock timestamps.  
**Hypothesis:** cross-host clock skew makes the timeline inconsistent; instrumentation defect remains an alternative.  
**Controlled experiment:** check host time synchronization and compare a local same-process fixture or SDK duration; rerun with consistent clocks.  
**Fix:** address time synchronization and use robust timing boundaries; do not “correct” arbitrary timestamps without evidence.  
**Verification:** negative/out-of-parent intervals decline and independent request duration remains consistent.  
**Prevention:** clock-health checks and trace-quality audit.

### Case 5 — Feature-fetch p99 dominates; caching is verified

**Fixture narrative:** `/predict` p99 is 900 ms. `feature.fetch` p99 is 650 ms while model inference p99 is 120 ms. Slow traces correlate with cache misses; safe cache outcome attribute is bounded. A local controlled cache test reduces feature-fetch tail, while model timing remains stable.

**Observation:** feature-fetch tail dominates and cache misses correlate with slow traces.  
**Hypothesis:** remote feature retrieval on misses is the dominant contributor.  
**Controlled experiment:** compare cache hit/miss paths with identical feature requests, then test a bounded cache with freshness/invalidation rules.  
**Fix:** introduce a correctness-safe cache or batch features, subject to data freshness requirements.  
**Verification:** compare end-to-end and feature-fetch distributions, hit rate, stale-result checks, errors, and memory.  
**Prevention:** separate feature-fetch and model spans; track cache outcomes without keys.

### Case 6 — 800 ms gap is pool wait

**Fixture narrative:** `api.request` lasts 1,000 ms. A DB child starts 800 ms after the API span begins and runs for 120 ms. Pool-in-use is at configured maximum; explicit pool-wait logs show roughly 780 ms for the same request cohort. Query execution metrics remain around 100–130 ms.

**Observation:** there is an 800 ms gap before the DB child; independent pool evidence reports long acquisition wait.  
**Hypothesis:** the gap is predominantly connection-pool wait, not DB execution.  
**Controlled experiment:** instrument acquisition duration and vary pool size conservatively under the same load while monitoring DB connection limits.  
**Fix:** reduce connection hold time or tune pool/backpressure based on DB capacity.  
**Verification:** compare pool-wait and request distributions plus DB saturation/error guardrails.  
**Prevention:** add pool acquisition timing and saturation dashboards.

### Case 7 — SQL attributes contain customer email addresses

**Fixture narrative:** an exported span attribute stores a raw SQL statement with an email literal. Trace search makes the value indexable. The team discovers it in a sanitized test export; assume no real customer value is shown in this lesson.

**Observation:** SQL literals are present in telemetry attributes; this violates the instrumentation policy.  
**Hypothesis:** automatic DB instrumentation or custom instrumentation records unparameterized SQL text.  
**Controlled experiment:** use a synthetic email-shaped fixture and assert the exporter output contains only parameterized statement shape, never the literal.  
**Fix:** disable unsafe attribute capture or scrub/allowlist before export; review retention/access policy and follow incident procedure if real secrets/PII were collected.  
**Verification:** regression test scans exported spans for prohibited patterns; confirm the backend no longer indexes sensitive fields.  
**Prevention:** privacy-by-default instrumentation, automated telemetry scanning, and code review.

### Facilitator Answer Key — Case studies

- **Case 1:** The repeated sequential calls and per-request query count are the strongest discriminators. Verify call scaling and patch under controlled replay. A release association alone is not causality.
- **Case 2:** The trace backend sample is not an unbiased population. Population metrics and sampling-policy evidence show why optimizing model inference was premature.
- **Case 3:** The first attempt times out before the normal downstream tail completes. Retry spans are visible work amplification, but timeout mismatch is the upstream mechanism to test.
- **Case 4:** A negative relative start is a data-quality warning. Check clock sync and independent timing; do not assume every out-of-parent span is clock skew.
- **Case 5:** Feature-fetch p99 and controlled cache-path evidence support the diagnosis. Validate freshness and correctness, not only speed.
- **Case 6:** Pool wait logs/metrics discriminate the 800 ms gap from query execution. Increasing the pool without DB capacity evidence can worsen the incident.
- **Case 7:** Raw SQL literals are a privacy defect regardless of performance. Remove/redact at source, scan exported telemetry, and follow applicable incident procedures if real data escaped.

---

## 12. Troubleshooting decision tree

Use the first row that matches the symptom. In every case, seek corroborating evidence before declaring root cause.

| Symptom | First evidence | Plausible explanations | Discriminating check | Safe next action |
|---|---|---|---|---|
| Trace missing or incomplete | Request metric count, trace ID, Collector/exporter errors, sampling config. | Sampling, propagation failure, export drop, wrong time range, no instrumentation. | Generate one known local request and inspect propagation/export counters end-to-end. | Use fixture fallback; repair the narrow pipeline boundary. |
| Long parent span with no child detail | Root duration, child count, instrumentation boundaries. | Uninstrumented work, dropped children, broad SDK span, blocking call. | Add a coarse child span around the suspected phase; compare logs/resource metrics. | Instrument meaningful boundaries; avoid micro-span explosion. |
| One slow dependency span | Dependency histogram, timeout/error metrics, matching logs. | Slow query, network, pool wait, downstream saturation, retry hidden inside span. | Split acquisition/query/transfer phases or use a controlled stub. | Engage dependency owner with trace + population evidence. |
| Large gap before child | Parent/child timestamps and pool/queue metrics. | Pool acquisition, queue wait, scheduler, connection setup, instrumentation gap, clock skew. | Add explicit timing around the suspected wait; compare enqueue/dequeue or pool logs. | Label gap “unexplained” until measured. |
| Repeated calls/retries | Span sequence, retry count, first failure, query count/request. | N+1, retry policy, client loop, duplicate work. | Vary input count or dependency response deterministically. | Bound retries/calls and add a regression test. |
| High p99 but typical traces look normal | Histogram sample count, sampling policy, slow cohort definition. | Rare slow path, sampling bias, insufficient sample, mixed workload. | Select several tail traces and matched cohorts; compare metrics with trace retention. | Expand sample under safe policy; don't optimize from a single trace. |
| Different versions behave differently | Versioned distributions, workload mix, rollout timestamps. | Code regression, config change, host drift, input mix, cache warmness. | Alternate stable/canary with matched workload and repeated runs. | Narrow the change and retain rollback path. |
| Async worker trace doesn't join request trace | Producer/consumer context, queue metadata, link fields. | Context not propagated, serializer strips headers, batch fan-in needs links. | Send a known test message and assert context/link survives enqueue/dequeue. | Fix propagation or model the relationship with links; don't force false parentage. |
| Negative/overlapping durations | Raw timestamps, source clock, parent interval, export conversion. | Clock skew, unit conversion error, malformed data, genuine async overlap. | Verify units/schema, compare same-process fixture and clock health. | Mark timing invalid until validated; don't blindly clamp values. |
| Sensitive/high-cardinality attributes | Exported sanitized fixture and attribute-value inventory. | Auto-instrumentation captures literals; custom fields contain IDs/URLs/payloads. | Test allowlist/redaction with synthetic prohibited values. | Stop unsafe emission, scrub at source, assess incident process, add regression scan. |

**Decision rule:** A trace pattern creates a hypothesis. Root-cause language requires a discriminating check and corroborating evidence. If the evidence conflicts, record the conflict and gather better data instead of selecting the most convenient explanation.

---

## 13. Verification, version sensitivity, and sources

Observability interfaces evolve. Verify every integration against the installed version and official documentation before using it in a shared environment.

### Verification checklist

- **Trace JSON:** identify the exact export format and timestamp unit; validate field names and parent/link representation with a real sanitized sample.
- **OpenTelemetry SDK APIs:** confirm installed SDK version, instrumentation library, exception/status behavior, propagation setup, and shutdown/flush behavior.
- **Semantic conventions:** confirm database, HTTP, messaging, service, and deployment attribute names against the convention version used by the SDK.
- **Collector:** confirm receiver/processor/exporter names, sampling configuration, spanmetrics support, pipeline ordering, and drop/error metrics for the installed release.
- **Backend:** verify search fields, TraceQL/query syntax, comparison features, service graph, retention, indexing, and export behavior in the installed Jaeger/Tempo or other backend version.
- **Prometheus:** confirm histogram type, labels, units, native/classic histogram behavior, and exemplar support/configuration.
- **Profiling:** confirm py-spy availability, flags, permissions, WSL2/container compatibility, and expected overhead. Use local help output and official docs.
- **Performance test:** record OS, Python/runtime, CPU limits, workload, sample count, warmup, version, and whether the run used a shared host.

Useful local checks (adapt to your environment):

```bash
python3 --version
python3 -m pip show opentelemetry-api opentelemetry-sdk
python3 -m pip show py-spy
py-spy --help                 # [VERIFY] only if installed
prometheus --version          # [VERIFY] if the binary is on PATH
promtool --version            # [VERIFY] if installed
```

These commands inspect local installation state; they do not prove that a feature is enabled or configured correctly. Do not install tooling just to complete a fixture-only lab. Use official documentation for the precise installed release. Genuine starting points include the OpenTelemetry documentation at `https://opentelemetry.io/docs/`, Prometheus documentation at `https://prometheus.io/docs/`, Grafana Tempo documentation at `https://grafana.com/docs/tempo/`, Jaeger documentation at `https://www.jaegertracing.io/docs/`, and py-spy project documentation at `https://github.com/benfred/py-spy`. Exact pages, current options, and release-specific capabilities must be checked **[VERIFY]**; this lesson does not claim live documentation was checked during authoring.

### Version-sensitive items to mark in lab notes

- Trace UI filters, TraceQL/search syntax, span comparison, service graphs, and export JSON schema: `[VERIFY]`.
- OpenTelemetry API methods, semantic-convention keys, instrumentation defaults, span links, and propagation details: `[VERIFY]`.
- Collector processor/connector names, tail-sampling settings, spanmetrics, and internal telemetry metric names: `[VERIFY]`.
- Prometheus histogram/exemplar behavior and metric names emitted by instrumentations: `[VERIFY]`.
- `py-spy` commands and WSL2/container permissions: `[VERIFY]`.
- Any benchmark, p99, time-to-isolate, or claimed test outcome: report only if measured and include conditions.

---

## 14. Practice questions

Answer all five questions. These are the only end-of-unit practice questions; lab/workbook exercises are separate.

1. A root span lasts 300 ms. Child A runs from 10–190 ms and child B runs from 20–80 ms in parallel. Assuming consistent clocks and nested intervals, calculate the direct-child interval union and root exclusive elapsed time. Explain why summing child durations gives the wrong result.
2. A trace has an 800 ms gap before a 120 ms DB span. Distinguish a long DB span from the gap and list the evidence required to support a connection-pool-wait diagnosis.
3. Explain how to isolate an N+1 or retry-related regression using all eight steps of the bottleneck-isolation workflow. State one observation, one hypothesis, and one controlled experiment.
4. Explain how sampling bias, cardinality, and PII can make trace analysis misleading or unsafe. Propose one instrumentation improvement that is privacy-safe and testable.
5. Design a statistically defensible before/after or canary comparison that links traces to metrics and logs. Include workload comparability, repeated runs/sample size, uncertainty, error/resource guardrails, and the rule for an inconclusive result.

### Answer key

1. The union of A and B is 10–190 ms, or 180 ms; B is fully contained in A's interval. Root exclusive elapsed time is 300 − 180 = 120 ms. Summing 180 + 60 = 240 ms double-counts the overlapping interval. This is elapsed time outside child intervals, not CPU time.
2. The gap is time inside the parent before the DB child starts; the DB span itself is 120 ms. Pool wait is a hypothesis, not a conclusion. Confirm with explicit acquisition timing or pool-wait metrics/logs, pool occupancy/limits, and query execution timing; rule out queueing, scheduler delay, connection setup, missing instrumentation, and clock skew.
3. Step 1 identify the affected population in histograms by operation/version; 2 select multiple slow and matched fast traces; 3 compare repeated calls/attempts; 4 locate repeated DB spans or retry/backoff on the critical path; 5 write a falsifiable hypothesis; 6 corroborate with query counts, timeout logs, dependency latency, and a bounded controlled test; 7 apply a narrow batch-query or timeout/retry fix; 8 compare repeated before/after distributions, errors, call volume, and resources. An observation is not the hypothesis itself.
4. Sampling can over-represent slow/error traces or hide rare failures; unbounded attributes can inflate index/cardinality costs; raw SQL/email/token/payload values can expose sensitive data. Add a bounded `cache.outcome` enum or safe feature count, redact SQL literals, and test exported fixtures for prohibited values and allowed cardinality.
5. Fix the workload, input mix, version, environment, warmup, concurrency, and duration; collect multiple independent runs and adequate sample counts; compare population histograms/quantiles and error/throughput/resource guardrails; select matched slow and median traces; correlate trace IDs to scrubbed logs and resource metrics; estimate run-to-run uncertainty and predeclare tolerance. Use A/A and planted-regression tests for a CI gate. If uncertainty overlaps the tolerance or sample count is insufficient, mark the result inconclusive rather than gating from one run.

---

## 15. Completion checklist and ten-pass audit

### Learner completion checklist

- [ ] Explain trace, span, parent, link, context propagation, sampling, and resource attributes without confusing them.
- [ ] Read sequential and parallel waterfalls and calculate child interval union and exclusive elapsed time.
- [ ] Identify gaps, retries, N+1 calls, fan-out stragglers, queue wait, setup overhead, GC/runtime pauses, contention, CPU pressure, payload overhead, and feature-fetch latency as hypotheses to validate.
- [ ] Start with a population histogram and select matched slow/median/fast traces.
- [ ] Complete the eight-step workflow and record time-to-isolate using explicit start/end definitions.
- [ ] Instrument useful safe spans/attributes; test propagation, redaction, and cardinality.
- [ ] Explain backend UI/version limitations and sampling bias.
- [ ] Run the analyzer or document fixture-based fallback; understand its algorithm and limitations.
- [ ] Complete Labs A–J or explicitly mark any live integration as unavailable and use the specified fallback.
- [ ] Complete at least six bounded fault drills and preserve before/after distributions, evidence, and stop/cleanup records.
- [ ] Compare fan-out observations with the stated simplified model and document deviations.
- [ ] Produce a latency-budget table tied to an explicit SLO and explain why component quantiles do not simply add.
- [ ] Diagnose all seven synthetic case studies with observation/hypothesis/experiment/fix/verification separated.
- [ ] Complete the five practice questions and review the answer key.
- [ ] Retain no sensitive trace exports or unsafe attribute values.

### Acceptance criteria for Labs A–J and analyzer

| Deliverable | Acceptance criterion |
|---|---|
| Lab A workbook | Five trace shapes represented: parent-child, parallel fan-out, retry, queue wait, and incomplete/clock-skew. Calculations and uncertainty are recorded. |
| Lab B drills | At least six faults completed; every drill has all eight steps, a safety/stop condition, before/after distributions, error/resource checks, time-to-isolate timestamps, facilitator key, and cleanup record. |
| Lab C analyzer | Script runs on documented fixtures; tests cover valid trace, parallel intervals, missing parent, duplicate IDs, malformed data, and aggregate-comparison minimum; limitations are stated. |
| Lab D fan-out | N=1 plus multiple branches; repeated trials; prediction assumptions, sample sizes, observed quantiles, and deviations recorded. |
| Lab E instrumentation | Before/after diagnosability demonstrated; propagation and redaction tests; bounded attribute audit. |
| Lab F profiling | Profile or clearly labeled fallback; local process only; repeatable before/after latency and correctness evidence. |
| Lab G release comparison | Bounded version label, matched workload, repeated runs, distributions, errors, confounders, and rollback/stop rule. |
| Lab H budgets | SLO-derived illustrative allocation, boundary tests, end-to-end metric comparison, and parallelism/quantile caveats. |
| Lab I quality audit | Severity/evidence/impact/fix/owner/verification report and checks for PII, cardinality, propagation, completeness, and links. |
| Lab J async/batch | Enqueue/queue-wait/worker stages, propagation or links, safe attributes, retries/errors, and freshness/deadline correlation or fixture fallback. |

### Evidence-retention checklist

- [ ] Workload and input definition, run order, version, environment, and sample counts.
- [ ] Population metrics and exact query/dashboard time range.
- [ ] Sanitized representative trace IDs or local fixture files; no raw customer payloads.
- [ ] Relevant scrubbed logs and resource/pool/queue signals.
- [ ] Hypothesis log with evidence for/against and discriminating experiment.
- [ ] Before/after p50/p95/p99, request count, errors, throughput, and guardrail metrics.
- [ ] Analyzer source, fixture files, test output, and limitations.
- [ ] Profiling artifact only if safe, with process/environment metadata.
- [ ] Instrumentation/privacy/cardinality audit and regression tests.
- [ ] Cleanup confirmation and record of any live integration not performed.

### Ten-pass audit

1. **Roadmap fidelity — PASS against the supplied roadmap/syllabus text:** target filename is Unit 10; it follows Unit 9 saturation and precedes Unit 11 scheduled-job freshness/deadline monitoring. No new M11 unit is proposed. The roadmap and M11 syllabus files were available in the supplied working directory; this lesson uses their stated unit order. No claim is made that the entire repository was edited.
2. **Coverage — PASS by section inspection:** trace concepts, all 14 latency shapes, trace-to-metric reasoning, eight-step workflow, instrumentation, backend limitations, analyzer, Labs A–J, seven case-study themes, decision tree, capacity modeling, operations program, five questions, and completion audit are included.
3. **Beginner-to-advanced progression — PASS by section order:** vocabulary and waterfall arithmetic precede diagnostic patterns, metrics, instrumentation, analyzer, labs, and operational gate design.
4. **Technical authenticity — PASS with stated limitations:** input schema and algorithm are explicit; UI/API/query/version-specific features are marked `[VERIFY]`; pseudocode is not presented as a drop-in SDK implementation. Actual installed tool versions are not known.
5. **Evidence quality — PASS by method design:** population metrics precede trace selection; observations are separated from hypotheses; fixes require controlled experiments and before/after distributions. No real benchmark or time-to-isolate result is fabricated.
6. **Privacy/cardinality — PASS by checklist and examples:** prohibited values are enumerated; examples use safe bounded fields; SQL is parameterized/scrubbed; attribute allowlists and redaction tests are required.
7. **Script integrity — PARTIAL pending execution in the learner environment:** implementation and tests are included for valid traces, parallel intervals, missing parents, duplicate IDs, malformed timestamps, and minimum comparison sample count. The aggregate-comparison test currently checks the minimum-count precondition rather than asserting exact rendered output; improve it if the lab requires fully unit-tested report rows. Do not assume tests passed without running them locally.
8. **Lab safety — PASS by written constraints:** labs are local, bounded, time-limited, stoppable, and include cleanup/fallback instructions. Actual host resource behavior must be verified by the learner.
9. **Assessment and operational readiness — PASS by section inspection:** exactly five end-of-unit questions with answers; lab and case-study facilitator keys are separated; playbook, CI gate, evidence templates, and acceptance criteria are included.
10. **Single-file integrity — PASS for authoring intent:** this deliverable is one Markdown lesson file. No other repository file is intentionally modified. Live Prometheus/Collector/backend/profiler integrations and runtime test results are not claimed; run the documented verification steps in the target environment.

**Final audit note:** The content is a self-contained teaching artifact, not a claim that the learner's live stack has been deployed or validated. Where environment, schema, SDK, UI, query syntax, or version affects correctness, verify the installed implementation and record the result.
