# Lab 0.1.4 — Program Execution Observation Lab

**Status:** Not Started
**Concepts exercised:** Files, Input/Output, Processes, What Happens When a Program Starts

## Objective

Watch an ordinary program (not written by the learner) turn into a running process, and connect
that observation to the "what happens when a program starts" narrative from concept file 17.

## Prerequisites

- Concept files 14–17 read (Files, Input/Output, Processes, What Happens When a Program Starts).
- Labs 1–3 completed.
- A terminal on Linux, Ubuntu, or WSL2.

## Commands/tools required

- `ps aux` or `ps -ef`
- `top` or `htop`
- Any long-running, harmless program available on the system (e.g. `sleep 300`, or a text editor
  like `nano`)

## Procedure outline

1. In one terminal, run a long-running command, e.g. `sleep 300`.
2. In a second terminal, run `ps aux | grep sleep` and locate the entry for the running command.
3. Note the process ID (PID), and any other columns shown (owning user, CPU%, MEM%, start time).
4. Open `top`/`htop` and find the same process by its PID; observe it listed as a running task.
5. Return to the first terminal and stop the program (`Ctrl+C`), then re-run
   `ps aux | grep sleep` in the second terminal to confirm the process is gone.
6. Repeat briefly with a second, different program to confirm each run gets its own new PID.

## Observations to record

- The PID assigned to the running program.
- What information `ps`/`top` shows about a running process besides its name.
- Confirmation that the process disappears from `ps aux` output once stopped.
- Confirmation that running the same program again produces a **different** PID.

## Expected learning outcome

The learner can describe, from direct observation, that "running a program" means the operating
system creates a distinct, identifiable process with its own PID and resource usage — turning the
abstract narrative in concept file 17 into something they watched happen on their own machine.

## Troubleshooting

- **`grep sleep` also matches the `grep` command itself:** this is expected — point it out and
  use it as a small, concrete example of how process listings work, or filter further with
  `grep sleep | grep -v grep`.
- **PID reused unexpectedly:** PIDs can be reused by the OS over time; if this happens, re-run the
  test and note the PID change between runs rather than expecting strictly increasing numbers.
- **No graphical/interactive program available to test with:** `sleep <n>` is sufficient on its
  own and requires no additional installation.

---

_This is a lab specification prepared during repository setup. No lab has been performed yet._
