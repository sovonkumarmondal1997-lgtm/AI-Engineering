# Practice Questions — Module 1.1

These six questions let you practise everything from the eight topic files
in this module. They are deliberately the same kind of problem you have
already seen broken down in the lessons — expenses, passwords, traffic
lights, counting, and simple text — because the goal here is not to learn
new ideas, but to build confidence solving problems **on your own**, from a
blank page.

This file does **not** contain full Python solutions. It gives you a
problem statement, a learning goal, suggestions for input/output, things to
think about, edge cases to test, and small hints — never a finished answer.
You are expected to write your own pseudocode and your own Python code for
every question.

## The practice workflow

Follow these steps, in this order, for every question below. This is the
same discipline taught in
[topic 7](07-pseudocode-flowcharts-and-dry-runs.md) and
[topic 6](06-preconditions-postconditions-and-edge-cases.md), applied as a
single repeatable routine.

1. **Understand the problem** — Read the question until you could explain
   it to someone else in your own words, without looking at it again.
2. **Identify inputs and outputs** — Write down exactly what information
   goes in, and exactly what result should come out.
3. **State your assumptions** — Decide anything the question does not say
   explicitly (for example, "can an expense be zero?"), and write your
   assumption down before coding.
4. **List edge cases** — Write down the empty-input case, any invalid
   input, duplicates, and boundary values you should test, following
   [topic 6](06-preconditions-postconditions-and-edge-cases.md).
5. **Write pseudocode** — Plan the steps in plain, structured English
   first, as shown in [topic 7](07-pseudocode-flowcharts-and-dry-runs.md).
   Do not open a Python file yet.
6. **Dry-run your pseudocode** — Trace through your own pseudocode by hand,
   using a made-up example, before trusting it.
7. **Implement in Python** — Only now, translate your pseudocode into
   Python, one small piece at a time.
8. **Test normal and edge cases** — Run your program on an ordinary input,
   then on every edge case you listed in step 4.
9. **Explain aloud** — Describe, out loud, what your code does and why,
   line by line. If you cannot, go back and re-read the relevant topic
   file.

For a structured place to write down steps 1–6 before you code, use
[`problem-solving-template.md`](problem-solving-template.md) in this same
folder.

---

## Question 1 — Total and average of a list of expenses

**Problem statement:** Given a list of amounts a person spent (for
example, on a trip), calculate the total amount spent and the average
amount per expense.

**Learning goal:** Practise the running-total pattern, basic iteration, and
handling a possible empty list correctly (see
[topic 4](04-sequence-selection-iteration-and-abstraction.md) and
[topic 6](06-preconditions-postconditions-and-edge-cases.md)).

**Suggested inputs / outputs:**

- Input: a list of numbers, such as `[12, 45, 9, 20]`.
- Output: two numbers — the total, and the average.

**Assumptions to consider:**

- Can an expense be `0`? Can it be negative (for example, a refund)?
- Should the average be rounded, or shown exactly as Python calculates it?
- For an empty list, choose and document what your program should return
  or report before coding.

**Edge cases to test:**

- An empty list of expenses.
- A list with exactly one expense.
- A list where every expense is the same value.
- A list that includes a very large number and a very small number
  together.

**Hints:**

- You have already seen the running-total pattern in
  [topic 1](01-algorithms-programs-and-data.md) and
  [topic 2](02-values-expressions-statements-and-variables.md). Reuse the
  idea, not the exact code.
- Think about what your function should do for an empty list *before* you
  write the division for the average — dividing by the count of items
  only works if there is at least one item.
- Consider writing this as two small functions, following
  [topic 5](05-problem-decomposition.md), rather than one large block.

**Completion checklist:**

- [ ] I wrote pseudocode before writing any Python.
- [ ] I dry-ran my pseudocode on a made-up list of expenses.
- [ ] My program gives the correct total and average for a normal list.
- [ ] My program does something sensible (not a crash) for an empty list,
      and I made that choice on purpose.
- [ ] I can explain my code aloud, line by line.

---

## Question 2 — Check whether a password meets minimum rules

**Problem statement:** Decide whether a password typed by a user meets a
small set of rules you choose (for example: at least 8 characters long,
and contains at least one digit).

**Learning goal:** Practise selection (`if` / `elif` / `else`), combining
conditions, and thinking through edge cases for text input, as covered in
[topic 4](04-sequence-selection-iteration-and-abstraction.md) and
[topic 6](06-preconditions-postconditions-and-edge-cases.md).

**Suggested inputs / outputs:**

- Input: a single password, as text.
- Output: a message stating whether the password is acceptable, and if
  not, which rule it failed.

**Assumptions to consider:**

- Exactly which rules count as "minimum" rules? Decide and write them down
  before coding (for example: minimum length, at least one digit, no
  spaces). This is intentionally open-ended: your chosen rules are part of
  the problem specification, so write them down before coding.
- Should the password be checked against *all* rules, or should checking
  stop at the first rule that fails?

**Edge cases to test:**

- An empty password.
- A password that is exactly at your minimum length boundary.
- A password that is one character short of your minimum length.
- A password made only of digits, or only of letters.

**Hints:**

- [Topic 6](06-preconditions-postconditions-and-edge-cases.md) shows a
  similar password example — read it again for the *shape* of the
  approach, then design your own rules rather than copying that one.
- `len(text)` gives you the number of characters; looping over each
  character with `for character in text:` lets you check things like
  digits, following the pattern from
  [topic 5](05-problem-decomposition.md)'s `has_a_digit` example.

**Completion checklist:**

- [ ] I wrote down my exact password rules, and whether I check all
      rules or stop at the first failure, before coding.
- [ ] I wrote pseudocode for checking each rule.
- [ ] I tested a password that passes every rule.
- [ ] I tested a password that fails each rule, one at a time, and
      confirmed my program's behavior follows the rules I documented.
- [ ] I tested an empty password and a password exactly at my length
      boundary.
- [ ] I can explain my code aloud, line by line.

---

## Question 3 — Simulate a traffic light with three states

**Problem statement:** Model a traffic light that starts at red, and can
move through its three states — red, green, and yellow — only in the
correct order, rejecting any request to change to a state that isn't
allowed next.

**Learning goal:** Practise state and state transitions, as covered in
[topic 8](08-state-and-state-modelling.md).

**Suggested inputs / outputs:**

- Input: a starting state, and a sequence of requests to change state (or
  simply repeated calls to "advance" to the next state).
- Output: the current state after each request, and whether each request
  succeeded or was rejected.

**Assumptions to consider:**

- Either design is acceptable. Whichever approach you choose, define the
  allowed transitions explicitly before coding and test both valid and
  invalid requests.
- Does the light always move to a single, fixed next state (like the
  simple example in topic 8), or can it be *asked* to jump to an arbitrary
  state, which you must then accept or reject (like the elevator example
  in topic 8)?
- What should happen if someone asks the light to "advance" many times in
  a row — should it just keep cycling?

**Edge cases to test:**

- Requesting an invalid transition (for example, red directly to yellow).
- Requesting the same, valid transition many times in a row.
- Starting the light at a state other than red, if your design allows
  that.

**Hints:**

- [Topic 8](08-state-and-state-modelling.md) has two worked examples (a
  traffic light and an elevator) showing both styles described above.
  Study the *shape* of the solution, then build your own version rather
  than copying the exact code.
- A dictionary mapping each state to its allowed next state (or states) is
  a clean way to represent the rules, as shown in topic 8.

**Completion checklist:**

- [ ] I listed all three states and the valid transitions between them
      before coding, and documented which transition model I chose (fixed
      next state, or accepting/rejecting requested transitions).
- [ ] I wrote pseudocode for how a transition request is checked.
- [ ] I tested a full valid cycle (red → green → yellow → red).
- [ ] I tested the behavior my model defines. If my design accepts
      requested transitions, I tested at least one invalid request and
      confirmed the state did not change.
- [ ] I can explain my code aloud, line by line.

---

## Question 4 — Count positive, negative, and zero numbers in a list

**Problem statement:** Given a list of numbers, count how many are
positive, how many are negative, and how many are exactly zero.

**Learning goal:** Practise iteration combined with selection (a loop with
an `if` / `elif` / `else` inside it), as covered in
[topic 4](04-sequence-selection-iteration-and-abstraction.md).

**Suggested inputs / outputs:**

- Input: a list of numbers, such as `[4, -2, 0, 7, -9, 0, 1]`.
- Output: three counts — how many positive, how many negative, how many
  zero.

**Assumptions to consider:**

- Are the numbers always whole numbers, or could they include decimals?
- Does your program need to handle the list containing non-number values,
  or can you assume every item is already a valid number?

**Edge cases to test:**

- An empty list.
- A list where every number is positive (so the other two counts should be
  zero).
- A list made entirely of zeros.
- A list with only one number in it.

**Hints:**

- This is the same shape of problem as topic 4's worked example — three
  running-total counters, updated inside a loop using selection. Design
  your own variable names and structure rather than reusing that example
  directly.
- Decide what your three counters should start at, and why.

**Completion checklist:**

- [ ] I wrote pseudocode showing the three counters and how each one is
      updated.
- [ ] I dry-ran my pseudocode on a short made-up list, by hand, tracking
      all three counters.
- [ ] My program gives correct counts on a normal list.
- [ ] My program gives three zero counts for an empty list.
- [ ] I can explain my code aloud, line by line.

---

## Question 5 — Find the largest number without using `max()`

**Problem statement:** Given a list of numbers, find the largest one,
without using Python's built-in `max()` function.

**Learning goal:** Practise designing a small algorithm yourself: keeping
track of "the best value seen so far" while iterating, which is a pattern
that reappears constantly in programming.

**Suggested inputs / outputs:**

- Input: a list of numbers, such as `[3, 9, 2, 9, 4]`.
- Output: a single number — the largest value in the list.

**Assumptions to consider:**

- What should your program do if the list is empty? Is there a sensible
  "largest number" of nothing? There is no single required choice for an
  empty list in this exercise; choose and document the behavior before
  coding.
- What should happen if the largest number appears more than once in the
  list?

**Edge cases to test:**

- An empty list.
- A list with exactly one number.
- A list where the largest number appears more than once.
- A list where all the numbers are negative.

**Hints:**

- Think about starting with a "best so far" variable set to the *first*
  item in the list, then comparing every other item against it — rather
  than starting it at `0`, which would go wrong for a list of entirely
  negative numbers.
- This is a precondition question too: what must be true about the list
  for your approach to work at all? Write that down, following
  [topic 6](06-preconditions-postconditions-and-edge-cases.md).

**Completion checklist:**

- [ ] I wrote pseudocode for the "best so far" approach before coding.
- [ ] I dry-ran my pseudocode by hand on a list with the largest number
      appearing twice.
- [ ] I decided, on purpose, what happens for an empty list.
- [ ] My program finds the correct largest number on at least three
      different normal-case lists.
- [ ] I can explain my code aloud, line by line.

---

## Question 6 — Convert a sentence into word counts, ignoring case and punctuation

**Problem statement:** Given a sentence, count how many times each word
appears, treating words the same regardless of capital letters, and
ignoring punctuation such as commas and periods.

**Learning goal:** Practise combining several small processing steps
(cleaning text, splitting it into words, counting) into one program,
following the decomposition habit from
[topic 5](05-problem-decomposition.md).

**Suggested inputs / outputs:**

- Input: a sentence, as text, such as
  `"The cat sat. The cat sat on the mat!"`.
- Output: a report of how many times each distinct word appears (for
  example, `"the"` appears a certain number of times, `"cat"` a certain
  number of times, and so on). Unless you define an ordering rule
  yourself, the exercise does not require a particular output order.

**Assumptions to consider:**

- Exactly which characters count as punctuation to remove? Decide on a
  small, clear list rather than trying to handle every possible symbol.
  This exercise intentionally uses a small, learner-defined punctuation
  set; document which characters your program will remove before coding.
- Should `"Cat"` and `"cat"` be counted as the same word? (The question
  says yes — decide *how* you will make that true in your code.)

**Edge cases to test:**

- An empty sentence.
- A sentence with only one word.
- A sentence where the same word appears with different capitalization
  and different surrounding punctuation (for example, `"Cat, cat. CAT!"`).
- A sentence with extra spaces between words.

**Hints:**

- Break this into small steps rather than one big block, following
  [topic 5](05-problem-decomposition.md): first make everything lowercase,
  then remove punctuation, then split the text into a list of words, then
  count them.
- `text.lower()` and `text.split()` are useful building blocks; look up
  what each one does on its own with a small example before combining
  them.
- You do not need a dictionary data type to attempt a first version — you
  can count using a list of words you have already seen and a matching
  list of counts, in the same style as topic 4's counters, if you prefer
  to stay with ideas already covered in this module.

**Completion checklist:**

- [ ] I decided exactly which punctuation characters to handle, and wrote
      that decision down.
- [ ] I wrote pseudocode for the separate cleaning, splitting, and
      counting steps.
- [ ] I tested that `"Cat"` and `"cat"` are correctly counted as the same
      word.
- [ ] I tested an empty sentence and a one-word sentence.
- [ ] I tested a sentence with extra spaces between words, and the word
      counts match my documented normalization rules.
- [ ] I can explain my code aloud, line by line.

---

## After you finish all six questions

- Re-read [topic 6](06-preconditions-postconditions-and-edge-cases.md) and
  check that every solution above states its precondition(s) and
  postcondition, even just as a comment.
- Pick one question and re-solve it a few days later, from a blank file,
  without looking at your earlier answer. If it takes noticeably less
  effort the second time, that is a good sign your understanding is
  solid.
- If any question felt very difficult, go back to the matching topic file
  linked in its hints and re-read it before trying again — do not move on
  to Module 1.2 while a question here still feels like guesswork.
