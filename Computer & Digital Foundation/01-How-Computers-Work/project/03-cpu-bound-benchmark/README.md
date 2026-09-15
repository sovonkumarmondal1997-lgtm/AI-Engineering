# Project 0.1.3 — Simple CPU-Bound Workload Benchmark

**Module:** How Computers Work
**Status:** Not Started

## Project objective

Build a small benchmark that runs a CPU-bound workload (e.g. a compute-heavy loop) and measures
how its execution time changes under different conditions (e.g. single-threaded vs using
multiple cores), demonstrating a working understanding of CPU, cores, and instruction execution.

## Concepts used

- CPU (`02-cpu.md`)
- Cores (`03-cores.md`)
- Instructions & Machine Code (`07-instructions-and-machine-code.md`)
- Processes (`16-processes.md`)

## Prerequisites

- Concept files 2, 3, 7, and 16 read and understood.
- Lab 3 (CPU observation) completed, so the learner has already watched CPU/core usage change
  under load before measuring it programmatically.

## Requirements

- Run a deliberately CPU-bound workload (e.g. computing primes up to N, or a large numeric loop)
  and measure its wall-clock execution time.
- Run the same total workload split across multiple processes/cores and measure execution time
  again.
- Report both timings so they can be compared directly.
- Keep the workload itself simple and understandable without requiring algorithms knowledge
  beyond what's introduced later in Stage 2 — the point is observing CPU behavior, not writing an
  efficient algorithm.

## Expected inputs

- A workload size parameter (e.g. "count primes up to 2,000,000") and a number of
  workers/processes to split the work across.

## Expected outputs

- Execution time for the single-core run.
- Execution time for the multi-core run.
- A plain-language comparison (e.g. "N times faster with N cores" or an explanation of why it
  wasn't a clean N-times speedup).

## Acceptance criteria

- [ ] Single-core run completes and reports a timing.
- [ ] Multi-core run completes and reports a timing.
- [ ] The two timings are comparable (same total workload in both runs).
- [ ] Learner can explain, using their own results, why more cores didn't necessarily produce a
      perfectly proportional speedup (e.g. overhead, core count limits, other system load).

## Testing expectations

- Confirm the single-core and multi-core runs produce the *same correctness result* (e.g. the
  same count of primes found), so the benchmark is known to be measuring speed, not correctness
  differences.
- Run each benchmark more than once and note timing variance, rather than trusting a single run.

## Debugging expectations

- If the multi-core run is not faster (or is slower), the learner should be able to connect this
  back to the core count found in Lab 1 (`nproc`) and reason about it, rather than assuming the
  benchmark code is simply wrong.

## Documentation expectations

- A short write-up of the measured timings and the learner's explanation of the result, written
  so it demonstrates real understanding of CPU/core behavior rather than just reporting numbers.

## Notes

This is a placeholder specification. No implementation, code, or solution exists yet. The
implementation is written and tested during the teaching phase, after concept files 2, 3, 7, and
16 have actually been taught.
