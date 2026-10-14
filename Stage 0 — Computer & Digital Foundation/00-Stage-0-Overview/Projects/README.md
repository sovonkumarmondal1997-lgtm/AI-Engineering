# 00 — Stage 0 Projects — Incident Simulation

**Status:** Not Started
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Section 5 — "Practical
projects," Project 0.5 — "Stage 0 Incident Simulation"

## Why this folder exists

This folder holds the **Stage 0 capstone project**: a single, complete, evidence-based incident
investigation that draws on everything taught across Modules 01–04 — filesystem literacy, process
and port diagnosis, local networking, reproducible Python environments, Git hygiene, and secrets
safety — and turns it into one real, written postmortem.

Every other project in Stage 0 practices one skill at a time. This one asks you to use several of
them together, the way a real engineer actually would: something breaks, and you have to find out
why using evidence, fix it safely, and write down what happened.

## Why engineers document failures using evidence, not assumptions

A guess about why something broke is not the same as knowing why it broke. Two people can both
"fix" the same problem — one by actually finding the cause, one by getting lucky — and only one of
them can explain it to a teammate, prevent it from happening again, or trust that it's really
fixed. This project exists to build the habit, from Stage 0 onward, of treating every failure as
something to investigate with real, checkable evidence — the exact discipline taught in
[`../../04-Developer-Environment/13-evidence-based-debugging-and-notes.md`](../../04-Developer-Environment/13-evidence-based-debugging-and-notes.md) —
rather than something to patch and forget.

## Complete this project in a separate practice directory or repository

**Do not perform this project's practical exercise inside this curriculum folder
(`AI Engineering/`).** Use a dedicated, separate practice directory (for example,
`~/practice-shell/stage-0-incident/`) or your own `engineering-foundations` practice repository
from Stage 0's earlier projects. This curriculum folder holds the lessons and guides; your own
practice space holds the evidence that you can apply them safely, without any risk to this
repository or its history.

## Expected evidence, documentation, Git hygiene, and secret safety

- Your deliverables (Section 5 of the project guide) are real files and real command output you
  produced yourself — not a description of what you expect would happen.
- Write your postmortem in your own words. An explanation you cannot defend out loud does not count
  as evidence of understanding.
- Follow Git hygiene from
  [`../../04-Developer-Environment/10-git-github-and-ssh-basics.md`](../../04-Developer-Environment/10-git-github-and-ssh-basics.md):
  small, descriptive commits, and checking `git status` and `git diff` before every one.
- Follow secrets hygiene from
  [`../../04-Developer-Environment/12-secrets-and-local-security-hygiene.md`](../../04-Developer-Environment/12-secrets-and-local-security-hygiene.md):
  never include a real secret, API key, password, token, or private key anywhere in your saved
  evidence — use only safe placeholders, and never capture or save sensitive log content.
- Never stop a process, change a permission, or run a command against anything you have not
  personally created and confirmed for this exercise — the project guide repeats this rule at every
  relevant step.

## Project

| Project | Focus |
|---|---|
| [`01-stage-0-incident-simulation.md`](./01-stage-0-incident-simulation.md) | Project 0.5 — a complete, evidence-based incident investigation and postmortem; the Stage 0 capstone |

For the full set of Stage 0 projects (Projects 0.1–0.5 across every module), see
[`../learning-plan.md`](../learning-plan.md), Section 5 — "Practical projects."
