# Module 1.1 — Computational Thinking and Program Design

This is the first module of Stage 1 in the Programming & Computational Thinking
part of the curriculum. It assumes you have finished Stage 0 (computer
basics, the command line, and a working developer environment), but it
assumes **no prior programming knowledge at all**. Every idea is explained
from zero.

## Module outcome

By the end of this module, you will be able to take a problem written in
plain English — for example, "work out how much a group of friends spent on
a trip" — and turn it into:

- clear **inputs** (what information goes in),
- a clear **output** (what answer or result comes out),
- explicit **rules** (how the inputs turn into the output),
- any **state** that needs to be remembered while the program runs, and
- a small set of **functions**, each with one clear job.

This skill — turning a fuzzy real-world problem into a precise, testable
plan — is the single most important skill in this entire curriculum. Every
later stage (Python details, testing, backend engineering, and eventually
Applied AI and agent systems) assumes you can already think this way.

## Topics in this module, in recommended learning order

Work through these files in order. Each one builds on the ideas from the
one before it.

1. [Algorithms, Programs, and Data](01-algorithms-programs-and-data.md)
2. [Values, Expressions, Statements, and Variables](02-values-expressions-statements-and-variables.md)
3. [Input → Process → Output](03-input-process-output.md)
4. [Sequence, Selection, Iteration, and Abstraction](04-sequence-selection-iteration-and-abstraction.md)
5. [Problem Decomposition](05-problem-decomposition.md)
6. [Preconditions, Postconditions, and Edge Cases](06-preconditions-postconditions-and-edge-cases.md)
7. [Pseudocode, Flowcharts, and Dry Runs](07-pseudocode-flowcharts-and-dry-runs.md)
8. [State and State Modelling](08-state-and-state-modelling.md)

Do not skip ahead. Topic 4 (loops and functions) will not make sense unless
you already understand topic 2 (variables), and topic 8 (state) leans on
almost everything before it.

## How to work through every topic (the engineering loop)

For every idea and every example in this module, follow the same nine-step
loop. This is not busywork — it is the habit that separates someone who
"copies code that works" from someone who can be trusted to write software.

```text
Understand → Predict → Implement → Test normal case → Test edge cases
→ Debug → Refactor → Document → Explain aloud
```

In plain words:

1. **Understand** — Read the example or exercise until you could describe
   the problem to someone else without looking at it.
2. **Predict** — Before running any code, guess what it will print or do.
3. **Implement** — Type the code yourself. Do not copy and paste.
4. **Test normal case** — Run it with an ordinary, expected input.
5. **Test edge cases** — Run it with empty input, unusual input, or extreme
   values (see [topic 6](06-preconditions-postconditions-and-edge-cases.md)).
6. **Debug** — When it breaks (it will), read the error message carefully
   and fix the real cause, not just the symptom.
7. **Refactor** — Once it works, tidy the code: better names, less
   repetition, clearer structure.
8. **Document** — Write one or two sentences (in a comment or a note) about
   what the code does and why.
9. **Explain aloud** — Say out loud, in your own words, how the code works,
   line by line. If you cannot, you do not understand it yet.

## Practice and Planning

Once you have read all eight topic files, move on to
[`practice-questions.md`](practice-questions.md) in this folder. It
contains six practice problems that reuse the ideas from this module
(expenses, passwords, traffic lights, counting, and simple text
processing).

For every practice question, solve it **first in plain English and
pseudocode, then in Python** — never the other way around. Concretely:

1. Read the question and restate it in your own words.
2. Write down its inputs, outputs, assumptions, and edge cases.
3. Write pseudocode for the steps, and dry-run that pseudocode by hand.
4. Only after that, open a Python file and implement it.

Use [`problem-solving-template.md`](problem-solving-template.md) as a
fill-in-the-blank template for this process — it has one section for each
step above (inputs, outputs, assumptions, rules, examples, edge cases,
state to track, pseudocode, dry run, test cases, implementation plan,
debugging notes, and a final explanation), plus a short worked example
showing the template filled in.

Longer, multi-step projects for this stage live in the
[Stage 1 Projects](../00-Stage-1-Overview/Projects/README.md) folder.

## Prerequisites

- Stage 0 completed: comfortable using a computer, a terminal, and a text
  editor or IDE.
- No prior programming experience is required for this module.

## A note on scope

This module deliberately stays at the level of plain Python and basic
programming ideas. It does not use external libraries, the internet,
databases, or anything related to machine learning or AI models. Those
topics come much later, once the fundamentals in this module are solid.

## Looking ahead

Later in this curriculum, in Applied AI and Agentic AI engineering work,
you will design AI "agents" that take a user's request, decide on a
sequence of steps, keep track of state (what has already happened), and
call tools in the right order with the right inputs. That is the exact same
skill you are building here — decomposing a plain-English problem into
inputs, outputs, rules, state, and small steps — just with an AI model
added on top later. The thinking habits in this module are the foundation;
nothing about them changes when AI is introduced.
