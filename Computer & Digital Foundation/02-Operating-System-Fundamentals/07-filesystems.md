# 07 — Filesystems

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Module 0.2 — Operating System Fundamentals
**Concept(s) covered:** filesystems, files, directories, paths, metadata, inodes, mounting
**Status:** Not Started

---

## 1. What Is It?

**Connecting to what you already know.** [Virtual Memory](06-virtual-memory.md) explained how a running process's *in-memory* data is organized and addressed. This lesson is about the other half of a process's data story: the data that needs to **persist** — survive after the process ends, after the machine reboots, and be available the next time something needs it. That's the job of storage and filesystems.

**Storage.** Simple meaning: the physical hardware that holds data even when the computer is turned off (Module 0.1 introduced this as distinct from RAM). Technical meaning: a storage device is physical hardware providing persistent, non-volatile capacity — raw space, addressed in low-level chunks the hardware itself understands, with no inherent concept of "files" or "names" at all.

**Filesystem.** Simple meaning: the organization system that turns a storage device's raw space into named, findable files and folders. Technical meaning: a filesystem is the software layer — implemented largely by the kernel — that organizes a storage device's raw capacity into a structured collection of named files and directories, and provides applications a consistent way to create, read, write, and locate them.

**File.** Simple meaning: one named, stored unit of data — a document, a script, an image, anything you'd think of as "a file." Technical meaning: a file is a named collection of data, along with associated metadata (Section 5), that the filesystem tracks as a single, addressable unit.

**Directory.** Simple meaning: a folder — a named container that can hold files and other directories. Technical meaning: a directory is a filesystem object that associates names with other filesystem objects (files or further directories), allowing the filesystem's contents to be organized hierarchically.

**Path.** Simple meaning: the "address" you use to refer to a specific file or directory — where it is, spelled out. Technical meaning: a path is a string describing a location within the filesystem hierarchy, built from a sequence of directory names leading to a specific file or directory (Section 5).

**A storage device and a filesystem are not the same thing — this distinction matters throughout this entire lesson:**

```text
Physical Storage                (the raw hardware — Module 0.1)
     ↓
Filesystem                       (the organization system built on top of it)
     ↓
Directories + Files               (the structure applications actually see)
     ↓
Application Access                  (a program working with names and paths, Section 6)
```

**An analogy: a warehouse and its organization system.**

```text
Storage device      = a physical warehouse (the building and shelving itself)
Filesystem            = the organization system used to arrange things inside it
                          (aisles, labeled sections, an inventory index)
Files                  = the actual stored items
Directories             = organizational categories (which aisle, which shelf)
Paths                    = addresses — "aisle 3, shelf B, bin 12" — that let you
                            find a specific item without searching the whole warehouse
```

A warehouse full of unlabeled items in no particular order is technically "storing" things, but it's nearly useless — nobody could reliably find anything, and two items could easily end up indistinguishable. A warehouse with a real organization system — categorized sections, a consistent addressing scheme, a maintained index of what's where — is what actually makes the storage *usable*. This is exactly the relationship between raw storage and a filesystem: the storage provides the space; the filesystem provides the organization that makes that space actually usable by name.

**Where this analogy is useful:** it captures the core distinction — raw capacity versus the organizational system built on top of it — and shows why "the warehouse" (storage) and "the organization system" (filesystem) are genuinely separate things, even though most people only ever interact with the organized version.

**Where this analogy breaks down:**

- A warehouse's organization system is usually set up once and rarely restructured; a computer's filesystem is constantly, routinely updated — files created, moved, deleted — as an ordinary part of normal operation.
- A human warehouse worker uses judgment to decide where something "should" go; a filesystem follows precise, mechanical rules (Section 5's directory-entry and metadata concepts) with no judgment involved.
- The same physical warehouse can really only use one organizational scheme at a time; a computer can have multiple different filesystems, potentially even of different types, mounted and accessible at once (Section 5's "Mounting" subsection) — this analogy doesn't capture that flexibility at all.

---

## 2. Why Does It Exist?

**The problem, if applications had to manage raw storage directly.** A storage device, at the hardware level, offers nothing more than numbered blocks of raw space — no names, no organization, no concept of "where one file ends and another begins." If every application had to track exactly which raw blocks held its data, and coordinate with every other application to avoid overwriting each other's blocks, building any real software would be enormously impractical.

```text
Requirement: persist data reliably, and find it again later, by name
     ↓
Requirement: let many different applications share one storage device safely
     ↓
Requirement: organize related data into a structure people and programs can navigate
     ↓
Applications should not have to manually manage raw storage sectors themselves
     ↓
The operating system provides a filesystem: a structured, named, shared abstraction
     over raw storage
```

**The specific problems a filesystem solves:**

- **Organizing persistent data.** Data is arranged into a navigable structure (directories) rather than an undifferentiated pile.
- **Naming files.** Every file gets a human-meaningful name, rather than needing to be referred to by raw storage location.
- **Locating files.** The filesystem maintains the structure (Section 5's directory-entry concept) that lets a name or path be resolved back to the actual data.
- **Organizing directories.** Related files can be grouped together hierarchically, mirroring how people naturally think about organizing information.
- **Storing metadata.** Beyond a file's actual content, the filesystem tracks information *about* it — size, timestamps, ownership, permissions (Section 5) — without which many everyday operations (like "show me the most recently modified file") would be impossible.
- **Tracking available space.** The filesystem keeps track of which raw storage blocks are in use and which are free, so new files can be created without colliding with existing data.
- **Managing access.** The filesystem, working with the OS's permission system (a preview of the very next lesson), governs who and what is allowed to read, write, or otherwise use each file.
- **Providing a consistent interface to applications.** Every application — regardless of what it does — can rely on the same basic operations (open, read, write, create, delete) working the same way, over the same kind of names and paths.

**Why applications should not have to manually manage raw storage sectors.** This is a direct extension of the operating-system abstraction principle Concept 01 introduced: just as user-space applications don't directly control hardware, and instead ask the kernel via system calls (Concept 02), applications don't directly manage a storage device's raw blocks either — they ask the filesystem, through the kernel, to create, read, and write *files*, and the filesystem handles the messy, error-prone work of actually mapping those requests onto real storage blocks. Without this abstraction, every application would need its own, incompatible way of managing storage — making it effectively impossible for different programs to reliably share data on the same device at all.

---

## 3. Why an AI Engineer Needs It

Nearly everything a real AI system depends on lives, at some point, as a file:

- **Python source files** — your application's own code.
- **Configuration files** — settings, API keys' locations, model parameters, often read at startup.
- **Datasets** — training data, evaluation data, often large and numerous.
- **Uploaded documents** — user-supplied files an application needs to process.
- **Logs** — a running service's ongoing record of what it's doing.
- **Model checkpoints and model files** — the actual trained weights a model depends on, often very large.
- **Tokenizer files** — auxiliary files many NLP/LLM pipelines need alongside a model.
- **Temporary files** — short-lived data created and discarded during processing.
- **Cached data** — previously computed results, stored to avoid redundant work.
- **Generated artifacts and evaluation outputs** — results, reports, and experiment outputs a pipeline produces.

**Practical problems an AI engineer can encounter, all directly explained by this lesson:**

- **File not found** — the path used doesn't resolve to an existing file (Section 5, Section 11).
- **Incorrect path** — a subtle but common mistake distinguishing absolute from relative paths (Section 5).
- **Insufficient disk space** — the filesystem has run out of free capacity (Section 9, Section 11).
- **Permission denied** — a related but distinct problem, previewed here and covered in depth in the very next lesson, [Permissions](08-permissions.md).
- **Unexpected temporary-file behavior** — temporary files not being where, or persisting as long as, expected.
- **Large model files consuming storage** — a single model checkpoint alone can occupy a meaningful share of available disk capacity.
- **Logs filling a filesystem** — an unbounded, ever-growing log file can exhaust available disk space over time.
- **Datasets stored in the wrong location** — leading to confusion about which copy of the data is authoritative, or to path errors.
- **Relative paths behaving differently depending on working directory** — a script that works when launched one way and fails when launched another (Section 5's path subsection covers this directly).

**Where this lesson stops, deliberately.** This lesson does not teach cloud object storage, distributed filesystems, databases, or container volumes — each is a genuinely important, later topic in the roadmap, built on top of the foundational, single-machine filesystem model this lesson establishes.

---

## 4. Beginner Explanation

**Building intuition before technical terms.** A filesystem gives a computer a structured way to organize and retrieve persistent data — that's the entire idea this lesson is built around. Before any technical vocabulary, consider a simple, everyday file:

```text
notes.txt
```

This is just a **filename** — a name for one piece of stored data. On its own, it doesn't say *where* this file lives. Now consider:

```text
/home/user/notes.txt
```

This is a **path** — it doesn't just name the file, it describes exactly where to find it: starting from the very top of the filesystem (`/`, the **root directory**, Section 5), go into `home`, then into `user`, and there is `notes.txt`.

One more example, showing a deeper structure:

```text
/home/user/projects/ai-app/config.json
```

**Breaking this down, term by term:**

- **Filename** — `config.json`, the name of this specific file.
- **Directory** — `ai-app`, the folder this file directly lives inside.
- **Parent directory** — `projects`, the folder that contains `ai-app` (every directory except the root has exactly one parent).
- **Path** — the entire string, `/home/user/projects/ai-app/config.json`, describing the complete location from the root all the way down to this specific file.
- **Root directory** — `/`, the single starting point every absolute path in the filesystem is ultimately measured from (Section 5 explains this further).

**The core intuition to walk away with:** a path is genuinely address-like — just as a street address describes a location by naming successively more specific containers (country, city, street, building), a filesystem path describes a file's location by naming successively more specific directories, from the root all the way down to the file itself. `/home/user/projects/ai-app/config.json` is not an arbitrary string — it's a precise, navigable description of exactly where one specific file lives.

---

## 5. Technical Explanation

### Paths: absolute vs. relative

**Absolute path.** Simple meaning: a complete address, starting from the very top of the filesystem. Technical meaning: an absolute path begins at the filesystem root (`/` on Linux) and fully specifies a location, unambiguous regardless of where a program happens to currently be "standing."

```text
/home/user/project/data/train.csv
```

**Relative path.** Simple meaning: a shorter address, understood relative to "where you currently are." Technical meaning: a relative path is interpreted relative to the current working directory — the directory a running process is currently associated with — rather than from the filesystem root.

```text
data/train.csv
```

**Why this distinction matters directly for Python applications, with a concrete illustration:**

```text
Program launched from:  /home/user/project
Relative path used:     data/train.csv
Resolves to:             /home/user/project/data/train.csv     ← works correctly

Program launched from:  /home/user
Relative path used:     data/train.csv
Resolves to:             /home/user/data/train.csv             ← likely wrong / not found
```

The exact same line of code (`open("data/train.csv")`) can succeed or fail depending entirely on the current working directory the program happens to be launched from — not because of any bug in the code itself. This is one of the most common, and most easily misdiagnosed, real-world path problems (Section 11's Scenario C returns to this directly). **This lesson uses generic example usernames and paths throughout** (`/home/user/...`) rather than any specific actual home directory, except where Section 9 explicitly shows genuinely observed output from this environment.

### The Linux filesystem hierarchy, at a foundational level

```text
/
├── bin        (essential command programs)
├── boot        (files needed to start the system)
├── dev          (device files — Section 5's next subsection)
├── etc           (system-wide configuration files)
├── home            (personal directories for regular users)
├── proc              (a virtual filesystem exposing kernel/process info — see below)
├── tmp                 (temporary files, often cleared on reboot)
├── usr                   (installed programs and their supporting files)
└── var                     (variable/changing data — logs, caches, and similar)
```

**Important caveat:** this is a common, representative layout — **not every Linux distribution has exactly this layout or contents**, and this lesson deliberately does not claim otherwise. The *purposes* below are broadly consistent across mainstream Linux distributions, even where exact contents vary.

| Path | Common purpose |
|---|---|
| `/` | The root of the entire filesystem hierarchy — every absolute path starts here |
| `/home` | Personal directories for regular (non-administrative) users |
| `/tmp` | Temporary files, often cleared automatically on reboot — not for anything meant to persist long-term |
| `/etc` | System-wide configuration files |
| `/var` | Data expected to change over time while the system runs — logs are a common example |
| `/usr` | Installed programs and the supporting files they need |
| `/dev` | Special files representing devices (Module 0.1's I/O concepts, exposed here as filesystem entries) |
| `/proc` | **Not ordinary persistent storage at all** — a virtual filesystem, generated live by the kernel, exposing kernel and process information (Concept 02, Concept 03) through filesystem-style paths. Nothing under `/proc` is actually stored on a disk; it's produced on demand, in memory, each time it's read. |

**Connecting `/proc` to previous lessons directly:** Concept 02 and Concept 03 already used `/proc/<PID>/status` and similar paths to inspect running processes — this lesson's contribution is naming *why* that works: `/proc` looks and behaves like a normal filesystem (you can `cd` into it, `cat` files from it, use paths to navigate it) precisely because the kernel deliberately exposes its internal information through the same filesystem interface applications already know how to use — without `/proc` being backed by any actual persistent storage.

### Files and directories

```text
project/
├── app/
│   ├── main.py
│   └── config.py
├── data/
│   └── train.csv
└── README.md
```

Relative to `project/`, each item's path:

| Item | Path relative to `project/` |
|---|---|
| `main.py` | `app/main.py` |
| `config.py` | `app/config.py` |
| `train.csv` | `data/train.csv` |
| `README.md` | `README.md` (directly inside `project/`, no subdirectory) |

**Parent/child relationships:** `app/` and `data/` are children of `project/`; `main.py` and `config.py` are children of `app/`. Every file and directory (other than the root) has exactly one parent directory — this is what makes the whole structure a navigable hierarchy rather than an unordered collection.

### File metadata

**A file is more than its content.** A 20 MB model checkpoint file *contains* the model's actual parameter data — but the filesystem also tracks information *about* that file, separate from the content itself:

| Metadata field | What it describes |
|---|---|
| Filename | The name used to refer to this file within its directory |
| Size | How much data the file's content occupies |
| Timestamps | When the file was created, last modified, and/or last accessed (exact fields vary by filesystem — Section 9 shows this concretely) |
| Ownership | Which user (and group) the filesystem considers this file to belong to |
| Permissions | Rules governing who may read, write, or execute this file — previewed here, the full subject of the next lesson |
| File type | Whether this is a regular file, a directory, or another kind of filesystem object |
| Inode identity | An internal reference identifying this specific file within the filesystem (next subsection) |

**Content vs. metadata, stated precisely:** the model's actual 20 MB of parameter data is the file's *content*; its size, timestamps, ownership, and permissions are its *metadata* — information the filesystem maintains *about* the file, not part of the file's own data. **Not every metadata field described here is guaranteed to exist, or behave identically, on every filesystem type** — this lesson deliberately avoids claiming a universal, complete list.

### Inodes, at a foundational conceptual level

**Inode.** Simple meaning: an internal record the filesystem keeps for each file, holding its metadata and pointing to where its actual data lives — separate from the file's name. Technical meaning: an inode is a data structure used by many Unix-like filesystems to store a file's metadata and references to its actual data blocks; the filename itself is not the inode, but is instead associated with an inode through a directory entry.

```text
filename
   │
   ▼
directory entry           (the association between a name and an inode, kept inside
                             the containing directory)
   │
   ▼
inode                      (metadata + references to where the data actually is)
   │
   ▼
file data
```

**Why "filename is not simply the inode" matters:** a directory doesn't literally contain file data — it contains a mapping of names to inodes. This is *why*, on filesystems that support it, the same file's data can be referenced by more than one name (a detail this lesson does not explore further) — the name and the underlying file identity are genuinely separate concepts.

**Important caveats:**

- **This diagram is a simplified conceptual model, not a complete or universal filesystem implementation.** The exact way metadata and data references are structured differs meaningfully between filesystem types (ext4, and others this lesson does not name or compare).
- **This lesson does not teach detailed inode layouts** — only that this separation (name → association → metadata/data-reference structure → actual data) exists conceptually, and that it's the reason "a file's name" and "a file's identity" are not exactly the same thing.

### Filesystem vs. storage device

```text
Storage device
     ↓
Partition / storage structure
     ↓
Filesystem
     ↓
Directories and files
     ↓
Application
```

At a conceptual level: a storage device provides raw capacity; that capacity may be divided into partitions (this lesson does not teach partition-table internals); a filesystem is then set up on top of a given partition (or the whole device) to organize that raw space into the directories and files applications actually work with. Each layer exists specifically so the layer above it doesn't need to understand the layer below's raw details — an application works with files and paths, never with raw storage blocks directly (Section 2).

### Mounting

**Mount point.** Simple meaning: a directory that acts as the "entry point" for a filesystem, making its contents accessible through the regular directory structure. Technical meaning: mounting is the process by which a filesystem (on a particular storage device or partition) is attached to a specific directory in the overall filesystem hierarchy, so that navigating into that directory transparently accesses that filesystem's contents.

```text
/
├── home
├── var
└── data      ← mount point
```

If a separate filesystem is mounted at `/data`, then navigating into `/data` transparently accesses that other filesystem's files — from an application's point of view, it looks like just another directory, even though the actual data may be on an entirely different physical device or filesystem type.

**Why filesystems are mounted this way:** it lets a single, unified directory hierarchy present data that's actually spread across multiple physical devices or filesystem types, without applications needing to know or care about that underlying complexity — another instance of the same abstraction principle from Section 2.

**Genuinely observed illustration**, captured directly from this environment (Section 9 shows the full context):

```text
/dev/sdd on / type ext4 (rw,relatime,discard,errors=remount-ro,data=ordered)
C:\ on /mnt/c type 9p (rw,noatime,aname=drvfs;path=C:\;uid=1000;gid=1000,...)
```

The root filesystem (`/`) is genuinely mounted from `/dev/sdd`, using the `ext4` filesystem type; `/mnt/c` is a *separate* mount, using an entirely different filesystem type (`9p`, a network-style filesystem protocol, configured here with `drvfs` — WSL2's specific mechanism for bridging to a Windows drive). **This is a real, concrete demonstration that two different directories in the same hierarchy can be backed by two genuinely different filesystem types at once** — exactly the kind of implementation variation this lesson deliberately avoids papering over.

**This lesson does not teach advanced mount namespaces, bind mounts, overlay filesystems, or container storage internals** — all genuinely more advanced topics built on top of this foundational mounting concept.

---

## 6. How It Works Internally

### Processes and filesystem access

A running process interacts with the filesystem through the same kind of kernel-mediated mechanism Concept 02 already introduced in general, applied here specifically to files:

```text
Python process
      │
      │  system call            (Concept 02 — the controlled boundary crossing)
      ▼
Operating system
      │
      ▼
Filesystem                       (this lesson)
      │
      ▼
Storage
```

A process can, through this mechanism: **open** a file, **read** from it, **write** to it, **create** a new file, **delete** a file, and access (list, navigate) a directory. Each of these is, underneath, a request that crosses the user/kernel boundary exactly as Concept 02 described in general — this lesson does not re-teach system-call mechanics (syscall numbers, arguments, the trap mechanism) in detail; it only applies that already-established model specifically to filesystem operations.

### Filesystem data and virtual memory

Connecting directly to [Virtual Memory](06-virtual-memory.md): files live in **persistent storage**, while a running process works with data in its **virtual address space** — two genuinely different things this lesson keeps carefully distinct:

```text
Persistent file data                    Process memory
(lives on storage, survives              (lives in the process's virtual address
 process/machine restarts)                space, exists only while running)
```

**How these two connect:** when a process reads a file, its content is typically brought into the process's memory to be worked with (via the read system call, Concept 02). Additionally, operating systems provide a mechanism — **memory mapping** — by which a file's contents can be made to appear directly within a process's virtual address space (Concept 06), so that accessing that memory transparently reads (or writes) the underlying file, without an explicit read/write call for every access. **This lesson introduces this only at the foundational conceptual level.** It does not teach the detailed implementation of `mmap()`, nor the operating system's page-cache mechanism (which keeps recently-used file data cached in memory for performance) in any depth — both are meaningfully more advanced topics than this lesson's scope.

**The one distinction worth holding onto precisely:** a file's data, sitting in persistent storage, and that same data once it's been read into a process's memory, are related but not identical — the file persists independent of any process; the in-memory copy exists only as long as the process holds it (and only as current as the last time it was read or written back).

---

## 7. Real-World Example

| Example | What's happening | Filesystem concept involved |
|---|---|---|
| A Python script reads `config.json` at startup | The process opens a file by path, reads its content into memory | Path resolution, file open/read (Section 6) |
| An AI service loads a model checkpoint from disk | A large file's content is read (or memory-mapped) into the process's memory | File content vs. metadata (Section 5), filesystem-to-memory connection (Section 6) |
| A data pipeline reads a dataset from `data/train.csv` | A relative path is resolved against the process's current working directory | Absolute vs. relative paths (Section 5), Section 11's Scenario C |
| A logging system appends new lines to a log file over time | The file's size grows; metadata (size, modified timestamp) changes with every write | File metadata (Section 5) |
| A background worker writes temporary files to `/tmp` | Files are created in a location conventionally used for short-lived data | Linux filesystem hierarchy (Section 5) |
| A service checks available disk space before writing a large output | The filesystem's overall capacity, not any single file, is the relevant constraint | Filesystem vs. storage device (Section 5), Section 9's `df -h` |
| A learner inspects a running Python process via `/proc/<PID>/status` | Paths are used to navigate kernel-exposed information, not real persistent files | `/proc` as a virtual filesystem (Section 5) |
| A model-serving machine's disk fills up from accumulated logs | The filesystem runs out of free capacity, independent of any single application's own memory usage | Filesystem capacity (Section 9), Section 11's Scenario B |
| Two different scripts refer to the same dataset using different-looking paths | One might use an absolute path, the other a relative path — both can correctly resolve to the same file | Absolute vs. relative paths (Section 5) |
| A container or Windows drive is made accessible under `/mnt/c` in WSL2 | A separate filesystem, of a different type, is mounted into the directory hierarchy | Mounting (Section 5), Section 9's genuinely observed example |

---

## 8. Relationships to Other Concepts

```text
Storage
   ↓
Filesystem
   ↓
Directories / Files
   ↓
Paths
   ↓
Application access
```

```text
Python Process
      ↓
System Call
      ↓
Operating System
      ↓
Filesystem
      ↓
Persistent Storage
```

```text
Process                              Process
   ↓                                    ↓
Virtual Address Space                File Access
   ↓                                    ↓
Memory                                Filesystem
                                         ↓
                                       Storage
```

```text
Filesystem
   ↓
Permissions                    (the very next lesson — previewed only, not taught here)
```

| Concept | Relationship to filesystems | Prerequisite or later? | Full treatment |
|---|---|---|---|
| Kernel and User Space | The kernel implements and manages the filesystem; applications access it only through the kernel | Prerequisite (Concept 01) | Already covered |
| System Calls | File operations (open, read, write, create, delete) are requested via system calls (Section 6) | Prerequisite (Concept 02) | Already covered |
| Processes | A process's current working directory (Section 5) determines how its relative paths resolve | Prerequisite (Concept 03) | Already covered |
| Threads | Threads within a process generally share the same view of the filesystem, including open file descriptors, as part of shared process resources | Prerequisite (Concept 04) | Already covered |
| Scheduling | Independent of filesystem structure, though file I/O commonly causes the runnable/waiting transitions Concept 05 described | Prerequisite (Concept 05) | Already covered |
| Virtual Memory | Files can be memory-mapped into a process's address space (Section 6); file content and process memory remain distinct concepts | Prerequisite (Concept 06) | Already covered |
| Permissions | Governs who may read/write/execute a given file — previewed in Section 5's metadata table, not taught in depth here | Later | Concept 08 |
| Environment Variables | Can hold configuration such as file paths a program should use | Later | Concept 09 |
| Signals | Independent of filesystem structure | Later | Concept 10 |
| Standard Input/Output | A process's standard streams can be redirected to and from files — connecting filesystem access to I/O concepts | Later | Concept 11 |
| Pipes | A different, non-file-backed kernel-managed channel, conceptually adjacent to files but distinct | Later | Concept 12 |
| Shell | Provides the everyday commands (`ls`, `cd`, `pwd`, and more) used to navigate the filesystem interactively | Later | Concept 13 |
| Process Lifecycle | A process's working directory and open files are established at creation and released at termination | Later | Concept 14 |

---

## 9. Practical Observation / Commands

You are working in Ubuntu inside WSL2. All commands below are safe, read-only (except creating and cleaning up one small, isolated demonstration directory), and require no `sudo`. No system configuration, permissions on existing files, or unrelated data is touched anywhere in this lesson. **WSL2 caveat, stated once, applying throughout:** WSL2 is a virtualized Linux environment — some filesystem observations reflect this virtualized Linux environment specifically, and, as this section demonstrates directly with genuinely observed output, some directories bridge into the Windows host's own drives through a distinct mounting mechanism.

### `pwd` — current working directory

```bash
pwd
```

**What it shows:** the process's current working directory — the location relative paths are resolved against (Section 5). Every relative path a running script uses depends entirely on this value at the moment it runs.

**Observed in this environment**, from inside a demonstration directory created specifically for this lesson:

```text
/tmp/claude-1000/.../scratchpad/fs-demo
```

(the full path has been shortened here for readability; the point is that `pwd` reported exactly the directory this demonstration was working in — directly confirming Section 5's absolute-path concept with a real, current value, not an example.)

### `ls` and `ls -la` — directory contents

```bash
ls
ls -la
```

**Observed in this environment**, inside the same demonstration directory (created with a small `app/` folder, a `data/` folder, and a `README.md` file, purely for this observation):

```text
total 0
drwxr-xr-x 4 sovon sovon 100 Sep 10 14:58 .
drwx------ 3 sovon sovon  60 Sep 10 14:58 ..
-rw-r--r-- 1 sovon sovon   0 Sep 10 14:58 README.md
drwxr-xr-x 2 sovon sovon  60 Sep 10 14:58 app
drwxr-xr-x 2 sovon sovon  60 Sep 10 14:58 data
```

**What to look for:** `ls -la` (the `-l` flag for a detailed listing, `-a` to include hidden entries and the `.`/`..` self/parent-directory references) shows, for each entry: type and permission string (the leading `d` on `app`/`data` marks them as directories, `-` marks `README.md` as a regular file — Section 5's file-type metadata, directly observed), owner and group, size, last-modified timestamp, and name. This is Section 5's metadata table, made concrete with real, current values.

### `stat` — detailed file metadata

```bash
stat data/train.csv
```

**Observed in this environment:**

```text
  File: data/train.csv
  size: 22        	Blocks: 8          IO Block: 4096   regular file
Device: 0,75	Inode: 223         Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/   sovon)   Gid: ( 1000/   sovon)
Access: 2026-09-10 14:58:38.186487441 +0000
Modify: 2026-09-10 14:58:38.186487441 +0000
Change: 2026-09-10 14:58:38.186487441 +0000
 Birth: 2026-09-10 14:58:38.186487441 +0000
```

**What to look for, matching directly to Section 5's concepts:** `size` (22 bytes — this file's content size); `Inode: 223` (a real, directly observed inode number — Section 5's "Inodes" subsection made concrete); `Access:` permission string and `Uid`/`Gid` (ownership); and four separate timestamp fields (`Access`, `Modify`, `Change`, `Birth`) — a genuinely observed illustration that "timestamps" is not necessarily just one single field, and that the exact set of timestamp fields a filesystem exposes is filesystem-dependent (Section 5's caveat about not overstating universal metadata fields). **Only report the fields your own `stat` output actually shows — do not assume every filesystem or every `stat` implementation displays identical fields.**

### `file` — determining actual file type

```bash
file app/main.py
file data/train.csv
file app
```

**Observed in this environment:**

```text
app/main.py: ASCII text
data/train.csv: ASCII text
app: directory
```

**What to look for:** the `file` command inspects a file's actual content to report its real type, rather than trusting its name or extension. Both `main.py` and `train.csv` were correctly identified as `ASCII text` — genuinely determined from their content, not merely assumed from their `.py`/`.csv` extensions. **This reinforces a foundational point from Module 0.1: a filename extension is a naming convention for humans (and some tools), not a guarantee of a file's actual type** — a file could be renamed with any extension and `file` would still report what it actually contains.

### `df -h` — filesystem capacity

```bash
df -h <path>
```

**Observed in this environment**, for the filesystem holding the demonstration directory, and separately for the WSL2/Windows-bridging mount:

```text
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           1.9G  500K  1.9G   1% /tmp

Filesystem      Size  Used Avail Use% Mounted on
C:\             193G   75G  118G  39% /mnt/c
```

**What to look for:** `df -h` reports capacity **for the entire filesystem a given path lives on** — `Size`, `Used`, `Avail`, `Use%`, and the `Mounted on` directory. Notice these are two genuinely different filesystems (`tmpfs`, a memory-backed temporary filesystem, versus the much larger `C:\` Windows-drive-backed mount) with completely independent capacity — filling one up has no direct effect on the other's available space, a direct, observed instance of Section 5's mounting concept.

### `du -sh` — directory/file disk usage

```bash
du -sh <path>
du -sh <path>/*
```

**Observed in this environment:**

```text
8.0K    fs-demo
0       fs-demo/README.md
4.0K    fs-demo/app
4.0K    fs-demo/data
```

**The distinction this demonstrates directly:** `df -h` answers "how much space is available on this entire filesystem?" while `du -sh` answers "how much space does this specific file or directory actually use?" — two genuinely different, commonly confused questions. Note also that `README.md`, despite being an empty (0-byte) file, still occupies a minimum block of actual disk space when its directory entry is included in `du`'s reporting for the parent — a small, concrete illustration that a filesystem's actual space usage isn't always a perfectly literal byte-for-byte reflection of file content size alone.

### `mount` — currently mounted filesystems

```bash
mount | grep -E " / | /mnt/c "
```

**Observed in this environment:**

```text
/dev/sdd on / type ext4 (rw,relatime,discard,errors=remount-ro,data=ordered)
C:\ on /mnt/c type 9p (rw,noatime,aname=drvfs;path=C:\;uid=1000;gid=1000,...)
```

**What this demonstrates, concretely, about WSL2:** the root filesystem (`/`) is a genuine Linux filesystem (`ext4`) on a virtual block device (`/dev/sdd`) that WSL2 provides; `/mnt/c` is an entirely different filesystem type (`9p`, with WSL2's `drvfs` mechanism) bridging into the Windows host's actual `C:\` drive. **This is a real, observed example of WSL2's Windows-drive integration**, not a hypothetical — and it directly demonstrates why WSL2 is not identical to a bare-metal Linux installation: a bare-metal Linux machine would not typically have anything resembling `/mnt/c` at all. `ls -d /mnt/*` in this environment also showed `/mnt/c`, `/mnt/d`, `/mnt/wsl`, and `/mnt/wslg` — **your own WSL2 environment's specific mounts will likely differ** (different drive letters, different additional mounts) depending on your own machine's configuration; this lesson does not claim every WSL2 installation has identical mounts.

### Cleanup

The demonstration directory used throughout this section was created specifically for this lesson and removed immediately after these observations were captured:

```bash
rm -rf fs-demo
ls -d fs-demo   # confirms removal
```

**Observed in this environment:** `ls: cannot access 'fs-demo': No such file or directory` — confirming complete cleanup, with no files left behind and no project directory ever used as the demonstration location.

---

## 10. Common Misconceptions

| Misconception | Why it's wrong |
|---|---|
| "A filesystem is the same thing as a hard drive." | A hard drive (or other storage device) is physical hardware; a filesystem is the organizational software layer built on top of it (Section 1). |
| "A file is just its filename." | A file consists of content plus separately tracked metadata (Section 5); its filename is only one small piece — and, via inodes (Section 5), even the name itself is a separate association layered on top of the file's actual identity. |
| "The file extension determines the actual file type." | An extension is a naming convention; a file's real type is determined by its actual content, as Section 9's genuinely observed `file` command output demonstrated directly. |
| "Every Linux filesystem has exactly the same internal implementation." | Filesystem implementation varies by type (Section 5) — this lesson deliberately avoids describing any one implementation as universal, and Section 9's genuinely observed `mount` output showed two different filesystem types (`ext4`, `9p`) in the very same environment. |
| "`/proc` stores normal persistent files." | `/proc` is a virtual filesystem generated live by the kernel, exposing kernel/process information — nothing under it is actually stored on disk (Section 5). |
| "A directory contains file data directly." | A directory contains associations between names and inodes (directory entries) — the actual file data lives separately, referenced through the inode (Section 5). |
| "An absolute path and relative path are interchangeable." | A relative path's meaning depends entirely on the current working directory; the same relative path can resolve to different actual locations depending on where a program is run from (Section 5). |
| "A file's size is all of its metadata." | Size is only one metadata field among several — timestamps, ownership, permissions, and file type are all separate metadata, as Section 9's genuinely observed `stat` output showed directly. |
| "A process stores all its data permanently in files." | A process's in-memory data (its virtual address space, Concept 06) is separate from persistent file data; only data explicitly written to a file actually persists (Section 6). |
| "Storage and RAM are the same thing." | Storage is persistent (survives power-off); RAM is volatile working memory (Module 0.1, Concept 06) — this lesson's entire premise depends on this distinction being clear. |
| "If a file exists, any process can automatically access it." | Access is governed by permissions, a related but separate system from filesystem structure (Section 5's metadata table previews this; the next lesson, [Permissions](08-permissions.md), covers it fully). |
| "Mounting means copying a filesystem into a directory." | Mounting makes a filesystem's *existing* contents accessible through a directory — it does not copy or duplicate any data (Section 5). |
| "Deleting a filename always means the underlying data is immediately physically erased." | Deletion generally removes the name's association (the directory entry) with its inode; what happens to the underlying data afterward is filesystem- and situation-dependent, and this lesson deliberately does not make universal claims about the exact physical outcome — only that "the name is gone" and "the data is instantly, physically erased" are not necessarily the same event. |

---

## 11. Debugging and Troubleshooting

Each scenario follows: problem, beginner's likely assumption, correct mental model, investigation approach, and expected conclusion.

**Scenario A — `FileNotFoundError`.**

1. *Problem:* a Python program reports `FileNotFoundError` when trying to open a file.
2. *Beginner's likely assumption:* "The file must not exist, or my code has a bug."
3. *Correct mental model:* a `FileNotFoundError` means the *exact path used* didn't resolve to an existing file — which can happen for several distinct, common reasons, most of them not code bugs at all.
4. *Investigation approach*, as a systematic sequence:

```text
1. Check the current working directory:      pwd
2. Inspect the expected directory's contents: ls
3. Check the exact path used in the code, character by character
4. Check filename spelling and capitalization (Linux filenames are case-sensitive)
5. Determine whether the path used is absolute or relative (Section 5)
6. Confirm the file actually exists at the resolved location
```

5. *Expected conclusion:* most `FileNotFoundError` cases trace back to one of: wrong working directory, an incorrect relative path, a spelling/capitalization mismatch, or a genuinely missing file — working through the six-step sequence above, in order, reliably narrows down which one it is.

**A brief, related note — `Permission denied`.** This is a *different* kind of failure from `FileNotFoundError`: the file exists and was found, but access to it was refused. Permissions are a related but distinct system from filesystem structure (Section 5's metadata table previews this). **This lesson explains only that conceptual relationship — the full mechanics of Linux permissions are the dedicated subject of the very next lesson, [Permissions](08-permissions.md).**

**Scenario B — Disk full.**

1. *Problem:* a model-serving machine reports `No space left on device`.
2. *Beginner's likely assumption:* "The application must have a bug that's using too much memory."
3. *Correct mental model:* this is a filesystem *capacity* problem (Section 9), not a process memory problem (Concept 06) — an entirely different resource, even though the error can feel similarly alarming.
4. *Investigation approach:* check overall filesystem capacity with `df -h` (Section 9) to confirm which filesystem is actually full, then use `du -sh` on likely large directories (logs, model artifacts, cached data) to identify what's consuming the space.
5. *Expected conclusion:* disk-full errors are filesystem-capacity problems, diagnosed with `df -h` and `du -sh` together — `df -h` tells you *that* a filesystem is full and *which one*; `du -sh` helps you find *what* is filling it.

**Scenario C — Unexpected dataset location (relative-path behavior).**

1. *Problem:* a data-processing script works correctly when run from one directory, but fails when run from another.
2. *Beginner's likely assumption:* "The dataset file must have been moved or deleted."
3. *Correct mental model:* this is very likely Section 5's relative-path behavior — the exact same relative path resolves to a different actual location depending on the current working directory the script happens to be launched from.
4. *Investigation approach:* check `pwd` at the moment the script is run in each case, and manually resolve the relative path against each working directory to see where it actually points.
5. *Expected conclusion:* "works from one directory, fails from another, same code" is a strong, specific signature of a relative-path problem — not file corruption or a missing dataset.

**Scenario D — Large model artifact.**

1. *Problem:* a model checkpoint file occupies significant disk space, and a learner is unsure how this relates to the process's memory usage.
2. *Beginner's likely assumption:* "A large file on disk means the process must be using that much memory too."
3. *Correct mental model:* a file's size on disk (filesystem capacity, this lesson) and a process's memory usage (Concept 06) are genuinely separate measurements — a large file can sit on disk without ever being memory-mapped or read into memory, and conversely, how a process reads and uses that file's content in memory is governed by Concept 06's virtual memory concepts, not this lesson's filesystem concepts.
4. *Investigation approach:* use `du -sh` or `stat` (Section 9) to measure the file's actual disk footprint, separately from `ps`/`/proc/<PID>/status` (Concept 06) to measure the process's actual memory usage — treat them as two different questions.
5. *Expected conclusion:* disk space and process memory are related in practice (a process typically does need to read a model file to use it) but are measured, and can be constrained, entirely independently.

**Scenario E — Misunderstanding `/proc`.**

1. *Problem:* a learner sees files under `/proc` and assumes they are ordinary, persistent files, perhaps worth backing up or expecting to survive a reboot.
2. *Beginner's likely assumption:* "These are regular files, just like anything else under `/home` or `/var`."
3. *Correct mental model:* `/proc` is a **virtual filesystem** — its contents are generated live by the kernel, in memory, each time they're read (Section 5, and Concept 02's original introduction of `/proc`), not stored on any physical device at all.
4. *Investigation approach:* consider whether a given path's contents change from moment to moment in a way ordinary persistent files wouldn't (for example, `/proc/<PID>/status`'s memory figures changing as a process runs) — this behavior is a strong signal of a virtual, kernel-generated filesystem rather than genuine persistent storage.
5. *Expected conclusion:* treating `/proc` entries as something to preserve, back up, or expect to survive a reboot reflects a misunderstanding of what they actually are — they are a live window into kernel state, not stored data.

---

## 12. Exercises

Work through these in your own words. No answer key exists for this lesson — the goal is reasoning ability, not matching a memorized phrase.

### Level 1 — Recognition

1. What is a filesystem, in your own words?
2. What is the difference between a storage device and a filesystem?
3. What is a file? What is a directory?
4. What is a path?
5. What is the difference between an absolute path and a relative path?
6. What is file metadata? Name three examples.
7. What is an inode, at the level this lesson introduced it?
8. What is a mount point?

### Level 2 — Understanding

9. Explain, in your own words, why applications shouldn't have to manage raw storage blocks directly.
10. Explain why a relative path can resolve to two different actual locations depending on how a program is run.
11. Explain why `/proc` is described as a "virtual filesystem" rather than ordinary persistent storage.
12. Explain the difference between a file's content and its metadata, using your own example.
13. Explain why a filename is not simply "the file itself," using the inode concept.
14. Explain why mounting does not involve copying data.
15. Explain the difference between filesystem capacity (`df`) and directory-level usage (`du`).
16. Explain why "every Linux filesystem works identically" is an inaccurate generalization.

### Level 3 — Application

17. Given the path `/home/user/projects/ai-app/config.json`, identify the filename, the immediate parent directory, and the root directory.
18. Given a directory tree with `project/app/main.py`, `project/data/train.csv`, and `project/README.md`, write the path to each file relative to `project/`.
19. Run `pwd` in your own WSL2 terminal, then create a small file with a relative path and confirm (with `ls`) that it was created where you expected.
20. Run `stat` on a file you created. Identify its reported size and at least two timestamp fields.
21. Run `file` on two files with different extensions but similar plain-text content. Explain what the output tells you about how file type is actually determined.
22. Run `df -h` on your own home directory's path. Identify the filesystem's total size, used space, and available space.
23. Run `du -sh` on a small directory you created. Explain the difference between what this command and `df -h` each measure.
24. A Python script uses `open("config.json")` and is launched two different ways: once from `/home/user/project`, once from `/home/user`. Predict what happens in each case, assuming `config.json` only exists inside `/home/user/project`.

### Level 4 — Debugging

25. A Python program raises `FileNotFoundError`. Using Scenario A's six-step method, describe how you'd investigate it, in order.
26. A model-serving machine reports `No space left on device`. Using Scenario B, explain how `df -h` and `du -sh` play different, complementary roles in diagnosing it.
27. A data-processing script works from one directory but fails from another, with no code changes. Using Scenario C, explain the most likely cause.
28. A learner assumes a large model checkpoint file on disk means the serving process must be using that much memory right now. Using Scenario D, explain why this assumption may be wrong.
29. A learner treats files under `/proc` as something worth backing up. Using Scenario E, explain why this reflects a misunderstanding.
30. A learner sees `Permission denied` and assumes it means the same thing as `FileNotFoundError`. Explain why these are different categories of failure.
31. A learner renames `data.txt` to `data.csv` without changing its actual content, and assumes the file is now genuinely CSV-formatted. Using Section 9's `file` command observation, explain why this assumption is incorrect.
32. A learner concludes that because `ls` shows a file, any process on the system must automatically be able to read it. Using Section 10's misconceptions, explain what's missing from this conclusion.

### Level 5 — Integration

33. Draw (in text/ASCII) the path data takes when a Python AI service starts, reads a configuration file, and then reads a model checkpoint — labeling each step as process, system call, filesystem, or storage, using Section 6's diagram as your model.
34. Design a filesystem layout for a small AI inference service that needs: application code, configuration, logs, temporary files, model artifacts, input documents, and outputs. Explain your reasoning for how you organized these into directories — not just a list of folder names, but *why* you grouped things the way you did (for example, why logs might belong somewhere different from model artifacts).
35. A production AI service's disk usage grows steadily every day, and the team isn't sure whether it's the model artifacts, the logs, or something else. Using Section 9's `du -sh` observation, describe a reasoned, non-destructive investigation process to find out.
36. Explain how this lesson's filesystem model, Concept 06's virtual memory model, and Concept 02's system-call model together explain what actually happens, end-to-end, when a Python script calls `open("model.bin", "rb").read()`.
37. A friend claims, "Since my AI service's model loads fine every time I test it locally, the file path must be fine in production too." Using Section 5's absolute-vs-relative-path distinction and Section 11's Scenario C, explain why this reasoning could still fail in production, and what you'd want to verify.

---

## 13. Expected Results

**Expected conceptual results — these should hold regardless of your specific machine:**

- Correctly distinguish a storage device from a filesystem, and a file from its metadata, in your own words.
- Correctly resolve both absolute and relative paths given a working directory and a directory tree.
- Explain why `/proc` is not ordinary persistent storage.
- Explain what a mount point is and why two different filesystem types can coexist in one directory hierarchy.
- Correctly identify, for several of this lesson's thirteen misconceptions, why each is wrong and what the accurate idea is instead.

**What the practical observations should generally demonstrate, regardless of the exact values:**

- `ls -la` should show a permission/type string, owner, group, size, and timestamp for every entry, including the special `.`/`..` entries.
- `stat` should report a size, an inode number, ownership, and one or more timestamp fields for any file you inspect.
- `file` should correctly identify a plain-text file's type regardless of its extension.
- `df -h` and `du -sh` should report *different* numbers when checked against the same directory, because they measure genuinely different things (filesystem-wide capacity vs. this-specific-directory's usage).
- If your environment is WSL2, `mount` should show your root filesystem as one filesystem type, and — if you have Windows-drive integration configured — any `/mnt/<drive>` mount as a distinctly different filesystem type.

**Possible environment-dependent results — these will vary by machine and are expected to vary:**

- The exact inode number, timestamps, ownership, and file sizes you observe will differ from this lesson's actual observed values (inode `223`, and the rest) — these are never predictable or reproducible across machines or runs.
- Your own filesystem capacity figures (`df -h`) will differ entirely from this lesson's actual observed values (`tmpfs` at `1.9G`, `/mnt/c` at `193G`) depending on your own disk configuration.
- Whether you have `/mnt/c`, `/mnt/d`, or any other Windows-drive mounts depends entirely on your own WSL2 configuration — this lesson's environment happened to have `/mnt/c`, `/mnt/d`, `/mnt/wsl`, and `/mnt/wslg`; yours may differ.
- The specific timestamp fields your own `stat` output shows may differ depending on your filesystem type — this lesson's environment showed `Access`, `Modify`, `Change`, and `Birth`; not every filesystem type exposes all four.

---

## 14. Review Questions

Answers are intentionally not provided directly below these questions.

### Foundational knowledge

- What is a filesystem?
- What is the difference between storage and a filesystem?
- What is a file? What is a directory?
- What is a path?
- What is metadata?
- What is an inode, at the level this lesson introduced it?
- What is mounting?

### Reasoning

- What is the difference between an absolute path and a relative path, and why does that difference matter for a running program?
- What is the difference between a filesystem and RAM?
- What is the difference between a file's content and its metadata?

### OS relationships

- **What is the full path from a process wanting to read a file to that data actually being retrieved from storage?** Walk through every layer.
- How does a process's current working directory affect how it accesses files?
- How does virtual memory relate to file-backed data, at the conceptual level this lesson introduced?

### Practical Linux

- What does `pwd` show, and why does it matter for relative paths?
- What is the difference between what `ls -la` and `stat` each reveal about a file?
- Why does `file` sometimes disagree with what a filename's extension suggests?
- What is the difference between what `df -h` and `du -sh` each measure?
- Why did this lesson's `mount` observation show two different filesystem types in the same environment?
- Why is `/proc` a filesystem in name but not in the same sense as `/home`?

### AI engineering

- Why do datasets, model checkpoints, and logs all depend on the filesystem concepts in this lesson?
- Why can a full disk cause an AI service to fail, even if the service's own process memory usage looks completely normal?
- Why might a script that "works on my machine" fail in a production environment purely because of path handling, even with identical code?

---

## 15. Production Relevance

At this point, you understand what a filesystem is, how files and directories are organized and named, the difference between absolute and relative paths, the Linux filesystem hierarchy's common purposes, what file metadata and inodes are, how mounting works conceptually, and how filesystems relate to processes and virtual memory. You are not yet expected to know detailed permission mechanics, the shell's file-manipulation commands, or the complete process lifecycle — those remain the next several lessons.

For a production Applied AI Engineer, this lesson's mental model shows up constantly:

- **Python backend and AI inference services.** Every configuration file, every model artifact, every log line depends on the filesystem concepts this lesson introduced — path resolution, metadata, and capacity all directly shape whether a service starts and keeps running correctly.
- **Model artifacts and datasets.** Understanding file size versus process memory (Section 11, Scenario D) is essential for correctly reasoning about a model-serving machine's actual resource constraints.
- **Logs.** Unbounded log growth is a classic, entirely filesystem-capacity-driven production failure mode (Section 11, Scenario B) — recognizing `df -h`/`du -sh` as the right diagnostic tools is a direct, practical skill.
- **Temporary files and cache directories.** Understanding conventional locations (`/tmp`, Section 5) and their expected lifetime (often cleared on reboot) prevents relying on them for anything that actually needs to persist.
- **Generated outputs.** Experiment outputs, evaluation results, and other generated artifacts all depend on correct path handling to be findable and reproducible later.
- **Disk capacity.** A "disk full" failure is a distinct category from a memory-related failure (Concept 06) — correctly diagnosing which one you're facing determines which tools and which fix are relevant.
- **Filesystem failures and startup dependencies.** A service that depends on a configuration file or model artifact existing at a specific path will fail at startup if that path is wrong — a category of failure this lesson's Scenario A and Scenario C directly prepare you to diagnose.
- **Path configuration across deployment environments.** A path that resolves correctly in local development can resolve differently (or not at all) in a production or container environment with a different working directory — exactly Section 5's and Scenario C's core lesson, now at production stakes.
- **Reproducibility.** Correctly and consistently organizing datasets, code, configuration, and outputs (Exercise 34's design exercise) is foundational to being able to reliably reproduce results later.

**Realistic production failure modes this lesson directly prepares you to reason about:** a missing configuration file at startup, an incorrect working directory in a deployment environment, a missing model artifact, a full disk, unexpected log growth, temporary-storage exhaustion, an incorrect mount path, and — previewed here, fully covered next — permission-related access failures.

**Where this lesson stops, deliberately.** This lesson does not teach container volumes, Kubernetes persistent volumes, cloud object storage, distributed filesystems, or storage orchestration — each is a genuinely important, later-roadmap topic, built directly on top of the single-machine filesystem foundation this lesson establishes. Trying to reason about a container's storage volumes without first understanding what a filesystem, a path, and a mount point actually are would be building on nothing.

**What comes next**, building directly on this lesson:

```text
Filesystems                     ← this lesson
  → Permissions                  (the full mechanics behind who may access a file)
  → Environment Variables         (often used to configure file paths)
  → Signals                        (independent of filesystem structure)
  → Standard Input/Output            (streams that can be redirected to and from files)
  → Pipes                             (a different, non-file-backed kernel channel)
  → Shell                              (the everyday interface for navigating the filesystem)
  → Process Lifecycle                   (when a process's working directory and open
                                          files are established and released)
```

None of these are taught here — this section exists only to show where this lesson sits within the larger Module 0.2 sequence you are building, one concept at a time.

---

_This file is the completed lesson for Concept 07 of Module 0.2. It intentionally does not teach filesystem kernel source code, block-device internals, disk-controller internals, partition-table implementation, RAID, LVM, filesystem journaling internals, ext4/XFS/Btrfs/ZFS internal data structures, advanced inode allocation, page-cache internals, VFS kernel implementation, overlayfs internals, mount namespaces, container storage internals, Kubernetes volumes, distributed filesystems, NFS, Ceph, object storage internals, filesystem performance engineering, storage benchmarking, filesystem forensics, or disk recovery in depth — those remain the subject of later, more advanced curriculum, not this beginner-level foundation._
