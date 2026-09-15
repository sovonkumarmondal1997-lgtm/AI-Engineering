# Concept 14 — Files — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../14-files.md`](../14-files.md), Section 14. Attempt every question yourself first, with your
> own worked reasoning, before reading any answer below.

---

## Level 1 — Recognition

**1. What is a file?** A named, persistent collection of data — a logical object presented by the
operating system/filesystem, built on top of physical storage.

**2. What is a directory/folder?** A filesystem structure used to organize and name a collection
of files (and other directories) — not a physical container.

**3. What is a filename?** The name used to identify a specific file — metadata about the file, not
its contents.

**4. What is a file extension?** The portion of a filename after the last `.` — a naming
convention that hints at (but does not determine) the file's actual content.

**5. Text vs. binary file?** A text file's bytes are meant to be interpreted as readable characters
via an encoding (ASCII, UTF-8); a binary file's bytes are not meant to be read as text (images,
executables, etc.).

**6. Absolute path?** A path that starts from the root directory (`/`) and specifies the full
route to a file or directory, regardless of current location.

**7. Relative path?** A path interpreted starting from the current working directory, rather than
from the root.

**8. Current working directory?** The directory a program or shell session is currently "located
in" — the starting point for resolving relative paths.

**9. What does `~` represent?** The user's home directory, in typical shell contexts — a shorthand
the shell expands, not a literal directory entry named "~".

**10. What does `..` represent?** The parent directory of the current working directory.

**11. What is file metadata?** Information *about* a file (size, timestamps, permissions,
ownership), as distinct from the file's actual contents.

**12. Three examples of file metadata.** Size, timestamps, permissions (any three of: size,
timestamps, permissions, ownership).

**13. File contents vs. metadata?** Contents are the actual bytes stored in the file; metadata is
information describing the file (size, timestamps, permissions, etc.) without being part of the
data itself.

**14. What does persistence mean for a file?** The file's data remains available across program
executions and, generally, power cycles, as long as the underlying storage is intact.

**15. File vs. database?** A file is a general persistent-data container; a database is a
structured system specifically designed to manage and query persistent data, offering more
capability than a plain file.

---

## Level 2 — Understanding

**16. Why is a file described as "logical" rather than physical?** Because a file is a structure
the filesystem constructs and presents on top of a storage device's underlying bytes — you can't
physically point to "the file" itself on the platter/flash chips the way you could point to a
physical object; what physically exists is bytes, organized and presented as "a file" by the
filesystem.

**17. Why can a file contain arbitrary bytes, not just text?** Because a file is fundamentally just
a named sequence of bytes (Concept 4), and bytes can represent anything a program is written to
interpret them as — text is only one possible interpretation among many (images, executables,
etc.).

**18. Why doesn't a file's extension guarantee its actual content?** Because the extension is a
naming convention/hint that many programs choose to honor — it is not verified, enforced, or tied
to the file's actual bytes in any automatic way (Section 11's genuinely observed `mislabeled.jpg`
example demonstrates this directly).

**19. Why is a directory not "a physical box containing files"?** Because a directory is a logical,
filesystem-managed structure that records names/organization — files aren't physically "inside" it
the way objects sit inside a box; the directory is more like an organizational record than a
physical container.

**20. Why does an absolute path always resolve to the same location, while a relative path might
not?** Because an absolute path always starts from the fixed root directory (`/`), giving one
unambiguous location, while a relative path's meaning depends on the current working directory at
the time it's evaluated — the same relative path text can point to different actual locations
depending on context.

**21. Why is a filename considered metadata rather than content?** Because the filename describes
*information about* the file (how it's identified/labeled) rather than being part of the actual
data stored inside it — renaming a file doesn't change what's inside it.

**22. Why does a file persist while RAM does not?** Because a file is stored on non-volatile
storage (Concept 11), designed specifically to retain data without continuous power, while RAM is
volatile (Concept 10) and loses its contents when power is removed.

**23. Why doesn't deleting a file necessarily erase its bytes immediately?** Because "deleting," at
the filesystem level, generally means the filesystem stops treating the data as an accessible,
named file — the underlying physical bytes may remain on the storage device until that space is
later reused; the exact mechanism/timing is beyond this lesson's scope.

**24. Why do AI engineering workflows depend heavily on files?** Because datasets, configuration,
model checkpoints, logs, and other AI-project artifacts are all commonly stored, read, and
persisted as files — file fundamentals underlie nearly every practical AI engineering task.

**25. Why is a database not simply "a special file"?** Because a database is an entire structured
system providing capabilities (querying, structure, management) well beyond what a plain file
offers by itself — even though it may be built using files and storage underneath, the
architectural distinction is real, not merely a naming difference.

---

## Level 3 — Application

### Exercise A — File vs. directory in `ls -l` output

**26.** The entry beginning with `d` (e.g., `drwxr-xr-x`) is the directory; the entry beginning
with `-` (e.g., `-rw-r--r--`) is the regular file. This first character in the permissions field
indicates the entry type — `d` for directory, `-` for a regular file — exactly as seen in Section
11's genuinely observed `ls -l project` output, where `data` (a directory) begins with `d` and the
other entries (files) begin with `-`.

### Exercise B — Interpreting extensions

**27.**

- `report.pdf` — likely a document (Section 3's "Document" category).
- `data.csv` — likely structured/data text (Section 3's "Structured/data text" category).
- `script.py` — likely Python source code (Section 3's "Source code" category, recalling Concept 7
  and Concept 8).
- `image.png` — likely image data (Section 3's "Image" category).

Each is only a reasonable *guess* because the extension is a naming convention (Section 3), not a
guarantee — the actual bytes could contain anything, exactly as Section 11's genuinely observed
`mislabeled.jpg` example demonstrated (a `.jpg` file containing plain text).

### Exercise C — Path reasoning (current working directory: `/home/user/project`)

**28.** `./data.txt` → `/home/user/project/data.txt` (same directory).

**29.** `../data.txt` → `/home/user/data.txt` (parent directory).

**30.** `data/input.csv` → `/home/user/project/data/input.csv` (a subdirectory named `data` inside
the current directory).

### Exercise D — Metadata interpretation

**31.** **Size** represents how many bytes the file's contents occupy — a measure of the data's
volume, not the data itself. **Permissions** represent who is allowed to do what with the file
(introduced only conceptually here, per Section 6's explicit boundary) — access-control
information, not content. **Timestamps** represent recorded points in time associated with the
file (e.g., last modified) — historical/administrative information, not content. None of these are
part of the file's actual content because they describe *facts about* the file rather than *data
stored inside* it — exactly Section 6's contents-vs-metadata distinction, directly illustrated by
Section 11's genuinely observed `stat` output, which lists size/permissions/timestamps entirely
separately from the file's actual text (shown separately via `cat`).

### Exercise E — Text vs. binary reasoning

**32.** This observation tells you the file's bytes were not intended to be interpreted as
readable text (Section 2, Section 13 Misconception 9) — it does **not** tell you the file is
broken, corrupted, or unusable; it may be a perfectly valid binary file (an image, executable, or
other non-text data) simply being viewed with the wrong tool for its actual nature. The correct
next step would be to use a tool like `file` (Section 11) to determine its actual type, rather than
assuming something is wrong.

---

## Level 4 — Debugging

**33. "This file has a `.txt` extension, so it must contain only readable text — I don't need to
check."** Wrong: the extension is a naming convention, not a guarantee (Misconception 3,
Misconception 11) — the actual bytes could be anything; checking with a tool like `file` (Section
11) is the reliable way to know, not trusting the extension alone.

**34. "I deleted the file, so its bytes are now completely gone from the physical storage device
immediately."** Wrong: deleting generally means the filesystem stops treating the data as an
accessible file — the underlying bytes may still physically remain until that space is reused
(Section 10, Misconception 8).

**35. "The file exists in RAM right now because I have it open in my program."** Partially
correct but imprecisely stated: the file's *data* may be temporarily loaded into RAM while the
program actively works with it (Section 9's Diagram C), but the *file itself*, as a persistent
entity, continues to reside on storage — RAM only holds a temporary working copy, not the file's
permanent home (Misconception 6, Misconception 14).

**36. "This directory contains 500 MB of files, so the directory itself is a 500 MB physical
container."** Wrong: a directory is a logical, filesystem-managed organizational structure, not a
physical container (Misconception 4) — the 500 MB refers to the combined size of the files it
organizes, not a physical property of the directory structure itself.

**37. "I renamed `data.txt` to `data.csv`, so the file's contents are now properly formatted as
CSV."** Wrong: renaming changes the filename (metadata), not the file's actual contents
(Misconception 5, Section 7) — the underlying bytes remain exactly as they were; only the label
changed.

**38. "A relative path `./config.json` will always point to the exact same file, no matter where
my program is run from."** Wrong: a relative path's meaning depends on the current working
directory at the time it's evaluated (Misconception 10, Section 5) — running the same program from
a different directory can make `./config.json` resolve to a completely different (or nonexistent)
file.

**39. "The file's permissions must be stored inside the text I see when I `cat` the file."**
Wrong: permissions are metadata, entirely separate from the file's contents (Misconception 13,
Section 6) — `cat` displays only the contents; permissions are shown separately, by tools like
`ls -l` or `stat` (Section 11).

**40. "Since this database stores data in files on disk, a database is really just a fancy
file."** Wrong: a database is a structured system providing capabilities (querying, structure,
management) well beyond a plain file, even though it may be built using files/storage underneath
(Misconception 12, Section 12).

---

## Level 5 — Integration / AI Engineering Reasoning

### Scenario A — AI dataset file

**41.** Conceptually, following Section 8's flow: the Python program requests to open the `.csv`
file → the operating system/filesystem locates it on storage (Concept 11, Concept 12) → the
relevant data is read from storage → the data becomes available to the program (commonly loaded
into RAM, Section 9, as the program processes it) → the program can then work with (process) that
data. This is the same general "Program → OS/filesystem → storage → file data → program" chain
Section 8 established, applied concretely to a dataset file.

**42.** The dataset's presence on persistent storage (rather than only in RAM) matters because RAM
is volatile (Concept 10) — if the dataset only existed in RAM, it would be lost the moment the
program (or the machine) stopped running, requiring it to be re-obtained from scratch every time.
Storing it as a file on persistent storage means it remains available across program runs and
power cycles (Section 9, Section 10), making it genuinely reusable for the AI project over time.

### Scenario B — Configuration file confusion

**43.** The `.json` extension is only a naming convention/hint (Section 3, Misconception 3,
Misconception 11) — nothing about the filesystem or operating system verifies that a file named
`.json` actually contains valid JSON syntax. The learner could investigate using this lesson's
practical tools: running `file settings.json` (Section 11) to see how the content is actually
identified, or using `cat`/`head` to directly view the file's actual contents and check whether
they look like valid JSON structure, rather than trusting the extension alone.

### Scenario C — Model checkpoint reasoning

**44.** Using Section 10's file lifecycle and Section 9's file-vs-RAM distinction: if the training
process's progress only existed in RAM (volatile, Concept 10), stopping the training script (or
losing power) would completely lose all that progress, since RAM's contents disappear when the
program exits. Saving a checkpoint to a *file* makes that progress persistent (Section 9,
Section 10) — it survives the training script stopping, and a later run of the script can read
that checkpoint file back in (Section 8's program-to-file flow) to resume from where it left off.
This is precisely why persistence, not just RAM, is essential for a genuine "stop and resume later"
capability.

### Scenario D — Path confusion in a project

**45.** At least two plausible explanations, reasoning from this lesson's concepts: (1) The script
was run from a different **current working directory** than expected (Section 5) — since
`data/input.csv` is a relative path, it resolves differently depending on where the script is
actually executed from, and if run from the wrong location, the relative path would point to a
nonexistent location even if the file genuinely exists elsewhere. (2) The file **genuinely does not
exist** at the expected location at all — perhaps it was never created, was moved, was renamed
(Section 7), or was deleted (Section 10) — a straightforward absence rather than a path-resolution
issue. Distinguishing between these two explanations would typically involve checking the actual
current working directory (`pwd`, Section 11) and verifying the file's real location (e.g., with
`ls` or `realpath`, Section 11) rather than assuming the path text alone must be wrong.

---

_This answer key covers Concept 14 (Files) only. It does not contain, reference, or anticipate
answers for Concept 15 (Input/Output) or any later concept._
