# Stage 0 Learning Plan — Computer, Linux, and Developer Foundations

**Status:** Not Started
**Roadmap position:** Stage 0 of the Applied AI / Agentic AI Engineering roadmap.
**Starting point:** The four modules of the original roadmap (0.1–0.4) below.
**Purpose:** Audit that learning, close a small number of practical gaps, and produce observable
evidence that you can work independently in a developer environment before starting programming.

> This is not an AI stage. It is the foundation that prevents later Python, backend, cloud,
> model-serving, and agent-engineering problems from becoming confusing. A production AI engineer
> must be able to inspect a process, read a log, manage an environment, and reproduce an
> issue — not only write prompts.

---

## 1. Stage outcome

By the end of this stage you can:

- explain how a program uses CPU, RAM, disk, files, and (at a high level) a GPU;
- use Windows, PowerShell, WSL2/Ubuntu, and Bash safely for development;
- navigate, create, inspect, search, and permission files from a terminal;
- identify a running process, its PID, resource use, logs, exit code, and listening port;
- create an isolated Python workspace and run a project reproducibly;
- use Git and GitHub for basic version control without exposing secrets;
- diagnose a small local-environment failure methodically; and
- explain these decisions in a short beginner-level technical interview.

You are **not** expected to know Docker, cloud, Kubernetes, CUDA, networking in depth, or Python
programming yet. Those come later.

---

## 2. Audit of the original four modules

The original roadmap contains these four modules. Keep them; they are correctly placed and
valuable. Work through each one's numbered concept files, in order, before treating it as
understood.

| Module | Folder | What you should already understand | Evidence to verify before moving on |
|---|---|---|---|
| **0.1 How computers work** | [`01-How-Computers-Work/`](../01-How-Computers-Work/README.md) | CPU/cores, registers, RAM/cache/storage, HDD vs SSD, GPU, binary, files, processes, I/O, compilation vs interpretation | In your own words, explain what happens from launching a Python command to seeing output, and why a GPU helps with parallel tensor operations. |
| **0.2 Operating-system fundamentals** | [`02-Operating-System-Fundamentals/`](../02-Operating-System-Fundamentals/README.md) | Kernel vs user space, system calls, processes vs threads, scheduling, virtual memory, filesystems, permissions, environment variables, signals, standard streams, pipes, process lifecycle | Find a running process, inspect its PID and resource use, stop a test process safely, and explain exit code `0` versus non-zero. |
| **0.3 Command line** | [`03-Command-Line/`](../03-Command-Line/README.md) | Navigation; file operations; `grep`, `find`, `sort`, `uniq`, `cut`, `xargs`; pipes; redirection; shell scripts; permissions | Complete the log-investigation project below (Project 0.2) using commands you understand, not copied commands. |
| **0.4 Developer environment** | [`04-Developer-Environment/`](../04-Developer-Environment/README.md) | VS Code, terminal, debugger, extensions, virtual environments, package managers, project layout, `uv`, `pip`, `venv`, and `pyproject.toml` | Create an isolated workspace, install one package, run a file, and document setup from a clean terminal. |

### Important distinction

"Completed" means you studied or practiced the modules. It does **not** automatically mean the
skills are operational. The projects in Section 5 and the completion gate in Section 8 verify
operational competence. If a check feels difficult, revisit that exact topic; do not restart all of
Stage 0.

---

## 3. Gaps to close before Stage 1

The original four modules are strong on concepts, but they should add the following practical
topics. These are small additions, not a separate long stage.

### Gap 0A — Git, GitHub, and SSH basics

Git appears later in the original roadmap, but basic version control must start now. Every project
from Stage 1 onward needs a history, a README, and a safe way to collaborate.

Learn, in this order:

1. What a repository, working tree, staging area, commit, branch, remote, and pull request are.
2. `git status`, `git add`, `git commit`, `git log`, `git diff`, `git switch`, `git branch`,
   `git pull`, and `git push`.
3. How to write small, descriptive commits: one meaningful change per commit.
4. How `.gitignore` prevents committing virtual environments, caches, local databases, `.env`
   files, and keys.
5. GitHub repository creation, README editing, issues, and pull requests.
6. SSH key purpose and GitHub authentication conceptually; follow GitHub's current official setup
   instructions when configuring it.

Use it now:

- Create one private or public learning repository named `engineering-foundations`.
- Commit each Stage 0 project separately.
- Add a concise README and a `.gitignore` before adding files.

**Do not learn yet:** complex rebase workflows, release management, Git internals, or advanced
branching strategies.

### Gap 0B — Safe terminal habits and filesystem literacy

Production engineering starts with not damaging your own environment.

Learn:

1. Absolute versus relative paths and how to confirm your current directory before changing files.
2. File extensions, hidden files, UTF-8 text, line endings, and why Windows and Linux paths differ.
3. Read, write, and execute permissions in Linux; the idea of file ownership and `chmod`.
4. Symbolic-link concept; recognize one before deleting or moving files.
5. Safe deletion: inspect first, avoid recursive commands unless you can name the exact target, and
   prefer a temporary practice directory.
6. Shell quoting: why paths with spaces and special characters need care.
7. Standard streams: input (`stdin`), normal output (`stdout`), errors (`stderr`), redirection
   (`>`, `>>`, `2>`), and pipe (`|`).

Practice with a dedicated folder such as `~/practice-shell`; never practice destructive commands in
Downloads, Documents, or a project folder.

### Gap 0C — Local networking needed for development

Full networking is later, but you need a small amount now to understand local services.

Learn:

1. `localhost` / `127.0.0.1`, IP address, port, DNS, and the client-server idea.
2. Why two programs cannot normally listen on the same port.
3. How to identify a local listener using `ss -ltnp` on Linux or `Get-NetTCPConnection` on
   PowerShell.
4. How `curl` sends a request and prints the response.
5. The difference between a process running successfully and a service being reachable.

This will make API, FastAPI, Docker, model serving, and agent-tool debugging much easier later.

### Gap 0D — Reproducible Python workspace

You do not need to learn Python syntax yet, but you must be able to create a clean environment.

Learn:

1. What the Python interpreter is and how to check its version with `python --version`.
2. Why packages should be isolated per project.
3. The difference between `pip`, `venv`, and `uv`: `pip` installs packages; `venv` provides
   isolation; `uv` can manage environments and dependencies quickly.
4. The role of `pyproject.toml`: project metadata and declared dependencies.
5. Why a lock file makes installations reproducible.
6. How to run a tiny program from the terminal, capture errors, and read the traceback from bottom
   to top.

Use **one** workflow consistently: prefer `uv` for new projects, while understanding enough `venv`
and `pip` to work in existing codebases.

### Gap 0E — Secrets and local security hygiene

AI projects use API keys early, so learn this before you ever use a model provider.

Learn:

1. API keys, passwords, tokens, and private keys are secrets, not configuration to commit.
2. Store local secrets in `.env` or your system's secure credential mechanism; put `.env` in
   `.gitignore`.
3. Use a `.env.example` file containing only variable names and placeholder values.
4. Check `git diff` and `git status` before every commit.
5. If a secret is exposed, revoke/rotate it immediately; deleting the line in a later commit does
   not make the exposure safe.
6. Install software and extensions from trusted publishers and keep operating systems/packages
   updated.

### Gap 0F — Engineering thinking from day one

For every exercise, practice this loop:

```text
Goal → assumptions → smallest experiment → observe output/logs
→ explain failure → change one variable → verify → document
```

Keep a small `learning-notes.md` file. For each issue, record:

- what you expected;
- what actually happened;
- the command or evidence you checked;
- root cause;
- fix; and
- what you would test next time.

This is the habit that later becomes debugging, incident response, evaluation, and architecture
thinking.

---

## 4. Recommended tools and how to use them

Install only the tools below; avoid extension/tool overload.

| Tool | Learn now | Use it for | Do not worry about yet |
|---|---|---|---|
| **Windows PowerShell** | `Get-ChildItem`, `Set-Location`, `Get-Content`, `Select-String`, `Get-Process`, `Get-NetTCPConnection` | Windows files, processes, and local environment inspection | Advanced PowerShell automation/frameworks |
| **WSL2 + Ubuntu** | Open Ubuntu, use Bash, understand `/home/...` versus `C:\...`, access project files intentionally | Your Linux learning and future Python/backend work | Running a production Linux server |
| **Bash** | `pwd`, `ls`, `cd`, `mkdir`, `cp`, `mv`, `rm`, `cat`, `less`, `head`, `tail`, `grep`, `find`, `sort`, `uniq`, `cut`, `chmod`, `ps`, `top`/`htop`, `kill`, `curl` | Navigation, logs, process inspection, and repeatable commands | Clever one-line scripts that you cannot explain |
| **VS Code** | Open a folder (not individual files), integrated terminal, Explorer, search, formatter, debugger, source-control view | Edit, search, inspect Git changes, and debug later code | Installing many unreviewed extensions |
| **Git + GitHub** | Status, add, commit, diff, log, branch, pull, push, `.gitignore`, README | Preserve work and demonstrate progress | Advanced Git tricks |
| **Python** | Check interpreter, run a file, read tracebacks | Prepare for Stage 1 | Language syntax in depth |
| **uv** | Create/sync a project environment; inspect declared dependencies | Reproducible Python project setup | Every packaging alternative |
| **pip + venv** | Recognize and use when an existing project requires them | Work across normal Python codebases | Mixing them randomly with `uv` in one project |
| **curl** | Send a request to a local URL and read status/body | Verify local services later | Full API design |
| **htop** or OS task tools | Find CPU/memory-consuming test processes | Basic diagnosis | Performance optimization |

### Suggested VS Code setup

Install only trusted, useful extensions:

- Python;
- Pylance;
- WSL (when using WSL projects);
- GitHub Pull Requests and Issues, if you use GitHub;
- an editor-config/formatting extension only when a project needs it.

Configure VS Code to format on save later in Stage 3; at this stage, learn where the terminal, file
explorer, search, debugger, and source-control panels are.

---

## 5. Practical projects

Complete the projects in order. They deliberately use little or no programming because Stage 1 is
where Python development begins.

### Project 0.1 — Developer Environment Health Check

**What you build:** A version-controlled `environment-report.md` containing a repeatable checklist
and the output of safe commands that verify your machine is ready for learning.

**Why this matters:** Engineers do not guess whether their environment works. They verify it. This
project gives you a baseline when a later tool, package, GPU library, or server setup fails.

**Build steps:**

1. Create an `engineering-foundations` Git repository and add a README.
2. Record OS version, terminal choices, WSL distribution, Python version, Git version, and VS Code
   version.
3. Verify that PowerShell and Ubuntu/Bash can each open, navigate to a practice folder, and display
   a text file.
4. Record the commands you ran and explain each command in plain English.
5. Create a `.gitignore` that excludes `.env`, virtual environments, Python caches, and
   editor-specific local files.
6. Commit the report with a message such as `docs: add environment health check`.

**Deliverables:** `README.md`, `.gitignore`, `environment-report.md`, and one clean Git commit.

**How it helps later:** It establishes reproducibility, version control, and troubleshooting
discipline for every Python, database, Docker, and AI project.

### Project 0.2 — Shell File-and-Stream Investigation Lab

**What you build:** A small, synthetic log directory plus `investigation.md` showing how you found
answers using shell tools.

**Scenario:** You receive application log files containing timestamps, levels such as
`INFO`/`WARN`/`ERROR`, request IDs, and messages. Determine how many errors occurred, which message
repeats most often, and which request IDs appear in error lines.

**Build steps:**

1. Create a safe practice directory with several plain-text log files; write the entries yourself
   or use non-sensitive sample data.
2. Use `head`, `tail`, and `less` to inspect the files before searching.
3. Use `grep` to filter error lines.
4. Use pipes plus `sort` and `uniq -c` to count repeated messages or IDs.
5. Redirect the final result into a report file while redirecting any command errors separately.
6. Repeat one task in PowerShell using `Get-Content` and `Select-String` so you understand the
   analogous workflow.
7. In `investigation.md`, write the question, commands, output, interpretation, and one limitation
   of your approach.

**Deliverables:** synthetic logs, `investigation.md`, and a small `commands.sh` containing only
commands you can explain.

**How it helps later:** AI services produce logs, traces, tool calls, evaluation output, and
failure reports. This is the first version of production debugging.

### Project 0.3 — Process, Resource, and Port Diagnosis Lab

**What you build:** A troubleshooting guide for a harmless local process and a short incident
report.

**Scenario:** A test program is consuming CPU or holding a port, and you must identify it and stop
it safely without restarting your computer.

**Build steps:**

1. Start a harmless long-running local process, such as a simple terminal loop or a built-in local
   HTTP server. Do this only inside your practice directory.
2. Identify its PID using `ps`/`top`/`htop` on Linux or `Get-Process` on PowerShell.
3. Observe CPU and memory usage; explain why an idle process and a busy loop differ.
4. If using a local HTTP server, discover the listening port with `ss -ltnp` or
   `Get-NetTCPConnection` and call it with `curl`.
5. Stop the test process gracefully first; verify it exited and the port is no longer listening.
6. Write `process-diagnosis.md`: symptom, observations, commands, root cause, safe remediation, and
   verification.

**Deliverables:** `process-diagnosis.md` and a one-page command reference in your own words.

**How it helps later:** Backend APIs, vector databases, model servers, agent workers, and queues
are all processes communicating through ports and consuming resources.

### Project 0.4 — Reproducible Python Workspace Bootstrap

**What you build:** A minimal Python workspace that another person can set up from the README.

**Build steps:**

1. Create a new folder, open it in VS Code, and initialize Git.
2. Initialize a Python project with `uv` and inspect the generated `pyproject.toml`.
3. Add one harmless dependency only if needed for a small experiment; otherwise keep the
   environment minimal.
4. Add a tiny `hello_environment.py` program that prints the interpreter version and current
   working directory. You may copy this minimal code initially, but annotate every line until you
   understand it.
5. Run it through the project environment, intentionally make one simple error, read the
   traceback, fix it, and record the debugging process.
6. Add `README.md` instructions for a clean setup, run, and expected output.
7. Add `.env.example`; do not put any real secret in it.

**Deliverables:** `pyproject.toml`, lock file if generated, `hello_environment.py`, README,
`.gitignore`, `.env.example`, and `learning-notes.md`.

**How it helps later:** This becomes your template for reproducible Python, LLM, data, and backend
projects.

### Project 0.5 — Stage 0 Incident Simulation

**What you build:** A short, evidence-based postmortem for one intentionally introduced local
failure.

Choose one safe scenario:

- a command fails because you are in the wrong directory;
- a Python package is unavailable because the environment is not activated/synced;
- a local port is already occupied by your test process;
- a file cannot be written because of permissions in the practice directory;
- a `.env` value is missing but no real secret is involved.

**Build steps:**

1. State the expected behavior before changing anything.
2. Reproduce the problem deliberately and save the exact error.
3. Inspect one fact at a time: directory, environment, process, port, permissions, or
   configuration.
4. Form a hypothesis and test it with the smallest safe command.
5. Apply the smallest fix.
6. Verify the original operation succeeds.
7. Write `postmortem-stage-0.md` using: summary, impact, timeline, root cause, fix, prevention, and
   verification.

**How it helps later:** This teaches the core engineering behavior: evidence before assumption and
prevention after repair.

---

## 6. Engineering-thinking practices for this stage

Use these rules in every project:

1. **Inspect before changing.** Check `pwd`/current directory, `git status`, file contents,
   process, or log before a command that modifies state.
2. **Make the smallest reproducible case.** Do not debug inside a large folder or with many
   unknown variables.
3. **Treat output as evidence.** Read errors and logs; do not repeatedly rerun commands hoping for
   a different result.
4. **Explain every command.** If you cannot explain a command's inputs, output, and risk, do not
   use it yet.
5. **Keep work reproducible.** Put setup instructions, dependencies, and expected output in the
   README.
6. **Keep secrets out of code and Git.** This remains mandatory for every future AI project.
7. **Write the failure down.** A note converts a temporary mistake into reusable engineering
   knowledge.

---

## 7. Parallel interview preparation

Do not start intensive algorithm interview practice yet. Build clear technical communication
instead.

Practice answering these aloud in 60–90 seconds each:

1. What is the difference between CPU, RAM, storage, and GPU?
2. What happens when you run a program from a terminal?
3. What is the difference between a process and a thread?
4. What is an environment variable, and why should a secret not be committed to Git?
5. What are `stdin`, `stdout`, and `stderr`?
6. Why use a virtual environment for Python?
7. What does Git track, and why make small commits?
8. A local server will not start because a port is in use — how would you diagnose it?

For every project, use this simple explanation format:

```text
Problem → approach → evidence → result → what I learned
```

This becomes the foundation for behavioral interviews, project deep dives, system design, and AI
architecture interviews later.

---

## 8. Stage 0 completion gate

You have completed Stage 0 when all statements below are true:

- [ ] I completed the original Modules 0.1–0.4 and can demonstrate the audit evidence in Section 2.
- [ ] I can work in both PowerShell and Bash/WSL without confusing their paths and commands.
- [ ] I can safely navigate, inspect, search, redirect, and permission files from the terminal.
- [ ] I can identify a process, inspect a local port, stop a harmless process safely, and verify
      the result.
- [ ] I can explain a basic traceback and isolate a local environment issue.
- [ ] I can initialize a Git repository, make meaningful commits, push it to GitHub, and protect
      `.env` files.
- [ ] I can create and run a reproducible minimal Python workspace with `uv`.
- [ ] I completed Projects 0.1–0.5 and committed their documentation to Git.
- [ ] I can answer the eight Stage 0 interview questions clearly without reading notes.

If one item is incomplete, practice that item specifically. Once the gate is met, proceed to
**Stage 1 — Programming Logic and Python Foundations**. Do not skip Stage 1 in order to begin LLMs
or agents.

## Notes

- Do not skip ahead to later modules (0.2 → 0.3 → 0.4) before earlier ones are understood — each
  module in Stage 0 assumes the previous one.
- Work through the numbered concept files inside each module folder (`01-How-Computers-Work/`
  through `04-Developer-Environment/`) in order; the audit table in Section 2 links directly to
  each one.
