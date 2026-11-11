# Storage Performance: IOPS, Throughput, and Latency

## 6.0 Why This Matters in Production

A PostgreSQL-backed data pipeline starts missing its latency objective shortly after a scheduled backup begins. Application p99 latency rises, write transactions take longer, and the ETL workers accumulate temporary files. The first dashboard someone checks is CPU utilization; another person runs `dd` once and declares the volume “fast.” Neither observation is enough to identify the cause.

A defensible investigation follows the I/O path and measures the workload at the right layer. The database may be waiting for WAL durability, the filesystem may be flushing buffered writes, the container may be throttled for CPU, a backup may be competing for I/O, or the storage backend may be enforcing a throughput limit. Similar symptoms can arise from different causes.

This unit teaches how to design a bounded storage experiment, interpret its measurements, and connect them to application outcomes. The running example is a data pipeline that writes to a PostgreSQL service backed by a PersistentVolumeClaim (PVC), while ETL tasks use scratch storage for shuffle and temporary output.

**Fidelity warning:** measurements taken through kind, a container runtime, WSL2, a host filesystem, and page cache are not production storage benchmarks. These labs teach repeatable methodology, interpretation, regression detection, and diagnosis. They do not establish production IOPS, provider limits, backend durability, or real failure-domain behavior.

## 6.1 Learning Objectives and Exit Criteria

By the end of the unit, the learner can:

- Define input/output operations per second (IOPS), throughput, latency, block size, queue depth, and concurrency, and calculate throughput from IOPS and request size.
- Trace an I/O request from an application through system calls, cache, filesystem, block layer, virtualization, and storage backend.
- Explain page cache, `O_DIRECT`, `fsync`, and why a successful write call does not always mean data is durable on persistent media.
- Select and run four bounded `fio` workload profiles against a fresh scratch file on a dedicated PVC.
- Summarize repeated results with explicit median and p95 definitions, validate JSON schemas, and preserve environment metadata.
- Explain why `iostat -x` `%util`, `kubectl top`, a single `dd` test, or a laptop benchmark cannot independently prove storage capacity.
- Design an application-relevant benchmark with warm-up, repeated runs, tail-latency analysis, and controlled variables.
- Explain storage throttling, noisy neighbors, PostgreSQL WAL/checkpoint behavior, and ETL I/O patterns.
- Diagnose a p99 latency spike, storage throttling, a full volume, and a slow database caused by CPU/query behavior rather than storage.
- Run a capacity projection script, state its assumptions, and distinguish regression detection from production capacity planning.
- Clean up lab resources only after verifying the Kubernetes context and explicit target.

**Exit gate:** save the four-profile results and environment record, explain the page-cache comparison, complete the bounded disk-full exercise or its safer alternative, run the capacity projection script, and write one evidence-based incident analysis. If a lab is blocked by an unsupported driver or resource constraint, document the blocker and what was not proven instead of inventing results.

## 6.2 Prerequisites, Lab Safety, and Environment

### Prerequisites

The learner should understand Linux processes and files, containers, Pods and Jobs, PersistentVolumes (PVs), PVCs, StorageClasses, resource requests/limits, and basic Kubernetes troubleshooting. Review these related lessons when needed:

- M05 Unit 1: `01-volumes-persistentvolumes-and-persistentvolumeclaims.md`
- M05 Unit 2: `02-storageclasses-dynamic-provisioning-and-csi-drivers.md`
- M05 Unit 3: `03-volume-snapshots-cloning-and-expansion.md`
- M05 Unit 5: `05-running-databases-and-brokers-with-operators.md`

### Environment preflight

Assume WSL2 Ubuntu or native Linux, approximately 4 CPU cores, 8 GB RAM, and 30 GB free disk. Use kind and a dedicated disposable cluster. Do not run PostgreSQL HA, MinIO, Kafka, a service mesh, and a full observability stack together for this unit.

```bash
kind version
kubectl version
kubectl config current-context
kubectl get nodes -o wide
kubectl get storageclass
df -h .
free -h
docker system df
command -v fio || true
command -v iostat || true
command -v pidstat || true
```

**Expected evidence (illustrative; not executed here):** version information, current context, node list, StorageClass names, free disk and memory, and which local tools are installed. Record the output locally. If the context is not the dedicated lab context, stop.

### Non-negotiable data-safety rules

> **DATA-SAFETY PREFACE — every write-heavy benchmark:** `fio` can overwrite data if directed at a raw device or an existing file. These examples target only a newly created file named `/scratch/fio-scratch.bin` on the dedicated `storage-perf-lab` PVC. Never change `filename` to `/dev/*`, a database data directory, a host path, or a user's existing file. Confirm the Kubernetes context, namespace, PVC, and mount path before running.

- Use only synthetic disposable data.
- Check free host disk before creating PVCs or benchmark files. A PVC request is not a promise that a backend has reserved that exact amount of host space.
- Keep every benchmark bounded by file size and runtime. Do not fill the host filesystem.
- Do not flush host caches or use privileged host commands for this lab.
- Do not change host mount options, remount filesystems, or modify kernel I/O settings.
- Do not delete database files or WAL to free space.
- Commands that delete lab resources must show read-only checks first and require an explicit `--apply` confirmation.
- WSL2 virtual disks can grow as data is written; deleting files inside Linux may not immediately shrink the host-side virtual disk. Follow the documented WSL/virtual-disk reclamation process for your setup only after confirming the correct disk.
- Do not paste real credentials, customer data, or sensitive benchmark files into evidence.

## 6.3 Concept Map and Vocabulary

### The I/O path

```text
Application / database / ETL worker
            |
       read(), write(), fsync()
            |
   Buffered I/O / page cache
       or direct I/O (O_DIRECT)
            |
     Filesystem (ext4, XFS, ...)
            |
 Block layer / device mapper / queues
            |
 Container runtime / VM / virtual disk
            |
 PVC -> PV -> CSI driver -> storage backend
            |
     device, network, or service

Measurements observe different layers:
fio = generated workload + completion behavior
iostat = visible block-device counters
pgbench = PostgreSQL transaction-level behavior
kubectl top = CPU/memory resource metrics, not disk latency
```

### Core performance dimensions

| Dimension | Meaning and units | Simple relationship | Key drivers | Common failure mode |
|---|---|---|---|---|
| IOPS | Completed I/O operations per second; `ops/s` | Count operations over elapsed time | Request size, random/sequential pattern, concurrency, latency, backend limits | Small random operations saturate operation limits before bandwidth |
| Throughput / bandwidth | Bytes transferred per second; B/s, MiB/s, or GB/s | `IOPS × average bytes per operation` | IOPS, request size, sequentiality, protocol/backend caps | Large transfers hit bandwidth limits while IOPS remains modest |
| Latency | Time for an I/O; usually ms or µs | Completion time distribution | Queueing, device service, flushes, contention, network, scheduling | Tail latency rises while mean remains acceptable |
| Queue depth | Number of I/O requests outstanding | Depends on engine, workload, and concurrency | `iodepth`, jobs, async engine, application concurrency | More queueing can increase throughput but worsen latency |
| Concurrency | Number of independent workers/requests | Not identical to queue depth | Clients, jobs, connections, async execution | Too little concurrency underdrives a backend; too much creates contention |
| Request/block size | Bytes per operation | Throughput ≈ IOPS × bytes/op | Application access pattern, filesystem, database page/WAL behavior | A 4 KiB random workload is not comparable to 1 MiB sequential I/O |
| Read/write mix | Fraction of reads versus writes | Must report each direction separately when relevant | Application pattern and write amplification | Aggregate metrics hide slow writes or sync-heavy operations |

**Worked calculation 1 — small random I/O [ILLUSTRATIVE]:** suppose a test completes 8,000 operations/s at an average request size of 4 KiB.

- `4 KiB = 4,096 bytes`
- `8,000 ops/s × 4,096 bytes/op = 32,768,000 bytes/s`
- Decimal throughput is about `32.768 MB/s`; binary throughput is `31.25 MiB/s`.

**Worked calculation 2 — larger sequential I/O [ILLUSTRATIVE]:** suppose another test completes 500 operations/s at 1 MiB per operation.

- `1 MiB = 1,048,576 bytes`
- `500 ops/s × 1,048,576 bytes/op = 524,288,000 bytes/s`
- That is `524.288 MB/s` decimal or `500 MiB/s` binary.

The second workload has much lower IOPS but much higher throughput. Neither result is inherently “better”; the right metric depends on the application. Use bytes and bits consistently: `1 byte = 8 bits`, and do not compare decimal MB/s with binary MiB/s without conversion.

### Tail latency and durable writes

Latency is a distribution, not a single number. p50 is the median; p95 is the value at or below which 95% of measured operations completed; p99 is the analogous 99th percentile. A small fraction of very slow writes can delay transactions, requests, or pipeline stages even when the average looks healthy.

PostgreSQL uses write-ahead logging (WAL): changes are represented in WAL before corresponding data-page changes are considered durable according to PostgreSQL’s configured durability contract. `fsync` and related synchronization calls request that data reach stable storage according to the operating system, filesystem, device, and virtualization stack. The exact guarantees depend on the entire stack and its correctness. A `write()` may complete after data enters the page cache; that is not by itself proof that data is safely persisted through power loss. `fsync()` asks the OS to synchronize relevant file state, but it cannot repair a backend that falsely acknowledges flushes.

PostgreSQL’s `synchronous_commit`, `fsync`, checkpoint, and WAL settings affect durability and latency trade-offs. Never disable durability settings as a generic performance fix. Any non-default durability configuration requires explicit risk acceptance, authoritative documentation review, and workload-specific testing. See the PostgreSQL documentation listed in Section 6.14.

### Page cache, direct I/O, and filesystems

- **Page cache:** the kernel caches file data in memory. A buffered read may be served from RAM rather than storage; buffered writes can be acknowledged before all data reaches persistent media.
- **`O_DIRECT` / `direct=1`:** asks for direct I/O where supported by the filesystem/kernel and tool. Alignment, filesystem behavior, and fallback/error behavior can vary. It reduces some page-cache effects but does **not** guarantee a perfect physical-device benchmark.
- **`fsync`:** requests synchronization of file data and relevant metadata as defined by the API and filesystem. It can expose flush latency that ordinary buffered writes do not.
- **ext4 and XFS:** both are mature Linux filesystems with different implementation and operational characteristics. Do not declare one universally faster; filesystem version, mount options, workload, kernel, and backend matter.
- **`noatime`:** a mount-option concept that reduces access-time metadata updates in applicable cases. This lesson does not prescribe remounting or changing host mount options.
- **Filesystem versus raw block device:** a filesystem provides names, directories, permissions, and allocation semantics. Raw-device tests bypass those filesystem semantics and can destroy data; they are prohibited in these labs.

### Tool selection table

| Tool | Question answered | Scope | Limitations / dependencies |
|---|---|---|---|
| `fio` | How does a defined read/write workload behave? | File or block target selected by the job | Can destroy data if target is wrong; results depend on engine, cache, filesystem, VM, and workload; JSON schema varies by version |
| `iostat -x` | What do visible block-device counters and queue/latency indicators show? | Linux block devices visible to the environment | Needs `sysstat`; device view may be virtualized; `%util` is not universal saturation proof |
| `iotop` | Which processes appear to be doing I/O? | Host/process view subject to kernel and permissions | May require root/capabilities; container view is not automatically host-wide |
| `pidstat` | What are process CPU, scheduling, and I/O-related statistics? | Process-level statistics supported by installed version | Requires `sysstat`; options/fields vary; does not replace storage-level measurements |
| `dd` | Can a simple sequential copy be performed? | A narrow copy workload | Poor general-purpose benchmark: often one pattern, weak workload control, cache effects, and limited latency distribution |
| `pgbench` | How does PostgreSQL transaction workload behave? | Database/client transaction path | Includes SQL, locks, CPU, connection, and network effects; not a pure storage benchmark |
| `kubectl top` | What CPU and memory usage is reported for Pods/nodes? | Kubernetes resource metrics API | Does **not** report disk IOPS, throughput, or I/O latency |
| `df`, `du` | How much filesystem space appears used? | Filesystem usage and visible file tree | Does not show backend performance or all deleted-open-file cases |
| `pidstat` + `iostat` + app metrics | Which layer may be limiting the workload? | Correlated process/device/application evidence | Requires consistent timestamps and correct visibility |

For node-level `iostat` in kind, run it on the Linux host/WSL2 environment if installed and permitted. It will show the devices visible to that environment, which may be virtual disks rather than the underlying physical device. Running `iostat` in an ordinary application container does not automatically expose host device counters. If tools are missing, install them only in the disposable lab environment or record the limitation; do not add privileged containers just to obtain a chart.

## 6.4 Level 1 — Beginner: Foundations

### 6.4.1 Storage performance is a workload experiment

There is no universal storage score. A database doing small random writes with frequent synchronization has a different profile from an ETL job writing large sequential files. A broker retaining many segments, a filesystem with many small files, and an object-store client each exercise different paths.

A benchmark needs at least:
- access pattern (random/sequential);
- request size;
- read/write mix;
- buffering/direct-I/O behavior;
- concurrency and I/O depth;
- duration and warm-up;
- target filesystem/volume/backend;
- success criteria and error handling.

### 6.4.2 Queue depth and latency

If a workload has insufficient concurrency, it may not drive a backend to its possible throughput. Increasing `iodepth` or job count can increase outstanding operations, but also increases queueing and tail latency. Some synchronous engines do not honor asynchronous queue-depth expectations in the same way as asynchronous engines. **[VERIFY: exact semantics of `iodepth`, `ioengine`, and sync behavior in the installed fio version’s HOWTO/man page.]**

Do not optimize throughput alone. For an interactive database, p99 commit latency and error rate may be more important than peak sequential bandwidth. For a batch pipeline, throughput may dominate if the job has a generous completion window. For both, durable writes and recovery behavior remain requirements.

### 6.4.3 What each measurement means

- `fio` measures completion behavior for the workload it generates at the chosen target. It does not automatically identify which underlying physical device served the data.
- `iostat -x` reports kernel-visible device statistics. `await` commonly reflects average time for I/O requests including queueing and service time as reported by that tool/kernel. `aqu-sz` is average queue length in supported versions. `%util` reports time the device was busy in the sampled interval, but on modern parallel devices, RAID, multipath, and virtualized storage it is not a universal saturation measure.
- `iotop` and `pidstat` can help identify process activity but depend on installed tools, permissions, kernel support, and namespace visibility.
- `dd` is useful for simple copying or sanity checks, not as a complete benchmark. It usually lacks controlled mixed workloads, useful latency distributions, and repeatable profile dimensions unless carefully constructed.
- `kubectl top` reports CPU and memory, not storage I/O performance.

### 6.4.4 Page-cache trap

A buffered test can appear extraordinarily fast if reads hit page cache or writes are absorbed by memory and flushed later. A comparable `direct=1` test can reduce some cache effects, but filesystem and platform support vary. Neither test by itself proves physical backend performance.

A fair comparison requires the same target, data size, access pattern, runtime, and concurrency; it also requires awareness of cache state and host activity. Do not flush host caches or use privileged cache-dropping commands. If cache state cannot be controlled safely, treat the result as a demonstration of measurement pitfalls, not as a benchmark conclusion.

## 6.5 Level 2 — Intermediate: Benchmark a PVC

### 6.5.1 Lab A overview

**Objective:** run four bounded `fio` profiles against a fresh scratch file on a dedicated PVC, collect JSON, and summarize repeated results.

**Estimated duration:** 60–120 minutes. **Approximate resources:** one small Pod (about 100–250 MiB RAM and modest CPU under load, estimate only), one 2 GiB PVC, and local result files. Actual resource use depends on the image, driver, and runtime. Check free disk first.

**Prerequisites:** disposable kind context, working StorageClass, `kubectl`, `python3`, and a fio image/version verified for your architecture. The example image tag below is not live-verified; **[VERIFY: select a pinned image/tag from a trusted source and confirm it contains `fio` and a shell.]**

### 6.5.2 PVC-backed Pod manifest

Save as `lab-a-pvc-pod.yaml`. It uses no `hostPath`. The PVC name and Pod name are fixed to make target verification explicit.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: storage-perf-scratch
  namespace: storage-perf-lab
  labels:
    app.kubernetes.io/name: storage-perf-lab
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
  # [VERIFY] Set storageClassName only after checking the selected
  # StorageClass and provisioner. Omit to use the cluster default.
---
apiVersion: v1
kind: Pod
metadata:
  name: fio-runner
  namespace: storage-perf-lab
  labels:
    app.kubernetes.io/name: storage-perf-lab
spec:
  restartPolicy: Never
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: fio
      # [VERIFY] Replace with a reviewed, pinned image/tag for your architecture.
      image: ghcr.io/axboe/fio:3.36
      command: ["sh", "-c", "sleep 36000"]
      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "1"
          memory: "512Mi"
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop: ["ALL"]
        readOnlyRootFilesystem: true
      volumeMounts:
        - name: scratch
          mountPath: /scratch
  volumes:
    - name: scratch
      persistentVolumeClaim:
        claimName: storage-perf-scratch
```

**[VERIFY]** The example assumes the selected image has a shell, `fio`, and supports UID/GID 10001. The PVC must be writable by that UID/GID. If the image or provisioner does not meet these requirements, choose a compatible image or adjust the lab-only security context after reviewing the image and volume permissions. Do not solve a permissions issue by making a host directory writable or adding a privileged container.

### 6.5.3 Create the namespace and inspect before applying

```bash
kubectl config current-context
kubectl get nodes -o wide
df -h .
free -h
kubectl get storageclass
```

Confirm the current context is your dedicated `kind-<lab-name>` context and that the disk budget is adequate.

```bash
kubectl create namespace storage-perf-lab
kubectl apply --dry-run=server -f lab-a-pvc-pod.yaml
kubectl apply -f lab-a-pvc-pod.yaml
kubectl wait --for=jsonpath='{.status.phase}'=Bound pvc/storage-perf-scratch \
  -n storage-perf-lab --timeout=120s
kubectl wait --for=condition=Ready pod/fio-runner \
  -n storage-perf-lab --timeout=180s
kubectl exec -n storage-perf-lab fio-runner -- sh -c \
  'id; command -v fio; df -h /scratch; test -w /scratch'
```

If PVC binding or Pod readiness times out, stop and inspect `kubectl describe pvc`, `kubectl describe pod`, events, StorageClass, image pulls, and volume permissions. Do not run `fio` until the target is confirmed.

### 6.5.4 Four fio job profiles

Each job targets only `/scratch/fio-scratch.bin`, bounded to 512 MiB, with a 5-second ramp-up and 30-second timed run. The PVC is 2 GiB to leave room for filesystem overhead and avoid filling the volume. Actual capacity and file allocation depend on the driver. Run profiles sequentially. The first write creates/replaces the dedicated scratch file; never point these jobs at any other path.

**DATA-SAFETY PREFACE — fio write profiles:** These jobs write to `/scratch/fio-scratch.bin` on `storage-perf-scratch` only. Verify the current context, namespace, Pod, PVC mount, and that the file is a lab-created scratch target. The profiles can overwrite that file. They must not be used against a raw device, database directory, or shared PVC.

Save each file under a local `fio-jobs/` directory, then copy it into the Pod. The examples use one job per file.

Save as `fio-jobs/01-randrw-4k-50-50.fio`:

```ini
[global]
filename=/scratch/fio-scratch.bin
size=512m
time_based=1
runtime=30
ramp_time=5
direct=1
ioengine=libaio
iodepth=8
numjobs=1
group_reporting=1
invalidate=1

[randrw-4k-50-50]
rw=randrw
bs=4k
rwmixread=50
```

This is random 4 KiB mixed read/write, with a 50/50 requested mix. It is not a pure read test. `libaio` and `direct=1` support are environment-dependent; **[VERIFY: fio HOWTO and filesystem/kernel behavior]**. If unsupported, record the error and use a documented supported engine rather than silently changing the profile.

Save as `fio-jobs/02-sequential-write-1m.fio`:

```ini
[global]
filename=/scratch/fio-scratch.bin
size=512m
time_based=1
runtime=30
ramp_time=5
direct=1
ioengine=libaio
iodepth=4
numjobs=1
group_reporting=1
invalidate=1

[seq-write-1m]
rw=write
bs=1m
```

This is sequential 1 MiB write I/O. It is useful for a large-write throughput profile, but does not represent every ETL workload. It overwrites the scratch file.

Save as `fio-jobs/03-randrw-4k-70-30.fio`:

```ini
[global]
filename=/scratch/fio-scratch.bin
size=512m
time_based=1
runtime=30
ramp_time=5
direct=1
ioengine=libaio
iodepth=16
numjobs=1
group_reporting=1
invalidate=1

[randrw-4k-70-30]
rw=randrw
bs=4k
rwmixread=70
```

This profile requests 70% reads and 30% writes for random 4 KiB I/O. It is a mixed workload, not a read-only test. Compare its IOPS, bandwidth, and latency with the 50/50 profile while noting that the requested mix is not guaranteed to be the exact completed mix under every failure or version.

Save as `fio-jobs/04-small-write-fsync.fio`:

```ini
[global]
filename=/scratch/fio-scratch.bin
size=512m
time_based=1
runtime=30
ramp_time=5
direct=1
ioengine=sync
iodepth=1
numjobs=1
group_reporting=1
invalidate=1

[small-write-fsync]
rw=write
bs=4k
fsync=1
```

This is a small-write, synchronization-heavy profile. `fsync=1` asks fio to issue a synchronization after each write, subject to fio and operating-system semantics. It approximates a durability-sensitive path but is not a faithful model of PostgreSQL WAL, transaction grouping, database commit semantics, or a physical power-loss test. `ioengine=sync` is deliberately chosen for a simple synchronous pattern; **[VERIFY: exact option semantics in the installed fio version]**.

### 6.5.5 Run each profile for N repetitions

Save as `run-fio.sh`. It runs each profile three times by default, saves one JSON file per run, records basic environment information, checks dependencies and command status, and refuses to proceed unless the current context matches the expected kind context. The script does not delete Kubernetes resources.

```bash
#!/usr/bin/env bash
set -euo pipefail

N="${N:-3}"
EXPECTED_CONTEXT="${EXPECTED_CONTEXT:-kind-storage-perf-lab}"
NAMESPACE="${NAMESPACE:-storage-perf-lab}"
POD="${POD:-fio-runner}"
OUTDIR="${OUTDIR:-results}"
REMOTE_DIR="/tmp/fio-jobs"

usage() {
  echo "Usage: EXPECTED_CONTEXT=kind-<cluster> N=3 $0 [--run]" >&2
  echo "Default is dry-run; pass --run to execute fio." >&2
}
APPLY=0
if [[ "${1:-}" == "--run" ]]; then APPLY=1; elif [[ $# -gt 0 ]]; then usage; exit 2; fi

[[ "$N" =~ ^[1-9][0-9]*$ ]] || { echo "N must be a positive integer" >&2; exit 2; }
for dep in kubectl python3; do
  command -v "$dep" >/dev/null 2>&1 || { echo "Missing dependency: $dep" >&2; exit 127; }
done
CTX="$(kubectl config current-context)"
[[ "$CTX" == "$EXPECTED_CONTEXT" ]] || {
  echo "Refusing: context '$CTX' != expected '$EXPECTED_CONTEXT'" >&2; exit 3;
}
kubectl get pod "$POD" -n "$NAMESPACE" >/dev/null
kubectl get pvc storage-perf-scratch -n "$NAMESPACE" >/dev/null
kubectl exec -n "$NAMESPACE" "$POD" -- sh -c \
  'test -w /scratch && command -v fio >/dev/null && df -h /scratch'

mkdir -p "$OUTDIR"
{
  printf 'timestamp_utc=%s\n' "$(date -u +%FT%TZ)"
  printf 'context=%s\nnamespace=%s\npod=%s\nN=%s\n' "$CTX" "$NAMESPACE" "$POD" "$N"
  kubectl version
  kubectl get nodes -o wide
  kubectl get pvc storage-perf-scratch -n "$NAMESPACE" -o wide
  df -h .
  free -h
} > "$OUTDIR/environment.txt" 2>&1

profiles=(
  "01-randrw-4k-50-50.fio"
  "02-sequential-write-1m.fio"
  "03-randrw-4k-70-30.fio"
  "04-small-write-fsync.fio"
)

if [[ "$APPLY" -ne 1 ]]; then
  echo "DRY RUN: no fio workloads executed. Review targets, then pass --run." >&2
  printf 'Would run %s profiles × %s repetitions against /scratch/fio-scratch.bin\n' "${#profiles[@]}" "$N"
  exit 0
fi

kubectl exec -n "$NAMESPACE" "$POD" -- mkdir -p "$REMOTE_DIR"
for local_job in "${profiles[@]}"; do
  [[ -f "fio-jobs/$local_job" ]] || { echo "Missing fio-jobs/$local_job" >&2; exit 4; }
  kubectl cp "fio-jobs/$local_job" "$NAMESPACE/$POD:$REMOTE_DIR/$local_job"
  for ((run=1; run<=N; run++)); do
    out="$OUTDIR/${local_job%.fio}-run${run}.json"
    echo "Running $local_job repetition $run/$N"
    if ! kubectl exec -n "$NAMESPACE" "$POD" -- fio \
      --output-format=json "$REMOTE_DIR/$local_job" > "$out"; then
      echo "fio failed; inspect $out and Pod logs/events. Stopping." >&2
      exit 5
    fi
    python3 -m json.tool "$out" >/dev/null || {
      echo "Malformed JSON: $out; stop and inspect fio version/output." >&2; exit 6;
    }
  done
done
echo "Completed all requested runs. No results are interpreted until schema validation."
```

Make it executable with `chmod +x run-fio.sh`. The default is a dry run; `--run` is an explicit action confirmation. Check the `fio-jobs/` directory and the expected context before execution. A Kubernetes context name may differ from the example; set `EXPECTED_CONTEXT` to the exact dedicated context you verified.

### 6.5.6 JSON parser and summary definitions

Fio JSON schemas and latency field names vary by version and engine. The parser below intentionally fails closed if it cannot find the expected standard fields. It does not guess alternative paths silently.

For each run:
- IOPS = sum of read and write `iops` for the job.
- Bandwidth = sum of read and write `bw_bytes` where present, in bytes/s.
- Per-run latency summary = the **maximum** of available read/write `clat_ns.percentile["95.000000"]` values. This is a conservative *worst-direction p95*, not a mathematically combined p95 across read and write operations.
- Across repetitions, report median IOPS, median bandwidth, median of the per-run worst-direction p95 latency values, and p95 of those per-run latency summaries. With only three runs, the across-run p95 is a rough summary, not a high-confidence estimate of tail behavior.

Save as `summarize-fio.py`:

```python
#!/usr/bin/env python3
import csv
import json
import math
import statistics
import sys
from pathlib import Path

P95_KEY = "95.000000"

def finite_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}: expected numeric value, got {value!r}")
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{label}: expected finite non-negative number, got {value!r}")
    return value

def read_json(path):
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: cannot read valid JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list) or not data["jobs"]:
        raise ValueError(f"{path}: missing non-empty 'jobs' array; inspect this fio version's JSON schema")
    return data

def parse_run(path):
    data = read_json(path)
    total_iops = 0.0
    total_bw = 0.0
    directional_p95 = []
    valid_directions = 0

    for job in data["jobs"]:
        if not isinstance(job, dict):
            raise ValueError(f"{path}: job entry is not an object")
        error = job.get("error", 0)
        if error not in (0, None):
            raise ValueError(f"{path}: fio job reports error={error}")
        for direction in ("read", "write"):
            stats = job.get(direction)
            if not isinstance(stats, dict):
                raise ValueError(f"{path}: missing jobs[].{direction} object; inspect schema")
            iops = finite_number(stats.get("iops"), f"{path} {direction}.iops")
            total_iops += iops
            # Fail closed: do not silently reinterpret bw units.
            bw = stats.get("bw_bytes")
            if bw is None:
                raise ValueError(
                    f"{path}: missing {direction}.bw_bytes. Inspect fio JSON; "
                    "do not assume the unit of 'bw' without validating the installed version."
                )
            total_bw += finite_number(bw, f"{path} {direction}.bw_bytes")
            if iops > 0:
                clat = stats.get("clat_ns")
                if not isinstance(clat, dict) or not isinstance(clat.get("percentile"), dict):
                    raise ValueError(f"{path}: missing {direction}.clat_ns.percentile")
                if P95_KEY not in clat["percentile"]:
                    raise ValueError(
                        f"{path}: missing percentile key {P95_KEY}; inspect fio JSON keys"
                    )
                directional_p95.append(
                    finite_number(clat["percentile"][P95_KEY], f"{path} {direction} p95")
                )
                valid_directions += 1

    if valid_directions == 0:
        raise ValueError(f"{path}: no successful read/write direction with latency data")
    return total_iops, total_bw, max(directional_p95)

def percentile_nearest_rank(values, p):
    if not values:
        raise ValueError("cannot calculate percentile of empty values")
    ordered = sorted(values)
    rank = max(1, math.ceil(p * len(ordered)))
    return ordered[rank - 1]

def main(paths):
    if not paths:
        raise SystemExit("Usage: python3 summarize-fio.py results/*.json")
    records = []
    for path_text in paths:
        path = Path(path_text)
        iops, bw, p95_ns = parse_run(path)
        records.append({
            "file": path.name,
            "profile": path.name.rsplit("-run", 1)[0],
            "iops": iops,
            "bandwidth_bytes_per_sec": bw,
            "worst_direction_clat_p95_ns": p95_ns,
        })

    out_csv = Path("results/fio-run-summaries.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    print("profile,runs,median_iops,median_bandwidth_bytes_per_sec,"
          "median_run_worst_direction_p95_ns,p95_across_run_latency_summaries_ns")
    profiles = sorted({r["profile"] for r in records})
    for profile in profiles:
        group = [r for r in records if r["profile"] == profile]
        if len(group) < 1:
            raise ValueError(f"{profile}: no successful runs")
        iops = [r["iops"] for r in group]
        bw = [r["bandwidth_bytes_per_sec"] for r in group]
        lat = [r["worst_direction_clat_p95_ns"] for r in group]
        print(f"{profile},{len(group)},{statistics.median(iops):.3f},"
              f"{statistics.median(bw):.3f},{statistics.median(lat):.3f},"
              f"{percentile_nearest_rank(lat, 0.95):.3f}")

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
```

Run only after successful fio jobs:

```bash
python3 summarize-fio.py results/*.json > results/fio-summary.csv
```

The parser writes per-run summaries to `results/fio-run-summaries.csv` and prints the profile-level summary. The command redirects that summary to a file. If the installed fio version lacks the expected fields, the parser exits with an error. Inspect a redacted sample JSON and the official fio documentation, then deliberately update the parser; do not make it accept unknown schemas silently.

### 6.5.7 Results template and illustrative interpretation

Save as `results-template.csv`:

```csv
profile,block_size,read_write_mix,direct_or_buffered,ioengine,iodepth,repetitions,median_iops,median_bandwidth_bytes_per_sec,median_run_worst_direction_p95_ns,p95_across_run_latency_summaries_ns,environment,caveats
```

Use a Markdown results table with the same columns. Include the PVC/StorageClass, Kubernetes and kind versions, node image, fio version, container runtime, host OS/WSL2, free disk, run time, ramp time, and whether the results were run on a warm or uncertain cache state.

**[ILLUSTRATIVE — not measured] Average versus tail latency example:**

| Workload | Mean latency | p50 | p95 | p99 | Interpretation |
|---|---:|---:|---:|---:|---|
| A | 2 ms | 1 ms | 4 ms | 8 ms | Most operations are quick, but some requests take materially longer |
| B | 2 ms | 1 ms | 5 ms | 80 ms | Same mean, but rare long stalls may breach a latency objective |

These values are fabricated for explanation and are not expected results for the lab. A percentile needs a defined measurement point, workload, duration, and enough samples. A p99 estimated from a tiny number of operations is unstable. Fio’s per-run p95 is not interchangeable with a p95 computed from three run-level summaries.

### 6.5.8 Node-level iostat and page-cache comparison

If `sysstat` is installed on the Linux host/WSL2 environment, run `iostat -x 1 10` while the bounded fio job runs. Save the timestamped output and identify which virtual/block devices correspond to the environment. Do not assume a device name or that its counters represent the physical storage backing the virtual disk.

Interpret:
- `r/s`, `w/s`: reads/writes per second;
- `rkB/s`, `wkB/s` or version-specific byte-rate columns: read/write throughput;
- `await`: average completion time including queueing as reported by the tool;
- `aqu-sz`: average queue depth where provided;
- `%util`: busy time during the interval, not a universal saturation metric for parallel or virtualized devices.

**Lab B — page-cache comparison.** Use the same bounded file and comparable workload, first with buffered I/O (`direct=0`) and then with `direct=1`, only if supported. Use separate job files and clearly label them. Do not run cache-flushing commands. Record fio version, filesystem, target, size, runtime, concurrency, cache caveats, and observed differences. Do not promise that buffered will always be faster or that direct I/O will always be slower. A fair comparison may be impossible because cache state and host activity cannot be controlled safely; in that case the exercise demonstrates why benchmark claims need caveats, not which mode is faster.

### 6.5.9 Troubleshooting

- **`fio` missing:** verify the image and `command -v fio`; use a reviewed image/tag and record its digest/version.
- **Permission denied:** verify PVC mount, UID/GID, and image user. Do not add privileged mode or hostPath.
- **PVC Pending:** inspect PVC events, StorageClass, provisioner, and node scheduling.
- **Pod fails to pull image:** verify registry reachability, image architecture, tag, and policy.
- **`O_DIRECT` or engine unsupported:** consult the installed fio version and filesystem/kernel documentation; mark the changed profile and do not compare it as if identical.
- **Malformed or incompatible JSON:** preserve the output, inspect the schema, and update the parser deliberately.
- **Job exceeds time or memory:** stop the lab safely, reduce repetitions or duration, and check node pressure; do not increase resource limits without understanding the host budget.
- **Results vary widely:** look for noisy neighbors, cache effects, background backup activity, thermal/power effects, resource throttling, and inconsistent test configuration.

## 6.6 Level 3 — Advanced: Methodology and System Interactions

### 6.6.1 Design a representative benchmark

Start with application evidence: database query/commit behavior, ETL file sizes, read/write mix, concurrency, synchronization pattern, and user-visible latency. Define success criteria before testing. Example criteria should be workload-specific and explicitly illustrative; do not adopt a generic IOPS target.

A rigorous sequence:
1. Define the question and the measurement layer.
2. Choose a workload profile based on observed application behavior.
3. Record versions, filesystem, PVC/StorageClass, resource limits, cache mode, and node/runtime.
4. Warm up for a defined interval, then measure at steady state.
5. Repeat at least N times (three is a learning default, not a statistical guarantee).
6. Report median and tail percentiles; show variation rather than hiding it.
7. Keep file size, duration, and disk use bounded.
8. Control noisy neighbors and run comparisons under equivalent conditions.
9. Change one factor at a time where possible.
10. Preserve raw JSON and environment metadata.

Do not compare raw numbers across unlike environments as if they were portable specifications. Relative regression within a consistent environment is usually more defensible than claiming that a WSL2 result predicts a cloud volume.

### 6.6.2 Tail percentiles and sample size

The average can hide a small fraction of slow operations. p50 represents the midpoint; p95 and p99 describe the slow tail. The number of samples matters: if a test generates too few completions, p99 may be driven by very few observations and will be unstable. Repeated runs help reveal run-to-run variation but do not replace a sufficiently large operation sample or a clearly defined time window.

Report at least the measurement point, workload, total operations/sample count if available, run duration, percentile calculation, and number of repetitions. Fio JSON fields may differ by version. **[VERIFY: exact latency fields and percentile keys in the installed fio output and official documentation.]**

### 6.6.3 Storage throttling and burst behavior

Some storage systems impose throughput or IOPS limits at the volume, instance, account, or aggregate level. Some products have burst behavior or credits; others have sustained performance tiers. A workload may run quickly initially and slow after a burst window, or an instance-level limit may constrain multiple volumes together.

Do not quote current provider limits, prices, or credit rules without verifying the exact product, tier, region, and date in official provider documentation. Collect provider metrics for throttling/credits, volume latency, queueing, throughput, and instance limits. Compare the timestamps with application p99 and workload activity. In kind, you cannot infer a cloud provider’s throttling behavior.

### 6.6.4 Storage type comparison

| Storage type | Latency/access profile | Sharing and semantics | Durability/failure domain | Common workloads and trade-offs |
|---|---|---|---|---|
| Local NVMe | Often low latency and high IOPS/throughput for local workloads; exact result depends on device and queue | Usually node-local block/device semantics | May be tied to one host; failure can remove local data unless replicated elsewhere | Cache, scratch, high-performance local processing; requires explicit data recovery/replication design |
| Network block storage | Block-device semantics presented over a network; latency includes network/backend path | Commonly attached/mounted according to driver and access-mode constraints | Provider/backend-specific durability and zone behavior **[VERIFY]** | Databases and persistent workloads where managed block semantics fit; may have caps or burst rules |
| Network file storage | Shared filesystem semantics over a network; metadata operations and small files can behave differently from large sequential I/O | Designed for shared file access according to service semantics | Service/provider-specific | Shared datasets, home directories, some data workloads; metadata latency and concurrency matter |
| Object storage | Object/API operations rather than a normal POSIX block device; often different latency and consistency/access semantics | Shared through API; not a drop-in mounted block volume | Service-specific durability and failure domain | Backups, data lake objects, archives; not a substitute for a low-latency database block volume |

Provider-specific performance, durability, availability, pricing, and limits must be verified. “Network” or “local” alone does not establish a guaranteed latency or durability level.

### 6.6.5 StorageClass performance tiers and parameters

Kubernetes defines StorageClass as a way to describe provisioner and parameters, but the meaning of performance-related parameters is backend-specific. A `parameters` field is not a portable promise of IOPS or latency. The CSI driver and storage service determine which parameters are valid and what they mean.

Conceptual example only:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: conceptual-performance-tier
provisioner: example.csi.invalid
parameters:
  # CONCEPTUAL ONLY — not a real driver configuration.
  performance-tier: "<driver-specific-value>"
```

Do not apply this example. Replace the placeholder only using the chosen CSI driver’s official documentation and a supported provisioner. **[VERIFY: exact driver name, parameter keys/values, topology, expansion support, mount options, and performance guarantees.]**

### 6.6.6 PostgreSQL interactions

PostgreSQL performance depends on more than disk bandwidth:

- **WAL placement and synchronization:** commit latency may be sensitive to WAL write/flush behavior. Separating WAL and data volumes can isolate workloads in some architectures, but it is not automatically faster and adds operational complexity.
- **`fsync`:** supports crash-safety by requesting synchronization. Disabling it can risk corruption after OS or hardware failure. Do not use it as a generic tuning knob.
- **`synchronous_commit`:** controls when a transaction is acknowledged relative to WAL flush/replication settings. Different settings alter durability/latency guarantees; exact semantics depend on configuration and PostgreSQL version. **[VERIFY: official PostgreSQL documentation for the deployed major version.]**
- **Checkpoints:** write dirty buffers and can create bursts of I/O. Checkpoint frequency, checkpoint completion targets, WAL volume, and workload shape can affect latency and write amplification.
- **Autovacuum:** performs maintenance I/O; suppressing it blindly can cause table bloat and future performance problems.
- **Query and lock behavior:** slow queries, poor plans, lock contention, or excessive connections can dominate latency even when storage is healthy.
- **Shared memory and cgroups:** memory pressure, OOM kills, CPU throttling, and reclaim can interact with database behavior. They must not be mislabeled as disk latency. **[VERIFY: kernel/cgroup and PostgreSQL version/platform behavior.]**

Use `pgbench` as a complementary application-level benchmark when a disposable PostgreSQL instance is available. It measures transaction behavior through the database path, not a pure storage layer. Do not run it against a production database.

### 6.6.7 CPU throttling versus I/O wait

CPU throttling occurs when a cgroup hits its CPU quota; I/O wait is a CPU accounting state associated with waiting for I/O, and storage latency is measured at a different layer. These signals can coexist, but none proves another. Compare Pod CPU usage/throttling metrics, process statistics, database waits, fio/iostat evidence, and application latency on aligned timelines. Cross-reference Stage 2E M03 Unit 2 for CPU/resource troubleshooting.

### 6.6.8 Noisy neighbors, cgroup v2, and ephemeral storage

On Linux cgroup v2, `io.max` is a control concept for limiting I/O bandwidth/IOPS for a cgroup on supported devices. Kubernetes does not provide a universally portable native per-Pod disk IOPS limiter across all CSI drivers, runtimes, and kernels. **[VERIFY: kernel cgroup v2 support, device mapping, runtime integration, and whether the platform exposes a supported control.]** Do not manually change host cgroups in this lab.

- **Disk-backed `emptyDir`:** uses node ephemeral storage and may share pressure with container writable layers and logs. Capacity and eviction depend on kubelet accounting and node configuration.
- **Memory-backed `emptyDir`:** typically uses memory-backed tmpfs semantics; it consumes memory and can contribute to memory pressure. It is not “free scratch space.”
- **Ephemeral-storage requests/limits:** participate in scheduling/accounting and can influence eviction behavior where supported. They do not automatically reserve persistent storage performance.
- **DiskPressure:** node pressure can trigger eviction and affect unrelated workloads. A full node filesystem is not an acceptable benchmark technique.

For ETL, large sequential writes can benefit from larger I/O units and well-sized output files, while many tiny files can increase metadata overhead. Parquet row-group sizing changes the balance between scan efficiency, parallelism, and read amplification. Shuffle spill can turn memory pressure into heavy temporary I/O. These are Stage 2C data-layout topics; this unit teaches how to measure their storage consequences, not a full Parquet tutorial.

## 6.7 Level 4 — Expert: SLOs, Capacity, and Incidents

### 6.7.1 Performance SLOs

A storage SLO must define the workload, measurement point, time window, and user-visible consequence. Possible indicators include:
- p99 database commit/write latency under a defined transaction mix;
- restore throughput and total restore time for a known data volume;
- attach/mount time where it affects recovery;
- I/O error rate and timeout rate;
- available capacity and estimated time to full;
- backup/WAL freshness and restore-test success.

A metric without a workload and window is not an SLO. Calibrate thresholds using production-like evidence and service objectives. See M11 for observability and SLO implementation and M15 for capacity/cost policy.

### 6.7.2 Capacity projection from measured growth

A simple linear model estimates days until a threshold using timestamped capacity measurements. It is useful for an initial runway estimate when growth is approximately stable; it is not a forecast guarantee. It fails when data growth is seasonal, workload-driven, stepwise, compressed differently, or constrained by retention and cleanup.

Save as `capacity.csv`:

```csv
timestamp,used_gib,capacity_gib
2026-10-01T00:00:00Z,40,100
2026-10-08T00:00:00Z,43,100
2026-10-15T00:00:00Z,46,100
2026-10-22T00:00:00Z,49,100
```

All rows above are **[ILLUSTRATIVE]**, not measured. `GiB` means gibibytes (binary units). The threshold in the script is 80% of capacity by default, a teaching example only; teams must calibrate it to response time, workload volatility, expansion lead time, and recovery needs.

Save as `capacity_projection.py`:

```python
#!/usr/bin/env python3
import argparse
import csv
import math
from datetime import datetime
from pathlib import Path

def parse_time(value):
    # Require an explicit timezone; normalize to UTC.
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"timestamp must include timezone: {value!r}")
    return dt.timestamp()

def load_points(path):
    points = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp", "used_gib", "capacity_gib"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"CSV must contain columns {sorted(required)}")
        for row_number, row in enumerate(reader, start=2):
            try:
                t = parse_time(row["timestamp"])
                used = float(row["used_gib"])
                capacity = float(row["capacity_gib"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid row {row_number}: {exc}") from exc
            if not all(math.isfinite(x) for x in (t, used, capacity)):
                raise ValueError(f"row {row_number}: values must be finite")
            if capacity <= 0 or used < 0 or used > capacity:
                raise ValueError(f"row {row_number}: require 0 <= used <= capacity and capacity > 0")
            points.append((t, used, capacity))
    if len(points) < 2:
        raise ValueError("need at least two valid measurements")
    points.sort()
    if len({t for t, _, _ in points}) != len(points):
        raise ValueError("timestamps must be unique")
    if len({cap for _, _, cap in points}) != 1:
        raise ValueError("this simple model requires constant capacity; model expansion separately")
    return points

def linear_slope(points):
    # Least-squares slope in GiB per day.
    xs = [(t - points[0][0]) / 86400.0 for t, _, _ in points]
    ys = [used for _, used, _ in points]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    if denom <= 0:
        raise ValueError("timestamps have no usable spread")
    return sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denom

def estimate(points, threshold_fraction):
    capacity = points[0][2]
    latest_used = points[-1][1]
    threshold = capacity * threshold_fraction
    growth = linear_slope(points)
    if latest_used >= threshold:
        return growth, threshold, 0.0
    if growth <= 0:
        return growth, threshold, None
    return growth, threshold, (threshold - latest_used) / growth

def main():
    parser = argparse.ArgumentParser(description="Estimate days until a capacity threshold.")
    parser.add_argument("csv_path")
    parser.add_argument("--threshold-fraction", type=float, default=0.80)
    args = parser.parse_args()
    if not (0 < args.threshold_fraction <= 1):
        raise SystemExit("--threshold-fraction must be > 0 and <= 1")
    points = load_points(args.csv_path)
    growth, threshold, days = estimate(points, args.threshold_fraction)
    print(f"measurements={len(points)}")
    print(f"capacity_gib={points[0][2]:.2f}")
    print(f"latest_used_gib={points[-1][1]:.2f}")
    print(f"threshold_gib={threshold:.2f}")
    print(f"estimated_growth_gib_per_day={growth:.4f}")
    if days is None:
        print("days_until_threshold=not_estimated (growth is zero or negative)")
    else:
        print(f"days_until_threshold={days:.2f}")
    print("LIMITATION: linear extrapolation assumes the measured trend continues.")

if __name__ == "__main__":
    main()
```

Run:
```bash
python3 capacity_projection.py capacity.csv --threshold-fraction 0.80
```

For the illustrative rows, the slope is approximately `3/7 ≈ 0.4286 GiB/day`; at the last sample, usage is 49 GiB and the illustrative threshold is 80 GiB, so the estimate is `(80 − 49) / 0.4286 ≈ 72.3 days`. This is a calculation over fabricated sample data, not an operational forecast.

Self-checks:
- At least two unique, timezone-aware timestamps are required.
- Invalid, missing, non-finite, or out-of-range capacity values fail.
- Non-positive growth does not produce a misleading finite runway estimate.
- The model assumes constant capacity; record volume expansion as a separate event rather than blending measurements across capacity changes.

### 6.7.3 CI regression guard using relative changes

A benchmark regression guard is useful only when the test environment and profile are consistent. It can catch configuration mistakes or large regressions in ephemeral kind; it is not a production capacity gate.

Save as `compare-benchmarks.py`:

```python
#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

KEY = "profile"
METRICS = ("median_iops", "median_bandwidth_bytes_per_sec")
# Example tolerances are illustrative; calibrate to run-to-run noise.
MAX_REGRESSION_FRACTION = 0.20

def load(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {KEY, *METRICS}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path}: required columns are {sorted(required)}")
        rows = {}
        for row in reader:
            profile = row[KEY]
            if not profile or profile in rows:
                raise ValueError(f"{path}: missing or duplicate profile {profile!r}")
            values = {}
            for metric in METRICS:
                value = float(row[metric])
                if value < 0:
                    raise ValueError(f"{path}: negative {metric}")
                values[metric] = value
            rows[profile] = values
        return rows

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: compare-benchmarks.py baseline.csv current.csv")
    base, current = load(sys.argv[1]), load(sys.argv[2])
    if base.keys() != current.keys():
        raise SystemExit("FAIL: baseline/current profile sets differ")
    failed = False
    for profile in sorted(base):
        for metric in METRICS:
            b, c = base[profile][metric], current[profile][metric]
            if b <= 0:
                print(f"OPEN {profile} {metric}: baseline is zero; no relative comparison")
                failed = True
                continue
            delta = (c - b) / b
            print(f"{profile} {metric}: baseline={b:.3f} current={c:.3f} "
                  f"relative_change={delta:+.1%}")
            # Lower IOPS/bandwidth is treated as regression in this simple example.
            if delta < -MAX_REGRESSION_FRACTION:
                failed = True
    if failed:
        print("FAIL/OPEN: inspect noise and environment before attributing cause.")
        raise SystemExit(1)
    print("PASS: no configured throughput/IOPS regression crossed the example threshold.")

if __name__ == "__main__":
    main()
```

The 20% threshold is **[ILLUSTRATIVE]**, not a universal recommendation. The example checks IOPS and bandwidth only; a real guard should include the relevant latency SLO, repeated-run variation, error counts, and environment drift. Do not compare runs with different fio versions, node images, PVC backends, cache settings, or profiles and then call the difference a storage regression.

### 6.7.4 “What these laptop numbers do NOT tell you”

| Question | What kind can establish | What it cannot establish |
|---|---|---|
| Production IOPS/latency | The behavior of a specific bounded workload in this local stack | A cloud volume’s production capacity or SLO |
| Backend durability | Whether the lab file remained available through the tested operation | Power-loss durability or provider backend correctness |
| Real zone behavior | Kubernetes object behavior in the local cluster | Independent physical zones, network partitions, or provider failover |
| Cloud throttling thresholds | Nothing about a provider unless separately tested/documented | Current provider caps, burst-credit rules, prices, or tier limits |
| Multi-tenant contention | Variation under observed local activity | Production noisy-neighbor patterns or isolation guarantees |
| Recovery time | Time for this specific lab procedure in this environment | Production restore/attach/failover time at a different data scale |
| Provider cost | Local resource consumption estimates | Provider pricing or total cost of ownership |
| Database durability | Behavior of a particular test pattern | End-to-end database transaction durability under all failures |

### 6.7.5 Database-is-slow decision tree

```text
User-visible latency elevated?
  |
  +--> Application: queueing, retries, connection pool, timeouts?
  |
  +--> Database: query plan, locks, waits, connection saturation?
  |       |
  |       +--> WAL/fsync/commit wait or checkpoint/autovacuum activity?
  |
  +--> Container/node: CPU throttling, memory pressure, OOM, eviction?
  |
  +--> PVC/filesystem: capacity, errors, mount state, workload contention?
  |
  +--> Node/block layer: iostat queue/await and correlated I/O rates?
  |
  +--> Backend/provider: throttling, volume/instance caps, service incidents?
```

Do not jump directly from “database slow” to “disk slow.” Collect aligned timestamps and evidence at each layer. A query-plan regression, lock contention, CPU throttling, network latency, or pool exhaustion can mimic storage latency.

### 6.7.6 Incident runbook table

| Symptom | Evidence to collect | Likely causes | Safe mitigation | Validation and prevention |
|---|---|---|---|---|
| p99 spikes during backup/snapshot | App p99, database waits, backup timeline, PVC and node I/O counters, backup logs | Competing reads/writes, flush bursts, CPU/network contention | Confirm correlation; if policy permits, reschedule or throttle the backup using supported controls; do not disable durability | Verify p99 and error rate recover; add maintenance coordination, capacity and contention monitoring |
| Performance drops after sustained load | Provider metrics, throttling/credit indicators, volume and instance limits, queue/latency | Burst exhaustion, tier cap, aggregate instance cap | Confirm exact product behavior; reduce load or use a supported tier/capacity change with approval | Compare post-change metrics; alert on documented provider signals; validate cost and performance |
| Volume reaches 100% | `df`, PVC status/events, DB/operator logs, deleted-open files, WAL/archive freshness, growth rate | Retention, failed archive, runaway output, logs, temporary spill | Preserve data; identify verified reclaimable disposable files; expand only if StorageClass/CSI/filesystem support is confirmed | Confirm free space, DB health, WAL freshness, backup/restore path; alert on runway and archive failures |
| Database slow but disk not proven | Query plans, locks/waits, CPU throttling, memory, pool, network, iostat/fio under controlled test | Bad query, lock contention, CPU quota, connection saturation, cache effects | Mitigate the demonstrated bottleneck; avoid speculative storage changes | Re-test with same workload and timestamps; keep the causal evidence and prevention action |

### 6.7.7 Safe expansion/cleanup decision flow

1. **Stabilize and preserve evidence.** Capture `df`, PVC/PV status, events, database/operator logs, and current workload. Identify whether the problem is a full PVC, full node filesystem, object-store capacity, or another resource.
2. **Verify data safety.** Confirm a recent usable backup and restore evidence where feasible. Do not assume that a green backup job proves recovery.
3. **Identify reclaimable data.** Confirm ownership and purpose before removing temporary output, old test files, or logs. Never delete database files or WAL as generic cleanup.
4. **Check expansion support.** Verify the StorageClass allows expansion, the CSI driver supports it, the backend permits it, and filesystem expansion is supported for the actual volume/filesystem. **[VERIFY]** all four layers. Do not assume kind’s default local-path provisioner supports PVC expansion.
5. **Choose a supported mitigation.** Remove only confirmed disposable data or perform a documented PVC expansion. Any destructive cleanup must use a data-safety preface and explicit confirmation.
6. **Validate after change.** Check capacity, PVC/PV conditions, filesystem size, database health, WAL/archive freshness, write/read behavior, and application error rate.
7. **Prevent recurrence.** Add growth/runway and archive-freshness alerts, adjust retention, and plan capacity with measured growth.

### 6.7.8 Bounded disk-full lab alternative

A realistic PVC exhaustion test can be unsafe or unreliable on kind because the PVC may be backed by a host path within the same virtual disk. Prefer a bounded scratch-file simulation. Do not attempt to fill the node or host filesystem.

**DATA-SAFETY PREFACE — disk-full simulation:** This exercise writes only a small synthetic file inside the disposable `storage-perf-lab` PVC and stops below a defined cap. It can still consume host disk and destabilize a node if misconfigured. Confirm the exact context, namespace, Pod, PVC, mount path, and available host disk. Never run against a database directory or shared volume.

A safer file-backed simulation is to write a bounded file of at most 256 MiB into the scratch PVC, while keeping the PVC at 2 GiB and monitoring `df -h /scratch`. This demonstrates space accounting and cleanup, but **does not prove a real filesystem/PVC will produce the same errors at 100% full**. Do not exceed the defined cap to force an error.

```bash
kubectl config current-context
kubectl get pod fio-runner -n storage-perf-lab -o wide
kubectl get pvc storage-perf-scratch -n storage-perf-lab -o wide
kubectl exec -n storage-perf-lab fio-runner -- df -h /scratch
# DATA-SAFETY PREFACE above must be satisfied before this bounded write:
kubectl exec -n storage-perf-lab fio-runner -- sh -c \
  'umask 077; dd if=/dev/zero of=/scratch/disk-full-simulation.bin bs=1M count=128 status=progress; sync; df -h /scratch'
```

The file is bounded at 128 MiB in this example. It may not create a disk-full error; that is intentional. Record before/after usage, operation status, and any observed application or filesystem error. Do not increase the count to consume all free space.

**DATA-SAFETY PREFACE — scratch cleanup:** The next command removes only the specifically named synthetic file inside the verified lab PVC. Check the context and file path first; if the path differs, stop.

```bash
kubectl config current-context
kubectl exec -n storage-perf-lab fio-runner -- ls -lh /scratch/disk-full-simulation.bin
# Execute only after verifying the exact lab file:
kubectl exec -n storage-perf-lab fio-runner -- rm -- /scratch/disk-full-simulation.bin
kubectl exec -n storage-perf-lab fio-runner -- df -h /scratch
```

If the selected driver demonstrably supports PVC expansion, a separate expansion exercise may be performed only using its official procedure. Otherwise document the expansion decision path; do not apply a speculative StorageClass or PVC patch.

## 6.8 SRE Lens: Measurement, Alerting, and Incident Response

### Define service objectives before thresholds

A storage signal becomes operationally useful when connected to a user-visible objective. For a database, an example objective could be p99 commit latency below a workload-specific limit during a defined peak window, with an error-rate and data-integrity guard. For recovery, measure restore throughput and total time at a known data volume. For capacity, alert on estimated runway based on measured growth and the time required to respond.

Example threshold policies are not portable defaults. Calibrate them using workload volatility, expansion lead time, recovery needs, and observed noise. Link implementation to M11 (observability/SLOs) and M15 (cost/capacity).

### Incident discipline

1. Establish impact and scope: which application, namespace, PVC, database, and time window?
2. Preserve a baseline: recent normal latency, workload mix, versions, and capacity.
3. Align timestamps from application, database, Kubernetes, node, and backend metrics.
4. Form competing hypotheses rather than assuming disk is responsible.
5. Prefer read-only inspection and bounded experiments.
6. Mitigate only the evidenced cause, with an explicit rollback/abort plan.
7. Verify user-visible latency and data integrity after mitigation.
8. Record the causal evidence, uncertainty, and prevention action.

### Snapshot/backup contention incident

If p99 rises when a backup starts, compare the backup timeline with database commit latency, WAL/fsync waits, device counters, PVC throughput, and CPU/network use. A temporal correlation is evidence but not proof. If the correlation is repeated and the backup is the likely cause, use supported scheduling/concurrency controls and re-test. Do not disable `fsync` or change durability settings to mask the symptom.

### Throttling incident

Inspect the exact backend’s official metrics and limits for the provisioned tier and region. Check both per-volume and per-instance caps, burst/credit signals if applicable, and whether other volumes share the same aggregate limit. Mitigation might include workload smoothing or a supported tier change; any cost or performance claim must be verified for that exact product. kind cannot reproduce cloud burst credits.

### Full-volume incident

Determine whether the full resource is the database PVC, node ephemeral storage, container writable layer, or object store. Check `df`, `du` where appropriate, PVC conditions, database/operator logs, WAL archive freshness, and open-but-deleted files using approved tools. Do not delete WAL/database files. Confirm recovery readiness before removing anything. Expansion is a supported path only when the StorageClass, CSI driver, backend, and filesystem all support it.

### CPU/query incident masquerading as storage

Compare CPU throttling, process statistics, query plans, locks/waits, connection pool saturation, and aligned I/O evidence. A low CPU usage reading can be caused by waiting, but it does not prove storage is the wait source. A high `iowait` signal is also not enough to identify which application or storage layer is responsible. Use corroborating evidence.

## 6.9 Security and Data-Safety Lens

- **Least privilege:** run fio as non-root when the image and volume permissions allow. Do not add privileged mode, hostPath, or broad capabilities to obtain benchmark access.
- **Target safety:** validate the exact scratch path before every write-heavy run. Never use `/dev/*`, a database data directory, or a shared PVC.
- **Data confidentiality:** benchmark files can contain workload data if a learner accidentally uses a non-synthetic source. Use only generated data and secure result artifacts.
- **Resource exhaustion:** bound file size, runtime, job count, and repetitions. Check host disk and memory before each run. Do not fill the node to simulate a full volume.
- **Cleanup controls:** inspect context and resources before deletion. Use explicit `--apply` for destructive scripts and never delete a namespace/PVC automatically from the benchmark runner.
- **Durability:** never treat disabling `fsync` or deleting WAL as a routine performance or capacity fix.
- **Supply chain:** verify image source, tag, architecture, and digest where practical. A tag alone may be mutable; record the selected image identity.
- **Host visibility:** do not grant host-level privileges simply to run `iostat` or `iotop`. Use host tools when available, or record that visibility is unavailable.
- **NetworkPolicy:** M04 policies are not an I/O performance control, although network storage can introduce network dependencies.
- **Backups/snapshots:** handle benchmark snapshots and outputs as potentially sensitive; follow M05 Unit 3 and M13 backup/DR controls.

## 6.10 Production Checklist

### Workload and measurement design

- [ ] Define the application question, workload, measurement layer, duration, and success criteria.
- [ ] Record block size, read/write mix, access pattern, `direct`, engine, queue depth, jobs, runtime, ramp time, and file size.
- [ ] Include latency distribution, errors, IOPS, and throughput; do not rely only on an average.
- [ ] Repeat runs and report variability; preserve raw results and environment metadata.
- [ ] Keep comparisons within equivalent environments and configuration.

### Storage and platform

- [ ] Identify the actual PVC, PV, StorageClass, CSI driver, filesystem, node, and backend.
- [ ] Verify backend-specific performance parameters and expansion capabilities in official docs.
- [ ] Monitor capacity, growth, node ephemeral storage, and `DiskPressure`.
- [ ] Distinguish local, block, file, and object storage semantics.
- [ ] Verify any provider-specific limits, burst behavior, prices, and tier claims.

### Database and pipeline

- [ ] Correlate application p99 with database waits, WAL/fsync, checkpoints, autovacuum, CPU throttling, and I/O evidence.
- [ ] Keep durability settings explicit and reviewed.
- [ ] Test ETL file size, small-file count, row-group layout, and shuffle spill using representative data.
- [ ] Avoid running `pgbench` against production or mixing unrelated heavy labs.

### Incident readiness

- [ ] Define capacity headroom and alert thresholds from growth and response time.
- [ ] Alert on storage errors, latency, archive freshness where relevant, and time-to-full.
- [ ] Document safe cleanup and verified PVC expansion paths.
- [ ] Have a tested backup/restore plan before destructive recovery operations.
- [ ] Define abort criteria for disk-full, benchmark, and incident exercises.
- [ ] Link dashboards and SLOs to M11 and capacity/cost decisions to M15.

## 6.11 Hands-on Labs

### Lab A — Four-profile fio harness

**Objective:** generate four controlled profiles, collect JSON over three repetitions, and produce a result table.

**Prerequisites and footprint:** dedicated kind cluster/context, `kubectl`, Python 3, fio image verified for your architecture, a working StorageClass, and adequate disk. Estimate one Pod with 128 MiB requested/512 MiB limited memory, up to one CPU, a 2 GiB PVC, and local JSON files. These are estimates; verify actual use.

**Procedure:** follow Sections 6.5.2–6.5.6 in order. Save the manifest as `lab-a-pvc-pod.yaml`, job files in `fio-jobs/`, runner as `run-fio.sh`, and parser as `summarize-fio.py`. Run `kubectl apply --dry-run=server` before apply. Verify `fio`, writable `/scratch`, PVC binding, and the expected context before execution. Run the runner first in dry-run mode, inspect the plan, then use `--run` only after confirming the target.

```bash
mkdir -p fio-jobs results
chmod +x run-fio.sh
EXPECTED_CONTEXT=kind-storage-perf-lab ./run-fio.sh
# Review printed context and target. Execute only after the DATA-SAFETY PREFACE:
EXPECTED_CONTEXT=kind-storage-perf-lab ./run-fio.sh --run
python3 summarize-fio.py results/*.json > results/fio-summary.csv
```

**Expected evidence (illustrative; not executed here):** four profile families × three JSON files, `environment.txt`, `fio-run-summaries.csv`, and `fio-summary.csv`. Actual measurements are unknown until you run the lab.

**Troubleshooting:** if `fio` fails, inspect the exact JSON/stdout and Pod events. If the parser rejects the schema, stop and inspect the installed fio documentation/output rather than assuming field names. If PVC provisioning or image pulling fails, fix that dependency before measuring.

**What this lab proves:** the learner can run bounded profiles, collect evidence, detect schema mismatches, and compare repeated results.

**What it does not prove:** production capacity, physical-device performance, provider guarantees, or power-loss durability.

**Cleanup — ⚠ DESTRUCTIVE — DATA LOSS:** the following can delete the synthetic benchmark file and lab PVC data. Read-only checks first; execute only with explicit `--apply`. This script intentionally refuses to delete resources outside the expected context and namespace.

Save as `cleanup-lab.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
EXPECTED_CONTEXT="${EXPECTED_CONTEXT:-kind-storage-perf-lab}"
NAMESPACE="${NAMESPACE:-storage-perf-lab}"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1
CTX="$(kubectl config current-context)"
echo "Current context: $CTX"
kubectl get all,pvc -n "$NAMESPACE" -o wide
[[ "$CTX" == "$EXPECTED_CONTEXT" ]] || { echo "Refusing: context mismatch" >&2; exit 3; }
if [[ "$APPLY" -ne 1 ]]; then
  echo "DRY RUN only. Review the exact resources; pass --apply to delete namespace $NAMESPACE."
  exit 0
fi
[[ "$NAMESPACE" == "storage-perf-lab" ]] || { echo "Refusing unexpected namespace" >&2; exit 4; }
kubectl delete namespace storage-perf-lab --wait=true --timeout=120s
kubectl get namespace storage-perf-lab >/dev/null 2>&1 && {
  echo "Namespace still exists; investigate before retrying." >&2; exit 5;
} || true
kubectl get pvc -A | grep -F storage-perf-scratch && {
  echo "PVC name still exists elsewhere; investigate; do not delete blindly." >&2; exit 6;
} || true
echo "Namespace deletion requested; inspect PV/reclaim behavior and backend artifacts manually."
```

Before cleanup, preserve results outside the namespace. Verify whether any PV or backend asset remains; do not automatically delete cluster-scoped resources or remove finalizers.

### Lab B — Page-cache comparison

**Objective:** compare otherwise similar bounded buffered and direct-I/O tests while learning why cache state biases results.

**Estimated duration:** 30–45 minutes. **Footprint:** same Pod/PVC as Lab A and two short runs. No additional cluster services.

**Procedure:**
1. Confirm context, Pod, PVC, and scratch path.
2. Copy a buffered job file using the same size, block size, mix, engine where supported, and duration as one direct-I/O profile, but set `direct=0`.
3. Run the buffered job and direct-I/O job separately against the same lab scratch file. Both may modify the file; this is permitted only for the disposable target.
4. Record JSON, fio version, filesystem, mount/backend details if known, and host activity. Do not flush host caches.
5. Compare throughput and latency but explain that different cache state and host activity may dominate the difference.

**DATA-SAFETY PREFACE:** these tests overwrite `/scratch/fio-scratch.bin` only. Verify it is the disposable file on `storage-perf-scratch`. Do not change the target to another path.

**Expected evidence (illustrative; not executed here):** two result files and a short interpretation note. No particular direction or performance ratio is expected.

**Troubleshooting:** `direct=1` failure means the selected engine/filesystem combination may not support the requested mode; consult official fio/kernel docs. Do not silently switch modes without noting the change.

**What this lab proves:** cache effects can alter measured behavior and a test must state its I/O mode.

**What it does not prove:** which mode is faster in general or the underlying backend’s physical performance.

### Lab C — PostgreSQL application-level view with pgbench

**Objective:** observe transaction-level performance as a complement to fio, if a disposable PostgreSQL instance from Unit 5 is already available.

**Estimated duration:** 30–60 minutes. **Footprint:** use the existing small disposable database; do not install a full HA stack or MinIO for this lab.

**Preflight:** verify context, database endpoint, target database, and that it contains synthetic data only. Use the current PostgreSQL documentation for exact `pgbench` options and version compatibility. **[VERIFY: installed `pgbench --version` and official pgbench documentation.]**

A command pattern is:

```bash
pgbench --version
# Illustrative pattern only; verify flags and connection options for your installed version.
pgbench -i -s 1 <disposable-lab-database>
pgbench -c 2 -j 1 -T 60 <disposable-lab-database>
```

Initialization (`-i`) modifies the target database and is destructive to pgbench's benchmark tables. Never use it against a production or shared database. Use safe credential handling (for example, an approved `.pgpass` file with restrictive permissions or an interactive method); do not put passwords in command-line arguments. Verify flags such as client count, jobs, duration, and initialization scale against the installed version.

Record TPS, latency output, client count, duration, database version, connection endpoint, and concurrent storage activity. Correlate the same time window with database waits, WAL/fsync behavior, PVC/node counters, CPU throttling, and application metrics. A slow pgbench result alone does not prove storage is the cause.

**Expected evidence (illustrative; not executed here):** a pgbench summary with transaction throughput/latency and a timeline of supporting signals. Do not fabricate values.

**What this lab proves:** database transaction latency includes SQL, locks, CPU, connection, and storage effects.

**What it does not prove:** a pure storage benchmark or performance of a production database.

### Lab D — Disk-full incident and recovery

**Objective:** practice capacity evidence and safe cleanup without exhausting the host.

**Estimated duration:** 30–60 minutes. **Footprint:** existing lab PVC and at most 128 MiB additional scratch data in the example. Check host disk and PVC capacity first.

Disk-full exercises can destabilize a node or host if performed carelessly. Use the bounded scratch-file simulation in Section 6.7.8. It intentionally may not fill the PVC. Record:
- before/after `df -h /scratch`;
- file size and operation status;
- namespace, PVC, StorageClass, and provisioner;
- any observed errors;
- cleanup command and after-cleanup free space;
- why the exercise did not prove behavior at 100% full.

Do not attempt PVC expansion unless the selected StorageClass and CSI driver explicitly support it and the capability is verified from official documentation. kind’s default local-path provisioner may not support expansion. If unsupported, document the expansion decision path and perform only safe scratch cleanup.

**DATA-SAFETY PREFACE:** delete only the exact synthetic file `disk-full-simulation.bin` after confirming context and path. Do not delete PostgreSQL data, WAL, PVCs, or unknown files.

**Expected evidence (illustrative; not executed here):** a capacity snapshot, bounded write result, cleanup verification, and incident note.

**What this lab proves:** how to inspect and recover scratch-space consumption safely.

**What it does not prove:** how a real database behaves when its filesystem reaches 100% or whether a particular CSI driver can expand a volume.

### Lab E — Capacity projection and regression guard

**Objective:** estimate capacity runway from measurements and compare benchmark results with a baseline using relative changes.

**Estimated duration:** 30–45 minutes. **Footprint:** local Python scripts and small CSVs; negligible CPU/RAM/disk.

Save the illustrative `capacity.csv` and `capacity_projection.py` from Section 6.7.2. Run:

```bash
python3 capacity_projection.py capacity.csv --threshold-fraction 0.80
```

Create baseline and current CSVs with columns `profile,median_iops,median_bandwidth_bytes_per_sec`; values must be measured by the learner or clearly labelled **[ILLUSTRATIVE]**. Then run:

```bash
python3 compare-benchmarks.py baseline.csv current.csv
```

The comparison script fails when a profile is missing, values are invalid, baseline is zero, or a configured relative regression is exceeded. Its example threshold is illustrative. It checks only IOPS and bandwidth; extend it with latency/error criteria before using it in CI.

**Expected evidence (illustrative; not executed here):** projected growth and days to threshold, comparison deltas, and notes on assumptions. The example script has input validation but has not been executed here; the learner should run it locally and record the actual output.

**Troubleshooting:** missing columns or invalid timestamps should fail clearly; zero/negative growth should not yield a finite runway estimate; mismatched profiles should fail rather than silently compare different tests.

**What this lab proves:** how to calculate a transparent, limited linear estimate and detect large relative changes in a consistent environment.

**What it does not prove:** future capacity with certainty or production performance from local kind results.

### Lab cleanup verification

**⚠ DESTRUCTIVE — DATA LOSS:** removing the namespace can delete Jobs, Pods, PVCs, and synthetic scratch data. Read-only checks first; explicit confirmation required.

```bash
kubectl config current-context
kubectl get pods,jobs,pvc,svc -n storage-perf-lab -o wide
kubectl get pv
# Only after confirming the dedicated context and preserving evidence:
./cleanup-lab.sh --apply
# Verify no lab namespace/resources remain:
kubectl get namespace storage-perf-lab
kubectl get pvc -A
kubectl get pv
```

If the namespace is already absent, verify the result rather than rerunning destructive commands. Inspect PV reclaim policy and backend artifacts manually. Do not delete a PV solely because its name looks related to the lab.

## 6.12 Self-check Questions and Answer Key

### Questions

1. **[L1] Calculation:** A workload completes 6,000 IOPS with 8 KiB requests. Calculate decimal MB/s and binary MiB/s.
2. **[L1]** Why does high IOPS not guarantee low latency?
3. **[L1]** Explain the page-cache trap and why `direct=1` is not a perfect physical-device benchmark.
4. **[L1]** What does `fsync` request, and why is a successful `write()` not always proof of durable persistence?
5. **[L1/L2]** Why is `dd` alone a poor general-purpose benchmark?
6. **[L2]** Design the four fio profiles and state the read/write mix for each.
7. **[L2]** Which fields and metadata would you preserve to compare three repeated runs fairly?
8. **[L2]** Why must the parser fail closed when the expected fio JSON fields are absent?
9. **[L2/L3]** Why may `%util` mislead on modern or virtualized devices?
10. **[L3]** Explain why p99 latency matters even if mean latency is acceptable.
11. **[L3]** Choose between local NVMe, network block, network file, and object storage for a latency-sensitive PostgreSQL workload. Defend the choice and state what must be verified.
12. **[L3]** How can a backup job cause a p99 spike, and what evidence would establish a likely causal relationship?
13. **[L3]** Why must CPU throttling and query behavior be investigated before blaming storage?
14. **[L3/L4]** Why must PostgreSQL `fsync` or durability settings not be casually disabled?
15. **[L4]** A volume is full. Explain a safe decision path and why deleting WAL is unsafe.
16. **[L4]** What can kind establish about storage performance, and what can it not establish?
17. **[L4]** A capacity script predicts 72 days to a threshold. What assumptions and checks are needed before acting on that result?
18. **[L4]** What should a CI storage regression guard compare, and why should it use relative rather than cross-environment absolute thresholds?

### Answer key

1. `8 KiB = 8,192 bytes`; `6,000 × 8,192 = 49,152,000 bytes/s`, or `49.152 MB/s` decimal and `46.875 MiB/s` binary.
2. IOPS is a rate; latency depends on service time and queueing. Higher concurrency can raise IOPS while creating longer queues and worse tail latency.
3. Buffered I/O may be served by RAM or acknowledged before data is flushed. Direct I/O reduces some cache effects but still depends on filesystem, kernel, virtualization, and backend behavior.
4. `fsync` requests synchronization according to the OS/filesystem/storage contract. A write may complete after data is copied into cache; end-to-end durability depends on every layer honoring flush semantics.
5. A simple `dd` run usually lacks controlled mixed/random patterns, useful latency percentiles, and enough workload dimensions. Cache and buffering can dominate.
6. Random 4 KiB 50/50 mixed read/write; sequential 1 MiB write; random 4 KiB 70/30 read/write; 4 KiB synchronous write with `fsync=1`. State direct/buffered mode, engine, queue depth, runtime, and file cap.
7. Profile, version, target/PVC/StorageClass, block size, mix, engine, direct mode, queue depth, jobs, runtime, ramp, IOPS, bandwidth, latency statistics, errors, environment, and cache caveats.
8. Silent fallback to an unknown schema can misinterpret units or fields and produce false results. Fail closed, inspect official docs and sample JSON, then deliberately update the parser.
9. `%util` is busy time in the tool’s visible device model; parallel devices, RAID, multipath, and virtualization can decouple busy time from saturation.
10. A small number of slow operations can breach user-facing latency objectives while barely affecting the mean. Percentiles need enough samples and a defined workload/window.
11. Network block storage is a common candidate for persistent database volumes, but the correct choice depends on required semantics, measured latency, durability, failure domains, sharing, and cost. Verify the actual CSI/backend product and documented limits; do not infer performance from the category alone.
12. A backup may compete for bandwidth/IOPS, generate flush activity, or contend for CPU/network. Correlate backup timing with application p99, database waits, PVC/node counters, provider metrics, and repeatable changes; correlation alone is not proof.
13. Query plans, locks, connection saturation, CPU quotas, memory pressure, and network issues can cause similar symptoms. Collect aligned evidence from each layer before attributing cause.
14. Disabling durability settings can risk data loss or corruption after failures. Performance changes require explicit risk acceptance and version-specific documentation; it is not a generic fix.
15. Preserve evidence and data safety, identify the full resource, check archive/backup status, verify reclaimable files, and use supported expansion only when StorageClass/CSI/backend/filesystem support is confirmed. Never delete database files or WAL as generic cleanup.
16. kind can teach controlled workload design and local regression detection. It cannot establish production IOPS/latency, provider throttling, physical-zone behavior, backend durability, production restore time, or costs.
17. Check timezone-aware samples, stable capacity, data quality, growth trend, retention, seasonality, workload changes, expansion lead time, and response time. Linear extrapolation is not a guarantee.
18. Compare identical profiles and versions in a stable environment, repeated runs, relative changes, errors, and latency as well as throughput. Absolute numbers across unlike environments are not portable specifications.

## 6.13 Evidence Artifacts and Completion Gate

### Evidence to save locally

- `environment.txt`: OS/WSL2, kind/Kubernetes version, node image/runtime, context, CPU/memory/free disk, StorageClass, fio version, and tool availability.
- `lab-a-pvc-pod.yaml`: exact manifest used, including verified image identity and PVC details.
- `fio-jobs/*.fio`: all four profiles plus any page-cache comparison profile.
- `run-fio.sh`: runner and the exact expected context used.
- `results/*.json`: raw output from each successful run, plus error logs for failed runs where useful.
- `results/fio-run-summaries.csv` and `results/fio-summary.csv`: parser output, with the latency statistic definition documented.
- `results-template.csv` or a completed Markdown result table with caveats and environment metadata.
- `capacity.csv`, `capacity_projection.py`, and actual output.
- `baseline.csv`, `current.csv`, `compare-benchmarks.py`, and regression comparison output.
- `pgbench-notes.md` if Lab C is completed, including target isolation and correlation with database/storage evidence.
- `disk-full-incident.md`: before/after capacity, safe target, observed behavior, cleanup, and fidelity limitation.
- `cleanup-verification.txt`: expected context, namespace/PVC/Pod/Job inventory before cleanup, and verification after cleanup.
- `incident-analysis.md`: symptom, timeline, hypotheses, evidence, mitigation, validation, prevention, and residual uncertainty.

Do not claim these artifacts exist until you create them. Do not include real credentials, sensitive application data, or unrelated host details.

### Completion gate

The learner completes the unit when they can:

- Explain IOPS, throughput, latency, block size, queue depth, page cache, direct I/O, and `fsync`.
- Safely run all four fio profiles on a disposable PVC or document a concrete environment blocker.
- Produce a repeated-run result table with median/p95 definitions and environment metadata.
- Demonstrate the page-cache measurement caveat without claiming it proves production performance.
- Complete the bounded disk-full/recovery exercise or document the safer alternative and its limitations.
- Run the capacity projection script on sample or learner-collected data and explain its assumptions.
- Write an incident analysis with evidence, competing hypotheses, safe mitigation, validation, and prevention.
- Verify cleanup and confirm the intended lab resources are gone without deleting unrelated resources.

## 6.14 Sources and Verification Notes

This lesson and its example assets were authored but **not executed or live-validated here**. All output examples are illustrative unless explicitly described as a formula calculated from illustrative input. The URLs below are canonical official starting points; check the documentation version that matches the installed tool/kernel/platform.

| Topic | Official document/source | Claim or behavior to verify | Version sensitivity / notes |
|---|---|---|---|
| fio job options, engines, direct I/O, JSON | fio HOWTO: https://fio.readthedocs.io/en/latest/fio_doc.html | `rw`, `bs`, `direct`, `ioengine`, `iodepth`, `runtime`, `ramp_time`, `fsync`, JSON fields | fio version, engine, filesystem, and platform |
| fio project | https://github.com/axboe/fio | Trusted release/image source and version | Verify image tag/digest and architecture |
| `fsync(2)` | https://man7.org/linux/man-pages/man2/fsync.2.html | Synchronization semantics and metadata behavior | Kernel/filesystem/device contract matters |
| `open(2)` / `O_DIRECT` | https://man7.org/linux/man-pages/man2/open.2.html | Alignment and direct-I/O restrictions | Filesystem/kernel/platform-dependent |
| `iostat(1)` | https://man7.org/linux/man-pages/man1/iostat.1.html | `await`, queue metrics, `%util`, output units | sysstat version and virtual device model |
| `pidstat(1)` | https://man7.org/linux/man-pages/man1/pidstat.1.html | Available process statistics and options | sysstat/kernel-dependent |
| `iotop(8)` | https://man7.org/linux/man-pages/man8/iotop.8.html | Permission and kernel requirements | Tool/kernel packaging varies |
| Linux block layer | https://docs.kernel.org/block/ | Block queues and I/O behavior | Kernel and device stack dependent |
| cgroup v2 | https://docs.kernel.org/admin-guide/cgroup-v2.html | `io.max` and device support | Requires supported cgroup v2 and correct device mapping |
| Kubernetes PVs/PVCs | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | PVC/PV lifecycle and access modes | Provisioner and backend behavior differ |
| Kubernetes StorageClasses | https://kubernetes.io/docs/concepts/storage/storage-classes/ | Provisioner-specific parameters and defaults | Parameters are not portable performance guarantees |
| Kubernetes Jobs | https://kubernetes.io/docs/concepts/workloads/controllers/job/ | Job lifecycle and retries | API behavior/version may vary |
| Kubernetes resource management | https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ | CPU/memory requests/limits and ephemeral storage | Node/runtime/accounting behavior varies |
| Kubernetes node-pressure eviction | https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/ | DiskPressure, eviction signals and behavior | Kubelet configuration/platform dependent |
| Kubernetes CSI volume expansion | https://kubernetes.io/docs/concepts/storage/persistent-volumes/#expanding-persistent-volumes-claims | Expansion workflow | StorageClass, CSI driver, backend, filesystem must support it |
| PostgreSQL WAL | https://www.postgresql.org/docs/current/wal-intro.html | WAL and durability/recovery concepts | Match deployed PostgreSQL major version |
| PostgreSQL reliability | https://www.postgresql.org/docs/current/wal-reliability.html | OS/storage flush assumptions | Hardware/virtualization contract is critical |
| PostgreSQL WAL configuration | https://www.postgresql.org/docs/current/runtime-config-wal.html | `fsync`, `synchronous_commit`, checkpoint settings | Match deployed major version and configuration |
| PostgreSQL monitoring | https://www.postgresql.org/docs/current/monitoring-stats.html | Wait/transaction/IO statistics available | Metrics and views vary by version |
| PostgreSQL pgbench | https://www.postgresql.org/docs/current/pgbench.html | Flags, initialization, workload and result semantics | Verify installed `pgbench` version |
| ext4 documentation | https://www.kernel.org/doc/html/latest/filesystems/ext4/ | Filesystem concepts and supported behavior | Kernel and mount options matter |
| XFS documentation | https://docs.kernel.org/admin-guide/xfs.html | Filesystem behavior and administration | Kernel/distribution tooling varies |
| kind | https://kind.sigs.k8s.io/ | Local cluster behavior and node image | Not a production storage environment |
| Stage 2E M03 Unit 2 | User roadmap / sibling module | CPU/resource troubleshooting | Use the exact local repository lesson |
| M05 Units 1–3, 5, 7–8 | User roadmap / sibling lessons | PVC/CSI/snapshot/database/topology/troubleshooting boundaries | Consult the matching local lesson |
| M11 and M15 | User roadmap / sibling modules | Observability/SLOs and cost/capacity | Detailed implementation is deferred |

### Claim register

| ID | Claim | Source | Confidence | Verification tag |
|---|---|---|---|---|
| C01 | Throughput is IOPS multiplied by average bytes per operation for the measured workload | Arithmetic; fio workload model | High | None; keep units consistent |
| C02 | Page cache can make buffered I/O appear faster than persistent storage service | Linux I/O documentation | High | Verify filesystem/kernel behavior |
| C03 | `direct=1` does not guarantee a physical-device benchmark | fio and `O_DIRECT` documentation | High | Verify exact engine/filesystem |
| C04 | `fsync` requests synchronization under the OS/storage contract | `fsync(2)`, PostgreSQL reliability docs | High | Verify deployed stack guarantees |
| C05 | Disabling `fsync` is not a generic safe performance fix | PostgreSQL WAL reliability docs | High | Match PostgreSQL version |
| C06 | Fio JSON field paths can vary by version/engine | fio documentation/output schema | High | Inspect actual JSON |
| C07 | `%util` alone is not universal saturation proof | `iostat(1)` semantics and device architecture | High | Verify sysstat output/device model |
| C08 | `kubectl top` reports CPU/memory rather than disk I/O latency | Kubernetes metrics API scope | High | Verify available metrics providers |
| C09 | PVC expansion requires support across StorageClass/CSI/backend/filesystem | Kubernetes PV expansion docs | High | Verify exact driver |
| C10 | kind/WSL2 results are not production capacity guarantees | Environment architecture and kind docs | High | Record local environment |
| C11 | Cloud storage may have per-volume/instance limits or burst behavior | Provider-specific official docs | Medium | **[VERIFY: exact provider/product/tier/region]** |
| C12 | PostgreSQL WAL/checkpoints/autovacuum can affect I/O and latency | PostgreSQL official docs | High | **[VERIFY: deployed major version/settings]** |
| C13 | Separate WAL volume is not automatically faster | Workload/architecture inference | Medium | Measure in the target environment |
| C14 | cgroup v2 `io.max` is a Linux control concept, not a portable Kubernetes per-Pod guarantee | Kernel cgroup v2 docs | High | **[VERIFY: kernel/runtime/device integration]** |
| C15 | `emptyDir` disk and memory-backed behavior affects ephemeral storage and memory pressure | Kubernetes resource/volume docs | High | **[VERIFY: node accounting and configuration]** |
| C16 | Linear capacity projection assumes stable growth | Linear regression model | High | Validate trend and input quality |
| C17 | A small number of runs cannot establish stable p99 behavior | Statistical reasoning | High | Record sample count and workload |
| C18 | A one-off `dd` result is not a general storage benchmark | Benchmark methodology | High | Use a workload-specific profile |
| C19 | The sample fio image tag is suitable for a particular architecture | Image registry/source | Open | **[VERIFY: image/tag/digest, shell, UID, fio version]** |
| C20 | The selected StorageClass supports writable 2 GiB PVCs and required access mode | Cluster configuration | Open | **[VERIFY: actual provisioner, binding, permissions]** |
| C21 | `libaio`, `direct=1`, and the selected fio fields behave as shown | fio/kernel/filesystem docs | Open | **[VERIFY: installed versions and test output]** |
| C22 | The current CSI driver supports PVC expansion | Driver/backend docs | Open | **[VERIFY: official driver capability and filesystem path]** |
| C23 | The exact PostgreSQL `pgbench` flags match the installed version | PostgreSQL docs | Open | **[VERIFY: `pgbench --version` and current docs]** |

### Cross-module alignment

- **M01:** non-root images, UID/GID, and volume permissions. This unit uses a non-root lab Pod where compatible.
- **M03 Unit 2:** CPU throttling/resource metrics versus I/O wait and storage latency.
- **M04:** NetworkPolicy is not an I/O performance control; network storage introduces network dependencies.
- **M05 Units 1–3:** PVC, StorageClass, CSI, snapshots, and expansion concepts are prerequisites, not retaught in full.
- **M05 Unit 5:** CloudNativePG/PostgreSQL WAL and database behavior; `pgbench` is optional and does not require a full HA stack.
- **M05 Unit 7:** topology and locality effects are referenced rather than retaught.
- **M05 Unit 8:** storage troubleshooting, disk-full symptoms, and orphaned resources are referenced rather than retaught.
- **M11:** storage/database observability and SLO implementation.
- **M15:** storage cost, capacity, and tiering.
- **Stage 2C:** ETL I/O patterns, small files, Parquet row groups, and shuffle spill.

This unit directly teaches workload design, measurement interpretation, safe local experiments, and evidence-based performance diagnosis. Deep CSI/PV lifecycle, topology, database operations, production monitoring implementation, and cost governance remain in the linked units.

## 6.15 Self-Audit Report

The following audit reflects a content review of this lesson. No cluster, fio job, parser, capacity script, pgbench run, or cleanup command was executed during authoring; therefore execution-related checks remain open.

| Check | PASS / FIXED / OPEN | Evidence / correction | Residual risk |
|---|---|---|---|
| Curriculum completeness | PASS | L1–L4 topics, four fio profiles, five labs, SRE/security/checklists, answer key, claim register included | Actual hands-on execution remains learner work |
| Technical accuracy | OPEN | Commands and version-sensitive behavior are linked to official docs; image tag, fio schema, PostgreSQL flags, and driver capabilities are marked for verification | Local versions may differ |
| Safety | FIXED | No raw-device fio targets, no hostPath, bounded file size/runtime, context checks, destructive cleanup confirmation | Learner must verify context and target before executing |
| Measurement integrity | PASS | No fabricated benchmark output; illustrative values labelled; throughput arithmetic uses explicit units; latency summaries are defined | Small N is not a high-confidence p99 estimate |
| Environment fidelity | PASS | WSL2/kind/laptop limitations stated; provider/production guarantees explicitly excluded | Local host/VM behavior still affects results |
| Executable assets | OPEN | YAML and scripts are provided inline with dry-run/confirmation and fail-closed parser logic | Not executed; image/schema/permissions require local verification |
| Cross-module consistency | PASS | M01/M03/M04/M05/M11/M15 and Stage 2C boundaries are linked | Exact local sibling content should be checked in repository |
| Source quality | OPEN | Official canonical starting points and topic-specific checks are listed | Links and latest version details were not live-verified |
| Capacity projection | FIXED | Input validation, timezone requirement, least-squares slope, threshold formula, and non-positive growth handling included | Linear model fails under nonlinear growth/capacity changes |
| Regression guard | FIXED | Profile matching and relative IOPS/bandwidth comparison fail closed on mismatch | Example guard does not yet include latency/error SLOs |
| Disk-full safety | FIXED | Bounded 128 MiB scratch simulation; explicit warning; no host-fill attempt; expansion gated on verified support | It may not reproduce a true full-filesystem error |
| Scope discipline | PASS | Unit 6 only; cross-references rather than reproducing Units 7–8 | None identified |
| Final source/verification notes | PASS | Claim register has 23 claims and identifies open version-dependent checks | Must be completed against actual installed stack |

### Five likely ways this lesson could mislead a learner—and mitigations

1. **Mistaking kind results for production capacity.** The lesson repeats the fidelity boundary and includes a table of claims the laptop lab cannot establish.
2. **Treating `direct=1` as proof of physical I/O.** The page-cache discussion explains engine/filesystem/kernel dependence and prohibits claiming a perfect device benchmark.
3. **Interpreting p95 across three runs as a reliable p99.** The parser defines its statistic precisely and warns that a few run summaries are not enough to estimate an operation-level tail with high confidence.
4. **Assuming a PVC can be expanded or that `%util` means saturation.** Both are explicitly gated on driver/device semantics and official documentation.
5. **Reclaiming database space by deleting WAL or filling the host to reproduce an incident.** The runbook prohibits deleting database/WAL files and uses a bounded scratch simulation instead.

**Open verification items before a real lab run:** select and verify the fio image/tag/digest; verify current fio options and JSON schema; confirm the default StorageClass, PVC binding, volume permissions, and resource budget; confirm `pgbench` flags against the installed version; and verify any CSI expansion or provider-specific performance behavior from official documentation. No lab result is claimed as observed.
