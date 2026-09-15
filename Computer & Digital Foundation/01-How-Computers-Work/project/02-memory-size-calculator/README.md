# Project 0.1.2 — Memory-Size Calculator

**Module:** How Computers Work
**Status:** Not Started

## Project objective

Build a small tool that converts a memory/storage size between units (bits, bytes, KB, MB, GB,
TB — and their binary variants, KiB/MiB/GiB, if in scope), demonstrating a working understanding
of how memory and storage capacity are actually measured.

## Concepts used

- Bits, Bytes & Binary (`04-binary-bits-and-bytes.md`)
- Cache (`09-cache.md`)
- RAM (`10-ram.md`)
- Storage (`11-storage.md`)
- Why RAM and Storage Are Different (`19-why-ram-and-storage-are-different.md`)

## Prerequisites

- Concept files 4, 9, 10, 11, and 19 read and understood.
- Lab 1 and Lab 2 (system information; memory and storage) completed, so real numbers from the
  learner's own machine are available to sanity-check the tool's output.

## Requirements

- Accept a numeric size and a unit (e.g. `8`, `GB`).
- Convert it to at least: bits, bytes, KB, MB, GB, TB.
- Clearly state whether decimal units (1000-based, KB/MB/GB) or binary units (1024-based,
  KiB/MiB/GiB) are being used, since this is a common real-world source of confusion.
- Reject invalid/unrecognized units with a clear message.

## Expected inputs

- A positive numeric value and a unit label, e.g. `4 GB`, `512 MB`, `1024 KiB`.

## Expected outputs

- The equivalent size in every other supported unit, clearly labeled, with the decimal/binary
  basis stated explicitly.

## Acceptance criteria

- [ ] Correctly converts a byte value up through KB/MB/GB/TB.
- [ ] Correctly converts a GB value back down to bytes.
- [ ] Correctly distinguishes 1000-based and 1024-based conversions when both are supported.
- [ ] Rejects an unrecognized unit with a clear error rather than a wrong silent result.
- [ ] Learner can use this tool to correctly explain the real RAM/storage numbers found in Lab 1.

## Testing expectations

- At least one round-trip test per unit (convert up, then back down, and confirm the original
  value is recovered, accounting for rounding).
- A test using the real RAM size measured in Lab 1 as input, checked against the tool's own
  `free -h`-reported unit.
- Edge cases: 0, and a very large value (e.g. converting bytes up to TB).

## Debugging expectations

- If a conversion is off by a factor of ~1.024, the learner should be able to identify it as a
  binary-vs-decimal unit mismatch rather than treating it as an unexplained bug.

## Documentation expectations

- A short explanation of which unit system (1000-based vs 1024-based) is used by default and why,
  written so it resolves the binary/decimal ambiguity for a future reader.

## Notes

This is a placeholder specification. No implementation, code, or solution exists yet. The
implementation is written and tested during the teaching phase, after concept files 4, 9, 10, 11,
and 19 have actually been taught.
