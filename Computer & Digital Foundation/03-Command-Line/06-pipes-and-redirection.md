# Module 0.3 — Command Line

## Lesson 06 — Pipes and Redirection

**Module:** Command Line
**Roadmap reference:** Stage 0 — Module 0.3 — Command Line
**Concept(s) covered:** pipes (`|`), redirection (`>`, `>>`, `<`, `2>`, `2>>`, `2>&1`, `&>`)
**Status:** Complete
**Builds on:** 01-navigation.md, 02-file-operations.md, 03-viewing-files.md, 04-searching.md, 05-text-processing.md, and Module 0.2 (processes, file descriptors, standard input/output, shell)

---

## 1. Learning Objectives

After completing this lesson you will be able to:

- Explain what a pipe is, in simple language.
- Explain what redirection is, in simple language.
- Distinguish **stdin**, **stdout**, and **stderr**.
- Understand file descriptors **0**, **1**, and **2** conceptually.
- Use `|` to connect two commands.
- Build simple multi-command pipelines.
- Use `>` to redirect stdout, and understand that it overwrites.
- Use `>>` to append stdout instead of overwriting it.
- Use `<` to provide stdin from a file.
- Use `2>` and `2>>` for stderr.
- Understand `2>&1` conceptually.
- Distinguish overwrite from append.
- Predict where a command's output will actually go, before running it.
- Reason about pipeline data flow, one stage at a time.
- Identify common pipeline/redirection mistakes.
- Debug simple pipeline and redirection failures.
- Use these techniques safely, without accidentally destroying data.
- Explain why these concepts matter in software engineering and Applied AI Engineering.

---

## 2. Prerequisites / Connection to Previous Lessons

You already have five Module 0.3 lessons behind you:

- **01-navigation.md** — knowing *where you are* in the filesystem.
- **02-file-operations.md** — creating, copying, moving, and deleting files.
- **03-viewing-files.md** — reading a file's contents (`cat`, `less`, `head`, `tail`).
- **04-searching.md** — locating content and files (`grep`, `find`).
- **05-text-processing.md** — transforming and organizing text (`sort`, `uniq`, `cut`, `xargs`).

Every one of those lessons taught you a command that, on its own, does one specific job. This lesson does not teach a new job — it teaches how to **connect** the jobs you already know, and how to **control where their output goes**. Nothing here re-teaches `grep`, `sort`, or any other earlier command in depth; they're used only as familiar building blocks.

This lesson also leans on Module 0.2, which already introduced **processes**, **file descriptors**, **standard input/output**, **pipes**, and the **shell** at a conceptual level. This lesson reconnects those ideas to actual, typed commands — it does not re-teach them from scratch.

---

## 3. What Are Pipes and Redirection?

Every command you've run so far has read from *somewhere* and written to *somewhere* — usually, by default, your keyboard and your terminal screen. **Pipes** and **redirection** are two different ways of changing that default:

- A **pipe** connects one command's output directly to a second command's input — no file involved, no typing required in between.
- **Redirection** changes where a command's input comes from, or where its output goes — usually a file, instead of the keyboard or the screen.

The core distinction, stated plainly, which the rest of this lesson builds on:

```text
PIPE:
  stdout of one command  →  stdin of another command

REDIRECTION:
  stdin/stdout/stderr  ↔  a file (or similar destination)
```

Both let you build on top of the individual commands you already know, rather than replacing anything about them.

---

## 4. Why Do They Exist?

Without pipes, if you wanted to search (`grep`) the *result* of another command, you'd have to first save that result to a file, then run `grep` on the file, then clean up the file afterward — for every single step of every investigation. Pipes exist so that one command's output can flow directly into the next command, instantly, with no file ever needing to be created just to pass data along.

Without redirection, every command's output would only ever appear on your screen, and every command needing input would only ever read from your keyboard. Redirection exists so you can capture a command's output permanently (into a file, for later review), or feed a command a file's contents as if you'd typed them, without manually retyping anything.

Together, they're the foundation of a core Unix/Linux design idea: build small, focused tools (like the ones from Lessons 03–05), and let them be **composed** — connected together — to do larger jobs neither tool could do alone.

---

## 5. The Command-Line Data Flow Mental Model

Before any syntax, build this mental model. Every command you run is a small process that can receive input, do some work, and produce output:

```text
INPUT
  ↓
stdin
  ↓
PROCESSING (the command does its job)
  ↓
stdout   (normal output)
stderr   (error/diagnostic output)
```

**Redirection** changes where that input comes from, or where stdout/stderr go:

```text
file  →  stdin  →  PROCESSING  →  stdout  →  file
                                → stderr  →  file
```

**A pipe** connects two of these little diagrams together — command A's stdout becomes command B's stdin directly:

```text
command A stdout
        ↓
       pipe
        ↓
command B stdin
```

Everything in this lesson is a variation on these three small diagrams. Keep returning to them whenever a specific example feels confusing.

---

## 6. Standard Input, Standard Output, and Standard Error

Recall from Module 0.2: every running program (process) has default channels for receiving and sending text. This lesson uses three of them constantly:

- **stdin** ("standard input") — where a command reads its input from, by default your keyboard.
- **stdout** ("standard output") — where a command writes its *normal* results, by default your terminal screen.
- **stderr** ("standard error") — where a command writes *error or diagnostic* messages, also by default your terminal screen.

### Why stdout and stderr are separate

On your screen, stdout and stderr look identical — both just appear as text in your terminal. But they are **two distinct channels**, and the distinction matters the moment you start redirecting or piping:

```text
command
  ├── stdout → normal output
  └── stderr → error/diagnostic output
```

If a command's normal results and its error messages both went to the same single channel, you'd have no reliable way to separate "the data I actually wanted" from "a warning about what went wrong" once you started saving or piping that output. Keeping them separate means you can, for example, save only the real results to a file while still seeing errors on screen — or the reverse.

**Important accuracy note:** not every message a command prints is automatically stderr, and not everything "expected" is automatically stdout. Which channel a given message goes to is a *design decision made by whoever wrote that program* — well-behaved programs send normal results to stdout and diagnostic/error messages to stderr, but this is a convention, not a law of physics. When in doubt about which channel a specific message uses, the redirection techniques in this lesson (Section 15 onward) let you test it directly, rather than guessing.

---

## 7. File Descriptors 0, 1, and 2

Module 0.2 introduced the concept of a **file descriptor** — a small number a process uses internally to refer to an open input/output channel. Three of these numbers are standardized by convention across Unix/Linux systems, and you'll use them by number throughout this lesson's redirection syntax:

| Number | Name | Default destination |
|---|---|---|
| `0` | stdin | Your keyboard |
| `1` | stdout | Your terminal screen |
| `2` | stderr | Your terminal screen |

This is why `2>` (Section 15) means "redirect file descriptor 2" — stderr — and why plain `>` (Section 12), with no number in front, defaults to redirecting file descriptor 1 — stdout. You don't need to understand file descriptors beyond this: they're simply the numeric names the shell's redirection syntax uses to refer to these three channels.

---

## 8. Pipes

A pipe, written `|`, connects one command's stdout directly to another command's stdin.

```bash
command1 | command2
```

What this means:

- `command1` runs and produces output on its stdout.
- The shell connects that stdout directly to `command2`'s stdin — no file is created or involved.
- `command2` reads that data as if it had been typed at its stdin.
- **`command1` and `command2` are separate processes**, running (conceptually) around the same time, with the pipe acting as the communication channel between them.

This last point matters: a pipe is not "one command with a weird syntax" — it's two independent programs, each doing its own job, connected by the shell.

---

## 9. How a Pipe Works Internally

Conceptually, when the shell sees `command1 | command2`:

1. The shell recognizes the `|` and understands this is a pipeline, not two separate commands.
2. The shell sets up a pipe — a communication channel the operating system provides (introduced conceptually in Module 0.2).
3. The shell starts `command1` as a process, with its stdout connected to the writing end of that pipe instead of the terminal.
4. The shell starts `command2` as a process, with its stdin connected to the reading end of the same pipe instead of the keyboard.
5. As `command1` produces output, it flows through the pipe; `command2` reads it as its input, processes it, and produces its own output (to its own stdout, which — unless further redirected — still goes to your terminal).
6. Both processes run, each doing its own job, until they finish.

This lesson does not go deeper than this — no kernel-level buffering details, no system-call-by-system-call walkthrough. The concept to hold onto: **a pipe connects two processes' streams, not two files, and not one single combined program.**

---

## 10. Basic Pipe Examples

Using commands you already know from earlier lessons:

```bash
cat file.txt | grep "error"
```

`cat` reads `file.txt` and writes its entire contents to stdout; `grep` reads that as its stdin and filters for lines containing `"error"`.

**Worth noticing immediately:** this particular pipeline is more complicated than necessary. `grep` (Lesson 04) can read a file directly:

```bash
grep "error" file.txt
```

This produces the same result, with one fewer process involved. This lesson will point this out again — learning *when a pipeline is unnecessary* is as important as learning how to build one (Section 20 returns to this).

A case where a pipe is genuinely useful — connecting two commands, neither of which can do the other's job:

```bash
grep "error" file.txt | sort
```

`grep` filters `file.txt` down to only lines containing `"error"`; `sort` (Lesson 05) then reorders just those matching lines. Neither command alone could do both jobs.

---

## 11. Multi-Stage Pipelines

You can chain more than two commands together:

```bash
command1 | command2 | command3
```

Data flows through each stage in order:

```text
input
 ↓
command A
 ↓
stdout
 ↓
pipe
 ↓
command B
 ↓
stdout
 ↓
pipe
 ↓
command C
 ↓
stdout (to your terminal, unless further redirected)
```

Each stage has its **own** stdin and stdout — command B doesn't "know" it's in the middle of a pipeline; it simply reads whatever arrives on its stdin and writes to its stdout, exactly as it would if run alone.

Example, building on Lesson 05's `sort`/`uniq` discussion:

```bash
grep "error" file.txt | sort | uniq
```

Step by step:
1. `grep "error" file.txt` — filters `file.txt` down to lines containing `"error"`.
2. `sort` — reorders those matching lines, grouping identical ones together (recall from Lesson 05 why this matters).
3. `uniq` — collapses the now-adjacent duplicate lines, leaving only distinct error messages.

**Practice predicting these by hand.** Before running any multi-stage pipeline, try to state what each stage will receive and produce — this is the single most useful habit this lesson can build.

---

## 12. Redirection

Redirection changes where a command's stdin, stdout, or stderr connects — typically to a file instead of the keyboard/screen.

```text
PIPE:
stdout of one command → stdin of another command

REDIRECTION:
stdin/stdout/stderr ↔ file or other destination
```

The operators this lesson covers:

| Operator | Meaning |
|---|---|
| `>` | Redirect stdout to a file, **overwriting** it |
| `>>` | Redirect stdout to a file, **appending** to it |
| `<` | Redirect stdin to come **from** a file |
| `2>` | Redirect stderr to a file, overwriting it |
| `2>>` | Redirect stderr to a file, appending to it |
| `2>&1` | Redirect stderr to wherever stdout is currently going |
| `&>` | Redirect **both** stdout and stderr to a file (Bash-specific; see Section 18) |

Each is explained individually below.

---

## 13. Output Redirection: `>`

```bash
command > file.txt
```

This means: **stdout is redirected to `file.txt`** instead of appearing on your screen.

- If `file.txt` doesn't exist, it is created.
- If `file.txt` already exists, **its previous contents are completely overwritten** — replaced entirely by the command's new output.

> **This overwrite behavior is worth emphasizing directly: `>` does not warn you, does not ask for confirmation, and does not preserve anything that was in the file before. If you redirect into a file that already held something important, that content is gone the instant the command runs.** This mirrors the exact same category of risk you learned about `cp`/`mv` overwriting a destination in Lesson 02 — redirection is simply another way the same kind of accidental data loss can happen.

Safe example:

```bash
printf "hello\n" > output.txt
```

`printf` here is used only as a small, predictable way to produce a line of text (the same minimal role it played in Lesson 05) — this lesson does not teach `printf` as a topic. After this runs, `output.txt` contains exactly `hello`, and nothing else — any prior content is gone.

---

## 14. Append Redirection: `>>`

```bash
command >> file.txt
```

This means: **stdout is added to the end of `file.txt`**, leaving whatever was already there untouched.

Compare directly:

```text
>   → overwrite (previous content destroyed)
>>  → append (previous content preserved, new content added after it)
```

Illustrative before/after:

```bash
printf "first line\n" > log.txt
printf "second line\n" >> log.txt
```

After both commands, `log.txt` contains **both** lines — the first `>` created the file with one line, and the second `>>` added a second line after it, rather than replacing the first.

**When append is appropriate:** whenever you want to accumulate output over time without losing what came before — for example, adding a new entry to a running record, rather than replacing it each time.

---

## 15. Input Redirection: `<`

```bash
command < input.txt
```

This means: **the command reads its stdin from `input.txt`**, instead of from your keyboard.

### `command < input.txt` vs. `command input.txt`

These are **not necessarily equivalent**, and this is a genuinely important distinction:

- `command input.txt` passes the filename as an **argument** — many commands (like `cat` or `grep`) are specifically written to accept a filename argument and open that file themselves.
- `command < input.txt` provides the file's contents **as stdin** — this works for any command that reads from stdin, including ones that have no concept of "take a filename argument" at all.

For a command like `cat`, both often produce the same visible result, but for different underlying reasons — `cat input.txt` opens the file itself; `cat < input.txt` never even "knows" a file was involved, and simply reads whatever arrives on its stdin. The distinction becomes important once you use a command that only knows how to read stdin, and has no filename-argument behavior of its own.

---

## 16. Error Redirection: `2>` and `2>>`

Recall from Section 7: file descriptor `2` is stderr.

```bash
command 2> errors.txt
```

This redirects **only stderr** to `errors.txt` (overwriting it) — stdout is completely unaffected and still goes to your screen, exactly as before.

```bash
command 2>> errors.txt
```

Same idea, but **appending** to `errors.txt` instead of overwriting it — the same overwrite-vs-append distinction from Sections 13–14, now applied specifically to stderr.

**Why stdout can still appear on screen while stderr is redirected:** because stdout and stderr are genuinely separate channels (Section 6), redirecting one has no effect on the other unless you redirect both. A command that produces some normal results and one error message, run as `command 2> errors.txt`, will still show its normal results directly on your screen — only the error message is diverted into the file.

---

## 17. Combining stdout and stderr

Sometimes you want **both** streams to end up in the same place. The syntax for this, `2>&1`, is one of the more conceptually tricky pieces of beginner Bash — read this section slowly.

```bash
command > output.txt 2>&1
```

Reading this left to right, as the shell actually processes it:

1. `> output.txt` — redirect stdout (file descriptor 1) to `output.txt`.
2. `2>&1` — redirect stderr (file descriptor 2) to **wherever file descriptor 1 is currently pointing** — which, because of step 1, is now `output.txt`.

The result: both stdout and stderr end up written into `output.txt`.

### Why order matters

```bash
command 2>&1 > output.txt
```

This looks similar, but the *order* changes the meaning entirely:

1. `2>&1` — redirect stderr to wherever stdout is **currently** pointing — at this point, that's still your terminal screen (nothing has redirected stdout yet).
2. `> output.txt` — *now* redirect stdout to `output.txt`.

The result here: stdout goes to `output.txt`, but stderr was already pointed at the terminal screen *before* stdout was redirected — so stderr continues going to the screen, not the file.

**The core lesson:** redirections are processed by the shell **in the order they're written, left to right**, and `2>&1` captures whatever file descriptor 1 points to *at that exact moment* — not wherever it might point to later. `command > output.txt 2>&1` (redirect stdout first, then point stderr at stdout) is the standard, correct pattern for capturing both streams together; reversing the order changes the result.

### `&>` — a Bash-specific shortcut

```bash
command &> all-output.txt
```

This is a shorthand, available in Bash specifically, meaning roughly "send both stdout and stderr to this file." **This is Bash-specific syntax** — it is not guaranteed to work identically (or at all) in every shell; portability differs. This lesson's primary, more universally understood pattern remains `command > file 2>&1`; `&>` is presented only as a Bash convenience you may encounter, not as the primary technique to rely on.

---

## 18. Pipes vs. Redirection

| | Pipe (`|`) | Redirection (`>`, `>>`, `<`, `2>`, etc.) |
|---|---|---|
| **Connects** | One command's stream to another command's stream | A command's stream to a file (or similar destination) |
| **Involves a file?** | No | Yes (typically) |
| **Number of processes involved** | Two or more | One (the command being redirected) |
| **Typical purpose** | Feed one command's output directly into another | Save output for later, or supply input from a saved file |

The two are frequently combined in the same command line — for example, `grep "error" file.txt | sort > errors.txt` uses a pipe to connect `grep` to `sort`, and redirection to save `sort`'s final result to a file. They are complementary tools, not alternatives to each other.

---

## 19. Pipeline Data Flow

Putting pipes and redirection together, walk through:

```bash
grep "error" app.log | sort > sorted-errors.txt
```

```text
app.log
   ↓ (read by grep)
grep "error"
   ↓ stdout (matching lines only)
   ↓ pipe
sort
   ↓ stdout (now sorted)
   ↓ redirection
sorted-errors.txt (file, on disk)
```

Nothing appears on your terminal screen here at all — every stage's output was either piped into the next stage, or, for the final stage, redirected into a file.

---

## 20. Shell Execution Model

This section connects everything above back to Module 0.2's process model. Conceptually, when the shell runs:

```bash
grep "error" app.log | sort > sorted-errors.txt
```

1. The shell **parses** the full command line.
2. The shell recognizes the `|` and understands this involves two connected commands.
3. The shell recognizes the `>` and understands the second command's stdout must be redirected to a file.
4. The shell **starts** `grep` as a process, and `sort` as a separate process (Module 2's process concept).
5. The shell connects `grep`'s stdout to the pipe.
6. The shell connects `sort`'s stdin to the same pipe (so it receives whatever `grep` writes).
7. The shell connects `sort`'s stdout to `sorted-errors.txt`, instead of the terminal.
8. Both processes actually execute — `grep` reading `app.log` and filtering; `sort` reading from the pipe and writing to the file.
9. The shell **waits for both processes to finish**, and tracks their completion status (Section 21).

This is the same shell/process/file-descriptor model introduced in Module 0.2 — this lesson has simply shown you the actual typed syntax that puts it to use. This lesson does not go beyond this conceptual level — no system-call-by-system-call trace, no kernel buffering internals.

---

## 21. Exit Status and Pipeline Failures

Recall from Lesson 04, Section 9: a command signals whether it succeeded or failed via its **exit status**, separately from whatever it printed.

**A pipeline is multiple independent commands, not one single magical command.** In `command1 | command2`, each command has its *own* exit status:

```bash
command1 | command2
```

Think of this as: "run `command1`. Also run `command2`. Connect their streams." Not: "run one combined thing called `command1 | command2`."

### Why this matters

By default, in most beginner-relevant scenarios, the exit status **you actually see reported** for a pipeline as a whole is the exit status of the **last** command in the pipeline. This means: if `command1` fails, but `command2` still runs and succeeds (perhaps producing no output, but not erroring), the pipeline can *look* successful even though something upstream actually went wrong.

### A more advanced Bash behavior — `pipefail` (introductory mention only)

Bash provides an option, `set -o pipefail`, which changes this default so that the *entire* pipeline is considered failed if **any** stage fails, not just the last one. This lesson mentions it only conceptually — to name the problem it solves ("a pipeline can silently succeed overall even when an earlier stage failed") — and does **not** teach how to write or use `set -o pipefail` in practice. That belongs to shell scripting, a later lesson (`08-shell-scripts.md`).

**What to actually take away at this stage:** don't assume a pipeline "worked correctly" just because it produced some output and didn't visibly crash — mentally check each stage, especially the earlier ones, when something seems off (Section 24 practices exactly this).

---

## 22. Common Mistakes

**1. Confusing `|` with `>`**
- A pipe connects two *commands*; redirection connects a command to a *file*. Writing `grep "x" file.txt > sort` (intending a pipe) sends output to a literal file named `sort`, not to the `sort` command.

**2. Forgetting that `>` overwrites**
- `command > existing-file.txt` silently destroys `existing-file.txt`'s previous contents — no warning, no confirmation (Section 13).

**3. Assuming `>>` overwrites**
- `>>` appends; only `>` overwrites. Confusing the two either loses data you meant to keep, or unexpectedly preserves old data you meant to replace.

**4. Forgetting that `uniq` only works on adjacent duplicates**
- Carried over directly from Lesson 05: piping unsorted data into `uniq` will miss non-adjacent duplicates. Sort first.

**5. Assuming stderr automatically goes through a pipe**
- `command1 | command2` connects `command1`'s **stdout only** to `command2`'s stdin. `command1`'s stderr is *not* piped — it still goes to your terminal screen by default, unless separately redirected.

**6. Confusing stdout with stderr**
- Assuming every visible message is stdout, or every "error-looking" message is stderr — as Section 6 explained, this depends on how the program was written, not on how a message looks to you.

**7. Misunderstanding `2>&1`**
- Treating it as "send stderr to a file called `1`" rather than "send stderr to wherever file descriptor 1 currently points" (Section 17).

**8. Getting redirection order wrong**
- `command 2>&1 > file.txt` does not behave the same as `command > file.txt 2>&1` — order matters, exactly as Section 17 demonstrated.

**9. Writing an unnecessarily complicated pipeline**
- Using `cat file.txt | grep "x"` when `grep "x" file.txt` alone would do — extra pipeline stages that don't add capability only add complexity (Section 10, Section 26).

**10. Assuming every shell behaves identically**
- Bash-specific syntax like `&>` may not exist or may behave differently elsewhere (Section 23).

**11. Forgetting that a pipeline contains multiple processes**
- Treating `command1 | command2` as one atomic unit rather than two independently running, independently failing processes (Section 21).

**12. Ignoring exit status**
- Assuming a pipeline "worked" just because something was printed, without considering whether an earlier stage actually failed (Section 21).

**13. Redirecting output to an unintended path**
- A typo in the destination filename, or forgetting which directory you're in (Lesson 01's `pwd` discipline), can send output somewhere unexpected — or worse, overwrite a file you didn't mean to touch.

**14. Using destructive commands while experimenting**
- Practicing redirection with real project files, or piping into commands like `rm` (echoing Lesson 05's `xargs` safety warning), turns a learning exercise into a real risk. Always use disposable files (Section 24).

**15. Assuming a command's input-file argument is identical to stdin redirection**
- As Section 15 explained, `command file.txt` and `command < file.txt` can behave differently depending on how the command itself is written — they are not automatically interchangeable.

---

## 23. Debugging Exercises

Work through each scenario's reasoning *before* reading the corrected command and lesson.

**Scenario 1 — Wrong pipe placement**
- *Broken command:* `grep "error" | app.log`
- *Expected intention:* Search `app.log` for lines containing `"error"`.
- *What is wrong:* The pipe is in the wrong place — `app.log` is being treated as a separate command name, not a file argument to `grep`.
- *Why it is wrong:* `|` connects two *commands*; `app.log` is not a command, so the shell will report an error trying to run it as one.
- *Reasoning process:* Ask "what is on each side of the `|`? Are both actually commands?"
- *Corrected command:* `grep "error" app.log`
- *General lesson:* A pipe requires a real command on both sides — a filename alone is not a command.

**Scenario 2 — Wrong redirection operator**
- *Broken command:* `printf "entry 1\n" > log.txt` followed later by `printf "entry 2\n" > log.txt`, intending to build up a log over time.
- *Expected intention:* Accumulate both entries in `log.txt`.
- *What is wrong:* The second command overwrites the first entry entirely.
- *Why it is wrong:* `>` always overwrites; only `>>` appends (Sections 13–14).
- *Reasoning process:* Ask "do I want to replace this file's contents, or add to them?"
- *Corrected command:* `printf "entry 1\n" > log.txt` then `printf "entry 2\n" >> log.txt`.
- *General lesson:* Choose `>` vs. `>>` deliberately, every time — never by habit.

**Scenario 3 — Accidental overwrite**
- *Broken command:* `sort names.txt > names.txt`
- *Expected intention:* Save the sorted version of `names.txt` back into the same file.
- *What is wrong:* This is unreliable and can produce an empty or corrupted file, because the shell may truncate (empty out) `names.txt` as part of setting up the redirection **before** `sort` has actually finished reading it.
- *Why it is wrong:* Redirection targets are typically opened (and, for `>`, truncated) before the command even starts running — so `sort` may end up trying to read from a file that's already been emptied out.
- *Reasoning process:* Ask "is my destination file the same as one of my inputs?"
- *Corrected command:* `sort names.txt > sorted-names.txt` (a different destination file).
- *General lesson:* Never redirect a command's output back into one of its own input files directly.

**Scenario 4 — Missing file**
- *Broken command:* `cat < missing.txt`
- *Expected intention:* Feed `missing.txt`'s contents to `cat` via stdin.
- *What is wrong:* `missing.txt` doesn't exist.
- *Why it is wrong:* Input redirection (`<`) requires the file to already exist — there's nothing to read otherwise.
- *Reasoning process:* Confirm the file actually exists first (`ls`, Lesson 01) before assuming the redirection syntax is the problem.
- *Corrected command:* Create the file first, or correct the filename/path, then retry.
- *General lesson:* An error from `<` is often a plain missing-file problem, not a syntax problem.

**Scenario 5 — stdout/stderr confusion**
- *Broken command:* `grep "error" nonexistent.txt > results.txt`, expecting `results.txt` to contain a helpful error message explaining the file is missing.
- *Expected intention:* Capture whatever `grep` says about the problem.
- *What is wrong:* `results.txt` ends up empty; the actual "No such file or directory" message appears on the screen instead.
- *Why it is wrong:* `>` only redirects stdout. The error message about the missing file is stderr, which is unaffected and still goes to the terminal (Section 16).
- *Reasoning process:* Ask "is this message actually stdout, or could it be stderr?"
- *Corrected command:* `grep "error" nonexistent.txt > results.txt 2> results-errors.txt` (or `2>&1` if you want both together).
- *General lesson:* Redirecting stdout does nothing to stderr — they are genuinely separate channels.

**Scenario 6 — `2>&1` ordering**
- *Broken command:* `grep "error" app.log 2>&1 > combined.txt`, expecting both stdout and stderr in `combined.txt`.
- *Expected intention:* Capture both streams together in one file.
- *What is wrong:* Only stdout ends up in `combined.txt`; stderr still goes to the screen.
- *Why it is wrong:* At the moment `2>&1` runs, stdout is still pointing at the terminal (the `> combined.txt` hasn't happened yet) — so stderr gets pointed at the terminal too, and *then* stdout separately gets redirected to the file (Section 17).
- *Reasoning process:* Trace the redirections left to right, one at a time, asking "where does file descriptor 1 point *at this exact step*?"
- *Corrected command:* `grep "error" app.log > combined.txt 2>&1`
- *General lesson:* Order matters for `2>&1` — redirect stdout to its final destination *first*, then point stderr at stdout.

**Scenario 7 — Pipeline stage failure**
- *Broken command:* `grep "error" wrong-filename.log | sort > result.txt`, and `result.txt` ends up empty, with no obvious error shown.
- *Expected intention:* Get sorted error lines from a log file.
- *What is wrong:* `wrong-filename.log` doesn't exist (a typo), so `grep` produces an error on stderr and no matching lines on stdout; `sort` then receives empty input, and dutifully produces empty output — no crash, just nothing useful.
- *Why it is wrong:* The **first** stage failed, but the pipeline as a whole didn't visibly "crash" — it just quietly produced nothing (Section 21).
- *Reasoning process:* When a pipeline's final result looks wrong or empty, test each stage **independently**, starting from the first one, rather than assuming the last stage is at fault.
- *Corrected command:* First run `grep "error" wrong-filename.log` alone to discover the real filename typo, fix it, then rebuild the pipeline.
- *General lesson:* An empty or wrong pipeline result is often caused by an earlier stage, not the one whose output you're actually looking at.

**Scenario 8 — Wrong assumption about stdin**
- *Broken command:* Assuming `sort < names.txt` and `sort names.txt` must always behave identically for every command, and being confused when a *different* command doesn't accept a filename argument the same way.
- *Expected intention:* Use whichever form is more convenient, interchangeably, for any command.
- *What is wrong:* Not every command is written to accept a filename as a direct argument — some only ever read from stdin.
- *Why it is wrong:* Whether a command accepts a filename argument at all is a property of *that specific command's design*, not a universal guarantee (Section 15).
- *Reasoning process:* Check, for the specific command in question, whether it documents accepting a filename argument, or only reads stdin.
- *Corrected command:* Use `<` redirection as the reliable, general-purpose fallback whenever unsure.
- *General lesson:* `<` works for any command that reads stdin; a filename argument only works if that specific command supports it.

---

## 24. Real-World Software Engineering Use Cases

- **Inspecting logs** — `tail -f app.log` (from Lesson 03) piped into `grep` to watch for a specific event live, or a saved log searched and sorted for review.
- **Filtering build output** — piping a build tool's output through `grep` to surface only errors or warnings among a large amount of text.
- **Searching configuration files** — combining `find` (Lesson 04) results conceptually with `grep`, exactly as previewed in Lesson 04, Section 7.
- **Extracting information** — `cut` (Lesson 05) on the output of another command, to pull out just the piece of data actually needed.
- **Analyzing command output** — piping a command's result into `sort`/`uniq` to summarize it, rather than reading raw, unsorted output by eye.
- **Processing generated text** — redirecting a generated report to a file for later review, instead of only seeing it once on screen.
- **Inspecting test results** — filtering a large test-run output down to just failures.
- **Checking service behavior** — separating a service's normal output from its error output, using the exact techniques from Sections 13–17.
- **Simple operational diagnostics** — a quick pipeline to answer "how many times did this happen?" using `grep | sort | uniq -c`.
- **Chaining Unix tools** — the general principle underlying every example above: small tools, connected together, doing more than any one of them could alone.

---

## 25. Applied AI Engineering Connection

The same techniques apply directly to AI-engineering work:

- **Inspecting model-training logs** — piping a training log through `grep` to find specific events (e.g. `grep "epoch" training.log`).
- **Filtering evaluation output** — isolating just the failed or noteworthy results from a larger evaluation report.
- **Saving experiment output** — redirecting a training run's output to a file for permanent record:

```text
model-training-command
    ↓ stdout
training-output.txt
```

- **Separating normal output from errors** — keeping a clean record of what happened, separately from what went wrong:

```text
model-training-command
    ├── stdout → training-output.txt
    └── stderr → training-errors.txt
```

- **Processing generated datasets** — piping a dataset preview through `head`/`cut` (Lessons 03 and 05) to check its shape without opening the whole thing.
- **Inspecting model files/artifacts** — combining `find` (locate the artifact) with viewing/searching commands, connected via a pipe when appropriate.
- **Combining search and filtering** — `grep`-ing a log for a specific error type, then `sort | uniq -c` to count how often each variant occurred.
- **Analyzing inference/service logs** — the same log-inspection techniques from Section 24, applied to a running inference service instead of a generic application.
- **Preparing data for later tooling** — redirecting a processed, filtered result into a file that a later step (a script, or a tool from a later stage of this roadmap) will consume.

A representative combined pipeline, using only tools already taught across Module 0.3:

```text
logs
 → grep (filter for relevant lines)
 → sort (group similar lines together)
 → uniq (collapse duplicates, optionally counting them)
 → cut (extract just the piece of information needed)
 → output file (redirected, for later review)
```

This lesson does not teach ML frameworks, LLM tooling, RAG, agents, Docker, Kubernetes, or cloud infrastructure. The goal here is narrower and foundational: the exact composition skills practiced in this lesson are what you'll still be reaching for, underneath far more sophisticated tooling, once you reach those later stages.

---

## 26. Bash / Linux / WSL2 / Git Bash / PowerShell

This lesson's primary and reference environment is **Bash on Linux**, identically available under **WSL2** and **Git Bash** — every operator covered here (`|`, `>`, `>>`, `<`, `2>`, `2>>`, `2>&1`) behaves the same way across all three.

**PowerShell** deserves an honest, high-level note rather than a false equivalence: Bash's pipelines are fundamentally **text-stream**-oriented — one command's text output becomes another's text input, exactly as taught throughout this lesson. PowerShell, by contrast, has an **object-oriented pipeline** model in addition to text-oriented behavior — commands can pass structured objects (with named properties) to each other, not just plain text. This is a genuinely different design, not just different syntax. This lesson does not teach PowerShell's pipeline model in depth — only flags that the underlying semantics differ, so you don't carry a false assumption of exact equivalence into a PowerShell environment later. All primary syntax and examples in this lesson are Bash-compatible.

---

## 27. Safe Practical Demonstration

Everything below uses a **disposable, learner-created practice directory** — for example, `command-line-pipes-demo/`. **This lesson does not create this directory for you** — create it yourself if you want to follow along:

```bash
mkdir -p ~/command-line-pipes-demo
cd ~/command-line-pipes-demo
```

Every command below is an **example command** to illustrate a concept. No command in this section has actually been executed by this lesson; every result shown is explicitly labeled `Example output:` — an illustration of expected behavior, never a captured result. Nothing here modifies the real Applied AI Engineering project, uses `sudo`, deletes unrelated files, touches system files, or affects any process other than the ones you deliberately start.

**Step 1 — create a small sample text file**

Example command:
```bash
printf "error: connection timeout\nOK: started\nerror: disk full\nOK: finished\n" > app.log
```
What this does: writes four lines into a new file `app.log`, two of which mention `"error"`.

**Step 2 — view it**

Example command:
```bash
cat app.log
```
Example output:
```text
error: connection timeout
OK: started
error: disk full
OK: finished
```
This confirms the file's contents before doing anything further to it (Lesson 03 habit).

**Step 3 — redirect output to a new file**

Example command:
```bash
grep "error" app.log > errors.txt
```
Where data flows: `grep`'s stdout (the two matching lines) is redirected into a new file `errors.txt`, instead of appearing on screen.
Example output (contents of `errors.txt` afterward):
```text
error: connection timeout
error: disk full
```
Why this result occurs: `>` creates the file and writes stdout into it; nothing appears on the terminal because stdout never reached it.

**Step 4 — append output**

Example command:
```bash
printf "error: retry limit exceeded\n" >> app.log
grep "error" app.log >> errors.txt
```
What this does: adds a new error line to `app.log`, then appends the updated matching results to the *end* of `errors.txt` (which still has Step 3's two lines in it).
Example output (contents of `errors.txt` afterward):
```text
error: connection timeout
error: disk full
error: connection timeout
error: disk full
error: retry limit exceeded
```
Why this result occurs: `>>` preserved the earlier content and added the new `grep` run's full output after it — illustrating exactly why `>` and `>>` produce very different accumulated results over repeated use.

**Step 5 — use input redirection**

Example command:
```bash
sort < app.log
```
Where data flows: `app.log`'s contents are fed to `sort` as stdin, rather than `sort` opening the file itself as an argument.
Example output:
```text
OK: finished
OK: started
error: connection timeout
error: disk full
error: retry limit exceeded
```

**Step 6 — create a simple pipe**

Example command:
```bash
grep "error" app.log | sort
```
Where data flows: `grep`'s matching lines flow directly into `sort`'s stdin via the pipe; the result appears on screen (nothing has been redirected here).
Example output:
```text
error: connection timeout
error: disk full
error: retry limit exceeded
```

**Step 7 — create a multi-stage pipeline**

Example command:
```bash
grep "error" app.log | sort | uniq -c
```
Where data flows: filtered lines → sorted → counted for adjacent duplicates (Lesson 05's `uniq -c`).
Example output:
```text
      1 error: connection timeout
      1 error: disk full
      1 error: retry limit exceeded
```
(Each appears once here since none of these particular lines repeat — this reinforces, rather than contradicts, Lesson 05's adjacency point.)

**Step 8 — redirect pipeline output to a file**

Example command:
```bash
grep "error" app.log | sort > sorted-errors.txt
```
Where data flows: the pipeline's *final* stage's stdout (from `sort`) is redirected to a file; nothing appears on screen.
What the learner should observe: `sorted-errors.txt` now exists, containing the sorted error lines; the terminal shows no output at all.

**Step 9 — separate stdout and stderr**

Example command:
```bash
grep "error" nonexistent-file.log > matches.txt 2> search-errors.txt
```
Where data flows: since `nonexistent-file.log` doesn't exist, `grep` produces no matching lines (so `matches.txt` ends up empty) but does produce an error message on stderr, captured into `search-errors.txt`.
Example output (contents of `search-errors.txt`):
```text
grep: nonexistent-file.log: No such file or directory
```
Why this occurs: stdout and stderr are redirected to two separate destinations independently, exactly as Section 16 described.

**Step 10 — combine output streams conceptually**

Example command:
```bash
grep "error" app.log > combined.txt 2>&1
```
Where data flows: stdout goes to `combined.txt` first; then stderr is pointed at wherever stdout now goes — the same file. Since `app.log` genuinely exists this time, there's no error to observe here, but this is the correct, order-sensitive pattern from Section 17 for the general case where a command might produce both kinds of output together.

**Cleanup:**

```bash
cd ~
rm -r ~/command-line-pipes-demo
```

---

## 28. Common Mistakes (Consolidated Reference)

Section 22 above already lists all fifteen required mistakes in detail — this short pointer exists only so the review section (Section 32) has a single place to reference back to.

---

## 29. Applied AI Engineering Connection (see Section 25)

Covered fully above; not repeated here to avoid redundant content.

---

## 30. Trade-offs

**Pipelines**
- Concise and composable — small tools combine into larger capability without writing new code.
- Powerful — you can answer new questions just by rearranging tools you already know.
- But: an overly long pipeline can become difficult to debug, because a problem in an early stage may not become visible until the very end (Section 23, Scenario 7).

**Redirection**
- Simple and predictable.
- Useful for reproducibility — a saved file is a durable record you can revisit, unlike screen output that scrolls away.
- Useful for preserving output — especially error output, for later diagnosis.
- But: it can overwrite data accidentally, with no warning (Section 13).

**Separating stdout and stderr**
- Improves operational clarity — you can tell "what happened" apart from "what went wrong."
- Enables better diagnostics — errors remain visible/available even when normal output is being saved or piped elsewhere.
- But: it requires actually understanding file descriptors and the two-channel model — a beginner who treats all output as one undifferentiated stream will be confused by cases like Scenario 5 in Section 23.

**One-liners**
- Fast and convenient once you're comfortable with the syntax.
- But: they can become unreadable — a long chain of pipes and redirections, written all at once without testing each stage, is hard for you (or anyone else) to verify or debug later.

None of these commands are "magic tricks" — each behaves according to the same small set of rules taught in this lesson; the judgment is in choosing *when* a pipeline or redirection genuinely simplifies a task, versus when it just adds complexity for no real benefit (Section 20's "make each stage understandable" principle).

---

## 31. Engineering Habits

- **Inspect before modifying** — view a file's current contents (Lesson 03) before redirecting into it.
- **Use disposable files during learning** — exactly as Section 27 modeled.
- **Prefer explicit commands** — a command whose behavior you can state confidently, over one you're only guessing about.
- **Avoid destructive commands while experimenting** — never pipe into `rm` or similar while still learning (echoing Lesson 05's `xargs` caution).
- **Verify paths** — confirm your current working directory (Lesson 01) before any redirection, since a wrong path can silently write somewhere unintended.
- **Understand whether output is stdout or stderr** — before assuming a redirection captured what you expected (Section 23, Scenario 5).
- **Avoid accidental overwrite** — double-check `>` targets, and consider whether `>>` is actually what you meant.
- **Keep pipelines readable** — favor a pipeline you (and others) can read and verify over a maximally "clever" one-liner.
- **Test pipeline stages independently when debugging** — exactly the reasoning process modeled in Section 23, Scenario 7.
- **Preserve useful output when investigating failures** — redirect error output to a file during an investigation, rather than letting it scroll past and disappear.

---

## 32. Practical Exercises

All Level 3–5 practical work must be done inside a disposable directory (for example, one under `/tmp/` or your home directory) created specifically for these exercises, using only harmless, learner-created sample content. Never perform any exercise against the real Applied AI Engineering project directory.

### Level 1 — Recognition

1. Which symbol represents a pipe?
2. Which symbol redirects stdout with overwrite behavior?
3. Which symbol redirects stdout with append behavior?
4. Which symbol redirects stdin from a file?
5. Which symbol redirects stderr with overwrite behavior?
6. What number is conventionally associated with stdout?
7. What number is conventionally associated with stderr?
8. In `command1 | command2`, which command's output becomes the other's input?

### Level 2 — Understanding

1. Explain, in your own words, the difference between `>` and `>>`.
2. Predict what happens to a file's existing content when you redirect into it with `>`.
3. Explain why `grep "x" file.txt > results.txt` might produce an empty `results.txt` even though `file.txt` clearly contains matching lines. (Hint: consider the filename itself.)
4. Explain, conceptually, what `2>&1` does.
5. Why does `command 2>&1 > file.txt` not reliably capture stderr into `file.txt`, while `command > file.txt 2>&1` does?
6. Explain why a command behaves differently when its input comes from a pipe versus when it's given a filename argument directly.
7. If `command1 | command2` runs and `command1` fails internally, why might the pipeline still appear to "succeed" overall?
8. Explain, using the mental model from Section 5, why a pipe is described as connecting two processes rather than two files.

### Level 3 — Application

Perform each of these inside a disposable directory you create for this purpose.

1. Create a small text file using `printf` and `>`.
2. View it with `cat`.
3. Redirect the output of a `grep` search on that file into a new file using `>`.
4. Append additional matching output to that same file using `>>`, and confirm both sets of lines are present.
5. Use `<` to feed the file's contents into `sort` as stdin.
6. Build a two-stage pipeline combining `grep` and `sort`.
7. Extend that pipeline into a three-stage pipeline by adding `uniq` (or `uniq -c`).
8. Deliberately cause an error (e.g. reference a nonexistent file) and use `2>` to capture just the error message into a separate file, confirming your normal terminal isn't cluttered with it.

### Level 4 — Debugging

For each scenario, state the likely cause and the safe fix — explain your reasoning, don't just guess a command.

1. `command1 | command2` reports an error that `command2` isn't recognized as a command, even though you're sure it exists. What might actually be on the left side of the pipe that's causing confusion?
2. You redirected into a file you meant to only add to, and now your earlier content is gone. What operator mistake likely caused this?
3. You expected an error message to appear in your redirected output file, but the file is empty and the message appeared on screen instead. What kind of message is this likely to be?
4. `command > file.txt 2>&1` behaves as expected, but a colleague's `command 2>&1 > file.txt` doesn't capture stderr. What's the difference?
5. A three-stage pipeline produces no output at all, with no visible error. What's your first debugging step?
6. You ran `sort somefile.txt > somefile.txt` and the result is empty or corrupted. What happened?
7. A command that you expected to accept a filename directly doesn't seem to be reading the file at all. What alternative approach, using redirection, would you try?
8. You built a five-stage pipeline and can't tell which stage is producing unexpected results. What systematic approach would you use to isolate the problem?

### Level 5 — Integration

These combine navigation (Lesson 01), file operations (Lesson 02, conceptually), viewing (Lesson 03), searching (Lesson 04), text processing (Lesson 05), and pipes/redirection (this lesson). Perform all of them inside a disposable workspace directory.

1. Navigate into a disposable workspace, create a small simulated log file with several normal lines and a few error lines, and build a pipeline that filters, sorts, and counts the distinct error messages, redirecting the final result to a file.
2. Using `find` (Lesson 04) to locate a specific sample file, pipe its path conceptually into a follow-up inspection step, and explain in words how you'd connect the two (without necessarily needing advanced `xargs` combinations beyond what Lesson 05 covered).
3. Create two sample files, use redirection to combine information extracted from each (via separate `cut` commands, each redirected into its own output file), and explain the resulting data flow.
4. Deliberately construct a pipeline where an early stage references a nonexistent file, observe the misleading "successful but empty" final result, and correctly diagnose it by testing each stage independently.
5. Build one complete, readable pipeline that uses at least three previously learned commands (from Lessons 03–05) connected by pipes, with its final output redirected to a file, and write one sentence justifying why each stage was necessary (per Section 20's readability principle).

---

## 33. Mini-Project — Command-Line Log Processing Pipeline

**Objective:** demonstrate the ability to compose previously learned commands using pipes and redirection to investigate a simulated application log — without any Python, Git, Docker, cloud services, databases, external APIs, or frameworks.

**Scenario:** You've been handed a small application log file. Some entries are normal; some are errors, and a few error messages repeat. You need to produce a clean, sorted, deduplicated summary of just the error messages, saved to a file — while making sure any genuine command errors of your own (like a typo'd filename) are kept separate and visible, not silently mixed into your results.

**Setup:** Create a disposable directory yourself, and populate a log file with sample content — for example:

```bash
mkdir -p ~/log-pipeline-project
cd ~/log-pipeline-project
printf "INFO: server started\nERROR: connection timeout\nINFO: request handled\nERROR: disk full\nERROR: connection timeout\nINFO: request handled\nERROR: disk full\nERROR: connection timeout\n" > service.log
```

**Step-by-step tasks:**

1. **Inspect the log** — view `service.log` completely with `cat` to confirm its contents before processing anything.
2. **Filter relevant lines** — use `grep` to isolate only the lines containing `ERROR`.
3. **Sort and process them** — pipe the filtered lines into `sort`, then into `uniq -c`, to get a count of each distinct error message.
4. **Redirect useful output to a file** — save the final summarized result into a new file (e.g. `error-summary.txt`) using `>`.
5. **Preserve error output separately where appropriate** — deliberately run one command against a filename you know doesn't exist, redirecting its stderr into a separate file (e.g. `pipeline-errors.txt`), to practice keeping genuine tooling errors separate from your actual data results.
6. **Explain the complete data flow** — write out, in your own words, each stage of your main pipeline and what it did to the data at that point.

**Expected reasoning:** the final `error-summary.txt` should show each distinct error message exactly once, with a count reflecting how many times it actually appeared in the original log — and this should only be correct *because* you sorted before deduplicating (Lesson 05).

**Debugging challenge:** run your filtering step against a mistyped filename on purpose, notice that the final summary file is empty or missing expected entries, and correctly trace the problem back to the first pipeline stage rather than assuming `sort` or `uniq` is at fault.

**Completion checklist:**
- [ ] Viewed the raw log before processing it.
- [ ] Built a working `grep | sort | uniq -c` pipeline.
- [ ] Redirected the final summary to a file using `>`.
- [ ] Demonstrated stderr captured separately from stdout, using a deliberate error case.
- [ ] Explained the full data flow, stage by stage, in your own words.
- [ ] Cleaned up the disposable project directory afterward.

**Cleanup instructions:**

```bash
cd ~
rm -r ~/log-pipeline-project
```

**What this project demonstrates:** the ability to compose multiple previously learned Module 0.3 commands into a single, purposeful multi-stage pipeline; to control exactly where different kinds of output end up; and to debug a pipeline by reasoning about each stage independently, rather than treating the whole thing as one opaque unit.

---

## 34. Review

**Pipe vs. redirection, in one line each:**
- A **pipe** connects one command's output directly to another command's input.
- **Redirection** connects a command's input or output to a file instead of the keyboard/screen.

**stdin vs. stdout vs. stderr, in one line each:**
- **stdin** — where a command reads its input from (default: keyboard).
- **stdout** — where a command writes its normal results (default: screen).
- **stderr** — where a command writes error/diagnostic messages (default: screen) — kept separate from stdout so the two can be handled independently.

**Syntax summary:**

| Syntax | Meaning |
|---|---|
| `command1 | command2` | Connect command1's stdout to command2's stdin |
| `command > file` | Redirect stdout to file, overwriting it |
| `command >> file` | Redirect stdout to file, appending to it |
| `command < file` | Feed file's contents to command's stdin |
| `command 2> file` | Redirect stderr to file, overwriting it |
| `command 2>> file` | Redirect stderr to file, appending to it |
| `command > file 2>&1` | Redirect stdout to file, then point stderr at the same place |
| `command &> file` | (Bash-specific) redirect both stdout and stderr to file |

**Mental models to hold onto:**

```text
PIPE:
command A stdout → pipe → command B stdin

REDIRECTION:
stdin/stdout/stderr ↔ file
```

**Common-mistakes checklist** (full detail in Section 22): confusing `|` and `>`; forgetting `>` overwrites; assuming `>>` overwrites; forgetting `uniq`'s adjacency requirement; assuming stderr is piped by default; confusing stdout with stderr; misreading `2>&1`; getting redirection order wrong; over-complicating a pipeline unnecessarily; assuming shell portability; forgetting a pipeline is multiple processes; ignoring exit status; redirecting to the wrong path; experimenting destructively; assuming filename arguments and `<` are always interchangeable.

**Debugging checklist:** test each pipeline stage independently; check whether a message is stdout or stderr before assuming a redirection missed it; trace redirection order left to right; confirm the file/path involved actually exists and is correct; never assume a pipeline "worked" just because it produced *some* output.

**Safety checklist:** use disposable directories and files; never redirect into a file that's also your input; never pipe into a destructive command while learning; avoid `sudo`; verify your current directory before any redirection.

You should now be able to explain, without memorizing definitions, why a pipe is fundamentally different from redirection, and why stdout and stderr are kept as two separate channels rather than one.

---

## 35. Interview Questions

1. **What is a pipe?** A mechanism that connects one command's stdout directly to another command's stdin, so data flows between two processes without an intermediate file.
2. **What does `|` do?** It's the pipe operator — it sets up exactly that connection between the command on its left and the command on its right.
3. **What is stdout?** The default channel a command uses to write its normal output, typically displayed on the terminal unless redirected.
4. **What is stderr?** The default channel a command uses to write error or diagnostic messages, kept separate from stdout so the two can be handled independently.
5. **What are file descriptors 0, 1, and 2?** The conventional numeric identifiers for stdin (0), stdout (1), and stderr (2) — the numbers redirection syntax like `2>` refers to.
6. **What is the difference between `>` and `>>`?** `>` overwrites the destination file's existing contents; `>>` appends to them, leaving existing content intact.
7. **What does `<` do?** It redirects a command's stdin to come from a file, instead of the keyboard.
8. **What does `2>` do?** It redirects stderr specifically to a file, leaving stdout unaffected.
9. **What does `2>&1` mean?** It redirects stderr to wherever file descriptor 1 (stdout) currently points — commonly used, after first redirecting stdout to a file, to capture both streams together.
10. **Why does redirection order matter?** Because the shell processes redirections left to right, and `2>&1` captures stdout's *current* destination at that point in the command — reversing the order changes what "current" means, and thus the result.
11. **What happens internally when `A | B` runs?** The shell starts both `A` and `B` as separate processes, connects `A`'s stdout to a pipe, connects `B`'s stdin to that same pipe, and lets both processes run concurrently, communicating through it.
12. **Why might a pipeline be harder to debug?** Because a failure in an early stage may not produce a visible error at the end — later stages can quietly process empty or wrong input without crashing, masking the real problem.
13. **What happens if an intermediate command fails?** The pipeline as a whole doesn't automatically stop or flag this by default — later stages still run on whatever (possibly empty or wrong) input they receive, and the commonly reported exit status reflects only the last command unless something like `pipefail` is explicitly used.
14. **Why separate stdout and stderr?** So normal results and error/diagnostic messages can be redirected, saved, or displayed independently — essential for both automation and clear manual debugging.
15. **When should you avoid an overly long pipeline?** When it becomes hard to read, hard to verify, or hard to debug — favor clarity and testable stages over a single maximally clever one-liner (Section 20).

---

## 36. Architecture Questions

1. **Why are Unix pipelines composable?** Because each tool follows the same simple convention — read from stdin, write to stdout — meaning any tool's output is automatically compatible as any other tool's input, without special-case integration work.
2. **Why is separating stdout and stderr useful operationally?** It lets you capture, log, or display normal results and error/diagnostic information independently — critical for both automated systems (which need to detect failures reliably) and humans debugging by hand.
3. **What are the advantages of streaming data between processes via a pipe, rather than writing to a temporary file first?** No intermediate file needs to be created, managed, or cleaned up; data can begin flowing to the next stage before the first stage even finishes, rather than waiting for a complete file to be written first.
4. **What failure modes exist in multi-stage pipelines?** An early stage can fail silently (from the pipeline's outward perspective) while later stages still run on incomplete or empty input, producing a misleadingly "successful-looking" but wrong final result (Section 21, Section 23 Scenario 7).
5. **How would you design a safe command-line workflow for processing logs?** Inspect the raw input first; build and test each pipeline stage independently before combining them; keep stdout and stderr separated so genuine tooling failures remain visible rather than mixed into results; redirect final results to a clearly named file rather than relying on transient screen output; avoid overwriting the original log or input data.
6. **How does pipeline composition reflect separation of concerns?** Each command in a pipeline does exactly one well-defined job (filter, sort, deduplicate, extract) — the same engineering principle of giving each component a single clear responsibility, applied at the command-line level rather than inside a single program.
7. **When is a pipeline better than writing a dedicated program?** When the task is a one-off or occasional composition of well-understood, simple operations that existing tools already handle correctly — writing custom code for something `grep | sort | uniq` already solves cleanly would usually be unnecessary effort.
8. **When does a pipeline become too complex?** When it grows long enough, or clever enough, that you (or someone else) can no longer read it and immediately understand what each stage does — at that point, breaking it into separate, named, testable steps (or, later in the roadmap, an actual script) becomes the better choice.

---

## 37. Production Application

The composition skills from this lesson remain directly relevant well beyond this beginner stage:

- **Linux operations** — nearly all day-to-day server investigation relies on exactly this kind of command composition.
- **Backend services** — inspecting a running service's output, separating its normal logs from its error output.
- **Deployment** — checking deployment logs and artifacts using the same filter/sort/redirect techniques.
- **CI/CD** — automated build and test pipelines routinely rely on exactly this stdout/stderr/exit-status model, even when wrapped in more sophisticated tooling.
- **Log inspection** — the single most common real-world application of everything in this lesson.
- **Debugging** — isolating which stage of a larger process actually failed, exactly as practiced in Section 23's debugging scenarios.
- **Automation** — any automated script (a later lesson's topic) still fundamentally relies on the same pipes/redirection/exit-status concepts underneath.
- **Data processing** — even sophisticated data pipelines, at their foundation, still move data from a source, through transformations, to a destination — the same `SOURCE → FILTER → TRANSFORM → OUTPUT` shape from Section 20.
- **AI/ML workflows** — training, evaluation, and inference logs are all inspected, filtered, and archived using these same fundamental techniques, even inside far more advanced infrastructure.

This lesson establishes the foundation for later, more advanced topics — **shell scripting** (automating these same techniques), **developer environments**, **deployment**, **CI/CD**, **observability**, **production debugging**, and **AI infrastructure** — none of which are taught here. The goal of this lesson is specifically to make sure that foundation, when you reach it, is already solid.

---

## 38. Relationship to Module 0.2

Module 0.2 (Operating System Fundamentals) already introduced, at a conceptual level:

- **Processes** — this lesson showed you that a pipe involves *multiple actual processes*, running independently and communicating.
- **File descriptors** — this lesson gave you the concrete numbers (0, 1, 2) and syntax (`2>`, `2>&1`) that put the concept to direct use.
- **Standard input/output** — this lesson turned the abstract "a process reads input and writes output" idea into commands you can actually type.
- **Pipes** — Module 0.2 introduced what a pipe *is*, conceptually, as an operating-system-provided communication channel; this lesson showed you how to actually create one from the shell with `|`.
- **The shell** — this lesson showed, concretely, how the shell parses a command line containing pipes and redirection and sets up the corresponding processes and connections.
- **Process lifecycle** — this lesson's discussion of exit status (Section 21) connects directly to a process's lifecycle concluding with some final status.

The conceptual bridge:

```text
Module 0.2:
Understand what pipes and file descriptors are.

Module 0.3 (this lesson):
Use pipes and redirection from the shell.

Future modules:
Automate and operate systems using these foundations.
```

This lesson does not re-teach Module 0.2's material — it assumes you have that conceptual foundation and builds the practical, hands-on layer directly on top of it.

---

## 39. Relationship to Previous Module 0.3 Lessons

The full progression through Module 0.3 so far:

```text
Navigation
→ locate where you are

File operations
→ create/move/manage files

Viewing
→ inspect content

Searching
→ find relevant content

Text processing
→ transform/select/order content

Pipes + redirection (this lesson)
→ compose commands and control data flow
```

This lesson does not replace anything from Lessons 01–05 — every example in this lesson used commands you already learned, connected together in new ways. The individual tools remain exactly as useful on their own as before; this lesson simply adds the ability to combine them.

---

## 40. Relationship to Next Lesson

The next lesson is `07-environment-variables.md`. This lesson does not teach environment variables — that topic is entirely separate and belongs to the next lesson. The only connection worth naming here: having learned how to compose commands and control data flow in this lesson, the curriculum next moves into environment variables, which affect *how* commands and the shell behave in the first place (rather than how their output flows) — a different, complementary piece of the command-line picture, covered fully when you get there.

---

## 41. Scope Boundary

This lesson teaches only:

- pipes (`|`)
- redirection (`>`, `>>`, `<`, `2>`, `2>>`, `2>&1`, and a brief, clearly-flagged mention of Bash-specific `&>`)
- stdin, stdout, stderr, and file descriptors 0/1/2 conceptually
- multi-stage pipeline data flow
- basic pipeline exit-status reasoning (with only an introductory mention of `pipefail`)
- safe, disposable practical composition of previously learned Module 0.3 commands
- debugging of pipeline/redirection mistakes

This lesson deliberately does **not** deeply teach:

- environment variables (`07-environment-variables.md`)
- shell scripting, loops, functions, or conditionals (`08-shell-scripts.md`)
- permissions (`09-permissions.md`)
- advanced Bash programming or metaprogramming
- process substitution or command substitution
- advanced regular expressions
- Git
- Python (or any language's) subprocess APIs
- Docker, Kubernetes, or cloud operations
- advanced observability or production log-aggregation systems
- distributed systems

These are separate roadmap topics and stages, mentioned in this lesson only where necessary for context. This lesson is not a preview course for any of them.

---

## 42. Final Self-Assessment

Before moving on to `07-environment-variables.md`, confirm you can do each of the following, ideally without checking back:

- [ ] Explain the difference between a pipe and redirection, in your own words.
- [ ] Explain the difference between stdin, stdout, and stderr, and why keeping stdout/stderr separate matters.
- [ ] State what file descriptors 0, 1, and 2 refer to.
- [ ] Predict, before running it, what `command > file.txt` will do to an existing file.
- [ ] Predict the difference in result between `>` and `>>` on the same file, run twice.
- [ ] Explain why `command 2>&1 > file.txt` and `command > file.txt 2>&1` produce different results.
- [ ] Build a two- or three-stage pipeline from commands you already know, and correctly predict its output before running it.
- [ ] Explain why a pipeline can appear to "succeed" even when an earlier stage actually failed.
- [ ] Identify, from a broken example, whether the mistake is a pipe/redirection confusion, an overwrite/append confusion, or a stdout/stderr confusion.
- [ ] State, in one sentence, why you would choose a pipeline over manually running several separate commands and passing results by hand.

If any of these feel uncertain, revisit the relevant section above before continuing — this lesson's techniques are used constantly throughout the rest of this roadmap, and are worth being genuinely solid on now.

---

_This lesson is complete. It covers pipes and redirection only. The remaining Module 0.3 topics are covered in subsequent lessons within this module._
