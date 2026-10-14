# 08 — Permissions

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Module 0.2 — Operating System Fundamentals
**Concept(s) covered:** permissions, access control, owner/group/others, read/write/execute, ownership, numeric and symbolic permissions
**Status:** Not Started

---

## 1. What Is It?

**Connecting to what you already know.** [Filesystems](07-filesystems.md) explained that every file has metadata beyond its content — including permissions, mentioned there only briefly. This lesson explains that piece fully: exactly what permissions are, how they're structured, and how the operating system uses them to decide, every single time, whether a given request to access a file or directory should be allowed.

**Operating-system permissions.** Simple meaning: rules the operating system checks before letting anyone (or anything) read, write, or run a specific file or directory. Technical meaning: permissions are metadata, attached to a filesystem object (Concept 07), that specify which categories of users are allowed to perform which categories of operations on it, enforced by the kernel every time such an operation is requested.

**Access control.** Simple meaning: the general idea of deciding who's allowed to do what. Technical meaning: access control is the broader principle — of which file permissions are one specific, foundational implementation — of governing which entities (users, processes) may perform which operations on which resources.

**Why the operating system needs permissions at all.** Concept 01 established that the kernel manages shared resources on behalf of many programs, and Concept 03 established that many independent, sometimes-buggy processes routinely run on one machine at once. Persistent files (Concept 07) are exactly this kind of shared resource — many different users and processes can potentially reach the same file. Without some rule-based system governing who can do what to it, one user's or process's mistake, or malicious action, could freely read, corrupt, or delete another's data.

**What resources can be protected.** This lesson focuses on files and directories, because that's where permissions matter most directly for the Module 0.2 goal — understanding what a running Python service is doing at the OS level. But the underlying access-control principle also applies more broadly to other OS-managed resources (devices, and others this lesson does not enumerate) — this lesson deliberately stays focused on the file/directory case.

**Why permissions are especially important for files and directories.** Files and directories are the primary way persistent data is shared and organized on a system (Concept 07) — configuration, datasets, code, logs, and model artifacts are all files. Getting file-level access control right is foundational to nearly every other kind of security or reliability guarantee a real system needs.

**A simple mental model** for this lesson:

```text
A process wants to read, write, or run a file/directory
     ↓
The operating system checks: who is asking, and what do the rules say?
     ↓
Permission is granted, or the request is denied
```

The rest of this lesson fills in exactly how "who is asking" and "what do the rules say" are actually represented and checked.

---

## 2. Why Does It Exist?

**The problems permissions solve, each with a concrete "why it matters":**

- **Preventing unauthorized access.** Without permissions, any user or process on a shared machine could read any other user's private files — permissions are what makes "this data belongs to me, not you" an enforceable fact, not just a polite assumption.
- **Preventing accidental modification.** Even well-intentioned users and programs make mistakes; marking a file as not writable by default protects it from being accidentally overwritten by something that had no business modifying it.
- **Protecting private data.** Configuration files, credentials, and personal data can be restricted to only the specific user (or process identity) that legitimately needs them.
- **Separating users.** On a machine used by more than one person (or running more than one service), permissions are what actually keeps each user's or service's files distinct and protected from the others, reinforcing the process-isolation principle Concept 03 introduced for memory, now applied to persistent storage.
- **Controlling application capabilities.** A process's ability to read, write, or execute specific files can be limited to only what it actually needs — a direct, concrete instance of restricting what a running program is allowed to do (Concept 01's broader theme).
- **Protecting system resources.** Critical system files (configuration, executables the OS itself depends on) are generally protected from being modified by ordinary users or processes, protecting the system's own stability.
- **Limiting the damage caused by a compromised or misconfigured process.** If a process is buggy, misconfigured, or has been compromised, restrictive permissions limit what damage it can actually do — it can only affect what its own identity is permitted to touch, not the entire filesystem.

**The principle underlying all of this: controlled access, not arbitrary syntax.** Permissions are not a set of arbitrary rules to memorize for their own sake — they exist to answer one consistent question, over and over, for every file and every request: **"is this specific entity allowed to perform this specific operation on this specific resource, right now?"** Every technical detail in this lesson — owners, groups, read/write/execute bits, numeric notation — is just the specific mechanism Linux uses to answer that one question precisely and consistently.

---

## 3. Why an AI Engineer Needs It

Nearly every real AI system depends on file access working correctly, and correctly denying access when it shouldn't succeed:

- **Python services reading configuration files** — a service that can't read its own config fails immediately at startup.
- **Applications loading datasets** — a data pipeline needs read access to dataset files, often owned by a different user or service account than the one running the pipeline.
- **Model/checkpoint files** — often deliberately made read-only, so a running inference service can load them but never accidentally (or maliciously) modify them.
- **Log files** — a service typically needs write access to its own log directory, but shouldn't need — and often shouldn't have — write access to much else.
- **Temporary files and cache directories** — usually need to be writable by the specific process using them, without being writable by every process on the machine.
- **Service accounts** — production services are frequently run under a dedicated, non-interactive user identity (rather than a personal login), specifically so their permissions can be scoped tightly to only what that service needs.
- **Deployment directories** — application code, once deployed, is often made read-only for the running service, to prevent a compromised or buggy process from modifying its own code.
- **Read-only model artifacts vs. writable application directories** — a single service commonly needs *different* permission levels for different directories it touches, all at once.
- **Secrets/configuration files** — credentials and API keys deserve the tightest possible permissions, readable only by the specific identity that legitimately needs them.

**Why permission knowledge helps debug production errors.** A huge share of real "my service won't start" or "my pipeline can't read this file" production incidents are permission problems, not application-logic bugs (Section 11 builds this skill directly). Recognizing the *shape* of a permission failure — and knowing how to investigate it methodically, rather than reaching for a blunt, unsafe fix — is a genuinely practical, everyday production skill.

**Distinguishing this lesson from advanced security engineering.** This lesson teaches the **foundational OS permission model** — the one every more advanced system (containers, cloud IAM, enterprise identity systems, and more) is ultimately built on top of. It deliberately does **not** teach those more advanced systems (see Section 15's closing scope note) — they belong to later stages of the roadmap, once this foundation is solid.

---

## 4. Beginner Explanation

**Analogy: a building with rooms, keys, and a front desk.**

```text
The building                       = the filesystem
A specific room                     = a specific file or directory
The building's front desk             = the operating system, checking every access request
A person's identity badge              = the user's identity (Section 5)
What that badge is allowed to do        = permissions
```

Imagine a building where every room has a rule posted on its door: who may enter and look around (**read**), who may enter and rearrange or add to what's inside (**write**), and who may actually operate the equipment inside the room (**execute** — the room contains something meant to be run or used, not just looked at). Every time someone tries to enter a room, the front desk checks: *who is this person, and what does this specific room's rule say they're allowed to do?* If the answer is "not this," the person is turned away — and if you've ever tried a door your badge doesn't open, you already have the everyday feeling this lesson calls **permission denied**.

**Four terms, introduced simply before the technical model:**

- **Owner.** The person "assigned" to the room — typically the room's rules are most generous for them.
- **Group.** A defined set of people (say, "everyone on the third floor") who might be given their own, separate level of access to a room, distinct from the owner and from everyone else.
- **Others.** Everyone else in the building, not the owner and not in the relevant group.
- **Access.** The general word for "being permitted to actually do something with a room" — read, write, or execute, depending on what the rule allows.

**Where this analogy is useful:** it captures the core shape — a specific identity, a specific resource, a specific rule about what that identity may do with that resource, checked every single time.

**Where this analogy must not replace the technical model, and breaks down:**

- A building's front desk can use human judgment ("I recognize you, go ahead"); the OS's permission check (Section 6) is entirely mechanical — for the traditional Unix permission-bit model taught in this lesson, the check uses the owner, group, and others permission categories (Section 5). Linux can also apply additional access-control mechanisms, which are outside this lesson's scope.
- "Read," "write," and "execute" mean something genuinely different for a *directory* than for a regular file (Section 5's dedicated "Files vs. Directories" section) — a detail this simple room analogy cannot capture, and that this lesson insists on getting exactly right.
- Real permissions are represented as precise, structured data — three-bit combinations, expressible in both symbolic and numeric form (Section 5) — not a vague, informal posted rule.

The rest of this lesson moves from this everyday intuition into the actual, precise Linux model — the analogy above is a starting point, not a substitute for the technical explanation that follows.

---

## 5. Technical Explanation

### Users and identities

**User.** Every person or service account on a Linux system has an identity the OS tracks.

**UID (User ID).** Simple meaning: the number the OS actually uses internally to represent a user's identity. Technical meaning: the UID is the numeric identifier the kernel uses to represent a user's identity; in the ordinary Unix/Linux permission model, the process's user and group credentials (including any supplementary groups) are used to determine which permission category applies. The human-readable username is just a convenient label mapped to that number.

**Group.** A named collection of users, used to grant a shared level of access to multiple users at once, without having to grant it to each individually.

**GID (Group ID).** The numeric identifier for a group, analogous to a UID for a user.

**Owner.** The specific user identity a file or directory belongs to.

**Owning group.** The specific group a file or directory is associated with (distinct from its owner — a file can be owned by one user but associated with a group other users also belong to).

**Other users.** Everyone who is neither the owner nor a member of the owning group.

**A genuinely observed illustration**, captured directly from this environment:

```text
$ id
uid=1000(sovon) gid=1000(sovon) groups=1000(sovon),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users)

$ whoami
sovon

$ groups
sovon adm cdrom sudo dip plugdev users
```

**What this shows, concretely:** `id` reports this user's UID (`1000`), primary GID (`1000`), and every group they belong to — note that a single user commonly belongs to *several* groups at once, not just one; `whoami` reports just the username corresponding to that UID; `groups` lists the same group memberships `id` showed, in a shorter format. **Your own environment's UID, username, and group memberships will differ** — this is genuinely observed output from this specific environment, not a value to expect universally.

### Permission categories

In the traditional Unix/Linux permission-bit model, access permissions are divided into three categories: owner, group, and others.

| Category | Applies to |
|---|---|
| **Owner** | The one specific user who owns the file |
| **Group** | Members of the file's owning group (other than the owner) |
| **Others** | Everyone else |

Each category gets its own, independently set combination of read/write/execute permission (next subsection) — this is why a file can be, for example, fully readable and writable by its owner, readable only by its group, and completely inaccessible to everyone else, all at once.

### Permission types: read, write, execute

| Symbol | Name |
|---|---|
| `r` | read |
| `w` | write |
| `x` | execute |

**These three letters mean something genuinely different depending on whether they're applied to a regular file or to a directory — this distinction is essential, and oversimplifying it is one of the most common sources of confusing permission errors (Section 11).**

**For a regular file:**

- **`r` (read)** — permission to view the file's content.
- **`w` (write)** — permission to modify the file's content.
- **`x` (execute)** — permission to run the file as a program (only meaningful for files that actually contain executable code or a valid script).

**For a directory:**

- **`r` (read)** — permission to **list** the names of entries inside the directory (what `ls` shows) — this is *not* the same as being able to read the *content* of the files inside it.
- **`w` (write)** — permission to **create, rename, or delete entries within the directory** (directory write permission allows modification of directory entries, subject to additional restrictions such as the sticky bit) — this is *not* "edit the directory like a text file"; a directory has no editable "content" in that sense. Having write on a directory affects whether you can add or remove things *inside* it, not whether you can modify the directory's own listing directly.
- **`x` (execute)** — permission to **traverse into the directory** — that is, to actually enter it and access things inside it by name (including files whose exact name you already know), *combined with whatever permissions apply to those specific items*.

**Why this distinction matters so much: read and execute on a directory answer two different questions.** `r` on a directory answers "can I see what's in here (get a listing)?" `x` on a directory answers "can I actually get in and reach something inside, by name?" These are independent — Section 9's genuinely observed lab demonstrates both directions of this directly: a directory with `x` but not `r` lets you access a specific, already-known filename inside it but not list its contents; a directory with `r` but not `x` lets you list what's inside but not actually access any of it.

### Octal (numeric) permissions

Each permission type has a fixed numeric value:

```text
r = 4
w = 2
x = 1
```

**Combining permissions within one category is done by adding these values together:**

| Combination | Sum | Symbolic form |
|---|---|---|
| nothing | 0 | `---` |
| execute only | 1 | `--x` |
| write only | 2 | `-w-` |
| write + execute | 3 | `-wx` |
| read only | 4 | `r--` |
| read + execute | 5 | `r-x` |
| read + write | 6 | `rw-` |
| read + write + execute | 7 | `rwx` |

**In the basic `rwx` model, permissions are commonly represented using three octal digits — one for owner, one for group, one for others — read left to right** (Linux also supports additional special mode bits, which are outside this lesson's scope):

| Numeric | Owner | Group | Others | Meaning |
|---|---|---|---|---|
| `644` | `rw-` (6) | `r--` (4) | `r--` (4) | Owner can read/write; everyone else can only read — a common default for ordinary files |
| `755` | `rwx` (7) | `r-x` (5) | `r-x` (5) | Owner has full access; everyone else can read and traverse/execute, but not modify — a common default for directories and executable scripts |
| `700` | `rwx` (7) | `---` (0) | `---` (0) | Only the owner has any access at all |
| `600` | `rw-` (6) | `---` (0) | `---` (0) | Only the owner can read or write; no one else has any access — common for private, sensitive files |

**Do not memorize these four numbers as magic values.** Every one of them is fully derivable, digit by digit, from the `r=4, w=2, x=1` model above — `644` is genuinely just "owner: 4+2=6, group: 4, others: 4," nothing more mysterious than that.

### Symbolic permissions

The other way to express and change permissions uses letters directly, rather than numbers:

```text
u = user (owner)
g = group
o = others
a = all (owner + group + others together)
```

Combined with `+` (add a permission), `-` (remove a permission), or `=` (set exactly this permission, replacing whatever was there), using the `chmod` command:

```bash
chmod u+x file      # add execute permission for the owner
chmod g-w file       # remove write permission for the group
chmod o-r file        # remove read permission for others
```

Numeric form is equally valid and often more concise for setting a complete permission value at once:

```bash
chmod 644 file
chmod 755 file
```

**A genuinely observed illustration of symbolic `chmod`**, captured directly from this environment:

```text
$ ls -l notes.txt
-rw-r--r-- 1 sovon sovon 6 Sep 10 15:05 notes.txt

$ chmod u+x notes.txt
$ ls -l notes.txt
-rwxr--r-- 1 sovon sovon 6 Sep 10 15:05 notes.txt

$ chmod u-x,g-w,o-r notes.txt
$ ls -l notes.txt
-rw-r----- 1 sovon sovon 6 Sep 10 15:05 notes.txt
```

Each `chmod` call visibly changed exactly the specific bit requested — `u+x` added only the owner's execute bit; `u-x,g-w,o-r` (multiple changes in one call, separated by commas) removed the owner's execute bit, the group's write bit, and others' read bit simultaneously — leaving every other bit untouched.

**Safety note, honored throughout this lesson:** every `chmod` example in this lesson is demonstrated on a file created specifically for that demonstration, inside an isolated temporary directory — never on an existing system file, another user's file, or any file outside a lesson-created demonstration area.

### Ownership

**Commands used to inspect ownership and identity, each explained:**

| Command | What it shows |
|---|---|
| `ls -l` | A file's permissions, owner, and group, alongside other metadata (Concept 07) |
| `stat` | A more detailed view of a file's metadata, including ownership and permissions in both symbolic and numeric form |
| `id` | The current user's UID, primary GID, and full group membership list |
| `whoami` | Just the current username |
| `groups` | The current user's group memberships |

**A genuinely observed illustration**, tying ownership directly to a real file:

```text
$ ls -l notes.txt
-rw-r--r-- 1 sovon sovon 6 Sep 10 15:05 notes.txt

$ stat notes.txt
  File: notes.txt
  size: 6         	Blocks: 8          IO Block: 4096   regular file
Device: 0,75	Inode: 240         Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/   sovon)   Gid: ( 1000/   sovon)
```

Reading `ls -l`'s output left to right: the permission string (`-rw-r--r--`), then owner (`sovon`), then group (`sovon`). `stat` shows the same permission information in both numeric (`0644`) and symbolic (`-rw-r--r--`) form simultaneously, alongside the owning `Uid`/`Gid` — directly connecting this section's ownership concepts to Concept 07's metadata concepts.

**Why ownership matters, and how it interacts with permissions:** the permission bits alone are meaningless without knowing *whose* rules apply to *whom* — ownership is what determines which of the three permission categories (owner/group/others) applies to any given user making a request (Section 6 explains the full check).

### Files vs. directories: a dedicated comparison, with genuinely observed evidence

| | Regular file | Directory |
|---|---|---|
| **`r`** | View the file's content | List the names of entries inside (not their content) |
| **`w`** | Modify the file's content | Create, rename, or delete entries within the directory |
| **`x`** | Run the file as a program | Traverse into the directory to access entries by name |

**Practical combinations, each demonstrated with genuinely observed output from this environment** (a directory `secretdir` containing one file, `inside.txt`):

**`x` without `r` (execute-only directory):**

```text
$ chmod 100 secretdir
$ ls -ld secretdir
d--x------ 2 sovon sovon 60 Sep 10 15:05 secretdir

$ ls secretdir
ls: cannot open directory 'secretdir': Permission denied

$ cat secretdir/inside.txt
inside
```

**This is the single most important, and most counterintuitive, result in this whole lesson: `ls secretdir` fails, but `cat secretdir/inside.txt` genuinely succeeds.** Without list (`r`) permission, you cannot enumerate what's inside the directory — but with traverse (`x`) permission, you can still reach a specific file by name, *if* you already know that name and the file's own permissions (Section 5's file-level rules) allow it.

**`r` without `x` (list-only directory):**

```text
$ chmod 400 secretdir
$ ls -ld secretdir
dr-------- 2 sovon sovon 60 Sep 10 15:05 secretdir

$ ls secretdir
inside.txt

$ cat secretdir/inside.txt
cat: secretdir/inside.txt: Permission denied
```

**The exact reverse result: `ls secretdir` succeeds (you can see that `inside.txt` exists), but `cat secretdir/inside.txt` fails.** You can see the *name* of what's inside, but you cannot actually traverse into the directory to reach it — knowing a file exists and being able to access it are genuinely separate permissions.

**`w` without `x`:** write permission on a directory (creating/deleting entries) generally requires traverse (`x`) permission to be practically usable at all — without `x`, a process typically cannot even reach into the directory to exercise that write permission in the first place. This lesson does not demonstrate this combination further, since its practical effect (an unusable write permission) follows directly from the traversal rule already demonstrated above.

**A full `rwx` directory**, restored at the end of this lesson's lab (Section 9), behaves the way most learners initially assume *every* directory permission works — list, create/delete, and traverse all function normally together. **The two examples above exist specifically to show that this "everything just works" behavior is not automatic — it depends on all three bits being present, and each bit genuinely governs something different.**

**Why directory permissions can produce confusing errors:** a learner who only thinks about read/write/execute in the regular-file sense (Section 5) will be genuinely surprised the first time they hit exactly the two scenarios demonstrated above — this is one of the most common sources of "but the file IS readable, why can't I access it?!" confusion in real troubleshooting (Section 11's Scenario 3 returns to this directly).

---

## 6. How It Works Internally

### The permission-checking flow

```text
Python process
      ↓
requests file access                (via a system call — Concept 02)
      ↓
OS receives request
      ↓
OS identifies process/user/group identity     (the requesting process's UID/GID — Section 5)
      ↓
OS examines target resource metadata            (owner, owning group, permission bits — Concept 07)
      ↓
OS evaluates applicable permissions               (which category — owner/group/others —
                                                      applies, and what that category allows)
      ↓
ALLOW or DENY
      ↓
Python receives success or error                    (data, or a permission-related exception)
```

**Connecting each step to earlier Module 0.2 concepts, without repeating them:**

- **User space and the kernel (Concept 01):** the Python process runs in user space and has no ability to directly grant itself access — the decision is made by the kernel, the trusted, privileged component with authority over this. (This lesson teaches the traditional Unix/Linux permission-bit model; Linux can also apply additional access-control mechanisms, which are intentionally outside this lesson's scope.)
- **System calls (Concept 02):** "requests file access" is, underneath, exactly the system-call mechanism Concept 02 introduced — the permission check happens as part of the kernel's handling of that call, at the "validation" step Concept 02 already described in general terms.
- **Processes (Concept 03):** the "process/user/group identity" the OS checks is the requesting process's own identity, established when it was created (a preview of the Process Lifecycle lesson still ahead).
- **Filesystems (Concept 07):** the "target resource metadata" is precisely the metadata Concept 07 introduced — owner, group, and permission bits, stored alongside every file and directory.

**What this lesson deliberately does not do:** go into kernel source code or filesystem-specific implementation details of exactly how this check is encoded or executed at the lowest level — the conceptual flow above is the right level of depth for this foundational lesson.

---

## 7. Real-World Example

| Example | What's happening | Permission concept involved |
|---|---|---|
| A model-serving service reads model weights | The service process's identity must have read permission on the model file | Owner/group/others, read on a regular file (Section 5) |
| An ingestion service reads a dataset directory | The process needs both `x` (to traverse into the directory) and read access to the individual files | Directory `x` vs. `r` (Section 5) |
| An application writes log files | The service's identity needs write permission on the log directory (to create new log files) and/or the log file itself | Write on a directory vs. a file (Section 5) |
| A service writes temporary artifacts | Similar to logs — write access scoped to a specific, expected directory | Write permission, service-account scoping (Section 3) |
| A model directory is made read-only for a serving process | The service can load the model but cannot accidentally modify or delete it | Read without write — a deliberate, common production pattern |
| A configuration/secrets file is tightly restricted | Permissions like `600`, restricting access to only the owning identity | Numeric permissions, "others" category (Section 5) |
| A service runs under a dedicated service account | The service's process identity (UID/GID) is distinct from any interactive human user, scoping its access narrowly | Ownership, user/group identity (Section 5) |
| A deployment directory is made read-only after deployment | Prevents a running service from modifying its own code, even if compromised or buggy | Least-privilege reasoning (Section 3, Section 15) |
| A script works locally but fails under a production service account | The two identities have different permissions on the same files | Section 11's Scenario 4 |
| A learner accesses a directory with `x` but not `r` | A specific, known file can still be reached, even though the directory can't be listed | Section 5's genuinely observed directory-permission experiment |

---

## 8. Relationships to Other Concepts

```text
Kernel
   ↓
System Calls
   ↓
Process Identity
   ↓
Filesystem
   ↓
File/Directory Metadata
   ↓
Permissions
   ↓
Application Behavior
```

| Concept | Relationship to permissions | Prerequisite or later? | Full treatment |
|---|---|---|---|
| Kernel and User Space | The kernel is the trusted authority that enforces the permission-bit checks taught here; user-space code cannot bypass them | Prerequisite (Concept 01) | Already covered |
| System Calls | Permission checks happen as part of the kernel's handling of file-related system calls (Section 6) | Prerequisite (Concept 02) | Already covered |
| Processes | A process's identity (UID/GID, inherited at creation) is exactly what permission checks evaluate against | Prerequisite (Concept 03) | Already covered |
| Threads | Threads within a process share that process's identity, and therefore share the same permission outcomes | Prerequisite (Concept 04) | Already covered |
| Scheduling | Independent of permissions — governs *when* a process runs, not *what* it may access | Prerequisite (Concept 05) | Already covered |
| Virtual Memory | Independent of file permissions, though file-backed memory mapping (Concept 06) is still subject to the underlying file's permissions | Prerequisite (Concept 06) | Already covered |
| Filesystems | Provides the files/directories and the metadata (owner, group, permission bits) this lesson's checks operate on | Prerequisite (Concept 07) | Already covered |
| Environment Variables | Independent of file permissions, though environment variables sometimes configure *which* file paths a service should use | Later | Concept 09 |
| Signals | Independent of file permissions — a separate kernel-mediated process interaction | Later | Concept 10 |
| Standard Input/Output | Redirecting standard streams to/from a file (Concept 11, still ahead) is still subject to that file's permissions | Later | Concept 11 |
| Pipes | A different, non-file-backed kernel channel, not directly subject to filesystem permissions | Later | Concept 12 |
| Shell | The everyday interface used to run `chmod`, `ls -l`, and every other command this lesson demonstrated | Later | Concept 13 |
| Process Lifecycle | Explains, in full, exactly how and when a process's identity (used throughout this lesson) is actually established | Later | Concept 14 |

---

## 9. Practical Observation / Commands

You are working in Ubuntu inside WSL2. All commands below are safe, use only a self-created temporary directory, and require no `sudo`. Every permission change in this lesson is made only to files and directories created specifically for this demonstration, and every one is cleaned up (and verified removed) at the end. **WSL2 caveat, stated once and applying throughout:** the permission behavior demonstrated below applies to this environment's native Linux filesystem (`ext4`, Concept 07). **Permission semantics are not guaranteed to behave identically on a Windows-mounted path such as `/mnt/c`** — those paths are bridged through WSL2's `drvfs` mechanism (Concept 07's genuinely observed example) onto an underlying Windows filesystem with a different native permission model, and this lesson deliberately does not claim WSL2 makes that difference disappear. All practical work in this lesson uses the native Linux filesystem specifically to avoid that ambiguity.

### Setting up a self-created temporary directory

```bash
mkdir -p /tmp/permissions-lesson-demo
cd /tmp/permissions-lesson-demo
pwd
```

**Observed in this environment** (path shortened for readability; the demonstration used an equivalent isolated temporary directory):

```text
/tmp/.../permissions-lesson-demo
```

### 1. Inspecting default permissions on a new file

```bash
printf "hello\n" > notes.txt
ls -l notes.txt
```

**Observed in this environment:**

```text
-rw-r--r-- 1 sovon sovon 6 Sep 10 15:05 notes.txt
```

A newly created file here defaults to `644` (`rw-r--r--`) — owner read/write, group and others read-only. (Default permissions for newly created files are influenced by a mechanism called `umask`, which this lesson does not teach in depth — only the observed *result* matters here.)

### 2. Changing permissions numerically, and observing the change

```bash
chmod 600 notes.txt
ls -l notes.txt
```

**Observed in this environment:**

```text
-rw------- 1 sovon sovon 6 Sep 10 15:05 notes.txt
```

### 3. Attempting an allowed operation, then a deliberately denied one

```bash
chmod 400 notes.txt
ls -l notes.txt
cat notes.txt                 # allowed: read bit is present
echo "more text" >> notes.txt  # denied: write bit was removed, even for the owner
```

**Observed in this environment:**

```text
-r-------- 1 sovon sovon 6 Sep 10 15:05 notes.txt
hello
/bin/bash: line 20: notes.txt: Permission denied
```

**This is a genuinely important, often-surprising result: even the file's *owner* is denied write access once the write bit is removed (for an ordinary unprivileged process).** Permission bits are not a suggestion that only applies to "other people" — they apply to the owner's own access too, exactly as literally specified.

### 4. Restoring safe permissions

```bash
chmod 644 notes.txt
ls -l notes.txt
```

**Observed in this environment:**

```text
-rw-r--r-- 1 sovon sovon 6 Sep 10 15:05 notes.txt
```

### 5. Directory permissions: the `x`-without-`r` and `r`-without-`x` experiments

```bash
mkdir secretdir
printf "inside\n" > secretdir/inside.txt
chmod 644 secretdir/inside.txt

chmod 100 secretdir        # x only — traverse, but cannot list
ls -ld secretdir
ls secretdir
cat secretdir/inside.txt
```

**Observed in this environment:**

```text
d--x------ 2 sovon sovon 60 Sep 10 15:05 secretdir
ls: cannot open directory 'secretdir': Permission denied
inside
```

```bash
chmod 400 secretdir        # r only — list, but cannot traverse
ls -ld secretdir
ls secretdir
cat secretdir/inside.txt
```

**Observed in this environment:**

```text
dr-------- 2 sovon sovon 60 Sep 10 15:05 secretdir
inside.txt
cat: secretdir/inside.txt: Permission denied
```

This is the same genuinely observed evidence already shown in Section 5 — reproduced here as a hands-on step-by-step lab you can repeat yourself.

### 6. Restoring the directory to safe permissions

```bash
chmod 700 secretdir
ls -ld secretdir
ls secretdir
```

**Observed in this environment:**

```text
drwx------ 2 sovon sovon 60 Sep 10 15:05 secretdir
inside.txt
```

### 7. Symbolic `chmod`

```bash
chmod u+x notes.txt
ls -l notes.txt
chmod u-x,g-w,o-r notes.txt
ls -l notes.txt
chmod 644 notes.txt          # restore to the safe default
```

**Observed in this environment** (also shown in Section 5):

```text
-rwxr--r-- 1 sovon sovon 6 Sep 10 15:05 notes.txt
-rw-r----- 1 sovon sovon 6 Sep 10 15:05 notes.txt
```

### 8. Cleanup, and verification

```bash
cd /
rm -rf /tmp/permissions-lesson-demo
ls -d /tmp/permissions-lesson-demo
```

**Observed in this environment:**

```text
ls: cannot access '/tmp/.../permissions-lesson-demo': No such file or directory
```

Confirming complete cleanup — nothing from this lesson's practical work was left behind, and no system file, unrelated user file, or unrelated process was ever touched.

---

## 10. Common Misconceptions

| Misconception | Why it's wrong |
|---|---|
| "File permissions and file ownership are the same thing." | Ownership (*who* the owner/group are — Section 5) and permissions (*what* each category may do — Section 5) are separate pieces of metadata that work together, not the same concept. |
| "`r` always means I can read the contents." | `r` on a regular file means read content; `r` on a directory only means you can *list its entries' names* — not read the content of the files inside (Section 5's dedicated comparison). |
| "`w` on a directory means I can edit the directory like a text file." | `w` on a directory governs whether you can create, rename, or delete entries *within* it — a directory has no editable "content" the way a regular file does (Section 5). |
| "`x` always means execute a program." | `x` on a regular file does mean "run as a program"; `x` on a directory means something entirely different — traverse/enter it (Section 5). |
| "`chmod 777` is the normal solution to permission errors." | `777` grants full read/write/execute to everyone — it fixes the symptom by removing all protection, rather than identifying and correctly granting the specific, minimal access actually needed (Section 11). |
| "If a Python program can see a path, it can necessarily access it." | Section 5's `r`-without-`x` experiment showed exactly this failing directly: a file's name can be visible (listed) while actually accessing it is still denied. |
| "A file extension determines permissions." | Permissions are entirely separate metadata from a filename (Concept 07's related misconception) — an extension has no bearing on a file's permission bits. |
| "Permissions only matter for human users." | Every process, including a non-interactive Python service, has an identity (UID/GID, Section 5) that permission checks apply to exactly the same way as for an interactive user. |
| "A process always runs with my interactive user's full access." | A process's actual identity depends on how and under which account it was started — a production service commonly runs under a different, more restricted service account (Section 3, Section 11's Scenario 4). |
| "Permission denied always means the file itself is missing." | A `PermissionError` and a `FileNotFoundError` (Concept 07) are different, distinguishable failures — the file can exist and still be inaccessible (Section 11). |
| "Changing permissions is always harmless." | Loosening permissions (especially broadly, like `777`) can expose data or allow unintended modification; tightening them incorrectly can break a service that legitimately needs the access removed — every change has a real effect (Section 11). |
| "Windows and Linux permission behavior are identical." | This lesson's own WSL2 caveat (above) explains directly why Windows-mounted paths (`/mnt/c`, bridged via `drvfs`) are not guaranteed to exhibit the same permission semantics as this environment's native Linux filesystem. |

---

## 11. Debugging and Troubleshooting

### A systematic reasoning workflow

```text
Reproduce
   ↓
Inspect
   ↓
Identify identity              (whoami / id — which UID/GID is actually making this request?)
   ↓
Inspect ownership                (ls -l / stat — who owns the target?)
   ↓
Inspect permissions                (what do the owner/group/others bits actually say?)
   ↓
Check directory traversal            (does every directory in the path have x for this identity?)
   ↓
Check parent directories               (the failure might not be the file itself at all)
   ↓
Form hypothesis
   ↓
Test safely                              (on a copy or a scoped, minimal change — never 777)
   ↓
Fix the root cause                         (grant the minimal permission actually needed)
   ↓
Verify
```

**Why "check directory traversal" and "check parent directories" are their own explicit steps:** Section 5's `x`-without-`r` experiment demonstrated directly that a file's *own* permissions being perfectly fine is not sufficient — every directory in the path leading to it also needs traverse (`x`) permission for the requesting identity. A surprising number of real permission failures trace back to a *parent* directory, not the file everyone initially suspects.

**Scenario 1 — `PermissionError: [Errno 13] Permission denied`.**

1. *Problem:* a Python program raises this exact error trying to open a file.
2. *Beginner's likely assumption:* "The file must be missing, or my code has a typo."
3. *Correct mental model:* `PermissionError` means the requested operation was denied because the process lacked sufficient access rights. The denial may involve the target file, a directory in the path, or another access-control condition (Section 6) — a different failure category from `FileNotFoundError` (Section 10).
4. *Investigation approach:* run `whoami`/`id` to confirm which identity is actually running the script, then `ls -l`/`stat` on the target file to compare its owner/group/permission bits against that identity.
5. *Expected conclusion:* the requesting identity does not have the required permission category (owner/group/others) satisfied for the requested operation — the fix is granting the *minimum* needed access to the *correct* identity, not blanket-opening the file.

**Scenario 2 — A program can read a file but cannot write it.**

1. *Problem:* reading succeeds; writing to the same file fails.
2. *Beginner's likely assumption:* "That doesn't make sense — if I can read it, I should be able to write it too."
3. *Correct mental model:* read and write are two entirely independent bits within the same category (Section 5) — a file can absolutely have `r` set and `w` unset for the same category at once (this lesson's own `400` example demonstrated exactly this).
4. *Investigation approach:* check the specific permission string (`ls -l`) for the write bit (`w`) in the category that applies to this identity, specifically.
5. *Expected conclusion:* read access and write access are never guaranteed to travel together — each must be checked and granted independently.

**Scenario 3 — A program cannot access a file inside a directory even though the file itself appears readable.**

1. *Problem:* `ls -l` on the file shows perfectly permissive bits, yet access still fails.
2. *Beginner's likely assumption:* "This must be a bug in the OS, since the file's own permissions look fine."
3. *Correct mental model:* this is precisely Section 5's `r`-without-`x` directory experiment — the *file's* permissions are irrelevant if a directory somewhere in the path leading to it lacks traverse (`x`) permission for this identity.
4. *Investigation approach:* check every directory in the path, not just the final file — `ls -ld` on each directory level, looking specifically for the `x` bit for the relevant category.
5. *Expected conclusion:* file-level permissions and the permissions of every containing directory are independent, and *all* of them must cooperate for access to succeed — a single missing `x` anywhere in the path is enough to cause exactly this symptom.

**Scenario 4 — A script works manually but fails under another user/service account.**

1. *Problem:* running a script interactively (as yourself) works fine; running the identical script under a service account fails.
2. *Beginner's likely assumption:* "The script must be broken for that specific account somehow."
3. *Correct mental model:* different identities (Section 5) can have genuinely different permission outcomes for the exact same files — your interactive user and a service account are different UIDs, very possibly in different groups, with no guarantee of matching access.
4. *Investigation approach:* determine which identity the service account actually runs as (this varies by how the service is configured — outside this lesson's scope to teach exhaustively), then compare that identity's access against the same file/directory permissions the script needs.
5. *Expected conclusion:* "works for me, fails as the service" is a strong, specific signature of an identity/permission mismatch, not a code bug — Section 3's service-account discussion previewed exactly this.

**Scenario 5 — A model-serving process cannot read a model/checkpoint file.**

1. *Problem:* an inference service fails to load its model file with a permission-related error.
2. *Beginner's likely assumption:* "The model file must be corrupted or in the wrong location."
3. *Correct mental model:* this is very likely an ownership/permission mismatch between the identity the serving process runs as and the model file's owner/group/permission bits — a common outcome when model artifacts are deployed by one identity (say, a build process) but served by another (a dedicated service account).
4. *Investigation approach:* `ls -l`/`stat` on the model file to see its owner and permission bits, compared against `whoami`/`id` for the actual serving process's identity.
5. *Expected conclusion:* granting the serving identity the minimum necessary read access (often via the appropriate group, rather than opening the file to "others") resolves this without over-broadening access.

**Scenario 6 — An application can create files in one directory but not another.**

1. *Problem:* the exact same code succeeds writing to `logs/` but fails writing to `data/`.
2. *Beginner's likely assumption:* "The application logic for writing must differ between these two paths."
3. *Correct mental model:* if the code path is genuinely identical, the difference is almost certainly the two directories' own permissions (specifically, the write bit for this identity's applicable category — Section 5) — not the application logic at all.
4. *Investigation approach:* `ls -ld` on both directories, comparing owner, group, and the write bit specifically for whichever category (owner/group/others) this identity falls into for each.
5. *Expected conclusion:* directory-level write permission is set independently for every directory — one directory being writable says nothing about any other, even to the exact same process.

---

## 12. Exercises

Work through these in your own words. No answer key exists for this lesson — the goal is reasoning ability, not matching a memorized phrase.

### Level 1 — Recognition

1. What are the three permission categories every file and directory has?
2. What do `r`, `w`, and `x` stand for?
3. What numeric value corresponds to each of `r`, `w`, and `x`?
4. What does the symbolic permission string `rwxr-x---` mean, category by category?
5. What numeric permission corresponds to `rwxr-x---`?
6. What is the difference between `u`, `g`, `o`, and `a` in symbolic `chmod` syntax?
7. Given `ls -l` output showing `-rw-r--r-- 1 alice staff ...`, identify the owner and the owning group.
8. What is the difference between a UID and a username?

### Level 2 — Understanding

9. Explain, in your own words, why `r` means something different for a directory than for a regular file.
10. Explain why `w` on a directory is not "editing the directory like a text file."
11. Explain, using Section 5's genuinely observed experiments, why a directory can allow `cat`-ing a known file while `ls` on that same directory fails.
12. Explain why the reverse (Section 5's `r`-without-`x` case) produces the opposite pattern.
13. Explain why a file's owner can still be denied access to their own file.
14. Explain why `chmod 777` is discouraged as a general troubleshooting fix.
15. Explain the difference between a `PermissionError` and a `FileNotFoundError`.
16. Explain why a Python service's identity might differ from your own interactive login identity.

### Level 3 — Application

17. In your own temporary directory, create a file and use `ls -l` to record its default permissions.
18. Change that file's permissions to `600` using numeric `chmod`, then confirm the change with `ls -l`.
19. Remove your own read permission from a file you own (`chmod 200` or similar) and attempt to read it. Record what happens.
20. Restore safe permissions on that file and clean it up.
21. Create a directory containing one file, then set the directory to `100` (execute-only). Attempt `ls` on the directory and `cat` on the known file inside it. Record both results.
22. Set the same directory to `400` (read-only) instead. Attempt the same two operations. Record both results, and explain why they differ from Exercise 21.
23. Use `chmod u+x`, then `chmod u-x`, on a file you created, confirming each change with `ls -l`.
24. Run `id`, `whoami`, and `groups` in your own terminal. Identify your UID and at least one group you belong to.

### Level 4 — Debugging

25. A Python script raises `PermissionError: [Errno 13] Permission denied` on a file that clearly exists. Using Scenario 1 from Section 11, describe your investigation steps in order.
26. A program can read a file but fails when trying to write to it. Using Scenario 2, explain why this is expected, not a contradiction.
27. A file shows fully permissive bits with `ls -l`, yet a process still cannot access it. Using Scenario 3, explain what you'd check next, and why.
28. A script works when you run it yourself but fails under a service account. Using Scenario 4, explain the most likely cause.
29. An inference service cannot read its own model checkpoint file. Using Scenario 5, describe how you'd diagnose it without immediately loosening permissions broadly.
30. An application can write to one directory but not another, using identical code. Using Scenario 6, explain what's most likely different between the two directories.
31. A learner's first instinct when hitting any permission error is to run `chmod 777` on the target. Explain, using Section 10 and Section 11, why this is not a good general troubleshooting habit, and what a better first step looks like.
32. A learner assumes that because they are the file's owner, they must always be able to read and write it no matter what. Using Section 9's `400` experiment, explain why this assumption is incorrect.

### Level 5 — Integration

33. Design a permission scheme (in your own words, not just numbers) for a small AI inference service with: a read-only model directory, a writable logs directory, a writable temporary-files directory, and a tightly restricted secrets/configuration file. Explain your reasoning for each.
34. A friend claims, "Since my script runs fine locally, permissions will never be an issue in production." Using Section 3, Section 7, and Scenario 4, construct a response explaining at least two concrete ways this assumption could fail.
35. Explain how this lesson's permission-checking flow (Section 6) and Concept 02's system-call model together explain what actually happens, step by step, when a Python data-processing script calls `open("dataset.csv")` and receives a `PermissionError`.
36. A production AI service's deployment process copies a model file as one user, but the model-serving process runs as a different, dedicated service account. Using Section 3, Section 7, and Scenario 5, explain what could go wrong and how you'd verify the fix before deploying it.
37. Using everything in this lesson, explain to a beginner (in your own words, as if teaching them) why "the file exists and looks fine in `ls`" is not the same claim as "this specific process can actually access it" — and why that distinction is one of the most valuable things this lesson teaches.

---

## 13. Expected Results

**Expected conceptual results — these should hold regardless of your specific machine:**

- Correctly translate between symbolic (`rwxr-xr--`) and numeric (`754`) permission notation, in either direction.
- Correctly explain what `r`, `w`, and `x` mean separately for regular files and for directories.
- Correctly predict, given a directory's permissions and a known filename inside it, whether `ls` and whether `cat <known file>` would each succeed or fail.
- Explain why a file's owner is not automatically exempt from its own permission restrictions.
- Correctly identify, for several of this lesson's twelve misconceptions, why each is wrong and what the accurate idea is instead.

**What the practical observations should generally demonstrate, regardless of the exact values:**

- A newly created file's default permissions should show as readable/writable by the owner and readable by group/others (commonly `644`), though the exact default can be influenced by system configuration this lesson does not teach (`umask`).
- Removing the write bit (`chmod 400`) should cause any write attempt — even by the file's own owner — to fail with `Permission denied`.
- A directory with `x` but not `r` should allow accessing a specific, already-known filename inside it while `ls` on that directory fails.
- A directory with `r` but not `x` should show the exact opposite pattern.

**Possible environment-dependent results — these will vary by machine and are expected to vary:**

- Your own `id`/`whoami`/`groups` output will differ entirely from this lesson's actual observed values (UID `1000`, username `sovon`, and this environment's specific group list) — every environment has its own identity.
- Your own file's inode number, timestamps, and exact default permissions may differ slightly depending on your system's configuration.
- Permission behavior on a Windows-mounted WSL2 path (`/mnt/c`) is **not** guaranteed to match this lesson's native-Linux-filesystem observations — this lesson deliberately performed all practical work on the native filesystem specifically to avoid that ambiguity, and you should do the same when practicing.

---

## 14. Review Questions

Answers are intentionally not provided directly below these questions.

### Foundational knowledge

- What is a permission, in the OS sense this lesson introduced?
- What are the three permission categories, and what does each cover?
- What is the difference between a UID and a GID?
- What is the difference between an owner and an owning group?

### Reasoning

- Why does `r` mean something different for a directory than for a regular file?
- Why can a directory be listable but not traversable, or traversable but not listable?
- Why is a file's owner still subject to that file's own permission bits?
- Why is `chmod 777` generally the wrong instinct when debugging a permission error?

### OS relationships

- **What happens, step by step, when a process requests access to a file the OS ultimately denies?**
- How does a process's identity (Concept 03) connect to the permission checks this lesson described?
- Why did this lesson need Concept 07 (filesystems) as a direct prerequisite?

### Practical Linux

- What is the difference between what `ls -l` and `stat` each show about a file?
- What do `id`, `whoami`, and `groups` each report?
- What numeric permission does `rwxr-x---` correspond to, and what does `chmod 750` set?
- Why might permission behavior differ between a native Linux path and a Windows-mounted WSL2 path?

### AI engineering

- Why might a model-serving process fail to read its own model checkpoint file, even though the file clearly exists?
- Why is it common, and often deliberately good practice, for a deployed model directory to be read-only for the serving process?
- Why can a script that works fine when you run it manually still fail once deployed under a service account?

---

## 15. Production Relevance

At this point, you understand what OS permissions are, how owner/group/others and read/write/execute work together, why files and directories interpret those three letters differently, how numeric and symbolic permission notation relate, and how the OS actually checks a request step by step. You are not yet expected to know ACLs, advanced Linux capabilities, container security, or cloud IAM — those remain later, more advanced topics.

For a production Applied AI Engineer, this lesson's mental model shows up constantly:

```text
AI Application
      ↓
Python Process
      ↓
Operating System Identity          (Section 5 — which UID/GID this process actually runs as)
      ↓
Filesystem                          (Concept 07)
      ↓
Permissions                          (this lesson)
      ↓
Dataset / Model / Config / Logs       (Section 3, Section 7)
```

- **A model-serving service reading model weights.** Must have read access, and typically *should not* have write access — a deliberate, common least-privilege pattern.
- **An ingestion service reading datasets.** Needs both traverse (`x`) permission on every containing directory and read access on the actual files — Section 5's directory-permission distinction, applied directly.
- **An application writing logs.** Needs write access scoped specifically to its log directory — not broad write access elsewhere.
- **A service writing temporary artifacts.** Similarly scoped — write access to exactly where it's expected to write, and nowhere else by default.
- **Read-only model directories.** A deliberate production safeguard: even if the serving process is compromised or has a bug, it cannot modify or delete the model it's serving.
- **Configuration/secrets protection.** Tightly restricted permissions (often `600`, readable only by the owning identity) are a first, foundational line of defense for credentials and sensitive configuration.
- **Separate service accounts.** Running different services under different, dedicated identities (rather than one shared, broadly-privileged account) is what makes scoped, minimal permissions actually meaningful and enforceable.
- **Least privilege.** The overarching principle behind every example above: grant each process identity exactly the access it needs to do its job, and nothing more — directly connecting back to Section 2's "why permissions exist" and Section 11's "never default to `777`" debugging guidance.
- **Avoiding unnecessarily broad permissions.** Every example in this lesson — from the `400`/`600` file experiments to the directory-traversal experiments — exists to build the instinct that *correctly scoped, minimal* permissions are both safer and, once you understand the model, no harder to reason about than overly broad ones.

**Where this lesson stops, deliberately.** This lesson does not teach ACLs, SELinux, AppArmor, Linux capabilities, namespaces, cgroups, container security, Kubernetes RBAC, cloud IAM, enterprise identity systems, cryptographic access control, advanced filesystem permission implementation, kernel source code, security hardening, or offensive security — every one of these is a genuinely important, more advanced topic, and every one of them is built directly on top of the owner/group/others, read/write/execute foundation this lesson just established. Trying to reason about container security or cloud IAM without first understanding what a UID, a permission bit, and a directory traversal check actually are would be building on nothing.

**What comes next**, building directly on this lesson:

```text
Permissions                     ← this lesson
  → Environment Variables         (often used to configure which file paths a service uses)
  → Signals                        (a separate kernel-mediated process interaction)
  → Standard Input/Output            (streams that can be redirected to/from permission-checked files)
  → Pipes                             (a different, non-file-backed kernel channel)
  → Shell                              (the everyday interface for running `chmod`, `ls -l`, and more)
  → Process Lifecycle                   (exactly how and when a process's identity is established)
```

None of these are taught here — this section exists only to show where this lesson sits within the larger Module 0.2 sequence you are building, one concept at a time.

---

_This file is the completed lesson for Concept 08 of Module 0.2. It intentionally does not teach ACL internals, SELinux internals, AppArmor internals, Linux capabilities in depth, namespaces, cgroups, container security, Kubernetes RBAC, cloud IAM, enterprise identity systems, cryptographic access control, advanced filesystem permission implementation, kernel source-code internals, advanced security hardening, penetration testing, or offensive security in depth — those remain the subject of later, more advanced curriculum, not this beginner-level foundation._
