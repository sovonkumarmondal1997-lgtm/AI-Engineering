# Problem-Solving Template

This file gives you a repeatable template for planning a solution to any
small programming problem **before** you write Python code. It turns the
practice workflow from
[`practice-questions.md`](practice-questions.md) into a concrete,
fill-in-the-blank form you can copy, print, or paste into your own notes.

## How to use this template

1. **Copy the blank template** from the "Reusable template" section below
   into a new note, a text file, or a piece of paper — one copy per
   problem you are solving.
2. **Fill in each section in order, from top to bottom.** Do not skip down
   to "Python implementation plan" early — the whole point of the template
   is to think clearly in plain English and pseudocode first, the same way
   [topic 7](07-pseudocode-flowcharts-and-dry-runs.md) teaches.
3. **Write short answers.** A sentence or two, or a short list, is enough
   for most sections. The goal is clarity, not length.
4. **Only open a Python file once "Pseudocode" and "Dry run" are filled
   in.** If you find yourself wanting to write Python earlier, that
   usually means one of the earlier sections (often "Assumptions" or
   "Edge cases") is still too vague, and is worth another minute of
   thought first.
5. **Come back and fill in "Debugging notes" and "Final explanation" after
   you've coded and tested**, not before — they record what actually
   happened, not what you planned.

This template is meant to be used for **every** problem in
[`practice-questions.md`](practice-questions.md), and for any problem you
meet in later modules or projects.

## Worked example: converting minutes into hours and minutes

This is a short, complete example of the template being filled in, using a
simple problem that is **not** one of the six required practice questions
in this module. It shows you the *level of detail* expected in each
section — it does not solve any of your assigned questions for you.

**Problem being solved:** Given a number of minutes (for example, a movie's
running time), show it as a number of whole hours plus the remaining
minutes.

---

**Problem statement**
Convert a single whole number of minutes into a number of whole hours and a
number of leftover minutes, so that the hours and leftover minutes
together equal the original number of minutes.

**Inputs**
One whole number: total minutes (for example, `135`).

**Outputs**
Two whole numbers: hours, and remaining minutes (for example, `2` hours and
`15` minutes).

**Assumptions**
- The input is a whole number of minutes, not a decimal.
- The input is zero or a positive number; negative minutes do not make
  sense for this problem and will be treated as invalid. The assumption
  defines the valid input; the edge-case section asks you to decide how the
  program should respond if that assumption is violated.

**Rules**
- Hours are found by dividing the total minutes by 60 and keeping only the
  whole-number part (ignoring any remainder).
- Remaining minutes are whatever is left over after removing those whole
  hours, in minutes.

**Examples**
- `135` minutes → `2` hours, `15` minutes (because `2 * 60 = 120`, and
  `135 - 120 = 15`).
- `60` minutes → `1` hour, `0` minutes.
- `45` minutes → `0` hours, `45` minutes.

**Edge cases**
- `0` minutes (should give `0` hours, `0` minutes).
- A number of minutes less than `60` (should give `0` hours).
- A number of minutes that divides evenly into hours, like `120`.
- A negative number of minutes (invalid, according to the assumption
  above — decide what the program should do: refuse it, or treat it as an
  error).

**State to track**
None — this calculation does not need to remember information beyond the
values being computed for this problem.

**Pseudocode**
```text
START
  INPUT total_minutes
  IF total_minutes < 0
    REPORT "invalid input"
  ELSE
    SET hours TO total_minutes divided by 60, whole number part only
    SET remaining_minutes TO total_minutes MINUS (hours times 60)
    OUTPUT hours, remaining_minutes
  END IF
END
```

**Dry run**
Using `total_minutes = 135`:
| Step | Action | Value |
|---|---|---|
| 1 | Check `135 < 0` | False, continue |
| 2 | `hours = 135 // 60` | `hours = 2` |
| 3 | `remaining_minutes = 135 - (2 * 60)` | `remaining_minutes = 15` |
| 4 | Output | `2` hours, `15` minutes — matches the expected example above |

**Test cases**
- Normal case: `135` → `2` hours, `15` minutes.
- Edge case, exact hour: `60` → `1` hour, `0` minutes.
- Edge case, less than an hour: `45` → `0` hours, `45` minutes.
- Edge case, zero: `0` → `0` hours, `0` minutes.
- Edge case, invalid: `-10` → program reports invalid input, no crash.

**Python implementation plan**
- One small function, `minutes_to_hours_and_minutes(total_minutes)`, that
  follows the pseudocode above.
- Use `//` for whole-number (integer) division to get the hours.
- Check for a negative input first, before doing any calculation.
- Return the two numbers together so the caller can decide how to display
  them.

**Debugging notes**
*(fill this in while and after implementing — for this worked example: if
you forget to use `//` and instead use `/`, you get a decimal number of
hours like `2.25`, not a whole number — this is a common mistake worth
watching for.)*

**Final explanation**
*(fill this in after your code works — write two or three sentences
describing, in your own words, how your function turns a number of minutes
into hours and minutes, as if explaining it to someone who has never seen
the code.)*

---

## Reusable template

Copy everything between the lines below into your own notes for a new
problem. Replace each prompt with your own answer; leave a section blank
only if you have genuinely thought about it and decided it does not apply
(for example, "State to track: none").

---

**Problem statement**


**Inputs**


**Outputs**


**Assumptions**


**Rules**


**Examples**


**Edge cases**


**State to track**


**Pseudocode**
```text

```

**Dry run**


**Test cases**


**Python implementation plan**


**Debugging notes**


**Final explanation**


---

## A note on using this template well

- The template is a thinking tool, not paperwork. If a section feels like
  a waste of time for a very small problem, that is usually a sign the
  problem is genuinely simple — but fill it in briefly anyway until this
  habit feels automatic.
- The "Pseudocode" and "Dry run" sections are the two most commonly
  skipped, and the two most valuable. They are exactly the habits taught
  in [topic 7](07-pseudocode-flowcharts-and-dry-runs.md).
- "Debugging notes" is not just for recording that something broke — it is
  for recording *why*, so the same mistake is easier to recognize next
  time.
