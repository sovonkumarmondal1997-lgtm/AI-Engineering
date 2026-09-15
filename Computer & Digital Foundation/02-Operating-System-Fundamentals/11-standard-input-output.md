# 11. Standard Input / Output

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Module 0.2 — Operating System Fundamentals
**Concept(s) covered:** standard input/output, file descriptors, stdin/stdout/stderr, redirection
**Status:** Not Started

---

## Learning Objectives

By the end of this lesson you should be able to explain, in your own words:

- what standard input, standard output, and standard error are
- why operating systems provide these as *standard* streams, established for every process
- how file descriptors represent these streams on Unix/Linux, and why file descriptors `0`, `1`, and `2` are conventional rather than arbitrary
- how a process receives input and produces output, and why "input" doesn't inherently mean "keyboard" and "output" doesn't inherently mean "screen"
- how shell redirection (`>`, `>>`, `<`, `2>`, `2>&1`) works at both a conceptual and practical level
- how standard streams set up the foundation for pipes (the next lesson)
- how Python programs read from and write to `stdin`, `stdout`, and `stderr`
- how standard I/O behaves in a real service, worker, or batch job
- how to diagnose common standard-I/O-related failures using a systematic method, not guesswork

## Prerequisites

This lesson builds directly on:

- [Kernel and User Space](01-kernel-and-user-space.md) and [System Calls](02-system-calls.md) — a process interacts with I/O resources through the same kernel-mediated system-call mechanism already introduced.
- [Processes](03-processes.md) — standard streams are part of a process's resources, established at creation and inherited exactly like the environment (Concept 09).
- [Permissions](08-permissions.md) — accessing a file a stream is redirected to is still subject to the permission rules already covered.
- [Environment Variables](09-environment-variables.md) and [Signals](10-signals.md) — both are referenced directly (Sections 15–16) as *different* process-communication mechanisms from standard I/O.

None of these lessons are repeated here — only the specific pieces this lesson needs are reused.

---

## 1. What Is Input and Output?

**Starting from the everyday idea.** Any useful program eventually needs to communicate with something outside itself: it needs to *receive* information to work with (**input**), and it needs to *produce* results or messages (**output**). Together, this is usually called **I/O** — input/output.

**A simple analogy, before any technical model: a kitchen.** A cook (the program's computation) takes raw ingredients (input), transforms them through a process (cooking — the actual computation), and produces a finished dish (output). The cooking itself — chopping, mixing, heating — is not input or output at all; it's the actual work. Input is what comes *in* before the work happens; output is what goes *out* once it's done (or as it's happening).

**Three genuinely distinct things this lesson keeps carefully separate:**

| | What it is | Example |
|---|---|---|
| **Program computation** | The actual work — logic, calculations, decisions | Adding two numbers, running a model's forward pass |
| **Input** | Information a program receives from outside itself | A typed value, a line from a file, data piped in from another program |
| **Output** | Information a program sends outward | A printed result, a line written to a log, a value returned to a caller |

**Examples from simple programs:** a program that asks "What is your name?" and then greets you is reading input (your typed name) and producing output (the greeting).

**Examples from services and workers:** a running AI inference service reads input (an incoming request), does computation (running the model), and produces output (a response, and separately, log messages about what it did — Section 6 explains why these are kept separate).

**The relationship between CPU computation and I/O:** Concept 05 (Scheduling) already introduced the idea that a process spends some of its time actively computing (CPU-bound) and some of its time waiting (I/O-bound). Input and output are exactly the kind of activity that can involve *waiting* — waiting for a user to type something, waiting for a file to be read, waiting for another program to send data. This lesson explains *what* these input/output channels actually are; Concept 05 already explained how the OS schedules a process around the waiting they can involve.

---

## 2. Why Standard Streams Exist

**The problem.** Every single program that needs input or output could, in principle, invent its own private way of receiving and producing data — but if every program did this differently, no two programs could easily work together, and the operating system would have no consistent way to connect a program to a terminal, a file, or another program.

**Standard streams** are the operating system's and process model's answer: **every process is automatically given three predictable, always-present communication channels the moment it starts** — one for receiving input, and two for producing output (Section 3 explains why there are two, not one).

**Why they're called "standard.":** they are *standardized* — every process, regardless of what programming language it's written in or what it actually does, has exactly these same three channels, always identified the same way (Section 4). A program doesn't need to ask "does this environment even have a way for me to receive input?" — the answer is always yes, and it always works the same way.

**Why this makes programs composable.** Because every program reads from the same kind of input channel and writes to the same kind of output channel, one program's output can become another program's input (Section 13's pipe foundation) — without either program needing to know anything special about the other. This uniformity is precisely what makes chains of small, independent programs able to work together, a foundational Unix design idea this lesson is building toward.

---

## 3. stdin, stdout, stderr

There are exactly three standard streams:

- **stdin** (standard input) — where a process reads input *from*.
- **stdout** (standard output) — where a process writes its normal, expected output *to*.
- **stderr** (standard error) — where a process writes diagnostic or error information *to*, kept deliberately separate from stdout (Section 6).

**Each one is represented by a small, specific integer, called a file descriptor (fully explained in Section 4):**

```text
0 → stdin
1 → stdout
2 → stderr
```

**Do not just memorize these three numbers — understand why they exist as numbers at all.** A process needs *some* consistent way to refer to "my input channel" or "my output channel" when asking the operating system to read or write. Rather than every program needing special, named handles, the operating system model uses small integers (file descriptors), and reserves the first three — `0`, `1`, and `2` — by convention, for exactly these three standard streams, for every single process, without exception. Section 4 explains the full concept these numbers belong to.

---

## 4. File Descriptors

**File descriptor.** Simple meaning: a small number a process uses to refer to something it can read from or write to. Technical meaning: a file descriptor is a process-local integer handle, maintained by the kernel in that process's own file descriptor table, referring to an open I/O resource the process has been given access to.

**Why the name contains "file," even though it can mean much more than a disk file.** Historically, and still today in the underlying Unix model, *almost anything* a process reads from or writes to — a real disk file, a terminal, a pipe, a network socket — is represented through this same uniform "file descriptor" abstraction. The name reflects that everything is accessed through the same kind of handle and the same basic operations (Section 7), **not** that every file descriptor literally refers to a file sitting on a disk.

**The relationship between a process and its file descriptor table.** Every process has its own private table mapping small integers to actual, currently-open I/O resources. `0`, `1`, and `2` are simply the first three entries every process starts with, pre-filled in with its standard streams — a process can also open additional files (getting descriptor `3`, `4`, and so on) as it runs, exactly as Section 17's practical lab demonstrates directly.

**A file descriptor can refer to many different kinds of underlying object:**

- A **terminal** (an interactive session, Section 5)
- A **regular file** (Concept 07)
- A **pipe** (Section 13's foundation for the next lesson)
- A **socket** (a network communication endpoint — mentioned here only by name; full treatment is out of this lesson's scope, Section 28)
- Other OS-managed I/O objects this lesson does not enumerate exhaustively

**A conceptual model:**

```text
Process
  |
  +-- FD 0 → stdin
  +-- FD 1 → stdout
  +-- FD 2 → stderr
```

**The single most important idea in this section: the exact underlying object connected to a given descriptor can change, while the descriptor number itself stays the same.** FD `1` is *always* "this process's stdout" from the process's own point of view — but what stdout is actually *connected to* (a terminal screen, a file, a pipe) can be different every time the process is started. Section 11 and Section 12 build directly on this exact point.

---

## 5. Terminal and Standard I/O

**What happens when a program runs interactively in a terminal:**

```text
Keyboard
   ↓
Terminal
   ↓
stdin (FD 0)
   ↓
Process

Process
   ↓
stdout (FD 1)
   ↓
Terminal
   ↓
Screen
```

**stderr follows a separate path, conceptually:**

```text
Process
   ↓
stderr (FD 2)
   ↓
Terminal
   ↓
Screen                (by default, also visible on screen — but through a separate stream)
```

**Three required clarifications, correcting common beginner assumptions:**

- **Keyboard input is not magically delivered directly to Python.** It passes through the terminal, which is itself a piece of OS-managed infrastructure participating in this flow — not a direct, invisible wire straight into your program.
- **stdout does not inherently mean "screen."** It is simply "this process's designated output channel" — which *happens*, by default, in an interactive terminal session, to be connected to the screen. Section 11 shows directly how this same stdout can just as easily be connected to a file instead, with the process never needing to know the difference.
- **stdin does not inherently mean "keyboard."** Just like stdout, it's simply "this process's designated input channel" — which *happens*, by default, in an interactive session, to be connected to the keyboard (via the terminal). It can just as easily be connected to a file (Section 11) or another program's output (Section 13).

**A genuinely observed illustration of exactly how non-obvious this can be.** While preparing this lesson, inspecting this specific automated environment's own shell showed:

```text
$ readlink /proc/self/fd/0
/dev/null
```

**This environment's own FD 0 pointed to `/dev/null`** (a special, "discard everything"/"nothing here" device) — **not a keyboard at all**, because this particular shell session is run by an automated tool, not a human sitting at an interactive terminal. This is a direct, concrete demonstration of this section's core point: stdin is whatever the process was actually given at startup — nothing about "stdin" guarantees a keyboard is involved. A genuine interactive terminal session would typically show something like `/dev/pts/0` here instead — shown as **example output** below, since it was not what this specific automated environment actually produced:

```text
Example output, in a genuine interactive terminal session:
0 -> /dev/pts/3
1 -> /dev/pts/3
2 -> /dev/pts/3
```

---

## 6. stdout vs stderr

**Why two separate output streams exist, rather than just one.** A running program frequently has two genuinely different kinds of things to say: its actual, intended **results** (the reason it was run at all), and **diagnostic information** about what it's doing, warnings, or errors. Keeping these separate — as **stdout** and **stderr** respectively — lets each be handled differently without the two ever being mixed together by accident.

```text
stdout → normal results          (the actual output the program exists to produce)
stderr → diagnostics/errors        (warnings, error messages, progress information)
```

**stderr is not simply "another kind of exception."** A program can write perfectly normal, non-crashing diagnostic messages to stderr — a warning that a particular input line was skipped (exactly like Section 22's mini-project), a progress update, or an informational log line. Conversely, a program can also write ordinary results to stdout even while something has gone slightly wrong elsewhere. **stderr is a *destination* for a *category* of message (diagnostics), not a synonym for "an exception occurred."**

**Why the separation is operationally useful:** if stdout and stderr were combined into a single stream, a program consuming another program's *results* (Section 13's pipe foundation) would have no reliable way to separate the actual data it needs from unrelated diagnostic chatter mixed into the same stream. Keeping them separate lets a script capture and use *just* the results (stdout) while a human or a logging system separately reviews *just* the diagnostics (stderr) — exactly the pattern Section 22's mini-project builds directly.

**A genuinely observed illustration**, from this lesson's own practical lab (Section 17 shows the full context):

```python
import sys
print("normal result", file=sys.stdout)
print("diagnostic message", file=sys.stderr)
```

**Observed in this environment**, with the two streams captured to separate files:

```text
stdout_only.txt:  normal result
stderr_only.txt:  diagnostic message
```

**Connecting this to real production services:** a well-behaved production service writes its actual results (an API response, a computed value) through one channel, and its operational diagnostics (startup messages, warnings, error traces) through a separate one — exactly this same stdout/stderr separation, at the OS level (Section 19, Section 26).

---

## 7. Standard I/O and System Calls

**Connecting directly to [System Calls](02-system-calls.md), without repeating that lesson.** Reading from or writing to any file descriptor — including the standard streams — is, underneath, exactly the kind of kernel-mediated operation Concept 02 already introduced in general.

```text
Application                (your Python code)
    ↓
Library/runtime             (Python's own standard library, built on a lower-level C library)
    ↓
System call                  (a controlled request crossing into the kernel — Concept 02)
    ↓
Kernel
    ↓
I/O resource                  (a terminal, a file, a pipe — whatever this descriptor
                                currently refers to, Section 4)
```

**Four operations worth naming, at a beginner-appropriate level, without turning this into a kernel-programming lesson:**

- **`open`** — conceptually, establishing a new file descriptor connected to some I/O resource (Concept 07 already covered files specifically; this is the general pattern, applied to any I/O resource).
- **`read`** — retrieving data from a file descriptor.
- **`write`** — sending data to a file descriptor.
- **`close`** — releasing a file descriptor when a process is done using it.

**Why this lesson does not go further into these:** the exact system-call-level mechanics of `read`/`write`/`open`/`close` — their precise arguments, error handling, and low-level behavior — belong to more advanced systems-programming material, not this foundational lesson. What matters here is only the *shape* of the relationship: reading `stdin` or writing to `stdout`/`stderr` from Python (Section 8) is never a purely "in-Python" operation — it always, ultimately, involves this same request crossing into the kernel.

---

## 8. Standard I/O in Python

Python provides two related ways to work with standard streams:

- **Convenience functions** — `input()` (reads from stdin) and `print()` (writes to stdout by default).
- **Direct stream objects** — `sys.stdin`, `sys.stdout`, `sys.stderr`, giving more explicit control, including the ability to write specifically to stderr.

**The conceptual relationship between these Python objects and OS-level file descriptors:** `sys.stdin`, `sys.stdout`, and `sys.stderr` are Python-level objects that the interpreter sets up, at startup, to correspond to this process's file descriptors `0`, `1`, and `2` respectively (Section 3). Calling `input()` or `print()` doesn't invent a new channel — it's simply a convenient, higher-level way of using exactly the same three streams this whole lesson has been describing.

```python
import sys

input()          # reads a line from sys.stdin  (FD 0)
print(...)        # writes to sys.stdout by default (FD 1)
print(..., file=sys.stderr)   # writes to FD 2 instead
```

---

## 9. Reading from stdin

**A small, complete example:**

```python
name = input("Name: ")
print(f"Hello, {name}")
```

**The execution flow, not just the code:**

1. `input("Name: ")` writes the prompt `"Name: "` to stdout (Section 3), *without* a trailing newline.
2. It then reads a single line from stdin (Section 3) — waiting, if necessary, until a line actually becomes available.
3. Whatever was read (with the trailing newline removed) becomes the value of `name`.
4. `print(f"Hello, {name}")` writes the greeting to stdout.

**A genuinely observed illustration**, feeding this exact program a piped input (not typed interactively, since this lesson's automated environment has no real keyboard — Section 5):

```bash
echo "Ada" | python3 greet.py
```

**Observed in this environment:**

```text
Name: Hello, Ada
```

**Why this looks like one line, not two — an important, precise detail.** `input("Name: ")` writes its prompt *without* a newline, so it doesn't visually separate from whatever comes next. Here, stdin was *piped* (Section 13's foundation) rather than typed at a live keyboard, so there was no interactive echoing of `"Ada\n"` back onto the screen the way a real terminal would show as you typed it — the program simply read `"Ada"` from the piped stream, and `print(f"Hello, {name}")` immediately followed it with `"Hello, Ada"` on the very same visual line as the prompt. This is a genuine, directly observed illustration of exactly Section 5's point: stdin's actual source (a live keyboard, versus piped data) can change what you visually see, even though the *code* never changes at all.

---

## 10. Writing to stdout and stderr

```python
print("this goes to stdout by default")
print("this goes to stderr", file=sys.stderr)
```

**Why an engineer might intentionally write to stderr:** to keep diagnostic, warning, or progress information visibly and functionally separate from the program's actual results (Section 6) — so that a script consuming this program's real output (Section 13) never has to filter diagnostic noise out of it.

**A genuinely observed demonstration of the difference**, using the same code shown in Section 6:

```bash
python3 streams_demo.py > stdout_only.txt 2> stderr_only.txt
```

**Observed in this environment:**

```text
stdout_only.txt:  normal result
stderr_only.txt:  diagnostic message
```

Each stream landed in a completely separate file — direct, genuine confirmation that they are two independent channels, not one.

---

## 11. Shell Redirection

Shell redirection lets you change what a stream is actually connected to, without changing the program's code at all (Section 4's core point, applied directly).

| Syntax | Effect |
|---|---|
| `>` | Redirect stdout to a file, **overwriting** it |
| `>>` | Redirect stdout to a file, **appending** to it |
| `<` | Redirect stdin to read from a file, instead of the terminal |
| `2>` | Redirect stderr to a file, overwriting it |
| `2>>` | Redirect stderr to a file, appending to it |
| `2>&1` | Redirect stderr to wherever stdout is *currently* going |

**Why `>` normally affects stdout, and `2>` affects stderr:** the number before `>` is exactly the file descriptor being redirected (Section 3, Section 4) — no number defaults to `1` (stdout); `2` explicitly targets stderr.

**Genuinely observed demonstrations, all from this lesson's own practical lab (Section 17 shows the complete context):**

```bash
echo "first line" > out.txt
cat out.txt
```

**Observed:** `first line`

```bash
echo "second line" >> out.txt
cat out.txt
```

**Observed:** `first line` then `second line` — confirming append, not overwrite.

```bash
cat < out.txt
```

**Observed:** `first line` and `second line` — `cat` read its input from the file, via redirected stdin, rather than from the terminal.

```bash
ls out.txt missing.txt > listing.txt 2> errors.txt
```

**Observed:**

```text
listing.txt (stdout): out.txt
errors.txt (stderr):  ls: cannot access 'missing.txt': No such file or directory
```

`ls` produced *both* a normal result (the existing file's name) and an error (the missing file) in the exact same command — and redirection cleanly separated them into two different files, a direct, genuine demonstration of Section 6's entire point.

**Combined redirection with `2>&1`:**

```bash
ls out.txt missing.txt > combined.txt 2>&1
```

**Observed**, both messages landing in the same file:

```text
ls: cannot access 'missing.txt': No such file or directory
out.txt
```

**Note the specific line order in this genuinely observed output:** the error line appears first here, ahead of the normal result — a reminder that once combined, stdout and stderr are no longer guaranteed to preserve any particular relative ordering between the two original streams (a consequence of Section 12's buffering-related behavior, which this lesson does not explore further beyond noting the effect here).

---

## 12. Redirection Internals

**What conceptually happens when a shell launches a process with redirected streams:**

```text
Shell
  |
  | prepares file descriptors before starting the process
  |
  +-- FD 0 → input source           (a file, instead of the terminal)
  +-- FD 1 → output file             (a file, instead of the terminal)
  +-- FD 2 → terminal                 (left connected to the screen, in this example)
  |
  ↓
Process
```

**The single most important idea in this whole lesson, stated directly: the process can continue using stdin/stdout/stderr exactly as before, without needing to know that stdout is now connected to a file instead of the terminal.** Nothing in the process's own code changes — `print(...)` is still just "write to FD 1" — only *what FD 1 is connected to* has changed, and that substitution happened entirely before the process even started, arranged by the shell. This is a genuine, powerful abstraction: it is precisely *why* the exact same, unmodified program can run interactively, write to a log file, or feed another program (Section 13), with zero code changes required.

---

## 13. Standard I/O and Pipes

**This section introduces only the foundation needed to understand [Pipes](12-pipes.md), still ahead — it deliberately does not teach pipe mechanics in depth.**

A **pipe** is another possible destination or source for a standard stream — specifically, one connecting two processes directly to each other, rather than connecting a process to a file or a terminal.

```text
Process A
stdout
  ↓
 pipe
  ↓
stdin
Process B
```

**Why this is powerful:** because every process already reads from stdin and writes to stdout in exactly the same, standardized way (Section 3), *any* two programs can be connected this way — Process A never needs to know its output is going to another program instead of a file or a screen, and Process B never needs to know its input is coming from another program instead of a file or a keyboard. This is Section 12's abstraction, extended one step further: the *thing* on the other end of a stream can be a file, a terminal, or an entirely different running process.

A brief, illustrative shell pipeline (not a full teaching example — `12-pipes.md` covers this properly):

```bash
echo "hello world" | tr 'a-z' 'A-Z'
```

Here, `echo`'s stdout becomes `tr`'s stdin, directly, without either program needing any special support for this — a direct, minimal instance of the diagram above. **The complete mechanics of how pipes actually work — including their capacity, blocking behavior, and more — belong entirely to [Pipes](12-pipes.md).**

---

## 14. Standard I/O and Process Lifecycle

**Connecting to [Processes](03-processes.md) and previewing [Process Lifecycle](14-process-lifecycle.md), still ahead, without repeating either.**

- A process starts with standard streams already available, in the normal command-line environment — established for it before its own code ever runs (Section 12).
- Those streams can be inherited from, or explicitly configured by, the parent process that started it — a direct parallel to how Concept 09 described environment inheritance.
- When a process exits, its file descriptors (including its standard streams) are closed as part of the OS's ordinary cleanup (a preview of what Concept 14 will cover fully).

**A required, precise distinction:**

```text
stdout/stderr → data/messages the process produces WHILE running

exit code       → a single, separate status/result value produced only
                    WHEN the process terminates (Concept 03's exit-status concept)
```

**Why this distinction matters:** a process can write extensive output to stdout and stderr and still exit with a failure status, or write nothing at all and exit successfully — the content of its streams and its final exit code are two entirely independent pieces of information, both worth checking, neither implied by the other. Section 22's mini-project demonstrates this directly, with genuinely different exit codes (`0`, `1`, `2`) depending on what happened during a run, regardless of what was printed.

---

## 15. Standard I/O and Environment Variables

**Briefly connecting to [Environment Variables](09-environment-variables.md), without repeating that lesson.**

```text
Environment variable                          Signal
        ↓                                        ↓
configuration supplied at process startup     (covered in Section 16 below)
```

- **Environment variables** configure a process — they answer "how should this process behave?" (Concept 09).
- **Standard streams** communicate data and diagnostics *with* a process while it runs — they answer "what information is flowing in and out of this process, right now?"
- Both are established as part of a process's execution environment at startup, and both are inherited from a parent process in a broadly similar way (Concept 09's inheritance model applies conceptually here too) — **but they solve genuinely different problems**, and this lesson does not conflate them.

---

## 16. Standard I/O and Signals

**Briefly connecting to [Signals](10-signals.md), without repeating that lesson.**

- **Signals** are a control/notification mechanism — a short, standardized event delivered to a process (Concept 10).
- **Standard I/O** is a data/stream communication mechanism — an ongoing channel for actual content flowing in and out of a process.
- These are genuinely different mechanisms, and this lesson does not conflate them: a signal does not carry stream data, and writing to stdout/stderr does not notify or control a process the way a signal does.
- **Both interact with process behavior**, sometimes at the same moment — for example, a process might be in the middle of writing output when it receives `SIGTERM` (Concept 10), at which point its own registered signal-handling logic (not this lesson's concern) determines what happens to any output still in progress.

---

## 17. Linux / Ubuntu / WSL2 Practical Lab

All commands below are safe, read-only where possible, and use only a self-created, isolated temporary directory and processes created specifically for this lab. No `sudo` is required, no system files are touched, and no unrelated process is ever inspected or signaled.

### Inspecting the current shell's own file descriptors

```bash
ls -l /proc/self/fd
readlink /proc/self/fd/0
readlink /proc/self/fd/1
readlink /proc/self/fd/2
```

**Observed in this environment** (this specific automated shell session, not a typical human-interactive terminal — see Section 5's discussion):

```text
total 0
lr-x------ 1 sovon sovon 64 Sep 10 16:26 0 -> /dev/null
l-wx------ 1 sovon sovon 64 Sep 10 16:26 1 -> pipe:[22250]
l-wx------ 1 sovon sovon 64 Sep 10 16:26 2 -> pipe:[22250]
lr-x------ 1 sovon sovon 64 Sep 10 16:26 3 -> /proc/7058/fd
```

**What to look for:** entries `0`, `1`, and `2` are exactly this shell's stdin/stdout/stderr (Section 3); entry `3` shows that a process can have *additional* open file descriptors beyond the standard three (Section 4). **Your own output will almost certainly differ** — in a genuine interactive terminal, `0`, `1`, and `2` would typically all point to the same terminal device (something like `/dev/pts/N`), rather than `/dev/null` and a pipe as shown here — this automated environment's specific values reflect how it happens to be run, not a universal result.

### Redirection, demonstrated end to end

```bash
mkdir -p /tmp/stdio-lesson && cd /tmp/stdio-lesson

echo "first line" > out.txt
cat out.txt

echo "second line" >> out.txt
cat out.txt

cat < out.txt

ls out.txt missing.txt > listing.txt 2> errors.txt
cat listing.txt
cat errors.txt

ls out.txt missing.txt > combined.txt 2>&1
cat combined.txt
```

**Observed in this environment** (run from an equivalent isolated temporary directory):

```text
> out.txt:              first line
>> out.txt:              first line
                          second line
< out.txt:                first line
                            second line
listing.txt (stdout):        out.txt
errors.txt (stderr):          ls: cannot access 'missing.txt': No such file or directory
combined.txt (2>&1):            ls: cannot access 'missing.txt': No such file or directory
                                  out.txt
```

Every result above is exactly as Section 11 already explained in detail — this is the same genuine demonstration, presented here as a single reproducible practical sequence.

### Inspecting a disposable, learner-created process's file descriptors

**Safety rule, honored here exactly as in Concept 10: create the process yourself, capture its PID, verify it, then inspect or signal only that PID.**

```bash
cat > longrun.py << 'EOF'
import time
while True:
    time.sleep(1)
EOF

python3 longrun.py &
PID=$!
echo "Created PID: $PID"
ls -l /proc/$PID/fd
readlink /proc/$PID/fd/0
readlink /proc/$PID/fd/1
readlink /proc/$PID/fd/2

kill -TERM "$PID"
ps -p "$PID"
```

**Observed in this environment:**

```text
Created PID: 7108
total 0
lrwx------+1 sovon sovon 64 Sep 10 16:27 0 -> socket:[28785]
l-wx------ 1 sovon sovon 64 Sep 10 16:27 1 -> /tmp/.../tasks/bqunby6nw.output
l-wx------ 1 sovon sovon 64 Sep 10 16:27 2 -> /tmp/.../tasks/bqunby6nw.output

(after kill -TERM, ps -p reported no matching process — confirming clean termination)
```

**What to look for:** the same `PID` used consistently to identify this one specific process (Concept 03); FD `1` and FD `2` here happen to point at the *same* underlying file — this automated environment's own way of capturing this background process's combined output, conceptually similar to a `2>&1` redirection (Section 11), even though nothing in this lesson's own commands explicitly requested that. **In a typical interactive terminal, you would instead see all three descriptors pointing at your terminal device**, unless you had redirected them yourself.

### Reading from stdin and separating stdout/stderr in Python

```bash
cat > greet.py << 'EOF'
name = input("Name: ")
print(f"Hello, {name}")
EOF
echo "Ada" | python3 greet.py

cat > streams_demo.py << 'EOF'
import sys
print("normal result", file=sys.stdout)
print("diagnostic message", file=sys.stderr)
EOF
python3 streams_demo.py > stdout_only.txt 2> stderr_only.txt
cat stdout_only.txt
cat stderr_only.txt
```

**Observed in this environment** (already shown in full in Sections 9 and 10):

```text
Name: Hello, Ada

stdout_only.txt: normal result
stderr_only.txt: diagnostic message
```

### Cleanup

```bash
cd /
rm -rf /tmp/stdio-lesson
```

**Observed in this environment:** the equivalent isolated directory used for this lab was fully removed, and its removal was verified (`ls -d <directory>` reporting "No such file or directory") — no temporary file, script, or disposable process from this lab was left behind.

### WSL2 considerations

- **WSL2 provides a genuine Linux environment on Windows** (Concept 01) — every command in this section ran inside that Linux environment, using Linux's file-descriptor and standard-stream model exactly as described throughout this lesson.
- **Windows processes and WSL2/Linux processes are separate** — a Windows program's own standard streams are not automatically the same channels as a WSL2 Linux process's streams, exactly as Concept 09 already explained for environment variables and Concept 10 for signals.
- **Some observations may differ from a native, bare-metal Linux installation** — this lesson's own genuinely observed examples (an automated shell with `/dev/null` as stdin, rather than a real terminal) illustrate this directly: what you observe depends on *how* a process was started, not only on the fact that it's running inside WSL2.
- **Treat WSL2 as a genuine, practical Linux learning environment**, while remembering it is a virtualized Linux environment running on a Windows host, not an unmediated view of that host's own I/O behavior.

---

## 18. PowerShell Comparison

Because the roadmap explicitly includes PowerShell, a brief conceptual comparison:

- PowerShell has its **own pipeline and object-passing model**, distinct from Bash/Unix's plain, text-oriented file-descriptor model — PowerShell pipelines commonly pass structured *objects* between commands, not just streams of raw text.
- **PowerShell should not be assumed to have identical file-descriptor semantics to Unix/Bash.** The numbered-file-descriptor model (`0`/`1`/`2`, Section 3) is specifically a Unix/Linux convention; PowerShell's own stream model (its numbered "streams" — success, error, warning, and more) is conceptually related but implemented differently, and this lesson does not teach it in depth.
- **This lesson remains Linux/Unix-oriented deliberately**, because Module 0.2 is specifically teaching OS fundamentals and file descriptors as they exist on the Linux systems this roadmap's practical work is built around (Ubuntu, WSL2). PowerShell's own I/O model is a separate, later topic to explore on its own terms, not a drop-in equivalent to master here.

---

## 19. AI Engineering Relevance

Standard I/O is not an abstract OS detail for an Applied AI Engineer — it's the everyday shape of how real AI tooling actually runs:

```text
Dataset/script
     ↓ stdin
Python processing job
     ↓ stdout
Results
```

```text
AI service
     ↓ stdout/stderr
logs / diagnostics
```

**Concrete categories where this lesson applies directly:**

- **Python AI scripts and CLI tools** — reading input, producing results, exactly as Section 9's example demonstrated.
- **Model inference scripts and evaluation jobs** — often read input data via stdin or files, and write results to stdout, while separately reporting progress or warnings to stderr.
- **Batch jobs and data-processing workers** — Section 22's mini-project is a direct, minimal example of this exact pattern.
- **Backend workers and model-serving processes** — their operational logs (Section 6) depend entirely on the stdout/stderr separation this lesson teaches.
- **Subprocess-based tooling and automation pipelines** — one tool's stdout commonly becomes another's stdin (Section 13), the same foundational idea behind chaining data-processing steps together.

**Why separating stdout and stderr specifically becomes valuable in production automation and observability:** an automated pipeline that captures a script's stdout as its actual *result* (to feed into the next step) needs that stream to be free of unrelated diagnostic noise — exactly what Section 11's `ls out.txt missing.txt` demonstration showed concretely. A logging or monitoring system, separately, wants to collect *just* the diagnostic stream (stderr) without it being mixed into actual data output.

**This lesson deliberately does not teach Docker, Kubernetes, or LLMOps internals** — those later systems (containers routing a process's stdout/stderr to their own logging systems, for example) are all built directly on top of exactly this OS-level standard-stream model. Understanding this lesson is the prerequisite for later understanding *how* those systems capture and route output at all.

---

## 20. Debugging Standard I/O Problems

For every scenario: symptom, likely cause, how to inspect, a safe diagnostic step, the reasoning process, and the likely fix.

**1. "My program is waiting for input."**
*Symptom:* the program appears to hang with no output. *Likely cause:* it called `input()` (or read from stdin) and stdin has no data ready — it's genuinely waiting, not broken. *Inspect:* check whether the program's code actually calls `input()`/reads stdin, and whether you launched it in a way that provides input (interactively, or piped/redirected). *Safe diagnostic:* try running it with input explicitly piped in (`echo "value" | python3 script.py`), as Section 9 did. *Reasoning:* a process reading from stdin with nothing available simply waits — this is expected stdin behavior (Section 3), not a hang or crash. *Fix:* supply input, or confirm the program is genuinely meant to run interactively.

**2. "My program printed nothing."**
*Symptom:* no visible output at all. *Likely cause:* output may have been written to a stream you're not currently looking at (for example, stderr, when you're only watching stdout — Section 6), or it may have been redirected somewhere unexpected (Section 11). *Inspect:* check whether the command included any redirection, and check both stdout and stderr separately. *Safe diagnostic:* rerun without redirection, or redirect both streams to separate, visible files and inspect each. *Reasoning:* "printed nothing" and "printed somewhere I'm not looking" are different problems with the same visible symptom. *Fix:* look at the correct stream, or remove unintended redirection.

**3. "My output went into a file instead of the terminal."**
*Symptom:* expected output on screen; found it in a file instead. *Likely cause:* an active `>` or `>>` redirection (Section 11) is silently sending stdout to that file. *Inspect:* re-examine the exact command that was run, looking specifically for `>` or `>>`. *Safe diagnostic:* run the same command without the redirection and confirm output now appears on screen. *Reasoning:* Section 12's abstraction means the program itself gave no indication anything was different — the redirection is entirely a property of how the command was launched, not the program's own behavior. *Fix:* remove the unintended redirection.

**4. "My error message is missing from the expected output file."**
*Symptom:* a file that should contain error output doesn't. *Likely cause:* only stdout was redirected (`>`), while the error was written to stderr, which went elsewhere (often the terminal, by default) — Section 6's separation, working exactly as designed. *Inspect:* check whether the command used `2>` (or `2>&1`) at all. *Safe diagnostic:* rerun with `2>` explicitly targeting a file, and check that file. *Reasoning:* stdout and stderr are independent destinations (Section 11) — redirecting one says nothing about the other. *Fix:* add explicit stderr redirection if you want it captured too.

**5. "I redirected stdout but still see an error."**
*Symptom:* `> file.txt` was used, yet an error message still appeared on screen. *Likely cause:* this is expected — the error was written to stderr, which was never redirected, and by default still goes to the terminal (Section 6, Section 11). *Inspect:* confirm the message is indeed an error/diagnostic message, not part of the program's normal results. *Safe diagnostic:* add `2>&1` or a separate `2>` and observe the difference. *Reasoning:* seeing *something* on screen after redirecting stdout is not a contradiction — it's stderr behaving exactly as it should, independently. *Fix:* redirect stderr too, if you want it suppressed or captured as well.

**6. "I accidentally overwrote a file using `>`."**
*Symptom:* a previously existing file's contents are gone. *Likely cause:* `>` **overwrites** its target file by default (Section 11) — `>>` is required to append instead. *Inspect:* check whether the intended operation actually needed `>>` rather than `>`. *Safe diagnostic:* going forward, use disposable filenames in an isolated temporary directory (Section 17) when experimenting, exactly as this lesson's own lab did. *Reasoning:* this is expected `>` behavior, not a bug — the fix is prevention, not recovery, since `>` provides no built-in undo. *Fix:* use `>>` for appending, and always double-check the target filename before redirecting into an existing, important file.

**7. "I expected stderr to behave like stdout."**
*Symptom:* confusion about why redirecting one stream didn't affect the other. *Likely cause:* treating stdout and stderr as a single stream, when they are genuinely independent (Section 6). *Inspect:* re-read the exact command for separate `>` and `2>` (or their absence). *Safe diagnostic:* deliberately redirect each stream to a different file (Section 11's `ls out.txt missing.txt` example) and observe that each file contains only what you'd expect from that specific stream. *Reasoning:* this misconception, once corrected with a concrete example, tends not to recur. *Fix:* always reason about stdout and stderr as two separate channels, never as one.

**8. "A program works interactively but behaves differently when redirected."**
*Symptom:* identical code, different behavior depending on how it's launched. *Likely cause:* many programs (and libraries) deliberately behave differently depending on whether their output is connected to a real terminal or not — for example, adjusting buffering behavior, or disabling interactive prompts/color output when not attached to a terminal. *Inspect:* check whether the specific program or library documents "TTY-aware" behavior. *Safe diagnostic:* compare running the exact same command with and without redirection, side by side. *Reasoning:* this isn't a bug in your redirection — many tools intentionally check "am I connected to a real terminal?" and adapt. *Fix:* consult the specific tool's documentation for any flags controlling this behavior; this lesson does not teach the detailed mechanics behind such checks (out of scope, Section 28).

**9. "A Python process receives EOF instead of interactive input."**
*Symptom:* `input()` raises an `EOFError` instead of returning a value. *Likely cause:* stdin was redirected from a source that ran out of data (for example, a file or pipe with no more lines left) rather than being connected to an interactive session that can keep waiting. *Inspect:* check whether stdin was redirected from a file or pipe (Section 11), and whether that source actually had enough lines for every expected `input()` call. *Safe diagnostic:* count how many `input()` calls the program makes versus how many lines the redirected source actually provides. *Reasoning:* `EOFError` is Python's precise, correct way of saying "I was asked to read a line, but the input source has genuinely ended" — not a random crash. *Fix:* supply enough input, or design the program to handle `EOFError` gracefully when reading a possibly-finite input source.

**10. "A subprocess behaves differently because its stdin/stdout/stderr were redirected."**
*Symptom:* launching a program as a subprocess from another program produces different behavior than running it directly in a terminal. *Likely cause:* exactly Scenario 8's pattern, now from the *parent* program's point of view — many subprocess-launching APIs redirect the child's standard streams (to capture output, for example), and the child, seeing it's not connected to a real terminal, may behave differently as a result. *Inspect:* check how the subprocess was actually launched, and whether its stdin/stdout/stderr were explicitly redirected/captured. *Safe diagnostic:* compare the subprocess's behavior when launched with its streams left connected to the parent's own terminal, versus explicitly captured. *Reasoning:* Section 12's abstraction cuts both ways — the child process can't tell the difference between talking to a terminal and talking to its parent through redirected streams, but its own *behavior* (not its correctness) can still depend on which one is actually true. *Fix:* be deliberate about which streams a subprocess needs redirected, and check the target program's own terminal-detection behavior if results seem unexpected.

---

## 21. Common Misconceptions

| Misconception | Why it's wrong |
|---|---|
| "stdin always means keyboard." | stdin is whatever this process's input channel is currently connected to — a keyboard, a file, or another program's output (Section 5, Section 11) — never guaranteed to be a keyboard. |
| "stdout always means screen." | stdout is whatever this process's output channel is currently connected to — the screen by default in an interactive terminal, but just as easily a file or another program's input (Section 5, Section 11). |
| "stderr means exceptions." | stderr is a destination for *diagnostic* messages generally — warnings, progress information, and errors alike — not exclusively a channel for exceptions (Section 6). |
| "File descriptor means disk file." | A file descriptor can refer to a terminal, a pipe, a socket, or a regular file — "file" in the name reflects a uniform handle model, not a guarantee of an actual disk file (Section 4). |
| "FD 0/1/2 are arbitrary numbers." | They are a deliberate, universal convention every process receives, precisely so no program ever has to guess which number means which stream (Section 3). |
| "stdout and stderr are the same stream." | They are two independent file descriptors (`1` and `2`) that happen to both default to the terminal in an interactive session — genuinely separate, as Section 11's `ls out.txt missing.txt` demonstration showed directly. |
| "Redirecting stdout also redirects stderr automatically." | Each stream must be redirected independently unless you explicitly combine them with something like `2>&1` (Section 11, Debugging Scenario 5). |
| "Python's `print()` directly talks to the terminal." | `print()` writes to `sys.stdout` (FD 1), whatever that currently happens to be connected to (Section 8) — it has no inherent, direct relationship to a terminal specifically. |
| "A process always owns the terminal directly." | A process is simply given file descriptors that may or may not currently point at a terminal (Section 4, Section 5) — many processes (background services, redirected scripts) never have a terminal connected to their streams at all. |
| "Exit code is the same thing as stderr." | These are two entirely independent pieces of information about a finished process — one is a single numeric status, the other is a stream of diagnostic content produced while it ran (Section 14). |
| "Pipes are unrelated to standard I/O." | A pipe is simply another possible destination/source for stdout/stdin (Section 13) — pipes are built directly on the same standard-stream model this lesson teaches, not a separate, unrelated mechanism. |
| "Standard I/O is only useful for CLI programs." | Every long-running service, background worker, and model-serving process (Section 19) depends on exactly this same standard-stream model for its logs and diagnostics, not only interactive command-line tools. |

---

## 22. Mini-Project

**Requirements.** Build a small, complete Python command-line program that reads numeric values from stdin (one per line), computes their count, sum, and average, reports normal results on stdout, reports a warning to stderr for any line that isn't a valid number, and exits with a status code reflecting exactly what happened: `0` for full success, `1` if no valid numbers were found at all, `2` if it succeeded but had to skip at least one invalid line.

**Design.** This mirrors a genuinely realistic data-processing pattern:

```text
input
  ↓
Python process
  ↓
normal results → stdout
diagnostics    → stderr
  ↓
exit status reflecting overall outcome
```

**Implementation:**

```python
import sys

def main():
    total = 0.0
    count = 0
    had_error = False

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            value = float(line)
        except ValueError:
            print(f"warning: skipping invalid line: {line!r}", file=sys.stderr)
            had_error = True
            continue
        total += value
        count += 1

    if count == 0:
        print("error: no valid numbers were provided", file=sys.stderr)
        sys.exit(1)

    print(f"count={count}")
    print(f"sum={total}")
    print(f"average={total / count}")

    sys.exit(2 if had_error else 0)

if __name__ == "__main__":
    main()
```

**How to run it** (piping input in, exactly as Section 9 demonstrated):

```bash
printf "3\n4\n5\n" | python3 process_numbers.py
```

**Observed in this environment (Test 1 — all valid input):**

```text
count=3
sum=12.0
average=4.0
exit code: 0
```

**How to test it with mixed input, redirecting each stream separately:**

```bash
printf "3\nabc\n5\n" | python3 process_numbers.py > results.txt 2> warnings.txt
```

**Observed in this environment (Test 2 — mixed valid/invalid input):**

```text
exit code: 2
results.txt (stdout):   count=2
                          sum=8.0
                          average=4.0
warnings.txt (stderr):    warning: skipping invalid line: 'abc'
```

**How to test the all-invalid case:**

```bash
printf "abc\nxyz\n" | python3 process_numbers.py
```

**Observed in this environment (Test 3 — no valid numbers at all):**

```text
warning: skipping invalid line: 'abc'
warning: skipping invalid line: 'xyz'
error: no valid numbers were provided
exit code: 1
```

**How to inspect its behavior further:** run it with `2>&1` to see both streams interleaved in one place, or run `echo $?` immediately after each invocation (Concept 03) to confirm the exit code directly, exactly as these genuinely observed tests did.

**Common failures:** forgetting that `float("abc")` raises `ValueError` (handled here explicitly); forgetting to strip trailing newlines from each `sys.stdin` line before conversion; assuming stdout and stderr will appear in a specific relative order when *not* redirected separately (Section 11's combined-redirection example showed this ordering is not guaranteed).

**Debugging approach if something goes wrong:** apply Section 20's method directly — check which stream (stdout or stderr) actually received the output you're looking for, confirm the exact exit code with `echo $?`, and re-run with each stream redirected to its own file to inspect them independently.

**Production relevance.** This exact pattern — read data, produce results on stdout, report problems on stderr, and signal overall success/partial-success/failure through a meaningful exit code — is precisely how a well-behaved batch job, data-validation script, or CLI tool in a real AI pipeline should be built, so that both human operators and automated systems (checking the exit code, capturing stdout as data, and separately watching stderr for problems) can rely on its behavior predictably.

---

## 23. Exercises

Work through these in your own words. No answer key exists for this lesson — the goal is reasoning ability, not matching a memorized phrase.

### Level 1 — Recognition

1. What is stdin? What is stdout? What is stderr?
2. What file descriptor number corresponds to each of stdin, stdout, and stderr?
3. What is a file descriptor, in your own words?
4. Name three kinds of underlying objects a file descriptor can refer to, besides a regular disk file.
5. What does `>` do? What does `>>` do?
6. What does `2>` redirect?
7. What is a terminal, in the context of this lesson?
8. What does `2>&1` do?

### Level 2 — Understanding

9. Explain why standard streams exist as a standardized, universal mechanism rather than something each program invents for itself.
10. Explain why stdout and stderr are kept as separate streams rather than one combined stream.
11. Explain how file descriptors relate to a process, using Section 4's table.
12. Explain, step by step, what happens when a shell redirects a process's stdout to a file.
13. Explain why stdout does not inherently mean "screen."
14. Explain why stdin does not inherently mean "keyboard."
15. Explain why pipes can connect one process's stdout to another's stdin without either program needing special support.
16. Explain the difference between a process's output and its exit code.

### Level 3 — Application

17. In your own WSL2 terminal, run `ls -l /proc/self/fd` and `readlink /proc/self/fd/0`, `/1`, and `/2`. Record what each descriptor points to.
18. Redirect the output of a simple command to a file using `>`, then confirm the file's contents with `cat`.
19. Append additional output to the same file using `>>`, and confirm both lines are present.
20. Redirect a command's stdin from a file using `<`.
21. Run a command that produces both normal output and an error (like `ls existingfile nonexistentfile`), redirecting stdout and stderr to two separate files, and inspect each independently.
22. Write a small Python script using `print(..., file=sys.stderr)` to write a diagnostic message, and confirm it lands in a separate file from your normal `print()` output when redirected.
23. Start a small, disposable long-running Python process, capture its PID, and inspect its file descriptors using `/proc/<PID>/fd`.
24. Pipe a value into a Python script that reads it with `input()`, and confirm the expected output.

### Level 4 — Debugging

25. A script appears to hang with no output. Using Debugging Scenario 1 (Section 20), explain your investigation approach.
26. A script produces no visible output at all. Using Scenario 2, explain what you'd check before assuming it produced nothing.
27. Expected terminal output instead appeared inside a file. Using Scenario 3, explain the likely cause.
28. An expected error message is missing from a redirected output file. Using Scenario 4, explain why, and how to fix it.
29. You redirected stdout, but an error still appeared on screen. Using Scenario 5, explain why this is expected, not a bug.
30. You accidentally overwrote an existing file with `>`. Using Scenario 6, explain how this happened and how to prevent it in the future.
31. A Python script raises `EOFError` on an `input()` call when its stdin was redirected from a file. Using Scenario 9, explain the root cause.
32. A subprocess launched from another Python program behaves differently than when run directly in a terminal. Using Scenario 10, explain a plausible reason.

### Level 5 — Integration

33. Design (in your own words, not just code) a small AI-engineering CLI tool that reads a list of file paths from stdin, attempts to check each one's existence, prints successfully found paths to stdout, and prints missing-path warnings to stderr — explain your reasoning for which stream carries which information.
34. A friend claims, "Since my script prints something, it must have succeeded." Using Section 14 and this lesson's mini-project, explain why exit codes and printed output are separate pieces of information, with a concrete counter-example.
35. Explain how Section 12's redirection abstraction and Concept 09's environment-variable inheritance are similar in spirit, even though they configure completely different aspects of a process.
36. A production batch job's output is being automatically captured by a monitoring pipeline that treats *all* of the job's combined terminal output as "results data." Using Section 6, Section 11, and Section 19, explain what could go wrong with this design, and how it should be fixed.
37. Using everything in this lesson, explain to a beginner (in your own words, as if teaching them) why "my program prints correctly when I run it myself" is not the same guarantee as "my program will behave correctly when its input and output are redirected or piped by something else" — and why that gap matters for real AI-engineering tooling.

---

## 24. Review

- What is stdin? What is stdout? What is stderr?
- Why are they separate streams rather than one combined channel?
- What is a file descriptor?
- Why are `0`, `1`, and `2` special, rather than arbitrary?
- What does file descriptor `1` actually point to, and can that change?
- Why can stdout point to a file instead of a terminal, with no code changes required?
- What actually happens during shell redirection, at the level Section 12 described?
- How does Python interact with standard streams, both through convenience functions and direct stream objects?
- How are standard streams related to pipes (Section 13)?
- How are standard streams different from a process's exit code (Section 14)?
- How do standard streams show up in a real, running AI service (Section 19)?

---

## 25. Interview / Architecture Questions

- Explain stdin, stdout, and stderr, and how they relate to file descriptors `0`, `1`, and `2`.
- What is a file descriptor, precisely, and why can it refer to more than a disk file?
- Why are `0`, `1`, and `2` conventional across virtually every Unix-like process?
- What actually happens, step by step, when a shell redirects a process's stdout to a file?
- Why is it useful, architecturally, to keep stderr separate from stdout?
- How can one process's output become another process's input? How does this relate to Unix pipelines?
- What happens to a child process's standard streams when it's launched by a parent process?
- Why does this distinction matter for a backend worker or a batch-processing job?
- Why does this distinction matter for an AI batch job or evaluation script specifically?
- How would you diagnose a subprocess that appears to hang waiting for input?
- How would you capture a child process's stdout and stderr separately, and why might you want to?

**For architecture-style questions, reason about trade-offs, not memorized terminology:** for example, when designing a CLI tool, *why* would you choose to put results on stdout and diagnostics on stderr, rather than combining them — what does that choice make easier or harder for whoever consumes this tool's output later?

---

## 26. Production Application

Standard I/O shows up directly in real production engineering:

- **CLI automation and batch processing.** Section 22's mini-project pattern — results on stdout, diagnostics on stderr, meaningful exit codes — is exactly the shape a production-quality batch tool should take.
- **Worker processes and subprocess execution.** A parent process launching workers or subprocesses commonly needs to capture their stdout/stderr separately (Debugging Scenario 10) to reason correctly about what each did.
- **AI evaluation jobs and model inference scripts.** Their actual results (predictions, scores) belong on stdout; their progress and warnings belong on stderr — mixing the two makes automated consumption of results unreliable.
- **Service diagnostics and log collection.** A production service's stdout/stderr output is very commonly what an operational logging system actually collects — understanding this OS-level foundation is the prerequisite for understanding how any such logging system works at all.
- **Automation pipelines.** Chains of tools connected via pipes (Section 13) depend entirely on each tool correctly separating real output from diagnostic noise.
- **Container processes, as a future connection.** Containerized applications' stdout/stderr are commonly what a container runtime captures as "the container's logs" — **this lesson does not teach container logging in depth** (Section 28), but everything such a system does rests directly on this lesson's foundation.

**Practical production concerns worth naming, without teaching them in full depth here:**

- **Buffering, at a high level.** Output isn't always written to its destination the instant `print()` is called — it can be buffered (held briefly) before actually being flushed out, which can affect how promptly output appears, especially when redirected to a file rather than an interactive terminal (Debugging Scenario 8 touches this indirectly). This lesson does not teach buffering internals in depth.
- **Output volume.** A process that writes an enormous amount of diagnostic output to stderr can itself become an operational problem, independent of whether its actual logic is correct.
- **Accidental sensitive-data logging.** Writing a secret or credential to stdout/stderr (an application-level mistake, exactly as Concept 09 warned for environment variables) is a genuine, recurring production risk, not a theoretical one.
- **Diagnosing hung processes.** Section 20's Scenario 1 — a process waiting on stdin — is one of the most common real "why is this process stuck" investigations an operator performs.
- **Operational observability.** Consistently separating results from diagnostics, at the OS level this lesson teaches, is the foundation every higher-level observability and logging system is eventually built on top of.

**This lesson deliberately does not teach advanced logging frameworks** — the objective here is the OS-level foundation those frameworks are built on, not the frameworks themselves.

---

## 27. Relationship to Module 0.2

```text
Kernel
  ↓
System Calls
  ↓
Processes
  ↓
File Descriptors
  ↓
Standard I/O                  ← this lesson
  ↓
Pipes
  ↓
Shell
  ↓
Process Lifecycle
```

**Also connected to:**

- **Permissions** — accessing a file a stream is redirected to is still subject to the permission rules Concept 08 already established.
- **Environment Variables** — a related but distinct process-startup mechanism (Section 15).
- **Signals** — a related but distinct process-communication mechanism (Section 16).
- **Filesystems** — regular files are one of several things a file descriptor can point to (Section 4).
- **Virtual Memory** — independent of standard I/O directly, though buffered output (Section 26) briefly occupies a process's own memory before being written out.

### Previously learned

Kernel/user space, system calls, processes, threads, scheduling, virtual memory, filesystems, permissions, environment variables, signals.

### Current lesson

Standard input, standard output, standard error, file descriptors in the context of standard streams, and basic redirection.

### Next lesson

[Pipes](12-pipes.md) — the full mechanics of connecting one process's stdout to another's stdin, introduced here only as a foundation (Section 13).

### Later

[Shell](13-shell.md), [Process Lifecycle](14-process-lifecycle.md).

---

## 28. Scope Boundaries

This lesson is foundational. It deliberately does **not** teach, in depth:

- Advanced asynchronous I/O, `select`, `poll`, `epoll`, `io_uring`
- Terminal driver internals, TTY/PTY internals
- Advanced buffering internals
- Kernel VFS internals
- Advanced file-descriptor flags, or `dup`/`dup2`/`dup3` internals
- Advanced subprocess internals
- Advanced IPC, sockets as a full topic, Unix domain sockets
- Advanced shell implementation
- Advanced Windows I/O internals

Each of these may be mentioned by name where relevant (Section 4, Section 7, Section 18), but every one belongs to later, more advanced curriculum — the objective here was a strong, correct conceptual and practical foundation, not exhaustive OS internals.

---

## 29. Final Mental Model

```text
Process
  |
  +-- FD 0 → stdin      (wherever input currently comes from — keyboard, file, or pipe)
  +-- FD 1 → stdout     (wherever normal results currently go — screen, file, or pipe)
  +-- FD 2 → stderr     (wherever diagnostics currently go — usually the screen, or a file)
```

**Hold onto this one idea above all others from this lesson:** a process always has exactly these three standard streams, always numbered the same way — but *what each one is actually connected to* can change freely, without the process's own code ever needing to know or care. That single fact is what makes redirection (Section 11–12), pipes (Section 13), and reliable production logging (Section 26) all possible, using the exact same, unmodified program every time.

---

_This file is the completed lesson for Concept 11 of Module 0.2. It intentionally does not teach advanced asynchronous I/O, terminal/TTY/PTY internals, buffering internals, kernel VFS internals, advanced descriptor-flag or `dup`-family internals, advanced subprocess internals, sockets as a full topic, advanced shell implementation, or advanced Windows I/O internals in depth — those remain the subject of later, more advanced curriculum, not this beginner-level foundation._
