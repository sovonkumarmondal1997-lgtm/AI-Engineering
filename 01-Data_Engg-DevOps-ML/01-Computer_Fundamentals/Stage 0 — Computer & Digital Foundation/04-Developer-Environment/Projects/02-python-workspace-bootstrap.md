# Project 0.4 — Reproducible Python Workspace Bootstrap

**Estimated time:** 60–90 minutes

**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Section 5 — "Practical
projects," Project 0.4 — "Reproducible Python Workspace Bootstrap."

---

## 1. Project title and estimated time

**Reproducible Python Workspace Bootstrap** — estimated 60–90 minutes.

## 2. Purpose and AI-engineering relevance

Every later Python, LLM, or backend project in this roadmap starts the same way: a project folder,
a declared set of dependencies, and a README someone else could follow from nothing but the
repository itself. This project builds exactly that — a minimal, working Python workspace, set up
with `uv`, that another person (or you, on a different machine) could reproduce from the README
alone.

This becomes your template for every reproducible Python, data, and AI project going forward — get
the pattern right once, here, with almost no real code involved, and every later project inherits
the habit.

## 3. Learning outcomes

By the end of this project, you will be able to:

- Create a new practice folder, initialize Git, and open the project folder (not a single file) in
  VS Code.
- Verify which Python interpreter is active, and initialize a project with `uv`.
- Read and explain a real `pyproject.toml`.
- Write a tiny Python program, explain every line of it, and run it through the project's own
  environment.
- Deliberately cause, correctly read, and fix a real traceback — and document the process.
- Write setup, run, expected-output, and troubleshooting instructions that let someone else
  reproduce your environment.
- Add `.env.example` with safe placeholders only, and correctly exclude `.env` from Git.

## 4. Prerequisites and safety rules

**Concepts you should have already read** (in this module, `04-Developer-Environment/`):

- `06-virtual-environments.md`, `07-package-managers.md`, `09-python-tooling.md` — the underlying
  concepts this project puts into practice.
- `11-reproducible-python-workspaces-with-uv.md` — this project follows that lesson's workflow
  directly: `uv init`, inspect `pyproject.toml`, `uv run`, `uv sync`, and reading a traceback
  bottom-to-top.
- `12-secrets-and-local-security-hygiene.md` — `.env`, `.env.example`, and `.gitignore`.
- `10-git-github-and-ssh-basics.md` — small, descriptive commits.

**Tools required** (all free): a terminal (Bash/WSL2 or PowerShell), Python 3, `uv`, Git, and VS
Code.

**Not required:** Docker, any cloud account, GPUs, or Python knowledge beyond `print()` and reading
a variable.

**Safety rules:**

1. **Build this project in a new, separate practice folder** (for example,
   `~/practice-shell/uv-bootstrap/` or as its own small repository) — never inside this `AI
   Engineering` curriculum folder.
2. **Confirm your current directory** before creating any file.
3. **No command in this guide deletes anything or requires `sudo`/administrator rights.**
4. **Every value in `.env.example` is a placeholder** — this project never uses or requires a real
   secret at any point.

## 5. Deliverables

By the end, your project folder should contain:

- [ ] `pyproject.toml`
- [ ] a lock file, generated automatically once you run `uv sync`
- [ ] `hello_environment.py`
- [ ] `README.md` — with setup, run, expected-output, and troubleshooting sections
- [ ] `.gitignore`
- [ ] `.env.example` — placeholder values only
- [ ] `learning-notes.md` — documenting the deliberate-error debugging process

## 6. Industry-standard workflow

Use this loop for every step below, especially Step 7.9's deliberate error:

```text
Goal → assumptions → smallest experiment → observe output/logs
→ explain failure → change one variable → verify → document
```

In practice, for each step: state what you're trying to do and what you expect (goal, assumptions),
run the smallest command that tests it (smallest experiment), read the real result (observe), and
if it's wrong, explain why using only what you actually saw (explain failure) before changing
exactly one thing (change one variable), confirming it worked (verify), and writing it down
(document).

## 7. Step-by-step instructions

### 7.1 Create a separate practice folder and initialize Git

```bash
mkdir -p ~/practice-shell/uv-bootstrap
cd ~/practice-shell/uv-bootstrap
pwd
git init
```

### 7.2 Open the project folder — not a single file — in VS Code

```bash
code .
```

- `code .` — opens the **current folder** in VS Code (the `.` means "this directory"). Opening the
  folder, rather than one file, gives you the Explorer, integrated terminal, and source-control
  view all scoped to this project — exactly
  [`../01-vscode-and-terminal.md`](../01-vscode-and-terminal.md)'s point about why a developer
  environment is more than just an editor.

### 7.3 Verify the Python interpreter

```bash
python3 --version
which python3
```

Record both — the version and the exact interpreter path
([`../11-reproducible-python-workspaces-with-uv.md`](../11-reproducible-python-workspaces-with-uv.md),
Section 2).

### 7.4 Initialize and run a minimal project with `uv`

```bash
uv --version
```

If this fails with "command not found," **stop and install `uv` first**, following `uv`'s own
official documentation for your operating system (search "uv installation" on `docs.astral.sh`,
`uv`'s official documentation site) — do not copy an installation command from an untrusted source
([`../12-secrets-and-local-security-hygiene.md`](../12-secrets-and-local-security-hygiene.md),
Section 9). Once installed, open a **new** terminal window before continuing.

```bash
uv init
```

- `uv init` — creates a minimal project here: `pyproject.toml` and a small starter file.

### 7.5 Inspect and explain `pyproject.toml`

```bash
cat pyproject.toml
```

Write, in your own words, one sentence for each of `name`, `version`, `requires-python`, and
`dependencies` — what each one declares, following
[`../11-reproducible-python-workspaces-with-uv.md`](../11-reproducible-python-workspaces-with-uv.md),
Section 8.

### 7.6 Add a minimal `hello_environment.py`

```python
import sys
import os

print("Python interpreter:", sys.executable)
print("Current working directory:", os.getcwd())
```

### 7.7 Explain each line in plain English

Write, in `learning-notes.md`, one sentence per line:

- `import sys` — brings in Python's `sys` module, which exposes details about the running
  interpreter itself.
- `import os` — brings in Python's `os` module, which exposes operating-system-level information
  like the current directory.
- `print("Python interpreter:", sys.executable)` — prints the full path to the interpreter
  actually running this file.
- `print("Current working directory:", os.getcwd())` — prints the directory this process considers
  "here" right now.

(Write these in your **own** words in `learning-notes.md` — the four bullets above are a reference
for what "explained in plain English" looks like, not text to copy verbatim.)

### 7.8 Run the program using the project environment

```bash
uv run python hello_environment.py
```

Confirm the printed interpreter path points *inside* this project's own environment, not your
system Python from Step 7.3 —
[`../11-reproducible-python-workspaces-with-uv.md`](../11-reproducible-python-workspaces-with-uv.md),
Section 9 explains why this distinction matters.

### 7.9 Intentionally introduce one safe, simple error, then fix it

Change one line to introduce a simple, safe mistake — for example, misspell a variable name:

```python
import sys
import os

print("Python interpreter:", sys.executible)   # deliberate typo: executible
print("Current working directory:", os.getcwd())
```

```bash
uv run python hello_environment.py
```

**Example traceback:**

```text
Traceback (most recent call last):
  File "hello_environment.py", line 4, in <module>
    print("Python interpreter:", sys.executible)
                                  ^^^^^^^^^^^^^^
AttributeError: module 'sys' has no attribute 'executible'. Did you mean: 'executable'?
```

**Read it from the bottom up**, exactly as
[`../11-reproducible-python-workspaces-with-uv.md`](../11-reproducible-python-workspaces-with-uv.md),
Section 11 taught: the last line names the error (`AttributeError`) and even suggests the fix here;
the line above shows the exact failing line. Fix the typo (`executible` → `executable`), rerun, and
confirm it now succeeds.

**Document the process in `learning-notes.md`**, following
[`../13-evidence-based-debugging-and-notes.md`](../13-evidence-based-debugging-and-notes.md),
Section 8's structure: expected result, actual result (the exact traceback), evidence checked, root
cause, fix, prevention, and next test.

### 7.10 Add setup, run, expected-output, and troubleshooting sections to the README

`````markdown
# uv Bootstrap

A minimal, reproducible Python workspace.

## Setup

1. Install `uv` (see `uv`'s official documentation for your OS).
2. `uv sync`

## Run

````bash
uv run python hello_environment.py
````

## Expected Output

````text
Python interpreter: /path/to/this-project/.venv/bin/python
Current working directory: /path/to/this-project
````

(Your exact paths will differ — what matters is that the interpreter path points inside this
project's own environment.)

## Troubleshooting

- `uv: command not found` — install `uv` first (see Setup).
- `ModuleNotFoundError` — run `uv sync` again; a dependency only becomes installed after syncing.
`````

### 7.11 Add `.env.example` and exclude `.env`

```bash
echo "EXAMPLE_API_KEY=your-api-key-here
EXAMPLE_DATABASE_URL=postgresql://user:password@localhost:5432/db" > .env.example

echo ".env
.venv/
__pycache__/
*.pyc" > .gitignore
```

Confirm `.env.example` contains **only** placeholder text (`your-api-key-here`, not anything that
looks like a real credential) — following
[`../12-secrets-and-local-security-hygiene.md`](../12-secrets-and-local-security-hygiene.md),
Section 5. This project never creates a real `.env` file at all, since no real secret is needed —
`.env.example` exists purely to demonstrate the reproducible pattern.

### 7.12 Verify a new learner could reproduce this from the README alone

Read only your `README.md`'s Setup and Run sections, as if you had never seen this project before,
and confirm each step is unambiguous: does "Setup" actually list everything needed? Does "Run"
produce exactly what "Expected Output" describes? If you had to add an unwritten step to make it
work, add that step to the README now — that's a genuine gap this exercise exists to catch.

Finally, commit your work:

```bash
git add pyproject.toml uv.lock hello_environment.py README.md .gitignore .env.example learning-notes.md
git status
git diff
git commit -m "feat: add reproducible uv Python workspace bootstrap"
```

## 8. Expected observations and acceptance criteria

- `uv run python hello_environment.py` prints an interpreter path *inside* this project's own
  environment folder, and the correct current working directory.
- The deliberate typo produces a real `AttributeError` traceback, correctly read bottom-up, and the
  fix resolves it — confirmed by rerunning.
- `learning-notes.md` documents the debugging process using the full expected-result /
  actual-result / evidence / root-cause / fix / prevention / next-test structure.
- `README.md`'s Setup and Run sections are complete enough that Step 7.12's self-check passes
  without needing to add an unwritten step.
- `.env.example` contains only clearly-labeled placeholder values; `.env` never appears in `git
  status`'s output.
- `git log` shows one clean commit containing all seven deliverables.

## 9. Common problems and safe troubleshooting

| Problem | Likely cause | Safe next step |
|---|---|---|
| `python3: command not found` | Python isn't installed | Install Python 3 from your OS's official source; then open a new terminal. |
| `uv: command not found` | `uv` isn't installed yet | Install it via `uv`'s own official documentation, then open a **new** terminal window before retrying. |
| `uv run` uses an unexpected Python version | The project's `requires-python` in `pyproject.toml` doesn't match what you assumed | Check `pyproject.toml`'s `requires-python` value against `python3 --version` from Step 7.3. |
| Dependencies seem "unsynced" (a `ModuleNotFoundError` for something you declared) | `pyproject.toml` was edited but `uv sync` wasn't run afterward | Run `uv sync` again — installation only happens at sync time, not the moment a dependency is added to the file. |
| The traceback in Step 7.9 doesn't match the example | You introduced a different typo, or fixed it before reading fully | That's fine — read *your* actual traceback's last line first, exactly the same bottom-up method, regardless of the exact wording. |

## 10. Interview-practice questions

Practice answering these aloud, in 60–90 seconds each, using your own `learning-notes.md`:

1. **"Walk me through how you'd set up a new, reproducible Python project from scratch."**
   Guidance: describe `uv init`, declaring dependencies in `pyproject.toml`, and `uv sync` — a
   single, repeatable command sequence, not a list of manually remembered steps.

2. **"How do you read a Python traceback?"**
   Guidance: bottom to top — the error type and message first, then the exact failing line, then
   the chain of calls above it. Use your own Step 7.9 example as a concrete anchor.

3. **"What makes a project's setup actually reproducible, rather than just working on your own
   machine?"**
   Guidance: a declared dependency file plus a lock file, and setup instructions you've personally
   verified are complete (Step 7.12) — not memory of what you happened to install.

4. **"Why keep a `.env.example` file instead of just telling teammates what environment variables
   they need?"**
   Guidance: a file in the repository is discoverable and version-controlled; a verbal or chat
   explanation gets lost — and it documents the *names* needed without ever exposing real values.

## 11. Final completion gate

You have completed this project when all statements below are true:

- [ ] I created a new practice folder, initialized Git, and opened the folder (not a file) in VS
      Code.
- [ ] I verified my Python interpreter and initialized a project with `uv`.
- [ ] I read and correctly explained every field in my `pyproject.toml`.
- [ ] I wrote `hello_environment.py`, explained every line in my own words, and ran it through the
      project's own environment.
- [ ] I deliberately caused, correctly read (bottom-up), and fixed a real traceback.
- [ ] `learning-notes.md` documents that debugging process with all seven fields from
      `13-evidence-based-debugging-and-notes.md`'s structure.
- [ ] My README's Setup, Run, Expected Output, and Troubleshooting sections passed my own
      "could a new learner reproduce this?" check.
- [ ] `.env.example` contains only placeholders, and `.env` is correctly excluded by `.gitignore`.
- [ ] I made one clean commit containing all seven deliverables.

Once every box is checked, this project satisfies Stage 0 Project 0.4 and the Module 0.4 audit
evidence. Return to
[`../../00-Stage-0-Overview/learning-plan.md`](../../00-Stage-0-Overview/learning-plan.md) to
continue with the rest of Stage 0.
