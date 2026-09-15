# Module 0.3 — Command Line

## Lesson 01 — Navigation

**Module:** Command Line
**Roadmap reference:** Stage 0 — Module 0.3 — Command Line
**Concept(s) covered:** `pwd`, `ls`, `cd`
**Status:** Complete
**Builds on:** Module 0.2 — Operating System Fundamentals (processes, filesystems, permissions, shell, environment variables)

---

### Learning Objectives

By the end of this lesson you will be able to:

- Explain, in your own words, what a terminal, a shell, and a command are — and how they differ.
- Explain what the "current working directory" is and why every process has one.
- Read and write both absolute and relative paths correctly.
- Use `pwd` to find out where you are in the filesystem.
- Use `ls` to inspect the contents of a directory, including hidden files and detailed listings.
- Use `cd` to move around the filesystem safely and predictably.
- Predict what a navigation command will do *before* running it.
- Diagnose and fix common navigation errors (`No such file or directory`, `Permission denied`, landing in the wrong place).
- Explain why filesystem navigation matters for software engineering and AI engineering work (projects, datasets, models, virtual environments, scripts).

---

### 1. What Is the Command Line?

The **command line** is a text-based way of talking to your computer. Instead of clicking icons, you type instructions, the computer runs them, and it prints the result back as text.

You already learned in Module 0.2 that an operating system manages processes, files, and permissions. The command line is simply a *direct, typed interface* to those same OS facilities — no mouse, no windows, just text in and text out.

Why this matters for you as a future AI engineer: almost everything in professional software and AI work — training scripts, servers, cloud machines, Docker containers, remote GPU boxes — is operated through a command line. There is often no icon to click. Comfort with the command line is not optional; it is the baseline skill layer everything else in this roadmap sits on top of.

### 2. Why Command-Line Navigation Exists

Every file and program on your computer lives somewhere in the **filesystem** — the tree of directories (folders) and files you learned about in Module 0.2. To *do* anything (open a file, run a script, install a package, train a model), a command needs to know **where** to look.

"Navigation" is simply the set of commands that let you:

1. Ask "where am I right now?" (`pwd`)
2. Ask "what is here?" (`ls`)
3. Move "there" (`cd`)

These three commands exist because the shell — like every running program — always operates from *some* location in the filesystem, and you need a reliable way to see and control that location. Without navigation, every command would require you to type the full, exact location of every file, every time, with zero ability to check your surroundings first.

### 3. Terminal vs Shell vs Command

Complete beginners often use these words interchangeably. They are not the same thing. Precisely separating them now will save you confusion for the rest of this roadmap.

| Term | What it actually is | Analogy |
|---|---|---|
| **Terminal** | An application (a window) that displays text input/output. It is just a screen and a keyboard — it has no intelligence of its own. | The phone handset |
| **Shell** | A *program* that runs inside the terminal, reads what you type, interprets it, and asks the operating system to act on it. Bash, Git Bash, and PowerShell are all shells. | The person you're talking to on the phone |
| **Command** | A single instruction you give the shell — e.g. `pwd`, `ls`, `cd projects` — which the shell parses and executes. | A sentence you speak into the phone |
| **Filesystem** | The tree structure of directories and files stored on disk (Module 0.2). Navigation commands operate *on* this structure. | The city the person you're talking to can walk around in |
| **Current working directory** | The one specific location in the filesystem that the shell (as a running process) is "standing in" right now. | The exact address the person is currently standing at in that city |

Concretely:

- You open a **terminal** window.
- Inside it, a **shell** (e.g. `bash`) starts running.
- You type a **command** like `ls`.
- The shell looks at the **filesystem**, starting from its **current working directory**, and prints the result back into the terminal window.

The terminal never changes location, never interprets commands, and never touches files — it only displays what the shell sends it. All the real work happens in the shell.

### 4. Current Working Directory

In Module 0.2 you learned that a **process** is a running instance of a program, and that the operating system tracks state for each process (memory, open files, permissions it runs under, etc.).

One piece of state every process has is its **current working directory (CWD)** — the single filesystem location it is "based in" at any given moment.

Key facts:

- The shell itself is a process. It has a CWD, just like any other process.
- When you run a command that refers to a file *without* a full path (e.g. `cat notes.txt`), the shell resolves `notes.txt` **relative to its CWD** — it does not search the entire filesystem.
- When the shell starts a new program (say, `python train.py`), that child process usually **inherits** the shell's current CWD as its own starting CWD. This is why "where you run a script from" can change how the script behaves — a script that opens `data/input.csv` will look for `data/` relative to wherever the process's CWD is.
- Changing directory with `cd` does not move any files. It only updates the shell process's internal "I am currently here" pointer.

This is the single most important mental model for this lesson: **navigation commands don't touch your files — they only change or reveal where the shell process is currently "standing."**

### 5. Paths

A **path** is a text description of a location in the filesystem tree.

Vocabulary, building directly on the filesystem tree from Module 0.2:

- **Directory** — a folder; a node in the tree that can contain other directories and files.
- **Root directory** — the top of the entire tree, written `/` on Linux/macOS/WSL2/Git Bash. Everything else is nested under it.
- **Parent directory** — the directory one level *above* a given directory (its container).
- **Child directory** — a directory nested *inside* a given directory.
- **Home directory** — the directory assigned to your user account for personal files, written `~` as a shortcut (e.g. `/home/learner`).
- **`.`** — shorthand for "the current directory itself."
- **`..`** — shorthand for "the parent of the current directory."

Example filesystem:

```text
/
├── home/
│   └── learner/
│       ├── projects/
│       │   └── ai-project/
│       └── documents/
└── tmp/
```

If you are currently standing in `ai-project/`:

- `.` means `ai-project/`
- `..` means `projects/`
- `../..` means `learner/`
- `~` always means `/home/learner`, no matter where you currently are

#### Absolute paths

An **absolute path** starts from the root (`/`) and spells out the *entire* location, unambiguously, regardless of where you currently are.

```text
/home/learner/projects/ai-project
```

- Always starts with `/` (or, on native Windows PowerShell, a drive letter like `C:\`).
- Always points to the same place, no matter what your current directory is.
- Slightly longer to type, but never ambiguous.

#### Relative paths

A **relative path** is interpreted *relative to your current working directory*. It does not start with `/`.

If your CWD is `/home/learner`, then:

```text
projects/ai-project
```

...means the same thing as the absolute path above. But if your CWD were `/tmp`, that same relative path `projects/ai-project` would mean something completely different (and probably not exist).

This is the trade-off: relative paths are shorter and convenient, but their meaning **changes depending on where you are** — which is exactly why `pwd` (knowing where you are) matters so much before using relative paths.

### 6. `pwd` — Print Working Directory

`pwd` asks the shell: "What is your current working directory, right now?"

```bash
$ pwd
/home/learner/projects/ai-project
```

- It takes no arguments in normal use.
- It always returns an **absolute path**.
- It never changes anything — it is a pure "read" operation, safe to run at any time.

Mental model: `pwd` is you asking the shell process "where are you standing?" and it reads that value straight out of its own process state (the same CWD concept from Section 4).

### 7. `ls` — List Directory Contents

`ls` asks the shell: "What files and directories exist in [some location]?"

```bash
$ ls
documents  projects

$ ls projects
ai-project

$ ls /home/learner
documents  projects
```

- With no arguments, `ls` lists the **current working directory**.
- With an argument (a path — absolute or relative), it lists *that* location instead, without moving you there.
- `ls` is also a read-only operation — it never changes your CWD or your files.

Useful flags for a beginner to know now (you will use these constantly):

| Flag | Meaning | Example |
|---|---|---|
| `-l` | "Long" format: shows permissions, owner, size, and modified date (connects directly to the permissions concept from Module 0.2) | `ls -l` |
| `-a` | "All": shows hidden files/directories too (anything starting with `.`, like `.gitignore` or `.env`) | `ls -a` |
| `-la` (or `-al`) | Combine both: long format, including hidden entries | `ls -la` |
| `-h` | "Human-readable" sizes (e.g. `2.1M` instead of `2201233`) — usually paired with `-l` | `ls -lh` |

Example combined output:

```bash
$ ls -la
drwxr-xr-x  4 learner learner 4096 Sep  8 19:10 .
drwxr-xr-x  6 learner learner 4096 Sep  8 19:10 ..
-rw-r--r--  1 learner learner  220 Sep  8 19:10 .gitignore
drwxr-xr-x  2 learner learner 4096 Sep  8 19:10 data
-rw-r--r--  1 learner learner 1830 Sep  8 19:10 train.py
```

Notice `.` (current directory) and `..` (parent directory) appear as entries themselves — this is the filesystem making the concepts from Section 5 directly visible. The leading `d` or `-` and the `rwx` permission triplets are exactly the permission bits you studied in Module 0.2 — `ls -l` is one of the main tools you'll use to *inspect* those permissions in practice.

### 8. `cd` — Change Directory

`cd` tells the shell: "Update your current working directory to this new location."

```bash
$ pwd
/home/learner

$ cd projects
$ pwd
/home/learner/projects
```

Common forms:

| Command | Effect |
|---|---|
| `cd projects` | Move into `projects`, relative to current CWD |
| `cd /home/learner/projects` | Move to that exact absolute location, regardless of current CWD |
| `cd ..` | Move up one level to the parent directory |
| `cd ../..` | Move up two levels |
| `cd ~` or `cd` (no argument) | Jump straight to your home directory |
| `cd -` | Jump back to the *previous* directory you were in before your last `cd` |
| `cd .` | "Move" to the current directory — effectively a no-op, but useful to understand `.` |

Mental model: `cd` is the only one of the three core commands that **changes process state**. `pwd` and `ls` only *read* and report; `cd` *writes* a new value into the shell's CWD. This is why `cd` is the command most likely to "surprise" a beginner — always confirm with `pwd` (or check your terminal prompt, which usually shows the CWD) after a `cd` if you're unsure.

### 9. How the Shell Resolves a Path (Internal Mechanics)

When you type a command involving a path, the shell performs a predictable sequence of steps:

1. **Is the path absolute?** (Does it start with `/`?) If yes, the shell starts resolution from the root `/` and follows each segment exactly as written — the current CWD is irrelevant.
2. **Is the path relative?** If it doesn't start with `/`, the shell takes its own current working directory and appends the path segments onto it, one at a time.
3. **Special segments are resolved as it goes:** `.` resolves to "stay here," `..` resolves to "step up to the parent," and `~` is expanded by the shell *before* resolution even begins, into your home directory's absolute path.
4. **Each segment is checked against the filesystem:** the shell (via the operating system, per Module 0.2's system-call concept) asks the filesystem "does a directory with this name exist inside the current segment?" If any segment along the way doesn't exist, or exists but isn't a directory, or you lack permission to enter it, resolution fails and you get an error — it does not silently guess or search elsewhere.
5. **Once fully resolved, the OS returns a definitive filesystem location**, which `cd` then stores as the shell process's new CWD (or which `ls`/other commands read from directly, without changing the CWD).

This is why a single typo, an extra `/`, or being one directory off produces an immediate, exact error rather than "close enough" behavior — path resolution is mechanical and literal, not fuzzy.

### 10. Real-World Use Cases

- **Running a training script**: `cd` into your project folder before running `python train.py`, so that relative paths inside the script (like `data/train.csv` or `outputs/model.pt`) resolve correctly.
- **Activating a virtual environment** (you'll meet this properly in Module 0.4): the activation command is usually run as a relative path from inside the project directory.
- **Inspecting a dataset directory** before writing code: `cd` into it and run `ls -lh` to see file sizes before you load anything into memory.
- **Working across cloud/remote machines**: SSH-ing into a GPU server drops you into some starting directory; the very first thing engineers do is `pwd` and `ls` to orient themselves before touching anything.
- **Avoiding destructive mistakes**: many dangerous commands (deleting files, overwriting checkpoints) are actually navigation mistakes in disguise — running the right command in the *wrong directory*.

### 11. Trade-offs

| Choice | Benefit | Cost |
|---|---|---|
| Absolute paths | Unambiguous, safe in scripts, work regardless of CWD | Longer to type/read; less portable if the project moves to a different location on disk |
| Relative paths | Short, portable (a whole project folder can be moved/renamed and relative paths inside it still work) | Meaning depends entirely on CWD — a script run from the wrong directory silently fails or, worse, touches the wrong files |
| Frequent `cd` between locations | Convenient, less typing per command | Increases the chance you forget where you are and run a command "in the wrong place" |
| Always confirming with `pwd`/`ls` before acting | Prevents mistakes, builds accurate mental model | Costs a few extra keystrokes each time |

The professional habit this lesson is building toward: **default to checking (`pwd`, `ls`) before acting, especially before any command that changes or deletes something** — that habit is introduced properly in the next lessons (`cp`, `mv`, `rm`), and it depends entirely on the navigation fluency built here.

### 12. Small Examples

```bash
# Where am I?
$ pwd
/home/learner

# What's here?
$ ls
projects  documents

# Go into projects
$ cd projects
$ pwd
/home/learner/projects

# What's in here?
$ ls
ai-project

# Go into the project, using a relative path
$ cd ai-project
$ pwd
/home/learner/projects/ai-project

# Go back up one level
$ cd ..
$ pwd
/home/learner/projects

# Jump straight home from anywhere
$ cd ~
$ pwd
/home/learner

# Jump to an absolute path directly, in one step
$ cd /home/learner/projects/ai-project
$ pwd
/home/learner/projects/ai-project

# Jump back to the previous directory
$ cd -
$ pwd
/home/learner
```

### 13. Practical Exercises

Work through these in an actual terminal (Bash, Git Bash, or WSL2 — all behave the same way for these commands).

1. Open your terminal and run `pwd`. Write down the exact output.
2. Run `ls -la` in that same location. Identify: one regular file, one directory, the `.` entry, and the `..` entry.
3. Predict, on paper, what `cd ..` will do *before* running it. Run it, then confirm with `pwd`.
4. From your home directory, `cd` into any two levels of nested directories in a single command, using a relative path (e.g. `cd projects/ai-project`).
5. From wherever you ended up in step 4, return home in exactly one command, two different ways (find both).
6. Use `cd` with an absolute path to jump directly to some directory, then use `cd -` to jump back. Confirm both locations with `pwd`.
7. Run `ls` on a directory *without* moving into it (pass it as an argument to `ls`), then run `pwd` and confirm your CWD never changed.

### 14. Debugging Exercises — Common Mistakes

For each scenario, identify the likely cause before reading the explanation.

**Scenario A**
```bash
$ cd projects
-bash: cd: projects: No such file or directory
```
*Likely cause:* There is no directory named `projects` inside your current working directory. Run `pwd` then `ls` to confirm what actually exists here — you may be one level off, or there may be a typo/case mismatch (`Projects` vs `projects` — filesystems on Linux/WSL2 are case-sensitive).

**Scenario B**
```bash
$ cd /home/learner/projects
-bash: cd: /home/learner/projects: Permission denied
```
*Likely cause:* The directory exists, but your user lacks the execute permission bit on it (recall from Module 0.2: the execute permission on a *directory* controls whether you're allowed to enter it, not whether you can "run" it). Check with `ls -l` on the parent directory.

**Scenario C**
```bash
$ python train.py
FileNotFoundError: [Errno 2] No such file or directory: 'data/train.csv'
```
*Likely cause:* This is not a Python bug — it's a navigation mistake. The script expects `data/train.csv` *relative to the CWD the script was launched from*. Run `pwd` before running the script; if you're not inside the project's root directory, `cd` there first.

**Scenario D**
```bash
$ cd ..
$ ls
# (unexpected files — not what you expected at all)
```
*Likely cause:* You lost track of your CWD before running `cd ..`. Always run `pwd` when uncertain — never assume your location from memory, especially after several `cd` commands in a row.

**Scenario E**
```bash
$ cd Projects
-bash: cd: Projects: No such file or directory
```
*Likely cause:* Case mismatch. The real directory is `projects` (lowercase). Filesystem navigation on Linux/macOS/WSL2 is case-sensitive, unlike native Windows.

**General diagnostic procedure whenever navigation misbehaves:**

1. Run `pwd` — confirm where you actually are.
2. Run `ls -la` — confirm what actually exists here, including hidden entries.
3. Re-read the exact path you typed, character by character, checking case and spelling.
4. Decide: should this be an absolute path instead of a relative one, to remove ambiguity?

### 15. Mini-Project: Filesystem Scavenger Hunt

Without creating, deleting, or modifying any files (this lesson is read-only navigation — `mkdir`, `cp`, `mv`, `rm` are covered in later lessons):

1. Starting from your home directory, use only `pwd`, `ls`, and `cd` to explore your filesystem and answer:
   - What is the absolute path of your home directory?
   - Name three directories that exist directly inside your home directory.
   - Pick one of them, move into it, and list what's inside using `ls -la`. Are there any hidden files?
   - What is the absolute path of the root directory's immediate children? (`ls /`)
   - From deep inside a nested directory, return to your home directory using `cd ~`, then confirm with `pwd`.
2. Write down, in your own words (a few sentences), the exact sequence of commands you used and why each one was necessary — as if explaining it to someone who has never used a terminal.
3. Deliberately trigger a `No such file or directory` error on purpose (try to `cd` into something that doesn't exist), read the error message carefully, and explain in one sentence exactly why it happened.

### 16. Review Questions

1. What is the difference between a terminal, a shell, and a command?
2. What does "current working directory" mean, and which Module 0.2 concept (process state) does it connect to?
3. Why do commands like `cat somefile.txt` sometimes fail depending on where you run them from?
4. What is the difference between an absolute path and a relative path? Give one example of each.
5. What do `.` and `..` mean, and where do you see them appear directly in `ls -la` output?
6. Does `ls` ever change your current working directory? Does `cd`? Explain the difference.
7. If you're unsure where you are, which single command should you run first?
8. Why is `cd Projects` different from `cd projects` on Linux/WSL2, but might not matter on native Windows?
9. What does `cd -` do?
10. Walk through, step by step, how the shell resolves the path `../data/train.csv` starting from `/home/learner/projects/ai-project`.

### 17. Interview / Architecture Questions

1. *"Explain what happens, at the process level, when you run `cd` in a shell."* — Expected answer: `cd` is a shell builtin (not a separate external program) that updates the calling shell process's own current-working-directory state; it must be a builtin because a separate child process cannot change its parent shell's CWD.
2. *"Why can a script that works fine on your machine fail with `FileNotFoundError` when run from a CI/CD pipeline or a colleague's machine?"* — Expected answer: the script likely uses relative paths, and the working directory it's launched from differs between environments; the fix is either to always `cd` to a known location before running it, or to have the script compute paths relative to its own file location rather than the CWD.
3. *"What's the practical difference between an absolute and a relative path when writing a deployment or automation script?"* — Expected answer: absolute paths are unambiguous but tie the script to one specific machine's directory layout; relative paths are portable across machines/environments but only work correctly if the script's CWD assumption always holds — production automation typically avoids relying on CWD entirely.
4. *"How would you debug a 'file not found' error in a production script without direct interactive access to the machine?"* — Expected answer: have the script (or the logs) explicitly print its working directory (`pwd`-equivalent) and the resolved absolute path it attempted to open, so the failure is diagnosable from logs alone rather than by guessing.

### 18. Production / AI Engineering Relevance

Every project in the remainder of this roadmap depends on reliable navigation:

- **Dataset paths**: AI/ML training and RAG pipelines constantly reference relative paths like `data/raw/`, `data/processed/`, or `checkpoints/`. If the working directory assumption is wrong, the pipeline either crashes immediately (`FileNotFoundError`) or — worse — silently reads or writes the wrong data.
- **Virtual environments and dependency isolation** (Module 0.4): activating the correct environment is a navigation-dependent step; running the wrong `python` or `pip` because you're in the wrong directory is a routine source of "it works on my machine" bugs.
- **Version control**: Git operates relative to the repository root, and knowing exactly where you are before running `git` commands (covered in a later module) prevents committing or discarding the wrong files.
- **Remote and cloud environments**: SSH sessions onto training servers, Docker containers, and CI/CD runners all start you in some directory that is not automatically "your project." Professionals reflexively run `pwd` and `ls` immediately upon connecting, before running anything else.
- **Automation and reproducibility**: production scripts and infrastructure-as-code are written to be independent of *who* runs them and *from where* — which is only possible once you deeply understand how CWD and path resolution work, which is exactly what this lesson built.

The commands themselves (`pwd`, `ls`, `cd`) are trivial to memorize. The capability this lesson actually built is the underlying mental model — current working directory as process state, and path resolution as a mechanical, literal process — which is what lets you *predict* and *debug* behavior across every tool you'll use for the rest of this roadmap.

---

_This lesson is complete. It covers `pwd`, `ls`, and `cd` only. The remaining Module 0.3 topics (`cp`, `mv`, `rm`, `mkdir`, `cat`, `less`, `head`, `tail`, `grep`, `find`, `sort`, `uniq`, `cut`, `xargs`, pipes, redirection, environment variables, shell scripts, permissions) are covered in subsequent lessons within this module._
