# Secrets and Local Security Hygiene

**Module:** Developer Environment
**Roadmap reference:** Stage 0 — Computer, Linux, and Developer Foundations, Gap 0E — "Secrets
and local security hygiene" (extends Module 0.4 — Developer Environment)
**Concept(s) covered:** secrets (API keys, passwords, tokens, private keys, connection strings),
`.env`, `.env.example`, environment variables, `.gitignore`, secure local credential storage,
trusted extensions and packages, secret exposure response
**Prerequisites:** `10-git-github-and-ssh-basics.md`, `11-reproducible-python-workspaces-with-uv.md`
**Status:** Not Started

---

## Learning Outcomes

By the end of this lesson you will be able to:

- List the categories of information that count as a secret, and explain why.
- Explain why a secret must never be committed to Git, pasted into code, written to a log, or
  included in a screenshot or public issue.
- Create and use a `.env` file and a matching `.env.example`, correctly.
- Explain how environment variables let a program use a secret without it being written into code.
- Write a `.gitignore` entry that keeps `.env` out of version control, and explain why `.gitignore`
  alone is not enough once a secret has already been committed.
- Check `git status` and `git diff` before every commit, specifically to catch an accidental secret.
- Explain what "trusted extensions and packages" means, and why installing from unverified sources
  is a real risk.
- Explain exactly what to do — and why — if a secret is ever exposed.

## Prerequisites

- **`10-git-github-and-ssh-basics.md`** — `git status`, `git diff`, `.gitignore`, and commit
  hygiene, all of which this lesson applies specifically to secrets.
- **`11-reproducible-python-workspaces-with-uv.md`** — the project structure (`pyproject.toml`,
  a project folder) this lesson's `.env` examples sit inside.

## Key Terms

- **Secret** — any piece of information that grants access or proves identity, and that must not
  be shared publicly: an API key, password, token, private key, or connection string.
- **API key** — a string a service issues you to authenticate your requests to it.
- **Token** — a piece of data (often temporary) granting access to a system or resource.
- **Connection string** — a piece of text (often including a password) describing how to connect
  to a database or service.
- **Environment variable** — a named value available to a running process, set outside the
  program's own source code (Module 0.2,
  [Environment Variables](../02-Operating-System-Fundamentals/09-environment-variables.md)).
- **`.env` file** — a local, untracked file holding real environment variable values, including
  secrets, for a project.
- **`.env.example`** — a companion file listing the *names* of the variables a project needs, with
  placeholder (not real) values, safe to commit.
- **Credential rotation** — replacing a secret with a brand-new one and invalidating the old one,
  the only real fix once a secret has been exposed.

---

## 1. Why Secrets Hygiene Belongs in Stage 0, Before Any Real API Key

You will use API keys very early — the moment you call any model provider or external service. If
the habits in this lesson aren't automatic *before* that first real key exists, the first mistake
happens with something that actually matters. This lesson exists so the discipline is already
built, using only safe, fake placeholder values, before you ever hold something real.

> **Every example value in this lesson is a placeholder.** None of them are real, working
> credentials — do not reuse any string in this lesson as an actual secret.

## 2. What Counts as a Secret

A **secret** is any piece of information that grants access to something or proves an identity, and
that would let someone else misuse it if they obtained it:

- **API keys** — e.g. `sk-EXAMPLE-PLACEHOLDER-0000000000` (a fake, illustrative shape only).
- **Passwords** — for any account, service, or database.
- **Tokens** — often short-lived, but still grant real access while valid.
- **Private keys** — including SSH private keys (Lesson 10, Section 10).
- **Connection strings** — e.g. `postgresql://user:PLACEHOLDER_PASSWORD@localhost:5432/db` — often
  overlooked because they look like configuration, but the password inside makes them a secret too.

**The test to apply:** if this value being seen by a stranger could let them access an account,
service, or system on your behalf, it's a secret — treat it accordingly, even if it "looks like"
ordinary configuration.

## 3. Why Secrets Must Never Be Committed, Pasted, Logged, or Screenshotted

Each of these is a distinct, real leak path — not just a hypothetical:

- **Committed to Git** — becomes part of permanent history (Section 6 explains why even deleting
  it later doesn't undo this).
- **Pasted into code** — visible to anyone who reads the source file, and often committed along
  with it without a second thought.
- **Written to a log** — logs are frequently less carefully protected than source code, and often
  shared more widely (shipped to a log-aggregation service, pasted into a support ticket).
- **Included in a screenshot** — shared in chat, a bug report, or a presentation, a screenshot can
  expose a key visible in a terminal or `.env` file just as effectively as pasting the text itself.
- **Posted in a public GitHub issue** — issues are public by default on public repositories, and
  pasting an error message that happens to include a key is a common, easy mistake.

**The unifying principle:** a secret's value should exist in as few places as possible, and never
in any place that's shared, logged, or version-controlled.

## 4. `.env` Files and Environment Variables

A `.env` file holds real configuration values, including secrets, as simple `NAME=value` lines:

```text
DATABASE_URL=postgresql://user:PLACEHOLDER_PASSWORD@localhost:5432/mydb
EXAMPLE_API_KEY=sk-EXAMPLE-PLACEHOLDER-0000000000
```

A program reads these as **environment variables** — values available to a running process without
being written into its source code at all (Module 0.2's
[Environment Variables](../02-Operating-System-Fundamentals/09-environment-variables.md) lesson
covers the underlying mechanism). This is *why* `.env` matters: the secret lives in one local file,
never inside the code itself, so the code can be shared, committed, and reviewed freely while the
secret stays behind.

## 5. `.env.example` — Sharing Structure Without Sharing Secrets

A `.env.example` file lists the same variable *names* your project needs, with placeholder values,
and **is safe to commit**:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
EXAMPLE_API_KEY=your-api-key-here
```

**Why this matters:** anyone cloning your project can see *exactly* which variables they need to
set, without your real values ever being exposed. Create `.env.example` alongside `.env` from the
start of a project — it's part of what makes a project reproducible (Lesson 11, Section 12).

## 6. `.gitignore` as Your Safety Net — and Its Limit

```text
.env
```

One line in `.gitignore` (Lesson 10, Section 8) stops Git from ever tracking `.env` — as long as it
was added **before** `.env` was ever committed.

**The critical limit, stated precisely:** `.gitignore` only prevents Git from tracking a file *it
doesn't already know about*. If `.env` was committed even once, before `.gitignore` excluded it,
that secret is now in your repository's permanent history — adding it to `.gitignore` afterward
stops *future* changes to the file from being tracked, but does **not** remove the already-committed
version, or the secret's value, from history. Section 10 covers what to actually do at that point.

## 7. Secure Local Credential Storage, Conceptually

Beyond a project's own `.env` file, most operating systems provide a **secure credential store** —
a system-managed, encrypted place to keep secrets that don't belong to a specific project (for
example, a personal GitHub token used across many projects): Windows Credential Manager, macOS
Keychain, or a Linux secret service. This lesson does not walk through using one — recognize the
concept now (a system-level, more permanent alternative to a project's `.env`), and reach for your
OS's own current documentation when a secret genuinely spans more than one project.

## 8. The Habit: Check `git status` and `git diff` Before Every Commit

This is Lesson 10's habit, applied specifically as a secrets safeguard:

```bash
git status
git diff
```

**Read both, every time, before `git add` and `git commit`** — specifically looking for anything
that shouldn't be there: a `.env` file appearing in the list, or a line in `git diff` containing
what looks like a real key or password pasted directly into a source file. This thirty-second habit
is the single most effective, lowest-effort defense against ever committing a secret by accident.

## 9. Trusted Extensions, Packages, and Updates

Secrets hygiene isn't only about your own files — it also includes what code you let run on your
machine at all:

- **Install extensions and packages only from trusted, well-known publishers** — an editor
  extension or a Python package can run arbitrary code on your machine; an unverified or
  low-reputation source is a real risk, not a theoretical one.
- **Avoid unverified installation commands** — a command copied from an untrusted forum post or
  video, piped directly into a shell without reading what it does, can do anything on your machine.
  Read a command before running it (Module 0.3's engineering-thinking habit, Module 0.4's own
  discipline).
- **Keep your operating system and packages updated** — many security fixes only take effect once
  you update; an outdated system is a wider, unnecessary attack surface.

## 10. What to Do If a Secret Is Exposed

If a real secret is ever committed, pasted publicly, or otherwise exposed, follow this order —
**precisely**, because the natural instinct (quietly delete the line) is not sufficient:

1. **Revoke or rotate the secret immediately**, at its source (the provider's dashboard or
   settings) — this is the only step that actually stops it from being usable. Deleting a line in a
   later Git commit does **not** remove the secret from earlier history, and does **not** stop
   anyone who already saw it from using it.
2. **Only after rotating**, clean up the repository if you want the old (now harmless) value out of
   the visible history too — this is a "keeping things tidy" step, not the security fix itself.
3. **Update wherever the new value is needed** — your local `.env`, any deployed service, any
   teammate who needs it — using the same safe channels (not the same leak path that caused the
   exposure).

**The one sentence to remember:** rotation is the fix; everything else is cleanup.

---

## Exercises

1. Create a practice project folder with `.gitignore` already containing `.env`, **before**
   creating `.env` itself. Add a fake, placeholder value to `.env`, run `git status`, and confirm
   it does not appear.
2. Create a matching `.env.example` listing the same variable names with placeholder values, and
   commit only that file.
3. Deliberately paste a fake, placeholder-looking "key" directly into a `.py` file (something
   clearly not real, like `EXAMPLE_API_KEY = "sk-EXAMPLE-PLACEHOLDER-0000000000"`), then run
   `git diff` and confirm you can see it clearly in the output — this is the check that would have
   caught it before a commit.
4. Write, in your own words, the three-step response from Section 10, in the correct order,
   without looking.
5. List three things you would check on a new machine before installing an editor extension or a
   package, based on Section 9.

## Expected Results

- **Exercise 1:** `.env` never appears in `git status`'s output, even though the file exists on
  disk — confirming `.gitignore` worked because it was in place first.
- **Exercise 2:** `git log`/`git status` show `.env.example` as tracked and `.env` as not —
  matching Section 5 and Section 6.
- **Exercise 3:** the fake key is clearly visible in `git diff`'s output — direct evidence that this
  check would catch a real accidental secret before it's committed.
- **Exercise 4:** your answer should correctly say "revoke/rotate first," matching Section 10 — not
  "delete the line first."
- **Exercise 5:** your answer should reference source trust and verification, matching Section 9.

---

## Summary

A secret is anything that grants access or proves identity — API keys, passwords, tokens, private
keys, and connection strings — and it must never be committed, pasted into code, logged,
screenshotted, or posted publicly. `.env` holds real values locally, read as environment variables
so secrets never live in source code; `.env.example` shares the required variable *names* safely.
`.gitignore` prevents tracking `.env`, but only if it's in place *before* the file is ever
committed — once committed, the fix is rotation, not deletion. Checking `git status` and `git diff`
before every commit is the simplest, most reliable habit against an accidental leak. Install
extensions and packages only from trusted sources, and keep your system updated. If a secret is
ever exposed, revoke or rotate it immediately — that is the actual fix; everything else is cleanup
afterward.

## Completion Checklist

- [ ] I can list the categories of secrets (API keys, passwords, tokens, private keys, connection
      strings) and explain the test for identifying one.
- [ ] I can explain why each leak path (commit, paste, log, screenshot, public issue) is a real
      risk, not a hypothetical one.
- [ ] I created a working `.env` and matching `.env.example`, using only placeholder values.
- [ ] I confirmed `.gitignore` correctly kept `.env` out of `git status`, having set it up before
      creating the file.
- [ ] I can explain why `.gitignore` alone does not fix an already-committed secret.
- [ ] I practiced checking `git status` and `git diff` specifically to catch a fake secret before
      committing.
- [ ] I can explain what "trusted extensions and packages" means and why it matters.
- [ ] I can state, correctly ordered and from memory, what to do if a secret is exposed.
- [ ] I completed the exercises above and my results match the expected results.

---

_This lesson is complete. It covers secrets and local security hygiene from Stage 0 Gap 0E,
building on `10-git-github-and-ssh-basics.md`'s Git habits and `11-reproducible-python-workspaces-with-uv.md`'s
project structure. It intentionally does not teach cloud secret managers, encryption internals, or
organizational security policy — those remain later, more advanced topics. Evidence-based debugging
— useful the moment any of this goes wrong — is covered next, in
[`13-evidence-based-debugging-and-notes.md`](./13-evidence-based-debugging-and-notes.md)._
