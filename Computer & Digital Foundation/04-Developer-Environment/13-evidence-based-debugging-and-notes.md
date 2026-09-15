# Evidence-Based Debugging and Notes

**Module:** Developer Environment
**Roadmap reference:** Stage 0 — Computer, Linux, and Developer Foundations, Gap 0F —
"Engineering thinking from day one" (extends Module 0.4 — Developer Environment)
**Concept(s) covered:** the goal-assumptions-experiment debugging loop, reading error messages and
tracebacks, isolating one variable, minimal reproducible examples, `learning-notes.md`
**Prerequisites:** `05-debugger.md`, `11-reproducible-python-workspaces-with-uv.md`
**Status:** Not Started

---

## Learning Outcomes

By the end of this lesson you will be able to:

- Apply the core engineering loop — goal, assumptions, smallest experiment, observe, explain,
  change one variable, verify, document — to any small technical problem.
- Explain why evidence is more reliable than guessing or repeatedly rerunning a command hoping for
  a different result.
- Read an error message, a log line, an exit code, and a traceback for the specific facts they
  contain.
- Isolate one variable at a time and build a minimal reproducible example of a problem.
- Maintain a `learning-notes.md` file with a consistent, useful structure.
- Work through a full, safe beginner incident end to end using this method.
- Explain how this habit becomes production debugging, incident response, evaluation, and
  AI-system architecture thinking later in the roadmap.

## Prerequisites

- **`05-debugger.md`** — using a debugger to inspect a program's actual state, one tool this
  lesson's "observe" step can draw on.
- **`11-reproducible-python-workspaces-with-uv.md`** — reading a traceback from bottom to top, used
  directly in Section 4 here.

## Key Terms

- **Evidence** — a directly observed fact (an exact error message, a command's real output, a log
  line) as opposed to a memory, an assumption, or a guess.
- **Exit code** — a number a process reports when it finishes, `0` meaning success and any non-zero
  value meaning some kind of failure (Module 0.2,
  [Process Lifecycle](../02-Operating-System-Fundamentals/14-process-lifecycle.md)).
- **Minimal reproducible example** — the smallest possible version of a problem that still shows
  the failure, with everything unrelated removed.
- **Isolating a variable** — changing exactly one thing between two attempts, so any difference in
  outcome can be attributed to that one change with confidence.
- **Root cause** — the actual, underlying reason a failure happened, as distinct from its symptom.

---

## 1. Why Debugging Is a Discipline, Not a Talent

Some people look like they're naturally good at debugging. What's actually happening is almost
always a consistent method, applied automatically: look at real evidence, change one thing at a
time, and confirm before moving on. This lesson makes that method explicit, so you can apply it
deliberately from your very first bug — not something you're hoping to develop "eventually" through
experience alone.

## 2. The Core Engineering Loop

```text
Goal → assumptions → smallest experiment → observe output/logs
→ explain failure → change one variable → verify → document
```

- **Goal** — state, in one sentence, what you're trying to find out or achieve.
- **Assumptions** — state what you expect to happen, *before* you run anything. Writing this down
  is what lets you notice, later, that something surprised you.
- **Smallest experiment** — run the smallest possible command or test that can inform your
  question — not the whole program, not a large script, the smallest piece that isolates the
  question.
- **Observe output/logs** — read the *actual* result. Don't skim it; don't assume you know what it
  says.
- **Explain failure** — if it didn't match your assumption, write down *why*, based only on what
  you actually observed.
- **Change one variable** — adjust exactly one thing and re-run, so you can attribute any
  difference to that one change (Section 6).
- **Verify** — confirm your fix or explanation actually holds, don't just assume it worked because
  the error stopped appearing once.
- **Document** — write it down (Section 8), before moving on to the next thing.

This loop applies equally to "why won't this script run" and, much later, "why did this model
server's response quality drop."

## 3. Why Evidence Beats Guessing and Rerunning

Two behaviors feel productive but usually aren't:

- **Guessing** — trying a fix because it "feels like" it should work, without evidence it addresses
  the actual cause. Sometimes it accidentally works; you then don't actually know why, and the same
  problem often resurfaces differently later.
- **Repeatedly rerunning** — running the same failing command again, hoping for a different result,
  without changing anything. If nothing changed, nothing new can be learned from running it again.

**The alternative this lesson teaches:** every step produces a specific, written piece of evidence
(exact command, exact output) that either supports or rules out a specific explanation — turning
"I'm not sure why this works now" into "I know exactly why this works, and could explain it to
someone else."

## 4. Reading Error Messages and Tracebacks

An error message's *exact wording* is evidence — read it in full, don't paraphrase it from memory.

```text
FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'
```

This single line already tells you: the error *type* (`FileNotFoundError`), and the *exact* missing
path (`config.yaml`) — enough to check, immediately, whether you're in the directory you think you
are (Module 0.3, Lesson 11) before guessing at anything more complicated.

For a full **traceback**, `11-reproducible-python-workspaces-with-uv.md`, Section 11 already taught
the core method: **read from the bottom up** — the last line names the error, the line just above it
is the exact failing line, and the lines above that show the chain of calls that led there.

## 5. Reading Logs, Exit Codes, Environment Details, and Process Information

Beyond a single error message, a full investigation often needs:

- **Logs** — read with `head`/`tail`/`less`/`grep` (Module 0.3) — look for the specific line at or
  just before the moment things went wrong, not the whole file at once.
- **Exit codes** — check with `echo $?` immediately after a command in Bash (or `$LASTEXITCODE` in
  PowerShell); `0` means success, anything else means failure, and the specific non-zero value is
  sometimes itself meaningful evidence.
- **Environment details** — which interpreter (`which python3`), which directory (`pwd`), which
  environment variables are actually set (Module 0.2,
  [Environment Variables](../02-Operating-System-Fundamentals/09-environment-variables.md)) — often
  the actual root cause hides here, not in the code itself.
- **Process information** — `ps`, `top`/`htop` (Module 0.2,
  [Processes](../02-Operating-System-Fundamentals/03-processes.md)) — is the process you expect
  actually running, and is it the one actually connected to the problem?

## 6. Isolating One Variable at a Time

If you change two things at once and the problem goes away, you don't actually know which change
fixed it — or whether both were needed. **Isolating a variable** means changing exactly one thing
between attempts:

```text
Attempt 1: original command, in the wrong directory       → fails
Attempt 2: same command, correct directory, nothing else changed → succeeds
```

This single, controlled comparison tells you, with real confidence, that the directory was the
cause — not a guess, a demonstrated fact.

## 7. Building a Minimal Reproducible Example

A **minimal reproducible example** is the smallest version of a problem that still shows the
failure — with every unrelated piece removed. If a 200-line script fails, don't debug all 200
lines at once: strip it down to the fewest lines that still reproduce the exact error. This matters
for two reasons: it's dramatically faster to reason about a 5-line failure than a 200-line one, and
it forces you to understand *which part* actually matters, rather than debugging the whole thing by
vague impression.

## 8. Maintaining `learning-notes.md`

For every real issue you hit, record:

```markdown
## Issue: <one-line summary>

- **Expected result:** what you thought would happen
- **Actual result:** what actually happened (exact error/output)
- **Command/evidence checked:** the exact commands you ran to investigate
- **Root cause:** the actual, confirmed reason — not a guess
- **Fix:** what you changed
- **Prevention:** what you'll do differently to avoid this next time
- **Next test:** what you'd check next if this happens again, or in a related situation
```

**Why write this down, even for something small:** a note converts a one-time frustration into
reusable knowledge — for yourself, three weeks from now when something similar happens, and
eventually for a team that benefits from a shared record instead of everyone rediscovering the same
issues independently.

## 9. Worked Example: A Safe Beginner Incident

**Scenario:** running a script fails with `ModuleNotFoundError`, and you're not sure why.

Applying the loop from Section 2:

```text
Goal:          Find out why `uv run python app.py` reports ModuleNotFoundError.
Assumptions:   I expect the script to run, since I added the package to pyproject.toml earlier.
```

```bash
uv run python app.py
```

```text
ModuleNotFoundError: No module named 'requests'
```

```text
Observe:       The exact error names the missing module: 'requests'.
Explain:       I added "requests" to pyproject.toml, but do I remember running `uv sync`
               afterward? I'm not certain — this is a real, checkable question, not a guess.
```

```bash
cat pyproject.toml | grep requests
uv sync
uv run python app.py
```

```text
Change one variable:  Ran `uv sync` — nothing else about the script or environment changed.
Verify:               The script now runs without the error.
```

```markdown
## Issue: ModuleNotFoundError for 'requests' despite it being declared

- **Expected result:** script runs normally
- **Actual result:** `ModuleNotFoundError: No module named 'requests'`
- **Command/evidence checked:** confirmed `requests` was in `pyproject.toml`; ran `uv sync`
- **Root cause:** dependency was declared but never synced into the environment
- **Fix:** ran `uv sync`
- **Prevention:** always run `uv sync` immediately after editing `pyproject.toml`, not "later"
- **Next test:** if this recurs, check `uv.lock`'s timestamp against `pyproject.toml`'s last edit
```

This same shape — goal, evidence, one change, verify, document — applies identically to a wrong
directory, a missing `.env` value, or an occupied local port (Module 0.2's
[Local Networking](../02-Operating-System-Fundamentals/16-local-networking-for-development.md)
lesson covers that last scenario in full).

## 10. Common Mistakes and Safe Troubleshooting

| Mistake | Why it slows you down | Better approach |
|---|---|---|
| Rerunning the exact same failing command repeatedly | Nothing changed, so nothing new can be learned | Change exactly one thing (Section 6) before rerunning. |
| Changing several things at once "to be safe" | You can no longer tell which change actually mattered | Isolate one variable at a time (Section 6). |
| Skimming an error message instead of reading it fully | You miss the exact, specific fact it's telling you | Read the full message, and for a traceback, start from the last line (Section 4). |
| Debugging inside a large, complex script | Too many moving parts to reason about clearly | Build a minimal reproducible example first (Section 7). |
| Fixing something without confirming *why* it was broken | The same problem often resurfaces differently later | Confirm a root cause with actual evidence before considering it fixed (Section 3, Section 9). |

## 11. From Here to Production: Incident Response, Evaluation, and AI-System Architecture Thinking

This exact loop scales up directly, without changing shape:

- **Production debugging** — a hung backend process or a failing deployment is diagnosed with the
  same goal → evidence → one-variable-at-a-time method, just with more sophisticated tools around
  it.
- **Incident response** — Section 8's `learning-notes.md` format is a small-scale version of a
  professional incident postmortem: expected vs. actual, evidence, root cause, fix, prevention.
- **Evaluation** — diagnosing why a model's evaluation score dropped uses the identical
  method: form a hypothesis about *one* changed variable (a prompt, a dataset version, a model
  version), test it in isolation, and verify with evidence before concluding anything.
- **AI-system architecture thinking** — reasoning about why a multi-component AI system (retrieval,
  a model call, a tool call) produced a wrong result requires isolating *which* component actually
  failed — exactly Section 6 and Section 7's skills, applied to a more complex system.

The tools change constantly throughout a career; this method — goal, evidence, one variable, verify,
document — does not.

---

## Exercises

1. Pick any small, real annoyance you've hit while working through this module (or deliberately
   cause a simple one — a typo'd command, a wrong directory) and work through the full loop from
   Section 2, writing each step down as you go, before you fix anything.
2. Take a traceback from any exercise in `11-reproducible-python-workspaces-with-uv.md` and
   practice reading it from the bottom up, out loud, in your own words.
3. Deliberately introduce two changes at once to something (for example, both a code change and an
   environment change) so it "works," then go back and isolate which one actually mattered.
4. Write a `learning-notes.md` entry, using Section 8's exact structure, for the exercise you did
   in Step 1.
5. In one paragraph, explain how you would apply this same loop to a *hypothetical* production
   incident: an AI service's response times suddenly doubled.

## Expected Results

- **Exercise 1:** your written notes show a clear, one-sentence goal and assumption written
  *before* your first command — not reconstructed afterward.
- **Exercise 2:** your explanation correctly identifies the error type from the last line before
  addressing anything else.
- **Exercise 3:** you can state, with a specific test, which of the two changes was actually
  necessary — not just "probably both."
- **Exercise 4:** your entry includes all seven fields from Section 8, each filled with a real,
  specific fact — not a vague restatement.
- **Exercise 5:** your paragraph should mention isolating one variable (which recent change
  correlates with the slowdown) and checking evidence (logs, metrics) before proposing a fix.

---

## Summary

Debugging well is a repeatable method, not a talent: state your goal and assumption, run the
smallest experiment that can inform it, read the real output carefully, explain any surprise using
only that evidence, change exactly one variable at a time, verify your fix actually holds, and
write it down. Evidence — an exact error message, a real command's output, a traceback read from
the bottom up — is always stronger than a guess or a hopeful rerun. Isolating one variable and
building a minimal reproducible example turn a confusing, large problem into a small, confident
answer. A `learning-notes.md` entry with expected result, actual result, evidence, root cause, fix,
prevention, and next test turns a one-time frustration into reusable knowledge. This exact loop is
also, unchanged in shape, what production debugging, incident response, evaluation, and AI-system
architecture reasoning look like later in the roadmap.

## Completion Checklist

- [ ] I can state the eight steps of the core engineering loop from memory.
- [ ] I can explain, with an example, why evidence beats guessing and repeated reruns.
- [ ] I read a real traceback from the bottom up and correctly identified the error and its exact
      line before reading further.
- [ ] I isolated one variable in a real (or deliberately created) problem and confirmed, with
      evidence, which change actually mattered.
- [ ] I built or recognized a minimal reproducible example, stripping away everything unrelated to
      the failure.
- [ ] I wrote a complete `learning-notes.md` entry using Section 8's structure, for a real issue I
      hit.
- [ ] I worked through Section 9's full worked example (or an equivalent one of my own) start to
      finish.
- [ ] I can explain, in my own words, how this method scales up to production debugging, incident
      response, and evaluation.
- [ ] I completed the exercises above and my results match the expected results.

---

_This lesson is complete. It covers evidence-based debugging and note-keeping from Stage 0 Gap 0F,
the final gap extension to Module 0.4. It intentionally does not teach formal incident-management
frameworks, statistical root-cause analysis, or production observability tooling — those remain
later, more advanced topics built directly on the habit this lesson establishes._
