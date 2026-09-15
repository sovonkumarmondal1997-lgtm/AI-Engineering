# Module 0.3 — Command Line

## Lesson 02 — File Operations

**Module:** Command Line
**Roadmap reference:** Stage 0 — Module 0.3 — Command Line
**Concept(s) covered:** `mkdir`, `cp`, `mv`, `rm`
**Status:** Complete
**Builds on:** 01-navigation.md (`pwd`, `ls`, `cd`) and Module 0.2 (filesystem, processes, permissions, shell)

---

## Learning Objectives

After completing this lesson you will be able to:

- Explain what a file operation is and why operating systems provide them.
- Create directories, including nested directories, using `mkdir`.
- Copy files and directories using `cp`, and explain when recursion is required.
- Move and rename files and directories using `mv`, and explain why moving and renaming are the same underlying operation.
- Delete files and directories using `rm`, and explain why deletion on the command line is far less forgiving than a graphical "trash" or "recycle bin."
- Reason correctly about source and destination paths, in both absolute and relative form.
- Predict what a file-operation command will do before running it.
- Recognize and avoid the highest-risk mistakes in file operations (wrong directory, bad wildcard, unintended overwrite, unrecoverable deletion).
- Diagnose and fix common file-operation errors.
- Explain how these four commands show up in real software-engineering and AI-engineering workflows — and what breaks when they're used carelessly.

---

## 1. What Are File Operations?

In the previous lesson you learned to move *yourself* (your shell's current position) around the filesystem, using `pwd`, `ls`, and `cd`. Those commands never touched a single file — they only let you look around.

**File operations** are the commands that actually change the filesystem: they create, duplicate, relocate, or remove files and directories. In this lesson you'll learn the four foundational ones:

| Command | What it does |
|---|---|
| `mkdir` | Creates a new directory |
| `cp` | Copies a file or directory |
| `mv` | Moves or renames a file or directory |
| `rm` | Deletes (removes) a file or directory |

A few terms, introduced carefully since they'll be used constantly from here on:

- **File** — a named unit of stored data (text, code, an image, a dataset, a model checkpoint — anything saved to disk).
- **Directory** — a container that organizes files (and other directories) under a name, as you learned in Lesson 01.
- **Source** — the file or directory an operation reads *from* / acts *on*.
- **Destination** — the location or name an operation produces *as a result*.

Every file operation you'll learn in this lesson follows one shape:

```text
SOURCE → OPERATION → DESTINATION
```

`mkdir` is a slight special case: it has no "source" to read from — it only has a destination (the new directory being created). `cp`, `mv`, and `rm` all involve a source; `cp` and `mv` also involve a destination.

---

## 2. Why File Operations Exist

An operating system has to give programs (and people) a reliable way to organize and manipulate stored data. Without built-in, standardized operations for this, every program would need to invent its own way of creating folders, duplicating data, relocating it, or discarding it — and no two programs would agree on how to do it safely.

Command-line file operations exist because:

- **Organization requires containers.** As soon as you have more than a handful of files, you need directories to group them — this is why `mkdir` exists.
- **Data often needs to exist in two places at once.** Backups, templates, and default configurations all require duplication without destroying the original — this is why `cp` exists.
- **Data often needs to be relocated or renamed without duplicating it.** Reorganizing a project, or simply correcting a filename, shouldn't require making a copy and manually deleting the old one — this is why `mv` exists, and why it also handles renaming.
- **Storage is finite, and clutter has real cost.** Temporary files, obsolete outputs, and failed experiment artifacts need to be reliably removable — this is why `rm` exists.

These four operations are not arbitrary conveniences — they are the minimum vocabulary needed to manage anything stored on a computer. Every higher-level tool you will eventually use (IDEs, Git, Docker, cloud storage consoles, ML pipeline orchestrators) performs some version of these same four operations underneath a friendlier interface.

---

## 3. File Operations and the Operating System

Recall from Module 0.2: the **filesystem** is how the operating system organizes and tracks where every file and directory physically lives, the **shell** is the program that reads what you type and turns it into action, and every running program is a **process** that asks the operating system to do things on its behalf via requests called **system calls**.

`mkdir`, `cp`, `mv`, and `rm` are just command-line programs. When you run one, this is the layered path your instruction travels:

```text
You type a command
        ↓
Terminal displays it, shell reads it
        ↓
Shell parses the command name and its arguments (paths, options)
        ↓
Shell locates and runs the program (mkdir / cp / mv / rm)
        ↓
That program asks the operating system to create/copy/move/delete,
via system calls, on your behalf
        ↓
Operating system carries out the change on the actual filesystem
```

This lesson stays at that top conceptual layer — "these commands cause real filesystem changes through the operating system" — without going deeper into how the filesystem itself stores data internally. That level of detail (and terms like inodes or journaling) belongs to later, dedicated filesystem material, not here.

The one practical consequence worth internalizing now: because these commands go through the *real* operating system, their effects are real and immediate. There is no "preview mode." A command that succeeds has already changed something on disk.

---

## 4. Source and Destination

The mental model for almost every command in this lesson is:

```text
SOURCE → OPERATION → DESTINATION
```

- `mkdir destination` — no source; only a destination (the new directory).
- `cp source destination` — copy source's contents into/as destination; source is untouched.
- `mv source destination` — relocate/rename source so it now exists at destination; source no longer exists at its old location.
- `rm source` — remove source; there is no destination at all.

Both source and destination can be written as **absolute paths** (starting from `/`) or **relative paths** (interpreted starting from your shell's current working directory) — exactly as covered in Lesson 01. This lesson does not re-teach that material, but it matters enormously here, because:

> **Getting source or destination wrong in a file operation doesn't just fail loudly — it can silently do something you didn't intend, especially with `cp` and `mv`, and it can be unrecoverable with `rm`.**

A few illustrative examples (none of these are executed against anything real — they illustrate the model only):

```bash
cp notes.txt backup.txt                 # source: notes.txt (relative)   → destination: backup.txt (relative)
cp notes.txt /tmp/backup.txt            # source: notes.txt (relative)   → destination: /tmp/backup.txt (absolute)
mv /tmp/draft.txt ./draft-final.txt     # source: absolute               → destination: relative
rm old-report.txt                       # source only — no destination
```

Because relative paths depend entirely on your current working directory, the single most important habit for this entire lesson is: **run `pwd` (and often `ls`) immediately before any file operation whose outcome you're not 100% sure of.** This costs a few seconds and prevents the majority of real-world file-operation mistakes.

---

## 5. The `mkdir` Command

`mkdir` ("make directory") creates a new, empty directory.

### Basic syntax

```bash
mkdir directory-name
```

### Examples

```bash
mkdir project
mkdir data
mkdir models
```

Each of these creates one new, empty directory inside your current working directory (relative path), or at the exact location given if you supply an absolute path.

### Creating nested directories

By default, `mkdir` only creates **one level at a time**, and only if its immediate parent already exists:

```bash
mkdir project/data/raw
```

If `project` or `project/data` doesn't already exist, this fails — `mkdir` refuses to guess whether you meant to create the whole chain.

### `mkdir -p` — create parent directories as needed

The `-p` flag ("parents") tells `mkdir` to create every missing directory along the path, not just the final one:

```bash
mkdir -p project/data/raw
```

This creates `project`, then `project/data`, then `project/data/raw` — all in one command, only creating whatever doesn't already exist. `-p` is also "safe" in the sense that it won't error if the directory already exists, whereas plain `mkdir` errors if the target directory is already there.

A **parent directory** is simply the directory that directly contains another — `project/data` is the parent of `project/data/raw`. `mkdir` (without `-p`) requires the parent to already exist because, without that requirement, a single typo in a long nested path could silently scatter unintended directories across your filesystem.

---

## 6. The `cp` Command

`cp` ("copy") duplicates a file or directory. The original (source) is left completely untouched; a new, independent copy is created at the destination.

### Copying a file

```bash
cp source-file.txt destination-file.txt
```

If `destination-file.txt` doesn't exist, it's created as a copy. If it *does* exist, its contents are silently overwritten by default (see the Safety section below for how to guard against this).

### Copying a file into a directory

```bash
cp report.txt archive/
```

If `archive/` is an existing directory, this places a copy named `report.txt` inside it — the destination is treated as a *container*, not a new filename, because it's a directory.

### Copying a directory — recursion

Trying to copy a directory the same way you copy a file fails:

```bash
cp data backup
# cp: -r not specified; omitting directory 'data'
```

This is deliberate. A directory can contain an unknown number of files and subdirectories — copying "all of that" is a fundamentally bigger, more consequential operation than copying one file, so `cp` requires you to say so explicitly.

**Recursive** means "repeat this operation on every item inside, and every item inside those, and so on, until there's nothing left to descend into." The `-r` (or `-R`) flag tells `cp` to do exactly that:

```bash
cp -r data backup
```

This copies `data` and everything inside it — files and subdirectories, at any depth — into a new directory called `backup`.

### Useful, beginner-relevant options

| Option | Meaning | Why it matters |
|---|---|---|
| `-r` / `-R` | Recursive — required to copy a directory | Without it, `cp` refuses to copy directories at all |
| `-i` | Interactive — asks for confirmation before overwriting an existing destination file | Protects against silently destroying an existing file |
| `-n` | No-clobber — never overwrites an existing destination file | An even stronger, non-interactive guard than `-i` |

This lesson intentionally does not cover every `cp` flag that exists — only the ones that matter for building a correct, safe mental model as a beginner.

### `cp` vs `mv`, at a glance

`cp source destination` results in **two** copies of the data existing (source is untouched). `mv source destination`, covered next, results in only **one** copy existing — moved, not duplicated.

---

## 7. The `mv` Command

`mv` ("move") relocates a file or directory to a new location, a new name, or both. Unlike `cp`, the source stops existing at its original location — nothing is duplicated.

### Moving a file

```bash
mv report.txt archive/
```

This moves `report.txt` out of the current directory and into `archive/`. After this runs, `report.txt` no longer exists in the original location — only inside `archive/`.

### Renaming a file

```bash
mv draft.txt final.txt
```

This is still `mv` — moving `draft.txt` to a new destination that happens to be in the *same* directory, under a *different name*. There is no separate "rename" command on the command line; **renaming is simply a move where the destination's directory doesn't change, only its name does.**

### Moving/renaming directories

`mv` works the same way on directories, and — unlike `cp` — does **not** require a recursive flag:

```bash
mv project old-project        # rename a directory
mv project archive/           # move a directory into another directory
```

There's no `-r` requirement here because `mv` isn't duplicating the directory's contents one item at a time — conceptually, it's relocating the directory as a whole (see Internal Mechanics below for why).

### Why renaming doesn't require copying file contents

When a move happens **within the same filesystem** (in practice: usually within the same disk/partition), the operating system does not need to read and rewrite the file's actual data at all. It only needs to update where that file is *recorded* as living — essentially relabeling an entry in the directory structure. This is why renaming or moving a huge file within the same disk is nearly instant, regardless of the file's size.

**This is a high-level model, not a universal guarantee.** When source and destination are on *different filesystems* — for example, moving a file from your main disk to a USB drive, or across certain network/cloud-mounted storage — there is no shared directory structure to simply relabel. In that case, `mv` has no choice but to read the entire file's data, write a full copy at the new location, and then delete the original — behaving, internally, much more like a `cp` followed by an `rm`. The *command* you type doesn't change; the *work involved* does, depending on where source and destination physically live.

---

## 8. The `rm` Command

`rm` ("remove") deletes files and directories.

### Deleting a file

```bash
rm old-notes.txt
```

### The most important warning in this lesson

> **Command-line deletion is not like dragging a file to a desktop Recycle Bin or Trash.** There is no built-in undo, no staging area, and typically no confirmation unless you explicitly ask for one. Once `rm` succeeds, recovering the data is — in the general case — not something the command line offers you a way to do.

### Interactive deletion

```bash
rm -i old-notes.txt
```

`-i` makes `rm` ask you to confirm before deleting each file — a simple, valuable safety net, especially while you're still building confidence.

### Deleting directories — recursion

Just like `cp`, `rm` refuses to delete a directory unless told to act recursively:

```bash
rm project
# rm: cannot remove 'project': Is a directory
```

```bash
rm -r project
```

`-r` tells `rm` to delete the directory *and* everything inside it, at any depth. This is exactly the same "recursive" concept introduced with `cp -r` — repeat the operation on every item inside, all the way down.

### Why `rm -rf` is dangerous

You will encounter `rm -rf` frequently in tutorials and real-world scripts. The `-f` ("force") flag suppresses confirmation prompts and ignores errors about files that don't exist, and combined with `-r` it will silently delete an entire directory tree, with **no confirmation of any kind**, regardless of how much is inside it.

This lesson will **not** instruct you to run `rm -rf` against any real directory. If you ever see it demonstrated, understand it conceptually as: *"recursively delete everything here, ask nothing, skip missing-file errors" — the single most consequential command combination in this entire lesson.* The only place it is acceptable to experiment with `-r` (with or without `-f`) is against a **disposable directory you created specifically for practice**, which is exactly what Section 17's demonstration and Section 23's mini-project do.

### Summary of `rm` forms covered

| Form | Behavior |
|---|---|
| `rm file` | Delete one file; errors if it's a directory |
| `rm -i file` | Ask for confirmation before deleting |
| `rm -r directory` | Recursively delete a directory and everything inside it |
| `rm -rf directory` | Recursively delete with no confirmation and no error on missing files — extremely dangerous; practice only on disposable directories |

---

## 9. Copy vs Move vs Rename vs Delete

| | `cp` (copy) | `mv` (move) | `mv` (rename) | `rm` (delete) |
|---|---|---|---|---|
| **Purpose** | Duplicate data | Relocate data | Change a name | Remove data |
| **Original remains?** | Yes | No | No (it *is* the "new" one, renamed) | No — nothing remains |
| **Destination created?** | Yes, a new copy | Yes, the relocated item | Yes, under the new name | No destination at all |
| **Destructive?** | No | Not to the data itself (but can overwrite an existing destination) | Not to the data itself | Yes — potentially unrecoverable |
| **Common use** | Backups, templates, duplicating configs | Reorganizing files/directories | Fixing/clarifying a filename | Cleaning up temporary or obsolete data |
| **Risk level** | Low (worst case: unwanted overwrite) | Low–Medium (source disappears from old location) | Low–Medium | **High** |
| **Example** | `cp config.yaml config.backup.yaml` | `mv results/ archive/` | `mv draft.txt final.txt` | `rm -r old-experiment/` |

---

## 10. File Operations with Paths

Everything from Lesson 01 about absolute vs. relative paths applies directly here — this section only shows it in action, without re-teaching the underlying concepts.

```bash
# Absolute source and destination — unambiguous regardless of current directory
cp /home/learner/projects/ai-project/config.yaml /home/learner/backups/config.yaml

# Relative source and destination — interpreted from the current working directory
cp config.yaml ../backups/config.yaml

# Mixed — perfectly valid; each path is resolved independently
mv notes.txt /home/learner/documents/

# Parent-directory reference used as a destination
cp report.txt ../
```

**Bash/Linux/WSL2/Git Bash** all use forward slashes (`/`) and the commands shown throughout this lesson.

**PowerShell** uses different command names entirely for the same concepts (introduced fully in Section 15) and traditionally uses backslashes (`\`), though it also accepts forward slashes in most cases:

```powershell
Copy-Item .\config.yaml ..\backups\config.yaml
```

The underlying mental model — source, destination, absolute vs. relative — is identical across all of these environments. Only the command names and path separator conventions differ.

---

## 11. Wildcards and Multiple Files

A **wildcard** is a symbol that stands in for "some text I don't want to spell out." The most common one, `*`, means "zero or more of any characters."

```bash
*.txt
```

This matches every filename in the current directory ending in `.txt`.

The critical concept to understand: **the shell — not `cp`, `mv`, or `rm` — expands the wildcard before the command ever runs.** When you type:

```bash
rm *.txt
```

the shell first looks at the current directory, finds every matching filename, and rewrites your command as if you had typed each one out individually (e.g. `rm draft.txt notes.txt report.txt`). The `rm` program never even sees the `*` — it only receives the final, already-expanded list of filenames.

This matters enormously for safety: **a wildcard can match far more than you expect**, especially in a directory you haven't checked with `ls` first. This lesson does not cover advanced pattern-matching (character classes, multiple wildcards, brace expansion, etc.) — only this one essential concept, because it's a prerequisite for using `cp`, `mv`, and `rm` safely with more than one file at a time.

> **Safety rule:** before running any destructive command with a wildcard, run the equivalent `ls` first (e.g. `ls *.txt`) to see exactly what would be affected — *then* substitute in `rm`, `mv`, or `cp` once you've confirmed the match is what you intended.

---

## 12. Recursive Operations

**Recursive** means: perform this same operation on a directory's contents, and on the contents of any subdirectories inside it, and so on, until there is nothing left to descend into.

Directories are the reason recursion exists as a concept here — a file has no "contents" to descend into, but a directory might contain an arbitrarily deep tree of other directories and files.

- `cp -r` — required to copy a directory, because copying means visiting and duplicating every file at every depth.
- `rm -r` — required to delete a non-empty directory, because deleting means removing every file at every depth before the (now-empty) directory itself can be removed.
- `mv` — notably does **not** need a recursive flag (Section 7 explains why: it typically relocates the directory as a whole rather than walking its contents).

Safe demonstration (disposable directory only):

```bash
mkdir -p /tmp/recursion-demo/level1/level2
cp -r /tmp/recursion-demo/level1 /tmp/recursion-demo/level1-copy
rm -r /tmp/recursion-demo
```

This creates a small nested structure, recursively copies it, and then recursively removes the *entire* disposable demo — never touching anything outside `/tmp/recursion-demo`.

---

## 13. Internal Mechanics

The layered path from Section 3, applied specifically to each command:

```text
Terminal → Shell → command (mkdir/cp/mv/rm) → operating system → filesystem
```

1. The shell parses what you typed, expanding any wildcards (Section 11) and resolving relative paths against the current working directory (Lesson 01).
2. The shell locates and runs the requested program — `mkdir`, `cp`, `mv`, or `rm`.
3. That program requests the operating system perform the change via system calls (Module 0.2).
4. The operating system checks whether the request is allowed — this is where **permissions** (a full Module 0.3 topic on its own, later) can cause a command to fail with "Permission denied."
5. The operating system carries out the change: creating a directory entry (`mkdir`), duplicating file contents (`cp`), relabeling or duplicating-then-removing (`mv` — see below), or removing a directory entry and freeing the associated storage (`rm`).
6. The filesystem's internal record of what exists, and where, is updated to reflect the change.

**For `mv` specifically:** as explained in Section 7, when source and destination are on the *same* filesystem, the operating system typically just updates the directory entry — no file content is read or rewritten. When they're on *different* filesystems, there is no shared entry to relabel, so the operating system falls back to copying the data to the new location and then removing the original. Same command, different amount of underlying work, depending entirely on where the source and destination physically live.

This lesson deliberately stops at this level of detail. Deeper filesystem implementation topics — inodes, journaling, the virtual filesystem layer, ext4-specific behavior, overlay filesystems, distributed filesystems — are out of scope here and belong to later, dedicated material.

---

## 14. Real-World Software Engineering Use Cases

- **Organizing source code**: `mkdir src tests docs` when starting a new project.
- **Preparing project directories**: `mkdir -p project/{data,models,configs}`-style scaffolding (the brace expansion itself is out of scope; the *reason* for doing it — setting up structure before work begins — is the point).
- **Moving build artifacts**: `mv dist/app.bin release/` after a build step.
- **Copying configuration templates**: `cp config.template.yaml config.yaml` so you can edit a working copy without losing the original template.
- **Organizing datasets**: `mkdir -p data/{raw,processed}`, then `mv downloaded_file.csv data/raw/`.
- **Moving model artifacts**: `mv checkpoint_epoch_12.pt models/best/`.
- **Creating experiment directories**: `mkdir experiments/run-2026-09-10-lr0.001`.
- **Managing logs**: `mv training.log logs/archive/`.
- **Backup/copy workflows**: `cp -r project project-backup-before-refactor`.
- **Preparing deployment artifacts**: `cp -r build/ deploy-package/`.
- **CI/CD workspace operations**: automated pipelines routinely `mkdir` a fresh workspace, `cp` needed inputs into it, and `rm -rf` it afterward to clean up (in a controlled, automated context — not something you type by hand against real data).

A representative AI-engineering project layout:

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

Realistically, over the life of such a project, you'd expect to: `mkdir` new subdirectories as the project grows (e.g. `data/processed`), `cp` a configuration file to create a variant for a new experiment, `mv` a finished model checkpoint from a temporary output folder into `models/`, and eventually `rm` old, superseded log or artifact directories to reclaim space. None of these operations are performed against the actual Applied AI Engineering project directory as part of this lesson — they are shown here only to illustrate intent.

---

## 15. Bash / Linux / WSL2 / Git Bash / PowerShell

This lesson's primary teaching environment is **Bash on Linux** (which is also what WSL2 and Git Bash provide) — all four commands (`mkdir`, `cp`, `mv`, `rm`) behave identically across Bash, WSL2, and Git Bash.

**PowerShell** (native Windows) provides the same *capabilities* through different command names:

| Bash/Linux | PowerShell equivalent | Notes |
|---|---|---|
| `mkdir dir` | `New-Item -ItemType Directory -Path dir` (or the alias `mkdir dir`, which PowerShell also supports) | PowerShell conveniently aliases `mkdir`, but its full underlying command is `New-Item` |
| `cp source dest` | `Copy-Item source dest` | `-Recurse` replaces `-r`/`-R` for directories |
| `mv source dest` | `Move-Item source dest` | Also used for renaming, same as `mv` |
| `rm file` | `Remove-Item file` | `-Recurse` replaces `-r`; there is no `-f` equivalent by that name, but `-Force` exists and is similarly dangerous |

This lesson is not a PowerShell course — this table exists only so that if you're working on native Windows, you know the underlying goal is identical even though the exact command differs. **WSL2** consideration worth knowing: it runs a real Linux filesystem, so commands behave exactly as in native Linux Bash — but be aware that WSL2's Linux filesystem and Windows' native filesystem are distinct, and moving files between them (e.g. `/mnt/c/...` paths) is exactly the "different filesystem" case discussed in Section 7 and 13, where `mv` cannot simply relabel an entry and must fall back to copy-then-delete.

---

## 16. Safety Rules for File Operations

1. **Know your current working directory** before modifying anything — run `pwd` if unsure.
2. **Understand the source and destination** of a command fully before executing it — read the command back to yourself before pressing Enter.
3. **Prefer disposable directories** (like `/tmp/...`) for practice and experimentation.
4. **Do not practice on the real project directory.** Every example and exercise in this lesson uses an isolated, disposable location.
5. **Do not delete system files.** If a path looks like it belongs to the operating system rather than something you created, stop.
6. **Do not use unnecessary `sudo`.** If a command needs elevated privileges to do something you didn't expect, that's a signal to stop and reconsider, not to force it through.
7. **Be extremely careful with recursive deletion (`rm -r`, `rm -rf`).** Re-read Section 8's warning before ever using these outside a disposable directory.
8. **Inspect broad wildcard matches before destructive operations** — run the equivalent `ls` first, as described in Section 11.
9. **Use interactive options (`-i`) when appropriate**, especially while you're still building confidence.
10. **Verify the result after important operations** — `ls` the destination (and, if relevant, confirm the source is gone or unchanged) rather than assuming success.
11. **Clean up only the disposable resources you created for the lesson** — never delete anything you didn't personally create for practice.
12. **Never assume a delete operation can be undone.** Treat every `rm` as final.

---

## 17. Safe Practical Demonstration

All commands below operate only inside a disposable directory: `/tmp/command-line-file-operations-demo`. Nothing here touches the real Applied AI Engineering project or any other user file. Output shown is **illustrative** — labeled explicitly as *Example output* — not output actually captured from a live run.

**Step 1 — create a disposable directory**

```bash
mkdir -p /tmp/command-line-file-operations-demo
cd /tmp/command-line-file-operations-demo
pwd
```
Example output:
```text
/tmp/command-line-file-operations-demo
```

**Step 2 — create nested directories**

```bash
mkdir -p workspace/data workspace/models workspace/archive
```

**Step 3 — create a harmless sample file** (using a redirection technique previewed only for this purpose — covered properly in a later lesson)

```bash
echo "sample content" > workspace/data/sample.txt
```

**Step 4 — copy a file**

```bash
cp workspace/data/sample.txt workspace/data/sample-copy.txt
ls workspace/data
```
Example output:
```text
sample-copy.txt  sample.txt
```

**Step 5 — copy a directory**

```bash
cp -r workspace/data workspace/data-backup
ls workspace
```
Example output:
```text
archive  data  data-backup  models
```

**Step 6 — move a file**

```bash
mv workspace/data/sample-copy.txt workspace/archive/
ls workspace/data workspace/archive
```
Example output:
```text
workspace/data:
sample.txt

workspace/archive:
sample-copy.txt
```

**Step 7 — rename a file**

```bash
mv workspace/data/sample.txt workspace/data/sample-original.txt
ls workspace/data
```
Example output:
```text
sample-original.txt
```

**Step 8 — move a directory**

```bash
mv workspace/data-backup workspace/archive/data-backup
ls workspace workspace/archive
```
Example output:
```text
workspace:
archive  data  models

workspace/archive:
data-backup  sample-copy.txt
```

**Step 9 — inspect the resulting structure, then safely remove the entire disposable demo**

```bash
ls -R /tmp/command-line-file-operations-demo
rm -r /tmp/command-line-file-operations-demo
```

Because the target being removed is the disposable demo directory itself — created solely for this lesson, in `/tmp`, and fully accounted for — this is the one appropriate context in this lesson to use `rm -r`. Confirm afterward it's gone:

```bash
ls /tmp/command-line-file-operations-demo
```
Example output:
```text
ls: cannot access '/tmp/command-line-file-operations-demo': No such file or directory
```

That final error is the *expected, correct* result — it confirms cleanup succeeded.

---

## 18. Common Mistakes and Debugging

**1. Source file does not exist**
- *Situation:* You try to copy a file you believe exists.
- *Symptom:* `cp: cannot stat 'reports.txt': No such file or directory`
- *Likely cause:* Typo, wrong extension, or wrong directory.
- *Investigate:* Run `pwd`, then `ls`, to see the exact filenames present.
- *Safe fix:* Correct the filename/path and retry.
- *Lesson learned:* Never assume a filename from memory — verify with `ls` first.

**2. Destination directory does not exist**
- *Situation:* `cp file.txt output/newfile.txt`, but `output/` was never created.
- *Symptom:* `cp: cannot create regular file 'output/newfile.txt': No such file or directory`
- *Likely cause:* Assumed a directory existed without creating it.
- *Investigate:* `ls` the intended parent directory.
- *Safe fix:* `mkdir -p output` first, then retry the `cp`.
- *Lesson learned:* Destination directories must exist beforehand — commands don't create them implicitly (except `mkdir -p` itself).

**3. Wrong current working directory**
- *Situation:* You run `cp data.csv backup/` expecting it to work on your project's data, but you're actually in your home directory.
- *Symptom:* Either an error, or — worse — it silently succeeds on the *wrong* `data.csv`.
- *Likely cause:* Forgot to `cd` into the project directory first.
- *Investigate:* `pwd`.
- *Safe fix:* `cd` to the correct directory, confirm with `pwd`, then retry.
- *Lesson learned:* This is exactly why Lesson 01's habit — checking `pwd` before acting — matters most for destructive/modifying commands.

**4. Relative path points somewhere unexpected**
- *Situation:* `mv ../output.log logs/`, but `..` wasn't the directory you thought.
- *Symptom:* Either an error, or a file quietly moves from an unintended location.
- *Likely cause:* Miscounted directory levels, or ran the command from a different directory than assumed.
- *Investigate:* `pwd`, then `ls ..` to see what's actually there before acting.
- *Safe fix:* Use an absolute path instead if there's any doubt.
- *Lesson learned:* When ambiguity is possible, prefer absolute paths for anything destructive.

**5. Accidentally copying into the wrong directory**
- *Situation:* `cp config.yaml ../configs`, intending `../configs/` but a directory named `configs` didn't exist at that level.
- *Symptom:* Instead of copying *into* a directory, `cp` creates a *file* literally named `configs` (since the destination didn't exist as a directory, `cp` treats it as a target filename).
- *Likely cause:* Assumed a destination directory existed without checking.
- *Investigate:* `ls ..` to confirm `configs` doesn't exist as a directory, and inspect the erroneous file that was created.
- *Safe fix:* Remove the incorrectly created file, `mkdir -p ../configs`, then redo the copy.
- *Lesson learned:* A missing trailing directory can silently change what a command means.

**6. Trying to copy a directory without recursive handling**
- *Situation:* `cp models trained-models`, where `models` is a directory.
- *Symptom:* `cp: -r not specified; omitting directory 'models'`
- *Likely cause:* Forgot `-r`.
- *Investigate:* Confirm the source is indeed a directory with `ls -l` (a leading `d` in the permissions column, per Lesson 01).
- *Safe fix:* Re-run with `cp -r models trained-models`.
- *Lesson learned:* Directories always require an explicit recursive flag with `cp` — this is a safety-by-design behavior, not a limitation to work around casually.

**7. Trying to delete a non-empty directory**
- *Situation:* `rm old-experiment`, where `old-experiment` still contains files.
- *Symptom:* `rm: cannot remove 'old-experiment': Is a directory`
- *Likely cause:* Forgot `-r`, or forgot that the directory wasn't actually empty.
- *Investigate:* `ls old-experiment` to see exactly what's inside before deciding.
- *Safe fix:* Once you've confirmed the contents are genuinely disposable, `rm -r old-experiment`.
- *Lesson learned:* This error is a deliberate checkpoint — treat it as an invitation to double-check contents, not an obstacle to bypass reflexively with `-r`.

**8. Permission denied**
- *Situation:* `rm` or `mv` on a file you don't own or lack write access to.
- *Symptom:* `rm: cannot remove 'file': Permission denied`
- *Likely cause:* Insufficient permissions (Module 0.2 concept — full permissions coverage comes later in this module).
- *Investigate:* `ls -l` on the file/directory to see ownership and permission bits.
- *Safe fix:* Do **not** reflexively reach for `sudo`. Confirm you're supposed to have access at all, and address the actual permission issue rather than forcing past it.
- *Lesson learned:* "Permission denied" is the operating system correctly protecting something — treat it as information, not an obstacle.

**9. Wildcard matches more files than expected**
- *Situation:* `rm *.log` intending to remove only old debug logs, but it also matches `important-results.log`.
- *Symptom:* Files you needed are gone, with no error at all — the command succeeded exactly as written.
- *Likely cause:* Didn't check what `*.log` actually expanded to before running a destructive command.
- *Investigate:* Too late to investigate the deletion itself (Section 8's warning) — this is why prevention (Section 11's rule) matters more than recovery here.
- *Safe fix:* Going forward, always run `ls *.log` first to see the exact match set before substituting `rm`.
- *Lesson learned:* Wildcards are expanded by the shell exactly as written — "expected" and "actual" match sets can differ, and destructive commands don't ask twice.

**10. Destination already exists**
- *Situation:* `cp report.txt archive/report.txt`, but `archive/report.txt` already exists from a previous run.
- *Symptom:* No error at all — the existing file is silently overwritten.
- *Likely cause:* `cp` overwrites by default; it does not warn unless told to.
- *Investigate:* Check timestamps/contents of the destination before running, if preserving the old version matters.
- *Safe fix:* Use `cp -i` to be prompted before overwriting, or `cp -n` to skip the copy entirely if the destination exists.
- *Lesson learned:* "The command ran successfully" is not the same as "the command did what I intended" — see Section 19.

**11. Moving across filesystem boundaries**
- *Situation:* `mv largefile.iso /mnt/external-drive/`, moving between two different physical/mounted filesystems (as discussed in Sections 7, 13, and 15's WSL2 note).
- *Symptom:* The move takes noticeably longer than expected, proportional to file size, unlike a typical near-instant rename.
- *Likely cause:* Source and destination are on different filesystems, so the OS must copy the data and then delete the original rather than simply relabeling an entry.
- *Investigate:* Recognize when source and destination are on different mounted filesystems (e.g. crossing from `/home/...` to `/mnt/...` in WSL2).
- *Safe fix:* Nothing to "fix" — this is expected behavior; just budget time/space accordingly, and ensure enough free space exists at the destination during the operation.
- *Lesson learned:* `mv`'s speed and mechanism are not guaranteed to be identical in every situation — the command's *effect* (source gone, destination exists) is guaranteed; the *mechanism* underneath can vary.

**12. Accidentally renaming instead of creating a copy**
- *Situation:* Meant to type `cp config.yaml config.backup.yaml` (to keep both), but typed `mv` instead.
- *Symptom:* No error — the command succeeds, but now only `config.backup.yaml` exists; `config.yaml` is gone.
- *Likely cause:* `cp` and `mv` take an identical argument pattern, so a slip of the fingers changes behavior without any syntax error.
- *Investigate:* `ls` to confirm which files currently exist.
- *Safe fix:* If a backup elsewhere still exists, restore from it; otherwise, recreate the file. There is no "undo."
- *Lesson learned:* `cp` and `mv` look nearly identical to type but have opposite consequences for the source — always pause before submitting either against anything you're not practicing with.

---

## 19. Common Misconceptions

- **"`mv` always copies the entire file."** — Not necessarily. Within the same filesystem, `mv` typically just relabels where the file is recorded, without rewriting its contents (Sections 7 and 13). It only behaves like copy-then-delete when crossing filesystem boundaries.
- **"`mv` and `cp` are basically the same."** — They produce opposite outcomes for the source: `cp` leaves two copies; `mv` leaves exactly one, relocated.
- **"`rm` moves files to a recycle bin."** — It does not. Command-line deletion is immediate and, by default, has no undo mechanism (Section 8).
- **"`mkdir` creates files."** — It creates directories only — empty containers, not files.
- **"A directory is just another kind of file."** — For this lesson's purposes, treat them as distinct: files hold data directly; directories organize other files and directories. (A deeper filesystem-internals view is out of scope here.)
- **"A relative path always starts from the project root."** — It starts from your shell's *current working directory*, which may or may not be your project's root — this is exactly why checking `pwd` matters (Lesson 01, and Section 18's mistake #3).
- **"`rm -r` is safe if I know the directory name."** — Knowing the name doesn't guarantee you're in the right location, or that the directory doesn't contain something you forgot about. Always confirm with `ls` first.
- **"A successful command always means I changed the thing I intended."** — A command can succeed while overwriting the wrong destination, matching an unintended wildcard set, or acting on the wrong current directory. "No error" is not the same as "correct outcome."
- **"Using `sudo` fixes every filesystem problem."** — `sudo` overrides permission checks; it does not fix a wrong path, a wrong assumption, or a genuine reason a file is protected. Reaching for it reflexively can turn a small mistake into a much larger one.
- **"Copying a directory automatically copies everything regardless of options."** — `cp` refuses to touch a directory at all without `-r`/`-R` (Section 6); it never partially or implicitly decides to go recursive on its own.

---

## 20. AI Engineering Connection

These four commands are unglamorous, but AI-engineering workflows depend on them constantly:

- **Dataset preparation**: organizing raw downloads into `data/raw/`, `data/processed/`, etc.
- **Model checkpoint management**: moving the best-performing checkpoint into a stable `models/` location.
- **Experiment directories**: creating a fresh, uniquely named directory per training run so results don't overwrite each other.
- **Training artifacts**: copying configuration files alongside outputs so each run's exact settings are preserved.
- **Evaluation results**: organizing per-run evaluation outputs into clearly separated directories.
- **Prompt/evaluation datasets**: duplicating a base evaluation set before modifying it for a new experiment.
- **RAG ingestion artifacts**: moving processed document chunks or embeddings into the directory a retrieval pipeline expects.
- **Generated reports**: relocating generated output files into a shared reports directory.
- **Logs**: archiving old logs out of an active working directory.
- **Temporary processing files**: creating and later removing disposable working directories during a pipeline run.
- **Deployment packages**: assembling exactly the right set of files into a package directory before shipping.

Realistic failure scenarios — every one of these is a *file-operation* mistake, not a modeling or algorithmic one:

- **Training reads the wrong dataset** because a file was `cp`'d into the wrong directory, and the training script silently picked up stale data sitting there from a previous run.
- **Inference loads an outdated model** because a new checkpoint was never actually `mv`'d into the location the inference code reads from.
- **Evaluation reads the wrong results directory** because an experiment directory name collided with an old one, and results were overwritten rather than kept separate.
- **A deployment package misses a required file** because a `cp` command's source path or wildcard didn't actually match everything needed.
- **Generated artifacts overwrite existing files** because `cp`'s default overwrite behavior (Section 18, mistake #10) destroyed a previous run's output with no warning.
- **Cleanup deletes required data** because an `rm -r` (or worse, `rm -rf`) was run against a path that was one directory level off from the intended disposable one.

None of these require a bug in your model code — they're all things that go wrong purely from imprecise navigation and file operations, which is exactly why this lesson exists before any AI/ML-specific material in the roadmap.

---

## 21. Trade-offs and Engineering Habits

- **Copying vs. moving** — copying is safer (the original survives) but uses more storage and can leave stale duplicates lying around; moving is tidier but leaves no fallback if you got it wrong.
- **Safety vs. speed** — `-i` and checking with `ls` first cost a few seconds; skipping them costs nothing until the one time it costs everything.
- **Interactive confirmation vs. automation** — interactive flags are appropriate while working by hand; automated scripts (CI/CD, pipelines) instead rely on *validating inputs and paths in advance*, since no human is present to answer a prompt.
- **Manual operations vs. scripts** — a one-off manual command is fine for exploration; anything repeated more than once or twice is a candidate for a script (covered later in this module), which is easier to review and re-run correctly than to retype by hand.
- **Relative vs. absolute paths** — relative paths are convenient and portable; absolute paths remove ambiguity entirely. For anything destructive or high-stakes, favor absolute paths or an explicit `pwd` check immediately beforehand.
- **Destructive commands vs. reversible workflows** — where possible, prefer workflows that keep a copy or a log of what was removed/moved, rather than relying on memory or assumption.
- **Local filesystem operations vs. later storage systems** — everything in this lesson operates on a local disk; cloud storage, object stores, and versioned data systems (encountered later in the roadmap) add their own guarantees (versioning, replication, audit trails) precisely because raw file operations, as taught here, offer none of that by default.

Production engineers favor operations that are **predictable, auditable, and repeatable** — not because manual commands are "wrong," but because a script or pipeline step that always does the same, reviewed thing is far safer at scale than a human retyping similar commands under time pressure.

---

## 22. Practical Exercises

All practical work in Levels 3–5 must be done inside a disposable directory — for example, a fresh directory under `/tmp/`, created specifically for these exercises, and removed only at the end. Do not perform any exercise against the real Applied AI Engineering project directory.

### Level 1 — Recognition

1. Which command creates a new, empty directory?
2. Which command would you use to duplicate a file while keeping the original?
3. Which command removes a file entirely?
4. Which command would you use to correct a misspelled filename?
5. In `cp source.txt destination.txt`, which part is the source and which is the destination?
6. Which of the four commands in this lesson has no "destination" argument at all?
7. Which flag is required to copy a directory with `cp`?
8. Between `rm file.txt` and `rm -r folder/`, which one requires a recursive flag, and why?

### Level 2 — Understanding

1. Predict what happens if the destination file in a `cp` command already exists.
2. Explain, in your own words, why `mv` can be used both to relocate a file and to rename it.
3. If your current working directory is `/home/learner/project`, what does `cp notes.txt ../notes-backup.txt` actually do?
4. Why does `rm project/` fail with an "Is a directory" error, and what fixes it?
5. Why is `mv` usually much faster than `cp` for a large file, when both are moving/copying within the same disk?
6. What does it mean for an operation to be "recursive," using a directory tree as your example?
7. Why does `cp` require `-r` for directories, but `mv` does not?
8. If `*.csv` matches three files you expected and one you didn't, what should you do before running `rm *.csv`?

### Level 3 — Application

Perform each of these inside a disposable directory you create for this purpose (e.g. `/tmp/lesson02-practice`).

1. Create a directory called `sandbox`, and inside it, create three subdirectories: `data`, `models`, `configs`.
2. Inside `sandbox/data`, create a plain text file (using any harmless method available to you) and copy it to a new filename in the same directory.
3. Copy that entire `data` directory (with `-r`) into a new directory called `data-backup` at the same level.
4. Move one file from `sandbox/data` into `sandbox/archive` (creating `archive` first if it doesn't exist).
5. Rename a file inside `sandbox/configs` to a clearer name using `mv`.
6. Move the entire `sandbox/data-backup` directory into `sandbox/archive`.
7. Use `ls -R` (or repeated `ls`) to confirm the final structure matches what you expect.
8. Safely remove the entire disposable directory you created for this exercise, and confirm with `ls` that it's gone.

### Level 4 — Debugging

For each broken scenario, state the likely cause and the safe fix — do not just guess a command; explain your reasoning.

1. `cp draft.txt draft-backup.txt` returns `cp: cannot stat 'draft.txt': No such file or directory`. What would you check first?
2. `mv results/ ../archive/results/` fails because `../archive/` doesn't exist yet. What's the safe fix?
3. You run `rm notes.txt` from what you thought was your project directory, but it turns out to have deleted a *different* `notes.txt`. What should you have checked beforehand?
4. `cp -r project newproject` appears to succeed, but `newproject` is missing several files you expected. What would you inspect to figure out why?
5. `rm old-run` fails with "Is a directory." What are your two possible next steps, and how do you decide between them safely?
6. After `cp config.yaml configs/`, you discover `configs/config.yaml` was silently overwritten and you needed the old version. What option, used beforehand, would have prevented this?
7. `rm *.tmp` deleted a file you didn't expect. What single command, run *before* the `rm`, would have caught this in advance?
8. `mv bigfile.bin /mnt/otherdrive/` takes far longer than a typical rename. Is this a bug? Explain why, referencing filesystem boundaries.

### Level 5 — Integration

These combine navigation (Lesson 01) with this lesson's commands, resembling small real workflows. Perform all of them inside a disposable workspace directory.

1. Starting from your home directory, navigate into a new disposable workspace, create a small project-like structure (`src`, `data`, `configs`), and confirm the structure with `ls` and `pwd` at each step.
2. Simulate "starting a new experiment": create a new directory named after a fake experiment (e.g. `run-001`), copy a configuration file into it, and move a (harmless, sample) result file into it once "finished."
3. Simulate a mistaken file operation and its recovery *where recovery is actually possible*: intentionally copy a file to the wrong destination, notice the mistake using `ls`, and correct it with an additional `mv` — without ever using `rm` in this exercise (to reinforce that not every mistake needs deletion to fix).
4. Build a small nested directory tree at least three levels deep using a single `mkdir -p` command, then verify every level exists using `cd` and `pwd` at the deepest level.
5. Perform a full cleanup: given a disposable workspace with several nested subdirectories and files (from any earlier exercise), safely remove the entire workspace in one command, and verify afterward that it no longer exists.

---

## 23. Mini-Project — Command-Line File Workspace Manager

**Goal:** demonstrate correct, safe file-operation reasoning — not to build anything AI-related yet. Use a disposable workspace only; do not touch the real Applied AI Engineering project.

**Setup:**

```bash
mkdir -p /tmp/workspace-manager-project
cd /tmp/workspace-manager-project
```

**Tasks:**

1. Create a workspace directory structure resembling a simplified AI/software project:
   ```text
   workspace/
   ├── data/
   ├── models/
   ├── configs/
   ├── artifacts/
   └── archive/
   ```
2. Create at least two harmless sample files inside `workspace/data/` (any simple text content).
3. Copy one of those sample files into `workspace/configs/`, giving it a name that reflects it as a "template."
4. Move the other sample file from `workspace/data/` into `workspace/artifacts/`.
5. Rename the copied file inside `workspace/configs/` to a more accurate final name.
6. Copy the entire `workspace/artifacts/` directory into `workspace/archive/` (recursively), simulating an "archive of this run's artifacts."
7. Decide that `workspace/models/` (still empty) is unnecessary for this particular exercise, and safely remove just that one empty directory — noting that an empty directory can be removed with plain `rm -r` (or even without `-r` on some systems, since there's nothing to recurse into) with minimal risk, precisely *because* it's empty.
8. Verify the final structure with `ls -R workspace` (or repeated `ls`), and confirm it matches your expectations.
9. Clean up entirely by removing `/tmp/workspace-manager-project` once you're satisfied, and confirm with `ls` that it's gone.

**Success criteria:** at every step, you can explain — before running the command — exactly what source, destination, and (if applicable) recursion is involved, and you can confirm the actual result matches your prediction using `ls`/`pwd` rather than assuming.

---

## 24. Review

Key terms from this lesson:

- **File** — a named unit of stored data.
- **Directory** — a container for files and other directories.
- **Source** — what a file operation reads from or acts on.
- **Destination** — where a file operation's result ends up.
- **`mkdir`** — creates a new directory (`-p` creates missing parent directories too).
- **`cp`** — duplicates a file or directory (`-r`/`-R` required for directories); original remains.
- **`mv`** — relocates and/or renames a file or directory; original location no longer holds it.
- **`rm`** — deletes a file or directory (`-r`/`-R` required for directories); no built-in undo.
- **Recursive operation** — repeating an operation on every item inside a directory, and inside its subdirectories, at any depth.
- **Absolute path** — a full path starting from the filesystem root; unambiguous regardless of current location.
- **Relative path** — a path interpreted from the current working directory; convenient but context-dependent.
- **Safety** — checking `pwd`/`ls` before acting, using `-i`, favoring absolute paths for destructive commands, and never assuming a deletion can be undone.

Compact command reference:

| Command | Minimal form | Directory form | Key safety option |
|---|---|---|---|
| `mkdir` | `mkdir name` | `mkdir -p a/b/c` (creates missing parents) | — |
| `cp` | `cp src dest` | `cp -r src dest` | `-i` (confirm overwrite), `-n` (never overwrite) |
| `mv` | `mv src dest` | `mv src dest` (no `-r` needed) | `-i` (confirm overwrite) |
| `rm` | `rm file` | `rm -r dir` | `-i` (confirm each deletion) |

---

## 25. Interview / Architecture Questions

1. What is the fundamental difference between `cp` and `mv`, in terms of what happens to the source?
2. Why can `mv` be used for renaming a file, when there's no dedicated "rename" command?
3. Explain what "recursive" means in the context of `cp -r` and `rm -r`, using a concrete directory example.
4. Why is `rm` considered one of the riskiest commands a beginner can run, and what specific habit reduces that risk the most?
5. A teammate says relative paths "always work the same no matter where you run them from." Why is this incorrect, and what real production bug could result from believing it?
6. What happens, at a high level, when `mv` moves a file across two different filesystems, compared to moving it within the same filesystem?
7. Why do backend services and deployment pipelines care about the same source/destination/path concepts introduced in this lesson, even though they rarely involve a human typing `cp` by hand?
8. Describe a realistic way an incorrect file operation could cause an ML training run to silently use the wrong dataset, without the training code itself containing any bug.
9. Describe a realistic way a file-operation mistake could cause a production AI deployment to serve an outdated model.
10. Why might a production system prefer a controlled, scripted, auditable set of file operations over allowing ad hoc manual commands against the same data?

---

## 26. Production Application

In production environments, the same four operations underpin much larger, more automated systems:

- **Build artifact management** — build systems `cp`/`mv` compiled outputs into versioned release locations.
- **Dataset staging** — data pipelines create (`mkdir`) staging directories, copy raw inputs in, and move validated outputs onward.
- **Model artifact movement** — a newly trained model is moved into a "current production model" location only after passing validation, precisely to avoid the "inference loads an outdated model" failure from Section 20.
- **Temporary workspaces** — batch jobs and CI/CD runners routinely create a fresh workspace directory, populate it, and remove it entirely afterward.
- **Batch-processing directories** — large-scale data processing often moves files between "pending," "processing," and "completed" directories as a simple, effective coordination mechanism.
- **Log/artifact organization** — production logging systems relocate or archive logs on a schedule, rather than letting them accumulate indefinitely.
- **Deployment packaging** — deployment tooling assembles an exact set of files (via `cp`) into a package before shipping it.
- **CI/CD workspaces** — pipeline runs typically create an isolated workspace per run and clean it up (`rm -r`) automatically afterward.

The key difference from what you practiced in this lesson: production systems generally wrap these same raw operations with stronger controls, including **validation** (confirming a path exists and is what's expected before acting), **permissions** (restricting who/what can modify which locations), **atomicity/reliability considerations** (ensuring an operation either fully completes or is safely retryable, rather than leaving things half-done), **logging** (recording exactly what was created, moved, or deleted, and when), and **monitoring** (detecting when an expected file-operation step failed). None of these production-grade controls are built into `mkdir`, `cp`, `mv`, or `rm` themselves — they are added around them by the systems that use them, and are topics for later stages of this roadmap, not this lesson.

---

## 27. Relationship to Module 0.2

This lesson's four commands are concrete, hands-on expressions of concepts you already learned conceptually in Module 0.2:

- **Filesystem** — every operation in this lesson changes the filesystem's record of what exists and where.
- **Permissions** — determine whether a given `cp`, `mv`, or `rm` is even allowed to proceed (Section 18's "Permission denied" scenario); full permissions administration is covered later in this module.
- **Processes** — `mkdir`, `cp`, `mv`, and `rm` are each, themselves, a short-lived process when you run them.
- **Shell** — parses your command, expands wildcards, and resolves relative paths before the actual program runs.
- **System calls** — the mechanism by which these commands actually ask the operating system to change the filesystem on their behalf.

The layering to keep in mind going forward:

```text
User → terminal → shell → command → process → operating system → filesystem/storage
```

This lesson does not re-teach any of Module 0.2's material in depth — it only shows these familiar concepts *in action*, through commands you can now actually run.

---

## 28. Scope Boundary

This lesson deliberately does **not** teach, in depth:

- `cat`, `less`, `head`, `tail` (viewing files — next lesson)
- `grep`, `find` (searching — later lessons)
- `sort`, `uniq`, `cut` (text processing — later lessons)
- `xargs`, pipes, redirection (later lessons — though a single redirection example was used minimally in Section 17 purely to create a sample file, without explanation of how it works)
- environment variables (later lesson)
- shell scripting (later lesson)
- permissions administration in depth (later lesson — this lesson only references permissions conceptually, as inherited from Module 0.2)
- advanced filesystem internals (inodes, journaling, VFS, ext4 internals, overlay filesystems, distributed filesystems)
- Docker, Kubernetes, cloud storage, or CI/CD implementation details

These are separate roadmap topics and stages, mentioned here only where necessary for context (for example, in the real-world and production sections). This lesson is not a preview course for any of them.

---

_This lesson is complete. It covers `mkdir`, `cp`, `mv`, and `rm` only. The remaining Module 0.3 topics are covered in subsequent lessons within this module._
