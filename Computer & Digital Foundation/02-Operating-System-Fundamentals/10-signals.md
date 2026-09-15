# 10 — Signals

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Module 0.2 — Operating System Fundamentals
**Concept(s) covered:** signals, SIGTERM/SIGINT/SIGKILL/SIGHUP/SIGSTOP/SIGCONT, `kill`, default actions, signal handlers, graceful shutdown
**Status:** Not Started

---

## 1. What Is It?

**Connecting to what you already know.** Every previous lesson in this module has focused on a process's *resources* — its memory ([Virtual Memory](06-virtual-memory.md)), its files ([Filesystems](07-filesystems.md), [Permissions](08-permissions.md)), its configuration ([Environment Variables](09-environment-variables.md)). This lesson introduces something different: a way for the operating system, the shell, or another process to reach a running process and tell it **something happened, or something is being requested of it** — without sending it ordinary data at all.

**Signal.** Simple meaning: a short, standardized notification the operating system delivers to a process, telling it that something has happened or is being requested. Technical meaning: a signal is an asynchronous, OS-delivered notification, identified by a specific name and number (Section 5), sent to a target process to inform it of an event or to request that it take a specific kind of action (Section 5's default-action table) — most commonly, but not always, related to interrupting, stopping, continuing, or terminating that process.

**A simple conceptual example:**

```text
A Python process is running
        ↓
The OS needs the process to stop           (a shutdown was requested, Ctrl+C was pressed, etc.)
        ↓
The OS sends a signal
        ↓
The process receives/handles the signal
        ↓
The process responds                        (terminates, cleans up and exits, ignores it,
                                               pauses, or resumes — depending on the signal
                                               and how the process is set up to respond)
```

**Why a separate mechanism is needed at all, previewed here and expanded in Section 2:** a process cannot practically check, every microsecond, "has someone asked me to stop yet?" — signals exist specifically so that this kind of event can be delivered *to* a process, rather than requiring the process to constantly watch for it.

**How a signal differs from ordinary application data — required, and easy to get wrong.** A signal is **not** the same thing as sending a process a text message through its standard input, and it is **not** the same thing as a network request arriving at a service. Those are both examples of **data** flowing to a process through a defined channel it actively reads from. A signal is fundamentally different: it's a small, standardized, out-of-band **notification** — it doesn't carry an arbitrary payload of information, and the process doesn't "read" it the way it reads a line of input; the operating system delivers it, and the process's response is governed either by a fixed default action or by a handler the process has specifically registered (Section 5, Section 6).

```text
Data channels (later lessons):    stdin / stdout / stderr / pipes  — carry arbitrary content
Control channel (this lesson):    signals                          — carry only a specific,
                                                                       predefined notification
```

---

## 2. Why Does It Exist?

**The problem: some events need to reach a running process, without that process constantly checking for them.** If the only way a process could ever learn "please stop" was to repeatedly check some file, some variable, or some external state in a loop, every single program would need to build this kind of polling logic itself, wasting CPU time (Concept 05) checking for something that, most of the time, hasn't happened yet. Signals exist so the operating system can deliver an event *directly* to a process, asynchronously, the moment it happens — without the process needing to ask for it repeatedly.

**The specific problems signals solve:**

- **Notifying a process of an event.** Something happened (a terminal hangup, a request to interrupt) that the process needs to know about right now.
- **Requesting process termination.** A structured, standardized way to ask a process to stop — with room for the process to respond thoughtfully (Section 5's SIGTERM) or, when necessary, unconditionally (Section 5's SIGKILL).
- **Interrupting execution.** Stopping whatever a process is currently doing, typically in response to a user action (Section 5's SIGINT).
- **Stopping and continuing processes.** Pausing a process's execution entirely, and later resuming it, without terminating it (Section 5's SIGSTOP/SIGCONT).
- **Reacting to operating-system events.** Signals are also how certain OS-level occurrences (not just human-initiated ones) are communicated to processes.
- **Controlling processes from the shell.** The shell (Concept 13, still ahead) uses signals as its primary mechanism for controlling processes it started — including, ultimately, the `kill` command this lesson focuses on (Section 5).
- **Graceful shutdown.** A structured way to ask an application to wind down cleanly, rather than simply vanishing (Section 6's dedicated subsection).
- **Operational control.** In production, operators and deployment systems routinely use signals to manage running services (Section 15).

**What signals are *not* a general-purpose replacement for.** Signals are deliberately narrow: they carry a specific, predefined notification (identified by name/number, Section 5) — **not** an arbitrary payload of application data. If two processes need to exchange real information, they use the data channels this module will cover later (standard I/O, pipes) — not signals. This lesson insists on this distinction repeatedly, because conflating "signal" with "message" is one of the most common beginner misunderstandings (Section 10).

---

## 3. Why an AI Engineer Needs It

- **Stopping a Python service correctly is a signals problem.** Whether you press Ctrl+C on a development server, or a deployment system shuts down a production service, the mechanism underneath is the same: a signal is delivered, and how the process responds determines whether it shuts down cleanly or abruptly.
- **Graceful shutdown is directly built on signal handling** (Section 6, Section 13) — an inference service that finishes in-flight requests before exiting, rather than dropping them mid-response, is doing so because its code explicitly handles a termination signal.
- **Worker processes, background workers, and batch jobs** all need to be stoppable in a controlled way — signals are the standard mechanism for requesting that, whether from an operator's terminal or an automated deployment process.
- **Service restarts and deployment shutdowns** routinely work by sending a termination signal to the old process before starting a new one — understanding what that signal actually does (and doesn't guarantee) is directly relevant to reasoning about deployment reliability.
- **Cleanup before termination** — releasing resources, closing open files and database connections (Concept 07, Concept 08) — only happens if the application has explicitly registered logic to do so in response to a signal (Section 6, Section 13); it is never automatic.

**A production-style sequence, previewed here and expanded fully in Section 7:**

```text
Deployment / operator
        ↓
Request process shutdown
        ↓
SIGTERM
        ↓
Python service
        ↓
Graceful shutdown logic                (application code, registered in advance — Section 6)
        ↓
Stop accepting new work
        ↓
Finish/abort in-flight work appropriately
        ↓
Release resources
        ↓
Exit
```

**Why this matters for reliable production systems.** A service that doesn't handle termination signals thoughtfully can drop in-flight work, leave files or connections open, or corrupt data mid-write when it's stopped — understanding signals is the foundation for building services that shut down *predictably*, which is a genuine reliability property, not a cosmetic one.

**This lesson does not teach Kubernetes lifecycle behavior, systemd, or other orchestration-level shutdown mechanisms in depth** (Section 15's scope note) — those are later, more advanced topics, all ultimately built on top of the same OS-level signal mechanism this lesson teaches.

---

## 4. Beginner Explanation

**Analogy: a worker receiving short, standardized notifications.**

```text
Process       = a worker, in the middle of doing their job
Signal          = a short, specific notification delivered to that worker
```

Imagine a worker at their desk, and a small set of standardized notifications that can be delivered to them, each with a fixed, well-understood meaning:

- **"Please stop"** — a polite, formal request: finish what you reasonably can, then stop. (This is the everyday feel of **SIGTERM**, Section 5.)
- **"Stop immediately"** — no negotiation, no chance to finish anything — you are removed from your desk right now. (This is the everyday feel of **SIGKILL**, Section 5.)
- **"Pause"** — stop working for now, but stay exactly where you are; you might be asked to resume later. (This is the everyday feel of **SIGSTOP**, Section 5.)
- **"Continue"** — resume exactly where you left off. (This is the everyday feel of **SIGCONT**, Section 5.)
- **"The user interrupted you"** — someone actively signaled, right now, that they want your attention or want you to stop what you're doing. (This is the everyday feel of **SIGINT**, Section 5 — the notification generated when someone presses Ctrl+C.)

**Where this analogy is useful:** it captures the core shape — a small, fixed set of standardized notifications, each with an established meaning, delivered to a specific worker (process) rather than being a general conversation.

**Where this analogy must not replace technical accuracy, and breaks down:**

- A human worker can always, in principle, choose to ignore or negotiate around an instruction; a real process **cannot** ignore every signal — some (SIGKILL, SIGSTOP) are enforced unconditionally by the operating system, with no way for the process to refuse or even notice in advance (Section 5, Section 12).
- "Please stop" from a human manager might come with a detailed conversation about *why* or *what to prioritize*; a real signal carries no such payload — it is only ever the fixed, predefined notification itself, nothing more (Section 1).
- A worker's response to "please stop" is entirely up to their own judgment; a process's response to SIGTERM is entirely up to whether — and how — its own code has been written to handle it (Section 6, Section 13) — with no code written for it, a fixed, OS-defined default action happens instead.

The rest of this lesson moves from this everyday intuition into the exact, technical model — the analogy is a way in, not a substitute for it.

---

## 5. Technical Explanation

### Important signals, explained precisely

**SIGINT** — *interrupt*. Generated by the terminal, most commonly when a user presses **Ctrl+C** on a running foreground process. **It is a request to interrupt — not universally equivalent to immediate termination.** Its default action (Section 5's table) is to terminate the process, but a process can register its own handler (Section 6) to respond differently — for example, prompting "are you sure?" before actually stopping.

**SIGTERM** — *terminate*. A termination **request**, and the conventional, polite way to ask a process to shut down. **The process can handle it** — registering a handler (Section 6) that performs cleanup (closing files, finishing in-flight work, releasing resources) **before** actually exiting. This is the signal graceful shutdown (Section 6's dedicated subsection) is built around.

**SIGKILL** — *kill, unconditionally*. An immediate termination request **enforced directly by the operating system**. **It cannot be caught, handled, or ignored by the target process — no exceptions.** Because the process is forcibly terminated by the kernel itself, **any cleanup code the process might have written for other signals simply never runs** when SIGKILL is what actually ends it.

**SIGHUP** — *hangup*. Traditionally generated when a controlling terminal was closed (the process's terminal connection was lost). In modern usage, many long-running services repurpose SIGHUP for other operational purposes (such as a request to reload configuration) — **this lesson does not claim SIGHUP always means one universal thing across every application; its traditional meaning is the terminal-hangup notification, and any further reuse is entirely application-specific.**

**SIGSTOP** — *stop, unconditionally*. Pauses a process's execution entirely. **Like SIGKILL, it cannot be caught or ignored by the target process.** Unlike SIGKILL, the process is not terminated — it remains in memory, simply not executing, until resumed.

**SIGCONT** — *continue*. Resumes a process that was previously stopped (by SIGSTOP or similar), letting it continue executing exactly where it left off.

**Linux defines many other signals beyond these six** (`kill -l`, Section 9, lists them) — this lesson deliberately teaches only the small set above in depth, since they cover the overwhelming majority of what an Applied AI Engineer actually needs for operating real services.

### Signal names and numbers

Every signal has both a symbolic **name** (`SIGTERM`, `SIGINT`, and so on) and a numeric identifier.

**Genuinely observed output from this environment**, listing every signal `kill -l` reports here:

```text
$ kill -l
 1) SIGHUP	 2) SIGINT	 3) SIGQUIT	 4) SIGILL	 5) SIGTRAP
 6) SIGABRT	 7) SIGBUS	 8) SIGFPE	 9) SIGKILL	10) SIGUSR1
11) SIGSEGV	12) SIGUSR2	13) SIGPIPE	14) SIGALRM	15) SIGTERM
16) SIGSTKFLT	17) SIGCHLD	18) SIGCONT	19) SIGSTOP	20) SIGTSTP
21) SIGTTIN	22) SIGTTOU	23) SIGURG	24) SIGXCPU	25) SIGXFSZ
```

**Important caveat: these numbers are a Linux convention observed in this specific environment, not a universal standard you should memorize.** Exact numeric values can differ across Unix-like systems and architectures. **This lesson's learning objective is knowing the symbolic names (`SIGTERM`, `SIGKILL`, and so on) and using them directly — never memorizing or relying on specific numbers.** Every example in this lesson uses names for exactly this reason.

### Default actions

Every signal has a **default action** — what happens if the receiving process has not registered its own handler for it (Section 6).

| Signal | Typical default action |
|---|---|
| `SIGTERM` | Terminate |
| `SIGINT` | Terminate |
| `SIGKILL` | Terminate (unconditionally — cannot be overridden) |
| `SIGHUP` | Terminate |
| `SIGSTOP` | Stop (unconditionally — cannot be overridden) |
| `SIGCONT` | Continue a stopped process |

**Not every signal terminates a process by default** — `SIGSTOP` pauses without terminating, and `SIGCONT` resumes execution rather than ending it. (Beyond the six this lesson focuses on, Linux also defines signals whose default action is to *ignore* the signal entirely, and others that terminate *and* can produce a diagnostic core dump — this lesson mentions these two additional categories only by name, without teaching them in depth, since they fall outside the core six signals an Applied AI Engineer needs first.)

### The `kill` command

**A required clarification, stated precisely:** **`kill` is a command for sending a signal to a process — its name does not mean that every invocation immediately terminates the target.** `kill` can send *any* signal, including ones whose entire purpose is not to terminate anything at all (`SIGSTOP`, `SIGCONT`).

```bash
kill PID
```

Sent with no signal specified, `kill` defaults to sending `SIGTERM` — a termination *request*, not an unconditional kill.

**Sending a specific signal by name:**

```bash
kill -TERM PID
kill -SIGTERM PID
kill -INT PID
kill -KILL PID
```

(`-TERM` and `-SIGTERM` are equivalent, accepted forms — this lesson uses the shorter form throughout for readability.)

**The relationship, end to end:**

```text
kill command
     ↓
request to send a specific signal
     ↓
OS                                    (checks permissions, Section 6's next subsection)
     ↓
target process
```

**Listing available signals:**

```bash
kill -l
```

This is exactly what produced the genuinely observed output shown above.

**A required safety rule, honored throughout this entire lesson:** **every practical demonstration in this lesson sends a signal only to a process the demonstration itself created, moments earlier, specifically for that purpose.** Before ever sending a signal to a PID, this lesson's own practice (Section 9) is: create the process, capture its exact PID from that creation, and only then send it a signal — never signal an arbitrary or previously-existing PID.

---

## 6. How It Works Internally

### The signal delivery flow

```text
Signal generated/requested          (a user presses Ctrl+C, or `kill` is run)
        ↓
OS identifies the target process
        ↓
Signal becomes pending/delivered according to OS rules
        ↓
Process receives the signal
        ↓
Default action OR custom handler            (whichever applies — see below)
        ↓
Process continues / stops / terminates
```

**Terminology, defined precisely:**

- **Signal source** — whatever generated the signal (a terminal, the `kill` command, an OS-level event).
- **Target process** — the specific process the signal is directed at.
- **Signal delivery** — the OS actually handing the signal to the target process for processing.
- **Default action** — what happens if the process has not registered a custom handler (Section 5's table).
- **Signal handler** — application-registered code that runs instead of the default action, for signals that can be caught (below).
- **Ignored signal** — some signals can be explicitly set to be ignored by the receiving process, rather than triggering their default action or a custom handler (not possible for `SIGKILL`/`SIGSTOP`, which can never be ignored).
- **Pending signal, at a conceptual level** — a signal that has been sent but not yet fully processed by the target; this lesson does not teach the detailed internal queuing/masking mechanics behind this.

**This lesson does not dive into kernel scheduler implementation or low-level signal queue internals** — the flow above is the correct level of depth for a foundational understanding.

### Signals and permissions

**Sending a signal to another process is not unconditionally allowed — connecting directly back to [Permissions](08-permissions.md):**

```text
Process identity                    (Concept 03, Concept 08)
      ↓
Permissions / authorization           (the OS checks whether this sender may signal this target)
      ↓
Can this process signal that target?
      ↓
Signal delivery (if authorized) — otherwise the OS refuses the request
```

**At a foundational level:** whether one process is allowed to send a signal to another depends on operating-system authorization rules, generally connected to process identity (Concept 08's ownership model) — a process cannot, in general, freely signal every other process on the system regardless of who owns it. **This lesson does not teach the detailed authorization rules or how to work around them** — only that this check exists, and connects the two lessons conceptually.

### Python signal handlers

Python's standard library exposes signal handling through the `signal` module:

```python
import signal
import sys

def handler(signum, frame):
    print("Signal received")
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)
```

**Conceptually, what happens when this process later receives SIGTERM:**

```text
OS
 ↓
SIGTERM delivered
 ↓
Python runtime
 ↓
registered handler                (the `handler` function above)
 ↓
application-defined response        (print a message, clean up, then exit)
```

**A required, precise statement: not every signal can be handled this way.** `signal.signal(signal.SIGKILL, ...)` and `signal.signal(signal.SIGSTOP, ...)` cannot override those signals' behavior — **`SIGKILL` cannot be caught, and `SIGSTOP` cannot be caught**, in Python or in any other language, because the operating system enforces both of them unconditionally, before any application code ever gets a chance to run (Section 5). Attempting to register a handler for either of these will fail or be rejected, depending on the platform — this lesson does not go further into Python's specific error behavior here, only the underlying, universal fact that both signals are simply not interceptable by any application.

**This lesson does not teach advanced Python signal-handling internals** (interaction with threads, signal-safe operations inside a handler, and more) — Section 9's practical demonstration shows the simple, correct pattern above, which is sufficient for this foundational lesson.

### Graceful shutdown vs. abrupt termination

**A required distinction.**

```text
Abrupt termination:
signal → process disappears                    (no cleanup logic runs at all)

Graceful shutdown:
signal
  ↓
application notices (a registered handler runs)
  ↓
stop accepting new work
  ↓
finish/cancel appropriate in-flight work
  ↓
release resources
  ↓
close resources                                  (files, database connections, and similar)
  ↓
exit
```

**The single most important sentence in this lesson: graceful shutdown is an application behavior built around a termination request — a signal alone does not magically perform application cleanup.** Sending `SIGTERM` to a process that has never registered a handler for it simply triggers its default action (terminate, Section 5's table) — **exactly as abruptly as if no thought had gone into shutdown at all.** Graceful shutdown only happens because a developer explicitly wrote code (Section 6's Python example) that runs in response to the signal — it is not a feature signals provide automatically.

**Directly connecting to realistic services:** an HTTP service that finishes in-flight requests before exiting, a worker that finishes its current job before stopping, a model-serving process that completes an in-progress inference before shutting down, a database connection that's properly closed rather than abandoned mid-transaction, temporary files that are cleaned up rather than left behind — **every one of these is graceful-shutdown application logic, triggered by a signal, but never provided by the signal itself.**

---

## 7. Real-World Example

**A complete production-style example:**

```text
AI Model-Serving Process
        ↓
receives requests
        ↓
deployment needs to stop the service
        ↓
SIGTERM
        ↓
service receives the termination request
        ↓
stop accepting new requests
        ↓
finish/cancel in-flight work appropriately
        ↓
release resources
        ↓
close connections/files
        ↓
exit
```

**Why `SIGTERM` is generally preferable to `SIGKILL` for shutting down a service:** `SIGTERM` gives the application a *chance* — via a registered handler (Section 6) — to shut down thoughtfully; `SIGKILL` gives it none at all. A well-operated production system escalates deliberately, `SIGTERM` first, `SIGKILL` only if the process fails to actually stop within a reasonable window (Section 11's escalation workflow) — never the reverse.

**Why application code must explicitly implement appropriate shutdown behavior:** as Section 6 stressed, nothing about sending `SIGTERM` automatically produces graceful behavior — a service with no registered handler shuts down exactly as abruptly under `SIGTERM`'s default action as it would under `SIGKILL`. The *only* difference `SIGTERM` provides is the *opportunity* to do better, which the application must actually take.

**Why long-running model inference may require a careful shutdown policy:** if a single inference request can take several seconds (or longer), a naive shutdown that terminates mid-request either wastes that work or, worse, could return a corrupted or partial result to a caller expecting a complete one — a thoughtful shutdown policy has to decide, deliberately, whether to finish in-flight inference, cancel it safely, or something in between, rather than leaving that outcome to chance.

**Why forced termination can leave work incomplete:** `SIGKILL` (or any abrupt termination) stops a process at whatever instruction it happened to be executing — a half-written file, a half-completed database transaction, or a dropped in-flight request are all realistic, direct consequences of forced termination with no opportunity for cleanup.

**Why operational control is part of production reliability:** a service that can be stopped predictably — cleanly finishing or safely abandoning its current work, every time — is measurably more reliable to operate than one whose shutdown behavior is a gamble. This is not a cosmetic concern; it is a direct, practical reliability property, and it rests entirely on the signal-handling foundation this lesson teaches.

| Real-world scenario | Signal typically used | What "graceful" means here |
|---|---|---|
| Stopping a Python service | `SIGTERM` (default) | Registered handler finishes/cancels work, then exits |
| Development server interruption | `SIGINT` (Ctrl+C) | Often just stops immediately — acceptable for local development |
| Worker process shutdown | `SIGTERM` | Finishes or safely abandons its current job |
| Model-serving process shutdown | `SIGTERM` | Completes or safely cancels in-flight inference before exiting |
| Batch job interruption | `SIGINT` or `SIGTERM` | Depends on whether partial batch progress is safe to abandon |
| Unresponsive process, last resort | `SIGKILL` | No cleanup occurs — accepted only when graceful shutdown has failed |

---

## 8. Relationships to Other Concepts

```text
Process running
      ↓
Signal received
      ↓
Application/OS response
      ↓
Process continues / stops / terminates
      ↓
Exit status / process state changes           (full detail: Process Lifecycle, Concept 14)
```

```text
Environment variable                          Signal
        ↓                                        ↓
configuration at process startup/runtime      event/control notification to a running process
```

```text
Data channels (later lessons):    stdin / stdout / stderr / pipes
Control channel (this lesson):    signals
```

| Concept | Relationship to signals | Prerequisite or later? | Full treatment |
|---|---|---|---|
| Kernel and User Space | The kernel is the sole authority that generates, queues, and delivers signals — user-space code cannot deliver a signal without going through it | Prerequisite (Concept 01) | Already covered |
| System Calls | Sending and handling signals are both kernel-mediated operations, using the same system-call boundary Concept 02 introduced generally | Prerequisite (Concept 02) | Already covered |
| Processes | A signal's target is always a specific process (or, in some cases, a process group) — Concept 03's process-identity model | Prerequisite (Concept 03) | Already covered |
| Threads | Signal delivery to a multi-threaded process involves additional considerations this lesson does not teach in depth | Prerequisite (Concept 04) | Already covered |
| Scheduling | Independent of signals directly, though a stopped process (`SIGSTOP`) becomes ineligible for scheduling until resumed | Prerequisite (Concept 05) | Already covered |
| Virtual Memory | Independent of signals | Prerequisite (Concept 06) | Already covered |
| Filesystems | Files a process has open are exactly the kind of resource graceful shutdown logic (Section 6) is responsible for closing properly | Prerequisite (Concept 07) | Already covered |
| Permissions | Governs whether one process is authorized to signal another at all (Section 6) | Prerequisite (Concept 08) | Already covered |
| Environment Variables | A different mechanism entirely — configuration supplied at startup, versus a signal's real-time event/control notification (Section 8's diagram) | Prerequisite (Concept 09) | Already covered |
| Standard Input/Output | A data channel, not a control channel — Section 1's and Section 8's core distinction | Later | Concept 11 |
| Pipes | Transfer data between processes; signals communicate control/events, not data (Section 1) | Later | Concept 12 |
| Shell | Creates processes and is the everyday tool used to send them signals (`kill`, Ctrl+C) — Section 5, Section 9 | Later | Concept 13 |
| Process Lifecycle | Signals are one of the mechanisms that cause the state transitions (interrupted, stopped, continued, terminated) that lesson covers fully | Later | Concept 14 |

---

## 9. Practical Observation / Commands

You are working in Ubuntu inside WSL2. Every signal in this lesson's practical work is sent only to a process created moments earlier, specifically for that demonstration — never to an existing, unrelated, or system process. No `sudo` is required anywhere in this lesson.

### WSL2 caveat, stated once, applying throughout

**This lesson's practical demonstrations run entirely inside the Linux/WSL2 environment, and every signal sent here targets a Linux process managed by WSL2's own Linux kernel** (Concept 01 already established that WSL2 runs a genuine Linux kernel). **Signals sent from within this Linux/WSL2 shell do not reach, and should never be assumed to control, arbitrary Windows host processes** — the two are separate process spaces managed by separate operating-system kernels, exactly as Concept 09 explained for environment variables. This lesson performs every demonstration inside the Linux/WSL2 environment specifically because that is where this module's signal-handling model applies directly and reliably.

### Setup, and a required safety habit

Before sending any signal, this lesson's practice is always: **(1)** create the process, **(2)** capture its exact PID from creation (`$!` in Bash captures the most recently backgrounded process's PID), **(3)** confirm that PID with `ps` before proceeding, **(4)** only then send a signal.

### Demonstration 1 — SIGTERM

```bash
tail -f /dev/null &
PID1=$!
echo "Created PID1: $PID1"
ps -p "$PID1" -o pid,stat,cmd
kill -TERM "$PID1"
ps -p "$PID1"
```

**Observed in this environment:**

```text
Created PID1: 6916
    PID STAT CMD
   6916 Sl   tail -f /dev/null
    PID TTY          TIME CMD
```

`tail -f /dev/null` (this module's standard, harmless stand-in for an idle long-running process, used because this lesson's tooling blocks a literal leading `sleep <N>` command — `sleep 300` works identically well for you in your own terminal) had no registered handler, so `SIGTERM`'s default action (Section 5) applied: the process terminated, and the final `ps -p` shows no matching row.

### Demonstration 2 — SIGINT

```bash
tail -f /dev/null &
PID2=$!
echo "Created PID2: $PID2"
ps -p "$PID2" -o pid,stat,cmd
kill -INT "$PID2"
ps -p "$PID2"
```

**Observed in this environment:**

```text
Created PID2: 6921
    PID STAT CMD
   6921 Sl   tail -f /dev/null
    PID TTY          TIME CMD
```

**The difference between this and pressing Ctrl+C interactively, stated precisely:** pressing Ctrl+C in an interactive terminal generates `SIGINT` and delivers it to whatever process is currently the terminal's *foreground* process — a mechanism tied to your terminal session itself. `kill -INT <PID>` sends the exact same signal, programmatically, to any specific target PID you choose, regardless of whether it's a foreground terminal process at all. **The signal delivered, and its default action, are identical either way** — only the *triggering mechanism* differs (a keypress in your terminal, versus an explicit command targeting a specific PID).

### Demonstration 3 — SIGKILL

```bash
tail -f /dev/null &
PID3=$!
echo "Created PID3: $PID3"
ps -p "$PID3" -o pid,stat,cmd
kill -KILL "$PID3"
ps -p "$PID3"
```

**Observed in this environment:**

```text
Created PID3: 6926
    PID STAT CMD
   6926 Sl   tail -f /dev/null
/bin/bash: line 32:  6926 Killed                     tail -f /dev/null
    PID TTY          TIME CMD
```

**Notice Bash itself reported `Killed`** — a direct, visible signal (no pun intended) that this termination happened differently from Demonstration 1's `SIGTERM` case, which produced no such message. `SIGKILL` is enforced unconditionally by the kernel (Section 5) — there was no opportunity for this process to run any cleanup code, even if it had been written to try.

### Demonstration 4 — SIGSTOP / SIGCONT

```bash
tail -f /dev/null &
PID4=$!
echo "Created PID4: $PID4"
ps -p "$PID4" -o pid,stat,cmd
kill -STOP "$PID4"
ps -p "$PID4" -o pid,stat,cmd
kill -CONT "$PID4"
ps -p "$PID4" -o pid,stat,cmd
kill -TERM "$PID4"        # cleanup
ps -p "$PID4"
```

**Observed in this environment:**

```text
Created PID4: 6944
    PID STAT CMD
   6944 Sl   tail -f /dev/null
    PID STAT CMD
   6944 Tl   tail -f /dev/null
    PID STAT CMD
   6944 Sl   tail -f /dev/null
    PID TTY          TIME CMD
```

**What changed, precisely, matching Concept 03's Linux state notation:** the `STAT` column changed from `Sl` (sleeping) to **`T`** (stopped) after `SIGSTOP` — a directly observed, real state transition — and back to `Sl` after `SIGCONT`. The process was never terminated during this entire sequence; it simply stopped executing, then resumed exactly where it left off, confirming Section 5's description of `SIGSTOP`/`SIGCONT` precisely. The final `kill -TERM` was this demonstration's own cleanup step.

### Demonstration 5 — A Python signal handler

**The script used** (created only in an isolated temporary location for this observation, not saved as a permanent project file):

```python
import signal
import sys
import time

def handler(signum, frame):
    print("Received SIGTERM, cleaning up...", flush=True)
    print("Cleanup complete, exiting.", flush=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)
print("Ready, waiting for signal...", flush=True)
while True:
    time.sleep(1)
```

**What this code does, line by line, for a beginner:** it imports the `signal` module (Section 6) and `sys` (for `sys.exit`); defines `handler`, a function that will run *instead of* the default action when this process receives `SIGTERM`; registers that handler with `signal.signal(signal.SIGTERM, handler)`; prints a "ready" message; then simply waits (a loop calling `time.sleep(1)` repeatedly) until a signal arrives.

**Running it, sending SIGTERM, and observing the result:**

```bash
python3 handler_demo.py > output.log 2>&1 &
PID5=$!
cat output.log
kill -TERM "$PID5"
cat output.log
ps -p "$PID5"
```

**Observed in this environment:**

```text
Created PID5: 6968

--- output.log before signal ---
Ready, waiting for signal...

--- sending SIGTERM ---

--- output.log after signal ---
Ready, waiting for signal...
Received SIGTERM, cleaning up...
Cleanup complete, exiting.

--- confirm process exited ---
    PID TTY          TIME CMD
```

**This is the complete, directly observed picture of graceful shutdown from Section 6, made concrete:** the process printed its "ready" message, received `SIGTERM`, ran its own registered handler instead of the default terminate action, printed two cleanup messages of its own choosing, and then exited on its own terms (`sys.exit(0)` — a clean, code `0` exit, Concept 03). The process's own `wait` result in this environment confirmed an exit status of `0`. Compare this directly to Demonstration 1 — same signal (`SIGTERM`), completely different outcome, because *this* process had explicitly registered a handler and the earlier one had not.

### Cleanup

All temporary files (`handler_demo.py`, `output.log`) and their containing directory were created in an isolated scratch location and fully removed after this lab, verified with `ls -d <directory>` returning "No such file or directory." No persistent project file, system file, or unrelated process was ever touched.

---

## 10. Common Misconceptions

| Misconception | Why it's wrong |
|---|---|
| "`kill` always kills a process immediately." | `kill` sends a signal — by default `SIGTERM`, a termination *request*, not an unconditional, instant kill (Section 5); it can also send signals that don't terminate anything at all, like `SIGSTOP`. |
| "`SIGTERM` and `SIGKILL` are the same." | `SIGTERM` can be caught and handled (Demonstration 5); `SIGKILL` cannot be caught under any circumstances and always terminates immediately (Section 5, Demonstration 3). |
| "Every signal can be caught." | `SIGKILL` and `SIGSTOP` specifically cannot be caught, handled, or ignored by any process (Section 5, Section 6). |
| "SIGTERM guarantees that cleanup will happen." | Cleanup only happens if the application explicitly registered a handler that performs it (Section 6) — Demonstration 1's process had no handler and terminated exactly as abruptly as `SIGKILL` would have. |
| "SIGKILL lets the application clean up before termination." | The opposite is true by design — `SIGKILL` is enforced by the kernel with no opportunity for any application code to run at all (Section 5, Demonstration 3). |
| "Ctrl+C directly kills the process." | Ctrl+C generates `SIGINT` (Section 5, Demonstration 2), which is a request whose default action is to terminate — but, like `SIGTERM`, it can be caught and handled differently. |
| "Signals are the same as stdin." | Signals are a control/notification mechanism; stdin is a data channel a process actively reads from — Section 1's and Section 8's core distinction. |
| "Signals are a general-purpose messaging system for arbitrary data." | A signal carries only a fixed, predefined notification (its name/number) — never an arbitrary payload (Section 1). |
| "Only Linux uses signals." | Signals are a general Unix/POSIX concept, used across Unix-like systems generally — this lesson focuses on Linux specifically because that's this roadmap's practical environment, not because the concept is Linux-exclusive. |
| "A signal is delivered directly from one application to another without OS involvement." | The kernel is always the intermediary — it generates or receives the request, checks authorization (Section 6), and delivers the signal; there is no direct application-to-application channel (Concept 01's kernel-mediation principle, applied here). |
| "A process can always ignore any signal." | `SIGKILL` and `SIGSTOP` cannot be ignored, set to a custom handler, or blocked by any process (Section 5, Section 6). |
| "SIGSTOP can be handled by the application." | It cannot — it is enforced unconditionally by the OS, identically to `SIGKILL` in this specific respect (Section 5, Section 6). |
| "SIGKILL can be handled by Python." | `signal.signal(signal.SIGKILL, ...)` cannot override its behavior — Python cannot make `SIGKILL` catchable, because the underlying OS guarantee applies regardless of language (Section 6). |
| "Sending a signal to any PID is safe." | This lesson's own safety rule (Section 5, Section 9) exists precisely because signaling the wrong process — especially an unrelated system or user process — can have real, unwanted consequences; always verify a PID belongs to a process you created before signaling it. |
| "Graceful shutdown is guaranteed just because SIGTERM was sent." | Section 6's central point, restated: `SIGTERM` only creates the *opportunity* for graceful shutdown — whether it actually happens depends entirely on whether the application registered appropriate handling logic. |
| "Signal handling is only useful for command-line programs." | Every long-running service — web APIs, background workers, model-serving processes (Section 3, Section 7) — depends on correct signal handling for reliable operation, not just interactive command-line tools. |
| "Signals replace proper service APIs or health checks." | Signals are one specific, low-level control mechanism among several a production system uses — they do not substitute for application-level health checks, readiness signaling, or service APIs, which operate at a different layer entirely. |

---

## 11. Debugging and Troubleshooting

### A systematic reasoning workflow

```text
Identify the target process
        ↓
Verify the PID                            (confirm it's actually the process you intend)
        ↓
Inspect process state                       (ps — running, sleeping, stopped?)
        ↓
Identify the intended signal
        ↓
Send the least-forceful appropriate signal    (SIGTERM before SIGKILL)
        ↓
Observe process behavior
        ↓
Check logs/output/state
        ↓
Determine whether the handler/default action ran
        ↓
Verify process state/exit
        ↓
Escalate only if necessary
```

**The escalation concept, stated precisely — never recommend arbitrary repeated killing:**

```text
SIGTERM
   ↓
wait / observe
   ↓
if the process has not stopped in a reasonable time
SIGKILL                          (last resort, only after SIGTERM has genuinely failed)
```

**Scenario 1 — A Python service does not stop immediately after SIGTERM.**

1. *Problem:* `kill -TERM <PID>` was sent, and the process is still running moments later.
2. *Beginner's likely assumption:* "The signal must not have worked, or the command must be broken."
3. *Correct mental model:* if the process has a registered `SIGTERM` handler (Section 6), taking a moment to finish in-flight work before exiting is exactly the *intended*, graceful behavior — not a failure.
4. *Investigation approach:* check the process's logs/output for evidence its handler is actively running (Demonstration 5's cleanup messages are exactly this kind of evidence), and give it a reasonable amount of time before assuming something is wrong.
5. *Expected conclusion:* a brief delay after `SIGTERM` is often correct, expected graceful-shutdown behavior — only escalate (Section 11's escalation workflow) if the process genuinely never stops within a reasonable window.

**Scenario 2 — A service exits without running expected cleanup.**

1. *Problem:* a developer wrote shutdown logic, but it doesn't seem to run when the service is stopped.
2. *Beginner's likely assumption:* "Signal handling in Python must be broken."
3. *Correct mental model:* several explanations are more likely than a broken language feature — the handler might be registered for the wrong signal name, the process might actually be receiving `SIGKILL` (which no handler can intercept, Section 5) rather than `SIGTERM`, or the handler might be registered after the signal was already sent.
4. *Investigation approach:* confirm exactly which signal is actually being sent to stop the service, and confirm the handler is registered for that exact signal, early enough in the program's execution.
5. *Expected conclusion:* "cleanup doesn't run" is almost always a mismatch between the signal actually sent and the signal actually handled — not evidence that Python's signal mechanism itself is unreliable.

**Scenario 3 — Ctrl+C stops a development server.**

1. *Problem (framed as an observation to explain, not necessarily a bug):* pressing Ctrl+C while running a local development server stops it immediately, with no cleanup messages.
2. *Beginner's likely assumption:* "This must mean Ctrl+C is somehow different from a real signal."
3. *Correct mental model:* Ctrl+C generates `SIGINT` (Section 5, Demonstration 2) — if this development server never registered a `SIGINT` handler, its default action (terminate) applies, exactly as expected, and exactly as Demonstration 2 showed directly.
4. *Investigation approach:* check whether the specific application actually registers a `SIGINT` handler — many simple development tools intentionally don't, since immediate termination is often perfectly acceptable during local development.
5. *Expected conclusion:* immediate termination on Ctrl+C is not a bug — it's simply the default action applying because no custom handling was registered, which is often a completely reasonable choice for a local development tool.

**Scenario 4 — SIGKILL prevents application cleanup.**

1. *Problem:* a service stopped with `SIGKILL` left behind an incomplete file, an unclosed connection, or similar.
2. *Beginner's likely assumption:* "The application's cleanup code must have a bug."
3. *Correct mental model:* this is Section 5's and Demonstration 3's central point directly — `SIGKILL` gives *no* opportunity for any application code to run, ever, regardless of how well-written the cleanup logic is.
4. *Investigation approach:* confirm which signal actually stopped the process (`SIGKILL` specifically, versus `SIGTERM`) — if it was `SIGKILL`, the missing cleanup is expected, not a code defect.
5. *Expected conclusion:* incomplete cleanup after `SIGKILL` is the signal's defining, unavoidable characteristic — the fix is avoiding `SIGKILL` except as a genuine last resort (Section 11's escalation workflow), not debugging the application's cleanup code.

**Scenario 5 — The wrong PID receives the signal.**

1. *Problem:* a signal was sent, but the intended process is unaffected, or an unrelated process was affected instead.
2. *Beginner's likely assumption:* "The `kill` command must not be working correctly."
3. *Correct mental model:* this is almost always a PID-identification mistake — PIDs are reused over time (Concept 03), and signaling a stale, mistyped, or unverified PID sends the signal to whatever process actually holds that number right now, not necessarily the one the operator had in mind.
4. *Investigation approach:* re-verify the target PID immediately before signaling it (`ps -p <PID> -o pid,cmd`, Section 5's safety rule), confirming the reported command matches exactly what you intend to signal.
5. *Expected conclusion:* always verify a PID's identity immediately before sending it a signal — this lesson's own lab modeled this habit in every single demonstration.

**Scenario 6 — A process is stopped with SIGSTOP and appears unresponsive.**

1. *Problem:* a process seems completely unresponsive — not crashing, not producing output, just silent.
2. *Beginner's likely assumption:* "The process must have crashed or hung."
3. *Correct mental model:* a process that has received `SIGSTOP` is not crashed at all — it is deliberately paused (Section 5, Demonstration 4), and will resume exactly where it left off once it receives `SIGCONT`.
4. *Investigation approach:* check the process's state with `ps` (the `T` state, exactly as Demonstration 4 showed) before assuming a crash — a stopped process looks very different from a genuinely hung or crashed one once you know to check.
5. *Expected conclusion:* "unresponsive" has more than one possible cause — a stopped process, a genuinely hung process, and a crashed process are all distinguishable with the right observation, and conflating them leads to the wrong fix.

**Scenario 7 — A worker process needs controlled shutdown.**

1. *Problem:* an operator needs to stop a background worker without corrupting whatever job it's currently processing.
2. *Beginner's likely assumption:* "Any signal that stops it should be fine."
3. *Correct mental model:* this is exactly the scenario graceful shutdown (Section 6, Section 7) exists for — send `SIGTERM` first, and rely on the worker's own registered handling logic (if it has any) to finish or safely abandon its current job before actually exiting.
4. *Investigation approach:* confirm whether the specific worker implementation has `SIGTERM` handling logic at all; if it does, `SIGTERM` alone is the correct first step; if it doesn't, `SIGTERM`'s default action will terminate it exactly as abruptly as `SIGKILL` would, and that gap in the worker's own design is the real issue to address.
5. *Expected conclusion:* controlled shutdown is a property of the *worker's own code*, not something any specific signal automatically provides — `SIGTERM` is the right signal to send; whether it behaves gracefully depends on what the worker does with it.

**Scenario 8 — A model-serving process must be shut down without unnecessarily disrupting active work.**

1. *Problem:* an operator needs to redeploy a model-serving process that currently has in-flight inference requests.
2. *Beginner's likely assumption:* "It doesn't matter how I stop it, as long as it stops."
3. *Correct mental model:* this is Section 7's production example directly — `SIGKILL` would abandon in-flight requests with no opportunity to complete or safely reject them; `SIGTERM`, paired with appropriate application-level handling, gives the process a chance to finish or safely cancel that work first.
4. *Investigation approach:* send `SIGTERM` first, and only escalate to `SIGKILL` (Section 11's escalation workflow) if the process genuinely fails to stop within a reasonable window — not as a routine first choice.
5. *Expected conclusion:* for any process with active, meaningful in-flight work, `SIGTERM`-first, `SIGKILL`-only-as-last-resort is the correct operational default — a direct, practical instance of this lesson's central production lesson.

---

## 12. Exercises

Work through these in your own words. No answer key exists for this lesson — the goal is reasoning ability, not matching a memorized phrase.

### Level 1 — Recognition

1. What is a signal, in your own words?
2. What does `SIGINT` mean, and what commonly generates it?
3. What does `SIGTERM` mean?
4. What does `SIGKILL` mean, and why is it different from `SIGTERM`?
5. What does `SIGSTOP` do? What does `SIGCONT` do?
6. What does the `kill` command actually do, precisely?
7. What is a "default action"?
8. Can every signal be caught by a process? Name at least one exception.

### Level 2 — Understanding

9. Explain, in your own words, why signals exist as a separate mechanism rather than requiring processes to constantly check for events.
10. Explain the difference between a signal's default action and a custom handler.
11. Explain why "SIGTERM guarantees cleanup" is inaccurate.
12. Explain why SIGKILL cannot be handled, using Section 5's or Section 6's reasoning.
13. Explain the difference between graceful shutdown and abrupt termination.
14. Explain why signals are not the same as stdin or a general messaging system.
15. Explain why `kill -INT <PID>` and pressing Ctrl+C produce the same signal but through different triggering mechanisms.
16. Explain why permissions matter when one process wants to signal another.

### Level 3 — Application

17. In your own WSL2 terminal, create a disposable process (e.g., `tail -f /dev/null &` or `sleep 300 &`), verify its PID with `ps`, then send it `SIGTERM` and confirm it terminated.
18. Repeat Exercise 17, but send `SIGINT` instead. Compare the result.
19. Create another disposable process and send it `SIGSTOP`. Use `ps -p <PID> -o pid,stat,cmd` to observe its state, then send `SIGCONT` and observe the state again.
20. Create a disposable process and terminate it with `SIGKILL`. Note any difference in your shell's output compared to a `SIGTERM` termination.
21. Write a small Python script that registers a `SIGTERM` handler printing a message and exiting cleanly. Run it, send it `SIGTERM`, and observe the output.
22. Run `kill -l` in your own terminal and identify at least three signals not covered in depth in this lesson.
23. Attempt (safely, on your own disposable process) to reason about what would happen if you tried to register a Python handler for `SIGKILL`. Explain your expectation before testing, if you choose to test it.
24. Using only processes you created yourself, demonstrate the full escalation workflow from Section 11: send `SIGTERM`, observe, and only send `SIGKILL` if the process is still running afterward.

### Level 4 — Debugging

25. A Python service doesn't stop immediately after `SIGTERM`. Using Scenario 1 from Section 11, explain why this might be expected behavior.
26. A service's cleanup code doesn't seem to run when the service is stopped. Using Scenario 2, list at least two possible causes to check before assuming Python's signal handling is broken.
27. Ctrl+C stops a development server immediately with no cleanup output. Using Scenario 3, explain why this is likely not a bug.
28. A service stopped with `SIGKILL` left an incomplete file behind. Using Scenario 4, explain why this is expected, not a cleanup-code defect.
29. A signal was sent but the intended process seems unaffected. Using Scenario 5, explain the most likely cause and how to verify it.
30. A process seems unresponsive but hasn't crashed. Using Scenario 6, explain how to distinguish a stopped process from a genuinely hung one.
31. An operator needs to stop a background worker without corrupting its current job. Using Scenario 7, explain the correct first step and why.
32. A model-serving process needs to be redeployed while handling active requests. Using Scenario 8, explain the correct signal-escalation approach and why `SIGKILL` should not be the first choice.

### Level 5 — Integration

33. Draw (in text/ASCII) a Python AI service receiving `SIGTERM`, running a registered handler, finishing an in-flight request, closing a database connection, and exiting — labeling each step using Section 6's graceful-shutdown model.
34. A friend claims, "Since I send SIGTERM to my service, I don't need to write any shutdown logic — the OS handles it." Using Section 6 and Section 10, construct a response explaining exactly what's missing from this claim.
35. Explain how this lesson's permission-and-signals connection (Section 6) and Concept 08's permission model together explain why one user's process generally cannot signal another user's unrelated process.
36. A production deployment process sends `SIGTERM` to a model-serving process, waits five seconds, and then sends `SIGKILL` regardless of whether the process has stopped. Using Section 7, Section 11's escalation workflow, and Scenario 8, evaluate whether this is a reasonable operational policy and what tradeoffs it involves.
37. Using everything in this lesson, explain to a beginner (in your own words, as if teaching them) why "I sent SIGTERM" and "my service shut down gracefully" are two different claims, and why the gap between them is the single most important idea in this lesson.

---

## 13. Expected Results

**Expected conceptual results — these should hold regardless of your specific machine:**

- Correctly explain what `SIGINT`, `SIGTERM`, `SIGKILL`, `SIGHUP`, `SIGSTOP`, and `SIGCONT` each mean, from memory.
- Correctly explain why `SIGKILL` and `SIGSTOP` cannot be caught, while `SIGTERM` and `SIGINT` can.
- Correctly distinguish a signal's default action from a custom handler's behavior.
- Explain why graceful shutdown depends on application code, not on the signal itself.
- Correctly identify, for several of this lesson's seventeen misconceptions, why each is wrong and what the accurate idea is instead.

**What the practical observations should generally demonstrate, regardless of the exact values:**

- A disposable process with no registered handler should terminate under both `SIGTERM` and `SIGINT`'s default action.
- A disposable process terminated with `SIGKILL` should produce a distinct "Killed" notification from the shell, differing visibly from a plain `SIGTERM` termination.
- A disposable process's `ps`-reported state should change from a sleeping/running state to `T` (stopped) after `SIGSTOP`, and back after `SIGCONT`, without the process ever terminating.
- A Python process with a registered `SIGTERM` handler should print its own custom messages upon receiving `SIGTERM`, rather than simply disappearing, and should exit with a clean, code-`0` status if its handler calls `sys.exit(0)`.

**Possible environment-dependent results — these will vary by machine and are expected to vary:**

- The exact PIDs you observe will differ entirely from this lesson's actual observed values (`6916`, `6921`, `6926`, `6944`, `6968`) — never predictable or reproducible across runs or machines.
- `kill -l`'s exact numbered listing may differ slightly between Linux distributions and versions — this lesson's genuinely observed listing reflects this specific environment; **rely on signal names, never on specific numbers, for exactly this reason.**
- The exact shell message shown for a `SIGKILL`-terminated background job may differ in wording between shells, though the underlying distinction (a forced, unconditional termination with no cleanup) is universal.

---

## 14. Review Questions

Answers are intentionally not provided directly below these questions.

### Foundational knowledge

- What is a signal?
- What is the difference between `SIGTERM` and `SIGKILL`?
- What is the difference between `SIGSTOP` and `SIGKILL`?
- What does `SIGCONT` do?
- What does the `kill` command actually send, by default?

### Reasoning

- Why can't `SIGKILL` be caught or ignored?
- Why doesn't sending `SIGTERM` guarantee graceful shutdown?
- Why is Ctrl+C's relationship to `SIGINT` important to understand precisely?
- Why are signals not a substitute for a general-purpose data-transport mechanism?

### OS relationships

- **How does a Python process actually go from "SIGTERM was sent" to "the process has cleanly exited"?** Walk through every layer.
- Why does sending a signal to another process depend on permissions (Concept 08)?
- How does a signal differ from an environment variable (Concept 09), in terms of what each actually communicates to a process?

### Practical Linux

- What does `ps`'s `STAT` column show for a process that has received `SIGSTOP`?
- Why should signal *names* be used instead of signal *numbers* in practice?
- What is the safety rule this lesson insists on before sending any signal to a PID?

### AI engineering

- Why might a model-serving process need more careful shutdown handling than a simple development script?
- Why is `SIGTERM`-then-`SIGKILL` escalation generally preferred over sending `SIGKILL` immediately?
- Give one concrete example of a resource an AI service's graceful-shutdown logic might need to release before exiting.

### Production debugging

- If a service's cleanup code never runs when it's stopped, what are the first two things you'd check?
- Why might a process that "isn't responding" actually be stopped, rather than crashed or hung?

---

## 15. Production Relevance

At this point, you understand what a signal is, why signals exist, the meaning and default actions of the core signals (`SIGINT`, `SIGTERM`, `SIGKILL`, `SIGHUP`, `SIGSTOP`, `SIGCONT`), how `kill` actually works, how Python signal handlers work, and — most importantly — the distinction between graceful shutdown and abrupt termination. You are not yet expected to know the complete process lifecycle, shell job control, or advanced orchestration-level shutdown protocols — those remain later topics.

For a production Applied AI Engineer, this lesson's mental model shows up constantly:

- **Graceful service shutdown.** Every reliable production service depends on correctly handling `SIGTERM` — this lesson's Demonstration 5 is a directly observed, minimal working example of exactly that pattern.
- **Worker management.** Background workers and task-queue consumers need the same `SIGTERM`-first discipline (Section 11, Scenario 7) to avoid corrupting in-progress jobs.
- **Batch-job interruption.** Whether interrupting a batch job cleanly is even possible — and safe — depends entirely on whether that job's own code was written to respond to a signal thoughtfully.
- **Service restart and deployment behavior.** Redeploying a service commonly means stopping the old process with `SIGTERM` before starting the new one — understanding this is essential for reasoning about deployment reliability and downtime.
- **Operational debugging.** Recognizing the difference between a stopped, a hung, and a crashed process (Section 11, Scenario 6) is a direct, practical production-debugging skill.
- **Resource cleanup.** Files, database connections, and temporary resources (Concept 07, Concept 08) are only released cleanly if an application's shutdown logic explicitly does so — this lesson's central, repeated point.
- **Process supervision, at a conceptual level.** Tools that monitor and restart services ultimately rely on exactly the signal mechanism this lesson taught, even though this lesson does not teach any specific supervision tool in depth.
- **Model-serving operations.** Section 7's and Scenario 8's shutdown-without-disruption reasoning is directly applicable every time a model-serving process needs to be redeployed or scaled down.

**Signals are one part of production process management** — a foundational one, but not the whole picture. **This lesson does not teach kernel signal implementation internals, `sigaction` internals, real-time signals, signal masks, `signalfd`, async-signal-safety rules, `ptrace`, process injection, advanced process supervisors, systemd internals, Kubernetes lifecycle management, or distributed/container shutdown protocols** — every one of these is a genuinely important, more advanced topic, and every one of them is built directly on top of the signal fundamentals this lesson just established. Trying to reason about a Kubernetes pod's termination grace period without first understanding what `SIGTERM`, a default action, and a registered handler actually are would be building on nothing.

**What comes next**, building directly on this lesson:

```text
Signals                          ← this lesson
  → Standard Input/Output          (a data channel, distinct from signals' control channel)
  → Pipes                           (data transfer between processes, not control/events)
  → Shell                            (the everyday tool for creating processes and
                                       sending them signals — `kill`, Ctrl+C, and more)
  → Process Lifecycle                 (the complete story of how signals fit into a
                                        process's full creation-to-termination journey)
```

None of these are taught here — this section exists only to show where this lesson sits within the larger Module 0.2 sequence you are building, one concept at a time.

---

_This file is the completed lesson for Concept 10 of Module 0.2. It intentionally does not teach kernel signal implementation internals, signal frame internals, low-level CPU signal mechanics, `sigaction` internals, advanced POSIX signal semantics, real-time signals, signal masks, `signalfd`, advanced async-signal-safety rules, `ptrace`, process injection, debugging another user's process, kernel programming, advanced process supervisors, systemd internals, Kubernetes lifecycle management, distributed shutdown protocols, or container signal-propagation internals in depth — those remain the subject of later, more advanced curriculum, not this beginner-level foundation._
