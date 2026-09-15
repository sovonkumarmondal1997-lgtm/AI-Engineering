# Project 0.2 — Shell File-and-Stream Investigation Lab

**Estimated time:** 60–90 minutes (can be split across two sessions)

**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Section 5 — "Practical
projects," Project 0.2 — "Shell File-and-Stream Investigation Lab"; and Section 2's Module 0.3
audit evidence: *"Complete the log-investigation project below using commands you understand, not
copied commands."*

---

## 1. Project title and estimated time

**Shell File-and-Stream Investigation Lab** — estimated 60–90 minutes.

## 2. Purpose and real-world AI-engineering relevance

This project is a small, evidence-based investigation. Its scenario: you receive a set of
application log files containing timestamps, severity levels (`INFO`/`WARN`/`ERROR`), request IDs,
and messages, and you need to answer three concrete questions — how many errors occurred, which
message repeats most often, and which request IDs appear in error lines — using only shell
commands you understand and can explain.

This is not a toy skill. Every AI service you build later — a backend API, a model-serving
endpoint, an agent worker — produces logs, and the very first debugging step, before any dedicated
log-analysis or observability tool is available, is exactly this: read the log, filter for what
matters, count what repeats, and turn raw text into a specific, evidence-backed answer. An engineer
who can only "look at the log and scroll" cannot debug a service under real production pressure;
an engineer who can pipe `grep`, `sort`, and `uniq -c` together can answer a precise question in
seconds.

## 3. Learning outcomes

By the end of this project, you will be able to:

- Create a small, synthetic set of log files with realistic structure (timestamps, levels, request
  IDs, messages) — safely, with no real or sensitive data.
- Inspect log files with `head`, `tail`, and `less` before searching them blindly.
- Filter for error lines with `grep`.
- Count repeated messages and request IDs with `sort` and `uniq -c`.
- Chain commands with pipes to answer a specific question directly, rather than reading everything
  by eye.
- Redirect final results and errors into separate files.
- Recognize the same investigation shape in PowerShell, using `Get-Content` and `Select-String`.
- Write a clear, evidence-based `investigation.md` report.

## 4. Prerequisites and safety rules

**Concepts you should have already read** (in this module, `03-Command-Line/`):

- `01-navigation.md`, `02-file-operations.md`, `03-viewing-files.md` — navigation, file operations,
  and viewing files
- `04-searching.md` — `grep`, `find`
- `05-text-processing.md` — `sort`, `uniq`, `cut`, `xargs`
- `06-pipes-and-redirection.md` — pipes and redirection
- `11-safe-terminal-and-filesystem-literacy.md` — safe practice-directory habits
- `12-shell-quoting-and-standard-streams.md` — quoting, `stdin`/`stdout`/`stderr`, `>`, `>>`, `2>`,
  `|`

You do not need to have memorized these — you need to be willing to reread one if a step below
doesn't make sense. This project assumes the concepts; it does not re-teach them from scratch.

**Tools required** (all free, already covered in Stage 0): a terminal (Bash/WSL2 or PowerShell) and
a text editor.

**Not required:** Docker, any cloud account, GPUs, or advanced programming — every command below is
explained before you're asked to run it.

**Safety rules:**

1. **Do all work inside a dedicated practice directory** (for example,
   `~/practice-shell/log-investigation/`), not inside Downloads, Documents, or an existing project.
   Confirm your current directory (`pwd`/`Get-Location`) before creating any file.
2. **Use only synthetic, non-sensitive data.** Every log file in this project is one you generate
   yourself in Step 7.2, containing invented, harmless content — never point these exercises at a
   real production log, a file with real secrets, or any file you didn't create for this project.
3. **Every command in this guide is read-only or creates a small file inside your practice
   folder.** None of them delete anything.

## 5. Deliverables and evidence checklist

By the end, your practice folder should contain:

- [ ] `logs/` — the synthetic log files you created in Step 7.2.
- [ ] `investigation.md` — your written report (Step 7.9): question, commands, evidence,
      interpretation, limitation, and next debugging step.
- [ ] `commands.sh` — a small file containing only commands you can explain (Step 7.10).
- [ ] `results.txt` and `results-errors.txt` — the redirected output from Step 7.7.
- [ ] A completed self-check against the completion gate in Section 11.

If you are tracking this work in Git (recommended — see Stage 0 Gap 0A), commit these files with a
message such as `docs: add shell file and stream investigation lab`.

## 6. Industry-standard investigation workflow

Use this loop for every question below, not only when something breaks:

```text
Goal → assumptions → smallest experiment → observe output/logs
→ explain failure → change one variable → verify → document
```

In practice, for each step:

1. **Goal** — one sentence: what question are you trying to answer?
2. **Assumptions** — one sentence: what do you expect the answer to be, before you run anything?
3. **Smallest experiment** — run the smallest command that can answer the question.
4. **Observe output/logs** — read the actual output; do not skim it.
5. **Explain failure** — if the result is unexpected (or a command errors), explain why, using the
   evidence in front of you, not a guess.
6. **Change one variable** — adjust exactly one part of the command (a flag, a pattern) and re-run.
7. **Verify** — confirm your final answer against the raw log directly, at least once.
8. **Document** — record the result in `investigation.md` before moving to the next question.

## 7. Step-by-step instructions

### 7.1 Create a dedicated safe practice directory

```bash
mkdir -p ~/practice-shell/log-investigation/logs
cd ~/practice-shell/log-investigation
pwd
```

(PowerShell: `New-Item -ItemType Directory -Force ~/practice-shell/log-investigation/logs`, then
`Set-Location ~/practice-shell/log-investigation`, then `Get-Location`.)

Record the confirmed path in `investigation.md` before continuing.

### 7.2 Create several small synthetic log files

Create two log files with realistic, entirely invented content — timestamps, levels, request IDs,
and repeatable messages. Type these yourself rather than copying blindly, so you know exactly
what's in them before you start searching.

```bash
cat > logs/app-2026-09-15.log << 'EOF'
2026-09-15T09:58:01 INFO req-1001 Handled request successfully
2026-09-15T09:58:14 INFO req-1002 Handled request successfully
2026-09-15T09:58:30 WARN req-1003 Response time exceeded 500ms
2026-09-15T09:59:02 ERROR req-1004 Failed to connect to database
2026-09-15T09:59:10 INFO req-1005 Handled request successfully
2026-09-15T09:59:45 ERROR req-1004 Failed to connect to database
2026-09-15T10:00:03 WARN req-1006 Response time exceeded 500ms
2026-09-15T10:00:20 ERROR req-1007 Timeout waiting for upstream service
2026-09-15T10:00:41 INFO req-1008 Handled request successfully
2026-09-15T10:01:02 ERROR req-1004 Failed to connect to database
EOF

cat > logs/worker-2026-09-15.log << 'EOF'
2026-09-15T09:57:55 INFO req-2001 Worker started task
2026-09-15T09:58:40 ERROR req-2002 Timeout waiting for upstream service
2026-09-15T09:59:20 INFO req-2003 Worker completed task
2026-09-15T10:00:05 ERROR req-2004 Failed to connect to database
2026-09-15T10:00:55 WARN req-2005 Response time exceeded 500ms
2026-09-15T10:01:30 ERROR req-2002 Timeout waiting for upstream service
EOF
```

`cat > file << 'EOF' ... EOF` writes everything between the two `EOF` markers directly into the
named file — a quick way to create a multi-line file from the terminal without an editor. The
quotes around the first `EOF` matter: they stop the shell from expanding anything special inside
the block, keeping the log lines exactly as typed (Lesson 12, Section 3).

**PowerShell equivalent** (create the same content using `Set-Content`):

```powershell
@"
2026-09-15T09:58:01 INFO req-1001 Handled request successfully
2026-09-15T09:58:14 INFO req-1002 Handled request successfully
2026-09-15T09:58:30 WARN req-1003 Response time exceeded 500ms
2026-09-15T09:59:02 ERROR req-1004 Failed to connect to database
2026-09-15T09:59:10 INFO req-1005 Handled request successfully
2026-09-15T09:59:45 ERROR req-1004 Failed to connect to database
2026-09-15T10:00:03 WARN req-1006 Response time exceeded 500ms
2026-09-15T10:00:20 ERROR req-1007 Timeout waiting for upstream service
2026-09-15T10:00:41 INFO req-1008 Handled request successfully
2026-09-15T10:01:02 ERROR req-1004 Failed to connect to database
"@ | Set-Content logs\app-2026-09-15.log
```

### 7.3 Inspect the logs with `head`, `tail`, and `less`

**Goal:** get a feel for the data before searching it blindly.

```bash
head -n 5 logs/app-2026-09-15.log
tail -n 5 logs/app-2026-09-15.log
less logs/app-2026-09-15.log      # press q to quit
```

- `head -n 5` — show the first 5 lines.
- `tail -n 5` — show the last 5 lines.
- `less` — scroll through the whole file one screen at a time.

Write in `investigation.md`: how many files you have, roughly how many lines each contains, and
what the three levels (`INFO`/`WARN`/`ERROR`) look like at a glance.

### 7.4 Filter error lines with `grep`

**Question 1: how many errors occurred?**

```bash
grep ERROR logs/app-2026-09-15.log
```

- `grep PATTERN FILE` — print only the lines containing `PATTERN`.

```bash
grep -c ERROR logs/app-2026-09-15.log
```

- `-c` — instead of printing matching lines, print a *count* of them.

To check **all** log files at once instead of just one:

```bash
grep -c ERROR logs/*.log
```

`logs/*.log` expands to every file in `logs/` ending in `.log` — the shell substitutes this before
`grep` ever runs (this is the same kind of shell behavior Lesson 12 covers for quoting, just
working in your favor here since there are no spaces in these filenames).

To get a single combined count across every file:

```bash
grep -h ERROR logs/*.log | wc -l
```

- `-h` — when searching multiple files, suppress the filename prefix `grep` normally adds, so the
  piped output is just the matching lines themselves.
- `wc -l` — count the number of lines it receives.

Record the exact count in `investigation.md`, along with the command you used to get it.

### 7.5 Use `sort` and `uniq -c` to find repeated messages and request IDs

**Question 2: which message repeats most often?**

The message text follows the request ID on each line. Extract just the message part, then count
repeats:

```bash
grep -h ERROR logs/*.log | cut -d' ' -f4- | sort | uniq -c | sort -rn
```

Reading this pipeline left to right:

- `grep -h ERROR logs/*.log` — every `ERROR` line, from every file, without filename prefixes.
- `cut -d' ' -f4-` — split each line on spaces (`-d' '`) and keep field 4 onward (skipping the
  timestamp, level, and request ID, leaving just the message).
- `sort` — put identical messages next to each other (`uniq` only merges *adjacent* duplicate
  lines, so this step is required first).
- `uniq -c` — collapse adjacent duplicate lines into one, prefixed with a **c**ount of how many
  times it appeared.
- `sort -rn` — sort **n**umerically, **r**eversed (largest count first), so the most frequent
  message is at the top.

**Question 3: which request IDs appear in error lines?**

```bash
grep -h ERROR logs/*.log | cut -d' ' -f3 | sort | uniq -c | sort -rn
```

Same pipeline, but extracting field 3 (the request ID — field 1 is the timestamp, field 2 is the
level) instead of the message. A request ID with a count greater than 1 tells you that specific
request failed more than once — worth investigating further in a real incident.

Record both results in `investigation.md`, with the exact commands used.

### 7.6 Answer all three questions with pipes

By this point you have the pipeline shape for each of the three questions:

1. **Error count:** `grep -h ERROR logs/*.log | wc -l`
2. **Most frequent error message:** `grep -h ERROR logs/*.log | cut -d' ' -f4- | sort | uniq -c |
   sort -rn`
3. **Request IDs in error lines:** `grep -h ERROR logs/*.log | cut -d' ' -f3 | sort | uniq -c |
   sort -rn`

Run all three again, together, and confirm the numbers are internally consistent — for example,
the sum of every request ID's count in Question 3 should equal the total error count from Question
1.

### 7.7 Redirect final results and errors into separate files

```bash
{
  echo "=== Error count ==="
  grep -h ERROR logs/*.log | wc -l
  echo
  echo "=== Most frequent error message ==="
  grep -h ERROR logs/*.log | cut -d' ' -f4- | sort | uniq -c | sort -rn
  echo
  echo "=== Request IDs in error lines ==="
  grep -h ERROR logs/*.log | cut -d' ' -f3 | sort | uniq -c | sort -rn
} > results.txt 2> results-errors.txt
```

- `{ ... }` — groups several commands so their combined output can be redirected together, once.
- `> results.txt` — sends all normal output (`stdout`) from the group to `results.txt`, following
  Lesson 12, Section 6.
- `2> results-errors.txt` — sends any error output (`stderr`) — for example, if a file were missing
  or unreadable — to a *separate* file, so a real error would never be silently mixed into your
  results.

```bash
cat results.txt
cat results-errors.txt
```

`results-errors.txt` should be empty in this exercise, since every command succeeds — confirm that
yourself rather than assuming it.

### 7.8 Repeat one task in PowerShell

Pick Question 1 (error count) and repeat it using PowerShell's equivalents:

```powershell
Get-Content logs\app-2026-09-15.log | Select-String "ERROR"
(Get-Content logs\app-2026-09-15.log | Select-String "ERROR").Count
```

- `Get-Content` — PowerShell's equivalent of `cat`: reads a file's lines.
- `Select-String "PATTERN"` — PowerShell's equivalent of `grep`: filters for lines matching a
  pattern.
- `.Count` — counts how many matches were found, the PowerShell equivalent of piping into `wc -l`.

Record the PowerShell command and its result in `investigation.md` next to the Bash version, and
confirm both report the same count.

### 7.9 Write `investigation.md`

Using your notes from Steps 7.1–7.8, write `investigation.md` with these sections, one per
question plus an overall wrap-up:

For **each** of the three questions (error count, most frequent message, request IDs in errors):

- **Question** — the exact question being answered.
- **Commands** — the exact pipeline you ran.
- **Evidence** — the real output you got (not a paraphrase).
- **Interpretation** — one or two sentences on what the evidence means.

Then, once at the end:

- **Limitation** — one honest limitation of this approach (for example: "this only counts exact
  message text matches — a message with a slightly different wording, like a different request ID
  embedded in the text itself, wouldn't be grouped together" or "this doesn't tell you *why* the
  database connection failed, only that it did, repeatedly").
- **Next debugging step** — what you would check next in a real incident (for example: "check the
  database service's own logs around `10:01:02` to see what it reported on its side").

### 7.10 Create `commands.sh`

Write a file, `commands.sh`, containing only the final, working commands from Steps 7.4–7.7 — one
per question, in order, with a `#` comment above each explaining what it answers. Do not include
any command you cannot personally explain, line by line, out loud. This file is not meant to be run
automatically; it's a personal reference of commands you've proven you understand.

## 8. Expected observations and acceptance criteria

- **Question 1 (error count):** 7 total (`ERROR` lines across both sample files) — confirm this
  matches what you count by eye in Step 7.3's `less` view.
- **Question 2 (most frequent message):** `Failed to connect to database` (4 occurrences) and
  `Timeout waiting for upstream service` (3 occurrences) should both appear, with "Failed to
  connect to database" ranked first by `sort -rn`.
- **Question 3 (request IDs in errors):** `req-1004` should show a count of 3 (it appears in three
  separate `ERROR` lines) — the single most-repeated request ID in the sample data.
- **Section 7.7:** `results.txt` contains all three answers in readable form; `results-errors.txt`
  is empty.
- **Section 7.8:** the PowerShell count for Question 1 matches the Bash count exactly.
- `investigation.md` contains real, observed output for every claim — not descriptions of what
  "should" happen.

(If you typed the sample logs in Section 7.2 exactly as given, your numbers should match these
exactly — if they don't, that's a genuine, useful debugging exercise in its own right: work out
which line was typed differently.)

## 9. Common mistakes and safe troubleshooting

| Problem | Likely cause | Safe next step |
|---|---|---|
| `grep -c ERROR logs/*.log` prints one number per file instead of a combined total | `-c` reports a count per file when multiple files are given | Use the `grep -h ... \| wc -l` form from Section 7.4 instead, which combines everything into a single stream first. |
| `uniq -c` shows every line as a separate count of 1, even for messages that look identical | The input wasn't sorted first — `uniq` only merges lines that are *adjacent* | Add `sort` before `uniq -c`, exactly as in the pipelines in Section 7.5. |
| `cut -d' ' -f4-` gives the wrong column | The log line has a different number of space-separated fields than expected (for example, extra spaces) | Run `cat -A logs/app-2026-09-15.log` to reveal exact spacing, or print one line alone through `cut` and adjust the field number until it matches. |
| `results-errors.txt` isn't empty | One of the grouped commands actually failed — check what it reported | Open `results-errors.txt` and read the exact message; it will name the specific command and reason, the same way Lesson 12's `2>` example does. |
| PowerShell's count doesn't match Bash's | A typo in one of the two log files, or matching on a different pattern | Re-run `Get-Content` and `cat` on the exact same file and compare line-by-line, rather than assuming one tool is "wrong." |

If you hit something not listed here, apply the workflow in Section 6: state what you expected,
what happened instead, and check one fact (the exact file, the exact field number, the exact
pattern) at a time before changing anything.

## 10. Interview-practice questions

Practice answering these aloud, in 60–90 seconds each, using your own notes from
`investigation.md`:

1. **"How would you find out how many errors are in a log file from the command line?"**
   Guidance: name `grep -c` (or `grep | wc -l` for multiple files) directly, and explain briefly
   why the multi-file form differs — this shows you've actually hit that distinction, not just read
   about it.

2. **"How would you find the most common error message in a large log file?"**
   Guidance: walk through the `cut | sort | uniq -c | sort -rn` pipeline in order, explaining what
   each stage does to the data — this is one of the most common real debugging patterns you'll use
   professionally.

3. **"Why do you need to `sort` before `uniq -c`?"**
   Guidance: explain that `uniq` only collapses *adjacent* duplicate lines, so unsorted input would
   make it undercount — a detail that shows genuine hands-on understanding rather than memorized
   syntax.

4. **"What's the difference between piping a command's output and redirecting it to a file?"**
   Guidance: connect this to Lesson 12 — a pipe (`|`) sends output to another command's input; a
   redirect (`>`/`>>`) sends it to a file instead, and the two are often combined in one
   investigation.

5. **"If your investigation script failed partway through, how would you find out why without
   losing your results so far?"**
   Guidance: describe separating `stdout` and `stderr` into different files (Section 7.7) — normal
   results keep accumulating in one file while any error is captured, readably, in another.

## 11. Completion gate

You have completed this project when all statements below are true:

- [ ] I created my own synthetic log files with realistic structure and no real or sensitive data.
- [ ] I inspected the logs with `head`, `tail`, and `less` before searching them.
- [ ] I answered all three questions (error count, most frequent message, request IDs in errors)
      using pipelines I built and can explain, not copied commands.
- [ ] I redirected results and errors into separate files and confirmed the error file was empty.
- [ ] I repeated the error-count question in PowerShell and confirmed it matched the Bash result.
- [ ] `investigation.md` is complete, in my own words, with real observed output for every claim,
      plus an honest limitation and a genuine next debugging step.
- [ ] `commands.sh` contains only commands I can explain line by line, out loud.
- [ ] I answered all five interview-practice questions aloud at least once.

Once every box is checked, this project satisfies Stage 0 Project 0.2 and the Module 0.3 audit
evidence referenced in the Stage 0 roadmap's Section 2. Return to
[`../../00-Stage-0-Overview/learning-plan.md`](../../00-Stage-0-Overview/learning-plan.md) to
continue with the rest of Stage 0.
