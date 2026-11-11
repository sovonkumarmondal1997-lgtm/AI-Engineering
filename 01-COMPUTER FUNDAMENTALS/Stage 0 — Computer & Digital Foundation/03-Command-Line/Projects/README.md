# Module 0.3 Projects — Command Line

**Status:** Not Started
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Module 0.3 — "Command
Line," audit evidence for Section 2, and Project 0.2

## Why these projects exist

Reading this module's numbered concept files — including navigation, file operations, text
processing, pipes and redirection, and the new
[Safe Terminal and Filesystem Literacy](../11-safe-terminal-and-filesystem-literacy.md) and
[Shell Quoting and Standard Streams](../12-shell-quoting-and-standard-streams.md) lessons — tells
you what each command-line tool does. It does not, by itself, prove you can combine them to answer
a real question about a real (if synthetic) set of files. The Stage 0 roadmap is explicit about
this: **"completed" means you studied or practiced the module. It does not automatically mean the
skill is operational.**

These projects exist to close that gap: turning individual commands you've read about into an
investigation you actually carried out yourself, with your own evidence written down.

## How to complete projects safely in a dedicated practice directory

1. Read the guide's **Purpose**, **Learning outcomes**, and **Prerequisites and safety rules**
   sections before running anything — each guide names the exact, dedicated practice directory to
   work in.
2. **Never** run this folder's exercises in Downloads, Documents, or an existing project folder —
   always create and confirm a fresh practice directory first, exactly as
   [`11-safe-terminal-and-filesystem-literacy.md`](../11-safe-terminal-and-filesystem-literacy.md)
   teaches.
3. Follow the **step-by-step instructions** in order, using the guide's investigation workflow
   (goal → assumptions → smallest experiment → observe → explain → change one variable → verify →
   document) at every step, not only when something breaks.
4. Use only **synthetic, non-sensitive data** — every project in this folder creates its own sample
   log files from scratch; never point these exercises at a real production log or a file
   containing real secrets.
5. Reread the relevant numbered concept file in this module if a step doesn't make sense — these
   guides assume the concepts; they don't re-teach them from scratch.
6. Use the guide's **completion gate** at the end to confirm you are actually done, not just tired
   of the exercise.

## Expected documentation, evidence, and Git habits

- Keep your working notes and real command output in a plain-text or Markdown file, exactly as each
  guide's deliverables section describes — a description of what you *think* a command would show
  is not evidence; the actual output you observed is.
- Write findings in your own words. An explanation you cannot defend out loud does not count as
  evidence of understanding.
- If you are keeping this work in a Git repository (for example, the `engineering-foundations`
  repository from the Stage 0 roadmap's Gap 0A), commit your notes with a small, descriptive
  message such as `docs: add shell file and stream investigation notes` — one meaningful change per
  commit, and never commit real secrets or API keys.
- Treat every unexpected result as evidence, not a failure: record what you expected, what actually
  happened, and what you checked next. This is Stage 0 Gap 0F — Engineering thinking from day
  one — the same habit used later to debug real backend and AI services.

## Projects in this module

| Project | Focus |
|---|---|
| [`01-shell-file-and-stream-investigation.md`](./01-shell-file-and-stream-investigation.md) | Investigating a synthetic log directory with `grep`, `sort`, `uniq -c`, pipes, and redirection |

For the full set of Stage 0 projects (Projects 0.1–0.5, which build a version-controlled,
cross-module portfolio), see
[`../../00-Stage-0-Overview/learning-plan.md`](../../00-Stage-0-Overview/learning-plan.md), Section
5 — "Practical projects."
