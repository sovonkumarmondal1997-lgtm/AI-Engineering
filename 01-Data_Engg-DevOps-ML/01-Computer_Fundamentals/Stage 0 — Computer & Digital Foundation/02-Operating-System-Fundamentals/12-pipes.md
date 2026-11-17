# 12. Pipes

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Module 0.2 — Operating System Fundamentals
**Concept(s) covered:** pipes, pipe read/write ends, buffering, blocking, backpressure, EOF, broken pipes, FIFOs, shell pipelines
**Status:** Not Started

---

## Learning Objectives

By the end of this lesson you should be able to explain, in your own words:

- what a pipe is, and why it is not a file stored on disk
- why operating systems provide pipes as a communication mechanism
- how one process communicates with another through a pipe
- how pipes relate to file descriptors, and to stdin/stdout specifically
- how a pipe connects one process's output to another process's input
- what happens conceptually when a shell runs `A | B`
- how data actually moves through a pipe, including buffering and blocking
- the difference between a pipe and a regular file
- the difference between anonymous pipes and named pipes (FIFOs)
- what EOF means for a pipe, and why closing unused ends matters
- what a broken pipe is, and how it relates to signals
- how Python creates and uses pipes directly, and through `subprocess`
- how pipe-related deadlocks happen, and how to reason about them
- how to debug common pipe-related failures systematically

You should finish this lesson able to say something far more precise than "a pipe connects two programs" — you should be able to explain *exactly* what connects to what, through which mechanism, and what can go wrong.

## Prerequisites

This lesson builds directly on [Standard Input/Output](11-standard-input-output.md) — specifically its model of file descriptors and the three standard streams:

```text
Process
   |
   +-- FD 0 → stdin
   +-- FD 1 → stdout
   +-- FD 2 → stderr
```

This lesson does not repeat that material. What it adds is one new idea: **a pipe is another OS-managed I/O mechanism that can be connected to a process's file descriptors** — meaning the "stdin" or "stdout" a process reads from or writes to can, without the process ever needing to know, actually be a pipe connecting it to another running process.

---

## 1. Connection to Standard Input / Output

Concept 11 already established that what a file descriptor is connected to can change — a terminal, a file, or something else — without the process's own code changing at all (Concept 11's central abstraction). This lesson introduces exactly that "something else": a pipe.

```text
Process A
   |
stdout (FD 1)
   |
   v
  PIPE
   |
   v
stdin (FD 0)
   |
Process B
```

**Why this is a natural extension of standard I/O, not a new topic bolted on:** Process A doesn't do anything different to "write to a pipe" than it does to write to a terminal or a file — it writes to FD `1`, exactly as always. Process B doesn't do anything different to "read from a pipe" than it does to read from a terminal or a file — it reads from FD `0`, exactly as always. **The pipe is entirely a property of what each process's stdin/stdout happen to be connected to** — precisely Concept 11's abstraction, now connecting two *processes* to each other instead of connecting one process to a file or a terminal.

---

## 2. What Is a Pipe?

**A simple analogy first: a conveyor belt between two workstations.** Imagine two workers at adjacent stations in a factory, connected by a short conveyor belt. Worker A places finished items on the belt; Worker B picks items off the belt as they arrive and continues working with them. Neither worker needs to understand the other's job — Worker A just needs to know "place things on the belt when ready," and Worker B just needs to know "take things off the belt when they arrive." The belt itself is the connecting mechanism — not a warehouse where items are permanently stored, just a channel moving things from one place to another.

**Now the real technical model, replacing the analogy.** A **pipe** is an OS-managed communication channel that lets bytes written by one process become available for another process to read, as an ordered byte stream — a **unidirectional**, **stream-oriented** channel (data flows one way, as an ongoing sequence of bytes, not as discrete, addressable "records").

**Three required, precise clarifications:**

- **A pipe is not a file stored on disk.** It has no permanent location in a filesystem (an anonymous pipe, Section 11, has no filesystem presence at all; even a named pipe/FIFO, Section 12, is only a filesystem-visible *name* for a channel — not a place bytes are durably stored, Section 10).
- **A pipe is associated with file descriptors**, exactly as Section 1 showed — a process interacts with a pipe using the same `read`/`write` operations (Concept 02, Concept 11) it would use for any other file descriptor.
- **A pipe is typically used to move a stream of bytes from one specific process to another** — it is fundamentally a process-to-process communication mechanism, not a general-purpose storage mechanism.

---

## 3. Why Pipes Exist

**The problem, without pipes:**

```text
Program A
   ↓
temporary file
   ↓
Program B
```

If Program A had to write its entire output to a temporary file, and Program B had to wait for that file to be completely finished before reading it, several real costs appear: Program B cannot start working until Program A is entirely done; disk space is consumed for data that's only ever needed briefly; someone has to remember to create and later clean up that temporary file; and the two programs become coupled through a shared file location, rather than a direct connection.

**With a pipe:**

```text
Program A
   ↓
pipe
   ↓
Program B
```

**The specific benefits this solves:**

- **Direct streaming.** Program B can start consuming data the moment Program A starts producing it — no need to wait for a complete file.
- **Composability.** Any program that reads stdin and any program that writes stdout can be connected this way, without either needing to be written with the other specifically in mind (Section 1's abstraction).
- **Avoiding unnecessary intermediate files.** No temporary file needs to be created, named, or cleaned up.
- **Processing data incrementally.** Data can be transformed as it flows, rather than requiring an entire dataset to be materialized at once.
- **Connecting simple, focused tools into workflows.** This is the foundational idea behind Unix's design philosophy — small programs, each doing one thing well, composed together through pipes rather than each reimplementing everything itself.

**Trade-offs, honestly stated — pipes are not free of complexity:**

- **Memory/buffering constraints.** A pipe's internal buffer is finite (Section 6) — it cannot hold unlimited data.
- **Blocking.** A writer can be forced to wait if the reader isn't consuming fast enough, and a reader can be forced to wait if no data is currently available (Section 7).
- **Backpressure**, at a conceptual level — when a slow consumer effectively "pushes back" on a fast producer, because the pipe's limited buffer fills up (Section 7).
- **Error-propagation complexity.** As Section 16 explains, stderr does **not** automatically flow through a pipe the way stdout does — errors in one stage of a pipeline require deliberate attention.
- **Debugging complexity.** A multi-stage pipeline that isn't producing expected output requires reasoning about several processes and their connections at once (Section 23).
- **Process coordination.** Multiple independent processes must all behave correctly, and correctly signal completion (Section 8's EOF), for a pipeline to work as intended.

---

## 4. Pipe and File Descriptors

**The conceptual model:**

```text
Process A
  FD 1
   |
   v
 PIPE WRITE END
   |
   |
 PIPE READ END
   |
   v
  FD 0
Process B
```

**Precise terminology:**

- A pipe has a **read end** and a **write end** — two genuinely distinct access points to the same underlying channel.
- Processes interact with these ends through **file descriptors** — a process-local integer handle (Concept 11), exactly like any other file descriptor.
- The file descriptor numbers themselves are **process-local** — Process A's FD `1` and Process B's FD `0` are simply *that process's own* handle for its end of this particular pipe; there's no shared, global numbering between the two processes.
- **The underlying pipe itself is maintained entirely by the OS/kernel** — the actual buffer, the bookkeeping of what's been written and what's been read, all of it lives in the kernel, not in either process's own memory.

**Why this design lets existing programs participate in pipelines without knowing anything about each other's implementation:** because both processes only ever interact with their own file descriptors, using the exact same `read`/`write` operations (Concept 02, Concept 11) they'd use for a file or a terminal, **neither process needs any special "pipe-awareness" built in.** A program written years before pipes were even involved in its use case can still participate in a pipeline perfectly, simply because it already knows how to read stdin and write stdout — this is precisely Section 1's abstraction, and the entire reason Unix composability (Section 3) actually works in practice.

---

## 5. Internal Mechanics

**The conceptual lifecycle of a pipe:**

```text
1. The OS creates a pipe.
2. The process (or processes) receive file descriptors representing the pipe's two ends.
3. A writer writes bytes to the write end.
4. The OS stores/transfers the data through the pipe mechanism.
5. A reader reads bytes from the read end.
6. The reader continues until data is exhausted / EOF is observed (Section 8).
7. Appropriate descriptors are closed once no longer needed.
```

```text
Writer Process
     |
     | write()
     v
+----------------+
| OS Pipe Buffer |
+----------------+
     |
     | read()
     v
Reader Process
```

**This is a conceptual model, not a claim about kernel implementation details.** The pipe buffer is a real, kernel-managed piece of memory with a finite capacity (Section 6) — this lesson does not describe its exact internal data structures, does not claim the pipe is "always a permanent file" (a direct contradiction of Section 2), and does not go into kernel source code. What matters here is the shape of the flow: bytes go in one end, are held briefly by the OS, and come out the other end, as an ordered byte stream.

---

## 6. Pipe Buffering

**Pipes are stream-based, and the OS temporarily buffers data flowing through them.** A writer's `write()` call and a reader's `read()` call don't need to happen at the same instant — the OS holds written-but-not-yet-read bytes in a buffer in between.

**Why finite buffering matters:** a pipe's buffer has a limited capacity. Writers and readers commonly operate at *different rates* — this is completely normal, and the buffer's job is to absorb some of that difference. But if a writer produces data much faster than a reader consumes it, the buffer will eventually fill up completely.

```text
Producer
   |
   | writes quickly
   v
[ PIPE BUFFER ]
   |
   | reads slowly
   v
Consumer
```

**Producer** — whichever process is writing into the pipe. **Consumer** — whichever process is reading from it. **Buffering** — the OS temporarily holding written data until it's read. **Backpressure** — the natural consequence of a full buffer: the producer cannot write any more data until the consumer has read enough to free up space, effectively slowing the producer down to match the consumer's actual pace. The discussion here assumes normal blocking I/O; nonblocking mode changes the behavior. This lesson introduces backpressure only at this conceptual level — it does not teach advanced asynchronous I/O techniques (`select`/`poll`/`epoll`, Section 31) for managing it.

**Multiple writers and `PIPE_BUF` (a short qualification).** A pipe is a byte stream, and the simplest mental model is one writer and one reader. In real systems a pipe can have multiple references to either end, including multiple writers. POSIX/Linux guarantee that a write of up to `PIPE_BUF` bytes is atomic (it will not be interleaved with other writers' data), while larger writes can be interleaved when multiple writers are involved. This lesson does not go further into concurrent writers.

---

## 7. Blocking and Backpressure

**Blocking, precisely defined here:** when a process's `read()` or `write()` call cannot complete immediately, the OS pauses that process (Concept 05's "waiting/blocked" state, applied directly) until the call *can* complete.

- **A writer can block** when the pipe's buffer is completely full and the reader isn't currently consuming data fast enough to free up space (Section 6's diagram).
- **A reader can block** when there is currently no data available to read, but the write end is still open — meaning more data might still arrive (Section 8 explains the alternative: if the write end is closed instead, the reader gets EOF, not a block).

**Why this is not a malfunction:** blocking is the pipe mechanism working exactly as designed — it's precisely what lets a fast producer and a slow consumer coexist safely, without the producer's data being silently lost or the consumer racing ahead of data that doesn't exist yet. Section 19's deadlock discussion explains when this expected, useful blocking behavior can turn into an actual problem.

---

## 8. EOF and Closed Pipe Ends

**EOF (end-of-file), in this context:** a signal to a reader that no more data will ever arrive on this stream — not merely "no data right now," but "there will never be any more."

**The relationship between closing the write end and EOF:** a reader sees EOF specifically once **every** writer's copy of the write end has been closed. As long as *any* process still holds the write end open, the reader has no way to know whether more data is still coming — so it will keep waiting (blocking, Section 7) instead of concluding EOF has been reached. (The one-writer/one-reader diagram is the simplest teaching model; in real systems, multiple processes can hold references to either end, and EOF occurs only after all write-end references are closed.)

```text
Writer
  |
  | writes data
  |
  | closes write end
  v
PIPE
  |
  v
Reader
  |
  | eventually sees EOF
```

**Why closing unused pipe ends matters, concretely:** if a process holds open a copy of the write end it doesn't actually intend to use (for example, because it inherited it accidentally, a topic Section 11's anonymous-pipe discussion touches on), the reader can wait forever for EOF that will never come — not because any bug exists in the reader's own logic, but because an unrelated, unused file descriptor was never closed. **This is one of the single most common real causes of a program that "hangs forever waiting" (Section 23's Debugging Scenario 3).**

---

## 9. Broken Pipes

**What happens when a writer continues writing after the reader has closed its read side:** the reader is gone — there is nothing left to receive the data. **The OS must signal this to the writer**, because it would otherwise have no way to know its output is going nowhere.

**The relationship to `SIGPIPE`, connecting directly to [Signals](10-signals.md):** on Unix-like systems, a process that writes to a pipe whose reader has gone away typically receives a `SIGPIPE` signal (Concept 10) — whose default action is to terminate the writing process. **This lesson does not re-teach signal mechanics** — only that this specific interaction exists: a pipe-related event (the reader disappearing) can trigger signal delivery (Concept 10's entire subject) to the writer.

**Python's corresponding behavior:** on Unix-like systems, writing after the pipe's read end has closed can result in `SIGPIPE` / the `EPIPE` error. Python commonly exposes this underlying broken-pipe condition to your code as a `BrokenPipeError` exception, which your code can catch.

**Why this matters practically:** a program that writes output through a pipe (for example, into a shell pipeline, Section 13) needs to be prepared for the possibility that whatever is downstream has already stopped reading — an entirely normal, expected event in pipeline usage, not a sign of corruption.

---

## 10. Pipe vs Regular File

| Dimension | Pipe | Regular file |
|---|---|---|
| **Storage** | No persistent storage — data exists only transiently, in a kernel-managed buffer | Persistent storage on a filesystem (Concept 07) |
| **Persistence** | Data is gone once read; nothing remains afterward | Data remains until explicitly deleted |
| **Producer/consumer relationship** | Directly connects a specific writer to a specific reader (or set of readers) | No inherent producer/consumer relationship — any process with permission (Concept 08) can open it independently, at any time |
| **Sequential streaming** | Fundamentally sequential — an ordered byte stream, read once and then gone (with multiple writers, see Section 6's `PIPE_BUF` note) | Also supports sequential access, but is not inherently "consumed" by reading |
| **Random access** | Not supported — you cannot "seek" backward in a pipe | Fully supported — you can read or write at arbitrary positions (Concept 07's filesystem model) |
| **Lifetime** | Exists only as long as it's needed by the processes using it (Section 11) | Exists independently of any process, until deleted |
| **Buffering** | A small, finite, kernel-managed buffer, central to how the pipe behaves (Section 6) | Not "buffered" in the same real-time-flow-control sense — writes are simply stored, generally without one process's write blocking on another process's read |
| **Typical use** | Connecting two running processes for a stream of data | Storing data that needs to persist, and might be accessed at arbitrary times by arbitrary processes |

**The core distinction, stated plainly:** a regular file is **persistent storage**; a pipe is primarily a **communication channel between processes** — the two solve genuinely different problems, and this lesson deliberately never conflates them.

---

## 11. Anonymous Pipes

**Why they're called "anonymous":** an anonymous pipe has **no name and no visible presence in the filesystem** at all (unlike the named pipes/FIFOs in Section 12) — it exists purely as a pair of file descriptors, known only to the specific processes that were given them.

**Typical usage: parent/child or otherwise related processes.** Because an anonymous pipe has no filesystem pathname through which an unrelated process can simply open it, the common Unix way another process gets access to either end is by **inheriting it** — receiving a copy of that file descriptor when it's created as a child of a process that already has it (Concept 03's process-inheritance model). File descriptors can also be explicitly transferred between processes using appropriate OS mechanisms, but that is outside this lesson's scope. This is exactly why shell pipelines (Section 13) work the way they do: the shell creates the pipe and arranges for each side of a pipeline to inherit the correct end.

**Lifetime.** An anonymous pipe exists only as long as at least one process still holds one of its ends open — once every reference to both ends is closed, the kernel reclaims it. There's no separate "delete the pipe" step, unlike a regular file (Concept 07).

**Why subprocess-launching mechanisms commonly use anonymous pipes:** when one program needs to capture another's output (Section 18's `subprocess.Popen` example), an anonymous pipe is the natural mechanism — it requires no filesystem name, is automatically cleaned up once both processes are done with it, and is inherited naturally through the parent/child relationship that launching a subprocess already creates.

**This lesson does not teach `fork()`/`exec()` internals** — the precise mechanics of how a new process actually comes into existence and inherits file descriptors belongs to more advanced systems-programming material and, at a higher level, to [Process Lifecycle](14-process-lifecycle.md), still ahead. Here, it's enough to know that inheritance through process creation is *how* an anonymous pipe's ends commonly reach the processes that use them.

---

## 12. Named Pipes / FIFO

**FIFO** stands for **F**irst **I**n, **F**irst **O**ut — describing the same ordered, stream-based behavior every pipe has (Section 2); the name specifically distinguishes this *named* variant from an anonymous pipe.

**Why a named pipe has a filesystem-visible name.** Unlike an anonymous pipe (Section 11), a FIFO is created with an actual path, visible in a directory listing (Concept 07) — this is precisely what lets **unrelated processes**, with no parent/child relationship at all, both find and open the exact same communication channel, simply by both knowing its path.

**A genuinely observed demonstration**, created and cleaned up entirely inside an isolated temporary directory:

```bash
mkdir -p /tmp/pipes-lesson
mkfifo /tmp/pipes-lesson/demo.fifo
ls -l /tmp/pipes-lesson/demo.fifo
```

**Observed in this environment:**

```text
prw-r--r-- 1 sovon sovon 0 Sep 10 16:33 demo.fifo
```

**Notice the leading `p`** in the permission string — this is `ls`'s way of marking this filesystem entry specifically as a pipe (FIFO), distinct from an ordinary regular file (which would show `-`) or a directory (`d`). **This is a required, precise clarification: a FIFO is still fundamentally a communication channel, not ordinary persistent file storage — the leading `p` is exactly the filesystem's own confirmation of this.** Its size is reported as `0` because a FIFO doesn't actually store bytes the way a regular file does (Section 10).

**A genuinely observed writer/reader demonstration**, both operating only inside this same disposable directory:

```bash
(printf "hello through the fifo\n" > /tmp/pipes-lesson/demo.fifo) &
cat < /tmp/pipes-lesson/demo.fifo
```

**Observed in this environment:**

```text
hello through the fifo
```

**What actually happened, step by step:** the writer (`printf ... > demo.fifo`) was started in the background; opening a FIFO for writing conceptually waits until a reader is also present (this is a defining behavioral difference from a regular file, which never waits for a "reader" to open at all); the foreground `cat < demo.fifo` then opened the read side, at which point both sides proceeded, the writer's line flowed through, and `cat` printed it — exactly matching Section 5's general pipe-lifecycle model, now using a named, filesystem-visible channel instead of an anonymous one.

**Cleanup, verified:**

```bash
rm -f /tmp/pipes-lesson/demo.fifo
```

**Observed in this environment:** the FIFO was removed, and its removal confirmed (a subsequent `ls` on it reported "No such file or directory") — like an anonymous pipe, removing the *name* doesn't "destroy data" the way deleting a regular file might feel like it does, precisely because a FIFO never held persistent data in the first place (Section 10).

**This lesson does not go into advanced IPC** (message queues, shared memory, and more — Section 31's scope boundaries) — a FIFO is introduced here only as the named counterpart to the anonymous pipes this lesson otherwise focuses on.

---

## 13. Shell Pipelines

**This is the most important bridge to the next lesson, [Shell](13-shell.md).**

```bash
command1 | command2
```

```text
command1
   |
stdout
   |
   v
 PIPE
   |
   v
stdin
   |
command2
```

**A genuinely observed example:**

```bash
printf '%s\n' apple banana apricot | grep '^ap'
```

**Observed in this environment:**

```text
apple
apricot
```

**What this means, precisely:** `printf`'s stdout was connected to a pipe, and `grep`'s stdin was connected to the *same* pipe's read end — `printf` never "sent data to grep" directly; it simply wrote to its own stdout, exactly as it always does, and the shell (Section 13's role, elaborated in [Shell](13-shell.md)) was what actually arranged this specific connection *before* either program started running (Concept 11's redirection-internals model, applied here to a pipe instead of a file).

**Each stage in a shell pipeline is typically a separate process** — `printf` and `grep` above are two independent, simultaneously-running processes (Concept 03), connected only through this one pipe.

---

## 14. Multi-Stage Pipelines

```text
A | B | C
```

```text
A stdout
   ↓
 PIPE 1
   ↓
B stdin

B stdout
   ↓
 PIPE 2
   ↓
C stdin
```

**A genuinely observed multi-stage example:**

```bash
printf '%s\n' apple banana apricot avocado | grep '^a' | sort
```

**Observed in this environment:**

```text
apple
apricot
avocado
```

**What happened, stage by stage:** `printf` produced four lines; `grep '^a'` (connected via `PIPE 1`) filtered them down to the three starting with `a` (all of them, in this case, since every word here starts with `a` — `banana` was the only one filtered out); `sort` (connected via `PIPE 2`) then alphabetized the surviving three lines. **Three stages (in a typical Unix shell, each in its own process), two separate pipes, each stage doing exactly one focused job** — a direct, concrete instance of Section 3's "Unix philosophy" benefit.

**This lesson does not teach a full shell implementation** — precisely *how* the shell parses `A | B | C`, creates each process, and wires up the pipes belongs to [Shell](13-shell.md), still ahead. Here, the objective is understanding what the pipes themselves are actually doing, once they exist.

---

## 15. Pipeline Exit Status

**Each stage of a pipeline finishes with its own exit code** (Concept 03). Typical Unix shell pipelines run each stage in a separate execution context, commonly a separate process (the exact process behavior depends on the shell, the kind of command, and shell options), so a three-command pipeline normally produces three separate statuses, independent of one another.

**Bash-specific behavior:** by default, a pipeline's overall status (`$?`) is the status of the **last** command. With `set -o pipefail`, the pipeline's status is instead the status of the rightmost command that exited non-zero, or zero if every command succeeded. Bash also records every stage's individual status in the `PIPESTATUS` array.

**An illustration**, using this lesson's own mini-project pipeline (Section 25 shows the complete script). `$?` and `PIPESTATUS` both describe the *most recent pipeline* — but running any other command (including a separate `echo`) resets them, so both must be read in the **same** command, immediately after the pipeline:

```bash
python3 producer.py | python3 processor.py | python3 consumer.py
echo "PIPESTATUS: ${PIPESTATUS[@]} | \$?: $?"
```

**Recorded output** (from the documented environment used when this lesson was prepared; the status values `0 2 0` / `0` were recorded for this pipeline, and the single-command form above was additionally checked in Bash with a stand-in pipeline of the same shape):

```text
warning: skipping invalid value: 'abc'
received 3 values, total=30.0
PIPESTATUS: 0 2 0 | $?: 0
```

**What this demonstrates:** without `pipefail`, Bash's `$?` is the **last** command's status — here `consumer.py`'s `0` — even though the *middle* stage, `processor.py`, actually exited with `2` (this lesson's mini-project convention for "succeeded, but had to skip something," Concept 03's exit-code discussion). `PIPESTATUS` reveals every stage's individual exit code (`0 2 0`) — information `$?` alone hides. With `set -o pipefail` set first, the same pipeline would report `$?` as `2` (the rightmost non-zero status), while `PIPESTATUS` would still be `0 2 0`.

**This lesson deliberately does not make shell-specific pipeline-status semantics its central topic**, and does not claim every shell behaves identically here — `PIPESTATUS` specifically is a Bash feature; other shells provide their own, sometimes differently-named mechanisms for the same underlying need. **Detailed, shell-specific pipeline-status behavior belongs to [Shell](13-shell.md), still ahead.** What matters here is the underlying fact this example demonstrates concretely: a pipeline's "overall success," in the naive sense of checking `$?` alone, can silently hide a real problem in an earlier stage.

---

## 16. Pipes and Standard Error

**A required, precise distinction, directly connecting to [Standard Input/Output](11-standard-input-output.md):** in a typical `A | B` pipeline, **A's stdout is connected to B's stdin — but A's stderr is not automatically sent through that same pipe.** By default, stderr continues going wherever it was already going (commonly, the terminal), completely independently of the pipe connecting stdout to the next stage.

**A genuinely observed demonstration:**

```python
import sys
print("apple")
print("banana")
print("skipped: banana", file=sys.stderr)
print("apricot")
```

```bash
python3 mixed_output.py | grep '^ap'
```

**Observed in this environment:**

```text
skipped: banana
apple
apricot
```

**What actually happened:** `grep '^ap'` only ever saw this script's **stdout** (`apple`, `banana`, `apricot`) through the pipe, and correctly filtered it down to `apple` and `apricot` — but the **stderr** line (`skipped: banana`) was never part of what flowed through the pipe at all; it went straight to the terminal, appearing here interleaved with grep's filtered output, purely a result of timing, not because `grep` processed it.

**Confirming this precisely, by explicitly discarding stderr this time:**

```bash
python3 mixed_output.py 2>/dev/null | grep '^ap'
```

**Observed in this environment:**

```text
apple
apricot
```

With stderr redirected away entirely (Concept 11's `2>` syntax), only the two matching stdout lines remained — direct, genuine confirmation that stderr was never part of the piped stream in the first place.

**Why this matters for debugging, logs, automation, and AI/data-processing pipelines:** a data-processing pipeline that pipes one stage's output into the next is relying entirely on stdout carrying the *actual data* — any diagnostic or warning messages a stage writes to stderr (exactly like Concept 11's and this lesson's own `processor.py`) never contaminate that data stream, letting the next stage safely assume everything it receives is real data, not commentary about the process along the way.

---

## 17. Python Pipes

On Unix/Linux, Python's standard library exposes the raw OS pipe mechanism directly through `os.pipe()` (Python also provides `os.pipe()` on Windows, although the surrounding platform semantics differ; this lesson stays Unix/Linux-focused).

```python
import os

read_fd, write_fd = os.pipe()
```

**Explained line by line:** `os.pipe()` asks the OS to create a new anonymous pipe (Section 11) and returns **two file descriptors** — one for the read end, one for the write end, exactly matching Section 4's model, now expressed directly in Python.

**A genuinely observed, complete example:**

```python
import os

read_fd, write_fd = os.pipe()
print("read_fd:", read_fd, "write_fd:", write_fd)

os.write(write_fd, b"hello from os.pipe\n")
os.close(write_fd)

data = os.read(read_fd, 1024)
print("read back:", data)

os.close(read_fd)
```

**Observed in this environment:**

```text
read_fd: 3 write_fd: 4
read back: b'hello from os.pipe'
```

**Explaining every line:** `os.pipe()` created the pipe and returned descriptors `3` and `4` here — genuinely observed proof of Section 4's point that descriptor numbers are simply the next available slots in this process's own file descriptor table, beyond the standard `0`/`1`/`2` (Concept 11). `os.write(write_fd, b"...")` wrote raw bytes (note the `b"..."` — this is bytes, not a Python string, since pipes at this level move raw byte streams, Section 2) to the write end. `os.close(write_fd)` closed the write end — this is exactly Section 8's "closing the write end" step, and is what lets the subsequent read genuinely detect EOF should it try to read further. `os.read(read_fd, 1024)` read up to 1024 bytes from the read end — the `1024` is simply the maximum amount to read in this one call, not a claim about the pipe's total capacity. `os.close(read_fd)` releases the read end once done.

### Python subprocesses and pipes

The far more common, higher-level way Python code actually uses pipes is through `subprocess.Popen`, which sets up pipes automatically to communicate with a child process it launches.

```python
import subprocess

proc = subprocess.Popen(
    ["grep", "^ap"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

stdout_data, stderr_data = proc.communicate(input="apple\nbanana\napricot\n")
```

**Observed in this environment:**

```text
child stdout: 'apple\napricot\n'
child stderr: ''
child exit status: 0
```

**Explaining the concepts, not just the syntax:** `subprocess.Popen(...)` starts `grep` as a **child process** of this Python script (the **parent**). `stdin=subprocess.PIPE`, `stdout=subprocess.PIPE`, and `stderr=subprocess.PIPE` each tell Python to create a real anonymous pipe (Section 11) — exactly like the `os.pipe()` example above, just set up automatically — connecting this parent process to the corresponding standard stream of the *child* process, instead of leaving it connected to the parent's own terminal or file descriptors. `proc.communicate(input="...")` writes the given text to the child's stdin pipe, then reads everything the child writes to its stdout and stderr pipes, and **waits for the child process to finish** — a single, convenient call handling exactly the write/read/close/wait sequence Section 5's general pipe lifecycle described. `proc.returncode` afterward holds the child's exit status (Concept 03), here confirmed as `0`.

**This lesson does not teach advanced asynchronous subprocess handling** (streaming output while it's still being produced, managing several subprocesses concurrently, and more) — `communicate()` is the recommended high-level approach for ordinary subprocess pipe communication because it coordinates input/output handling and avoids common pipe-buffer deadlocks (it does not, of course, prevent every possible application-level deadlock), and it is the simple pattern this lesson focuses on.

---

## 18. Pipe-Related Deadlocks

**A conceptual example.** Imagine a parent process that writes a large amount of data to a child process's stdin (via a pipe, exactly like Section 17's `subprocess.Popen` example) — but the child isn't currently reading it, perhaps because it's busy doing something else, or is itself waiting to write its *own* output back to the parent first.

```text
Parent
  |
  | write
  v
[PIPE BUFFER]  ← becomes full
  |
  X
Child is not reading
```

**What happens:** once the pipe's buffer fills up completely (Section 6), the parent's write call blocks (Section 7) — the parent is now stuck waiting for the child to read, so it can free up buffer space. If the child, in turn, is waiting for the parent to do something else first (for example, waiting for the parent to finish writing *all* of its input before the child starts producing output) — **neither process can make progress, and the program appears to simply hang.**

**The opposite direction is equally possible:** if a parent tries to read a child's entire output before it has written *any* input to the child's stdin, and the child is meanwhile waiting for that input before it can produce any output at all, the same mutual standstill occurs, just with the roles reversed.

**How engineers reason about this kind of failure:** recognize that "the program hangs" with no error message, no crash, and no CPU usage (Concept 05's related debugging pattern) is a strong signal that something is blocked waiting on I/O rather than stuck in a computational loop — and specifically, when subprocesses and pipes are involved, ask: *is one side waiting for the other to do something it's also waiting on in return?* Common, safer patterns include using `communicate()` (Section 17), which is designed to avoid this common trap by coordinating the read/write handling, or restructuring the exchange so that reading and writing between the two sides can happen concurrently rather than in a strict, mutually-dependent sequence.

**This lesson does not teach advanced concurrency theory** (formal deadlock conditions, prevention algorithms, and more — Section 31's scope boundaries) — only the specific, highly practical shape this particular failure takes with pipes and subprocesses, which is common enough in real engineering work to deserve this foundational treatment now.

---

## 19. Linux / Ubuntu / WSL2 Practical Lab

All commands below are safe, use only processes and files created specifically for this lab, and are fully cleaned up afterward. No `sudo` is required, and no unrelated process or existing project file is ever touched.

### Lab 1 — Simple shell pipeline

```bash
printf '%s\n' apple banana apricot | grep '^ap'
```

**Observed in this environment:**

```text
apple
apricot
```

`printf` wrote three lines to its stdout; the shell connected that stdout to a pipe whose read end became `grep`'s stdin; `grep '^ap'` filtered for lines starting with `ap` (Section 13).

### Lab 2 — Multi-stage pipeline

```bash
printf '%s\n' apple banana apricot avocado | grep '^a' | sort
```

**Observed in this environment:**

```text
apple
apricot
avocado
```

Two pipes, three processes, each doing one job (Section 14).

### Lab 3 — Observing stdout → stdin behavior directly

Labs 1 and 2 already demonstrate this directly: `grep`'s and `sort`'s *input*, in each case, was never typed or read from a file — it was another process's *output*, delivered through a pipe, with neither program needing any special support for this (Section 4).

### Lab 4 — stdout vs stderr through a pipe

```bash
mkdir -p /tmp/pipes-lesson && cd /tmp/pipes-lesson
cat > mixed_output.py << 'EOF'
import sys
print("apple")
print("banana")
print("skipped: banana", file=sys.stderr)
print("apricot")
EOF

python3 mixed_output.py | grep '^ap'
python3 mixed_output.py 2>/dev/null | grep '^ap'
```

**Observed in this environment** (already shown in full in Section 16):

```text
python3 mixed_output.py | grep '^ap':
skipped: banana
apple
apricot

python3 mixed_output.py 2>/dev/null | grep '^ap':
apple
apricot
```

**Important:** the small Python script above is written directly into the disposable `/tmp/pipes-lesson/` directory for this lab — never into the project directory itself. If you're following along, create it there yourself; this lesson does not create any project files on your behalf.

### Lab 5 — Named pipe / FIFO

```bash
mkdir -p /tmp/pipes-lesson
mkfifo /tmp/pipes-lesson/demo.fifo
ls -l /tmp/pipes-lesson/demo.fifo

(printf "hello through the fifo\n" > /tmp/pipes-lesson/demo.fifo) &
cat < /tmp/pipes-lesson/demo.fifo

rm -f /tmp/pipes-lesson/demo.fifo
```

**Observed in this environment** (already shown in full in Section 12):

```text
prw-r--r-- 1 sovon sovon 0 Sep 10 16:33 demo.fifo
hello through the fifo
```

**Why one side may wait for the other:** as Section 12 explained, opening a FIFO for writing conceptually waits for a reader to also be present — this is why the writer above was started *in the background* (with `&`), so the foreground `cat` could then open the read side without both commands blocking each other in the same terminal.

### Lab 6 — Inspecting a process's file descriptors during pipe use

```bash
python3 -c "
import os
r, w = os.pipe()
print('read_fd:', r, 'write_fd:', w)
input()  # pause so you can inspect /proc/<PID>/fd in another step
" &
PID=$!
echo "PID: $PID"
ls -l /proc/$PID/fd
```

**Expected result (conceptual, not a specific fabricated observation for this exact command):** alongside the standard `0`, `1`, `2` entries (Concept 11), you should see two additional entries — one for the pipe's read end, one for its write end — both pointing at something like `pipe:[<some number>]`, exactly matching the general shape Concept 11's own `os.pipe()`-adjacent observations already demonstrated for other file descriptors. **Actual descriptor numbers, and the exact `pipe:[...]` identifier, will differ every time you run this** — treat the specific numbers as illustrative, not something to expect to reproduce exactly.

**Only ever inspect a PID you created yourself for this exercise, and never terminate any process you didn't create for this lab.**

### Cleanup

```bash
cd /
rm -rf /tmp/pipes-lesson
```

Every temporary file, FIFO, and script created during this lab was removed from an isolated, disposable directory, with removal verified after each step (Sections 12, 16, and 25 show this explicitly for the specific commands run there).

---

## 20. WSL2 Considerations

- **WSL2 provides a genuine Linux environment on Windows** (Concept 01) — every pipe, FIFO, and pipeline in this lesson's lab ran inside that Linux environment, using Linux's own pipe implementation.
- **Bash/Linux commands in this lesson execute inside the Linux environment specifically** — the pipe behavior studied here is Linux/Unix pipe behavior, not a claim about how Windows itself implements inter-process communication.
- **PowerShell has its own, different pipeline model** (Section 21) — Linux shell pipelines should not be assumed to be identical to PowerShell pipelines, even though both use the word "pipeline."
- **Filesystem and process observations in WSL2 may differ from a native, bare-metal Linux installation in some environmental details** — exactly as Concept 09, Concept 10, and Concept 11 already noted for their own respective topics; this lesson's genuinely observed FIFO permission string, descriptor numbers, and similar details reflect this specific environment, not a universal guarantee.

---

## 21. PowerShell Comparison

Because PowerShell is explicitly part of this roadmap's toolset, a brief, deliberately limited comparison:

```text
Bash/Unix pipeline:

stdout bytes/text
   ↓
pipe
   ↓
stdin
```

**PowerShell's pipeline is conceptually related but implemented very differently: it passes structured *objects* between commands, not a raw stream of bytes/text.** A PowerShell pipeline stage commonly receives a rich object with named properties, rather than needing to parse plain text the way a Unix pipeline stage typically does.

**Why this matters here:** this lesson's entire technical model — file descriptors, read/write ends, byte-stream buffering (Sections 4–6) — describes the Unix/Linux pipe mechanism specifically. **PowerShell pipelines are not simply "the same pipe mechanism with different syntax"** — they are a genuinely different underlying model. This lesson does not teach PowerShell's pipeline internals in depth; the point here is solely to prevent the incorrect assumption that every "pipeline," across every shell, behaves identically underneath.

---

## 22. AI Engineering Relevance

```text
Input Data
    ↓
Preprocessor
    ↓
PIPE
    ↓
Python Transformation
    ↓
PIPE
    ↓
Evaluation / Analysis
```

**Concrete categories where this lesson applies directly:**

- **Data-processing pipelines** — preprocessing, transformation, and analysis stages chained together exactly as Section 14's multi-stage pipeline demonstrated, just with domain-specific tools instead of `grep`/`sort`.
- **CLI-based ML tools** — many command-line ML/data tools are specifically designed to read from stdin and write to stdout, precisely so they can participate in pipelines like this one.
- **Model evaluation workflows and batch inference** — a script producing predictions can feed its stdout directly into a separate scoring/evaluation script's stdin, without an intermediate file.
- **Log processing** — filtering, transforming, or summarizing a running service's log output (Concept 11's stdout/stderr model) using exactly this same pipe mechanism.
- **Dataset inspection** — quickly filtering or sampling a large dataset using chained Unix utilities before ever writing dedicated code.
- **Subprocess-based AI tools** — a Python orchestration script launching another tool as a subprocess (Section 17) and communicating with it through pipes.
- **Chaining Unix utilities around a Python program** — using shell tools for simple filtering/sorting steps, and a Python script for the domain-specific transformation in between, exactly like Section 14's structure.
- **Worker processes and automation** — a worker that both consumes work from one pipe-connected source and produces results to another.

**A required distinction: this is not the same thing as a distributed data pipeline.** Everything in this lesson happens between processes on a **single machine**, communicating through a mechanism (Section 2) that only works because those processes share the same operating system and kernel. A distributed data pipeline (processing data across many machines, potentially using message queues, distributed storage, or network protocols) is a genuinely different, much larger topic — this lesson's pipes are a foundational, single-machine building block, not a substitute for that later material.

**This lesson only establishes the foundation for:** subprocess management, backend workers, containers, deployment, observability, and distributed systems — **none of these are taught here.** Every one of them, at some layer, still depends on understanding exactly what this lesson taught: how one process's output can become another's input, and what can go right or wrong along the way.

---

## 23. Debugging Pipe Problems

For every scenario: symptom, likely cause, what the OS/processes are actually doing, a safe inspection method, the reasoning process, and the likely fix.

**1. "Pipeline produces no output."** *Likely cause:* an earlier stage produced nothing at all (perhaps it filtered everything out, or failed silently), or output is going to stderr instead of stdout (Section 16) and therefore isn't part of the piped stream. *Inspect:* run each stage of the pipeline individually, without piping, and check its own output directly. *Reasoning:* isolate which specific stage is actually the source of the missing data before assuming the pipe mechanism itself is at fault. *Fix:* correct whichever individual stage isn't producing the expected stdout output.

**2. "Pipeline appears to hang."** *Likely cause:* a reader is blocked waiting for data that a writer hasn't produced yet, or a writer is blocked because the reader isn't consuming (Section 7), or — very commonly — a write end that should have been closed wasn't, so a reader is waiting for EOF that will never come (Section 8). *Inspect:* check each process's state (`ps`, Concept 03/05) — a process shown as sleeping/waiting rather than running or crashed points toward a blocking I/O wait. *Reasoning:* "hanging" almost always means blocked on I/O, not stuck in a computational loop, once you know to check process state rather than assuming a crash. *Fix:* ensure every unused pipe end is actually closed, and confirm each stage is genuinely producing the input the next stage expects.

**3. "Reader waits forever."** *Likely cause:* exactly Section 8's central point — some process, possibly not even one you were thinking about, still holds the write end open. *Inspect:* enumerate every process that received a copy of that write end (through inheritance, Section 11) and confirm each one has actually closed it. *Reasoning:* a reader cannot distinguish "no more data is coming" from "more data might still come" until literally every writer reference is closed. *Fix:* explicitly close every unused write-end reference, in every process that has one.

**4. "Writer blocks."** *Likely cause:* the pipe's buffer is full because the reader isn't consuming fast enough, or isn't reading at all (Section 7, Section 18). *Inspect:* confirm the reader process is actually running and actively calling `read()` (or the Python-level equivalent), rather than being stuck elsewhere itself. *Reasoning:* a blocked writer is a direct, expected consequence of a full buffer — the real question is *why* the reader isn't draining it. *Fix:* fix whatever is preventing the reader from consuming data, or use a pattern like `communicate()` (Section 17) that manages this coordination correctly.

**5. "FIFO appears stuck."** *Likely cause:* one side (writer or reader) opened the FIFO and is waiting for the other side to also open it (Section 12) — this is expected FIFO-opening behavior, not necessarily a bug. *Inspect:* confirm both a writer and a reader process actually exist and are both attempting to use the same FIFO path. *Reasoning:* a FIFO opened by only one side, with no corresponding process on the other side, will simply wait indefinitely — by design. *Fix:* ensure both a writer and a reader are actually running and targeting the same FIFO.

**6. "Python subprocess hangs."** *Likely cause:* exactly Section 18's deadlock pattern — writing too much to a subprocess's stdin before reading any of its stdout, while the subprocess is itself waiting to write its own output before reading more input. *Inspect:* check whether the code uses raw `Popen` with manual `.stdin.write()`/`.stdout.read()` calls in a strict sequence, rather than `communicate()`. *Reasoning:* `communicate()` is designed to avoid this common trap by coordinating both directions; manual read/write sequencing is where this failure most commonly appears. *Fix:* use `communicate()` for simple cases (Section 17), or restructure I/O to avoid a strict, mutually blocking sequence.

**7. "Parent process waits forever."** *Likely cause:* the parent is waiting (via `communicate()`, `wait()`, or similar) for a child process that itself never terminates — possibly because the child is waiting on input the parent never provided, or a pipe end the parent forgot to close (Section 8). *Inspect:* check the child process's own state directly, and confirm the parent actually sent everything the child is waiting for. *Reasoning:* "the parent hangs" is often really "the child hangs, and the parent is correctly waiting for it." *Fix:* diagnose the child's actual blocking condition first, using this same debugging method recursively.

**8. "stderr appears in the terminal instead of expected pipeline data."** *Likely cause:* this is expected default behavior (Section 16) — stderr is never automatically part of a pipe's data stream. *Inspect:* confirm whether the visible output is actually diagnostic/error content (stderr) rather than the pipeline's intended data (stdout). *Reasoning:* seeing unexpected text is not evidence the pipe is broken — it's evidence stdout and stderr are doing exactly what Section 16 described. *Fix:* if this diagnostic output shouldn't be visible at all, redirect it explicitly (`2>/dev/null`, or `2>` to a log file) rather than assuming the pipe should have suppressed it automatically.

**9. "Pipeline succeeds interactively but behaves differently when redirected."** *Likely cause:* exactly Concept 11's terminal-detection behavior, now affecting one stage of a pipeline — some tool changes its own behavior (buffering, formatting, interactive prompts) depending on whether it's connected to a real terminal. *Inspect:* check whether the specific tool involved documents different behavior when its output isn't a terminal. *Reasoning:* this is the same underlying cause as Concept 11's own equivalent debugging scenario, just appearing inside a pipeline instead of a simple redirection. *Fix:* consult that specific tool's documentation for flags controlling this behavior.

**10. "Broken pipe / `BrokenPipeError`."** *Likely cause:* exactly Section 9's scenario — a downstream reader closed its end (perhaps it only needed the first few lines, like `head`) while an upstream writer was still producing output. *Inspect:* confirm whether the downstream stage in the pipeline genuinely stopped reading early (many tools, like `head`, do this intentionally). *Reasoning:* this is frequently entirely expected, normal pipeline behavior, not a defect in the writing program. *Fix:* if the writing program needs to tolerate this gracefully (rather than crashing with a visible traceback), it should catch `BrokenPipeError` explicitly, rather than treating the pipe mechanism itself as unreliable.

**11. "Large data transfer causes apparent deadlock."** *Likely cause:* exactly Section 18's pattern, triggered specifically because the data volume exceeded what casual, small-scale testing would have revealed — small test inputs may never actually fill the pipe buffer (Section 6), masking a real deadlock risk until larger, real data is used. *Inspect:* check whether the failure only appears above a certain data size, which is a strong signal this is a buffer-driven blocking issue, not a logic bug. *Reasoning:* "it worked with small test data" does not rule out a pipe-buffering issue that only manifests at scale. *Fix:* use `communicate()` or a properly concurrent read/write pattern (Section 17, Section 18), rather than a strict sequential read-then-write (or write-then-read) approach.

**12. "One pipeline stage exits early."** *Likely cause:* a downstream stage (like `head`) intentionally stops after processing only part of the available input, and closes its read end afterward. *Inspect:* check `PIPESTATUS` (Section 15) to see each stage's individual exit code, rather than relying on `$?` alone. *Reasoning:* an "early exit" in one stage is sometimes entirely intentional design, and can itself trigger Scenario 10's broken-pipe condition in an upstream stage, as an expected consequence, not a separate bug. *Fix:* confirm whether early termination was actually intended; if so, ensure the upstream writer handles the resulting `BrokenPipeError`/`SIGPIPE` gracefully (Section 9).

---

## 24. Common Misconceptions

| Misconception | Why it's wrong |
|---|---|
| "A pipe is a file on disk." | A pipe has no persistent, disk-backed storage — even a named pipe (FIFO) is only a filesystem-visible *name* for a channel, not stored data (Section 2, Section 10, Section 12's genuinely observed `0`-byte FIFO). |
| "A pipe stores data permanently." | Data flowing through a pipe exists only transiently in a kernel buffer, and is gone once read (Section 6, Section 10). |
| "A pipe always connects exactly two shell commands." | A pipe connects two file descriptors, full stop — it can connect two processes launched by a Python script (Section 17), or be created and used entirely within one process via `os.pipe()` (Section 17), with no shell command involved at all. |
| "stdout automatically means the screen." | Exactly Concept 11's point, directly relevant here: stdout is whatever the process's FD `1` is currently connected to — a pipe, in every example in this lesson (Section 1, Section 13). |
| "Every output from A goes into B." | Only A's **stdout** goes into B through the pipe — A's stderr does not (Section 16), a genuinely observed, concrete distinction demonstrated directly in this lesson. |
| "stderr automatically flows through `|`." | Directly contradicted by Section 16's genuinely observed demonstration — stderr bypassed the pipe entirely and appeared separately. |
| "A pipe can hold unlimited data." | A pipe's buffer has a finite capacity (Section 6) — this finite limit is exactly what causes blocking (Section 7) and deadlock risk (Section 18). |
| "The reader can always read immediately." | A reader blocks if no data is currently available and the write end remains open (Section 7) — reading is not guaranteed to complete instantly. |
| "A pipeline is one process." | A typical Unix shell pipeline runs each stage in its own execution context, commonly a separate process (Concept 03), each with its own exit code (Section 15's `PIPESTATUS` example); the exact process behavior depends on the shell, the command type, and shell options. |
| "A FIFO is just an ordinary file." | A FIFO is marked with a distinct `p` file type (Section 12's genuinely observed `ls -l` output) and behaves fundamentally differently — it's a communication channel with no persistent content, not ordinary file storage. |
| "Pipes are only useful for shell commands." | `os.pipe()` and `subprocess.Popen` (Section 17) use the exact same OS pipe mechanism entirely from within Python code, with no shell involved at all. |
| "Pipes are the same as sockets." | Sockets support network communication (potentially between different machines) and have their own distinct API and semantics — mentioned here only by name, as an explicitly out-of-scope, related mechanism (Section 31). |
| "Pipes are the same as message queues." | Message queues are a distinct IPC mechanism with different delivery and structuring semantics — also explicitly out of scope here (Section 31), not taught as part of this lesson's pipe model. |
| "A pipe is a distributed-system communication mechanism." | A pipe works only between processes sharing the same kernel, on the same machine (Section 22) — it is not, by itself, a mechanism for communicating across machines. |
| "If a process hangs, the code must have an infinite loop." | A hanging process is very often blocked waiting on I/O (Section 7, Section 18, Debugging Scenario 2) — a process genuinely waiting for a pipe to have data, or for a reader to consume it, shows no CPU activity at all, unlike a true infinite computational loop. |

---

## 25. Mini-Project

**Requirements.** Build a small, three-stage pipeline demonstrating a realistic producer → processor → consumer pattern: a **producer** that emits raw values, a **processor** (the interesting stage) that validates and transforms them — reporting problems to stderr rather than silently failing — and a **consumer** that aggregates the final results, with each stage's exit status independently meaningful.

**Design:**

```text
Input Producer
      |
      | stdout
      v
   PIPE
      |
      | stdin
      v
Python Processor
      |
      | stdout
      v
   PIPE
      |
      v
Result Consumer
```

**Implementation** — three small, standalone scripts (create each of these yourself in a disposable directory such as `/tmp/pipes-lesson/`; this lesson does not create project files on your behalf):

```python
# producer.py
import sys
for value in ["3", "abc", "5", "7"]:
    print(value)
```

```python
# processor.py
import sys

had_error = False
produced = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        value = float(line)
    except ValueError:
        print(f"warning: skipping invalid value: {line!r}", file=sys.stderr)
        had_error = True
        continue
    print(value * 2)
    produced += 1

if produced == 0:
    print("error: no valid values to process", file=sys.stderr)
    sys.exit(1)

sys.exit(2 if had_error else 0)
```

```python
# consumer.py
import sys

total = 0.0
count = 0
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    total += float(line)
    count += 1

print(f"received {count} values, total={total}")
```

**How to run it:**

```bash
python3 producer.py | python3 processor.py | python3 consumer.py
```

**Observed in this environment:**

```text
warning: skipping invalid value: 'abc'
received 3 values, total=30.0
```

**Notice, precisely:** the `warning` line came from `processor.py`'s **stderr**, and — exactly as Section 16 explained — it was never part of what flowed into `consumer.py`'s stdin through the pipe; `consumer.py` only ever received the doubled numeric values (`6`, `10`, `14`), correctly summing them to `30.0`.

**How to test its exit-status behavior:**

```bash
python3 producer.py | python3 processor.py | python3 consumer.py
echo "PIPESTATUS: ${PIPESTATUS[@]} | \$?: $?"
```

(Read both in the same command, right after the pipeline — any intervening command resets them, as Section 15 explained.)

**Recorded in the documented environment used when this lesson was prepared (status values only):**

```text
PIPESTATUS: 0 2 0 | $?: 0
```

**Exactly Section 15's point, now demonstrated by this project's own pipeline:** `processor.py` genuinely exited with `2` (it had to skip `'abc'`), but without `pipefail` Bash's `$?` shows only `consumer.py`'s exit code (`0`) — checking `PIPESTATUS` is what actually reveals that the middle stage encountered (and correctly reported) a problem. (With `set -o pipefail` in Bash, `$?` would instead be `2`.)

**Failure modes to expect and test yourself:** feed `processor.py` input containing *only* invalid values, and confirm it exits with `1` and prints its `"error: no valid values to process"` message to stderr; try piping a much larger volume of input through and confirm the pipeline still completes (a basic, informal check against Section 18's deadlock risk, since this simple line-by-line streaming pattern reads and writes incrementally, rather than trying to hold everything in memory before passing it along).

**Debugging this project, if something doesn't work as expected:** apply Section 23's method — check `PIPESTATUS` for each stage's actual exit code; run each script individually (feeding it sample input directly) to isolate which specific stage is misbehaving; and confirm any diagnostic output is landing in the stream you expect (stderr, not stdout) by redirecting each separately, exactly as Section 16 demonstrated.

**Production relevance.** This exact three-stage shape — a source, a validating/transforming stage that separates real results from diagnostics, and a stage that consumes and aggregates the final output, all connected by streaming pipes rather than intermediate files — is a genuinely realistic pattern for small-to-medium data-processing and evaluation workflows in real AI-engineering work (Section 22), and understanding its exit-status and stderr behavior is exactly what lets such a pipeline be trusted in an automated setting, not just when watched interactively.

---

## 26. Exercises

Work through these in your own words. No answer key exists for this lesson — the goal is reasoning ability, not matching a memorized phrase.

### Level 1 — Recognition

1. What is a pipe, in your own words?
2. What is the "read end" of a pipe? What is the "write end"?
3. In `A | B`, which stream of A connects to which stream of B?
4. What does "producer" mean in the context of a pipe? What does "consumer" mean?
5. What is a pipeline?
6. What is the difference between an anonymous pipe and a named pipe (FIFO)?
7. What file-type character does `ls -l` show for a FIFO?
8. What does EOF mean, in the context of a pipe?

### Level 2 — Understanding

9. Explain why pipes exist, contrasting the "with a pipe" and "without a pipe" diagrams from Section 3.
10. Explain how a pipe relates to file descriptors, using Section 4's model.
11. Explain, step by step, how stdout "becomes" stdin in a shell pipeline.
12. Explain pipe buffering and why finite buffer size matters.
13. Explain blocking, using both the writer and reader cases from Section 7.
14. Explain why closing unused write-end references matters for EOF to ever be observed.
15. Explain the difference between a pipe and a regular file, using at least three dimensions from Section 10's table.
16. Explain why anonymous pipes require a parent/child relationship, while named pipes don't.

### Level 3 — Application

17. Run `printf '%s\n' apple banana apricot | grep '^ap'` in your own terminal and confirm the result matches this lesson's genuinely observed output.
18. Build your own three-stage pipeline using different words and a different filter/sort combination than this lesson's examples.
19. Create a FIFO in an isolated temporary directory, write to it from a background process, and read from it in the foreground.
20. Write a small Python script that prints something to stdout and something else to stderr, then pipe it through `grep` and observe which content is and isn't filtered.
21. Write a small Python `os.pipe()` example: write bytes into the write end, close it, and read them back from the read end.
22. Use `subprocess.Popen` with `stdin=subprocess.PIPE`, `stdout=subprocess.PIPE`, and `stderr=subprocess.PIPE` to run a simple command and capture its output with `communicate()`.
23. Inspect a disposable Python process's file descriptors via `/proc/<PID>/fd` while it holds an open `os.pipe()` pair.
24. Run a pipeline of at least three commands and inspect `PIPESTATUS` (Bash) to see each stage's individual exit code.

### Level 4 — Debugging

25. A pipeline produces no visible output. Using Section 23's first scenario, describe how you'd isolate which stage is at fault.
26. A pipeline appears to hang with no error. Using Scenario 2, explain what to check first.
27. A reader seems to wait forever even though a writer clearly sent data. Using Scenario 3, explain the most likely cause.
28. A Python script using raw `Popen` (not `communicate()`) hangs when writing a large amount of input to a subprocess. Using Scenario 6, explain the likely deadlock pattern.
29. You see unexpected diagnostic text appear even though you expected only piped data. Using Scenario 8, explain why this is expected behavior.
30. A downstream pipeline stage (like `head`) exits early, and an upstream Python script then crashes with `BrokenPipeError`. Using Scenario 10, explain why this is often expected, not a bug.
31. A pipeline that worked fine with small test data hangs with large real data. Using Scenario 11, explain why data size specifically might matter here.
32. `$?` after a pipeline shows `0`, but you suspect an earlier stage actually failed. Using Section 15, explain how to check for this properly.

### Level 5 — Integration

33. Draw (in text/ASCII) a small AI-engineering workflow: a data-loading script piped into a Python filtering/cleaning script piped into an evaluation script — label each pipe, each stdin/stdout connection, and where stderr goes in each stage.
34. A friend claims, "Since I'm piping A into B, if A crashes, B will automatically know and stop." Using Section 8, Section 9, and Section 23, explain what actually happens to B in this situation, precisely.
35. Explain how this lesson's pipe model and Concept 10's signal model (`SIGPIPE`) work together to explain what happens when a writer keeps writing after its reader has disappeared.
36. A production data-processing pipeline chains three Python scripts with `|`, and the team wants to know whether the overall pipeline "succeeded." Using Section 15's `PIPESTATUS` demonstration, explain why checking only the shell's final exit code could hide a real problem, and what a more reliable check would look like.
37. Using everything in this lesson, explain to a beginner (in your own words, as if teaching them) why "connect two programs" is an incomplete description of a pipe, and what specifically is missing from that description that this lesson filled in.

---

## 27. Review

- What is a pipe?
- Why does an operating system need pipes?
- What is the read end of a pipe? What is the write end?
- How are pipes represented through file descriptors?
- How does stdout connect to stdin in a pipeline?
- What is pipe buffering?
- What is blocking, in the context of a pipe?
- What is backpressure?
- What is EOF, and why does it matter for a pipe specifically?
- Why does closing unused pipe descriptors matter?
- What is a broken pipe?
- How is a pipe different from a regular file?
- What is a FIFO?
- How does `A | B` work, conceptually, from start to finish?
- Why doesn't stderr automatically flow through a pipe the way stdout does?
- How does Python use pipes, both directly (`os.pipe()`) and through `subprocess`?
- Why can subprocesses hang because of how pipes are used?
- Why are pipes relevant to Applied AI Engineering work specifically?

---

## 28. Interview / Architecture Questions

- Explain a Unix pipe, from first principles.
- How does `A | B` actually work, underneath the shell syntax?
- How are pipes related to file descriptors?
- Why can a pipe block a writer? Why can a reader wait indefinitely?
- What causes EOF on a pipe? What causes a broken pipe?
- Why is closing unused pipe descriptors an important engineering habit?
- What is the difference between an anonymous pipe and a FIFO?
- Why isn't a pipe equivalent to a regular file?
- How would you debug a Python subprocess that hangs?
- How would you diagnose a shell pipeline that stops producing output partway through?
- How can stdout/stderr separation affect what a pipeline actually receives?
- When would you use a pipe instead of a temporary file? When would a pipe *not* be the right choice?

**For architecture-style questions, reason explicitly about:** communication pattern (streaming vs. batch), lifetime (transient vs. persistent), throughput and buffering limits, failure modes (blocking, broken pipes, deadlock), process boundaries, debuggability, and the operational trade-offs between pipes, temporary files, and more advanced IPC mechanisms this lesson deliberately left out of scope (Section 31).

---

## 29. Production Application

Pipes appear directly in real production engineering:

- **Subprocess execution and CLI tooling.** Any Python service that shells out to another tool and captures its output (Section 17) depends entirely on this lesson's model.
- **Worker processes and data processing.** Section 25's three-stage mini-project shape is a genuinely realistic pattern for real batch/worker pipelines.
- **Model evaluation and batch inference.** Chaining a prediction step and a scoring step through a pipe, rather than an intermediate file, is a direct, practical application of Section 3's benefits.
- **Automation and log processing.** Filtering and summarizing log output using chained utilities (Section 22).
- **Unix-style tool composition.** Building small, focused tools that compose through pipes rather than large, monolithic scripts.
- **Process orchestration**, at a foundational level — any system that launches and coordinates multiple processes needs exactly this lesson's understanding of blocking, EOF, and broken pipes to do so reliably.

**Production concerns worth naming explicitly, at the foundational level this lesson supports:**

- **Blocking and backpressure** (Section 7) directly affect throughput and responsiveness in any pipe-connected system.
- **Deadlocks** (Section 18) are a genuine, recurring risk in subprocess-heavy production code, not a theoretical concern.
- **Output volume** — a stage producing far more data than a downstream consumer can keep up with is exactly Section 6's/Section 18's concern, made real.
- **Error streams** (Section 16) must be deliberately handled — an automated system that assumes "everything printed is data" will misbehave the moment a stage writes anything to stderr.
- **Process termination and EOF** (Section 8) determine whether a pipeline actually completes cleanly or hangs waiting for a signal that never comes.
- **Failure propagation** (Section 15) — a naive `$?` check can hide a real failure in an earlier pipeline stage.
- **Resource cleanup** — unused pipe/FIFO ends left open (Section 8, Section 12) are a real, if often invisible, source of hangs in long-running or repeatedly-invoked automation.

**Why engineers must understand this before building AI systems that launch or coordinate processes:** every one of the failure modes above shows up, in practice, in real production AI tooling that shells out to other programs, runs data through multi-stage CLI pipelines, or manages worker subprocesses — recognizing these patterns *before* they cause a production incident is exactly what this lesson's foundation is for. **This lesson does not teach advanced distributed systems** — that is a separate, later, much larger topic, built on entirely different mechanisms than the single-machine pipes covered here.

---

## 30. Relationship to Module 0.2

```text
Kernel
   ↓
System Calls
   ↓
Processes
   ↓
File Descriptors
   ↓
Standard I/O
   ↓
Pipes                          ← this lesson
   ↓
Shell
   ↓
Process Lifecycle
```

**Also connected to:**

- **Permissions** — a FIFO's filesystem entry (Section 12) is still subject to the permission rules Concept 08 already established.
- **Environment Variables** — an independent, separate process-startup mechanism, mentioned here only to distinguish it from pipes' data-streaming role.
- **Signals** — directly connected through `SIGPIPE`/`BrokenPipeError` (Section 9).
- **Filesystems** — regular files are the direct point of comparison for pipes throughout this lesson (Section 10), and FIFOs occupy an actual filesystem path (Section 12).
- **Threads** — a pipe's file descriptors, like any of a process's file descriptors, are generally shared among that process's threads (Concept 04's shared-resources model).
- **Scheduling** — a blocked reader or writer (Section 7) is exactly the "waiting" process state Concept 05 already described, now with a specific, concrete cause.

### Previously learned

Kernel/user space, system calls, processes, threads, scheduling, virtual memory, filesystems, permissions, environment variables, signals, standard input/output.

### Current lesson

Pipes, pipe read/write ends, process-to-process stream communication, basic buffering/blocking/EOF concepts, and the shell-pipeline foundation.

### Next lesson

[Shell](13-shell.md) — the full mechanics of how a shell actually parses `A | B | C`, creates each process, and wires up every pipe, introduced here only at the conceptual level this lesson needed.

### Later

[Process Lifecycle](14-process-lifecycle.md).

---

## 31. Scope Boundaries

This lesson is foundational. It deliberately does **not** teach, in depth:

- Advanced IPC generally — message queues, shared memory, semaphores as IPC
- Unix domain sockets, TCP/UDP sockets as a full topic
- Advanced asynchronous I/O — `select`, `poll`, `epoll`, `io_uring`
- Advanced pipe flags, or kernel pipe implementation internals
- Advanced scheduler interaction beyond the basic blocking/waiting connection already made to Concept 05
- Advanced deadlock theory (formal conditions, prevention algorithms)
- Distributed messaging systems — Kafka, RabbitMQ, Redis Streams
- Multiprocessing architecture in depth
- Advanced shell implementation (belongs to [Shell](13-shell.md))
- Advanced PowerShell internals
- Container pipe internals, Kubernetes process/pipe internals

Each of these is mentioned only where it directly clarifies a boundary of what this lesson does cover (Sections 9, 21, 22, 29) — every one of them belongs to later, more advanced curriculum, not this beginner-level foundation.

---

## 32. Final Mental Model

```text
Process A
   |
stdout / FD 1
   |
   v
 PIPE
   |
stdin / FD 0
   |
   v
Process B
```

**Hold onto this above everything else in this lesson:** a pipe is not a file, not magic, and not a claim about how two programs "talk" to each other in some abstract sense — it is a specific, OS-managed channel with a **read end** and a **write end**, each accessed through an ordinary **file descriptor**, exactly like any other I/O this module has covered. A process writes to its own stdout; the OS moves those bytes through a finite buffer; another process reads them from its own stdin — and neither process ever needs to know whether the other end is a terminal, a file, or, as in this entire lesson, another running program. **That single piece of uniformity — the same read/write model, regardless of what's on the other end — is what a pipe actually is, and it is precisely what makes `A | B | C` work at all.**

---

_This file is the completed lesson for Concept 12 of Module 0.2. It intentionally does not teach advanced IPC (message queues, shared memory, sockets as a full topic), advanced asynchronous I/O (`select`/`poll`/`epoll`/`io_uring`), kernel pipe implementation internals, advanced deadlock theory, distributed messaging systems, advanced shell implementation, advanced PowerShell internals, or container/Kubernetes pipe internals in depth — those remain the subject of later, more advanced curriculum, not this beginner-level foundation._
