# 15. OS Tools Overview

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Module 0.2 — Operating System Fundamentals
**Concept(s) covered:** `ps`, `top`/`htop`, `/proc`, `kill`/signals, file descriptors, exit codes, permissions, resource limits, process trees
**Status:** Not Started

---

## Learning Objectives

By the end of this lesson you should be able to:

- explain what each core Linux process-inspection tool (`ps`, `top`, `htop`, `/proc`, `kill`) actually observes, and how it relates to the OS concepts Module 0.2 already taught
- use these tools to answer concrete questions about a running process — its identity, parent, state, CPU/memory usage, open files, resource limits, and exit status
- understand that no single tool gives the complete picture, and correlate evidence from multiple tools into a coherent diagnosis
- safely observe and control a disposable process's lifecycle without ever risking an unrelated or system process
- apply this exact toolkit to realistic AI-engineering scenarios — diagnosing a slow, stuck, memory-heavy, or unexpectedly-exited Python service

## Prerequisites

This is the **final lesson of Module 0.2**, and it deliberately does not teach any new OS *concept* — every idea here was already built, piece by piece, across the previous fourteen lessons. This lesson's job is different: **it teaches the tools that let you actually *see* those concepts in a real, running process.**

```text
Kernel → User Space → System Calls → Processes → Threads → Scheduling
   → Virtual Memory → Filesystems → Permissions → Environment Variables
   → Signals → Standard I/O → Pipes → Shell → Process Lifecycle
   → OS Tools Overview (this lesson)
```

This lesson does not repeat [Processes](03-processes.md), [Signals](10-signals.md), [Standard Input/Output](11-standard-input-output.md), [Permissions](08-permissions.md), or [Process Lifecycle](14-process-lifecycle.md) — it shows you the specific commands that reveal what each of those lessons already taught you to expect.

---

## 1. The Core Mental Model: Tools as Windows into a Process

```text
Running Program
      ↓
Operating-System Process                    (Concept 03)
      ↓
PID / PPID / State / Resources / Files / I/O
      ↓
OS exposes observable information
      ↓
Diagnostic tools inspect that information
      ↓
Engineer interprets evidence
      ↓
Engineer diagnoses behavior
```

**The single most important idea in this entire lesson: no one tool gives the complete picture.** Each tool is a different, partial "window" into the same underlying process:

```text
ps                          → Who is running?
top / htop                   → What is consuming CPU/memory right now?
/proc                         → What information does Linux expose about this process?
lsof (optional)                → What files/resources does this process have open?
kill / signals                  → How can we safely observe/control lifecycle behavior?
ulimit / /proc/<pid>/limits       → What limits can affect the process?
echo $?                            → What result did the previous command return?
id / ls -l / stat                    → Who owns the resource and what permissions apply?
```

**This lesson is not a list of command definitions to memorize.** Every tool below is taught as a diagnostic instrument, answering a specific question about a process — and Section 21 teaches how professionals combine several of these instruments together, rather than trusting any single one in isolation.

---

## 2. Roadmap Tools: Linux, Ubuntu, WSL2, Bash, PowerShell

**Linux/Ubuntu** is this lesson's primary environment — every genuinely observed example below was captured on Ubuntu, running inside WSL2.

```text
Windows
   ↓
WSL2
   ↓
Linux distribution (Ubuntu)
   ↓
Linux processes and Linux OS tools
```

**You are observing genuine Linux processes, using genuine Linux tools, inside WSL2's Linux environment** (Concept 01's own WSL2 explanation, reused here) — **this lesson does not claim WSL2 is architecturally identical to a native, bare-metal Linux installation in every detail**; Section 20 returns to this precisely.

**Bash** is used for every primary command example in this lesson. **PowerShell** is given a concise, deliberate comparison (Section 18) — this lesson does not duplicate [Shell](13-shell.md)'s own, more complete PowerShell discussion.

---

## 3. `ps` — Process Snapshot

**What it is.** `ps` prints a **snapshot** — a single, one-moment-in-time listing — of currently running processes.

**Why "snapshot" matters, precisely:** the instant `ps` finishes printing, its information may already be stale — a process it showed as running could finish a millisecond later. This is exactly why Section 4 introduces `top` as a *live*, continuously refreshing complement to `ps`'s one-shot view.

**Useful invocations:**

```bash
ps
ps -f
ps -ef
ps -o pid,ppid,user,state,stat,%cpu,%mem,etime,cmd -p <pid>
ps --forest
```

**A genuinely observed illustration**, run against a disposable Python process created specifically for this lesson:

```text
$ ps -o pid,ppid,user,state,stat,%cpu,%mem,etime,cmd -p <pid>
    PID    PPID USER     S STAT %CPU %MEM     ELAPSED CMD
   7843    7841 sovon    S S     0.3  0.2       00:09 python3 observer.py
```

**What each column means:** `PID`/`PPID` (Concept 03/14's identity model); `USER` (the owning identity, Concept 08); `S`/`STAT` (process state — `S` for sleeping, Concept 14); `%CPU`/`%MEM` (Section 9–10); `ETIME` (elapsed wall-clock time since the process started); `CMD` (the command line that launched it).

**A required caveat:** `ps` options and column availability are not perfectly identical across every Unix-like system — the invocations above are specifically Linux/Ubuntu examples, exactly this lesson's stated scope (Section 2).

**What `ps` lets you answer directly:** what processes exist; who owns a given process; what its parent is; what state it's in; what command started it; roughly how much CPU/memory it's using right now; and, with `--forest`, its place in the process hierarchy (Section 16).

---

## 4. `top` — Live Process Observation

**What it is.** Unlike `ps`'s single snapshot, `top` shows a **continuously refreshing, live** view of running processes, typically ranked by CPU usage.

**A genuinely observed illustration** (captured in non-interactive batch mode, `-b -n 1`, filtered to a specific disposable PID):

```text
$ top -b -n1 | grep -E "PID|<pid>"
    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   7843 sovon     20   0   16056   9868   6752 S   0.0   0.3   0:00.02 python3
```

**What to look for:** the same `PID`/`USER`/`S`(tate)/`%CPU`/`%MEM` concepts `ps` already showed, now easily comparable *across every process at once*, refreshed continuously in interactive use. `VIRT`/`RES` are `top`'s names for virtual and resident memory (Concept 06, Section 10).

**How to identify, at a glance:** a **CPU-heavy process** (sustained high `%CPU`); a **memory-heavy process** (high `%MEM`/`RES`); a **sleeping process** (`S` state, near-`0%` CPU — exactly this genuinely observed example); a **running process** (`R` state); and a **suspiciously long-lived process** (an unusually large elapsed/`TIME+` value for something expected to be short-lived).

**This lesson does not teach advanced performance tuning.** `top` is an **observation** tool — it tells you *what's currently happening*, not automatically *why*, or how to fix it (Section 21's entire point).

---

## 5. `htop` — Interactive Process View (Optional)

**What it adds, conceptually, over `top`:** a more visual, interactive, typically color-coded process view, with easier scrolling, sorting, and even direct process selection/signaling from within the interface itself.

**A required, honest check — never assume it's installed:**

```bash
command -v htop
```

**Genuinely observed in this environment:** `htop` is **not installed** — consistent with every previous lesson in this module. **This lesson does not require installing it, and does not use `sudo` to do so.** `top` (Section 4) is fully sufficient for every observation this lesson needs, and every genuinely observed example in this lesson uses `top`, `ps`, or `/proc` specifically for that reason. If `htop` happens to be available in your own environment, everything Section 4 taught about `top` applies to it directly — the same underlying concepts, presented more interactively.

---

## 6. `/proc` — Linux Process Information

**This is one of the most important tools in this entire lesson.** `/proc` is a Linux **pseudo-filesystem** — Concept 02, Concept 07, and Concept 11 already introduced this concept — exposing **kernel-maintained** process and system information through ordinary-looking file paths, generated live, in memory, never stored on disk.

```text
/proc
/proc/<pid>
```

**Genuinely observed illustrations, from a disposable demo process:**

```bash
grep -E "^(Name|State|Pid|PPid|Threads|VmRSS|VmSize):" /proc/<pid>/status
```

```text
Name:	python3
State:	S (sleeping)
Pid:	7843
PPid:	7841
VmSize:	   16056 kB
VmRSS:	    9868 kB
Threads:	1
```

```bash
cat /proc/<pid>/cmdline | tr '\0' ' '
```

```text
python3 observer.py
```

```bash
cat /proc/<pid>/stat
```

```text
7843 (python3) S 7841 7843 7841 0 -1 4194304 980 0 0 0 2 0 0 0 20 0 1 0 1206701 16441344 2440 ...
```

```bash
grep -E "Max (open files|processes|stack size)" /proc/<pid>/limits
```

```text
Max stack size            8388608              unlimited            bytes
Max processes             15371                15371                processes
Max open files            1048576              1048576              files
```

**Connecting each file to what it reveals:** `status` — identity, state, memory (Concept 03, Concept 06, Concept 14); `cmdline` — the exact command line that launched it (Concept 13); `stat` — a dense, single-line, machine-oriented summary (state, PPID, and many further fields this lesson does not exhaustively decode — Section 33's scope boundary); `limits` — resource limits (Section 15).

**Why `/proc` is different from ordinary application data files:** nothing under `/proc` lives on a disk — it is generated by the kernel, on demand, the instant you read it, and reflects that process's *current*, live state (Concept 02's original introduction of this exact idea) — this is precisely why `VmRSS` in the example above will show a different value the next time you check it.

**Connecting `/proc` directly to concepts already learned:** the kernel (Concept 01) generates it; reading it is a system call (Concept 02) like any file read; it describes processes (Concept 03) and their filesystem-like resources (Concept 07); access to it is still subject to permissions (Concept 08); it reveals open file descriptors (Section 7) and resource limits (Section 15). **This lesson does not teach the complete `/proc` filesystem** — only the specific files that matter for process diagnosis.

---

## 7. File Descriptor Inspection

**Directly connecting to [Standard Input/Output](11-standard-input-output.md), without repeating that lesson.**

```text
0 → stdin
1 → stdout
2 → stderr
```

```bash
ls -l /proc/<pid>/fd
```

**Genuinely observed in this environment:**

```text
lr-x------ 1 sovon sovon 64 Sep 10 16:57 0 -> /dev/null
l-wx------ 1 sovon sovon 64 Sep 10 16:57 1 -> /tmp/.../scratchpad/os-tools-lab/observer2.log
l-wx------ 1 sovon sovon 64 Sep 10 16:57 2 -> /tmp/.../scratchpad/os-tools-lab/observer2.log
```

**What this shows:** exactly Concept 11's model, now observed directly — FD `0` (stdin) here points at `/dev/null` (this backgrounded process has no interactive input source); FD `1` and FD `2` (stdout and stderr) both point at the same redirected log file, since this demo process's output was captured with `> observer2.log 2>&1`. **Your own output will differ** — file descriptor targets depend entirely on how a specific process was started (Concept 11's own core point).

**`lsof` (optional, not a required Module 0.2 tool).** `lsof -p <pid>` shows the same open-file information in a different format, alongside additional detail this lesson does not require:

```bash
command -v lsof
lsof -p <pid>
```

**This lesson does not make `lsof` a required tool**, since it is not explicitly listed among Module 0.2's roadmap tools — `/proc/<pid>/fd`, demonstrated above, already provides everything this lesson needs, using only tools the roadmap explicitly requires.

---

## 8. Process State Inspection

```bash
ps -o pid,ppid,state,stat,cmd -p <pid>
```

Combined with `/proc/<pid>/status`'s own `State:` line (Section 6), this reveals exactly the states Concept 05 and Concept 14 already taught conceptually: **running**, **sleeping/waiting**, **stopped**, and **zombie**.

**Connecting state inspection directly to concepts already learned:** a sleeping state (Section 6's genuinely observed `S (sleeping)`) connects to Concept 05's scheduling model (not currently granted CPU time) and Concept 11/12's I/O-waiting model (blocked on input or a pipe); a stopped state (`T`) connects to Concept 10's `SIGSTOP`/`SIGTSTP`; a zombie state (`Z`) connects directly to Concept 14's own, genuinely observed zombie demonstration. **This lesson does not re-teach scheduling or process lifecycle in depth** — it teaches you the specific commands that reveal what those lessons already told you to expect.

---

## 9. CPU Inspection

```bash
ps -o pid,%cpu,cmd -p <pid>
top
htop   # if available
```

**What `%CPU` means:** roughly, the share of CPU capacity this process has recently been using (Concept 05's own scheduling model, applied here as an observable number).

**Why a high `%CPU` value does not automatically mean a bug:** a genuinely CPU-bound task (Concept 05's own category) is *supposed* to show high, sustained CPU usage — that alone is not evidence of a problem; the real question, addressed directly in Section 22's debugging scenarios, is whether that usage matches what the process is actually supposed to be doing right now.

**Why CPU percentage can change from one moment to the next:** because it reflects genuinely live, recent activity (Concept 05) — a process alternating between computing and waiting will show correspondingly fluctuating `%CPU` values across successive checks, entirely normally.

**This lesson does not teach advanced CPU performance analysis** — only how to observe this one number and interpret it cautiously.

---

## 10. Memory Inspection

```bash
ps -o pid,%mem,rss,vsz,cmd -p <pid>
top
cat /proc/<pid>/status | grep -E "VmRSS|VmSize"
```

**A genuinely observed illustration** (already shown in Section 6):

```text
VmSize:	   16056 kB
VmRSS:	    9868 kB
```

**Foundational concepts, directly reused from Concept 06:** **resident memory** (`RES`/`VmRSS`) — how much of this process's memory is *currently* actually occupying physical RAM; **virtual memory** (`VIRT`/`VmSize`) — the total size of this process's mapped virtual address space, which can be, and here genuinely is, larger than what's actually resident (Concept 06's own genuinely observed lesson, applying identically here).

**Why memory numbers can differ between tools:** `ps` and `top` sometimes label the same underlying values with slightly different column names (`RSS`/`RES`, `VSZ`/`VIRT`), and different tools may round or sample at slightly different moments — small discrepancies between two tools checked back-to-back are expected, not evidence of a problem (Section 21's tool-correlation discipline applies directly here).

**This lesson does not teach page tables, the TLB, or other virtual-memory internals** — Concept 06 already established the appropriate depth; this lesson only shows you where to *observe* the concepts that lesson taught.

---

## 11. `kill` and Process Termination

**Directly connecting to [Signals](10-signals.md) and [Process Lifecycle](14-process-lifecycle.md), without repeating either.**

```bash
kill <pid>
kill -TERM <pid>
kill -INT <pid>
kill -KILL <pid>
```

**A required, precise statement, restated from Concept 10 specifically because it matters this much: `kill` is fundamentally a signal-sending command — it does not always mean "forcefully terminate."**

```text
kill PID
    ↓
no signal specified
    ↓
default signal: SIGTERM             (a termination request, not an unconditional kill)
```

**The distinction between `SIGTERM`, `SIGINT`, and `SIGKILL`, restated briefly:** `SIGTERM` is a polite termination request a process can catch and handle (Concept 10); `SIGINT` is the same kind of request, conventionally generated by Ctrl+C; `SIGKILL` is enforced unconditionally by the kernel, with zero opportunity for the target to run any cleanup code at all. **This lesson does not repeat Concept 10's full signal treatment** — its job here is showing `kill` specifically as the *tool* you use to observe and manage lifecycle behavior in practice.

---

## 12. Safe `kill` Practices

**This is mandatory, and every demonstration in this lesson honors it exactly.**

**Every `kill` demonstration in this lesson targets only a disposable process created specifically for that demonstration.** Before ever sending a signal, this lesson's own practice, every time, is:

1. Capture the process's PID at the moment it's created.
2. Verify its command with `ps -p <pid> -o pid,cmd`.
3. Confirm this is genuinely the intended demo process.
4. Send the signal.
5. Verify its state/result afterward.
6. Clean up any temporary files.
7. Verify the process is actually gone.

**A genuinely observed illustration, following this exact sequence:**

```bash
ps -p "$PID" -o pid,cmd
```

```text
    PID CMD
   7843 python3 observer.py
```

```bash
kill -TERM "$PID"
ps -p "$PID"
```

```text
    PID TTY          TIME CMD
(no matching row)
```

**Never** signal PID `1`, any kernel/system process, an unknown process, another user's process, a production service, or any arbitrary PID you did not create specifically for a controlled demonstration. **This lesson never instructs you to run `kill -9 1` or any equivalent — nor does any legitimate diagnostic reason exist to do so in a learning context.**

---

## 13. Process Exit Codes

**Directly connecting to [Shell](13-shell.md) and [Process Lifecycle](14-process-lifecycle.md), without repeating either.**

```bash
echo $?
```

**Genuinely observed in this environment:**

```text
$ true
$ echo $?
0
```

**The convention, restated:** `0` commonly means success; non-zero commonly indicates some kind of failure or special condition, application-defined. **Exit status is part of the process lifecycle** (Concept 14) — it's produced at termination and observed (via `$?`, or a parent's `wait()`/`waitpid()`) afterward.

**Python's own exit-status mechanism, directly:**

```python
import sys
sys.exit(0)     # success
sys.exit(1)     # failure/problem, by convention
```

**This lesson introduces this only at the foundational level already established by Concept 13 and Concept 14** — its job here is naming `echo $?` specifically as the diagnostic *tool* you reach for to observe it.

---

## 14. Permission Inspection

**Directly connecting to [Permissions](08-permissions.md), without repeating that lesson.**

```bash
id
whoami
groups
ls -l
stat
```

**Genuinely observed in this environment:**

```text
$ id
uid=1000(sovon) gid=1000(sovon) groups=1000(sovon),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users)
$ whoami
sovon
$ groups
sovon adm cdrom sudo dip plugdev users
```

**How permissions affect process diagnosis specifically, not just file access generally:** the identity `id` reports is exactly what determines whether you're even permitted to inspect **another** user's process at all — some `/proc/<pid>/` entries and some `ps` columns can be restricted for processes you don't own (Concept 08's ownership model, applied to process inspection itself, not just files); signaling a process (Section 11–12) is likewise subject to this same identity check (Concept 10's own "signals and permissions" connection). **This lesson does not teach advanced Linux security** — only that permission checks apply to *diagnostic* actions too, not only to ordinary file access.

---

## 15. Resource Limit Inspection

**The roadmap explicitly requires this.**

```bash
ulimit -a
cat /proc/<pid>/limits
```

**Genuinely observed in this environment:**

```text
$ ulimit -a | grep -E "open files|max user processes|stack size"
open files                          (-n) 1048576
stack size                  (kbytes, -s) 8192
max user processes                  (-u) 15371
```

```text
$ cat /proc/<pid>/limits
Max stack size            8388608              unlimited            bytes
Max processes             15371                15371                processes
Max open files            1048576              1048576              files
```

**What resource limits are.** OS-enforced ceilings on how much of a given resource a process (or user) may consume — here, the maximum number of simultaneously open files, the maximum stack size, and the maximum number of processes a user may run at once.

**Why limits exist:** to keep any single process or user from unintentionally (or maliciously) exhausting a shared resource and starving everything else on the system (Concept 01's own broader resource-protection theme, applied concretely here).

**Why a process can fail because of a limit, and why this matters for production reliability:** a process that tries to open more files than `Max open files` allows, or that recurses deeply enough to exceed `Max stack size`, will fail — not because its own logic is wrong, but because it hit an OS-enforced ceiling. Recognizing this as a *distinct* failure category (rather than assuming a code bug) is directly useful production-debugging reasoning (Section 22's Scenario 7).

**A required distinction, precisely:** `ulimit -a` reports limits for the **current shell** (and processes it subsequently creates); `/proc/<pid>/limits` reports the **actual, specific limits already in effect for that one existing process** — two related but genuinely different views. **This lesson does not teach cgroups, containers, or Kubernetes resource limits** (Section 33's scope boundaries) — those are later, more advanced systems built on top of exactly this OS-level foundation.

---

## 16. Process Tree Observation

```bash
ps --forest -o pid,ppid,stat,cmd
pstree -p <pid>
```

**Genuinely observed in this environment:**

```text
$ pstree -p 1092
Relay(1095)(1092)---bash(1095)---claude(1358)-+-bash(7819)-+-head(7822)
                                              |            `-pstree(7821)
                                              |-{claude}(1360)
                                              |-{claude}(1372)
                                              ...
```

**What to read from this:** every process is nested under its parent, forming a **process hierarchy** (Concept 03, Concept 14) — a shell's own child commands appear directly beneath it, and `{claude}(1360)`-style entries mark **threads** (Concept 04) belonging to a process, distinct from genuine child processes. **If `pstree` isn't installed in your environment, `ps --forest` provides equivalent information without requiring any installation** — check with `command -v pstree` first (Section 17), exactly this lesson's own required habit.

**Why this connects directly to a genuinely observed detail from this lesson's own lab:** one of this lesson's disposable demo processes was found, moments after creation, already reparented to PID `1092` (`/init`) rather than its original launching shell — **exactly Concept 14's orphan concept**, observed here purely as a side effect of how this lesson's own tooling manages background processes across separate command invocations, not something deliberately engineered. This is a genuine, honest illustration that process-tree observation can reveal lifecycle events (Concept 14) you didn't necessarily set out to demonstrate.

---

## 17. Checking Command Availability

**A required habit, honored throughout this entire lesson: never assume a tool is installed.**

```bash
command -v ps
command -v top
command -v htop
command -v pstree
command -v lsof
```

**Genuinely observed in this environment:** `ps`, `top`, `pstree`, and `lsof` are all available; `htop` is not (Section 5).

**Required vs. optional tools, precisely:** `ps`, `top`, `kill`, and `/proc` are the roadmap's explicitly required tools (Section 2) — every genuinely observed example in this lesson relies only on these, plus ordinary shell builtins (`echo $?`, `id`, `ls -l`, `ulimit`). `htop`, `pstree`, and `lsof` are genuinely useful, but **this lesson never depends on any of them being installed**, and never instructs you to install anything with `sudo` merely to complete this lesson.

---

## 18. PowerShell Comparison

A concise, deliberate comparison — **this lesson does not duplicate [Shell](13-shell.md)'s own PowerShell discussion.**

| Linux / Bash | PowerShell concept |
|---|---|
| `ps` | `Get-Process` |
| `kill <pid>` | `Stop-Process -Id <pid>` |
| `echo $?` | `$LASTEXITCODE` |
| `/proc/<pid>/*` | No direct equivalent — PowerShell exposes process information through cmdlet output (`Get-Process`), not a filesystem-like interface |
| environment inspection | `Get-ChildItem Env:` (Concept 09's own genuinely observed PowerShell example) |

**A required, precise statement: PowerShell does not provide an identical `/proc` interface.** Linux process inspection is this lesson's primary focus, exactly as stated in Section 2 — PowerShell has genuinely different underlying abstractions and commands. **The underlying process *concepts* (identity, state, resource usage, termination, exit status) still map conceptually across both** — only the specific tools and their exact output differ.

---

## 19. Practical OS / Process Observation Lab

All commands below are safe, use only a disposable Python process created specifically for this lab, and were genuinely executed while preparing this lesson. No `sudo` is required, no system process is ever touched, and every temporary file was created in an isolated directory and fully removed afterward.

**Create the demo process yourself**, only inside a disposable directory such as `/tmp/os-tools-lab/` — **this lesson does not create it for you automatically**:

```bash
mkdir -p /tmp/os-tools-lab && cd /tmp/os-tools-lab
cat > observer.py << 'EOF'
import os
import time

print(f"Starting. PID={os.getpid()} PPID={os.getppid()}", flush=True)
total = sum(range(2_000_000))
print(f"work result: {total}", flush=True)
time.sleep(20)
print("done sleeping", flush=True)
EOF

python3 observer.py > observer.log 2>&1 &
echo "PID: $!"
```

### Lab 1 — Find the process

```bash
ps
```

**Expected pattern:** a row showing `python3 observer.py` among the current processes.

### Lab 2 — Identify PID and PPID

```bash
ps -o pid,ppid,user,state,stat,cmd -p <pid>
```

**Genuinely observed in this environment:**

```text
    PID    PPID USER     S STAT %CPU %MEM     ELAPSED CMD
   7843    7841 sovon    S S     0.3  0.2       00:09 python3 observer.py
```

### Lab 3 — Inspect the process tree

```bash
ps --forest -o pid,ppid,stat,cmd -p <pid>
```

or, if available, `pstree -p <ppid>` (Section 16).

### Lab 4 — Observe live CPU/memory

```bash
top -b -n1 | grep -E "PID|<pid>"
```

**Genuinely observed in this environment:** `%CPU 0.0`, `%MEM 0.3`, state `S` — consistent with a process currently sleeping (Section 8), not actively computing.

### Lab 5 — Inspect `/proc`

```bash
cat /proc/<pid>/status | grep -E "Name|State|PPid|VmRSS"
cat /proc/<pid>/cmdline
cat /proc/<pid>/limits | grep -E "Max open files|Max processes"
```

**Genuinely observed in this environment** — the complete result already shown in full in Section 6.

### Lab 6 — Inspect file descriptors

```bash
ls -l /proc/<pid>/fd
```

**Genuinely observed in this environment** — the complete result already shown in full in Section 7.

### Lab 7 — Observe process state

```bash
ps -o pid,ppid,state,stat,cmd -p <pid>
```

Already demonstrated in Lab 2; repeated here specifically to confirm state (Section 8) after any of the previous steps.

### Lab 8 — Observe exit status

```bash
true
echo $?
```

**Genuinely observed in this environment:** `0` (Section 13).

### Lab 9 — Observe signal-driven lifecycle

**Following Section 12's required safety sequence exactly:**

```bash
ps -p <pid> -o pid,cmd     # verify identity first
kill -TERM <pid>
ps -p <pid>                 # verify termination
```

**Genuinely observed in this environment:** the process's command was confirmed (`python3 observer.py`), `SIGTERM` was sent, and the follow-up `ps -p <pid>` returned no matching row — confirming clean termination, with no need to escalate to `SIGKILL` (Concept 10's own escalation discipline, honored here).

### Lab 10 — Resource limits

```bash
ulimit -a | grep -E "open files|max user processes|stack size"
cat /proc/<pid>/limits | grep -E "Max open files|Max processes|Max stack size"
```

**Genuinely observed in this environment** — the complete result already shown in full in Section 15. **`ulimit -a`** reflects your *current shell's* configured limits; **`/proc/<pid>/limits`** reflects the limits already in effect for one *specific, existing* process — related, but not identical, views (Section 15).

### Cleanup

```bash
cd /
rm -rf /tmp/os-tools-lab
```

**Genuinely observed in this environment:** every temporary script, log file, and directory used throughout this lab was created in an isolated location and fully removed afterward, with removal verified — no project file, system file, or unrelated process was ever touched.

**A required labeling reminder, honored throughout this entire lesson:** every block above marked "Genuinely observed in this environment" reflects real output captured while preparing this lesson. **Your own PIDs, timestamps, memory figures, and exact numeric values will differ — this is expected, not a discrepancy to worry about.**

---

## 20. WSL2-Specific Lab Guidance

```text
Windows
   ↓
WSL2
   ↓
Ubuntu/Linux
   ↓
Linux process
```

**Every command in this lesson's lab (Section 19) runs inside this Linux/WSL2 environment specifically.** `ps`, `top`, and `/proc` are observing **Linux** processes managed by WSL2's own Linux kernel (Concept 01) — **not** Windows processes.

**A required, precise statement: Windows Task Manager and Linux `ps` observe genuinely different layers/environments.** A process you start inside WSL2 (like this lesson's own `observer.py`) will **not** appear in Windows Task Manager as a directly recognizable, equivalently-identified entry — Windows sees WSL2 itself as a managed environment, not a window into every individual Linux process running inside it. **Linux PIDs inside WSL2 should never be assumed to directly correspond to Windows process IDs** — they belong to entirely separate process-numbering spaces, managed by separate kernels. **This lesson does not turn into a WSL2 architecture course** — only this practical caveat, directly relevant to correctly interpreting what you observe.

---

## 21. How Engineers Correlate OS Tools

**Professional diagnosis rarely comes from one command.**

```text
Symptom:
"Python AI service is slow."

        ↓

ps
        ↓
Find PID and current CPU/memory

        ↓

top
        ↓
Observe whether CPU/memory is persistently high

        ↓

/proc/<pid>/status
        ↓
Inspect process state and memory information

        ↓

/proc/<pid>/fd
        ↓
Inspect open descriptors

        ↓

/proc/<pid>/limits
        ↓
Inspect resource limits

        ↓

signals / lifecycle
        ↓
Determine whether the process is stuck, stopped, waiting, or terminating
```

**This is evidence-based debugging, not guessing.** Each tool in this chain answers one specific question; none of them, alone, tells you "the problem is X" — the *engineer*, correlating what several tools independently report, forms and verifies that conclusion (Section 22 applies this method directly, scenario by scenario).

---

## 22. Realistic Debugging Scenarios

For every scenario: symptom, evidence to collect, tool, interpretation, hypothesis, verification, and safe remediation.

**Scenario 1 — Python service using too much CPU.** *Symptom:* sustained high `%CPU`. *Evidence:* `ps -o pid,%cpu,cmd`, then `top` over a short interval to confirm it's sustained, not a brief spike. *Interpretation:* a `%CPU` value staying consistently high across several checks (Section 9) suggests genuine, ongoing computation. *Hypothesis:* either legitimate heavy work, or an unintended loop. *Verification:* compare against what the service should be doing right now (is it actively serving a large batch, or supposedly idle?). *Remediation:* investigate the application's own logic if the usage doesn't match expected behavior — this lesson's tools identify *where* to look, not the code-level fix itself.

**Scenario 2 — Python service using too much memory.** *Evidence:* `ps -o pid,%mem,rss`, `top`, `/proc/<pid>/status`'s `VmRSS` (Section 10), checked repeatedly over time. *Interpretation:* memory that grows and then stabilizes (matching a data-loading phase, for example) is expected; memory that grows without bound, uncorrelated with actual workload, is a stronger leak signal (Concept 06's own debugging guidance). *Verification:* correlate growth with specific application events. *Remediation:* application-level investigation, guided by exactly where the observed growth began.

**Scenario 3 — Process appears stuck.** *Evidence:* process state (`ps`'s `STAT`, `/proc/<pid>/status`'s `State:`) — Section 8. *Interpretation:* a sleeping/waiting state (`S`) suggests it's blocked on I/O or an event (Concept 05/11/12), not necessarily broken; a running state (`R`) with no progress suggests a genuine infinite loop instead. *Verification:* check what it's plausibly waiting for — a pipe, a socket, a file — given what the process is supposed to be doing. *Remediation:* depends entirely on which of the two categories the evidence points to.

**Scenario 4 — Process exited unexpectedly.** *Evidence:* exit status (`echo $?`, or a parent's own recorded result — Section 13), the exact command line that started it (`/proc/<pid>/cmdline` while it was still running, or logs), and its parent relationship (Section 16). *Interpretation:* a non-zero exit status (Concept 03/13/14) indicates the specific kind of failure, by whatever convention the program itself uses. *Verification:* check the process's own output/logs (referenced here only conceptually — this lesson does not teach logging frameworks) for the actual error. *Remediation:* application-level, guided by the exit status and any captured diagnostic output.

**Scenario 5 — Zombie process.** *Evidence:* `ps`'s `STAT` showing `Z`, `CMD` showing `<defunct>` — exactly Concept 14's own genuinely observed pattern. *Interpretation:* the process has already finished; its parent hasn't yet collected its exit status (Concept 14). *Verification:* check the parent's own PID (`PPID`) and whether it's designed to call `wait()`/`waitpid()` at all. *Remediation:* a fix belongs in the *parent's* code, not the (already-finished) zombie itself — exactly Concept 14's own production-failure-mode guidance.

**Scenario 6 — Permission-related failure.** *Evidence:* `id` (your own identity), `ls -l` and `stat` on the relevant file/resource (Concept 08). *Interpretation:* compare the owning identity and permission bits against your own identity's category (owner/group/others, Concept 08). *Verification:* confirm the specific permission bit (read/write/execute) actually required for the failing operation. *Remediation:* grant the minimal necessary permission to the correct identity (Concept 08's own guidance against overly broad fixes).

**Scenario 7 — Process cannot use an expected resource.** *Evidence:* `cat /proc/<pid>/limits` (Section 15). *Interpretation:* compare the resource actually being requested (an open file, a new subprocess) against the corresponding limit column. *Verification:* confirm the failure occurs specifically once that limit is reached, not for an unrelated reason. *Remediation:* recognizing a limit-driven failure as its own category — distinct from a code bug — is this scenario's entire point.

---

## 23. AI Engineering Relevance

Every tool in this lesson applies directly to real AI workloads: Python API services, LLM inference services, embedding workers, document-processing workers, batch inference processes, evaluation processes, agent workers, model-loading processes, and background task workers.

```text
Python process
      ↓
PID                       (Section 3, Section 6)
      ↓
CPU                        (Section 9)
      ↓
RAM                         (Section 10)
      ↓
Open files / sockets conceptually  (Section 7)
      ↓
Process state                        (Section 8)
      ↓
Signals                                (Section 11–12, Concept 10)
      ↓
Exit status                              (Section 13)
```

**Questions this exact toolkit lets an AI engineer answer directly:**

- **Is the service alive?** — `ps -p <pid>` (Section 3).
- **Which PID is the service?** — `ps` combined with the command line (Section 3, Section 6).
- **Is it CPU-bound?** — `top`/`ps`'s `%CPU` (Section 9).
- **Is it memory-heavy?** — `top`/`ps`'s `%MEM`, `/proc/<pid>/status`'s `VmRSS` (Section 10).
- **Is it sleeping/waiting?** — process state (Section 8).
- **Did it exit?** — `ps -p <pid>` returning nothing, plus its recorded exit status (Section 13).
- **What was its parent?** — `PPID` (Section 3, Section 16).
- **Is it a zombie?** — `STAT Z` / `<defunct>` (Section 8, Section 22's Scenario 5).
- **Is it hitting resource limits?** — `/proc/<pid>/limits` (Section 15).
- **Is it responding to termination signals?** — sending `SIGTERM` safely (Section 12) and observing the result.

**This lesson does not teach GPU-specific monitoring tools** — GPU tooling is a later, dedicated topic; everything here applies to the CPU-side process management every AI workload still depends on, GPU-accelerated or not (Concept 05's own "CPU still matters" point, reused here).

---

## 24. Production Mental Model

```text
Production AI Service
        ↓
Operating-system process
        ↓
PID / PPID
        ↓
CPU / Memory
        ↓
Files / File Descriptors / I/O
        ↓
Environment / Permissions
        ↓
Signals
        ↓
Lifecycle
        ↓
Exit status
        ↓
OS-level observability
```

**These tools are not merely commands to memorize — they are observation interfaces for understanding real system behavior.** Every row in this diagram corresponds to a Module 0.2 lesson, and every one of them is now directly observable using the specific commands this lesson taught.

---

## 25. Common Misconceptions

| Misconception | Why it's wrong |
|---|---|
| "`ps` continuously monitors processes." | `ps` produces a single **snapshot**, not a live, ongoing view — `top` is the live-observation tool (Section 3–4). |
| "`top` tells you everything about a process." | `top` shows CPU/memory/state at a glance, but not file descriptors, resource limits, or the full identity detail `/proc` provides (Section 21's whole point). |
| "`kill` always means force-kill." | `kill` sends a signal — by default `SIGTERM`, a request, not an unconditional kill (Section 11, Concept 10). |
| "PID is the same as PPID." | A PID identifies a process itself; a PPID identifies its **parent** — different values (Section 3, Section 16). |
| "`/proc` contains ordinary persistent files." | `/proc` is a kernel-generated virtual filesystem — nothing under it is stored on disk (Section 6). |
| "`/proc/<pid>` is the application's own directory." | It's a kernel-provided *view* of that process, not something the application itself created or controls (Section 6). |
| "High CPU always means a bug." | Genuine, expected computation also produces high CPU usage (Section 9, Section 22's Scenario 1) — the number alone doesn't distinguish the two. |
| "Low CPU means a process is healthy." | A process stuck waiting on something that will never resolve can also show near-zero CPU (Section 22's Scenario 3) — low usage alone doesn't guarantee health. |
| "Sleeping means the process is dead." | Sleeping (`S`) is a normal, expected waiting state (Section 8, Concept 14) — the process is fully alive. |
| "A zombie process is still executing." | A zombie has already finished executing entirely — only its exit-status bookkeeping remains (Section 22's Scenario 5, Concept 14). |
| "`htop` is required for Linux process management." | `htop` is optional and, in this lesson's own environment, genuinely not even installed — `ps`/`top` are fully sufficient and are the roadmap's actual required tools (Section 5, Section 17). |
| "`lsof` is a core Module 0.2 roadmap requirement." | `lsof` is a useful, optional tool this lesson explicitly does not require — `/proc/<pid>/fd` covers the same need using only roadmap-required tools (Section 7). |
| "Windows Task Manager and Linux `ps` are observing exactly the same process layer in WSL2." | They observe genuinely different environments — Windows processes versus Linux processes managed by WSL2's own kernel (Section 20). |
| "Exit code `0` guarantees the application is correct." | `0` conventionally means the process didn't detect a failure it chose to report — it does not guarantee the *result* was actually correct in every sense (Concept 13/14's own convention, restated). |
| "A process consuming memory is automatically leaking memory." | Legitimate, expected memory growth (loading data, building a cache) looks identical to a leak at a single glance — correlating growth with actual workload (Section 22's Scenario 2) is what actually distinguishes them. |
| "`/proc/<pid>/status` provides the complete internal state of the process." | It exposes a specific, kernel-chosen set of fields (Section 6) — not the process's own internal application-level variables or logic. |
| "Sending SIGKILL is equivalent to graceful shutdown." | `SIGKILL` allows zero cleanup opportunity, the direct opposite of graceful shutdown (Concept 10, Concept 14). |
| "More diagnostic commands automatically mean better diagnosis." | Evidence must be correctly interpreted and correlated (Section 21) — running many commands without a clear question in mind produces noise, not necessarily insight. |

---

## 26. Exercises

Work through these in your own words. No answer key exists for this lesson — the goal is reasoning ability, not matching a memorized phrase.

### Level 1 — Recognition

1. What does `ps` show? What does `top` add beyond `ps`?
2. What is `/proc`? What is `/proc/<pid>`?
3. What is the difference between a PID and a PPID?
4. What does the `STAT`/`State` field tell you about a process?
5. What does `%CPU` represent?
6. What is the difference between `VmSize` and `VmRSS`?
7. What does `echo $?` show?
8. What does `ulimit -a` show, and how does it differ from `/proc/<pid>/limits`?

### Level 2 — Understanding

9. Explain why `ps` is described as a "snapshot" tool.
10. Explain why `top` is useful even though `ps` already exists.
11. Explain why `/proc` is valuable for process diagnosis.
12. Explain why no single tool in this lesson gives a complete diagnosis on its own.
13. Explain the difference between a process's virtual memory size and its resident memory size.
14. Explain why a sleeping process is not the same as a dead process.
15. Explain how `kill` relates to signals, and why its name is potentially misleading.
16. Explain why resource limits can cause a failure that isn't a code bug.

### Level 3 — Application

17. In your own WSL2 terminal, find a running process with `ps` and record its PID.
18. Inspect that process's PID/PPID/state with `ps -o pid,ppid,state,stat,cmd`.
19. Inspect its CPU/memory with `top -b -n1 | grep <pid>`.
20. Inspect `/proc/<pid>/status`, `/proc/<pid>/cmdline`, and `/proc/<pid>/limits` for a disposable process you create yourself.
21. Inspect that same process's open file descriptors with `ls -l /proc/<pid>/fd`.
22. Check `id`, `whoami`, and `groups` in your own terminal.
23. Check `ulimit -a` and identify at least two limit values.
24. Following Section 12's safety sequence, safely terminate a disposable process you created and verify its termination.

### Level 4 — Debugging

25. A Python service shows sustained high `%CPU`. Using Section 22's Scenario 1, describe your investigation steps.
26. A Python service's memory keeps growing. Using Scenario 2, explain how to distinguish expected growth from a leak.
27. A process shows no progress and no crash. Using Scenario 3, explain how to determine whether it's legitimately waiting or truly stuck.
28. A process exited, and you want to know why. Using Scenario 4, list the evidence you'd collect.
29. `ps` shows a process with `STAT Z`. Using Scenario 5, explain the root cause and where the actual fix belongs.
30. A command fails with a permissions error. Using Scenario 6, describe your diagnostic steps.
31. A process fails after opening many files. Using Scenario 7, explain how `/proc/<pid>/limits` would confirm this.
32. Two different tools report slightly different memory values for the same process. Using Section 10, explain why this is expected.

### Level 5 — Integration

33. Design a short, step-by-step investigation plan for the symptom "AI inference service is slow," using at least four different tools from this lesson, referencing Section 21's correlation method.
34. A friend claims, "I checked `top` once and the CPU looked fine, so the service must be healthy." Using Section 25's misconceptions, explain what's incomplete about this conclusion.
35. Explain how a `/proc/<pid>/fd` inspection (Section 7) and Concept 12's pipe model together would help you diagnose a data-processing pipeline stage that appears stuck.
36. A production Python worker occasionally becomes a zombie under heavy load. Using Section 22's Scenario 5 and Concept 14's own production-failure-mode guidance, explain what you'd inspect and where the actual fix belongs.
37. Using everything in this lesson, explain to a beginner (in your own words, as if teaching them) why "I can start a Python service" and "I can tell you exactly what that service is doing right now" are different skills — and which specific tools close that gap.

---

## 27. Mini-Project: Python Service OS-Level Observer

**Objective.** Manually create a small Python process and investigate it exactly as if it were a simple production service, producing a short diagnostic report.

**Workflow:**

```text
Start process
↓
Identify PID
↓
Identify PPID
↓
Inspect process tree
↓
Observe CPU/memory
↓
Inspect /proc
↓
Inspect file descriptors
↓
Inspect resource limits
↓
Observe lifecycle state
↓
Send safe termination signal
↓
Verify exit
↓
Record findings
```

**Create the process yourself**, only inside a disposable directory such as `/tmp/os-tools-lab/` (Section 19 already showed the exact script and commands to reuse here) — **this lesson does not create project files automatically.**

**Your diagnostic report should record:**

- **Process identity** — PID, command line (`/proc/<pid>/cmdline`).
- **Parent relationship** — PPID, and what process that actually is.
- **State** — running/sleeping/stopped, from `ps`/`/proc/<pid>/status`.
- **CPU observation** — `%CPU` from `top`/`ps`, and whether it matches expected behavior.
- **Memory observation** — `VmRSS`/`VmSize` or `RES`/`VIRT`, and whether they seem reasonable for what the script is doing.
- **Open descriptor observation** — `ls -l /proc/<pid>/fd`, and what each one is connected to.
- **Resource-limit observation** — at least two relevant limits from `/proc/<pid>/limits`.
- **Termination behavior** — the exact signal sent, and confirmation of clean termination.
- **Final diagnosis** — one paragraph, in your own words, describing this process's complete observed lifecycle from your own evidence.

**Safety requirements**, exactly as throughout this lesson: use only a disposable process you created; verify its PID/command before signaling it; clean up all temporary files; verify cleanup. **Do not require Docker, Kubernetes, systemd, or any external infrastructure** — everything needed is a single Python script and the tools this lesson already covered.

---

## 28. Review

- What problem does `ps` solve? What is the difference between `ps` and `top`?
- What does `htop` add, and why is this lesson's own environment a genuine example of not needing it?
- What is `/proc`? Why is `/proc/<pid>` useful?
- What are PID and PPID?
- How do you inspect process state, CPU usage, and memory usage?
- How do you inspect file descriptors? How do you inspect resource limits?
- What does `kill` actually do?
- How do signals connect to process lifecycle?
- How do you inspect an exit status?
- How do permissions affect process diagnosis?
- Why should multiple tools be correlated, rather than trusted individually?
- How would you investigate a stuck Python service? A high-memory Python service? A process that exited unexpectedly?

---

## 29. Interview / Architecture Questions

- What does `ps` do, and why is it considered a snapshot?
- What is the difference between `ps` and `top`?
- What is `/proc`, and why does Linux expose process information this way?
- How would you find the PID of a Python service, and determine its parent process?
- How would you determine whether a process is running or sleeping?
- How would you investigate high CPU usage? High memory usage?
- How would you inspect open file descriptors? Process limits?
- What is the relationship between `kill` and signals?
- How would you safely terminate a process?
- What is an exit status, and how would you investigate a zombie process?
- Why is one diagnostic tool rarely sufficient on its own?
- How would you investigate an unhealthy AI inference worker?
- What evidence would you collect before restarting a production process?

**For architecture-style questions, reason explicitly about:** what evidence each tool actually provides versus what it cannot tell you (Section 21), the cost/benefit of checking multiple sources before acting, and why jumping straight to a restart without collecting evidence first can hide the actual root cause.

---

## 30. Production Application

```text
Alert:
"AI inference service is slow"

        ↓

Identify process              →  ps
        ↓

Observe CPU / memory          →  top / htop
        ↓

Inspect process state         →  ps, /proc/<pid>
        ↓

Inspect resources             →  /proc/<pid>/status, /proc/<pid>/limits
        ↓

Inspect file descriptors      →  /proc/<pid>/fd
        ↓

Inspect lifecycle/signals     →  process lifecycle knowledge (Concept 14)
        ↓

Form evidence-based hypothesis
        ↓
Verify
        ↓
Take appropriate engineering action
```

**The essential engineering mindset this lesson leaves you with:** **OS tools provide evidence. They do not automatically provide the diagnosis.** Every tool in this lesson answers a specific, narrow question; turning that evidence into a correct conclusion is still the engineer's own reasoning, exactly as Section 21 and Section 22 demonstrated repeatedly.

---

## 31. Relationship to Module 0.2

| Module 0.2 Concept | Tool / Observation | What the learner sees |
|---|---|---|
| Kernel | `/proc` | Kernel-exposed process information (Section 6) |
| User space | every tool in this lesson | User-space observation interfaces, not kernel-internal access |
| System calls | tools, conceptually | The *effects* of OS interactions (file reads, process creation) made visible |
| Processes | `ps`, `top` | Process identity/state (Section 3–4) |
| Threads | `ps`/`pstree` | Thread entries alongside processes, at a basic level (Section 16) |
| Scheduling | `top`, process state | CPU usage and runnable/waiting behavior (Section 9) |
| Virtual memory | `ps`, `/proc` | `VIRT`/`RES`, `VmSize`/`VmRSS` (Section 10) |
| Filesystems | `/proc`, `ls`, `stat` | Filesystem/process resource relationships (Section 6–7) |
| Permissions | `id`, `ls -l`, `stat` | Ownership/access (Section 14) |
| Environment variables | shell/Python inspection | Process configuration context (Concept 09, not repeated here) |
| Signals | `kill` | Lifecycle control (Section 11–12) |
| Standard I/O | `/proc/<pid>/fd` | File descriptors (Section 7) |
| Pipes | file-descriptor inspection | Process communication relationships (Section 7, Section 16) |
| Shell | `ps`, process tree | Shell → child process (Section 16) |
| Process lifecycle | `ps`, `kill`, exit status | Creation → running → waiting → termination (Section 8, 11, 13, 22's Scenario 5) |

**This table does not re-teach any of these concepts** — every one was already fully covered in its own dedicated lesson; this lesson's contribution was showing you exactly how to *observe* each one in a genuinely running process.

---

## 32. Final Integrated Mental Model

```text
Concepts
   ↓
Operating System
   ↓
Running Process
   ↓
OS-maintained state/resources
   ↓
Diagnostic tools
   ↓
Evidence
   ↓
Interpretation
   ↓
Debugging
   ↓
Engineering decision
```

```text
Python AI Service
       ↓
Linux Process
       ↓
PID / PPID
       ↓
CPU / Memory
       ↓
Files / FDs / I/O
       ↓
Permissions / Environment
       ↓
Signals
       ↓
Lifecycle
       ↓
Exit Status
       ↓
OS-Level Diagnosis
```

**The single idea to carry forward from this lesson, and from Module 0.2 as a whole:** an Applied AI Engineer should not only know how to *start* an AI service. **They should be able to inspect what that service is doing at the operating-system level** — its identity, its resource usage, its state, its lifecycle — using exactly the small, focused set of tools this lesson taught: `ps`, `top`, `/proc`, `kill`, `echo $?`, `id`, `ulimit`. None of them are complicated in isolation; their real power, as Section 21 and Section 22 demonstrated repeatedly, comes from correlating what several of them show you into one coherent, evidence-based understanding of a real, running process.

---

## 33. Scope Boundaries

This lesson is a foundational OS/process-tools overview. It deliberately does **not** teach, in depth:

- Advanced kernel internals or kernel debugging
- Scheduler implementation or advanced scheduling algorithms (Concept 05 already covers the appropriate depth)
- Page tables, TLB, advanced memory profiling (Concept 06)
- Filesystem internals, advanced permissions, ACLs, SELinux, AppArmor (Concept 07–08)
- Advanced signal internals, advanced IPC (Concept 10, Concept 12)
- Advanced thread debugging, pthread internals (Concept 04)
- Advanced shell scripting (Concept 13)
- Networking diagnostics, packet analysis
- Docker internals, Kubernetes, cgroups, namespaces
- Distributed systems
- GPU monitoring
- Advanced observability platforms

Each is mentioned only where it directly clarifies a boundary of what this lesson does cover — every one belongs to later modules and stages, built directly on top of the OS/process fundamentals this lesson, and all of Module 0.2, just established.

---

_This file is the completed lesson for Concept 15, and completes Module 0.2 — Operating System Fundamentals. It intentionally does not teach advanced kernel internals, scheduler implementation, memory/filesystem/permission internals, advanced signal or IPC internals, advanced shell scripting, networking diagnostics, container/Kubernetes internals, or distributed systems in depth — those remain the subject of later stages of the roadmap, not this beginner-level foundation._
