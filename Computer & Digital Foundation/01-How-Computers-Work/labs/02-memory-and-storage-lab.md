# Lab 0.1.2 — Memory and Storage Lab

**Status:** Not Started
**Concepts exercised:** Cache, RAM, Storage, HDD vs SSD

## Objective

Observe the practical difference between memory (RAM) and storage (disk) — in capacity, in
persistence, and in a simple felt sense of speed — without writing any code.

## Prerequisites

- Concept files 9–12 read (Cache, RAM, Storage, HDD vs SSD).
- Lab 1 completed (system information already gathered).
- A terminal on Linux, Ubuntu, or WSL2.

## Commands/tools required

- `free -h`
- `df -h`
- `time` (shell builtin)
- A large-ish test file (created with `dd` or similar) for the copy-speed observation

## Procedure outline

1. Run `free -h` again and note how much RAM is *available* right now vs *total*.
2. Run `df -h` and note total and free space on the main storage volume.
3. Create a test file of a fixed size (e.g. 500 MB) using `dd if=/dev/zero of=testfile bs=1M count=500`.
4. Time copying that file within the same disk using `time cp testfile testfile_copy`.
5. Restart the shell/terminal (closing it fully) and confirm the test file still exists afterward
   — contrast this with what would happen to data only held in RAM.
6. Delete the test files when done.

## Observations to record

- Total RAM vs total storage capacity (which is larger, and roughly by what factor).
- Time taken to copy the test file.
- Confirmation that the file survived a terminal/session restart (persistence), and a note on
  what would NOT survive a restart (anything only in RAM, e.g. unsaved variables in a running
  program).

## Expected learning outcome

The learner can explain, using their own measured numbers, why RAM and storage are different
in capacity, persistence, and speed — grounding concept file 19
(`19-why-ram-and-storage-are-different.md`) in a real observation instead of an abstract claim.

## Troubleshooting

- **`dd` not available:** use `fallocate -l 500M testfile` as an alternative to create a test
  file of a given size.
- **Disk is an SSD and copy feels "too fast to notice":** that outcome is itself a valid, worth
  recording observation — connect it back to concept file 12 (HDD vs SSD).
- **Low disk space warning:** reduce the test file size (e.g. 100 MB) rather than skipping the
  lab.

---

_This is a lab specification prepared during repository setup. No lab has been performed yet._
