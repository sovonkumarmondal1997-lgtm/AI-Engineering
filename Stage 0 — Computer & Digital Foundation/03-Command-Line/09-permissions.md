# Module 0.3 — Command Line

## Lesson 9 — Permissions

**Module:** Command Line
**Roadmap reference:** Stage 0 — Module 0.3 — Command Line
**Concept(s) covered:** file permissions, ownership (user/group/others), `rwx`, numeric and symbolic `chmod`, `stat`, `whoami`/`id`/`groups`
**Status:** Complete
**Builds on:** 01-navigation.md, 02-file-operations.md, 06-pipes-and-redirection.md, 07-environment-variables.md, 08-shell-scripts.md, and Module 0.2 (processes, filesystems, system calls, standard I/O)

---

## 1. Lesson Overview

**Purpose:** every command you've run so far has quietly succeeded because you happened to have permission to do what you asked. This lesson makes that invisible layer visible — it teaches you what a permission actually is, how to read one, how to change one safely, and how to reason about the many "it exists, but I can't touch it" failures that permissions cause.

**Prerequisites:** this lesson assumes you're comfortable with `pwd`, `ls`, `cd`, `cp`, `mv`, `mkdir`, `cat`, `grep`, pipes/redirection, environment variables, and basic shell scripts (Lessons 01–08). It does not re-teach any of them — it uses them as the context permissions apply to.

**Why permissions belong in command-line engineering, not just "Linux administration":** almost every confusing "it should work, but it doesn't" moment you'll encounter for the rest of this roadmap — a script that won't run, a service that can't read a model file, a write that silently fails — eventually reduces to permissions. Understanding this layer now means you'll recognize these failures on sight later, instead of guessing.

**The relationship this lesson builds toward:**

```text
Files
  ↓
Ownership
  ↓
Permissions
  ↓
Access decision
  ↓
Program/process behavior
```

Every file has an **owner** (Section 3); that owner, plus a **group**, plus everyone else, each have a set of **permissions** (Sections 4–7) on that file; when some process tries to do something with the file, the operating system makes an **access decision** based on all of that (Section 13); and *that decision* — allowed or denied — becomes part of how the running program actually behaves (Section 14), sometimes in ways that look, at first, like a completely unrelated bug.

**Learning objectives.** By the end of this lesson you will be able to:

- Explain what a file permission is, and why operating systems need access control at all.
- Explain users, groups, owners, and others, and inspect your own identity (`whoami`, `id`, `groups`).
- Read a permission string from `ls -l` (e.g. `-rw-r--r--`) correctly, piece by piece.
- Explain `r`, `w`, and `x` for regular files — and explain how their meaning **changes** for directories.
- Explain why directory permissions and file permissions are not the same thing, and why deleting a file depends on the *directory's* permissions, not the file's own write permission.
- Decode and apply numeric permissions (`644`, `755`, `700`, `600`) and symbolic permissions (`u+x`, `g-w`, `o-r`).
- Use `chmod` safely, in both numeric and symbolic form.
- Use `stat` to inspect detailed file metadata, and explain how it differs from `ls -l`.
- Reason through a permission-check flow methodically, rather than guessing.
- Diagnose common permission failures — including several that look like they should be unrelated bugs.
- Explain why permissions matter for shell scripts (Lesson 08) and file operations (Lesson 02).
- Explain the principle of least privilege, and why `chmod 777` is not a real fix.
- Explain why permissions matter specifically in Applied AI Engineering workflows.

---

## 2. What Are File Permissions?

**A simple analogy first:** think of a shared filing cabinet in an office. Some drawers are labeled "anyone can read this, but only I can add new pages"; others are locked to everyone except one specific person. A **permission** is exactly that label, attached to a real file or directory, describing who is allowed to do what with it.

**The technical model:** a **filesystem object** (a file or a directory — you met both in Lesson 01) has, alongside its actual data, a small set of rules describing **access** — what specific operations (reading, changing, running) are allowed, and by whom. **Ownership** identifies *whose* rules apply first (Section 3); **permission** is the actual rule itself (read/write/execute, per category).

**Why operating systems need this at all:** a computer running many programs — sometimes on behalf of many different people or services — needs some way to stop one program or user from freely reading or overwriting another's files, whether by mistake or by malicious intent. Permissions are the operating system's foundational mechanism for expressing "who is allowed to do what, to this specific thing."

**Permissions determine what certain users/processes are allowed to do with filesystem objects** — nothing more, nothing less. This is deliberately precise, because of an important, required correction: **permissions are not, in every situation, an absolute, unbreakable security boundary.** They are one real, load-bearing mechanism among several a full security posture might include (Section 22 names some of the others by name, without teaching them). This lesson teaches permissions as the foundational, everyday access-control layer you'll interact with constantly — not as a claim that they solve every security problem in every environment.

---

## 3. Users, Groups, Owners, and Others

**User identity:** every person or process acting on a Linux system does so *as* some **user**. Internally, the system tracks this using a numeric **UID** (User ID) — the username you see is just a friendly label for that number.

**Group identity:** users can belong to one or more **groups** — a way of bundling several users together so permissions can be granted to "this whole group" at once, rather than to each person individually. Internally, tracked via a numeric **GID** (Group ID).

**How this attaches to a file:** every file has exactly one **owner** (a specific user) and exactly one **group** associated with it. Anyone who is neither the owner nor a member of that group falls into a third category: **others**.

```text
User
  ↓
UID

Group
  ↓
GID

File
  ├── owner
  └── group

Everyone else
  ↓
others
```

**Inspecting your own identity:**

```bash
whoami
```
Prints your current username.

```bash
id
```
Prints your UID, your primary GID, and every group you belong to, in one line.

```bash
groups
```
Prints just the list of group names you belong to.

Example output (illustrative — your actual values will differ):
```text
$ whoami
learner

$ id
uid=1000(learner) gid=1000(learner) groups=1000(learner),27(sudo)

$ groups
learner sudo
```

**Why groups exist:** on a system used by more than one person (or by several services), groups let you grant access to a whole team or role at once — "everyone on the `data-team` group can read this dataset" — without having to name every individual user separately, and without having to open access to literally everyone (`others`). This connects directly to **multi-user systems** (several human accounts on one machine) and **services** (a running program, like a web server or an AI inference service, often operates under its own dedicated user/group identity, distinct from the developer who wrote it — a theme this lesson returns to repeatedly in Sections 14, 22, and 24).

---

## 4. Reading `ls -l`

```bash
ls -l
```

You met the long-listing form of `ls` briefly back in Lesson 01 — this lesson is where you learn to actually read every part of it.

Example output:
```text
-rw-r--r--  1 learner learner  220 Sep  8 19:10 notes.txt
drwxr-xr-x  2 learner learner 4096 Sep  8 19:10 project/
```

Focus on the first column — the **permission string**, e.g. `-rw-r--r--`. Broken into its pieces:

```text
-
rw-
r--
r--
```

| Position | Meaning |
|---|---|
| first character | file type indicator |
| next 3 characters | owner permissions |
| next 3 characters | group permissions |
| final 3 characters | others permissions |

**File type indicator, at a foundational level:** `-` means an ordinary regular file; `d` means a directory (as seen in `drwxr-xr-x` above). This lesson does not expand into the full range of other, more obscure type indicators (symbolic links and other special file types) — only these two, which cover the overwhelming majority of what you'll encounter in this roadmap's early stages.

So `-rw-r--r--` reads as: a regular file (`-`), whose owner can read and write but not execute (`rw-`), whose group can only read (`r--`), and whose others can only read (`r--`).

---

## 5. `r`, `w`, and `x`

For **regular files**, each of the three permission letters means:

### Read (`r`)
Can the file's **contents** be read (e.g. opened and viewed with `cat`, Lesson 03)?

### Write (`w`)
Can the file's **contents** be modified (e.g. overwritten by a text editor, or by redirection, Lesson 06)?

### Execute (`x`)
Can the file be **run** as a program or script — subject to other requirements (for a script, this is exactly the requirement Lesson 08, Section 6 introduced for `./script.sh`; for a compiled program, it's the direct equivalent)?

**A required, explicit clarification:** execute permission on a file is **not** the same thing as read permission, and neither implies the other. A file can have execute permission without read permission (unusual, but possible — you could be allowed to *run* something without being allowed to *view its contents*), and — far more commonly encountered — a file can have read permission without execute permission (an ordinary text file, or a script you can view with `cat` but cannot yet run directly with `./`, exactly the situation Lesson 08's `chmod +x` addressed).

**For directories, the meaning of `r`, `w`, and `x` changes substantially** — enough that it deserves its own dedicated section next. Do not assume directory permissions work "the same way, but for a folder" — they don't, and this is one of the most consequential distinctions in this entire lesson.

---

## 6. Directory Permissions

**This is a critical concept — read it slowly.**

For a **directory**, the same three letters mean something structurally different from what they mean for a file:

```text
Directory:
r → list directory entries
w → modify directory entries
x → search/traverse/access entries

Most create/delete/rename operations require both w and x
on the relevant directory.
```

- **`r` on a directory** — controls whether you can **list** what's inside it (e.g. run `ls` on it and actually see the names of its contents).
- **`w` on a directory** — controls whether you can **modify entries within it** (create, delete, or rename them — which in practice also requires `x` on that directory, see below) — note carefully: this is about modifying the *directory's own listing* (adding/removing names from it), not about modifying the *contents* of files that happen to live inside it.
- **`x` on a directory** — controls whether you can **traverse into it** — enter it, and access things by name inside it (including things nested more deeply within it).

**Why `directory write ≠ file write`, stated directly:** having write permission (together with search/`x` permission) on a directory lets you add, remove, or rename the *entries* (names) listed inside it. It says nothing at all about whether you can modify the *contents* of a specific file inside that directory — that's governed by the *file's own* `w` permission (Section 7's comparison table makes this side by side).

**Why a user might be able to read a file but still fail to access it, because of directory traversal permissions:** even if you have full `rwx` on a specific file itself, if you lack **execute (`x`)** permission on *any directory in the path leading to it*, you cannot reach the file at all — the system never even gets to check the file's own permissions, because it can't traverse the path to find it in the first place. This is why "I have `rw-` on this exact file, why can't I open it?" is very often actually a directory-permission problem, one level up (or more), not a file-permission problem at all.

**Simple example, illustrated conceptually:**

```text
/home/learner/private/secret.txt

secret.txt permissions: rw-r--r--  (looks perfectly readable)
private/  permissions:  drw-r--r--  (missing 'x' for group/others!)
```

Even though `secret.txt` itself looks readable by anyone, a user who is not the owner of `private/` cannot traverse into it at all (no `x`), and therefore can never reach `secret.txt` — regardless of how permissive `secret.txt`'s own permissions look.

---

## 7. File Permissions vs. Directory Permissions

| Permission | Regular File | Directory |
|---|---|---|
| `r` | Read contents | List entries |
| `w` | Modify contents | Modify entries (create/delete/rename generally need `w` and `x` on the directory) |
| `x` | Execute the file | Traverse/access entries |

**Important edge cases, stated conceptually:**

- A file can be **deletable** even if the file itself has **no write permission**, as long as the **containing directory** has write permission for you — because deleting means removing an *entry from the directory's listing*, not modifying the file's own contents (Section 16 returns to this directly, since it's a very common and consequential misconception).
- A directory can be **listable** (`r`) without being **enterable** (`x`) — you could see the *names* of things inside it (if `r` is set) but be unable to actually go into it or open anything by name inside it (if `x` is missing). In practice, a directory almost always needs both together to be genuinely useful.
- A directory can be **enterable** (`x`) without being **listable** (`r`) — you could `cd` into it and access a file if you already know its exact name, but you couldn't run `ls` inside it to *discover* what's there.

---

## 8. Numeric / Octal Permissions

Each permission letter has a numeric value:

```text
r = 4
w = 2
x = 1
```

Adding the values for whichever permissions are granted produces a single digit per category (owner/group/others):

```text
7 = rwx   (4+2+1)
6 = rw-   (4+2)
5 = r-x   (4+1)
4 = r--   (4)
3 = -wx   (2+1)
2 = -w-   (2)
1 = --x   (1)
0 = ---   (nothing)
```

Three digits together — owner, group, others, in that order — give a complete permission setting.

### `644`

```text
644

owner  → rw-
group  → r--
others → r--
```

Owner can read and write; everyone else can only read. A common default for ordinary data files.

### `755`

```text
755

owner  → rwx
group  → r-x
others → r-x
```

Owner can read, write, and execute; everyone else can read and execute, but not modify. A common pattern for scripts and programs meant to be run by others but changed only by the owner (directly relevant to Lesson 08's `chmod +x` — this is one of the actual numeric values that grants execute permission).

### `700`

```text
700

owner  → rwx
group  → ---
others → ---
```

Only the owner has any access at all. Common for private scripts or directories not meant to be touched by anyone else on a shared system.

### `600`

```text
600

owner  → rw-
group  → ---
others → ---
```

Only the owner can read or write; no execute for anyone, no access at all for group/others. A common pattern for sensitive personal files.

**A required, explicit correction:** these four values are common, recognizable *patterns* — not universally correct answers for every situation. Which permission is actually appropriate depends entirely on context: who legitimately needs access, and to do what. Section 19 returns to this directly.

---

## 9. Symbolic Permissions

An alternative way of expressing *who* and *what*, using letters instead of numbers:

```text
u = user/owner
g = group
o = others
a = all (owner, group, and others together)
```

Symbolic changes use `+` (add a permission), `-` (remove a permission), or `=` (set exactly this permission, replacing whatever was there):

```bash
chmod u+x script.sh
chmod g-w file.txt
chmod o-r file.txt
```

- `chmod u+x script.sh` — **add** execute permission for the **owner** only, leaving group/others untouched.
- `chmod g-w file.txt` — **remove** write permission for the **group** only.
- `chmod o-r file.txt` — **remove** read permission for **others** only.

**The key advantage of symbolic form over numeric form:** you can change just *one* category's *one* permission bit without needing to know or restate the other five bits — numeric form (Section 8) always specifies all nine bits at once; symbolic form lets you make a small, targeted adjustment.

---

## 10. `chmod`

`chmod` ("change mode") changes a filesystem object's permission bits.

### Numeric form

```bash
chmod 644 file.txt
chmod 755 script.sh
chmod 700 private.txt
chmod 600 private.txt
```

Each of these **replaces the entire permission setting** with the exact three-digit value given (Section 8).

### Symbolic form

```bash
chmod u+x script.sh
chmod g-w file.txt
chmod o-r file.txt
```

Each of these **adjusts one specific bit**, leaving the rest of the permission setting unchanged (Section 9).

**What `chmod` changes, stated precisely:** the file's **mode bits** — this lesson focuses on the ordinary owner/group/others `rwx` permission bits — and nothing about who owns it. **A required, explicit correction: `chmod` does not change file ownership.** Changing who *owns* a file is a separate operation (conventionally `chown`, which this lesson does not teach, since it's outside this lesson's scope of foundational permission bits) — `chmod` only ever adjusts the `rwx` settings for the owner/group/others categories that already exist on the file.

**Permissions belong to the filesystem object itself** — not to you, not to your current shell session. Once changed, the new permission persists on that file/directory regardless of who's looking at it or which shell session is active, until something changes it again.

---

## 11. Inspecting Permissions with `stat`

```bash
stat file.txt
```

Example output (illustrative):
```text
  File: file.txt
  Size: 220             Blocks: 8          IO Block: 4096   regular file
Device: 802h/2050d      Inode: 1234567     Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/ learner)   Gid: ( 1000/ learner)
Access: 2026-09-08 19:10:00.000000000 +0000
Modify: 2026-09-08 19:10:00.000000000 +0000
Change: 2026-09-08 19:10:00.000000000 +0000
```

**Why `stat` is useful:** `ls -l` gives you a fast, convenient, human-scannable overview — great for glancing at a whole directory at once. `stat` gives you significantly more detailed metadata about **one specific object** — including the numeric permission value directly (`0644`), explicit UID/GID, and multiple separate timestamps.

**The distinction, stated directly:**
- `ls -l` — convenient, human-readable, best for scanning many files at once.
- `stat` — more detailed, best for a focused look at exactly one file's metadata.

This lesson does not turn `stat` into a complete filesystem-metadata course — only enough to know it exists, what it's for, and how it complements `ls -l`.

---

## 12. Who Am I, and What Groups Do I Belong To?

Practical identity inspection, tying Section 3's commands directly into a debugging habit:

```bash
whoami
id
groups
```

**How this helps debug permission problems:** a permission failure is always the answer to a question involving *both* "who is asking?" and "what does the target allow?" — you cannot reason about the second half without first being certain of the first.

**Example diagnostic flow:**

```text
Who am I?
   ↓
What UID do I have?
   ↓
What groups do I belong to?
   ↓
Who owns the file?
   ↓
What group owns the file?
   ↓
What permissions exist?
   ↓
Why is access allowed/denied?
```

This flow — identity first, then target, then the actual permission bits, then a reasoned conclusion — is the backbone of nearly every debugging scenario in Section 21. Memorize the *order*, not just the individual commands.

---

## 13. Permission-Check Flow

A strong conceptual model for what happens when a process tries to access a filesystem object:

```text
Process
  ↓
Identity
  ↓
Which user?
  ↓
Which groups?
  ↓
Target filesystem object
  ↓
Owner/group/others permissions
  ↓
Requested operation
  ↓
Access decision
```

Step by step: a running **process** (Module 0.2's concept) has an **identity** — the user (and groups) it's running as. When it attempts an operation (read, write, execute) against a specific filesystem object, the operating system compares that identity against the object's **owner**, **group**, and **others** permission bits, checks whether the **specific requested operation** is permitted for whichever category actually applies (owner, if the process's user matches the file's owner; else group, if the process's user belongs to the file's group; else others), and returns an **access decision** — allow, or deny.

**A required, explicit acknowledgment:** this lesson teaches the basic traditional Unix/Linux owner/group/others permission-bit model. Real systems can have additional access-control mechanisms, which are outside this lesson's scope, and the actual kernel-level permission model has additional real-world details and nuances beyond this simplified flow — this lesson presents the **foundational model**, sufficient for reasoning about and debugging the overwhelming majority of everyday permission situations you'll encounter, without claiming to be a complete, exhaustive account of every kernel-level subtlety.

**Connecting to Module 0.2:** this flow directly reuses concepts you already have — **processes** (a running program with an identity), **user space** (where ordinary programs, as opposed to the kernel itself, run), **system calls** (the mechanism by which a process asks the kernel to actually perform a filesystem operation — mentioned here only conceptually, exactly as earlier lessons have consistently done, not re-taught), **filesystems** (where the object and its metadata live), and **file descriptors** (Lesson 06's concept — what a process holds once an open, permitted access has actually been granted). This lesson does not re-teach any of these; it only shows you where permission-checking fits into that already-familiar picture.

---

## 14. Permissions and Processes

**Why permissions apply to processes attempting operations, restated directly:** a permission check is never about "the file" in isolation — it's about a *specific attempt*, by a *specific process*, running as a *specific identity*, to do a *specific thing* to that file. The same file can be perfectly accessible to one process and completely inaccessible to another, purely because they're running as different identities.

```text
Python service
      ↓
process identity
      ↓
attempt to open model file
      ↓
OS permission check
      ↓
allowed / denied
```

**Why a process can fail even when the file exists, stated directly:** "the file exists" answers a completely different question from "is *this specific process*, running as *this specific identity*, allowed to access it?" A file can exist, be perfectly intact, and still be entirely inaccessible to a given process — which is exactly why "but the file is right there!" is not, on its own, evidence that something else is wrong.

**Connecting to a familiar Python error:** this is precisely the scenario behind a Python `PermissionError` — the file genuinely exists; the code's logic is genuinely correct; the actual cause is that the operating system denied the specific access attempt, for the specific identity the Python process happens to be running as. This lesson does not teach Python exception handling — it only explains, at the permissions level, *why* this specific category of error occurs, so you recognize it correctly when you see it later.

---

## 15. Permissions and Shell Scripts

This connects directly to `08-shell-scripts.md` — nothing here repeats that lesson's material in depth.

Recall from Lesson 08, Section 6: `./script.sh` requires the script file to have **executable permission**, because you're asking the system to run the file **directly**, using its shebang to determine the interpreter. `bash script.sh`, by contrast, needs **no** special execute permission on the script file — you're explicitly telling the already-runnable `bash` program to read the file's *contents* as input; the file itself is never being "run" as a program in that case.

```bash
bash script.sh    # no execute permission needed on script.sh
./script.sh        # requires execute permission on script.sh
```

This lesson's contribution beyond Lesson 08's brief mention: you now understand **why**, precisely, in terms of the `rwx` model from Sections 5 and 8 — `x` is specifically the bit that governs whether a file may be run directly as a program, distinct from `r` (whether its contents can be read/viewed) — and you now have the tool (`chmod +x`, or the numeric equivalent, e.g. `755`) to grant it deliberately, understanding exactly what you're changing and why.

---

## 16. Permissions and File Operations

This connects directly to `02-file-operations.md` — nothing here repeats that lesson's commands in depth.

Commands like `cp`, `mv`, `rm`, and `mkdir` can all be affected by permissions, in ways that trace back to the file-vs-directory distinction from Section 6:

- **Unable to create a file** — typically a **directory** permission problem (you lack `w` and/or `x` on the directory you're trying to create something inside).
- **Unable to delete a file** — again, typically a **directory** permission problem (`w` and `x` on it), *not* a problem with the file's own permissions (see the required correction below).
- **Unable to enter a directory** — a directory **execute** (`x`) permission problem (Section 6).
- **Unable to rename an entry** — a directory permission problem (`w` and `x`) on the directory the entry lives in (renaming is, structurally, removing one directory entry and adding another; renaming across directories involves the directories on both sides).

**This is an important misconception to address directly, exactly as Section 7 flagged it:** deleting or renaming a file is strongly related to the **permissions on the file's containing directory** — specifically, whether you have write and search (`x`) permission *on that directory* — not simply the file's own write permission. A file with absolutely no write permission of its own (`r--r--r--`, or even `------` with nothing at all) can still be perfectly deletable, if you have write permission on the directory it lives in — because `rm` doesn't need to modify the file's contents to remove it; it needs to remove the file's *entry* from its containing directory's listing, which is governed primarily by the *directory's* permissions (`w` plus `x`), not the file's. Additional restrictions can also apply: in shared world-writable directories such as `/tmp`, the sticky bit can further restrict who may delete or rename entries.

---

## 17. Safe Practical Demonstration

Everything below uses a **disposable, learner-created practice directory** — created uniquely with `mktemp -d` and referred to below as `$DEMO_DIR`. **This lesson does not create this directory for you.** You may create it manually, using commands from earlier lessons:

```bash
DEMO_DIR="$(mktemp -d)"
cd "$DEMO_DIR"
```

**No command in this section has actually been executed by this lesson.** Every result shown is explicitly labeled `Example output:` — an illustration of expected behavior, never a captured result. Nothing here modifies real project files, system files, `/etc`, `/usr`, `/var`, `/root`, or any other sensitive system location; nothing here requires `sudo`; nothing here is destructive against any pre-existing file.

**1. Create a file**

```bash
printf "hello\n" > sample.txt
```

**2. Inspect permissions**

```bash
ls -l sample.txt
```
Example output:
```text
-rw-r--r-- 1 learner learner 6 Sep 10 12:00 sample.txt
```

**3. Inspect current user**

```bash
whoami
```
Example output:
```text
learner
```

**4. Inspect groups**

```bash
groups
```
Example output:
```text
learner
```

**5. Change permissions**

```bash
chmod 600 sample.txt
```

**6. Inspect again**

```bash
ls -l sample.txt
```
Example output:
```text
-rw------- 1 learner learner 6 Sep 10 12:00 sample.txt
```
Notice: group and others permissions are now completely absent (`------` beyond the owner's `rw-`).

**7. Test access safely**

```bash
cat sample.txt
```
Example output:
```text
hello
```
(This still succeeds because **you are the owner**, and the owner retains `rw-` — this deliberately demonstrates that removing group/others access has no effect on the owner's own access.)

**8. Restore safe permissions**

```bash
chmod 644 sample.txt
ls -l sample.txt
```
Example output:
```text
-rw-r--r-- 1 learner learner 6 Sep 10 12:00 sample.txt
```

**9. Clean up**

```bash
cd /tmp
rm -r "$DEMO_DIR"   # removes only the directory this exercise created
```

---

## 18. Practical Permission Experiments

All experiments below extend Section 17's disposable setup. Every experiment is safe, non-destructive, and uses only learner-created files.

### Experiment A — Read permission

```bash
printf "secret content\n" > readtest.txt
chmod 000 readtest.txt
cat readtest.txt
```
Expected behavior: `cat` fails with a permission-denied error, because read permission has been removed even for the owner.
```bash
chmod 644 readtest.txt   # restore
```

### Experiment B — Write permission

```bash
printf "original\n" > writetest.txt
chmod 444 writetest.txt
printf "changed\n" > writetest.txt
```
Expected behavior: the redirection attempt fails, because write permission has been removed — the file's contents cannot be overwritten this way.
```bash
chmod 644 writetest.txt   # restore
```

### Experiment C — Execute permission

```bash
printf '#!/usr/bin/env bash\necho "hi"\n' > runtest.sh
./runtest.sh
```
Expected behavior: this fails with a permission-denied error (exactly Lesson 08's first debugging scenario), because `runtest.sh` was never marked executable.
```bash
chmod +x runtest.sh
./runtest.sh
```
Expected behavior: now it succeeds, printing `hi`.

### Experiment D — Directory traversal

```bash
mkdir blocked-dir
printf "inside\n" > blocked-dir/inner.txt
chmod 644 blocked-dir      # remove execute permission on the directory
ls blocked-dir             # listing may still work, depending on the removed bit
cat blocked-dir/inner.txt
```
Expected behavior: accessing `inner.txt` directly fails, even though `inner.txt` itself was never touched — because the **directory's** execute permission, not the file's own permission, governs whether it can be traversed into (Section 6).
```bash
chmod 755 blocked-dir       # restore
```

### Experiment E — Ownership observation

```bash
ls -l sample.txt
stat sample.txt
id
whoami
groups
```
Purpose: compare `ls -l`'s quick summary against `stat`'s fuller detail (Section 11), and confirm your own identity against the file's reported owner/group.

**Never modify permissions on system-critical files as part of these experiments — every file touched above is one you created yourself, in a disposable directory, for this exact purpose.**

---

## 19. Common Permission Patterns

| Value | Decoded | Typical use | What it allows | What it does *not* guarantee |
|---|---|---|---|---|
| `644` | owner `rw-`, group `r--`, others `r--` | Ordinary data files, configuration meant to be read broadly | Owner can edit; everyone can read | Does not make the file executable; does not protect it from being deleted if the containing directory is writable by others (Section 16) |
| `755` | owner `rwx`, group `r-x`, others `r-x` | Scripts and programs meant to be run by others | Owner can edit and run; everyone can run, but not edit | Does not mean the file's contents are safe from being read by anyone who can run it (readability and executability aren't the same protection) |
| `700` | owner `rwx`, group `---`, others `---` | Private scripts/directories on a shared system | Only the owner has any access at all | Does not protect against a process running *as* the owner accessing it — permissions govern identity, not intent |
| `600` | owner `rw-`, group `---`, others `---` | Sensitive personal files, private notes | Only the owner can read or write | Not a substitute for real secret management (Lesson 07, Section 17) if the file's *contents* are genuinely sensitive credentials |

**Context determines the appropriate permission** — none of these four values is a universally "correct" default. A shared team dataset might legitimately need `664` (group-writable) or a group-oriented setup this lesson doesn't teach in depth; a private key–like file might legitimately need something even more restrictive than `600`. Treat these four as recognizable, common starting points to reason from — never as rules to apply blindly.

---

## 20. Common Mistakes and Misconceptions

**1. "`r` always means the same thing for files and directories."**
- *Correct understanding:* `r` on a file means readable contents; `r` on a directory means listable entries — related in spirit, but structurally different (Section 6).
- *Example:* a directory with `r` but no `x` lets you see filenames inside it but not open any of them.
- *Lesson:* always ask "file or directory?" before interpreting a permission bit.

**2. "`w` on a file controls whether the file can be deleted."**
- *Correct understanding:* deletion depends on the *containing directory's* permissions (write + search/execute), not the file's own (Section 16).
- *Example:* Experiment B-style file with `444` (no write) can still be `rm`-ed if the directory allows it.
- *Lesson:* deletion is a directory-listing operation, not a file-content operation.

**3. "Directory write permission equals file write permission."**
- *Correct understanding:* directory `w` (with `x`) governs adding/removing/renaming *entries*; it says nothing about a specific file's own `w` bit (Section 6, Section 7).
- *Example:* you can have `w` on a directory and still be unable to edit a specific file inside it whose own permissions deny you.
- *Lesson:* check both levels independently.

**4. "Execute permission means 'run anything.'"**
- *Correct understanding:* execute permission on a *file* means that specific file may be run (subject to it actually being a valid program/script); execute on a *directory* means something entirely different — traversal (Section 6).
- *Lesson:* "execute" is context-dependent, not one universal capability.

**5. "`644` is always correct."**
- *Correct understanding:* it's a common pattern, not a universal rule (Section 19).
- *Lesson:* context (who needs access, and to do what) determines the right value.

**6. "`755` is always correct."**
- *Correct understanding:* same as above — common for scripts meant to be run by others, not automatically appropriate everywhere.
- *Lesson:* same as above.

**7. "`chmod` changes ownership."**
- *Correct understanding:* `chmod` changes permission bits only; ownership is a separate concept this lesson does not teach how to change (Section 10).
- *Lesson:* don't conflate "who owns it" with "what it allows."

**8. "`ls -l` shows every possible access-control mechanism."**
- *Correct understanding:* `ls -l` shows the standard owner/group/others `rwx` bits; other access-control mechanisms exist on some systems (Section 22 names some, without teaching them) and aren't fully visible in this basic listing.
- *Lesson:* `ls -l` is a foundational view, not an exhaustive one.

**9. "Permissions are the same on every operating system."**
- *Correct understanding:* Windows has a genuinely different permission/security model (Section 26); this lesson's `rwx`/owner-group-others model is specifically the Linux/Unix model.
- *Lesson:* don't assume portability of this exact model across platforms.

**10. "`sudo` should be the first solution to every permission problem."**
- *Correct understanding:* a permission denial is often correct, informative behavior — the right first step is understanding *why*, not overriding it (this lesson's entire debugging section, Section 21, models this).
- *Lesson:* treat `sudo` as a last resort you fully understand the implications of, never a reflex.

**11. "Making everything `777` is a good fix."**
- *Correct understanding:* `777` grants full read/write/execute to owner, group, *and* others — removing essentially all access control on that object; this creates real security and reliability risk rather than solving the underlying problem (Section 22 addresses this directly and explicitly).
- *Lesson:* a permission error is a signal to diagnose, not an obstacle to blast through.

**12. "A file existing means the process can read it."**
- *Correct understanding:* existence and accessibility are separate questions (Section 14).
- *Lesson:* "the file is right there" is not evidence permissions are fine.

**13. "A Python service runs with the same access as the developer."**
- *Correct understanding:* a production service very often runs under its own distinct identity, different from the developer's own user account (Section 24).
- *Lesson:* never assume "it worked when I ran it" implies "it will work when the service runs it."

**14. "Group membership is irrelevant."**
- *Correct understanding:* group membership directly determines whether the *group* permission category applies to you at all (Section 3, Section 12).
- *Lesson:* always check `groups`/`id` before concluding a group-permission problem doesn't apply to you.

**15. "Directory traversal does not matter."**
- *Correct understanding:* missing `x` on any directory in a path blocks access to everything beneath it, regardless of that content's own permissions (Section 6).
- *Lesson:* a permission problem might be one or more directory levels away from the file you're actually looking at.

**16. "`bash script.sh` and `./script.sh` have identical permission requirements."**
- *Correct understanding:* only `./script.sh` requires execute permission on the file; `bash script.sh` does not (Section 15).
- *Lesson:* the two execution forms genuinely differ in what they require.

**17. "Permissions alone determine every access decision in every environment."**
- *Correct understanding:* other mechanisms can exist in some environments (Section 22); this lesson's model is foundational, not exhaustive (Section 2, Section 13).
- *Lesson:* stay precise about what this lesson actually claims to cover.

**18. "Windows permissions and Linux permissions are identical."**
- *Correct understanding:* genuinely different models (Section 26) — do not assume direct equivalence.
- *Lesson:* treat platform differences as real, not cosmetic.

**19. "WSL2 always behaves exactly like a native Linux installation."**
- *Correct understanding:* WSL2's Linux environment follows this lesson's model internally, but interoperability with the Windows filesystem can introduce real differences (Section 26).
- *Lesson:* don't assume perfect equivalence across that boundary.

**20. "Permission errors are random."**
- *Correct understanding:* every permission decision is fully determined by identity, target object, and requested operation (Section 13) — never random, even when the cause isn't immediately obvious.
- *Lesson:* a permission error always has a discoverable, specific cause; the diagnostic flow (Section 12) exists to find it.

---

## 21. Debugging Permission Problems

Work through each scenario's reasoning *before* reading the fix and prevention.

**Scenario 1 — `Permission denied` when reading a file**
- *Situation:* `cat secret-notes.txt` fails.
- *Symptom:* `cat: secret-notes.txt: Permission denied`
- *Likely causes:* missing read permission for your identity's applicable category, or a directory traversal problem one level up.
- *Diagnostic commands:* `ls -l secret-notes.txt`; `whoami`; `id`.
- *Reasoning process:* identify which category (owner/group/others) applies to you; check whether that category has `r`.
- *Root cause:* the applicable category lacks `r`.
- *Fix:* if you're the legitimate owner and this is your own disposable file, `chmod` to add `r` for the correct category.
- *Prevention:* check `ls -l` before assuming a file is readable.

**Scenario 2 — `Permission denied` when writing a file**
- *Situation:* redirecting output into a file fails.
- *Symptom:* `bash: file.txt: Permission denied`
- *Likely causes:* missing write permission for your applicable category.
- *Diagnostic commands:* `ls -l file.txt`.
- *Reasoning process:* same as Scenario 1, checking for `w` specifically.
- *Root cause:* the applicable category lacks `w`.
- *Fix:* `chmod` to add `w` for the correct category, if appropriate.
- *Prevention:* don't assume every file you can read is also writable — check both independently.

**Scenario 3 — `Permission denied` when executing a script**
- *Situation:* `./script.sh` fails.
- *Symptom:* `bash: ./script.sh: Permission denied`
- *Likely causes:* missing execute permission (Section 15; Lesson 08, Section 22's first scenario).
- *Diagnostic commands:* `ls -l script.sh`.
- *Reasoning process:* determine which permission class applies to the current identity (owner → owner execute bit; group → group execute bit; otherwise → other execute bit), and check for `x` in *that* class.
- *Root cause:* the file was never marked executable.
- *Fix:* `chmod +x script.sh`.
- *Prevention:* remember this is a one-time, necessary step for `./script.sh`, not for `bash script.sh`.

**Scenario 4 — File exists but application cannot open it**
- *Situation:* a program reports it cannot open a file you can plainly see with `ls`.
- *Symptom:* an open/read failure inside the application, despite the file's visible existence.
- *Likely causes:* the application is running as a different identity than you (Section 14, Section 24); or a directory traversal problem.
- *Diagnostic commands:* `ls -l` on the file and each parent directory; check what identity the application actually runs as, if you can determine it.
- *Reasoning process:* "exists" and "accessible to this specific process" are different questions (Section 14).
- *Root cause:* the process's identity lacks the needed permission, even though your own interactive shell's identity might have it.
- *Fix:* grant the correct category (matching the application's actual identity) the needed permission — never simply run everything as `sudo` to bypass this without understanding it.
- *Prevention:* always ask "which identity is actually making this request?" before trusting your own successful manual test.

**Scenario 5 — Directory exists but application cannot enter it**
- *Situation:* a program fails to access anything inside a directory that visibly exists.
- *Symptom:* a "cannot access" or similar error referencing the directory or something inside it.
- *Likely causes:* missing execute (`x`) permission on the directory (Section 6).
- *Diagnostic commands:* `ls -l` on the directory itself (or its parent, to see the directory's own permission bits).
- *Reasoning process:* recall that directory `x` governs traversal, separate from `r`.
- *Root cause:* the directory lacks `x` for the applicable category.
- *Fix:* `chmod` to add `x` for the correct category on the directory.
- *Prevention:* remember that directory permissions, not just file permissions, gate access (Section 6, Section 7).

**Scenario 6 — User is not in the required group**
- *Situation:* a file is group-readable, but you still can't read it.
- *Symptom:* `Permission denied`, despite the group category showing `r`.
- *Likely causes:* you're not actually a member of the file's group.
- *Diagnostic commands:* `ls -l` (to see which group owns the file); `groups` or `id` (to see your own group memberships).
- *Reasoning process:* group permission only applies to you if you're actually *in* that group (Section 3).
- *Root cause:* group mismatch — the permission bit is fine, but it doesn't apply to your identity.
- *Fix:* (context-dependent; this lesson does not teach how to add users to groups, since that's outside its scope) — recognize this as the actual cause rather than assuming the permission bits themselves are wrong.
- *Prevention:* always check `groups`/`id` before concluding a "group-readable" file should be accessible to you.

**Scenario 7 — Incorrect owner**
- *Situation:* a file was created by a different identity than expected (e.g. created by a service, now needs to be edited by a developer).
- *Symptom:* the expected owner category's permissions don't apply because the actual owner is someone/something else.
- *Diagnostic commands:* `ls -l` or `stat` to see the actual recorded owner.
- *Reasoning process:* compare the file's actual owner (from `ls -l`/`stat`) against your own identity (`whoami`/`id`).
- *Root cause:* an ownership mismatch — the file's owner category simply isn't you.
- *Fix:* (ownership changes, via `chown`, are outside this lesson's scope) — recognize the mismatch as the actual cause.
- *Prevention:* check actual recorded ownership before assuming a permission bit is "wrong."

**Scenario 8 — Incorrect group**
- *Situation:* similar to Scenario 7, but for the group association rather than the owner.
- *Symptom:* group permissions don't apply because the file's associated group isn't one you belong to, or isn't the group you expected.
- *Diagnostic commands:* `ls -l`/`stat` (file's group); `groups` (your groups).
- *Reasoning process:* same comparison as Scenario 6/7, focused on group specifically.
- *Root cause:* group mismatch at the file level.
- *Fix:* outside this lesson's scope to change; recognize the cause correctly.
- *Prevention:* same as Scenario 6.

**Scenario 9 — Permissions accidentally changed**
- *Situation:* something that used to work now fails, with no obvious code or content change.
- *Symptom:* a sudden `Permission denied` on something previously fine.
- *Diagnostic commands:* `ls -l`/`stat`, compared against what you remember (or expect) the permissions to have been.
- *Reasoning process:* consider whether a recent `chmod` (by you, a script, or a tool) might have altered this file's or a parent directory's permissions.
- *Root cause:* an unintended permission change, possibly from an overly broad `chmod` run earlier.
- *Fix:* restore the intended permission explicitly.
- *Prevention:* be deliberate and specific with `chmod` — prefer targeted symbolic changes over broad recursive ones when only one thing actually needs to change.

**Scenario 10 — Developer can access a file but service cannot**
- *Situation:* you can `cat` a file just fine; a running service reports it cannot.
- *Symptom:* the service logs a permission error for a file you've just confirmed works for you.
- *Diagnostic commands:* determine the service's actual running identity; `ls -l` the file, checking against that identity rather than your own.
- *Reasoning process:* your own successful manual test only proves the file works for *your* identity — the service is very likely running as a different one (Section 24).
- *Root cause:* an identity mismatch between your interactive shell and the service's actual runtime identity.
- *Fix:* grant the correct permission to the category the service's identity actually falls into.
- *Prevention:* never treat "it works when I test it manually" as proof it will work for a service running under a different identity.

**Scenario 11 — Model/checkpoint exists but Python service cannot read it**
- *Situation:* a model file is clearly present on disk; a Python inference service fails to load it.
- *Symptom:* a `PermissionError` (or similar) inside the Python service's logs.
- *Diagnostic commands:* `ls -l` on the model file and its containing directories; confirm the service's running identity.
- *Reasoning process:* directly combining Scenario 4, Scenario 5, and Scenario 10's reasoning — check both the file's own permissions *and* every containing directory's traversal permission, against the *service's* identity specifically, not your own.
- *Root cause:* usually either the file's read permission or a containing directory's execute permission doesn't extend to the service's identity.
- *Fix:* grant the correct permission to whichever category the service's identity falls under.
- *Prevention:* when deploying a service that needs to read specific artifacts, verify access using that service's actual identity, not just your own developer account (Section 24's central lesson).

**Scenario 12 — Removing file write permission does not prevent deletion**
- *Situation:* you remove write permission from a file, expecting this to protect it from being deleted, and it still gets deleted.
- *Symptom:* `rm` succeeds despite the file having no write permission at all.
- *Diagnostic commands:* `ls -l` on the file's *containing directory*.
- *Reasoning process:* recall Section 16's direct correction — deletion depends on the *directory's* permissions (write + search/execute), not the file's own.
- *Root cause:* a misunderstanding of what file write permission actually protects against.
- *Fix:* there is no fix to "make" — this is expected behavior; if deletion protection is genuinely needed, the relevant permission to examine is the *containing directory's*, not the file's.
- *Prevention:* internalize Section 16's distinction permanently — it is one of the most consequential misconceptions in this entire lesson.

**Scenario 13 — Script works with `bash script.sh` but fails with `./script.sh`**
- *Situation:* exactly Lesson 08's Section 22, Scenario 3 and Scenario 1 combined.
- *Symptom:* `bash script.sh` runs fine; `./script.sh` reports `Permission denied`.
- *Diagnostic commands:* `ls -l script.sh`.
- *Reasoning process:* Section 15's direct explanation — only `./script.sh` requires the file's own execute bit.
- *Root cause:* missing execute permission on the script file.
- *Fix:* `chmod +x script.sh`.
- *Prevention:* remember which of the two execution forms actually depends on this bit.

**Scenario 14 — Permissions differ between Windows and WSL2**
- *Situation:* a file accessed from within WSL2's Linux environment behaves differently than the same file accessed from Windows directly (particularly across the `/mnt/c/...` boundary).
- *Symptom:* unexpected permission behavior specifically when crossing between the two filesystems.
- *Diagnostic commands:* `ls -l` from within WSL2, comparing behavior for a file that lives natively in the Linux filesystem versus one that lives on the Windows side.
- *Reasoning process:* recall Section 26 — WSL2's Linux environment follows this lesson's model internally, but the Windows/Linux interoperability boundary is a genuinely different situation, not guaranteed to behave identically.
- *Root cause:* the file in question lives across (or was accessed across) the WSL2/Windows filesystem boundary, where this lesson's pure Linux permission model doesn't apply as cleanly.
- *Fix:* prefer keeping files you're actively developing scripts against within the native Linux filesystem inside WSL2, when this lesson's exact model needs to apply cleanly.
- *Prevention:* be aware this boundary exists; don't assume perfect equivalence across it.

**Scenario 15 — Recursive permission change produces unexpected access**
- *Situation:* a broad, recursive `chmod` (applied to a whole directory tree at once) results in some files or subdirectories ending up with unintended permissions.
- *Symptom:* files that should have stayed private are now more broadly accessible than intended (or vice versa), after one recursive command.
- *Diagnostic commands:* `ls -l` (or a broader recursive listing) across the affected tree, compared against what was actually intended.
- *Reasoning process:* a single recursive permission value applied uniformly to everything underneath a directory does not distinguish between files that should be executable (like scripts) and files that shouldn't be (like plain data) — one blanket value is rarely correct for every object in a mixed tree.
- *Root cause:* an overly broad, insufficiently targeted permission change.
- *Fix:* re-apply permissions deliberately, ideally per-object or per-category, rather than one uniform recursive value across a mixed directory tree.
- *Prevention:* treat recursive permission changes with real caution, and prefer narrow, deliberate `chmod` operations (Scenario 9's prevention note applies equally here).

---

## 22. Security and Safety

Permissions are a genuinely important security mechanism — but a required, direct clarification governs everything in this section: **they are one real, load-bearing mechanism, not the entirety of security.**

**Least privilege**, introduced fully in Section 25: give a user or process only the access it actually needs — nothing more.

**Why this matters in practice:**

- **Avoiding unnecessary access** — a process that can read far more than it needs has a correspondingly larger opportunity to do damage, whether through a bug or through misuse.
- **Protecting sensitive files** — restrictive permissions (like `600`, Section 8) are a first, meaningful line of defense for files that shouldn't be broadly readable.
- **Protecting model artifacts** — a production model file, once trained and validated, generally shouldn't be casually writable by every process that happens to run nearby.
- **Protecting configuration** — configuration files sometimes contain sensitive values (Lesson 07, Section 17's exact warning); restricting who can read them reduces exposure.
- **Reducing accidental modification** — permissions that are more restrictive than "everyone can write" reduce the chance of an unrelated process or careless command accidentally corrupting something important.
- **Service-account access** — a production service ideally has access to exactly what it needs, and nothing beyond that (Section 24 expands on this directly).

**Why `chmod 777 ...` is dangerous, stated explicitly:**

```bash
chmod 777 ...
```

This grants **full read, write, and execute access to absolutely everyone** — owner, group, and others alike. It is sometimes reached for as a quick way to "make a permission error go away," but doing so **removes essentially all access control from that object**. Any process or user on the system can now read it, modify it, or (for a script/program) run it. **This lesson does not encourage broad permissions as a troubleshooting shortcut, under any circumstance.** "Make everything writable/readable" trades a specific, diagnosable problem for a much larger, harder-to-reason-about one — it doesn't actually fix the underlying cause (an identity mismatch, a directory traversal issue, a genuine ownership question), it just removes the system's ability to say no to *anyone*, including processes and users who have no legitimate reason to touch the file at all.

**This lesson intentionally does not teach:**

- ACLs (Access Control Lists)
- SELinux
- AppArmor
- Linux capabilities
- namespaces
- cgroups
- Kubernetes RBAC
- cloud IAM

These are real, more advanced access-control and isolation mechanisms that exist beyond the basic owner/group/others model taught here — mentioned by name only so you know they exist and belong to later, more advanced study, not as something to learn now.

---

## 23. Real-World Software Engineering Use Cases

| Use case | Problem | Permission concern | Failure mode |
|---|---|---|---|
| **Multi-user Linux systems** | Several people share one machine | Each user's files need protection from others by default | One user accidentally reads/edits another's files |
| **Development environments** | A team shares project files | Some files need to be broadly writable, others not | A teammate accidentally overwrites something they shouldn't have touched |
| **Application deployments** | Deployed code runs under a specific identity | That identity needs exactly the access the app requires | The app fails to start because it can't read its own files |
| **Service accounts** | A running service isn't "a person" | It has its own identity, with its own scoped access | A service that was accidentally granted too much (or too little) access |
| **Shared directories** | Multiple users/services need access to common data | Group permissions need to be set up deliberately | Access denied for a legitimate group member, or overly broad access for everyone |
| **Logs** | Logs may contain sensitive operational detail | Read access should often be limited | Sensitive log content exposed more broadly than intended |
| **Configuration files** | May contain sensitive settings (Lesson 07) | Restricted read access is often appropriate | A configuration value leaked to an unintended reader |
| **Build artifacts** | Generated during a build process | Usually need to be readable/executable by whoever runs them | A build artifact that can't be executed due to a missing `x` bit |
| **Executable scripts** | Meant to be run, sometimes by others | Need `x` for the intended runner's category | `Permission denied` on `./script.sh` (Section 21, Scenario 3) |
| **Temporary files** | Created and discarded during processing | Usually only need to be accessible to their creator | A temp file left with overly broad access by mistake |
| **Backup files** | Copies of potentially sensitive data | Often need protection at least as strict as the original | A backup that's more broadly readable than the file it was backing up |

---

## 24. Applied AI Engineering Use Cases

**This section is essential.**

### Dataset access

```text
dataset
   ↓
filesystem
   ↓
process identity
   ↓
permission check
   ↓
training process
```

A training process needs read access to the dataset files, and traversal (`x`) access to every directory in the path leading to them — exactly Section 6 and Section 21, Scenario 11's model, applied specifically to training data.

### Model/checkpoint access

**Why a Python/ML process might fail to load a model even when the model file exists:** exactly Section 14 and Section 21, Scenario 11 — the process's specific identity may lack read permission on the file, or execute (traversal) permission on a directory somewhere in its path, even though the file is plainly present when *you* look at it with your own identity.

### Evaluation artifacts

Protecting evaluation outputs from unintended modification means deliberately choosing permissions (perhaps closer to `644` or even more restrictive, depending on who legitimately needs to write vs. only read) so that a result, once produced, isn't accidentally overwritten by an unrelated process before it's been reviewed.

### Configuration

Configuration files may require restricted access specifically because, as Lesson 07 established, configuration sometimes carries sensitive values — restrictive permissions are one part (not the whole solution, per Lesson 07's own explicit warning) of reducing accidental exposure.

### AI service accounts

**Production AI services may run under identities different from developers** — exactly Section 21, Scenario 10's lesson, applied specifically to AI infrastructure: the fact that *you* can read a model file or dataset from your own developer account proves nothing about whether the actual running inference or training service — under its own, separate identity — can.

### Shared model/data directories

Groups (Section 3) matter here directly: a shared dataset or model-artifact directory used by multiple team members or services benefits from a deliberately designed group-permission setup, rather than either "only one person can touch it" or "everyone can do anything" (Section 22's `777` warning applies exactly here).

### Temporary artifacts

Generated files (intermediate processing outputs, scratch data) still deserve a deliberate, safe access boundary — not necessarily broad, and not necessarily identical to the original data's own permission scheme.

**Connecting to the layers ahead:** Python services, ML pipelines, LLM applications, evaluation workflows, agent workflows, and production AI services all inherit this exact permission model underneath them — none of them are exempt from "does this specific process's identity actually have access to this specific file?" This lesson does not teach cloud IAM, Kubernetes RBAC, containers, or advanced platform security — those are separate, later stages that build on top of (rather than replace) the foundational model taught here.

---

## 25. Permissions and Least Privilege

**The principle, stated as simply as possible:**

```text
Give a process/user
only the access
it actually needs.
```

**Trade-offs:**

**Too restrictive:**
- Failures — legitimate operations get denied.
- Operational friction — more time spent granting exactly the right access, repeatedly.
- Debugging difficulty — distinguishing "genuinely broken" from "correctly denied, but inconveniently so" takes real care.

**Too permissive:**
- Security risk — anything (or anyone) that shouldn't have access, does.
- Accidental modification — more things are able to change something they shouldn't.
- Data exposure — sensitive content reachable by more identities than intended.
- Larger blast radius — if something *does* go wrong (a bug, a compromised process, a mistake), the amount of damage it can potentially cause scales with how much access it had.

**Connecting to production AI systems:** a training pipeline, an inference service, and an evaluation job likely don't all need identical access to the same files — least privilege means deliberately scoping each one's access to exactly what *that specific process* requires, rather than granting broad access "just in case," which is precisely the instinct Section 22's `chmod 777` warning exists to counter.

---

## 26. Cross-Platform Coverage

**Primary environment for this lesson:** Linux/Ubuntu with Bash. WSL2 provides a Linux environment where the Linux permission model applies to its native Linux filesystem; files accessed through Windows-mounted paths such as `/mnt/c` can behave differently because of Windows/WSL filesystem interoperability.

**Git Bash:** provides a Bash-like command-line environment on Windows, but **filesystem permission behavior may differ from native Linux** — Windows' underlying filesystem doesn't natively implement the exact owner/group/others `rwx` model taught in this lesson, so `chmod`/`ls -l` output inside Git Bash can behave in ways that don't map perfectly onto genuine Linux semantics.

**PowerShell:** has a **genuinely different permission/security model and command syntax** entirely — this lesson does not teach Windows ACLs (Access Control Lists) in depth; only notes that PowerShell's approach to file access control is a different system, not a re-skinned version of this lesson's `rwx` model.

**WSL2:** Linux permissions inside WSL2 **apply to its native Linux filesystem** as taught throughout this lesson — but **Windows filesystem interoperability can introduce differences** (Section 21, Scenario 14) specifically when crossing between WSL2's own Linux filesystem and the Windows filesystem it can also access (e.g. `/mnt/c/...` paths). **This lesson does not claim WSL2 is identical to native Linux in every filesystem situation** — only that its own Linux-side filesystem follows this lesson's model faithfully.

---

## 27. Internal Mechanics

```text
Process
   ↓
requests filesystem operation
   ↓
OS/kernel
   ↓
identify process credentials
   ↓
identify target object
   ↓
evaluate ownership/group/permission information
   ↓
access decision
   ↓
allow or deny
```

Step by step, at a beginner-appropriate level:

1. **A process requests a filesystem operation** — e.g. "open this file for reading" — the same kind of request underlying every command from Lessons 02–08.
2. **The OS/kernel receives this request** — via a system call (mentioned here only conceptually, exactly as prior lessons have consistently done — not re-taught).
3. **The kernel identifies the process's credentials** — its UID and group memberships (Section 3), attached to the process itself.
4. **The kernel identifies the target filesystem object** — resolving the given path (Lesson 01's path-resolution model) to the actual file/directory and its stored metadata.
5. **The kernel evaluates ownership/group/permission information** — comparing the process's credentials against the object's owner, group, and permission bits (Section 13's flow, restated at this internal level).
6. **An access decision is produced** — allow or deny, for the specific requested operation (read/write/execute).
7. **The operation proceeds, or is refused** — and, if refused, the calling process (and, ultimately, whatever program or script triggered it) receives an error reflecting that refusal — exactly the `PermissionError` and `Permission denied` outcomes seen throughout Sections 14 and 21.

**Connecting to already-familiar concepts:** system calls (the request mechanism), the filesystem (where the object and its metadata live), the process (the thing making the request, with an identity), user/group identity (Section 3, what's actually being compared), file descriptors (Lesson 06 — what a process holds once access has actually been granted), and Python application behavior (Section 14 — where a denied access ultimately surfaces as a visible, familiar error). This lesson does not teach kernel source code or advanced VFS (virtual filesystem) internals — this conceptual flow is the intended depth.

---

## 28. Testing Permissions

**The methodology, stated simply:** a permission configuration should be **tested against realistic identities and operations** — not assumed correct just because it "looks reasonable" when you glance at `ls -l`.

Safe conceptual test cases to actually try (using your own disposable files, per Section 17):

```text
Can owner read?
Can owner write?
Can owner execute?
Can group read?
Can group write?
Can others read?
Can process enter directory?
Can service read model artifact?
```

**Testing from evidence rather than assumption, stated directly:** the correct way to know whether a given identity can access a given file is to actually check — with `ls -l`/`stat` for the permission bits, and `whoami`/`id`/`groups` for the identity — and reason through Section 13's flow explicitly, rather than assuming "it's probably fine" or "it's probably broken." Every debugging scenario in Section 21 models exactly this evidence-first habit.

**Connecting to production engineering:** this is the same underlying principle Lesson 08 (Section 26) applied to shell scripts — a system (here, a permission configuration) should be **tested**, not merely set up once and trusted. Before relying on a permission setup for anything real, actually verify it answers each of the questions above the way you intend, ideally using the *actual* identity (a service account, not just your own developer login) that will really be making the request (Section 21, Scenario 10 and Scenario 11).

---

## 29. Trade-offs

### More restrictive permissions

**Advantages:**
- Stronger isolation between users/processes.
- Lower chance of accidental access by something that shouldn't have it.
- Reduced exposure of sensitive content.

**Disadvantages:**
- Operational friction — more explicit permission-granting needed for legitimate access.
- Harder debugging — more potential points where a legitimate operation gets denied.
- Possible application failures if a genuinely necessary access path was under-provisioned.

### More permissive permissions

**Advantages:**
- Easier collaboration — fewer access failures for legitimate users.
- Fewer access failures generally, in the short term.

**Disadvantages:**
- Larger blast radius if something goes wrong (Section 25).
- Increased security risk — more identities than necessary can act on the object.
- Accidental modification — more opportunities for an unrelated process or user to change something unintentionally.

**Why production systems generally seek *appropriate* access rather than *maximum* access:** the goal is never "as much access as possible, to avoid ever seeing a permission error" — that trades a manageable, diagnosable problem for an unmanageable, larger-consequence one (exactly Section 22's `777` warning). The goal is access that's **just right** for what each specific identity actually, legitimately needs to do — which is precisely what least privilege (Section 25) describes.

---

## 30. Mini-Project — Secure Command-Line Workspace

**Objective:** build a small, disposable workspace that demonstrates deliberate, reasoned permission design — not just "make it work by any means," but "make it work with exactly the access it needs, and be able to explain why."

**Requirements:** no Git, no cloud, no Docker, no Kubernetes, no external APIs, no production credentials, no system-wide changes, no `sudo`.

**Conceptual design:** you'll create a small workspace containing one ordinary data file, one script, and one deliberately restricted file — inspect and set permissions on each deliberately, test that the resulting access matches your intent, deliberately break one thing, diagnose it using this lesson's methodology, and restore it.

**Directory structure (to be created by you, manually — not created automatically by this lesson):**

```text
secure-workspace/
├── data/
│   └── notes.txt
├── scripts/
│   └── report.sh
└── private/
    └── restricted.txt
```

**Implementation steps:**

1. Create the directory structure above, using `mkdir -p` (Lesson 02).
2. Create `data/notes.txt` with a few harmless lines of text.
3. Create `scripts/report.sh` with a simple shebang and one `echo` line (Lesson 08).
4. Create `private/restricted.txt` with a harmless placeholder line (never a real secret, per this lesson's safety requirements).
5. Inspect every file's default permissions with `ls -l`.
6. Identify your own identity (`whoami`, `id`, `groups`) before making any changes.

**Permission plan (design this deliberately, then apply it):**

| File | Intended permission | Why |
|---|---|---|
| `data/notes.txt` | `644` | Ordinary data — owner can edit, readable by others if needed |
| `scripts/report.sh` | `755` | Meant to be run directly (`./report.sh`); owner can also edit it |
| `private/restricted.txt` | `600` | Meant to be accessible only to the owner |

7. Apply the permission plan using `chmod` (numeric or symbolic — your choice, but be able to explain which form you used and why).
8. Make `scripts/report.sh` executable and confirm it, run both as `bash scripts/report.sh` and as `./scripts/report.sh` (Section 15).

**Test cases:**
- Confirm `data/notes.txt` is readable and editable by you.
- Confirm `scripts/report.sh` runs successfully both ways (`bash` and `./`).
- Confirm `private/restricted.txt` is readable by you but reflects `600` in `ls -l`.

**Failure scenarios / debugging tasks (deliberately induce, then fix):**

9. Remove execute permission from `scripts/report.sh` (`chmod -x scripts/report.sh`), confirm `./scripts/report.sh` now fails exactly as Section 21's Scenario 3 predicts, diagnose it using `ls -l`, and restore the correct permission.
10. Remove execute (traversal) permission from the `private/` directory itself (not the file inside it), confirm that `cat private/restricted.txt` now fails even though the file's own permissions never changed, correctly diagnose this as a *directory* traversal problem (Section 21, Scenario 5), and restore it.

**Document your permission design:** write a short summary (a few sentences) explaining, for each of the three files, why you chose the permission you did — connecting back to what each file is actually for and who legitimately needs what kind of access.

**Expected behavior:** by the end, every file has the permission from your design table, `scripts/report.sh` runs correctly both ways, and you can explain — from evidence, not assumption (Section 28) — exactly why each permission choice is appropriate for that file's purpose.

**Completion checklist:**
- [ ] Created the three-file workspace structure manually.
- [ ] Inspected default permissions with `ls -l` before making changes.
- [ ] Identified your own identity with `whoami`/`id`/`groups`.
- [ ] Applied the permission plan deliberately (`644`/`755`/`600`).
- [ ] Confirmed `scripts/report.sh` runs both as `bash ...` and `./...`.
- [ ] Deliberately broke and correctly diagnosed the missing-execute-permission scenario.
- [ ] Deliberately broke and correctly diagnosed the directory-traversal scenario.
- [ ] Restored all permissions to the intended design.
- [ ] Documented the reasoning behind each permission choice.
- [ ] Cleaned up the disposable workspace afterward.

**Extension challenges (optional, staying within this lesson's scope):** add a second, disposable "teammate" scenario by reasoning (in writing, not necessarily executing) about what group permission you'd choose if a second user needed read-only access to `data/notes.txt` but no access at all to `private/restricted.txt`.

---

## 31. Exercises

All Level 3–5 practical work should be done inside your own disposable directory, using only harmless, learner-created files. Never modify real project or system files.

### Level 1 — Recognition

1. In `id`'s output, which part represents your primary group?
2. In `-rwxr-xr--`, which three characters represent the group's permissions?
3. What numeric value corresponds to `rwx`?
4. What numeric value corresponds to `r--`?
5. Which command lists your current username?
6. Which command lists the groups you belong to?
7. In `chmod g-w file.txt`, what does `g` refer to?
8. Which permission letter, on a directory, governs whether you can traverse into it?

### Level 2 — Understanding

1. Explain the difference between what `w` means for a file versus what it means for a directory.
2. Explain why a file can be perfectly readable and still inaccessible, due to a directory permission elsewhere in its path.
3. Predict what happens if a directory has `r-x` but not `w`, when you try to create a new file inside it.
4. Explain why removing a file's own write permission does not necessarily prevent it from being deleted.
5. Explain the difference between symbolic and numeric `chmod` forms, and when you'd prefer one over the other.
6. Explain why a Python service might receive a `PermissionError` even though the target file clearly exists.
7. Explain why `chmod 777` is not an appropriate general-purpose fix for a permission error.
8. Given `-rw-r--r--`, explain exactly what each of the three permission groups is allowed to do.

### Level 3 — Application

Perform each of these in your own disposable directory.

1. Create a file and inspect its default permissions with `ls -l`.
2. Use `stat` on the same file and compare its output to `ls -l`.
3. Run `whoami`, `id`, and `groups`, and note your own identity and group memberships.
4. Change the file's permissions to `600` using numeric `chmod`, and confirm the change with `ls -l`.
5. Change one specific bit using symbolic `chmod` (e.g. `chmod g+r`), and confirm the change.
6. Create a script, confirm it fails with `./script.sh` before being made executable, then fix it with `chmod +x` and confirm it now runs.
7. Create a directory, remove its execute permission, and confirm that accessing a file inside it fails even though the file itself was never touched.
8. Restore every permission you changed in this exercise set back to a safe, sensible state, and clean up your disposable directory.

### Level 4 — Debugging

For each scenario, state the likely cause and the safe fix — explain your reasoning, don't just guess a command.

1. `cat` reports "Permission denied" on a file you're sure you created. What would you check first?
2. A redirection (`>`) into an existing file fails with a permission error. What bit is most likely missing?
3. `./script.sh` fails, but `bash script.sh` works fine on the exact same file. What's the fix?
4. A file's group permissions show `r--`, but you still can't read it as a non-owner. What identity fact would you check?
5. You remove a file's write permission expecting to protect it from deletion, and it still gets deleted. What misconception does this reveal?
6. A directory shows `r-xr-xr-x`, and a colleague reports being unable to see what's inside it with `ls`. What specific bit would you check?
7. A Python service reports `PermissionError` on a model file that you, personally, can open without any problem. What's the most likely explanation?
8. After a recursive `chmod` on a whole project directory, some files that should have stayed private are now broadly readable. What would you do differently next time?

### Level 5 — Integration

These combine permissions with earlier Module 0.3 skills (file operations, shell scripts, process/identity reasoning). Perform each in your own disposable directory.

1. Write a short shell script (Lesson 08) that checks whether a given file argument is readable, using its own logic (an `if` combined with an appropriate test), before attempting to `cat` it — and test it against both an accessible and a deliberately inaccessible file.
2. Create a directory structure with a script inside it, deliberately remove execute permission from the *directory* (not the script), and confirm and explain why the script now fails to run even after separately confirming the script file itself is still executable.
3. Reason through (in writing) exactly which identity a background/service process would need appropriate permissions for, if you wanted it to read a dataset file that only you currently have access to — describe the check you'd want to perform before deploying such a service.
4. Given a simulated "AI artifact access problem" — a model file exists, permissions show `rw-------` (owner-only), and a service is failing to load it — diagnose, step by step, using this lesson's methodology, what's most likely wrong and what you'd check to confirm it.
5. Design (on paper, not necessarily executed) a safe permission configuration for a small shared workspace containing one script others should be able to run but not edit, and one data file only you should be able to modify — state the exact `chmod` commands you'd use and justify each one.

---

## 32. Review

**Users and identity:** every user has a UID; every process runs as some user, with associated group memberships (GIDs). `whoami`, `id`, and `groups` inspect this identity directly.

**Owner/group/others:** every file has exactly one owner and one associated group; everyone else falls under "others." `ls -l`'s permission string encodes owner, group, and others permissions, in that order, after the file-type indicator.

**`rwx`:** for files — read contents, modify contents, run as a program. For directories — list entries, modify entries (create/delete/rename generally need `w` and `x`), traverse into the directory. The meanings genuinely differ between files and directories.

**Numeric permissions:** `r=4, w=2, x=1`, summed per category; `644`, `755`, `700`, `600` are common, recognizable — not universal — patterns.

**Symbolic permissions:** `u`/`g`/`o`/`a`, combined with `+`/`-`/`=`, for targeted single-bit changes.

**`chmod`:** changes permission bits only, never ownership.

**`stat`:** more detailed metadata than `ls -l`'s convenient overview.

**Permission-check flow:** identity → target object → owner/group/others bits → requested operation → allow/deny — the backbone of every debugging scenario in this lesson.

**Least privilege:** grant only the access actually needed; both over-restriction and over-permission carry real costs.

**Debugging:** always check identity (`whoami`/`id`/`groups`) and the target's actual permissions (`ls -l`/`stat`) before concluding anything — never guess.

**Shell-script relationship:** `./script.sh` requires the file's own execute bit; `bash script.sh` does not.

**Process relationship:** a permission decision depends on the identity actually making the request — which is very often not the same as your own interactive shell's identity, especially for a running service.

**AI Engineering relevance:** exactly the same model governs whether a training job can read a dataset, whether an inference service can load a model, and whether an evaluation job can write its results — permission failures in these contexts are not mysterious; they're the same, fully diagnosable pattern taught throughout this lesson.

### Self-assessment checklist

- [ ] I can decode `755`.
- [ ] I can explain directory execute permission.
- [ ] I can inspect ownership with `ls -l` and `stat`.
- [ ] I can diagnose a permission failure using identity + target-permission evidence, rather than guessing.
- [ ] I can safely change permissions on learner-created files, using both numeric and symbolic `chmod`.
- [ ] I can explain why a Python service may receive a `PermissionError` even when the file plainly exists.
- [ ] I can reason about service-account access — why "it works for me" doesn't prove "it will work for the service."

---

## 33. Interview Questions

1. **What are Linux file permissions?** Rules, attached to a filesystem object, describing what its owner, its associated group, and everyone else are allowed to do with it (read, write, execute).
2. **What do `r`, `w`, and `x` mean?** For files: read contents, modify contents, execute as a program. For directories: list entries, modify entries (create/delete/rename generally need `w` and `x`), traverse into the directory — the meanings differ between the two.
3. **What is the difference between file and directory permissions?** The same three letters govern structurally different capabilities depending on whether the target is a file or a directory (Section 6) — most notably, directory `x` governs traversal, not "running" the directory.
4. **What does `644` mean?** Owner can read and write; group and others can only read.
5. **What does `755` mean?** Owner can read, write, and execute; group and others can read and execute, but not modify.
6. **What is the difference between UID and GID?** UID identifies a specific user; GID identifies a specific group — a user can belong to multiple groups, each with its own GID.
7. **What are owner, group, and others?** The three categories a file's permissions are organized into: the specific user who owns the file, the specific group associated with it, and everyone else.
8. **What does `chmod` do?** Changes a filesystem object's permission bits — never its ownership.
9. **What's the difference between symbolic and numeric permissions?** Numeric form (e.g. `644`) sets all nine permission bits at once; symbolic form (e.g. `u+x`) adjusts one specific bit for one specific category, leaving the rest unchanged.
10. **Why can a user read a file but fail to access its directory?** Because directory execute (traversal) permission gates the ability to reach anything inside it at all — a missing `x` on any directory in the path blocks access regardless of the target file's own permissions (Section 6).
11. **Why might `./script.sh` fail while `bash script.sh` works?** `./script.sh` runs the file directly and requires its own execute permission; `bash script.sh` reads the file's contents as input to an already-runnable interpreter and needs no such permission on the file itself.
12. **Why is `chmod 777` generally a poor production solution?** It removes essentially all access control from the object, granting full read/write/execute to everyone — trading a specific, diagnosable problem for a much larger, harder-to-reason-about security and reliability risk, without addressing the actual underlying cause.
13. **Why might a Python service receive a `PermissionError`?** Because the specific identity the service runs as lacks the required permission on the target file or a directory in its path — even though the file exists and is accessible to other identities, including the developer's own.
14. **Why are groups useful in production systems?** They let access be granted to a whole team or role at once, without granting it to literally everyone (`others`) or having to manage each individual user's access separately.

---

## 34. Architecture / Engineering Questions

1. **How would you design permissions for a production AI service?** Identify exactly what the service's own identity needs to read/write (model files, datasets, config, logs, output artifacts), grant only that access under its own dedicated identity, and avoid running it under a broad, general-purpose account with unrelated access.
2. **How would you protect model artifacts from accidental modification?** Use restrictive write permissions (readable broadly if needed, but writable only by whatever process is responsible for producing/updating it), so unrelated processes can't accidentally overwrite a validated artifact.
3. **How should a service account access shared datasets?** Through deliberately designed group membership and directory/file permissions scoped to exactly what that account needs — read access to the data it consumes, without broader access to unrelated files in the same shared location.
4. **How would you debug a production AI service that cannot read a model file?** Determine the service's actual running identity (not your own developer identity); check the model file's own permissions and every directory in its path for traversal access, from that identity's perspective specifically (Section 21, Scenario 11).
5. **How does least privilege reduce blast radius?** By limiting what a given identity can access in the first place, a bug, mistake, or compromise involving that identity can only affect what it actually had access to — not everything on the system.
6. **When would restrictive permissions become an operational problem?** When they're set more narrowly than what a legitimate process/user actually needs, causing real, valid operations to fail — the "too restrictive" side of the trade-off in Section 29, requiring careful, deliberate scoping rather than either extreme.
7. **How should developers and production services differ in filesystem access?** A developer's interactive account often has broad access across a shared development environment for convenience; a production service should run under its own, narrowly scoped identity with access limited to exactly what that specific service needs — the two should not be assumed equivalent (Section 21, Scenario 10).

---

## 35. Production Application

**Where permissions become important in production:**

- **Application services** — need exactly the access required to start and run correctly, under their own identity.
- **Model files** — need to be readable by whatever service loads them, and appropriately protected from unintended modification.
- **Datasets** — need to be readable by whatever pipeline/service consumes them, scoped to the identities that legitimately need access.
- **Configuration** — often needs restricted read access, given the sensitivity concerns from Lesson 07.
- **Logs** — may need restricted access depending on what operational detail they contain.
- **Generated artifacts** — need to be writable by whatever produced them, and appropriately protected afterward.
- **Temporary directories** — need a sensible, scoped access boundary, not automatically broad access.
- **Service accounts** — the identity layer underneath all of the above; scoped deliberately, per Section 25's least-privilege principle.
- **Shared resources** — need deliberate group-permission design, rather than either "one person only" or "everyone."
- **Deployment environments** — the specific identity a deployed application runs under is itself a permission decision, made deliberately, not left to default.

**Example conceptual flow:**

```text
AI Service
    ↓
runs as a service identity
    ↓
reads model artifact
    ↓
reads configuration
    ↓
writes logs/artifacts
    ↓
filesystem permission checks
```

**How an incorrect permission can become:**

- **Application startup failure** — the service can't even begin, because it can't read a file it needs immediately.
- **Model loading failure** — exactly Section 21, Scenario 11, at production scale.
- **Data pipeline failure** — a step in the pipeline can't read its expected input.
- **Artifact-writing failure** — a step produces a result but can't actually save it anywhere.
- **Operational incident** — any of the above, discovered in production rather than caught earlier through deliberate testing (Section 28).

**Connecting to the roadmap's production engineering principles:**

```text
Requirements
→ Design
→ Implementation
→ Testing
→ Validation
→ Security
→ Reliability
→ Architecture Review
```

Permission design belongs squarely in **Design** (deciding, deliberately, what each identity needs) and **Testing**/**Validation** (actually confirming, with evidence, that the intended access works — and unintended access doesn't) — and it's a direct, concrete contributor to both **Security** and **Reliability**. This lesson does not teach advanced deployment or security infrastructure beyond this foundational model — those later stages build on top of exactly the reasoning taught here.

---

## 36. Applied AI Engineering Connection

```text
Filesystem
   ↓
Permissions
   ↓
Processes
   ↓
Python services
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

**Permissions are not merely Linux administration trivia.** They give an Applied AI Engineer a concrete, reliable way to reason about:

- **Who can access data** — which identities have legitimate read/write access to a given dataset or artifact.
- **Which process can read/write artifacts** — a training job, an inference service, and an evaluation job may each need genuinely different access.
- **Why services fail despite files existing** — the exact "exists ≠ accessible to this identity" lesson from Section 14, which recurs constantly in real production AI systems.
- **How to reduce accidental access** — deliberate, scoped permissions rather than defaulting to broad access "just in case."
- **How to reduce blast radius** — least privilege (Section 25), applied specifically to the identities running your AI systems.
- **How production identities differ from developer identities** — Section 21, Scenario 10's lesson, which is precisely why "it worked when I tested it" is not sufficient evidence that a production AI service will actually be able to do the same thing.

---

## 37. Relationship with Previous Lessons

**`02-file-operations.md`:** file operations (`cp`, `mv`, `rm`, `mkdir`) may require appropriate permissions to succeed — this lesson explained *why*, specifically connecting deletion/renaming to *directory* write permission (Section 16), a distinction Lesson 02 itself did not need to cover.

**`06-pipes-and-redirection.md`:** scripts/processes writing redirected output still interact with filesystem permissions exactly as any other write attempt would — a redirection target you lack write permission on fails for precisely the reasons in Section 21, Scenario 2.

**`07-environment-variables.md`:** environment configuration may point processes toward files/directories that they must actually be able to access — a correctly exported path (Lesson 07) is necessary but not sufficient; the process's identity must also have the appropriate permission on whatever that path points to.

**`08-shell-scripts.md`:** executable scripts depend on permissions when executed directly — Section 15 gave the precise reason `./script.sh` requires the file's own execute bit while `bash script.sh` does not, extending Lesson 08's brief mention into a full explanation.

None of these earlier lessons are re-taught here — this lesson only supplies the permission-layer explanation that each of them assumed or deferred.

---

## 38. Relationship with Module 0.2

This lesson connects directly to Module 0.2's OS-level foundation:

- **Users/processes** — Module 0.2 introduced processes as running programs with an identity; this lesson showed exactly how that identity is used in an access decision.
- **Filesystem** — Module 0.2 introduced the filesystem as where files/directories live; this lesson showed the access-control metadata attached to those same objects.
- **System calls** — Module 0.2's mechanism for a process to request something from the kernel; this lesson used it only conceptually (Section 27), as the vehicle for a permission-checked filesystem request.
- **File descriptors** — Module 0.2/Lesson 06's concept of what a process holds once access is granted; this lesson's "allow" outcome is precisely what makes a file descriptor obtainable in the first place.
- **Standard I/O** — Lesson 06's stdout/stderr model; a permission failure often surfaces as an error message on stderr, exactly as any other command failure would.
- **Shell** — the program that launches the processes whose identity this entire lesson has been reasoning about.
- **Process lifecycle** — Module 0.2's concept of a process's start-to-finish existence; permission checks happen at specific moments during that lifecycle (when an operation is actually attempted), not once, globally, at the start.

**Module 0.2 established the OS-level foundation; this Module 0.3 lesson teaches practical command-line interaction with permissions** — inspecting them (`ls -l`, `stat`, `whoami`, `id`, `groups`), changing them (`chmod`), and reasoning through failures (Sections 12, 13, 21) — built directly on top of that earlier conceptual foundation, without repeating it.

---

## 39. Relationship with Next Lesson

The next lesson is `10-command-line-tools-overview.md`, which will **integrate** the command-line tools and workflows from across this entire module — navigation, file operations, viewing, searching, text processing, pipes/redirection, environment variables, shell scripts, and permissions — into a broader, unifying perspective. This lesson does not teach that integration in depth; it only completes the last individual concept (permissions) that the next lesson will draw together with everything before it.

---

## 40. Scope Boundary

This lesson teaches only:

- what file permissions are, and why operating systems need access control
- users, groups, owners, others, UID, GID
- reading `ls -l` permission strings
- `r`/`w`/`x` for both files and directories, and how their meanings differ
- numeric permissions (`644`, `755`, `700`, `600`) and symbolic permissions (`u`/`g`/`o`/`a` with `+`/`-`/`=`)
- `chmod` (numeric and symbolic)
- `stat`, `whoami`, `id`, `groups`
- the permission-check flow, and its connection to processes and Module 0.2
- the relationship between permissions and shell scripts, and permissions and file operations
- least privilege, and why `chmod 777` is not a real fix
- basic, foundational cross-platform awareness (Bash/Linux/WSL2 primary; Git Bash and PowerShell noted, not taught)

This lesson deliberately does **not** deeply teach:

- ACLs (Access Control Lists)
- SELinux
- AppArmor
- Linux capabilities
- namespaces
- cgroups
- container permissions
- Kubernetes RBAC
- cloud IAM
- advanced authentication systems
- enterprise identity management
- advanced filesystem security
- encryption
- cryptographic access control
- advanced Windows ACLs
- advanced PowerShell security
- security policy frameworks

These may be mentioned as future topics (Section 22, Section 24, Section 26), but are not taught in depth here. This lesson is a foundational command-line permissions lesson, not a cybersecurity course.

---

_This lesson is complete. It covers file permissions — ownership, `rwx`, numeric and symbolic `chmod`, `stat`, and identity inspection — only. The remaining Module 0.3 topic (`10-command-line-tools-overview.md`) integrates this and every prior lesson into a broader perspective._
