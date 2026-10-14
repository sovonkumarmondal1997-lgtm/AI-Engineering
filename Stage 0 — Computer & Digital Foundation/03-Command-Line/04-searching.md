# Module 0.3 — Command Line

## Lesson 04 — Searching

**Module:** Command Line
**Roadmap reference:** Stage 0 — Module 0.3 — Command Line
**Concept(s) covered:** `grep`, `find`
**Status:** Complete
**Builds on:** 01-navigation.md (`pwd`, `ls`, `cd`), 02-file-operations.md (`mkdir`, `cp`, `mv`, `rm`), 03-viewing-files.md (`cat`, `less`, `head`, `tail`), and Module 0.1/0.2 (filesystem, directories, processes, shell)

---

## Learning Objectives

After completing this lesson you will be able to:

1. Explain what searching means on the command line.
2. Explain why command-line searching is useful, especially where no graphical interface exists.
3. Distinguish searching file **content** from searching filesystem **location/structure**.
4. Explain what `grep` is used for.
5. Explain what `find` is used for.
6. Use basic `grep` commands safely.
7. Use basic `find` commands safely.
8. Understand common `grep` options (`-n`, `-i`, `-r`, `-l`, `-c`).
9. Understand common `find` conditions (`-name`, `-type f`, `-type d`).
10. Search within one file.
11. Search across multiple files.
12. Search recursively with the appropriate command.
13. Search for files by name, type, or location.
14. Explain the difference between `grep` and `find`.
15. Predict what a search command will do before running it.
16. Diagnose common searching failures.
17. Apply command-line searching to software-engineering and Applied AI Engineering workflows.
18. Use searching safely, without accidentally modifying or deleting data.

---

## 1. What Is Command-Line Searching?

**Searching**, in everyday language, means looking for something specific among a larger collection of things. On the command line, "something specific" is almost always one of two categories:

- **Content** — specific text that exists *inside* a file (a word, an error message, a configuration key).
- **Filesystem objects** — files or directories that match some description (a name, a type, a location) — regardless of what's written inside them.

These are genuinely different questions, and this lesson teaches one command for each:

- **`grep`** — "Find this text/pattern **inside content**."
- **`find`** — "Find these **files/directories** that satisfy these conditions."

You already have the tools to move around the filesystem (Lesson 01), manage files (Lesson 02), and read a file's contents once you've located it (Lesson 03). Searching answers a question those lessons don't: **when you don't already know exactly where something is, or exactly which file has it, how do you locate it?**

### Why command-line searching, specifically

A graphical file explorer's search box, or a code editor's "find in files" feature, can answer similar questions — but command-line searching remains essential for engineers because:

- It works in **every** environment you'll encounter later in this roadmap — remote servers, containers, CI/CD runners — many of which have no graphical interface at all (the same point made in Lesson 03, Section 2).
- It is **precise and scriptable** — a command-line search can be repeated exactly, combined with other commands, or automated, in ways a manual GUI search cannot.
- It operates directly on the same filesystem and text you've already been working with all module — no separate tool or application to open.

---

## 2. Why Searching Matters to an Engineer

Realistic situations where searching is the actual skill being used, day to day:

- **Finding a configuration value** — "what is this setting currently set to, and in which file?"
- **Locating an error message** — "where did this exact error text get logged?"
- **Finding references to a function or class** — "everywhere in this codebase that mentions `AgentConfig`."
- **Locating log entries** — "every line in this log mentioning `timeout`."
- **Finding files by name** — "where is `config.yaml` in this project?"
- **Finding Python files** — "list every `.py` file in this project."
- **Finding datasets** — "where are the `.csv` files in this repository?"
- **Finding model artifacts** — "where did the training run save its output?"
- **Locating configuration files** — "which files in this project are actually configuration?"
- **Finding generated files** — "what did this script actually produce, and where?"
- **Investigating an unfamiliar project** — before you've read any documentation, searching is often the fastest way to orient yourself.
- **Diagnosing a missing file** — "is this file actually here, and if not, where did it end up?"
- **Inspecting a large project tree** — one where manually navigating with `cd`/`ls` alone would be far too slow.

Every one of these situations reduces to one of the two mental models introduced in Section 1: either you're looking for *text inside something*, or you're looking for *something by its filesystem description*. This lesson's entire job is to make that distinction automatic, and to give you the two commands that answer each case.

---

## 3. Searching and the Operating System

Recall from Module 0.1 and Module 0.2: files live inside a **filesystem hierarchy** — a tree of directories containing files and other directories (Module 0.1) — and every command you run is a **process** that the **shell** launches on your behalf, receiving whatever arguments you typed, and interacting with the filesystem through the operating system (Module 0.2).

Both commands in this lesson fit that same model, just with different jobs:

- **`find`** is given a starting location and some conditions, and it **traverses** the filesystem hierarchy from that point — walking into directories, and their subdirectories, checking each filesystem entry (file or directory) against your conditions.
- **`grep`** is given a pattern and some input (typically one or more files), and it **reads that input's content**, checking each line against your pattern.

In other words: `find` operates on the *structure* the operating system already tracks (what exists, where, and what kind of thing it is); `grep` operates on the *content* stored inside whatever file(s) you point it at. This lesson keeps this connection at the conceptual level established in Module 0.2 — it does not revisit kernel-level detail or filesystem implementation internals.

---

## 4. The `grep` Command

`grep` searches text content for lines matching a given pattern, and prints the matching lines.

### What `grep` is for, and why it exists

Without a dedicated search command, finding a specific piece of text inside a file would mean opening it (`cat` or `less`, from Lesson 03) and reading through it yourself, line by line, until you happened to spot what you were looking for. That's manageable for a short file, but hopeless for a large log or a project with hundreds of files. `grep` exists to do that line-by-line checking for you, instantly, and to show you only the lines that actually matched.

### Basic syntax

```bash
grep "pattern" file
```

- **`grep`** — the command itself.
- **`"pattern"`** — the text you're searching for, in quotes (explained further in Section 5).
- **`file`** — the file `grep` should read and check.

### Searching one file

```bash
grep "timeout" server.log
```

This reads `server.log` line by line and prints every line containing the text `timeout`.

### Showing line numbers — `-n`

```bash
grep -n "timeout" server.log
```

Adds the line number to each matching line, so you know exactly where in the file the match occurred — useful when you'll next open the file (e.g. in `less`) and want to jump straight to the relevant spot.

### Case-insensitive searching — `-i`

By default, `grep` is **case-sensitive** — `"Timeout"` and `"timeout"` are treated as different text entirely.

```bash
grep -i "timeout" server.log
```

`-i` ("ignore case") makes `grep` match `timeout`, `Timeout`, `TIMEOUT`, or any other capitalization, all at once.

### Searching multiple files

```bash
grep "timeout" server.log worker.log
```

`grep` checks both files and, when more than one file is given, prefixes each matching line with the filename it came from — so you know which file each result belongs to.

### Searching recursively — `-r`

```bash
grep -r "timeout" logs/
```

`-r` ("recursive") tells `grep` to search not just the files directly inside `logs/`, but every file inside every subdirectory beneath it too — the same "recursive" concept from Lesson 02 (repeat this operation on everything inside, and everything inside that, at any depth), applied here to searching instead of copying or deleting.

### Showing only filenames that matched — `-l`

```bash
grep -rl "timeout" logs/
```

`-l` ("files with matches") prints only the *names* of files containing at least one match, rather than the matching lines themselves — useful when you just want to know *which* files are relevant, before deciding whether to open any of them.

### Counting matches — `-c`

```bash
grep -c "timeout" server.log
```

`-c` ("count") prints a single number: how many *lines* in the file matched (not the total number of occurrences of the pattern) — without showing the lines themselves.

### Putting the pieces together

Every `grep` command you've seen has the same four components:

```text
grep   [options]   "pattern"   target(s)
 ↑         ↑           ↑            ↑
command  behavior   what to      file(s) or
         modifiers   search for   directory
```

This lesson covers only the options above (`-n`, `-i`, `-r`, `-l`, `-c`) — the ones needed to search confidently and safely as a beginner. `grep` has many more options; they are intentionally left out here to keep the mental model clear rather than exhaustive.

---

## 5. `grep` Patterns

A **pattern** is the text `grep` looks for on each line. By default, `grep` interprets its pattern as a **basic regular expression**. The simple patterns used so far, such as `error`, behave like literal text because they contain no special characters (subject to case-sensitivity, per `-i` above).

```bash
grep "error" app.log        # case-sensitive: matches "error", not "Error" or "ERROR"
grep -i "error" app.log     # matches "error", "Error", "ERROR", and any other capitalization
grep "python" requirements.txt
grep "timeout" server.log
```

Characters such as `.`, `*`, `^`, and `$` can have special meaning in a pattern (for example, `foo.bar` does not mean only the literal text `foo.bar`, because `.` matches any single character). Regular expressions — a small pattern language for describing text more flexibly than an exact string — are a substantial topic on their own, and this lesson deliberately does not teach them; sticking to simple word-like patterns is enough to use `grep` productively and safely as a beginner. A dedicated, deeper treatment of pattern matching belongs to a later stage of this roadmap, not this lesson.

### Why quote your pattern

```bash
grep "error message" app.log
```

Quoting matters because the shell (Lesson 01, Section 9's path-resolution discussion, and Lesson 02's wildcard-expansion discussion) processes what you type *before* `grep` ever sees it. Without quotes, a pattern containing spaces or certain special characters could be split apart or misinterpreted by the shell itself, and `grep` would receive something different from what you intended. Quoting your pattern keeps it together as one shell word and prevents pathname expansion (globbing) of characters like `*`. (Double quotes still allow some shell expansions, such as parameter expansion and command substitution; single quotes prevent those too.) It is a simple habit that prevents a whole category of confusing mistakes.

---

## 6. The `find` Command

`find` searches the filesystem for files and directories matching given conditions, based on their name, type, or location (filesystem entries and their properties/conditions) — not their content.

### What `find` is for, and why it exists

Once a project has more than a handful of files, manually navigating with `cd` and `ls` (Lesson 01) to locate one specific file, or every file of a certain kind, becomes slow and error-prone. `find` exists to answer exactly that question directly: "starting from here, show me everything that matches this description."

### Basic syntax

```bash
find . -name "filename"
```

- **`find`** — the command itself.
- **`.`** — the **starting directory** — recall from Lesson 01 that `.` means "the current directory." `find` begins here and looks downward into every subdirectory beneath it, automatically — unlike `grep`, `find` does not need a separate `-r` flag, because searching downward through the directory tree is simply what `find` always does.
- **`-name "filename"`** — a **condition**: only report entries whose name matches exactly what's given.

### Searching by exact filename

```bash
find . -name "config.yaml"
```

Starting from the current directory, this reports the path to every file or directory named exactly `config.yaml`, anywhere underneath it.

### Searching by a wildcard pattern

```bash
find . -name "*.py"
```

Here, `*` is a **wildcard** — a symbol standing in for "any sequence of characters" (the same concept briefly introduced in Lesson 02, Section 11, for shell wildcards). `*.py` describes "any name ending in `.py`" — that is, every Python file.

**Important distinction:** when a wildcard appears *inside quotes* as part of a `-name` condition, the shell does **not** expand it the way it would for an unquoted wildcard typed directly at the shell (as in Lesson 02's `rm *.txt` example) — instead, the quoted pattern is passed to `find` exactly as written, and `find` itself checks each filename against that pattern as it traverses. This is a subtle but important beginner distinction: **the same `*` symbol can be expanded by the shell, or interpreted by a command like `find`, depending on whether it's quoted** — quoting it here ensures `find` (not the shell) decides what counts as a match, which is what lets `find` correctly check filenames deep inside subdirectories the shell couldn't even see in advance.

### Searching by type — files vs. directories

```bash
find . -type f
```

`-type f` restricts results to **files** only (`f` for "file").

```bash
find . -type d
```

`-type d` restricts results to **directories** only (`d` for "directory").

### Combining name and type

```bash
find . -type f -name "*.log"
```

This combines both conditions: only report **files** (not directories) whose name ends in `.log`. Conditions given to `find` combine naturally this way — each additional condition narrows the results further.

### Summary of what you've learned

| Piece | Meaning |
|---|---|
| `.` | Start searching from the current directory (and everything beneath it) |
| `-name "x"` | Match entries named exactly `x` |
| `-name "*.py"` | Match entries whose name ends in `.py` (wildcard pattern) |
| `-type f` | Only match files |
| `-type d` | Only match directories |

This lesson covers only these conditions — `find` supports many more (searching by size, modification time, permissions, and so on), which are intentionally out of scope here to keep the mental model focused.

---

## 7. `grep` vs. `find`

| Question | Appropriate tool |
|---|---|
| "Which files are named `config.yaml`?" | `find` |
| "Which files contain the word `timeout`?" | `grep` |
| "Where are all the Python files?" | `find` |
| "Which Python files contain `async`?" | Conceptually, a *combination* of `find` and `grep` — see note below |
| "Is there a directory called `models` anywhere in this project?" | `find` |
| "Does any log file mention `ERROR`?" | `grep` |

The memorable core distinction:

```text
grep → searches CONTENT (what's written inside files)
find → searches FILESYSTEM ENTRIES and their properties (name, type, location)
```

**On combining them:** a question like "which Python files contain `async`?" genuinely needs both ideas — first locating the right files (`find`'s job), then checking their content (`grep`'s job). In later lessons, you'll learn **pipes** (`06-pipes-and-redirection.md`) and `xargs`, which let you connect commands like this together directly. This lesson does not teach that mechanism — for now, understand only that such a question is conceptually a two-step process, addressed by two separate commands, one at a time: first use `find` to get a list of Python files, then use `grep` on those specific files.

---

## 8. Internal Mechanics

### For `grep`

1. The shell parses your command — the pattern, any options, and the target file(s) or directory.
2. The shell launches `grep` as a process (Module 0.2).
3. `grep` receives its arguments — the pattern to look for, and what to read.
4. `grep` opens and reads the target input, one line at a time.
5. Each line is compared against the pattern.
6. Matching lines are written to **standard output** — the same concept introduced in Lesson 03, Section 11 — which is what appears in your terminal.
7. `grep` also communicates an **exit status** — a signal, separate from the printed output, indicating whether at least one match was found or whether something went wrong (expanded in Section 9 below).

### For `find`

1. The shell launches `find` as a process, with your starting path and conditions as arguments.
2. `find` begins at the starting directory you specified.
3. It **traverses** the directory tree — visiting the starting directory's contents, then each subdirectory's contents, and so on, descending automatically.
4. For each filesystem entry it encounters (each file and directory along the way), it examines that entry's properties — name, type, and so on.
5. Each entry is checked against your conditions (`-name`, `-type`, or both together).
6. Every entry that satisfies **all** given conditions has its path printed to standard output, by default, as `find` encounters it.

Both commands, in the end, are simply processes reading data the operating system already manages — `grep` reads file *content*; `find` reads filesystem *structure* — and both report their findings through the same standard-output channel introduced in the previous lesson. This lesson does not go beyond this level of detail; deeper implementation topics remain out of scope, exactly as in Lesson 03.

---

## 9. Standard Output and Exit Status

As just described, both `grep` and `find` print their results to **standard output** — but it's worth being explicit about something beginners often assume incorrectly: **a search command's visible output and whether it "succeeded" are two separate things.**

Concretely, a search can:

- **Find one or more matches** — output is printed; the command is considered to have succeeded.
- **Find no matches at all** — no output is printed, but this is not an error. `grep`/`find` did exactly what was asked; there simply was nothing to report. (Section 16 addresses this misconception directly.)
- **Fail outright** — for example, due to a nonexistent path or a permissions problem (Section 14) — in which case an actual error message is printed, distinct from "no matches."

In the Bash/Linux environment taught here, the two commands differ:

```text
grep:  0 → at least one match was found
       1 → no match was found
       2 → an error occurred
find:  0 → traversal completed successfully — even if no entry matched the conditions
       non-zero → an error/problem occurred
```

So `grep` producing no output is not the same as `grep` failing, and `find` does not signal "no match" through its exit status the way `grep` does.

Command-line programs communicate this distinction through something called an **exit status** — a small signal a program sends when it finishes, indicating success or failure, separate from anything it printed. This lesson does not teach how to read or use exit status directly (that connects to shell scripting, a later lesson) — only that it exists, and that it's the reason "no output" and "the command is broken" are not the same thing.

This lesson also does not teach **redirection** (sending output to a file instead of the screen) or **pipes** (sending one command's output into another command) — those are the dedicated subjects of `06-pipes-and-redirection.md`.

---

## 10. Real-World Software Engineering Use Cases

Consider a small, realistic project:

```text
my-ai-project/
├── app/
│   ├── main.py
│   ├── agent.py
│   └── config.py
├── tests/
│   ├── test_agent.py
│   └── test_config.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
└── logs/
```

Realistic questions, and the command that answers each:

```bash
# "Where is the config module defined?"
find . -name "config.py"

# "Which files mention 'API_KEY'?"
grep -r "API_KEY" .

# "What test files exist?"
find tests -type f -name "test_*.py"

# "Does the log mention any errors?"
grep -i "error" logs/app.log

# "What's actually inside the data directory?"
find data -type f
```

None of this requires reading documentation about the project first — searching *is* often the fastest way to start understanding an unfamiliar codebase, confirm a suspicion while debugging, or locate exactly the file you need to change. This lesson does not cover Git (finding *when* something changed) or any language's filesystem APIs (finding things *from inside a program*) — both are separate, later topics.

---

## 11. Applied AI Engineering Connection

The same two commands are just as essential once your projects involve data, models, and experiments rather than only source code:

- **Finding model configuration files** — `find . -name "*.yaml"` or `find . -name "model_config.*"`.
- **Locating dataset files** — `find data -type f -name "*.csv"`, or `find . -name "*.jsonl"` for line-delimited JSON datasets.
- **Finding files by type across formats** — `.json`, `.jsonl`, `.csv`, `.parquet`, `.py`, `.yaml`, `.toml` are all just different `-name` patterns to the same `find` command.
- **Finding occurrences of a model name or config key** — `grep -r "gpt-4" configs/`, to see everywhere a specific model identifier is referenced.
- **Locating prompt or configuration files** — `find . -name "*prompt*"`.
- **Searching logs for errors** — `grep -i "error" logs/training.log`, exactly the kind of first step described in Lesson 03's debugging discussion of `tail`.
- **Finding generated evaluation artifacts** — `find artifacts -type f -name "*.json"`.
- **Diagnosing why an expected file is missing** — running `find` for the expected filename and getting no result is itself valuable evidence (Section 9) — it tells you the file genuinely isn't there, rather than that you looked in the wrong place by accident.
- **Exploring an unfamiliar AI project** — the same "orient yourself via search" approach from Section 10, applied to a project full of configs, datasets, and experiment directories instead of only source code.
- **Locating evaluation or agent/tool configuration** — `find . -name "eval_config.yaml"`, or `grep -r "tool_name" .` to find where a specific tool is registered.

### Failure scenarios caused by poor searching skills

- **Using the wrong dataset** — assuming a `find` result was the only matching file, when a stale duplicate existed elsewhere in the project too.
- **Editing the wrong configuration** — `grep`-ing for a setting name, finding it in one file, and not realizing an identically named setting also exists in a second, unrelated config.
- **Inspecting the wrong model artifact** — confusing two similarly named files because the search wasn't specific enough (e.g. a bare `-name "model*"` matching several unrelated files).
- **Missing an error** — searching a log case-sensitively for `"Error"` when the actual log entry says `"ERROR"`, and concluding — incorrectly — that no error occurred.
- **Debugging the wrong file** — acting on a `grep` match found in a backup or archive copy rather than the actual file currently in use.
- **Running commands from the wrong project location** — forgetting to check `pwd` (Lesson 01) before running `find .` or `grep -r`, and searching an entirely different directory than intended.

This lesson stays at the level of the two foundational commands themselves — it does not introduce RAG pipelines, agent frameworks, LLMOps tooling, Docker, Kubernetes, or cloud infrastructure. Those are mentioned only as future context: the exact same `grep`/`find` skills you're building here will still be exactly what you reach for, underneath all of that tooling, later in the roadmap.

---

## 12. Bash / Linux / WSL2 / Git Bash / PowerShell

This lesson's primary and reference environment is **Bash on Linux**, **WSL2** and **Git Bash** provide broadly similar command-line capabilities, and the basic `grep`/`find` examples here are written for Bash/Linux. These environments are not identical, though — implementations, versions, filesystem integration, and some behaviors can differ.

**PowerShell** (native Windows) has different, though conceptually related, tools:

| Bash/Linux | PowerShell equivalent | Notes |
|---|---|---|
| `grep "pattern" file` | `Select-String -Pattern "pattern" -Path file` | Roughly equivalent capability: searches content for a matching pattern |
| `find . -name "file"` | `Get-ChildItem -Recurse -Filter "file"` | Roughly equivalent capability: searches the filesystem by name, recursively |

This lesson is not a PowerShell course — this table exists only so that, if you're working on native Windows, you know roughly equivalent capability exists under different command names (these are conceptual equivalents, not implementation-level ones). **WSL2** consideration: searching inside WSL2's Linux filesystem is generally the cleanest practice environment, while Windows-mounted paths (`/mnt/c/...`, see Lesson 02) can have different performance and interoperability characteristics; searching a very large tree across that boundary can be noticeably slower than searching entirely within one filesystem.

---

## 13. Safe Practical Demonstration

All commands below are demonstrated against a disposable, learner-created practice directory — for example, `/tmp/command-line-search-demo` — containing only harmless, learner-created sample content. Nothing here touches the real Applied AI Engineering project or any unrelated file. **No command in this section has actually been executed** — every result shown is explicitly labeled `Example output:` as an illustration of expected behavior, not a captured result.

Conceptual demonstration directory:

```text
command-line-search-demo/
├── notes.txt
├── errors.txt
├── config.txt
├── app/
│   ├── main.py
│   └── agent.py
├── logs/
│   ├── app.log
│   └── worker.log
└── data/
    ├── sample.csv
    └── sample.json
```

**Setup (conceptual):**

```bash
mkdir -p /tmp/command-line-search-demo/app /tmp/command-line-search-demo/logs /tmp/command-line-search-demo/data
cd /tmp/command-line-search-demo
```

**1. `grep` against a single file**

```bash
grep "timeout" logs/app.log
```
Example output:
```text
2026-09-10 12:03:11 WARNING timeout while connecting to worker
```

**2. Case-insensitive search**

```bash
grep -i "error" errors.txt
```
Example output:
```text
Error: missing configuration key
ERROR: retry limit exceeded
error: connection closed
```

**3. Line-number search**

```bash
grep -n "timeout" logs/app.log
```
Example output:
```text
14:2026-09-10 12:03:11 WARNING timeout while connecting to worker
```

**4. Recursive search across the whole demo directory**

```bash
grep -r "config" .
```
Example output:
```text
./config.txt:default_config=true
./app/agent.py:from app.config import load_config
```

**5. `find` by exact filename**

```bash
find . -name "config.txt"
```
Example output:
```text
./config.txt
```

**6. `find` by extension**

```bash
find . -name "*.py"
```
Example output:
```text
./app/main.py
./app/agent.py
```

**7. `find` by type**

```bash
find . -type d
```
Example output:
```text
.
./app
./logs
./data
```

**Cleanup:**

```bash
cd /tmp
rm -r /tmp/command-line-search-demo
```

Removing this directory afterward follows the same safe cleanup habit from Lesson 02 — this disposable practice area should not be left behind once you've finished experimenting.

---

## 14. Common Mistakes

**1. Searching the wrong directory**
- *Symptom:* No matches found, even though you're sure the file/text exists somewhere.
- *Likely cause:* You're not actually inside (or pointing `find`/`grep -r` at) the directory that contains what you're looking for.
- *Diagnose:* `pwd`, then `ls`, to confirm your actual location (Lesson 01).
- *Fix:* Navigate to the correct directory, or point the command explicitly at the correct path.

**2. Forgetting the current working directory**
- *Symptom:* `find .` or `grep -r "x" .` returns results from an unexpected part of the filesystem.
- *Likely cause:* `.` always means "here" — and "here" may not be where you assumed.
- *Diagnose:* `pwd` before running any recursive search.
- *Fix:* `cd` to the intended starting point first.

**3. Using the wrong filename**
- *Symptom:* `find . -name "confg.yaml"` returns nothing.
- *Likely cause:* Typo in the filename.
- *Diagnose:* `ls` the directory you believe contains it, to see the real name.
- *Fix:* Correct the spelling and retry.

**4. Case-sensitive mismatch**
- *Symptom:* `grep "error" app.log` returns nothing, even though the log clearly says `"Error"`.
- *Likely cause:* `grep` is case-sensitive by default.
- *Diagnose:* Re-check the exact capitalization in the file (e.g. with `less`, Lesson 03).
- *Fix:* Add `-i` for a case-insensitive search.

**5. Confusing `grep` and `find`**
- *Symptom:* `grep "config.yaml" .` returns nothing, even though `config.yaml` clearly exists as a file.
- *Likely cause:* `grep` searches file *content*, not filenames — this command is looking for the literal text `config.yaml` written *inside* files, not for a file *named* that.
- *Diagnose:* Re-read Section 7's distinction.
- *Fix:* Use `find . -name "config.yaml"` instead.

**6. Forgetting quotes around patterns**
- *Symptom:* An error, or unexpected behavior, when the pattern contains spaces or special characters.
- *Likely cause:* The shell processed part of the pattern before `grep` ever received it (Section 5).
- *Diagnose:* Re-examine exactly what was typed, character by character.
- *Fix:* Wrap the pattern in quotes.

**7. Misunderstanding `*`**
- *Symptom:* Confusion about why `find . -name *.py` (unquoted) sometimes behaves differently from `find . -name "*.py"` (quoted).
- *Likely cause:* An unquoted `*` may be expanded by the shell itself before `find` runs, based on what matches in the *current* directory only — not what `find` would otherwise search for recursively.
- *Diagnose:* Recall Section 6's note on quoting wildcards for `find`.
- *Fix:* Always quote wildcard patterns given to `find`'s `-name` condition.

**8. Searching binary files as though they were normal text**
- *Symptom:* `grep` on a non-text file (an image, a compiled file) produces strange output or a "binary file matches" notice. (`grep` is taught here with text files; binary files may produce binary-match behavior or output that isn't useful as normal text.)
- *Likely cause:* The file isn't text at all — the same binary/text distinction from Lesson 03, Section 18.
- *Diagnose:* Consider whether the file you're searching is actually meant to be read as text.
- *Fix:* Restrict your search to text files you actually intend to inspect.

**9. Permission-related search errors**
- *Symptom:* `find` or `grep -r` reports "Permission denied" for some subdirectories, but still shows other results.
- *Likely cause:* You lack read/access permission on some part of the tree (Module 0.2 concept).
- *Diagnose:* `ls -l` on the specific directory named in the error.
- *Fix:* Do not reflexively reach for `sudo`; confirm you're actually supposed to have access there.

**10. Expecting output when there are no matches**
- *Symptom:* A search command "does nothing" — no text appears at all.
- *Likely cause:* This usually means exactly what it looks like — no matches exist — not that the command failed (Section 9).
- *Diagnose:* Re-check your pattern, path, and case-sensitivity assumptions before assuming something is broken.
- *Fix:* Adjust the search (broaden the pattern, check `-i`, confirm the path) if you believe a match should exist.

**11. Searching a huge directory tree unnecessarily**
- *Symptom:* A recursive search takes a long time and returns an overwhelming number of results.
- *Likely cause:* Starting the search from a much higher/broader directory than actually necessary.
- *Diagnose:* Consider how narrow the search actually needs to be.
- *Fix:* Start from the most specific directory that's still guaranteed to contain what you're looking for (Section 17).

**12. Using a path that does not exist**
- *Symptom:* `find nonexistent-folder -name "*.py"` produces an error about the path itself.
- *Likely cause:* The starting path was mistyped or never created.
- *Diagnose:* `ls` the parent directory to confirm what actually exists.
- *Fix:* Correct the path and retry.

---

## 15. Debugging Exercises

Work through each scenario's reasoning *before* reading the "Expected reasoning/result." These are not typed answer keys — they are meant to make you think first.

**Scenario 1 — Case mismatch**
- *Situation:* A log file contains the line `Connection Timeout at 12:04`.
- *Observed symptom:* `grep "timeout" server.log` returns no output.
- *Investigate:* Compare the exact text in the file against the exact pattern typed.
- *Likely root cause:* Case sensitivity — the file has `Timeout`, the search used `timeout`.
- *Learner task:* Rewrite the command so it matches regardless of capitalization.
- *Expected reasoning/result:* `grep -i "timeout" server.log` — using `-i` resolves the mismatch, matching `Timeout` correctly.

**Scenario 2 — Wrong file**
- *Situation:* You expect the word `retry` to appear in `worker.log`, but you actually run the search against `app.log`.
- *Observed symptom:* No matches, and you conclude the text "doesn't exist."
- *Investigate:* Confirm which file actually contains what you're looking for, using `ls` and/or `less`.
- *Likely root cause:* The target file argument was wrong, not the pattern.
- *Learner task:* Identify the correct target file before concluding anything about the pattern's presence.
- *Expected reasoning/result:* `grep "retry" worker.log` — the mistake was the file, not the search term.

**Scenario 3 — Wrong directory**
- *Situation:* You run `grep -r "database_url" .` expecting to find a config reference, but you're actually inside a subdirectory that doesn't contain the config file at all.
- *Observed symptom:* No matches.
- *Investigate:* `pwd`, then consider where the actual config file lives relative to here.
- *Likely root cause:* Current working directory doesn't contain (or isn't an ancestor of) the target file.
- *Learner task:* Determine the correct starting point for the search.
- *Expected reasoning/result:* Navigate up to the project root (or point the search explicitly at it) before re-running the recursive search.

**Scenario 4 — Wrong filename pattern with `find`**
- *Situation:* You're looking for Python files but write `find . -name "*.python"`.
- *Observed symptom:* No results, despite `.py` files clearly existing.
- *Investigate:* Check the actual file extension used in this project.
- *Likely root cause:* Incorrect assumed extension — Python files use `.py`, not `.python`.
- *Learner task:* Correct the pattern.
- *Expected reasoning/result:* `find . -name "*.py"`.

**Scenario 5 — Wildcard misunderstanding**
- *Situation:* You run `find . -name *.py` (no quotes) from a directory that itself contains one `.py` file, expecting it to also find `.py` files in subdirectories.
- *Observed symptom:* Subdirectory files are missing from the results, or an unexpected error appears.
- *Investigate:* Recall Section 6's and Section 14 (mistake 7)'s explanation of quoting.
- *Likely root cause:* The shell expanded the unquoted `*.py` itself, based only on what matched in the current directory, before `find` ever ran.
- *Learner task:* Rewrite the command so `find` receives the wildcard pattern itself.
- *Expected reasoning/result:* `find . -name "*.py"` (quoted) — this lets `find` apply the pattern at every level it traverses, not just the starting directory.

**Scenario 6 — Incorrect starting path**
- *Situation:* You type `find projct -name "*.log"` (typo: `projct` instead of `project`).
- *Observed symptom:* An error referencing the path itself, not "no matches."
- *Investigate:* Read the error message carefully — does it complain about the path, or report zero results?
- *Likely root cause:* The starting directory itself doesn't exist, due to a typo.
- *Learner task:* Identify and correct the typo.
- *Expected reasoning/result:* `find project -name "*.log"`.

**Scenario 7 — Permission-related error**
- *Situation:* `grep -r "key" .` prints several matches, but also several lines like `grep: ./restricted: Permission denied`.
- *Observed symptom:* Partial results mixed with error messages.
- *Investigate:* `ls -l` on the specific directory named in the error.
- *Likely root cause:* You lack read access to that particular subdirectory (Module 0.2 permissions concept).
- *Learner task:* Decide whether that restricted directory is actually relevant to your search, rather than assuming the whole command failed.
- *Expected reasoning/result:* The matches found elsewhere are still valid; the permission error only means that one subdirectory couldn't be checked — not that the entire search failed.

**Scenario 8 — Confusing content search with filename search**
- *Situation:* You want to know whether a file called `retry_policy.py` exists, and type `grep "retry_policy.py" .`.
- *Observed symptom:* No output, despite the file existing.
- *Investigate:* Re-read Section 7 — what is `grep` actually checking here?
- *Likely root cause:* `grep` searched file *content* for the literal text `retry_policy.py`; it never looked at filenames at all.
- *Learner task:* Rewrite this as a filename search.
- *Expected reasoning/result:* `find . -name "retry_policy.py"`.

**Scenario 9 — Binary/non-text file behavior**
- *Situation:* You run `grep "model" model.bin` on a binary model-weights file.
- *Observed symptom:* A message like `binary file model.bin matches` instead of readable lines, or garbled output.
- *Investigate:* Consider what kind of file this actually is (Lesson 03, Section 18).
- *Likely root cause:* The file isn't text; `grep` can technically scan it, but the result isn't meaningful the way it would be for a text file.
- *Learner task:* Decide whether searching this file with `grep` was ever a meaningful question.
- *Expected reasoning/result:* For binary files like model weights, `grep` on the raw content is not useful — you'd instead need to know something about the file's *name* or *metadata* (a `find` question), not its raw byte content.

**Scenario 10 — No-match result misunderstood as command failure**
- *Situation:* `grep "async" app.py` produces absolutely nothing.
- *Observed symptom:* No text at all appears; the learner assumes the terminal "froze" or the command errored.
- *Investigate:* Re-check the exit-status concept from Section 9 — did an error message actually appear, or just... nothing?
- *Likely root cause:* This is normal, correct behavior when there are genuinely zero matches — not a malfunction.
- *Learner task:* Confirm, separately (e.g. by opening the file with `less`), whether the word `async` is actually present at all.
- *Expected reasoning/result:* If `less app.py` confirms `async` truly isn't in the file, then `grep`'s silent, empty result was the *correct* answer all along.

---

## 16. Common Misconceptions

- **"`grep` finds files."** — It finds *lines of text inside files* that match a pattern; it never reports on filenames unless the filename text happens to appear as content somewhere.
- **"`find` searches inside files."** — It does not read file content at all; it only examines filesystem entries and their properties — name, type, location.
- **"`grep` and `find` do the same thing."** — They answer fundamentally different questions: content vs. structure (Section 7).
- **"No output means the command crashed."** — No output from `grep` or `find` most commonly means no matches were found — a valid, correct result, not a failure (Section 9, Section 15 Scenario 10).
- **"`*` always means the same thing everywhere."** — Its behavior depends on whether the shell expands it first or a command like `find` interprets it directly, which in turn depends on quoting (Section 6, Section 14 mistake 7).
- **"A search command automatically searches the entire computer."** — Both `grep -r` and `find` only search wherever you point them — starting from a specific path you provide, never the whole filesystem, unless you explicitly told them to start from the root.
- **"Searching is harmless regardless of where I run it."** — The searches taught in this lesson do not modify data, but running a broad recursive search from the wrong (e.g. far too large, or permission-restricted) location can be slow, noisy, or produce misleading partial results (Section 14, mistakes 1, 9, 11).
- **"Recursive searching is always the best option."** — A narrower, targeted search is often faster and gives cleaner, more relevant results than blindly searching an entire large tree (Section 17).

---

## 17. Trade-offs and Engineering Habits

- **Targeted search vs. recursive search** — a search scoped to exactly the directory you need is faster and easier to interpret than a broad recursive search across an entire project.
- **Precision vs. convenience** — a very specific pattern or filename returns fewer, more relevant results; a broad, loose one is quicker to type but noisier to sift through.
- **Small search scope vs. large search scope** — starting from a narrower, more specific directory reduces both the time taken and the chance of irrelevant matches.
- **Literal matching vs. pattern matching** — literal text is simpler and predictable; wildcard/pattern-based matching (Sections 5–6) is more flexible but requires more care to get right.
- **Readability vs. command complexity** — a simple, well-chosen `grep`/`find` command is easier to trust and re-use than a convoluted one stacking many options at once.
- **Speed vs. unnecessary filesystem traversal** — recursively searching a huge, irrelevant portion of a filesystem (e.g. starting from `/` instead of your project directory) costs real time for no benefit.

Good habits to build now:

1. **Start with a narrow search** — the most specific directory you're confident contains the answer, rather than the broadest one that might.
2. **Confirm the current directory** (`pwd`) before any recursive search.
3. **Inspect the path before searching** — a quick `ls` to sanity-check that the location you're about to search actually looks right.
4. **Use precise patterns** — an exact filename or exact text when you know it, rather than an overly broad guess.
5. **Avoid unnecessarily searching huge trees** — scope your search to what's actually relevant.
6. **Understand what a command will inspect before running it** — content or structure, and from where.
7. **Treat command output as evidence** — a match, or the absence of one, tells you something real about the filesystem or file content, worth trusting over assumption.
8. **Distinguish "no result" from "command error"** — re-read Section 9 whenever you're unsure which one you're looking at.

---

## 18. Practical Exercises

All Level 3–5 practical work must be done inside a disposable directory (for example, one under `/tmp/`) created specifically for these exercises. Never perform any exercise against the real Applied AI Engineering project directory.

### Level 1 — Recognition

1. Which command searches for text *inside* files: `grep` or `find`?
2. Which command searches for files *by name*: `grep` or `find`?
3. What does the `-i` option do for `grep`?
4. What does the `-r` option do for `grep`?
5. What does `-type f` restrict `find`'s results to?
6. What does `-type d` restrict `find`'s results to?
7. In `find . -name "*.py"`, what does the `.` represent?
8. In `grep -n "error" app.log`, what does `-n` add to the output?

### Level 2 — Understanding

1. Explain why `grep "config.yaml" .` would not find a file literally named `config.yaml`.
2. Predict the output of `grep -c "error" app.log` if the file contains three lines mentioning "error."
3. Explain why `find . -name *.py` (unquoted) can behave differently from `find . -name "*.py"` (quoted).
4. Why would `grep "Timeout" app.log` fail to match a line containing `timeout` (lowercase)?
5. Explain, in your own words, why `find` never needs a `-r`/recursive flag the way `grep` does.
6. If `find . -name "settings.yaml"` returns nothing, what are two different possible explanations?
7. Why does `grep -r "key" .` sometimes print both matches and permission-denied errors in the same run?
8. Explain why "no output" from a search command is not automatically evidence that something is broken.

### Level 3 — Application

Perform each of these inside a disposable directory you create for this purpose (e.g. `/tmp/lesson04-practice`).

1. Create a small text file containing at least one line with the word `error` in it, and search it with `grep` for that word.
2. Add a line containing `Error` (capitalized) to the same file, and run a case-insensitive search that matches both.
3. Re-run your search with line numbers shown.
4. Create a small directory tree with at least two subdirectories, each containing a text file, and run a recursive `grep` search across the whole tree for a word you placed in one of the files.
5. Create at least two `.py`-named files (empty or with placeholder content is fine) inside your practice directory, and use `find` to locate all of them.
6. Use `find` with `-type d` to list only the directories in your practice tree.
7. Create a file named `worker.log` containing a line with the word `retry`, and use `find` to confirm the file's location before using `grep` to confirm the word's presence.
8. Use `grep -l` across multiple files in your practice directory to identify which specific files contain a chosen word, without displaying the matching lines themselves.

### Level 4 — Debugging

For each scenario, state the likely cause and the safe fix — explain your reasoning, don't just guess a command.

1. `grep "warning" app.log` returns nothing, but you can see the word `Warning` in the file when you open it with `less`. What's wrong?
2. `find . -name "app.py"` returns nothing, even though `app.py` exists somewhere in a subdirectory two levels down. What are two possible explanations?
3. `grep -r "timeout" .` returns results, but also several `Permission denied` lines. Does this mean the whole command failed?
4. You meant to search for files named `report.csv`, but typed `grep "report.csv" .` instead. What's the conceptual mistake here?
5. `find . -name *.log` (no quotes) behaves unexpectedly compared to what you intended. What's the likely cause?
6. You're confident a config file exists, but `find configs -name "settings.yml"` finds nothing, while the file is actually named `settings.yaml`. What happened?
7. `grep "error" model.bin` produces a strange one-line notice instead of matching text lines. What kind of file is this likely to be?
8. You ran a recursive `grep -r` from your home directory instead of your project directory, and it took a very long time with too many irrelevant results. What should you have done differently?

### Level 5 — Integration

These combine navigation (Lesson 01), file operations (Lesson 02), file viewing (Lesson 03), and searching (this lesson). Perform all of them inside a disposable workspace directory.

1. Starting from your home directory, navigate into a new disposable workspace, create a small project-like structure with a few text files and subdirectories, and use `find` to confirm the structure exists as expected.
2. Create a simulated log file with several lines, one of which contains the word `ERROR`; use `tail` (Lesson 03) to view the end of the file, then confirm the error's exact line number using `grep -n`.
3. Copy (`cp`, Lesson 02) a sample configuration file into a new subdirectory, then use `find` to confirm both the original and the copy exist, and `grep` to confirm both contain identical content.
4. Create three files with different extensions (e.g. `.py`, `.txt`, `.csv`) in a small directory tree, and use `find` with `-name` to isolate just one extension at a time.
5. Simulate a small investigation: create a "log" file with several normal-looking lines and one line containing `FATAL`, use `grep -i` to locate it, note its line number, then use `less` (Lesson 03) to jump to that area of the file and read the surrounding context.

---

## 19. Mini-Project — Command-Line Project Search Investigator

**Scenario:** You've joined a small AI project you've never seen before. Something isn't working, and before touching anything, you need to orient yourself using only `find` and `grep` — the same situation described in Sections 2 and 11.

**Setup:** Create a disposable project-like directory yourself — for example:

```bash
mkdir -p /tmp/search-investigator-project/{app,tests,data,models,logs,configs}
cd /tmp/search-investigator-project
```

Inside it, create a few small, harmless learner-created files of your own choosing — for example: one or two `.py` files inside `app/`, a `.yaml` or `.txt` configuration file inside `configs/`, a small `.csv` inside `data/`, and a log file inside `logs/` containing several normal-looking lines plus one line containing the word `ERROR` (or `FATAL`) somewhere near the end, simulating a real failure.

**Tasks:**

1. **Identify the correct starting directory** — confirm with `pwd` that you're at the root of this disposable project before searching.
2. **Locate files using `find`** — find every file inside `configs/`.
3. **Locate specific file types** — find every `.py` file in the entire project tree.
4. **Search file contents using `grep`** — search the log file for the word `error`.
5. **Perform both case-sensitive and case-insensitive searches** — first without `-i`, then with `-i`, and compare the results.
6. **Investigate the simulated error** — use `grep -n` to find the exact line number of the failure in the log, then explain what you'd do next (e.g. open the file with `less` around that line, per Lesson 03).
7. **Explain which command was appropriate and why** — for each task above, write one sentence justifying why you chose `grep` or `find` specifically.
8. **Document your findings** — write a short summary (a few sentences) of what you found: which files exist, what the simulated failure was, and where exactly it was located.

**Expected observations:** a case-sensitive search for `"error"` may miss the failure if you wrote it as `"ERROR"`; the case-insensitive version should reliably find it regardless of how you capitalized it when creating the file.

**Debugging challenge:** deliberately mistype a filename in one `find` command and one word in a `grep` command, observe the "no result" outcome, and correctly reason (per Section 9) that this reflects a mistaken input, not a broken command — then correct both.

**Completion criteria:** you can state, without checking notes, which command you'd use for any new question resembling "where is X" versus "does anything contain Y," and you've correctly located the simulated error using `grep -n`.

**Cleanup instructions:**

```bash
cd /tmp
rm -r /tmp/search-investigator-project
```

**Reflection questions:**

- Which command did you reach for first when you didn't yet know where anything was?
- Was there a moment where you almost used the wrong command (`grep` for a filename, or `find` for content)? What corrected your thinking?
- How would this same approach apply to a real, much larger AI project you've never seen before?

---

## 20. Review

Key terms and commands from this lesson:

- **Searching** — locating specific content or specific filesystem objects that you don't already know the exact location of.
- **`grep`** — searches file *content* line by line for a matching pattern; options covered: `-n` (line numbers), `-i` (case-insensitive), `-r` (recursive), `-l` (filenames only), `-c` (count).
- **`find`** — searches the *filesystem* for files/directories matching conditions; conditions covered: `-name` (by filename, literal or wildcard), `-type f` (files only), `-type d` (directories only).
- **Pattern** — the text (or, later, regular expression) `grep` compares each line against; literal patterns were this lesson's focus.
- **Recursion** (as applied to search) — descending into subdirectories automatically; `find` always does this; `grep` needs `-r` to do it.
- **Standard output / exit status** — search results appear via standard output; success/failure is signaled separately via exit status; "no matches" is not the same as "command failed."
- **Safety** — the specific `grep` and `find` commands taught in this lesson perform read/inspection operations and do not modify or delete the searched files.
- **AI Engineering relevance** — locating datasets, configs, model artifacts, and log errors in exactly the same way, applied to AI-specific project structures.

Compact command reference:

| Command | Purpose | Example |
|---|---|---|
| `grep "pattern" file` | Search one file's content | `grep "timeout" server.log` |
| `grep -n "pattern" file` | ...with line numbers | `grep -n "timeout" server.log` |
| `grep -i "pattern" file` | ...case-insensitively | `grep -i "timeout" server.log` |
| `grep -r "pattern" dir` | ...recursively through a directory | `grep -r "timeout" logs/` |
| `grep -l "pattern" files` | Show only matching filenames | `grep -rl "timeout" logs/` |
| `grep -c "pattern" file` | Count matching lines | `grep -c "timeout" server.log` |
| `find . -name "name"` | Find by exact name | `find . -name "config.yaml"` |
| `find . -name "*.ext"` | Find by wildcard pattern | `find . -name "*.py"` |
| `find . -type f` | Find files only | `find . -type f` |
| `find . -type d` | Find directories only | `find . -type d` |

Final mental model:

```text
grep
  ↓
search CONTENT
"what's written inside this file/these files?"

find
  ↓
search FILESYSTEM ENTRIES and their properties
"what files/directories exist, matching this description?"
```

Expanded into practical engineering reasoning: whenever you catch yourself asking **"where is...?"** or **"what files are...?"**, reach for `find`. Whenever you catch yourself asking **"does anything say...?"** or **"where does this text appear?"**, reach for `grep`. And whenever the real question needs both — "which files of this kind contain this text?" — recognize it as a two-step problem for now, to be connected smoothly once you learn pipes in a later lesson.

---

## 21. Interview / Architecture Questions

1. What is `grep` used for?
2. What is `find` used for?
3. What is the fundamental difference between `grep` and `find`?
4. How would you find all Python files in a project?
5. How would you search for a specific word inside a set of files?
6. Why might `grep` return no output, even when you're confident the text exists somewhere in the project?
7. Why might `find` return no files, even when you're confident the file exists?
8. What does "recursive search" mean, in the context of `grep -r` or `find`'s default traversal?
9. Why can recursive searches be expensive, especially on a large or deeply nested directory tree?
10. What is the difference between searching file content and searching filenames?
11. Why should search scope (the starting directory) be deliberately controlled rather than always searching from the broadest possible location?
12. How can command-line searching help you debug a production service, before any dedicated logging or monitoring tool is involved?
13. Describe a realistic way an AI engineering mistake could result from searching too broadly, or from a case-sensitivity assumption that turned out to be wrong.

---

## 22. Production Application

The same two commands remain part of an engineer's everyday toolkit once systems reach production, typically as an immediate, no-setup-required first step:

- **Inspecting application logs** — `grep -i "error" service.log` to quickly check whether anything went wrong, before reaching for any dedicated tool.
- **Locating configuration files** — `find /etc/myservice -name "*.conf"` (or an equivalent project-specific path) to confirm exactly what configuration exists and where.
- **Identifying generated artifacts** — `find output/ -type f` to see exactly what a job actually produced.
- **Finding source references** — `grep -r "functionName" src/` to see every place a function is used before changing it.
- **Investigating failures** — combining `find` (to locate the relevant log or output file) with `grep` (to locate the specific failure within it), exactly as practiced in this lesson's mini-project.
- **Locating datasets and model artifacts** — the same `find`-by-name/type approach used throughout Section 11, at production scale.
- **Diagnosing deployment-related files** — confirming a specific file was actually included in a deployed package, using `find`.
- **Inspecting an unfamiliar repository** — the fastest way to start understanding a codebase you've just inherited or joined, before any documentation review.

This lesson does not teach production observability systems, log aggregation platforms, or DevOps tooling — those build on top of exactly these same foundational ideas (locating content, locating files) at a much larger, automated scale, and are covered at a later stage of this roadmap. The point here is narrower and more durable: **no matter how sophisticated the tooling around you becomes, `grep` and `find` remain the fastest, always-available way to answer a direct question about a filesystem or its content.**

---

## 23. Relationship to Previous and Next Lessons

The progression through Module 0.3 so far:

- **Lesson 01 — Navigation:** know *where you are* in the filesystem.
- **Lesson 02 — File operations:** *manage* filesystem objects — create, copy, move, delete.
- **Lesson 03 — Viewing files:** *inspect the contents* of a file once you've located it.
- **Lesson 04 — Searching (this lesson):** *locate* relevant files and content when you don't already know exactly where they are.
- **Lesson 05 — Text processing (next):** *transform and process* text/data, often building on what you've found via searching.
- **Lesson 06 — Pipes/redirection:** *connect* commands together and control where output goes — including, eventually, connecting `find` and `grep` together directly, and sending search results into further processing.

This lesson does not teach Lesson 05 or Lesson 06's material — the two mentions above exist only to show *why* searching comes before them: once you can locate the right files and content, the natural next steps are to process that text (Lesson 05) and to connect commands together so results can flow from one into another (Lesson 06).

---

## 24. Scope Boundary

This lesson teaches only:

- `grep`
- `find`
- foundational (literal-text) search patterns
- safe command-line searching
- basic recursive searching
- search debugging
- practical software- and AI-engineering search use

This lesson deliberately does **not** deeply teach:

- `sort`, `uniq`, `cut` (text processing — Lesson 05)
- `xargs`, pipes, redirection (Lesson 06)
- environment variables (later lesson)
- shell scripting (later lesson)
- permissions administration (later lesson)
- Git (a separate, later roadmap topic)
- advanced regular expressions (beyond literal-text patterns, intentionally deferred)
- advanced filesystem internals
- Docker, Kubernetes, or cloud infrastructure
- observability platforms or advanced DevOps
- Python (or any language's) filesystem APIs
- advanced automation

These are separate roadmap topics and stages, mentioned in this lesson only where necessary for context. This lesson is not a preview course for any of them.

---

_This lesson is complete. It covers `grep` and `find` only. The remaining Module 0.3 topics are covered in subsequent lessons within this module._
