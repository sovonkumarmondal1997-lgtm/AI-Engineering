# Project 0.1.1 — Binary / Decimal / Hex Converter

**Module:** How Computers Work
**Status:** Not Started

## Project objective

Build a small tool that converts a number between binary, decimal, and hexadecimal
representations, in any direction, demonstrating a working understanding of how the same value
is represented differently across number bases.

## Concepts used

- Bits, Bytes & Binary (`04-binary-bits-and-bytes.md`)
- Hexadecimal (`05-hexadecimal.md`)
- Instructions & Machine Code (`07-instructions-and-machine-code.md`) — context for *why* these
  bases matter to a computer, not required for the implementation itself.

## Prerequisites

- Concept files 4 and 5 read and understood.
- A working Python environment (this project is implemented in Stage 0 but may be executed once
  Module 0.4's developer environment setup is complete; exact language/tooling choice is
  finalized at build time).

## Requirements

- Accept a number in one base (binary, decimal, or hex) as input.
- Convert and display it in the other two bases.
- Handle at minimum non-negative whole numbers.
- Reject or clearly report invalid input (e.g. a "2" in a binary input, or a non-hex character in
  a hex input) rather than failing silently or crashing uninformatively.

## Expected inputs

- A binary string (e.g. `1011`), a decimal integer (e.g. `42`), or a hexadecimal string (e.g.
  `2A`), each explicitly labeled with its base by the user.

## Expected outputs

- The same value expressed in all three bases (binary, decimal, hexadecimal), clearly labeled.

## Acceptance criteria

- [ ] Converts a known binary value to correct decimal and hex (e.g. `1011` → `11` → `B`).
- [ ] Converts a known decimal value to correct binary and hex (e.g. `42` → `101010` → `2A`).
- [ ] Converts a known hex value to correct binary and decimal (e.g. `2A` → `101010` → `42`).
- [ ] Correctly reports invalid input for all three input bases.
- [ ] Learner can explain, without looking at the code, why each conversion works.

## Testing expectations

- At least one test case per conversion direction (binary→decimal, binary→hex, decimal→binary,
  decimal→hex, hex→binary, hex→decimal).
- At least one test case for invalid input per base.
- Edge cases: zero, and the largest value likely to be used by hand during learning (e.g. an
  8-bit value, `11111111` / `255` / `FF`).

## Debugging expectations

- If a conversion is wrong, the learner should be able to trace the error back to a specific
  step (e.g. incorrect place-value calculation) rather than guessing-and-checking until it works.

## Documentation expectations

- A short explanation (in the project's own README or a comment block, added once built) of the
  place-value logic used for each conversion direction, written so a future reader who has read
  concept files 4–5 could follow it without seeing the code run.

## Notes

This is a placeholder specification. No implementation, code, or solution exists yet. The
implementation is written and tested during the teaching phase, after concept files 4 and 5 have
actually been taught.
