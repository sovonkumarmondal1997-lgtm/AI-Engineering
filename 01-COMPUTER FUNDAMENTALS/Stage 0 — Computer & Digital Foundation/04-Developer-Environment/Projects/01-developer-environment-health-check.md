# Project 0.1 — Developer Environment Health Check

**Estimated time:** 45–75 minutes

**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Section 5 — "Practical
projects," Project 0.1 — "Developer Environment Health Check"; and Section 2's audit evidence:
*"Create an isolated workspace, install one package, run a file, and document setup from a clean
terminal."*

---

## 1. Project title and estimated time

**Developer Environment Health Check** — estimated 45–75 minutes.

## 2. Purpose and real-world AI-engineering relevance

Engineers do not guess whether their environment works — they verify it, and they write the
verification down. This project builds a version-controlled `environment-report.md`: a repeatable
checklist and the real output of safe commands proving your machine is actually ready for the work
ahead.

This matters beyond Stage 0. When a later tool, package, GPU library, or server setup fails, this
report becomes your baseline — evidence of what your environment looked like when things were
working, making "what changed since then?" an answerable question instead of a guess. Every AI team
that has ever debugged "it works on my machine" has needed exactly this kind of documented
baseline.

## 3. Learning outcomes

By the end of this project, you will be able to:

- Create a new, separate Git repository and give it a clear README.
- Record the exact versions of every core tool in your developer environment.
- Verify, with real evidence, that both PowerShell and Bash/WSL can navigate and display a file.
- Document every command you ran and explain it in plain English.
- Write a `.gitignore` that safely excludes secrets, environments, caches, and editor files before
  your first real commit.
- Inspect `git status` and `git diff` before committing, and make one clean, descriptive commit.
- Verify your own repository does not contain any secret, and could be reproduced by someone else.

## 4. Prerequisites and safety rules

**Concepts you should have already read** (in this module, `04-Developer-Environment/`):

- `01-vscode-and-terminal.md` — VS Code and the integrated terminal
- `10-git-github-and-ssh-basics.md` — `git status`, `git add`, `git commit`, `.gitignore`
- `12-secrets-and-local-security-hygiene.md` — what counts as a secret and why it must never be
  committed
- Module 0.3 — Command Line, for basic navigation in both Bash and PowerShell

You do not need to have memorized these — you need to be willing to reread one if a step below
doesn't make sense.

**Tools required** (all free, already covered in Stage 0): Windows PowerShell, WSL2/Ubuntu with
Bash, Python 3, Git, and VS Code.

**Not required:** Docker, any cloud account, GPUs, or advanced programming.

**Safety rules:**

1. **Build this project in a separate, new repository** — for example,
   `~/engineering-foundations/` — never inside this `AI Engineering` curriculum folder.
2. **Do all work inside that dedicated repository/practice directory.** Confirm your current
   directory (`pwd`/`Get-Location`) before creating any file.
3. **No command in this guide deletes anything or requires `sudo`/administrator rights.** If a step
   ever seems to need one of those, stop — that isn't part of this project.
4. **Every value in this project is real system information you're allowed to see (your own tool
   versions) — never a password, API key, or token.** Nothing here should ever require a secret.

## 5. Deliverables

By the end, your `engineering-foundations` repository should contain:

- [ ] `README.md` — a short description of the repository and its purpose.
- [ ] `.gitignore` — excluding `.env`, virtual environments, Python caches, local databases, and
      editor-specific local files.
- [ ] `environment-report.md` — your full health-check report (Section 8).
- [ ] One clean, meaningful Git commit containing all of the above.

## 6. Industry-standard workflow

Use this loop for every step below:

```text
Goal → assumptions → smallest experiment → observe output/logs
→ explain findings → verify → document
```

In practice, for each step:

1. **Goal** — one sentence: what are you trying to confirm?
2. **Assumptions** — one sentence: what do you expect the command to report, before running it?
3. **Smallest experiment** — run the smallest command that can answer the question.
4. **Observe output/logs** — read the actual output; don't skim it.
5. **Explain findings** — write, in your own words, what the output tells you.
6. **Verify** — if anything is surprising (a missing tool, an unexpected version), check it again
   before concluding.
7. **Document** — record the exact command and its exact output in `environment-report.md` before
   moving to the next check.

## 7. Step-by-step instructions

### 7.1 Create a separate `engineering-foundations` practice repository

```bash
mkdir -p ~/engineering-foundations
cd ~/engineering-foundations
pwd
git init
```

(PowerShell: `New-Item -ItemType Directory -Force ~/engineering-foundations`, then
`Set-Location ~/engineering-foundations`, then `Get-Location`, then `git init`.)

- `git init` — turns this directory into a new, empty Git repository (`10-git-github-and-ssh-basics.md`,
  Section 4).

### 7.2 Create a concise README

```bash
echo "# Engineering Foundations

A version-controlled record of my developer-environment setup and Stage 0 practice projects." > README.md
```

Keep it short — its job here is only to explain what this repository is, not to document every
detail (that's `environment-report.md`'s job).

### 7.3 Record core tool versions

Run each of these, one at a time, and copy the **exact** output into your notes — don't
paraphrase.

**Windows / PowerShell:**

```powershell
[System.Environment]::OSVersion.VersionString
$PSVersionTable.PSVersion
wsl --list --verbose
git --version
code --version
```

- `[System.Environment]::OSVersion.VersionString` — the Windows version string.
- `$PSVersionTable.PSVersion` — the installed PowerShell version.
- `wsl --list --verbose` — lists installed WSL distributions and their versions.
- `git --version` — the installed Git version.
- `code --version` — VS Code's version (run from a terminal where the `code` command is available).

**WSL2/Ubuntu — Bash:**

```bash
lsb_release -a
bash --version
python3 --version
git --version
```

- `lsb_release -a` — the Ubuntu/Linux distribution version.
- `bash --version` — the installed Bash version.
- `python3 --version` — the installed Python version (Module 0.4's
  [`11-reproducible-python-workspaces-with-uv.md`](../11-reproducible-python-workspaces-with-uv.md),
  Section 2, covers this in depth).
- `git --version` — confirms Git is available inside WSL2 too (it may be a different install from
  the Windows one).

Record every command and its real output in `environment-report.md` as you go (Section 8 gives the
template).

### 7.4 Verify PowerShell and Bash/WSL can navigate and display a text file

```bash
mkdir -p ~/practice-shell
echo "hello from bash" > ~/practice-shell/test.txt
cd ~/practice-shell
cat test.txt
```

```powershell
New-Item -ItemType Directory -Force ~/practice-shell
Set-Location ~/practice-shell
Get-Content test.txt
```

- `cat`/`Get-Content` — print a file's contents. Confirm the same file's content is visible from
  **both** shells (WSL2's `~/practice-shell` and Windows's own filesystem are different locations
  unless you're deliberately crossing between them — see
  [`../03-Command-Line/11-safe-terminal-and-filesystem-literacy.md`](../../03-Command-Line/11-safe-terminal-and-filesystem-literacy.md),
  Section 3, for why paths differ between the two).

**Goal here:** confirm both shells can open, navigate to, and read a plain-text file — the minimum
proof each environment is actually usable for the work ahead.

### 7.5 Document every command, in plain English

For each command you ran in Steps 7.3–7.4, write one sentence explaining what it does and why you
ran it — in your own words, not copied from this guide. This is the single habit that turns a list
of commands into something you can actually explain later, in an interview or to a teammate.

### 7.6 Create a safe `.gitignore`

```bash
echo ".env
.venv/
__pycache__/
*.pyc
*.sqlite3
.vscode/
*.log" > .gitignore
```

Each line matters, following
[`../10-git-github-and-ssh-basics.md`](../10-git-github-and-ssh-basics.md), Section 8:

- `.env` — real secrets (never applicable to this project, but excluded on principle from the
  start).
- `.venv/`, `__pycache__/`, `*.pyc` — Python environment and cache files, reproducible from
  `pyproject.toml`, never needed in history.
- `*.sqlite3` — local databases, machine-specific.
- `.vscode/` — editor-specific local settings, not shared project configuration.
- `*.log` — local log output.

**Create this file before your first `git add`**, so nothing you don't intend to track is ever
staged.

### 7.7 Inspect `git status` and `git diff`

```bash
git status
git diff
```

Read both fully, following
[`../12-secrets-and-local-security-hygiene.md`](../12-secrets-and-local-security-hygiene.md),
Section 8's habit — confirm exactly `README.md`, `.gitignore`, and `environment-report.md` are what
would be staged, and nothing else.

### 7.8 Make one clean, descriptive commit

```bash
git add README.md .gitignore environment-report.md
git status
git commit -m "docs: add environment health check"
git log
```

Confirm `git log` shows exactly one commit, with that message, containing all three files.

### 7.9 Verify reproducibility and the absence of secrets

```bash
git show --stat HEAD
grep -ri "key\|password\|token\|secret" environment-report.md README.md
```

- `git show --stat HEAD` — lists exactly which files are in your one commit — confirm it matches
  Section 5's deliverables list precisely.
- The `grep` command searches your own files for words that commonly indicate an accidentally
  included secret — it should find nothing, since this project never uses real credentials at all.
  Finding nothing is the expected, correct result.

## 8. A suggested structure for `environment-report.md`

```markdown
# Environment Health Check

**Date:** <the date you ran this>

## Tool Versions

| Tool | Version | Command used |
|---|---|---|
| Windows | ... | `[System.Environment]::OSVersion.VersionString` |
| PowerShell | ... | `$PSVersionTable.PSVersion` |
| WSL distribution | ... | `wsl --list --verbose` |
| Ubuntu/Linux | ... | `lsb_release -a` |
| Bash | ... | `bash --version` |
| Python | ... | `python3 --version` |
| Git | ... | `git --version` |
| VS Code | ... | `code --version` |

## Cross-Shell Verification

- PowerShell: navigated to `~/practice-shell` and displayed `test.txt` — [confirmed / not confirmed]
- Bash/WSL: navigated to `~/practice-shell` and displayed `test.txt` — [confirmed / not confirmed]

## Commands Explained

For each command above, one sentence explaining what it does and why it was run (Section 7.5).

## Notes

Anything unexpected you observed, and how you resolved or explained it.
```

## 9. Expected observations and acceptance criteria

- Every tool-version command produces a real, specific version string — not an error, and not a
  placeholder like "unknown."
- Both PowerShell and Bash/WSL successfully display `test.txt`'s contents.
- `git status` shows a clean working tree immediately after your one commit.
- `git log` shows exactly one commit.
- The `grep` check in Step 7.9 returns no matches.
- `environment-report.md` contains real, observed output for every claim — not descriptions of what
  "should" happen.

## 10. Common problems and safe troubleshooting

| Problem | Likely cause | Safe next step |
|---|---|---|
| `code: command not found` | VS Code's terminal command isn't installed | Open VS Code, run "Shell Command: Install 'code' command in PATH" from its command palette, then open a **new** terminal. |
| `wsl --list --verbose` fails or shows nothing | WSL2 isn't installed, or you're not running it from Windows PowerShell | Confirm you're in Windows PowerShell (not WSL2's own Bash) when running this specific command. |
| `python3: command not found` in WSL2 | Python isn't installed there yet | Install Python 3 via Ubuntu's package manager, following its own official documentation. |
| Bash and PowerShell show different content for the "same" file | They're actually looking at two different filesystem locations | Reread [`../../03-Command-Line/11-safe-terminal-and-filesystem-literacy.md`](../../03-Command-Line/11-safe-terminal-and-filesystem-literacy.md), Section 3, on Windows vs. WSL2 path differences. |
| A file you didn't intend appears in `git status` | `.gitignore` wasn't created before the file existed, or a broad `git add .` was used without checking first | Confirm `.gitignore` lists the right pattern, then stage files individually and recheck `git status` before committing. |

## 11. Interview-practice questions

Practice answering these aloud, in 60–90 seconds each, using your own `environment-report.md`:

1. **"How would you verify a new machine is actually ready for development work?"**
   Guidance: describe checking specific tool versions and cross-shell file access with real
   commands, not just "install everything and hope."

2. **"Why document your environment setup instead of just remembering it?"**
   Guidance: connect to reproducibility and having a baseline to compare against when something
   breaks later — exactly this project's purpose.

3. **"What goes in a `.gitignore`, and why create it before your first commit?"**
   Guidance: name specific categories (secrets, environments, caches, editor files) and explain
   that `.gitignore` only prevents tracking files it doesn't already know about.

4. **"How do you make sure a commit doesn't contain something it shouldn't?"**
   Guidance: describe checking `git status` and `git diff` before every commit — the exact habit
   from Step 7.7.

## 12. Final completion gate

You have completed this project when all statements below are true:

- [ ] I created a separate `engineering-foundations` repository, outside this curriculum folder.
- [ ] I recorded real, observed version output for every tool in Section 7.3.
- [ ] I verified, with real evidence, that both PowerShell and Bash/WSL can display the same test
      file.
- [ ] I documented every command I ran in plain English, in my own words.
- [ ] I created `.gitignore` before my first commit, correctly excluding secrets, environments,
      caches, and editor files.
- [ ] I checked `git status` and `git diff` before committing.
- [ ] I made exactly one clean, descriptive commit containing all four deliverables.
- [ ] I verified my commit contains no secrets and matches the deliverables list exactly.

Once every box is checked, this project satisfies Stage 0 Project 0.1. Continue with
[`02-python-workspace-bootstrap.md`](./02-python-workspace-bootstrap.md), or return to
[`../../00-Stage-0-Overview/learning-plan.md`](../../00-Stage-0-Overview/learning-plan.md) for the
rest of Stage 0.
