# Module 0.1 Exercises

**Status:** Not Started

This is an exercise **plan and question index**, not the exercises themselves with answers.
Questions are specified now so the structure exists; actual worked exercises (with expected
answers/solutions) are written during the teaching phase, one concept file at a time.

Exercises progress through 5 levels of increasing depth. Every concept in this module is touched
by at least one exercise at Level 1 and Level 2; not every concept needs a Level 4/5 exercise
individually — some are integrated together at those levels, per the Integration column below.

## Level 1 — Recognition

**Objective:** Recognize and correctly name a concept when shown an example of it, without yet
explaining how it works.

Planned questions cover, per concept file (1–20):
- Given a real-world example or image/description, identify which hardware/software concept it
  illustrates (e.g. "a laptop's main circuit board" → motherboard).
- Given a number written in an unfamiliar format, identify which base it's most likely in
  (binary / decimal / hex) based on its characters.
- Match a term (e.g. "cache", "RAM", "SSD") to its one-line role in the memory/storage hierarchy.

## Level 2 — Understanding

**Objective:** Explain, in the learner's own words, what a concept is and why it exists.

Planned questions cover, per concept file (1–20):
- "What is [concept] and why does a computer need it?" — one short-answer prompt per concept.
- "What would happen if [concept] didn't exist / was removed?" — reinforces *why* it exists, not
  just what it is.
- Compare two related concepts and state the difference in one or two sentences (e.g. cache vs
  RAM; HDD vs SSD; compilation vs interpretation; process vs program).

## Level 3 — Application

**Objective:** Use a concept to solve a small, concrete problem — not just describe it.

Planned exercises:
- Convert a given set of numbers by hand between binary, decimal, and hex (paired with Project
  0.1.1, but doable before the tool is built).
- Convert a given set of memory/storage sizes by hand between units (paired with Project 0.1.2).
- Given a described machine (CPU model, core count, RAM, storage type), answer practical
  questions about it (e.g. "would this machine handle N parallel CPU-bound tasks well?").
- Given a short snippet of pseudocode, identify which parts are "compiled/prepared" vs
  "interpreted/run", once compilation/interpretation (file 8) has been read.

## Level 4 — Debugging

**Objective:** Given a wrong answer, a misconception, or unexpected observed behavior, diagnose
what went wrong and why.

Planned exercises:
- Given an incorrect binary→decimal (or other base) conversion, find and explain the error.
- Given a described scenario where a program runs slower than expected, decide whether the likely
  cause is CPU-bound, memory-bound, or storage-bound, and justify the reasoning.
- Given Lab 3's CPU observation results showing usage NOT scaling linearly with added load tasks,
  explain the discrepancy.
- Given a common misconception (e.g. "more RAM always makes a CPU-bound task faster"), explain
  why it's wrong using concepts from this module.

## Level 5 — Integration

**Objective:** Combine multiple concepts from across the module into one coherent explanation —
the same skill required by the Stage 0 completion gate.

Planned exercises:
- Narrate, end to end and in the correct order, what happens from double-clicking a program icon
  to that program running as a process (integrates files 1–3, 6–8, 14–17).
- Narrate, end to end, what happens when a running program calls a function, including where
  arguments and return values physically go (integrates files 6, 8, 17, 18).
- Explain why a GPU is used for AI workloads instead of a CPU, using the CPU/core/memory model
  built earlier in the module (integrates files 2, 3, 9–13, 20).
- Explain, using a concrete example, why RAM and storage cannot substitute for each other in a
  running AI application (integrates files 9–12, 19).

## Coverage map

| Concept file(s) | Exercised at levels |
|---|---|
| 1–3 (Motherboard/Buses, CPU, Cores) | 1, 2, 3, 5 |
| 4–5 (Binary/Bits/Bytes, Hexadecimal) | 1, 2, 3, 4 |
| 6–8 (Registers, Instructions/Machine Code, Compilation/Interpretation) | 1, 2, 3, 5 |
| 9–10 (Cache, RAM) | 1, 2, 4, 5 |
| 11–12 (Storage, HDD vs SSD) | 1, 2, 3, 5 |
| 13 (GPU) | 1, 2, 5 |
| 14–16 (Files, Input/Output, Processes) | 1, 2, 5 |
| 17–18 (Program starts, Function executes) | 2, 5 |
| 19–20 (Why RAM/storage differ, Why GPUs matter for AI) | 2, 4, 5 |

## Notes

- No answers, model solutions, or worked examples exist yet in this folder.
- Exercises are written to match each concept file's eventual "12. Hands-on exercise" and
  "14. Review questions" sections once lesson content is produced — this index exists so the
  overall shape is planned in advance.
