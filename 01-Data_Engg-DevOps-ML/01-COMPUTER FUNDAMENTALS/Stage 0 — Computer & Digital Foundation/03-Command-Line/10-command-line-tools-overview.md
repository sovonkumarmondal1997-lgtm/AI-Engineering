# Module 0.3 — Command Line

# Lesson 10 — Command-Line Tools Overview

**Module:** Command Line
**Roadmap reference:** Stage 0 — Module 0.3 — Command Line (final lesson)
**Concept(s) covered:** integration of every Module 0.3 topic — navigation, file operations, viewing, searching, text processing, pipes/redirection, environment variables, shell scripts, permissions
**Status:** Complete
**Builds on:** 01–09 (all of Module 0.3) and Module 0.2 (processes, filesystem, shell, standard I/O)

---

## 1. Learning Objectives

After completing this lesson you will be able to:

- Recall, at a glance, every command and concept taught across Module 0.3, and which category each belongs to.
- Explain how the nine categories of command-line capability (navigate, inspect, locate, read, transform, connect, configure, automate, control access) relate to and build on one another.
- Given an unfamiliar command-line task, reason through a fixed sequence of questions to decide which tool or combination of tools is appropriate.
- Read and predict the behavior of a short, multi-command workflow combining several Module 0.3 tools at once.
- Diagnose a failure in a combined workflow by isolating which stage or which category of tool is actually responsible.
- Explain the trade-offs between doing something manually at the prompt versus scripting it, and between a simple tool and a more complex one.
- Explain why this entire toolkit remains foundational to later software engineering and Applied AI Engineering work, even after you learn more powerful tools.
- Self-assess your own command-line capability against a concrete completion checklist for all of Module 0.3.

---

## 2. Roadmap Alignment

This lesson is the **final lesson of Module 0.3 — Command Line**, itself part of **Stage 0 — Computer & Digital Foundations**. Its job is different from every lesson before it: instead of teaching a new command or concept, it **integrates, consolidates, and applies** everything Module 0.3 has already taught.

The roadmap's Module 0.3 topics — every one of which has already been taught in a dedicated lesson — are:

```text
pwd, ls, cd
cp, mv, rm, mkdir
cat, less, head, tail
grep, find
sort, uniq, cut, xargs
pipes, redirection
environment variables
shell scripts
permissions
```

The Module 0.3 lesson progression:

```text
01 Navigation
   ↓
02 File Operations
   ↓
03 Viewing Files
   ↓
04 Searching
   ↓
05 Text Processing
   ↓
06 Pipes and Redirection
   ↓
07 Environment Variables
   ↓
08 Shell Scripts
   ↓
09 Permissions
   ↓
10 Command-Line Tools Overview (this lesson)
```

**Why this sequence exists, and how each lesson built on the last:**

- **01 Navigation** came first because every other command needs to know *where it's operating* — you can't sensibly copy, search, or run anything without first understanding the current working directory and paths.
- **02 File Operations** built on navigation immediately, because once you can find your way around, the next natural need is to actually create, move, and remove things.
- **03 Viewing Files** followed, because once files exist and are organized, you need to look inside them.
- **04 Searching** built on viewing — once you can look inside one file, the next question is "which file, out of many, has what I need?"
- **05 Text Processing** built on searching — once you've located relevant content, you often need to reorder, deduplicate, or extract pieces of it.
- **06 Pipes and Redirection** connected everything before it — the tools from 01–05 stopped being isolated commands and became composable building blocks.
- **07 Environment Variables** introduced process-level configuration — a different kind of context, alongside the current directory, that shapes how commands and programs behave.
- **08 Shell Scripts** combined 01–07 into saved, repeatable procedures.
- **09 Permissions** explained the access-control layer that had been silently present underneath every single command since Lesson 01 — why some operations succeed and others don't.
- **10 (this lesson)** does not add a new command. It teaches you to **see the whole toolkit as one connected system**, and to reason about which pieces to reach for, in combination, for a real task.

This lesson does not invent any additional roadmap topics beyond the list above — everything discussed here was already taught in Lessons 01–09.

---

## 3. Prerequisites

This lesson assumes you have completed Lessons 01–09 and are comfortable with the individual commands and concepts each one taught: `pwd`/`ls`/`cd`; `cp`/`mv`/`rm`/`mkdir`; `cat`/`less`/`head`/`tail`; `grep`/`find`; `sort`/`uniq`/`cut`/`xargs`; pipes (`|`) and redirection (`>`, `>>`, `<`, `2>`, `2>&1`); environment variables and `export`; shell scripts (shebang, arguments, variables, conditionals, loops, functions); and permissions (`rwx`, `chmod`, ownership).

**This lesson does not re-teach any individual command from scratch.** Where a command is mentioned, it's treated as already-known vocabulary being put to integrated use — if any of it feels unfamiliar, that's a signal to revisit the specific earlier lesson, not something this lesson will re-explain in depth.

---

## 4. What This Final Lesson Is About

Every prior Module 0.3 lesson taught you **one category** of capability in isolation. This lesson is not "one more category" — it's the lesson where those nine categories stop being nine separate things you memorized in sequence, and become **one coherent way of thinking about the command line**.

Concretely, this lesson's job is to help you answer a question you'll face constantly for the rest of this roadmap: **"I have a command-line task in front of me — which tool, or combination of tools, do I actually reach for?"** Every prior lesson answered "how does this one tool work?" This lesson answers "how do I *choose*, *combine*, and *debug* across all of them?"

---

## 5. The Complete Command-Line Mental Model

Recall the individual mental models from each earlier lesson — this section places them all on one shared map.

```text
NAVIGATE     (Lesson 01)   → where am I, and how do I move around?
    ↓
FILE OPERATIONS (Lesson 02) → create, copy, move, remove filesystem objects
    ↓
READ         (Lesson 03)   → look inside a file's contents
    ↓
LOCATE       (Lesson 04)   → find files, or find content, when I don't already know where
    ↓
TRANSFORM    (Lesson 05)   → reorder, deduplicate, extract pieces of text
    ↓
CONNECT      (Lesson 06)   → compose commands together; control where output goes
    ↓
CONFIGURE    (Lesson 07)   → adjust behavior via the process environment
    ↓
AUTOMATE     (Lesson 08)   → save a sequence of steps as a repeatable script
    ↓
CONTROL ACCESS (Lesson 09) → understand who/what is allowed to do any of the above
```

**Read this diagram as a rough, common *order of operations* for a new task, not a rigid law.** In practice, real work jumps around this diagram constantly — you might check permissions before transforming data, or configure an environment variable before navigating anywhere. But when you're lost on where to even start, walking down this list in order — "do I know where I am? do I know what exists? have I looked inside it? do I need to find something? does it need reshaping? should I chain steps together? does behavior depend on configuration? should this be saved as a script? am I actually allowed to do this?" — is a reliable way to locate the right tool.

**The single most important idea in this entire lesson:** none of these nine categories replaced any other. `find` (LOCATE) didn't make `ls` (NAVIGATE) obsolete; `chmod` (CONTROL ACCESS) didn't replace anything about `cp` (file operations). Each category answers a genuinely different question, and real command-line work draws on several of them, together, for almost any nontrivial task.

---

## 6. The Module 0.3 Command-Line Toolkit

| Command/Topic | What it does | When you use it | Typical input | Typical output/effect | Category | Key risk/mistake |
|---|---|---|---|---|---|---|
| `pwd` | Prints the current working directory | Whenever you're unsure where you are | none | An absolute path | Navigate | Assuming you know your location without checking |
| `ls` | Lists directory contents | To see what exists before acting | a path (optional) | Filenames/directories | Navigate | Forgetting `-la` and missing hidden files |
| `cd` | Changes the current working directory | To move somewhere else | a path | Updates your shell's location | Navigate | Losing track of location after several `cd`s |
| `cp` | Copies a file/directory | To duplicate without destroying the original | source + destination | A new copy | File operations | Forgetting `-r` for directories; silent overwrite |
| `mv` | Moves or renames a file/directory | To relocate or rename | source + destination | Source disappears, destination appears | File operations | Confusing with `cp`; accidental rename |
| `rm` | Removes files; directories normally require a recursive option such as `rm -r` | To remove something no longer needed | a path | Irreversible removal | File operations | `rm -rf` with no confirmation; wrong path |
| `mkdir` | Creates a directory | To set up structure before adding files | a path | A new, empty directory | File operations | Forgetting `-p` for nested paths |
| `cat` | Prints an entire file | Small files, quick full view | a file | Full contents to stdout | Viewing | Using it on very large files |
| `less` | Interactively pages through a file | Large or unfamiliar files | a file | An interactive, scrollable view | Viewing | Not knowing `q` to exit |
| `head` | Shows the beginning of a file | Checking headers, first rows | a file (+ `-n`) | First N lines | Viewing | Assuming it shows "a representative sample" |
| `tail` | Shows the end of a file | Recent logs, final results | a file (+ `-n`/`-f`) | Last N lines, or live updates | Viewing | Forgetting `-f` runs until stopped |
| `grep` | Searches file **content** for a pattern | "Does anything say X?" | a pattern + file(s)/dir | Matching lines | Locate | Confusing with `find`; case sensitivity |
| `find` | Searches the **filesystem** by name/type | "Where is/are file(s) named/typed X?" | a starting path + conditions | Matching paths | Locate | Unquoted wildcards expanding early |
| `sort` | Reorders lines | Before deduplicating, or for readability | lines of text | Reordered lines | Transform | Textual vs. numeric (`-n`) sorting |
| `uniq` | Collapses **adjacent** duplicate lines | After sorting, to deduplicate/count | sorted lines | Deduplicated lines, optionally counted | Transform | Assuming it finds non-adjacent duplicates |
| `cut` | Extracts a field or character range | Simple, consistently delimited text | delimiter + field/lines | One column/slice per line | Transform | Assuming it understands complex CSV |
| `xargs` | Builds and runs a command from input items | Applying a command to many items at once | lines/words of input | Executes a constructed command | Transform | Pairing with a mutating command on untrusted input; ordinary whitespace-delimited `xargs` is not safe for arbitrary filenames containing whitespace/newlines (safer: `find -exec … {} +` or `find -print0 \| xargs -0`) |
| `\|` (pipe) | Connects one command's stdout to another's stdin | Combining tools without an intermediate file | two commands | A live stream between processes | Connect | Assuming stderr is piped too |
| `>` / `>>` / `<` / `2>` / `2>&1` | Redirects stdin/stdout/stderr to/from files | Saving output, separating errors, feeding input | a command + a file | A file is read/written | Connect | `>` silently overwrites; `2>&1` ordering |
| Environment variables / `export` | Configuration attached to a process's environment | Making behavior vary by environment, safely | `NAME=value` (+ `export`) | Available to child processes | Configure | Forgetting `export`; assuming persistence |
| Shell scripts | A saved sequence of shell commands | Repeating a procedure reliably | a `.sh` file | Runs the same steps every time | Automate | Missing shebang/execute permission; unquoted variables |
| Permissions (`rwx`, `chmod`, ownership) | Access-control rules on filesystem objects | Understanding/fixing "permission denied" | a file/directory | Allow/deny for a given identity | Control access | `chmod 777` as a false "fix" |

This table is a **map back to Lessons 01–09**, not a replacement for them — each row is intentionally brief; the full explanation, mechanics, and nuance for every item lives in its dedicated lesson.

---

## 7. Tool Categories

Restating Section 5's model as an explicit grouping, since this is the structure the rest of this lesson (especially Section 11's decision-making section) relies on:

| Category | Lessons | Central question it answers |
|---|---|---|
| **Navigate** | 01 | Where am I, and how do I get somewhere else? |
| **File operations** | 02 | How do I create, duplicate, relocate, or remove things? |
| **Read** | 03 | What's actually inside this file? |
| **Locate** | 04 | Where is it, or where does this text appear, when I don't already know? |
| **Transform** | 05 | How do I reorder, deduplicate, or extract pieces of text I've found? |
| **Connect** | 06 | How do I combine tools, and control where their output goes? |
| **Configure** | 07 | How does a process's behavior vary based on its environment? |
| **Automate** | 08 | How do I save a procedure so it's reliably repeatable? |
| **Control access** | 09 | Who/what is actually allowed to do any of the above, and why did something just get denied? |

---

## 8. How Commands Work Together

Individual commands are useful; **combinations** of them are where real command-line work actually happens. A few representative combinations, each explicitly citing which categories and which earlier lessons it draws from:

**Locate + limit/display results:**
```bash
find . -name "*.log" | head
```
Locate (04) finds candidate files; Connect (06) pipes the list of pathnames into `head`, which limits/displays the first results (it does not read the files' contents).

**Locate + Transform + Connect:**
```bash
grep "ERROR" app.log | sort | uniq -c
```
Locate (04) filters; Transform (05) orders and counts identical matching lines; Connect (06) links the three stages and could redirect the final result to a file.

**Configure + Automate:**
```bash
export APP_ENV=production
bash deploy-check.sh
```
Configure (07) sets behavior; Automate (08) runs a saved procedure that reads it.

**Automate + Control access:**
```bash
chmod +x setup.sh
./setup.sh
```
Control access (09) grants the specific permission Automate (08) depends on for direct execution.

**File operations + Control access:**
```bash
mkdir -p project/data
chmod 700 project/data
```
File operations (02) creates structure; Control access (09) immediately scopes who can touch it.

**The pattern across every example above:** a real task is almost never "one command from one category." It's a short **sequence**, drawing from two, three, or more categories, each contributing exactly what it's good at.

---

## 9. Integrated Workflow Thinking

A repeatable way to approach an unfamiliar command-line task, tying directly back to Section 3's Primary Objective questions:

```text
1. Where am I?                          → Navigate
2. What exists here?                    → Navigate / File operations
3. Do I need to create/move/remove?      → File operations
4. Do I need to see inside a file?       → Read
5. Do I need to find something?          → Locate
6. Do I need to reorganize/extract text? → Transform
7. Do I need to combine steps?           → Connect
8. Does behavior depend on config?       → Configure
9. Should this be saved and reused?      → Automate
10. Am I actually allowed to do this?    → Control access
11. What could go wrong, and how would I notice? → Debugging (Section 15)
```

Walking through these questions **in this order**, for any new task, is the practical payoff of this entire lesson. You don't need to consciously recite all eleven every time — but when you're stuck, this list is the systematic fallback.

**Worked example — "I need to find every error in yesterday's logs, and save a clean summary."**

1. Where am I? → `pwd` to confirm.
2. What exists? → `ls logs/`.
3. Create/move/remove? → not yet.
4. See inside a file? → `less logs/app.log` for a first look.
5. Find something? → `grep -i "error" logs/app.log`.
6. Reorganize/extract? → pipe into `sort | uniq -c`.
7. Combine steps? → the pipeline itself: `grep -i "error" logs/app.log | sort | uniq -c`.
8. Config-dependent? → maybe, if the log path comes from an environment variable.
9. Save and reuse? → if you'll do this again tomorrow, wrap it in a shell script.
10. Allowed to do this? → confirm you have read access to `logs/app.log`.
11. What could go wrong? → wrong file, case-sensitivity, or a permission issue — Section 15 covers exactly these.

---

## 10. Internal Mechanics

This lesson does not introduce new internal mechanics — it consolidates what Lessons 01–09 already established, because an integrated workflow is still just several individual commands, one after another, each following the same model:

```text
Terminal → Shell → command → process → operating system → filesystem/environment → output/exit status
```

- The **shell** (Lesson 01) parses each command, resolving paths and expanding wildcards.
- Not every command is a separate process. External commands normally execute in a separate execution environment/process (Module 0.2), inheriting a **copy** of the current environment (Lesson 07) at the moment they start, while shell builtins (like `cd`) and shell functions can execute within the current shell. Pipeline elements normally execute in separate execution contexts/processes, although exact behavior can depend on the shell.
- **Pipes** (Lesson 06) connect one process's stdout directly to another's stdin; **redirection** (Lesson 06) connects a process's stdin/stdout/stderr to a file instead.
- Every filesystem operation a process attempts is checked against **permissions** (Lesson 09) — the process's identity versus the target's owner/group/others bits.
- Every command reports an **exit status** (Lessons 04, 06, 08) when it finishes — the signal that lets a script, or a human, know whether it actually succeeded.

**The integrated insight this section adds:** a multi-stage workflow is not one new kind of "thing" the operating system understands specially — it's simply several of these individual process lifecycles, chained or sequenced by the shell, each one following exactly the same rules you already learned, one lesson at a time.

---

## 11. Command Selection and Decision Making

A practical decision table, mapping common task phrasing to the right category and starting point:

| If your task sounds like... | Reach for... | Category |
|---|---|---|
| "Where am I / what's here?" | `pwd`, `ls` | Navigate |
| "I need a new folder/file, or to move/copy/delete something." | `mkdir`, `cp`, `mv`, `rm` | File operations |
| "I need to see what's inside this one file." | `cat`, `less`, `head`, `tail` | Read |
| "I don't know which file has this, or where a file is." | `grep`, `find` | Locate |
| "I have the right lines, now I need them ordered/deduplicated/one column." | `sort`, `uniq`, `cut` | Transform |
| "I need to apply a command to a list of items." | `xargs` | Transform |
| "I need to feed one command's result into another, or save output." | `\|`, `>`, `>>`, `<` | Connect |
| "Behavior should differ between setups without editing code." | environment variables | Configure |
| "I'll be doing this exact sequence again." | shell script | Automate |
| "Something says 'Permission denied,' or I need to restrict access." | `chmod`, ownership reasoning | Control access |

**A decision-making principle, restated from Lesson 04's `grep`-vs-`find` discussion and generalized:** ask what *kind* of question you're actually asking (location? content? order? access?) before reaching for a command — matching the *question* to the *category*, rather than guessing at a command name, is what this whole table is meant to train.

---

## 12. Bash / Git Bash / WSL2 / PowerShell

Restating, once, the cross-platform position established consistently across Lessons 01–09:

- **Bash on Linux** is this module's — and this entire roadmap's early stages' — primary, reference environment. Every command and example in this lesson is Bash syntax.
- **WSL2** provides a genuine Linux environment on Windows; everything in this lesson applies identically inside it, with the one caveat (repeated in Lessons 02, 04, 08, and 09) that crossing the Windows/Linux filesystem boundary (`/mnt/c/...`) can introduce path, performance, or permission differences worth being aware of.
- **Git Bash** provides a Bash-like environment on Windows; the commands in this lesson generally behave the same way there, with filesystem-permission behavior specifically noted (Lesson 09) as an area where it can diverge from native Linux.
- **PowerShell** is a **genuinely different** shell — a different syntax, a different (partly object-oriented) pipeline model, and a different permission/security model. This lesson does not teach PowerShell in depth, and — consistent with every earlier lesson — makes no claim that Bash syntax runs unchanged in PowerShell.

This lesson does not add any new cross-platform detail beyond what Lessons 01–09 already established — it only restates the consistent position: **learn Bash/Linux as the primary model; recognize that other shells provide similar capability through genuinely different syntax.**

---

## 13. Safe Practical Demonstrations

Everything below uses a **disposable, learner-created practice area** — for example, `/tmp/module-0-3-overview-demo/`. **This lesson does not create this directory for you.** No command below has actually been executed by this lesson; every result shown is explicitly labeled `Example output:` — an illustration of expected behavior, never a captured result. Nothing here modifies the real Applied AI Engineering project, uses `sudo`, or touches any file outside this disposable area.

**Setup:**
```bash
mkdir -p /tmp/module-0-3-overview-demo/logs
cd /tmp/module-0-3-overview-demo
```

**Demonstration 1 — Navigate + File operations + Read**
```bash
pwd
mkdir -p data
printf "one\ntwo\nERROR: disk full\nthree\n" > logs/app.log
cat logs/app.log
```
Example output:
```text
/tmp/module-0-3-overview-demo
one
two
ERROR: disk full
three
```

**Demonstration 2 — Locate + Transform + Connect**
```bash
grep -i "error" logs/app.log | sort | uniq -c > data/error-summary.txt
cat data/error-summary.txt
```
Example output:
```text
      1 ERROR: disk full
```

**Demonstration 3 — Configure + Automate**
```bash
cat > scripts_check.sh <<'EOF'
#!/usr/bin/env bash
echo "Environment: ${APP_ENV:-unset}"
EOF
chmod +x scripts_check.sh
export APP_ENV=development
./scripts_check.sh
```
Example output:
```text
Environment: development
```

**Demonstration 4 — Control access**
```bash
chmod 600 data/error-summary.txt
ls -l data/error-summary.txt
```
Example output:
```text
-rw------- ... ... ... ... data/error-summary.txt   (owner, group, size and timestamp vary by environment)
```

**Cleanup:**
```bash
cd /tmp
rm -r /tmp/module-0-3-overview-demo
```

---

## 14. Common Mistakes and Misconceptions

1. **Treating each command as an isolated trick, rather than part of a system.** The value comes from combination (Section 8), not memorized one-liners.
2. **Reaching for `grep` when the real question is about filenames, not content** (should be `find`) — restated from Lesson 04.
3. **Assuming a pipeline "worked" because it produced output**, without checking whether an earlier stage actually failed silently (Lesson 06).
4. **Forgetting `export`**, then being confused why a script or child process can't see a variable (Lesson 07).
5. **Assuming `./script.sh` and `bash script.sh` have identical requirements** — only the former needs execute permission (Lessons 08–09).
6. **Reaching for `chmod 777`** as a generic fix for any permission error, instead of diagnosing the actual identity/target mismatch (Lesson 09).
7. **Not checking `pwd` before a destructive or redirecting command**, and acting on the wrong file (Lessons 01–02, 06).
8. **Assuming `uniq` finds all duplicates** without sorting first (Lesson 05).
9. **Assuming `cut` can parse arbitrary, quoted, or irregular CSV** (Lesson 05).
10. **Unquoted variables or wildcards inside a script**, causing unexpected word-splitting (Lessons 05, 08).
11. **Skipping the "what could go wrong" step** entirely, and being surprised by a failure that a moment's thought would have anticipated.
12. **Assuming a workflow that works manually will work identically when automated or run by a different identity/service** (Lessons 07–09).
13. **Building an overly long, cryptic one-liner** instead of a few clear, testable steps (Lesson 06's readability principle).
14. **Assuming Bash syntax works unchanged in PowerShell**, or that WSL2 is identical to native Linux in every case (Section 12).
15. **Never testing a combined workflow against more than the one "happy path" input** before trusting it (Lesson 08's testing habit).

---

## 15. Debugging Exercises

Work through each scenario's reasoning before reading the diagnosis.

**Scenario 1 — Pipeline produces no output**
- *Situation:* `grep "ERROR" app.log | sort | uniq -c` produces nothing.
- *Diagnose:* test each stage independently, starting with `grep "ERROR" app.log` alone (Lesson 06's isolation habit).
- *Likely cause:* wrong filename, wrong current directory, or a case-sensitivity mismatch (Lessons 01, 04).
- *Fix:* correct the path or add `-i`.

**Scenario 2 — Script can't see an exported variable**
- *Situation:* `export APP_ENV=development` then `./check.sh` reports "unset."
- *Diagnose:* confirm the export happened *before* the script started (Lesson 07's inheritance timing), and that the script actually reads `APP_ENV` (not a typo).
- *Fix:* re-export, then re-run; or fix the variable name.

**Scenario 3 — `./script.sh` fails but `bash script.sh` works**
- *Situation:* one execution form fails, the other doesn't.
- *Diagnose:* `ls -l script.sh` — check for the execute bit (Lessons 08–09).
- *Fix:* `chmod +x script.sh`.

**Scenario 4 — File exists, but a command can't read it**
- *Situation:* `cat data/results.txt` reports "Permission denied," even though `ls` shows the file.
- *Diagnose:* `ls -l` for the file's permissions *and* every parent directory's execute bit; `whoami`/`id`/`groups` for your identity (Lesson 09).
- *Fix:* correct the specific missing bit for the applicable category.

**Scenario 5 — Wildcard matches more than expected**
- *Situation:* `for f in *.log; do ...; done` processes an unintended file.
- *Diagnose:* run the equivalent `ls *.log` first, separately, to see the real match set (Lessons 04–05, 08).
- *Fix:* narrow the pattern or directory before trusting it inside a loop.

**Scenario 6 — Redirected output overwrote something important**
- *Situation:* `command > results.txt` destroyed prior content you needed.
- *Diagnose:* recall `>` always overwrites, with no warning (Lesson 06).
- *Fix:* going forward, use `>>` deliberately when appending is intended, and double-check the destination before using `>`.

**Scenario 7 — A workflow works for you but fails for a service**
- *Situation:* you can read a model file manually; a service running under a different identity cannot.
- *Diagnose:* "exists for me" ≠ "accessible to that process's identity" (Lesson 09, Section 21's identity-mismatch lesson).
- *Fix:* check permissions against the service's actual identity, not your own.

**Scenario 8 — A long combined command fails and it's unclear where**
- *Situation:* `find . -name "*.csv" -exec grep "error" {} + | sort | uniq -c > out.txt` produces an empty `out.txt`. (`find -exec … {} +` is used here rather than `find | xargs`, because ordinary whitespace-delimited `xargs` can split filenames containing spaces or newlines.)
- *Diagnose:* break the chain apart, testing `find`, then `find -exec grep`, then adding `sort`, one stage at a time (Section 8's composition model, applied backward for debugging).
- *Fix:* whichever isolated stage first shows the wrong (or no) result is where the actual problem lives.
- *Bash note:* by default, a Bash pipeline's exit status is normally the status of the final command, so an earlier stage can fail while the pipeline still reports success. `set -o pipefail` makes a pipeline report failure when an earlier component fails, rather than relying only on the final command's status.

**Scenario 9 — Directory traversal blocks access to a file with fine permissions**
- *Situation:* a file shows `-rw-r--r--` (looks readable) but access still fails.
- *Diagnose:* check every directory in the path for missing execute (`x`) permission (Lesson 09, Section 6).
- *Fix:* correct the directory's `x` bit, not the file's own bits.

**Scenario 10 — A script that worked locally fails elsewhere**
- *Situation:* the same script fails on a different machine or environment.
- *Diagnose:* look for a hard-coded, machine-specific path, or an environment variable assumed to be set that wasn't (Lessons 07–08).
- *Fix:* replace the assumption with an argument, a documented required variable, or a relative/portable path.

---

## 16. Real-World Software Engineering Applications

- **Onboarding into an unfamiliar codebase** — Navigate + Read + Locate, in sequence, is exactly how most engineers orient themselves in a new project before reading any documentation.
- **Debugging a failing build** — Read + Locate (find the build log, then search it) + Transform (isolate just the error lines).
- **Preparing a release** — File operations + Automate (a script that assembles the right files) + Control access (ensuring the right permissions on what's produced).
- **Investigating a production incident** — Locate + Read + Transform on logs, exactly the combined pattern from Section 8, often under real time pressure — which is precisely why fluency across categories (not just knowing individual commands) matters.
- **Setting up a new development environment** — Configure + Automate, so the same setup works consistently for every new contributor.

---

## 17. Applied AI Engineering Applications

Using the same representative project layout from earlier lessons:

```text
ai-project/
├── data/
├── models/
├── configs/
├── logs/
└── evaluations/
```

- **Dataset investigation:** Navigate to `data/`, Locate the relevant files (`find`), Read a sample (`head`), Transform to check for duplicate labels (`sort | uniq -c`) — the exact combined workflow from Lesson 05's mini-project, now recognized as spanning four categories at once.
- **Training run diagnostics:** Locate the right log (`find`), Read/Locate within it (`tail`, `grep`), Transform to summarize repeated errors — Lesson 06's mini-project, revisited.
- **Environment-driven model selection:** Configure (`MODEL_NAME`, `APP_ENV`) read by an Automate-layer script that then runs the actual training/inference command — Lessons 07–08 combined.
- **Protecting model artifacts:** Control access ensuring only the right identity can overwrite a validated checkpoint — Lesson 09's central AI-relevant example.
- **A full evaluation pipeline, end to end:** Navigate → Locate inputs → Read/Transform intermediate results → Connect stages with pipes/redirection → Configure via environment variables → Automate the whole thing as a script → Control access on the final report. This single sentence touches every category in this module, in the order Section 5's mental model lays them out — which is exactly the point of this final lesson.

**Failure modes this integration prevents, restated from earlier lessons:** using the wrong dataset because of a navigation mistake (01); editing the wrong config because of an incorrect search (04); silently continuing past a failed pipeline stage (06); a service failing to load a model due to a permission mismatch, not a missing file (09). Every one of these is a *combination*-level failure, not a single-command failure — which is why this lesson's integrated view, not just the individual lessons, matters for catching them.

---

## 18. Trade-offs and Engineering Practices

- **Manual, one-off commands vs. a saved script** — manual is fine for exploration; anything repeated deserves to become a script (Lesson 08).
- **A simple tool vs. a more powerful one** — `cut` is fast and simple for clean, predictable data, but a real parser (a later-roadmap topic) is correct for messy or complex structured data (Lesson 05).
- **A short pipeline vs. a long one** — composability is powerful, but an overly long chain becomes hard to debug (Lesson 06); prefer a few clear, testable stages.
- **Broad access vs. scoped access** — `chmod 777` "solves" an error today at the cost of removing all access control (Lesson 09); least privilege is the durable habit.
- **Convenience vs. safety** — every "quick fix" this module warned against (`sudo` reflexively, `chmod 777`, skipping quoting, ignoring exit status) trades a small amount of friction now for real risk later.

**The overall engineering practice this whole module has been building toward:** default to the narrowest, most understandable tool that solves the actual problem; check assumptions (location, identity, permissions, exit status) rather than guessing; and prefer a few clear steps you can test independently over one clever, opaque command.

---

## 19. Practical Exercises

All practical work should be done inside your own disposable directory, using only harmless placeholder content. Never modify the real Applied AI Engineering project.

### Level 1 — Recognition

1. Which category does `find` belong to: Locate, or Read?
2. Which category does `chmod` belong to?
3. Which two commands together form the "Transform" category's deduplication pattern?
4. Which symbol connects one command's stdout to another's stdin?
5. Which lesson introduced `export`?
6. Which category does a shell script itself belong to?
7. Name one command from the "Navigate" category and one from "File operations."
8. Is `grep` a Locate tool or a Transform tool?

### Level 2 — Understanding

1. Explain, in your own words, why `find` came before `sort`/`uniq`/`cut` in the Module 0.3 sequence.
2. Explain why permissions (Lesson 09) apply to "every command since Lesson 01," even though it was taught last.
3. Given a task described only as "summarize how often each error occurs in this log," name the categories (not commands) it involves.
4. Explain why a script that works manually might fail when automated or run by a different identity.
5. Explain the difference between debugging a single command and debugging a multi-stage pipeline.
6. Why is "the pipeline produced some output" not sufficient evidence that every stage succeeded?
7. Explain why `chmod 777` is a bad general answer to a permission error, using this lesson's category model.
8. Explain, using Section 9's ordered questions, how you'd start investigating an unfamiliar project directory.

### Level 3 — Application

1. Build a disposable workspace and use Navigate + File operations to create a small structure.
2. Create a sample log file and use Read + Locate to find lines matching a keyword.
3. Extend the previous exercise with Transform (`sort | uniq -c`) to summarize matches.
4. Redirect that summary to a file using Connect (`>`).
5. Export a configuration variable and read it inside a small script (Configure + Automate).
6. Make that script executable and run it both as `bash script.sh` and `./script.sh`.
7. Set a restrictive permission (`600`) on one output file and confirm it with `ls -l` (Control access).
8. Combine at least four categories into one short, readable multi-line workflow, and write one sentence explaining each stage's purpose.

### Level 4 — Debugging

1. A pipeline you built produces no output — diagnose by testing each stage independently.
2. A script can't see an environment variable you're sure you set — determine why.
3. `./script.sh` fails but `bash script.sh` doesn't — fix it.
4. A file looks readable in `ls -l` but access still fails — check the directory chain.
5. A wildcard inside a loop matched more than intended — identify the missing verification step.
6. A redirect (`>`) destroyed content you needed — explain what should have been checked first.
7. A workflow that works for you fails for a "service" identity you simulate by reasoning about permissions — diagnose the mismatch.
8. A long combined command fails with an unclear cause — describe how you'd isolate the failing stage.

### Level 5 — Integration

1. Design and build a workflow that touches at least six of the nine categories from Section 7, using only disposable files.
2. Simulate a small "investigate a production incident" scenario using Locate + Read + Transform on a sample log you create.
3. Build a script that validates its own inputs, reads configuration from the environment, and reports a clear success/failure exit status.
4. Design a permission scheme for a small multi-file disposable workspace and justify each choice.
5. Write, in your own words, a one-paragraph explanation of how this entire module's toolkit will support your first real Python/AI-engineering project later in this roadmap.

---

## 20. Mini-Project — Module 0.3 Capstone: Command-Line Project Workspace

**Objective:** demonstrate integrated command-line capability across every category taught in this module, by building and operating a small, disposable, simulated project workspace from scratch.

**Scenario:** you've been handed a small, fake project. You need to organize it, locate and summarize relevant information, configure and automate a repeatable check, and secure the result — using nothing but what Module 0.3 taught.

**Setup (create this yourself; not created automatically by this lesson):**
```bash
mkdir -p /tmp/module-0-3-capstone/{data,logs,scripts,reports}
cd /tmp/module-0-3-capstone
```

**Tasks:**

1. **Navigate + File operations:** confirm your location (`pwd`), and create the structure above if you haven't already.
2. **Read:** create a small sample log in `logs/` with a mix of normal and `ERROR` lines, and view it fully.
3. **Locate:** find every `.log` file in the workspace using `find`.
4. **Transform:** filter, sort, and count identical matching error lines (`grep | sort | uniq -c`).
5. **Connect:** redirect that summary into `reports/error-summary.txt`.
6. **Configure:** export a variable (e.g. `REPORT_LEVEL=summary`) that a script will read.
7. **Automate:** write a script in `scripts/` that reads that variable, re-runs the filter/sort/count step, and reports its own exit status clearly.
8. **Control access:** make the script executable; set the report file to `644` (readable, owner-writable) and explain why that's appropriate here.
9. **Debug:** deliberately break one thing (an unexported variable, a missing execute bit, or a wrong path) and correctly diagnose and fix it using this lesson's methodology.
10. **Document:** write a short summary of which category each step belonged to, and why you sequenced them the way you did.

**Test cases:** run the script twice — once after `export APP_ENV=development`, then again after `unset APP_ENV` (so the two states are actually different in the same shell) — and confirm the behavior differs exactly as expected.

**Completion checklist:**
- [ ] Workspace structure created and confirmed with `pwd`/`ls`.
- [ ] Sample log created and read in full.
- [ ] `find` used to locate log files.
- [ ] `grep | sort | uniq -c` pipeline built and redirected to a report file.
- [ ] Configuration variable exported and read by a script.
- [ ] Script made executable and run both as `bash` and `./`.
- [ ] Report file's permissions deliberately set and justified.
- [ ] One deliberate failure introduced, diagnosed, and fixed.
- [ ] Workspace cleaned up afterward (`rm -r`).

**Cleanup:**
```bash
cd /tmp
rm -r /tmp/module-0-3-capstone
```

**Capability demonstrated:** the ability to move fluidly across every Module 0.3 category — navigating, managing files, reading, locating, transforming, connecting, configuring, automating, and controlling access — as one coherent workflow, rather than as nine separate, disconnected skills.

---

## 21. Review and Self-Assessment

**The nine categories, one line each:** Navigate (where am I), File operations (create/move/remove), Read (what's inside), Locate (find files/content), Transform (reorder/dedupe/extract), Connect (compose commands, control I/O), Configure (process-level behavior via environment), Automate (save a repeatable procedure), Control access (who's allowed to do any of this).

**The integrated mental model:**
```text
NAVIGATE → FILE OPERATIONS → READ → LOCATE → TRANSFORM → CONNECT → CONFIGURE → AUTOMATE → CONTROL ACCESS
```
used as a common order to check, not a rigid rule.

**The decision habit:** match the *question* you're actually asking to a *category*, before reaching for a specific command (Section 11).

**The debugging habit:** isolate stages; check identity and permissions; verify assumptions about location, quoting, and exit status, rather than guessing (Section 15).

### Self-assessment checklist

- [ ] I can name all nine Module 0.3 categories and at least one command/topic from each.
- [ ] I can look at a short, unfamiliar command-line task and identify which category (or categories) it needs.
- [ ] I can read a three- or four-stage pipeline and predict its output before running it.
- [ ] I can debug a failing combined workflow by isolating stages, rather than guessing at the whole thing.
- [ ] I can explain why permissions apply to every command in this module, even though it was the last lesson taught.
- [ ] I can explain the trade-off between a manual command and a saved script, and between a simple tool and a more powerful one.
- [ ] I can build a small multi-category workflow from scratch, in a disposable directory, without referring back to individual lessons for basic syntax.
- [ ] I can explain, in my own words, why this toolkit remains foundational to later Python, data, ML, and AI engineering work.

---

## 22. Interview Questions

1. **What are the main categories of command-line tools taught in this module?** Navigate, file operations, read/view, locate/search, transform, connect (pipes/redirection), configure (environment variables), automate (shell scripts), and control access (permissions).
2. **Why does `find` matter separately from `grep`?** `find` searches filesystem objects by name/type/location; `grep` searches file *content* for a pattern — genuinely different questions.
3. **Why is sorting often paired with deduplication?** `uniq` only collapses *adjacent* duplicate lines; sorting first groups equal lines together so `uniq` can actually catch all of them.
4. **What's the difference between a pipe and redirection?** A pipe connects one command's output to another command's input directly; redirection connects a command's input/output to a file.
5. **Why does `export` matter for automation?** A plain shell variable isn't inherited by a child process (like a script); only an exported variable is passed along.
6. **Why might a script behave differently when automated than when run manually?** Automation often runs from a different working directory, a different (or empty) environment, and sometimes a different user/service identity than your interactive session.
7. **Why is `chmod 777` considered risky rather than a real fix?** It removes essentially all access control from the object, trading a specific, diagnosable problem for a much larger security and reliability risk.
8. **How would you debug a multi-stage pipeline that produces no output?** Test each stage independently, starting from the first, since an early failure can silently produce empty input for every stage after it.
9. **Why does directory permission matter separately from file permission?** Deleting/renaming a file depends on the containing directory's write permission, and reaching a file at all depends on every directory in its path having execute (traversal) permission — neither is the same as the file's own permissions.
10. **What's the value of combining commands instead of writing a custom program for everything?** Small, well-understood tools composed together can solve many tasks quickly and transparently, without the overhead of building and maintaining custom software for something that already has a simple, tested solution.
11. **When should a sequence of commands become a shell script instead of staying manual?** Once it's something you (or others) will repeat more than once or twice, and consistency/reliability matters more than the convenience of typing it fresh each time.
12. **How does this command-line foundation relate to later programming and AI engineering work?** The same underlying questions — where is this, what's inside it, how do I combine steps, how is this configured, who's allowed to touch it — recur constantly in Python scripts, data pipelines, and production AI systems, just expressed through different tools.

---

## 23. Architecture / Engineering Questions

1. **How would you approach orienting yourself in a completely unfamiliar project directory?** Navigate to confirm location, use File operations/Read to see structure and sample key files, and use Locate to find configuration or entry points — before making any changes.
2. **How would you design a safe, repeatable investigation workflow for a production log?** Locate the relevant file(s), Read a sample first, Transform to filter/summarize rather than reading everything by eye, and Connect the stages with a pipeline you've tested one stage at a time — never acting destructively during investigation.
3. **How does composability (small tools, connected together) reflect good engineering design generally?** Each tool does one job well; combining single-purpose tools is more flexible and easier to reason about than one large tool trying to do everything — the same separation-of-concerns principle that applies to software design generally.
4. **When does a manual command-line workflow become a liability rather than a convenience?** When it's repeated often enough that inconsistency or human error becomes likely, or when it needs to run unattended — at that point it belongs in a script, with validated inputs and checked exit status.
5. **How would you reason about permission design for a small team's shared project resources?** Identify exactly which identities need which kind of access to which specific resources, and grant only that — favoring group-based, scoped access over either "just me" or "everyone."
6. **What risk does an overly long, clever one-liner introduce, architecturally?** Reduced readability and testability — a failure inside a long, uninspected chain is much harder to isolate than a failure in a short, clearly-labeled sequence of steps.
7. **How does this module's toolkit set up later Applied AI Engineering architecture decisions?** Every later system — a data pipeline, a training job, a deployed inference service — still needs to be navigated, inspected, configured, automated, and access-controlled; this module is the foundation those later architectural decisions are built on top of, not a separate, disconnected topic.

---

## 24. Production Application

Every category from this module reappears, directly, in production engineering:

- **Navigate/File operations** — organizing deployed code, artifacts, and data.
- **Read** — inspecting configuration, logs, and generated output.
- **Locate** — finding the relevant log entry, file, or artifact during an incident.
- **Transform** — summarizing large amounts of log or output data into something actionable.
- **Connect** — composing existing tools rather than writing new code for something already solved.
- **Configure** — the same environment-variable-driven behavior that separates development from production.
- **Automate** — the same shell-scripting foundation that underlies build, test, and deployment tooling, before (and often still alongside) more sophisticated automation.
- **Control access** — service accounts, scoped permissions, and least privilege, protecting real production data and artifacts.

**A production-style conceptual example, drawing every category together:**
```text
AI Service
    ↓ runs as a scoped service identity (Control access)
    ↓ reads configuration from environment variables (Configure)
    ↓ locates and reads its model/data artifacts (Locate, Read)
    ↓ processes and summarizes output (Transform)
    ↓ writes logs/results via redirection (Connect)
    ↓ the whole startup sequence is itself a script (Automate)
```

This lesson does not teach CI/CD, Docker, Kubernetes, cloud infrastructure, or advanced observability — those are later stages that build directly on top of exactly this foundation, not separate, unrelated topics.

---

## 25. Module 0.3 Completion Checklist

Confirm you can do each of the following before considering Module 0.3 complete:

- [ ] Navigate confidently using `pwd`, `ls`, `cd`, including relative and absolute paths.
- [ ] Create, copy, move, and remove files/directories safely with `mkdir`, `cp`, `mv`, `rm`.
- [ ] View a file's full contents, browse a large file interactively, and inspect just its beginning or end (`cat`, `less`, `head`, `tail`).
- [ ] Search file content and locate files by name/type (`grep`, `find`), and explain the difference between the two.
- [ ] Reorder, deduplicate (correctly, with sorting first), and extract fields from text (`sort`, `uniq`, `cut`), and safely use `xargs`.
- [ ] Build and redirect a multi-stage pipeline, and correctly reason about stdout vs. stderr.
- [ ] Distinguish a shell variable from an exported environment variable, and explain inheritance.
- [ ] Write, execute (both ways), and debug a basic shell script with arguments, variables, conditionals, loops, and functions.
- [ ] Read a permission string, decode numeric/symbolic permissions, and diagnose a "Permission denied" error methodically.
- [ ] Combine at least four of these categories into one coherent, readable workflow, from scratch, in a disposable directory.

If any box is uncertain, that's a signal to revisit the specific lesson it maps to — this lesson intentionally does not re-teach any of them in depth.

---

## 26. Scope Boundary

This lesson integrates and consolidates only the Module 0.3 topics already taught in Lessons 01–09:

```text
pwd, ls, cd, cp, mv, rm, mkdir, cat, less, head, tail,
grep, find, sort, uniq, cut, xargs,
pipes, redirection, environment variables, shell scripts, permissions
```

This lesson deliberately does **not** introduce any new command, and does **not** deeply teach:

- Python or any programming language
- Git or version control
- Docker, Kubernetes, or containers
- cloud infrastructure or cloud IAM
- CI/CD systems
- advanced Bash scripting (traps, advanced parameter expansion, process substitution)
- advanced PowerShell scripting
- ACLs, SELinux, AppArmor, or other advanced access-control systems
- observability/monitoring platforms
- databases

These belong to later stages of this roadmap, built directly on top of the foundation this module established. This lesson's own scope is strictly: **integrating, consolidating, and applying** what Lessons 01–09 already taught.

---

## 27. Final Takeaways

- The command line is not a list of commands to memorize — it's a small set of **questions** (where am I, what exists, what's inside it, where is it, how should it be shaped, how do I combine steps, how is behavior configured, should this be saved, am I allowed to) that a fixed set of tools answers.
- Real work almost always combines several categories at once; fluency means recognizing which categories a task needs, not just recalling individual command syntax.
- Every category from this module — navigation, file operations, viewing, searching, text processing, connecting commands, configuration, automation, and access control — reappears, unchanged in spirit, in every later stage of this roadmap: Python development, data pipelines, ML workflows, LLM applications, agent systems, and production AI infrastructure.
- The debugging habit this module built — check location, check identity, check permissions, isolate stages, verify assumptions rather than guessing — is durable and will keep paying off long after the specific commands feel automatic.
- Module 0.3 is complete. The foundation is now in place to move into the next stage of this roadmap.

---

_This lesson is complete. It integrates and consolidates Module 0.3 — Command Line (Lessons 01–09) and does not introduce new commands beyond what those lessons already taught. Module 0.3 is now complete._
