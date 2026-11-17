# Project 0.3 — Process, Resource, and Port Diagnosis Lab

**Practical hands-on project**
**Estimated time:** 60–90 minutes.

**Main objective:** Learn to identify a running process, inspect its CPU and memory usage, find its listening port, safely stop it and verify that it has actually stopped.

---

## 1. Project purpose and industry relevance

Imagine a Python API, AI model server or background worker is consuming too much CPU or holding a port that another service needs.

Instead of restarting your computer, you should:

1. Identify the problematic process.
2. Inspect its behavior and resources.
3. Confirm its identity.
4. Stop it safely.
5. Verify that the process and port are gone.

These are important production troubleshooting skills.

---

## 2. Prerequisites and safety

Previously covered concepts:

- Processes and threads.
- CPU scheduling.
- Signals (`SIGTERM` vs. `SIGKILL`).
- Process lifecycle and exit codes.
- Local networking, ports and reachability.

**Required tools:** Bash/WSL2 or PowerShell, Python 3 and a text editor.

**Safety rules:**

- Work only inside a dedicated practice directory.
- Create and stop only processes you started yourself.
- Capture and independently verify the PID before stopping anything.
- Always attempt graceful termination first.
- No `sudo`, administrator rights or system configuration changes are required.

---

## 3. Industry-standard troubleshooting workflow

Follow this loop:

Goal → Assumptions → Smallest experiment → Observe output → Form hypothesis → Change one variable → Verify → Document.

Do not guess or change multiple things simultaneously.

---

## 4. Practical implementation

### Step 1 — Create a practice directory

```bash
mkdir -p ~/practice-shell/process-diagnosis
cd ~/practice-shell/process-diagnosis
pwd
```

### Step 2 — Start a test process. Choose one:

**Option A:** Idle process.

```bash
sleep 600 &
PID=$!
echo "PID: $PID"
```

**Option B:** Local HTTP server.

```bash
python3 -m http.server 8000 &
PID=$!
echo "PID: $PID"
```

`$!` captures the PID of the most recently started background process. Record it immediately.

### Step 3 — Verify the process identity.

```bash
ps -p "$PID" -o pid,stat,etime,cmd
```

PowerShell equivalent:

```powershell
Get-Process -Id $PID
```

Confirm that the command matches your test process.

### Step 4 — Inspect CPU and memory.

```bash
top -p "$PID"
```

An idle process should show near-zero CPU usage. To compare, run a short CPU-heavy Python calculation:

```bash
python3 -c "total=0
for i in range(50000000):
    total += i
print(total)"
```

The calculation should temporarily consume much more CPU. Both processes are still running processes, but their resource usage differs.

### Step 5 — Inspect the listening port (Option B).

```bash
ss -ltnp | grep 8000
```

PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

Confirm that the reported PID matches your captured PID.

### Step 6 — Test reachability.

```bash
curl -i http://localhost:8000/
```

An HTTP `200 OK` response confirms that the service is responding.

### Step 7 — Stop the process gracefully.

```bash
kill -TERM "$PID"
```

PowerShell:

```powershell
Stop-Process -Id $PID
```

`SIGTERM` requests termination and allows cleanup. `SIGKILL` or `-Force` should only be considered as a last resort after rechecking the same confirmed PID.

### Step 8 — Verify termination.

```bash
ps -p "$PID"
ss -ltnp | grep 8000
```

Expected: no matching process and no listening port. The port check applies if you chose Option B.

---

## 5. Incident report and deliverables

Create `process-diagnosis.md` containing:

- **Symptom:** What problem were you investigating?
- **Observations:** Actual PID, CPU, memory, port and `curl` results.
- **Commands:** Exact commands executed, in order.
- **Root cause:** The test process you intentionally created.
- **Safe remediation:** How you stopped it and why graceful termination came first.
- **Verification:** Evidence that the process and port were gone.

The project folder should also contain your completed self-checks.

---

## 6. Common problems and troubleshooting

| Problem | Safe response |
|---|---|
| PID variable is empty | Find the process again and independently verify its identity. |
| No such process | It may already have exited; check with `ps`. |
| Process remains after `SIGTERM` | Wait and recheck; consider `SIGKILL` only as a last resort. |
| Port visible without process name | Use its PID and cross-check with `ps`. |
| Connection refused | Check the server terminal and actual listening port. |

---

## 7. Exercises, interview and completion

The project includes:

- CPU comparison between idle and busy processes.
- Port ownership and reachability testing.
- Five interview questions covering process inspection, port conflicts, graceful vs. forced termination, verification and service reachability.
- A completion checklist requiring real command output and a written incident report.

**Production relevance:** These skills apply to AI inference services, training jobs, backend APIs, model servers and agent workers.

---

## Final takeaway

A production engineer must identify the exact process, collect evidence, confirm its identity, stop it safely and verify the result. Never guess which process to terminate or restart the entire machine without diagnosing the problem.
