# Project 0.3 — Process, Resource, and Port Diagnosis Lab

**Estimated time:** 60–90 minutes (can be split across two sessions)

**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Section 5 — "Practical
projects," Project 0.3 — "Process, Resource, and Port Diagnosis Lab"; and Section 2's Module 0.2
audit evidence: *"Find a running process, inspect its PID and resource use, stop a test process
safely, and explain exit code `0` versus non-zero."*

---

## 1. Project title and estimated time

**Process, Resource, and Port Diagnosis Lab** — estimated 60–90 minutes.

## 2. Purpose and production AI-engineering relevance

This project is a small, evidence-based diagnosis exercise. Its scenario: a test program is
consuming CPU or holding a network port, and you must identify it and stop it safely — without
restarting your computer, and without guessing.

This is not a toy skill. In production AI-engineering work, this exact loop — find the process,
confirm what it's doing, confirm it's the right one, stop it cleanly, verify it's actually gone —
is how engineers handle a hung backend API, a runaway training job, a model server that won't
release a port before a redeploy, or an agent worker that's stuck. An engineer who cannot do this
methodically ends up restarting the whole machine to "fix" a problem they never actually diagnosed —
which doesn't work in a shared server or production environment, and teaches nothing about the
actual cause.

## 3. Learning outcomes

By the end of this project, you will be able to:

- Start a harmless, disposable local process and capture its PID at the moment of creation.
- Identify that process using `ps`, `top`/`htop` (Linux/WSL2), or `Get-Process` (PowerShell), and
  explain what its CPU and memory figures mean.
- Explain, with a real example, the difference between an idle process and a busy one.
- Find a listening port using `ss -ltnp` (Linux/WSL2) or `Get-NetTCPConnection` (PowerShell), and
  confirm it belongs to your test process.
- Verify a local service is actually reachable using `curl`, not just assumed.
- Stop **only a PID you have personally confirmed** belongs to your own test process, gracefully
  first.
- Verify both the process and the port are gone afterward.
- Write a short, evidence-based incident report.

## 4. Prerequisites, safety rules, and practice-directory warning

**Concepts you should have already read** (in this module,
`02-Operating-System-Fundamentals/`):

- `03-processes.md`, `04-threads.md` — what a process is and how it differs from a thread
- `05-scheduling.md` — why CPU usage rises and falls
- `10-signals.md` — `SIGTERM` vs. `SIGKILL`, graceful vs. forced termination
- `14-process-lifecycle.md` — creation, running, termination, exit codes
- `16-local-networking-for-development.md` — ports, listening, reachability, `ss -ltnp`,
  `Get-NetTCPConnection`, `curl`

You do not need to have memorized these — you need to be willing to reread one if a step below
doesn't make sense. This project assumes the concepts; it does not re-teach them.

**Tools required** (all free, already covered in Stage 0): a terminal (Bash/WSL2 or PowerShell),
Python 3 (for the optional local HTTP server), and a text editor.

**Not required:** Docker, any cloud account, GPUs, or advanced programming — every command below is
explained before you're asked to run it.

> ### ⚠️ Work only in a dedicated practice directory
>
> Every step in this project must happen inside a practice folder created specifically for it — for
> example, `~/practice-shell/process-diagnosis/` (Bash) or
> `C:\practice-shell\process-diagnosis\` (PowerShell). **Never** run this project's commands from
> Downloads, Documents, or an existing project folder. Confirm your current directory (`pwd` /
> `Get-Location`) before starting any process.

**Safety rules — read before Section 6:**

1. **You only ever create, inspect, and stop processes you started yourself, in this session, for
   this project.** Never target a PID you have not personally confirmed belongs to your own test
   process (Step 7.3 shows exactly how to confirm this).
2. **Stop gracefully first.** This project's commands ask a process to stop (`SIGTERM` on
   Linux/WSL2, or `Stop-Process` without `-Force` on PowerShell) before ever considering a forced
   stop — see `10-signals.md` for why that distinction matters.
3. **No command in this guide deletes files, modifies system configuration, or requires `sudo` /
   administrator rights.** If a step ever seems to need one of those, stop — that is not part of
   this project.
4. **If you are ever unsure whether a PID is your test process, do not act on it.** Re-run the
   confirmation command in Step 7.3 instead of guessing.

## 5. Deliverables and evidence checklist

By the end, your practice folder should contain:

- [ ] `process-diagnosis.md` — your incident report (Section 7.9), written in the format described
      there.
- [ ] A completed self-check against Section 7's steps.
- [ ] A completed self-check against the completion gate in Section 11.

If you are tracking this work in Git (recommended — see Stage 0 Gap 0A), commit these files with a
message such as `docs: add process, resource, and port diagnosis report`.

## 6. Industry-standard troubleshooting workflow

Use this loop for every step below, not only when something breaks:

```text
Goal → assumptions → smallest experiment → observe output/logs
→ form hypothesis → change one variable → verify → document
```

In practice, for each step:

1. **Goal** — one sentence: what are you trying to find out or confirm?
2. **Assumptions** — one sentence: what do you expect to happen, before you run anything?
3. **Smallest experiment** — run the smallest command that can answer the question.
4. **Observe output/logs** — read the actual output; do not skim it.
5. **Form hypothesis** — if something is surprising, write down your best explanation for why.
6. **Change one variable** — test that explanation by changing exactly one thing at a time.
7. **Verify** — confirm the result, don't assume it.
8. **Document** — record it in `process-diagnosis.md` before moving to the next step.

## 7. Step-by-step practical instructions

### 7.1 Create and confirm a safe practice directory

```bash
mkdir -p ~/practice-shell/process-diagnosis
cd ~/practice-shell/process-diagnosis
pwd
```

(PowerShell: `New-Item -ItemType Directory -Force ~/practice-shell/process-diagnosis`, then
`Set-Location ~/practice-shell/process-diagnosis`, then `Get-Location`.)

Record the confirmed path in `process-diagnosis.md`. Every remaining step happens here.

### 7.2 Start a harmless long-running process or local HTTP server

Choose **one** of these two harmless, disposable test workloads.

**Option A — a simple idle loop** (Bash):

```bash
sleep 600 &
PID=$!
echo "Started test process with PID: $PID"
```

`sleep 600` does nothing but wait for 600 seconds, then exit on its own — a safe, inert stand-in
for a stuck or idle process. The trailing `&` runs it in the background; `$!` captures the PID of
the most recently started background process, immediately, at creation. This is the key safety
habit for this whole project: **capture the PID the moment you create the process, before doing
anything else.**

**Option B — a local HTTP server** (Bash, builds directly on
`16-local-networking-for-development.md`):

```bash
python3 -m http.server 8000 &
PID=$!
echo "Started test server with PID: $PID"
```

This starts a small local web server listening on port `8000` — useful if you want to practice the
port-diagnosis steps (7.5–7.6) as well as process diagnosis.

**PowerShell equivalent (Option A style):**

```powershell
$proc = Start-Process -PassThru -NoNewWindow powershell -ArgumentList "-Command Start-Sleep -Seconds 600"
$PID = $proc.Id
Write-Output "Started test process with PID: $PID"
```

Record the PID you captured in `process-diagnosis.md` before continuing — this is your one, single
source of truth for the rest of the project.

### 7.3 Identify the process and confirm it's genuinely yours

**Goal:** prove, independently of the number you just wrote down, that this PID really refers to
your test process — not assume it.

Linux/WSL2:

```bash
ps -p "$PID" -o pid,stat,etime,cmd
```

- `ps` — lists processes. `-p "$PID"` restricts it to the exact PID you captured.
- `-o pid,stat,etime,cmd` — chooses which columns to show: process ID, status, elapsed running
  time, and the exact command line.

**Example output:**

```text
    PID STAT     ELAPSED CMD
  41207 S           0:05 sleep 600
```

`CMD` showing `sleep 600` (or `python3 -m http.server 8000`) is your confirmation: this PID is
genuinely the process you started, not something else that happens to share a number with a
process from an earlier session.

PowerShell:

```powershell
Get-Process -Id $PID | Select-Object Id, ProcessName, CPU, StartTime
```

Record this output in `process-diagnosis.md`. **This is the confirmation step every later
"stop the process" action in this project depends on — do not skip it.**

### 7.4 Inspect CPU and memory use; explain idle vs. busy

While your test process is running, observe it with a live monitoring tool:

Linux/WSL2:

```bash
top -p "$PID"
```

or, if installed:

```bash
htop -p "$PID"
```

- `top`/`htop` — live, continuously-updating views of running processes and their resource use.
  `-p "$PID"` restricts the view to just your process. Press `q` to quit.

PowerShell:

```powershell
Get-Process -Id $PID | Select-Object CPU, WorkingSet
```

**What to observe:** `sleep 600` (or an idle HTTP server with no requests yet) should show
consistently near-0% CPU — it isn't doing any computation, only waiting. Note the memory (RSS /
Working Set) figure too; it should be small and stable.

**Now create contrast, briefly:** in a separate terminal, run a short CPU-heavy command such as:

```bash
python3 -c "
total = 0
for i in range(50_000_000):
    total += i
print(total)
"
```

While that runs, check `top`/`Get-Process` for *that* process (find its PID the same way, via
`ps aux | grep python3` or a fresh `Start-Process` capture) and note its CPU percentage — it should
spike close to 100% of one core while running, then drop to nothing once it finishes.

In `process-diagnosis.md`, write 2–4 sentences explaining, in your own words, why an idle process
(`sleep`, or a server with no requests) shows near-0% CPU while a computation-heavy process shows
high CPU — and why both are still equally "running" as far as `ps` is concerned. This is Section
5's scheduling-and-CPU distinction from `05-scheduling.md`, observed directly.

### 7.5 Find a listening port (if you chose Option B)

Skip this step if you used Option A (`sleep 600`) and did not also start the HTTP server.

Linux/WSL2:

```bash
ss -ltnp | grep 8000
```

**Example output:**

```text
LISTEN 0  5  127.0.0.1:8000  0.0.0.0:*  users:(("python3",pid=41301,fd=3))
```

Confirm the `pid=` value matches the PID you captured in Step 7.2.

PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

Confirm the `OwningProcess` value matches your captured PID.

Full explanations of every part of this output are in
[`../16-local-networking-for-development.md`](../16-local-networking-for-development.md), Section
9 — reread it now if any part of this is unclear.

### 7.6 Verify reachability with `curl` (if you chose Option B)

```bash
curl -i http://localhost:8000/
```

Confirm you get a real `HTTP/1.0 200 OK` (or similar) response, not a "connection refused" error.
This proves the process is not just running (Step 7.3) and not just listening (Step 7.5), but
actually **reachable** end to end — the full distinction covered in
`16-local-networking-for-development.md`, Section 5.

### 7.7 Stop the identified test process gracefully

**This is the step where the safety rules in Section 4 matter most. Re-read your confirmation from
Step 7.3 before running anything here.**

Linux/WSL2:

```bash
kill -TERM "$PID"
```

- `kill -TERM` — sends `SIGTERM`, a polite termination *request* (see `10-signals.md`), to the
  exact PID you already confirmed in Step 7.3. This is not a forced kill — a process can, in
  principle, clean up before exiting in response to it.

PowerShell:

```powershell
Stop-Process -Id $PID
```

Without `-Force`, this requests a normal termination, the equivalent of `SIGTERM`.

**Only if** the process is still confirmed running after a few seconds (recheck with Step 7.8
below) should you consider a forced stop (`kill -KILL "$PID"` / `Stop-Process -Id $PID -Force`) —
and only on the same, already-confirmed PID.

### 7.8 Verify the PID ended and the port is no longer listening

```bash
ps -p "$PID"
```

**Expected result:** no matching process — `ps` prints only its header row, or an error indicating
the PID doesn't exist. This confirms termination.

If you used Option B, also recheck:

```bash
ss -ltnp | grep 8000
```

**Expected result:** no output. The port is free again.

PowerShell equivalents:

```powershell
Get-Process -Id $PID -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
```

Both should return nothing.

### 7.9 Write an evidence-based `process-diagnosis.md` incident report

Using the notes you've been collecting through Steps 7.1–7.8, write `process-diagnosis.md` with
these sections:

- **Symptom** — one or two sentences describing the scenario (a test process consuming resources
  or holding a port that needed to be identified and stopped).
- **Observations** — the actual PID, `ps`/`Get-Process` output, CPU/memory notes from Step 7.4, and
  (if applicable) the `ss -ltnp`/`Get-NetTCPConnection` and `curl` results from Steps 7.5–7.6. Use
  real output, not paraphrases.
- **Commands** — the exact commands you ran, in order.
- **Root cause** — in this lab, simply: "a test process I started intentionally, later confirmed by
  PID and stopped deliberately" — the point is demonstrating the *method*, not a real incident.
- **Safe remediation** — how you stopped it (graceful `SIGTERM`/`Stop-Process`, and why that was
  tried before any forced option).
- **Verification** — the exact evidence (Step 7.8's output) proving both the process and, if
  applicable, the port were actually gone afterward.

## 8. Expected observations and success criteria

- The PID you captured at creation (Step 7.2) matches, exactly, the PID confirmed by `ps`/
  `Get-Process` (Step 7.3) and, if using Option B, the `pid=`/`OwningProcess` value from `ss -ltnp`/
  `Get-NetTCPConnection` (Step 7.5).
- CPU usage for an idle process (`sleep`, or a server with no requests) stays near 0%; a
  computation-heavy process spikes near 100% of one core while running, then returns to 0% once
  finished.
- If using Option B: `curl` returns a real HTTP response while the server is running, and
  "connection refused" after it's stopped.
- After Step 7.7, `ps -p "$PID"` (or `Get-Process -Id $PID`) shows the process is gone, and (if
  applicable) `ss -ltnp` no longer shows the port.
- `process-diagnosis.md` contains real, observed output for every claim — not descriptions of what
  "should" happen.

## 9. Common problems and safe troubleshooting

| Problem | Likely cause | Safe next step |
|---|---|---|
| `$PID` is empty or wrong in a later step | You opened a new terminal/session since Step 7.2, so the shell variable no longer holds the value | Re-run Step 7.3's confirmation using `ps aux \| grep sleep` (or `grep python3`) to find the PID again from scratch, rather than trusting a stale variable. |
| `kill -TERM "$PID"` reports "No such process" | The process already exited (for example, `sleep 600` finished naturally if you took a long break) | Confirm with `ps -p "$PID"` first — this is expected, not an error; just restart Step 7.2 if you still need an active process for later steps. |
| Process still shows in `ps` after `kill -TERM` | Some programs take a moment to clean up, or (rarely) ignore `SIGTERM` | Wait a few seconds and recheck; only after confirming it is still your already-verified PID, consider `kill -KILL "$PID"` as a last resort. |
| `ss -ltnp` shows the port with no process name | Insufficient permissions to see the process name for that socket | Use the PID number alone (still shown) and cross-check it with `ps -p <pid>` — you don't need the name from `ss` if `ps` confirms the same PID independently. |
| `curl` says "connection refused" while the server "should" be running | The server crashed after starting, or is listening on a different port | Check the server's own terminal for an error message, and re-run `ss -ltnp` to see what port (if any) it actually bound to — see `16-local-networking-for-development.md`, Section 11. |

If you hit something not listed here, apply the workflow in Section 6: state what you expected,
what happened instead, and check one fact (PID, port, permissions) at a time before changing
anything.

## 10. Interview-practice questions

Practice answering these aloud, in 60–90 seconds each, using your own notes from
`process-diagnosis.md`:

1. **"How would you find out what a specific running process is doing on your machine?"**
   Guidance: name the actual tools (`ps`, `top`/`htop`, or `Get-Process`) and the specific fields
   you'd check (PID, CPU%, memory, command line) — anchor your answer in your own captured PID and
   output, not a general description.

2. **"A local server won't start because a port is already in use — how would you diagnose it?"**
   Guidance: walk through `ss -ltnp`/`Get-NetTCPConnection` to find the PID holding the port, `ps`/
   `Get-Process` to confirm what that process actually is, and only then decide whether to stop it —
   emphasizing that you'd confirm before acting, never guess-kill a port.

3. **"What's the difference between a graceful and a forced process termination, and why does it
   matter?"**
   Guidance: connect `SIGTERM` (a request, allowing cleanup) versus `SIGKILL`/`-Force` (immediate,
   no cleanup possible) to a concrete risk — for example, a server mid-write to a file or database
   connection.

4. **"How do you verify a process actually stopped, rather than assuming it did?"**
   Guidance: describe re-checking with `ps -p <pid>` (or `Get-Process -Id <pid>`) after stopping it,
   and, if relevant, re-checking the port with `ss -ltnp` — evidence, not assumption.

5. **"What's the difference between a process being alive and a service being reachable?"**
   Guidance: use your own Option B experience if you did it — a process can be running and still
   fail to answer `curl` if it crashed before binding its port, or is listening elsewhere.

## 11. Completion gate

You have completed this project when all statements below are true:

- [ ] I created a disposable test process (or local HTTP server) myself and captured its PID at the
      moment of creation.
- [ ] I confirmed that exact PID independently using `ps`/`Get-Process` before taking any further
      action on it.
- [ ] I observed and can explain, with real numbers, the difference between an idle and a
      CPU-busy process.
- [ ] (If Option B) I found the listening port with `ss -ltnp`/`Get-NetTCPConnection` and confirmed
      it matched my process's PID, and verified reachability with `curl`.
- [ ] I stopped only my already-confirmed PID, gracefully, and explained why graceful comes first.
- [ ] I verified afterward, with real command output, that both the process and (if applicable) the
      port were gone.
- [ ] `process-diagnosis.md` is complete, in my own words, with real observed output for every
      claim.
- [ ] I answered all five interview-practice questions aloud at least once.

Once every box is checked, this project satisfies Stage 0 Project 0.3 and the Module 0.2 audit
evidence referenced in the Stage 0 roadmap's Section 2. Return to
[`../../00-Stage-0-Overview/learning-plan.md`](../../00-Stage-0-Overview/learning-plan.md) to
continue with the rest of Stage 0.
