# Module 0.2 Projects — Operating System Fundamentals

**Status:** Not Started
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Module 0.2 — "Operating
System Fundamentals," audit evidence for Section 2, and Project 0.3

## Why these projects exist

Reading this module's numbered concept files — including
[`16-local-networking-for-development.md`](../16-local-networking-for-development.md) — tells you
how processes, signals, and local services work. It does not, by itself, prove you can find a real
process on your own machine, read its resource use, discover the port it's listening on, and stop
it safely. The Stage 0 roadmap is explicit about this: **"completed" means you studied or practiced
the module. It does not automatically mean the skill is operational.**

These projects exist to close that gap — turning concepts you've read into evidence you produced
yourself, on your own machine, in writing.

## How to use these project guides safely

1. Read the guide's **Purpose**, **Learning outcomes**, and especially its **Prerequisites and
   safety rules** section before running anything — it names the exact, dedicated practice
   directory to work in and the process-safety rules that apply throughout.
2. Follow the **step-by-step instructions** in order, using the guide's troubleshooting workflow
   (goal → assumptions → smallest experiment → observe → hypothesis → change one variable → verify
   → document) at every step, not only when something breaks.
3. **Never act on a process ID (PID) you have not personally confirmed** belongs to the test process
   you started yourself. Every guide in this folder is written so you always create the process,
   capture its PID at creation, and re-confirm that PID before doing anything to it.
4. Reread the relevant numbered concept file in this module (or
   [`16-local-networking-for-development.md`](../16-local-networking-for-development.md)) if a step
   doesn't make sense — these guides assume the concepts; they don't re-teach them from scratch.
5. Use the guide's **completion gate** at the end to confirm you are actually done, not just tired
   of the exercise.

## Expected documentation, evidence, and Git habits

- Keep your working notes and real command output in a plain-text or Markdown file, exactly as each
  guide's deliverables section describes — a report describing what you *think* would happen is not
  evidence; the actual output you observed is.
- Write findings in your own words. An explanation you cannot defend out loud does not count as
  evidence of understanding.
- If you are keeping this work in a Git repository (for example, the `engineering-foundations`
  repository from the Stage 0 roadmap's Gap 0A), commit your notes with a small, descriptive
  message such as `docs: add process, resource, and port diagnosis notes` — one meaningful change
  per commit, and never commit real secrets or API keys.
- Treat every unexpected result as evidence, not a failure: record what you expected, what actually
  happened, and what you checked next. This is Stage 0 Gap 0F — Engineering thinking from day
  one — the same habit used later to debug real backend and AI services.

## Projects in this module

| Project | Focus |
|---|---|
| [`01-process-resource-and-port-diagnosis.md`](./01-process-resource-and-port-diagnosis.md) | Safely finding, observing, and stopping a local test process; discovering and verifying a listening port |

For the full set of Stage 0 projects (Projects 0.1–0.5, which build a version-controlled,
cross-module portfolio), see
[`../../00-Stage-0-Overview/learning-plan.md`](../../00-Stage-0-Overview/learning-plan.md), Section
5 — "Practical projects."
