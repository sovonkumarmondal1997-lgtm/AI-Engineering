# Storage

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 11

---

## 1. What Is Storage, and Why Do Computers Need It?

**Storage** is where a computer keeps data and programs for long-term use, even when the computer is turned off. This is called **persistent** or **non-volatile** storage.

RAM and storage serve different purposes:

- **Storage:** Keeps files, programs, datasets, and AI models for future use.
- **RAM:** Temporarily holds the data and programs needed while the computer is running.
- **CPU cache:** Keeps frequently needed data close to the CPU.
- **Registers:** Hold tiny amounts of information for immediate CPU operations.

Think of storage as a filing cabinet, RAM as a work desk, cache as a small tray, and registers as things currently in your hands. Storage preserves information; RAM supports active work.

When a computer restarts, programs and data can be loaded from storage into memory as needed.

---

## 2. How Storage Works

Applications generally access stored data through the operating system and its file interfaces rather than controlling the physical storage device directly.

The basic flow is:

```
Application → Operating system → Storage system → Storage device → Persistent media
```

When an application reads or writes a file, the operating system coordinates the operation. Real systems may use caches and buffers, so a save operation does not always mean every byte has immediately reached the physical storage medium.

A **file** is a logical representation of stored data. A **filesystem** organizes files and directories; its detailed internals belong to Module 0.2, Operating System Fundamentals.

---

## 3. Storage Capacity and Performance

Capacity is commonly measured in KB, MB, GB, and TB. Manufacturers often use decimal units, while operating systems may display binary-based units, explaining why reported capacity can appear smaller than advertised.

Four important properties are:

- **Capacity:** How much data storage can hold.
- **Latency:** How long an individual operation takes.
- **Throughput:** How much data is transferred over time.
- **IOPS:** Input/output operations per second, particularly relevant to many small reads and writes.

Copying a large file depends heavily on throughput; accessing many small files can depend more on latency and IOPS. More storage capacity does not automatically mean faster storage or a faster computer.

---

## 4. Why Storage Matters in AI Engineering

Applied AI projects depend on persistent storage for:

- Python source code and software environments.
- Training and evaluation datasets.
- Trained model files and checkpoints.
- Logs, configuration files, and generated artifacts.
- Data pipelines that repeatedly read and write data.

Large datasets may exceed available RAM, so they remain in storage and are loaded or mapped into memory as needed.

---

## 5. Practical Linux/WSL2 Commands

| Command | Purpose |
|---|---|
| `uname -a` | Identifies Linux environment details. |
| `df -h` | Shows filesystem capacity, used space, available space, and usage percentage. |
| `lsblk` | Lists available block devices and their reported sizes, if supported. |
| `du -sh .` | Shows disk usage of the current directory and its contents. |
| `du -sh ./*` | Shows the sizes of items directly inside the current directory. |

> **Important:** WSL2 uses virtualization. Its reported devices and capacities may not directly reflect your physical drive. `/mnt/c` exposes the Windows C: drive inside Linux; it is not necessarily a separate physical drive. Run directory-usage commands only in a safe, manageable directory.

---

## 6. Common Mistakes and Troubleshooting

Remember these distinctions:

- Storage is not the same as RAM, and it is not simply slower RAM.
- Storage retains data without power; RAM is volatile.
- A file is not a physical storage device.
- `df -h` reports filesystem space, not the exact physical SSD model or capacity.
- `du` measures files and directories, not total physical disk capacity.
- Programs do not simply execute directly from an SSD; program execution involves memory and the relevant runtime or compilation process.
- Deleting a file is normally a logical operation, not physical destruction of the drive.

---

## 7. Exercises and Production Relevance

The module includes 53 exercises covering definitions, memory hierarchy, program execution, capacity, AI artifacts, Linux observations, debugging misconceptions, and WSL2 interpretation. It also provides 15 review questions and a practical task to run the commands, document observations, and explain what they can and cannot prove.

Use only the specified read-only commands. Do not format disks, alter partitions, consume large amounts of disk space, benchmark storage, or modify the `project/` directory.

**Scope boundary:** This lesson introduces storage concepts, not HDD/SSD internals, filesystem internals, distributed storage, cloud storage architecture, database storage engines, or advanced performance optimization.

---

## Next Concept

**Concept 12 — HDD vs. SSD**
