# Practice Questions

## How to Use This Practice Set

This workbook is designed to move from concept application to production-level engineering judgment. For each problem, stop after **Problem** and work it yourself before reading **How to Solve the Problem** and **Solution**.

Every exercise follows the same sequence:

1. **Problem** — the engineering situation you must solve.
2. **How to Solve the Problem** — a reasoning path that guides the investigation without giving away the final answer.
3. **Solution** — a complete production-oriented solution.
4. **Key Concepts Tested** — the Module 2.20 concepts exercised.
5. **Why This Solution Works** — the engineering rationale.

## Difficulty Levels

| Level | Questions | Focus |
|---|---:|---|
| Basic | 01–10 | Foundational application of individual concepts and closely related signals |
| Moderate | 11–20 | Multi-concept pipeline reasoning and engineering decisions |
| Hard | 21–30 | Production debugging, failure investigation, security, governance, and reliability trade-offs |
| Advanced | 31–40 | Senior-level architecture, cross-system incidents, governance, security, privacy, and operational judgment |

## Coverage Summary

The set collectively covers pipeline metrics/run metadata, OpenTelemetry tracing, alerting/on-call, OpenLineage, catalogs/metadata, PII protection, encryption, access control, retention/deletion, and incident response. Hard and Advanced problems intentionally combine multiple module topics.

# Part I — Basic

## Question 01 — Choose the right signal for pipeline health

**Difficulty:** Basic

### Problem

An API-to-warehouse batch pipeline completes successfully every run. The team wants to monitor whether each run processed the expected workload without creating a high-cardinality metric. Design the minimum useful metric/run-metadata combination and explain which signal belongs in Prometheus versus per-run metadata.

### How to Solve the Problem

1. Separate aggregate time-series signals from per-run facts.
2. Identify workload and outcome signals that remain low-cardinality.
3. Use run_id for detailed correlation rather than turning it into a metric label.
4. Explain how the resulting signals support a dashboard and investigation.

### Solution

Use a small set of pipeline metrics such as run success/failure, run duration, rows processed, bytes processed, and freshness where applicable. Put stable dimensions such as pipeline name and environment in metric labels, but do not use run_id, customer ID, request ID, or other unbounded identifiers as metric labels.

Store run_id, start/end timestamps, status, row/byte counts, retry count, Git SHA, image digest, and other run-specific facts in unified run metadata. Prometheus is appropriate for aggregated time-series trends and alerting; run metadata is the detailed record used to investigate one execution. Structured JSON logs can carry the same run_id for correlation.

### Key Concepts Tested

- metrics
- run metadata
- run IDs
- metric cardinality
- structured logging

### Why This Solution Works

This works because metrics answer 'is the system behaving normally over time?' while run metadata answers 'what happened in this particular execution?' Keeping high-cardinality identifiers out of metric labels protects the observability system from uncontrolled series growth.

## Question 02 — Select the correct metric type

**Difficulty:** Basic

### Problem

A pipeline exposes three measurements: total records successfully processed since process start, current Kafka consumer lag, and distribution of pipeline run durations. Choose an appropriate Prometheus metric type for each and justify the choices.

### How to Solve the Problem

1. Ask whether each value monotonically accumulates, represents current state, or describes a distribution.
2. Map those semantics to counter, gauge, or histogram.
3. Consider whether the measurement will be aggregated and queried for latency percentiles.

### Solution

Use a counter for total records successfully processed because the value monotonically increases and can be queried with a rate over time. Use a gauge for current consumer lag because lag can rise and fall. Use a histogram for run duration because it records observations into buckets and supports latency distributions and percentile-oriented analysis.

A summary can also represent observed distributions, but histograms are generally preferable when aggregation across instances or workers is important.

### Key Concepts Tested

- counters
- gauges
- histograms
- summaries
- Prometheus

### Why This Solution Works

The metric type should match the semantic behavior of the value. Choosing by name rather than behavior produces misleading queries and alerts.

## Question 03 — Diagnose a freshness violation

**Difficulty:** Basic

### Problem

A pipeline's average runtime is normal, but downstream consumers report that the table is stale. Which observability signals should you inspect first to distinguish processing latency from queueing, upstream delay, or delayed publication?

### How to Solve the Problem

1. Define freshness as the consumer-facing timeliness objective.
2. Break elapsed freshness delay into upstream availability, queue time, processing time, and publication delay.
3. Inspect run metadata and pipeline metrics for each component.
4. Correlate a specific affected run using run_id.

### Solution

Start with freshness metrics and the latest successful run's run metadata. Compare the source event/data availability timestamp with pipeline start time to identify upstream delay or queue time. Compare start and end timestamps for processing duration. Then inspect the publication/availability timestamp of the target dataset to determine downstream publication delay.

Use run_id to correlate structured logs and execution details. If traces exist, use the trace to locate the slow stage. This avoids concluding that processing is the problem merely because the consumer sees stale data.

### Key Concepts Tested

- freshness
- queue time
- run duration
- run metadata
- run IDs

### Why This Solution Works

Freshness is an end-to-end property. A normal processing duration does not prove that the data became available on time.

## Question 04 — Correlate one failed run

**Difficulty:** Basic

### Problem

A pipeline failed after three retries. An engineer has the run_id and needs to reconstruct what happened. Identify the telemetry and metadata that should be correlated and the order in which you would inspect them.

### How to Solve the Problem

1. Start with the run-level record.
2. Use run_id to locate structured logs.
3. Use the associated trace_id when tracing is available.
4. Inspect retry history, failure status, timing, and deployment identity.

### Solution

Start with unified run metadata for status, timestamps, retry count, pipeline version, Git SHA, and image digest. Use the run_id in structured JSON logs to reconstruct the chronological sequence. If the run carries a trace_id, open the corresponding distributed trace and inspect failed/error spans and their attributes/events. Compare the failing run with the last known successful run and its deployment identity.

The investigation should preserve the exact run identity rather than relying on aggregate metrics alone.

### Key Concepts Tested

- run IDs
- structured JSON logging
- traces
- trace IDs
- retry metadata

### Why This Solution Works

A single run is best reconstructed by moving from stable run metadata to correlated logs and traces. The correlation identifiers provide a consistent investigative path across telemetry types.

## Question 05 — Build an actionable freshness alert

**Difficulty:** Basic

### Problem

A team currently has a dashboard showing table freshness but no alert. The dataset has a freshness SLO. Explain what must be defined before turning the dashboard signal into an actionable alert.

### How to Solve the Problem

1. Identify the SLI and SLO.
2. Define the violation threshold and evaluation window.
3. Decide severity and ownership.
4. Attach a runbook and route the alert to the correct on-call path.
5. Avoid firing on transient noise without an operational response.

### Solution

Define freshness as an SLI, specify the target SLO and the evaluation window, and determine when the observed freshness crosses the actionable threshold. Configure an alert with meaningful severity and routing. The alert should identify the affected dataset/pipeline without using unbounded labels.

Attach a runbook that explains how to inspect freshness, run metadata, logs, traces, upstream availability, and downstream publication. If an error-budget or burn-rate policy is used, incorporate it into the alert strategy rather than alerting on every small fluctuation.

### Key Concepts Tested

- freshness alerts
- SLIs
- SLOs
- runbooks
- alert routing

### Why This Solution Works

A dashboard is descriptive; an actionable alert represents a condition requiring human action. The SLO provides the operational definition of unacceptable behavior.

## Question 06 — Trace a pipeline stage

**Difficulty:** Basic

### Problem

A pipeline consists of an HTTP extraction call, database read, transformation, and warehouse write. Explain how traces and spans should represent this execution and what information should be placed in span attributes versus events.

### How to Solve the Problem

1. Create one trace for the end-to-end operation.
2. Represent meaningful operations as spans.
3. Use attributes for stable searchable context.
4. Use events for notable point-in-time occurrences such as exceptions.
5. Record status/errors without putting sensitive data into telemetry.

### Solution

Create an end-to-end trace with spans for the HTTP call, database operation, transformation stage, and warehouse write. Give spans useful attributes such as service/component, operation, dataset or pipeline identifiers where appropriate, and relevant non-sensitive status information. Record exceptions as span events and set span status appropriately.

Do not create one span per record. Avoid placing raw PII, secrets, or full payloads in attributes/events. Use the trace ID to connect the execution with logs and metrics.

### Key Concepts Tested

- traces
- spans
- attributes
- events
- telemetry security

### Why This Solution Works

Spans represent meaningful units of work and provide timing context. Attributes support analysis, while events capture discrete occurrences. Keeping telemetry bounded and sanitized preserves both performance and security.

## Question 07 — Protect trace context across Kafka

**Difficulty:** Basic

### Problem

An HTTP request starts a pipeline and publishes a Kafka message. A downstream consumer creates a processing span, but the resulting trace appears disconnected. What mechanism should be checked, and what should the producer and consumer carry?

### How to Solve the Problem

1. Identify distributed context propagation as the likely boundary problem.
2. Check W3C Trace Context handling at the HTTP boundary.
3. Propagate trace context through Kafka headers.
4. Verify the consumer extracts the context before starting its child span.

### Solution

Check that the producer injects the current OpenTelemetry context into Kafka message headers and that the consumer extracts it before creating the processing span. W3C Trace Context provides the propagation model used across service boundaries. The consumer should create a child span or correctly linked continuation from the extracted context.

Do not put the trace context into message payload business fields merely to make tracing work; Kafka headers are the appropriate propagation mechanism.

### Key Concepts Tested

- context propagation
- W3C Trace Context
- Kafka headers
- OpenTelemetry

### Why This Solution Works

Distributed tracing only becomes distributed when execution context crosses service and messaging boundaries. Kafka headers preserve the trace relationship without coupling tracing data to business payload schemas.

## Question 08 — Make an alert useful to an on-call engineer

**Difficulty:** Basic

### Problem

An alert says 'Pipeline unhealthy' and fires for multiple unrelated conditions. List the information and operational linkage that should be added so an on-call engineer can act on it.

### How to Solve the Problem

1. Identify the symptom precisely.
2. Include enough stable context to locate the affected pipeline/dataset.
3. Assign severity and routing.
4. Link the runbook and relevant dashboard.
5. Ensure deduplication/grouping does not hide distinct incidents.

### Solution

The alert should identify the pipeline or dataset, the concrete symptom such as freshness, failure rate, lag, or quality violation, severity, and the relevant time window. It should route to the correct on-call team and link to a runbook and dashboard. Alertmanager grouping/deduplication should prevent repeated pages for the same underlying incident while preserving distinct failures.

The runbook should tell the responder what to inspect first and how to contain or escalate the issue.

### Key Concepts Tested

- actionable alerts
- severity
- routing
- runbooks
- Alertmanager

### Why This Solution Works

An alert is useful only when it reduces time to diagnosis and provides a clear next action. Vague alerts increase alert fatigue without improving reliability.

## Question 09 — Choose an access-control model

**Difficulty:** Basic

### Problem

A data platform has analysts, data engineers, and service identities. Analysts need read access to approved datasets, engineers need broader operational access, and services need only the permissions required for their pipeline. Which authorization concepts should form the baseline design?

### How to Solve the Problem

1. Separate authentication from authorization.
2. Identify human and machine identities.
3. Apply least privilege.
4. Use roles/groups for repeatable permissions.
5. Add row/column restrictions for sensitive data rather than granting unrestricted table access.

### Solution

Use authenticated users, groups, roles, and service identities as distinct principals. Apply least privilege so each principal receives only the permissions required for its work. RBAC is a suitable baseline for repeatable role-based permissions; ABAC or tag-based policies can complement it where access depends on attributes such as data classification.

Sensitive datasets should additionally use column-level controls, masking, or row-level security where required. Machine identities should not reuse broad human credentials.

### Key Concepts Tested

- authentication vs authorization
- least privilege
- RBAC
- service identities
- column-level security

### Why This Solution Works

Authorization is about what an authenticated principal is allowed to do. Separating roles and service identities reduces accidental privilege expansion and improves auditability.

## Question 10 — Design a safe retention record

**Difficulty:** Basic

### Problem

A dataset contains customer activity data. Before automating deletion, what metadata should its retention policy capture, and why is a retention period alone insufficient?

### How to Solve the Problem

1. Identify the purpose of the dataset.
2. Define the retention period and its starting point.
3. Define the end action.
4. Identify legal holds and relevant copies/storage layers.
5. Make the policy auditable and executable.

### Solution

The retention metadata should identify the dataset, purpose, owner or steward where applicable, retention period, the event from which retention is measured, and the end action such as deletion or archival. It should also account for legal holds, storage-specific retention behavior, and downstream copies that are governed by the same policy.

A period alone is insufficient because the system must know why the data exists, when the clock starts, what should happen at expiry, and whether deletion is temporarily blocked by a legal hold.

### Key Concepts Tested

- retention policy
- data purpose
- retention metadata
- legal holds
- data lifecycle

### Why This Solution Works

A retention rule must be executable and auditable. The period is only one component of the lifecycle decision.

# Part II — Moderate

## Question 11 — Unify metrics, metadata, logs, and traces

**Difficulty:** Moderate

### Problem

A nightly pipeline's duration increased by 40%, but CPU utilization is normal. Design an investigation path that uses pipeline metrics, run metadata, structured logs, and OpenTelemetry traces to determine whether the regression is queueing, I/O, an external dependency, or a code path.

### How to Solve the Problem

1. Compare current and historical run-duration distributions.
2. Inspect run metadata for timing breakdowns, retries, Git SHA, and image digest.
3. Correlate the affected run_id with structured logs.
4. Follow trace spans to the slow operation.
5. Compare the finding with the deployment identity and external dependency behavior.

### Solution

Start with run-duration histograms and recent run metadata. Determine whether the increase is isolated to a deployment, dataset, partition, or all executions. Inspect queue/start delay, processing duration, retry count, Git SHA, and image digest.

Use run_id to find structured JSON logs and identify the stage where time accumulated. If the run has a trace_id, inspect the trace for long HTTP, database, transformation, or warehouse spans. If an external call dominates the span, inspect its timing and status. If the transformation span dominates and the Git SHA changed, compare the code path.

The remediation depends on the diagnosed boundary: reduce queueing, address dependency latency, or revert/fix the code. Add a regression signal or alert only after identifying a meaningful SLI.

### Key Concepts Tested

- metrics
- run metadata
- structured logs
- OpenTelemetry traces
- Git SHA
- image digest

### Why This Solution Works

No single telemetry signal proves the cause. The correlation chain from aggregate metric to run, logs, and trace lets the engineer move from symptom to causal stage.

## Question 12 — Design a low-cardinality pipeline dashboard

**Difficulty:** Moderate

### Problem

Design a dashboard for ten production pipelines that must show reliability, freshness, throughput, retries, and cost without creating an unmanageable metric-cardinality problem. Specify useful dimensions and explain what belongs outside metrics.

### How to Solve the Problem

1. List the questions the dashboard must answer.
2. Map each question to a low-cardinality metric.
3. Choose bounded labels such as pipeline and environment.
4. Keep run-specific and high-cardinality information in metadata/logs.
5. Make the dashboard support drill-down into individual runs.

### Solution

Use metrics for run success/failure, duration distributions, processed rows/bytes, retry rates, freshness, lag where applicable, and cost-related aggregates. Labels can include bounded dimensions such as pipeline, environment, service, or bounded status categories.

Do not label metrics with run_id, request ID, customer ID, arbitrary error strings, or other unbounded values. Store those details in run metadata and structured logs. The dashboard should link to the run-level investigation path using a selected pipeline/time window rather than requiring every run identifier to become a metric series.

### Key Concepts Tested

- metric cardinality
- labels
- dashboards
- run metadata
- pipeline metrics

### Why This Solution Works

The dashboard remains useful when its metrics are stable and aggregatable. Detailed context belongs in systems designed for event/run-level records rather than the metric label space.

## Question 13 — Use SLOs and burn rate to prioritize alerts

**Difficulty:** Moderate

### Problem

A data product has a freshness SLO, but engineers receive pages for every short freshness delay. Explain how SLI, SLO, error budget, and burn-rate reasoning can replace noisy threshold alerts.

### How to Solve the Problem

1. Define the freshness SLI precisely.
2. Establish the SLO target and evaluation window.
3. Interpret violations as error-budget consumption.
4. Use burn rate to detect sustained or severe budget consumption.
5. Route alerts according to operational severity.

### Solution

Define an SLI such as the proportion of eligible data updates delivered within the freshness objective. Set an SLO for the required proportion over an agreed window. Freshness violations consume the error budget. Instead of paging on every isolated delay, use burn-rate conditions that detect rapid or sustained budget consumption.

Use higher-severity alerts for rapid budget burn and lower-severity notifications for slower degradation. Attach runbooks and ensure the alert identifies the affected data product and owner.

### Key Concepts Tested

- SLI
- SLO
- error budget
- burn rate
- alert fatigue

### Why This Solution Works

SLO-based alerting aligns paging with reliability impact rather than arbitrary instantaneous thresholds. Burn rate helps distinguish a small blip from a condition that threatens the reliability objective.

## Question 14 — Investigate a lineage-backed data-quality failure

**Difficulty:** Moderate

### Problem

A warehouse table contains incorrect values after a successful pipeline run. OpenLineage shows the table was produced by a Spark job from two upstream datasets. Explain how you would use runtime lineage, run information, and data-quality signals to scope the investigation.

### How to Solve the Problem

1. Start at the affected dataset and walk upstream.
2. Identify the producing job and run.
3. Inspect upstream datasets and relevant lineage facets.
4. Correlate the affected run with metrics/logs/traces.
5. Determine whether the defect originated upstream, during transformation, or at publication.

### Solution

Use lineage to identify the producing job and its input datasets. Distinguish design-time expectations from runtime evidence: the runtime OpenLineage events should identify the actual job/run/dataset relationships and relevant schema, SQL, or quality facets when available.

Use the producing run's run metadata, logs, and trace to identify the failing or suspicious stage. Compare upstream data quality and freshness with the target output. If an upstream dataset was wrong, scope downstream impact through lineage. If the transformation produced the wrong values, contain publication and investigate the transformation/deployment.

### Key Concepts Tested

- OpenLineage
- runtime lineage
- jobs/runs/datasets
- data-quality facets
- root-cause analysis

### Why This Solution Works

Lineage converts a vague 'bad table' incident into a graph of actual dependencies and execution context, reducing both investigation time and unnecessary blast radius.

## Question 15 — Combine catalog metadata with governance

**Difficulty:** Moderate

### Problem

A newly published data product has no owner, unclear PII classification, and no freshness status. Design the minimum catalog metadata required before the product is considered trustworthy for broad discovery.

### How to Solve the Problem

1. Separate technical, business, and operational metadata.
2. Identify ownership/stewardship.
3. Add classifications/tags and PII status.
4. Link lineage and data-quality/freshness status.
5. Define certification/deprecation expectations.

### Solution

The catalog entry should include technical metadata describing the dataset/schema, business metadata describing meaning and domain, and operational metadata such as freshness and quality status. Assign an owner/steward and domain. Add appropriate classification and PII tags. Integrate lineage so consumers can understand upstream/downstream relationships.

Where the platform uses certification, mark the product's trust status explicitly. Define deprecation metadata when a dataset is scheduled for retirement. Metadata-as-code or CI validation can enforce required fields for future data products.

### Key Concepts Tested

- data catalogs
- technical metadata
- business metadata
- operational metadata
- ownership
- PII tags

### Why This Solution Works

A catalog is not merely a searchable schema registry. Trust requires ownership, meaning, classification, operational status, and discoverable dependencies.

## Question 16 — Choose masking, pseudonymisation, or tokenization

**Difficulty:** Moderate

### Problem

An analytics team needs to join records across systems using a stable customer identifier, but analysts must not see the original identifier. Compare static masking, keyed hashing/pseudonymisation, and tokenization for this use case.

### How to Solve the Problem

1. Determine whether reversibility is required.
2. Determine whether equality-preserving joins are required.
3. Identify who may recover the original identifier.
4. Consider key/vault management and re-identification risk.
5. Select the least privileged mechanism that satisfies the business requirement.

### Solution

If analysts only need a stable join key and no authorized party needs to recover the original identifier from the analytics value, a controlled keyed-hashing/pseudonymisation approach can be appropriate, provided key management and re-identification risks are handled.

If authorized systems must recover the original identifier, tokenization with a protected token vault provides a stronger separation between the analytics token and the original value. Static masking is appropriate when the value should simply be obscured and not used as a reversible identity.

The choice must be governed by reversibility, linkage requirements, key management, and the risk of re-identification.

### Key Concepts Tested

- static masking
- pseudonymisation
- keyed hashing
- tokenization
- token vault
- re-identification

### Why This Solution Works

The correct control depends on the required data operation and reversibility. No single masking technique is universally appropriate.

## Question 17 — Secure encryption with KMS and TLS

**Difficulty:** Moderate

### Problem

A pipeline writes sensitive data to object storage, reads from PostgreSQL, and publishes to Kafka. Design the encryption controls at rest and in transit, including where KMS and TLS belong.

### How to Solve the Problem

1. Identify every storage and network boundary.
2. Use encryption at rest for persistent data.
3. Use KMS-backed key management where customer-managed control is required.
4. Use TLS for network connections and validate certificates.
5. Include Kafka-specific transport/authentication controls without inventing custom cryptography.

### Solution

Use encryption at rest for object storage and database storage, with provider-managed or customer-managed keys according to the platform's control requirements. Where customer-managed keys are used, KMS can protect key-encryption keys and support rotation/policy controls; envelope encryption separates data encryption from key-management operations.

Use TLS for PostgreSQL connections, object-storage/service endpoints where applicable, and Kafka client-broker communication. Validate certificates and hostnames rather than disabling verification. Kafka may additionally use SASL for authentication as taught in the module. Do not implement custom cryptographic primitives.

### Key Concepts Tested

- encryption at rest
- encryption in transit
- KMS
- envelope encryption
- TLS
- Kafka TLS

### Why This Solution Works

Security must be applied at both storage and network boundaries. KMS manages keys; TLS protects transport. These controls solve different parts of the threat model.

## Question 18 — Design multi-tenant row and column security

**Difficulty:** Moderate

### Problem

A warehouse contains customers from multiple tenants. Analysts should see only their tenant's rows, while only a restricted role may see email addresses. Explain how row-level and column-level controls should work together.

### How to Solve the Problem

1. Separate row isolation from column sensitivity.
2. Identify the authenticated identity and tenant attribute.
3. Enforce row policy at the data-access boundary.
4. Restrict or mask sensitive columns separately.
5. Test both allowed and denied cases, including export/bypass paths.

### Solution

Use row-level security to restrict each analyst to rows belonging to the tenant associated with the authenticated principal or approved role attributes. Use column-level security or dynamic masking to prevent ordinary analysts from seeing email addresses. A privileged role may receive access only where explicitly approved.

The policy should be enforced where the data is queried, not only in application code. Add negative tests proving that a tenant cannot select another tenant's rows and that an analyst cannot retrieve restricted columns. Review export paths because copying data into a less-controlled destination can bypass the original policy boundary.

### Key Concepts Tested

- row-level security
- column-level security
- multi-tenant isolation
- dynamic masking
- negative access tests

### Why This Solution Works

Rows and columns represent different authorization dimensions. Combining their controls prevents an analyst from bypassing tenant isolation or sensitive-field restrictions.

## Question 19 — Execute an auditable deletion workflow

**Difficulty:** Moderate

### Problem

A customer requests deletion. The customer's data exists in an operational database, Bronze/Silver/Gold datasets, a warehouse, Kafka, logs, and quarantine storage. Design the high-level deletion workflow and identify the role of catalog and lineage.

### How to Solve the Problem

1. Resolve the data subject identity.
2. Build the data inventory and dependency graph.
3. Apply legal-hold checks.
4. Execute deletion or appropriate end actions across every governed copy.
5. Verify completion and record auditable proof.

### Solution

Resolve the subject using a stable identity key and consult the data inventory, catalog, and lineage graph to discover copies and derived datasets. Check whether a legal hold changes the deletion path. Execute idempotent deletion across the operational database, lake layers, warehouse representations, Kafka where applicable, logs/quarantine, and other governed stores.

Handle time-travel/history and caches explicitly. Where immediate physical deletion is constrained by backups or retention mechanisms, follow the documented policy and record the applicable control. Verify each layer, reconcile failures, and produce a deletion record/certificate containing what was processed, what remains under an approved exception, and the evidence supporting completion.

### Key Concepts Tested

- right to erasure
- catalog
- lineage
- identity keys
- end-to-end deletion
- deletion proof

### Why This Solution Works

Deletion is a dependency problem, not a single SQL DELETE. Catalog and lineage provide the inventory needed to find copies and derived data, while verification makes the operation auditable.

## Question 20 — Respond to PII found in logs

**Difficulty:** Moderate

### Problem

A pipeline's structured logs unexpectedly contain customer email addresses. The logs are retained centrally and are visible to a broad engineering group. Describe the immediate and preventive response.

### How to Solve the Problem

1. Treat the event as a potential privacy/security incident.
2. Stop further exposure.
3. Scope affected logs and retention windows.
4. Restrict access and apply approved deletion/redaction procedures.
5. Fix the logging path and add continuous/CI detection.

### Solution

Immediately stop or reduce the source of PII leakage, such as removing payload logging or applying approved redaction. Restrict access to affected logs while scoping which services, time ranges, and identifiers were exposed. Follow the incident process and privacy/security escalation requirements.

Do not rely on manual cleanup alone. Add PII detection for structured logs and other telemetry, CI checks where possible, and production scanning. Review retention so exposed telemetry is not retained longer than necessary. The remediation should also verify that traces, events, metrics, quarantine data, and other telemetry do not contain the same sensitive content.

### Key Concepts Tested

- PII in logs
- telemetry PII protection
- incident response
- retention
- continuous scanning

### Why This Solution Works

Logs are a data store and therefore part of the privacy boundary. Containment, scope, remediation, and prevention are required rather than simply deleting one visible log line.

# Part III — Hard

## Question 21 — Debug a successful but incomplete pipeline

**Difficulty:** Hard

### Problem

A daily revenue pipeline reports SUCCESS, finishes within its duration SLO, and shows normal CPU and memory. Finance reports that yesterday's revenue is 30% lower than expected. Design a production investigation using metrics, run metadata, logs, traces, lineage, and data-quality signals.

### How to Solve the Problem

1. Treat business correctness as an incident despite technical success.
2. Compare row/byte counts, freshness, and quality signals with historical baselines.
3. Identify the exact successful run and deployment identity.
4. Correlate logs and traces to identify missing extraction or transformation behavior.
5. Use lineage to determine downstream blast radius.
6. Contain publication before broad consumption and verify recovery.

### Solution

First establish whether the revenue drop is a real data defect rather than a business-volume change. Compare rows processed, bytes processed, source availability, quarantine counts, and other quality signals with prior successful runs. Retrieve the run metadata for the affected execution, including run_id, Git SHA, image digest, and retries.

Use the run_id to inspect structured logs and the trace to find whether an upstream API returned fewer records, a filter dropped records, or a downstream write was incomplete. Use OpenLineage to identify all downstream datasets produced from the affected run and determine blast radius.

Contain the issue by marking affected outputs as unreliable or stopping downstream publication where the incident process requires it. Identify the last known good state, correct the source/transformation problem, rerun or backfill safely, and reconcile totals against trusted source data. Verify both the corrected revenue and the absence of residual downstream impact.

Finally, add a control that would detect the specific failure mode: for example, volume/quality checks, source completeness validation, a data-quality facet, or a domain-specific reconciliation signal. The goal is not merely to make the pipeline finish; it is to make incorrect success observable.

### Key Concepts Tested

- failure investigation
- run metadata
- data quality
- OpenTelemetry
- OpenLineage
- blast radius
- reconciliation

### Why This Solution Works

Pipeline execution status is an operational signal, not proof of data correctness. The investigation combines telemetry and lineage to move from an apparently healthy run to a correctness failure and its downstream impact.

## Question 22 — Repair a broken trace across HTTP and Kafka

**Difficulty:** Hard

### Problem

A pipeline begins with an HTTP service, publishes to Kafka, and is processed by a downstream consumer. HTTP spans appear in one trace while Kafka processing appears in another. Metrics show no failure. Diagnose the observability defect and propose a repair and validation plan.

### How to Solve the Problem

1. Verify that HTTP instrumentation creates the expected root/producer context.
2. Inspect W3C propagation at the HTTP boundary.
3. Verify trace-context injection into Kafka headers.
4. Verify extraction before consumer span creation.
5. Test the full path with a known trace and inspect telemetry security/overhead.

### Solution

The likely defect is loss of OpenTelemetry context at the Kafka boundary. Verify that the HTTP request creates the root context and that the producer has access to it. Confirm that the producer injects W3C Trace Context into Kafka headers and that the consumer extracts it before starting its processing span.

Validate that the consumer's span is connected to the producer trace and that logs carry the corresponding trace_id where supported. Test both successful and failed processing. Inspect whether any custom instrumentation accidentally creates a new root span.

Do not solve the problem by putting arbitrary trace identifiers into business payloads. Keep propagation in supported headers/context mechanisms. Also ensure that trace attributes/events are sanitized and that instrumentation does not create per-record spans, which would create unnecessary overhead.

### Key Concepts Tested

- context propagation
- W3C Trace Context
- Kafka headers
- logs + traces
- telemetry overhead

### Why This Solution Works

The metrics were healthy because execution itself succeeded; the defect is in observability context propagation. Correcting the propagation boundary restores distributed causality without changing business processing.

## Question 23 — Fix noisy alerts without hiding incidents

**Difficulty:** Hard

### Problem

A data platform has 50 alerts. During a warehouse outage, engineers receive hundreds of pages for pipeline failures, freshness violations, and downstream quality checks. Design an Alertmanager strategy that reduces noise while preserving actionable incident visibility.

### How to Solve the Problem

1. Identify symptoms versus causes.
2. Group alerts around a common incident context.
3. Use inhibition when a higher-level cause explains downstream symptoms.
4. Route by severity/ownership.
5. Use silences only for deliberate, time-bounded maintenance.
6. Validate that grouping does not hide independent failures.

### Solution

Classify the alerts into cause and symptom relationships. For example, a confirmed warehouse outage can be a causal condition that explains many downstream pipeline failures and freshness alerts. Configure Alertmanager grouping on bounded dimensions such as environment, service, or incident context so related alerts are consolidated.

Use inhibition to suppress lower-value downstream symptom alerts when the known root condition is active, while preserving the primary outage alert. Route severity levels to the appropriate on-call path. Use silences for explicit, time-bounded maintenance rather than as a permanent noise-control mechanism.

Keep runbooks linked to the primary alerts. Test the strategy by injecting both a warehouse outage and an unrelated pipeline defect at the same time; the second incident must remain visible. Monitor alert fatigue and false-positive rates after deployment.

### Key Concepts Tested

- Alertmanager
- grouping
- inhibition
- silencing
- symptom vs cause
- alert fatigue

### Why This Solution Works

Good alerting compresses correlated symptoms without suppressing independent failures. The strategy must be validated against simultaneous incidents, not only the common single-failure case.

## Question 24 — Determine lineage completeness before using it for impact analysis

**Difficulty:** Hard

### Problem

An incident responder uses OpenLineage to estimate blast radius, but one downstream dataset does not appear in the graph. The pipeline uses SQL transformations that are not fully captured by the available lineage integration. Explain how to proceed without falsely treating incomplete lineage as complete.

### How to Solve the Problem

1. Identify the missing edge as a lineage gap.
2. Compare expected design-time dependencies with observed runtime lineage.
3. Investigate SQL parsing/integration limitations.
4. Use alternate evidence to bound the impact.
5. Record the completeness limitation and improve instrumentation.

### Solution

Do not treat the current graph as authoritative if a known lineage edge is missing. Determine whether the gap comes from unsupported SQL constructs, an integration boundary, a missing emitter, or incomplete runtime events. Compare design-time lineage and runtime lineage to identify expected dependencies.

During the incident, use query/job metadata, catalog information, deployment configuration, and affected time windows to conservatively bound the blast radius. Mark the impact analysis as incomplete where appropriate rather than claiming certainty.

After containment, improve the lineage emitter/integration, add validation for expected datasets, and monitor lineage completeness. Security must also be considered: lineage itself can reveal sensitive dataset relationships, so access to lineage should follow appropriate governance controls.

### Key Concepts Tested

- lineage gaps
- SQL parsing limitations
- lineage completeness
- impact analysis
- lineage security

### Why This Solution Works

Lineage is evidence, not magic. When completeness is uncertain, incident decisions must explicitly account for missing edges and use additional signals rather than producing false confidence.

## Question 25 — Investigate a PII classification failure

**Difficulty:** Hard

### Problem

A new JSON event contains phone numbers in a nested field. The catalog does not mark the field as PII, and a downstream test dataset contains raw values. Design a detection and remediation workflow that addresses structured data, catalog metadata, and test data.

### How to Solve the Problem

1. Identify the detection gap.
2. Inspect nested JSON using rules, heuristics, sampling, or Presidio where appropriate.
3. Update classification/tagging.
4. Remediate existing exposed test data.
5. Add CI and continuous production scanning.

### Solution

First confirm the sensitive field and determine whether the phone number is a direct identifier or other sensitive value under the module's classification model. Use appropriate detection rules, sampling, checksums/heuristics, or Microsoft Presidio where suitable. Human review can be used for uncertain classifications.

Update the catalog with a PII classification/tag and ensure downstream datasets inherit or are evaluated for the classification. Remove or mask the raw values in the test dataset and replace them with safe synthetic/test representations.

Add CI checks to catch schema/test-fixture regressions and continuous scanning for production data changes. Also inspect logs, events, quarantine, and telemetry because the same raw event may have propagated beyond the primary table.

### Key Concepts Tested

- PII detection
- JSON
- Presidio
- catalog tags
- test data
- continuous scanning

### Why This Solution Works

PII governance must follow data through the pipeline. A catalog tag without detection and enforcement is insufficient, while detection without downstream remediation leaves the exposure intact.

## Question 26 — Recover from a key-rotation failure

**Difficulty:** Hard

### Problem

A customer-managed encryption key is rotated, and one workload can no longer decrypt data while other workloads continue normally. Design a diagnosis and recovery process that preserves security rather than disabling encryption or certificate verification.

### How to Solve the Problem

1. Determine whether the failure is key version, permission, or application configuration related.
2. Inspect KMS key policy/version state and the workload identity.
3. Verify envelope-encryption assumptions.
4. Restore correct authorized access or key-version compatibility.
5. Validate decryption and audit the change.

### Solution

Start by identifying the exact workload, affected data, key identifier/version, and failure time. Determine whether the application uses envelope encryption with a data-encryption key protected by a key-encryption key in KMS. Check whether the workload identity still has the required KMS permissions and whether the rotated key version is available for decrypt operations.

Do not disable encryption or bypass security controls to restore service. If rotation produced an incompatible application configuration, correct the application or key-policy/version handling while preserving least privilege and separation of duties. Validate access with a controlled read/decrypt test and confirm that unaffected workloads remain secure.

Record the incident timeline and the exact key/policy change. Add tests for key rotation compatibility and monitoring for decryption failures before future rotations.

### Key Concepts Tested

- KMS
- key rotation
- envelope encryption
- key policies
- separation of duties
- incident response

### Why This Solution Works

A rotation incident can arise from key version handling, authorization, or workload configuration. Production recovery must restore the intended trust boundary rather than weakening it.

## Question 27 — Find an authorization bypass at an export boundary

**Difficulty:** Hard

### Problem

PostgreSQL row-level security correctly restricts analysts to their tenant, but an analyst can export data into a shared table that lacks the same policy. Explain the enforcement boundary failure and design controls to prevent recurrence.

### How to Solve the Problem

1. Identify where RLS is enforced and where it stops.
2. Treat exports as a new data-access boundary.
3. Check destination permissions and policy inheritance.
4. Add negative tests for both source access and export paths.
5. Add audit logging and review controls.

### Solution

RLS protects queries against the source table but does not automatically protect every destination created by an authorized user. The shared export table is therefore an enforcement boundary where tenant isolation can be lost.

Restrict who can create/write shared destinations, require destination datasets to carry appropriate row/column policies, and use policy-as-code or metadata-driven controls to prevent creation of ungoverned sensitive datasets. Add negative tests that attempt cross-tenant export and unauthorized reads. Audit export operations and review access regularly.

The design should explicitly enumerate enforcement boundaries: source tables, views, downstream tables, files, extracts, and other supported consumption paths. Time-bound or approved break-glass access should remain exceptional and auditable.

### Key Concepts Tested

- RLS
- enforcement boundaries
- export/bypass risks
- policy-as-code
- negative tests
- audit logs

### Why This Solution Works

Security controls are only as strong as their last enforcement boundary. An RLS policy cannot protect data after it has been copied into an unrestricted destination.

## Question 28 — Design deletion with time travel and backups

**Difficulty:** Hard

### Problem

A data-subject erasure request has been processed from the current warehouse table, but the warehouse retains historical versions and backups. The catalog shows downstream Gold aggregates. Design an auditable deletion strategy that addresses historical copies and recovery mechanisms.

### How to Solve the Problem

1. Inventory current and historical representations using catalog/lineage.
2. Identify time-travel retention and backup constraints.
3. Determine what can be physically deleted immediately.
4. Use approved retention/legal-hold/crypto-shredding controls where direct deletion is constrained.
5. Verify and document every exception.

### Solution

Use the catalog and lineage graph to inventory the current table, downstream Gold aggregates, caches, and other representations. Explicitly inspect warehouse time-travel/history because deleting the current row does not necessarily remove historical versions immediately.

Handle backups according to the documented retention and deletion policy. If immediate physical deletion from a backup is not supported, record the controlled exception and the mechanism by which the data becomes inaccessible or is removed at expiry. Where the module's encryption design permits crypto-shredding as a control, it may be used when its assumptions are satisfied.

Reconcile all affected downstream representations and produce auditable deletion evidence. The workflow must be idempotent so retries do not create inconsistent state. Legal holds must override ordinary deletion where required and be recorded.

### Key Concepts Tested

- right to erasure
- time travel
- backups
- lineage
- crypto-shredding
- idempotency

### Why This Solution Works

Erasure is not complete merely because the current row disappeared. Historical versions, derived copies, and backups are separate lifecycle surfaces that require explicit policy and evidence.

## Question 29 — Build an incident timeline from telemetry

**Difficulty:** Hard

### Problem

During a data incident, responders disagree about whether the first failure occurred at 02:10 or 02:35. Design a method to reconstruct the timeline using run metadata, metrics, structured logs, traces, and OpenLineage events, and explain how to preserve evidence.

### How to Solve the Problem

1. Establish trusted timestamps from multiple telemetry sources.
2. Identify the first anomalous signal, first failed run/event, and first affected output.
3. Correlate identifiers across systems.
4. Distinguish detection time from occurrence time.
5. Preserve original evidence and record interpretations separately.

### Solution

Start with run metadata and time-series metrics to establish when behavior changed. Identify the first affected run_id and inspect its structured logs for precise execution events. Use trace timestamps to identify where the first abnormal operation occurred. OpenLineage START/COMPLETE/FAIL events can establish execution and dataset dependency timing.

Distinguish the time the defect occurred, the time it became visible, and the time it was detected/declared. Preserve original logs, trace/event records, and relevant metadata according to the incident evidence policy. Build a timeline with source references and mark uncertain timestamps rather than silently choosing one.

The resulting timeline should support root-cause analysis and postmortem actions, including TTD, TTM, and TTR measurements.

### Key Concepts Tested

- incident timeline
- run metadata
- structured logs
- traces
- OpenLineage events
- TTD/TTM/TTR
- evidence preservation

### Why This Solution Works

Different telemetry systems answer different timing questions. Correlating them prevents detection time from being mistaken for failure time and creates a defensible incident record.

## Question 30 — Convert a repeat incident into preventive controls

**Difficulty:** Hard

### Problem

The same pipeline has had three incidents caused by missing upstream data. Each incident was fixed manually, but no preventive control was added. Design a production improvement that connects postmortem findings to tests, alerts, runbooks, and ownership.

### How to Solve the Problem

1. Separate root cause from contributing factors.
2. Define a corrective action and preventive action.
3. Map each action to an automated test, alert, or runbook.
4. Assign an owner and deadline.
5. Verify completion and monitor recurrence.

### Solution

Use a blameless postmortem and Five Whys to establish the root cause and contributing factors. If the root cause is that upstream completeness is not validated, add an explicit data-quality or completeness control before publication. Add an alert based on the appropriate signal and a runbook describing investigation and containment.

Add a regression test for the known failure mode and, where appropriate, failure injection to prove the alert and runbook work. Assign action owners and deadlines. Track whether the preventive control reduces repeat incidents and whether it introduces unacceptable false positives or operational cost.

Map the postmortem action to the corresponding test, alert, and runbook so future engineers can verify that the lesson has become an operational control.

### Key Concepts Tested

- postmortems
- Five Whys
- corrective actions
- preventive actions
- tests
- alerts
- runbooks
- failure injection

### Why This Solution Works

A postmortem creates value only when lessons become durable controls. Explicit mappings from incident findings to tests, alerts, and runbooks make prevention verifiable rather than aspirational.

# Part IV — Advanced

## Question 31 — Design an end-to-end observable and governed data platform

**Difficulty:** Advanced

### Problem

Design the observability, lineage, metadata, privacy, encryption, authorization, retention, and incident-response control plane for a production platform ingesting APIs and Kafka events into lakehouse/warehouse data products. The design must support both daily batch and streaming workloads.

### How to Solve the Problem

1. Start with the data lifecycle and trust boundaries.
2. Define telemetry signals and run metadata.
3. Add distributed tracing and context propagation.
4. Add runtime lineage and catalog metadata.
5. Add PII detection and privacy controls.
6. Add encryption and access-control enforcement points.
7. Add retention/deletion controls.
8. Connect everything to alerting and incident response.

### Solution

Use pipeline metrics and unified run metadata as the operational backbone: success/failure, duration, retries, rows/bytes, freshness, lag, cost, run_id, Git SHA, and image digest. Use structured JSON logs with correlation identifiers. Use OpenTelemetry traces for meaningful pipeline stages, propagate W3C context through HTTP and Kafka, and use the Collector with appropriate receivers/processors/exporters. Avoid per-record spans and redact sensitive telemetry.

Emit OpenLineage runtime events for jobs, runs, and datasets, enriched with appropriate schema, SQL, data-quality, and custom facets. Integrate the catalog with ownership, domains, classifications, PII tags, freshness, quality, lineage, certification, and deprecation. Enforce metadata quality through metadata-as-code/CI where applicable.

Detect PII in structured data, free text, JSON, logs, events, quarantine, and test data using rules, heuristics, sampling, Presidio, and human review where needed. Use approved masking, pseudonymisation, or tokenization controls based on reversibility requirements.

Encrypt data at rest and in transit. Use KMS and envelope-encryption patterns where customer-managed key control is required, TLS with certificate validation for transport, and explicit encryption inventories/boundaries. Enforce least-privilege authorization using RBAC/ABAC as appropriate, row/column controls, dynamic masking, policy-as-code, negative tests, and audit logging.

Define retention metadata by purpose, period, and end action, and implement lifecycle controls across databases, object storage, Kafka, logs, quarantine, historical versions, and derived data. Use catalog and lineage to support auditable deletion workflows, with legal holds and backup/time-travel constraints explicitly handled.

Finally, implement actionable SLO-based alerts, runbooks, on-call escalation, and a data incident process with Incident Commander, technical responder, communications lead, scribe, evidence preservation, blast-radius analysis, recovery verification, reconciliation, and blameless postmortems. Test the control plane with failure injection across observability, privacy, security, and deletion paths.

### Key Concepts Tested

- observability architecture
- OpenTelemetry
- OpenLineage
- catalogs
- PII protection
- KMS/TLS
- access control
- retention/deletion
- incident response

### Why This Solution Works

The design is effective because each control addresses a different production risk while shared identifiers and metadata connect them. Metrics detect, traces explain execution, lineage scopes impact, catalogs govern meaning/ownership, security controls protect access/data, lifecycle controls manage retention, and incident processes coordinate response and prevention.

## Question 32 — Trace and diagnose a slow HTTP → Kafka → Spark → warehouse path

**Difficulty:** Advanced

### Problem

A critical pipeline has a freshness SLO violation. The path is HTTP ingestion → Kafka → Spark processing → warehouse publication. Metrics show Kafka lag is elevated, but it is unclear whether lag is the root cause or a symptom. Design a multi-signal investigation and remediation plan.

### How to Solve the Problem

1. Establish the SLO violation and affected time window.
2. Compare HTTP arrival, Kafka lag, Spark run/processing time, and warehouse publication time.
3. Follow a distributed trace across HTTP and Kafka.
4. Use run metadata and logs to identify Spark/warehouse behavior.
5. Use lineage to identify affected outputs.
6. Contain and recover based on the causal boundary.

### Solution

Begin with the freshness SLI/SLO and determine when the violation began. Compare source arrival time, Kafka lag, consumer start time, Spark processing duration, and warehouse publication time. Elevated Kafka lag may be the root cause, but it can also result from slow downstream processing.

Use OpenTelemetry context propagation to follow the path from HTTP through Kafka into downstream processing where instrumentation supports it. Inspect consumer and processing spans, retry/error events, and warehouse spans. Use run metadata for exact execution identity, retries, Git SHA, and image digest, then inspect structured logs.

Use OpenLineage to identify which datasets and data products were affected by the delayed runs. If consumer throughput is the bottleneck, contain by controlling downstream load and recover consumer capacity. If Spark or warehouse processing is slow, address that stage instead. After recovery, verify end-to-end freshness, not merely Kafka lag.

Add or refine alerts around the SLO-relevant condition and the most diagnostic causal signals, and document the investigation path in a runbook.

### Key Concepts Tested

- freshness SLO
- Kafka lag
- distributed tracing
- run metadata
- OpenLineage
- runbooks
- recovery

### Why This Solution Works

A lag metric alone cannot establish causality. End-to-end timestamps plus traces and run metadata distinguish upstream arrival delay, queueing, processing latency, and publication delay.

## Question 33 — Respond to a combined data-quality and PII incident

**Difficulty:** Advanced

### Problem

A customer-data pipeline produces incorrect records and simultaneously writes raw email addresses into a quarantine table and logs. The pipeline succeeded technically. Design the incident response from detection through postmortem, including privacy escalation, blast-radius analysis, containment, recovery, and preventive controls.

### How to Solve the Problem

1. Declare the incident based on both correctness and privacy impact.
2. Establish Incident Commander roles and preserve evidence.
3. Contain publication and the PII leakage.
4. Use lineage and telemetry to scope both defects and exposure.
5. Recover with reconciliation and privacy-safe handling.
6. Convert findings into tests, alerts, scanning, and runbooks.

### Solution

Declare the incident with severity based on the combined data-integrity and privacy impact. Assign an Incident Commander, technical responder, communications lead, and scribe as appropriate. Preserve evidence before destructive cleanup while restricting unnecessary access to exposed logs/quarantine data.

Contain the incorrect data from reaching further consumers and stop the logging/quarantine path from generating additional PII exposure. Use run metadata, structured logs, traces, and data-quality signals to identify the failing run and defect stage. Use OpenLineage to determine downstream datasets affected by incorrect records. Separately scope where the PII appeared, including telemetry and quarantine.

Correct the transformation/source issue, rerun safely, reconcile corrected records with a trusted source, and verify downstream outputs. Apply approved deletion/masking/retention procedures to exposed PII according to the incident and privacy controls. Escalate to the appropriate privacy/security process.

The postmortem should distinguish root cause from contributing factors and create owned corrective/preventive actions: regression tests for the data defect, PII detection/CI scanning, telemetry redaction, quarantine controls, actionable alerts, and an updated runbook. Validate the controls through failure injection where appropriate.

### Key Concepts Tested

- data-quality incident
- PII exposure
- Incident Commander
- lineage
- containment
- reconciliation
- postmortem
- PII scanning

### Why This Solution Works

The incident has two different risk dimensions: incorrect data and unauthorized exposure. Treating them separately during scoping but coordinating them operationally prevents one workstream from being overlooked.

## Question 34 — Design tenant isolation with sensitive columns and break-glass access

**Difficulty:** Advanced

### Problem

A multi-tenant analytics platform contains PII. Normal analysts must see only their tenant's rows and masked email addresses. A small operations group occasionally needs temporary unmasked access during approved incidents. Design the authorization model, enforcement points, verification, and audit strategy.

### How to Solve the Problem

1. Define normal and exceptional access separately.
2. Enforce row isolation and column protection at the data-access boundary.
3. Use least-privilege roles/service identities.
4. Make break-glass access time-bound and approval-controlled.
5. Add positive/negative policy tests and audit logging.
6. Review export and downstream bypass paths.

### Solution

Normal analysts should receive a role that permits only the required datasets and tenant rows. Row-level security should enforce tenant isolation, while column-level security or dynamic masking protects email addresses. The policy should derive tenant access from an authenticated identity or approved attribute, not from a user-controlled query parameter.

The operations group should not receive permanent unmasked access merely because they might need it. Break-glass access should be explicitly approved, time-bound, least-privileged, auditable, and used only for the incident scope. Access reviews should verify that emergency privileges expire and are not retained.

Implement negative tests for cross-tenant reads, unmasked columns, and export paths. Add positive tests for approved access. Audit both ordinary and break-glass access, including identity, time, purpose, and affected data. Review enforcement boundaries outside the primary warehouse table so extracts or shared destinations do not bypass the controls.

### Key Concepts Tested

- multi-tenant isolation
- RLS
- column-level security
- dynamic masking
- break-glass
- access reviews
- audit logs
- export/bypass risks

### Why This Solution Works

Normal access and emergency access have different risk profiles. Separating them prevents an operational exception from becoming a standing privilege and makes the exceptional path auditable.

## Question 35 — Execute a deletion request across the full data lifecycle

**Difficulty:** Advanced

### Problem

A customer requests erasure. The platform contains OLTP data, Bronze/Silver/Gold datasets, warehouse history, Kafka events, logs, quarantine records, feature data, test fixtures, and backups. Some data is under a legal hold and some historical storage is governed by retention policies. Design an auditable end-to-end workflow.

### How to Solve the Problem

1. Resolve the subject identity and establish the authoritative inventory.
2. Use catalog and lineage to enumerate direct and derived copies.
3. Classify each copy by deletion mechanism and retention/hold constraints.
4. Execute idempotent deletion or approved exception handling.
5. Verify and reconcile every layer.
6. Produce evidence and certificate data without exposing new PII.

### Solution

Create an erasure case keyed by a stable identity and enumerate all governed representations using the catalog and lineage graph. Include OLTP, Bronze/Silver/Gold, warehouse current and historical representations, caches/aggregates where applicable, Kafka, logs, quarantine, feature data, test fixtures, and backups.

For each location, define the required action: immediate deletion, partition/lifecycle deletion, removal of derived representations, controlled expiry, or an approved exception. A legal hold must prevent prohibited deletion while recording the reason and scope. Historical warehouse versions and backups require explicit handling; current-row deletion alone is insufficient.

Make each operation idempotent and record status per layer. On failure, retry or escalate without falsely marking the request complete. Verify the absence or approved disposition of the subject's data and reconcile derived outputs. Produce an auditable deletion record/certificate with identifiers and evidence while avoiding unnecessary reproduction of the subject's sensitive data.

Use privacy-by-design principles throughout, including minimizing the data copied into the deletion workflow itself. Test the workflow with injected failures and partial completion to prove recovery behavior.

### Key Concepts Tested

- end-to-end deletion
- catalog
- lineage
- legal holds
- time travel
- backups
- idempotency
- deletion certificates
- privacy by design

### Why This Solution Works

The platform is a graph of data copies, not a single table. A reliable erasure process needs inventory, dependency discovery, per-store controls, idempotency, verification, and auditable exceptions.

## Question 36 — Build a senior-level observability SLO and incident workflow

**Difficulty:** Advanced

### Problem

A critical data product has intermittent freshness violations, high consumer lag, occasional failed runs, and rising alert volume. Design an operational model connecting metrics, SLOs, burn-rate alerts, traces, runbooks, on-call escalation, and postmortems. Explain how you would avoid both under-alerting and alert fatigue.

### How to Solve the Problem

1. Define the freshness SLI and reliability SLO.
2. Add supporting causal metrics without paging on every symptom.
3. Use burn rate for paging and lower-severity alerts for slower degradation.
4. Ensure traces/logs/run metadata support diagnosis.
5. Build runbooks and escalation paths.
6. Review incidents and tune controls from postmortem evidence.

### Solution

Define the freshness SLI based on actual consumer-visible delivery timeliness and set an SLO appropriate for the data product. Track supporting metrics such as pipeline duration, retries, Kafka lag, rows/bytes, queue time, and failure rate. Use those metrics diagnostically rather than turning every metric into a page.

Use burn-rate-based alerts to identify rapid or sustained SLO-budget consumption. Configure Alertmanager grouping, inhibition, severity, and routing so a single underlying outage does not produce hundreds of pages. Lower-severity notifications can capture slower degradation without waking the primary on-call.

The runbook should start with freshness and move through source availability, queue/lag, run metadata, structured logs, traces, and lineage. On-call escalation should define ownership, handover, and stakeholder/data-status communication.

After incidents, measure TTD, TTM, and TTR, conduct blameless postmortems, and map corrective actions to tests, alerts, and runbooks. Failure injection should validate the end-to-end response.

### Key Concepts Tested

- SLI/SLO
- burn rate
- Alertmanager
- alert fatigue
- runbooks
- on-call
- TTD/TTM/TTR
- postmortems

### Why This Solution Works

Operational maturity comes from connecting detection to diagnosis and response. SLOs determine what matters, alerts prioritize it, telemetry enables investigation, and postmortems improve the system.

## Question 37 — Design telemetry security without destroying usefulness

**Difficulty:** Advanced

### Problem

A platform team wants full payloads in logs, traces, and quarantine data to simplify debugging. The platform handles PII and sensitive events. Design a telemetry-security policy that preserves diagnostic value while minimizing privacy risk and overhead.

### How to Solve the Problem

1. Identify sensitive telemetry surfaces.
2. Define what should be recorded as attributes/events versus omitted.
3. Apply PII detection/redaction and access controls.
4. Set retention appropriately.
5. Avoid per-record tracing and uncontrolled cardinality.
6. Validate the policy through tests and incident exercises.

### Solution

Do not log or trace full business payloads merely for convenience. Define structured fields that identify the pipeline, run, stage, status, timing, and non-sensitive diagnostic context. Use run_id and trace_id for correlation. Record exception events without copying raw sensitive payloads.

Apply PII detection/redaction to logs, traces, events, quarantine, and other telemetry. Restrict access using least privilege and appropriate row/column or dataset controls where supported. Define retention so sensitive telemetry is not kept indefinitely.

Avoid per-record spans because they create high telemetry volume and overhead. Use bounded metric labels and meaningful stage-level spans. Test that representative PII is redacted and that diagnostic correlation still works. Include failure injection to confirm that an exception does not accidentally dump sensitive payload content.

### Key Concepts Tested

- telemetry PII protection
- redaction
- structured logging
- trace overhead
- metric cardinality
- retention
- least privilege

### Why This Solution Works

The goal is diagnostic sufficiency, not maximal data collection. Correlation identifiers and carefully selected fields usually provide enough debugging value without turning telemetry into another uncontrolled sensitive-data repository.

## Question 38 — Design a production lineage and catalog trust model

**Difficulty:** Advanced

### Problem

A data organization wants to use lineage and catalog metadata to drive impact analysis, ownership, PII governance, certification, and deprecation. Runtime lineage is incomplete for some SQL workloads. Design a trust model that prevents consumers from treating incomplete metadata as authoritative.

### How to Solve the Problem

1. Separate metadata types and trust levels.
2. Distinguish design-time expectations from runtime evidence.
3. Track lineage completeness and known gaps.
4. Integrate ownership, classification, quality, freshness, and certification.
5. Use CI/metadata-as-code to prevent regressions.
6. Make uncertainty visible in operational workflows.

### Solution

Treat catalog and lineage as governed metadata products with explicit quality indicators. Store technical, business, and operational metadata separately but link them through dataset identities. Ownership, domain, PII classification, quality status, freshness, certification, and deprecation state should be visible to consumers.

For lineage, distinguish design-time lineage from runtime OpenLineage evidence. Where SQL parsing or integrations are incomplete, record the known gap rather than implying full coverage. A dataset should not be considered fully impact-analysis-ready if critical downstream edges are missing.

Use metadata-as-code and CI validation for required metadata fields and expected lineage relationships where practical. Integrate runtime lineage, data-quality facets, and catalog status. During incidents, the workflow should surface lineage completeness so responders can bound blast radius conservatively.

Security must apply to metadata itself: lineage can reveal sensitive relationships and should be accessible only to appropriate principals.

### Key Concepts Tested

- data catalogs
- metadata quality
- runtime vs design-time lineage
- lineage completeness
- metadata-as-code
- certification
- lineage security

### Why This Solution Works

Trustworthy governance requires metadata quality, not merely metadata presence. Making completeness and certification explicit prevents automation and incident responders from over-trusting partial lineage.

## Question 39 — Architect a combined financial-corruption and privacy incident response

**Difficulty:** Advanced

### Problem

A revenue pipeline recently changed a field interpretation and multiplied cents by 100 during transformation. The same release also caused customer identifiers to appear in structured error logs. The pipeline reports success and downstream dashboards have already consumed the data. Design the complete response, including blast radius, containment, privacy handling, recovery, reconciliation, and preventive controls.

### How to Solve the Problem

1. Declare a high-severity data incident with both financial and privacy dimensions.
2. Establish last known good state and preserve evidence.
3. Use run metadata/deployment identity to scope affected executions.
4. Use lineage to identify all affected outputs.
5. Contain financial publication and PII exposure separately.
6. Recover with controlled correction and reconciliation.
7. Apply privacy remediation and audit evidence.
8. Convert both root causes into durable controls.

### Solution

Declare the incident and assign the Incident Commander, technical responder, communications lead, and scribe as appropriate. Preserve the affected logs, run metadata, traces, and lineage evidence before cleanup. Use Git SHA/image digest and run_id to identify the release boundary and affected executions.

Use OpenLineage to enumerate downstream datasets and data products derived from the bad runs. Mark affected financial outputs as unreliable and stop further publication or consumption according to the incident process. Establish the last known good run and calculate the financial blast radius by reconciling affected outputs against a trusted source.

For the PII exposure, restrict access to affected logs, stop further raw-identifier logging, and execute approved retention/deletion/redaction procedures. Escalate through the privacy/security process. Do not erase evidence before required preservation steps are complete.

Fix the unit interpretation, rerun/backfill using a controlled process, and reconcile financial totals at each affected layer. Verify corrected dashboards and downstream datasets before declaring recovery. Confirm the PII leakage path is closed.

The postmortem should identify the root cause and contributing factors separately. Prevent recurrence with unit/semantic validation tests, data-quality/reconciliation controls, CI checks for telemetry redaction, continuous PII scanning, actionable alerts, and a runbook. Assign owners and deadlines and map each action to a test, alert, or operational control.

### Key Concepts Tested

- financial-data corruption
- PII exposure
- blast radius
- last known good state
- reconciliation
- evidence preservation
- postmortem
- preventive controls

### Why This Solution Works

The scenario requires two coordinated containment tracks: correctness and privacy. Lineage and deployment/run metadata establish scope, while reconciliation proves financial recovery and privacy controls address the separate exposure risk.

## Question 40 — Design the operating model for a governed data platform

**Difficulty:** Advanced

### Problem

You are the senior engineer responsible for a production data platform serving multiple data products. Leadership asks for an operating model that proves the platform is observable, traceable, governed, privacy-aware, secure, compliant, and capable of recovering from incidents. Produce a concrete control framework and explain how it would be continuously validated.

### How to Solve the Problem

1. Organize controls by observability, lineage/metadata, privacy, security, lifecycle, and incident response.
2. Define signals, ownership, enforcement points, and evidence for each.
3. Connect controls through shared identifiers and metadata.
4. Define automated tests and failure-injection exercises.
5. Define operational reviews and measurable reliability outcomes.
6. Ensure exceptions, legal holds, emergency access, and incomplete metadata are explicit and auditable.

### Solution

The operating model should establish a common production control plane.

**Observability:** instrument pipeline metrics for success/failure, duration, retries, rows/bytes, freshness, lag, cost, and queue time. Store unified run metadata with run_id, deployment identity, and execution context. Use structured JSON logs and OpenTelemetry traces with W3C context propagation, Kafka header propagation, Collector processing, telemetry redaction, bounded cardinality, and meaningful spans.

**Lineage and metadata:** emit runtime OpenLineage events for jobs/runs/datasets and appropriate facets. Maintain catalog technical, business, and operational metadata with ownership, domains, classifications, PII tags, quality/freshness status, lineage, certification, usage, and deprecation. Track lineage completeness and do not treat missing edges as authoritative.

**Privacy:** continuously detect PII in structured data, free text, JSON, logs, events, quarantine, and test data using appropriate rules/heuristics/Presidio and human review. Apply masking, pseudonymisation, or tokenization according to use case. Protect telemetry and test data as governed data stores.

**Security:** encrypt at rest and in transit using approved primitives/services, KMS, envelope encryption where applicable, TLS certificate validation, and explicit encryption boundaries. Enforce least privilege with human and service identities, RBAC/ABAC, row/column controls, masking, policy-as-code, negative tests, audit logging, access reviews, time-bound approvals, and controlled break-glass access. Treat exports and downstream copies as enforcement boundaries.

**Lifecycle/compliance:** maintain retention metadata by purpose, period, and end action. Apply lifecycle controls to databases, object storage, Kafka, logs, quarantine, historical versions, caches, aggregates, feature/training data, test data, and backups. Use catalog and lineage for deletion inventory, support legal holds, make workflows idempotent, verify every layer, and produce auditable deletion evidence/certificates.

**Incident response:** define severity, detection, declaration, Incident Commander roles, triage, containment, blast-radius analysis, root cause, last known good state, remediation, recovery, verification, reconciliation, communication, evidence preservation, and blameless postmortems. Measure TTD, TTM, and TTR. Require corrective/preventive actions with owners and deadlines and map them to tests, alerts, and runbooks.

Continuously validate the operating model through CI policy checks, authorization negative tests, PII scanning, metadata/contract checks, telemetry tests, deletion failure-injection tests, alert tests, and game days. Review dashboards/SLOs, access logs, lineage completeness, retention/deletion evidence, incident trends, and recurring failure patterns. The system should demonstrate not only that controls exist, but that they work under failure.

### Key Concepts Tested

- end-to-end platform governance
- observability
- lineage
- metadata
- PII
- encryption
- authorization
- retention
- incident response
- continuous validation
- game days

### Why This Solution Works

A production control framework is credible only when every control has an owner, enforcement point, observable evidence, and a validation mechanism. Continuous testing and game days turn documented policy into demonstrated operational capability.

# Final Practice Checklist

- [x] Exactly 40 questions.
- [x] Exactly 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced questions.
- [x] Every question contains Problem, How to Solve the Problem, Solution, Key Concepts Tested, and Why This Solution Works.
- [x] All ten Module 2.20 topic areas are represented.
- [x] Cross-topic reasoning increases substantially in the Hard and Advanced sections.
- [x] Failure-injection and production-incident scenarios are included.
- [x] Security, privacy, governance, retention/deletion, and incident-response scenarios are included.
- [x] Solutions explain reasoning, controls, enforcement boundaries, verification, and trade-offs rather than giving definition-only answers.
- [x] Code/configuration is used only where it improves the engineering solution.
- [x] No unrelated curriculum is introduced.
