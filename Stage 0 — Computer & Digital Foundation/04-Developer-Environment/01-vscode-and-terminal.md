# VS Code and the Terminal

**Module:** Developer Environment
**Roadmap reference:** Stage 0 — Module 0.4 — Developer Environment
**Concept(s) covered:** VS Code, terminal
**Prerequisites:** Module 0.1 (How Computers Work), Module 0.2 (Operating System Fundamentals), Module 0.3 (Command Line)
**Status:** Complete

### Hands-on environment

The practical exercises in this lesson assume a Unix-like environment using **Bash**, specifically
**Linux, macOS, or Windows with WSL2**. PowerShell and other shells are discussed for comparison, but
the commands in the exercises are written primarily for Bash. This is why commands such as `pwd`,
`ls`, `cat`, `rm`, `wc`, and `python3` appear throughout.

---

## 1. Introduction

### What a developer environment is

A **developer environment** is the collection of tools a person uses to write, run, inspect, and
fix software: an editor to write code, a terminal to run commands, and (later in this module) tools
that manage packages and isolated project setups. None of these tools are the computer itself —
they are ordinary programs that run *on top of* the operating system you studied in Module 0.2.
Setting up a developer environment means arranging these programs so you can move quickly between
"writing code" and "running code" without friction.

### Why developers need one

In Module 0.3 you learned to operate a computer directly through the command line: navigating
directories, manipulating files, running programs. That is already a real developer environment,
just a minimal one. Professional developers add an editor on top of it because reading, writing,
and navigating hundreds of files by hand in a terminal (with tools like `cat`, `nano`, or `vim`) is
slow. An editor gives you a visual map of a project, while the terminal remains the place where code
actually gets executed. Neither replaces the other; they are used together.

### What VS Code is

**VS Code** (Visual Studio Code) is a **code editor**: an application whose job is to let you open,
read, write, and organize source code files efficiently. It is a regular user-space application —
the same category of program as a web browser or a text editor, not part of the operating system.

### What a terminal is

You already know this from Module 0.3: a **terminal** is a program that gives you a text-based
interface for typing commands and reading their output. VS Code does not replace your terminal
knowledge — it gives you a *convenient place to open one* without leaving the editor window.

### How VS Code and the terminal are different

| | VS Code | Terminal |
|---|---|---|
| Primary purpose | View and edit files | Execute commands and programs |
| Interface style | Graphical (windows, panels, mouse + keyboard) | Text-based (keyboard only) |
| What it operates on | Files, as readable/editable text | Processes, as running programs |
| Typical output | Syntax-highlighted text on screen | Lines of text (stdout/stderr) |

### How they work together

VS Code can open a terminal *inside itself* (called the **integrated terminal**, covered in Section
4). This means one window gives you both views: the file/editor view on one side, and a
command-execution view at the bottom. You edit a file in the editor, switch to the terminal panel,
run it, read the result, and go back to editing — all without switching windows.

### Why this matters for an Applied AI Engineer

Every later stage of this roadmap — Python scripts, data pipelines, model training, RAG systems,
LLM agents, backend services — is written as code in an editor and executed from a terminal. The
editor is not the language runtime that runs your code; it mainly edits the text (and can invoke a
runtime through its tooling). The terminal (through a shell, through the operating system) is what
we will use to start the process that runs it. Understanding this split
precisely, now, prevents confusion later when a script "looks correct in the editor" but fails when
run.

---

## 2. VS Code Fundamentals

Building from first principles, using only ideas you can verify by looking at the application:

### File vs. folder vs. project vs. workspace vs. application/editor

These five words get blurred by beginners. They are distinct:

- **File** — a single unit of stored data on disk (Module 0.2). Example: `notes.txt`.
- **Folder (directory)** — a container that groups files and other folders (Module 0.2/0.3).
  Example: a folder named `my-first-script` containing `main.py` and `README.md`.
- **Project** — a human/organizational concept: a folder whose contents are meant to work together
  toward one purpose (a script, an application, a report). "Project" is not a special file-system
  object — it is just a folder that a developer has decided to treat as one unit of work.
- **Workspace** — VS Code's term for "the folder (or folders) currently open in this editor
  window." A VS Code workspace normally consists of one or more folders opened in a VS Code window;
  VS Code can also be used without an opened workspace. When you open a project folder in VS Code,
  that folder becomes your workspace. VS Code stores workspace-specific settings so different
  projects can be configured differently.
- **Application/editor (VS Code itself)** — the program you launch. It is not tied to any one
  project; you point it at whichever folder you want to work on.

Relationship: **application → opens a → workspace (a folder) → containing → files and
sub-folders**, some of which are grouped conceptually into a **project**.

### Code editor

A **code editor** is software built specifically for editing source code, as opposed to prose. It
differs from a plain text editor by understanding the *structure* of code: it colors keywords
differently from strings (**syntax highlighting**), shows line numbers, indicates matching brackets,
and can display errors inline. VS Code is a code editor.

### Workspace

Already defined above. Practically: when you tell VS Code "open this folder," everything you see —
the file tree, the terminal's starting location, project-specific settings — is scoped to that
folder. Opening a *different* folder gives you a different workspace, even in the same VS Code
window.

### File explorer

The **file explorer** is the panel (usually on the left) that shows the folder tree of your current
workspace: folders you can expand/collapse, and files you can click to open. It is a graphical
equivalent of running `ls` repeatedly and remembering the tree structure — except it stays visible
and updates automatically.

### Editor area

The **editor area** is the large central region where the actual contents of an open file are
displayed and edited. This is where you type code.

### Tabs

Each file you open occupies a **tab** at the top of the editor area, similar to browser tabs. Tabs
let you keep several files open at once and switch between them by clicking, without closing and
reopening files repeatedly.

### Command palette

The **command palette** (opened with `Ctrl+Shift+P` on Linux/Windows, `Cmd+Shift+P` on macOS) is a
searchable text box that lists nearly every action VS Code can perform — opening a terminal,
changing settings, selecting a Python interpreter, and so on — as typed commands instead of buried
menu clicks. It exists because a keyboard-driven search is faster than hunting through nested menus
once you know roughly what you want to do.

### Integrated terminal

Covered in depth in Section 4. Conceptually for now: a terminal panel that lives inside the VS Code
window, opened via the command palette or a keyboard shortcut, so you do not need a separate
terminal application window.

### Source-control area (conceptual only)

VS Code has a panel dedicated to source control (most commonly Git, which is a separate, later
topic in this roadmap). At this stage you only need to know it exists: it shows which files in your
workspace have changed since the last recorded snapshot of the project. It is not required to
understand this module and is not covered further here.

### Settings

**Settings** are configuration values that change how VS Code behaves — for example, how many
spaces a tab character represents, or which font size to use. Settings can apply to the whole
application (**user settings**) or only to the currently open workspace (**workspace settings**).
You do not need to configure anything yet; just know that "Settings" is where such preferences
live, and that a workspace can override the global defaults.

### Extensions (high level only)

**Extensions** are add-on packages that give VS Code new capabilities it does not have out of the
box — for example, understanding a specific programming language more deeply, or adding a new
panel. VS Code's built-in feature set is intentionally general; extensions are how it gets
specialized for a particular kind of work (such as Python development). Extensions are covered in
full in the next lesson (`03-extensions.md`); here you only need to know that they exist and that
they are how VS Code becomes "a Python editor," "a JavaScript editor," and so on.

---

## 3. How VS Code Relates to the Operating System

This section reuses Module 0.1/0.2 concepts rather than re-teaching them — refer back to those
modules if any term below is unfamiliar.

- **VS Code is a user-space application.** Like any other program you learned about in Module 0.1
  (an "application" running on top of the operating system, not part of the kernel), VS Code is
  started by the OS as a process, is scheduled for CPU time by the OS, and is granted memory by the
  OS. It has no special privileges over other programs.

- **VS Code interacts with the filesystem.** When VS Code's file explorer shows you a folder's
  contents, it is doing the same thing the `ls` command does: asking the operating system's
  filesystem for a directory listing. When you save a file in the editor, VS Code performs a file
  write through the OS, identical in principle to redirecting output to a file in the terminal
  (`>` from Module 0.3).

- **VS Code launches processes.** VS Code is an application that interacts with operating-system
  resources and processes. For operations that invoke external programs or tools — running a
  debugger, opening a terminal — VS Code or its extensions can ask the operating system to start
  those **processes** (Module 0.2). VS Code is not the Python runtime itself; the language
  runtime/interpreter executes the program, and VS Code can invoke that runtime through its tooling.

- **VS Code can launch a shell/terminal.** The integrated terminal panel is VS Code starting a
  **shell process** (defined precisely in Section 5) and connecting its input/output to that panel,
  instead of to a separate terminal window.

- **The terminal runs commands through a shell.** Exactly as in Module 0.3: you type a command, the
  shell interprets it, and for an external command the shell asks the OS to start a new process.

- **Commands execute as processes.** Running `python main.py` inside VS Code's integrated terminal
  creates a `python` process, tracked by the OS with a process ID, exactly like running the same
  command in a standalone terminal outside VS Code.

- **Programs read and write files.** Whether a program was started from VS Code's terminal or from
  a terminal outside VS Code, it accesses files the same way — through the OS's file APIs. VS Code
  has no special channel for this.

- **The current working directory matters.** This is expanded fully in Section 6, but the principle
  from Module 0.3 carries over unchanged: every process has a current working directory, and
  relative paths are resolved against it.

The point of this section: **VS Code does not introduce new operating-system behavior.** It is a
graphical front end that triggers the exact same processes, filesystem calls, and shells you already
understand. Nothing about how the OS works has changed — only how you interact with it has.

---

## 4. Terminal Fundamentals Inside VS Code

### Integrated terminal

The **integrated terminal** is a panel inside the VS Code window that hosts a running shell. You
open it via the command palette (`Ctrl+Shift+P` → "Terminal: Create New Terminal") or the shortcut
`` Ctrl+` `` (backtick). It behaves like any terminal window: you type commands, press Enter, and
read output — the only difference is that it is docked inside VS Code rather than being a separate
application window.

**Important distinction:** the integrated terminal is *not itself* a shell. It is a **terminal
emulator** — a program (in this case, a panel inside VS Code) that displays text input/output and
hosts a shell process. The shell is a separate program running inside that panel. This distinction
is expanded in Section 5.

### Shell

As covered in Module 0.3: the **shell** is the program that reads the text you type, interprets it
as a command (with a program name and arguments), and asks the operating system to run it. Bash is
one example of a shell.

### Command prompt

The **prompt** is the line of text the shell displays to indicate it is ready for input — often
showing the current directory and ending in a symbol like `$` or `%`. It is not the shell itself; it
is the shell's way of signaling "type a command now."

### Current working directory

The **current working directory (CWD)** is the directory a running process treats as its default
reference point for relative paths — the same concept from Module 0.2/0.3, unchanged inside VS
Code's terminal.

### Command, arguments

A **command** is the name of a program to run. **Arguments** are the extra pieces of text after the
command name that modify its behavior. Example: in `ls -la project/`, `ls` is the command; `-la` and
`project/` are arguments.

### Standard input, standard output, standard error

Reused directly from Module 0.3:

- **Standard input (stdin)** — the default source of input data a process reads from (usually your
  keyboard, unless redirected).
- **Standard output (stdout)** — the default stream a process writes its normal results to (usually
  displayed in the terminal).
- **Standard error (stderr)** — a *separate* stream a process writes error/diagnostic messages to,
  also usually displayed in the terminal, but distinguishable from stdout by tools when needed.

VS Code's integrated terminal displays both stdout and stderr in the same panel, just as an external
terminal does.

### Environment variables

An **environment variable** is a named value available to a running process, inherited from the
process that started it (Module 0.2). Example: `PATH` tells the shell which directories to search
for a command's program file. A process normally inherits environment variables from its parent
process, and shell startup/configuration files can then modify that environment. VS Code's
integrated terminal therefore starts with the environment inherited from VS Code (itself shaped by
how it was launched), plus a few VS Code–specific additions (for example, ones that make the "open
file in editor from terminal" convenience command work), and then the shell's own startup
configuration is applied.

### Process execution

When you type a command and press Enter, the shell parses it, locates the program (often using
`PATH`), and asks the OS to create a new **process** running that program. This is identical whether
the shell is running inside VS Code's integrated terminal or in a standalone terminal window — VS
Code adds no extra step to this chain.

Not every command starts a separate external process. Shells also provide built-in commands, such
as `cd`, that are handled by the shell itself. External commands such as `python3` are separate
programs that the shell can start. (This is why `cd` can change the shell's own working directory.)

### The full chain

```
VS Code (application)
   -> opens -> Integrated Terminal (a panel = terminal emulator)
        -> hosts -> Shell (e.g. Bash) — a running process
             -> you type a command
             -> shell parses command + arguments
             -> shell asks OS to start a new process
                  -> Operating System
                       -> creates the process
                       -> process runs, reads/writes files, uses CPU/memory
                       -> process produces stdout/stderr
             -> shell displays that output back in the terminal panel
```

**Concrete example.** Suppose your workspace folder contains a file `hello.py`. Inside the
integrated terminal:

```
$ python3 hello.py
```

Here, `python3` is the command, `hello.py` is its argument. (`python3` is the command used in the
Bash/Linux/macOS/WSL2 examples in this lesson; the Python command name can differ on other
platforms.) The shell finds the `python3` program
via `PATH`, the OS starts a `python3` process, that process reads and executes the text in
`hello.py`, and whatever the script prints appears as the process's stdout in the terminal panel.
None of this differs from running the same command in a terminal outside VS Code — VS Code only
supplied the panel the shell is displayed in.

---

## 5. Shell Selection

### The terminal-vs-shell distinction

This is the single most important distinction in this lesson, and it is easy to blur because the
words get used loosely in casual conversation.

- **Terminal** = the *interface* through which you see text input and output. It is a display and
  input mechanism — a window (or, inside VS Code, a panel) with a text area. On its own, a terminal
  does nothing with the text you type; it just shows characters and passes them along.
- **Shell** = the *program* running inside that terminal that actually interprets the text you type
  as commands and asks the OS to execute them.

Analogy: the terminal is like a phone handset — it lets you speak and hear. The shell is like the
person on the other end of the line who actually understands what you're saying and takes action.
Swapping the handset (terminal) does not change who you're talking to (the shell), and swapping who
you're talking to does not require a different handset.

**Why this distinction matters practically:** you can run different shells inside the same terminal
program, and the same shell can be displayed inside different terminal programs (VS Code's
integrated terminal, a standalone terminal application, a remote SSH session's terminal). Knowing
which layer a problem is in — "is my terminal broken, or is the shell configured wrong, or is the
command itself wrong?" — is a real diagnostic skill, used throughout Section 10.

### Common shells and terminals you will encounter

| Name | What it is | Typically used on |
|---|---|---|
| **Bash** | A shell — interprets Linux/Unix-style commands | Linux, macOS, WSL2, Git Bash |
| **PowerShell** | A shell — interprets Windows-style commands (different syntax from Bash) | Windows |
| **Git Bash** | A Bash-compatible shell environment bundled with Git for Windows (it ships with its own terminal window, but the shell is the core piece), letting Windows users run Bash-style commands | Windows |
| **WSL2** | A real Linux environment running on a Windows machine (Module 0.2's concepts apply fully once inside); a terminal can display a Bash shell running in it | Windows, running Linux |

VS Code's integrated terminal panel can be configured to start *any* of these shells — it is just
the display surface. On a machine with WSL2 (as described in this repository's own prerequisites),
VS Code is typically configured to open its integrated terminal into a WSL2/Bash environment.

**Bash and PowerShell are not interchangeable.** They use different command names and different
syntax for similar tasks (for example, listing files is `ls` in Bash and `Get-ChildItem` — often
aliased as `dir` — in PowerShell). A command copied from a Bash tutorial will often fail, or fail
silently in an unexpected way, if typed into a PowerShell prompt, and vice versa. This module does
not teach PowerShell or Git Bash syntax in depth; it only asks you to recognize that shells differ
and to know which one your terminal is running (see the debugging exercise in Section 10).

---

## 6. Working Directory

The **current working directory** is not a VS Code concept — it is an operating-system-level
property of every running process (Module 0.2), reused here because it directly affects your daily
VS Code + terminal workflow.

### Why it matters inside VS Code

When you open the integrated terminal, the shell it starts is typically given a current working
directory equal to your **workspace root** (the folder you opened in VS Code). This is convenient —
but it also means several real problems trace back to "the working directory was not what I
expected":

- **Opening the wrong folder.** If you open VS Code on a parent folder (e.g. your home directory)
  instead of your actual project folder, the integrated terminal's working directory starts there
  too. A command like `python main.py` then fails, because `main.py` is not in that directory — it's
  one level down.

- **Running a command from the wrong directory.** If you have multiple terminal tabs open (one you
  `cd`'d into a subfolder, one still at the root), running the same command in the wrong tab
  produces a different, sometimes confusing, result or error.

- **Python not finding a file.** A Python script that opens `data.csv` using a relative path will
  succeed only if the shell's current working directory contains `data.csv`. If you run the script
  from a different directory, Python reports the file as missing — even though the file exists
  somewhere on disk. This is a working-directory problem, not a missing-file problem.

- **Configuration files appearing missing.** Tools that look for a configuration file "in the
  current directory" (a pattern you will see repeatedly with Python tooling, later in this module)
  will silently fail to find it if the terminal's working directory is not the project root.

- **Relative paths behaving unexpectedly.** A relative path like `../data/input.txt` resolves
  differently depending on where the shell currently is — exactly as taught in Module 0.3. VS Code
  changes nothing about this rule; it only changes where the terminal *starts*.

### The rule to hold onto

Opening a folder in VS Code does not "activate" that folder for every purpose. It affects the file
explorer and (usually) the integrated terminal's starting directory — but once a terminal is open,
its working directory only changes when you explicitly `cd`, exactly as you learned in Module 0.3.
Always verify the current working directory (`pwd` in Bash) before assuming a command will find what
you expect.

---

## 7. VS Code + Terminal Developer Workflow

A realistic beginner workflow, repeated dozens of times a day by working developers:

1. **Open the project directory in VS Code** — using "Open Folder," pointed at the project's root
   folder, not a parent or a subfolder.
2. **Inspect the project files** — using the file explorer to see what already exists.
3. **Open the integrated terminal** — `` Ctrl+` `` or via the command palette.
4. **Check the current directory** — run `pwd` to confirm the terminal is where you expect.
5. **Run a command** — for example, listing files (`ls`) to cross-check against the file explorer.
6. **Create or edit a file** — either in the editor area, or from the terminal (both act on the same
   underlying filesystem — see Section 3).
7. **Run the program** — for example, `python3 script.py`.
8. **Observe output or errors** — read stdout/stderr in the terminal panel.
9. **Return to the editor** — to read the relevant source line, guided by any error message.
10. **Fix the code or configuration** — edit the file in the editor area.
11. **Run again** — repeat from step 7 until the output matches what is expected.

### Why professional developers constantly move between editor and terminal

The editor is where understanding and precision happen — reading code, forming a hypothesis about
what's wrong, making a controlled change. The terminal is where reality happens — where you find out
whether your hypothesis was correct, by actually executing the code and observing real output. Doing
all of this in one window (VS Code) rather than switching between two separate applications removes
friction from a cycle developers repeat constantly, sometimes dozens of times per hour. This
edit-run-observe loop is the core rhythm of programming, and it stays exactly the same shape in every
later stage of this roadmap — only what you're running changes (a script, a training job, a test
suite, a server).

---

## 8. Practical Examples

All examples below are safe: they only create/read a small text file inside your own project folder
and run one command already covered in Module 0.3. No destructive commands, credentials, or
administrative privileges are used. Where output is shown, it is labeled as **Example output** —
your actual output may differ slightly (timestamps, exact paths) but the structure will match.

**1. Open a project directory.**
In VS Code: File → Open Folder → select your project folder (for example, this module's folder).

**2. Check the current directory.**
Open the integrated terminal (`` Ctrl+` ``) and run:

```
$ pwd
```

Example output:

```
/home/you/AI Engineering/Computer & Digital Foundation/04-Developer-Environment
```

This confirms the terminal's working directory matches the folder you opened in VS Code.

**3. List files.**

```
$ ls
```

Example output:

```
01-vscode-and-terminal.md  02-ide-concepts.md  README.md  concepts  examples  exercises  labs  project
```

Cross-check this against what the file explorer panel shows — they describe the same directory.

**4. Create a simple file from the terminal.**

```
$ echo "hello from the terminal" > scratch.txt
```

This uses output redirection (`>`), from Module 0.3, to write text into a new file `scratch.txt`.

**5. Edit the file in VS Code.**
Click `scratch.txt` in the file explorer (it now appears there, because VS Code and the terminal
share the same filesystem — Section 3). Add a second line of text in the editor area, then save
(`Ctrl+S`).

**6. Observe the change from the terminal.**

```
$ cat scratch.txt
```

Example output:

```
hello from the terminal
a second line added in VS Code
```

This demonstrates that a save made in the editor is immediately visible to the terminal, and vice
versa, because both operate on the same underlying file through the same operating system.

**7. Run a simple command and observe output.**

```
$ echo "this line goes to stdout"
```

Example output:

```
this line goes to stdout
```

**8. Intentionally produce a simple error.**

```
$ cat file-that-does-not-exist.txt
```

Example output (exact wording may vary slightly by system):

```
cat: file-that-does-not-exist.txt: No such file or directory
```

**9. Diagnose the error.**
This message is written to **stderr**, not stdout (Section 4) — it is the shell/program telling you
the operation failed, not a normal result. The cause is simple: no file with that name exists in the
current working directory. Confirm with `ls` (does the file appear?) and `pwd` (are you in the
directory you think you are?) before assuming anything more complicated is wrong. Clean up the
practice file when done (before using `rm`, verify the current directory and the filename you
intend to remove):

```
$ rm scratch.txt
```

---

## 9. VS Code and Python Preparation

This section introduces only what is needed to *prepare* for Python work starting later in this
module — it does not teach Python programming, and it does not teach `venv`, `pip`, `uv`, or
`pyproject.toml`, which each get their own dedicated lesson later in Module 0.4.

### Python source file

A **Python source file** is a plain text file, conventionally ending in `.py`, containing Python
code. VS Code edits it exactly as it edits any other text file — syntax highlighting for Python is
added by an extension (Section 2), covered in the next lesson.

### Python interpreter (concept only)

Code you write in a `.py` file is text — it is not directly executable by the CPU (Module 0.1). A
**Python interpreter** is a program (itself just another process, per Section 3) that reads Python
source text and carries out the instructions it describes. "Running a Python script" means starting
this interpreter process and pointing it at your file.

### Running Python from the terminal

The basic pattern, using what you already know from Section 4:

```
$ python3 hello.py
```

Here `python3` is the command that starts the Python interpreter process; `hello.py` is the argument
telling it which source file to execute. This is identical in structure to any other command you
ran in Module 0.3 or Section 8 above — a command name plus an argument, run through the shell.

### VS Code selecting/interacting with a Python interpreter

A single computer can have more than one Python interpreter installed, and later in this module you
will learn to create isolated, project-specific interpreters (**virtual environments**). VS Code
lets you tell it, per workspace, *which* installed interpreter to use for features like showing
errors inline and running code with a button — this is called **interpreter selection**, done via
the command palette ("Python: Select Interpreter"). At this stage you only need the concept: VS
Code is not the Python runtime. Python tooling in VS Code can select and invoke a Python
interpreter for running, debugging, and language-related features.

### Why interpreter/environment selection matters

If VS Code (or you, from the terminal) uses a *different* Python interpreter than the one a project
was actually set up for, code can fail in confusing ways — a package that was installed for one
interpreter appears "missing" to another, because each interpreter has its own separate set of
installed packages. This is exactly why virtual environments exist, and why the topic gets a full,
dedicated lesson (`06-virtual-environments.md`) rather than being covered deeply here. For now,
remember only this: **which interpreter is running matters, and mismatches between "what VS Code is
using" and "what the terminal is using" are a real, common source of errors.**

---

## 10. Common Beginner Problems

Each problem: symptom, likely cause, how to inspect it, how to fix it, how to prevent it.

### VS Code opened the wrong folder

- **Symptom:** File explorer shows unrelated files, or an unexpectedly large/small set of files.
- **Likely cause:** "Open Folder" was pointed at a parent directory, a sibling directory, or a
  subdirectory instead of the actual project root.
- **Inspect:** Look at the folder name shown at the top of the file explorer, or run `pwd` in the
  integrated terminal.
- **Fix:** File → Open Folder → select the correct project root.
- **Prevent:** Before opening, confirm the target folder's path in a terminal (`pwd` after `cd`-ing
  to it) so you know exactly what you're pointing VS Code at.

### Terminal starts in an unexpected directory

- **Symptom:** `pwd` in the integrated terminal shows a directory that isn't the project root.
- **Likely cause:** The workspace itself is rooted somewhere unexpected (see above), or a
  previously-open terminal tab was manually `cd`'d elsewhere and left open.
- **Inspect:** Run `pwd`; compare against the folder shown in the file explorer.
- **Fix:** `cd` to the correct directory, or open a fresh integrated terminal (which restarts at the
  workspace root).
- **Prevent:** Get in the habit of running `pwd` as the first command in a new terminal session.

### Command is not found

- **Symptom:** Something like `command not found: <name>` after pressing Enter.
- **Likely cause:** The program is not installed, or it is installed but not listed in the shell's
  `PATH` (Module 0.2/0.3), or it was typed with a typo.
- **Inspect:** Re-check spelling; confirm the tool is actually installed by consulting its
  installation instructions.
- **Fix:** Install the missing tool, or correct the command name.
- **Prevent:** Verify a new tool is installed and runs (e.g., checking its version) immediately
  after installing it, before relying on it inside a larger workflow.

### Wrong shell selected

- **Symptom:** A command that "should work" produces a syntax error, or behaves completely
  differently than a tutorial describes.
- **Likely cause:** The integrated terminal is running a different shell than the one the command
  was written for (e.g., a Bash command typed into PowerShell — Section 5).
- **Inspect:** Check which shell the terminal panel is running (VS Code shows this in the terminal
  panel's dropdown/label).
- **Fix:** Either translate the command to the running shell's syntax, or open a terminal running the
  intended shell instead.
- **Prevent:** Know, deliberately, which shell your integrated terminal defaults to on your machine
  before following shell-specific instructions from any source.

### Wrong Python interpreter selected

- **Symptom:** VS Code reports an import/package as missing, even though you are sure it is
  installed; or code run via VS Code's "Run" button behaves differently than the same file run
  manually from the terminal.
- **Likely cause:** VS Code is using a different Python interpreter than the terminal is (Section 9).
- **Inspect:** Use the command palette's "Python: Select Interpreter" to see which one is active, and
  compare it against `which python3` run in the terminal (in Bash/Unix-like environments, this shows
which executable is being resolved).
- **Fix:** Select the interpreter you actually intend to use, consistently, in both places.
- **Prevent:** After setting up a project's environment (later lessons), explicitly select that
  environment's interpreter in VS Code rather than leaving it on a default.

### File exists but command cannot find it

- **Symptom:** A command reports a file as missing, but you can see it in the file explorer.
- **Likely cause:** Working-directory mismatch (Section 6) — the file exists, but not relative to
  where the shell currently is.
- **Inspect:** Run `pwd`, then `ls`, and compare the file's actual location (shown in the file
  explorer, or via `ls` in the containing folder) to the current working directory.
- **Fix:** `cd` into the correct directory, or use a corrected relative/absolute path.
- **Prevent:** Prefer running project commands from the project root, and double-check working
  directory before relying on relative paths.

### Relative path failure

- **Symptom:** A path like `data/file.txt` fails from one location but works from another.
- **Likely cause:** Relative paths are resolved against the current working directory (Module 0.3);
  running the same command from two different directories changes what the relative path points to.
- **Inspect:** Compare `pwd` output between the working and failing cases.
- **Fix:** Run the command from the directory the relative path assumes, or use an absolute path.
- **Prevent:** Be explicit (in scripts and instructions) about which directory a relative path is
  meant to be run from.

### Environment variable unavailable

- **Symptom:** A command or script that depends on an environment variable behaves as if the
  variable is empty or unset.
- **Likely cause:** The variable was set in a different terminal session, or a different shell, or a
  configuration file that this particular terminal did not load (Module 0.2's environment variable
  inheritance rules apply here unchanged).
- **Inspect:** In Bash, `echo $VARIABLE_NAME` displays the value of that environment variable for
  the current shell session; run it in the terminal actually being used.
- **Fix:** Set the variable in the session/shell that needs it, using the method appropriate to that
  shell.
- **Prevent:** Know which terminal/shell session you are in before assuming environment state
  carries over from another one.

### Terminal command works in one environment but not another

- **Symptom:** A command succeeds in VS Code's integrated terminal but fails in a separate terminal
  window (or vice versa), on the same machine.
- **Likely cause:** Different working directory, different shell, or a different environment
  (`PATH`, other variables) between the two sessions — each terminal session is independent unless
  explicitly configured to match.
- **Inspect:** Compare `pwd`, the active shell, and relevant environment variables between the two
  sessions.
- **Fix:** Align whichever setting differs (directory, shell, or variable) between the two.
- **Prevent:** Treat every terminal session as independent state rather than assuming settings
  "carry over" automatically.

---

## 11. Engineering Trade-offs

No tool below is universally better — each is suited to different situations.

| Trade-off | Favors GUI / VS Code side | Favors terminal-only side |
|---|---|---|
| **GUI vs. terminal** | Visual file browsing, easier for beginners, good for reading unfamiliar codebases | Faster for experienced users, works over minimal remote connections, no graphical overhead |
| **VS Code vs. terminal-only workflow** | Convenient editing, integrated feedback, one window for most tasks | Fewer moving parts, works identically on any machine with just a shell (e.g., a bare remote server) |
| **Integrated terminal vs. external terminal** | Convenient, no window-switching, shares VS Code's window layout | External terminal keeps working even if VS Code crashes or is closed; useful for long-running processes you want independent of the editor |
| **Bash vs. PowerShell** | PowerShell integrates deeply with Windows-specific administration | Bash is the standard across Linux, macOS, and most server/cloud environments — the environments this roadmap targets |
| **Convenience vs. explicit control** | GUI actions are quick and discoverable | Typed commands are precise, repeatable, and can be saved as scripts |
| **Graphical tooling vs. reproducible command-line workflows** | Easier to learn interactively | Command-line steps can be written down, automated, and run identically on another machine — essential for later automation and production work |

**General principle for this roadmap:** use VS Code for reading and writing code, and the terminal
for actually running and verifying it. As you progress toward production work (automation, remote
servers, containers — introduced conceptually in Section 18), command-line fluency becomes
increasingly load-bearing, because many of those environments have no graphical interface at all.

---

## 12. Applied AI Engineering Connection

This is a forward-looking preview only — none of the following technologies are taught here. The
purpose is to show that the VS Code + terminal skills in this lesson are the same skills you will
use, unchanged in kind, throughout the rest of the roadmap:

- **Python projects** — opened as a VS Code workspace; run from the integrated terminal.
- **Datasets** — files inspected in the file explorer, loaded from paths resolved relative to a
  working directory (Section 6).
- **Model files** — large files managed and referenced the same way as any other project file.
- **Training scripts** — Python files, launched from the terminal exactly like `hello.py` in Section
  9, just longer-running.
- **Inference scripts** — same execution pattern, used to get predictions from a trained model.
- **Configuration** — files read by tools/scripts, subject to the same working-directory rules from
  Section 6.
- **Evaluation scripts** — again, ordinary commands run from the terminal, producing stdout/stderr
  you will learn to read carefully.
- **Logs** — text output, often written to files, inspected using terminal tools from Module 0.3.
- **RAG applications, LLM applications, agent systems, backend services** — all, at the code level,
  are Python (or similar) projects opened in VS Code and run from a terminal, just with more moving
  parts.
- **Docker commands** — typed into the same integrated terminal, following the same
  command-arguments-process pattern from Section 4.
- **Tests** — run as terminal commands, with pass/fail reported via stdout/stderr and exit codes
  (Module 0.2).
- **Git** — used from VS Code's source-control panel or the terminal; both ultimately run the same
  underlying `git` commands as processes.
- **Cloud/deployment workflows** — frequently operated entirely through a terminal, often on a
  remote machine with no graphical interface at all — which is exactly why terminal fluency, not
  just VS Code fluency, matters for production AI engineering.

---

## 13. Practical Exercises

Complete these in order, inside your own copy of this module's folder. All exercises are safe and
reversible.

**Exercise 1 — Open the correct project folder.**
Close VS Code if it is open. Reopen it using File → Open Folder, pointed specifically at the
`04-Developer-Environment` folder (not a parent folder). Confirm the file explorer shows this
lesson file among its contents.

**Exercise 2 — Open and navigate the integrated terminal.**
Open the integrated terminal. Note which shell it reports itself as running (check the terminal
panel's label/dropdown).

**Exercise 3 — Identify the current working directory.**
Run `pwd`. Write down (in your own notes, not in this file) the exact path it prints.

**Exercise 4 — List project files.**
Run `ls`. Compare the result against what the file explorer panel shows for the same folder. Confirm
they describe the same set of files and folders.

**Exercise 5 — Create and edit a small file.**
From the terminal, run `echo "exercise file" > my-notes.txt`. Open `my-notes.txt` in the VS Code
editor, add a second line of your own, and save it.

**Exercise 6 — Run a command and read stdout.**
Run `cat my-notes.txt` and confirm both lines appear in the terminal panel.

**Exercise 7 — Distinguish stdout from stderr.**
Run `cat my-notes.txt` (succeeds — note the output) and then `cat does-not-exist.txt` (fails — note
the error message). Identify, in your own words, which stream each message came from.

**Exercise 8 — Identify the active shell explicitly.**
In Bash, `echo $0` can provide a clue about the current shell. Run it and note what it prints. Compare this with what the terminal panel's own label
told you in Exercise 2.

**Exercise 9 — Create and diagnose a path error.**
Create a subfolder named `sub` (`mkdir sub`), and inside it create a file `inner.txt` containing any
text. From the *project root* (not from inside `sub`), run `cat inner.txt` and confirm it fails.
Then run `cat sub/inner.txt` and confirm it succeeds. Explain to yourself, in writing (your own
notes), why the first attempt failed given what Section 6 taught about the working directory.

**Cleanup:** remove the practice files you created (`my-notes.txt`, `sub/`) once finished, so the
module folder is left as you found it. Before using `rm`, verify the current directory and the
filename you intend to remove.

---

## 14. Debugging Exercise

**Situation.** A learner has a project folder containing a single file, `app.py`, which reads a
configuration file named `settings.txt` located in the same folder using a relative path. The
learner opens VS Code, but instead of opening the project folder directly, opens its *parent*
folder (which also contains several unrelated folders). They then open the integrated terminal and
run:

```
$ python3 app.py
```

**Expected behavior.** The script should read `settings.txt` and print its contents.

**Actual behavior.**

```
FileNotFoundError: [Errno 2] No such file or directory: 'settings.txt'
```

**Evidence.** The learner is confident `settings.txt` exists, because they can see it in the file
explorer's tree, nested one level down under a subfolder.

**Investigation.** Applying Section 6 and Section 10: the first thing to check is the current
working directory the terminal is actually using, not what the file explorer visually shows. Running
`pwd` reveals the terminal's working directory is the *parent* folder — not the subfolder containing
`app.py` and `settings.txt`. Running `ls` from there confirms `settings.txt` is not directly present;
it is one level down.

**Root cause.** VS Code was opened on the wrong folder (the parent, not the project folder itself).
Because the integrated terminal's working directory follows the workspace root, the terminal started
one level "too high," and the script's relative path (`settings.txt`, meaning "in the current working
directory") could not resolve to the actual file location.

**Fix.** Two valid options: (a) close and reopen VS Code directly on the correct project subfolder
so the terminal's working directory matches where `app.py` expects to run from, or (b) from the
current terminal, `cd` into the correct subfolder before running the script.

**Prevention.** Before running a script that depends on relative paths, run `pwd` to confirm the
working directory matches the project's actual root — the same habit introduced in Exercise 3 and
in the "Terminal starts in an unexpected directory" entry of Section 10.

---

## 15. Mini Application

**Goal:** build and run a tiny "project status" workflow using only VS Code and the terminal, to
practice the full loop from Section 7 end-to-end. No external libraries; no Python required — plain
shell commands only, all reused from Module 0.3.

**Steps:**

1. In your open workspace, create a new folder named `status-app` (`mkdir status-app`, from the
   integrated terminal).
2. Move into it: `cd status-app`.
3. Confirm your location: `pwd`.
4. Create a file listing today's "tasks," one per line, using the editor: create `tasks.txt` in VS
   Code's file explorer (right-click the `status-app` folder → New File), and type three short lines
   of any text representing tasks.
5. From the terminal (still inside `status-app`), count how many tasks you wrote:
   `wc -l tasks.txt`. Read the number in the output.
6. Append a new task from the terminal without opening the editor:
   `echo "review VS Code lesson" >> tasks.txt` (the `>>` operator, from Module 0.3, appends instead
   of overwriting).
7. Reopen `tasks.txt` in the editor and confirm the new line appears — demonstrating, concretely,
   that editor and terminal changes apply to the same file (Section 3).
8. Recount: `wc -l tasks.txt` and confirm the number increased by one.
9. Intentionally trigger a path error: move back to the parent folder (`cd ..`) and run
   `wc -l tasks.txt` again. Observe and explain the failure using Section 6/14's reasoning.
10. Return to the correct directory (`cd status-app`) and confirm the command works again.

This exercise deliberately combines: opening/using the file explorer, editing in the editor area,
running commands in the integrated terminal, working-directory awareness, and diagnosing a
self-induced path error — the same skills used, at larger scale, throughout the rest of this
roadmap.

**Cleanup:** remove the `status-app` folder when finished.

---

## 16. Review

### Key concepts

- A **developer environment** combines an editor (VS Code) and a terminal; neither replaces the
  other.
- VS Code is a **user-space application**, not an operating system, and not a shell.
- A **workspace** is the folder (or folders) currently open in VS Code.
- The **integrated terminal** is a panel inside VS Code that hosts a shell process; it is a terminal
  emulator, not a shell itself.
- The **current working directory** governs how relative paths resolve, in the terminal exactly as
  it did in Module 0.3 — VS Code changes nothing about this rule.
- **Interpreter selection** in VS Code determines which Python interpreter VS Code's Python tooling
  invokes for Python-specific features; it can differ from whatever `python3` resolves to in the terminal.

### Important distinctions

- **Terminal vs. shell** — terminal displays input/output; shell interprets commands.
- **File vs. folder vs. project vs. workspace vs. application** — five distinct concepts, defined in
  Section 2.
- **Bash vs. PowerShell** — both are shells, with different, non-interchangeable syntax.
- **Integrated terminal vs. external terminal** — same underlying shell concept, different hosting
  window.

### Common mistakes

- Assuming the integrated terminal *is* a shell, rather than a panel hosting one.
- Assuming a command that works in one shell will work unchanged in a different shell.
- Assuming the file explorer's tree tells you the terminal's current working directory.
- Assuming VS Code and the terminal always agree on which Python interpreter is active.
- Running commands without first confirming the working directory with `pwd`.

### Mental model

```
VS Code (application, user-space process)
   |
   |-- File Explorer  --\
   |-- Editor Area      |--> all operate on the same filesystem, via the OS
   |
   \-- Integrated Terminal (panel)
          |
          \-- Shell (e.g. Bash) -- a process
                 |
                 \-- you type: command + arguments
                        |
                        \-- shell asks OS to create a new process
                               |
                               \-- Operating System (Module 0.2)
                                      |
                                      \-- process runs, touches files, produces stdout/stderr
```

### Self-check questions

1. In your own words, what is the difference between a workspace and a project?
2. If the file explorer shows a file, does that guarantee the terminal's current working directory
   can reach it with a plain relative path? Why or why not?
3. Why is it inaccurate to say "VS Code's integrated terminal is Bash"?
4. What is the difference between what appears in stdout and what appears in stderr?
5. Why might the exact same command succeed in one terminal tab and fail in another, on the same
   machine?

---

## 17. Interview / Architecture Questions

**Q: What is VS Code?**
A: A code editor — a user-space application for viewing, writing, and organizing source code and
project files. It is not an operating system and is not the language runtime that executes code
(it can invoke one through its tooling).

**Q: What is a terminal?**
A: A program that provides a text-based interface for entering commands and viewing their output; it
displays what a shell reports, but does not itself interpret commands.

**Q: What is a shell?**
A: A program that reads typed commands, interprets them (command + arguments), and asks the
operating system to execute them (external commands run as new processes; built-ins such as `cd`
are handled by the shell itself).

**Q: What is the difference between a terminal and a shell?**
A: The terminal is the display/input surface; the shell is the program that actually interprets
commands. A terminal hosts a shell — they are two different layers, and one terminal can host
different shells at different times.

**Q: What is a workspace?**
A: In VS Code, the folder (or set of folders) currently open in the editor window, which scopes the
file explorer view, workspace-specific settings, and typically the integrated terminal's starting
directory.

**Q: Why does the current working directory matter?**
A: Because relative file paths — used constantly in scripts, configuration, and commands — are
resolved against it. The same relative path can point to different (or nonexistent) locations
depending on which directory a process is currently "in."

**Q: Why might a command work in one terminal but not another?**
A: Because different terminal sessions can be running different shells, have different current
working directories, or have different environment variables (such as `PATH`) — any of which can
change whether and how a command executes.

**Q: What happens when a command is executed from the integrated terminal?**
A: The shell hosted in that terminal panel parses the typed text into a command and arguments, then
asks the operating system to create a new process to run it — exactly as it would in any other
terminal running that same shell.

**Q: Why do engineers still use terminals when graphical tools exist?**
A: Terminal commands are precise, scriptable, and reproducible — they can be written down, shared,
and rerun identically. Many real environments (remote servers, containers, cloud machines) provide
only a terminal, with no graphical interface at all, so terminal fluency is not optional for those
contexts.

**Q: Why is command-line knowledge important for production AI engineering?**
A: Production AI systems are typically deployed, monitored, and debugged on remote machines, inside
containers, or through automated pipelines — environments that are terminal-only. The same editor
and terminal habits practiced here (checking working directory, reading stdout/stderr, running
processes deliberately) are the direct foundation for that later, higher-stakes work.

---

## 18. Production Engineering Connection

The habits built in this lesson are not "beginner scaffolding" that gets discarded later — they are
the same habits production engineering depends on, only carried out in less forgiving settings:

- **Reproducibility.** Running a command from a known, verified working directory reduces one source
  of variation. Reproducibility also depends on versions, dependencies, configuration, environment,
  and inputs — the same factors that decide whether a script works identically on a teammate's
  machine or a production server.
- **Debugging.** The discipline from Section 10 and Section 14 — check the working directory, check
  the shell, check stdout vs. stderr — is exactly how real production incidents get diagnosed,
  just at larger scale and higher pressure.
- **Automation.** Anything typed into a terminal by hand can, in principle, be captured into a
  script and run unattended. Production systems run enormous numbers of commands this way, with no
  human present to notice a wrong working directory — which is precisely why getting these
  fundamentals right now matters.
- **CI/CD.** Automated build/test/deploy pipelines execute the same kind of shell commands you ran
  by hand in this lesson's exercises, on a remote machine, with no VS Code and no graphical
  interface at all.
- **Containers.** Many production containers (introduced only conceptually here) use a Linux
  userspace and are commonly interacted with through a terminal or shell, so the shell fundamentals
  from Module 0.3 and this lesson transfer directly, without VS Code present.
- **Remote servers.** Connecting to a remote machine typically gives you a terminal and a shell, and
  nothing else — the working-directory and shell-identification skills from this lesson transfer
  directly.
- **Linux environments.** Nearly all production AI/ML infrastructure runs on Linux, which is why
  this roadmap's Stage 0 is built around Linux/WSL2 command-line fluency rather than a graphical
  workflow.
- **Cloud infrastructure.** Cloud machines are frequently administered entirely through a terminal,
  often over a remote connection with real latency and no visual file explorer — the file/folder
  mental model from Section 2 must be held in your head rather than seen on screen.
- **AI/ML workloads.** Training runs, batch inference jobs, and evaluation scripts are, mechanically,
  the same "run a command, read stdout/stderr, fix, rerun" loop practiced in Section 7 and Section
  15 — just with longer-running processes and larger inputs.

None of these topics (CI/CD specifics, Docker, cloud platforms, deployment mechanics) are taught in
this lesson. The goal here is only to establish that the conceptual chain you now understand — **VS
Code → terminal → shell → command → process → operating system → filesystem** — is the same chain
every later production system in this roadmap is built on.
