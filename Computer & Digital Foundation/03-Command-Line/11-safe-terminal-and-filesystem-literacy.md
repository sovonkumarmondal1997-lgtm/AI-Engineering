# Module 0.3 — Command Line

## Lesson 11 — Safe Terminal and Filesystem Literacy

**Module:** Command Line
**Roadmap reference:** Stage 0 — Computer, Linux, and Developer Foundations, Gap 0B — "Safe
terminal habits and filesystem literacy" (extends Module 0.3 — Command Line)
**Concept(s) covered:** absolute vs. relative paths, confirming the current directory, Windows vs.
Linux/WSL path differences, files/folders/extensions, hidden files, UTF-8 text, line endings,
permissions and ownership, a safe introduction to `chmod`, symbolic links, safe deletion
principles, `pwd`, `ls`, `cd`, `mkdir`, `cp`, `mv`, `cat`, `less`, `find`
**Status:** Not Started
**Builds on:** 01-navigation.md, 02-file-operations.md, 03-viewing-files.md, 04-searching.md, and
Module 0.2 (filesystems, permissions)

---

### Learning Outcomes

By the end of this lesson you will be able to:

- State your current directory with certainty before running any command that creates, moves, or
  removes files.
- Explain the difference between an absolute path and a relative path, and choose the right one
  deliberately.
- Explain why a path that works on Windows can fail on Linux/WSL, and vice versa.
- Explain what a file extension, a hidden file, UTF-8 text, and a line ending are, and why each one
  occasionally causes confusing errors.
- Read a permission string, explain read/write/execute for a file and a directory, and use `chmod`
  safely on a file you created yourself.
- Recognize a symbolic link before moving or deleting it, and explain why that recognition matters.
- Apply a small set of safe-deletion habits that prevent the most common "I deleted the wrong
  thing" mistakes.
- Explain why filesystem literacy specifically matters for reading logs, working in a codebase, and
  handling model files and configuration reliably.

### Prerequisites

- **01-navigation.md** — `pwd`, `ls`, `cd`, and the idea of a current working directory.
- **02-file-operations.md** — `cp`, `mv`, `rm`, `mkdir`.
- **03-viewing-files.md** — `cat`, `less`, `head`, `tail`.
- **04-searching.md** — `grep`, `find`.
- **Module 0.2** — [Filesystems](../02-Operating-System-Fundamentals/07-filesystems.md) and
  [Permissions](../02-Operating-System-Fundamentals/08-permissions.md), for the conceptual
  background this lesson turns into everyday habits.

### Key Terms

- **Absolute path** — a path written from the filesystem's root, unambiguous regardless of your
  current directory (e.g. `/home/you/project/notes.md`).
- **Relative path** — a path written relative to your current directory (e.g. `notes.md` or
  `../data/notes.md`); its meaning changes depending on where you are.
- **Current working directory (CWD)** — the directory a running process (including your shell)
  currently considers "here"; every relative path is resolved against it.
- **File extension** — the part of a filename after the last dot (e.g. `.md`, `.py`); a convention,
  not something the operating system enforces.
- **Hidden file** — on Linux/WSL, any file or folder whose name starts with a dot (e.g. `.gitignore`,
  `.env`); hidden from a plain `ls`, not from the system itself.
- **UTF-8** — the character-encoding standard almost all modern text files use, capable of
  representing virtually any character from any language.
- **Line ending** — the invisible character(s) marking the end of a line in a text file; Linux uses
  `\n` (LF), Windows uses `\r\n` (CRLF).
- **Permission** — a rule describing who may read, write, or execute a file or directory (full
  treatment in Module 0.2's [Permissions](../02-Operating-System-Fundamentals/08-permissions.md)).
- **Ownership** — the specific user (and group) a file belongs to, which determines whose
  permission bits apply.
- **Symbolic link (symlink)** — a special file that points to another file or directory by path,
  rather than containing data itself.
- **Recursive command** — a command that applies itself to a directory and everything inside it;
  powerful, and correspondingly risky if the target is wrong.

---

### 1. Why Filesystem Literacy Matters Before Anything Else

Every command in this module — copying a file, searching logs, running a script — operates on
*some* location in the filesystem. If you are not certain which location that is, every one of
those commands becomes a guess instead of a deliberate action. This lesson is not about new
commands so much as a new habit: **know where you are, and know exactly what you're about to
affect, before you affect it.**

This matters more, not less, as your work gets more capable. A typo in a `cp` command copies the
wrong file; a typo in a careless recursive `rm` can delete work that took hours to produce. The
tools themselves don't distinguish between "an intentional cleanup" and "a costly mistake" — only
your own habits do.

### 2. Absolute vs. Relative Paths, and Confirming Your Current Directory

You met both path types briefly in `01-navigation.md`. Here, the focus is the habit built around
them.

**Absolute path** — starts from the filesystem root (`/` on Linux/WSL, or a drive letter like `C:\`
on Windows) and means the same thing no matter where you currently are:

```bash
/home/you/practice-shell/notes.md
```

**Relative path** — starts from your current directory, so its meaning depends entirely on where
you are when you use it:

```bash
notes.md            # a file right here
../notes.md         # a file one directory up
data/notes.md        # a file in a subdirectory called "data"
```

**The habit:** before running any command that creates, copies, moves, or deletes something, run
`pwd` (Bash) or `Get-Location` (PowerShell) first, and read the result — don't assume you're where
you think you are, especially after a series of `cd` commands or switching terminal tabs.

```bash
pwd
```

```text
/home/you/practice-shell
```

If a relative path in a command doesn't do what you expect, the very first thing to check is
whether your assumption about the current directory was actually correct.

### 3. Windows vs. Linux/WSL Path Differences

If you work in both Windows PowerShell and Linux/WSL2 (as Stage 0 assumes), path differences are a
common source of "file not found" confusion — not because either system is broken, but because they
use different conventions.

| | Windows (PowerShell) | Linux/WSL2 (Bash) |
|---|---|---|
| Separator | Backslash `\` | Forward slash `/` |
| Root | A drive letter, e.g. `C:\` | A single root, `/` |
| Case sensitivity | Not case-sensitive | Case-sensitive (`Notes.md` ≠ `notes.md`) |
| Example absolute path | `C:\Users\you\project\notes.md` | `/home/you/project/notes.md` |
| Accessing the other OS's files | Native | `/mnt/c/Users/you/...` reaches Windows's `C:\Users\you\...` from inside WSL2 |

**Why this matters practically:** a path copied from a Windows file explorer will not work directly
in a WSL2 Bash prompt, and vice versa. When something in WSL2 can't find a file you know exists on
Windows, check whether you're using a Windows-style path (`C:\...`) where a Linux-style one
(`/mnt/c/...`) is needed — this single mix-up accounts for a large share of early "path" confusion.

### 4. Files, Folders, and Extensions

A **file** holds data; a **folder** (directory) holds files and other folders, organizing them into
a tree — you covered the shape of this tree in Module 0.2's
[Filesystems](../02-Operating-System-Fundamentals/07-filesystems.md) lesson.

A **file extension** (`.md`, `.py`, `.txt`, `.log`) is the part of the name after the last dot. On
Linux, **the extension is only a naming convention** — the operating system doesn't refuse to run a
Python script just because you named it `script.txt`, and renaming `notes.md` to `notes.py` doesn't
turn it into working code. Programs and editors use the extension as a *hint* about how to treat a
file — it is not an enforced rule the way it can feel like on some systems.

### 5. Hidden Files

On Linux/WSL2, any file or folder whose name starts with a dot is **hidden** from a plain listing —
for example, `.gitignore`, `.env`, or `.bashrc`. This is a display convention, not a security
feature: hidden files are ordinary files, just filtered out of `ls`'s default output so everyday
directory listings aren't cluttered with configuration files.

```bash
ls
ls -a
```

`ls -a` (**a**ll) shows hidden entries too, including the special `.` (this directory) and `..`
(parent directory) entries every directory has. You will rely on `ls -a` constantly once you start
working with `.env` and `.gitignore` files (Stage 0 Gap 0E and Gap 0A).

### 6. UTF-8 Text and Line Endings

**UTF-8** is the character encoding almost every modern text file uses — a standard way of
representing letters, numbers, symbols, and characters from virtually any language as bytes on
disk. You rarely need to think about it directly, except when a tool complains about "encoding" or
displays odd characters — that's usually a sign a file isn't UTF-8, or was mishandled between
programs that disagree about encoding.

**Line endings** are the invisible character(s) marking where one line ends and the next begins.
Linux/WSL2 uses a single character, `\n` (**LF**, line feed). Windows uses two characters, `\r\n`
(**CRLF**, carriage return + line feed). Most of the time this is invisible and harmless. It becomes
visible when:

- A script written on Windows and run in Bash on Linux fails with a strange error mentioning `\r`
  or "command not found" for a command that clearly exists — the extra `\r` character got
  interpreted as part of the command.
- A file edited on both systems shows every line as "changed" in a diff, even though the visible
  text is identical — only the line endings differ.

You don't need to fix this yourself yet; you only need to recognize it as a real, named cause the
next time something behaves strangely for no visible reason.

### 7. Permissions and Ownership — a Safe Introduction to `chmod`

Module 0.2's [Permissions](../02-Operating-System-Fundamentals/08-permissions.md) lesson covers the
full model — read that first if any of this feels new. Here is the safe, practical minimum for
everyday command-line work.

Every file has an **owner** and a set of **permissions** — read (`r`), write (`w`), and execute
(`x`) — for the owner, a group, and everyone else. Reading them from `ls -l`:

```bash
ls -l notes.sh
```

```text
-rwxr--r-- 1 you you 120 Sep 15 10:00 notes.sh
```

Reading left to right: `-` (a regular file), then three groups of three: `rwx` (owner: read, write,
execute), `r--` (group: read only), `r--` (others: read only).

**Safe, minimal `chmod` use** — making a script you wrote yourself executable:

```bash
chmod u+x notes.sh
```

- `chmod` — **ch**ange **mod**e (permissions).
- `u+x` — for the **u**ser (owner), **add** the e**x**ecute permission. Symbolic form like this is
  easier to reason about safely than memorizing numeric permission codes while you're still
  building the habit.

**Safety rule for this lesson:** only run `chmod` on files you created yourself, inside your
practice directory. Never run `chmod 777` (which grants everyone full read/write/execute) as a way
to "make an error go away" — it is not a fix, and Module 0.2's Permissions lesson explains exactly
why.

### 8. Symbolic Links — What They Are and Why You Must Identify Them First

A **symbolic link** (symlink) is a special file that points to another file or directory by path,
rather than containing real data of its own — similar to a shortcut. `ls -l` reveals one clearly:

```bash
ls -l
```

```text
lrwxrwxrwx 1 you you 20 Sep 15 10:00 latest-log -> logs/2026-09-15.log
```

The leading `l` (instead of `-` or `d`) means "this is a link," and the `->` shows what it points
to.

**Why you must identify a symlink before moving or deleting it:** deleting a symlink only removes
the link itself — the file it points to is untouched. But moving or copying *through* a symlink, or
assuming a symlink "is" the file it points to, can lead to confusing results — editing what you
think is a copy but is actually the original, or being surprised when a "deleted" file's data is
still there because you only removed a link to it. The habit: run `ls -l` before acting on anything
whose name or role you're unsure about, and read the first character and any `->` in the output
before deciding what a `cp`, `mv`, or `rm` command will actually do.

### 9. Safe Deletion Principles

This is the single most important habit in this lesson, because it's the one mistake that's hardest
to undo.

1. **Inspect before you delete.** Run `ls` (or `ls -la` for hidden files) on the exact target
   first, and read the output — don't delete based on memory of what you think is there.
2. **Use a dedicated practice directory** (e.g. `~/practice-shell/`) for any exercise involving
   deletion, exactly as this and later lessons instruct — never practice destructive commands in
   Downloads, Documents, or a real project folder.
3. **Avoid broad recursive commands.** `rm -r some-folder/` removes a folder and everything inside
   it; only run a recursive delete when you can name the *exact* folder you intend to remove, having
   just listed its contents, and never as a hurried "clean everything up" gesture.
4. **Prefer deleting one named thing at a time** over a wildcard (`rm *`) until you are completely
   confident reading exactly what a wildcard will match — a mistaken wildcard is one of the most
   common ways to delete far more than intended.
5. **When in doubt, move instead of delete.** `mv` a file to a `trash/` folder inside your practice
   directory first, confirm nothing needed it, and delete it later — a reversible step beats an
   irreversible one when you're not fully sure.

### 10. Practical Command Walkthrough

All of this happens inside a dedicated practice directory:

```bash
mkdir -p ~/practice-shell/filesystem-literacy
cd ~/practice-shell/filesystem-literacy
pwd
```

Create a small file and a folder, and inspect them:

```bash
mkdir data
cp /etc/hostname ./data/example.txt   # copies a small, harmless system file as sample text
ls -la data
cat data/example.txt
less data/example.txt                # press q to quit
find . -name "*.txt"
```

- `mkdir` — make a new directory.
- `cp SOURCE DEST` — copy a file; here, a small existing text file, so you have real content to
  practice on without writing anything sensitive.
- `ls -la` — list all entries, including hidden ones, in long format (showing permissions and
  ownership, Section 7).
- `cat` — print a file's entire contents to the terminal at once.
- `less` — view a file's contents one screen at a time (useful for anything longer than a screen).
- `find . -name "*.txt"` — search the current directory tree (`.`) for filenames matching a pattern.

**PowerShell equivalents:**

```powershell
New-Item -ItemType Directory -Force ~/practice-shell/filesystem-literacy
Set-Location ~/practice-shell/filesystem-literacy
Get-Location
New-Item -ItemType Directory data
Copy-Item C:\Windows\System32\drivers\etc\hosts .\data\example.txt
Get-ChildItem -Force data
Get-Content .\data\example.txt
Get-ChildItem -Recurse -Filter *.txt
```

### 11. Common Mistakes and Safe Troubleshooting

| Problem | Likely cause | Safe next step |
|---|---|---|
| `No such file or directory` | A relative path was resolved against the wrong current directory | Run `pwd` and `ls` first, and rebuild the path from what you actually see, not from memory. |
| A WSL2 command can't find a file you know exists on Windows | Used a Windows-style path (`C:\...`) inside Bash | Rewrite it as `/mnt/c/...` (Section 3). |
| `Permission denied` running a script you just wrote | The file lacks execute permission | Check with `ls -l`, then `chmod u+x <file>` on that exact file only (Section 7) — never `chmod 777` as a shortcut. |
| A script fails with an error mentioning `\r` or a command that "isn't found" even though it clearly exists | Windows-style line endings (CRLF) in a file meant to run on Linux | Recognize this as a line-ending issue (Section 6) rather than assuming the script itself is broken. |
| Deleted or moved a file unexpectedly through what turned out to be a symlink | Didn't check with `ls -l` first | Reread Section 8; going forward, always check for a leading `l` and `->` before acting on an unfamiliar entry. |

### 12. Exercises

1. In a fresh terminal, run `pwd`, then `cd` into two or three different directories, running `pwd`
   after each move. Write down, before each `cd`, what you *expect* the new directory to be — then
   confirm.
2. In your WSL2 terminal, try to `cat` a file using its Windows-style path (e.g.
   `C:\Users\you\Desktop\test.txt`), observe the error, then correctly reach the same file using
   `/mnt/c/...`.
3. Create a file, list it with `ls -l`, and write out — in your own words — what each of the nine
   permission characters means.
4. Make a small script executable with `chmod u+x`, confirm the permission change with `ls -l`
   before and after.
5. Create a symlink (`ln -s target linkname`), then run `ls -l` and identify it correctly before
   doing anything else with it.

### 13. Expected Results

- **Exercise 1:** each `pwd` result matches your written prediction; any mismatch is evidence of a
  path or `cd` misunderstanding worth investigating immediately, not glossing over.
- **Exercise 2:** the Windows-style path fails inside Bash (`No such file or directory`); the
  `/mnt/c/...` form succeeds.
- **Exercise 3:** your explanation correctly separates owner/group/others and read/write/execute,
  matching Section 7.
- **Exercise 4:** `ls -l` shows no `x` before, and an `x` in the owner's position after `chmod
  u+x`.
- **Exercise 5:** `ls -l` shows a leading `l` and a `->` pointing at the target — confirmed evidence
  before you'd act on it further.

### 14. Why This Matters for AI Engineering

- **Reading logs reliably** depends on knowing exactly which file and directory you're looking at —
  a wrong-directory mistake makes you debug the wrong log entirely, and mismatched line endings
  (Section 6) can make grep or diff behave unexpectedly on log files moved between systems.
- **Working in a real codebase** means constantly moving between directories, and AI/ML projects
  commonly reference relative paths like `data/raw/` or `checkpoints/` — an uncertain current
  directory is one of the most common causes of "file not found" errors in training and evaluation
  scripts.
- **Model files and configuration** are often large, and a careless recursive delete or an
  overwrite from a wrong-path `cp`/`mv` can destroy hours of downloaded or trained work — Section
  9's safe-deletion habits exist specifically to prevent this class of costly mistake.
- **Permissions failures** are a routine, specific cause of a model server or script failing to read
  a checkpoint or write a log file — being able to read a permission string and apply a minimal,
  correct `chmod` (Section 7) turns a mysterious failure into a two-minute fix.
- **Reliability, generally**, comes from habits, not memory: confirming your directory, inspecting
  before deleting, and recognizing symlinks are exactly the small, repeatable checks that prevent
  the class of mistake that's expensive to recover from in any real engineering environment.

---

### Summary

Filesystem literacy is a set of small habits, not a body of trivia: know your current directory
before you act, understand why a path that works on Windows may not work in WSL2, recognize hidden
files, extensions, UTF-8 text, and line endings as named, specific things rather than sources of
mysterious errors, read a permission string before reaching for `chmod`, identify a symlink before
acting on it, and always inspect before you delete — especially anything recursive. None of this
requires memorizing new commands beyond what earlier lessons already taught; it's the discipline
around using them safely.

### Completion Checklist

- [ ] I can state my current directory with certainty, using `pwd`/`Get-Location`, before running a
      command that changes anything.
- [ ] I can explain the difference between an absolute and a relative path, and why a Windows-style
      path fails inside WSL2 Bash.
- [ ] I can explain what a hidden file, a file extension, UTF-8 text, and a line ending are, in my
      own words.
- [ ] I read a real permission string with `ls -l` and correctly explained every character.
- [ ] I safely used `chmod u+x` on a file I created myself, and confirmed the change.
- [ ] I identified a symbolic link using `ls -l` before treating it as an ordinary file.
- [ ] I can list, from memory, the five safe-deletion principles in Section 9.
- [ ] I completed Section 12's exercises and my results match Section 13's expected results.

---

_This lesson is complete. It covers safe terminal habits and filesystem literacy as an extension to
Module 0.3, drawn from Stage 0 Gap 0B. It intentionally does not re-teach `pwd`, `ls`, `cd`, `cp`,
`mv`, `rm`, or `mkdir` in full — those remain the subject of `01-navigation.md` and
`02-file-operations.md`. Shell quoting and standard streams are covered next, in
[`12-shell-quoting-and-standard-streams.md`](./12-shell-quoting-and-standard-streams.md)._
