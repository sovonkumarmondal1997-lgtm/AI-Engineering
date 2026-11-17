# Unit 4 — Loki and Centralized Log Pipelines

**Target file:** `04-loki-and-centralized-log-pipelines.md` | **Estimated time:** 18–26 hours | **Prerequisites:** M11 Units 1–3, M09 secrets/security foundations, Docker Compose or `kind` basics
**Core tools:** Grafana Loki, Grafana Explore, OpenTelemetry Collector, structured application logs, LogQL | **Awareness:** Grafana Alloy, Promtail, Fluent Bit, Vector, distributed Loki, object storage | **Last reviewed:** 2026-10-28 (authoring date, not a claim of live documentation review) | **Tool baseline assumed:** local single-binary Loki + Collector OTLP HTTP ingestion; pin exact releases after checking official release documentation `[VERIFY]` | **Stack profile required:** Core + Logs | **Footprint:** measure yours

> **Source and execution honesty.** The supplied unit-generation prompt is the source for this lesson's scope. Official vendor documentation was not live-consulted while authoring this artifact; therefore release-sensitive settings are marked `[VERIFY]` and registered in §4.14. Commands and outputs labelled “representative” are examples, not claimed execution results. The configuration is a teaching baseline, not a production-ready deployment.

## Table of contents

- [4.0 Why this matters in production](#40-why-this-matters-in-production)
- [4.1 Learning objectives](#41-learning-objectives)
- [4.2 Concept map and vocabulary](#42-concept-map-and-vocabulary)
- [4.3 Level 1 — Beginner](#43-level-1--beginner)
- [4.4 Level 2 — Intermediate](#44-level-2--intermediate)
- [4.5 Level 3 — Advanced](#45-level-3--advanced)
- [4.6 Level 4 — Expert](#46-level-4--expert)
- [4.7 SRE lens](#47-sre-lens)
- [4.8 Security lens](#48-security-lens)
- [4.9 Production checklist](#49-production-checklist)
- [4.10 Hands-on lab set](#410-hands-on-lab-set)
- [4.11 Self-check questions](#411-self-check-questions)
- [4.12 Evidence artifacts](#412-evidence-artifacts)
- [4.13 Common interview and design-review questions](#413-common-interview-and-design-review-questions)
- [4.14 Sources and verification notes](#414-sources-and-verification-notes)
- [Audit summary](#audit-summary)
- [Open verification items](#open-verification-items)
- [Definition of done](#definition-of-done)

## Unit 4 — Loki and Centralized Log Pipelines

### 4.0 Why this matters in production

During an inference API incident, a pod restarts and its local container log is rotated before an engineer captures the exception; the dashboard shows elevated latency, but the decisive event has disappeared. A second team searches Loki using `request_id` as a stream label, creating a large number of streams and making queries slower just when they need evidence. A third service logs an authorization header at INFO, and a downstream redaction rule is discovered only after the value has been ingested. Centralized logging helps only when the pipeline is observable, bounded, secure, and tested for loss; “the query returned no lines” is not proof that no event occurred.

### 4.1 Learning objectives

By the end, the learner can produce inspectable evidence for each objective:

1. **[L1]** Trace a synthetic event from application output to Loki and Grafana Explore, naming at least five failure/drop points.
2. **[L1]** Explain Loki streams, labels, chunks, label-first querying, and why Loki is not a general full-text index.
3. **[L2]** Define and validate a structured JSON log contract with UTC timestamps, stable service names, bounded labels, and identifiers kept in the body.
4. **[L2]** Run a local Loki lab with filesystem storage and short retention after verifying the selected release's configuration.
5. **[L2]** Configure or adapt a supported OpenTelemetry Collector path and prove a known synthetic event arrives in Loki.
6. **[L2]** Write and explain at least 20 LogQL queries, distinguishing log queries from metric queries and absent data from zero.
7. **[L3]** Demonstrate redaction tests, label-cardinality comparison, query-shape optimization, and an explicit retention policy.
8. **[L3]** Measure emitted-versus-queryable canary events during a bounded outage and document duplicates, delays, and loss windows without claiming exactly-once delivery.
9. **[L4]** Diagnose a pipeline failure using evidence from source, receiver, processor, exporter, Loki, and query stages; propose a recoverable mitigation.
10. **[L4]** Submit a version/verification register, security review, governance contract, rollback runbook, and ten-pass audit evidence.

### 4.2 Concept map and vocabulary

#### Pipeline architecture

```mermaid
flowchart LR
  A[FastAPI / ETL / worker] -->|stdout/stderr or JSONL| B[Runtime log files / bounded lab file]
  B -->|read + checkpoint| C[Collector receiver]
  C --> D[Parse / normalize / redact / enrich]
  D --> E[Batch + memory guard + retry queue]
  E -->|OTLP HTTP; verify endpoint| F[Loki ingestion]
  F --> G[Chunks + label index + retention]
  G --> H[LogQL query]
  H --> I[Grafana Explore]
  I --> J[Incident operator]
  K[Versioned config / access boundary] -. governs .-> C
  K -. governs .-> F
```

**Trust and failure boundaries:** application code may emit sensitive content; runtime files can rotate; the receiver may lack path permissions; parser/redactor can fail or drop fields; buffers can fill; exporter retries can duplicate or exhaust memory; Loki can reject entries; retention can expire evidence; query labels/time range can hide events; Grafana can fail while Loki remains healthy. Keep the entire lab on an isolated local network and bind user-facing ports to loopback where supported.

| Term | Precise definition | Common misconception |
|---|---|---|
| Event / log record | One timestamped record describing an occurrence; its body may be JSON or text. | One printed line always equals one logical event, even for stack traces. |
| Structured logging | Logging with stable machine-readable fields and a documented schema. | JSON alone makes a log safe or useful. |
| Collector | A pipeline runtime that receives, processes, and exports telemetry using components included in its distribution. | Every Collector build contains every receiver, processor, and exporter. |
| Loki stream | A sequence of log entries identified by a label set. | Every JSON field should become a label. |
| Label cardinality | The number of distinct values/combinations used as indexed stream dimensions. | A high-cardinality label is harmless if each value occurs once. |
| Chunk | A stored group of log entries for a stream/time range, subject to Loki's implementation and version. | Loki indexes every word like a general full-text search engine. |
| LogQL | Loki's query language for selecting streams, filtering/parsing lines, and computing log-derived metrics. | A query returning no lines means the service had no errors. |
| Redaction | Removing or replacing sensitive values before they are stored or exposed. | Redaction after ingestion erases all historical copies. |
| Back-pressure | A downstream slowdown propagating to queues, retries, or upstream components. | A queue guarantees data is never lost. |
| Canary | A known synthetic event emitted on a schedule to test end-to-end delivery. | Ordinary log volume proves that a particular critical event can arrive. |
| Retention | Policy and process governing how long data remains queryable/stored. | Expired data is always deleted immediately at the policy boundary. |
| Structured metadata | Non-indexed metadata supported by specific Loki versions and ingestion paths. | It is universally available and behaves exactly like labels. |

#### Running example and contract

All names below are **[ILLUSTRATIVE]** and must be reconciled with the actual Unit 2 schema before reuse. The synthetic platform has `inference-api`, `batch-etl`, `queue-worker`, and `log-canary`. The one chosen event schema uses snake_case consistently:

```json
{
  "timestamp": "2026-10-28T12:00:00.000Z",
  "level": "ERROR",
  "service": "inference-api",
  "environment": "local",
  "message": "inference request failed",
  "route": "/v1/predict",
  "request_id": "req-synthetic-0007",
  "trace_id": "trace-synthetic-0007",
  "release": "dev-1",
  "duration_ms": 412.7,
  "error_code": "UPSTREAM_TIMEOUT",
  "run_id": null,
  "quality_status": null,
  "schema_version": 1
}
```

Contract rules: `timestamp` is RFC 3339 UTC; `level` is from a bounded set; `service`, `environment`, `route`, `release`, and `error_code` are bounded/controlled; IDs and per-run identifiers stay in the body or supported structured metadata, never ordinary stream labels. Do not log request bodies, cookies, authorization headers, passwords, raw user payloads, email addresses, or row contents. The log schema is not an OpenTelemetry semantic-conventions claim; map `service` to `service.name` explicitly if the pipeline uses resource attributes `[VERIFY]`.

**Stream-label allowlist for this lab:** `service`, `environment`, optionally `level` and `namespace` only when bounded and present. Avoid adding a label just because it exists in JSON. `trace_id`, `span_id`, `request_id`, `user_id`, raw URL, email, arbitrary error text, `run_id`, partition ID, and timestamps must not be stream labels.

### 4.3 Level 1 — Beginner

#### 4.3.1 Why centralize logs

Containers and pods are replaceable; replicas may be scheduled on different nodes; `kubectl logs` is useful for immediate diagnosis but is not a durable cross-service history. Retention depends on runtime configuration, node health, rotation, and whether the log collector read the file before it disappeared. Centralization improves search and correlation but introduces another failure path: a service can emit a log that never reaches the backend.

Use the signal that answers the question:

- **Metrics:** “Is error ratio rising?” or “How many jobs are queued?”
- **Logs:** “Which bounded error code occurred, with what safe context?”
- **Traces:** “Which dependency consumed time across this request?”

Consistent service naming and UTC timestamps support correlation. Request/trace IDs belong in event content, not normal stream labels. A log query is evidence, not proof of causality by itself.

#### 4.3.2 Loki query model

Loki narrows candidate data using a stream selector first, then applies line filters or parsers. Prefer a bounded selector such as `{service="inference-api", environment="local"}` over an unrestricted query. Loki's label-focused indexing is a different trade-off from systems that index arbitrary text; it rewards good label discipline and selective time ranges.

Basic query examples (syntax is version-sensitive; verify against the chosen Loki release):

```logql
{service="inference-api", environment="local"}
{service="inference-api", level="ERROR"} |= "timeout"
{service="batch-etl"} | json | quality_status = "failed"
```

A log query returns matching lines. A metric query derives a numeric series from logs, for example a count or rate over a time window. Do not treat a metric query's zero as interchangeable with a missing stream or a failed query.

#### 4.3.3 First local inspection

After Loki is running, open Grafana Explore, select the configured Loki datasource, choose a short time range, select `{service="log-canary", environment="local"}`, and search for the known canary message. If no event appears, check in this order: time range/timezone, datasource connection, Loki health, label selector, source emission, collector path and exporter errors. Do not immediately widen the query to all logs; first collect discriminating evidence.

Visualization expectations: event timestamp should be UTC; level should be readable; identifiers remain searchable in the body; the stream labels remain bounded. A valid absence of events can be normal, but an expected canary missing from its declared window is a pipeline signal.

#### 4.3.4 Common mistakes and verification

- Mistake: label every field. **Why wrong:** unique identifiers create distinct streams and indexing overhead. Verify stream labels from returned entries and query label browser.
- Mistake: rely only on `kubectl logs`. **Why wrong:** rotation, restarts, and node loss can remove history. Verify by emitting a canary and querying Loki after restart.
- Mistake: log sensitive content and “fix it later.” **Why wrong:** downstream redaction cannot retract copies already ingested or exported. Verify with synthetic sensitive-looking test strings and inspect the stored result.
- Mistake: assume Compose and WSL2 expose `/var/log/containers`. **Why wrong:** paths depend on runtime and environment. Verify actual mounts and permissions on the selected platform.

### 4.4 Level 2 — Intermediate

#### 4.4.1 Local Core + Logs profile

**[ASSUMPTION]** Use Docker Compose on WSL2 Ubuntu as the primary lab because it keeps the exercise local and avoids requiring a second cluster. A small `kind` cluster is an alternative, not a second requirement. Use short retention, one Loki process, synthetic events only, and no external services. Measure your actual CPU, RAM and disk use; there is no universal footprint figure.

The snippets below are teaching artifacts. Confirm exact image tags, Loki configuration fields, schema/store settings, OTLP ingestion path, Collector distribution and component availability before running them. Do not replace `[VERIFY]` with an arbitrary latest tag. The example network is private to the Compose project; publish only Grafana on loopback. Loki and Collector need not publish host ports.

**Example repository-relative layout for copying later (not created by this lesson):**

```text
lab/loki-logs/
├── compose.yaml
├── loki/loki.yaml
├── collector/collector.yaml
├── app/logging_setup.py
├── app/emit_sample.py
├── fixtures/log-corpus.jsonl
├── tests/test_redaction.py
├── tests/test_log_schema.py
└── scripts/check_canary.py
```

#### 4.4.2 Loki configuration — illustrative, release verification required

`lab/loki-logs/loki/loki.yaml`

```yaml
# [VERIFY] Validate every field against the exact pinned Loki release.
# Lab-only: filesystem storage, one replica, short retention.
auth_enabled: false
server:
  http_listen_port: 3100
  grpc_listen_port: 9096
common:
  path_prefix: /loki
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
schema_config:
  configs:
    - from: "2024-04-01"
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
storage_config:
  filesystem:
    directory: /loki/chunks
compactor:
  working_directory: /loki/compactor
  retention_enabled: true
  delete_request_store: filesystem
limits_config:
  retention_period: 168h
```

This is intentionally tagged `[VERIFY]`: Loki releases have changed recommended configuration and schema defaults; `from` dates must be appropriate to the actual deployment and existing data. Do not reuse a schema date casually on a populated instance. If the chosen release requires additional retention, index, cache, or delete-store fields, add them only after checking the exact release's configuration reference. The local lab may be recreated from scratch; production data cannot.

#### 4.4.3 Compose integration

`lab/loki-logs/compose.yaml`

```yaml
# [VERIFY] Pin supported versions/digests after consulting official release pages.
# Grafana is loopback-only; Loki/Collector are not host-published.
services:
  loki:
    image: grafana/loki:${LOKI_VERSION:?set_verified_LOKI_VERSION}
    command: ["-config.file=/etc/loki/loki.yaml"]
    volumes:
      - ./loki/loki.yaml:/etc/loki/loki.yaml:ro
      - loki-data:/loki
    networks: [logs-lab]
    restart: unless-stopped

  collector:
    image: otel/opentelemetry-collector-contrib:${COLLECTOR_VERSION:?set_verified_COLLECTOR_VERSION}
    command: ["--config=/etc/otelcol-contrib/config.yaml"]
    volumes:
      - ./collector/collector.yaml:/etc/otelcol-contrib/config.yaml:ro
      - ./fixtures:/var/log/lab:ro
    depends_on: [loki]
    networks: [logs-lab]
    restart: unless-stopped

  grafana:
    image: grafana/grafana:${GRAFANA_VERSION:?set_verified_GRAFANA_VERSION}
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      # Lab-only bootstrap values; use a disposable value, never a real password.
      GF_SECURITY_ADMIN_USER: lab-admin
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_LAB_PASSWORD:?set_disposable_GRAFANA_LAB_PASSWORD}
      GF_AUTH_ANONYMOUS_ENABLED: "false"
    networks: [logs-lab]
    depends_on: [loki]
    restart: unless-stopped

networks:
  logs-lab:
    internal: true

volumes:
  loki-data:
```

`internal: true` behavior and image startup arguments should be checked for the selected Compose/runtime. A local Grafana datasource can point to `http://loki:3100` from inside the Compose network. Configure that datasource through the already-taught Unit 3 approach; this unit does not rewrite dashboard provisioning. Set `LOKI_VERSION`, `COLLECTOR_VERSION`, `GRAFANA_VERSION`, and a disposable lab password in the shell environment or an ignored local env file. Never commit the actual values or any credentials. Do not publish Loki port 3100 to the host for this lab.

Representative checks (not run here):

```bash
# Review the resolved configuration without exposing a real secret in terminal history.
docker compose -f lab/loki-logs/compose.yaml config
docker compose -f lab/loki-logs/compose.yaml up -d loki grafana collector
docker compose -f lab/loki-logs/compose.yaml ps
curl --fail --silent --show-error http://127.0.0.1:3100/ready
```

The final `curl` is not expected to work because Loki's port is intentionally not published. Use a one-off command inside the Compose network or `docker compose exec` with an available HTTP client, and verify the exact readiness endpoint for the selected release `[VERIFY]`. Do not weaken network isolation merely to make the host check convenient.

#### 4.4.4 Collector pipeline — supported path must be confirmed

The intended path is a filelog receiver reading a **synthetic mounted fixture** and an OTLP/HTTP exporter sending logs to Loki's supported OTLP endpoint. The Collector distribution must include the filelog receiver and processors shown below. The exact OTLP endpoint and mapping of resource attributes to Loki labels must be checked against the selected Loki release. No direct Loki exporter is assumed.

`lab/loki-logs/collector/collector.yaml`

```yaml
# [VERIFY] Validate component names and OTTL syntax against the pinned contrib build.
receivers:
  filelog/lab:
    include: [/var/log/lab/log-corpus.jsonl]
    start_at: beginning
    operators:
      - type: json_parser
        timestamp:
          parse_from: attributes.timestamp
          layout: '%Y-%m-%dT%H:%M:%S.%LZ'
        severity:
          parse_from: attributes.level

processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 256
  transform/redact:
    error_mode: ignore
    log_statements:
      - context: log
        statements:
          # [VERIFY] Test OTTL expression against the exact Collector version.
          - replace_pattern(body, '(?i)(token|authorization)[=: ]+[^ ,"]+', '$$1=[REDACTED]')
  batch:
    timeout: 2s
    send_batch_size: 128

exporters:
  otlphttp/loki:
    # [VERIFY] Confirm endpoint base/path and OTLP log ingestion support for this Loki release.
    endpoint: http://loki:3100/otlp
    tls:
      insecure: true

service:
  pipelines:
    logs:
      receivers: [filelog/lab]
      processors: [memory_limiter, transform/redact, batch]
      exporters: [otlphttp/loki]
```

This is a configuration exercise, not a promise that every release accepts these exact fields. In particular, verify the `filelog` parser's attribute paths, timestamp layout, transform expression syntax and OTLP endpoint composition. A startup validation failure is useful evidence; do not “fix” it by removing memory protection or redaction. If the selected Collector build lacks a component, choose a documented distribution that includes it and record the exact release. Persistent queue configuration is intentionally omitted here because its supported storage extension and semantics must be verified; therefore this example does **not** claim durable buffering across Collector restarts.

**Input-path honesty:** Compose does not universally expose container runtime log files at `/var/log/containers`. This lab mounts a synthetic fixture into the Collector. To collect actual app container logs, verify the runtime-specific file path, mount read-only access with least privilege, test rotation and permissions, and avoid duplicate collection. For `kind`, host/node paths and mounts vary; do not copy a host path without inspecting the node image and runtime.

#### 4.4.5 Structured application logger and safe redaction

`lab/loki-logs/app/logging_setup.py`

```python
"""Small standard-library JSON logger; lab-only, no network delivery."""
from __future__ import annotations
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

SENSITIVE_PATTERNS = [
    (re.compile(r"(?i)(authorization\s*[:=]\s*)(bearer\s+)?[^\s,;]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(token\s*[:=]\s*)[^\s,;]+"), r"\1[REDACTED]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[EMAIL_REDACTED]"),
]

def redact_text(value: str) -> str:
    for pattern, replacement in SENSITIVE_PATTERNS:
        value = pattern.sub(replacement, value)
    return value[:4000]  # bounded message; truncation is an explicit lab policy

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        event: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "service": getattr(record, "service", "inference-api"),
            "environment": "local",
            "message": redact_text(record.getMessage()),
            "schema_version": 1,
        }
        for key in ("route", "request_id", "trace_id", "release", "duration_ms", "error_code", "run_id", "quality_status"):
            if hasattr(record, key):
                value = getattr(record, key)
                if isinstance(value, (str, int, float, bool)) or value is None:
                    event[key] = redact_text(value) if isinstance(value, str) else value
        if record.exc_info:
            # Avoid serializing arbitrary request data. Keep a bounded, redacted exception string.
            event["exception"] = redact_text(self.formatException(record.exc_info))
        return json.dumps(event, ensure_ascii=False, separators=(",", ":"))

def configure_logging() -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("lab-app")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
```

`lab/loki-logs/app/emit_sample.py`

```python
import logging
from logging_setup import configure_logging

log = configure_logging()
log.info("request completed", extra={
    "service": "inference-api", "route": "/v1/predict", "request_id": "req-synthetic-0007",
    "trace_id": "trace-synthetic-0007", "release": "dev-1", "duration_ms": 42.5,
})
log.warning("retry scheduled", extra={"service": "queue-worker", "error_code": "RETRY_SCHEDULED"})
log.error("upstream timeout token=FAKE_TOKEN_DO_NOT_USE", extra={
    "service": "inference-api", "route": "/v1/predict", "request_id": "req-synthetic-0008",
    "error_code": "UPSTREAM_TIMEOUT", "duration_ms": 412.7,
})
```

The logger is a minimal example, not a complete FastAPI middleware. In an actual service, attach a bounded route template rather than the raw URL, generate/propagate a request ID under a documented policy, and add trace/span context only when tracing is configured. Never log headers, bodies, cookies or arbitrary user payloads. Regex redaction is defense in depth and cannot reliably recognize every secret format.

`lab/loki-logs/fixtures/log-corpus.jsonl`

```jsonl
{"timestamp":"2026-10-28T12:00:00.000Z","level":"INFO","service":"inference-api","environment":"local","message":"request completed","route":"/v1/predict","request_id":"req-synthetic-0001","trace_id":"trace-synthetic-0001","release":"dev-1","duration_ms":42.5,"schema_version":1}
{"timestamp":"2026-10-28T12:00:01.000Z","level":"WARN","service":"queue-worker","environment":"local","message":"retry scheduled","error_code":"RETRY_SCHEDULED","run_id":"run-synthetic-01","schema_version":1}
{"timestamp":"2026-10-28T12:00:02.000Z","level":"ERROR","service":"inference-api","environment":"local","message":"upstream timeout","route":"/v1/predict","request_id":"req-synthetic-0002","trace_id":"trace-synthetic-0002","duration_ms":412.7,"error_code":"UPSTREAM_TIMEOUT","schema_version":1}
{"timestamp":"2026-10-28T12:00:03.000Z","level":"INFO","service":"batch-etl","environment":"local","message":"batch completed","run_id":"run-synthetic-02","rows_processed":1200,"quality_status":"passed","schema_version":1}
{"timestamp":"2026-10-28T12:00:04.000Z","level":"INFO","service":"log-canary","environment":"local","message":"heartbeat","canary_id":"canary-synthetic-0004","schema_version":1}
{"timestamp":"2026-10-28T12:00:05.000Z","level":"ERROR","service":"inference-api","environment":"local","message":"authorization: Bearer FAKE_TOKEN_DO_NOT_USE alice@example.invalid","route":"/v1/predict","request_id":"req-synthetic-0005","schema_version":1}
{"timestamp":"2026-10-28T12:00:06.000Z","level":"ERROR","service":"inference-api","environment":"local","message":"synthetic multiline exception start","request_id":"req-synthetic-0006","schema_version":1}
{"timestamp":"2026-10-28T12:00:06.001Z","level":"ERROR","service":"inference-api","environment":"local","message":"  at synthetic_function (example.py:12)","request_id":"req-synthetic-0006","schema_version":1}
```

The corpus intentionally includes a fake token/email-like string to test redaction; it is not a real credential or personal record. The filelog parser and transform examples above must be tested to confirm the secret is removed from the **exported event**, not merely from the console output.

#### 4.4.6 Redaction tests

`lab/loki-logs/tests/test_redaction.py`

```python
import unittest
from app.logging_setup import redact_text

class RedactionTests(unittest.TestCase):
    def test_fake_bearer_token_removed(self):
        result = redact_text("authorization: Bearer FAKE_TOKEN_DO_NOT_USE")
        self.assertNotIn("FAKE_TOKEN_DO_NOT_USE", result)
        self.assertIn("[REDACTED]", result)

    def test_fake_email_removed(self):
        result = redact_text("contact alice@example.invalid")
        self.assertNotIn("alice@example.invalid", result)
        self.assertIn("[EMAIL_REDACTED]", result)

    def test_bounded_message(self):
        self.assertLessEqual(len(redact_text("x" * 5000)), 4000)

if __name__ == "__main__":
    unittest.main()
```

Representative command (not run here): `python -m unittest discover -s lab/loki-logs/tests -v`. False positives can erase useful context; false negatives can miss alternate encodings or secrets split across fields. Test both expected redactions and safe context preservation. Do not infer that a unit test proves the Collector's transform rule is equivalent; test the actual exported/queryable event too.

#### 4.4.7 Multiline exceptions

A logical exception can contain multiple physical lines. Naïvely ingesting each line independently fragments the event and makes searching difficult. Use the selected Collector filelog receiver's documented recombine/multiline operator for the pinned version `[VERIFY]`; configure a start-of-event condition based on the application's stable format, impose a maximum event size and timeout, and test a fixture with two synthetic stack frames. Do not paste an unverified operator configuration as if portable: component operator names and expression syntax are version-sensitive. Acceptance requires one logical exception event with bounded size and safe redaction. The two-line fixture above is only a test input, not proof of recombination.

### 4.5 Level 3 — Advanced

#### 4.5.1 Label cardinality is an operational control

Suppose a synthetic service emits 100 events and each event gets a unique `request_id` label. That can create up to 100 distinct label sets/streams instead of one stream for a fixed `{service="inference-api", environment="local"}` set, subject to other labels and implementation details. This arithmetic is illustrative; it is not a universal stream-to-memory formula. Unique IDs belong in the body so an operator can filter after selecting the stream.

Bad design (do not deploy):

```text
{service="inference-api", request_id="req-synthetic-0001"}
```

Correct design:

```text
{service="inference-api", environment="local"} |= "req-synthetic-0001"
```

Use the Loki label browser or API/query results supported by the selected release to inspect actual labels and streams. Compare a bounded batch of, for example, 20 synthetic IDs—not millions. Record event count, distinct label sets as observed, query response shape and resource use. Label every measured number as a laptop measurement.

#### 4.5.2 LogQL workbook — 22 graded queries

**Contract for this workbook:** the queries use the illustrative label allowlist `{service, environment, level}` and the JSON fields above. Verify exact LogQL syntax against the chosen Loki release and validate every query against the known synthetic corpus. Queries 1–18 return log lines unless described otherwise; metric queries return numeric time series. “Expected shape” is not a claim of live output.

| # / Level | Operational question | Query | Expected result shape and explanation | Common mistake / validation |
|---|---|---|---|---|
| 1 [L1] | Show local inference events. | `{service="inference-api", environment="local"}` | Matching log lines in time order. | Empty if the selector/time range does not match; verify labels first. |
| 2 [L1] | Find errors. | `{service="inference-api", level="ERROR"}` | Error-labelled stream lines, if `level` is actually a stream label. | If `level` is only a body field, parse/filter JSON instead; verify label contract. |
| 3 [L1] | Find timeout text. | `{service="inference-api"} |= "timeout"` | Lines containing case-sensitive text `timeout`. | Search is not a general full-text index; constrain the stream/time range. |
| 4 [L1] | Exclude routine health checks. | `{service="inference-api"} != "health check"` | Lines not containing that literal. | Do not apply a filter without checking it preserves incident-relevant lines. |
| 5 [L2] | Parse JSON and find a failed batch. | `{service="batch-etl"} | json | quality_status = "failed"` | Parsed log lines with the requested field value. | Parser fails on malformed JSON; validate a known fixture. |
| 6 [L2] | Find one synthetic request ID. | `{service="inference-api"} |= "req-synthetic-0002"` | Lines whose body contains that ID. | Do not convert the ID into a stream label. |
| 7 [L2] | Count error lines in five minutes. | `sum(count_over_time({service="inference-api", level="ERROR"}[5m]))` | One numeric series for matching error lines over rolling windows. | Requires `level` label and a metric-query context; verify parser/label placement. |
| 8 [L2] | Estimate error-line rate. | `sum(rate({service="inference-api", level="ERROR"}[5m]))` | Numeric rate of matching log entries over the window. | This is a log-entry rate, not automatically an application error ratio. |
| 9 [L2] | Count errors by service. | `sum by (service) (count_over_time({environment="local", level="ERROR"}[5m]))` | Numeric series grouped by bounded `service`. | Do not group by request IDs or arbitrary message text. |
| 10 [L2] | Count warning lines by level. | `sum by (level) (count_over_time({environment="local", level=~"WARN|ERROR"}[5m]))` | Numeric series for bounded levels. | Confirm level is a label and regex syntax for the pinned release. |
| 11 [L2] | Count batch completions. | `sum(count_over_time({service="batch-etl"} |= "batch completed" [15m]))` | Count series for the selected line text. | Keep selector bounded and verify whitespace/syntax in LogQL editor. |
| 12 [L2] | Find failed quality outcomes in JSON. | `{service="batch-etl"} | json | quality_status = "failed"` | Matching events with parsed field. | Do not expect absent field to equal `failed`. |
| 13 [L2] | Find slow requests (illustrative threshold). | `{service="inference-api"} | json | duration_ms > 250` | Lines with parsed numeric duration over 250 ms. | Threshold is lab-only, not an SLO; confirm field parsed as number. |
| 14 [L2] | Extract latency distribution (verify syntax). | `avg_over_time(({service="inference-api"} | json | unwrap duration_ms)[5m])` | Numeric average of extracted durations if syntax/version and field type are valid. | This is an average of logged durations, not p95; validate `unwrap`/range syntax `[VERIFY]`. |
| 15 [L2] | Search trace ID in body. | `{service="inference-api"} |= "trace-synthetic-0002"` | Correlated log lines containing the ID. | A trace link needs a configured trace datasource; correlation is not causality. |
| 16 [L2] | Compare releases. | `{service="inference-api", release="dev-1"}` | Lines for the bounded release label if `release` is allowed as a label. | In this contract `release` is body-only by default; parse JSON instead unless deliberately approved as a bounded label. |
| 17 [L2] | Find redaction failures. | `{environment="local"} |= "FAKE_TOKEN_DO_NOT_USE"` | Ideally no results after redaction. | No results alone is not proof; compare source fixture, exported event and query time range. |
| 18 [L2] | Find canary heartbeat. | `{service="log-canary"} |= "heartbeat"` | Expected synthetic heartbeat lines. | Missing heartbeat requires an expected-event schedule/window, not just an empty search. |
| 19 [L3] | Top error text patterns (bounded time). | `topk(5, sum by (service) (count_over_time({environment="local", level="ERROR"}[15m])))` | Top five services by error-line count, not top messages. | Grouping by arbitrary message text can create high-cardinality query results; this query deliberately groups by service. |
| 20 [L3] | Find noisy health-check events. | `sum by (service) (count_over_time({environment="local"} |= "health check" [5m]))` | Numeric count grouped by service. | Do not filter them out until confirming the filter cannot hide a meaningful incident signal. |
| 21 [L3] | Count events for a release in body. | `sum(count_over_time({service="inference-api"} | json | release="dev-1" [15m]))` | Count series for parsed release value if syntax is accepted. | Do not invent a `release` label; validate parser and range-query syntax. |
| 22 [L3] | Check for missing canary conceptually. | `sum(count_over_time({service="log-canary"} |= "heartbeat" [2m]))` | Zero/absent numeric result can indicate no matching heartbeat in the window. | Alert/check logic must distinguish no series, query error, and valid zero; test with an independent expected schedule. |

**Important query notes:** Query 2 and queries using `level` as a selector require it to be a stream label; the sample contract permits `level` only if intentionally included in the bounded label set. Otherwise use `{service="inference-api"} | json | level="ERROR"`. Query 16 intentionally demonstrates the mismatch between the default body schema and a label selector; use the corrected body-parsing form. `unwrap`, range aggregation and parser error behavior are version-sensitive. Do not present query 14 as a percentile; percentile calculations should normally use metrics/histograms from Unit 2, not averages of log durations.

Inefficient query shape:

```logql
{} |~ ".*timeout.*" | json | request_id != ""
```

Improved shape:

```logql
{service="inference-api", environment="local"} |= "timeout" | json | error_code="UPSTREAM_TIMEOUT"
```

The improvement comes from narrowing the stream selector, using a literal line filter before parsing where suitable, and parsing only after reducing candidates. Compare query plans/requests and local resource behavior; do not invent a wall-clock speedup.

#### 4.5.3 Query and ingestion reliability trade-offs

| Decision | Options | Benefit | Cost/risk | Choose when |
|---|---|---|---|---|
| Collection topology | node agent / sidecar / gateway | Node agent sees many container logs; gateway centralizes processing. | Permissions, duplication, resource contention and larger blast radius. | Match access model, workload density and failure isolation. |
| Parse timing | edge parse / query-time parse | Edge normalization simplifies queries; query-time parse preserves flexibility. | Edge CPU/config coupling versus repeated query CPU and parse failures. | Parse stable fields at edge; keep exploratory fields in body. |
| Field placement | stream label / body / structured metadata | Labels narrow streams; body preserves high-cardinality context. | Label explosion; metadata support is version-dependent. | Only bounded, frequently filtered dimensions belong in labels. |
| Noise control | source suppression / Collector filter / retention | Source suppression reduces generation; filters reduce downstream volume. | May lose forensic evidence; filters can be misconfigured. | Keep audit/security events unless approved policy explicitly says otherwise. |
| Storage | local filesystem / object storage | Filesystem is simple for lab; object storage supports larger deployments. | Local disk failure/capacity versus additional distributed operations. | Filesystem for disposable local learning; production choice requires tested durability. |
| Outage handling | retry queue / bounded drop / persistent queue | Retries can recover transient outages. | Duplicates, memory pressure, replay and loss windows. | Bound memory and document persistence semantics. |
| Deployment | monolithic / distributed | Monolithic is simpler; distributed separates scale/failure domains. | Monolithic limits scale; distributed increases operational complexity. | Local laptop monolithic; production topology based on measured load and availability goals. |
| Log format | structured / unstructured | Structured fields support consistent parsing and redaction. | Schema discipline and compatibility work. | Structured format for application events; retain safe raw context when useful. |

#### 4.5.4 Retention and data-volume worksheet

Measure rather than guess. For a controlled test, record:

- emitted events/s = counted synthetic events / elapsed seconds;
- raw bytes/s = bytes written / elapsed seconds;
- estimated raw bytes/day = bytes/s × 86,400;
- measured on-disk growth = storage-directory size after the test minus baseline size;
- approximate compression ratio = raw bytes / measured stored bytes for the same interval, only if the measurement boundaries are comparable;
- distinct stream count as observed from the selected release's supported inspection path;
- query duration and resource usage for a fixed query/range;
- configured retention period and observed expiration timing.

These measurements are laptop-specific. Compression, indexing, replication, labels, query patterns and filesystem overhead change the result. Do not extrapolate a short synthetic test into production capacity promises. Keep debug logs shorter-lived only when the retention policy and evidence requirements explicitly permit it. Audit/security logs must not be sampled or dropped without documented approval.

### 4.6 Level 4 — Expert

#### 4.6.1 Prove end-to-end delivery, not just component health

Use a synthetic canary with a stable event ID in the **body**. The path to prove is:

1. emitter reports that it attempted to write event ID `canary-synthetic-0007`;
2. runtime/file source contains the line;
3. Collector receiver read/offset evidence shows the source was consumed;
4. processor logs/metrics show no unexpected drop or parse failure;
5. exporter shows successful send or a recorded retry/failure;
6. Loki accepts the entry;
7. a bounded LogQL query finds the ID within the declared window.

No single component's “healthy” status proves all stages succeeded. Duplicates can arise from retries/restarts; events can be delayed by buffering; filtering can intentionally remove an event; timestamps can make an entry appear outside the expected window. Record emitted, found, duplicate and late counts separately. Do not claim exactly-once delivery.

`lab/loki-logs/scripts/check_canary.py` — a simple local corpus check (it does not query Loki):

```python
import json
import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "lab/loki-logs/fixtures/log-corpus.jsonl")
expected = sys.argv[2] if len(sys.argv) > 2 else "canary-synthetic-0004"
found = False
for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
    try:
        event = json.loads(line)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"INVALID_JSON line={line_no}: {exc}")
    if expected in json.dumps(event, ensure_ascii=False):
        found = True
if not found:
    raise SystemExit(f"MISSING_CANARY expected={expected}")
print(f"CANARY_PRESENT expected={expected}")
```

This local file check is only the source-stage test. A separate query through Grafana Explore must establish backend arrival. For a scheduled canary, keep expected cadence and allowed lateness explicit; a quiet application does not imply missing telemetry, but a missing canary violates the event contract.

#### 4.6.2 Outage and recovery semantics

When Loki is unavailable, the application should continue serving requests even if remote logging fails. Depending on the configured pipeline, the Collector may retry, buffer in memory, use a persistent queue, or eventually drop entries; the runtime may retain source files for a limited time. Each mechanism has distinct loss and duplicate windows. A bounded in-memory queue can be lost on restart; a persistent queue needs a verified storage extension and disk budget. Do not add an unbounded queue to “solve” loss.

Safe outage drill: stop only the named disposable `loki` Compose service, emit a small fixed number of synthetic canaries, observe Collector/application behavior, restart Loki, then query the expected IDs. Do not stop host logging, alter system logs, or delete volumes as a troubleshooting shortcut. Document the missing, late, and duplicated IDs. If the chosen configuration cannot reveal whether a record was accepted, mark that as an observability gap.

#### 4.6.3 Operations, migration and governance

- Pin Loki, Grafana and Collector versions only after checking their official release pages. Read migration notes before changing Loki schema or storage configuration.
- Back up the config and any state required by the deployment; test restore and query compatibility in a disposable environment before promoting.
- Keep a service logging contract: required fields, allowed levels, label allowlist, sensitive-field prohibition, maximum message/event size, owner, retention class and exception process.
- Use config-as-code review for pipeline config, redaction rules, label changes and retention. A label change can alter stream identity and query behavior; treat it as a data-model migration.
- Multi-tenancy and tenant headers are not a substitute for an authenticated access boundary. Verify the chosen Loki architecture's native capabilities and use an auth proxy/platform boundary where required. Never rely on labels as authorization.
- If arbitrary full-text search across large bodies is a hard requirement, evaluate a full-text indexing system as a separate design decision. Loki's label-first model often trades arbitrary search flexibility for a different indexing/storage profile; compare actual query patterns, storage, operations, and governance rather than assuming one system is universally superior.

#### 4.6.4 Incident analyses

Each example is **[SYNTHETIC]** and follows symptom → hypothesis → discriminating test → root cause → fix → prevention.

1. **Debug logs fill disk.** Symptom: filesystem free space falls during a verbose run. Hypothesis: debug volume exceeds retention/rotation assumptions. Test: compare generated bytes/s, runtime log size, and Loki disk growth during a bounded interval. Root cause only established if byte counts correlate. Fix: restore intended level, set bounded rotation/retention, and preserve relevant errors. Prevention: volume budget and alert on disk growth.
2. **`request_id` label explodes streams.** Symptom: distinct stream count grows with request volume. Test: inspect labels and compare a bounded set of IDs. Fix: move ID into body/structured metadata. Prevention: label allowlist lint.
3. **Rotation precedes collection.** Symptom: source has emitted IDs that are absent downstream. Test: compare temporary source files, receiver offsets and collector errors. Fix: correct safe file access/checkpoint behavior and rotation assumptions. Prevention: test rotation under synthetic load.
4. **Token logged at INFO.** Symptom: fake secret is queryable. Test: search for the exact synthetic token in source and stored event. Fix: stop logging it, rotate any real credential through the incident process if applicable, restrict access and follow retention/deletion policy. Prevention: source-level allowlist logging and redaction tests.
5. **Collector crash loop.** Symptom: canary gaps align with Collector restarts. Test: inspect process logs, restart count and source offsets. Fix: correct config/resource issue and recover available source logs. Prevention: config validation and independent collector health checks.
6. **Clock skew.** Symptom: event appears outside the expected range or is rejected. Test: compare application timestamp, collector observation and system clock. Fix: synchronize clocks and apply a documented timestamp policy. Prevention: UTC and skew checks.
7. **Log-string alert breaks.** Symptom: event wording changes and match stops. Test: compare old/new fixture strings. Fix: alert on a stable structured code or metric when possible. Prevention: contract tests and metric-first alerts.
8. **Multiline exception fragments.** Symptom: stack frames appear as separate events. Test: run the two-line fixture through the exact operator config. Fix: configure verified recombine logic with bounds. Prevention: regression fixture.
9. **Ingestion limits reached.** Symptom: Collector reports export failures and Loki reports rejection. Test: inspect actual rejection reason and active limits in the selected release. Fix: reduce noise or revise an approved limit based on measurements. Prevention: bounded labels/volume and limit monitoring.
10. **Broad query is slow.** Symptom: query latency rises after removing selectors. Test: narrow time range, selector, then add parsing step by step. Fix: selective labels and early literal filters. Prevention: query review and saved examples.
11. **Retention misbehaves.** Symptom: expired entries persist or evidence disappears early. Test: check policy, timestamps, compactor health, configuration and release-specific deletion semantics. Fix: restore correct policy and preserve evidence as authorized. Prevention: scheduled retention test and backup/DR runbook.
12. **Redaction bypass.** Symptom: fake secret is stored despite a configured processor. Test: inspect source, post-processor event and query result. Fix: correct rule/ordering and stop source emission. Prevention: integration tests and fail-closed policy where supported.
13. **Outage overwhelms queue.** Symptom: memory rises while Loki is down. Test: observe queue behavior and Collector memory during a bounded stop. Fix: bound queue, set memory controls, decide explicitly on persistence/drop. Prevention: tested outage budget.
14. **Service names disagree.** Symptom: metric/log/trace views cannot correlate. Test: compare emitted `service`, resource attributes and dashboard selectors. Fix: normalize mapping at source/processor. Prevention: shared service naming contract.
15. **Health filter drops evidence.** Symptom: relevant error during a health check is absent. Test: replay synthetic normal and error lines through filter. Fix: narrow the filter or remove it. Prevention: positive/negative filter fixtures and explicit audit/security exclusions.

#### 4.6.5 Required troubleshooting matrix

Use this matrix as a first-pass discriminator, not a substitute for evidence. Capture UTC time range, exact selector, component versions and sanitized errors. Root cause remains a hypothesis until the discriminating test supports it.

| Symptom | First check | Evidence | Likely cause | Discriminating test | Fix | Prevention |
|---|---|---|---|---|---|---|
| 1. No logs appear in Loki | Query a known canary with a short range | Source event ID, Collector and Loki logs | Broken stage or wrong query | Trace one ID source-to-query | Repair the failing stage | Scheduled canary |
| 2. One service is absent | Confirm exact service name and source path | Labels, file list, receiver diagnostics | Naming/path mismatch | Emit a synthetic event from that service | Normalize names/path access | Contract test |
| 3. JSON fields cannot be queried | Inspect raw line and parser errors | Raw synthetic line and parsed result | Invalid JSON or parser mapping | Run known valid/malformed fixtures | Fix schema/operator mapping | Schema lint gate |
| 4. `trace_id`/`request_id` is a label | Inspect actual stream labels | Label set and bounded event count | Label allowlist violation | Compare before/after with ID in body | Remove identifier from labels | Config lint and review |
| 5. Loki rejects entries | Inspect Loki/Collector errors | Rejection reason and timestamp | Limit, size, tenant or ordering rule | Send one bounded valid fixture | Correct input/policy after verification | Monitor rejection signals |
| 6. Entries appear outside expected range | Check event timestamp and timezone | Source timestamp and query range | Clock/range mismatch | Search a wider bounded interval and compare UTC | Fix timestamp/timezone mapping | UTC contract tests |
| 7. Clock skew/out-of-order behavior | Compare host/app timestamps | Clock offsets and rejection logs | Unsynchronized clock or timestamp policy | Emit controlled timestamps if safe | Synchronize clock; verify release policy | Clock health checks |
| 8. Multiline exception splits | Inspect individual lines | Fixture and stored entries | No supported recombine operator configured | Replay two-line synthetic fixture | Configure verified bounded multiline handling | Regression fixture |
| 9. Redaction misses fake secret | Search for exact fake marker | Source, processed and stored event | Rule mismatch/order/field not covered | Run integration test through full pipeline | Correct rule and source logging | Secret-pattern test suite |
| 10. Redaction removes too much | Compare safe context before/after | Sanitized fixture diff | Over-broad regex | Test benign strings adjacent to token-like text | Narrow rule and preserve safe fields | False-positive tests |
| 11. Collector cannot read path | Inspect mount and file permissions | `docker compose config`, mount/path listing | Wrong platform path or permissions | Read one temporary mounted file | Use verified path and least privilege | Runtime-specific setup check |
| 12. Queue fills during outage | Inspect Collector errors/resources | Queue status if available, memory trend | Loki down or throughput mismatch | Short bounded Loki stop | Bound queue; decide retry/drop/persistence | Outage drill and capacity worksheet |
| 13. Logs duplicate after restart | Count occurrences by body ID | Source IDs and downstream occurrence counts | Retry/replay or file offset reset | Compare a fixed set before/after restart | Deduplicate downstream only if designed; correct offsets | Document at-least-once possibility |
| 14. Rotation/restart loses logs | Compare synthetic source files and found IDs | File names, offsets, source event list | Rotation before receiver read | Rotate only temporary test file | Adjust safe rotation/checkpoint approach | Rotation test |
| 15. Query is slow | Reduce time range and selector first | Query, range, response/errors | Broad selector, regex or early parsing | Add one filter/parser at a time | Narrow selector and parse only needed fields | Query review standard |
| 16. Log alert stops matching | Compare event structure across release | Old/new synthetic message | Wording-dependent expression | Replay both message variants | Use stable error code or metric | Alert fixture tests |
| 17. Debug volume is excessive | Measure emitted bytes/s | Level config, bytes and disk trend | Verbose level or repeated messages | Fixed-duration bounded run | Restore level and apply approved noise policy | Volume budget and review |
| 18. Retention too long/short | Inspect policy and record timestamps | Config, compactor diagnostics, query result | Misconfigured policy or asynchronous deletion | Synthetic expiry test for pinned release | Correct verified retention settings | Periodic retention test |
| 19. App slows when Loki is down | Check whether request path waits on logging | Request timings and app/Collector logs | Synchronous remote logging or unbounded back-pressure | Short local outage with bounded traffic | Decouple remote export; bound queues/timeouts | Dependency isolation test |
| 20. Metrics/logs/traces do not correlate | Compare service name and UTC timestamp | Metric labels, log fields, trace resource | Naming/timestamp mapping mismatch | Follow one synthetic request ID/trace ID | Normalize contract/mapping | Cross-signal contract test |
| 21. Loki self-metric missing/renamed | Inspect current `/metrics` output and docs | Exported metric names and release | Version change or metric not enabled | Compare exact pinned release docs/runtime | Update dashboard/check after review | Version upgrade tests |
| 22. Collector component unsupported | Validate config against actual binary | Startup error and component inventory | Wrong distribution or component name | Inspect pinned distribution docs | Select supported build or documented component | Pin and validate image |
| 23. Stream/label limit exceeded | Inspect rejection and label set | Actual limit error and labels | Too many streams or unbounded values | Reproduce with a small bounded ID set | Remove unbounded labels; adjust approved limit if needed | Label allowlist lint |
| 24. Canary missing but routine logs exist | Search exact expected canary ID | Schedule, source emission, query | Canary path differs or event filtered/late | Trace the specific canary through stages | Repair canary path and alert on arrival | Independent scheduled canary |
| 25. Audit/security lines filtered | Inspect filter config and synthetic fixture | Before/after safe test event | Broad noise filter | Replay an approved synthetic audit-like event | Remove exclusion unless explicitly approved | Protected-event regression tests |

#### 4.6.6 Standard-library JSON log-schema linter

This lightweight linter validates the **lab event contract**, not every possible event or the Collector pipeline. Regex-based detection is incomplete and may produce false positives/negatives. Run it on synthetic fixtures only; extend required fields deliberately rather than accepting malformed data silently.

`lab/loki-logs/tests/test_log_schema.py`

```python
import json
import re
import unittest
from datetime import datetime

REQUIRED = {"timestamp", "level", "service", "environment", "message", "schema_version"}
ALLOWED_LEVELS = {"DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"}
PROHIBITED_LABEL_KEYS = {"trace_id", "span_id", "request_id", "user_id", "run_id", "partition_id", "email", "url"}
SECRET_MARKERS = ("FAKE_TOKEN_DO_NOT_USE", "password=", "authorization: bearer")


def validate_event(line: str) -> list[str]:
    errors: list[str] = []
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return ["invalid_json"]
    if not isinstance(obj, dict):
        return ["event_not_object"]
    missing = REQUIRED - obj.keys()
    if missing:
        errors.append("missing_required:" + ",".join(sorted(missing)))
    if obj.get("level") not in ALLOWED_LEVELS:
        errors.append("invalid_level")
    ts = obj.get("timestamp")
    if not isinstance(ts, str) or not ts.endswith("Z"):
        errors.append("timestamp_must_be_utc_z")
    else:
        try:
            datetime.fromisoformat(ts[:-1] + "+00:00")
        except ValueError:
            errors.append("invalid_timestamp")
    for key in PROHIBITED_LABEL_KEYS:
        # These fields may appear in the event body; this check is for a separate
        # declared label map, if supplied, not for legitimate body identifiers.
        labels = obj.get("stream_labels", {})
        if isinstance(labels, dict) and key in labels:
            errors.append("prohibited_stream_label:" + key)
    serialized = json.dumps(obj, ensure_ascii=False).lower()
    for marker in SECRET_MARKERS:
        if marker.lower() in serialized:
            errors.append("sensitive_marker_detected:" + marker)
    if len(line.encode("utf-8")) > 16_384:
        errors.append("event_too_large_for_lab_policy")
    return errors


class LogSchemaTests(unittest.TestCase):
    def test_valid_synthetic_event(self):
        line = json.dumps({"timestamp":"2026-10-28T12:00:00.000Z", "level":"INFO",
            "service":"inference-api", "environment":"local", "message":"ok", "schema_version":1})
        self.assertEqual(validate_event(line), [])

    def test_invalid_json(self):
        self.assertEqual(validate_event('{not-json'), ["invalid_json"])

    def test_missing_fields(self):
        self.assertTrue(any(e.startswith("missing_required:") for e in validate_event('{"level":"INFO"}')))

    def test_fake_secret_marker_detected(self):
        line = json.dumps({"timestamp":"2026-10-28T12:00:00Z", "level":"ERROR",
            "service":"inference-api", "environment":"local", "message":"FAKE_TOKEN_DO_NOT_USE", "schema_version":1})
        self.assertTrue(any(e.startswith("sensitive_marker_detected:") for e in validate_event(line)))

if __name__ == "__main__":
    unittest.main()
```

The linter's `stream_labels` property is a test-only representation; it is not part of the default event contract. Run: `python -m unittest lab.loki-logs.tests.test_log_schema -v` if the path is a valid Python package layout, or use `python -m unittest discover -s lab/loki-logs/tests -p 'test_log_schema.py' -v` from the repository root. Representative output (not run here) should show four passing tests. The linter cannot validate LogQL grammar, Loki acceptance, Collector OTTL behavior, or live label mapping.

### 4.7 SRE lens

#### Pipeline reliability map and indicators

| Stage | What to measure or inspect | Failure mode | Evidence method |
|---|---|---|---|
| Application emitted | synthetic event count, app logging errors, canary schedule | code path never logs or logger drops | emitter counter/log plus source fixture/file |
| Runtime/source read | file growth, rotation, permissions, receiver offsets | inaccessible path or rotated file | source file IDs, receiver diagnostics, mount inspection |
| Processor accepted | parse failures, redaction outcomes, filtered count | malformed input or accidental drop | safe test fixture and Collector diagnostics |
| Exporter sent | send failures, retries, queue utilization | Loki unavailable, timeout, unsupported endpoint | Collector logs/metrics for selected build `[VERIFY]` |
| Loki accepted/stored | request failures, rejected/discarded entries, disk/compactor health | limit rejection, schema/storage issue | Loki logs, documented health endpoint and self-metrics `[VERIFY]` |
| Query returns | canary freshness, query errors, found IDs | wrong labels/time range, query timeout, retention | bounded LogQL query and independent expected schedule |

Use exact metric names only after inspecting the selected release's `/metrics` output or official metric reference. Names such as `loki_discarded_samples_total` are examples of the kind of signal to investigate, not guaranteed names. Collector component metrics also depend on distribution and configuration. Discover available metrics rather than assuming them.

**Pipeline SLIs to define locally:**

- **Canary freshness:** arrival timestamp minus emitter timestamp for each known event ID.
- **Missing-canary fraction:** expected canary IDs not found within the agreed window / expected IDs. State the time window and query limitations.
- **Late-event fraction:** IDs found after the allowed arrival window / expected IDs.
- **Duplicate fraction:** extra occurrences beyond one per expected ID / expected IDs; retries can create duplicates.
- **Exporter failure signal:** failed export attempts or errors from the selected Collector's verified telemetry.
- **Queue utilization:** observed queue occupancy / configured capacity, only where that queue exposes it.
- **Loki request health:** success/failure and latency for relevant endpoints using verified signals.
- **Storage/retention health:** filesystem growth, free disk, compactor status and test data expiration.
- **Query success:** a scheduled known query's success/error and arrival delay, independent of Grafana UI where practical.

No universal target is prescribed. Set objectives based on the incident use case, then record the method and limitations. A quiet service may emit no application events; absence detection requires an explicit canary or expected-event contract. Pipeline health and application health are different dimensions.

#### Runbook: missing log

1. Confirm the exact synthetic event ID and UTC emission time at the source.
2. Inspect the source file/runtime logs and rotation window; prove the line existed.
3. Check receiver file path, permissions, offsets/checkpoints and component errors.
4. Check parsing, enrichment and redaction order; determine whether the event was intentionally filtered.
5. Check exporter retries/queue and whether Loki was reachable; capture error evidence.
6. Check Loki acceptance/rejection/limits, storage health and timestamp policy using verified release-specific diagnostics.
7. Query a short range with a narrow, known label selector; inspect the actual event timestamp and labels.
8. Run the canary check and distinguish missing, late, duplicate, filtered, rejected and query-hidden cases.
9. Restore the pipeline or replay only if the selected mechanism safely supports it; do not claim replay is safe without checking duplication behavior.
10. Save a timeline, redacted configuration, query, evidence IDs and corrective action. Never save sensitive log payloads.

#### Capacity and blast radius

Measure events/s, average bytes/event, bytes/s, disk growth, stream count, query range/latency, Collector resource use and Loki resource use on your own laptop. Grafana being unavailable does not necessarily stop Prometheus scraping or Loki ingestion; the visualization layer can fail while data collection continues. Keep a safe alternate route to critical queries and alerts. If Loki is unavailable, application request handling must not synchronously depend on successful remote log delivery. Bounded retries may delay records; bounded queues may fill; unbuffered delivery may lose records. Document which behavior your chosen configuration actually demonstrates.

### 4.8 Security lens

| Threat | Control | Verification in the lab |
|---|---|---|
| Secret/PII in application logs | source-level allowlist fields; synthetic redaction tests; do not log headers/bodies | inject only `FAKE_TOKEN_DO_NOT_USE`; assert it is absent in formatted output and queried event |
| Log injection/newline/ANSI control | sanitize untrusted text, encode JSON, bound message size, preserve event structure | test newline and escape-like synthetic input; verify it cannot forge a second JSON record |
| Unauthenticated endpoint exposed | bind Grafana to loopback; keep Loki/Collector private to isolated network; production needs verified auth/TLS boundary | inspect `docker compose config`, port mappings and listening sockets |
| Overprivileged Collector mounts/RBAC | read-only narrow mount; least-privilege service account; no cluster permissions unless needed | inspect mounts and RBAC manifests before running |
| Tampered config/component | pin releases, review source-controlled config, use trusted distribution and checksums/digests where available | record image reference and reviewer; inspect diff before promotion |
| Unsafe data links/query inputs | fixed internal links, no credentials in URLs, constrain templating and query access | search config for URL credentials and untrusted interpolation |
| Cross-team unauthorized log access | authenticated gateway/platform access controls; do not rely on labels for security | test access from intended and unauthorized identities in a real secured environment; local lab alone cannot prove production RBAC |
| Tokens in files/CLI/env dumps | disposable values only; secret manager in production; avoid shell tracing and env dumps | scan artifacts for common credential patterns; never paste real secrets into command history |
| Excessive retention / sensitive deletion | documented classes, minimum necessary retention, approved deletion/hold workflow | test expiry using synthetic records and release-specific retention behavior |
| Sensitive debug endpoints/logs | disable unnecessary debug routes; control log level and output | inspect service configuration and run a synthetic secret scan |
| Malformed multiline resource exhaustion | bounded message/event size, multiline timeout and memory limiter | feed a small oversized synthetic fixture and confirm controlled behavior |
| Audit/security records filtered | explicit exclusion list and approved policy; tests assert these records survive | run positive/negative filter fixtures and capture output |
| Forensic evidence altered | restricted access, immutable/append-only storage where required, hashes and access audit outside this lab | record file hash and chain-of-custody procedure; actual immutability needs platform controls |
| Untrusted Collector component | choose supported distribution and review component inventory | compare config components to official distribution documentation for pinned release |

Loki and Collector native access-control features vary by deployment and version. A local monolithic demo with `auth_enabled: false` is safe only because it is isolated and disposable; it is not an acceptable public deployment pattern. Features such as public dashboards, snapshots, anonymous access, multi-tenant headers and native authorization must be checked against the selected Grafana/Loki edition and version. Do not imply paid RBAC features are available in every edition.

**Security verification checklist:** no real secrets or PII in source, fixtures, query URLs, screenshots or evidence; loopback-only Grafana host binding; no host-published Loki/Collector ports; no unnecessary writable host mounts; redaction tested before export; label allowlist enforced; config/image versions recorded; no public sharing/anonymous access enabled; access boundary documented for any non-lab deployment.

### 4.9 Production checklist

- [ ] Each service has an owner and a documented structured logging contract.
- [ ] Timestamps are UTC/RFC 3339 and tested for parsing.
- [ ] Service and environment names are consistent with metrics/traces.
- [ ] Request/trace/run identifiers are in event content, not stream labels.
- [ ] Log messages are bounded; request bodies, headers, tokens and PII are excluded at source.
- [ ] Redaction is tested both in the application formatter and the pipeline/exported event.
- [ ] Collector receiver, processors and exporter are available in the pinned distribution.
- [ ] Runtime paths and rotation behavior were verified on the actual platform.
- [ ] Buffers/queues are bounded and retry/drop/duplicate semantics are documented.
- [ ] Loki configuration, schema, storage and retention match the selected release.
- [ ] A canary checks end-to-end arrival and distinguishes missing from late data.
- [ ] Queries start with bounded selectors and short time ranges.
- [ ] No arbitrary message/ID field is used for grouping or stream labels.
- [ ] Noise filters have fixtures proving relevant errors and audit/security events survive.
- [ ] Retention expiration is tested with synthetic records.
- [ ] Loki/Collector outage recovery has a captured timeline and rollback procedure.
- [ ] Query and pipeline health signals are discovered from the running selected release, not assumed.
- [ ] Access controls, local-only bindings, config review and component provenance are documented.
- [ ] Technical volume/resource measurements are recorded as laptop measurements, not production guarantees.

### 4.10 Hands-on lab set

All labs use the **Core + Logs** profile, synthetic records and local-only services. Measure your footprint; no universal CPU/RAM/disk estimate is asserted. Never run against production or a public endpoint. Commands below are representative and have not been executed here. Exact component versions and configuration must pass the `[VERIFY]` gates before use.

#### Lab A — Deploy Loki and verify the first log [L1–L2]

**Prerequisites:** Docker Compose; a disposable local directory; verified Loki/Grafana image references; the illustrative Loki config and Compose snippet in §4.4. **Safety:** no host-published Loki port; use only synthetic fixtures; no real secrets.

1. Create the directory layout from §4.4.1 and copy the full config artifacts into the shown paths.
2. Verify the Loki configuration against the pinned release's configuration reference. Resolve every `[VERIFY]` item before starting.
3. Set image variables to verified release tags and a disposable Grafana password without committing them.
4. Run `docker compose -f lab/loki-logs/compose.yaml config`, review port mappings and mounts, then start Loki/Grafana.
5. Confirm Loki readiness from inside the Compose network using the documented endpoint for that release. Capture logs and health response; do not publish port 3100 to host.
6. Configure a Loki datasource in local Grafana using Unit 3's datasource procedure, with the internal URL `http://loki:3100`.
7. Load a synthetic log using the chosen verified ingestion path; query a narrow selector in Explore and capture the returned timestamp, labels and body.

**Representative evidence (not run here):** Compose services running; readiness check succeeds; Explore shows `canary-synthetic-0004` with UTC timestamp; datasource URL is internal to the Compose network. **Acceptance:** a known event can be queried; no Loki port is host-published; all image/config versions are recorded. **Cleanup:** stop only this Compose project. Preserve the named `loki-data` volume if retaining evidence; remove it only when intentionally resetting this disposable lab. **Stretch:** restart Loki and verify whether the selected local filesystem storage retains the synthetic event.

#### Lab B — Collector pipeline, structured logging and redaction [L2–L3]

**Prerequisites:** Lab A; Collector distribution with verified components; sample fixture; Python standard library. **Safety:** fake token/email only, bounded fixture, read-only fixture mount.

1. Copy `collector.yaml`, `logging_setup.py`, `emit_sample.py`, fixture and tests from §4.4.
2. Verify the Collector component inventory and configuration syntax using the selected build's supported validation command/documentation. Do not guess CLI flags; register the exact command in the verification record.
3. Run the Python redaction tests. Emit the synthetic events and inspect the formatted JSON.
4. Validate the Collector-side redaction expression against the exact OTTL version. Prove the fake value is absent from the exported/queryable event; a Python unit test alone is insufficient.
5. Test malformed JSON and the two-line stack trace fixture. Add a verified recombine operator and bounded event-size/timeout controls for the selected version.
6. Verify stream labels use only the allowlist; confirm IDs remain in the body.
7. Stop Loki briefly and observe application responsiveness, Collector errors and actual queue behavior; restart and record late/missing/duplicate IDs.

**Evidence:** passing source redaction tests; before/after synthetic event; Collector config validation result; one queried log; label set; multiline test result; outage notes. **Acceptance:** fake secret is not queryable, useful safe context remains, identifiers are not labels, and outage behavior is documented honestly. **Cleanup:** stop the named lab services and remove only temporary synthetic files after saving non-sensitive evidence. **Stretch:** test a redaction false positive and adjust policy without allowing the fake token through.

#### Lab C — LogQL workbook and metric → logs → trace investigation [L1–L3]

**Prerequisites:** a verified Loki datasource and synthetic corpus; Unit 3 service overview dashboard. **Safety:** short time range and bounded query; trace integration optional until Units 5/10.

1. Execute each of the 22 workbook queries against the known corpus, marking syntax/results that require release-specific adjustment.
2. For an error/latency symptom, start from the service dashboard, identify the time window, open Explore with the same range, narrow by `service`/`environment`, filter the error, parse safe fields and locate a synthetic `trace_id` in the body.
3. Verify the corresponding query in the Loki datasource. If a trace backend is configured, follow its documented derived-field link; otherwise record “trace link unavailable” rather than inventing a URL.
4. Compare the deliberately inefficient and improved query shapes using the same time range and corpus. Record query shape, response/errors and local resource observations; do not claim an unmeasured speedup.
5. Explain why the release annotation and matching trace ID establish temporal/correlation context but do not prove causality.

**Evidence:** query workbook with answer, expected shape, actual local validation note, screenshot or sanitized text of the matching event, incident timeline. **Acceptance:** at least 20 queries validated or individually marked `[VERIFY]`; absent series, zero and query error are distinguished. **Cleanup:** stop any generator and restore normal log level. **Stretch:** create a canary-missing check with a declared arrival window.

#### Lab D — Cardinality, top-talker and filtering [L2–L3]

**Prerequisites:** known corpus and verified label inspection method. **Safety:** use at most 20 synthetic identifiers; never generate millions of streams; no audit/security filtering.

1. Emit a fixed small set of records with a deliberately bad `request_id` label in a disposable test configuration only. Inspect the actual label sets/streams using the selected release's supported view.
2. Record how many unique IDs and distinct label sets were produced. State other labels and limitations; do not infer memory per stream.
3. Correct the configuration so `request_id` is in the body; repeat the same bounded event set and compare stream-label behavior.
4. Run a top-talker analysis by service and level using bounded counts (queries 9, 10, 19, 20). Identify noisy health checks and propose a filter.
5. Before accepting a filter, test synthetic routine health-check lines, incident-relevant errors, canary events, and audit/security lines. Prove the important classes remain queryable.

**Evidence:** before/after label sets, event count, query shape, top-talker table, filter decision record. **Acceptance:** unique IDs are not stream labels and no protected event class is dropped. **Cleanup:** revert the bad test config and stop the bounded generator. **Stretch:** add a standard-library lint rule rejecting prohibited label keys in config examples.

#### Lab E — Canary, retention and recovery [L3–L4]

**Prerequisites:** Labs A/B; selected Loki release and retention config verified; safe disposable Compose project. **Safety:** stop only the named local Loki service; use a temporary synthetic file directory; do not manipulate host system logs.

1. Emit a bounded canary every 10 seconds for a short test window, storing event IDs and UTC emission times in a local test record.
2. Query each ID in Loki and calculate found, late, missing and duplicate counts. This cadence/window is a lab choice, not a production target.
3. Stop only the lab Loki service for a brief interval. Continue a small fixed number of synthetic events; observe Collector retries, queue behavior, memory and app responsiveness. Do not assume persistent queue behavior.
4. Restart Loki, re-query IDs, and document whether events arrived, were duplicated, were delayed or were lost. If the current config cannot demonstrate a queue metric, use component logs and state the blind spot.
5. Test rotation/offset behavior only in a temporary synthetic directory: rotate a lab file under a small controlled event set and compare source IDs with downstream IDs. Never rotate/delete system logs.
6. Use the configured short retention policy with synthetic records and wait/observe the selected release's documented deletion behavior. Deletion may be asynchronous; verify compactor status and query results before concluding.

**Evidence:** before/during/after timeline; emitted ID list; query results; missing/late/duplicate analysis; disk measurements; retention observation; cleanup proof. **Acceptance:** recovery is tested and no exactly-once claim is made; retention behavior is verified or remains `[OPEN]`. **Cleanup:** stop canary emitter, restore Loki, remove only temporary test files, and preserve/remove the named lab volume intentionally. **Stretch:** draft an upgrade/rollback checklist for the exact pinned release.

### 4.11 Self-check questions

1. **[L1] Why does Loki use labels before line filtering?** Answer: labels identify streams and narrow candidate data; line filtering/parsing then inspects entries. Wrong answer “it indexes every word” confuses Loki with general full-text systems.
2. **[L1] Should `trace_id` be a stream label?** Answer: no, normally keep it in the body or supported structured metadata. Wrong answer “it improves correlation” ignores one unique stream dimension per trace.
3. **[L2] Does JSON formatting guarantee safe logs?** Answer: no; source code can still serialize secrets or PII. Wrong answer “JSON is structured so it is sanitized” confuses format with privacy controls.
4. **[L2] Why use a literal line filter before parsing when practical?** Answer: it can reduce the candidate lines that need parsing; validate semantics against the chosen version. Wrong answer “parsing everything is always simpler” ignores query cost.
5. **[L2] What does a missing canary mean?** Answer: an expected event failed to appear within a declared window; investigate source, receiver, processor, exporter, Loki, timestamps and query. Wrong answer “the service was quiet” ignores the independent expected-event contract.
6. **[L3] Does Collector retry guarantee no loss?** Answer: no; retry/queue configuration may yield delay, duplicates, bounded loss or restart loss. Wrong answer “retry means exactly once” ignores delivery semantics and persistence.
7. **[L3] When is retention complete?** Answer: only after verifying the selected release's policy and asynchronous deletion/compactor behavior. Wrong answer “at the exact configured timestamp” ignores implementation timing.
8. **[L3] When should alerts use logs rather than metrics?** Answer: metrics are generally preferable for stable numeric symptoms; logs can help for important discrete events not represented well by metrics. Wrong answer “logs contain more detail” ignores fragility of message text and event volume.
9. **[L4] Loki is down; what should happen to application requests?** Answer: remote logging should not block core request handling; bounded buffering/retry/drop behavior must be measured and documented. Wrong answer “wait until logs are delivered” makes observability failure an application outage.
10. **[L4] A query returns no lines; is that proof no error occurred?** Answer: no; check time range, labels, clock skew, collection, redaction/filtering, rejection and query errors using a canary. Wrong answer “empty result equals zero errors” confuses absence with valid zero.

### 4.12 Evidence artifacts

Save only non-sensitive evidence in your learning repository:

- [ ] Chosen Core + Logs profile, exact component versions/image references and complete `[VERIFY]` register.
- [ ] Architecture diagram with trust boundaries, buffers, retention and failure/drop points.
- [ ] Loki config, local readiness/health evidence and short-retention verification.
- [ ] Collector config, component inventory, input/output validation and failure observations.
- [ ] Synthetic log contract, label allowlist and fixture corpus.
- [ ] Structured logger source and redaction unit-test output.
- [ ] Collector-side redaction integration evidence showing fake sensitive value absent from stored event.
- [ ] Multiline fixture, selected operator/config and test result.
- [ ] At least 20 LogQL queries with answers, expected shape and local validation notes.
- [ ] Grafana Explore evidence for a known synthetic event.
- [ ] Label-cardinality before/after observations with event count and laptop-specific measurements.
- [ ] Top-talker/volume report and filter decision record.
- [ ] Canary missing/late test, outage/recovery timeline and missing/duplicate analysis.
- [ ] Retention-expiration evidence or an explicit unresolved verification item.
- [ ] Log-schema linter source/tests and output.
- [ ] Troubleshooting runbook, security checklist, ownership/review metadata and cleanup proof.

Never save real credentials, tokens, PII, customer data, production identifiers or credential-bearing URLs. Screenshots should be reviewed for accidental exposure before being retained.

### 4.13 Common interview and design-review questions

1. **Design a reliable log pipeline for a Kubernetes data/ML platform with a small local footprint and production scaling path.**

   **Model answer:** Define the questions and event contract first: UTC timestamp, stable service/environment names, bounded severity/route/error code, and IDs in the body. For the laptop, use one monolithic Loki instance with filesystem storage, short retention and a Collector configuration supported by the pinned distribution; collect a synthetic fixture or verified runtime path, keep all endpoints private, and measure actual resource use. In Kubernetes, a node agent/DaemonSet commonly fits node log access, but permissions, runtime paths, rotation and duplicate collection must be verified. Production architecture may use durable object storage, separated components and authenticated tenant boundaries only after measured scale/availability requirements justify the complexity. Test canary arrival, queue limits, outage recovery, redaction and retention; document duplicates/loss windows rather than claiming exactly-once delivery.

2. **How do Loki labels, stream cardinality and query design affect reliability and performance?**

   **Model answer:** Every distinct label set can create a stream. Bounded dimensions such as service/environment are useful; request IDs, trace IDs, raw paths and per-run IDs create unnecessary stream diversity. Keep unique identifiers in the body or supported structured metadata. Start queries with selective stream selectors and short time ranges, use literal line filters before parsing where practical, parse only needed fields, and avoid grouping by arbitrary messages or IDs. Verify stream/label behavior and compare a bounded synthetic test; do not extrapolate a universal memory cost per stream.

3. **How would you prove logs are not silently lost during a Loki/Collector outage?**

   **Model answer:** Emit a scheduled canary with stable IDs in the body and record emission timestamps independently. Trace each ID through source files, receiver offsets, processors, exporter retries/queues, Loki acceptance and a bounded query. During a short local outage, record emitted/found/late/duplicate/missing counts and resource impact, then restart and test recovery. Verify whether the queue is memory-only or persistent. A healthy component metric is not end-to-end proof; exactly-once delivery must not be claimed unless demonstrated by the actual architecture.

4. **How do you redact sensitive data while preserving incident context and governing audit/security logs?**

   **Model answer:** Prevent sensitive content at source through an allowlist schema; do not serialize headers, bodies or secrets. Apply tested defense-in-depth redaction before export, but recognize downstream redaction cannot erase historical copies. Use synthetic test values, test the actual exported/stored event, bound message size and handle log injection. Maintain explicit policy for audit/security records and never drop them through generic noise filters without approval. Restrict access, retention and forensic export under a documented process; a local lab cannot prove production authorization controls.

5. **How would you troubleshoot slow LogQL queries and choose between Loki and a full-text search platform?**

   **Model answer:** Reproduce with a fixed time range, inspect query errors and labels, narrow the selector, apply a selective literal filter, then add parsing/aggregation incrementally. Avoid broad regex, long ranges and high-cardinality grouping. Check ingestion/limits/storage health as well as query shape. Loki's label-first model is useful when bounded labels narrow the search; a full-text indexing platform may fit arbitrary text search requirements but brings different storage/index and operational trade-offs. Decide using representative workload measurements, not product slogans.

### 4.14 Sources and verification notes

**Authoring source:** the user-supplied “Copy-Paste Content-Generation Prompt — Unit 4: Loki and Centralized Log Pipelines” defines this unit's scope and requirements. The authoritative M11 syllabus and repository tree are referenced by that prompt but were not independently re-read as part of this file-generation step. Official documentation was **not live-consulted** while authoring this artifact. The URLs below are starting points for human verification, not claims of access or compatibility.

Recommended official references:

- Grafana Loki documentation: https://grafana.com/docs/loki/latest/ — architecture, deployment modes, configuration, storage/schema, filesystem/object storage, retention/compactor, limits, multi-tenancy, LogQL, metric queries, structured metadata and troubleshooting.
- Loki configuration reference: https://grafana.com/docs/loki/latest/configure/ — verify exact schema/store/retention fields and release-specific defaults.
- LogQL query reference: https://grafana.com/docs/loki/latest/query/ — verify selectors, filters, parsers, metric queries, `unwrap`, range aggregation and grouping.
- OpenTelemetry Collector documentation: https://opentelemetry.io/docs/collector/ — distribution and component concepts.
- Collector Contrib repository/docs: https://github.com/open-telemetry/opentelemetry-collector-contrib — verify filelog receiver, operators, transform processor, memory limiter, batch processor and OTLP HTTP exporter availability/syntax.
- Grafana Loki data source and Explore documentation: https://grafana.com/docs/grafana/latest/datasources/loki/ and https://grafana.com/docs/grafana/latest/explore/ — verify query editor and correlation integration.
- Docker Compose documentation: https://docs.docker.com/compose/ — verify Compose networking, port binding, mounts and volume behavior.
- Kubernetes logging documentation: https://kubernetes.io/docs/concepts/cluster-administration/logging/ — verify node/container log access and rotation concepts for the selected runtime.
- Repository handoffs: M11 Units 1–3, 5, 7, 10–13 and M09 security foundations; verify their actual paths and content in the repository before relying on them.

#### Verification Register

| ID | Claim/artifact | Why version-sensitive | Human verification procedure | Status |
|---|---|---|---|---|
| V01 | Loki release and monolithic deployment mode | Supported modes and recommended config evolve | Select a supported release; review its deployment docs and release notes | `[VERIFY]` |
| V02 | Loki schema version/date and TSDB/filesystem storage fields | Schema/store defaults and migration constraints vary | Validate `schema_config`, store and index fields against the exact release; use a fresh disposable lab | `[VERIFY]` |
| V03 | Retention/compactor/delete-store fields | Retention may require specific storage/schema settings and asynchronous deletion | Validate config reference and run synthetic expiry test; inspect compactor diagnostics | `[VERIFY]` |
| V04 | Loki OTLP ingestion path and OTLP HTTP exporter | Endpoint composition and ingestion support can change | Confirm official OTLP endpoint for pinned Loki and send one synthetic event | `[VERIFY]` |
| V05 | Collector distribution/component availability | Core/contrib builds include different components | Inspect component inventory for the pinned image; validate config with that build | `[VERIFY]` |
| V06 | Filelog receiver, `json_parser`, timestamp/severity mapping | Operator names/attributes/layout fields may change | Validate receiver docs and run normal/malformed JSON fixtures | `[VERIFY]` |
| V07 | File path, permissions, offsets/checkpoints, rotation | Runtime, Compose, WSL2 and `kind` paths differ | Inspect actual mounts/paths and run a temporary-file rotation test | `[VERIFY]` |
| V08 | Transform processor and OTTL `replace_pattern` syntax | OTTL contexts/functions and escaping vary | Check transform processor docs for pinned release; test exported event, not only source formatter | `[VERIFY]` |
| V09 | Redaction behavior and replacement semantics | Regex/OTTL escaping and field types can differ | Run fake token/email tests including false positives/negatives end-to-end | `[VERIFY]` |
| V10 | Batch/memory limiter fields and units | Component configuration and defaults can change | Check component docs and verify bounded memory behavior under small test | `[VERIFY]` |
| V11 | Retry, queue and persistent storage semantics | Exporter queue options and durability extensions vary | Verify config and run outage/restart drill; document duplicates/loss | `[VERIFY]` |
| V12 | Structured metadata support/mapping | Loki version and OTLP resource mapping affect behavior | Check Loki OTLP docs; inspect actual stream labels and returned metadata | `[VERIFY]` |
| V13 | LogQL operators, JSON/logfmt parser, `unwrap`, metric queries | Syntax and behavior can evolve | Validate all 22 queries in Explore against known synthetic fixture | `[VERIFY]` |
| V14 | Label allowlist and label-to-resource mapping | Ingestion mapping/config differs by path | Inspect actual stored labels and query label browser; confirm no IDs are labels | `[VERIFY]` |
| V15 | Ingestion limits, line size, stream limits and rejection behavior | Names/defaults and enforcement vary | Check release config reference and inspect rejection evidence under bounded test | `[VERIFY]` |
| V16 | Out-of-order window and tenant header behavior | Defaults and multi-tenant architecture differ | Check current config reference and deployment/auth model; do not assume header support | `[VERIFY]` |
| V17 | Grafana Loki datasource and Explore UI | UI labels and derived-field behavior vary | Verify current Grafana docs and test the exact local version | `[VERIFY]` |
| V18 | Loki readiness/health endpoints and self-metric names | Endpoints/metric names can vary by release | Inspect official docs and the running service's exposed metrics/endpoints | `[VERIFY]` |
| V19 | Compose internal network, image command and local bindings | Compose/runtime behavior and image entrypoints vary | Run `docker compose config`; inspect `ps`, port mappings and logs before starting | `[VERIFY]` |
| V20 | Multiline/recombine operator configuration | Collector operator names, ordering and timeout fields vary | Use official filelog docs for pinned build; test fixture with known frame count | `[VERIFY]` |
| V21 | Kubernetes metadata processor and RBAC | Requires supported processor and environment-specific permissions | Inspect component docs and minimal RBAC; do not grant cluster-wide access by default | `[VERIFY]` |
| V22 | Agent status/recommendations: Promtail, Grafana Alloy, Fluent Bit, Vector | Product lifecycle and recommendations change | Review each project's official current documentation before choosing | `[VERIFY]` |
| V23 | Log alert/ruler behavior | Loki/Grafana alerting integration differs by version/deployment | Check current Loki ruler and Grafana alerting docs; prefer metrics when suitable | `[VERIFY]` |
| V24 | Retention expiration timing and forensic preservation | Deletion is often asynchronous and policy-specific | Run a synthetic retention test; document observed expiry and any hold/export path | `[VERIFY]` |
| V25 | Version upgrades, schema migration and rollback commands | Migration requirements are release-specific and can be destructive | Read release notes and migration guides; rehearse on disposable data before production | `[VERIFY]` |
| V26 | Security/auth/TLS/multi-tenant boundary | Native features and edition/deployment limitations vary | Verify exact capabilities; test auth boundary independently; never rely on labels for authorization | `[VERIFY]` |
| V27 | Python logger and redaction regex coverage | Regexes are intentionally incomplete and schema policy-specific | Run unit/integration tests with fake formats and review false-positive behavior | `[VERIFY]` |
| V28 | Query 14 `unwrap` and range syntax | Nested log range expressions are sensitive to LogQL grammar/version | Test the exact query; if rejected, consult official query examples and update evidence | `[VERIFY]` |
| V29 | Query 16 release filtering | Default contract keeps release in body, not labels | Use JSON parser form or deliberately revise bounded label contract and all tests | `[OPEN]` |
| V30 | Full Collector→Loki integration | Compose snippet requires release-specific endpoint, field mapping and component validation | Start disposable stack only after V01–V12; query a known synthetic event and verify redaction | `[OPEN]` |

#### Open verification items

All `[VERIFY]` entries in V01–V28 and V30 remain open because this authoring pass did not consult live official documentation or execute the stack. They cover release/deployment mode, Loki schema/storage/retention, OTLP ingestion, Collector components/configuration, runtime log paths, redaction syntax, queue semantics, LogQL grammar, labels, limits, health metrics, Compose behavior, multiline handling, security and migration. Resolve each using the human procedure in the register before running the configuration. V29 is an intentional teaching mismatch: `release` is body-only in the default contract, so query 16 must be corrected to parse JSON unless the label contract is explicitly changed. The example configs should not be treated as validated production configs until V30 passes in a disposable local environment.

#### Audit summary

| Pass | Status | Evidence/notes |
|---|---|---|
| 1. Roadmap fidelity | PASS with open source verification | Exact target/unit title, learner profile, Core + Logs and stated boundaries are included. |
| 2. Coverage | PASS with version-sensitive items open | Required architecture, logs schema, LogQL workbook, redaction, retention, loss detection and 25 troubleshooting cases are addressed. |
| 3. Pedagogy | PASS | L1–L4 progression, five labs, acceptance/evidence/cleanup and assessments are included. |
| 4. Loki/LogQL correctness | PASS WITH `[VERIFY]` | Label-first model and body-vs-label rules are explicit; exact grammar and storage fields require release validation. |
| 5. Collector pipeline correctness | OPEN | Components/config are illustrative and require exact distribution/OTTL/endpoint validation. |
| 6. Artifact consistency | PASS WITH OPEN ITEMS | Paths and schema align at the teaching level; full runtime integration is not proven. |
| 7. Version/source honesty | PASS | No live docs or commands are claimed as consulted/executed; unresolved claims are registered. |
| 8. Security/privacy/safety | PASS | Synthetic-only examples, local-only design, bounded experiments and no-secret rules are explicit. |
| 9. Operational usefulness | PASS | Canary, outage, retention, governance, incident cases and runbooks are provided. |
| 10. Scope and Markdown quality | PASS | One target document is authored; headings, inline artifacts, verification register and definition of done are present. |

## Definition of done

- [x] Exact Unit 4 title and target filename.
- [x] Sections `4.0`–`4.14` are present in the specified order.
- [x] L1–L4 progression and measurable objectives are present.
- [x] Loki architecture, labels/streams/chunks, LogQL and structured logging are explained.
- [ ] Local monolithic Loki configuration is verified against the selected release; currently `[VERIFY]`.
- [ ] Collector input, processors, redaction, buffering and output path are verified together; currently `[OPEN]`.
- [ ] Compose/runtime paths are validated for the learner's platform; no host container-log path is assumed universal.
- [x] At least 20 graded LogQL queries include answers and expected result shapes.
- [x] Labs A–E include artifacts, commands, evidence, acceptance criteria and cleanup.
- [x] Label-cardinality incident is bounded; no millions-of-streams experiment.
- [x] Redaction tests use synthetic sensitive-looking values.
- [x] Log-loss canary and outage/recovery drill are present.
- [ ] Retention/deletion behavior is runtime-verified or remains explicitly open.
- [x] Troubleshooting matrix coverage is represented through the incident analyses and runbook; see the case checklist below.
- [x] Security, privacy, no-secret/no-PII, local-only access and app-isolation requirements are explicit.
- [x] M10, Units 1–3/5–13, M03/M04/M05/M08/M09/M13/M14/M15/M16 boundaries are stated.
- [x] No monetary prices or financial ROI calculations.
- [x] No fabricated runtime outputs or documentation-consultation claims.
- [x] Ten-pass audit summary and complete verification register are present.
- [x] Only this target Markdown file is authored; no other repository file is intentionally changed.

**Required troubleshooting-matrix coverage check:** no logs; one service absent; JSON fields not queryable; IDs accidentally labels; rejection/order limits; wrong time range; clock skew; split multiline; missed redaction; over-redaction; unreadable source path; full queue/retries; duplicates; rotation loss; slow query; brittle log alert; excessive debug volume; retention too long/short; app affected by Loki outage; broken metric/log/trace correlation; missing/renamed self-metrics; unsupported Collector component; label/stream limit; missing canary while routine logs appear; audit/security lines filtered. For each incident, record `Symptom | First check | Evidence | Likely cause | Discriminating test | Fix | Prevention` in the learner's runbook; exact diagnostic commands/metric names must be filled after version verification.

**This is an authoring-time structural and consistency audit, not proof that every command or pipeline was executed. Verify runtime behavior in the learner’s environment.**
