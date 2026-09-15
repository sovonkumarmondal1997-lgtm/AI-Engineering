# Module 0.3 — Command Line

## Lesson 8 — Shell Scripts

**Module:** Command Line
**Roadmap reference:** Stage 0 — Module 0.3 — Command Line
**Concept(s) covered:** shell scripts, shebang, script execution, arguments, variables, quoting, exit status, conditionals, loops, functions
**Status:** Complete
**Builds on:** 01–07 (navigation, file operations, viewing, searching, text processing, pipes/redirection, environment variables) and Module 0.2 (processes, shell, standard I/O, exit codes)

---

## 1. Lesson Overview

**Purpose:** every previous Module 0.3 lesson taught you commands you type one at a time. This lesson teaches you how to save a **sequence** of those commands into a file, so it can be run again and again — reliably, repeatably, and without retyping anything. This is the natural bridge from "I know how to use the command line" to "I can automate the command line."

**Prerequisites:** this lesson assumes you've completed Lessons 01–07 — navigation, file operations, viewing files, searching, text processing, pipes/redirection, and environment variables — and that you're comfortable running the commands those lessons taught (`cd`, `ls`, `cp`, `grep`, `sort`, `|`, `>`, `export`, and so on). This lesson does **not** re-teach any of them in depth; it uses them as ingredients.

**Learning objectives.** By the end of this lesson you will be able to:

- Explain what a shell script is and why it exists.
- Explain what a shebang is, and why `#!/usr/bin/env bash` is a common, portable choice.
- Create a shell script file and run it two different ways (`bash script.sh` and `./script.sh`), and explain why those two ways differ.
- Explain, at a foundational level, why `./script.sh` depends on an executable permission, without needing the full permissions lesson yet.
- Use script arguments (`$0`, `$1`, `$#`, `$@`) correctly and safely.
- Use variables in a script, and distinguish a plain shell variable from an exported environment variable.
- Quote variables correctly, and explain what breaks when you don't.
- Read and reason about exit status (`$?`), including in automated contexts.
- Write a basic `if`/`then`/`else`/`fi` conditional.
- Write a basic `for` loop and a basic `while` loop.
- Write and use a basic shell function.
- Combine pipes, redirection, and environment variables (from Lessons 06–07) inside a script.
- Diagnose common shell-script failures methodically, rather than by guessing.
- Explain when a shell script is the right tool, and when it isn't.
- Explain how this foundational skill connects to Applied AI Engineering automation later in this roadmap.

**What you should be able to *do* after this lesson:** write a small, safe, correct shell script from scratch; predict what it will do before running it; run it two different ways and explain the difference; and, when it doesn't work, diagnose *why* using a systematic process rather than trial and error.

---

## 2. What Is a Shell Script?

Recall the vocabulary from earlier lessons: a **shell** is the program that reads what you type and runs it (Module 0.2, Lesson 01); a **command** is one instruction you give it. An **interpreter** is a program that reads instructions written as text and carries them out directly, one at a time — Bash is both your interactive shell *and*, when pointed at a file, an interpreter for that file's contents.

A **shell script** is a plain text file containing a sequence of shell commands — the exact same kinds of commands you've been typing all module — saved so they can be run together, as a unit, instead of retyped one at a time. The file itself is often called a **script file**; once you've arranged for it to be run directly (Section 6), it's sometimes called an **executable script**.

**Automation**, in this context, simply means: doing something by running a saved procedure, rather than by manually repeating the same steps yourself each time.

### The mental model

```text
Manual workflow:

command 1
command 2
command 3
command 4
```

Each time you want this sequence to happen, you type all four commands again, by hand, in order — and you can make a different typo, or forget a step, every single time.

```text
Shell script:

script
  ↓
command 1
command 2
command 3
command 4
```

Now the four commands live inside one file. Running the script runs all four, in the same order, every time — identically.

**Why this matters to a software engineer:** the value isn't "typing less" — it's **consistency**. A procedure that lives in a file can be reviewed, corrected once, shared with someone else, and trusted to behave the same way on the tenth run as it did on the first. A procedure that lives only in your memory and your fingers cannot make any of those guarantees.

---

## 3. Why Shell Scripts Exist

**The engineering problems shell scripts solve:**

- **Repetitive command execution** — the same five commands, run every morning, every deploy, every test cycle.
- **Manual error** — a step skipped, a flag forgotten, a typo, all more likely the more times a human retypes something.
- **Inconsistent procedures** — two people (or the same person, on two different days) doing "the same" manual task slightly differently.
- **Repeated environment setup** — preparing a workspace the same way each time (Lesson 02's `mkdir` patterns, repeated).
- **File preparation** — organizing, renaming, or arranging files as a repeatable first step before real work begins.
- **Project initialization** — scaffolding a new project's directory structure the same way every time.
- **Data preparation** — a consistent sequence of filtering/sorting/extracting steps (Lesson 05) applied to new data each time it arrives.
- **Development workflows** — running the same handful of setup commands every time you sit down to work.
- **Operational tasks** — routine checks or cleanups that need to happen the same way, reliably.
- **Deployment preparation** — assembling files into the right shape before a deployment step (this lesson does not teach deployment itself — see Section 20's scope note).
- **Local automation** — anything on your own machine that benefits from "run this one thing" instead of "remember and retype these eight things."

### Automation vs. complex software

**Automation**, as taught in this lesson, means capturing a **known, well-understood sequence of command-line steps** so it can be repeated reliably.

**Complex software** means building something with genuine logic — data structures, error handling for many distinct failure modes, business rules, user interfaces, and so on.

**The important, explicit boundary this lesson draws:** shell scripts are an excellent tool for the first category, and a poor tool for the second. A script that runs four commands in order, checks one condition, and reports success or failure is a great use of shell scripting. A program that needs to model complex data, handle dozens of distinct error conditions gracefully, or maintain significant internal state is not — that's a job for a real programming language, a topic this roadmap reaches later. Section 20 returns to this distinction in more detail.

---

## 4. Shell Script Anatomy

A shell script file is just a plain text file. Its structure, piece by piece:

| Part | What it is |
|---|---|
| **First line (shebang)** | Tells the system which interpreter should run this file |
| **Comments** | Lines starting with `#`, ignored by the interpreter, meant for humans reading the file |
| **Commands** | The actual shell commands — the same ones from every earlier lesson |
| **Blank lines** | Ignored; used only to improve readability |
| **Execution** | Running the file causes its commands to be interpreted and run in order |
| **Exit status** | When the script finishes, it reports a success/failure signal (Section 10) |

### The shebang

```bash
#!/usr/bin/env bash
```

**What it is:** the very first line of a script file, starting with `#!` (pronounced "shebang"), followed by the path to the interpreter that should run the rest of the file.

**What it means, precisely:** it tells whatever launches this file directly (Section 6's `./script.sh` form specifically) *which program* should read and interpret the rest of the file's contents — in this case, `env` is used to locate `bash` wherever it happens to be installed on this particular system, which is why `#!/usr/bin/env bash` is a common, portable choice, rather than hard-coding a specific path like `#!/bin/bash` (which assumes Bash lives at that exact location).

**A precise correction, stated directly:** the shebang is **not** a Bash command, and Bash does not execute it as one. It's a special, two-character signal (`#!`) that the operating system's own program-loading mechanism recognizes *before* any interpreter is even involved — it's how the system knows *which* interpreter to hand the rest of the file to in the first place. (This lesson does not go deeper into how the operating system recognizes this signal — that belongs to a more advanced systems discussion, out of scope here.)

### Comments

```bash
# This script prints a greeting.
```

Anything after a `#` on a line is ignored by Bash — comments exist purely to explain *why* something is done, for the next human who reads the file (which is often your own future self).

### A minimal example, explained line by line

```bash
#!/usr/bin/env bash

echo "Hello from a shell script"
```

- **Line 1** (`#!/usr/bin/env bash`) — the shebang; tells the system to interpret this file using Bash.
- **Line 2** — a blank line, purely for readability; it has no effect.
- **Line 3** (`echo "Hello from a shell script"`) — an ordinary command, exactly like ones you've typed directly at a shell prompt all module; it prints the given text.

---

## 5. Creating a Basic Shell Script

The basic workflow: create a file → write commands → save it → inspect it → execute it → observe the result → inspect the exit status.

**This lesson does not create any files for you.** Every command below is something you would type yourself, in your own disposable practice area (Section 23 sets one up explicitly).

**Creating the file** — one simple way, using a technique called a **heredoc** (only explained to the minimum depth needed here — this is not a heredoc lesson):

```bash
cat > hello.sh <<'EOF'
#!/usr/bin/env bash

echo "Hello from a shell script"
EOF
```

What this does: `cat` is told (via `>`, from Lesson 06) to write its input into a new file `hello.sh`; the `<<'EOF' ... EOF` part is a heredoc — a way of feeding `cat` several lines of text directly, ending exactly at the line that just says `EOF`. The quotes around `'EOF'` specifically prevent Bash from trying to expand anything (like a `$variable`) inside the block — for this lesson's purposes, just recognize this pattern as "a way to write several lines into a file at once," rather than studying it further.

**A simpler, more familiar alternative:** you could just as well open `hello.sh` in any ordinary text editor (a code editor, `nano`, or similar), type the same two lines, and save it. The heredoc above is shown only because it's fully expressible as a single command block in this lesson; in your own practice, use whichever method you're comfortable with.

**Inspecting it** (Lesson 03):

```bash
cat hello.sh
```

**Executing it** (Section 6 covers this in full):

```bash
bash hello.sh
```

Example output:
```text
Hello from a shell script
```

**Observing the exit status** (Section 10 covers this in full):

```bash
echo $?
```

Example output:
```text
0
```

---

## 6. Executing Shell Scripts

There are two distinct ways to run a script file, and beginners frequently conflate them.

### `bash script.sh`

```bash
bash hello.sh
```

This tells Bash directly: "read this file and run its contents as commands." You're explicitly naming the interpreter (`bash`) and handing it the file. **The shebang line is irrelevant here** — you already told the system which interpreter to use by typing `bash` yourself.

### `./script.sh`

```bash
./hello.sh
```

This asks the system to run `hello.sh` **as a program, directly** — using the file's own shebang line to determine which interpreter should actually read it. `./` is a relative-path prefix (recall from Lesson 01: `.` means "the current directory") — it's required here so the shell knows you mean "the file right here," rather than searching `PATH` (Lesson 07, Section 15) for a command literally named `hello.sh`.

### Why these differ — and the permission connection

For `./hello.sh` to work, **the file must have executable permission** — the system needs to be told, as one of the file's own properties, "this file is allowed to be run directly as a program." `bash hello.sh` does **not** need this, because you're not asking the system to run the file directly at all — you're asking Bash (which you already have permission to run) to read the file's *contents* as input.

By default, a newly created text file does **not** have executable permission, which is why a fresh script typically fails with a permission-related error the first time you try `./script.sh` on it.

```bash
chmod +x hello.sh
```

`chmod +x` marks the file as executable, which then allows `./hello.sh` to work.

**This lesson deliberately explains `chmod +x` only to this minimum depth.** Permissions — what the bits actually mean, who can set them, the full read/write/execute model — are the dedicated subject of `09-permissions.md`, the very next lesson. This lesson only establishes *why* `chmod +x` is the specific, minimal step needed to make `./script.sh` work; it does not turn this into a permissions lesson.

**A precise correction, stated directly:** `chmod +x` is **not** required for `bash script.sh` to work — only for the `./script.sh` form. Claiming otherwise would be inaccurate, and this lesson does not make that claim.

---

## 7. Script Arguments

A script can receive **arguments** — values supplied when it's run, the same way a command like `grep "pattern" file.txt` receives `"pattern"` and `file.txt` as arguments.

```bash
./greet.sh Alice
```

Inside `greet.sh`, several special variables become available:

| Variable | Meaning |
|---|---|
| `$0` | The script's own name (as it was invoked) |
| `$1` | The first argument (`Alice`, in the example above) |
| `$2` | The second argument (if any) |
| `$3` | The third argument (if any), and so on |
| `$#` | The total number of arguments supplied |
| `$@` | All arguments, as separate values |

Example:

```bash
#!/usr/bin/env bash

echo "Script name: $0"
echo "First argument: $1"
echo "Number of arguments: $#"
```

Running `./greet.sh Alice`:

Example output:
```text
Script name: ./greet.sh
First argument: Alice
Number of arguments: 1
```

### `"$@"` vs. unquoted argument handling

```bash
for arg in "$@"; do
    echo "$arg"
done
```

Using **`"$@"`** (quoted) treats each argument as its own separate, intact item — even if one argument itself contains spaces. Using it **unquoted** (`$@`, no quotes) can cause an argument containing spaces to be incorrectly split into multiple pieces — the exact same "whitespace splits things unexpectedly" risk you already met with `xargs` in Lesson 05.

**This lesson does not go deeper into Bash's parameter-expansion rules than this one, practically important habit: prefer `"$@"` (quoted) over `$@` (unquoted) when working with a script's arguments.**

---

## 8. Variables in Shell Scripts

This section connects directly to Lesson 07 — it does not repeat that lesson's material, only applies it inside a script.

### Shell variables (script-local)

```bash
name="Alice"
echo "$name"
```

This creates an ordinary shell variable, exactly as in Lesson 07 — it exists for the life of this script's execution (and would be inherited by anything the script itself starts as a child process, per Lesson 07's inheritance model), but it is not automatically part of some broader "environment" beyond that.

### Why spaces around `=` break this

```bash
name = "Alice"
```

**This is incorrect in Bash** and will produce an error — Bash's assignment syntax requires `name=value` with **no spaces** around the `=`. With spaces, Bash instead interprets `name` as a command name, and `=` and `"Alice"` as separate arguments to it — an entirely different (and, here, invalid) instruction.

### Exported environment variables — a continuity connection only

```bash
export APP_ENV="development"
```

This is the exact same `export` from Lesson 07 — nothing new here beyond using it inside a script file instead of typing it interactively. A script can `export` a variable, and anything that script itself starts (a child process) will inherit it, following exactly Lesson 07's inheritance model.

### The distinction, restated for this context

- **Shell variable** (`name="Alice"`) — local to this script's own execution; not automatically handed to anything the script starts.
- **Environment variable** (`export APP_ENV="development"`) — handed to any child process the script itself starts, from that point forward, per Lesson 07.

A script can also **read** environment variables that were already exported *before* it was run — for example, if you ran `export APP_ENV="development"` in your shell and then ran a script, that script inherits `APP_ENV` automatically, exactly as any child process would (Lesson 07, Section 12).

---

## 9. Quoting

Reliable scripts depend on quoting variables correctly — this is one of the most consequential habits in this entire lesson.

### The three forms

```bash
name="AI Engineer"

echo $name        # unquoted
echo "$name"       # double-quoted
echo '$name'       # single-quoted
```

- **Unquoted** (`$name`) — Bash expands the variable, but the result is then subject to further word-splitting on spaces, exactly like the `$@` risk in Section 7. With `name="AI Engineer"`, unquoted `echo $name` can behave unexpectedly, because the space inside the value causes it to be treated as *two* separate words rather than one.
- **Double-quoted** (`"$name"`) — Bash still expands the variable (substitutes its value), but the result is treated as **one single, intact value**, spaces and all. This is the generally correct, safe default.
- **Single-quoted** (`'$name'`) — Bash does **not** expand anything inside single quotes at all; this would literally print the text `$name`, not its value.

### A simple failure caused by missing quotes

```bash
#!/usr/bin/env bash

name="AI Engineer"
echo $name
```

Example output (illustrating the word-splitting risk, using a command that reveals it — `printf` printing each word on its own line):
```text
AI
Engineer
```

versus the corrected version:

```bash
echo "$name"
```

Example output:
```text
AI Engineer
```

**The engineering habit this section builds:** quote your variables (`"$name"`) as the default, every time, unless you specifically understand and intend the unquoted, word-splitting behavior. This lesson does not go deeper into Bash's word-splitting/parsing rules beyond this practical habit.

---

## 10. Exit Status

Recall from Lesson 04 (Section 9) and Lesson 06 (Section 21): every command reports an **exit status** — a small signal, separate from anything it printed, indicating success or failure.

```bash
$?
```

`$?` holds the exit status of the **most recently completed command**.

```bash
echo "hello"
echo $?
```

Example output:
```text
hello
0
```

**The convention, stated precisely:**

- `0` **generally** means success.
- Any **non-zero** value **generally** means some kind of failure.

**An explicit, required correction:** this lesson does **not** claim every non-zero exit code means the same thing. Different programs use different non-zero values to signal different specific failure reasons — `$?` tells you *that* something didn't succeed, and (if you know the specific program's conventions) sometimes *what kind* of failure occurred, but "non-zero" as a category is not one single, universal meaning.

**Why scripts — and automation generally — care about exit status:**

- **Automation** — a calling script (or a human) can check `$?` to decide whether to proceed, retry, or stop.
- **CI/CD** (mentioned only for context; not taught here) — automated pipelines use a step's exit status to decide whether the overall pipeline continues or is marked failed.
- **Deployment** (same caveat) — a deployment step failing (non-zero) should typically halt the process rather than continue as if nothing went wrong.
- **Operational scripts** — a script that ignores exit status can silently continue past a real failure, producing a misleading "it finished" result that hides a genuine problem (exactly Lesson 06, Section 21's pipeline-failure lesson, now applied to whole scripts).
- **Failure detection generally** — exit status is the fundamental signal automation relies on to know whether something actually worked.

---

## 11. Conditional Execution

A basic `if` structure:

```bash
if [ "$APP_ENV" = "production" ]; then
    echo "Production environment"
else
    echo "Non-production environment"
fi
```

**Structure, piece by piece:**

- `if [ condition ]; then` — begins the conditional; `[ ... ]` is Bash's basic test syntax, checking the condition inside it.
- `"$APP_ENV" = "production"` — a string-equality test (note the quoting, per Section 9 — this protects against `APP_ENV` being empty or containing spaces).
- The lines between `then` and `else` run **only if** the condition is true.
- The lines between `else` and `fi` run **only if** the condition is false.
- `fi` — ends the `if` block (literally "if" spelled backward — a Bash convention for closing several block keywords).

### Simple command-success conditions, conceptually

```bash
if grep -q "ERROR" app.log; then
    echo "Errors were found"
fi
```

Here, the *condition* being tested is not a `[ ... ]` comparison at all — it's simply "did the command (`grep -q ...`, Lesson 04's quiet-mode search) succeed (exit status `0`) or fail?" This works because `if` can test the exit status of **any** command directly, not only the `[ ... ]` test syntax — a natural extension of Section 10's exit-status concept.

**This lesson deliberately stops here.** It does not attempt to be a complete reference for every Bash condition/comparison operator — only enough to read and write a simple, correct `if`/`else` block.

---

## 12. Loops

### `for` — iterate over a known list of items

```bash
for file in *.txt; do
    echo "$file"
done
```

**Step by step:** `*.txt` is a wildcard (Lesson 04, Section 6) — the shell expands it, *before* the loop even starts, into the actual list of matching filenames in the current directory. The loop then runs once for each filename in that list, with `file` set to the current one each time; `echo "$file"` (correctly quoted, per Section 9) prints it.

### `while` — repeat as long as a condition holds

```bash
count=1
while [ "$count" -le 3 ]; do
    echo "Count is $count"
    count=$((count + 1))
done
```

**Step by step:** `count=1` sets a starting value; `[ "$count" -le 3 ]` tests "is `count` less than or equal to 3?"; as long as that's true, the loop body runs, printing the current count and then incrementing it (`$(( ... ))` performs basic arithmetic — shown here only as much as needed for this one example, not taught as a separate topic).

Example output:
```text
Count is 1
Count is 2
Count is 3
```

**This lesson does not introduce** advanced loop control (like early-exit keywords beyond a passing mention), process substitution, coprocesses, or any other advanced shell metaprogramming — only these two foundational loop forms, sufficient for small, useful scripts.

---

## 13. Functions

```bash
greet() {
    echo "Hello, $1"
}

greet "Alice"
```

**Why functions exist:** to group a reusable sequence of commands under one name, so you don't repeat the same lines multiple times in the same script, and so a script's overall structure becomes easier to read (a short list of function calls, rather than one long unbroken sequence of commands).

**How it works:** `greet() { ... }` defines a function named `greet`; inside it, `$1` refers to whatever argument was passed to the *function* (not the overall script — the same `$1` convention from Section 7, but scoped to this function call). Calling `greet "Alice"` runs the function's body with `$1` set to `"Alice"`.

Example output:
```text
Hello, Alice
```

**Parameters:** exactly as shown above — a function receives its own arguments via `$1`, `$2`, etc., just like a whole script does.

**Return status, conceptually:** a function, like any command, produces an exit status (Section 10) when it finishes — by default, the exit status of the last command it ran. This lesson mentions this only conceptually, as a natural extension of Section 10's idea, without teaching Bash's more advanced explicit `return`-value patterns.

**How functions make scripts easier to maintain:** if the same three-step "check, prepare, report" sequence is needed in several places in a script, wrapping it in one function means fixing a bug, or improving it, in exactly one place — rather than hunting down every repeated copy.

---

## 14. Pipes and Redirection Inside Scripts

This section connects directly to Lesson 06 — nothing new is taught about pipes or redirection themselves here; they simply work **identically** inside a script file as they do when typed interactively.

```bash
#!/usr/bin/env bash

grep "ERROR" app.log | sort > sorted-errors.txt
```

This is exactly the pipeline from Lesson 06 (filter, then sort, then redirect to a file) — placed inside a script instead of typed directly. Nothing about how the pipe or the redirection behaves changes by being inside a file.

**The point this section makes, stated directly:** a shell script does not **replace** the command-line fundamentals from Lessons 01–06 — it **combines** them into a single, repeatable, named workflow. Everything you already know how to do at the prompt, you can now save.

---

## 15. Environment Variables and Configuration

This section connects directly to Lesson 07.

```bash
export APP_ENV="development"
bash run.sh
```

Here, `run.sh` inherits `APP_ENV` exactly as any child process would (Lesson 07, Section 12) — and inside `run.sh`:

```bash
echo "Environment: $APP_ENV"
```

**Why scripts often use environment variables for configuration:**

- **Configuration** — the same script can behave differently depending on what's already exported before it runs, without editing the script itself.
- **Portability** — the script doesn't need a hard-coded value baked in; the calling context supplies it.
- **Environment-specific behavior** — the exact `development`/`production` pattern from Section 11's conditional example.
- **Avoiding hard-coded environment assumptions** — a script that assumes one specific path, one specific hostname, or one specific mode baked directly into its own code is far less reusable than one that reads such things from its environment.

### Security warning — required, stated directly

**This lesson does not teach environment variables as inherently secure secret storage.** Exactly as established in Lesson 07 (Section 17), an environment variable is a convenient way to pass a value into a process — not a secure vault. **No real credentials, API keys, tokens, passwords, or private secrets appear anywhere in this lesson's examples.** Stronger secret-management approaches are explicitly deferred to later stages of this roadmap (Section 35's scope boundary).

---

## 16. Script Execution Model — Internal Mechanics

```text
Terminal
   ↓
Shell
   ↓
Launch script
   ↓
Interpreter
   ↓
Read script
   ↓
Parse commands
   ↓
Execute commands
   ↓
Child processes where required
   ↓
Commands produce output/status
   ↓
Script finishes
   ↓
Exit status
```

Step by step, in beginner-appropriate terms:

1. **The script itself is just a file** — plain text, nothing more, until something reads and runs it.
2. **Bash (the interpreter) reads the file** — either because you explicitly ran `bash script.sh`, or because the system used the shebang line to launch Bash for you (`./script.sh`, Section 6).
3. **Bash interprets the commands, one at a time**, in the order they appear in the file — exactly as it would if you'd typed them interactively.
4. **Some commands cause additional (child) processes to be created** — for example, `grep`, `sort`, or `python` inside the script each start as their own process (Module 0.2's process model), exactly as they would if typed directly at a prompt.
5. **stdout/stderr belong to whichever process is currently running** — Lesson 06's stdout/stderr model applies identically inside a script; a command inside the script can still be redirected or piped exactly as before.
6. **Environment variables may be inherited** — anything exported *before* the script started is available to it, and anything the script itself exports is available to whatever it, in turn, starts (Section 15).
7. **The script has its own process execution context** — while it's running, it's a process (running the Bash interpreter, executing your file's commands) with its own environment, its own current working directory, and so on.
8. **When the script finishes, it reports an exit status** — by default, the exit status of the last command it ran (echoing Section 10 and Section 13's function-return note).

**Connecting explicitly to Module 0.2:** everything above is the same processes / parent-child relationship / environment / standard I/O / pipes / exit-code model you already studied there — this lesson has simply shown you what that model looks like when the "process" in question is a saved script file, rather than a single typed command. This lesson does not repeat Module 0.2's full material, and does not go further into permissions here beyond Section 6's minimal, necessary mention (permissions proper is `09-permissions.md`, next).

---

## 17. Shell Scripts and the Operating System

A conceptual, OS-level view of what happens between typing `./script.sh` and seeing its output:

```text
user enters command
        ↓
shell parses command
        ↓
filesystem lookup
        ↓
permission/execution checks
        ↓
interpreter/script execution
        ↓
processes execute commands
        ↓
I/O occurs
        ↓
exit status returned
```

- **User enters command** — you type `./script.sh` (optionally with arguments).
- **Shell parses command** — your shell (Lesson 01's shell concept) recognizes this as a request to run a specific file, located via the `./` relative-path prefix.
- **Filesystem lookup** — the operating system locates the actual file at that path (Lesson 01's path-resolution model).
- **Permission/execution checks** — the system confirms the file is actually allowed to be run directly (Section 6's `chmod +x` connection; the full mechanics belong to `09-permissions.md`).
- **Interpreter/script execution** — the shebang line tells the system which interpreter (Bash, here) should read and run the file's contents.
- **Processes execute commands** — Bash works through the file's commands, starting child processes as needed (Section 16).
- **I/O occurs** — output appears on your terminal, or is redirected/piped exactly as any command's output would be (Lesson 06).
- **Exit status returned** — when everything finishes, an overall exit status is reported back (Section 10).

This connects directly to your existing Module 0.2 knowledge of processes and the shell — this lesson mentions **system calls** only conceptually, as "the operating system is asked to do these things," without turning into another dedicated system-call lesson (that material belongs to Module 0.2, already covered).

---

## 18. Real-World Software Engineering Uses

| Use case | Problem | Why a script helps | Limitation |
|---|---|---|---|
| **Local development setup** | Several manual setup steps every time you start working | One script runs them consistently | Doesn't replace understanding what each step actually does |
| **Project initialization** | Repeatedly creating the same directory/file scaffolding for new projects | A script scaffolds it identically every time | Still needs updating if the desired scaffolding changes |
| **Running test commands** | Remembering the exact test command and its flags | A script encodes it once, correctly | Doesn't replace an actual testing framework's own capabilities |
| **Formatting/linting** | Running the same code-quality tools before every commit | A script runs them all in one step | The tools themselves still do the real work; the script is just glue |
| **Starting development services** | Manually starting several local processes in the right order | A script starts them consistently | Doesn't manage complex service dependencies robustly |
| **Data preparation** | Repeating the same filter/sort/extract steps (Lesson 05) on new data | A script applies the same steps reliably | Not suited to complex, branching data-transformation logic |
| **Artifact preparation** | Assembling files into a specific shape before a next step | A script automates the assembly | Still needs a human decision if the required shape changes significantly |
| **Backup workflows** | Manually copying important files somewhere safe | A script does the copy consistently (Lesson 02's `cp`) | Not a substitute for a real, tested backup/restore system at scale |
| **Log inspection** | Running the same `grep`/`sort`/`tail` sequence to check logs | A script bundles the sequence | Doesn't replace real log-monitoring tooling for production scale |
| **Build automation** | Running the same multi-step build command sequence | A script encodes the sequence | Complex builds are usually better served by a dedicated build tool |
| **Deployment preparation** | Gathering and arranging files before a deployment step | A script automates the arrangement | Actual deployment mechanics are a separate, later topic (Section 35) |
| **Operational maintenance** | Routine, repeatable maintenance checks | A script runs the checks the same way each time | Doesn't replace monitoring/alerting for anything urgent |

---

## 19. Applied AI Engineering Use Cases

**This section is important — it connects everything above to your actual roadmap destination.**

### Dataset preparation

```text
download/preparation
        ↓
directory setup
        ↓
validation
        ↓
processing command
```

A script can create the expected directory structure (Lesson 02's `mkdir`), confirm expected files are present (Lesson 04's `find`), and run a processing step — all as one repeatable procedure, run identically every time new data arrives.

### Model workflow

```text
prepare data
   ↓
run training
   ↓
save artifacts
   ↓
run evaluation
```

A script can be the "glue" that runs each of these steps in order, checking (via exit status, Section 10) that each one actually succeeded before moving to the next.

### LLM application development

- **Starting local services** — a script that starts whatever local processes a development environment needs.
- **Preparing configuration** — exporting the right environment variables (Section 15) before running an application.
- **Running evaluation commands** — a script that runs a fixed evaluation command against a set of inputs.
- **Invoking batch jobs** — running the same command across a batch of inputs (conceptually connecting to Lesson 05's `xargs`, without re-teaching it).
- **Collecting artifacts** — gathering generated output files into one place (Lesson 02's `mv`/`cp`).
- **Inspecting logs** — the same log-investigation pattern from Section 18, applied to an LLM application's logs.
- **Launching development environments** — a single script that sets up everything needed to start working.

### Agentic AI development

- **Running test workflows** — a repeatable script that runs a fixed set of test commands.
- **Preparing fixtures** — setting up known, disposable test data the same way every time.
- **Launching local dependencies** — starting whatever a local agent development setup needs, consistently.
- **Running evaluation suites** — the same "run this fixed sequence of checks" pattern, applied to agent behavior.
- **Collecting execution artifacts** — gathering logs/outputs from an agent run into one place for review.

**The key conceptual point:** shell scripts are very often the **orchestration glue** *around* Python programs, CLIs, services, containers, and infrastructure tools — not a replacement for any of them. This lesson does not teach Docker, Kubernetes, CI/CD systems, cloud deployment, or agent frameworks — those are separate, later stages of this roadmap. The only claim made here is the connective one: the scripting skill you're building in this lesson is exactly the skill that ties those later, more sophisticated tools together in real workflows.

---

## 20. When Shell Scripts Are Appropriate

**Good cases for shell scripting:**

- Short, well-understood command sequences.
- Filesystem automation (creating, organizing, cleaning up files/directories).
- CLI orchestration — running several existing command-line tools in sequence.
- Development workflows — setup, teardown, routine local tasks.
- Deployment "glue" — arranging files/steps around a deployment, not the deployment logic itself.
- Environment setup — exporting configuration, preparing a workspace.
- Simple operational automation — routine, repeatable, low-complexity checks or tasks.

**When shell scripting should *not* be the main implementation:**

- Complex application logic — many interacting rules, deep branching, intricate decision-making.
- Complex data structures — Bash has only limited, awkward support for anything beyond simple strings and lists.
- Complicated error handling — handling many distinct failure modes gracefully is difficult and fragile in Bash compared to a real programming language.
- Large, maintainable applications — Bash scripts become hard to read, test, and maintain as they grow large.
- Sophisticated business logic — logic with many rules and edge cases deserves a language with better structure, testing, and tooling.
- Cross-platform applications requiring strong portability — Bash scripts don't run unchanged on every platform (Section 24 returns to this directly).
- Large data-processing logic — better suited to a language (like Python, introduced properly later in this roadmap) with real data structures and libraries.

### Shell script vs. Python program (conceptual comparison only)

| | Shell script | Python program |
|---|---|---|
| Best for | Short command sequences, filesystem/CLI glue | Complex logic, data structures, larger applications |
| Error handling | Basic (exit status, simple conditionals) | Rich (structured error handling) |
| Data structures | Minimal (strings, simple lists) | Rich (native structures, libraries) |
| Portability | Bash-specific; not automatically cross-platform | More consistently portable across platforms |
| Typical role in this roadmap | Orchestration glue around tools/processes | The application logic itself |

This lesson does not teach Python — this table exists purely to help you recognize, later, when you've outgrown what a shell script should reasonably do.

---

## 21. Common Shell-Scripting Mistakes

**1. Wrong shebang**
- *Symptom:* the script fails to run as expected, or runs with an unexpected interpreter.
- *Likely cause:* a typo in the shebang line, or omitting it entirely.
- *Diagnosis:* inspect the first line of the file directly.
- *Correction:* use `#!/usr/bin/env bash` as taught in Section 4.
- *Prevention:* always make the shebang the very first line, with no typos.

**2. Script not executable**
- *Symptom:* `./script.sh` fails with a permission-related error.
- *Likely cause:* the file was never marked executable.
- *Diagnosis:* check whether `chmod +x` was ever run on this file.
- *Correction:* `chmod +x script.sh`.
- *Prevention:* remember this is a one-time step needed only for `./script.sh`, not for `bash script.sh` (Section 6).

**3. Running `./script.sh` from the wrong directory**
- *Symptom:* "No such file or directory," even though the script clearly exists somewhere.
- *Likely cause:* your current working directory (Lesson 01) isn't where the script actually is.
- *Diagnosis:* `pwd`, then `ls`, to confirm.
- *Correction:* `cd` to the correct directory, or use the correct relative/absolute path.
- *Prevention:* the same navigation discipline from every earlier lesson.

**4. Using `bash script.sh` vs. `./script.sh` incorrectly**
- *Symptom:* confusion about why one form works and the other doesn't in a given situation.
- *Likely cause:* forgetting that `./script.sh` needs executable permission and relies on the shebang, while `bash script.sh` needs neither.
- *Diagnosis:* re-read Section 6's distinction.
- *Correction:* choose the form that matches your actual situation (no execute permission yet → use `bash script.sh`, or grant it with `chmod +x`).
- *Prevention:* internalize the two forms as genuinely different mechanisms, not interchangeable syntax.

**5. Missing quotes**
- *Symptom:* a variable containing spaces behaves unexpectedly (Section 9).
- *Likely cause:* using `$var` instead of `"$var"`.
- *Diagnosis:* check whether the value in question could ever contain spaces or special characters.
- *Correction:* quote it: `"$var"`.
- *Prevention:* quote variables by default, always.

**6. Spaces around variable assignment**
- *Symptom:* `name = "Alice"` produces an error.
- *Likely cause:* Bash's assignment syntax requires no spaces around `=` (Section 8).
- *Diagnosis:* look at the exact assignment line.
- *Correction:* `name="Alice"`.
- *Prevention:* always write `name=value`, no spaces.

**7. Misspelled variable names**
- *Symptom:* a variable appears empty when read back.
- *Likely cause:* the name used when reading doesn't exactly match the name used when assigning — echoing Lesson 07, Section 19's identical warning.
- *Diagnosis:* compare both occurrences character by character.
- *Correction:* make the names match exactly.
- *Prevention:* consistent, careful naming.

**8. Assuming variables are automatically exported**
- *Symptom:* a variable a script sets doesn't seem to be visible to something the script starts.
- *Likely cause:* the variable was never `export`ed (Section 8, and Lesson 07, Section 7).
- *Diagnosis:* check whether `export` was actually used.
- *Correction:* add `export` if the value genuinely needs to reach a child process.
- *Prevention:* remember: plain assignment is script-local only.

**9. Confusing shell variables with environment variables**
- *Symptom:* general confusion about why some values "carry over" to child processes and others don't.
- *Likely cause:* not distinguishing the two categories from Lesson 07 (Section 7).
- *Diagnosis:* ask, for the specific variable in question: was it exported, or not?
- *Correction:* re-apply Lesson 07's distinction deliberately.
- *Prevention:* treat "exported" as a conscious decision, not an assumption.

**10. Forgetting argument validation**
- *Symptom:* a script behaves strangely, or fails confusingly, when run with too few (or unexpected) arguments.
- *Likely cause:* the script assumed arguments would always be present and well-formed.
- *Diagnosis:* check what `$#` (Section 7) actually was when the failure occurred.
- *Correction:* check `$#` (or specific arguments) explicitly before relying on them.
- *Prevention:* validate expected inputs near the top of a script, before using them.

**11. Wrong argument position**
- *Symptom:* a script reads the wrong value into the wrong place.
- *Likely cause:* confusing `$1`/`$2`/etc. ordering, or the caller supplying arguments in an unexpected order.
- *Diagnosis:* print `$1`, `$2`, etc. explicitly to confirm what was actually received.
- *Correction:* correct either the script's expectations or the calling command's argument order.
- *Prevention:* document, in a comment, exactly what order a script expects its arguments in.

**12. Ignoring exit status**
- *Symptom:* a script appears to "finish successfully" even though an important step actually failed.
- *Likely cause:* never checking `$?` (or a command's success) after a step that could fail.
- *Diagnosis:* re-run the specific step and check `$?` immediately afterward.
- *Correction:* add an explicit check (an `if`, per Section 11) after important steps.
- *Prevention:* treat every consequential command's exit status as worth checking, not assuming.

**13. Continuing after a failed command**
- *Symptom:* later steps run using bad/missing data because an earlier step actually failed.
- *Likely cause:* a script has no logic to stop when something goes wrong (directly echoing Lesson 06, Section 21's pipeline-failure lesson).
- *Diagnosis:* trace back to the first step that could plausibly have failed.
- *Correction:* check exit status after critical steps, and stop (or handle it) if it indicates failure.
- *Prevention:* don't assume "the script printed something" means "everything worked."

**14. Incorrect conditional syntax**
- *Symptom:* a syntax error when running the script, often near an `if` line.
- *Likely cause:* missing spaces inside `[ ... ]` (Bash requires spaces around the brackets), or a missing `then`/`fi`.
- *Diagnosis:* compare the exact `if` line against Section 11's example structure.
- *Correction:* fix spacing/keywords to match the correct structure.
- *Prevention:* copy the structural pattern exactly until it becomes familiar.

**15. Incorrect loop syntax**
- *Symptom:* a syntax error near a `for`/`while` line, or a loop that doesn't do what was intended.
- *Likely cause:* a missing `do`/`done`, or a malformed condition.
- *Diagnosis:* compare against Section 12's examples structurally.
- *Correction:* fix the structure to match.
- *Prevention:* same as above — follow the established pattern closely while still learning.

**16. Wildcard matching unexpected files**
- *Symptom:* a `for file in *.txt` loop (or similar) processes more, or different, files than intended.
- *Likely cause:* the wildcard matched more broadly than assumed (directly echoing Lesson 04, Section 6's `find` wildcard caution, and Lesson 05's `xargs` caution).
- *Diagnosis:* run `ls *.txt` (or the equivalent pattern) first, separately, to see exactly what would match.
- *Correction:* narrow the pattern, or the directory, until it matches only what's intended.
- *Prevention:* always check a wildcard's actual matches before using it inside a loop that does anything consequential.

**17. Filenames containing spaces**
- *Symptom:* a loop or argument-handling step splits one filename into multiple pieces unexpectedly.
- *Likely cause:* unquoted variable/argument handling (Sections 7, 9) colliding with a filename containing a space.
- *Diagnosis:* check whether any relevant filename actually contains a space.
- *Correction:* quote consistently (`"$file"`, `"$@"`).
- *Prevention:* quote by default, everywhere, as a habit — not just when you remember a specific filename might be tricky.

**18. Assuming Bash behavior works identically in PowerShell**
- *Symptom:* a script (or a piece of syntax) that works in Bash fails, or behaves differently, in PowerShell.
- *Likely cause:* assuming the two shells share syntax or semantics (Section 24 explains why this assumption is wrong).
- *Diagnosis:* confirm which shell is actually being used.
- *Correction:* use the appropriate shell's own syntax; do not attempt to run a Bash script unchanged in PowerShell.
- *Prevention:* remember Bash and PowerShell are genuinely different tools, not two dialects of the same thing.

**19. Hard-coding machine-specific paths**
- *Symptom:* a script works on one machine but fails immediately on another.
- *Likely cause:* a path specific to one particular computer's layout was written directly into the script.
- *Diagnosis:* look for any absolute path in the script that assumes a specific machine's structure.
- *Correction:* use relative paths, arguments, or environment variables (Section 15) instead of a hard-coded absolute path.
- *Prevention:* ask "would this path exist on someone else's machine?" before hard-coding it.

**20. Exposing secrets in script contents or output**
- *Symptom:* a sensitive value ends up visible in the script's own text, or printed to the terminal/logs.
- *Likely cause:* writing a real credential directly into a script, or printing/echoing a variable that happens to hold one, without thinking about where that output goes.
- *Diagnosis:* review the script's contents and any place it prints a variable's value.
- *Correction:* never place real secrets in a script's text; avoid printing sensitive variables at all (directly echoing Lesson 07, Section 17's security principle).
- *Prevention:* treat this as a standing rule for every script you ever write, not just this lesson's examples.

---

## 22. Debugging Shell Scripts

Work through each scenario's reasoning *before* reading the fix and lesson.

**Scenario 1 — `Permission denied`**
- *Situation:* you run `./script.sh` for the first time.
- *Incorrect example:* `./script.sh`
- *Expected behavior:* the script runs and prints its output.
- *Actual/symptomatic behavior:* `bash: ./script.sh: Permission denied`
- *Investigation steps:* check the file's permissions (a brief look ahead to `09-permissions.md`, using only what Section 6 already explained).
- *Root cause:* the file was never marked executable.
- *Fix:* `chmod +x script.sh`, then retry `./script.sh`.
- *Engineering lesson:* `./script.sh` depends on executable permission; `bash script.sh` does not (Section 6).

**Scenario 2 — `command not found`**
- *Situation:* you try to run a script by typing just its name.
- *Incorrect example:* `script.sh`
- *Expected behavior:* the script runs.
- *Actual/symptomatic behavior:* `bash: script.sh: command not found`
- *Investigation steps:* recall Lesson 07's `PATH` discussion — is the current directory in `PATH`?
- *Root cause:* the shell searches `PATH` for a bare command name, and (by design, on most systems) the current directory is not normally included in `PATH`.
- *Fix:* use `./script.sh` (explicitly pointing at the file here) or `bash script.sh`.
- *Engineering lesson:* running a script directly by its bare name (without `./` or `bash`) relies on `PATH`, which usually doesn't include your current directory.

**Scenario 3 — script works with `bash script.sh` but not `./script.sh`**
- *Situation:* `bash script.sh` runs fine; `./script.sh` fails.
- *Incorrect example:* `./script.sh`
- *Expected behavior:* both forms should run the script.
- *Actual/symptomatic behavior:* a permission-related failure specifically on the `./` form.
- *Investigation steps:* check execute permission specifically (Section 6).
- *Root cause:* the file lacks executable permission — irrelevant to `bash script.sh`, required for `./script.sh`.
- *Fix:* `chmod +x script.sh`.
- *Engineering lesson:* this is exactly Section 6's core distinction, observed directly.

**Scenario 4 — variable appears empty**
- *Situation:* `echo "$name"` inside a script prints nothing.
- *Incorrect example:* the script reads `$Name` but the assignment was `name="Alice"`.
- *Expected behavior:* the script should print `Alice`.
- *Actual/symptomatic behavior:* nothing is printed.
- *Investigation steps:* compare the exact variable name at the point of assignment against the point of use.
- *Root cause:* a case mismatch (`name` vs. `Name`) — Bash variable names are case-sensitive, so these are two entirely different, unrelated variables.
- *Fix:* make both names match exactly.
- *Engineering lesson:* an empty result from a misspelled/mismatched name produces no error at all — always suspect this first when a variable "just doesn't have a value."

**Scenario 5 — variable is not inherited by a child process**
- *Situation:* a script sets `MODEL_NAME` and then runs a Python command expecting to read it.
- *Incorrect example:* `MODEL_NAME="example-model"` (no `export`), followed by `python3 -c "import os; print(os.environ.get('MODEL_NAME'))"`.
- *Expected behavior:* Python should print `example-model`.
- *Actual/symptomatic behavior:* Python prints `None`.
- *Investigation steps:* confirm whether `export` was actually used (directly echoing Lesson 07, Section 29, Scenario 1).
- *Root cause:* a plain shell variable is never handed to a child process (Section 8).
- *Fix:* `export MODEL_NAME="example-model"`.
- *Engineering lesson:* the exact same inheritance rule from Lesson 07 applies identically inside scripts.

**Scenario 6 — argument containing spaces breaks**
- *Situation:* a script is called with `./process.sh "final report.txt"`, expecting one argument.
- *Incorrect example:* inside the script, `echo $1` (unquoted).
- *Expected behavior:* the script should treat `"final report.txt"` as one single argument.
- *Actual/symptomatic behavior:* the value gets split unexpectedly when used further in the script (e.g. in a loop or another command).
- *Investigation steps:* check whether `$1` (or `$@`) was quoted anywhere it was subsequently used.
- *Root cause:* unquoted variable expansion allows word-splitting on the internal space (Section 9).
- *Fix:* use `"$1"` (quoted) everywhere the value is used.
- *Engineering lesson:* quoting matters most exactly where you'd assume it doesn't — with values you "know" only ever came from one argument.

**Scenario 7 — wildcard matches unexpected files**
- *Situation:* `for file in *.log; do rm "$file"; done` (intending to remove only old log files) — note: this exact destructive form is discussed conceptually only, never actually run in this lesson's exercises, per the safety requirements in Section 29's cautions.
- *Incorrect example:* running the loop without first checking what `*.log` actually matches.
- *Expected behavior:* only the intended old logs are affected.
- *Actual/symptomatic behavior:* an unexpected file matching `*.log` is also affected.
- *Investigation steps:* run `ls *.log` (a safe, read-only check) *before* trusting the pattern in anything destructive.
- *Root cause:* the wildcard matched more broadly than assumed (Section 21, mistake 16).
- *Fix:* narrow the pattern or the directory until `ls` confirms only the intended files match.
- *Engineering lesson:* never trust a wildcard's scope inside a script without checking it first, especially before anything irreversible.

**Scenario 8 — script continues despite a failed command**
- *Situation:* a script has several sequential steps; one fails partway through, but the script keeps going and reports "done" at the end.
- *Incorrect example:* no exit-status check after a step that can plausibly fail.
- *Expected behavior:* the script should stop, or clearly flag the failure, rather than continuing as if nothing happened.
- *Actual/symptomatic behavior:* later steps run on bad or missing data, and the script's final message is misleadingly reassuring.
- *Investigation steps:* re-run each step manually, checking `$?` after each one, to find which step actually failed.
- *Root cause:* the script never checked exit status (Section 21, mistakes 12–13).
- *Fix:* add an explicit `if` check (Section 11) after the critical step, and decide deliberately what should happen on failure.
- *Engineering lesson:* "the script finished" and "the script succeeded" are not the same claim.

**Scenario 9 — relative path fails**
- *Situation:* a script references `./input/data.txt`, and works when run from one directory but fails when run from another.
- *Incorrect example:* `cat ./input/data.txt` inside the script, run from an unexpected current working directory.
- *Expected behavior:* the script should find the file regardless of where it's launched from — or, at minimum, fail with a clear, expected reason.
- *Actual/symptomatic behavior:* "No such file or directory."
- *Investigation steps:* check `pwd` at the moment the script was launched, and compare against where `input/` actually lives.
- *Root cause:* the relative path was resolved against the wrong current working directory (directly echoing Lesson 01's core lesson).
- *Fix:* either always run the script from the expected directory, or have the script determine its own location and build paths from there (a technique this lesson does not teach in depth).
- *Engineering lesson:* a script that relies on relative paths is implicitly relying on being run from a specific directory — worth stating as an explicit assumption (Section 25).

**Scenario 10 — wrong shell/interpreter**
- *Situation:* a script written for Bash is run using a different shell/interpreter, or a PowerShell script is mistakenly assumed to be runnable via Bash.
- *Incorrect example:* attempting to run a `.ps1` PowerShell script's syntax as if it were Bash, or vice versa.
- *Expected behavior:* the script's own syntax should be understood correctly.
- *Actual/symptomatic behavior:* syntax errors, or behavior that doesn't match what the script's author intended.
- *Investigation steps:* confirm which shell/interpreter the script was actually written for (check its shebang, or its file extension convention).
- *Root cause:* Bash and PowerShell are genuinely different languages/environments (Section 21, mistake 18; Section 24).
- *Fix:* run the script with the interpreter it was actually written for.
- *Engineering lesson:* never assume syntax portability between fundamentally different shells.

**Scenario 11 — conditional behaves unexpectedly**
- *Situation:* an `if [ "$APP_ENV" = "production" ]` check doesn't seem to take the branch you expect.
- *Incorrect example:* `if [ $APP_ENV = "production" ]` (unquoted).
- *Expected behavior:* the comparison should correctly detect whether `APP_ENV` equals `"production"`.
- *Actual/symptomatic behavior:* a syntax error, or incorrect behavior, especially if `APP_ENV` happens to be unset or empty.
- *Investigation steps:* check whether the variable inside `[ ... ]` was quoted.
- *Root cause:* an unquoted, empty/unset variable can turn `[ $APP_ENV = "production" ]` into malformed syntax (`[ = "production" ]`) — exactly the quoting risk from Section 9, applied inside a condition.
- *Fix:* quote it: `[ "$APP_ENV" = "production" ]`.
- *Engineering lesson:* quoting inside conditionals isn't optional politeness — it prevents genuinely broken syntax when a variable turns out to be empty.

**Scenario 12 — script succeeds locally but fails in another environment**
- *Situation:* a script that works perfectly on your machine fails when run somewhere else (another machine, another user's setup).
- *Incorrect example:* a script containing a hard-coded, machine-specific path (Section 21, mistake 19).
- *Expected behavior:* the script should work anywhere its stated assumptions are met.
- *Actual/symptomatic behavior:* "No such file or directory," or a similarly environment-specific failure, elsewhere.
- *Investigation steps:* review the script for any assumption (a specific path, a specific installed tool, a specific pre-set environment variable) that might not hold true on the other machine.
- *Root cause:* an unstated, machine-specific assumption baked into the script.
- *Fix:* replace the hard-coded assumption with something portable (a relative path, an argument, or a documented required environment variable).
- *Engineering lesson:* "works on my machine" is not the same as "correct" — this is precisely why Section 25 emphasizes making assumptions explicit.

---

## 23. Safe Practical Demonstration

Everything below uses a **disposable, learner-created practice area** — for example, `/tmp/shell-script-lesson-demo/`. **This lesson does not create this directory for you.** You may create it manually, using commands from earlier lessons:

```bash
mkdir -p /tmp/shell-script-lesson-demo/input /tmp/shell-script-lesson-demo/output /tmp/shell-script-lesson-demo/scripts
cd /tmp/shell-script-lesson-demo
```

**No command in this section has actually been executed by this lesson.** Every result shown is explicitly labeled `Example output:` — an illustration of expected behavior, never a captured result. Nothing here modifies the real Applied AI Engineering project, uses `sudo`, installs software, creates a Git repository, or touches any file outside this disposable area.

**1. Create a script**

```bash
cat > scripts/greet.sh <<'EOF'
#!/usr/bin/env bash

echo "Hello, $1"
EOF
```

**2. Inspect it**

```bash
cat scripts/greet.sh
```

**3. Execute it with Bash**

```bash
bash scripts/greet.sh Alice
```
Example output:
```text
Hello, Alice
```

**4. Make it executable**

```bash
chmod +x scripts/greet.sh
```

**5. Execute with `./`**

```bash
cd scripts
./greet.sh Alice
cd ..
```
Example output:
```text
Hello, Alice
```

**6. Pass arguments**

```bash
bash scripts/greet.sh Bob
```
Example output:
```text
Hello, Bob
```

**7. Use variables**

```bash
cat > scripts/config-demo.sh <<'EOF'
#!/usr/bin/env bash

app_env="development"
echo "App environment: $app_env"
EOF
bash scripts/config-demo.sh
```
Example output:
```text
App environment: development
```

**8. Use conditions**

```bash
cat > scripts/check-env.sh <<'EOF'
#!/usr/bin/env bash

if [ "$1" = "production" ]; then
    echo "Production mode"
else
    echo "Non-production mode"
fi
EOF
bash scripts/check-env.sh production
```
Example output:
```text
Production mode
```

**9. Use loops**

```bash
printf "one\ntwo\nthree\n" > input/sample.txt
cat > scripts/read-lines.sh <<'EOF'
#!/usr/bin/env bash

while read -r line; do
    echo "Line: $line"
done < "$1"
EOF
bash scripts/read-lines.sh input/sample.txt
```
Example output:
```text
Line: one
Line: two
Line: three
```
(This introduces `read -r` and Lesson 06's `<` input redirection together, purely as a natural, safe way to demonstrate a `while` loop over a file's lines — not as a new topic to master beyond this one example.)

**10. Check exit status**

```bash
bash scripts/greet.sh Alice
echo $?
```
Example output:
```text
Hello, Alice
0
```

**Cleanup:**

```bash
cd /tmp
rm -r /tmp/shell-script-lesson-demo
```

---

## 24. Cross-Platform Coverage

**Bash** is the primary shell scripting environment for this lesson — every example above is Bash syntax.

**Linux/Ubuntu** is the primary environment for command-line and scripting practice throughout this roadmap.

**WSL2** provides a genuine Linux environment on Windows, and is entirely appropriate for practicing everything in this lesson exactly as written. One thing worth knowing: filesystem boundaries and Windows/Linux interoperability (crossing between WSL2's Linux filesystem and Windows' native filesystem, e.g. `/mnt/c/...` paths — the same point made in Lessons 02 and 04) can sometimes create path or permission differences worth being aware of, though this lesson does not go deeper into that interop configuration.

**Git Bash** provides a Bash-like environment on Windows; the commands and scripts in this lesson generally behave the same way there as in Linux Bash.

**PowerShell** is a genuinely **different** shell and scripting environment — different syntax, different conventions, a different underlying model (echoing Lessons 05 and 06's notes on PowerShell's object-oriented pipeline). **This lesson does not teach PowerShell scripting.** A Bash script does **not** automatically run, unchanged, in PowerShell — the two are not interchangeable, and this lesson makes no claim otherwise.

---

## 25. Reliability and Safety Practices

- **Quote variables** — as a default habit, not an occasional afterthought (Section 9).
- **Validate inputs** — check that expected arguments/variables are actually present before relying on them (Section 21, mistake 10).
- **Use meaningful names** — for variables, functions, and the script itself.
- **Use comments where necessary** — to explain *why*, not to restate *what* the code already says.
- **Keep scripts small** — a script that's grown too large and complex is a signal to reconsider whether Bash is still the right tool (Section 20).
- **Avoid unnecessary global state** — prefer passing values explicitly (arguments, function parameters) over relying on many loosely tracked variables.
- **Check important command failures** — via exit status (Section 10), especially for anything the rest of the script depends on.
- **Avoid hard-coded machine-specific paths** — Section 21, mistake 19.
- **Avoid destructive commands** — especially while a script is still being written and tested.
- **Avoid exposing secrets** — Section 21, mistake 20; Section 15's security warning.
- **Test scripts in disposable environments** — exactly as Section 23 modeled.
- **Make assumptions explicit** — if a script assumes a specific starting directory, a specific pre-set variable, or a specific installed tool, say so (in a comment, or an explicit check).
- **Document expected inputs** — what arguments, and what pre-existing environment variables, does this script actually require?
- **Keep automation predictable** — the same inputs should produce the same outcome, every time.

### `set -e` — introduced carefully, as a conceptual topic only

```bash
set -e
```

**What this does, conceptually:** placed near the top of a script, `set -e` causes the script to **exit immediately** if a command it runs returns a non-zero exit status (Section 10) — rather than continuing on to the next line as it would by default.

**A required, explicit correction:** `set -e` is **not** a complete error-handling solution. It has real, important edge cases (certain contexts — inside some conditionals, some pipelines, and a few other situations — don't trigger it the way a beginner might expect), and relying on it as if it guarantees "my script will always stop safely on any failure" is a mistake. This lesson introduces it only as a concept worth knowing exists, not as something to adopt uncritically or rely on as your only safety net — checking exit status explicitly where it matters (Section 11's `if` pattern) remains the more reliable, beginner-appropriate habit taught in this lesson.

**This lesson does not teach** `set -u`, `pipefail` (already mentioned only introductorily back in Lesson 06, Section 21), traps, or other shell "strict mode" options in any depth — these belong to more advanced Bash study, out of this lesson's scope.

---

## 26. Testing Shell Scripts

Testing a shell script means deliberately running it against a range of situations, not just the one "happy path" case you first wrote it for:

```text
normal input
invalid input
missing input
unexpected environment
command failure
```

- **Normal input** — does the script do the right thing with reasonable, expected input?
- **Invalid input** — what happens if an argument is malformed, or a file doesn't contain what's expected?
- **Missing input** — what happens if an expected argument, or an expected file, is simply absent (Section 21, mistake 10)?
- **Unexpected environment** — what happens if an environment variable the script expects was never exported (Section 22, Scenario 5)?
- **Command failure** — what happens if a step inside the script itself fails (Section 22, Scenario 8)?

**How to test, at this beginner stage:** run the script deliberately against each of these situations, using **disposable inputs** (never real project data), and observe — did it behave the way you expected, or did it silently do the wrong thing?

**Connecting to the roadmap's production-engineering principle:** a system should be **tested**, not merely demonstrated once and assumed correct. A script you've only ever run once, with exactly the input you happened to have on hand, has not actually been shown to work — only shown to work *that one time*. This lesson does not introduce any external testing framework — only this simple, deliberate habit of trying a script against several different situations before trusting it.

---

## 27. Mini-Project — Command-Line Workflow Automation Script

**Goal:** build a small shell script that automates a safe, repeatable command-line workflow — demonstrating script creation, the shebang, comments, variables, arguments, quoting, environment variables, conditions, loops, functions, pipes/redirection, exit status, basic validation, safe filesystem operations, and debugging — all in one project.

**Requirements:**
- No Git repository.
- No external APIs.
- No cloud services.
- No destructive operations.
- Entirely inside a disposable, learner-created directory.

**Directory structure (to be created by you, manually, using earlier-lesson commands — not created automatically by this lesson):**

```text
workflow-project/
├── input/
├── output/
└── scripts/
```

**Objective:** write one script, `scripts/process.sh`, that:

1. Accepts one argument: the name of a file inside `input/` to process.
2. Validates that the argument was actually supplied, and that the file actually exists — reporting a clear message and a non-zero exit status if not.
3. Reads a configuration value from an environment variable (e.g. `LOG_LEVEL`), with a sensible default if it isn't set.
4. Uses a function to print a formatted status message.
5. Filters the input file's lines for a specific keyword (Lesson 04's `grep`), sorts the result (Lesson 05's `sort`), and writes it to a file inside `output/` (Lesson 06's redirection).
6. Uses a loop to report, line by line, how many matching lines were found (or simply to display them).
7. Checks the exit status of its key step and reports success or failure clearly at the end.

**Conceptual workflow:**

```text
input files
     ↓
inspect files
     ↓
filter/select files
     ↓
process/organize information
     ↓
write output
     ↓
report result
```

**Implementation steps (for you to carry out, in your own disposable directory):**

1. Create the directory structure shown above.
2. Create a harmless sample file inside `input/` (a few lines of plain text, with at least one line containing a keyword like `"ERROR"`).
3. Write `scripts/process.sh`, building it up piece by piece: shebang and comments first, then argument validation, then the environment-variable read, then the function, then the filter/sort/redirect step, then the loop, then the final exit-status report.
4. Make it executable (`chmod +x`), and confirm it also runs correctly via `bash scripts/process.sh ...`.
5. Run it against your sample file and inspect the resulting output file.

**Expected behavior:** running `./scripts/process.sh sample.txt` (with the current directory set appropriately, or an adjusted path) should validate the argument, read `LOG_LEVEL` (using a default if unset), filter and sort the matching lines into `output/`, report how many were found, and finish with a clear success message and exit status `0`.

**Test cases** (per Section 26):
- Normal input: a real file, containing at least one matching line.
- Invalid input: a filename that doesn't exist inside `input/`.
- Missing input: running the script with no argument at all.
- Unexpected environment: running it with `LOG_LEVEL` unset, to confirm the default kicks in correctly.
- Command failure: deliberately pointing the script at a file with no matching lines at all, to confirm it still reports clearly (zero matches is not the same as a broken script).

**Debugging cases:** deliberately reintroduce one mistake from Section 21 (for example, remove a needed `export`, or unquote a variable that should be quoted) and confirm you can diagnose and fix it using the reasoning style from Section 22.

**Extension challenges** (optional, staying within this lesson's scope): add a second optional argument controlling how many matching lines to display; add a simple `for` loop that processes every `.txt` file inside `input/` in one run, instead of just one named file.

**Completion checklist:**
- [ ] Script has a correct shebang and at least one explanatory comment.
- [ ] Script validates its argument and reports a clear error (with non-zero exit status) if missing/invalid.
- [ ] Script reads at least one environment variable, with a sensible default.
- [ ] Script defines and uses at least one function.
- [ ] Script uses a pipe and output redirection together.
- [ ] Script uses at least one loop.
- [ ] Script checks and reports its own exit status/success clearly.
- [ ] Script has been run successfully via both `bash scripts/process.sh ...` and `./scripts/process.sh ...`.
- [ ] All five test cases from above were actually tried.
- [ ] The disposable project directory was cleaned up afterward.

---

## 28. Exercises

All Level 3–5 practical work should be done inside your own disposable directory, using only harmless placeholder content. Never modify the real Applied AI Engineering project.

### Level 1 — Recognition

1. What symbol combination starts a shebang line?
2. Which variable holds a script's first argument?
3. Which variable holds the total number of arguments supplied to a script?
4. Which command marks a script file as executable?
5. Which exit status value conventionally means "success"?
6. Which keyword ends an `if` block in Bash?
7. Which keyword ends a `for` or `while` loop in Bash?
8. In `greet() { ... }`, what is `greet`?

### Level 2 — Understanding

1. Explain, in your own words, the difference between `bash script.sh` and `./script.sh`.
2. Explain why a shebang is not itself a Bash command.
3. Predict what `echo $name` will print if `name="AI Engineer"` and the value is used unquoted, and explain why.
4. Explain why a plain variable assignment inside a script is not automatically visible to a child process the script starts.
5. Explain why `if [ $var = "x" ]` can break when `var` is unset, and why quoting fixes it.
6. Explain, conceptually, what `$?` holds immediately after a command runs.
7. Explain why a script that never checks exit status can "finish" while having actually failed partway through.
8. Explain why a Bash script does not automatically run unchanged in PowerShell.

### Level 3 — Application

Perform each of these in your own disposable directory.

1. Create a script with a correct shebang that prints a simple greeting.
2. Run it two ways: `bash script.sh` and (after `chmod +x`) `./script.sh`.
3. Modify the script to accept and print an argument (`$1`).
4. Add a shell variable to the script and print it using correct double-quoting.
5. Add a simple `if`/`else` that checks whether the first argument equals a specific value.
6. Add a `for` loop that iterates over a small, safe set of files (e.g. `*.txt` in a disposable directory you control).
7. Add a function that takes one argument and prints a formatted message, then call it.
8. Combine a `grep`/`sort` pipeline (Lessons 04–06) with output redirection inside your script.

### Level 4 — Debugging

For each scenario, state the likely cause and the safe fix — explain your reasoning, don't just guess a command.

1. `./script.sh` fails with a permission error, but `bash script.sh` works fine. What's the fix?
2. A script prints an empty value for a variable you're sure you set. What are the two most likely causes to check first?
3. A script exports a variable, but a child process still doesn't see it. What ordering mistake might explain this?
4. `if [ $status = "ok" ]` produces a syntax error when `status` happens to be unset. What's the fix?
5. A `for file in *.log` loop inside a script processes more files than intended. What should you check before trusting the pattern?
6. A script "finishes" and prints a success message, but you later discover an early step actually failed. What's missing from the script?
7. A script that works when run from one directory fails with "No such file or directory" when run from another. What kind of path might be at fault?
8. A colleague tries to run your Bash script's syntax directly in PowerShell and it fails immediately. What's the actual cause?

### Level 5 — Integration

These combine shell scripting with earlier Module 0.3 skills (navigation, file operations, viewing, searching, text processing, pipes/redirection, environment variables). Perform each in your own disposable directory.

1. Write a script that navigates conceptually (documents, in a comment, what directory it expects to be run from), validates that an expected input file exists (Lesson 04's `find`), and reports a clear error if not.
2. Write a script that reads a configuration value from an exported environment variable (Lesson 07) and uses it inside a conditional to choose between two different `grep` patterns.
3. Write a script that processes a small sample file with a `sort | uniq -c` pipeline (Lesson 05, via Lesson 06's pipe) and redirects the result to an output file, then reports the exit status of that step.
4. Write a script containing a function that wraps a `cp` (Lesson 02) operation with basic validation (does the source file exist first?), and call that function from a loop over several sample files.
5. Deliberately introduce and then fix one "works locally, fails elsewhere" mistake (Section 21, mistake 19; Section 22, Scenario 12) in a script you've written for this exercise set, explaining the fix in your own words.

---

## 29. Review

**Shell vs. shell script:** a shell is the interactive program that reads and runs commands you type; a shell script is a saved file of such commands, run as a unit.

**Script execution:** `bash script.sh` (explicit interpreter, no permission needed) vs. `./script.sh` (direct execution via the shebang, requires executable permission).

**Shebang:** the first line (`#!/usr/bin/env bash`) telling the system which interpreter should run the file directly — not a Bash command itself.

**Variables:** `name=value` (shell variable, script-local) vs. `export name=value` (environment variable, inherited by child processes) — the exact Lesson 07 distinction, now applied inside scripts.

**Arguments:** `$0` (script name), `$1`/`$2`/... (positional arguments), `$#` (count), `"$@"` (all arguments, safely quoted).

**Quoting:** `"$var"` (safe default) vs. `$var` (risky, subject to word-splitting) vs. `'$var'` (no expansion at all).

**Exit status:** `$?` — `0` generally means success, non-zero generally means some failure, but not all non-zero codes mean the same thing.

**Conditions:** `if [ condition ]; then ... else ... fi`, and testing a command's own success directly.

**Loops:** `for item in list; do ... done` and `while [ condition ]; do ... done`.

**Functions:** `name() { ... }` — grouping reusable commands, with their own `$1`/`$2` parameters.

**Pipes/redirection in scripts:** identical to Lesson 06, simply placed inside a file.

**Debugging:** a systematic process — check exit status, check quoting, check variable names/export status, check current working directory, check wildcard matches — rather than guesswork.

**Safe automation:** disposable testing, quoting by default, validating inputs, avoiding hard-coded paths, never exposing secrets.

**Bash vs. PowerShell:** genuinely different shells with different syntax; scripts do not translate automatically between them.

**Appropriate use cases:** short, well-understood command sequences and CLI/filesystem orchestration — not complex application logic, complex data structures, or large maintainable applications.

### Final self-assessment checklist

You should be able to answer **yes** to each of these, based on actual capability, not just recognition:

- [ ] I can write a script with a correct shebang and at least one comment.
- [ ] I can run the same script two different ways and correctly explain why one requires `chmod +x` and the other doesn't.
- [ ] I can write a script that reads and validates its own arguments.
- [ ] I can correctly distinguish, in a script I've written, which variables are script-local and which are exported.
- [ ] I can explain, and demonstrate, why quoting a variable matters.
- [ ] I can check and act on a command's exit status inside a script.
- [ ] I can write a working `if`/`else`, a working `for` loop, and a working function from scratch.
- [ ] I can combine a pipe, a redirection, and an environment variable inside one script.
- [ ] I can diagnose at least five of this lesson's common mistakes without looking them up.
- [ ] I can explain, in my own words, when I should reach for a shell script and when I shouldn't.

---

## 30. Interview Questions

1. **What is a shell script?** A plain text file containing a sequence of shell commands, saved so it can be run as a repeatable unit instead of retyped manually.
2. **What is a shebang?** The first line of a script (e.g. `#!/usr/bin/env bash`), which tells the system which interpreter should read and run the rest of the file when it's executed directly.
3. **Why use `#!/usr/bin/env bash`?** It locates Bash via the system's `PATH`, wherever it happens to be installed, making the script more portable than hard-coding a specific path like `#!/bin/bash`.
4. **What's the difference between `bash script.sh` and `./script.sh`?** `bash script.sh` explicitly tells Bash to read and run the file's contents, and needs no special file permission; `./script.sh` runs the file directly as a program, relying on its shebang and requiring executable permission on the file.
5. **What is `$0`?** The script's own name, as it was invoked.
6. **What are `$1`, `$2`, and `$@`?** `$1`/`$2` are the first/second positional arguments; `$@` represents all arguments — best used quoted (`"$@"`) to keep each one intact even if it contains spaces.
7. **What is an exit status?** A small numeric signal a command (or script) reports when it finishes, indicating success or failure, separate from anything it printed.
8. **What does exit status 0 mean?** Conventionally, success — though not every program uses the same convention for what a specific non-zero value means beyond "not success."
9. **What's the difference between a shell variable and an environment variable?** A shell variable exists only in the current shell/script; an environment variable (created via `export`) is additionally passed to child processes started afterward.
10. **Why quote variables?** To prevent unintended word-splitting on spaces (or other special characters) inside a value, which can otherwise cause a script to misinterpret one value as multiple separate items.
11. **Why might a script work manually but fail in automation?** Automation often runs from a different current working directory, with a different (or empty) environment, and no human present to notice or correct an unexpected prompt or assumption — exposing hard-coded paths, missing exports, or unvalidated inputs that a manual run happened not to trigger.
12. **When should you use shell scripting instead of Python?** For short, well-understood command-line sequences and filesystem/CLI orchestration; once real data structures, complex error handling, or substantial application logic are involved, a real programming language like Python is the more appropriate tool.

---

## 31. Architecture / Engineering Questions

1. **When should an AI engineering workflow use a shell script?** When the task is a short, well-understood sequence of existing command-line steps — orchestrating other tools, preparing a workspace, or gluing together already-built pieces — rather than implementing genuine application logic.
2. **When should shell scripting be replaced by Python?** Once the workflow needs real data structures, nuanced error handling for many distinct failure modes, or logic complex enough that a plain sequence of commands can no longer represent it clearly and maintainably.
3. **How can shell scripts become a reliability risk?** By silently continuing past a failed step (Section 21, mistakes 12–13), by relying on unstated, machine-specific assumptions (Section 21, mistake 19), or by mishandling inputs (unquoted variables, unchecked wildcards) in ways that behave unpredictably depending on the exact data encountered.
4. **How should configuration be passed into a shell script?** Through validated arguments and/or environment variables (Section 15) — with required configuration explicitly checked at the start, rather than assumed — rather than hard-coded directly into the script's own text.
5. **How would you design a safe script for a model-evaluation workflow?** Validate that required inputs (data files, configuration) actually exist before starting; use environment variables for anything that should vary between environments; check the exit status of each meaningful step (data preparation, the evaluation run itself, result collection) before proceeding to the next; report a clear final success/failure signal; test it against normal, invalid, and missing-input cases (Section 26) before trusting it with real work.
6. **How would you make a shell-based automation workflow reproducible?** Avoid hard-coded, machine-specific assumptions; make required inputs and configuration explicit and validated; keep the script's steps in one place rather than scattered manual steps; and test it, deliberately, against more than just the one "happy path" case it was first written for.

---

## 32. Production Application

This lesson's skills appear in production contexts as:

- **Developer tooling** — setup/teardown scripts that make a development environment consistent across a team.
- **Build workflows** — a script encoding the correct build sequence.
- **Test automation** — a script running the correct test invocation consistently.
- **Deployment glue** — scripts that arrange files/steps around an actual deployment mechanism (which this lesson does not teach).
- **Batch processing** — a script applying the same processing step across many inputs.
- **Data preparation** — the same filter/sort/organize pattern from Section 19, run identically each time.
- **Model workflows** — orchestrating prepare → train → save → evaluate as one reliable sequence.
- **Evaluation workflows** — running a fixed evaluation procedure consistently.
- **Operational tooling** — routine checks or maintenance tasks, run the same way every time.
- **Service startup** — scripts that prepare configuration and start local or remote processes consistently.
- **Artifact management** — gathering, organizing, or archiving generated outputs.

**What production shell scripts should be:**

- **Predictable** — the same inputs produce the same result, every time.
- **Observable** — you can tell, from output or logs, what the script actually did and whether it succeeded.
- **Safe** — no destructive surprises, no exposed secrets.
- **Documented** — expected inputs and assumptions are stated clearly (Section 25).
- **Tested** — tried against more than just the ideal case (Section 26).
- **Environment-aware** — behaves correctly across the environments it's actually meant to run in, without hidden machine-specific assumptions.
- **Appropriately scoped** — kept to the kind of task shell scripting is actually good at (Section 20), rather than expanded into something better suited to a real programming language.

**Connecting to the roadmap's production engineering spine:**

```text
Requirements
→ Design
→ Implementation
→ Testing
→ Validation
→ Logging/Observability
→ Security
→ Performance
→ Cost
→ Deployment
→ Reliability
→ Architecture Review
```

Everything in this lesson maps onto the early stages of that spine — a shell script is, itself, a small **implementation**, which still benefits from being **designed** deliberately (Section 27's mini-project structure), **tested** (Section 26), and reviewed for **security** (Section 15, Section 21's secret-exposure mistake) before being trusted. This lesson does not teach CI/CD, Docker, Kubernetes, cloud infrastructure, or advanced deployment systems — those are separate, later parts of this same spine.

---

## 33. Applied AI Engineering Connection

```text
Shell commands
      ↓
Shell scripts
      ↓
Python automation
      ↓
Backend services
      ↓
Data pipelines
      ↓
ML pipelines
      ↓
LLM applications
      ↓
Agent workflows
      ↓
Production AI systems
```

**Shell scripting is not the final automation technology this roadmap will teach — it's the foundation.** Every later layer in the diagram above still, ultimately, involves running commands, checking whether they succeeded, passing configuration around, and orchestrating multiple pieces together — the exact concepts this lesson taught. A shell script is often the first, simplest tool that ties several already-built pieces together into one repeatable workflow; as your systems grow more sophisticated, some of that orchestration moves into Python, into dedicated pipeline tools, or into infrastructure systems not yet covered — but the underlying skill of thinking in terms of "sequence of steps, checked for success, configured through variables, run reliably" carries forward unchanged.

---

## 34. Relationship With Previous and Next Lessons

**Previous — `06-pipes-and-redirection.md`:** shell scripts can contain and compose the exact pipe/redirection workflows already learned there (Section 14) — nothing about pipes or redirection behaves differently inside a script.

**Previous — `07-environment-variables.md`:** scripts consume configuration through shell variables and inherited environment variables (Section 8, Section 15), following exactly the inheritance model already taught there — nothing new about environment variables themselves was introduced in this lesson.

**Next — `09-permissions.md`:** executing a script directly with `./script.sh` depends on executable permission (Section 6, Section 22's first scenario) — this lesson explained *that* this dependency exists and the minimal `chmod +x` step to satisfy it, but the full permissions model (what the permission bits actually mean, who can change them, and the broader read/write/execute system) is the dedicated subject of the next lesson. This lesson does not teach that material.

---

## 35. Scope Boundary

This lesson teaches only:

- what a shell script is, and why it exists
- the shebang, script anatomy, and comments
- creating and executing a script (`bash script.sh` and `./script.sh`), including the minimal, necessary connection to executable permission
- script arguments (`$0`, `$1`, `$#`, `$@`)
- variables in scripts, and their connection to Lesson 07's shell-variable/environment-variable distinction
- quoting
- exit status (`$?`)
- basic `if`/`then`/`else`/`fi` conditionals
- basic `for` and `while` loops
- basic functions
- combining pipes/redirection/environment variables (from Lessons 06–07) inside scripts
- basic testing and debugging of shell scripts
- safe, disposable practical demonstration and a mini-project

This lesson deliberately does **not** deeply teach:

- advanced Bash programming
- advanced shell parameter expansion
- advanced regular expressions
- complex process substitution
- advanced traps
- advanced signal handling
- advanced job control
- advanced shell internals
- Bash completion
- shell plugin systems
- `.bashrc` customization in depth
- `.bash_profile` / startup-file administration
- PowerShell scripting
- Windows batch scripting
- Python scripting
- Makefiles
- CI/CD systems
- Docker
- Kubernetes
- cloud deployment
- infrastructure-as-code
- secrets managers
- advanced security
- production orchestration platforms

These are separate roadmap topics and stages, mentioned in this lesson only where necessary for context. This lesson is not a preview course for any of them.

---

_This lesson is complete. It covers shell scripts — shebang, execution, arguments, variables, quoting, exit status, conditionals, loops, and functions — only. The remaining Module 0.3 topics are covered in subsequent lessons within this module._
