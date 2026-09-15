# Module 0.3 — Command Line

## Lesson 12 — Shell Quoting and Standard Streams

**Module:** Command Line
**Roadmap reference:** Stage 0 — Computer, Linux, and Developer Foundations, Gap 0B — "Safe
terminal habits and filesystem literacy" (extends Module 0.3 — Command Line, and Concept 06 —
Pipes and Redirection)
**Concept(s) covered:** shell quoting (single vs. double quotes), PowerShell quoting basics,
`stdin`, `stdout`, `stderr`, redirection (`>`, `>>`, `2>`), pipes (`|`), diagnosing quoting and
redirection mistakes
**Status:** Not Started
**Builds on:** 01-navigation.md, 02-file-operations.md, 03-viewing-files.md,
06-pipes-and-redirection.md, 11-safe-terminal-and-filesystem-literacy.md, and Module 0.2 (standard
input/output, pipes, shell)

---

### Learning Outcomes

By the end of this lesson you will be able to:

- Explain why a path or argument containing spaces or special characters needs quoting, and quote
  it correctly.
- Explain the difference between single and double quotes in Bash, and choose the right one
  deliberately.
- Recognize the equivalent quoting concern in PowerShell.
- Explain `stdin`, `stdout`, and `stderr`, and why keeping them separate is useful.
- Use `>`, `>>`, and `2>` correctly and explain the difference between each.
- Use `|` to pass one command's output directly into another command.
- Read a real log-style text file using redirection and pipes, correctly separating results from
  errors.
- Diagnose the most common quoting and redirection mistakes from their symptoms alone.

### Prerequisites

- **01-navigation.md, 02-file-operations.md, 03-viewing-files.md** — basic navigation, file
  operations, and viewing files.
- **06-pipes-and-redirection.md** — this lesson assumes you've met `|`, `>`, `>>`, and basic
  redirection there; here, the focus shifts to quoting safety and to using streams specifically for
  investigation, not to re-teaching redirection from zero.
- **11-safe-terminal-and-filesystem-literacy.md** — working inside a dedicated practice directory,
  and confirming your current directory before running commands.
- **Module 0.2** —
  [Standard Input/Output](../02-Operating-System-Fundamentals/11-standard-input-output.md) and
  [Pipes](../02-Operating-System-Fundamentals/12-pipes.md), for the conceptual model this lesson
  turns into everyday practice.

### Key Terms

- **Quoting** — wrapping an argument in quote characters so the shell treats it as one single
  piece of text, spaces and all, instead of splitting it into multiple arguments.
- **Single quotes (`'...'`)** — in Bash, treat everything inside literally; no variable expansion,
  no special-character interpretation.
- **Double quotes (`"..."`)** — in Bash, treat most things literally but still expand variables
  (`$VAR`) and a few special sequences inside them.
- **`stdin` (standard input)** — the default input stream a program reads from, usually your
  keyboard unless redirected.
- **`stdout` (standard output)** — the default stream a program writes its normal results to,
  usually your terminal.
- **`stderr` (standard error)** — a *separate* stream a program writes error messages to, also
  shown in your terminal by default, but redirectable independently of `stdout`.
- **Redirection** — sending a stream to or from a file instead of the terminal, using `>`, `>>`, or
  `2>`.
- **`>`** — redirect `stdout` to a file, overwriting the file's previous contents.
- **`>>`** — redirect `stdout` to a file, appending to any existing contents instead of overwriting.
- **`2>`** — redirect `stderr` specifically (file descriptor 2) to a file.
- **Pipe (`|`)** — connects one command's `stdout` directly to the next command's `stdin`, without
  any file in between.

---

### 1. Why Quoting and Streams Matter Together

This lesson pairs two ideas that, at first glance, look unrelated: how the shell splits up what you
type (quoting), and how a program's output and errors flow (streams). They belong together because
both are about **precision** — making sure the shell does exactly what you intended, not something
that merely looks similar. A missing quote can make a command touch the wrong file; a misread stream
can make you believe a command failed silently when it actually reported the error clearly, just
somewhere you weren't looking.

### 2. Why Paths with Spaces or Special Characters Need Quoting

The shell normally splits what you type into separate arguments at each space. This is usually
exactly what you want — `cp a.txt b.txt` clearly means "copy `a.txt` to `b.txt`." But it becomes a
problem the moment a single argument, like a filename, legitimately contains a space:

```bash
ls My Documents
```

Without quoting, the shell treats this as **two separate arguments**, `My` and `Documents` — `ls`
tries to list two things named `My` and `Documents`, neither of which exists, instead of one folder
named `My Documents`.

```bash
ls "My Documents"
```

Quoting tells the shell: treat everything inside the quotes as **one single argument**, spaces
included. The same problem, and the same fix, applies to other characters the shell treats
specially — parentheses, ampersands, dollar signs, and more — all of which you'll increasingly
encounter as folder and file names grow more realistic (a project folder like `AI Engineering`, for
instance, needs exactly this kind of quoting).

### 3. Single Quotes vs. Double Quotes in Bash

Bash gives you two kinds of quotes, and they behave differently — choosing the wrong one is a common
source of confusing results.

**Single quotes (`'...'`)** — everything inside is completely literal. No variable expansion, no
special interpretation of anything:

```bash
echo 'Home is $HOME'
```

```text
Home is $HOME
```

**Double quotes (`"..."`)** — spaces and most special characters are still protected, but variables
(`$VAR`) are still expanded:

```bash
echo "Home is $HOME"
```

```text
Home is /home/you
```

**The practical rule:** use double quotes by default when you want spaces protected but still need
a variable's value substituted in (very common — e.g. `cd "$PROJECT_DIR/data"`); use single quotes
specifically when you want the text preserved exactly as typed, with no substitution at all (for
example, when the literal text `$5` or `$HOME` needs to stay as-is).

### 4. PowerShell Quoting, Briefly

PowerShell follows a similar split, worth recognizing even if you work mostly in Bash:

- **Single quotes (`'...'`)** — literal, no variable expansion, similar to Bash.
- **Double quotes (`"..."`)** — variables (`$var`) are expanded inside them, similar to Bash.

```powershell
$name = "world"
Write-Output 'Hello $name'    # prints literally: Hello $name
Write-Output "Hello $name"    # prints: Hello world
```

The underlying idea — single quotes protect literally, double quotes still allow variable
substitution — carries over directly from Bash, even though the two shells are otherwise quite
different.

### 5. Standard Input, Output, and Error (`stdin`, `stdout`, `stderr`)

Every command-line program is connected, by default, to three **streams** — covered conceptually in
Module 0.2's [Standard Input/Output](../02-Operating-System-Fundamentals/11-standard-input-output.md)
lesson. Here's the practical version:

- **`stdin`** — where a program reads input from, if it reads any at all; by default, your keyboard.
- **`stdout`** — where a program writes its normal, expected results; by default, your terminal.
- **`stderr`** — a *separate* stream where a program writes error and diagnostic messages; also
  shown in your terminal by default, but critically, **not the same stream as `stdout`**.

**Why keeping them separate matters:** because `stdout` and `stderr` are different streams, you can
redirect one without touching the other — saving a command's real results to a file while still
seeing errors on your screen, or the reverse. This is the single most useful property of the whole
system, used constantly in Section 6 and in real debugging.

### 6. Redirection: `>`, `>>`, and `2>`

```bash
echo "hello" > output.txt
```

`>` sends `stdout` to a file, **overwriting** the file's previous contents entirely — use it
carefully, since it silently discards whatever was there before.

```bash
echo "another line" >> output.txt
```

`>>` sends `stdout` to a file too, but **appends** to the end instead of overwriting — safe to run
repeatedly without losing earlier content.

```bash
ls nonexistent-folder 2> errors.txt
```

`2>` redirects **only `stderr`** (file descriptor `2`) to a file — `stdout` from the same command
(if any) still goes to your terminal, unaffected. This lets you separate "what the command actually
produced" from "what went wrong" into two different files, which is exactly what a real
investigation needs.

You can combine both:

```bash
some_command > results.txt 2> errors.txt
```

Now normal output goes to `results.txt`, and only errors go to `errors.txt` — nothing is mixed
together, and nothing is silently lost.

### 7. Pipes: `|`

A **pipe** connects one command's `stdout` directly to the next command's `stdin` — no file is
created in between at all:

```bash
cat access.log | grep ERROR
```

This runs `cat access.log`, and instead of printing its output to the terminal, sends it straight
into `grep ERROR`, which filters for lines containing `ERROR`. You can chain several commands this
way, each one processing the previous command's output — you'll do exactly this in this module's
Project 0.2.

### 8. Practical Examples in a Dedicated Practice Directory

```bash
mkdir -p ~/practice-shell/quoting-and-streams
cd ~/practice-shell/quoting-and-streams
pwd
```

Create two small text files to practice on:

```bash
printf "INFO starting up\nWARN low disk space\nERROR failed to connect\n" > sample.log
printf "line one\nline two\n" > "notes with spaces.txt"
```

Now practice quoting:

```bash
cat notes with spaces.txt        # fails — two arguments, neither exists
cat "notes with spaces.txt"      # works — one argument, quoted correctly
```

Practice streams and redirection:

```bash
grep ERROR sample.log > errors-only.txt
cat errors-only.txt
```

```text
ERROR failed to connect
```

Practice a deliberate error, to see `stderr` in action:

```bash
cat does-not-exist.txt 2> missing-file-error.txt
cat missing-file-error.txt
```

```text
cat: does-not-exist.txt: No such file or directory
```

Practice a pipe:

```bash
cat sample.log | grep -c ERROR
```

```text
1
```

`grep -c` counts matching lines instead of printing them — a small preview of the counting technique
this module's Project 0.2 builds on directly.

### 9. Why Streams and Redirection Matter for Investigating Logs and AI-Service Failures

- **Separating `stdout` and `stderr`** is exactly how you avoid missing a real error buried among
  normal log lines, or conversely, avoid mistaking a normal status message for an error — the two
  streams exist specifically so tools (and you) can tell them apart automatically instead of by
  eye.
- **Redirecting a service's output to a file** (`>`/`>>`) is the simplest form of logging — before
  any dedicated logging framework is involved, this is literally how a running program's history
  gets captured for later investigation.
- **Piping a log through `grep`, `sort`, and `uniq -c`** (this module's Project 0.2) is the
  first-line technique for answering "how many errors happened" and "what's the most common
  failure" — before reaching for any specialized log-analysis tool.
- **Quoting failures are a common, avoidable cause of scripts breaking** on real project paths — a
  path like `AI Engineering/Computer & Digital Foundation` (this very repository) requires exactly
  the quoting discipline this lesson teaches; an unquoted script that works on a no-spaces test
  path can fail unpredictably on a real one.
- **When an AI service crashes or misbehaves**, the very first useful evidence is almost always
  captured through exactly this mechanism: redirected output, separated error streams, and a piped
  filter to find the one relevant line in a large log — the same small toolkit this lesson teaches,
  used at production scale.

### 10. Common Quoting and Redirection Mistakes

| Symptom | Likely cause | Safe next step |
|---|---|---|
| A command reports "No such file or directory" for a path you can see exists | The path contains a space and wasn't quoted, so the shell split it into multiple arguments | Quote the whole path with double quotes, e.g. `cd "AI Engineering"`. |
| A variable prints literally as `$VAR` instead of its value | Single quotes were used where double quotes were needed | Switch to double quotes if you want the variable's value substituted (Section 3). |
| A file you redirected into is now empty when you expected it to grow | `>` was used instead of `>>`, overwriting previous contents | Use `>>` to append, and reserve `>` for when you deliberately want to start fresh (Section 6). |
| An error message appears on screen even though you redirected the command's output to a file | Only `stdout` (`>`) was redirected; `stderr` went to the terminal as normal, since it's a separate stream | Add `2>` to send errors to their own file too, if you want them captured (Section 6). |
| A pipe seems to "do nothing" | The first command in the pipe produced no output at all (check it alone, without the pipe, first) | Run the first command by itself to confirm it actually produces output before adding a `\|` to filter it. |

### 11. Exercises

1. Create a file with a space in its name inside your practice directory. Try `cat` on it
   unquoted, observe the failure, then correctly quote it.
2. Set a variable (`MY_NAME=you` in Bash) and `echo` it inside single quotes, then inside double
   quotes. Write down, before running each, what you expect to see.
3. Redirect a command's output to a file with `>` twice in a row, using different text each time.
   Confirm the file only contains the second output, not both.
4. Repeat exercise 3 using `>>` instead, and confirm the file now contains both outputs, in order.
5. Deliberately run a command against a file that doesn't exist, redirecting only `stderr` with
   `2>` to a file. Confirm your terminal shows nothing (the error went to the file), and the file
   contains the exact error text.
6. Chain at least two commands with a pipe (for example, `cat` into `grep`) against the sample log
   from Section 8, and explain in one sentence what data is flowing between the two commands.

### 12. Expected Results

- **Exercise 1:** the unquoted attempt fails with a "not found"-style error naming pieces of the
  filename separately; the quoted version succeeds.
- **Exercise 2:** the single-quoted `echo` prints the variable name literally (e.g. `$MY_NAME`); the
  double-quoted one prints its actual value.
- **Exercise 3:** the file contains only the second write — confirming `>` overwrites.
- **Exercise 4:** the file contains both writes, in order — confirming `>>` appends.
- **Exercise 5:** the terminal shows no output from the failing command itself; the redirected file
  contains the exact error text that would otherwise have appeared on screen.
- **Exercise 6:** your explanation correctly describes the first command's `stdout` becoming the
  second command's `stdin`, matching Section 7.

---

### Summary

Quoting and streams are both about telling the shell precisely what you mean. Quote any argument
containing spaces or special characters — double quotes when you still want variables expanded,
single quotes when you want the text preserved exactly as typed. Every command has three streams:
`stdin` for input, `stdout` for normal output, and `stderr` for errors — kept separate specifically
so you can redirect one without disturbing the other, using `>` (overwrite), `>>` (append), and
`2>` (errors only). Pipes (`|`) connect one command's output directly into the next command's
input, with no file in between. Together, these are the exact tools used to turn a raw log file
into a specific, evidence-backed answer — the skill this module's Project 0.2 puts into practice.

### Completion Checklist

- [ ] I can explain why an unquoted path with a space breaks a command, and quote it correctly.
- [ ] I can explain the difference between single and double quotes in Bash, with a working example
      of each.
- [ ] I can explain `stdin`, `stdout`, and `stderr` as three separate streams, in my own words.
- [ ] I used `>` and `>>` and can explain, from direct observation, the difference between them.
- [ ] I used `2>` to capture an error separately from normal output, and confirmed it worked.
- [ ] I chained at least two commands with a pipe and explained what data flowed between them.
- [ ] I completed Section 11's exercises and my results match Section 12's expected results.
- [ ] I can diagnose at least three of Section 10's common mistakes from their symptoms alone.

---

_This lesson is complete. It extends `06-pipes-and-redirection.md` with a focus on quoting safety
and on streams as an investigation tool, drawn from Stage 0 Gap 0B. These same skills — filtering,
counting, and redirecting log output — are practiced end to end in
[`Projects/01-shell-file-and-stream-investigation.md`](./Projects/01-shell-file-and-stream-investigation.md)._
