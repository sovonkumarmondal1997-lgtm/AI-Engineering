# Module 0.1 Projects — How Computers Work

**Status:** Not Started
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Module 0.1 — "How
Computers Work," audit evidence for Section 2

## Why these projects exist

Reading the 20 numbered concept files in this module (`01-motherboard-and-buses.md` through
`20-why-gpus-matter-for-ai.md`) tells you what a computer does. It does not, by itself, prove you
can *explain* it in your own words or connect it to something you actually ran. The Stage 0
roadmap draws an important line: **"completed" means you studied or practiced the module. It does
not automatically mean the skill is operational.**

These projects exist to close that gap. Each one takes concepts you have already read about and
asks you to observe them happening on your own machine, explain what you saw in plain language, and
write it down — producing a real artifact instead of a memory of having read something once.

## Observable evidence of Stage 0 understanding

The Stage 0 roadmap's audit table names a specific piece of evidence for this module:

> In your own words, explain what happens from launching a Python command to seeing output, and
> why a GPU helps with parallel tensor operations.

[`01-program-execution-and-gpu-audit.md`](./01-program-execution-and-gpu-audit.md) is that
evidence. Completing it and keeping your written notes is how you (or anyone reviewing your
progress) can confirm this module is operational — not just read.

## How to use these project guides

1. Read the guide's **Purpose**, **Learning outcomes**, and **Prerequisites** sections first, so
   you know what you're proving and what you need before starting.
2. Follow the **step-by-step instructions** in order. Do not skip steps even if a result seems
   obvious — the point is to *observe* it happening, not to assume it.
3. Use the **industry-standard workflow** described in each guide (goal → assumptions → smallest
   experiment → observe → explain → verify → document) for every step, not just when something goes
   wrong.
4. Stop and reread the relevant numbered concept file in this module if a step doesn't make sense —
   these projects assume the concepts, they don't re-teach them from scratch.
5. Use the guide's **completion gate** at the end to confirm you are actually done, not just tired
   of the exercise.

## Expected documentation and Git habits

- Keep your working notes and command output in a plain-text or Markdown file, exactly as each
  project guide's deliverables section describes.
- Write findings in your own words. Copy-pasted explanations you cannot defend out loud do not
  count as evidence.
- If you are keeping this work in a Git repository (for example, the `engineering-foundations`
  repository from the Stage 0 roadmap's Gap 0A), commit your notes with a small, descriptive
  message such as `docs: add program execution and GPU audit notes` — one meaningful change per
  commit, and never commit real secrets or API keys.
- Treat every unexpected result as evidence, not a failure: write down what you expected, what
  actually happened, and what you checked next. This habit is Gap 0F — Engineering thinking from
  day one — from the Stage 0 roadmap, and it is the same habit used later for debugging real AI
  systems.

## Projects in this module

| Project | Focus |
|---|---|
| [`01-program-execution-and-gpu-audit.md`](./01-program-execution-and-gpu-audit.md) | Program execution audit (Python command → output) and a high-level explanation of GPU parallelism for tensor operations |

For the full set of Stage 0 projects (Projects 0.1–0.5, which build a version-controlled,
cross-module portfolio), see
[`../../00-Stage-0-Overview/learning-plan.md`](../../00-Stage-0-Overview/learning-plan.md), Section
5 — "Practical projects."
