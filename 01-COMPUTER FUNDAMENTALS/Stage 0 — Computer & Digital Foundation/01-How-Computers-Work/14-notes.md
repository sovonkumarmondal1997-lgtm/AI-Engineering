# Files

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 14

---

## 1. What Is a File?

A **file** is a named collection of data managed by the operating system and filesystem. It is a logical object, not a physical object sitting on a disk. Files can contain text, images, executable code, configuration, datasets, and other data.

---

## 2. File Contents, Types, and Extensions

Every file ultimately contains bytes. Their meaning depends on how software interprets them.

- **Text files:** Bytes interpreted as characters using an encoding such as ASCII or UTF-8.
- **Binary files:** Bytes intended for data such as images or executable code, rather than directly readable text.
- **Filename:** The name used to identify a filesystem object.
- **Extension:** A naming hint, such as `.txt`, `.json`, `.py`, `.png`, or `.pdf`.

An extension does not guarantee a file's real contents or validity. For example, a file named `settings.json` might contain invalid JSON, and a `.jpg` file might actually contain plain text.

---

## 3. Directories and Paths

A **directory** (folder) organizes files and other directories in a tree-like hierarchy. It is a logical filesystem structure, not a physical container.

Linux path basics:

- `/` — root directory.
- `~` — shell shorthand for the user's home directory.
- `.` — current working directory.
- `..` — parent directory.

An **absolute path**, such as `/home/user/project/data.txt`, starts at the root. A **relative path**, such as `data.txt` or `../data.txt`, depends on the current working directory. Linux filenames are generally case-sensitive, though behavior can differ on Windows-mounted paths in WSL2.

---

## 4. File Metadata and Operations

**Contents** are the actual bytes. **Metadata** is information about a file, such as its size, timestamps, permissions, and ownership. Permissions and ownership are introduced conceptually only; their detailed implementation belongs to the Operating System Fundamentals module.

Common file operations include creating, reading, writing, appending, renaming, copying, moving, and deleting.

A program requests file access through the operating system/filesystem, which accesses the underlying storage. Programs do not directly manipulate physical storage hardware.

---

## 5. Files, RAM, and Storage

- **File:** Persistent data stored through the filesystem, assuming the storage remains intact.
- **RAM:** Temporary, volatile working memory used while programs run.
- **Storage device:** Physical hardware that persistently holds file data.

When a program reads a file, its data may be loaded into RAM. When the program exits, the file remains on storage. Deleting a file generally removes its accessible filesystem reference; it does not guarantee that the underlying bytes are immediately erased.

A file's lifecycle can include creation, writing, storage, reading, modification, renaming or moving, and deletion.

---

## 6. Practical Linux/WSL2 Commands

The module demonstrates safe file inspection in a temporary directory:

| Command | Purpose |
|---|---|
| `pwd` | Show the current directory |
| `ls -l` | List files and metadata |
| `file filename` | Identify likely content type |
| `stat filename` | Inspect detailed metadata |
| `cat filename` | Display file contents |
| `head -c 50 filename` | Preview the first 50 bytes |
| `wc filename` | Count lines, words, and bytes |
| `xxd filename` | Display bytes in hexadecimal |
| `realpath filename` | Resolve an absolute path |
| `du -sh directory` | Estimate directory storage usage |

The lesson creates harmless example files, compares filenames with actual contents, examines paths and metadata, and removes its temporary workspace. In WSL2, Linux behavior may differ from Windows-mounted paths such as `/mnt/c`. Never assume the lesson's example output will match your system.

---

## 7. Real-World and AI Engineering Relevance

AI projects use files for datasets, JSON/YAML configuration, model files, checkpoints, tokenizer resources, logs, prompts, training artifacts, and evaluation datasets.

A database is not simply a special file: it is a system designed to structure, manage, and query persistent data.

---

## 8. Exercises, Review, and Scope

The module contains 45 exercises covering definitions, paths, metadata, debugging, file handling, datasets, configuration errors, model checkpoints, and missing-file problems. Solutions are in `exercises/14-files-answer-key.md`. Review questions reinforce the same concepts.

Detailed filesystem internals, system calls, file descriptors, permissions implementation, databases, and AI pipeline implementation are out of scope.

---

## Next Concept

**Concept 15 — Input/Output (I/O)**, which explains the deeper mechanics of how programs read and write data.
