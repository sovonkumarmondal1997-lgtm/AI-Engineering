# Module 0.3 — Command Line

## Lesson 01: Navigation — Simple Summary

This lesson teaches you how to navigate your computer’s filesystem using three essential commands: `pwd`, `ls`, and `cd`.

---

## 1. What is the command line?

The **command line** is a text-based way to communicate with your computer. Instead of clicking icons, you type commands and receive text output. It is widely used in software development, AI engineering, cloud servers, Docker containers, and remote GPU machines.

---

## 2. Terminal vs Shell vs Command

- **Terminal:** The application or window where you type and see output.
- **Shell:** The program inside the terminal that interprets your commands, such as Bash or PowerShell.
- **Command:** An instruction given to the shell, such as `pwd`, `ls`, or `cd`.
- **Filesystem:** The structure containing files and directories.
- **Current Working Directory (CWD):** The directory where a running process is currently operating.

---

## 3. Current Working Directory

Every process has a current working directory. When you run a program, it usually inherits the shell’s directory. This matters because relative file paths are resolved from that location. The `cd` command changes the shell’s directory; it does not move files.

---

## 4. Understanding Paths

A **path** tells the computer where a file or directory is located.

- **Root (`/`):** The top of the filesystem.
- **Home (`~`):** Your personal directory.
- **Parent (`..`):** One directory above.
- **Current (`.`):** The directory you are currently in.

Two path types:

- **Absolute path:** Complete location, e.g. `/home/learner/projects/ai-project`. It works regardless of your current directory.
- **Relative path:** Location based on your CWD, e.g. `projects/ai-project`. Its meaning changes depending on where you are.

---

## 5. The Three Essential Commands

| Command | Purpose |
|---|---|
| `pwd` | Shows your current directory as an absolute path. |
| `ls` | Lists files and directories without changing location. |
| `cd` | Changes your current working directory. |

Useful `ls` options:

- `ls -l`: Detailed listing, including permissions and file sizes.
- `ls -a`: Includes hidden files.
- `ls -la`: Combines detailed and hidden listings.
- `ls -lh`: Displays human-readable file sizes.

Useful `cd` commands:

- `cd projects`: Enter a directory.
- `cd ..`: Move one level up.
- `cd ../..`: Move two levels up.
- `cd ~` or `cd`: Go home.
- `cd -`: Return to the previous directory.
- `cd .`: Stay in the current directory.

**Important:** `pwd` and `ls` only read information. `cd` changes the shell's directory.

---

## 6. How Path Resolution Works

The shell processes your command and expansions such as `~`. The program receives the path, and the operating system resolves it. Absolute paths start at `/`; relative paths start at the process's CWD. Missing directories, incorrect names, and insufficient permissions cause errors.

---

## 7. Practical Applications

Navigation is essential for:

- Running AI/ML training scripts from the correct project directory.
- Finding datasets, model checkpoints, and output folders.
- Activating virtual environments.
- Working on remote GPU servers and cloud machines.
- Avoiding mistakes when modifying or deleting files.

---

## 8. Trade-offs and Professional Habits

Absolute paths are predictable but less portable. Relative paths are shorter and more portable but depend on the CWD. Frequently changing directories can cause mistakes.

**Professional habit:** Check `pwd` and `ls` before executing commands, especially destructive ones.

---

## 9. Exercises and Practice

The lesson includes:

- Seven practical navigation exercises.
- Five debugging scenarios covering missing directories, permission errors, incorrect working directories, and case mismatches.
- A filesystem scavenger hunt using only `pwd`, `ls`, and `cd`.
- Ten review questions and four interview/architecture questions.

---

## 10. Production and AI Engineering Relevance

Incorrect working directories can cause dataset-loading failures, incorrect environment activation, Git mistakes, and production automation errors. Production scripts should avoid depending on an unpredictable CWD and should log their working directory and resolved file paths.

**Lesson boundary:** This lesson covers only `pwd`, `ls`, and `cd`. Commands such as `cp`, `mv`, `rm`, `mkdir`, file-reading tools, pipes, redirection, environment variables, and shell scripting are reserved for later lessons.
