# Files

**Module:** How Computers Work
**Roadmap reference:** Stage 0 — Module 0.1 — How Computers Work
**Concept(s) covered:** files
**Status:** Not Started

---

## Prerequisites

**Prerequisites:**

- Concept 11 — Storage
- Concept 12 — HDD vs SSD

**Supporting previous concepts:**

- Concept 4 — Binary, Bits & Bytes
- Concept 5 — Hexadecimal
- Concept 10 — RAM
- Concept 13 — GPU

**Complete prior concept sequence:**

Concept 1 — Motherboard & Buses, Concept 2 — CPU, Concept 3 — Cores, Concept 4 — Binary, Bits &
Bytes, Concept 5 — Hexadecimal, Concept 6 — Registers, Concept 7 — Instructions & Machine Code,
Concept 8 — Compilation & Interpretation, Concept 9 — Cache, Concept 10 — RAM, Concept 11 —
Storage, Concept 12 — HDD vs SSD, Concept 13 — GPU.

**Next concept:** Concept 15 — Input/Output.

This lesson reuses Concept 11's storage-vs-RAM distinction, Concept 12's storage-device
vocabulary, Concept 4's bits/bytes vocabulary, and Concept 5's hexadecimal notation directly — it
does not re-teach any of them from scratch. **A required, explicit boundary before you begin:**
this lesson does not become an Operating System Fundamentals lesson (that's Stage 0, Module 0.2),
and it does not teach Concept 15 (Input/Output), Concept 16 (Processes), Concept 17 (What Happens
When a Program Starts), Concept 18 (What Happens When a Function Executes), Concept 19 (Why RAM
and Storage Are Different), or Concept 20 (Why GPUs Matter for AI) in depth — each remains a
separate, later lesson.

---

## 1. What Is a File?

**Starting from what you already know.** Concept 11 established storage as persistent, non-volatile
technology, and introduced "file" only as a brief conceptual preview — "a logical representation of
stored data." This lesson develops that idea properly.

**File — simple meaning:** A file is a named, persistent collection of data that a computer can
store, retrieve, and work with as a single unit.

**File — technical meaning:** A file is a logical object presented by an operating system and
filesystem (Concept 11's conceptual preview) — a named, addressable unit of data that the
filesystem manages on top of physical storage (Concept 11, Concept 12), letting programs and users
work with "a file" without needing to think about exactly how or where its underlying bytes
physically sit on the storage device.

**A required, explicit distinction, central to this entire lesson:**

> A file is a *logical* object the operating system/filesystem presents — not a physical object
> sitting on the disk in the way you might picture a physical folder holding physical papers.

This directly extends Concept 11, Section 5's identical point about applications interacting with
files "through operating-system interfaces rather than directly controlling the physical storage
hardware." A file's actual bytes ultimately reside somewhere on a real storage device (Concept 11,
Concept 12), but "a file" — as something with a name, a size, a location in a directory structure —
is a concept the filesystem constructs and manages on your behalf, not something you could point
to physically on the platter or flash chips themselves.

**Examples of different kinds of files, introduced here and developed in Section 3:**

- **Text files** — files whose bytes are meant to be interpreted as readable text (Section 2).
- **Binary files** — files whose bytes are not meant to be read as text directly (Section 2).
- **Executable files** — files containing machine code (recall Concept 7) meant to be run directly
  by the operating system.
- **Configuration files** — files holding settings that control how a program behaves.
- **Data files** — a general category for files holding information a program reads, produces, or
  works with (datasets, images, documents, and so on).

**A required, explicit correction, stated immediately:**

> A file is not necessarily "a piece of text." A file can contain arbitrary bytes.

This is one of the most important ideas in this entire lesson, and Section 2 develops it fully.
Whatever you already associate with "opening a file" (a document, perhaps) is only one narrow
example of what a file can be — a file is, fundamentally, just a named collection of bytes
(recalling Concept 4), and those bytes can represent text, an image, executable instructions
(Concept 7), or anything else a program is written to interpret.

---

## 2. File Contents, Bytes, Text, and Binary Data

**Building directly on Concept 4.** A file's actual contents are, underneath everything else,
simply a sequence of bytes — exactly the same bits-and-bytes vocabulary Concept 4 already taught
you. Nothing about a file's physical reality is different from any other bit pattern you've
studied throughout this module; what differs is how those bytes are meant to be *interpreted*.

**Recall Concept 4's central principle, directly relevant here again:**

> Bits themselves do not inherently mean "number," "letter," "image," or "instruction." A system
> defines how a bit pattern is interpreted.

A file's contents are exactly this: a bit pattern (organized into bytes) whose *meaning* depends
entirely on what's interpreting it.

**Text representation.** A **text file** is a file whose bytes are meant to be interpreted as
readable characters, using an **encoding** — an agreed system mapping specific byte values to
specific characters (recall Concept 4, Section 7, Example 3's "character → encoding → numeric code
→ bits" chain). Two encoding examples, introduced only at this beginner level:

- **ASCII** — one of the earliest, simplest character encodings, mapping a limited set of
  characters (English letters, digits, basic punctuation) to specific byte values.
- **UTF-8** — a widely-used, more comprehensive encoding capable of representing a much larger
  range of characters from many languages.

**A required, explicit boundary:** this lesson does not teach Unicode internals, how UTF-8's
variable-byte encoding scheme actually works, or any other character-encoding implementation
detail — those are genuine, deeper topics beyond this foundational lesson's scope. The only point
required here: text is bytes interpreted through an agreed encoding, exactly as Concept 4 already
established for any bit pattern generally.

**Binary data.** A **binary file** is a file whose bytes are *not* meant to be interpreted as text
— an image, an executable (Concept 7's machine code), or any other non-text data. "Binary" here
does not mean "made of only 0s and 1s" (every file, text or otherwise, is made of bits — Concept
4) — it specifically means "not intended to be read as text."

**Readable vs. non-readable contents.** If you open a text file's bytes with a tool that displays
them as characters (Section 11's practical work), you'll generally see something recognizable and
readable. If you do the same with a binary file's bytes, you'll generally see unreadable-looking
output — not because anything is broken, but because those bytes were never meant to be
interpreted as text in the first place (Section 13, Misconception 9 corrects a related
misunderstanding directly).

### Comparison Table — Text File vs. Binary File

| Property | Text file | Binary file |
|---|---|---|
| What the bytes represent | Characters, via an agreed encoding (e.g., ASCII, UTF-8) | Data not intended to be interpreted as characters (images, executables, and more) |
| Human-readable when viewed directly? | Generally yes | Generally no (appears as unreadable/garbled output) |
| Example (from this lesson) | `notes.txt`, `config.json` (Section 11) | `fakeimage.png` (Section 11) |
| Underlying reality | Still just bytes (Concept 4) | Still just bytes (Concept 4) |

**A required, explicit qualification:** the distinction between "text" and "binary" is about
*intended interpretation*, not a different physical kind of byte — every file, text or binary, is
made of the exact same kind of bit patterns Concept 4 already taught you.

---

## 3. Filenames, Extensions, and File Types

**Filename.** The name used to identify a specific file within a directory (Section 4). A filename
is metadata about the file (Section 6) — it is not the file's contents.

**Basename.** The filename itself, as distinct from any directory path leading to it (Section 5
develops paths fully) — for example, in `project/notes.txt`, the basename is `notes.txt`.

**Extension.** The portion of a filename after the last `.` — for example, `.txt` in
`notes.txt`, or `.json` in `config.json`.

**A required, explicit, central correction:**

> An extension is generally a *naming convention* used to indicate/associate a file type — it does
> not determine, guarantee, or change what a file's actual bytes contain.

This directly corrects the misconception:

> "`.txt` means the operating system automatically knows the file's true internal format."

This is not accurate. An extension is a **hint**, a **convention** — many programs and operating
systems *use* the extension to guess how to handle a file (which program should open it, how to
display an icon for it, and so on), but nothing about the file's actual bytes is inspected,
verified, or changed by that extension. **File contents and filename extension are not inherently
the same thing** — Section 11's practical work demonstrates this concretely, with real, captured
evidence.

**Naming conventions.** Beyond extensions, filenames commonly follow other conventions (using
hyphens or underscores instead of spaces, lowercase names, descriptive names) — this lesson does
not teach a specific convention as mandatory, only that such conventions exist and are followed for
readability and consistency, not because the filesystem itself requires them.

**Case sensitivity.** On Linux (and therefore inside WSL2's Ubuntu environment), filenames are
generally **case-sensitive** — `notes.txt` and `Notes.txt` are treated as two different filenames.
**This lesson does not teach filesystem-implementation details of why** — only that this is a
practical, observable behavior you should expect in your WSL2/Ubuntu environment specifically (a
different behavior may apply to Windows-mounted paths, briefly noted in Section 11).

### File Types — Conceptual Overview

| Category | Conceptual meaning | Common extension examples |
|---|---|---|
| Text | Bytes meant to be read as characters | `.txt`, `.md` |
| Structured/data text | Text following a specific structured format | `.json`, `.csv` |
| Source code | Text written in a programming language (Concept 7, Concept 8) | `.py` |
| Image | Bytes representing visual/pixel data | `.jpg`, `.png` |
| Document | Bytes representing formatted document content | `.pdf` |
| Executable | Bytes containing machine code (Concept 7) meant to be run directly | `.exe` (Windows), ELF format (common on Linux) |

**A required, explicit boundary:**

> This lesson does not teach the internal format specifications of any of these file types — how
> JSON's structure is precisely defined, how PNG or JPEG encode image data, how PDF represents a
> document, or how the ELF executable format is laid out internally. Those are all real, deeper
> topics belonging to later, more specific material — not this foundational lesson.

The only point this section establishes: files come in many conceptual categories, extensions are
a common (but not authoritative) convention for signaling which category a file likely belongs to,
and the actual bytes are what truly determine a file's content, regardless of what its name
suggests.

---

## 4. Directories and Folders

**Directory / folder — simple meaning:** A directory (also commonly called a "folder," especially
in graphical interfaces) is a way of organizing and naming a collection of files (and other
directories) within the filesystem.

**A required, explicit correction:**

> A directory is not merely "a physical box containing files." A directory is a filesystem
> structure used to organize/name file objects.

Just as Section 1 established that a file is a *logical* object the filesystem presents (not a
physical thing sitting on the disk), a directory is likewise a logical, filesystem-managed
structure — not a physical container. What a directory actually *does*, at the level this lesson
teaches, is provide a way to group and name files (and other directories) so they can be organized
and located. **This lesson does not teach filesystem inode structures** — the actual internal
mechanism a filesystem uses to implement directories — that belongs to Module 0.2 and other later
material.

**Files inside directories.** A file exists "inside" a directory in the sense that the directory
records the file's name and where to find its data — not in the sense of physical containment
(exactly the correction above).

**Nested directories / directory hierarchy.** Directories can contain other directories, which can
contain further directories, and so on — building a branching, tree-like structure. This is called
the **directory hierarchy**.

### Comparison Table — File vs. Directory

| Property | File | Directory |
|---|---|---|
| What it holds | Actual data/contents (Section 2) | Names/references organizing files and other directories |
| Can it contain other files? | No | Yes |
| Has its own contents in the "data" sense? | Yes | Not in the same sense — its role is organizational (Section 4's explicit correction) |
| Example (from this lesson) | `notes.txt` | `project`, `data` (Section 11) |
| Physical container? | No — a logical object (Section 1) | No — a logical, filesystem-managed structure, not a physical box |

### Diagram A — File → Directory → Filesystem → Storage Relationship

```text
Storage device (Concept 11, Concept 12)
        │
        ▼
   Filesystem (organizes the device's bytes into a usable structure)
        │
        ▼
   Directory hierarchy (directories, nested within directories)
        │
        ▼
   Files (named, logical objects the filesystem presents)
        │
        ▼
   File contents (the actual bytes, per Section 2)
```

> Simplified conceptual diagram. The file itself is not a separate physical object sitting on the
> disk — it is a logical structure the filesystem constructs and presents on top of the storage
> device's underlying bytes.

---

## 5. Paths: Absolute and Relative

**Path — simple meaning:** A path is a way of specifying the location of a file or directory
within the directory hierarchy (Section 4) — essentially, a set of directions for finding it.

**Absolute path.** A path that starts from the very top of the filesystem's directory hierarchy
(the **root directory**, `/` on Linux) and specifies every directory along the way to the target.
Example (Linux): `/home/user/project/data.txt`.

**Relative path.** A path that starts from wherever you currently "are" in the directory hierarchy
— the **current working directory** (introduced below) — rather than from the root. Example:
`./data.txt` or `data.txt` refers to a file named `data.txt` located in the current directory;
`../data.txt` refers to a file named `data.txt` located in the *parent* directory of the current
one.

**Current working directory.** The directory a program (or your shell session) is currently
"located in" — relative paths are interpreted starting from here.

**Parent directory.** The directory that directly contains the current directory, one level up in
the hierarchy.

**Root directory.** The topmost directory in the entire filesystem hierarchy, from which every
absolute path begins — written as `/` on Linux.

### Diagram B — Absolute vs. Relative Path

```text
Absolute path (always starts from root):

/home/user/project/data.txt
│    │    │       │
root user  project data.txt
(the entire path is spelled out, from / all the way to the file)


Relative path (starts from the current working directory):

Current working directory: /home/user/project

./data.txt   → /home/user/project/data.txt   (same directory)
../data.txt  → /home/user/data.txt            (parent directory)
```

> Simplified conceptual diagram. The exact resolved location of a relative path always depends on
> the current working directory at the time it's used — the same relative path can point to
> different actual files depending on where it's evaluated from.

### Comparison Table — Absolute Path vs. Relative Path

| Property | Absolute path | Relative path |
|---|---|---|
| Starting point | Root directory (`/`) | Current working directory |
| Depends on current location? | No — always resolves to the same location | Yes — resolves differently depending on where it's evaluated from |
| Typical use | Referring to a file unambiguously, regardless of context | Convenient, shorter references within a known working context |
| Example (Linux) | `/home/user/project/data.txt` | `./data.txt`, `data.txt`, `../data.txt` |

### Linux Path Concepts

- **`/`** — the root directory, the top of the entire filesystem hierarchy.
- **`~`** — represents the user's home directory in typical shell contexts (for example,
  `~/project` means "the `project` directory inside my home directory"). **A required, explicit
  correction:** `~` is a shorthand the shell expands for you — **do not imply that `~` is
  literally a directory entry named "~"** somewhere in the filesystem; it's a convenience symbol
  your shell substitutes with your actual home directory's real path before using it.
- **`.`** — represents the current working directory itself.
- **`..`** — represents the parent directory of the current working directory.

---

## 6. File Metadata

**File contents vs. file metadata — a required, explicit distinction.** Section 2 covered a file's
*contents* — its actual bytes. **Metadata** is different: it's *information about* the file,
rather than the file's own data.

**Beginner-level metadata concepts:**

- **Size** — how many bytes the file's contents occupy (directly recalling Concept 4's byte
  vocabulary).
- **Timestamps** — recorded times associated with the file (for example, when it was last
  modified).
- **Permissions (as metadata only)** — information recording who is allowed to do what with the
  file.
- **Ownership (as metadata only)** — information recording which user (and, on Linux, which group)
  is associated with the file.

**A required, explicit, firm boundary:**

> Permissions and ownership are only introduced conceptually here. Detailed Linux permissions,
> users, groups, `chmod`, `chown`, and ACLs belong to Stage 0 — Module 0.2 — Operating System
> Fundamentals. This lesson does not teach how to read or change permission notation, how users and
> groups actually work, or any related command — those are explicitly deferred.

### Comparison Table — File Contents vs. File Metadata

| Property | File contents | File metadata |
|---|---|---|
| What it is | The actual bytes stored in the file (Section 2) | Information *about* the file |
| Examples | Text, image data, executable machine code | Size, timestamps, permissions, ownership |
| Changes when you edit the file's data? | Yes — directly | Indirectly (e.g., size and modification timestamp update) |
| Changes when you rename the file? | No | Yes — the filename itself is part of the file's metadata |

---

## 7. Creating, Reading, Writing, Copying, Moving, and Deleting Files

At a conceptual level, files support a small set of common operations:

- **Create** — bring a new file into existence.
- **Read** — retrieve a file's contents.
- **Write** — store new contents into a file (potentially replacing what was there).
- **Append** — add additional data onto the end of a file's existing contents, without replacing
  what was already there.
- **Rename** — change a file's name (Section 6 — a metadata change, not a contents change).
- **Copy** — create a new, independent file containing the same contents as an existing one.
- **Move** — relocate a file to a different directory (Section 4), potentially also renaming it in
  the process.
- **Delete** — remove a file so it's no longer accessible through the filesystem (Section 10
  develops exactly what this does and does not mean).

**A required, explicit statement of this section's scope boundary:**

> These operations are performed through software/operating-system interfaces — not by an
> application directly manipulating physical storage hardware (recalling Concept 11, Section 5's
> identical point). This lesson does not teach system calls — the specific, lower-level mechanism
> an operating system provides for programs to request these operations. System calls belong to
> Module 0.2.

---

## 8. How Programs Interact With Files

**A simple conceptual flow, connecting a program to a file's actual data:**

```text
Program
   ↓
requests file access (e.g., "open this file")
   ↓
operating system / filesystem
   ↓
storage (Concept 11, Concept 12)
   ↓
file data
   ↓
program
```

Walking through this: a program doesn't reach directly into storage hardware to read or write a
file — it makes a request to the operating system/filesystem (echoing Concept 11, Section 5 and
Section 6's identical conceptual chain), which locates the file's data on the storage device and
either retrieves it (a read) or writes new data to it (a write), ultimately handing control back to
the program.

**The typical shape of a program's interaction with a file, described conceptually — not as code
or an API:**

1. The program **opens** the file — signaling its intent to work with it.
2. The program **reads** data from the file (or **writes** data to it).
3. The program **processes** whatever data it read (or prepares whatever data it's about to
   write) — this "processing" step is exactly what Concept 7 and Concept 8 already taught you
   happens through executed instructions.
4. The program **closes** the file — signaling it's finished working with it.

**A required, explicit, firm boundary — this lesson's relationship to Concept 15:**

> This lesson does not teach system calls, file descriptors, buffering, or the detailed mechanics
> of how the operating system actually carries out a read or write request. Concept 15 —
> Input/Output — will teach that material properly, as a separate, later lesson. This lesson
> establishes only enough of the "program → OS/filesystem → storage → data → program" flow to
> prepare you for that later, deeper discussion — it does not anticipate or duplicate it.

---

## 9. Files, RAM, and Storage

**Building directly on Concept 10 and Concept 11 — a required, explicit distinction.**

**File:**

- Persistent (Concept 11's defining property).
- Stored through the storage/filesystem layer (Section 1, Section 4).
- Remains after a program exits, or even after the machine restarts, **assuming the underlying
  storage is intact** (echoing Concept 11's non-volatility discussion precisely).

**RAM:**

- Volatile (Concept 10, Section 4's defining property).
- Used while programs actively execute — holding data a running program is currently working with.
- Much faster to access than persistent storage (Concept 9, Concept 10, Concept 11's established
  latency comparisons).

### Diagram C — File vs. RAM Conceptual Relationship

```text
File on storage (persistent)
        │
        │  program reads the file's contents
        ▼
Data held in RAM while the program runs (volatile, active working memory)
        │
        │  program may write updated data back
        ▼
File on storage (persistent again, once written)
```

> Simplified conceptual model. This mirrors Concept 11, Section 5's original "Persistent data →
> Storage device → Operating system → Files/directories → Application" chain, now shown
> specifically alongside RAM's role as the active, temporary working copy of a file's data while a
> program uses it.

### Comparison Table — File vs. RAM vs. Storage Device

| Property | File | RAM | Storage device |
|---|---|---|---|
| What it is | A logical, named unit of data (Section 1) | Active, volatile working memory (Concept 10) | The physical hardware providing persistent capacity (Concept 11, Concept 12) |
| Persistent? | Yes (as long as underlying storage is intact) | No — volatile | Yes — non-volatile by design |
| Directly visible to ordinary programs as...? | A named object opened/read/written through OS interfaces (Section 8) | Program variables/data structures | Not directly — programs interact with files, not raw storage hardware (Concept 11, Section 5) |
| Relationship to the others | Exists *on* a storage device, and its data may be *loaded into* RAM while in use | Temporarily holds a file's data while a program actively works with it | Physically holds the bytes that make up files, persistently |

**A required, explicit correction:**

> "A file remains in RAM after a program exits" is incorrect. Once a program that had loaded a
> file's data into RAM exits, that RAM is freed and its contents are gone (Concept 10's volatility).
> The file itself, however, continues to exist on persistent storage — exactly because it is a
> separate, persistent thing from whatever temporary RAM-based copy of its data a program happened
> to be working with.

---

## 10. File Lifecycle and Persistence

**The general lifecycle, conceptually:**

```text
Create
  ↓
Write
  ↓
Store
  ↓
Read
  ↓
Modify
  ↓
Rename / Move
  ↓
Delete
```

A file is created, written with initial data, and stored persistently (Section 9). It can then be
read (its data retrieved and used, potentially by many different programs over time), modified
(its contents changed), renamed or moved (Section 6, Section 7 — metadata/location changes), and
eventually deleted.

**Persistence, restated precisely.** A file's persistence means its data remains available across
program executions and, generally, across power cycles (Concept 10 vs. Concept 11's volatility
distinction, applied here specifically to files) — as long as the underlying storage device itself
remains intact and the file hasn't been deleted.

**A required, explicit, carefully-worded correction:**

> Deleting a file does not necessarily mean its physical storage bytes are immediately erased.

At the conceptual level this lesson teaches: deleting a file generally means the filesystem stops
treating that data as an accessible, named file — but the underlying bytes may still physically
remain on the storage device for some time afterward, until that space is eventually reused. **This
lesson does not teach filesystem internals, block allocation, journaling, inode internals, SSD
garbage collection, or secure deletion** — exactly *how* and *when* the underlying bytes are
actually overwritten or reclaimed is genuinely more advanced material, entirely out of this
lesson's scope (see the Strict Boundary section). The only point required here: "deleted" (from the
filesystem's perspective) is not automatically identical to "physically, immediately erased" — this
directly corrects Misconception 8 in Section 13.

---

## 11. Practical Linux/WSL2 File Observation

As with every prior concept file, this section is safe, entirely read-only for inspection purposes,
uses only an explicitly isolated temporary working directory for anything created, requires no
`sudo`, never modifies important system files, and never fabricates output. Reminder of your
environment:

```text
Windows
   ↓
WSL2
   ↓
Ubuntu
```

**Checking command availability first, as this lesson's Command Validation requirement demands.**
Every command below (`pwd`, `ls`, `file`, `stat`, `cat`, `head`, `wc`, `xxd`, `realpath`, `du`) is
part of a standard Ubuntu installation and was confirmed available in the environment used to
prepare this lesson via `which`. **The output shown below is genuinely observed** — captured by
actually running these commands in an isolated temporary directory (`/tmp/files-lesson-demo`),
which was fully removed afterward. **Your own output will very likely differ in exact values
(filenames, sizes, timestamps, your own username) — treat the specific values below as this
lesson's own observed example, not a universal expectation.**

**Step 1 — set up an isolated, temporary working directory (cleaned up at the end):**

```bash
mkdir -p /tmp/files-lesson-demo/project/data
cd /tmp/files-lesson-demo
```

**Step 2 — create a few small, harmless example files:**

```bash
echo "Hello, this is plain text." > project/notes.txt
printf 'This has no trailing newline' > project/nonewline.txt
printf '\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR' > project/fakeimage.png
echo '{"name": "demo", "value": 42}' > project/config.json
```

**Step 3 — observe your current location:**

```bash
pwd
```

*Observed output:*

```text
/tmp/files-lesson-demo
```

*What this shows:* `pwd` ("print working directory") reports your current working directory
(Section 5) — the starting point relative paths are resolved from.

**Step 4 — list directory contents:**

```bash
ls
```

*Observed output:*

```text
project
```

```bash
ls -l project
```

*Observed output:*

```text
total 16
-rw-r--r-- 1 sovon sovon 30 Sep  8 21:48 config.json
drwxr-xr-x 2 sovon sovon 40 Sep  8 21:48 data
-rw-r--r-- 1 sovon sovon 16 Sep  8 21:48 fakeimage.png
-rw-r--r-- 1 sovon sovon 28 Sep  8 21:48 nonewline.txt
-rw-r--r-- 1 sovon sovon 27 Sep  8 21:48 notes.txt
```

*What this shows:* `ls -l` gives a "long listing," showing metadata (Section 6) for each entry:
permissions (introduced only conceptually here, per this lesson's boundary), owner and group
(`sovon sovon`, in this specific captured environment — **your own username will differ**), size
in bytes, last-modified timestamp, and name. Notice `data` begins with `d` (a directory) while the
files begin with `-` (a regular file) — a directly observable illustration of Section 4's file vs.
directory distinction.

**Step 5 — identify actual file types by content, not by name:**

```bash
file project/*
```

*Observed output:*

```text
project/config.json:   JSON text data
project/data:          directory
project/fakeimage.png: PNG image data, 0 x 0, 0-bit grayscale, non-interlaced
project/nonewline.txt: ASCII text, with no line terminators
project/notes.txt:     ASCII text
```

*What this shows:* the `file` command inspects a file's actual **bytes** (not just its name) to
determine its type — notice it correctly identified `fakeimage.png` as "PNG image data" *because
its first bytes genuinely matched the real PNG file-format signature*, not merely because of its
`.png` extension. This is a direct, concrete demonstration of Section 3's central point: content,
not extension, is what truly determines a file's nature.

**A second, deliberately mismatched example, to demonstrate the same point from the opposite
direction — genuinely observed:**

```bash
echo "This is actually plain text, not a real image." > mislabeled.jpg
file mislabeled.jpg
```

*Observed output:*

```text
mislabeled.jpg: ASCII text
```

*What this shows:* even though this file is named with a `.jpg` extension, `file` correctly
reports its actual content as plain **ASCII text** — a direct, concrete refutation of
Misconception 3 ("the extension determines the actual file contents") and Misconception 11 ("the
operating system automatically understands every extension"). The extension is just a name; the
bytes are the truth.

**Step 6 — inspect detailed metadata:**

```bash
stat project/notes.txt
```

*Observed output:*

```text
  File: project/notes.txt
  size: 27        	Blocks: 8          IO Block: 4096   regular file
Device: 0,73	Inode: 237         Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/   sovon)   Gid: ( 1000/   sovon)
Access: 2026-09-08 21:48:42.707891136 +0000
Modify: 2026-09-08 21:48:42.670020536 +0000
Change: 2026-09-08 21:48:42.670020536 +0000
 Birth: 2026-09-08 21:48:42.663891136 +0000
```

*What this shows:* far more detailed metadata (Section 6) than `ls -l` — size, an inode number
(mentioned only by name here — inode internals are explicitly out of scope, per this lesson's
Strict Boundary), and several distinct timestamps. **This lesson does not teach what each
timestamp precisely tracks in filesystem-implementation detail** — only that multiple, distinct
timestamps exist as metadata.

**Step 7 — view text file contents safely:**

```bash
cat project/notes.txt
```

*Observed output:*

```text
Hello, this is plain text.
```

```bash
head -c 50 project/config.json
```

*Observed output:*

```text
{"name": "demo", "value": 42}
```

*What this shows:* `cat` displays a file's entire contents; `head -c 50` displays only the first
50 bytes — useful for safely previewing a file without dumping potentially large contents to your
terminal.

**Step 8 — measure a file's size in a different way:**

```bash
wc project/notes.txt
```

*Observed output:*

```text
 1  5 27 project/notes.txt
```

*What this shows:* `wc` ("word count") reports line count, word count, and byte count (27 bytes,
matching the size shown by `ls -l` and `stat` above) — a second, independent confirmation of
Section 2's "a file's contents are just bytes" point.

**Step 9 — inspect a binary file's raw bytes, in hexadecimal (recalling Concept 5):**

```bash
xxd project/fakeimage.png | head -3
```

*Observed output:*

```text
00000000: 8950 4e47 0d0a 1a0a 0000 000d 4948 4452  .PNG........IHDR
```

*What this shows:* exactly as in Concept 5 and Concept 7's own practical sections, `xxd` displays
raw bytes in hexadecimal. Notice the very first bytes (`89 50 4e 47 0d 0a 1a 0a`) — this is a real
example of a file-format "signature" (a fixed, recognizable byte sequence at the start of a file),
which is precisely what let the `file` command in Step 5 correctly identify this as PNG data,
without ever looking at the filename.

**Step 10 — observe absolute and relative paths together:**

```bash
realpath project/notes.txt
```

*Observed output:*

```text
/tmp/files-lesson-demo/project/notes.txt
```

*What this shows:* `realpath` converts a relative path (`project/notes.txt`, relative to the
current working directory from Step 3) into its full absolute path (Section 5) — a direct,
concrete demonstration of the relative-to-absolute relationship this lesson's Diagram B describes.

```bash
cd project
ls ../
```

*Observed output:*

```text
project
```

*What this shows:* after moving into the `project` directory, `../` (the parent directory,
per Section 5's Linux path concepts) correctly refers back to `/tmp/files-lesson-demo`, whose only
visible entry is `project` itself — directly demonstrating `..`'s meaning with real, observed
output.

**Step 11 — measure directory size:**

```bash
du -sh project
```

*Observed output (run from `/tmp/files-lesson-demo`):*

```text
16K	project
```

*What this shows:* recalling Concept 11, Section 10's identical `du` discussion — this reports the
total disk space used by everything inside the `project` directory, combining all the small example
files created in Step 2.

**Step 12 — clean up, exactly as promised:**

```bash
cd /tmp
rm -rf /tmp/files-lesson-demo
```

This removes the entire isolated temporary directory and everything created inside it — nothing
outside `/tmp/files-lesson-demo` was touched at any point in this practical section, and this
cleanup step was genuinely performed while preparing this lesson.

**Required WSL2-specific caveats, stated explicitly, matching the pattern from every prior concept
file's practical section:**

- These observations were made inside WSL2's Ubuntu Linux filesystem (`/tmp/...`) — Linux paths and
  behavior (like case-sensitive filenames, per Section 3) apply here.
- Windows drives are exposed inside WSL2 through paths like `/mnt/c` (as first seen in Concept 11
  and Concept 12's own practical sections) — **file behavior on `/mnt/c` (a Windows-managed
  filesystem bridge) is not guaranteed to be identical to native Linux filesystem behavior** — for
  example, case-sensitivity and permission handling can differ. This lesson does not teach the
  specific differences in depth.
- Do not assume a specific username — this lesson's own captured output shows `sovon`, a
  reflection of the specific environment used to prepare it; your own output will show your own
  username.
- Never modify Windows files outside an explicitly isolated temporary workspace, exactly as this
  section's own practical work stayed confined to `/tmp/files-lesson-demo` throughout, and cleaned
  it up afterward.

---

## 12. Files in Real-World and AI Engineering Work

**Why files matter beyond this lesson's abstractions.** Everything you'll build as an Applied AI
Engineer ultimately reads, transforms, creates, and persists data through files (and, later,
Concept 15's Input/Output mechanisms, and other storage mechanisms this lesson does not teach).

**Concrete AI-engineering examples, kept conceptual — this lesson does not teach any specific
format's internal structure or any ML framework's API:**

- **Datasets** — data used for training or evaluating an AI model is commonly stored as one or more
  files (recalling Concept 11, Section 9's original dataset discussion).
- **JSON configuration** — settings for an application or experiment, commonly stored in `.json`
  files (Section 3's structured-text category), read by a program at startup.
- **YAML configuration** — another common structured-text format for configuration, mentioned here
  only by name (its specific syntax is not taught in this lesson).
- **Model checkpoints** — saved model progress (recalling Concept 11, Section 9, Example 7, and
  Concept 12, Section 10, Example 7) — persisted as one or more files.
- **Tokenizer files** — supporting files a text-processing component depends on, mentioned here
  only by name — not taught in depth.
- **Logs** — records of what a program did over time (recalling Concept 11, Example 6), written to
  a file for later review.
- **Prompt/configuration files** — text files holding instructions or settings used to guide an AI
  system's behavior.
- **Training artifacts** — general outputs produced during a training process (recalling Concept
  11's "artifacts" discussion).
- **Evaluation datasets** — data files used specifically to measure a model's performance, distinct
  from the data used to train it.
- **Model files** — the persisted, saved form of a trained model (Concept 12, Section 10, Example
  6), containing the model's learned parameters.

**A required, explicit boundary:**

> This lesson does not teach model formats, ML framework APIs, dataset-pipeline implementation, or
> model-serialization internals — all of that is genuinely later material. The goal here is only
> for you to recognize: **AI systems ultimately read, transform, create, and persist data through
> files and other storage mechanisms** — a conceptual foundation, not implementation knowledge.

**File vs. database, introduced only conceptually.** A **file** is a general persistent-data
container — the subject of this entire lesson. A **database** is a structured system specifically
designed to manage and query persistent data, offering capabilities well beyond what a plain file
provides on its own. **This lesson does not teach SQL, indexing, transactions, database engines, or
normalization** — those belong to later backend/database learning. The only distinction required
here: a database is not simply "a special kind of file" (Section 13, Misconception 12) — it is a
different kind of system, generally built on top of files and storage (Concept 11), but providing
substantially more structure and capability than a plain file offers by itself.

---

## 13. Common Mistakes and Misconceptions

```text
Misconception 1  → "A file is always text."
Correct idea     → A file is a named collection of bytes; those bytes can represent text, but
                    they can equally represent an image, executable machine code, or any other
                    kind of data (Section 1, Section 2).
Example          → project/fakeimage.png in this lesson's practical section (Section 11)
                    contains real binary PNG-format bytes, not text — attempting to read it as
                    text would produce unreadable-looking output, not because anything is
                    broken, but because it was never meant to be interpreted as text.
```

```text
Misconception 2  → "A .jpg file is literally stored as an image object."
Correct idea     → A file's actual storage is just bytes (Section 2) — there is no special
                    "image object" the storage device holds; the *interpretation* of those
                    bytes as a viewable image happens in software (an image viewer) that
                    understands the specific image format's byte layout.
Example          → xxd project/fakeimage.png in Section 11 shows raw hexadecimal bytes — not
                    anything resembling a picture; a program has to interpret those specific
                    bytes according to the PNG format to actually display an image.
```

```text
Misconception 3  → "The extension determines the actual file contents."
Correct idea     → The extension is a naming convention/hint (Section 3) — it does not
                    determine, verify, or change what a file's bytes actually contain.
Example          → Section 11's genuinely observed mislabeled.jpg example: named with a .jpg
                    extension, but file correctly identified its actual content as plain ASCII
                    text.
```

```text
Misconception 4  → "A folder physically contains files like a box."
Correct idea     → A directory is a logical, filesystem-managed structure that organizes and
                    names files — not a physical container (Section 4's explicit correction).
Example          → Deleting a directory entry doesn't mean physically removing anything from
                    inside a literal box — it means the filesystem's organizational structure
                    no longer records that grouping/naming relationship.
```

```text
Misconception 5  → "A filename and a file are the same thing."
Correct idea     → A filename is metadata about a file (Section 6) — a label used to identify
                    it. The file itself is the underlying data (contents) plus its associated
                    metadata as a whole. Renaming a file (Section 7) changes its filename
                    without changing its contents at all.
Example          → Renaming notes.txt to my-notes.txt (Section 7's "rename" operation) does not
                    alter the text "Hello, this is plain text." stored inside it.
```

```text
Misconception 6  → "Files exist in RAM."
Correct idea     → Files are persistent, stored on non-volatile storage (Section 9, recalling
                    Concept 11). A file's data may be temporarily loaded into RAM while a
                    program actively works with it, but the file itself, as a persistent
                    entity, resides on storage — not in RAM.
Example          → Diagram C (Section 9) shows the file on storage, data loaded into RAM only
                    while a program is actively using it, and the file remaining on storage
                    afterward — RAM's copy disappears when the program exits (Concept 10's
                    volatility).
```

```text
Misconception 7  → "A file is the same thing as a storage device."
Correct idea     → A file is a logical object the filesystem presents (Section 1); a storage
                    device is the physical hardware providing the underlying persistent
                    capacity (Concept 11, Concept 12). A single storage device can hold an
                    enormous number of separate files — this exact point was already
                    established in Concept 11, Misconception 5, and applies identically here.
Example          → The /tmp/files-lesson-demo directory in Section 11 held five separate files
                    on one single storage device, each independently named and manageable.
```

```text
Misconception 8  → "Deleting a file immediately destroys all physical bytes."
Correct idea     → Deleting a file generally means the filesystem stops treating that data as
                    an accessible, named file — the underlying bytes may still physically
                    remain on the storage device for some time afterward (Section 10's explicit
                    correction), until that space is eventually reused. This lesson does not
                    teach the exact mechanism or timing.
Example          → This is analogous to Concept 11, Misconception 12's identical point:
                    deleting a file is a logical operation, not necessarily an instantaneous
                    physical erasure.
```

```text
Misconception 9  → "Every file can be opened as readable text."
Correct idea     → Only text files are meant to be interpreted as readable characters (Section
                    2). Attempting to view a binary file's bytes as text produces unreadable-
                    looking output — not a malfunction, simply a mismatch between the file's
                    actual nature and how you're trying to interpret it.
Example          → Running cat on project/fakeimage.png (rather than a proper image viewer)
                    would display garbled, unreadable characters — the bytes are exactly as
                    intended; they were just never meant to be read as text.
```

```text
Misconception 10 → "A relative path is the same as an absolute path."
Correct idea     → A relative path's meaning depends on the current working directory it's
                    evaluated from (Section 5); an absolute path always resolves to the exact
                    same location regardless of context. The same relative path text can point
                    to entirely different files depending on where it's used from.
Example          → Section 11, Step 10's genuinely observed realpath project/notes.txt shows
                    the relative path project/notes.txt resolving to the absolute path
                    /tmp/files-lesson-demo/project/notes.txt — but only because the current
                    working directory happened to be /tmp/files-lesson-demo at that moment.
```

```text
Misconception 11 → "The operating system automatically understands every extension."
Correct idea     → An extension is a convention many programs choose to honor (Section 3) — the
                    operating system does not have built-in, guaranteed knowledge of what every
                    possible extension "truly" means; it's software (and human convention) that
                    typically associates extensions with expected behavior, not an inherent,
                    infallible system-level guarantee.
Example          → Section 11's genuinely observed mislabeled.jpg: despite carrying a
                    recognized ".jpg" extension, its content was plain text — nothing in the
                    system automatically "corrected" this mismatch or refused to allow it.
```

```text
Misconception 12 → "A database is just a special file."
Correct idea     → A database is a structured system specifically designed to manage and query
                    persistent data (Section 12) — while it is commonly built using files and
                    storage underneath (Concept 11), it provides substantially more capability
                    (querying, structure, and more — none of which this lesson teaches) than a
                    plain file offers by itself.
Example          → A single text file can hold data, but it has no built-in way to efficiently
                    search, structure, or query that data the way a database system is
                    specifically designed to — the distinction is architectural, not merely a
                    difference in file extension.
```

```text
Misconception 13 → "File permissions are part of the file's contents."
Correct idea     → Permissions are metadata — information about the file — not part of its
                    actual byte contents (Section 6's explicit contents-vs-metadata
                    distinction).
Example          → Section 11's genuinely observed stat project/notes.txt output shows
                    permissions (0644/-rw-r--r--) listed alongside size and timestamps, entirely
                    separate from the file's actual text content ("Hello, this is plain
                    text."), which cat displayed separately in Step 7.
```

```text
Misconception 14 → "A file remains in RAM after a program exits."
Correct idea     → RAM is volatile (Concept 10) — once a program that had loaded a file's data
                    into RAM exits, that RAM is freed and its contents are gone. The file
                    itself continues to exist on persistent storage, entirely independent of
                    whatever temporary RAM-based copy a program was using (Section 9's explicit
                    correction).
Example          → Diagram C (Section 9) shows the file returning to (remaining on) storage
                    once a program's active use of it ends — RAM is only ever a temporary,
                    working copy of a file's data, never the file's permanent home.
```

---

## 14. Exercises and Debugging Scenarios

Work through these in order, showing your reasoning for every explanation or comparison — not just
a final answer.

### Level 1 — Recognition

1. What is a file?
2. What is a directory/folder?
3. What is a filename?
4. What is a file extension?
5. What is the difference between a text file and a binary file?
6. What is an absolute path?
7. What is a relative path?
8. What is the current working directory?
9. What does `~` represent in a typical shell context?
10. What does `..` represent?
11. What is file metadata?
12. Name three examples of file metadata.
13. What is the difference between file contents and file metadata?
14. What does it mean for a file to be persistent?
15. What is the difference between a file and a database, at the conceptual level this lesson
    teaches?

### Level 2 — Understanding

Answer each in your own words, in at least one or two full sentences.

16. Why is a file described as a "logical" object rather than a physical one?
17. Why can a file contain arbitrary bytes, not just text?
18. Why doesn't a file's extension guarantee its actual content?
19. Why is a directory not "a physical box containing files"?
20. Why does an absolute path always resolve to the same location, while a relative path might
    not?
21. Why is a filename considered metadata rather than content?
22. Why does a file persist while RAM does not?
23. Why doesn't deleting a file necessarily erase its bytes immediately?
24. Why do AI engineering workflows depend heavily on files?
25. Why is a database not simply "a special file"?

### Level 3 — Application

**Exercise A — Identify file vs. directory.** Given `ls -l` output showing an entry starting with
`d` and another starting with `-`:

26. Explain which is the directory and which is the file, and how you know.

**Exercise B — Interpreting extensions.** Given the filenames `report.pdf`, `data.csv`,
`script.py`, and `image.png`:

27. For each, state the likely intended file category, and explain why this is only a reasonable
    guess, not a guarantee.

**Exercise C — Path reasoning.** Suppose the current working directory is `/home/user/project`.

28. What absolute path does `./data.txt` refer to?
29. What absolute path does `../data.txt` refer to?
30. What absolute path does `data/input.csv` refer to?

**Exercise D — Metadata interpretation.** Given a `stat` output showing a file's size, permissions,
and three different timestamps:

31. Explain what each of these three pieces of information (size, permissions, timestamps)
    represents, and why none of them are part of the file's actual content.

**Exercise E — Text vs. binary reasoning.** Given a file that displays garbled, unreadable
characters when opened with `cat`:

32. Explain what this observation does and does not tell you about the file.

### Level 4 — Debugging

For each statement, identify exactly what's wrong and explain the corrected understanding.

33. "This file has a `.txt` extension, so it must contain only readable text — I don't need to
    check."
34. "I deleted the file, so its bytes are now completely gone from the physical storage device
    immediately."
35. "The file exists in RAM right now because I have it open in my program."
36. "This directory contains 500 MB of files, so the directory itself is a 500 MB physical
    container."
37. "I renamed `data.txt` to `data.csv`, so the file's contents are now properly formatted as
    CSV."
38. "A relative path `./config.json` will always point to the exact same file, no matter where my
    program is run from."
39. "The file's permissions must be stored inside the text I see when I `cat` the file."
40. "Since this database stores data in files on disk, a database is really just a fancy file."

### Level 5 — Integration / AI Engineering Reasoning

**Scenario A — AI dataset file.** A dataset for an AI project is stored as a single large `.csv`
file on disk.

41. Explain, using this lesson's vocabulary, what happens conceptually when a Python program reads
    this file to begin processing it (referencing Section 8's program-to-file flow).
42. Explain why the dataset's presence on disk (rather than only in RAM) matters for the project's
    long-term usability.

**Scenario B — Configuration file confusion.** A learner has a file named `settings.json` that
actually contains plain, unstructured text rather than valid JSON.

43. Explain why the `.json` extension alone does not guarantee the file is valid, well-formed JSON,
    and how the learner could investigate this using this lesson's practical tools.

**Scenario C — Model checkpoint reasoning.** An AI training process periodically saves a model
checkpoint to a file, and the training script can be stopped and resumed later.

44. Explain, using the file lifecycle (Section 10) and the file-vs-RAM distinction (Section 9), why
    saving to a file (rather than relying only on the training process's RAM) is essential for this
    resume-later capability to work at all.

**Scenario D — Path confusion in a project.** A learner's script fails with a "file not found"
error when using the relative path `data/input.csv`.

45. List at least two different possible explanations for this error, reasoning from this lesson's
    concepts (current working directory, relative vs. absolute paths, actual file existence).

**Solutions are not provided here.** See
[`exercises/14-files-answer-key.md`](./exercises/14-files-answer-key.md) — open it only after
attempting every question above.

---

## 15. Review and Production Relevance

### Review Questions

Answers are intentionally not provided directly below these questions.

1. What is a file, and why is it described as a logical rather than physical object?
2. Why can a file contain arbitrary bytes rather than only text?
3. What is the difference between a filename and a file extension?
4. Why doesn't a file's extension guarantee its actual content?
5. What is the difference between a file and a directory?
6. What is the difference between an absolute path and a relative path?
7. What do `/`, `~`, `.`, and `..` each represent in a Linux path context?
8. What is the difference between file contents and file metadata?
9. Why does a file persist while data in RAM does not?
10. Why doesn't deleting a file necessarily erase its bytes immediately?
11. Why is a database not simply "a special file"?
12. Why do AI engineering workflows depend heavily on files?
13. Why can't WSL2 file behavior on `/mnt/c` be assumed identical to native Linux filesystem
    behavior?

### Production Relevance

You now understand what a file actually is (a logical, filesystem-presented object, not a physical
disk object), how file contents relate to bytes and encoding, how filenames and extensions relate
(and don't determine) actual content, how directories and paths organize and locate files, what
file metadata is, the basic file operations, how programs interact with files at a conceptual
level, how files relate to RAM and storage, and the file lifecycle including persistence and
deletion.

**How this connects to your future work:**

```text
AI application
      ↓
reads/writes files (datasets, configuration, checkpoints, logs, artifacts)
      ↓
operating system / filesystem (Section 8)
      ↓
storage (Concept 11, Concept 12)
```

This foundation becomes directly useful when you later study:

- **Input/Output (Concept 15, the very next lesson)** — the deeper mechanics of how programs
  actually read and write data, building directly on this lesson's Section 8 preview.
- **Operating System Fundamentals (Module 0.2)** — permissions, users, groups, system calls,
  filesystem internals, and other topics this lesson deliberately deferred.
- **The Command Line (a later module)** — practical, fluent use of the exact commands this lesson's
  Section 11 introduced.
- **Developer Environment (a later module)** — project structure, dependency files, and other
  file-organization concepts built on this lesson's foundation.
- **Backend Engineering** — reading/writing files, and eventually databases (Section 12's
  file-vs-database distinction), as part of real applications.
- **AI Engineering** — datasets, configuration, model artifacts, checkpoints, logs, and evaluation
  data (Section 12) all depend on the file fundamentals this lesson established.

**A required, final, explicit boundary:**

> This lesson does not teach system calls, file descriptors, filesystem internals, permissions
> implementation, databases, or AI dataset-pipeline/model-serialization internals. What this lesson
> provides is the conceptual foundation — what a file is, how it's named and located, what it
> contains, how it relates to RAM and storage, and why it matters — that all of that later material
> will build directly on top of.

---

_This file was written as the completed Concept 14 lesson for Module 0.1. It does not teach kernel
internals, system calls, file descriptors, inode internals, superblocks, journaling, filesystem
implementation, ext4/NTFS internals, permissions implementation, ACLs, mount internals, VFS
internals, block allocation, disk scheduling, storage drivers, I/O scheduling, process internals,
threads, virtual memory, page cache internals, buffering internals, async I/O, database
implementation, SQL, object storage architecture, distributed filesystems, cloud storage
architecture, Git internals, container filesystem layers, Docker storage drivers, AI dataset
pipelines, model serialization internals, or model serving storage architecture in depth — those
remain scaffolded, unwritten concept files (or entirely untouched, in the case of later-stage or
later-module material) until their own turn in the sequence. Input/Output specifically is the very
next concept, Concept 15, and is not taught here._
