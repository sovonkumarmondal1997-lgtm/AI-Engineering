# Unit 11 — Scheduled Job Freshness and Deadline Monitoring

> **Stage:** 2E — Production DevOps & Platform Engineering  
> **Module:** M11 — Production Observability Stack and Performance Operations  
> **Unit position:** Unit 11, after Unit 10 (distributed trace analysis and bottleneck isolation) and before Unit 12 (observability cost, cardinality, and data retention)  
> **Artifact:** `11-scheduled-job-freshness-and-deadline-monitoring.md`

**Evidence labels used throughout**

- `[SYNTHETIC]` — fabricated data, logs, traces, incident narratives, or sample output.
- `[ILLUSTRATIVE]` — example threshold, SLO allocation, schedule, or configuration value that is not a universal default.
- `[ASSUMPTION]` — a design choice made for a local teaching example.
- `[VERIFY]` — version-, platform-, exporter-, or deployment-dependent behavior that must be checked against official documentation and the installed environment.

No real customer data, secrets, external service, or production endpoint is required. All local experiments must be bounded and cleaned up.

> M10 Unit 2 defined freshness, coverage, correctness, and timeliness SLIs/SLOs for data workloads and introduced the batch-metrics pitfalls. This unit **implements the monitoring** — exporter/metric patterns, Kubernetes CronJob and orchestrator monitoring, deadline and missed-run detection, silent-failure detection, and operations at scale — on the production stack.

---

## 0. Purpose, prerequisites, and exact handoff

### 0.1 What this unit teaches

A scheduled pipeline can report success while delivering data that is stale, incomplete, invalid, incorrect, uncommitted, or never consumed. This unit makes those distinct states observable. It builds metric contracts, deadline and freshness rules, dashboards, a small DAG slack calculator, a last-success registry design, streaming progress signals, known-answer canaries, and a safe local chaos matrix.

The running example is a synthetic data path:

```text
scheduler -> ingest -> validate -> durable commit -> feature refresh -> model/API consumer
     |             |        |              |                 |
 heartbeat      run state  coverage      last valid       watermark/
 and expected               and canary     success          consumer lag
 schedule
```

A related streaming path is:

```text
synthetic producer -> queue -> consumer -> transform -> checkpoint / sink
                              |             |              |
                           time lag       DLQ rate      watermark delay
```

This unit answers questions such as:

- Did the expected run start, and did it finish before its deadline?
- Did validated data commit durably?
- How old is the last valid committed data, and how far has event time progressed?
- Did all expected partitions arrive?
- Did a successful process silently emit empty or semantically wrong output?
- Is a streaming consumer making progress, or is lag growing?
- Who owns the dataset, which consumers are affected, and what safe recovery is available?

It deliberately does **not** re-derive M10 SLI/SLO mathematics, reteach M11 Unit 8 runbook foundations, duplicate Unit 9 queue/saturation concepts, or repeat Unit 10 trace-analysis instruction. It uses those outputs. Unit 12 will address observability cost, cardinality, and retention; later capstone work can integrate these patterns across the complete platform.

### 0.2 Prerequisites and readiness check

The learner should already be comfortable with Python, Linux shell basics, containers, basic Kubernetes/kind, Prometheus and PromQL, Grafana, logs, traces, alerting, SLOs, and incident response.

Readiness check:

- [ ] Explain the difference between a process exit code and validated output.
- [ ] Find a time series and inspect its labels before writing an alert.
- [ ] Explain why a metric can be absent because the job is absent, the exporter is down, the series is stale, or the label scope is wrong.
- [ ] Explain idempotency and why rerunning a pipeline can duplicate output.
- [ ] Identify the dataset owner, freshness threshold, deadline, consumers, and runbook for a critical dataset.
- [ ] Use a synthetic fixture when kind or telemetry infrastructure is unavailable.

### 0.3 Definitions

| Term | Operational meaning |
|---|---|
| Scheduled job | A task expected to start according to a schedule or explicit trigger policy. |
| Pipeline | A set of dependent stages that transforms inputs into outputs. |
| Run | One logical execution attempt; retries may be part of one run or separate attempts depending on the orchestrator. |
| Freshness | Age of the last successful, valid, durably committed update, measured against the correct business/event-time contract. |
| Event time | Timestamp describing when an event or source fact occurred, not when the pipeline processed it. |
| Processing/run time | Wall-clock time spent executing a job or stage. |
| Watermark | A progress claim about event time: for example, the latest event-time boundary considered complete enough by a stream processor. Semantics are pipeline-specific. |
| Deadline | Latest acceptable completion time for a run or output to remain useful. |
| Coverage | Proportion or set of expected partitions, records, entities, or time windows actually represented. |
| Validity | Whether output satisfies structural and domain validation rules. |
| Correctness | Whether output represents the intended facts and transformations; validity checks alone may not prove correctness. |
| Idempotency | Repeating the same logical operation does not create unintended additional effects. |
| Duplicate run | Two attempts process the same logical schedule/window or write the same output more than once. |
| Silent semantic failure | A pipeline runs and appears operationally successful but produces incorrect or unusable data without an obvious process error. |
| Last valid success | Timestamp recorded only after validation and durable commit have both succeeded. |
| Consumer freshness | Whether downstream users or systems have actually received and used the expected output. |

### 0.4 Completion criteria

You should finish with: (1) a documented metric contract, (2) tested freshness/deadline rules, (3) a working DAG critical-path/slack script and tests, (4) a tested registry update policy, (5) a canary/reconciliation check, (6) a local six-class chaos matrix, and (7) an evidence-backed runbook. Local timings are **laptop measurements—not production guarantees**.

---

## 1. Scheduled-work failure modes and operational semantics

A healthy process is not the same thing as a healthy data product. Separate the state transitions:

1. **Scheduled:** the run was expected.
2. **Started:** an attempt began.
3. **Executed:** the process performed work.
4. **Exited:** the process returned an exit status.
5. **Validated:** output passed structural and domain checks.
6. **Committed:** output became durably visible under the storage system's commit semantics.
7. **Fresh:** the committed output meets the event-time/freshness contract.
8. **Complete:** expected partitions and coverage are present.
9. **Correct:** known-answer, reconciliation, or domain checks support correctness.
10. **Consumed:** downstream consumers received or used the output.

A process exit code of `0` proves only that the process reported success. It does not prove stages 5–10.

### 1.1 Failure-mode table

All examples are `[SYNTHETIC]`.

| Failure mode | Likely signal | What it proves | What it does not prove | Next check |
|---|---|---|---|---|
| Job did not start | Expected schedule exists; no run-start event | A start is not observed within the detection window | Whether scheduler, worker, or telemetry failed | Scheduler heartbeat, queue, orchestrator event log |
| Job started late | Start timestamp exceeds schedule plus grace | Start was late according to chosen clock/calendar | Whether data deadline was missed | Expected deadline and downstream impact |
| Job ran and failed | Run counter/status or orchestrator failure | An attempt failed if telemetry is trustworthy | Whether previous output remains fresh/valid | Last valid commit and failure stage |
| Job succeeded too slowly | Duration above baseline or deadline slack near zero | Duration regressed or deadline risk increased | Why it became slow | Stage timings, resource and dependency metrics |
| Exit `0`, empty output | Rows zero; validation/canary fails | Output is empty under measured definition | Whether emptiness is always invalid | Dataset contract and expected-volume calendar |
| Partial/incorrect output | Coverage, reconciliation, or canary mismatch | A specific validation failed | Full scope of data corruption | Partition manifest and source counts |
| Hung/deadline exceeded | Active run persists beyond limit | Run exceeds operational limit | Whether process is blocked or merely slow | Logs, stage progress, worker/resource signals |
| Duplicate/DST double-run | Duplicate logical window or idempotency conflict | Duplicate execution/output detected | Whether all duplicates were prevented | Schedule identity, timezone policy, sink keys |
| Stale input/watermark | Event-time watermark stops advancing | Event-time progress is stale | Whether source is late or consumer is stuck | Source heartbeat, queue lag, watermark producer |
| Output not consumed | Consumer offset/ack/receipt or downstream freshness stale | Consumption evidence is missing/stale | Whether consumer telemetry is complete | Consumer health and delivery contract |
| Scheduler hangs while idle | Scheduler heartbeat becomes stale | Scheduler is not reporting progress | Whether a particular run was due | Expected schedule registry and scheduler logs |
| Stale last-success series | Old success timestamp remains exposed | Old state remains visible | That job is still deployed or healthy | Inventory/decommission state and registry lease |
| Exporter is down | Scrape target down or `up == 0` | Prometheus cannot scrape that exporter | Whether the job itself failed | Independent run metadata or orchestrator state |
| Metric absent | `absent()` matches scoped query | No matching series was returned under that selector | Whether job is missing, exporter down, labels changed, or scrape failed | Target health, expected inventory, raw series |

A useful incident report separates:

- **Observation:** “The last valid commit timestamp is 9 hours old.”
- **Hypothesis:** “The scheduler may have stopped triggering runs.”
- **Discriminating evidence:** “Scheduler heartbeat is current, but expected schedule `orders-hourly/14:00Z` has no start event.”
- **Conclusion:** only after corroborating evidence identifies the cause.

### 1.2 Six synthetic timeline examples

| Scenario | Schedule / run facts | Data facts | Interpretation |
|---|---|---|---|
| Late | `[SYNTHETIC]` due 02:00, started 02:12, finished 02:18 | Valid commit at 02:18 | Run completed, but start and possibly freshness deadline were late |
| Hung | Due 02:00, started 02:01, still active at 02:45 | Last valid commit yesterday | Current attempt is not evidence of fresh output |
| Empty | Finished 02:05, exit `0`, rows `0` | Contract expects non-empty partition | Process success; validation should fail and last-success must not advance |
| Partial | Finished 02:05, 9 of 10 partitions committed | Coverage is 90% | A run-level success counter alone hides incomplete output |
| Duplicate | Same logical window processed twice after a scheduler retry/DST ambiguity | Output row count doubles | Need logical run key, idempotent sink, and duplicate detection |
| Stale input | Job finished at 02:05 and committed | Watermark remains at prior day's 23:00 | New processing time does not mean event-time freshness advanced |

### 1.3 Duplicate and calendar semantics

Schedules must specify timezone, daylight-saving-time policy, business calendar, grace, and a logical window key. A “daily at 01:30 local time” schedule may encounter a skipped or repeated wall-clock time around DST transitions. Do not infer how a scheduler resolves that ambiguity: inspect its official documentation and test the selected timezone in a sandbox `[VERIFY]`.

A robust sink uses a stable logical key such as `(dataset, partition_window)` and an idempotent commit/upsert policy. “Run ID” alone is not sufficient to prevent duplicate logical output because retries often have different attempt IDs.

---

## 2. Freshness, deadlines, schedules, and SLIs

### 2.1 Freshness is not run duration

For a dataset with a valid committed update timestamp \(t_c\), processing time now \(t\), and event-time watermark \(t_w\), keep these separate:

- **Commit-age freshness:** \(t - t_c\), useful for “when was a valid output last committed?”
- **Event-time lag:** \(t - t_w\), useful for “how far behind real-world event time is the data?”
- **Run duration:** \(t_{finish} - t_{start}\), useful for execution performance.
- **Deadline slack:** deadline minus estimated finish time; positive slack is time remaining, negative slack means the estimate crosses the deadline.
- **Consumer freshness:** age of the latest output acknowledged or observed by the consumer.

A successful job can process yesterday's input quickly and commit it today. Commit age looks recent while event-time freshness is bad. Conversely, a long-running backfill may create useful historical partitions but not advance the current watermark.

The proposed metric `job_data_watermark_timestamp_seconds` represents an event-time timestamp in Unix seconds. It is a lab contract, not a universal standard. Its semantics must say whether it is the maximum observed event time, a completeness watermark, or another explicitly defined boundary.

### 2.2 Schedule, grace, deadline, and missed-run detection

Define:

- **Cadence:** expected interval or calendar rule.
- **Expected schedule signal:** timestamp/identifier emitted by a schedule registry or orchestrator for each expected logical run.
- **Grace period:** allowed delay after expected start/deadline before classifying a run as late/missed.
- **Deadline \(T\):** latest acceptable time for valid committed output.
- **Missed run:** an expected logical run has no qualifying start/completion evidence after its grace period.
- **Duration regression:** execution time worsens relative to a comparable historical baseline, even if the deadline has not yet been missed.

Do not encode a complex business calendar solely as a fixed interval in PromQL. Use an orchestrator or schedule registry that emits the next expected run/deadline and run identity. This handles holidays, monthly close, DST, and irregular schedules more reliably.

### 2.3 Worked synthetic timeline

`[SYNTHETIC]` An hourly dataset has a 15-minute completion grace after the scheduled trigger and an event-time watermark target no older than 90 minutes. These values are illustrative only.

| Time | Event | Commit-age result | Event-time result | Operational action |
|---|---|---:|---:|---|
| 10:00 | Expected run | Previous valid commit is 60 min old | Watermark at 09:00 | Wait within agreed grace |
| 10:08 | Run starts | 68 min old | Still 60 min behind | Check run state only if start late |
| 10:16 | Process exits `0`, 0 rows | Still 76 min since previous valid commit | Watermark unchanged | Validation failure; do not advance success |
| 10:20 | Deadline + grace exceeded | Previous valid commit 80 min old | Watermark unchanged | Alert on missed/invalid output |
| 10:28 | Corrected run commits valid output | Commit-age near zero | Watermark advances to 10:00 | Close only after validation and consumer checks |

### 2.4 Separate SLIs

| SLI | Example definition | Evidence source | Common trap |
|---|---|---|---|
| Per-run duration | Fraction of qualifying runs finished within duration budget | Run start/finish events | Treating a fast failed run as good |
| Dataset freshness | Fraction of evaluated time slices where last valid committed output is within threshold | Last-success registry and clock | Updating success on process start or exit `0` |
| Event-time freshness | Fraction of slices where watermark lag is within threshold | Watermark metric | Confusing latest event timestamp with completeness watermark |
| Partition coverage | Fraction of expected partitions present and valid | Manifest/catalog/reconciliation | Counting records without enumerating expected partitions |
| Correctness/validation | Fraction of runs passing required domain checks | Validation events/canary | Assuming schema-valid means semantically correct |
| Consumer freshness | Fraction of slices where consumer has acknowledged current output | Consumer metadata/offset/receipt | Assuming producer commit means consumer delivery |

### 2.5 Time-slice freshness SLI

Reuse M10's established freshness SLO and burn-rate approach. For a time-slice SLI, evaluate each minute (or agreed slice) against the dataset contract:

```text
good slice = valid committed output exists
             AND commit age <= freshness threshold
             AND watermark lag <= threshold (if required)
             AND coverage/validation requirements pass
bad slice  = expected telemetry is present and the contract is violated
unknown    = telemetry is missing/ambiguous; handle separately, do not silently call it good
```

A missing series should not automatically count as good. Decide explicitly whether unknown telemetry is bad for the user-facing SLI, a separate observability SLI, or both. Reuse the project's M10 burn-rate definitions rather than inventing a new formula. Add tests for good, bad, missing, and planned-backfill states.

### 2.6 Backfills and maintenance

A planned backfill can legitimately create old partitions or duplicate work while the current freshness obligation remains in force. Prefer explicit maintenance metadata scoped to `(dataset, logical window, reason, expiry)` rather than globally muting all freshness alerts.

Suppression rules must have:
- a named owner and reason;
- exact datasets and alert families in scope;
- start and expiry timestamps;
- an explicit maximum duration;
- a validation that expiry is present and in the future;
- an automatic notification or alert when suppression expires;
- a test proving an unrelated real missed run still fires.

Never suppress scheduler heartbeat loss or all dataset alerts merely because one backfill is planned.

### 2.7 SLO definition template

```yaml
dataset: "<DATASET>"
owner: "<TEAM_OR_OWNER>"
consumers:
  - "<CONSUMER>"
schedule:
  description: "hourly on the approved business calendar"
  timezone: "UTC"
  expected_run_source: "<SCHEDULE_REGISTRY_OR_ORCHESTRATOR>"
freshness:
  valid_commit_age_seconds: 5400   # [ILLUSTRATIVE]
  event_time_lag_seconds: 5400     # [ILLUSTRATIVE]
deadline:
  grace_seconds: 900               # [ILLUSTRATIVE]
coverage:
  required_partition_fraction: 1.0
validation:
  non_empty: true
  known_answer_canary: true
measurement_window: "<M10_DEFINED_WINDOW>"
alert_policy: "<M10_BURN_RATE_POLICY>"
runbook: "<RUNBOOK_URL>"
```

This is a teaching template, not a validated schema. Validate it against your own catalog schema before generating rules.

---

## 3. Batch instrumentation and metric contract

The following are proposed lab metric names, not universal standards.

### 3.1 Metric contract

| Proposed metric | Type/unit | Update semantics | Stable labels | Limitation |
|---|---|---|---|---|
| `job_last_success_timestamp_seconds` | Gauge, Unix seconds | Update only after validation **and durable commit** | `job`, `dataset`, `env` | Does not prove current watermark or consumer receipt |
| `job_last_run_timestamp` | Gauge, Unix seconds | Update when an attempt starts or reaches the documented run-state boundary; document which | `job`, `dataset`, `env` | Name lacks `_seconds`; choose one convention consistently in a real contract |
| `job_last_duration_seconds` | Gauge, seconds | Set after each completed attempt | `job`, `dataset`, `env` | Last run only; use histogram/events for distributions |
| `job_run_total{status}` | Counter, runs | Increment exactly once per observed terminal outcome | `job`, `dataset`, `env`, bounded `status` | Retries and process restarts require clear semantics |
| `job_rows_processed` | Gauge, rows | Set for the latest run or use a counter if cumulative; specify contract | `job`, `dataset`, `env` | Do not mix latest-run and cumulative meanings |
| `job_data_watermark_timestamp_seconds` | Gauge, Unix event-time seconds | Update only after verifying watermark semantics for the committed output | `job`, `dataset`, `env` | Not the job finish timestamp |
| `job_validation_failures` | Counter or gauge | Counter for failures, or gauge for current run result; do not mix | `job`, `dataset`, `env`, bounded `check` | High-cardinality check names must be avoided |
| `job_partition_coverage_ratio` | Gauge, ratio 0–1 | Update after comparing observed and expected partitions | `job`, `dataset`, `env` | Ratio can hide which partition is missing; retain details in logs/manifest |
| `job_duplicate_outputs_total` | Counter, duplicates | Increment when a duplicate logical key is detected | `job`, `dataset`, `env` | Metric alone cannot show affected keys |
| `scheduler_heartbeat_timestamp_seconds` | Gauge, Unix seconds | Updated by scheduler heartbeat, independently of job runs | `scheduler`, `env` | Must not be emitted only by the job it monitors |
| `job_expected_deadline_timestamp_seconds` | Gauge, Unix seconds | Set from schedule registry for the next expected logical run | `job`, `dataset`, `env` | Requires reliable calendar calculation and expiry |
| `stream_watermark_timestamp_seconds` | Gauge, Unix event-time seconds | Updated from streaming engine's documented watermark | `pipeline`, `env` | Semantics vary by engine |
| `stream_checkpoint_timestamp_seconds` | Gauge, Unix seconds | Update after successful checkpoint | `pipeline`, `env` | Checkpoint age alone does not prove end-to-end freshness |
| `stream_consumer_lag_seconds` | Gauge, seconds | Estimate event-time delay or processing lag with explicit definition | `pipeline`, `consumer`, `env` | Do not confuse seconds with record count |
| `stream_input_records_per_second` / `stream_processed_records_per_second` | Gauge, records/s | Current rates over defined windows | `pipeline`, `env` | Short windows are noisy; compare like-for-like |
| `stream_dlq_records_total` | Counter, records | Increment for records routed to DLQ | `pipeline`, `env`, bounded `reason` if safe | Raw exception text must not become a label |

**Label policy:** keep dimensions bounded and stable, for example `job`, `pipeline`, `dataset`, and `env`. Never use `run_id`, record ID, customer ID, arbitrary path, timestamp, raw URL/query string, or exception message as a metric label. Keep run-specific IDs in structured logs and traces.

### 3.2 Update order is a correctness contract

Correct order:

```text
start run
  -> process to temporary/staging output
  -> validate schema, non-empty expectation, canary, and coverage
  -> commit atomically according to the storage system's real semantics
  -> update last valid success and watermark metadata
  -> emit terminal success event
```

On failure, record the failure outcome and duration, but do **not** advance last valid success. If output commit succeeds but registry update fails, the data and monitoring state can diverge. Treat that as a recoverable consistency problem: reconcile committed manifests with registry state, and make registry updates idempotent. A filesystem rename may provide atomic visibility on the same filesystem, but it is not a universal transaction for databases, object stores, distributed filesystems, or multi-partition commits.

### 3.3 Local synthetic batch job

This standard-library example models the contract. It writes JSON to a temporary file and uses `os.replace` for a local same-filesystem commit. `[ASSUMPTION]` This is a local teaching boundary, not a claim about transactional behavior for other storage systems.

Save as `batch_demo.py`:

```python
#!/usr/bin/env python3
"""Bounded synthetic batch job: validate before commit, then record success."""
import json
import os
import sys
import time
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("BATCH_DEMO_DIR", "./batch-demo")).resolve()
OUTPUT = ROOT / "committed-output.json"
STATE = ROOT / "job-state.json"
EXPECTED_PARTITIONS = {"p0", "p1"}
FAULT = os.environ.get("BATCH_FAULT", "none")  # none|empty|partial|stale|duplicate

def utc_now():
    return datetime.now(timezone.utc).timestamp()

def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)  # same-filesystem local demo only
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise

def process_records():
    records = [
        {"partition": "p0", "event_time": "2026-01-01T10:00:00Z", "value": 7},
        {"partition": "p1", "event_time": "2026-01-01T10:05:00Z", "value": 9},
    ]
    if FAULT == "empty":
        return []
    if FAULT == "partial":
        return records[:1]
    if FAULT == "duplicate":
        return records + [records[0]]
    return records

def validate(records):
    if not records:
        raise ValueError("validation_failed: empty output")
    partitions = {row["partition"] for row in records}
    missing = EXPECTED_PARTITIONS - partitions
    if missing:
        raise ValueError(f"validation_failed: missing partitions {sorted(missing)}")
    keys = [(r["partition"], r["event_time"]) for r in records]
    if len(keys) != len(set(keys)):
        raise ValueError("validation_failed: duplicate logical output key")
    if any(not isinstance(r.get("value"), int) for r in records):
        raise ValueError("validation_failed: invalid value type")
    return partitions

def main():
    started = time.monotonic()
    started_epoch = utc_now()
    ROOT.mkdir(parents=True, exist_ok=True)
    print(json.dumps({"event": "run_started", "job": "synthetic-hourly",
                      "start_timestamp": started_epoch}))
    try:
        records = process_records()
        if FAULT == "stale":
            watermark = 0.0  # deliberately stale event-time fixture
        else:
            watermark = started_epoch - 60  # illustrative synthetic watermark
        partitions = validate(records)
        output = {"records": records, "committed_at": utc_now(),
                  "watermark_timestamp_seconds": watermark}
        atomic_json(OUTPUT, output)
        # Only after output commit and validation:
        state = {"last_success_timestamp_seconds": utc_now(),
                 "last_run_timestamp_seconds": started_epoch,
                 "last_duration_seconds": time.monotonic() - started,
                 "last_status": "success",
                 "rows_processed": len(records),
                 "partition_coverage_ratio": len(partitions) / len(EXPECTED_PARTITIONS),
                 "watermark_timestamp_seconds": watermark}
        atomic_json(STATE, state)
        print(json.dumps({"event": "run_succeeded", "job": "synthetic-hourly",
                          "rows": len(records), "coverage": state["partition_coverage_ratio"],
                          "duration_seconds": state["last_duration_seconds"]}))
        if FAULT == "stale":
            print(json.dumps({"event": "watermark_stale", "job": "synthetic-hourly"}))
        return 0
    except Exception as exc:
        duration = time.monotonic() - started
        print(json.dumps({"event": "run_failed", "job": "synthetic-hourly",
                          "error_class": type(exc).__name__,
                          "duration_seconds": duration}), file=sys.stderr)
        # Deliberately do not overwrite last valid success on failed validation.
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
```

Run with a temporary directory:

```bash
python3 batch_demo.py
BATCH_FAULT=empty python3 batch_demo.py
BATCH_FAULT=partial python3 batch_demo.py
BATCH_FAULT=duplicate python3 batch_demo.py
BATCH_FAULT=stale python3 batch_demo.py
```

Expected observations: empty, partial, and duplicate modes exit non-zero and do not advance `last_success_timestamp_seconds`; the stale mode demonstrates that a recent successful commit can still have a stale event-time watermark. `stale` is intentionally allowed through this demo's structural validation so the monitoring layer can detect it. In a real contract, decide whether stale watermark is a validation failure or a distinct freshness failure.

**Troubleshooting:** if `os.replace` fails, check permissions and filesystem boundaries; temp file and destination must be on a compatible filesystem for this demo. Do not use this script against real datasets. Remove `./batch-demo` after the exercise.

### 3.4 Partial-commit and retry hazards

- A job may write several partitions and fail halfway. Record a commit manifest or transactional boundary; do not publish success until the intended set is complete.
- Retrying after an uncertain commit can duplicate output. Use stable logical keys and idempotent writes, and reconcile before retrying.
- Metrics are not the durable source of truth. Store enough commit/run metadata to reconstruct last valid success after exporter or process restart.
- Separate “run attempt failed” from “dataset is stale.” A failed new run may coexist with a still-valid prior dataset until its freshness threshold expires.

---

## 4. Batch metrics exposure patterns and trade-offs

### 4.1 Comparison matrix

| Pattern | Best fit | Failure modes | Stale-series behavior | Security/coupling | Validation |
|---|---|---|---|---|---|
| Pushgateway | Service-level batch job whose last-run state must be scraped after process exit | Push fails; stale groups remain; gateway unavailable | Pushed series can persist until explicitly deleted; persistence is not health | Network/auth controls and grouping-key hygiene; avoid run IDs in grouping keys | Inspect group lifecycle, push/delete behavior, and official suitability guidance `[VERIFY]` |
| node-exporter textfile collector | Local host job writes a small metrics file | Half-written file, wrong permissions, stale file, exporter down | File remains until replaced/deleted; stale mtime must be monitored | Trusted directory, atomic replacement, restricted writer permissions | Write to temp file, fsync if needed, rename into place, verify exposition |
| Long-running exporter/last-success registry | Central durable run metadata shared across jobs | Registry unavailable, stale record, bad authorization, schema migration | Can expose durable state plus record update time/lease | Strong access control; exporter becomes dependency | Unit-test monotonic updates, identity mapping, read/export behavior |
| Short-lived scrape window | Long enough-running job or intentionally coordinated scrape | Process exits before scrape; scrape race | No series may be observed | Simple but coupled to scrape timing | Compare job duration and scrape interval; not sole source of truth |
| Event/log-derived monitoring | Existing structured run events or orchestrator event stream | Missing logs, parser drift, retention gaps, duplicate events | Derived state can go stale if ingestion stops | Parser and log pipeline coupling; protect sensitive fields | Test missing-event handling, parser versions, and independent heartbeat |
| Per-run tracing | Stage timing, errors, dependencies, and run correlation | Sampling drops runs; propagation gaps; traces expire | Trace history does not itself represent durable last-success state | Run ID belongs in trace/logs, not metric labels | Correlate a known run with commit manifest and metrics |

### 4.2 Pushgateway notes

Pushgateway behavior and intended use must be verified against the official Pushgateway documentation `[VERIFY]`. A retained last-success series is not evidence that the job remains deployed or healthy. Design group keys around stable service/job identity, not individual run IDs. Establish cleanup for decommissioned jobs and obsolete groups, and protect push/delete endpoints. Do not expose a write endpoint to untrusted callers: a caller able to publish metrics may spoof success.

Do not rely on `up` for the batch job's health. `up` usually reports whether Prometheus scraped the target it knows about; it does not prove that a short-lived batch execution ran or committed valid output.

### 4.3 Textfile collector atomic write pattern

Write a complete file in the same trusted directory, then atomically replace the destination. Example shell pattern, subject to filesystem/platform validation `[VERIFY]`:

```bash
set -eu
dir="${TEXTFILE_DIR:-./textfile}"
mkdir -p "$dir"
tmp="$(mktemp "$dir/.job.prom.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
cat >"$tmp" <<'METRICS'
job_last_success_timestamp_seconds{job="synthetic-hourly",dataset="demo",env="local"} 1760000000
job_partition_coverage_ratio{job="synthetic-hourly",dataset="demo",env="local"} 1
METRICS
# Atomic replacement is expected only when source and destination share a filesystem.
mv -f "$tmp" "$dir/job.prom"
trap - EXIT
```

The values above are `[SYNTHETIC]`. A real job must render values from trusted state, escape labels correctly, validate exposition, and avoid writing secrets. Restrict write access to the directory and monitor file age and exporter health independently. Never let a scrape see a partially generated destination file.

### 4.4 Local recommendation

For a small laptop lab, start with durable JSON state and deterministic fixtures. Add the textfile collector pattern if node-exporter is already available; add Pushgateway only to learn group lifecycle and safe cleanup. Use a registry service when several jobs need one authoritative view. Avoid deploying every component at once on an 8 GB machine.

---

## 5. PromQL: freshness, deadlines, missed schedules, and duration

All metric names below are proposed lab names. Before using an expression, discover actual series and labels in the installed Prometheus. Query `/api/v1/label/__name__/values` or the UI's series explorer where permitted, then inspect a concrete selector. Prometheus endpoints and UI paths depend on deployment `[VERIFY]`.

```promql
{__name__=~"job_.*|scheduler_.*|stream_.*"}
```

Use the result to discover names, then inspect exact labels:

```promql
job_last_success_timestamp_seconds
```

### 5.1 Time since last valid success

```promql
time() - job_last_success_timestamp_seconds
```

- **Assumptions:** timestamp is Unix seconds and only advances after validation plus durable commit.
- **Unit:** seconds since last valid success.
- **Proves:** the recorded last-success time is old by the calculated age.
- **Does not prove:** the record is current, the exporter is healthy, or event-time data is fresh.
- **No-data handling:** pair with target/registry health and expected dataset inventory. A missing series must not silently be interpreted as age zero.

A freshness threshold example:

```promql
(time() - job_last_success_timestamp_seconds) > 5400
```

`5400` seconds is `[ILLUSTRATIVE]`, not a default. Use per-dataset thresholds from the catalog, ideally generated as rules.

### 5.2 Event-time freshness

```promql
time() - job_data_watermark_timestamp_seconds
```

This is meaningful only if the metric represents an event-time watermark timestamp in seconds. If the timestamp can be in the future due to clock skew or bad data, negative results require investigation, not a green interpretation.

### 5.3 Deadline exceeded

A schedule registry may expose `job_expected_deadline_timestamp_seconds` for the expected logical run. One simple deadline test is:

```promql
time() > job_expected_deadline_timestamp_seconds
and on (job, dataset, env)
job_last_success_timestamp_seconds < job_expected_deadline_timestamp_seconds
```

This is illustrative. It assumes the expected deadline refers to the output that `job_last_success_timestamp_seconds` must satisfy. If a previous success is older than the current deadline, the expression can indicate overdue output. It does not by itself distinguish a run that is active from one that never started; include run state and scheduler heartbeat.

### 5.4 Missed schedule

Prefer a schedule-derived metric such as:

- `job_expected_run_timestamp_seconds`
- `job_expected_deadline_timestamp_seconds`
- `job_run_started_timestamp_seconds` or explicit run-state events

Then compare the expected logical run with observed start/finish state. Do not invent a universal PromQL expression for cron calendars, business holidays, DST, and monthly close. Have the schedule registry/orchestrator compute expected runs and expose a bounded state.

### 5.5 Missing metrics and `absent()`

```promql
absent(job_last_success_timestamp_seconds{job="synthetic-hourly",env="local"})
```

This detects absence for that exact selector scope. It does not distinguish a decommissioned job, label rename, exporter outage, scrape failure, or missing data. `absent_over_time()` syntax/availability and behavior should be checked against the installed Prometheus version `[VERIFY]`.

For many datasets, a catalog/inventory metric can make missing expected series detectable. Be careful: `absent()` returns a synthetic result with labels derived from its selector in limited ways; it does not magically reconstruct every expected dataset label. Test label scoping explicitly with `promtool`.

### 5.6 Exporter down versus pipeline not running

```promql
up{job="batch-metadata-exporter"} == 0
```

This indicates a scrape target failure under the configured target label. It does not prove the batch job failed. Conversely, `up == 1` proves the exporter was scraped successfully, not that its data is fresh. Monitor these independently:

1. exporter/registry availability;
2. scheduler heartbeat;
3. expected run state;
4. last valid commit age;
5. event-time watermark;
6. coverage/validation;
7. consumer receipt.

### 5.7 Duration regression

If the metric is a gauge of the last duration, compare it with a historical baseline only if each series has consistent semantics:

```promql
job_last_duration_seconds
/
clamp_min(avg_over_time(job_last_duration_seconds[7d]), 0.001)
```

The result is a ratio, not a statistical significance test. A seven-day window is `[ILLUSTRATIVE]`; sparse gauges may repeat the same last-run value across many scrapes, making the average a poor estimate of per-run duration. Prefer per-run events or a histogram/recorded duration series if available. Test query semantics and baseline comparability `[VERIFY]`.

### 5.8 Empty output, coverage, validation, duplicates, and stale state

```promql
job_rows_processed == 0
job_partition_coverage_ratio < 1
increase(job_validation_failures[30m]) > 0
increase(job_duplicate_outputs_total[30m]) > 0
(time() - job_data_watermark_timestamp_seconds) > 5400
```

Each query assumes the named series exists, labels are stable, and values have the documented meaning. `job_rows_processed` should represent latest-run rows if used as a gauge. A zero may be valid for some datasets, so scope the alert to contracts that require non-empty output. `increase()` over counters is sensitive to window size and sparse events; choose a window aligned with the schedule.

### 5.9 Kubernetes CronJob/Job signals

The following metric names are awareness examples and must be checked against the installed kube-state-metrics version and configuration `[VERIFY]`:

- `kube_cronjob_status_last_schedule_time`
- `kube_cronjob_status_active`
- `kube_job_status_failed`
- `kube_job_status_succeeded`
- `kube_job_complete`
- `kube_job_failed`
- `kube_cronjob_next_schedule_time`

Discover actual names and labels first. A Kubernetes Job being complete does not prove its output was valid or committed. CronJob suspension, concurrency policy, job history cleanup, missed schedule handling, and controller behavior must be checked against the installed Kubernetes version's official CronJob documentation `[VERIFY]`. Monitor expected schedule/deadline and application-level validation alongside Kubernetes state.

### 5.10 Streaming signals

Potential proposed lab signals:

```promql
time() - stream_watermark_timestamp_seconds
time() - stream_checkpoint_timestamp_seconds
stream_consumer_lag_seconds
stream_processed_records_per_second / clamp_min(stream_input_records_per_second, 0.001)
rate(stream_dlq_records_total[5m])
```

These expressions require explicit definitions and units. A processed/input ratio below one may indicate accumulating backlog but can be normal during startup or a deliberate replay. A DLQ counter rate can be noisy at low volumes. Use a replay state/maintenance record with bounded scope and expiry; still alert on unbounded growth, correctness failures, or expired suppression.

### 5.11 PromQL validation checklist

- [ ] Confirm metric names and units.
- [ ] Inspect label sets and cardinality.
- [ ] Test no-data and exporter-down separately.
- [ ] Test stale last-success and stale watermark independently.
- [ ] Confirm expected schedule is calendar-derived, not guessed from a fixed interval.
- [ ] Verify syntax with installed `promtool`.
- [ ] Test all critical firing and no-fire cases before rollout.

---

## 6. Alerting and operational context

### 6.1 Alert design

A critical alert should include owner, dataset/pipeline, last valid success, watermark age, expected deadline, consumer/lineage impact if available, and `<RUNBOOK_URL>`. Keep bounded identifiers in labels; put explanatory details in annotations or linked metadata.

| Alert family | Typical severity | Evidence | Required context |
|---|---|---|---|
| Freshness approaching SLO | Ticket/warning | Remaining freshness budget is low | Dataset, owner, deadline, last success |
| Freshness SLO breached | Page only if agreed business impact warrants it | Valid commit age or watermark lag exceeds SLO | Consumers, impact, runbook |
| Deadline missed / no start | Page for critical dataset | Expected run deadline passed with no qualifying completion/start | Schedule ID/window, heartbeat |
| Job failed | Ticket or page by criticality | Terminal failure event | Error class, stage, prior valid output |
| Hung/long-running | Warning/page based on deadline risk | Active duration exceeds expected bound | Start time, stage progress, safe termination |
| Scheduler heartbeat lost | Page if scheduler is critical | Heartbeat older than threshold | Scheduler owner and independent checks |
| Empty/partial/invalid output | Page if output is published or deadline is at risk | Validation/coverage/canary failure | Validation result, commit state |
| Watermark/checkpoint stale | Severity based on downstream impact | Event-time progress stopped | Source, consumer, last progress |
| Missing/stale metrics | Ticket or observability alert | Expected series absent or exporter down | Distinguish exporter vs pipeline |
| Duplicate run/output | Page if data integrity risk | Duplicate logical key or overlapping run | Logical window and idempotency evidence |
| CronJob suspended/overlap/failure | Based on deadline and impact | Verified Kubernetes state series | Namespace/job and schedule registry |
| Streaming lag/DLQ growth | Based on lag budget and consumer impact | Lag, watermark delay, DLQ rate | Replay status and consumer owner |

Do not page on every anomalous row count if the dataset's contract permits variation. Start in observe-only mode, validate false-positive behavior, then enable tickets and pages according to impact.

### 6.2 Example alert rule file

The rules below are illustrative and use proposed metrics. Adjust label matchers, `for` durations, and PromQL syntax to the installed version and local contracts `[VERIFY]`.

```yaml
groups:
  - name: scheduled-data-health
    rules:
      - alert: DatasetFreshnessBreached
        expr: (time() - job_last_success_timestamp_seconds) > 5400
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Dataset freshness threshold breached"
          description: "dataset={{ $labels.dataset }} job={{ $labels.job }} owner={{ $labels.owner }}"
          last_success: "{{ $value }}"
          runbook_url: "<RUNBOOK_URL>"

      - alert: DatasetWatermarkStale
        expr: (time() - job_data_watermark_timestamp_seconds) > 5400
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Event-time watermark is stale"
          description: "dataset={{ $labels.dataset }} owner={{ $labels.owner }}"
          runbook_url: "<RUNBOOK_URL>"

      - alert: DatasetCoverageIncomplete
        expr: job_partition_coverage_ratio < 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Dataset partition coverage is incomplete"
          description: "dataset={{ $labels.dataset }} coverage={{ $value }}"
          runbook_url: "<RUNBOOK_URL>"

      - alert: BatchExporterDown
        expr: up{job="batch-metadata-exporter"} == 0
        for: 2m
        labels:
          severity: ticket
        annotations:
          summary: "Batch metadata exporter is unavailable"
          description: "Exporter failure is not proof that the batch job failed."
          runbook_url: "<RUNBOOK_URL>"
```

The example includes `owner` in an annotation, but owner may not be a Prometheus label in your contract. Prefer a bounded catalog join or generated annotation if owner labels would increase cardinality or be duplicated inconsistently. Never assume the rule above is ready for production without tests.

### 6.3 `promtool` tests

`promtool` test-file syntax and features depend on the installed Prometheus version `[VERIFY]`. Check:

```bash
prometheus --version
promtool --version
promtool check rules ./rules.yml
promtool test rules ./rules_test.yml
```

Illustrative `rules_test.yml` skeleton:

```yaml
rule_files:
  - rules.yml
evaluation_interval: 1m
tests:
  - name: freshness breach after stale success
    interval: 1m
    input_series:
      - series: 'job_last_success_timestamp_seconds{job="j1",dataset="d1",env="local"}'
        values: '0+0x10'
    alert_rule_test:
      - eval_time: 10m
        alertname: DatasetFreshnessBreached
        exp_alerts:
          - exp_labels:
              job: j1
              dataset: d1
              env: local
              severity: warning
            exp_annotations:
              summary: "Dataset freshness threshold breached"
              description: "dataset=d1 job=j1 owner="
              last_success: "0"
              runbook_url: "<RUNBOOK_URL>"
```

This is a test design sketch, not a guaranteed passing fixture: alert labels/annotations and rule evaluation time must be aligned to your actual rule file and `promtool` version. Use `promtool test rules --help` and a minimal passing fixture first. Test at least:

- stale success fires;
- fresh success does not fire;
- missing series is handled explicitly;
- exporter-down does not get mislabeled as pipeline failure;
- exact label scoping for each dataset;
- a planned backfill suppresses only the intended alert and only until expiry;
- validation failure and incomplete coverage fire;
- a decommissioned job's stale series cannot masquerade as a live dataset.

### 6.4 Alert coverage check

Maintain a catalog table for each critical alert:

| Alert | Owner exists | Impact annotation | Test exists | Runbook exists | No-data case tested |
|---|---|---|---|---|---|
| Dataset freshness | [ ] | [ ] | [ ] | [ ] | [ ] |
| Deadline missed | [ ] | [ ] | [ ] | [ ] | [ ] |
| Validation/coverage | [ ] | [ ] | [ ] | [ ] | [ ] |
| Scheduler heartbeat | [ ] | [ ] | [ ] | [ ] | [ ] |
| Streaming lag/checkpoint | [ ] | [ ] | [ ] | [ ] | [ ] |

Roll out progressively: recording rules first, dashboard validation second, alert notifications to a test route third, low-severity notifications next, and paging only after observing real-like fixtures and confirming ownership. A rule with no owner or runbook is an operational defect.

---

## 7. Freshness/deadline dashboard and fleet view

Recommended layout:

```text
+---------------------------------------------------------------------+
| Fleet freshness SLO | overdue deadlines | missing telemetry | owners|
+----------------------+----------------------+-----------------------+
| Dataset freshness vs SLO             | Expected/next run + deadline|
+--------------------------------------+-----------------------------+
| Last valid commit | Event watermark  | Scheduler heartbeat/state  |
+--------------------------------------+-----------------------------+
| Run duration & baseline              | Rows / coverage / validation|
+--------------------------------------+-----------------------------+
| DAG critical path / slack            | Streaming lag / checkpoint  |
+--------------------------------------+-----------------------------+
| Alert history | backfill annotations | consumers / lineage / runbook|
+---------------------------------------------------------------------+
```

### 7.1 Panel specification

| Panel | Question | Unit | Suggested range/aggregation | Source | Interpretation trap |
|---|---|---|---|---|---|
| Freshness vs SLO | Which datasets are approaching/breaching threshold? | seconds/minutes | Current value and threshold; fleet grouped by owner/criticality | Last-success registry | Recent run timestamp is not valid committed freshness |
| Last valid commit | When did valid output last commit? | Unix timestamp / age | Current state plus history | Registry/metadata | A stale record can persist after decommission |
| Event-time watermark | How far behind is event-time progress? | seconds | Current age and trend | Job/stream metrics | Watermark semantics differ by engine |
| Expected run/deadline | What was expected and when is it overdue? | timestamp / seconds remaining | Next run and deadline | Schedule registry/orchestrator | Fixed interval ignores holidays/DST |
| Duration trend | Is execution time regressing? | seconds | Per-run samples, comparable windows | Run events/histogram | A repeated last-value gauge is not a run distribution |
| Volume and coverage | Was expected output produced? | rows, ratio 0–1 | Per run/window | Validation manifest | Volume can vary legitimately; coverage is not correctness |
| Validation/duplicates | Did semantic checks fail? | count/rate | Per run and recent window | Validation events | No failure event can mean telemetry is missing |
| Scheduler/Job state | Is the scheduler alive and is a run active/failed? | heartbeat age, state | Current state plus recent history | Scheduler and orchestrator | Exporter availability is not scheduler health |
| DAG critical path/slack | Which dependency threatens the deadline? | seconds | Current estimate and historical range | DAG planner/registry | Deterministic estimates do not guarantee future finish |
| Streaming progress | Is the stream advancing? | seconds, records/s | Lag/watermark/checkpoint trends | Stream engine/exporter | Backlog during replay may be expected |
| Alert history/backfill | Was a signal suppressed or recurring? | count/timeline | Selected incident window | Alert manager/catalog | Global mute hides unrelated failures |
| Consumer/lineage impact | Who depends on this dataset? | categorical/list | Current lineage metadata | Catalog | Stale lineage can misstate impact |

Use annotations for planned backfills, deploys, source incidents, and schema changes. Avoid putting run IDs or arbitrary dataset values into high-cardinality dashboard variables without limits.

---

## 8. DAG critical-path and slack-time script

A DAG (directed acyclic graph) represents stage dependencies. If stages can run in parallel, end-to-end duration is the longest dependency path, not the sum of every stage's duration. For each stage, its earliest finish is its duration plus the maximum earliest finish among its predecessors. This script uses deterministic durations and optional stage buffers; it does not model probability distributions, resource contention, retries, or calendar-aware scheduling.

Save as `dag_slack.py`:

```python
#!/usr/bin/env python3
"""Calculate deterministic critical path and deadline slack for a DAG."""
from __future__ import annotations
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"timestamp must include timezone: {value}")
    return dt

def analyze(spec: dict[str, Any]) -> dict[str, Any]:
    jobs = spec.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("jobs must be a non-empty list")
    deadline = parse_utc(spec["deadline"])
    start = parse_utc(spec["start"])
    if deadline < start:
        raise ValueError("deadline precedes start")

    by_name: dict[str, dict[str, Any]] = {}
    for job in jobs:
        name = job.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("each job needs a non-empty name")
        if name in by_name:
            raise ValueError(f"duplicate job: {name}")
        duration = job.get("duration_seconds")
        buffer = job.get("buffer_seconds", 0)
        if not isinstance(duration, (int, float)) or duration < 0:
            raise ValueError(f"invalid duration for {name}")
        if not isinstance(buffer, (int, float)) or buffer < 0:
            raise ValueError(f"invalid buffer for {name}")
        deps = job.get("depends_on", [])
        if not isinstance(deps, list) or len(deps) != len(set(deps)):
            raise ValueError(f"invalid or duplicate dependencies for {name}")
        by_name[name] = {**job, "duration_seconds": float(duration),
                         "buffer_seconds": float(buffer), "depends_on": deps}

    for name, job in by_name.items():
        for dep in job["depends_on"]:
            if dep not in by_name:
                raise ValueError(f"{name} depends on missing job {dep}")

    visiting: set[str] = set()
    visited: set[str] = set()
    finish: dict[str, float] = {}
    predecessor: dict[str, str | None] = {}

    def visit(name: str) -> float:
        if name in visiting:
            raise ValueError(f"cycle detected at {name}")
        if name in visited:
            return finish[name]
        visiting.add(name)
        job = by_name[name]
        best_dep = None
        best_finish = 0.0
        for dep in job["depends_on"]:
            dep_finish = visit(dep)
            if dep_finish > best_finish:
                best_finish, best_dep = dep_finish, dep
        own = job["duration_seconds"] + job["buffer_seconds"]
        finish[name] = best_finish + own
        predecessor[name] = best_dep
        visiting.remove(name)
        visited.add(name)
        return finish[name]

    for name in by_name:
        visit(name)

    end_stage = max(finish, key=finish.get)
    total = finish[end_stage]
    critical_path = []
    current: str | None = end_stage
    while current is not None:
        critical_path.append(current)
        current = predecessor[current]
    critical_path.reverse()

    finish_at = start.timestamp() + total
    slack = deadline.timestamp() - finish_at
    return {
        "start": start.isoformat(),
        "deadline": deadline.isoformat(),
        "estimated_duration_seconds": total,
        "estimated_finish": datetime.fromtimestamp(finish_at, start.tzinfo).isoformat(),
        "slack_seconds": slack,
        "feasible": slack >= 0,
        "critical_path": critical_path,
        "stage_finish_offsets_seconds": finish,
        "assumption": "deterministic durations; dependencies only; no contention/retry/calendar model",
    }

def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} fixture.json", file=sys.stderr)
        return 2
    try:
        spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        print(json.dumps(analyze(spec), indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
```

### 8.1 Fixture

Save as `dag_fixture.json`:

```json
{
  "start": "2026-10-28T01:00:00Z",
  "deadline": "2026-10-28T02:00:00Z",
  "jobs": [
    {"name": "ingest", "duration_seconds": 600, "buffer_seconds": 60, "depends_on": []},
    {"name": "validate", "duration_seconds": 300, "depends_on": ["ingest"]},
    {"name": "features", "duration_seconds": 900, "buffer_seconds": 120, "depends_on": ["validate"]},
    {"name": "dimensions", "duration_seconds": 480, "depends_on": ["validate"]},
    {"name": "model-refresh", "duration_seconds": 600, "depends_on": ["features", "dimensions"]},
    {"name": "publish", "duration_seconds": 120, "depends_on": ["model-refresh"]}
  ]
}
```

`[SYNTHETIC]` The longest path is ingest → validate → features → model-refresh → publish, with buffers included. The script reports a deterministic finish estimate and slack. Exact output is derived by running the script; do not treat this fixture as a real schedule.

Run:

```bash
python3 dag_slack.py dag_fixture.json
```

### 8.2 Unit tests

Save as `test_dag_slack.py` in the same directory:

```python
import unittest
from dag_slack import analyze

BASE = {
    "start": "2026-10-28T01:00:00Z",
    "deadline": "2026-10-28T02:00:00Z",
    "jobs": [
        {"name": "a", "duration_seconds": 10, "depends_on": []},
        {"name": "b", "duration_seconds": 20, "depends_on": ["a"]},
        {"name": "c", "duration_seconds": 15, "depends_on": ["a"]},
        {"name": "d", "duration_seconds": 5, "depends_on": ["b", "c"]}
    ]
}

class DagTests(unittest.TestCase):
    def test_valid_parallel_dag(self):
        report = analyze(BASE)
        self.assertEqual(report["estimated_duration_seconds"], 35)
        self.assertEqual(report["critical_path"], ["a", "b", "d"])
        self.assertTrue(report["feasible"])

    def test_zero_slack_boundary(self):
        spec = {**BASE, "deadline": "2026-10-28T01:00:35Z"}
        report = analyze(spec)
        self.assertEqual(report["slack_seconds"], 0)
        self.assertTrue(report["feasible"])

    def test_negative_slack(self):
        spec = {**BASE, "deadline": "2026-10-28T01:00:34Z"}
        report = analyze(spec)
        self.assertEqual(report["slack_seconds"], -1)
        self.assertFalse(report["feasible"])

    def test_cycle(self):
        spec = {**BASE, "jobs": [
            {"name": "a", "duration_seconds": 1, "depends_on": ["b"]},
            {"name": "b", "duration_seconds": 1, "depends_on": ["a"]}]}
        with self.assertRaisesRegex(ValueError, "cycle"):
            analyze(spec)

    def test_missing_dependency(self):
        spec = {**BASE, "jobs": [
            {"name": "a", "duration_seconds": 1, "depends_on": ["missing"]}]}
        with self.assertRaisesRegex(ValueError, "missing"):
            analyze(spec)

    def test_invalid_duration(self):
        spec = {**BASE, "jobs": [
            {"name": "a", "duration_seconds": -1, "depends_on": []}]}
        with self.assertRaisesRegex(ValueError, "duration"):
            analyze(spec)

    def test_timezone_required(self):
        spec = {**BASE, "start": "2026-10-28T01:00:00"}
        with self.assertRaisesRegex(ValueError, "timezone"):
            analyze(spec)

    def test_duplicate_edge(self):
        spec = {**BASE, "jobs": [
            {"name": "a", "duration_seconds": 1, "depends_on": []},
            {"name": "b", "duration_seconds": 1, "depends_on": ["a", "a"]}]}
        with self.assertRaisesRegex(ValueError, "dependencies"):
            analyze(spec)

if __name__ == "__main__":
    unittest.main()
```

Run:

```bash
python3 -m unittest -v test_dag_slack.py
```

The tests cover a valid DAG, parallel branches, zero/negative slack, cycles, missing dependencies, negative duration, timezone-naive timestamps, and duplicate edges. This lesson does not claim these tests passed unless executed in the learner's environment. A production planner should also validate schema types, timezone policy, schedule calendars, uncertain duration quantiles, resource contention, retries, and critical-path ties.

### 8.3 Sample report template

```text
Dataset: <DATASET>
Deadline: <ISO_TIMESTAMP_WITH_TIMEZONE>
Estimated finish: <ISO_TIMESTAMP_WITH_TIMEZONE>
Estimated duration: <SECONDS>
Slack: <SECONDS> (positive = buffer; zero = boundary; negative = deadline at risk)
Critical path: <STAGE -> STAGE -> STAGE>
Largest uncertain contributors: <STAGES>
Assumptions: <DURATION_STATISTIC, DEPENDENCY_MODEL, RESOURCE MODEL>
Decision: <ON_TRACK / AT_RISK / INFEASIBLE>
Next evidence to collect: <METRICS, RUN HISTORY, OWNER>
```

---

## 9. Streaming and continuous-job monitoring

### 9.1 Signals that matter

- **Consumer lag in time:** delay between event time expected and event time processed/consumed. Record count lag can be misleading when event rates vary.
- **Watermark delay:** difference between current time and a defined event-time watermark.
- **Checkpoint age:** age of last successful checkpoint or durable progress marker.
- **Processing/input rate:** compare records/s or bytes/s over consistent windows; if sustained input exceeds processing, backlog can grow.
- **Restarts and progress:** restart counts matter when paired with stalled progress or lost state.
- **DLQ rate:** count/rate of records rejected or sent aside for later inspection.
- **Retry/replay behavior:** deliberate replay can temporarily increase lag or duplicate processing; monitor idempotency and bounded replay state.

Kafka-like exporter metrics are awareness only. Names and labels vary by platform/exporter/version `[VERIFY]`; do not make a specific platform a prerequisite for this local lab.

### 9.2 Local deterministic simulator

Save as `stream_sim.py`:

```python
#!/usr/bin/env python3
"""Local-only bounded stream-progress simulator; no network or broker required."""
import argparse
import json
import time

def simulate(mode: str, steps: int = 12) -> list[dict]:
    if steps < 1 or steps > 100:
        raise ValueError("steps must be between 1 and 100")
    backlog = 0
    rows = []
    event_watermark = 0
    checkpoint_age = 0
    for tick in range(steps):
        incoming = 12 if mode in {"burst", "replay"} and tick < 4 else 5
        processing = 4 if mode == "slow" else (15 if mode == "replay" else 6)
        dlq = 1 if mode == "bad-records" and tick % 3 == 0 else 0
        backlog = max(0, backlog + incoming - processing)
        # Watermark advances only when the simulated processor makes progress.
        if mode != "stalled":
            event_watermark += processing
            checkpoint_age = 0
        else:
            checkpoint_age += 1
        rows.append({
            "tick": tick, "input_records_per_tick": incoming,
            "processed_records_per_tick": processing, "backlog_records": backlog,
            "consumer_lag_seconds": backlog * 2,  # explicit synthetic conversion
            "watermark_delay_seconds": max(0, tick * 10 - event_watermark),
            "checkpoint_age_seconds": checkpoint_age * 10,
            "dlq_records": dlq, "mode": mode
        })
    return rows

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["normal", "burst", "replay", "slow", "stalled", "bad-records"], default="normal")
    parser.add_argument("--steps", type=int, default=12)
    args = parser.parse_args()
    for row in simulate(args.mode, args.steps):
        print(json.dumps(row, sort_keys=True))
```

Run a bounded set:

```bash
python3 stream_sim.py --mode normal --steps 12
python3 stream_sim.py --mode burst --steps 12
python3 stream_sim.py --mode replay --steps 12
python3 stream_sim.py --mode slow --steps 12
python3 stream_sim.py --mode stalled --steps 12
python3 stream_sim.py --mode bad-records --steps 12
```

The simulator's `consumer_lag_seconds = backlog * 2` is an explicit synthetic conversion, not a general rule. It exists to demonstrate the need to define units. The `replay` mode processes faster than input in the initial period to catch up; whether lag is healthy depends on trend and the replay plan.

### 9.3 Replay suppression

Represent a replay with dataset/pipeline, reason, owner, start, expiry, and expected backlog envelope. During replay, suppress only the alert whose semantics are intentionally violated, such as a transient lag threshold. Do not suppress DLQ correctness alerts, scheduler heartbeat, or all consumer-freshness alerts automatically. Test:
1. replay active and lag rising within expected envelope;
2. replay active but DLQ spikes;
3. replay expires while lag remains high;
4. replay metadata is missing or malformed.

After expiry, normal alerting resumes. A replay is not complete until the lag trend returns to the agreed operating range and downstream correctness checks pass.

---

## 10. Last-success registry service and spoofing prevention

A registry centralizes durable job outcome metadata so Prometheus can scrape it even after a short-lived job exits. It is also a dependency and security boundary: an unauthorized writer must not be able to claim a dataset is fresh.

### 10.1 Schema and rules

A registry record should contain:

```json
{
  "job": "synthetic-hourly",
  "pipeline": "orders",
  "dataset": "orders_hourly",
  "successful_commit_timestamp_seconds": 1760000000,
  "event_time_watermark_timestamp_seconds": 1759996400,
  "validation_status": "passed",
  "coverage_ratio": 1.0,
  "source_version": "fixture-v1",
  "updated_at_timestamp_seconds": 1760000001
}
```

All values are `[SYNTHETIC]`. Required invariants:

- A record is accepted only from an authenticated identity authorized for that job/dataset mapping.
- Validation status must be `passed`, coverage must be within its documented bounds, and commit timestamp must be valid.
- An older commit timestamp or older watermark must not silently overwrite newer accepted state.
- Replayed duplicate events are idempotent.
- The registry records update time separately from commit and event-time timestamps.
- Registry unavailability must be reported separately from pipeline staleness.
- Secrets never appear in labels, logs, or error responses.

### 10.2 Minimal local registry core

This standard-library implementation demonstrates update validation and monotonicity. It is not an HTTP service and has no authentication layer; it must remain local and be wrapped in an authenticated API before any shared use.

Save as `registry_core.py`:

```python
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class Record:
    job: str
    dataset: str
    commit_ts: float
    watermark_ts: float
    validation_status: str
    coverage_ratio: float
    source_version: str

class Registry:
    def __init__(self, allowed: dict[str, set[str]]):
        # stable job identity -> allowed datasets
        self.allowed = {job: set(datasets) for job, datasets in allowed.items()}
        self.records: Dict[str, Record] = {}

    def update(self, authenticated_job: str, record: Record) -> str:
        if record.job != authenticated_job:
            raise ValueError("job identity mismatch")
        if record.dataset not in self.allowed.get(authenticated_job, set()):
            raise PermissionError("job is not authorized for dataset")
        if record.validation_status != "passed":
            raise ValueError("validation must pass")
        if not (0.0 <= record.coverage_ratio <= 1.0):
            raise ValueError("coverage_ratio must be within [0, 1]")
        if record.commit_ts <= 0 or record.watermark_ts < 0:
            raise ValueError("invalid timestamp")
        old = self.records.get(record.dataset)
        if old:
            if record.commit_ts < old.commit_ts:
                raise ValueError("stale commit update")
            if record.watermark_ts < old.watermark_ts:
                raise ValueError("watermark regression")
            if record.commit_ts == old.commit_ts and record == old:
                return "duplicate"
        self.records[record.dataset] = record
        return "updated"

    def read(self, dataset: str) -> Record | None:
        return self.records.get(dataset)
```

### 10.3 Registry tests

Save as `test_registry_core.py`:

```python
import unittest
from registry_core import Registry, Record

def record(commit=100, watermark=90, dataset="d1", job="j1",
           validation="passed", coverage=1.0):
    return Record(job, dataset, commit, watermark, validation, coverage, "fixture-v1")

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = Registry({"j1": {"d1"}, "j2": {"d2"}})

    def test_successful_update_and_read(self):
        self.assertEqual(self.registry.update("j1", record()), "updated")
        self.assertEqual(self.registry.read("d1").commit_ts, 100)

    def test_invalid_validation_rejected(self):
        with self.assertRaisesRegex(ValueError, "validation"):
            self.registry.update("j1", record(validation="failed"))

    def test_stale_commit_rejected(self):
        self.registry.update("j1", record(commit=100, watermark=90))
        with self.assertRaisesRegex(ValueError, "stale commit"):
            self.registry.update("j1", record(commit=99, watermark=90))

    def test_duplicate_event_idempotent(self):
        self.registry.update("j1", record())
        self.assertEqual(self.registry.update("j1", record()), "duplicate")

    def test_spoofed_dataset_rejected(self):
        with self.assertRaises(PermissionError):
            self.registry.update("j1", record(dataset="d2", job="j1"))

    def test_job_identity_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity"):
            self.registry.update("j2", record(job="j1", dataset="d1"))

    def test_coverage_out_of_range_rejected(self):
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.registry.update("j1", record(coverage=1.2))

    def test_watermark_regression_rejected(self):
        self.registry.update("j1", record(commit=100, watermark=90))
        with self.assertRaisesRegex(ValueError, "watermark"):
            self.registry.update("j1", record(commit=101, watermark=89))

if __name__ == "__main__":
    unittest.main()
```

Run:

```bash
python3 -m unittest -v test_registry_core.py
```

The core tests are expected to exercise update, invalid update, stale update, duplicate/replayed event, read behavior, and spoofing prevention. They do not test HTTP authentication, durable storage, concurrency, registry recovery, or exporter exposition. Add those tests before using a real service.

### 10.4 Registry availability behavior

Expose separate health signals for the registry service and each dataset record. If the registry cannot be scraped, alert on telemetry availability; do not transform missing data into “fresh.” If the registry is available but a dataset's last valid commit is old, alert on pipeline freshness. Consider durable storage, backup, schema migration, writer authentication, authorization audit logs, and recovery reconciliation.

---

## 11. Silent semantic failures and canary records

A run can be recent and valid according to basic schema checks yet still compute the wrong value, drop a subset of records, use a stale dimension table, or fail to deliver data to consumers. A known-answer canary is a synthetic record whose expected result is controlled and checked at each important stage.

### 11.1 Canary design

`[SYNTHETIC]` Define a test-only record with a non-sensitive deterministic key:

```json
{
  "canary_key": "canary-order-0001",
  "source_value": 7,
  "expected_transformed_value": 14,
  "expected_partition": "canary-partition"
}
```

The pipeline should verify:
1. source fixture contains exactly one canary;
2. transform produces the expected value;
3. output manifest contains the expected partition;
4. durable commit includes the canary;
5. consumer reads/acknowledges the committed canary;
6. duplicate delivery is detected or safely idempotent.

Do not inject canaries into real customer data without an approved design. Keep canary data segregated or clearly marked, and ensure it cannot contaminate business aggregates.

### 11.2 Reconciliation and drift

Useful checks include:
- source count versus output count with documented filtering rules;
- expected partition list versus committed partition manifest;
- sum/count reconciliation for appropriate additive metrics;
- key uniqueness and duplicate-rate checks;
- schema/domain validation;
- distributions of bounded, privacy-safe values;
- cross-system consistency where the source of truth is independent;
- canary arrival, transformation, and consumer acknowledgement.

A distribution shift is a signal, not automatic proof of failure. Seasonality, business events, and intentional model/data changes can change distributions.

### 11.3 Canary test cases

| Case | Expected signal | First check |
|---|---|---|
| Canary missing | Count zero / validation failure | Source fixture and filtering path |
| Canary late | Deadline/arrival age breached | Queue lag, stage progress, source delay |
| Canary duplicated | Duplicate key count > 0 | Retry behavior and sink idempotency |
| Canary transformed incorrectly | Expected value mismatch | Transformation version and unit test |
| Canary present but not consumed | Commit exists, consumer acknowledgement absent | Delivery/consumer state, offsets/receipt |

### 11.4 Diagnostic decision tree

```text
Canary failed?
  ├─ Not in source -> source fixture/generator or source delay
  ├─ In source, absent after transform -> filter/join/transformation
  ├─ Present but wrong value -> transformation/version/configuration
  ├─ Correct in staging, absent in committed manifest -> commit/publish boundary
  ├─ Committed but not acknowledged -> delivery/consumer lag
  └─ Multiple copies -> retry/replay/idempotency
```

Record the observation, hypothesis, discriminating test, owner, and regression test. Never conclude “data corruption” from a missing canary until the expected source and stage telemetry are verified.

---

## 12. Required practical labs

All labs are local-only and bounded. Save evidence in a dedicated scratch directory, for example `./m11-unit11-evidence/`. Do not use production data or alter the host clock. Every time measurement is a **laptop measurement—not a production guarantee**.

### Lab A — Instrumented batch job using Pushgateway and textfile collector

**Purpose:** demonstrate how one synthetic batch run can expose the same stable run-state contract through two patterns.

**Prerequisites:** Python 3; optional local Prometheus, Pushgateway, node-exporter with textfile collector. Component versions and command-line flags are `[VERIFY]`.

**Procedure:**

1. Run the `batch_demo.py` program from Section 3 in a disposable directory.
2. Inspect `job-state.json`; confirm the success timestamp only changes after validation and output commit.
3. Add a textfile writer that exports the fields in the metric contract. Write to a temporary file and rename it into the configured collector directory.
4. If Pushgateway is available, push only stable job/dataset/environment grouping keys. Verify exact push URL/API behavior against installed Pushgateway documentation `[VERIFY]`.
5. Test safe cleanup of the exact group created by this lab. Never delete a shared group or use a broad wildcard cleanup command.
6. Inject the modes below, recording expected and observed signals. DST is simulated by passing two logical schedule events with the same window key; do not change host time.

A textfile exporter should be generated from the trusted `job-state.json`, not from hard-coded success values. Save as `render_textfile.py`:

```python
#!/usr/bin/env python3
import json
import os
import tempfile
from pathlib import Path

state_path = Path(os.environ.get("BATCH_STATE_FILE", "./batch-demo/job-state.json"))
textfile_dir = Path(os.environ.get("TEXTFILE_DIR", "./textfile")).resolve()
destination = textfile_dir / "batch_job.prom"
state = json.loads(state_path.read_text(encoding="utf-8"))

# Fixed, allowlisted label values for this lab; never insert run IDs or user input.
labels = 'job="synthetic-hourly",dataset="demo",env="local"'
lines = [
    f"job_last_success_timestamp_seconds{{{labels}}} {float(state['last_success_timestamp_seconds'])}",
    f"job_last_run_timestamp{{{labels}}} {float(state['last_run_timestamp_seconds'])}",
    f"job_last_duration_seconds{{{labels}}} {float(state['last_duration_seconds'])}",
    f"job_rows_processed{{{labels}}} {int(state['rows_processed'])}",
    f"job_partition_coverage_ratio{{{labels}}} {float(state['partition_coverage_ratio'])}",
    f"job_data_watermark_timestamp_seconds{{{labels}}} {float(state['watermark_timestamp_seconds'])}",
]
textfile_dir.mkdir(parents=True, exist_ok=True)
fd, temp_name = tempfile.mkstemp(prefix=".batch_job.", suffix=".prom", dir=textfile_dir)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write("\\n".join(lines) + "\\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_name, destination)
except Exception:
    try:
        os.unlink(temp_name)
    except FileNotFoundError:
        pass
    raise
print(destination)
```

Run it after a successful synthetic run:

```bash
python3 batch_demo.py
python3 render_textfile.py
cat ./textfile/batch_job.prom
```

A failed validation deliberately leaves the previous `job-state.json` success values intact. In a real system, also expose the most recent attempt's failure state through a separate event/metric contract; do not overwrite last valid success just to show the failure.

For Pushgateway, the exact URL and grouping-key syntax must be checked against the installed version `[VERIFY]`. A typical lab interaction may use an explicit stable grouping key, with a URL shaped like this:

```bash
export PUSHGATEWAY_URL="<PUSHGATEWAY_URL>"
# The rendered file is the payload; do not put run IDs in the grouping key.
curl --fail --data-binary @./textfile/batch_job.prom \\
  "$PUSHGATEWAY_URL/metrics/job/synthetic-hourly/dataset/demo/env/local"
# After confirming this is the exact disposable lab group, delete only that group:
curl --fail -X DELETE \\
  "$PUSHGATEWAY_URL/metrics/job/synthetic-hourly/dataset/demo/env/local"
```

These commands are `[VERIFY]` examples, not evidence that a gateway is running. Use authentication/TLS options required by your environment, never put credentials in shell history or lesson output, and do not send data to an unknown endpoint. Before cleanup, inspect the exact grouping key and verify it belongs only to this lab.

| Fault mode | Injection | Expected evidence |
|---|---|---|
| Late | Sleep a bounded amount in the local wrapper, e.g. at most 3 seconds | Start/deadline difference in logs |
| Hung | Use a wrapper with `timeout 5s` around a deliberately bounded sleep of 10 seconds | Timeout and no success timestamp advancement |
| Empty | `BATCH_FAULT=empty` | Validation failure; prior success preserved |
| Partial | `BATCH_FAULT=partial` | Coverage/partition validation failure |
| Duplicate | `BATCH_FAULT=duplicate` | Duplicate logical key rejected |
| Stale metric | Leave old fixture state and compare its timestamp with current time | Freshness rule fires or test flags stale state |
| DST double-run | Feed same logical schedule window twice with different attempt IDs | Idempotency/duplicate detection catches duplicate logical window |

**Alert tests:** add firing/no-fire fixtures for each fault mode. Use `promtool check rules` and `promtool test rules` where installed; syntax is `[VERIFY]`. If no telemetry stack is available, write a Python assertion script that checks the expected JSON state and preserves the previous success on failure.

**Expected observation:** textfile and Pushgateway are transport patterns, not sources of semantic truth. The job's commit/validation contract must remain identical.

**Validation/evidence:** save sanitized JSON state before/after, rendered `.prom` file, alert test output, and a short note identifying which signal proved each condition.

**Cleanup:** remove only the lab's temporary directory and exact Pushgateway group created by the lab. Do not clear shared state.

**Troubleshooting:** verify timestamps are seconds, labels are bounded, exporter target is up, textfile path is configured, and no half-written destination is visible. If components are unavailable, use fixtures.

**Acceptance criteria:** all seven fault modes have a documented expected signal, no invalid run advances last-success, the `.prom` file is atomically replaced, and alert tests cover at least one firing and one no-fire case per supported rule.

### Lab B — Kubernetes CronJob monitoring

**Purpose:** distinguish Kubernetes execution state from application-level freshness and validity.

**Prerequisites:** kind and kubectl are optional; a disposable cluster only. Check `kind --version`, `kubectl version --client`, and the installed kube-state-metrics documentation `[VERIFY]`.

**Procedure:**

1. If a safe local cluster exists, create a dedicated namespace `<NAMESPACE>` and a trivial image/job that writes only synthetic output.
2. Create a CronJob with a conservative schedule and explicit history/concurrency policy. Exact API fields and policy behavior must be checked against the Kubernetes version `[VERIFY]`.
3. Observe Job/CronJob state and kube-state-metrics series. Discover actual metric names/labels; do not assume the examples in Section 5 exist.
4. Test a normal completion, non-zero exit, a deliberately bounded long run, suspended schedule, and overlapping trigger in a disposable namespace.
5. Correlate each case with application-level validation/commit metrics and the schedule registry.

**Fixture fallback:** use JSON objects representing `expected`, `active`, `failed`, `succeeded`, `suspended`, and `overlap` states, then run the same decision table without a cluster.

**Expected observation:** Job completion is execution evidence; only application validation/commit/watermark signals establish data health.

**Validation/evidence:** save sanitized `kubectl get jobs,cronjobs -o yaml` output if used, series names, rule test results, and runbook outcome.

**Cleanup:** delete only the lab namespace after verifying its name. Do not run cluster-wide destructive commands.

**Troubleshooting:** if no metric appears, verify scrape configuration, kube-state-metrics installation/version, namespace filtering, and label names. No series does not mean no job exists.

**Acceptance criteria:** alerts or fixture checks cover missed/late, failed, long-running, suspended, and overlap states; every case distinguishes exporter/controller telemetry from application success.

### Lab C — Freshness/deadline dashboard

**Purpose:** make per-dataset status and consumer impact visible.

**Prerequisites:** Grafana/Prometheus optional; fixtures sufficient.

**Procedure:**

1. Implement panels from Section 7.
2. Use catalog fixture entries for dataset, owner, schedule/calendar, threshold, consumer, and runbook.
3. Add annotations for a planned backfill and a simulated missed run.
4. Display commit age and event-time watermark age separately.
5. Add a “telemetry missing” state; do not render no-data as zero age.
6. Add DAG critical path/slack output from Lab D.

**Expected observation:** one dataset may have recent commit time but stale event-time watermark, or good freshness but incomplete coverage.

**Validation/evidence:** screenshot/export of dashboard JSON if available, panel definitions, fixture data, and a written interpretation of two divergent cases.

**Cleanup:** delete only the lab dashboard/data source if created solely for the exercise.

**Troubleshooting:** check timestamp units, label joins, timezone display, and whether the panel is showing latest state or an aggregation over repeated gauge samples.

**Acceptance criteria:** all required panel families exist; commit time and watermark are not conflated; missing data is explicit; every critical dataset has owner and runbook context.

### Lab D — DAG slack/critical-path script

**Purpose:** calculate deterministic deadline feasibility and identify the longest dependency chain.

**Prerequisites:** Python 3; standard library only.

**Procedure:**

1. Save `dag_slack.py`, `dag_fixture.json`, and `test_dag_slack.py` from Section 8 into one scratch directory.
2. Run `python3 -m unittest -v test_dag_slack.py`.
3. Run `python3 dag_slack.py dag_fixture.json`.
4. Change the deadline to exactly the predicted finish and then to one second earlier.
5. Add a cycle, missing dependency, duplicate edge, negative duration, and timezone-naive timestamp to separate test fixtures.
6. Compare estimated critical-path contributors with actual run-stage history if a local pipeline exists.

**Expected observation:** parallel branches contribute through their longest predecessor chain; summing all branches overestimates elapsed time. The result is deterministic, not a probabilistic guarantee.

**Validation/evidence:** test output, fixture, sample report, and explicit assumptions.

**Cleanup:** remove only scratch fixtures when evidence has been retained.

**Troubleshooting:** check timezone offsets, duplicate node names, unknown dependencies, and cycle reports.

**Acceptance criteria:** tests cover valid parallel DAG, zero/negative slack, cycle, missing dependency, invalid duration, duplicate edge, and timezone-aware input; output names the critical path and slack sign convention.

### Lab E — Streaming-consumer monitoring

**Purpose:** compare normal progress, burst, replay, slow processing, stall, and DLQ growth.

**Prerequisites:** Python 3; no broker required.

**Procedure:**

1. Save `stream_sim.py` from Section 9.
2. Run all six bounded modes with `--steps 12`.
3. Compare input rate, processing rate, backlog, lag seconds, watermark delay, checkpoint age, and DLQ records.
4. Define a replay window with a start and expiry in a fixture; ensure only the intended lag alert is temporarily suppressed.
5. Simulate expiry while lag remains high and confirm normal alerting resumes.

**Expected observation:** a temporary backlog during replay differs from a steadily growing backlog after replay expiry. A stalled watermark/checkpoint can expose a failure that a process heartbeat alone misses.

**Validation/evidence:** JSONL output, a small comparison table, alert test results, and the chosen replay policy.

**Cleanup:** no external resources; remove scratch output.

**Troubleshooting:** remember simulator units are deliberately synthetic and not calibrated to a real stream engine.

**Acceptance criteria:** all progress signals are defined with units; replay suppression is bounded and expires; DLQ and correctness alerts are not globally muted.

### Lab F — Last-success registry + exporter

**Purpose:** test durable-state update invariants and spoofing controls.

**Prerequisites:** Python 3; no HTTP server required for the core exercise.

**Procedure:**

1. Save `registry_core.py` and `test_registry_core.py` from Section 10.
2. Run `python3 -m unittest -v test_registry_core.py`.
3. Add fixtures for stale commit, watermark regression, unauthorized job/dataset mapping, duplicate event, invalid validation, and registry read after update.
4. Design an exporter that reads only the registry and exposes stable metrics. Keep authentication at the API boundary; do not treat the in-memory class as an authenticated service.
5. Simulate registry unavailable separately from a stale dataset record.

**Expected observation:** stale or unauthorized state cannot overwrite the last valid record; registry health and pipeline freshness are separate signals.

**Validation/evidence:** test output, schema, access-control matrix, and a registry-down versus dataset-stale decision table.

**Cleanup:** remove local state; no external resources are required.

**Troubleshooting:** test that caller identity is authenticated by the wrapper and not merely copied from request JSON. Use an allowlisted identity-to-dataset mapping.

**Acceptance criteria:** tests cover successful update, invalid update, stale update, duplicate/replayed event, read/export, identity mismatch, and spoofed dataset. Document missing durability/authentication in the local core.

### Lab G — Freshness SLO as a time-slice SLI

**Purpose:** classify good/bad/unknown time slices and reuse M10 burn-rate semantics.

**Prerequisites:** M10 freshness SLO definition and Prometheus/promtool optional.

**Procedure:**

1. Write a fixture with one-minute samples for valid commit age, watermark age, coverage, and telemetry presence.
2. Classify slices using the dataset contract.
3. Create a bad-minute recording rule and burn-rate alert consistent with M10's established policy.
4. Test fresh/good, stale/bad, missing/unknown, and planned-backfill/expired cases.
5. If using Prometheus, verify syntax with installed `promtool` `[VERIFY]`.

**Expected observation:** unknown telemetry is not silently counted as good. Planned maintenance is scoped and expires.

**Validation/evidence:** classification table, rules, test output, and explanation of the reused M10 policy.

**Cleanup:** remove only test rule files or test series.

**Troubleshooting:** align time-slice interval, sample cadence, and label scope; test `absent()` explicitly.

**Acceptance criteria:** tests cover good/bad/missing periods, alert context, scoped suppression, and suppression expiry; no SLO math is redefined inconsistently with M10.

### Lab H — Silent-failure canary pipeline

**Purpose:** detect semantically incorrect output even when the process succeeds.

**Prerequisites:** Section 11 synthetic canary fixture.

**Procedure:**

1. Pass a synthetic known-answer record through source, transform, commit, and consumer stages.
2. Assert its expected transformed value and partition.
3. Inject missing, late, duplicated, incorrectly transformed, and committed-but-not-consumed variants.
4. Correlate stage events with validation/coverage metrics.
5. Add a regression test for each failure.

**Expected observation:** each failure maps to a different stage and next check; one generic “job failed” alert is insufficient.

**Validation/evidence:** sanitized fixture, assertion output, alert/runbook mapping, and known-answer expectation.

**Cleanup:** delete only the test dataset and ensure canary records cannot enter real aggregates.

**Troubleshooting:** verify the canary is not filtered by design and that consumer acknowledgment is independently measured.

**Acceptance criteria:** all five fault variants are detected or explicitly classified unknown; wrong output cannot update a “fully healthy” status.

### Lab I — Six-class pipeline chaos matrix

**Purpose:** measure detection behavior under safe, deterministic failures.

**Safety rules:** use only synthetic fixtures and a disposable directory/namespace. Never fill the host disk, alter host clock, overload a shared service, or inject faults into real data. A “full volume” scenario must be a small quota-limited temporary filesystem/container volume or a mocked storage error, with a strict cap.

| Failure class | Safe injection | Expected signal | Recovery/prevention |
|---|---|---|---|
| Source/input delay | Hold fixture release for a bounded interval | Source heartbeat/watermark stale; deadline risk | Verify source contract and catch-up |
| Scheduler hang/missed trigger | Omit one expected event in fixture or stop disposable scheduler | Expected run absent; scheduler heartbeat stale if applicable | Restart safely, reconcile missed logical window |
| Corrupt/empty/partial partition | Alter synthetic manifest or output fixture | Validation/canary/coverage failure | Quarantine, repair, idempotent rerun |
| Duplicate trigger/DST double-run | Submit same logical window twice | Duplicate logical key or duplicate output count | Enforce unique key/idempotent sink |
| Clock/DST/calendar mismatch | Inject a fake clock/timezone into test code | Expected-run mismatch or invalid timestamp | Fix calendar/timezone policy; never change host clock |
| Resource/dependency pressure | Inject a bounded sleep/error or quota-limited temporary storage failure | Duration, retry, deadline, resource signal | Remove fault; verify recovery and rerun safety |

For each test, fill this record:

```text
Failure class:
Injection:
Expected signal/alert:
Detection start definition:
Detection end definition:
Time-to-detect = end - start:
Observed outcome:
Evidence links:
Recovery:
Cleanup verified:
Prevention/regression test:
Laptop measurement—not production guarantee:
```

Do not fill time-to-detect with invented values. Measure it only when the learner executes the test. Define start as the first timestamp at which the injected failure meets the stated condition, and end as the first timestamp the alert/monitoring system detects it; separately record notification delivery delay if relevant.

**Validation/evidence:** completed matrix with actual measured results or “not run,” fixture, test output, and cleanup confirmation.

**Cleanup:** stop only lab processes, remove the disposable namespace/directory, and confirm no background loop remains.

**Troubleshooting:** if detection did not occur, inspect expected-series inventory, scrape health, label scope, alert evaluation interval, `for` duration, and schedule registry.

**Acceptance criteria:** all six classes have an injection, expected signal, measured or explicitly unmeasured time-to-detect, recovery, cleanup, and prevention control.

### Lab J — Runbook validation

**Purpose:** verify that an operator can resolve one injected freshness/deadline fault safely.

**Runbook decision tree:**

```text
Alert: freshness/deadline breached
  1. Is the dataset expected to run now? Check calendar and suppression expiry.
  2. Did the scheduler emit the expected run? Check heartbeat and schedule registry.
  3. Did an attempt start and finish? Check run state, logs, and trace if available.
  4. Did validation pass and did output commit? Check manifest/commit metadata.
  5. Is event-time watermark current? Check source delay, queue/stream progress.
  6. Is coverage complete and canary correct? Check partitions and reconciliation.
  7. Is the issue resource/dependency-related? Check Unit 9 saturation and Unit 10 traces.
  8. Is downstream consumption current? Check consumer acknowledgement/lag.
  9. Can the logical window be rerun idempotently? Verify dry-run and unique keys.
 10. Is a backfill required? Scope it, assign owner, set expiry, and preserve normal alerting.
```

**Procedure:** choose one fault from Lab I; follow the tree without reading the injection label if possible; capture the first check, evidence, mitigation decision, and verification. Use dry-run first. Never rerun a non-idempotent pipeline blindly.

**Validation/evidence:** completed incident template, commands/queries used, result, and follow-up regression test.

**Cleanup:** restore the fixture and remove suppression metadata.

**Troubleshooting:** if the runbook depends on a missing dashboard, missing owner, or unavailable registry, record that as an operational gap rather than guessing.

**Acceptance criteria:** the learner distinguishes process failure, invalid commit, stale input, scheduler failure, resource/dependency issue, and downstream consumption; rerun/backfill has idempotency and stop conditions.

---

## 13. Fleet-scale freshness operations and governance

### 13.1 Dataset catalog as the control plane

Maintain a catalog for every critical dataset:

```yaml
dataset: "<DATASET>"
owner: "<OWNER>"
criticality: "tier-1"
consumers:
  - "<CONSUMER>"
schedule_calendar: "<CALENDAR_ID>"
timezone: "UTC"
expected_schedule_source: "<REGISTRY_OR_ORCHESTRATOR>"
freshness_threshold_seconds: 5400  # [ILLUSTRATIVE]
deadline_policy: "<POLICY_ID>"
source_dependencies:
  - "<SOURCE_DATASET>"
validation_rules:
  - "partition_coverage"
  - "known_answer_canary"
runbook: "<RUNBOOK_URL>"
lineage_ref: "<LINEAGE_ID>"
```

A schema validator should reject missing owner, missing runbook, unbounded metric dimensions, invalid thresholds, unknown calendar IDs, and invalid suppression policy. Generate alert rules and dashboard variables from this catalog so the same owner and threshold are not copied by hand into many files.

### 13.2 Consumer-impact-aware severity

Severity should reflect:
- whether the dataset is customer/business critical;
- how many downstream consumers are blocked;
- how close the deadline is and whether slack is negative;
- whether an alternative source or safe degraded mode exists;
- whether data is stale versus merely delayed but still within grace;
- whether the signal is trusted or telemetry is missing.

A freshness issue in a non-critical analytical table may be a ticket; stale data powering a customer-facing decision path may warrant paging. Use lineage and ownership metadata rather than guessing from dataset name.

### 13.3 Weekly freshness report

A report should contain:
- SLO attainment by dataset and owner;
- datasets with freshness/deadline breaches;
- top recurrent late-run causes;
- run duration trends and missed schedules;
- watermark and consumer lag trends;
- validation/coverage/canary failures;
- incidents and time-to-detect/resolve;
- suppressions/backfills that expired or repeatedly extended;
- missing owner/runbook/catalog entries;
- corrective actions with owner and due date.

Do not invent report values. The output template can use placeholders until telemetry exists.

### 13.4 Scale to thousands of jobs

- Keep metric labels bounded; put per-run IDs in logs/traces.
- Use consistent job/dataset naming and a catalog as the inventory source.
- Generate rules with schema validation and deterministic output; test generated files before deployment.
- Group alerts by owner, pipeline, and incident window to reduce notification storms.
- Verify Pushgateway scaling/sharding and intended use against current official docs `[VERIFY]`; avoid one group per run.
- Monitor registry availability, read/write latency, stale records, and reconciliation backlog.
- Make exporter and orchestrator adapters replaceable behind a stable run-event/registry contract where feasible.
- Treat OpenLineage event schemas and integrations as version-sensitive awareness `[VERIFY]`; validate the installed version's official documentation.
- Apply business calendars and DST policy centrally.
- Compare the cost/benefit of tighter freshness targets: stricter targets can require more compute, retries, replication, and on-call response. Do not invent monetary savings or prices; measure the actual trade-off.

### 13.5 Generated-rule validation

A safe generation pipeline should:
1. validate catalog schema and owner/runbook completeness;
2. reject forbidden/high-cardinality label dimensions;
3. generate deterministic rule and dashboard files;
4. run syntax checks and unit tests;
5. diff generated output and require review for material changes;
6. test no-data, stale-series, and decommission behavior;
7. deploy gradually and monitor false positives;
8. retain the catalog version used to generate each release.

---

## 14. Required incident analyses: diagnose → fix → prevent

All incident narratives and evidence below are `[SYNTHETIC]`; they are teaching cases, not real incident reports. For each, observation is not the same as hypothesis, and a controlled reproduction is required before claiming cause.

### Case 1 — Exit `0`, zero rows; run-time freshness green for two days

**Observation:** run timestamps update every hour and the process exits `0`. Row count is zero; the last-success metric is incorrectly updated at process exit. Consumer reports missing records.

**Hypothesis:** a source filter or input delay yields empty output, and the instrumentation treats process success as data success.

**First checks:** compare `job_rows_processed`, validation events, source counts, committed manifest, and watermark; inspect the code path that updates last-success.

**Controlled reproduction:** run the empty fixture and verify whether the success timestamp advances. If it does, the metric contract is broken.

**Fix:** move success update after validation and durable commit; make non-empty expectation dataset-specific; alert on validation and canary failure.

**Before/after evidence:** last-success must remain unchanged for invalid output; record validation failure and coverage state; compare freshness/consumer status after a valid run.

**Prevent:** unit test empty output, code review checklist, and metric-contract test.

### Case 2 — Pushgateway retained success from decommissioned job

**Observation:** last-success remains recent even though the job was removed from the schedule.

**Hypothesis:** Pushgateway retained the group's series and alert rules treat its presence as current health.

**First checks:** inspect grouping keys, deployment inventory, target status, group lifecycle, and decommission metadata.

**Controlled reproduction:** in a lab-only group, push a synthetic series, stop pushing, and verify whether it persists; then test exact cleanup behavior using installed documentation `[VERIFY]`.

**Fix:** add lifecycle/decommission cleanup and an independent expected-job inventory/lease; alert on stale registry state and missing expected schedule, not series presence alone.

**Before/after evidence:** decommissioned fixture no longer appears as an active dataset; stale success cannot satisfy the current expected-run contract.

**Prevent:** group ownership, exact cleanup procedure, retention review, and a test for removed jobs.

### Case 3 — DST double-run doubled output

**Observation:** two attempts process the same logical daily window and output count doubles around a daylight-saving transition.

**Hypothesis:** scheduler retry/calendar ambiguity and a non-idempotent sink allow the same logical window to commit twice.

**First checks:** inspect timezone, scheduler run history, logical window keys, sink uniqueness, and duplicate-output metric.

**Controlled reproduction:** submit two fixture events with different attempt IDs but the same logical window key; never alter host clock.

**Fix:** define timezone/DST policy; use a stable logical window key and idempotent upsert/unique constraint; emit duplicate detection.

**Before/after evidence:** second attempt is treated as duplicate/idempotent, row count remains correct, and alert/test catches a deliberately non-idempotent fixture.

**Prevent:** DST calendar test matrix, retry contract, and uniqueness constraints.

### Case 4 — Freshness alert fired during backfill; team muted it and missed next real run

**Observation:** alert was globally muted during planned backfill; a subsequent current-window run was missed without notification.

**Hypothesis:** suppression scope was too broad or had no expiry.

**First checks:** inspect silence scope/expiry, planned-backfill record, expected schedule, and alert history.

**Controlled reproduction:** create a scoped replay/backfill fixture and separately omit a current logical run; verify only the intended alert is suppressed.

**Fix:** scope suppression by dataset/window/alert family, require owner/reason/expiry, and notify on expiry.

**Before/after evidence:** planned work does not page for the agreed signal; unrelated missed run still fires; expired suppression resumes alerting.

**Prevent:** suppression schema validation and alert-rule tests.

### Case 5 — Scheduler hung; no alert until deadline passed

**Observation:** no job is active and no alert fired before the expected deadline.

**Hypothesis:** scheduler heartbeat was not monitored, or expected-run telemetry was emitted only by the job itself.

**First checks:** scheduler logs/heartbeat, schedule registry, worker queue, and expected next run.

**Controlled reproduction:** stop the disposable scheduler process while retaining an independent heartbeat expectation.

**Fix:** monitor scheduler health independently and emit expected-run/deadline metadata outside the job process.

**Before/after evidence:** heartbeat alert detects scheduler loss before the next run deadline when its threshold permits; missed-run alert still fires at deadline.

**Prevent:** independent control-plane monitoring and failure-mode tests.

### Case 6 — Partial partition load passed run-level success

**Observation:** job status is success, but only 9 of 10 expected partitions are committed.

**Hypothesis:** success is recorded before coverage validation or the run-level metric hides partial output.

**First checks:** expected partition manifest, committed manifest, coverage ratio, and validation logs.

**Controlled reproduction:** remove one partition from the fixture and run the validation gate.

**Fix:** validate expected coverage before publishing success; retain partition-level evidence in manifest/logs rather than metric labels.

**Before/after evidence:** incomplete coverage prevents last-success advancement or marks the dataset invalid; full coverage passes.

**Prevent:** coverage tests and alert for partial commit.

### Case 7 — `absent()` selector never fires because labels are scoped incorrectly

**Observation:** expected missing-dataset alert does not fire when one dataset disappears.

**Hypothesis:** selector is too broad/narrow, label values changed, or `absent()` cannot synthesize the expected per-dataset label set.

**First checks:** inspect raw series/labels, evaluate the expression directly, and test a known missing selector.

**Controlled reproduction:** remove one fixture series and compare exact selector results using `promtool`/Prometheus `[VERIFY]`.

**Fix:** derive expected datasets from a catalog/inventory metric or generate one exact missing-series rule per critical dataset where appropriate.

**Before/after evidence:** test proves each expected dataset's absence is detected and unrelated datasets do not match.

**Prevent:** label-scope tests and rule review.

### Case 8 — Textfile collector read a half-written file

**Observation:** scrape sees malformed or partially updated metric output.

**Hypothesis:** the job writes directly to the destination while a scrape can read it.

**First checks:** inspect writer code, file permissions, timestamps, exporter logs, and exposition parser errors.

**Controlled reproduction:** use a test writer to write a partial temporary file, then replace destination only after completion; validate scrape never sees partial destination.

**Fix:** same-directory temp file plus atomic replacement, trusted directory permissions, and file-content validation.

**Before/after evidence:** repeated scrape during updates sees either previous complete file or next complete file, not an intermediate partial file, under the tested filesystem behavior `[VERIFY]`.

**Prevent:** shared helper, test, and stale-file alert.

---

## 15. Runbook, verification, and source hygiene

### 15.1 Runbook template

```text
Alert:
Impact / affected consumers:
Dataset / pipeline:
Owner:
Runbook version:
Last valid committed success:
Event-time watermark and age:
Expected schedule / deadline / grace:
Coverage and validation status:
Recent run state / run ID (logs/traces only):
Scheduler heartbeat:
Exporter/registry health:

First checks:
1. Confirm the dataset is expected to run under the current calendar.
2. Check expected-run/deadline metadata and suppression expiry.
3. Check scheduler heartbeat independently of job state.
4. Check attempt start/finish, failure stage, and structured logs.
5. Check validation, committed manifest, coverage, and canary.
6. Check event-time watermark and source/queue/stream lag.
7. Check Unit 9 resource saturation and Unit 10 trace evidence if relevant.
8. Check downstream consumer receipt/lag.

Decision tree:
- Did it run?
- Did validation pass and did output commit?
- Is the input/event-time watermark fresh?
- Is partition coverage complete and correctness canary passing?
- Is scheduler/orchestrator healthy?
- Is the issue upstream, resource-related, or downstream?
- Can the same logical window be rerun idempotently?
- Is a backfill required and safely scoped?

Safe mitigation:
- Use dry-run first.
- Verify idempotency key and current commit state.
- Quarantine invalid output rather than publishing it.
- Preserve prior last-valid-success state.
- Scope any backfill suppression and set expiry.
- Stop if output commit state is ambiguous or duplicate risk is unresolved.

Rerun/backfill procedure:
<APPROVED_COMMAND_OR_WORKFLOW>
Dry-run result:
Idempotency verified by:
Rollback/stop conditions:
Verification after mitigation:
- valid commit timestamp advanced only after validation/commit
- event-time watermark meets contract
- coverage and canary pass
- downstream consumer acknowledges expected output
Evidence links:
Follow-up owner and due date:
```

### 15.2 Version and installation checks

Run only where tools are installed and commands are appropriate to the environment `[VERIFY]`:

```bash
prometheus --version
promtool --version
promtool check rules ./rules.yml
promtool test rules ./rules_test.yml
kubectl version --client
kind --version
python3 --version
python3 -m pip show prometheus-client
```

For Kubernetes, kube-state-metrics, Pushgateway, node-exporter textfile collector, Python client, and orchestrator details:
1. inspect installed versions and configuration;
2. read the matching official documentation;
3. inspect available metrics/labels in the running instance;
4. test the behavior in a disposable environment;
5. record the tested version and assumptions with the rule/lesson.

Official documentation areas to consult:
- Prometheus documentation: querying basics, functions (`time`, `absent`, `absent_over_time` where available), recording/alerting rules, and unit testing with `promtool` `[VERIFY]`.
- Pushgateway official README/documentation: intended use, grouping keys, deletion/cleanup, persistence, and security `[VERIFY]`.
- Prometheus node-exporter documentation: textfile collector usage and file exposition expectations `[VERIFY]`.
- Kubernetes official documentation: CronJobs, time zones, concurrency policy, suspension, missed schedules, and Job behavior for the installed version `[VERIFY]`.
- OpenTelemetry official documentation if run IDs/traces are correlated: propagation and SDK/exporter versions `[VERIFY]`.
- Orchestrator and streaming platform official docs for their schedule, watermark, checkpoint, and consumer-lag semantics `[VERIFY]`.

No live documentation lookup or environment inspection is claimed in this lesson. Verify exact URLs and version-matched behavior before deployment rather than relying on a remembered URL or metric name.

### 15.3 Missing metric vs missing job vs exporter failure

| Evidence | Likely interpretation | Next discriminating check |
|---|---|---|
| `up == 0` for exporter | Scrape target unavailable | Exporter process/network/configuration |
| `up == 1`, expected series absent | Exporter is scrapeable but metric may be missing | Registry content, labels, stale-series behavior |
| Expected run absent and scheduler heartbeat stale | Scheduler/control-plane issue is plausible | Scheduler logs and independent health |
| Scheduler healthy, no expected run event | Calendar/registration or orchestration issue is plausible | Schedule registry and orchestrator event log |
| Run succeeded but last valid success unchanged | Validation/commit/registry update may have failed | Manifest, validation, registry write result |
| Recent commit, stale watermark | Input event time may be stale or watermark semantics wrong | Source progress and watermark producer |
| Valid commit and watermark, consumer stale | Delivery/consumer issue is plausible | Consumer lag/acknowledgment |

A healthy exporter proves only that a scrape succeeded. It does not prove a job ran. A recent job timestamp does not prove the data is fresh. A fresh commit does not prove the event-time watermark or downstream consumer is current.

### 15.4 Security controls

- Authenticate registry writers and authorize stable job identity to allowed dataset mappings.
- Protect Pushgateway write/delete endpoints; isolate lab instances and restrict network exposure.
- Restrict textfile directory write permissions and reject untrusted metric content.
- Never log credentials, tokens, raw records, customer identifiers, or secret payloads.
- Keep run IDs in logs/traces rather than metric labels.
- Validate timestamps, monotonicity, status, coverage, and schema before accepting a success update.
- Audit registry changes and cleanup/decommission operations.
- Separate exporter availability alerts from pipeline freshness alerts.

---

## 16. Practice questions and answer key

Exactly five end-of-unit questions follow. Lab and workbook questions elsewhere are separate exercises.

### Questions

1. **Exit code versus data health:** Explain why `exit 0` and a recent run timestamp do not prove fresh, valid data. Name at least four independent signals you would inspect.
2. **Green alert despite empty/partial output:** Diagnose a freshness alert that stayed green after a job produced zero rows or only some expected partitions. Describe the metric-contract defect and the test that would prevent recurrence.
3. **Pushgateway versus textfile collector:** Compare their stale-state, availability, and operational failure modes. Choose one for a local single-host batch job and justify the choice, including a condition under which you would choose the other.
4. **Watermark, deadline, and DAG slack:** A dataset has recent commit time but stale event-time watermark; the DAG estimator reports negative slack. Explain what each signal means, what it does not prove, and the next evidence to collect.
5. **Silent-failure canary:** Design a synthetic known-answer canary for an end-to-end pipeline and define its metrics, alert context, runbook response, privacy protections, and tests for missing, late, duplicated, incorrectly transformed, and not-consumed cases.

### Answer key

1. `exit 0` is process-reported completion only. A recent run timestamp may reflect a start or any completed attempt, not a valid commit. Inspect last valid committed success, event-time watermark age, validation status, partition coverage, source/expected counts, duplicate detection, and downstream consumer acknowledgment. The exact set depends on the dataset contract.
2. The likely defect is success timestamp advancement on process start/exit rather than after validation and durable commit, and/or the absence of coverage validation. Inspect the committed manifest, row count, coverage ratio, validation events, and watermark. Add tests that empty/partial outputs do not advance last-success and that the alert fires for the dataset's contract.
3. Pushgateway can retain groups and is a separate network service; cleanup, grouping keys, and write access must be managed. Textfile collector is local and simple but has file permission, stale file, exporter, and atomic-write concerns. For a local host job, textfile can be suitable if the exporter is already present and atomic replacement is implemented; Pushgateway may fit a service-level job that needs a network push path. Neither is universally best; use durable metadata as the truth and verify official guidance.
4. Recent commit age means the output was committed recently according to the registry; stale watermark means the event-time progress claim is old; negative DAG slack means the deterministic estimated finish is after the deadline. None alone proves why. Inspect source freshness, watermark semantics, stage durations, queue/pool wait, expected deadline/calendar, and historical run distributions. The DAG model omits uncertainty and contention, so compare with actual telemetry.
5. Use a synthetic unique key and deterministic expected transformation, then verify source presence, transform output, committed manifest/partition, and consumer acknowledgment. Expose bounded metrics for canary failures and coverage, keep the key in logs/traces rather than metric labels, and include owner/dataset/deadline/last-success/runbook in alerts. Test missing, late, duplicate, wrong-value, and committed-but-not-consumed cases. Never include customer data or secrets; quarantine failed output and rerun only after idempotency is verified.

---

## 17. Completion checklist and ten-pass audit

### 17.1 Learner completion checklist

- [ ] Explain process exit, validation, durable commit, freshness, event-time watermark, coverage, correctness, and consumption as distinct states.
- [ ] Define each dataset's schedule/calendar, owner, consumers, deadline, grace, freshness threshold, coverage, validation, and runbook.
- [ ] Implement bounded batch metrics and update last-success only after validation and commit.
- [ ] Compare Pushgateway, textfile collector, registry/exporter, scrape-window, event/log, and trace patterns.
- [ ] Test freshness, deadline, missed-run, failure, hang, missing metric, stale watermark, coverage, duplicate, and streaming signals.
- [ ] Build dashboard panels with explicit units, source, aggregation, time range, and interpretation traps.
- [ ] Run the DAG script/tests and explain deterministic critical path and slack limitations.
- [ ] Run the stream simulator and distinguish replay backlog from unhealthy lag.
- [ ] Test registry monotonicity, idempotency, authorization mapping, and stale update rejection.
- [ ] Test canary correctness and consumer acknowledgment.
- [ ] Complete all six chaos classes or mark them not run, with no invented timing values.
- [ ] Validate one runbook against an injected fault and retain evidence.
- [ ] Confirm cleanup of all local resources and no host clock changes.

### 17.2 Acceptance criteria for Labs A–J

| Lab | Testable acceptance criteria |
|---|---|
| A — Batch metrics | Both transport patterns documented/tested where available; last-success only advances after validation+commit; all seven fault modes have expected signals; safe cleanup demonstrated |
| B — Kubernetes | Missed/late, failed, long-running, suspended, and overlap states tested in kind or fixture fallback; metric names verified |
| C — Dashboard | Required freshness, watermark, deadline, duration, coverage, validation, scheduler, DAG, streaming, lineage, and alert panels specified; no-data distinct from zero |
| D — DAG script | Critical path/slack output; tests for valid parallel graph, boundary/negative slack, cycle, missing dependency, invalid duration, duplicate edge, timezone-aware input |
| E — Streaming | Lag, watermark, checkpoint, input/processing rate, DLQ measured; burst/replay tested; replay suppression expires |
| F — Registry | Success/invalid/stale/duplicate/read/export/spoofing cases tested; registry down distinct from dataset stale |
| G — Time-slice SLI | Good/bad/unknown slices and M10 burn-rate reuse tested; planned suppression is scoped and expires |
| H — Canary | Missing/late/duplicate/wrong-transform/not-consumed cases tested; failed canary prevents healthy status |
| I — Chaos matrix | Six failure classes have injection, signal, detection definition, actual or explicitly unmeasured time-to-detect, recovery, cleanup, prevention |
| J — Runbook | One injected fault diagnosed; dry-run/idempotency and stop conditions documented; evidence and follow-up retained |

### 17.3 Evidence-retention checklist

Retain only sanitized, relevant evidence:

- catalog/SLO contract version and tested schedule/timezone policy;
- metric contract, discovered names/labels, and version notes;
- fixture input/output, commit manifest, validation/canary result;
- PromQL expressions and rule files;
- `promtool` version/check/test output when actually executed;
- dashboard export or panel specification;
- DAG fixture, script, and unit-test output;
- stream simulator output and replay expiry tests;
- registry schema, test output, and authorization mapping;
- chaos matrix with actual measured time-to-detect or “not run”;
- runbook validation record, cleanup confirmation, and follow-up actions.

Never retain raw sensitive payloads, credentials, or unbounded record identifiers in metric labels.

### 17.4 Ten-pass audit

1. **Roadmap fidelity — PASS (content check):** exact target filename and Unit 11 placement are stated; the verbatim M10 handoff is included. The authoritative roadmap/syllabus source files were not independently inspected in this authoring context, so source alignment beyond the supplied prompt remains `[VERIFY]`.
2. **Failure coverage — PASS (content check):** scheduled failure modes and all eight required incident patterns are included.
3. **Metric correctness — PASS (content check):** run time, event time, valid commit, bounded labels, and missing-data behavior are separated; success is updated only after validation and commit in the local example.
4. **Monitoring patterns — PASS (content check):** Pushgateway, textfile collector, long-running registry/exporter, short-lived scrape caveat, event/log, and tracing are compared.
5. **Kubernetes/orchestrator coverage — PASS WITH `[VERIFY]`:** CronJob/Job, heartbeat, missed/late/failed/hung/suspended/overlap cases are covered; metric names and version semantics require installed-version validation.
6. **SLO/alert correctness — PASS WITH `[VERIFY]`:** time-slice SLI, bad-minute concept, burn-rate reuse, deadlines, grace, backfills, and test plans are included; actual PromQL/`promtool` behavior must be verified in the installed version.
7. **Script integrity — CONTENT REVIEW COMPLETE; EXECUTION NOT CLAIMED:** DAG algorithm, assumptions, and edge-case tests are specified. Run the commands locally before treating the script as validated in your environment.
8. **Silent-failure and streaming coverage — PASS (content check):** canary correctness, reconciliation, watermark, lag, checkpoint, processing/input rate, DLQ, burst/replay, and suppression expiry are covered.
9. **Lab safety and assessment — PASS (content check):** Labs A–J include bounded local procedures, cleanup, troubleshooting, and acceptance criteria; exactly five end-of-unit questions and answers are present.
10. **Single-file and evidence integrity — PASS (authoring intent):** this lesson is a single-file deliverable; synthetic examples and illustrative values are labelled. Live integration tests, current official documentation checks, and repository-diff verification were not performed; do not infer they passed.

**Known limitations:** no live Prometheus, Pushgateway, node-exporter, Kubernetes/kind, orchestrator, streaming platform, or registry HTTP integration was run as part of authoring. Metric names, APIs, PromQL functions, Kubernetes fields, and exporter behavior remain `[VERIFY]` where version-dependent. All example timings, schedules, and thresholds are synthetic/illustrative. Execute the included scripts/tests and verify official documentation against installed versions before adapting any pattern to a production system.
