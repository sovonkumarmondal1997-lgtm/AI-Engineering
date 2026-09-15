# Project 0.1.1 — Program Execution and GPU Audit

**Estimated time:** 60–90 minutes (can be split across two sessions)

**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Section 2 — "Audit of the
original Stage 0," Module 0.1 evidence requirement: *"In your own words, explain what happens from
launching a Python command to seeing output, and why a GPU helps with parallel tensor operations."*

---

## 1. Purpose and real-world AI-engineering relevance

This project is a small, hands-on audit. Its only goal is to prove — to yourself, not just to a
reader — that you can explain two things without notes:

1. What actually happens, mechanically, between typing a Python command in a terminal and seeing
   output on screen.
2. At a high level, why a **GPU** (Graphics Processing Unit — a processor built for doing many
   simple calculations at the same time) helps AI workloads that do **tensor operations** (math on
   large grids of numbers, such as the matrix multiplications inside a neural network).

This matters beyond Stage 0. Every later AI-engineering task — running a training script, calling a
model API, debugging a slow inference request, deciding whether a workload needs a GPU at all — sits
on top of this same mechanical picture: a process is started, it uses an interpreter, it touches
CPU, RAM, and disk, it produces output or an error, and (for heavy numeric work) it may hand
calculations to a GPU instead of the CPU. An engineer who cannot explain this picture will treat
every slow script or "out of memory" error as a mystery instead of something to investigate
methodically.

## 2. Learning outcomes

By the end of this project, you will be able to:

- Confirm a working Python interpreter and terminal on your machine, and identify which interpreter
  is actually running.
- Run a small Python program and identify its process, working directory, and resource use while
  it runs.
- Explain, in your own words, the path from "you press Enter" to "output appears on screen."
- Explain the difference between compilation and interpretation in plain language, using Python as
  the concrete example.
- Explain, without needing any GPU hardware, why GPUs are structurally suited to parallel tensor
  operations and why that matters for AI workloads.
- Produce a short, evidence-based written record of what you ran, observed, and concluded.

## 3. Prerequisites and safe-working rules

**Concepts you should have already read** (in this module, `01-How-Computers-Work/`):

- `02-cpu.md`, `03-cores.md` — what a CPU is and does
- `06-registers.md`, `07-instructions-and-machine-code.md`, `08-compilation-and-interpretation.md`
- `09-cache.md`, `10-ram.md`, `11-storage.md` — the memory hierarchy
- `13-gpu.md`, `20-why-gpus-matter-for-ai.md` — what a GPU is and why it matters for AI
- `14-files.md`, `15-input-output.md`, `16-processes.md`
- `17-what-happens-when-a-program-starts.md`

You do not need to have memorized these files. You do need to be willing to reopen and reread one
if a step below doesn't make sense — this project assumes the concepts, it does not re-teach them.

**Tools required** (all free, all already covered in Stage 0):

- A terminal: Bash (Linux/macOS/WSL2) or PowerShell (Windows).
- Python 3, already installed or installable without a paid account.
- A plain-text or Markdown editor (VS Code is fine).

**Not required:** Docker, any cloud account, CUDA, a GPU, or any Python beyond `print()`, a `for`
loop, and importing a few standard-library modules. If a step ever seems to need more than that,
stop and re-read the step — it doesn't.

**Safe-working rules** (from Stage 0 Gap 0B — safe terminal habits):

1. Do all work inside a dedicated practice folder (for example, `~/practice-shell/program-audit/`
   or `C:\practice-shell\program-audit\`), not inside Downloads, Documents, or an existing project.
2. Confirm your current directory (`pwd` in Bash, `Get-Location` in PowerShell) before creating or
   running any file.
3. Every command in this guide is read-only or creates a small file inside your practice folder.
   None of them delete anything. If you ever feel tempted to add a deletion or a recursive command
   to "clean up," stop and do it manually and individually instead.

## 4. Deliverables and evidence checklist

By the end, your practice folder should contain:

- [ ] `execution_audit.py` — the small Python script you ran and annotated.
- [ ] `findings.md` — your written notes: what you expected, what you ran, what you observed, and
      your explanations, following the workflow in Section 6.
- [ ] A completed self-check against the checklist in Section 7.7.
- [ ] A completed self-check against the completion gate in Section 11.

If you are tracking this work in Git (recommended — see Stage 0 Gap 0A), commit these files with a
message such as `docs: add program execution and GPU audit notes`.

## 5. Industry-standard workflow

Use this loop for **every** step below, not only when something breaks. This is Stage 0 Gap 0F —
Engineering thinking from day one — and it is the same loop used later for real debugging:

```text
Goal → assumptions → smallest experiment → observe output/logs
→ explain findings → verify → document
```

In practice, for each step:

1. **Goal** — write one sentence: what are you trying to find out?
2. **Assumptions** — write one sentence: what do you *expect* to happen, before you run anything?
3. **Smallest experiment** — run the smallest command that can answer the question.
4. **Observe output/logs** — read the actual output. Do not skim it.
5. **Explain findings** — write, in your own words, what the output tells you and whether it
   matched your assumption.
6. **Verify** — if anything is surprising, check one fact at a time until you understand why.
7. **Document** — add the result to `findings.md` before moving to the next step.

## 6. Step-by-step instructions

Work through these in order. Each step tells you what command to run and what to record.

### 6.1 Check Python and terminal availability

**Goal:** confirm you have a working terminal and Python interpreter, and know exactly which one.

In Bash:

```bash
pwd
python3 --version
which python3
```

In PowerShell:

```powershell
Get-Location
python --version
Get-Command python
```

Record in `findings.md`:

- The Python version reported.
- The full path to the interpreter (`which`/`Get-Command` output). This is the actual program file
  that will run your code — not an abstract concept.
- Your current directory.

If Python is not found, see Section 9 before doing anything else.

### 6.2 Create and run a tiny Python example

Create a practice folder and, inside it, a file named `execution_audit.py` with this content. Type
it yourself rather than copying it blindly, and read every line before moving on — you will be
asked to explain each one in Section 6.3.

```python
import sys
import os
import time

print("interpreter path:", sys.executable)
print("python version:", sys.version.split()[0])
print("process id (PID):", os.getpid())
print("working directory:", os.getcwd())

# A small, deliberately repetitive calculation.
# This exists only to give the CPU something to do for a moment,
# so you can observe the process while it is active.
total = 0
for i in range(20_000_000):
    total += i
print("sum result:", total)

# Prove this process can read and write files.
with open("execution_audit_output.txt", "w") as f:
    f.write(f"PID {os.getpid()} finished at {time.ctime()}\n")
print("wrote execution_audit_output.txt")
```

Run it:

```bash
python3 execution_audit.py
```

(PowerShell: `python execution_audit.py`)

The loop is intentionally large enough to take a few seconds — you need that window to observe the
process while it runs in the next step, so don't shrink it.

### 6.3 Observe and explain what happened

While the script is running (or immediately after, for the output file), gather evidence for each
of the following. Use a second terminal window if you want to inspect the process while it's still
running.

**Working directory** — Confirm `os.getcwd()` in the output matches what `pwd`/`Get-Location`
showed in Step 6.1. Explain: why does a running program need to know its working directory? (Hint:
this is exactly how it found `execution_audit_output.txt` without a full path.)

**Interpreter** — Compare `sys.executable` to the `which python3` result from Step 6.1. Explain:
what does it mean that a "Python script" doesn't run by itself, but is read and executed by this
specific interpreter program?

**Process** — While the script runs, in a second terminal, run `ps aux | grep python` (Bash) or
`Get-Process python` (PowerShell). Find the PID and confirm it matches the `os.getpid()` value the
script printed. Explain: what is a process, and why does the same program produce a different PID
every time you run it?

**CPU** — While the loop is running, run `top` or `htop` (Bash) or open Task Manager / run
`Get-Process python | Select CPU` (PowerShell). Note the CPU percentage for the Python process.
Explain: why does the CPU usage rise during the loop and fall once the script finishes?

**RAM** — In the same tool, note the memory (RSS or "Working Set") used by the process. Explain:
this small script barely uses any RAM — what would you expect to happen to this number if `total`
were instead a list holding 20 million separate numbers rather than one running sum?

**Disk / file access** — After the script finishes, run `cat execution_audit_output.txt` (Bash) or
`Get-Content execution_audit_output.txt` (PowerShell) and confirm the PID inside matches what was
printed to the terminal. Explain: what is the difference between what you saw printed to the
terminal (standard output) and what was saved to disk (a file)? Why might a program need both?

**Terminal output** — Explain, in one or two sentences, how text you typed (`python3
execution_audit.py`) turned into a request the operating system could act on, and how the
program's `print()` calls turned into characters appearing on your screen. If this isn't fully
clear, reread `15-input-output.md` and `17-what-happens-when-a-program-starts.md` before writing
your answer — don't guess.

Write your explanation for each of the six items above into `findings.md`, in your own words, in
2–4 sentences each. One-word answers are not evidence.

### 6.4 Explain compilation versus interpretation in plain language

Using Python as your concrete example, write a short explanation (4–8 sentences) in `findings.md`
answering:

- Is Python compiled, interpreted, or something in between? (It's fine to say "something in
  between" — that's closer to correct than a flat answer either way.)
- What has to happen to the text in `execution_audit.py` before the CPU can actually execute any
  of it?
- If you ran `python3 execution_audit.py` a second time, would that "compilation-like" step happen
  again? Why might Python cache something to avoid repeating work? (Look for a `__pycache__`
  folder that may have appeared next to your script after running it — that's a clue, not the full
  answer.)

Reread `08-compilation-and-interpretation.md` first if you're unsure — this step is checking
whether you can restate that concept in your own words using a real example you just ran, not
whether you can derive it from scratch.

### 6.5 Explain GPU parallelism and tensor operations — no GPU required

You do not need a GPU, CUDA, or any special library for this step. This is a conceptual explanation
exercise.

First, do this thought experiment and write down your answer before reading further:

> Imagine you have 1,000 pairs of numbers, and your only task is to multiply each pair together.
> One person doing this one multiplication at a time will take 1,000 steps. Now imagine 100 people,
> each with their own pair, all multiplying at the same moment. How many "rounds" of multiplication
> does that take, roughly? What has to be true about the *task* (not the people) for splitting it
> up like this to actually help?

Then write a short explanation (5–10 sentences) in `findings.md` covering:

- In plain language, what is a **tensor**? (A grid of numbers — a list of numbers, a table of
  numbers, or a stack of tables of numbers — used to represent data like an image, a batch of
  text, or a set of model weights.)
- What is a **tensor operation**, and why does training or running a neural network involve doing
  the *same* simple operation (like multiply-and-add) across *huge numbers* of values at once?
- Structurally, how does a CPU differ from a GPU? (A CPU has a small number of powerful cores, each
  good at complex, branching, one-after-another logic. A GPU has a very large number of simpler
  cores, each good at doing the *same* simple operation on *different* pieces of data, all at the
  same time.)
- Connect these: why does a GPU's structure match a tensor operation's shape so well, and why does
  that make GPUs much faster than CPUs specifically for this kind of work — while not necessarily
  faster for the kind of one-after-another logic your `execution_audit.py` script did in Step 6.2?

Reread `13-gpu.md` and `20-why-gpus-matter-for-ai.md` before writing if any of this feels shaky.
You are not expected to explain GPU hardware in engineering detail — you are expected to explain,
correctly and in your own words, *why the shape of the work matches the shape of the hardware.*

### 6.6 Record findings in clear, beginner-friendly notes

By this point `findings.md` should already contain your answers from Steps 6.1–6.5. Now add a short
top section (3–5 sentences) written as if explaining this project to someone who has never seen it,
summarizing:

- What you ran.
- What you observed.
- The one thing you understood better after doing this than before you started.

This top summary is what you would say out loud first in an interview — see Section 10.

### 6.7 Verify all completion criteria

Before moving on, check every box below honestly. If any box is unchecked, go back to that step —
do not mark this project done based on having read the material once.

- [ ] I can state, without looking, the exact path of the Python interpreter that ran my script.
- [ ] I found my script's process by PID in a process-monitoring tool while it was running.
- [ ] I observed CPU usage rise during the loop and explained why.
- [ ] I explained the working-directory, file-write, and terminal-output evidence in my own words.
- [ ] I explained compilation vs. interpretation using my own script as the example.
- [ ] I explained why a GPU's structure suits tensor operations, using the thought experiment.
- [ ] `findings.md` contains full sentences, not single words or copied text I can't defend aloud.

## 7. Expected observations and a model explanation outline

This section tells you what a *correct shape* of answer looks like — not a full answer to copy.
Use it to check your own explanation, after writing it, not before.

**Program execution, expected shape:**

1. The shell (Bash/PowerShell) receives your typed command and looks up the `python3`/`python`
   program on disk.
2. The operating system creates a new **process** for that program, giving it its own memory space
   and a PID.
3. The Python interpreter starts inside that process, reads your `.py` file as text, and translates
   it into an internal form it can execute (see Step 6.4 — this is the compilation-like step).
4. The interpreter executes that internal form one step at a time: allocating memory for variables
   in RAM, running the loop on the CPU, and calling the operating system to read/write files and
   print to the terminal.
5. When the script finishes, the process exits, freeing its resources; the shell gets control back
   and shows your prompt again.

If your explanation covers roughly these five beats, in your own words, with evidence from what you
actually observed (a real PID, a real CPU spike, a real file), it's correct — the exact wording
doesn't need to match.

**GPU/tensor explanation, expected shape:**

- A CPU core executes one instruction stream very capably, including branches and dependent steps.
- A GPU has many more, simpler cores that each execute the *same* instruction on *different* data
  at the same time — well suited to doing one operation (like multiply-add) across millions of
  tensor values simultaneously, rather than one after another.
- Neural network math is dominated by exactly this kind of large, repetitive, parallel-friendly
  arithmetic, which is why GPUs (and specialized AI accelerators) dramatically speed up training
  and inference compared to a CPU doing the same math sequentially.

If your explanation reaches this conclusion through your own reasoning and the thought experiment,
rather than reciting it, you've met the goal.

## 8. Common problems and safe troubleshooting steps

| Problem | Likely cause | Safe next step |
|---|---|---|
| `python3: command not found` (Bash) | Python not installed, or installed as `python` not `python3` | Try `python --version`. If neither works, install Python 3 from your OS's official package manager or python.org — do not use an untrusted installer. |
| `python : The term 'python' is not recognized` (PowerShell) | Python not installed or not on PATH | Reinstall Python from python.org with "Add to PATH" checked, then open a **new** terminal window. |
| Script runs but no `execution_audit_output.txt` appears | You ran the script from a different directory than you're looking in | Run `pwd`/`Get-Location` again immediately after running the script; the file is written to whatever directory Python reports as `os.getcwd()`. |
| `ps aux \| grep python` shows nothing while script is running | The loop finished before you switched terminals | Increase the loop count in `execution_audit.py` (e.g., `40_000_000`) temporarily, giving yourself more time to observe it, then change it back. |
| Permission error writing the output file | You're running the script somewhere you don't have write access | Move your practice folder to somewhere you own, such as your home directory; do not use `sudo`/administrator mode to force it. |
| `__pycache__` folder confuses you | This is normal — CPython's caching of the compiled form (see Step 6.4) | Leave it; it's evidence for your compilation/interpretation explanation, not a problem. |

If you hit something not listed here: apply the workflow in Section 5. State what you expected,
what happened instead, and check one fact at a time (interpreter path, working directory, file
permissions) before changing anything.

## 9. Interview-practice questions

Practice answering these aloud, in 60–90 seconds each, using your own notes from `findings.md` —
not by reading a script.

1. **"Walk me through what happens when you run a Python script from the terminal."**
   Guidance: start from the shell reading your command, through process creation, interpretation,
   and exit. Use your own script and PID as a concrete anchor instead of speaking abstractly.

2. **"What's the difference between compiled and interpreted languages?"**
   Guidance: use Python's actual behavior (translating to an internal form, then executing it, with
   some caching) as your example rather than a textbook definition you can't back up.

3. **"Why would a GPU help train a neural network faster than a CPU?"**
   Guidance: lead with the *shape of the work* (millions of identical, independent multiply-add
   operations) before the *shape of the hardware* (many simple parallel cores) — that ordering
   shows you understand cause and effect, not just the vocabulary.

4. **"How would you check what a running Python process is doing on your machine?"**
   Guidance: name the actual tools you used (`ps`/`top` or `Get-Process`) and what you looked for
   (PID, CPU%, memory) — this is a very common real-world debugging question.

5. **"What's the difference between output printed to the terminal and output written to a file?"**
   Guidance: connect this to standard output versus file I/O, and give a reason a real program
   might need both (a log file that persists, versus immediate feedback to a user).

## 10. Completion gate

You have completed this project when all statements below are true:

- [ ] I ran `execution_audit.py` myself and can point to the real output it produced.
- [ ] I identified my script's interpreter path, PID, working directory, CPU activity, and output
      file, using real commands, not assumptions.
- [ ] I can explain compilation vs. interpretation in Python using my own script as the example,
      without reading from notes.
- [ ] I can explain why GPUs suit tensor operations, using the thought experiment and my own
      reasoning, without reading from notes.
- [ ] `findings.md` is complete, in my own words, and matches the deliverables checklist in
      Section 4.
- [ ] I answered all five interview-practice questions aloud at least once.

Once every box is checked, this project satisfies the Module 0.1 audit evidence referenced in the
Stage 0 roadmap's Section 2. Return to
[`../../00-Stage-0-Overview/learning-plan.md`](../../00-Stage-0-Overview/learning-plan.md) to
continue with the rest of Stage 0.
