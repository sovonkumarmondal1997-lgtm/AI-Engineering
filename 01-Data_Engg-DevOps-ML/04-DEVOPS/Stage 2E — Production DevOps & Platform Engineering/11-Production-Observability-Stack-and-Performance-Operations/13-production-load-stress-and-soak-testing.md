# Unit 13 — Production Load, Stress, and Soak Testing

**Target file:** `13-production-load-stress-and-soak-testing.md`  
**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Module:** M11 — Production Observability Stack and Performance Operations  
**Unit:** 13 — Production load, stress, and soak testing

> **Safety contract:** The required experiments target only the learner's own local lab service or deterministic fixtures. Do not point these examples at production, public, shared, or third-party systems. Every run is bounded, has a predeclared abort path, and uses synthetic data. Laptop measurements are educational observations—not production capacity guarantees.

**Evidence labels used throughout**

- `[SYNTHETIC]` — generated fixture data, not a real incident or measurement.
- `[ILLUSTRATIVE]` — example values used to explain a calculation; replace them with measurements.
- `[ASSUMPTION]` — a design choice that must be confirmed for the learner's environment.
- `[VERIFY]` — version- or environment-sensitive syntax/behavior that must be checked against installed tools and official documentation.

---

## 0. Unit orientation and learning contract

### What this unit teaches

A performance test is a controlled experiment, not a request generator. It asks a falsifiable question about a defined system, workload, time window, and success criterion. The answer must include workload validity, client-side observations, service telemetry, uncertainty, and limitations.

This unit builds on M11 Units 1–12:

- Units 1–8 supply the metrics, logs, traces, alerting, correlation, and incident-response foundations.
- Unit 9 supplies saturation, queue-depth, and resource-exhaustion reasoning.
- Unit 10 supplies trace critical-path and bottleneck isolation.
- Unit 11 supplies scheduled-job freshness and deadline monitoring.
- Unit 12 supplies telemetry cardinality, retention, and cost controls.
- M10's SLO and error-budget work supplies the business/service objectives used to set thresholds; this unit does not re-derive the entire SLO module.

Forward boundaries: release-health comparison belongs with M08 Unit 9; capacity and reliability governance belong with M10; disaster-recovery/failover planning belongs with M13/M14. This unit introduces only the performance-testing evidence those modules consume.

### Measurable outcomes

By completion, the learner can:

1. Select the correct experiment type and workload model for a stated question.
2. Explain offered arrival rate, achieved throughput, goodput, concurrency, queue wait, service time, and client-observed response time.
3. Run a bounded, allow-listed local load scenario and preserve reproducible run metadata.
4. Correlate load-generator health with service RED metrics, saturation, dependency telemetry, and traces.
5. Identify a measured capacity knee and distinguish a service bottleneck from a generator bottleneck.
6. Compare candidate and baseline distributions using raw samples, effect sizes, and uncertainty.
7. Use A/A tests to estimate noise and validate a CI gate against both a planted regression and no-change fixtures.
8. Estimate a resource-growth slope during a bounded soak while explaining why extrapolation is conditional.
9. Run a local resilience-under-load matrix and a backfill-versus-online isolation experiment.
10. Produce a defensible report with a clear verdict: improvement, regression, or inconclusive.

### Scope map

| Concept | Artifact/lab | Evidence required |
|---|---|---|
| Open-loop workload | Lab 1 | Offered schedule, actual starts, completions, generator health |
| Coordinated omission | Lab 2 | Closed-loop/open-loop latency and missed-arrival comparison |
| Knee and capacity envelope | Lab 3 | Step table and latency/goodput/saturation plot data |
| Stress, spike, autoscaler lag | Lab 4 | Abort log, recovery time, SLO impact |
| Leak vs warm-up | Lab 5 | Time-series samples, slope interval, cleanup verification |
| Resilience | Lab 6 | Expected-versus-observed matrix |
| Workload isolation | Lab 7 | Online and batch before/after distributions |
| Statistics/A-A | Lab 8 | Raw samples, effect size, bootstrap interval, A/A false-positive check |
| CI smoke gate | Lab 9 | Planted-regression detection and A/A result |
| Reporting | Lab 10 | Reproducible report and limitations |
| Observability capacity | Lab 11 | Backend resource/volume trend or fixture fallback |
| Safety | Lab 12 | Safety validator rejects unsafe target/config |

### Suggested sequence

Complete Sections 0–2 first, then Labs 1–3, followed by Labs 8–9 before using the gate for any automated decision. Run Labs 4–7 only after the safety checklist is familiar. Labs 10–12 consolidate reporting, observability overhead, and safety.

### What a laptop experiment can and cannot prove

A laptop can demonstrate local mechanisms, relative behavior, instrumentation correctness, and whether a repeatable regression is detectable in a controlled setup. It cannot establish production capacity, multi-node high availability, cloud/network behavior, realistic production traffic distribution, shared-hardware effects, managed-backend limits, or multi-day reliability. WSL2 and the host may share CPU, memory, disk, and network resources; generator and service compete for those resources.

**Readiness check:** Can you name the exact local target, state the maximum offered rate and duration, identify the abort switch, and explain what would count as a valid run? If not, do not start a load test.

---

## 1. Why performance testing is an SRE discipline

Functional tests establish that selected inputs produce expected outputs under their test conditions. They do not establish that the service remains useful at expected peak load, fails gracefully beyond capacity, recovers after overload, avoids resource leaks, or preserves its SLO during dependency trouble.

Performance testing supports:

- **Capacity verification:** characterize the envelope where latency, error rate, and goodput remain acceptable.
- **Knee discovery:** identify where additional offered load stops producing useful throughput and starts creating queueing or failures.
- **Bottleneck isolation:** use traces and metrics to find the first limiting resource rather than treating correlated symptoms as causes.
- **Degradation detection:** find memory, connection, file-descriptor, disk, and queue growth over time.
- **Timeout/retry validation:** ensure retries do not amplify overload and that recovery is possible.
- **Release risk reduction:** compare baseline and candidate under comparable workload and environment.
- **SLO protection:** translate service objectives into measurable test acceptance criteria.

A test with a fast average but unacceptable p99 is not a pass. A server that returns errors quickly may have high raw throughput but low goodput. A generator that cannot sustain its intended arrival rate cannot support a claim about the service at that rate.

### Experiment contract

Before running a test, write:

- **Question:** What decision will the result support?
- **Hypothesis:** What should happen at a specified workload?
- **Independent variables:** arrival rate, concurrency, payload mix, cache state, replicas, fault.
- **Controlled variables:** build, data, environment, telemetry profile, warm-up, test window.
- **Measurements:** raw request latency, status, offered/achieved rate, goodput, generator resources, service saturation, dependency signals.
- **Acceptance rule:** derived from the learner's SLO/baseline and stated before seeing the result.
- **Abort rule:** predeclared safety boundary and command/action.
- **Reproducibility bundle:** run ID, versions, configuration, raw samples, plots, conclusion.

---

## 2. L1 — Test types, workload models, and metrics

### 2.1 Test types: different questions require different experiments

| Type | Purpose and setup | Pass/fail question | Main risk |
|---|---|---|---|
| Load | Expected or forecast peak, representative mix | Does the service meet objectives at this load? | Unrealistic workload gives false confidence |
| Stress | Step beyond expected capacity with an abort boundary | Does it degrade predictably and recover? | Resource exhaustion or collateral damage |
| Spike | Sudden increase/decrease in arrivals | Can the service absorb the transient and recover? | Queue/retry amplification |
| Soak/endurance | Sustained bounded workload for 2–4 hours, or explicitly accelerated simulation | Do resources, errors, or latency drift over time? | Long unattended run, disk/resource exhaustion |
| Capacity/knee | Stepwise increase in offered load | Where does marginal useful throughput deteriorate? | Generator or telemetry bottleneck mistaken for SUT |
| Breakpoint | Find a pre-defined failure boundary under controlled increments | At what condition does a specified criterion fail? | Treating a lab breakpoint as universal capacity |
| Scalability | Compare service behavior as CPU/memory/replicas change | Does added resource improve useful throughput? | Shared bottleneck dominates |
| Volume | Increase dataset/payload size while controlling request rate | Does data size change latency or resource needs? | Confounding volume with rate |
| Failover/chaos-under-load | Inject one approved fault while bounded load runs | Does behavior match recovery/degradation policy? | Fault scope exceeds the lab |

These experiments are not interchangeable. A brief spike does not reveal a slow leak; a soak does not necessarily locate the capacity knee; a load test below the knee does not show graceful overload behavior.

### 2.2 Workload models: open-loop and closed-loop

**Open-loop:** the arrival schedule is independent of response time. If the target slows, the generator still attempts arrivals at the intended rate. This is useful when modeling external arrivals that continue during a service stall.

**Closed-loop:** a fixed number of workers issue another request after the previous one completes. This is useful for bounded clients/workers, but as latency increases, the request-start rate naturally falls. It may under-represent pressure from arrivals that continue regardless of service latency.

Other workload dimensions matter: think time, request mix, burstiness, payload size, auth overhead, hot keys/skew, cache state, data distribution, error mix, and online traffic competing with backfills.

#### Coordinated omission

A closed-loop generator can omit arrivals that would have happened during a long stall. For example, if one worker sends a request every time the previous request finishes, a 2-second response delays the next scheduled request by 2 seconds. A constant-arrival external workload may instead have attempted several requests during that interval. The observed closed-loop samples can therefore under-represent the latency experience of arrivals during the stall.

`[ILLUSTRATIVE]` Suppose a target normally responds in 50 ms but stalls for 1 second. With 10 closed-loop workers, each stalled worker simply waits; its next request starts later. Under an open-loop schedule of 100 arrivals/s, roughly 100 arrivals are due during one second. The actual number started depends on generator capacity, queuing policy, dropped iterations, and scheduling semantics. Do not assume every tool corrects coordinated omission automatically. Check the chosen tool's current documentation and report intended arrivals, actual starts, late/dropped arrivals, completions, and response-time definition.

### 2.3 Performance metrics and distributions

| Metric | Meaning | Unit / caution |
|---|---|---|
| Offered arrival rate | Intended arrivals to the SUT | requests/s; record the schedule |
| Achieved start rate | Requests actually started | requests/s; can be below offered rate |
| Throughput | Completed requests/work | requests/s or operations/s |
| Goodput | Successful, useful work completed | successful operations/s; validate response correctness |
| Error rate | Failed/invalid requests divided by attempts | percentage plus error classes |
| Latency/response time | Client-observed time from request start to completion | ms or s; includes client/network effects |
| Service time | Time spent processing, as defined by instrumentation | ms or s; definition must be explicit |
| Queue wait | Time waiting before service begins | ms or s |
| p50/p90/p95/p99/p99.9/max | Distribution summaries | require sample count and window |
| Concurrency | Simultaneous in-flight work | requests, workers, or connections; specify which |
| Saturation | Resource pressure/queued work relative to capacity | CPU, memory, throttling, pool waits, queue depth |
| Generator health | CPU, memory, network, event loop/worker utilization | measured separately from SUT |

Averages hide tails. Do not average p95 values across runs and call the result a combined p95: quantiles are not additive, and the result depends on each run's sample count and distribution. Prefer raw per-request observations or mergeable histograms with known semantics. Preserve the sample count, time window, and request mix.

**Goodput example:** `[SYNTHETIC]` 800 requests complete in 10 seconds, but 120 are errors and 30 return semantically invalid output. If these categories are disjoint, useful successes are \(800-120-30=650\), so goodput is 65 useful requests/s. State how invalid responses are counted to avoid double counting.

#### Little's Law

\[
L = \lambda W
\]

Where \(L\) is average work in the system (requests), \(\lambda\) is stable throughput (requests/s), and \(W\) is average time in the system (s). `[ILLUSTRATIVE]` At 40 requests/s and 0.25 s average time, \(L=40\times0.25=10\) average in-flight requests. This is a consistency check for a stable system, not a guarantee for overloaded or rapidly changing workloads.

### 2.4 Load-generator choice: k6 primary, Locust awareness

This lesson uses **k6** as the primary example because it has a JavaScript test format and supports arrival-rate executor concepts in versions that provide them. Exact installation steps, executor names/options, output integrations, thresholds, and metric behavior are `[VERIFY]`: confirm them against the installed k6 version and its official documentation before running. Locust is an alternative with Python user scenarios and worker-based load generation; exact behavior and open-loop suitability depend on version/configuration and must be checked.

Do not install multiple heavy tools just to complete the unit. If k6 is unavailable, use the deterministic Python fixture/analysis exercises; do not silently substitute a closed-loop script and call it open-loop.

### 2.5 Derive thresholds from objectives

Do not copy universal p95/p99 limits. Derive test thresholds from the learner's service SLO, product expectations, baseline, and error budget. Write the rule before the test.

**Hypothesis template**

> `[ASSUMPTION]` At an offered rate of `<TARGET_RPS>` using request mix `<MIX_VERSION>`, dataset `<DATA_VERSION>`, and build `<BUILD_ID>`, the service will maintain p95 and p99 within `<SLO_DERIVED_LIMITS>`, error rate below `<ERROR_BUDGET_LIMIT>`, and useful goodput at or above `<MIN_GOODPUT>` for `<DURATION>`, without crossing `<ABORT_THRESHOLDS>`.

Record why each limit is appropriate and how a run will be marked invalid (e.g., generator saturation, missing samples, telemetry loss, wrong build, unexpected target).

---

## 3. L2 — Design a realistic load test for the local inference API

### 3.1 Define and protect the system under test

Use only the learner's local lab service. Do not accept arbitrary remote URLs. The following k6 example hard-codes the permitted local host and rejects any other host. `[VERIFY]` the selected k6 version's environment-variable and scenario syntax before use.

The endpoint path and response schema are assumptions; adapt them to the actual local service without changing the local-host guard.

```javascript
// File: loadtest/local_inference.js
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';
const ALLOWED_HOSTS = new Set(['127.0.0.1:8000', 'localhost:8000']);

function validateTarget(url) {
  let parsed;
  try {
    parsed = new URL(url);
  } catch (_) {
    throw new Error('BASE_URL is not a valid URL');
  }
  if (parsed.protocol !== 'http:' || !ALLOWED_HOSTS.has(parsed.host)) {
    throw new Error('Refusing non-local or non-allow-listed target: ' + parsed.host);
  }
  return url.replace(/\/+$/, '');
}

const base = validateTarget(BASE_URL);
const runId = (__ENV.RUN_ID || 'local-manual').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 48);
const durationSeconds = Number(__ENV.DURATION_SECONDS || 60);
const targetRate = Number(__ENV.TARGET_RPS || 5);

if (!Number.isInteger(durationSeconds) || durationSeconds < 1 || durationSeconds > 300) {
  throw new Error('DURATION_SECONDS must be an integer from 1 to 300');
}
if (!Number.isInteger(targetRate) || targetRate < 1 || targetRate > 20) {
  throw new Error('TARGET_RPS must be an integer from 1 to 20 for this lab');
}

export const options = {
  scenarios: {
    bounded_local_arrivals: {
      // [VERIFY] Confirm this executor and its options for the installed k6 version.
      executor: 'constant-arrival-rate',
      rate: targetRate,
      timeUnit: '1s',
      duration: `${durationSeconds}s`,
      preAllocatedVUs: Math.max(2, targetRate),
      maxVUs: Math.max(5, targetRate * 2),
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.02'], // [ILLUSTRATIVE] replace with an SLO-derived threshold
    http_req_duration: ['p(95)<500'], // [ILLUSTRATIVE] replace with local SLO-derived value
  },
  tags: { test_run: runId },
};

export default function () {
  const payload = JSON.stringify({
    request_id: `${runId}-${__VU}-${__ITER}`,
    features: [0.1, 0.2, 0.3],
    mode: 'synthetic',
  });
  const response = http.post(`${base}/predict`, payload, {
    headers: { 'Content-Type': 'application/json', 'X-Test-Run': runId },
    tags: { request_type: 'predict', test_run: runId },
    timeout: '3s',
  });
  check(response, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
    'body is JSON': (r) => {
      try { JSON.parse(r.body); return true; } catch (_) { return false; }
    },
  });
}
```

**Important:** This is a bounded local harness example, not a verified drop-in for every k6 release. Confirm syntax with `k6 version` and the official scenario/executor documentation. Never raise the maximum rate/duration until a lower-rate run is valid and the safety preflight passes.

### 3.2 Workload design

Define these before the test:

- **Request mix:** for example, inference 70%, feature lookup 20%, health check 10% `[ILLUSTRATIVE]`; health checks may be excluded from business goodput.
- **Payload classes:** small/medium/large synthetic payloads with explicit byte sizes.
- **Arrival pattern:** steady, burst, ramp, or scheduled mix.
- **Warm-up:** state how long is excluded and why; retain it separately for diagnosis.
- **Cache:** label cold-start and warmed-cache runs separately.
- **Data skew:** include a hot-key scenario only if relevant to the actual service.
- **Concurrent batch work:** explicitly decide whether a synthetic backfill is present.
- **Validation:** status, response schema, and a deterministic correctness assertion.
- **Isolation:** use a dedicated test namespace/prefix and synthetic records; cleanup only that namespace.

### 3.3 Run metadata and reproducibility

Record at least:

```text
run_id, timestamp_start, timestamp_end, git_sha, service_build,
test_data_version, OS/WSL2 version, CPU/memory/disk budget,
tool and version, generator settings, SUT replicas/resources,
request mix, target rate, achieved starts, completions, errors,
warm-up exclusion, telemetry profile, raw-results path, verdict,
abort reason (if any), cleanup confirmation
```

Do not record secrets or environment variables wholesale. Store only a reviewed allow-list of non-secret configuration values.

### 3.4 Observability during the test

Dashboard rows should include:

1. Generator: offered/started/completed rate, dropped or late arrivals if available, CPU, memory, network, event-loop/worker saturation.
2. SUT RED: request rate, errors, latency distribution, semantically valid goodput.
3. Saturation: CPU, memory/RSS, throttling, queue depth, worker/pool wait.
4. Dependencies: database/feature fetch/model stage latency, retries, timeouts.
5. Traces: only when Full profile is required; link slow/error traces and compare spans.
6. Observability pipeline: dropped/buffered telemetry, Collector resource use, backend query/ingestion pressure.

Grafana annotation APIs and exact integration syntax are `[VERIFY]`. Safe fallback: write UTC phase markers to a local CSV with `run_id`, `phase`, `timestamp_utc`, and `note`; compare them with metric time ranges. Do not add high-cardinality run IDs to permanent metric labels unless the local telemetry design explicitly handles that dimension.

### 3.5 Find the knee and first bottleneck

Run bounded steps, e.g. 2, 4, 6, 8 requests/s for 60 seconds each `[ILLUSTRATIVE]`; use lower values if the laptop is constrained. At each step record:

| Offered RPS | Actual starts/s | Goodput/s | p50 | p95 | p99 | Error % | Queue | CPU/throttling | Generator CPU | Valid? |
|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| [TO MEASURE] | | | | | | | | | | |
| [TO MEASURE] | | | | | | | | | | |

Define a knee rule before testing, such as “the first step where goodput gain becomes materially smaller than offered-load gain while p95/queue/error worsens beyond the predeclared bound.” This is an operational rule, not a universal mathematical knee.

The **first bottleneck** is the earliest limiting component supported by evidence. CPU may rise after a queue has already grown due to a slow database; a slow trace span may be a symptom of connection-pool wait, not database execution. Compare generator health, service metrics, dependency signals, and traces before attributing cause.

---

## 4. L3 — Analyze results and diagnose failure modes

### 4.1 Statistical discipline

Repeat each important run, exclude warm-up according to a predeclared rule, and keep environment/build/workload comparable. Interleave A and B runs where practical (A-B-B-A or randomized order) to reduce time-of-day and thermal confounding. Report raw per-request samples or an explicitly justified summary. Do not bootstrap only p95/p99 summaries and pretend the original distribution has been reconstructed.

A confidence interval describes uncertainty under the method's assumptions; it does not prove causality. Bootstrap resampling assumes the observations are suitable for resampling. Strong autocorrelation from time-series traffic can make naïve independent resampling overconfident. For highly time-correlated samples, consider block resampling or summarize independent run-level results; document the choice.

#### Standard-library comparison script

This script compares raw latency samples in milliseconds. It uses a percentile bootstrap for the difference in medians and reports a median ratio as an effect-size aid. It is intentionally small; it does not model time autocorrelation and should not be treated as a production-grade statistical package.

```python
# File: scripts/compare_latency.py
import argparse
import json
import random
import statistics
import sys
from pathlib import Path

def percentile(values, p):
    if not values:
        raise ValueError("percentile requires at least one value")
    xs = sorted(values)
    pos = (len(xs) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac

def load_samples(path):
    try:
        obj = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(obj, list) or not obj:
        raise ValueError(f"{path} must contain a non-empty JSON list of latency_ms values")
    values = []
    for i, value in enumerate(obj):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{path}[{i}] is not numeric")
        if value < 0:
            raise ValueError(f"{path}[{i}] is negative")
        values.append(float(value))
    return values

def bootstrap_median_difference(a, b, reps=2000, seed=7):
    if len(a) < 2 or len(b) < 2:
        raise ValueError("at least two samples per group are required")
    rng = random.Random(seed)
    diffs = []
    for _ in range(reps):
        sa = [a[rng.randrange(len(a))] for _ in a]
        sb = [b[rng.randrange(len(b))] for _ in b]
        diffs.append(statistics.median(sb) - statistics.median(sa))
    return percentile(diffs, 0.025), percentile(diffs, 0.975)

def summarize(xs):
    return {
        "n": len(xs),
        "p50_ms": round(percentile(xs, 0.50), 3),
        "p95_ms": round(percentile(xs, 0.95), 3),
        "p99_ms": round(percentile(xs, 0.99), 3),
        "mean_ms": round(statistics.fmean(xs), 3),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline_json")
    parser.add_argument("candidate_json")
    parser.add_argument("--bootstrap-reps", type=int, default=2000)
    args = parser.parse_args()
    if args.bootstrap_reps < 100:
        parser.error("--bootstrap-reps must be >= 100")
    try:
        a = load_samples(args.baseline_json)
        b = load_samples(args.candidate_json)
        lo, hi = bootstrap_median_difference(a, b, args.bootstrap_reps)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    report = {
        "baseline": summarize(a),
        "candidate": summarize(b),
        "median_difference_candidate_minus_baseline_ms": round(statistics.median(b) - statistics.median(a), 3),
        "bootstrap_95pct_interval_difference_ms": [round(lo, 3), round(hi, 3)],
        "median_ratio_candidate_over_baseline": round(statistics.median(b) / max(statistics.median(a), 1e-12), 4),
        "method_note": "Raw samples; percentile bootstrap of medians; independent-resampling assumption; not causal proof."
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# File: tests/test_compare_latency.py
import json
import tempfile
import unittest
from pathlib import Path
from scripts.compare_latency import load_samples, percentile, bootstrap_median_difference

class CompareLatencyTests(unittest.TestCase):
    def test_percentile_boundary(self):
        self.assertEqual(percentile([1, 2, 3], 0), 1)
        self.assertEqual(percentile([1, 2, 3], 1), 3)

    def test_load_and_reject_empty(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "samples.json"
            p.write_text(json.dumps([10, 12, 14]))
            self.assertEqual(load_samples(p), [10.0, 12.0, 14.0])
            p.write_text("[]")
            with self.assertRaises(ValueError):
                load_samples(p)

    def test_candidate_slower_positive_difference(self):
        lo, hi = bootstrap_median_difference([10, 11, 12, 13], [20, 21, 22, 23], reps=200, seed=1)
        self.assertGreater(lo, 0)
        self.assertGreater(hi, 0)

if __name__ == "__main__":
    unittest.main()
```

Save fixtures as JSON arrays of raw latency milliseconds, for example `[SYNTHETIC]` baseline `[20,21,19,22,20,23,18,21]` and candidate `[28,29,27,31,28,30,26,29]`. Run with `python -m unittest tests.test_compare_latency` from the illustrative lesson workspace `[VERIFY]`. The script intentionally emits a numeric interval rather than automatically declaring a regression: the learner must define practical tolerance, error/goodput requirements, sample-size adequacy, and A/A behavior before setting a verdict.

### 4.2 Baseline versus candidate

Compare, at minimum:

- Raw latency samples and p50/p95/p99 with sample count.
- Error rate and error classes.
- Goodput and achieved arrival rate.
- CPU-seconds per successful request, with a documented measurement method.
- Memory/resource slope, connection counts, file descriptors, queue depth.
- Dependency latency, pool waits, throttling, retries.
- Generator CPU/memory/network and late/dropped arrivals.
- SLO impact and recovery behavior.

Use verdicts such as:

- **Improvement:** candidate passes all guardrails and shows an effect beyond the predeclared practical threshold with acceptable uncertainty.
- **Regression:** candidate violates a predeclared guardrail or shows a material adverse change with adequate evidence.
- **Inconclusive:** run validity, sample size, noise, confidence interval, or workload comparability is insufficient.

### 4.3 A/A testing and false positives

A/A compares the same build/configuration under nominally equivalent conditions. Run the gate repeatedly on equivalent candidates to estimate how often noise triggers a regression. If A/A frequently fails, improve environment control, sample size, interleaving, or decision logic before relying on the gate. An A/A test is not proof that every future false positive is impossible.

A deterministic fixture can test the decision logic, but it cannot estimate real runner noise. For an empirical false-positive rate, run multiple actual A/A pairs under the intended runner and retain every result.

### 4.4 Capacity and scalability

The capacity envelope is the range of offered load where the system satisfies the predeclared latency, error, goodput, and saturation requirements. Keep headroom below the measured knee; do not use the exact knee as an operating target. Vertical scaling can hit per-process limits, while horizontal scaling can be blocked by a single database primary, global lock, hot partition, queue, cache stampede, or load-generator cap. Autoscaling has detection and startup delay, so a spike can rise faster than new capacity arrives.

Never convert laptop RPS to production commitments. Production inference requires representative hardware, data, network, dependency limits, deployment topology, and approved production validation.

### 4.5 Leak versus warm-up and normal drift

A rising memory line is not proof of a leak. Possible explanations include:

- Cache warm-up that plateaus.
- Allocator retaining freed memory for reuse.
- Fragmentation or GC/runtime behavior.
- Bounded buffers filling to a stable limit.
- Workload mix changing over time.
- Actual unbounded growth from a leak.
- Increasing connections, file descriptors, queue depth, logs, or disk use.

Collect memory/RSS, heap if available, connections, descriptors, queue depth, disk/log growth, request mix, and restart events. A leak hypothesis becomes stronger when resource growth persists after warm-up under stable workload, is repeatable, and correlates with retained objects or unreleased resources. Use a controlled planted leak only in a disposable local branch.

### 4.6 Soak slope and time-to-limit

For samples \((t_i, r_i)\), estimate a simple linear slope using least squares:

\[
\hat{\beta} = \frac{\sum_i (t_i-\bar t)(r_i-\bar r)}{\sum_i (t_i-\bar t)^2}
\]

Use hours for \(t\) and MiB for \(r\) to report MiB/hour. A projected time to a chosen limit \(R_{\max}\) is \((R_{\max}-R_{\text{current}})/\hat{\beta}\) only when the slope is positive and the linear-growth assumption is plausible. This projection can be invalid if growth is nonlinear, cache warming plateaus, GC cycles intervene, workload changes, or the measurement window is too short.

A short synthetic soak is not proof that a multi-day leak is absent. Report the observation window and uncertainty; if you cannot estimate a defensible interval, say so rather than fabricate one.

### 4.7 Regression triage workflow

1. Verify the test was valid: correct target/build, actual arrival rate, enough samples, no abort, no telemetry gap.
2. Compare run metadata and workload definitions.
3. Inspect generator saturation before blaming the SUT.
4. Compare RED and goodput metrics.
5. Inspect saturation, queues, pools, dependencies, and traces.
6. Isolate the changed component or configuration.
7. Reproduce with one controlled variable changed.
8. Classify as regression, noise, or inconclusive using declared criteria.
9. Mitigate/rollback if required.
10. Add a regression test, preserve evidence, and document the conclusion.

---

## 5. L4 — Resilience, CI gates, and performance operations

### 5.1 Stress, overload, and spike response

Healthy overload behavior is deliberate: bounded queues, backpressure, load shedding/rejection, timeouts, retry budgets, circuit breaking, and predictable recovery. A system that retries every timeout can multiply demand precisely when a dependency is weakest.

For an optional kind/HPA exercise, measure the time between the configured signal crossing its scale threshold and usable capacity becoming available. Compare this with spike rise time and the interval of SLO violation. Kubernetes HPA behavior and metric prerequisites are `[VERIFY]`; if kind is too heavy, use a deterministic simulator that delays a fictional scale-out by a configurable number of seconds. Never install a large platform only to complete this one lab.

### 5.2 Resilience-under-load matrix

| Scenario | Hypothesis | Preconditions / abort | Evidence | Recovery / prevention |
|---|---|---|---|---|
| Dependency slowdown | Bounded timeout/backpressure protects the API | Local stub only; stop if error/latency guardrail is crossed | Dependency span, queue, timeout and retry counts | Remove delay; test timeout/retry budget |
| Replica/pod kill | Remaining local replicas serve or reject predictably | Disposable kind namespace; no shared cluster | Availability, goodput, recovery time | Restore replicas; verify readiness and PDB assumptions |
| Node drain/PDB | Disruption policy limits simultaneous loss | Only if local kind setup safely supports it `[VERIFY]` | Pod availability and rescheduling timeline | Uncordon/restore node; document cluster-specific limits |
| Cache flush | Cold cache causes bounded degradation | Local disposable cache only | Cache hit ratio, latency tail, backend load | Warm safely; test stampede protection |
| DB failover | Client recovers within declared limits | Only if existing local DB operator supports it | Connection errors, retries, recovery time | Restore local DB; no mandatory extra platform |
| Resource pressure | Limits/backpressure avoid runaway work | Throwaway local process/container only | CPU/memory/queue and abort logs | Remove fault; restart disposable service if needed |

Do not inject multiple faults at once until each single-fault result is understood.

### 5.3 Backfill versus online isolation

Run synthetic online inference and a bounded synthetic backfill together. Compare:

- Online p95/p99, errors, goodput, and SLO budget.
- Batch records/s, completion time, and resource use.
- Queue depth, CPU throttling, memory, database/pool waits.
- Results with and without a local concurrency cap, separate queue, quota, priority, or resource limit.

The objective is not to maximize batch throughput at any cost. Choose an isolation policy that keeps online objectives acceptable while making batch progress. Stop if online abort thresholds are crossed; remove the cap only after the lab is cleaned up and the baseline is restored.

### 5.4 Performance CI smoke gate

A short gate should validate:

- p95 relative to a recorded baseline plus learner-defined tolerance.
- CPU-seconds per successful request, or another clearly defined efficiency metric.
- Error rate and goodput.
- Run validity and generator health.
- A planted regression is detected.
- An A/A comparison is not rejected under the chosen noise-aware rule.

Use interleaved A/B runs and a pinned workload/build environment. Do not fail CI on one noisy percentile sample without justification. If the result is uncertain, emit `INCONCLUSIVE` and schedule a controlled rerun rather than silently passing or failing.

### 5.5 Continuous performance operations

Maintain a shared workload-model library, templates for API/batch/stream/model-serving archetypes, a versioned scenario catalog, environment policies, result retention, release comparisons, canary comparisons (M08 Unit 9 forward reference), production-derived trend reviews, and efficiency indicators such as CPU-seconds per successful request. Recalibrate capacity models as workload, data, dependencies, hardware, and software change.

### 5.6 Governance, long-haul soaks, cost, and ethics

Production load tests require authorization, approved windows, stakeholder communication, a blast-radius assessment, a kill switch, impact monitoring, and an explicit decision about error-budget consumption (M10 forward reference). Failover/DR testing belongs to M13/M14 and must not bypass approvals.

A multi-day soak is a staging/production program, not this laptop lab: schedule windows, define failure budget, monitor memory and resource trends, preserve headroom, and document recovery. Cost-versus-capacity choices must use measured resource demand and stakeholder priorities; this lesson does not provide pricing.

Respect privacy and third parties. Use synthetic payloads, no credentials/PII, and local targets only. Synthetic workloads may omit real-world skew, network behavior, cache patterns, dependencies, and customer concurrency. A local test cannot prove production scale, multi-node HA, cloud network behavior, or long-term reliability.

---

## 6. Mandatory practical labs — all twelve

### Common safety preflight for every lab

Before each run, confirm:

- [ ] Authorization: only your own local lab/fixtures.
- [ ] Target identity: `127.0.0.1`/`localhost` and explicit allow-list.
- [ ] Maximum rate, concurrency, duration, payload size, and data volume are bounded.
- [ ] Synthetic test data and dedicated test prefix are used.
- [ ] Current CPU, memory, and disk headroom have been measured.
- [ ] Generator and service health are visible.
- [ ] Abort command/switch is ready and tested.
- [ ] Fault injection has a named cleanup step.
- [ ] Recovery and baseline verification are defined.
- [ ] No unexpected external traffic is observed.

If host pressure, disk use, errors, SLO impact, or unexpected traffic crosses the learner's predeclared threshold, stop the generator and remove the injected fault. Do not wait for a test to finish.

### Lab 1 — Open-loop load-test harness

**Objective:** Run a bounded, allow-listed local workload and capture workload validity.

**Profile:** Core. Measure actual resource footprint; avoid running full traces unless required.

**Prerequisites:** Local API, Python/k6 as selected, health check, dashboard or CSV evidence path.

**Steps:**

1. Confirm the API is listening on the expected local port. Verify the build and test namespace.
2. Read Section 3's k6 script; verify syntax and executor support for the installed version `[VERIFY]`.
3. Start with `TARGET_RPS=1`, `DURATION_SECONDS=30`, and a unique synthetic `RUN_ID`. Do not increase until correctness checks pass.
4. Save tool output and run metadata. Record intended rate, actual starts/completions, errors, and generator CPU.
5. Write timestamped phase markers (`warm-up`, `steady`, `ramp-down`) to CSV if annotations are not verified.
6. Repeat only after a clean, valid run.

**Abort:** Ctrl-C/host process termination for the generator; stop the local service if it behaves unexpectedly. Confirm the fault state is cleared.

**Expected evidence:** Valid local target, response correctness, raw result data, run ID, actual-vs-offered rate, generator health.

**Acceptance:** The script refuses a non-allow-listed host; the run remains within the configured rate/duration caps; correctness checks and metadata are retained.

**Troubleshooting:** If actual arrivals fall below the target, inspect generator resources and tool output before drawing conclusions. If the endpoint differs from `/predict`, adapt the local path while retaining target validation.

**Cleanup:** Stop the generator, remove only test-prefixed data, restore any temporary service settings, and confirm baseline health.

### Lab 2 — Coordinated-omission demonstration

**Objective:** Compare fixed-concurrency closed-loop behavior with a constant-arrival open-loop scenario during a local injected stall.

**Setup:** Use a deterministic local endpoint that delays responses for a short, controlled interval. Do not inject delay into any external service.

**Procedure:**

1. Run a low fixed-concurrency workload for 60 seconds `[ILLUSTRATIVE]`; capture raw latency and request starts.
2. Enable a local-only delay, for example 500 ms for a bounded 5-second window `[ILLUSTRATIVE]`.
3. Repeat the closed-loop run, then run the open-loop harness at a low rate with the same request mix.
4. Compare intended arrivals, actual starts, late/dropped iterations, completions, and latency samples during the stall.
5. Repeat once with the fault disabled to verify recovery.

**Expected observation:** Closed-loop starts may decline during the stall because workers wait for completions. Open-loop arrivals continue to be scheduled independently, although the generator may itself miss/delay arrivals.

**Acceptance:** Report the arrival schedule and the actual observed behavior; do not claim a universal correction factor. If generator health fails, mark the run invalid.

**Cleanup:** Disable the delay and verify baseline latency and error rate.

### Lab 3 — Knee/capacity test

**Objective:** Identify the first measured knee under a predeclared rule.

**Procedure:** Use a short stepwise rate ladder, such as 1, 2, 3, 4, 5 requests/s `[ILLUSTRATIVE]`, with 30–60 seconds per step. Use lower rates if resource pressure rises. Keep payload and cache state consistent. Collect the table in Section 3.5.

**Acceptance:** At least three valid steps; raw sample count and generator health recorded; a knee rule stated before interpreting the data; first bottleneck supported by at least two independent signals where possible.

**Failure modes:** Too few samples, different request mix, cache warming mixed into steady state, generator saturation, telemetry dropped, or concurrent host activity.

**Cleanup:** Stop the workload, remove test data, return to baseline, and retain the step table.

### Lab 4 — Stress/overload plus spike and autoscaler lag

**Objective:** Observe controlled degradation and recovery without risking shared systems.

**Profile:** Core, local simulator preferred; kind optional.

**Procedure:**

1. Set low local caps and a hard maximum duration (e.g. 120 seconds `[ILLUSTRATIVE]`).
2. Increase offered rate one step at a time until the predeclared abort condition or knee is reached; do not continue beyond the safety boundary.
3. For a spike, briefly raise the offered rate within the configured maximum, then restore the previous rate.
4. Record error rate, goodput, queue depth, p95/p99, CPU/memory, and time to return to baseline.
5. If kind/HPA is already available, observe scale signal and ready-capacity timing; verify metric prerequisites and HPA behavior `[VERIFY]`. Otherwise simulate a scale delay in a local model.

**Acceptance:** The test has an explicit abort path; no external target; recovery time is measured from the stated start/end definitions; the conclusion separates observed behavior from inferred cause.

**Cleanup:** Stop generator, remove injected delay/pressure, restore replica count and limits, verify baseline.

### Lab 5 — Bounded soak with planted slow leak

**Objective:** Distinguish persistent growth from warm-up/allocator effects.

**Profile:** Core. Keep duration to 2–4 hours or use an explicitly accelerated deterministic simulation. Never run an unattended unbounded soak.

**Procedure:**

1. Record baseline memory/RSS, connections, file descriptors, queue depth, disk use, and request mix.
2. Run a low steady workload and sample resource usage at a fixed interval.
3. In a disposable local branch, enable a small planted leak (for example, retaining a bounded test object per request at a slow rate); ensure the process and data are isolated.
4. Collect timestamped samples. Plot resource against elapsed time. Compare a fault-enabled run to a no-leak run.
5. Estimate slope and uncertainty only if sample count/window support it; document assumptions and any nonlinear behavior.
6. Project time to a chosen local limit only under an explicit linear-growth assumption. Do not run until OOM to “prove” it.

**Acceptance:** The report includes sample interval, units, window, slope method, uncertainty limitations, projected-limit assumptions, and a cache-warm-up comparison. It explicitly says a short soak cannot rule out a multi-day leak.

**Abort:** Stop on predeclared memory/disk/latency limits. Never intentionally fill the host disk.

**Cleanup:** Disable the planted leak, stop the process, verify resources return to baseline or explain allocator retention, and delete only the lab artifacts.

### Lab 6 — Resilience-under-load matrix

**Objective:** Test one fault at a time under bounded local load.

Run at least the local dependency-slowdown and replica-kill scenarios if safely available. Node drain/PDB, cache flush, or DB failover are optional and only for existing disposable local infrastructure.

For each scenario record:

| Field | Record |
|---|---|
| Hypothesis | [TO MEASURE] |
| Precondition and target | [TO MEASURE] |
| Fault and duration | [TO MEASURE] |
| Abort threshold | [TO MEASURE] |
| Expected result | [TO MEASURE] |
| Observed result | [TO MEASURE] |
| SLO impact and recovery time | [TO MEASURE] |
| Cleanup and prevention | [TO MEASURE] |

**Acceptance:** Each executed fault has an abort condition, a cleanup command/action, and before/after health evidence. Unavailable infrastructure is marked “not run” and covered with a deterministic fixture—not claimed as executed.

### Lab 7 — Backfill versus online concurrency

**Objective:** Quantify online impact from batch competition and evaluate isolation.

**Procedure:**

1. Run online synthetic requests alone and record p95/p99, errors, goodput, and generator health.
2. Run a bounded synthetic backfill with fixed record count and concurrency cap alongside online requests.
3. Repeat with a lower batch concurrency or isolated queue/resource cap.
4. Compare online and batch outcomes; do not treat faster batch completion as success if online SLO is violated.
5. Restore the original configuration and verify baseline.

**Acceptance:** Both online and batch metrics are reported; the isolation change is narrow and reversible; the backfill cannot create unbounded resource use.

### Lab 8 — Statistical comparison with A/A checks

**Objective:** Compare raw request samples and validate decision logic.

**Procedure:**

1. Create JSON files containing raw latency samples (milliseconds), not only p95/p99.
2. Run the Section 4.1 comparison script; retain sample counts, medians, p95/p99, and bootstrap interval.
3. Run equivalent-build A/A pairs repeatedly in the intended environment to observe noise.
4. Use a synthetic planted regression fixture to check whether the chosen gate catches a material shift.
5. Document interleaving, warm-up, autocorrelation risk, and the predeclared practical threshold.

**Acceptance:** The report does not claim causality from an interval alone; A/A false positives are counted from repeated actual pairs, not guessed; insufficient data yields “inconclusive.”

### Lab 9 — Performance CI smoke gate

**Objective:** Build a bounded local gate for p95, CPU-seconds per successful request (or documented substitute), error rate, goodput, and run validity.

**Gate decision logic example:**

```python
# File: scripts/gate_decision.py
def decide(candidate, baseline, limits):
    required = ("p95_ms", "cpu_seconds_per_success", "error_rate", "goodput_rps")
    for name, obj in (("candidate", candidate), ("baseline", baseline)):
        if not isinstance(obj, dict) or any(k not in obj for k in required):
            return "INCONCLUSIVE", f"{name} missing required fields"
        if any(not isinstance(obj[k], (int, float)) for k in required):
            return "INCONCLUSIVE", f"{name} has non-numeric required fields"
        if obj["goodput_rps"] <= 0:
            return "INCONCLUSIVE", f"{name} has no successful goodput"
    if not candidate.get("run_valid", False) or not baseline.get("run_valid", False):
        return "INCONCLUSIVE", "invalid run or generator health"
    if candidate["error_rate"] > limits["max_error_rate"]:
        return "REGRESSION", "error rate exceeds limit"
    if candidate["p95_ms"] > baseline["p95_ms"] * (1 + limits["p95_tolerance"]):
        return "REGRESSION", "p95 exceeds declared relative tolerance"
    if candidate["cpu_seconds_per_success"] > baseline["cpu_seconds_per_success"] * (1 + limits["cpu_tolerance"]):
        return "REGRESSION", "CPU per successful request exceeds tolerance"
    if candidate["goodput_rps"] < baseline["goodput_rps"] * (1 - limits["goodput_tolerance"]):
        return "REGRESSION", "goodput fell beyond tolerance"
    return "PASS", "all configured point-estimate checks passed; uncertainty check still required"
```

This small example is a guardrail sketch, not a complete statistically defensible CI gate. Add a confidence/uncertainty rule based on raw samples, repeated interleaved runs, and A/A noise. The final verdict should be `INCONCLUSIVE` if the run is invalid or the evidence is insufficient. Test it with (1) a baseline/candidate A/A fixture and (2) a planted regression in p95 or CPU/request; verify the gate does not mislabel invalid data as a pass.

**Acceptance:** Planted regression is caught by the configured rule; A/A is evaluated under repeated runs and a documented false-positive tolerance; baseline drift is reviewed rather than silently accepted.

### Lab 10 — Performance report

Create a report using a clearly labelled synthetic example or populate it with measured values. Do not state that a real test ran unless it did.

```text
# Performance test report
Run ID: [TO MEASURE]
Question / hypothesis: [TO MEASURE]
Target: local allow-listed service only
Build / git SHA / data version: [TO MEASURE]
Environment and versions: [TO MEASURE]
Workload mix / offered rate / duration: [TO MEASURE]
Warm-up handling: [TO MEASURE]
Sample count and raw data path: [TO MEASURE]
Offered rate / achieved starts / throughput / goodput: [TO MEASURE]
p50 / p95 / p99 / max: [TO MEASURE]
Error rate and classes: [TO MEASURE]
CPU-seconds per successful request: [TO MEASURE]
Memory/resource slope and interval: [TO MEASURE]
Queue depth / pool waits / dependency latency: [TO MEASURE]
Generator CPU / memory / network / missed arrivals: [TO MEASURE]
SLO impact and recovery time: [TO MEASURE]
First bottleneck and supporting evidence: [TO MEASURE]
Verdict: IMPROVEMENT / REGRESSION / INCONCLUSIVE
Limitations, cleanup, reproducibility commands: [TO MEASURE]
```

### Lab 11 — Observability-stack soak

**Objective:** Determine whether telemetry collection or storage becomes a bottleneck during the test.

**Profile:** Core+Logs for log-volume questions; Full only when trace evidence is essential. Do not run all components at once on an 8 GB machine.

**Procedure:**

1. Measure baseline Prometheus/Collector/Loki resource use, disk, telemetry ingestion, and query latency if the components are available.
2. Run a bounded low-rate test while sampling backend CPU/memory, disk growth, buffered/dropped telemetry indicators, and query latency.
3. Compare a short window with and without trace collection if traces are not required for the question.
4. If backend metrics are unavailable, use fixture files with byte counts and record that live backend measurement was not performed.
5. Check retention/compaction behavior only using the installed version's official documentation `[VERIFY]`.

**Acceptance:** Resource trend and telemetry volume are recorded; no deletion or retention change is assumed to have occurred without evidence; cleanup and disk-space verification are documented.

### Lab 12 — Load-test safety checklist exercise

**Objective:** Validate that unsafe targets and unbounded configurations are rejected before a request is sent.

```python
# File: scripts/safety_guard.py
from urllib.parse import urlparse

ALLOWED = {("http", "127.0.0.1:8000"), ("http", "localhost:8000")}

def validate_target(url, duration_s, rate, max_duration_s=300, max_rate=20):
    parsed = urlparse(url)
    if (parsed.scheme, parsed.netloc) not in ALLOWED:
        raise ValueError("refusing target outside local allow-list")
    if isinstance(duration_s, bool) or not isinstance(duration_s, int) or not 1 <= duration_s <= max_duration_s:
        raise ValueError("duration outside configured bound")
    if isinstance(rate, bool) or not isinstance(rate, int) or not 1 <= rate <= max_rate:
        raise ValueError("rate outside configured bound")
    return True

if __name__ == "__main__":
    cases = [
        ("http://127.0.0.1:8000", 30, 2, True),
        ("https://example.com", 30, 2, False),  # intentionally unsafe fixture
        ("http://127.0.0.1:8000", 3600, 2, False),
    ]
    for url, duration, rate, expected in cases:
        try:
            actual = validate_target(url, duration, rate)
        except ValueError:
            actual = False
        assert actual is expected, (url, duration, rate, actual, expected)
    print("safety fixtures: PASS")
```

**Acceptance:** The unsafe public-host fixture and overlong-duration fixture are rejected; no HTTP request is made by the validator; all other lab scripts enforce equivalent bounds before traffic starts.

---

## 7. Additional required artifacts and evidence templates

### Before/after table

| Field | Baseline | Candidate | Validity / confidence notes |
|---|---|---|---|
| Offered load (requests/s) | [TO MEASURE] | [TO MEASURE] | |
| Achieved throughput/goodput | [TO MEASURE] | [TO MEASURE] | |
| p50 / p95 / p99 | [TO MEASURE] | [TO MEASURE] | raw sample count |
| Error rate | [TO MEASURE] | [TO MEASURE] | include classes |
| CPU-seconds per successful request | [TO MEASURE] | [TO MEASURE] | method |
| Memory/resource slope | [TO MEASURE] | [TO MEASURE] | units and window |
| Queue depth / pool wait | [TO MEASURE] | [TO MEASURE] | |
| Generator resource use | [TO MEASURE] | [TO MEASURE] | validity check |
| SLO impact | [TO MEASURE] | [TO MEASURE] | objective and window |
| Recovery time | [TO MEASURE] | [TO MEASURE] | start/end definitions |
| First bottleneck | [TO MEASURE] | [TO MEASURE] | evidence |
| Statistical uncertainty | [TO MEASURE] | [TO MEASURE] | method and assumptions |

### Results repository layout (illustrative only)

```text
performance-results/
  README.md
  runs/
    <run_id>/
      metadata.json
      raw-latency-baseline.json
      raw-latency-candidate.json
      phases.csv
      summary.json
      report.md
```

This is a suggested layout inside the learner's own lab workspace, not a request to create these repository files for this lesson. Retain only the data needed for reproducibility and privacy; avoid secrets/PII.

### Capacity-knee plot data

Export CSV with columns `offered_rps,actual_starts_rps,goodput_rps,p50_ms,p95_ms,p99_ms,error_rate,queue_depth,sut_cpu_pct,generator_cpu_pct,valid`. Plot latency and goodput against offered rate; mark invalid steps rather than silently dropping them.

---

## 8. Required worked incident analyses

All timelines and values below are `[SYNTHETIC]`; they are teaching scenarios, not claims about the learner's system.

### 8.1 Closed-loop estimate was 3× too optimistic

**Symptoms:** A prior capacity estimate based on fixed concurrency looked healthy, but a constant-arrival rehearsal showed worse tails. “3×” is an illustrative incident detail, not a universal ratio.

**Evidence:** Compare intended arrival schedule, actual starts, late/dropped arrivals, client latency samples, generator health, and queueing during stalls.

**Reasoning:** The closed-loop model reduced starts while requests were slow, omitting some arrivals that would have occurred under external demand. The original test answered a different question.

**Immediate mitigation:** Recalculate the launch decision using a valid arrival-rate workload; lower launch exposure or add conservative headroom until evidence is sufficient.

**Durable fix:** Version the workload model, test both open- and closed-loop if both client behaviors matter, and validate generator health.

**Regression guard:** Add a stall fixture and a check that compares scheduled arrivals to actual starts. **Verification:** repeat with the same build and request mix. **Prevention:** review workload assumptions during release planning.

### 8.2 Soak skipped; slow leak caused periodic OOM

**Symptoms:** Service looked healthy in short load tests but failed after long uptime.

**Evidence:** Resource time series, restart/OOM records, connection/file-descriptor counts, workload stability, and profile data where available.

**Hypothesis:** A leak or unbounded resource accumulation persisted after warm-up. **Confirm:** reproduce under stable local load and compare leak-enabled/no-leak branches.

**Mitigation:** Reduce load or restart according to the service's safe recovery procedure; do not claim restart is a durable fix.

**Durable fix:** Release the resource, add a bounded soak and growth alert, test recovery, and document uncertainty in time-to-limit projection.

### 8.3 Tiny staging dataset passed; production volume was larger

**Symptoms:** Small fixture had acceptable latency, while large payload/data distribution caused regression.

**Evidence:** Dataset sizes, payload-size percentiles, cache behavior, query plans where relevant, serialization time, memory and dependency signals.

**Mitigation:** Restrict exposure or use a representative approved staging dataset. **Fix:** add volume classes and skew/hot-key scenarios to the workload catalog. **Guardrail:** require data-volume metadata and coverage in the test report.

### 8.4 Generator saturated first

**Symptoms:** Offered rate increased, but achieved starts did not; service metrics looked deceptively healthy.

**Evidence:** Generator CPU/network/event loop, tool dropped-arrival output, actual start/completion rate, SUT resource use.

**Mitigation:** Mark the run invalid. **Fix:** reduce per-request generator overhead, use a suitably isolated generator, or use a lower workload that the generator can sustain. Do not blame the service without evidence.

### 8.5 Shared CI runner made gate flaky

**Symptoms:** A noisy gate was disabled, then a regression shipped.

**Evidence:** A/A distribution, runner contention, run-to-run variance, build/workload metadata.

**Fix:** use interleaved repetitions, a noise-aware verdict, a pinned workload, and an `INCONCLUSIVE` path. Keep the gate but avoid making it a single-sample oracle.

### 8.6 Stress test affected a shared database

**Symptoms:** Another team saw elevated latency during a test.

**Evidence:** Target and dependency identities, outbound network logs, run configuration, approvals.

**Immediate response:** Stop generator and fault injection; notify affected owners through approved channels. **Prevention:** local stubs only for this curriculum, strict target guard, and preflight test that rejects non-local destinations.

### 8.7 Autoscaler lag exceeded spike rise time

**Symptoms:** p95/errors crossed the objective before capacity became ready.

**Evidence:** Offered rate, desired/current/ready replicas, scale signal, pod startup/readiness time, queue, SLO impact.

**Fix options:** keep safe headroom, reduce startup time, improve scaling signal, pre-scale for known events, or shed load while capacity arrives. Validate in local kind only if safely available; otherwise use a simulator.

### 8.8 Backfill competed with online inference

**Symptoms:** Batch throughput rose, but online tail latency and errors worsened.

**Evidence:** Online and batch goodput, queue/pool wait, CPU throttling, dependency saturation.

**Fix:** cap batch concurrency, separate queues, use quotas/priorities, or schedule away from online peaks. Re-run both workloads and verify online SLO recovery.

### 8.9 Averages hid p99

**Symptoms:** Report says average improved while p99 violated the objective.

**Evidence:** Raw samples/histograms, sample count, request mix, errors, slow trace distribution.

**Fix:** publish percentiles and goodput with sample counts; use a predeclared tail objective. Do not average p99 values across runs.

### 8.10 Retries amplified overload

**Symptoms:** Request rate and dependency work rose while useful completions fell.

**Evidence:** Retry count, timeout distribution, downstream latency, queue depth, error classes.

**Fix:** bounded retry budget, exponential backoff with jitter where appropriate, timeouts aligned to dependency behavior, and load shedding. Validate recovery time as well as peak throughput.

### 8.11 Cache stampede or hot key

**Symptoms:** A subset of keys dominates latency and dependency traffic; aggregate average hides it.

**Evidence:** key-skew distribution using safe synthetic categories, cache hit ratio, per-stage traces, backend request rate.

**Fix:** request coalescing, bounded concurrency, TTL jitter, or cache policy appropriate to the application. Do not label raw customer keys in metrics.

### 8.12 Warm-up misclassified as a leak

**Symptoms:** Memory rises early then plateaus.

**Evidence:** Longer resource time series, cache size, allocator/RSS/heap distinction, stable request mix.

**Fix:** separate warm-up from steady state and compare against a no-leak control. Do not project OOM from a non-stationary early slope.

### 8.13 Observability backend saturated

**Symptoms:** Missing traces/metrics or delayed ingestion during the load test.

**Evidence:** Collector/backend CPU, queues, drops, disk/query latency, generator and SUT telemetry gaps.

**Fix:** mark the run's observability validity as compromised, reduce telemetry overhead/profile, or use fixtures. Unit 12 governs telemetry cost controls. Never interpret absent evidence as proof of healthy behavior.

### 8.14 Generator failed to sustain open-loop arrivals

**Symptoms:** Tool configuration requested a rate, but actual starts were lower.

**Evidence:** scheduled versus started arrivals, dropped/late iterations, generator CPU and network.

**Fix:** invalidate the run, lower rate or improve generator capacity, and repeat. Report achieved starts rather than presenting the intended rate as measured load.

---

## 9. Troubleshooting matrix and decision tables

### Troubleshooting matrix

| Symptom | Likely causes | First evidence | Safe next action | Verification / rollback |
|---|---|---|---|---|
| p95/p99 rises; average stable | Tail-specific dependency, queue, skew | Raw samples, slow traces, queue/pool waits | Compare slow and median requests | Repeat matched workload |
| Offered rate rises; goodput flattens | Knee, saturation, errors | Actual starts, goodput, queue, CPU | Stop at predeclared boundary | Restore baseline |
| Errors rise during spike | Overload, timeout/retry amplification | Error classes, retries, dependency latency | Reduce rate/restore fault-free state | Recovery time and error rate |
| Queue grows while CPU low | Slow dependency, pool limit, blocked workers | Pool wait, dependency spans, queue age | Inspect downstream capacity | Confirm queue drains |
| CPU throttling/pool wait rises first | CPU limit or pool contention | Throttle counters, pool wait | Narrowly adjust local cap/config | Compare distributions |
| Dependency latency dominates | Slow stub/DB/model/feature fetch | Trace and dependency metrics | Isolate one dependency | Remove delay and repeat |
| Generator CPU/network saturated | Client bottleneck | Generator metrics, actual starts | Mark run invalid | Repeat at sustainable rate |
| Open-loop arrivals not achieved | Too few workers or generator limits | Scheduled/start/dropped count | Lower rate or tune generator safely | Achieved rate matches target within declared tolerance |
| Sample counts differ | Invalid runs or workload changes | Metadata and raw files | Reconcile before comparison | Re-run matched pair |
| A/B noisy | Shared host, small sample, drift | A/A results and run order | Mark inconclusive | Repeat interleaved runs |
| A/A false regression | Gate too sensitive | Repeated A/A distribution | Adjust justified tolerance or runner | Re-test A/A and planted regression |
| Memory grows slowly | Leak, cache, allocator, workload drift | Longitudinal resource data | Compare no-leak control | Restart/cleanup and retest |
| Memory rises then plateaus | Warm-up/cache/allocator retention | Extended time series | Avoid leak claim without more evidence | Check plateau repeatability |
| Connections/descriptors grow | Leak or pool misconfiguration | Counts, pool stats, error logs | Stop before resource limit | Confirm counts stabilize |
| Disk/log volume grows | Debug noise, duplicate shipping | bytes/time, source identity | Reduce known noise safely | Verify incident lines retained |
| HPA scales after spike | Startup/metric lag | desired/current/ready replicas | Use headroom or shed load | Measure time-to-capacity |
| Backfill harms online SLO | Shared CPU/DB/queue | online and batch metrics | Cap batch concurrency | Verify online baseline |
| Gate catches regression but fails A/A | Noise or threshold too strict | A/A and effect-size results | Return inconclusive; tune evidence | Both fixture cases pass expected behavior |
| Gate misses planted regression | Weak metric/rule or too little data | Gate report and raw samples | Strengthen guardrail | Planted regression reliably detected |
| Traces/metrics missing | Sampling, pipeline pressure, config | Collector/backend health | Mark run invalid | Telemetry completeness restored |
| Recovery not baseline | Persistent queue/cache/fault/config | Resource and dependency signals | Stop further tests; restore config | Repeat low-rate health check |
| Safety validator rejects target | Wrong target or typo | Parsed host and allow-list | Do not bypass guard | Fix target only if local and approved |

### Decision tables

**Open-loop vs closed-loop**

| Choose | When | Main caveat |
|---|---|---|
| Open-loop | External arrivals continue during slow responses | Generator must sustain scheduled arrivals |
| Closed-loop | Fixed worker/client pool is the real workload | Can under-represent demand during stalls |
| Both | Both client behaviors matter | Keep conclusions separate |

**Load vs stress vs spike vs soak vs knee**

| Experiment | Primary question |
|---|---|
| Load | Does expected peak meet objectives? |
| Stress | How does the system fail and recover beyond capacity? |
| Spike | Can it absorb a sudden transient? |
| Soak | Does behavior drift over time? |
| Knee | Where does marginal useful throughput deteriorate? |

**Service vs generator bottleneck**

| Evidence | Interpretation |
|---|---|
| Generator saturated; SUT resources modest; actual starts low | Generator-limited or invalid run |
| Generator healthy; SUT queue/saturation rises; goodput flattens | SUT/dependency bottleneck likely |
| Both saturated | Separate the effects; current run may not isolate cause |

**Leak vs warm-up/allocator retention**

| Pattern | Next discriminating check |
|---|---|
| Resource rises then plateaus | Longer stable run and no-leak control |
| Resource grows persistently at stable workload | Inspect retained objects/resources; repeat |
| RSS high but heap/active objects stable | Consider allocator/fragmentation; do not infer leak from RSS alone |
| Connections/descriptors monotonically rise | Inspect close/release paths and pool settings |

**Regression vs noise vs inconclusive**

| Verdict | Rule |
|---|---|
| Regression | Predeclared guardrail violated with valid evidence |
| Improvement | Meaningful improvement, no guardrail regression, adequate validity |
| Inconclusive | Invalid run, insufficient samples, high uncertainty, or confounded workload |

**Scale vs optimize vs shed load vs backpressure**

| Signal | Candidate response |
|---|---|
| Independent stateless replicas help; dependency has headroom | Consider horizontal scaling after validation |
| One span/query dominates | Optimize that path and verify |
| Capacity exhausted; safety/SLO at risk | Shed/reject bounded work |
| Queue is growing and downstream cannot catch up | Apply backpressure/concurrency caps; do not enqueue without bound |

**Run now vs abort vs require approval**

| Condition | Decision |
|---|---|
| Local allow-listed target, preflight complete, caps set | Run bounded test |
| Unexpected external traffic, resource threshold crossed, unknown target | Abort immediately |
| Shared/production dependency, node drain, DB failover, or unapproved impact | Require explicit authorization and approved plan; not part of required local labs |

---

## 10. Reference implementation quality and verification

### Running the Python examples

Use a Python 3 environment and confirm the actual interpreter:

```bash
python3 --version
python3 -m unittest discover -s tests -v
```

`[VERIFY]` Adjust import paths to the actual workspace layout. The examples show an illustrative layout; the lesson does not create additional repository files.

### Code-quality expectations

Every analysis script should:

- Validate inputs and reject empty/malformed data explicitly.
- Preserve raw per-request observations where feasible.
- Include units and sample counts.
- Separate missing data from measured zero.
- Emit deterministic reports and exit codes.
- Include unit tests for normal and edge cases.
- Avoid secrets, PII, unbounded labels, and arbitrary remote targets.
- Document assumptions and limitations.

### Statistical guardrails

- Bootstrap raw request samples only when resampling assumptions are reasonable.
- Do not treat per-request samples as independent when strong time correlation is present.
- Compare equivalent request mix, environment, build settings, warm-up, and load shape.
- Use both A/A noise characterization and a planted-regression test.
- Do not equate statistical significance with operational importance.
- A confidence interval that overlaps zero does not prove equivalence; define a practical equivalence/tolerance region in advance.
- Do not infer causal attribution from a before/after comparison alone if multiple variables changed.

### Example result interpretation

**Example — yours will differ in values, IDs, and timings.** `[SYNTHETIC]` Suppose candidate p95 is 12% worse, the 95% bootstrap interval for median difference is positive, error rate is unchanged, and the candidate's generator had 95% CPU. This is not automatically a service regression: the generator may have distorted the workload. Mark the run invalid or inconclusive, repeat with a healthy generator, and then evaluate the candidate. This avoids mistaking a client-side bottleneck for a service bottleneck.

---

## 11. Sources and version discipline

Use the official documentation for the installed versions. The following are established project documentation entry points; check the current version and relevant section before relying on exact syntax:

- k6 documentation: `https://grafana.com/docs/k6/latest/` — installation, scenarios/executors, thresholds, results, and outputs. `[VERIFY]` executor names/options and arrival-rate behavior against the installed version.
- Locust documentation: `https://docs.locust.io/` — awareness-level alternative; verify worker/concurrency and load-shape behavior for the installed version.
- Prometheus documentation: `https://prometheus.io/docs/` — histograms, query semantics, scrape metrics, and recording rules.
- Grafana documentation: `https://grafana.com/docs/grafana/latest/` — dashboard annotations and data-source behavior `[VERIFY]`.
- Kubernetes documentation: `https://kubernetes.io/docs/` — HPA, PDB, node drain, readiness, and workload behavior `[VERIFY]`.
- kind documentation: `https://kind.sigs.k8s.io/` — local cluster limitations and commands `[VERIFY]`.
- Python documentation: `https://docs.python.org/3/` — standard library, profiling, `tracemalloc`, and runtime behavior.
- py-spy project documentation: `https://github.com/benfred/py-spy` — optional profiler installation, permissions, platform limits, and commands `[VERIFY]`.

These URLs are documentation entry points, not a claim that external pages were checked during this lesson's creation. No external command output or benchmark is asserted.

### Version checklist

Before use, verify:

- k6 installation, scenario/executor names, arrival-rate semantics, dropped/late iteration behavior, output formats, and thresholds.
- Histogram and percentile semantics in the installed Prometheus/Grafana stack.
- HPA metric availability and scaling behavior for the local cluster.
- kind/node-drain/PDB support and safety.
- Python version and profiler availability/permissions.
- Prometheus/Grafana/Collector metric names and any query integrations.
- Statistical method assumptions and any third-party library version if one is introduced.

Keep an evidence ledger with `item`, `installed version`, `verification command/doc`, `result`, and `date`. Mark anything not checked `[VERIFY]`.

---

## 12. Practice questions and answer key

### Questions

1. **Workload model and coordinated omission.** A fixed-concurrency test records a median of 80 ms and a p99 of 250 ms. During a local 1-second stall, request starts drop sharply. Explain why these results may understate the latency experience of a constant-arrival workload. What evidence must be collected before accepting an open-loop result?

2. **Distribution, goodput, and knee.** At a higher offered rate, throughput rises from 90 to 100 requests/s, but useful goodput rises from 86 to 87/s, p99 doubles, and queue depth grows. Is this a capacity improvement? State the likely interpretation and the evidence needed to identify the first bottleneck.

3. **Soak slope and projection.** A 90-minute sample shows memory rising by 45 MiB. Calculate the naïve slope in MiB/hour. Explain why this is not enough to claim an OOM time, and list what uncertainty and control evidence you would need.

4. **Statistics, A/A, and CI.** A candidate p95 is 8% worse than baseline, but the A/A runs frequently vary by 10%. The candidate generator also reached high CPU. What verdict should the gate return, and what experiment should happen next?

5. **Safety and workload isolation.** A synthetic backfill increases batch goodput but causes online p99 and errors to breach their predeclared limits. Describe the immediate safe action, the evidence to retain, and how to test a concurrency cap without risking a shared workload.

### Answer key

1. Fixed-concurrency workers wait for requests to finish before issuing more, so starts can fall during a stall; a constant-arrival workload would continue scheduling arrivals independently. Collect intended arrival schedule, actual starts, completions, late/dropped arrivals, generator CPU/network, raw latency samples, request mix, and service saturation. A run with a saturated generator is invalid for the intended-rate claim.

2. Raw throughput rose, but goodput barely improved while p99 and queue depth worsened. That suggests diminishing useful returns and likely movement past the knee, not a clean capacity improvement. Check generator health, service saturation, dependency spans/latency, pool waits, retries, errors, and queue age. Identify the first bottleneck using corroborating signals rather than one trace alone.

3. \(45\text{ MiB}/1.5\text{ h}=30\text{ MiB/h}\) naïvely. That slope assumes the 90-minute window is representative and linear. Collect more samples, compare with a no-leak control, separate warm-up/cache effects, record workload stability and memory/RSS/heap differences, and estimate uncertainty. Projection to a limit requires a chosen limit, current value, positive stable slope, and explicit linearity assumption; it is not a guarantee.

4. Return **INCONCLUSIVE** because observed A/A noise is larger than the candidate effect and generator CPU threatens run validity. Repeat with a healthy generator, interleaved A/B order, identical workload and warm-up, sufficient raw samples, and a predeclared practical threshold. Do not loosen the gate simply to make it green; verify both A/A false-positive behavior and planted-regression detection.

5. Stop the backfill or reduce it to the safe cap immediately, then verify online recovery. Retain run ID, rate/concurrency, online p99/errors/goodput, batch goodput, queue/pool/CPU signals, generator health, and recovery time. Repeat locally with synthetic data and a fixed workload, changing only the batch concurrency cap; confirm online objectives recover while batch remains bounded and useful. Do not test on shared/production workloads without explicit authorization and an approved plan.

---

## 13. Final completeness and correctness audit

This is a self-audit of the lesson structure, not independent verification of every environment-specific command. No claim is made that live k6, Grafana, Prometheus, Kubernetes, or soak integrations were executed.

| # | Audit item | Status | Evidence / limitation |
|---:|---|---|---|
| 1 | Exact target filename, module, Unit 13 | PASS | Header identifies exact file and M11 Unit 13 |
| 2 | L1 taxonomy, open/closed loop, coordinated omission, distributions, goodput, generator health | PASS | Sections 2.1–2.5 |
| 3 | L2 realistic workload design | PASS | Section 3 and Lab 1 |
| 4 | L3 statistics, A/A, leak-vs-cache, capacity, triage | PASS | Section 4 and Labs 5, 8 |
| 5 | L4 resilience, CI, governance, cost-aware capacity, safety | PASS | Section 5 |
| 6 | All 12 mandatory labs with acceptance and cleanup | PASS | Section 6 |
| 7 | Primary tool selected and version-sensitive syntax marked | PASS | k6 selected; executor/config behavior `[VERIFY]` |
| 8 | Required harness, omission, knee, stress/spike, soak, resilience, isolation, stats, CI, report, observability soak, safety | PASS | Labs 1–12 |
| 9 | Planted regression and A/A behavior required | PASS | Labs 8–9 |
| 10 | Soak slope and projection assumptions | PASS | Section 4.6 and Lab 5 |
| 11 | Raw distributions or explicit limitations | PASS | Section 4.1; raw samples used by example script |
| 12 | Test-run observability and generator metrics | PASS | Section 3.4 |
| 13 | Required incident analyses and troubleshooting tables | PASS | Section 8 and Section 9 |
| 14 | Exactly five practice questions and separate answers | PASS | Section 12 |
| 15 | Authorization, local allow-list, caps, abort, cleanup | PASS | Safety contract, common preflight, Lab 12 |
| 16 | Required labs do not target shared/production/third-party systems | PASS | Safety contract and lab instructions |
| 17 | Laptop constraints and production-fidelity limits | PASS | Sections 0 and 5.6 |
| 18 | Results measured/derived/synthetic; no fabricated run claims | PASS | Evidence labels and blank templates |
| 19 | Version-sensitive items marked `[VERIFY]` | PASS | Sections 2.4, 3, 5, 11 |
| 20 | Before/after template and honest conclusion | PASS | Section 7 |
| 21 | No other repository files intentionally changed | PASS | This deliverable is a single Markdown lesson |
| 22 | Full teaching content rather than outline | PASS | Definitions, calculations, code, labs, troubleshooting, and answers included |
| 23 | No invented command output or claimed execution | PASS | Tool runs are described as learner tasks; live integrations not run |

**Not independently verified:** The complete roadmap tree and authoritative M11 syllabus source were not available for independent inspection in this authoring context. This lesson follows the supplied Unit 13 generation prompt. Tool-specific syntax and integrations remain `[VERIFY]`. The audit above checks authored coverage; it is not a substitute for running the learner's local environment tests.

### Completion checklist

- [ ] All safety preflights completed before each executed lab.
- [ ] Each run has a unique ID, version/build metadata, workload, time window, and raw evidence.
- [ ] Invalid generator/telemetry runs are marked invalid rather than treated as service results.
- [ ] Labs 1–12 are complete or explicitly marked not run with a fixture-based alternative.
- [ ] The planted regression is detected and A/A noise is characterized before enforcing CI.
- [ ] Soak slope and projection state assumptions and uncertainty.
- [ ] Before/after report includes offered load, goodput, p50/p95/p99, errors, CPU/request, resource slope, queue, generator health, SLO impact, recovery, bottleneck, and confidence notes.
- [ ] Cleanup restores the local lab baseline and removes only synthetic test artifacts.
- [ ] Conclusion states what the evidence supports and what remains unknown.

**Evidence-retention checklist:** preserve run metadata, raw request samples, phase markers, service/generator resource samples, relevant logs/traces, configuration/build identifiers, test validity notes, abort/cleanup record, analysis outputs, and final decision. Do not retain secrets, PII, or unnecessary payloads.
