# Module 0.4 Projects — Developer Environment

**Status:** Not Started
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Module 0.4 — "Developer
Environment," audit evidence for Section 2, and Projects 0.1 and 0.4

## Why these projects exist

Reading this module's numbered concept files — VS Code, the debugger, virtual environments,
`pyproject.toml`, Git and GitHub basics, reproducible Python workspaces with `uv`, secrets hygiene,
and evidence-based debugging — tells you what each tool and habit is for. It does not, by itself,
prove you can actually set up a working, reproducible, version-controlled developer environment
from a clean terminal. The Stage 0 roadmap is explicit about this: **"completed" means you studied
or practiced the module. It does not automatically mean the skill is operational.**

These two projects exist to close that gap — turning individual tools you've read about into a
real, documented setup you built yourself, with evidence you can point to.

## Complete these projects in a separate practice repository

**Do not build these projects inside this curriculum folder (`AI Engineering/`).** Each project
guide instructs you to create its own, separate Git repository — for example, the
`engineering-foundations` repository named in the Stage 0 roadmap's Gap 0A — outside this
repository entirely. This curriculum folder holds the lessons; your own practice repository holds
the evidence that you can apply them. Keeping the two separate also means you never risk mixing a
real (if placeholder-only) practice project with this documentation project's own history.

## Expected evidence, documentation, Git hygiene, and secret safety

- Each project's deliverables (listed in its own guide) are real files you create — a report, a
  script, a README — not descriptions of what you *would* do. A guide's completion gate is only
  satisfied by evidence you can actually show.
- Write findings and explanations in your own words. Text you cannot defend out loud does not count
  as evidence of understanding.
- Follow Git hygiene from
  [`../10-git-github-and-ssh-basics.md`](../10-git-github-and-ssh-basics.md) throughout: small,
  descriptive commits, and checking `git status` and `git diff` before every one.
- Follow secrets hygiene from
  [`../12-secrets-and-local-security-hygiene.md`](../12-secrets-and-local-security-hygiene.md)
  throughout: real secrets never belong in these projects at all — every `.env` value used is a
  safe placeholder, and `.gitignore` excludes `.env` from the very first commit.
- Treat every unexpected result as evidence, not a failure: record what you expected, what actually
  happened, and what you checked next, following
  [`../13-evidence-based-debugging-and-notes.md`](../13-evidence-based-debugging-and-notes.md).

## Projects in this module

Complete these in order — each builds on habits the previous one established.

| Order | Project | Focus |
|---|---|---|
| 1 | [`01-developer-environment-health-check.md`](./01-developer-environment-health-check.md) | Project 0.1 — verifying and documenting your machine's developer-environment setup, with your first version-controlled commit |
| 2 | [`02-python-workspace-bootstrap.md`](./02-python-workspace-bootstrap.md) | Project 0.4 — building a minimal, reproducible Python project with `uv`, and debugging a real traceback |

For the full set of Stage 0 projects (Projects 0.1–0.5 across every module), see
[`../../00-Stage-0-Overview/learning-plan.md`](../../00-Stage-0-Overview/learning-plan.md), Section
5 — "Practical projects."
