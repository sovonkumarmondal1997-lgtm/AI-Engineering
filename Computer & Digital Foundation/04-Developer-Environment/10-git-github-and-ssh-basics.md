# Git, GitHub, and SSH Basics

**Module:** Developer Environment
**Roadmap reference:** Stage 0 — Computer, Linux, and Developer Foundations, Gap 0A — "Git,
GitHub, and SSH basics" (extends Module 0.4 — Developer Environment)
**Concept(s) covered:** repository, working tree, staging area, commit, branch, remote, pull
request, `.gitignore`, GitHub, `git status`, `git add`, `git commit`, `git log`, `git diff`,
`git switch`, `git branch`, `git pull`, `git push`, SSH keys
**Prerequisites:** Module 0.3 — Command Line (navigation, file operations, viewing files)
**Status:** Not Started

---

## Learning Outcomes

By the end of this lesson you will be able to:

- Explain what a repository, working tree, staging area, commit, branch, and remote are, in your
  own words.
- Use `git status`, `git add`, `git commit`, `git log`, and `git diff` to track and inspect changes.
- Use `git switch` and `git branch` to move between and create branches.
- Use `git pull` and `git push` to sync with a remote repository.
- Write small, descriptive commits, checking `git status` and `git diff` before every one.
- Write a `.gitignore` that correctly excludes `.env` files, virtual environments, caches, local
  databases, and keys.
- Explain, at a conceptual level, what a GitHub repository, README, issue, and pull request are.
- Explain the purpose of an SSH key for GitHub authentication, and where to find current, official
  setup instructions when you actually configure one.
- Name what this lesson deliberately does not teach yet, and why.

## Prerequisites

- **Module 0.3 — Command Line**, specifically navigation and file operations
  ([`../03-Command-Line/01-navigation.md`](../03-Command-Line/01-navigation.md),
  [`../03-Command-Line/02-file-operations.md`](../03-Command-Line/02-file-operations.md)) — this
  lesson assumes you're comfortable with `pwd`, `ls`, `cd`, `cp`, `mv`, and creating files from a
  terminal.
- **Module 0.3, Lesson 11** —
  [Safe Terminal and Filesystem Literacy](../03-Command-Line/11-safe-terminal-and-filesystem-literacy.md)
  — the safe-practice-directory habit this lesson uses throughout.
- No prior Git knowledge is assumed. This lesson is the entry point.

## Key Terms

- **Repository (repo)** — a project folder that Git is tracking the history of.
- **Working tree** — the actual files on disk, as you currently see and edit them.
- **Staging area (index)** — a holding area where you place exactly the changes you want included
  in your *next* commit, separate from changes you're not ready to commit yet.
- **Commit** — a saved snapshot of the staged changes, with a message describing what changed and
  why.
- **Branch** — an independent line of commits, letting you work on something without affecting the
  main line of history until you're ready.
- **Remote** — a copy of the repository hosted elsewhere (commonly on GitHub) that you can push to
  and pull from.
- **Pull request (PR)** — a GitHub feature proposing that changes from one branch be reviewed and
  merged into another.
- **`.gitignore`** — a file listing patterns Git should never track, regardless of what exists on
  disk.
- **SSH key** — a pair of cryptographic keys used to prove your identity to a remote server (like
  GitHub) without typing a password each time.

---

## 1. Why Version Control Belongs Here, Not Just "Later"

Every project you build from Stage 1 onward needs three things: a history of what changed and why,
a README explaining what the project is, and a safe way to share or collaborate on it. Git provides
the first; GitHub commonly provides the second and third. Learning this now — before you've written
any real code — means every future project starts with these habits already in place, instead of
being bolted on after something has already gone wrong.

## 2. What Git Actually Is

**Git** is a **version control system**: a tool that records snapshots of a project's files over
time, so you can see what changed, when, and why — and recover any earlier state if needed.

Three ideas sit at the center of how Git works day to day:

```text
Working tree           Staging area            Repository history
(your actual files) →  (what you're about  →   (permanent, named
                        to save)                 snapshots — commits)
```

- The **working tree** is simply your files, exactly as you're editing them right now.
- The **staging area** is where you deliberately choose *which* changes belong in your next
  snapshot — you don't have to commit everything you've touched at once.
- A **commit** takes whatever is staged and saves it permanently in the repository's history, with
  a message.

This three-step shape — edit, stage, commit — is deliberate: it lets you review exactly what you're
about to save before you save it, rather than blindly snapshotting everything.

## 3. Branches and Remotes

A **branch** is an independent line of commits. Every repository starts with one default branch
(commonly named `main`); creating a new branch lets you try something — a new feature, an
experiment — without touching that main line until you're ready to bring the change back in.

A **remote** is a copy of your repository hosted somewhere else — most commonly, a repository on
GitHub. Your local repository and the remote one are separate copies that you deliberately
synchronize, in each direction, using `git push` (send your commits there) and `git pull` (bring
their commits here) — covered in Section 6.

## 4. The Beginner Git Workflow

This is the loop you'll repeat constantly. Practice it inside a dedicated practice directory
(Module 0.3, Lesson 11).

```bash
mkdir -p ~/practice-shell/git-basics
cd ~/practice-shell/git-basics
git init
```

- `git init` — turns the current directory into a new, empty Git repository (creates a hidden
  `.git/` folder that stores all history — you never edit this folder by hand).

```bash
echo "# Git Basics Practice" > README.md
git status
```

- `git status` — shows which files have changed, which are staged, and which are untracked
  (Git has never seen them before). **Run this before almost every other Git command** — it tells
  you exactly what state you're in before you act.

```bash
git add README.md
git status
```

- `git add FILE` — moves a file's current changes into the staging area. Run `git status` again
  afterward and notice the same file now appears under a different heading — staged, not just
  changed.

```bash
git commit -m "docs: add README"
```

- `git commit -m "MESSAGE"` — saves everything currently staged as a new, permanent snapshot, with
  the given message.

```bash
git log
```

- `git log` — shows the history of commits, most recent first: who, when, and the message.

```bash
echo "More notes." >> README.md
git diff
```

- `git diff` — shows the *exact* line-by-line changes in your working tree that are not yet
  staged. Read this before every `git add` — it's your last check on exactly what you're about to
  include.

## 5. Moving Between Branches

```bash
git branch practice-branch
git switch practice-branch
```

- `git branch NAME` — creates a new branch (but does not move you onto it).
- `git switch NAME` — moves you onto the named branch; your working tree now reflects that
  branch's history.

```bash
git branch
```

- `git branch` (no argument) — lists all local branches, with a `*` marking the one you're
  currently on.

**Beginner rule:** always check `git status` after switching branches, before making any change —
confirm you're on the branch you meant to be on.

## 6. Syncing With a Remote

Once a repository has a remote configured (commonly by creating a repository on GitHub first, then
connecting your local one to it — see Section 9):

```bash
git push
```

- `git push` — sends your local commits to the remote, making them visible there.

```bash
git pull
```

- `git pull` — fetches commits from the remote and merges them into your current branch, bringing
  you up to date with anything others (or you, from another machine) have pushed.

**Beginner rule:** run `git pull` before starting new work in a shared repository, so you're
building on the latest version, not an outdated one.

## 7. Writing Small, Descriptive Commits

A good commit does **one** meaningful thing and says what it did:

```text
docs: add environment health check report
fix: correct wrong path in setup script
feat: add hello_environment.py entry point
```

**Why small commits matter:** each one is easy to review, easy to explain, and easy to undo on its
own if something turns out to be wrong — a single giant commit mixing five unrelated changes makes
all three of those things much harder.

**The habit, every time, before committing:**

```bash
git status
git diff
```

Read both. Confirm you're staging exactly what you intend — nothing more, nothing accidentally
included (Section 8 explains why this check matters especially for secrets).

## 8. `.gitignore` — What Must Never Be Committed

A `.gitignore` file lists patterns Git should never track, no matter what exists on disk:

```text
.env
.venv/
__pycache__/
*.pyc
*.sqlite3
*.log
```

**Why each of these matters:**

- **`.env`** — holds real secrets (API keys, passwords) — Lesson 12 covers this in full; it must
  never be committed.
- **`.venv/`** (virtual environments) — large, machine-specific, and fully reproducible from
  `pyproject.toml` (Lesson 11) — committing it bloats the repository for no benefit.
- **`__pycache__/`, `*.pyc`** — Python's own generated cache files — never source code, never
  needed in history.
- **Local databases (`*.sqlite3`) and logs (`*.log`)** — machine-specific, often large, and
  sometimes containing data that shouldn't be shared.

**Practical habit:** create your `.gitignore` **before** your first `git add`, so nothing you
didn't mean to track is ever staged in the first place.

## 9. GitHub — Repositories, README, Issues, and Pull Requests

**GitHub** is a website that hosts Git repositories remotely, and adds collaboration features on
top of plain Git. At a conceptual level:

- **Repository (on GitHub)** — the hosted copy of your project; created through GitHub's web
  interface, then connected to your local repository as a remote (Section 6).
- **README** — the file (`README.md`) GitHub displays automatically on a repository's main page —
  the first thing anyone sees, and where you explain what the project is and how to use it.
- **Issue** — a tracked note about a bug, task, or idea related to the repository — a lightweight
  way to record "this needs attention" without it being code yet.
- **Pull request (PR)** — a proposal to merge one branch's commits into another, giving a
  reviewer(s) a place to comment on the exact changes before they become part of the main history.

This lesson does not walk through GitHub's interface step by step — it changes over time, and
GitHub's own documentation is the authoritative, current source. The goal here is that you recognize
each term and its purpose before you encounter it.

## 10. SSH Keys and GitHub Authentication

An **SSH key** is a pair of cryptographic keys — a private key you keep secret on your machine, and
a public key you register with GitHub — that together let you authenticate to GitHub (for example,
to `git push`) without typing a username and password every time.

**The concept, in one sentence:** your machine proves it holds the private key; GitHub checks that
against the public key you registered; if they match, you're authenticated.

**This lesson does not walk through generating or registering an SSH key.** Exact commands and
GitHub's interface both change over time, and getting this step wrong (or following outdated
instructions) is a common source of confusion. When you're ready to actually configure this,
**follow GitHub's own, current official documentation** — search for "GitHub SSH key setup" on
`docs.github.com`, GitHub's official documentation site. Understanding *why* this mechanism exists
(Section-level conceptual understanding) is this lesson's goal; the exact setup steps belong to
GitHub's own, always-current source of truth.

## 11. Practical Walkthrough

Inside your practice directory from Section 4:

```bash
cd ~/practice-shell/git-basics
echo ".env
.venv/
__pycache__/
*.pyc" > .gitignore
git add .gitignore README.md
git status
git commit -m "chore: add gitignore and initial README"
git log
```

Make a second, unrelated change and repeat the loop, deliberately checking `git diff` first:

```bash
echo "## Notes" >> README.md
git diff
git add README.md
git commit -m "docs: add notes section to README"
git log
```

Confirm your history now shows two separate, small, descriptive commits — not one large, vague one.

## 12. Common Mistakes and Safe Troubleshooting

| Problem | Likely cause | Safe next step |
|---|---|---|
| A file you didn't mean to commit shows up in `git status` as staged | You ran a broad `git add .` without checking `git status` first | Unstage it and check status again before committing; going forward, review `git status` before every `git add`. |
| `git commit` says "nothing to commit" | Nothing is staged — `git add` wasn't run, or nothing actually changed | Run `git status` and `git diff` to see the real current state before assuming the commit should work. |
| A secret ends up in a commit despite `.gitignore` | The file was already tracked by Git *before* it was added to `.gitignore` — `.gitignore` only prevents tracking *new* files | See Lesson 12, Section 6 and Section 10 — this requires rotating the secret, not just editing `.gitignore`. |
| `git push` fails, asking to `git pull` first | The remote has commits your local repository doesn't have yet | Run `git pull` first, resolve anything it reports, then push again — never force-push as a first response. |
| Unsure which branch you're on | Switched branches earlier and lost track | Run `git branch` — the `*` marks your current branch — and `git status`, before making any further change. |

## 13. What Not to Learn Yet

Deliberately out of scope for this lesson: rebasing, advanced branching strategies, Git internals
(how commits, trees, and blobs are actually stored), and release management (tags, versioning
strategies). These are real, useful topics — just not foundational ones. Trying to learn them before
this lesson's basics are solid tends to produce confusion, not confidence.

## 14. Why This Matters for AI Engineering

- **Every AI project needs a reproducible history.** A model-training script, a prompt template, or
  an agent's configuration all change over time — Git is how you know what changed and can revert
  a regression.
- **`.gitignore` discipline (Section 8) is the first line of defense against leaking secrets** —
  covered fully in Lesson 12, but the habit starts here, before you ever hold a real API key.
- **Small, descriptive commits** make it possible to bisect a regression later — find exactly which
  change introduced a bug in a model's behavior or a service's reliability.
- **Pull requests** are how AI teams review changes to prompts, evaluation code, and model configs
  before they reach production — the same review discipline as any other software change.

---

## Exercises

1. Initialize a new practice repository, create a `.gitignore` before adding any files, and make
   your first commit.
2. Make a second change, run `git diff` before staging it, and write down — before committing —
   what you expect `git log` to show afterward.
3. Create a branch, switch to it, make a change, and confirm with `git branch` and `git status`
   that you're working on the branch you intended.
4. Deliberately create a file named `.env` with a fake placeholder value (e.g.
   `EXAMPLE_KEY=placeholder`) and confirm `git status` does **not** list it as untracked, once it's
   listed in `.gitignore`.
5. In your own words, write one sentence each defining: repository, staging area, commit, branch,
   remote, and pull request — without copying this lesson's wording.

## Expected Results

- **Exercise 1:** `git log` shows exactly one commit, and `git status` reports a clean working
  tree afterward.
- **Exercise 2:** your written prediction of `git log`'s output matches what you actually see.
- **Exercise 3:** `git branch` shows your new branch with a `*` next to it after switching.
- **Exercise 4:** `.env` never appears in `git status`'s output — confirming `.gitignore` is
  working before any real secret is ever involved.
- **Exercise 5:** your definitions should closely match this lesson's Section 2 and Section 3
  content, phrased in your own words.

---

## Summary

Git tracks a project's history through a deliberate three-step loop: edit your working tree, stage
exactly what you want to save, and commit it with a descriptive message — checking `git status` and
`git diff` before every commit. Branches let you work independently without disturbing the main
history; remotes (commonly on GitHub) let you push and pull to synchronize with others. A
`.gitignore`, written before your first commit, keeps secrets, virtual environments, and caches out
of history entirely. GitHub adds a README, issues, and pull requests on top of plain Git for
collaboration. SSH keys authenticate you to GitHub without a password — set them up later, following
GitHub's own current documentation. Rebasing, advanced branching, Git internals, and release
management are real topics, but not this lesson's — the beginner workflow above is enough to work
safely and reproducibly from here on.

## Completion Checklist

- [ ] I can explain repository, working tree, staging area, commit, branch, and remote in my own
      words.
- [ ] I used `git status`, `git add`, `git commit`, `git log`, and `git diff` in a real practice
      repository.
- [ ] I created and switched to a branch, and confirmed which branch I was on before making changes.
- [ ] I wrote a `.gitignore` before my first commit, correctly excluding `.env`, virtual
      environments, caches, and local databases.
- [ ] I can explain, conceptually, what a GitHub repository, README, issue, and pull request are.
- [ ] I can explain what an SSH key does for GitHub authentication, and know to follow GitHub's own
      current documentation when actually configuring one.
- [ ] I can name what this lesson deliberately did not teach, and why that's the right scope for
      now.
- [ ] I completed the exercises above and my results match the expected results.

---

_This lesson is complete. It covers the Git and GitHub fundamentals from Stage 0 Gap 0A. It
intentionally does not teach rebasing, advanced branching strategies, Git internals, or release
management — those remain later, more advanced topics. Secrets hygiene is covered next, in
[`12-secrets-and-local-security-hygiene.md`](./12-secrets-and-local-security-hygiene.md)._
