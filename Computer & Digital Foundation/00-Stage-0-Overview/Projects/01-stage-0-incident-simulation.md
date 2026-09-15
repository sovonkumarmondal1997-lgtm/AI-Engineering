# Project 0.5 — Stage 0 Incident Simulation

**Estimated time:** 45–75 minutes

**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Section 5 — "Practical
projects," Project 0.5 — "Stage 0 Incident Simulation."

---

## 1. Project title and estimated time

**Stage 0 Incident Simulation** — estimated 45–75 minutes.

## 2. Purpose and real-world AI-engineering relevance

This is the **Stage 0 capstone project**. Its scenario is simple to describe and deliberately
realistic: something you control breaks, and you must find out exactly why — using evidence, not
assumptions — fix it with the smallest possible change, verify the fix actually worked, and write a
short, honest postmortem explaining what happened.

This is not a synthetic academic exercise. Every AI team, at every level of seniority, handles real
incidents this same way: state what should happen, gather evidence about what actually happened,
form and test a hypothesis, apply the smallest fix, verify it, and write it down so the same
mistake doesn't recur. A hung model server, a failing deployment, or a broken evaluation pipeline
all get diagnosed with exactly this method — Stage 0 teaches it now, on something small and safe, so
it's already a habit by the time it matters on something that isn't.

## 3. Learning outcomes

By the end of this project, you will be able to:

- Apply the full investigation workflow — goal, assumptions, smallest reproducible experiment,
  observe, hypothesis, one-variable test, smallest fix, verify, document — to a real, self-created
  incident.
- Deliberately reproduce a chosen, safe failure and capture its exact evidence.
- Investigate a problem one fact at a time using only safe, read-only or reversible commands.
- Apply the smallest possible fix and prove, with evidence, that it worked.
- Write a complete, evidence-based postmortem using an industry-standard structure.
- Explain why this exact discipline is what production incident response, debugging, and AI-system
  reliability work are built on.

## 4. Prerequisites and safety rules

**Concepts and projects you should have already completed:**

- [`../../03-Command-Line/11-safe-terminal-and-filesystem-literacy.md`](../../03-Command-Line/11-safe-terminal-and-filesystem-literacy.md) —
  safe practice-directory habits, permissions.
- [`../../02-Operating-System-Fundamentals/16-local-networking-for-development.md`](../../02-Operating-System-Fundamentals/16-local-networking-for-development.md)
  and [`Project 0.3`](../../02-Operating-System-Fundamentals/Projects/01-process-resource-and-port-diagnosis.md) —
  if you choose the occupied-port scenario.
- [`../../04-Developer-Environment/11-reproducible-python-workspaces-with-uv.md`](../../04-Developer-Environment/11-reproducible-python-workspaces-with-uv.md) —
  if you choose the missing-package scenario.
- [`../../04-Developer-Environment/12-secrets-and-local-security-hygiene.md`](../../04-Developer-Environment/12-secrets-and-local-security-hygiene.md) —
  if you choose the missing-`.env`-value scenario.
- [`../../04-Developer-Environment/13-evidence-based-debugging-and-notes.md`](../../04-Developer-Environment/13-evidence-based-debugging-and-notes.md) —
  the investigation loop this entire project applies.

You do not need to have memorized these — you need to be willing to reread the relevant one for
whichever scenario you choose in Section 7.

**Tools required** (all free, already covered in Stage 0): a terminal (Bash/WSL2 or PowerShell),
Python 3, `uv`, and Git.

**Not required:** Docker, any cloud account, GPUs, or advanced programming.

> ### ⚠️ Safety rules — read before Section 7
>
> 1. **Work only in a dedicated, separate practice directory or repository** — never inside this
>    `AI Engineering` curriculum folder.
> 2. **Never stop, kill, or otherwise act on any process you did not personally start for this
>    exercise, and whose PID you have not personally confirmed.** If your chosen scenario involves a
>    process or port, it must be one you created yourself, moments earlier, for this project alone.
> 3. **Never alter system-level permissions, ownership, or configuration.** Every permissions
>    scenario in this project happens entirely inside your own practice directory, on files you
>    created — never on a system file, another user's file, or anything requiring elevated
>    privileges.
> 4. **Never use a real secret, API key, password, token, or private key anywhere in this
>    project.** Every `.env` value involved is a placeholder — this project never needs a real
>    credential at any point.
> 5. **Save no sensitive log content.** If any command's output could plausibly contain something
>    sensitive (it shouldn't, in any of Section 7's scenarios), stop and reconsider before saving
>    it as evidence.

## 5. Deliverables

By the end, your practice directory should contain:

- [ ] `postmortem-stage-0.md` — your complete, evidence-based postmortem (Section 9's template).
- [ ] Saved error evidence — the exact error text or output you captured, with no secrets or
      sensitive information in it.
- [ ] Documented verification that the issue is fixed — the exact command and output proving the
      original operation now succeeds.

## 6. Industry-standard investigation workflow

Use this loop, in order, for your chosen incident:

```text
Goal → assumptions → smallest reproducible experiment → observe output/logs
→ form hypothesis → test one variable → apply smallest fix → verify → document prevention
```

- **Goal** — one sentence: what are you trying to restore or confirm?
- **Assumptions** — one sentence: what do you expect to happen, stated *before* you break anything.
- **Smallest reproducible experiment** — the smallest command that reliably reproduces the problem.
- **Observe output/logs** — read the *exact* output; don't paraphrase it from memory.
- **Form hypothesis** — your best, evidence-based explanation for the cause.
- **Test one variable** — change exactly one thing to test that hypothesis.
- **Apply smallest fix** — the minimal change that resolves the actual cause, not a broad
  workaround.
- **Verify** — confirm, with a real command and real output, that the original operation now
  succeeds.
- **Document prevention** — write down what you'd do differently to avoid this recurring.

## 7. Safe incident-scenario selection

Choose **exactly one** of these five scenarios. Each is safe, reversible, and entirely within your
own practice directory — pick whichever connects best to the module you found most interesting.

1. **Wrong directory.** A command fails because you are not in the directory you assume you're in.
2. **Missing or unsynced Python environment.** A Python package is unavailable because the project
   environment was never created or never synced (builds on
   [`11-reproducible-python-workspaces-with-uv.md`](../../04-Developer-Environment/11-reproducible-python-workspaces-with-uv.md)).
3. **Occupied local port.** A local port is already held by your own harmless test process, started
   moments earlier for this exercise (builds on
   [`16-local-networking-for-development.md`](../../02-Operating-System-Fundamentals/16-local-networking-for-development.md)
   and its
   [project](../../02-Operating-System-Fundamentals/Projects/01-process-resource-and-port-diagnosis.md)).
4. **Permissions failure.** A file cannot be written because of its permissions, inside your own
   dedicated practice directory only (builds on
   [`11-safe-terminal-and-filesystem-literacy.md`](../../03-Command-Line/11-safe-terminal-and-filesystem-literacy.md)).
5. **Missing placeholder `.env` value.** A script fails because a required environment variable
   isn't set in `.env` — using only a placeholder variable, never a real secret (builds on
   [`12-secrets-and-local-security-hygiene.md`](../../04-Developer-Environment/12-secrets-and-local-security-hygiene.md)).

Write your chosen scenario's number and name at the top of `postmortem-stage-0.md` before
continuing.

## 8. Step-by-step instructions

### 8.1 State the expected behavior before introducing the problem

Before breaking anything, run the operation you're about to disrupt, once, successfully, and write
down exactly what "working" looks like. For example, for Scenario 2: `uv run python
hello_environment.py` prints the interpreter path and working directory without error.

### 8.2 Reproduce the selected problem deliberately, and save the exact error

Introduce your chosen problem on purpose. Examples, one per scenario:

- **Scenario 1:** `cd` to a different, unrelated directory, then run the same command you ran in
  8.1 using a relative path that only works from the original location.
- **Scenario 2:** delete or rename your project's `.venv`, or skip `uv sync` in a fresh clone, then
  run the program.
- **Scenario 3:** start a harmless test process on a port (e.g. `python3 -m http.server 8000 &`,
  capturing its PID immediately as taught in the process-diagnosis project), then try to start a
  **second** one on the same port.
- **Scenario 4:** create a file, remove your own write permission from it (`chmod u-w
  myfile.txt`, on a file you created, inside your practice directory only), then try to write to
  it.
- **Scenario 5:** reference an environment variable in a small script that isn't set in your `.env`
  yet, and run the script.

```bash
<the command that now fails> > error-evidence.txt 2>&1
cat error-evidence.txt
```

- `2>&1` — redirects `stderr` into the same place as `stdout`, so both the command's normal output
  and its error are captured together in one file
  ([`12-shell-quoting-and-standard-streams.md`](../../03-Command-Line/12-shell-quoting-and-standard-streams.md)).

Confirm `error-evidence.txt` contains the **exact** error text, and confirm it contains nothing
sensitive before keeping it (Section 4's safety rules).

### 8.3 Inspect one fact at a time, using safe commands

Check exactly one thing per command, reading the real result each time before checking the next:

- Current directory: `pwd` / `Get-Location`
- File/permission state: `ls -la <file>` / `Get-Acl <file>`
- Process/port state (Scenario 3 only): `ps aux | grep <name>`, `ss -ltnp` /
  `Get-NetTCPConnection`
- Environment/dependency state (Scenario 2 or 5): `cat pyproject.toml`, `cat .env`, `uv sync`
  (dry inspection, not yet the fix)

Write each fact you checked, and its exact result, into your working notes.

### 8.4 Form a clear hypothesis

Based only on the evidence from 8.2–8.3, write one or two sentences stating your best explanation
for the cause. State it as something checkable, not a vague feeling — for example, "the script
fails because `.venv` doesn't exist, so `uv run` has nothing to run against," not "something's
wrong with Python."

### 8.5 Test the smallest safe command or change

Test your hypothesis with the smallest possible check — not the fix itself yet, just confirmation.
For example, for Scenario 4: run `ls -l myfile.txt` and confirm the permission bits actually show
the write bit missing, before assuming that's the cause.

### 8.6 Apply the smallest possible fix

Apply the minimal, targeted fix — not a broad workaround:

- **Scenario 1:** use the correct path, or `cd` back to the correct directory.
- **Scenario 2:** run `uv sync`.
- **Scenario 3:** stop your own, already-confirmed test process gracefully
  (`kill -TERM <confirmed-pid>` / `Stop-Process -Id <confirmed-pid>`), exactly as taught in
  [Project 0.3](../../02-Operating-System-Fundamentals/Projects/01-process-resource-and-port-diagnosis.md) —
  never a PID you have not personally confirmed.
- **Scenario 4:** restore your own write permission on your own file
  (`chmod u+w myfile.txt`) — never touch permissions outside your practice directory.
- **Scenario 5:** add the missing placeholder value to `.env`.

### 8.7 Verify the original operation now succeeds

Rerun the exact operation from Section 8.1 and capture its real output:

```bash
<the original operation> > verification.txt 2>&1
cat verification.txt
```

Confirm it now matches your Section 8.1 expectation — this file is your fix-verification
deliverable.

### 8.8 Write an evidence-based postmortem

Using everything from Sections 8.1–8.7, write `postmortem-stage-0.md` following Section 9's
template.

## 9. `postmortem-stage-0.md` template

```markdown
# Postmortem: <one-line title of your chosen incident>

**Scenario:** <number and name from Section 7>
**Date:**

## Summary

One or two sentences: what broke, and what fixed it.

## Impact

What operation was affected, and for how long (in this simulation, this can be brief — e.g. "a
single local script could not run").

## Timeline

- Expected behavior confirmed (Section 8.1)
- Problem reproduced deliberately (Section 8.2)
- Investigation performed (Section 8.3–8.5)
- Fix applied (Section 8.6)
- Fix verified (Section 8.7)

## Expected vs. Actual Behavior

- **Expected:** (from Section 8.1)
- **Actual:** (the exact error from Section 8.2)

## Evidence Collected

- Exact error text (from `error-evidence.txt`)
- Exact facts checked and their results (from Section 8.3)

## Root Cause

The specific, confirmed reason — not a guess — stated in one or two sentences.

## Fix

The exact, minimal change applied (Section 8.6).

## Prevention

What you would do differently going forward to avoid this recurring (a habit, a check, a step
added to a README).

## Verification

The exact command and output proving the original operation now succeeds (from
`verification.txt`).

## What to Test Next Time

One concrete thing you'd check first if something similar happens again.
```

## 10. Expected observations and acceptance criteria

- `error-evidence.txt` contains the real, exact error produced by your chosen scenario — not a
  paraphrase.
- Your hypothesis (Section 8.4) is stated as something checkable, and is confirmed or refined by
  Section 8.5's test before you apply any fix.
- The fix applied is the smallest one that addresses the actual root cause — not a broad
  workaround like reinstalling everything or granting wide permissions.
- `verification.txt` shows the original operation succeeding, using the same command style as
  Section 8.1.
- `postmortem-stage-0.md` includes every section from Section 9's template, filled with real,
  specific content — no placeholder text like "TBD" remaining.
- No file in your deliverables contains a real secret or sensitive information.

## 11. Common mistakes and safe troubleshooting

| Mistake | Why it's a problem | Better approach |
|---|---|---|
| Fixing the problem before writing down the expected behavior (Section 8.1) | You lose your own baseline for what "verified" even means | Always state expected behavior first, even for something that feels obvious. |
| Applying a broad fix (e.g., `chmod 777`, reinstalling everything) instead of the smallest one | Hides the real root cause and can introduce new problems | Apply only the minimal change identified by your hypothesis and its test (Section 8.5–8.6). |
| Stopping a process without confirming its PID first | Risks affecting something other than your own test process | Always confirm the exact PID belongs to your own test process before stopping it — never guess. |
| Skipping the verification step because "it looks fixed" | "Looks fixed" is not evidence | Always rerun the original operation and capture real output (Section 8.7) before considering it done. |
| Copying this guide's example wording into the postmortem instead of your own | Doesn't demonstrate real understanding | Write every section in your own words, based on your own actual evidence. |

## 12. Interview-practice questions

Practice answering these aloud, in 60–90 seconds each, using your own `postmortem-stage-0.md`:

1. **"Walk me through how you investigated and fixed a recent problem."**
   Guidance: use your own incident as a concrete example, following the goal → evidence →
   hypothesis → fix → verify shape — this is exactly what this question is testing for.

2. **"Why write a postmortem for something small, instead of just moving on once it's fixed?"**
   Guidance: connect to reusable knowledge and prevention — the same reasoning from
   `13-evidence-based-debugging-and-notes.md`.

3. **"How do you know your fix actually worked, rather than just the symptom going away?"**
   Guidance: describe rerunning the *original* operation and capturing real, specific evidence
   (Section 8.7) — not assuming.

4. **"What's the difference between a smallest fix and a broad workaround, and why does it
   matter?"**
   Guidance: use your own scenario — explain why the targeted fix you applied was better than a
   broader one you could have reached for instead.

## 13. Final Stage 0 project completion gate

You have completed this project when all statements below are true:

- [ ] I performed this project entirely in a separate practice directory or repository, never
      inside the curriculum folder.
- [ ] I chose exactly one scenario from Section 7 and stated it at the top of my postmortem.
- [ ] I stated the expected behavior before introducing any problem.
- [ ] I deliberately reproduced the problem and saved the exact error, with nothing sensitive in
      it.
- [ ] I inspected one fact at a time using only safe commands, and never acted on an unconfirmed
      process, altered a system-level permission, or used a real secret.
- [ ] I formed a checkable hypothesis and tested it before applying any fix.
- [ ] I applied the smallest possible fix that addressed the confirmed root cause.
- [ ] I verified the original operation succeeds again, with real, saved evidence.
- [ ] `postmortem-stage-0.md` is complete, using Section 9's full template, in my own words.

Once every box is checked, this project satisfies Stage 0 Project 0.5 — the capstone. Together
with Projects 0.1–0.4, this completes the practical evidence required by the Stage 0 completion
gate. Return to [`../learning-plan.md`](../learning-plan.md), Section 8 — "Stage 0 completion gate"
— to confirm every remaining item before moving on to Stage 1.
