# Module 0.3 — Command Line

## Lesson 03 — Viewing Files

**Module:** Command Line
**Roadmap reference:** Stage 0 — Module 0.3 — Command Line
**Concept(s) covered:** `cat`, `less`, `head`, `tail` (including `tail -f`)
**Status:** Complete
**Builds on:** 01-navigation.md (`pwd`, `ls`, `cd`), 02-file-operations.md (`mkdir`, `cp`, `mv`, `rm`), and Module 0.2 (filesystem, processes, shell, standard input/output)

---

## Learning Objectives

After completing this lesson you will be able to:

- Explain what it means to "view" a file from the command line, and why this is a core engineering skill rather than a convenience.
- Explain what `cat`, `less`, `head`, and `tail` each do, and choose correctly between them based on file size and purpose.
- Display an entire small file safely using `cat`.
- Navigate a large file interactively using `less`, without modifying it.
- Inspect the beginning of a file using `head`, including a specific number of lines.
- Inspect the end of a file using `tail`, including a specific number of lines.
- Use `tail -f` to watch new lines appended to a growing file, and safely stop watching.
- Explain, at a conceptual level, how these commands relate to the shell, the filesystem, and standard output.
- Recognize when a file is not safe or sensible to view as plain text.
- Diagnose common file-viewing mistakes and errors.
- Explain why these four commands are foundational to debugging, log investigation, and everyday AI-engineering workflows.

---

## 1. What Does "Viewing a File" Mean?

A **file** is data saved to storage under a name — you already worked with files directly in the previous lesson when you created, copied, moved, and deleted them with `mkdir`, `cp`, `mv`, and `rm`. This lesson does not re-teach those commands; it picks up right after them, with a question those commands never answer: **what's actually inside the file?**

A **text file** is a file whose contents are stored as readable characters — letters, numbers, punctuation, line breaks — rather than data meant to be interpreted by a specific program (like an image or an audio file). Most of what you'll inspect in this lesson — configuration files, logs, datasets in plain formats like CSV, source code — is text.

"Viewing" or "inspecting" a file means reading its contents without changing them, so you can understand what's actually stored there. On a graphical desktop, you'd double-click a file to open it in some application. On the command line, you use a small set of dedicated commands whose *only* job is to read a file's contents and show them to you — this lesson covers the four most fundamental ones: `cat`, `less`, `head`, and `tail`.

**Why engineers need this at all:** you cannot safely operate on, copy, deploy, or debug something you haven't actually looked at. File operations (Lesson 02) change what exists and where; file viewing tells you what's *inside* what already exists — a necessary step before and after most other command-line work.

---

## 2. Why File Viewing Matters

Engineers inspect file contents constantly, for reasons that recur across nearly every kind of work:

- **Debugging software** — reading a script or configuration to understand why something behaved unexpectedly.
- **Checking configuration** — confirming what settings a program will actually run with before starting it.
- **Examining logs** — reading a record of what a program did, in what order, and where it may have failed.
- **Inspecting datasets** — checking that a data file actually contains what you expect, in the format you expect.
- **Checking generated artifacts** — confirming that a build, export, or report was produced correctly.
- **Validating outputs** — comparing what a process produced against what it was supposed to produce.
- **Investigating failures** — reading whatever evidence (logs, output files, error dumps) exists after something goes wrong.
- **Understanding unfamiliar projects** — reading configuration and documentation files to orient yourself in a codebase you didn't write.

Command-line inspection specifically (rather than a graphical text editor) matters most in exactly the environments you'll spend increasing time in as an engineer:

- **Remote servers** — you're connected via a text-only terminal session; there is no desktop to open a file browser on.
- **Linux systems generally** — the command line is often the fastest, most direct way to inspect something, even when a GUI exists.
- **Containers** (briefly: isolated, lightweight environments used to package and run software — covered properly much later in this roadmap) — frequently have no graphical tools installed at all.
- **CI/CD environments** (briefly: automated systems that build, test, and deploy code — also covered later) — run entirely without a human present or a graphical interface available.
- **Cloud machines** — typically accessed the same way as remote servers: a terminal session, nothing else.

None of these environments are taught in depth here — they're mentioned only so you understand *why* the command line, rather than a graphical alternative, is often the only realistic option.

---

## 3. File Viewing and the Operating System

Recall from Module 0.2: the **shell** reads what you type and turns it into action, a running command is a **process**, the **filesystem** tracks where file data actually lives on disk, and processes communicate with the user through **standard output** — the default destination for whatever text a program prints.

The conceptual path for a file-viewing command:

```text
You type a command
        ↓
Terminal displays it, shell reads it
        ↓
Shell parses the command name and its arguments (which file, which options)
        ↓
Shell locates and runs the program (cat / less / head / tail)
        ↓
That program asks the operating system to read the requested file's contents
        ↓
The program decides what to do with what it read — show all of it,
show it a screen at a time, or show only part of it
        ↓
The result is written to standard output
        ↓
Standard output is displayed in your terminal
```

The critical distinction for this entire lesson: **file viewing only reads.** `cat`, `less`, `head`, and `tail` ask the operating system to *read* file data — none of them write anything back to the file, rename it, move it, or delete it. This is fundamentally different from every command in Lesson 02, all of which changed the filesystem. Nothing in this lesson can, by itself, modify a file's contents.

This lesson stays at this conceptual level. It does not explain *how* the operating system locates and reads file data internally (file descriptors, system-call-level detail) — that depth is intentionally deferred.

---

## 4. The Four File-Viewing Commands

Before learning each command in depth, here's how they compare at a glance:

| Command | Primary purpose | Typical file size | Output behavior | Interactive? | Useful for logs? | Useful for quick inspection? |
|---|---|---|---|---|---|---|
| `cat` | Display the entire file | Small | Dumps everything at once | No | Rarely (usually too much output) | Yes, for small files |
| `less` | Browse a file's contents | Any size, especially large | Shows one screen at a time; you control movement | Yes | Yes | Yes, especially when unsure of size |
| `head` | Show the beginning | Any size | Shows a fixed number of lines from the start (default 10) | No | Occasionally | Yes |
| `tail` | Show the end | Any size | Shows a fixed number of lines from the end (default 10); `-f` keeps watching | No (unless using `-f`, which stays running) | Yes, very commonly | Yes |

Keep this table in mind as a reference point — the sections below explain *why* each command behaves this way, not just *that* it does.

---

## 5. The `cat` Command

`cat` displays a file's entire contents, all at once, to standard output.

### Where the name comes from

`cat` is short for **concatenate** — to link things together in a sequence. Its original and still-valid purpose is to join multiple files' contents into one continuous output stream:

```bash
cat intro.txt body.txt conclusion.txt
```

This prints `intro.txt`'s contents, immediately followed by `body.txt`'s, immediately followed by `conclusion.txt`'s — as one continuous output, as if they'd been joined into a single file. Using `cat` on just *one* file is really the same behavior with only one thing to "concatenate" — which is why it doubles as the simplest way to just "print this whole file."

### Basic syntax

```bash
cat file.txt
```

This reads `file.txt` from start to finish and writes its entire contents to standard output — the whole thing appears in your terminal immediately, with no interaction required.

### When `cat` is convenient

- The file is short — a small configuration file, a short note, a brief script.
- You want the complete contents visible at once, with no navigation needed.
- You want to quickly confirm a file exists and has the content you expect.

### When `cat` is a poor choice

If a file is large — thousands of lines, or more — `cat` will flood your terminal with output that scrolls past faster than you can read it, leaving only the very end visible on screen. `cat` has no concept of "too much" — it will do exactly what it's told regardless of size. For anything beyond a small file, `less` (next section) is almost always the better choice.

`cat` sends its output to standard output, exactly like every command in this lesson (Section 11 expands on this briefly). You may see `cat` used together with other symbols like `>` or `|` in tutorials — those are **redirection** and **pipes**, which are separate Module 0.3 lessons covered later. This lesson does not teach how they work; only be aware that `cat`'s output, like any command's, can eventually be sent elsewhere instead of just the screen.

---

## 6. The `less` Command

`less` is a **pager** — a program whose job is to display text one screen at a time, letting you move through it at your own pace, instead of dumping everything at once the way `cat` does.

### Why a pager exists

A file with thousands or millions of lines cannot be usefully "displayed" all at once — your terminal window only shows a limited number of lines at a time regardless of the command. `cat` ignores this limitation and prints everything anyway, leaving you to scroll back through your terminal's history to find anything. `less` instead only ever shows you one screen's worth of content, and gives you deliberate controls to move forward, backward, or search — making it the appropriate tool once a file is too large to comfortably read via `cat`.

### Opening a file

```bash
less file.txt
```

This does not print anything immediately in the way `cat` does. Instead, it takes over your terminal temporarily, showing you the first screen of the file's contents, and waits for you to navigate.

### Basic navigation (while inside `less`)

| Key | Action |
|---|---|
| `Space` (or `Page Down`) | Move forward one screen |
| `b` (or `Page Up`) | Move backward one screen |
| `↓` / `↑` (arrow keys) | Move down/up one line |
| `g` | Jump to the beginning of the file |
| `G` | Jump to the end of the file |
| `/searchterm` then Enter | Search forward for text matching `searchterm` |
| `n` | Jump to the next match after a search |
| `q` | Quit `less` and return to your normal shell prompt |

This is intentionally a short, practical list — `less` supports many more keys and behaviors, but this lesson covers only what a beginner needs to navigate and search confidently.

### `less` does not modify the file

Opening a file in `less` — no matter how you scroll or search inside it — never changes the file on disk. `less` only reads; there is no save action, no edit mode, and no way to accidentally alter the file's contents through normal navigation. This is worth stating explicitly because the word "editor" is sometimes loosely (and incorrectly) applied to it — `less` is a **viewer**, not an editor.

### `cat file.txt` vs `less file.txt`

```bash
cat file.txt     # prints everything immediately, no interaction, best for small files
less file.txt    # opens an interactive, scrollable view, best for large or unfamiliar files
```

If you're unsure how large a file is, `less` is the safer default — it never floods your terminal, regardless of the file's actual size.

> **Note on demonstrated interaction:** any `less` session shown in this lesson (Section 15) describes what you would see and do interactively — it is not, and cannot be, captured as ordinary terminal output the way `cat`'s output can, since `less` takes over the screen. Where this lesson shows what a `less` screen would look like, it is explicitly labeled as an illustration, not literal captured output.

---

## 7. The `head` Command

`head` shows only the **beginning** of a file — by default, its first 10 lines.

### Basic syntax and default behavior

```bash
head file.txt
```

This prints the first 10 lines of `file.txt` to standard output, then stops — regardless of how long the file actually is.

### Choosing a specific number of lines

```bash
head -n 10 file.txt
head -n 3 file.txt
```

The `-n` option lets you specify exactly how many lines from the start you want to see, instead of relying on the default of 10.

### Why the beginning of a file is valuable

- **Configuration files** — settings are often listed near the top; the beginning tells you what a config is fundamentally structured to control.
- **CSV files** (a plain-text format that stores rows of data separated by commas) — the first line is typically a **header row** naming each column, so `head` is the fastest way to see what fields a dataset actually has.
- **Datasets in general** — a quick look at the first few rows confirms the data looks like what you expect, before you commit to loading the whole thing into a program.
- **Logs** — the beginning of a log tells you when logging started and in what initial state the program was.
- **Generated reports** — the top of a report often states what was generated, when, and by what process.
- **Metadata files** — key identifying information is frequently placed first.

### An important limitation

`head` only displays lines — it has no understanding of what those lines *mean*. When you run `head data.csv`, you see the first several lines of text, which *happens* to include the CSV header row if the file is well-formed — but `head` does not know the file is CSV, does not parse columns, and would show you exactly the same kind of output on a file that merely *looks* similar but isn't actually valid CSV. Understanding a CSV file's actual structure and contents is a job for a proper parsing tool or library (encountered later in this roadmap, once you reach programming) — not for `head`, which only knows about lines of text, not the format they represent.

---

## 8. The `tail` Command

`tail` shows only the **end** of a file — by default, its last 10 lines.

### Basic syntax and default behavior

```bash
tail file.txt
```

This prints the last 10 lines of `file.txt`, regardless of how long the file is.

### Choosing a specific number of lines

```bash
tail -n 20 file.txt
tail -n 5 file.txt
```

Just like `head`, `-n` lets you control exactly how many lines you want to see, from the end instead of the beginning.

### Why the end of a file is valuable

- **Logs** — the most recent events, including the most recent errors, are at the end of a log file that's continuously appended to.
- **Generated reports** — a summary or final result is often written last.
- **Batch-processing output** — the final status ("completed," "3 records failed," etc.) typically appears at the end.
- **Application results** — final computed values or conclusions are commonly the last thing written.
- **Error messages** — when a long-running process fails, the actual error is usually the very last thing it printed before stopping — exactly what `tail` surfaces without wading through everything that came before it.

### `tail -f` — following appended output

Some files — most notably active log files — keep growing while a program runs, with new lines continuously added to the end. `tail -f` ("follow") does something the plain commands in this lesson don't: instead of printing a fixed amount and stopping, it keeps running and displays new lines *as they're appended*, live.

```bash
tail -f application.log
```

Conceptually: `tail -f` first shows you the existing end of the file (like a normal `tail`), and then stays active, watching the file for anything newly written to it, printing each new line the moment it appears. This is how engineers watch a running service's behavior in real time, directly from its log file, without repeatedly re-running `tail` by hand.

**Exiting `tail -f` safely:** because it keeps running indefinitely by design, it does not stop on its own. Press `Ctrl+C` to stop it and return to your normal shell prompt — this only stops the *viewing*; it has no effect whatsoever on the program that's actually writing to the log file.

This lesson introduces `tail -f` only as a way to observe a file that is actively growing — it does not turn this into a log-monitoring or observability lesson. Real production log monitoring, covered far later in this roadmap, involves dedicated tools built for exactly this purpose at much larger scale.

---

## 9. `cat` vs `less` vs `head` vs `tail`

| | `cat` | `less` | `head` | `tail` |
|---|---|---|---|---|
| **Purpose** | Display entire file | Browse file interactively | Show the beginning | Show the end |
| **Output amount** | All of it, at once | Controlled by you, screen at a time | A fixed number of lines (default 10) | A fixed number of lines (default 10), or continuous with `-f` |
| **Interactive?** | No | Yes | No | No (except `-f`, which runs continuously until stopped) |
| **Best use case** | Small file, want it all immediately | Large or unfamiliar file, want to browse/search | Check the start — headers, config, early log entries | Check the end — recent logs, final results, errors |
| **Large-file suitability** | Poor — floods the terminal | Excellent — this is exactly what it's for | Good — only ever shows a small, fixed amount | Good — only ever shows a small, fixed amount (or a live trickle with `-f`) |
| **Log usefulness** | Low, unless the log is tiny | High, for browsing/searching history | Low–moderate, for checking when logging began | High — most investigations start at the end |
| **Beginner usage** | Very easy | Requires learning a few navigation keys | Very easy | Very easy |
| **Potential risk** | Overwhelming output on a large file | None functionally; just takes a moment to learn navigation | None — output is inherently limited | `-f` runs indefinitely if you forget to stop it |

### Practical decision rules

- Need to see a **small file completely** → `cat`
- Need to **inspect a large file interactively** → `less`
- Need to see the **beginning** of a file → `head`
- Need to see the **end** of a file → `tail`
- Need to **watch appended log data live** → `tail -f`

These are practical defaults, not absolute laws — for instance, `less` works perfectly well on a small file too; it's simply not *necessary* there. Use judgment based on what you're actually trying to learn from the file.

---

## 10. Internal Mechanics

At a conceptual level, running any of these four commands follows the same shape:

1. **The shell parses the command** — identifying the command name, any options (like `-n 10` or `-f`), and the target file path (resolved as absolute or relative, exactly as covered in Lesson 01).
2. **The command is executed** as a short-lived process (Module 0.2).
3. **The command accesses the requested file** through the operating system, which locates the file's data via the filesystem.
4. **File contents are read.**
5. **The command processes or selects what should actually be displayed** — this is where the four commands diverge:
   - `cat` reads and prints everything, start to finish, with no selection logic.
   - `head` reads only as far as it needs to satisfy the requested line count, then stops early.
   - `tail` locates the end of the file's content and works backward to gather the requested number of lines.
   - `less` reads only enough to fill the current screen, requesting more from the file only as you scroll further — it does not need to have "the whole file" in hand to start showing you something.
6. **Output is presented through the terminal** — for `cat`, `head`, and `tail`, this is a normal, one-time print to standard output; for `less`, it's an interactive display that stays under your control until you press `q`.

For **`tail -f`** specifically: after printing the current end of the file, the process does not exit the way `head` or a plain `tail` does. It remains running, periodically checking whether new content has been appended to the file, and immediately prints anything new it finds — which is why it keeps running until you deliberately stop it with `Ctrl+C`.

This lesson deliberately stops at this level. It does not explain buffering strategies, kernel-level read mechanisms, filesystem implementation details, or terminal-driver internals — those are out of scope here.

---

## 11. Standard Output Connection

Every command in this lesson produces its result by writing to **standard output** — the default channel a running program uses to send text output, which your terminal displays for you. This is the same concept briefly introduced in Module 0.2 and referenced conceptually in Lesson 02.

For now, the only thing to internalize is: **when `cat`, `head`, or `tail` print something, they are writing to standard output, and your terminal is simply showing you what arrived there.** `less` is a bit different — because it's interactive, it manages the terminal display directly rather than simply streaming to standard output the way the others do, but it's still fundamentally about text content flowing from the file to something you can read.

This lesson does not teach what you can *do* with standard output beyond viewing it directly — specifically, it does not cover file descriptors, output redirection (`>`, `>>`), error-stream redirection (`2>`, `2>&1`), or pipes (`|`). Those are separate, dedicated Module 0.3 lessons. The only goal here is the mental connection: **these commands produce output; that output normally goes to your screen; later lessons will show you how to send it elsewhere instead.**

---

## 12. Real-World Software Engineering Use Cases

- **Inspecting application configuration** — `cat config.yaml` to quickly confirm settings before starting a service.
- **Inspecting logs** — `tail -n 50 server.log` to see recent activity, or `tail -f server.log` while reproducing an issue live.
- **Inspecting generated files** — `less generated-report.txt` to review something a tool produced.
- **Inspecting build output** — `tail build.log` to see whether a build finished successfully or where it failed.
- **Inspecting test output** — `less test-results.txt` to review a long test run's full output.
- **Inspecting data files** — `head dataset.csv` to sanity-check a file before using it.
- **Inspecting model metadata** — `cat model-info.json` to check a small metadata file describing a saved model.
- **Inspecting experiment results** — `head`/`tail` on a results file to spot-check the start and end of an experiment's output.
- **Inspecting deployment artifacts** — `cat` or `less` on a packaged file's manifest or contents listing.
- **Troubleshooting failed processes** — `tail` a process's log immediately after it fails, since the error is almost always at the end.

Command-line inspection is especially valuable when there's **no graphical interface available at all** — which, as Section 2 explained, is the normal situation on remote servers, inside containers, and in CI/CD environments. In those contexts, `cat`, `less`, `head`, and `tail` are often the *only* practical way to look inside a file.

---

## 13. AI Engineering Connection

Using the same representative project layout from the previous lesson:

```text
project/
├── src/
├── tests/
├── data/
├── models/
├── configs/
├── logs/
└── artifacts/
```

Realistic file-viewing usage in this kind of project:

- `head data/training-set.csv` — confirm the dataset's columns and a few sample rows before starting a training run.
- `tail logs/training-run-042.log` — check whether a training run completed successfully or check the most recent error.
- `less artifacts/evaluation-report.txt` — read through a large evaluation report at your own pace, searching for specific metrics.
- `cat configs/experiment-config.yaml` — quickly review a small configuration file's exact settings.
- `cat models/model-info.json` — check a model artifact's metadata (version, training date, key parameters).
- `head artifacts/batch-output.csv` — spot-check the beginning of a batch-processing job's output.
- `tail -f logs/live-inference.log` — watch a running inference service's log in real time while testing it.

Realistic failure scenarios this lesson's commands directly help investigate:

- **A training job produced unexpected output** — `tail` the training log to see the final lines before it stopped, which usually contain the actual error or last successful step.
- **An evaluation report is incomplete** — `less` (or `tail`) the report to check whether it actually finished writing, or cut off partway through.
- **An application log contains an error near the end** — exactly the scenario `tail` (or `tail -f`, if the process is still running) is built for.
- **A dataset contains unexpected rows** — `head` the file to check the format actually matches what your code expects, before assuming the bug is in your code rather than the data.
- **A generated configuration is incorrect** — `cat` the generated file directly to see exactly what was produced, rather than assuming from the generating code alone.
- **Model metadata is missing or malformed** — `cat` the metadata file to see its literal contents, which often reveals the problem immediately (empty file, wrong format, missing fields).

None of this requires any AI/ML framework knowledge — it's the same four commands, applied to files that happen to belong to an AI project.

---

## 14. Bash / Linux / WSL2 / Git Bash / PowerShell

This lesson's primary teaching environment is **Bash on Linux**, which behaves identically under **WSL2** and **Git Bash** for all four commands.

**PowerShell** (native Windows) provides overlapping capability through a different command:

| Bash/Linux | PowerShell equivalent | Notes |
|---|---|---|
| `cat file.txt` | `Get-Content file.txt` | Displays the whole file, similar to `cat` |
| `head -n 10 file.txt` | `Get-Content file.txt -Head 10` | `-Head` selects the first N lines |
| `tail -n 10 file.txt` | `Get-Content file.txt -Tail 10` | `-Tail` selects the last N lines |
| `less file.txt` | *(no exact equivalent by default)* | PowerShell has no built-in interactive pager identical to `less`; long output is typically piped through another tool instead |

This table exists only to orient you if you're working on native Windows — it is not a PowerShell course, and this lesson does not teach PowerShell's broader command model. **WSL2** consideration worth repeating from the previous lesson: it runs a genuine Linux filesystem and shell, so `cat`, `less`, `head`, and `tail` behave exactly as described throughout this lesson when used inside a WSL2 session.

---

## 15. Safe Practical Demonstration

Everything below happens inside a disposable directory, `/tmp/command-line-viewing-demo`, created solely for this demonstration. Nothing here touches the real Applied AI Engineering project or any unrelated file. All shown output is explicitly labeled **Example output** — illustrative only, not literally captured from a live run.

**Step 1 — create the disposable area and a small sample file**

```bash
mkdir -p /tmp/command-line-viewing-demo
cd /tmp/command-line-viewing-demo
printf "line 1\nline 2\nline 3\n" > sample.txt
```

**Step 2 — inspect it completely with `cat`**

```bash
cat sample.txt
```
Example output:
```text
line 1
line 2
line 3
```

**Step 3 — inspect it with `less`**

```bash
less sample.txt
```
Example output (illustrating what the interactive screen would show):
```text
line 1
line 2
line 3
~
~
(END)
```
The `~` lines indicate there's nothing more below the file's content, and `(END)` marks that you've reached the bottom. Pressing `q` here returns you to your shell prompt. Because `sample.txt` is only 3 lines, `less` is not really *necessary* here — it's shown only to demonstrate the interaction; `cat` would be the more natural choice for a file this small.

**Step 4 — inspect the first lines with `head`**

```bash
head -n 2 sample.txt
```
Example output:
```text
line 1
line 2
```

**Step 5 — inspect the last lines with `tail`**

```bash
tail -n 2 sample.txt
```
Example output:
```text
line 2
line 3
```

**Step 6 — create a larger sample file**

```bash
seq 1 500 > larger-sample.txt
```
(This creates 500 lines, each containing one number — a harmless, disposable stand-in for a "large file.")

**Step 7 — demonstrate why `less` is preferable for a large file**

```bash
cat larger-sample.txt
```
Running this would immediately print all 500 lines, scrolling past far faster than readable, leaving only the last screenful visible without scrolling back through your terminal's history.

```bash
less larger-sample.txt
```
This instead opens one screen at a time — you could press `Space` repeatedly to move forward at your own pace, `g` to jump to the start, `G` to jump to the end, or `/` to search for a specific number — all without ever overwhelming your terminal.

**Step 8 — demonstrate `tail -f`**

```bash
tail -f larger-sample.txt
```

This requires an interactive terminal session and cannot be meaningfully shown as static output — running it against `larger-sample.txt` (which nothing is currently appending to) would simply show the last 10 lines and then wait indefinitely for new lines that never arrive, since nothing is writing to this file. In a real scenario, `tail -f` is run against a file that *something else* (a running program) is actively writing to. If you try this yourself, remember: press `Ctrl+C` to stop it and return to your prompt — this does not affect any other process.

**Step 9 — clean up the disposable demonstration area**

```bash
cd /tmp
rm -r /tmp/command-line-viewing-demo
ls /tmp/command-line-viewing-demo
```
Example output (confirming cleanup succeeded):
```text
ls: cannot access '/tmp/command-line-viewing-demo': No such file or directory
```

---

## 16. Common Mistakes and Debugging

**1. File does not exist**
- *Situation:* `cat report.txt`, but the file was never created, or was named differently.
- *Symptom:* `cat: report.txt: No such file or directory`
- *Likely cause:* Typo, wrong extension, or the file simply isn't there yet.
- *Investigate:* `ls` the current directory to see what actually exists.
- *Safe fix:* Correct the filename and retry.
- *Lesson learned:* Confirm a file exists before assuming a viewing command is broken.

**2. Wrong path**
- *Situation:* `head data/train.csv`, but `data/` doesn't exist at this level.
- *Symptom:* `head: cannot open 'data/train.csv' for reading: No such file or directory`
- *Likely cause:* The path assumed a directory structure that doesn't match reality from here.
- *Investigate:* `ls` to see what directories actually exist, or use `pwd` combined with `ls` on suspected parent directories.
- *Safe fix:* Correct the path, or navigate (Lesson 01) to the right location first.
- *Lesson learned:* Viewing commands resolve paths exactly the same way navigation and file operations do — the same care applies.

**3. Wrong current working directory**
- *Situation:* `cat config.yaml` from the wrong directory, either erroring or — worse — successfully displaying a *different* file that happens to share the name.
- *Symptom:* Either an error, or unexpectedly unfamiliar content.
- *Likely cause:* Forgot to check `pwd` before assuming what a relative path points to.
- *Investigate:* `pwd`, then `ls`.
- *Safe fix:* Navigate to the intended directory, confirm with `pwd`, and retry.
- *Lesson learned:* This is the same navigation discipline from Lesson 01 — it applies to viewing files just as much as to operating on them.

**4. Permission denied**
- *Situation:* `cat /var/log/secure-app.log` (or any file you don't have read access to).
- *Symptom:* `cat: /var/log/secure-app.log: Permission denied`
- *Likely cause:* Insufficient permissions (Module 0.2 concept; full permissions coverage comes later in this module).
- *Investigate:* `ls -l` on the file to check its permission bits and ownership.
- *Safe fix:* Do not reflexively reach for `sudo`. Confirm you're actually supposed to have access before trying to force past this.
- *Lesson learned:* "Permission denied" while viewing is the operating system correctly protecting something — treat it as information, not an obstacle to bypass.

**5. Trying to use `cat` on a very large file**
- *Situation:* `cat massive-dataset.csv`, where the file has millions of lines.
- *Symptom:* Your terminal is flooded with scrolling text for a long time, and you can only see the last screenful once it finally stops.
- *Likely cause:* `cat` has no size awareness — it always prints everything.
- *Investigate:* Check the file's size first if you're unsure (a topic covered more fully with `ls -lh`, from Lesson 01).
- *Safe fix:* Use `less` to browse interactively, or `head`/`tail` if you only need part of it.
- *Lesson learned:* Choose `cat` deliberately for small files, not as a default habit for every file regardless of size.

**6. Misunderstanding `head` output**
- *Situation:* Assuming `head data.csv` has shown you "the data," when it's only shown the first 10 lines.
- *Symptom:* No error — but conclusions drawn from `head` alone turn out to be wrong once the full file is examined (e.g. assuming a column's values are always small numbers, when later rows differ wildly).
- *Likely cause:* Treating a partial view as if it were the complete picture.
- *Investigate:* Consider also checking `tail`, or using `less` to browse more broadly, before drawing conclusions about an entire dataset from `head` alone.
- *Safe fix:* Use `head` for a quick first look, not as a substitute for actually understanding the full file when it matters.
- *Lesson learned:* `head` shows you *some* of the file, not a summary or a representative sample of the *whole* file.

**7. Misunderstanding `tail` output**
- *Situation:* Assuming `tail file.log` shows "the last line," when it actually shows the last 10 lines by default.
- *Symptom:* Confusion about which line is "the" most recent one among the several printed.
- *Likely cause:* Not realizing the default is 10 lines, not 1.
- *Investigate:* Re-run with an explicit `-n 1` if you specifically want only the single last line.
- *Safe fix:* Use `tail -n 1 file.log` when you truly want just the final line.
- *Lesson learned:* Always know (or explicitly set) how many lines a command is showing you, rather than assuming.

**8. `tail -f` appears to be stuck**
- *Situation:* `tail -f app.log` is run, and nothing appears to happen — no new output, no return to the prompt.
- *Symptom:* The terminal seems frozen.
- *Likely cause:* This is expected, not a malfunction — `tail -f` waits indefinitely for new content, and if nothing is currently being written to the file, nothing new will appear. The command is running correctly; it's simply waiting.
- *Investigate:* Confirm whether the process you expect to be writing to this log is actually running and actually producing output.
- *Safe fix:* This isn't something to "fix" by force — if you no longer need to watch, press `Ctrl+C` to stop and return to your prompt.
- *Lesson learned:* "No new output" from `tail -f` usually means "no new activity," not "the command is broken."

**9. User cannot exit `less`**
- *Situation:* Inside a `less` session, unsure how to get back to the shell prompt.
- *Symptom:* Typing seemingly does nothing useful, or produces unexpected on-screen behavior.
- *Likely cause:* Not knowing the exit key.
- *Investigate:* Recall Section 6's navigation table.
- *Safe fix:* Press `q`.
- *Lesson learned:* `less` uses dedicated single-key commands rather than typed commands with Enter — `q` is the one to remember above all others.

**10. Binary/non-text file produces confusing output**
- *Situation:* `cat image.png` or `cat model-weights.bin`.
- *Symptom:* A burst of strange symbols, garbled characters, or a terminal that visually looks "broken" afterward (colors or characters displaying oddly even after the command finishes).
- *Likely cause:* The file is **binary** — data meant for a specific program to interpret, not human-readable text — and `cat` printed its raw bytes directly to your terminal, which tried (and failed) to interpret them as text/display codes.
- *Investigate:* Recognize the file type from its purpose or extension before viewing it as text.
- *Safe fix:* Don't `cat` binary files. If your terminal looks visually corrupted afterward, closing and reopening the terminal window (or, in some terminals, typing `reset` and pressing Enter) restores it.
- *Lesson learned:* Not every file is safe to display as text — see Section 18.

**11. File changes while being inspected**
- *Situation:* You `cat` or `head` a log file, then look again moments later and see different content, or a program writing to the file behaves unexpectedly around the same time.
- *Symptom:* Confusing, seemingly "inconsistent" output between two inspections.
- *Likely cause:* The file is actively being written to by another process; each viewing command simply reads it at one instant in time — it's not a "live" view unless you specifically use `tail -f`.
- *Investigate:* Consider whether the file is one that's continuously updated (a log, typically) rather than static.
- *Safe fix:* For files that change over time, use `tail -f` when you specifically want to observe ongoing changes, rather than repeatedly re-running a one-time viewing command.
- *Lesson learned:* `cat`, `head`, and plain `tail` each capture a single snapshot in time — not a live view.

**12. Terminal output is too large to interpret**
- *Situation:* After running `cat` on a large file, so much text has scrolled past that you can't find anything useful.
- *Symptom:* Overwhelming, seemingly unusable output.
- *Likely cause:* Same root cause as mistake #5 — `cat` was the wrong tool for this size of file.
- *Investigate:* Consider what you were actually trying to find — the beginning, the end, or something specific in the middle.
- *Safe fix:* Re-approach with `head`, `tail`, or `less` (with its search capability), depending on what you actually need.
- *Lesson learned:* When output feels unmanageable, that's a sign to choose a more targeted command, not to scroll harder.

---

## 17. Common Misconceptions

- **"`cat` is only for tiny files."** — There's no hard size limit; `cat` works on files of any size. The issue is *practicality*, not a restriction — it becomes an unpleasant, hard-to-read choice as files grow, but it isn't disabled or unsafe on larger files, just inconvenient.
- **"`less` modifies the file."** — It does not. `less` is a read-only viewer; nothing about scrolling, searching, or exiting changes the file's contents.
- **"`head` understands the structure of CSV files."** — It doesn't. `head` only knows about lines of text; it has no concept of columns, headers, or CSV syntax specifically (Section 7).
- **"`tail` always shows only the final line."** — By default it shows the last 10 lines; use `tail -n 1` if you specifically want just one.
- **"`tail -f` is frozen when no new data appears."** — It's working correctly; it's simply waiting for new content, exactly as designed (Section 16, mistake #8).
- **"Viewing a file changes it."** — None of the four commands in this lesson write to the file being viewed; viewing and modifying are entirely separate categories of operation (Section 3).
- **"`cat` is always the fastest/best choice."** — It's the simplest for small files, but a poor choice for large ones, where `less`, `head`, or `tail` are more appropriate (Section 9).
- **"A file ending in `.log` is automatically a log format understood by `tail`."** — `tail` doesn't parse or understand "log format" at all; it just shows lines of text, regardless of the file's extension or actual structure. `.log` is only a naming convention, not something the command interprets specially.
- **"All files are safe to display as text."** — Binary files can produce garbled output and, in some cases, visually disrupt your terminal session (Section 16, mistake #10; Section 18).
- **"PowerShell and Bash use exactly the same commands."** — They achieve similar goals with different commands and options (Section 14) — `cat` and `Get-Content` are related in purpose, not identical in syntax.

---

## 18. File Types and Viewing Safety

Not every file should be treated as ordinary readable text:

- **Text files** — human-readable characters and line breaks; this is what `cat`, `less`, `head`, and `tail` are meant for, and what nearly every example in this lesson has used.
- **Binary files** — data encoded for a specific program to interpret (images, audio, compiled programs, many model-weight files). Viewing these as text produces meaningless or garbled output, and — as noted in Section 16 — can occasionally leave your terminal display looking visually corrupted until it's reset or reopened.
- **Structured text such as CSV or JSON** — still genuinely text, and safe to view with these commands, but with internal structure (columns, key-value pairs) that `cat`/`less`/`head`/`tail` display as plain lines without understanding that structure at all (Section 7's CSV point applies equally to JSON).
- **Logs** — ordinary text files, distinguished only by convention (typically one event per line, growing over time) — nothing about the commands in this lesson treats "logs" as a special category; they're simply text files that happen to be used this way.

This lesson does not teach binary file formats in depth, nor does it introduce specialized inspection tools beyond `cat`/`less`/`head`/`tail` — the only safety point to carry forward is: **before viewing an unfamiliar file, consider whether it's actually meant to be read as text at all.**

---

## 19. Trade-offs and Engineering Habits

- **`cat`'s simplicity vs. excessive output** — trivially simple for small files, but scales poorly; the convenience disappears exactly when the file grows.
- **`less`'s interactivity vs. automation** — excellent for a human browsing a file by hand, but its interactive nature makes it unsuitable for scripts or automated processes (which need output that finishes and returns predictably — a topic that becomes relevant once you reach shell scripting, later in this module).
- **`head`/`tail`'s efficiency for partial inspection** — both are efficient precisely because they don't need to process an entire large file to answer a narrow question ("what's at the start/end?").
- **Inspecting a small portion before opening a large file** — a `head` or `tail` glance before committing to a full `less` session (or, worse, a full `cat`) often tells you enough to decide whether deeper inspection is even necessary.
- **Manual inspection vs. later automation** — reading files by hand with these commands is appropriate for one-off investigation; recurring, systematic inspection needs (like continuous log monitoring) eventually call for the automated approaches introduced far later in this roadmap.
- **Human-readable inspection vs. machine parsing** — these commands show you text as a human reads it; actually processing a file's structured content programmatically (extracting specific fields, aggregating values) is a job for the searching and text-processing commands in upcoming lessons, or for a programming language once you reach that stage.

The engineering habit this lesson is building: **inspect only what you need first.**

```text
head → understand the beginning
tail → understand the ending
less → inspect selectively, at your own pace
cat  → display a small, complete file in one step
```

This habit matters increasingly as you work with larger datasets, larger logs, and production systems where a careless `cat` on a multi-gigabyte file isn't just inconvenient — it can meaningfully slow down or clutter a shared remote session other people depend on.

---

## 20. Practical Exercises

All Level 3–5 practical work must be done inside a disposable directory (for example, a fresh directory under `/tmp/`), created specifically for these exercises. Never perform any exercise against the real Applied AI Engineering project directory.

### Level 1 — Recognition

1. Which command displays an entire small file at once, with no interaction required?
2. Which command is designed specifically for browsing large files interactively?
3. Which command shows only the beginning of a file?
4. Which command shows only the end of a file?
5. Which command would you use to watch a log file for new lines as they're written?
6. What key exits a `less` session?
7. What is the default number of lines shown by `head` and `tail` when no count is specified?
8. Which of the four commands never finishes on its own unless you stop it?

### Level 2 — Understanding

1. Predict what `cat` would do if run on a file containing one million lines.
2. Given a 5-line file, does it matter whether you use `cat` or `less`? Explain why or why not.
3. Why is `head` a poor tool for confirming that a CSV file has no malformed rows anywhere in the file?
4. If a log file is actively being written to by a running service, why would `tail -f` show you something that a plain `tail` would not?
5. Explain, in your own words, why `less` reading "just enough for one screen" is different from `cat` reading the whole file up front.
6. Why does pressing `Ctrl+C` on a running `tail -f` not affect the program that's writing to the log?
7. If you only want the single most recent line of a log file, what exact command would you use, and why isn't plain `tail` enough on its own?
8. Why is `cat` on a binary file likely to produce confusing terminal output, even though the command "succeeds"?

### Level 3 — Application

Perform each of these inside a disposable directory you create for this purpose (e.g. `/tmp/lesson03-practice`).

1. Create a small text file with 5 short lines of your own choosing, and display it completely using `cat`.
2. Open that same file with `less`, scroll to the end, then scroll back to the beginning, then exit without making any changes.
3. Create a second file with at least 50 lines (numbers or repeated short lines are fine), and use `head` to view only the first 5.
4. Use `tail` on that same file to view only the last 5 lines.
5. Use `head -n 1` and then `tail -n 1` on the 50-line file to confirm the very first and very last line.
6. Create a third file simulating a small "log," with several lines, and use `tail -n 3` to simulate checking "recent activity."
7. Practice searching inside a file using `less`'s `/searchterm` feature on one of your created files.
8. Clean up your disposable practice directory entirely, and confirm with `ls` that it's gone.

### Level 4 — Debugging

For each scenario, state the likely cause and the safe fix — explain your reasoning, don't just guess a command.

1. `cat notes.txt` returns `cat: notes.txt: No such file or directory`. What would you check first?
2. `head -n 10 data/values.csv` fails because `data/` doesn't exist from your current location. What's the safe next step?
3. You run `tail report.txt` and see only 10 lines, but you specifically need the last 30. What's wrong with your command?
4. `tail -f service.log` seems to "hang" with no output for several minutes. Is this necessarily a problem? How would you check?
5. You're inside a `less` session and can't figure out how to leave. What should you try?
6. `cat photo.jpg` produces a burst of strange characters and your terminal looks visually odd afterward. What happened, and how do you recover?
7. You ran `head config.yaml` and concluded the whole file only has 8 lines, but a teammate says it has 200. What's the flaw in your conclusion?
8. A file you're viewing with `cat` appears to have different content each time you view it. What would you check to understand why?

### Level 5 — Integration

These combine navigation (Lesson 01), file operations (Lesson 02), and file viewing (this lesson). Perform all of them inside a disposable workspace directory.

1. Starting from your home directory, navigate into a new disposable workspace, create a small file with `mkdir`/basic file creation, then inspect it with `cat` to confirm its contents before proceeding.
2. Create a directory structure resembling `workspace/logs/`, create a simulated log file inside it with several lines, move it (using `mv`) to a renamed file, then `tail` the renamed file to confirm the move preserved its contents.
3. Copy (using `cp`) a sample "config" file to a second location, and use `cat` on both the original and the copy to confirm they're identical.
4. Create a larger sample file (50+ lines), use `head` and `tail` to inspect both ends, then safely delete (`rm`) only that one disposable file — confirming with `ls` that only the intended file was removed.
5. Simulate a small investigation: create a "log" file with a normal-looking first half and an "ERROR" line near the end, then use `tail` to demonstrate how you'd quickly locate that error without reading the whole file with `cat`.

---

## 21. Mini-Project — Command-Line File Inspector

**Goal:** build file-inspection judgment — choosing the *right* command for each situation — not command memorization. Use a disposable workspace only; do not touch the real Applied AI Engineering project.

**Setup:**

```bash
mkdir -p /tmp/file-inspector-project/workspace/{data,configs,logs,reports,artifacts}
cd /tmp/file-inspector-project/workspace
```

**Tasks:**

1. Navigate into the disposable workspace and confirm your location with `pwd`.
2. Create a small configuration file inside `configs/` (a few lines is enough) and inspect it completely using `cat` — appropriate here because it's short.
3. Create a longer "report" file inside `reports/` (at least 60 lines) and inspect it using `less`, practicing scrolling and searching for a specific line.
4. Create a "data" file inside `data/` with a header-like first line followed by several data-like lines, and use `head` to inspect only its beginning.
5. Create a "log" file inside `logs/` with several normal lines followed by a final line reading something like `ERROR: process failed`, and use `tail` to inspect only its end.
6. For each of the four files above, write one sentence explaining *why* you chose that particular command for that particular file — this is the actual point of the exercise.
7. Simulate investigating a failure: without reading the entire log file, use `tail` to find the error line, and state what command (and options) you used to find it fastest.
8. Once finished, safely remove the entire disposable project directory, and confirm with `ls` that it no longer exists.

**Success criteria:** for every file, you can justify — before running the command — why `cat`, `less`, `head`, or `tail` was the right choice, based on the file's size and what you needed to learn from it.

---

## 22. Review

Key terms and commands from this lesson:

- **File viewing** — reading a file's contents without modifying it.
- **`cat`** — displays an entire file's contents at once; named for "concatenate."
- **`less`** — a pager; displays a file interactively, one screen at a time, with scrolling and search.
- **`head`** — shows the beginning of a file (default: first 10 lines; `-n` to choose a count).
- **`tail`** — shows the end of a file (default: last 10 lines; `-n` to choose a count).
- **`tail -f`** — continuously watches a file and prints new lines as they're appended, until manually stopped with `Ctrl+C`.
- **Standard output** — the default channel these commands write their results to, which your terminal displays.
- **Text vs. binary** — text files are safe and meaningful to view with these commands; binary files are not.
- **Safe inspection** — none of these four commands modify the file being viewed.
- **Debugging use case** — file viewing is frequently the first step in investigating a failure, especially via `tail` on logs.

Compact command reference:

| Command | Shows | Default amount | Best for |
|---|---|---|---|
| `cat file` | Entire file | Everything | Small files |
| `less file` | Interactive, scrollable view | One screen at a time | Large or unfamiliar files |
| `head file` / `head -n N file` | Beginning | 10 lines | Headers, first rows, early config |
| `tail file` / `tail -n N file` | End | 10 lines | Recent logs, final results, errors |
| `tail -f file` | End, then live updates | Continuous, until stopped | Watching an actively growing log |

Decision guide — "If I need X, use Y":

- If I need to see a **small file, completely** → `cat`
- If I need to **browse a large file at my own pace** → `less`
- If I need to see **how a file starts** → `head`
- If I need to see **how a file ends, or its most recent content** → `tail`
- If I need to **watch a file grow in real time** → `tail -f`

---

## 23. Interview / Architecture Questions

1. What's the practical difference between `cat` and `less`, and when would choosing the wrong one become a real problem?
2. Why is `less` generally a safer default than `cat` when you don't yet know how large a file is?
3. What's the difference in purpose between `head` and `tail`?
4. Why is `tail` specifically so commonly reached for when investigating logs, compared to `head` or `cat`?
5. What does `tail -f` actually do, and why does it not exit on its own the way `head` or a plain `tail` does?
6. Why does file-viewing capability matter disproportionately in production debugging, compared to, say, local development on a personal machine with a graphical file explorer?
7. Why can blindly running `cat` on a very large file be a genuine problem, beyond just being visually inconvenient?
8. How can an incorrect assumption about the current working directory lead to inspecting the wrong file entirely, even when the command itself is typed correctly?
9. Conceptually, what happens between typing `cat file.txt` and seeing its contents appear in your terminal?
10. If a training run or evaluation job fails, how would an AI engineer use `tail` (and possibly `less`) to begin investigating what went wrong, without needing to open every file from the start?
11. Why do production systems generally move toward structured logging and dedicated observability tools rather than relying solely on engineers manually running `tail`/`less` against raw log files?

---

## 24. Production Application

The same four commands remain genuinely useful in production contexts, typically as the *first* step of an investigation:

- **Investigating service logs** — `tail -f` on a live service's log while reproducing or observing an issue.
- **Checking deployment artifacts** — `cat`/`less` on a manifest or packaged file to confirm exactly what was deployed.
- **Inspecting configuration** — `cat` on a configuration file actually loaded by a running service, to confirm it matches what was intended.
- **Inspecting batch job output** — `tail` on a batch job's output or log to check its final status quickly.
- **Checking ML experiment results** — `head`/`tail`/`less` on results files to spot-check outcomes without needing a full analysis tool.
- **Inspecting evaluation reports** — `less` for reports too long to comfortably `cat`.
- **Investigating failed data processing** — `tail` a processing log to find the specific point of failure quickly.
- **Inspecting generated artifacts** — a quick `cat`/`head` sanity check that a generation step actually produced sensible output.

As systems grow, production engineers combine this kind of manual file inspection with **logging** (structured, systematic recording of events), **observability** (broader visibility into a running system's health and behavior), **automation** (scripted or scheduled checks rather than manual commands), **structured data processing** (extracting and analyzing log/data content programmatically rather than reading it line by line), and **monitoring** (continuous, automatic detection of problems). None of these are taught in depth in this lesson — the point here is only to establish that `cat`, `less`, `head`, and `tail` remain the foundational, always-available layer underneath all of that tooling: even with the most sophisticated observability platform in place, engineers still frequently drop into a terminal and run `tail` on a raw log file to see, directly and immediately, what actually happened.

---

## 25. Relationship to Module 0.2 and Earlier Module 0.3 Lessons

This lesson's four commands build directly on concepts already introduced:

**From Module 0.2:**
- **Filesystem** — file-viewing commands read data that the filesystem tracks the location of.
- **Permissions** — determine whether you're allowed to read a given file at all (Section 16's "Permission denied" scenario); full permissions administration is covered later in this module.
- **Processes** — each viewing command runs as its own short-lived process, exactly like the commands from Lesson 02.
- **Shell** — parses the command and resolves the file's path before the program itself runs.
- **Standard input/output** — the channel through which these commands' results reach your terminal (Section 11).

**From earlier Module 0.3 lessons:**
- **Navigation (Lesson 01)** — knowing your current working directory and how relative/absolute paths resolve is exactly as important here as it was for `cd`, `cp`, `mv`, and `rm`.
- **File operations (Lesson 02)** — you now have the tools to create, copy, move, and delete files (Lesson 02) *and* to see what's actually inside them (this lesson) — together, a complete basic toolkit for working with files at the command line.

The conceptual flow tying these together:

```text
Navigate (Lesson 01)
    → locate the file
File operations (Lesson 02)
    → understand what you're working with, arrange it as needed
File viewing (this lesson)
    → inspect what's actually inside it
    → diagnose what you find
```

This lesson does not re-teach `pwd`, `ls`, `cd`, `mkdir`, `cp`, `mv`, or `rm` — it assumes that foundation and builds directly on top of it.

---

## 26. Scope Boundary

This lesson deliberately does **not** teach, in depth:

- `grep`, `find` (searching — later lessons)
- `sort`, `uniq`, `cut` (text processing — later lessons)
- `xargs`, pipes, redirection (later lessons)
- environment variables (later lesson)
- shell scripting (later lesson)
- permissions administration in depth (later lesson — this lesson only references permissions conceptually, as inherited from Module 0.2)
- advanced filesystem internals
- log aggregation systems, observability platforms, or structured logging frameworks
- Docker, Kubernetes, or cloud logging systems
- Python (or any language's) file-processing APIs

These are separate roadmap topics and stages, mentioned here only where necessary for context (for example, in the real-world and production sections). This lesson is not a preview course for any of them.

---

_This lesson is complete. It covers `cat`, `less`, `head`, and `tail` (including `tail -f`) only. The remaining Module 0.3 topics are covered in subsequent lessons within this module._
