# Lab 0.1.3 — CPU Observation Lab

**Status:** Not Started
**Concepts exercised:** CPU, Cores, Instructions (observed indirectly through load)

## Objective

Observe the CPU actually doing work — before any programming has been taught — by generating
load and watching per-core CPU usage change in real time.

## Prerequisites

- Concept files 2–3 and 6–8 read (CPU, Cores, Registers, Instructions & Machine Code,
  Compilation & Interpretation).
- Lab 1 completed (CPU model/core count already known).
- A terminal on Linux, Ubuntu, or WSL2.

## Commands/tools required

- `top` or `htop` (install with `sudo apt install htop` if not present)
- `nproc`
- `yes > /dev/null` (a trivial, no-code way to fully load one CPU core)

## Procedure outline

1. Run `nproc` to confirm the number of logical CPU cores available.
2. Open `top` (or `htop`) in one terminal window/pane and observe idle per-core usage.
3. In a second terminal, run `yes > /dev/null &` to start a CPU-bound background task.
4. Watch `top`/`htop` and note which core's usage jumps and by how much.
5. Repeat step 3 several times (running multiple `yes > /dev/null &` commands) up to the core
   count from step 1, and observe usage spreading across cores.
6. Stop all background tasks with `kill %1 %2 ...` (or `pkill yes`) when done.

## Observations to record

- Idle CPU usage per core before starting any load.
- Which core(s) usage increased on, and to roughly what percentage, after starting one load task.
- What happens once the number of load tasks equals or exceeds the number of cores (e.g. usage
  maxes out, further tasks queue rather than adding more usage).

## Expected learning outcome

The learner can explain, using something they personally watched happen, why "cores" let a
computer do more than one thing at once, and why CPU-bound work eventually saturates a fixed
number of cores regardless of how many tasks are requested.

## Troubleshooting

- **`htop` not installed and no `sudo` access:** fall back to plain `top`, which is preinstalled
  on virtually all Linux/WSL2 systems.
- **Forgetting to stop background `yes` processes:** run `pkill yes` to clean up; leaving them
  running will keep the CPU busy afterward.
- **WSL2 shows fewer cores than the host Windows machine has:** note this as an observation — it
  connects to virtualization/resource-allocation concepts covered later in Module 0.2.

---

_This is a lab specification prepared during repository setup. No lab has been performed yet._
