# Concept 07 — Filesystems

A **filesystem** is the system that organizes data on storage devices into files and folders so applications can easily save, find, read, and update information.

---

## 1. Basic concepts

- **Storage device:** Physical hardware that stores data permanently, even when the computer is switched off.
- **Filesystem:** The organizational system built on storage that manages files and directories.
- **File:** A named collection of stored data, such as a Python script, image, or dataset.
- **Directory:** A folder that contains files and other directories.
- **Path:** The address used to locate a file or directory.

Think of storage as a warehouse and the filesystem as its organization system.

---

## 2. Why filesystems exist

Without a filesystem, applications would need to manage raw storage blocks themselves. Filesystems solve this by providing:

- File naming and organization.
- Easy file and directory navigation.
- Metadata management (size, timestamps, ownership, permissions).
- Tracking used and available storage space.
- Access control.
- Standard operations such as opening, reading, writing, and deleting files.

---

## 3. Important technical concepts

### Absolute vs. relative paths

- **Absolute path:** Complete location starting from `/`, e.g. `/home/user/project/data/train.csv`.
- **Relative path:** Location interpreted from the process's current working directory, e.g. `data/train.csv`.

The same Python code, `open("data/train.csv")`, can work or fail depending on where the program is launched.

### Linux directories

- `/` — filesystem root.
- `/home` — user directories.
- `/tmp` — temporary files.
- `/etc` — system configuration.
- `/var` — changing data, including logs.
- `/usr` — installed programs.
- `/dev` — device files.
- `/proc` — virtual filesystem exposing live kernel and process information, not persistent disk files.

### File metadata

**File metadata:** Information about a file, separate from its actual content. Includes size, timestamps, ownership, permissions, file type, and inode identity.

**Inode:** A Unix/Linux filesystem record containing file metadata and references to its data. A directory entry connects a filename to an inode. Therefore, a filename and the underlying file identity are different things.

### Mounting

**Mounting:** Attaching a filesystem to a directory called a **mount point**. For example, `/mnt/c` in WSL2 makes a Windows drive accessible inside Linux without copying its contents.

---

## 4. How filesystem access works

A process requests file operations through system calls. The operating system and filesystem handle access to persistent storage.

File data can also be read into process memory or memory-mapped into its virtual address space. Persistent file data and process memory are related but distinct.

---

## 5. Practical Linux commands

| Command | Purpose |
|---|---|
| `pwd` | Show current working directory |
| `ls -la` | List files, directories, and details |
| `stat file` | Show detailed metadata |
| `file filename` | Identify what a file appears to contain |
| `df -h` | Show filesystem-wide capacity |
| `du -sh folder` | Show specific folder's disk usage |
| `mount` | Show mounted filesystems |

**Important:** `df` measures filesystem capacity; `du` measures file or directory usage. Their results can differ.

---

## 6. Debugging and production relevance

Common problems include:

- **`FileNotFoundError`:** Check working directory, path, spelling, capitalization, and file existence.
- **No space left on device:** Use `df -h` to identify the full filesystem and `du -sh` to find what consumes space.
- **Different behavior across launch locations:** Investigate relative paths.
- **Large model files:** Disk size does not automatically equal process memory usage.
- **`/proc` confusion:** Its entries are dynamically generated, not ordinary persistent files.

For AI engineering, filesystems are essential for managing Python code, configuration, datasets, model checkpoints, tokenizer files, logs, temporary files, caches, and generated outputs.

---

## 7. Key takeaways

A filesystem is not a storage device or RAM. File content differs from metadata; absolute paths differ from relative paths; mounting does not copy data; and file permissions determine whether a process can access an existing file.

The lesson includes 13 misconceptions, 5 debugging scenarios, 37 exercises, expected results, and review questions covering these concepts.

**Next topic:** Concept 08 — Permissions, which explains who can read, write, or execute files.
